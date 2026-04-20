"""Regression test: red-transcript-fixture.jsonl is valid JSONL.

Guards against pretty-printed multi-line JSON regressions (Copilot comment on
PR #22). JSONL requires exactly one JSON object per line so line-by-line
parsers (including Claude Code session readers) can consume it.
"""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURE_PATH = PROJECT_ROOT / "tests" / "pressure" / "red-transcript-fixture.jsonl"


def test_fixture_exists() -> None:
    assert FIXTURE_PATH.is_file(), f"Expected fixture at {FIXTURE_PATH}"


def test_every_line_parses_as_json() -> None:
    with FIXTURE_PATH.open(encoding="utf-8") as fh:
        lines = [line for line in fh if line.strip()]
    assert lines, "Fixture must contain at least one record"
    for i, line in enumerate(lines, 1):
        try:
            json.loads(line)
        except json.JSONDecodeError as exc:
            raise AssertionError(
                f"Line {i} is not valid JSON: {exc.msg} — {line.rstrip()[:80]!r}"
            ) from exc


def test_expected_record_count() -> None:
    """The RED scenario doc references 4 records; guard against drift."""
    with FIXTURE_PATH.open(encoding="utf-8") as fh:
        records = [json.loads(line) for line in fh if line.strip()]
    assert len(records) == 4, f"Expected 4 records, got {len(records)}"


def test_records_have_expected_shape() -> None:
    """Each record must have the JSONL transcript-event keys we rely on."""
    required_keys = {"type", "message", "uuid", "timestamp", "sessionId"}
    with FIXTURE_PATH.open(encoding="utf-8") as fh:
        records = [json.loads(line) for line in fh if line.strip()]
    for i, record in enumerate(records, 1):
        missing = required_keys - record.keys()
        assert not missing, f"Record {i} missing keys: {missing}"
