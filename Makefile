SHELL = /bin/bash

default: help

.PHONY: test
test: ## Run tests
	tox -e py35,py38

.PHONY: coverage
coverage: ## Test coverage report
	tox -e coverage

.PHONY: lint
lint: check-format flake8 bandit ## Lint code

.PHONY: flake8
flake8:
	tox -e flake8

.PHONY: bandit
bandit:
	tox -e bandit

.PHONY: extra-lint
extra-lint: pylint mypy  ## Extra, optional linting.

.PHONY: pylint
pylint:
	tox -e pylint

.PHONY: mypy
mypy:
	tox -e mypy

.PHONY: check-format
check-format:
	tox -e check-format

.PHONY: format
format: ## Format code
	tox -e format

.PHONY: piprot
piprot: ## Check for outdated dependencies
	tox -e piprot

.PHONY: docs
docs:  ## Generate documentation
	tox -e docs

.PHONY: precommit
precommit: test lint coverage mypy docs ## Pre-commit targets
	@ python -m this

.PHONY: recreate
recreate: ## Recreate tox environments
	tox --recreate --notest -e py35,py36,py37,py38,coverage,format,flake8,bandit,piprot,pylint,mypy

.PHONY: clean
clean: ## Clean generated files
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	rm -rf build/ dist/ *.egg-info/ .cache .coverage .pytest_cache coverage.* coverage.*
	find . -name "*.egg-info" -type d -print | xargs -t rm -r
	find . -name "__pycache__" -type d -print | xargs -t rm -r
	find . -name "test-output" -type d -print | xargs -t rm -r

.PHONY: deps
deps: jsdeps ## Install or update dependencies

.PHONY: pydeps
pydeps:
	pip install -U -r requirements.txt -c constraints.txt
	pip install -U -r test_requirements.txt -c constraints.txt
	pip check
	@ echo "Outdated:"
	@ pip list --outdated

.PHONY: jsdeps
jsdeps:
	npm install mountebank@2.2.1 --production

.PHONY: repl
repl: ## Python REPL
	tox -e py38 -- python

.PHONY: outdated
outdated: ## List outdated dependancies
	tox -e py38 -- pip list --outdated

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1,$$2}'
