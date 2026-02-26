# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

`mbtest` is an opinionated Python wrapper and utility library for [Mountebank](https://github.com/bbyars/mountebank), an over-the-wire test double tool. It provides:
- A Pythonic API to define Mountebank imposters, stubs, predicates, and responses
- A pytest fixture (`mock_server`) to start/stop Mountebank automatically during tests
- PyHamcrest matchers (`had_request`, `email_sent`) to assert on recorded requests

## Commands

### Running tests
```sh
# All tests (requires Docker running via colima)
make test            # uv run pytest tests/unit/ tests/integration/

# Run a specific test file or test
uv run pytest tests/unit/mbtest/test_matchers.py
uv run pytest tests/unit/mbtest/test_matchers.py::test_name

# Coverage report
make coverage        # uv run pytest --cov src/mbtest --cov-report=term-missing
```

### Linting & formatting
```sh
make lint            # check-format via ruff
make format          # auto-format with ruff
make extra-lint      # typecheck with pyright
uv run ruff format . --check && uv run ruff check .    # check format
uv run ruff format . && uv run ruff check . --fix      # fix format
uv run pyright src/                                    # type checking
```

### Pre-commit check
```sh
make precommit       # runs tests, typecheck, lint, and docs
```

### Docs
```sh
make docs            # uv run sphinx-build docs build_docs --color -W -bhtml
```

### Dependencies
```sh
# Install/sync all dependencies (including dev)
make sync            # uv sync --all-groups

# Install Mountebank (required for integration tests run locally)
npm install mountebank@2.9 --omit=dev

# Start Docker (required for integration tests)
colima status || colima start
```

## Architecture

### Source layout (`src/mbtest/`)

- **`server.py`** — Core server classes:
  - `MountebankServer`: Connects to an already-running Mountebank instance; used as a context manager to add/delete imposters.
  - `ExecutingMountebankServer`: Subclass that also spawns the `mb` process via `subprocess`.
  - `mock_server()`: Factory function intended for use in a pytest `conftest.py` fixture; registers a finalizer to stop the server after the test session.

- **`imposters/`** — Object model mirroring the Mountebank JSON API:
  - `base.py`: `JsonSerializable` ABC (all domain objects extend this); defines `as_structure()` / `from_structure()` round-trip interface and `add_if_true` / `set_if_in_dict` helpers.
  - `imposters.py`: `Imposter` (top-level mock server on a port), `HttpRequest`, `SentEmail`, `smtp_imposter()` factory.
  - `stubs.py`: `Stub` (predicate → response mapping), `AddStub` (for adding stubs to a running imposter).
  - `predicates.py`: `Predicate`, `AndPredicate`, `OrPredicate`, `NotPredicate`, `TcpPredicate`, `InjectionPredicate`. Predicates support `&`, `|`, and `~` operators for logical composition.
  - `responses.py`: `Response`, `HttpResponse`, `TcpResponse`, `FaultResponse`, `Proxy`, `InjectionResponse`, `PredicateGenerator`.
  - `behaviors/`: `Copy`, `Lookup`, and related xpath/jsonpath/regex helpers for response behaviors.
  - `__init__.py`: Re-exports the primary public API symbols.

- **`matchers.py`** — PyHamcrest matchers:
  - `had_request()` / `HadRequest`: Asserts that an `Imposter` or `MountebankServer` recorded a matching HTTP request. Uses a builder pattern (`with_path(...)`, `and_method(...)`, etc.).
  - `email_sent()` / `EmailSent`: Asserts that an SMTP imposter received a matching email.

- **`util.py`** — Utility helpers (e.g., `find_mountebank_executable()`).

### Test layout (`tests/`)

- `tests/unit/` — Pure unit tests (no Mountebank needed).
- `tests/integration/` — Integration tests that require a live Mountebank instance and (for some tests) a Docker-hosted httpbin service.
- `tests/integration/conftest.py` — Defines the `mock_server` and `httpbin` pytest fixtures.
- `tests/docker-compose.yml` — Used by `pytest-docker` to bring up httpbin for integration tests.

### Key design patterns

- Every domain object implements `as_structure() -> dict` (serialise to Mountebank JSON) and `from_structure(dict)` (deserialise). This makes the Python objects a thin, typed layer over the Mountebank REST API.
- `MountebankServer.__call__(imposters)` followed by `__enter__` / `__exit__` is the primary usage pattern for managing imposters within a `with` block.
- Ruff is used for both formatting and linting (see `pyproject.toml` for ignored rules). Line length is 120. The `ALL` rule set is selected with a curated ignore list.
- 100% test coverage is enforced via `fail_under = 100` in `[tool.coverage.report]` in `pyproject.toml`.
