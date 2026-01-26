---
fdd: true
type: requirement
name: Workflow Selection
version: 2.1
purpose: Select appropriate FDD workflow based on project state
---

# Workflow Selection Guide

## Prerequisite Checklist

- [ ] Agent has read and understood this requirement
- [ ] Agent will follow the rules defined here

---


## Overview

This guide helps you select the correct FDD workflow based on:
- Current project state
- Artifacts that exist or need creation
- Phase of development

**All workflows located in**: `/FDD/workflows/`

---

## ⚠️ FIRST STEP: Check for FDD Adapter

**BEFORE selecting any workflow**:

1. Check if `FDD-Adapter/AGENTS.md` exists at project root level
2. Check these locations (in order):
   - `{project-root}/FDD-Adapter/AGENTS.md` (recommended)
   - `{project-root}/guidelines/FDD-Adapter/AGENTS.md`
   - `{project-root}/spec/FDD-Adapter/AGENTS.md`
   - `{project-root}/docs/FDD-Adapter/AGENTS.md`

**Important**: Adapter MUST be at project root level, NOT deeply nested in subdirectories

**If NO adapter** → Start with `adapter.md` workflow

**If adapter exists** → Continue to workflow selection below

---

## Available Workflows

### Phase 0: Adapter Setup

**adapter.md** - Create or update FDD adapter
- **Use when**: No adapter exists OR need to update adapter
- **Creates**: `{project-root}/FDD-Adapter/AGENTS.md` + spec files
- **Location**: Project root level (not nested in subdirectories)
- **Modes**: CREATE or UPDATE
- **Next**: `prd` or `adapter-validate`

**adapter-from-sources.md** - Extract adapter from existing codebase
- **Use when**: Legacy project, want to reverse-engineer adapter
- **Analyzes**: Existing code to propose formats
- **Next**: `adapter-validate`

**adapter-agents.md** - Generate AI agent config from adapter
- **Use when**: Want IDE-specific AI configuration
- **Creates**: `.windsurf/`, `.cursorrules`, etc.
- **Next**: Any architecture workflow

**adapter-validate.md** - Validate adapter structure
- **Use when**: Adapter created or updated
- **Validates**: File structure, AGENTS.md format, spec files
- **Next**: `prd` or `design`

---

### Phase 1: PRD & Architecture

## Phase 1: PRD & Architecture

### Workflow: `prd`

**prd.md** - Create or update PRD.md
- **Use when**: Need to document PRD
- **Creates**: `architecture/PRD.md`
- **Sections**: Vision, Actors, Capabilities
- **Modes**: CREATE or UPDATE
- **Next**: `prd-validate`

### Workflow: `prd-validate`

**prd-validate.md** - Validate prd

**When**: After PRD.md created or updated
- **Validates**: Required sections, actor/capability IDs
- **Score**: ≥90/100
- **Next**: `design`

**design.md** - Create or update overall design
- **Use when**: Need architecture/system design
- **Creates**: `architecture/DESIGN.md`
- **Sections**: Architecture, Requirements, Technical Details
- **Modes**: CREATE or UPDATE
- **Next**: `design-validate`

**design-validate.md** - Validate overall design
- **Use when**: DESIGN.md created or updated
- **Validates**: Sections, domain model, API contracts, diagrams
- **Score**: 100/100 + 100% completeness
- **Next**: `adr` (optional) or `features`

**adr.md** - Create or update Architecture Decision Records
- **Use when**: Need to document architectural decisions
- **Creates**: `architecture/ADR/` (directory with per-record ADR files)
- **Format**: MADR with FDD extensions
- **Modes**: CREATE (new ADR) or UPDATE (edit ADR)
- **Next**: `adr-validate`

**adr-validate.md** - Validate ADRs
- **Use when**: ADRs created or updated
- **Validates**: MADR format, numbering, related design elements
- **Score**: ≥90/100
- **Next**: `features` or continue design work

---

### Phase 2: Feature Planning

## Phase 2: Feature Planning

### Workflow: `features`

**features.md** - Create or update features manifest
- **Use when**: Need to plan/list features
- **Creates**: `architecture/FEATURES.md`
- **Modes**: CREATE (from DESIGN.md) or UPDATE (manual)
- **Next**: `features-validate`

**features-validate.md** - Validate features manifest
- **Use when**: FEATURES.md created or updated
- **Validates**: Manifest structure, feature list completeness
- **Score**: ≥90/100
- **Next**: `feature` (for each feature)

**feature.md** - Create or update feature design
- **Use when**: Need to design single feature
- **Creates**: `architecture/features/feature-{slug}/DESIGN.md`
- **Sections**: A-F (Overview, Actors, Algorithms, Data, API, Requirements)
- **Modes**: CREATE or UPDATE
- **Next**: `feature-validate`

**feature-validate.md** - Validate feature design
- **Use when**: Feature DESIGN.md created or updated
- **Validates**: All sections, actor flows, FDL, no type redefinitions
- **Score**: 100/100 + 100% completeness
- **Next**: `implement`

---

### Phase 3: Implementation

**code.md** - Implement feature directly from design
- **Use when**: Feature validated, ready to code from `DESIGN.md`
- **Implements**: Feature requirements directly from `DESIGN.md`
- **Updates**: Feature DESIGN.md checkboxes/statuses iteratively during coding
- **Next**: `code-validate`

**code-validate.md** - Validate feature code
- **Use when**: Feature implementation is in progress or complete
- **Validates**: Code compiles, tests pass, requirements and test scenarios implemented
- **Next**: Update FEATURES.md: Mark feature status as COMPLETE

---

## Decision Tree

```
START
│
├─ No adapter?
│  └─> adapter.md (or adapter-from-sources.md for legacy)
│
├─ Adapter exists, no PRD.md?
│  └─> prd.md → prd-validate.md
│
├─ PRD.md exists, no DESIGN.md?
│  └─> design.md → design-validate.md
│
├─ Need to document decisions?
│  └─> adr.md → adr-validate.md
│
├─ DESIGN.md validated, no FEATURES.md?
│  └─> features.md → features-validate.md
│
├─ FEATURES.md exists, need feature design?
│  └─> feature.md → feature-validate.md
│
├─ Feature validated, ready to code?
│  └─> code.md
│
├─ All changes done, validate code?
│  └─> code-validate.md
│
├─ Need to update existing doc?
│  └─> Use same workflow in UPDATE mode
│
└─ Need to validate feature or design?
   └─> feature-validate.md or design-validate.md
```

---

## Common Sequences

### New project from scratch
```
adapter → adapter-validate
  ↓
prd → prd-validate
  ↓
design → design-validate
  ↓
[optional: adr → adr-validate]
  ↓
features → features-validate
  ↓
feature → feature-validate (for each feature)
  ↓
implement
  ↓
code-validate
```

### Legacy project integration
```
adapter-from-sources → adapter-validate
  ↓
[reverse-engineer existing docs or create new]
  ↓
design → design-validate
  ↓
[continue as new project]
```

### Add feature to existing project
```
[adapter + design already exist]
  ↓
features → features-validate (update manifest)
  ↓
feature → feature-validate
  ↓
implement
  ↓
code-validate
```

### Update existing design
```
design (UPDATE mode) → design-validate
  ↓
[if impacts features: update feature designs]
  ↓
feature (UPDATE mode) → feature-validate
```

---

## Quick Reference

### "I want to..."

**Set up FDD for my project**
→ `adapter.md` (or `adapter-from-sources.md` for legacy code)

**Document PRD**
→ `prd.md` → `prd-validate.md`

**Design system architecture**
→ `design.md` → `design-validate.md`

**Record architectural decisions**
→ `adr.md` → `adr-validate.md`

**Plan features**
→ `features.md` → `features-validate.md`

**Design a feature**
→ `feature.md` → `feature-validate.md`

**Implement feature directly from design**
→ `code.md`

**Validate feature code**
→ `code-validate.md`

**Update existing document**
→ Use same workflow in UPDATE mode

**Generate IDE config**
→ `adapter-agents.md`

---

## Validation Criteria

- [ ] All MUST requirements are satisfied
- [ ] No MUST NOT rules are violated

---


## Validation Checklist

- [ ] Document follows required structure
- [ ] All validation criteria pass

---


## References

**This file is used by**:
- `workflows/AGENTS.md` - Directs to this guide for workflow selection
- AI agents - To select appropriate workflow

**This file references**:
- `workflow-execution.md` - How to execute selected workflow
- `../.adapter/specs/patterns.md` - Workflow file format specification
- All requirement files in `requirements/` - Referenced by workflows

**All workflows located in**: `/FDD/workflows/`

## Workflow Resolution Algorithm

Algorithm for resolving user request to workflow file path is implemented throughout this document via keyword matching and routing logic.

Key steps:
- Extract keywords from request
- Initialize workflow candidates
- Return appropriate workflow based on request type (adapter, prd, design, feature, validate, implement)
