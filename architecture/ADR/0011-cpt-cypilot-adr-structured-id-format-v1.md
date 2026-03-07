---
status: accepted
date: 2026-03-07
decision-makers: project maintainer
---

# ADR-0011: Structured `cpt-*` ID Format with `@cpt-*` Code Tags


<!-- toc -->

- [Context and Problem Statement](#context-and-problem-statement)
- [Decision Drivers](#decision-drivers)
- [Considered Options](#considered-options)
- [Decision Outcome](#decision-outcome)
  - [Consequences](#consequences)
  - [Confirmation](#confirmation)
- [Pros and Cons of the Options](#pros-and-cons-of-the-options)
  - [Structured `cpt-*` IDs with `@cpt-*` code tags](#structured-cpt-ids-with-cpt-code-tags)
  - [UUID-based IDs](#uuid-based-ids)
  - [File path references](#file-path-references)
- [Traceability](#traceability)

<!-- /toc -->

**ID**: `cpt-cypilot-adr-structured-id-format`

## Context and Problem Statement

Cypilot's core value is linking design elements to code. This requires a unique identifier system that works across Markdown artifacts and source code files in any programming language. IDs must be human-readable, deterministically parseable, and collision-resistant across systems in a monorepo.

## Decision Drivers

* **Human readability** — IDs appear in design documents read by humans; they must convey meaning
* **Deterministic parsing** — IDs must be extractable by regex without Markdown/AST parsing
* **Collision resistance** — monorepos with multiple systems need namespace isolation
* **Language agnosticism** — code tags must work in any programming language's comment syntax
* **Bidirectional traceability** — from design → code (where is this implemented?) and code → design (why does this exist?)

## Considered Options

1. **Structured `cpt-*` IDs with `@cpt-*` code tags** — human-readable, grep-friendly, namespace-isolated
2. **UUID-based IDs** — globally unique, no naming conventions
3. **File path references** — use file paths as identifiers

## Decision Outcome

Chosen: **Structured ID format `cpt-{system}-{kind}-{slug}`** in artifacts, with **`@cpt-*` code tags** in source files.

### Consequences

**Artifact IDs** (definitions): `**ID**: \`cpt-cypilot-fr-core-init\``
- `cpt` — universal prefix (grep-friendly, collision-resistant)
- `{system}` — system slug for monorepo namespace isolation
- `{kind}` — element type (fr, nfr, actor, usecase, algo, component, etc.)
- `{slug}` — human-readable identifier

**Code tags** (references): `@cpt-cypilot-fr-core-init` in language-native comments
- Block markers: `@cpt-begin:{id}` / `@cpt-end:{id}` for coverage measurement
- Inline markers: `@cpt-ref:{id}` for point references

**ID versioning**: optional `-vN` suffix (e.g., `cpt-{system}-fr-{slug}-v2`) for tracking ID evolution.

* Good, because human-readable — `cpt-cypilot-fr-core-init` tells you: system=cypilot, kind=functional-requirement, scope=core-init
* Good, because grep-friendly — `grep -r "cpt-cypilot-fr-core-init"` finds all references instantly
* Good, because namespace isolation — `cpt-backend-*` vs `cpt-frontend-*` never collide
* Good, because language-agnostic — `@cpt-*` works in `//`, `#`, `/* */`, `--`, `%` comments
* Bad, because verbose — long IDs in code comments add visual noise
* Bad, because manual tagging — developers must add `@cpt-*` tags (mitigated by generate workflow adding them automatically)

### Confirmation

Confirmed by bidirectional traceability working across all architecture artifacts and source files using `grep -r "cpt-cypilot-"` for discovery.

## Pros and Cons of the Options

### Structured `cpt-*` IDs with `@cpt-*` code tags

* Good, because human-readable and grep-friendly
* Good, because namespace isolation for monorepos
* Bad, because verbose IDs in code comments

### UUID-based IDs

* Good, because globally unique, no collisions
* Bad, because not human-readable — `a1b2c3d4` conveys no meaning
* Bad, because not grep-friendly

### File path references

* Good, because no separate ID system needed
* Bad, because breaks on file rename/move
* Bad, because no granularity below file level

## Traceability

- **PRD**: `cpt-cypilot-fr-core-traceability`
- **DESIGN**: `cpt-cypilot-component-traceability-engine`, `cpt-cypilot-principle-traceability-by-design`
- **Spec**: `architecture/specs/traceability.md`
