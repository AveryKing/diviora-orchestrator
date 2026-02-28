from __future__ import annotations

from typing import Any

PYDANTIC_SOURCE = "real"
LANGGRAPH_SOURCE = "real"

try:
    from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
except ImportError:
    from diviora.compat.pydantic_shim import BaseModel, ConfigDict, Field, ValidationError

    PYDANTIC_SOURCE = "shim"

    def field_validator(*_args: Any, **_kwargs: Any):
        def _decorator(func: Any) -> Any:
            return func

        return _decorator

try:
    from langgraph.graph import END, StateGraph
except ImportError:
    from diviora.compat.langgraph_shim import END, StateGraph

    LANGGRAPH_SOURCE = "shim"


def runtime_dependency_state() -> dict[str, Any]:
    return {
        "pydantic": PYDANTIC_SOURCE,
        "langgraph": LANGGRAPH_SOURCE,
        "trusted_runtime": "REAL_DEPENDENCIES_ACTIVE"
        if PYDANTIC_SOURCE == "real" and LANGGRAPH_SOURCE == "real"
        else "SHIM_FALLBACK_ONLY",
    }
