"""Integration regression tests: /proceed skill repo integration."""

import pytest
import yaml

from tests._skill_helpers import SKILLS_ROOT

SKILL_DIR = SKILLS_ROOT / "proceed"
SKILL_PATH = SKILL_DIR / "SKILL.md"


class TestSkillPresence:
    """Verify the skill directory and file exist in the repo."""

    def test_proceed_dir_in_skills(self) -> None:
        skill_dirs = [d.name for d in SKILLS_ROOT.iterdir() if d.is_dir()]
        assert "proceed" in skill_dirs

    def test_proceed_skill_md_exists(self) -> None:
        assert SKILL_PATH.exists(), f"Expected skill file at {SKILL_PATH}"


class TestSkillDirectoryContents:
    """Verify the skill directory contains only the expected file."""

    def test_skill_dir_contains_only_skill_md(self) -> None:
        files = list(SKILL_DIR.iterdir())
        assert len(files) == 1, (
            f"Expected exactly 1 file in {SKILL_DIR}, found: {[f.name for f in files]}"
        )
        assert files[0].name == "SKILL.md"


class TestSkillCompleteness:
    """Verify the skill file is a complete, parseable unit."""

    @pytest.fixture(scope="class")
    def skill_text(self) -> str:
        return SKILL_PATH.read_text()

    def test_skill_has_frontmatter_delimiters(self, skill_text: str) -> None:
        parts = skill_text.split("---", 2)
        assert len(parts) >= 3, "SKILL.md must have --- frontmatter delimiters"

    def test_frontmatter_is_dict(self, skill_text: str) -> None:
        parts = skill_text.split("---", 2)
        frontmatter = yaml.safe_load(parts[1])
        assert isinstance(frontmatter, dict)

    def test_body_is_non_empty(self, skill_text: str) -> None:
        parts = skill_text.split("---", 2)
        body = parts[2].strip()
        assert len(body) > 0, "Body must not be empty"
