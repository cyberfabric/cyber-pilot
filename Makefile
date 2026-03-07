# @cpt-algo:cpt-cypilot-spec-init-structure-change-infrastructure:p1
.PHONY: test test-verbose test-quick test-coverage validate validate-examples validate-feature validate-code validate-code-feature self-check validate-kits validate-kits-sdlc vulture vulture-ci install install-pipx install-proxy clean help check-pytest check-pytest-cov check-pipx check-vulture check-versions update spec-coverage ci lint-ci

# Detect container architecture for act (arm64 on Apple Silicon, amd64 otherwise)
UNAME_M := $(shell uname -m)
ifeq ($(UNAME_M),arm64)
  ACT_ARCH := linux/arm64
else ifeq ($(UNAME_M),aarch64)
  ACT_ARCH := linux/arm64
else
  ACT_ARCH := linux/amd64
endif
ACT_FLAGS ?= --container-architecture $(ACT_ARCH)

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
	@echo "  make validate-kits                 - Validate all registered kits"
	@echo "  make validate-kits-sdlc            - Validate kits/sdlc kit by path"
	@echo "  make check-versions                - Check version consistency across components"
	@echo "  make spec-coverage                 - Check spec coverage (≥90% overall, ≥60% per file)"
	@echo "  make vulture                       - Scan python code for dead code (report only, does not fail)"
	@echo "  make vulture-ci                    - Scan python code for dead code (fails if findings)"
	@echo "  make ci                            - Run full CI pipeline locally"
	@echo "  make lint-ci                       - Lint GitHub Actions workflow files"
	@echo "  make install                       - Install Python dependencies"
	@echo "  make install-proxy                 - Reinstall cpt proxy from local source"
	@echo "  make update                        - Update .bootstrap from local source"
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
	@$(VULTURE_PIPX) skills/cypilot/scripts/cypilot vulture_whitelist.py --min-confidence $(VULTURE_MIN_CONF) || true

vulture-ci: check-vulture
	@echo "Running vulture dead-code scan (CI mode, fails if findings)..."
	$(VULTURE_PIPX) skills/cypilot/scripts/cypilot vulture_whitelist.py --min-confidence $(VULTURE_MIN_CONF)

# Spec coverage check (Cypilot system only)
spec-coverage:
	@echo "Checking spec coverage (Cypilot system)..."
	$(PYTHON) .bootstrap/.core/skills/cypilot/scripts/cypilot.py spec-coverage --system cypilot --min-coverage 90 --min-file-coverage 60 --min-granularity 0.45

# Check version consistency
check-versions:
	@$(PYTHON) scripts/check_versions.py

# Update .bootstrap from local source
update:
	$(CPT) update --source . --force

# Validate core methodology spec
validate:
	$(CPT) validate

# Validate SDLC examples against templates
self-check:
	@echo "Running self-check: validating SDLC examples against templates..."
	$(CPT) self-check

# Validate all registered kits
validate-kits:
	@echo "Validating all registered kits..."
	$(CPT) validate-kits

# Validate kits/sdlc kit by path
validate-kits-sdlc:
	@echo "Validating kits/sdlc..."
	$(CPT) validate-kits kits/sdlc

# Install Python dependencies
install-pipx: check-pipx
	@echo "Installing pytest + pytest-cov via pipx..."
	@$(PIPX) install pytest >/dev/null 2>&1 || $(PIPX) upgrade pytest
	@$(PIPX) inject pytest pytest-cov
	@echo "Done. If pytest is not found, run: pipx ensurepath (then restart your shell)."

install: install-pipx

# Reinstall cpt/cypilot proxy from local source
install-proxy: check-pipx
	$(PIPX) install --force .

# Lint CI workflow files
lint-ci:
	@echo "Linting GitHub Actions workflows..."
	actionlint

# Run CI via act in Docker (mirrors .github/workflows/ci.yml exactly)
# Runs jobs sequentially — stops on first failure.
# Auto-detects arm64/amd64. Override: make ci ACT_FLAGS="--your-flags"
ci: lint-ci
	@for job in $$(act push --list $(ACT_FLAGS) 2>/dev/null | tail -n +2 | awk '{print $$2}'); do \
		echo "▶ Running job: $$job"; \
		act push -j $$job $(ACT_FLAGS) || exit 1; \
	done
	@echo ""
	@echo "✓ All CI jobs passed."

# Clean Python cache
clean:
	@echo "Cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete"
