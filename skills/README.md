# Skills

## Naming Convention

Skills are composed from modifiers. Each modifier maps to a specific underlying
skill:

| Modifier | Skill invoked                  | What it adds                                                    |
|----------|--------------------------------|-----------------------------------------------------------------|
| `super`  | `/brainstorming` + `/tdd`      | Brainstorm requirements and design, then implement using `/tdd` |
| `duper`  | `/using-git-worktrees`         | Isolated git worktree                                           |
| `cat`    | `/subagent-driven-development` | Parallel subagent execution                                     |
| `tdd`    | `/tdd`                         | Test-driven development                                         |

## Combinatorics

### Base: TDD

| Skill            | Modifiers         | Invokes                                                    |
|------------------|-------------------|------------------------------------------------------------|
| `/tdd`           | tdd               | /tdd                                                       |
| `/tdd-cat`       | tdd + cat         | /subagent-driven-development + /tdd                        |
| `/duper-tdd`     | duper + tdd       | /using-git-worktrees + /tdd                                |
| `/duper-tdd-cat` | duper + tdd + cat | /tdd + /using-git-worktrees + /subagent-driven-development |

### Base: Brainstorm + TDD

| Skill              | Modifiers                 | Invokes                                                                     |
|--------------------|---------------------------|-----------------------------------------------------------------------------|
| `/super`           | super + tdd               | /brainstorming + /tdd                                                       |
| `/super-cat`       | super + tdd + cat         | /brainstorming + /tdd + /subagent-driven-development                        |
| `/super-duper`     | super + duper + tdd       | /brainstorming + /tdd + /using-git-worktrees                                |
| `/super-duper-cat` | super + duper + tdd + cat | /brainstorming + /tdd + /using-git-worktrees + /subagent-driven-development |

### Base: Debug + Brainstorm + TDD

| Skill                            | Modifiers                         | Invokes                                                                                            |
|----------------------------------|-----------------------------------|----------------------------------------------------------------------------------------------------|
| `/super-debug-and-fix`           | super + debug + tdd               | /expert-review debug + /brainstorming + /tdd                                                       |
| `/super-debug-and-fix-cat`       | super + debug + tdd + cat         | /expert-review debug + /brainstorming + /tdd + /subagent-driven-development                        |
| `/super-duper-debug-and-fix`     | super + duper + debug + tdd       | /expert-review debug + /brainstorming + /tdd + /using-git-worktrees                                |
| `/super-duper-debug-and-fix-cat` | super + duper + debug + tdd + cat | /expert-review debug + /brainstorming + /tdd + /using-git-worktrees + /subagent-driven-development |

### Base: Expert Review

| Skill                            | Modifiers                          | Invokes                                                                                      |
|----------------------------------|------------------------------------|----------------------------------------------------------------------------------------------|
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

## Other Skills

| Skill                         | Purpose                                                                                                  |
|-------------------------------|----------------------------------------------------------------------------------------------------------|
| `/checkpoint-save`            | Save a resumable work checkpoint                                                                         |
| `/checkpoint-resume`          | Resume from a saved checkpoint                                                                           |
| `/fast-pr-feedback-to-me`     | Process code review feedback received on your PR                                                         |
| `/fast-pr-feedback-to-others` | Give code review feedback on a PR                                                                        |
| `/fast-pr-final-self-review`  | Self-review before merge                                                                                 |
| `/sync`                       | Sync files between two local directories/repos/worktrees (5 modes, .gitignore-aware, --claude allowlist) |
