"""Smoke tests for skills/add-to-roadmap/SKILL.md.

Verifies the operational recipe is complete enough for Claude to follow
without further guesswork: walk-up rule, fuzzy match rule, insertion rule,
item format, and multi-line wrap rule are all documented with concrete
examples.
"""

from __future__ import annotations

import re


class TestAddToRoadmapSmoke:
    """Operational completeness checks for skills/add-to-roadmap/SKILL.md."""

    def test_walk_up_rule_documented(self, skill_md: str) -> None:
        """The walk-up-from-CWD strategy for locating ROADMAP.md must be
        documented so Claude knows how to find the file.
        """
        assert re.search(
            r"walk.?up|walking.?up|parent director|CWD",
            skill_md,
            re.IGNORECASE,
        ), "Walk-up rule (walking up from CWD to find ROADMAP.md) must be documented."

    def test_git_repo_root_stopping_condition_documented(self, skill_md: str) -> None:
        """Walk-up must stop at the git repo root; this must be documented."""
        assert re.search(
            r"git rev-parse.*show-toplevel|repo root|repository root",
            skill_md,
            re.IGNORECASE,
        ), "Walk-up stopping condition (git repo root) must be documented."

    def test_fuzzy_contains_match_rule_documented(self, skill_md: str) -> None:
        """Fuzzy contains-match rule must be documented: lowercased input
        substring must appear in lowercased header text.
        """
        assert re.search(
            r"contains.?match|substring.*match|fuzzy",
            skill_md,
            re.IGNORECASE,
        ), "Fuzzy contains-match rule must be documented."

    def test_case_insensitive_match_documented(self, skill_md: str) -> None:
        """The match must be explicitly noted as case-insensitive."""
        assert re.search(
            r"case.?insensitive|case.?insensitively",
            skill_md,
            re.IGNORECASE,
        ), "Case-insensitive matching must be explicitly documented."

    def test_concrete_fuzzy_match_example_present(self, skill_md: str) -> None:
        """At least one concrete example of the fuzzy match must appear
        (e.g., showing how 'phase 2' matches '## Phase 2 — Skill hardening').
        """
        assert re.search(
            r"[Pp]hase\s+[0-9]|[Ss]kill hardening|[Mm]easurement",
            skill_md,
        ), (
            "At least one concrete fuzzy-match example using a real-looking "
            "phase/section name is required."
        )

    def test_bottom_of_section_insertion_documented(self, skill_md: str) -> None:
        """Insertion at the bottom of the chosen section's checkbox list must
        be documented.
        """
        assert re.search(
            r"bottom.*section|end.*section|append.*section|last.*item",
            skill_md,
            re.IGNORECASE,
        ), "Bottom-of-section insertion rule must be documented."

    def test_item_format_checkbox_bold_em_dash(self, skill_md: str) -> None:
        r"""Item format '- [ ] **...** — ...' must be documented with a
        concrete example.
        """
        assert re.search(
            r"- \[ \] \*\*",
            skill_md,
        ), r"Item format '- [ ] **...**' must appear in the SKILL.md."
        assert re.search(
            r"\*\* —|\*\*\s+—",
            skill_md,
        ), "Em-dash separator after bold name must be documented."

    def test_multi_line_wrap_6_space_continuation_documented(
        self, skill_md: str
    ) -> None:
        """Multi-line wrap with 6-space continuation indent must be documented."""
        assert re.search(
            r"6.?space|six.?space|continuation indent",
            skill_md,
            re.IGNORECASE,
        ), "6-space continuation indent for multi-line wrap must be documented."

    def test_wrap_column_width_documented(self, skill_md: str) -> None:
        """The 80-character wrap column must be documented."""
        assert re.search(
            r"80.?char|wrap.*80|column.*80",
            skill_md,
            re.IGNORECASE,
        ), "80-character wrap column must be documented."
