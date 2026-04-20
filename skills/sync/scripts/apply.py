"""Apply a SyncPlan by shelling out to rsync.

Always uses explicit `list[str]` argv (never shell=True). The file list is
written to a tempfile and passed via `--files-from`. Rsync failures are
wrapped in RsyncFailedError with stderr attached. Target-not-writable
errors are detected up front and raised as TargetNotWritableError.
"""

import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from skills.sync.scripts.exceptions import RsyncFailedError, TargetNotWritableError
from skills.sync.scripts.types import FileOp, SyncPlan


@dataclass(frozen=True)
class ApplyOptions:
    dry_run: bool = False
    delete: bool = False


def run_apply(plan: SyncPlan, opts: ApplyOptions) -> None:
    if not plan.ops:
        return

    src_to_tgt = tuple(op for op in plan.ops if op.direction == "src→tgt")
    tgt_to_src = tuple(op for op in plan.ops if op.direction == "tgt→src")

    # Preflight: check every destination we will actually write into.
    if src_to_tgt:
        _check_target_writable(plan.target)
    if tgt_to_src:
        _check_target_writable(plan.source)

    if src_to_tgt:
        _rsync(plan.source, plan.target, src_to_tgt, opts)
    if tgt_to_src:
        _rsync(plan.target, plan.source, tgt_to_src, opts)

    if opts.delete and not opts.dry_run:
        _delete_orphans(plan.source, plan.target, src_to_tgt)


def _check_target_writable(target: Path) -> None:
    if not target.exists():
        try:
            target.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise TargetNotWritableError(
                f"cannot create target {target}: {exc}"
            ) from exc
    if not os.access(target, os.W_OK):
        raise TargetNotWritableError(f"target {target} is not writable")


def _delete_orphans(src: Path, dst: Path, ops: tuple[FileOp, ...]) -> None:
    """Remove files in dst that don't exist in src's synced set.

    Only considers files that were part of the synced path set; ``.git/``
    internals and other excluded paths are never touched.
    """
    synced = {op.path for op in ops}
    for child in sorted(dst.rglob("*")):
        if not child.is_file():
            continue
        rel = child.relative_to(dst)
        if rel.parts and rel.parts[0] == ".git":
            continue
        if rel not in synced and not (src / rel).exists():
            child.unlink()


def _rsync(src: Path, dst: Path, ops: tuple[FileOp, ...], opts: ApplyOptions) -> None:
    with tempfile.NamedTemporaryFile(
        "w", delete=False, prefix="sync-files-", suffix=".lst"
    ) as fh:
        for op in ops:
            fh.write(f"{op.path}\n")
        files_from = fh.name

    argv: list[str] = [
        "rsync",
        "-a",
        "--files-from",
        files_from,
        f"{src}/",
        f"{dst}/",
    ]
    if opts.dry_run:
        argv.insert(2, "--dry-run")

    try:
        subprocess.run(argv, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as exc:
        raise RsyncFailedError(f"rsync failed: {exc}", stderr=exc.stderr or "") from exc
    finally:
        Path(files_from).unlink(missing_ok=True)
