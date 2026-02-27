# FEATURE Blueprint
Blueprint for Feature Specification Documents.

This file is the single source of truth for:
- template.md generation (from @cpt:heading + @cpt:prompt markers)
- example.md generation (from @cpt:heading examples + @cpt:example markers)
- rules.md generation (from @cpt:rules + @cpt:rule markers)
- checklist.md generation (from @cpt:checklist + @cpt:check markers)
- constraints.toml contributions (from @cpt:heading + @cpt:id markers)

All text between markers is ignored by the generator.

FEATURE defines precise behavior using CDSL (Context-Driven Specification
Language): actor flows, processes/algorithms, state machines, definitions
of done, and acceptance criteria.

## Metadata

> **`@cpt:blueprint`** — Blueprint metadata: artifact kind, kit slug, version. Internal; not output to any file.

`@cpt:blueprint`
```toml
# Blueprint version (semver)
version = 1
# Kit slug this blueprint belongs to
kit = "sdlc"
# Artifact kind: PRD | ADR | DESIGN | DECOMPOSITION | FEATURE | CODE
artifact = "FEATURE"
codebase = false
```
`@/cpt:blueprint`

## Skill Integration

> **`@cpt:skill`** — Skill content. Agent-facing navigation and instructions. Output: `.gen/kits/{slug}/SKILL.md`.

`@cpt:skill`
```markdown
### FEATURE Commands
- `cypilot validate --artifact <FEATURE.md>` — validate FEATURE structure and IDs
- `cypilot list-ids --kind flow` — list all flows
- `cypilot list-ids --kind algo` — list all algorithms
- `cypilot list-ids --kind state` — list all state machines
- `cypilot list-ids --kind dod` — list all definitions of done
- `cypilot where-defined <id>` — find where a FEATURE ID is defined
- `cypilot where-used <id>` — find where a FEATURE ID is referenced in code
### FEATURE Workflows
- **Generate FEATURE**: create a new FEATURE from template with guided CDSL prompts
- **Analyze FEATURE**: validate structure (deterministic) then semantic quality (checklist-based)
```
`@/cpt:skill`

---

## Rules Definition

### Rules Skeleton

> **`@cpt:rules`** — Rules skeleton. Defines section structure (prerequisites, requirements, tasks, validation, etc.) for `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rules`
```toml
# Prerequisite steps (load dependencies, read configs)
[prerequisites]
# Ordered list of section keys (each needs a matching @cpt:rule block)
sections = ["load_dependencies"]

# Requirement sections (structural, semantic, constraints, etc.)
[requirements]
# Ordered list of section keys (each needs a matching @cpt:rule block)
sections = ["structural", "versioning", "semantic", "traceability", "constraints", "scope", "upstream_traceability", "featstatus", "checkbox_management", "deliberate_omissions"]
# Display names for non-obvious requirement section keys
[requirements.names]
deliberate_omissions = "Deliberate Omissions (MUST NOT HAVE)"

# Task phases — step-by-step workflow for creating the artifact
[tasks]
# Ordered list of phase keys (each needs a matching @cpt:rule block)
phases = ["setup", "content_creation", "ids_and_structure", "quality_check"]
# Display names for non-obvious task phase keys
[tasks.names]
ids_and_structure = "IDs and Structure"

# Validation phases — ordered checks run after artifact is written
[validation]
# Ordered list of phase keys (each needs a matching @cpt:rule block)
phases = ["structural", "semantic", "traceability", "validation_report", "applicability", "report_format", "reporting"]
# Display names for non-obvious validation phase keys
[validation.names]
structural = "Structural Validation (Deterministic)"
semantic = "Semantic Validation (Checklist-based)"
traceability = "Traceability Validation (if FULL mode)"
applicability = "Applicability Context"
report_format = "Report Format"
reporting = "Reporting Commitment"

# Error handling sections — what to do when things go wrong
[error_handling]
# Ordered list of section keys (each needs a matching @cpt:rule block)
sections = ["missing_decomposition", "missing_design", "missing_parent", "escalation"]

# Next steps — recommended actions after completing the artifact
[next_steps]
# Ordered list of section keys (each needs a matching @cpt:rule block)
sections = ["options"]
```
`@/cpt:rules`

### Prerequisites

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "prerequisites"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "load_dependencies"
```
```markdown
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md` for structure
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md` for semantic guidance
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/examples/task-crud.md` for reference style
- [ ] Read DECOMPOSITION to get feature ID and context
- [ ] Read DESIGN to understand domain types and components
- [ ] Read `{cypilot_path}/config/artifacts.toml` to determine FEATURE artifact path
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/constraints.toml` for kit-level constraints
- [ ] Load `{cypilot_path}/.core/architecture/specs/traceability.md` for ID formats
```
`@/cpt:rule`

### Requirements

#### Structural

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "structural"
```
```markdown
- [ ] FEATURE follows `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md` structure
- [ ] Artifact frontmatter (optional): use `cpt:` format for document metadata
- [ ] References parent feature from DECOMPOSITION manifest
- [ ] All flows, algorithms, states, DoD items have unique IDs
- [ ] All IDs follow `cpt-{system}-{kind}-{slug}` pattern (see artifacts.toml for hierarchy)
- [ ] All IDs have priority markers (`p1`-`p9`) when required by constraints
- [ ] If you want to keep feature ownership obvious, include the feature slug in `{slug}` (example: `algo-cli-control-handle-command`)
- [ ] CDSL instructions follow format: `N. [ ] - \`pN\` - Description - \`inst-slug\``
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs within document
```
`@/cpt:rule`

#### Versioning

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "versioning"
```
```markdown
- [ ] When editing existing FEATURE: increment version in frontmatter
- [ ] When flow/algo/state/dod significantly changes: add `-v{N}` suffix to ID
- [ ] Keep changelog of significant changes
- [ ] Versioning code markers must match: `@cpt-{kind}:cpt-{system}-{kind}-{slug}-v2:p{N}`
```
`@/cpt:rule`

#### Semantic

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "semantic"
```
```markdown
**Reference**: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md` for detailed criteria

- [ ] Actor flows define complete user journeys
- [ ] Algorithms specify processing logic clearly
- [ ] State machines capture all valid transitions
- [ ] DoD items are testable and traceable
- [ ] CDSL instructions describe "what" not "how"
- [ ] Control flow keywords used correctly (IF, RETURN, FROM/TO/WHEN)
```
`@/cpt:rule`

#### Traceability

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "traceability"
```
```markdown
- [ ] All IDs with `to_code="true"` must be traced to code
- [ ] Code must contain markers: `@cpt-{kind}:{cpt-id}:p{N}`
- [ ] Each CDSL instruction maps to code marker
```
`@/cpt:rule`

#### Constraints

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

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

#### Scope

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "scope"
```
```markdown
**One FEATURE per feature from DECOMPOSITION manifest**. Match scope to implementation unit.

| Scope | Examples | Guideline |
|-------|----------|-----------|
| **Too broad** | "User management feature" covering auth, profiles, roles | Split into separate FEATUREs |
| **Right size** | "User login flow" covering single capability | Clear boundary, implementable unit |
| **Too narrow** | "Validate email format" | Implementation detail, belongs in flow/algo |

**FEATURE-worthy content**:
- Actor flows (complete user journeys)
- Algorithms (processing logic)
- State machines (entity lifecycle)
- DoD items / acceptance criteria
- Test scenarios

**NOT FEATURE-worthy** (use other artifacts):
- System architecture → DESIGN
- Technology decisions → ADR
- Business requirements → PRD
- Multiple unrelated capabilities → Split into FEATUREs

**Relationship to other artifacts**:
- **DECOMPOSITION** → FEATURE: DECOMPOSITION lists what to build, FEATURE details implementable behavior
- **DESIGN** → FEATURE: DESIGN provides architecture context, FEATURE details implementable behavior
- **FEATURE** → CODE: FEATURE defines behavior, CODE implements with traceability markers
```
`@/cpt:rule`

#### Upstream Traceability

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "upstream_traceability"
```
```markdown
- [ ] When all flows/algorithms/states/DoD items `[x]` → mark feature as `[x]` in DECOMPOSITION
- [ ] When feature complete → update status in DECOMPOSITION (→ IMPLEMENTED)
```
`@/cpt:rule`

#### Feature Status

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "featstatus"
```
```markdown
- [ ] FEATURE defines a `featstatus` ID definition directly under the H1 title (before `## Feature Context`)
- [ ] Template: `cpt-{system}-featstatus-{feature-slug}`
- [ ] The `featstatus` checkbox MUST be consistent with all task-tracked items within its scope:
  - If `featstatus` is `[x]` then ALL nested task-tracked ID definitions AND ALL task-checkbox references within its content MUST be `[x]`
  - If ALL nested task-tracked ID definitions AND ALL task-checkbox references within its content are `[x]` then `featstatus` MUST be `[x]`
- [ ] `featstatus` is a documentation/status rollup marker (it is not a `to_code` identifier kind)
```
`@/cpt:rule`

#### Checkbox Management

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "checkbox_management"
```
```markdown
**Quick Reference**: Check FEATURE element when ALL code markers for that element exist and implementation verified.

| ID kind | `to_code` | Check when... |
|---------|-----------|---------------|
| `flow` | `true` | ALL `@cpt-flow:cpt-{system}-flow-{feature-slug}-{slug}:p{N}` markers exist in code |
| `algo` | `true` | ALL `@cpt-algo:cpt-{system}-algo-{feature-slug}-{slug}:p{N}` markers exist in code |
| `state` | `true` | ALL `@cpt-state:cpt-{system}-state-{feature-slug}-{slug}:p{N}` markers exist in code |
| `dod` | `true` | Implementation complete AND tests pass |

**Detailed Rules**:

| Kind | `to_code` | Meaning |
|---------|-----------|--------|
| `flow` | `true` | Flow is checked when code markers exist and implementation verified |
| `algo` | `true` | Algorithm is checked when code markers exist and implementation verified |
| `state` | `true` | State machine is checked when code markers exist and implementation verified |
| `dod` | `true` | DoD item is checked when implementation complete and tests pass |

**Checkbox States**:
1. **Flow Checkbox** (kind: `flow`):
   - `[ ] **ID**: cpt-{system}-flow-{feature-slug}-{slug}` — unchecked until implemented
   - `[x] **ID**: cpt-{system}-flow-{feature-slug}-{slug}` — checked when ALL code markers exist
2. **Algorithm Checkbox** (kind: `algo`):
   - `[ ] **ID**: cpt-{system}-algo-{feature-slug}-{slug}` — unchecked until implemented
   - `[x] **ID**: cpt-{system}-algo-{feature-slug}-{slug}` — checked when ALL code markers exist
3. **State Machine Checkbox** (kind: `state`):
   - `[ ] **ID**: cpt-{system}-state-{feature-slug}-{slug}` — unchecked until implemented
   - `[x] **ID**: cpt-{system}-state-{feature-slug}-{slug}` — checked when ALL code markers exist
4. **DoD Checkbox** (kind: `dod`):
   - `[ ] p1 - cpt-{system}-dod-{feature-slug}-{slug}` — unchecked until satisfied
   - `[x] p1 - cpt-{system}-dod-{feature-slug}-{slug}` — checked when implementation complete and tests pass

**When to Update Upstream Artifacts**:
- [ ] When `flow` is checked → verify all CDSL instructions have code markers
- [ ] When `algo` is checked → verify algorithm logic is implemented
- [ ] When `state` is checked → verify all transitions are implemented
- [ ] When `dod` is checked → verify requirement is satisfied and tested
- [ ] When ALL defined IDs in FEATURE are `[x]` → mark feature as complete in DECOMPOSITION
- [ ] When feature is `[x]` → update upstream references in DECOMPOSITION (which cascades to PRD/DESIGN)

**Validation Checks**:
- `cypilot validate` will warn if `to_code="true"` ID has no code markers
- `cypilot validate` will warn if a reference points to a non-existent ID
- `cypilot validate` will report code coverage: N% of CDSL instructions have markers

**Cross-Artifact References**:

| Reference Type | Source Artifact | Purpose |
|----------------|-----------------|--------|
| Parent feature ID | DECOMPOSITION | Links to parent feature in manifest |
| Actor ID (`cpt-{system}-actor-{slug}`) | PRD | Identifies actors involved in flows |
| FR ID (`cpt-{system}-fr-{slug}`) | PRD | Covers functional requirement |
| NFR ID (`cpt-{system}-nfr-{slug}`) | PRD | Covers non-functional requirement |
| Principle ID (`cpt-{system}-principle-{slug}`) | DESIGN | Applies design principle |
| Constraint ID (`cpt-{system}-constraint-{slug}`) | DESIGN | Satisfies design constraint |
| Component ID (`cpt-{system}-component-{slug}`) | DESIGN | Uses design component |
| Sequence ID (`cpt-{system}-seq-{slug}`) | DESIGN | Implements sequence diagram |
| Data ID (`cpt-{system}-dbtable-{slug}`) | DESIGN | Uses database table |
```
`@/cpt:rule`

#### Deliberate Omissions (MUST NOT HAVE)

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "requirements"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "deliberate_omissions"
```
```markdown
FEATURE documents must NOT contain the following — report as violation if found:

- **ARCH-FDESIGN-NO-001**: No System-Level Type Redefinitions (CRITICAL) — system types belong in DESIGN
- **ARCH-FDESIGN-NO-002**: No New API Endpoints (CRITICAL) — API surface belongs in DESIGN
- **ARCH-FDESIGN-NO-003**: No Architectural Decisions (HIGH) — decisions belong in ADR
- **BIZ-FDESIGN-NO-001**: No Product Requirements (HIGH) — requirements belong in PRD
- **BIZ-FDESIGN-NO-002**: No Sprint/Task Breakdowns (HIGH) — tasks belong in DECOMPOSITION
- **MAINT-FDESIGN-NO-001**: No Code Snippets (HIGH) — code belongs in implementation
- **TEST-FDESIGN-NO-001**: No Test Implementation (MEDIUM) — test code belongs in implementation
- **SEC-FDESIGN-NO-001**: No Security Secrets (CRITICAL) — secrets must never appear in documentation
- **OPS-FDESIGN-NO-001**: No Infrastructure Code (MEDIUM) — infra code belongs in implementation
```
`@/cpt:rule`

### Task Phases

#### Setup

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "setup"
```
```markdown
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md` for structure
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md` for semantic guidance
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/examples/task-crud.md` for reference style
- [ ] Read DECOMPOSITION to get feature ID and context
- [ ] Read DESIGN to understand domain types and components
- [ ] Read `{cypilot_path}/config/artifacts.toml` to determine FEATURE artifact path

**FEATURE path resolution**:
- Read system's `artifacts_dir` from `artifacts.toml` (default: `architecture`)
- Use kit's default subdirectory for FEATUREs: `features/`
```
`@/cpt:rule`

#### Content Creation

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "content_creation"
```
```markdown
**CDSL instruction generation:**
- [ ] Each instruction has phase marker: `\`pN\``
- [ ] Each instruction has unique inst ID: `\`inst-{slug}\``
- [ ] Instructions describe what, not how
- [ ] Use **IF**, **RETURN**, **FROM/TO/WHEN** keywords for control flow
- [ ] Nested instructions for conditional branches
```
`@/cpt:rule`

#### IDs & Structure

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "ids_and_structure"
```
```markdown
- [ ] Generate flow IDs: `cpt-{system}-flow-{feature-slug}-{slug}`
- [ ] Generate algorithm IDs: `cpt-{system}-algo-{feature-slug}-{slug}`
- [ ] Generate state IDs: `cpt-{system}-state-{feature-slug}-{slug}`
- [ ] Generate DoD IDs: `cpt-{system}-dod-{feature-slug}-{slug}`
- [ ] Assign priorities (`p1`-`p9`) based on feature priority
- [ ] Verify ID uniqueness with `cypilot list-ids`
```
`@/cpt:rule`

#### Quality Check

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "tasks"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "quality_check"
```
```markdown
- [ ] Compare CDSL style to `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/examples/task-crud.md`
- [ ] Self-review against `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md` MUST HAVE items
- [ ] Ensure no MUST NOT HAVE violations
- [ ] Verify parent feature reference exists
```
`@/cpt:rule`

### Error Handling

#### Missing Decomposition

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "error_handling"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "missing_decomposition"
```
```markdown
- [ ] Option 1: Run `/cypilot-generate DECOMPOSITION` first (recommended)
- [ ] Option 2: Continue without manifest (FEATURE will lack traceability)
```
`@/cpt:rule`

#### Missing Design

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "error_handling"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "missing_design"
```
```markdown
- [ ] Option 1: Run `/cypilot-generate DESIGN` first (recommended for architectural context)
- [ ] Option 2: Continue without DESIGN (reduced domain model context)
  - Document "DESIGN pending" in FEATURE frontmatter
  - Skip component/type references validation
  - Plan to update when DESIGN available
```
`@/cpt:rule`

#### Missing Parent

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "error_handling"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "missing_parent"
```
```markdown
- [ ] Verify feature ID: `cpt-{system}-feature-{slug}`
- [ ] If new feature: add to DECOMPOSITION first
- [ ] If typo: correct the ID reference
```
`@/cpt:rule`

#### Escalation

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "error_handling"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "escalation"
```
```markdown
- [ ] Ask user when flow complexity requires domain expertise
- [ ] Ask user when algorithm correctness uncertain
- [ ] Ask user when state transitions ambiguous
```
`@/cpt:rule`

### Validation

#### Structural

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

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
  - CDSL instruction format
  - No placeholders
  - Parent feature reference validity
```
`@/cpt:rule`

#### Semantic

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "semantic"
```
```markdown
Apply `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md` systematically:
1. For each MUST HAVE item: check if requirement is met
2. For each MUST NOT HAVE item: scan document for violations
3. Use example for quality baseline
```
`@/cpt:rule`

#### Traceability

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "traceability"
```
```markdown
For IDs with `to_code="true"`:
- [ ] Verify code markers exist: `@cpt-{kind}:{cpt-id}:p{N}`
- [ ] Report missing markers
- [ ] Report orphaned markers
```
`@/cpt:rule`

#### Validation Report

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "validation_report"
```
````markdown
```
FEATURE Validation Report
═══════════════════════════

Structural: PASS/FAIL
Semantic: PASS/FAIL (N issues)

Issues:
- [SEVERITY] CHECKLIST-ID: Description
```
````
`@/cpt:rule`

#### Applicability Context

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "applicability"
```
```markdown
Before evaluating each checklist item, the expert MUST:

1. **Understand the feature's domain** — What kind of feature is this? (e.g., user-facing UI feature, backend API feature, data processing pipeline, CLI command)

2. **Determine applicability for each requirement** — Not all checklist items apply to all features:
   - A simple CRUD feature may not need complex State Management analysis
   - A read-only feature may not need Data Integrity analysis
   - A CLI feature may not need UI/UX analysis

3. **Require explicit handling** — For each checklist item:
   - If applicable: The document MUST address it (present and complete)
   - If not applicable: The document MUST explicitly state "Not applicable because..." with reasoning
   - If missing without explanation: Report as violation

4. **Never skip silently** — Either:
   - The requirement is met (document addresses it), OR
   - The requirement is explicitly marked not applicable (document explains why), OR
   - The requirement is violated (report it with applicability justification)

**Key principle**: The reviewer must be able to distinguish "author considered and excluded" from "author forgot"
```
`@/cpt:rule`

#### Report Format

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

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

- **Why Applicable**: Explain why this requirement applies to this specific feature's context (e.g., "This feature handles user authentication, therefore security analysis is required")
- **Checklist Item**: `{CHECKLIST-ID}` — {Checklist item title}
- **Severity**: CRITICAL|HIGH|MEDIUM|LOW
- **Issue**: What is wrong (requirement missing or incomplete)
- **Evidence**: Quote the exact text or "No mention found"
- **Why it matters**: Impact (risk, cost, user harm, compliance)
- **Proposal**: Concrete fix with clear acceptance criteria

```markdown
## Review Report (Issues Only)

### 1. {Short issue title}

**Checklist Item**: `{CHECKLIST-ID}` — {Checklist item title}

**Severity**: CRITICAL|HIGH|MEDIUM|LOW

#### Why Applicable

{Explain why this requirement applies to this feature's context}

#### Issue

{What is wrong}

#### Evidence

{Quote or "No mention found"}

#### Why It Matters

{Impact}

#### Proposal

{Concrete fix}
```
````
`@/cpt:rule`

#### Reporting Commitment

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "validation"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "reporting"
```
```markdown
- [ ] I reported all issues I found
- [ ] I used the exact report format defined in this checklist (no deviations)
- [ ] I included Why Applicable justification for each issue
- [ ] I included evidence and impact for each issue
- [ ] I proposed concrete fixes for each issue
- [ ] I did not hide or omit known problems
- [ ] I verified explicit handling for all major checklist categories
- [ ] I am ready to iterate on the proposals and re-review after changes
```
`@/cpt:rule`

### Next Steps

> **`@cpt:rule`** — Rule entry. TOML selects category+section; markdown block becomes the section body in `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/rules.md`.

`@cpt:rule`
```toml
# Rule category: prerequisites | requirements | tasks | validation | error_handling | next_steps
kind = "next_steps"
# Section name — must match a section defined in the @cpt:rules skeleton
section = "options"
```
```markdown
- [ ] FEATURE design complete → `/cypilot-generate CODE` — implement feature
- [ ] Code implementation done → `/cypilot-analyze CODE` — validate implementation
- [ ] Feature IMPLEMENTED → update status in DECOMPOSITION
- [ ] Another feature to design → `/cypilot-generate FEATURE` — design next feature
- [ ] Want checklist review only → `/cypilot-analyze semantic` — semantic validation
```
`@/cpt:rule`

---

## Checklist Definition

Feature quality checks organized by domain.

### Checklist Skeleton

> **`@cpt:checklist`** — Checklist preamble. Static markdown placed at the top of `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md` (standards, prerequisites, severity dictionary).

`@cpt:checklist`
```toml
[severity]
levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

[review]
priority = ["ARCH", "SEM", "PERF", "SEC", "REL", "DATA", "INT", "OPS", "MAINT", "TEST", "COMPL", "UX", "BIZ", "DOC"]

[[domain]]
abbr = "ARCH"
name = "🏗️ ARCHITECTURE Expertise"
header = "🏗️ ARCHITECTURE Expertise (ARCH)"
standards_text = """> **Standard**: [IEEE 1016-2009](https://standards.ieee.org/ieee/1016/4502/) — Software Design Descriptions
>
> Design entities require: identification, type, purpose, function, subordinates, dependencies, resources, processing, data (§5.4)"""

[[domain]]
abbr = "SEM"
name = "Semantic Alignment"
header = "Semantic Alignment (SEM)"
standards_text = """> **Standard**: [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) — Requirements Engineering
>
> "Each requirement shall be traceable bidirectionally... uniquely identified" (§5.2.8, §6.5)"""

[[domain]]
abbr = "PERF"
name = "⚡ PERFORMANCE Expertise"
header = "⚡ PERFORMANCE Expertise (PERF)"
standards_text = """> **Standard**: [ISO/IEC 25010:2011](https://www.iso.org/standard/35733.html) — Performance Efficiency
>
> Sub-characteristics: time behavior, resource utilization, capacity under defined conditions"""

[[domain]]
abbr = "SEC"
name = "🔒 SECURITY Expertise"
header = "🔒 SECURITY Expertise (SEC)"
standards_text = """> **Standards**:
> - [ISO/IEC 25010:2011](https://www.iso.org/standard/35733.html) — Security: confidentiality, integrity, non-repudiation, accountability, authenticity
> - [OWASP ASVS 5.0](https://owasp.org/www-project-application-security-verification-standard/) — Application Security Verification Standard"""

[[domain]]
abbr = "REL"
name = "🛡️ RELIABILITY Expertise"
header = "🛡️ RELIABILITY Expertise (REL)"
standards_text = """> **Standard**: [ISO/IEC 25010:2011](https://www.iso.org/standard/35733.html) — Reliability
>
> Sub-characteristics: maturity, availability, fault tolerance, recoverability"""

[[domain]]
abbr = "DATA"
name = "📊 DATA Expertise"
header = "📊 DATA Expertise (DATA)"
standards = []

[[domain]]
abbr = "INT"
name = "🔌 INTEGRATION Expertise"
header = "🔌 INTEGRATION Expertise (INT)"
standards = []

[[domain]]
abbr = "OPS"
name = "🖥️ OPERATIONS Expertise"
header = "🖥️ OPERATIONS Expertise (OPS)"
standards = []

[[domain]]
abbr = "MAINT"
name = "🔧 MAINTAINABILITY Expertise"
header = "🔧 MAINTAINABILITY Expertise (MAINT)"
standards_text = """> **Standard**: [ISO/IEC 25010:2011](https://www.iso.org/standard/35733.html) — Maintainability
>
> Sub-characteristics: modularity, reusability, analysability, modifiability, testability"""

[[domain]]
abbr = "TEST"
name = "🧪 TESTING Expertise"
header = "🧪 TESTING Expertise (TEST)"
standards_text = """> **Standards**:
> - [ISO/IEC/IEEE 29119-3:2021](https://www.iso.org/standard/79429.html) — Test documentation templates
> - [ISO/IEC 25010:2011](https://www.iso.org/standard/35733.html) §4.2.7.5 — Testability sub-characteristic"""

[[domain]]
abbr = "COMPL"
name = "📜 COMPLIANCE Expertise"
header = "📜 COMPLIANCE Expertise (COMPL)"
standards = []

[[domain]]
abbr = "UX"
name = "👤 USABILITY Expertise"
header = "👤 USABILITY Expertise (UX)"
standards_text = """> **Standards**:
> - [ISO/IEC 25010:2011](https://www.iso.org/standard/35733.html) — Usability: learnability, operability, user error protection, accessibility
> - [WCAG 2.2](https://www.w3.org/TR/WCAG22/) — Web Content Accessibility Guidelines (Level AA)"""

[[domain]]
abbr = "BIZ"
name = "🏢 BUSINESS Expertise"
header = "🏢 BUSINESS Expertise (BIZ)"
standards_text = """> **Standard**: [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) — Requirements Engineering
>
> "Requirements shall be necessary, implementation-free, unambiguous, consistent, complete, singular, feasible, traceable, verifiable" (§5.2)"""

[[domain]]
abbr = "DOC"
name = "DOC"
header = "DOC (DOC)"
standards = []

```
````markdown
# FEATURE Expert Checklist

**Artifact**: Feature (FEATURE)
**Version**: 2.0
**Last Updated**: 2026-02-03
**Purpose**: Comprehensive quality checklist for FEATURE artifacts

---

## Referenced Standards

This checklist validates FEATURE artifacts based on the following international standards:

| Standard | Domain | Description |
|----------|--------|-------------|
| [IEEE 1016-2009](https://standards.ieee.org/ieee/1016/4502/) | **Design Description** | Software Design Descriptions — detailed design viewpoint, design entities |
| [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) | **Requirements Notation** | Requirements engineering — behavioral requirements, shall notation, traceability |
| [ISO/IEC 25010:2011](https://www.iso.org/standard/35733.html) | **Quality Model** | SQuaRE — 8 quality characteristics: performance, security, reliability, maintainability |
| [ISO/IEC/IEEE 29119-3:2021](https://www.iso.org/standard/79429.html) | **Test Documentation** | Software testing — test specification, acceptance criteria |
| [OWASP ASVS 5.0](https://owasp.org/www-project-application-security-verification-standard/) | **Security Verification** | Application security requirements — authentication, authorization, input validation |
| [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | **Accessibility** | Web Content Accessibility Guidelines — POUR principles, Level AA |
---

## Review Scope Selection

**Choose review mode based on feature complexity and risk**:

| Review Mode | When to Use | Domains to Check |
|-------------|-------------|------------------|
| **Quick** | Simple CRUD, minor updates | ARCH (core) + BIZ + changed domains |
| **Standard** | New feature, moderate complexity | All applicable domains |
| **Full** | Security-sensitive, complex logic | All 12 domains with evidence |

### Quick Review (Core Items Only)

**MUST CHECK** (blocking):
- [ ] ARCH-FDESIGN-001: Feature Context Completeness
- [ ] ARCH-FDESIGN-003: Actor Flow Completeness
- [ ] BIZ-FDESIGN-001: Requirements Alignment
- [ ] DOC-FDESIGN-001: Explicit Non-Applicability

**Changed sections** — also check relevant domain items for any sections modified.

### Domain Prioritization by Feature Type

| Feature Type | Priority Domains (check first) | Secondary Domains | Often N/A |
|--------------|-------------------------------|-------------------|-----------|
| **User-facing UI** | ARCH, UX, SEC, TEST | PERF, REL, DATA | OPS, INT, COMPL |
| **Backend API** | ARCH, SEC, DATA, INT | PERF, REL, TEST | UX, COMPL |
| **Data Processing** | ARCH, DATA, PERF, REL | INT, TEST | SEC, UX, OPS, COMPL |
| **CLI Command** | ARCH, MAINT, TEST | DATA, INT | SEC, PERF, UX, OPS, COMPL |
| **Integration/Webhook** | ARCH, INT, SEC, REL | DATA, TEST | UX, PERF, OPS, COMPL |
| **Auth/Security** | SEC, ARCH, DATA, REL | TEST, COMPL | UX, PERF, OPS, INT |

**Applicability Rule**: Domains in "Often N/A" column still require explicit "Not applicable because..." statement in document if skipped.

---

## Prerequisites

Before starting the review, confirm:

- [ ] I understand this checklist validates FEATURE artifacts
- [ ] I will follow the Applicability Context rules below
- [ ] I will check ALL items in MUST HAVE sections
- [ ] I will verify ALL items in MUST NOT HAVE sections
- [ ] I will document any violations found
- [ ] I will provide specific feedback for each failed check
- [ ] I will complete the Final Checklist and provide a review report

---

## Applicability Context

Before evaluating each checklist item, the expert MUST:

1. **Understand the feature's domain** — What kind of feature is this? (e.g., user-facing UI feature, backend API feature, data processing pipeline, CLI command)

2. **Determine applicability for each requirement** — Not all checklist items apply to all features:
   - A simple CRUD feature may not need complex State Management analysis
   - A read-only feature may not need Data Integrity analysis
   - A CLI feature may not need UI/UX analysis

3. **Require explicit handling** — For each checklist item:
   - If applicable: The document MUST address it (present and complete)
   - If not applicable: The document MUST explicitly state "Not applicable because..." with reasoning
   - If missing without explanation: Report as violation

4. **Never skip silently** — The expert MUST NOT skip a requirement just because it's not mentioned. Either:
   - The requirement is met (document addresses it), OR
   - The requirement is explicitly marked not applicable (document explains why), OR
   - The requirement is violated (report it with applicability justification)

**Key principle**: The reviewer must be able to distinguish "author considered and excluded" from "author forgot"

---

## Severity Dictionary

- **CRITICAL**: Unsafe/misleading/unverifiable; blocks downstream work.
- **HIGH**: Major ambiguity/risk; should be fixed before approval.
- **MEDIUM**: Meaningful improvement; fix when feasible.
- **LOW**: Minor improvement; optional.
````
`@/cpt:checklist`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ARCH-FDESIGN-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ARCH"
# Human-readable check title
title = "Feature Context Completeness"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "IEEE 1016-2009 §5.4.1 (Design entity attributes)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Feature identifier is present and stable (unique within the project)
- [ ] Feature status documented
- [ ] Overall Design reference present
- [ ] Requirements source reference present
- [ ] Actors/user roles are defined and referenced consistently
- [ ] Feature scope clearly stated
- [ ] Feature boundaries explicit
- [ ] Out-of-scope items documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ARCH-FDESIGN-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ARCH"
# Human-readable check title
title = "Overall Design Alignment"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Any shared types/schemas are referenced from a canonical source (architecture doc, schema repo, API contract)
- [ ] Any shared APIs/contracts are referenced from a canonical source (API documentation/spec)
- [ ] Architectural decisions are consistent with the architecture and design baseline (if it exists)
- [ ] Domain concepts are referenced consistently with the canonical domain model (if it exists)
- [ ] API endpoints/contracts are referenced consistently with the canonical API documentation (if it exists)
- [ ] Principles compliance documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ARCH-FDESIGN-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ARCH"
# Human-readable check title
title = "Actor Flow Completeness"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] A flows/user-journeys section exists and is sufficiently detailed
- [ ] All user-facing functionality has actor flows
- [ ] Each flow has a unique name/identifier within the document
- [ ] Flows cover happy path
- [ ] Flows cover error paths
- [ ] Flows cover edge cases
- [ ] Actor/user roles are defined consistently with the requirements document
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ARCH-FDESIGN-004"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ARCH"
# Human-readable check title
title = "Algorithm Completeness"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] A algorithms/business-rules section exists and is sufficiently detailed
- [ ] All business logic has algorithms
- [ ] Each algorithm has a unique name/identifier within the document
- [ ] Algorithms are deterministic and testable
- [ ] Input/output clearly defined
- [ ] Error handling documented
- [ ] Edge cases addressed
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ARCH-FDESIGN-005"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ARCH"
# Human-readable check title
title = "State Management"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] A states/state-machine section exists when stateful behavior is present (can be minimal)
- [ ] Stateful components have state definitions
- [ ] State transitions define explicit triggers/conditions
- [ ] Valid states enumerated
- [ ] Transition guards documented
- [ ] Invalid state transitions documented
- [ ] State persistence documented (if applicable)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ARCH-FDESIGN-006"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ARCH"
# Human-readable check title
title = "Component Interaction"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Inter-component interactions documented
- [ ] Service calls documented
- [ ] Event emissions documented
- [ ] Data flow between components clear
- [ ] Async operations documented
- [ ] Timeout handling documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ARCH-FDESIGN-007"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ARCH"
# Human-readable check title
title = "Extension Points"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Customization points identified
- [ ] Plugin/hook opportunities documented
- [ ] Configuration options documented
- [ ] Feature flags integration documented
- [ ] Versioning considerations documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEM-FDESIGN-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEM"
# Human-readable check title
title = "PRD Coverage Integrity"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC/IEEE 29148:2018 §6.5 (Traceability)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] All referenced PRD FR/NFR IDs are valid and correctly cited
- [ ] Feature requirements do not contradict PRD scope, priorities, or constraints
- [ ] Feature outcomes preserve PRD intent and success criteria
- [ ] Any PRD trade-offs are explicitly documented and approved
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEM-FDESIGN-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEM"
# Human-readable check title
title = "Design Principles and Constraints"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Feature design adheres to design principles referenced in the Overall Design
- [ ] Feature design respects all design constraints and does not bypass them
- [ ] Any constraint exception is explicitly documented with rationale
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEM-FDESIGN-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEM"
# Human-readable check title
title = "Architecture and Component Consistency"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Feature responsibilities align with component boundaries in the Overall Design
- [ ] Interactions and sequences match the system interaction design
- [ ] Data models and entities conform to the Overall Design domain model
- [ ] API contracts and integration boundaries match the Overall Design
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEM-FDESIGN-004"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEM"
# Human-readable check title
title = "Feature Semantics Completeness"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Actor flows, algorithms, and state machines are consistent with the design context
- [ ] Definition of Done mappings cover required design references (principles, constraints, components, sequences, tables)
- [ ] Any semantic deviation from design is documented and approved
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEM-FDESIGN-005"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEM"
# Human-readable check title
title = "Design Decomposition Consistency"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Feature ID matches the entry in the DECOMPOSITION
- [ ] Purpose, scope, and out-of-scope items align with the DECOMPOSITION entry
- [ ] Dependencies in the feature design match the DECOMPOSITION dependency list
- [ ] Requirements covered (FR/NFR) match the DECOMPOSITION mapping
- [ ] Design principles and constraints covered match the DECOMPOSITION mapping
- [ ] Domain entities, components, APIs, sequences, and data tables match the DECOMPOSITION entry
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "PERF-FDESIGN-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "PERF"
# Human-readable check title
title = "Performance-Critical Paths"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2011 §4.2.2 (Performance efficiency)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Hot paths identified
- [ ] Latency-sensitive operations marked
- [ ] Caching strategy documented
- [ ] Batch processing opportunities identified
- [ ] N+1 query prevention addressed
- [ ] Database query optimization documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "PERF-FDESIGN-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "PERF"
# Human-readable check title
title = "Resource Management"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Memory allocation patterns documented
- [ ] Connection pooling documented
- [ ] Resource cleanup documented
- [ ] Large data handling documented
- [ ] Streaming approaches documented (if applicable)
- [ ] Pagination documented (if applicable)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "PERF-FDESIGN-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "PERF"
# Human-readable check title
title = "Scalability Considerations"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Concurrent access handling documented
- [ ] Lock contention minimized
- [ ] Stateless patterns used where possible
- [ ] Horizontal scaling support documented
- [ ] Rate limiting handled
- [ ] Throttling documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "PERF-FDESIGN-004"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "PERF"
# Human-readable check title
title = "Performance Acceptance Criteria"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Response time targets stated
- [ ] Throughput targets stated
- [ ] Resource usage limits stated
- [ ] Performance test requirements documented
- [ ] Baseline metrics identified
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEC-FDESIGN-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEC"
# Human-readable check title
title = "Authentication Integration"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "OWASP ASVS V2 (Authentication), ISO 25010 §4.2.6 (Authenticity)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Authentication requirements documented
- [ ] Session handling documented
- [ ] Token validation documented
- [ ] Authentication failure handling documented
- [ ] Multi-factor requirements documented (if applicable)
- [ ] Service-to-service auth documented (if applicable)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEC-FDESIGN-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEC"
# Human-readable check title
title = "Authorization Implementation"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Permission checks documented in flows
- [ ] Role-based access documented
- [ ] Resource-level authorization documented
- [ ] Authorization failure handling documented
- [ ] Privilege escalation prevention documented
- [ ] Cross-tenant access prevention documented (if applicable)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEC-FDESIGN-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEC"
# Human-readable check title
title = "Input Validation"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "OWASP ASVS V5 (Validation, Sanitization), ISO 25010 §4.2.6 (Integrity)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] All inputs validated
- [ ] Validation rules documented
- [ ] Validation failure handling documented
- [ ] SQL injection prevention documented
- [ ] XSS prevention documented
- [ ] Command injection prevention documented
- [ ] Path traversal prevention documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEC-FDESIGN-004"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEC"
# Human-readable check title
title = "Data Protection"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Sensitive data handling documented
- [ ] PII handling documented
- [ ] Encryption requirements documented
- [ ] Data masking documented (if applicable)
- [ ] Secure data transmission documented
- [ ] Data sanitization documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEC-FDESIGN-005"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEC"
# Human-readable check title
title = "Audit Trail"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Auditable actions identified
- [ ] Audit logging documented
- [ ] User attribution documented
- [ ] Timestamp handling documented
- [ ] Audit data retention documented
- [ ] Non-repudiation requirements documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEC-FDESIGN-006"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEC"
# Human-readable check title
title = "Security Error Handling"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Security errors don't leak information
- [ ] Error messages are safe
- [ ] Stack traces hidden from users
- [ ] Timing attacks mitigated
- [ ] Rate limiting on security operations documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "REL-FDESIGN-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "REL"
# Human-readable check title
title = "Error Handling Completeness"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2011 §4.2.5 (Fault tolerance, Recoverability)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] All error conditions identified
- [ ] Error classification documented
- [ ] Recovery actions documented
- [ ] Error propagation documented
- [ ] User-facing error messages documented
- [ ] Logging requirements documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "REL-FDESIGN-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "REL"
# Human-readable check title
title = "Fault Tolerance"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] External dependency failures handled
- [ ] Timeout handling documented
- [ ] Retry logic documented
- [ ] Circuit breaker integration documented
- [ ] Fallback behavior documented
- [ ] Graceful degradation documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "REL-FDESIGN-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "REL"
# Human-readable check title
title = "Data Integrity"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2011 §4.2.6.2 (Integrity)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Transaction boundaries documented
- [ ] Consistency guarantees documented
- [ ] Concurrent modification handling documented
- [ ] Idempotency documented (where applicable)
- [ ] Data validation before persistence documented
- [ ] Rollback scenarios documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "REL-FDESIGN-004"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "REL"
# Human-readable check title
title = "Resilience Patterns"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Bulkhead patterns documented (if applicable)
- [ ] Backpressure handling documented
- [ ] Queue overflow handling documented
- [ ] Resource exhaustion handling documented
- [ ] Deadlock prevention documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "REL-FDESIGN-005"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "REL"
# Human-readable check title
title = "Recovery Procedures"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Recovery from partial failure documented
- [ ] Data reconciliation documented
- [ ] Manual intervention procedures documented
- [ ] Compensating transactions documented (if applicable)
- [ ] State recovery documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "DATA-FDESIGN-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "DATA"
# Human-readable check title
title = "Data Access Patterns"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Read patterns documented
- [ ] Write patterns documented
- [ ] Query patterns documented
- [ ] Index usage documented
- [ ] Join patterns documented
- [ ] Aggregation patterns documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "DATA-FDESIGN-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "DATA"
# Human-readable check title
title = "Data Validation"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Business rule validation documented
- [ ] Format validation documented
- [ ] Range validation documented
- [ ] Referential integrity validation documented
- [ ] Uniqueness validation documented
- [ ] Validation error messages documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "DATA-FDESIGN-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "DATA"
# Human-readable check title
title = "Data Transformation"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Input transformation documented
- [ ] Output transformation documented
- [ ] Data mapping documented
- [ ] Format conversion documented
- [ ] Null handling documented
- [ ] Default value handling documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "DATA-FDESIGN-004"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "DATA"
# Human-readable check title
title = "Data Lifecycle"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Data creation documented
- [ ] Data update documented
- [ ] Data deletion documented
- [ ] Data archival documented (if applicable)
- [ ] Data retention compliance documented
- [ ] Data migration considerations documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "DATA-FDESIGN-005"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "DATA"
# Human-readable check title
title = "Data Privacy"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH (if applicable)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] PII handling documented
- [ ] Data minimization applied
- [ ] Consent handling documented
- [ ] Data subject rights support documented
- [ ] Cross-border transfer handling documented
- [ ] Anonymization/pseudonymization documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "INT-FDESIGN-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "INT"
# Human-readable check title
title = "API Interactions"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] API calls documented with method + path
- [ ] Request construction documented
- [ ] Response handling documented
- [ ] Error response handling documented
- [ ] Rate limiting handling documented
- [ ] Retry behavior documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "INT-FDESIGN-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "INT"
# Human-readable check title
title = "Database Operations"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] DB operations documented with operation + table
- [ ] Query patterns documented
- [ ] Transaction usage documented
- [ ] Connection management documented
- [ ] Query parameterization documented
- [ ] Result set handling documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "INT-FDESIGN-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "INT"
# Human-readable check title
title = "External Integrations"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH (if applicable)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] External system calls documented
- [ ] Integration authentication documented
- [ ] Timeout configuration documented
- [ ] Failure handling documented
- [ ] Data format translation documented
- [ ] Version compatibility documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "INT-FDESIGN-004"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "INT"
# Human-readable check title
title = "Event/Message Handling"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM (if applicable)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Event publishing documented
- [ ] Event consumption documented
- [ ] Message format documented
- [ ] Ordering guarantees documented
- [ ] Delivery guarantees documented
- [ ] Dead letter handling documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "INT-FDESIGN-005"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "INT"
# Human-readable check title
title = "Cache Integration"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM (if applicable)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Cache read patterns documented
- [ ] Cache write patterns documented
- [ ] Cache invalidation documented
- [ ] Cache miss handling documented
- [ ] Cache TTL documented
- [ ] Cache consistency documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "OPS-FDESIGN-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "OPS"
# Human-readable check title
title = "Observability"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Logging points documented
- [ ] Log levels documented
- [ ] Metrics collection documented
- [ ] Tracing integration documented
- [ ] Correlation ID handling documented
- [ ] Debug information documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "OPS-FDESIGN-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "OPS"
# Human-readable check title
title = "Configuration"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Configuration parameters documented
- [ ] Default values documented
- [ ] Configuration validation documented
- [ ] Runtime configuration documented
- [ ] Environment-specific configuration documented
- [ ] Feature flags documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "OPS-FDESIGN-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "OPS"
# Human-readable check title
title = "Health & Diagnostics"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Health check contributions documented
- [ ] Diagnostic endpoints documented
- [ ] Self-healing behavior documented
- [ ] Troubleshooting guidance documented
- [ ] Common issues documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "OPS-FDESIGN-004"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "OPS"
# Human-readable check title
title = "Rollout & Rollback"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Rollout strategy is documented (phased rollout, feature flag, etc.) when applicable
- [ ] Rollback strategy is documented
- [ ] Data migration/backward compatibility considerations are addressed when applicable
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "MAINT-FDESIGN-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "MAINT"
# Human-readable check title
title = "Code Organization"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2011 §4.2.7 (Modularity, Modifiability)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Module structure implied
- [ ] Separation of concerns evident
- [ ] Single responsibility evident
- [ ] Dependency injection opportunities identified
- [ ] Interface boundaries clear
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "MAINT-FDESIGN-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "MAINT"
# Human-readable check title
title = "Documentation Quality"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Flows self-documenting
- [ ] Complex logic explained
- [ ] Business rules documented
- [ ] Assumptions documented
- [ ] Edge cases documented
- [ ] Examples provided where helpful
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "MAINT-FDESIGN-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "MAINT"
# Human-readable check title
title = "Technical Debt Awareness"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Known limitations documented
- [ ] Workarounds documented
- [ ] Future improvement opportunities noted
- [ ] Deprecation plans documented (if applicable)
- [ ] Migration considerations documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "TEST-FDESIGN-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "TEST"
# Human-readable check title
title = "Testability"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2011 §4.2.7.5 (Testability), ISO/IEC/IEEE 29119-3:2021"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Flows are testable (deterministic, observable)
- [ ] Algorithms are testable (clear inputs/outputs)
- [ ] States are testable (verifiable transitions)
- [ ] Mock boundaries clear
- [ ] Test data requirements documented
- [ ] Test isolation achievable
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "TEST-FDESIGN-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "TEST"
# Human-readable check title
title = "Test Coverage Guidance"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Unit test targets identified
- [ ] Integration test targets identified
- [ ] E2E test scenarios documented
- [ ] Edge case tests identified
- [ ] Error path tests identified
- [ ] Performance test targets identified
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "TEST-FDESIGN-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "TEST"
# Human-readable check title
title = "Acceptance Criteria"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Each requirement has verifiable criteria
- [ ] Criteria are unambiguous
- [ ] Criteria are measurable
- [ ] Criteria cover happy path
- [ ] Criteria cover error paths
- [ ] Criteria testable automatically
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "COMPL-FDESIGN-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "COMPL"
# Human-readable check title
title = "Regulatory Compliance"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH (if applicable)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Compliance requirements addressed
- [ ] Audit trail requirements met
- [ ] Data handling compliant
- [ ] Consent handling compliant
- [ ] Retention requirements met
- [ ] Reporting requirements addressed
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "COMPL-FDESIGN-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "COMPL"
# Human-readable check title
title = "Privacy Compliance"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH (if applicable)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Privacy by design evident
- [ ] Data minimization applied
- [ ] Purpose limitation documented
- [ ] Consent handling documented
- [ ] Data subject rights supported
- [ ] Cross-border considerations addressed
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "UX-FDESIGN-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "UX"
# Human-readable check title
title = "User Experience Flows"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC 25010:2011 §4.2.4 (Usability)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] User journey clear
- [ ] Feedback points documented
- [ ] Error messages user-friendly
- [ ] Loading states documented
- [ ] Progress indication documented
- [ ] Confirmation flows documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "UX-FDESIGN-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "UX"
# Human-readable check title
title = "Accessibility"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM (if applicable)"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "[WCAG 2.2](https://www.w3.org/TR/WCAG22/) Level AA, ISO/IEC 25010:2011 §4.2.4.6 (Accessibility)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Accessibility requirements addressed
- [ ] Keyboard navigation supported
- [ ] Screen reader support documented
- [ ] Color contrast considered
- [ ] Focus management documented
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "BIZ-FDESIGN-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "BIZ"
# Human-readable check title
title = "Requirements Alignment"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Reference standard (ISO, IEEE, etc.) or empty string
ref = "ISO/IEC/IEEE 29148:2018 §5.2 (Characteristics of requirements)"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] All feature requirements (Definitions of Done) documented
- [ ] Requirements trace to PRD
- [ ] Requirements trace to a roadmap/backlog item (if used)
- [ ] Business rules accurately captured
- [ ] Edge cases reflect business reality
- [ ] Acceptance criteria business-verifiable
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "BIZ-FDESIGN-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "BIZ"
# Human-readable check title
title = "Value Delivery"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_have"
```
```markdown
- [ ] Feature delivers stated value
- [ ] User needs addressed
- [ ] Business process supported
- [ ] Success metrics achievable
- [ ] ROI evident
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "DOC-FDESIGN-001"
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
- [ ] If a section or requirement is intentionally omitted, it is explicitly stated in the document (e.g., "Not applicable because...")
- [ ] No silent omissions — every major checklist area is either present or has a documented reason for absence
- [ ] Reviewer can distinguish "author considered and excluded" from "author forgot"
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ARCH-FDESIGN-NO-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ARCH"
# Human-readable check title
title = "No System-Level Type Redefinitions"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No new system-wide entity/type definitions (define once in a canonical place)
- [ ] No new value object definitions
- [ ] No domain model changes
- [ ] No schema definitions
- [ ] No type aliases

**Where it belongs**: Central domain model / schema documentation
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ARCH-FDESIGN-NO-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ARCH"
# Human-readable check title
title = "No New API Endpoints"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No new endpoint definitions
- [ ] No new API contracts
- [ ] No request/response schema definitions
- [ ] No new HTTP methods on existing endpoints
- [ ] Reference existing endpoints by ID only

**Where it belongs**: API contract documentation (e.g., OpenAPI)
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "ARCH-FDESIGN-NO-003"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "ARCH"
# Human-readable check title
title = "No Architectural Decisions"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No "we chose X over Y" discussions
- [ ] No pattern selection justifications
- [ ] No technology choice explanations
- [ ] No pros/cons analysis
- [ ] No decision debates

**Where it belongs**: `ADR`
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "BIZ-FDESIGN-NO-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "BIZ"
# Human-readable check title
title = "No Product Requirements"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No actor definitions (reference PRD)
- [ ] No functional requirement definitions (reference PRD)
- [ ] No use case definitions (reference PRD)
- [ ] No NFR definitions (reference PRD)
- [ ] No business vision

**Where it belongs**: `PRD`
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "BIZ-FDESIGN-NO-002"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "BIZ"
# Human-readable check title
title = "No Sprint/Task Breakdowns"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No sprint assignments
- [ ] No task lists beyond phases
- [ ] No effort estimates
- [ ] No developer assignments
- [ ] No timeline estimates
- [ ] No Jira/Linear ticket references

**Where it belongs**: Project management tools
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "MAINT-FDESIGN-NO-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "MAINT"
# Human-readable check title
title = "No Code Snippets"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "HIGH"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No production code
- [ ] No code diffs
- [ ] No implementation code
- [ ] No configuration file contents
- [ ] No SQL queries (describe operations instead)
- [ ] No API request/response JSON

**Where it belongs**: Source code repository
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "TEST-FDESIGN-NO-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "TEST"
# Human-readable check title
title = "No Test Implementation"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No test code
- [ ] No test scripts
- [ ] No test data files
- [ ] No assertion implementations
- [ ] No mock implementations

**Where it belongs**: Test directories in source code
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "SEC-FDESIGN-NO-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "SEC"
# Human-readable check title
title = "No Security Secrets"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "CRITICAL"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No API keys
- [ ] No passwords
- [ ] No certificates
- [ ] No encryption keys
- [ ] No connection strings with credentials
- [ ] No tokens

**Where it belongs**: Secret management system
```
`@/cpt:check`

> **`@cpt:check`** — Checklist item. TOML defines id/domain/severity; markdown defines the check criteria. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/checklist.md`.

`@cpt:check`
```toml
# Unique check ID (format: {DOMAIN}-{ARTIFACT}-{NNN})
id = "OPS-FDESIGN-NO-001"
# Expertise domain: BIZ|ARCH|SEC|TEST|MAINT|OPS|DOC|UX|SAFE|COMPL|PERF|DATA|INT
domain = "OPS"
# Human-readable check title
title = "No Infrastructure Code"
# Severity: CRITICAL | HIGH | MEDIUM | LOW
severity = "MEDIUM"
# Check kind: must_have | must_not_have
kind = "must_not_have"
```
```markdown
**What to check**:
- [ ] No Terraform/CloudFormation
- [ ] No Kubernetes manifests
- [ ] No Docker configurations
- [ ] No CI/CD pipeline definitions
- [ ] No deployment scripts

**Where it belongs**: Infrastructure code repository
```
`@/cpt:check`


---

## Template Structure

Headings, prompts, IDs, and examples that define the generated `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`
and `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/examples/example.md` files. The FEATURE template covers: context (overview,
purpose, actors, references), actor flows with CDSL instructions, processes/
algorithms, state machines, definitions of done, and acceptance criteria.

### Title (H1)

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "feature-h1-title"
# Markdown heading level (1=H1 … 6=H6)
level = 1
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = false
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Suggested heading text template for authors
template = "Feature: {Feature Name}"
# Brief writing instruction for content under this heading
prompt = "Name of the feature from DECOMPOSITION"
# Human description of this heading's purpose
description = "FEATURE document title (H1)."
# Example heading texts showing correct usage
examples = ["# Feature: Task CRUD"]
```
`@/cpt:heading`

> **`@cpt:id`** — Identifier constraint. Defines an ID kind (template, references, task/priority rules). Output: `constraints.toml`.

`@cpt:id`
```toml
kind = "featstatus"
name = "Feature Status"
description = "A feature-level status/anchor marker used in FEATURE context."
required = true          # true = at least one ID of this kind must exist in artifact
task = true                # true = must carry task attr | false = prohibited | omit = optional
# priority: omitted (optional) # true = must carry priority | false = prohibited | omit = optional
template = "cpt-{system}-featstatus-{feature-slug}"
examples = ["cpt-cypilot-featstatus-template-system", "cpt-ex-ovwa-featstatus-tracker-core", "cpt-todo-app-featstatus-task-storage-foundation"]
to_code = false              # true = ID is expected to appear in code via @cpt-* markers
headings = ["feature-h1-title"]  # heading constraint IDs where this identifier must be placed

[references.DESIGN]  # how this ID is referenced in DESIGN artifacts
coverage = false           # true = must reference | false = referencing prohibited | omit = optional
[references.PRD]  # how this ID is referenced in PRD artifacts
coverage = false           # true = must reference | false = referencing prohibited | omit = optional
```
`@/cpt:id`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:prompt`
```markdown
- [ ] `p1` - **ID**: `cpt-{system}-featstatus-{feature-slug}`
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/examples/example.md`.

`@cpt:example`
```markdown
- [ ] `p1` - **ID**: `cpt-ex-task-flow-featstatus-task-crud`

- [ ] `p2` - `cpt-ex-task-flow-feature-task-crud`
```
`@/cpt:example`

### Feature Context

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "feature-context"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Feature Context"
# Human description of this heading's purpose
description = "Feature context section."
# Example heading texts showing correct usage
examples = ["## Feature Context"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:prompt`
```markdown
- [ ] `p2` - `cpt-{system}-feature-{slug}`
```
`@/cpt:prompt`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "feature-context-overview"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Overview"
# Human description of this heading's purpose
description = "Feature overview."
# Example heading texts showing correct usage
examples = ["### 1. Overview"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:prompt`
```markdown
{Brief overview of what this feature does — 1-2 sentences.}
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/examples/example.md`.

`@cpt:example`
```markdown
Core task management functionality for creating, viewing, updating, and deleting tasks. This feature provides the foundation for team collaboration by enabling users to track work items through their lifecycle.

Problem: Teams need a central place to track tasks with status, priority, and assignments.
Primary value: Enables organized task tracking with clear ownership.
Key assumptions: Users have accounts and belong to at least one team.
```
`@/cpt:example`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "feature-context-purpose"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Purpose"
# Human description of this heading's purpose
description = "Feature purpose."
# Example heading texts showing correct usage
examples = ["### 2. Purpose"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:prompt`
```markdown
{Why this feature exists, what PRD requirements or DESIGN element it addresses.}
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/examples/example.md`.

`@cpt:example`
```markdown
Enable team members to manage their work items with full lifecycle tracking from creation through completion.

Success criteria: Users can create, view, update, and delete tasks within 500ms response time.
```
`@/cpt:example`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "feature-context-actors"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Actors"
# Human description of this heading's purpose
description = "Actors involved in the feature."
# Example heading texts showing correct usage
examples = ["### 3. Actors"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:prompt`
```markdown
| Actor | Role in Feature |
|-------|-----------------|
| `cpt-{system}-actor-{slug}` | {What this actor does in this feature} |
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/examples/example.md`.

`@cpt:example`
```markdown
- `cpt-ex-task-flow-actor-member`
- `cpt-ex-task-flow-actor-lead`
```
`@/cpt:example`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "feature-context-references"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "References"
# Human description of this heading's purpose
description = "References to related artifacts."
# Example heading texts showing correct usage
examples = ["### 4. References"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:prompt`
```markdown
- **PRD**: [PRD.md](../PRD.md)
- **Design**: [DESIGN.md](../DESIGN.md)
- **Dependencies**: {List feature dependencies or "None"}
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/examples/example.md`.

`@cpt:example`
```markdown
- Overall Design: [DESIGN.md](../../DESIGN.md)
- ADRs: `cpt-ex-task-flow-adr-postgres-storage`
- Related feature: [Notifications](../notifications.md)
```
`@/cpt:example`

### Actor Flows (CDSL)

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "feature-actor-flows"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Actor Flows (CDSL)"
# Human description of this heading's purpose
description = "Actor flows section."
# Example heading texts showing correct usage
examples = ["## Actor Flows"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:prompt`
```markdown
User-facing interactions that start with an actor (human or external system) and describe the end-to-end flow of a use case. Each flow has a triggering actor and shows how the system responds to actor actions.
```
`@/cpt:prompt`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "feature-actor-flow"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = false
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = true
# Suggested heading text template for authors
template = "{Flow Name}"
# Human description of this heading's purpose
description = "A single actor flow."
# Example heading texts showing correct usage
examples = []
```
`@/cpt:heading`

> **`@cpt:id`** — Identifier constraint. Defines an ID kind (template, references, task/priority rules). Output: `constraints.toml`.

`@cpt:id`
```toml
kind = "flow"
name = "Flow"
description = "An actor-facing CDSL flow describing a user/system interaction end-to-end."
required = false          # true = at least one ID of this kind must exist in artifact
# task: omitted (optional) # true = must carry task attr | false = prohibited | omit = optional
# priority: omitted (optional) # true = must carry priority | false = prohibited | omit = optional
template = "cpt-{system}-flow-{feature-slug}-{slug}"
examples = ["cpt-cypilot-flow-template-system-load", "cpt-cypilot-flow-template-system-validate", "cpt-ex-ovwa-flow-run-tracker"]
to_code = true              # true = ID is expected to appear in code via @cpt-* markers
headings = ["feature-actor-flow"]  # heading constraint IDs where this identifier must be placed

[references.PRD]  # how this ID is referenced in PRD artifacts
coverage = false           # true = must reference | false = referencing prohibited | omit = optional
```
`@/cpt:id`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:prompt`
```markdown
- [ ] `p1` - **ID**: `cpt-{system}-flow-{feature-slug}-{slug}`

**Actor**: `cpt-{system}-actor-{slug}`

**Success Scenarios**:
- {Scenario 1}

**Error Scenarios**:
- {Error scenario 1}

**Steps**:
1. [ ] - `p1` - {Actor action} - `inst-{step-id}`
2. [ ] - `p1` - {API: METHOD /path (request/response summary)} - `inst-{step-id}`
3. [ ] - `p1` - {DB: OPERATION table(s) (key columns/filters)} - `inst-{step-id}`
4. [ ] - `p1` - **IF** {condition} - `inst-{step-id}`
   1. [ ] - `p1` - {Action if true} - `inst-{step-id}`
5. [ ] - `p1` - **ELSE** - `inst-{step-id}`
   1. [ ] - `p1` - {Action if false} - `inst-{step-id}`
6. [ ] - `p1` - **RETURN** {result} - `inst-{step-id}`
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/examples/example.md`.

`@cpt:example`
```markdown
### Create Task

- [ ] `p1` - **ID**: `cpt-ex-task-flow-flow-create-task`

**Actors**:
- `cpt-ex-task-flow-actor-member`
- `cpt-ex-task-flow-actor-lead`

1. [x] - `p1` - User fills task form (title, description, priority) - `inst-fill-form`
2. [x] - `p1` - API: POST /api/tasks (body: title, description, priority, due_date) - `inst-api-create`
3. [x] - `p1` - Algorithm: validate task input using `cpt-ex-task-flow-algo-validate-task` - `inst-run-validate`
4. [x] - `p1` - DB: INSERT tasks(title, description, priority, due_date, status=BACKLOG) - `inst-db-insert`
5. [ ] - `p2` - User optionally assigns task to team member - `inst-assign`
6. [ ] - `p2` - API: POST /api/tasks/{task_id}/assignees (body: assignee_id) - `inst-api-assign`
7. [ ] - `p2` - DB: INSERT task_assignees(task_id, assignee_id) - `inst-db-assign-insert`
8. [x] - `p1` - API: RETURN 201 Created (task_id, status=BACKLOG) - `inst-return-created`
```
`@/cpt:example`

### Processes / Business Logic

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "feature-processes"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Processes / Business Logic (CDSL)"
# Human description of this heading's purpose
description = "Processes / business logic section."
# Example heading texts showing correct usage
examples = ["## Processes / Business Logic"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:prompt`
```markdown
Internal system functions and procedures that do not interact with actors directly. Examples: database layer operations, authorization logic, middleware, validation routines, library functions, background jobs. These are reusable building blocks called by Actor Flows or other processes.
```
`@/cpt:prompt`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "feature-process"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = false
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = true
# Suggested heading text template for authors
template = "{Process Name}"
# Human description of this heading's purpose
description = "A single process/algorithm."
# Example heading texts showing correct usage
examples = []
```
`@/cpt:heading`

> **`@cpt:id`** — Identifier constraint. Defines an ID kind (template, references, task/priority rules). Output: `constraints.toml`.

`@cpt:id`
```toml
kind = "algo"
name = "Algorithm"
description = "A reusable internal process described in CDSL (business logic not directly initiated by an actor)."
required = false          # true = at least one ID of this kind must exist in artifact
# task: omitted (optional) # true = must carry task attr | false = prohibited | omit = optional
# priority: omitted (optional) # true = must carry priority | false = prohibited | omit = optional
template = "cpt-{system}-algo-{feature-slug}-{slug}"
examples = ["cpt-cypilot-algo-template-system-extract-ids", "cpt-cypilot-algo-methodology-core-apply-constraints", "cpt-ex-ovwa-algo-track-active-time"]
to_code = true              # true = ID is expected to appear in code via @cpt-* markers
headings = ["feature-processes"]  # heading constraint IDs where this identifier must be placed

[references.PRD]  # how this ID is referenced in PRD artifacts
coverage = false           # true = must reference | false = referencing prohibited | omit = optional
```
`@/cpt:id`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:prompt`
```markdown
- [ ] `p2` - **ID**: `cpt-{system}-algo-{feature-slug}-{slug}`

**Input**: {Input description}

**Output**: {Output description}

**Steps**:
1. [ ] - `p1` - {Parse/normalize input} - `inst-{step-id}`
2. [ ] - `p1` - {DB: OPERATION table(s) (key columns/filters)} - `inst-{step-id}`
3. [ ] - `p1` - {API: METHOD /path (request/response summary)} - `inst-{step-id}`
4. [ ] - `p1` - **FOR EACH** {item} in {collection} - `inst-{step-id}`
   1. [ ] - `p1` - {Process item} - `inst-{step-id}`
5. [ ] - `p1` - **TRY** - `inst-{step-id}`
   1. [ ] - `p1` - {Risky operation} - `inst-{step-id}`
6. [ ] - `p1` - **CATCH** {error} - `inst-{step-id}`
   1. [ ] - `p1` - {Handle error} - `inst-{step-id}`
7. [ ] - `p1` - **RETURN** {result} - `inst-{step-id}`
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/examples/example.md`.

`@cpt:example`
```markdown
### Validate Task

- [ ] `p1` - **ID**: `cpt-ex-task-flow-algo-validate-task`

1. [x] - `p1` - **IF** title is empty **RETURN** error "Title required" - `inst-check-title`
2. [x] - `p1` - **IF** priority not in [LOW, MEDIUM, HIGH] **RETURN** error - `inst-check-priority`
3. [x] - `p1` - **IF** due_date is present AND due_date is in the past **RETURN** error - `inst-check-due-date`
4. [x] - `p1` - DB: SELECT tasks WHERE title=? AND status!=DONE (dedupe check) - `inst-db-dedupe-check`
5. [ ] - `p2` - **IF** duplicate exists **RETURN** error - `inst-return-duplicate`
6. [x] - `p1` - **RETURN** valid - `inst-return-valid`
```
`@/cpt:example`

### States

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "feature-states"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "States (CDSL)"
# Human description of this heading's purpose
description = "States section."
# Example heading texts showing correct usage
examples = ["## States"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:prompt`
```markdown
Optional: Include when entities have explicit lifecycle states.
```
`@/cpt:prompt`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "feature-state"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = false
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = true
# Suggested heading text template for authors
template = "{Entity Name} State Machine"
# Human description of this heading's purpose
description = "A single state machine."
# Example heading texts showing correct usage
examples = []
```
`@/cpt:heading`

> **`@cpt:id`** — Identifier constraint. Defines an ID kind (template, references, task/priority rules). Output: `constraints.toml`.

`@cpt:id`
```toml
kind = "state"
name = "State Machine"
description = "A lifecycle/state machine definition for an entity or subsystem, described in CDSL transitions."
required = false          # true = at least one ID of this kind must exist in artifact
# task: omitted (optional) # true = must carry task attr | false = prohibited | omit = optional
# priority: omitted (optional) # true = must carry priority | false = prohibited | omit = optional
template = "cpt-{system}-state-{feature-slug}-{slug}"
examples = ["cpt-cypilot-state-template-system-lifecycle", "cpt-cypilot-state-methodology-core-validation-outcome", "cpt-ex-ovwa-state-daemon-lifecycle"]
to_code = true              # true = ID is expected to appear in code via @cpt-* markers
headings = ["feature-state"]  # heading constraint IDs where this identifier must be placed

[references.PRD]  # how this ID is referenced in PRD artifacts
coverage = false           # true = must reference | false = referencing prohibited | omit = optional
```
`@/cpt:id`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:prompt`
```markdown
- [ ] `p2` - **ID**: `cpt-{system}-state-{feature-slug}-{slug}`

**States**: {State1}, {State2}, {State3}

**Initial State**: {State1}

**Transitions**:
1. [ ] - `p1` - **FROM** {State1} **TO** {State2} **WHEN** {condition} - `inst-{step-id}`
2. [ ] - `p1` - **FROM** {State2} **TO** {State3} **WHEN** {condition} - `inst-{step-id}`
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/examples/example.md`.

`@cpt:example`
```markdown
### Task Status

- [ ] `p1` - **ID**: `cpt-ex-task-flow-state-task-status`

1. [x] - `p1` - **FROM** BACKLOG **TO** IN_PROGRESS **WHEN** user starts work - `inst-start`
2. [ ] - `p2` - **FROM** IN_PROGRESS **TO** DONE **WHEN** user completes - `inst-complete`
3. [ ] - `p2` - **FROM** DONE **TO** BACKLOG **WHEN** user reopens - `inst-reopen`
```
`@/cpt:example`

### Definitions of Done

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "feature-dod"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Definitions of Done"
# Human description of this heading's purpose
description = "Definitions of done section."
# Example heading texts showing correct usage
examples = ["## Definitions of Done"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:prompt`
```markdown
Specific implementation tasks derived from flows/algorithms above.
```
`@/cpt:prompt`

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "feature-dod-entry"
# Markdown heading level (1=H1 … 6=H6)
level = 3
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = false
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = true
# Suggested heading text template for authors
template = "{Requirement Title}"
# Human description of this heading's purpose
description = "A single definition of done entry."
# Example heading texts showing correct usage
examples = []
```
`@/cpt:heading`

> **`@cpt:id`** — Identifier constraint. Defines an ID kind (template, references, task/priority rules). Output: `constraints.toml`.

`@cpt:id`
```toml
kind = "dod"
name = "Definition of Done"
description = "A concrete implementation task derived from flows/processes/states, with required traceability."
required = true          # true = at least one ID of this kind must exist in artifact
task = true                # true = must carry task attr | false = prohibited | omit = optional
priority = true            # true = must carry priority attr | false = prohibited | omit = optional
template = "cpt-{system}-dod-{feature-slug}-{slug}"
examples = ["cpt-cypilot-dod-template-system-validation", "cpt-cypilot-dod-methodology-core", "cpt-ex-ovwa-dod-launchagent-autostart"]
to_code = true              # true = ID is expected to appear in code via @cpt-* markers
headings = ["feature-dod-entry"]  # heading constraint IDs where this identifier must be placed

[references.PRD]  # how this ID is referenced in PRD artifacts
coverage = false           # true = must reference | false = referencing prohibited | omit = optional
```
`@/cpt:id`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:prompt`
```markdown
- [ ] `p1` - **ID**: `cpt-{system}-dod-{feature-slug}-{slug}`

The system **MUST** {clear description of what to implement}.

**Implements**:
- `cpt-{system}-flow-{feature-slug}-{slug}`

**Touches**:
- API: `{METHOD} {/path}`
- DB: `{table}`
- Entities: `{EntityName}`
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/examples/example.md`.

`@cpt:example`
```markdown
### Task Creation

- [ ] `p1` - **ID**: `cpt-ex-task-flow-dod-task-create`

Users can create tasks with title, description, priority, and due date. The system validates input and stores the task with BACKLOG status.

**Implementation details**:
- API: `POST /api/tasks` with JSON body `{title, description, priority, due_date}`
- DB: insert into `tasks` table (columns: title, description, priority, due_date, status)
- Domain: `Task` entity (id, title, description, priority, due_date, status)

**Implements**:
- `cpt-ex-task-flow-flow-create-task`
- `cpt-ex-task-flow-algo-validate-task`

**Covers (PRD)**:
- `cpt-ex-task-flow-fr-task-management`
- `cpt-ex-task-flow-nfr-performance`

**Covers (DESIGN)**:
- `cpt-ex-task-flow-principle-realtime-first`
- `cpt-ex-task-flow-constraint-supported-platforms`
- `cpt-ex-task-flow-component-api-server`
- `cpt-ex-task-flow-component-postgresql`
- `cpt-ex-task-flow-seq-task-creation`
- `cpt-ex-task-flow-dbtable-tasks`
```
`@/cpt:example`

### Acceptance Criteria

> **`@cpt:heading`** — Heading constraint. Defines required/optional heading in the artifact structure. Output: `constraints.toml` + `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:heading`
```toml
# Unique heading constraint ID — referenced by identifier.headings to bind IDs to sections
id = "feature-acceptance-criteria"
# Markdown heading level (1=H1 … 6=H6)
level = 2
# true = heading MUST appear in artifact | false = optional
required = true
# true = may have number prefix (e.g. "1. Overview") | false = no numbering
numbered = true
# true = multiple instances allowed | false = exactly one | "required" = must have 2+
multiple = false
# Regex the heading text must match (omit or null = any text)
pattern = "Acceptance Criteria"
# Human description of this heading's purpose
description = "Acceptance criteria for the feature."
# Example heading texts showing correct usage
examples = ["## Acceptance Criteria"]
```
`@/cpt:heading`

> **`@cpt:prompt`** — Writing instruction. Markdown tells authors what to write under the preceding heading. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/template.md`.

`@cpt:prompt`
```markdown
- [ ] {Testable criterion for this feature}
- [ ] {Another testable criterion}
```
`@/cpt:prompt`

> **`@cpt:example`** — Example content. Filled-in sample of the preceding section. Output: `{cypilot_path}/.gen/kits/sdlc/artifacts/FEATURE/examples/example.md`.

`@cpt:example`
```markdown
- [ ] The feature supports task creation and assignment flow end-to-end
- [ ] Validation rules reject invalid titles, priorities, and past due dates
- [ ] State transitions follow the Task Status state machine

## Additional Context (optional)

The feature must keep task status transitions consistent with the Task Status state machine in Section D. All state changes should emit events for the notification system.
```
`@/cpt:example`
