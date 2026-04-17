"""Smoke tests: invoke /proceed skill via claude -p and verify behavior.

These tests are non-deterministic. A 90% pass rate is the quality gate.
They cost real API tokens — keep instructions minimal, use haiku model.
"""

import pytest

pytestmark = pytest.mark.smoke


def _assert_claude_succeeded(result) -> None:
    assert result.returncode == 0, (
        f"claude exited non-zero: {result.returncode}\nstderr: {result.stderr[:500]}"
    )


class TestProceedSkillSummary:
    """Invoke /proceed and confirm it describes single-gate approval behavior."""

    def test_describes_approval_concepts(self, invoke_skill) -> None:
        result = invoke_skill(
            "/proceed : summarize in one sentence what this skill does"
        )
        _assert_claude_succeeded(result)
        output = result.stdout.lower()
        assert any(
            phrase in output
            for phrase in ["aligned", "approved", "gate", "proceed", "authorization"]
        ), f"Expected approval-related output, got:\n{result.stdout[:500]}"


class TestProceedSingleGateScope:
    """Invoke /proceed and confirm single-gate scope, not standing approval."""

    def test_not_standing_authorization(self, invoke_skill) -> None:
        import re

        result = invoke_skill(
            "/proceed : is this standing authorization for future gates?"
        )
        _assert_claude_succeeded(result)
        output = result.stdout.lower()

        explicit_negation = re.search(
            r"\b(no|not|never|doesn'?t|does not)\b[^.\n]{0,40}\bstanding\b", output
        )
        current_gate_only = re.search(
            r"\bonly\b[^.\n]{0,40}\b(current|this)\b[^.\n]{0,40}\bgate\b", output
        ) or re.search(
            r"\b(current|this)\b[^.\n]{0,40}\bgate\b[^.\n]{0,40}\bonly\b", output
        )
        single_gate = re.search(r"\bsingle[- ]gate\b", output)

        assert explicit_negation or current_gate_only or single_gate, (
            "Expected explicit negation of standing authorization or a "
            "current-gate-only phrase, got:\n"
            f"{result.stdout[:500]}"
        )


class TestProceedBasicInvocation:
    """Verify /proceed returns a non-empty successful response."""

    def test_returncode_zero_and_nonempty_output(self, invoke_skill) -> None:
        result = invoke_skill("/proceed : confirm you loaded the skill")
        _assert_claude_succeeded(result)
        assert len(result.stdout.strip()) > 0, "Expected non-empty output"
