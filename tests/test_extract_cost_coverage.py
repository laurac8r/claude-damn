"""Additional coverage tests for extract_cost.py.

Covers model_key(), calc_cost(), parse_session(), _purge_session_entries(),
and write_log_entry(). Fast-mode pricing tests live in test_extract_cost.py;
this file does NOT duplicate those.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import src.extract_cost as extract_cost
from src.extract_cost import (
    DEFAULT_PRICING,
    _purge_session_entries,
    calc_cost,
    model_key,
    parse_session,
    write_log_entry,
)

# ---------------------------------------------------------------------------
# Triples 1-3: model_key() — parametrized
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "model_name, expected",
    [
        ("claude-opus-4-6", "claude-opus-4-6"),
        ("", ""),
        ("gpt-4o", "gpt-4o"),
    ],
    ids=["exact-match-opus", "empty-string", "unknown-model-unchanged"],
)
def test_model_key_returns_expected(model_name: str, expected: str) -> None:
    """model_key() should return exact match, empty, or pass-through unchanged."""
    assert model_key(model_name) == expected


# ---------------------------------------------------------------------------
# Triple 4: calc_cost() — opus 1M input tokens = $15.00
# ---------------------------------------------------------------------------


def test_calc_cost_opus_1m_input_tokens() -> None:
    """calc_cost for opus with 1M input tokens should return 15.00 USD."""
    usage = {"input_tokens": 1_000_000, "output_tokens": 0}
    cost = calc_cost("claude-opus-4-6", usage)
    assert cost == pytest.approx(15.00)


# ---------------------------------------------------------------------------
# Triple 5: calc_cost() — unknown model falls back to Sonnet pricing
# ---------------------------------------------------------------------------


def test_calc_cost_unknown_model_falls_back_to_sonnet() -> None:
    """calc_cost for unknown model should fall back to Sonnet pricing ($3.00/Mtok)."""
    usage = {"input_tokens": 1_000_000, "output_tokens": 0}
    cost = calc_cost("unknown-model", usage)
    expected = DEFAULT_PRICING["input"]  # 3.00
    assert cost == pytest.approx(expected)


# ---------------------------------------------------------------------------
# Triple 6: parse_session() — 2-turn JSONL with opus + sonnet
# ---------------------------------------------------------------------------


@pytest.fixture()
def two_turn_session_file(tmp_path: Path) -> Path:
    """Write a two-turn JSONL session file (one opus, one sonnet turn)."""
    session_file = tmp_path / "session.jsonl"
    lines = [
        json.dumps(
            {
                "type": "assistant",
                "timestamp": "2026-04-12T10:00:00Z",
                "message": {
                    "model": "claude-opus-4-6",
                    "usage": {
                        "input_tokens": 1000,
                        "output_tokens": 500,
                        "cache_read_input_tokens": 0,
                        "cache_creation_input_tokens": 0,
                    },
                },
            }
        ),
        json.dumps(
            {
                "type": "assistant",
                "timestamp": "2026-04-12T10:01:00Z",
                "message": {
                    "model": "claude-sonnet-4-6",
                    "usage": {
                        "input_tokens": 2000,
                        "output_tokens": 1000,
                        "cache_read_input_tokens": 0,
                        "cache_creation_input_tokens": 0,
                    },
                },
            }
        ),
    ]
    session_file.write_text("\n".join(lines) + "\n")
    return session_file


def test_parse_session_two_turns(two_turn_session_file: Path) -> None:
    """parse_session should return turns==2, per-model counts, and non-zero cost."""
    result = parse_session(two_turn_session_file)

    assert result["turns"] == 2
    assert result["total_cost_usd"] > 0.0

    models = result["models"]
    assert "claude-opus-4-6" in models
    assert "claude-sonnet-4-6" in models

    assert models["claude-opus-4-6"]["input_tokens"] == 1000
    assert models["claude-opus-4-6"]["output_tokens"] == 500
    assert models["claude-sonnet-4-6"]["input_tokens"] == 2000
    assert models["claude-sonnet-4-6"]["output_tokens"] == 1000


# ---------------------------------------------------------------------------
# Triple 7: _purge_session_entries() — only target session is removed
# ---------------------------------------------------------------------------


@pytest.fixture()
def cost_log_dir_with_two_sessions(tmp_path: Path) -> Path:
    """Cost log directory containing entries for two distinct sessions."""
    log_dir = tmp_path / "cost-log"
    log_dir.mkdir()
    log_file = log_dir / "2026-04-12_1000_mixed.jsonl"
    entries = [
        json.dumps({"session_id": "abc123", "turns": 3, "total_cost_usd": 0.05}),
        json.dumps({"session_id": "xyz789", "turns": 5, "total_cost_usd": 0.10}),
    ]
    log_file.write_text("\n".join(entries) + "\n")
    return log_dir


def test_purge_session_entries_removes_only_target(
    cost_log_dir_with_two_sessions: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_purge_session_entries should remove only 'abc123', leaving 'xyz789' intact."""
    monkeypatch.setattr(extract_cost, "COST_LOG_DIR", cost_log_dir_with_two_sessions)

    _purge_session_entries("abc123")

    remaining_lines: list[dict] = []
    for log_file in cost_log_dir_with_two_sessions.glob("*.jsonl"):
        for line in log_file.read_text().splitlines():
            if line.strip():
                remaining_lines.append(json.loads(line))

    session_ids = [entry["session_id"] for entry in remaining_lines]
    assert "abc123" not in session_ids
    assert "xyz789" in session_ids


# ---------------------------------------------------------------------------
# Triple 8: write_log_entry() — creates correctly named JSONL file
# ---------------------------------------------------------------------------


def test_write_log_entry_creates_named_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """write_log_entry should create a YYYY-MM-DD_HHmm_<session>.jsonl file."""
    log_dir = tmp_path / "cost-log"
    monkeypatch.setattr(extract_cost, "COST_LOG_DIR", log_dir)

    data = {
        "session_id": "deadbeef-1234-5678-abcd-000000000000",
        "turns": 4,
        "total_cost_usd": 0.12,
        "last_ts": "2026-04-12T14:30:00Z",
        "models": {},
        "first_ts": "2026-04-12T14:00:00Z",
        "project": "/tmp/myproject",
        "last_prompt": "",
    }

    fpath = write_log_entry(data)

    # File must exist
    assert fpath.exists()

    # Filename pattern: YYYY-MM-DD_HHmm_<first8chars>.jsonl
    fname = fpath.name
    pattern = r"^\d{4}-\d{2}-\d{2}_\d{4}_[a-zA-Z0-9\-]{1,8}\.jsonl$"
    assert re.match(pattern, fname), f"Unexpected filename: {fname!r}"

    # Content must be valid JSON containing session_id
    written = json.loads(fpath.read_text().strip())
    assert written["session_id"] == data["session_id"]
    assert written["total_cost_usd"] == pytest.approx(0.12)

    # File must be inside the monkeypatched log dir
    assert fpath.parent == log_dir


def test_write_log_entry_handles_malformed_timestamp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """write_log_entry should not crash when last_ts is unparseable."""
    log_dir = tmp_path / "cost-log"
    monkeypatch.setattr(extract_cost, "COST_LOG_DIR", log_dir)

    data = {
        "session_id": "badbadba",
        "turns": 1,
        "total_cost_usd": 0.01,
        "last_ts": "not-a-timestamp",
        "models": {},
        "first_ts": None,
        "project": "/tmp/x",
        "last_prompt": "",
    }

    fpath = write_log_entry(data)

    assert fpath.exists()
    written = json.loads(fpath.read_text().strip())
    assert written["session_id"] == "badbadba"
