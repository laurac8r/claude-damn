"""Structural regression tests: /listen skill file existence and metadata."""

from pathlib import Path

import pytest
import yaml

from tests._skill_helpers import PROJECT_ROOT

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
        assert not OLD_SKILL_PATH.exists(), (
            f"Old skill should not exist at {OLD_SKILL_PATH}"
        )


class TestFrontmatter:
    """Verify frontmatter has required fields with correct values."""

    @pytest.fixture(scope="class")
    def frontmatter(self) -> dict:
        return _parse_frontmatter(SKILL_PATH)

    @pytest.mark.parametrize(
        "key,expected",
        [
            ("name", "listen"),
            ("description", None),
            ("argument-hint", None),
            ("user-invocable", True),
        ],
    )
    def test_frontmatter_key(
        self, frontmatter: dict, key: str, expected: object
    ) -> None:
        assert key in frontmatter, f"Missing frontmatter key: {key!r}"
        if expected is not None:
            assert frontmatter[key] == expected

    def test_parses_without_error(self) -> None:
        fm = _parse_frontmatter(SKILL_PATH)
        assert isinstance(fm, dict)
