#!/usr/bin/env bats
# Tests for sync-theme.sh — the LaunchAgent script that syncs
# Claude Code's themePreference with macOS Light/Dark mode.
#
# The script must respect SETTINGS env var for testability.
# If SETTINGS is set, it uses that path; otherwise defaults to
# $HOME/.claude/settings.json.

SCRIPT="$BATS_TEST_DIRNAME/../src/sync-theme.sh"
REAL_JQ="$(command -v jq)"

setup() {
  TEST_DIR="$(mktemp -d)"
  export TEST_SETTINGS="$TEST_DIR/settings.json"

  # Write a valid baseline settings.json
  cat >"$TEST_SETTINGS" <<'JSON'
{
  "respectGitignore": true,
  "permissions": {
    "allow": ["Read(.)"],
    "deny": ["Bash(*git commit *)"],
    "defaultMode": "default"
  },
  "model": "opus[1m]",
  "hooks": {},
  "enabledPlugins": {},
  "statusLine": {
    "type": "command",
    "command": "bash statusline-command.sh"
  },
  "themePreference": "light"
}
JSON
}

teardown() {
  rm -rf "$TEST_DIR"
}

# Helper: get MD5 of file content (for change detection)
file_hash() {
  md5 -q "$1"
}

# ---------- Regression: no `local` outside functions ----------

@test "script does not use 'local' keyword at top level" {
  # Simple and robust: the script should have zero `local` keywords
  # since it has no functions. If functions are added later, this
  # test can be refined.
  run grep -c '^[[:space:]]*local ' "$SCRIPT"
  [ "$output" -eq 0 ]
}

# ---------- Script respects SETTINGS env var ----------

@test "script uses SETTINGS env var when set" {
  run grep -E 'SETTINGS=.*\$\{SETTINGS:-' "$SCRIPT"
  [ "$status" -eq 0 ]
}

# ---------- Backup creation ----------

@test "backup file is created before writing" {
  SETTINGS="$TEST_SETTINGS" run /bin/zsh "$SCRIPT"
  [ -f "${TEST_SETTINGS}.bak" ]
}

# ---------- Happy path: theme changes, other settings preserved ----------

@test "theme value updates while preserving all other settings" {
  SETTINGS="$TEST_SETTINGS" run /bin/zsh "$SCRIPT"
  [ "$status" -eq 0 ]

  # File must still be valid JSON
  run "$REAL_JQ" empty "$TEST_SETTINGS"
  [ "$status" -eq 0 ]

  # All original keys must be present
  run "$REAL_JQ" 'keys' "$TEST_SETTINGS"
  [[ "$output" == *"respectGitignore"* ]]
  [[ "$output" == *"permissions"* ]]
  [[ "$output" == *"model"* ]]
  [[ "$output" == *"hooks"* ]]
  [[ "$output" == *"enabledPlugins"* ]]
  [[ "$output" == *"statusLine"* ]]
  [[ "$output" == *"themePreference"* ]]

  # Nested values must survive
  run "$REAL_JQ" -r '.model' "$TEST_SETTINGS"
  [ "$output" = "opus[1m]" ]
}

# ---------- Guard: empty jq output triggers restore ----------

@test "restores from backup when jq produces empty output" {
  HASH_BEFORE=$(file_hash "$TEST_SETTINGS")

  # Create a wrapper that returns empty for the write call
  FAKE_JQ="$TEST_DIR/jq"
  cat >"$FAKE_JQ" <<FAKE
#!/bin/zsh
# theme-setting call: return empty string
if [[ "\$*" == *"--arg"* ]]; then
    echo ""
    exit 0
fi
# all other calls: delegate to real jq
exec "$REAL_JQ" "\$@"
FAKE
  chmod +x "$FAKE_JQ"

  SETTINGS="$TEST_SETTINGS" PATH="$TEST_DIR:$PATH" run /bin/zsh "$SCRIPT"

  # File must still be valid JSON with original content
  run "$REAL_JQ" -r '.model' "$TEST_SETTINGS"
  [ "$output" = "opus[1m]" ]
}

# ---------- Guard: invalid JSON output triggers restore ----------

@test "restores from backup when jq produces invalid JSON" {
  FAKE_JQ="$TEST_DIR/jq"
  cat >"$FAKE_JQ" <<FAKE
#!/bin/zsh
if [[ "\$*" == *"--arg"* ]]; then
    echo "NOT VALID JSON {{{{"
    exit 0
fi
exec "$REAL_JQ" "\$@"
FAKE
  chmod +x "$FAKE_JQ"

  SETTINGS="$TEST_SETTINGS" PATH="$TEST_DIR:$PATH" run /bin/zsh "$SCRIPT"

  # File must still be valid JSON with original content
  run "$REAL_JQ" -r '.model' "$TEST_SETTINGS"
  [ "$output" = "opus[1m]" ]
}

# ---------- Guard: python3 fallback preserves settings ----------

@test "python3 fallback preserves settings when jq is unavailable" {
  # Hide jq from PATH by creating a dir with no jq
  CLEAN_DIR="$TEST_DIR/clean_bin"
  mkdir -p "$CLEAN_DIR"
  # Symlink only essential commands (not jq)
  for cmd in python3 defaults; do
    CMD_PATH="$(command -v "$cmd" 2>/dev/null)"
    if [ -n "$CMD_PATH" ]; then
      ln -s "$CMD_PATH" "$CLEAN_DIR/$cmd"
    fi
  done

  SETTINGS="$TEST_SETTINGS" PATH="$CLEAN_DIR:/usr/bin:/bin" run /bin/zsh "$SCRIPT"

  [ "$status" -eq 0 ]

  # File must still be valid JSON
  run "$REAL_JQ" empty "$TEST_SETTINGS"
  [ "$status" -eq 0 ]

  # All keys preserved
  run "$REAL_JQ" -r '.model' "$TEST_SETTINGS"
  [ "$output" = "opus[1m]" ]
}

# ---------- Plist uses correct shell ----------

@test "LaunchAgent plist uses /bin/zsh not /bin/bash" {
  PLIST="$HOME/Library/LaunchAgents/com.claude.sync-theme.plist"
  [ -f "$PLIST" ]

  run grep '/bin/zsh' "$PLIST"
  [ "$status" -eq 0 ]

  # Must NOT reference /bin/bash
  run grep '/bin/bash' "$PLIST"
  [ "$status" -ne 0 ]
}
