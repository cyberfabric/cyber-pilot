# DESIGN Rules

**Artifact**: DESIGN (Technical Design Document)
**Purpose**: Rules for DESIGN generation and validation

---

## Table of Contents

1. [Requirements](#requirements)
   - [Structural Requirements](#structural-requirements)
   - [Versioning Requirements](#versioning-requirements)
   - [Semantic Requirements](#semantic-requirements)
   - [DESIGN Scope Guidelines](#design-scope-guidelines)
   - [Upstream Traceability](#upstream-traceability)
   - [Checkbox Management](#checkbox-management-covered_by-attribute)
2. [Tasks](#tasks)
   - [Phase 1: Setup](#phase-1-setup)
   - [Phase 2: Content Creation](#phase-2-content-creation)
   - [Phase 3: IDs and References](#phase-3-ids-and-references)
   - [Phase 4: Quality Check](#phase-4-quality-check)
3. [Validation](#validation)
4. [Next Steps](#next-steps)

---

**Dependencies**:
- `template.md` — required structure
- `checklist.md` — semantic quality criteria
- `examples/example.md` — reference implementation
- `{spider_path}/requirements/template.md` — Spider template marker syntax specification

---

## Requirements

Agent confirms understanding of requirements:

### Structural Requirements

- [ ] DESIGN follows `template.md` structure
- [ ] Artifact frontmatter (optional): use `spd:` format for document metadata
- [ ] All required sections present and non-empty
- [ ] All IDs follow `spd-{hierarchy-prefix}-{kind}-{slug}` convention (see artifacts.json for hierarchy)
- [ ] References to PRD are valid
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs within document

### Versioning Requirements

- [ ] When editing existing DESIGN: increment version in frontmatter
- [ ] When changing type/component definition: add `-v{N}` suffix to ID or increment existing version
- [ ] Format: `spd-{hierarchy-prefix}-type-{slug}-v2`, `spd-{hierarchy-prefix}-comp-{slug}-v3`, etc.
- [ ] Keep changelog of significant changes

### Semantic Requirements

**Reference**: `checklist.md` for detailed semantic criteria

- [ ] Architecture overview is complete and clear
- [ ] Domain model defines all core types
- [ ] Components have clear responsibilities and boundaries
- [ ] Integration points documented
- [ ] ADR references provided for key decisions
- [ ] PRD capabilities traced to components

### DESIGN Scope Guidelines

**One DESIGN per system/subsystem**. Match scope to architectural boundaries.

| Scope | Examples | Guideline |
|-------|----------|-----------|
| **Too broad** | "Entire platform design" for 50+ components | Split into subsystem DESIGNs |
| **Right size** | "Auth subsystem design" covering auth components | Clear boundary, manageable size |
| **Too narrow** | "Login button component design" | Implementation detail, use SPEC |

**DESIGN-worthy content**:
- System/subsystem architecture overview
- Domain model (core types, relationships)
- Component responsibilities and boundaries
- Integration points and contracts
- Key architectural decisions (reference ADRs)

**NOT DESIGN-worthy** (use SPEC instead):
- Individual spec implementation details
- UI flows and interactions
- Algorithm pseudo-code
- Test scenarios

**Relationship to other artifacts**:
- **PRD** → DESIGN: PRD defines WHAT, DESIGN defines HOW (high-level)
- **DESIGN** → DECOMPOSITION: DESIGN defines architecture, DECOMPOSITION lists implementations
- **DESIGN** → SPEC: DESIGN provides context, SPEC details implementation

### Upstream Traceability

- [ ] When component fully implemented → mark component `[x]` in DESIGN
- [ ] When all components for ADR implemented → update ADR status (PROPOSED → ACCEPTED)
- [ ] When all design elements for PRD capability implemented → mark capability `[x]` in PRD

### Checkbox Management (`covered_by` Attribute)

**Quick Reference**: Check DESIGN element when ALL specs referencing it are `[x]`.

| Element | Check when... |
|---------|---------------|
| `id:principle` | All specs applying principle are `[x]` |
| `id:constraint` | All specs satisfying constraint are `[x]` |
| `id:component` | All specs using component are `[x]` |
| `id:seq` | All specs implementing sequence are `[x]` |
| `id:dbtable` | All specs using table are `[x]` |

**Detailed Rules**:

DESIGN defines IDs with `covered_by` attributes that track downstream implementation:

| ID Type | `covered_by` | Meaning |
|---------|--------------|---------|
| `id:principle` | `DECOMPOSITION,SPEC` | Principle is covered when applied in spec designs |
| `id:constraint` | `DECOMPOSITION,SPEC` | Constraint is covered when satisfied by specs |
| `id:component` | `DECOMPOSITION,SPEC` | Component is covered when integrated in specs |
| `id:seq` | `DECOMPOSITION,SPEC` | Sequence is covered when implemented in specs |
| `id:dbtable` | `DECOMPOSITION,SPEC` | Table is covered when used in specs |

**Checkbox States**:

1. **Principle Checkbox** (`id:principle`):
   - `[ ] p1 - spd-{hierarchy-prefix}-principle-{slug}` — unchecked until principle is applied
   - `[x] p1 - spd-{hierarchy-prefix}-principle-{slug}` — checked when ALL specs applying this principle are `[x]`

2. **Constraint Checkbox** (`id:constraint`):
   - `[ ] p1 - spd-{hierarchy-prefix}-constraint-{slug}` — unchecked until constraint is satisfied
   - `[x] p1 - spd-{hierarchy-prefix}-constraint-{slug}` — checked when ALL specs satisfying this constraint are `[x]`

3. **Component Checkbox** (`id:component`):
   - `[ ] p1 - spd-{hierarchy-prefix}-comp-{slug}` — unchecked until component is implemented
   - `[x] p1 - spd-{hierarchy-prefix}-comp-{slug}` — checked when ALL specs using this component are `[x]`

4. **Sequence Checkbox** (`id:seq`):
   - `[ ] p1 - spd-{hierarchy-prefix}-seq-{slug}` — unchecked until sequence is implemented
   - `[x] p1 - spd-{hierarchy-prefix}-seq-{slug}` — checked when ALL specs implementing this sequence are `[x]`

5. **Database Table Checkbox** (`id:dbtable`):
   - `[ ] p1 - spd-{hierarchy-prefix}-dbtable-{slug}` — unchecked until table is created
   - `[x] p1 - spd-{hierarchy-prefix}-dbtable-{slug}` — checked when ALL specs using this table are `[x]`

**When to Check DESIGN Checkboxes**:

- [ ] A design element (principle, constraint, component, etc.) can be checked when:
  - All `id-ref` references in DECOMPOSITION manifest are `[x]`
  - All `id-ref` references in individual SPEC designs are `[x]`
  - Implementation is verified and tested

**Validation Checks**:
- `spider validate` will warn if `id:*` has no references in `covered_by` artifacts
- `spider validate` will warn if reference is `[x]` but definition is not

---

## Tasks

Agent executes tasks during generation:

### Phase 1: Setup

- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read parent PRD for context

**If PRD not found or incomplete**:
```
⚠ Parent PRD not found or incomplete
→ Option 1: Run /spider-generate PRD first (recommended)
→ Option 2: Continue without PRD (DESIGN will lack traceability)
   - Document "PRD pending" in DESIGN frontmatter
   - Skip PRD reference validation
   - Plan to update DESIGN when PRD available
```

**If PRD exists but outdated**:
```
⚠ PRD may be outdated (last modified: {date})
→ Review PRD before proceeding
→ If PRD needs updates: /spider-generate PRD UPDATE
→ If PRD is current: proceed with DESIGN
```

### Phase 2: Content Creation

**Apply checklist.md semantics during creation:**

| Checklist Section | Generation Task |
|-------------------|-----------------|
| ARCH-DESIGN-001: Architecture Overview | Document system purpose, high-level architecture, context diagram |
| ARCH-DESIGN-002: Principles Coherence | Define actionable, non-contradictory principles |
| DOMAIN-DESIGN-001: Domain Model | Define types, relationships, boundaries |
| COMP-DESIGN-001: Component Design | Define responsibilities, interfaces, dependencies |

**Partial Completion Handling**:

If DESIGN cannot be completed in a single session:

1. **Checkpoint progress**:
   - Note completed sections (Architecture, Domain, Components, etc.)
   - Note current section being worked on
   - List remaining sections
2. **Ensure valid intermediate state**:
   - All completed sections must be internally consistent
   - Add `status: DRAFT` to frontmatter
   - Mark incomplete sections with `<!-- INCOMPLETE: {reason} -->`
3. **Document resumption point**:
   ```
   DESIGN checkpoint:
   - Completed: Architecture Overview, Domain Model
   - In progress: Component Design (3/7 components)
   - Remaining: Sequences, Data Model
   - Resume: Continue with component spd-{hierarchy-prefix}-comp-{slug}
   ```
4. **On resume**:
   - Verify PRD unchanged since last session
   - Continue from documented checkpoint
   - Remove incomplete markers as sections are finished

### Phase 3: IDs and References

- [ ] Generate type IDs: `spd-{hierarchy-prefix}-type-{slug}` (e.g., `spd-myapp-type-user-entity`)
- [ ] Generate component IDs (if needed)
- [ ] Link to PRD actors/capabilities
- [ ] Reference relevant ADRs
- [ ] Verify uniqueness with `spider list-ids`

### Phase 4: Quality Check

- [ ] Self-review against `checklist.md` MUST HAVE items
- [ ] Ensure no MUST NOT HAVE violations
- [ ] Verify PRD traceability

---

## Validation

Validation workflow applies rules in two phases:

### Phase 1: Structural Validation (Deterministic)

Run `spider validate` for:
- [ ] Template structure compliance
- [ ] ID format validation
- [ ] Cross-reference validity
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

### Validation Report

Output format:
```
DESIGN Validation Report
════════════════════════

Structural: PASS/FAIL
Semantic: PASS/FAIL (N issues)

Issues:
- [SEVERITY] CHECKLIST-ID: Description
```

---

## Next Steps

After DESIGN generation/validation, offer these options:

| Condition | Suggested Next Step |
|-----------|---------------------|
| DESIGN complete | `/spider-generate DECOMPOSITION` — create specs manifest |
| Need architecture decision | `/spider-generate ADR` — document key decision |
| PRD missing/incomplete | `/spider-generate PRD` — create/update PRD first |
| DESIGN needs revision | Continue editing DESIGN |
| Want checklist review only | `/spider-analyze semantic` — semantic validation (skip deterministic) |
