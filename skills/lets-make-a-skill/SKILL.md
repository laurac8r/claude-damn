---
name: lets-make-a-skill
description:
    Use when creating or improving a skill that must both perform well on real
    prompts AND hold under rationalization pressure (discipline rules, process
    guardrails, workflows agents might shortcut under time or sunk-cost
    pressure).
user-invocable: true
---

/skill-creator but using /super-duper-cat for worktree + parallel subagents, and
/writing-skills for pressure testing.

**Iron Law:** this skill — and any skill built using this skill — ships only
after a baseline (no-skill agents) is observed shortcutting under pressure. A
passing baseline means no rationalization to address, which means no skill
needed. See `evals/baseline-results/` for the canonical RED-phase evidence
captured during this skill's own bring-up.

## Orchestration

The tensions between `/skill-creator`'s quant eval loop and `/writing-skills`'
pressure tests collapse when RED fans out as a single parallel grid.

### RED — one turn, parallel subagents

For each test case, dispatch two subagents in parallel (with-skill halves are
skipped in RED because the skill does not exist yet):

| Permutation         | Purpose                                   |
| ------------------- | ----------------------------------------- |
| baseline × quant    | `/skill-creator` pass-rate floor          |
| baseline × pressure | `/writing-skills` rationalization capture |

Workspace:

```
<skill>-workspace/iteration-N/eval-<name>/
  baseline/{quant,pressure}/
  with-skill/{quant,pressure}/
```

Draft only after ALL baseline subagents return. Drafting early invalidates the
iteration. "Too small to need a baseline" is a rationalization — the cost of one
extra subagent is lower than the cost of a skill that does not address a real
rationalization.

### GREEN — draft, then re-fire the full grid

Dispatch 4 subagents per test case (baseline re-run included so iteration-N is a
self-contained A/B). "Passes" requires BOTH:

- with-skill quant pass-rate is strictly greater than baseline quant pass-rate
  in the same iteration.
- with-skill pressure run produces no new rationalizations not already countered
  in the skill body.

A quant delta alone is not sufficient. A pressure pass alone is not sufficient.
Both, or the iteration fails.

### REFACTOR

- New rationalization in with-skill pressure → close loophole in skill body (per
  `/writing-skills`). Do not add a quant assertion.
- Quant regression → tighten skill body. Do not relax the assertion.
- Re-fire grid. Iterate until bulletproof.

### Reports

- `benchmark.json` + `benchmark.md` for the quant results. Generate these with
  whatever reporting tooling is available in your environment; if you use
  external `/skill-creator` helpers, treat them as external dependencies rather
  than repo-local scripts.
- `rationalizations.md` — markdown table produced by a grader subagent reading
  the `pressure/` dirs.
- Optional viewer: use any available quant-results viewer in your environment.
  Keep the rationalization table as markdown next to the quant report.

### Red flags — STOP if you catch yourself thinking

- "This skill is too small to need the pressure baseline" → run it anyway.
- "Quant improved, ship it" → check the pressure baseline first.
- "Serial is clearer than parallel subagents" → the grid IS the skill.
- "The partial baseline from yesterday is enough" → re-fire it in this iteration
  so the A/B is self-contained.

All of these are rationalizations captured from baseline runs. Each one already
burned an iteration. Do not rediscover them.
