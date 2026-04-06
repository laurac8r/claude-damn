#!/usr/bin/env bats
# Tests for checkpoint-save and checkpoint-resume SKILL.md archive behavior.
#
# These validate the shell commands the skills instruct the agent to run,
# confirming filesystem state matches the spec expectations for each of the
# 8 testing scenarios in:
#   docs/superpowers/specs/2026-04-05-checkpoint-archive-on-branch-change-design.md

# ── Helpers ──────────────────────────────────────────────────────────────

# Slugify a branch name per spec rules:
# lowercase, / → -, strip non-[a-z0-9-], collapse consecutive -
slugify() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | tr '/' '-' | sed 's/[^a-z0-9-]//g; s/-\{2,\}/-/g'
}

# Write a minimal CHECKPOINT.md with a Branch line
write_checkpoint() {
  local dir="${2:-.}"
  cat >"$dir/CHECKPOINT.md" <<EOF
# Checkpoint: Test

**Date:** 2026-04-05
**Branch:** \`$1\`
**Session context:** test checkpoint for branch $1

## Current State
- testing

## Next Steps
1. keep testing
EOF
}

# Resolve archive dir the way the skill instructs
resolve_archive() {
  local common_dir
  common_dir=$(git -C "$1" rev-parse --path-format=absolute --git-common-dir)
  echo "$(dirname "$common_dir")/.checkpoints"
}

# ── Setup / Teardown ────────────────────────────────────────────────────

setup() {
  TEST_DIR="$(mktemp -d)"
  REPO="$TEST_DIR/repo"
  mkdir -p "$REPO"
  git -C "$REPO" init -b main --quiet
  git -C "$REPO" commit --allow-empty -m "init" --quiet
}

teardown() {
  rm -rf "$TEST_DIR"
}

# ── Scenario 1: Branch-switch clobber (save Case B) ────────────────────

@test "scenario 1: save archives different-branch checkpoint to .checkpoints/<old-slug>.md" {
  # Save a checkpoint on main
  write_checkpoint "main" "$REPO"
  ARCHIVE=$(resolve_archive "$REPO")
  mkdir -p "$ARCHIVE"

  # Switch to feat-a
  git -C "$REPO" switch -c feat-a --quiet

  # Skill Step 4 Case B: existing CHECKPOINT.md branch (main) ≠ current (feat-a)
  # → move to .checkpoints/main.md
  mv "$REPO/CHECKPOINT.md" "$ARCHIVE/main.md"

  # Write new checkpoint for feat-a
  write_checkpoint "feat-a" "$REPO"

  # Assertions
  [ -f "$ARCHIVE/main.md" ]
  grep -q 'Branch.*main' "$ARCHIVE/main.md"
  [ -f "$REPO/CHECKPOINT.md" ]
  grep -q 'Branch.*feat-a' "$REPO/CHECKPOINT.md"
}

# ── Scenario 2: Same-branch iteration (save Case A) ───────────────────

@test "scenario 2: same-branch save copies to .checkpoints/<slug>.prev.md" {
  write_checkpoint "main" "$REPO"
  ARCHIVE=$(resolve_archive "$REPO")
  mkdir -p "$ARCHIVE"

  # Skill Step 4 Case A: same branch → copy to .prev.md
  cp "$REPO/CHECKPOINT.md" "$ARCHIVE/main.prev.md"

  # Overwrite with updated checkpoint
  write_checkpoint "main" "$REPO"
  echo "## Extra stuff" >>"$REPO/CHECKPOINT.md"

  # Assertions
  [ -f "$ARCHIVE/main.prev.md" ]
  # .prev.md should NOT have the extra stuff (it's the pre-save version)
  ! grep -q "Extra stuff" "$ARCHIVE/main.prev.md"
  # Current CHECKPOINT.md should have it
  grep -q "Extra stuff" "$REPO/CHECKPOINT.md"
}

# ── Scenario 3: Multi-worktree save (archive at main checkout root) ───

@test "scenario 3: worktree save archives to main checkout .checkpoints/" {
  # Create a worktree
  git -C "$REPO" switch -c feat-wt-x --quiet
  git -C "$REPO" switch main --quiet
  WT="$TEST_DIR/wt"
  git -C "$REPO" worktree add "$WT" feat-wt-x --quiet 2>/dev/null

  # Resolve archive from inside the worktree
  ARCHIVE=$(resolve_archive "$WT")
  MAIN_ARCHIVE=$(resolve_archive "$REPO")
  mkdir -p "$ARCHIVE"

  # Both should resolve to the same place: main checkout's .checkpoints/
  [ "$ARCHIVE" = "$MAIN_ARCHIVE" ]
  [[ "$ARCHIVE" == "$REPO/.checkpoints" ]]

  # Cleanup worktree
  git -C "$REPO" worktree remove "$WT" --force 2>/dev/null || true
}

# ── Scenario 4: Resume drift (resume Case B) ──────────────────────────

@test "scenario 4: resume detects branch mismatch and should prompt user" {
  # CHECKPOINT.md says main, but we're on feat-a
  write_checkpoint "main" "$REPO"
  git -C "$REPO" switch -c feat-a --quiet

  # Parse the Branch line
  ckpt_branch=$(sed -n 's/.*\*\*Branch:\*\* `\([^`]*\)`.*/\1/p' "$REPO/CHECKPOINT.md")
  current_branch=$(git -C "$REPO" branch --show-current)

  # Skill Step 4 Case B fires when these differ
  [ "$ckpt_branch" = "main" ]
  [ "$current_branch" = "feat-a" ]
  [ "$ckpt_branch" != "$current_branch" ]
}

# ── Scenario 5: Resume from archive match (resume Case C) ─────────────

@test "scenario 5: resume moves matching archive to CWD" {
  ARCHIVE=$(resolve_archive "$REPO")
  mkdir -p "$ARCHIVE"

  # No CHECKPOINT.md at CWD, but archive has one for current branch
  git -C "$REPO" switch -c feat-a --quiet
  write_checkpoint "feat-a" "$ARCHIVE"
  mv "$ARCHIVE/CHECKPOINT.md" "$ARCHIVE/feat-a.md"
  [ ! -f "$REPO/CHECKPOINT.md" ]

  # Skill Step 4 Case C: move (not copy) archive to CWD
  mv "$ARCHIVE/feat-a.md" "$REPO/CHECKPOINT.md"

  # Assertions: restored at CWD, gone from archive
  [ -f "$REPO/CHECKPOINT.md" ]
  [ ! -f "$ARCHIVE/feat-a.md" ]
  grep -q 'Branch.*feat-a' "$REPO/CHECKPOINT.md"
}

# ── Scenario 6: Pick-from-list (resume Case D) ────────────────────────

@test "scenario 6: resume lists archive when no slug match, archive non-empty" {
  ARCHIVE=$(resolve_archive "$REPO")
  mkdir -p "$ARCHIVE"

  # Create archives for other branches
  write_checkpoint "feature-x" "$ARCHIVE"
  mv "$ARCHIVE/CHECKPOINT.md" "$ARCHIVE/feature-x.md"
  write_checkpoint "bugfix-y" "$ARCHIVE"
  mv "$ARCHIVE/CHECKPOINT.md" "$ARCHIVE/bugfix-y.md"

  # Also create a .prev.md that should be excluded from listing
  echo "backup" >"$ARCHIVE/feature-x.prev.md"

  # No CHECKPOINT.md, on main (no main.md in archive)
  [ ! -f "$REPO/CHECKPOINT.md" ]
  [ ! -f "$ARCHIVE/main.md" ]

  # Enumerate: list *.md excluding *.prev.md
  candidates=()
  for f in "$ARCHIVE"/*.md; do
    case "$f" in
    *.prev.md) continue ;;
    *) candidates+=("$f") ;;
    esac
  done

  # Should find exactly 2 candidates, neither is a .prev.md
  [ "${#candidates[@]}" -eq 2 ]
  for c in "${candidates[@]}"; do
    [[ "$c" != *.prev.md ]]
  done
}

# ── Scenario 7: Archive collision (save Case B with -2 suffix) ────────

@test "scenario 7: archive collision appends -2 suffix" {
  ARCHIVE=$(resolve_archive "$REPO")
  mkdir -p "$ARCHIVE"

  # First archive of a main checkpoint already exists
  write_checkpoint "main" "$ARCHIVE"
  mv "$ARCHIVE/CHECKPOINT.md" "$ARCHIVE/main.md"

  # Now we have another CHECKPOINT.md from main to archive
  write_checkpoint "main" "$REPO"
  git -C "$REPO" switch -c other --quiet

  # Skill Step 4 Case B: old-slug is "main", but main.md exists → main-2.md
  old_slug="main"
  target="$ARCHIVE/${old_slug}.md"
  if [ -f "$target" ]; then
    n=2
    while [ -f "$ARCHIVE/${old_slug}-${n}.md" ]; do
      n=$((n + 1))
    done
    target="$ARCHIVE/${old_slug}-${n}.md"
  fi
  mv "$REPO/CHECKPOINT.md" "$target"

  # Assertions
  [ -f "$ARCHIVE/main.md" ]   # original untouched
  [ -f "$ARCHIVE/main-2.md" ] # collision suffixed
  grep -q 'Branch.*main' "$ARCHIVE/main-2.md"
}

# ── Scenario 8: .gitignore missing (save Step 3) ──────────────────────

@test "scenario 8: save appends .checkpoints/ to .gitignore when missing" {
  # Ensure no .gitignore exists
  rm -f "$REPO/.gitignore"

  COMMON_DIR=$(git -C "$REPO" rev-parse --path-format=absolute --git-common-dir)
  GITIGNORE="$(dirname "$COMMON_DIR")/.gitignore"

  # Skill Step 3: check and append if missing
  if ! grep -qF '.checkpoints/' "$GITIGNORE" 2>/dev/null; then
    echo ".checkpoints/" >>"$GITIGNORE"
  fi

  # Assertions
  [ -f "$GITIGNORE" ]
  grep -qF '.checkpoints/' "$GITIGNORE"
}

# ── Slug derivation ───────────────────────────────────────────────────

@test "slug: lowercase and replace slashes" {
  result=$(slugify "Feature/My-Branch")
  [ "$result" = "feature-my-branch" ]
}

@test "slug: strip non-alphanumeric-dash chars" {
  result=$(slugify "feat/some_thing!@#")
  [ "$result" = "feat-something" ]
}

@test "slug: collapse consecutive dashes" {
  result=$(slugify "feat//double--dash")
  [ "$result" = "feat-double-dash" ]
}

@test "slug: detached HEAD falls back to CWD basename" {
  # Simulate detached HEAD: git branch --show-current returns empty
  git -C "$REPO" checkout --detach --quiet
  branch=$(git -C "$REPO" branch --show-current)
  [ -z "$branch" ]

  # Fallback: use basename of CWD
  slug=$(slugify "$(basename "$REPO")")
  [ -n "$slug" ]
}