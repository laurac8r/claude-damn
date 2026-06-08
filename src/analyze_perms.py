"""Analyze Claude Code transcripts to suggest read-only allowlist entries.

Scans recent session JSONL transcripts, aggregates Bash/MCP tool-call
frequencies, drops commands already auto-allowed by the harness plus any
mutating or arbitrary-code-execution wildcards, then emits a ranked list of
allowlist patterns suitable for merging into `.claude/settings.json`.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

Verdict = Literal["auto", "mutating", "risky_wildcard", "allowlist"]

# Auto-allowed single-token commands (harness approves with any args).
_AUTO_COMMANDS: frozenset[str] = frozenset(
    {
        "cal",
        "uptime",
        "cat",
        "head",
        "tail",
        "wc",
        "stat",
        "strings",
        "hexdump",
        "od",
        "nl",
        "id",
        "uname",
        "free",
        "df",
        "du",
        "locale",
        "groups",
        "nproc",
        "basename",
        "dirname",
        "realpath",
        "cut",
        "paste",
        "tr",
        "column",
        "tac",
        "rev",
        "fold",
        "expand",
        "unexpand",
        "fmt",
        "comm",
        "cmp",
        "numfmt",
        "readlink",
        "diff",
        "true",
        "false",
        "sleep",
        "which",
        "type",
        "expr",
        "test",
        "getconf",
        "seq",
        "tsort",
        "pr",
        "echo",
        "printf",
        "ls",
        "cd",
        "find",
        "pwd",
        "whoami",
        "alias",
        "xargs",
        "file",
        "sed",
        "sort",
        "man",
        "help",
        "netstat",
        "ps",
        "base64",
        "grep",
        "egrep",
        "fgrep",
        "sha256sum",
        "sha1sum",
        "md5sum",
        "tree",
        "date",
        "hostname",
        "info",
        "lsof",
        "pgrep",
        "tput",
        "ss",
        "fd",
        "fdfind",
        "aki",
        "rg",
        "jq",
        "uniq",
        "history",
        "arch",
        "ifconfig",
        "pyright",
    }
)

# git/gh/docker subcommands the harness auto-allows (matched as `<tool> <sub>`).
_AUTO_PAIRS: frozenset[str] = frozenset(
    {
        "git status",
        "git log",
        "git diff",
        "git show",
        "git blame",
        "git branch",
        "git remote",
        "git ls-files",
        "git ls-remote",
        "git config",
        "git rev-parse",
        "git describe",
        "git reflog",
        "git shortlog",
        "git cat-file",
        "git for-each-ref",
        "git worktree",
        "gh pr",
        "gh issue",
        "gh run",
        "gh workflow",
        "gh repo",
        "gh release",
        "gh api",
        "gh auth",
        "docker ps",
        "docker images",
        "docker logs",
        "docker inspect",
    }
)

# Commands that mutate / publish / install — never eligible for allowlist.
_MUTATING_COMMANDS: frozenset[str] = frozenset(
    {
        "rm",
        "rmdir",
        "mv",
        "cp",
        "ln",
        "touch",
        "chmod",
        "chown",
        "mkdir",
        "tee",
        "truncate",
        "shred",
        "dd",
        "kill",
        "pkill",
        "killall",
        "brew",
        "port",
        "apt",
        "apt-get",
        "yum",
        "dnf",
        "pacman",
        "pip",
        "pip3",
        "poetry",
        "pipenv",
    }
)
_MUTATING_PAIRS: frozenset[str] = frozenset(
    {
        "git push",
        "git commit",
        "git merge",
        "git rebase",
        "git reset",
        "git checkout",
        "git cherry-pick",
        "git revert",
        "git add",
        "git clean",
        "git restore",
        "git pull",
        "git fetch",
        "git tag",
        "git stash",
        "git apply",
        "gh pr create",
        "gh pr merge",
        "gh pr close",
        "gh pr edit",
        "gh pr review",
        "gh pr comment",
        "gh issue create",
        "gh issue close",
        "gh issue edit",
        "gh issue comment",
        "gh release create",
        "gh repo create",
        "gh repo delete",
        "npm install",
        "npm i",
        "npm update",
        "npm uninstall",
        "npm publish",
        "yarn install",
        "yarn add",
        "yarn remove",
        "yarn publish",
        "pnpm install",
        "pnpm add",
        "pnpm remove",
        "pnpm publish",
        "bun install",
        "bun add",
        "bun remove",
        "bun publish",
        "cargo install",
        "cargo publish",
        "cargo add",
        "cargo remove",
        "uv sync",
        "uv add",
        "uv remove",
        "uv pip",
        "uv lock",
        "docker run",
        "docker exec",
        "docker build",
        "docker rm",
        "docker rmi",
        "docker push",
        "docker pull",
        "docker start",
        "docker stop",
        "docker restart",
        "docker kill",
    }
)

# Wildcarding any of these would grant arbitrary code execution.
# Pair families (``git``, ``gh``, ``docker``, ``npm``, ``yarn``, ``pnpm``,
# ``bun``, ``cargo``, ``uv``) are risky at the bare-leaf level because
# ``Bash(git *)`` also matches ``git push``; known-safe subcommands are
# whitelisted via ``_AUTO_PAIRS`` which wins in ``classify_bash_key``.
_RISKY_COMMANDS: frozenset[str] = frozenset(
    {
        "python",
        "python3",
        "node",
        "deno",
        "ruby",
        "perl",
        "php",
        "lua",
        "bash",
        "sh",
        "zsh",
        "fish",
        "eval",
        "exec",
        "ssh",
        "scp",
        "npx",
        "bunx",
        "uvx",
        "pipx",
        "git",
        "gh",
        "docker",
        "npm",
        "yarn",
        "pnpm",
        "bun",
        "cargo",
        "uv",
        # Shell control keywords — parsing `for f in *; do ...` strands
        # ``for`` as a leading token; allowlisting it would be nonsense.
        "for",
        "while",
        "if",
        "case",
        "do",
        "then",
        "function",
    }
)
_RISKY_PAIRS: frozenset[str] = frozenset(
    {
        "npm run",
        "yarn run",
        "pnpm run",
        "bun run",
        "cargo run",
        "go run",
        "make",  # bare `make` runs arbitrary Makefile targets
        "uv run",
        "just",
    }
)

_ENV_PREFIX = re.compile(r"^(?:[A-Za-z_][A-Za-z0-9_]*=\S+(?:\s+|$))+")
_SEGMENT_SEP = re.compile(r"&&|\|\||[;|]")
_VAR_ASSIGN = re.compile(r"^[A-Z_][A-Z0-9_]*=")
# ``env`` flags that consume a following argument (``env -u NAME cmd``).
_ENV_FLAGS_WITH_ARG: frozenset[str] = frozenset({"-u", "-C", "-S"})

# Second tokens that signal per-session noise rather than a stable subcommand:
# absolute/relative/home paths, commit-sha-like hex blobs, or filenames.
# Applied as a post-filter in ``rank_suggestions`` so the parser and counter
# stay stable and only the emitted allowlist is pruned.
_NOISY_SECOND_TOKEN = re.compile(r"^(?:[~/.]|[a-f0-9]{7,40}$|.*\.[a-z]{1,5}$)")


def _is_numeric_duration(token: str) -> bool:
    core = token[:-1] if token and token[-1] in "smhd" else token
    return bool(core) and core.replace(".", "", 1).isdigit()


def extract_first_command(cmd: str) -> tuple[str, str] | None:
    """Return (leading_token, leading+first_subcommand) for a bash command.

    Path prefixes are stripped from the leading token so allowlist keys stay
    command names (``git``) rather than install locations (``/usr/bin/git``).
    Flag-prefixed second tokens (``--oneline``) are dropped so keys stay
    stable across flag variations.

    Returns ``None`` when no runnable command survives stripping env
    assignments and wrappers.
    """
    s = cmd.strip()
    if not s:
        return None

    s = _ENV_PREFIX.sub("", s)

    m = _SEGMENT_SEP.search(s)
    if m is not None:
        s = s[: m.start()].strip()

    tokens = s.split()
    while tokens and tokens[0] in ("sudo", "nohup"):
        tokens.pop(0)
    if tokens and tokens[0] == "env":
        tokens.pop(0)
        while tokens:
            t = tokens[0]
            if t.startswith("-"):
                tokens.pop(0)
                if t in _ENV_FLAGS_WITH_ARG and tokens:
                    tokens.pop(0)
                continue
            if _VAR_ASSIGN.match(t):
                tokens.pop(0)
                continue
            break
    if tokens and tokens[0] == "timeout":
        tokens.pop(0)
        while tokens:
            t = tokens[0]
            if t.startswith("-"):
                tokens.pop(0)
                if tokens:
                    nxt = tokens[0]
                    if not nxt.startswith("-") and not _is_numeric_duration(nxt):
                        tokens.pop(0)
                continue
            if _is_numeric_duration(t):
                tokens.pop(0)
                continue
            break

    if not tokens:
        return None

    leading = tokens[0].rsplit("/", 1)[-1]
    second = tokens[1] if len(tokens) > 1 else ""
    if second.startswith("-"):
        second = ""
    pair = f"{leading} {second}".strip()
    return leading, pair


def classify_bash_key(key: str) -> Verdict:
    """Classify a ``leading subcommand`` key as auto / mutating / risky / allow.

    Pair lookups win over single-token lookups so e.g. ``git push`` classifies
    as ``mutating`` even though ``git`` alone would be treated as an auto-
    allowed pair family.
    """
    leading = key.split(" ", 1)[0]
    if key in _AUTO_PAIRS:
        return "auto"
    if key in _MUTATING_PAIRS:
        return "mutating"
    if key in _RISKY_PAIRS:
        return "risky_wildcard"
    if leading in _AUTO_COMMANDS:
        return "auto"
    if leading in _MUTATING_COMMANDS:
        return "mutating"
    if leading in _RISKY_COMMANDS:
        return "risky_wildcard"
    return "allowlist"


@dataclass
class ScanResult:
    bash: Counter[str] = field(default_factory=Counter)
    mcp: Counter[str] = field(default_factory=Counter)


def scan_transcripts(paths: Iterable[Path]) -> ScanResult:
    """Aggregate Bash and MCP tool-call frequencies across JSONL transcripts.

    Bash commands are keyed by the ``leading subcommand`` pair returned from
    :func:`extract_first_command`. MCP tools are keyed by their verbatim name.
    Malformed lines and non-``tool_use`` content are silently skipped.
    """
    result = ScanResult()
    for path in paths:
        try:
            fh = path.open(encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(obj, dict) or obj.get("type") != "assistant":
                    continue
                message = obj.get("message")
                if not isinstance(message, dict):
                    continue
                content = message.get("content")
                if not isinstance(content, list):
                    continue
                for item in content:
                    if not isinstance(item, dict) or item.get("type") != "tool_use":
                        continue
                    name = item.get("name") or ""
                    if name == "Bash":
                        cmd = (item.get("input") or {}).get("command", "")
                        if not isinstance(cmd, str) or not cmd.strip():
                            continue
                        parsed = extract_first_command(cmd)
                        if parsed is None:
                            continue
                        result.bash[parsed[1]] += 1
                    elif name.startswith("mcp__"):
                        result.mcp[name] += 1
    return result


@dataclass(frozen=True)
class Suggestion:
    pattern: str
    count: int
    note: str


def rank_suggestions(
    scan: ScanResult,
    *,
    limit: int = 20,
    min_count: int = 3,
) -> list[Suggestion]:
    """Rank allowlist suggestions by observed frequency across Bash + MCP.

    Bash keys that the harness already auto-allows, or that mutate, or that
    would need an arbitrary-exec wildcard, are dropped. Remaining Bash keys
    emit as ``Bash(<key> *)``; MCP tool names emit verbatim. Entries below
    ``min_count`` are discarded, and the result is capped at ``limit``.
    """
    suggestions: list[Suggestion] = []
    for key, count in scan.bash.items():
        if count < min_count:
            continue
        if classify_bash_key(key) != "allowlist":
            continue
        if " " in key and _NOISY_SECOND_TOKEN.match(key.split(" ", 1)[1]):
            continue
        suggestions.append(Suggestion(f"Bash({key} *)", count, key))
    for name, count in scan.mcp.items():
        if count < min_count:
            continue
        suggestions.append(Suggestion(name, count, "MCP tool"))
    suggestions.sort(key=lambda s: (-s.count, s.pattern))
    return suggestions[:limit]


def find_recent_transcripts(root: Path, *, limit: int) -> list[Path]:
    """Return the ``limit`` most recently modified ``*.jsonl`` files under root.

    Pytest worker temp dirs (paths containing ``pytest-of``) are excluded so
    local test-suite runs don't pollute the allowlist suggestions.
    """
    candidates: list[tuple[float, Path]] = []
    for p in root.rglob("*.jsonl"):
        if any("pytest-of" in part for part in p.relative_to(root).parts):
            continue
        try:
            mtime = p.stat().st_mtime
        except OSError:
            continue
        candidates.append((mtime, p))
    candidates.sort(key=lambda candidate: candidate[0], reverse=True)
    return [path for _, path in candidates[:limit]]


def format_table(suggestions: list[Suggestion]) -> str:
    """Render a ranked suggestion list as a Markdown table."""
    if not suggestions:
        return "No suggestions (below min_count or all auto-allowed)."
    rows = ["| # | Pattern | Count | Notes |", "|---|---------|-------|-------|"]
    for rank, s in enumerate(suggestions, start=1):
        rows.append(f"| {rank} | `{s.pattern}` | {s.count} | {s.note} |")
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: scan transcripts and print a ranked allowlist table."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Suggest allowlist entries from recent Claude Code transcripts."
    )
    parser.add_argument(
        "--projects-dir",
        type=Path,
        default=Path.home() / ".claude" / "projects",
        help="Root of Claude Code project transcripts.",
    )
    parser.add_argument(
        "--sessions", type=int, default=50, help="Recent sessions to scan."
    )
    parser.add_argument(
        "--limit", type=int, default=20, help="Max suggestions to show."
    )
    parser.add_argument(
        "--min-count", type=int, default=3, help="Drop patterns below this count."
    )
    args = parser.parse_args(argv)

    try:
        if not args.projects_dir.exists():
            raise FileNotFoundError(
                f"[Errno 2] No such file or directory: '{args.projects_dir}'"
            )
        paths = find_recent_transcripts(args.projects_dir, limit=args.sessions)
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    scan = scan_transcripts(paths)
    suggestions = rank_suggestions(scan, limit=args.limit, min_count=args.min_count)
    print(format_table(suggestions))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
