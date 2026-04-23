"""Unit tests for tests/_skill_helpers.py shared helpers.

Covers the dataclass shape and invoke_skill signature without shelling out
to a real `claude -p` subprocess.
"""

import os
import subprocess
from pathlib import Path

import pytest

from tests._skill_helpers import PROJECT_ROOT, SkillResult, invoke_skill


def test_skill_result_is_dataclass_with_three_fields() -> None:
    result = SkillResult(stdout="out", stderr="err", returncode=0)
    assert result.stdout == "out"
    assert result.stderr == "err"
    assert result.returncode == 0


def test_project_root_points_at_repo_root() -> None:
    assert (PROJECT_ROOT / "pyproject.toml").exists()


class _FakeRun:
    """Captures the last subprocess.run call and returns a canned result."""

    def __init__(self, stdout: str = "", stderr: str = "", returncode: int = 0) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.last_args: tuple = ()
        self.last_kwargs: dict = {}

    def __call__(self, *args, **kwargs) -> subprocess.CompletedProcess:
        self.last_args = args
        self.last_kwargs = kwargs
        return subprocess.CompletedProcess(
            args=args[0] if args else kwargs.get("args", []),
            returncode=self.returncode,
            stdout=self.stdout,
            stderr=self.stderr,
        )


def test_invoke_skill_runs_claude_with_prompt_and_default_model(
    monkeypatch,
) -> None:
    fake = _FakeRun(stdout="hello")
    monkeypatch.setattr("tests._skill_helpers.subprocess.run", fake)

    result = invoke_skill("/listen /tdd : say hi")

    assert result == SkillResult(stdout="hello", stderr="", returncode=0)
    argv = fake.last_args[0]
    assert argv[0] == "claude"
    assert "-p" in argv
    assert "/listen /tdd : say hi" in argv
    assert "--model" in argv
    assert "haiku" in argv
    assert fake.last_kwargs["timeout"] == 120
    assert fake.last_kwargs["cwd"] == str(PROJECT_ROOT)


def test_invoke_skill_honors_model_and_timeout_overrides(monkeypatch) -> None:
    fake = _FakeRun()
    monkeypatch.setattr("tests._skill_helpers.subprocess.run", fake)

    invoke_skill("prompt", model="opus", timeout=300)

    argv = fake.last_args[0]
    assert "opus" in argv
    assert fake.last_kwargs["timeout"] == 300


def test_invoke_skill_uses_provided_cwd(monkeypatch, tmp_path: Path) -> None:
    fake = _FakeRun()
    monkeypatch.setattr("tests._skill_helpers.subprocess.run", fake)

    invoke_skill("prompt", cwd=tmp_path)

    assert fake.last_kwargs["cwd"] == str(tmp_path)


def test_invoke_skill_returns_timeout_sentinel_on_timeout(monkeypatch) -> None:
    def _raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="claude", timeout=120)

    monkeypatch.setattr("tests._skill_helpers.subprocess.run", _raise_timeout)

    result = invoke_skill("prompt")

    assert result == SkillResult(stdout="", stderr="TIMEOUT", returncode=-1)


@pytest.mark.skipif(
    os.environ.get("PYTEST_XDIST_WORKER") is not None,
    reason="Fixture only yields None when not running under xdist",
)
def test_worker_worktree_yields_none_outside_xdist(
    worker_worktree,
) -> None:
    assert worker_worktree is None
