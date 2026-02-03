---
spider: true
type: requirement
name: Code Traceability Specification
version: 1.2
purpose: Define Spider code traceability markers and validation rules (weaver-agnostic)
---

# Code Traceability Specification

## Table of Contents

1. [Overview](#overview)
2. [Quick Reference](#quick-reference)
3. [Weaver Ownership](#weaver-ownership)
4. [Marker Syntax](#marker-syntax)
5. [Traceability Mode](#traceability-mode)
6. [Validation Rules](#validation-rules)
7. [Versioning](#versioning)
8. [Common Errors](#common-errors)
9. [References](#references)

---

## Quick Reference

**Scope marker** (single-line):
```
@spider-{kind}:{spd-id}:p{N}
```

**Block markers** (paired):
```
@spider-begin:{spd-id}:p{N}:inst-{local}
...code...
@spider-end:{spd-id}:p{N}:inst-{local}
```

**Validate markers**:
```bash
python3 {Spider}/skills/spider/scripts/spider.py validate-code
```

---

## Overview

Spider code traceability links IDs defined in artifacts to implementation code through markers. This enables:
- Automated verification that code references real, registered design IDs
- Coverage checks for IDs explicitly marked as requiring implementation (`to_code="true"`)
- Bidirectional navigation between artifacts and code (via ID search)

This specification is **weaver-agnostic**:
- This document defines the **generic marker format** and generic validation expectations.
- The active weaver (registered in `artifacts.json`) defines:
  - which artifact kinds exist
  - which IDs exist and which are marked `to_code="true"`
  - what `{kind}` values are meaningful for that weaver

---

## Weaver Ownership

Spider core does not require a fixed list of `{kind}` values.

To understand which kinds exist and what they mean for your project:
1. Identify the active weaver for a system in `artifacts.json`.
2. Read that weaver’s taxonomy guide: `weavers/<weaver>/guides/TAXONOMY.md`.
3. Use weaver templates/rules to determine which IDs must be implemented in code (`to_code="true"`) and how.

---

## Marker Syntax

### Scope Markers (Single-line)

Mark scope entry points (functions, classes, modules):

```
@spider-{kind}:{spd-id}:p{N}
```

**Kind token (`{kind}`):**
`{kind}` is a weaver-defined string that classifies what the marker is about (for example, a behavior type, a requirement type, a test type, etc.).

Spider tools validate marker structure and referenced IDs; additional constraints on `{kind}` (allowed values, meaning, mapping to artifact kinds) are weaver-owned.

**Format:**
- `{spd-id}` — Full Spider ID defined in artifacts (e.g., `spd-my-system-...`)
- `p{N}` — Phase number (required)

**Example:**
```python
# @spider-flow:spd-my-system-feature-core-auth-v2:p1
def login_flow(request):
    ...
```

### Block Markers (Paired)

Wrap specific SDSL instruction implementations:

```
@spider-begin:{spd-id}:p{N}:inst-{local}
...code...
@spider-end:{spd-id}:p{N}:inst-{local}
```

**Format:**
- `{spd-id}` — Full Spider ID defined in artifacts
- `p{N}` — Phase number
- `inst-{local}` — Local instruction identifier (the meaning and source of this value is weaver-defined)

**Example:**
```python
# @spider-begin:spd-my-system-feature-core-auth-v2:p1:inst-fetch-tenant-from-db
def validate_credentials(username, password):
    if not username or not password:
        raise ValidationError("Missing credentials")
    return authenticate(username, password)
# @spider-end:spd-my-system-feature-core-auth-v2:p1:inst-fetch-tenant-from-db
```

### Language-Specific Comment Syntax

| Language | Single-line | Block start | Block end |
|----------|-------------|-------------|-----------|
| Python | `# @spider-...` | `# @spider-begin:...` | `# @spider-end:...` |
| TypeScript/JS | `// @spider-...` | `// @spider-begin:...` | `// @spider-end:...` |
| Go | `// @spider-...` | `// @spider-begin:...` | `// @spider-end:...` |
| Rust | `// @spider-...` | `// @spider-begin:...` | `// @spider-end:...` |
| Java | `// @spider-...` | `// @spider-begin:...` | `// @spider-end:...` |

---

## Traceability Mode

Traceability mode is configured in `artifacts.json` (and may be further constrained by weaver rules).

At minimum, Spider distinguishes:

- `FULL`: markers are allowed and validated.
  - Structural checks apply (pairing, no empty blocks, etc.).
  - Cross-validation applies: code markers must reference IDs that exist in artifacts.
  - Coverage applies: any ID marked `to_code="true"` in artifacts must be referenced by at least one code marker.
- `DOCS-ONLY`: code markers are prohibited for the affected scope.

Registry lookup (conceptual):
```
artifacts.json → systems[] → { weaver, artifacts[], codebase[] }
```

Note: specific scoping rules (per-system vs per-artifact vs per-codebase-entry) are implementation-defined; weaver documentation should describe the expected policy for your project.

## Validation Rules

### Placement Rules

1. **Scope markers**: Place at beginning of function/method/class implementing the scope
2. **Block markers**: Wrap exact code implementing SDSL instruction
3. **Multiple markers**: Allowed when code implements multiple IDs
4. **External dependencies**: Place on integration point (import/registration)

### Pairing Rules

1. **Every `@spider-begin` MUST have matching `@spider-end`**
2. **Same ID required**: Begin and end must have identical ID string
3. **No empty blocks**: Code MUST exist between begin/end
4. **No nesting**: Block markers cannot be nested

### ID Rules

1. **Exact match**: Marker ID must exactly match design ID
2. **Phase required**: All markers must include `:p{N}` postfix
3. **No invention**: Use only IDs that exist in design (no new IDs)

---

## Versioning

When design ID is versioned:

| Design ID | Code Marker |
|-----------|-------------|
| `spd-app-feature-auth-flow-login` | `@spider-flow:spd-app-feature-auth-flow-login:p1` |
| `spd-app-feature-auth-flow-login-v2` | `@spider-flow:spd-app-feature-auth-flow-login-v2:p1` |

**Migration:**
- When design version increments, update all code markers
- Old markers may be kept commented during transition

---

## Validation

Run:
```bash
python3 {Spider}/skills/spider/scripts/spider.py validate-code
```

---

## Common Errors

### ❌ Missing Phase Postfix

```python
# WRONG - missing :pN
# @spider-flow:spd-app-feature-auth-flow-login
def login(): ...

# CORRECT
# @spider-flow:spd-app-feature-auth-flow-login:p1
def login(): ...
```

### ❌ Mismatched Begin/End IDs

```python
# WRONG - IDs don't match
# @spider-begin:spd-app-feature-auth-flow-login:p1:inst-validate
def validate(): ...
# @spider-end:spd-app-feature-auth-flow-login:p1:inst-check  # DIFFERENT!

# CORRECT - IDs match exactly
# @spider-begin:spd-app-feature-auth-flow-login:p1:inst-validate
def validate(): ...
# @spider-end:spd-app-feature-auth-flow-login:p1:inst-validate
```

### ❌ Invented IDs

```python
# WRONG - ID doesn't exist in design
# @spider-flow:spd-app-feature-auth-flow-my-custom-thing:p1
def my_function(): ...

# CORRECT - Use only IDs from design document
# @spider-flow:spd-app-feature-auth-flow-login:p1
def login_flow(): ...
```

### ❌ Empty Block

```python
# WRONG - no code between markers
# @spider-begin:spd-app-feature-auth-flow-login:p1:inst-validate
# @spider-end:spd-app-feature-auth-flow-login:p1:inst-validate

# CORRECT - actual implementation between markers
# @spider-begin:spd-app-feature-auth-flow-login:p1:inst-validate
def validate_credentials(user, password):
    return authenticate(user, password)
# @spider-end:spd-app-feature-auth-flow-login:p1:inst-validate
```

### ❌ Nested Blocks

```python
# WRONG - nested block markers
# @spider-begin:...:inst-outer
# @spider-begin:...:inst-inner  # NESTING NOT ALLOWED
# ...
# @spider-end:...:inst-inner
# @spider-end:...:inst-outer

# CORRECT - sequential blocks
# @spider-begin:...:inst-outer
# ...
# @spider-end:...:inst-outer
# @spider-begin:...:inst-inner
# ...
# @spider-end:...:inst-inner
```

---

Validation performs:
- Deterministic checks (syntax, pairing, empty blocks, nesting)
- Cross-validation against artifacts (orphaned markers)
- Coverage checks driven by `to_code="true"` IDs (weaver-owned)

---

## References

- Registry: `artifacts.json`
- Weaver taxonomy: `weavers/<weaver>/guides/TAXONOMY.md`
- Template markers: `requirements/template.md`
- Validation command: `python3 {Spider}/skills/spider/scripts/spider.py validate-code`
