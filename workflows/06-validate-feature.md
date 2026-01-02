# Validate Feature Design

**Phase**: 3 - Feature Development  
**Purpose**: Validate Feature DESIGN.md completeness and compliance with FDD requirements

---

## Prerequisites

- Feature directory exists: `architecture/features/feature-{slug}/`
- Feature DESIGN.md exists and contains content

## Input Parameters

- **slug**: Feature identifier (lowercase, kebab-case)
  - Example: `dashboard-mgmt`, `user-auth`

---

## Requirements

### 1: Validate File Exists and Size

**Requirement**: DESIGN.md must exist with appropriate size

**Location**: `architecture/features/feature-{slug}/DESIGN.md`

**Size Constraints**:
- **Recommended**: ≤3000 lines
- **Hard limit**: ≤4000 lines

**Expected Outcome**: File exists and is within size limits

**Validation Criteria**:
- File `DESIGN.md` exists in feature directory
- File size is reasonable (warning if >3000 lines, error if >4000 lines)
- File has substantial content (not empty or placeholder-only)

---

### 2: Validate Section Structure

**Requirement**: All required sections A-F must be present

**Required Sections**:
- **Section A**: Feature Context
- **Section B**: Actor Flows
- **Section C**: Algorithms
- **Section D**: States
- **Section E**: Technical Details
- **Section F**: Validation & Implementation

**Expected Outcome**: All 6 sections present with proper headings

**Validation Criteria**:
- Each section heading follows format `## A.`, `## B.`, etc.
- All 6 sections found in correct order
- No duplicate sections

---

### 3: Validate Section A (Feature Context)

**Requirement**: Section A must document feature context

**Size Constraint**: ≤500 lines recommended

**Required Subsections**:
- **Overview**: What this feature does
- **Purpose**: Why it exists, what problem it solves
- **Actors**: Who interacts with this feature
- **References**: Links to Overall Design and dependencies

**Expected Outcome**: Complete feature context documented

**Validation Criteria**:
- All required subsections present
- Section size reasonable (≤500 lines)
- References to Overall Design included
- Dependencies listed (if any)

---

### 4: Validate Section B (Actor Flows)

**Requirement**: Section B must document actor flows in FDL

**Size Constraint**: ≥50 lines (standard features)

**Content Requirements**:
- Actor flows written in FDL (see `../FDL.md`)
- Each flow includes: Actor, Steps, Success Scenarios, Error Scenarios
- Flows are comprehensive and cover main use cases
- No code blocks - only FDL syntax

**Expected Outcome**: Complete actor flows documented

**Validation Criteria**:
- Section has substantial content (≥50 lines for standard features)
- Flows use FDL syntax, not code
- All major actors and interactions covered

**Exceptions**:
- Init feature may have intentionally minimal Section B (structural task only)
- Technical/infrastructure features with minimal user interaction may have shorter flows
- Small utility features may require <50 lines if functionality is simple

---

### 5: Validate Section C (Algorithms)

**Requirement**: Section C must document algorithms in FDL (not code)

**Size Constraint**: ≥100 lines (standard features)

**Content Requirements**:
- Algorithms written in FDL (see `../FDL.md`)
- Each algorithm includes: Input, Output, Steps in FDL
- No programming language code blocks (no `rust`, `typescript`, `javascript`, `python`, `java`, etc.)
- No programming syntax (`fn`, `function`, `def`, `class`, `interface`)
- Use FDL control structures: **IF/THEN/ELSE**, **FOR EACH**, **WHILE**, etc.

**Expected Outcome**: Algorithms documented in FDL

**Validation Criteria**:
- Section has substantial content (≥100 lines for standard features)
- Uses FDL syntax, not code
- No code blocks with programming languages
- Algorithms are clear and implementable

**Exception**: Init feature may have intentionally minimal Section C (structural task only)

**Reference**: See `../FDL.md` for FDL syntax

---

### 6: Validate Section E (Technical Details)

**Requirement**: Section E must document technical implementation details

**Size Constraint**: ≥200 lines recommended

**Content Requirements**:
- **Database Schema**: Tables/entities, columns, relationships
- **API Endpoints**: Endpoint list with descriptions (reference API specification)
- **Security**: Authorization rules, access control
- **Error Handling**: Error types and handling approaches

**Expected Outcome**: Complete technical details documented

**Validation Criteria**:
- Section has substantial content (≥200 lines recommended)
- All technical aspects covered
- Details sufficient for implementation
- References to external specs where appropriate

---

### 7: Check for Type Redefinitions

**Requirement**: Feature must reference DML types, not redefine them

**Prohibited Content**:
- New type definitions (should reference Overall Design DML)
- JSON/YAML schema definitions
- Type redefinitions or duplicates

**Expected Behavior**:
- All types referenced from Overall Design
- Use DML references format (per adapter)
- No duplicate type definitions

**Expected Outcome**: Feature references existing types only

**Validation Criteria**:
- No phrases like "type definition" found
- No schema definitions in JSON/YAML blocks
- All types referenced, not defined

---

### 8: Check for TODO/TBD Markers

**Requirement**: Design must be complete with no placeholder content

**Prohibited Markers**:
- `TODO`
- `TBD`
- `FIXME`
- `XXX`
- `{placeholder}` or similar

**Expected Outcome**: Design is complete and ready for implementation

**Validation Criteria**:
- No TODO/TBD/FIXME/XXX markers found
- No placeholder content remaining
- All sections fully written
- Design is implementation-ready

---

### 9: Validate References to Overall Design

**Requirement**: Feature Design must correctly reference Overall Design elements

**What to Validate**:
- Domain types referenced (not redefined) from Overall Design
- API endpoints referenced (not redefined) from Overall Design
- Actors used match those defined in Overall Design
- Capabilities align with Overall Design Section A

**Reference Format**:
- Use DML notation for type references (per adapter)
- Use API paths for endpoint references
- Link to Overall Design sections where appropriate

**Expected Outcome**: Feature Design properly references Overall Design

**Validation Criteria**:
- No type redefinitions (already checked in Requirement 7)
- No API endpoint redefinitions
- Actor names consistent with Overall Design
- Clear traceability to Overall Design

---

### 10: Validate OpenSpec Changes Listed

**Requirement**: Section F must list planned OpenSpec changes

**Required Content**:
- **Testing Scenarios**: Test cases for validation
- **OpenSpec Changes**: List of implementation changes
  - Change numbering (001, 002, etc.)
  - Change descriptions
  - Scope and dependencies
  - Effort estimates
  - Verification criteria

**Expected Outcome**: Implementation plan documented

**Validation Criteria**:
- Section F contains OpenSpec changes
- Changes are numbered and described
- Testing scenarios defined
- Implementation is plannable

---

## Completion Criteria

Validation complete when:

- [ ] File size ≤4000 lines (recommended ≤3000)
- [ ] All sections A-F present
- [ ] Section A ≤500 lines
- [ ] Section B ≥50 lines (or minimal for init)
- [ ] Section C ≥100 lines, uses FDL (or minimal for init)
- [ ] Section E ≥200 lines
- [ ] No type redefinitions
- [ ] No TODO/TBD markers
- [ ] OpenSpec changes listed

---

## Common Challenges

### Issue: Section Too Short

**Resolution**: Add more detail. Review FDD requirements in `../AGENTS.md`

### Issue: Code Blocks in Section C

**Resolution**: Convert to FDL. See `../FDL.md`

### Issue: Type Definitions Found

**Resolution**: Remove definitions, reference DML types from Overall Design instead

---

## Next Activities

After validation passes:

1. **Initialize OpenSpec**: Run `09-openspec-init.md`
   - Creates openspec structure
   - Generates first change

2. **Start Implementation**: Follow OpenSpec workflow
   - Implement changes
   - Complete feature

---

## Scoring

**Validation Score**: 100/100 if all checks pass

**Completeness**: 100% if all sections have required content

**Target**: 100/100 + 100% completeness before starting implementation

---

## References

- **Core FDD**: `../AGENTS.md` - Validation requirements
- **FDL Spec**: `../FDL.md` - FDL syntax (flows, algorithms, states)
- **Next Workflow**: `09-openspec-init.md`
