from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from diviora.schemas import StepResult, WorkerExecutionMode, WorkerRuntime


class Worker(ABC):
    worker_id: str
    worker_type: str
    worker_runtime: WorkerRuntime
    execution_mode: WorkerExecutionMode

    def describe(self) -> dict[str, str]:
        return {
            "worker_id": self.worker_id,
            "worker_type": self.worker_type,
            "worker_runtime": self.worker_runtime.value,
            "execution_mode": self.execution_mode.value,
        }

    @abstractmethod
    def execute(self, step_id: str, inputs: dict[str, Any], requires_approval: bool) -> StepResult:
        raise NotImplementedError
