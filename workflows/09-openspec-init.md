# Initialize OpenSpec for Feature

**Phase**: 3 - Feature Development  
**Purpose**: Create OpenSpec structure and first change for feature implementation

---

## Prerequisites

- Feature DESIGN.md validated (100/100 + 100%)
- Feature status IN_PROGRESS
- Feature directory exists: `architecture/features/feature-{slug}/`

## Input Parameters

- **slug**: Feature identifier (lowercase, kebab-case)
- **change-name**: Descriptive name for first change (e.g., "implement-core" - will be prefixed with number by OpenSpec)

---

## Requirements

### 1: Initialize OpenSpec with CLI Tool

**Requirement**: Use `openspec init` to create structure

**Command**:
```bash
cd architecture/features/feature-{slug}/
openspec init
```

**What This Does**:
- Creates `openspec/` directory structure
- Creates `openspec/specs/` for source of truth
- Creates `openspec/changes/` for active changes
- Initializes configuration

**Expected Outcome**: OpenSpec initialized with proper structure

**Verification**: Run `openspec list` to confirm initialization

---

### 2: Create First Change Manually

**Requirement**: Manually create change directory structure

**Commands**:
```bash
cd openspec/
mkdir -p changes/{change-name}/specs
```

**What This Does**:
- Creates `changes/{change-name}/` directory
- Creates `specs/` subdirectory for delta specifications

**Expected Outcome**: Change directory structure created

**Note**: OpenSpec does not have a `create` command. Changes are created manually.

---

### 3: Create Proposal Document

**Requirement**: Write proposal.md following OpenSpec format

**Location**: `openspec/changes/{change-name}/proposal.md`

**Required Structure** (OpenSpec standard):
```markdown
# Change: {Brief description of change}

## Why
{1-2 sentences on problem/opportunity}

## What Changes
- {Bullet list of changes}
- {Mark breaking changes with **BREAKING**}

## Impact
- Affected specs: {list capabilities}
- Affected code: {key files/systems}
```

**Content Source**: Extract from `../../DESIGN.md` Section F

**Expected Outcome**: Proposal created with proper OpenSpec format

**Note**: Use OpenSpec standard format, not custom templates

---

### 4: Create Tasks Checklist

**Requirement**: Write tasks.md with implementation steps

**Location**: `openspec/changes/{change-name}/tasks.md`

**Required Structure** (OpenSpec standard):
```markdown
## 1. Implementation
- [ ] 1.1 Create database schema
- [ ] 1.2 Implement API endpoint
- [ ] 1.3 Add frontend component
- [ ] 1.4 Write tests
```

**Guidelines**:
- Number tasks sequentially
- Break down into specific, actionable items
- Include testing and documentation tasks

**Expected Outcome**: Clear implementation checklist

---

### 5: Create Delta Specifications

**Requirement**: Write delta specs using OpenSpec format

**Location**: `openspec/changes/{change-name}/specs/{capability}/spec.md`

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

**Expected Outcome**: Delta specs created per affected capability

---

### 6: Create design.md (Optional)

**Requirement**: Create design.md only if needed

**Location**: `openspec/changes/{change-name}/design.md`

**Create design.md if ANY apply**:
- Cross-cutting change (multiple services/modules)
- New external dependency
- Significant data model changes
- Security, performance, or migration complexity
- Technical decisions needed before coding

**Otherwise**: Skip this file

**Minimal Structure**:
```markdown
## Context
{Background, constraints}

## Goals / Non-Goals
- Goals: {...}
- Non-Goals: {...}

## Decisions
- Decision: {What and why}
- Alternatives: {Options + rationale}

## Risks / Trade-offs
- {Risk} → Mitigation

## Migration Plan
{Steps, rollback}
```

**Note**: Feature DESIGN.md is at `../../DESIGN.md` - reference it, don't duplicate

**Expected Outcome**: design.md created only if complexity requires it

---

### 7: Validate with OpenSpec

**Requirement**: Validate change structure and specs

**Command**:
```bash
openspec validate {change-name} --strict
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

### 8: Link to Feature DESIGN.md

**Requirement**: Reference OpenSpec change in Feature DESIGN.md

**Location**: `../../DESIGN.md` (Feature DESIGN.md, not openspec/design.md)

**Add to Section F**:
```markdown
## F. Validation & Implementation

### OpenSpec Changes

See `openspec/changes/` for implementation details:
- `{change-name}` - {Brief description}
```

**Expected Outcome**: Feature DESIGN.md references OpenSpec change

**Note**: Feature design is in `architecture/features/feature-{slug}/DESIGN.md`

---

## Completion Criteria

OpenSpec initialization complete when:

- [ ] `openspec/specs/` directory exists
- [ ] `openspec/changes/{change-name}/` created manually
- [ ] `proposal.md` follows OpenSpec format (Why, What Changes, Impact)
- [ ] `tasks.md` has numbered implementation checklist
- [ ] Delta specs created in `specs/{capability}/spec.md` with ADDED/MODIFIED/etc
- [ ] Each requirement has at least one `#### Scenario:`
- [ ] `design.md` created if complexity requires it (optional)
- [ ] `openspec validate {change-name} --strict` passes
- [ ] Feature DESIGN.md (../../DESIGN.md) Section F references change
- [ ] Ready to start implementation

---

## Common Challenges

### Issue: Too Many Tasks

**Resolution**: Break change into smaller changes (001, 002, etc.). Each change should be completable in 4-8 hours.

### Issue: Unclear Specs

**Resolution**: Return to DESIGN.md, clarify Section E (Technical Details). Specs should be unambiguous.

---

## Next Activities

After OpenSpec initialization:

1. **Review Proposal**: Ensure implementation plan is clear
   - Verify scope
   - Check dependencies
   - Validate effort estimate

2. **Start Implementation**: Run `10-openspec-change-implement.md`
   - Follow tasks.md checklist
   - Implement according to specs
   - Test as you go

3. **Track Progress**: Update tasks.md as work progresses

---

## OpenSpec Best Practices

**Changes Should Be**:
- **Atomic**: Self-contained unit of work
- **Traceable**: Clear what changed and why
- **Testable**: Verification criteria defined
- **Reversible**: Can be undone if needed

**Specs Should Be**:
- **Precise**: No ambiguity
- **Complete**: All details specified
- **Consistent**: Align with DESIGN.md
- **Reviewable**: Easy to validate

---

## References

- **Core FDD**: `../AGENTS.md` - OpenSpec integration
- **OpenSpec Docs**: https://openspec.dev - Full OpenSpec framework
- **Next Workflow**: `10-openspec-change-implement.md`
