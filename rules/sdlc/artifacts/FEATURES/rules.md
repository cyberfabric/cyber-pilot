# FEATURES Rules

**Artifact**: FEATURES (Features Manifest)
**Purpose**: Rules for FEATURES manifest generation and validation
**Version**: 1.1
**Last Updated**: 2025-02-01

**Dependencies**:
- `template.md` — required structure
- `checklist.md` — semantic quality criteria
- `examples/example.md` — reference implementation
- `{FDD}/requirements/template.md` — FDD template marker syntax specification

---

## Table of Contents

1. [Requirements](#requirements)
   - [Structural Requirements](#structural-requirements)
   - [Versioning Requirements](#versioning-requirements)
   - [Semantic Requirements](#semantic-requirements)
   - [Checkbox Management](#checkbox-management-requirements)
2. [Tasks](#tasks)
   - [Phase 1-4: Setup through Quality Check](#phase-1-setup)
   - [Phase 5: Checkbox Status Workflow](#phase-5-checkbox-status-workflow)
3. [Validation](#validation)
4. [Error Handling](#error-handling)
5. [Next Steps](#next-steps)

---

## Requirements

Agent confirms understanding of requirements:

### Structural Requirements

- [ ] FEATURES follows `template.md` structure
- [ ] **DO NOT copy `fdd-template:` frontmatter** — that is template metadata only
- [ ] Artifact frontmatter (optional): use `fdd:` format for document metadata
- [ ] All required sections present and non-empty
- [ ] Each feature has unique ID: `fdd-{system}-feature-{slug}`
- [ ] Each feature has priority marker (`p1`-`p9`)
- [ ] Each feature has valid status
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate feature IDs

### Versioning Requirements

- [ ] When editing existing FEATURES: increment version in frontmatter
- [ ] When feature scope significantly changes: add `-v{N}` suffix to feature ID
- [ ] Format: `fdd-{system}-feature-{slug}-v2`
- [ ] Keep changelog of significant changes

### Semantic Requirements

**Reference**: `checklist.md` for detailed criteria

- [ ] Status overview reflects actual feature statuses
- [ ] Features map to PRD capabilities
- [ ] Feature grouping is logical and cohesive
- [ ] Dependencies between features documented
- [ ] Status progression is valid (NOT_STARTED → IN_DESIGN → DESIGN_READY → IN_DEVELOPMENT → IMPLEMENTED)

### Upstream Traceability

- [ ] When feature status → IMPLEMENTED, mark `[x]` on feature ID
- [ ] When all features for a component IMPLEMENTED → mark component `[x]` in DESIGN
- [ ] When all features for a capability IMPLEMENTED → mark capability `[x]` in PRD

### Checkbox Management Requirements

**Checkbox Types in FEATURES Manifest**:

1. **Overall Status Checkbox** (`id:status`):
   - `[ ] p1 - fdd-{system}-status-overall` — unchecked until ALL features are implemented
   - `[x] p1 - fdd-{system}-status-overall` — checked when ALL features are `[x]`

2. **Feature Checkbox** (`id:feature`):
   - `[ ] p1 - fdd-{system}-feature-{slug}` — unchecked while feature is in progress
   - `[x] p1 - fdd-{system}-feature-{slug}` — checked when feature is fully implemented

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
- [ ] When unchecking a feature, all nested `id-ref` checkboxes MAY remain checked (partial progress is preserved)

**When to Check Reference Checkboxes**:

| Reference Type | Check When |
|----------------|------------|
| `id-ref:fr` | Functional requirement is implemented and tested |
| `id-ref:principle` | Principle is applied in the implementation |
| `id-ref:constraint` | Constraint is satisfied and verified |
| `id-ref:component` | Component is implemented and integrated |
| `id-ref:seq` | Sequence flow is implemented and working |
| `id-ref:dbtable` | Database table is created and migrations applied |

**Cross-Artifact Checkbox Synchronization (`covered_by` Relationships)**:

PRD and DESIGN artifacts define IDs with `covered_by` attributes that specify which artifacts reference them:

| Source Artifact | ID Type | `covered_by` | Meaning |
|-----------------|---------|--------------|---------|
| PRD | `id:fr` | `DESIGN,FEATURES,FEATURE` | FR is covered when referenced in downstream artifacts |
| PRD | `id:nfr` | `DESIGN,FEATURES,FEATURE` | NFR is covered when referenced in downstream artifacts |
| DESIGN | `id:principle` | `FEATURES,FEATURE` | Principle is covered when applied in features |
| DESIGN | `id:constraint` | `FEATURES,FEATURE` | Constraint is covered when satisfied in features |
| DESIGN | `id:component` | `FEATURES,FEATURE` | Component is covered when integrated in features |
| DESIGN | `id:seq` | `FEATURES,FEATURE` | Sequence is covered when implemented in features |
| DESIGN | `id:dbtable` | `FEATURES,FEATURE` | Table is covered when used in features |

**When to Update Upstream Artifacts**:

- [ ] When `id-ref:fr` is checked in FEATURES → mark corresponding `id:fr` as `[x]` in PRD (if all references are checked)
- [ ] When `id-ref:principle` is checked → mark corresponding `id:principle` as `[x]` in DESIGN (if all references are checked)
- [ ] When `id-ref:constraint` is checked → mark corresponding `id:constraint` as `[x]` in DESIGN (if all references are checked)
- [ ] When `id-ref:component` is checked → mark corresponding `id:component` as `[x]` in DESIGN (if all references are checked)
- [ ] When `id-ref:seq` is checked → mark corresponding `id:seq` as `[x]` in DESIGN (if all references are checked)
- [ ] When `id-ref:dbtable` is checked → mark corresponding `id:dbtable` as `[x]` in DESIGN (if all references are checked)
- [ ] When `id:feature` is checked → update feature's status in FEATURES manifest

**Validation Checks** (automated via `python3 {FDD}/skills/fdd/scripts/fdd.py validate`):
- Will warn if a reference is `[x]` but its definition is not
- Will warn if definition has `covered_by` but no references exist in downstream artifacts
- Agent does NOT manually check `covered_by` — the CLI tool handles this automatically

---

## Tasks

Agent executes tasks during generation:

### Phase 1: Setup

- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read PRD to identify capabilities to implement

### Phase 2: Content Creation

**Use example as reference for content style:**

| Section | Example Reference | Checklist Guidance |
|---------|-------------------|-------------------|
| Status Overview | How example shows status counts | FEATURES-001: Status Accuracy |
| Feature List | How example structures features | FEATURES-002: Feature Coverage |
| Dependencies | How example documents dependencies | FEATURES-003: Dependency Clarity |

### Phase 3: IDs and Structure

- [ ] Generate feature IDs: `fdd-{system}-feature-{slug}`
- [ ] Assign priorities based on PRD capability priorities
- [ ] Set initial status to NOT_STARTED
- [ ] Link to PRD capabilities implemented
- [ ] Verify uniqueness with `python3 {FDD}/skills/fdd/scripts/fdd.py list-ids`

### Phase 4: Quality Check

- [ ] Compare output to `examples/example.md`
- [ ] Self-review against `checklist.md` MUST HAVE items
- [ ] Ensure status overview counts are accurate
- [ ] Verify PRD capability coverage

### Phase 5: Checkbox Status Workflow

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
2. Run `python3 {FDD}/skills/fdd/scripts/fdd.py validate` to confirm no checkbox inconsistencies
3. Change the `id:feature` line from `[ ]` to `[x]`
4. Update feature status emoji (e.g., ⏳ → ✅)

**Manifest Completion (Marking Overall Done)**:
1. Verify ALL `id:feature` blocks have `[x]`
2. Run `python3 {FDD}/skills/fdd/scripts/fdd.py validate` to confirm cascade consistency
3. Change the `id:status` line from `[ ]` to `[x]`

**Checkbox Syntax Reference**:
```markdown
<!-- Unchecked state -->
- [ ] `p1` - **ID**: `fdd-{system}-feature-{slug}`

<!-- Checked state -->
- [x] `p1` - **ID**: `fdd-{system}-feature-{slug}`
```

**Common Errors to Avoid**:
- ❌ Checking feature ID before all references are checked
- ❌ Checking overall status before all features are checked
- ❌ Leaving references checked but feature unchecked after rollback
- ❌ Inconsistent priority between definition and reference

---

## Validation

Validation workflow applies rules in two phases:

### Phase 1: Structural Validation (Deterministic)

Run `python3 {FDD}/skills/fdd/scripts/fdd.py validate --artifact <path>` for:
- [ ] Template structure compliance
- [ ] ID format validation
- [ ] Priority markers present
- [ ] Valid status values
- [ ] No placeholders

### Phase 2: Semantic Validation (Checklist-based)

Apply `checklist.md` systematically:

1. **Read checklist.md** in full
2. **For each MUST HAVE item**:
   - Check if requirement is met
   - If not met: report as violation with severity
   - If not applicable: verify explicit "N/A" with reasoning
3. **For each MUST NOT HAVE item**:
   - Scan document for violations
   - Report any findings

**Use example for quality baseline**:
- Compare feature descriptions to `examples/example.md`
- Verify status tracking completeness

### Validation Report

Output format:
```
FEATURES Validation Report
══════════════════════════

Structural: PASS/FAIL
Semantic: PASS/FAIL (N issues)

Issues:
- [SEVERITY] CHECKLIST-ID: Description
```

---

## Error Handling

### Missing Dependencies

**If `template.md` cannot be loaded**:
```
⚠ Template not found: rules/sdlc/artifacts/FEATURES/template.md
→ Verify FDD installation is complete
→ STOP — cannot proceed without template
```

**If `checklist.md` cannot be loaded**:
```
⚠ Checklist not found: rules/sdlc/artifacts/FEATURES/checklist.md
→ Structural validation possible, semantic validation skipped
→ Warn user: "Semantic validation unavailable"
```

**If PRD not accessible** (Phase 1 Setup):
```
⚠ PRD not found or not readable
→ Ask user for PRD location
→ Cannot generate features without PRD capabilities
```

### Checkbox Inconsistencies

**If cascade validation fails**:
```
⚠ Checkbox cascade error: {feature} has unchecked references but feature is marked [x]
→ Either uncheck the feature, or check all its references
→ Run validation again after fixing
```

**Recovery from partial update**:
1. Run `python3 {FDD}/skills/fdd/scripts/fdd.py validate --artifact <path>`
2. Review reported inconsistencies
3. Fix in order: references first, then features, then overall status

### Escalation

**Ask user when**:
- PRD capabilities are ambiguous or missing
- Feature scope unclear (should it be one feature or multiple?)
- Status progression is unclear (when is a feature "IMPLEMENTED"?)
- Cross-artifact checkbox synchronization fails

---

## Next Steps

After FEATURES generation/validation, offer these options:

| Condition | Suggested Next Step |
|-----------|---------------------|
| Features defined | `/fdd-generate FEATURE` — design first/next feature |
| Feature IMPLEMENTED | Update feature status in manifest |
| All features IMPLEMENTED | `/fdd-validate DESIGN` — validate design completion |
| New feature needed | Add to manifest, then `/fdd-generate FEATURE` |
| Want checklist review only | `/fdd-validate semantic` — semantic validation (skip deterministic) |
