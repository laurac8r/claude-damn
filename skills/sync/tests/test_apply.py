from pathlib import Path

import pytest

from skills.sync.scripts.apply import ApplyOptions, run_apply
from skills.sync.scripts.exceptions import RsyncFailedError, TargetNotWritableError
from skills.sync.scripts.types import FileOp, SyncPlan


def _make_trees(root: Path) -> tuple[Path, Path]:
    src = root / "src"
    tgt = root / "tgt"
    src.mkdir(exist_ok=True)
    tgt.mkdir(exist_ok=True)
    return src, tgt


def test_push_copies_files(sandboxed_worktree: Path) -> None:
    src, tgt = _make_trees(sandboxed_worktree)
    (src / "a.txt").write_text("hello")
    (src / "sub").mkdir()
    (src / "sub" / "b.txt").write_text("world")
    plan = SyncPlan(
        source=src,
        target=tgt,
        mode="push",
        ops=(
            FileOp(Path("a.txt"), "add", "src→tgt", "only in source"),
            FileOp(Path("sub/b.txt"), "add", "src→tgt", "only in source"),
        ),
    )
    run_apply(plan, ApplyOptions())
    assert (tgt / "a.txt").read_text() == "hello"
    assert (tgt / "sub" / "b.txt").read_text() == "world"


def test_dry_run_leaves_target_untouched(sandboxed_worktree: Path) -> None:
    src, tgt = _make_trees(sandboxed_worktree)
    (src / "a.txt").write_text("hello")
    plan = SyncPlan(
        source=src,
        target=tgt,
        mode="push",
        ops=(FileOp(Path("a.txt"), "add", "src→tgt", "only in source"),),
    )
    run_apply(plan, ApplyOptions(dry_run=True))
    assert not (tgt / "a.txt").exists()


def test_delete_flag_removes_target_only(sandboxed_worktree: Path) -> None:
    src, tgt = _make_trees(sandboxed_worktree)
    (src / "a.txt").write_text("a")
    (tgt / "a.txt").write_text("a")
    (tgt / "orphan.txt").write_text("old")
    plan = SyncPlan(
        source=src,
        target=tgt,
        mode="push",
        ops=(FileOp(Path("a.txt"), "add", "src→tgt", "only in source"),),
    )
    run_apply(plan, ApplyOptions(delete=True))
    assert not (tgt / "orphan.txt").exists()


def test_no_delete_preserves_target_only(sandboxed_worktree: Path) -> None:
    src, tgt = _make_trees(sandboxed_worktree)
    (src / "a.txt").write_text("a")
    (tgt / "orphan.txt").write_text("keep me")
    plan = SyncPlan(
        source=src,
        target=tgt,
        mode="push",
        ops=(FileOp(Path("a.txt"), "add", "src→tgt", "only in source"),),
    )
    run_apply(plan, ApplyOptions(delete=False))
    assert (tgt / "orphan.txt").read_text() == "keep me"


def test_unwritable_target_raises(sandboxed_worktree: Path) -> None:
    src, tgt = _make_trees(sandboxed_worktree)
    (src / "a.txt").write_text("a")
    tgt.chmod(0o500)
    plan = SyncPlan(
        source=src,
        target=tgt,
        mode="push",
        ops=(FileOp(Path("a.txt"), "add", "src→tgt", "only in source"),),
    )
    try:
        with pytest.raises((TargetNotWritableError, RsyncFailedError)):
            run_apply(plan, ApplyOptions())
    finally:
        tgt.chmod(0o700)
