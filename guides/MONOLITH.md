# Modular Monolith Guide

Use this guide when you have a single repository and a single deployable (a monolith), but the codebase is organized into **modules** with strict boundaries.

Examples use Windsurf slash commands (like `/fdd-design`).
You can apply the same flow in any agent by opening the corresponding workflow files under `workflows/`.

## Goal

Maintain:
- A validated **project-level architecture** (overall design + ADRs).
- A validated **module-level architecture** for each module.

In a modular monolith:
- Project-level architecture lives in `architecture/DESIGN.md` and `architecture/ADR/**`.
- Each module MUST have its architecture isolated inside the module folder (co-located with the code).

A practical convention is:
- Module code lives under `src/modules/{module}/`.
- Module architecture lives under `src/modules/{module}/architecture/`.
- The module architecture is a full set of FDD artifacts (module-level scope):
  - `src/modules/{module}/architecture/PRD.md`
  - `src/modules/{module}/architecture/DESIGN.md`
  - `src/modules/{module}/architecture/ADR/**`
  - `src/modules/{module}/architecture/features/FEATURES.md`
  - `src/modules/{module}/architecture/features/feature-{slug}/DESIGN.md`

## Recommended Structure (Example)

Monolith repo example:
- `src/modules/auth/`
- `src/modules/billing/`
- `src/modules/notifications/`

FDD artifacts:
- `architecture/PRD.md`
- `architecture/DESIGN.md`
- `architecture/ADR/**`
- `architecture/features/FEATURES.md` (project-level features)
- `architecture/features/feature-{slug}/DESIGN.md`
- `src/modules/auth/architecture/PRD.md`
- `src/modules/auth/architecture/DESIGN.md`
- `src/modules/auth/architecture/ADR/**`
- `src/modules/auth/architecture/features/FEATURES.md`
- `src/modules/billing/architecture/PRD.md`
- `src/modules/billing/architecture/DESIGN.md`
- `src/modules/billing/architecture/ADR/**`
- `src/modules/billing/architecture/features/FEATURES.md`

## How to Provide Context in Prompts

In a modular monolith, the most important context is:
- Module list and module boundaries.
- Allowed dependencies between modules.
- Where code for each module lives.

Example format:
```text
/fdd-design
Context:
- Architecture style: modular monolith
- Scope: project
- Modules:
  - auth
  - billing
  - notifications
- Project features (NOT modules):
  - pricing-plans
  - invoice-lifecycle
  - tenant-management
- Code map:
  - auth: src/modules/auth/
  - billing: src/modules/billing/
  - notifications: src/modules/notifications/
- Module architecture paths:
  - auth: src/modules/auth/architecture/
  - billing: src/modules/billing/architecture/
  - notifications: src/modules/notifications/architecture/
- Module dependency rules:
  - auth -> (none)
  - billing -> auth
  - notifications -> auth
```

## Workflow Sequence (Modular Monolith)

This is a two-level workflow:
- Project-level artifacts describe the full system and cross-module rules.
- Module-level artifacts describe one module in isolation, but must stay compatible with the project architecture.

### 1. `/fdd-prd`

**What it does**:
- Creates or updates `architecture/PRD.md` ([taxonomy](TAXONOMY.md#prdmd)).

**Provide context**:
- Product vision + actors/capabilities
- The fact you are building a modular monolith

Prompt example:
```text
/fdd-prd
Context:
- Product: SaaS platform
- Architecture style: modular monolith
- Core modules: auth, billing, notifications
```

### 2. `/fdd-prd-validate`

```text
/fdd-prd-validate
```

### 3. `/fdd-design` (Project-level Overall Design + ADRs)

**What it does**:
- Creates or updates `architecture/DESIGN.md` ([taxonomy](TAXONOMY.md#designmd)).
- Creates or updates `architecture/ADR/**` ([taxonomy](TAXONOMY.md#adr)).

**Provide context**:
- Module list
- Cross-module integration approach (shared DB, events, internal APIs)
- Dependency rules between modules

Prompt example:
```text
/fdd-design
Context:
- Architecture style: modular monolith
- Scope: project
- Modules:
  - auth (src/modules/auth/)
  - billing (src/modules/billing/)
- Dependency rules:
  - billing -> auth
- Integration:
  - Shared DB, but tables are owned by modules
  - Cross-module calls must go via module public interfaces
```

If you need to create a new ADR or edit an existing ADR explicitly, use the dedicated ADR workflow:
```text
/fdd-adr
```

### 4. `/fdd-design-validate`

```text
/fdd-design-validate
```

If you created or updated ADRs, you can also run the dedicated ADR validator:
```text
/fdd-adr-validate
Context:
- Focus on ADR ID: `fdd-myapp-adr-module-boundaries`
```

### 5. `/fdd-features` (Project-level Features)

**What it does**:
- Creates or updates `architecture/features/FEATURES.md` ([taxonomy](TAXONOMY.md#featuresmd)).

**Provide context**:
- Project-level features (core product features, shared libraries, cross-cutting capabilities)
- Major constraints and non-goals
- Explicitly: do not list modules here

Prompt example:
```text
/fdd-features
Context:
- Architecture style: modular monolith
- Scope: project
- Project features:
  - pricing-plans
  - invoice-lifecycle
  - tenant-management
```

### 6. `/fdd-features-validate`

```text
/fdd-features-validate
```

## Module-Level Architecture (Repeat per Module)

Use this section when you want a module to have a fully self-contained architecture (including module-level PRD/DESIGN/ADR/FEATURES).

Notes:
- Module-level `FEATURES.md` describes features inside that module.
- Module features are not the same as project-level features.

### 7. `/fdd-prd` (Module)

**What it does**:
- Creates or updates module PRD:
  - `src/modules/{module}/architecture/PRD.md`

Prompt example:
```text
/fdd-prd
Context:
- Scope: module
- Module: auth
- Module code path: src/modules/auth/
- Module architecture root: src/modules/auth/architecture/
```

### 8. `/fdd-design` (Module)

**What it does**:
- Creates or updates module design and ADRs:
  - `src/modules/{module}/architecture/DESIGN.md`
  - `src/modules/{module}/architecture/ADR/**`

Prompt example:
```text
/fdd-design
Context:
- Scope: module
- Module: auth
- Module code path: src/modules/auth/
- Module architecture root: src/modules/auth/architecture/
- Dependencies:
  - Allowed: none
  - Consumes from other modules: (none)
```

### 9. `/fdd-features` (Module)

**What it does**:
- Creates or updates module features manifest:
  - `src/modules/{module}/architecture/features/FEATURES.md`

Prompt example:
```text
/fdd-features
Context:
- Scope: module
- Module: auth
- Module code path: src/modules/auth/
- Module architecture root: src/modules/auth/architecture/
```

### 10. `/fdd-feature` (Module)

**What it does**:
- Creates or updates a module feature design:
  - `src/modules/{module}/architecture/features/feature-{slug}/DESIGN.md` ([taxonomy](TAXONOMY.md#feature-designmd)).

**Provide context**:
- Target module slug
- Module responsibilities and public interface
- Data ownership (tables, events)
- Explicit “allowed dependencies” for this module
- Module code path
- Module architecture path

Prompt example:
```text
/fdd-feature
Context:
- Scope: module
- Module: auth
- Feature: sessions
- Module code path: src/modules/auth/
- Module architecture root: src/modules/auth/architecture/
- Public interface:
  - AuthService (login, logout, refresh)
  - Auth middleware integration for other modules
- Data ownership:
  - Owns tables: users, sessions
- Allowed dependencies:
  - No dependencies on other modules
```

### 11. `/fdd-feature-validate`

```text
/fdd-feature-validate
Context:
- Scope: module
- Module: auth
- Feature: sessions
```

### 12. `/fdd-code`

**What it does**:
- Implements the feature directly from `DESIGN.md` (default path).

Prompt example:
```text
/fdd-code
Context:
- Scope: module
- Module: auth
- Feature: sessions
- Module code path: src/modules/auth/
- Module architecture root: src/modules/auth/architecture/
```

### 16. `/fdd-code-validate`

```text
/fdd-code-validate
Context:
- Scope: module
- Module: auth
- Feature: sessions
- Code paths:
  - src/modules/auth/
```

## Adapter Example for a Modular Monolith

Below is an example of what you typically encode in your project adapter.

### `FDD-Adapter/AGENTS.md`

```markdown
# Project FDD Adapter

ALWAYS open and follow `../FDD/AGENTS.md`

WHEN working in this repo:
- This is a modular monolith.
- Each module MUST have its architecture co-located with module code.
- Module architecture path convention:
  - `src/modules/{module}/architecture/PRD.md`
  - `src/modules/{module}/architecture/DESIGN.md`
  - `src/modules/{module}/architecture/ADR/**`
  - `src/modules/{module}/architecture/features/FEATURES.md`
  - `src/modules/{module}/architecture/features/feature-{slug}/DESIGN.md`
- Module boundaries are enforced by code structure and dependency rules.

WHEN asked to generate/validate feature artifacts:
- Ask whether the scope is project-level or module-level.
- If module-level: ask which module is in scope.
- Ask for the module code path(s).
- Ask for the module architecture path(s).
```

### `FDD-Adapter/specs/patterns.md` (excerpt)

```markdown
# Modular Monolith Patterns

## Module Boundaries

- Modules live under `src/modules/{module}/`.
- The feature slug MUST match the module name (e.g. `auth` -> `feature-auth`).

## Dependencies

- A module may only depend on the public interfaces of other modules.
- Cycles are forbidden.
- Shared DB is allowed, but table ownership must be defined per module.

## How to Read Code

- Prefer scanning module entry points first:
  - `src/modules/{module}/index.*`
  - `src/modules/{module}/public.*`
- Treat anything under `internal/` as non-public.
```

## Status

- This guide is focused on structure and prompts.
- You still follow the standard FDD taxonomy and validators.
