import subprocess
from pathlib import Path

import pytest

from skills.sync.scripts.plan import PlanOptions, build_plan


@pytest.fixture
def src(tmp_path: Path) -> Path:
    root = tmp_path / "src"
    root.mkdir()
    subprocess.run(
        ["git", "init", "-q", str(root)], check=True, capture_output=True, text=True
    )
    (root / ".gitignore").write_text("ignored.txt\n")
    (root / "a.txt").write_text("a")
    (root / "ignored.txt").write_text("i")
    return root


@pytest.fixture
def tgt(tmp_path: Path) -> Path:
    root = tmp_path / "tgt"
    root.mkdir()
    return root


def test_build_plan_push_default(src: Path, tgt: Path) -> None:
    plan = build_plan(src, tgt, PlanOptions(mode="push"))
    assert plan.mode == "push"
    assert plan.source == src
    assert plan.target == tgt
    paths = {op.path for op in plan.ops}
    assert Path("a.txt") in paths
    assert Path("ignored.txt") not in paths


def test_build_plan_claude_flag_enables_allowlist(src: Path, tgt: Path) -> None:
    (src / "CLAUDE.md").write_text("c")
    (src / ".gitignore").write_text("ignored.txt\nCLAUDE.md\n")
    plan = build_plan(src, tgt, PlanOptions(mode="push", claude=True))
    paths = {op.path for op in plan.ops}
    assert Path("CLAUDE.md") in paths
