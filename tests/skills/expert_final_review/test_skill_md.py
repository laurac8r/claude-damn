"""Structural tests for skills/expert-final-review/SKILL.md."""

from __future__ import annotations

from pathlib import Path


class TestSkillMdExists:
    def test_skill_md_file_exists(self, skill_root: Path) -> None:
        assert (skill_root / "SKILL.md").exists()

    def test_skill_md_is_non_empty(self, skill_md: str) -> None:
        assert len(skill_md.strip()) > 0


class TestSkillMdFrontmatter:
    def test_name_matches_dir(self, frontmatter: dict) -> None:
        assert frontmatter["name"] == "expert-final-review"

    def test_is_user_invocable(self, frontmatter: dict) -> None:
        assert frontmatter.get("user-invocable") is True

    def test_has_description(self, frontmatter: dict) -> None:
        assert "description" in frontmatter
        assert len(frontmatter["description"]) > 20


class TestSkillMdComposedSkillReferences:
    def test_references_fast_pr_final_self_review(self, skill_md: str) -> None:
        assert "/fast-pr-final-self-review" in skill_md

    def test_references_expert_review(self, skill_md: str) -> None:
        assert "/expert-review" in skill_md
