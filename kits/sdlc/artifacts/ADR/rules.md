# ADR Rules

**Artifact**: ADR (Architecture Decision Record)
**Purpose**: Rules for ADR generation and validation

---

## Table of Contents

- [ADR Rules](#adr-rules)
  - [Table of Contents](#table-of-contents)
  - [Requirements](#requirements)
    - [Structural Requirements](#structural-requirements)
    - [Versioning Requirements](#versioning-requirements)
    - [Semantic Requirements](#semantic-requirements)
    - [ADR Scope Guidelines](#adr-scope-guidelines)
    - [Status Traceability](#status-traceability)
    - [Checkbox Management](#checkbox-management)
  - [Tasks](#tasks)
    - [Phase 1: Setup](#phase-1-setup)
    - [Phase 2: Content Creation](#phase-2-content-creation)
    - [Phase 3: IDs and Structure](#phase-3-ids-and-structure)
    - [Phase 4: Quality Check](#phase-4-quality-check)
  - [Validation](#validation)
    - [Phase 1: Structural Validation (Deterministic)](#phase-1-structural-validation-deterministic)
    - [Phase 2: Semantic Validation (Checklist-based)](#phase-2-semantic-validation-checklist-based)
    - [Validation Report](#validation-report)
  - [Next Steps](#next-steps)

---

**Dependencies**:
- `template.md` — required structure
- `checklist.md` — semantic quality criteria
- `examples/example.md` — reference implementation
- `{cypilot_path}/requirements/template.md` — Cypilot template marker syntax specification
- `../../constraints.json` — kit-level constraints (primary rules for ID definitions/references)
- `{cypilot_path}/requirements/kit-constraints.md` — constraints specification
- `{cypilot_path}/schemas/kit-constraints.schema.json` — constraints JSON Schema

---

## Requirements

Agent confirms understanding of requirements:

### Structural Requirements

- [ ] ADR follows `template.md` structure
- [ ] Artifact frontmatter (optional): use `cpt:` format for document metadata
- [ ] ADR has unique ID: `cpt-{hierarchy-prefix}-adr-{slug}` (e.g., `cpt-myapp-adr-use-postgresql`)
- [ ] ID has priority marker (`p1`-`p9`)
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs

### Versioning Requirements

- [ ] ADR version in filename: `NNNN-{slug}-v{N}.md`
- [ ] When PROPOSED: minor edits allowed without version change
- [ ] When ACCEPTED: **immutable** — do NOT edit decision/rationale
- [ ] To change accepted decision: create NEW ADR with SUPERSEDES reference
- [ ] Superseding ADR: `cpt-{hierarchy-prefix}-adr-{new-slug}` with status SUPERSEDED on original

### Semantic Requirements

**Reference**: `checklist.md` for detailed criteria

- [ ] Problem/context clearly stated
- [ ] At least 2-3 options considered
- [ ] Decision rationale explained
- [ ] Consequences documented (pros and cons)
- [ ] Valid status (PROPOSED, ACCEPTED, REJECTED, DEPRECATED, SUPERSEDED)

### ADR Scope Guidelines

**One ADR per decision**. Avoid bundling multiple decisions.

| Scope | Examples | Guideline |
|-------|----------|-----------|
| **Too broad** | "Use microservices and React and PostgreSQL" | Split into separate ADRs |
| **Right size** | "Use PostgreSQL for persistent storage" | Single architectural choice |
| **Too narrow** | "Use VARCHAR(255) for email field" | Implementation detail, not ADR-worthy |

**ADR-worthy decisions**:
- Technology choices (languages, frameworks, databases)
- Architectural patterns (monolith vs microservices, event-driven)
- Integration approaches (REST vs GraphQL, sync vs async)
- Security strategies (auth mechanisms, encryption approaches)
- Infrastructure decisions (cloud provider, deployment model)

**NOT ADR-worthy** (handle in code/design docs):
- Variable naming conventions
- File organization within modules
- Specific library versions (unless security-critical)
- UI component styling choices

### Status Traceability

**Valid Statuses**: PROPOSED, ACCEPTED, REJECTED, DEPRECATED, SUPERSEDED

**Status Transitions**:

| From | To | Trigger | Action |
|------|-----|---------|--------|
| PROPOSED | ACCEPTED | Decision approved | Update status, begin implementation |
| PROPOSED | REJECTED | Decision declined | Update status, document rejection reason |
| ACCEPTED | DEPRECATED | Decision no longer applies | Update status, note why |
| ACCEPTED | SUPERSEDED | Replaced by new ADR | Update status, add `superseded_by` reference |

**Status Change Procedure**:

1. **Locate ADR file**: `architecture/ADR/NNNN-{slug}.md`
2. **Update frontmatter status**: Change `status: {OLD}` → `status: {NEW}`
3. **Add status history** (if present): Append `{date}: {OLD} → {NEW} ({reason})`
4. **For SUPERSEDED**: Add `superseded_by: cpt-{hierarchy-prefix}-adr-{new-slug}`
5. **For REJECTED**: Add `rejection_reason: {brief explanation}`

**REJECTED Status**:

Use when:
- Decision was reviewed but not approved
- Alternative approach was chosen (document which)
- Requirements changed before acceptance

Keep REJECTED ADRs for historical record — do not delete.

### Constraints (`constraints.json`) — Mandatory

- [ ] ALWAYS open and follow `../../constraints.json` (kit root)
- [ ] Treat `constraints.json` as primary validator for:
  - where IDs are defined
  - where IDs are referenced
  - which cross-artifact references are required / optional / prohibited

**References**:
- `{cypilot_path}/requirements/kit-constraints.md`
- `{cypilot_path}/schemas/kit-constraints.schema.json`

**Validation Checks**:
- `cypilot validate` enforces `identifiers[<kind>].references` rules for ADR coverage in DESIGN

---

## Tasks

Agent executes tasks during generation:

### Phase 1: Setup

- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read adapter `artifacts.json` to determine ADR directory
- [ ] Determine next ADR number (ADR-NNNN)

**ADR path resolution**:
1. List existing ADRs from `artifacts` array where `kind: "ADR"`
2. For new ADR, derive default path:
   - Read system's `artifacts_dir` from `artifacts.json` (default: `architecture`)
   - Use kit's default subdirectory for ADRs: `ADR/`
   - Create at: `{artifacts_dir}/ADR/{NNNN}-{slug}.md`
3. Register new ADR in `artifacts.json` with FULL path

**ADR Number Assignment**:

1. List existing ADRs from `artifacts` array where `kind: "ADR"`
2. Extract highest number: parse `NNNN` from filenames
3. Assign next sequential: `NNNN + 1`

**If number conflict detected** (file already exists):
```
⚠ ADR number conflict: {NNNN} already exists
→ Verify existing ADRs: ls architecture/ADR/
→ Assign next available number: {NNNN + 1}
→ If duplicate content: consider updating existing ADR instead
```

**If ADR directory doesn't exist**:
```
⚠ ADR directory not found
→ Create: mkdir -p architecture/ADR
→ Start numbering at 0001
```

### Phase 2: Content Creation

**Use example as reference:**

| Section | Example Reference | Checklist Guidance |
|---------|-------------------|-------------------|
| Context | How example states problem | ADR-001: Context Clarity |
| Options | How example lists alternatives | ADR-002: Options Analysis |
| Decision | How example explains choice | ADR-003: Decision Rationale |
| Consequences | How example documents impact | ADR-004: Consequences |

### Phase 3: IDs and Structure

- [ ] Generate ID: `cpt-{hierarchy-prefix}-adr-{slug}` (e.g., `cpt-myapp-adr-use-postgresql`)
- [ ] Assign priority based on impact
- [ ] Link to DESIGN if applicable
- [ ] Verify uniqueness with `cypilot list-ids`

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

Run `cypilot validate` for:
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
| ADR ACCEPTED | `/cypilot-generate DESIGN` — incorporate decision into design |
| Related ADR needed | `/cypilot-generate ADR` — create related decision record |
| ADR supersedes another | Update original ADR status to SUPERSEDED |
| Want checklist review only | `/cypilot-analyze semantic` — semantic validation (skip deterministic) |
