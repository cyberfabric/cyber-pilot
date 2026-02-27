# DECOMPOSITION Blueprint
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

## Metadata

> **`@cpt:blueprint`** — Blueprint metadata: artifact kind, kit slug, version. Internal; not output to any file.

`@cpt:blueprint`
```toml
# Blueprint version (semver)
version = 1
# Kit slug this blueprint belongs to
kit = "sdlc"
# Artifact kind: PRD | ADR | DESIGN | DECOMPOSITION | FEATURE | CODE
artifact = "DECOMPOSITION"
codebase = false
```
`@/cpt:blueprint`

## Skill Integration

> **`@cpt:skill`** — Skill content. Agent-facing navigation and instructions. Output: `.gen/kits/{slug}/SKILL.md`.

`@cpt:skill`
```markdown
### DECOMPOSITION Commands
- `cypilot validate --artifact <DECOMPOSITION.md>` — validate DECOMPOSITION structure and IDs
- `cypilot list-ids --kind feature` — list all features
- `cypilot list-ids --kind status` — list status indicators
- `cypilot where-defined --id <id>` — find where a feature ID is defined
- `cypilot where-used --id <id>` — find where a feature ID is referenced in FEATURE artifacts
### DECOMPOSITION Workflows
- **Generate DECOMPOSITION**: create feature manifest from DESIGN with guided prompts
- **Analyze DECOMPOSITION**: validate structure (deterministic) then decomposition quality (checklist-based)
```
`@/cpt:skill`

---

## Rules Definition

### Rules Skeleton

> **`@cpt:rules`** — Rules skeleton. Defines section structure (prerequisites, requirements, tasks, validation, etc.) for `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rules`
```toml
# Prerequisite steps (load dependencies, read configs)
[prerequisites]
# Ordered list of section keys (each needs a matching @cpt:rule block)
sections = ["load_dependencies"]

# Requirement sections (structural, semantic, constraints, etc.)
[requirements]
# Ordered list of section keys (each needs a matching @cpt:rule block)
sections = ["structural", "decomposition_quality", "upstream_traceability", "checkbox_management", "constraints"]

# Task phases — step-by-step workflow for creating the artifact
[tasks]
# Ordered list of phase keys (each needs a matching @cpt:rule block)
phases = ["setup", "content_creation", "ids_and_structure", "quality_check", "checkbox_workflow"]
# Display names for non-obvious task phase keys
[tasks.names]
ids_and_structure = "IDs and Structure"
checkbox_workflow = "Checkbox Status Workflow"

# Validation phases — ordered checks run after artifact is written
[validation]
# Ordered list of phase keys (each needs a matching @cpt:rule block)
phases = ["structural", "decomposition_quality", "validation_report", "applicability", "report_format", "domain_disposition", "reporting"]
# Display names for non-obvious validation phase keys
[validation.names]
structural = "Structural Validation (Deterministic)"
decomposition_quality = "Decomposition Quality Validation (Checklist-based)"
applicability = "Applicability Context"
report_format = "Report Format"
domain_disposition = "Domain Disposition"
reporting = "Reporting"

# Error handling sections — what to do when things go wrong
[error_handling]
# Ordered list of section keys (each needs a matching @cpt:rule block)
sections = ["missing_dependencies", "quality_issues", "escalation"]

# Next steps — recommended actions after completing the artifact
[next_steps]
# Ordered list of section keys (each needs a matching @cpt:rule block)
sections = ["options"]
```
`@/cpt:rules`

### Prerequisites

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "prerequisites"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "load_dependencies"
```
```markdown
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md` for structure
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md` for decomposition quality guidance
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/examples/example.md` for reference style
- [ ] Read DESIGN to identify elements to decompose
- [ ] Read PRD to identify requirements to cover
- [ ] Read `{cypilot_path}/config/artifacts.toml` to determine artifact paths
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/constraints.toml` for kit-level constraints
- [ ] Load `{cypilot_path}/.core/architecture/specs/traceability.md` for ID formats
```
`@/cpt:rule`

### Requirements

#### Structural

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "structural"
```
```markdown
- [ ] DECOMPOSITION follows `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md` structure
- [ ] All required sections present and non-empty
- [ ] Each feature has unique ID: `cpt-{hierarchy-prefix}-feature-{slug}`
- [ ] Each feature has priority marker (`p1`-`p9`)
- [ ] Each feature has valid status
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate feature IDs
```
`@/cpt:rule`

#### Decomposition Quality

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "decomposition_quality"
```
```markdown
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
```
`@/cpt:rule`

#### Upstream Traceability

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "upstream_traceability"
```
```markdown
- [ ] When feature status → IMPLEMENTED, mark `[x]` on feature ID
- [ ] When all features for a component IMPLEMENTED → mark component `[x]` in DESIGN
- [ ] When all features for a capability IMPLEMENTED → mark capability `[x]` in PRD
```
`@/cpt:rule`

#### Checkbox Management

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "constraints"
```
```markdown
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
```
`@/cpt:rule`

### Task Phases

#### Setup

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "setup"
```
```markdown
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md` for structure
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md` for decomposition quality guidance
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/examples/example.md` for reference style
- [ ] Read DESIGN to identify elements to decompose
- [ ] Read PRD to identify requirements to cover
```
`@/cpt:rule`

#### Content Creation

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "quality_check"
```
```markdown
- [ ] Compare output to `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/examples/example.md`
- [ ] Self-review against `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md` COV, EXC, ATTR, TRC, DEP sections
- [ ] Verify 100% design element coverage
- [ ] Verify no scope overlaps between features
- [ ] Verify dependency graph is valid DAG
```
`@/cpt:rule`

#### Checkbox Workflow

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "error_handling"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "missing_dependencies"
```
```markdown
- [ ] If DESIGN not accessible: ask user for DESIGN location
- [ ] If template not found: STOP — cannot proceed without template
```
`@/cpt:rule`

#### Quality Issues

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "error_handling"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "quality_issues"
```
```markdown
- [ ] Coverage gap: add design element to appropriate feature or document exclusion
- [ ] Scope overlap: assign to single feature or document sharing with reasoning
```
`@/cpt:rule`

#### Escalation

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "error_handling"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "decomposition_quality"
```
```markdown
Apply `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md` systematically:
1. **COV (Coverage)**: Verify 100% design element coverage
2. **EXC (Exclusivity)**: Verify no scope overlaps
3. **ATTR (Attributes)**: Verify each feature has all required attributes
4. **TRC (Traceability)**: Verify bidirectional traceability
5. **DEP (Dependencies)**: Verify valid dependency graph
```
`@/cpt:rule`

#### Validation Report

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "next_steps"
# Section name — must match a section defined in the @cpt:rules skeleton
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

> **`@cpt:checklist`** — Checklist preamble. Static markdown placed at the top of `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md` (standards, prerequisites, severity dictionary).

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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "COV-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "COV"
# Human-readable check title
title = "Design Element Coverage (100% Rule)"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO 21511:2018 §4.2 (WBS 100% rule)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "COV-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "COV"
# Human-readable check title
title = "Requirements Coverage Passthrough"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC/IEEE 29148:2018 §6.5 (Traceability)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] ALL functional requirements (FR) from PRD are covered by at least one feature
- [ ] ALL non-functional requirements (NFR) from PRD are covered by at least one feature
- [ ] No orphaned requirements (requirements not in any feature)

**Note**: This verifies that the decomposition covers requirements transitively through DESIGN.
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "COV-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "COV"
# Human-readable check title
title = "Coverage Mapping Completeness"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "EXC-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "EXC"
# Human-readable check title
title = "Scope Non-Overlap"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO 21511:2018 §4.2 (Mutual exclusivity)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "EXC-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "EXC"
# Human-readable check title
title = "Boundary Clarity"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Each feature has clear "Scope" boundaries (what's in)
- [ ] Each feature has clear "Out of Scope" boundaries (what's explicitly excluded)
- [ ] Boundaries between adjacent features are explicit and non-ambiguous
- [ ] Domain entities are assigned to single feature (or clear reason for sharing)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "EXC-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "EXC"
# Human-readable check title
title = "Dependency vs Overlap Distinction"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Dependencies (one feature uses output of another) are clearly distinct from overlaps
- [ ] Shared components are documented as dependencies, not duplicate scope
- [ ] Integration points are explicit
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ATTR-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ATTR"
# Human-readable check title
title = "Entity Identification"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "IEEE 1016-2009 §5.4.1 (identification attribute)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Each feature has unique **ID** following naming convention (`cpt-{system}-feature-{slug}`)
- [ ] IDs are stable (won't change during implementation)
- [ ] IDs are human-readable and meaningful
- [ ] No duplicate IDs within the decomposition
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ATTR-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ATTR"
# Human-readable check title
title = "Entity Type"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "IEEE 1016-2009 §5.4.1 (type attribute)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Each feature has **type** classification implied by priority/status (or explicit type field)
- [ ] Type indicates nature: core, supporting, infrastructure, integration, etc.
- [ ] Types are consistent across similar features
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ATTR-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ATTR"
# Human-readable check title
title = "Entity Purpose"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "IEEE 1016-2009 §5.4.1 (purpose attribute)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Each feature has clear one-line **Purpose** statement
- [ ] Purpose explains WHY this feature exists
- [ ] Purpose is distinct from other features' purposes
- [ ] Purpose is implementation-agnostic (describes intent, not approach)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ATTR-004"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ATTR"
# Human-readable check title
title = "Entity Function (Scope)"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "IEEE 1016-2009 §5.4.1 (function attribute)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Each feature has concrete **Scope** bullets describing WHAT it does
- [ ] Scope items are actionable and verifiable
- [ ] Scope aligns with Purpose
- [ ] Scope is at appropriate abstraction level (not too detailed, not too vague)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ATTR-005"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ATTR"
# Human-readable check title
title = "Entity Subordinates"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "IEEE 1016-2009 §5.4.1 (subordinates attribute)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Each feature documents phases/milestones (subordinate decomposition)
- [ ] Or explicitly states "single phase" / no sub-decomposition needed
- [ ] Subordinates represent meaningful implementation milestones
- [ ] Subordinate relationships are hierarchically valid
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "LEV-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "LEV"
# Human-readable check title
title = "Granularity Consistency"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO 21511:2018 §5.2 (decomposition levels)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] All features are at similar abstraction level (consistent granularity)
- [ ] No feature is significantly larger than others (≤3x size difference)
- [ ] No feature is significantly smaller than others (≥1/3x size difference)
- [ ] Size is measured by scope items or estimated effort
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "LEV-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "LEV"
# Human-readable check title
title = "Decomposition Depth"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "IEEE 1016-2009 §5.4.2 (decomposition hierarchy)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Features are decomposed to implementable units (not too coarse)
- [ ] Features are not over-decomposed (not too granular for this artifact level)
- [ ] Hierarchy is clear: DESIGN → DECOMPOSITION → FEATURE
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "LEV-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "LEV"
# Human-readable check title
title = "Phase Balance"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "LOW"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Phase/milestone counts are roughly balanced across features
- [ ] No feature has disproportionately many phases (>5x average)
- [ ] No feature has zero phases without explicit reason
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "CFG-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "CFG"
# Human-readable check title
title = "Configuration Item Boundaries"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO 10007:2017 §6.2 (CI selection)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Each feature represents a logical configuration item (CI)
- [ ] Feature boundaries align with natural configuration/release boundaries
- [ ] Features can be versioned and baselined independently (where applicable)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "CFG-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "CFG"
# Human-readable check title
title = "Change Control Readiness"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "LOW"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO 10007:2017 §6.3 (change control)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Feature status enables configuration status accounting
- [ ] Changes to features are trackable (ID versioning pattern documented)
- [ ] Feature structure supports incremental delivery
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "TRC-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "TRC"
# Human-readable check title
title = "Forward Traceability (Design → Features)"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC/IEEE 29148:2018 §6.5.2 (forward traceability)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Each design element can be traced to implementing feature(s)
- [ ] Traceability links use valid design IDs
- [ ] Coverage is explicit (listed in References sections)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "TRC-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "TRC"
# Human-readable check title
title = "Backward Traceability (Features → Design)"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC/IEEE 29148:2018 §6.5.2 (backward traceability)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Each feature traces back to source design elements
- [ ] References to design IDs are valid and resolvable
- [ ] No feature exists without design justification
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "TRC-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "TRC"
# Human-readable check title
title = "Cross-Artifact Consistency"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC/IEEE 42010:2022 §5.6 (architecture description consistency)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Feature IDs and slugs will match FEATURE artifacts
- [ ] References between DECOMPOSITION and FEATURE artifacts are planned
- [ ] Any missing feature design is documented as intentional
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "TRC-004"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "TRC"
# Human-readable check title
title = "Impact Analysis Readiness"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC/IEEE 42010:2022 §5.6 (consistency checking)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Dependency graph supports impact analysis (what is affected if X changes)
- [ ] Cross-references support reverse lookup (what depends on X)
- [ ] Changes to design can be traced to affected features
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "DEP-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "DEP"
# Human-readable check title
title = "Dependency Graph Quality"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2023 §4.2.7.2 (Modularity — loose coupling)"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "DEP-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "DEP"
# Human-readable check title
title = "Dependency Minimization"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Features have minimal dependencies (loose coupling)
- [ ] Features can be implemented independently (given dependencies)
- [ ] Features support parallel development where possible
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "DEP-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "DEP"
# Human-readable check title
title = "Implementation Order"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Dependencies reflect valid implementation order
- [ ] Foundation/infrastructure features listed first
- [ ] Feature ordering supports incremental delivery
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "CHK-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "CHK"
# Human-readable check title
title = "Status Integrity"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Overall status tasks is `[x]` only when ALL `cpt-{system}-*` blocks are `[x]`
- [ ] `cpt-{system}-*` is `[x]` only when ALL nested `cpt-{system}-*` blocks within that feature are `[x]`
- [ ] Priority markers (`p1`-`p9`) are consistent between definitions and references
- [ ] Status emoji matches checkbox state (⏳ for in-progress, ✅ for done)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "CHK-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "CHK"
# Human-readable check title
title = "Reference Validity"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] All `cpt-{system}-*` references resolve to valid definitions in source artifacts (DESIGN, PRD)
- [ ] No orphaned checked references (reference checked but definition unchecked)
- [ ] No duplicate checkboxes for the same ID within a feature block
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "DOC-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "DOC"
# Human-readable check title
title = "Explicit Non-Applicability"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] If a design element is intentionally NOT covered, it is explicitly stated with reasoning
- [ ] If features intentionally overlap, the reason is documented
- [ ] No silent omissions — reviewer can distinguish "considered and excluded" from "forgot"
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "DECOMP-NO-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "DECOMP"
# Human-readable check title
title = "No Implementation Details"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "DECOMP-NO-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "DECOMP"
# Human-readable check title
title = "No Requirements Definitions"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "DECOMP-NO-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "DECOMP"
# Human-readable check title
title = "No Architecture Decisions"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "FMT-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "FMT"
# Human-readable check title
title = "Feature Entry Format"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "format_validation"
```
```markdown
- [ ] Each feature entry has unique title
- [ ] Each feature entry has stable identifier
- [ ] Entries are consistently formatted
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "FMT-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "FMT"
# Human-readable check title
title = "Required Fields Present"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
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

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "FMT-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "FMT"
# Human-readable check title
title = "Checkbox Syntax"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Check kind: must_have | must_not_have
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

Headings, prompts, IDs, and examples that define the generated `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md`
and `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/examples/example.md` files. The DECOMPOSITION template covers: overview, feature
entries with status/priority/scope/dependencies/traceability.

### Title (H1)

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "decomposition-h1-title"
# Markdown heading level (1=H1 … 6=H6)
level = 1
# true = heading MUST appear in artifact | false = optional
required = true
# numbered: true = required | false = prohibited | omit = allowed
numbered = false
# multiple: true = required (2+) | false = prohibited (exactly one) | omit = allowed
multiple = false
# Suggested heading text template for authors
template = "Decomposition: {PROJECT_NAME}"
# Brief writing instruction for content under this heading
prompt = "Project or system name"
# Human description of this heading's purpose
description = "DECOMPOSITION document title (H1)."
# Example heading texts showing correct usage
examples = ["# Decomposition: TaskFlow"]
```
`@/cpt:heading`

### Overview

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "decomposition-overview"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# numbered: true = required | false = prohibited | omit = allowed
numbered = true
# multiple: true = required (2+) | false = prohibited (exactly one) | omit = allowed
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Overview"
# Human description of this heading's purpose
description = "Overview of decomposition strategy."
# Example heading texts showing correct usage
examples = ["## 1. Overview"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md`.

`@cpt:prompt`
```markdown
{ Description of how the DESIGN was decomposed into features, the decomposition strategy, and any relevant decomposition rationale. }
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/examples/example.md`.

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

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "decomposition-entries"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# numbered: true = required | false = prohibited | omit = allowed
numbered = true
# multiple: true = required (2+) | false = prohibited (exactly one) | omit = allowed
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Entries"
# Human description of this heading's purpose
description = "List of feature entries."
# Example heading texts showing correct usage
examples = ["## 2. Entries"]
```
`@/cpt:heading`

> **`@cpt:id`** — Identifier constraint. Defines an ID kind (template, references, task/priority rules). Output: `constraints.toml`.

`@cpt:id`
```toml
kind = "status"
name = "Overall Status"
description = "A decomposition-level status indicator used to summarize overall progress/state."
required = false          # true = at least one ID of this kind must exist in artifact
# task: omitted (optional) # true = must carry task attr | false = prohibited | omit = optional
# priority: omitted (optional) # true = must carry priority | false = prohibited | omit = optional
template = "cpt-{system}-status-overall"
examples = ["cpt-cypilot-status-overall", "cpt-ex-ovwa-status-overall", "cpt-cypilot-status-overall"]
to_code = false              # true = ID is expected to appear in code via @cpt-* markers
headings = ["decomposition-entries"]  # heading constraint IDs where this identifier must be placed
```
`@/cpt:id`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md`.

`@cpt:prompt`
```markdown
**Overall implementation status:**

- [ ] `p1` - **ID**: `cpt-{system}-status-overall`
```
`@/cpt:prompt`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "decomposition-entry"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# numbered: true = required | false = prohibited | omit = allowed
numbered = true
# multiple: true = required (2+) | false = prohibited (exactly one) | omit = allowed
multiple = true
# Suggested heading text template for authors
template = "[{Feature Title 1}](feature-{slug}/) - HIGH"
# Human description of this heading's purpose
description = "A single feature entry."
# Example heading texts showing correct usage
examples = []
```
`@/cpt:heading`

> **`@cpt:id`** — Identifier constraint. Defines an ID kind (template, references, task/priority rules). Output: `constraints.toml`.

`@cpt:id`
```toml
kind = "feature"
name = "Feature Entry"
description = "A DECOMPOSITION entry representing a FEATURE spec, including dependency and coverage links."
required = true          # true = at least one ID of this kind must exist in artifact
# task: omitted (optional) # true = must carry task attr | false = prohibited | omit = optional
# priority: omitted (optional) # true = must carry priority | false = prohibited | omit = optional
template = "cpt-{system}-feature-{slug}"
examples = ["cpt-cypilot-feature-template-system", "cpt-cypilot-feature-adapter-system", "cpt-ex-ovwa-feature-tracker-core"]
to_code = false              # true = ID is expected to appear in code via @cpt-* markers
headings = ["decomposition-entry"]  # heading constraint IDs where this identifier must be placed

[references.FEATURE]  # how this ID is referenced in FEATURE artifacts
coverage = true            # true = must reference | false = referencing prohibited | omit = optional
# task: omitted (optional) # true = ref must carry task | false = prohibited | omit = optional
# priority: omitted (optional) # true = ref must carry priority | false = prohibited | omit = optional
headings = ["feature-h1-title"]  # target heading constraint in FEATURE
```
`@/cpt:id`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md`.

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

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/examples/example.md`.

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

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "decomposition-feature-deps"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# numbered: true = required | false = prohibited | omit = allowed
numbered = true
# multiple: true = required (2+) | false = prohibited (exactly one) | omit = allowed
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Feature Dependencies"
# Human description of this heading's purpose
description = "Cross-feature dependency overview."
# Example heading texts showing correct usage
examples = ["## 3. Feature Dependencies"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/template.md`.

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

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/DECOMPOSITION/examples/example.md`.

`@cpt:example`
```markdown
None.
```
`@/cpt:example`
