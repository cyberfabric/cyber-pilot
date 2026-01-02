# Initialize Feature

**Phase**: 3 - Feature Development  
**Purpose**: Start work on a specific feature by initializing its design

---

## Prerequisites

- Features manifest exists: `architecture/features/FEATURES.md`
- Feature listed in manifest
- All feature dependencies have validated designs (DESIGN.md complete)

## Input Parameters

- **slug**: Feature identifier (lowercase, kebab-case)
  - Example: `user-auth`, `dashboard-mgmt`

---

## Requirements

### 1. Verify Feature in Manifest

**Requirement**: Feature must be documented in FEATURES.md

**Expected Outcome**: Feature listed and ready for development

**Validation Criteria**: Feature slug found in manifest

---

### 2. Verify Dependency Status

**Requirement**: All feature dependencies must have validated designs

**Dependency Check**:
- Extract "Depends On" from feature entry in FEATURES.md
- If "None" - proceed (no dependencies)
- If dependencies listed - verify each has validated DESIGN.md (passed workflow 06)

**Expected Outcome**: Prerequisites satisfied

**Validation Criteria**: All dependencies have complete and validated designs

---

### 3. Establish Feature Directory

**Requirement**: Feature must have dedicated directory

**Required Directory**: `architecture/features/feature-{slug}/`

**Expected Outcome**: Directory exists

**Validation Criteria**: Directory path accessible

---

### 4. Initialize Feature Design Document

**Requirement**: Create complete DESIGN.md template

**Required File**: `architecture/features/feature-{slug}/DESIGN.md`

**Template Structure**:
```bash
cat > DESIGN.md << 'EOF'
# {Feature Name} - Feature Design

**Status**: 🔄 IN_PROGRESS  
**Module**: {Project Name}

---

## A. Feature Context

### Overview

{Describe what this feature does}

### Purpose

{Why this feature exists, what problem it solves}

### Actors

- **Actor Name**: Role and what they do with this feature

### References

**MANDATORY Reading**:
- Overall Design: `@/architecture/DESIGN.md`
- FEATURES.md: `@/architecture/features/FEATURES.md`

**Dependencies**:
- {List dependent features if any}

---

## B. Actor Flows

### Flow 1: {Primary Actor Action}

**Actor**: {Actor Name}

**Steps**:
1. Actor does something
2. System responds
3. Actor sees result

**Success Scenario**:
- Outcome 1
- Outcome 2

**Error Scenarios**:
- Error condition 1 → System behavior
- Error condition 2 → System behavior

---

## C. Algorithms

### Algorithm 1: {Name}

**Input**: {Parameters}

**Output**: {Result}

**Steps** (in FDL):
1. Validate input parameters
   1. **IF** parameter invalid **THEN** return error
   2. **IF** parameter valid **THEN** continue

2. **FOR EACH** item in collection:
   1. Process item
   2. **IF** condition met **THEN** add to results

3. Return processed results

---

## D. States

*If feature has state machines, document here. Otherwise mark as N/A*

---

## E. Technical Details

### Database Schema

**Tables/Entities**:
- Table name: columns, relationships

### API Endpoints

**Endpoints** (reference API specification):
- `GET /api/v1/{resource}`: Description
- `POST /api/v1/{resource}`: Description

### Security

**Authorization**:
- Who can access what
- Security checks required

### Error Handling

**Errors**:
- ErrorType: When it occurs, how to handle

---

## F. Validation & Implementation

### Testing Scenarios

1. **Scenario Name**:
   - Given: Initial state
   - When: Action
   - Then: Expected result

### OpenSpec Changes

**Total Changes**: {Number}

#### Change 001: {Change Name}

**Status**: ⏳ NOT_STARTED

**Description**: {What this change does}

**Scope**:
- Item 1
- Item 2

**Dependencies**: {Dependencies or None}

**Effort**: {Hours estimate}

**Verification**:
- How to verify it works

---
EOF

  echo "✓ DESIGN.md template created"
fi
```

**Expected Result**: DESIGN.md has full template

---

### 5. Update Feature Status

**Requirement**: Mark feature as IN_PROGRESS in manifest

**Status Change**: ⏳ NOT_STARTED → 🔄 IN_PROGRESS

**Location**: Feature entry in `architecture/features/FEATURES.md`

**Expected Outcome**: Manifest reflects active development

**Validation Criteria**: Feature status shows IN_PROGRESS

---

## Completion Criteria

Feature initialization complete when:

- [ ] Feature exists in FEATURES.md
- [ ] All dependencies have validated designs
- [ ] Feature directory created
- [ ] DESIGN.md created with full template
- [ ] Feature status IN_PROGRESS
- [ ] Ready to fill in design details

---

## Common Challenges

### Issue: Dependencies Not Met

**Resolution**: Complete and validate dependency designs first (workflow 06). Design order should follow dependency graph in FEATURES.md

### Issue: Feature Not in Manifest

**Resolution**: Add to FEATURES.md first using `03-init-features.md`

---

## Next Activities

After initialization:

1. **Fill in DESIGN.md**: Complete all sections A-F
   - Define actors and flows (Section B - PRIMARY)
   - Describe algorithms in ADL (Section C)
   - Document technical details (Section E)
   - List OpenSpec changes (Section F)

2. **Validate Design**: Run `06-validate-feature.md {slug}`
   - Must pass 100/100 + 100% completeness
   - Fix issues and re-validate

3. **Start Implementation**: After validation passes
   - Run `09-openspec-init.md {slug}`
   - Implement changes
   - Complete feature

---

## References

- **Core FDD**: `../AGENTS.md` - Feature Design structure
- **FDL Spec**: `../FDL.md` - FDL syntax (flows, algorithms, states)
- **Next Workflow**: `06-validate-feature.md`
