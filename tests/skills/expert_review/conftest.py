from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

SKILL_ROOT = (
    Path(__file__).resolve().parent.parent.parent.parent / "skills" / "expert-review"
)


@pytest.fixture
def skill_root() -> Path:
    return SKILL_ROOT


@pytest.fixture
def skill_md(skill_root: Path) -> str:
    path = skill_root / "SKILL.md"
    assert path.exists(), f"SKILL.md not found at {path}"
    return path.read_text()


@pytest.fixture
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
