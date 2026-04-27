"""Unit tests for skills/_shared/anchor.py."""

from __future__ import annotations

import subprocess
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from skills._shared.anchor import Anchor, AnchorSource, resolve_anchor


def test_anchor_source_enum_has_four_rungs() -> None:
    assert len(AnchorSource) == 4
    assert AnchorSource.MODIFIED_FILE.value == "modified-file"
    assert AnchorSource.BRANCH.value == "branch"
    assert AnchorSource.MEMORY.value == "memory"
    assert AnchorSource.UNRESOLVED.value == "unresolved"


def test_anchor_dataclass_is_frozen() -> None:
    a = Anchor(slug="feat-x", source=AnchorSource.BRANCH)
    with pytest.raises(FrozenInstanceError):
        a.slug = "changed"  # type: ignore[misc]


def test_anchor_equality_by_value() -> None:
    a = Anchor(slug="x", source=AnchorSource.BRANCH)
    b = Anchor(slug="x", source=AnchorSource.BRANCH)
    assert a == b


def _init_git_repo(path: Path) -> None:
    subprocess.run(
        ["git", "init", "-b", "main"], cwd=path, check=True, capture_output=True
    )
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=path, check=True)


def test_resolve_anchor_override_short_circuits(git_sandbox: Path) -> None:
    anchor, warnings = resolve_anchor(git_sandbox, override="My Custom Anchor")
    assert anchor.slug == "my-custom-anchor"
    # override is treated as explicit pin
    assert anchor.source == AnchorSource.MODIFIED_FILE
    assert warnings == []


def test_resolve_anchor_modified_file_wins(git_sandbox: Path) -> None:
    _init_git_repo(git_sandbox)
    (git_sandbox / "src.py").write_text("# stub\n")
    subprocess.run(["git", "add", "src.py"], cwd=git_sandbox, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=git_sandbox,
        check=True,
        capture_output=True,
    )
    (git_sandbox / "src.py").write_text("# changed\n")  # now modified
    anchor, warnings = resolve_anchor(git_sandbox)
    assert anchor.slug == "src-py"
    assert anchor.source == AnchorSource.MODIFIED_FILE
    assert warnings == []


def test_resolve_anchor_branch_when_no_modified_files(git_sandbox: Path) -> None:
    _init_git_repo(git_sandbox)
    (git_sandbox / "x.txt").write_text("x")
    subprocess.run(["git", "add", "x.txt"], cwd=git_sandbox, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=git_sandbox,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "checkout", "-b", "feat/foo-bar"],
        cwd=git_sandbox,
        check=True,
        capture_output=True,
    )
    anchor, warnings = resolve_anchor(git_sandbox)
    assert anchor.slug == "feat-foo-bar"
    assert anchor.source == AnchorSource.BRANCH
    assert warnings == []


def test_resolve_anchor_unresolved_when_nothing_matches(git_sandbox: Path) -> None:
    # git_sandbox has no .git, no modified files, and we point memory_dir at empty
    anchor, warnings = resolve_anchor(
        git_sandbox, memory_dir=git_sandbox / "no-such-dir"
    )
    assert anchor.slug == "void"
    assert anchor.source == AnchorSource.UNRESOLVED
    assert warnings  # at least one warning string
    assert any("no anchor source" in w.lower() for w in warnings)


def test_resolve_anchor_modified_file_uses_basename_only(git_sandbox: Path) -> None:
    """Spec §5.2: slugify the basename of the modified file, not its full path."""
    _init_git_repo(git_sandbox)
    nested = git_sandbox / "src" / "deep"
    nested.mkdir(parents=True)
    (nested / "Button.tsx").write_text("// stub\n")
    subprocess.run(["git", "add", "src/deep/Button.tsx"], cwd=git_sandbox, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=git_sandbox,
        check=True,
        capture_output=True,
    )
    (nested / "Button.tsx").write_text("// changed\n")  # modified
    anchor, warnings = resolve_anchor(git_sandbox)
    # basename "Button.tsx" → "button-tsx", NOT "src-deep-button-tsx"
    assert anchor.slug == "button-tsx"
    assert anchor.source == AnchorSource.MODIFIED_FILE
    assert warnings == []
