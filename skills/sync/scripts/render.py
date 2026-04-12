"""Human-readable plan renderer for --mode plan and --dry-run."""

from collections import Counter

from skills.sync.scripts.types import SyncPlan

_SAMPLE_LIMIT = 10


def render_plan(plan: SyncPlan) -> str:
    lines: list[str] = [
        f"Sync plan ({plan.mode}): {plan.source} → {plan.target}",
        "",
    ]
    if not plan.ops:
        lines.append("  (nothing to do — source and target already in sync)")
        return "\n".join(lines)

    counts = Counter(op.action for op in plan.ops)
    for action in ("add", "update", "delete", "skip"):
        if counts[action]:
            lines.append(f"  {action}: {counts[action]}")
    lines.append("")
    lines.append("First operations:")
    for op in plan.ops[:_SAMPLE_LIMIT]:
        arrow = "→" if op.direction == "src→tgt" else "←"
        lines.append(f"  {op.action:6s} {arrow} {op.path}  ({op.reason})")
    if len(plan.ops) > _SAMPLE_LIMIT:
        lines.append(f"  … and {len(plan.ops) - _SAMPLE_LIMIT} more")
    return "\n".join(lines)
