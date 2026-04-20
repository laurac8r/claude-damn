# Copilot Instructions for `claude-damn`

These instructions guide GitHub Copilot code-review, Copilot Chat, and the
Copilot coding agent when working in this repository.

## Python version

- **`requires-python = ">=3.14"`** (see `pyproject.toml`). Do not flag features,
  syntax, or stdlib additions that are valid in Python 3.14+.

## PEP 758: `except` / `except*` without parentheses

[PEP 758](https://peps.python.org/pep-0758/) (accepted in Python 3.14) makes the
parentheses around multi-exception `except` and `except*` clauses **optional**.
Both forms below are valid and semantically identical on 3.14+:

```python
try:
    ...
except (UnicodeDecodeError, PermissionError):
    ...

try:
    ...
except UnicodeDecodeError, PermissionError:
    ...
```

The second form is **not** Python 2 `except-as-name` syntax (which was spelled
`except X, e:` and required exactly one exception type followed by a name). PEP
758's form requires *two or more* exception types and binds no name; the tuple
is unambiguous to the parser.

**Do NOT flag** `except A, B:` or `except* A, B:` as a `SyntaxError`, "Python 2
syntax," or a porting issue. This project targets 3.14+ only.

**Do NOT suggest** re-adding the parentheses — `ruff format` (≥ 0.15) strips
them back on the next run because they are syntactically redundant.

## Formatter discipline

- Formatting is handled by `ruff format` (Black-compatible defaults).
  `pyproject.toml` requires `ruff>=0.15.10`.
- If a snippet round-trips under `ruff format` to a form different from what
  Copilot wants to suggest, prefer the `ruff format` output — it is the source
  of truth for style in this repo.

## Lint

- `ruff check` rules enabled: `E`, `F`, `I` (see `ruff.toml`).
- Do not flag issues ruff would already catch.

## Project-specific conventions

See `CLAUDE.md` at the repository root for broader conventions (architecture,
testing standards, task workflow). Those conventions apply equally to Copilot
suggestions.