from __future__ import annotations

from typing import Any, Callable

END = "__end__"


class _CompiledGraph:
    def __init__(self, entry: str, nodes: dict[str, Callable], edges: dict[str, str]) -> None:
        self.entry = entry
        self.nodes = nodes
        self.edges = edges

    def invoke(self, state: dict[str, Any]) -> dict[str, Any]:
        current = self.entry
        working = state
        while current != END:
            working = self.nodes[current](working)
            current = self.edges[current]
        return working


class StateGraph:
    def __init__(self, _state_type: Any) -> None:
        self._entry: str | None = None
        self._nodes: dict[str, Callable] = {}
        self._edges: dict[str, str] = {}

    def add_node(self, name: str, fn: Callable) -> None:
        self._nodes[name] = fn

    def set_entry_point(self, name: str) -> None:
        self._entry = name

    def add_edge(self, left: str, right: str) -> None:
        self._edges[left] = right

    def compile(self) -> _CompiledGraph:
        if self._entry is None:
            raise ValueError("entry point not set")
        return _CompiledGraph(self._entry, self._nodes, self._edges)
