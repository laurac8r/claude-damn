"""Shared pytest fixtures for /sync tests."""

import shutil
import subprocess
import tempfile
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture
def sandboxed_worktree() -> Iterator[Path]:
    """Isolated git worktree sandboxed under /tmp/.

    Each test gets a detached worktree of the current repo at a fresh
    /tmp/sync-test-<uuid>/ path. Auto-removed on teardown, even if the
    test fails.
    """
    prefix = f"sync-test-{uuid.uuid4().hex[:8]}-"
    tmp_root = Path(tempfile.mkdtemp(prefix=prefix, dir="/tmp"))
    assert str(tmp_root).startswith("/tmp/"), "sandbox must live under /tmp/"
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(tmp_root)],
        capture_output=True,
        text=True,
        check=True,
    )
    try:
        yield tmp_root
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(tmp_root)],
            capture_output=True,
            text=True,
            check=False,
        )
        shutil.rmtree(tmp_root, ignore_errors=True)
