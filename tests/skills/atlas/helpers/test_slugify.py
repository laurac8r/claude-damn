"""Unit tests for skills/_shared/slugify.py."""

from __future__ import annotations

import pytest

from skills._shared.slugify import slugify


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("src/widgets/Button.tsx", "src-widgets-button-tsx"),
        ("feat/widget-cleanup", "feat-widget-cleanup"),
        ("hooks/block-inline-scripts.py", "hooks-block-inline-scripts-py"),
        ("core-memories", "core-memories"),
        ('"memory-system-redesign"', "memory-system-redesign"),
        ("Already-A-Slug", "already-a-slug"),
        ("   leading and trailing spaces   ", "leading-and-trailing-spaces"),
        ("multiple___underscores", "multiple-underscores"),
        ("CamelCase", "camelcase"),
        ("emoji-🧊-survives-as-dash", "emoji-survives-as-dash"),
    ],
)
def test_slugify_canonical_examples(raw: str, expected: str) -> None:
    assert slugify(raw) == expected


def test_slugify_empty_string_returns_empty() -> None:
    assert slugify("") == ""


def test_slugify_only_separators_returns_empty() -> None:
    assert slugify("///   ___") == ""
