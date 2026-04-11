---
name: sme-test
description:
  "TDD coach: guides users through Given/When/Then test design using a Subject Matter Expert approach. Use when writing
  new tests, adding test coverage, or learning TDD patterns."
user-invocable: true
argument-hint: "[file|function] [--expert|-x] [--auto|-xa]"
---

# sme-test: Subject Matter Expert TDD Coach

A coaching-driven TDD workflow that teaches you to think in Given/When/Then triples before writing test code.

**Arguments:** "$ARGUMENTS"

---

## Mode Dispatch

Parse arguments to determine mode:

| Input                      | Mode            | Flow                                                          |
| -------------------------- | --------------- | ------------------------------------------------------------- |
| (default)                  | **Coach**       | Full 6-stage coaching flow with 3-Whys dialogue               |
| `--expert` or `-x`         | **Expert**      | Single-turn: paste G/W/T triples directly, skip coaching      |
| `--expert --auto` or `-xa` | **Expert-Auto** | Auto-infer triples from code scan with mandatory preview gate |

`--auto --yes` is **not a valid flag combination** — the preview gate cannot be bypassed.

**Escape hatches (available at any prompt in expert/expert-auto modes):**

- Type `coach` → bail up to full coach mode (3-Whys flow)
- Type `paste` → bail sideways to manual triple entry (expert mode)

---

## Coach Mode (Default) — 6-Stage Flow

### Stage 1: Dispatch

Read the prompt from `prompts/coach-dispatch.md` and execute it.

Detect the target code file/function from arguments. Identify the project language using the adapter DETECT capability.
Select the appropriate adapter from `adapters/`. Load any existing `shared/` memory state from prior sessions.

**Subagent:** test-coach (Opus) — judgment-heavy, needs deep reasoning for intent extraction.

### Stage 2: 3-Whys

Read the prompt from `prompts/three-whys.md` and execute it.

Ask three progressive "why" questions to surface the real behavioral intent behind the user's test request. Do not
accept "test this function" as sufficient — probe until a concrete behavioral contract emerges.

**Subagent:** test-coach (Opus) — conversational coaching requires judgment.

### Stage 3: G/W/T Formulation

Read the prompt from `prompts/gwt-formulation.md` and execute it.

Guide the user to translate 3-Whys answers into Given/When/Then triples. Each triple must be concrete, testable, and
non-redundant. Validate each triple before accepting.

**Subagent:** test-coach (Opus) — triple validation requires judgment.

### Stage 4: Test-Writer Delegation

Read the prompt from `prompts/test-writer.md` and execute it.

Dispatch a Sonnet subagent (test-writer) with the approved triples and the selected language adapter. The subagent
generates executable test code. Stage output for user review before proceeding.

**Subagent:** test-writer (Sonnet) — structured code generation from approved triples, no deep judgment needed.

Write subagent state to `shared/test-writer-output.md`. Read all files in `shared/` before dispatching.

### Stage 5: RED Gate

Read the prompt from `prompts/red-gate.md` and execute it.

Dispatch a Sonnet subagent (test-runner) to execute the generated tests. The tests **MUST fail** (red state). This gate
is **mandatory** — there is **no override**. If tests pass, this is an error (see error class 4 in
`errors/error-handlers.md`).

**Subagent:** test-runner (Sonnet) — test execution is deterministic, no reasoning needed.

Write subagent state to `shared/red-gate-result.md`. Read all files in `shared/` before dispatching.

### Stage 6: Handoff

Present the failing tests to the user. Offer handoff options:

- Continue manually — user writes implementation code
- Handoff to `/tdd` — use the TDD skill for RED→GREEN→REFACTOR
- Handoff to `/duper-tdd` — TDD in an isolated worktree

---

## Expert Mode (`--expert` / `-x`)

Skip Stages 2-3 (no 3-Whys, no coached G/W/T formulation).

1. Prompt user to paste Given/When/Then triples in structured format
2. Parse triples (no per-triple critique — trust the expert user)
3. Proceed directly to Stage 4 (test-writer delegation)
4. RED gate (Stage 5) remains **mandatory**
5. Handoff (Stage 6)

**Model routing:** Sonnet-only — no Opus subagent required. Parsing structured input does not require deep reasoning.

---

## Expert-Auto Mode (`--expert --auto` / `-xa`)

Replace Stages 2-3 with automated triple inference.

1. **Code scan:** test-coach (Opus) scans target file, infers triples from function signatures and docstrings
2. **Provenance tags:** Each inferred triple carries a tag identifying which function/signature it was inferred from
3. **Cap:** Maximum **8 triples** per invocation (hard cap)
4. **Mandatory preview gate:** User sees all inferred triples and must explicitly:
   - **(k)eep all** — accept all triples
   - **(d)rop N** — remove specific triples
   - **(a)dd** — add custom triples
   - **(abort)** — cancel entirely

5. Proceed to Stage 4 → Stage 5 (RED gate mandatory) → Stage 6 (handoff)

**Model routing:** test-coach on Opus for inference quality (code understanding + triple generation).

---

## Subagent Coordination

All subagents coordinate via the `shared/` memory directory pattern (per CLAUDE.md):

| Subagent    | Model                         | Stages | Writes to `shared/`            |
| ----------- | ----------------------------- | ------ | ------------------------------ |
| test-coach  | Opus (coach), Sonnet (expert) | 1-3    | `shared/coach-state.md`        |
| test-writer | Sonnet                        | 4      | `shared/test-writer-output.md` |
| test-runner | Sonnet                        | 5      | `shared/red-gate-result.md`    |

**Rules:**

- Each subagent writes only its own file in `shared/`
- Each subagent reads all files in `shared/` on startup
- Main skill agent manages cleanup and compacts to `COMBINED.md` after subagent completion
- No subagent modifies `COMBINED.md` directly

---

## Error Handling

See `errors/error-handlers.md` for the 5 error classes and recovery paths:

1. **Input errors** — malformed triples, unsupported language, missing target
2. **Environment errors** — test runner not installed, wrong version, missing deps
3. **Subagent errors** — timeout, unexpected output, coordination failure
4. **RED-gate errors** — tests pass when they should fail (false green)
5. **Safety-refusal errors** — subagent refuses to generate test

---

## Adapter Contract

All language adapters implement 4 capabilities: **DETECT**, **GENERATE**, **RUN**, **EXPLAIN**.

v1 adapters:

- `adapters/python/adapter.md` — pytest
- `adapters/bats/adapter.md` — bats (N-block parametrize limitation documented)
