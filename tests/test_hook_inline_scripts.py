"""Regression tests: block-inline-scripts.py hook behavior."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK_SCRIPT = Path(__file__).parent.parent / "hooks" / "block-inline-scripts.py"


def run_hook(tool_name: str, command: str) -> dict:
    """Feed a simulated tool call to the hook and return its JSON output."""
    payload = json.dumps({
        "tool_name": tool_name,
        "tool_input": {"command": command},
    })
    result = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"Hook crashed: {result.stderr}"
    return json.loads(result.stdout)


class TestHookBlocksInlineScripts:
    """Commands that MUST be blocked."""

    @pytest.mark.parametrize("command", [
        'python3 -c "import os; os.listdir()"',
        "python -c 'x = 1\nprint(x)'",
        "python3 <<EOF\nprint('hello')\nEOF",
        "python3 <<'EOF'\nimport sys\nEOF",
        "ruby -c 'puts 1; puts 2'",
        "node -c 'console.log(1)\nconsole.log(2)'",
        "perl -e 'print 1; print 2'",
        "cat /tmp/script.py | python3",
        "echo 'print(1)' | python3",
        "echo 'puts 1' | ruby",
    ])
    def test_blocks_inline_script(self, command: str) -> None:
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny", (
            f"Should block: {command!r}"
        )

    @pytest.mark.parametrize("command", [
        'python3 -c "import os; os.listdir()"',
        "python3 <<EOF\nprint('hello')\nEOF",
        "cat /tmp/x.py | python3",
    ])
    def test_blocked_output_has_system_message(self, command: str) -> None:
        output = run_hook("Bash", command)
        assert "systemMessage" in output
        assert "BLOCKED" in output["systemMessage"]


class TestHookAllowsSafeCommands:
    """Commands that must NOT be blocked."""

    @pytest.mark.parametrize("command", [
        'python3 -c "print(1)"',
        "python3 /tmp/script_analysis.py",
        "uv run pytest tests/",
        "git status",
        "ls -la",
        "npm run build",
        "echo hello",
        "rg 'pattern' src/",
        "python3 --version",
    ])
    def test_allows_safe_command(self, command: str) -> None:
        output = run_hook("Bash", command)
        assert output == {}, f"Should allow: {command!r}"


class TestHookIgnoresNonBash:
    """Non-Bash tools should pass through without inspection."""

    @pytest.mark.parametrize("tool_name", [
        "Read",
        "Write",
        "Edit",
        "Grep",
        "Glob",
    ])
    def test_ignores_non_bash_tools(self, tool_name: str) -> None:
        output = run_hook(tool_name, 'python3 -c "import os; os.listdir()"')
        assert output == {}


class TestHookMalformedInput:
    """Hook must not crash on unexpected input."""

    def test_empty_command(self) -> None:
        output = run_hook("Bash", "")
        assert output == {}

    def test_missing_tool_input(self) -> None:
        payload = json.dumps({"tool_name": "Bash"})
        result = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        # Should not crash — either {} or an error message
        assert isinstance(output, dict)

    def test_invalid_json(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input="not json",
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "systemMessage" in output  # graceful error
