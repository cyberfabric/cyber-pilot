# Initialize Features from Overall Design

**Phase**: 2 - Feature Planning  
**Purpose**: Analyze Overall Design and generate feature list with dependencies through interactive review

**Structure Requirements**: See `../requirements/features-manifest-structure.md` for complete FEATURES.md structure specification

---

## Prerequisites

- Overall Design validated (run `02-validate-architecture.md` first)
- `architecture/DESIGN.md` complete with all sections
- `architecture/features/` directory exists

**Note**: Before generating FEATURES.md, read `../requirements/features-manifest-structure.md` to understand manifest structure

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

### 3. User Review and Confirmation (MANDATORY)

**Requirement**: User MUST review and explicitly approve feature breakdown before generation

**⚠️ CRITICAL**: AI agent MUST NOT proceed to Step 4 (file generation) without explicit user approval. This is a mandatory checkpoint.

**Interactive Review**:
```
Review the proposed feature breakdown above.

Options:
  1. Approve and proceed with generation
  2. Suggest modifications (describe changes)
  3. Cancel

Your choice: ___
```

**After modifications**:
- Apply user changes to proposal
- Show updated breakdown
- Ask for confirmation again (loop until approved or cancelled)

**If option 3 (Cancel)**:
- Stop workflow immediately
- Do not create any files
- Exit workflow

**Expected Outcome**: User explicitly typed "1" or "Approve" to confirm

**Validation Criteria**:
- User explicitly approved (option 1 selected)
- feature-init remains first
- Dependencies still form valid DAG
- **BLOCKED**: Cannot proceed without approval

---

### 4. Create Features Manifest Document

**Requirement**: Document all planned features in structured manifest

**Required File**: `architecture/features/FEATURES.md`

**Structure Specification**: See `../requirements/features-manifest-structure.md` for complete FEATURES.md structure requirements

**Critical Requirements**:
- `feature-init` MUST be feature #1
- init MUST have "Depends On: None"
- Dependencies must form valid DAG (no cycles)
- All features have clickable dependency links

**Expected Outcome**: Complete feature manifest ready for implementation per requirements specification

---

### 5. Create Feature DESIGN.md Stubs

**Requirement**: Create DESIGN.md stub for each feature using template from requirements

**Source**: `../requirements/feature-design-structure.md`

**Process**:
1. Read `../requirements/feature-design-structure.md` to understand Feature Design structure
2. For each feature in the proposed list:
   - Create directory: `architecture/features/feature-{slug}/`
   - Create stub: `architecture/features/feature-{slug}/DESIGN.md`
   - Use structure from requirements file
   - Mark all sections as `{To be designed}` except basic metadata

**Special Case - feature-init**:
- Init is **structural only** - NO business logic
- Sections B and C intentionally minimal
- Focus on what structure is created, not what it does
- See adapter documentation for framework-specific init templates

**Expected Outcome**: Each feature has DESIGN.md stub following requirements structure

**Validation Criteria**:
- Each feature directory has `DESIGN.md`
- All DESIGN.md files follow structure from `feature-design-structure.md`
- Stubs contain correct metadata (status, module name)
- No duplication of requirements file content

---

### 6. Summary and Next Steps

**Requirement**: Confirm completion and guide next actions

**Expected Outcome**: User understands what was created and what to do next

**Validation Criteria**:
- All features have DESIGN.md stubs following `feature-design-structure.md`
- FEATURES.md manifest is complete
- User knows next workflow to run

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

**Action**: Validate FEATURES.md structure and ordering

**Validation Requirements**:
- **First feature check**: feature-init must be the first numbered feature entry
- **Dependencies check**: All feature dependencies reference existing features
- **Format check**: All features follow the structure defined in `../requirements/features-manifest-structure.md`

**Expected Result**: 
- ✓ feature-init is first feature in manifest
- ✓ All dependencies are valid
- ✓ Features manifest structure is correct

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
