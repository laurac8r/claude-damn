from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import read_skill_file

PROMPT_FILES = [
    "prompts/coach-dispatch.md",
    "prompts/three-whys.md",
    "prompts/gwt-formulation.md",
    "prompts/test-writer.md",
    "prompts/red-gate.md",
]


class TestPromptFilesExist:
    @pytest.mark.parametrize("prompt_file", PROMPT_FILES)
    def test_prompt_file_exists(self, skill_root: Path, prompt_file: str) -> None:
        assert (skill_root / prompt_file).exists(), f"Missing: {prompt_file}"


class TestCoachDispatch:
    @pytest.fixture
    def content(self, skill_root: Path) -> str:
        return read_skill_file(skill_root, "prompts/coach-dispatch.md")

    def test_has_language_detection(self, content: str) -> None:
        lower = content.lower()
        assert "detect" in lower or "language" in lower

    def test_has_adapter_selection(self, content: str) -> None:
        assert "adapter" in content.lower()

    def test_has_target_identification(self, content: str) -> None:
        lower = content.lower()
        assert "target" in lower or "file" in lower or "function" in lower

    def test_has_shared_memory_instructions(self, content: str) -> None:
        assert "shared/" in content or "shared memory" in content.lower()


class TestThreeWhys:
    @pytest.fixture
    def content(self, skill_root: Path) -> str:
        return read_skill_file(skill_root, "prompts/three-whys.md")

    def test_has_three_questions(self, content: str) -> None:
        lower = content.lower()
        assert "why" in lower
        assert "three" in lower or "3" in lower

    def test_has_behavioral_intent(self, content: str) -> None:
        lower = content.lower()
        assert "behavior" in lower or "intent" in lower

    def test_rejects_shallow_answers(self, content: str) -> None:
        lower = content.lower()
        assert (
            "test this function" in lower
            or "shallow" in lower
            or "insufficient" in lower
            or "not sufficient" in lower
            or "probe" in lower
        )


class TestGwtFormulation:
    @pytest.fixture
    def content(self, skill_root: Path) -> str:
        return read_skill_file(skill_root, "prompts/gwt-formulation.md")

    def test_has_given_when_then(self, content: str) -> None:
        assert "Given" in content
        assert "When" in content
        assert "Then" in content

    def test_validates_concrete(self, content: str) -> None:
        assert "concrete" in content.lower()

    def test_validates_testable(self, content: str) -> None:
        assert "testable" in content.lower()

    def test_validates_non_redundant(self, content: str) -> None:
        lower = content.lower()
        assert "redundant" in lower or "non-redundant" in lower


class TestTestWriter:
    @pytest.fixture
    def content(self, skill_root: Path) -> str:
        return read_skill_file(skill_root, "prompts/test-writer.md")

    def test_targets_sonnet(self, content: str) -> None:
        assert "sonnet" in content.lower() or "Sonnet" in content

    def test_references_adapter(self, content: str) -> None:
        assert "adapter" in content.lower()

    def test_generates_test_code(self, content: str) -> None:
        lower = content.lower()
        assert "generate" in lower or "write" in lower
        assert "test" in lower

    def test_writes_to_shared(self, content: str) -> None:
        assert "shared/" in content


class TestRedGate:
    @pytest.fixture
    def content(self, skill_root: Path) -> str:
        return read_skill_file(skill_root, "prompts/red-gate.md")

    def test_tests_must_fail(self, content: str) -> None:
        lower = content.lower()
        assert "fail" in lower
        assert "must" in lower or "mandatory" in lower

    def test_no_override(self, content: str) -> None:
        lower = content.lower()
        assert (
            "no override" in lower or "mandatory" in lower or "non-negotiable" in lower
        )

    def test_handles_false_green(self, content: str) -> None:
        lower = content.lower()
        assert "pass" in lower

    def test_references_error_handler(self, content: str) -> None:
        assert "error" in content.lower()

    def test_writes_to_shared(self, content: str) -> None:
        assert "shared/" in content
