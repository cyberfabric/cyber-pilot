---
status: accepted
date: 2026-03-07
decision-makers: project maintainer
---

# ADR-0009: Two-Workflow Model (Generate / Analyze)


<!-- toc -->

- [Context and Problem Statement](#context-and-problem-statement)
- [Decision Drivers](#decision-drivers)
- [Considered Options](#considered-options)
- [Decision Outcome](#decision-outcome)
  - [Consequences](#consequences)
  - [Confirmation](#confirmation)
- [Pros and Cons of the Options](#pros-and-cons-of-the-options)
  - [Two universal workflows](#two-universal-workflows)
  - [Per-artifact workflows](#per-artifact-workflows)
  - [Per-operation workflows](#per-operation-workflows)
- [Traceability](#traceability)

<!-- /toc -->

**ID**: `cpt-cypilot-adr-two-workflow-model`

## Context and Problem Statement

AI agents need structured workflows to follow when users request Cypilot operations. The system could provide many specialized workflows (one per artifact kind, one per operation type) or a small number of universal workflows that route internally. Too many workflows increase maintenance and agent confusion; too few may be too generic.

## Decision Drivers

* **Agent simplicity** — agents perform better with fewer, well-defined entry points than with many specialized ones
* **Intent classification** — all user requests naturally divide into "change something" (write) or "check something" (read)
* **Maintenance** — fewer workflows mean less duplication of shared logic (execution protocol, rule loading, config resolution)
* **Kit extensibility** — kits add domain-specific content (rules, templates, checklists) but should not need to define new workflow types

## Considered Options

1. **Two universal workflows** (Generate / Analyze) — write vs read intent classification
2. **Per-artifact workflows** — one workflow per artifact kind (create-prd, review-adr, etc.)
3. **Per-operation workflows** — one workflow per operation (create, update, validate, review, etc.)

## Decision Outcome

Chosen: **Exactly two universal workflows**:

1. **Generate** (write intent): create, edit, fix, update, implement, refactor, configure, build
2. **Analyze** (read intent): validate, review, check, inspect, audit, compare, list, find

Both workflows share a common execution protocol (load config, resolve system, load rules). Kit-specific behavior is injected through rules, templates, and checklists — not through separate workflow files.

Kit workflow files (e.g., `pr-review.md`, `pr-status.md`) are agent entry points that delegate to the core generate/analyze workflows with pre-configured parameters.

### Consequences

* Good, because agents only need to classify intent as "write" or "read" — simple routing
* Good, because shared execution protocol is maintained in one place
* Good, because kits extend behavior through content (rules/templates), not new workflow types
* Bad, because some operations (e.g., PR review) feel like they need their own workflow — mitigated by kit workflow entry points that wrap the core workflows
* Neutral, because "ambiguous intent" cases prompt the user to clarify

### Confirmation

Confirmed by all user requests being classifiable as either generate (write) or analyze (read) intent, with kit workflow entry points delegating to the two core workflows.

## Pros and Cons of the Options

### Two universal workflows

* Good, because simple intent classification for agents
* Good, because shared execution protocol
* Bad, because some operations feel like they need their own workflow

### Per-artifact workflows

* Good, because precise, tailored behavior per artifact
* Bad, because N×M explosion (artifacts × operations)
* Bad, because duplicated execution protocol

### Per-operation workflows

* Good, because clear operation semantics
* Bad, because still many workflows to maintain
* Bad, because kits must define new workflow types

## Traceability

- **PRD**: `cpt-cypilot-fr-core-workflows`
- **DESIGN**: Architecture Drivers → Generic Workflows
