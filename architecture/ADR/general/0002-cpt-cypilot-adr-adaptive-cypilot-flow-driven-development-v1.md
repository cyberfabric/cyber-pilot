---
status: accepted
date: 2026-01-25
---

# ADR-0002: Adaptive Cypilot - Framework for Documentation and Development

**ID**: `cpt-cypilot-adr-adaptive-cypilot-flow-driven-development-v1`

## Context and Problem Statement

Cypilot should behave as a set of loosely coupled workflows and tools where a user can start from any point (design, implementation, or validation) and still make progress. In brownfield projects, required artifacts may be missing, partially present, or exist only as informal context (docs, READMEs, tickets, prompts).

In this ADR, "Spec-Driven Design" terminology is considered deprecated and is not used.

In this ADR, "Cypilot" may be interpreted as:
- **Framework for Documentation and Development**: the methodology centered around flows/workflows, where artifacts and tooling are assembled into end-to-end user-driven pipelines.

Today, artifact discovery and dependency resolution are often tied to assumed repository layouts and strict prerequisites. This prevents "start anywhere" usage and makes adoption harder in large codebases where artifacts may be distributed across multiple scopes.

We need a deterministic, adapter-owned source of truth that:
- tells the `cypilot` tool where to look for artifacts (and what they "mean"),
- supports hierarchical project scopes (system → sub-system → module),
- supports per-artifact traceability configuration,
- and enables adaptive ("ask the user") behavior instead of hard failure when dependencies are missing.

## Decision Drivers

- Enable "start anywhere" adoption for brownfield projects (incremental onboarding without forcing upfront artifact creation).
- Keep core technology-agnostic while allowing project-specific layouts via the adapter system.
- Preserve deterministic validation behavior where possible, but avoid blocking progress when artifacts are absent.
- Support system decomposition into multiple nested scopes.
- Keep configuration discoverable for AI agents and tools, and editable by humans.

## Considered Options

- **Option 1: Hardcoded artifact locations**
- **Option 2: Store artifact locations only in `.cypilot-config.json`**
- **Option 3: Adapter-owned `artifacts.json` registry + Framework for Documentation and Development (SELECTED)**

## Decision Outcome

Chosen option: **Adapter-owned `artifacts.json` registry + Framework for Documentation and Development**, because it allows the `cypilot` tool and workflows to deterministically discover project structure and artifact locations across complex codebases, while enabling adaptive user-guided fallback when artifacts are missing.

### What changes

1. The Cypilot adapter directory MUST contain an `artifacts.json` file describing:
   - artifact kinds, locations (roots/globs), and semantics (normative vs context-only),
   - hierarchical project scopes (system → sub-system → module),
   - per-artifact configuration including code traceability enablement.

2. The `cypilot` tool MUST use `artifacts.json` to locate artifacts and resolve dependencies.
   - If an expected dependency is not found, `cypilot` MUST continue validation using only discovered artifacts and MUST report missing dependencies as diagnostics (not as a crash condition).
   - Interactive workflows and agents SHOULD ask the user to provide a path, confirm a scope root, or accept "context-only" inputs to proceed.

3. Code traceability MUST be configurable per artifact (especially spec designs), because in brownfield adoption some specs may be implemented before their spec design exists or before traceability tagging is introduced.

### Hierarchical Scopes (3 levels)

`artifacts.json` MUST support describing up to three levels of project scopes:

- **Level 1: System scope**
  - the overall repository context (global conventions, shared core artifacts, shared ADRs).
- **Level 2: Sub-system scope**
  - a large subsystem inside the system (may have its own architecture folder, its own specs).
- **Level 3: Module scope**
  - a smaller unit within a sub-system (may have localized artifacts or be context-only).

Examples:
- **Example A (system → sub-system → module)**:
  - System: `platform`
  - Sub-system: `billing`
  - Module: `invoicing`
- **Example B (monorepo with shared + per-sub-system architecture)**:
  - System: `platform` (shared `architecture/` for org-wide decisions)
  - Sub-system: `auth` (has its own `modules/auth/architecture/`)
  - Module: `token-issuer` (may keep only context docs, or a local spec folder)
- **Example C (single-repo, single sub-system)**:
  - System: `platform`
  - Sub-system: `app` (the main runnable app)
  - Module: `payments` (a package/module inside the app)

Scopes MUST support inheritance:
- child scopes inherit artifact discovery rules from parent scopes,
- and may override/add locations for specific artifact kinds.

### Consequences

- Positive: Cypilot becomes usable in brownfield environments without forcing an upfront "perfect artifact graph"
- Negative: Discovery becomes more flexible and therefore requires strong diagnostics and clear user interaction patterns to avoid confusion
- Follow-up: Update tooling to use artifacts.json for artifact discovery

### Confirmation

Confirmed by validating artifact discovery across multiple example layouts using `cypilot adapter-info` + `cypilot validate`.

## Pros and Cons of the Options

### Option 1: Hardcoded artifact locations

* Good, because simplest to implement
* Bad, because breaks brownfield adoption and complex layouts

### Option 2: Store artifact locations only in `.cypilot-config.json`

* Good, because centralized configuration
* Bad, because poor discoverability for agents and hard to evolve across scopes

### Option 3: Adapter-owned `artifacts.json` registry

* Good, because deterministic discovery with hierarchical scopes
* Bad, because requires stronger diagnostics and tooling

## Traceability

- **PRD**: [PRD.md](../../PRD.md)
- **DESIGN**: [DESIGN.md](../../DESIGN.md)

This decision directly addresses the following requirements or design elements:

* `cpt-cypilot-fr-workflow-execution`
* `cpt-cypilot-fr-validation`
* `cpt-cypilot-fr-brownfield-support`
* `cpt-cypilot-fr-adapter-config`

