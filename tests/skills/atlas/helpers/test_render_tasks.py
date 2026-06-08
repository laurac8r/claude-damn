"""Test task-list rendering."""

from __future__ import annotations

from skills._shared.anchor import Anchor, AnchorSource
from skills.atlas.render import AtlasInput, TaskRecord, render


def _input_with_tasks(tasks: list[TaskRecord]) -> AtlasInput:
    return AtlasInput(
        anchor=Anchor(slug="x", source=AnchorSource.BRANCH),
        shelf_entries=[],
        git_state=None,
        checkpoint=None,
        task_list=tasks,
        mode="single",
    )


def test_render_tasks_empty_state() -> None:
    out = render(_input_with_tasks([]))
    assert "no active tasks" in out.lower()


def test_render_tasks_status_pills() -> None:
    tasks = [
        TaskRecord(id="1", subject="Done thing", status="completed", blocked_by=[]),
        TaskRecord(id="2", subject="Doing thing", status="in_progress", blocked_by=[]),
        TaskRecord(id="3", subject="Pending thing", status="pending", blocked_by=["2"]),
    ]
    out = render(_input_with_tasks(tasks))
    for s in ("completed", "in_progress", "pending"):
        assert s in out
    assert "Done thing" in out
    assert "blocked by 2" in out.lower()


def test_render_tasks_escapes_subject_and_blocked_by() -> None:
    tasks = [
        TaskRecord(
            id="1",
            subject='fix <script>alert(1)</script> & "edge"',
            status="pending",
            blocked_by=["<x>", "a&b"],
        )
    ]
    out = render(_input_with_tasks(tasks))
    assert "fix &lt;script&gt;alert(1)&lt;/script&gt; &amp; &quot;edge&quot;" in out
    assert "&lt;x&gt;" in out
    assert "a&amp;b" in out
    assert "<script>" not in out
    assert "<x>" not in out


def test_render_tasks_escapes_status() -> None:
    tasks = [
        TaskRecord(
            id="2",
            subject="normal subject",
            status='x"><script>alert(1)</script>',  # type: ignore[arg-type]
            blocked_by=[],
        )
    ]
    out = render(_input_with_tasks(tasks))
    assert "<script>" not in out
    assert "&lt;script&gt;" in out
    assert "&quot;" in out
