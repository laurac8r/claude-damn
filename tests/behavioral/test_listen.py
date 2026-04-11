"""Behavioral regression tests: /listen skill enforcement protocol content."""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_PATH = PROJECT_ROOT / "skills" / "listen" / "SKILL.md"


@pytest.fixture(scope="module")
def skill_content() -> str:
    """Read the full SKILL.md content."""
    return SKILL_PATH.read_text()


class TestEnforcementProtocolSteps:
    """Verify all 4 enforcement protocol steps are present."""

    def test_step_scan_instructions(self, skill_content: str) -> None:
        assert "Scan" in skill_content
        assert "/skill-name" in skill_content

    def test_step_build_checklist(self, skill_content: str) -> None:
        assert "Build a checklist" in skill_content

    def test_step_invoke_each_skill(self, skill_content: str) -> None:
        assert "Invoke each skill" in skill_content
        assert "Skill tool" in skill_content

    def test_step_verify_completeness(self, skill_content: str) -> None:
        assert "Verify completeness" in skill_content


class TestEnforcementRules:
    """Verify all 4 enforcement rules are present."""

    def test_compositional_skill_handling(self, skill_content: str) -> None:
        assert "compositional skill" in skill_content
        assert "do not decompose" in skill_content

    def test_no_reference_passthrough(self, skill_content: str) -> None:
        assert "no skill references" in skill_content
        assert "without this enforcement overhead" in skill_content

    def test_failure_reporting(self, skill_content: str) -> None:
        assert "fails or is denied" in skill_content
        assert "note it explicitly" in skill_content

    def test_skill_instruction_delegation(self, skill_content: str) -> None:
        assert "does not override how each skill operates" in skill_content


class TestPlaceholdersAndExamples:
    """Verify argument placeholder and example skill references."""

    def test_arguments_placeholder(self, skill_content: str) -> None:
        assert "$ARGUMENTS" in skill_content

    @pytest.mark.parametrize("example", [
        "/tdd",
        "/brainstorming",
        "/super-duper-cat",
    ])
    def test_example_skill_referenced(self, skill_content: str, example: str) -> None:
        assert example in skill_content
