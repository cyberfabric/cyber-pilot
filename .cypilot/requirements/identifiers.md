---
cypilot: true
type: requirement
name: Cypilot Identifiers Specification
version: 1.3
purpose: Define artifact ID formats and naming conventions used by Cypilot validation
---

# Cypilot Identifiers Specification

## Table of Contents

- [Cypilot Identifiers Specification](#cypilot-identifiers-specification)
  - [Table of Contents](#table-of-contents)
  - [Quick Reference](#quick-reference)
  - [Prerequisite Checklist](#prerequisite-checklist)
  - [Overview](#overview)
  - [ID Formats](#id-formats)
    - [ID Definition](#id-definition)
    - [ID Reference](#id-reference)
    - [Inline ID Reference](#inline-id-reference)
    - [ID Naming Convention](#id-naming-convention)
  - [Task Marker Semantics](#task-marker-semantics)
    - [Meaning of a task marker on an ID definition](#meaning-of-a-task-marker-on-an-id-definition)
    - [Scope: constraints.json and references coverage](#scope-constraintsjson-and-references-coverage)
    - [Task markers and references coverage](#task-markers-and-references-coverage)
    - [Task synchronization between definitions and references](#task-synchronization-between-definitions-and-references)
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

**ID format**: `` `cpt-{hierarchy-prefix}-{kind}-{slug}` `` (see [ID Naming Convention](#id-naming-convention))

**Validate template**:
```bash
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py validate --artifact <path>
```

---

## Prerequisite Checklist

- [ ] Agent has identified the artifact being validated
- [ ] Agent understands ID definition and reference formats
- [ ] Agent has access to the template file for the artifact kind

---

## Overview

Cypilot validation relies on scanning artifacts for:

- ID definitions (e.g. ``**ID**: `cpt-...` ``)
- ID references (backticked `cpt-...` occurrences)
- CDSL instructions (see `requirements/CDSL.md`)

**Supported Version**: `1.0`

---

## ID Formats

### ID Definition

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
- `- [ ]` or `- [x]` — optional task checkbox (task list item)
- `` `p1` `` - `` `p9` `` — optional priority
- `` `cpt-{hierarchy-prefix}-{kind}-{slug}` `` — the ID in backticks (required)

### ID Reference

```
`cpt-myapp-fr-must-authenticate`
[ ] `cpt-myapp-core-comp-api-gateway`
[x] `p1` - `cpt-myapp-core-auth-flow-login`
```

**Pattern**:

```regex
^(?:(?:\[\s*[xX]?\s*\])\s*(?:`p\d+`\s*-\s*)?)?`cpt-[a-z0-9][a-z0-9-]+`\s*$
```

### Inline ID Reference

Any `` `cpt-xxx` `` in content is treated as a reference.

**Pattern**:

```regex
`(cpt-[a-z0-9][a-z0-9-]+)`
```

### ID Naming Convention

IDs are built by concatenating **slugs** through the hierarchy chain (from `artifacts.json`), followed by the element kind and a descriptive slug.

```
cpt-{hierarchy-prefix}-{kind}-{slug}
```

Where:
- `cpt-` — literal prefix (required)
- `{hierarchy-prefix}` — concatenated slugs from system → subsystem → component (e.g., `myapp-core-auth`)
- `{kind}` — element kind in lowercase (actor, cap, fr, nfr, comp, flow, algo, state, req, etc.)
- `{slug}` — descriptive slug (lowercase, alphanumeric, hyphens)

**What is a slug?**

A **slug** is a machine-readable identifier derived from a human name. Slugs are URL-safe, lowercase strings used for stable references.

| Human Name | Slug |
|------------|------|
| "My Cool App" | `my-cool-app` |
| "User Authentication" | `user-auth` |
| "API Gateway v2" | `api-gateway-v2` |

**Slug rules**: lowercase letters, numbers, hyphens only. No spaces, no leading/trailing hyphens. Pattern: `^[a-z0-9]+(-[a-z0-9]+)*$`

**Hierarchy Examples** (from `artifacts.json`):

| Hierarchy Level | ID Pattern | Example |
|-----------------|------------|---------|
| System | `cpt-{system}-{kind}-{slug}` | `cpt-saas-fr-user-auth` |
| Subsystem | `cpt-{system}-{subsystem}-{kind}-{slug}` | `cpt-saas-core-comp-api-gateway` |
| Component | `cpt-{system}-{subsystem}-{component}-{kind}-{slug}` | `cpt-saas-core-auth-flow-login` |

**Element Kind Examples**:
- `cpt-myapp-actor-admin-user` — Actor at system level
- `cpt-myapp-cap-user-management` — Capability at system level
- `cpt-myapp-fr-must-authenticate` — Functional requirement
- `cpt-myapp-core-comp-api-gateway` — Component at subsystem level
- `cpt-myapp-core-auth-flow-login` — Flow at component level
- `cpt-myapp-core-auth-algo-password-hash` — Algorithm at component level

---

## Task Marker Semantics

A task marker is the checkbox token on a definition/reference line (`[ ]` / `[x]`).

### Meaning of a task marker on an ID definition

If an ID definition includes a task marker, it declares that the ID is an **actionable task** that MUST be tracked downstream via references when references are required by kit constraints.

If an ID definition does not include a task marker, it declares that the ID is **non-task context**, and downstream references MAY be optional (see rules below).

### Scope: constraints.json and references coverage

This rule is only applied for target artifact kinds explicitly listed under:

- `kits/<kit>/constraints.json` → `<SOURCE_KIND>.identifiers[<ID_KIND>].references`

This rule MUST NOT create implicit requirements for artifact kinds that are not present in that `references` map.

### Task markers and references coverage

`coverage` in kit constraints is authoritative. Task markers MUST NOT upgrade `coverage: "optional"` to `required`.

- When `coverage: "required"`, references are mandatory as specified by constraints.
- If an ID definition includes a task marker, at least one reference used to satisfy a `coverage: "required"` rule MUST also include a task marker.

### Task synchronization between definitions and references

Task markers between an ID definition and its references MUST be synchronized:

- A reference that includes a task marker MUST refer to an ID definition that also includes a task marker.
- If both the reference and the definition include task markers and the reference is marked done (`[x]`), the definition MUST be marked done (`[x]`).
- If an ID definition includes a task marker, any reference used to satisfy a required coverage rule MUST also include a task marker.

---

## References

- **Schema**: `schemas/cypilot-template-frontmatter.schema.json`
- **Validation behavior**: `requirements/kit-constraints.md`
- **Code traceability**: `requirements/traceability.md`
