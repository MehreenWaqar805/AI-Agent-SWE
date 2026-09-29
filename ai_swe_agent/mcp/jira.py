from __future__ import annotations

import re
from typing import Any

import httpx

from ai_swe_agent.config import Settings
from ai_swe_agent.models import TicketContext

TICKET_KEY_RE = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")
FIGMA_URL_RE = re.compile(r"https://[\w.-]*figma\.com/[^\s)]+", re.IGNORECASE)
CRITERIA_LINE_RE = re.compile(
    r"^\s*(?:[-*]|\d+\.)\s+(?:\[.\]\s+)?(.+)$",
    re.MULTILINE,
)


def extract_ticket_key(text: str) -> str | None:
    match = TICKET_KEY_RE.search(text.upper())
    return match.group(1) if match else None


def extract_figma_urls(text: str) -> list[str]:
    return list(dict.fromkeys(FIGMA_URL_RE.findall(text or "")))


def extract_acceptance_criteria(description: str) -> list[str]:
    if not description:
        return []
    lowered = description.lower()
    marker = None
    for label in ("acceptance criteria", "acceptance criterion", "ac:"):
        idx = lowered.find(label)
        if idx != -1:
            marker = idx
            break
    block = description[marker:] if marker is not None else description
    items = [line.strip() for line in CRITERIA_LINE_RE.findall(block)]
    return [item for item in items if item and not item.lower().startswith("acceptance")]


def _adf_to_text(node: Any) -> str:
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(_adf_to_text(child) for child in node)
    if not isinstance(node, dict):
        return str(node)
    node_type = node.get("type")
    text = node.get("text", "")
    content = _adf_to_text(node.get("content", []))
    hrefs = []
    attrs = node.get("attrs") or {}
    if attrs.get("url"):
        hrefs.append(str(attrs["url"]))
    if attrs.get("href"):
        hrefs.append(str(attrs["href"]))
    for mark in node.get("marks") or []:
        mark_attrs = (mark or {}).get("attrs") or {}
        if mark_attrs.get("href"):
            hrefs.append(str(mark_attrs["href"]))
    extra = (" " + " ".join(hrefs)) if hrefs else ""
    if node_type in {"paragraph", "heading", "blockquote", "listItem"}:
        return f"{text}{content}{extra}\n"
    if node_type == "hardBreak":
        return "\n"
    return f"{text}{content}{extra}"


class JiraAdapter:
    """Jira MCP-facing adapter: ticket details, AC, attachments, linked issues."""

    def __init__(self, settings: Settings, client: httpx.Client | None = None) -> None:
        self.settings = settings
        self._client = client

    def _http(self) -> httpx.Client:
        if self._client is not None:
            return self._client
        if not self.settings.jira_configured():
            raise RuntimeError(
                "Jira is not configured. Set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN."
            )
        self._client = httpx.Client(
            base_url=self.settings.jira_base_url.rstrip("/"),
            auth=(self.settings.jira_email, self.settings.jira_api_token),
            headers={"Accept": "application/json"},
            timeout=30.0,
        )
        return self._client

    def get_ticket_details(self, issue_key: str) -> TicketContext:
        response = self._http().get(
            f"/rest/api/3/issue/{issue_key}",
            params={
                "fields": "summary,description,status,assignee,priority,issuetype,labels,attachment,issuelinks",
            },
        )
        response.raise_for_status()
        return self._to_ticket(response.json())

    def get_description(self, issue_key: str) -> str:
        return self.get_ticket_details(issue_key).description

    def get_acceptance_criteria(self, issue_key: str) -> list[str]:
        return self.get_ticket_details(issue_key).acceptance_criteria

    def get_attachments(self, issue_key: str) -> list[dict[str, Any]]:
        return self.get_ticket_details(issue_key).attachments

    def get_linked_tickets(self, issue_key: str) -> list[str]:
        return self.get_ticket_details(issue_key).linked_tickets

    def _to_ticket(self, payload: dict[str, Any]) -> TicketContext:
        fields = payload.get("fields") or {}
        description = _adf_to_text(fields.get("description"))
        attachments = []
        for item in fields.get("attachment") or []:
            attachments.append(
                {
                    "id": item.get("id"),
                    "filename": item.get("filename"),
                    "mimeType": item.get("mimeType"),
                    "content": item.get("content"),
                }
            )
        linked: list[str] = []
        for link in fields.get("issuelinks") or []:
            for side in ("outwardIssue", "inwardIssue"):
                key = (link.get(side) or {}).get("key")
                if key:
                    linked.append(key)
        assignee = fields.get("assignee") or {}
        base = self.settings.jira_base_url.rstrip("/")
        key = payload.get("key", "")
        return TicketContext(
            key=key,
            summary=fields.get("summary") or "",
            description=description.strip(),
            acceptance_criteria=extract_acceptance_criteria(description),
            status=((fields.get("status") or {}).get("name") or ""),
            assignee=assignee.get("displayName"),
            priority=((fields.get("priority") or {}).get("name")),
            issue_type=((fields.get("issuetype") or {}).get("name")),
            labels=list(fields.get("labels") or []),
            attachments=attachments,
            linked_tickets=linked,
            figma_urls=extract_figma_urls(description),
            url=f"{base}/browse/{key}" if base and key else None,
        )


def ticket_from_fields(
    key: str,
    summary: str,
    description: str = "",
    **extra: Any,
) -> TicketContext:
    return TicketContext(
        key=key,
        summary=summary,
        description=description,
        acceptance_criteria=extract_acceptance_criteria(description),
        figma_urls=extract_figma_urls(description),
        **extra,
    )
