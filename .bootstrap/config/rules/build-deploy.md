---
cypilot: true
type: project-rule
topic: build-deploy
generated-by: auto-config
version: 1.0
---

# Build & Deploy


<!-- toc -->

- [Build System](#build-system)
- [CI Pipeline](#ci-pipeline)
  - [Local CI via act](#local-ci-via-act)
  - [GitHub Actions](#github-actions)
- [Make Targets](#make-targets)
- [Dependencies](#dependencies)
- [Coverage Requirements](#coverage-requirements)

<!-- /toc -->

Build automation, CI/CD pipeline, and dependency management for the Cypilot project.

## Build System

**Build Tool**: Makefile  
**Package Manager**: pipx (isolated tool execution)  
**Local CI**: [act](https://github.com/nektos/act) (GitHub Actions in Docker)  
**Lint**: [actionlint](https://github.com/rhysd/actionlint) (workflow file linting)  

## CI Pipeline

### Local CI via act

`make ci` runs the exact same GitHub Actions workflow locally via act in Docker. Single source of truth — `.github/workflows/ci.yml`.

```bash
# Run full CI (auto-detects arm64/amd64)
make ci

# Override act flags if needed
make ci ACT_FLAGS="--container-architecture linux/amd64"
```

Jobs run sequentially and stop on first failure. On Apple Silicon, containers run natively as arm64. Matrix jobs limited to Python 3.13 by default to avoid Docker resource exhaustion.

Evidence: `Makefile:4-13` (arch detection), `Makefile:174-183` (ci target).

### GitHub Actions

CI runs on every push to `main` and every PR targeting `main`. Six parallel jobs:

1. **Test** — `make test` on Python 3.11, 3.12, 3.13, 3.14
2. **Coverage** — `make test-coverage` on Python 3.14 (≥90% gate)
3. **Vulture** — `make vulture-ci` dead code scan
4. **Versions** — `make check-versions` consistency check
5. **Spec Coverage** — `make spec-coverage` (≥80% overall, ≥70% per file)
6. **Validate** — `make validate` + `make self-check` on Python 3.11–3.14

Evidence: `.github/workflows/ci.yml`.

## Make Targets

| Command | Description | CI? |
|---------|-------------|-----|
| `make ci` | Run full CI locally via act | — |
| `make lint-ci` | Lint GitHub Actions workflow files | — |
| `make test` | Run all tests with pytest | Yes |
| `make test-verbose` | Run tests with verbose output | — |
| `make test-quick` | Fast tests only (skip `@pytest.mark.slow`) | — |
| `make test-coverage` | Tests + coverage report (≥90% required) | Yes |
| `make validate` | Validate core methodology via `cpt validate` | Yes |
| `make self-check` | Validate SDLC examples against templates | Yes |
| `make check-versions` | Check version consistency across components | Yes |
| `make spec-coverage` | Check spec coverage (≥80% overall, ≥70% per file) | Yes |
| `make vulture` | Scan for dead code (report only) | — |
| `make vulture-ci` | Scan for dead code (fails if findings) | Yes |
| `make install` | Install pytest + pytest-cov via pipx | — |
| `make install-proxy` | Reinstall `cpt` CLI from local source | — |
| `make update` | Sync `.bootstrap/` from local source | — |
| `make clean` | Remove Python cache files | — |

## Dependencies

Dependencies managed via pipx for isolation. No virtual environment required for CI.

```bash
# Install test tools
make install

# Install CLI proxy
make install-proxy
```

Required tools: Python 3.11+, pipx, make, Docker, act, actionlint.

## Coverage Requirements

- **Threshold**: 90% per file minimum
- **Report**: HTML report at `htmlcov/index.html`
- **Check**: `python scripts/check_coverage.py coverage.json --root skills/cypilot/scripts/cypilot --min 90`

Evidence: `Makefile:89-106` (test-coverage target), `scripts/check_coverage.py`.
