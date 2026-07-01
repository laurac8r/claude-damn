"""PreToolUse hook: block dangerous Bash commands.

Three rules enforced via a rule registry:
1. Inline non-Bash scripts (python/ruby/node/perl/php via -c, heredocs, pipes)
2. Command character length limit
3. Statement separator count limit

Rule 1 runs on every command. Rules 2 & 3 are exempted only for commands that
append (`>>`) into ~/.tesseract/bulk-beings.md (see TESSERACT_REDIRECT_PATTERN)
— long/chained "bulk-beings" appends to that file are legitimate. All
applicable violations are reported together.
"""

import json
import re
import sys
from collections.abc import Callable
from dataclasses import dataclass

from constants import (  # type: ignore[import-not-found]
    MAX_COMMAND_LENGTH,
    MAX_STATEMENT_COUNT,
)

# ---------------------------------------------------------------------------
# Rule dataclass
# ---------------------------------------------------------------------------


@dataclass
class Rule:
    name: str
    check: Callable[[str], str | None]


# ---------------------------------------------------------------------------
# Rule 1: Inline script detection (existing regex, unchanged)
# ---------------------------------------------------------------------------

INLINE_SCRIPT_PATTERN = re.compile(
    r"(python3?|ruby|node|perl|php)\s+"
    r"(-c\s+['\"][\s\S]*[\n;]|.*<<[-']?EOF)"
    r"|(python3?|ruby|node|perl|php)\s+-e\s+['\"].*[;\n]"
    r"|cat\s.*\|\s*(python3?|ruby|node|perl|php)"
    r"|echo\s.*\|\s*(python3?|ruby|node|perl|php)",
    re.IGNORECASE,
)

INLINE_SCRIPT_MESSAGE = """**Inline non-Bash script detected — BLOCKED.**

You are violating the **No Inline Non-Bash Scripts in Bash** rule from CLAUDE.md.

**Required workflow:**
1. Write the script to `/tmp/script_<name>.py` using the **Write** tool.
2. Wait for user review.
3. Execute via Bash: `python3 /tmp/script_<name>.py`

Single-statement `python3 -c "print(1)"` is allowed (no `;` or newlines)."""


def check_inline_script(command: str) -> str | None:
    if INLINE_SCRIPT_PATTERN.search(command):
        return INLINE_SCRIPT_MESSAGE
    return None


# ---------------------------------------------------------------------------
# Tesseract path bypass — exempt rules 2 & 3 only (rule 1 still fires)
# ---------------------------------------------------------------------------

# Matches ONLY a `>>` redirect whose target is ~/.tesseract/bulk-beings.md — the
# single legitimate Bash append the tesseract skill makes (the shelf is written
# via the Write tool, not Bash). Scoped to the redirect target (not a free
# substring) so merely mentioning the path in a comment or unused argument cannot
# disarm rules 2 & 3, and narrowed to one file to minimize the bypass surface.
TESSERACT_REDIRECT_PATTERN = re.compile(
    r">>\s+(?:~|\$HOME|/(?:Users|home)/[^/\s]+)/\.tesseract/bulk-beings\.md(?:\s|$)"
)


# Rule 1 (inline-script) still fires regardless; only rules 2 & 3 are exempted,
# and only for legitimate `>> ~/.tesseract/bulk-beings.md` appends.
def _is_tesseract_redirect(command: str) -> bool:
    return bool(TESSERACT_REDIRECT_PATTERN.search(command))


# ---------------------------------------------------------------------------
# Rule 2: Character length limit
# ---------------------------------------------------------------------------

CHAR_LIMIT_MESSAGE = (
    "**Command too long — BLOCKED.**\n\n"
    "Command length ({actual}) exceeds maximum ({limit} chars)."
    " Write a script to `/tmp/` and execute it instead."
)


def check_char_limit(command: str) -> str | None:
    if _is_tesseract_redirect(command):
        return None
    actual = len(command)
    if actual > MAX_COMMAND_LENGTH:
        return CHAR_LIMIT_MESSAGE.format(actual=actual, limit=MAX_COMMAND_LENGTH)
    return None


# ---------------------------------------------------------------------------
# Rule 3: Statement separator count limit
# ---------------------------------------------------------------------------

SEPARATOR_PATTERN = re.compile(r">>|<<|&&|\|\||[|><;\n\r]")

STATEMENT_LIMIT_MESSAGE = (
    "**Too many chained statements — BLOCKED.**\n\n"
    "Command contains {count} statement separators (max {limit})."
    " Break this into a script in `/tmp/` or simplify."
)


def check_statement_limit(command: str) -> str | None:
    # Rule-3 exemption is deliberate: bulk-beings appends chain `>>` redirects
    # into tesseract files, which legitimately exceed the separator limit.
    if _is_tesseract_redirect(command):
        return None
    count = len(SEPARATOR_PATTERN.findall(command))
    if count > MAX_STATEMENT_COUNT:
        return STATEMENT_LIMIT_MESSAGE.format(count=count, limit=MAX_STATEMENT_COUNT)
    return None


# ---------------------------------------------------------------------------
# Rule registry
# ---------------------------------------------------------------------------

RULES: list[Rule] = [
    Rule(name="inline_script", check=check_inline_script),
    Rule(name="char_limit", check=check_char_limit),
    Rule(name="statement_limit", check=check_statement_limit),
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    try:
        data = json.load(sys.stdin)
        tool_name = data.get("tool_name", "")
        if tool_name != "Bash":
            print(json.dumps({}))
            return

        tool_input = data.get("tool_input", {})
        if not isinstance(tool_input, dict):
            tool_input = {}
        command = tool_input.get("command", "")
        if not isinstance(command, str):
            command = ""
        violations = [msg for rule in RULES if (msg := rule.check(command)) is not None]

        if not violations:
            print(json.dumps({}))
            return

        combined = "\n\n---\n\n".join(violations)
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": combined,
                    },
                }
            )
        )
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
