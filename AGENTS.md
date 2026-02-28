# Diviora Orchestrator Agent Guide

## Repository purpose
Diviora Orchestrator v0 is a deterministic orchestration kernel for two task types (`research_report`, `code_task`) with explicit approvals, append-only run evidence, and verification-gated PASS/FAIL outcomes.

## Core principles
- Agents can propose plans, but only bounded code paths execute.
- Fail closed by default.
- Side effects require explicit approval.
- Every meaningful event must remain auditable.
- Verification gates determine final outcome.

## What v0 is and is not
v0 is a minimal internal operator kernel for repeatable demos and controlled execution.
v0 is not a workflow platform, scheduler, memory system, swarm framework, or UI product.

## Architecture boundaries
- Keep the graph flow intact: `intake -> plan -> validate_plan -> approval_gate -> execute_steps -> verify -> finalize`.
- Do not add new task types without explicit product direction.
- Do not replace append-only ledger/approval records.
- Prefer small additive usability improvements over structural redesign.

## Trusted runtime assumptions
- Python 3.11+
- Prefer real `pydantic` and `langgraph`; compatibility shims are fallback only.
- Shell execution remains bounded by allowlisted roots (`DIVIORA_ALLOWED_SHELL`).

## Testing expectations
- Run `pytest` before finishing.
- For CLI/operator changes, run at least one real CLI command against `examples/`.
- Validate that run folders contain expected evidence files.

## Do not violate rules
- No hidden autonomous loops.
- No silent side effects.
- No unlogged state mutations.
- No schema relaxations that reduce determinism or auditability.

## Review guidelines
When reviewing a change, confirm:
1. Determinism and approval boundaries are preserved.
2. Run evidence (`ledger.jsonl`, `approvals.jsonl`, `verification.json`, `outcome.json`) remains complete.
3. Operator ergonomics improved without broadening scope.

## How to make changes safely
1. Inspect current behavior first (`README.md`, `src/diviora/cli.py`, `src/diviora/graph.py`, `examples/`).
2. Prefer minimal edits in-place.
3. Keep outputs human-inspectable (clear paths, clear status, compact summaries).
4. Update docs for any operator-facing behavior change.
5. Re-run tests and include exact commands in validation/report artifacts.
