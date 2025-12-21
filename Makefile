.PHONY: help install dev-install test test-cov check lint format typecheck clean clean-all build publish example-basic example-demo generate-samples

# Variables
PYTHON := python3
SRC_DIR := src
TEST_DIR := tests
EXAMPLES_DIR := examples
SCRIPTS_DIR := scripts

# Default target
help:
	@echo "Chuk Math Gym - Available Commands"
	@echo "==================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          - Install production dependencies"
	@echo "  make dev-install      - Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run tests"
	@echo "  make test-cov         - Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make check            - Run all checks (lint + test)"
	@echo "  make lint             - Run linter (ruff)"
	@echo "  make format           - Format code with ruff"
	@echo "  make typecheck        - Run type checker (mypy)"
	@echo ""
	@echo "Examples:"
	@echo "  make example-basic    - Run basic usage example"
	@echo "  make example-demo     - Run full system demo"
	@echo ""
	@echo "Data Generation:"
	@echo "  make generate-samples - Generate verifier training samples"
	@echo ""
	@echo "Build & Publishing:"
	@echo "  make build            - Build distribution packages"
	@echo "  make publish          - Build and publish to PyPI"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            - Remove generated files"
	@echo "  make clean-all        - Remove all generated files and caches"

# Setup & Installation
install:
	@echo "Installing production dependencies..."
	@if command -v uv >/dev/null 2>&1; then \
		uv pip install -e .; \
	else \
		$(PYTHON) -m pip install -e .; \
	fi

dev-install:
	@echo "Installing development dependencies..."
	@if command -v uv >/dev/null 2>&1; then \
		uv pip install -e ".[dev]"; \
	else \
		$(PYTHON) -m pip install -e ".[dev]"; \
	fi

# Testing
test:
	@echo "Running tests..."
	@if command -v uv >/dev/null 2>&1; then \
		PYTHONPATH=$(SRC_DIR) uv run pytest $(TEST_DIR) -v; \
	else \
		PYTHONPATH=$(SRC_DIR) $(PYTHON) -m pytest $(TEST_DIR) -v; \
	fi

test-cov:
	@echo "Running tests with coverage..."
	@if command -v uv >/dev/null 2>&1; then \
		PYTHONPATH=$(SRC_DIR) uv run pytest $(TEST_DIR) --cov=$(SRC_DIR)/chuk_math_gym --cov-report=term-missing --cov-report=html; \
	else \
		PYTHONPATH=$(SRC_DIR) $(PYTHON) -m pytest $(TEST_DIR) --cov=$(SRC_DIR)/chuk_math_gym --cov-report=term-missing --cov-report=html; \
	fi
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"

# Code Quality
check: lint test
	@echo ""
	@echo "All checks passed!"

lint:
	@echo "Running linter..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run ruff check $(SRC_DIR) $(TEST_DIR); \
		uv run ruff format --check $(SRC_DIR) $(TEST_DIR); \
	else \
		ruff check $(SRC_DIR) $(TEST_DIR); \
		ruff format --check $(SRC_DIR) $(TEST_DIR); \
	fi

format:
	@echo "Formatting code..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run ruff format $(SRC_DIR) $(TEST_DIR); \
		uv run ruff check --fix $(SRC_DIR) $(TEST_DIR); \
	else \
		ruff format $(SRC_DIR) $(TEST_DIR); \
		ruff check --fix $(SRC_DIR) $(TEST_DIR); \
	fi

typecheck:
	@echo "Running type checker..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run mypy $(SRC_DIR) || echo "Type check found issues (non-blocking)"; \
	else \
		mypy $(SRC_DIR) || echo "Type check found issues (non-blocking)"; \
	fi

# Examples
example-basic:
	@echo "Running basic usage example..."
	@if command -v uv >/dev/null 2>&1; then \
		PYTHONPATH=$(SRC_DIR) uv run python $(EXAMPLES_DIR)/basic_usage.py; \
	else \
		PYTHONPATH=$(SRC_DIR) $(PYTHON) $(EXAMPLES_DIR)/basic_usage.py; \
	fi

example-demo:
	@echo "Running full system demo..."
	@if command -v uv >/dev/null 2>&1; then \
		PYTHONPATH=$(SRC_DIR) uv run python $(EXAMPLES_DIR)/demo_full_system.py; \
	else \
		PYTHONPATH=$(SRC_DIR) $(PYTHON) $(EXAMPLES_DIR)/demo_full_system.py; \
	fi

# Data Generation
generate-samples:
	@echo "Generating verifier training samples..."
	@if command -v uv >/dev/null 2>&1; then \
		PYTHONPATH=$(SRC_DIR) uv run python $(SCRIPTS_DIR)/generate_verifier_samples.py; \
	else \
		PYTHONPATH=$(SRC_DIR) $(PYTHON) $(SCRIPTS_DIR)/generate_verifier_samples.py; \
	fi

# Build & Publishing
build:
	@echo "Building distribution packages..."
	@rm -rf dist/ build/ *.egg-info $(SRC_DIR)/*.egg-info 2>/dev/null || true
	@if command -v uv >/dev/null 2>&1; then \
		uv build; \
	else \
		$(PYTHON) -m build; \
	fi
	@echo ""
	@echo "Build complete. Distributions are in the 'dist' folder."
	@ls -lh dist/

publish: build
	@echo "Publishing to PyPI..."
	@version=$$(grep '^version = ' pyproject.toml | cut -d'"' -f2); \
	tag="v$$version"; \
	echo "Version: $$version"; \
	echo "Tag: $$tag"; \
	echo ""; \
	if git diff --quiet && git diff --cached --quiet; then \
		echo "Working directory is clean"; \
	else \
		echo "Working directory has uncommitted changes"; \
		git status --short; \
		echo ""; \
		echo "Please commit or stash your changes before releasing."; \
		exit 1; \
	fi; \
	echo ""; \
	echo "This will create and push tag $$tag"; \
	read -p "Continue? (y/N) " -n 1 -r; \
	echo ""; \
	if [[ ! $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "Aborted."; \
		exit 1; \
	fi; \
	git tag -a "$$tag" -m "Release $$tag"; \
	git push origin "$$tag"; \
	echo ""; \
	echo "Tag $$tag created and pushed. GitHub Actions will publish to PyPI."

# Cleanup
clean:
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov 2>/dev/null || true

clean-all: clean
	@echo "Cleaning all files..."
	rm -rf build/ dist/ *.egg-info $(SRC_DIR)/*.egg-info 2>/dev/null || true
	rm -rf output/*.jsonl 2>/dev/null || true
	find . -name '.DS_Store' -delete 2>/dev/null || true

# Development helpers
dev: dev-install
	@echo "Development environment ready!"
	@echo "Run 'make test' to run tests"

quick-check: format lint
	@echo "Quick check complete!"

# CI helper
ci: dev-install check
	@echo "CI pipeline complete!"

# Version info
version:
	@echo "Python version:"
	@$(PYTHON) --version
	@echo ""
	@echo "Package version:"
	@grep '^version = ' pyproject.toml
