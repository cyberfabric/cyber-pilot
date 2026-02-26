# FEATURE Rules

**Artifact**: FEATURE (Feature Design Document)
**Purpose**: Rules for FEATURE design generation and validation

---

## Table of Contents

- [FEATURE Rules](#feature-rules)
  - [Table of Contents](#table-of-contents)
  - [Requirements](#requirements)
    - [Structural Requirements](#structural-requirements)
    - [Versioning Requirements](#versioning-requirements)
    - [Semantic Requirements](#semantic-requirements)
    - [Traceability Requirements](#traceability-requirements)
    - [Constraints (`constraints.json`) — Mandatory](#constraints-constraintsjson--mandatory)
    - [FEATURE Scope Guidelines](#feature-scope-guidelines)
    - [Upstream Traceability](#upstream-traceability)
    - [Feature Status (`featstatus`)](#feature-status-featstatus)
    - [Checkbox Management (`to_code` Attribute)](#checkbox-management-to_code-attribute)
  - [Tasks](#tasks)
    - [Phase 1: Setup](#phase-1-setup)
    - [Phase 2: Content Creation](#phase-2-content-creation)
    - [Phase 3: IDs and Structure](#phase-3-ids-and-structure)
    - [Phase 4: Quality Check](#phase-4-quality-check)
  - [Validation](#validation)
    - [Phase 1: Structural Validation (Deterministic)](#phase-1-structural-validation-deterministic)
    - [Phase 2: Semantic Validation (Checklist-based)](#phase-2-semantic-validation-checklist-based)
    - [Phase 3: Traceability Validation (if FULL mode)](#phase-3-traceability-validation-if-full-mode)
    - [Validation Report](#validation-report)
  - [Next Steps](#next-steps)

---

**Dependencies**:
- `template.md` — required structure
- `checklist.md` — semantic quality criteria
- `examples/example.md` — reference implementation
- `{cypilot_path}/.core/requirements/identifiers.md` — ID formats and naming
- `../../constraints.json` — kit-level constraints (primary rules for ID definitions/references)
- `{cypilot_path}/.core/requirements/kit-constraints.md` — constraints specification
- `{cypilot_path}/.core/schemas/kit-constraints.schema.json` — constraints JSON Schema

---

## Requirements

Agent confirms understanding of requirements:

### Structural Requirements

- [ ] FEATURE follows `template.md` structure
- [ ] Artifact frontmatter (optional): use `cpt:` format for document metadata
- [ ] References parent feature from DECOMPOSITION manifest
- [ ] All flows, algorithms, states, DoD items have unique IDs
- [ ] All IDs follow `cpt-{system}-{kind}-{slug}` pattern (see artifacts.toml for hierarchy)
- [ ] All IDs have priority markers (`p1`-`p9`) when required by constraints
- [ ] CDSL instructions follow format: `N. [ ] - \`pN\` - Description - \`inst-slug\``
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs within document

### Versioning Requirements

- [ ] When editing existing FEATURE: increment version in frontmatter
- [ ] When flow/algo/state/dod significantly changes: add `-v{N}` suffix to ID
- [ ] Format: `cpt-{system}-{kind}-{slug}-v2`
- [ ] Keep changelog of significant changes
- [ ] Versioning code markers must match: `@cpt-{kind}:cpt-{system}-{kind}-{slug}-v2:p{N}`
- [ ] If you want to keep feature ownership obvious, include the feature slug in `{slug}` (example: `algo-cli-control-handle-command`)

### Semantic Requirements

**Reference**: `checklist.md` for detailed criteria

- [ ] Actor flows define complete user journeys
- [ ] Algorithms specify processing logic clearly
- [ ] State machines capture all valid transitions
- [ ] DoD items are testable and traceable
- [ ] CDSL instructions describe "what" not "how"
- [ ] Control flow keywords used correctly (IF, RETURN, FROM/TO/WHEN)

### Traceability Requirements

- [ ] All IDs with `to_code="true"` must be traced to code
- [ ] Code must contain markers: `@cpt-{kind}:{cpt-id}:p{N}`
- [ ] Each CDSL instruction maps to code marker

### Constraints (`constraints.json`) — Mandatory

- [ ] ALWAYS open and follow `../../constraints.json` (kit root)
- [ ] Treat `constraints.json` as primary validator for:
  - where IDs are defined
  - where IDs are referenced
  - which cross-artifact references are required / optional / prohibited

**References**:
- `{cypilot_path}/.core/requirements/kit-constraints.md`
- `{cypilot_path}/.core/schemas/kit-constraints.schema.json`

### FEATURE Scope Guidelines

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

### Feature Status (`featstatus`)

- [ ] FEATURE defines a `featstatus` ID definition directly under the H1 title (before `## Feature Context`)
- [ ] Template: `cpt-{system}-featstatus-{feature-slug}`
- [ ] The `featstatus` checkbox MUST be consistent with all task-tracked items within its scope:
  - If `featstatus` is `[x]` then ALL nested task-tracked ID definitions AND ALL task-checkbox references within its content MUST be `[x]`
  - If ALL nested task-tracked ID definitions AND ALL task-checkbox references within its content are `[x]` then `featstatus` MUST be `[x]`
- [ ] `featstatus` is a documentation/status rollup marker (it is not a `to_code` identifier kind)

### Checkbox Management (`to_code` Attribute)

**Quick Reference**: Check FEATURE element when ALL code markers for that element exist and implementation verified.

| ID kind (defined in `constraints.json`) | Check when... |
|---------|---------------|
| `flow` | ALL `@cpt-flow:cpt-{system}-flow-{feature-slug}-{slug}:p{N}` markers exist in code |
| `algo` | ALL `@cpt-algo:cpt-{system}-algo-{feature-slug}-{slug}:p{N}` markers exist in code |
| `state` | ALL `@cpt-state:cpt-{system}-state-{feature-slug}-{slug}:p{N}` markers exist in code |
| `dod` | Implementation complete AND tests pass |

**Detailed Rules**:

FEATURE defines identifier kinds with `to_code: true` in `constraints.json` that track code implementation:

| Kind | `to_code` | Meaning |
|---------|-----------|---------|
| `flow` | `true` | Flow is checked when code markers exist and implementation verified |
| `algo` | `true` | Algorithm is checked when code markers exist and implementation verified |
| `state` | `true` | State machine is checked when code markers exist and implementation verified |
| `dod` | `true` | DoD item is checked when implementation complete and tests pass |

**Checkbox States**:

1. **Flow Checkbox** (kind: `flow`):
   - `[ ] **ID**: cpt-{system}-flow-{feature-slug}-{slug}` — unchecked until implemented
   - `[x] **ID**: cpt-{system}-flow-{feature-slug}-{slug}` — checked when ALL code markers `@cpt-flow:cpt-{system}-flow-{feature-slug}-{slug}:p{N}` exist

2. **Algorithm Checkbox** (kind: `algo`):
   - `[ ] **ID**: cpt-{system}-algo-{feature-slug}-{slug}` — unchecked until implemented
   - `[x] **ID**: cpt-{system}-algo-{feature-slug}-{slug}` — checked when ALL code markers `@cpt-algo:cpt-{system}-algo-{feature-slug}-{slug}:p{N}` exist

3. **State Machine Checkbox** (kind: `state`):
   - `[ ] **ID**: cpt-{system}-state-{feature-slug}-{slug}` — unchecked until implemented
   - `[x] **ID**: cpt-{system}-state-{feature-slug}-{slug}` — checked when ALL code markers `@cpt-state:cpt-{system}-state-{feature-slug}-{slug}:p{N}` exist

4. **DoD Checkbox** (kind: `dod`):
   - `[ ] p1 - cpt-{system}-dod-{feature-slug}-{slug}` — unchecked until satisfied
   - `[x] p1 - cpt-{system}-dod-{feature-slug}-{slug}` — checked when implementation complete and tests pass

**Cross-Artifact References**:

FEATURE references elements from PRD and DESIGN:

| Reference Type | Source Artifact | Purpose |
|----------------|-----------------|---------|
| Parent feature ID | DECOMPOSITION | Links to parent feature in manifest |
| Actor ID reference (`cpt-{system}-actor-{slug}`) | PRD | Identifies actors involved in flows |
| FR ID reference (`cpt-{system}-fr-{slug}`) | PRD | Covers functional requirement |
| NFR ID reference (`cpt-{system}-nfr-{slug}`) | PRD | Covers non-functional requirement |
| Principle ID reference (`cpt-{system}-principle-{slug}`) | DESIGN | Applies design principle |
| Constraint ID reference (`cpt-{system}-constraint-{slug}`) | DESIGN | Satisfies design constraint |
| Component ID reference (`cpt-{system}-component-{slug}`) | DESIGN | Uses design component |
| Sequence ID reference (`cpt-{system}-seq-{slug}`) | DESIGN | Implements sequence diagram |
| Data ID reference (`cpt-{system}-dbtable-{slug}`) | DESIGN | Uses database table |

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

---

## Tasks

Agent executes tasks during generation:

### Phase 1: Setup

- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read DECOMPOSITION to get feature ID and context
- [ ] Read DESIGN to understand domain types and components
- [ ] Read adapter `artifacts.toml` to determine FEATURE artifact path
- [ ] Read adapter `specs/project-structure.md` (if exists) for directory conventions

**FEATURE path resolution**:
1. Check if FEATURE with matching slug already registered in `artifacts` array
2. If found, use registered path (it's a FULL path relative to `project_root`)
3. If not found, derive default path:
   - Read system's `artifacts_dir` from `artifacts.toml` (default: `architecture`)
   - Use kit's default subdirectory for FEATUREs: `specs/` (temporary compatibility)
   - Create at: `{artifacts_dir}/specs/{slug}.md`

**If DECOMPOSITION not found**:
```
⚠ DECOMPOSITION not found
→ Option 1: Run /cypilot-generate DECOMPOSITION first (recommended)
→ Option 2: Continue without manifest (FEATURE will lack traceability)
   - Document "DECOMPOSITION pending" in FEATURE frontmatter
   - Skip parent feature reference validation
   - Plan to update when DECOMPOSITION available
```

**If DESIGN not found or incomplete**:
```
⚠ DESIGN not found or incomplete
→ Option 1: Run /cypilot-generate DESIGN first (recommended for architectural context)
→ Option 2: Continue without DESIGN (reduced domain model context)
   - Document "DESIGN pending" in FEATURE frontmatter
   - Skip component/type references validation
   - Plan to update when DESIGN available
```

**If parent feature not in DECOMPOSITION**:
```
⚠ Parent feature ID not found in DECOMPOSITION
→ Verify feature ID: cpt-{system}-feature-{slug}
→ If new feature: add to DECOMPOSITION first
→ If typo: correct the ID reference
```

### Phase 2: Content Creation

**Use example as reference for CDSL style:**

| Section | Example Reference | Checklist Guidance |
|---------|-------------------|-------------------|
| Flows | How example structures flows | Flow Completeness |
| Algorithms | How example defines algorithms | Algorithm Clarity |
| States | How example documents states | State Coverage |
| DoD | How example links DoD items | DoD Traceability |

**CDSL instruction generation:**
- [ ] Each instruction has phase marker: `\`pN\``
- [ ] Each instruction has unique inst ID: `\`inst-{slug}\``
- [ ] Instructions describe what, not how
- [ ] Use **IF**, **RETURN**, **FROM/TO/WHEN** keywords for control flow
- [ ] Nested instructions for conditional branches

**Partial Completion Handling**:

If FEATURE cannot be completed in a single session:

1. **Checkpoint progress**:
   - Note completed sections (Flows, Algorithms, States, Requirements, Tests)
   - Note current section being worked on
   - List remaining sections
2. **Ensure valid intermediate state**:
   - All completed flows/algorithms must be internally consistent
   - Add `status: DRAFT` to frontmatter
   - Mark incomplete sections with `<!-- INCOMPLETE: {reason} -->`
3. **Document resumption point**:
   ```
   FEATURE checkpoint:
   - Completed: Actor Flows (3/3), Algorithms (2/4)
   - In progress: Algorithm cpt-{system}-algo-{slug}
   - Remaining: States, DoD, Test Scenarios
   - Resume: Continue with algorithm definition
   ```
4. **On resume**:
   - Verify DECOMPOSITION unchanged since last session
   - Verify DESIGN unchanged since last session
   - Continue from documented checkpoint
   - Remove incomplete markers as sections are finished

### Phase 3: IDs and Structure

- [ ] Generate flow IDs: `cpt-{system}-flow-{slug}`
- [ ] Generate algorithm IDs: `cpt-{system}-algo-{slug}`
- [ ] Generate state IDs: `cpt-{system}-state-{slug}`
- [ ] Generate DoD IDs: `cpt-{system}-dod-{slug}`
- [ ] Assign priorities (`p1`-`p9`) based on feature priority
- [ ] Verify ID uniqueness with `cypilot list-ids`

### Phase 4: Quality Check

- [ ] Compare CDSL style to `examples/example.md`
- [ ] Self-review against `checklist.md` MUST HAVE items
- [ ] Ensure no MUST NOT HAVE violations
- [ ] Verify parent feature reference exists

---

## Validation

Validation workflow applies rules in two phases:

### Phase 1: Structural Validation (Deterministic)

Run `cypilot validate` for:
- [ ] Template structure compliance
- [ ] ID format validation
- [ ] Priority markers present
- [ ] CDSL instruction format
- [ ] No placeholders
- [ ] Parent feature reference validity

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
- Compare CDSL instruction quality to `examples/example.md`
- Verify flow/algorithm completeness

### Phase 3: Traceability Validation (if FULL mode)

For IDs with `to_code="true"`:
- [ ] Verify code markers exist: `@cpt-{kind}:{cpt-id}:p{N}`
- [ ] Report missing markers
- [ ] Report orphaned markers

### Validation Report

Output format:
```
FEATURE Validation Report
═════════════════════════

Structural: PASS/FAIL
Semantic: PASS/FAIL (N issues)
Traceability: PASS/FAIL (coverage: N%)

Issues:
- [SEVERITY] CHECKLIST-ID: Description
```

---

## Next Steps

After FEATURE generation/validation, offer these options:

| Condition | Suggested Next Step |
|-----------|---------------------|
| FEATURE design complete | `/cypilot-generate CODE` — implement feature |
| Code implementation done | `/cypilot-analyze CODE` — validate implementation |
| Feature IMPLEMENTED | Update status in DECOMPOSITION |
| Another feature to design | `/cypilot-generate FEATURE` — design next feature |
| FEATURE needs revision | Continue editing FEATURE design |
| Want checklist review only | `/cypilot-analyze semantic` — semantic validation (skip deterministic) |
