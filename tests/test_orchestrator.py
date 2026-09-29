from ai_swe_agent.config import Settings
from ai_swe_agent.mcp.jira import ticket_from_fields
from ai_swe_agent.models import Phase, PhaseStatus
from ai_swe_agent.orchestrator import AgentOrchestrator


class FakeJira:
    def get_ticket_details(self, issue_key: str):
        return ticket_from_fields(
            issue_key,
            "Design Home Screen",
            "Build home\nhttps://www.figma.com/design/Abc123xyz99/Movies?node-id=1-2\n",
            status="To Do",
        )


def test_dry_run_implements_phases(tmp_path) -> None:
    (tmp_path / "src").mkdir()
    settings = Settings(
        workspace_root=tmp_path,
        memory_dir=tmp_path / "memory",
        jira_base_url="https://example.atlassian.net",
        jira_email="dev@example.com",
        jira_api_token="token",
    )
    logs: list[str] = []
    orchestrator = AgentOrchestrator(
        settings,
        jira=FakeJira(),
        logger=logs.append,
    )
    report = orchestrator.run("Implement JIRA ticket SCRUM-1", dry_run=True)
    assert report.ticket_key == "SCRUM-1"
    assert report.plan and report.plan.branch_name == "feature/scrum-1"
    assert any("SwiftUI" in step.title for step in report.plan.steps)
    assert report.phases[Phase.UNDERSTAND] == PhaseStatus.PASSED
    assert report.phases[Phase.GATHER] == PhaseStatus.PASSED
    assert report.phases[Phase.EXECUTE] == PhaseStatus.PASSED
    assert report.phases[Phase.DELIVER] == PhaseStatus.PASSED
    assert report.pull_request and report.pull_request.skipped_reason == "dry-run"
    assert any("Understand" in line for line in logs)
