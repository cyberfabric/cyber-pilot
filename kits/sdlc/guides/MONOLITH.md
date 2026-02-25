# Modular Monolith Guide

Use this guide when you have a single repository with a single deployable (a monolith) organized into **modules** with strict boundaries.

All prompts work through the `cypilot` skill — enable it with `cypilot on` and use natural language prompts.

## Goal

Maintain:
- A validated **project-level architecture** (overall design + ADRs)
- A validated **module-level architecture** for each module

---

## Artifact Registry Structure

In a modular monolith, modules are represented as `children` in the system hierarchy. The `artifacts.toml` schema supports nested systems for this purpose.

### Canonical Hierarchies

**Recommended nesting levels** (from project author):

| Hierarchy | When to use |
|-----------|-------------|
| **System → Subsystem → Component** | Most monoliths — clear boundaries, manageable depth |
| **System → Subsystem → Component → Module** | Large systems — when components need further decomposition |

**Examples:**

```
System: E-Commerce Platform
├── Subsystem: Storefront
│   ├── Component: Catalog
│   ├── Component: Cart
│   └── Component: Checkout
├── Subsystem: Backoffice
│   ├── Component: Inventory
│   ├── Component: Orders
│   └── Component: Reports
└── Subsystem: Platform
    ├── Component: Auth
    ├── Component: Billing
    └── Component: Notifications
```

```
System: Banking Platform
├── Subsystem: Core Banking
│   ├── Component: Accounts
│   │   ├── Module: Current
│   │   ├── Module: Savings
│   │   └── Module: Deposits
│   └── Component: Transactions
│       ├── Module: Transfers
│       ├── Module: Payments
│       └── Module: Standing Orders
└── Subsystem: Channels
    ├── Component: Mobile
    └── Component: Web
```

Each level can have its own `artifacts` and `codebase`. Deeper levels inherit context from parents.

### Example: 4-Level Hierarchy

System → Subsystem → Component → Module:

```json
{
  "version": "1.0",
  "project_root": "..",
  "kits": {
    "cypilot-sdlc": {
      "format": "Cypilot",
      "path": ".cypilot/kits/sdlc"
    }
  },
  "systems": [
    {
      "name": "Banking Platform",
      "slug": "banking",
      "kit": "cypilot-sdlc",
      "artifacts_dir": "architecture",
      "artifacts": [
        { "name": "Platform PRD", "path": "architecture/PRD.md", "kind": "PRD", "traceability": "DOCS-ONLY" },
        { "name": "Platform Design", "path": "architecture/DESIGN.md", "kind": "DESIGN", "traceability": "FULL" }
      ],
      "codebase": [
        { "name": "Source", "path": "src", "extensions": [".ts"] }
      ],
      "children": [
        {
          "name": "Core Banking",
          "slug": "core",
          "kit": "cypilot-sdlc",
          "artifacts_dir": "subsystems/core/architecture",
          "artifacts": [
            { "path": "subsystems/core/architecture/DESIGN.md", "kind": "DESIGN", "traceability": "FULL" }
          ],
          "codebase": [
            { "name": "Core Subsystem", "path": "src/core", "extensions": [".ts"] }
          ],
          "children": [
            {
              "name": "Accounts",
              "slug": "accounts",
              "kit": "cypilot-sdlc",
              "artifacts_dir": "subsystems/core/accounts/architecture",
              "artifacts": [
                { "path": "subsystems/core/accounts/architecture/DESIGN.md", "kind": "DESIGN", "traceability": "FULL" }
              ],
              "codebase": [
                { "name": "Accounts", "path": "src/core/accounts", "extensions": [".ts"] }
              ],
              "children": [
                {
                  "name": "Savings",
                  "slug": "savings",
                  "kit": "cypilot-sdlc",
                  "artifacts_dir": "subsystems/core/accounts/savings/architecture",
                  "artifacts": [
                    { "path": "subsystems/core/accounts/savings/architecture/features/interest-calc.md", "kind": "FEATURE", "traceability": "FULL" }
                  ],
                  "codebase": [
                    { "name": "Savings", "path": "src/core/accounts/savings", "extensions": [".ts"] }
                  ],
                  "children": []
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

**Key points:**
- System level: platform-wide PRD and DESIGN
- Subsystem level: subsystem DESIGN (references system DESIGN)
- Component level: component DESIGN + codebase scope
- Module level: FEATURE artifacts + narrowest codebase scope

---

### Example 1: Full Module Architecture

Each module has its own complete artifact set:

```json
{
  "version": "1.0",
  "project_root": "..",
  "kits": {
    "cypilot-sdlc": {
      "format": "Cypilot",
      "path": ".cypilot/kits/sdlc"
    }
  },
  "systems": [
    {
      "name": "SaaS Platform",
      "slug": "saas",
      "kit": "cypilot-sdlc",
      "artifacts_dir": "architecture",
      "artifacts": [
        { "name": "Product Requirements", "path": "architecture/PRD.md", "kind": "PRD", "traceability": "DOCS-ONLY" },
        { "name": "System Design", "path": "architecture/DESIGN.md", "kind": "DESIGN", "traceability": "FULL" },
        { "name": "Feature Breakdown", "path": "architecture/DECOMPOSITION.md", "kind": "DECOMPOSITION", "traceability": "FULL" },
        { "name": "Modular Architecture", "path": "architecture/ADR/0001-modular-monolith.md", "kind": "ADR", "traceability": "DOCS-ONLY" }
      ],
      "codebase": [
        { "name": "Source Code", "path": "src", "extensions": [".ts", ".tsx"] }
      ],
      "children": [
        {
          "name": "Auth",
          "slug": "auth",
          "kit": "cypilot-sdlc",
          "artifacts_dir": "modules/auth/architecture",
          "artifacts": [
            { "path": "modules/auth/architecture/PRD.md", "kind": "PRD", "traceability": "DOCS-ONLY" },
            { "path": "modules/auth/architecture/DESIGN.md", "kind": "DESIGN", "traceability": "FULL" },
            { "path": "modules/auth/architecture/features/login.md", "kind": "FEATURE", "traceability": "FULL" },
            { "path": "modules/auth/architecture/features/sessions.md", "kind": "FEATURE", "traceability": "FULL" }
          ],
          "codebase": [
            { "name": "Auth Module", "path": "src/modules/auth", "extensions": [".ts"] }
          ],
          "children": []
        },
        {
          "name": "Billing",
          "slug": "billing",
          "kit": "cypilot-sdlc",
          "artifacts_dir": "modules/billing/architecture",
          "artifacts": [
            { "path": "modules/billing/architecture/PRD.md", "kind": "PRD", "traceability": "DOCS-ONLY" },
            { "path": "modules/billing/architecture/DESIGN.md", "kind": "DESIGN", "traceability": "FULL" },
            { "path": "modules/billing/architecture/features/invoices.md", "kind": "FEATURE", "traceability": "FULL" }
          ],
          "codebase": [
            { "name": "Billing Module", "path": "src/modules/billing", "extensions": [".ts"] }
          ],
          "children": []
        }
      ]
    }
  ]
}
```

### Example 2: Feature-Only Modules

Modules have only FEATURE artifacts, sharing project-level DESIGN:

```json
{
  "version": "1.0",
  "project_root": "..",
  "kits": {
    "cypilot-sdlc": {
      "format": "Cypilot",
      "path": ".cypilot/kits/sdlc"
    }
  },
  "systems": [
    {
      "name": "SaaS Platform",
      "slug": "saas",
      "kit": "cypilot-sdlc",
      "artifacts_dir": "architecture",
      "artifacts": [
        { "name": "Product Requirements", "path": "architecture/PRD.md", "kind": "PRD", "traceability": "DOCS-ONLY" },
        { "name": "System Design", "path": "architecture/DESIGN.md", "kind": "DESIGN", "traceability": "FULL" },
        { "name": "Feature Breakdown", "path": "architecture/DECOMPOSITION.md", "kind": "DECOMPOSITION", "traceability": "FULL" }
      ],
      "codebase": [
        { "name": "Source Code", "path": "src", "extensions": [".ts", ".tsx"] }
      ],
      "children": [
        {
          "name": "Auth",
          "slug": "auth",
          "kit": "cypilot-sdlc",
          "artifacts_dir": "modules/auth/architecture",
          "artifacts": [
            { "path": "modules/auth/architecture/features/login.md", "kind": "FEATURE", "traceability": "FULL" },
            { "path": "modules/auth/architecture/features/sessions.md", "kind": "FEATURE", "traceability": "FULL" }
          ],
          "codebase": [
            { "name": "Auth Module", "path": "src/modules/auth", "extensions": [".ts"] }
          ],
          "children": []
        },
        {
          "name": "Billing",
          "slug": "billing",
          "kit": "cypilot-sdlc",
          "artifacts_dir": "modules/billing/architecture",
          "artifacts": [
            { "path": "modules/billing/architecture/features/invoices.md", "kind": "FEATURE", "traceability": "FULL" }
          ],
          "codebase": [
            { "name": "Billing Module", "path": "src/modules/billing", "extensions": [".ts"] }
          ],
          "children": []
        }
      ]
    }
  ]
}
```

### Example 3: Code-Only Modules

Modules declared for codebase scoping only, no module-level artifacts:

```json
{
  "version": "1.0",
  "project_root": "..",
  "kits": {
    "cypilot-sdlc": {
      "format": "Cypilot",
      "path": ".cypilot/kits/sdlc"
    }
  },
  "systems": [
    {
      "name": "SaaS Platform",
      "slug": "saas",
      "kit": "cypilot-sdlc",
      "artifacts_dir": "architecture",
      "artifacts": [
        { "name": "Product Requirements", "path": "architecture/PRD.md", "kind": "PRD", "traceability": "DOCS-ONLY" },
        { "name": "System Design", "path": "architecture/DESIGN.md", "kind": "DESIGN", "traceability": "FULL" },
        { "name": "Feature Breakdown", "path": "architecture/DECOMPOSITION.md", "kind": "DECOMPOSITION", "traceability": "FULL" }
      ],
      "codebase": [
        { "name": "Source Code", "path": "src", "extensions": [".ts", ".tsx"] }
      ],
      "children": [
        {
          "name": "Auth",
          "slug": "auth",
          "kit": "cypilot-sdlc",
          "codebase": [
            { "name": "Auth Module", "path": "src/modules/auth", "extensions": [".ts"] }
          ],
          "children": []
        },
        {
          "name": "Billing",
          "slug": "billing",
          "kit": "cypilot-sdlc",
          "codebase": [
            { "name": "Billing Module", "path": "src/modules/billing", "extensions": [".ts"] }
          ],
          "children": []
        }
      ]
    }
  ]
}
```

### Directory Structure

The registry maps to this file structure:

```text
project-root/
├── .cypilot-adapter/
│   └── artifacts.toml
├── architecture/
│   ├── PRD.md
│   ├── DESIGN.md
│   ├── DECOMPOSITION.md
│   └── ADR/
│       └── 0001-modular-monolith.md
├── modules/
│   ├── auth/
│   │   └── architecture/
│   │       ├── PRD.md
│   │       ├── DESIGN.md
│   │       └── features/
│   │           ├── login.md
│   │           └── sessions.md
│   └── billing/
│       └── architecture/
│           ├── PRD.md
│           ├── DESIGN.md
│           └── features/
│               └── invoices.md
└── src/
    └── ...
```

---

## Component DESIGN from Project DESIGN

When creating a component DESIGN, use the project (or parent) DESIGN as input for consistency.

### Flow

```
1. cypilot make DESIGN for component auth from project DESIGN
   → Reads project DESIGN
   → Extracts auth-related elements
   → Creates component DESIGN with references to project DESIGN

2. cypilot validate DESIGN for component auth refs
   → Validates references to project DESIGN components
   → Ensures component doesn't contradict project architecture
```

### Prompts

| Prompt | What happens |
|--------|--------------|
| `cypilot make DESIGN for component auth from project DESIGN` | Creates component DESIGN using project architecture |
| `cypilot make DESIGN for component auth inheriting from project` | Same, alternative phrasing |
| `cypilot sync DESIGN for component auth with project` | Updates component DESIGN to match project changes |
| `cypilot compare DESIGN for component auth to project` | Shows differences from project DESIGN |

### Example with Context

```
cypilot make DESIGN for component auth from project DESIGN
Context:
- Component: auth
- Project DESIGN: architecture/DESIGN.md
- Component code path: src/core/auth/
- Extract elements: AuthService, SessionManager, TokenValidator
- Component owns tables: users, sessions, refresh_tokens
- Public interface: login(), logout(), refresh(), validateToken()
```

The agent will:
1. Read project DESIGN
2. Extract auth-related elements and their interfaces
3. Create component DESIGN that references project elements by ID
4. Add component-specific details (internal structure, data ownership)

---

## Traceability Between Levels

### ID Conventions

IDs are built by concatenating **slugs** through the hierarchy chain, followed by the element kind and element slug.

**Pattern:** `cpt-{system}-{subsystem}-{component}-{kind}-{slug}`

The tool validates IDs against the known hierarchy, so IDs must match registered slugs exactly.

| Hierarchy Level | ID Pattern | Example |
|-----------------|------------|---------|
| System PRD | `cpt-{system}-fr-{slug}` | `cpt-saas-fr-user-management` |
| System DESIGN | `cpt-{system}-component-{slug}` | `cpt-saas-component-auth-service` |
| Subsystem DESIGN | `cpt-{system}-{subsystem}-component-{slug}` | `cpt-banking-core-component-account-service` |
| Component PRD | `cpt-{system}-{subsystem}-{component}-fr-{slug}` | `cpt-banking-core-accounts-fr-balance-query` |
| Component DESIGN | `cpt-{system}-{subsystem}-{component}-component-{slug}` | `cpt-banking-core-accounts-component-ledger` |
| Module FEATURE | `cpt-{system}-{subsystem}-{component}-{module}-flow-{slug}` | `cpt-banking-core-accounts-savings-flow-interest-calc` |

**Slug rules:**
- Lowercase letters, numbers, and hyphens only
- No spaces, no leading/trailing hyphens
- Defined in `slug` field of each system node
- Example: `"name": "Core Banking"` → `"slug": "core"`

### Cross-Level References

Child artifacts reference parent artifacts using full hierarchical IDs:

**In component DESIGN (banking-core-accounts):**
```markdown
## Traceability

### Project References
- Implements: `cpt-banking-component-core-banking` (from system DESIGN)
- Implements: `cpt-banking-core-component-account-service` (from subsystem DESIGN)
- Satisfies: `cpt-banking-fr-account-management`, `cpt-banking-fr-balance-query` (from system PRD)
- Follows: `cpt-banking-adr-component-boundaries` (component boundary rules)
```

**In module FEATURE (banking-core-accounts-savings):**
```markdown
## Traceability

### Component References
- Component: `cpt-banking-core-accounts-component-ledger`
- Requirement: `cpt-banking-core-accounts-fr-balance-query`

### System References
- System component: `cpt-banking-component-core-banking`
- System requirement: `cpt-banking-fr-account-management`
```

### Traceability Queries

| Prompt | What happens |
|--------|--------------|
| `cypilot trace cpt-saas-fr-user-management` | Shows: PRD → DESIGN → component DESIGN → FEATURE → CODE |
| `cypilot trace cpt-saas-component-auth-service` | Shows system component and all child implementations |
| `cypilot trace cpt-saas-auth-login-flow-token-validation` | Shows full path from system PRD to component code |
| `cypilot find refs to cpt-saas-component-auth-service` | Lists all child artifacts referencing this component |
| `cypilot validate refs for component auth` | Validates all cross-level references in component |
| `cypilot show orphans across levels` | Finds broken references between project and children |

### Validation Across Levels

| Prompt | What happens |
|--------|--------------|
| `cypilot validate all` | Validates project + all children |
| `cypilot validate all refs` | Validates all cross-references at all levels |
| `cypilot validate component auth against project` | Checks component compatibility with project |
| `cypilot compare component auth to project DESIGN` | Shows component drift from project architecture |

---

## How to Provide Context

In a modular monolith, the most important context is:
- Scope: system, subsystem, component, or module
- Target name (component/module name if applicable)
- Boundaries and dependencies
- Code paths

**Example format:**
```
cypilot make DESIGN
Context:
- Scope: system
- Architecture style: modular monolith
- Components: auth, billing, notifications
- Dependency rules: billing -> auth, notifications -> auth
```

---

## Project-Level Workflow

Describe the full system and cross-module rules.

### 1. PRD (Project)

**Create**

| Prompt | What happens |
|--------|--------------|
| `cypilot make PRD` | Creates project PRD interactively |
| `cypilot make PRD for SaaS platform` | Creates PRD with context |

**Update**

| Prompt | What happens |
|--------|--------------|
| `cypilot update PRD` | Updates project PRD |
| `cypilot extend PRD with multi-tenant support` | Adds capability |

**Provide context:** product vision, component list, architecture style.

**Example:**
```
cypilot make PRD
Context:
- Product: SaaS platform
- Architecture style: modular monolith
- Core components: auth, billing, notifications
```

### 2. Validate PRD (Project)

| Prompt | What happens |
|--------|--------------|
| `cypilot validate PRD` | Full validation (300+ criteria) |
| `cypilot validate PRD semantic` | Semantic only |
| `cypilot validate PRD structural` | Structural only |

### 3. ADR + DESIGN (Project)

**Create DESIGN**

| Prompt | What happens |
|--------|--------------|
| `cypilot make DESIGN` | Creates project DESIGN interactively |
| `cypilot make DESIGN from PRD` | Transforms PRD into architecture |

**Update DESIGN**

| Prompt | What happens |
|--------|--------------|
| `cypilot update DESIGN` | Updates project DESIGN |
| `cypilot extend DESIGN with component notifications` | Adds component |
| `cypilot update DESIGN dependency rules` | Updates component dependencies |

**ADR**

| Prompt | What happens |
|--------|--------------|
| `cypilot make ADR for component boundaries` | Creates ADR for architecture decision |
| `cypilot make ADR for cross-component communication` | Creates ADR comparing approaches |
| `cypilot update ADR 0001` | Updates specific ADR |

**Provide context:** component list, dependency rules, integration approach.

**Example:**
```
cypilot make DESIGN
Context:
- Scope: system
- Architecture style: modular monolith
- Components:
  - auth (subsystems/core/auth/)
  - billing (subsystems/core/billing/)
- Dependency rules: billing -> auth
- Integration: shared DB, tables owned by components
```

### 4. Validate DESIGN + ADR (Project)

| Prompt | What happens |
|--------|--------------|
| `cypilot validate DESIGN` | Full validation (380+ criteria) |
| `cypilot validate DESIGN semantic` | Semantic only |
| `cypilot validate DESIGN refs` | Cross-references |
| `cypilot validate ADR` | Validates all ADRs |
| `cypilot validate ADR 0001` | Validates specific ADR |

### 5. DECOMPOSITION (Project)

**Create**

| Prompt | What happens |
|--------|--------------|
| `cypilot decompose` | Creates project decomposition |
| `cypilot decompose by capability` | Groups by business capability |

**Update**

| Prompt | What happens |
|--------|--------------|
| `cypilot add feature {slug}` | Adds project feature |
| `cypilot update feature {slug} status` | Updates status |

**Provide context:** system-level features (NOT components).

**Example:**
```
cypilot decompose
Context:
- Scope: system
- System features: pricing-plans, invoice-lifecycle, tenant-management
- Note: components are NOT features
```

### 6. Validate DECOMPOSITION (Project)

| Prompt | What happens |
|--------|--------------|
| `cypilot validate DECOMPOSITION` | Full validation |
| `cypilot validate DECOMPOSITION semantic` | Semantic only |
| `cypilot validate DECOMPOSITION refs` | Cross-references |

---

## Component-Level Workflow

Use when you want a component (or module in 4-level hierarchies) to have its own architecture.

> **Note**: Use `for component {name}` in prompts. For 4-level hierarchies, use `for module {name}` to target the deepest level.

### 7. PRD (Component)

**Create**

| Prompt | What happens |
|--------|--------------|
| `cypilot make PRD for component auth` | Creates component PRD |
| `cypilot make PRD` with component context | Creates interactively |

**Update**

| Prompt | What happens |
|--------|--------------|
| `cypilot update PRD for component auth` | Updates component PRD |
| `cypilot extend PRD for component auth with MFA` | Adds capability |

**Provide context:** scope, component name, component paths.

**Example:**
```
cypilot make PRD for component auth
Context:
- Scope: component
- Component: auth
- Component code path: src/core/auth/
- Component architecture: subsystems/core/auth/architecture/
```

### 8. DESIGN (Component)

**Create**

| Prompt | What happens |
|--------|--------------|
| `cypilot make DESIGN for component auth` | Creates component DESIGN |
| `cypilot reverse DESIGN for component auth` | Reverse-engineers from code |

**Update**

| Prompt | What happens |
|--------|--------------|
| `cypilot update DESIGN for component auth` | Updates component DESIGN |
| `cypilot extend DESIGN for component auth with sessions` | Adds internal component |
| `cypilot sync DESIGN for component auth from code` | Syncs with code |

**Provide context:** component dependencies, public interface, data ownership.

**Example:**
```
cypilot make DESIGN for component auth
Context:
- Scope: component
- Component: auth
- Component code path: src/core/auth/
- Dependencies: none
- Public interface: AuthService (login, logout, refresh)
- Data ownership: users, sessions tables
```

### 9. DECOMPOSITION (Component)

**Create**

| Prompt | What happens |
|--------|--------------|
| `cypilot decompose component auth` | Creates component decomposition |
| `cypilot decompose component auth from code` | From existing code |

**Update**

| Prompt | What happens |
|--------|--------------|
| `cypilot add feature {slug} to component auth` | Adds component feature |
| `cypilot update feature {slug} in component auth` | Updates feature |

**Example:**
```
cypilot decompose component auth
Context:
- Scope: component
- Component: auth
- Component features: login, sessions, mfa
```

### 10. FEATURE (Component)

**Create**

| Prompt | What happens |
|--------|--------------|
| `cypilot make FEATURE sessions for component auth` | Creates component feature |
| `cypilot reverse FEATURE sessions for component auth` | From existing code |

**Update**

| Prompt | What happens |
|--------|--------------|
| `cypilot update FEATURE sessions for component auth` | Updates feature |
| `cypilot extend FEATURE sessions with token refresh` | Adds scenario |
| `cypilot sync FEATURE sessions from code` | Syncs with code |

**Provide context:** component, feature slug, scenarios, data ownership.

**Example:**
```
cypilot make FEATURE sessions for component auth
Context:
- Scope: component
- Component: auth
- Feature: sessions
- Include scenarios: login, logout, token refresh, session expiry
- Data ownership: sessions table
```

### 11. Validate FEATURE (Component)

| Prompt | What happens |
|--------|--------------|
| `cypilot validate FEATURE sessions for component auth` | Full validation |
| `cypilot validate FEATURE sessions for component auth semantic` | Semantic only |
| `cypilot validate FEATURE sessions for component auth refs` | Cross-references |

### 12. CODE (Component)

**Implement**

| Prompt | What happens |
|--------|--------------|
| `cypilot implement sessions for component auth` | Generates code |
| `cypilot implement sessions for component auth step by step` | With confirmation |
| `cypilot implement sessions for component auth tests first` | Tests first |

**Implement specific parts**

| Prompt | What happens |
|--------|--------------|
| `cypilot implement sessions for component auth flow token-refresh` | Specific flow |
| `cypilot implement sessions for component auth api` | API layer only |
| `cypilot implement sessions for component auth tests` | Tests only |

**Continue / update**

| Prompt | What happens |
|--------|--------------|
| `cypilot continue implementing sessions for component auth` | Continue partial |
| `cypilot implement sessions for component auth remaining` | Unimplemented only |
| `cypilot sync code with FEATURE sessions for component auth` | Sync with feature |

**Add markers**

| Prompt | What happens |
|--------|--------------|
| `cypilot add markers for sessions in component auth` | Adds markers to existing code |
| `cypilot fix markers in src/core/auth/` | Fixes incorrect markers |

**Example:**
```
cypilot implement sessions for component auth
Context:
- Component code path: src/core/auth/
- Component architecture: subsystems/core/auth/architecture/
```

### 13. Validate Code (Component)

**Full validation**

| Prompt | What happens |
|--------|--------------|
| `cypilot validate code for component auth` | All component code |
| `cypilot validate code for sessions in component auth` | Specific feature |
| `cypilot validate code in src/core/auth/` | Specific path |

**Coverage**

| Prompt | What happens |
|--------|--------------|
| `cypilot validate code coverage for component auth` | Component coverage |
| `cypilot validate code coverage for sessions in component auth` | Feature coverage |
| `cypilot show uncovered for component auth` | Lists unimplemented |

**Traceability**

| Prompt | What happens |
|--------|--------------|
| `cypilot validate code orphans for component auth` | Orphaned markers |
| `cypilot validate code refs for component auth` | Marker references |
| `cypilot list code markers for component auth` | Lists component markers |

**Consistency**

| Prompt | What happens |
|--------|--------------|
| `cypilot compare code to FEATURE sessions for component auth` | Shows drift |
| `cypilot validate code consistency for component auth` | Checks code matches features |

---

## Quick Reference

### Project Level

| Step | Generate | Validate |
|------|----------|----------|
| 1 | `cypilot make PRD` | `cypilot validate PRD` |
| 2 | `cypilot make DESIGN` | `cypilot validate DESIGN` |
| 3 | `cypilot make ADR for ...` | `cypilot validate ADR` |
| 4 | `cypilot decompose` | `cypilot validate DECOMPOSITION` |

### Component Level

| Step | Generate | Validate |
|------|----------|----------|
| 1 | `cypilot make PRD for component {name}` | `cypilot validate PRD for component {name}` |
| 2 | `cypilot make DESIGN for component {name}` | `cypilot validate DESIGN for component {name}` |
| 3 | `cypilot decompose component {name}` | `cypilot validate DECOMPOSITION for component {name}` |
| 4 | `cypilot make FEATURE {slug} for component {name}` | `cypilot validate FEATURE {slug} for component {name}` |
| 5 | `cypilot implement {slug} for component {name}` | `cypilot validate code for {slug} in component {name}` |

> For 4-level hierarchies, use `module` instead of `component` to target the deepest level.

**Validation modes** (append to any `validate` command):
- `semantic` — content quality, completeness, clarity
- `structural` — format, IDs, template compliance
- `refs` — cross-references to other artifacts
- `quick` — critical issues only (fast)

---

## Adapter Configuration

Example adapter AGENTS.md for a modular monolith:

```markdown
# Project Cypilot Adapter

WHEN working in this repo:
- This is a modular monolith with hierarchy: System → Subsystem → Component
- Each component MUST have its architecture co-located with component code.
- Component architecture path convention:
  - `subsystems/{subsystem}/{component}/architecture/PRD.md`
  - `subsystems/{subsystem}/{component}/architecture/DESIGN.md`
  - `subsystems/{subsystem}/{component}/architecture/ADR/**`
  - `subsystems/{subsystem}/{component}/architecture/DECOMPOSITION.md`
  - `subsystems/{subsystem}/{component}/architecture/features/{slug}.md`
- Component boundaries are enforced by code structure and dependency rules.

WHEN asked to generate/validate artifacts:
- Ask whether the scope is system-level or component-level.
- If component-level: ask which component is in scope.
```

---

## Iteration Rules

- System-level artifacts describe the full system and cross-component rules
- Component-level artifacts describe one component in isolation
- Component artifacts must stay compatible with system architecture
- If component code changes, update component FEATURE first, then validate
- Cross-component changes may require updating system DESIGN
