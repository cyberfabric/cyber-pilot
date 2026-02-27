---
cypilot: true
type: project-rule
topic: architecture
generated-by: auto-config
version: 1.0
---

# Architecture


<!-- toc -->

- [Source Layout](#source-layout)
- [Two-Package Design](#two-package-design)
- [Context Singleton](#context-singleton)
- [Path Resolution](#path-resolution)
- [Registry as Source of Truth](#registry-as-source-of-truth)
- [Architecture Patterns](#architecture-patterns)
  - [Template-Centric Architecture](#template-centric-architecture)
  - [Adaptive Workflow Model](#adaptive-workflow-model)
  - [Kit Package Pattern](#kit-package-pattern)
- [Critical Files](#critical-files)

<!-- /toc -->

System design, module boundaries, and key abstractions of the Cypilot project.

## Source Layout

```
src/cypilot_proxy/          # Proxy package (5 files, ~730 LOC)
  cli.py                    # Entry point: main() → resolve → forward
  resolve.py                # Skill target resolution (project → cache)
  cache.py                  # GitHub release download + extraction

skills/cypilot/scripts/cypilot/   # Skill engine (~34 files)
  cli.py                    # Command dispatch (lazy imports per command)
  constants.py              # Shared regex patterns and constants
  commands/                 # One module per CLI subcommand
  utils/                    # Shared utility modules

tests/                      # 26 test modules, pytest + conftest
```

## Two-Package Design

The proxy (`src/cypilot_proxy/`) is installed globally via pipx. It resolves the skill engine location (project-installed or cached) and forwards via `subprocess.run`. The skill engine (`skills/cypilot/scripts/cypilot/`) contains all business logic. They share no code at import time — communication is via process invocation.

## Context Singleton

`CypilotContext.load()` runs once at CLI startup (`cli.py:124`), parses `artifacts.toml`, loads constraints, and stores the result in a module-level `_context` variable accessed via `get_context()` / `set_context()`. Commands retrieve context with `get_context()`.

## Path Resolution

Two path-resolution systems exist:
- **Proxy**: `resolve.py` — walks up from cwd to find `AGENTS.md` with `@cpt:root-agents` marker, reads `cypilot_path` variable from TOML fence block
- **Skill**: `files.py` — same root-finding logic plus `core_subpath()` / `gen_subpath()` helpers for `.core/` vs `.gen/` layout

## Registry as Source of Truth

`artifacts.toml` declares systems, artifacts, codebases, and kit references. The `ArtifactsMeta` dataclass parses it and provides lookups. The `autodetect` sections in the registry drive artifact discovery during `cpt init`.

## Architecture Patterns

### Template-Centric Architecture
Templates are the foundation — each artifact type is a self-contained package (`kits/sdlc/artifacts/{KIND}/`) with `template.md`, `rules.md`, `checklist.md`, and `examples/`.

### Adaptive Workflow Model
"Start anywhere" adoption — users begin from any point (design, implementation, or validation). The `artifacts.toml` registry drives artifact discovery, with per-artifact traceability configuration (FULL vs DOCS-ONLY).

### Kit Package Pattern
Validation rules and templates are packaged as "kits" (`kits/{kit-id}/`) reusable across projects. Single source of truth for artifact validation.

## Critical Files

| File | Why it matters |
|------|---------------|
| `skills/cypilot/scripts/cypilot/cli.py` | Command dispatch hub — touch when adding/renaming commands |
| `skills/cypilot/scripts/cypilot/utils/context.py` | CypilotContext — loaded on every invocation |
| `skills/cypilot/scripts/cypilot/utils/files.py` | Project root + cypilot dir discovery |
| `skills/cypilot/scripts/cypilot/utils/artifacts_meta.py` | Registry parser — touch when changing artifacts.toml schema |
| `skills/cypilot/scripts/cypilot/commands/init.py` | Init flow — copies cache → .core/, creates config/ |
| `src/cypilot_proxy/resolve.py` | Skill resolution — touch when changing install layout |
| `src/cypilot_proxy/cache.py` | GitHub download — touch when changing release format |
| `cypilot/config/artifacts.toml` | Source of truth for systems, artifacts, codebases |
| `tests/conftest.py` | sys.path setup — must include all source roots |
