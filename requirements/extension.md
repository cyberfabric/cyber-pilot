---
cypilot: true
type: requirement
name: Extension Mechanism
version: 1.0
purpose: Define how files extend other files using Extends directive
---

# Cypilot Extension Mechanism

---

## Table of Contents

- [Agent Instructions](#agent-instructions)
- [Overview](#overview)
- [How Extends Works](#how-extends-works)
- [Examples](#examples)
- [Extension Rules](#extension-rules)
- [Use Cases](#use-cases)
- [Error Handling](#error-handling)
- [Consolidated Validation Checklist](#consolidated-validation-checklist)
- [References](#references)

---

## Agent Instructions

**ALWAYS open and follow**: This file WHEN processing files with `**Extends**:` directive

**Prerequisite**: Agent confirms understanding before proceeding:
- [ ] Agent understands extension mechanism concept
- [ ] Agent has identified the base file being extended
- [ ] Agent will follow the rules defined here

---

## Overview

**Extension mechanism** - Allows files to inherit content from base files and add modifications

**Format**: `**Extends**: {path-to-base-file}`

**Applies to**: AGENTS.md, specification files, requirements files

---

## How Extends Works

### Basic Rule

**When file has `**Extends**: {base-file}`**:

1. Load base file first
2. Load current file
3. Merge = base content + current modifications
4. Never skip base
5. Never replace base rules entirely

### Loading Order

```
Base File (loaded first)
    ↓
Current File (loaded second)
    ↓
Merged Result (base + modifications)
```

### Merge Behavior

**Base content** is ALWAYS included

**Current file** can:
- ✅ Add new sections
- ✅ Add new rules
- ✅ Add new instructions
- ✅ Override specific values (if explicitly stated)
- ❌ Remove base rules
- ❌ Contradict base principles

---

## Examples

### Valid Extension

**Base**: `Cypilot/AGENTS.md`
```markdown
See [PRD.md](PRD.md)
See [ADR](ADR/)
See [api.json](../../../docs/api/api.json)
```
ALWAYS open and follow `.cypilot-adapter/specs/conventions.md` WHEN modifying Cypilot files
```

**Extension**: `{adapter-directory}/AGENTS.md`
```markdown
# Project AI Agent Navigation

**Extends**: `../Cypilot/AGENTS.md`

ALWAYS open and follow `{adapter-directory}/domain-model.gts` WHEN executing workflows: design/, design-validate/, adr/, adr-validate/
ALWAYS open and follow `{adapter-directory}/api-contracts.yaml` WHEN executing workflows: design.md, design-validate.md, adr.md, adr-validate.md
```

**Result**: Agent reads Cypilot/AGENTS.md first, then adds project-specific instructions

### Invalid Extension

```markdown
# Project AI Agent Navigation

**Extends**: `../Cypilot/AGENTS.md`

# This contradicts base - INVALID
DO NOT read requirements files
```

---

## Extension Rules

**MUST**:
- Specify exact path to base file
- Load base file before processing current file
- Preserve all base rules and instructions
- Add modifications that complement base

**MUST NOT**:
- Skip loading base file
- Remove base rules
- Contradict base principles
- Create circular dependencies (A extends B, B extends A)

---

## Use Cases

### AGENTS.md Extension

**Base**: Core Cypilot navigation  
**Extension**: Project-specific navigation (domain model, API contracts, tech stack)

### Requirements Extension

**Base**: General structure requirements  
**Extension**: Project-specific validation rules

### Specification Extension

**Base**: Core syntax/grammar  
**Extension**: Project-specific extensions to syntax

---

## Error Handling

### Base File Not Found

**If base file specified in Extends doesn't exist**:
```
⚠️ Base file not found: {path}
→ Verify path is correct relative to extension file location
→ Check if base file was moved or renamed
→ Fix Extends path or create missing base file
```
**Action**: STOP — extension cannot be processed without base.

### Circular Dependency Detected

**If extension chain creates a loop**:
```
⚠️ Circular dependency detected: {A} → {B} → {A}
→ Extension chains must be acyclic
→ Review Extends declarations in both files
→ Remove one direction of the extension
```
**Action**: STOP — circular dependencies cause infinite loading.

### Base File Unreadable

**If base file exists but cannot be read**:
```
⚠️ Cannot read base file: {path}
→ Check file permissions
→ Verify file is not corrupted
→ Check file encoding is UTF-8
```
**Action**: STOP — cannot merge without reading base content.

### Contradiction Detected

**If extension contradicts base rules**:
```
⚠️ Extension contradicts base: {description}
→ Extension at: {extension_path}
→ Base rule at: {base_path}:{line}
→ Fix: Remove contradicting instruction OR use override syntax
```
**Action**: FAIL validation — contradictions invalidate extension.

### Deep Extension Chain

**If extension chain exceeds reasonable depth**:
```
⚠️ Deep extension chain detected: {depth} levels
→ Chain: {A} → {B} → {C} → ...
→ Consider flattening chain or restructuring inheritance
```
**Action**: WARN and continue — deep chains increase complexity and loading time.

---

## Consolidated Validation Checklist

**Use this single checklist for all extension validation.**

### Structure (S)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| S.1 | `**Extends**:` directive present in header | YES | Pattern match in first 20 lines |
| S.2 | Base file path specified correctly | YES | Path string is non-empty |
| S.3 | Path format is correct (relative or absolute) | YES | Valid path syntax |
| S.4 | Extension file has proper header | YES | Title and metadata present |

### Accessibility (A)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| A.1 | Base file exists at specified path | YES | File exists at resolved path |
| A.2 | Base file is readable | YES | Read operation succeeds |
| A.3 | Base file path is correct relative to extension file | YES | Path resolution from extension directory |
| A.4 | No broken references in base file | YES | All links in base file resolve |

### Merge Correctness (M)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| M.1 | Extension adds new content | YES | Content diff shows additions |
| M.2 | Extension doesn't contradict base rules | YES | No MUST NOT violations of base MUST |
| M.3 | Extension doesn't remove base content | YES | All base sections still accessible |
| M.4 | Extension complements base appropriately | YES | New content aligns with base purpose |

### Dependency (D)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| D.1 | No circular dependencies | YES | DFS traversal detects no cycles |
| D.2 | Base file is loaded before extension | YES | Loading order verified |
| D.3 | Extension chain is finite | YES | Chain depth < 10 levels |
| D.4 | All base files in chain are accessible | YES | Each Extends target exists |

### Final (F)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| F.1 | All Structure checks pass | YES | S.1-S.4 verified |
| F.2 | All Accessibility checks pass | YES | A.1-A.4 verified |
| F.3 | All Merge Correctness checks pass | YES | M.1-M.4 verified |
| F.4 | All Dependency checks pass | YES | D.1-D.4 verified |

---

## References

**This file is referenced by**:
- All files using **Extends** directive

**References**:
- `../.cypilot-adapter/specs/patterns.md` - Defines structure for AGENTS.md files
- `adapter-structure.md` - Requires adapter AGENTS.md to extend Cypilot AGENTS.md
