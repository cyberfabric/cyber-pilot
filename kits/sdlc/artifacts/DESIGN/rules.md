# DESIGN Rules

**Artifact**: DESIGN
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
   - [Scope](#scope)
   - [Traceability](#traceability)
   - [Constraints](#constraints)
   - [Deliberate Omissions (MUST NOT HAVE)](#deliberate-omissions-must-not-have)
   - [Technology Stack & Capacity](#technology-stack-capacity)
3. [Tasks](#tasks)
   - [Phase 1: Setup](#phase-1-setup)
   - [Phase 2: Content Creation](#phase-2-content-creation)
   - [Phase 3: IDs and References](#phase-3-ids-and-references)
   - [Phase 4: Quality Check](#phase-4-quality-check)
4. [Validation](#validation)
   - [Phase 1: Structural Validation (Deterministic)](#phase-1-structural-validation-deterministic)
   - [Phase 2: Semantic Validation (Checklist-based)](#phase-2-semantic-validation-checklist-based)
   - [Phase 3: Validation Report](#phase-3-validation-report)
   - [Phase 4: Applicability Context](#phase-4-applicability-context)
   - [Phase 5: Report Format](#phase-5-report-format)
   - [Compact Report Format (Quick Reviews)](#compact-report-format-quick-reviews)
   - [Phase 6: Reporting Commitment](#phase-6-reporting-commitment)
   - [Phase 7: PR Review Focus (Design)](#phase-7-pr-review-focus-design)
5. [Error Handling](#error-handling)
   - [Missing Prd](#missing-prd)
   - [Incomplete Prd](#incomplete-prd)
   - [Escalation](#escalation)
6. [Next Steps](#next-steps)
   - [Options](#options)

---

## Prerequisites

### Load Dependencies

- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/DESIGN/template.md` for structure
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/DESIGN/checklist.md` for semantic guidance
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/DESIGN/examples/example.md` for reference style
- [ ] Read parent PRD for context
- [ ] Load `{cypilot_path}/.core/architecture/specs/traceability.md` for ID formats
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/constraints.toml` for kit-level constraints
- [ ] Load `{cypilot_path}/.core/architecture/specs/kit/constraints.md` for constraints specification
- [ ] Load `{cypilot_path}/.core/schemas/kit-constraints.schema.json` for constraints JSON Schema

---

## Requirements

### Structural

- [ ] DESIGN follows `{cypilot_path}/.gen/kits/sdlc/artifacts/DESIGN/template.md` structure
- [ ] Artifact frontmatter (optional): use `cpt:` format for document metadata
- [ ] All required sections present and non-empty
- [ ] All IDs follow `cpt-{hierarchy-prefix}-{kind}-{slug}` convention (see artifacts.toml for hierarchy)
- [ ] References to PRD are valid
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs within document

### Versioning

- [ ] When editing existing DESIGN: increment version in frontmatter
- [ ] When changing type/component definition: add `-v{N}` suffix to ID or increment existing version
- [ ] Format: `cpt-{hierarchy-prefix}-type-{slug}-v2`, `cpt-{hierarchy-prefix}-comp-{slug}-v3`, etc.
- [ ] Keep changelog of significant changes

### Semantic

**Reference**: `{cypilot_path}/.gen/kits/sdlc/artifacts/DESIGN/checklist.md` for detailed semantic criteria

- [ ] Architecture overview is complete and clear
- [ ] Domain model defines all core types
- [ ] Components have clear responsibilities and boundaries
- [ ] Integration points documented
- [ ] ADR references provided for key decisions
- [ ] PRD capabilities traced to components

### Scope

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

### Traceability

- [ ] When component fully implemented → mark component `[x]` in DESIGN
- [ ] When all components for ADR implemented → update ADR status (PROPOSED → ACCEPTED)
- [ ] When all design elements for PRD capability implemented → mark capability `[x]` in PRD

### Constraints

- [ ] ALWAYS open and follow `{cypilot_path}/.gen/kits/sdlc/constraints.toml` (kit root)
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

### Deliberate Omissions (MUST NOT HAVE)

DESIGN documents must NOT contain the following — report as violation if found:

- **ARCH-DESIGN-NO-001**: No Spec-Level Details (CRITICAL) — DESIGN captures architecture, not feature specs
- **ARCH-DESIGN-NO-002**: No Decision Debates (HIGH) — debates belong in ADR
- **BIZ-DESIGN-NO-003**: No Product Requirements (HIGH) — requirements belong in PRD
- **BIZ-DESIGN-NO-004**: No Implementation Tasks (HIGH) — tasks belong in DECOMPOSITION
- **DATA-DESIGN-NO-001**: No Code-Level Schema Definitions (MEDIUM) — code schemas belong in implementation
- **INT-DESIGN-NO-001**: No Complete API Specifications (MEDIUM) — full API specs belong in FEATURE
- **OPS-DESIGN-NO-001**: No Infrastructure Code (MEDIUM) — infra code belongs in implementation
- **TEST-DESIGN-NO-001**: No Test Code (MEDIUM) — test code belongs in implementation
- **MAINT-DESIGN-NO-001**: No Code Snippets (HIGH) — code belongs in implementation
- **SEC-DESIGN-NO-001**: No Security Secrets (CRITICAL) — secrets must never appear in documentation

### Technology Stack & Capacity

**ARCH-DESIGN-009: Technology Stack Alignment** (MEDIUM):
- [ ] Technology choices documented (if applicable)
- [ ] Choices align with constraints
- [ ] Choices align with team capabilities
- [ ] Choices support NFRs
- [ ] Choices are maintainable long-term
- [ ] Technology risks identified

**ARCH-DESIGN-010: Capacity and Cost Budgets** (HIGH):
- [ ] Capacity planning approach documented
- [ ] Cost estimation approach documented
- [ ] Budget allocation strategy documented
- [ ] Cost optimization patterns documented

---

## Tasks

### Phase 1: Setup

- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/DESIGN/template.md` for structure
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/DESIGN/checklist.md` for semantic guidance
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/DESIGN/examples/example.md` for reference style
- [ ] Read parent PRD for context

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
   - Mark incomplete sections with `INCOMPLETE: {reason}`
3. **Document resumption point**:
   ```
   DESIGN checkpoint:
   - Completed: Architecture Overview, Domain Model
   - In progress: Component Design (3/7 components)
   - Remaining: Sequences, Data Model
   - Resume: Continue with component cpt-{hierarchy-prefix}-comp-{slug}
   ```
4. **On resume**:
   - Verify PRD unchanged since last session
   - Continue from documented checkpoint
   - Remove incomplete markers as sections are finished

### Phase 3: IDs and References

- [ ] Generate type IDs: `cpt-{hierarchy-prefix}-type-{slug}` (e.g., `cpt-myapp-type-user-entity`)
- [ ] Generate component IDs (if needed)
- [ ] Link to PRD actors/capabilities
- [ ] Reference relevant ADRs
- [ ] Verify uniqueness with `cypilot list-ids`

### Phase 4: Quality Check

- [ ] Self-review against `{cypilot_path}/.gen/kits/sdlc/artifacts/DESIGN/checklist.md` MUST HAVE items
- [ ] Ensure no MUST NOT HAVE violations
- [ ] Verify PRD traceability

---

## Validation

### Phase 1: Structural Validation (Deterministic)

- [ ] Run `cypilot validate --artifact <path>` for:
  - Template structure compliance
  - ID format validation
  - Cross-reference validity
  - No placeholders

### Phase 2: Semantic Validation (Checklist-based)

- [ ] Read `{cypilot_path}/.gen/kits/sdlc/artifacts/DESIGN/checklist.md` in full
- [ ] For each MUST HAVE item: check if requirement is met
  - If not met: report as violation with severity
  - If not applicable: verify explicit "N/A" with reasoning
- [ ] For each MUST NOT HAVE item: scan document for violations

### Phase 3: Validation Report

```
DESIGN Validation Report
══════════════════════════

Structural: PASS/FAIL
Semantic: PASS/FAIL (N issues)

Issues:
- [SEVERITY] CHECKLIST-ID: Description
```

### Phase 4: Applicability Context

Before evaluating each checklist item, the expert MUST:

1. **Understand the artifact's domain** — What kind of system/project is this DESIGN for? (e.g., web service, CLI tool, data pipeline, methodology framework)

2. **Determine applicability for each requirement** — Not all checklist items apply to all designs:
   - A CLI tool design may not need Security Architecture analysis
   - A methodology framework design may not need Performance Architecture analysis
   - A local development tool design may not need Operations Architecture analysis

3. **Require explicit handling** — For each checklist item:
   - If applicable: The document MUST address it (present and complete)
   - If not applicable: The document MUST explicitly state "Not applicable because..." with reasoning
   - If missing without explanation: Report as violation

4. **Never skip silently** — Either:
   - The requirement is met (document addresses it), OR
   - The requirement is explicitly marked not applicable (document explains why), OR
   - The requirement is violated (report it with applicability justification)

**Key principle**: The reviewer must be able to distinguish "author considered and excluded" from "author forgot"

### Phase 5: Report Format

Report **only** problems (do not list what is OK).

For each issue include:

- **Why Applicable**: Explain why this requirement applies to this specific DESIGN's context
- **Checklist Item**: `{CHECKLIST-ID}` — {Checklist item title}
- **Severity**: CRITICAL|HIGH|MEDIUM|LOW
- **Issue**: What is wrong (requirement missing or incomplete)
- **Evidence**: Quote the exact text or "No mention found"
- **Why it matters**: Impact (risk, cost, user harm, compliance)
- **Proposal**: Concrete fix with clear acceptance criteria

### Compact Report Format (Quick Reviews)

For quick reviews, use this condensed table format:

```markdown
## DESIGN Review Summary

| ID | Severity | Issue | Proposal |
|----|----------|-------|----------|
| ARCH-DESIGN-001 | HIGH | Missing context diagram | Add system context diagram to Section A |
| ARCH-DESIGN-005 | MEDIUM | No schema location | Add path to domain types in Section C.1 |

**Applicability**: {System type} — checked {N} priority domains, {M} marked N/A
```

### Phase 6: Reporting Commitment

- [ ] I reported all issues I found
- [ ] I used the exact report format defined in this checklist (no deviations)
- [ ] I included Why Applicable justification for each issue
- [ ] I included evidence and impact for each issue
- [ ] I proposed concrete fixes for each issue
- [ ] I did not hide or omit known problems
- [ ] I verified explicit handling for all major checklist categories
- [ ] I am ready to iterate on the proposals and re-review after changes

### Phase 7: PR Review Focus (Design)

When reviewing PRs that add or change design documents, additionally focus on:

- [ ] Alignment with existing architecture (see project DESIGN artifacts)
- [ ] Trade-off analysis — are alternatives considered and justified?
- [ ] API contract consistency with existing endpoints and conventions
- [ ] Security considerations — authentication, authorization, data protection
- [ ] Compliance with `{cypilot_path}/.gen/kits/sdlc/artifacts/DESIGN/template.md` structure (generated from blueprint)
- [ ] Identify antipatterns — god objects, leaky abstractions, tight coupling
- [ ] Compare proposed design with existing industry patterns in SaaS platforms
- [ ] Compare proposed design with IEEE, ISO, and other industry standards where applicable
- [ ] Critical assessment of design decisions — challenge assumptions and gaps
- [ ] Split findings by checklist category and rate each 1-10

---

## Error Handling

### Missing Prd

- [ ] If parent PRD not found:
  - Option 1: Run `/cypilot-generate PRD` first (recommended)
  - Option 2: Continue without PRD (DESIGN will lack traceability)
  - If Option 2: document "PRD pending" in DESIGN frontmatter, skip PRD reference validation

### Incomplete Prd

- [ ] If PRD exists but is outdated: review PRD before proceeding
- [ ] If PRD needs updates: `/cypilot-generate PRD UPDATE`
- [ ] If PRD is current: proceed with DESIGN

### Escalation

- [ ] Ask user when uncertain about component boundaries
- [ ] Ask user when architecture decisions require ADR but none exists
- [ ] Ask user when PRD requirements are ambiguous or contradictory

---

## Next Steps

### Options

- [ ] DESIGN complete → `/cypilot-generate DECOMPOSITION` — create specs manifest
- [ ] Need architecture decision → `/cypilot-generate ADR` — document key decision
- [ ] PRD missing/incomplete → `/cypilot-generate PRD` — create/update PRD first
- [ ] DESIGN needs revision → continue editing DESIGN
- [ ] Want checklist review only → `/cypilot-analyze semantic` — semantic validation
