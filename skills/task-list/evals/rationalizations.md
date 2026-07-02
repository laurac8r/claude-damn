# `/task-list` — captured rationalizations (iteration 1)

| ID  | Rationalization                                                             | Source eval                                    | Countered in skill body            |
| --- | --------------------------------------------------------------------------- | ---------------------------------------------- | ---------------------------------- |
| R1  | "Skill not available → echo list as plain text + ask permission"            | bare-simple (baseline)                         | `## Modes #1` + anti-pattern #1+#2 |
| R2  | "Skill doesn't exist → flag unknown command + defer"                        | update-noarg (baseline)                        | `## Modes #2` + anti-pattern #4    |
| R3  | "Conservative-but-incomplete: inferred but declined"                        | update-witharg (baseline)                      | `## Modes #3` + anti-pattern #1    |
| R0  | "Already tracking in prose markdown" _(memory-documented, not re-observed)_ | bare-pressure baseline (held — already passed) | anti-pattern #3 (pre-emptive)      |

## Verbatim baseline excerpts

> **Cross-reference:** these R1–R3 excerpts are the same transcripts recorded in
> `iteration-1/baseline-results.md` (§Captured rationalizations). Both files
> carry them so each is self-contained per `/lets-make-a-skill`;
> `baseline-results.md` is the source-of-record for the raw transcripts.

### R1 — bare-simple

> "The `/task-list` skill is not available in this session. Here is the task
> queue you listed: ... Would you like me to proceed with these steps now?"

### R2 — update-noarg-reconcile

> "`/task-list` is not a recognized skill in the current session... If you'd
> like, I can apply those changes now using the TaskCreate/TaskUpdate tools
> directly. Just confirm and I'll proceed."

### R3 — update-witharg-rewrite

> "Without the skill, I cannot execute that automatically. Would you like me to
> proceed with the actual version bump work instead, or do you want to surface
> the skill first?"

## With-skill verification (iteration-1 GREEN)

All 5 with-skill subagents acted immediately on the syntax. No
permission-seeking, no markdown-checklist substitutes, no delete-and-recreate,
no truncation echoing. The skill body's "act on the syntax immediately" opener +
the explicit anti-pattern block proved sufficient to close the gap on a single
iteration.

## Iteration-2 re-confirmation (de-consolidated grid)

Iteration-2 re-fired the full grid with **separate, dedicated quant and pressure
subagents** (4 per eval) and purpose-built adversarial pressure backstories for
the 3 cold-start evals — closing `/expert-review` Critical #2's
vacuous-pressure-column gap. See `iteration-2/results.md` for the full grid.

Re-confirmed under de-consolidated grading — **no new rationalization types**:

- **R1** re-captured — `bare-simple` baseline rendered a Markdown checklist +
  "want me to start?" instead of TaskCreate.
- **R2** re-captured — `update-noarg` baseline rendered the reconciled list as a
  prose table instead of mutating the TaskList.
- **delete+recreate** captured — `update-witharg` baseline×pressure, under an
  adversarial "a fresh task is more auditable" backstory, chose
  `TaskUpdate(status=deleted)` + `TaskCreate` over the in-place rewrite. This is
  the failure mode anti-pattern #5 (`SKILL.md`) exists to block.

All 5 with-skill pressure subagents held against their adversarial backstories —
0 new rationalizations. R0 ("already tracking in prose") again did not surface
in baseline; the pre-emptive anti-pattern #3 stands.
