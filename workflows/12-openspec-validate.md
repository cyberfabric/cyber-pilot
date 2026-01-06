# Validate OpenSpec Structure

**Phase**: 3 - Feature Development  
**Purpose**: Validate OpenSpec directory structure and specifications consistency

**Structure Requirements**: See `../requirements/openspec-change-structure.md` for complete change structure specification

---

## Prerequisites

- OpenSpec initialized for feature
- OpenSpec directory exists: `openspec/` (project root)

## Input Parameters

- **slug**: Feature identifier (lowercase, kebab-case)

**Note**: Before validating, read `../requirements/openspec-change-structure.md` to understand expected change structure

---

## Requirements

### 1: Run OpenSpec Validation

**Requirement**: Use OpenSpec tool to validate entire structure

**Command**:
```bash
# Run from project root (not from openspec/ directory)
openspec validate --all --no-interactive
```

**What This Validates**:
- Directory structure (specs/, changes/ exist)
- All active changes have required files
- Change numbering is sequential
- Status consistency across files
- Spec files are valid markdown
- No empty or malformed files
- Source of truth integrity

**Expected Outcome**: Validation passes with no errors

**Resolution if Failed**: Fix reported issues, then re-run validation

---

### 2: Review Validation Results

**Requirement**: Understand and address any validation issues

**OpenSpec Output Shows**:
- ✅ Passed checks (green)
- ⚠️  Warnings (yellow) 
- ❌ Errors (red)

**Common Issues**:
- Missing files → Create required files
- Empty specs → Fill in specifications
- Status mismatch → Sync status across files
- Numbering gaps → Renumber changes sequentially
- Invalid markdown → Fix spec file format

**Expected Outcome**: All errors resolved, warnings reviewed

---

### 3: List Changes with OpenSpec

**Requirement**: Verify change status and progress

**Commands**:
```bash
# List active changes
openspec list

# List archived changes
openspec list --archived

# Show specific change
openspec show {change-id}
```

**What to Verify**:
- Active changes listed correctly
- Status is accurate for each
- Archived changes properly moved
- No orphaned or lost changes

**Expected Outcome**: Complete and accurate change inventory

---

### 4: Verify Specs Integrity

**Requirement**: Ensure source of truth specs are valid

**What OpenSpec Checks**:
- All specs in `specs/` directory
- Specs are valid markdown
- Source attribution present
- No duplicate or conflicting specs

**Manual Review** (if needed):
- Check specs make sense
- Verify technical accuracy
- Confirm completeness

**Expected Outcome**: Source of truth is reliable

---

### 5: Validate Specs Against Feature Design

**Requirement**: Auto-discover Feature DESIGN.md from spec names and validate against it

**Step 1: Discover Feature Design Files**

For each spec in OpenSpec, extract feature slug and locate DESIGN.md:

**Process**:
1. List all specs using `openspec list --specs`
2. For each spec starting with "fdd-":
   - Extract feature slug from format: `fdd-{project-name}-feature-{feature-slug}`
   - Example: `fdd-fdd-cli-feature-init` → feature-slug = `init`
3. Locate Feature DESIGN.md at `architecture/features/feature-{slug}/DESIGN.md`
4. Verify file exists

**Expected Results**:
- ✓ Found: Feature DESIGN.md for each spec
- ❌ Missing: Report missing DESIGN.md files

**Step 2: Validate Spec Requirements Against Section F**

For each discovered Feature DESIGN.md:

**Load Requirements**: Read Feature DESIGN.md Section F (Requirements)

**Check Merged Spec**: `openspec/specs/$spec/spec.md` (source of truth)

**Check Delta Specs**: Active changes in `openspec/changes/*/specs/$spec/spec.md`

**What to Verify for Merged Specs** (`openspec/specs/$spec/spec.md`):
- ✅ All requirements from Section F are present
- ✅ Requirement IDs match between DESIGN.md and spec.md
- ✅ No requirements that aren't in Section F
- ✅ Requirement descriptions align with Section F

**What to Verify for Delta Specs** (`openspec/changes/*/specs/$spec/spec.md`):
- ✅ ADDED requirements align with new Section F requirements
- ✅ MODIFIED requirements reference existing Section F requirements
- ✅ REMOVED requirements exist in Section F (with deprecation reason)
- ✅ RENAMED requirements maintain ID traceability
- ✅ Delta spec changes match what's described in change `proposal.md`

**Delta Spec Format Check**:
```
## ADDED Requirements
{New requirements from Section F}

## MODIFIED Requirements  
{Changed requirements - full text with updates}

## REMOVED Requirements
{Deprecated requirements with reason}

## RENAMED Requirements
{Name changes only - ID must match}
```

**Step 3: Validate Changes Against Section G**

For each Feature DESIGN.md:

**Load Implementation Plan**: Read Feature DESIGN.md Section G (Implementation Plan)

**What to Verify**:
- ✅ All changes from Section G exist in `openspec/changes/` or `openspec/changes/archive/`
- ✅ Change numbering matches Section G plan
- ✅ Change scope matches Section G descriptions
- ✅ No extra changes that aren't in Section G
- ✅ Each change `proposal.md` references Section F requirements
- ✅ Change tasks align with Section E (Technical Details)

**Expected Outcome**: Complete traceability for all FDD specs

**Validation Criteria**:
- ✅ All specs with `fdd-` prefix have corresponding Feature DESIGN.md
- ✅ All Section F requirements present in spec.md
- ✅ All Section G changes exist in OpenSpec
- ✅ All active/archived changes listed in Section G
- ✅ Each change proposal references DESIGN.md sections
- ❌ Specs without Feature DESIGN.md
- ❌ Requirements mismatch between Section F and spec.md
- ❌ Orphaned changes not in Section G

**Resolution if Failed**:
- Missing DESIGN.md → Create Feature Design (workflow 05, 06)
- Requirements mismatch → Update Section F or spec.md
- Changes mismatch → Update Section G or remove orphaned changes

---

### 6: Output Validation Results

**Requirement**: Display validation results in chat (DO NOT create report files)

**⚠️ CRITICAL**: Output results directly in chat, DO NOT create VALIDATION_REPORT.md or similar files

**Output Format**:
```markdown
# OpenSpec Validation Results

**Validation Date**: {timestamp}

## Structure Status
- Directory structure: ✅/❌
- Required directories present: ✅/❌
- Archive structure: ✅/❌

## Changes Status
- Active changes: {count}
- Archived changes: {count}
- All changes have required files: ✅/❌
- Change numbering sequential: ✅/❌
- Status consistency: ✅/❌

## Specifications Status
- Source of truth specs: {count}
- Spec files valid: ✅/❌
- No conflicts: ✅/❌

## Traceability Status
- All DESIGN.md changes exist: ✅/❌
- All changes traceable: ✅/❌
- No orphaned changes: ✅/❌

## Validation Score: {X}/100

{If issues found, list them here}
```

**Expected Outcome**: Validation results displayed in chat with comprehensive information

---

## Validation Scoring

**Target Score**: All checks must pass (100%)

**Validation Categories**:
1. **Structure** (20 points)
   - Directory structure exists and valid
   - Required directories present (specs/, changes/)
   - Archive structure correct

2. **Changes** (20 points)
   - All changes have required files (proposal.md, tasks.md, specs/)
   - Change numbering sequential
   - Status consistent across files

3. **Specifications** (20 points)
   - Spec files valid markdown
   - Source of truth specs valid
   - No conflicting or duplicate specs

4. **Traceability** (30 points)
   - All changes from feature DESIGN.md Section G exist
   - All changes traceable to feature design
   - Change proposals reference design sections
   - No orphaned or unplanned changes

5. **Integrity** (10 points)
   - No orphaned files
   - No broken references
   - Validation report generated

**Pass Criteria**: 100/100 (all checks must pass)

---

## Completion Criteria

Validation complete when:

- [ ] Directory structure valid (20 pts)
- [ ] All changes have proposal.md, tasks.md, specs/ (20 pts)
- [ ] Change numbering sequential
- [ ] Status consistent across files
- [ ] Spec files valid markdown (20 pts)
- [ ] Source of truth specs valid
- [ ] All planned changes from DESIGN.md Section G exist (30 pts)
- [ ] All changes traceable to feature design
- [ ] Change proposals reference design sections
- [ ] No orphaned or unplanned changes
- [ ] No broken references (10 pts)
- [ ] Validation results output to chat (NO report files created)
- [ ] Score: 100/100

---

## Common Challenges

### Issue: Missing Required Files

**Resolution**: Create missing files following templates in `09-openspec-change-next.md`

### Issue: Status Mismatch

**Resolution**: Synchronize status across proposal.md and tasks.md

### Issue: Empty Spec Files

**Resolution**: Fill in specs or remove empty files

---

## When to Run

**Regular Validation**:
- Before completing a change
- Before completing a feature
- During code review

**Troubleshooting**:
- When OpenSpec structure seems corrupted
- After manual changes to openspec/
- When merging branches

---

## Next Activities

After validation:

1. **Fix Issues**: Address any errors or warnings

2. **Continue Work**: If validation passes
   - Continue implementation
   - Complete changes

3. **Report**: Share validation report with team if needed

---

## References

- **Core FDD**: `../AGENTS.md` - OpenSpec integration
- **OpenSpec**: https://openspec.dev - Framework docs
- **Related Workflows**: `09-openspec-change-next.md`, `10-openspec-change-implement.md`, `11-openspec-change-complete.md`
