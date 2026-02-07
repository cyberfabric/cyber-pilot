# Brownfield Guide

Use this guide when you already have a codebase and want to adopt Cypilot.

All prompts work through the `cypilot` skill — enable it with `cypilot on` and use natural language prompts.

## Goal

Adopt Cypilot incrementally — start with what makes sense for your project, not a fixed sequence.

## Key Principle: Start Anywhere

Unlike greenfield projects, **brownfield has no required order**. You can:

- Start with **any artifact** — PRD, DESIGN, SPEC, or even just CODE
- Work **top-down** (PRD → DESIGN → CODE) or **bottom-up** (CODE → SPEC → DESIGN)
- Adopt **incrementally** — use only what you need, add more later
- Use **code-only mode** — just Cypilot's code generation with checklist benefits

**Even with zero artifacts**, Cypilot's code generation uses the `code-checklist` internally for quality guidance.

---

## Adoption Scenarios

### Scenario A: Code-Only

You just want better code generation. No artifacts needed.

| Prompt | What happens |
|--------|--------------|
| `cypilot implement spec auth` | Generates code using code-checklist quality guidance |
| `cypilot add markers to src/auth/` | Adds traceability markers to existing code |
| `cypilot validate code` | Validates code quality and marker correctness |

**Benefits**: Quality-guided code generation, consistent patterns, marker-based traceability.

### Scenario B: Spec-First (Bottom-Up)

You want to document existing specs, then build up.

```
1. cypilot reverse SPEC from src/auth/     → Creates SPEC spec from code
2. cypilot reverse SPEC from src/billing/  → Creates another SPEC spec
3. cypilot decompose from specs            → Creates DECOMPOSITION from SPECs
4. cypilot make DESIGN from DECOMPOSITION     → Creates DESIGN from structure
5. cypilot make PRD from DESIGN               → (optional) Creates PRD from DESIGN
```

**When to use**: You want to document what exists without changing code.

### Scenario C: Design-First (Middle-Out)

You want to capture architecture, then decompose into specs.

```
1. cypilot reverse DESIGN from codebase       → Extracts architecture from code
2. cypilot decompose                          → Creates spec breakdown
3. cypilot make SPEC for {slug}            → Creates detailed specs
4. cypilot implement {slug}                   → Implements with markers
```

**When to use**: You want architectural control before spec work.

### Scenario D: Full Top-Down

You want complete documentation from requirements to code.

```
1. cypilot reverse PRD from codebase          → Extracts requirements
2. cypilot make DESIGN from PRD               → Creates architecture
3. cypilot decompose                          → Creates spec breakdown
4. cypilot make SPEC for {slug}            → Creates detailed specs
5. cypilot implement {slug}                   → Implements with markers
```

**When to use**: New team members, compliance requirements, or major refactoring.

### Scenario E: Gradual Adoption

Start minimal, add artifacts as needed.

```
Week 1: cypilot implement {slug}              → Code-only, with checklist
Week 2: cypilot make SPEC for {slug}       → Add specs for complex specs
Week 3: cypilot decompose                     → Organize specs
Later:  cypilot make DESIGN                   → Document architecture
```

**When to use**: You want low-friction adoption with growing benefits.

---

## What You Will Produce

Cypilot artifacts registered in `.cypilot-adapter/artifacts.json` ([taxonomy](TAXONOMY.md)):

| Artifact | Default Location |
|----------|------------------|
| PRD | `architecture/PRD.md` |
| ADR | `architecture/ADR/*.md` |
| DESIGN | `architecture/DESIGN.md` |
| DECOMPOSITION | `architecture/DECOMPOSITION.md` |
| SPEC | `architecture/specs/{slug}.md` |

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

Goal: produce validated baseline artifacts before you add or refactor specs.

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

**Provide context:** source of truth, existing specs, constraints.

**Example:**
```
cypilot reverse DESIGN from codebase
Context:
- Source of truth: code
- Existing specs: docs/openapi.yaml, docs/db-schema.md
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
| `cypilot decompose from codebase` | Extracts specs from existing code structure |
| `cypilot decompose by module` | Groups by code modules |
| `cypilot decompose by capability` | Groups by business capability |

**Update**

| Prompt | What happens |
|--------|--------------|
| `cypilot add spec {slug}` | Adds new spec entry |
| `cypilot update spec {slug} status` | Updates spec status |
| `cypilot update spec {slug} priority` | Updates spec priority |

**Provide context:** module boundaries, spec grouping preferences.

**Example:**
```
cypilot decompose from codebase
Context:
- Group specs by modules: billing, auth, reporting
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

## Workflow: Add a New Spec

Use when baseline exists and you want to add a new capability.

### 1. Add to DECOMPOSITION

| Prompt | What happens |
|--------|--------------|
| `cypilot add spec {slug}` | Adds new spec to decomposition |
| `cypilot add spec notifications` | Example: adds notifications spec |

### 2. SPEC spec

**Create**

| Prompt | What happens |
|--------|--------------|
| `cypilot make SPEC for {slug}` | Creates spec spec |
| `cypilot make SPEC spec for notifications` | Creates detailed design |

**Reverse-engineer from existing code**

| Prompt | What happens |
|--------|--------------|
| `cypilot reverse SPEC from src/notifications/` | Creates spec from existing code |
| `cypilot reverse SPEC {slug} from code` | Same, using spec slug |
| `cypilot draft SPEC from code` | Same, alternative phrasing |

**Update**

| Prompt | What happens |
|--------|--------------|
| `cypilot update SPEC {slug}` | Updates spec spec |
| `cypilot extend SPEC {slug} with {scenario}` | Adds scenario to spec |
| `cypilot sync SPEC {slug} from code` | Updates spec to match code |

**Provide context:** spec slug, code boundaries, scenarios to include.

**Example:**
```
cypilot make SPEC for notifications
Context:
- Include scenarios: retries, rate limits, provider outage
- Code boundaries: src/notifications/
```

### 3. Validate SPEC

| Prompt | What happens |
|--------|--------------|
| `cypilot validate SPEC {slug}` | Full validation (380+ criteria) |
| `cypilot validate SPEC {slug} semantic` | Semantic only (flows, edge cases) |
| `cypilot validate SPEC {slug} structural` | Structural only (CDSL, IDs) |
| `cypilot validate SPEC {slug} refs` | Cross-references to DESIGN |

### 4. CODE

**Implement from scratch**

| Prompt | What happens |
|--------|--------------|
| `cypilot implement {slug}` | Generates code from SPEC spec |
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
| `cypilot sync code with SPEC {slug}` | Updates code to match SPEC changes |

**Add markers to existing code**

| Prompt | What happens |
|--------|--------------|
| `cypilot add markers to {path}` | Adds `@cpt-*` markers to existing code |
| `cypilot add markers for {slug}` | Adds markers matching SPEC spec |
| `cypilot fix markers in {path}` | Fixes incorrect/incomplete markers |

**Provide context:** spec slug, code paths.

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
| `cypilot validate code for {slug}` | Validates specific spec |
| `cypilot validate code in {path}` | Validates code in specific path |

**Coverage**

| Prompt | What happens |
|--------|--------------|
| `cypilot validate code coverage` | Reports implementation coverage % |
| `cypilot validate code coverage for {slug}` | Coverage for specific spec |
| `cypilot show uncovered flows` | Lists flows without implementation |
| `cypilot show uncovered algorithms` | Lists algorithms without implementation |

**Traceability**

| Prompt | What happens |
|--------|--------------|
| `cypilot validate code orphans` | Finds markers referencing non-existent IDs |
| `cypilot validate code refs` | Validates all marker references |
| `cypilot validate code markers` | Checks marker format correctness |
| `cypilot list code markers` | Lists all markers in codebase |
| `cypilot list code markers for {slug}` | Lists markers for specific spec |

**Consistency**

| Prompt | What happens |
|--------|--------------|
| `cypilot compare code to SPEC {slug}` | Shows drift between code and spec |
| `cypilot validate code consistency` | Checks code matches SPEC specs |
| `cypilot find missing implementations` | Lists SPEC elements without code |

---

## Sync and Compare

When code and design drift apart:

| Prompt | What happens |
|--------|--------------|
| `cypilot compare DESIGN to code` | Shows drift between design and implementation |
| `cypilot compare SPEC {slug} to code` | Shows drift for specific spec |
| `cypilot sync DESIGN from code` | Updates DESIGN to match current code |
| `cypilot sync SPEC {slug} from code` | Updates SPEC to match current code |
| `cypilot sync code with SPEC {slug}` | Updates code to match SPEC |
| `cypilot diff SPEC {slug}` | Shows changes since last validation |

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
cypilot propagate DESIGN changes to SPEC {slug}
cypilot validate SPEC {slug}
```

### Spec Design Changed

```
cypilot update SPEC {slug}
cypilot validate SPEC {slug}
cypilot sync code with SPEC {slug}
cypilot validate code for {slug}
```

### Code Changed Without Design Update

```
cypilot compare SPEC {slug} to code
cypilot sync SPEC {slug} from code
cypilot validate SPEC {slug}
```

---

## Quick Reference

### By Adoption Level

| Level | What you do | Benefits |
|-------|-------------|----------|
| **Code-only** | `cypilot implement {slug}` | Code checklist, consistent patterns |
| **+ SPEC** | Add `cypilot make SPEC` | Flows, algorithms, edge cases documented |
| **+ DECOMPOSITION** | Add `cypilot decompose` | Spec organization, dependencies |
| **+ DESIGN** | Add `cypilot make DESIGN` | Architecture, components, data model |
| **+ PRD** | Add `cypilot make PRD` | Requirements, actors, full traceability |

### Top-Down (Full)

| Step | Generate | Validate |
|------|----------|----------|
| 1 | `cypilot reverse PRD from codebase` | `cypilot validate PRD` |
| 2 | `cypilot reverse DESIGN from codebase` | `cypilot validate DESIGN` |
| 3 | `cypilot decompose` | `cypilot validate DECOMPOSITION` |
| 4 | `cypilot make SPEC for {slug}` | `cypilot validate SPEC {slug}` |
| 5 | `cypilot implement {slug}` | `cypilot validate code for {slug}` |

### Bottom-Up (Spec-First)

| Step | Generate | Validate |
|------|----------|----------|
| 1 | `cypilot reverse SPEC from src/{path}/` | `cypilot validate SPEC {slug}` |
| 2 | `cypilot decompose from specs` | `cypilot validate DECOMPOSITION` |
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
- If code changes affect spec behavior, update SPEC first
- Re-validate the SPEC design
- Run `cypilot validate code` to ensure design and code remain consistent
- If code contradicts design, decide: update design OR update code
