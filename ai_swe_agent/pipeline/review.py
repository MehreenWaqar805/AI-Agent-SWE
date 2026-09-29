from __future__ import annotations

from ai_swe_agent.models import GatheredContext, PipelineResult, ReviewResult, ReviewVerdict
from ai_swe_agent.tools.workspace import WorkspaceTools


class ReviewAgent:
    """Architecture, quality, security, and convention review of the working tree."""

    def __init__(self, workspace: WorkspaceTools) -> None:
        self.workspace = workspace

    def review(self, context: GatheredContext, pipeline: PipelineResult) -> ReviewResult:
        findings: list[str] = []
        suggestions: list[str] = []

        if not pipeline.compile_ok:
            findings.append("Build/compile step failed.")
        if not pipeline.tests_ok:
            findings.append("Unit tests failed.")
        if not pipeline.quality_ok:
            findings.append("Quality checks failed.")

        if not context.ticket.acceptance_criteria:
            suggestions.append("Add explicit acceptance criteria on the Jira ticket.")
        if context.ticket.figma_urls and not context.figma:
            findings.append("Ticket links Figma but no design context was loaded.")
        if not context.codebase or not context.codebase.top_level:
            suggestions.append("iOS workspace looks empty; confirm IOS_APP_PATH.")
        if context.codebase and "swift" not in context.codebase.languages:
            findings.append("No Swift files under the iOS app path.")
        force_unwraps = [
            hit
            for hit in self.workspace.search_code(r"\w+!", glob="*.swift")
            if "XCTest" not in hit and "fatalError" not in hit
        ]
        if force_unwraps:
            suggestions.append("Avoid force unwraps in Swift production code.")

        secrets = [
            hit
            for hit in self.workspace.search_code(
                r"(?i)(?:^|[^A-Za-z0-9_])(?:api[_-]?token|client_secret|password)\s*=\s*['\"][^'\"]+['\"]"
            )
            if not hit.startswith("tests/")
        ]
        if secrets:
            findings.append("Possible hardcoded secret found in the workspace.")

        verdict = ReviewVerdict.CHANGES_REQUESTED if findings else ReviewVerdict.APPROVED
        return ReviewResult(verdict=verdict, findings=findings, suggestions=suggestions)
