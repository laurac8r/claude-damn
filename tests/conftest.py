"""Shared fixtures for settings.json regression tests and xdist worktrees."""

import json
import os
import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest

SETTINGS_PATH = Path(__file__).parent / "fixtures" / "settings.json"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SETTINGS_PATH = PROJECT_ROOT / "settings.json"


@pytest.fixture(scope="session")
def worker_worktree(tmp_path_factory) -> Iterator[Path | None]:
    """Yield an ephemeral git worktree for the current xdist worker.

    Returns ``None`` when not running under xdist (``pytest -n``),
    making the fixture a no-op for default single-process runs.
    """
    worker_id = os.environ.get("PYTEST_XDIST_WORKER")
    if worker_id is None:
        yield None
        return
    wt_path = tmp_path_factory.mktemp(f"pytest-{worker_id}")
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(wt_path), "HEAD"],
        check=True,
        cwd=str(PROJECT_ROOT),
    )
    try:
        yield wt_path
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(wt_path)],
            check=False,
            cwd=str(PROJECT_ROOT),
        )


@pytest.fixture(scope="session")
def settings() -> dict:
    """Load settings.json once for the entire test session."""
    return json.loads(SETTINGS_PATH.read_text())


@pytest.fixture(scope="session")
def permissions(settings: dict) -> dict:
    """Extract the permissions block."""
    return settings["permissions"]


@pytest.fixture(scope="session")
def allow_list(permissions: dict) -> list[str]:
    return permissions["allow"]


@pytest.fixture(scope="session")
def deny_list(permissions: dict) -> list[str]:
    return permissions["deny"]


@pytest.fixture(scope="session")
def ask_list(permissions: dict) -> list[str]:
    return permissions["ask"]


@pytest.fixture(scope="session")
def enabled_plugins(settings: dict) -> dict[str, bool]:
    return settings["enabledPlugins"]
