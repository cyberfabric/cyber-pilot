---
fdd: true
type: requirement
name: Overall Design Structure
version: 1.1
purpose: Define validation rules for DESIGN.md files
---

# Overall Design Structure Requirements

---

## Agent Instructions

**ALWAYS open and follow**: `../workflows/design.md` WHEN executing workflow

**ALWAYS open and follow**: `../templates/DESIGN.template.md` WHEN generating content

**ALWAYS open**: `../examples/requirements/overall-design/valid.md` WHEN reviewing valid artifact structure

**ALWAYS open and follow**: `requirements.md` WHEN extracting shared requirements

---

## Prerequisite Checklist

- [ ] Agent has read and understood this requirement
- [ ] Agent will follow the rules defined here
- [ ] Agent will use template for generation
- [ ] Agent will reference example for structure validation

---

## Overview

**This file defines**: Validation rules (WHAT must be valid)  
**Template defines**: Structure for generation (HOW to create)  
**Workflow defines**: Process (STEP by STEP)

**Size limits**:
- Recommended: ≤1500 lines
- Hard limit: ≤2000 lines

**Related**:
- `prd-structure.md` — PRD.md structure
- `adr-structure.md` — ADR directory structure

---

## File Overview

**Purpose**: Technical requirements, principles, and architecture

**Location**: `architecture/DESIGN.md`

**Contains**: 
- Section A: Architecture Overview
- Section B: Principles & Constraints
- Section C: Technical Architecture (C.1-C.4, optional C.5-C.7)
- Section D: Additional Context (optional)

---

## Content Boundaries

**Should contain**:
- System-level constraints and principles.
- Shared concepts/types/contracts that features must not redefine.
- References to domain model and API contract sources.

**Should not contain**:
- Feature-level flows/algorithms/states (use feature `DESIGN.md`).
- Implementation tasks or task breakdowns (track implementation status directly in feature `DESIGN.md`).
- Decision rationale debates (use ADRs).

---

## Validation Criteria

### File Validation

1. **File exists**
   - File `architecture/DESIGN.md` exists
   - File contains ≥200 lines (recommended: 500-2000 lines)

### Structure Validation

1. **All required sections present**
   - Section A: Architecture Overview
   - Section B: Principles & Constraints (B.1-B.2)
   - Section C: Technical Architecture (C.1-C.4, optional C.5-C.7)
   - Section D: Additional Context (optional)

2. **Section order correct**: A → B → C → D

3. **No prohibited sections**
   - Only A-D allowed at top level
   - Section C has required subsections C.1-C.4
   - Section C MAY include optional subsections C.5-C.7

4. **Section A includes Architecture drivers**
    - Section A MUST include a subsection titled `### Architecture drivers`
    - `### Architecture drivers` MUST include `#### Product requirements`
    - `#### Product requirements` MUST include a Markdown table with columns:
      - `FDD ID`
      - `Solution short description`

5. **Headers use proper levels**
   - `##` for sections A-D
   - `###` for subsections B.1-B.2, C.1-C.7
   - Subsection headers MUST use `:` or `.` after the number (examples: `### B.1: Design Principles`, `### C.3: API Contracts`)

### Content Boundaries Validation

**Check**:
- [ ] No feature-level flows/algorithms/states are authored here (those belong in feature `DESIGN.md`)
- [ ] No implementation tasks or task breakdowns are authored here (track implementation status directly in feature `DESIGN.md`)
- [ ] No ADR-style decision rationale debates are authored here (use ADR files for decision records)

### Section B Subsections

| Subsection | Content | Expected Content |
|------------|---------|------------------|
| B.1 | Design Principles | A list of architectural/design principles that shape decisions across the system. Each principle should include `**ID**: \`fdd-{project}-principle-{name}\`` and MAY include `**ADRs**:` references. |
| B.2 | Constraints | A list of hard constraints that limit solution space (regulatory, platform, compatibility, vendor, data residency, legacy integration). Each constraint should include `**ID**: \`fdd-{project}-constraint-{name}\`` and MAY include `**ADRs**:` references. |

### Section C Subsections

| Subsection | Content | Expected Content |
|------------|---------|------------------|
| C.1 | Domain Model | The authoritative domain model: entities/aggregates/value objects and their relationships, core invariants, and how they map to schemas. MUST provide clickable links to machine-readable schema sources (e.g., JSON Schema, TypeScript types, OpenAPI schemas) and indicate where they live in the repo. |
| C.2 | Component Model | High-level decomposition of the system into components/services/modules with responsibilities, boundaries, and key interactions. Include at least one diagram (image, Mermaid, or ASCII) and describe major data/control flows between components. |
| C.3 | API Contracts | The authoritative API contract surface (external and/or internal). MUST provide clickable links to machine-readable contracts (OpenAPI/CLISPEC/proto/GraphQL). For CLI tools, CLISPEC is the canonical and authoritative interface specification format and MUST be treated as machine-readable by validators and agents. Describe key endpoints/operations, request/response shapes at a high level, error handling expectations, authn/authz entry points, and versioning strategy if applicable. |
| C.4 | Interactions & Sequences | Sequence diagrams for the most important flows. Use cases and actors referenced here MUST be referenced by ID only and MUST exist in PRD.md. |
| C.5 | Database schemas & tables (optional) | Optional. If present, database tables MUST use stable IDs: `fdd-{project}-db-table-{name}`. |
| C.6 | Topology (optional) | Optional physical view (files, pods, containers, VMs, etc). If present, include stable ID: `fdd-{project}-topology-{name}`. |
| C.7 | Tech stack (optional) | Optional. If present, include stable ID: `fdd-{project}-tech-{name}`. |

### Content Validation

1. **Domain Model accessible**
   - Files at specified location exist
   - Files are in machine-readable format (GTS, JSON Schema, OpenAPI, TypeScript)
   - References are clickable Markdown links

2. **API Contracts accessible**
   - Files at specified location exist
   - Files are in machine-readable format (OpenAPI, GraphQL, CLISPEC, proto)
   - For CLI tools, CLISPEC is the canonical machine-readable format and MUST be accepted as authoritative
   - References are clickable Markdown links

3. **Component diagram present**
   - At least one diagram in Section C.2
   - Can be embedded image, Mermaid code, or ASCII art

---

## FDD ID Format Validation

| ID Type | Format | Example |
|---------|--------|---------|
| Principle | `fdd-{project}-principle-{name}` | `fdd-analytics-principle-plugin-based` |
| Constraint | `fdd-{project}-constraint-{name}` | `fdd-analytics-constraint-api-dep` |
| ADR | `fdd-{project}-adr-{name}` | `fdd-analytics-adr-event-sourcing` |
| DB Table (optional) | `fdd-{project}-db-table-{name}` | `fdd-analytics-db-table-users` |
| Topology (optional) | `fdd-{project}-topology-{name}` | `fdd-analytics-topology-local-dev` |
| Tech (optional) | `fdd-{project}-tech-{name}` | `fdd-analytics-tech-python` |
| Design Context (optional) | `fdd-{project}-design-context-{name}` | `fdd-analytics-design-context-migration-notes` |

**ID Rules**:
- All IDs wrapped in backticks
- Names in kebab-case (2-4 words)
- Unique within their section
- `**ID**:` line MUST be first non-empty line after heading

---

## Cross-Reference Validation

### PRD.md → DESIGN.md References

1. **Actor References (MANDATORY)**
   - If DESIGN.md references any actor IDs, each referenced actor ID MUST exist in PRD.md

2. **Use Case References (MANDATORY)**
   - If DESIGN.md references any use case IDs, each referenced use case ID MUST exist in PRD.md

3. **ADR References (MANDATORY)**
   - If DESIGN.md references any ADR IDs, each referenced ADR ID MUST exist in `architecture/ADR/`

### Validation Checks

- All referenced actor IDs exist in PRD.md
- All referenced use case IDs exist in PRD.md
- All referenced ADR IDs exist in `architecture/ADR/` (when ADR directory exists)

---

## Scoring

| Category | Points |
|----------|--------|
| Structure | 35 |
| Domain Model & API Contracts | 35 |
| Cross-References | 20 |
| Content Quality | 10 |
| **Total** | **100** |

**Penalties**:
- Invalid referenced actor ID: **-5 points** per ID
- Invalid referenced use case ID: **-5 points** per ID
- Invalid referenced ADR ID: **-5 points** per ID

---

## Common Issues

- Missing required top-level sections (A/B/C)
- Missing required C.1-C.4 subsections
- Domain model/API references not clickable links

---

## Validation Checklist (Final)

- [ ] Document follows required structure
- [ ] All validation criteria pass
- [ ] All traceability rules satisfied
- [ ] Agent used template for generation
- [ ] Agent referenced example for validation

---

## References

**Template**: `../templates/DESIGN.template.md`

**Example**: `../examples/requirements/overall-design/valid.md`

**Related**:
- `prd-structure.md` — PRD.md structure
- `adr-structure.md` — ADR directory structure
- `feature-design-structure.md` — Feature DESIGN.md structure
