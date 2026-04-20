from pathlib import Path

from skills.sync.scripts.render import render_plan
from skills.sync.scripts.types import FileOp, SyncPlan


def test_render_summary_counts_per_action() -> None:
    plan = SyncPlan(
        source=Path("/s"),
        target=Path("/t"),
        mode="push",
        ops=(
            FileOp(Path("a.txt"), "add", "src→tgt", "only in source"),
            FileOp(Path("b.txt"), "add", "src→tgt", "only in source"),
            FileOp(Path("c.txt"), "update", "src→tgt", "content differs"),
        ),
    )
    out = render_plan(plan)
    assert "push" in out
    assert "/s" in out and "/t" in out
    assert "add: 2" in out
    assert "update: 1" in out
    assert "a.txt" in out


def test_render_empty_plan_says_noop() -> None:
    plan = SyncPlan(source=Path("/s"), target=Path("/t"), mode="push", ops=())
    out = render_plan(plan)
    assert "nothing to do" in out.lower()
