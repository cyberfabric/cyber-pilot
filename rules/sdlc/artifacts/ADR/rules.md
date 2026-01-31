# ADR Rules

**Artifact**: ADR (Architecture Decision Record)
**Purpose**: Rules for ADR generation and validation

**Dependencies**:
- `template.md` — required structure
- `checklist.md` — semantic quality criteria
- `examples/example.md` — reference implementation
- `{FDD}/requirements/template.md` — FDD template marker syntax specification

---

## Requirements

Agent confirms understanding of requirements:

### Structural Requirements

- [ ] ADR follows `template.md` structure
- [ ] **DO NOT copy `fdd-template:` frontmatter** — that is template metadata only
- [ ] Artifact frontmatter (optional): use `fdd:` format for document metadata
- [ ] ADR has unique ID: `fdd-{project}-adr-{slug}`
- [ ] ID has priority marker (`p1`-`p9`)
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs

### Versioning Requirements

- [ ] ADR version in filename: `NNNN-{slug}-v{N}.md`
- [ ] When PROPOSED: minor edits allowed without version change
- [ ] When ACCEPTED: **immutable** — do NOT edit decision/rationale
- [ ] To change accepted decision: create NEW ADR with SUPERSEDES reference
- [ ] Superseding ADR: `fdd-{project}-adr-{slug}-v2` with status SUPERSEDED on original

### Semantic Requirements

**Reference**: `checklist.md` for detailed criteria

- [ ] Problem/context clearly stated
- [ ] At least 2-3 options considered
- [ ] Decision rationale explained
- [ ] Consequences documented (pros and cons)
- [ ] Valid status (PROPOSED, ACCEPTED, DEPRECATED, SUPERSEDED)

### Status Traceability

- [ ] PROPOSED → ACCEPTED: when decision approved and implementation started
- [ ] When all components referencing ADR implemented → ADR is validated in practice
- [ ] DEPRECATED: when decision no longer applies
- [ ] SUPERSEDED: when replaced by new ADR (must reference superseding ADR)

---

## Tasks

Agent executes tasks during generation:

### Phase 1: Setup

- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Determine next ADR number (ADR-NNNN)

### Phase 2: Content Creation

**Use example as reference:**

| Section | Example Reference | Checklist Guidance |
|---------|-------------------|-------------------|
| Context | How example states problem | ADR-001: Context Clarity |
| Options | How example lists alternatives | ADR-002: Options Analysis |
| Decision | How example explains choice | ADR-003: Decision Rationale |
| Consequences | How example documents impact | ADR-004: Consequences |

### Phase 3: IDs and Structure

- [ ] Generate ID: `fdd-{project}-adr-{slug}`
- [ ] Assign priority based on impact
- [ ] Link to DESIGN if applicable
- [ ] Verify uniqueness with `fdd list-ids`

### Phase 4: Quality Check

- [ ] Compare to `examples/example.md`
- [ ] Self-review against `checklist.md`
- [ ] Verify rationale is complete

**ADR Immutability Rule**:
- After ACCEPTED: do not modify decision/rationale
- To change: create new ADR with SUPERSEDES reference

---

## Validation

### Phase 1: Structural Validation (Deterministic)

Run `fdd validate` for:
- [ ] Template structure compliance
- [ ] ID format validation
- [ ] No placeholders

### Phase 2: Semantic Validation (Checklist-based)

Apply `checklist.md`:
1. Verify context explains why decision needed
2. Verify options have pros/cons
3. Verify decision has clear rationale
4. Verify consequences documented

### Validation Report

```
ADR Validation Report
═════════════════════

Structural: PASS/FAIL
Semantic: PASS/FAIL (N issues)

Issues:
- [SEVERITY] CHECKLIST-ID: Description
```

---

## Next Steps

After ADR generation/validation, offer these options:

| Condition | Suggested Next Step |
|-----------|---------------------|
| ADR PROPOSED | Share for review, then update status to ACCEPTED |
| ADR ACCEPTED | `/fdd-generate DESIGN` — incorporate decision into design |
| Related ADR needed | `/fdd-generate ADR` — create related decision record |
| ADR supersedes another | Update original ADR status to SUPERSEDED |
