# V0 Runtime and CI Validation

## Objective

Execute a single end-to-end runtime validation pass against real dependencies, fix compatibility issues discovered under real dependency mode, run the full test suite, add GitHub Actions CI for push/PR testing, and document the resulting trust boundary.

## Repository State Observed

- Project dependencies in `pyproject.toml` target `pydantic>=2.7` and `langgraph>=0.2.0` with `pytest` in `dev` extras.
- Runtime dependency selection was already centralized in `src/diviora/runtime_deps.py` with real-import preference and shim fallback behavior.
- Compatibility shim implementations remained present under `src/diviora/compat/`.
- Tests instantiate `TaskRequest` with string values for enum-backed fields (`task_type`, `approval_mode`).

## Real Dependency Validation Plan

1. Inspect dependency/trust-boundary files and tests.
2. Install project with dev dependencies from internet-accessible package index.
3. Verify import origins and runtime dependency mode (`real` vs `shim`).
4. Run full test suite under real dependencies.
5. Fix only compatibility breaks required for real-runtime correctness.
6. Add minimal CI workflow on push/pull_request.
7. Update README to reflect CI/runtime truth.

## Dependency Installation

- Initial install attempt with default interpreter failed because host default was Python 3.10 while project requires `>=3.11`.
- Re-ran installation using `PYENV_VERSION=3.11.14` and successfully installed editable package and real dependencies including real `pydantic` and real `langgraph`.

## Runtime Trust Boundary

- Runtime selection remains explicit in `src/diviora/runtime_deps.py`: real libraries are imported first; shims only on `ImportError`.
- Programmatic verification after successful install reported:
  - `runtime_dependency_state()['pydantic'] == 'real'`
  - `runtime_dependency_state()['langgraph'] == 'real'`
  - module origins for `pydantic` and `langgraph.graph` resolved to site-packages under Python 3.11.
- Compatibility shims still exist as explicit fallback-only code paths, but active runtime is now unambiguous in this environment.

## Changes Made

1. **Real-dependency compatibility fix for pydantic v2 strict enum handling**
   - Added `field_validator` import in `runtime_deps` real path, and a no-op fallback decorator in shim mode.
   - Added `TaskRequest` enum coercion validators (`mode="before"`) for `task_type` and `approval_mode` so string payloads used by tests/CLI remain accepted while preserving strict model behavior.
2. **CI workflow added**
   - Created `.github/workflows/ci.yml` running pytest on push and pull_request with Python 3.11.
3. **README update**
   - Added CI section documenting workflow behavior.
   - Normalized install command to `python -m pip install -e .[dev]`.
4. **Repository hygiene update**
   - Added a minimal `.gitignore` for Python cache/artifact noise generated during local/CI validation.

## Test Execution

- First full run under real dependencies failed (5 tests) due to strict enum instance validation with real pydantic.
- After targeted compatibility fix, full suite passed.

Final status: `9 passed`.

## CI Workflow Added

Added `.github/workflows/ci.yml` with:
1. `actions/checkout@v4`
2. `actions/setup-python@v5` (Python 3.11)
3. `python -m pip install --upgrade pip`
4. `python -m pip install -e .[dev]`
5. `pytest`

Workflow triggers on both `push` and `pull_request`.

## Results

**Classification: REAL_DEPENDENCIES_VALIDATED_AND_CI_ENABLED**

Criteria check:
- real pydantic active ✅
- real langgraph active ✅
- tests pass ✅
- CI workflow added ✅
- runtime trust boundary documented and non-ambiguous for normal runtime ✅

## Failures Encountered

1. `python -m pip install -e .[dev]` failed under default Python 3.10 (`requires-python >=3.11`).
2. Initial `pytest` run under real dependencies failed due to strict enum instance checks in `TaskRequest` with string inputs.

Both issues were remediated in this pass.

## Remaining Risks

- If runtime executes with Python <3.11, installation still fails by design (`requires-python >=3.11`).
- Shim code paths remain for environments lacking dependencies; while inactive in validated runtime, they still represent alternate behavior in degraded environments.

## Final Verdict

Repository now runs against real `pydantic` and real `langgraph`, passes full tests under supported Python, and includes an automated GitHub Actions CI workflow for push/PR validation.

## Exact Commands Used

```bash
pwd
rg --files -g 'AGENTS.md'
find .. -maxdepth 3 -name AGENTS.md
rg --files
sed -n '1,240p' pyproject.toml
sed -n '1,260p' README.md
sed -n '1,240p' src/diviora/runtime_deps.py
sed -n '1,260p' src/diviora/compat/pydantic_shim.py
sed -n '1,260p' src/diviora/compat/langgraph_shim.py
sed -n '1,260p' tests/test_schemas.py
sed -n '1,260p' tests/test_ledger.py
sed -n '1,260p' tests/test_plan_validation.py
sed -n '1,300p' tests/test_research_report_flow.py
sed -n '1,300p' tests/test_code_task_flow.py
sed -n '1,220p' tests/test_artifacts.py
sed -n '1,260p' src/diviora/compat/__init__.py
sed -n '1,260p' src/diviora/graph.py
sed -n '1,260p' src/diviora/workers/llm_worker.py
git status --short
python -m pip install -e .[dev]
python --version
python3 --version
command -v python3.11 && python3.11 --version || true
PYENV_VERSION=3.11.14 python --version
PYENV_VERSION=3.11.14 python -m pip install -e .[dev]
PYENV_VERSION=3.11.14 python - <<'PY'
import importlib
from diviora.runtime_deps import runtime_dependency_state
mods=['pydantic','langgraph','diviora.compat.pydantic_shim','diviora.compat.langgraph_shim']
print(runtime_dependency_state())
for m in mods:
    mod=importlib.import_module(m)
    print(m, getattr(mod,'__file__',None))
PY
PYENV_VERSION=3.11.14 python - <<'PY'
import importlib
for m in ['langgraph.graph','langgraph.graph.state','pydantic','pydantic.main']:
    mod=importlib.import_module(m)
    print(m, mod.__file__)
PY
PYENV_VERSION=3.11.14 pytest
PYENV_VERSION=3.11.14 pytest
```

## Files Modified

- `src/diviora/runtime_deps.py`
- `src/diviora/schemas.py`
- `.github/workflows/ci.yml`
- `README.md`
- `.gitignore`
- `V0_RUNTIME_AND_CI_VALIDATION.md`
