# FEATURE Rules

**Artifact**: FEATURE (Feature Design Document)
**Purpose**: Rules for FEATURE design generation and validation

**Dependencies**:
- `template.md` — required structure
- `checklist.md` — semantic quality criteria
- `examples/example.md` — reference implementation
- `{FDD}/requirements/template.md` — FDD template marker syntax specification

---

## Requirements

Agent confirms understanding of requirements:

### Structural Requirements

- [ ] FEATURE follows `template.md` structure
- [ ] **DO NOT copy `fdd-template:` frontmatter** — that is template metadata only
- [ ] Artifact frontmatter (optional): use `fdd:` format for document metadata
- [ ] References parent feature from FEATURES manifest
- [ ] All flows, algorithms, states, requirements have unique IDs
- [ ] All IDs follow `fdd-{project}-feature-{feature}-{kind}-{slug}` pattern
- [ ] All IDs have priority markers (`p1`-`p9`)
- [ ] FDL instructions follow format: `N. [ ] - \`ph-N\` - Description - \`inst-slug\``
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate IDs within document

### Versioning Requirements

- [ ] When editing existing FEATURE: increment version in frontmatter
- [ ] When flow/algorithm/requirement significantly changes: add `-v{N}` suffix to ID
- [ ] Format: `fdd-{project}-feature-{feature}-flow-{slug}-v2`
- [ ] Keep changelog of significant changes
- [ ] Versioning code markers must match: `@fdd-flow:{id}-v2:ph-{N}`

### Semantic Requirements

**Reference**: `checklist.md` for detailed criteria

- [ ] Actor flows define complete user journeys
- [ ] Algorithms specify processing logic clearly
- [ ] State machines capture all valid transitions
- [ ] Requirements are testable and traceable
- [ ] FDL instructions describe "what" not "how"
- [ ] Control flow keywords used correctly (IF, RETURN, FROM/TO/WHEN)

### Traceability Requirements

- [ ] All IDs with `to_code="true"` must be traced to code
- [ ] Code must contain markers: `@fdd-{kind}:{id}:ph-{N}`
- [ ] Each FDL instruction maps to code marker

### Upstream Traceability

- [ ] When all flows/algorithms/requirements `[x]` → mark feature as `[x]` in FEATURES manifest
- [ ] When feature complete → update status in FEATURES manifest (→ IMPLEMENTED)

---

## Tasks

Agent executes tasks during generation:

### Phase 1: Setup

- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read FEATURES manifest to get feature ID and context
- [ ] Read DESIGN to understand domain types and components

### Phase 2: Content Creation

**Use example as reference for FDL style:**

| Section | Example Reference | Checklist Guidance |
|---------|-------------------|-------------------|
| Actor Flows | How example structures flows | FEATURE-001: Flow Completeness |
| Algorithms | How example defines algorithms | FEATURE-002: Algorithm Clarity |
| State Machines | How example documents states | FEATURE-003: State Coverage |
| Requirements | How example links requirements | FEATURE-004: Requirement Traceability |

**FDL instruction generation:**
- [ ] Each instruction has phase marker: `\`ph-N\``
- [ ] Each instruction has unique inst ID: `\`inst-{slug}\``
- [ ] Instructions describe what, not how
- [ ] Use **IF**, **RETURN**, **FROM/TO/WHEN** keywords for control flow
- [ ] Nested instructions for conditional branches

### Phase 3: IDs and Structure

- [ ] Generate flow IDs: `fdd-{project}-feature-{feature}-flow-{slug}`
- [ ] Generate algorithm IDs: `fdd-{project}-feature-{feature}-algo-{slug}`
- [ ] Generate state IDs: `fdd-{project}-feature-{feature}-state-{slug}`
- [ ] Generate requirement IDs: `fdd-{project}-feature-{feature}-req-{slug}`
- [ ] Assign priorities (`p1`-`p9`) based on feature priority
- [ ] Verify ID uniqueness with `fdd list-ids`

### Phase 4: Quality Check

- [ ] Compare FDL style to `examples/example.md`
- [ ] Self-review against `checklist.md` MUST HAVE items
- [ ] Ensure no MUST NOT HAVE violations
- [ ] Verify parent feature reference exists

---

## Validation

Validation workflow applies rules in two phases:

### Phase 1: Structural Validation (Deterministic)

Run `fdd validate` for:
- [ ] Template structure compliance
- [ ] ID format validation
- [ ] Priority markers present
- [ ] FDL instruction format
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
- Compare FDL instruction quality to `examples/example.md`
- Verify flow/algorithm completeness

### Phase 3: Traceability Validation (if FULL mode)

For IDs with `to_code="true"`:
- [ ] Verify code markers exist: `@fdd-{kind}:{id}:ph-{N}`
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
| FEATURE design complete | `/fdd-generate CODE` — implement feature |
| Code implementation done | `/fdd-validate CODE` — validate implementation |
| Feature IMPLEMENTED | Update status in FEATURES manifest |
| Another feature to design | `/fdd-generate FEATURE` — design next feature |
| FEATURE needs revision | Continue editing FEATURE design |
