from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import extract_sections, read_skill_file

ERROR_CLASSES = [
    "input",
    "environment",
    "subagent",
    "red-gate",
    "safety-refusal",
]


class TestErrorHandlerExists:
    def test_error_handler_file_exists(self, skill_root: Path) -> None:
        assert (skill_root / "errors" / "error-handlers.md").exists()


class TestErrorClasses:
    @pytest.fixture
    def content(self, skill_root: Path) -> str:
        return read_skill_file(skill_root, "errors/error-handlers.md")

    @pytest.mark.parametrize("error_class", ERROR_CLASSES)
    def test_error_class_documented(self, content: str, error_class: str) -> None:
        assert (
            error_class in content.lower()
        ), f"Error class '{error_class}' not found in error-handlers.md"

    def test_every_error_class_has_recovery_section(self, content: str) -> None:
        """Each error class section must contain a Recovery heading or keyword."""
        lower = content.lower()
        assert (
            "recovery" in lower
            or "recover" in lower
            or "resolution" in lower
            or "fix" in lower
        )

    def test_has_five_error_classes(self, content: str) -> None:
        sections = extract_sections(content)
        error_sections = [
            s for s in sections if any(ec in s.lower() for ec in ERROR_CLASSES)
        ]
        assert len(error_sections) >= 5, (
            f"Expected 5 error class sections, found "
            f"{len(error_sections)}: {error_sections}"
        )
