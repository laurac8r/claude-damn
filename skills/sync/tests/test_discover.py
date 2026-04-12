import subprocess
from pathlib import Path

import pytest

from skills.sync.scripts.claude_allowlist import (
    BUILTIN_ALLOW,
    BUILTIN_DENY,
    ClaudeAllowlist,
)
from skills.sync.scripts.discover import DiscoverOptions, discover


@pytest.fixture
def src(tmp_path: Path) -> Path:
    root = tmp_path / "src"
    root.mkdir()
    subprocess.run(
        ["git", "init", "-q", str(root)], check=True, capture_output=True, text=True
    )
    (root / ".gitignore").write_text(".claude\nbuild/\n")
    (root / "a.py").write_text("a")
    (root / "b.py").write_text("b")
    (root / "CLAUDE.md").write_text("c")
    (root / "build").mkdir()
    (root / "build" / "o.o").write_text("o")
    (root / ".claude").mkdir()
    (root / ".claude" / "settings.json").write_text("{}")
    (root / ".claude" / "projects").mkdir()
    (root / ".claude" / "projects" / "p.json").write_text("{}")
    return root


def test_default_respects_gitignore(src: Path) -> None:
    opts = DiscoverOptions()
    paths = set(discover(src, opts))
    assert Path("a.py") in paths
    assert Path("b.py") in paths
    assert Path("CLAUDE.md") in paths
    assert Path("build/o.o") not in paths
    assert Path(".claude/settings.json") not in paths


def test_no_gitignore_includes_everything_except_dotgit(src: Path) -> None:
    opts = DiscoverOptions(respect_gitignore=False)
    paths = set(discover(src, opts))
    assert Path("build/o.o") in paths
    assert Path(".claude/settings.json") in paths
    assert not any(str(p).startswith(".git/") for p in paths)


def test_exclude_glob_drops_matching(src: Path) -> None:
    opts = DiscoverOptions(exclude=("*.py",))
    paths = set(discover(src, opts))
    assert Path("a.py") not in paths
    assert Path("CLAUDE.md") in paths


def test_include_glob_restricts_to_matching(src: Path) -> None:
    opts = DiscoverOptions(include=("*.py",))
    paths = set(discover(src, opts))
    assert paths == {Path("a.py"), Path("b.py")}


def test_claude_allowlist_overrides_gitignore(src: Path) -> None:
    opts = DiscoverOptions(
        claude_allowlist=ClaudeAllowlist(allow=BUILTIN_ALLOW, deny=BUILTIN_DENY),
    )
    paths = set(discover(src, opts))
    assert Path(".claude/settings.json") in paths
    assert Path(".claude/projects/p.json") not in paths
    assert Path("build/o.o") not in paths
