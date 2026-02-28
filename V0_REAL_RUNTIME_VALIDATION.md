# V0 Real Runtime Validation

## Objective

Harden Diviora Orchestrator v0 from local-shim shadowed runtime behavior to an explicit trust boundary where real `pydantic`/`langgraph` are preferred, and fallback shim behavior is isolated and unambiguous.

## Current State Observed

- Before changes, local packages at `src/pydantic/` and `src/langgraph/` could satisfy imports used by runtime modules and tests, creating package-shadow ambiguity in environments that set `PYTHONPATH=src`.
- `pyproject.toml` already declared real dependencies (`pydantic`, `langgraph`), but the local shim packages made it unclear whether runtime was using real dependencies or local substitutes.
- README did not explicitly describe runtime dependency trust mode or fallback conditions.

## Real Dependency Validation Plan

1. Verify current import resolution and trust boundary.
2. Attempt real dependency installation using declared project path.
3. Remove import-shadowing package names from runtime path.
4. Preserve operability by relocating shims to non-shadowing namespace fallback.
5. Run full test suite in final configuration.
6. Document final trust classification and exact evidence.

## Changes Made

- Added `src/diviora/runtime_deps.py` to centralize dependency loading policy:
  - Prefer real `pydantic` and `langgraph` imports.
  - Fallback to internal shim modules only on `ImportError`.
  - Expose runtime status through `runtime_dependency_state()`.
- Added isolated shim modules:
  - `src/diviora/compat/pydantic_shim.py`
  - `src/diviora/compat/langgraph_shim.py`
  - `src/diviora/compat/__init__.py`
- Updated runtime imports:
  - `src/diviora/schemas.py` now imports pydantic interfaces from `diviora.runtime_deps`.
  - `src/diviora/graph.py` now imports langgraph interfaces from `diviora.runtime_deps`.
- Updated tests:
  - `tests/test_schemas.py` now imports `ValidationError` from `diviora.runtime_deps` to match active runtime backend.
- Removed top-level shadow packages:
  - deleted `src/pydantic/__init__.py`
  - deleted `src/langgraph/__init__.py`
  - deleted `src/langgraph/graph.py`
- Updated README to document runtime dependency mode and inspection command.

## Shim Handling Decision

Decision: **Quarantine shims under non-shadowing namespace and keep as explicit fallback only**.

- Chosen strategy: move shim logic to `diviora.compat.*` and remove top-level `pydantic`/`langgraph` shim packages.
- Result: normal import resolution no longer allows local shim packages to silently shadow real `pydantic`/`langgraph` package names.

## Test Execution

- Executed full suite with final code state:
  - `PYTHONPATH=src pytest`
- Result: **9 passed, 0 failed, 0 skipped**.

## Results

Final runtime classification: **PARTIAL_VALIDATION_OFFLINE_FALLBACK**.

Reason:
- Real dependency installation could not be completed due environment package index/proxy restrictions.
- Runtime trust boundary is now explicit and non-ambiguous.
- Repository remains runnable and tests pass under explicit shim fallback.

## Behavior Differences Found

- Before hardening: local shim packages were directly importable as `pydantic` and `langgraph`, which could silently shadow real packages in common local execution modes.
- After hardening: runtime imports are policy-driven via `diviora.runtime_deps`; shim usage is explicit fallback only from `diviora.compat`, not top-level package shadowing.

## Remaining Risks

- Full real-runtime validation remains incomplete until dependencies can be installed in this environment.
- Compatibility with latest upstream `langgraph` behavior is not validated in this run.
- Compatibility with upstream `pydantic` runtime validation semantics is not validated in this run.

## Final Verdict

**PARTIAL_VALIDATION_OFFLINE_FALLBACK**

The repository is now in a non-ambiguous trust state with shim fallback isolated from normal top-level import shadowing. Real dependency validation could not be completed due package installation restrictions, so this is not a full `REAL_DEPENDENCIES_VALIDATED` verdict.

## Exact Commands Used

```bash
rg --files
sed -n '1,220p' pyproject.toml
sed -n '1,260p' README.md
sed -n '1,260p' src/pydantic/__init__.py
sed -n '1,260p' src/langgraph/__init__.py
sed -n '1,260p' src/langgraph/graph.py
rg "from pydantic|import pydantic|from langgraph|import langgraph" -n src tests
python -c "import pydantic, langgraph, sys; print('pydantic', pydantic.__file__); print('langgraph', langgraph.__file__); print('sys.path0', sys.path[0])"
python -m pip install -e .[dev]
mkdir -p src/diviora/compat
# wrote: src/diviora/compat/pydantic_shim.py
# wrote: src/diviora/compat/langgraph_shim.py
# wrote: src/diviora/runtime_deps.py
# updated: src/diviora/schemas.py, src/diviora/graph.py, tests/test_schemas.py
python - <<'PY' ... (remove top-level shim files/directories) ...
python - <<'PY' ... (update README runtime mode section) ...
PYTHONPATH=src python -c "from diviora.runtime_deps import runtime_dependency_state; print(runtime_dependency_state())"
PYTHONPATH=src python - <<'PY' ... (import resolution/spec checks) ...
PYTHONPATH=src pytest
```

## Files Modified

- `README.md`
- `src/diviora/runtime_deps.py`
- `src/diviora/compat/__init__.py`
- `src/diviora/compat/pydantic_shim.py`
- `src/diviora/compat/langgraph_shim.py`
- `src/diviora/schemas.py`
- `src/diviora/graph.py`
- `tests/test_schemas.py`
- deleted `src/pydantic/__init__.py`
- deleted `src/langgraph/__init__.py`
- deleted `src/langgraph/graph.py`
