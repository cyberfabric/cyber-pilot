# Features Manifest Structure Requirements

**Purpose**: Define required structure for `architecture/features/FEATURES.md`

**Used by**:
- Workflow 03 (init-features): Generate FEATURES.md from Overall Design
- Workflow 04 (validate-features): Validate FEATURES.md completeness

---

## File Location

**Path**: `architecture/features/FEATURES.md`

**Purpose**: Central manifest tracking all features in the project

---

## Required Structure

### Header Section

**Project metadata**:
```markdown
# Features: {PROJECT_NAME}

**Status Overview**: X features total (Y completed, Z in progress, W not started)
```

**Status summary** showing feature breakdown by status

---

### Feature List Section

**Format**: Numbered sections with subsections

**Required per feature**:
1. **Section heading**: `### N. [feature-slug](feature-slug/) EMOJI PRIORITY`
   - N: Sequential number (1, 2, 3, ...)
   - Slug: Lowercase kebab-case
   - Emoji: ⏳ (NOT_STARTED), 🔄 (IN_PROGRESS), ✅ (IMPLEMENTED)
   - Priority: CRITICAL, HIGH, MEDIUM, LOW

2. **Purpose**: `**Purpose**: One-line description`

3. **Status**: `**Status**: NOT_STARTED | IN_PROGRESS | IMPLEMENTED`

4. **Depends On**: `**Depends On**: comma-separated clickable links to feature directories or "None"`
   - Format: `[feature-slug](feature-slug/)` for each dependency
   - Multiple dependencies: `[feature-a](feature-a/), [feature-b](feature-b/)`
   - Links must be clickable and navigable

5. **Blocks**: `**Blocks**: comma-separated clickable links to feature directories or "None"`
   - Format: `[feature-slug](feature-slug/)` for each blocked feature
   - Multiple blocks: `[feature-a](feature-a/), [feature-b](feature-b/)`
   - Links must be clickable and navigable

6. **Scope**: `**Scope**:` followed by bulleted list

**Example**:
```markdown
### 1. [feature-user-auth](feature-user-auth/) ⏳ CRITICAL
**Purpose**: User authentication and authorization  
**Status**: NOT_STARTED  
**Depends On**: None  
**Blocks**: [feature-user-profile](feature-user-profile/), [feature-notifications](feature-notifications/)  
**Scope**:
- Login/logout flows
- JWT token management
- Password reset

---

### 2. [feature-user-profile](feature-user-profile/) ⏳ HIGH
**Purpose**: User profile management  
**Status**: NOT_STARTED  
**Depends On**: [feature-user-auth](feature-user-auth/)  
**Blocks**: None  
**Scope**:
- Profile CRUD operations
- Avatar upload
- Settings management
```

---

## Validation Criteria

### File-Level Validation

1. **File exists**
   - `architecture/features/FEATURES.md` exists
   - File has substantive content

2. **Header present**
   - Project name in title
   - Status overview present

### Structure Validation

1. **Feature list present**
   - ≥1 feature defined
   - All features have required fields

2. **Feature entry format**
   - Status emoji valid (⏳🔄✅)
   - Slug is kebab-case
   - Design path exists
   - Dependencies reference valid features

### Content Validation

1. **Feature directories exist**
   - Each feature has directory: `architecture/features/feature-{slug}/`
   - DESIGN.md exists in each feature directory (if status ≠ NOT_STARTED)

2. **Dependencies valid**
   - All dependency slugs reference existing features
   - No circular dependencies (DAG structure)
   - Dependency order is implementable

3. **Status consistency**
   - Feature status matches DESIGN.md existence
   - IN_PROGRESS features have DESIGN.md
   - IMPLEMENTED features have complete DESIGN.md

### Cross-Validation with Overall Design

1. **Feature alignment**
   - Features derived from Overall Design capabilities
   - Feature scope matches Overall Design
   - No features contradict Overall Design

2. **Completeness**
   - All Overall Design capabilities covered by features
   - No orphaned features (not mapped to capabilities)

---

## Status Lifecycle

**Feature states**:
1. **⏳ NOT_STARTED**: Feature planned, no DESIGN.md yet
2. **🔄 IN_PROGRESS**: DESIGN.md exists, implementation not complete
3. **✅ IMPLEMENTED**: All OpenSpec changes completed, feature validated

**State transitions**:
- NOT_STARTED → IN_PROGRESS: Start feature design (workflow 05)
- IN_PROGRESS → IMPLEMENTED: Complete all changes (workflow 07)

---

## Generation Guidelines

### For Generator (Workflow 03)

**Input**: Overall Design capabilities (Section A)

**Process**:
1. Extract capabilities from Overall Design
2. Identify foundational vs. dependent features
3. Propose feature breakdown
4. User reviews and confirms
5. Generate FEATURES.md with all entries
6. Create feature directories

**Output**:
- `FEATURES.md` with all features listed
- Feature directories created
- All features in NOT_STARTED status initially

### For Validator (Workflow 04)

**Validate**:
1. File-level (exists, has content)
2. Structure (header, feature list format)
3. Content (directories exist, dependencies valid)
4. Cross-validation (alignment with Overall Design)

**Report format**:
- Issues: List of missing/invalid items
- Recommendations: What to fix

---

## Dependency Rules

1. **Acyclic**: No circular dependencies allowed
2. **Valid references**: All dependencies must exist in manifest
3. **Implementation order**: Dependencies must be implemented before dependents
4. **Foundation first**: Core/infrastructure features have no dependencies

---

## Example FEATURES.md

```markdown
# Features Manifest: my-project

**Status**: PLANNING

**Last Updated**: 2026-01-06

---

## Features List

### 1. [feature-user-auth](feature-user-auth/) ✅ CRITICAL
**Purpose**: User authentication and authorization  
**Status**: IMPLEMENTED  
**Depends On**: None  
**Blocks**: feature-user-profile, feature-notifications  
**Scope**:
- Login/logout flows
- JWT token management
- Password reset
- Session management

---

### 2. [feature-data-storage](feature-data-storage/) ✅ CRITICAL
**Purpose**: Data persistence layer  
**Status**: IMPLEMENTED  
**Depends On**: None  
**Blocks**: feature-user-profile, feature-reporting  
**Scope**:
- Database schema setup
- Repository pattern implementation
- Connection pooling
- Migration system

---

### 3. [feature-user-profile](feature-user-profile/) 🔄 HIGH
**Purpose**: User profile management  
**Status**: IN_PROGRESS  
**Depends On**: feature-user-auth, feature-data-storage  
**Blocks**: feature-reporting  
**Scope**:
- Profile CRUD operations
- Avatar upload
- Settings management
- Profile validation

---

### 4. [feature-notifications](feature-notifications/) ⏳ MEDIUM
**Purpose**: Notification system  
**Status**: NOT_STARTED  
**Depends On**: feature-user-auth  
**Blocks**: None  
**Scope**:
- Email notifications
- In-app notifications
- Notification preferences
- Delivery queue

---

### 5. [feature-reporting](feature-reporting/) ⏳ LOW
**Purpose**: Analytics and reporting  
**Status**: NOT_STARTED  
**Depends On**: feature-data-storage, feature-user-profile  
**Blocks**: None  
**Scope**:
- Report generation
- Data aggregation
- Export functionality
- Scheduled reports
```

---

## References

**Workflows using this**:
- `workflows/03-init-features.md` - Generate FEATURES.md
- `workflows/04-validate-features.md` - Validate FEATURES.md

**Related specifications**:
- `overall-design-structure.md` - Overall Design (source of capabilities)
- `feature-design-structure.md` - Feature Design structure

**Related workflows**:
- `workflows/05-init-feature.md` - Initialize individual feature
- `workflows/07-complete-feature.md` - Mark feature as IMPLEMENTED
