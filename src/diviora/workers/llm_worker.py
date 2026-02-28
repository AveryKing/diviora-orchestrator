from __future__ import annotations

from typing import Any, Callable

from diviora.schemas import StepResult, StepStatus, WorkerExecutionMode, WorkerRuntime
from diviora.workers.base import Worker


LLMCallable = Callable[[str, dict[str, Any]], str]


def default_stub(prompt: str, context: dict[str, Any]) -> str:
    goal = context.get("goal", "")
    if "research report" in prompt.lower() or context.get("task_type") == "research_report":
        return (
            "# Objective\n"
            f"{goal}\n\n"
            "# Options\n"
            "- Option A\n- Option B\n\n"
            "# Risks\n"
            "- Risk 1\n\n"
            "# Recommendation\n"
            "Choose Option A for determinism.\n\n"
            "# Next Steps\n"
            "1. Execute approved actions.\n"
        )
    return f"Generated content for: {goal}".strip()


class LLMWorker(Worker):
    def __init__(self, responder: LLMCallable | None = None) -> None:
        self._responder = responder or default_stub
        self.worker_id = "llm.local.stub"
        self.worker_type = "llm"
        self.worker_runtime = WorkerRuntime.local
        self.execution_mode = WorkerExecutionMode.synchronous

    def execute(self, step_id: str, inputs: dict[str, Any], requires_approval: bool) -> StepResult:
        prompt = str(inputs.get("prompt", ""))
        context = inputs.get("context", {})
        output = self._responder(prompt, context)
        return StepResult(
            step_id=step_id,
            status=StepStatus.success,
            worker_id=self.worker_id,
            worker_type=self.worker_type,
            worker_runtime=self.worker_runtime,
            execution_mode=self.execution_mode,
            requires_approval=requires_approval,
            step_inputs=inputs,
            stdout=output,
            stderr="",
            artifact_paths=[],
            metadata={"worker": "llm"},
        )
