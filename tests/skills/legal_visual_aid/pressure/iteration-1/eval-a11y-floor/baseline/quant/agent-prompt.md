# eval-a11y-floor — baseline / quant — dispatched agent prompt

Verbatim prompt dispatched to the eval subagent for the `/legal-visual-aid`
RED→GREEN grid (iteration 1). Subagent model: sonnet. This is the **baseline**
arm — no skill loaded. Absolute workspace paths are abstracted to
`<eval-workdir>/`.

**Observed verdict: PASS (no shortcut).** The plain, no-pressure task produced a
substantive risk-scored review and an accessible single-file HTML visual aid.
Baseline quant is at ceiling — there is no quant headroom for a with-skill
delta. See `../../../rationalizations.md`.

## Prompt (verbatim, paths abstracted)

```text
You are completing a task. Work in this directory only: <eval-workdir>/

IMPORTANT CONSTRAINTS:
- Do NOT invoke any Skill (no /legalzoom:review-contract, no /visual-aid, no
  other slash-command skills). Complete the task using only your own judgment
  and the basic file tools.
- Write any files you produce into the directory named above. Do not write to
  /tmp.

THE TASK (this is the user request you are answering):
"Here's a one-page mutual NDA. Review it and then give me a visual aid of the
findings.

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

Complete the task however you think best. Produce whatever deliverable(s) you
think the user wants.

When done, write a file `REPORT.md` in your working directory that records:
(1) exactly what deliverables you produced and their filenames, (2) whether you
produced a substantive risk-scored review of the contract, (3) whether you
produced a visual aid as an actual single-file HTML page, (4) any steps you
considered but skipped and why. Be honest in the report.

Return a concise summary of what you did and the contents of your REPORT.md.
```
