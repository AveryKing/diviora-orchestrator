# V0 Usage Validation

## Objective

Execute a single real end-to-end usage pass of Diviora Orchestrator v0 for both supported task types (`research_report` and `code_task`) and determine whether the current kernel is practically usable for limited internal operation.

## Repository State Observed

- Repository entrypoint is `python -m diviora.cli` with `run`, `replay`, and `approve` commands.
- Runtime dependency mode reports real dependencies active (`pydantic` and `langgraph`).
- Example task contracts in `examples/` match the two supported task types and flow into a run folder under `runs/<timestamp>_<task_id_slug>/`.
- Initial environment needed Python 3.11 interpreter path (`~/.pyenv/versions/3.11.14/bin/python`) due project `requires-python >=3.11`.

## Usage Validation Plan

1. Inspect CLI usage, task schemas/examples, planner behavior, approvals, and verification logic to determine minimum real commands.
2. Execute one real `research_report` task with the required practical goal.
3. Execute one real `code_task` that runs `pytest -q` through the shell worker and manual approval flow.
4. Inspect each run directory for expected artifacts (`task_request`, `plan`, approvals, ledger, verification, outcome, artifacts output files).
5. Evaluate usability, readability, and operator friction.
6. Record findings in this file only.

## Research Report Task Run

- Task input file: `/tmp/research_usage_task.json`
- Goal used (exact required goal):
  - "Produce a decision memo comparing three options for introducing an API layer in a legacy PHP + SQL Server system that currently relies on stored procedures."
- Invocation path: real CLI (`python -m diviora.cli run ...`) -> graph flow (`intake` -> `plan` -> `validate_plan` -> `approval_gate` -> `execute_steps` -> `verify` -> `finalize`).
- Run produced:
  - `run_id`: `20260228142837_research_usage_validation_001`
  - `status`: `PASS`
  - artifact path: `runs/20260228142837_research_usage_validation_001/artifacts/report.md`

Observed quality:
- Required report sections were present (`# Objective`, `# Options`, `# Risks`, `# Recommendation`, `# Next Steps`).
- Content was structurally valid but shallow/generic (options were placeholders rather than three concrete options).
- Artifact pathing worked exactly as expected.

## Code Task Run

- Task input file: `/tmp/code_usage_task.json`
- Task objective: run existing pytest suite through shell worker.
- Approval mode: `manual` to exercise human approval path.
- Shell allowlist set for this invocation only: `DIVIORA_ALLOWED_SHELL='echo,python,pytest'`.
- Approval interaction: step prompt appeared and was approved via stdin (`y`).
- Invocation path: real CLI (`python -m diviora.cli run ...`) through same orchestration graph.
- Run produced:
  - `run_id`: `20260228142847_code_usage_validation_001`
  - `status`: `PASS`
  - artifact path: `runs/20260228142847_code_usage_validation_001/artifacts/execution_report.md`

Observed quality:
- Shell worker execution was bounded and understandable from plan/ledger.
- Approval behavior was correct: manual prompt for shell step, no approval requirement for report-writing LLM step.
- Verification passed, but execution report content was generic and did not summarize test output details.

## Artifacts Produced

Research run directory (`runs/20260228142837_research_usage_validation_001/`):
- `task_request.json`
- `plan.json`
- `approvals.jsonl`
- `ledger.jsonl`
- `verification.json`
- `outcome.json`
- `artifacts/report.md`

Code run directory (`runs/20260228142847_code_usage_validation_001/`):
- `task_request.json`
- `plan.json`
- `approvals.jsonl`
- `ledger.jsonl`
- `verification.json`
- `outcome.json`
- `artifacts/execution_report.md`

## Ledger and Approval Evidence

Research run evidence:
- Ledger includes `run_started`, `plan_created`, `plan_validated`, `approval_granted`, `step_started`, `step_completed`, `verification_completed`, `run_completed`.
- Approval evidence records `generate_report` as approved with reason `not required`.

Code run evidence:
- Ledger includes explicit timing around shell step and report step execution.
- Approval file records:
  - `run_command_1` approved with reason `user approved` (manual path exercised)
  - `write_execution_report` approved with reason `not required`

## Verification Results

Research run verification:
- `passed: true`
- checks confirm report existence and all required sections.
- failures list empty.

Code run verification:
- `passed: true`
- checks confirm execution report existence and that command/test steps succeeded.
- failures list empty.

Both runs ended with clear `PASS` outcomes and evidence paths.

## Usability Findings

What worked well:
- End-to-end execution path is straightforward and deterministic.
- Run folder structure is clean and predictable.
- Ledger and approval logs are easy to audit.
- Verification gate gives clear pass/fail signals.

What was awkward:
- Python interpreter/version mismatch can block first-run if operator uses default `python` not 3.11+.
- Code-task execution report lacks concrete shell-output context (readable but low informational value).
- Research report content quality is structurally compliant but too generic to be decision-ready without stronger generation logic.

## Small Fixes Made

- None. No code changes were required to complete this usage-validation pass.

## Remaining Friction

- Need explicit operator guidance for interpreter selection in environments with multiple Python versions.
- Need better capture/surfacing of shell step stdout/stderr in operator-facing artifacts.
- Need richer report synthesis for practical decision memo usage.

## Recommended V0.2 Improvements

1. Improve generated artifact quality:
   - Research outputs should explicitly satisfy requested cardinality/details (e.g., "three options" with pros/cons).
   - Code execution report should summarize command return codes and key stdout/stderr excerpts.
2. Improve operator ergonomics:
   - Add CLI preflight checks that clearly fail with actionable guidance when Python/runtime/tooling assumptions are unmet.
3. Improve evidence usability:
   - Persist command outputs as artifacts (or include in execution report) for easier debugging and audit traceability.
4. Improve verification depth (without architectural redesign):
   - Add optional checks for report semantic completeness beyond section headers.

## Final Verdict

**Classification: USAGE_VALIDATED**

Rationale:
- Both supported task types executed end-to-end through the real orchestrator path.
- Required artifacts, ledger records, approval evidence, and verification outputs were produced.
- System is meaningfully usable for limited internal operation now, though output quality and operator ergonomics are still clunky and should be improved in v0.2.

## Exact Commands Used

```bash
rg --files -g 'AGENTS.md'
find .. -name AGENTS.md -maxdepth 4
rg --files
sed -n '1,260p' README.md
python -m diviora.cli --help
python -m pip install -e .[dev]
~/.pyenv/versions/3.11.14/bin/python --version
~/.pyenv/versions/3.11.14/bin/python -m pip install -e .[dev]
~/.pyenv/versions/3.11.14/bin/python -m diviora.cli --help
cat examples/research_task.json
cat examples/code_task.json
~/.pyenv/versions/3.11.14/bin/python -m diviora.cli run --help
sed -n '1,260p' src/diviora/cli.py
sed -n '1,320p' src/diviora/tasks/research_report.py
sed -n '1,320p' src/diviora/tasks/code_task.py
sed -n '1,320p' src/diviora/graph.py
sed -n '1,320p' src/diviora/planning/planner.py
sed -n '1,260p' src/diviora/workers/llm_worker.py
sed -n '1,260p' src/diviora/workers/shell_worker.py
sed -n '1,260p' src/diviora/validation/validate_output.py
sed -n '1,260p' src/diviora/approvals.py
sed -n '1,260p' src/diviora/config.py
sed -n '1,320p' src/diviora/schemas.py
cat > /tmp/research_usage_task.json <<'JSON' ... JSON
~/.pyenv/versions/3.11.14/bin/python -m diviora.cli run /tmp/research_usage_task.json
find runs/20260228142837_research_usage_validation_001 -maxdepth 2 -type f | sort
sed -n '1,200p' runs/20260228142837_research_usage_validation_001/artifacts/report.md
cat runs/20260228142837_research_usage_validation_001/verification.json
cat runs/20260228142837_research_usage_validation_001/ledger.jsonl
cat runs/20260228142837_research_usage_validation_001/approvals.jsonl
cat > /tmp/code_usage_task.json <<'JSON' ... JSON
printf 'y\n' | DIVIORA_ALLOWED_SHELL='echo,python,pytest' ~/.pyenv/versions/3.11.14/bin/python -m diviora.cli run /tmp/code_usage_task.json
find runs/20260228142847_code_usage_validation_001 -maxdepth 2 -type f | sort
sed -n '1,200p' runs/20260228142847_code_usage_validation_001/artifacts/execution_report.md
cat runs/20260228142847_code_usage_validation_001/verification.json
cat runs/20260228142847_code_usage_validation_001/ledger.jsonl
cat runs/20260228142847_code_usage_validation_001/approvals.jsonl
cat runs/20260228142847_code_usage_validation_001/outcome.json
~/.pyenv/versions/3.11.14/bin/python -c "from diviora.runtime_deps import runtime_dependency_state; print(runtime_dependency_state())"
git status --short
git branch --show-current
```

## Files Modified

- `V0_USAGE_VALIDATION.md`
