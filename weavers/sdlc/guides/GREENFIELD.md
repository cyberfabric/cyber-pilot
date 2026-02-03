# Greenfield Guide

Use this guide when you are starting a new project from scratch.

Examples use Windsurf slash commands (like `/spider-design`).
You can apply the same flow in any agent by opening the corresponding workflow files under [`workflows/`](../../../workflows/).

## Goal

Create a validated baseline (PRD + architecture) before writing code.

## What You Will Produce

- Spider artifacts registered in `{adapter-dir}/artifacts.json` ([taxonomy](TAXONOMY.md))
  - PRD (default: `{project-root}/architecture/PRD.md`)
  - Overall DESIGN (default: `{project-root}/architecture/DESIGN.md`)
  - ADR directory (default: `{project-root}/architecture/ADR/**`)
  - DECOMPOSITION (default: `{project-root}/architecture/DECOMPOSITION.md`)
  - Feature DESIGN (default: `{project-root}/architecture/features/feature-{slug}/DESIGN.md`)

## How to Provide Context in Prompts

Each workflow can be run with additional context in the same prompt.

Recommended context to include:
- Current state (what exists already, what is missing)
- Links/paths to existing docs (README, specs, diagrams)
- Constraints (security, compliance, performance)
- Non-goals and out-of-scope items
- For validation workflows: what artifact/path you want to validate (resolve via `{adapter-dir}/artifacts.json`; defaults may be `architecture/...`)

Example format:
```text
/spider-design
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

### 1. `/spider-prd`

**What it does**:
- Creates or updates the PRD artifact ([taxonomy](TAXONOMY.md#prdmd)).

**Provide context**:
- Product vision, target users, key capabilities
- Existing PRD/BRD (if any) and file paths

**Prompt example**:
```text
/spider-prd
Context:
- Product: Task management API
- Users: individual users + teams
- Key capabilities: create tasks, assign tasks, due dates, comments
```

### 2. `/spider-prd-validate`

**What it does**:
- Validates the PRD artifact deterministically (path resolved from `{adapter-dir}/artifacts.json`; default: `architecture/PRD.md`).

**Provide context**:
- If your PRD artifact is not in the standard location, provide the exact path to validate

**Result**:
- PASS/FAIL with issues to fix.

Prompt example:
```text
/spider-prd-validate
```

### 3. `/spider-design` (ADR + Overall Design)

**What it does**:
- Creates or updates the overall design artifact ([taxonomy](TAXONOMY.md#designmd)).
- Creates or updates ADR artifacts as needed ([taxonomy](TAXONOMY.md#adr)).

**Provide context**:
- Architecture constraints (cloud/on-prem, multi-tenant, auth model)
- Existing domain model, database schema, API contracts

Prompt example:
```text
/spider-design
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
/spider-adr
```

### 4. `/spider-design-validate`

**What it does**:
- Validates the overall design artifact and related ADRs (paths resolved from `{adapter-dir}/artifacts.json`; defaults: `architecture/DESIGN.md`, `architecture/ADR/**`).

**Provide context**:
- If you want to validate a specific ADR first, provide the ADR file path
- If you have multiple services/modules, mention which code areas the design must describe

Prompt example:
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

### 5. `/spider-features`

**What it does**:
- Creates or updates the DECOMPOSITION artifact ([taxonomy](TAXONOMY.md#featuresmd)) from the overall design.

**Provide context**:
- Any feature boundaries you want (what should be separate features)

Prompt example:
```text
/spider-features
Context:
- Split into features by capability: task-crud, comments, notifications
```

### 6. `/spider-features-validate`

**What it does**:
- Validates the features manifest.

**Provide context**:
- If you keep the features manifest in a non-standard place, provide the exact path to validate

Prompt example:
```text
/spider-features-validate
```

### 7. `/spider-feature`

**What it does**:
- Creates or updates a feature design artifact ([taxonomy](TAXONOMY.md#feature-designmd)).

**Where SCENARIOS live**:
- Define feature-level test scenarios inside the feature `DESIGN.md`.

**Provide context**:
- Feature slug
- Acceptance criteria, edge cases, error handling expectations

Prompt example:
```text
/spider-feature
Context:
- Feature: task-crud
- Include scenarios: bulk update, permission errors, validation errors
```

### 8. `/spider-feature-validate`

**What it does**:
- Validates the feature design against overall design and manifest.

**Provide context**:
- Feature slug to validate (or the feature directory path)

Prompt example:
```text
/spider-feature-validate
Context:
- Feature: task-crud
```

### 9. `/spider-code`

**What it does**:
- Implements the feature directly from the feature design artifact (path resolved from `{adapter-dir}/artifacts.json`; default: `architecture/features/feature-{slug}/DESIGN.md`).

**Provide context**:
- Feature slug
- If code lives outside the default service/module, provide the relevant code paths

Prompt example:
```text
/spider-code
Context:
- Feature: task-crud
```

### 10. `/spider-code-validate`

**What it does**:
- Validates implementation against the feature design and traceability expectations.

**Provide context**:
- Feature slug (or feature directory path)
- If code lives outside the default service/module, provide the relevant code paths

Prompt example:
```text
/spider-code-validate
Context:
- Feature: task-crud
```

## Iteration Rules

- If a change impacts behavior, update the relevant design first (overall or feature).
- Re-run the validator for the modified artifact before continuing.

## Rules

- Always run validation workflows before moving to the next layer.
- If code contradicts design, update design first, then re-validate.
