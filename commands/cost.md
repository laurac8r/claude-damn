Extract and log cost data for the current session.

1. Run
   `python3 ~/.claude/cost-log/extract_cost.py --latest ~/.claude/projects/$(echo "$PWD" | sed 's|/|-|g' | sed 's|^-||') --append-log`
   to extract cost data from the current project's latest session and log it.
2. If the project directory mapping fails, find the correct project dir by listing `~/.claude/projects/` and matching
   the current working directory.
3. Display a concise summary: total cost, model breakdown, token counts, and turns.
4. Format as a compact table for readability.