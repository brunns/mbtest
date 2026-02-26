SHELL = /bin/bash

default: help

.PHONY: colima
colima:
	colima status || colima start

.PHONY: test
test: colima ## Run tests
	uv run pytest tests/unit/ tests/integration/

.PHONY: coverage
coverage: colima ## Test coverage report
	uv run pytest --cov src/mbtest --cov-report=term-missing

.PHONY: precommit-test
precommit-test: colima
	uv run pytest tests/unit/ tests/integration/
	uv run pytest --cov src/mbtest --cov-report=term-missing

.PHONY: lint
lint: check-format  ## Lint code

.PHONY: extra-lint
extra-lint: typecheck  ## Extra, optional linting.

.PHONY: typecheck
typecheck:
	uv run pyright src/

.PHONY: check-format
check-format:
	uv run ruff format . --check
	uv run ruff check .

.PHONY: format
format: ## Format code
	uv run ruff format .
	uv run ruff check . --fix

.PHONY: mutmut
mutmut: clean ## Run mutation tests
	uv run mutmut run
	uv run mutmut html
	open html/index.html

.PHONY: docs
docs:  ## Generate documentation
	uv run sphinx-build docs build_docs --color -W -bhtml

.PHONY: precommit
precommit: precommit-test typecheck lint docs ## Pre-commit targets
	@ python -m this

.PHONY: sync
sync: ## Install/sync dependencies
	uv sync --all-groups

.PHONY: jsdeps
jsdeps:
	- rm -r node_modules/ package.json package-lock.json
	npm install mountebank@2.9 --omit=dev

.PHONY: clean
clean: ## Clean generated files
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	- rm -r build/ build_docs/ dist/ *.egg-info/ .cache .coverage .pytest_cache/ .mbdb/ .mypy_cache/ *.log *.pid *.svg .mutmut-cache html/
	find . -name "__pycache__" -type d -print | xargs -t rm -r
	find . -name "test-output" -type d -print | xargs -t rm -r

.PHONY: repl
repl: ## Python REPL
	uv run python

.PHONY: outdated
outdated: ## List outdated dependancies
	uv pip list --outdated

.PHONY: help
help: ## Show this help
	@ grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1,$$2}'
