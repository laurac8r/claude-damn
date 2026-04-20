"""Smoke tests: invoke /learn skill via claude -p and verify behavior.

Non-deterministic. 90% pass rate is the quality gate. Real API tokens —
haiku, minimal prompts.
"""

import pytest

pytestmark = pytest.mark.smoke


class TestNoSkillsInSession:
    """With no prior Skill tool-calls in context, /learn should report no
    misfires rather than fabricating them."""

    def test_reports_no_invocations(self, invoke_skill) -> None:
        result = invoke_skill(
            "/learn : one sentence only. if this fresh session has no skill "
            "invocations to analyze, say so literally."
        )
        assert result.returncode == 0, (
            f"claude exited non-zero: {result.returncode}\n"
            f"stderr: {result.stderr[:500]}"
        )
        output = result.stdout.lower()
        assert any(
            phrase in output
            for phrase in [
                "no skill invocations",
                "no misfires",
                "nothing to",
                "no findings",
                "no prior",
            ]
        ), f"Expected empty-session acknowledgement, got:\n{result.stdout[:500]}"


class TestPlaybookVocabulary:
    """/learn should use its taxonomy terms, not generic 'issue/failure' prose."""

    def test_uses_misfire_vocabulary(self, invoke_skill) -> None:
        result = invoke_skill(
            "/learn : in one sentence, name the two classifications the "
            "playbook uses for findings."
        )
        assert result.returncode == 0, (
            f"claude exited non-zero: {result.returncode}\n"
            f"stderr: {result.stderr[:500]}"
        )
        output = result.stdout.lower()
        assert "misfire" in output, (
            f"Expected 'misfire' term, got:\n{result.stdout[:500]}"
        )
        assert "preference" in output, (
            f"Expected 'preference shift' term, got:\n{result.stdout[:500]}"
        )


class TestDelegatesToWritingSkills:
    """/learn should name /writing-skills as the fix-applier, not edit
    skill files directly."""

    def test_names_writing_skills_as_delegate(self, invoke_skill) -> None:
        result = invoke_skill(
            "/learn : in one line, which skill does /learn delegate "
            "approved fixes to?"
        )
        assert result.returncode == 0, (
            f"claude exited non-zero: {result.returncode}\n"
            f"stderr: {result.stderr[:500]}"
        )
        output = result.stdout.lower()
        assert "writing-skills" in output, (
            f"Expected /writing-skills delegation, got:\n{result.stdout[:500]}"
        )