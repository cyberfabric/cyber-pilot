# Create OpenSpec Change

**Phase**: 3 - Feature Implementation  
**Purpose**: Create change from Feature DESIGN.md implementation plan (first or subsequent)

**Structure Requirements**: See `../requirements/openspec-change-structure.md` for complete change structure specification

---

## Prerequisites

- OpenSpec initialized at project root (`openspec/` directory exists)
- Feature DESIGN.md validated (100/100 + 100%)
- Feature DESIGN.md Section F has requirements defined
- Feature DESIGN.md Section G has implementation plan with changes
- For subsequent changes: Previous change completed and archived

**Note**: Before creating changes, read `../requirements/openspec-change-structure.md` to understand required change structure

---

## Overview

This workflow is the **universal change creation workflow** for all OpenSpec changes (first or subsequent). It reads Feature DESIGN.md Section G to identify changes, displays status, and guides through creating the selected change.

**Key Principle**: Single workflow for all change creation. Read plan, show status, let user choose.

**Usage**:
- **First change**: Run after feature design validated (workflow 06)
- **Subsequent changes**: Run after previous change completed (workflow 11)

---

## Interactive Questions

### Q1: Feature Slug

**Requirement**: Identify which feature to create the next OpenSpec change for

**Note**: Project name is already known from FDD adapter configuration and project context

**Question to User**:
```
Which feature are you creating the next change for?
Provide feature slug: ___

Example: "user-auth", "payment-flow"
```

**Store as**: `FEATURE_SLUG`

**Spec Name Format**: Follow naming convention defined in `../requirements/openspec-change-structure.md`:
- Format: `fdd-{project-name}-{feature-slug}-feature`
- Example: `fdd-payment-system-user-auth-feature`

### Q2: Verify OpenSpec Structure

**Requirement**: Confirm OpenSpec directory structure exists at project root

**Required Directories**:
- `openspec/` (main directory)
- `openspec/specs/` (merged specifications)
- `openspec/changes/` (active changes)

**Required Files**:
- `openspec/project.md` (project metadata)

**Validation**: All directories and files must exist

**If Missing**: Run workflow `01-init-project.md` first or create structure manually

**Expected Outcome**: OpenSpec structure verified

---

### Q3: Read and Display Change Status

**Action**: Read `architecture/features/feature-{FEATURE_SLUG}/DESIGN.md` Section G

**Extract**:
- List of all planned implementation changes from Section G
- Current status of each change (✅ COMPLETED, 🔄 IN_PROGRESS, ⏳ NOT_STARTED)
- Check `openspec/changes/` for active changes
- Check `openspec/changes/archive/` for completed changes

**Display to User**:
```
OpenSpec Changes Status (from DESIGN.md Section G):
────────────────────────────────────────────────────

{For each change in Section H}
{Status Icon} Change {NNN}: {Change Name}
  Description: {from DESIGN.md}
  Implements: {requirement IDs from Section G}
  Dependencies: {from DESIGN.md}
  Status: {✅ COMPLETED / 🔄 IN_PROGRESS / ⏳ NOT_STARTED}

────────────────────────────────────────────────────
Completed: {count} | In Progress: {count} | Remaining: {count}
```

### Q4: Select Change to Create

**If NO changes exist yet (first change)**:
```
No changes created yet. Creating first change.

Available changes from Section G:
{List all planned changes}

Which change should be created first?
Options:
{For each change in Section G}
  {N}. Change {NNN}: {name}
     {brief description}

Your choice: ___
```

**If multiple NOT_STARTED changes available**:
```
Which change should be created next?

Options:
{For each NOT_STARTED change}
  {N}. Change {NNN}: {name}
     {brief description}
     Dependencies: {list or "None"}

Your choice: ___
```

**If only one NOT_STARTED change remaining**:
```
Only one change remaining:
Change {NNN}: {name}

Proceed with this change? (y/n)
```

**If NO NOT_STARTED changes (all completed)**:
```
✅ All changes completed!

No remaining changes to create.
Consider running workflow 07-complete-feature to mark feature as done.
```

**Store as**: `CHANGE_NUMBER`, `CHANGE_NAME`, `CHANGE_DESC`, `CHANGE_SCOPE[]`

### Q5: Confirm Creation

**Display Summary**:
```
Change Creation Summary:
────────────────────────────────
Feature: feature-{FEATURE_SLUG}
Change: Change {CHANGE_NUMBER}: {CHANGE_NAME}

Will create:
✓ openspec/specs/fdd-{project-name}-feature-{feature-slug}/ (if first change)
  ✓ spec.md (from Section G)
✓ openspec/changes/{CHANGE_NAME}/
  ✓ proposal.md (Why, What, Impact)
  ✓ tasks.md (Implementation checklist)
  ✓ specs/fdd-{project-name}-feature-{feature-slug}/spec.md (Delta specifications)
  ✓ design.md (if complexity requires)

Change details:
- Number: Change {CHANGE_NUMBER}
- Description: {CHANGE_DESC}
- Implements: {requirement IDs from Section G}
- Scope: {list CHANGE_SCOPE items}
- Dependencies: {list or "None"}

Proceed with creation? (y/n)
```

**Expected Outcome**: User confirms or cancels

---

## Requirements

### 1. Create Feature Spec (First Change Only)

**Requirement**: Create initial spec.md for feature from DESIGN.md Section F

**Condition**: Only if `openspec/specs/fdd-{project-name}-feature-{feature-slug}/` does not exist (first change)

**Location**: `openspec/specs/fdd-{project-name}-feature-{feature-slug}/spec.md`

**Generated Content** (from Section F Requirements):
```markdown
# {FEATURE_NAME}

{For each requirement in Section G, copy with SHALL statements and scenarios}

## Requirement: {Requirement Title}

{Requirement SHALL statement}

### Scenario: {Scenario name from Testing Scenarios}
- **WHEN** {condition from FDL scenario}
- **THEN** {expected result from FDL scenario}
```

**Expected Outcome**: Initial feature spec created from Section F (first change only)

**Validation**: If file exists, skip this step (subsequent changes)

---

### 2. Create Change Directory Structure

**Requirement**: Manually create change directory

**Commands**:
```bash
# Run from project root
mkdir -p openspec/changes/{CHANGE_NAME}/specs/{SPEC_NAME}
```

**What This Does**:
- Creates `changes/{CHANGE_NAME}/` directory
- Creates `specs/{SPEC_NAME}/` subdirectory for delta specifications

**Expected Outcome**: Change directory structure created

**Note**: OpenSpec does not have a `create` command. Changes are created manually.

---

### 3. Generate Proposal Document

**Requirement**: Write proposal.md following OpenSpec format

**Location**: `openspec/changes/{NEXT_CHANGE_NAME}/proposal.md`

**Generated Content** (OpenSpec standard):
```markdown
# Change: {NEXT_CHANGE_DESC from Q3}

## Why
{Extract "Why" from DESIGN.md Section G for this change if available, otherwise:}
This change implements Change {NEXT_CHANGE_NUMBER} of {FEATURE_NAME} feature.
{NEXT_CHANGE_DESC}

## What Changes
{For each item in NEXT_CHANGE_SCOPE from Q3}
- {Scope item}

{If breaking changes identified in DESIGN.md}
- **BREAKING**: {Breaking change description}

## Impact
- Affected specs: {Derive from NEXT_CHANGE_SCOPE}
- Affected code: {Key modules/files from scope}
- Dependencies: {List dependencies from Q3}
```

**Content Source**: 
- Primary: User selection from Q3 + DESIGN.md Section G
- All content from planned change in DESIGN.md

**Clickable Links Required**:
- **Change Name**: Must link to Feature DESIGN.md Section G
- **Feature**: Must link to Feature DESIGN.md
- **Implements Requirements**: Each requirement ID must link to Section F

**Expected Outcome**: Proposal created with actual content from DESIGN.md

**Validation Criteria**:
- Contains Why, What Changes, Impact sections
- Content from DESIGN.md, not placeholders
- Dependencies documented
- Breaking changes marked if any

---

### 4. Generate Tasks Checklist

**Requirement**: Write tasks.md with implementation steps

**Location**: `openspec/changes/{NEXT_CHANGE_NAME}/tasks.md`

**Generated Content** (OpenSpec standard):
```markdown
## 1. Implementation
{Extract tasks from DESIGN.md Section G for this specific change}
{If detailed tasks in DESIGN.md:}
- [ ] 1.{N} {Task from DESIGN.md}

{Otherwise, generate from NEXT_CHANGE_SCOPE:}
{For each scope item, create 1-2 tasks}
- [ ] 1.{N} {Actionable task derived from scope item}

## 2. Testing
{MANDATORY: Generate tests from Section F Testing Scenarios (FDL)}
{For each requirement being implemented in this change}
{Extract all FDL test scenarios from DESIGN.md Section F}
{For each scenario, create test task}
- [ ] 2.1 Implement test: {Test name from Section F}
  - Test steps: {FDL numbered list from Section F}
- [ ] 2.2 Implement test: {Next test name}
  - Test steps: {FDL numbered list from Section F}

{Add general validation tasks:}
- [ ] 2.{N} Validate against Feature DESIGN.md Section B/C
- [ ] 2.{N+1} Update documentation if needed
```

**Task Generation Guidelines**:
- Primary: Extract from DESIGN.md Section G for this change
- Fallback: Derive from NEXT_CHANGE_SCOPE items
- **MANDATORY**: Extract all Testing Scenarios from Section F for requirements in this change
- Each scenario from Section F → 1 test task with FDL steps
- Always include: validation, documentation
- Number sequentially (1.1, 1.2, 2.1, 2.2, etc.)

**Expected Outcome**: Actionable checklist with tests for all Section G scenarios

**Validation Criteria**:
- Tasks from DESIGN.md or derived from scope
- **All Testing Scenarios from Section F converted to test tasks**
- Each test task includes FDL test steps from Section F
- Validation included
- All tasks actionable and specific

---

### 5. Create Delta Specifications

**Requirement**: Write delta specs using OpenSpec format

**Location**: `openspec/changes/{next-change-name}/specs/fdd-{project-name}-feature-{feature-slug}/spec.md`

**Delta Operations** (use these headers):
- `## ADDED Requirements` - New capabilities
- `## MODIFIED Requirements` - Changed behavior
- `## REMOVED Requirements` - Deprecated features
- `## RENAMED Requirements` - Name changes

**Required Format**:
```markdown
## ADDED Requirements
### Requirement: New Feature
The system SHALL provide...

#### Scenario: Success case
- **WHEN** user performs action
- **THEN** expected result
```

**Critical Rules**:
- Every requirement MUST have at least one `#### Scenario:`
- Use `**WHEN**` and `**THEN**` in scenarios
- Use SHALL/MUST for normative requirements
- For MODIFIED: copy full requirement from `openspec/specs/`, then edit

**Content Source**: Extract from Feature DESIGN.md Section F (Requirements)

**Expected Outcome**: Delta specs created per affected capability

---

### 6. Create design.md (REQUIRED)

**Requirement**: Create design.md as reference file to Feature DESIGN.md

**Location**: `openspec/changes/{next-change-name}/design.md`

**Purpose**: Reference file linking to Feature DESIGN.md

**Required Content**:
```markdown
# Design Reference

**MUST READ**: [Feature DESIGN.md](../../architecture/features/feature-{slug}/DESIGN.md)

**Agent Instruction**: This change implements requirements from Feature DESIGN.md. Read the full design before implementation.

## Implementation Notes

{Optional: Add any change-specific implementation notes if needed}
```

**Note**: This is a reference file, not a place for extensive new design. Feature DESIGN.md is the source of truth.

**Expected Outcome**: design.md created with link to Feature DESIGN.md

---

### 7. Validate with OpenSpec

**Requirement**: Validate change structure and specs

**Command**:
```bash
openspec validate {next-change-name} --strict
```

**What This Checks**:
- Change has at least one delta
- All requirements have scenarios
- Scenario format correct (`#### Scenario:`)
- Files not empty
- Delta operations properly formatted

**Expected Outcome**: Validation passes with zero errors

**Resolution if Failed**: Fix reported issues, then re-validate

---

### 8. Update Feature DESIGN.md Section G Status

**Requirement**: Mark change as IN_PROGRESS in Feature DESIGN.md Section G

**Location**: `architecture/features/feature-{slug}/DESIGN.md` Section G

**Update Section G**:
```markdown
## G. Implementation Plan

### Change {PREVIOUS_NUMBER}: {previous-change-name}
**Status**: ✅ COMPLETED
{Keep remaining fields}

### Change {NEXT_CHANGE_NUMBER}: {NEXT_CHANGE_NAME}
**Status**: 🔄 IN_PROGRESS
**Description**: {NEXT_CHANGE_DESC}
**Implements Requirements**: {list requirement IDs from Section G}
**Dependencies**: {dependencies}

### Change {FUTURE_NUMBER}: {future-change-name}
**Status**: ⏳ NOT_STARTED
{Keep remaining changes}
```

**Expected Outcome**: Feature DESIGN.md Section G reflects current change IN_PROGRESS

---

### 9. Update Section F Requirements Status

**Requirement**: Mark requirements as IN_PROGRESS in Section F for this change

**Location**: `architecture/features/feature-{slug}/DESIGN.md` Section F

**For each requirement implemented in this change**:
```markdown
## F. Requirements

### Requirement: {Requirement Title}

**Status**: 🔄 IN_PROGRESS

{Requirement description with SHALL statements}

**Testing Scenarios (FDL)**:
{FDL numbered list scenarios}

**Acceptance Criteria**:
{Criteria list}
```

**What to Update**:
- Find requirements listed in Section G under "Implements Requirements" for this change
- Update each requirement's status from ⏳ NOT_STARTED to 🔄 IN_PROGRESS
- Leave other requirements with their existing status

**Expected Outcome**: Requirements in Section F show IN_PROGRESS for those in this change

---

### 10. Update FEATURES.md Status (First Change Only)

**Requirement**: Mark feature as IN_PROGRESS in features manifest (first change only)

**Condition**: Only if this is the first change for this feature

**Location**: `architecture/features/FEATURES.md`

**Update Feature Entry**:
```markdown
### N. [feature-{slug}](feature-{slug}/) {priority}
**Purpose**: {purpose}
**Status**: IN_PROGRESS  
**Depends On**: {dependencies}
**Blocks**: {blocked features}
**Scope**:
{scope items}
```

**What to Change**:
- Status: `NOT_STARTED` → `IN_PROGRESS`

**Expected Outcome**: FEATURES.md reflects feature implementation started (first change only)

**Verification**: Check feature status shows 🔄 IN_PROGRESS

---

### 11. Show Summary

**Requirement**: Display what was created

**Display Summary**:
```
Change Created!
────────────────────────────────────
Feature: feature-{FEATURE_SLUG}

Created:
{If first change: "✓ openspec/specs/fdd-{project-name}-feature-{feature-slug}/spec.md (from Section F)"}
✓ openspec/changes/{CHANGE_NAME}/
  ✓ proposal.md (Why, What, Impact with clickable links)
  ✓ tasks.md ({N} implementation tasks)
  ✓ specs/fdd-{project-name}-feature-{feature-slug}/spec.md (delta specifications)
  ✓ design.md (reference to Feature DESIGN.md)

✓ Feature DESIGN.md Section G updated (Change {CHANGE_NUMBER} → IN_PROGRESS)
✓ Feature DESIGN.md Section F updated (Requirements → IN_PROGRESS)
{If first change: "✓ FEATURES.md updated (feature → IN_PROGRESS)"}

Change Details:
- Number: Change {CHANGE_NUMBER}
- Name: {CHANGE_NAME}
- Description: {CHANGE_DESC}
- Tasks: {N} items to implement

Progress:
- Completed: {count} changes
- Current: Change {CHANGE_NUMBER}
- Remaining: {count} changes

Next Steps:
1. Review openspec/changes/{CHANGE_NAME}/ structure
2. Validate: openspec validate {CHANGE_NAME} --strict
3. Start implementation: Run workflow 10-openspec-change-implement
```

**Expected Outcome**: Summary displayed

---

## Completion Criteria

Change creation complete when:

- [ ] User selected feature slug (Q1)
- [ ] OpenSpec structure verified (Q2)
- [ ] Change status read from DESIGN.md Section H (Q3)
- [ ] User selected change to create (Q4)
- [ ] User confirmed creation (Q5)
- [ ] `openspec/specs/fdd-{project-name}-feature-{feature-slug}/spec.md` created from Section F (first change only)
- [ ] `openspec/changes/{CHANGE_NAME}/` created manually
- [ ] `proposal.md` generated with content from DESIGN.md:
  - [ ] Why, What Changes, Impact sections present
  - [ ] Content from DESIGN.md Section G, not placeholders
  - [ ] Dependencies documented
  - [ ] **Change Name, Feature, Requirements are clickable links**
- [ ] `tasks.md` generated with tasks from DESIGN.md or scope:
  - [ ] Tasks from DESIGN.md or derived from scope
  - [ ] Testing tasks included
  - [ ] Validation tasks included
- [ ] Delta specs directory created (specs content added later)
- [ ] `design.md` created as reference file (REQUIRED)
- [ ] Feature DESIGN.md Section G updated (change marked IN_PROGRESS)
- [ ] Feature DESIGN.md Section F updated (requirements marked IN_PROGRESS)
- [ ] Summary displayed to user
- [ ] Ready to create delta specs and validate

---

## Common Challenges

### Issue: Unclear Which Change to Create Next

**Resolution**: Review DESIGN.md Section G implementation plan. Changes should be ordered by dependencies. If order unclear, implement foundational changes first (data model, core logic, then UI/API).

### Issue: Change Plan Changed Since Design

**Resolution**: If implementation reveals changes need to be different:
1. Use workflow 08 (fix-design) to update DESIGN.md Section G
2. Re-validate Feature Design
3. Then create change with updated plan

### Issue: Multiple Changes Could Be Next

**Resolution**: Choose based on:
- Dependency order (prerequisites first)
- Risk level (higher risk earlier for feedback)
- Team capacity (parallel work if independent)

---

## Next Activities

After creating next change:

1. **Implement Change**: Run `10-openspec-change-implement.md`
   - Follow implementation workflow
   - Complete all tasks in tasks.md

2. **Complete When Done**: Run `11-openspec-change-complete.md`
   - Archive change
   - Merge specs

3. **Repeat if Needed**: If more changes remain
   - Run this workflow again for next change
   - Or run `12-openspec-validate.md` to check overall structure

4. **Complete Feature**: When all changes done
   - Run `07-complete-feature.md`
   - Mark feature as IMPLEMENTED

---

## Best Practices

**Change Extraction**:
- Copy implementation details directly from DESIGN.md Section G
- Don't make up new requirements - follow design
- If design is insufficient, fix design first (workflow 08)

**Clickable Links**:
- Always create clickable links in proposal.md for Change Name, Feature, Requirements
- Format: `[id](../../architecture/features/feature-{slug}/DESIGN.md#section-x)`
- This ensures full traceability from OpenSpec to Feature Design

**Change Scope**:
- Each change should be completable in 4-8 hours
- If too large, break into multiple changes
- If too small, consider combining with next

**Dependencies**:
- Check if change depends on previous changes being deployed
- Document dependencies in proposal.md Impact section
- Order changes by dependency graph

---

## References

- **Core FDD**: `../AGENTS.md` - OpenSpec integration
- **Feature Design**: `../../DESIGN.md` - Section G implementation plan
- **Requirements**: `../requirements/openspec-change-structure.md` - Change structure specification
- **Previous Workflow**: `11-openspec-change-complete.md` - Complete previous change
- **Next Workflow**: `10-openspec-change-implement.md` - Implement this change
- **OpenSpec Docs**: `../openspec/AGENTS.md` - Full OpenSpec specification
