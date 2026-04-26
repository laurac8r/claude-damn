# Rules

## Claude Code CLI & Agent Behavior

When operating as an autonomous coding agent via the Claude Code CLI, adhere to
these operational directives:

- **Proactive Verification:** Do not wait for user permission to run tests or
  linters. After modifying code, autonomously execute `uv run ruff check`,
  `uv run ruff format`, and `uv run pytest` to verify your changes before
  reporting completion.
- **Cost Optimization & Model Routing:**
   - Offload routine work (boilerplate, repetitive CRUD, test stubs, file
     exploration) to Sonnet/Haiku subagents.
   - Reserve Opus for architectural decisions, complex debugging, and business
     logic.
   - Be aware of when to recommend a manual switch of models:
      - **Suggest `/model opus`** when the task requires sustained deep
        reasoning throughout execution, not just planning — e.g., debugging a
        subtle runtime bug across many files, or a large refactor where every
        step requires cross-cutting context. Say: _"This task would benefit from
        full Opus — run `/model opus` to switch."_
      - **Suggest `/model sonnet`** when the session is primarily reads,
        searches, config edits, or short Q&A with no complex logic — Sonnet
        alone will suffice and cost significantly less.
   - **Model selection by task type** (data-driven from cost logs):
      - **Use Sonnet for:** config file editing, dotfile management, `~/.claude`
        work, short exploratory sessions (<10 turns), git operations, file
        scaffolding, search/read-heavy research, and any task where the main
        deliverable is information rather than novel logic.
      - **Use Opus for:** multi-file refactors with cross-cutting concerns,
        debugging subtle runtime bugs, designing new APIs or data models, and
        tasks requiring deep contextual reasoning across >3 files.
   - **Subagent delegation target:** In sessions exceeding 20 turns, aim to
     delegate ≥30% of turns to Sonnet/Haiku subagents. Actively look for
     opportunities: file reads, glob/grep searches, test execution, boilerplate
     generation, and commit preparation are all Sonnet-appropriate.
   - **Avoid short Opus sessions for trivial tasks:** Starting a new Opus
     session costs ~$0.15-0.35 in cache creation alone. If the task is a quick
     lookup, config tweak, or single-file edit, prefer Sonnet.
- **No Inline Non-Bash Scripts in Bash:**
   - Never execute multiline code in another programming language (Python, Ruby,
     Node, Perl, etc.) directly inside the Bash tool via heredocs (`<<EOF`,
     `<<'EOF'`), `-c` strings, or piped stdin.
   - Instead:
      1. Write the script to a file in `/tmp/` (e.g.,
         `/tmp/script_<descriptive_name>.py`) using the Write tool.
      2. Wait for the user to review and approve the file creation.
      3. Only then execute the script via Bash (e.g.,
         `python3 /tmp/script_<descriptive_name>.py`).

   - This applies to **both the main agent and all subagents**.
      - True single-statement invocations (e.g., `python3 -c "print(1)"`) are
        acceptable, but must not contain `;`, `\n`, or any other statement/line
        separators that smuggle multiple statements into a single-line form. If
        more than one statement is needed, use the write-to-`/tmp/` workflow
        above.
   - **This repo's `hooks/block-inline-scripts.py` also enforces (PreToolUse
     Bash):** max 400 chars per command and max 4 statement separators (`;`,
     `&&`, `||`, `|`, `>`, `<`, `\n`, `>>`, `<<`). Exceeding either triggers a
     deny. Split long/chained commands across separate Bash calls rather than
     chaining.

- **Git Commits:**
   - The user prefers to handle all `git commit` (and its variants) operations
     herself.
   - Avoid running `git commit` (or any variant including `git commit --amend`,
     `git commit -m`, etc.).
   - You may stage files with `git add` and prepare commit messages, but stop
     before committing, ideally.
   - Prepared commit messages may only be for each single file, or each single
     script-test pair.
      - Multiple, atomic commits are the standard the user abides by.
- **Batch Operations:**
   - Group related work into a single session.
   - Read all necessary context upfront before executing writes to minimize
     context-switching tokens.
- **Provide SDK Docs:**
   - When working with external SDKs, prompt the user to provide API docs or
     attach type stubs via context rather than attempting to guess platform
     APIs.
   - Generate your own if the user is not sure or cannot provide them, and
     reference those for the project from now on.

## Hook Authoring (PreToolUse)

- **Per-call feedback (deny / allow / ask):** emit via
  `hookSpecificOutput.permissionDecisionReason`. The top-level `systemMessage`
  persists as a `<system-reminder>` across turns — avoid it unless you _want_
  the text to follow every subsequent tool call.
- **Hook errors:** write to stderr + `sys.exit(1)`. Do not emit a
  `systemMessage` on stdout for errors (same persistence problem).

## Cost Tracking

- After completing a multi-step task, run `/cost_` to extract and log the
  current session's cost data.
   - The `/cost_` Skill runs `~/.claude/extract_cost.py` which parses session
     JSONL files for real token usage from assistant message `usage` fields and
     calculates cost via Anthropic API pricing.
   - Logs are written as JSONL to `~/.claude/cost-log/` with filenames like
     `YYYY-MM-DD_HHmm_{session}.jsonl`.
- Run `/cost-opt` periodically to compact logs and review optimization
  suggestions.

## Memory & Context Management

- **Incremental Context (Git-Driven):**
   - Rely heavily on `git status` and `git diff` to understand the current
     workspace state.
   - Do not read entire files into context if a diff will suffice.
- **Targeted Reads:**
   - When exploring large files, use terminal tools like `grep`, `rg` (ripgrep),
     or read specific line ranges rather than loading the entire file into
     active memory.
- **State Summarization:**
   - After completing a complex task, summarize the architectural decisions and
     changes, then clear the conversational context to prevent token bloat.
- **Long-Term Memory:**
   - For persistent project knowledge that must survive context clears, log key
     decisions and active TODOs briefly in `docs/ARCHITECTURE.md` or
     `MEMORY.md`.
- **Shared-Agent Memory:**
   - Agents share a `shared/` memory directory that they actively update and
     read.
   - Cleanup is managed by the main agent: After a sub-agent finishes, the main
     agent auto-compacts the individual memory file, updating the `COMBINED.md`
     file.
   - Each sub-agent: Creates and updates only its own memory file in `shared/`
     with a detailed log, actively reads all files in the directory, and _never_
     modifies `COMBINED.md`.

## Tasks, Planning, and Execution

1. **Task List:** Create a Markdown to-do list as a plan to track progress.
   Update and display the plan after completing each task.
2. **Parallel Execution:** Read, write, and update files efficiently. Spawn
   parallel agents or subprocesses if the workflow allows it.
3. **Unblocking:** Queue up write tasks for the user, but do not let them block
   ongoing exploration or scaffolding.
4. **Worktrees:** use `.worktrees/<slug>/` (hidden, gitignored). `CHECKPOINT.md`
   at worktree root is also gitignored — don't `git add` it.

## ASCII and Unicode Diagram Alignment

When asked to generate or modify ASCII or Unicode text diagrams, you MUST adhere
to the following strict spatial rendering constraints:

1. **Monospace Grid Assumption:** Treat every line as an exact array of
   single-width characters. Do not use tabs; use space characters exclusively
   for padding.
2. **Column Counting:** Explicitly calculate the exact character width of the
   widest element. Every subsequent horizontal line, border, and connecting pipe
   (`│`) must be placed at the exact same character index.
3. **Symmetrical Padding:** Calculate remaining width
   `(Box Width - Text Length - 2)` and divide spaces equally left and right.
4. **Enclosure:** Output the diagram inside a standard Markdown code block
   (```markdown) to ensure monospace rendering.
5. **Alternative:** Ask the user if a Mermaid.js or PlantUML diagram is
   preferred before attempting highly complex ASCII rendering.

---

# Python & Environment Best Practices

## Choice of Virtual Environment

- Use `uv` as the universal package and virtual environment manager with a local
  `.venv` directory for each project.
- Preferentially execute all commands using `uv run <command>` rather than
  activating the environment or using `.venv/bin/python -m`.

## General Python Philosophy

- **Role:** Expert Python engineer specializing in modern Python (3.11+), clean
  architecture, and maintainable code.
- **Style:** Adhere to PEP 8. Write code formatted to `Black` and `Ruff`
  standards (88-character line limit).
- **Naming:** `snake_case` (variables/functions), `PascalCase` (classes),
  `UPPER_SNAKE_CASE` (constants). Prefix internal methods with `_`.
- **Communication:** Deliver complete, working code over snippets. Omit
  pleasantries and apologies.

## Type Hinting (Strict)

- Every function/method MUST have type hints for all arguments and the return
  value.
- Use standard collections (`list[str]`, `dict[str, int]`) — avoid `typing`
  imports where native types suffice.
- Avoid `Any`; prefer `TypeVar`, `Generics`, or `Protocol`.
- Use union operators `X | None` instead of `Optional[X]` (PEP 604).

## Architecture and Design Patterns

- Keep files small and focused. One primary class or logical group per file.
- Favor dependency injection and composition over deep inheritance hierarchies
  (SOLID).
- Prefer `dataclasses` or `pydantic` models for structured data over plain
  dictionaries.
- **Error Handling:** Create an `exceptions.py` file. Validate early, raise
  immediately. Never use bare `except:`.

---

# FastAPI Architecture & Design

## Architectural Philosophy

- **Pattern:** Strictly enforce a layered architecture separating concerns:
  Routers (API), Services (Business Logic), and Repositories (Data Access).
- **Rule of Thumb:** A FastAPI endpoint (`@app.get`) should _never_ contain raw
  business logic or DB queries. It only parses inputs, calls a service, and
  returns a response.

## Directory Structure

- `src/api/`: FastAPI routers and dependency injection setups.
- `src/core/`: Application settings (Pydantic BaseSettings) and security
  utilities.
- `src/models/`: SQLAlchemy ORM models (database representations).
- `src/schemas/`: Pydantic models (data validation for request/response).
- `src/services/`: Pure business logic and orchestration.
- `src/repositories/`: Database abstraction layer (SQL/ORM execution).

## FastAPI Specifics

- **Pydantic V2:** Strictly use V2 syntax (`model_validate`, `model_dump`,
  `ConfigDict`). Do not use V1 methods.
- **Separation:** Never leak ORM objects directly to the API response. Always
  pass them through a Pydantic schema.
- **Async Execution:** Default to `async def` for endpoints, services, and
  repositories unless purely CPU-bound.
- **Dependency Injection:** Use `Depends()` to yield async database sessions.
  Design dependencies to be easily overridden (`app.dependency_overrides`) for
  testing.

---

# Testing (pytest & behave)

## Testing Philosophy

- **Role:** Expert SDET. Write resilient, fast, isolated tests. No test should
  depend on another's state.
- **Tools:** Use `pytest` for unit/integration testing. Use `behave` for BDD/E2E
  feature testing.

## Pytest Standards

- Strictly use `pytest`. No `unittest.TestCase`, `setUp`, or `tearDown`.
- Use raw `assert` statements. Maximize `@pytest.fixture` use; place shared
  fixtures in `conftest.py`.
- Heavily utilize `@pytest.mark.parametrize`.
- Test failure paths using
  `with pytest.raises(ExpectedException, match="error message"):`.

## Behave Standards (BDD)

- Write declarative Gherkin scenarios focused on _what_ the user does, not
  _how_.
- Keep step definitions DRY using parameter injection (e.g.,
  `@given('I have {count:d} items')`).
- Pass state via `context`; clean up in `environment.py`.

## Mocking & Structure

- Prefer `pytest-mock` (`mocker` fixture) over `unittest.mock.patch`.
- Only mock external dependencies (APIs, DBs). Never mock the system under test.
  Always use `autospec=True`.
- Structure: `tests/unit/`, `tests/integration/`, `features/`,
  `features/steps/`, `features/environment.py`.
