from __future__ import annotations

from diviora.schemas import Plan, TaskRequest

FORBIDDEN_TOOLS = {"browser", "network", "filesystem_delete"}


def validate_plan(plan: Plan, task: TaskRequest) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not plan.steps:
        errors.append("plan has no steps")
    if len(plan.steps) > 8:
        errors.append("plan exceeds max step count 8")
    if not plan.expected_artifacts:
        errors.append("plan expected_artifacts required")

    step_ids = [s.step_id for s in plan.steps]
    if len(step_ids) != len(set(step_ids)):
        errors.append("duplicate step_ids")

    for step in plan.steps:
        if step.tool in FORBIDDEN_TOOLS:
            errors.append(f"forbidden tool: {step.tool}")
        if step.tool not in task.allowed_tools:
            errors.append(f"tool not in allowed_tools: {step.tool}")
        if not step.expected_outputs:
            errors.append(f"step missing expected_outputs: {step.step_id}")

    return (len(errors) == 0, errors)
