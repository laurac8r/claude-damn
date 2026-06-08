"""Test checkpoint-section rendering in skills/atlas/render.py."""

from __future__ import annotations

from skills._shared.anchor import Anchor, AnchorSource
from skills._shared.parse_checkpoint import CheckpointDoc
from skills.atlas.render import AtlasInput, render


def _input_with_ckpt(ckpt: CheckpointDoc | None) -> AtlasInput:
    return AtlasInput(
        anchor=Anchor(slug="x", source=AnchorSource.BRANCH),
        shelf_entries=[],
        git_state=None,
        checkpoint=ckpt,
        task_list=[],
        mode="single",
    )


def test_render_checkpoint_none_empty_state() -> None:
    out = render(_input_with_ckpt(None))
    assert "no checkpoint saved" in out.lower()


def test_render_checkpoint_full_doc() -> None:
    doc = CheckpointDoc(
        branch="feat/foo",
        current_state="working on section 3",
        next_steps=["1. Do A", "2. Do B"],
        key_decisions=["- X locked"],
        blockers=["- None"],
        raw="...",
    )
    out = render(_input_with_ckpt(doc))
    assert "feat/foo" in out
    assert "Do A" in out
    assert "Do B" in out
    assert "X locked" in out


def test_render_checkpoint_unparseable_falls_back_to_raw() -> None:
    raw = "garbage CHECKPOINT.md content"
    doc = CheckpointDoc(branch="", current_state="", raw=raw)
    out = render(_input_with_ckpt(doc))
    assert raw in out  # the raw fallback is in the page


def test_render_checkpoint_escapes_html() -> None:
    # Structured path — special chars in every interpolated field.
    doc = CheckpointDoc(
        branch="feat/<x>",
        current_state="state: <script>1</script>",
        next_steps=['1. Do <a> & "b"'],
        key_decisions=["- decided: <X>"],
        blockers=['- "blocked"'],
        raw="ignored on this path",
    )
    out = render(_input_with_ckpt(doc))
    assert "feat/&lt;x&gt;" in out
    assert "state: &lt;script&gt;1&lt;/script&gt;" in out
    assert "Do &lt;a&gt; &amp; &quot;b&quot;" in out
    assert "decided: &lt;X&gt;" in out
    assert "&quot;blocked&quot;" in out
    assert "<script>" not in out

    # Raw-fallback path — the entire raw markdown blob must be escaped.
    raw = "## Section\n```\n<script>alert(1)</script>\n```\n"
    doc2 = CheckpointDoc(branch="", current_state="", raw=raw)
    out2 = render(_input_with_ckpt(doc2))
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in out2
    assert "<script>alert(1)</script>" not in out2
