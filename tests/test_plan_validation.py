from diviora.schemas import Plan, PlanStep, TaskRequest
from diviora.validation.validate_plan import validate_plan


def test_forbidden_tool_rejected() -> None:
    task = TaskRequest(
        task_id="t1",
        task_type="research_report",
        goal="g",
        constraints=[],
        allowed_tools=["llm"],
        approval_mode="auto",
    )
    plan = Plan(
        plan_id="p1",
        task_id="t1",
        summary="s",
        steps=[
            PlanStep(
                step_id="s1",
                title="x",
                description="d",
                tool="browser",
                inputs={},
                requires_approval=False,
                expected_outputs=["o"],
            )
        ],
        expected_artifacts=["a"],
        success_criteria=["ok"],
    )
    ok, errors = validate_plan(plan, task)
    assert not ok
    assert any("forbidden tool" in error for error in errors)
