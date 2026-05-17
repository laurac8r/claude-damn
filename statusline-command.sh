#!/usr/bin/env bash
# Claude Code statusLine command — styled after the robbyrussell Oh My Zsh theme
# Receives JSON on stdin with session context

input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // empty')
basename_dir=$(basename "$cwd")

model=$(echo "$input" | jq -r '.model.display_name // empty')

# Git branch and dirty state (skip optional locks so we never block the prompt)
git_branch=""
git_dirty=""
if git -C "$cwd" rev-parse --git-dir --no-optional-locks >/dev/null 2>&1; then
  git_branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null || git -C "$cwd" --no-optional-locks rev-parse --short HEAD 2>/dev/null)
  if ! git -C "$cwd" --no-optional-locks diff --quiet 2>/dev/null || ! git -C "$cwd" --no-optional-locks diff --cached --quiet 2>/dev/null; then
    git_dirty="1"
  fi
fi

# Context window remaining
remaining=$(echo "$input" | jq -r '.context_window.remaining_percentage // empty')

# Build output with ANSI colors matching robbyrussell palette
# cyan for directory, bold blue + red for git, dim for model/context
CYAN='\033[0;36m'
BOLD_BLUE='\033[1;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
DIM='\033[2m'
RESET='\033[0m'
# robbyrussell uses bold blue for the closing paren too

parts=""

# Directory (cyan, basename like robbyrussell)
parts+=$(printf "${CYAN}%s${RESET}" "$basename_dir")

# Git branch (bold blue with red branch name, matching robbyrussell)
# Dirty state: yellow ✗ when working tree or index has changes
if [ -n "$git_branch" ]; then
  if [ -n "$git_dirty" ]; then
    parts+=$(printf "  ${BOLD_BLUE}git:(${RED}%s${BOLD_BLUE}) ${YELLOW}✗${RESET}" "$git_branch")
  else
    parts+=$(printf "  ${BOLD_BLUE}git:(${RED}%s${BOLD_BLUE})${RESET}" "$git_branch")
  fi
fi

# Model (dim)
if [ -n "$model" ]; then
  parts+=$(printf "  ${DIM}%s${RESET}" "$model")
fi

# Context remaining (dim, only when available)
if [ -n "$remaining" ]; then
  parts+=$(printf "  ${DIM}ctx:%s%%${RESET}" "$(printf '%.0f' "$remaining")")
fi

# Session cost estimate from cumulative token counts
# Pricing (per million tokens): input $3, output $15, cache_creation $3.75, cache_read $0.30
total_in=$(echo "$input" | jq -r '.context_window.total_input_tokens // 0')
total_out=$(echo "$input" | jq -r '.context_window.total_output_tokens // 0')
cache_create=$(echo "$input" | jq -r '.context_window.current_usage.cache_creation_input_tokens // 0')
cache_read=$(echo "$input" | jq -r '.context_window.current_usage.cache_read_input_tokens // 0')

if [ "$total_in" != "0" ] || [ "$total_out" != "0" ]; then
  cost=$(awk "BEGIN {
    in_cost  = $total_in   / 1000000 * 3.00;
    out_cost = $total_out  / 1000000 * 15.00;
    cc_cost  = $cache_create / 1000000 * 3.75;
    cr_cost  = $cache_read   / 1000000 * 0.30;
    total    = in_cost + out_cost + cc_cost + cr_cost;
    printf \"\$%.4f\", total
  }")
  parts+=$(printf "  ${DIM}%s${RESET}" "$cost")
fi

printf "%s" "$parts"
