"""Test warnings rendering at the top of the page."""

from __future__ import annotations

from skills._shared.anchor import Anchor, AnchorSource
from skills.atlas.render import AtlasInput, render


def _input_with_warnings(warnings: list[str]) -> AtlasInput:
    return AtlasInput(
        anchor=Anchor(slug="x", source=AnchorSource.BRANCH),
        shelf_entries=[],
        git_state=None,
        checkpoint=None,
        task_list=[],
        mode="single",
        warnings=warnings,
    )


def test_no_warnings_means_no_warning_card() -> None:
    out = render(_input_with_warnings([]))
    assert 'class="warnings"' not in out


def test_warnings_render_as_visible_card() -> None:
    out = render(
        _input_with_warnings(
            ["shelf entry skipped: bad heading", "git command failed: blah"]
        )
    )
    assert 'class="warnings"' in out
    assert "shelf entry skipped" in out
    assert "git command failed" in out


def test_render_warnings_escapes_html() -> None:
    out = render(
        _input_with_warnings(
            [
                "parse failed at <path>/foo.md: <bad tag>",
                'git: "fatal" & abort',
            ]
        )
    )
    assert "parse failed at &lt;path&gt;/foo.md: &lt;bad tag&gt;" in out
    assert "git: &quot;fatal&quot; &amp; abort" in out
    assert "<path>" not in out
    assert "<bad tag>" not in out
