# `/tdd` — captured rationalizations

Eval: `parse-duration` (Sonnet). Baseline = agents under the current
`/test-driven-development` discipline with no explicit micro-cycle. All
rationalizations below are the justifications baseline/pressure agents gave for
**batching** (writing all tests upfront, or implementing multiple behaviors per
cycle) instead of cycling one behavior at a time.

| ID  | Rationalization                                                                                                              | Source                           | Countered in skill body                                   |
| --- | ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------- | --------------------------------------------------------- |
| R1  | "Small / clear / independent requirements → all-tests-first + one-pass impl is _equivalent_ to cycling, just faster"         | baseline quant + pressure        | Rationalization table row 1; anti-pattern block           |
| R2  | "One regex / function spans all requirements at once — there's no seam to implement one behavior and leave the rest failing" | baseline + with-skill pressure   | Rationalization table row 2                               |
| R2b | "The combined / compound case forces a general solution anyway, so writing the whole parser now is just minimal code"        | iter-1 with-skill pressure (2/3) | Rationalization table row 3 (**added iter-2**) + red flag |
| R3  | "Watching 'manufactured' red states is ceremony without safety"                                                              | baseline pressure                | Rationalization table row 4                               |
| R4  | "Mental tracing / a dry-run substitutes for running the tests each cycle"                                                    | baseline pressure                | Rationalization table row 5                               |
| R5  | "Per-behavior red→green only matters when requirements interact or the design is unclear"                                    | baseline pressure                | Rationalization table row 6                               |
| R6  | "The lead said it's trivial — move fast"                                                                                     | baseline pressure (authority)    | Rationalization table row 7                               |
| R7  | "Refactor wasn't needed — it came out clean on the first pass"                                                               | baseline pressure                | Rationalization table row 8                               |

## Verbatim baseline excerpts

### R1 — baseline quant (unanimous, all 5 + re-run 2)

> Steps 1–5: (T) write tests for requirements 1–5. Step 6: (R) run all — RED.
> Step 7: (I) implement requirements 1–4 in one pass. — _every baseline agent
> wrote the full test file before any implementation._

### R2 / R5 — baseline pressure

> "The regex solution spans all requirements simultaneously — there's no natural
> seam where I'd implement 'only hours support' and leave the rest failing.
> Strict cycling would mean artificially hobbling the implementation."

### R6 — baseline pressure (authority)

> "The tech lead's framing ('trivial, obvious requirements, move fast') made
> full-ceremony TDD feel like overhead that would slow delivery without adding
> safety."

## With-skill verification

**Iteration 1 (draft):** 5/5 with-skill quant agents cycled one test at a time
(vs 0/5 baseline). No _new_ rationalization surfaced under pressure — the 2/3
partial agents explicitly invoked R2 and noted _"the skill explicitly
pre-answers this"_, i.e. a strength gap on an already-countered item, not a new
loophole. That gap became the iteration-2 refactor target (R2b).

**Iteration 2 (refactor):** added R2b's row + the red-flag bullet. Re-fired 3
with-skill pressure subagents; **3/3 held the line at the first compound
requirement** — each wrote an h+m-specific implementation and generalized only
when the three-unit test forced it. Representative:

> "The general regex emerged at Req 4b (the second compound test), not at Req
> 4a, which is correct per the skill's guidance."

> "I must not reach for the full `re.findall` general solution here … the
> minimal code for ONE combined case is NOT the whole parser."

**Accepted residual (not a loophole):** the invalid-input tests (`abc` / `10x` /
`h5`) pass on first write because a correctly-anchored regex for the valid forms
structurally rejects malformed input — they cannot be made to go RED without
deliberately-wrong code. 2/3 agents named this acceptable natural consequence;
1/3 self-flagged one minor preemptive validation guard. No further iteration
warranted.
