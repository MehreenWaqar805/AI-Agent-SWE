from ai_swe_agent.config import Settings
from ai_swe_agent.llm.engine import ReasoningEngine
from ai_swe_agent.mcp.figma_server import mcp as figma_mcp
from ai_swe_agent.mcp.github import parse_github_remote
from ai_swe_agent.mcp.github_server import mcp as github_mcp
from ai_swe_agent.mcp.jira_server import mcp as jira_mcp


def test_parse_github_remote() -> None:
    host = "github.com"
    assert parse_github_remote(f"git@{host}:acme/movies.git") == ("acme", "movies")
    assert parse_github_remote(f"https://{host}/acme/movies.git") == ("acme", "movies")


def test_local_mcp_servers_register_tools() -> None:
    assert {tool.name for tool in jira_mcp._tool_manager.list_tools()} >= {
        "get_ticket_details",
        "get_description",
        "get_acceptance_criteria",
        "get_attachments",
        "get_linked_tickets",
    }
    assert {tool.name for tool in figma_mcp._tool_manager.list_tools()} >= {
        "get_file",
        "get_file_from_url",
        "get_layouts",
        "get_components",
        "get_styles",
        "get_assets",
    }
    assert {tool.name for tool in github_mcp._tool_manager.list_tools()} >= {
        "get_repository",
        "search_code",
        "read_file",
        "write_file",
        "create_branch",
        "create_pull_request",
        "list_webhooks",
    }


def test_engine_attaches_figma_and_github(tmp_path) -> None:
    settings = Settings(workspace_root=tmp_path, memory_dir=tmp_path / "memory", github_token="")
    servers = ReasoningEngine(settings).mcp_servers()
    assert "figma" in servers and servers["figma"]["url"] == "https://mcp.figma.com/mcp"
    assert "github" in servers and servers["github"]["url"] == "https://api.githubcopilot.com/mcp/"
    assert "figma-local" in servers
    assert "github-local" in servers
    assert "jira-local" in servers
    assert servers["figma-local"]["args"][-1].endswith("figma-mcp-server/figma_server.py")
    assert servers["github-local"]["args"][-1].endswith("github-mcp-server/github_server.py")
