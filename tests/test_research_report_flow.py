from pathlib import Path

from diviora.config import Config
from diviora.graph import run_task
from diviora.schemas import TaskRequest


def test_research_report_flow(tmp_path: Path) -> None:
    cfg = Config(runs_dir=tmp_path / "runs", allowed_shell_roots=("echo", "python"), openai_model="stub")
    task = TaskRequest(
        task_id="research-1",
        task_type="research_report",
        goal="compare options",
        constraints=[],
        allowed_tools=["llm"],
        approval_mode="auto",
        context_notes=["note"],
    )
    outcome = run_task(task, config=cfg)
    assert outcome.status == "PASS"
    run_dirs = list((tmp_path / "runs").iterdir())
    run_dir = run_dirs[0]
    report = run_dir / "artifacts" / "report.md"
    assert report.exists()
    assert (run_dir / "run_summary.json").exists()
    content = report.read_text(encoding="utf-8")
    assert "# Objective" in content
    assert "# Recommendation" in content
