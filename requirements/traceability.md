---
fdd: true
type: requirement
name: Code Traceability Specification
version: 1.0
purpose: Define FDD code traceability markers and validation rules
---

# Code Traceability Specification

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
