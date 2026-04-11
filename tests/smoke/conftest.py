"""Shared fixtures for smoke tests that invoke Claude Code skills."""

import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass
class SkillResult:
    """Captured output from a Claude Code skill invocation."""

    stdout: str
    stderr: str
    returncode: int


@pytest.fixture(scope="module")
def invoke_skill():
    """Factory fixture: invoke a skill via claude -p and return captured output."""

    def _invoke(prompt: str, timeout: int = 120) -> SkillResult:
        result = subprocess.run(
            ["claude", "-p", prompt, "--model", "haiku"],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(PROJECT_ROOT),
        )
        return SkillResult(
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
        )

    return _invoke
