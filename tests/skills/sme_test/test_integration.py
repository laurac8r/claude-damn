"""Cross-file consistency tests for sme-test skill.

Verifies that references between skill files are valid and that
the overall file layout matches the v1 contract.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import extract_sections, read_skill_file

# ---------- v1 file manifest ----------

V1_FILES = [
    "SKILL.md",
    "prompts/coach-dispatch.md",
    "prompts/three-whys.md",
    "prompts/gwt-formulation.md",
    "prompts/test-writer.md",
    "prompts/red-gate.md",
    "adapters/python/adapter.md",
    "adapters/bats/adapter.md",
    "errors/error-handlers.md",
]

PROMPT_FILES = [f for f in V1_FILES if f.startswith("prompts/")]
ADAPTER_FILES = [f for f in V1_FILES if f.startswith("adapters/")]

SUBAGENT_NAMES = ["test-coach", "test-writer", "test-runner"]

SHARED_MEMORY_FILES = ["coach-state", "test-writer-output", "red-gate-result"]

ADAPTER_CAPABILITIES = ["DETECT", "GENERATE", "RUN", "EXPLAIN"]


# ---------- Test classes ----------


class TestFileLayout:
    """All 9 v1 files must exist."""

    @pytest.mark.parametrize("relative_path", V1_FILES)
    def test_v1_file_exists(self, skill_root: Path, relative_path: str) -> None:
        path = skill_root / relative_path
        assert path.exists(), f"Missing v1 file: {relative_path}"


class TestCrossReferences:
    """SKILL.md must reference every file, and every referenced file must exist."""

    @pytest.mark.parametrize("prompt", PROMPT_FILES)
    def test_skill_md_references_prompt(self, skill_md: str, prompt: str) -> None:
        assert prompt in skill_md, f"SKILL.md does not reference {prompt}"

    @pytest.mark.parametrize("adapter", ADAPTER_FILES)
    def test_skill_md_references_adapter(self, skill_md: str, adapter: str) -> None:
        assert adapter in skill_md, f"SKILL.md does not reference {adapter}"

    def test_skill_md_references_error_handlers(self, skill_md: str) -> None:
        assert "errors/error-handlers.md" in skill_md

    @pytest.mark.parametrize("relative_path", V1_FILES[1:])
    def test_referenced_file_exists_on_disk(
        self, skill_root: Path, relative_path: str
    ) -> None:
        path = skill_root / relative_path
        assert path.exists(), f"SKILL.md references {relative_path} but file is missing"


class TestSubagentConsistency:
    """Subagent names must appear in SKILL.md and their respective prompts."""

    @pytest.mark.parametrize("name", SUBAGENT_NAMES)
    def test_subagent_in_skill_md(self, skill_md: str, name: str) -> None:
        assert name in skill_md, f"Subagent '{name}' not referenced in SKILL.md"

    def test_test_coach_in_coach_dispatch(self, skill_root: Path) -> None:
        content = read_skill_file(skill_root, "prompts/coach-dispatch.md")
        assert "test-coach" in content

    def test_test_writer_in_test_writer_prompt(self, skill_root: Path) -> None:
        content = read_skill_file(skill_root, "prompts/test-writer.md")
        assert "test-writer" in content

    def test_test_runner_in_red_gate(self, skill_root: Path) -> None:
        content = read_skill_file(skill_root, "prompts/red-gate.md")
        assert "test-runner" in content


class TestSharedMemoryConsistency:
    """shared/ memory filenames must appear consistently across prompts."""

    def test_coach_state_in_dispatch(self, skill_root: Path) -> None:
        content = read_skill_file(skill_root, "prompts/coach-dispatch.md")
        assert "coach-state" in content

    def test_test_writer_output_in_test_writer(self, skill_root: Path) -> None:
        content = read_skill_file(skill_root, "prompts/test-writer.md")
        assert "test-writer-output" in content

    def test_red_gate_result_in_red_gate(self, skill_root: Path) -> None:
        content = read_skill_file(skill_root, "prompts/red-gate.md")
        assert "red-gate-result" in content

    def test_skill_md_documents_all_shared_files(self, skill_md: str) -> None:
        for name in SHARED_MEMORY_FILES:
            assert name in skill_md, f"shared/ file '{name}' not documented in SKILL.md"


class TestAdapterContractCompleteness:
    """Both adapters must implement all 4 capability sections."""

    @pytest.mark.parametrize("adapter", ADAPTER_FILES)
    @pytest.mark.parametrize("capability", ADAPTER_CAPABILITIES)
    def test_adapter_has_capability_section(
        self, skill_root: Path, adapter: str, capability: str
    ) -> None:
        content = read_skill_file(skill_root, adapter)
        sections = extract_sections(content)
        assert any(capability in s for s in sections), (
            f"{adapter} missing ## {capability} section"
        )
