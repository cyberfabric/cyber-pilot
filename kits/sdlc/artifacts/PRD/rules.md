# PRD Rules

**Artifact**: PRD
**Kit**: sdlc

**Dependencies**:
- `template.md` — structural reference
- `checklist.md` — semantic quality criteria
- `examples/example.md` — reference implementation

## Table of Contents

1. [Prerequisites](#prerequisites)
   - [Load Dependencies](#load-dependencies)
2. [Requirements](#requirements)
   - [Structural](#structural)
   - [Versioning](#versioning)
   - [Semantic](#semantic)
   - [Traceability](#traceability)
   - [Constraints](#constraints)
3. [Tasks](#tasks)
   - [Phase 1: Setup](#phase-1-setup)
   - [Phase 2: Content Creation](#phase-2-content-creation)
   - [Phase 3: IDs and Structure](#phase-3-ids-and-structure)
   - [Phase 4: Quality Check](#phase-4-quality-check)
4. [Validation](#validation)
   - [Phase 1: Structural Validation (Deterministic)](#phase-1-structural-validation-deterministic)
   - [Phase 2: Semantic Validation (Checklist-based)](#phase-2-semantic-validation-checklist-based)
   - [Phase 3: Validation Report](#phase-3-validation-report)
5. [Error Handling](#error-handling)
   - [Missing Dependencies](#missing-dependencies)
   - [Missing Adapter](#missing-adapter)
   - [Escalation](#escalation)
6. [Next Steps](#next-steps)
   - [Options](#options)

---

## Prerequisites

### Load Dependencies

- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read adapter config for project ID prefix
- [ ] Load `{cypilot_path}/.core/architecture/specs/traceability.md` for ID formats
- [ ] Load `{cypilot_path}/config/kits/sdlc/constraints.toml` for kit-level constraints
- [ ] Load `{cypilot_path}/.core/architecture/specs/kit/constraints.md` for constraints specification

---

## Requirements

### Structural

- [ ] PRD follows `template.md` structure
- [ ] Artifact frontmatter (optional): use `cpt:` format for document metadata
- [ ] All required sections present and non-empty
- [ ] All IDs follow `cpt-{hierarchy-prefix}-{kind}-{slug}` convention
- [ ] All capabilities have priority markers (`p1`–`p9`)
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs within document

### Versioning

- [ ] When editing existing PRD: increment version in frontmatter
- [ ] When changing capability definition: add `-v{N}` suffix to ID or increment existing version
  - Format: `cpt-{hierarchy-prefix}-cap-{slug}-v2`, `cpt-{hierarchy-prefix}-cap-{slug}-v3`, etc.
- [ ] Keep changelog of significant changes

### Semantic

- [ ] Purpose MUST be ≤ 2 paragraphs
- [ ] Purpose MUST NOT contain implementation details
- [ ] Vision MUST explain WHY the product exists
  - VALID: "Enables developers to validate artifacts against templates" (explains purpose)
  - INVALID: "A tool for Cypilot" (doesn't explain why it matters)
- [ ] Background MUST describe current state and specific pain points
- [ ] MUST include target users and key problems solved
- [ ] All goals MUST be measurable with concrete targets
  - VALID: "Reduce validation time from 15min to <30s" (quantified with baseline)
  - INVALID: "Improve validation speed" (no baseline, no target)
- [ ] Success criteria MUST include baseline, target, and timeframe
- [ ] All actors MUST be identified with specific roles (not just "users")
  - VALID: "Framework Developer", "Project Maintainer", "CI Pipeline"
  - INVALID: "Users", "Developers" (too generic)
- [ ] Each actor MUST have defined capabilities/needs
- [ ] Actor IDs follow: `cpt-{system}-actor-{slug}`
- [ ] Non-goals MUST explicitly state what product does NOT do
- [ ] Every FR MUST use observable behavior language (MUST, MUST NOT, SHOULD)
- [ ] Every FR MUST have a unique ID: `cpt-{system}-fr-{slug}`
- [ ] Every FR MUST have a priority marker (`p1`–`p9`)
- [ ] Every FR MUST have a rationale explaining business value
- [ ] Every FR MUST reference at least one actor
- [ ] Capabilities MUST trace to business problems
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs within document
- [ ] All requirements verified via automated tests (unit, integration, e2e) targeting 90%+ code coverage unless otherwise specified
- [ ] Document verification method only for non-test approaches (analysis, inspection, demonstration)
- [ ] NFRs MUST have measurable thresholds with units and conditions
- [ ] NFR exclusions MUST have explicit reasoning
- [ ] Intentional exclusions MUST list N/A checklist categories with reasoning
- [ ] Use cases MUST cover primary user journeys
- [ ] Use cases MUST include alternative flows for error scenarios
- [ ] Use case IDs follow: `cpt-{system}-usecase-{slug}`
- [ ] Key assumptions MUST be explicitly stated
- [ ] Open questions MUST have owners and target resolution dates
- [ ] Risks and uncertainties MUST be documented with impact and mitigation

### Traceability

- [ ] Capabilities traced through: PRD → DESIGN → DECOMPOSITION → FEATURE → CODE
- [ ] When capability fully implemented (all specs IMPLEMENTED) → mark capability `[x]`
- [ ] When all capabilities `[x]` → product version complete

### Constraints

- [ ] ALWAYS open and follow `{cypilot_path}/config/kits/sdlc/constraints.toml` (kit root)
- [ ] Treat `constraints.toml` as primary validator for:
  - where IDs are defined
  - where IDs are referenced
  - which cross-artifact references are required / optional / prohibited

**References**:
- `{cypilot_path}/.core/requirements/kit-constraints.md`
- `{cypilot_path}/.core/schemas/kit-constraints.schema.json`

**Validation Checks**:
- `cypilot validate` enforces `identifiers[<kind>].references` rules (required / optional / prohibited)
- `cypilot validate` enforces headings scoping for ID definitions and references
- `cypilot validate` enforces "checked ref implies checked def" consistency

---

## Tasks

### Phase 1: Setup

- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `example.md` for reference style
- [ ] Read adapter config for project ID prefix

### Phase 2: Content Creation

- [ ] Write each section guided by blueprint prompts and examples
- [ ] Use example as reference for content depth:
  - Vision → how example explains purpose (BIZ-PRD-001)
  - Actors → how example defines actors (BIZ-PRD-002)
  - Capabilities → how example structures caps (BIZ-PRD-003)
  - Use Cases → how example documents journeys (BIZ-PRD-004)
  - NFRs + Exclusions → how example handles N/A categories (DOC-PRD-001)
  - Non-Goals & Risks → how example scopes product (BIZ-PRD-008)
  - Assumptions → how example states assumptions (BIZ-PRD-007)

### Phase 3: IDs and Structure

- [ ] Generate actor IDs: `cpt-{hierarchy-prefix}-actor-{slug}` (e.g., `cpt-myapp-actor-admin-user`)
- [ ] Generate capability IDs: `cpt-{hierarchy-prefix}-fr-{slug}` (e.g., `cpt-myapp-fr-user-management`)
- [ ] Assign priorities based on business impact
- [ ] Verify uniqueness with `cypilot list-ids`

### Phase 4: Quality Check

- [ ] Compare output quality to `examples/example.md`
- [ ] Self-review against `checklist.md` MUST HAVE items
- [ ] Ensure no MUST NOT HAVE violations

---

## Validation

### Phase 1: Structural Validation (Deterministic)

- [ ] Run `cypilot validate --artifact <path>` for:
  - Template structure compliance
  - ID format validation
  - Priority markers present
  - No placeholders
  - No duplicate IDs

### Phase 2: Semantic Validation (Checklist-based)

- [ ] Read `checklist.md` in full
- [ ] For each MUST HAVE item: check if requirement is met
  - If not met: report as violation with severity
  - If not applicable: verify explicit "N/A" with reasoning
- [ ] For each MUST NOT HAVE item: scan document for violations
- [ ] Compare content depth to `examples/example.md`
  - Flag significant quality gaps

### Phase 3: Validation Report

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

- [ ] If `template.md` cannot be loaded → STOP, cannot proceed without template
- [ ] If `checklist.md` cannot be loaded → warn user, skip semantic validation
- [ ] If `examples/example.md` cannot be loaded → warn user, continue with reduced guidance

### Missing Adapter

- [ ] If adapter config unavailable → use default project prefix `cpt-{dirname}`
- [ ] Ask user to confirm or provide custom prefix

### Escalation

- [ ] Ask user when cannot determine appropriate actor roles for the domain
- [ ] Ask user when business requirements are unclear or contradictory
- [ ] Ask user when success criteria cannot be quantified without domain knowledge
- [ ] Ask user when uncertain whether a category is truly N/A or just missing

---

## Next Steps

### Options

- [ ] PRD complete → `/cypilot-generate DESIGN` — create technical design
- [ ] Need architecture decision → `/cypilot-generate ADR` — document key decision
- [ ] PRD needs revision → continue editing PRD
- [ ] Want checklist review only → `/cypilot-analyze semantic` — semantic validation
