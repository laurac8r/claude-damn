from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from tests._skill_helpers import SKILLS_ROOT

SKILL_ROOT = SKILLS_ROOT / "expert-review"


@pytest.fixture(scope="module")
def skill_root() -> Path:
    return SKILL_ROOT


@pytest.fixture(scope="module")
def skill_md(skill_root: Path) -> str:
    path = skill_root / "SKILL.md"
    assert path.exists(), f"SKILL.md not found at {path}"
    return path.read_text()


@pytest.fixture(scope="module")
def frontmatter(skill_md: str) -> dict:
    return parse_frontmatter(skill_md)


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from a markdown file."""
    if not content.startswith("---"):
        raise ValueError("No YAML frontmatter found (file must start with ---)")
    end = content.index("---", 3)
    return yaml.safe_load(content[3:end])


def extract_sections(content: str) -> list[str]:
    """Extract all ## and ### heading texts from markdown content."""
    return re.findall(r"^#{2,3}\s+(.+)$", content, re.MULTILINE)
