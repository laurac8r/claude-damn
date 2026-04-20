"""Behavioral tests: /listen skill structural invariants.

Tests assert the CONTRACT (structure) of SKILL.md rather than exact prose,
so harmless prose edits do not cause spurious failures.

TDD approach: each invariant is verified against a local in-memory mutation
that SHOULD fail the assertion, confirming the test is not a vacuous pass.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_PATH = PROJECT_ROOT / "skills" / "listen" / "SKILL.md"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?\n)---\n", re.DOTALL)
REQUIRED_FRONTMATTER_KEYS = ("name", "description")


def _parse_frontmatter(content: str) -> dict[str, object]:
    """Extract and parse YAML frontmatter from markdown content."""
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        raise ValueError("No YAML frontmatter found")
    return yaml.safe_load(match.group(1)) or {}


def _extract_protocol_block(content: str) -> str:
    """Return the text from the '## Enforcement Protocol' heading onwards."""
    idx = content.find("## Enforcement Protocol")
    if idx == -1:
        return ""
    return content[idx:]


def _numbered_steps(block: str) -> list[str]:
    """Return lines matching a numbered-list pattern (e.g. '1. ...')."""
    return re.findall(r"^\d+\.", block, re.MULTILINE)


def _has_slash_token(block: str) -> bool:
    """Return True if the block contains a /skill-name pattern."""
    return bool(re.search(r"/[a-z][a-z0-9-]+", block))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def skill_content() -> str:
    """Read the full SKILL.md content once per module."""
    return SKILL_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def protocol_block(skill_content: str) -> str:
    """Return only the Enforcement Protocol section."""
    return _extract_protocol_block(skill_content)


# ---------------------------------------------------------------------------
# Invariant 1: Enforcement Protocol heading exists
# ---------------------------------------------------------------------------


class TestEnforcementProtocolHeading:
    """The '## Enforcement Protocol' heading must be present."""

    def test_heading_present_in_real_file(self, skill_content: str) -> None:
        assert "## Enforcement Protocol" in skill_content

    def test_mutation_without_heading_fails(self, skill_content: str) -> None:
        """TDD mutation check: removing the heading should make the assertion fail."""
        mutated = skill_content.replace("## Enforcement Protocol", "## Removed Heading")
        assert "## Enforcement Protocol" not in mutated  # mutation is effective


# ---------------------------------------------------------------------------
# Invariant 2: Protocol section has at least 3 numbered steps
# ---------------------------------------------------------------------------


class TestEnforcementProtocolSteps:
    """The protocol section must contain at least 3 numbered steps."""

    def test_at_least_three_steps(self, protocol_block: str) -> None:
        steps = _numbered_steps(protocol_block)
        assert len(steps) >= 3, f"Expected >=3 numbered steps, found {len(steps)}"

    def test_mutation_with_zero_steps_fails(self, skill_content: str) -> None:
        """TDD mutation check: stripping numbered steps should drop count below 3."""
        mutated = re.sub(r"^\d+\.", "-", skill_content, flags=re.MULTILINE)
        block = _extract_protocol_block(mutated)
        steps = _numbered_steps(block)
        assert len(steps) < 3  # mutation is effective


# ---------------------------------------------------------------------------
# Invariant 3: Skill-name token pattern referenced in protocol block
# ---------------------------------------------------------------------------


class TestSlashTokenPattern:
    """The protocol block must contain a /skill-name invocation pattern."""

    def test_slash_token_present(self, protocol_block: str) -> None:
        assert _has_slash_token(protocol_block), (
            "Expected a /skill-name token (regex r'/[a-z][a-z0-9-]+') "
            "in the Enforcement Protocol block"
        )

    def test_mutation_without_slash_tokens_fails(self, skill_content: str) -> None:
        """TDD mutation check: removing slash tokens should fail the invariant."""
        mutated = re.sub(r"/[a-z][a-z0-9-]+", "SKILL_REF", skill_content)
        block = _extract_protocol_block(mutated)
        assert not _has_slash_token(block)  # mutation is effective


# ---------------------------------------------------------------------------
# Invariant 4: Frontmatter is valid YAML with required keys
# ---------------------------------------------------------------------------


class TestFrontmatterValidity:
    """SKILL.md frontmatter must be valid YAML and contain required keys."""

    def test_frontmatter_parses(self, skill_content: str) -> None:
        fm = _parse_frontmatter(skill_content)
        assert isinstance(fm, dict)

    @pytest.mark.parametrize("key", REQUIRED_FRONTMATTER_KEYS)
    def test_required_key_present(self, skill_content: str, key: str) -> None:
        fm = _parse_frontmatter(skill_content)
        assert key in fm, f"Frontmatter missing required key: {key!r}"

    def test_mutation_missing_name_fails(self, skill_content: str) -> None:
        """TDD mutation: stripping 'name:' line should fail the name key check."""
        mutated = re.sub(r"^name:.*\n", "", skill_content, flags=re.MULTILINE)
        fm = _parse_frontmatter(mutated)
        assert "name" not in fm  # mutation is effective

    def test_mutation_missing_description_fails(self, skill_content: str) -> None:
        """TDD mutation: stripping 'description:' line should fail that key check."""
        mutated = re.sub(r"^description:.*\n", "", skill_content, flags=re.MULTILINE)
        fm = _parse_frontmatter(mutated)
        assert "description" not in fm  # mutation is effective
