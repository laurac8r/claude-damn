"""Unit tests for skills/_shared/parse_shelf.py."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date
from pathlib import Path

import pytest

from skills._shared.parse_shelf import ShelfEntry, parse_shelf


def test_parse_shelf_happy_path(tmp_path: Path) -> None:
    p = tmp_path / "user-preferences.md"
    p.write_text(
        "# Shelf — user-preferences\n\n"
        "## 2026-04-27T04:49:51Z\n\n"
        "anchor: user-preferences\n"
        "signal: spec-doc skeleton approved\n"
        "hallways: 4\n\n"
        "## 2026-04-26T17:34:59Z\n\n"
        "anchor: user-preferences\n"
        "signal: present commit hunks alongside their messages\n"
        "hallways: 4\n"
    )
    entries, warnings = parse_shelf(p)
    assert warnings == []
    assert len(entries) == 2
    assert entries[0] == ShelfEntry(
        date=date(2026, 4, 27),
        slug="user-preferences",
        body=(
            "anchor: user-preferences\nsignal: spec-doc skeleton approved\nhallways: 4"
        ),
    )
    assert entries[1].date == date(2026, 4, 26)


def test_parse_shelf_missing_file_returns_empty(tmp_path: Path) -> None:
    entries, warnings = parse_shelf(tmp_path / "no-such.md")
    assert entries == []
    assert warnings == []  # missing file is empty state, not a failure


def test_parse_shelf_malformed_heading_emits_warning(tmp_path: Path) -> None:
    p = tmp_path / "broken.md"
    p.write_text(
        "# Shelf — broken\n\n"
        "## not-an-iso-timestamp\n\n"
        "anchor: broken\n"
        "signal: ok\n"
        "hallways: 4\n\n"
        "## 2026-04-25T10:00:00Z\n\n"
        "anchor: broken\n"
        "signal: also ok\n"
        "hallways: 4\n"
    )
    entries, warnings = parse_shelf(p)
    assert len(entries) == 1
    assert entries[0].date == date(2026, 4, 25)
    assert any("not-an-iso-timestamp" in w for w in warnings)


def test_parse_shelf_uses_file_stem_when_h1_missing(tmp_path: Path) -> None:
    p = tmp_path / "fallback-slug.md"
    p.write_text(
        "## 2026-04-27T00:00:00Z\n\nanchor: fallback-slug\nsignal: x\nhallways: 4\n"
    )
    entries, _ = parse_shelf(p)
    assert entries == [
        ShelfEntry(
            date=date(2026, 4, 27),
            slug="fallback-slug",
            body="anchor: fallback-slug\nsignal: x\nhallways: 4",
        )
    ]


def test_shelf_entry_is_frozen() -> None:
    entry = ShelfEntry(date=date(2026, 4, 27), slug="x", body="anchor: x\n")
    with pytest.raises(FrozenInstanceError):
        entry.slug = "y"  # type: ignore[misc]


def test_parse_shelf_strips_quoted_timestamp(tmp_path: Path) -> None:
    """The plan-prescribed strip('"') accepts quoted timestamps."""
    p = tmp_path / "quoted.md"
    p.write_text(
        "# Shelf — quoted\n\n"
        '## "2026-04-27T00:00:00Z"\n\n'
        "anchor: quoted\n"
        "signal: x\n"
        "hallways: 4\n"
    )
    entries, warnings = parse_shelf(p)
    assert warnings == []
    assert len(entries) == 1
    assert entries[0].date == date(2026, 4, 27)


def test_parse_shelf_h1_only_zero_entries(tmp_path: Path) -> None:
    """H1 present with no `## <ts>` blocks yields ([], [])."""
    p = tmp_path / "empty.md"
    p.write_text("# Shelf — empty\n\nNo entries yet.\n")
    entries, warnings = parse_shelf(p)
    assert entries == []
    assert warnings == []
