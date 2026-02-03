# SDLC Weaver Taxonomy

Canonical taxonomy for the SDLC weaver.

This guide defines what each SDLC artifact/code kind is, how it transforms into the next layer, how it traces to upstream IDs, and which files define templates/rules/examples.

## Pipeline (dependency chain)

In the SDLC weaver, artifacts form a strict chain:

```
PRD
  -> ADR
    -> DESIGN
      -> DECOMPOSITION
        -> FEATURE
          -> CODE
```

## Kinds

### PRD

**Purpose**: product intent and problem definition.

**Defines IDs** (examples):
- Actors: `spd-{system}-actor-{slug}`
- Functional requirements: `spd-{system}-fr-{slug}`
- Non-functional requirements: `spd-{system}-nfr-{slug}`
- Use cases: `spd-{system}-usecase-{slug}`

**Transforms into**:
- **DESIGN**: design drivers reference PRD FR/NFR IDs and describe architectural responses.
- **DECOMPOSITION**/**FEATURE**: downstream layers must keep referencing the same PRD IDs they cover.

**Traceability**:
- PRD is the root of many downstream references (FR/NFR coverage).

**Validation**:
- Template structure + ID formats
- Cross-reference validity (downstream references must resolve)

**Files**:
- Template: [weavers/sdlc/artifacts/PRD/template.md](../artifacts/PRD/template.md)
- Rules: [weavers/sdlc/artifacts/PRD/rules.md](../artifacts/PRD/rules.md)
- Checklist: [weavers/sdlc/artifacts/PRD/checklist.md](../artifacts/PRD/checklist.md)
- Examples: [weavers/sdlc/artifacts/PRD/examples/](../artifacts/PRD/examples/)

### ADR

**Purpose**: record a single architecture decision (context → options → outcome → consequences).

**Defines IDs**:
- ADR record: `spd-{system}-adr-{slug}`

**Transforms into**:
- **DESIGN**: design drivers reference ADR IDs and incorporate decisions.

**Traceability**:
- ADR IDs are referenced from DESIGN (and optionally from FEATURE context).

**Validation**:
- Template structure + ID format + required Meta fields

**Files**:
- Template: [weavers/sdlc/artifacts/ADR/template.md](../artifacts/ADR/template.md)
- Rules: [weavers/sdlc/artifacts/ADR/rules.md](../artifacts/ADR/rules.md)
- Checklist: [weavers/sdlc/artifacts/ADR/checklist.md](../artifacts/ADR/checklist.md)
- Examples: [weavers/sdlc/artifacts/ADR/examples/](../artifacts/ADR/examples/)

### DESIGN

**Purpose**: the technical architecture that satisfies PRD requirements and ADR decisions.

**References upstream IDs**:
- PRD FR/NFR IDs (as drivers)
- ADR IDs (as decision drivers)

**Defines IDs** (examples):
- Principles: `spd-{system}-principle-{slug}`
- Constraints: `spd-{system}-constraint-{slug}`
- Components: `spd-{system}-component-{slug}`
- Sequences: `spd-{system}-seq-{slug}`
- DB tables (optional): `spd-{system}-dbtable-{slug}`

**Transforms into**:
- **DECOMPOSITION**: features are defined as work units that cover specific design elements (principles/constraints/components/etc.).

**Traceability**:
- DESIGN references PRD/ADR.
- DECOMPOSITION/FEATURE must keep referencing the DESIGN IDs they implement/cover.

**Validation**:
- Template structure + ID formats
- Cross-reference validity for all referenced IDs

**Files**:
- Template: [weavers/sdlc/artifacts/DESIGN/template.md](../artifacts/DESIGN/template.md)
- Rules: [weavers/sdlc/artifacts/DESIGN/rules.md](../artifacts/DESIGN/rules.md)
- Checklist: [weavers/sdlc/artifacts/DESIGN/checklist.md](../artifacts/DESIGN/checklist.md)
- Examples: [weavers/sdlc/artifacts/DESIGN/examples/](../artifacts/DESIGN/examples/)

### DECOMPOSITION

**Purpose**: turn DESIGN into a set of implementable features with explicit coverage links.

**Defines IDs**:
- Overall status tracker: `spd-{system}-status-overall`
- Features: `spd-{system}-feature-{slug}`

**References upstream IDs**:
- PRD FR/NFR IDs (requirements covered)
- DESIGN IDs (principles/constraints/components/sequences/data)

**Transforms into**:
- **FEATURE**: each decomposition entry links to a feature folder (`feature-{slug}/`) containing a feature design.

**Traceability**:
- A feature entry is the upstream anchor for a FEATURE design (`FEATURE` references the `feature` ID).

**Validation**:
- Template structure + feature link format
- Cross-reference validity for all coverage references

**Files**:
- Template: [weavers/sdlc/artifacts/DECOMPOSITION/template.md](../artifacts/DECOMPOSITION/template.md)
- Rules: [weavers/sdlc/artifacts/DECOMPOSITION/rules.md](../artifacts/DECOMPOSITION/rules.md)
- Checklist: [weavers/sdlc/artifacts/DECOMPOSITION/checklist.md](../artifacts/DECOMPOSITION/checklist.md)
- Examples: [weavers/sdlc/artifacts/DECOMPOSITION/examples/](../artifacts/DECOMPOSITION/examples/)

### FEATURE

**Purpose**: the executable(ish) behavior spec for a single feature, with definition-of-done and implementable steps.

**References upstream IDs**:
- The decomposition feature ID: `spd-{system}-feature-{slug}`
- PRD actor IDs (actors)
- PRD FR/NFR IDs (coverage)
- DESIGN IDs (principles/constraints/components/sequences/data)

**Defines IDs** (SDLC code-traceable kinds):
- Flow: `spd-{system}-feature-{feature}-flow-{slug}`
- Algorithm: `spd-{system}-feature-{feature}-algo-{slug}`
- State machine: `spd-{system}-feature-{feature}-state-{slug}`
- Requirement (definition-of-done): `spd-{system}-feature-{feature}-req-{slug}`

These IDs are typically marked `to_code="true"` in the template, which makes them subject to code coverage checks.

**Transforms into**:
- **CODE**: implement flows/algorithms/states/requirements in source code and tag implementation with Spider markers.

**Traceability**:
- FEATURE IDs are referenced from code using scope markers: `@spider-{kind}:{spd-id}:p{N}`.
- Instruction-level implementations can be wrapped with block markers:
  - `@spider-begin:{spd-id}:p{N}:inst-{local}` / `@spider-end:...`

Phase tokens:
- FEATURE step lines use `ph-{N}` (as part of the step formatting).
- Code markers use `p{N}` (as part of marker syntax).

**Validation**:
- Template structure + ID formats
- Cross-reference validity for all referenced IDs
- Code coverage and orphan checks via `validate-code`

**Files**:
- Template: [weavers/sdlc/artifacts/FEATURE/template.md](../artifacts/FEATURE/template.md)
- Rules: [weavers/sdlc/artifacts/FEATURE/rules.md](../artifacts/FEATURE/rules.md)
- Checklist: [weavers/sdlc/artifacts/FEATURE/checklist.md](../artifacts/FEATURE/checklist.md)
- Example: [weavers/sdlc/artifacts/FEATURE/examples/example.md](../artifacts/FEATURE/examples/example.md)

### CODE

**Purpose**: the implementation layer validated against FEATURE IDs.

**Defines**:
- No new Spider IDs are defined in code. Code only references IDs that exist in artifacts.

**Traceability**:
- Mark code with Spider markers as specified in `requirements/traceability.md`.

**Validation**:
- Structure and pairing checks + cross-validation + coverage checks via `validate-code`.
- Semantic code review criteria via SDLC codebase checklist.

**Files**:
- Rules: [weavers/sdlc/codebase/rules.md](../codebase/rules.md)
- Checklist: [weavers/sdlc/codebase/checklist.md](../codebase/checklist.md)

## Validation commands

- Validate artifacts (templates + cross-refs): `python3 {Spider}/skills/spider/scripts/spider.py validate`
- Validate code markers (pairing + coverage): `python3 {Spider}/skills/spider/scripts/spider.py validate-code`
- Validate weaver package itself: `python3 {Spider}/skills/spider/scripts/spider.py validate-weavers`

## References

- Traceability marker spec: [requirements/traceability.md](../../../requirements/traceability.md)
- Template marker spec: [requirements/template.md](../../../requirements/template.md)
- Rules format spec: [requirements/rules-format.md](../../../requirements/rules-format.md)
- SDLC behavior language (SDSL): [requirements/SDSL.md](../../../requirements/SDSL.md)