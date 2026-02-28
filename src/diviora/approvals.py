from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from .schemas import ApprovalDecision, ApprovalMode, PlanStep


ApprovalFn = Callable[[PlanStep], ApprovalDecision]


def cli_approver(step: PlanStep) -> ApprovalDecision:
    answer = input(f"Approve step {step.step_id} ({step.title})? [y/N]: ").strip().lower()
    approved = answer in {"y", "yes"}
    reason = "user approved" if approved else "user denied"
    return ApprovalDecision(step_id=step.step_id, approved=approved, reason=reason)


def decide_approval(
    mode: ApprovalMode,
    step: PlanStep,
    approvals_path: Path,
    approval_fn: ApprovalFn | None = None,
) -> ApprovalDecision:
    if not step.requires_approval:
        decision = ApprovalDecision(step_id=step.step_id, approved=True, reason="not required")
    elif mode == ApprovalMode.auto:
        decision = ApprovalDecision(step_id=step.step_id, approved=True, reason="auto mode")
    else:
        fn = approval_fn or cli_approver
        decision = fn(step)

    with approvals_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(decision.model_dump(), sort_keys=True) + "\n")
    return decision
