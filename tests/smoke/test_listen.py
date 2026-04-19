"""Smoke tests: invoke /listen skill via claude -p and verify behavior.

These tests are non-deterministic. A 90% pass rate is the quality gate.
They cost real API tokens — keep instructions minimal, use haiku model.
"""

import pytest

pytestmark = pytest.mark.smoke


class TestSingleSkillReference:
    """Given instructions with one skill reference, /listen should invoke it."""

    def test_invokes_referenced_skill(self, invoke_skill) -> None:
        result = invoke_skill(
            "/listen /tdd : list the 3 core steps of TDD in a numbered list, nothing else"
        )
        assert result.returncode == 0, (
            f"claude exited non-zero: {result.returncode}\nstderr: {result.stderr[:500]}"
        )
        output = result.stdout.lower()
        assert any(
            phrase in output
            for phrase in [
                "red",
                "green",
                "refactor",
                "failing test",
                "test-driven",
                "tdd",
            ]
        ), f"Expected TDD-related output, got:\n{result.stdout[:500]}"


class TestNoSkillReference:
    """Given instructions with no skill references, /listen should execute normally."""

    def test_executes_without_enforcement(self, invoke_skill) -> None:
        result = invoke_skill('/listen say exactly "HELLO_SMOKE_TEST" and nothing else')
        assert result.returncode == 0, (
            f"claude exited non-zero: {result.returncode}\nstderr: {result.stderr[:500]}"
        )
        assert (
            "HELLO_SMOKE_TEST" in result.stdout
        ), f"Expected literal output, got:\n{result.stdout[:500]}"


class TestCompositionalSkillReference:
    """Given a compositional skill reference, /listen should invoke it as a unit."""

    def test_invokes_compositional_skill_directly(self, invoke_skill) -> None:
        result = invoke_skill(
            "/listen /super-duper-cat : describe what skills you just loaded, as a bullet list"
        )
        assert result.returncode == 0, (
            f"claude exited non-zero: {result.returncode}\nstderr: {result.stderr[:500]}"
        )
        output = result.stdout.lower()
        assert any(
            phrase in output
            for phrase in [
                "brainstorm",
                "worktree",
                "subagent",
                "super-duper-cat",
                "tdd",
            ]
        ), f"Expected compositional skill evidence, got:\n{result.stdout[:500]}"


class TestMultipleSkillReferences:
    """Given instructions with multiple skill references, all should be invoked."""

    def test_invokes_all_referenced_skills(self, invoke_skill) -> None:
        result = invoke_skill(
            "/listen /tdd /review : list which skills you were asked to invoke, nothing else"
        )
        assert result.returncode == 0, (
            f"claude exited non-zero: {result.returncode}\nstderr: {result.stderr[:500]}"
        )
        output = result.stdout.lower()
        assert "tdd" in output, f"Expected tdd mention, got:\n{result.stdout[:500]}"
        assert (
            "review" in output
        ), f"Expected review mention, got:\n{result.stdout[:500]}"
