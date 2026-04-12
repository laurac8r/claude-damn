from pathlib import Path

import pytest

from skills.sync.scripts.types import FileOp, SyncPlan


def test_file_op_is_frozen() -> None:
    op = FileOp(
        path=Path("a.txt"),
        action="add",
        direction="src→tgt",
        reason="only in source",
    )
    with pytest.raises(AttributeError):
        op.action = "delete"  # type: ignore[misc]


def test_sync_plan_ops_is_tuple() -> None:
    plan = SyncPlan(
        source=Path("/src"),
        target=Path("/tgt"),
        mode="push",
        ops=(
            FileOp(
                path=Path("a.txt"),
                action="add",
                direction="src→tgt",
                reason="only in source",
            ),
        ),
    )
    assert isinstance(plan.ops, tuple)
    assert len(plan.ops) == 1
