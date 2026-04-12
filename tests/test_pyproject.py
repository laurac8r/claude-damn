"""Regression tests: pyproject.toml dependency placement."""

import tomllib
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def pyproject() -> dict:
    with open(PROJECT_ROOT / "pyproject.toml", "rb") as f:
        return tomllib.load(f)


@pytest.fixture(scope="module")
def runtime_deps(pyproject: dict) -> list[str]:
    return pyproject.get("project", {}).get("dependencies", [])


@pytest.fixture(scope="module")
def dev_deps(pyproject: dict) -> list[str]:
    return pyproject.get("dependency-groups", {}).get("dev", [])


class TestRuntimeDependencies:
    """Test-only packages must not appear in runtime dependencies."""

    @pytest.mark.parametrize("package", ["pytest", "pyyaml"])
    def test_test_package_not_in_runtime_deps(
        self, package: str, runtime_deps: list[str]
    ) -> None:
        matches = [dep for dep in runtime_deps if dep.lower().startswith(package)]
        assert matches == [], (
            f"{package!r} must not appear in [project.dependencies]; found: {matches}"
        )


class TestDevDependencies:
    """All dev/test packages must live in [dependency-groups.dev]."""

    @pytest.mark.parametrize(
        "package",
        ["pytest", "pyyaml", "pytest-xdist", "ruff"],
    )
    def test_dev_package_in_dev_group(self, package: str, dev_deps: list[str]) -> None:
        normalised = [
            dep.lower().replace("-", "").replace("_", "").split(">")[0].split("=")[0]
            for dep in dev_deps
        ]
        needle = package.lower().replace("-", "").replace("_", "")
        assert needle in normalised, (
            f"{package!r} must appear in [dependency-groups.dev]; "
            f"current dev deps: {dev_deps}"
        )
