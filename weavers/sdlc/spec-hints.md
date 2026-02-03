# Spec Hints for SDLC Weaver

Maps adapter specs to artifact kinds supported by this weaver. Used by `/spider-adapter` to generate WHEN rules in `AGENTS.md`.

## Supported Artifact Kinds

This weaver supports the following artifact kinds:
- `PRD` — Product Requirements Document
- `DESIGN` — Technical Design
- `DECOMPOSITION` — Features Manifest
- `FEATURE` — Individual Feature Design
- `ADR` — Architecture Decision Record

## Spec Mapping

| Spec | Artifact Kinds | Codebase | Description |
|------|----------------|----------|-------------|
| `tech-stack.md` | DESIGN, ADR | ✓ | Languages, frameworks, dependencies |
| `project-structure.md` | DESIGN, ADR | ✓ | Directory layout, module organization |
| `domain-model.md` | DESIGN, DECOMPOSITION, FEATURE | ✓ | Core concepts, entities, data structures |
| `conventions.md` | — | ✓ | Code style, naming, file organization |
| `testing.md` | — | ✓ | Test framework, patterns, coverage |
| `build-deploy.md` | — | ✓ | Build commands, CI/CD, deployment |
| `api-contracts.md` | DESIGN, ADR, FEATURE | ✓ | API patterns, contracts, protocols |
| `patterns.md` | DESIGN, ADR, FEATURE | ✓ | Architecture and design patterns |
| `security.md` | DESIGN, ADR, FEATURE | ✓ | Auth, authorization, data protection |
| `data-governance.md` | DESIGN, FEATURE | ✓ | Data lifecycle, retention, privacy |
| `performance.md` | DESIGN, ADR, FEATURE | ✓ | SLAs, caching, optimization |
| `reliability.md` | DESIGN, ADR, FEATURE | ✓ | Error handling, recovery, resilience |
| `compliance.md` | PRD, DESIGN, FEATURE | ✓ | Regulations, standards, audit |

## How Adapter Uses This

1. Adapter reads `artifacts.json` → finds weaver `spider-sdlc`
2. Adapter loads `weavers/sdlc/spec-hints.md` → parses mapping table
3. For each spec file that exists in adapter:
   - Generates WHEN rule with artifact kinds from this mapping
   - Adds `OR codebase` if Codebase column is ✓

## Example Generated Rules

```markdown
ALWAYS open and follow `specs/domain-model.md` WHEN Spider uses weaver `spider-sdlc` for artifact kinds: DESIGN, DECOMPOSITION, FEATURE OR codebase

ALWAYS open and follow `specs/conventions.md` WHEN Spider uses weaver `spider-sdlc` for codebase
```

---

**Version**: 1.0
**Last Updated**: 2026-02-03
