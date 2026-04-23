"""Integration test: /sync invocation works from any directory.

Verifies the SKILL.md-documented command (`PYTHONPATH="$HOME/.claude" python3 -m
skills.sync.scripts.sync ...`) succeeds when run from a directory that does
NOT contain a `skills/` package or a `pyproject.toml`.
"""

import os
import subprocess
import sys
from pathlib import Path


def test_sync_invocation_works_from_any_directory(tmp_path: Path) -> None:
    """Running `python3 -m skills.sync.scripts.sync --help` succeeds from /tmp.

    Reproduces the bug where `python -m skills.sync.scripts.sync` failed with
    `ModuleNotFoundError: No module named 'skills'` when CWD was not the
    claude-damn repo root.
    """
    repo_root = Path(__file__).resolve().parents[3]
    assert (repo_root / "skills" / "sync" / "scripts" / "sync.py").is_file(), (
        f"expected repo root containing skills/ under {repo_root}"
    )

    env = {**os.environ, "PYTHONPATH": str(repo_root)}
    result = subprocess.run(
        [sys.executable, "-m", "skills.sync.scripts.sync", "--help"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        f"invocation failed from {tmp_path}: "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "usage: sync" in result.stdout
