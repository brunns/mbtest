SHELL = /bin/bash

default: help
.PHONY: help

test: ## Run tests
	tox

unit:
	#pytest --durations=10 --hypothesis-show-statistics test/unit/

integration:
	#pytest -m"not slow" --durations=10 --hypothesis-show-statistics test/integration/

alltests: ## Run all tests, including slow ones.
	#pytest --durations=10 test/

coverage: ## Test coverage report
	tox -e coverage

lint: flake8 bandit safety ## Lint code

flake8:
	tox -e flake8

bandit:
	tox -e bandit

safety:
	tox -e safety

format: ## Format code
	tox -e format

piprot: ## Check for outdated dependencies
	piprot requirements.txt
	piprot test_requirements.txt

precommit: format test lint coverage ## Pre-commit targets

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

publish: ## Publish to pypi
	python setup.py sdist upload -r pypi

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1,$$2}'
