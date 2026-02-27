# DECOMPOSITION Rules

**Artifact**: DECOMPOSITION
**Kit**: sdlc

**Dependencies**:
- `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md` — structural reference
- `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md` — semantic quality criteria
- `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/examples/example.md` — reference implementation

## Table of Contents

1. [Prerequisites](#prerequisites)
   - [Load Dependencies](#load-dependencies)
2. [Requirements](#requirements)
   - [Structural](#structural)
   - [Decomposition Quality](#decomposition-quality)
   - [Upstream Traceability](#upstream-traceability)
   - [Checkbox Management](#checkbox-management)
   - [Constraints](#constraints)
3. [Tasks](#tasks)
   - [Phase 1: Setup](#phase-1-setup)
   - [Phase 2: Content Creation](#phase-2-content-creation)
   - [Phase 3: IDs and Structure](#phase-3-ids-and-structure)
   - [Phase 4: Quality Check](#phase-4-quality-check)
   - [Phase 5: Checkbox Status Workflow](#phase-5-checkbox-status-workflow)
4. [Validation](#validation)
   - [Phase 1: Structural Validation (Deterministic)](#phase-1-structural-validation-deterministic)
   - [Phase 2: Decomposition Quality Validation (Checklist-based)](#phase-2-decomposition-quality-validation-checklist-based)
   - [Phase 3: Validation Report](#phase-3-validation-report)
   - [Phase 4: Applicability Context](#phase-4-applicability-context)
   - [Phase 5: Report Format](#phase-5-report-format)
   - [Phase 6: Domain Disposition](#phase-6-domain-disposition)
   - [Phase 7: Reporting](#phase-7-reporting)
5. [Error Handling](#error-handling)
   - [Missing Dependencies](#missing-dependencies)
   - [Quality Issues](#quality-issues)
   - [Escalation](#escalation)
6. [Next Steps](#next-steps)
   - [Options](#options)

---

## Prerequisites

### Load Dependencies

- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md` for structure
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md` for decomposition quality guidance
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/examples/example.md` for reference style
- [ ] Read DESIGN to identify elements to decompose
- [ ] Read PRD to identify requirements to cover
- [ ] Read `{cypilot_path}/config/artifacts.toml` to determine artifact paths
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/constraints.toml` for kit-level constraints
- [ ] Load `{cypilot_path}/.core/architecture/specs/traceability.md` for ID formats

---

## Requirements

### Structural

- [ ] DECOMPOSITION follows `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md` structure
- [ ] All required sections present and non-empty
- [ ] Each feature has unique ID: `cpt-{hierarchy-prefix}-feature-{slug}`
- [ ] Each feature has priority marker (`p1`-`p9`)
- [ ] Each feature has valid status
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate feature IDs

### Decomposition Quality

**Reference**: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md` for detailed criteria based on IEEE 1016 and ISO 21511

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

### Checkbox Management

**Defined IDs (from `constraints.toml`)**:
- **Kind**: `status` — `[ ] p1 - **ID**: cpt-{hierarchy-prefix}-status-overall` — checked when ALL features checked
- **Kind**: `feature` — `[ ] p1 - **ID**: cpt-{hierarchy-prefix}-feature-{slug}` — checked when FEATURE spec complete

**References (not ID definitions)**:
- Any `cpt-...` occurrences outside an `**ID**` definition line are references
- Common reference kinds: `fr`, `nfr`, `principle`, `constraint`, `component`, `seq`, `dbtable`

**Progress / Cascade Rules**:
- [ ] A `feature` ID should not be checked until the feature entry is fully implemented
- [ ] `status-overall` should not be checked until ALL `feature` entries are checked

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

---

## Tasks

### Phase 1: Setup

- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md` for structure
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md` for decomposition quality guidance
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/examples/example.md` for reference style
- [ ] Read DESIGN to identify elements to decompose
- [ ] Read PRD to identify requirements to cover

### Phase 2: Content Creation

**Decomposition Strategy**:
1. Identify all components, sequences, data entities from DESIGN
2. Group related elements into features (high cohesion)
3. Minimize dependencies between features (loose coupling)
4. Verify 100% coverage (all elements assigned)
5. Verify mutual exclusivity (no overlaps)

### Phase 3: IDs and Structure

- [ ] Generate feature IDs: `cpt-{hierarchy-prefix}-feature-{slug}` (e.g., `cpt-myapp-feature-user-auth`)
- [ ] Assign priorities based on dependency order
- [ ] Set initial status to NOT_STARTED
- [ ] Link to DESIGN elements being implemented
- [ ] Verify uniqueness with `cypilot list-ids`

### Phase 4: Quality Check

- [ ] Compare output to `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/examples/example.md`
- [ ] Self-review against `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md` COV, EXC, ATTR, TRC, DEP sections
- [ ] Verify 100% design element coverage
- [ ] Verify no scope overlaps between features
- [ ] Verify dependency graph is valid DAG

### Phase 5: Checkbox Status Workflow

**Initial Creation (New Feature)**:
1. Create feature entry with `[ ]` unchecked on the feature ID
2. Add all reference blocks with `[ ]` unchecked on each referenced ID
3. Overall `status-overall` remains `[ ]` unchecked

**During Implementation (Marking Progress)**:
1. When a specific requirement is implemented: find the referenced ID entry, change `[ ]` to `[x]`
2. When a component is integrated: find the referenced component entry, change `[ ]` to `[x]`
3. Continue for all reference types as work progresses

**Feature Completion (Marking Feature Done)**:
1. Verify ALL referenced IDs within the feature entry have `[x]`
2. Run `cypilot validate` to confirm no checkbox inconsistencies
3. Change the feature ID line from `[ ]` to `[x]`
4. Update feature status emoji (e.g., ⏳ → ✅)

**Manifest Completion (Marking Overall Done)**:
1. Verify ALL feature entries have `[x]`
2. Run `cypilot validate` to confirm cascade consistency
3. Change the `status-overall` line from `[ ]` to `[x]`

---

## Validation

### Phase 1: Structural Validation (Deterministic)

- [ ] Run `cypilot validate --artifact <path>` for:
  - Template structure compliance
  - ID format validation
  - Priority markers present
  - Valid status values
  - No placeholders

### Phase 2: Decomposition Quality Validation (Checklist-based)

Apply `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md` systematically:
1. **COV (Coverage)**: Verify 100% design element coverage
2. **EXC (Exclusivity)**: Verify no scope overlaps
3. **ATTR (Attributes)**: Verify each feature has all required attributes
4. **TRC (Traceability)**: Verify bidirectional traceability
5. **DEP (Dependencies)**: Verify valid dependency graph

### Phase 3: Validation Report

```
DECOMPOSITION Validation Report
═════════════════════════════════════

Structural: PASS/FAIL
Semantic: PASS/FAIL (N issues)

Issues:
- [SEVERITY] CHECKLIST-ID: Description
```

### Phase 4: Applicability Context

**Purpose of DECOMPOSITION artifact**: Break down the overall DESIGN into implementable work packages (features) that can be assigned, tracked, and implemented independently.

**What this checklist tests**: Quality of the decomposition itself — not the quality of requirements, design decisions, security, performance, or other concerns. Those belong in PRD and DESIGN checklists.

**Key principle**: A perfect decomposition has:
1. **100% coverage** — every design element appears in at least one feature
2. **No overlap** — no design element appears in multiple features without clear reason
3. **Complete attributes** — every feature has identification, purpose, scope, dependencies
4. **Consistent granularity** — features are at similar abstraction levels
5. **Bidirectional traceability** — can trace both ways between design and features

### Phase 5: Report Format

Report **only** problems (do not list what is OK).

For each issue include:

- **Checklist Item**: `{CHECKLIST-ID}` — {Checklist item title}
- **Severity**: CRITICAL|HIGH|MEDIUM|LOW
- **Issue**: What is wrong
- **Evidence**: Quote or location in artifact
- **Why it matters**: Impact on decomposition quality
- **Proposal**: Concrete fix

```markdown
## Review Report (Issues Only)

### 1. {Short issue title}

**Checklist Item**: `{CHECKLIST-ID}` — {Checklist item title}

**Severity**: CRITICAL|HIGH|MEDIUM|LOW

#### Issue

{What is wrong}

#### Evidence

{Quote or "No mention found"}

#### Why It Matters

{Impact on decomposition quality}

#### Proposal

{Concrete fix}
```

### Phase 6: Domain Disposition

For each major checklist category, confirm:

- [ ] COV (Coverage): Addressed or violation reported
- [ ] EXC (Exclusivity): Addressed or violation reported
- [ ] ATTR (Attributes): Addressed or violation reported
- [ ] TRC (Traceability): Addressed or violation reported
- [ ] DEP (Dependencies): Addressed or violation reported

### Phase 7: Reporting

Report **only** problems (do not list what is OK).

For each issue include:

- **Issue**: What is wrong
- **Evidence**: Quote or location in artifact
- **Why it matters**: Impact on decomposition quality
- **Proposal**: Concrete fix

```markdown
## Review Report (Issues Only)

### 1. {Short issue title}

**Checklist Item**: `{CHECKLIST-ID}` — {Checklist item title}

**Severity**: CRITICAL|HIGH|MEDIUM|LOW

#### Issue

{What is wrong}

#### Evidence

{Quote or "No mention found"}

#### Why It Matters

{Impact on decomposition quality}

#### Proposal

{Concrete fix}
```

---

## Error Handling

### Missing Dependencies

- [ ] If DESIGN not accessible: ask user for DESIGN location
- [ ] If template not found: STOP — cannot proceed without template

### Quality Issues

- [ ] Coverage gap: add design element to appropriate feature or document exclusion
- [ ] Scope overlap: assign to single feature or document sharing with reasoning

### Escalation

- [ ] Ask user when design elements are ambiguous
- [ ] Ask user when decomposition granularity unclear
- [ ] Ask user when dependency ordering unclear

---

## Next Steps

### Options

- [ ] Features defined → `/cypilot-generate FEATURE` — design first/next feature
- [ ] Feature IMPLEMENTED → update feature status in decomposition
- [ ] All features IMPLEMENTED → `/cypilot-analyze DESIGN` — validate design completion
- [ ] New feature needed → add to decomposition, then `/cypilot-generate FEATURE`
- [ ] Want checklist review only → `/cypilot-analyze semantic` — decomposition quality validation
