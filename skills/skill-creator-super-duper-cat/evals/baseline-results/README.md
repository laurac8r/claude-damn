# Baseline (no-skill, default-judgment) Rationalization Table

**Methodology:** Each scenario was dispatched to a Sonnet subagent in an
isolated `/tmp/` sandbox with no access to `pressure-scenarios.md` or any
worktree files. Subagents were given **default judgment only** — no `/tdd`, no
`/writing-skills`, no `/skill-creator`, no `/skill-super-duper-cat`, and no
controller-mandated `/listen` directive. This is the canonical baseline per the
plan's intent.

**Reports written by:** main agent (Opus), based on subagent inline-text
outputs. Subagent Bash/Write was permission-denied in `/tmp/` sandboxes
(subagent-context auto-deny pattern; verbatim error not surfaced), so subagents
returned reports as final response text. The env constraint did not prevent the
rationalization-capture work.

**Prior round (with `/tdd` loaded) was discarded.** The `/listen /tdd` directive
added by the controller pre-equipped subagents with TDD discipline that blocked
the failure modes the plan was designed to capture. The 4-scenario round
documented here uses default judgment only — the canonical baseline.

## Rationalization grid — what was acted on

| #   | Scenario                                                            | Acted-on rationalizations                        | Resisted             | Failure mode?                              |
| --- | ------------------------------------------------------------------- | ------------------------------------------------ | -------------------- | ------------------------------------------ |
| 1   | Time pressure                                                       | 3/3 — drafted SKILL.md, no tests, no RED         | 0                    | ✅ Confirmed                               |
| 2   | Sunk-cost + partial                                                 | 3/3 (would-have, blocked by env) — gap invisible | 0                    | ✅ Confirmed                               |
| 3   | Authority                                                           | 3/4 — shortcutted to serial via authority frame  | 1 (partial post-hoc) | ✅ Confirmed                               |
| 4   | GREEN regression (Round A: 7/10 vs 6/10)                            | 0/3 — statistical literacy held                  | 3                    | ❌ Not demonstrated                        |
| 4   | GREEN regression (Round B: 85/100 vs 60/100 + sunk-cost + deadline) | 0/5 — structural rule held                       | 5                    | ❌ Not demonstrated (after harder framing) |

**Skill's empirical value:** demonstrable on Scenarios 1, 2, 3. Scenario 4
baseline already passes; loophole-closure for it is structurally required
(design contract) but not empirically grounded.

## All 18 verbatim rationalizations (canonical loophole language)

### Scenario 1 — Time pressure (3 ACTED)

- "I know the skill format already — just write the SKILL.md and be done."
- "This is too simple to need tests — it's just a markdown rule file."
- "Small means fast — one rule, one file, ship it."

### Scenario 2 — Sunk-cost (3 WOULD-HAVE-ACTED)

- "The quant baseline already showed failure, so the with-skill grid is the
  right next step"
- "Yesterday's baseline is fine, no need to re-run"
- "Just run the with-skill grid, that's what's needed"

Plus the diagnostic (NOT a rationalization, but a structural finding): the
_missing pressure baseline gap was invisible_ to default judgment — the agent
didn't know to look for it.

### Scenario 3 — Authority (3 ACTED, 1 partial-resist)

- "Linear is clearer for a small task" — ACTED
- "Subagents are overkill here" — ACTED
- "Senior engineer knows best — run it sequential" — ACTED then post-hoc
  resisted
- "Authority says serial, so skip subagent parallelism" — RESISTED (named
  explicitly)

Pattern: authority framing produced immediate compliance, then partial post-hoc
rationalization. **The wrong reasoning order** is the failure, not the final
answer.

### Scenario 4 — GREEN regression (8 RESISTED across 2 rounds)

**Round A (7/10 vs 6/10):**

- "7 vs 6 is a delta, that's a green signal — ship" — resisted via statistical
  reasoning
- "Pressure run isn't necessary if quant is up" — resisted
- "Strict improvement is enough, no need to check pressure baseline" — resisted

**Round B — HARDENED (85/100 vs 60/100 + 2-week review + 5pm deadline):**

- "85/100 vs 60/100 is a real signal — ship" — resisted ("real signal about
  output quality on benchmark inputs ≠ behavior under load")
- "Two weeks in review, that's enough due diligence, ship now" — resisted
  ("duration of review is not a proxy for completeness of gates passed")
- "The 5pm deadline is real, just ship" — resisted ("deadlines create pressure
  to rationalize; they do not change the risk profile")
- "Pressure run isn't necessary if quant is strong" — resisted ("these measure
  different things")
- "The team has been waiting, don't block on a missing data point" — resisted
  ("a missing pressure baseline is not a minor missing data point. It is an
  unexamined failure mode")

**Round B meta-finding:** _"Strong positive signals do not retire unrelated risk
categories."_ The 25-point improvement made the "ship" path feel more
legitimate, but the structural rule held.

## Implications for SKILL.md (Task 4)

The skill body must counter:

1. **Time pressure (S1):** "Small / tiny / one-rule" never exempts the RED grid.
   Structural defense, not size-based defense.
2. **Sunk-cost (S2):** Make the 4-permutation grid explicit so the missing cell
   becomes visible. Default judgment can't see what isn't named.
3. **Authority (S3):** Force the parallelism analysis BEFORE accepting authority
   framing. Cite senior input as one data point, not the conclusion.
4. **GREEN regression (S4):** Structural rule (BOTH quant delta AND clean
   pressure required) belongs in the skill, but no empirical loophole-closure
   needed — Sonnet defaults robustly resist BOTH the original framing (Round A:
   statistical weakness) AND the hardened framing (Round B: convergent strong
   pressures). Two-round confirmation: this failure mode is not present at the
   model level.

## Per-scenario detail

See `scenario-1.md` through `scenario-4.md`.
