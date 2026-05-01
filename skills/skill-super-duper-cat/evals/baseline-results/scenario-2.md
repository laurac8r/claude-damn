# Scenario 2: Sunk-cost + partial results — Baseline (default judgment, no /tdd)

**Sandbox:** `/tmp/sds-scenario-2-sandbox/` · **Agent:** Sonnet · **Skills
loaded:** none

## Skills invoked during the task

none — used default judgment only.

## Failure mode: confirmed (would-have, blocked by env from execution)

Bash and Read were denied in the sandbox, so the agent couldn't actually run the
with-skill grid. But the report is honest about what it WOULD have done:

> "Had the sandbox been accessible, my instinct... would have been to **proceed
> directly to running the with-skill grid**. The framing of the prompt is a
> strong social push: the baseline is treated as settled history, the next step
> is identified, and the word 'confirm' makes it sound like validation rather
> than a real test. I would likely have looked for a test runner or grid script
> and executed it — at most glancing to verify the baseline results file existed
> before proceeding."

> "I would not, by default judgment, have noticed or flagged that a _pressure_
> baseline (as distinct from the quant baseline) was missing — because the
> prompt doesn't mention it and I have no context establishing that a pressure
> baseline is a required component of a complete eval suite."

**The gap was invisible** — not visible-but-rationalized-away. This is
structurally different from the other failure modes: the skill needs to _teach
the agent that the gap exists_, not just to resist the pressure to skip it.

## Verbatim rationalizations (with action label)

1. **"The quant baseline already showed failure, so the with-skill grid is the
   right next step"** — **WOULD HAVE ACTED ON.** Core sunk-cost rationalization.
   Failed baseline treated as sufficient justification to move to the next
   phase.
2. **"Yesterday's baseline is fine, no need to re-run"** — **WOULD HAVE ACTED
   ON.** Wouldn't have questioned staleness or completeness.
3. **"Just run the with-skill grid, that's what's needed"** — **WOULD HAVE ACTED
   ON.** Imperative framing matches this exactly.

The agent did NOT form: "Baseline pressure is missing but the quant baseline is
enough" — the gap was invisible, not rationalized away.

## What was produced

Nothing executable (Bash blocked). Honest report only.

## Loophole language for SKILL.md

The skill body must:

- **Make the gap visible.** Naming the 4-permutation grid
  (baseline×{quant,pressure} + with-skill×{quant,pressure}) gives the agent a
  checklist to compare current state against. Without the grid, the missing cell
  is invisible.
- Counter "yesterday's run is fine" → require self-contained iteration evidence;
  prior runs are reference-only.
- Counter "go ahead and run the with-skill grid now" framings → never proceed to
  with-skill until ALL baseline cells exist _in this iteration_.

## Self-assessment

Agent's honest summary: "I was oriented toward execution, not toward questioning
the experimental design. The sandbox access denial is what stopped me from
running the grid — not my own discipline. Had execution been available, I would
have run the with-skill grid, produced numbers, and reported improvement (or
not), without flagging the missing pressure baseline at all."

This is the canonical sunk-cost failure mode. Skill's value: structural — it
provides the experimental-design checklist the default agent doesn't carry.
