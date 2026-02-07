---
cypilot: true
type: requirement
name: Code Traceability Specification
version: 1.2
purpose: Define Cypilot code traceability markers and validation rules (kit-agnostic)
---

# Code Traceability Specification

## Table of Contents

1. [Overview](#overview)
2. [Quick Reference](#quick-reference)
3. [Kit Ownership](#kit-ownership)
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
@cpt-{kind}:{cpt-id}:p{N}
```

**Block markers** (paired):
```
@cpt-begin:{cpt-id}:p{N}:inst-{local}
...code...
@cpt-end:{cpt-id}:p{N}:inst-{local}
```

**Validate markers**:
```bash
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py validate-code
```

---

## Overview

Cypilot code traceability links IDs defined in artifacts to implementation code through markers. This enables:
- Automated verification that code references real, registered design IDs
- Coverage checks for IDs explicitly marked as requiring implementation (`to_code="true"`)
- Bidirectional navigation between artifacts and code (via ID search)

This specification is **kit-agnostic**:
- This document defines the **generic marker format** and generic validation expectations.
- The active kit (registered in `artifacts.json`) defines:
  - which artifact kinds exist
  - which IDs exist and which are marked `to_code="true"`
  - what `{kind}` values are meaningful for that kit

---

## Kit Ownership

Cypilot core does not require a fixed list of `{kind}` values.

To understand which kinds exist and what they mean for your project:
1. Identify the active kit for a system in `artifacts.json`.
2. Read that kit’s taxonomy guide: `kits/<kit>/guides/TAXONOMY.md`.
3. Use kit templates/rules to determine which IDs must be implemented in code (`to_code="true"`) and how.

---

## Marker Syntax

### Scope Markers (Single-line)

Mark scope entry points (functions, classes, modules):

```
@cpt-{kind}:{cpt-id}:p{N}
```

**Kind token (`{kind}`):**
`{kind}` is a kit-defined string that classifies what the marker is about (for example, a behavior type, a requirement type, a test type, etc.).

Cypilot tools validate marker structure and referenced IDs; additional constraints on `{kind}` (allowed values, meaning, mapping to artifact kinds) are kit-owned.

**Format:**
- `{cpt-id}` — Full Cypilot ID defined in artifacts (e.g., `cpt-my-system-...`)
- `p{N}` — Phase number (required)

**Example:**
```python
# @cpt-flow:cpt-my-system-spec-core-auth-v2:p1
def login_flow(request):
    ...
```

### Block Markers (Paired)

Wrap specific CDSL instruction implementations:

```
@cpt-begin:{cpt-id}:p{N}:inst-{local}
...code...
@cpt-end:{cpt-id}:p{N}:inst-{local}
```

**Format:**
- `{cpt-id}` — Full Cypilot ID defined in artifacts
- `p{N}` — Phase number
- `inst-{local}` — Local instruction identifier (the meaning and source of this value is kit-defined)

**Example:**
```python
# @cpt-begin:cpt-my-system-spec-core-auth-v2:p1:inst-fetch-tenant-from-db
def validate_credentials(username, password):
    if not username or not password:
        raise ValidationError("Missing credentials")
    return authenticate(username, password)
# @cpt-end:cpt-my-system-spec-core-auth-v2:p1:inst-fetch-tenant-from-db
```

### Language-Specific Comment Syntax

| Language | Single-line | Block start | Block end |
|----------|-------------|-------------|-----------|
| Python | `# @cpt-...` | `# @cpt-begin:...` | `# @cpt-end:...` |
| TypeScript/JS | `// @cpt-...` | `// @cpt-begin:...` | `// @cpt-end:...` |
| Go | `// @cpt-...` | `// @cpt-begin:...` | `// @cpt-end:...` |
| Rust | `// @cpt-...` | `// @cpt-begin:...` | `// @cpt-end:...` |
| Java | `// @cpt-...` | `// @cpt-begin:...` | `// @cpt-end:...` |

---

## Traceability Mode

Traceability mode is configured in `artifacts.json` (and may be further constrained by kit rules).

At minimum, Cypilot distinguishes:

- `FULL`: markers are allowed and validated.
  - Structural checks apply (pairing, no empty blocks, etc.).
  - Cross-validation applies: code markers must reference IDs that exist in artifacts.
  - Coverage applies: any ID marked `to_code="true"` in artifacts must be referenced by at least one code marker.
- `DOCS-ONLY`: code markers are prohibited for the affected scope.

Registry lookup (conceptual):
```
artifacts.json → systems[] → { kit, artifacts[], codebase[] }
```

Note: specific scoping rules (per-system vs per-artifact vs per-codebase-entry) are implementation-defined; kit documentation should describe the expected policy for your project.

## Validation Rules

### Placement Rules

1. **Scope markers**: Place at beginning of function/method/class implementing the scope
2. **Block markers**: Wrap exact code implementing CDSL instruction
3. **Multiple markers**: Allowed when code implements multiple IDs
4. **External dependencies**: Place on integration point (import/registration)

### Pairing Rules

1. **Every `@cpt-begin` MUST have matching `@cpt-end`**
2. **Same ID required**: Begin and end must have identical ID string
3. **No empty blocks**: Code MUST exist between begin/end
4. **Nesting allowed**: Block markers MAY be nested, but MUST be properly nested (well-formed) and MUST NOT overlap/cross

### ID Rules

1. **Exact match**: Marker ID must exactly match design ID
2. **Phase required**: All markers must include `:p{N}` postfix
3. **No invention**: Use only IDs that exist in design (no new IDs)

---

## Versioning

When design ID is versioned:

| Design ID | Code Marker |
|-----------|-------------|
| `cpt-app-spec-auth-flow-login` | `@cpt-flow:cpt-app-spec-auth-flow-login:p1` |
| `cpt-app-spec-auth-flow-login-v2` | `@cpt-flow:cpt-app-spec-auth-flow-login-v2:p1` |

**Migration:**
- When design version increments, update all code markers
- Old markers may be kept commented during transition

---

## Validation

Run:
```bash
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py validate-code
```

---

## Common Errors

### ❌ Missing Phase Postfix

```python
# WRONG - missing :pN
# @cpt-flow:cpt-app-spec-auth-flow-login
def login(): ...

# CORRECT
# @cpt-flow:cpt-app-spec-auth-flow-login:p1
def login(): ...
```

### ❌ Mismatched Begin/End IDs

```python
# WRONG - IDs don't match
# @cpt-begin:cpt-app-spec-auth-flow-login:p1:inst-validate
def validate(): ...
# @cpt-end:cpt-app-spec-auth-flow-login:p1:inst-check  # DIFFERENT!

# CORRECT - IDs match exactly
# @cpt-begin:cpt-app-spec-auth-flow-login:p1:inst-validate
def validate(): ...
# @cpt-end:cpt-app-spec-auth-flow-login:p1:inst-validate
```

### ❌ Invented IDs

```python
# WRONG - ID doesn't exist in design
# @cpt-flow:cpt-app-spec-auth-flow-my-custom-thing:p1
def my_function(): ...

# CORRECT - Use only IDs from design document
# @cpt-flow:cpt-app-spec-auth-flow-login:p1
def login_flow(): ...
```

### ❌ Empty Block

```python
# WRONG - no code between markers
# @cpt-begin:cpt-app-spec-auth-flow-login:p1:inst-validate
# @cpt-end:cpt-app-spec-auth-flow-login:p1:inst-validate

# CORRECT - actual implementation between markers
# @cpt-begin:cpt-app-spec-auth-flow-login:p1:inst-validate
def validate_credentials(user, password):
    return authenticate(user, password)
# @cpt-end:cpt-app-spec-auth-flow-login:p1:inst-validate
```

---

Validation performs:
- Deterministic checks (syntax, pairing, empty blocks, nesting)
- Cross-validation against artifacts (orphaned markers)
- Coverage checks driven by `to_code="true"` IDs (kit-owned)

---

## References

- Registry: `artifacts.json`
- Kit taxonomy: `kits/<kit>/guides/TAXONOMY.md`
- Template markers: `requirements/template.md`
- Validation command: `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py validate-code`
