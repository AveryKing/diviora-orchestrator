from __future__ import annotations

from abc import ABC, abstractmethod

from diviora.schemas import TaskRequest


class TaskHandler(ABC):
    @abstractmethod
    def supports(self, task: TaskRequest) -> bool:
        raise NotImplementedError
