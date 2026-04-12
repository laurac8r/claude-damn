#!/usr/bin/env bash
# Run the test plan in isolated git worktrees under /tmp, in parallel.
#
# Each suite gets its own worktree so that uv's per-project .venv, pytest
# caches, and any filesystem side-effects stay off the live checkout. On
# exit (success or failure) the worktrees are torn down.
#
# Suites:
#   ruff    — `uv run ruff check` + `uv run ruff format --check`
#   pytest  — `uv run pytest`
#   bats    — the two .bats files under tests/
#
# Usage:
#   scripts/test-isolated.sh              # run all suites
#   scripts/test-isolated.sh ruff pytest  # run a subset
#   KEEP=1 scripts/test-isolated.sh       # leave worktrees behind for inspection
#
# Written for bash 3.2 (macOS default) — no associative arrays.

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
REF="$(git -C "$REPO_ROOT" rev-parse HEAD)"
TMP_BASE="/tmp/claude-damn-test"
LOG_DIR="$TMP_BASE/logs"
mkdir -p "$LOG_DIR"

suite_command() {
  case "$1" in
  ruff) echo "uv run ruff check . && uv run ruff format --check ." ;;
  pytest) echo "uv run pytest" ;;
  bats) echo "bats tests/test_checkpoint_archive.bats tests/test_sync_theme.bats" ;;
  *) return 1 ;;
  esac
}

if [ "$#" -eq 0 ]; then
  set -- ruff pytest bats
fi
suites=("$@")

cleanup() {
  if [ "${KEEP:-0}" = "1" ]; then
    echo "KEEP=1 — leaving worktrees at $TMP_BASE-*" >&2
    return
  fi
  for suite in "${suites[@]}"; do
    git -C "$REPO_ROOT" worktree remove --force "$TMP_BASE-$suite" 2>/dev/null || true
  done
  git -C "$REPO_ROOT" worktree prune
}
trap cleanup EXIT

pids=()
names=()
for suite in "${suites[@]}"; do
  cmd="$(suite_command "$suite")" || {
    echo "unknown suite: $suite" >&2
    exit 2
  }
  wt="$TMP_BASE-$suite"
  rm -rf "$wt"
  git -C "$REPO_ROOT" worktree add --detach "$wt" "$REF" >/dev/null
  # Propagate uncommitted working-tree changes (staged + unstaged + untracked)
  # so the worktree reflects what's actually being tested, not just HEAD.
  if ! git -C "$REPO_ROOT" diff HEAD --quiet; then
    git -C "$REPO_ROOT" diff HEAD --binary | git -C "$wt" apply --whitespace=nowarn
  fi
  # Copy untracked-but-not-ignored files too (e.g. new test files).
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    mkdir -p "$wt/$(dirname "$f")"
    cp "$REPO_ROOT/$f" "$wt/$f"
  done < <(git -C "$REPO_ROOT" ls-files --others --exclude-standard)
  log="$LOG_DIR/$suite.log"
  (cd "$wt" && eval "$cmd") >"$log" 2>&1 &
  pids+=("$!")
  names+=("$suite")
done

fail=0
n=${#pids[@]}
for ((i = 0; i < n; i++)); do
  if wait "${pids[$i]}"; then
    printf '  PASS  %s\n' "${names[$i]}"
  else
    printf '  FAIL  %s  (log: %s)\n' "${names[$i]}" "$LOG_DIR/${names[$i]}.log"
    fail=1
  fi
done

if [ "$fail" -ne 0 ]; then
  echo
  echo "--- tail of each log ---"
  for name in "${names[@]}"; do
    echo "=== $name ==="
    tail -30 "$LOG_DIR/$name.log" 2>/dev/null | sed "s|^|[$name] |"
  done
fi

exit "$fail"