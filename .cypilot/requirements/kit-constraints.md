---
cypilot: true
type: requirement
name: Kit Constraints
version: 1.1
purpose: Define kit-level constraints.json used for strict ID definition validation and cross-artifact reference rules
---

# Kit Constraints

## Overview

Kits MAY include a `constraints.json` file in the kit root (e.g. `kits/sdlc/constraints.json`).

This file defines additional constraints for artifact kinds in that kit, specifically for:

- ID definition and reference validation (text-based)
- Cross-artifact reference rules
- Document outline validation via `headings`

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
- `headings`: list[Heading Constraint Entry]

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
- `template` (optional): string
  - A human-readable ID template hint to guide authors (used in validation errors)
  - Example: `cpt-{system}-flow-{feature slug}-{slug}`
- `examples` (optional): list
- `references` (optional): object mapping artifact kinds to reference rules
- `required` (optional): boolean
- `task` (optional): string
- `priority` (optional): string
- `to_code` (optional): boolean

### Heading Constraint Entry

Each element of `headings` is an object:

- `id` (optional): string
  - Stable identifier for this heading constraint entry
  - Used by the validator to reference constraints precisely in errors
- `pattern` (optional): string (regexp)
  - Applied to the **heading title text** (excluding the leading `#` markers and excluding optional numbering prefix)
  - MUST NOT include `#` markers (they are controlled by `level`)
- `description` (optional): string
  - Human-readable description of the section intent
  - Used in validation errors to make scoping and outline errors more actionable
- `level` (required): integer 1-6
- `required` (optional): boolean (default `true`)
- `multiple` (optional): string enum `allow|prohibited|required`
  - Controls whether the same heading constraint may match multiple headings
- `numbered` (optional): string enum `allow|prohibited|required`
  - Controls whether the heading must be numbered

Note: Heading constraint entries do not scope ID kinds directly. Scoping is done via
`identifiers[<kind>].headings` (for definitions) and `identifiers[<kind>].references[<target>].headings`
(for references), which refer to *heading constraint ids*.

### Reference Rule Entry

Each element of `references` is an object:

- `coverage` (required): string enum `required|optional|prohibited`
  - Controls whether references to this ID kind must exist in the target artifact kind.
- `task` (optional): string enum `allowed|required|prohibited` (default: `allowed`)
- `priority` (optional): string enum `allowed|required|prohibited` (default: `allowed`)
- `headings` (optional): list[string]
  - Heading constraint ids that define the **required locations** for references.
  - Semantics:
    - If `coverage` is `required` and `headings` is non-empty, then **at least one** reference in the target artifact kind must appear under one of these heading constraint ids.
    - Otherwise, references are allowed anywhere in the target artifact kind (unless `coverage` is `prohibited`).

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
            "priority": "allowed"
          },
          "DECOMPOSITION": {"coverage": "optional"},
          "FEATURE": {"coverage": "optional"},
          "ADR": {"coverage": "prohibited"}
        }
      },
      "nfr": {
        "name": "Non-functional Requirement",
        "description": "An NFR ID",
        "examples": ["cpt-bookcatalog-nfr-latency"],
        "priority": "required",
        "task": "allowed",
        "references": {
          "DESIGN": {"coverage": "required"},
          "FEATURE": {"coverage": "optional"}
        }
      },
      "actor": {
        "name": "Actor",
        "description": "An actor ID",
        "examples": ["cpt-bookcatalog-actor-admin"],
        "required": false,
        "task": "prohibited",
        "priority": "prohibited"
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
    },
    "headings": [
      {
        "level": 2,
        "pattern": "Functional Requirements",
        "required": true,
        "multiple": "prohibited",
        "numbered": "allow",
        "identifiers": ["fr"]
      },
      {
        "level": 2,
        "pattern": "Non-functional Requirements",
        "required": true,
        "multiple": "prohibited",
        "numbered": "allow",
        "identifiers": ["nfr"]
      },
      {
        "level": 2,
        "pattern": "Actors",
        "required": false,
        "multiple": "prohibited",
        "numbered": "allow",
        "identifiers": ["actor"]
      }
    ]
  }
}
```

## Semantics

### Priority

`constraints.json` defines validation rules for ID definitions and references discovered in artifact text.

- **`required`** controls whether an ID kind must be defined at least once in the artifact.
  - If omitted, it defaults to `true`.
  - If `required: true` and there are no ID definitions of that kind, validation FAILS.
  - If `required: false`, the kind is optional.

- **`priority` / `task`** apply to the definition/reference line formats.
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

- **`to_code`** indicates that the ID is expected to be traceable to code (see `requirements/traceability.md`).
  - If the ID definition has a task checkbox, required code coverage is enabled only when the checkbox is checked (`[x]`).
  - If the ID definition has a task checkbox and it is not checked (`[ ]`), referencing the ID from code is an error.
  - If the ID definition has no task checkbox, `to_code: true` requires at least one code marker.

### Heading Constraints (`headings`)

`headings` defines a **document outline contract** for artifacts of a given kind.

The validator walks the artifact’s markdown headings and checks that:

- Heading occurrences required by constraints exist
- Constrained headings are **not mixed**: their relative order MUST match the order of entries in `headings`
- Constrained heading repetition complies with `multiple`
- Numbering (if required/prohibited) and numbering progression are correct
- If `identifiers` is specified on a heading constraint entry, IDs of those kinds MUST be scoped to that heading’s section and those kinds become reserved (see below)

#### Matching rules

For each markdown heading line:

- The heading `level` is derived from the number of leading `#` characters.
- The heading `raw title` is the remainder after the `#` and a single required space.
- If the heading is numbered, the numbering prefix is parsed as `^<num>(\.<num>)*\s+` (e.g. `1 `, `1.2 `, `2.10.3 `).
- The heading `title text` used for `pattern` matching is the `raw title` with the numbering prefix removed (if present).

A heading constraint entry matches a document heading when:

- `level` equals the document heading level
- If `pattern` is present, it matches the `title text`

#### Ordering and nesting rules

The outline contract is validated as follows:

- The tool iterates `headings` constraint entries in order and attempts to match them against the document outline.
- When a constrained heading `H_i` is found, the next constrained heading found in the document at `level <= H_i.level` MUST be the next entry in the constraints list.
- Between `H_i` and the next constrained heading `H_{i+1}`:
  - Headings of **deeper level** (`level > H_i.level`) are allowed in free form **unless** they are constrained elsewhere in `headings`.
  - Headings of the same or higher level (`level <= H_i.level`) that are not `H_{i+1}` are considered a mixing error.

This means:

- If you constrain `##` headings only, any `###` headings inside a constrained section are allowed freely.
- If you also constrain some `###` headings, then inside a constrained `##` section the constrained `###` headings MUST appear in the declared order.

#### Presence and repetition

- `required` defaults to `true`.
- `multiple` defaults to `allow`.
- If `multiple: prohibited`, the constraint entry may match at most one heading.
- If `multiple: required`, the constraint entry MUST match at least two headings.

#### Numbering rules

- `numbered` defaults to `allow`.
- If `numbered: required`, each matching heading MUST have a numbering prefix.
- If `numbered: prohibited`, each matching heading MUST NOT have a numbering prefix.

Numbering progression is validated per heading level and nesting:

- For a numbered heading at level `L`, the numbering prefix MUST be unique among headings at the same `L` within the same parent numbering scope.
- If two consecutive numbered headings at the same level `L` share the same parent prefix, the last segment MUST be `+1`.
- Nested numbering MUST be consistent with parents:
  - If a parent numbered heading is `2` (at level 2), then numbered children at level 3 MUST start with `2.<n>`.
  - If a parent numbered heading is `2.3` (at level 3), then numbered children at level 4 MUST start with `2.3.<n>`.

#### Heading id scoping (definitions and references)

If an ID constraint entry specifies `headings`:

- For definitions (`identifiers[<kind>].headings`): each ID definition of that kind MUST appear within a section whose active heading constraint id is in the list.
- For references (`identifiers[<kind>].references[<target>].headings`): each reference MUST appear within a section whose active heading constraint id is in the list.

`headings` values are compared against the heading constraint `id` values from the artifact kind’s `headings` contract.

## Cross-Artifact Validation

Cross-artifact validation:

- Performs scans of artifacts.
- Builds an index of ID definitions and references across artifacts.
- Enforces `identifiers[<kind>].references` rules (`coverage: required|optional|prohibited`).

Notes:

- Cross-artifact coverage requirements are derived ONLY from `identifiers[<kind>].references[<target_kind>]` with `coverage: required`.
- There is no additional implicit rule like "an ID must be referenced from any other artifact kind" when constraints exist for the artifact kind being validated.

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

### Checkbox Synchronization (Done Status)

Cross-artifact validation also enforces:

- If a reference is marked done (`[x]`) and both the reference and the definition explicitly track task status (`has_task == true`), then the definition MUST be marked done.

## Artifact Scanning and Validation

Cypilot extracts **IDs**, **ID references**, and **CDSL instructions** from artifacts using best-effort scanning.

Scanning is the authoritative method for artifact signal extraction.

### Non-Goals

Scanning is explicitly **not** intended to provide deterministic structural compliance.

- Scanning does **not** guarantee structural compliance.
- Scanning does **not** provide precise block boundaries for validation errors.

### Supported Signal Extraction

#### ID Definitions

Scanning recognizes **ID definitions** via human-facing formats, for example:

```markdown
- [ ] **ID**: `cpt-my-system-fr-login`
- [x] `p1` - **ID**: `cpt-my-system-flow-login`
```

The scanner emits hits with:

- `type: definition`
- `id: <cpt-id>`
- `line: <line number>`
- `checked: true|false` (when a checkbox is present)
- `priority: pN` (when present)

#### ID References

Scanning recognizes **references** in three ways:

- Standalone backticked IDs on list lines:
  - ``- `cpt-my-system-fr-login` ``
  - ``* `cpt-my-system-fr-login` ``
- Any inline backticked occurrence:
  - `... Inline `cpt-my-system-fr-login` here ...`

The scanner emits hits with:

- `type: reference`
- `id: <cpt-id>`
- `line: <line number>`

#### CDSL Instruction Extraction

Scanning can extract CDSL instructions (see `requirements/CDSL.md`).

The scanner identifies lines matching the CDSL step format, and emits:

- `type: cdsl_instruction`
- `phase: <int>`
- `inst: <string>` (without the `inst-` prefix)
- `line: <line number>`

##### Parent binding rule

Extracted CDSL instructions use a best-effort **parent binding** rule:

- The instruction’s `parent_id` is the **nearest preceding ID definition** found above the instruction.
- If no preceding ID definition exists, `parent_id` is omitted.

#### Ignoring Code Fences

All scanning MUST ignore content inside fenced code blocks:

```markdown
```
...ignored...
```
```

This prevents documentation examples from being interpreted as real IDs/instructions.

### Validation Behavior

#### Template Structure Validation

- Template block structure validation is skipped.

#### Cross-Artifact Consistency

Artifacts participate in cross-artifact checks:

- Orphaned references (a reference to an undefined ID) may be reported.
- Duplicate ID definitions may be reported (implementation-defined).

#### Traceability Interaction

Artifacts can interact with code traceability (see `requirements/traceability.md`) depending on registry settings.

Key rule:

- If an artifact’s registry traceability mode is `FULL`, Cypilot may accept that code markers reference IDs defined in that artifact.

#### Covered-By (Fallback)

When there is no additional metadata for covered-by constraints, coverage expectations are approximated:

- For artifacts, each `**ID**: ...` definition SHOULD be referenced from at least one other artifact kind.
- If the project scope only contains one kind (no “other kinds” exist), Cypilot SHOULD emit a warning instead of an error.

### Content Scoping (Optional Helper)

Some tools may provide a helper for retrieving an approximate content “scope” for a given ID in a document.

The scope heuristics are best-effort and may use:

- Heading-based scopes (e.g., a heading line containing an ID)
- Separator-based scopes (implementation-defined)

This is not a validation guarantee; it is intended for navigation and UX.

## References

- `requirements/traceability.md` (to_code and traceability concepts)
