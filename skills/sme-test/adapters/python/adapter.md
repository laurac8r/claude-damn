# Python / pytest Adapter

This adapter translates Given/When/Then test triples into pytest test code.

## DETECT

Identify a Python project by checking for these signals (strongest-first):

1. `pyproject.toml` with a `[tool.pytest.ini_options]` or `[tool.pytest]` section — highest confidence.
2. `pyproject.toml` or `setup.cfg` with `pytest` listed under `[options.extras_require]` or
   `[project.optional-dependencies]`.
3. `setup.py` present in the project root.
4. `requirements.txt` or `requirements-dev.txt` containing `pytest`.
5. `conftest.py` present in root or a `tests/` directory.
6. `.py` files inside a `tests/` or `test/` directory with names matching `test_*.py` or `*_test.py`.

If two or more signals match, treat the project as a Python/pytest project and proceed.

## GENERATE

Generate pytest test code from G/W/T triples using these conventions:

### Naming

```
def test_<when>_<then>():
```

Convert the When and Then descriptions to `snake_case`. Keep names descriptive but concise.

### Basic structure

```python
import pytest


@pytest.fixture
def <given_resource>():
    # Given: set up the precondition
    return <value>


def test_<when>_<then>(<given_resource>):
    # When
    result = <call_under_test>(<given_resource>)

    # Then
    assert result == <expected>
```

- Use `@pytest.fixture` for every Given that establishes state or resources.
- Place shared fixtures in `conftest.py` when multiple test triples share the same Given.
- One test function per When/Then pair.

### Multiple input cases — use parametrize

When a single scenario has N input/output pairs:

```python
@pytest.mark.parametrize(
    "input_value, expected",
    [
        (1, 2),
        (0, 1),
        (-1, 0),
    ],
)
def test_<when>_<then>(input_value: int, expected: int) -> None:
    result = increment(input_value)
    assert result == expected
```

Always prefer `@pytest.mark.parametrize` over copy-pasting test functions.

### Error / exception cases

```python
def test_<when>_raises_<error>() -> None:
    with pytest.raises(ValueError, match="expected pattern"):
        <call_under_test>(bad_input)
```

Use `match=` to assert on the error message content.

## RUN

Execute the test file with:

```
uv run pytest <test_file> -v
```

Parse the output for:

- `PASSED` — test succeeded.
- `FAILED` — test ran but assertion failed; show the diff.
- `ERROR` — test setup/teardown raised an exception; show the traceback.

For the full suite: `uv run pytest -v`

Report the summary line: `N passed, M failed, K errors in Xs`.

## EXPLAIN

Key pytest patterns to explain when guiding the user:

### Bare assert statements

pytest rewrites `assert` expressions to produce rich diff output on failure. No need for `assertEqual` or `assertThat`
helpers — just write:

```python
assert result == expected
assert "substring" in response.text
assert my_list == [1, 2, 3]
```

### @pytest.fixture

Fixtures provide reusable, isolated setup. Declare them with `@pytest.fixture` and accept them as function parameters:

```python
@pytest.fixture
def db_session():
    session = create_session()
    yield session
    session.rollback()
```

Fixtures can be scoped: `function` (default), `class`, `module`, or `session`.

### @pytest.mark.parametrize

Run one test function with multiple input sets. Each tuple in the list becomes a separate test case:

```python
@pytest.mark.parametrize("x, expected", [(1, True), (0, False)])
def test_is_truthy(x: int, expected: bool) -> None:
    assert bool(x) == expected
```

### pytest.raises with match=

Assert that a specific exception is raised and that its message matches a pattern:

```python
with pytest.raises(KeyError, match="missing_key"):
    my_dict["missing_key"]
```

The `match=` argument is a regex applied to `str(exc_value)`.
