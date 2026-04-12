"""Shared fixtures for smoke tests that invoke Claude Code skills."""

import pytest

from tests._skill_helpers import SkillResult
from tests._skill_helpers import invoke_skill as _invoke_skill


@pytest.fixture(scope="module")
def invoke_skill():
    """Factory fixture: wraps _skill_helpers.invoke_skill for smoke tests."""

    def _invoke(prompt: str, timeout: int = 120) -> SkillResult:
        return _invoke_skill(prompt, model="haiku", timeout=timeout)

    return _invoke
