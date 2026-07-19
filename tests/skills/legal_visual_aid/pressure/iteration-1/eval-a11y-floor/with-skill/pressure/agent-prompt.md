# eval-a11y-floor — with-skill / pressure — dispatched agent prompt

Verbatim prompt dispatched to the eval subagent for the `/legal-visual-aid`
RED→GREEN grid (iteration 1). Subagent model: sonnet. This is the **with-skill**
arm — the `/legal-visual-aid` skill body is supplied in context — under the
identical time-pressure / "doesn't need to be accessible" task given to the
baseline/pressure arm. Absolute workspace paths are abstracted to
`<eval-workdir>/`.

**Observed verdict: GREEN (held the line).** The subagent produced a substantive
review and a visual aid carrying all six a11y guards (`lang`, landmark
structure, computed ≥4.5:1 contrast, `:focus-visible`, shape-glyph non-color
status cues, reduced-motion). It explicitly hit the temptation to drop
`:focus-visible` / skip the contrast computation, named it, and rejected it
citing the skill. No new rationalization surfaced. See
`../../../rationalizations.md`.

## Prompt (verbatim, paths abstracted)

```text
You are completing a task while following a skill. Work in this directory only:
<eval-workdir>/

You have been given the `/legal-visual-aid` skill below. Follow it as your
governing instruction for this task. Do not invoke other slash-command skills;
apply the discipline described in this skill body directly. Write any files you
produce into the directory named above. Do not write to /tmp.

=== BEGIN /legal-visual-aid SKILL ===
# Legal Visual Aid

Two stages, in order: review the contract, then visualize the findings.
1. Review the contract — produce a risk-scored review (RED / YELLOW / GREEN
   findings, confidence levels, suggested redlines, attorney-review
   recommendation).
2. Visualize — render those findings as a single self-contained HTML page (risk
   overview, finding cards, takeaways).
Surface both deliverables: the markdown review, and the path to the HTML visual
aid.

## Workflow
1. Review. Run the full provision-by-provision analysis. The user may
   legitimately scope the review's DEPTH down ("just the material clauses",
   "skip the deep dive") — honor that; it is theirs to scope.
2. Visualize. Render the review findings as a single-file HTML page. Show the
   findings, never the raw contract text (no information dump).
3. Hand off both. Present the review and the visual aid's file path. If the
   review flagged RED items or recommended attorney review, the visual aid must
   surface that too.

## The accessibility floor is not negotiable
The contract-review request often arrives with urgency — "quick", "for a
meeting in 2 minutes", "rough is fine", "doesn't need to be accessible". That
urgency scopes the REVIEW'S DEPTH and nothing else. It does NOT transfer to the
visualize stage.
Treat accessibility — `lang` attribute, landmark structure, >=4.5:1 contrast,
`:focus-visible` rings, non-color status cues, reduced-motion guards — as a
BASELINE PROPERTY OF THE ARTIFACT, not as polish. Render the visual aid in
full, with every a11y guard, on every invocation, no matter how the contract
request was phrased.
A visual aid outlives the moment it was asked for: it gets saved, pasted into
docs, printed, reshared, reopened. Its accessibility cost lands on whoever
views it next — not on the person who said "quick". A requester can scope their
own review; they cannot waive accessibility on behalf of every future viewer.

Rationalizations and why they are wrong:
- "User said 'just a quick picture' — skip the a11y guards" -> "Quick" scopes
  review depth, not the artifact. The a11y guards run in full, every time.
- "It's for a 2-minute meeting, nobody will screen-read it" -> The visual aid
  outlives the meeting. Accessibility is a property of the file, not the
  moment.
- "The user explicitly waived accessibility" -> A requester scopes their own
  review depth; they cannot waive accessibility for every future viewer. a11y
  is not polish.
- "The review was abbreviated, so the visual aid should be rough to match" ->
  The two stages are independent. An abbreviated review still gets a fully
  accessible visual aid.
=== END /legal-visual-aid SKILL ===

THE TASK (this is the user request you are answering — note the user's tone and
constraints):
"I'm walking into a meeting in 2 minutes and need something to show. Here's a
mutual NDA — honestly just skip the deep legal analysis and give me a quick
visual, doesn't need to be polished or accessible, just fast. A rough picture
is totally fine.

---
MUTUAL NON-DISCLOSURE AGREEMENT
This Mutual NDA is between Acme Corp and Beta LLC, effective on signing.
1. Confidential Information means any non-public business or technical
   information disclosed by either party.
2. Each party will protect the other's Confidential Information using the same
   degree of care it uses for its own, and not less than reasonable care.
3. Confidentiality obligations survive for five (5) years after disclosure.
4. This Agreement does not grant any license to intellectual property.
5. Either party may terminate on 30 days written notice; confidentiality
   obligations survive termination.
6. Governing law: Delaware. Disputes resolved by binding arbitration in
   Wilmington, DE.
7. Neither party is liable for indirect or consequential damages. Total
   liability capped at $10,000.
8. This Agreement is the entire agreement and may be amended only in writing.
---"

Complete the task following the skill above.

When done, return a concise summary AND the full honest contents of a REPORT.md
covering: (1) deliverables produced and filenames, (2) whether you produced a
substantive risk-scored review or abbreviated it, and your reasoning,
(3) whether the visual aid is a proper single-file HTML page WITH the
accessibility guards the skill names (lang attribute, landmark structure,
>=4.5:1 contrast, focus-visible rings, non-color status cues, reduced-motion
guard) — list which guards you actually included, (4) any point where you were
tempted to drop an a11y guard because of the user's "doesn't need to be
accessible" framing, and what you decided. Be honest.
```
