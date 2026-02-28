from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Callable

from diviora.runtime_deps import END, StateGraph

from diviora.approvals import ApprovalFn, decide_approval
from diviora.artifacts import ArtifactManager
from diviora.config import Config, load_config
from diviora.ledger import Ledger
from diviora.planning.planner import build_plan
from diviora.schemas import RunOutcome, StepResult, StepStatus, TaskRequest
from diviora.state import RunState
from diviora.validation.validate_output import command_steps_passed, verify_outputs
from diviora.validation.validate_plan import validate_plan
from diviora.validation.validate_step import validate_step
from diviora.workers.llm_worker import LLMWorker
from diviora.workers.shell_worker import ShellWorker
from diviora.workers.external_terminal_worker import ExternalTerminalWorker


def _slug(value: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in value.lower()).strip("_")


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_run_summary(run_dir: Path, task: TaskRequest, state: RunState, outcome: RunOutcome) -> None:
    verification = state.get("verification")
    step_results = state.get("step_results", [])
    approvals = state.get("approvals", [])
    step_statuses = [
        {
            "step_id": result.step_id,
            "status": result.status.value,
            "worker_id": result.worker_id,
            "worker_type": result.worker_type,
            "worker_runtime": result.worker_runtime.value,
            "execution_mode": result.execution_mode.value,
            "requires_approval": result.requires_approval,
            "stderr": result.stderr,
            "artifact_paths": result.artifact_paths,
        }
        for result in step_results
    ]

    summary = {
        "run_id": outcome.run_id,
        "task_id": outcome.task_id,
        "task_type": task.task_type.value,
        "status": outcome.status,
        "reason": outcome.reason,
        "run_dir": str(run_dir),
        "key_files": {
            "task_request": str(run_dir / "task_request.json"),
            "plan": str(run_dir / "plan.json"),
            "approvals": str(run_dir / "approvals.jsonl"),
            "ledger": str(run_dir / "ledger.jsonl"),
            "verification": str(run_dir / "verification.json"),
            "outcome": str(run_dir / "outcome.json"),
        },
        "artifact_paths": outcome.artifact_paths,
        "approval_counts": {
            "total": len(approvals),
            "approved": sum(1 for decision in approvals if decision.get("approved")),
            "denied": sum(1 for decision in approvals if not decision.get("approved")),
        },
        "verification": verification.model_dump() if verification else None,
        "step_statuses": step_statuses,
    }
    _write_json(run_dir / "run_summary.json", summary)


def run_task(task: TaskRequest, config: Config | None = None, approval_fn: ApprovalFn | None = None) -> RunOutcome:
    cfg = config or load_config()
    run_id = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{_slug(task.task_id)}"
    run_dir = cfg.runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    ledger = Ledger(run_dir / "ledger.jsonl")
    artifact_mgr = ArtifactManager(run_dir)
    llm = LLMWorker()
    shell = ShellWorker(cfg.allowed_shell_roots)
    external_terminal = ExternalTerminalWorker(run_dir / "artifacts")

    _write_json(run_dir / "task_request.json", task.model_dump())
    ledger.append("run_started", {"run_id": run_id, "task_id": task.task_id})

    def intake(state: RunState) -> RunState:
        return {**state, "run_id": run_id, "run_dir": str(run_dir), "task_request": task, "step_results": [], "approvals": []}

    def plan(state: RunState) -> RunState:
        p = build_plan(task)
        _write_json(run_dir / "plan.json", p.model_dump())
        ledger.append("plan_created", {"plan_id": p.plan_id})
        return {**state, "plan": p}

    def validate_plan_node(state: RunState) -> RunState:
        ok, errors = validate_plan(state["plan"], task)
        ledger.append("plan_validated", {"valid": ok, "errors": errors})
        if not ok:
            return {**state, "error": "; ".join(errors), "plan_valid": False}
        return {**state, "plan_valid": True}

    def approval_gate(state: RunState) -> RunState:
        if not state.get("plan_valid", False):
            return state
        approvals = list(state.get("approvals", []))
        approvals_path = run_dir / "approvals.jsonl"
        for step in state["plan"].steps:
            decision = decide_approval(task.approval_mode, step, approvals_path, approval_fn=approval_fn)
            approvals.append(decision.model_dump())
            ledger.append("approval_granted" if decision.approved else "approval_denied", decision.model_dump())
            if not decision.approved:
                return {**state, "approvals": approvals, "error": f"approval denied for {step.step_id}"}
        return {**state, "approvals": approvals}

    def execute_steps(state: RunState) -> RunState:
        if state.get("error"):
            return state
        results: list[StepResult] = []
        for step in state["plan"].steps:
            valid, reason = validate_step(step, task)
            if not valid:
                res = StepResult(step_id=step.step_id, status=StepStatus.failed, stdout="", stderr=reason, metadata={}, artifact_paths=[], step_inputs=step.inputs, requires_approval=step.requires_approval)
                results.append(res)
                ledger.append("step_failed", {"step_id": step.step_id, "reason": reason})
                return {**state, "step_results": results, "error": reason}

            ledger.append("step_started", {"step_id": step.step_id, "tool": step.tool})
            if step.tool == "llm":
                res = llm.execute(step.step_id, step.inputs, requires_approval=step.requires_approval)
                artifact_name = step.inputs.get("artifact_name")
                if artifact_name:
                    path = artifact_mgr.write_text(str(artifact_name), res.stdout)
                    res.artifact_paths.append(path)
            elif step.tool == "shell":
                res = shell.execute(step.step_id, step.inputs, requires_approval=step.requires_approval)
            elif step.tool == "external_terminal":
                res = external_terminal.execute(step.step_id, step.inputs, requires_approval=step.requires_approval)
            else:
                res = StepResult(
                    step_id=step.step_id,
                    status=StepStatus.failed,
                    stdout="",
                    stderr=f"unsupported tool {step.tool}",
                    step_inputs=step.inputs,
                    requires_approval=step.requires_approval,
                    artifact_paths=[],
                    metadata={},
                )

            results.append(res)
            event = "step_completed" if res.status == StepStatus.success else "step_failed"
            ledger.append(event, {"step_id": step.step_id, "status": res.status.value, "stderr": res.stderr, "worker_id": res.worker_id, "worker_type": res.worker_type, "worker_runtime": res.worker_runtime.value, "execution_mode": res.execution_mode.value})
            if res.status != StepStatus.success:
                return {**state, "step_results": results, "error": f"step failed {step.step_id}"}

        return {**state, "step_results": results}

    def verify(state: RunState) -> RunState:
        passed_commands = command_steps_passed(state.get("step_results", []))
        vr = verify_outputs(task, run_dir, passed_commands)
        _write_json(run_dir / "verification.json", vr.model_dump())
        ledger.append("verification_completed", {"passed": vr.passed, "failures": vr.failures})
        return {**state, "verification": vr}

    def finalize(state: RunState) -> RunState:
        verification = state.get("verification")
        passed = bool(verification and verification.passed and not state.get("error"))
        outcome = RunOutcome(
            run_id=run_id,
            task_id=task.task_id,
            status="PASS" if passed else "FAIL",
            reason="ok" if passed else (state.get("error") or "verification failed"),
            artifact_paths=verification.evidence_paths if verification else [],
        )
        _write_json(run_dir / "outcome.json", outcome.model_dump())
        _write_run_summary(run_dir, task, state, outcome)
        ledger.append("run_completed", outcome.model_dump())
        return {**state, "outcome": outcome}

    graph = StateGraph(RunState)
    graph.add_node("intake", intake)
    graph.add_node("plan", plan)
    graph.add_node("validate_plan", validate_plan_node)
    graph.add_node("approval_gate", approval_gate)
    graph.add_node("execute_steps", execute_steps)
    graph.add_node("verify", verify)
    graph.add_node("finalize", finalize)

    graph.set_entry_point("intake")
    graph.add_edge("intake", "plan")
    graph.add_edge("plan", "validate_plan")
    graph.add_edge("validate_plan", "approval_gate")
    graph.add_edge("approval_gate", "execute_steps")
    graph.add_edge("execute_steps", "verify")
    graph.add_edge("verify", "finalize")
    graph.add_edge("finalize", END)

    app = graph.compile()
    final_state = app.invoke({})
    return final_state["outcome"]
