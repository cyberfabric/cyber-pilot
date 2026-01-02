# Fix Design Issue

**Phase**: 3 - Feature Development  
**Purpose**: Fix design issues discovered during implementation

---

## Prerequisites

- Feature is IN_PROGRESS or IMPLEMENTED
- Design issue identified (missing detail, incorrect logic, etc.)
- Feature directory exists: `architecture/features/feature-{slug}/`

## Input Parameters

- **slug**: Feature identifier (lowercase, kebab-case)
- **issue**: Description of design issue to fix

---

## Requirements

### 1: Document Issue

**Requirement**: Record design issue before making changes

**Location**: `architecture/features/feature-{slug}/DESIGN_ISSUES.md`

**Required Information**:
- **Issue Title**: Brief description
- **Date**: When discovered
- **Discovered During**: Implementation phase (e.g., coding, testing)
- **Problem**: Detailed description of what's wrong or missing
- **Impact**: What this affects (implementation, testing, other features)
- **Proposed Solution**: How to fix it

**Expected Outcome**: Issue documented for tracking and future reference

**Validation Criteria**:
- Issue clearly described
- Impact assessment included
- Solution approach outlined

---

### 2: Update DESIGN.md

**Requirement**: Make necessary changes to design document

**Manual Step**: Edit DESIGN.md to fix the issue

**Guidelines**:
- Update relevant sections (A-F)
- Maintain section structure
- Keep FDL syntax in Section C (see `../FDL.md`)
- Update OpenSpec changes if needed

**Example Changes**:
- Add missing actor flow (Section B)
- Clarify algorithm steps (Section C)
- Add missing technical details (Section E)
- Define new error cases

---

### 3: Validate Updated Design

**Requirement**: Re-run design validation after changes

**Validation Steps**: Follow workflow `06-validate-feature.md` for feature `{slug}`

**Expected Outcome**: Design validation passes 100/100 + 100% completeness

**Validation Criteria**:
- All sections A-F still compliant
- Size constraints met
- FDL syntax correct
- No TODO/TBD markers
- No type redefinitions
- Changes don't break existing validation rules

---

### 4: Update OpenSpec if Needed

**Requirement**: Assess if implementation must change due to design fix

**Decision Criteria**:
- **No code changes needed**: Design clarification only, continue with existing implementation
- **Minor code changes needed**: Update existing OpenSpec change tasks
- **Major code changes needed**: Create new OpenSpec change (use workflow `12-openspec-change-next.md`)

**Expected Outcome**: Implementation plan aligned with updated design

**Validation Criteria**:
- Design changes mapped to implementation impact
- OpenSpec reflects any necessary code changes
- Dependencies between changes updated if needed

**Note**: Pure design clarifications may not require code changes

---

### 5: Document Resolution

**Requirement**: Record how issue was resolved

**Location**: Append to same issue in `DESIGN_ISSUES.md`

**Required Information**:
- **Resolution Date**: When fixed
- **Changes Made**: List changes by section (A-F)
- **Validation Status**: Confirmation validation passed (100/100)
- **Implementation Impact**: None / Minor / Major
- **Related OpenSpec Changes**: IDs if implementation affected

**Expected Outcome**: Complete audit trail of issue and resolution

**Validation Criteria**:
- Resolution clearly documented
- All changes listed by section
- Validation status confirmed
- Implementation impact assessed

---

### 6: Notify Team (Optional)

**Requirement**: If working in team, notify about design changes

**Manual Step**: 
- Update team via communication channel
- Review changes with stakeholders if significant
- Update documentation references if needed

---

## Completion Criteria

Design fix complete when:

- [ ] Issue documented in DESIGN_ISSUES.md
- [ ] DESIGN.md updated to fix issue
- [ ] Design validation passes (100/100)
- [ ] OpenSpec updated if implementation affected
- [ ] Resolution documented
- [ ] Team notified (if applicable)

---

## Common Challenges

### Issue: Validation Fails After Changes

**Resolution**: Review validation errors, fix issues iteratively. May need multiple update cycles.

### Issue: Breaking Changes to Implementation

**Resolution**: Create new OpenSpec change to handle implementation updates. May need to revert some code.

### Issue: Unclear What to Fix

**Resolution**: Consult with team, review Overall Design, check similar features for patterns.

---

## Design Issue Categories

### 1. Missing Detail

**Example**: Actor flow too vague  
**Fix**: Add detailed steps, error scenarios

### 2. Incorrect Logic

**Example**: Algorithm has logical flaw  
**Fix**: Rewrite algorithm in Section C

### 3. Incomplete Technical Details

**Example**: Security requirements missing  
**Fix**: Add to Section E

### 4. Scope Creep

**Example**: Feature trying to do too much  
**Fix**: Split into multiple features, update FEATURES.md

### 5. Missing Error Cases

**Example**: No handling for edge case  
**Fix**: Add error scenarios to Section B, update Section E

---

## When to Fix vs Start Over

**Fix Design (this workflow)**:
- Minor clarifications
- Adding missing details
- Fixing logical errors
- Improving existing content

**Start New Feature**:
- Major scope change
- Complete redesign
- Different approach entirely
- Would invalidate most of current design

---

## Next Activities

After fixing design:

1. **Continue Implementation**: If in progress
   - Apply design changes to code
   - Update tests if needed
   - Complete remaining work

2. **Re-implement**: If major changes
   - May need to refactor code
   - Update OpenSpec changes
   - Re-run tests

3. **Complete Feature**: After fixes applied
   - Run: `07-complete-feature.md {slug}`

---

## References

- **Core FDD**: `../AGENTS.md` - Design iteration
- **Validation**: `06-validate-feature.md` - Re-validate after changes
- **OpenSpec**: `09-openspec-init.md` - If implementation needs updates
