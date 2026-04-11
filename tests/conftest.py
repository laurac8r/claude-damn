"""Shared fixtures for settings.json regression tests."""

import json
from pathlib import Path

import pytest

SETTINGS_PATH = Path(__file__).parent.parent / "settings.json"


@pytest.fixture(scope="session")
def settings() -> dict:
    """Load settings.json once for the entire test session."""
    return json.loads(SETTINGS_PATH.read_text())


@pytest.fixture(scope="session")
def permissions(settings: dict) -> dict:
    """Extract the permissions block."""
    return settings["permissions"]


@pytest.fixture(scope="session")
def allow_list(permissions: dict) -> list[str]:
    return permissions["allow"]


@pytest.fixture(scope="session")
def deny_list(permissions: dict) -> list[str]:
    return permissions["deny"]


@pytest.fixture(scope="session")
def ask_list(permissions: dict) -> list[str]:
    return permissions["ask"]


@pytest.fixture(scope="session")
def enabled_plugins(settings: dict) -> dict[str, bool]:
    return settings["enabledPlugins"]
