# PRD Rules

**Artifact**: PRD (Product Requirements Document)
**Purpose**: Rules for PRD generation and validation

**Dependencies**:
- `template.md` — required structure
- `checklist.md` — semantic quality criteria
- `examples/example.md` — reference implementation
- `{FDD}/requirements/template.md` — FDD template marker syntax specification

---

## Requirements

Agent confirms understanding of requirements:

### Structural Requirements

- [ ] PRD follows `template.md` structure
- [ ] **DO NOT copy `fdd-template:` frontmatter** — that is template metadata only
- [ ] Artifact frontmatter (optional): use `fdd:` format for document metadata
- [ ] All required sections present and non-empty
- [ ] All IDs follow `fdd-{project}-{kind}-{slug}` convention
- [ ] All capabilities have priority markers (`p1`-`p9`)
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs within document

### Versioning Requirements

- [ ] When editing existing PRD: increment version in frontmatter
- [ ] When changing capability definition: add `-v{N}` suffix to ID or increment existing version
- [ ] Format: `fdd-{project}-cap-{slug}-v2`, `fdd-{project}-cap-{slug}-v3`, etc.
- [ ] Keep changelog of significant changes

### Semantic Requirements

**Reference**: `checklist.md` for detailed criteria

- [ ] Vision is clear and explains WHY the product exists
- [ ] All actors are identified with specific roles (not just "users")
- [ ] Each actor has defined capabilities
- [ ] Capabilities trace to business problems
- [ ] Success criteria are measurable (with baselines and timeframes where applicable)
- [ ] Use cases cover primary user journeys
- [ ] Use cases include alternative flows for error scenarios
- [ ] Non-goals explicitly state what product does NOT do
- [ ] Risks and uncertainties are documented
- [ ] Key assumptions are explicitly stated
- [ ] Open questions have owners and target resolution dates
- [ ] Intentional Exclusions list N/A checklist categories with reasoning

### Downstream Traceability

- [ ] Capabilities are traced through: PRD → DESIGN → FEATURES → FEATURE → CODE
- [ ] When capability fully implemented (all features IMPLEMENTED) → mark capability `[x]`
- [ ] When all capabilities `[x]` → product version complete

---

## Tasks

Agent executes tasks during generation:

### Phase 1: Setup

- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read adapter config for project ID prefix

### Phase 2: Content Creation

**Use example as reference for content style and depth:**

| Section | Example Reference | Checklist Guidance |
|---------|-------------------|-------------------|
| Vision | How example explains purpose | BIZ-PRD-001: Vision Clarity |
| Actors | How example defines actors | BIZ-PRD-002: Stakeholder Coverage |
| Capabilities | How example structures caps | BIZ-PRD-003: Requirements Completeness |
| Use Cases | How example documents journeys | BIZ-PRD-004: Use Case Coverage |
| NFRs + Exclusions | How example handles N/A categories | DOC-PRD-001: Explicit Non-Applicability |
| Non-Goals & Risks | How example scopes product | BIZ-PRD-008: Risks & Non-Goals |
| Assumptions | How example states assumptions | BIZ-PRD-007: Assumptions & Open Questions |

### Phase 3: IDs and Structure

- [ ] Generate actor IDs: `fdd-{project}-actor-{slug}`
- [ ] Generate capability IDs: `fdd-{project}-cap-{slug}`
- [ ] Assign priorities based on business impact
- [ ] Verify uniqueness with `fdd list-ids`

### Phase 4: Quality Check

- [ ] Compare output quality to `examples/example.md`
- [ ] Self-review against `checklist.md` MUST HAVE items
- [ ] Ensure no MUST NOT HAVE violations

---

## Validation

Validation workflow applies rules in two phases:

### Phase 1: Structural Validation (Deterministic)

Run `fdd validate` for:
- [ ] Template structure compliance
- [ ] ID format validation
- [ ] Priority markers present
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
- Compare content depth to `examples/example.md`
- Flag significant quality gaps

### Validation Report

Output format:
```
PRD Validation Report
═════════════════════

Structural: PASS/FAIL
Semantic: PASS/FAIL (N issues)

Issues:
- [SEVERITY] CHECKLIST-ID: Description
```

---

## Next Steps

After PRD generation/validation, offer these options:

| Condition | Suggested Next Step |
|-----------|---------------------|
| PRD complete | `/fdd-generate DESIGN` — create technical design |
| Need architecture decision | `/fdd-generate ADR` — document key decision |
| PRD needs revision | Continue editing PRD |
