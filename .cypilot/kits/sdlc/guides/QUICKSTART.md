# Cypilot SDLC Quick Start

**Learn Cypilot SDLC in 10 minutes with real prompts and examples**

Cypilot SDLC works through the `cypilot` skill — enable it with `cypilot on` and use natural language prompts prefixed with `cypilot`. The skill handles artifact discovery, template loading, validation, and traceability automatically.

---

## What You'll Learn

1. **Exact prompts to type** — copy-paste into your AI chat
2. **Complete pipeline** — from requirements to validated code
3. **Reverse engineering** — create artifacts from existing code
4. **Working with existing docs** — import what you already have

---

## The Pipeline

Cypilot SDLC = **Design First, Code Second**

```mermaid
flowchart LR
    PRD["**PRD**<br/>300+ criteria"]
    ADR["**ADR**<br/>270+ criteria"]
    DESIGN["**DESIGN**<br/>380+ criteria"]
    DECOMP["**DECOMPOSITION**<br/>130+ criteria"]
    FEATURE["**FEATURE**<br/>380+ criteria"]
    CODE["**CODE**<br/>200+ criteria"]

    PRD --> ADR --> DESIGN --> DECOMP --> FEATURE --> CODE
```

| Artifact | Purpose |
|----------|---------|
| **PRD** | Product requirements — actors, capabilities, requirements, use cases, constraints |
| **ADR** | Architecture Decision Record — context, options, decision, consequences |
| **DESIGN** | Technical architecture — components, interfaces, data models, sequences |
| **DECOMPOSITION** | Feature breakdown — ordered implementation units with dependencies |
| **FEATURE** | Feature acceptance criteria, flows, algorithms, edge cases, definitions of done |
| **CODE** | Implementation — tagged with `@cpt-*` markers for traceability |

**Key principle**: If code contradicts design, fix design first, then regenerate code.

Learn what each artifact means: [TAXONOMY.md](TAXONOMY.md)

---

## Getting Started

| Prompt | What happens |
|--------|--------------|
| `cypilot on` | Enables Cypilot mode, discovers adapter, loads project context |
| `cypilot init` | Creates `.cypilot-adapter/` with `artifacts.json` and domain context files |
| `cypilot show pipeline` | Displays current artifact hierarchy and validation status |

**Customizing artifact locations:**

| Prompt | What happens |
|--------|--------------|
| `cypilot set artifacts_dir to docs/design/` | Changes default base directory for new artifacts |
| `cypilot register PRD at docs/requirements/product-requirements.md` | Registers existing file as PRD artifact |
| `cypilot move PRD to docs/requirements/PRD.md` | Moves artifact and updates registry |
| `cypilot show artifact locations` | Displays current paths from `artifacts.json` |

---

## Example Prompts — Greenfield Project

**PRD — Product Requirements**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot make PRD` | Generates PRD interactively, asking for context |
| `cypilot make PRD for task management API` | Generates PRD with actors, requirements, flows |
| `cypilot draft PRD from README` | Creates PRD draft from existing README |
| `cypilot extend PRD with notifications` | Adds new capability to existing PRD |
| `cypilot validate PRD` | Full validation (300+ criteria) |
| `cypilot validate PRD semantic` | Semantic validation only (completeness, clarity) |
| `cypilot validate PRD structural` | Structural validation only (format, IDs, template) |
| `cypilot validate PRD refs` | Check cross-references to other artifacts |

**ADR — Architecture Decision Records**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot make ADR for PostgreSQL` | Creates ADR for technology choice |
| `cypilot make ADR for REST vs GraphQL` | Creates ADR comparing approaches |
| `cypilot draft ADR from discussion` | Extracts decision from conversation |
| `cypilot list ADRs` | Shows all ADRs with status |
| `cypilot validate ADR` | Validates all ADRs (270+ criteria each) |
| `cypilot validate ADR 0001` | Validates specific ADR by number |
| `cypilot validate ADR semantic` | Semantic validation (rationale quality) |
| `cypilot validate ADR structural` | Structural validation (format, sections) |

**DESIGN — Technical Architecture**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot make DESIGN` | Creates DESIGN from PRD interactively |
| `cypilot make DESIGN from PRD` | Transforms PRD into architecture |
| `cypilot extend DESIGN with caching layer` | Adds new component to existing DESIGN |
| `cypilot update DESIGN components` | Updates component section |
| `cypilot validate DESIGN` | Full validation (380+ criteria) |
| `cypilot validate DESIGN semantic` | Semantic validation (consistency, completeness) |
| `cypilot validate DESIGN structural` | Structural validation (format, IDs) |
| `cypilot validate DESIGN refs` | Check references to PRD/ADR |

**DECOMPOSITION — Feature Breakdown**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot decompose` | Creates DECOMPOSITION interactively |
| `cypilot decompose into features` | Creates ordered feature list with dependencies |
| `cypilot decompose by capability` | Groups features by business capability |
| `cypilot decompose by layer` | Groups features by technical layer |
| `cypilot add feature to decomposition` | Adds new feature entry |
| `cypilot validate DECOMPOSITION` | Full validation (130+ criteria) |
| `cypilot validate DECOMPOSITION semantic` | Semantic validation (coverage, dependencies) |
| `cypilot validate DECOMPOSITION structural` | Structural validation (format, IDs) |

**FEATURE — Feature Specification**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot make FEATURE for auth` | Creates feature design for auth |
| `cypilot make FEATURE for task-crud` | Creates detailed feature design |
| `cypilot draft FEATURE from code` | Reverse-engineers feature from implementation |
| `cypilot extend FEATURE auth with MFA` | Adds scenario to existing feature |
| `cypilot validate FEATURE auth` | Full validation (380+ criteria) |
| `cypilot validate FEATURE auth semantic` | Semantic validation (flows, edge cases) |
| `cypilot validate FEATURE auth structural` | Structural validation (CDSL format, IDs) |
| `cypilot validate FEATURE auth refs` | Check references to DESIGN/DECOMPOSITION |

**CODE — Implementation**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot implement {slug}` | Generates code from FEATURE |
| `cypilot implement {slug} step by step` | Implements with user confirmation |
| `cypilot implement {slug} tests first` | Generates tests first, then code |
| `cypilot implement {slug} flow {flow-id}` | Implements specific flow only |
| `cypilot implement {slug} api` | Implements API layer only |
| `cypilot implement {slug} tests` | Generates tests only |
| `cypilot continue implementing {slug}` | Continues partial implementation |
| `cypilot implement {slug} remaining` | Implements only unimplemented parts |
| `cypilot sync code with FEATURE {slug}` | Updates code to match FEATURE |
| `cypilot add markers to {path}` | Adds markers to existing code |
| `cypilot add markers for {slug}` | Adds markers matching FEATURE |

**CODE — Validation**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot validate code` | Validates all code markers |
| `cypilot validate code for {slug}` | Validates specific feature |
| `cypilot validate code coverage` | Reports implementation coverage % |
| `cypilot validate code coverage for {slug}` | Coverage for specific feature |
| `cypilot validate code orphans` | Finds orphaned markers |
| `cypilot validate code refs` | Validates marker references |
| `cypilot validate code markers` | Checks marker format |
| `cypilot list code markers` | Lists all markers |
| `cypilot list code markers for {slug}` | Lists markers for feature |
| `cypilot show uncovered flows` | Lists flows without code |
| `cypilot compare code to FEATURE {slug}` | Shows drift from feature |
| `cypilot find missing implementations` | Lists unimplemented elements |

**Pipeline & Cross-Artifact**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot validate all` | Validates entire hierarchy |
| `cypilot validate refs` | Checks all cross-references |
| `cypilot show pipeline` | Displays artifact status |
| `cypilot coverage report` | Summary of implementation coverage |

---

## Example Prompts — Brownfield Project

**Reverse-engineer from code**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot reverse PRD from codebase` | Extracts requirements from existing implementation |
| `cypilot reverse DESIGN from src/` | Documents current architecture from code |
| `cypilot reverse FEATURE from src/auth/` | Creates FEATURE from auth module |
| `cypilot reverse FEATURE auth from code` | Same, using feature slug |
| `cypilot analyze src/api/` | Systematic code analysis with checklist |

**Import from existing docs**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot make PRD from docs/requirements.txt` | Extracts requirements into PRD format |
| `cypilot make PRD from README` | Creates PRD from project README |
| `cypilot make PRD from this conversation` | Creates PRD from stakeholder discussion |
| `cypilot import OpenAPI as DESIGN` | Converts API spec into DESIGN |
| `cypilot import db-schema.sql as DESIGN data model` | Extracts data model from SQL |
| `cypilot convert user-stories.md to PRD` | Transforms user stories to PRD |

**Sync and compare**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot compare DESIGN to code` | Shows drift between design and implementation |
| `cypilot sync DESIGN from code` | Updates DESIGN to match current code |
| `cypilot diff FEATURE auth` | Shows changes since last validation |

---

## Example Prompts — Evolution & Maintenance

**Extend artifacts**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot extend PRD with payments` | Adds capability to PRD |
| `cypilot extend DESIGN with caching` | Adds component to DESIGN |
| `cypilot extend FEATURE auth with MFA` | Adds scenario to feature |
| `cypilot add feature billing to decomposition` | Adds feature entry |

**Update and propagate**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot update PRD requirements` | Updates requirements section |
| `cypilot propagate PRD changes to DESIGN` | Updates DESIGN from PRD changes |
| `cypilot sync DESIGN from code` | Updates DESIGN to match implementation |

**Impact analysis**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot show impact of removing FR-AUTH-002` | Traces downstream references |
| `cypilot show impact of changing component auth` | Shows affected artifacts |
| `cypilot deprecate feature user-import` | Marks deprecated across artifacts |

**Refactoring**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot refactor component auth-service` | Updates DESIGN and FEATUREs |
| `cypilot rename feature billing to payments` | Renames across all artifacts |
| `cypilot split feature payments` | Creates sub-features |
| `cypilot merge features billing and invoicing` | Combines features |

---

## Example Prompts — Review & Quality

**Validation modes**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot validate {ARTIFACT}` | Full validation (structural + semantic) |
| `cypilot validate {ARTIFACT} semantic` | Semantic only (content quality, completeness) |
| `cypilot validate {ARTIFACT} structural` | Structural only (format, IDs, template compliance) |
| `cypilot validate {ARTIFACT} refs` | Cross-reference validation only |
| `cypilot validate {ARTIFACT} quick` | Fast check (critical issues only) |
| `cypilot validate all` | Full validation of entire pipeline |
| `cypilot validate all semantic` | Semantic validation across all artifacts |

**Traceability queries**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot trace FR-AUTH-001` | Shows path: PRD → DESIGN → FEATURE → CODE |
| `cypilot trace feature auth` | Shows all references to auth feature |
| `cypilot find orphans` | Lists IDs with no upstream/downstream refs |
| `cypilot find orphan code` | Code markers referencing non-existent IDs |
| `cypilot find orphan requirements` | Requirements not covered by DESIGN |
| `cypilot list unimplemented` | Features without code coverage |
| `cypilot coverage report` | Implementation coverage by artifact |
| `cypilot show refs for DESIGN` | All references in DESIGN artifact |

**Review prompts**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot review PRD` | Deep review with 300+ criteria |
| `cypilot review DESIGN for consistency` | Checks for internal contradictions |
| `cypilot review FEATURE auth for completeness` | Validates edge cases and error handling |
| `cypilot review PR #42 against FEATURE` | Checks PR implements feature items |
| `cypilot review code for auth` | Reviews implementation quality |

---

## Live Example

[Taskman (Cypilot example project)](https://github.com/cyberfabric/cyber-pilot-examples-taskman) — a complete task management project with the full Cypilot artifact set and implementation.

---

## Guides by Scenario

| Scenario | Guide | Key Point |
|----------|-------|-----------|
| **Greenfield** | [GREENFIELD.md](GREENFIELD.md) | Start from PRD, work down to code |
| **Brownfield** | [BROWNFIELD.md](BROWNFIELD.md) | Start anywhere — code-only, bottom-up, or full |
| **Modular monolith** | [MONOLITH.md](MONOLITH.md) | Project-level + module-level artifacts |

**Brownfield flexibility**: No required order. Start with code-only (checklist benefits), add FEATURE designs for complex areas, add DESIGN later. Or go full top-down. Your choice.

## Reference

- Artifact taxonomy: [TAXONOMY.md](TAXONOMY.md)
- Full prompt reference: [README.md](../../../README.md#example-prompts)
