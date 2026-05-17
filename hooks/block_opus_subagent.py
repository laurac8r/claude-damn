"""PreToolUse hook — block Opus model in Task (subagent) dispatches.

Reads a PreToolUse payload on stdin. Denies Task-tool calls whose `model`
field contains "opus" (case-insensitive) unless an override is present.

Overrides (any → allow through):
  - Env CLAUDE_BATCH_MODE in {"1", "true", "yes"} (case-insensitive).
  - tool_input.prompt or tool_input.description contains "[BATCH_OVERRIDE]"
    (case-sensitive, so accidental lowercase doesn't bypass the policy).

TODO(operator): Confirm how the built-in /batch command/skill leaks context
into spawned Task calls (env var / tool_input field / prompt prefix?). Once
known, add that detection here as a third override condition.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

_TRUTHY = frozenset({"1", "true", "yes"})
_SENTINEL = "[BATCH_OVERRIDE]"


def is_opus(model: str) -> bool:
    """Case-insensitive check — True when model string contains 'opus'."""
    return "opus" in model.lower()


def _batch_env_active() -> bool:
    return os.environ.get("CLAUDE_BATCH_MODE", "").lower() in _TRUTHY


def _has_sentinel(tool_input: dict[str, Any]) -> bool:
    prompt = str(tool_input.get("prompt") or "")
    description = str(tool_input.get("description") or "")
    return _SENTINEL in prompt or _SENTINEL in description


def check(payload: Any) -> dict[str, Any]:
    """Evaluate a PreToolUse payload. Empty dict = allow; populated = deny."""
    if not isinstance(payload, dict):
        return {}

    if payload.get("tool_name", "") != "Task":
        return {}

    tool_input = payload.get("tool_input", {})
    if not isinstance(tool_input, dict):
        return {}

    model = str(tool_input.get("model", ""))
    if not model or not is_opus(model):
        return {}

    if _batch_env_active() or _has_sentinel(tool_input):
        return {}

    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "Opus subagents are blocked by policy. "
                "Use model='sonnet' or model='haiku'. "
                "Override: set CLAUDE_BATCH_MODE=1, "
                "include [BATCH_OVERRIDE] in the prompt or description, "
                "or invoke via /batch."
            ),
        }
    }


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
