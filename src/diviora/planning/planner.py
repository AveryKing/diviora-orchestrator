from __future__ import annotations

from diviora.planning.prompts import CODE_TASK_PROMPT, RESEARCH_REPORT_PROMPT
from diviora.schemas import Plan, PlanStep, TaskRequest


def build_plan(task: TaskRequest) -> Plan:
    if task.task_type.value == "research_report":
        steps = [
            PlanStep(
                step_id="generate_report",
                title="Generate markdown report",
                description="Produce research report markdown",
                tool="llm",
                inputs={
                    "prompt": RESEARCH_REPORT_PROMPT,
                    "context": {"goal": task.goal, "task_type": task.task_type.value, "notes": task.context_notes},
                    "artifact_name": "report.md",
                },
                requires_approval=False,
                expected_outputs=["report.md"],
            )
        ]
        expected_artifacts = ["report.md"]
    else:
        commands = task.commands or [["echo", task.goal]]
        steps = []
        for i, cmd in enumerate(commands, start=1):
            steps.append(
                PlanStep(
                    step_id=f"run_command_{i}",
                    title=f"Run command {i}",
                    description="Execute approved shell command",
                    tool="shell",
                    inputs={"command": cmd},
                    requires_approval=True,
                    expected_outputs=["stdout", "stderr"],
                )
            )
        steps.append(
            PlanStep(
                step_id="write_execution_report",
                title="Write execution report",
                description="Create markdown summary of command results",
                tool="llm",
                inputs={
                    "prompt": CODE_TASK_PROMPT,
                    "context": {"goal": task.goal, "task_type": task.task_type.value},
                    "artifact_name": "execution_report.md",
                },
                requires_approval=False,
                expected_outputs=["execution_report.md"],
            )
        )
        expected_artifacts = ["execution_report.md"]

    return Plan(
        plan_id=f"plan_{task.task_id}",
        task_id=task.task_id,
        summary=f"Deterministic plan for {task.task_type.value}",
        steps=steps,
        expected_artifacts=expected_artifacts,
        success_criteria=["All steps succeed", "Verification passes"],
    )
