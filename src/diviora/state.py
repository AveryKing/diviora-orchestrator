from __future__ import annotations

from typing import TypedDict

from .schemas import Plan, RunOutcome, StepResult, TaskRequest, VerificationResult


class RunState(TypedDict, total=False):
    run_id: str
    run_dir: str
    task_request: TaskRequest
    plan: Plan
    plan_valid: bool
    approvals: list[dict]
    step_results: list[StepResult]
    verification: VerificationResult
    outcome: RunOutcome
    error: str
