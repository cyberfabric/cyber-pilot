# FEATURE Rules

**Artifact**: FEATURE (Feature Design Document)
**Purpose**: Rules for FEATURE design generation and validation

---

## Table of Contents

1. [Requirements](#requirements)
   - [Structural Requirements](#structural-requirements)
   - [Versioning Requirements](#versioning-requirements)
   - [Semantic Requirements](#semantic-requirements)
   - [Traceability Requirements](#traceability-requirements)
   - [FEATURE Scope Guidelines](#feature-scope-guidelines)
   - [Upstream Traceability](#upstream-traceability)
   - [Checkbox Management](#checkbox-management-to_code-attribute)
2. [Tasks](#tasks)
   - [Phase 1: Setup](#phase-1-setup)
   - [Phase 2: Content Creation](#phase-2-content-creation)
   - [Phase 3: IDs and Structure](#phase-3-ids-and-structure)
   - [Phase 4: Quality Check](#phase-4-quality-check)
3. [Validation](#validation)
4. [Next Steps](#next-steps)

---

**Dependencies**:
- `template.md` — required structure
- `checklist.md` — semantic quality criteria
- `examples/example.md` — reference implementation
- `{Spider}/requirements/template.md` — Spider template marker syntax specification

---

## Requirements

Agent confirms understanding of requirements:

### Structural Requirements

- [ ] FEATURE follows `template.md` structure
- [ ] **DO NOT copy `spider-template:` frontmatter** — that is template metadata only
- [ ] Artifact frontmatter (optional): use `spd:` format for document metadata
- [ ] References parent feature from DECOMPOSITION manifest
- [ ] All flows, algorithms, states, requirements have unique IDs
- [ ] All IDs follow `spd-{system}-feature-{feature}-{kind}-{slug}` pattern
- [ ] All IDs have priority markers (`p1`-`p9`)
- [ ] SDSL instructions follow format: `N. [ ] - \`ph-N\` - Description - \`inst-slug\``
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs within document

### Versioning Requirements

- [ ] When editing existing FEATURE: increment version in frontmatter
- [ ] When flow/algorithm/requirement significantly changes: add `-v{N}` suffix to ID
- [ ] Format: `spd-{system}-feature-{feature}-flow-{slug}-v2`
- [ ] Keep changelog of significant changes
- [ ] Versioning code markers must match: `@spider-flow:{spd-id}-v2:p{N}`

### Semantic Requirements

**Reference**: `checklist.md` for detailed criteria

- [ ] Actor flows define complete user journeys
- [ ] Algorithms specify processing logic clearly
- [ ] State machines capture all valid transitions
- [ ] Requirements are testable and traceable
- [ ] SDSL instructions describe "what" not "how"
- [ ] Control flow keywords used correctly (IF, RETURN, FROM/TO/WHEN)

### Traceability Requirements

- [ ] All IDs with `to_code="true"` must be traced to code
- [ ] Code must contain markers: `@spider-{kind}:{spd-id}:p{N}`
- [ ] Each SDSL instruction maps to code marker

### FEATURE Scope Guidelines

**One FEATURE per feature from DECOMPOSITION manifest**. Match scope to implementation unit.

| Scope | Examples | Guideline |
|-------|----------|-----------|
| **Too broad** | "User management feature" covering auth, profiles, roles | Split into separate FEATUREs |
| **Right size** | "User login flow" covering single capability | Clear boundary, implementable unit |
| **Too narrow** | "Validate email format" | Implementation detail, belongs in flow/algorithm |

**FEATURE-worthy content**:
- Actor flows (complete user journeys)
- Algorithms (processing logic)
- State machines (entity lifecycle)
- Feature-specific requirements
- Test scenarios

**NOT FEATURE-worthy** (use other artifacts):
- System architecture → DESIGN
- Technology decisions → ADR
- Business requirements → PRD
- Multiple unrelated capabilities → Split into FEATUREs

**Relationship to other artifacts**:
- **FEATURES** → FEATURE: DECOMPOSITION lists what to build, FEATURE details how
- **DESIGN** → FEATURE: DESIGN provides architecture context, FEATURE details implementation
- **FEATURE** → CODE: FEATURE defines behavior, CODE implements with traceability markers

### Upstream Traceability

- [ ] When all flows/algorithms/requirements `[x]` → mark feature as `[x]` in DECOMPOSITION
- [ ] When feature complete → update status in DECOMPOSITION (→ IMPLEMENTED)

### Checkbox Management (`to_code` Attribute)

**Quick Reference**: Check FEATURE element when ALL code markers for that element exist and implementation verified.

| Element | Check when... |
|---------|---------------|
| `id:flow` | ALL `@spider-flow:{spd-id}:p{N}` markers exist in code |
| `id:algo` | ALL `@spider-algo:{spd-id}:p{N}` markers exist in code |
| `id:state` | ALL `@spider-state:{spd-id}:p{N}` markers exist in code |
| `id:req` | Implementation complete AND tests pass |

**Detailed Rules**:

FEATURE defines IDs with `to_code="true"` attribute that track code implementation:

| ID Type | `to_code` | Meaning |
|---------|-----------|---------|
| `id:flow` | `true` | Flow is checked when code markers exist and implementation verified |
| `id:algo` | `true` | Algorithm is checked when code markers exist and implementation verified |
| `id:state` | `true` | State machine is checked when code markers exist and implementation verified |
| `id:req` | `true` | Requirement is checked when code markers exist and tests pass |

**Checkbox States**:

1. **Flow Checkbox** (`id:flow`):
   - `[ ] - spd-{system}-feature-{feature}-flow-{slug}` — unchecked until implemented
   - `[x] - spd-{system}-feature-{feature}-flow-{slug}` — checked when ALL code markers `@spider-flow:{spd-id}:p{N}` exist

2. **Algorithm Checkbox** (`id:algo`):
   - `[ ] - spd-{system}-feature-{feature}-algo-{slug}` — unchecked until implemented
   - `[x] - spd-{system}-feature-{feature}-algo-{slug}` — checked when ALL code markers `@spider-algo:{spd-id}:p{N}` exist

3. **State Machine Checkbox** (`id:state`):
   - `[ ] - spd-{system}-feature-{feature}-state-{slug}` — unchecked until implemented
   - `[x] - spd-{system}-feature-{feature}-state-{slug}` — checked when ALL code markers `@spider-state:{spd-id}:p{N}` exist

4. **Requirement Checkbox** (`id:req`):
   - `[ ] p1 - spd-{system}-feature-{feature}-req-{slug}` — unchecked until satisfied
   - `[x] p1 - spd-{system}-feature-{feature}-req-{slug}` — checked when implementation complete and tests pass

**Cross-Artifact References (`id-ref`)**:

FEATURE references elements from PRD and DESIGN:

| Reference Type | Source Artifact | Purpose |
|----------------|-----------------|---------|
| `id-ref:feature` | DECOMPOSITION | Links to parent feature in manifest |
| `id-ref:actor` | PRD | Identifies actors involved in flows |
| `id-ref:fr` | PRD | Covers functional requirement |
| `id-ref:nfr` | PRD | Covers non-functional requirement |
| `id-ref:principle` | DESIGN | Applies design principle |
| `id-ref:constraint` | DESIGN | Satisfies design constraint |
| `id-ref:component` | DESIGN | Uses design component |
| `id-ref:seq` | DESIGN | Implements sequence diagram |
| `id-ref:dbtable` | DESIGN | Uses database table |

**When to Update Upstream Artifacts**:

- [ ] When `id:flow` is checked → verify all SDSL instructions have code markers
- [ ] When `id:algo` is checked → verify algorithm logic is implemented
- [ ] When `id:state` is checked → verify all transitions are implemented
- [ ] When `id:req` is checked → verify requirement is satisfied and tested
- [ ] When ALL `id:*` in FEATURE are `[x]` → mark `id-ref:feature` as `[x]` in DECOMPOSITION
- [ ] When feature is `[x]` → update upstream `id-ref` checkboxes in DECOMPOSITION (which cascades to PRD/DESIGN)

**Validation Checks**:
- `spider validate` will warn if `to_code="true"` ID has no code markers
- `spider validate` will warn if `id-ref` references non-existent ID
- `spider validate` will report code coverage: N% of SDSL instructions have markers

---

## Tasks

Agent executes tasks during generation:

### Phase 1: Setup

- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read DECOMPOSITION to get feature ID and context
- [ ] Read DESIGN to understand domain types and components

**If DECOMPOSITION not found**:
```
⚠ DECOMPOSITION not found
→ Option 1: Run /spider-generate DECOMPOSITION first (recommended)
→ Option 2: Continue without manifest (FEATURE will lack traceability)
   - Document "DECOMPOSITION pending" in FEATURE frontmatter
   - Skip parent feature reference validation
   - Plan to update when DECOMPOSITION available
```

**If DESIGN not found or incomplete**:
```
⚠ DESIGN not found or incomplete
→ Option 1: Run /spider-generate DESIGN first (recommended for architectural context)
→ Option 2: Continue without DESIGN (reduced domain model context)
   - Document "DESIGN pending" in FEATURE frontmatter
   - Skip component/type references validation
   - Plan to update when DESIGN available
```

**If parent feature not in DECOMPOSITION**:
```
⚠ Parent feature ID not found in DECOMPOSITION
→ Verify feature ID: spd-{system}-feature-{slug}
→ If new feature: add to DECOMPOSITION first
→ If typo: correct the ID reference
```

### Phase 2: Content Creation

**Use example as reference for SDSL style:**

| Section | Example Reference | Checklist Guidance |
|---------|-------------------|-------------------|
| Actor Flows | How example structures flows | FEATURE-001: Flow Completeness |
| Algorithms | How example defines algorithms | FEATURE-002: Algorithm Clarity |
| State Machines | How example documents states | FEATURE-003: State Coverage |
| Requirements | How example links requirements | FEATURE-004: Requirement Traceability |

**SDSL instruction generation:**
- [ ] Each instruction has phase marker: `\`ph-N\``
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
   - In progress: Algorithm spd-{system}-feature-{feature}-algo-{slug}
   - Remaining: State Machines, Requirements, Test Scenarios
   - Resume: Continue with algorithm definition
   ```
4. **On resume**:
   - Verify DECOMPOSITION unchanged since last session
   - Verify DESIGN unchanged since last session
   - Continue from documented checkpoint
   - Remove incomplete markers as sections are finished

### Phase 3: IDs and Structure

- [ ] Generate flow IDs: `spd-{system}-feature-{feature}-flow-{slug}`
- [ ] Generate algorithm IDs: `spd-{system}-feature-{feature}-algo-{slug}`
- [ ] Generate state IDs: `spd-{system}-feature-{feature}-state-{slug}`
- [ ] Generate requirement IDs: `spd-{system}-feature-{feature}-req-{slug}`
- [ ] Assign priorities (`p1`-`p9`) based on feature priority
- [ ] Verify ID uniqueness with `spider list-ids`

### Phase 4: Quality Check

- [ ] Compare SDSL style to `examples/example.md`
- [ ] Self-review against `checklist.md` MUST HAVE items
- [ ] Ensure no MUST NOT HAVE violations
- [ ] Verify parent feature reference exists

---

## Validation

Validation workflow applies rules in two phases:

### Phase 1: Structural Validation (Deterministic)

Run `spider validate` for:
- [ ] Template structure compliance
- [ ] ID format validation
- [ ] Priority markers present
- [ ] SDSL instruction format
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
- Compare SDSL instruction quality to `examples/example.md`
- Verify flow/algorithm completeness

### Phase 3: Traceability Validation (if FULL mode)

For IDs with `to_code="true"`:
- [ ] Verify code markers exist: `@spider-{kind}:{spd-id}:p{N}`
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
| FEATURE design complete | `/spider-generate CODE` — implement feature |
| Code implementation done | `/spider-validate CODE` — validate implementation |
| Feature IMPLEMENTED | Update status in DECOMPOSITION |
| Another feature to design | `/spider-generate FEATURE` — design next feature |
| FEATURE needs revision | Continue editing FEATURE design |
| Want checklist review only | `/spider-validate semantic` — semantic validation (skip deterministic) |
