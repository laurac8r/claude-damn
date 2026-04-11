"""Structural regression tests: /listen skill file existence and metadata."""

from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_PATH = PROJECT_ROOT / "skills" / "listen" / "SKILL.md"
OLD_SKILL_PATH = PROJECT_ROOT / "skills" / "enforce" / "SKILL.md"


def _parse_frontmatter(path: Path) -> dict:
    """Extract YAML frontmatter from a SKILL.md file."""
    text = path.read_text()
    parts = text.split("---", 2)
    assert len(parts) >= 3, "SKILL.md must have --- delimited frontmatter"
    return yaml.safe_load(parts[1])


class TestSkillFileExists:
    """Verify the skill file is at the correct path."""

    def test_listen_skill_exists(self) -> None:
        assert SKILL_PATH.exists(), f"Expected skill at {SKILL_PATH}"

    def test_enforce_skill_removed(self) -> None:
        assert not OLD_SKILL_PATH.exists(), f"Old skill should not exist at {OLD_SKILL_PATH}"


class TestFrontmatter:
    """Verify frontmatter has required fields with correct values."""

    @pytest.fixture(scope="class")
    def frontmatter(self) -> dict:
        return _parse_frontmatter(SKILL_PATH)

    def test_has_name(self, frontmatter: dict) -> None:
        assert "name" in frontmatter

    def test_name_is_listen(self, frontmatter: dict) -> None:
        assert frontmatter["name"] == "listen"

    def test_has_description(self, frontmatter: dict) -> None:
        assert "description" in frontmatter

    def test_has_argument_hint(self, frontmatter: dict) -> None:
        assert "argument-hint" in frontmatter

    def test_has_user_invocable(self, frontmatter: dict) -> None:
        assert "user-invocable" in frontmatter

    def test_user_invocable_is_true(self, frontmatter: dict) -> None:
        assert frontmatter["user-invocable"] is True

    def test_frontmatter_parses_without_error(self) -> None:
        fm = _parse_frontmatter(SKILL_PATH)
        assert isinstance(fm, dict)
