---
cypilot: true
type: project-rule
topic: conventions
generated-by: auto-config
version: 1.0
---

# Conventions


<!-- toc -->

- [File & Module Organization](#file-module-organization)
  - [CLI Command Modules](#cli-command-modules)
  - [File Naming](#file-naming)
- [Code Style](#code-style)
  - [Type Hints](#type-hints)
  - [Dataclasses for Domain Objects](#dataclasses-for-domain-objects)
  - [Traceability Markers](#traceability-markers)
- [Testing Conventions](#testing-conventions)

<!-- /toc -->

Naming, code style, imports, and file organization rules extracted from the Cypilot codebase.

## File & Module Organization

### CLI Command Modules

Add new commands in `commands/{name}.py` with a `cmd_{name}(argv: List[str]) -> int` entry function. Register in `cli.py` via a lazy-import thunk (`_cmd_{name}`) and add to the dispatch `if/elif` chain. Use `argparse` for flags inside `cmd_*`.

Evidence: `commands/validate.py:14`, `commands/init.py`, `cli.py:34-98`.

### File Naming

Use `snake_case.py` for all Python modules. Use `UPPERCASE.md` for major documentation files (`AGENTS.md`, `README.md`). CLI spec lives at `architecture/specs/CLISPEC.md`. Use kebab-case for non-Python config files (`artifacts.toml`, `core.toml`).

Evidence: `src/cypilot_proxy/`, `skills/cypilot/scripts/cypilot/utils/`.

## Code Style

### Type Hints

All function signatures use type hints. Use `Optional[X]` (not `X | None`) for Python 3.11 compatibility with the proxy. Use `from __future__ import annotations` only in test files.

Evidence: `resolve.py:13`, `cache.py:17`, `tests/conftest.py:1`.

### Dataclasses for Domain Objects

Use `@dataclass` for value objects and domain types. Key examples: `CypilotContext`, `LoadedKit`, `ArtifactsMeta`, `SystemNode`, `CodeFile`, `ScopeMarker`.

Evidence: `utils/context.py:21-38`, `utils/artifacts_meta.py`, `utils/codebase.py`.

### Traceability Markers

Production code uses `@cpt-{kind}:{id}:p{N}` scope markers and `@cpt-begin`/`@cpt-end` block markers. Place scope markers on the line above or inside the docstring of the function they trace. Block markers wrap the implementation steps of a traced flow.

Evidence: `src/cypilot_proxy/cli.py:7-11` (scope), `src/cypilot_proxy/cli.py:54-56` (begin/end).

## Testing Conventions

- Test files mirror source structure in `tests/`
- Test classes named `Test{ClassName}` or `Test{SpecName}`
- Test methods named `test_{behavior_being_tested}`
- Use `TemporaryDirectory` for file system tests

Evidence: `tests/test_validate.py`, `tests/test_cli_integration.py`.
