import os
from pathlib import Path

import pytest

from skills.sync.scripts.diff import diff_ops
from skills.sync.scripts.exceptions import InvalidModeError
from skills.sync.scripts.types import FileOp


def _touch(p: Path, content: str = "x", mtime: float | None = None) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    if mtime is not None:
        os.utime(p, (mtime, mtime))


@pytest.fixture
def trees(tmp_path: Path) -> tuple[Path, Path]:
    src = tmp_path / "src"
    tgt = tmp_path / "tgt"
    src.mkdir()
    tgt.mkdir()
    return src, tgt


def test_push_only_in_source_is_add(trees: tuple[Path, Path]) -> None:
    src, tgt = trees
    _touch(src / "a.txt", "a")
    ops = diff_ops(src, tgt, mode="push", src_paths={Path("a.txt")}, tgt_paths=set())
    assert ops == (FileOp(Path("a.txt"), "add", "src→tgt", "only in source"),)


def test_push_differing_content_is_update(trees: tuple[Path, Path]) -> None:
    src, tgt = trees
    _touch(src / "a.txt", "new")
    _touch(tgt / "a.txt", "old")
    ops = diff_ops(
        src, tgt, mode="push", src_paths={Path("a.txt")}, tgt_paths={Path("a.txt")}
    )
    assert len(ops) == 1
    assert ops[0].action == "update"
    assert ops[0].direction == "src→tgt"


def test_push_identical_content_is_skip(trees: tuple[Path, Path]) -> None:
    src, tgt = trees
    _touch(src / "a.txt", "same")
    _touch(tgt / "a.txt", "same")
    ops = diff_ops(
        src, tgt, mode="push", src_paths={Path("a.txt")}, tgt_paths={Path("a.txt")}
    )
    assert ops == ()


def test_push_target_only_not_touched(trees: tuple[Path, Path]) -> None:
    src, tgt = trees
    _touch(tgt / "only.txt", "t")
    ops = diff_ops(src, tgt, mode="push", src_paths=set(), tgt_paths={Path("only.txt")})
    assert ops == ()


def test_pull_is_inverse_of_push(trees: tuple[Path, Path]) -> None:
    src, tgt = trees
    _touch(tgt / "a.txt", "a")
    ops = diff_ops(src, tgt, mode="pull", src_paths=set(), tgt_paths={Path("a.txt")})
    assert ops == (FileOp(Path("a.txt"), "add", "tgt→src", "only in target"),)


def test_mirror_newer_source_wins(trees: tuple[Path, Path]) -> None:
    src, tgt = trees
    _touch(src / "a.txt", "new", mtime=200)
    _touch(tgt / "a.txt", "old", mtime=100)
    ops = diff_ops(
        src, tgt, mode="mirror", src_paths={Path("a.txt")}, tgt_paths={Path("a.txt")}
    )
    assert ops[0].direction == "src→tgt"
    assert ops[0].reason == "newer mtime in source"


def test_mirror_newer_target_wins(trees: tuple[Path, Path]) -> None:
    src, tgt = trees
    _touch(src / "a.txt", "old", mtime=100)
    _touch(tgt / "a.txt", "new", mtime=200)
    ops = diff_ops(
        src, tgt, mode="mirror", src_paths={Path("a.txt")}, tgt_paths={Path("a.txt")}
    )
    assert ops[0].direction == "tgt→src"
    assert ops[0].reason == "newer mtime in target"


def test_mirror_source_only_adds_to_target(trees: tuple[Path, Path]) -> None:
    src, tgt = trees
    _touch(src / "a.txt", "a")
    ops = diff_ops(src, tgt, mode="mirror", src_paths={Path("a.txt")}, tgt_paths=set())
    assert ops[0].direction == "src→tgt"
    assert ops[0].action == "add"


def test_mirror_target_only_adds_to_source(trees: tuple[Path, Path]) -> None:
    src, tgt = trees
    _touch(tgt / "a.txt", "a")
    ops = diff_ops(src, tgt, mode="mirror", src_paths=set(), tgt_paths={Path("a.txt")})
    assert ops[0].direction == "tgt→src"
    assert ops[0].action == "add"


def test_unsupported_mode_raises_invalid_mode_error(trees: tuple[Path, Path]) -> None:
    src, tgt = trees
    with pytest.raises(InvalidModeError):
        diff_ops(src, tgt, mode="bogus", src_paths=set(), tgt_paths=set())  # ty: ignore[invalid-argument-type]
