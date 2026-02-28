from __future__ import annotations

import json
from pathlib import Path

import typer

from diviora.config import load_config
from diviora.graph import run_task
from diviora.schemas import TaskRequest

app = typer.Typer(help="Diviora Orchestrator v0 CLI")


@app.command(help="Execute a task request JSON and print a concise run summary.")
def run(task_file: Path, json_output: bool = typer.Option(False, "--json", help="Print only outcome JSON.")) -> None:
    if not task_file.exists():
        raise typer.BadParameter(f"Task file not found: {task_file}")

    payload = json.loads(task_file.read_text(encoding="utf-8"))
    task = TaskRequest.model_validate(payload)
    outcome = run_task(task)

    run_dir = load_config().runs_dir / outcome.run_id
    summary_path = run_dir / "run_summary.json"

    if json_output:
        typer.echo(json.dumps(outcome.model_dump(), indent=2))
        return

    typer.echo(f"Run complete: {outcome.status} ({outcome.reason})")
    typer.echo(f"Run ID: {outcome.run_id}")
    typer.echo(f"Run folder: {run_dir}")
    typer.echo(f"Outcome: {run_dir / 'outcome.json'}")
    typer.echo(f"Summary: {summary_path}")
    if outcome.artifact_paths:
        typer.echo("Artifacts:")
        for path in outcome.artifact_paths:
            typer.echo(f"- {path}")


@app.command(help="Run a built-in demo task from examples/.")
def demo(
    task_type: str = typer.Option("research", "--task-type", help="Demo type: research or code."),
    json_output: bool = typer.Option(False, "--json", help="Print only outcome JSON."),
) -> None:
    demo_map = {
        "research": Path("examples/research_task.json"),
        "code": Path("examples/code_task.json"),
    }
    if task_type not in demo_map:
        raise typer.BadParameter("--task-type must be 'research' or 'code'")
    run(demo_map[task_type], json_output=json_output)


@app.command(help="Print the outcome.json for a previous run directory.")
def replay(run_dir: Path) -> None:
    outcome_path = run_dir / "outcome.json"
    if not outcome_path.exists():
        raise typer.BadParameter("outcome.json not found")
    typer.echo(outcome_path.read_text(encoding="utf-8"))


@app.command(help="Print a structured approval decision payload.")
def approve(step_id: str, decision: bool, reason: str = "cli approval") -> None:
    typer.echo(json.dumps({"step_id": step_id, "approved": decision, "reason": reason}))


if __name__ == "__main__":
    app()
