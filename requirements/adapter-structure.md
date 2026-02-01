---
fdd: true
type: requirement
name: Adapter Structure
version: 1.1
purpose: Define validation rules for FDD adapter files
---

# FDD Adapter Structure Requirements

---

## Table of Contents

- [Agent Instructions](#agent-instructions)
- [Overview](#overview)
- [Content Boundaries](#content-boundaries)
- [Required Files](#required-files)
- [Two-Phase Validation](#two-phase-validation)
- [Spec File Structure](#spec-file-structure)
- [Error Handling](#error-handling)
- [Consolidated Validation Checklist](#consolidated-validation-checklist)
- [Common Issues](#common-issues)
- [References](#references)

---

## Agent Instructions

**ALWAYS open and follow**: `../workflows/adapter.md` WHEN executing workflow

**ALWAYS open and follow**: `../templates/adapter-AGENTS.template.md` WHEN generating adapter AGENTS.md

**ALWAYS open**: `../templates/examples/adapter/AGENTS-EXAMPLE.md` WHEN reviewing valid artifact structure

**Prerequisite**: Agent confirms understanding before proceeding:
- [ ] Agent has read and understood this requirement
- [ ] Agent will follow the rules defined here

---

## Overview

- **This file defines**: Validation rules — see [Consolidated Validation Checklist](#consolidated-validation-checklist)
- **Template defines**: Structure for generation (HOW to create)
- **Workflow defines**: Process (STEP by STEP)

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
ALWAYS open and follow `{spec-file}` WHEN FDD follows rules `{rule-id}` for artifact kinds: {KIND1}, {KIND2} [OR codebase]
```

**Valid artifact kinds**: As defined in `artifacts.json` rules section. Standard FDD kinds: PRD, DESIGN, FEATURES, ADR, FEATURE. Custom kinds may be added per project.

**Codebase**: Use `OR codebase` when spec applies to code validation/generation

**Valid examples** ✅:
```markdown
ALWAYS open and follow `specs/tech-stack.md` WHEN FDD follows rules `fdd-sdlc` for artifact kinds: DESIGN, ADR OR codebase

ALWAYS open and follow `specs/conventions.md` WHEN FDD follows rules `fdd-sdlc` for codebase

ALWAYS open and follow `specs/domain-model.md` WHEN FDD follows rules `fdd-sdlc` for artifact kinds: DESIGN, FEATURES, FEATURE
```

**Invalid examples** ❌:
```markdown
# Missing rule ID
ALWAYS open and follow `specs/tech-stack.md` WHEN generating DESIGN
→ FIX: Add `FDD follows rules `fdd-sdlc` for artifact kinds:`

# Using legacy workflow format
ALWAYS open and follow `specs/tech-stack.md` WHEN executing workflows: fdd-generate, fdd-validate
→ FIX: Use rules-based format with artifact kinds

# Missing artifact kinds
ALWAYS open and follow `specs/tech-stack.md` WHEN FDD follows rules `fdd-sdlc`
→ FIX: Specify `for artifact kinds: X, Y` or `for codebase`
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

**Required spec files** (created by `/fdd-adapter` during Discovery phase or manually):

| Spec File | Contains | Created When |
|-----------|----------|--------------|
| `tech-stack.md` | Languages, frameworks, databases | DESIGN.md references tech stack |
| `domain-model.md` | Schema format, entity structure | DESIGN.md defines domain entities |
| `api-contracts.md` | Contract format, endpoint patterns | DESIGN.md includes API specs |
| `patterns.md` | Architecture patterns | ADR or DESIGN references patterns |
| `conventions.md` | Naming, style, file organization | Codebase exists OR DESIGN defines conventions |
| `build-deploy.md` | Build commands, CI/CD | Project has build/deploy config |
| `testing.md` | Test frameworks, structure | Project has test infrastructure |

**Creation trigger**: Run `/fdd-adapter --rescan` to auto-detect and propose spec files based on project state.

---

## Validation Criteria

**See [Consolidated Validation Checklist](#consolidated-validation-checklist)** for complete validation criteria.

Quick reference:
- **Phase 1 (Bootstrap)**: Checks 1.1-1.10
- **Phase 2 (Evolved)**: Checks 2.1-2.15
- **Final**: Checks F.1-F.4

---

## Spec File Structure

Each spec file MUST include:

1. **Header**: Version, Purpose, Scope
2. **Content sections**: Specific to spec type
3. **Validation criteria**: Checklist for agent self-verification
4. **Examples**: Valid/invalid examples with checkmarks

---

## Error Handling

### Missing Referenced Files

**If template file not found** (`../templates/adapter-AGENTS.template.md`):
```
⚠️ Template not found: {path}
→ Verify FDD installation is complete
→ Check path is relative to requirements/ directory
```
**Action**: STOP — cannot generate without template.

**If example file not found** (`../templates/examples/adapter/AGENTS-EXAMPLE.md`):
```
⚠️ Example not found: {path}
→ Proceed with template only (reduced quality assurance)
```
**Action**: WARN and continue.

**If spec file referenced in AGENTS.md doesn't exist**:
```
⚠️ Orphaned WHEN rule: {spec-file} not found
→ Create spec file OR remove WHEN rule from AGENTS.md
```
**Action**: Validation FAIL — orphaned references must be resolved.

### Validation Failures

**If Phase 1 validation fails**:
1. Check AGENTS.md exists at adapter path
2. Verify `**Extends**:` declaration present
3. Verify Extends path points to valid FDD AGENTS.md

**If Phase 2 validation fails**:
1. Identify which spec files are missing
2. Run `/fdd-adapter --rescan` to regenerate
3. For each failed check, see [Consolidated Validation Checklist](#consolidated-validation-checklist)

**Recovery**: After fixing issues, re-run `/fdd-validate` to confirm resolution.

---

## Consolidated Validation Checklist

**Use this single checklist for all adapter validation** (replaces scattered criteria above).

### Phase 1: Bootstrap (Minimal Adapter)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| 1.1 | `.fdd-config.json` exists at project root | YES | File exists check |
| 1.2 | `.fdd-config.json` is valid JSON | YES | JSON parse succeeds |
| 1.3 | `fddAdapterPath` field present | YES | Field exists in JSON |
| 1.4 | Adapter path points to directory with AGENTS.md | YES | Path + `/AGENTS.md` exists |
| 1.5 | AGENTS.md has project name heading | YES | `# FDD Adapter: {name}` present |
| 1.6 | AGENTS.md has `**Extends**:` declaration | YES | Pattern match |
| 1.7 | Extends path resolves to valid file | YES | File exists at path |
| 1.8 | No PRD content in adapter | YES | No problem/solution/scope sections |
| 1.9 | No ADR rationale in adapter | YES | No decision rationale sections |
| 1.10 | No feature specs in adapter | YES | No requirement IDs or flows |

### Phase 2: Evolved Adapter (with specs)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| 2.1 | All Phase 1 checks pass | YES | Run Phase 1 first |
| 2.2 | Version field present | YES | `**Version**:` in AGENTS.md |
| 2.3 | Last Updated field present | YES | `**Last Updated**:` in AGENTS.md |
| 2.4 | Tech Stack summary present | YES | Tech Stack section exists |
| 2.5 | WHEN rules use rules-based format | YES | Pattern: `WHEN FDD follows rules` |
| 2.6 | No orphaned WHEN rules | YES | All referenced specs exist |
| 2.7 | tech-stack.md complete | CONDITIONAL | If tech stack defined in DESIGN |
| 2.8 | domain-model.md complete | CONDITIONAL | If domain model in DESIGN |
| 2.9 | api-contracts.md complete | CONDITIONAL | If API defined in DESIGN |
| 2.10 | patterns.md has ≥1 pattern | CONDITIONAL | If patterns in DESIGN/ADR |
| 2.11 | conventions.md complete | CONDITIONAL | If codebase exists |
| 2.12 | build-deploy.md complete | CONDITIONAL | If build config exists |
| 2.13 | testing.md complete | CONDITIONAL | If test infra exists |
| 2.14 | Each spec has source reference | YES | "Source:" field in each spec |
| 2.15 | Consistent with DESIGN.md | YES | Cross-reference check |

### Final Verification

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| F.1 | Agent used template for generation | YES | Template path appears in agent context/logs |
| F.2 | Agent referenced example for validation | YES | Example path appears in agent context/logs |
| F.3 | Phase-appropriate validation applied | YES | Phase 1 OR Phase 2 checklist completed |
| F.4 | All applicable checks pass | YES | No FAIL status in checklist results |

---

## Common Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| Missing Extends | Validation fails at 1.6 | Add `**Extends**: \`{path}/FDD/AGENTS.md\`` |
| Legacy WHEN format | Validation fails at 2.5 | Convert to `WHEN FDD follows rules \`{id}\` for artifact kinds:` |
| Orphaned WHEN rules | Validation fails at 2.6 | Create missing spec OR remove rule |
| Inconsistent tech refs | Spec conflicts with DESIGN | Update spec to match DESIGN source of truth |
| Missing spec files | Validation fails at 2.7-2.13 | Run `/fdd-adapter --rescan` to generate |
| PRD content in adapter | Validation fails at 1.8 | Move to PRD artifact |

---

## References

**Template**: `../templates/adapter-AGENTS.template.md`

**Example**: `../templates/examples/adapter/AGENTS-EXAMPLE.md`

**Related**:
- `../AGENTS.md` — Core FDD requirements
- `workflow-requirements.md` — Workflow structure requirements
