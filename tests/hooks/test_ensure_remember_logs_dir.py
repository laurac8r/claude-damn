"""Tests for ~/.claude/hooks/ensure_remember_logs_dir.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_HOOK = Path.home() / ".claude" / "hooks" / "ensure_remember_logs_dir.py"

# Import the module under test directly for unit tests.
sys.path.insert(0, str(Path.home() / ".claude" / "hooks"))
import ensure_remember_logs_dir as hook  # noqa: E402


# ---- unit: resolve_project_dir ---------------------------------------------


def test_resolve_project_dir_uses_payload_cwd(tmp_path: Path) -> None:
    assert hook.resolve_project_dir({"cwd": str(tmp_path)}) == tmp_path


def test_resolve_project_dir_falls_back_to_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    assert hook.resolve_project_dir({}) == tmp_path


def test_resolve_project_dir_returns_none_when_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    assert hook.resolve_project_dir({}) is None
    assert hook.resolve_project_dir(None) is None
    assert hook.resolve_project_dir("not-a-dict") is None


def test_resolve_project_dir_ignores_empty_cwd(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    assert hook.resolve_project_dir({"cwd": ""}) is None


# ---- unit: ensure_dirs ------------------------------------------------------


def test_ensure_dirs_creates_all_subdirs(tmp_path: Path) -> None:
    created = hook.ensure_dirs(tmp_path)
    assert (tmp_path / ".remember" / "logs").is_dir()
    assert (tmp_path / ".remember" / "tmp").is_dir()
    assert (tmp_path / ".remember" / "logs" / "autonomous").is_dir()
    # All three should be reported as freshly created.
    assert len(created) == 3


def test_ensure_dirs_is_idempotent(tmp_path: Path) -> None:
    hook.ensure_dirs(tmp_path)
    second = hook.ensure_dirs(tmp_path)
    # Second call creates nothing new.
    assert second == []


# ---- integration: stdin → stdout via subprocess ----------------------------


def _run_hook(payload: dict, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(_HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_subprocess_creates_dirs_with_payload_cwd(tmp_path: Path) -> None:
    result = _run_hook({"cwd": str(tmp_path)})
    assert result.returncode == 0
    assert result.stdout.strip() == "{}"
    assert (tmp_path / ".remember" / "logs").is_dir()


def test_subprocess_fails_open_on_malformed_json() -> None:
    result = subprocess.run(
        ["python3", str(_HOOK)],
        input="not json at all",
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "{}"
