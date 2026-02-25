# DECOMPOSITION Rules

**Artifact**: DECOMPOSITION (Design Decomposition)
**Purpose**: Rules for DECOMPOSITION artifact generation and validation
**Version**: 2.0
**Last Updated**: 2026-02-03

**Dependencies**:
- `template.md` — required structure
- `checklist.md` — decomposition quality criteria
- `examples/example.md` — reference implementation
- `{cypilot_path}/.core/requirements/identifiers.md` — ID formats and naming
- `../../constraints.json` — kit-level constraints (primary rules for ID definitions/references)
- `{cypilot_path}/.core/requirements/kit-constraints.md` — constraints specification
- `{cypilot_path}/.core/schemas/kit-constraints.schema.json` — constraints JSON Schema

---

## Table of Contents

- [DECOMPOSITION Rules](#decomposition-rules)
  - [Table of Contents](#table-of-contents)
  - [Requirements](#requirements)
    - [Structural Requirements](#structural-requirements)
    - [Decomposition Quality Requirements](#decomposition-quality-requirements)
    - [Upstream Traceability](#upstream-traceability)
    - [Checkbox Management Requirements](#checkbox-management-requirements)
    - [Constraints (`constraints.json`) — Mandatory](#constraints-constraintsjson--mandatory)
  - [Tasks](#tasks)
    - [Phase 1: Setup](#phase-1-setup)
    - [Phase 2: Content Creation](#phase-2-content-creation)
    - [Phase 3: IDs and Structure](#phase-3-ids-and-structure)
    - [Phase 4: Quality Check](#phase-4-quality-check)
    - [Phase 5: Checkbox Status Workflow](#phase-5-checkbox-status-workflow)
  - [Validation](#validation)
    - [Phase 1: Structural Validation (Deterministic)](#phase-1-structural-validation-deterministic)
    - [Phase 2: Decomposition Quality Validation (Checklist-based)](#phase-2-decomposition-quality-validation-checklist-based)
    - [Validation Report](#validation-report)
  - [Error Handling](#error-handling)
    - [Missing Dependencies](#missing-dependencies)
    - [Decomposition Quality Issues](#decomposition-quality-issues)
    - [Escalation](#escalation)
  - [Next Steps](#next-steps)

---

## Requirements

Agent confirms understanding of requirements:

### Structural Requirements

- [ ] DECOMPOSITION follows `template.md` structure
- [ ] All required sections present and non-empty
- [ ] Each feature has unique ID: `cpt-{hierarchy-prefix}-feature-{slug}` (see artifacts.toml for hierarchy)
- [ ] Each feature has priority marker (`p1`-`p9`)
- [ ] Each feature has valid status
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate feature IDs

### Decomposition Quality Requirements

**Reference**: `checklist.md` for detailed criteria based on IEEE 1016 and ISO 21511

**Coverage (100% Rule)**:
- [ ] ALL components from DESIGN are assigned to at least one feature
- [ ] ALL sequences from DESIGN are assigned to at least one feature
- [ ] ALL data entities from DESIGN are assigned to at least one feature
- [ ] ALL requirements from PRD are covered transitively

**Exclusivity (Mutual Exclusivity)**:
- [ ] Features do not overlap in scope
- [ ] Each design element assigned to exactly one feature (or explicit reason for sharing)
- [ ] Clear boundaries between features

**Entity Attributes (IEEE 1016 §5.4.1)**:
- [ ] Each feature has identification (unique ID)
- [ ] Each feature has purpose (why it exists)
- [ ] Each feature has function (scope bullets)
- [ ] Each feature has subordinates (phases or "none")

**Dependencies**:
- [ ] Dependencies are explicit (Depends On field)
- [ ] No circular dependencies
- [ ] Foundation features have no dependencies

### Upstream Traceability

- [ ] When feature status → IMPLEMENTED, mark `[x]` on feature ID
- [ ] When all features for a component IMPLEMENTED → mark component `[x]` in DESIGN
- [ ] When all features for a capability IMPLEMENTED → mark capability `[x]` in PRD

### Checkbox Management Requirements

**Identifier Kinds and References in DECOMPOSITION**:

1. **Defined IDs (from `constraints.json`)**:
   - **Kind**: `status`
     - `[ ] p1 - **ID**: cpt-{hierarchy-prefix}-status-overall`
     - Checked when ALL feature entries are checked
   - **Kind**: `feature`
     - `[ ] p1 - **ID**: cpt-{hierarchy-prefix}-feature-{slug}`
     - Checked when the corresponding FEATURE spec is complete

2. **References (not ID definitions)**:
   - Any `cpt-...` occurrences outside an `**ID**` definition line are treated as references.
   - Examples of reference kinds commonly used in DECOMPOSITION entries:
     - PRD: `fr`, `nfr`
     - DESIGN: `principle`, `constraint`, `component`, `seq`, `dbtable`

**Progress / Cascade Rules**:

- [ ] A `feature` ID should not be checked until the feature entry is fully implemented (and downstream work is complete)
- [ ] `status-overall` should not be checked until ALL `feature` entries are checked

**Cross-Artifact Checkbox Synchronization (`constraints.json`)**:

Cross-artifact reference requirements and prohibitions are enforced using `../../constraints.json` (kit root):

- Coverage rules are defined by `identifiers[<kind>].references[<artifact_kind>].coverage` as `required|optional|prohibited`.
- The validator detects ID definitions and references from document text.

### Constraints (`constraints.json`) — Mandatory

- [ ] ALWAYS open and follow `../../constraints.json` (kit root)
- [ ] Treat `constraints.json` as the primary validator for:
  - where IDs are defined
  - where IDs are referenced
  - which cross-artifact references are required / optional / prohibited

**References**:
- `{cypilot_path}/.core/requirements/kit-constraints.md`
- `{cypilot_path}/.core/schemas/kit-constraints.schema.json`

---

## Tasks

Agent executes tasks during generation:

### Phase 1: Setup

- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for decomposition quality guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read DESIGN to identify elements to decompose
- [ ] Read PRD to identify requirements to cover
- [ ] Read adapter `artifacts.toml` to determine artifact paths
- [ ] Read adapter `specs/project-structure.md` (if exists) for directory conventions

### Phase 2: Content Creation

**Use example as reference for content style:**

| Section | Example Reference | Checklist Guidance |
|---------|-------------------|-------------------|
| Overview | How example explains decomposition strategy | COV-001: Coverage rationale |
| Feature List | How example structures features | ATTR-001-005: Entity attributes |
| Dependencies | How example documents dependencies | DEP-001: Dependency graph |

**Decomposition Strategy**:
1. Identify all components, sequences, data entities from DESIGN
2. Group related elements into features (high cohesion)
3. Minimize dependencies between features (loose coupling)
4. Verify 100% coverage (all elements assigned)
5. Verify mutual exclusivity (no overlaps)

### Phase 3: IDs and Structure

- [ ] Generate feature IDs: `cpt-{hierarchy-prefix}-feature-{slug}` (e.g., `cpt-myapp-feature-user-auth`)
- [ ] Assign priorities based on dependency order
- [ ] Set initial status to NOT_STARTED
- [ ] Link to DESIGN elements being implemented
- [ ] Verify uniqueness with `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py list-ids`

### Phase 4: Quality Check

- [ ] Compare output to `examples/example.md`
- [ ] Self-review against `checklist.md` COV, EXC, ATTR, TRC, DEP sections
- [ ] Verify 100% design element coverage
- [ ] Verify no scope overlaps between features
- [ ] Verify dependency graph is valid DAG

### Phase 5: Checkbox Status Workflow

**Initial Creation (New Feature)**:
1. Create feature entry with `[ ]` unchecked on the feature ID
2. Add all reference blocks with `[ ]` unchecked on each referenced ID
3. Overall `status-overall` remains `[ ]` unchecked

**During Implementation (Marking Progress)**:
1. When a specific requirement is implemented:
   - Find the referenced `cpt-{system}-fr-{slug}` entry for that requirement
   - Change `[ ]` to `[x]` on that specific reference line
2. When a component is integrated:
   - Find the referenced `cpt-{system}-component-{slug}` entry
   - Change `[ ]` to `[x]`
3. Continue for all reference types as work progresses

**Feature Completion (Marking Feature Done)**:
1. Verify ALL referenced IDs within the feature entry have `[x]`
2. Run `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py validate` to confirm no checkbox inconsistencies
3. Change the feature ID line from `[ ]` to `[x]`
4. Update feature status emoji (e.g., ⏳ → ✅)

**Manifest Completion (Marking Overall Done)**:
1. Verify ALL feature entries have `[x]`
2. Run `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py validate` to confirm cascade consistency
3. Change the `status-overall` line from `[ ]` to `[x]`

---

## Validation

Validation workflow applies rules in two phases:

### Phase 1: Structural Validation (Deterministic)

Run `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py validate --artifact <path>` for:
- [ ] Template structure compliance
- [ ] ID format validation
- [ ] Priority markers present
- [ ] Valid status values
- [ ] No placeholders

### Phase 2: Decomposition Quality Validation (Checklist-based)

Apply `checklist.md` systematically:

1. **COV (Coverage)**: Verify 100% design element coverage
2. **EXC (Exclusivity)**: Verify no scope overlaps
3. **ATTR (Attributes)**: Verify each feature has all required attributes
4. **TRC (Traceability)**: Verify bidirectional traceability
5. **DEP (Dependencies)**: Verify valid dependency graph

### Validation Report

Output format:
```
DECOMPOSITION Validation Report
═══════════════════════════════

Structural: PASS/FAIL
Decomposition Quality: PASS/FAIL (N issues)

Issues:
- [SEVERITY] CHECKLIST-ID: Description
```

---

## Error Handling

### Missing Dependencies

**If `template.md` cannot be loaded**:
```
⚠ Template not found: kits/sdlc/artifacts/DECOMPOSITION/template.md
→ Verify Cypilot installation is complete
→ STOP — cannot proceed without template
```

**If DESIGN not accessible** (Phase 1 Setup):
```
⚠ DESIGN not found or not readable
→ Ask user for DESIGN location
→ Cannot decompose without DESIGN artifact
```

### Decomposition Quality Issues

**If coverage validation fails**:
```
⚠ Coverage gap: {design element} not assigned to any feature
→ Add design element to appropriate feature
→ Or document intentional exclusion with reasoning
```

**If exclusivity validation fails**:
```
⚠ Scope overlap: {design element} appears in multiple features: {feature1}, {feature2}
→ Assign to single feature
→ Or document intentional sharing with reasoning
```

### Escalation

**Ask user when**:
- Design elements are ambiguous (should it be one feature or multiple?)
- Decomposition granularity unclear (how fine to decompose?)
- Dependency ordering unclear

---

## Next Steps

After DECOMPOSITION generation/validation, offer these options:

| Condition | Suggested Next Step |
|-----------|---------------------|
| Features defined | `/cypilot-generate FEATURE` — design first/next feature |
| Feature IMPLEMENTED | Update feature status in decomposition |
| All features IMPLEMENTED | `/cypilot-analyze DESIGN` — validate design completion |
| New feature needed | Add to decomposition, then `/cypilot-generate FEATURE` |
| Want checklist review only | `/cypilot-analyze semantic` — decomposition quality validation |
