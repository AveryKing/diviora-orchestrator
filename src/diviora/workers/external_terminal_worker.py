from __future__ import annotations

from pathlib import Path
from typing import Any

from diviora.schemas import StepResult, StepStatus, WorkerExecutionMode, WorkerRuntime
from diviora.workers.base import Worker


class ExternalTerminalWorker(Worker):
    """Scaffold worker for future external terminal execution lanes.

    This worker intentionally does not perform remote execution in v0.
    It records a deterministic placeholder artifact and fails closed.
    """

    def __init__(self, artifacts_dir: Path) -> None:
        self._artifacts_dir = artifacts_dir
        self.worker_id = "external.terminal.scaffold"
        self.worker_type = "external_terminal"
        self.worker_runtime = WorkerRuntime.external
        self.execution_mode = WorkerExecutionMode.unsupported

    def execute(self, step_id: str, inputs: dict[str, Any], requires_approval: bool) -> StepResult:
        requested_mode = str(inputs.get("mode", "execute"))
        artifact_paths: list[str] = []

        if requested_mode == "inspect":
            status = StepStatus.success
            stdout = "external terminal inspection only; no side effects"
            stderr = ""
        elif not requires_approval:
            status = StepStatus.rejected
            stdout = ""
            stderr = "external terminal lane requires approval for side-effectful execution"
        else:
            status = StepStatus.not_implemented
            stdout = ""
            stderr = "external terminal execution is not implemented in v0 scaffold"

        placeholder = self._artifacts_dir / f"{step_id}_external_terminal_scaffold.json"
        placeholder.write_text(
            (
                "{\n"
                f'  "step_id": "{step_id}",\n'
                f'  "worker_id": "{self.worker_id}",\n'
                f'  "requested_mode": "{requested_mode}",\n'
                f'  "requires_approval": {str(requires_approval).lower()},\n'
                f'  "status": "{status.value}",\n'
                '  "note": "scaffold only; no external execution performed"\n'
                "}\n"
            ),
            encoding="utf-8",
        )
        artifact_paths.append(str(placeholder))

        return StepResult(
            step_id=step_id,
            status=status,
            worker_id=self.worker_id,
            worker_type=self.worker_type,
            worker_runtime=self.worker_runtime,
            execution_mode=self.execution_mode,
            requires_approval=requires_approval,
            step_inputs=inputs,
            stdout=stdout,
            stderr=stderr,
            artifact_paths=artifact_paths,
            metadata={
                "worker": self.worker_type,
                "scaffold": True,
                "supported": False,
                "requested_mode": requested_mode,
            },
        )
