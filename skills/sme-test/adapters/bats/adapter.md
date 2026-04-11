# Bats (Bash Automated Testing System) Adapter

This adapter translates Given/When/Then test triples into bats test code.

## DETECT

Identify a bats/shell project by checking for these signals (strongest-first):

1. `.bats` files present anywhere in the repository — highest confidence.
2. `test_helper/` directory at the project root (conventional bats helper layout).
3. `bats` listed as a dependency in `package.json` (Node-managed bats installs).
4. Shell scripts (`.sh` or `.bash` files) in a `tests/` or `test/` directory.
5. A `Makefile` with a `test` target that invokes `bats`.
6. Bash or shell scripts (`.sh`, `.bash`) dominating the source tree.

If two or more signals match, treat the project as a bats project and proceed.

## GENERATE

Generate bats test code from G/W/T triples using these conventions:

### Naming

```bash
@test "description of what is being tested" {
```

Descriptions should be plain English, describing the When and Then in natural language.

### Basic structure

```bash
#!/usr/bin/env bats

setup() {
  # Given: establish preconditions before each test
  export FIXTURE_DIR="$(mktemp -d)"
  cp -r fixtures/ "$FIXTURE_DIR/"
}

teardown() {
  # Cleanup after each test
  rm -rf "$FIXTURE_DIR"
}

@test "running the command with valid input produces expected output" {
  # When
  run my_command --flag "$FIXTURE_DIR/input.txt"

  # Then
  assert_success
  assert_output "expected output"
}
```

- `setup()` runs before each `@test` block — use it for the Given.
- `teardown()` runs after each `@test` block — use it for cleanup.
- `run` captures the command's exit code in `$status` and stdout in `$output`.
- Each `@test` block is fully isolated.

### Parametrize limitation — N discrete @test blocks

**Bats has no native parametrize mechanism.** There is no equivalent to `@pytest.mark.parametrize`.

For N input/output pairs, generate N discrete `@test` blocks — one per case. This is verbose but correct. This verbosity
is accepted for v1 and is not worked around.

Example with three cases instead of one parametrized test:

```bash
@test "increment returns 2 when given 1" {
  run increment 1
  assert_success
  assert_output "2"
}

@test "increment returns 1 when given 0" {
  run increment 0
  assert_success
  assert_output "1"
}

@test "increment returns 0 when given -1" {
  run increment -1
  assert_success
  assert_output "0"
}
```

### Error / failure cases

```bash
@test "command fails when input file is missing" {
  run my_command --flag nonexistent.txt

  assert_failure
  assert_output --partial "No such file"
}
```

Use `assert_failure` to assert a non-zero exit code.

## RUN

Execute the test file with:

```
bats <test_file>
```

For a directory: `bats tests/`

bats emits TAP (Test Anything Protocol) output. Parse for:

- `ok N - description` — test passed.
- `not ok N - description` — test failed; the following lines show context.

Report the summary: `N tests, M failures`.

To run with helpers (bats-support, bats-assert):

```bash
load 'test_helper/bats-support/load'
load 'test_helper/bats-assert/load'
```

Add these load lines at the top of each `.bats` file when the helpers are present.

## EXPLAIN

Key bats patterns to explain when guiding the user:

### `run` captures command output

The `run` helper executes a command and captures:

- `$status` — the exit code (0 = success, non-zero = failure).
- `$output` — the combined stdout of the command.
- `$lines` — array of individual output lines.

```bash
run echo "hello world"
echo "$status" # 0
echo "$output" # hello world
echo "${lines[0]}" # hello world
```

### assert_success / assert_failure

From bats-assert:

```bash
assert_success # asserts $status == 0
assert_failure # asserts $status != 0
assert_failure 2 # asserts $status == 2
```

### assert_output

```bash
assert_output "exact string" # exact match
assert_output --partial "substring" # contains check
assert_output --regexp "pattern.*here" # regex match
```

### setup / teardown

```bash
setup() {
  # Runs before every @test block
  TEST_TMPDIR="$(mktemp -d)"
}

teardown() {
  # Runs after every @test block, even if the test fails
  rm -rf "$TEST_TMPDIR"
}
```

### @test block isolation

Each `@test` block runs in its own subshell. Environment changes inside one block do not leak into others. Use `setup()`
and global variables (exported) to share state from preconditions into test bodies.
