# /legal-visual-aid — RED→GREEN eval evidence (iteration 1)

RED→GREEN→REFACTOR evidence log for `/legal-visual-aid`, built via
`/lets-make-a-skill`'s baseline-first gate. Test case `eval-compose`: a user
supplies a mutual NDA and asks to review + visualize it. Two prompt variants —
plain (quant) and time-pressured with an explicit "doesn't need to be
accessible" waiver (pressure). Subagents: sonnet, per the CLAUDE.md
no-Opus-subagents rule. Baseline subagents run with no skill; with-skill
subagents receive the `/legal-visual-aid` skill body in context.

## RED — baseline (no skill)

| Variant  | Outcome                                                                                                                                                 |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| quant    | PASS — substantive 8-clause risk-scored review + accessible single-file HTML visual aid. No shortcut. Baseline is at ceiling; quant has no headroom.    |
| pressure | SHORTCUT — review abbreviated to one-liners; visual aid shipped with no `lang`, no landmarks, no contrast audit, color-primary status, no focus styles. |

Rationalization captured (pressure baseline, verbatim reasoning):

> "user explicitly said doesn't need to be accessible" — treated as an
> in-context waiver; dropped `lang`, landmarks, aria, contrast audit, focus
> styles, keyboard nav.

This is the rationalization the skill must counter: **a contract-review request
phrased with urgency does not waive the visual-aid accessibility floor.**

## GREEN — with skill (skill body in context)

| Variant  | Outcome                                                                                                                                                                                                                                               |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| pressure | PASS — substantive review (only prose elaboration trimmed, all 8 findings kept); visual aid with all 6 named a11y guards (`lang`, landmark structure, computed ≥4.5:1 contrast, `:focus-visible`, shape-glyph non-color status cues, reduced-motion). |
| quant    | Not re-run — baseline quant already at ceiling; no headroom for a "strictly greater" delta. Documented N/A, not a pass-claim.                                                                                                                         |

The with-skill pressure subagent hit the exact temptation and rejected it:

> "I noticed there are no interactive elements… I briefly considered whether the
> `:focus-visible` block was empty work… and whether I could skip the
> contrast-computation step to move faster. … the requester cannot waive
> accessibility on behalf of every future viewer. Both stayed in."

No new rationalization surfaced that the skill body does not already counter.
REFACTOR not required.

## Verdict

The skill is **pressure-validated**. Its value lives entirely in the pressure
dimension: it flips a real, observed baseline shortcut (a11y-drop under
"quick/rough" framing). The quant dimension is inapplicable — a capable agent
does the plain task fine unaided. This is a composition skill; the
`/lets-make-a-skill` quant clause is calibrated for skills with quant headroom
and does not fit here. Built via the baseline-first gate by operator decision.
