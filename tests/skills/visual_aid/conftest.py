from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tests._skill_helpers import SKILLS_ROOT

SKILL_ROOT = SKILLS_ROOT / "visual-aid"


@pytest.fixture(scope="module")
def skill_root() -> Path:
    return SKILL_ROOT


@pytest.fixture(scope="module")
def skill_md(skill_root: Path) -> str:
    path = skill_root / "SKILL.md"
    assert path.exists(), f"SKILL.md not found at {path}"
    return path.read_text()


@pytest.fixture(scope="module")
def frontmatter(skill_md: str) -> dict[str, object]:
    if not skill_md.startswith("---"):
        raise ValueError("No YAML frontmatter found (file must start with ---)")
    end = skill_md.index("---", 3)
    return yaml.safe_load(skill_md[3:end])


@pytest.fixture(scope="module")
def baseline_html_path(skill_root: Path) -> Path:
    return skill_root / "baseline.html"


@pytest.fixture(scope="module")
def baseline_html(baseline_html_path: Path) -> str:
    assert baseline_html_path.exists(), (
        f"baseline.html not found at {baseline_html_path}"
    )
    return baseline_html_path.read_text()
