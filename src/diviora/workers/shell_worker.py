from __future__ import annotations

import subprocess
from typing import Any

from diviora.schemas import StepResult, StepStatus, WorkerExecutionMode, WorkerRuntime
from diviora.workers.base import Worker


class ShellWorker(Worker):
    def __init__(self, allowlist: tuple[str, ...]) -> None:
        self.allowlist = allowlist
        self.worker_id = "shell.local"
        self.worker_type = "shell"
        self.worker_runtime = WorkerRuntime.local
        self.execution_mode = WorkerExecutionMode.synchronous

    def execute(self, step_id: str, inputs: dict[str, Any], requires_approval: bool) -> StepResult:
        command = inputs.get("command")
        if not isinstance(command, list) or not command:
            return StepResult(
                step_id=step_id,
                status=StepStatus.failed,
                worker_id=self.worker_id,
                worker_type=self.worker_type,
                worker_runtime=self.worker_runtime,
                execution_mode=self.execution_mode,
                requires_approval=requires_approval,
                step_inputs=inputs,
                stdout="",
                stderr="invalid command format",
                artifact_paths=[],
                metadata={"worker": "shell"},
            )

        root = command[0]
        if root not in self.allowlist:
            return StepResult(
                step_id=step_id,
                status=StepStatus.rejected,
                worker_id=self.worker_id,
                worker_type=self.worker_type,
                worker_runtime=self.worker_runtime,
                execution_mode=self.execution_mode,
                requires_approval=requires_approval,
                step_inputs=inputs,
                stdout="",
                stderr=f"command root not allowed: {root}",
                artifact_paths=[],
                metadata={"worker": "shell", "rejected": True},
            )

        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        status = StepStatus.success if completed.returncode == 0 else StepStatus.failed
        return StepResult(
            step_id=step_id,
            status=status,
            worker_id=self.worker_id,
            worker_type=self.worker_type,
            worker_runtime=self.worker_runtime,
            execution_mode=self.execution_mode,
            requires_approval=requires_approval,
            step_inputs=inputs,
            stdout=completed.stdout,
            stderr=completed.stderr,
            artifact_paths=[],
            metadata={"worker": "shell", "returncode": completed.returncode},
        )
