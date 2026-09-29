from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import httpx

from ai_swe_agent.config import Settings

REMOTE_RE = re.compile(
    r"github\.com[:/](?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)


class GitHubAdapter:
    """GitHub MCP-facing adapter: repo, branch, PR, and search via gh/git."""

    def __init__(self, settings: Settings, cwd: Path | None = None) -> None:
        self.settings = settings
        self.cwd = cwd or settings.resolved_workspace()

    def current_branch(self) -> str:
        return self._git("rev-parse", "--abbrev-ref", "HEAD").strip()

    def default_branch(self) -> str:
        return self.settings.github_default_base

    def create_branch(self, name: str, start_point: str | None = None) -> str:
        base = start_point or self.default_branch()
        existing = self._git("branch", "--list", name).strip()
        if existing:
            self._git("checkout", name)
            return name
        self._git("checkout", "-b", name, base)
        return name

    def commit(self, message: str) -> str:
        self._git("add", "-A")
        status = self._git("status", "--porcelain").strip()
        if not status:
            return "nothing to commit"
        self._git("commit", "-m", message)
        return self._git("rev-parse", "--short", "HEAD").strip()

    def push(self, branch: str | None = None) -> str:
        name = branch or self.current_branch()
        return self._git("push", "-u", self.settings.github_default_remote, name)

    def create_pull_request(self, title: str, body: str, base: str | None = None) -> str:
        args = [
            "gh",
            "pr",
            "create",
            "--title",
            title,
            "--body",
            body,
            "--base",
            base or self.default_branch(),
        ]
        return self._run(args)

    def search_code(self, query: str) -> str:
        return self._git("grep", "-n", "-I", query)

    def read_file(self, relative: str) -> str:
        return self._safe_path(relative).read_text(encoding="utf-8")

    def write_file(self, relative: str, content: str) -> str:
        path = self._safe_path(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return str(path.relative_to(self.cwd))

    def list_webhooks(self) -> list[dict]:
        owner, repo = self._owner_repo()
        with self._http() as client:
            response = client.get(f"/repos/{owner}/{repo}/hooks")
        response.raise_for_status()
        hooks = []
        for item in response.json():
            hooks.append(
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "url": (item.get("config") or {}).get("url"),
                    "events": item.get("events") or [],
                    "active": item.get("active"),
                }
            )
        return hooks

    def _safe_path(self, relative: str) -> Path:
        path = (self.cwd / relative).resolve()
        if path != self.cwd and self.cwd not in path.parents:
            raise ValueError(f"Path escapes repository: {relative}")
        return path

    def _http(self) -> httpx.Client:
        if not self.settings.github_configured():
            raise RuntimeError("GitHub is not configured. Set GITHUB_TOKEN.")
        return httpx.Client(
            base_url="https://api.github.com",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.settings.github_token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30.0,
        )

    def _owner_repo(self) -> tuple[str, str]:
        identity = self.repo_identity()
        parsed = parse_github_remote(identity.get("remote") or "")
        if not parsed:
            raise RuntimeError("Could not parse owner/repo from git remote.")
        return parsed

    def _git(self, *args: str) -> str:
        return self._run(["git", *args])

    def _run(self, args: list[str]) -> str:
        result = subprocess.run(
            args,
            cwd=self.cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(f"{' '.join(args)} failed: {detail}")
        return result.stdout

    def repo_identity(self) -> dict[str, str]:
        try:
            remote = self._git("remote", "get-url", self.settings.github_default_remote).strip()
        except RuntimeError:
            remote = ""
        parsed = parse_github_remote(remote)
        return {
            "remote": remote,
            "branch": self.current_branch() if remote else "",
            "cwd": str(self.cwd),
            "owner": parsed[0] if parsed else "",
            "repo": parsed[1] if parsed else "",
        }

    def format_pr_body(self, ticket_key: str, ticket_url: str | None, summary: str) -> str:
        payload = {
            "ticket": ticket_key,
            "url": ticket_url,
            "summary": summary,
        }
        return (
            f"## Summary\nImplements {ticket_key}: {summary}\n\n"
            f"## Jira\n{ticket_url or ticket_key}\n\n"
            f"<!-- {json.dumps(payload)} -->\n"
        )


def parse_github_remote(url: str) -> tuple[str, str] | None:
    match = REMOTE_RE.search(url.strip())
    if not match:
        return None
    return match.group("owner"), match.group("repo")
