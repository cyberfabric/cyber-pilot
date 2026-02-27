# @cpt-algo:cpt-cypilot-spec-init-structure-change-infrastructure:p1
.PHONY: test test-verbose test-quick test-coverage validate validate-examples validate-feature validate-code validate-code-feature self-check vulture vulture-ci install install-pipx clean help check-pytest check-pytest-cov check-pipx check-vulture

PYTHON ?= python3
PIPX ?= pipx
CPT ?= cpt
PYTEST_PIPX ?= $(PIPX) run --spec pytest pytest
PYTEST_PIPX_COV ?= $(PIPX) run --spec pytest-cov pytest
VULTURE_PIPX ?= $(PIPX) run --spec vulture vulture
VULTURE_MIN_CONF ?= 0

# Default target
help:
	@echo "Cypilot Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make test                          - Run all tests"
	@echo "  make test-verbose                  - Run tests with verbose output"
	@echo "  make test-quick                    - Run fast tests only (skip slow integration tests)"
	@echo "  make test-coverage                 - Run tests with coverage report"
	@echo "  make validate-examples             - Validate requirements examples under examples/requirements"
	@echo "  make validate                      - Validate core methodology spec"
	@echo "  make self-check                    - Validate SDLC examples against their templates"
	@echo "  make vulture                       - Scan python code for dead code (report only, does not fail)"
	@echo "  make vulture-ci                    - Scan python code for dead code (fails if findings)"
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

check-vulture: check-pipx
	@$(VULTURE_PIPX) --version >/dev/null 2>&1 || { \
		echo ""; \
		echo "ERROR: vulture is not runnable via pipx"; \
		echo ""; \
		echo "Install it with:"; \
		echo "  pipx install vulture"; \
		echo "or just run: make vulture (pipx run will download it)"; \
		echo ""; \
		exit 1; \
	}

test: check-pytest
	@echo "Running Cypilot tests with pipx..."
	$(PYTEST_PIPX) tests/ -v --tb=short

# Run tests with verbose output
test-verbose: check-pytest
	@echo "Running Cypilot tests (verbose) with pipx..."
	$(PYTEST_PIPX) tests/ -vv

# Run quick tests only
test-quick: check-pytest
	@echo "Running quick tests with pipx..."
	$(PYTEST_PIPX) tests/ -v -m "not slow"

# Run tests with coverage
test-coverage: check-pytest-cov
	@echo "Running tests with coverage..."
	$(PYTEST_PIPX_COV) tests/ \
		--cov=skills/cypilot/scripts/cypilot \
		--cov-report=term-missing \
		--cov-report=json:coverage.json \
		--cov-report=html \
		-v --tb=short
	@$(PYTHON) scripts/check_coverage.py coverage.json --root skills/cypilot/scripts/cypilot --min 90
	@echo ""
	@echo "Coverage report generated:"
	@echo "  HTML: htmlcov/index.html"
	@echo "  Open with: open htmlcov/index.html"

vulture: check-vulture
	@echo "Running vulture dead-code scan (excluding tests by scanning only skills/cypilot/scripts/cypilot)..."
	@echo "Tip: raise/lower VULTURE_MIN_CONF to reduce false positives (current: $(VULTURE_MIN_CONF))."
	@$(VULTURE_PIPX) skills/cypilot/scripts/cypilot --min-confidence $(VULTURE_MIN_CONF) || true

vulture-ci: check-vulture
	@echo "Running vulture dead-code scan (CI mode, fails if findings)..."
	$(VULTURE_PIPX) skills/cypilot/scripts/cypilot --min-confidence $(VULTURE_MIN_CONF)

# Validate core methodology spec
validate:
	$(CPT) validate

validate-code:
	$(CPT) validate-code

# Validate specific feature
validate-feature:
	@if [ -z "$(FEATURE)" ]; then \
		echo "Error: FEATURE parameter required"; \
		echo "Usage: make validate-feature FEATURE=feature-name"; \
		exit 1; \
	fi
	@echo "Validating feature: $(FEATURE)..."
	@$(CPT) validate \
		--artifact architecture/features/$(FEATURE)/DESIGN.md

# Validate code traceability for specific feature
validate-code-feature:
	@if [ -z "$(FEATURE)" ]; then \
		echo "Error: FEATURE parameter required"; \
		echo "Usage: make validate-code-feature FEATURE=feature-name"; \
		exit 1; \
	fi
	@echo "Validating code traceability for feature: $(FEATURE)..."
	@$(CPT) validate --artifact architecture/features/$(FEATURE)

# Validate SDLC examples against templates
self-check:
	@echo "Running self-check: validating SDLC examples against templates..."
	$(CPT) self-check

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
