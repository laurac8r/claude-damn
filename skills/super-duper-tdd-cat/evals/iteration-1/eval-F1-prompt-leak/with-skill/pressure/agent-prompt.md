# F1 with-skill — agent's written subagent prompt

## VERDICT — GREEN ✓

The skill discipline (§1) was applied. No absolute path leaked. Agent cites the
rule directly.

## Agent's written prompt (verbatim)

> **<hypothesis-name> Worker — Subagent Prompt**
>
> You are testing the <hypothesis-name> hypothesis: that a real
> `MethodChannel('<channel-id>')` call hangs indefinitely in the test framework
> because there is no registered mock handler, so the platform side never
> replies. The fix under test is adding a timeout on the channel call so the
> test can complete.
>
> **Branch state**
>
> You are already inside your own isolated worktree. Do not touch any other
> directory.
>
> 1. Confirm you are on branch `<feature-branch>` at HEAD `<commit-sha>`:
>    ```
>    git rev-parse --verify HEAD
>    ```
>    If the SHA does not match `<commit-sha>`, stop and report the mismatch.
> 2. Apply the WIP stash:
>    ```
>    git stash apply stash^{/<wip-stash-name>}
>    ```
>    This restores the broken `<app-subdir>/lib/main.dart` and
>    `<app-subdir>/test/widget_test.dart`.
>
> [...rest of prompt covers fix application + report format, all using >
> `<placeholder>` syntax...]

## Agent's rationale (verbatim, citing rules)

> The prompt includes the branch name (`<feature-branch>`), HEAD commit SHA
> (`<commit-sha>`), and stash message ( `<wip-stash-name>`) as load-bearing
> context — exactly what the skill's §1 rule marks as permitted. The parent
> worktree's absolute filesystem path (`$HOME/.../.worktrees/<branch>/`) is
> entirely absent. The Agent tool's `isolation: "worktree"` flag already places
> the subagent in its own cwd, so including the parent path would only create an
> edit-leak vector where the subagent might resolve it as a target directory
> instead of its own. All file references are expressed as relative paths within
> the worktree (`<app-subdir>/lib/main.dart`,
> `<app-subdir>/test/widget_test.dart`), per the rule's concrete checklist.

## Comparison to baseline

| Aspect           | Baseline                                                         | With-skill                                                     |
| ---------------- | ---------------------------------------------------------------- | -------------------------------------------------------------- |
| Project location | `<absolute-path-to-parent-worktree>` (absolute path leak)        | absent — explicit "Do not touch any other directory"           |
| Branch reference | `<feature-branch>` placeholder                                   | `<feature-branch>` placeholder                                 |
| Cwd guidance     | Inferred ("Verify cwd is under `.claude/worktrees/agent-<id>/`") | Explicit ("You are already inside your own isolated worktree") |
| Cite rules?      | No                                                               | Yes, §1 directly                                               |

No new rationalizations surfaced.
