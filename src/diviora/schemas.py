from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from diviora.runtime_deps import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class TaskType(str, Enum):
    research_report = "research_report"
    code_task = "code_task"


class ApprovalMode(str, Enum):
    manual = "manual"
    auto = "auto"


class TaskRequest(StrictModel):
    task_id: str
    task_type: TaskType
    goal: str
    constraints: list[str] = Field(default_factory=list)
    allowed_tools: list[str]
    approval_mode: ApprovalMode
    context_notes: list[str] = Field(default_factory=list)
    commands: list[list[str]] = Field(default_factory=list)

    @field_validator("task_type", mode="before")
    @classmethod
    def _coerce_task_type(cls, value: TaskType | str) -> TaskType:
        return value if isinstance(value, TaskType) else TaskType(value)

    @field_validator("approval_mode", mode="before")
    @classmethod
    def _coerce_approval_mode(cls, value: ApprovalMode | str) -> ApprovalMode:
        return value if isinstance(value, ApprovalMode) else ApprovalMode(value)


class PlanStep(StrictModel):
    step_id: str
    title: str
    description: str
    tool: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool
    expected_outputs: list[str]


class Plan(StrictModel):
    plan_id: str
    task_id: str
    summary: str
    steps: list[PlanStep]
    expected_artifacts: list[str]
    success_criteria: list[str]


class ApprovalDecision(StrictModel):
    step_id: str
    approved: bool
    reason: str


class StepStatus(str, Enum):
    success = "success"
    failed = "failed"
    rejected = "rejected"


class StepResult(StrictModel):
    step_id: str
    status: StepStatus
    stdout: str
    stderr: str
    artifact_paths: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class VerificationResult(StrictModel):
    passed: bool
    checks: list[str]
    failures: list[str]
    evidence_paths: list[str]


class RunOutcome(StrictModel):
    run_id: str
    task_id: str
    status: Literal["PASS", "FAIL"]
    reason: str
    artifact_paths: list[str] = Field(default_factory=list)
