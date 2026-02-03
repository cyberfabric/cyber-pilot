# DECOMPOSITION Rules

**Artifact**: DECOMPOSITION (Design Decomposition)
**Purpose**: Rules for DECOMPOSITION artifact generation and validation
**Version**: 2.0
**Last Updated**: 2025-02-03

**Dependencies**:
- `template.md` — required structure
- `checklist.md` — decomposition quality criteria
- `examples/example.md` — reference implementation
- `{Spider}/requirements/template.md` — Spider template marker syntax specification

---

## Table of Contents

1. [Requirements](#requirements)
   - [Structural Requirements](#structural-requirements)
   - [Decomposition Quality Requirements](#decomposition-quality-requirements)
   - [Checkbox Management](#checkbox-management-requirements)
2. [Tasks](#tasks)
   - [Phase 1-3: Setup through IDs and Structure](#phase-1-setup)
   - [Phase 4: Feature Scaffolding](#phase-4-feature-scaffolding)
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
- [ ] **DO NOT copy `spider-template:` frontmatter** — that is template metadata only
- [ ] Artifact frontmatter (optional): use `spd:` format for document metadata
- [ ] All required sections present and non-empty
- [ ] Each feature has unique ID: `spd-{system}-feature-{slug}`
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

**Checkbox Types in DECOMPOSITION**:

1. **Overall Status Checkbox** (`id:status`):
   - `[ ] p1 - spd-{system}-status-overall` — unchecked until ALL features are implemented
   - `[x] p1 - spd-{system}-status-overall` — checked when ALL features are `[x]`

2. **Feature Checkbox** (`id:feature`):
   - `[ ] p1 - spd-{system}-feature-{slug}` — unchecked while feature is in progress
   - `[x] p1 - spd-{system}-feature-{slug}` — checked when feature is fully implemented

3. **Reference Checkboxes** (`id-ref:*`):
   - `id-ref:fr` — Requirements Covered
   - `id-ref:principle` — Design Principles Covered
   - `id-ref:constraint` — Design Constraints Covered
   - `id-ref:component` — Design Components
   - `id-ref:seq` — Sequences
   - `id-ref:dbtable` — Data

**Checkbox Cascade Rules**:

- [ ] All `id-ref` checkboxes within a feature block MUST be checked before the feature's `id:feature` can be checked
- [ ] All `id:feature` checkboxes MUST be checked before `id:status` can be checked
- [ ] If ANY checkbox within a feature block is unchecked, the feature checkbox MUST remain unchecked

**Cross-Artifact Checkbox Synchronization (`covered_by` Relationships)**:

| Source Artifact | ID Type | `covered_by` | Meaning |
|-----------------|---------|--------------|---------|
| PRD | `id:fr` | `DESIGN,DECOMPOSITION,FEATURE` | FR is covered when referenced in downstream artifacts |
| PRD | `id:nfr` | `DESIGN,DECOMPOSITION,FEATURE` | NFR is covered when referenced in downstream artifacts |
| DESIGN | `id:principle` | `DECOMPOSITION,FEATURE` | Principle is covered when applied in features |
| DESIGN | `id:constraint` | `DECOMPOSITION,FEATURE` | Constraint is covered when satisfied in features |
| DESIGN | `id:component` | `DECOMPOSITION,FEATURE` | Component is covered when integrated in features |
| DESIGN | `id:seq` | `DECOMPOSITION,FEATURE` | Sequence is covered when implemented in features |
| DESIGN | `id:dbtable` | `DECOMPOSITION,FEATURE` | Table is covered when used in features |

---

## Tasks

Agent executes tasks during generation:

### Phase 1: Setup

- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for decomposition quality guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read DESIGN to identify elements to decompose
- [ ] Read PRD to identify requirements to cover

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

- [ ] Generate feature IDs: `spd-{system}-feature-{slug}`
- [ ] Assign priorities based on dependency order
- [ ] Set initial status to NOT_STARTED
- [ ] Link to DESIGN elements being implemented
- [ ] Verify uniqueness with `python3 {Spider}/skills/spider/scripts/spider.py list-ids`

### Phase 4: Feature Scaffolding

Create stub files for all features defined in decomposition to ensure links are valid:

- [ ] For each feature entry with slug `{slug}`:
  - Create directory: `{features_dir}/feature-{slug}/`
  - Create stub file: `{features_dir}/feature-{slug}/DESIGN.md`
- [ ] Stub file content (minimal valid structure):

```markdown
<!-- spd:#:feature -->
# Feature: {slug}

<!-- spd:##:overview -->
## Overview

**Status**: NOT_STARTED

<!-- spd:id:feature has="priority,task" -->
- [ ] `p1` - **ID**: `spd-{system}-feature-{slug}`

This feature design is a placeholder. Generate full content with `/spider-generate FEATURE`.
<!-- spd:##:overview -->
<!-- spd:#:feature -->
```

- [ ] Verify all feature links in DECOMPOSITION resolve to existing files

### Phase 5: Quality Check

- [ ] Compare output to `examples/example.md`
- [ ] Self-review against `checklist.md` COV, EXC, ATTR, TRC, DEP sections
- [ ] Verify 100% design element coverage
- [ ] Verify no scope overlaps between features
- [ ] Verify dependency graph is valid DAG

### Phase 6: Checkbox Status Workflow

**Initial Creation (New Feature)**:
1. Create feature entry with `[ ]` unchecked on `id:feature`
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

**Feature Completion (Marking Feature Done)**:
1. Verify ALL `id-ref` blocks within the feature have `[x]`
2. Run `python3 {Spider}/skills/spider/scripts/spider.py validate` to confirm no checkbox inconsistencies
3. Change the `id:feature` line from `[ ]` to `[x]`
4. Update feature status emoji (e.g., ⏳ → ✅)

**Manifest Completion (Marking Overall Done)**:
1. Verify ALL `id:feature` blocks have `[x]`
2. Run `python3 {Spider}/skills/spider/scripts/spider.py validate` to confirm cascade consistency
3. Change the `id:status` line from `[ ]` to `[x]`

---

## Validation

Validation workflow applies rules in two phases:

### Phase 1: Structural Validation (Deterministic)

Run `python3 {Spider}/skills/spider/scripts/spider.py validate --artifact <path>` for:
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
⚠ Template not found: weavers/sdlc/artifacts/DECOMPOSITION/template.md
→ Verify Spider installation is complete
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
| Features defined | `/spider-generate FEATURE` — design first/next feature |
| Feature IMPLEMENTED | Update feature status in decomposition |
| All features IMPLEMENTED | `/spider-validate DESIGN` — validate design completion |
| New feature needed | Add to decomposition, then `/spider-generate FEATURE` |
| Want checklist review only | `/spider-validate semantic` — decomposition quality validation |
