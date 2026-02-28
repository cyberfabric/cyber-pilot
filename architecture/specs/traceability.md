---
cypilot: true
type: spec
name: Identifiers & Traceability Specification
version: 2.0
purpose: Define artifact ID formats, naming conventions, task marker semantics, code traceability markers, and validation rules
drivers:
  - cpt-cypilot-fr-core-traceability
  - cpt-cypilot-component-traceability-engine
---

# Identifiers & Traceability Specification

---

## Table of Contents

- [Identifiers \& Traceability Specification](#identifiers--traceability-specification)
  - [Table of Contents](#table-of-contents)
  - [Quick Reference](#quick-reference)
  - [Part I — Identifiers](#part-i--identifiers)
    - [ID Format](#id-format)
    - [ID Naming Convention](#id-naming-convention)
    - [ID Definition](#id-definition)
    - [ID Reference](#id-reference)
    - [Task Marker Semantics](#task-marker-semantics)
  - [Part II — Code Traceability](#part-ii--code-traceability)
    - [Code Traceability Overview](#code-traceability-overview)
    - [Scope Markers](#scope-markers)
    - [Block Markers](#block-markers)
    - [Language-Specific Syntax](#language-specific-syntax)
    - [Traceability Mode](#traceability-mode)
    - [Code Validation Rules](#code-validation-rules)
    - [Versioning](#versioning)
    - [Common Errors](#common-errors)
  - [References](#references)

---

## Quick Reference

**ID definition**:
```
- [ ] **ID**: `cpt-myapp-fr-must-authenticate`
- [x] `p1` - **ID**: `cpt-myapp-flow-login`
```

**ID reference**:
```
- `cpt-myapp-fr-must-authenticate`
- [x] `p1` - `cpt-myapp-flow-login`
```

**ID format**: `` `cpt-{hierarchy-prefix}-{kind}-{slug}` ``

**Code scope marker** (single-line):
```
@cpt-{kind}:{cpt-id}:p{N}
```

**Code block markers** (paired):
```
@cpt-begin:{cpt-id}:p{N}:inst-{local}
...code...
@cpt-end:{cpt-id}:p{N}:inst-{local}
```

**Validate**:
```bash
cypilot validate --artifact <path>    # artifact IDs
cypilot validate-code                 # code markers
```

---

## Part I — Identifiers

### ID Format

All Cypilot identifiers follow the pattern:

```
cpt-{hierarchy-prefix}-{kind}-{slug}
```

Where:
- `cpt-` — literal prefix (required)
- `{hierarchy-prefix}` — concatenated slugs from system → subsystem → component (e.g., `myapp-core-auth`)
- `{kind}` — element kind in lowercase (actor, cap, fr, nfr, comp, flow, algo, state, req, etc.)
- `{slug}` — descriptive slug (lowercase, alphanumeric, hyphens)

**Full regex**: `` `cpt-[a-z0-9][a-z0-9-]+` ``

### ID Naming Convention

IDs are built by concatenating **slugs** through the hierarchy chain (from `.cypilot/config/artifacts.toml`), followed by the element kind and a descriptive slug.

**Slug rules**: lowercase letters, numbers, hyphens only. No spaces, no leading/trailing hyphens. Pattern: `^[a-z0-9]+(-[a-z0-9]+)*$`

| Human Name | Slug |
|------------|------|
| "My Cool App" | `my-cool-app` |
| "User Authentication" | `user-auth` |
| "API Gateway v2" | `api-gateway-v2` |

**Hierarchy examples**:

| Level | Pattern | Example |
|-------|---------|---------|
| System | `cpt-{system}-{kind}-{slug}` | `cpt-saas-fr-user-auth` |
| Subsystem | `cpt-{system}-{subsystem}-{kind}-{slug}` | `cpt-saas-core-comp-api-gateway` |
| Component | `cpt-{system}-{subsystem}-{component}-{kind}-{slug}` | `cpt-saas-core-auth-flow-login` |

**Element kind examples**:
- `cpt-myapp-actor-admin-user` — Actor
- `cpt-myapp-fr-must-authenticate` — Functional requirement
- `cpt-myapp-core-comp-api-gateway` — Component
- `cpt-myapp-core-auth-flow-login` — Flow
- `cpt-myapp-core-auth-algo-password-hash` — Algorithm

### ID Definition

An ID definition declares a new identifier in an artifact:

```
**ID**: `cpt-myapp-fr-must-authenticate`
- [ ] **ID**: `cpt-myapp-actor-admin-user`
- [x] `p1` - **ID**: `cpt-myapp-core-comp-api-gateway`
`p2` - **ID**: `cpt-myapp-core-auth-flow-login`
```

**Pattern**:
```regex
^(?:\*\*ID\*\*:\s*`cpt-[a-z0-9][a-z0-9-]+`|`p\d+`\s*-\s*\*\*ID\*\*:\s*`cpt-[a-z0-9][a-z0-9-]+`|[-*]\s+\[\s*[xX]?\s*\]\s*(?:`p\d+`\s*-\s*)?\*\*ID\*\*:\s*`cpt-[a-z0-9][a-z0-9-]+`)\s*$
```

Components:
- `**ID**:` — literal prefix (required)
- `- [ ]` or `- [x]` — optional task checkbox
- `` `p1` `` – `` `p9` `` — optional priority marker
- `` `cpt-{hierarchy-prefix}-{kind}-{slug}` `` — the ID in backticks (required)

### ID Reference

A reference to an existing ID:

```
`cpt-myapp-fr-must-authenticate`
[ ] `cpt-myapp-core-comp-api-gateway`
[x] `p1` - `cpt-myapp-core-auth-flow-login`
```

**Standalone pattern**:
```regex
^(?:(?:\[\s*[xX]?\s*\])\s*(?:`p\d+`\s*-\s*)?)?`cpt-[a-z0-9][a-z0-9-]+`\s*$
```

**Inline pattern** (any backticked `cpt-*` in content):
```regex
`(cpt-[a-z0-9][a-z0-9-]+)`
```

### Task Marker Semantics

A task marker is the checkbox token on a definition/reference line (`[ ]` / `[x]`).

**Meaning on ID definition**:
- With task marker → ID is an **actionable task** tracked downstream via references
- Without task marker → ID is **non-task context**; references may be optional

**Scope**: task/coverage rules apply only for artifact kinds explicitly listed under `[identifiers.<kind>.ref.<TARGET>]` in `constraints.toml`. They MUST NOT create implicit requirements for unlisted artifact kinds.

**Coverage interaction**:
- `coverage` in constraints.toml is authoritative; task markers MUST NOT upgrade optional to required
- When `coverage = true` (required): references are mandatory per constraints
- If definition has task marker: at least one satisfying reference MUST also have a task marker

**Task synchronization**:
- A reference with task marker MUST refer to a definition that also has a task marker
- If both have task markers and the reference is done (`[x]`), the definition MUST also be done (`[x]`)
- If definition has task marker, any reference satisfying a required coverage rule MUST also have a task marker

---

## Part II — Code Traceability

### Code Traceability Overview

Code traceability links IDs defined in artifacts to implementation code through `@cpt-*` markers in comments. This enables:
- Automated verification that code references real, registered design IDs
- Coverage checks for IDs marked `to_code = true` in `constraints.toml`, optionally gated by task checkbox state
- Bidirectional navigation between artifacts and code (via ID search)

This specification is **kit-agnostic**:
- Defines the **generic marker format** and validation expectations
- The active kit (registered in `{cypilot_path}/config/core.toml`) defines which `{kind}` values are meaningful and which IDs require code traceability

### Scope Markers

Single-line markers for scope entry points (functions, classes, modules):

```
@cpt-{kind}:{cpt-id}:p{N}
```

- `{kind}` — kit-defined classification string (e.g., `flow`, `algo`, `comp`)
- `{cpt-id}` — full Cypilot ID from artifacts (e.g., `cpt-my-system-flow-login`)
- `p{N}` — phase number (required)

**Example**:
```python
# @cpt-flow:cpt-my-system-feature-core-auth-v2:p1
def login_flow(request):
    ...
```

### Block Markers

Paired markers wrapping specific CDSL instruction implementations:

```
@cpt-begin:{cpt-id}:p{N}:inst-{local}
...code...
@cpt-end:{cpt-id}:p{N}:inst-{local}
```

- `inst-{local}` — local instruction identifier (kit-defined)

**Granularity rule**: Each `@cpt-begin`/`@cpt-end` pair wraps **only the specific lines** that implement that one CDSL instruction — NOT the entire function. A function implementing multiple CDSL instructions contains multiple independent block marker pairs, each wrapping its own code fragment.

**Example** (single function, multiple instructions — each wrapped individually):
```python
# @cpt-flow:cpt-my-system-feature-core-auth-v2:p1
def validate_credentials(username, password):
    # @cpt-begin:cpt-my-system-feature-core-auth-v2:p1:inst-validate-input
    if not username or not password:
        raise ValidationError("Missing credentials")
    # @cpt-end:cpt-my-system-feature-core-auth-v2:p1:inst-validate-input

    # @cpt-begin:cpt-my-system-feature-core-auth-v2:p1:inst-authenticate
    result = authenticate(username, password)
    # @cpt-end:cpt-my-system-feature-core-auth-v2:p1:inst-authenticate

    # @cpt-begin:cpt-my-system-feature-core-auth-v2:p1:inst-return-token
    return generate_token(result.user_id)
    # @cpt-end:cpt-my-system-feature-core-auth-v2:p1:inst-return-token
```

**Anti-pattern** — do NOT wrap the entire function body with a single begin/end pair:
```python
# WRONG — wraps entire function, loses per-instruction traceability
# @cpt-begin:cpt-my-system-feature-core-auth-v2:p1:inst-validate-input
def validate_credentials(username, password):
    if not username or not password:
        raise ValidationError("Missing credentials")
    result = authenticate(username, password)
    return generate_token(result.user_id)
# @cpt-end:cpt-my-system-feature-core-auth-v2:p1:inst-validate-input
```

### Language-Specific Syntax

| Language | Single-line | Block start | Block end |
|----------|-------------|-------------|-----------|
| Python | `# @cpt-...` | `# @cpt-begin:...` | `# @cpt-end:...` |
| TypeScript/JS | `// @cpt-...` | `// @cpt-begin:...` | `// @cpt-end:...` |
| Go | `// @cpt-...` | `// @cpt-begin:...` | `// @cpt-end:...` |
| Rust | `// @cpt-...` | `// @cpt-begin:...` | `// @cpt-end:...` |
| Java | `// @cpt-...` | `// @cpt-begin:...` | `// @cpt-end:...` |

### Traceability Mode

Traceability mode is configured per artifact/codebase entry in `.cypilot/config/artifacts.toml`:

- **`FULL`**: markers are allowed and validated
  - Structural checks: pairing, no empty blocks, proper nesting
  - Cross-validation: code markers must reference IDs that exist in artifacts
  - Coverage for `to_code = true` IDs (from `constraints.toml`):
    - Definition has checked checkbox (`[x]`): code marker required
    - Definition has unchecked checkbox (`[ ]`): code marker prohibited
    - Definition has no checkbox: code marker required
- **`DOCS-ONLY`**: code markers are prohibited for the affected scope

### Code Validation Rules

**Placement**:
1. Scope markers at beginning of function/method/class (single-line, no begin/end)
2. Block markers wrap **only the specific lines** implementing one CDSL instruction — place them as close to the relevant code as possible
3. When a function implements multiple CDSL instructions, use **separate** begin/end pairs for each instruction inside the function body — do NOT wrap the entire function with one pair
4. Multiple markers allowed when code implements multiple IDs
5. External dependencies: place on integration point

**Pairing**:
1. Every `@cpt-begin` MUST have matching `@cpt-end`
2. Begin and end must have identical ID + inst string
3. Code MUST exist between begin/end (no empty blocks)
4. Nesting allowed but MUST be well-formed (no overlapping)

**IDs**:
1. Marker ID must exactly match design ID
2. All markers must include `:p{N}` phase postfix
3. No invented IDs — only IDs from design artifacts

**Validation command**:
```bash
cypilot validate-code
```

Validation performs:
- Deterministic structural checks (syntax, pairing, empty blocks, nesting)
- Cross-validation against artifacts (orphaned markers)
- Coverage checks driven by `to_code = true` IDs (gated by task checkbox state)

### Versioning

When design IDs are versioned:

| Design ID | Code Marker |
|-----------|-------------|
| `cpt-app-feature-auth-flow-login` | `@cpt-flow:cpt-app-feature-auth-flow-login:p1` |
| `cpt-app-feature-auth-flow-login-v2` | `@cpt-flow:cpt-app-feature-auth-flow-login-v2:p1` |

When design version increments, update all code markers. Old markers may be kept commented during transition.

### Common Errors

**Missing phase postfix**:
```python
# WRONG
# @cpt-flow:cpt-app-feature-auth-flow-login
def login(): ...

# CORRECT
# @cpt-flow:cpt-app-feature-auth-flow-login:p1
def login(): ...
```

**Mismatched begin/end IDs**:
```python
# WRONG — inst doesn't match
# @cpt-begin:cpt-app-feature-auth-flow-login:p1:inst-validate
def validate(): ...
# @cpt-end:cpt-app-feature-auth-flow-login:p1:inst-check

# CORRECT
# @cpt-begin:cpt-app-feature-auth-flow-login:p1:inst-validate
def validate(): ...
# @cpt-end:cpt-app-feature-auth-flow-login:p1:inst-validate
```

**Invented IDs**:
```python
# WRONG — ID doesn't exist in design
# @cpt-flow:cpt-app-feature-auth-flow-my-custom-thing:p1

# CORRECT — use only IDs from design document
# @cpt-flow:cpt-app-feature-auth-flow-login:p1
```

**Empty block**:
```python
# WRONG
# @cpt-begin:cpt-app-feature-auth-flow-login:p1:inst-validate
# @cpt-end:cpt-app-feature-auth-flow-login:p1:inst-validate

# CORRECT
# @cpt-begin:cpt-app-feature-auth-flow-login:p1:inst-validate
def validate_credentials(user, password):
    return authenticate(user, password)
# @cpt-end:cpt-app-feature-auth-flow-login:p1:inst-validate
```

---

## References

- **Kit specification**: `specs/kit/` — blueprint format, constraint definitions, validation semantics
- **CDSL**: `{cypilot_path}/.core/architecture/specs/CDSL.md` — behavioral specification language
- **Artifacts registry**: `.cypilot/config/artifacts.toml` — system, artifact, codebase definitions
- **CLI**: `{cypilot_path}/.core/architecture/specs/cli.md` — `validate`, `validate-code`, `list-ids`, `where-defined`, `where-used` commands
