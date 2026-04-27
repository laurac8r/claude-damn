"""Unit tests for skills/_shared/anchor.py."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from skills._shared.anchor import Anchor, AnchorSource


def test_anchor_source_enum_has_four_rungs() -> None:
    assert len(AnchorSource) == 4
    assert AnchorSource.MODIFIED_FILE.value == "modified-file"
    assert AnchorSource.BRANCH.value == "branch"
    assert AnchorSource.MEMORY.value == "memory"
    assert AnchorSource.UNRESOLVED.value == "unresolved"


def test_anchor_dataclass_is_frozen() -> None:
    a = Anchor(slug="feat-x", source=AnchorSource.BRANCH)
    with pytest.raises(FrozenInstanceError):
        a.slug = "changed"  # type: ignore[misc]


def test_anchor_equality_by_value() -> None:
    a = Anchor(slug="x", source=AnchorSource.BRANCH)
    b = Anchor(slug="x", source=AnchorSource.BRANCH)
    assert a == b
