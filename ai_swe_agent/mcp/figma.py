from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

import httpx

from ai_swe_agent.config import Settings
from ai_swe_agent.models import FigmaContext

FIGMA_PATH_RE = re.compile(
    r"/design/(?P<file>[A-Za-z0-9]+)|/file/(?P<file2>[A-Za-z0-9]+)"
)


def parse_figma_url(url: str) -> tuple[str | None, str | None]:
    parsed = urlparse(url)
    match = FIGMA_PATH_RE.search(parsed.path)
    file_key = None
    if match:
        file_key = match.group("file") or match.group("file2")
    query = parse_qs(parsed.query)
    raw_node = (query.get("node-id") or [None])[0]
    node_id = raw_node.replace("-", ":") if raw_node else None
    return file_key, node_id


class FigmaAdapter:
    """Figma MCP-facing adapter: file/frame, layout, components, styles, assets."""

    def __init__(self, settings: Settings, client: httpx.Client | None = None) -> None:
        self.settings = settings
        self._client = client

    def _http(self) -> httpx.Client:
        if self._client is not None:
            return self._client
        if not self.settings.figma_configured():
            raise RuntimeError("Figma is not configured. Set FIGMA_ACCESS_TOKEN.")
        self._client = httpx.Client(
            base_url="https://api.figma.com/v1",
            headers={"X-Figma-Token": self.settings.figma_access_token},
            timeout=30.0,
        )
        return self._client

    def from_url(self, url: str) -> FigmaContext:
        file_key, node_id = parse_figma_url(url)
        if not file_key:
            return FigmaContext(file_key="", notes=f"Could not parse Figma URL: {url}")
        if not self.settings.figma_configured() and self._client is None:
            return FigmaContext(
                file_key=file_key,
                node_id=node_id,
                notes="FIGMA_ACCESS_TOKEN not set; URL recorded only.",
            )
        return self.get_file(file_key, node_id)

    def get_file(self, file_key: str, node_id: str | None = None) -> FigmaContext:
        response = self._http().get(f"/files/{file_key}")
        response.raise_for_status()
        payload = response.json()
        document = payload.get("document") or {}
        frames, components, colors = self._walk(document)
        typography = self._typography(document)
        return FigmaContext(
            file_key=file_key,
            file_name=payload.get("name") or "",
            node_id=node_id,
            frames=frames[:40],
            components=components[:40],
            colors=sorted(set(colors))[:40],
            notes="; ".join(typography[:12]),
        )

    def get_styles(self, file_key: str) -> dict:
        context = self.get_file(file_key)
        response = self._http().get(f"/files/{file_key}")
        response.raise_for_status()
        named = []
        for style_id, style in (response.json().get("styles") or {}).items():
            named.append(
                {
                    "id": style_id,
                    "name": style.get("name"),
                    "type": style.get("styleType"),
                }
            )
        return {
            "colors": context.colors,
            "typography": [item for item in context.notes.split("; ") if item],
            "named_styles": named[:40],
        }

    def get_assets(self, file_key: str, node_ids: list[str] | None = None) -> dict:
        context = self.get_file(file_key)
        ids = node_ids or ([context.node_id] if context.node_id else [])
        if not ids:
            return {"file_key": file_key, "images": {}, "note": "Pass node_ids to export assets."}
        response = self._http().get(
            f"/images/{file_key}",
            params={"ids": ",".join(ids), "format": "png"},
        )
        response.raise_for_status()
        return {"file_key": file_key, "images": response.json().get("images") or {}}

    def _walk(self, node: dict) -> tuple[list[str], list[str], list[str]]:
        frames: list[str] = []
        components: list[str] = []
        colors: list[str] = []

        def visit(item: dict) -> None:
            name = item.get("name") or ""
            kind = item.get("type")
            if kind in {"FRAME", "SECTION", "COMPONENT_SET"} and name:
                frames.append(name)
            if kind in {"COMPONENT", "INSTANCE"} and name:
                components.append(name)
            fills = item.get("fills") or []
            for fill in fills:
                color = fill.get("color")
                if fill.get("type") == "SOLID" and isinstance(color, dict):
                    colors.append(
                        "#{r:02x}{g:02x}{b:02x}".format(
                            r=round(color.get("r", 0) * 255),
                            g=round(color.get("g", 0) * 255),
                            b=round(color.get("b", 0) * 255),
                        )
                    )
            for child in item.get("children") or []:
                visit(child)

        visit(node)
        return frames, components, colors

    def _typography(self, node: dict) -> list[str]:
        found: list[str] = []

        def visit(item: dict) -> None:
            style = item.get("style") or {}
            family = style.get("fontFamily")
            size = style.get("fontSize")
            if family and size:
                found.append(f"{family} {size}")
            for child in item.get("children") or []:
                visit(child)

        visit(node)
        return list(dict.fromkeys(found))
