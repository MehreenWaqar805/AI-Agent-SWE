from __future__ import annotations

from ai_swe_agent.mcp.github import GitHubAdapter
from ai_swe_agent.models import ExecutionPlan, PullRequestResult, TicketContext


class PullRequestFlow:
    def __init__(self, github: GitHubAdapter) -> None:
        self.github = github

    def deliver(
        self,
        ticket: TicketContext,
        plan: ExecutionPlan,
        *,
        dry_run: bool = False,
        create_pr: bool = True,
    ) -> PullRequestResult:
        branch = plan.branch_name or f"feature/{ticket.key.lower()}"
        title = f"{ticket.key}: {ticket.summary}"
        body = self.github.format_pr_body(ticket.key, ticket.url, ticket.summary)
        if dry_run:
            return PullRequestResult(
                created=False,
                branch=branch,
                title=title,
                skipped_reason="dry-run",
            )
        try:
            self.github.create_branch(branch)
            self.github.commit(title)
            self.github.push(branch)
            if not create_pr:
                return PullRequestResult(created=False, branch=branch, title=title, skipped_reason="create_pr=false")
            url = self.github.create_pull_request(title, body).strip()
            return PullRequestResult(created=True, url=url or None, branch=branch, title=title)
        except RuntimeError as exc:
            return PullRequestResult(
                created=False,
                branch=branch,
                title=title,
                skipped_reason=str(exc),
            )
