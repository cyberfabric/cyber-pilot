# FEATURE Rules

**Artifact**: FEATURE
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
   - [Scope](#scope)
   - [Upstream Traceability](#upstream-traceability)
   - [Featstatus](#featstatus)
   - [Checkbox Management](#checkbox-management)
   - [Deliberate Omissions (MUST NOT HAVE)](#deliberate-omissions-must-not-have)
3. [Tasks](#tasks)
   - [Phase 1: Setup](#phase-1-setup)
   - [Phase 2: Content Creation](#phase-2-content-creation)
   - [Phase 3: IDs and Structure](#phase-3-ids-and-structure)
   - [Phase 4: Quality Check](#phase-4-quality-check)
4. [Validation](#validation)
   - [Phase 1: Structural Validation (Deterministic)](#phase-1-structural-validation-deterministic)
   - [Phase 2: Semantic Validation (Checklist-based)](#phase-2-semantic-validation-checklist-based)
   - [Phase 3: Traceability Validation (if FULL mode)](#phase-3-traceability-validation-if-full-mode)
   - [Phase 4: Validation Report](#phase-4-validation-report)
   - [Phase 5: Applicability Context](#phase-5-applicability-context)
   - [Phase 6: Report Format](#phase-6-report-format)
   - [Phase 7: Reporting Commitment](#phase-7-reporting-commitment)
5. [Error Handling](#error-handling)
   - [Missing Decomposition](#missing-decomposition)
   - [Missing Design](#missing-design)
   - [Missing Parent](#missing-parent)
   - [Escalation](#escalation)
6. [Next Steps](#next-steps)
   - [Options](#options)

---

## Prerequisites

### Load Dependencies

- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/task-crud.md` for reference style
- [ ] Read DECOMPOSITION to get feature ID and context
- [ ] Read DESIGN to understand domain types and components
- [ ] Read `{cypilot_path}/config/artifacts.toml` to determine FEATURE artifact path
- [ ] Load `{cypilot_path}/config/kits/sdlc/constraints.toml` for kit-level constraints
- [ ] Load `{cypilot_path}/.core/architecture/specs/traceability.md` for ID formats

---

## Requirements

### Structural

- [ ] FEATURE follows `template.md` structure
- [ ] Artifact frontmatter (optional): use `cpt:` format for document metadata
- [ ] References parent feature from DECOMPOSITION manifest
- [ ] All flows, algorithms, states, DoD items have unique IDs
- [ ] All IDs follow `cpt-{system}-{kind}-{slug}` pattern (see artifacts.toml for hierarchy)
- [ ] All IDs have priority markers (`p1`-`p9`) when required by constraints
- [ ] If you want to keep feature ownership obvious, include the feature slug in `{slug}` (example: `algo-cli-control-handle-command`)
- [ ] CDSL instructions follow format: `N. [ ] - \`pN\` - Description - \`inst-slug\``
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs within document

### Versioning

- [ ] When editing existing FEATURE: increment version in frontmatter
- [ ] When flow/algo/state/dod significantly changes: add `-v{N}` suffix to ID
- [ ] Keep changelog of significant changes
- [ ] Versioning code markers must match: `@cpt-{kind}:cpt-{system}-{kind}-{slug}-v2:p{N}`

### Semantic

**Reference**: `checklist.md` for detailed criteria

- [ ] Actor flows define complete user journeys
- [ ] Algorithms specify processing logic clearly
- [ ] State machines capture all valid transitions
- [ ] DoD items are testable and traceable
- [ ] CDSL instructions describe "what" not "how"
- [ ] Control flow keywords used correctly (IF, RETURN, FROM/TO/WHEN)

### Traceability

- [ ] All IDs with `to_code="true"` must be traced to code
- [ ] Code must contain markers: `@cpt-{kind}:{cpt-id}:p{N}`
- [ ] Each CDSL instruction maps to code marker

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

### Scope

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

### Upstream Traceability

- [ ] When all flows/algorithms/states/DoD items `[x]` → mark feature as `[x]` in DECOMPOSITION
- [ ] When feature complete → update status in DECOMPOSITION (→ IMPLEMENTED)

### Featstatus

- [ ] FEATURE defines a `featstatus` ID definition directly under the H1 title (before `## Feature Context`)
- [ ] Template: `cpt-{system}-featstatus-{feature-slug}`
- [ ] The `featstatus` checkbox MUST be consistent with all task-tracked items within its scope:
  - If `featstatus` is `[x]` then ALL nested task-tracked ID definitions AND ALL task-checkbox references within its content MUST be `[x]`
  - If ALL nested task-tracked ID definitions AND ALL task-checkbox references within its content are `[x]` then `featstatus` MUST be `[x]`
- [ ] `featstatus` is a documentation/status rollup marker (it is not a `to_code` identifier kind)

### Checkbox Management

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

### Deliberate Omissions (MUST NOT HAVE)

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

---

## Tasks

### Phase 1: Setup

- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/task-crud.md` for reference style
- [ ] Read DECOMPOSITION to get feature ID and context
- [ ] Read DESIGN to understand domain types and components
- [ ] Read `{cypilot_path}/config/artifacts.toml` to determine FEATURE artifact path

**FEATURE path resolution**:
- Read system's `artifacts_dir` from `artifacts.toml` (default: `architecture`)
- Use kit's default subdirectory for FEATUREs: `features/`

### Phase 2: Content Creation

**CDSL instruction generation:**
- [ ] Each instruction has phase marker: `\`pN\``
- [ ] Each instruction has unique inst ID: `\`inst-{slug}\``
- [ ] Instructions describe what, not how
- [ ] Use **IF**, **RETURN**, **FROM/TO/WHEN** keywords for control flow
- [ ] Nested instructions for conditional branches

### Phase 3: IDs and Structure

- [ ] Generate flow IDs: `cpt-{system}-flow-{feature-slug}-{slug}`
- [ ] Generate algorithm IDs: `cpt-{system}-algo-{feature-slug}-{slug}`
- [ ] Generate state IDs: `cpt-{system}-state-{feature-slug}-{slug}`
- [ ] Generate DoD IDs: `cpt-{system}-dod-{feature-slug}-{slug}`
- [ ] Assign priorities (`p1`-`p9`) based on feature priority
- [ ] Verify ID uniqueness with `cypilot list-ids`

### Phase 4: Quality Check

- [ ] Compare CDSL style to `examples/task-crud.md`
- [ ] Self-review against `checklist.md` MUST HAVE items
- [ ] Ensure no MUST NOT HAVE violations
- [ ] Verify parent feature reference exists

---

## Validation

### Phase 1: Structural Validation (Deterministic)

- [ ] Run `cypilot validate --artifact <path>` for:
  - Template structure compliance
  - ID format validation
  - Priority markers present
  - CDSL instruction format
  - No placeholders
  - Parent feature reference validity

### Phase 2: Semantic Validation (Checklist-based)

Apply `checklist.md` systematically:
1. For each MUST HAVE item: check if requirement is met
2. For each MUST NOT HAVE item: scan document for violations
3. Use example for quality baseline

### Phase 3: Traceability Validation (if FULL mode)

For IDs with `to_code="true"`:
- [ ] Verify code markers exist: `@cpt-{kind}:{cpt-id}:p{N}`
- [ ] Report missing markers
- [ ] Report orphaned markers

### Phase 4: Validation Report

```
FEATURE Validation Report
═══════════════════════════

Structural: PASS/FAIL
Semantic: PASS/FAIL (N issues)

Issues:
- [SEVERITY] CHECKLIST-ID: Description
```

### Phase 5: Applicability Context

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

### Phase 6: Report Format

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

### Phase 7: Reporting Commitment

- [ ] I reported all issues I found
- [ ] I used the exact report format defined in this checklist (no deviations)
- [ ] I included Why Applicable justification for each issue
- [ ] I included evidence and impact for each issue
- [ ] I proposed concrete fixes for each issue
- [ ] I did not hide or omit known problems
- [ ] I verified explicit handling for all major checklist categories
- [ ] I am ready to iterate on the proposals and re-review after changes

---

## Error Handling

### Missing Decomposition

- [ ] Option 1: Run `/cypilot-generate DECOMPOSITION` first (recommended)
- [ ] Option 2: Continue without manifest (FEATURE will lack traceability)

### Missing Design

- [ ] Option 1: Run `/cypilot-generate DESIGN` first (recommended for architectural context)
- [ ] Option 2: Continue without DESIGN (reduced domain model context)
  - Document "DESIGN pending" in FEATURE frontmatter
  - Skip component/type references validation
  - Plan to update when DESIGN available

### Missing Parent

- [ ] Verify feature ID: `cpt-{system}-feature-{slug}`
- [ ] If new feature: add to DECOMPOSITION first
- [ ] If typo: correct the ID reference

### Escalation

- [ ] Ask user when flow complexity requires domain expertise
- [ ] Ask user when algorithm correctness uncertain
- [ ] Ask user when state transitions ambiguous

---

## Next Steps

### Options

- [ ] FEATURE design complete → `/cypilot-generate CODE` — implement feature
- [ ] Code implementation done → `/cypilot-analyze CODE` — validate implementation
- [ ] Feature IMPLEMENTED → update status in DECOMPOSITION
- [ ] Another feature to design → `/cypilot-generate FEATURE` — design next feature
- [ ] Want checklist review only → `/cypilot-analyze semantic` — semantic validation
