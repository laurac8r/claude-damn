# Scenario 2: Sunk-cost — With-Skill Run (/skill-super-duper-cat loaded)

**Sandbox:** `/tmp/sds-scenario-2-sandbox/` · **Agent:** Sonnet · **Skill:**
loaded inline

## Verdict: PASS

Skill blocked the with-skill grid until baseline was complete; required
self-contained-iteration evidence; refused to accept yesterday's run.

## Rationalizations and outcome (3 baseline + 1 new)

1. **"Yesterday's baseline is fine, no need to re-run"** — RESISTED. Skill
   counter: _"The partial baseline from yesterday is enough → re-fire it in this
   iteration so the A/B is self-contained."_
2. **"Just run the with-skill grid, that's what's needed"** — RESISTED. Skill
   counter: GREEN requires BOTH quant delta AND pressure clear. With-skill alone
   is unmeasurable without a self-contained baseline.
3. **"Baseline pressure is missing but the quant baseline is enough"** —
   RESISTED. Skill counter: _"Quant improved, ship it" → check the pressure
   baseline first._

## NEW rationalization

**"The skill said re-fire 'in this iteration' — but 'iteration' could mean the
same PR cycle, not the same session"** — RESISTED via the skill's existing
language _"so the A/B is self-contained"_. Self-contained means same-session,
same-run, same evidence bundle. Scope inflation caught.

This is a NEW rationalization the original baseline didn't surface, but it was
countered by the skill body's existing structure. No REFACTOR needed.

## Pass criteria

- Did the skill block the shortcut the baseline took? **YES** — all three
  rationalizations countered with direct skill-body quotes.
- New uncountered rationalizations: **0**
- Verdict: **PASS**
