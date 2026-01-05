# Initialize Feature

**Phase**: 3 - Feature Development  
**Purpose**: Start work on a specific feature by initializing its design through guided questions

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

**Generated Content**:
```markdown
# {FEATURE_NAME from Q2} - Feature Design

**Status**: 🔄 IN_PROGRESS  
**Module**: {PROJECT_NAME from manifest}

---

## A. Feature Context

### Overview

{FEATURE_NAME from Q2}: {Brief from FEATURES.md manifest}

### Purpose

{FEATURE_PURPOSE from Q3}

### Actors

{For each actor in ACTORS[] from Q4}
- **{Actor Name}**: {Actor role from Q4}

### References

**MANDATORY Reading**:
- Overall Design: `@/architecture/DESIGN.md`
- FEATURES.md: `@/architecture/features/FEATURES.md`

**Dependencies**:
{If dependencies from manifest}
- {List each dependent feature}
{Else}
- None

---

## B. Actor Flows

{For each flow in MAIN_FLOWS[] from Q5}
### Flow: {Flow Name}

**Actor**: {Primary actor from ACTORS[]}

**Brief**: {Flow description from Q5}

**Steps** (to be detailed in FDL):
1. {First step based on flow description}
2. System processes request
3. {Result based on flow description}

**Success Scenario**:
- {Expected outcome}

**Error Scenarios**:
- To be defined during design

---

## C. Algorithms

**Note**: Algorithms will be defined in FDL during feature design.

{Generate 1-2 algorithm placeholders based on MAIN_FLOWS}
### Algorithm: {Derived from flow name}

**Purpose**: {Based on flow description}

**Steps** (in FDL): To be defined

---

## D. States

{If feature involves state transitions}
**Note**: Define state machines if applicable.
{Else}
N/A - This feature does not require state machine modeling.

---

## E. Technical Details

### Database Schema

**Tables/Entities**: To be defined

### API Endpoints

**Endpoints** (reference Overall Design API specification): To be defined

### Security

**Authorization**: {Reference security model from Overall Design}

### Error Handling

**Errors**: To be defined

---

## F. Validation & Implementation

### Testing Scenarios

{For each flow, generate basic test scenario}
1. **{Flow name} - Happy Path**:
   - Given: {Initial state}
   - When: {Action from flow}
   - Then: {Expected result}

---

## G. Requirements

**Note**: Requirements formalize the scope by combining flows, algorithms, states, and technical details.

{Generate 1-2 example requirements based on flows and Q6}
### Requirement R{001}: {Requirement Name from Q6}

**Status**: ⏳ NOT_STARTED

**Description**: {Requirement description from Q6}

**References**:
- [Flow: {Flow Name}](#flow-{flow-slug})
- [Algorithm: {Algorithm Name}](#algorithm-{algo-slug})
{If technical details referenced}
- [Technical: {Detail}](#technical-details)

**Testing Scenarios** (FDL):

**Test: {Success case}**

1. {Set up initial state}
2. {Actor} performs {action}
3. **IF** {operation succeeds}:
   1. {Verify expected outcome}
   2. {Verify side effects}
4. {Assert result is correct}

**Test: {Error case}**

1. {Set up error condition}
2. {Actor} performs {action}
3. **TRY**:
   1. {Execute operation}
4. **CATCH** {ErrorType}:
   1. {Verify error handling}
   2. {Verify system state}

**Acceptance Criteria**:
- {Derive from requirement description}
- {Add 1-2 more criteria}

{Repeat for each requirement from Q6}

---

## H. Implementation Plan

**Total Changes**: {CHANGES_COUNT from Q7}

{Generate placeholders for each change}
### Change 001: {Infer name from first 1-2 requirements}

**Status**: ⏳ NOT_STARTED

**Description**: To be defined during detailed design

**Implements Requirements**:
- [R001: {Requirement name}](#requirement-r001)
{If multiple requirements: add more}

**Dependencies**: None

**Effort**: To be estimated

**Verification**: To be defined

---

{Repeat for remaining changes}

---

**Document Status**: Initial version - ready for detailed design

**Next Steps**:
1. Expand actor flows with detailed FDL (Section B)
2. Define algorithms in FDL (Section C)
3. Document technical details (Section E)
4. Complete requirements with references and phases (Section G)
5. Detail implementation changes (Section H)
6. Validate design (workflow 06-validate-feature)
```

**Expected Result**: DESIGN.md with meaningful starter content

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
  - [ ] Section F: Validation & Implementation (test scenarios)
  - [ ] Section G: Requirements (from Q6, references to B-E)
  - [ ] Section H: Implementation Plan (changes from Q7, implementing requirements)
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
