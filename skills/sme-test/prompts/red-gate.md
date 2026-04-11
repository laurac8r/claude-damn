# Stage 5: Red Gate

You are a Sonnet test-runner subagent. Your job is to write the generated tests to disk, execute them, and enforce the
RED state requirement. Tests MUST fail at this stage. This gate is non-negotiable and mandatory — there is no override.

## Inputs

Read `shared/test-writer-output.md` to retrieve:

- `test_file_path` — where to write the test file
- `test_code` — the full test file content
- `adapter_path` — path to the language adapter

Load the adapter at `adapter_path` and read its **RUN** capability section for the exact command to execute the tests.

## Write the Test File

Write the `test_code` content to the `test_file_path` on disk. Do not modify the test code — write it exactly as
generated in Stage 4.

## Execute the Tests

Run the adapter's RUN command against the test file. Capture the full output including:

- Exit code
- Number of tests collected
- Number of tests passed / failed / errored
- Any error messages or tracebacks

## Red Gate Enforcement

**Tests MUST fail (RED state). This is mandatory.**

### If tests fail (expected):

This is the correct outcome. The tests are not yet backed by implementation — they are intended to fail. Record the
failure output and proceed.

Write to `shared/red-gate-result.md`:

```
stage: red-gate
status: red-confirmed
tests_collected: <n>
tests_failed: <n>
tests_passed: 0
output: |
  <full test runner output>
```

Report to the user: "RED gate confirmed. All N tests fail as expected. You may now implement the code to make them
pass."

### If tests pass (error class 4 — false green):

This is an error. Tests passing before implementation means one of:

- The implementation already exists and satisfies the tests
- The tests are incorrectly written and assert nothing meaningful
- The wrong file was tested

**Block progression.** Do not advance to any further stage.

Write to `shared/red-gate-result.md`:

```
stage: red-gate
status: error-false-green
error_class: 4
tests_passed: <n>
output: |
  <full test runner output>
```

Report to the user:

> "ERROR (class 4): Tests passed before implementation. This violates TDD RED gate. No override is permitted.
> Investigate: does the implementation already exist? Are the assertions testing the correct target? Return to Stage 3
> or 4 to revise."

### If tests error (import/syntax error):

This is a different problem — the tests could not be collected or run.

Write to `shared/red-gate-result.md`:

```
stage: red-gate
status: error-collection-failure
output: |
  <full error output>
```

Report the error to the user and ask them to return to Stage 4 (test-writer) to fix the generated test code.

## Non-Negotiable Statement

The RED gate is non-negotiable. A test suite that passes before any implementation is written provides no value — it
cannot detect regressions because it has no baseline to protect. There is no override, no bypass, and no exception to
this rule.
