---
cypilot: true
type: requirement
name: Kit Constraints
version: 1.0
purpose: Define kit-level constraints.json that overrides template marker attributes for ID definitions/references
---

# Kit Constraints

## Overview

Kits MAY include a `constraints.json` file in the kit root (e.g. `kits/sdlc/constraints.json`).

This file defines additional constraints for artifact kinds in that kit, specifically for:

- ID definition blocks (`<!-- cpt:id:... -->`)
- ID reference blocks (`<!-- cpt:id-ref:... -->`)

`constraints.json` constraints have **higher priority** than marker attributes in `template.md`.

If `constraints.json` contradicts an explicit marker attribute, validation MUST fail.

## File Location

- `kits/<kit-name>/constraints.json`

The tool discovers this file by resolving each kit’s registry path (`kits[*].path` in `artifacts.json`) and checking for `constraints.json` in that directory.

## Schema

`constraints.json` is a JSON object mapping **artifact kinds** (e.g. `PRD`, `DESIGN`, `SPEC`) to a constraints object.

Each artifact kind constraints object MUST include:

- `defined-id`: list of ID definition block constraints
- `name`: string
- `description`: string

### JSON Schema

The constraints file MAY include a JSON Schema reference for editor validation:

```json
{
  "$schema": "../../schemas/kit-constraints.schema.json"
}
```

### ID Constraint Entry

Each element of `defined-id` is an object:

- `kind` (required): string
  - For `defined-id`, this must match a template block with `type == "id"` and `name == kind`
- `name` (optional): string
- `description` (optional): string
- `examples` (optional): list
- `references` (optional): object mapping artifact kinds to reference rules
- `task` (optional): boolean
- `priority` (optional): boolean
- `to_code` (optional): boolean
- `headings` (optional): list[string]

### Example

```json
{
  "PRD": {
    "name": "PRD constraints",
    "description": "How PRD IDs must be represented",
    "defined-id": [
      {
        "kind": "fr",
        "name": "Functional Requirement",
        "description": "A functional requirement ID",
        "examples": ["cpt-bookcatalog-fr-search"],
        "task": true,
        "priority": true,
        "to_code": true,
        "references": {
          "DESIGN": {"coverage": "required"},
          "SPEC": {"coverage": "required"}
        },
        "headings": ["Functional Requirements"]
      }
    ]
  }
}
```

## Semantics

### Priority

`constraints.json` overrides marker attributes in `template.md`.

- **`priority` / `task`** are applied via the `has="..."` marker attribute.
  - `priority: true` means `has` contains `priority`
  - `priority: false` means `has` does not contain `priority`
  - `task: true` means `has` contains `task`
  - `task: false` means `has` does not contain `task`
- **`references`** declares where references MUST/MAY/MUST NOT appear.
  - `coverage: "required"` implies the ID must be referenced from that artifact kind.
  - `coverage: "optional"` means reference may exist but is not required.
  - `coverage: "prohibited"` means reference must not exist from that artifact kind.

- **`to_code`** is applied via the `to_code="true|false"` marker attribute.
- **`headings`** is stored as a JSON-encoded string attribute `headings="[...]"` for downstream tooling.

### Contradictions

If a template marker explicitly specifies an attribute and `constraints.json` specifies a different value, validation MUST fail.

Contradictions include:

- Marker has `has="priority"` but constraint sets `priority: false`
- Marker has `to_code="false"` but constraint sets `to_code: true`
- Marker explicitly encodes a different requirement than `references` implies (e.g. conflicting required reference targets)

### Missing Template Blocks

If `constraints.json` references an ID kind that does not exist in the template as a corresponding block, validation MUST fail.

## Validation Integration

The tool loads and applies constraints when loading templates for kits.

Constraint errors are surfaced during:

- `validate` (artifact validation)
- `validate-kits` (template validation)

## Strict Artifact Semantics

When `constraints.json` defines constraints for an artifact kind (e.g. `PRD`), the validator applies **strict semantics** to artifacts of that kind.

### Allowed ID Kinds

For a constrained artifact kind:

- For **ID definitions** (`defined-id`): the artifact MUST NOT contain any `<!-- cpt:id:<kind> -->` blocks where `<kind>` is not listed in `defined-id`.
- For **ID references**: reference expectations are defined by `defined-id[].references`.

If such a block exists and yields a parsed ID definition/reference, validation FAILS with a `constraints` error.

### Required Presence

For a constrained artifact kind:

- Every `defined-id[].kind` MUST appear **at least once** as an ID definition in the artifact.

References are validated via `defined-id[].references` rules (coverage required|optional|prohibited).

If a constrained kind is missing, validation FAILS.

### Heading Scoping (`headings`)

If a constraint entry specifies `headings`, then the corresponding IDs MUST be scoped under those headings in the artifact.

Rules:

- Every ID definition/reference of that `kind` MUST be located under at least one of the listed headings.
- It is a validation error if an ID of that kind appears under a different heading (i.e. not within the heading scope).
- It is a validation error if the artifact contains at least one such ID-kind, but **none** of its occurrences are under the required headings.

Heading matching is performed by comparing heading titles (the text after `#`, `##`, ...). Headings are detected outside fenced code blocks.

## References

- `requirements/template.md` (marker-based template system)
- `requirements/traceability.md` (to_code and traceability concepts)
