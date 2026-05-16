"""Pressure tests for skills/add-to-roadmap/SKILL.md.

Verifies that the skill addresses adversarial and edge-case scenarios with
named guidance: missing ROADMAP.md, ambiguous fuzzy match, zero-match,
malformed args, and nested-section name collisions.
"""

from __future__ import annotations

import re


class TestAddToRoadmapPressure:
    """Adversarial-scenario coverage for skills/add-to-roadmap/SKILL.md."""

    def test_missing_roadmap_error_path_documented(self, skill_md: str) -> None:
        """Skill must document the error path when ROADMAP.md is not found
        after walking up to the repo root.
        """
        assert re.search(
            r"not found|no ROADMAP|cannot find|missing.*ROADMAP|ROADMAP.*not",
            skill_md,
            re.IGNORECASE,
        ), "Missing-ROADMAP.md error path must be explicitly named."

    def test_ambiguous_fuzzy_match_disambiguation_documented(
        self, skill_md: str
    ) -> None:
        """Skill must document that multiple matches require a disambiguation
        listing (not silent first-match or silent failure).
        """
        assert re.search(
            r"disambiguation|ambiguous|multiple match|more than one match",
            skill_md,
            re.IGNORECASE,
        ), "Ambiguous-match disambiguation requirement must be documented."

    def test_disambiguation_lists_matches(self, skill_md: str) -> None:
        """The disambiguation response must list the matching headers, not
        just say 'ambiguous'.
        """
        assert re.search(
            r"list.*match|matches.*list|listing.*match|show.*match",
            skill_md,
            re.IGNORECASE,
        ), (
            "Disambiguation must specify that matching headers are listed for "
            "the operator."
        )

    def test_zero_match_error_path_documented(self, skill_md: str) -> None:
        """Skill must document the error path when no headers match the
        fuzzy input.
        """
        assert re.search(
            r"zero match|no match|not found.*header|no.*section.*match|"
            r"0 match|no headers",
            skill_md,
            re.IGNORECASE,
        ), "Zero-match error path must be explicitly named."

    def test_malformed_args_missing_separator_documented(self, skill_md: str) -> None:
        """Skill must document behavior when the '::' separator is absent."""
        assert re.search(
            r"::|separator.*missing|missing.*separator|without.*::|no.*::",
            skill_md,
            re.IGNORECASE,
        ), "Malformed-args (missing '::' separator) error path must be documented."

    def test_nested_section_collision_precedence_documented(
        self, skill_md: str
    ) -> None:
        """Skill must document a deterministic precedence rule for the case
        where a Phase header contains a Subsection header's name as a
        substring (nested-section name collision).
        """
        assert re.search(
            r"collision|nested.*section|section.*collision|precedence|"
            r"substring.*header|header.*substring",
            skill_md,
            re.IGNORECASE,
        ), "Nested-section name collision and precedence rule must be documented."

    def test_confirmation_required_before_write(self, skill_md: str) -> None:
        """Skill must document the requirement for operator confirmation
        (unified diff shown before writing) when invoked interactively.
        """
        assert re.search(
            r"confirm|diff.*before|before.*writ|unified diff|operator.*confirm",
            skill_md,
            re.IGNORECASE,
        ), "Unified diff + operator confirmation before writing must be documented."
