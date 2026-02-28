# Cypilot Adapter: Cypilot

**Version**: 3.0

---

## Project Overview

Cypilot is a workflow-centered methodology framework for AI-assisted software development with design-to-code traceability. This adapter configures Cypilot for the Cypilot framework itself (self-hosted).

---

## Navigation Rules

### Schema & Registry

ALWAYS open and follow `{cypilot_path}/.core/schemas/artifacts.schema.json` WHEN working with artifacts.toml

ALWAYS open and follow `{cypilot_path}/.core/requirements/artifacts-registry.md` WHEN working with artifacts.toml

### Project Rules

ALWAYS open and follow `{cypilot_path}/config/rules/tech-stack.md` WHEN writing code, choosing technologies, or adding dependencies

ALWAYS open and follow `{cypilot_path}/config/rules/conventions.md` WHEN writing code, naming files/functions/variables, or reviewing code

ALWAYS open and follow `{cypilot_path}/config/rules/project-structure.md` WHEN creating files, adding modules, or navigating codebase

ALWAYS open and follow `{cypilot_path}/config/rules/domain-model.md` WHEN working with entities, data structures, or business logic

ALWAYS open and follow `{cypilot_path}/config/rules/testing.md` WHEN writing tests, reviewing test coverage, or debugging

ALWAYS open and follow `{cypilot_path}/config/rules/build-deploy.md` WHEN building, deploying, or configuring CI/CD

ALWAYS open and follow `{cypilot_path}/config/rules/architecture.md` WHEN modifying architecture, adding components, or refactoring module boundaries

ALWAYS open and follow `{cypilot_path}/config/rules/patterns.md` WHEN implementing features or writing business logic

ALWAYS open and follow `{cypilot_path}/config/rules/anti-patterns.md` WHEN reviewing code or refactoring

---

## Development Rules

NEVER edit files inside `{cypilot_path}/.core/` or `{cypilot_path}/.gen/` directly — they are read-only copies. ALWAYS edit the canonical source files under project root (`skills/`, `kits/`, `schemas/`, etc.) and then run `cpt update --source . --force` to sync changes into `{cypilot_path}/`.

---

## Project Documentation (auto-configured)

<!-- auto-config:docs:start -->

ALWAYS open and follow `architecture/specs/CLISPEC.md` WHEN writing CLI commands, modifying command dispatch, or adding new subcommands

<!-- auto-config:docs:end -->
