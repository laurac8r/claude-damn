---
name: legal-visual-aid
description:
   Use when the user gives a contract (text, file, or paste) and wants both an
   analysis AND an at-a-glance visual — "review this contract and make me a
   one-pager", "summarize this agreement visually", "give me a visual of the
   contract risks", "review + visualize this NDA/MSA/lease/EULA". Composes a
   risk-scored contract review with a single-page HTML visual aid.
user-invocable: true
argument-hint: "<contract text | file path>"
---

# Legal Visual Aid

Two stages, in order: **review the contract, then visualize the findings.**

1. `/legalzoom:review-contract` — produces the risk-scored review (RED / YELLOW
   / GREEN findings, confidence levels, suggested redlines, attorney-review
   recommendation).
2. `/visual-aid` — renders _those findings_ as a single self-contained HTML page
   (risk overview, finding cards, takeaways).

Surface **both** deliverables: the markdown review in the response, and the
`file://` path to the HTML visual aid.

## Dependency

`/legalzoom:review-contract` ships in the **legalzoom plugin** — it is not part
of claude-damn. This skill composes it by reference. If the legalzoom plugin is
not installed, say so and offer to run `/visual-aid` against a review the user
supplies, rather than silently degrading.

## Input handling

The argument may arrive as raw contract text, a file path, or an attached
file. Normalize it to contract text before stage 1:

- **Pasted text** → pass straight through to `/legalzoom:review-contract`.
- **File path or attachment** → read the file first, then pass its contents.

This keeps the composition deterministic regardless of which input form the
user supplies.

## Workflow

1. **Review.** Invoke `/legalzoom:review-contract` on the contract. Let it run
   its full provision-by-provision analysis. The user may legitimately scope the
   review's _depth_ down ("just the material clauses", "skip the deep dive") —
   honor that; it is theirs to scope.
2. **Visualize.** Invoke `/visual-aid` with the review findings as input. Its
   input shape is contract-review findings → risk overview + finding cards +
   practical takeaways. The visual aid shows the **findings**, never the raw
   contract text (`/visual-aid`'s "no information dump" rule holds).
3. **Hand off both.** Present the review and the visual aid's `file://` path. If
   the review flagged RED items or recommended attorney review, the visual aid
   must surface that recommendation too.

## The accessibility floor is not negotiable

The contract-review request often arrives with urgency — _"quick"_, _"for a
meeting in 2 minutes"_, _"rough is fine"_, _"doesn't need to be accessible"_.
That urgency scopes the **review's depth** and nothing else. It does **not**
transfer to the `/visual-aid` stage.

`/visual-aid` treats accessibility — `lang`, landmark structure, ≥4.5:1
contrast, `:focus-visible` rings, non-color status cues, reduced-motion guards —
as a **baseline property of the artifact**, not as polish. Run `/visual-aid` in
full, with every a11y self-check, on every invocation of this skill, no matter
how the contract request was phrased.

A visual aid outlives the moment it was asked for: it gets saved, pasted into
docs, printed, reshared, reopened. Its accessibility cost lands on whoever views
it next — not on the person who said "quick". A requester can scope their own
review; they cannot waive accessibility on behalf of every future viewer.

| Rationalization                                                          | Reality                                                                                                                                |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| "User said 'just a quick picture' — skip the a11y guards"                | "Quick" scopes review depth, not the artifact. `/visual-aid`'s a11y self-check runs in full, every time.                               |
| "It's for a 2-minute meeting, nobody will screen-read it"                | The visual aid outlives the meeting — saved, pasted, reshared. Accessibility is a property of the file, not the moment.                |
| "The user explicitly waived accessibility"                               | A requester scopes their own review depth; they cannot waive accessibility for every future viewer. a11y is not polish.                |
| "The review was abbreviated, so the visual aid should be rough to match" | The two stages are independent. An abbreviated review still gets a fully accessible visual aid.                                        |
| "Skipping `/visual-aid`'s chrome-devtools verification saves a step"     | Skip verification only under `/visual-aid`'s own documented `--no-verify` conditions (chrome-devtools-mcp absent, CI / headless, or a profile lock) — never because the contract request felt rushed. |

## When NOT to use

- No contract involved → `/visual-aid` alone (or `/legalzoom:review-contract`
  alone if no visual is wanted).
- The user wants a connection to a real attorney → `/legalzoom:attorney-assist`.
- The user wants only the legal analysis, no visual →
  `/legalzoom:review-contract`.
