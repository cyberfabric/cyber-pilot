---
cypilot: true
type: project-rule
topic: tech-stack
generated-by: auto-config
version: 1.0
---

# Tech Stack


<!-- toc -->

- [Languages](#languages)
- [Frameworks & Libraries](#frameworks-libraries)
- [Testing](#testing)
- [Build & Development](#build-development)
- [Code Quality](#code-quality)

<!-- /toc -->

## Languages

- **Python 3.11+** — Primary language (uses `tomllib` from stdlib)

## Frameworks & Libraries

Zero third-party runtime dependencies — stdlib only:

- **argparse** — CLI argument parsing
- **dataclasses** — Data structures
- **pathlib** — File system operations
- **json** — Data serialization
- **re** — Regex-based parsing
- **tomllib** — TOML config parsing (stdlib, Python 3.11+)
- **hashlib** — Blueprint hash computation
- **difflib** — Three-way merge for kit migration

## Testing

- **pytest** — Test framework (via pipx)
- **pytest-cov** — Coverage reporting (via pipx)
- **unittest.mock** — Mocking for unit tests

## Build & Development

- **Makefile** — Build automation
- **pipx** — Isolated tool execution (no venv required)
- **Docker** — Container runtime for local CI
- **[act](https://github.com/nektos/act)** — Run GitHub Actions locally in Docker
- **[actionlint](https://github.com/rhysd/actionlint)** — Lint GitHub Actions workflow files

## Code Quality

- **Coverage threshold**: 90% per file
- **Type hints**: Used throughout codebase
- **[vulture](https://github.com/jendrikseipp/vulture)** — Dead code detection (via pipx)
