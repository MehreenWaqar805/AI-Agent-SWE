from __future__ import annotations

import argparse
import sys

from ai_swe_agent.config import load_settings
from ai_swe_agent.orchestrator import AgentOrchestrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-swe-agent",
        description="iOS SWE agent: implement a Jira ticket as Swift/SwiftUI in ios/.",
    )
    parser.add_argument("request", nargs="?", help='Natural-language request, e.g. "Implement JIRA ticket SCRUM-1"')
    parser.add_argument("--ticket", help="Jira issue key, used if request has none")
    parser.add_argument("--dry-run", action="store_true", help="Plan and gather only; do not edit or open a PR")
    parser.add_argument("--create-pr", action="store_true", help="Push a branch and open a GitHub pull request")
    parser.add_argument("--skip-tests", action="store_true", help="Skip the unit-test step of the pipeline")
    parser.add_argument("--json", action="store_true", help="Print the delivery report as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    request = args.request or (f"Implement JIRA ticket {args.ticket}" if args.ticket else None)
    if not request:
        parser.error("Provide a request or --ticket")

    settings = load_settings()
    orchestrator = AgentOrchestrator(settings)
    try:
        report = orchestrator.run(
            request,
            dry_run=args.dry_run,
            create_pr=args.create_pr,
            skip_tests=args.skip_tests,
        )
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(report.model_dump_json(indent=2))
    else:
        print()
        print(f"Ticket: {report.ticket_key}")
        for phase, status in report.phases.items():
            print(f"  {phase.value}: {status.value}")
        if report.pull_request and report.pull_request.url:
            print(f"PR: {report.pull_request.url}")
        if report.review:
            print(f"Review: {report.review.verdict.value}")
            for finding in report.review.findings:
                print(f"  - {finding}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
