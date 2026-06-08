"""Test git-section rendering in skills/atlas/render.py."""

from __future__ import annotations

from skills._shared.anchor import Anchor, AnchorSource
from skills._shared.parse_git import GitState
from skills.atlas.render import AtlasInput, render


def _input_with_git(git: GitState | None) -> AtlasInput:
    return AtlasInput(
        anchor=Anchor(slug="x", source=AnchorSource.BRANCH),
        shelf_entries=[],
        git_state=git,
        checkpoint=None,
        task_list=[],
        mode="single",
    )


def test_render_git_none_shows_empty_state_card() -> None:
    out = render(_input_with_git(None))
    assert "not in a git repo" in out.lower()


def test_render_git_shows_branch_and_dirty() -> None:
    state = GitState(
        branch="feat/foo",
        ahead=2,
        behind=1,
        dirty=["a.py", "b.py"],
        recent_commits=["init", "second"],
    )
    out = render(_input_with_git(state))
    assert "feat/foo" in out
    assert "a.py" in out
    assert "b.py" in out
    assert "init" in out


def test_render_git_clean_repo_shows_clean_marker() -> None:
    state = GitState(
        branch="main", ahead=0, behind=0, dirty=[], recent_commits=["only"]
    )
    out = render(_input_with_git(state))
    # Clean repos should not render the dirty list at all
    assert '<ul class="dirty"' not in out


def test_render_git_escapes_html_in_dirty_paths_and_commits() -> None:
    state = GitState(
        branch="feat/<x>",
        ahead=0,
        behind=0,
        dirty=["docs/<script>.py", "a&b.py"],
        recent_commits=['fix: add & guard "edge"', "<img onerror=alert(1)>"],
    )
    out = render(_input_with_git(state))
    # Escaped forms are present.
    assert "feat/&lt;x&gt;" in out
    assert "docs/&lt;script&gt;.py" in out
    assert "a&amp;b.py" in out
    assert "fix: add &amp; guard &quot;edge&quot;" in out
    # Raw unescaped payloads must never reach the output.
    assert "<script>" not in out
    assert "<img onerror=alert(1)>" not in out
