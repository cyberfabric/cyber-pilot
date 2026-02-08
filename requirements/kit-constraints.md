---
cypilot: true
type: requirement
name: Kit Constraints
version: 1.0
purpose: Define kit-level constraints.json used for strict ID definition validation and cross-artifact reference rules
---

# Kit Constraints

## Overview

Kits MAY include a `constraints.json` file in the kit root (e.g. `kits/sdlc/constraints.json`).

This file defines additional constraints for artifact kinds in that kit, specifically for:

- ID definition blocks (`<!-- cpt:id:... -->`)
- ID reference blocks (`<!-- cpt:id-ref:... -->`)

Markers are **optional**.

Validation is markerless-first: IDs and references are recognized from the document text (e.g. ``**ID**: `cpt-...` `` and backticked ID occurrences) even if no `<!-- cpt:... -->` markers exist.

When markers are present in `template.md`, `constraints.json` still has higher priority and is the authoritative source of rules.

`constraints.json` constraints have **higher priority** than marker attributes in `template.md`.

If `constraints.json` contradicts an explicit marker attribute, validation MUST fail.

## File Location

- `kits/<kit-name>/constraints.json`

The tool discovers this file by resolving each kit’s registry path (`kits[*].path` in `artifacts.json`) and checking for `constraints.json` in that directory.

## Schema

`constraints.json` is a JSON object mapping **artifact kinds** (e.g. `PRD`, `DESIGN`, `SPEC`) to a constraints object.

Each artifact kind constraints object MUST include:

- `identifiers`: object mapping ID kind -> constraint entry

Each artifact kind constraints object MAY include:

- `name`: string
- `description`: string

### JSON Schema

The constraints file MAY include a JSON Schema reference for editor validation:

```json
{
  "$schema": "../../schemas/kit-constraints.schema.json"
}
```

Keys starting with `$` (like `$schema`) are ignored by the parser.

### ID Constraint Entry

Each element of `identifiers` is an object (map key is the ID kind):

- `kind` (optional): string
  - If provided, it MUST match the `identifiers` key
  - The effective kind is the `identifiers` key
- `name` (optional): string
- `description` (optional): string
- `examples` (optional): list
- `references` (optional): object mapping artifact kinds to reference rules
- `required` (optional): boolean
- `task` (optional): string
- `priority` (optional): string
- `to_code` (optional): boolean
- `headings` (optional): list[string]

### Reference Rule Entry

Each element of `references` is an object:

- `coverage` (required): string enum `required|optional|prohibited`
- `task` (optional): string enum `required|allowed|prohibited` (legacy booleans accepted)
- `priority` (optional): string enum `required|allowed|prohibited` (legacy booleans accepted)
- `headings` (optional): list[string]

### Example

```json
{
  "PRD": {
    "name": "PRD constraints",
    "description": "How PRD IDs must be represented",
    "identifiers": {
      "fr": {
        "name": "Functional Requirement",
        "description": "A functional requirement ID",
        "examples": ["cpt-bookcatalog-fr-search"],
        "required": true,
        "task": "required",
        "priority": "required",
        "to_code": true,
        "references": {
          "DESIGN": {
            "coverage": "required",
            "task": "allowed",
            "priority": "allowed",
            "headings": ["Upstream", "Traceability"]
          },
          "DECOMPOSITION": {"coverage": "optional"},
          "SPEC": {"coverage": "optional"},
          "ADR": {"coverage": "prohibited"}
        },
        "headings": ["Functional Requirements"]
      },
      "nfr": {
        "name": "Non-functional Requirement",
        "description": "An NFR ID",
        "examples": ["cpt-bookcatalog-nfr-latency"],
        "priority": "required",
        "task": "allowed",
        "references": {
          "DESIGN": {"coverage": "required"},
          "SPEC": {"coverage": "optional"}
        }
      },
      "actor": {
        "name": "Actor",
        "description": "An actor ID",
        "examples": ["cpt-bookcatalog-actor-admin"],
        "required": false,
        "task": "prohibited",
        "priority": "prohibited",
        "headings": ["Actors"]
      },
      "usecase": {
        "name": "Use Case",
        "description": "A use case ID",
        "examples": ["cpt-bookcatalog-usecase-search"],
        "task": true,
        "priority": false,
        "references": {
          "DECOMPOSITION": {"coverage": "optional", "task": "required", "priority": "required"}
        }
      }
    }
  }
}
```

## Semantics

### Priority

`constraints.json` overrides marker attributes in `template.md` for ID definition blocks.

- **`required`** controls whether an ID kind must be defined at least once in the artifact.
  - If omitted, it defaults to `true`.
  - If `required: true` and there are no ID definitions of that kind, validation FAILS.
  - If `required: false`, the kind is optional.

- **`priority` / `task`** are applied via the `has="..."` marker attribute.
  - Supported values: `required`, `allowed`, `prohibited`
  - Legacy booleans are accepted for backward compatibility:
    - `true` => `required`
    - `false` => `prohibited`
  - `required` means `has` MUST contain the token
  - `prohibited` means `has` MUST NOT contain the token
  - `allowed` means priority/task is permitted (it MAY be present or absent). The validator does not enforce presence/absence.
- **`references`** declares where references MUST/MAY/MUST NOT appear.
  - `coverage: "required"` implies the ID must be referenced from that artifact kind.
  - `coverage: "optional"` means reference may exist but is not required.
  - `coverage: "prohibited"` means reference must not exist from that artifact kind.
  - Only explicitly declared `references` target kinds participate in validation. The validator MUST NOT require coverage from artifact kinds that are not listed under `references`.

- **`to_code`** is applied via the `to_code="true|false"` marker attribute.
- **`headings`** is stored as a JSON-encoded string attribute `headings="[...]"` for downstream tooling.

### Contradictions

If a template marker explicitly specifies an attribute and `constraints.json` specifies a different value, validation MUST fail.

Contradictions include:

- Marker has `has="priority"` but constraint sets `priority: "prohibited"`
- Marker has `to_code="false"` but constraint sets `to_code: true`

Notes:

- Template-load-time contradiction checking is applied only for `identifiers` constraints against `cpt:id:<kind>` blocks.
- `references` rules are enforced during cross-artifact validation.

### Missing Template Blocks

If `constraints.json` references an ID kind that does not exist in the template as a corresponding block, validation MUST fail.

## Validation Integration

The tool loads and applies constraints when loading templates for kits.

Constraint errors are surfaced during:

- `validate` (artifact validation)
- `validate-kits` (template validation)

## Strict Artifact Semantics

When `constraints.json` defines constraints for an artifact kind (e.g. `PRD`), the validator applies **strict semantics** to artifacts of that kind.

Strict semantics are applied during template-based validation (`Template.validate`) and operate on marker-defined `cpt:id:<kind>` blocks.

### Allowed ID Kinds

For a constrained artifact kind:

- For **ID definitions** (`identifiers`): the artifact MUST NOT contain any `<!-- cpt:id:<kind> -->` blocks where `<kind>` is not listed in `identifiers`.
- For **ID references**: reference expectations are defined by `identifiers[<kind>].references`.

If such a block exists and yields a parsed ID definition/reference, validation FAILS with a `constraints` error.

### Required Presence

For a constrained artifact kind:

- Every identifier kind listed in `identifiers` MUST appear **at least once** as an ID definition in the artifact (unless `required: false`).

The `required` flag controls this behavior:

- If omitted, it defaults to `true`.
- If `required: true` and the kind is missing, validation FAILS.
- If `required: false`, missing definitions of that kind are allowed.

References are validated via `identifiers[<kind>].references` rules (coverage required|optional|prohibited).

If a constrained kind is missing, validation FAILS.

### Heading Scoping (`headings`)

If a constraint entry specifies `headings`, then the corresponding IDs MUST be scoped under those headings in the artifact.

Rules:

- Every ID definition of that `kind` MUST be located under at least one of the listed headings.
- It is a validation error if an ID of that kind appears under a different heading (i.e. not within the heading scope).
- It is a validation error if the artifact contains at least one such ID-kind, but **none** of its occurrences are under the required headings.

Heading matching is performed by comparing heading titles (the text after `#`, `##`, ...). Headings are detected outside fenced code blocks.

Notes:

- Strict template validation normalizes headings (case-insensitive, trims whitespace, ignores `:`).
- Markerless cross-artifact validation compares headings using simple string equality after `strip()`.

## Cross-Artifact Validation (Markerless-First)

Cross-artifact validation:

- Ignores template markers and performs markerless scans of artifacts.
- Builds an index of ID definitions and references across artifacts.
- Enforces `identifiers[<kind>].references` rules (`coverage: required|optional|prohibited`).

Notes:

- Cross-artifact coverage requirements are derived ONLY from `identifiers[<kind>].references[<target_kind>]` with `coverage: required`.
- There is no additional implicit rule like "an ID must be referenced from any other artifact kind" when constraints exist for the artifact kind being validated.

Cross-artifact validation is markerless-first and may detect IDs/references even when artifacts do not contain any `<!-- cpt:... -->` markers.

### System Scoping

IDs are interpreted as internal only when the system prefix matches a registered system prefix.

- Registered system prefixes are derived from the system tree in `artifacts.json` using each node’s slug hierarchy prefix (e.g. `overwork-alert`, `saas-platform-core-auth`).
- System matching is longest-prefix-wins.

### Reference Coverage Rules (`references`)

For each ID definition `d` of identifier kind `K` in artifact kind `A`, and each rule `identifiers[K].references[T]`:

- `coverage: required`
  - If `T` is not present for the system (no artifacts of that kind exist), the validator emits a warning: `Required reference target kind not in scope`.
  - Otherwise, if there are no references to that ID from artifact kind `T`, validation FAILS.
- `coverage: optional`
  - No requirement.
- `coverage: prohibited`
  - If any reference exists from artifact kind `T`, validation FAILS.

### Reference Task/Priority Rules

Reference rules MAY additionally require or prohibit task/priority markers on references:

- `task: required|allowed|prohibited`
- `priority: required|allowed|prohibited`

The validator derives reference flags from the reference text:

- `has_task`: a checkbox is present (e.g. `[ ]` / `[x]`)
- `has_priority`: a priority token is present (e.g. `` `p1` ``)

Notes:

- Reference `task/priority` rules are enforced only when a reference exists.
- Template marker attributes like `<!-- cpt:id-ref:<kind> has="..." -->` are not used for tri-state enforcement; enforcement is based on the reference line text.

### Checkbox Synchronization (Done Status)

Cross-artifact validation also enforces:

- If a reference is marked done (`[x]`) and both the reference and the definition explicitly track task status (`has_task == true`), then the definition MUST be marked done.

## References

- `requirements/template.md` (marker-based template system)
- `requirements/traceability.md` (to_code and traceability concepts)
