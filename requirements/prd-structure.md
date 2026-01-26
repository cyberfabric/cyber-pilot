---
fdd: true
type: requirement
name: PRD Structure
version: 1.2
purpose: Define validation rules for PRD.md files
---

# PRD Structure Requirements

---

## Agent Instructions

**ALWAYS open and follow**: `../workflows/prd.md` WHEN executing workflow

**ALWAYS open and follow**: `../templates/PRD.template.md` WHEN generating content

**ALWAYS open**: `../examples/requirements/prd/valid.md` WHEN reviewing valid artifact structure

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
- Recommended: ≤500 lines
- Hard limit: ≤1000 lines

---

## File Overview

**Purpose**: PRD, actors, and requirements

**Location**: `architecture/PRD.md`

**Contains**: 
- Section A: Vision
- Section B: Actors
- Section C: Functional Requirements
- Section D: Use Cases
- Section E: Non-functional requirements
- Section F: Additional Context (optional)

---

## Content Boundaries

**Should contain**:
- Vision, actors, and requirements with stable IDs.
- Business vocabulary that downstream artifacts can reference without reinterpretation.

**Should not contain**:
- Technical architecture (use `architecture/DESIGN.md`).
- API endpoint specs or schemas.

---

## Validation Criteria

### File Validation

1. **File exists**
   - File `architecture/PRD.md` exists
   - File contains ≥50 lines (recommended: 200-500 lines)

### Structure Validation

1. **All required sections present**
   - Section A: VISION
   - Section B: Actors
   - Section C: Functional Requirements
   - Section D: Use Cases
   - Section E: Non-functional requirements
   - Section F: Additional Context (optional, not validated)

2. **Section order correct**
   - A → B → C → D → E → F

3. **No prohibited sections**
   - Only A-F allowed at top level

4. **Headers use proper levels**
   - `##` for sections A-F
   - `####` for actors/functional requirements/use cases/NFRs

### Content Boundaries Validation

**Check**:
- [ ] No technical architecture sections or architecture-level decisions are described here
- [ ] No implementation plans, tasks, or code-level details are described here
- [ ] No API endpoint specs or schemas are authored here (links are allowed)

### Content Validation

1. **Section A: VISION**
   - Contains: Purpose, Target Users, Key Problems Solved, Success Criteria
   - Contains: Capabilities (bulleted list, no IDs)
   - Success criteria are measurable
   - ≥2 paragraphs of content

2. **Section B: Actors**
   - ≥1 actor defined
   - Grouped by Human Actors and System Actors
   - Each actor has:
     - `####` heading with actor name
     - `**ID**:` line with valid actor ID
     - `**Role**:` line with description

3. **Section C: Functional Requirements**
   - ≥1 functional requirement defined
   - Each functional requirement has:
     - `####` heading with requirement name
     - `**ID**:` line with valid functional requirement ID
     - `**Actors**:` line listing actor IDs
     - Description (one or more paragraphs or a bulleted list)
   - All referenced actor IDs exist in Section B

4. **Section D: Use Cases**
   - ≥1 use case defined
   - Each use case has:
     - `####` heading with "UC-XXX: Use Case Name" format
     - `**ID**:` line with valid use case ID
     - `**Actor**:` line listing actor IDs
     - `**Preconditions**:` description
     - `**Flow**:` numbered list of steps
     - `**Postconditions**:` description
   - All referenced actor IDs exist in Section B
   - Flow steps MAY reference functional requirement IDs from Section C

5. **Section E: Non-functional requirements**
   - ≥1 NFR defined
   - Each NFR has:
     - `####` heading
     - `**ID**:` line with valid NFR ID
     - Description (one or more paragraphs or a bulleted list)

### FDD ID Format Validation

| ID Type | Format | Example |
|---------|--------|---------|
| Actor | `fdd-{project}-actor-{name}` | `fdd-analytics-actor-admin` |
| Functional Requirement | `fdd-{project}-fr-{name}` | `fdd-analytics-fr-export-report` |
| Use Case | `fdd-{project}-usecase-{name}` | `fdd-analytics-usecase-create-report` |
| NFR | `fdd-{project}-nfr-{name}` | `fdd-analytics-nfr-security` |
| PRD Context | `fdd-{project}-prd-context-{name}` | `fdd-analytics-prd-context-market-notes` |

**ID Rules**:
- All IDs wrapped in backticks
- Names in kebab-case (2-4 words)
- Unique within their section

### Cross-Reference Validation

1. **Functional Requirement → Actor**
   - All actor IDs in `**Actors**:` lines must exist in Section B
   - At least one actor per functional requirement

2. **Use Case → Actor**
   - All actor IDs in `**Actor**:` lines must exist in Section B

3. **Use Case → Capability**
   - Functional requirement IDs referenced in Flow must exist in Section C (optional)

---

## Best Practices

1. **Business-focused content** — no technical implementation details
2. **Actor definitions** — distinguish human vs system, concise roles
3. **Functional requirement scope** — broad but coherent, group related behaviors
4. **Success criteria** — measurable, quantitative targets
5. **ID naming** — descriptive, domain language, kebab-case

---

## Common Issues

- Missing required section structure (A/B/C headings)
- Actor headings not `####` or not grouped by Human/System
- Actor IDs wrong format or not wrapped in backticks
- Functional requirements missing actor references
- Use case actors using names instead of IDs
- Missing required section D (Use Cases)
- Missing required section E (Non-functional requirements)

---

## Validation Checklist (Final)

- [ ] Document follows required structure
- [ ] All validation criteria pass
- [ ] Agent used template for generation
- [ ] Agent referenced example for validation

---

## References

**Template**: `../templates/PRD.template.md`

**Example**: `../examples/requirements/prd/valid.md`

**Related**:
- `overall-design-structure.md` — DESIGN.md references PRD.md
- `../.adapter/specs/conventions.md` — Core FDD principles
