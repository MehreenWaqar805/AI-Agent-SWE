# AI Software Engineering Agent

iOS software-engineering agent. It takes a Jira ticket + Figma screen and implements **Swift/SwiftUI** in `ios/MoviesApp` (MVVM-C), then runs `xcodebuild`, reviews, and can open a PR.

```text
User request → Orchestrator (plan / act / verify / reflect)
  MCP: Jira, Figma, GitHub
  Tools: read / write / search / modify / run / git
  Memory: architecture, conventions, decisions
  Pipeline → PR → review
```

## Setup

```bash
.venv/bin/python -m pip install -e ".[dev]"
cp .env.example .env
```

Fill in Jira, Figma, GitHub, and `CURSOR_API_KEY` as needed.

## Run

```bash
.venv/bin/python -m ai_swe_agent --dry-run "Implement JIRA ticket SCRUM-1"
.venv/bin/python -m ai_swe_agent "Implement JIRA ticket SCRUM-1"
open ios/MoviesApp.xcodeproj
```

Local MCP servers (stdio):

```bash
.venv/bin/python jira-mcp-server/jira_server.py
.venv/bin/python figma-mcp-server/figma_server.py
.venv/bin/python github-mcp-server/github_server.py
```

Official remotes are also attached: Figma `https://mcp.figma.com/mcp` and GitHub `https://api.githubcopilot.com/mcp/`. Project Cursor config is in `.cursor/mcp.json`.
