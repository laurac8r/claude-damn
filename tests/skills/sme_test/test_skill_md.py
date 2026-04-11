from __future__ import annotations

from pathlib import Path

import pytest


class TestSkillMdExists:
    def test_skill_md_file_exists(self, skill_root: Path) -> None:
        assert (skill_root / "SKILL.md").exists()


class TestSkillMdFrontmatter:
    def test_name_is_sme_test(self, frontmatter: dict) -> None:
        assert frontmatter["name"] == "sme-test"

    def test_has_description(self, frontmatter: dict) -> None:
        assert "description" in frontmatter
        assert len(frontmatter["description"]) > 20

    def test_is_user_invocable(self, frontmatter: dict) -> None:
        assert frontmatter.get("user-invocable") is True

    def test_has_argument_hint(self, frontmatter: dict) -> None:
        assert "argument-hint" in frontmatter


class TestSkillMdModeDispatch:
    def test_documents_coach_mode(self, skill_md: str) -> None:
        assert "coach" in skill_md.lower()

    def test_documents_expert_flag(self, skill_md: str) -> None:
        assert "--expert" in skill_md
        assert "-x" in skill_md

    def test_documents_auto_flag(self, skill_md: str) -> None:
        assert "--auto" in skill_md
        assert "-xa" in skill_md

    def test_no_auto_yes_flag(self, skill_md: str) -> None:
        assert (
            "--auto --yes" not in skill_md
            or "not a valid flag" in skill_md.lower()
            or "not valid" in skill_md.lower()
            or "refused" in skill_md.lower()
        )


class TestSkillMdStageReferences:
    @pytest.mark.parametrize(
        "stage_file",
        [
            "prompts/coach-dispatch.md",
            "prompts/three-whys.md",
            "prompts/gwt-formulation.md",
            "prompts/test-writer.md",
            "prompts/red-gate.md",
        ],
    )
    def test_references_prompt_file(self, skill_md: str, stage_file: str) -> None:
        assert stage_file in skill_md, f"SKILL.md must reference {stage_file}"


class TestSkillMdSubagents:
    def test_defines_test_coach(self, skill_md: str) -> None:
        assert "test-coach" in skill_md

    def test_defines_test_writer(self, skill_md: str) -> None:
        assert "test-writer" in skill_md

    def test_defines_test_runner(self, skill_md: str) -> None:
        assert "test-runner" in skill_md

    def test_coach_uses_opus(self, skill_md: str) -> None:
        assert "opus" in skill_md.lower()

    def test_writer_uses_sonnet(self, skill_md: str) -> None:
        assert "sonnet" in skill_md.lower()


class TestSkillMdEscapeHatches:
    def test_coach_escape(self, skill_md: str) -> None:
        assert "coach" in skill_md.lower()

    def test_paste_escape(self, skill_md: str) -> None:
        assert "paste" in skill_md.lower()


class TestSkillMdRedGate:
    def test_red_gate_mandatory(self, skill_md: str) -> None:
        content_lower = skill_md.lower()
        assert "red gate" in content_lower or "red-gate" in content_lower
        assert "mandatory" in content_lower or "no override" in content_lower


class TestSkillMdSharedMemory:
    def test_references_shared_memory(self, skill_md: str) -> None:
        assert "shared/" in skill_md or "shared memory" in skill_md.lower()
