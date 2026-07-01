# Skills

## Naming Convention

Skills are composed from modifiers. Each modifier maps to a specific underlying
skill:

| Modifier         | Skill invoked                  | What it adds                                                    |
| ---------------- | ------------------------------ | --------------------------------------------------------------- |
| `super`          | `/brainstorming` + `/tdd`      | Brainstorm requirements and design, then implement using `/tdd` |
| `duper`          | `/using-git-worktrees`         | Isolated git worktree                                           |
| `cat`            | `/subagent-driven-development` | Parallel subagent execution                                     |
| `tdd`            | `/tdd`                         | Test-driven development                                         |
| `fixer`          | `/expert-review` (debug) + `/systematic-debugging` | Debug the root cause, then fix             |
| `skill-creator`  | `/skill-creator`               | Skill scaffolding + quant eval grid                             |
| `writing-skills` | `/writing-skills`              | Pressure-scenario testing + rationalization tables              |

## Combinatorics

### Base: TDD

| Skill            | Modifiers         | Invokes                                                    |
| ---------------- | ----------------- | ---------------------------------------------------------- |
| `/tdd`           | tdd               | /tdd                                                       |
| `/tdd-cat`       | tdd + cat         | /subagent-driven-development + /tdd                        |
| `/duper-tdd`     | duper + tdd       | /using-git-worktrees + /tdd                                |
| `/duper-tdd-cat` | duper + tdd + cat | /tdd + /using-git-worktrees + /subagent-driven-development |

### Base: Brainstorm + TDD

| Skill              | Modifiers                 | Invokes                                                                     |
| ------------------ | ------------------------- | --------------------------------------------------------------------------- |
| `/super`           | super + tdd               | /brainstorming + /tdd                                                       |
| `/super-cat`       | super + tdd + cat         | /brainstorming + /tdd + /subagent-driven-development                        |
| `/super-duper`     | super + duper + tdd       | /brainstorming + /tdd + /using-git-worktrees                                |
| `/super-duper-cat` | super + duper + tdd + cat | /brainstorming + /tdd + /using-git-worktrees + /subagent-driven-development |

### Base: Debug + Fix (fixer)

The `fixer` skills run `/expert-review debug` first, then fix using the matching
`/super*` skill (bare `/fixer` is an alias for `/systematic-debugging`).

| Skill                        | Modifiers                         | Invokes                                                                                              |
| ---------------------------- | --------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `/fixer`                     | fixer                             | /systematic-debugging                                                                                |
| `/super-fixer`               | super + fixer                     | /expert-review (debug) + /brainstorming + /tdd                                                       |
| `/super-fixer-cat`           | super + fixer + cat               | /expert-review (debug) + /brainstorming + /tdd + /subagent-driven-development                        |
| `/super-duper-fixer`         | super + duper + fixer             | /expert-review (debug) + /brainstorming + /tdd + /using-git-worktrees                                |
| `/super-duper-fixer-cat`     | super + duper + fixer + cat       | /expert-review (debug) + /brainstorming + /tdd + /using-git-worktrees + /subagent-driven-development |
| `/super-duper-fixer-tdd-cat` | super + duper + tdd + fixer + cat | /expert-review (debug) + /brainstorming + /tdd + /using-git-worktrees + /subagent-driven-development |

### Base: Expert Review

| Skill                            | Modifiers                          | Invokes                                                                                      |
| -------------------------------- | ---------------------------------- | -------------------------------------------------------------------------------------------- |
| `/expert-review`                 | expert                             | /expert-review                                                                               |
| `/expert-cat-review`             | expert + cat                       | /expert-review (parallel subagent phases)                                                    |
| `/expert-tdd-review`             | expert + tdd                       | /expert-review + /tdd                                                                        |
| `/expert-tdd-cat-review`         | expert + tdd + cat                 | /expert-review + /tdd + /subagent-driven-development                                         |
| `/expert-super-review`           | expert + super + tdd               | /expert-review + /brainstorming + /tdd                                                       |
| `/expert-super-cat-review`       | expert + super + tdd + cat         | /expert-review + /brainstorming + /tdd + /subagent-driven-development                        |
| `/expert-duper-tdd-review`       | expert + duper + tdd               | /expert-review + /tdd + /using-git-worktrees                                                 |
| `/expert-duper-tdd-cat-review`   | expert + duper + tdd + cat         | /expert-review + /tdd + /using-git-worktrees + /subagent-driven-development                  |
| `/expert-super-duper-review`     | expert + super + duper + tdd       | /expert-review + /brainstorming + /tdd + /using-git-worktrees                                |
| `/expert-super-duper-cat-review` | expert + super + duper + tdd + cat | /expert-review + /brainstorming + /tdd + /using-git-worktrees + /subagent-driven-development |
| `/expert-super-tdd-review`       | expert + super + tdd               | /expert-review + /brainstorming + /tdd                                                       |
| `/expert-super-tdd-cat-review`   | expert + super + tdd + cat         | /expert-review + /brainstorming + /tdd + /subagent-driven-development                        |
| `/expert-super-duper-tdd-review` | expert + super + duper + tdd       | /expert-review + /brainstorming + /tdd + /using-git-worktrees                                |
| `/expert-super-duper-tdd-cat-review` | expert + super + duper + tdd + cat | /expert-review + /brainstorming + /tdd + /using-git-worktrees + /subagent-driven-development |

`/expert-final-review` is a final pre-merge gate that composes review skills in
sequence rather than via the modifier matrix:

| Skill                   | Composition                                                                  |
| ----------------------- | --------------------------------------------------------------------------- |
| `/expert-final-review`  | `/fast-pr-final-self-review` (confirm PR feedback addressed) → `/expert-review all` (full sweep) → one go/no-go summary |

### Base: Skill Creation

| Skill                    | Modifiers                                            | Invokes                                                                                                        |
| ------------------------ | ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `/lets-make-a-skill`     | skill-creator + super + duper + cat + writing-skills | /skill-creator + /brainstorming + /tdd + /using-git-worktrees + /subagent-driven-development + /writing-skills |

## Other Skills

| Skill                         | Purpose                                                                                                  |
| ----------------------------- | -------------------------------------------------------------------------------------------------------- |
| `/checkpoint-save`            | Save a resumable work checkpoint                                                                         |
| `/checkpoint-resume`          | Resume from a saved checkpoint                                                                           |
| `/listen`                     | Execute instructions while invoking every `/skill` referenced in them                                    |
| `/proceed`                    | Signal single-gate alignment — authorize Claude to pass the current approval gate only                   |
| `/fast-pr-feedback-to-me`     | Process code review feedback received on your PR                                                         |
| `/fast-pr-feedback-to-others` | Give code review feedback on a PR                                                                        |
| `/fast-pr-final-self-review`  | Self-review before merge                                                                                 |
| `/sync`                       | Sync files between two local directories/repos/worktrees (5 modes, .gitignore-aware, --claude allowlist) |
| `/atlas`                      | Single-page "where am I / done / next" session survey (read-only)                                        |
| `/tesseract`                  | Cross-session arc of an anchor via git / memory / shelf / bulk-beings                                     |
| `/visual-aid`                 | Render a topic as a single self-contained HTML page                                                      |
| `/legal-visual-aid`           | Review a contract, then render findings as an HTML visual aid                                            |
| `/learn`                      | Review the session for skill misfires; propose fixes for approval                                       |
| `/pause`                      | Wrap up at a clean stop without starting new work                                                       |
| `/check-yourself`             | Update the task list and save a checkpoint at each step boundary                                        |
| `/task-list`                  | Create / update / render the session TaskList                                                           |
| `/add-to-roadmap`             | Append a task to a ROADMAP.md phase or section (with confirmation)                                      |
| `/review`                     | Review a GitHub pull request for bugs and improvements                                                  |
| `/address-pr-feedback`        | Plan and address unaddressed PR feedback on the current branch                                          |
| `/draft-cmt-msg-4-below`      | Draft a commit message for the changes below                                                            |
| `/sme-test`                   | TDD coach: Given/When/Then test design via a subject-matter-expert approach                             |
| `/cost_`                      | Extract and log the current session's token cost                                                        |
| `/cost-opt`                   | Compact cost logs, recalibrate pricing, surface optimizations                                           |
| `/continue`                   | Retry the last tool use the user interrupted                                                            |
| `/jcvd`                       | Open a Jean-Claude Van Damme movie in the browser                                                       |
