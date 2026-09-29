from __future__ import annotations

import re
from collections.abc import Callable

from ai_swe_agent.config import Settings, load_settings
from ai_swe_agent.llm.engine import ReasoningEngine
from ai_swe_agent.mcp.figma import FigmaAdapter
from ai_swe_agent.mcp.github import GitHubAdapter
from ai_swe_agent.mcp.jira import JiraAdapter, extract_ticket_key, ticket_from_fields
from ai_swe_agent.memory.store import ProjectMemory
from ai_swe_agent.models import (
    DeliveryReport,
    ExecutionPlan,
    GatheredContext,
    Phase,
    PhaseStatus,
    TaskStep,
    TicketContext,
)
from ai_swe_agent.pipeline.build import BuildPipeline
from ai_swe_agent.pipeline.pull_request import PullRequestFlow
from ai_swe_agent.pipeline.review import ReviewAgent
from ai_swe_agent.tools.workspace import WorkspaceTools

LogFn = Callable[[str], None]


class AgentOrchestrator:
    """Four-phase loop: understand → gather → execute → deliver, with reflect."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        jira: JiraAdapter | None = None,
        figma: FigmaAdapter | None = None,
        github: GitHubAdapter | None = None,
        logger: LogFn | None = None,
    ) -> None:
        self.settings = settings or load_settings()
        self.jira = jira or JiraAdapter(self.settings)
        self.figma = figma or FigmaAdapter(self.settings)
        self.github = github or GitHubAdapter(self.settings)
        self.workspace = WorkspaceTools(self.settings)
        self.ios_workspace = WorkspaceTools(self.settings, root=self.settings.resolved_ios_app())
        self.memory = ProjectMemory(self.settings)
        self.llm = ReasoningEngine(self.settings)
        self.pipeline = BuildPipeline(self.ios_workspace, settings=self.settings)
        self.reviewer = ReviewAgent(self.ios_workspace)
        self.pr_flow = PullRequestFlow(self.github)
        self._log = logger or (lambda message: print(message, flush=True))

    def run(
        self,
        request: str,
        *,
        dry_run: bool = False,
        create_pr: bool = False,
        skip_tests: bool = False,
    ) -> DeliveryReport:
        report = DeliveryReport(request=request, dry_run=dry_run)
        try:
            ticket, plan = self.understand_and_plan(request)
            report.ticket_key = ticket.key
            report.plan = plan
            report.phases[Phase.UNDERSTAND] = PhaseStatus.PASSED
            self._reflect(report, f"Planned {len(plan.steps)} steps for {ticket.key}.")

            context = self.gather_context(ticket, plan)
            report.phases[Phase.GATHER] = PhaseStatus.PASSED
            self._reflect(report, f"Gathered codebase + {len(context.figma)} Figma file(s).")

            self.execute_and_iterate(context, dry_run=dry_run, skip_tests=skip_tests)
            report.pipeline = self.pipeline.run(skip_tests=True) if dry_run else self.pipeline.run(skip_tests=skip_tests)
            execute_ok = report.pipeline.compile_ok and report.pipeline.tests_ok
            report.phases[Phase.EXECUTE] = PhaseStatus.PASSED if execute_ok or dry_run else PhaseStatus.FAILED
            self._reflect(report, "Execute finished; pipeline logs captured.")

            if not execute_ok and not dry_run:
                report.phases[Phase.DELIVER] = PhaseStatus.SKIPPED
                self._reflect(report, "Delivery skipped because the pipeline failed.")
                return report

            review = self.reviewer.review(context, report.pipeline)
            if self.llm.available() and not dry_run:
                review.suggestions.append(self.llm.review(context, self.workspace.root))
            report.review = review

            pr = self.pr_flow.deliver(ticket, plan, dry_run=dry_run or not create_pr, create_pr=create_pr)
            if not create_pr and not dry_run:
                pr.skipped_reason = pr.skipped_reason or "create_pr=false"
            report.pull_request = pr
            report.phases[Phase.DELIVER] = PhaseStatus.PASSED
            self.memory.remember("delivered", f"{ticket.key}: {ticket.summary}", ticket.key)
        except Exception as exc:
            failed = next((phase for phase, status in report.phases.items() if status == PhaseStatus.RUNNING), None)
            if failed is None:
                pending = [phase for phase in Phase if phase not in report.phases]
                failed = pending[0] if pending else Phase.UNDERSTAND
            report.phases[failed] = PhaseStatus.FAILED
            self._reflect(report, f"Failed during {failed.value}: {exc}")
            raise
        return report

    def understand_and_plan(self, request: str) -> tuple[TicketContext, ExecutionPlan]:
        self._log("1. Understand & Plan")
        key = extract_ticket_key(request)
        if key and self.settings.jira_configured():
            ticket = self.jira.get_ticket_details(key)
        elif key:
            ticket = ticket_from_fields(key, summary=request, description=request)
        else:
            ticket = ticket_from_fields("LOCAL-0", summary=request, description=request)

        steps = [
            TaskStep(id=1, title="Read Jira ticket", detail=ticket.summary),
            TaskStep(id=2, title="Load Figma iOS screen", detail=", ".join(ticket.figma_urls) or "none"),
            TaskStep(id=3, title="Inspect SwiftUI app (MVVM-C)", detail=str(self.settings.resolved_ios_app())),
            TaskStep(id=4, title="Implement SwiftUI screen + view model"),
            TaskStep(id=5, title="xcodebuild test, review, PR"),
        ]
        slug = re.sub(r"[^a-z0-9-]+", "-", ticket.key.lower()).strip("-")
        plan = ExecutionPlan(
            ticket_key=ticket.key,
            goal=ticket.summary or request,
            steps=steps,
            branch_name=f"feature/{slug}",
            risks=["No Figma token"] if ticket.figma_urls and not self.settings.figma_configured() else [],
        )
        return ticket, plan

    def gather_context(self, ticket: TicketContext, plan: ExecutionPlan) -> GatheredContext:
        self._log("2. Gather Context")
        designs = []
        for url in ticket.figma_urls:
            designs.append(self.figma.from_url(url))
        codebase = self.ios_workspace.inspect()
        memory = self.memory.load()
        return GatheredContext(
            ticket=ticket,
            plan=plan,
            figma=designs,
            codebase=codebase,
            memory=memory,
        )

    def execute_and_iterate(
        self,
        context: GatheredContext,
        *,
        dry_run: bool,
        skip_tests: bool,
    ) -> str:
        self._log("3. Execute & Iterate")
        if dry_run:
            return "dry-run: skipped code changes"
        if self.llm.available():
            return self.llm.implement(context, self.workspace.root)
        self._log("CURSOR_API_KEY missing — skipping automated code edits.")
        return "cursor-sdk skipped"

    def _reflect(self, report: DeliveryReport, message: str) -> None:
        report.reflections.append(message)
        self._log(f"   reflect: {message}")
