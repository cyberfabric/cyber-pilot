# DECOMPOSITION Blueprint
<!-- 
  Blueprint for Decomposition Plans.
  
  This file is the single source of truth for:
  - template.md generation (from @cpt:heading + @cpt:prompt markers)
  - example.md generation (from @cpt:heading examples + @cpt:example markers)
  - rules.md generation (from @cpt:rules + @cpt:rule markers)
  - checklist.md generation (from @cpt:checklist + @cpt:check markers)
  - constraints.toml contributions (from @cpt:heading + @cpt:id markers)
  
  All text between markers is ignored by the generator — it serves as
  human-readable documentation for anyone editing this blueprint.
  
  DECOMPOSITION bridges DESIGN → FEATURE by listing features, ordering,
  dependencies, and traceability to PRD/DESIGN.
-->

## Metadata

`@cpt:blueprint`
```toml
version = 1
kit = "sdlc"
artifact = "DECOMPOSITION"
codebase = false
```
`@/cpt:blueprint`

## Skill Integration

`@cpt:skill`
```markdown
### DECOMPOSITION Commands
- `cypilot validate --artifact <DECOMPOSITION.md>` — validate DECOMPOSITION structure and IDs
- `cypilot list-ids --kind feature` — list all features
- `cypilot list-ids --kind status` — list status indicators
- `cypilot where-defined <id>` — find where a feature ID is defined
- `cypilot where-used <id>` — find where a feature ID is referenced in FEATURE artifacts
### DECOMPOSITION Workflows
- **Generate DECOMPOSITION**: create feature manifest from DESIGN with guided prompts
- **Analyze DECOMPOSITION**: validate structure (deterministic) then decomposition quality (checklist-based)
```
`@/cpt:skill`

---

## Rules Definition

### Rules Skeleton

`@cpt:rules`
```toml
[prerequisites]
sections = ["load_dependencies"]

[requirements]
sections = ["structural", "decomposition_quality", "upstream_traceability", "checkbox_management", "constraints"]

[tasks]
phases = ["setup", "content_creation", "ids_and_structure", "quality_check", "checkbox_workflow"]
[tasks.names]
ids_and_structure = "IDs and Structure"
checkbox_workflow = "Checkbox Status Workflow"

[validation]
phases = ["structural", "decomposition_quality", "validation_report", "applicability", "report_format", "domain_disposition", "reporting"]
[validation.names]
structural = "Structural Validation (Deterministic)"
decomposition_quality = "Decomposition Quality Validation (Checklist-based)"
applicability = "Applicability Context"
report_format = "Report Format"
domain_disposition = "Domain Disposition"
reporting = "Reporting"

[error_handling]
sections = ["missing_dependencies", "quality_issues", "escalation"]

[next_steps]
sections = ["options"]
```
`@/cpt:rules`

### Prerequisites

`@cpt:rule`
```toml
kind = "prerequisites"
section = "load_dependencies"
```
```markdown
- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for decomposition quality guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read DESIGN to identify elements to decompose
- [ ] Read PRD to identify requirements to cover
- [ ] Read `{cypilot_path}/config/artifacts.toml` to determine artifact paths
- [ ] Load `{cypilot_path}/config/kits/sdlc/constraints.toml` for kit-level constraints
- [ ] Load `{cypilot_path}/.core/architecture/specs/traceability.md` for ID formats
```
`@/cpt:rule`

### Requirements

#### Structural

`@cpt:rule`
```toml
kind = "requirements"
section = "structural"
```
```markdown
- [ ] DECOMPOSITION follows `template.md` structure
- [ ] All required sections present and non-empty
- [ ] Each feature has unique ID: `cpt-{hierarchy-prefix}-feature-{slug}`
- [ ] Each feature has priority marker (`p1`-`p9`)
- [ ] Each feature has valid status
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate feature IDs
```
`@/cpt:rule`

#### Decomposition Quality

`@cpt:rule`
```toml
kind = "requirements"
section = "decomposition_quality"
```
```markdown
**Reference**: `checklist.md` for detailed criteria based on IEEE 1016 and ISO 21511

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
```
`@/cpt:rule`

#### Upstream Traceability

`@cpt:rule`
```toml
kind = "requirements"
section = "upstream_traceability"
```
```markdown
- [ ] When feature status → IMPLEMENTED, mark `[x]` on feature ID
- [ ] When all features for a component IMPLEMENTED → mark component `[x]` in DESIGN
- [ ] When all features for a capability IMPLEMENTED → mark capability `[x]` in PRD
```
`@/cpt:rule`

#### Checkbox Management

`@cpt:rule`
```toml
kind = "requirements"
section = "checkbox_management"
```
```markdown
**Defined IDs (from `constraints.toml`)**:
- **Kind**: `status` — `[ ] p1 - **ID**: cpt-{hierarchy-prefix}-status-overall` — checked when ALL features checked
- **Kind**: `feature` — `[ ] p1 - **ID**: cpt-{hierarchy-prefix}-feature-{slug}` — checked when FEATURE spec complete

**References (not ID definitions)**:
- Any `cpt-...` occurrences outside an `**ID**` definition line are references
- Common reference kinds: `fr`, `nfr`, `principle`, `constraint`, `component`, `seq`, `dbtable`

**Progress / Cascade Rules**:
- [ ] A `feature` ID should not be checked until the feature entry is fully implemented
- [ ] `status-overall` should not be checked until ALL `feature` entries are checked
```
`@/cpt:rule`

#### Constraints

`@cpt:rule`
```toml
kind = "requirements"
section = "constraints"
```
```markdown
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
```
`@/cpt:rule`

### Task Phases

#### Setup

`@cpt:rule`
```toml
kind = "tasks"
section = "setup"
```
```markdown
- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for decomposition quality guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read DESIGN to identify elements to decompose
- [ ] Read PRD to identify requirements to cover
```
`@/cpt:rule`

#### Content Creation

`@cpt:rule`
```toml
kind = "tasks"
section = "content_creation"
```
```markdown
**Decomposition Strategy**:
1. Identify all components, sequences, data entities from DESIGN
2. Group related elements into features (high cohesion)
3. Minimize dependencies between features (loose coupling)
4. Verify 100% coverage (all elements assigned)
5. Verify mutual exclusivity (no overlaps)
```
`@/cpt:rule`

#### IDs & Structure

`@cpt:rule`
```toml
kind = "tasks"
section = "ids_and_structure"
```
```markdown
- [ ] Generate feature IDs: `cpt-{hierarchy-prefix}-feature-{slug}` (e.g., `cpt-myapp-feature-user-auth`)
- [ ] Assign priorities based on dependency order
- [ ] Set initial status to NOT_STARTED
- [ ] Link to DESIGN elements being implemented
- [ ] Verify uniqueness with `cypilot list-ids`
```
`@/cpt:rule`

#### Quality Check

`@cpt:rule`
```toml
kind = "tasks"
section = "quality_check"
```
```markdown
- [ ] Compare output to `examples/example.md`
- [ ] Self-review against `checklist.md` COV, EXC, ATTR, TRC, DEP sections
- [ ] Verify 100% design element coverage
- [ ] Verify no scope overlaps between features
- [ ] Verify dependency graph is valid DAG
```
`@/cpt:rule`

#### Checkbox Workflow

`@cpt:rule`
```toml
kind = "tasks"
section = "checkbox_workflow"
```
```markdown
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
```
`@/cpt:rule`

### Error Handling

#### Missing Dependencies

`@cpt:rule`
```toml
kind = "error_handling"
section = "missing_dependencies"
```
```markdown
- [ ] If DESIGN not accessible: ask user for DESIGN location
- [ ] If template not found: STOP — cannot proceed without template
```
`@/cpt:rule`

#### Quality Issues

`@cpt:rule`
```toml
kind = "error_handling"
section = "quality_issues"
```
```markdown
- [ ] Coverage gap: add design element to appropriate feature or document exclusion
- [ ] Scope overlap: assign to single feature or document sharing with reasoning
```
`@/cpt:rule`

#### Escalation

`@cpt:rule`
```toml
kind = "error_handling"
section = "escalation"
```
```markdown
- [ ] Ask user when design elements are ambiguous
- [ ] Ask user when decomposition granularity unclear
- [ ] Ask user when dependency ordering unclear
```
`@/cpt:rule`

### Validation

#### Structural

`@cpt:rule`
```toml
kind = "validation"
section = "structural"
```
```markdown
- [ ] Run `cypilot validate --artifact <path>` for:
  - Template structure compliance
  - ID format validation
  - Priority markers present
  - Valid status values
  - No placeholders
```
`@/cpt:rule`

#### Decomposition Quality

`@cpt:rule`
```toml
kind = "validation"
section = "decomposition_quality"
```
```markdown
Apply `checklist.md` systematically:
1. **COV (Coverage)**: Verify 100% design element coverage
2. **EXC (Exclusivity)**: Verify no scope overlaps
3. **ATTR (Attributes)**: Verify each feature has all required attributes
4. **TRC (Traceability)**: Verify bidirectional traceability
5. **DEP (Dependencies)**: Verify valid dependency graph
```
`@/cpt:rule`

#### Validation Report

`@cpt:rule`
```toml
kind = "validation"
section = "validation_report"
```
````markdown
```
DECOMPOSITION Validation Report
═════════════════════════════════════

Structural: PASS/FAIL
Semantic: PASS/FAIL (N issues)

Issues:
- [SEVERITY] CHECKLIST-ID: Description
```
````
`@/cpt:rule`

#### Applicability Context

`@cpt:rule`
```toml
kind = "validation"
section = "applicability"
```
```markdown
**Purpose of DECOMPOSITION artifact**: Break down the overall DESIGN into implementable work packages (features) that can be assigned, tracked, and implemented independently.

**What this checklist tests**: Quality of the decomposition itself — not the quality of requirements, design decisions, security, performance, or other concerns. Those belong in PRD and DESIGN checklists.

**Key principle**: A perfect decomposition has:
1. **100% coverage** — every design element appears in at least one feature
2. **No overlap** — no design element appears in multiple features without clear reason
3. **Complete attributes** — every feature has identification, purpose, scope, dependencies
4. **Consistent granularity** — features are at similar abstraction levels
5. **Bidirectional traceability** — can trace both ways between design and features
```
`@/cpt:rule`

#### Report Format

`@cpt:rule`
```toml
kind = "validation"
section = "report_format"
```
````markdown
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
````
`@/cpt:rule`

#### Domain Disposition

`@cpt:rule`
```toml
kind = "validation"
section = "domain_disposition"
```
```markdown
For each major checklist category, confirm:

- [ ] COV (Coverage): Addressed or violation reported
- [ ] EXC (Exclusivity): Addressed or violation reported
- [ ] ATTR (Attributes): Addressed or violation reported
- [ ] TRC (Traceability): Addressed or violation reported
- [ ] DEP (Dependencies): Addressed or violation reported
```
`@/cpt:rule`

#### Reporting

`@cpt:rule`
```toml
kind = "validation"
section = "reporting"
```
````markdown
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
````
`@/cpt:rule`

### Next Steps

`@cpt:rule`
```toml
kind = "next_steps"
section = "options"
```
```markdown
- [ ] Features defined → `/cypilot-generate FEATURE` — design first/next feature
- [ ] Feature IMPLEMENTED → update feature status in decomposition
- [ ] All features IMPLEMENTED → `/cypilot-analyze DESIGN` — validate design completion
- [ ] New feature needed → add to decomposition, then `/cypilot-generate FEATURE`
- [ ] Want checklist review only → `/cypilot-analyze semantic` — decomposition quality validation
```
`@/cpt:rule`

---

## Checklist Definition

Decomposition quality checks organized by domain.

### Checklist Skeleton

`@cpt:checklist`
```toml
[sections]
format_validation = "Format Validation"

[severity]
levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

[review]
priority = ["COV", "EXC", "ATTR", "LEV", "CFG", "TRC", "DEP", "CHK", "DOC"]

[[domain]]
abbr = "COV"
name = "COVERAGE"
header = "COVERAGE (COV)"
standards_text = """> **Standard**: [ISO 21511:2018](https://www.iso.org/standard/69702.html) §4.2 — WBS 100% Rule
>
> "The WBS must include 100% of the work defined by the scope and capture all deliverables.""""

[[domain]]
abbr = "EXC"
name = "EXCLUSIVITY"
header = "EXCLUSIVITY (EXC)"
standards_text = """> **Standard**: [ISO 21511:2018](https://www.iso.org/standard/69702.html) §4.2 — Mutual Exclusivity
>
> "Work packages should be mutually exclusive to avoid double-counting and ambiguity.""""

[[domain]]
abbr = "ATTR"
name = "ENTITY ATTRIBUTES"
header = "ENTITY ATTRIBUTES (ATTR)"
standards_text = """> **Standard**: [IEEE 1016-2009](https://standards.ieee.org/ieee/1016/4502/) §5.4.1 — Decomposition Description Attributes
>
> "Each design entity in decomposition must have: identification, type, purpose, function, subordinates.""""

[[domain]]
abbr = "LEV"
name = "DECOMPOSITION LEVELS"
header = "DECOMPOSITION LEVELS (LEV)"
standards_text = """> **Standard**: [ISO 21511:2018](https://www.iso.org/standard/69702.html) §5.2 — Levels of Decomposition"""

[[domain]]
abbr = "CFG"
name = "CONFIGURATION ITEMS"
header = "CONFIGURATION ITEMS (CFG)"
standards_text = """> **Standard**: [ISO 10007:2017](https://www.iso.org/standard/70400.html) §6.2 — Configuration Identification
>
> "Configuration items should be selected using established criteria. Their inter-relationships describe the product structure.""""

[[domain]]
abbr = "TRC"
name = "TRACEABILITY"
header = "TRACEABILITY (TRC)"
standards_text = """> **Standards**: [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) §6.5, [ISO/IEC/IEEE 42010:2022](https://www.iso.org/standard/74393.html) §5.6"""

[[domain]]
abbr = "DEP"
name = "DEPENDENCIES"
header = "DEPENDENCIES (DEP)"
standards_text = """> **Standard**: [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) §4.2.7.2 — Modularity (loose coupling)"""

[[domain]]
abbr = "CHK"
name = "CHECKBOX CONSISTENCY"
header = "CHECKBOX CONSISTENCY (CHK)"
standards = []

[[domain]]
abbr = "DOC"
name = "DELIBERATE OMISSIONS"
header = "DELIBERATE OMISSIONS (DOC)"
standards = []

```
````markdown
# DECOMPOSITION Expert Checklist

**Artifact**: Design Decomposition (DECOMPOSITION)
**Version**: 2.0
**Last Updated**: 2025-02-03
**Purpose**: Validate quality of design decomposition into implementable work packages

---

## Referenced Standards

This checklist validates decomposition quality based on the following international standards:

| Standard | Domain | Description |
|----------|--------|-------------|
| [IEEE 1016-2009](https://standards.ieee.org/ieee/1016/4502/) | **Design Decomposition** | Software Design Descriptions — Decomposition Description viewpoint (§5.4) |
| [ISO 21511:2018](https://www.iso.org/standard/69702.html) | **Work Breakdown Structure** | WBS for project/programme management — scope decomposition, 100% rule |
| [ISO 10007:2017](https://www.iso.org/standard/70400.html) | **Configuration Management** | Configuration items, product structure, baselines |
| [ISO/IEC/IEEE 42010:2022](https://www.iso.org/standard/74393.html) | **Architecture Description** | Architecture viewpoints, model correspondences, consistency |
| [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) | **Requirements Traceability** | Bidirectional traceability, verification |
---

## Prerequisites

Before starting the review, confirm:

- [ ] I understand this checklist validates DECOMPOSITION artifacts (design breakdown into features)
- [ ] I have access to the source DESIGN artifact being decomposed
- [ ] I will check ALL items in MUST HAVE sections
- [ ] I will verify ALL items in MUST NOT HAVE sections
- [ ] I will document any violations found
- [ ] I will use the [Reporting](#reporting) format for output

---

## Applicability Context

**Purpose of DECOMPOSITION artifact**: Break down the overall DESIGN into implementable work packages (features) that can be assigned, tracked, and implemented independently.

**What this checklist tests**: Quality of the decomposition itself — not the quality of requirements, design decisions, security, performance, or other concerns. Those belong in PRD and DESIGN checklists.

**Key principle**: A perfect decomposition has:
1. **100% coverage** — every design element appears in at least one feature
2. **No overlap** — no design element appears in multiple features without clear reason
3. **Complete attributes** — every feature has identification, purpose, scope, dependencies
4. **Consistent granularity** — features are at similar abstraction levels
5. **Bidirectional traceability** — can trace both ways between design and features

---

## Severity Dictionary

- **CRITICAL**: Decomposition is fundamentally broken; cannot proceed to implementation.
- **HIGH**: Significant decomposition gap; should be fixed before implementation starts.
- **MEDIUM**: Decomposition improvement needed; fix when feasible.
- **LOW**: Minor improvement; optional.

---

## Checkpointing (Long Reviews)

### Checkpoint After Each Domain

After completing each expertise domain (COV, EXC, ATTR, etc.), output:
```
✓ {DOMAIN} complete: {N} items checked, {M} issues found
Issues: {list issue IDs}
Remaining: {list unchecked domains}
```

### Minimum Viable Review

If full review impossible, prioritize in this order:
1. **COV-001** (CRITICAL) — WBS 100% Rule
2. **EXC-001** (CRITICAL) — Mutual Exclusivity
3. **ATTR-001** (HIGH) — Entity Identification
4. **TRC-001** (HIGH) — Forward Traceability
5. **DOC-001** (CRITICAL) — Deliberate Omissions

Mark review as "PARTIAL" if not all domains completed.
````
`@/cpt:checklist`

`@cpt:check`
```toml
id = "COV-001"
domain = "COV"
title = "Design Element Coverage (100% Rule)"
severity = "CRITICAL"
ref = "ISO 21511:2018 §4.2 (WBS 100% rule)"
kind = "must_have"
```
```markdown
- [ ] ALL components from DESIGN are assigned to at least one feature
- [ ] ALL sequences/flows from DESIGN are assigned to at least one feature
- [ ] ALL data entities from DESIGN are assigned to at least one feature
- [ ] ALL design principles from DESIGN are assigned to at least one feature
- [ ] ALL design constraints from DESIGN are assigned to at least one feature
- [ ] No orphaned design elements (elements not in any feature)

**Verification method**: Cross-reference DESIGN IDs with DECOMPOSITION references.
```
`@/cpt:check`

`@cpt:check`
```toml
id = "COV-002"
domain = "COV"
title = "Requirements Coverage Passthrough"
severity = "HIGH"
ref = "ISO/IEC/IEEE 29148:2018 §6.5 (Traceability)"
kind = "must_have"
```
```markdown
- [ ] ALL functional requirements (FR) from PRD are covered by at least one feature
- [ ] ALL non-functional requirements (NFR) from PRD are covered by at least one feature
- [ ] No orphaned requirements (requirements not in any feature)

**Note**: This verifies that the decomposition covers requirements transitively through DESIGN.
```
`@/cpt:check`

`@cpt:check`
```toml
id = "COV-003"
domain = "COV"
title = "Coverage Mapping Completeness"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Each feature explicitly lists "Requirements Covered" with IDs
- [ ] Each feature explicitly lists "Design Components" with IDs
- [ ] Each feature explicitly lists "Sequences" with IDs (or "None")
- [ ] Each feature explicitly lists "Data" with IDs (or "None")
- [ ] No implicit or assumed coverage
```
`@/cpt:check`

`@cpt:check`
```toml
id = "EXC-001"
domain = "EXC"
title = "Scope Non-Overlap"
severity = "CRITICAL"
ref = "ISO 21511:2018 §4.2 (Mutual exclusivity)"
kind = "must_have"
```
```markdown
- [ ] Features do not overlap in scope (each deliverable assigned to exactly one feature)
- [ ] No duplicate coverage of the same design element by multiple features without explicit reason
- [ ] Responsibility for each deliverable is unambiguous
- [ ] No "shared" scope that could cause confusion about ownership

**Verification method**: Check if any design element ID appears in multiple features' references.
```
`@/cpt:check`

`@cpt:check`
```toml
id = "EXC-002"
domain = "EXC"
title = "Boundary Clarity"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Each feature has clear "Scope" boundaries (what's in)
- [ ] Each feature has clear "Out of Scope" boundaries (what's explicitly excluded)
- [ ] Boundaries between adjacent features are explicit and non-ambiguous
- [ ] Domain entities are assigned to single feature (or clear reason for sharing)
```
`@/cpt:check`

`@cpt:check`
```toml
id = "EXC-003"
domain = "EXC"
title = "Dependency vs Overlap Distinction"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] Dependencies (one feature uses output of another) are clearly distinct from overlaps
- [ ] Shared components are documented as dependencies, not duplicate scope
- [ ] Integration points are explicit
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ATTR-001"
domain = "ATTR"
title = "Entity Identification"
severity = "HIGH"
ref = "IEEE 1016-2009 §5.4.1 (identification attribute)"
kind = "must_have"
```
```markdown
- [ ] Each feature has unique **ID** following naming convention (`cpt-{system}-feature-{slug}`)
- [ ] IDs are stable (won't change during implementation)
- [ ] IDs are human-readable and meaningful
- [ ] No duplicate IDs within the decomposition
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ATTR-002"
domain = "ATTR"
title = "Entity Type"
severity = "MEDIUM"
ref = "IEEE 1016-2009 §5.4.1 (type attribute)"
kind = "must_have"
```
```markdown
- [ ] Each feature has **type** classification implied by priority/status (or explicit type field)
- [ ] Type indicates nature: core, supporting, infrastructure, integration, etc.
- [ ] Types are consistent across similar features
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ATTR-003"
domain = "ATTR"
title = "Entity Purpose"
severity = "HIGH"
ref = "IEEE 1016-2009 §5.4.1 (purpose attribute)"
kind = "must_have"
```
```markdown
- [ ] Each feature has clear one-line **Purpose** statement
- [ ] Purpose explains WHY this feature exists
- [ ] Purpose is distinct from other features' purposes
- [ ] Purpose is implementation-agnostic (describes intent, not approach)
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ATTR-004"
domain = "ATTR"
title = "Entity Function (Scope)"
severity = "HIGH"
ref = "IEEE 1016-2009 §5.4.1 (function attribute)"
kind = "must_have"
```
```markdown
- [ ] Each feature has concrete **Scope** bullets describing WHAT it does
- [ ] Scope items are actionable and verifiable
- [ ] Scope aligns with Purpose
- [ ] Scope is at appropriate abstraction level (not too detailed, not too vague)
```
`@/cpt:check`

`@cpt:check`
```toml
id = "ATTR-005"
domain = "ATTR"
title = "Entity Subordinates"
severity = "MEDIUM"
ref = "IEEE 1016-2009 §5.4.1 (subordinates attribute)"
kind = "must_have"
```
```markdown
- [ ] Each feature documents phases/milestones (subordinate decomposition)
- [ ] Or explicitly states "single phase" / no sub-decomposition needed
- [ ] Subordinates represent meaningful implementation milestones
- [ ] Subordinate relationships are hierarchically valid
```
`@/cpt:check`

`@cpt:check`
```toml
id = "LEV-001"
domain = "LEV"
title = "Granularity Consistency"
severity = "MEDIUM"
ref = "ISO 21511:2018 §5.2 (decomposition levels)"
kind = "must_have"
```
```markdown
- [ ] All features are at similar abstraction level (consistent granularity)
- [ ] No feature is significantly larger than others (≤3x size difference)
- [ ] No feature is significantly smaller than others (≥1/3x size difference)
- [ ] Size is measured by scope items or estimated effort
```
`@/cpt:check`

`@cpt:check`
```toml
id = "LEV-002"
domain = "LEV"
title = "Decomposition Depth"
severity = "MEDIUM"
ref = "IEEE 1016-2009 §5.4.2 (decomposition hierarchy)"
kind = "must_have"
```
```markdown
- [ ] Features are decomposed to implementable units (not too coarse)
- [ ] Features are not over-decomposed (not too granular for this artifact level)
- [ ] Hierarchy is clear: DESIGN → DECOMPOSITION → FEATURE
```
`@/cpt:check`

`@cpt:check`
```toml
id = "LEV-003"
domain = "LEV"
title = "Phase Balance"
severity = "LOW"
kind = "must_have"
```
```markdown
- [ ] Phase/milestone counts are roughly balanced across features
- [ ] No feature has disproportionately many phases (>5x average)
- [ ] No feature has zero phases without explicit reason
```
`@/cpt:check`

`@cpt:check`
```toml
id = "CFG-001"
domain = "CFG"
title = "Configuration Item Boundaries"
severity = "MEDIUM"
ref = "ISO 10007:2017 §6.2 (CI selection)"
kind = "must_have"
```
```markdown
- [ ] Each feature represents a logical configuration item (CI)
- [ ] Feature boundaries align with natural configuration/release boundaries
- [ ] Features can be versioned and baselined independently (where applicable)
```
`@/cpt:check`

`@cpt:check`
```toml
id = "CFG-002"
domain = "CFG"
title = "Change Control Readiness"
severity = "LOW"
ref = "ISO 10007:2017 §6.3 (change control)"
kind = "must_have"
```
```markdown
- [ ] Feature status enables configuration status accounting
- [ ] Changes to features are trackable (ID versioning pattern documented)
- [ ] Feature structure supports incremental delivery
```
`@/cpt:check`

`@cpt:check`
```toml
id = "TRC-001"
domain = "TRC"
title = "Forward Traceability (Design → Features)"
severity = "HIGH"
ref = "ISO/IEC/IEEE 29148:2018 §6.5.2 (forward traceability)"
kind = "must_have"
```
```markdown
- [ ] Each design element can be traced to implementing feature(s)
- [ ] Traceability links use valid design IDs
- [ ] Coverage is explicit (listed in References sections)
```
`@/cpt:check`

`@cpt:check`
```toml
id = "TRC-002"
domain = "TRC"
title = "Backward Traceability (Features → Design)"
severity = "HIGH"
ref = "ISO/IEC/IEEE 29148:2018 §6.5.2 (backward traceability)"
kind = "must_have"
```
```markdown
- [ ] Each feature traces back to source design elements
- [ ] References to design IDs are valid and resolvable
- [ ] No feature exists without design justification
```
`@/cpt:check`

`@cpt:check`
```toml
id = "TRC-003"
domain = "TRC"
title = "Cross-Artifact Consistency"
severity = "HIGH"
ref = "ISO/IEC/IEEE 42010:2022 §5.6 (architecture description consistency)"
kind = "must_have"
```
```markdown
- [ ] Feature IDs and slugs will match FEATURE artifacts
- [ ] References between DECOMPOSITION and FEATURE artifacts are planned
- [ ] Any missing feature design is documented as intentional
```
`@/cpt:check`

`@cpt:check`
```toml
id = "TRC-004"
domain = "TRC"
title = "Impact Analysis Readiness"
severity = "MEDIUM"
ref = "ISO/IEC/IEEE 42010:2022 §5.6 (consistency checking)"
kind = "must_have"
```
```markdown
- [ ] Dependency graph supports impact analysis (what is affected if X changes)
- [ ] Cross-references support reverse lookup (what depends on X)
- [ ] Changes to design can be traced to affected features
```
`@/cpt:check`

`@cpt:check`
```toml
id = "DEP-001"
domain = "DEP"
title = "Dependency Graph Quality"
severity = "CRITICAL"
ref = "ISO/IEC 25010:2023 §4.2.7.2 (Modularity — loose coupling)"
kind = "must_have"
```
```markdown
- [ ] All dependencies are explicit (Depends On field)
- [ ] No circular dependencies
- [ ] Dependencies form a valid DAG (Directed Acyclic Graph)
- [ ] Foundation features have no dependencies
- [ ] Dependency links reference existing features
```
`@/cpt:check`

`@cpt:check`
```toml
id = "DEP-002"
domain = "DEP"
title = "Dependency Minimization"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Features have minimal dependencies (loose coupling)
- [ ] Features can be implemented independently (given dependencies)
- [ ] Features support parallel development where possible
```
`@/cpt:check`

`@cpt:check`
```toml
id = "DEP-003"
domain = "DEP"
title = "Implementation Order"
severity = "MEDIUM"
kind = "must_have"
```
```markdown
- [ ] Dependencies reflect valid implementation order
- [ ] Foundation/infrastructure features listed first
- [ ] Feature ordering supports incremental delivery
```
`@/cpt:check`

`@cpt:check`
```toml
id = "CHK-001"
domain = "CHK"
title = "Status Integrity"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] Overall status tasks is `[x]` only when ALL `cpt-{system}-*` blocks are `[x]`
- [ ] `cpt-{system}-*` is `[x]` only when ALL nested `cpt-{system}-*` blocks within that feature are `[x]`
- [ ] Priority markers (`p1`-`p9`) are consistent between definitions and references
- [ ] Status emoji matches checkbox state (⏳ for in-progress, ✅ for done)
```
`@/cpt:check`

`@cpt:check`
```toml
id = "CHK-002"
domain = "CHK"
title = "Reference Validity"
severity = "HIGH"
kind = "must_have"
```
```markdown
- [ ] All `cpt-{system}-*` references resolve to valid definitions in source artifacts (DESIGN, PRD)
- [ ] No orphaned checked references (reference checked but definition unchecked)
- [ ] No duplicate checkboxes for the same ID within a feature block
```
`@/cpt:check`

`@cpt:check`
```toml
id = "DOC-001"
domain = "DOC"
title = "Explicit Non-Applicability"
severity = "CRITICAL"
kind = "must_have"
```
```markdown
- [ ] If a design element is intentionally NOT covered, it is explicitly stated with reasoning
- [ ] If features intentionally overlap, the reason is documented
- [ ] No silent omissions — reviewer can distinguish "considered and excluded" from "forgot"
```
`@/cpt:check`

`@cpt:check`
```toml
id = "DECOMP-NO-001"
domain = "DECOMP"
title = "No Implementation Details"
severity = "CRITICAL"
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No code snippets or algorithms
- [ ] No detailed technical specifications (belongs in FEATURE artifact)
- [ ] No user flows or state machines (belongs in FEATURE artifact)
- [ ] No API request/response schemas (belongs in FEATURE artifact)

**Where it belongs**: FEATURE (feature design) artifact
```
`@/cpt:check`

`@cpt:check`
```toml
id = "DECOMP-NO-002"
domain = "DECOMP"
title = "No Requirements Definitions"
severity = "HIGH"
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No functional requirement definitions (FR-xxx) — should reference PRD
- [ ] No non-functional requirement definitions (NFR-xxx) — should reference PRD
- [ ] No use case definitions — should reference PRD
- [ ] No actor definitions — should reference PRD

**Where it belongs**: PRD artifact
```
`@/cpt:check`

`@cpt:check`
```toml
id = "DECOMP-NO-003"
domain = "DECOMP"
title = "No Architecture Decisions"
severity = "HIGH"
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No "why we chose X" explanations (should reference ADR)
- [ ] No technology selection rationales (should reference ADR)
- [ ] No pros/cons analysis (should reference ADR)

**Where it belongs**: ADR artifact
```
`@/cpt:check`

`@cpt:check`
```toml
id = "FMT-001"
domain = "FMT"
title = "Feature Entry Format"
severity = "HIGH"
kind = "format_validation"
```
```markdown
- [ ] Each feature entry has unique title
- [ ] Each feature entry has stable identifier
- [ ] Entries are consistently formatted
```
`@/cpt:check`

`@cpt:check`
```toml
id = "FMT-002"
domain = "FMT"
title = "Required Fields Present"
severity = "HIGH"
kind = "format_validation"
```
```markdown
- [ ] **ID**: Present and follows convention
- [ ] **Purpose**: One-line description
- [ ] **Depends On**: None or feature references
- [ ] **Scope**: Bulleted list
- [ ] **Out of Scope**: Bulleted list (or explicit "None")
- [ ] **Requirements Covered**: ID references
- [ ] **Design Components**: ID references
```
`@/cpt:check`

`@cpt:check`
```toml
id = "FMT-003"
domain = "FMT"
title = "Checkbox Syntax"
severity = "CRITICAL"
kind = "format_validation"
```
```markdown
- [ ] All checkboxes use correct syntax: `[ ]` (unchecked) or `[x]` (checked)
- [ ] Checkbox followed by backtick-enclosed priority: `[ ] \`p1\``
- [ ] Priority followed by dash and backtick-enclosed ID
```
`@/cpt:check`


---

## Template Structure

Headings, prompts, IDs, and examples that define the generated `template.md`
and `example.md` files. The DECOMPOSITION template covers: overview, feature
entries with status/priority/scope/dependencies/traceability.

### Title (H1)

`@cpt:heading`
```toml
id = "decomposition-h1-title"
level = 1
required = true
numbered = false
multiple = false
template = "Decomposition: {PROJECT_NAME}"
prompt = "Project or system name"
description = "DECOMPOSITION document title (H1)."
examples = ["# Decomposition: TaskFlow"]
```
`@/cpt:heading`

### Overview

`@cpt:heading`
```toml
id = "decomposition-overview"
level = 2
required = true
numbered = true
multiple = false
pattern = "Overview"
description = "Overview of decomposition strategy."
examples = ["## 1. Overview"]
```
`@/cpt:heading`

`@cpt:prompt`
```markdown
{ Description of how the DESIGN was decomposed into features, the decomposition strategy, and any relevant decomposition rationale. }
```
`@/cpt:prompt`

`@cpt:example`
```markdown
TaskFlow design is decomposed into features organized around core task management capabilities. The decomposition follows a dependency order where foundational CRUD operations enable higher-level features like notifications and reporting.

**Decomposition Strategy**:
- Features grouped by functional cohesion (related capabilities together)
- Dependencies minimize coupling between features
- Each feature covers specific components and sequences from DESIGN
- 100% coverage of all DESIGN elements verified
```
`@/cpt:example`

### Feature Entries

`@cpt:heading`
```toml
id = "decomposition-entries"
level = 2
required = true
numbered = true
multiple = false
pattern = "Entries"
description = "List of feature entries."
examples = ["## 2. Entries"]
```
`@/cpt:heading`

`@cpt:id`
```toml
kind = "status"
name = "Overall Status"
description = "A decomposition-level status indicator used to summarize overall progress/state."
required = false
task = false
priority = false
template = "cpt-{system}-status-overall"
examples = ["cpt-cypilot-status-overall", "cpt-ex-ovwa-status-overall"]
to_code = false
headings = ["decomposition-entries"]
```
`@/cpt:id`

`@cpt:prompt`
```markdown
**Overall implementation status:**

- [ ] `p1` - **ID**: `cpt-{system}-status-overall`
```
`@/cpt:prompt`

`@cpt:heading`
```toml
id = "decomposition-entry"
level = 3
required = true
numbered = true
multiple = true
template = "[{Feature Title 1}](feature-{slug}/) - HIGH"
description = "A single feature entry."
examples = []
```
`@/cpt:heading`

`@cpt:id`
```toml
kind = "feature"
name = "Feature Entry"
description = "A DECOMPOSITION entry representing a FEATURE spec, including dependency and coverage links."
required = true
task = false
priority = false
template = "cpt-{system}-feature-{slug}"
examples = ["cpt-cypilot-feature-template-system", "cpt-cypilot-feature-adapter-system", "cpt-ex-ovwa-feature-tracker-core"]
to_code = false
headings = ["decomposition-entry"]
```
`@/cpt:id`

`@cpt:prompt`
```markdown
- [ ] `p1` - **ID**: `cpt-{system}-feature-{slug}`

- **Purpose**: {Few sentences describing what this feature accomplishes and why it matters}

- **Depends On**: None

- **Scope**:
  - {in-scope item 1}
  - {in-scope item 2}

- **Out of scope**:
  - {out-of-scope item 1}
  - {out-of-scope item 2}

- **Requirements Covered**:

  - [ ] `p1` - `cpt-{system}-fr-{slug}`
  - [ ] `p1` - `cpt-{system}-nfr-{slug}`

- **Design Principles Covered**:

  - [ ] `p1` - `cpt-{system}-principle-{slug}`

- **Design Constraints Covered**:

  - [ ] `p1` - `cpt-{system}-constraint-{slug}`

- **Domain Model Entities**:
  - {entity 1}
  - {entity 2}


- **Design Components**:

  - [ ] `p1` - `cpt-{system}-component-{slug}`



- **API**:
  - POST /api/{resource}
  - GET /api/{resource}/{id}
  - {CLI command}


- **Sequences**:

  - [ ] `p1` - `cpt-{system}-seq-{slug}`


- **Data**:

  - [ ] `p1` - `cpt-{system}-dbtable-{slug}`






### 2.2 [{Feature Title 2}](feature-{slug}/) - MEDIUM


- [ ] `p2` - **ID**: `cpt-{system}-feature-{slug}`


- **Purpose**: {Few sentences describing what this feature accomplishes and why it matters}



- **Depends On**: `cpt-{system}-feature-{slug}` (previous feature)



- **Scope**:
  - {in-scope item 1}
  - {in-scope item 2}



- **Out of scope**:
  - {out-of-scope item 1}


- **Requirements Covered**:

  - [ ] `p2` - `cpt-{system}-fr-{slug}`


- **Design Principles Covered**:

  - [ ] `p2` - `cpt-{system}-principle-{slug}`


- **Design Constraints Covered**:

  - [ ] `p2` - `cpt-{system}-constraint-{slug}`



- **Domain Model Entities**:
  - {entity}


- **Design Components**:

  - [ ] `p2` - `cpt-{system}-component-{slug}`



- **API**:
  - PUT /api/{resource}/{id}
  - DELETE /api/{resource}/{id}


- **Sequences**:

  - [ ] `p2` - `cpt-{system}-seq-{slug}`


- **Data**:

  - [ ] `p2` - `cpt-{system}-dbtable-{slug}`






### 2.3 [{Feature Title 3}](feature-{slug}/) - LOW


- [ ] `p3` - **ID**: `cpt-{system}-feature-{slug}`


- **Purpose**: {Few sentences describing what this feature accomplishes and why it matters}



- **Depends On**: `cpt-{system}-feature-{slug}`



- **Scope**:
  - {in-scope item}



- **Out of scope**:
  - {out-of-scope item}


- **Requirements Covered**:

  - [ ] `p3` - `cpt-{system}-fr-{slug}`


- **Design Principles Covered**:

  - [ ] `p3` - `cpt-{system}-principle-{slug}`


- **Design Constraints Covered**:

  - [ ] `p3` - `cpt-{system}-constraint-{slug}`



- **Domain Model Entities**:
  - {entity}


- **Design Components**:

  - [ ] `p3` - `cpt-{system}-component-{slug}`



- **API**:
  - GET /api/{resource}/stats


- **Sequences**:

  - [ ] `p3` - `cpt-{system}-seq-{slug}`


- **Data**:

  - [ ] `p3` - `cpt-{system}-dbtable-{slug}`





---
```
`@/cpt:prompt`

`@cpt:example`
```markdown
**Overall implementation status:**

- [ ] `p1` - **ID**: `cpt-ex-task-flow-status-overall`

### 2.1 [Task CRUD](feature-task-crud/) ⏳ HIGH

- [ ] `p1` - **ID**: `cpt-ex-task-flow-feature-task-crud`

- **Purpose**: Enable users to create, view, edit, and delete tasks with full lifecycle management.

- **Depends On**: None

- **Scope**:
  - Task creation with title, description, priority, due date
  - Task assignment to team members
  - Status transitions (BACKLOG → IN_PROGRESS → DONE)
  - Task deletion with soft-delete

- **Out of scope**:
  - Recurring tasks
  - Task templates

- **Requirements Covered**:

  - [ ] `p1` - `cpt-ex-task-flow-fr-task-crud`
  - [ ] `p2` - `cpt-ex-task-flow-nfr-performance-reliability`

- **Design Principles Covered**:

  - [ ] `p1` - `cpt-ex-task-flow-principle-realtime-first`
  - [ ] `p2` - `cpt-ex-task-flow-principle-simplicity-over-features`

- **Design Constraints Covered**:

  - [ ] `p1` - `cpt-ex-task-flow-constraint-supported-platforms`

- **Domain Model Entities**:
  - Task
  - User

- **Design Components**:

  - [ ] `p1` - `cpt-ex-task-flow-component-react-spa`
  - [ ] `p1` - `cpt-ex-task-flow-component-api-server`
  - [ ] `p1` - `cpt-ex-task-flow-component-postgresql`
  - [ ] `p2` - `cpt-ex-task-flow-component-redis-pubsub`

- **API**:
  - POST /api/tasks
  - GET /api/tasks
  - PUT /api/tasks/{id}
  - DELETE /api/tasks/{id}

- **Sequences**:

  - [ ] `p1` - `cpt-ex-task-flow-seq-task-creation`

- **Data**:

  - [ ] `p1` - `cpt-ex-task-flow-dbtable-tasks`

### 2.2 [Notifications](feature-notifications/) ⏳ MEDIUM

- [ ] `p2` - **ID**: `cpt-ex-task-flow-feature-notifications`

- **Purpose**: Notify users about task assignments, due dates, and status changes.

- **Depends On**: `cpt-ex-task-flow-feature-task-crud`

- **Scope**:
  - Push notifications for task assignments
  - Email alerts for overdue tasks
  - In-app notification center

- **Out of scope**:
  - SMS notifications
  - Custom notification templates

- **Requirements Covered**:

  - [ ] `p2` - `cpt-ex-task-flow-fr-notifications`

- **Design Principles Covered**:

  - [ ] `p1` - `cpt-ex-task-flow-principle-realtime-first`
  - [ ] `p2` - `cpt-ex-task-flow-principle-mobile-first`

- **Design Constraints Covered**:

  - [ ] `p1` - `cpt-ex-task-flow-constraint-supported-platforms`

- **Domain Model Entities**:
  - Task
  - User
  - Notification

- **Design Components**:

  - [ ] `p1` - `cpt-ex-task-flow-component-react-spa`
  - [ ] `p1` - `cpt-ex-task-flow-component-api-server`
  - [ ] `p2` - `cpt-ex-task-flow-component-redis-pubsub`

- **API**:
  - POST /api/notifications
  - GET /api/notifications
  - PUT /api/notifications/{id}/read

- **Sequences**:

  - [ ] `p2` - `cpt-ex-task-flow-seq-notification-delivery`

- **Data**:

  - [ ] `p2` - `cpt-ex-task-flow-dbtable-notifications`
```
`@/cpt:example`

`@cpt:heading`
```toml
id = "decomposition-feature-deps"
level = 2
required = true
numbered = true
multiple = false
pattern = "Feature Dependencies"
description = "Cross-feature dependency overview."
examples = ["## 3. Feature Dependencies"]
```
`@/cpt:heading`

`@cpt:prompt`
````markdown
```text
cpt-{system}-feature-{foundation-slug}
    ↓
    ├─→ cpt-{system}-feature-{dependent-1-slug}
    └─→ cpt-{system}-feature-{dependent-2-slug}
```

**Dependency Rationale**:

- `cpt-{system}-feature-{dependent-1-slug}` requires `cpt-{system}-feature-{foundation-slug}`: {explain why dependent-1 needs foundation}
- `cpt-{system}-feature-{dependent-2-slug}` requires `cpt-{system}-feature-{foundation-slug}`: {explain why dependent-2 needs foundation}
- `cpt-{system}-feature-{dependent-1-slug}` and `cpt-{system}-feature-{dependent-2-slug}` are independent of each other and can be developed in parallel
````
`@/cpt:prompt`

`@cpt:example`
```markdown
None.
```
`@/cpt:example`
