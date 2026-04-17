"""Per-directory y/n/a interactive approval, dropbox-restore-style."""

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .types import FileOp


@dataclass(frozen=True)
class PromptOptions:
    yes: bool = False
    limit: int | None = None


def approve_ops(ops: tuple[FileOp, ...], opts: PromptOptions) -> tuple[FileOp, ...]:
    """Return the subset of `ops` the user (or --yes) approved."""
    if opts.yes:
        return _apply_limit(ops, opts.limit)

    grouped: dict[Path, list[FileOp]] = defaultdict(list)
    for op in ops:
        grouped[op.path.parent].append(op)

    approved: list[FileOp] = []
    approve_all = False
    for directory in sorted(grouped):
        dir_ops = grouped[directory]
        if approve_all:
            approved.extend(dir_ops)
            continue
        answer = _ask(directory, dir_ops)
        if answer == "a":
            approve_all = True
            approved.extend(dir_ops)
        elif answer == "y":
            approved.extend(dir_ops)
    return _apply_limit(tuple(approved), opts.limit)


def _ask(directory: Path, dir_ops: list[FileOp]) -> str:
    prompt = f"{directory}/ ({len(dir_ops)} file ops) — [y]es / [n]o / [a]ll: "
    while True:
        answer = input(prompt).strip().lower() or "y"
        if answer in ("y", "n", "a"):
            return answer


def _apply_limit(ops: tuple[FileOp, ...], limit: int | None) -> tuple[FileOp, ...]:
    if limit is None:
        return ops
    return ops[:limit]
