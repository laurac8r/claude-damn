"""Smallest-possible-render tests for skills/atlas/render.py::render."""

from __future__ import annotations

from skills._shared.anchor import Anchor, AnchorSource
from skills.atlas.render import AtlasInput, render


def _empty_input() -> AtlasInput:
    return AtlasInput(
        anchor=Anchor(slug="void", source=AnchorSource.UNRESOLVED),
        shelf_entries=[],
        git_state=None,
        checkpoint=None,
        task_list=[],
        mode="single",
    )


def test_render_returns_string() -> None:
    out = render(_empty_input())
    assert isinstance(out, str)


def test_render_returns_full_html_doc() -> None:
    out = render(_empty_input())
    assert out.lstrip().lower().startswith("<!doctype html>")
    assert "</html>" in out.lower()


def test_render_includes_anchor_slug() -> None:
    out = render(_empty_input())
    assert "void" in out
