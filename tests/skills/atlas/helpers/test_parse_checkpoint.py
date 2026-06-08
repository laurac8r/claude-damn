"""Unit tests for skills/_shared/parse_checkpoint.py."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from skills._shared.parse_checkpoint import CheckpointDoc, parse_checkpoint

SAMPLE = """# Checkpoint: foo

**Branch:** `feat/foo`

## Current State
Mid-foo.

## Next Steps
1. Do A
2. Do B

## Key Decisions Made
- X locked.
- Y locked.

## Open Questions / Blockers
- None.
"""


def test_parse_checkpoint_no_file_returns_none(tmp_path: Path) -> None:
    doc, warnings = parse_checkpoint(tmp_path)
    assert doc is None
    assert warnings == []


def test_parse_checkpoint_cwd_first(tmp_path: Path) -> None:
    (tmp_path / "CHECKPOINT.md").write_text(SAMPLE)
    doc, warnings = parse_checkpoint(tmp_path)
    assert isinstance(doc, CheckpointDoc)
    assert doc.branch == "feat/foo"
    assert doc.next_steps == ["1. Do A", "2. Do B"]
    assert doc.key_decisions == ["- X locked.", "- Y locked."]
    assert doc.blockers == ["- None."]
    assert "Mid-foo." in doc.current_state
    assert doc.raw == SAMPLE
    assert warnings == []


def test_parse_checkpoint_unparseable_returns_raw_with_warning(tmp_path: Path) -> None:
    (tmp_path / "CHECKPOINT.md").write_text("not a checkpoint document\n")
    doc, warnings = parse_checkpoint(tmp_path)
    assert isinstance(doc, CheckpointDoc)
    assert doc.branch == ""
    assert doc.next_steps == []
    assert doc.raw == "not a checkpoint document\n"
    assert any("parse" in w.lower() for w in warnings)


def test_checkpoint_doc_is_frozen() -> None:
    doc = CheckpointDoc(branch="x", current_state="")
    with pytest.raises(FrozenInstanceError):
        doc.branch = "y"  # type: ignore[misc]
