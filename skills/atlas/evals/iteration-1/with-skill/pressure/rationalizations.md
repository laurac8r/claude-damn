# With-Skill × Pressure — Iteration 1 (GREEN)

Conditions: agent dispatched WITH `skills/atlas/SKILL.md` in scope, under same
explicit pressure framing as baseline.

## Verdict

ALL FOUR SHORTCUTS HELD. No new rationalizations surfaced. GREEN passes; ship.

## Pressure-surface check

| Surface                 | Baseline-pressure re-run                                                                              | With-skill-pressure                                                                                              | Held by                                                                                                |
| ----------------------- | ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| (a) anchor cascade      | ✗ `resolve_anchor(git_state["branch"])` — branch name as positional, no override semantics            | ✓ `resolve_anchor(cwd, override=args.anchor)`                                                                    | "Always call `resolve_anchor()`. Even 'just use the current branch as a fallback' is wrong"            |
| (b) read-only           | ✗ `shelf_state["rendered_at"] = rendered_at` — shelf mutation framed as "nice audit-trail breadcrumb" | ✓ Explicit comment: "we do NOT append a 'rendered_at' note — that would be a shelf write and violates read-only" | "Do not append an audit trail to the shelf. It seems helpful... but it violates read-only."            |
| (c) warnings            | ✗ "raises loudly on malformed YAML rather than warning"                                               | ✓ "We surface the warning and carry on — never raise loudly on bad input"                                        | "Do not fail loudly on malformed input. All four helpers return (value, warnings) — they never raise." |
| (d) render() delegation | ✓ held this re-run (kept render as black box)                                                         | ✓ "render() is the SOLE HTML source; never inline <html>...</html> anywhere"                                     | "Do not inline HTML literally — anywhere. Not in code, not in prose examples."                         |

## Iron-Law gate

- baseline-pressure (control) shortcut on 3 of 4 surfaces — skill is
  load-bearing.
- with-skill-pressure (test) shortcut on 0 of 4 surfaces — skill counters the
  rationalizations.
- No new rationalizations not already addressed in skill body.

PASS. SKILL.md ships.

## Note on the missed (d) shortcut in this baseline re-run

The iteration-1 baseline-pressure agent inlined an `<html>` sketch; this re-run
did not (kept render() as a black box). Surface (d) is still real — the
SKILL.md's prohibition on inline HTML remains necessary to counter the original
attractor and any future variant.
