---
fdd: true
type: requirement
name: Feature Design Structure
version: 1.2
purpose: Define validation rules for feature DESIGN.md files
---

# Feature Design Structure Requirements

---

## Agent Instructions

**ALWAYS open and follow**: `../workflows/feature.md` WHEN executing workflow

**ALWAYS open and follow**: `../templates/feature-DESIGN.template.md` WHEN generating content

**ALWAYS open**: `../examples/requirements/feature-design/valid.md` WHEN reviewing valid artifact structure

**ALWAYS open and follow**: `requirements.md` WHEN extracting shared requirements

**ALWAYS open and follow**: `FDL.md` WHEN writing flows, algorithms, or states

---

## Prerequisite Checklist

- [ ] Agent has read and understood this requirement
- [ ] Agent will follow the rules defined here
- [ ] Agent will use template for generation
- [ ] Agent will reference example for structure validation
- [ ] Agent will follow FDL syntax for behavioral sections

---

## Overview

**This file defines**: Validation rules (WHAT must be valid)  
**Template defines**: Structure for generation (HOW to create)  
**Workflow defines**: Process (STEP by STEP)

**Location**: `architecture/features/feature-{slug}/DESIGN.md`

**Size limits**:
- Recommended: ≤3000 lines
- Hard limit: ≤4000 lines

---

## Content Boundaries

**Should contain**:
- Feature context, references, and boundaries.
- FDL content:
  - Actor flows
  - Algorithms
  - States
- Feature requirements and phases.
- Implementation guidance for developers/agents.
- Explicit technical interactions where applicable (API calls, database operations, external integrations).

**Should not contain**:
- Sprint/task breakdowns.
- System-level type redefinitions (use `architecture/DESIGN.md`).
- Code diffs or code snippets.

---

## Required Sections

| Section | Purpose | Required |
|---------|---------|----------|
| A | Feature Context | YES |
| B | Actor Flows (FDL) | YES |
| C | Algorithms (FDL) | YES |
| D | States (FDL) | YES (can be minimal) |
| E | Requirements | YES |
| F | Additional Context | Optional |

**Order**: A → B → C → D → E → [F]

---

## Validation Criteria

### File Validation

- File exists at `architecture/features/feature-{slug}/DESIGN.md`
- File ≤4000 lines (warning if >3000)

### Structure Validation

- All required sections A-E present
- Correct section order
- No duplicate sections

### Content Boundaries Validation

**Check**:
- [ ] No sprint/task breakdowns are authored here
- [ ] No system-level type redefinitions are authored here (reference `architecture/DESIGN.md` instead)
- [ ] No code diffs or code snippets are authored here

### Section Requirements

| Section | Min Lines | Key Requirement |
|---------|-----------|-----------------|
| A | — | Feature ID, Status, Actors from PRD.md |
| B | 50 | FDL syntax, flow IDs, checkboxes, explicit API/DB/integration interactions when applicable |
| C | 100 | FDL syntax, algo IDs, explicit API/DB/integration interactions when applicable |
| D | — | FDL syntax with **WHEN** keyword |
| E | — | ≥1 requirement with all required fields |
| F | — | If present: context IDs and payload blocks |

---

## FDD ID Formats

| ID Type | Format |
|---------|--------|
| Flow | `fdd-{project}-feature-{slug}-flow-{name}` |
| Algorithm | `fdd-{project}-feature-{slug}-algo-{name}` |
| State | `fdd-{project}-feature-{slug}-state-{name}` |
| Requirement | `fdd-{project}-feature-{slug}-req-{name}` |
| Context | `fdd-{project}-feature-{slug}-context-{name}` |

**ID Rules**:
- All IDs wrapped in backticks
- Names in kebab-case (2-4 words)
- Unique within their section
- Must include checkbox: `- [ ] **ID**: {id}` or `- [x] **ID**: {id}`

---

## FDL Requirements

### Mandatory for Sections B, C, D

**Step format**:
```
1. [ ] - `ph-1` - {instruction} - `inst-{short-id}`
```

**Required elements per step**:
- Checkbox: `[ ]` or `[x]`
- Phase token: `ph-{N}`
- Instruction ID: `inst-{short-id}` (unique within section)

**Technical detail requirement (B and C)**:
- Actor flows and algorithms **MUST** include explicit interaction details when the step implies them:
  - API: method + path (example: `API: POST /api/tasks`)
  - DB: operation + table(s) (example: `DB: INSERT tasks(...)` or `DB: SELECT tasks WHERE id=?`)
  - Integrations: system name + action (example: `Integration: notify Slack channel #ops`)
- If the feature reuses system-level endpoints or schemas, steps **MUST** reference them rather than redefine them.

### FDL Keywords

**Allowed**:
- Control: **IF**, **ELSE IF**, **ELSE**, **FOR EACH**, **WHILE**
- Error: **TRY**, **CATCH**
- Flow: **RETURN**, **PARALLEL**, **GO TO**, **SKIP TO**
- Pattern: **MATCH**, **CASE**
- State: **FROM**, **TO**, **WHEN** (states only)

**Prohibited** (as bold keywords):
- **WHEN** (except in states), **THEN**, **SET**, **VALIDATE**, **CHECK**
- **LOAD**, **READ**, **WRITE**, **CREATE**, **ADD**, **AND**
- Gherkin: **GIVEN**, **WHEN**, **THEN** (in tests)

---

## Section E: Requirements Validation

**Required fields per requirement**:

| Field | Description |
|-------|-------------|
| **ID** | Unique requirement ID with checkbox |
| **Status** | ⏳ NOT_STARTED, 🔄 IN_PROGRESS, ✅ IMPLEMENTED |
| **Description** | SHALL/MUST statements |
| **Implementation details** | Guidance and constraints for implementation |
| **References** | Anchors to sections B-E |
| **Implements** | Flow/algo/state IDs |
| **Phases** | Phase decomposition with checkboxes |

**Implementation details** is the authoritative place to specify API/DB/domain entity impact when relevant.

---

## Cross-Validation with Overall Design

### Type References
- ✅ Reference types from Overall Design Section C
- ❌ No new type definitions in feature DESIGN.md

### API References
- ✅ Reference endpoints from Overall Design
- ❌ No new endpoint definitions

### Actor Alignment
- ✅ Only actors from PRD.md
- Actor IDs must match

---

## Scoring

| Category | Points |
|----------|--------|
| Structure (A-E present) | 20 |
| FDL Compliance (B, C, D) | 35 |
| Requirements (E) | 35 |
| Additional Context (F, if present) | 10 |
| **Total** | **100** |

---

## Common Issues

- Missing required sections (A-E)
- Invalid section order
- Missing or invalid FDL step format
- Missing required requirement fields
- Missing `<!-- fdd-id-content -->` payload blocks
- Type redefinitions instead of references

---

## Validation Checklist (Final)

- [ ] Document follows required structure (A-E)
- [ ] All validation criteria pass
- [ ] FDL syntax correct in B, C, D
- [ ] Cross-validation with Overall Design passes
- [ ] Agent used template for generation
- [ ] Agent referenced example for validation
- [ ] Agent followed FDL.md for behavioral sections

---

## References

**Template**: `../templates/feature-DESIGN.template.md`

**Example**: `../examples/requirements/feature-design/valid.md`

**Related**:
- `FDL.md` — FDL syntax specification
- `overall-design-structure.md` — Overall Design structure
