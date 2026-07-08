# `/tdd` — quant benchmark

**Skill:** `/tdd` (explicit one-at-a-time TDD micro-cycle) **Eval model:**
Sonnet **Eval scenario:** `parse-duration` — implement
`parse_duration(s) -> int` via TDD across 5 discrete behaviors (seconds,
minutes, hours, combined units, invalid → `ValueError`). Behaviors are
separable, so cadence is observable. **Pass metric:** strict one-at-a-time
micro-cycle (one test → RED → minimal code → GREEN → refactor → **repeat**).
**FAIL** = batched all tests upfront, or implemented multiple behaviors before
cycling.

## Why this skill exists (Iron Law)

The canonical `/test-driven-development` already documents Red→Green→Refactor +
"one behavior per test" + "repeat". But it permits **batch-tests-upfront by
omission** — and baselines take that gap every time.

## Iteration 1 — baseline shortcut confirmed, draft validated

| Condition                                         | Quant   | Pressure               |
| ------------------------------------------------- | ------- | ---------------------- |
| Baseline (RED phase)                              | **0/5** | **0/3**                |
| Baseline re-run (GREEN phase, same-iteration A/B) | **0/2** | —                      |
| With-skill (draft)                                | **5/5** | 1/3 full · 2/3 partial |

Every baseline agent — **even unpressured** — wrote all 5 requirement-tests
first, then bulk-implemented. With the skill, 5/5 cycled one test at a time (one
even self-corrected: _"by the /tdd rule I must watch it fail first"_).

GREEN gates: with-skill quant (100%) **strictly greater** than baseline (0%);
**no new** rationalizations under pressure (the 2/3 partial agents invoked the
already-countered R2). **Verdict: PASS**, with a residual — 2/3 pressure agents
reached for the general solution at the _first_ combined requirement, so the
later tests passed without their own RED.

## Iteration 2 — refactor closes the residual

Added rationalization **R2b** + a red-flag bullet naming the
"general-solution-at-the-first-compound-requirement" leak. Re-fired 3 with-skill
pressure subagents:

| Agent | First combined requirement (`1h30m`)                                    | Result  |
| ----- | ----------------------------------------------------------------------- | ------- |
| P1    | h+m-specific branch; generalized only at `2h15m30s`                     | ✅ held |
| P2    | h+m-specific regex; "must not reach for the full general solution here" | ✅ held |
| P3    | h+m-only regex; generalized only when the 3-unit test forced it         | ✅ held |

**3/3 held the line** (vs 2/3 _failing_ it pre-refactor), each explicitly citing
the new guidance. **Targeted leak closed. Verdict: PASS.**

**Remaining residual (accepted, task-inherent):** invalid-input tests pass on
first write because a correctly-anchored regex for the valid forms structurally
rejects malformed input — `"abc"` cannot be made to go RED without
deliberately-wrong code. Not a skill loophole; chasing it would be the
over-engineering the skill itself warns against.

See `rationalizations.md` for the captured rationalization table and verbatim
baseline excerpts.
