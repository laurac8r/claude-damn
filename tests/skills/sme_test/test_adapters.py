from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import read_skill_file

CAPABILITIES = ["DETECT", "GENERATE", "RUN", "EXPLAIN"]
ADAPTERS = ["python", "bats"]


class TestAdapterFilesExist:
    @pytest.mark.parametrize("adapter", ADAPTERS)
    def test_adapter_file_exists(self, skill_root: Path, adapter: str) -> None:
        path = skill_root / "adapters" / adapter / "adapter.md"
        assert path.exists(), f"Missing adapter: {path}"


class TestAdapterContract:
    @pytest.fixture(params=ADAPTERS)
    def adapter_content(
        self, skill_root: Path, request: pytest.FixtureRequest
    ) -> tuple[str, str]:
        adapter: str = request.param
        return adapter, read_skill_file(skill_root, f"adapters/{adapter}/adapter.md")

    @pytest.mark.parametrize("capability", CAPABILITIES)
    def test_adapter_has_capability(
        self, adapter_content: tuple[str, str], capability: str
    ) -> None:
        adapter, content = adapter_content
        assert capability in content, (
            f"Adapter '{adapter}' missing capability '{capability}'"
        )


class TestPythonAdapter:
    @pytest.fixture
    def content(self, skill_root: Path) -> str:
        return read_skill_file(skill_root, "adapters/python/adapter.md")

    def test_references_pytest(self, content: str) -> None:
        assert "pytest" in content.lower()

    def test_detect_lists_project_files(self, content: str) -> None:
        lower = content.lower()
        assert (
            "pyproject.toml" in lower or "setup.py" in lower or "requirements" in lower
        )

    def test_generate_uses_parametrize(self, content: str) -> None:
        assert "parametrize" in content.lower()

    def test_generate_uses_fixtures(self, content: str) -> None:
        assert "fixture" in content.lower()

    def test_run_has_command(self, content: str) -> None:
        lower = content.lower()
        assert "uv run pytest" in lower or "pytest" in lower

    def test_explain_covers_patterns(self, content: str) -> None:
        lower = content.lower()
        assert "assert" in lower


class TestBatsAdapter:
    @pytest.fixture
    def content(self, skill_root: Path) -> str:
        return read_skill_file(skill_root, "adapters/bats/adapter.md")

    def test_references_bats(self, content: str) -> None:
        assert "bats" in content.lower()

    def test_documents_parametrize_limitation(self, content: str) -> None:
        lower = content.lower()
        assert (
            "parametrize" in lower
            or "parameterize" in lower
            or "n discrete" in lower
            or "multiple @test" in lower
        )

    def test_detect_lists_indicators(self, content: str) -> None:
        lower = content.lower()
        assert ".bats" in lower or "shell" in lower or "bash" in lower

    def test_run_has_command(self, content: str) -> None:
        assert "bats" in content.lower()

    def test_uses_test_annotation(self, content: str) -> None:
        assert "@test" in content
