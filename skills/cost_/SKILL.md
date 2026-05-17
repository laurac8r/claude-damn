---
name: cost_
description: Extract and log cost data for the current session.
user-invocable: true
---

Extract and log cost data for the current session.

1. Run
   `python3 ~/.claude/src/extract_cost.py --latest ~/.claude/projects/$(echo "$PWD" | sed 's|/|-|g' | sed 's|^-||') --append-log`
   to extract cost data from the current project's latest session and log it.

   **Fallback if the script isn't at that path** (it's been moved before):

   ```
   find ~/.claude -maxdepth 3 -name 'extract_cost.py' -not -path '*/__pycache__/*'
   ```

   Use whichever path the find returns. The canonical location is
   `~/.claude/src/extract_cost.py`; older docs (e.g. CLAUDE.md text in
   worktrees) may still reference `~/.claude/extract_cost.py`.

2. If the project directory mapping fails, find the correct project dir by
   listing `~/.claude/projects/` and matching the current working directory.
3. Display a concise summary: total cost, model breakdown, token counts, and
   turns.
4. Format as a compact table for readability.
