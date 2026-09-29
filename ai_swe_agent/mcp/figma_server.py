from __future__ import annotations

from ai_swe_agent.config import load_settings
from ai_swe_agent.mcp.figma import FigmaAdapter

try:
    from mcp.server import MCPServer
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install the mcp package to run the Figma MCP server.") from exc

mcp = MCPServer("figma")
_adapter: FigmaAdapter | None = None


def _figma() -> FigmaAdapter:
    global _adapter
    if _adapter is None:
        _adapter = FigmaAdapter(load_settings())
    return _adapter


@mcp.tool()
def get_file(file_key: str, node_id: str = "") -> dict:
    """Get a Figma file: frames, components, colors, and typography."""
    return _figma().get_file(file_key, node_id or None).model_dump()


@mcp.tool()
def get_file_from_url(url: str) -> dict:
    """Resolve a Figma URL to file/frame context, layouts, and styles."""
    return _figma().from_url(url).model_dump()


@mcp.tool()
def get_layouts(file_key: str) -> list[str]:
    """List UI frames and sections in a Figma file."""
    return _figma().get_file(file_key).frames


@mcp.tool()
def get_components(file_key: str) -> list[str]:
    """List components and instances in a Figma file."""
    return _figma().get_file(file_key).components


@mcp.tool()
def get_styles(file_key: str) -> dict:
    """Get colors, typography, and named styles from a Figma file."""
    return _figma().get_styles(file_key)


@mcp.tool()
def get_assets(file_key: str, node_ids: str = "") -> dict:
    """Get export URLs for Figma nodes. Pass comma-separated node ids, or omit for top frames."""
    ids = [item.strip() for item in node_ids.split(",") if item.strip()]
    return _figma().get_assets(file_key, ids or None)
