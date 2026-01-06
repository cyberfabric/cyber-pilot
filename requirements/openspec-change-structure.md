# OpenSpec Change Structure Requirements

**Purpose**: Define required structure for OpenSpec changes in `openspec/changes/{change-name}/`

**Used by**:
- Workflow 09 (openspec-change-next): Create new OpenSpec change
- Workflow 12 (openspec-validate): Validate OpenSpec structure

**Note**: OpenSpec changes are atomic implementation units (1-5 requirements per change)

---

## Naming Convention

**Spec Name Format**: `fdd-{project-name}-{feature-slug}-feature`

**Components**:
- `fdd-` - Prefix indicating FDD methodology
- `{project-name}` - Project name in kebab-case (from project context)
- `-{feature-slug}-` - Feature identifier
- `feature` - Suffix indicating feature specification

**Example**: `fdd-payment-system-user-auth-feature`

---

## Change Directory Structure

**Location**: `openspec/changes/{change-name}/`

**Change Name Requirement**: 
- **MUST match** change name defined in Feature DESIGN.md Section G (Implementation Plan)
- Format: `fdd-{project-name}-feature-{feature-slug}-change-{short-name}`
- This ensures traceability from Feature Design to OpenSpec implementation

**Required files**:
1. `proposal.md` - Change description and justification
2. `tasks.md` - Implementation tasks checklist
3. `specs/{spec-name}/spec.md` - Technical specification for feature
   - `{spec-name}` MUST follow Spec Name Format: `fdd-{project-name}-{feature-slug}-feature`
   - Example: `specs/fdd-payment-system-user-auth-feature/spec.md`
4. `design.md` - Reference file to Feature DESIGN.md (required)

---

## File: proposal.md

**Purpose**: Describe what will be changed and why

**Required sections**:
1. **Change Name**: Unique identifier (kebab-case)
   - **MUST match exactly** the change name in Feature DESIGN.md Section G
   - Format: `fdd-{project-name}-feature-{feature-slug}-change-{short-name}`
   - **MUST be clickable link** to Feature DESIGN.md Section G
   - Format: `[change-name](../../architecture/features/feature-{slug}/DESIGN.md#section-g-implementation-plan)`
2. **Feature**: Feature slug this change belongs to
   - **MUST match** the feature slug from Feature DESIGN.md directory name
   - Example: if DESIGN.md is in `feature-user-auth/`, Feature must be `user-auth`
   - **MUST be clickable link** to Feature DESIGN.md
   - Format: `[feature-slug](../../architecture/features/feature-{slug}/DESIGN.md)`
3. **Implements Requirements**: List of requirement IDs from Feature DESIGN.md Section F
   - **MUST use exact requirement IDs** from Section F (not invented or paraphrased)
   - Format: `fdd-{project-name}-feature-{feature-slug}-req-{short-name}`
   - Each ID must exist in Feature DESIGN.md Section F
   - **Each ID MUST be clickable link** to Feature DESIGN.md Section F
   - Format: `[req-id](../../architecture/features/feature-{slug}/DESIGN.md#section-f-requirements)`
4. **Description**: Clear description of what will be implemented
5. **Justification**: Why this change is needed
6. **Dependencies**: Other changes this depends on (or "None")
7. **Status**: ⏳ NOT_STARTED, 🔄 IN_PROGRESS, or ✅ COMPLETED

**Validation**:
- Change Name matches Feature DESIGN.md Section G exactly
- Feature slug matches feature directory
- Implements 1-5 requirements
- All requirement IDs exist in Feature DESIGN.md Section F
- Dependencies are valid change names from Section G

---

## File: tasks.md

**Purpose**: Checklist of implementation tasks

**Format**: Markdown checklist with task descriptions

**Requirements**:
- ≥3 tasks per change
- Tasks specific and actionable
- Clear completion criteria
- No vague tasks like "Implement feature"

**Example**:
```markdown
- [ ] Create domain type definitions
- [ ] Implement validation logic
- [ ] Add unit tests
- [ ] Update API documentation
```

---

## File: specs/{spec-name}/spec.md

**Path Format**: `specs/{spec-name}/spec.md`
- `{spec-name}` MUST follow Spec Name Format: `fdd-{project-name}-{feature-slug}-feature`
- Example: `specs/fdd-payment-system-user-auth-feature/spec.md`

**Purpose**: Technical specification for implementation

**Required sections**:
1. **Overview**: What this spec defines
   - **MUST include clickable link** to Feature DESIGN.md
   - Format: `[Feature DESIGN.md](../../architecture/features/feature-{slug}/DESIGN.md)`
   - This provides context and traceability to feature requirements
2. **Domain Model Changes**: Types/schemas added or modified
3. **API Changes**: Endpoints added or modified
4. **Implementation Notes**: Technical details for developers
5. **Testing Requirements**: What must be tested

**Validation**:
- Directory name matches Spec Name Format exactly
- Spec name matches feature being implemented
- References Feature DESIGN.md sections
- No contradictions with Overall Design
- Sufficient detail for implementation

---

## File: design.md

**Purpose**: Reference file linking to Feature DESIGN.md

**Agent Instruction**:
- **MUST READ** Feature DESIGN.md before working on this change
- **MUST include link**: `[Feature DESIGN.md](../../architecture/features/feature-{slug}/DESIGN.md)`
- This file serves as a reference pointer to ensure agents read the source Feature DESIGN.md

**Content**: Link to Feature DESIGN.md and any implementation-specific notes if needed

**Required**: This file must be created for every OpenSpec change to enforce design context awareness

---

## Change Lifecycle

**States**:
1. **⏳ NOT_STARTED**: Change created, not yet started
2. **🔄 IN_PROGRESS**: Implementation in progress
3. **✅ COMPLETED**: Implementation finished, tested, archived

**State transitions**:
- NOT_STARTED → IN_PROGRESS: Start implementation (workflow 10)
- IN_PROGRESS → COMPLETED: Complete implementation (workflow 11)

**Archive location**: `openspec/changes/archive/{change-name}/`

---

## Validation Criteria

### File-Level Validation

1. **Required files exist**
   - `proposal.md` exists
   - `tasks.md` exists
   - `specs/{feature-slug}/spec.md` exists

2. **Directory structure**
   - Change directory: `openspec/changes/{change-name}/`
   - Spec directory: `openspec/changes/{change-name}/specs/{feature-slug}/`

### Content Validation

1. **proposal.md**
   - All required sections present
   - Implements 1-5 requirements
   - Feature slug valid
   - Requirements exist in feature DESIGN.md
   - Dependencies valid

2. **tasks.md**
   - ≥3 tasks present
   - Tasks specific and actionable
   - Checklist format valid

3. **spec.md**
   - All required sections present
   - References feature DESIGN.md
   - No contradictions with Overall Design
   - Sufficient implementation detail

### Cross-Validation

1. **With Feature Design**
   - Feature slug matches `architecture/features/feature-{slug}/`
   - Requirements exist in Feature DESIGN.md Section F
   - No contradictions with feature design

2. **With Overall Design**
   - Domain model changes reference Overall Design types
   - API changes reference Overall Design contracts
   - No new types/endpoints without Overall Design update

3. **With Other Changes**
   - Dependencies are valid change names
   - No circular dependencies
   - Implementation order is clear

---

## Merged Specs Location

**After completion**: Changes merged to `openspec/specs/{feature-slug}/`

**Format**: One spec file per feature combining all completed changes

**Validation**:
- All active changes merged
- No conflicts between changes
- Spec is implementation-ready

---

## Output Requirements

### For Generator (Workflow 09)

**Generate**:
- Change directory structure
- `proposal.md` with all required sections
- `tasks.md` with initial task checklist
- `specs/{spec-name}/spec.md` with technical specification
- `design.md` with link to Feature DESIGN.md (reference file)

### For Validator (Workflow 12)

**Validate**:
1. File structure (all required files present)
2. Content completeness (all required sections)
3. Cross-validation (feature design, overall design, dependencies)
4. Status consistency (change states valid)

**Report format**:
- Issues: List of missing/invalid items
- Recommendations: What to fix

---

## References

**Workflows using this**:
- `workflows/09-openspec-change-next.md` - Create OpenSpec change
- `workflows/10-openspec-change-implement.md` - Implement change
- `workflows/11-openspec-change-complete.md` - Complete and archive change
- `workflows/12-openspec-validate.md` - Validate OpenSpec structure

**Related specifications**:
- `feature-design-structure.md` - Feature Design structure (Section F: Requirements, Section G: Implementation Plan)
- `overall-design-structure.md` - Overall Design structure

**External specification**:
- `../openspec/AGENTS.md` - Complete OpenSpec specification
