"""Regression tests: block-inline-scripts.py hook behavior."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK_SCRIPT = Path(__file__).parent.parent / "hooks" / "block-inline-scripts.py"


def run_hook(tool_name: str, command: str) -> dict:
    """Feed a simulated tool call to the hook and return its JSON output."""
    payload = json.dumps(
        {
            "tool_name": tool_name,
            "tool_input": {"command": command},
        }
    )
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

    @pytest.mark.parametrize(
        "command",
        [
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
        ],
    )
    def test_blocks_inline_script(self, command: str) -> None:
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny", (
            f"Should block: {command!r}"
        )

    @pytest.mark.parametrize(
        "command",
        [
            'python3 -c "import os; os.listdir()"',
            "python3 <<EOF\nprint('hello')\nEOF",
            "cat /tmp/x.py | python3",
        ],
    )
    def test_blocked_output_has_deny_reason(self, command: str) -> None:
        output = run_hook("Bash", command)
        assert "systemMessage" not in output
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]
        assert "BLOCKED" in reason


class TestHookAllowsSafeCommands:
    """Commands that must NOT be blocked."""

    @pytest.mark.parametrize(
        "command",
        [
            'python3 -c "print(1)"',
            "python3 /tmp/script_analysis.py",
            "uv run pytest tests/",
            "git status",
            "ls -la",
            "npm run build",
            "echo hello",
            "rg 'pattern' src/",
            "python3 --version",
        ],
    )
    def test_allows_safe_command(self, command: str) -> None:
        output = run_hook("Bash", command)
        assert output == {}, f"Should allow: {command!r}"


class TestCharLimit:
    """Commands exceeding MAX_COMMAND_LENGTH must be blocked."""

    def test_blocks_command_over_300_chars(self) -> None:
        command = "echo " + "a" * 296  # 301 chars total
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny"

    def test_allows_command_at_exactly_300_chars(self) -> None:
        command = "echo " + "a" * 295  # 300 chars total
        output = run_hook("Bash", command)
        # Should not be blocked by char limit; also won't trip other rules
        assert output == {}

    def test_blocked_message_includes_length_and_limit(self) -> None:
        command = "echo " + "a" * 296  # 301 chars
        output = run_hook("Bash", command)
        assert "systemMessage" not in output
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]
        assert "301" in reason
        assert "300" in reason
        assert "BLOCKED" in reason


class TestStatementLimit:
    """Commands with too many statement separators must be blocked."""

    def test_blocks_command_with_4_semicolons(self) -> None:
        command = "echo a; echo b; echo c; echo d; echo e"
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny"

    def test_blocks_command_with_4_and_operators(self) -> None:
        command = "echo a && echo b && echo c && echo d && echo e"
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny"

    def test_blocks_command_with_4_or_operators(self) -> None:
        command = "echo a || echo b || echo c || echo d || echo e"
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny"

    def test_blocks_command_with_4_pipes(self) -> None:
        command = "cat file | grep a | sort | uniq | wc -l"
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny"

    def test_blocks_command_with_mixed_separators(self) -> None:
        command = "echo a && echo b | grep c; echo d > out.txt"
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny"

    def test_allows_command_with_exactly_3_separators(self) -> None:
        command = "echo a && echo b | grep c; echo d"
        output = run_hook("Bash", command)
        # 3 separators (&&, |, ;) — at the limit, not over
        assert output == {}

    def test_double_ampersand_counts_as_one(self) -> None:
        """'&&' is one separator, not two '&' characters."""
        command = "echo a && echo b && echo c && echo d"
        output = run_hook("Bash", command)
        # 3 && = 3 separators, at the limit
        assert output == {}

    def test_double_pipe_counts_as_one(self) -> None:
        """'||' is one separator, not two '|' characters."""
        command = "echo a || echo b || echo c || echo d"
        output = run_hook("Bash", command)
        # 3 || = 3 separators, at the limit
        assert output == {}

    def test_newline_counts_as_separator(self) -> None:
        command = "echo a\necho b\necho c\necho d\necho e"
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny"

    def test_carriage_return_counts_as_separator(self) -> None:
        command = "echo a\recho b\recho c\recho d\recho e"
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny"

    def test_redirect_counts_as_separator(self) -> None:
        command = "echo a > f1 > f2 > f3 > f4"
        output = run_hook("Bash", command)
        hook_out = output.get("hookSpecificOutput", {})
        assert hook_out.get("permissionDecision") == "deny"

    def test_blocked_message_includes_count_and_limit(self) -> None:
        command = "echo a; echo b; echo c; echo d; echo e"
        output = run_hook("Bash", command)
        assert "systemMessage" not in output
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]
        assert "4" in reason  # 4 semicolons
        assert "3" in reason  # max is 3
        assert "BLOCKED" in reason

    # --- Fix A: SEPARATOR_PATTERN must not double-count >> and << ---

    def test_double_right_redirect_pattern_counts_as_one(self) -> None:
        """Unit test: SEPARATOR_PATTERN.findall treats '>>' as one token."""
        spec = importlib.util.spec_from_file_location(
            "block_inline_scripts",
            Path(__file__).parent.parent / "hooks" / "block-inline-scripts.py",
        )
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        assert mod.SEPARATOR_PATTERN.findall("a >> b") == [">>"]

    def test_double_left_redirect_pattern_counts_as_one(self) -> None:
        """Unit test: SEPARATOR_PATTERN.findall treats '<<' as one token."""
        spec = importlib.util.spec_from_file_location(
            "block_inline_scripts",
            Path(__file__).parent.parent / "hooks" / "block-inline-scripts.py",
        )
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        assert mod.SEPARATOR_PATTERN.findall("a << b") == ["<<"]

    def test_double_right_redirect_allowed_at_limit(self) -> None:
        """Integration: 'echo a >> f1 >> f2 >> f3' has 3 >> tokens = 3 separators."""
        command = "echo a >> f1 >> f2 >> f3"
        output = run_hook("Bash", command)
        # 3 '>>' = 3 separators — at the limit, must be ALLOWED
        assert output == {}, f"Should allow: {command!r}"


class TestMultipleViolations:
    """Commands tripping multiple rules report all violations."""

    def test_char_limit_and_statement_limit_both_reported(self) -> None:
        # Long command with many separators
        command = "echo " + "a" * 280 + "; echo b; echo c; echo d; echo e"
        output = run_hook("Bash", command)
        assert "systemMessage" not in output
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]
        assert "Command too long" in reason
        assert "Too many chained statements" in reason
        assert "---" in reason

    def test_all_three_rules_reported(self) -> None:
        # Inline script + long + many separators
        command = (
            'python3 -c "import os; os.listdir()" && '
            + "echo "
            + "a" * 280
            + "; echo b; echo c; echo d"
        )
        output = run_hook("Bash", command)
        assert "systemMessage" not in output
        reason = output["hookSpecificOutput"]["permissionDecisionReason"]
        assert "Inline non-Bash script detected" in reason
        assert "Command too long" in reason
        assert "Too many chained statements" in reason


class TestHookIgnoresNonBash:
    """Non-Bash tools should pass through without inspection."""

    @pytest.mark.parametrize(
        "tool_name",
        [
            "Read",
            "Write",
            "Edit",
            "Grep",
            "Glob",
        ],
    )
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
        # Error path: exit 1 + stderr message, no persistent systemMessage on stdout
        assert result.returncode == 1
        assert "Hook error" in result.stderr
        assert result.stdout.strip() == ""

    # --- Fix B: non-string / non-dict inputs must coerce to empty, not error ---

    def test_null_command_is_allowed(self) -> None:
        """null command coerces to '' → no rules fire → {}."""
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": None}})
        result = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output == {}, f"Expected {{}}, got {output!r}"

    def test_non_string_command_is_allowed(self) -> None:
        """Integer command coerces to '' → no rules fire → {}."""
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": 42}})
        result = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output == {}, f"Expected {{}}, got {output!r}"

    def test_non_dict_tool_input_is_allowed(self) -> None:
        """Non-dict tool_input coerces to {} → command = '' → no rules → {}."""
        payload = json.dumps({"tool_name": "Bash", "tool_input": "oops"})
        result = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output == {}, f"Expected {{}}, got {output!r}"
