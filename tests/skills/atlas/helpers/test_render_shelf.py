"""Test shelf-section rendering."""

from __future__ import annotations

from datetime import date

from skills._shared.anchor import Anchor, AnchorSource
from skills._shared.parse_shelf import ShelfEntry
from skills.atlas.render import AtlasInput, render


def _input_with_shelf(entries: list[ShelfEntry]) -> AtlasInput:
    return AtlasInput(
        anchor=Anchor(slug="x", source=AnchorSource.BRANCH),
        shelf_entries=entries,
        git_state=None,
        checkpoint=None,
        task_list=[],
        mode="single",
    )


def test_render_shelf_empty_state() -> None:
    out = render(_input_with_shelf([]))
    assert "no shelf entries" in out.lower() or "first visit" in out.lower()


def test_render_shelf_lists_entries_newest_first() -> None:
    entries = [
        ShelfEntry(date=date(2026, 4, 27), slug="x", body="signal: latest"),
        ShelfEntry(date=date(2026, 4, 25), slug="x", body="signal: older"),
    ]
    out = render(_input_with_shelf(entries))
    latest_pos = out.index("latest")
    older_pos = out.index("older")
    assert latest_pos < older_pos


def test_render_shelf_includes_dates() -> None:
    entries = [ShelfEntry(date=date(2026, 4, 27), slug="x", body="signal: x")]
    out = render(_input_with_shelf(entries))
    assert "2026-04-27" in out


def test_render_shelf_escapes_html_in_body() -> None:
    entries = [
        ShelfEntry(
            date=date(2026, 4, 27),
            slug="x",
            body='note: <script>alert(1)</script> & "quoted"',
        )
    ]
    out = render(_input_with_shelf(entries))
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in out
    assert "&amp;" in out
    assert "&quot;quoted&quot;" in out
    assert "<script>" not in out
