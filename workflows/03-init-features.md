# Initialize Features from Overall Design

**Phase**: 2 - Feature Planning  
**Purpose**: Analyze Overall Design and generate feature list with dependencies through interactive review

---

## Prerequisites

- Overall Design validated (run `02-validate-architecture.md` first)
- `architecture/DESIGN.md` complete with all sections
- `architecture/features/` directory exists

---

## Overview

This workflow analyzes the Overall Design, proposes a feature breakdown based on capabilities, and generates the features manifest after user review and confirmation.

**Key Principle**: Analyze, propose, review, confirm before creating.

---

## Requirements

### 1. Analyze System Capabilities

**Requirement**: Extract and understand core capabilities from Overall Design

**Input Source**:
- Section A (Business Context → Core Capabilities) of `architecture/DESIGN.md`
- Section B (Requirements & Principles) for business rules
- Project name from document title

**Analysis Actions**:
1. Read `architecture/DESIGN.md`
2. Extract all capabilities from Section A
3. Identify business rules from Section B
4. Understand capability relationships
5. Determine foundational vs. dependent capabilities

**Display Analysis**:
```
Capability Analysis:
───────────────────
Project: {PROJECT_NAME}

Capabilities found:
1. {Capability 1}
2. {Capability 2}
3. {Capability 3}
...

Key business rules:
- {Rule 1}
- {Rule 2}
...
```

**Expected Outcome**: Clear understanding of system capabilities

**Validation Criteria**:
- All capabilities from Section A extracted
- Business rules identified
- Capability relationships understood

---

### 2. Propose Feature Breakdown

**Requirement**: Analyze capabilities and propose feature breakdown

**Planning Guidelines**:
- **First feature**: Always `feature-init` (infrastructure, no dependencies)
- **Capability mapping**: Create 1-3 features per major capability  
- **Feature scope**: Each feature focused and independently testable
- **Dependencies**: Define clear dependency relationships
- **Priority**: CRITICAL for init and core features, HIGH/MEDIUM/LOW for others

**Feature Naming**:
- Format: `feature-{descriptive-name}`
- Lowercase with hyphens  
- Descriptive of functionality

**Auto-Generate Proposal**:
```
Proposed Feature Breakdown:
──────────────────────────

### 1. feature-init (CRITICAL)
**Purpose**: Initialize project structure
**Scope**:
- Create compilable skeleton
- Set up framework integration
- Establish layer structure
**Depends On**: None
**Status**: NOT_STARTED

{For each capability, propose 1-3 features}
### {N}. feature-{derived-from-capability} ({PRIORITY})
**Purpose**: {Derived from capability description}
**Scope**:
- {Scope item 1 based on capability}
- {Scope item 2}
- {Scope item 3}
**Depends On**: {feature-init or other features}
**Status**: NOT_STARTED

──────────────────────────
Total Features: {COUNT}
Estimated Implementation Order: {init} → {feature2} → {feature3}...
```

**Expected Outcome**: Feature breakdown proposal generated

**Validation Criteria**:
- All capabilities covered by features
- feature-init is first
- Dependencies form valid DAG
- Each feature has clear scope

---

### 3. Review and Confirm Feature Breakdown

**Requirement**: User reviews and confirms or adjusts proposed features

**Interactive Review**:
```
Review the proposed feature breakdown above.

Options:
  1. Approve and proceed with generation
  2. Suggest modifications (describe changes)
  3. Cancel

Your choice: ___
```

**If option 2 (Suggest modifications)**:
```
Describe the modifications you'd like:
- Add feature: ___
- Remove feature: ___  
- Modify feature {name}: ___
- Change dependencies: ___
- Change priorities: ___
```

**After modifications**:
- Apply user changes to proposal
- Show updated breakdown
- Ask for confirmation again

**Expected Outcome**: User-approved feature breakdown

**Validation Criteria**:
- User explicitly approved
- feature-init remains first
- Dependencies still form valid DAG

---

### 4. Create Features Manifest Document

**Requirement**: Document all planned features in structured manifest

**Required File**: `architecture/features/FEATURES.md`

**Required Content Structure**:

**Header**:
- Module name
- Overall status (PLANNING initially)

**For Each Feature**:
- **Feature slug**: Unique identifier (e.g., `feature-init`)
- **Status**: Current state (⏳ NOT_STARTED, 🔄 IN_PROGRESS, ✅ IMPLEMENTED)
- **Priority**: Importance level (CRITICAL, HIGH, MEDIUM, LOW)
- **Depends On**: List of prerequisite features or "None"
- **Blocks**: List of features that depend on this feature or "None" (calculated from reverse "Depends On" relationships)
- **Purpose**: One-line description of feature goal
- **Scope**: Bulleted list of what feature creates/implements

**Additional Sections**:
- **Feature Dependencies**: Visual dependency graph
- **Implementation Order**: Numbered list in execution order

**Critical Requirements**:
- `feature-init` MUST be feature #1
- init MUST have "Depends On: None"
- Dependencies must form valid DAG (no cycles)
- Implementation order must respect dependencies

**Expected Outcome**: Complete feature manifest ready for implementation

**Validation Criteria**:
- File `architecture/features/FEATURES.md` exists
- All features documented with required fields
- init is first feature
- Dependency graph is acyclic
- Implementation order valid

---

### 5. Initialize Init Design Document

**Requirement**: Create design document for init feature

**Required File**: `architecture/features/feature-init/DESIGN.md`

**Content Requirements**:
- **Section A**: Feature context (minimal for init)
- **Section B**: Actor flows (intentionally minimal - structural task, in FDL)
- **Section C**: Algorithms (intentionally minimal - structural task, in FDL)
- **Section D**: States (in FDL if needed, typically not applicable for init)
- **Section E**: Technical details (structure being created)
- **Section F**: Validation & implementation (compilation tests)
- **Section G**: Requirements (minimal for init - structural requirements)
- **Section H**: Implementation Plan (changes for init structure)

**Critical Constraints**:
- Init is **structural only** - NO business logic
- Minimal sections B and C acceptable for init
- Focus on what structure is created, not what it does

**Note**: Framework-specific init templates defined in project adapter documentation

**Expected Outcome**: Init design document exists

**Validation Criteria**:
- File `architecture/features/feature-init/DESIGN.md` exists
- Contains all sections A-H
- Clearly defines structural scope
- No business logic described

**Commands**:
```bash
mkdir -p features/feature-init

# Generic init template
cat > features/feature-init/DESIGN.md << 'EOF'
# Init - Feature Design

**Status**: ⏳ NOT_STARTED  
**Module**: {Module Name}

---

## A. Feature Context

### Overview

Create minimal project structure. This establishes the compilable skeleton for business features.

**Critical Scope Constraint**: Init creates **structure only**, NO business logic.

### Purpose

Initialize the project with:
- Empty compilable structure
- Framework integration
- Layer folders ready for features

### Actors

- **Developer/Architect**: Creates project structure

### References

- Overall Design: `@/architecture/DESIGN.md`

### What Init IS vs IS NOT

**Init creates** (✅):
- Project structure
- Configuration scaffolding
- Empty layers/folders

**Init does NOT create** (❌):
- Business logic
- API definitions
- Database entities
- Any domain-specific code

---

## B. Actor Flows

*Intentionally minimal for init.*

Developer runs init → creates skeleton → verifies compilation.

---

## C. Algorithms

*Intentionally minimal for init.*

See implementation for details.

---

## D. States

*Not applicable for init* (use FDL if needed - see `../FDL.md`)

---

## E. Technical Details

### Structure Created

(Framework-specific - see adapter documentation)

---

## F. Validation & Implementation

### Testing

1. **Compilation Test**: Verify structure compiles
2. **Integration Test**: Verify framework registration

---

## G. Requirements

### Requirement R001: Project Structure Initialization

**Status**: ⏳ NOT_STARTED

**Description**: The system SHALL create compilable project structure with framework integration.

**References**:
- [Overall Design](../../DESIGN.md)

**Testing Scenarios** (FDL):

**Test: Successful Project Initialization**

1. Developer opens empty project directory
2. Developer runs init command
3. **IF** command succeeds:
   1. Project structure is created
   2. All folders exist
4. Developer runs build command
5. **IF** build succeeds:
   1. Project compiles successfully
   2. No errors reported

**Acceptance Criteria**:
- Project compiles without errors
- Framework properly configured
- All structural folders created

---

## H. Implementation Plan

### Change 001: Initialize Project Structure

**Status**: ⏳ NOT_STARTED

**Description**: Create minimal compilable project structure

**Implements Requirements**:
- [R001: Project Structure Initialization](#requirement-r001-project-structure-initialization)

**Dependencies**: None

---
EOF
```

**Expected Result**: Init DESIGN.md created

**Note**: For framework-specific init templates, see project adapter documentation

---

### 6. Create Placeholder Design Documents

**Requirement**: Initialize design documents for all other features

**Required Files**:
- One DESIGN.md per feature in `architecture/features/feature-{slug}/`
- Exclude init (already created in previous requirement)

**Content Requirements**:
- Basic template with sections A-H
- Status: ⏳ NOT_STARTED
- Placeholder text indicating design pending
- Reference to Overall Design

**Purpose**: Establish feature structure, content filled during feature initialization workflow

**Expected Outcome**: All feature directories have initial DESIGN.md

**Validation Criteria**:
- Each feature has directory `architecture/features/feature-{slug}/`
- Each directory contains `DESIGN.md`
- Files have basic structure
- Status marked as NOT_STARTED

**Commands**:
```bash
# For each feature (except init)
for FEATURE in feature-{name} feature-{name2}; do
  mkdir -p features/$FEATURE
  
  cat > features/$FEATURE/DESIGN.md << EOF
# {Feature Name} - Feature Design

**Status**: ⏳ NOT_STARTED

## A. Feature Context

### Overview

{To be designed after Overall Design is finalized}

### Purpose

{Define purpose}

---

## B. Actor Flows

{To be designed}

---

## C. Algorithms

{To be designed}

---

## D. States

{To be designed if needed - use FDL, see `../FDL.md`}

---

## E. Technical Details

{To be designed}

---

## F. Validation & Implementation

{To be designed}

---

## G. Requirements

{To be designed - formalized requirements with references to B-E}

---

## H. Implementation Plan

{To be designed - OpenSpec changes with status}

---
EOF
done
```

**Expected Result**: Placeholder designs created

---

### 7. Show Summary

**Requirement**: Display what was created

**Display Summary**:
```
Feature Initialization Complete!
────────────────────────────────
Project: {PROJECT_NAME}

Created:
✓ architecture/features/FEATURES.md
  - {COUNT} features defined
  - Dependencies mapped
  - Implementation order established

✓ architecture/features/feature-init/DESIGN.md
  - Init feature design created

✓ Placeholder designs for {COUNT-1} features:
  {List other feature slugs}

Implementation Order:
1. feature-init (CRITICAL)
2. {feature 2}
3. {feature 3}
...

Next Steps:
1. Start with feature-init: Run workflow 05-init-feature feature-init
2. Complete init design and validate
3. Follow implementation order from FEATURES.md
```

**Expected Outcome**: Summary displayed

---

### 8. Validate Features Manifest Structure

**Action**: Run validation on FEATURES.md

**Commands**:
```bash
# Check init is first
FIRST_FEATURE=$(grep "^### [0-9]\." features/FEATURES.md | head -1)
if ! echo "$FIRST_FEATURE" | grep -q "feature-init"; then
  echo "ERROR: init must be first feature"
  exit 1
fi

# Check dependencies valid
echo "✓ init is first feature"
echo "✓ Features manifest created"
```

**Expected Result**: Validation passes

---

## Completion Criteria

Feature initialization is complete when:

- [ ] Capabilities analyzed from Overall Design
- [ ] Feature breakdown proposed automatically
- [ ] User reviewed and approved feature breakdown
- [ ] FEATURES.md created with all approved features:
  - [ ] feature-init is first feature (CRITICAL priority)
  - [ ] All features have: status, priority, dependencies, blocks, purpose, scope
  - [ ] Blocks field consistent with Depends On (reverse dependencies)
  - [ ] Dependencies form valid DAG (no cycles)
- [ ] feature-init/DESIGN.md created with content
- [ ] Placeholder designs created for other features
- [ ] Summary displayed showing what was created
- [ ] Next steps communicated to user

---

## Common Challenges

### Challenge: Feature Granularity

**Resolution**: Each feature should be implementable in 1-4 weeks. If larger, break into multiple features. If smaller, consider combining. Aim for 3-7 initial features.

### Challenge: Complex Dependencies

**Resolution**: Create dependency diagram before documenting. Ensure no circular dependencies. If dependencies complex, may indicate need for feature restructuring.

### Challenge: Unclear Feature Boundaries

**Resolution**: Each feature should have single clear purpose. If feature scope unclear, likely combining multiple concerns. Split into separate features.

---

## Next Activities

After feature initialization:

1. **Develop Init**: Start feature development workflow for init
   - Complete init DESIGN.md
   - Validate design
   - Implement structure

2. **Develop Remaining Features**: Follow implementation order from manifest
   - Initialize next feature
   - Complete design
   - Validate
   - Implement

---

## References

- **Core FDD**: `../AGENTS.md` - Feature planning
- **Next Workflow**: `04-validate-features.md` then `05-init-feature.md`
