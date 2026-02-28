from pathlib import Path

from diviora.config import Config
from diviora.graph import run_task
from diviora.schemas import ApprovalDecision, TaskRequest


def test_code_task_flow_pass(tmp_path: Path) -> None:
    cfg = Config(runs_dir=tmp_path / "runs", allowed_shell_roots=("echo", "python"), openai_model="stub")
    task = TaskRequest(
        task_id="code-1",
        task_type="code_task",
        goal="run smoke",
        constraints=[],
        allowed_tools=["shell", "llm"],
        approval_mode="auto",
        commands=[["echo", "hello"]],
    )
    outcome = run_task(task, config=cfg)
    assert outcome.status == "PASS"
    run_dirs = list((tmp_path / "runs").iterdir())
    assert (run_dirs[0] / "run_summary.json").exists()


def test_manual_approval_denial_fails_run(tmp_path: Path) -> None:
    cfg = Config(runs_dir=tmp_path / "runs", allowed_shell_roots=("echo",), openai_model="stub")
    task = TaskRequest(
        task_id="code-2",
        task_type="code_task",
        goal="run denied",
        constraints=[],
        allowed_tools=["shell", "llm"],
        approval_mode="manual",
        commands=[["echo", "hello"]],
    )

    def deny(_step):
        return ApprovalDecision(step_id="run_command_1", approved=False, reason="no")

    outcome = run_task(task, config=cfg, approval_fn=deny)
    assert outcome.status == "FAIL"
    assert "approval denied" in outcome.reason


def test_shell_allowlist_rejection_fails_step(tmp_path: Path) -> None:
    cfg = Config(runs_dir=tmp_path / "runs", allowed_shell_roots=("echo",), openai_model="stub")
    task = TaskRequest(
        task_id="code-3",
        task_type="code_task",
        goal="run blocked command",
        constraints=[],
        allowed_tools=["shell", "llm"],
        approval_mode="auto",
        commands=[["python", "-V"]],
    )
    outcome = run_task(task, config=cfg)
    assert outcome.status == "FAIL"
