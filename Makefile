SHELL = /bin/bash

default: help
.PHONY: help

test: tox ## Run tests

unit:
	#pytest --durations=10 --hypothesis-show-statistics test/unit/

integration:
	#pytest -m"not slow" --durations=10 --hypothesis-show-statistics test/integration/

alltests: ## Run all tests, including slow ones.
	#pytest --durations=10 test/

coverage: ## Test coverage report
	#pytest --cov uc/ --durations=10 --hypothesis-show-statistics --cov-report term-missing --cov-fail-under 95 test/unit/

lint: flake8 bandit safety ## Lint code

flake8:
	tox -e flake8

bandit:
	tox -e bandit

safety:
	tox -e safety

piprot: ## Check for outdated dependencies
	piprot requirements.txt
	piprot test_requirements.txt

precommit: lint coverage integration ## Pre-commit targets

clean: ## Clean generated files
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	rm -rf build/ dist/ *.egg-info/ .cache .coverage .pytest_cache
	find . -name "__pycache__" -type d -print | xargs -t rm -r
	find . -name "test-output" -type d -print | xargs -t rm -r

deps: jsdeps ## Install or update dependencies

pydeps:
	pip install -U -r requirements.txt -c constraints.txt
	pip install -U -r test_requirements.txt -c constraints.txt
	pip check
	@ echo "Outdated:"
	@ pip list --outdated

jsdeps:
	npm install mountebank@1.14.1 --production

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1,$$2}'
