"""Mode-specific conversion of (src_paths, tgt_paths) pairs into FileOps."""

import hashlib
from pathlib import Path

from skills.sync.scripts.exceptions import InvalidModeError
from skills.sync.scripts.types import FileOp, Mode


def diff_ops(
    source: Path,
    target: Path,
    mode: Mode,
    src_paths: set[Path],
    tgt_paths: set[Path],
) -> tuple[FileOp, ...]:
    """Return the ordered tuple of operations implied by the two path sets."""
    if mode in ("push", "interactive", "plan"):
        return _diff_push(source, target, src_paths, tgt_paths)
    if mode == "pull":
        return _flip(_diff_push(target, source, tgt_paths, src_paths))
    if mode == "mirror":
        return _diff_mirror(source, target, src_paths, tgt_paths)
    raise InvalidModeError(f"unsupported mode: {mode}")


def _diff_push(
    source: Path,
    target: Path,
    src_paths: set[Path],
    tgt_paths: set[Path],
) -> tuple[FileOp, ...]:
    ops: list[FileOp] = []
    for rel in sorted(src_paths):
        if rel not in tgt_paths:
            ops.append(FileOp(rel, "add", "src→tgt", "only in source"))
            continue
        if _same_content(source / rel, target / rel):
            continue
        ops.append(FileOp(rel, "update", "src→tgt", "content differs"))
    return tuple(ops)


def _diff_mirror(
    source: Path,
    target: Path,
    src_paths: set[Path],
    tgt_paths: set[Path],
) -> tuple[FileOp, ...]:
    ops: list[FileOp] = []
    for rel in sorted(src_paths - tgt_paths):
        ops.append(FileOp(rel, "add", "src→tgt", "only in source"))
    for rel in sorted(tgt_paths - src_paths):
        ops.append(FileOp(rel, "add", "tgt→src", "only in target"))
    for rel in sorted(src_paths & tgt_paths):
        s_abs = source / rel
        t_abs = target / rel
        if _same_content(s_abs, t_abs):
            continue
        s_m = s_abs.stat().st_mtime
        t_m = t_abs.stat().st_mtime
        if s_m >= t_m:
            ops.append(FileOp(rel, "update", "src→tgt", "newer mtime in source"))
        else:
            ops.append(FileOp(rel, "update", "tgt→src", "newer mtime in target"))
    return tuple(ops)


def _flip(ops: tuple[FileOp, ...]) -> tuple[FileOp, ...]:
    return tuple(
        FileOp(
            path=o.path,
            action=o.action,
            direction="tgt→src" if o.direction == "src→tgt" else "src→tgt",
            reason=o.reason.replace("source", "__SRC__")
            .replace("target", "source")
            .replace("__SRC__", "target"),
        )
        for o in ops
    )


def _same_content(a: Path, b: Path) -> bool:
    if a.stat().st_size != b.stat().st_size:
        return False
    return _sha(a) == _sha(b)


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
