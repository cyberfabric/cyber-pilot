# Initialize Feature

**Phase**: 3 - Feature Development  
**Purpose**: Start work on a specific feature by initializing its design through guided questions

**Structure Requirements**: See `../requirements/feature-design-structure.md` for complete Feature Design structure specification

---

## AI Agent Instructions

**MANDATORY**: Before executing this workflow, you MUST read the following specification files:

1. **Read `../requirements/feature-design-structure.md`** - Complete structure specification
   - Understand all required sections (A-G) and their content requirements
   - Understand size constraints and validation criteria
   - Use this as the source of truth for structure

2. **Read `../FDL.md`** - Complete FDL syntax specification
   - Understand valid FDL keywords for flows, algorithms, and state machines
   - Use this when generating Sections B, C, D, F (Testing Scenarios)
   - Apply FDL syntax rules from `../FDL.md` directly

**Key Points**:
- Generate according to structure defined in `../requirements/feature-design-structure.md`
- Use FDL syntax from `../FDL.md` for behavioral content
- Reference Overall Design types (never redefine)
- No placeholders - generate meaningful content

---

## Prerequisites

- Features manifest exists: `architecture/features/FEATURES.md`
- Feature listed in manifest
- All feature dependencies have validated designs (DESIGN.md complete)

---

## Overview

This workflow initializes a feature by gathering context through interactive questions, then generates a Feature Design document with meaningful starter content instead of empty placeholders.

**Key Principle**: Ask questions, generate initial content, make it easy to continue.

---

## Interactive Questions

Ask the user these questions **one by one** to gather requirements:

### Q1: Feature Slug
```
What is the slug for this feature? (lowercase, kebab-case)
Example: "user-auth", "payment-flow", "dashboard-view"
```
**Store as**: `FEATURE_SLUG`

### Q2: Feature Name
```
What is the human-readable name for this feature?
Example: "User Authentication", "Payment Processing Flow", "Analytics Dashboard"
```
**Store as**: `FEATURE_NAME`

### Q3: Feature Purpose
```
What does this feature do and why does it exist?
Describe in 2-3 sentences.

Example: "This feature handles user login and authentication. 
It validates credentials, creates sessions, and manages authentication tokens. 
The goal is to provide secure access control for the application."
```
**Store as**: `FEATURE_PURPOSE`

### Q4: Primary Actors
```
Who are the primary actors that interact with this feature?
List 1-3 actors with their roles:

Example:
- End User: Logs in and accesses protected resources
- Administrator: Manages user accounts and permissions
```
**Store as**: `ACTORS[]` (each with name and role)

### Q5: Main Flows
```
What are the 1-3 main actor flows for this feature?
Briefly describe each flow:

Example:
- User Login: User enters credentials, system validates, creates session
- Password Reset: User requests reset, receives email, sets new password
```
**Store as**: `MAIN_FLOWS[]` (each with name and brief description)

### Q6: Initial Requirements
```
What are 2-4 key requirements for this feature?
List them as complete sentences describing system behavior:

Example:
1. The system SHALL register an `fdd init` command that accepts optional project path
2. The system SHALL validate the target directory is empty or doesn't exist
3. The system SHALL generate architecture directory structure with templates
```
**Store as**: `REQUIREMENTS[]` (each requirement as full sentence)

### Q7: Estimated Changes
```
How many implementation changes do you estimate?
Each change implements 1-5 requirements.

Options:
  1. Small (1-2 changes)
  2. Medium (3-4 changes)
  3. Large (5-8 changes)
  4. Custom (specify number)
```
**Store as**: `CHANGES_COUNT`

---

## Requirements

### 1. Verify Feature Exists and Read Manifest Data

**Requirement**: Feature must be documented in FEATURES.md and extract metadata

**Required Actions**:
- Verify feature slug exists in `architecture/features/FEATURES.md`
- Extract feature metadata from manifest:
  - Feature description
  - Dependencies
  - Status
- Read project name from Overall Design

**Expected Outcome**: Feature verified and metadata collected

**Validation Criteria**: 
- Feature slug found in manifest
- Dependencies identified
- Project name retrieved

---

### 2. Verify Dependency Status

**Requirement**: All feature dependencies must have validated designs

**Dependency Check**:
- Extract "Depends On" from feature entry in FEATURES.md
- If "None" - proceed (no dependencies)
- If dependencies listed - verify each has validated DESIGN.md (passed workflow 06)

**Expected Outcome**: Prerequisites satisfied

**Validation Criteria**: All dependencies have complete and validated designs

---

### 3. Establish Feature Directory

**Requirement**: Feature must have dedicated directory

**Required Directory**: `architecture/features/feature-{slug}/`

**Expected Outcome**: Directory exists

**Validation Criteria**: Directory path accessible

---

### 4. Generate Feature Design Document

**Requirement**: Create DESIGN.md with actual content from collected answers

**Required File**: `architecture/features/feature-{slug}/DESIGN.md`

**Structure Source**: `../requirements/feature-design-structure.md`

**Instructions**:
1. Read `../requirements/feature-design-structure.md` to understand complete Feature Design structure
2. Generate DESIGN.md following the structure from requirements file
3. Populate sections A-G with content derived from interactive answers (Q1-Q7)
4. Use FDL syntax for sections B, C, D (reference `../FDL.md`)

**Content Mapping**:
- Q1 (FEATURE_SLUG) → Directory name, file metadata
- Q2 (FEATURE_NAME) → Section A (Overview, Purpose)
- Q3 (FEATURE_PURPOSE) → Section A (Purpose statement)
- Q4 (ACTORS[]) → Section A (Actors list)
- Q5 (MAIN_FLOWS[]) → Section B (Actor Flows in FDL)
- Q6 (REQUIREMENTS[]) → Section G (Requirements with Testing Scenarios)
- Q7 (CHANGES_COUNT, CHANGES[]) → Section H (Implementation Plan)

**Generation Notes**:
- Follow structure exactly as defined in `feature-design-structure.md`
- Use FDL syntax for sections B, C, D (reference `../FDL.md`)
- Keep initial content minimal but meaningful (not placeholders like "{To be designed}")
- Generate realistic starter content derived from user answers
- Mark status as 🔄 IN_PROGRESS

**Expected Result**: DESIGN.md with complete structure and initial content ready for detailed design

**Validation Criteria**:
- File contains actual content from Q2-Q7
- Actor names and roles filled from Q4
- Flow descriptions filled from Q5
- Requirements listed in Section G from Q6
- Changes count in Section H matches Q7
- No empty placeholders like "[TODO]"
- Document ready for user to expand with details

---

### 5. Show Summary and Confirm

**Requirement**: Display what will be created and get user confirmation

**Display Summary**:
```
Feature Initialization Summary:
───────────────────────────────
Feature: {FEATURE_NAME}
Slug: {FEATURE_SLUG}

Will create:
✓ architecture/features/feature-{FEATURE_SLUG}/
  ✓ DESIGN.md (with initial content)

DESIGN.md will include:
- Purpose: {first 60 chars of FEATURE_PURPOSE}...
- {count} actors
- {count} main flows
- {count} requirements from Q6
- {CHANGES_COUNT} implementation changes from Q7
{If dependencies: "- Dependencies: {list}"}

Feature status will change: NOT_STARTED → IN_PROGRESS

Proceed with initialization? (y/n)
```

**Expected Outcome**: User confirms or cancels

**Validation Criteria**:
- Summary shows all content to be created
- User can review before proceeding
- Easy to abort if needed

---

### 6. Update Feature Status

**Requirement**: Mark feature as IN_PROGRESS in manifest

**Status Change**: ⏳ NOT_STARTED → 🔄 IN_PROGRESS

**Location**: Feature entry in `architecture/features/FEATURES.md`

**Expected Outcome**: Manifest reflects active development

**Validation Criteria**: Feature status shows IN_PROGRESS

---

## Completion Criteria

Feature initialization complete when:

- [ ] User answered all questions (Q1-Q6)
- [ ] User confirmed initialization summary
- [ ] Feature verified in FEATURES.md
- [ ] Dependencies verified (if any)
- [ ] Feature directory created: `architecture/features/feature-{FEATURE_SLUG}/`
- [ ] DESIGN.md generated with actual content from answers:
  - [ ] Section A: Feature Context (overview, purpose, actors)
  - [ ] Section B: Actor Flows (initial flow descriptions from Q5)
  - [ ] Section C: Algorithms (placeholders based on flows)
  - [ ] Section E: Technical Details (placeholders)
  - [ ] Section F: Requirements (from Q6, references to B-E, includes Testing Scenarios in FDL)
  - [ ] Section G: Implementation Plan (changes from Q7, implementing requirements)
- [ ] Feature status updated: NOT_STARTED → IN_PROGRESS
- [ ] No empty placeholders like "[TODO]" in generated content
- [ ] Document ready for user to expand with detailed FDL and technical specs

---

## Common Challenges

### Issue: Dependencies Not Met

**Resolution**: Complete and validate dependency designs first (workflow 06). Design order should follow dependency graph in FEATURES.md

### Issue: Feature Not in Manifest

**Resolution**: Add to FEATURES.md first using `03-init-features.md`

---

## Next Activities

After initialization:

1. **Fill in DESIGN.md**: Complete all sections A-H
   - Define actors and flows (Section B - PRIMARY)
   - Describe algorithms in FDL (Section C)
   - Document technical details (Section E)
   - Complete requirements with phases (Section G)
   - Detail implementation changes (Section H)

2. **Validate Design**: Run `06-validate-feature.md {slug}`
   - Must pass 100/100 + 100% completeness
   - Fix issues and re-validate

3. **Start Implementation**: After validation passes
   - Run `09-openspec-change-next.md {slug}`
   - Implement changes
   - Complete feature

---

## References

- **Core FDD**: `../AGENTS.md` - Feature Design structure
- **FDL Spec**: `../FDL.md` - FDL syntax (flows, algorithms, states)
- **Next Workflow**: `06-validate-feature.md`
