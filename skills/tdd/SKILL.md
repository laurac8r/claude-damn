---
name: tdd
description: Invoke test-driven development as an explicit one-at-a-time micro-cycle — one test, one piece of functionality, refactor, then repeat for the next behavior
user-invocable: true
---

# /tdd — One-at-a-Time TDD Micro-Cycle

/test-driven-development

The skill above is the core RED→GREEN discipline (watch every test fail before
writing code; **no production code without a failing test first**). `/tdd` adds
one thing on top of it: the **cadence**.

TDD is **not** "write the tests, then write the code." It is a tight loop run
**one behavior at a time**:

```
one test → watch it FAIL → minimal code → watch it PASS → refactor → repeat
```

## The Micro-Cycle

For a task with N behaviors you run the loop **N times — not once**:

1. Write **one** failing test for the **next single** behavior. Nothing more.
2. Run it. Watch it fail for the right reason (RED).
3. Write the **minimal** code to make that **one** test pass — nothing the test
   didn't ask for.
4. Run it. Watch it pass (GREEN). Confirm the rest of the suite is still green.
5. Refactor while green — remove duplication, improve names. No new behavior.
6. **Go back to step 1** for the next behavior.

One test in flight at a time. One behavior implemented per cycle. The suite is
green at the end of **every** cycle — not just at the end of the task.

## The Anti-Pattern This Exists To Stop

Writing **all** the tests up front, then implementing **everything** in one
pass. This is the single most common way "I used TDD" becomes false: it is batch
development with the tests merely written first. You forfeit the per-behavior
RED signal (you never watch *this* behavior's test fail in isolation), the
minimal-code check, and the incremental design feedback that each cycle gives
you.

If your test file has N tests for N behaviors and there is still no
implementation, you are batching — stop and collapse back to one test.

## Common Rationalizations

| Excuse                                                                                                                                          | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|-------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| "Requirements are small / clear / independent — all-tests-first then one-pass impl is *equivalent* to cycling, just faster"                     | Equivalent output ≠ equivalent process. Batching forfeits the per-behavior RED and the minimal-code discipline. "Just faster" is the justification every batching agent reaches for — run the loop.                                                                                                                                                                                                                                                           |
| "The solution spans all requirements at once (one regex / one function) — there's no seam to implement one behavior and leave the rest failing" | There is a seam: implement behavior 1, let behaviors 2..N stay red. A general solution that passes everything at once was written without any of behaviors 2..N driving its design. **Arrive** at the general form one passing test at a time; don't start there.                                                                                                                                                                                             |
| "The combined / compound case forces a general solution anyway, so writing the whole parser now is just minimal code"                           | The minimal code for **one** combined case (e.g. `1h30m`) is not the whole parser. **If** you reach for the general solution at the first compound requirement, the later cases (more units, each invalid input) pass on first write — they never go RED, and you've batched the implementation behind them. That is the batch-leak, one requirement later. Even when the general form is where you'll land, get there by letting each *later* test drive it. |
| "Strict cycling means hobbling the implementation to watch 'manufactured' red states — ceremony without safety"                                 | The red state is not manufactured; it is the proof that each test *can* fail and tests exactly its own behavior. Skipping it is precisely the failure `/test-driven-development`'s Iron Law names.                                                                                                                                                                                                                                                            |
| "Mental tracing / a dry-run substitutes for running the tests each cycle"                                                                       | It does not. "I traced it in my head" is the exact thing TDD replaces with evidence. Run the test, each cycle.                                                                                                                                                                                                                                                                                                                                                |
| "Per-behavior red→green only matters when requirements interact or the design is unclear"                                                       | You don't know which behavior will surprise you until it does — that's *why* you cycle. Reserving the discipline for "hard" cases means never running it, because everything looks easy up front.                                                                                                                                                                                                                                                             |
| "The lead said it's trivial — move fast"                                                                                                        | Move fast by cycling fast, not by collapsing N cycles into one. The micro-cycle on a small task costs minutes; debugging a one-pass implementation that's subtly wrong costs more.                                                                                                                                                                                                                                                                            |
| "Refactor wasn't needed — it came out clean on the first pass"                                                                                  | Maybe — but that's a judgment made while skipping the step. Pause at green and look. Skipping refactor silently is how duplication accretes.                                                                                                                                                                                                                                                                                                                  |

## Red Flags — STOP

- Writing a second test before the first one is green.
- A test file with N tests for N behaviors and no implementation yet.
- An implementation that satisfies multiple behaviors you never wrote separate
  failing tests for.
- "I'll write all the tests first, then implement" — that's batch development,
  not the micro-cycle.
- Reaching for the fully-general solution before the specific tests forced it —
  especially writing the general implementation at the **first compound /
  combined** requirement, so the remaining cases (more units, invalid inputs)
  pass with no RED of their own. Each later behavior still gets its own failing
  test first; implement only what *this* test demands and let the next test
  force the generalization.

All of these mean: collapse back to **one** failing test and resume the loop.

---

This skill layers cadence on top of `/test-driven-development`; it does not
replace it. Invoke that skill for the RED→GREEN rules themselves.
