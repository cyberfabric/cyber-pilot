# PRD Rules

ALWAYS open and follow `{cypilot_path}/.core/requirements/identifiers.md` FIRST

**Artifact**: PRD (Product Requirements Document)
**Purpose**: Rules for PRD generation and validation

**Dependencies**:
- `template.md` — required structure
- `checklist.md` — semantic quality criteria
- `examples/example.md` — reference implementation
- `{cypilot_path}/.core/requirements/identifiers.md` — ID formats and naming
- `../../constraints.json` — kit-level constraints (primary rules for ID definitions/references)
- `{cypilot_path}/.core/requirements/kit-constraints.md` — constraints specification
- `{cypilot_path}/.core/schemas/kit-constraints.schema.json` — constraints JSON Schema

---

## Table of Contents

1. [Requirements](#requirements)
2. [Tasks](#tasks)
3. [Validation](#validation)
4. [Error Handling](#error-handling)
5. [Next Steps](#next-steps)

---

## Requirements

Agent confirms understanding of requirements:

### Structural Requirements

- [ ] PRD follows `template.md` structure
- [ ] Artifact frontmatter (optional): use `cpt:` format for document metadata
- [ ] All required sections present and non-empty
- [ ] All IDs follow `cpt-{hierarchy-prefix}-{kind}-{slug}` convention (see artifacts.toml for hierarchy)
- [ ] All capabilities have priority markers (`p1`-`p9`)
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs within document

### Versioning Requirements

- [ ] When editing existing PRD: increment version in frontmatter
- [ ] When changing capability definition: add `-v{N}` suffix to ID or increment existing version
- [ ] Format: `cpt-{hierarchy-prefix}-cap-{slug}-v2`, `cpt-{hierarchy-prefix}-cap-{slug}-v3`, etc.
- [ ] Keep changelog of significant changes

### Semantic Requirements

**Reference**: `checklist.md` for detailed criteria

- [ ] Vision is clear and explains WHY the product exists
  - ✓ "Enables developers to validate artifacts against templates" (explains purpose)
  - ✗ "A tool for Cypilot" (doesn't explain why it matters)
- [ ] All actors are identified with specific roles (not just "users")
  - ✓ "Framework Developer", "Project Maintainer", "CI Pipeline"
  - ✗ "Users", "Developers" (too generic)
- [ ] Each actor has defined capabilities
- [ ] Capabilities trace to business problems
- [ ] Success criteria are measurable with concrete targets
  - ✓ "Reduce validation time from 15min to <30s" (quantified with baseline)
  - ✗ "Improve validation speed" (no baseline, no target)
- [ ] Use cases cover primary user journeys
- [ ] Use cases include alternative flows for error scenarios
- [ ] Non-goals explicitly state what product does NOT do
- [ ] Risks and uncertainties are documented
- [ ] Key assumptions are explicitly stated
- [ ] Open questions have owners and target resolution dates
- [ ] Intentional Exclusions list N/A checklist categories with reasoning

### Downstream Traceability

- [ ] Capabilities are traced through: PRD → DESIGN → DECOMPOSITION → SPEC → CODE
- [ ] When capability fully implemented (all specs IMPLEMENTED) → mark capability `[x]`
- [ ] When all capabilities `[x]` → product version complete

### Constraints (`constraints.json`) — Mandatory

- [ ] ALWAYS open and follow `../../constraints.json` (kit root)
- [ ] Treat `constraints.json` as primary validator for:
  - where IDs are defined
  - where IDs are referenced
  - which cross-artifact references are required / optional / prohibited

**References**:
- `{cypilot_path}/.core/requirements/kit-constraints.md`
- `{cypilot_path}/.core/schemas/kit-constraints.schema.json`

**Validation Checks** (automated via `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py validate`):
- Enforces `identifiers[<kind>].references` rules (required / optional / prohibited)
- Enforces headings scoping for ID definitions and references when constraints specify `headings` (identifier-level and reference-rule-level)
- Enforces "checked ref implies checked def" consistency

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

- [ ] Generate actor IDs: `cpt-{hierarchy-prefix}-actor-{slug}` (e.g., `cpt-myapp-actor-admin-user`)
- [ ] Generate capability IDs: `cpt-{hierarchy-prefix}-cap-{slug}` (e.g., `cpt-myapp-cap-user-management`)
- [ ] Assign priorities based on business impact
- [ ] Verify uniqueness with `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py list-ids`

### Phase 4: Quality Check

- [ ] Compare output quality to `examples/example.md`
- [ ] Self-review against `checklist.md` MUST HAVE items
- [ ] Ensure no MUST NOT HAVE violations

---

## Validation

Validation workflow applies rules in two phases:

### Phase 1: Structural Validation (Deterministic)

Run `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py validate --artifact <path>` for:
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

## Error Handling

### Missing Dependencies

**If `template.md` cannot be loaded**:
```
⚠ Template not found: kits/sdlc/artifacts/PRD/template.md
→ Verify Cypilot installation is complete
→ STOP — cannot proceed without template
```

**If `checklist.md` cannot be loaded**:
```
⚠ Checklist not found: kits/sdlc/artifacts/PRD/checklist.md
→ Structural validation possible, semantic validation skipped
→ Warn user: "Semantic validation unavailable"
```

**If `examples/example.md` cannot be loaded**:
```
⚠ Example not found — continuing with reduced guidance
→ Warn user: "No reference example available for quality comparison"
```

### Missing Adapter Config

**If adapter config unavailable** (Phase 1 Setup, line 100):
```
⚠ No adapter config found
→ Use default project prefix: "cpt-{dirname}"
→ Ask user to confirm or provide custom prefix
```

### Escalation

**Ask user when**:
- Cannot determine appropriate actor roles for the domain
- Business requirements are unclear or contradictory
- Success criteria cannot be quantified without domain knowledge
- Uncertain whether a category is truly N/A or just missing

---

## Next Steps

After PRD generation/validation, offer these options:

| Condition | Suggested Next Step |
|-----------|---------------------|
| PRD complete | `/cypilot-generate DESIGN` — create technical design |
| Need architecture decision | `/cypilot-generate ADR` — document key decision |
| PRD needs revision | Continue editing PRD |
| Want checklist review only | `/cypilot-analyze semantic` — semantic validation (skip deterministic) |
