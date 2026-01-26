# Brownfield Guide

Use this guide when you already have a codebase and want to adopt FDD.

Examples use Windsurf slash commands (like `/fdd-design`).
You can apply the same flow in any agent by opening the corresponding workflow files under `workflows/`.

## Choose Your Starting Point

If you have a monolith with strict module boundaries (a modular monolith), see: [MONOLITH.md](MONOLITH.md)

### Baseline (Existing System)

Use this track when you have an existing codebase (with or without existing docs).

**Goal**: produce validated baseline artifacts so future changes are controlled.

- Use the codebase and any existing docs as input.
- Create `architecture/PRD.md` ([taxonomy](TAXONOMY.md#prdmd)).
- Create `architecture/DESIGN.md` ([taxonomy](TAXONOMY.md#designmd)).
- Capture stable decisions as ADRs when needed ([taxonomy](TAXONOMY.md#adr)).
- Validate baseline artifacts before feature work.

### Add a New Feature (Existing System)

Use this when baseline exists and you want to code a new capability.

- Update `architecture/features/FEATURES.md` ([taxonomy](TAXONOMY.md#featuresmd)).
- Create/update feature `DESIGN.md` ([taxonomy](TAXONOMY.md#feature-designmd)).
- Implement with `implement`.


## How to Provide Context in Prompts

Brownfield work is context-heavy.
Add context to each prompt to control what the agent reads and how it maps existing reality into FDD artifacts.

Recommended context to include:
- Existing code entry points (directories, modules)
- Existing docs you trust (paths)
- Constraints and invariants you must preserve
- What you want to treat as source of truth (code vs docs)
- For validation workflows: what artifact/path you want to validate (defaults are standard FDD locations)

Example format:
```text
/fdd-design
Context:
- Source of truth: code
- Code areas:
  - src/api/
  - src/domain/
- Existing docs:
  - docs/architecture.md (may be outdated)
```

## Workflow Sequence

### Baseline (Existing System)

Goal:
- Produce validated baseline artifacts before you add or refactor features.

#### 1. `/fdd-prd`

**What it does**:
- Creates or updates `architecture/PRD.md` ([taxonomy](TAXONOMY.md#prdmd)).

**Provide context**:
- If docs exist: paths and what is reliable
- If docs are missing: where in code to look for user roles and capabilities

Prompt example:
```text
/fdd-prd
Context:
- Source of truth: code
- Code entry points:
  - src/routes/
  - src/controllers/
```

#### 2. `/fdd-prd-validate`

```text
/fdd-prd-validate
```

#### 3. `/fdd-design` (ADR + Overall Design)

**What it does**:
- Creates or updates `architecture/DESIGN.md` ([taxonomy](TAXONOMY.md#designmd)).
- Creates or updates ADRs when decisions must be recorded ([taxonomy](TAXONOMY.md#adr)).

**Provide context**:
- If you have OpenAPI/GraphQL/DB schema: file paths
- Constraints you must preserve (compatibility, migrations, auth)

Prompt example:
```text
/fdd-design
Context:
- Source of truth: code
- Existing specs:
  - docs/openapi.yaml
  - docs/db-schema.md
- Constraints:
  - Do not break public API
```

If you need to create a new ADR or edit an existing ADR explicitly, use the dedicated ADR workflow:
```text
/fdd-adr
```

#### 4. `/fdd-design-validate`

```text
/fdd-design-validate
```

If you created or updated ADRs, you can also run the dedicated ADR validator:
```text
/fdd-adr-validate
```

To narrow the scope, add a focus ID in the same prompt (for example a requirement/principle ID referenced by ADRs):
```text
/fdd-adr-validate
Context:
- Focus on ADR ID: `fdd-myapp-adr-authentication-strategy`
```

#### 5. `/fdd-features`

**What it does**:
- Creates or updates `architecture/features/FEATURES.md` ([taxonomy](TAXONOMY.md#featuresmd)).

**Provide context**:
- If the system is large: which modules/domains should become separate features
- Any feature boundaries you want to enforce (ownership, deployment boundaries)

Prompt example:
```text
/fdd-features
Context:
- Group features by modules: billing, auth, reporting
```

#### 6. `/fdd-features-validate`

```text
/fdd-features-validate
```

### Add a New Feature

#### 1. `/fdd-features` (Update feature list)
```text
/fdd-features
Context:
- Add feature: notifications
```

#### 2. `/fdd-feature` (Design the feature)
```text
/fdd-feature
Context:
- Feature: notifications
- Include scenarios: retries, rate limits, provider outage
- Code boundaries:
  - src/notifications/
```

#### 3. `/fdd-feature-validate`
```text
/fdd-feature-validate
Context:
- Feature: notifications
```

#### 4. `/fdd-code`
```text
/fdd-code
Context:
- Feature: notifications
- Where to implement:
  - src/notifications/
```

#### 5. `/fdd-code-validate`
```text
/fdd-code-validate
Context:
- Feature: notifications
```

## Common Scenarios (Brownfield)

### Scenario 1: Requirements Changed (PRD)

When you need to change PRD capabilities:

```text
/fdd-prd
/fdd-prd-validate
```

Then update design and affected features as needed.

### Scenario 2: Design Changed (ADR + Overall Design)

When you discovered a missing domain field, API constraint, or architectural rule:

```text
/fdd-design
/fdd-design-validate
```

Then update impacted feature designs and re-validate them.

### Scenario 3: Feature Design Changed

When feature behavior changes:

```text
/fdd-feature
/fdd-feature-validate
/fdd-code
```

## Quick Reference

### Add a Feature

```text
/fdd-features
/fdd-features-validate
/fdd-feature
/fdd-feature-validate
/fdd-code
/fdd-code-validate
```

## Keeping Features Actual After Code Changes

- If code changes affect a feature behavior, update the feature `DESIGN.md` first.
- Re-validate the feature design.
- Run `code-validate` to ensure design and code remain consistent.
