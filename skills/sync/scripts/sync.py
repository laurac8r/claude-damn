"""CLI entrypoint for the /sync skill.

Usage::

    uv run python -m skills.sync.scripts.sync [--from PATH] <target> [options]
    uv run python -m skills.sync.scripts.sync --to PATH    [options]
"""

import argparse
import sys
from pathlib import Path

from skills.sync.scripts.apply import ApplyOptions, run_apply
from skills.sync.scripts.exceptions import SyncError
from skills.sync.scripts.plan import PlanOptions, build_plan
from skills.sync.scripts.prompt import PromptOptions, approve_ops
from skills.sync.scripts.render import render_plan
from skills.sync.scripts.types import SyncPlan


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sync",
        description="Sync files between two local directories.",
    )
    p.add_argument(
        "target",
        nargs="?",
        help="Target directory (alternative to --to).",
    )
    p.add_argument(
        "--from",
        dest="source",  # "from" is a Python keyword; dest= maps it to a valid name
        metavar="PATH",
        help="Source directory (default: $PWD).",
    )
    p.add_argument(
        "--to",
        dest="target_flag",
        metavar="PATH",
        help="Target directory (alternative to positional arg).",
    )
    p.add_argument(
        "--mode",
        choices=["plan", "interactive", "push", "pull", "mirror"],
        default="plan",
        help="Sync mode (default: plan).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen; write nothing.",
    )
    p.add_argument("--yes", "-y", action="store_true", help="Auto-approve all prompts.")
    p.add_argument(
        "--limit", type=int, default=None, metavar="N", help="Cap operations at N."
    )
    p.add_argument(
        "--include",
        action="append",
        default=[],
        metavar="GLOB",
        help="Include only matching paths.",
    )
    p.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="Exclude matching paths.",
    )
    p.add_argument(
        "--no-gitignore", action="store_true", help="Disable .gitignore filtering."
    )
    p.add_argument(
        "--delete",
        action="store_true",
        help="Remove target-only files (orphan deletion).",
    )
    p.add_argument(
        "--claude",
        action="store_true",
        help="Carry over Claude-workflow files despite gitignore.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    source = Path(args.source) if args.source else Path.cwd()
    target_str = args.target_flag or args.target
    if not target_str:
        print(
            "error: a target directory is required (positional arg or --to)",
            file=sys.stderr,
        )
        return 2
    target = Path(target_str)

    plan_opts = PlanOptions(
        mode=args.mode,
        respect_gitignore=not args.no_gitignore,
        include=tuple(args.include),
        exclude=tuple(args.exclude),
        claude=args.claude,
    )

    try:
        plan = build_plan(source=source, target=target, opts=plan_opts)
    except SyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(render_plan(plan))

    if args.mode == "plan":
        return 0

    apply_opts = ApplyOptions(dry_run=args.dry_run, delete=args.delete)

    if args.mode == "interactive" and not args.yes:
        prompt_opts = PromptOptions(yes=False, limit=args.limit)
        try:
            approved_ops = approve_ops(plan.ops, prompt_opts)
        except KeyboardInterrupt:
            print("\nAborted.", file=sys.stderr)
            return 1
        plan = SyncPlan(
            source=plan.source,
            target=plan.target,
            mode=plan.mode,
            ops=approved_ops,
        )
    elif args.limit is not None:
        plan = SyncPlan(
            source=plan.source,
            target=plan.target,
            mode=plan.mode,
            ops=plan.ops[: args.limit],
        )

    try:
        run_apply(plan, apply_opts)
    except SyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
