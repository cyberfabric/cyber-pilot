---
cypilot: true
type: spec
name: Checklist Specification
version: 1.0
purpose: Define the format, structure, and usage of checklist.md kit files
drivers:
  - cpt-cypilot-fr-core-kits
---

# Checklist Specification (checklist.md)


<!-- toc -->

- [Overview](#overview)
- [Location](#location)
- [File Structure](#file-structure)
- [File Format](#file-format)
- [Domain Sections](#domain-sections)
- [Check Items](#check-items)
- [Applicability Conditions](#applicability-conditions)
- [Example](#example)
- [Usage](#usage)
- [Error Handling](#error-handling)

<!-- /toc -->

---
---

## Overview

`checklist.md` is a kit file that provides a structured quality checklist for an artifact kind. It is authored by kit authors and user-editable after installation, organized by expertise domain and check kind (MUST HAVE / MUST NOT HAVE).

**Key properties**:
- Kit file — user-editable, preserved across kit updates via file-level diff
- Organized by expertise domain (e.g., Business, Architecture, Security, Testing)
- Each domain has MUST HAVE and MUST NOT HAVE sections
- Severity levels: CRITICAL, HIGH, MEDIUM, LOW
- Used by analyze workflows for semantic quality review

---

## Location

**Per-artifact**: `{cypilot_path}/config/kits/<slug>/artifacts/<KIND>/checklist.md`

**Codebase**: `{cypilot_path}/config/kits/<slug>/codebase/checklist.md`

---

## File Structure

> **Legacy note**: In the previous blueprint-based model, `checklist.md` was generated from `@cpt:checklist` and `@cpt:check` markers. In the current model, `checklist.md` is authored directly by kit authors. See [blueprint.md](blueprint.md) (DEPRECATED) for legacy marker reference.

`checklist.md` follows the domain-organized structure defined below. Kit authors maintain this file directly.

---

## File Format

```markdown
# PRD Quality Checklist

**Artifact**: PRD
**Kit**: sdlc

**Severity levels**: CRITICAL > HIGH > MEDIUM > LOW
**Review priority**: BIZ → ARCH → SEC → TEST

---

## BIZ — Business

**Standards**: ISO/IEC/IEEE 29148:2018 §6.2 (StRS), §6.4 (SRS)

### MUST HAVE

#### BIZ-PRD-001 — Vision Clarity [CRITICAL]

- [ ] Purpose statement explains WHY the product exists
- [ ] Target users clearly identified with specificity (not just "users")
- [ ] Key problems solved are concrete and measurable

> **Ref**: ISO/IEC/IEEE 29148 §5.2.5

#### BIZ-PRD-002 — Scope Boundaries [HIGH]

- [ ] In-scope items explicitly listed
- [ ] Out-of-scope items explicitly listed

### MUST NOT HAVE

#### BIZ-PRD-NO-001 — No Implementation Details [CRITICAL]

- [ ] No database schema definitions
- [ ] No API endpoint specifications

> **Belongs to**: DESIGN

---

## ARCH — Architecture

...
```

---

## Domain Sections

Each domain section contains:

1. **Domain header**: `## {ABBR} — {Name}`
2. **Standards line**: referenced standards from `[[domain]].standards`
3. **Applicability table** (if any checks have conditions):
   ```markdown
   | Check | Applicable When | Not Applicable When |
   |-------|----------------|-------------------|
   | BIZ-PRD-003 | Multiple user roles | Single-user system |
   ```
4. **MUST HAVE** subsection: checks with `kind = "must_have"`
5. **MUST NOT HAVE** subsection: checks with `kind = "must_not_have"`

---

## Check Items

Each check item is rendered as:

```markdown
#### {ID} — {Title} [{SEVERITY}]

{task-list content from ```markdown block}

> **Ref**: {ref}                    # if ref is set
> **Belongs to**: {belongs_to}      # if belongs_to is set (must_not_have items)
```

Checks within each kind section are sorted by severity (CRITICAL → HIGH → MEDIUM → LOW), then by definition order within the same severity.

---

## Applicability Conditions

Checks may have conditional applicability:

| TOML Key | Effect |
|----------|--------|
| `applicable_when` | Check applies only when the condition is true |
| `not_applicable_when` | Check does not apply when the condition is true |
| Both omitted | Check always applies |

Conditions are rendered in the applicability table at the top of the domain section.

---

## Example

Example checklist structure using TOML notation:

```toml
# @cpt:checklist
[severity]
levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
[review]
priority = ["BIZ", "ARCH"]
[[domain]]
abbr = "BIZ"
name = "Business"
standards = ["ISO/IEC/IEEE 29148:2018"]
```

```toml
# @cpt:check
id = "BIZ-PRD-001"
domain = "BIZ"
title = "Vision Clarity"
severity = "CRITICAL"
kind = "must_have"
```

Resulting checklist.md structure:

```markdown
## BIZ — Business

**Standards**: ISO/IEC/IEEE 29148:2018

### MUST HAVE

#### BIZ-PRD-001 — Vision Clarity [CRITICAL]

- [ ] Purpose statement explains WHY the product exists
...
```

---

## Usage

- **Analyze workflows**: load `checklist.md` as semantic quality criteria for artifact review
- **Generate workflows**: reference `checklist.md` to ensure generated content meets quality standards
- **Agent context**: agents use domain-organized checklists to systematically validate artifact quality

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `CHECKLIST_NO_DOMAINS` | `@cpt:checklist` has no `[[domain]]` entries | Add at least one domain definition |
| `CHECKLIST_UNKNOWN_DOMAIN` | `@cpt:check.domain` doesn't match any `[[domain]].abbr` | Fix domain abbreviation or add domain to `@cpt:checklist` |
| `CHECKLIST_UNKNOWN_SEVERITY` | `@cpt:check.severity` not in `[severity].levels` | Use a defined severity level |
| `CHECKLIST_DUPLICATE_ID` | Two `@cpt:check` blocks with same `id` | Use unique check IDs |
