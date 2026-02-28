from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    runs_dir: Path
    allowed_shell_roots: tuple[str, ...]
    openai_model: str


def load_config() -> Config:
    runs_dir = Path(os.getenv("DIVIORA_RUNS_DIR", "runs"))
    allowed_raw = os.getenv("DIVIORA_ALLOWED_SHELL", "echo,python")
    allowed = tuple(item.strip() for item in allowed_raw.split(",") if item.strip())
    model = os.getenv("DIVIORA_OPENAI_MODEL", "gpt-4o-mini")
    return Config(runs_dir=runs_dir, allowed_shell_roots=allowed, openai_model=model)
