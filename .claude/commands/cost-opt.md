1. First, ensure logs exist by running: `python3 ~/.claude/extract_cost.py --append-log --quiet`
2. Read the JSONL cost log files in `~/.claude/cost-log/*.jsonl` and the existing `~/.claude/cost-log/SUMMARY.md`.
3. Perform an efficient `/compact` summary on the log files (just changes since last summary) and update `SUMMARY.md`
   with the compacted summary including: total spend, spend by model, spend by project, busiest sessions, and trends.
4. Suggest cost optimizations based on the data — e.g., sessions where Opus was used for tasks that Sonnet could handle,
   high cache-creation ratios, or sessions with excessive turns.
5. **Ignore and filter out** work done on the `~/.claude` and `~/.awesome` directories, in the cost analysis, summary
   and recommendations.
6. **Formatting rule — escape dollar signs:** In prose sections (bullet points, numbered lists, paragraphs),
   always write `\$` instead of bare `$` to prevent Markdown renderers from interpreting `$...$` as LaTeX math.
   Dollar signs inside tables and fenced code blocks do NOT need escaping. Never break a dollar amount across lines.