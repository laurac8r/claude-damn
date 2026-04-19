"""Shared fixtures for performance matrix tests."""

import pytest

from tests._skill_helpers import SkillResult
from tests._skill_helpers import invoke_skill as _invoke_skill


@pytest.fixture
def invoke_skill(worker_worktree):
    def _invoke(prompt: str, model: str = "haiku", timeout: int = 180) -> SkillResult:
        return _invoke_skill(prompt, model=model, timeout=timeout, cwd=worker_worktree)

    return _invoke
