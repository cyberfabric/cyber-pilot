# FEATURES Rules

**Artifact**: FEATURES (Features Manifest)
**Purpose**: Rules for FEATURES manifest generation and validation

**Dependencies**:
- `template.md` — required structure
- `checklist.md` — semantic quality criteria
- `examples/example.md` — reference implementation
- `{FDD}/requirements/template.md` — FDD template marker syntax specification

---

## Requirements

Agent confirms understanding of requirements:

### Structural Requirements

- [ ] FEATURES follows `template.md` structure
- [ ] **DO NOT copy `fdd-template:` frontmatter** — that is template metadata only
- [ ] Artifact frontmatter (optional): use `fdd:` format for document metadata
- [ ] All required sections present and non-empty
- [ ] Each feature has unique ID: `fdd-{project}-feature-{slug}`
- [ ] Each feature has priority marker (`p1`-`p9`)
- [ ] Each feature has valid status
- [ ] No placeholder content (TODO, TBD, FIXME)
- [ ] No duplicate feature IDs

### Versioning Requirements

- [ ] When editing existing FEATURES: increment version in frontmatter
- [ ] When feature scope significantly changes: add `-v{N}` suffix to feature ID
- [ ] Format: `fdd-{project}-feature-{slug}-v2`
- [ ] Keep changelog of significant changes

### Semantic Requirements

**Reference**: `checklist.md` for detailed criteria

- [ ] Status overview reflects actual feature statuses
- [ ] Features map to PRD capabilities
- [ ] Feature grouping is logical and cohesive
- [ ] Dependencies between features documented
- [ ] Status progression is valid (NOT_STARTED → IN_DESIGN → DESIGN_READY → IN_DEVELOPMENT → IMPLEMENTED)

### Upstream Traceability

- [ ] When feature status → IMPLEMENTED, mark `[x]` on feature ID
- [ ] When all features for a component IMPLEMENTED → mark component `[x]` in DESIGN
- [ ] When all features for a capability IMPLEMENTED → mark capability `[x]` in PRD

---

## Tasks

Agent executes tasks during generation:

### Phase 1: Setup

- [ ] Load `template.md` for structure
- [ ] Load `checklist.md` for semantic guidance
- [ ] Load `examples/example.md` for reference style
- [ ] Read PRD to identify capabilities to implement

### Phase 2: Content Creation

**Use example as reference for content style:**

| Section | Example Reference | Checklist Guidance |
|---------|-------------------|-------------------|
| Status Overview | How example shows status counts | FEATURES-001: Status Accuracy |
| Feature List | How example structures features | FEATURES-002: Feature Coverage |
| Dependencies | How example documents dependencies | FEATURES-003: Dependency Clarity |

### Phase 3: IDs and Structure

- [ ] Generate feature IDs: `fdd-{project}-feature-{slug}`
- [ ] Assign priorities based on PRD capability priorities
- [ ] Set initial status to NOT_STARTED
- [ ] Link to PRD capabilities implemented
- [ ] Verify uniqueness with `fdd list-ids`

### Phase 4: Quality Check

- [ ] Compare output to `examples/example.md`
- [ ] Self-review against `checklist.md` MUST HAVE items
- [ ] Ensure status overview counts are accurate
- [ ] Verify PRD capability coverage

---

## Validation

Validation workflow applies rules in two phases:

### Phase 1: Structural Validation (Deterministic)

Run `fdd validate` for:
- [ ] Template structure compliance
- [ ] ID format validation
- [ ] Priority markers present
- [ ] Valid status values
- [ ] No placeholders

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
- Compare feature descriptions to `examples/example.md`
- Verify status tracking completeness

### Validation Report

Output format:
```
FEATURES Validation Report
══════════════════════════

Structural: PASS/FAIL
Semantic: PASS/FAIL (N issues)

Issues:
- [SEVERITY] CHECKLIST-ID: Description
```

---

## Next Steps

After FEATURES generation/validation, offer these options:

| Condition | Suggested Next Step |
|-----------|---------------------|
| Features defined | `/fdd-generate FEATURE` — design first/next feature |
| Feature IMPLEMENTED | Update feature status in manifest |
| All features IMPLEMENTED | `/fdd-validate DESIGN` — validate design completion |
| New feature needed | Add to manifest, then `/fdd-generate FEATURE` |
