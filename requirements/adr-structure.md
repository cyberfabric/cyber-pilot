---
fdd: true
type: requirement
name: ADR Structure
version: 1.1
purpose: Define validation rules for ADR directory and per-record ADR files
---

# ADR Structure Requirements

---

## Agent Instructions

**ALWAYS open and follow**: `../workflows/adr.md` WHEN executing workflow

**ALWAYS open and follow**: `../templates/ADR.template.md` WHEN generating a new ADR file under `architecture/ADR/`

**ALWAYS open**: `../examples/requirements/adr/valid.md` WHEN reviewing valid artifact structure

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

**Format**: Industry-standard MADR (Markdown Any Decision Records) with FDD extensions

---

## File Overview

**Purpose**: Track all significant architectural decisions and their rationale

**Location**: `architecture/ADR/` (directory)

**Default category**: `architecture/ADR/general/`

**File naming**: `architecture/ADR/{category}/0001-<adr-fdd-id>.md`
- `{category}`: user-defined grouping folder (kebab-case recommended)
- `0001`: ADR number (must match `ADR-0001`)
- `<adr-fdd-id>`: `fdd-{project}-adr-{slug}`

**Reference from DESIGN.md**: link to ADR file path under `architecture/ADR/`

---

## Content Boundaries

**Should contain**:
- Context/problem statement.
- Considered options (short, comparable).
- Decision outcome and consequences.
- Links to related design elements (IDs).

**Should not contain**:
- Full architecture description (keep that in `architecture/DESIGN.md`).
- Detailed implementation steps.
- Broad product requirements.

---

## Validation Criteria

### File Validation

1. **ADR directory exists**
   - Directory `architecture/ADR/` exists
   - Directory contains ≥1 ADR file matching `architecture/ADR/**/NNNN-fdd-*-adr-*.md` (categories are optional)

### ADR Structure Validation (Across All Files)

1. **ADR numbering**
   - Format: `ADR-NNNN` (zero-padded 4 digits)
   - ADR-0001 exists (required — initial architecture)
   - Numbers are sequential, no gaps
   - All numbers unique

2. **File naming matches ADR header**
   - Each ADR file name MUST start with `NNNN-`
   - Each ADR file MUST contain exactly one ADR header: `# ADR-NNNN: Title`
   - `NNNN` in filename MUST match `NNNN` in ADR header

3. **File naming matches ADR FDD ID**
   - Each ADR file name MUST include `<adr-fdd-id>` after `NNNN-`
   - Each ADR file MUST include an `**ADR ID**:` line with the same `<adr-fdd-id>`
   - `<adr-fdd-id>` MUST match pattern: `fdd-{project}-adr-{slug}`

### ADR Structure Validation (Per ADR File)

1. **Required metadata fields**
   - `**Date**: YYYY-MM-DD`
   - `**Status**: Proposed | Rejected | Accepted | Deprecated | Superseded`
   - `**ADR ID**: ` with a valid FDD ADR ID wrapped in backticks

2. **Required sections (MADR core + FDD extension)**
   - `## Context and Problem Statement`
   - `## Considered Options`
   - `## Decision Outcome`
   - `## Related Design Elements` (FDD extension)

3. **Optional MADR sections (allowed)**
   - `## Decision Drivers`
   - `### Consequences` (under `## Decision Outcome`)
   - `### Confirmation` (under `## Decision Outcome`)
   - `## Pros and Cons of the Options`
   - `## More Information`

4. **Status valid**
   - One of: Proposed, Rejected, Accepted, Deprecated, Superseded
   - If Superseded, references another ADR

5. **Date format**
   - YYYY-MM-DD format
   - Date is valid

### Content Boundaries Validation

**Check**:
- [ ] ADR does not restate the entire architecture (keep that in `architecture/DESIGN.md`)
- [ ] ADR does not contain detailed implementation plans or task lists
- [ ] ADR does not contain broad product requirement catalogs

### Content Validation

| Section | Requirement |
|---------|-------------|
| Context | ≥2 sentences describing the problem |
| Considered Options | ≥2 distinct options, chosen marked |
| Decision Outcome | Chosen option + rationale + consequences |
| Related Design Elements | ≥1 category with ≥1 FDD ID |

### Decision Outcome Requirements

- `Chosen option:` stated
- **Rationale** provided (≥1 sentence)
- If `### Consequences` is present: include at least one good and one bad consequence

### Related Design Elements (FDD Extension)

**Categories**:
- **Actors**: IDs from PRD.md Section B
- **Capabilities**: IDs from PRD.md Section C
- **Requirements**: IDs from DESIGN.md Section B
- **Principles**: IDs from DESIGN.md Section B

**Rules**:
- At least one category MUST have ≥1 ID
- All IDs wrapped in backticks
- All IDs follow format: `fdd-{project}-{type}-{name}`
- Each ID followed by brief description

---

## Cross-Reference Validation

1. **Actor IDs** — exist in PRD.md Section B
2. **Capability IDs** — exist in PRD.md Section C
3. **Requirement IDs** — exist in DESIGN.md Section B
4. **Principle IDs** — exist in DESIGN.md Section B

---

## Best Practices

### Write ADRs When

- Making significant architectural decisions
- Choosing between multiple viable options
- Establishing architectural constraints
- Changing existing architecture

### Do NOT Write ADRs For

- Obvious or trivial decisions
- Easily reversible decisions
- Implementation details
- Coding standards

### Quality Guidelines

- **Good Context**: Specific problem, clear constraints
- **Good Options**: ≥2 distinct viable alternatives
- **Good Rationale**: Clear reasoning, references drivers, honest about cons

---

## Common Issues

- Missing required ADR fields (`**Date**`, `**Status**`)
- Missing required sections (Context, Drivers, Options, Outcome, Related Elements)
- Related Design Elements does not reference any FDD IDs
- ADR-0001 missing (initial architecture decision)
- Status not one of valid values

---

## Validation Checklist (Final)

- [ ] Document follows required structure
- [ ] All validation criteria pass
- [ ] All FDD ID references are valid
- [ ] Agent used template for generation
- [ ] Agent referenced example for validation

---

## References

**Template**: `../templates/ADR.template.md`

**Example**: `../examples/requirements/adr/valid.md`

**External**:
- MADR: https://adr.github.io/madr/
- ADR Organization: https://github.com/joelparkerhenderson/architecture-decision-record

**Related**:
- `prd-structure.md` — Actor/Capability IDs
- `overall-design-structure.md` — Requirement/Principle IDs
