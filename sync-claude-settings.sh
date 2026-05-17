#!/usr/bin/env bash
# Sync ~/.claude/settings.local.json from the canonical ~/.claude/settings.json.
#
# Canonical is source of truth. Local is overwritten byte-for-byte.
# The prior local file is moved to the system Trash via /usr/bin/trash
# (recoverable delete per user's iron rule — never rm).
#
# Usage:
#   ~/.claude/sync-claude-settings.sh          # sync
#   ~/.claude/sync-claude-settings.sh --dry    # show diff, do nothing
#   ~/.claude/sync-claude-settings.sh --diff   # alias for --dry

set -euo pipefail

CANONICAL="$HOME/.claude/settings.json"
LOCAL="$HOME/.claude/settings.local.json"
TRASH_BIN="/usr/bin/trash"

crash-landing() {
  printf 'sync-claude-settings: %s\n' "$*" >&2
  exit 1
}

[[ -f "$CANONICAL" ]] || crash-landing "canonical missing: $CANONICAL"

# Validate canonical is parseable JSON before we touch local.
if command -v python3 >/dev/null 2>&1; then
  python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$CANONICAL" \
    || crash-landing "canonical is not valid JSON: $CANONICAL"
fi

mode="sync"
case "${1:-}" in
  --dry | --diff) mode="dry" ;;
  "") ;;
  *) crash-landing "unknown flag: $1 (use --dry or --diff)" ;;
esac

if [[ ! -f "$LOCAL" ]]; then
  printf 'local missing — will create fresh copy from canonical.\n'
  [[ "$mode" == "dry" ]] && {
    printf '(dry run — no write)\n'
    exit 0
  }
  cp "$CANONICAL" "$LOCAL"
  printf 'wrote %s\n' "$LOCAL"
  exit 0
fi

if cmp -s "$CANONICAL" "$LOCAL"; then
  printf 'already in sync — nothing to do.\n'
  exit 0
fi

printf 'diff (canonical → local):\n'
diff -u "$LOCAL" "$CANONICAL" || true

if [[ "$mode" == "dry" ]]; then
  printf '\n(dry run — no write)\n'
  exit 0
fi

printf '\nproceed with overwrite? [y/N] '
read -r ans
[[ "$ans" =~ ^[Yy]$ ]] || crash-landing "aborted by user"

# Recoverable delete of the old local file — trash, not rm.
if [[ -x "$TRASH_BIN" ]]; then
  "$TRASH_BIN" "$LOCAL"
else
  crash-landing "trash not found at $TRASH_BIN — refusing to overwrite without recoverable backup"
fi

cp "$CANONICAL" "$LOCAL"
printf 'wrote %s  (prior file moved to Trash)\n' "$LOCAL"
