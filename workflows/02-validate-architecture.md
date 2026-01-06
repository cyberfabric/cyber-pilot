# Validate Overall Design

**Phase**: 1 - Architecture Design  
**Purpose**: Validate Overall Design (DESIGN.md) completeness and structure

**⚠️ CRITICAL**: This workflow is a validation wrapper. All validation criteria are defined in `../requirements/overall-design-structure.md`. Read that file first before proceeding.

---

## AI Agent Instructions

### Step 1: Read Requirements File

**Action**: Read `../requirements/overall-design-structure.md` in full

**Purpose**: Load complete validation criteria including:
- File location and size requirements
- Required sections and subsections structure
- Content validation criteria for each section
- Validation scoring methodology
- Output format requirements

### Step 2: Validate Against Requirements

**Action**: Validate `architecture/DESIGN.md` against ALL criteria from requirements file

**Validation Process**:
1. Check file-level validation (existence, size)
2. Check structure validation (sections A-D, subsections C.1-C.5)
3. Check content validation (domain model, API contracts, completeness)
4. Calculate score according to requirements scoring system
5. Generate validation report in chat (not as file)

**Report Format** (from requirements):
- Score: X/100 (must be ≥90)
- Completeness: X% (must be 100%)
- Issues: List of missing/invalid items
- Recommendations: What to fix

### Step 3: Determine Next Action

**If validation passes** (score ≥90, completeness 100%):
- ✅ Suggest next workflow: `03-init-features.md` or `04-validate-features.md`

**If validation fails**:
- ❌ List specific issues from requirements that failed
- Provide actionable recommendations to fix
- User must fix issues and re-run validation

---

## Validation Checklist

All criteria are defined in `../requirements/overall-design-structure.md`. Use this checklist to ensure nothing is missed:

- [ ] Read requirements file completely
- [ ] File-level validation (from requirements)
- [ ] Structure validation (from requirements)
- [ ] Content validation (from requirements)
- [ ] Scoring (from requirements)
- [ ] Report generation (in chat, per requirements)

---

## References

**Primary Source**: `../requirements/overall-design-structure.md`

**Related Workflows**:
- `01-init-project.md` - Generate Overall Design (uses same requirements)
- `03-init-features.md` - Next step after validation passes

**Related Requirements** (future):
- `feature-design-structure.md` - Feature DESIGN.md validation
- `adapter-structure.md` - Adapter validation

---

---

## End of Workflow

**Remember**: All validation logic is in `../requirements/overall-design-structure.md`. This workflow is just a thin wrapper that instructs you to read and apply those requirements.
