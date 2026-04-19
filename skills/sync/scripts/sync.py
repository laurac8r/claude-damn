"""CLI entrypoint for /sync.

Invoked as ``python -m skills.sync.scripts.sync`` or via the /sync skill.
Parses arguments, builds a SyncPlan, optionally prompts for interactive
approval, then applies the plan via rsync.
"""

import argparse
import dataclasses
import sys
from pathlib import Path

from skills.sync.scripts.apply import ApplyOptions, run_apply
from skills.sync.scripts.exceptions import (
    RsyncFailedError,
    SourceNotFoundError,
    SyncError,
)
from skills.sync.scripts.plan import PlanOptions, build_plan
from skills.sync.scripts.prompt import PromptOptions, approve_ops
from skills.sync.scripts.render import render_plan
from skills.sync.scripts.types import SyncPlan


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sync", description="Sync files between directories."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Target directory (positional).",
    )
    parser.add_argument(
        "--from",
        dest="source",
        type=Path,
        default=None,
        metavar="PATH",
        help="Source directory (default: cwd).",
    )
    parser.add_argument(
        "--to",
        dest="to",
        type=Path,
        default=None,
        metavar="PATH",
        help="Target directory (alternative to positional).",
    )
    parser.add_argument(
        "--mode",
        choices=["plan", "interactive", "push", "pull", "mirror"],
        default="plan",
        help="Sync mode (default: plan).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without copying anything.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Approve all operations without prompting.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Limit the number of operations applied.",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=None,
        metavar="GLOB",
        help="Glob pattern to include (repeatable).",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=None,
        metavar="GLOB",
        help="Glob pattern to exclude (repeatable).",
    )
    parser.add_argument(
        "--no-gitignore",
        action="store_true",
        help="Ignore .gitignore rules.",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete target-only files after sync.",
    )
    parser.add_argument(
        "--claude",
        action="store_true",
        help="Include CLAUDE.md and allowlisted files even if gitignored.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and run the sync pipeline. Returns an exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Resolve target: exactly one of positional or --to must be given.
    if args.target is not None and args.to is not None:
        parser.error("target: use positional or --to, not both")
    if args.target is None and args.to is None:
        parser.error("target required (positional or --to)")

    effective_target: Path = (
        Path(args.target).resolve() if args.target else Path(args.to).resolve()
    )
    effective_source: Path = (
        Path(args.source).resolve() if args.source else Path.cwd().resolve()
    )

    try:
        if not effective_source.is_dir():
            raise SourceNotFoundError(f"source not found: {effective_source}")

        plan_opts = PlanOptions(
            mode=args.mode,
            respect_gitignore=not args.no_gitignore,
            include=tuple(args.include or ()),
            exclude=tuple(args.exclude or ()),
            claude=args.claude,
        )
        plan: SyncPlan = build_plan(effective_source, effective_target, plan_opts)
        print(render_plan(plan))

        if args.mode == "plan":
            return 0

        if args.mode == "interactive":
            try:
                approved = approve_ops(
                    plan.ops, PromptOptions(yes=args.yes, limit=args.limit)
                )
            except KeyboardInterrupt:
                print("Sync operation cancelled by user.", file=sys.stderr)
                return 1
            plan = dataclasses.replace(plan, ops=approved)
        elif args.limit is not None:
            plan = dataclasses.replace(plan, ops=plan.ops[: args.limit])

        try:
            run_apply(plan, ApplyOptions(dry_run=args.dry_run, delete=args.delete))
        except OSError as exc:
            raise SyncError(f"failed to execute rsync: {exc}") from exc
        return 0

    except RsyncFailedError as exc:
        print(f"/sync: {exc}", file=sys.stderr)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        return 1
    except SyncError as exc:
        print(f"/sync: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
