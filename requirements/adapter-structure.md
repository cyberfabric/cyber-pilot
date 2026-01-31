---
fdd: true
type: requirement
name: Adapter Structure
version: 1.1
purpose: Define validation rules for FDD adapter files
---

# FDD Adapter Structure Requirements

---

## Agent Instructions

**ALWAYS open and follow**: `../workflows/adapter.md` WHEN executing workflow

**ALWAYS open and follow**: `../templates/adapter-AGENTS.template.md` WHEN generating adapter AGENTS.md

**ALWAYS open**: `../templates/examples/adapter/AGENTS-EXAMPLE.md` WHEN reviewing valid artifact structure

**ALWAYS open and follow**: `requirements.md` WHEN extracting shared requirements

---

## Prerequisite Checklist

- [ ] Agent has read and understood this requirement
- [ ] Agent will follow the rules defined here

---

## Overview

**This file defines**: Validation rules (WHAT must be valid)  
**Template defines**: Structure for generation (HOW to create)  
**Workflow defines**: Process (STEP by STEP)

**FDD Adapter** — Dynamic project-specific configuration that evolves with the project

**Philosophy**: 
- Adapter specs derive from design decisions, not predefined templates
- Technical decisions appear during design → captured in adapter
- Existing projects → adapter discovers patterns from code/docs/ADRs
- Greenfield projects → adapter starts minimal, grows with design

**Lifecycle**:
1. **Bootstrap**: Minimal AGENTS.md with `Extends` only
2. **Discovery**: Scan code/docs/ADRs → propose specs
3. **Evolution**: Design decisions → update adapter specs
4. **Refinement**: Code patterns → update adapter specs

---

## Content Boundaries

**Should contain**:
- `**Extends**: ...` back to core `AGENTS.md`.
- Project-specific conventions and pointers:
  - Tech stack/tooling constraints.
  - Domain model format and location.
  - API contract format and location.
  - Validation/CI expectations.

**Should not contain**:
- PRD content (use PRD artifact).
- Architecture decisions rationale (use ADRs).
- Feature specs or implementation plans.

---

## Required Files

### .fdd-config.json

**Location**: `{project-root}/.fdd-config.json`

**Mandatory fields**:
```json
{
  "fddAdapterPath": "FDD-Adapter"
}
```

**Validation**:
- [ ] File exists at project root
- [ ] Valid JSON format
- [ ] `fddAdapterPath` field present
- [ ] Path points to existing directory with AGENTS.md

### AGENTS.md

**Location**: `{adapter-directory}/AGENTS.md`

**WHEN rule format** (mandatory for adapter navigation rules):
```
ALWAYS open and follow {spec-file} WHEN executing workflows: {workflow1.md}, {workflow2.md}, ...
```

---

## Two-Phase Validation

### Phase 1: Bootstrap (Minimal)

**When**: New project, no design yet

**Required content**:
```markdown
# FDD Adapter: {Project Name}

**Extends**: `{path}/FDD/AGENTS.md`
```

### Phase 2: Evolved Adapter

**When**: Project with DESIGN.md OR discovered codebase

**Additional required fields**:
- Version
- Last Updated
- Tech Stack

**Required spec files** (created dynamically):

| Spec File | Contains |
|-----------|----------|
| `tech-stack.md` | Languages, frameworks, databases |
| `domain-model.md` | Schema format, entity structure |
| `api-contracts.md` | Contract format, endpoint patterns |
| `patterns.md` | Architecture patterns |
| `conventions.md` | Naming, style, file organization |
| `build-deploy.md` | Build commands, CI/CD |
| `testing.md` | Test frameworks, structure |

---

## Validation Criteria

### Phase 1: Bootstrap

| Check | Required |
|-------|----------|
| AGENTS.md exists | YES |
| Contains project name heading | YES |
| Contains `**Extends**:` declaration | YES |

**Content boundaries checks**:
- [ ] No PRD content included
- [ ] No architecture decision rationale included
- [ ] No feature specs or implementation plans included

### Phase 2: Evolved Adapter

**Checks**:
- [ ] AGENTS.md exists with Extends
- [ ] Version and Last Updated fields present
- [ ] Tech Stack summary present
- [ ] MUST rules for each spec file
- [ ] No orphaned MUST rules
- [ ] tech-stack.md complete
- [ ] domain-model.md complete
- [ ] api-contracts.md complete
- [ ] patterns.md has ≥1 pattern
- [ ] conventions.md complete
- [ ] build-deploy.md complete
- [ ] testing.md complete (if present/required by adapter)
- [ ] Each spec references source
- [ ] All references valid
- [ ] Consistent with DESIGN (when applicable)

---

## Spec File Structure

Each spec file MUST include:

1. **Header**: Version, Purpose, Scope
2. **Content sections**: Specific to spec type
3. **Validation criteria**: Checklist for agent self-verification
4. **Examples**: Valid/invalid examples with checkmarks

---

## Common Issues

- Missing required sections and specifications
- Missing or invalid `**Extends**` declaration
- WHEN clauses not using workflow list format
- Orphaned MUST rules (specs missing)
- Inconsistent technology references

---

## Validation Checklist (Final)

- [ ] Document follows required structure
- [ ] All validation criteria pass
- [ ] Phase-appropriate validation applied
- [ ] Agent used template for generation
- [ ] Agent referenced example for validation

---

## References

**Template**: `../templates/adapter-AGENTS.template.md`

**Example**: `../templates/examples/adapter/AGENTS-EXAMPLE.md`

**Related**:
- `../AGENTS.md` — Core FDD requirements
- `workflow-requirements.md` — Workflow structure requirements
