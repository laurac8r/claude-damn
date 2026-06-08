"""Shared fixtures for /atlas tests — mirrors tests/skills/tesseract/conftest.py."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

SKILL_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "skills" / "atlas"


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


@pytest.fixture
def git_sandbox(tmp_path: Path, request: pytest.FixtureRequest) -> Path:
    """Labeled subdirectory of ``tmp_path`` for tests that init a real git repo.

    Returns a freshly-created directory at
    ``<tmp_path>/atlas-git-sandbox-<test-name>``. Putting the spurious
    ``.git`` under a labeled subdir (rather than bare ``tmp_path``) makes
    the artifacts recognizable in ``/tmp`` listings — operator preference.
    """
    sandbox = tmp_path / f"atlas-git-sandbox-{request.node.name}"
    sandbox.mkdir()
    return sandbox
