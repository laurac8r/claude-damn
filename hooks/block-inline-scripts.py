"""PreToolUse hook: block inline non-Bash scripts in the Bash tool.

Prevents multiline Python/Ruby/Node/Perl/PHP from being executed
directly via -c strings, heredocs, or piped stdin. Enforces the
write-to-/tmp/ workflow from CLAUDE.md.
"""

import json
import re
import sys

PATTERN = re.compile(
    r"(python3?|ruby|node|perl|php)\s+"
    r"(-c\s+['\"][\s\S]*[\n;]|.*<<[-']?EOF)"
    r"|(python3?|ruby|node|perl|php)\s+-e\s+['\"].*[;\n]"
    r"|cat\s.*\|\s*(python3?|ruby|node|perl|php)"
    r"|echo\s.*\|\s*(python3?|ruby|node|perl|php)",
    re.IGNORECASE,
)

MESSAGE = """**Inline non-Bash script detected — BLOCKED.**

You are violating the **No Inline Non-Bash Scripts in Bash** rule from CLAUDE.md.

**Required workflow:**
1. Write the script to `/tmp/script_<name>.py` using the **Write** tool.
2. Wait for user review.
3. Execute via Bash: `python3 /tmp/script_<name>.py`

Single-statement `python3 -c "print(1)"` is allowed (no `;` or newlines)."""


def main():
    try:
        data = json.load(sys.stdin)
        tool_name = data.get("tool_name", "")
        if tool_name != "Bash":
            print(json.dumps({}))
            return

        command = data.get("tool_input", {}).get("command", "")
        if PATTERN.search(command):
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                        },
                        "systemMessage": MESSAGE,
                    }
                )
            )
        else:
            print(json.dumps({}))
    except Exception as e:
        print(json.dumps({"systemMessage": f"Hook error: {e}"}))


if __name__ == "__main__":
    main()
    sys.exit(0)
