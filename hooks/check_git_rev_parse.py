"""PreToolUse hook — flag unsafe `git rev-parse` patterns in Bash commands.

WARN-MODE: emits a `systemMessage` describing the suspect pattern but does
NOT block the tool call. See `~/.claude/rules/git_rev_parse_safety.md` for
the full rule rationale.

Patterns flagged:

  - Pattern A: unquoted `$VAR` / `${VAR}` after `git rev-parse`
  - Pattern D: `git rev-parse --parseopt` co-located with the eval builtin
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any

# ---------------------------------------------------------------------------
# Pattern A — unquoted variable expansion after `git rev-parse`
# ---------------------------------------------------------------------------

# Matches the `git rev-parse` invocation, optionally with `-C <path>` between
# `git` and `rev-parse`. The match end-anchor sits right after `rev-parse` so
# the segment scan starts on the first arg.
_GIT_REV_PARSE_RE = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?rev-parse\b")


def _extract_segment(command: str, start: int) -> str:
    """Return command[start:] up to the next unquoted shell separator.

    Tracks single/double quotes and parenthesis depth so we don't mistake a
    `;` or `)` inside a string or subshell for a real boundary.
    """
    in_dquote = False
    in_squote = False
    paren_depth = 0
    end = len(command)
    i = start
    while i < len(command):
        c = command[i]
        prev = command[i - 1] if i > 0 else ""
        if not in_squote and c == '"' and prev != "\\":
            in_dquote = not in_dquote
        elif not in_dquote and c == "'":
            in_squote = not in_squote
        elif not in_dquote and not in_squote:
            if c == "(":
                paren_depth += 1
            elif c == ")":
                if paren_depth == 0:
                    end = i
                    break
                paren_depth -= 1
            elif c in ";|&\n" and paren_depth == 0:
                end = i
                break
        i += 1
    return command[start:end]


def _has_unquoted_var(segment: str) -> bool:
    """Return True iff segment contains a `$VAR` or `${VAR}` outside quotes.

    A `$(` (subshell start) or `$$` does NOT count — only bare variable
    expansions where the next character is a name-start or `{`.
    """
    in_dquote = False
    in_squote = False
    i = 0
    while i < len(segment):
        c = segment[i]
        prev = segment[i - 1] if i > 0 else ""
        if not in_squote and c == '"' and prev != "\\":
            in_dquote = not in_dquote
        elif not in_dquote and c == "'":
            in_squote = not in_squote
        elif c == "$" and not in_dquote and not in_squote:
            if i + 1 < len(segment):
                nxt = segment[i + 1]
                if nxt.isalpha() or nxt == "_" or nxt == "{":
                    return True
        i += 1
    return False


def has_unquoted_var_after_rev_parse(command: Any) -> bool:
    if not isinstance(command, str):
        return False
    for m in _GIT_REV_PARSE_RE.finditer(command):
        if _has_unquoted_var(_extract_segment(command, m.end())):
            return True
    return False


# ---------------------------------------------------------------------------
# Pattern D — `--parseopt` co-located with the `eval` builtin
# ---------------------------------------------------------------------------

# Word-boundary match so "evaluating" / "evaluation" don't trigger.
_EVAL_TOKEN_RE = re.compile(r"\beval\b")


def has_parseopt_eval_combo(command: Any) -> bool:
    if not isinstance(command, str):
        return False
    if "--parseopt" not in command:
        return False
    return bool(_EVAL_TOKEN_RE.search(command))


# ---------------------------------------------------------------------------
# Decision
# ---------------------------------------------------------------------------

_HEADER = (
    "**`git rev-parse` safety warning** — see "
    "`~/.claude/rules/git_rev_parse_safety.md`."
)
_FOOTER = "_(Warn-mode: not blocking. Proceed if confident.)_"

_PATTERN_A_MSG = (
    "**Pattern A** — `git rev-parse <unquoted $VAR>` detected. "
    'Quote variables (`"$VAR"`) and resolve refs with `--verify`.'
)
_PATTERN_D_MSG = (
    "**Pattern D** — `git rev-parse --parseopt` co-located with the "
    "`eval` builtin. Treat the eval site as an untrusted-input boundary; "
    "keep the spec string static."
)


def check(payload: Any) -> dict:
    if not isinstance(payload, dict):
        return {}
    if payload.get("tool_name") != "Bash":
        return {}
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return {}
    command = tool_input.get("command", "")
    if not isinstance(command, str) or not command:
        return {}

    warnings: list[str] = []
    if has_unquoted_var_after_rev_parse(command):
        warnings.append(_PATTERN_A_MSG)
    if has_parseopt_eval_combo(command):
        warnings.append(_PATTERN_D_MSG)
    if not warnings:
        return {}
    body = "\n\n".join([_HEADER, *warnings, _FOOTER])
    return {"systemMessage": body}


# ---------------------------------------------------------------------------
# Script entry — fail open on any malformed input
# ---------------------------------------------------------------------------


def main_from_stdin() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError, ValueError:
        print("{}")
        return
    print(json.dumps(check(data)))


if __name__ == "__main__":
    main_from_stdin()
    sys.exit(0)
