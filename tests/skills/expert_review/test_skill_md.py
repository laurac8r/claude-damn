"""Structural tests for skills/expert-review/SKILL.md."""

from __future__ import annotations

import re


class TestExpertReviewSkillMd:
    """Verify expert-review SKILL.md structural invariants."""

    def test_no_duplicate_combine_roles_bullet(self, skill_md: str) -> None:
        """'You combine the roles of' should appear exactly once."""
        count = skill_md.count("You combine the roles of")
        assert count == 1, f"Expected 1 occurrence, found {count}"

    def test_phase0_sequential_numbering(self, skill_md: str) -> None:
        """Phase 0 steps should be numbered sequentially (1, 2, 3...)."""
        phase0_match = re.search(
            r"## Phase 0.*?(?=## Phase [1-9])", skill_md, re.DOTALL
        )
        assert phase0_match, "Phase 0 section not found"
        phase0 = phase0_match.group()
        # Find top-level numbered items (lines starting with digit+period)
        numbers = re.findall(r"^(\d+)\.\s", phase0, re.MULTILINE)
        numbers = [int(n) for n in numbers]
        expected = list(range(1, len(numbers) + 1))
        assert numbers == expected, (
            f"Expected sequential {expected}, got {numbers}"
        )
