"""Regression tests: settings.json structure and required values."""

import pytest


class TestRequiredKeys:
    """Ensure all top-level keys exist and have correct types."""

    def test_has_permissions_block(self, settings: dict) -> None:
        assert "permissions" in settings

    def test_has_model(self, settings: dict) -> None:
        assert "model" in settings

    def test_has_hooks(self, settings: dict) -> None:
        assert "hooks" in settings

    def test_has_enabled_plugins(self, settings: dict) -> None:
        assert "enabledPlugins" in settings

    def test_has_status_line(self, settings: dict) -> None:
        assert "statusLine" in settings

    def test_respects_gitignore(self, settings: dict) -> None:
        assert settings["respectGitignore"] is True


class TestPermissionsStructure:
    """Ensure permissions has allow/deny/ask lists and a default mode."""

    def test_has_allow_list(self, permissions: dict) -> None:
        assert isinstance(permissions["allow"], list)

    def test_has_deny_list(self, permissions: dict) -> None:
        assert isinstance(permissions["deny"], list)

    def test_has_ask_list(self, permissions: dict) -> None:
        assert isinstance(permissions["ask"], list)

    def test_default_mode_is_default(self, permissions: dict) -> None:
        assert permissions["defaultMode"] == "default"

    def test_allow_list_not_empty(self, allow_list: list[str]) -> None:
        assert len(allow_list) > 0

    def test_deny_list_not_empty(self, deny_list: list[str]) -> None:
        assert len(deny_list) > 0


class TestHooksStructure:
    """Ensure PreToolUse hook for inline script blocking is configured."""

    def test_has_pre_tool_use(self, settings: dict) -> None:
        assert "PreToolUse" in settings["hooks"]

    def test_pre_tool_use_has_bash_matcher(self, settings: dict) -> None:
        hooks = settings["hooks"]["PreToolUse"]
        matchers = [h["matcher"] for h in hooks]
        assert "Bash" in matchers

    def test_bash_hook_runs_block_script(self, settings: dict) -> None:
        hooks = settings["hooks"]["PreToolUse"]
        bash_hook = next(h for h in hooks if h["matcher"] == "Bash")
        commands = [hk["command"] for hk in bash_hook["hooks"]]
        assert any("block-inline-scripts" in cmd for cmd in commands)

    def test_bash_hook_has_timeout(self, settings: dict) -> None:
        hooks = settings["hooks"]["PreToolUse"]
        bash_hook = next(h for h in hooks if h["matcher"] == "Bash")
        for hk in bash_hook["hooks"]:
            assert "timeout" in hk
            assert hk["timeout"] <= 30  # hooks must be fast


class TestStatusLine:
    """Ensure status line is command-based and points to the right script."""

    def test_type_is_command(self, settings: dict) -> None:
        assert settings["statusLine"]["type"] == "command"

    def test_command_references_script(self, settings: dict) -> None:
        cmd = settings["statusLine"]["command"]
        assert "statusline-command.sh" in cmd


class TestPluginDefaults:
    """Ensure critical plugins stay enabled and problematic ones stay disabled."""

    @pytest.mark.parametrize("plugin", [
        "code-review@claude-plugins-official",
        "commit-commands@claude-plugins-official",
        "pr-review-toolkit@claude-plugins-official",
        "security-guidance@claude-plugins-official",
        "hookify@claude-plugins-official",
    ])
    def test_critical_plugins_enabled(
            self, enabled_plugins: dict[str, bool], plugin: str
    ) -> None:
        assert enabled_plugins.get(plugin) is True, f"{plugin} must be enabled"

    @pytest.mark.parametrize("plugin", [
        "explanatory-output-style@claude-plugins-official",
        "ralph-loop@claude-plugins-official",
    ])
    def test_noisy_plugins_not_enabled(
            self, enabled_plugins: dict[str, bool], plugin: str
    ) -> None:
        # These plugins should either be absent or explicitly False
        assert enabled_plugins.get(plugin) is not True, f"{plugin} must not be enabled"
