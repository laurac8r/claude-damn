# Iteration 1 — RED baseline results

| Eval                   | Quant | Pressure (rationalization captured?)                         |
| ---------------------- | ----- | ------------------------------------------------------------ |
| bare-simple            | FAIL  | Yes — R1                                                     |
| bare-pressure          | PASS  | None — agent correctly TaskCreated all 4 despite prior prose |
| update-noarg-reconcile | FAIL  | Yes — R2                                                     |
| update-witharg-rewrite | FAIL  | Yes — R3                                                     |
| display-fulllist       | PASS  | None — agent correctly enumerated all 20 via TaskGet         |

**3 of 5 baselines failed.** Iron Law gate satisfied: rationalizations exist for
at least 3 scenarios, so the skill is justified.

The 2 passing baselines (bare-pressure, display-fulllist) tell us the skill body
should NOT over-correct — modern Sonnet already handles those instincts.

## Captured rationalizations

### R1 — "Skill not available → echo + ask"

_From bare-simple baseline._

> "The `/task-list` skill is not available in this session. Here is the task
> queue you listed: ... Would you like me to proceed with these steps now?"

The agent treats `/task-list` as a slash-command invocation of a non-existent
skill, halts execution, echoes the list back as plain text, and asks for
permission. It does NOT default to TaskCreate even though the directive is
unambiguous.

### R2 — "Skill doesn't exist → flag unknown command + defer"

_From update-noarg-reconcile baseline._

> "`/task-list` is not a recognized skill in the current session... If you'd
> like, I can apply those changes now using the TaskCreate/TaskUpdate tools
> directly. Just confirm and I'll proceed."

The agent INFERS the reconcile semantic correctly from session context, then
DEFERS execution behind a confirmation prompt. The skill body must collapse
"infer + propose + ask" into "infer + execute."

### R3 — "Conservative-but-incomplete: inferred but declined"

_From update-witharg-rewrite baseline._

> "Without the skill, I cannot execute that automatically. Would you like me to
> proceed with the actual version bump work instead, or do you want to surface
> the skill first?"

The agent inferred the rewrite semantic correctly but routed it through a
permission prompt instead of calling TaskUpdate — even offering to do unrelated
work rather than the requested operation. The skill body must license the agent
to act on unambiguous syntax without permission-seeking.

## Pre-existing rationalization (memory-documented, not re-observed)

### R0 — "Already tracking in prose markdown"

_From feedback_reconcile_skill_created_tasks.md memory._

> When a skill auto-creates tasks, drive them with TaskUpdate as work
> progresses; don't ignore system-reminder nudges or run a parallel text
> checklist.

NOT observed in iteration-1 baseline (bare-pressure agent passed cleanly), but
pre-emptively counter in the skill body since the failure mode is documented
from prior sessions.

## Implications for skill body

1. **Lead with action verbs, not "consider whether."** Skill body must say "call
   TaskCreate" / "call TaskUpdate" — not "you may want to call."
2. **Anti-pattern: ask-before-act.** Explicitly flag the "would you like me to
   proceed?" rationalization (R1, R2) as forbidden when syntax is unambiguous.
3. **Anti-pattern: prose-list substitute.** Pre-emptively counter R0 even though
   baseline didn't trigger it.
4. **Preserve the passing instincts.** Don't over-instruct on enumeration logic
   for `--display` — Sonnet already handles it. Just affirm "render all without
   truncation, no mutation."
5. **Flag semantics must be tight.** `--update` (no arg) vs
   `--update <#> :: <new>` need crisp examples; baselines show agents inferred
   correctly but didn't act, so semantics aren't the gap — execution licensing
   is.
