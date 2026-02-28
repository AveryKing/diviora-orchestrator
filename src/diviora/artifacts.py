from __future__ import annotations

from pathlib import Path


class ArtifactManager:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.artifacts_dir = run_dir / "artifacts"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def write_text(self, relative_path: str, content: str) -> str:
        target = self.artifacts_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return str(target)
