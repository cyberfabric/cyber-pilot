---
fdd: true
type: workflow
name: PRD
version: 1.0
purpose: Create or update PRD document
---

# Create or Update PRD


ALWAYS open and follow `../requirements/workflow-execution.md` WHEN executing this workflow

**Type**: Operation  
**Role**: Product Manager  
**Artifact**: `architecture/PRD.md`

---

## Prerequisite Checklist

- [ ] Agent has read execution-protocol.md
- [ ] Agent has read workflow-execution.md
- [ ] Agent understands this workflow's purpose

---

## Overview

This workflow guides the execution of the specified task.

---



## Requirements

**ALWAYS open and follow**: `../requirements/prd-structure.md`

**ALWAYS open and follow**: `../templates/PRD.template.md` WHEN generating content

Extract:
- Required sections (A: Vision, B: Actors, C: Functional Requirements, D: Use Cases, E: Non-functional requirements)
- Optional sections (F: Additional context)
- ID formats for actors, functional requirements, use cases, and NFRs
- Content requirements per section
- Examples and validation criteria

---

## Prerequisites

**MUST validate**:
- [ ] Project repository exists - validate: Check .git directory
- [ ] Architecture directory exists - validate: Check `architecture/` directory or create

**No dependencies** - This is typically second workflow after adapter

---

## Steps

Determine Mode.
 
### 1. Determine Mode
Check if `architecture/PRD.md` exists:
- **If exists**: UPDATE mode - Read and propose changes
- **If NOT exists**: CREATE mode - Generate from scratch

### 2. Mode-Specific Actions

**CREATE Mode**:
- Proceed to Step 3 for interactive input collection

**UPDATE Mode**:
- Read existing PRD.md
- Extract current content:
  - Section A: Vision
  - Section B: Actors (with IDs)
  - Section C: Functional Requirements (with IDs)
  - Section D: Use Cases (required)
  - Section E: Non-functional requirements (required)
  - Section F: Additional context (if present)
- Ask user: What to update?
  - Add new actors
  - Edit existing actors
  - Remove actors
  - Add new functional requirements
  - Edit existing functional requirements
  - Remove functional requirements
  - Update use cases
  - Update non-functional requirements
  - Update vision
  - Update additional context
- Proceed to Step 3 with appropriate questions

### 3. Interactive Input Collection

**Mode-specific behavior**:

**Q1: Section A (Vision)**
- Context: High-level purpose, target users, problems solved, success criteria, and a capabilities list (no IDs)
- **CREATE**: Propose based on README.md and repository context
- **UPDATE**: Show current Section A, ask for updates or keep
- Store as: `VISION` and `CAPABILITY_LIST[]`

**Q2: Section B (Actors)**
- Context: Who interacts with this system?
- **CREATE**: Ask for 3-5 actors, propose based on vision
- **UPDATE**: Show current actors, ask to add/edit/remove or keep
- For each: Name and role description
- Store as: `ACTORS[]`

**Q3: Section C (Functional Requirements)**
- Context: Verifiable, testable statements about WHAT the system does (not HOW)
- **CREATE**: Ask for 3-10 functional requirements, propose based on vision/actors
- **UPDATE**: Show current functional requirements, ask to add/edit/remove or keep
- Store as: `FUNCTIONAL_REQUIREMENTS[]`

**Q4: Section D (Use Cases)** (required)
- Context: How actors achieve goals via the system (may reference functional requirements)
- **CREATE**: Ask for 1-5 use cases
- **UPDATE**: Show current use cases, ask to add/edit/remove or keep
- Store as: `USE_CASES[]`

**Q5: Section E (Non-functional requirements)** (required)
- Context: Constraints and quality attributes (security, performance, compliance)
- **CREATE**: Ask for 1-5 NFRs
- **UPDATE**: Show current NFRs, ask to add/edit/remove or keep
- Store as: `NFRS[]`

**Q6: Section F (Additional context)** (optional)
- Context: Anything relevant (market notes, stakeholder feedback, assumptions)
- **CREATE**: Allow skip if none
- **UPDATE**: Show current context, ask for updates or keep
- Store as: `ADDITIONAL_CONTEXT`

### 4. Generate/Update IDs

**For new actors**:
- Generate ID: `fdd-{project}-actor-{kebab-case-name}`
- Validate format per requirements

**For new functional requirements**:
- Generate ID: `fdd-{project}-fr-{kebab-case-name}`
- Link to relevant actors
- Validate format per requirements

**For new NFRs**:
- Generate ID: `fdd-{project}-nfr-{kebab-case-name}`
- Validate format per requirements

**For edited actors/functional requirements/NFRs**:
- Keep existing IDs unless rename requested
- Update descriptions/roles as needed

### 5. Generate Content

**CREATE mode**: Generate complete new PRD.md

**UPDATE mode**: Update existing PRD.md with changes

Generate content following `prd-structure.md`:
- Section A: Vision ({VISION}) + Capabilities list ({CAPABILITY_LIST})
- Section B: Actors (with IDs, roles)
- Section C: Functional Requirements (with IDs, descriptions, actor references)
- Section D: Use Cases ({USE_CASES})
- Section E: Non-functional requirements ({NFRS})
- Section F: Additional context (if {ADDITIONAL_CONTEXT})

Ensure:
- All IDs wrapped in backticks
- All required sections present
- No placeholders

### 6. Summary and Confirmation

Show:
- **CREATE**: File path: `architecture/PRD.md` (new file)
- **UPDATE**: File path: `architecture/PRD.md` (updating existing)
- Vision statement (if changed)
- Actors: {count} ({added}/{modified}/{removed})
- Capabilities: {count} ({added}/{modified}/{removed})
- Use cases (if any/changed)
- Additional context (if any/changed)
- Changes summary (for UPDATE mode)

Ask: Proceed? [yes/no/modify]

### 7. Create or Update File

**CREATE Mode**:
- Create `architecture/` directory if needed
- Create `architecture/PRD.md`

**UPDATE Mode**:
- Read existing PRD.md
- Apply changes to content
- Write updated PRD.md

After operation:
- Verify file exists
- Verify content correct

---

## Validation

Run: `prd-validate`

Expected:
- Score: ≥90/100
- Status: PASS

---

## Validation Criteria

- [ ] All workflow steps completed
- [ ] Output artifacts are valid

---


## Validation Checklist

- [ ] All prerequisites were met
- [ ] All steps were executed in order

---


## Next Steps

**If validation passes**: `design` workflow (create DESIGN.md)

**If validation fails**: Fix PRD.md, re-run `prd-validate`
