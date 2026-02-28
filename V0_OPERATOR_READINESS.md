# V0 Operator Readiness

## Objective
Perform one usability and operator-readiness productization pass on the existing validated v0 kernel without changing architecture, task model, or runtime scope.

## Repository State Observed
- v0 already had two supported task types (`research_report`, `code_task`) and a deterministic graph runtime.
- CLI existed with `run`, `replay`, and `approve`, but `run` emitted raw JSON only and did not provide quick operator guidance.
- Run folders were complete for auditability but lacked a compact single-file summary for fast inspection.
- README documented core concepts but did not provide one obvious demo command path for new operators.
- Validation artifacts were present (`V0_RUNTIME_AND_CI_VALIDATION.md`, `V0_USAGE_VALIDATION.md`) and indicated real dependency/runtime flow was already validated.

## Operator Readiness Plan
1. Add a practical top-level `AGENTS.md` for persistent coding-agent guardrails.
2. Improve CLI ergonomics with clearer command help and user-facing run completion output.
3. Add one explicit demo invocation path via CLI for both existing task types.
4. Add a compact run summary artifact in each run folder.
5. Update README to reflect the operator-focused flow and inspection order.
6. Keep all changes small and architecture-preserving.

## AGENTS.md Added
Added a top-level `AGENTS.md` with concise, actionable guidance for future coding agents:
- repository purpose and v0 boundaries
- architecture boundaries (including fixed graph flow)
- trusted runtime assumptions
- testing expectations
- non-negotiable rules and review checklist
- safe-change workflow for minimal, auditable edits

## CLI and Demo Improvements
Implemented focused CLI usability improvements in `src/diviora/cli.py`:
- Added command-level help descriptions for all commands.
- Improved `run` output to print:
  - clear PASS/FAIL line
  - run ID
  - run folder path
  - outcome path
  - summary path
  - artifact paths
- Added `--json` option to `run` for prior machine-friendly output mode.
- Added `demo` command with `--task-type research|code` to provide an obvious end-to-end invocation path using existing `examples/` inputs.
- Added missing-task-file validation for clearer operator error messages.

## Run Output Improvements
Implemented a compact human-inspection artifact:
- Added `run_summary.json` to every run folder in `src/diviora/graph.py`.
- Summary includes:
  - run identity/status/reason
  - key evidence file paths
  - artifact paths
  - approval counts
  - verification payload
  - per-step status snapshot

This preserves the append-only ledger model while reducing inspection friction.

## End-to-End Demo Path
One clear command path now exists directly in CLI and README:
- Research demo: `python -m diviora.cli demo --task-type research`
- Code demo: `python -m diviora.cli demo --task-type code`

These commands use existing example tasks and produce fully inspectable run folders with `run_summary.json` + existing evidence files.

## Usability Gains
- New operators can discover and execute a demo from `--help` without opening source files.
- Operators immediately see where to inspect output after each run.
- Completed run inspection now starts with one compact summary instead of manual multi-file traversal.
- Agent contributors now have persistent, explicit guardrails in-repo via `AGENTS.md`.

## Small Fixes Made
- Added explicit task-file existence check in CLI `run` command to fail with a direct, actionable message.
- Added test assertions for `run_summary.json` generation in both task-type flow tests.

## Remaining Friction
- `run_summary.json` is JSON-only; some operators may still prefer a markdown summary variant for direct reading.
- `execution_report.md` content quality still depends on current LLM worker behavior and remains intentionally minimal at v0 scope.

## Recommended V0.3 Priorities
1. Add optional `run_summary.md` rendering alongside JSON for non-technical operator read-through.
2. Improve execution report richness with bounded command output excerpts while preserving determinism.
3. Add a tiny `inspect` CLI helper to print key fields from `run_summary.json` for a selected run.

## Final Verdict
**Classification: OPERATOR_READY**

Rationale:
- `AGENTS.md` exists and is practical.
- CLI/demo flow is materially clearer and easier to execute.
- Run outputs are easier to inspect through a compact summary artifact.
- Core architecture and validated kernel behavior were preserved.

## Exact Commands Used
```bash
pwd && rg --files -g 'AGENTS.md'
find .. -maxdepth 3 -name AGENTS.md
ls -la
sed -n '1,220p' README.md
sed -n '1,260p' src/diviora/cli.py
sed -n '1,320p' src/diviora/graph.py
ls -la examples && for f in examples/*.json; do echo '---' $f; sed -n '1,220p' $f; done
ls tests && sed -n '1,260p' tests/test_cli.py && sed -n '1,320p' tests/test_graph.py
sed -n '1,260p' tests/test_research_report_flow.py && sed -n '1,320p' tests/test_code_task_flow.py
sed -n '1,300p' src/diviora/tasks/research_report.py && sed -n '1,320p' src/diviora/tasks/code_task.py && sed -n '1,320p' src/diviora/planning/planner.py && sed -n '1,280p' src/diviora/validation/validate_output.py
~/.pyenv/versions/3.11.14/bin/python -m pip install -e .[dev]
~/.pyenv/versions/3.11.14/bin/python -m diviora.cli --help
~/.pyenv/versions/3.11.14/bin/python -m diviora.cli demo --task-type research
~/.pyenv/versions/3.11.14/bin/python -m diviora.cli demo --task-type code
cat runs/20260228183447_code_001/run_summary.json
~/.pyenv/versions/3.11.14/bin/python -m pytest
```

## Files Modified
- `AGENTS.md`
- `README.md`
- `src/diviora/cli.py`
- `src/diviora/graph.py`
- `tests/test_research_report_flow.py`
- `tests/test_code_task_flow.py`
- `V0_OPERATOR_READINESS.md`
