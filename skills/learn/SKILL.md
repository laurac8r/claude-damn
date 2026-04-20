---
name: learn
description:
  Use when you want to review the current session for skills that misfired
  (skipped, invoked-but-ignored, or triggered user corrections) and update
  them — scans the active transcript, classifies findings, and delegates
  fixes to /writing-skills with per-finding approval
user-invocable: true
---

# Learn From This Session

Invoked at the end of (or partway through) a session. `/learn` reviews the
active transcript, identifies skills that **misfired**, and delegates fixes
to `/writing-skills` — with a per-finding approval gate between detection
and edit.

**First action:** Invoke `/listen` with this argument:

> `/writing-skills update any skill that misfired in the current session, following the analysis playbook below.`

`/listen`'s enforcement layer guarantees `/writing-skills` is invoked for
each approved finding. The playbook below is the work content `/listen`
carries forward.

## Analysis Playbook

### 1. Locate the transcript

Current session = most recently modified `*.jsonl` file in
`~/.claude/projects/<slug>/`, where `<slug>` is the current working
directory with `/` replaced by `-`, then any leading `-` stripped.

If the directory is missing or the newest file is ambiguous (multiple files
touched within the last second), ask the user to confirm or paste the
session ID.

### 2. Scan for misfire signals

Review the transcript in two passes:

1. For each `Skill` tool-call in the transcript, inspect the invocation, its
   output, and the next ~3 user/assistant turns.
2. Also scan the surrounding user requests and Claude actions for places
   where a skill *should* have been invoked based on its description, but
   was never called at all — this is how **Skipped** findings surface,
   since by definition they leave no tool-call to iterate over.

| Signal                                           | What it looks like                                                                                                                    |
|--------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| **Skipped**                                      | A skill's description clearly matched the task, but the skill was never invoked                                                       |
| **Invoked-but-ignored**                          | The skill was invoked, and Claude's next action directly contradicts its instructions                                                 |
| **User correction**                              | User writes "wait", "hold up", "hmm", "double check", "no", "don't", "stop", "that's wrong", "why did you…" within 3 turns of a skill |
| **User invokes another skill to course-correct** | User invokes another skill to double-check output, logic, consistency, security, actions, or tool use in this session                 |
| **Discarded output**                             | User reverts or overrides the artifact the skill produced                                                                             |
| **Hook-rejection loop**                          | A blocked action is retried after rejection — a skill should have prevented the first try                                             |
| **Re-prompt**                                    | User restates or clarifies the same request — skill interpreted it wrongly                                                            |

Also capture the **rationalization verbatim** — the sentence Claude used to
justify the misfire. `/writing-skills` needs this to add a specific counter.

### 3. Classify each finding

- **Misfire** — the skill's text is wrong, incomplete, or its triggers
  don't match the scenario. Fixable via `/writing-skills`.
- **Preference shift** — the skill followed its text faithfully; the user
  simply wants different behavior going forward. Report separately; **do
  not auto-update**.

Decision rule: "would a careful reading of this skill have produced the
user's preferred behavior?" Yes → preference shift. No → misfire.

### 4. Present findings

One row per finding:

```
skill · signal · evidence (line refs) · classification · proposed-fix
```

For each row ask: **approve**, **skip**, or **reclassify**.

### 5. Apply approved fixes

For each approved misfire, invoke `/writing-skills` with:

- the skill's file path,
- the observed rationalization/gap (verbatim),
- enough context for a pressure scenario.

`/writing-skills` carries its own TDD discipline — do not bypass it.

### 6. Update scope

Edits are allowed in:

- `~/.claude/skills/` (user skills)
- `<cwd>/.claude/skills/` (project skills, if the directory exists)

Plugin-cache skills under `~/.claude/plugins/cache/**` are **read-only** —
plugin updates overwrite local edits. If a misfire lives there, surface
the finding but do not edit.

## What This Skill Does NOT Do

- Does not edit skills in the plugin cache.
- Does not apply fixes without per-finding approval.
- Does not analyze sessions other than the current one.
- Does not treat every user correction as a skill bug — preference shifts
  are filtered out and reported separately.
- Does not summarize or moralize about Claude's performance — output is a
  findings table, not a retrospective.

## Edge Cases

- **No skills used** → report "no skill invocations found" and exit.
- **All skills used correctly** → report "no misfires detected".
- **All findings are preference shifts** → surface as a design-question
  list, do not call `/writing-skills`.
- **Misfire lives in plugin cache** → surface, note it cannot be edited,
  suggest filing upstream.
- **Transcript unreadable / JSONL corrupt** → report the error; do not
  proceed blindly.