# Cypilot Adapter: Cypilot

**Extends**: `../AGENTS.md`

**Version**: 2.0
**Last Updated**: 2026-02-03

---

## Project Overview

Cypilot is a workflow-centered methodology framework for AI-assisted software development with design-to-code traceability. This adapter configures Cypilot for the Cypilot framework itself (self-hosted).

---

## Variables

**While Cypilot is enabled**, remember these variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `{cypilot_adapter_path}` | Directory containing this AGENTS.md | Root path for Cypilot Adapter navigation |

Use `{cypilot_adapter_path}` as the base path for all relative Cypilot Adapter file references.

---

## Navigation Rules

### Schema & Registry

ALWAYS open and follow `{cypilot_path}/schemas/artifacts.schema.json` WHEN working with artifacts.json

ALWAYS open and follow `{cypilot_path}/requirements/artifacts-registry.md` WHEN working with artifacts.json

### Project Specs

ALWAYS open and follow `specs/tech-stack.md` WHEN writing code, choosing technologies, or adding dependencies

ALWAYS open and follow `specs/conventions.md` WHEN writing code, naming files/functions/variables, or reviewing code

ALWAYS open and follow `specs/project-structure.md` WHEN creating files, adding modules, or navigating codebase

ALWAYS open and follow `specs/domain-model.md` WHEN working with entities, data structures, or business logic

ALWAYS open and follow `specs/testing.md` WHEN writing tests, reviewing test coverage, or debugging

ALWAYS open and follow `specs/build-deploy.md` WHEN building, deploying, or configuring CI/CD

ALWAYS open and follow `specs/patterns.md` WHEN implementing features, designing components, or refactoring

## Quick Reference

- **Adapter**: `.cypilot-adapter/`
- **Kit**: `kits/sdlc/`
- **Workflows**: `workflows/`
- **Requirements**: `requirements/`
- **Schemas**: `schemas/`
