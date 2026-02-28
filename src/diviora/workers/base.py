from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from diviora.schemas import StepResult


class Worker(ABC):
    @abstractmethod
    def execute(self, step_id: str, inputs: dict[str, Any]) -> StepResult:
        raise NotImplementedError
