# Spider Adapter: Spider

**Extends**: `../AGENTS.md`

**Version**: 2.0
**Last Updated**: 2026-02-03

---

## Project Overview

Spider is a workflow-centered methodology framework for AI-assisted software development with design-to-code traceability. This adapter configures Spider for the Spider framework itself (self-hosted).

---

## Navigation Rules

### Schema & Registry

ALWAYS open and follow `../schemas/artifacts.schema.json` WHEN working with artifacts.json

ALWAYS open and follow `../requirements/artifacts-registry.md` WHEN working with artifacts.json

ALWAYS open and follow `artifacts.json` WHEN Spider uses weaver `spider-sdlc` for artifact kinds: PRD, DESIGN, DECOMPOSITION, ADR, FEATURE OR codebase

### Tech Stack & Conventions

ALWAYS open and follow `specs/tech-stack.md` WHEN Spider uses weaver `spider-sdlc` for artifact kinds: DESIGN, ADR OR codebase

ALWAYS open and follow `specs/conventions.md` WHEN Spider uses weaver `spider-sdlc` for codebase

### Domain Model

ALWAYS open and follow `specs/domain-model.md` WHEN Spider uses weaver `spider-sdlc` for artifact kinds: DESIGN, DECOMPOSITION, FEATURE OR codebase

### Project Structure

ALWAYS open and follow `specs/project-structure.md` WHEN Spider uses weaver `spider-sdlc` for artifact kinds: DESIGN, ADR OR codebase

### Testing

ALWAYS open and follow `specs/testing.md` WHEN Spider uses weaver `spider-sdlc` for codebase

### Build & Deploy

ALWAYS open and follow `specs/build-deploy.md` WHEN Spider uses weaver `spider-sdlc` for codebase

### Patterns

ALWAYS open and follow `specs/patterns.md` WHEN Spider uses weaver `spider-sdlc` for artifact kinds: DESIGN, ADR, FEATURE OR codebase

---

## Artifact Locations

| Kind | Path | Traceability |
|------|------|--------------|
| PRD | `architecture/PRD.md` | FULL |
| DESIGN | `architecture/DESIGN.md` | FULL |
| DECOMPOSITION | `architecture/DECOMPOSITION.md` | FULL |
| ADR | `architecture/ADR/general/*.md` | FULL |

## Codebase Locations

| Name | Path | Extensions |
|------|------|------------|
| Spider CLI | `skills/spider/scripts/spider/` | `.py` |
| Tests | `tests/` | `.py` |

---

## Quick Reference

- **Adapter**: `.spider-adapter/`
- **Weaver**: `weavers/sdlc/`
- **Workflows**: `workflows/`
- **Requirements**: `requirements/`
- **Schemas**: `schemas/`
