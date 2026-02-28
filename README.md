# Diviora Orchestrator v0

Diviora Orchestrator v0 is a minimal deterministic orchestration kernel.

It accepts a task request, creates a bounded plan, validates policy, executes approved steps with controlled workers, verifies deterministic checks, and emits an auditable PASS/FAIL outcome with evidence.

## Core principles

- Agents propose; code executes.
- Fail closed by default.
- Side effects require explicit approval.
- Every meaningful action is logged.
- Every run writes artifacts to a run folder.
- Verification gates are mandatory.
- No hidden autonomous loops.

## Architecture overview

Main orchestration flow (LangGraph):

1. `intake`
2. `plan`
3. `validate_plan`
4. `approval_gate`
5. `execute_steps`
6. `verify`
7. `finalize`

Each run creates:

`runs/<timestamp>_<task_slug>/`

- `task_request.json`
- `plan.json`
- `approvals.jsonl`
- `ledger.jsonl`
- `verification.json`
- `outcome.json`
- `run_summary.json` (quick human summary)
- `artifacts/`

## Repo structure

```
README.md
AGENTS.md
pyproject.toml
.env.example
examples/
src/diviora/
  cli.py
  config.py
  graph.py
  state.py
  schemas.py
  ledger.py
  artifacts.py
  approvals.py
  planning/
  validation/
  workers/
  tasks/
tests/
```

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .[dev]
```

## CLI quickstart

Check commands:

```bash
python -m diviora.cli --help
```

Run with a task file:

```bash
python -m diviora.cli run --task-file examples/research_task.json
python -m diviora.cli run --task-file examples/code_task.json
```

Run a built-in demo path:

```bash
python -m diviora.cli demo --task-type research
python -m diviora.cli demo --task-type code
```

Use `--json` if you only want `outcome.json`-style output from `run` or `demo`.

## Run inspection

After each run, inspect:

1. `run_summary.json` for quick status, artifacts, approvals, and key file paths.
2. `outcome.json` for final PASS/FAIL.
3. `verification.json` for deterministic checks.
4. `ledger.jsonl` and `approvals.jsonl` for audit trail.

## Approvals

- `approval_mode=auto`: required approvals are auto-granted and logged.
- `approval_mode=manual`: each approval-required step pauses for CLI confirmation.
- Shell steps are side-effectful by default and require approval.

## Task types

### `research_report`

- Tooling: `llm`
- Output artifact: `artifacts/report.md`
- Verification: artifact exists and required sections exist:
  - Objective
  - Options
  - Risks
  - Recommendation
  - Next Steps

### `code_task`

- Tooling: `shell` + `llm`
- Output artifact: `artifacts/execution_report.md`
- Verification: report exists and command/test steps succeeded

## Dependency runtime mode

The runtime now prefers real `pydantic` and real `langgraph` dependencies.

- If both imports succeed, Diviora runs with real dependencies.
- If either import is unavailable, Diviora falls back to internal compatibility shims under `diviora.compat` (these shims are no longer import-shadowing top-level packages).

To inspect active dependency mode:

```bash
python -c "from diviora.runtime_deps import runtime_dependency_state; print(runtime_dependency_state())"
```

## CI

GitHub Actions runs `pytest` on every `push` and `pull_request` using Python 3.11 via `.github/workflows/ci.yml`.

## Test

```bash
pytest
```

## Agent guidance

See `AGENTS.md` for persistent coding-agent boundaries and safe-change workflow for this repository.

## Intentionally out of scope

- UI and browser automation
- Distributed orchestration
- Agent swarms
- Generalized long-term memory
- Databases and scheduling systems
- Autonomous retries/loops
