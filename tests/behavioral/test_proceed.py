"""Behavioral tests: /proceed skill structural invariants.

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
SKILL_PATH = PROJECT_ROOT / "skills" / "proceed" / "SKILL.md"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?\n)---\n", re.DOTALL)
REQUIRED_FRONTMATTER_KEYS = ("name", "description")

# Matches phrases like "current approval gate", "only the current gate",
# "single-use approval", "single gate", "current gate only", etc.
SINGLE_GATE_PATTERN = re.compile(
    r"\b(current|only|single)[\w\s,-]{0,30}(gate|approval)\b"
    r"|\b(gate|approval)[\w\s,-]{0,30}(only|single|current)\b",
    re.IGNORECASE,
)


def _parse_frontmatter(content: str) -> dict[str, object]:
    """Extract and parse YAML frontmatter from markdown content."""
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        raise ValueError("No YAML frontmatter found")
    return yaml.safe_load(match.group(1)) or {}


def _extract_body(content: str) -> str:
    """Return the text after the closing frontmatter delimiter."""
    parts = content.split("---", 2)
    if len(parts) < 3:
        return ""
    return parts[2]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def skill_content() -> str:
    """Read the full SKILL.md content once per module."""
    return SKILL_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def body(skill_content: str) -> str:
    """Return only the body (post-frontmatter) section."""
    return _extract_body(skill_content)


@pytest.fixture(scope="module")
def frontmatter(skill_content: str) -> dict[str, object]:
    """Parse the frontmatter once per module."""
    return _parse_frontmatter(skill_content)


# ---------------------------------------------------------------------------
# Invariant 1: Body contains "Aligned and approved"
# ---------------------------------------------------------------------------


class TestAlignedAndApprovedPhrase:
    """Body must contain the exact phrase 'Aligned and approved'."""

    def test_phrase_present_in_real_file(self, body: str) -> None:
        assert "Aligned and approved" in body, (
            "Expected exact phrase 'Aligned and approved' in skill body"
        )

    def test_mutation_without_phrase_fails(self, body: str) -> None:
        """TDD mutation check: removing the phrase should make the assertion fail."""
        mutated = body.replace("Aligned and approved", "Ready to continue")
        assert "Aligned and approved" not in mutated  # mutation is effective


# ---------------------------------------------------------------------------
# Invariant 2: Body references "proceed"
# ---------------------------------------------------------------------------


class TestProceedReference:
    """Body must reference the word 'proceed' (case-insensitive)."""

    def test_proceed_referenced(self, body: str) -> None:
        assert re.search(r"\bproceed\b", body, re.IGNORECASE), (
            "Expected 'proceed' to appear in skill body"
        )

    def test_mutation_without_proceed_fails(self, body: str) -> None:
        """TDD mutation check: removing 'proceed' references should fail the check."""
        mutated = re.sub(r"\bproceed\b", "continue", body, flags=re.IGNORECASE)
        assert not re.search(r"\bproceed\b", mutated, re.IGNORECASE)  # effective


# ---------------------------------------------------------------------------
# Invariant 3: Single-gate scope indicator present
# ---------------------------------------------------------------------------


class TestSingleGateScopeIndicator:
    """Body must indicate the authorization is scoped to the current gate only."""

    def test_single_gate_indicator_present(self, body: str) -> None:
        assert SINGLE_GATE_PATTERN.search(body), (
            "Expected a single-gate scope phrase (e.g. 'current approval gate', "
            "'only the current gate', 'single-use') in skill body"
        )

    def test_mutation_without_gate_language_fails(self, body: str) -> None:
        """TDD mutation: stripping gate/approval language should fail the check."""
        mutated = re.sub(
            r"\b(gate|approval)\b", "permission", body, flags=re.IGNORECASE
        )
        assert not SINGLE_GATE_PATTERN.search(mutated)  # mutation is effective


# ---------------------------------------------------------------------------
# Invariant 4: Frontmatter is valid YAML with required keys
# ---------------------------------------------------------------------------


class TestFrontmatterValidity:
    """SKILL.md frontmatter must be valid YAML and contain required keys."""

    def test_frontmatter_parses(self, frontmatter: dict[str, object]) -> None:
        assert isinstance(frontmatter, dict)

    @pytest.mark.parametrize("key", REQUIRED_FRONTMATTER_KEYS)
    def test_required_key_present(
        self, frontmatter: dict[str, object], key: str
    ) -> None:
        assert key in frontmatter, f"Frontmatter missing required key: {key!r}"

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
