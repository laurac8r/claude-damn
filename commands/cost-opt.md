1. First, ensure logs exist by running: `python3 ~/.claude/cost-log/extract_cost.py --append-log --quiet`
2. Read the JSONL cost log files in `~/.claude/cost-log/*.jsonl` and the existing `~/.claude/cost-log/SUMMARY.md`.
3. Perform an efficient `/compact` summary on the log files (just changes since last summary) and update `SUMMARY.md`
   with the compacted summary including: total spend, spend by model, spend by project, busiest sessions, and trends.
4. Suggest cost optimizations based on the data — e.g., sessions where Opus was used for tasks that Sonnet could handle,
   high cache-creation ratios, or sessions with excessive turns.