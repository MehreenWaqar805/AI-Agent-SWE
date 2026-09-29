from ai_swe_agent.mcp.figma import parse_figma_url


def test_parse_figma_url() -> None:
    url = "https://www.figma.com/design/7iabHUyQa2JY031YGU54g8/Movies-app--Community-?node-id=0-1&p=f"
    file_key, node_id = parse_figma_url(url)
    assert file_key == "7iabHUyQa2JY031YGU54g8"
    assert node_id == "0:1"
