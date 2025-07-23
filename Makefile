# Makefile for CodeTV Project - Code Quality Commands
# Usage: make <target>

# Variables
PYTHON := python3
UV := uv
PROJECT_DIRS := agent_framework app tests

# Help target
.PHONY: help
help: ## Show this help message
	@echo "CodeTV Project - Code Quality Commands"
	@echo "====================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation targets
.PHONY: install-dev
install-dev: ## Install development dependencies
	$(UV) pip install -r dev-requirements.txt

.PHONY: install-hooks
install-hooks: ## Install pre-commit hooks
	$(PYTHON) -m pre_commit install

.PHONY: setup
setup: install-dev install-hooks ## Complete development setup

# Code quality targets
.PHONY: format
format: ## Format code with Black
	$(PYTHON) -m black $(PROJECT_DIRS)

.PHONY: format-check
format-check: ## Check code formatting without making changes
	$(PYTHON) -m black --check $(PROJECT_DIRS)

.PHONY: lint
lint: ## Run linting with Ruff (with auto-fixes)
	$(PYTHON) -m ruff check --fix $(PROJECT_DIRS)

.PHONY: lint-check
lint-check: ## Run linting without auto-fixes
	$(PYTHON) -m ruff check $(PROJECT_DIRS)

.PHONY: type-check
type-check: ## Run type checking with MyPy
	$(PYTHON) -m mypy $(PROJECT_DIRS)

.PHONY: security
security: ## Run security checks with Bandit
	$(PYTHON) -m bandit -r $(PROJECT_DIRS) -x tests

# Testing targets
.PHONY: test
test: ## Run all tests with coverage
	$(PYTHON) -m pytest

.PHONY: test-unit
test-unit: ## Run only unit tests
	$(PYTHON) -m pytest -m unit

.PHONY: test-integration
test-integration: ## Run only integration tests
	$(PYTHON) -m pytest -m integration

.PHONY: test-fast
test-fast: ## Run tests without slow tests
	$(PYTHON) -m pytest -m "not slow"

.PHONY: test-no-cov
test-no-cov: ## Run tests without coverage reporting
	$(PYTHON) -m pytest --no-cov

.PHONY: coverage-report
coverage-report: ## Generate HTML coverage report
	$(PYTHON) -m pytest --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

# Pre-commit targets
.PHONY: pre-commit
pre-commit: ## Run pre-commit hooks on all files
	$(PYTHON) -m pre_commit run --all-files

.PHONY: pre-commit-update
pre-commit-update: ## Update pre-commit hook versions
	$(PYTHON) -m pre_commit autoupdate

# Combined quality checks
.PHONY: check
check: format-check lint-check type-check test ## Run all quality checks (CI-style)

.PHONY: fix
fix: format lint ## Fix all auto-fixable issues

.PHONY: quality
quality: fix type-check test ## Fix issues and run quality checks

# Clean targets
.PHONY: clean
clean: ## Clean build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: clean-all
clean-all: clean ## Clean everything including virtual environment
	rm -rf .venv/

# Documentation targets
.PHONY: docs
docs: ## Open code quality documentation
	@echo "Opening CODE_QUALITY.md..."
	@if command -v open > /dev/null; then open CODE_QUALITY.md; elif command -v xdg-open > /dev/null; then xdg-open CODE_QUALITY.md; else echo "Please open CODE_QUALITY.md manually"; fi

# Verification targets
.PHONY: verify-setup
verify-setup: ## Verify development environment setup
	@echo "Verifying development environment..."
	@echo "Checking Python version:"
	@$(PYTHON) --version
	@echo "Checking installed packages:"
	@$(UV) pip list | grep -E "(black|ruff|mypy|pytest|pre-commit)" || echo "Some packages may be missing"
	@echo "Checking pre-commit installation:"
	@$(PYTHON) -m pre_commit --version || echo "Pre-commit not installed"
	@echo "Environment verification complete!"

# Default target
.DEFAULT_GOAL := help
