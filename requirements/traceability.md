---
fdd: true
type: requirement
name: Code Traceability Specification
version: 1.1
purpose: Define FDD code traceability markers and validation rules
---

# Code Traceability Specification

## Table of Contents

1. [Overview](#overview)
2. [Quick Reference](#quick-reference)
3. [Traceability Mode](#traceability-mode)
4. [Marker Syntax](#marker-syntax)
5. [Marker Rules](#marker-rules)
6. [Versioning](#versioning)
7. [Design Synchronization](#design-synchronization)
8. [Agent Workflow](#agent-workflow)
9. [Common Errors](#common-errors)
10. [Validation](#validation)
11. [References](#references)

---

## Quick Reference

**Scope marker** (single-line):
```
@fdd-{kind}:{full-id}:ph-{N}
```

**Block markers** (paired):
```
@fdd-begin:{full-id}:ph-{N}:inst-{local}
...code...
@fdd-end:{full-id}:ph-{N}:inst-{local}
```

**Validate markers**:
```bash
python3 {FDD}/skills/fdd/scripts/fdd.py validate-code
```

---

## Overview

FDD code traceability links design artifacts (FEATURE designs) to implementation code through markers. This enables:
- Automated verification that design is implemented
- Bidirectional navigation between design and code
- Progress tracking via checkbox synchronization

---

## Traceability Mode

### Mode Determination

**Traceability Mode is ON when ALL conditions are met:**

1. Target artifact is registered in `artifacts.json`
2. Artifact has `traceability: "FULL"` (not `"DOCS-ONLY"`)
3. Artifact kind is `FEATURE` (feature design document)

**Mode lookup:**
```
artifacts.json → systems[].artifacts[] → { path, kind, traceability }
```

### Mode Effects

| Mode | Code Markers | Checkbox Sync | Tag Verification |
|------|--------------|---------------|------------------|
| `FULL` | Required | Required | Required |
| `DOCS-ONLY` | Prohibited | N/A | N/A |

---

## Marker Syntax

### Scope Markers (Single-line)

Mark scope entry points (functions, classes, modules):

```
@fdd-{kind}:{full-id}:ph-{N}
```

**Kinds:**
- `@fdd-flow:{id}:ph-{N}` — Actor flow implementation
- `@fdd-algo:{id}:ph-{N}` — Algorithm implementation
- `@fdd-state:{id}:ph-{N}` — State machine implementation
- `@fdd-req:{id}:ph-{N}` — Requirement implementation
- `@fdd-test:{id}:ph-{N}` — Test scenario implementation

**Format:**
- `{id}` — Full FDD ID from design (e.g., `fdd-myapp-feature-auth-flow-login`)
- `ph-{N}` — Phase number (mandatory postfix)

**Example:**
```python
# @fdd-flow:fdd-myapp-feature-auth-flow-login:ph-1
def login_flow(request):
    ...
```

### Block Markers (Paired)

Wrap specific FDL instruction implementations:

```
@fdd-begin:{full-id}:ph-{N}:inst-{local}
...code...
@fdd-end:{full-id}:ph-{N}:inst-{local}
```

**Format:**
- `{full-id}` — Full FDD ID from design
- `ph-{N}` — Phase number
- `inst-{local}` — Instruction ID from FDL step (e.g., `inst-validate-creds`)

**Example:**
```python
# @fdd-begin:fdd-myapp-feature-auth-flow-login:ph-1:inst-validate-creds
def validate_credentials(username, password):
    if not username or not password:
        raise ValidationError("Missing credentials")
    return authenticate(username, password)
# @fdd-end:fdd-myapp-feature-auth-flow-login:ph-1:inst-validate-creds
```

### Language-Specific Comment Syntax

| Language | Single-line | Block start | Block end |
|----------|-------------|-------------|-----------|
| Python | `# @fdd-...` | `# @fdd-begin:...` | `# @fdd-end:...` |
| TypeScript/JS | `// @fdd-...` | `// @fdd-begin:...` | `// @fdd-end:...` |
| Go | `// @fdd-...` | `// @fdd-begin:...` | `// @fdd-end:...` |
| Rust | `// @fdd-...` | `// @fdd-begin:...` | `// @fdd-end:...` |
| Java | `// @fdd-...` | `// @fdd-begin:...` | `// @fdd-end:...` |

---

## Marker Rules

### Placement Rules

1. **Scope markers**: Place at beginning of function/method/class implementing the scope
2. **Block markers**: Wrap exact code implementing FDL instruction
3. **Multiple markers**: Allowed when code implements multiple IDs
4. **External dependencies**: Place on integration point (import/registration)

### Pairing Rules

1. **Every `@fdd-begin` MUST have matching `@fdd-end`**
2. **Same ID required**: Begin and end must have identical ID string
3. **No empty blocks**: Code MUST exist between begin/end
4. **No nesting**: Block markers cannot be nested

### ID Rules

1. **Exact match**: Marker ID must exactly match design ID
2. **Phase required**: All markers must include `:ph-{N}` postfix
3. **No invention**: Use only IDs that exist in design (no new IDs)

---

## Versioning

When design ID is versioned:

| Design ID | Code Marker |
|-----------|-------------|
| `fdd-app-feature-auth-flow-login` | `@fdd-flow:fdd-app-feature-auth-flow-login:ph-1` |
| `fdd-app-feature-auth-flow-login-v2` | `@fdd-flow:fdd-app-feature-auth-flow-login-v2:ph-1` |

**Migration:**
- When design version increments, update all code markers
- Old markers may be kept commented during transition

---

## Design Synchronization

### Checkbox Rules

When code marker exists and is valid:
- Mark corresponding FDL instruction `- [ ]` → `- [x]` in design

When all instructions in scope are `[x]`:
- Mark parent scope `- [ ]` → `- [x]` in design

### Status Rules

| Condition | Requirement Status |
|-----------|-------------------|
| First instruction implemented | `🔄 IN_PROGRESS` |
| All instructions implemented | `✅ IMPLEMENTED` |

---

## Agent Workflow

### When to Add Markers

**During code implementation** (via `/fdd-generate CODE`):

1. **Before writing code**: Identify which design IDs you're implementing
2. **At function/class level**: Add scope marker as first line in docstring/comment
3. **For specific instructions**: Wrap implementation with begin/end markers
4. **After implementation**: Run `validate-code` to verify coverage

### Marker Placement Workflow

```
1. Read FEATURE design → identify ID with to_code="true"
2. Locate existing code OR create new file
3. Add scope marker at entry point (function/class)
4. Add block markers around instruction implementations
5. Run validation: python3 {FDD}/skills/fdd/scripts/fdd.py validate-code
6. Update design checkbox if implementation complete
```

### Multi-ID Implementation

When one function implements multiple design IDs:
- Add multiple scope markers (one per ID)
- Each instruction block gets its own begin/end pair
- Order markers by ID hierarchy (parent first, then children)

---

## Common Errors

### ❌ Missing Phase Postfix

```python
# WRONG - missing :ph-N
# @fdd-flow:fdd-app-feature-auth-flow-login
def login(): ...

# CORRECT
# @fdd-flow:fdd-app-feature-auth-flow-login:ph-1
def login(): ...
```

### ❌ Mismatched Begin/End IDs

```python
# WRONG - IDs don't match
# @fdd-begin:fdd-app-feature-auth-flow-login:ph-1:inst-validate
def validate(): ...
# @fdd-end:fdd-app-feature-auth-flow-login:ph-1:inst-check  # DIFFERENT!

# CORRECT - IDs match exactly
# @fdd-begin:fdd-app-feature-auth-flow-login:ph-1:inst-validate
def validate(): ...
# @fdd-end:fdd-app-feature-auth-flow-login:ph-1:inst-validate
```

### ❌ Invented IDs

```python
# WRONG - ID doesn't exist in design
# @fdd-flow:fdd-app-feature-auth-flow-my-custom-thing:ph-1
def my_function(): ...

# CORRECT - Use only IDs from design document
# @fdd-flow:fdd-app-feature-auth-flow-login:ph-1
def login_flow(): ...
```

### ❌ Empty Block

```python
# WRONG - no code between markers
# @fdd-begin:fdd-app-feature-auth-flow-login:ph-1:inst-validate
# @fdd-end:fdd-app-feature-auth-flow-login:ph-1:inst-validate

# CORRECT - actual implementation between markers
# @fdd-begin:fdd-app-feature-auth-flow-login:ph-1:inst-validate
def validate_credentials(user, password):
    return authenticate(user, password)
# @fdd-end:fdd-app-feature-auth-flow-login:ph-1:inst-validate
```

### ❌ Nested Blocks

```python
# WRONG - nested block markers
# @fdd-begin:...:inst-outer
# @fdd-begin:...:inst-inner  # NESTING NOT ALLOWED
# ...
# @fdd-end:...:inst-inner
# @fdd-end:...:inst-outer

# CORRECT - sequential blocks
# @fdd-begin:...:inst-outer
# ...
# @fdd-end:...:inst-outer
# @fdd-begin:...:inst-inner
# ...
# @fdd-end:...:inst-inner
```

---

## Validation

### Deterministic Checks

1. **Marker format**: Syntax matches specification
2. **Pairing**: All begin markers have matching end
3. **No empty blocks**: Code exists between begin/end
4. **Phase postfix**: All markers include `:ph-{N}`

### Traceability Checks

1. **Coverage**: All `to_code="true"` IDs have markers in code
2. **No orphans**: All code markers reference existing design IDs
3. **No stale**: All referenced design IDs still exist
4. **Sync**: Markers match checkbox state in design

### Validation Report

```
Traceability Validation Report
══════════════════════════════

Mode: FULL | DOCS-ONLY
Design IDs (to_code="true"): N
Code markers found: M

Coverage: P%

Missing markers:
  - {id} (no marker in code)

Orphaned markers:
  - {marker} (no design ID)

Sync errors:
  - {id} (marker exists but not [x] in design)

Pairing errors:
  - {marker} (missing @fdd-end)

Status: PASS | FAIL
```

---

## References

- **Design artifacts**: `artifacts.json → systems[].artifacts[]`
- **Traceability setting**: `artifact.traceability = "FULL" | "DOCS-ONLY"`
- **FDL instruction format**: `requirements/FDL.md`
- **Template markers**: `requirements/template.md`
- **Validation command**: `python3 {FDD}/skills/fdd/scripts/fdd.py validate-code`
