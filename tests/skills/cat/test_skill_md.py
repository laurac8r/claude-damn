"""Structural tests for skills/cat/SKILL.md.

Covers the Task #3 rework: /cat as the explicit combination of BOTH superpowers
skills (/subagent-driven-development + /dispatching-parallel-agents), driven by
ONE combined pre-dispatch AskUserQuestion over two axes — execution mode (3
presets) and edit approval (2 modes) — with the "No Shortcut" guard preserved
and extended to manual-approve mode.
"""

from __future__ import annotations

import re
from pathlib import Path


class TestSkillMdExists:
    def test_skill_md_file_exists(self, skill_root: Path) -> None:
        assert (skill_root / "SKILL.md").exists()

    def test_skill_md_is_non_empty(self, skill_md: str) -> None:
        assert len(skill_md.strip()) > 0


class TestSkillMdFrontmatter:
    def test_name_matches_dir(self, frontmatter: dict) -> None:
        assert frontmatter["name"] == "cat"

    def test_is_user_invocable(self, frontmatter: dict) -> None:
        assert frontmatter.get("user-invocable") is True

    def test_has_description(self, frontmatter: dict) -> None:
        assert "description" in frontmatter
        assert len(frontmatter["description"]) > 20


class TestComposedSkillReferences:
    """/cat is the explicit combination of BOTH superpowers source skills."""

    def test_references_subagent_driven_development(self, skill_md: str) -> None:
        assert "/subagent-driven-development" in skill_md

    def test_references_dispatching_parallel_agents(self, skill_md: str) -> None:
        assert "/dispatching-parallel-agents" in skill_md

    def test_sdd_has_bare_invocation_in_body(self, skill_body: str) -> None:
        # Must appear at least once in the body NOT wrapped as inline code,
        # else per skill-invocation-literalness it never actually loads
        # (the /tdd 1.11.1 backtick-everything regression).
        assert re.search(r"(?<!`)/subagent-driven-development\b", skill_body)

    def test_parallel_has_bare_invocation_in_body(self, skill_body: str) -> None:
        assert re.search(r"(?<!`)/dispatching-parallel-agents\b", skill_body)


class TestCombinedPreDispatchQuestion:
    """ONE combined AskUserQuestion: 3 execution presets x 2 edit-approval modes."""

    def test_uses_askuserquestion(self, skill_md: str) -> None:
        assert "AskUserQuestion" in skill_md

    def test_names_all_three_execution_presets(self, skill_md: str) -> None:
        assert "Full parallel" in skill_md
        assert "Hybrid" in skill_md
        assert "Strict sequential" in skill_md

    def test_names_both_edit_approval_modes(self, skill_md: str) -> None:
        assert "Auto-accept" in skill_md
        assert "Manual-approve" in skill_md

    def test_manual_approve_is_foreground(self, skill_md: str) -> None:
        assert "foreground" in skill_md.lower()


class TestNoShortcutReconciliation:
    def test_no_shortcut_section_present(self, skill_md: str) -> None:
        headings = re.findall(r"^#{2,3}\s+(.+)$", skill_md, re.MULTILINE)
        assert any("No Shortcut" in h for h in headings)

    def test_manual_approve_not_license_for_inline(self, skill_md: str) -> None:
        # The rework explicitly extends the guard: manual-approve / foreground
        # is NOT a license for inline main-agent edits.
        assert "not a license for inline" in skill_md.lower()

    def test_combined_question_precedes_no_shortcut(self, skill_md: str) -> None:
        # Pre-dispatch question must come before the anti-shortcut guard.
        q_idx = skill_md.index("AskUserQuestion")
        ns_idx = next(
            m.start()
            for m in re.finditer(r"^#{2,3}\s+.*No Shortcut.*$", skill_md, re.MULTILINE)
        )
        assert q_idx < ns_idx
