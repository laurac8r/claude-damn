# `git rev-parse` Safety — Script-Hardening Rule

`git rev-parse` is a **plumbing** command (stable, machine-parseable output)
rather than a porcelain command (human-readable). That makes it the right
tool for shell scripts, but its safety depends entirely on how inputs and
outputs are handled.

This rule is the canonical reference for agents writing or reviewing shell
that calls `git rev-parse`. The companion hook
`~/.claude/hooks/check_git_rev_parse.py` flags the high-risk patterns at
PreToolUse time on the `Bash` matcher (warn-mode, non-blocking).

## ✅ Safe uses

### 1. Verifying you are in a Git repository
Standard preflight check before running other Git commands.

```sh
git rev-parse --is-inside-work-tree   # prints "true" or "false"
```

### 2. Finding absolute paths
Resolve standard Git paths regardless of the caller's `cwd`. Hardcoding
paths in hooks or CI is brittle.

```sh
git rev-parse --show-toplevel   # absolute path of the work-tree root
git rev-parse --git-dir         # path to the .git directory
```

### 3. Resolving a single reference (with `--verify`)
`--verify` requires *exactly one* parameter and ensures it resolves to a
valid Git object. If the user passes `--all`, `--verify` errors out instead
of silently dumping every ref.

```sh
git rev-parse --verify HEAD
git rev-parse --verify main
```

### 4. Disambiguating revisions from file names
A branch and a file may share a name. Use `--` to declare "everything
after this is a path."

```sh
git rev-parse HEAD -- path/to/file
```

## ❌ Unsafe patterns (and the fixes)

### Pattern A — Passing user input without `--verify`

```sh
HASH=$(git rev-parse $USER_INPUT)        # 🚫 unsafe
HASH=$(git rev-parse --verify "$USER_INPUT") || exit 1   # ✅ safe
```

If `USER_INPUT` is `--all`, the unsafe form returns *every ref*, turning
`$HASH` into a multi-line monster that breaks the next consumer (e.g.
`git checkout $HASH`). `--verify` constrains the output to a single ref or
a non-zero exit.

### Pattern B — Failing to validate exit code

```sh
ROOT=$(git rev-parse --show-toplevel)    # 🚫 unsafe outside a repo
rm -rf $ROOT/tmp/                        # 💥 becomes `rm -rf /tmp/`
```

Outside a Git repo, `git rev-parse` fails and `$ROOT` is empty. Combine
with an unguarded `rm -rf` and you delete the wrong directory tree.

```sh
ROOT=$(git rev-parse --show-toplevel) || exit 1   # ✅ guarded
# or — top of the script:
set -e
```

### Pattern C — Unquoted variable expansion (shell injection)

```sh
git rev-parse $USER_INPUT                # 🚫 unquoted
git rev-parse --verify "$USER_INPUT"     # ✅ quoted + --verify
```

If `USER_INPUT=$'HEAD; rm -rf /'`, the unquoted form lets the shell
re-interpret the `;` and execute the second command. Always quote.

### Pattern D — Misusing `--parseopt` + `eval`

`git rev-parse --parseopt` parses flags for shell scripts. Its output is
designed to be `eval`'d, which means a malformed spec string or unquoted
output is an arbitrary-code-execution vector inside the script.

```sh
eval "$(git rev-parse --parseopt -- "$@" <<-EOF
USAGE: ...
EOF
)"
```

Either treat the eval site like any other untrusted-input boundary
(static spec string, never user-controlled), or skip `--parseopt` and
parse flags some other way.

## Rule of thumb

> **Always quote your variables, always use `--verify` when resolving
> references, and always explicitly check the command's exit code before
> proceeding.**

## Enforcement

`~/.claude/hooks/check_git_rev_parse.py` is registered as a `PreToolUse`
hook for the `Bash` matcher in `~/.claude/settings.local.json`. It is
**warn-mode**: it emits a `systemMessage` describing the suspect pattern
but does **not** block the tool call. The patterns it currently flags:

- **A** — `git rev-parse <unquoted $VAR>`
- **D** — `git rev-parse --parseopt` co-located with `eval` in the same
  command string

Patterns B and C are not auto-detected because they require multi-line
context the hook doesn't see; rely on this doc + review for those.

## If the hook warns

Read the message, decide whether the pattern is genuinely unsafe in the
context, and (if so) rewrite using the matching ✅ form above. The hook
does **not** block — proceed if you are sure.

## Cross-references

- Doc (this file): `~/.claude/rules/git_rev_parse_safety.md`
- Hook: `~/.claude/hooks/check_git_rev_parse.py`
- Hook tests: `~/.claude/tests/hooks/test_check_git_rev_parse.py`
- Settings registration: `~/.claude/settings.local.json` under
  `hooks.PreToolUse[matcher="Bash"]`
