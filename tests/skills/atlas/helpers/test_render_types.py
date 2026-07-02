"""Unit tests for the dataclasses in skills/atlas/render.py."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from skills._shared.anchor import Anchor, AnchorSource
from skills.atlas.render import AtlasInput, TaskRecord


def test_task_record_minimal_fields() -> None:
    t = TaskRecord(id="1", subject="X", status="pending", blocked_by=[])
    assert t.id == "1"
    assert t.status == "pending"


def test_task_record_status_typing() -> None:
    # Literal type hint is advisory at runtime; ensure constructor accepts each value.
    for s in ("pending", "in_progress", "completed"):
        TaskRecord(id="1", subject="X", status=s, blocked_by=[])  # type: ignore[arg-type]


def test_task_record_is_frozen() -> None:
    t = TaskRecord(id="1", subject="X", status="pending", blocked_by=[])
    with pytest.raises(FrozenInstanceError):
        t.subject = "Y"  # type: ignore[misc]


def test_atlas_input_default_warnings_empty() -> None:
    inp = AtlasInput(
        anchor=Anchor(slug="x", source=AnchorSource.BRANCH),
        shelf_entries=[],
        git_state=None,
        checkpoint=None,
        task_list=[],
        mode="single",
    )
    assert inp.warnings == []


def test_atlas_input_is_frozen() -> None:
    inp = AtlasInput(
        anchor=Anchor(slug="x", source=AnchorSource.BRANCH),
        shelf_entries=[],
        git_state=None,
        checkpoint=None,
        task_list=[],
        mode="single",
    )
    with pytest.raises(FrozenInstanceError):
        inp.mode = "all"  # type: ignore[misc]
