from __future__ import annotations

from ai_swe_agent.config import load_settings
from ai_swe_agent.mcp.jira import JiraAdapter

try:
    from mcp.server import MCPServer
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install the mcp package to run the Jira MCP server.") from exc

mcp = MCPServer("jira")
_adapter: JiraAdapter | None = None


def _jira() -> JiraAdapter:
    global _adapter
    if _adapter is None:
        _adapter = JiraAdapter(load_settings())
    return _adapter


@mcp.tool()
def get_ticket_details(issue_key: str) -> dict:
    """Get Jira ticket details: summary, description, status, assignee, priority."""
    return _jira().get_ticket_details(issue_key).model_dump()


@mcp.tool()
def get_description(issue_key: str) -> str:
    """Read the Jira ticket description as plain text."""
    return _jira().get_description(issue_key)


@mcp.tool()
def get_acceptance_criteria(issue_key: str) -> list[str]:
    """Extract acceptance criteria from the Jira description."""
    return _jira().get_acceptance_criteria(issue_key)


@mcp.tool()
def get_attachments(issue_key: str) -> list[dict]:
    """List attachments on a Jira ticket."""
    return _jira().get_attachments(issue_key)


@mcp.tool()
def get_linked_tickets(issue_key: str) -> list[str]:
    """List issue keys linked to this Jira ticket."""
    return _jira().get_linked_tickets(issue_key)
