import json

from diviora.ledger import Ledger


def test_ledger_append_only(tmp_path) -> None:
    path = tmp_path / "ledger.jsonl"
    ledger = Ledger(path)
    ledger.append("run_started", {"a": 1})
    ledger.append("run_completed", {"b": 2})

    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    second = json.loads(lines[1])
    assert first["event"] == "run_started"
    assert second["event"] == "run_completed"
