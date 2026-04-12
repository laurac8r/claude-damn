# Error Handlers

This document defines the five error classes recognized by the `sme-test` TDD
coach skill, along with their triggers, examples, and recovery paths.

---

## Error Class 1: Input Errors

**Trigger:** Malformed triples, unsupported language, missing target file, or
invalid `expert-auto` targets.

**Examples:**

- Triple uses wrong format (e.g., missing `Given`/`When`/`Then` structure)
- File path provided does not exist
- No adapter registered for the specified language
- `expert-auto` target has no detectable functions or methods

**Recovery:**

1. Display the specific problem clearly (e.g., "Triple is missing a `Then`
   clause").
2. Show the expected format with a concrete example.
3. List supported languages (v1: Python, Bats).
4. Prompt the user to supply valid input before proceeding.

---

## Error Class 2: Environment Errors

**Trigger:** Test runner not installed, wrong version, or missing dependencies
that prevent test execution.

**Examples:**

- `pytest` not found in the environment
- `bats` not installed or not on `PATH`
- Required test dependencies absent (e.g., `pytest-mock`)
- Python version incompatible with the target project

**Recovery:**

1. Detect the missing or incompatible tool via version probe.
2. Output installation instructions:
   - Python: `uv add --dev pytest`
   - Bats: `brew install bats-core`

3. Surface version mismatch details (required vs. found).
4. Re-run detection automatically after the user confirms the install.

---

## Error Class 3: Subagent Errors

**Trigger:** Subagent timeout, unexpected output format, or coordination failure
in the shared memory layer.

**Examples:**

- `test-writer` subagent times out during generation
- Subagent returns output that cannot be parsed as expected
- `shared/` memory file is missing or corrupt when a later stage reads it
- Subagent returns `BLOCKED` status

**Recovery:**

1. Retry the failed subagent once automatically.
2. On second failure, surface the raw subagent output for manual inspection.
3. If the failure is a coordination error (missing `shared/` file), re-run the
   prior stage that was supposed to produce that file.
4. Halt the workflow after two consecutive failures and report the stage that
   failed.

---

## Error Class 4: RED-Gate Errors

**Trigger:** Tests pass when they should fail — a false green that violates the
RED phase gate of the TDD cycle.

**Examples:**

- Assertion is trivially true and does not exercise real behavior
- Tests verify existing passing behavior rather than the new requirement
- Test contains a vacuous-pass bug (e.g., empty loop, condition always false)

**Recovery:**

1. **BLOCK** progression — never allow advancement to the GREEN phase while this
   error is active.
2. Display the full test output so the user can see exactly what passed.
3. Explain why a passing test at the RED gate is an error, not success.
4. Offer three resolution paths:
   - Review and revise the Given/When/Then triple
   - Inspect and fix the generated test code directly
   - Return to the 3-Whys diagnostic stage

5. Re-run the RED gate automatically after the user makes changes.

---

## Error Class 5: Safety-Refusal Errors

**Trigger:** A subagent refuses to generate test content due to content policy
or safety constraints.

**Examples:**

- Test pattern involves security-sensitive operations that trigger content
  moderation
- Prompt phrasing causes the subagent to refuse on policy grounds

**Recovery:**

1. Surface the refusal reason verbatim so the user understands what was blocked.
2. Offer resolution options:
   - Rephrase the Given/When/Then triple to avoid the triggering pattern
   - Switch to manual triple entry
   - Write the test stub manually and skip subagent generation for this triple

3. Never attempt to circumvent or work around the safety refusal.
4. Log the refusal event (triple text, reason, timestamp) in
   `shared/coach-state.md` for audit purposes.
