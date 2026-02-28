from __future__ import annotations

from diviora.schemas import PlanStep, TaskRequest


def validate_step(step: PlanStep, task: TaskRequest) -> tuple[bool, str]:
    if step.tool not in task.allowed_tools:
        return False, f"step tool not allowed: {step.tool}"
    if not step.expected_outputs:
        return False, "step expected_outputs missing"
    return True, "ok"
