from __future__ import annotations

from pathlib import Path

import pytest
import yaml

SKILL_ROOT = (
    Path(__file__).resolve().parent.parent.parent.parent / "skills" / "tesseract"
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
    if not skill_md.startswith("---"):
        raise ValueError("No YAML frontmatter found (file must start with ---)")
    end = skill_md.index("---", 3)
    return yaml.safe_load(skill_md[3:end])
