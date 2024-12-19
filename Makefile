SHELL = /bin/bash

default: help

.PHONY: colima
colima:
	colima status || colima start

.PHONY: test
test: colima ## Run tests
	tox -e py39,py313,pypy3.10

.PHONY: coverage
coverage: colima ## Test coverage report
	tox -e coverage

.PHONY: precommit-test
precommit-test: colima
	tox -e py39,coverage

.PHONY: lint
lint: check-format flake8 bandit refurb  ## Lint code

.PHONY: flake8
flake8:
	tox -e flake8

.PHONY: bandit
bandit:
	tox -e bandit

.PHONY: extra-lint
extra-lint: pylint typecheck  ## Extra, optional linting.

.PHONY: pylint
pylint:
	tox -e pylint

.PHONY: refurb
refurb:
	tox -e refurb

.PHONY: typecheck
typecheck:
	tox -e pyright,mypy

.PHONY: check-format
check-format:
	tox -e check-format

.PHONY: format
format: ## Format code
	tox -e format

.PHONY: piprot
piprot: ## Check for outdated dependencies
	tox -e piprot

.PHONY: mutmut
mutmut: clean ## Run mutation tests
	tox -e mutmut run
	tox -e mutmut html
	open open html/index.html

.PHONY: docs
docs:  ## Generate documentation
	tox -e docs

.PHONY: precommit
precommit: precommit-test typecheck lint docs ## Pre-commit targets
	@ python -m this

.PHONY: recreate
recreate: clean jsdeps ## Recreate tox environments
	tox --recreate --notest -p -s
	tox --recreate --notest -e coverage,format,check-format,flake8,pylint,bandit,piprot,mypy,pyright,docs,refurb -p

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
	tox -e py313 -- python

.PHONY: outdated
outdated: ## List outdated dependancies
	tox -e py313 -- pip list -o

.PHONY: help
help: ## Show this help
	@ grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1,$$2}'
