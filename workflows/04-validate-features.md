# Validate Features Manifest

**Phase**: 2 - Feature Planning  
**Purpose**: Validate FEATURES.md manifest completeness and consistency

**⚠️ CRITICAL**: This workflow is a validation wrapper. All validation criteria are defined in `../requirements/features-manifest-structure.md`. Read that file first before proceeding.

---

## AI Agent Instructions

### Step 1: Read Requirements File

**Action**: Read `../requirements/features-manifest-structure.md` in full

**Purpose**: Load complete validation criteria including:
- File location and format
- Required structure (header, feature list)
- Feature entry format and required fields
- Status consistency rules
- Dependency validation rules
- Cross-validation with Overall Design

### Step 2: Validate Against Requirements

**Action**: Validate `architecture/features/FEATURES.md` against ALL criteria from requirements file

**Validation Process**:
1. Check file-level validation (existence, content)
2. Check structure validation (header, feature list format)
3. Check content validation (directories exist, dependencies valid, status consistency)
4. Check cross-validation (alignment with Overall Design capabilities)
5. Generate validation report in chat (not as file)

**Report Format** (from requirements):
- Issues: List of missing/invalid items
- Recommendations: What to fix

### Step 3: Determine Next Action

**If validation passes**:
- ✅ Suggest next workflow: `05-init-feature.md` (initialize first feature)

**If validation fails**:
- ❌ List specific issues from requirements that failed
- Provide actionable recommendations to fix
- User must fix issues and re-run validation

---

## Prerequisites

- `architecture/features/FEATURES.md` exists
- At least one feature defined

## Input Parameters

None (validates entire FEATURES.md)

**Note**: Before validating, read `../requirements/features-manifest-structure.md` to understand expected manifest structure

---

## Validation Checklist

All criteria are defined in `../requirements/features-manifest-structure.md`. Use this checklist to ensure nothing is missed:

- [ ] Read requirements file completely
- [ ] File-level validation (from requirements)
- [ ] Structure validation (from requirements)
- [ ] Content validation (from requirements)
- [ ] Cross-validation with Overall Design (from requirements)
- [ ] Report generation (in chat, per requirements)

---

## References

**Primary Source**: `../requirements/features-manifest-structure.md`

**Related Specifications**:
- `overall-design-structure.md` - Overall Design (source of capabilities)

**Related Workflows**:
- `03-init-features.md` - Generate FEATURES.md (uses same requirements)
- `05-init-feature.md` - Initialize individual feature

---

## End of Workflow

**Remember**: All validation logic is in `../requirements/features-manifest-structure.md`. This workflow is just a thin wrapper that instructs you to read and apply those requirements.
