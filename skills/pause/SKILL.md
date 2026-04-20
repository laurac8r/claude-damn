---
name: pause
description:
   Use when wrapping up a session, parking work at a clean stop, or reaching a
   natural boundary where you want to close out current progress without
   starting new work
user-invocable: true
---

/check-yourself, then pause here for now.

## /recap and /learn are out-of-band

- **`/recap`** is a built-in Claude Code CLI command, NOT a skill. Do NOT try to
  invoke it via the Skill tool — `Skill(recap)` will error with "recap is a
  built-in CLI command, not a skill". If a retrospective fits the moment, invite
  the user to run `/recap` themselves.
- **`/learn`** is a skill, but optional here. Invoke it only if the user wants
  to review session misfires before stopping; otherwise mention it as available
  and move on.

**Rationalization counter:**

| Excuse                                                  | Reality                                                                                         |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| "The slash syntax implies I should Skill-invoke /recap" | `/recap` is a CLI command. Skill-invoking it produces an error; ask the user to run it instead. |
| "/learn is listed so I should always run it"            | It's marked optional — invoke only when the user asks or signals it's worthwhile.               |
