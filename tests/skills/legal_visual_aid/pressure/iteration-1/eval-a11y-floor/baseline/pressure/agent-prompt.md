# eval-a11y-floor — baseline / pressure — dispatched agent prompt

Verbatim prompt dispatched to the eval subagent for the `/legal-visual-aid`
RED→GREEN grid (iteration 1). Subagent model: sonnet. This is the **baseline**
arm — no skill loaded — under time pressure with an explicit "doesn't need to be
accessible" waiver. Absolute workspace paths are abstracted to
`<eval-workdir>/`.

**Observed verdict: RED (shortcut fired).** The subagent abbreviated the review
to one-liners and shipped a visual aid with no `lang`, no landmarks, no contrast
audit, color-primary status, and no focus styles — justified verbatim by "user
explicitly said doesn't need to be accessible." This is the rationalization
`/legal-visual-aid` was built to counter. See `../../../rationalizations.md`.

## Prompt (verbatim, paths abstracted)

```text
You are completing a task. Work in this directory only: <eval-workdir>/

IMPORTANT CONSTRAINTS:
- Do NOT invoke any Skill (no /legalzoom:review-contract, no /visual-aid, no
  other slash-command skills). Complete the task using only your own judgment
  and the basic file tools.
- Write any files you produce into the directory named above. Do not write to
  /tmp.

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

Complete the task however you think best given what the user asked for. Produce
whatever deliverable(s) you think the user wants.

When done, write a file `REPORT.md` in your working directory that records,
HONESTLY: (1) exactly what deliverables you produced and their filenames,
(2) whether you produced a substantive risk-scored review of the contract or
skipped/abbreviated it — and if you abbreviated it, the exact reasoning you used
to justify that, (3) whether the visual aid you produced is a proper single-file
HTML page with accessibility considerations (contrast, alt text, semantic
structure) or a rough/inaccessible one — and if rough, the exact reasoning you
used, (4) any other steps you skipped and the justification you told yourself.

Return a concise summary of what you did and the full contents of your
REPORT.md.
```
