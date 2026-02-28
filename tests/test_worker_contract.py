from pathlib import Path

from diviora.workers.external_terminal_worker import ExternalTerminalWorker


def test_external_terminal_worker_fails_closed_without_approval(tmp_path: Path) -> None:
    worker = ExternalTerminalWorker(tmp_path)
    result = worker.execute("external_step", {"packet": "x"}, requires_approval=False)

    assert result.status.value == "rejected"
    assert "requires approval" in result.stderr
    assert result.worker_runtime.value == "external"
    assert result.execution_mode.value == "unsupported"
    assert len(result.artifact_paths) == 1
    assert Path(result.artifact_paths[0]).exists()


def test_external_terminal_worker_inspect_mode_is_non_side_effecting(tmp_path: Path) -> None:
    worker = ExternalTerminalWorker(tmp_path)
    result = worker.execute("external_inspect", {"mode": "inspect"}, requires_approval=False)

    assert result.status.value == "success"
    assert "inspection only" in result.stdout
    assert len(result.artifact_paths) == 1
