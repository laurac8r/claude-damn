"""Shared helpers for skill-invocation tests.

Plain module (not a fixture) so smoke, performance, and any other test
subdirectory can import without re-declaring the dataclass or the subprocess
shape. Import as: ``from tests._skill_helpers import invoke_skill, SkillResult``.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class SkillResult:
    """Captured output from a Claude Code skill invocation."""

    stdout: str
    stderr: str
    returncode: int


def invoke_skill(
    prompt: str,
    model: str = "haiku",
    timeout: int = 120,
    cwd: Path | None = None,
) -> SkillResult:
    """Run ``claude -p <prompt> --model <model>`` and capture the result.

    ``cwd`` defaults to the repository root; callers (notably the xdist
    ``worker_worktree`` fixture) may pass an ephemeral worktree path to
    isolate concurrent invocations from shared ``.claude/`` state.
    """
    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--model", model],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd) if cwd is not None else str(PROJECT_ROOT),
        )
    except subprocess.TimeoutExpired:
        return SkillResult(stdout="", stderr="TIMEOUT", returncode=-1)
    return SkillResult(
        stdout=result.stdout,
        stderr=result.stderr,
        returncode=result.returncode,
    )
