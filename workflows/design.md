---
fdd: true
type: workflow
name: Design
version: 1.0
purpose: Create or update overall design document
---

# Create or Update Overall Design

**Type**: Operation  
**Role**: Architect  
**Artifact**: `architecture/DESIGN.md`

---

## Prerequisite Checklist

- [ ] Agent has read execution-protocol.md
- [ ] Agent has read workflow-execution.md
- [ ] Agent understands this workflow's purpose

---

## Overview

This workflow guides the execution of the specified task.

---



ALWAYS open and follow `../requirements/workflow-execution.md` WHEN executing this workflow

## Requirements

**ALWAYS open and follow**: `../requirements/overall-design-structure.md`

**ALWAYS open and follow**: `../templates/DESIGN.template.md` WHEN generating content

Extract:
- Required sections (A: Architecture Overview, B: Principles & Constraints, C: Technical Architecture, D: Additional Context)
- Content requirements per section
- Validation criteria

---

## Prerequisites

**MUST validate**:
- [ ] PRD.md exists - validate: Check file at `architecture/PRD.md`
- [ ] PRD.md validated - validate: Score ≥90/100

**If missing**: Run `prd` and `prd-validate` first

---

## Steps
 
 Determine Mode.
 
### 1. Determine Mode

Check if `architecture/DESIGN.md` exists:
- **If exists**: UPDATE mode - Read and propose changes
- **If NOT exists**: CREATE mode - Generate from scratch

### 2. Read PRD

Open `architecture/PRD.md`

Extract:
- Vision (Section A)
- Actors list (Section B)
- Capabilities list (Section C)

### 3. Mode-Specific Actions

**CREATE Mode**:
- Proceed to Step 4 for interactive input collection

**UPDATE Mode**:
- Read existing DESIGN.md
- Extract current content:
  - Section A: Architecture Overview
  - Section B: Principles & Constraints
  - Section C: Technical Architecture
  - Section D: Additional Context
- Ask user: What to update?
  - Update architecture style/layers
  - Add/edit/remove principles
  - Add/edit/remove constraints
  - Update technical architecture
  - Update components
- Proceed to Step 4 with appropriate questions

### 4. Interactive Input Collection

**Mode-specific behavior**:

**Q1: Architecture Style**
- Context: Architectural pattern for this system
- Options: Monolithic, Microservices, Layered, Hexagonal, Event-Driven, Other
- **CREATE**: Propose based on capabilities complexity
- **UPDATE**: Show current style, ask to change or keep
- Store as: `ARCH_STYLE`

**Q2: Key Components**
- Context: Main system components (3-7 components)
- **CREATE**: Propose based on architecture style and capabilities
- **UPDATE**: Show current components, ask to add/edit/remove or keep
- Store as: `COMPONENTS[]`

**Q3: Technical Stack** (if adapter missing)
- Context: Technologies, frameworks, libraries
- **CREATE**: Detect from project files or ask
- **UPDATE**: Show current stack, ask to update or keep
- Store as: `TECH_STACK`
- Note: If adapter exists, use adapter tech specs

**Q4: Design Principles**
- Context: Key architectural principles (3-5 principles)
- **CREATE**: Propose FDD defaults + style-specific
- **UPDATE**: Show current principles, ask to add/edit/remove or keep
- Store as: `PRINCIPLES[]`

**Q5: Constraints**
- Context: Hard constraints that bound the solution space
- **CREATE**: Propose initial constraints based on PRD + context
- **UPDATE**: Show current constraints, ask to add/edit/remove or keep
- Store as: `CONSTRAINTS[]`

### 6. Generate Content

**CREATE mode**: Generate complete new DESIGN.md

**UPDATE mode**: Update existing DESIGN.md with changes

Generate content following `overall-design-structure.md`:
- Section A: Architecture Overview (architectural vision, architecture drivers, layers)
- Section B: Principles & Constraints
- Section C: Technical Architecture (domain model, components, API contracts, interactions)
- Section D: Additional Context (optional)

Ensure:
- No contradictions with PRD.md
- No type redefinitions
- All IDs formatted correctly

### 7. Summary and Confirmation

Show:
- **CREATE**: File path: `architecture/DESIGN.md` (new file)
- **UPDATE**: File path: `architecture/DESIGN.md` (updating existing)
- Architecture style (if changed)
- Components: {count} ({added}/{modified}/{removed})
- Requirements: {count} ({added}/{modified}/{removed})
- Principles: {count} ({added}/{modified}/{removed})
- References to PRD.md
- Changes summary (for UPDATE mode)

Ask: Proceed? [yes/no/modify]

### 8. Create or Update File

**CREATE Mode**:
- Create `architecture/DESIGN.md`

**UPDATE Mode**:
- Read existing DESIGN.md
- Apply changes to content
- Write updated DESIGN.md

After operation:
- Verify file exists
- Verify content correct

### 9. Create Architecture Decision Records

**CREATE Mode only**:
- Automatically trigger `adr` workflow
- If `architecture/ADR/` does NOT exist or has no ADR files: Create ADR-0001 under `architecture/ADR/general/`
- If `architecture/ADR/` already has ADR files: Skip

**UPDATE Mode**:
- Skip ADR creation (user can run `adr` workflow separately if needed)

**ADR-0001 Content** (CREATE mode):
- Title: "Initial {Module/Project} Architecture"
- Context: Based on architecture style and key decisions from DESIGN.md
- Drivers: Key requirements and principles
- Options: Architecture alternatives considered
- Outcome: Chosen architecture with rationale
- Related Elements: Link to actors, capabilities, requirements, principles

**Output** (CREATE mode):
```markdown
---

## Creating Initial ADR

Creating ADR-0001 under `architecture/ADR/general/`...
```

---

## Validation

Run: `design-validate`

Expected:
- Score: ≥90/100
- Status: PASS
- No contradictions with PRD.md

Then run: `adr-validate`

Expected:
- Score: ≥90/100
- Status: PASS
- ADR-0001 properly formatted

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

**If both validations pass**: `features` workflow (decompose into features)

**If validation fails**: Fix issues, re-validate


