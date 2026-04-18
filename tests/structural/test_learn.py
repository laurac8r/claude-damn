"""Structural regression tests: /learn skill file existence and metadata."""

from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_PATH = PROJECT_ROOT / "skills" / "learn" / "SKILL.md"


def _parse_frontmatter(path: Path) -> dict:
    """Extract YAML frontmatter from a SKILL.md file."""
    text = path.read_text()
    parts = text.split("---", 2)
    assert len(parts) >= 3, "SKILL.md must have --- delimited frontmatter"
    return yaml.safe_load(parts[1])


class TestSkillFileExists:
    def test_learn_skill_exists(self) -> None:
        assert SKILL_PATH.exists(), f"Expected skill at {SKILL_PATH}"


class TestFrontmatter:
    @pytest.fixture(scope="class")
    def frontmatter(self) -> dict:
        return _parse_frontmatter(SKILL_PATH)

    @pytest.mark.parametrize(
        "key,expected",
        [
            ("name", "learn"),
            ("description", None),
            ("user-invocable", True),
        ],
    )
    def test_frontmatter_key(
        self, frontmatter: dict, key: str, expected: object
    ) -> None:
        assert key in frontmatter, f"Missing frontmatter key: {key!r}"
        if expected is not None:
            assert frontmatter[key] == expected

    def test_description_starts_with_use_when(self, frontmatter: dict) -> None:
        desc = frontmatter["description"]
        assert isinstance(desc, str)
        assert desc.strip().lower().startswith("use when"), (
            "description must start with 'Use when' per writing-skills guidance"
        )
