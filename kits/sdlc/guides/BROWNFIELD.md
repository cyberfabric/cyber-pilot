# Brownfield Guide

Use this guide when you already have a codebase and want to adopt Cypilot.

All prompts work through the `cypilot` skill — enable it with `cypilot on` and use natural language prompts.

## Goal

Adopt Cypilot incrementally — start with what makes sense for your project, not a fixed sequence.

## Key Principle: Start Anywhere

Unlike greenfield projects, **brownfield has no required order**. You can:

- Start with **any artifact** — PRD, DESIGN, FEATURE, or even just CODE
- Work **top-down** (PRD → DESIGN → CODE) or **bottom-up** (CODE → FEATURE → DESIGN)
- Adopt **incrementally** — use only what you need, add more later
- Use **code-only mode** — just Cypilot's code generation with checklist benefits

**Even with zero artifacts**, Cypilot's code generation uses the `code-checklist` internally for quality guidance.

---

## Adoption Scenarios

### Scenario A: Code-Only

You just want better code generation. No artifacts needed.

| Prompt | What happens |
|--------|--------------|
| `cypilot implement feature auth` | Generates code using code-checklist quality guidance |
| `cypilot add markers to src/auth/` | Adds traceability markers to existing code |
| `cypilot validate code` | Validates code quality and marker correctness |

**Benefits**: Quality-guided code generation, consistent patterns, code traceability.

### Scenario B: Feature-First (Bottom-Up)

You want to document existing features, then build up.

```
1. cypilot reverse FEATURE from src/auth/     → Creates FEATURE from code
2. cypilot reverse FEATURE from src/billing/  → Creates another FEATURE from code
3. cypilot decompose from features            → Creates DECOMPOSITION from FEATUREs
4. cypilot make DESIGN from DECOMPOSITION     → Creates DESIGN from structure
5. cypilot make PRD from DESIGN               → (optional) Creates PRD from DESIGN
```

**When to use**: You want to document what exists without changing code.

### Scenario C: Design-First (Middle-Out)

You want to capture architecture, then decompose into features.

```
1. cypilot reverse DESIGN from codebase       → Extracts architecture from code
2. cypilot decompose                          → Creates feature breakdown
3. cypilot make FEATURE for {slug}            → Creates detailed features
4. cypilot implement {slug}                   → Implements with traceability markers
```

**When to use**: You want architectural control before feature work.


### Scenario D: Full Top-Down

You want complete documentation from requirements to code.

```
1. cypilot reverse PRD from codebase          → Extracts requirements
2. cypilot make DESIGN from PRD               → Creates architecture
3. cypilot decompose                          → Creates feature breakdown
4. cypilot make FEATURE for {slug}            → Creates detailed features
5. cypilot implement {slug}                   → Implements with traceability markers
```

**When to use**: New team members, compliance requirements, or major refactoring.

### Scenario E: Gradual Adoption

Start minimal, add artifacts as needed.

```
Week 1: cypilot implement {slug}              → Code-only, with checklist
Week 2: cypilot make FEATURE for {slug}       → Add features for complex work
Week 3: cypilot decompose                     → Organize features
Later:  cypilot make DESIGN                   → Document architecture
```

**When to use**: You want low-friction adoption with growing benefits.

---

## What You Will Produce

Cypilot artifacts registered in `.cypilot-adapter/artifacts.toml` ([taxonomy](TAXONOMY.md)):

| Artifact | Default Location |
|----------|------------------|
| PRD | `architecture/PRD.md` |
| ADR | `architecture/ADR/*.md` |
| DESIGN | `architecture/DESIGN.md` |
| DECOMPOSITION | `architecture/DECOMPOSITION.md` |
| FEATURE | `architecture/features/{slug}.md` |

## How to Provide Context

Brownfield work is context-heavy. Add context to control what the agent reads and how it maps existing reality into Cypilot artifacts.

Recommended context:
- Source of truth (code vs docs)
- Existing code entry points (directories, modules)
- Existing docs you trust (paths)
- Constraints and invariants you must preserve

**Example format:**
```
cypilot make DESIGN
Context:
- Source of truth: code
- Code areas: src/api/, src/domain/
- Existing docs: docs/architecture.md (may be outdated)
- Constraints: do not break public API
```

The agent will read inputs, ask targeted questions, propose answers, and produce artifacts.

---

## Workflow: Create Baseline

Goal: produce validated baseline artifacts before you add or refactor features.

### 1. PRD

**Reverse-engineer from code**

| Prompt | What happens |
|--------|--------------|
| `cypilot reverse PRD from codebase` | Extracts requirements from existing code |
| `cypilot reverse PRD from src/` | Extracts from specific directory |
| `cypilot make PRD from code` | Same, alternative phrasing |

**Create from existing docs**

| Prompt | What happens |
|--------|--------------|
| `cypilot make PRD from README` | Creates PRD from project README |
| `cypilot make PRD from docs/requirements.txt` | Extracts from existing requirements |
| `cypilot make PRD from this conversation` | Creates PRD from stakeholder discussion |
| `cypilot import user-stories.md as PRD` | Converts user stories to PRD |

**Update**

| Prompt | What happens |
|--------|--------------|
| `cypilot update PRD` | Updates PRD interactively |
| `cypilot extend PRD with {capability}` | Adds capability to existing PRD |
| `cypilot sync PRD from code` | Updates PRD to match current code |

**Provide context:** source of truth, code entry points, existing docs.

**Example:**
```
cypilot reverse PRD from codebase
Context:
- Source of truth: code
- Code entry points: src/routes/, src/controllers/
- Existing docs: docs/api.md (partial)
```

### 2. Validate PRD

| Prompt | What happens |
|--------|--------------|
| `cypilot validate PRD` | Full validation (300+ criteria) |
| `cypilot validate PRD semantic` | Semantic only (content quality) |
| `cypilot validate PRD structural` | Structural only (format, IDs) |
| `cypilot validate PRD quick` | Fast check (critical issues) |

### 3. ADR + DESIGN

**Reverse-engineer DESIGN**

| Prompt | What happens |
|--------|--------------|
| `cypilot reverse DESIGN from codebase` | Documents current architecture from code |
| `cypilot reverse DESIGN from src/` | From specific directory |
| `cypilot make DESIGN from code` | Same, alternative phrasing |

**Create from existing docs**

| Prompt | What happens |
|--------|--------------|
| `cypilot make DESIGN from PRD` | Transforms PRD into architecture |
| `cypilot import OpenAPI as DESIGN` | Converts API spec into DESIGN |
| `cypilot import db-schema.sql as DESIGN data model` | Extracts data model from SQL |

**Update**

| Prompt | What happens |
|--------|--------------|
| `cypilot update DESIGN` | Updates DESIGN interactively |
| `cypilot extend DESIGN with {component}` | Adds component to DESIGN |
| `cypilot sync DESIGN from code` | Updates DESIGN to match current code |

**ADR**

| Prompt | What happens |
|--------|--------------|
| `cypilot make ADR for PostgreSQL` | Creates ADR for technology choice |
| `cypilot make ADR for REST vs GraphQL` | Creates ADR comparing approaches |
| `cypilot draft ADR from discussion` | Extracts decision from conversation |
| `cypilot update ADR 0001` | Updates specific ADR |

**Provide context:** source of truth, existing features, constraints.

**Example:**
```
cypilot reverse DESIGN from codebase
Context:
- Source of truth: code
- Existing features: docs/openapi.yaml, docs/db-schema.md
- Constraints: do not break public API
```

### 4. Validate DESIGN + ADR

| Prompt | What happens |
|--------|--------------|
| `cypilot validate DESIGN` | Full validation (380+ criteria) |
| `cypilot validate DESIGN semantic` | Semantic only (consistency) |
| `cypilot validate DESIGN structural` | Structural only (format) |
| `cypilot validate DESIGN refs` | Cross-references to PRD |
| `cypilot validate ADR` | Validates all ADRs |
| `cypilot validate ADR 0001` | Validates specific ADR |
| `cypilot validate ADR semantic` | Semantic only (rationale quality) |

### 5. DECOMPOSITION

**Create**

| Prompt | What happens |
|--------|--------------|
| `cypilot decompose` | Creates DECOMPOSITION interactively |
| `cypilot decompose from codebase` | Extracts features from existing code structure |
| `cypilot decompose by module` | Groups by code modules |
| `cypilot decompose by capability` | Groups by business capability |

**Update**

| Prompt | What happens |
|--------|--------------|
| `cypilot add feature {slug}` | Adds new feature entry |
| `cypilot update feature {slug} status` | Updates feature status |
| `cypilot update feature {slug} priority` | Updates feature priority |

**Provide context:** module boundaries, feature grouping preferences.

**Example:**
```
cypilot decompose from codebase
Context:
- Group features by modules: billing, auth, reporting
- Code structure: src/modules/
```

### 6. Validate DECOMPOSITION

| Prompt | What happens |
|--------|--------------|
| `cypilot validate DECOMPOSITION` | Full validation (130+ criteria) |
| `cypilot validate DECOMPOSITION semantic` | Semantic only (coverage) |
| `cypilot validate DECOMPOSITION structural` | Structural only (format) |
| `cypilot validate DECOMPOSITION refs` | Cross-references to DESIGN |

---

## Workflow: Add a New Feature

Use when baseline exists and you want to add a new capability.

### 1. Add to DECOMPOSITION

| Prompt | What happens |
|--------|--------------|
| `cypilot add feature {slug}` | Adds new feature to decomposition |
| `cypilot add feature notifications` | Example: adds notifications feature |

### 2. FEATURE

**Create**

| Prompt | What happens |
|--------|--------------|
| `cypilot make FEATURE for {slug}` | Creates FEATURE |
| `cypilot make FEATURE for notifications` | Creates detailed feature design |

**Reverse-engineer from existing code**

| Prompt | What happens |
|--------|--------------|
| `cypilot reverse FEATURE from src/notifications/` | Creates FEATURE from existing code |
| `cypilot reverse FEATURE {slug} from code` | Same, using feature slug |
| `cypilot draft FEATURE from code` | Same, alternative phrasing |

**Update**

| Prompt | What happens |
|--------|--------------|
| `cypilot update FEATURE {slug}` | Updates FEATURE |
| `cypilot extend FEATURE {slug} with {scenario}` | Adds scenario to FEATURE |
| `cypilot sync FEATURE {slug} from code` | Updates FEATURE to match code |

**Provide context:** feature slug, code boundaries, scenarios to include.

**Example:**
```
cypilot make FEATURE for notifications
Context:
- Include scenarios: retries, rate limits, provider outage
- Code boundaries: src/notifications/
```

### 3. Validate FEATURE

| Prompt | What happens |
|--------|--------------|
| `cypilot validate FEATURE {slug}` | Full validation (380+ criteria) |
| `cypilot validate FEATURE {slug} semantic` | Semantic only (flows, edge cases) |
| `cypilot validate FEATURE {slug} structural` | Structural only (CDSL, IDs) |
| `cypilot validate FEATURE {slug} refs` | Cross-references to DESIGN |

### 4. CODE

**Implement from scratch**

| Prompt | What happens |
|--------|--------------|
| `cypilot implement {slug}` | Generates code from FEATURE |
| `cypilot implement {slug} step by step` | Implements with user confirmation |
| `cypilot implement {slug} tests first` | Generates tests first, then code |

**Implement specific parts**

| Prompt | What happens |
|--------|--------------|
| `cypilot implement {slug} flow {flow-id}` | Implements specific flow only |
| `cypilot implement {slug} api` | Implements API layer only |
| `cypilot implement {slug} data layer` | Implements data/repository layer only |
| `cypilot implement {slug} tests` | Generates tests only |

**Continue / update**

| Prompt | What happens |
|--------|--------------|
| `cypilot continue implementing {slug}` | Continues partial implementation |
| `cypilot implement {slug} remaining` | Implements only unimplemented parts |
| `cypilot sync code with FEATURE {slug}` | Updates code to match FEATURE changes |

**Add markers to existing code**

| Prompt | What happens |
|--------|--------------|
| `cypilot add markers to {path}` | Adds `@cpt-*` markers to existing code |
| `cypilot add markers for {slug}` | Adds markers matching FEATURE |
| `cypilot fix markers in {path}` | Fixes incorrect/incomplete markers |

**Provide context:** feature slug, code paths.

**Example:**
```
cypilot implement notifications
Context:
- Where to implement: src/notifications/
```

### 5. Validate Code

**Full validation**

| Prompt | What happens |
|--------|--------------|
| `cypilot validate code` | Validates all code markers |
| `cypilot validate code for {slug}` | Validates specific feature |
| `cypilot validate code in {path}` | Validates code in specific path |

**Coverage**

| Prompt | What happens |
|--------|--------------|
| `cypilot validate code coverage` | Reports implementation coverage % |
| `cypilot validate code coverage for {slug}` | Coverage for specific feature |
| `cypilot show uncovered flows` | Lists flows without implementation |
| `cypilot show uncovered algorithms` | Lists algorithms without implementation |

**Traceability**

| Prompt | What happens |
|--------|--------------|
| `cypilot validate code orphans` | Finds markers referencing non-existent IDs |
| `cypilot validate code refs` | Validates all marker references |
| `cypilot validate code markers` | Checks marker format correctness |
| `cypilot list code markers` | Lists all markers in codebase |
| `cypilot list code markers for {slug}` | Lists markers for specific feature |

**Consistency**

| Prompt | What happens |
|--------|--------------|
| `cypilot compare code to FEATURE {slug}` | Shows drift between code and feature |
| `cypilot validate code consistency` | Checks code matches FEATURE |
| `cypilot find missing implementations` | Lists FEATURE elements without code |

---

## Sync and Compare

When code and design drift apart:

| Prompt | What happens |
|--------|--------------|
| `cypilot compare DESIGN to code` | Shows drift between design and implementation |
| `cypilot compare FEATURE {slug} to code` | Shows drift for specific feature |
| `cypilot sync DESIGN from code` | Updates DESIGN to match current code |
| `cypilot sync FEATURE {slug} from code` | Updates FEATURE to match current code |
| `cypilot sync code with FEATURE {slug}` | Updates code to match FEATURE |
| `cypilot diff FEATURE {slug}` | Shows changes since last validation |

---

## Common Scenarios

### Requirements Changed

```
cypilot update PRD
cypilot validate PRD
cypilot propagate PRD changes to DESIGN
cypilot validate DESIGN
```

### Design Changed

```
cypilot update DESIGN
cypilot validate DESIGN
cypilot propagate DESIGN changes to FEATURE {slug}
cypilot validate FEATURE {slug}
```

### Feature Design Changed

```
cypilot update FEATURE {slug}
cypilot validate FEATURE {slug}
cypilot sync code with FEATURE {slug}
cypilot validate code for {slug}
```

### Code Changed Without Design Update

```
cypilot compare FEATURE {slug} to code
cypilot sync FEATURE {slug} from code
cypilot validate FEATURE {slug}
```

---

## Quick Reference

### By Adoption Level

| Level | What you do | Benefits |
|-------|-------------|----------|
| **Code-only** | `cypilot implement {slug}` | Code checklist, consistent patterns |
| **+ FEATURE** | Add `cypilot make FEATURE` | Flows, algorithms, edge cases documented |
| **+ DECOMPOSITION** | Add `cypilot decompose` | Feature organization, dependencies |
| **+ DESIGN** | Add `cypilot make DESIGN` | Architecture, components, data model |
| **+ PRD** | Add `cypilot make PRD` | Requirements, actors, full traceability |

### Top-Down (Full)

| Step | Generate | Validate |
|------|----------|----------|
| 1 | `cypilot reverse PRD from codebase` | `cypilot validate PRD` |
| 2 | `cypilot reverse DESIGN from codebase` | `cypilot validate DESIGN` |
| 3 | `cypilot decompose` | `cypilot validate DECOMPOSITION` |
| 4 | `cypilot make FEATURE for {slug}` | `cypilot validate FEATURE {slug}` |
| 5 | `cypilot implement {slug}` | `cypilot validate code for {slug}` |

### Bottom-Up (Feature-First)

| Step | Generate | Validate |
|------|----------|----------|
| 1 | `cypilot reverse FEATURE from src/{path}/` | `cypilot validate FEATURE {slug}` |
| 2 | `cypilot decompose from features` | `cypilot validate DECOMPOSITION` |
| 3 | `cypilot make DESIGN from DECOMPOSITION` | `cypilot validate DESIGN` |

### Code-Only

| Prompt | What happens |
|--------|--------------|
| `cypilot implement {slug}` | Generates code with checklist guidance |
| `cypilot add markers to {path}` | Adds traceability to existing code |
| `cypilot validate code` | Validates code quality |

**Validation modes** (append to any `validate` command):
- `semantic` — content quality, completeness, clarity
- `structural` — format, IDs, template compliance
- `refs` — cross-references to other artifacts
- `quick` — critical issues only (fast)

## Iteration Rules

- Start with what you need — add more artifacts as value becomes clear
- If code changes affect feature behavior, update FEATURE first
- Re-validate the FEATURE design
- Run `cypilot validate code` to ensure design and code remain consistent
- If code contradicts design, decide: update design OR update code
