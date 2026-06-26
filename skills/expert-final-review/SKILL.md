---
name: expert-final-review
description:
   Final pre-merge gate — verify all PR peer feedback is addressed, then run a
   full /expert-review
user-invocable: true
---

Run /fast-pr-final-self-review to confirm all PR peer feedback on the current
branch is addressed, then run /expert-review all for a final multi-phase sweep.
Address anything the self-review surfaces before treating the expert review as
merge sign-off; aggregate both into one go / no-go summary.
