"""Orchestrator: compose discover + diff into a SyncPlan."""

from dataclasses import dataclass, field
from pathlib import Path

from skills.sync.scripts.claude_allowlist import load_claude_allowlist
from skills.sync.scripts.diff import diff_ops
from skills.sync.scripts.discover import DiscoverOptions, discover
from skills.sync.scripts.types import Mode, SyncPlan


@dataclass(frozen=True)
class PlanOptions:
    mode: Mode = "plan"
    respect_gitignore: bool = True
    include: tuple[str, ...] = field(default_factory=tuple)
    exclude: tuple[str, ...] = field(default_factory=tuple)
    claude: bool = False
    custom_allowlist_file: Path = field(
        default_factory=lambda: Path.home() / ".claude" / "sync-allowlist.txt"
    )


def build_plan(source: Path, target: Path, opts: PlanOptions) -> SyncPlan:
    allowlist = (
        load_claude_allowlist(opts.custom_allowlist_file) if opts.claude else None
    )
    discover_opts = DiscoverOptions(
        respect_gitignore=opts.respect_gitignore,
        include=opts.include,
        exclude=opts.exclude,
        claude_allowlist=allowlist,
    )
    src_paths = set(discover(source, discover_opts))
    tgt_paths = set(discover(target, discover_opts)) if target.exists() else set()
    ops = diff_ops(
        source=source,
        target=target,
        mode=opts.mode,
        src_paths=src_paths,
        tgt_paths=tgt_paths,
    )
    return SyncPlan(source=source, target=target, mode=opts.mode, ops=ops)
