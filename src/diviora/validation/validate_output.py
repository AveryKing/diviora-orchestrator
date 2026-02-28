from __future__ import annotations

from pathlib import Path

from diviora.schemas import StepStatus, TaskRequest, VerificationResult


REQUIRED_SECTIONS = ["# Objective", "# Options", "# Risks", "# Recommendation", "# Next Steps"]


def verify_outputs(task: TaskRequest, run_dir: Path, step_results_ok: bool) -> VerificationResult:
    checks: list[str] = []
    failures: list[str] = []
    evidence: list[str] = []

    artifacts_dir = run_dir / "artifacts"
    if task.task_type.value == "research_report":
        report = artifacts_dir / "report.md"
        if not report.exists():
            failures.append("report.md missing")
        else:
            content = report.read_text(encoding="utf-8")
            evidence.append(str(report))
            checks.append("report.md exists")
            for section in REQUIRED_SECTIONS:
                if section not in content:
                    failures.append(f"missing section {section}")
                else:
                    checks.append(f"section present {section}")

    if task.task_type.value == "code_task":
        report = artifacts_dir / "execution_report.md"
        if not report.exists():
            failures.append("execution_report.md missing")
        else:
            checks.append("execution_report.md exists")
            evidence.append(str(report))
        if not step_results_ok:
            failures.append("one or more command/test steps failed")
        else:
            checks.append("command/test step succeeded")

    return VerificationResult(
        passed=len(failures) == 0,
        checks=checks,
        failures=failures,
        evidence_paths=evidence,
    )


def command_steps_passed(step_results: list) -> bool:
    relevant = [s for s in step_results if s.step_id.startswith("run_command_")]
    return all(s.status == StepStatus.success for s in relevant)
