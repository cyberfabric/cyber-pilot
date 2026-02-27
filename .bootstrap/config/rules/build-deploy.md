---
cypilot: true
type: project-rule
topic: build-deploy
generated-by: auto-config
version: 1.0
---

# Build & Deploy


<!-- toc -->

- [Build \& Deploy](#build--deploy)
  - [Build System](#build-system)
  - [Available Commands](#available-commands)
  - [Dependencies](#dependencies)
  - [Coverage Requirements](#coverage-requirements)
  - [CI/CD](#cicd)

<!-- /toc -->

## Build System

**Build Tool**: Makefile
**Package Manager**: pipx (for isolated tool execution)

## Available Commands

| Command | Description |
|---------|-------------|
| `make test` | Run all tests with pytest |
| `make test-verbose` | Run tests with verbose output |
| `make test-quick` | Run fast tests only (skip slow) |
| `make test-coverage` | Run tests with coverage report |
| `make validate` | Validate core methodology |
| `make validate-feature FEATURE=name` | Validate specific feature |
| `make validate-code` | Validate codebase traceability |
| `make validate-code-feature FEATURE=name` | Validate code traceability for specific feature |
| `make self-check` | Validate SDLC examples against templates |
| `make vulture` | Scan for dead code (report only) |
| `make vulture-ci` | Scan for dead code (fails if findings) |
| `make install` | Install Python dependencies via pipx |
| `make clean` | Remove Python cache files |

## Dependencies

Dependencies are managed via pipx for isolation:

```bash
# Install pytest + pytest-cov
make install

# Or manually:
pipx install pytest
pipx inject pytest pytest-cov
```

## Coverage Requirements

- **Threshold**: 90% per file minimum
- **Report**: HTML report generated at `htmlcov/index.html`
- **Check**: `python scripts/check_coverage.py coverage.json --root skills/cypilot/scripts/cypilot --min 90`

## CI/CD

No automated CI/CD pipeline configured. Tests run locally via Makefile.

**Recommended workflow**:
1. `make test` - Run all tests before committing
2. `make test-coverage` - Verify coverage threshold
3. `make self-check` - Validate examples
