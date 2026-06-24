"""Test --all mode suppresses git/checkpoint/tasks; keeps shelf only."""

from __future__ import annotations

from datetime import date

from skills._shared.anchor import Anchor, AnchorSource
from skills._shared.parse_checkpoint import CheckpointDoc
from skills._shared.parse_git import GitState
from skills._shared.parse_shelf import ShelfEntry
from skills.atlas.render import AtlasInput, TaskRecord, render


def _full_input(mode: str) -> AtlasInput:
    return AtlasInput(
        anchor=Anchor(slug="multi", source=AnchorSource.BRANCH),
        shelf_entries=[
            ShelfEntry(date=date(2026, 4, 27), slug="multi", body="signal: x")
        ],
        git_state=GitState(
            branch="main", ahead=0, behind=0, dirty=[], recent_commits=["c"]
        ),
        checkpoint=CheckpointDoc(branch="main", current_state="x", raw="x"),
        task_list=[TaskRecord(id="1", subject="t", status="pending", blocked_by=[])],
        mode=mode,  # type: ignore[arg-type]
    )


def test_single_mode_renders_all_sections() -> None:
    out = render(_full_input("single"))
    assert 'class="git' in out
    assert 'class="shelf' in out
    assert 'class="checkpoint' in out
    assert 'class="tasks' in out


def test_all_mode_suppresses_per_project_sections() -> None:
    out = render(_full_input("all"))
    assert 'class="git' not in out
    assert 'class="checkpoint' not in out
    assert 'class="tasks' not in out
    # shelf is preserved
    assert 'class="shelf' in out
