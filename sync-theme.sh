#!/bin/zsh

# Sync Claude Code theme with macOS Light/Dark mode
# Triggered by LaunchAgent when ~/Library/Preferences/.GlobalPreferences.plist changes

SETTINGS="$HOME/.claude/settings.json"

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

# Update theme in settings.json
# IMPORTANT: Write in-place (not via tmp+mv) so that kqueue/fsevents watchers
# on the existing inode fire and active Claude Code sessions pick up the change.
if command -v jq &>/dev/null; then
  CURRENT=$(jq -r '.themePreference // empty' "$SETTINGS")
  if [[ "$CURRENT" != "$THEME" ]]; then
    local CONTENT=$(jq --arg t "$THEME" '.themePreference = $t' "$SETTINGS")
    printf '%s\n' "$CONTENT" > "$SETTINGS"
  fi
else
  # Fallback: python3 (always available on macOS) — already writes in-place
  python3 -c "
import json, sys
with open('$SETTINGS') as f:
    data = json.load(f)
if data.get('themePreference') != '$THEME':
    data['themePreference'] = '$THEME'
    with open('$SETTINGS', 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')
"
fi