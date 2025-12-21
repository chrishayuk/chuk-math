.PHONY: help install dev-install test test-cov test-watch check lint format format-check typecheck security clean clean-build clean-all build publish publish-manual publish-test example-basic example-demo generate-samples serve-coverage dev quick-check ci version

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
RUFF := ruff
MYPY := mypy

# Directories
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
	@echo "  make test-watch       - Run tests in watch mode"
	@echo "  make serve-coverage   - Serve HTML coverage report on localhost:8000"
	@echo ""
	@echo "Code Quality:"
	@echo "  make check            - Run all checks (lint + type check + test)"
	@echo "  make lint             - Run linter (ruff)"
	@echo "  make format           - Format code with ruff"
	@echo "  make format-check     - Check code formatting"
	@echo "  make typecheck        - Run type checker (mypy)"
	@echo "  make security         - Run security checks (bandit)"
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
	@echo "  make publish          - Build and publish to PyPI (via GitHub trusted publishing)"
	@echo "  make publish-manual   - Build and publish to PyPI (manual with twine)"
	@echo "  make publish-test     - Build and publish to TestPyPI"
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
		$(PIP) install -e .; \
	fi

dev-install:
	@echo "Installing development dependencies..."
	@if command -v uv >/dev/null 2>&1; then \
		uv pip install -e ".[dev]"; \
	else \
		$(PIP) install -e ".[dev]"; \
	fi

# Testing
test:
	@echo "Running tests..."
	@if command -v uv >/dev/null 2>&1; then \
		PYTHONPATH=$(SRC_DIR) uv run pytest $(TEST_DIR) -v; \
	else \
		PYTHONPATH=$(SRC_DIR) $(PYTEST) $(TEST_DIR) -v; \
	fi

test-cov coverage:
	@echo "Running tests with coverage..."
	@if command -v uv >/dev/null 2>&1; then \
		PYTHONPATH=$(SRC_DIR) uv run pytest $(TEST_DIR) --cov=$(SRC_DIR)/chuk_math_gym --cov-report=term-missing --cov-report=html --cov-report=xml; \
	else \
		PYTHONPATH=$(SRC_DIR) $(PYTEST) $(TEST_DIR) --cov=$(SRC_DIR)/chuk_math_gym --cov-report=term-missing --cov-report=html --cov-report=xml; \
	fi
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"

test-watch:
	@echo "Running tests in watch mode..."
	@if command -v uv >/dev/null 2>&1; then \
		PYTHONPATH=$(SRC_DIR) uv run pytest-watch $(TEST_DIR); \
	else \
		PYTHONPATH=$(SRC_DIR) $(PYTHON) -m pytest_watch $(TEST_DIR); \
	fi

# Code Quality
check: lint typecheck test
	@echo ""
	@echo "✓ All checks passed!"

lint:
	@echo "Running linter..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run ruff check $(SRC_DIR) $(TEST_DIR); \
		uv run ruff format --check $(SRC_DIR) $(TEST_DIR); \
	elif command -v $(RUFF) >/dev/null 2>&1; then \
		$(RUFF) check $(SRC_DIR) $(TEST_DIR); \
		$(RUFF) format --check $(SRC_DIR) $(TEST_DIR); \
	else \
		echo "Ruff not found. Install with: pip install ruff"; \
		exit 1; \
	fi

format:
	@echo "Formatting code..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run ruff format $(SRC_DIR) $(TEST_DIR); \
		uv run ruff check --fix $(SRC_DIR) $(TEST_DIR); \
	elif command -v $(RUFF) >/dev/null 2>&1; then \
		$(RUFF) format $(SRC_DIR) $(TEST_DIR); \
		$(RUFF) check --fix $(SRC_DIR) $(TEST_DIR); \
	else \
		echo "Ruff not found. Install with: pip install ruff"; \
		exit 1; \
	fi

format-check:
	@echo "Checking code formatting..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run ruff format --check $(SRC_DIR) $(TEST_DIR); \
	elif command -v $(RUFF) >/dev/null 2>&1; then \
		$(RUFF) format --check $(SRC_DIR) $(TEST_DIR); \
	else \
		echo "Ruff not found. Install with: pip install ruff"; \
		exit 1; \
	fi

typecheck:
	@echo "Running type checker..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run mypy $(SRC_DIR) || echo "Type check found issues (non-blocking)"; \
	elif command -v $(MYPY) >/dev/null 2>&1; then \
		$(MYPY) $(SRC_DIR) || echo "Type check found issues (non-blocking)"; \
	else \
		echo "MyPy not found. Install with: pip install mypy"; \
		exit 1; \
	fi

# Alias for typecheck
type-check: typecheck

# Security
security:
	@echo "Running security checks..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run bandit -r $(SRC_DIR) -f txt || echo "Security issues found (non-blocking)"; \
	elif command -v bandit >/dev/null 2>&1; then \
		bandit -r $(SRC_DIR) -f txt || echo "Security issues found (non-blocking)"; \
	else \
		echo "Bandit not found. Install with: pip install bandit"; \
		exit 1; \
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
build: clean-build
	@echo "Building distribution packages..."
	@if command -v uv >/dev/null 2>&1; then \
		uv build; \
	else \
		$(PYTHON) -m build; \
	fi
	@echo ""
	@echo "Build complete. Distributions are in the 'dist' folder."
	@ls -lh dist/

publish:
	@echo "Starting automated release process..."
	@echo ""
	@version=$$(grep '^version = ' pyproject.toml | cut -d'"' -f2); \
	tag="v$$version"; \
	echo "Version: $$version"; \
	echo "Tag: $$tag"; \
	echo ""; \
	\
	echo "Pre-flight checks:"; \
	echo "=================="; \
	\
	if git diff --quiet && git diff --cached --quiet; then \
		echo "✓ Working directory is clean"; \
	else \
		echo "✗ Working directory has uncommitted changes"; \
		echo ""; \
		git status --short; \
		echo ""; \
		echo "Please commit or stash your changes before releasing."; \
		exit 1; \
	fi; \
	\
	if git tag -l | grep -q "^$$tag$$"; then \
		echo "✗ Tag $$tag already exists"; \
		echo ""; \
		echo "To delete and recreate:"; \
		echo "  git tag -d $$tag"; \
		echo "  git push origin :refs/tags/$$tag"; \
		exit 1; \
	else \
		echo "✓ Tag $$tag does not exist yet"; \
	fi; \
	\
	current_branch=$$(git rev-parse --abbrev-ref HEAD); \
	echo "✓ Current branch: $$current_branch"; \
	echo ""; \
	\
	echo "This will:"; \
	echo "  1. Create and push tag $$tag"; \
	echo "  2. Trigger GitHub Actions to:"; \
	echo "     - Create a GitHub release with changelog"; \
	echo "     - Run tests on all platforms"; \
	echo "     - Build and publish to PyPI"; \
	echo ""; \
	read -p "Continue? (y/N) " -n 1 -r; \
	echo ""; \
	if [[ ! $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "Aborted."; \
		exit 1; \
	fi; \
	\
	echo ""; \
	echo "Creating and pushing tag..."; \
	git tag -a "$$tag" -m "Release $$tag"; \
	git push origin "$$tag"; \
	echo ""; \
	echo "✓ Tag $$tag created and pushed"; \
	echo ""; \
	echo "GitHub Actions will now:"; \
	echo "  - Run tests"; \
	echo "  - Create GitHub release"; \
	echo "  - Publish to PyPI"; \
	echo ""; \
	echo "Monitor progress at:"; \
	echo "  https://github.com/chrishayuk/chuk-math/actions"

publish-manual: build
	@echo "Manual PyPI Publishing"
	@echo "======================"
	@echo ""
	@version=$$(grep '^version = ' pyproject.toml | cut -d'"' -f2); \
	tag="v$$version"; \
	echo "Version: $$version"; \
	echo "Tag: $$tag"; \
	echo ""; \
	\
	echo "Pre-flight checks:"; \
	echo "=================="; \
	\
	if git diff --quiet && git diff --cached --quiet; then \
		echo "✓ Working directory is clean"; \
	else \
		echo "✗ Working directory has uncommitted changes"; \
		echo ""; \
		git status --short; \
		echo ""; \
		echo "Please commit or stash your changes before publishing."; \
		exit 1; \
	fi; \
	\
	if git tag -l | grep -q "^$$tag$$"; then \
		echo "✓ Tag $$tag exists"; \
	else \
		echo "⚠ Tag $$tag does not exist yet"; \
		echo ""; \
		read -p "Create tag now? (y/N) " -n 1 -r; \
		echo ""; \
		if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
			git tag -a "$$tag" -m "Release $$tag"; \
			echo "✓ Tag created locally"; \
		else \
			echo "Continuing without creating tag..."; \
		fi; \
	fi; \
	\
	echo ""; \
	echo "This will upload version $$version to PyPI"; \
	echo ""; \
	read -p "Continue? (y/N) " -n 1 -r; \
	echo ""; \
	if [[ ! $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "Aborted."; \
		exit 1; \
	fi; \
	\
	echo ""; \
	echo "Uploading to PyPI..."; \
	if [ -n "$$PYPI_TOKEN" ]; then \
		if command -v uv >/dev/null 2>&1; then \
			uv run twine upload --username __token__ --password "$$PYPI_TOKEN" dist/*; \
		else \
			$(PYTHON) -m twine upload --username __token__ --password "$$PYPI_TOKEN" dist/*; \
		fi; \
	else \
		if command -v uv >/dev/null 2>&1; then \
			uv run twine upload dist/*; \
		else \
			$(PYTHON) -m twine upload dist/*; \
		fi; \
	fi

publish-test: build
	@echo "Publishing to TestPyPI..."
	@echo ""
	@if [ -n "$$PYPI_TOKEN" ]; then \
		if command -v uv >/dev/null 2>&1; then \
			uv run twine upload --repository testpypi --username __token__ --password "$$PYPI_TOKEN" dist/*; \
		else \
			$(PYTHON) -m twine upload --repository testpypi --username __token__ --password "$$PYPI_TOKEN" dist/*; \
		fi; \
	else \
		if command -v uv >/dev/null 2>&1; then \
			uv run twine upload --repository testpypi dist/*; \
		else \
			$(PYTHON) -m twine upload --repository testpypi dist/*; \
		fi; \
	fi

# Cleanup
clean:
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov coverage.xml 2>/dev/null || true

clean-build:
	@echo "Cleaning build artifacts..."
	@rm -rf build/ dist/ *.egg-info $(SRC_DIR)/*.egg-info 2>/dev/null || true
	@rm -rf .eggs/ 2>/dev/null || true
	@find . -name '*.egg' -exec rm -f {} + 2>/dev/null || true

clean-all: clean clean-build
	@echo "Cleaning all files..."
	rm -rf output/*.jsonl 2>/dev/null || true
	find . -name '.DS_Store' -delete 2>/dev/null || true

# Development helpers
serve-coverage:
	@echo "Serving coverage report on http://localhost:8000..."
	cd htmlcov && $(PYTHON) -m http.server 8000

dev: dev-install
	@echo "Development environment ready!"
	@echo "Run 'make test' to run tests"

quick-check: format lint
	@echo "Quick check complete!"

# CI/CD helpers
ci: dev-install check
	@echo "CI pipeline complete!"

# Version info
version:
	@echo "Python version:"
	@$(PYTHON) --version
	@echo ""
	@echo "Package version:"
	@grep '^version = ' pyproject.toml
