# @fdd-algo:fdd-fdd-feature-init-structure-change-infrastructure:ph-1
.PHONY: test test-verbose test-quick test-coverage validate validate-examples validate-feature validate-code validate-code-feature install install-pipx clean help check-pytest check-pytest-cov check-pipx

PYTHON ?= python3
PIPX ?= pipx
PYTEST_PIPX ?= $(PIPX) run --spec pytest pytest
PYTEST_PIPX_COV ?= $(PIPX) run --spec pytest-cov pytest

# Default target
help:
	@echo "FDD Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make test                          - Run all tests"
	@echo "  make test-verbose                  - Run tests with verbose output"
	@echo "  make test-quick                    - Run fast tests only (skip slow integration tests)"
	@echo "  make test-coverage                 - Run tests with coverage report"
	@echo "  make validate-examples             - Validate requirements examples under examples/requirements"
	@echo "  make validate                      - Validate core methodology feature"
	@echo "  make validate-feature FEATURE=name - Validate specific feature"
	@echo "  make validate-code                 - Validate codebase traceability (entire project)"
	@echo "  make validate-code-feature FEATURE=name - Validate code traceability for specific feature"
	@echo "  make install                       - Install Python dependencies"
	@echo "  make clean                         - Remove Python cache files"
	@echo "  make help                          - Show this help message"

# Run all tests
check-pipx:
	@command -v $(PIPX) >/dev/null 2>&1 || { \
		echo ""; \
		echo "ERROR: pipx not found"; \
		echo ""; \
		echo "Install it with:"; \
		echo "  brew install pipx"; \
		echo "  pipx ensurepath"; \
		echo ""; \
		exit 1; \
	}

check-pytest: check-pipx
	@$(PYTEST_PIPX) --version >/dev/null 2>&1 || { \
		echo ""; \
		echo "ERROR: pytest is not runnable via pipx"; \
		echo ""; \
		echo "Install it with:"; \
		echo "  make install"; \
		echo ""; \
		exit 1; \
	}

check-pytest-cov: check-pytest
	@$(PYTEST_PIPX_COV) --help 2>/dev/null | grep -q -- '--cov' || { \
		echo ""; \
		echo "ERROR: pytest-cov not available (missing --cov option)"; \
		echo ""; \
		echo "Install it with:"; \
		echo "  make install"; \
		echo ""; \
		exit 1; \
	}

test: check-pytest
	@echo "Running FDD tests with pipx..."
	$(PYTEST_PIPX) tests/ -v --tb=short

# Run tests with verbose output
test-verbose: check-pytest
	@echo "Running FDD tests (verbose) with pipx..."
	$(PYTEST_PIPX) tests/ -vv

# Run quick tests only
test-quick: check-pytest
	@echo "Running quick tests with pipx..."
	$(PYTEST_PIPX) tests/ -v -m "not slow"

# Run tests with coverage

test-coverage: check-pytest-cov
	@echo "Running tests with coverage..."
	$(PYTEST_PIPX_COV) tests/ \
		--cov=skills/fdd/scripts/fdd \
		--cov-report=term-missing \
		--cov-report=json:coverage.json \
		--cov-report=html \
		-v --tb=short
	@$(PYTHON) scripts/check_coverage.py coverage.json --root skills/fdd/scripts/fdd --min 90
	@echo ""
	@echo "Coverage report generated:"
	@echo "  HTML: htmlcov/index.html"
	@echo "  Open with: open htmlcov/index.html"

validate-examples: check-pytest
	@echo "Validating requirements examples..."
	$(PYTEST_PIPX) tests/test_validate.py -k TestRequirementExamples -v --tb=short

# Validate core methodology feature
validate:
	$(PYTHON) skills/fdd/scripts/fdd.py validate

# Validate specific feature
validate-feature:
	@if [ -z "$(FEATURE)" ]; then \
		echo "Error: FEATURE parameter required"; \
		echo "Usage: make validate-feature FEATURE=feature-name"; \
		exit 1; \
	fi
	@echo "Validating feature: $(FEATURE)..."
	@python3.11 skills/fdd/scripts/fdd.py validate \
		--artifact architecture/features/$(FEATURE)/DESIGN.md


# Validate code traceability for specific feature
validate-code-feature:
	@if [ -z "$(FEATURE)" ]; then \
		echo "Error: FEATURE parameter required"; \
		echo "Usage: make validate-code-feature FEATURE=feature-name"; \
		exit 1; \
	fi
	@echo "Validating code traceability for feature: $(FEATURE)..."
	@python3.11 skills/fdd/scripts/fdd.py validate --artifact architecture/features/$(FEATURE)

# Install Python dependencies
install-pipx: check-pipx
	@echo "Installing pytest + pytest-cov via pipx..."
	@$(PIPX) install pytest >/dev/null 2>&1 || $(PIPX) upgrade pytest
	@$(PIPX) inject pytest pytest-cov
	@echo "Done. If pytest is not found, run: pipx ensurepath (then restart your shell)."

install: install-pipx

# Clean Python cache
clean:
	@echo "Cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete"
