from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Phase(str, Enum):
    UNDERSTAND = "understand_and_plan"
    GATHER = "gather_context"
    EXECUTE = "execute_and_iterate"
    DELIVER = "deliver"


class PhaseStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TicketContext(BaseModel):
    key: str
    summary: str
    description: str = ""
    acceptance_criteria: list[str] = Field(default_factory=list)
    status: str = ""
    assignee: str | None = None
    priority: str | None = None
    issue_type: str | None = None
    labels: list[str] = Field(default_factory=list)
    attachments: list[dict[str, Any]] = Field(default_factory=list)
    linked_tickets: list[str] = Field(default_factory=list)
    figma_urls: list[str] = Field(default_factory=list)
    url: str | None = None


class FigmaContext(BaseModel):
    file_key: str
    file_name: str = ""
    node_id: str | None = None
    frames: list[str] = Field(default_factory=list)
    components: list[str] = Field(default_factory=list)
    colors: list[str] = Field(default_factory=list)
    notes: str = ""


class MemorySnapshot(BaseModel):
    architecture: str = ""
    conventions: str = ""
    project_structure: str = ""
    api_patterns: str = ""
    design_system: str = ""
    recent_decisions: list[str] = Field(default_factory=list)


class TaskStep(BaseModel):
    id: int
    title: str
    detail: str = ""
    done: bool = False


class ExecutionPlan(BaseModel):
    ticket_key: str
    goal: str
    steps: list[TaskStep] = Field(default_factory=list)
    branch_name: str = ""
    risks: list[str] = Field(default_factory=list)


class CodebaseContext(BaseModel):
    workspace_root: str
    languages: list[str] = Field(default_factory=list)
    top_level: list[str] = Field(default_factory=list)
    notes: str = ""


class GatheredContext(BaseModel):
    ticket: TicketContext
    plan: ExecutionPlan
    figma: list[FigmaContext] = Field(default_factory=list)
    codebase: CodebaseContext | None = None
    memory: MemorySnapshot = Field(default_factory=MemorySnapshot)


class PipelineResult(BaseModel):
    compile_ok: bool = True
    tests_ok: bool = True
    quality_ok: bool = True
    commands: list[str] = Field(default_factory=list)
    logs: str = ""


class ReviewVerdict(str, Enum):
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"


class ReviewResult(BaseModel):
    verdict: ReviewVerdict
    findings: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class PullRequestResult(BaseModel):
    created: bool = False
    url: str | None = None
    branch: str = ""
    title: str = ""
    skipped_reason: str | None = None


class DeliveryReport(BaseModel):
    request: str
    ticket_key: str | None = None
    phases: dict[Phase, PhaseStatus] = Field(default_factory=dict)
    plan: ExecutionPlan | None = None
    pipeline: PipelineResult | None = None
    pull_request: PullRequestResult | None = None
    review: ReviewResult | None = None
    reflections: list[str] = Field(default_factory=list)
    dry_run: bool = False
