# SDLC Kit Taxonomy

Canonical taxonomy for the SDLC kit.

This guide defines what each SDLC artifact/code kind is, how it transforms into the next layer, how it traces to upstream IDs, and which files define templates/rules/examples.

## Dependency chain

In the SDLC kit, artifacts form a strict chain:

```mermaid
graph LR
  PRD --> ADR --> DESIGN --> DECOMPOSITION --> SPEC --> CODE
```

## Kinds

### PRD

**Purpose**: product intent and problem definition.

**Defines IDs** (examples):
- Actors: `cpt-{system}-actor-{slug}`
- Functional requirements: `cpt-{system}-fr-{slug}`
- Non-functional requirements: `cpt-{system}-nfr-{slug}`
- Use cases: `cpt-{system}-usecase-{slug}`

**Transforms into**:
- **DESIGN**: design drivers reference PRD FR/NFR IDs and describe architectural responses.
- **DECOMPOSITION**/**SPEC**: downstream layers must keep referencing the same PRD IDs they cover.

**Traceability**:
- PRD is the root of many downstream references (FR/NFR coverage).

**Validation**:
- Template structure + ID formats
- Cross-reference validity (downstream references must resolve)

**Files**:
- Template: [kits/sdlc/artifacts/PRD/template.md](../artifacts/PRD/template.md)
- Rules: [kits/sdlc/artifacts/PRD/rules.md](../artifacts/PRD/rules.md)
- Checklist: [kits/sdlc/artifacts/PRD/checklist.md](../artifacts/PRD/checklist.md)
- Examples: [kits/sdlc/artifacts/PRD/examples/](../artifacts/PRD/examples/)

### ADR

**Purpose**: record a single architecture decision (context → options → outcome → consequences).

**Defines IDs**:
- ADR record: `cpt-{system}-adr-{slug}`

**Transforms into**:
- **DESIGN**: design drivers reference ADR IDs and incorporate decisions.

**Traceability**:
- ADR IDs are referenced from DESIGN (and optionally from SPEC context).

**Validation**:
- Template structure + ID format + required Meta fields

**Files**:
- Template: [kits/sdlc/artifacts/ADR/template.md](../artifacts/ADR/template.md)
- Rules: [kits/sdlc/artifacts/ADR/rules.md](../artifacts/ADR/rules.md)
- Checklist: [kits/sdlc/artifacts/ADR/checklist.md](../artifacts/ADR/checklist.md)
- Examples: [kits/sdlc/artifacts/ADR/examples/](../artifacts/ADR/examples/)

### DESIGN

**Purpose**: the technical architecture that satisfies PRD requirements and ADR decisions.

**References upstream IDs**:
- PRD FR/NFR IDs (as drivers)
- ADR IDs (as decision drivers)

**Defines IDs** (examples):
- Principles: `cpt-{system}-principle-{slug}`
- Constraints: `cpt-{system}-constraint-{slug}`
- Components: `cpt-{system}-component-{slug}`
- Sequences: `cpt-{system}-seq-{slug}`
- DB tables (optional): `cpt-{system}-dbtable-{slug}`

**Transforms into**:
- **DECOMPOSITION**: specs are defined as work units that cover specific design elements (principles/constraints/components/etc.).

**Traceability**:
- DESIGN references PRD/ADR.
- DECOMPOSITION/SPEC must keep referencing the DESIGN IDs they implement/cover.

**Validation**:
- Template structure + ID formats
- Cross-reference validity for all referenced IDs

**Files**:
- Template: [kits/sdlc/artifacts/DESIGN/template.md](../artifacts/DESIGN/template.md)
- Rules: [kits/sdlc/artifacts/DESIGN/rules.md](../artifacts/DESIGN/rules.md)
- Checklist: [kits/sdlc/artifacts/DESIGN/checklist.md](../artifacts/DESIGN/checklist.md)
- Examples: [kits/sdlc/artifacts/DESIGN/examples/](../artifacts/DESIGN/examples/)

### DECOMPOSITION

**Purpose**: turn DESIGN into a set of implementable specs with explicit coverage links.

**Defines IDs**:
- Overall status tracker: `cpt-{system}-status-overall`
- Specs: `cpt-{system}-spec-{slug}`

**References upstream IDs**:
- PRD FR/NFR IDs (requirements covered)
- DESIGN IDs (principles/constraints/components/sequences/data)

**Transforms into**:
- **SPEC**: each decomposition entry links to a spec folder (`specs/`) containing a spec design.

**Traceability**:
- A spec entry is the upstream anchor for a SPEC design (`SPEC` references the `spec` ID).

**Validation**:
- Template structure + spec link format
- Cross-reference validity for all coverage references

**Files**:
- Template: [kits/sdlc/artifacts/DECOMPOSITION/template.md](../artifacts/DECOMPOSITION/template.md)
- Rules: [kits/sdlc/artifacts/DECOMPOSITION/rules.md](../artifacts/DECOMPOSITION/rules.md)
- Checklist: [kits/sdlc/artifacts/DECOMPOSITION/checklist.md](../artifacts/DECOMPOSITION/checklist.md)
- Examples: [kits/sdlc/artifacts/DECOMPOSITION/examples/](../artifacts/DECOMPOSITION/examples/)

### SPEC

**Purpose**: the executable(ish) behavior spec for a single spec, with definition-of-done and implementable steps.

**References upstream IDs**:
- The decomposition spec ID: `cpt-{system}-spec-{slug}`
- PRD actor IDs (actors)
- PRD FR/NFR IDs (coverage)
- DESIGN IDs (principles/constraints/components/sequences/data)

**Defines IDs** (SDLC code-traceable kinds):
- Flow: `cpt-{system}-spec-{spec}-flow-{slug}`
- Algorithm: `cpt-{system}-spec-{spec}-algo-{slug}`
- State machine: `cpt-{system}-spec-{spec}-state-{slug}`
- Requirement (definition-of-done): `cpt-{system}-spec-{spec}-req-{slug}`

These IDs are typically marked `to_code="true"` in the template, which makes them subject to code coverage checks.

**Transforms into**:
- **CODE**: implement flows/algorithms/states/requirements in source code and tag implementation with Cypilot markers.

**Traceability**:
- SPEC IDs are referenced from code using scope markers: `@cpt-{kind}:{cpt-id}:p{N}`.
- Instruction-level implementations can be wrapped with block markers:
  - `@cpt-begin:{cpt-id}:p{N}:inst-{local}` / `@cpt-end:...`

Phase tokens:
- SPEC step lines use `ph-{N}` (as part of the step formatting).
- Code markers use `p{N}` (as part of marker syntax).

**Validation**:
- Template structure + ID formats
- Cross-reference validity for all referenced IDs
- Code coverage and orphan checks via `validate-code`

**Files**:
- Template: [kits/sdlc/artifacts/SPEC/template.md](../artifacts/SPEC/template.md)
- Rules: [kits/sdlc/artifacts/SPEC/rules.md](../artifacts/SPEC/rules.md)
- Checklist: [kits/sdlc/artifacts/SPEC/checklist.md](../artifacts/SPEC/checklist.md)
- Example: [kits/sdlc/artifacts/SPEC/examples/example.md](../artifacts/SPEC/examples/example.md)

### CODE

**Purpose**: the implementation layer validated against SPEC IDs.

**Defines**:
- No new Cypilot IDs are defined in code. Code only references IDs that exist in artifacts.

**Traceability**:
- Mark code with Cypilot markers as specified in `requirements/traceability.md`.

**Validation**:
- Structure and pairing checks + cross-validation + coverage checks via `validate-code`.
- Semantic code review criteria via SDLC codebase checklist.

**Files**:
- Rules: [kits/sdlc/codebase/rules.md](../codebase/rules.md)
- Checklist: [kits/sdlc/codebase/checklist.md](../codebase/checklist.md)

## Validation commands

- Validate artifacts (templates + cross-refs): `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py validate`
- Validate code markers (pairing + coverage): `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py validate-code`
- Validate kit package itself: `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py validate-kits`

## References

- Traceability marker spec: [requirements/traceability.md](../../../requirements/traceability.md)
- Template marker spec: [requirements/template.md](../../../requirements/template.md)
- Rules format spec: [requirements/rules-format.md](../../../requirements/rules-format.md)
- SDLC behavior language (CDSL): [requirements/CDSL.md](../../../requirements/CDSL.md)