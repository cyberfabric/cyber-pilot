# Brownfield Guide

Use this guide when you already have a codebase and want to adopt Spider.

Examples use Windsurf slash commands (like `/spider-design`).
You can apply the same flow in any agent by opening the corresponding workflow files under `workflows/`.

## Choose Your Starting Point

If you have a monolith with strict module boundaries (a modular monolith), see: [MONOLITH.md](MONOLITH.md)

### Baseline (Existing System)

Use this track when you have an existing codebase (with or without existing docs).

**Goal**: produce validated baseline artifacts so future changes are controlled.

- Use the codebase and any existing docs as input.
- Create the PRD artifact (default: `architecture/PRD.md`) ([taxonomy](TAXONOMY.md#prdmd)).
- Create the overall design artifact (default: `architecture/DESIGN.md`) ([taxonomy](TAXONOMY.md#designmd)).
- Capture stable decisions as ADRs when needed ([taxonomy](TAXONOMY.md#adr)).
- Validate baseline artifacts before feature work.

### Add a New Feature (Existing System)

Use this when baseline exists and you want to code a new capability.

- Update the DECOMPOSITION artifact (default: `architecture/DECOMPOSITION.md`) ([taxonomy](TAXONOMY.md#decompositionmd)).
- Create/update feature `DESIGN.md` ([taxonomy](TAXONOMY.md#feature-designmd)).
- Implement with `implement`.


## How to Provide Context in Prompts

Brownfield work is context-heavy.
Add context to each prompt to control what the agent reads and how it maps existing reality into Spider artifacts.

Recommended context to include:
- Existing code entry points (directories, modules)
- Existing docs you trust (paths)
- Constraints and invariants you must preserve
- What you want to treat as source of truth (code vs docs)
- For validation workflows: what artifact/path you want to validate (resolve via `{adapter-dir}/artifacts.json`; defaults may be `architecture/...`)

Example format:
```text
/spider-design
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

#### 1. `/spider-prd`

**What it does**:
- Creates or updates the PRD artifact ([taxonomy](TAXONOMY.md#prdmd)).

**Provide context**:
- If docs exist: paths and what is reliable
- If docs are missing: where in code to look for user roles and capabilities

Prompt example:
```text
/spider-prd
Context:
- Source of truth: code
- Code entry points:
  - src/routes/
  - src/controllers/
```

#### 2. `/spider-prd-validate`

```text
/spider-prd-validate
```

#### 3. `/spider-design` (ADR + Overall Design)

**What it does**:
- Creates or updates the overall design artifact ([taxonomy](TAXONOMY.md#designmd)).
- Creates or updates ADRs when decisions must be recorded ([taxonomy](TAXONOMY.md#adr)).

**Provide context**:
- If you have OpenAPI/GraphQL/DB schema: file paths
- Constraints you must preserve (compatibility, migrations, auth)

Prompt example:
```text
/spider-design
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
/spider-adr
```

#### 4. `/spider-design-validate`

```text
/spider-design-validate
```

If you created or updated ADRs, you can also run the dedicated ADR validator:
```text
/spider-adr-validate
```

To narrow the scope, add a focus ID in the same prompt (for example a requirement/principle ID referenced by ADRs):
```text
/spider-adr-validate
Context:
- Focus on ADR ID: `spd-myapp-adr-authentication-strategy`
```

#### 5. `/spider-features`

**What it does**:
- Creates or updates the DECOMPOSITION artifact ([taxonomy](TAXONOMY.md#featuresmd)).

**Provide context**:
- If the system is large: which modules/domains should become separate features
- Any feature boundaries you want to enforce (ownership, deployment boundaries)

Prompt example:
```text
/spider-features
Context:
- Group features by modules: billing, auth, reporting
```

#### 6. `/spider-features-validate`

```text
/spider-features-validate
```

### Add a New Feature

#### 1. `/spider-features` (Update feature list)
```text
/spider-features
Context:
- Add feature: notifications
```

#### 2. `/spider-feature` (Design the feature)
```text
/spider-feature
Context:
- Feature: notifications
- Include scenarios: retries, rate limits, provider outage
- Code boundaries:
  - src/notifications/
```

#### 3. `/spider-feature-validate`
```text
/spider-feature-validate
Context:
- Feature: notifications
```

#### 4. `/spider-code`
```text
/spider-code
Context:
- Feature: notifications
- Where to implement:
  - src/notifications/
```

#### 5. `/spider-code-validate`
```text
/spider-code-validate
Context:
- Feature: notifications
```

## Common Scenarios (Brownfield)

### Scenario 1: Requirements Changed (PRD)

When you need to change PRD capabilities:

```text
/spider-prd
/spider-prd-validate
```

Then update design and affected features as needed.

### Scenario 2: Design Changed (ADR + Overall Design)

When you discovered a missing domain field, API constraint, or architectural rule:

```text
/spider-design
/spider-design-validate
```

Then update impacted feature designs and re-validate them.

### Scenario 3: Feature Design Changed

When feature behavior changes:

```text
/spider-feature
/spider-feature-validate
/spider-code
```

## Quick Reference

### Add a Feature

```text
/spider-features
/spider-features-validate
/spider-feature
/spider-feature-validate
/spider-code
/spider-code-validate
```

## Keeping Features Actual After Code Changes

- If code changes affect a feature behavior, update the feature `DESIGN.md` first.
- Re-validate the feature design.
- Run `code-validate` to ensure design and code remain consistent.
