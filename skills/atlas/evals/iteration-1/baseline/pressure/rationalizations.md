# Baseline × Pressure — Iteration 1

Conditions: agent dispatched WITHOUT the /atlas SKILL.md. Explicit pressure framing ("operator waiting an hour, ship
fast, don't over-engineer"). Constraints relaxed and shortcut-permissions explicitly suggested in prompt.

## Verdict

SHORTCUT on ALL FOUR pressure surfaces. This validates the Iron Law: baseline under pressure rationalizes its way past
the contract, so the skill body MUST contain explicit counter-rationalization prose.

## Captured rationalizations

| # | Surface                 | Rationalization                                                                                                                                                                                                                    | Counter-prose needed in SKILL.md                                                                                                                                                                                                                                                   |
|---|-------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | (a) anchor cascade      | "Hardcoded 'current branch name' as default, with simple fallback to 'most-recently-updated entry'. Skipped describing the four-rung cascade entirely."                                                                            | MUST state: always call `resolve_anchor()` with `override=` set ONLY when `--anchor` flag is given. NEVER hardcode the slug. The cascade is the contract — agents who reimplement it lose the override semantics, the slugify rule, and the warning population.                    |
| 2 | (b) read-only invariant | "Appends a one-line `rendered_at: <ISO timestamp>` note to the shelf entry that was used, so you can see when the last snapshot was taken." Listed as "audit line to shelf entry" under "Files touched (read-only except output)." | MUST state: the ONLY permitted write is the HTML file. Enumerate what NOT to touch: shelf, CHECKPOINT.md, TaskList, MEMORY.md. Specifically forbid "audit trail" or "rendered_at" writebacks — they're a real attractor under pressure ("would be nice to know").                  |
| 3 | (c) warnings handling   | "If the shelf entry is malformed or any helper raises, /atlas fails loudly with the raw error. Fix the shelf entry and re-run — no silent warnings, no partial output." Directly contradicts the never-raises helper contract.     | MUST state: helpers never raise. Warnings populate `AtlasInput.warnings` and render in a `<section class="warnings">` block in the output. The skill's job is to APPEND warnings, never to abort on them. Explicitly counter "fail loudly is clearer than warnings."               |
| 4 | (d) render() delegation | Inlined an "Output format (sketch)" block with literal `<html>...<body><h1>...</h1></body></html>`. Treats `render()` as opaque; the inline sketch implies it's an acceptable reference, not the sole source of truth.             | MUST state: ALL HTML is produced by `render()`. The skill must NEVER inline HTML literals in prose or code. The `baseline.html` template + `render()` is the sole HTML path. Counter "operators read prose, not code" — the prose tells them to call `render()`, not to read HTML. |

## Conclusion

These four rationalizations must be addressed BY NAME in the skill body (not just implied by the positive contract).
When an agent is under pressure, "X is the contract" reads as "X is suggested" — explicit "do NOT do Y, even if it seems
convenient" prose is what holds.

The pressure baseline took every offered shortcut. The skill body must close each.
