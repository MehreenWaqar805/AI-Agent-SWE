from ai_swe_agent.mcp.jira import (
    _adf_to_text,
    extract_acceptance_criteria,
    extract_figma_urls,
    extract_ticket_key,
    ticket_from_fields,
)


def test_extract_ticket_key() -> None:
    assert extract_ticket_key("Implement JIRA ticket SCRUM-1") == "SCRUM-1"
    assert extract_ticket_key("please do mob-1234 now") == "MOB-1234"
    assert extract_ticket_key("no ticket here") is None


def test_extract_figma_and_criteria() -> None:
    description = """
    Design Home Screen
    https://www.figma.com/design/7iabHUyQa2JY031YGU54g8/Movies-app?node-id=0-1

    Acceptance criteria
    - Home shows trending movies
    - Search icon opens search
    """
    ticket = ticket_from_fields("SCRUM-1", "TM-201", description)
    assert ticket.figma_urls
    assert "7iabHUyQa2JY031YGU54g8" in ticket.figma_urls[0]
    assert extract_acceptance_criteria(description) == [
        "Home shows trending movies",
        "Search icon opens search",
    ]


def test_adf_inline_figma_link() -> None:
    adf = {
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "Design Home Screen"},
                    {
                        "type": "inlineCard",
                        "attrs": {
                            "url": "https://www.figma.com/design/7iabHUyQa2JY031YGU54g8/Movies-app"
                        },
                    },
                ],
            }
        ],
    }
    text = _adf_to_text(adf)
    assert extract_figma_urls(text)
