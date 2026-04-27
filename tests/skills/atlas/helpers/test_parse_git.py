"""Unit tests for skills/_shared/parse_git.py."""

from __future__ import annotations

import subprocess
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from skills._shared.parse_git import GitState, parse_git


def _init_repo(path: Path) -> None:
    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "t@t"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "t"],
        cwd=path,
        check=True,
        capture_output=True,
    )


def test_parse_git_returns_none_outside_repo(git_sandbox: Path) -> None:
    state, warnings = parse_git(git_sandbox)
    assert state is None
    assert warnings == []


def test_parse_git_in_clean_repo(git_sandbox: Path) -> None:
    _init_repo(git_sandbox)
    (git_sandbox / "x.txt").write_text("x\n")
    subprocess.run(
        ["git", "add", "x.txt"],
        cwd=git_sandbox,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=git_sandbox,
        check=True,
        capture_output=True,
    )
    state, warnings = parse_git(git_sandbox)
    assert isinstance(state, GitState)
    assert state.branch == "main"
    assert state.dirty == []
    assert state.recent_commits == ["init"]
    assert state.ahead == 0
    assert state.behind == 0
    assert warnings == []


def test_parse_git_dirty_files_listed(git_sandbox: Path) -> None:
    _init_repo(git_sandbox)
    (git_sandbox / "x.txt").write_text("x\n")
    subprocess.run(
        ["git", "add", "x.txt"],
        cwd=git_sandbox,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=git_sandbox,
        check=True,
        capture_output=True,
    )
    (git_sandbox / "x.txt").write_text("dirty\n")
    (git_sandbox / "y.txt").write_text("new\n")
    state, _ = parse_git(git_sandbox)
    assert state is not None
    assert sorted(state.dirty) == ["x.txt", "y.txt"]


def test_git_state_is_frozen() -> None:
    state = GitState(branch="main", ahead=0, behind=0)
    with pytest.raises(FrozenInstanceError):
        state.branch = "feat/x"  # type: ignore[misc]
