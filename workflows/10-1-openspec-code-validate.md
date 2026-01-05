# Validate Code Against OpenSpec

**Phase**: 3 - Feature Development  
**Purpose**: Verify implemented code matches OpenSpec change specifications

---

## Prerequisites

- Change implemented (run `10-openspec-change-implement.md` first)
- Code compiles without errors
- Basic tests passing

## Input Parameters

- **slug**: Feature identifier (lowercase, kebab-case)
- **change-id**: Change number (e.g., "001", "002")

---

## Requirements

### 1: Load Change Specifications

**Requirement**: Read specs to understand what code should implement

**Location**: `openspec/changes/{change-name}/specs/fdd-{project-name}-feature-{feature-slug}/` (project root)

**Command**:
```bash
# Run from project root
openspec show {change-name}
```

**What to Load**:
- `proposal.md` - What this change does
- `specs/**/*.md` - Technical specifications
- `design.md` (if exists) - Technical decisions

**Expected Outcome**: Clear understanding of requirements

---

### 2: Validate Code Against Specifications

**Requirement**: Verify code implements all spec requirements

**Load Adapter**:
```bash
cat ../../../FDD-Adapter/AGENTS.md
```

**What to Validate**:

**API Contracts** (if specified):
- ✅ All endpoints in specs are implemented
- ✅ Request/response schemas match spec
- ✅ HTTP methods match spec
- ✅ Status codes match spec
- ❌ Extra endpoints not in spec

**Domain Model** (if specified):
- ✅ All types in specs are implemented
- ✅ Type properties match spec
- ✅ Type relationships match spec
- ❌ Type definitions contradict spec

**Business Logic** (if specified):
- ✅ Algorithms follow spec steps
- ✅ Validation rules match spec
- ✅ Error handling matches spec
- ✅ Edge cases from spec are handled

**Database Schema** (if specified):
- ✅ Tables/collections match spec
- ✅ Columns/fields match spec
- ✅ Indexes match spec
- ✅ Constraints match spec

**Use Adapter Commands**:
Run project-specific validation commands from adapter:
```bash
# Get validation commands from adapter
cat ../../../FDD-Adapter/AGENTS.md | grep -A 20 "Code Validation Commands"
```

**Expected Outcome**: Code fully implements spec

**Validation Criteria**:
- All specified APIs implemented
- All specified types implemented
- All specified logic implemented
- No contradictions between code and spec
- No extra functionality not in spec

---

### 3: Cross-Reference with Feature Design

**Requirement**: Verify change aligns with feature DESIGN.md

**Load Feature Design**:
```bash
cat ../DESIGN.md
```

**What to Verify**:
- Change implements part of Section B (Actor Flows) or Section C (Algorithms)
- Implementation doesn't contradict feature design
- Types used match Overall Design domain model
- API endpoints match Overall Design contracts

**Expected Outcome**: Change aligns with feature design

---

### 4: Run Spec-Specific Tests

**Requirement**: Execute tests that verify spec compliance

**Test Categories**:

**Unit Tests**:
- Test each spec requirement individually
- Verify spec edge cases
- Test spec error conditions

**Integration Tests** (if applicable):
- Test spec workflows end-to-end
- Verify spec data flow
- Test spec side effects

**Contract Tests** (if APIs specified):
- Validate request/response schemas
- Verify endpoint behavior
- Test error responses

**Use Adapter Test Commands**:
```bash
# Get test commands from adapter
cat ../../../FDD-Adapter/AGENTS.md | grep -A 10 "Test Commands"
```

**Expected Outcome**: 100% spec-related tests passing

---

### 5: Generate Validation Report

**Requirement**: Document validation results

**Report Structure**:
```markdown
# Code Validation Report - {change-id}

**Validation Date**: {timestamp}
**Change**: {change-id}-{name}

## Specifications Coverage

- [ ] API contracts implemented (if applicable)
- [ ] Domain model types implemented (if applicable)
- [ ] Business logic implemented (if applicable)
- [ ] Database schema implemented (if applicable)

## Spec Compliance

### ✅ Implemented Requirements
- {List spec requirements that are implemented}

### ❌ Missing Requirements
- {List spec requirements not yet implemented}

### ⚠️ Deviations from Spec
- {List any code that contradicts or extends spec}

## Test Results

- Unit tests: {X/Y passed}
- Integration tests: {X/Y passed}
- Contract tests: {X/Y passed}

## Feature Design Alignment

- ✅ Aligns with feature DESIGN.md Section B/C
- ✅ Uses correct domain types
- ✅ Uses correct API endpoints

## Validation Status

**PASS** / **FAIL**

{If FAIL, list required fixes}
```

**Report Location**: `openspec/changes/{change-id}-{name}/VALIDATION_REPORT.md`

**Expected Outcome**: Complete validation audit trail

---

## Validation Scoring

**Target Score**: 100/100 (all checks must pass)

**Scoring Categories**:
1. **Spec Coverage** (40 points)
   - All API contracts implemented
   - All domain types implemented
   - All business logic implemented
   - All database schema implemented

2. **Spec Compliance** (40 points)
   - Code matches spec exactly
   - No deviations from spec
   - No contradictions with spec
   - No extra functionality beyond spec

3. **Design Alignment** (10 points)
   - Aligns with feature design
   - Uses correct domain types
   - Uses correct API endpoints

4. **Test Coverage** (10 points)
   - All spec requirements tested
   - All tests passing
   - Edge cases covered

**Pass Criteria**: 100/100 (all checks must pass)

---

## Completion Criteria

Validation complete when:

- [ ] All spec requirements implemented (40 pts)
- [ ] Code matches spec exactly (40 pts)
- [ ] No deviations or contradictions
- [ ] Aligns with feature design (10 pts)
- [ ] All spec tests passing (10 pts)
- [ ] Validation report generated
- [ ] Score: 100/100

---

## Common Issues

### Issue: Code Deviates from Spec

**Resolution**: 
- Option 1: Update code to match spec
- Option 2: Update spec if deviation is justified, then re-validate change

### Issue: Missing Spec Requirements

**Resolution**: Complete implementation, update tasks.md checklist

### Issue: Extra Functionality Not in Spec

**Resolution**: Remove extra code or update spec to include it

---

## Auto-Validation

**This workflow runs automatically after workflow 10**

**Trigger**: After `10-openspec-change-implement.md` completes

**Behavior**:
- If validation passes → Suggest workflow 11
- If validation fails → Report issues, block workflow 11

---

## Next Activities

After validation:

1. **If Validation Passes**: Proceed to `11-openspec-change-complete.md`

2. **If Validation Fails**: 
   - Fix code to match spec, or
   - Update spec if justified, then re-run workflow 10

---

## References

- **Feature Design**: `../DESIGN.md` - Feature requirements
- **Change Specs**: `changes/{change-id}-{name}/specs/` - Technical specs
- **Adapter**: `../../../FDD-Adapter/AGENTS.md` - Project commands
