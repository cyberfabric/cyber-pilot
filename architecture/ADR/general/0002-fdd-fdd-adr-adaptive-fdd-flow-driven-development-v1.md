# ADR-0002: Adaptive FDD - Flow-Driven Development

**Date**: 2026-01-25

**Status**: Accepted

**ADR ID**: `fdd-fdd-adr-adaptive-fdd-flow-driven-development-v1`

## Context and Problem Statement

FDD should behave as a set of loosely coupled workflows and tools where a user can start from any point (design, implementation, or validation) and still make progress. In brownfield projects, required artifacts may be missing, partially present, or exist only as informal context (docs, READMEs, tickets, prompts).

In this ADR, “Feature-Driven Design” terminology is considered deprecated and is not used.

In this ADR, “FDD” may be interpreted as:
- **Flow-Driven Development**: the methodology centered around flows/workflows, where artifacts and tooling are assembled into end-to-end user-driven pipelines.

Today, artifact discovery and dependency resolution are often tied to assumed repository layouts and strict prerequisites. This prevents “start anywhere” usage and makes adoption harder in large codebases where artifacts may be distributed across multiple scopes.

We need a deterministic, adapter-owned source of truth that:
- tells the `fdd` tool where to look for artifacts (and what they “mean”),
- supports hierarchical project scopes (system → sub-system → module),
- supports per-artifact traceability configuration,
- and enables adaptive (“ask the user”) behavior instead of hard failure when dependencies are missing.

## Decision Drivers

* Enable “start anywhere” adoption for brownfield projects (incremental onboarding without forcing upfront artifact creation).
* Keep core technology-agnostic while allowing project-specific layouts via the adapter system.
* Preserve deterministic validation behavior where possible, but avoid blocking progress when artifacts are absent.
* Support system decomposition into multiple nested scopes.
* Keep configuration discoverable for AI agents and tools, and editable by humans.

## Considered Options

* **Option 1: Hardcoded artifact locations**
* **Option 2: Store artifact locations only in `.fdd-config.json`**
* **Option 3: Adapter-owned `artifacts.json` registry + Flow-Driven Development (SELECTED)**

## Decision Outcome

Chosen option: **Adapter-owned `artifacts.json` registry + Flow-Driven Development**, because it allows the `fdd` tool and workflows to deterministically discover project structure and artifact locations across complex codebases, while enabling adaptive user-guided fallback when artifacts are missing.

### What changes

1. The FDD adapter directory MUST contain an `artifacts.json` file describing:
   - artifact kinds, locations (roots/globs), and semantics (normative vs context-only),
   - hierarchical project scopes (system → sub-system → module),
   - per-artifact configuration including code traceability enablement.

2. The `fdd` tool MUST use `artifacts.json` to locate artifacts and resolve dependencies.
   - If an expected dependency is not found, `fdd` MUST continue validation using only discovered artifacts and MUST report missing dependencies as diagnostics (not as a crash condition).
   - Interactive workflows and agents SHOULD ask the user to provide a path, confirm a scope root, or accept “context-only” inputs to proceed.

3. Code traceability MUST be configurable per artifact (especially feature designs), because in brownfield adoption some features may be implemented before their feature design exists or before traceability tagging is introduced.

### Hierarchical Scopes (3 levels)

`artifacts.json` MUST support describing up to three levels of project scopes:

- **Level 1: System scope**
  - the overall repository context (global conventions, shared core artifacts, shared ADRs).
- **Level 2: Sub-system scope**
  - a large subsystem inside the system (may have its own architecture folder, its own features).
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
  - Module: `token-issuer` (may keep only context docs, or a local feature folder)
- **Example C (single-repo, single sub-system)**:
  - System: `platform`
  - Sub-system: `app` (the main runnable app)
  - Module: `payments` (a package/module inside the app)

Scopes MUST support inheritance:
- child scopes inherit artifact discovery rules from parent scopes,
- and may override/add locations for specific artifact kinds.

### Consequences

* Good, because FDD becomes usable in brownfield environments without forcing an upfront “perfect artifact graph”.
* Bad, because discovery becomes more flexible and therefore requires strong diagnostics and clear user interaction patterns to avoid confusion.

## Related Design Elements

**Actors**:
* `fdd-fdd-actor-ai-assistant` - Must guide the user through missing context and still complete workflows
* `fdd-fdd-actor-fdd-tool` - Must locate artifacts deterministically and report diagnostics
* `fdd-fdd-actor-technical-lead` - Configures adapter and project structure (including artifacts registry)

**Capabilities**:
* `fdd-fdd-fr-workflow-execution` - Workflows must remain executable even with partial artifacts
* `fdd-fdd-fr-validation` - Validation must work incrementally and report actionable results
* `fdd-fdd-fr-brownfield-support` - Brownfield adoption and incremental onboarding is a core capability
* `fdd-fdd-fr-adapter-config` - Project-specific structure and conventions live in adapters

**Requirements**:
* `fdd-fdd-req-executable-workflows` - Users can start from any workflow step and still progress
* `fdd-fdd-req-deterministic-validation` - Validators remain deterministic and provide structured reports
* `fdd-fdd-req-migration` - Must support incremental adoption for existing projects
* `fdd-fdd-req-adapter-configuration` - Adapter remains the extension point for project specifics

**Principles**:
* `fdd-fdd-principle-tech-agnostic` - Core remains portable; structure knowledge belongs to adapter/config
* `fdd-fdd-principle-machine-readable` - `artifacts.json` is machine-readable for tools and agents
* `fdd-fdd-principle-deterministic-gate` - Deterministic tooling still runs early; missing deps become diagnostics
