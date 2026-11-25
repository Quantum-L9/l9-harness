# Repository-owned implementation of the make-v2 execution phases.
#
# CI parity:
#   setup     -> "Sync the locked environment" in ci.yml and deep-plan.yml
#   validate  -> scripts/validate_repository.py, the 27-check repository gate
#   check     -> ruff check and ruff format --check
#   test-fast -> the bounded selection ci.yml runs on a pull request
#   test      -> the whole pytest suite deep-plan.yml runs on an apply
#
# Core runs each phase as its own make process, so every recipe resolves the
# environment it needs rather than relying on state a previous phase exported.
#
# The development dependencies are PEP 735 [dependency-groups], which pip
# cannot install, so the same pins the lock records are installed explicitly
# here. Bytecode is suppressed everywhere: validate_repository.py fails on
# cache residue inside the tree it is validating.
PYTHON ?= python3
VENV := $(CURDIR)/.venv
BIN := $(VENV)/bin
export PATH := $(BIN):$(PATH)
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: repo-setup repo-validate repo-check repo-test-fast repo-test

repo-setup: ## Create .venv and install the project with its development pins
	@test -x "$(BIN)/python" || $(PYTHON) -m venv "$(VENV)"
	@"$(BIN)/pip" install --quiet --upgrade pip
	@"$(BIN)/pip" install --quiet -e .
	@"$(BIN)/pip" install --quiet "ruff==0.16.6" "mypy==1.17.1" "pytest==9.1.1" "jsonschema==4.26.0"

repo-validate: ## Run the repository validation gate
	@"$(BIN)/python" -B scripts/validate_repository.py

repo-check: ## Ruff lint and format check
	@ruff check .
	@ruff format --check .

repo-test-fast: ## Bounded pull-request test selection
	@pytest -q -p no:cacheprovider tests/contract tests/architecture

repo-test: ## Whole pytest suite
	@pytest -q -p no:cacheprovider
