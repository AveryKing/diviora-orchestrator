import pytest
from diviora.runtime_deps import ValidationError
from diviora.schemas import PlanStep, TaskRequest


def test_task_request_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        TaskRequest(
            task_id="t1",
            task_type="research_report",
            goal="g",
            constraints=[],
            allowed_tools=["llm"],
            approval_mode="auto",
            unexpected=True,
        )


def test_plan_step_requires_expected_outputs() -> None:
    with pytest.raises(ValidationError):
        PlanStep(
            step_id="s1",
            title="x",
            description="d",
            tool="llm",
            inputs={},
            requires_approval=False,
            expected_outputs="not-a-list",
        )
