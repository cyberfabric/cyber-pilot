# SPEC Rules

**Artifact**: SPEC (Spec Design Document)
**Purpose**: Rules for SPEC design generation and validation

---

## Table of Contents

1. [Requirements](#requirements)
   - [Structural Requirements](#structural-requirements)
   - [Versioning Requirements](#versioning-requirements)
   - [Semantic Requirements](#semantic-requirements)
   - [Traceability Requirements](#traceability-requirements)
   - [SPEC Scope Guidelines](#spec-scope-guidelines)
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
- `{cypilot_path}/requirements/template.md` — Cypilot template marker syntax specification

---

## Requirements

Agent confirms understanding of requirements:

### Structural Requirements

- [ ] SPEC follows `template.md` structure
- [ ] Artifact frontmatter (optional): use `cpt:` format for document metadata
- [ ] References parent spec from DECOMPOSITION manifest
- [ ] All flows, algorithms, states, requirements have unique IDs
- [ ] All IDs follow `cpt-{hierarchy-prefix}-{kind}-{slug}` pattern (see artifacts.json for hierarchy)
- [ ] All IDs have priority markers (`p1`-`p9`)
- [ ] CDSL instructions follow format: `N. [ ] - \`ph-N\` - Description - \`inst-slug\``
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs within document

### Versioning Requirements

- [ ] When editing existing SPEC: increment version in frontmatter
- [ ] When flow/algorithm/requirement significantly changes: add `-v{N}` suffix to ID
- [ ] Format: `cpt-{hierarchy-prefix}-flow-{slug}-v2`
- [ ] Keep changelog of significant changes
- [ ] Versioning code markers must match: `@cpt-flow:cpt-{hierarchy-prefix}-flow-{slug}-v2:p{N}`

### Semantic Requirements

**Reference**: `checklist.md` for detailed criteria

- [ ] Actor flows define complete user journeys
- [ ] Algorithms specify processing logic clearly
- [ ] State machines capture all valid transitions
- [ ] Requirements are testable and traceable
- [ ] CDSL instructions describe "what" not "how"
- [ ] Control flow keywords used correctly (IF, RETURN, FROM/TO/WHEN)

### Traceability Requirements

- [ ] All IDs with `to_code="true"` must be traced to code
- [ ] Code must contain markers: `@cpt-{kind}:{cpt-id}:p{N}`
- [ ] Each CDSL instruction maps to code marker

### SPEC Scope Guidelines

**One SPEC per spec from DECOMPOSITION manifest**. Match scope to implementation unit.

| Scope | Examples | Guideline |
|-------|----------|-----------|
| **Too broad** | "User management spec" covering auth, profiles, roles | Split into separate SPECs |
| **Right size** | "User login flow" covering single capability | Clear boundary, implementable unit |
| **Too narrow** | "Validate email format" | Implementation detail, belongs in flow/algorithm |

**SPEC-worthy content**:
- Actor flows (complete user journeys)
- Algorithms (processing logic)
- State machines (entity lifecycle)
- Spec-specific requirements
- Test scenarios

**NOT SPEC-worthy** (use other artifacts):
- System architecture → DESIGN
- Technology decisions → ADR
- Business requirements → PRD
- Multiple unrelated capabilities → Split into SPECs

**Relationship to other artifacts**:
- **DECOMPOSITION** → SPEC: DECOMPOSITION lists what to build, SPEC details how
- **DESIGN** → SPEC: DESIGN provides architecture context, SPEC details implementation
- **SPEC** → CODE: SPEC defines behavior, CODE implements with traceability markers

### Upstream Traceability

- [ ] When all flows/algorithms/requirements `[x]` → mark spec as `[x]` in DECOMPOSITION
- [ ] When spec complete → update status in DECOMPOSITION (→ IMPLEMENTED)

### Checkbox Management (`to_code` Attribute)

**Quick Reference**: Check SPEC element when ALL code markers for that element exist and implementation verified.

| Element | Check when... |
|---------|---------------|
| `id:flow` | ALL `@cpt-flow:{cpt-id}:p{N}` markers exist in code |
| `id:algo` | ALL `@cpt-algo:{cpt-id}:p{N}` markers exist in code |
| `id:state` | ALL `@cpt-state:{cpt-id}:p{N}` markers exist in code |
| `id:req` | Implementation complete AND tests pass |

**Detailed Rules**:

SPEC defines IDs with `to_code="true"` attribute that track code implementation:

| ID Type | `to_code` | Meaning |
|---------|-----------|---------|
| `id:flow` | `true` | Flow is checked when code markers exist and implementation verified |
| `id:algo` | `true` | Algorithm is checked when code markers exist and implementation verified |
| `id:state` | `true` | State machine is checked when code markers exist and implementation verified |
| `id:req` | `true` | Requirement is checked when code markers exist and tests pass |

**Checkbox States**:

1. **Flow Checkbox** (`id:flow`):
   - `[ ] - cpt-{hierarchy-prefix}-flow-{slug}` — unchecked until implemented
   - `[x] - cpt-{hierarchy-prefix}-flow-{slug}` — checked when ALL code markers `@cpt-flow:cpt-{hierarchy-prefix}-flow-{slug}:p{N}` exist

2. **Algorithm Checkbox** (`id:algo`):
   - `[ ] - cpt-{hierarchy-prefix}-algo-{slug}` — unchecked until implemented
   - `[x] - cpt-{hierarchy-prefix}-algo-{slug}` — checked when ALL code markers `@cpt-algo:cpt-{hierarchy-prefix}-algo-{slug}:p{N}` exist

3. **State Machine Checkbox** (`id:state`):
   - `[ ] - cpt-{hierarchy-prefix}-state-{slug}` — unchecked until implemented
   - `[x] - cpt-{hierarchy-prefix}-state-{slug}` — checked when ALL code markers `@cpt-state:cpt-{hierarchy-prefix}-state-{slug}:p{N}` exist

4. **Requirement Checkbox** (`id:req`):
   - `[ ] p1 - cpt-{hierarchy-prefix}-req-{slug}` — unchecked until satisfied
   - `[x] p1 - cpt-{hierarchy-prefix}-req-{slug}` — checked when implementation complete and tests pass

**Cross-Artifact References (`id-ref`)**:

SPEC references elements from PRD and DESIGN:

| Reference Type | Source Artifact | Purpose |
|----------------|-----------------|---------|
| `id-ref:spec` | DECOMPOSITION | Links to parent spec in manifest |
| `id-ref:actor` | PRD | Identifies actors involved in flows |
| `id-ref:fr` | PRD | Covers functional requirement |
| `id-ref:nfr` | PRD | Covers non-functional requirement |
| `id-ref:principle` | DESIGN | Applies design principle |
| `id-ref:constraint` | DESIGN | Satisfies design constraint |
| `id-ref:component` | DESIGN | Uses design component |
| `id-ref:seq` | DESIGN | Implements sequence diagram |
| `id-ref:dbtable` | DESIGN | Uses database table |

**When to Update Upstream Artifacts**:

- [ ] When `id:flow` is checked → verify all CDSL instructions have code markers
- [ ] When `id:algo` is checked → verify algorithm logic is implemented
- [ ] When `id:state` is checked → verify all transitions are implemented
- [ ] When `id:req` is checked → verify requirement is satisfied and tested
- [ ] When ALL `id:*` in SPEC are `[x]` → mark `id-ref:spec` as `[x]` in DECOMPOSITION
- [ ] When spec is `[x]` → update upstream `id-ref` checkboxes in DECOMPOSITION (which cascades to PRD/DESIGN)

**Validation Checks**:
- `cypilot validate` will warn if `to_code="true"` ID has no code markers
- `cypilot validate` will warn if `id-ref` references non-existent ID
- `cypilot validate` will report code coverage: N% of CDSL instructions have markers

---

## Tasks

Agent executes tasks during generation:

### Phase 1: Setup

- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read DECOMPOSITION to get spec ID and context
- [ ] Read DESIGN to understand domain types and components
- [ ] Read adapter `artifacts.json` to determine SPEC artifact path
- [ ] Read adapter `specs/project-structure.md` (if exists) for directory conventions

**SPEC path resolution**:
1. Check if SPEC with matching slug already registered in `artifacts` array
2. If found, use registered path (it's a FULL path relative to `project_root`)
3. If not found, derive default path:
   - Read system's `artifacts_dir` from `artifacts.json` (default: `architecture`)
   - Use kit's default subdirectory for SPECs: `specs/`
   - Create at: `{artifacts_dir}/specs/{slug}.md`

**If DECOMPOSITION not found**:
```
⚠ DECOMPOSITION not found
→ Option 1: Run /cypilot-generate DECOMPOSITION first (recommended)
→ Option 2: Continue without manifest (SPEC will lack traceability)
   - Document "DECOMPOSITION pending" in SPEC frontmatter
   - Skip parent spec reference validation
   - Plan to update when DECOMPOSITION available
```

**If DESIGN not found or incomplete**:
```
⚠ DESIGN not found or incomplete
→ Option 1: Run /cypilot-generate DESIGN first (recommended for architectural context)
→ Option 2: Continue without DESIGN (reduced domain model context)
   - Document "DESIGN pending" in SPEC frontmatter
   - Skip component/type references validation
   - Plan to update when DESIGN available
```

**If parent spec not in DECOMPOSITION**:
```
⚠ Parent spec ID not found in DECOMPOSITION
→ Verify spec ID: cpt-{hierarchy-prefix}-spec-{slug}
→ If new spec: add to DECOMPOSITION first
→ If typo: correct the ID reference
```

### Phase 2: Content Creation

**Use example as reference for CDSL style:**

| Section | Example Reference | Checklist Guidance |
|---------|-------------------|-------------------|
| Actor Flows | How example structures flows | SPEC-001: Flow Completeness |
| Algorithms | How example defines algorithms | SPEC-002: Algorithm Clarity |
| State Machines | How example documents states | SPEC-003: State Coverage |
| Requirements | How example links requirements | SPEC-004: Requirement Traceability |

**CDSL instruction generation:**
- [ ] Each instruction has phase marker: `\`ph-N\``
- [ ] Each instruction has unique inst ID: `\`inst-{slug}\``
- [ ] Instructions describe what, not how
- [ ] Use **IF**, **RETURN**, **FROM/TO/WHEN** keywords for control flow
- [ ] Nested instructions for conditional branches

**Partial Completion Handling**:

If SPEC cannot be completed in a single session:

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
   SPEC checkpoint:
   - Completed: Actor Flows (3/3), Algorithms (2/4)
   - In progress: Algorithm cpt-{hierarchy-prefix}-algo-{slug}
   - Remaining: State Machines, Requirements, Test Scenarios
   - Resume: Continue with algorithm definition
   ```
4. **On resume**:
   - Verify DECOMPOSITION unchanged since last session
   - Verify DESIGN unchanged since last session
   - Continue from documented checkpoint
   - Remove incomplete markers as sections are finished

### Phase 3: IDs and Structure

- [ ] Generate flow IDs: `cpt-{hierarchy-prefix}-flow-{slug}` (e.g., `cpt-myapp-auth-flow-login`)
- [ ] Generate algorithm IDs: `cpt-{hierarchy-prefix}-algo-{slug}` (e.g., `cpt-myapp-auth-algo-password-hash`)
- [ ] Generate state IDs: `cpt-{hierarchy-prefix}-state-{slug}` (e.g., `cpt-myapp-auth-state-session-lifecycle`)
- [ ] Generate requirement IDs: `cpt-{hierarchy-prefix}-req-{slug}` (e.g., `cpt-myapp-auth-req-must-validate-token`)
- [ ] Assign priorities (`p1`-`p9`) based on spec priority
- [ ] Verify ID uniqueness with `cypilot list-ids`

### Phase 4: Quality Check

- [ ] Compare CDSL style to `examples/example.md`
- [ ] Self-review against `checklist.md` MUST HAVE items
- [ ] Ensure no MUST NOT HAVE violations
- [ ] Verify parent spec reference exists

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
- [ ] Parent spec reference validity

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
SPEC Validation Report
═════════════════════════

Structural: PASS/FAIL
Semantic: PASS/FAIL (N issues)
Traceability: PASS/FAIL (coverage: N%)

Issues:
- [SEVERITY] CHECKLIST-ID: Description
```

---

## Next Steps

After SPEC generation/validation, offer these options:

| Condition | Suggested Next Step |
|-----------|---------------------|
| SPEC design complete | `/cypilot-generate CODE` — implement spec |
| Code implementation done | `/cypilot-analyze CODE` — validate implementation |
| Spec IMPLEMENTED | Update status in DECOMPOSITION |
| Another spec to design | `/cypilot-generate SPEC` — design next spec |
| SPEC needs revision | Continue editing SPEC design |
| Want checklist review only | `/cypilot-analyze semantic` — semantic validation (skip deterministic) |
