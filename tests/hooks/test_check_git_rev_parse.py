"""Regression tests for check_git_rev_parse.py hook.

The hook flags two high-confidence unsafe patterns in `git rev-parse`
invocations on the Bash matcher:

  - Pattern A: unquoted `$VAR` / `${VAR}` after `git rev-parse`
  - Pattern D: `git rev-parse --parseopt` co-located with the eval builtin

It is **warn-mode** — emits `systemMessage` and does NOT block.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK_SCRIPT = Path(__file__).parent.parent.parent / "hooks" / "check_git_rev_parse.py"

# Make hook importable for unit tests without going through subprocess.
sys.path.insert(0, str(HOOK_SCRIPT.parent))

from check_git_rev_parse import (  # noqa: E402
    check,
    has_parseopt_eval_combo,
    has_unquoted_var_after_rev_parse,
)

# ---------------------------------------------------------------------------
# Pattern A — unquoted variable after `git rev-parse`
# ---------------------------------------------------------------------------


class TestUnquotedVarDetector:
    @pytest.mark.parametrize(
        "command",
        [
            "git rev-parse $FOO",
            "git rev-parse ${FOO}",
            "git rev-parse --verify $USER_INPUT",
            "HASH=$(git rev-parse $USER_INPUT)",
            "git -C /tmp rev-parse $FOO",
            "git rev-parse HEAD~$N",
        ],
    )
    def test_flags_unquoted(self, command: str) -> None:
        assert has_unquoted_var_after_rev_parse(command) is True

    @pytest.mark.parametrize(
        "command",
        [
            'git rev-parse "$FOO"',
            'git rev-parse "${FOO}"',
            'git rev-parse --verify "$USER_INPUT"',
            "git rev-parse '$FOO'",
            "git rev-parse --is-inside-work-tree",
            "git rev-parse --show-toplevel",
            "git rev-parse --git-dir",
            "git rev-parse HEAD",
            "git rev-parse --verify HEAD",
            "git rev-parse HEAD -- path/to/file",
            'HASH=$(git rev-parse --verify "$USER_INPUT") || exit 1',
        ],
    )
    def test_allows_safe(self, command: str) -> None:
        assert has_unquoted_var_after_rev_parse(command) is False

    def test_no_rev_parse_in_command(self) -> None:
        assert has_unquoted_var_after_rev_parse("echo $FOO") is False

    def test_subshell_after_rev_parse_is_not_a_bare_var(self) -> None:
        # $( starts a subshell, not a var expansion. Should NOT trigger.
        assert has_unquoted_var_after_rev_parse("git rev-parse $(echo HEAD)") is False


# ---------------------------------------------------------------------------
# Pattern D — --parseopt co-located with the eval builtin
# ---------------------------------------------------------------------------


class TestParseoptEvalCombo:
    @pytest.mark.parametrize(
        "command",
        [
            'eval "$(git rev-parse --parseopt -- "$@" <<EOF\nUSAGE: x\nEOF\n)"',
            "eval $(git rev-parse --parseopt -- $@ <<-EOF\nUSAGE\nEOF\n)",
            "git rev-parse --parseopt -- $@ | eval",
        ],
    )
    def test_flags_combo(self, command: str) -> None:
        assert has_parseopt_eval_combo(command) is True

    @pytest.mark.parametrize(
        "command",
        [
            "git rev-parse --parseopt -- $@",  # parseopt without eval
            "eval echo hi",  # eval without rev-parse
            "git rev-parse --verify HEAD",  # neither
            "echo evaluating-not-a-builtin",  # the word eval inside another token
        ],
    )
    def test_allows_others(self, command: str) -> None:
        assert has_parseopt_eval_combo(command) is False


# ---------------------------------------------------------------------------
# check() — full PreToolUse payload decision
# ---------------------------------------------------------------------------


class TestCheck:
    def test_allows_safe_command(self) -> None:
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "git rev-parse --is-inside-work-tree"},
        }
        assert check(payload) == {}

    def test_warns_on_unquoted_var(self) -> None:
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "git rev-parse $USER_INPUT"},
        }
        result = check(payload)
        assert "systemMessage" in result
        assert "Pattern A" in result["systemMessage"]
        # Warn-mode: must NOT include permissionDecision (would block/ask).
        assert "hookSpecificOutput" not in result

    def test_warns_on_parseopt_eval(self) -> None:
        payload = {
            "tool_name": "Bash",
            "tool_input": {
                "command": 'eval "$(git rev-parse --parseopt -- "$@" <<EOF\nU\nEOF\n)"'
            },
        }
        result = check(payload)
        assert "systemMessage" in result
        assert "Pattern D" in result["systemMessage"]

    def test_no_op_for_non_bash_tool(self) -> None:
        payload = {
            "tool_name": "Write",
            "tool_input": {"command": "git rev-parse $FOO"},
        }
        assert check(payload) == {}

    def test_handles_missing_tool_input(self) -> None:
        payload = {"tool_name": "Bash"}
        assert check(payload) == {}

    def test_handles_non_dict_payload(self) -> None:
        assert check("not a dict") == {}
        assert check(None) == {}
        assert check(42) == {}

    def test_combines_messages_when_both_patterns_present(self) -> None:
        payload = {
            "tool_name": "Bash",
            "tool_input": {
                "command": (
                    'eval "$(git rev-parse --parseopt -- "$@" <<EOF\nU\nEOF\n)"; '
                    "git rev-parse $X"
                )
            },
        }
        result = check(payload)
        assert "Pattern A" in result["systemMessage"]
        assert "Pattern D" in result["systemMessage"]


# ---------------------------------------------------------------------------
# Subprocess integration — fail-open on malformed JSON, JSON-shape on stdout
# ---------------------------------------------------------------------------


def _run_hook(stdin_text: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return proc.returncode, proc.stdout, proc.stderr


class TestSubprocessEntry:
    def test_safe_payload_emits_empty_json(self) -> None:
        payload = json.dumps(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "git rev-parse --show-toplevel"},
            }
        )
        rc, out, _ = _run_hook(payload)
        assert rc == 0
        assert json.loads(out) == {}

    def test_unsafe_payload_emits_warning_json(self) -> None:
        payload = json.dumps(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "git rev-parse $USER_INPUT"},
            }
        )
        rc, out, _ = _run_hook(payload)
        assert rc == 0
        body = json.loads(out)
        assert "systemMessage" in body

    def test_malformed_json_fails_open(self) -> None:
        rc, out, _ = _run_hook("this is not json {{{")
        assert rc == 0
        assert json.loads(out) == {}

    def test_empty_stdin_fails_open(self) -> None:
        rc, out, _ = _run_hook("")
        assert rc == 0
        assert json.loads(out) == {}
