# DESIGN Rules

**Artifact**: DESIGN (Technical Design Document)
**Purpose**: Rules for DESIGN generation and validation

**Dependencies**:
- `template.md` — required structure
- `checklist.md` — semantic quality criteria
- `examples/example.md` — reference implementation
- `{FDD}/requirements/template.md` — FDD template marker syntax specification

---

## Requirements

Agent confirms understanding of requirements:

### Structural Requirements

- [ ] DESIGN follows `template.md` structure
- [ ] **DO NOT copy `fdd-template:` frontmatter** — that is template metadata only
- [ ] Artifact frontmatter (optional): use `fdd:` format for document metadata
- [ ] All required sections present and non-empty
- [ ] All IDs follow `fdd-{project}-{kind}-{slug}` convention
- [ ] References to PRD are valid
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs within document

### Versioning Requirements

- [ ] When editing existing DESIGN: increment version in frontmatter
- [ ] When changing type/component definition: add `-v{N}` suffix to ID or increment existing version
- [ ] Format: `fdd-{project}-type-{slug}-v2`, `fdd-{project}-comp-{slug}-v3`, etc.
- [ ] Keep changelog of significant changes

### Semantic Requirements

**Reference**: `checklist.md` for detailed semantic criteria

- [ ] Architecture overview is complete and clear
- [ ] Domain model defines all core types
- [ ] Components have clear responsibilities and boundaries
- [ ] Integration points documented
- [ ] ADR references provided for key decisions
- [ ] PRD capabilities traced to components

### Upstream Traceability

- [ ] When component fully implemented → mark component `[x]` in DESIGN
- [ ] When all components for ADR implemented → update ADR status (PROPOSED → ACCEPTED)
- [ ] When all design elements for PRD capability implemented → mark capability `[x]` in PRD

---

## Tasks

Agent executes tasks during generation:

### Phase 1: Setup

- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read parent PRD for context

### Phase 2: Content Creation

**Apply checklist.md semantics during creation:**

| Checklist Section | Generation Task |
|-------------------|-----------------|
| ARCH-DESIGN-001: Architecture Overview | Document system purpose, high-level architecture, context diagram |
| ARCH-DESIGN-002: Principles Coherence | Define actionable, non-contradictory principles |
| DOMAIN-DESIGN-001: Domain Model | Define types, relationships, boundaries |
| COMP-DESIGN-001: Component Design | Define responsibilities, interfaces, dependencies |

### Phase 3: IDs and References

- [ ] Generate type IDs: `fdd-{project}-type-{slug}`
- [ ] Generate component IDs (if needed)
- [ ] Link to PRD actors/capabilities
- [ ] Reference relevant ADRs
- [ ] Verify uniqueness with `fdd list-ids`

### Phase 4: Quality Check

- [ ] Self-review against `checklist.md` MUST HAVE items
- [ ] Ensure no MUST NOT HAVE violations
- [ ] Verify PRD traceability

---

## Validation

Validation workflow applies rules in two phases:

### Phase 1: Structural Validation (Deterministic)

Run `fdd validate` for:
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
| DESIGN complete | `/fdd-generate FEATURES` — create features manifest |
| Need architecture decision | `/fdd-generate ADR` — document key decision |
| PRD missing/incomplete | `/fdd-generate PRD` — create/update PRD first |
| DESIGN needs revision | Continue editing DESIGN |
