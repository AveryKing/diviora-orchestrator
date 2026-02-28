from __future__ import annotations

from diviora.schemas import TaskRequest
from diviora.tasks.base import TaskHandler


class ResearchReportTask(TaskHandler):
    def supports(self, task: TaskRequest) -> bool:
        return task.task_type.value == "research_report"
