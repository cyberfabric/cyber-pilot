# Greenfield Guide

Use this guide when you are starting a new project from scratch.

Examples use Windsurf slash commands (like `/fdd-design`).
You can apply the same flow in any agent by opening the corresponding workflow files under `workflows/`.

## Goal

Create a validated baseline (PRD + architecture) before writing code.

## What You Will Produce

- `architecture/PRD.md` ([taxonomy](TAXONOMY.md#prdmd))
- `architecture/DESIGN.md` ([taxonomy](TAXONOMY.md#designmd))
- `architecture/ADR/**` ([taxonomy](TAXONOMY.md#adr))
- `architecture/features/FEATURES.md` ([taxonomy](TAXONOMY.md#featuresmd))
- `architecture/features/feature-{slug}/DESIGN.md` ([taxonomy](TAXONOMY.md#feature-designmd))

## How to Provide Context in Prompts

Each workflow can be run with additional context in the same prompt.

Recommended context to include:
- Current state (what exists already, what is missing)
- Links/paths to existing docs (README, specs, diagrams)
- Constraints (security, compliance, performance)
- Non-goals and out-of-scope items
- For validation workflows: what artifact/path you want to validate (defaults are standard FDD locations)

Example format:
```text
/fdd-design
Context:
- Repo: <short description>
- Existing docs:
  - docs/architecture.md
  - docs/openapi.yaml
- Constraints:
  - Must support SSO
  - Must be multi-tenant
```

The agent should:
- Read the provided inputs
- Ask targeted questions
- Propose answers
- Produce the artifact(s)

## Workflow Sequence (Greenfield)

### 1. `/fdd-prd`

**What it does**:
- Creates or updates `architecture/PRD.md` ([taxonomy](TAXONOMY.md#prdmd)).

**Provide context**:
- Product vision, target users, key capabilities
- Existing PRD/BRD (if any) and file paths

**Prompt example**:
```text
/fdd-prd
Context:
- Product: Task management API
- Users: individual users + teams
- Key capabilities: create tasks, assign tasks, due dates, comments
```

### 2. `/fdd-prd-validate`

**What it does**:
- Validates `architecture/PRD.md` deterministically.

**Provide context**:
- If your PRD artifact is not in the standard location, provide the exact path to validate

**Result**:
- PASS/FAIL with issues to fix.

Prompt example:
```text
/fdd-prd-validate
```

### 3. `/fdd-design` (ADR + Overall Design)

**What it does**:
- Creates or updates `architecture/DESIGN.md` ([taxonomy](TAXONOMY.md#designmd)).
- Creates or updates `architecture/ADR/**` as needed ([taxonomy](TAXONOMY.md#adr)).

**Provide context**:
- Architecture constraints (cloud/on-prem, multi-tenant, auth model)
- Existing domain model, database schema, API contracts

Prompt example:
```text
/fdd-design
Context:
- Tech: HTTP API, relational DB
- Constraints:
  - Must be multi-tenant
  - Must support audit logging
- Existing docs:
  - docs/openapi.yaml
  - docs/db-schema.md
```

If you need to create a new ADR or edit an existing ADR explicitly, use the dedicated ADR workflow:
```text
/fdd-adr
```

### 4. `/fdd-design-validate`

**What it does**:
- Validates `architecture/DESIGN.md` and related ADRs.

**Provide context**:
- If you want to validate a specific ADR first, provide the ADR file path
- If you have multiple services/modules, mention which code areas the design must describe

Prompt example:
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

### 5. `/fdd-features`

**What it does**:
- Creates or updates `architecture/features/FEATURES.md` ([taxonomy](TAXONOMY.md#featuresmd)) from the overall design.

**Provide context**:
- Any feature boundaries you want (what should be separate features)

Prompt example:
```text
/fdd-features
Context:
- Split into features by capability: task-crud, comments, notifications
```

### 6. `/fdd-features-validate`

**What it does**:
- Validates the features manifest.

**Provide context**:
- If you keep the features manifest in a non-standard place, provide the exact path to validate

Prompt example:
```text
/fdd-features-validate
```

### 7. `/fdd-feature`

**What it does**:
- Creates or updates a feature design: `architecture/features/feature-{slug}/DESIGN.md` ([taxonomy](TAXONOMY.md#feature-designmd)).

**Where SCENARIOS live**:
- Define feature-level test scenarios inside the feature `DESIGN.md`.

**Provide context**:
- Feature slug
- Acceptance criteria, edge cases, error handling expectations

Prompt example:
```text
/fdd-feature
Context:
- Feature: task-crud
- Include scenarios: bulk update, permission errors, validation errors
```

### 8. `/fdd-feature-validate`

**What it does**:
- Validates the feature design against overall design and manifest.

**Provide context**:
- Feature slug to validate (or the feature directory path)

Prompt example:
```text
/fdd-feature-validate
Context:
- Feature: task-crud
```

### 9. `/fdd-code`

**What it does**:
- Implements the feature directly from `DESIGN.md` (default path).

**Provide context**:
- Feature slug
- If code lives outside the default service/module, provide the relevant code paths

Prompt example:
```text
/fdd-code
Context:
- Feature: task-crud
```

### 10. `/fdd-code-validate`

**What it does**:
- Validates implementation against the feature design and traceability expectations.

**Provide context**:
- Feature slug (or feature directory path)
- If code lives outside the default service/module, provide the relevant code paths

Prompt example:
```text
/fdd-code-validate
Context:
- Feature: task-crud
```

## Iteration Rules

- If a change impacts behavior, update the relevant design first (overall or feature).
- Re-run the validator for the modified artifact before continuing.

## Rules

- Always run validation workflows before moving to the next layer.
- If code contradicts design, update design first, then re-validate.
