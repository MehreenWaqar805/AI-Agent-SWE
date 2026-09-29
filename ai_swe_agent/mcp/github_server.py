from __future__ import annotations

from ai_swe_agent.config import load_settings
from ai_swe_agent.mcp.github import GitHubAdapter

try:
    from mcp.server import MCPServer
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install the mcp package to run the GitHub MCP server.") from exc

mcp = MCPServer("github")
_adapter: GitHubAdapter | None = None


def _github() -> GitHubAdapter:
    global _adapter
    if _adapter is None:
        _adapter = GitHubAdapter(load_settings())
    return _adapter


@mcp.tool()
def get_repository() -> dict:
    """Get the current repository remote, branch, owner, and name."""
    return _github().repo_identity()


@mcp.tool()
def search_code(query: str) -> str:
    """Search the local repository for a code pattern."""
    return _github().search_code(query)


@mcp.tool()
def read_file(path: str) -> str:
    """Read a file from the local checkout."""
    return _github().read_file(path)


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write a file in the local checkout (does not commit)."""
    return _github().write_file(path, content)


@mcp.tool()
def create_branch(name: str, start_point: str = "") -> str:
    """Create or check out a git branch."""
    return _github().create_branch(name, start_point or None)


@mcp.tool()
def create_pull_request(title: str, body: str, base: str = "") -> str:
    """Open a GitHub pull request from the current branch."""
    return _github().create_pull_request(title, body, base or None)


@mcp.tool()
def list_webhooks() -> list[dict]:
    """List webhooks configured on the GitHub repository."""
    return _github().list_webhooks()
