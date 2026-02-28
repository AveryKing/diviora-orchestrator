from __future__ import annotations

import json
from pathlib import Path

import typer

from diviora.graph import run_task
from diviora.schemas import TaskRequest

app = typer.Typer(help="Diviora Orchestrator v0 CLI")


@app.command()
def run(task_file: Path) -> None:
    payload = json.loads(task_file.read_text(encoding="utf-8"))
    task = TaskRequest.model_validate(payload)
    outcome = run_task(task)
    typer.echo(json.dumps(outcome.model_dump(), indent=2))


@app.command()
def replay(run_dir: Path) -> None:
    outcome_path = run_dir / "outcome.json"
    if not outcome_path.exists():
        raise typer.BadParameter("outcome.json not found")
    typer.echo(outcome_path.read_text(encoding="utf-8"))


@app.command()
def approve(step_id: str, decision: bool, reason: str = "cli approval") -> None:
    typer.echo(json.dumps({"step_id": step_id, "approved": decision, "reason": reason}))


if __name__ == "__main__":
    app()
