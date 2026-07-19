"""Structural tests for the TDD execution-mode axis across the *-tdd-cat family.

Covers the Task #4 rework: /tdd-cat as the canonical home of the A/B TDD
execution-mode axis — Mode A (split-phase: one RED/GREEN/REFACTOR phase per
subagent) vs Mode B (micro-cycle: full /tdd loop inside each subagent) — asked
as a THIRD question in /cat's ONE combined pre-dispatch AskUserQuestion, with a
never-default-silently guard. The other eight compositions reference the axis;
/cat itself stays untouched (it also serves non-TDD compositions).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests._skill_helpers import SKILLS_ROOT

#: The eight non-atomic ``*-tdd-cat`` compositions that inherit the axis from
#: the canonical ``tdd-cat`` definition.
FAMILY_SKILLS = (
    "duper-tdd-cat",
    "super-tdd-cat",
    "super-duper-tdd-cat",
    "super-duper-fixer-tdd-cat",
    "expert-tdd-cat-review",
    "expert-duper-tdd-cat-review",
    "expert-super-tdd-cat-review",
    "expert-super-duper-tdd-cat-review",
)


def read_skill_md(name: str) -> str:
    path = SKILLS_ROOT / name / "SKILL.md"
    assert path.exists(), f"SKILL.md not found at {path}"
    return path.read_text()


def extract_sections(content: str) -> list[str]:
    """Extract all ## and ### heading texts from markdown content."""
    return re.findall(r"^#{2,3}\s+(.+)$", content, re.MULTILINE)


class TestSkillMdExists:
    def test_skill_md_file_exists(self, skill_root: Path) -> None:
        assert (skill_root / "SKILL.md").exists()

    def test_skill_md_is_non_empty(self, skill_md: str) -> None:
        assert len(skill_md.strip()) > 0


class TestSkillMdFrontmatter:
    def test_name_matches_dir(self, frontmatter: dict) -> None:
        assert frontmatter["name"] == "tdd-cat"

    def test_is_user_invocable(self, frontmatter: dict) -> None:
        assert frontmatter.get("user-invocable") is True

    def test_has_description(self, frontmatter: dict) -> None:
        assert "description" in frontmatter
        assert len(frontmatter["description"]) > 20


class TestComposedSkillInvocations:
    """/tdd-cat composes /tdd and /cat via standalone bare invocations."""

    def test_tdd_bare_invocation_in_body(self, skill_body: str) -> None:
        # Standalone invocation line (<=3 spaces indent, no backticks) is what
        # actually loads the composed skill — the /tdd 1.11.1 backtick
        # regression; same rationale as tests/skills/cat.
        assert re.search(r"(?m)^ {0,3}/tdd\s*$", skill_body)

    def test_cat_bare_invocation_in_body(self, skill_body: str) -> None:
        assert re.search(r"(?m)^ {0,3}/cat\s*$", skill_body)


class TestExecutionModeAxis:
    """Canonical A/B axis definition lives in tdd-cat."""

    def test_axis_section_heading(self, skill_md: str) -> None:
        assert any("TDD Execution Mode" in h for h in extract_sections(skill_md))

    def test_defines_mode_a_split_phase(self, skill_md: str) -> None:
        assert "Mode A" in skill_md
        assert "split-phase" in skill_md.lower()

    def test_defines_mode_b_micro_cycle(self, skill_md: str) -> None:
        assert "Mode B" in skill_md
        assert "micro-cycle" in skill_md.lower()

    def test_names_all_three_phases(self, skill_md: str) -> None:
        for phase in ("RED", "GREEN", "REFACTOR"):
            assert phase in skill_md

    def test_third_question_same_call(self, skill_md: str) -> None:
        # The axis rides /cat's ONE combined pre-dispatch question as a third
        # question in the SAME single AskUserQuestion call — not a separate
        # sequential prompt.
        assert "third question" in skill_md.lower()
        assert "AskUserQuestion" in skill_md

    def test_mode_semantics_pairing_in_table(self, skill_md: str) -> None:
        # PR #92 expert-review: independent substring checks let an A<->B
        # swap pass — pin the label->semantics binding in the table rows.
        assert re.search(r"(?m)^\|\s*\*\*A — Split-phase\*\*", skill_md)
        assert re.search(r"(?m)^\|\s*\*\*B — Micro-cycle\*\*", skill_md)

    def test_orthogonality_note(self, skill_md: str) -> None:
        # A/B is orthogonal to /cat's two axes; within one behavior RED must
        # precede GREEN, so phases of the same behavior never parallelize.
        assert "orthogonal" in skill_md.lower()
        assert "within a behavior" in skill_md.lower()


class TestNoShortcutGuard:
    def test_guard_heading_present(self, skill_md: str) -> None:
        headings = extract_sections(skill_md)
        assert any("Never Default" in h or "No Shortcut" in h for h in headings)

    def test_rationalization_table(self, skill_md: str) -> None:
        # House style of /cat and /tdd: an Excuse | Reality counter table.
        assert re.search(r"(?m)^\|\s*Excuse\s*\|\s*Reality", skill_md)

    def test_axis_precedes_guard(self, skill_md: str) -> None:
        axis_idx = next(
            m.start()
            for m in re.finditer(
                r"^#{2,3}\s+.*TDD Execution Mode.*$", skill_md, re.MULTILINE
            )
        )
        guard_idx = next(
            m.start()
            for m in re.finditer(
                r"^#{2,3}\s+.*(Never Default|No Shortcut).*$",
                skill_md,
                re.MULTILINE,
            )
        )
        assert axis_idx < guard_idx


@pytest.mark.parametrize("family_skill", FAMILY_SKILLS)
class TestFamilyReferencesAxis:
    """Each of the eight compositions references the canonical axis."""

    def test_references_axis(self, family_skill: str) -> None:
        assert "tdd execution mode" in read_skill_md(family_skill).lower()

    def test_names_both_modes(self, family_skill: str) -> None:
        content = read_skill_md(family_skill)
        assert "Mode A" in content
        assert "Mode B" in content

    def test_points_to_canonical(self, family_skill: str) -> None:
        assert "tdd-cat" in read_skill_md(family_skill)

    def test_third_question_wording(self, family_skill: str) -> None:
        assert "third question" in read_skill_md(family_skill).lower()

    def test_never_default_wording(self, family_skill: str) -> None:
        assert "never default" in read_skill_md(family_skill).lower()

    def test_mode_semantics_pairing(self, family_skill: str) -> None:
        # Same swap-guard as the canonical table: bind each mode label to
        # its semantics adjacently (\s* tolerates a reflowed line break).
        content = read_skill_md(family_skill)
        assert re.search(r"Mode A\*\*\s*\(split-phase", content)
        assert re.search(r"Mode B\*\*\s*\(micro-cycle", content)

    def test_axis_heading_at_column_zero(self, family_skill: str) -> None:
        # Copilot on PR #92 flagged a leading space before "##". CommonMark
        # still renders <=3 leading spaces as a heading, but the drift breaks
        # heading-anchored tooling and sibling consistency — pin column 0.
        assert re.search(
            r"(?m)^## TDD execution mode \(third axis\)$",
            read_skill_md(family_skill),
        )


class TestCatStaysUntouched:
    """/cat serves non-TDD compositions too — the axis must NOT leak into it."""

    def test_cat_has_no_tdd_axis(self) -> None:
        assert "tdd execution" not in read_skill_md("cat").lower()
