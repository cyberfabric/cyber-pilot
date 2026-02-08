# DECOMPOSITION Rules

**Artifact**: DECOMPOSITION (Design Decomposition)
**Purpose**: Rules for DECOMPOSITION artifact generation and validation
**Version**: 2.0
**Last Updated**: 2025-02-03

**Dependencies**:
- `template.md` — required structure
- `checklist.md` — decomposition quality criteria
- `examples/example.md` — reference implementation
- `{cypilot_path}/requirements/template.md` — Cypilot template marker syntax specification
- `../../constraints.json` — kit-level constraints (primary rules for ID definitions/references)
- `{cypilot_path}/requirements/kit-constraints.md` — constraints specification
- `{cypilot_path}/schemas/kit-constraints.schema.json` — constraints JSON Schema

---

## Table of Contents

1. [Requirements](#requirements)
   - [Structural Requirements](#structural-requirements)
   - [Decomposition Quality Requirements](#decomposition-quality-requirements)
   - [Checkbox Management](#checkbox-management-requirements)
2. [Tasks](#tasks)
   - [Phase 1-3: Setup through IDs and Structure](#phase-1-setup)
   - [Phase 4: Spec Scaffolding](#phase-4-spec-scaffolding)
   - [Phase 5: Quality Check](#phase-5-quality-check)
   - [Phase 6: Checkbox Status Workflow](#phase-6-checkbox-status-workflow)
3. [Validation](#validation)
4. [Error Handling](#error-handling)
5. [Next Steps](#next-steps)

---

## Requirements

Agent confirms understanding of requirements:

### Structural Requirements

- [ ] DECOMPOSITION follows `template.md` structure
- [ ] Artifact frontmatter (optional): use `cpt:` format for document metadata
- [ ] All required sections present and non-empty
- [ ] Each spec has unique ID: `cpt-{hierarchy-prefix}-spec-{slug}` (see artifacts.json for hierarchy)
- [ ] Each spec has priority marker (`p1`-`p9`)
- [ ] Each spec has valid status
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate spec IDs

### Decomposition Quality Requirements

**Reference**: `checklist.md` for detailed criteria based on IEEE 1016 and ISO 21511

**Coverage (100% Rule)**:
- [ ] ALL components from DESIGN are assigned to at least one spec
- [ ] ALL sequences from DESIGN are assigned to at least one spec
- [ ] ALL data entities from DESIGN are assigned to at least one spec
- [ ] ALL requirements from PRD are covered transitively

**Exclusivity (Mutual Exclusivity)**:
- [ ] Specs do not overlap in scope
- [ ] Each design element assigned to exactly one spec (or explicit reason for sharing)
- [ ] Clear boundaries between specs

**Entity Attributes (IEEE 1016 §5.4.1)**:
- [ ] Each spec has identification (unique ID)
- [ ] Each spec has purpose (why it exists)
- [ ] Each spec has function (scope bullets)
- [ ] Each spec has subordinates (phases or "none")

**Dependencies**:
- [ ] Dependencies are explicit (Depends On field)
- [ ] No circular dependencies
- [ ] Foundation specs have no dependencies

### Upstream Traceability

- [ ] When spec status → IMPLEMENTED, mark `[x]` on spec ID
- [ ] When all specs for a component IMPLEMENTED → mark component `[x]` in DESIGN
- [ ] When all specs for a capability IMPLEMENTED → mark capability `[x]` in PRD

### Checkbox Management Requirements

**Checkbox Types in DECOMPOSITION**:

1. **Overall Status Checkbox** (`id:status`):
   - `[ ] p1 - cpt-{hierarchy-prefix}-status-overall` — unchecked until ALL specs are implemented
   - `[x] p1 - cpt-{hierarchy-prefix}-status-overall` — checked when ALL specs are `[x]`

2. **Spec Checkbox** (`id:spec`):
   - `[ ] p1 - cpt-{hierarchy-prefix}-spec-{slug}` — unchecked while spec is in progress
   - `[x] p1 - cpt-{hierarchy-prefix}-spec-{slug}` — checked when spec is fully implemented

3. **Reference Checkboxes** (`id-ref:*`):
   - `id-ref:fr` — Requirements Covered
   - `id-ref:principle` — Design Principles Covered
   - `id-ref:constraint` — Design Constraints Covered
   - `id-ref:component` — Design Components
   - `id-ref:seq` — Sequences
   - `id-ref:dbtable` — Data

**Checkbox Cascade Rules**:

- [ ] All `id-ref` checkboxes within a spec block MUST be checked before the spec's `id:spec` can be checked
- [ ] All `id:spec` checkboxes MUST be checked before `id:status` can be checked
- [ ] If ANY checkbox within a spec block is unchecked, the spec checkbox MUST remain unchecked

**Cross-Artifact Checkbox Synchronization (`constraints.json`)**:

Cross-artifact reference requirements and prohibitions are enforced using `../../constraints.json` (kit root):

- Coverage rules are defined by `identifiers[<kind>].references[<artifact_kind>].coverage` as `required|optional|prohibited`.
- The validator is markerless-first: it detects ID definitions and references from document text, even if markers are missing.

### Constraints (`constraints.json`) — Mandatory

- [ ] ALWAYS open and follow `../../constraints.json` (kit root)
- [ ] Treat `constraints.json` as the primary validator for:
  - where IDs are defined
  - where IDs are referenced
  - which cross-artifact references are required / optional / prohibited

**References**:
- `{cypilot_path}/requirements/kit-constraints.md`
- `{cypilot_path}/schemas/kit-constraints.schema.json`

---

## Tasks

Agent executes tasks during generation:

### Phase 1: Setup

- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for decomposition quality guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read DESIGN to identify elements to decompose
- [ ] Read PRD to identify requirements to cover
- [ ] Read adapter `artifacts.json` to determine artifact paths
- [ ] Read adapter `specs/project-structure.md` (if exists) for directory conventions

### Phase 2: Content Creation

**Use example as reference for content style:**

| Section | Example Reference | Checklist Guidance |
|---------|-------------------|-------------------|
| Overview | How example explains decomposition strategy | COV-001: Coverage rationale |
| Spec List | How example structures specs | ATTR-001-005: Entity attributes |
| Dependencies | How example documents dependencies | DEP-001: Dependency graph |

**Decomposition Strategy**:
1. Identify all components, sequences, data entities from DESIGN
2. Group related elements into specs (high cohesion)
3. Minimize dependencies between specs (loose coupling)
4. Verify 100% coverage (all elements assigned)
5. Verify mutual exclusivity (no overlaps)

### Phase 3: IDs and Structure

- [ ] Generate spec IDs: `cpt-{hierarchy-prefix}-spec-{slug}` (e.g., `cpt-myapp-spec-user-auth`)
- [ ] Assign priorities based on dependency order
- [ ] Set initial status to NOT_STARTED
- [ ] Link to DESIGN elements being implemented
- [ ] Verify uniqueness with `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py list-ids`

### Phase 4: Spec Scaffolding

Create stub files for all specs defined in decomposition to ensure links are valid.

**Path resolution**:
1. Check if SPEC with matching slug already registered in `artifacts` array
2. If found, use registered path (it's a FULL path relative to `project_root`)
3. If not found, derive default path:
   - Read system's `artifacts_dir` from `artifacts.json` (default: `architecture`)
   - Use kit's default subdirectory for SPECs: `specs/`
   - Create at: `{artifacts_dir}/specs/{slug}.md`
4. Register new SPEC in `artifacts.json` with FULL path

- [ ] For each spec entry with slug `{slug}`:
  - Resolve path from adapter (see Path resolution above)
  - Create stub file at resolved path
  - Register in `artifacts.json` if not already registered
- [ ] Stub file content (minimal valid structure):

```markdown
<!-- cpt:#:spec -->
# Spec: {slug}

<!-- cpt:##:overview -->
## Overview

**Status**: NOT_STARTED

<!-- cpt:id:spec has="priority,task" -->
- [ ] `p1` - **ID**: `cpt-{hierarchy-prefix}-spec-{slug}`

This spec design is a placeholder. Generate full content with `cypilot make SPEC spec for {slug}`.
<!-- cpt:##:overview -->
<!-- cpt:#:spec -->
```

- [ ] Verify all spec links in DECOMPOSITION resolve to existing files

### Phase 5: Quality Check

- [ ] Compare output to `examples/example.md`
- [ ] Self-review against `checklist.md` COV, EXC, ATTR, TRC, DEP sections
- [ ] Verify 100% design element coverage
- [ ] Verify no scope overlaps between specs
- [ ] Verify dependency graph is valid DAG

### Phase 6: Checkbox Status Workflow

**Initial Creation (New Spec)**:
1. Create spec entry with `[ ]` unchecked on `id:spec`
2. Add all `id-ref` blocks with `[ ]` unchecked on each reference
3. Overall `id:status` remains `[ ]` unchecked

**During Implementation (Marking Progress)**:
1. When a specific requirement is implemented:
   - Find the `id-ref:fr` entry for that requirement
   - Change `[ ]` to `[x]` on that specific reference line
2. When a component is integrated:
   - Find the `id-ref:component` entry
   - Change `[ ]` to `[x]`
3. Continue for all reference types as work progresses

**Spec Completion (Marking Spec Done)**:
1. Verify ALL `id-ref` blocks within the spec have `[x]`
2. Run `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py validate` to confirm no checkbox inconsistencies
3. Change the `id:spec` line from `[ ]` to `[x]`
4. Update spec status emoji (e.g., ⏳ → ✅)

**Manifest Completion (Marking Overall Done)**:
1. Verify ALL `id:spec` blocks have `[x]`
2. Run `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py validate` to confirm cascade consistency
3. Change the `id:status` line from `[ ]` to `[x]`

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
3. **ATTR (Attributes)**: Verify each spec has all required attributes
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
⚠ Coverage gap: {design element} not assigned to any spec
→ Add design element to appropriate spec
→ Or document intentional exclusion with reasoning
```

**If exclusivity validation fails**:
```
⚠ Scope overlap: {design element} appears in multiple specs: {spec1}, {spec2}
→ Assign to single spec
→ Or document intentional sharing with reasoning
```

### Escalation

**Ask user when**:
- Design elements are ambiguous (should it be one spec or multiple?)
- Decomposition granularity unclear (how fine to decompose?)
- Dependency ordering unclear

---

## Next Steps

After DECOMPOSITION generation/validation, offer these options:

| Condition | Suggested Next Step |
|-----------|---------------------|
| Specs defined | `/cypilot-generate SPEC` — design first/next spec |
| Spec IMPLEMENTED | Update spec status in decomposition |
| All specs IMPLEMENTED | `/cypilot-analyze DESIGN` — validate design completion |
| New spec needed | Add to decomposition, then `/cypilot-generate SPEC` |
| Want checklist review only | `/cypilot-analyze semantic` — decomposition quality validation |
