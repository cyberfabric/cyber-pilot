# Validate Feature Design

**Phase**: 3 - Feature Development  
**Purpose**: Validate Feature DESIGN.md completeness and compliance with FDD requirements

**⚠️ CRITICAL**: This workflow is a validation wrapper. All validation criteria are defined in `../requirements/feature-design-structure.md`. Read that file first before proceeding.

---

## AI Agent Instructions

### Step 1: Read Requirements File

**Action**: Read `../requirements/feature-design-structure.md` in full

**Purpose**: Load complete validation criteria including:
- File location and size requirements
- Required sections structure (A-G)
- FDL syntax requirements (reference `../FDL.md`)
- Content validation criteria for each section
- Cross-validation with Overall Design
- Validation scoring methodology
- Output format requirements

### Step 2: Read FDL Specification

**Action**: Read `../FDL.md` in full

**Purpose**: Understand FDL syntax for validating Sections B, C, D, F (Testing Scenarios)
- Valid FDL keywords
- Prohibited keywords
- FDL format rules

### Step 3: Validate Against Requirements

**Action**: Validate `architecture/features/feature-{slug}/DESIGN.md` against ALL criteria from requirements file

**Validation Process**:
1. Check file-level validation (existence, size ≤4000 lines)
2. Check structure validation (sections A-G present, correct order)
3. Check content validation (FDL syntax, no code, sufficient detail)
4. Check cross-validation (alignment with Overall Design)
5. Check completeness (no placeholders, no type redefinitions)
6. Calculate score according to requirements scoring system
7. Generate validation report in chat (not as file)

**Report Format** (from requirements):
- Score: X/100 (must be 100)
- Completeness: X% (must be 100%)
- Issues: List of missing/invalid items
- Recommendations: What to fix

### Step 4: Determine Next Action

**If validation passes** (score 100, completeness 100%):
- ✅ Suggest next workflow: `09-openspec-change-next.md`

**If validation fails**:
- ❌ List specific issues from requirements that failed
- Provide actionable recommendations to fix
- User must fix issues and re-run validation

---

## Input Parameters

- **slug**: Feature identifier (lowercase, kebab-case)
  - Example: `dashboard-mgmt`, `user-auth`

---

## Validation Checklist

All criteria are defined in `../requirements/feature-design-structure.md`. Use this checklist to ensure nothing is missed:

- [ ] Read requirements file completely
- [ ] Read FDL.md for syntax rules
- [ ] File-level validation (from requirements)
- [ ] Structure validation (from requirements)
- [ ] Content validation (from requirements)
- [ ] Cross-validation with Overall Design (from requirements)
- [ ] Completeness check (from requirements)
- [ ] Scoring (from requirements)
- [ ] Report generation (in chat, per requirements)

---

## References

**Primary Source**: `../requirements/feature-design-structure.md`

**Related Specifications**:
- `../FDL.md` - FDL syntax for flows, algorithms, states
- `../../DESIGN.md` - Overall Design for cross-validation

**Related Workflows**:
- `05-init-feature.md` - Generate feature DESIGN.md (uses same requirements)
- `09-openspec-change-next.md` - Next step after validation passes

**Related Requirements** (same level):
- `overall-design-structure.md` - Overall Design validation

---

## End of Workflow

**Remember**: All validation logic is in `../requirements/feature-design-structure.md`. This workflow is just a thin wrapper that instructs you to read and apply those requirements.

---

## Common Issues (Quick Reference)

See requirements file for full details. Common fixes:

**Section B/C has code blocks**: Convert to FDL (see `../FDL.md`)

**Invalid FDL keywords**: Use only valid keywords from `../FDL.md`
- ✅ Allowed: **IF**, **FOR EACH**, **WHILE**, **TRY/CATCH**, **RETURN**
- ❌ Prohibited: **WHEN** (in flows), **THEN**, **SET**, **VALIDATE**

**Gherkin in Testing Scenarios**: Replace with plain English
- ❌ **GIVEN/WHEN/THEN** → ✅ "User provides", "System parses", "Verify"

**Type definitions found**: Remove, reference Overall Design types instead

---

## Completion Validation (From Requirements)

Per `../requirements/feature-design-structure.md`:

**Target Score**: 100/100 + 100% completeness

**Must Pass**:
- File ≤4000 lines (recommended ≤3000)
- All sections A-G present
- FDL syntax valid (no code)
- No type redefinitions
- No TODO/TBD markers
- Cross-validation with Overall Design passes

---
