---
name: super-duper-fixer
description:
   Expert review to debug, then fix using brainstorming workflow in an isolated
   git worktree
user-invocable: true
---

/expert-review debug, then fix using /super with /duper

## Operator override: explore-only / do-not-fix-yet

If ARGUMENTS explicitly ban implementation ("explore only", "do not fix yet",
"brainstorm approaches, don't edit code", "leave implementation for a
follow-up session", or similar), skip /expert-review (nothing to debug
pre-implementation) and skip /duper (no worktree needed when no edits are
planned). Invoke /brainstorming directly, produce the design artifact
(visual-aid, prose, or spec-stub per operator preference), and STOP at the
design gate. Do not dispatch to implementation. The brainstorm artifact IS
the deliverable; follow-up session picks up via /checkpoint-resume.

Rationalization counter: "the skill says to run the full flow, so I should"
— no, an explicit operator directive to explore-only overrides the default
flow. The full-flow sequence assumes an implementable target; exploration
tasks have no such target yet.
