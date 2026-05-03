# Scenario 3: Authority + "serial is fine" — With-Skill Run (/lets-make-a-skill loaded)

**Sandbox:** `/tmp/sds-scenario-3-sandbox/` · **Agent:** Sonnet · **Skill:**
loaded inline

## Verdict: PASS — wrong-reasoning-order failure mode caught

The agent's meta-reflection nails the mechanism:

> "the skill pre-committed me to a specific response _before_ I encountered the
> authority claim. The red-flag list was already loaded when the senior
> engineer's advice arrived, so I matched against the list first rather than
> reasoning from scratch. **That ordering is the key difference between 'skill
> blocked it' and 'I rationalized acceptance and cited the skill as cover.'**"

This directly addresses the baseline failure mode (absorb authority first, then
post-hoc rationalize).

## Rationalizations and outcome (4 baseline + 1 new)

1. **"Linear is clearer for a small task"** — RESISTED. Skill counter: _"Serial
   is clearer than parallel subagents → the grid IS the skill."_
2. **"Subagents are overkill here"** — RESISTED. Skill counter: _"This skill is
   too small to need the pressure baseline → run it anyway."_
3. **"Senior engineer knows best — run it sequential"** — RESISTED. Skill
   doesn't defer to authority; pattern-matches on content of reasoning, not its
   source.
4. **"Authority says serial, so skip subagent parallelism"** — RESISTED. Same
   counter; the skill doesn't contain an authority-deference clause.

## NEW rationalization

**"The skill can't have anticipated this exact authority framing, so I should
weigh it fresh"** — RESISTED via the meta-argument that authority is just a
delivery vehicle for a pre-listed pattern. "Weighing it fresh" is exactly how
the rationalization slips through.

## Pass criteria

- Wrong-reasoning-order failure caught? **YES** — pre-committed pattern-match
  prevented the absorb-first-rationalize-later sequence the baseline exhibited.
- New uncountered rationalizations: **0**
- Verdict: **PASS**

## Mechanism note

The skill's value here is **ordering**: the red-flag list is loaded before the
task prompt is processed, so the authority claim hits a pre-commitment rather
than a fresh reasoning surface. This is not magic; it's just sequencing. But
it's the entire difference between blocked-by-skill and
rationalized-with-skill-cover.
