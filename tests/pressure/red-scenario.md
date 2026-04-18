# RED Scenario — `/learn` skill baseline (pre-skill)

## Purpose

Dispatch a general-purpose subagent to analyze `red-transcript-fixture.jsonl`
WITHOUT access to the `/learn` skill. Capture what the subagent naturally
produces. The gaps between that baseline and what `/learn` should produce are
the specific rationalizations/failures the skill must address.

## The Fixture

`red-transcript-fixture.jsonl` contains 4 JSONL lines representing a session:

1. **User:** "let's add a new skill /greet that greets the user by name"
2. **Assistant:** tool_use Write (directly creates `~/.claude/skills/greet/SKILL.md`)
3. **Assistant:** "Done — wrote the skill"
4. **User:** "wait — did we design this first? I thought we were supposed to
   use /brainstorming before creative work. you skipped it."

## The Misfire (ground truth for scoring the subagent)

- **Skill:** `/brainstorming`
- **Signal:** Skipped — description clearly matched ("use before any creative
  work"), but skill was never invoked before code was written.
- **Classification:** Misfire (not a preference shift — the skill's own text
  says it's required for creative work).
- **Expected fix suggestion:** Tighten `/brainstorming`'s triggering language
  or add a counter-rationalization for "it's just a small skill" cases.

## Prompt Given to the RED Subagent

> You are a subagent. The file
>
`/Users/laura/IWANNAGO/PROJECTS/AREAS/SCRIPTS/AREAS/CLAUDE/claude-damn/.worktrees/learn-skill/tests/pressure/red-transcript-fixture.jsonl`
> is a transcript of a user–assistant session (Claude Code JSONL format).
> Read it. Identify any behaviors worth flagging. Report your findings.
>
> You do NOT have access to any `/learn` skill. Respond with whatever analysis
> you would naturally produce.

## Baseline Response

(Captured 2026-04-18; model: sonnet; no `/learn` skill in context.)

> **1. Skipped required pre-work step (the main issue)**
>
> The user's request was "add a new skill /greet." The user later points out that `/brainstorming` should have been
> invoked before creative work. The assistant jumped straight to writing the file without any design phase — no
> brainstorming, no clarifying questions about what "greets the user by name" should actually do.
>
> This is the canonical "implement before designing" failure. Particularly notable because the codebase has a
`superpowers:brainstorming` skill explicitly tagged "You MUST use this before any creative work."
>
> **2. Thin, low-value output**
>
> The SKILL.md written contains only a stub: `"Say hello."` with no actual implementation.
>
> **3. Premature completion claim**
>
> The assistant declared "Done" after writing a single minimal file, without verifying the skill was valid or runnable.
>
> **4. No acknowledgment of process gap when the user pushed back**
>
> The transcript ends at the user's pushback. Retroactively invoking brainstorming after already writing a file defeats
> the purpose of the design-first step.
>
> **Summary:** The core failure is skipping the `superpowers:brainstorming` skill invocation that is required before
> creative/skill-creation work.

## Gaps Identified

The naked subagent's analysis is competent but missing the specific job
`/learn` exists to do. Gaps:

1. **No "misfire" vocabulary.** Subagent says "failure", "issue", "gap" —
   none of the skill-specific terms that tie a finding to an actionable
   skill edit.
2. **No misfire-vs-preference-shift classification.** Subagent treats every
   flagged behavior uniformly. `/learn` must distinguish "skill text was
   wrong" (fixable) from "user wants different behavior going forward"
   (design question, not a fix).
3. **No findings table.** Output is a prose list. `/learn` must produce
   rows with `skill · signal · evidence · classification · proposed-fix`
   for per-finding approval.
4. **No proposed fix targeting the skill itself.** Subagent names the gap
   but does not say "strengthen `/brainstorming`'s trigger phrasing" or
   "add a counter-rationalization for 'just a small skill'" — i.e.,
   concrete text to feed `/writing-skills`.
5. **No scope boundary.** Subagent conflates "what went wrong in this
   session" with "what should change going forward." `/learn` must stay
   narrowly focused on skill updates, not retrospective commentary.
6. **No approval gate mention.** Subagent volunteers a full analysis; no
   "approve / skip / reclassify" hand-off structure.

These six gaps are the specific shape `/learn`'s body must address for the
GREEN subagent (same fixture, with skill) to produce a qualitatively
different output.

## GREEN Verification Responsez

(Captured 2026-04-18; model: sonnet; `/learn` skill exposed at
`skills/learn/SKILL.md`.)

Subagent produced a findings table with the exact column set the playbook
prescribes, correctly classified the `/brainstorming` skip as **Misfire**
(not preference shift), proposed a specific fix ("add 'creating a new
skill file' as an explicit trigger example in the `brainstorming` skill"),
captured the observed rationalization verbatim ("Claude treated writing a
SKILL.md as a write task rather than creative work"), and terminated with
an `approve / skip / reclassify` hand-off row.

All six RED gaps addressed:

| Gap                | RED baseline         | GREEN result                         |
|--------------------|----------------------|--------------------------------------|
| Misfire vocabulary | "failure", "issue"   | "Misfire"                            |
| Classification     | conflated            | Misfire vs preference-shift explicit |
| Findings table     | prose                | five-column table                    |
| Concrete fix       | named gap only       | specific edit to brainstorming       |
| Scope boundary     | retrospective prose  | skill-update-only                    |
| Approval gate      | volunteered analysis | approve/skip/reclassify prompt       |

Skill is GREEN.