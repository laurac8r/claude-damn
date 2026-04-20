"""Claude-workflow file/directory allowlist for --claude mode."""

import fnmatch
from dataclasses import dataclass
from pathlib import Path

BUILTIN_ALLOW: tuple[str, ...] = (
    "CLAUDE.md",
    "AGENTS.md",
    "GEMINI.md",
    ".claude/settings.json",
    ".claude/settings.local.json",
    ".claude/skills/**",
    ".claude/commands/**",
    ".claude/hooks/**",
    ".claude/agents/**",
    ".remember/**",
    "CHECKPOINT.md",
    "docs/superpowers/**",
    ".worktrees/**",
    "worktrees/**",
    ".checkpoints/**",
)

BUILTIN_DENY: tuple[str, ...] = (
    ".claude/projects/**",
    ".claude/sessions/**",
    ".claude/shell-snapshots/**",
    ".claude/history.jsonl",
    ".claude/plugins/**",
    ".claude/cache/**",
    ".claude/file-history/**",
    ".claude/paste-cache/**",
    ".claude/ide/**",
    ".claude/telemetry/**",
    ".claude/backups/**",
    ".claude/cost-log/**",
)


@dataclass(frozen=True)
class ClaudeAllowlist:
    """Allow/deny glob lists for the --claude flag."""

    allow: tuple[str, ...]
    deny: tuple[str, ...]

    def matches(self, relative_path: Path) -> bool:
        """Return True if this path should be force-included despite gitignore.

        Deny patterns always win over allow patterns — a file matching both
        is dropped.
        """
        s = str(relative_path)
        if any(fnmatch.fnmatch(s, d) for d in self.deny):
            return False
        return any(fnmatch.fnmatch(s, a) for a in self.allow)


def load_claude_allowlist(custom_file: Path) -> ClaudeAllowlist:
    """Load the allowlist. If `custom_file` exists, it replaces the allow list.

    Deny list is always the built-in — users cannot weaken the ephemeral-state
    protection through their custom file.
    """
    if not custom_file.exists():
        return ClaudeAllowlist(allow=BUILTIN_ALLOW, deny=BUILTIN_DENY)
    allow: list[str] = []
    for raw in custom_file.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        allow.append(line)
    return ClaudeAllowlist(allow=tuple(allow), deny=BUILTIN_DENY)
