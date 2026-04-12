#!/bin/zsh

# Sync Claude Code theme with macOS Light/Dark mode
# Triggered by LaunchAgent when ~/Library/Preferences/.GlobalPreferences.plist changes

set -euo pipefail

SETTINGS="${SETTINGS:-$HOME/.claude/settings.json}"

# Detect macOS appearance
if defaults read -g AppleInterfaceStyle &>/dev/null; then
  THEME="dark"
else
  THEME="light"
fi

# Bail if settings.json doesn't exist
if [[ ! -f "$SETTINGS" ]]; then
  exit 0
fi

# Backup before any write — allows restore on failure
cp "$SETTINGS" "${SETTINGS}.bak"

# Restore helper: copy backup over corrupted file
restore_from_backup() {
  if [[ -f "${SETTINGS}.bak" ]]; then
    cp "${SETTINGS}.bak" "$SETTINGS"
  fi
}

# Update theme in settings.json
# IMPORTANT: Write in-place (not via tmp+mv) so that kqueue/fsevents watchers
# on the existing inode fire and active Claude Code sessions pick up the change.
if command -v jq &>/dev/null; then
  CURRENT=$(jq -r '.themePreference // empty' "$SETTINGS")
  if [[ "$CURRENT" != "$THEME" ]]; then
    CONTENT=$(jq --arg t "$THEME" '.themePreference = $t' "$SETTINGS")

    # Guard: validate output before writing
    if [[ -z "$CONTENT" ]]; then
      restore_from_backup
      exit 1
    fi
    if ! echo "$CONTENT" | jq empty &>/dev/null; then
      restore_from_backup
      exit 1
    fi

    printf '%s\n' "$CONTENT" > "$SETTINGS"

    # Verify file is still valid after write
    if ! jq empty "$SETTINGS" &>/dev/null; then
      restore_from_backup
      exit 1
    fi
  fi
else
  # Fallback: python3 (always available on macOS)
  python3 -c "
import json, sys
settings_path = '$SETTINGS'
try:
    with open(settings_path) as f:
        data = json.load(f)
    if data.get('themePreference') != '$THEME':
        data['themePreference'] = '$THEME'
        with open(settings_path, 'w') as f:
            json.dump(data, f, indent=2)
            f.write('\n')
except Exception as e:
    print(f'sync-theme: python3 fallback error: {e}', file=sys.stderr)
    sys.exit(1)
"
  # If python3 failed, restore
  if [[ $? -ne 0 ]]; then
    restore_from_backup
    exit 1
  fi
fi