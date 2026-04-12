"""PreToolUse hook: block dangerous Bash commands.

Three rules enforced via a rule registry:
1. Inline non-Bash scripts (python/ruby/node/perl/php via -c, heredocs, pipes)
2. Command character length limit
3. Statement separator count limit

All rules run on every command; all violations are reported together.
"""

import json
import re
import sys
from collections.abc import Callable
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Configurable constants — edit these to change defaults
# ---------------------------------------------------------------------------
MAX_COMMAND_LENGTH = 300  # characters
MAX_STATEMENT_COUNT = 3  # separator occurrences


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
# Rule 2: Character length limit
# ---------------------------------------------------------------------------

CHAR_LIMIT_MESSAGE = (
    "**Command too long — BLOCKED.**\n\n"
    "Command length ({actual}) exceeds maximum ({limit} chars)."
    " Write a script to `/tmp/` and execute it instead."
)


def check_char_limit(command: str) -> str | None:
    actual = len(command)
    if actual > MAX_COMMAND_LENGTH:
        return CHAR_LIMIT_MESSAGE.format(actual=actual, limit=MAX_COMMAND_LENGTH)
    return None


# ---------------------------------------------------------------------------
# Rule 3: Statement separator count limit
# ---------------------------------------------------------------------------

SEPARATOR_PATTERN = re.compile(r"&&|\|\||[|><;\n\r]")

STATEMENT_LIMIT_MESSAGE = (
    "**Too many chained statements — BLOCKED.**\n\n"
    "Command contains {count} statement separators (max {limit})."
    " Break this into a script in `/tmp/` or simplify."
)


def check_statement_limit(command: str) -> str | None:
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

        command = data.get("tool_input", {}).get("command", "")
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
                    },
                    "systemMessage": combined,
                }
            )
        )
    except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as e:
        print(json.dumps({"systemMessage": f"Hook error: {e}"}))


if __name__ == "__main__":
    main()
    sys.exit(0)
