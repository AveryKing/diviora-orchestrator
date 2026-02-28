# V0 Worker Lane Readiness

## Objective

Harden Diviora's worker adapter boundary for safe future external execution lanes while preserving deterministic orchestration, strict schemas, approval-gated side effects, append-only audit evidence, and verification-based PASS/FAIL outcomes.

## Repository State Observed

- Worker execution existed through local `LLMWorker` and `ShellWorker` with a minimal base interface.
- `StepResult` captured status/logs/artifacts/metadata but did not explicitly standardize worker identity/runtime/execution semantics.
- Orchestration path and audit files were already deterministic and append-only.

## Worker-Lane Readiness Plan

1. Strengthen worker contract fields for identity, runtime, execution mode, and approval context.
2. Align all existing workers to the contract without changing graph semantics.
3. Add one external terminal scaffold worker that fails closed deterministically.
4. Ensure ledger/run summaries include richer worker execution evidence.
5. Validate existing flows plus scaffold behavior.

## Worker Contract Changes

- Extended `StepResult` with explicit worker-lane contract fields:
  - `worker_id`
  - `worker_type`
  - `worker_runtime` (`local|external`)
  - `execution_mode` (`synchronous|deferred|unsupported`)
  - `requires_approval`
  - `step_inputs`
- Added `StepStatus.not_implemented` for clear, auditable scaffold outcomes.
- Hardened `Worker` abstract base class to require these semantics through worker identity attributes and an execution signature that includes `requires_approval`.
- Updated `LLMWorker` and `ShellWorker` to emit complete contract-compliant `StepResult` payloads.

## External Lane Scaffold Added

Added `src/diviora/workers/external_terminal_worker.py` as the single new scaffold for a future Warp/Oz-style terminal lane.

Behavior:
- Reports as `worker_runtime=external` and `execution_mode=unsupported`.
- Writes a deterministic scaffold JSON artifact per invocation.
- Supports inspection-only mode (`inputs.mode == "inspect"`) as a non-side-effect success path.
- Fails closed for side-effectful execution:
  - `requires_approval=False` => `rejected` with explicit stderr.
  - `requires_approval=True` => `not_implemented` (no external execution performed).

## Safety and Approval Model

- Existing approval gate remains unchanged and authoritative.
- External lane scaffold enforces explicit side-effect posture even when called directly.
- No silent execution paths were added.
- Ledger records now include worker identity/runtime/execution mode on step completion/failure events.

## Demo or Validation Path

Validated:
- Full test suite.
- Real CLI runs for `research_report` and `code_task` example tasks.
- Presence of required evidence files in run directories.
- Direct scaffold invocation showing fail-closed rejection without approval and placeholder artifact creation.

## Small Fixes Made

- `run_summary.json` step entries now include worker identity/runtime/execution-mode context.
- README updated with concise worker-lane documentation and scaffold limitations.

## Remaining Gaps

- No live external terminal transport/protocol integration yet (intentional).
- No deferred polling/continuation protocol for external jobs yet.
- No plan generator path currently emits `external_terminal` tool steps (intentional for v0 safety).

## Recommended V0.4 Priorities

1. Define a bounded external task packet schema and signed handoff format.
2. Add deferred execution lifecycle support (`queued/running/completed`) with deterministic polling limits.
3. Add explicit approval scoping for external lanes (command class/environment/artifact boundaries).
4. Add end-to-end tests for an external-lane plan step once product direction approves.

## Final Verdict

**WORKER_LANE_READY**

The worker boundary is now explicit and stricter, exactly one safe external lane scaffold exists, and existing deterministic/approval/audit/verification behavior remains intact.

## Exact Commands Used

- `rg --files -g 'AGENTS.md'`
- `sed -n '1,220p' src/diviora/workers/base.py; sed -n '1,260p' src/diviora/workers/llm_worker.py; sed -n '1,280p' src/diviora/workers/shell_worker.py; sed -n '1,320p' src/diviora/graph.py; sed -n '1,260p' src/diviora/schemas.py; sed -n '1,260p' src/diviora/state.py; sed -n '1,260p' src/diviora/cli.py; sed -n '1,260p' README.md`
- `python - <<'PY' ...` (targeted file rewrites for worker contract updates)
- `cat > src/diviora/workers/external_terminal_worker.py <<'PY' ...`
- `cat > tests/test_worker_contract.py <<'PY' ...`
- `pytest`
- `PYTHONPATH=src python -m diviora.cli run examples/research_task.json`
- `PYTHONPATH=src python -m diviora.cli run examples/code_task.json`
- `for d in runs/20260228184545_research_001 runs/20260228184548_code_001; do ...; done`
- `PYTHONPATH=src python - <<'PY' ... ExternalTerminalWorker ...`

## Files Modified

- `src/diviora/schemas.py`
- `src/diviora/workers/base.py`
- `src/diviora/workers/llm_worker.py`
- `src/diviora/workers/shell_worker.py`
- `src/diviora/workers/external_terminal_worker.py`
- `src/diviora/graph.py`
- `tests/test_worker_contract.py`
- `README.md`
- `V0_WORKER_LANE_READINESS.md`
