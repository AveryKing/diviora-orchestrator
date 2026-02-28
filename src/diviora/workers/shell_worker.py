from __future__ import annotations

import subprocess
from typing import Any

from diviora.schemas import StepResult, StepStatus


class ShellWorker:
    def __init__(self, allowlist: tuple[str, ...]) -> None:
        self.allowlist = allowlist

    def execute(self, step_id: str, inputs: dict[str, Any]) -> StepResult:
        command = inputs.get("command")
        if not isinstance(command, list) or not command:
            return StepResult(
                step_id=step_id,
                status=StepStatus.failed,
                stdout="",
                stderr="invalid command format",
                artifact_paths=[],
                metadata={"worker": "shell"},
            )

        root = command[0]
        if root not in self.allowlist:
            return StepResult(
                step_id=step_id,
                status=StepStatus.failed,
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
            stdout=completed.stdout,
            stderr=completed.stderr,
            artifact_paths=[],
            metadata={"worker": "shell", "returncode": completed.returncode},
        )
