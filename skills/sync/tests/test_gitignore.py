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
