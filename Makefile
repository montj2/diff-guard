# DiffGuard Makefile

PYTHON := python3.11
VENV := .venv
PIP := $(VENV)/bin/pip
PY := $(VENV)/bin/python
PYTEST := $(VENV)/bin/pytest

# Minimum coverage threshold (can be overridden: make test-strict COVERAGE_MIN=90)
COVERAGE_MIN ?= 85

.DEFAULT_GOAL := help

## help: Show this help.
help:
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | awk 'BEGIN {FS":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}' | sort

$(VENV): ## Create virtual environment
	$(PYTHON) -m venv $(VENV)

.PHONY: venv
venv: $(VENV)

.PHONY: install
install: venv ## Install project with dev dependencies
	$(PIP) install -U pip
	$(PIP) install -e .[dev]

.PHONY: lint
lint: ## Run ruff (lint), black --check, mypy
	$(VENV)/bin/ruff check .
	$(VENV)/bin/black --check .
	$(VENV)/bin/mypy .

.PHONY: format
format: ## Auto-format using ruff (fix) + black
	$(VENV)/bin/ruff check --fix .
	$(VENV)/bin/black .

.PHONY: test
test: ## Run pytest (default args configured in pyproject for coverage)
	$(PYTEST)

.PHONY: test-strict
test-strict: ## Run tests enforcing minimum coverage (--cov-fail-under=$(COVERAGE_MIN))
	$(PYTEST) --cov-fail-under=$(COVERAGE_MIN)

.PHONY: run-api
run-api: ## Run FastAPI dev server
	$(VENV)/bin/uvicorn backend.app:app --reload --port 8000

.PHONY: run-worker
run-worker: ## Run worker (skeleton)
	$(PY) -m diff_worker.worker

.PHONY: dev
dev: install lint test ## Install deps then run lint & tests

.PHONY: clean
clean: ## Remove caches and build artifacts
	rm -rf .mypy_cache .ruff_cache $(VENV) build dist **/__pycache__ .pytest_cache

.PHONY: backtest
backtest: ## Placeholder for future backtest harness
	@echo "Backtest harness not implemented yet"
