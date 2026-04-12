from pathlib import Path

from skills.sync.scripts.claude_allowlist import (
    BUILTIN_ALLOW,
    BUILTIN_DENY,
    ClaudeAllowlist,
    load_claude_allowlist,
)


def test_builtin_allows_cover_expected_paths() -> None:
    assert "CLAUDE.md" in BUILTIN_ALLOW
    assert ".claude/skills/**" in BUILTIN_ALLOW
    assert ".remember/**" in BUILTIN_ALLOW
    assert "docs/superpowers/**" in BUILTIN_ALLOW
    assert ".worktrees/**" in BUILTIN_ALLOW
    assert "worktrees/**" in BUILTIN_ALLOW
    assert ".checkpoints/**" in BUILTIN_ALLOW


def test_builtin_denies_block_ephemeral() -> None:
    assert ".claude/projects/**" in BUILTIN_DENY
    assert ".claude/plugins/**" in BUILTIN_DENY
    assert ".claude/cache/**" in BUILTIN_DENY
    # These should NOT be in deny (moved to allow per spec update)
    assert ".worktrees/**" not in BUILTIN_DENY
    assert "worktrees/**" not in BUILTIN_DENY
    assert ".checkpoints/**" not in BUILTIN_DENY


def test_allow_overrides_deny_for_allowed_paths() -> None:
    al = ClaudeAllowlist(allow=BUILTIN_ALLOW, deny=BUILTIN_DENY)
    assert al.matches(Path("CLAUDE.md")) is True
    assert al.matches(Path(".claude/skills/sync/SKILL.md")) is True
    assert al.matches(Path(".claude/projects/foo.json")) is False
    assert al.matches(Path("src/main.py")) is False


def test_custom_allowlist_replaces_builtin(tmp_path: Path) -> None:
    custom = tmp_path / "sync-allowlist.txt"
    custom.write_text("# a comment\nFOO.md\nbar/**\n\n")
    al = load_claude_allowlist(custom)
    assert al.allow == ("FOO.md", "bar/**")
    assert al.deny == BUILTIN_DENY


def test_missing_custom_file_uses_builtin(tmp_path: Path) -> None:
    al = load_claude_allowlist(tmp_path / "nonexistent.txt")
    assert al.allow == BUILTIN_ALLOW
    assert al.deny == BUILTIN_DENY
