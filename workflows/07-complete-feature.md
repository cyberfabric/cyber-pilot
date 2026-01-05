# Complete Feature

**Phase**: 3 - Feature Development  
**Purpose**: Mark feature as complete after all implementation is done

---

## Prerequisites

- Feature is IN_PROGRESS
- All OpenSpec changes implemented and archived
- All tests passing
- Feature fully functional

## Input Parameters

- **slug**: Feature identifier (lowercase, kebab-case)

---

## Requirements

### 1: Verify All Changes Complete

**Requirement**: All OpenSpec changes must be completed and archived

**Location**: `openspec/` (project root)

**Validation Criteria**:
- No active changes for this feature in `openspec/changes/`
- All changes listed in Section G are ✅ COMPLETED
- All requirements from Section F present in `openspec/specs/fdd-{project-name}-feature-{feature-slug}/spec.md`
- No changes with status ⏳ NOT_STARTED or 🔄 IN_PROGRESS

**Tools**: 
- Use `openspec list` from `openspec/` directory
- Use `openspec validate {feature-slug}` to verify spec

**Expected Outcome**: Zero pending OpenSpec changes

**Resolution if Failed**: Complete remaining changes using workflows 10 and 11

---

### 2: Run Final Design Validation

**Requirement**: Design validation must pass one final time

**Validation**: Execute workflow `06-validate-feature.md` for feature `{slug}`

**Expected Outcome**: Validation score 100/100 + 100% completeness

**Validation Criteria**:
- All sections A-G compliant
- Section F: All requirements documented
- Section G: All changes marked ✅ COMPLETED
- No validation errors
- Design matches implementation

**Resolution if Failed**: Fix design issues using workflow `08-fix-design.md` before marking complete

---

### 3: Verify Tests

**Requirement**: All feature tests must pass

**Test Coverage**:
- Unit tests for feature components
- Integration tests for feature flows
- End-to-end tests if applicable
- All test scenarios from Section F (Requirements) validated

**Expected Outcome**: 100% tests passing, zero failures

**Framework Examples** (reference only):
- Rust: `cargo test`
- Node.js: `npm test`
- Python: `pytest`
- Java: `mvn test`
- Go: `go test`

**Resolution if Failed**: Fix failing tests before marking complete

---

### 4: Verify Compilation/Build

**Requirement**: Code must compile/build without errors

**Validation Criteria**:
- No compilation errors
- No type errors
- No syntax errors
- All dependencies resolved
- Build process succeeds

**Expected Outcome**: Clean build with zero errors

**Framework Examples** (reference only):
- Rust: `cargo check`
- TypeScript: `tsc --noEmit`
- Python: `mypy` or `pyright`
- Java: `mvn compile`
- Go: `go build`

**Critical**: This prevents marking incomplete work as done

**Resolution if Failed**: Fix compilation errors before proceeding

---

### 5: Update FEATURES.md Status

**Requirement**: Update feature status to IMPLEMENTED

**Location**: `architecture/features/FEATURES.md`

**Status Change**: 🔄 IN_PROGRESS → ✅ IMPLEMENTED

**Update Requirements**:
- Find feature entry for `feature-{slug}`
- Change status emoji and text
- Preserve all other feature information
- Maintain formatting and links

**Expected Outcome**: Feature shows status ✅ IMPLEMENTED

**Validation Criteria**:
- Status updated correctly
- No formatting broken
- Feature still listed in correct order

---

### 6: Identify Unblocked Features

**Requirement**: Identify features that can now start

**Analysis**:
- Review this feature's "Blocks" field in `FEATURES.md` to see which features it blocks
- Check those features' "Depends On" fields to verify all dependencies are met
- Identify features that are now fully unblocked

**Expected Outcome**: List of features that are now unblocked

**Next Steps**:
- Prioritize newly unblocked features
- Verify all their dependencies are satisfied
- Start highest priority unblocked feature next

---

### 7: Verify OpenSpec Spec Complete

**Requirement**: OpenSpec spec must contain all feature requirements

**Location**: `openspec/specs/fdd-{project-name}-feature-{feature-slug}/spec.md`

**Required Content**:
- Spec file exists for feature
- All requirements from DESIGN.md Section F are present
- All scenarios documented
- Spec validates successfully

**Validation Criteria**:
- File `openspec/specs/fdd-{project-name}-feature-{feature-slug}/spec.md` exists
- Contains all requirements from Section F
- No ADDED/MODIFIED/REMOVED markers (fully merged)
- Spec structure valid

**Expected Outcome**: Complete, merged spec for feature

**Tools**: 
- Run `openspec validate {feature-slug}` from `openspec/` directory
- Compare spec.md requirements to DESIGN.md Section F

---

### 8: Update Feature Status in Header

**Requirement**: Update status in DESIGN.md header

**Location**: `architecture/features/feature-{slug}/DESIGN.md` - header section (lines 1-5)

**Status Update**:
```markdown
# {Feature Name} - Feature Design

**Status**: ✅ IMPLEMENTED  
**Module**: {module-name}
```

**What to Change**:
- Status line: Update from `🔄 IN_PROGRESS` to `✅ IMPLEMENTED`

**Expected Outcome**: Feature header reflects IMPLEMENTED status

**Validation Criteria**:
- Status line updated in header (top of file)
- No additional completion sections added elsewhere
- Header formatting preserved

**Note**: Section G (Implementation Plan) should list all changes with ✅ COMPLETED status

---

## Completion Criteria

Feature completion verified when:

- [ ] All changes in Section G marked ✅ COMPLETED
- [ ] All Section F requirements in openspec/specs/fdd-{project-name}-feature-{feature-slug}/spec.md
- [ ] Design validation passes (100/100 + 100%)
- [ ] Tests passing
- [ ] Code compiles without errors
- [ ] FEATURES.md status = IMPLEMENTED
- [ ] Dependent features identified
- [ ] OpenSpec spec complete and valid
- [ ] Completion note in DESIGN.md

---

## Common Challenges

### Issue: Tests Failing

**Resolution**: Fix tests before marking complete. Feature is not done if tests fail.

### Issue: OpenSpec Changes Not Complete

**Resolution**: Complete and archive remaining changes:
```bash
# Run from project root
openspec list  # Check active changes
openspec archive {change-name} -y  # Archive completed change
```

**Note**: All changes must be archived and specs merged to `openspec/specs/fdd-{project-name}-feature-{feature-slug}/`

---

## Next Activities

After completing feature:

1. **Review FEATURES.md**: Check for next feature to implement
   - Look at implementation order
   - Verify dependencies met

2. **Start Next Feature**: Run `05-init-feature.md {next-slug}`
   - Or start dependent feature that's now unblocked

3. **Update Documentation**: If needed
   - Update Overall Design
   - Update architecture diagrams

---

## References

- **Core FDD**: `../AGENTS.md` - Completion criteria
- **Next Workflow**: `05-init-feature.md` for next feature
