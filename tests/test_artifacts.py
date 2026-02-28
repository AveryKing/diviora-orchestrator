from pathlib import Path

from diviora.artifacts import ArtifactManager


def test_artifact_write(tmp_path: Path) -> None:
    mgr = ArtifactManager(tmp_path)
    path = mgr.write_text("report.md", "hello")
    assert Path(path).exists()
    assert Path(path).read_text(encoding="utf-8") == "hello"
