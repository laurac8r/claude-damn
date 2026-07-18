from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tests._skill_helpers import SKILLS_ROOT

SKILL_ROOT = SKILLS_ROOT / "tdd-cat"


@pytest.fixture(scope="module")
def skill_root() -> Path:
    return SKILL_ROOT


@pytest.fixture(scope="module")
def skill_md(skill_root: Path) -> str:
    path = skill_root / "SKILL.md"
    assert path.exists(), f"SKILL.md not found at {path}"
    return path.read_text()


@pytest.fixture(scope="module")
def skill_body(skill_md: str) -> str:
    """Markdown body with the YAML frontmatter stripped.

    Bare-invocation checks must target the body (the dispatch instructions),
    not the frontmatter ``description`` prose — a backticked-everywhere body
    stops actually loading the composed skills (the /tdd 1.11.1 regression).
    """
    end = skill_md.index("---", 3)
    return skill_md[end + 3 :]


@pytest.fixture(scope="module")
def frontmatter(skill_md: str) -> dict:
    return parse_frontmatter(skill_md)


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from a markdown file."""
    if not content.startswith("---"):
        raise ValueError("No YAML frontmatter found (file must start with ---)")
    end = content.index("---", 3)
    return yaml.safe_load(content[3:end])
