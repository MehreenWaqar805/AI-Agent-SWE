from __future__ import annotations

from pathlib import Path

from ai_swe_agent.config import Settings
from ai_swe_agent.mcp.launch import stdio_command
from ai_swe_agent.models import GatheredContext


IMPLEMENT_PROMPT = """You are the execute step of an iOS software engineering agent.

Implement the Jira ticket as **native iOS** code (Swift / SwiftUI, iOS 17+, MVVM-C).
Write only under `ios/`. Do not modify the Python agent, MCP servers, or `.env`.

Ticket: {key} — {summary}
URL: {url}
Description:
{description}

Acceptance criteria:
{criteria}

Figma (match layout, type, and color):
{figma}

iOS project memory:
{memory}

Plan:
{plan}

Rules:
- SwiftUI views + ViewModels. Coordinator handles navigation.
- Pixel-follow the Figma screen named in the ticket (Home, Search, Wishlist, Rating).
- Add or update XCTest coverage for the view model when behavior is non-trivial.
- No force unwraps, no hardcoded secrets, no UIKit unless the module already uses it.
- Keep `MoviesApp.xcodeproj` building for iPhone.
"""


REVIEW_PROMPT = """You are the iOS code-review agent.

Review the Swift/SwiftUI changes for ticket {key}.
Check MVVM-C, Figma fidelity, accessibility, concurrency, and that only `ios/` was edited.
Return a short verdict (approved or changes requested) and a bullet list of findings.
"""


class ReasoningEngine:
    """Cursor SDK reasoning engine. Falls back to a local plan when no API key is set."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def available(self) -> bool:
        return self.settings.cursor_configured()

    def implement(self, context: GatheredContext, workspace: Path) -> str:
        prompt = IMPLEMENT_PROMPT.format(
            key=context.ticket.key,
            summary=context.ticket.summary,
            url=context.ticket.url or "",
            description=context.ticket.description or "(none)",
            criteria="\n".join(f"- {item}" for item in context.ticket.acceptance_criteria) or "- (none listed)",
            figma=self._figma_block(context),
            memory=self._memory_block(context),
            plan="\n".join(f"{step.id}. {step.title}: {step.detail}" for step in context.plan.steps),
        )
        return self._run(prompt, workspace)

    def review(self, context: GatheredContext, workspace: Path) -> str:
        return self._run(REVIEW_PROMPT.format(key=context.ticket.key), workspace)

    def mcp_servers(self) -> dict[str, dict[str, object]]:
        """Local + official MCP servers attached to the Cursor SDK agent."""
        servers: dict[str, dict[str, object]] = {}
        if self.settings.atlassian_mcp_url:
            servers["atlassian"] = {"url": self.settings.atlassian_mcp_url}
        if self.settings.figma_mcp_url:
            servers["figma"] = {"url": self.settings.figma_mcp_url}
        if self.settings.github_mcp_url:
            github: dict[str, object] = {"url": self.settings.github_mcp_url}
            if self.settings.github_token:
                github["headers"] = {"Authorization": f"Bearer {self.settings.github_token}"}
            servers["github"] = github
        local = {
            "jira-local": "jira-mcp-server/jira_server.py",
            "figma-local": "figma-mcp-server/figma_server.py",
            "github-local": "github-mcp-server/github_server.py",
        }
        for name, script in local.items():
            command = stdio_command(script)
            servers[name] = {"command": command[0], "args": command[1:]}
        return servers

    def _sdk_mcp_servers(self, http_cls, stdio_cls) -> dict:
        configs = {}
        for name, spec in self.mcp_servers().items():
            if "url" in spec:
                headers = spec.get("headers") if isinstance(spec.get("headers"), dict) else None
                configs[name] = http_cls(url=spec["url"], headers=headers)
            else:
                configs[name] = stdio_cls(command=spec["command"], args=list(spec["args"]))
        return configs

    def _run(self, prompt: str, workspace: Path) -> str:
        if not self.available():
            return "cursor-sdk skipped: CURSOR_API_KEY is not set."
        from cursor_sdk import (  # type: ignore[import-not-found]
            Agent,
            AgentOptions,
            HttpMcpServerConfig,
            LocalAgentOptions,
            StdioMcpServerConfig,
        )

        servers = self._sdk_mcp_servers(HttpMcpServerConfig, StdioMcpServerConfig)
        with Agent.create(
            AgentOptions(
                api_key=self.settings.cursor_api_key,
                model=self.settings.cursor_model,
                local=LocalAgentOptions(cwd=str(workspace)),
                mcp_servers=servers or None,
            )
        ) as agent:
            run = agent.send(prompt)
            result = run.wait()
            return getattr(result, "result", None) or str(result.status)

    def _figma_block(self, context: GatheredContext) -> str:
        if not context.figma:
            return "(no Figma context)"
        parts = []
        for item in context.figma:
            parts.append(
                f"- {item.file_name or item.file_key} node={item.node_id} "
                f"frames={', '.join(item.frames[:8])} colors={', '.join(item.colors[:8])} {item.notes}"
            )
        return "\n".join(parts)

    def _memory_block(self, context: GatheredContext) -> str:
        memory = context.memory
        return "\n\n".join(
            block
            for block in (
                memory.architecture,
                memory.conventions,
                memory.project_structure,
                "\n".join(memory.recent_decisions),
            )
            if block.strip()
        )
