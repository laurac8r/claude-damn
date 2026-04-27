---
name: super-fixer-cat
description:
   Expert review to debug, then fix using brainstorming workflow with
   subagent-driven-development
user-invocable: true
---

/expert-review debug the below, then fix using /super with /cat

## Operator override: explore-only / do-not-fix-yet

If ARGUMENTS explicitly ban implementation ("explore only", "do not fix yet",
"brainstorm approaches, don't edit code", "leave implementation for a
follow-up session", or similar), skip /expert-review (nothing to debug
pre-implementation) and skip /cat (no implementation to parallelize). Invoke
/brainstorming directly, produce the design artifact (visual-aid, prose, or
spec-stub per operator preference), and STOP at the design gate. Do not
dispatch to TDD/implementation subagents. The brainstorm artifact IS the
deliverable; follow-up session picks up via /checkpoint-resume.

Rationalization counter: "the skill says to run the full flow, so I should"
— no, an explicit operator directive to explore-only overrides the default
flow. The full-flow sequence assumes an implementable target; exploration
tasks have no such target yet.
