import subprocess
from pathlib import Path

import pytest

from skills.sync.scripts.gitignore import GitignoreFilter


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    subprocess.run(
        ["git", "init", "-q", str(tmp_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    (tmp_path / ".gitignore").write_text("ignored.txt\nbuild/\n")
    (tmp_path / "kept.txt").write_text("k")
    (tmp_path / "ignored.txt").write_text("i")
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "out.o").write_text("o")
    return tmp_path


def test_respects_gitignore(repo: Path) -> None:
    f = GitignoreFilter(root=repo)
    assert f.is_ignored(Path("ignored.txt")) is True
    assert f.is_ignored(Path("build/out.o")) is True
    assert f.is_ignored(Path("kept.txt")) is False


def test_non_git_root_returns_false(tmp_path: Path) -> None:
    f = GitignoreFilter(root=tmp_path)
    assert f.is_ignored(Path("anything.txt")) is False


def test_batch_ignored_returns_subset(repo: Path) -> None:
    f = GitignoreFilter(root=repo)
    paths = [Path("ignored.txt"), Path("kept.txt"), Path("build/out.o")]
    result = f.batch_ignored(paths)
    assert Path("ignored.txt") in result
    assert Path("build/out.o") in result
    assert Path("kept.txt") not in result


def test_batch_ignored_empty_input(repo: Path) -> None:
    f = GitignoreFilter(root=repo)
    assert f.batch_ignored([]) == frozenset()


def test_batch_ignored_non_git_root(tmp_path: Path) -> None:
    f = GitignoreFilter(root=tmp_path)
    assert f.batch_ignored([Path("anything.txt")]) == frozenset()


def test_is_ignored_from_subdirectory(repo: Path) -> None:
    """GitignoreFilter should work even when root is a subdirectory inside a repo."""
    sub = repo / "subdir"
    sub.mkdir()
    (sub / "ignored.txt").write_text("i")
    (sub / "kept.txt").write_text("k")
    # Point root at the subdirectory — git rev-parse --git-dir still succeeds
    f = GitignoreFilter(root=sub)
    # ignored.txt is listed in the parent's .gitignore so git still sees it
    assert f.is_ignored(Path("ignored.txt")) is True
    assert f.is_ignored(Path("kept.txt")) is False
