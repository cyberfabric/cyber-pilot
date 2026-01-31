# CODE Rules

**Target**: Codebase Implementation
**Purpose**: Rules for code generation and validation with FDD traceability

**Dependencies**:
- `checklist.md` — code quality criteria
- `{FDD}/requirements/traceability.md` — marker syntax and validation rules
- `{adapter-dir}/AGENTS.md` — project conventions
- **Source** (one of, in priority order):
  1. FEATURE design — registered artifact with `to_code="true"` IDs
  2. Other FDD artifact — PRD, DESIGN, ADR, FEATURES
  3. Similar content — user-provided description, spec, or requirements
  4. Prompt only — direct user instructions

---

## Requirements

Agent confirms understanding of requirements:

### Structural Requirements

- [ ] Code implements FEATURE design requirements
- [ ] Code follows project conventions from adapter

### Traceability Requirements

**Reference**: `{FDD}/requirements/traceability.md` for full specification

- [ ] Traceability Mode determined per spec (FULL vs DOCS-ONLY)
- [ ] If Mode ON: markers follow spec syntax (`@fdd-*`, `@fdd-begin`/`@fdd-end`)
- [ ] If Mode ON: all `to_code="true"` IDs have markers
- [ ] If Mode ON: no orphaned/stale markers
- [ ] If Mode ON: design checkboxes synced with code
- [ ] If Mode OFF: no FDD markers in code

### Versioning Requirements

- [ ] When design ID versioned (`-v2`): update code markers to match
- [ ] Marker format with version: `@fdd-flow:{id}-v2:ph-{N}`
- [ ] Migration: update all markers when design version increments
- [ ] Keep old markers commented during transition (optional)

### Engineering Best Practices (MANDATORY)

- [ ] **TDD**: Write failing test first, implement minimal code to pass, then refactor
- [ ] **SOLID**:
  - Single Responsibility: Each module/function focused on one reason to change
  - Open/Closed: Extend behavior via composition/configuration, not editing unrelated logic
  - Liskov Substitution: Implementations honor interface contract and invariants
  - Interface Segregation: Prefer small, purpose-driven interfaces over broad ones
  - Dependency Inversion: Depend on abstractions; inject dependencies for testability
- [ ] **DRY**: Remove duplication by extracting shared logic with clear ownership
- [ ] **KISS**: Prefer simplest correct solution matching design and adapter conventions
- [ ] **YAGNI**: No features/abstractions not required by current design scope
- [ ] **Refactoring discipline**: Refactor only after tests pass; keep behavior unchanged
- [ ] **Testability**: Structure code so core logic is testable without heavy integration
- [ ] **Error handling**: Fail explicitly with clear errors; never silently ignore failures
- [ ] **Observability**: Log meaningful events at integration boundaries (no secrets)

### Quality Requirements

**Reference**: `checklist.md` for detailed criteria

- [ ] Code passes quality checklist
- [ ] Functions/methods are appropriately sized
- [ ] Error handling is consistent
- [ ] Tests cover implemented requirements

---

## Tasks

Agent executes tasks during generation:

### Phase 1: Setup

**1.1 Resolve Source**

Ask user for implementation source (if not provided):

| Source Type | Traceability | Action |
|-------------|--------------|--------|
| FEATURE design (registered) | FULL possible | Load artifact, extract `to_code="true"` IDs |
| Other FDD artifact (PRD/DESIGN/ADR) | DOCS-ONLY | Load artifact, extract requirements |
| User-provided spec/description | DOCS-ONLY | Use as requirements reference |
| Prompt only | DOCS-ONLY | Implement per user instructions |
| None | — | Suggest: `/fdd-generate FEATURE` to create design first |

**1.2 Load Context**

- [ ] Read adapter `AGENTS.md` for code conventions
- [ ] Load source artifact/description
- [ ] Load `checklist.md` for quality guidance
- [ ] If FEATURE source: identify all IDs with `to_code="true"` attribute
- [ ] Determine Traceability Mode (see Requirements)
- [ ] Plan implementation order (by requirement, flow, or phase)

### Phase 2: Implementation (Work Packages)

Choose implementation order based on feature design:
- One requirement end-to-end, or
- One flow/algo/state section end-to-end, or
- One phase at a time if design defines phases

**For each work package:**

1. Identify exact design items to code (flows/algos/states/requirements/tests)
2. Implement according to adapter conventions
3. **If Traceability Mode ON**: Add instruction-level tags while implementing
4. Run work package validation (tests, build, linters per adapter)
5. **If Traceability Mode ON**: Update feature DESIGN.md checkboxes
6. Proceed to next work package

### Phase 3: FDD Markers (Traceability Mode ON only)

**Reference**: `{FDD}/requirements/traceability.md` for full marker syntax

**Apply markers per spec:**
- Scope markers: `@fdd-{kind}:{id}:ph-{N}` at function/class entry
- Block markers: `@fdd-begin:{id}:ph-{N}:inst-{local}` / `@fdd-end:...` wrapping FDL steps

**Quick reference:**
```python
# @fdd-begin:fdd-myapp-feature-auth-flow-login:ph-1:inst-validate-creds
def validate_credentials(username, password):
    # implementation here
    pass
# @fdd-end:fdd-myapp-feature-auth-flow-login:ph-1:inst-validate-creds
```

### Phase 4: Sync Feature DESIGN.md (Traceability Mode ON only)

**After each work package, sync checkboxes:**

1. For each `...:ph-{N}:inst-{local}` implemented:
   - Locate owning scope entry in DESIGN.md by base ID
   - Find matching FDL step line with `ph-{N}` and `inst-{local}`
   - Mark checkbox: `- [ ]` → `- [x]`

2. For each requirement ID implemented:
   - First work package for requirement: set `**Status**` to `🔄 IN_PROGRESS`
   - Mark `**Phases**` checkboxes as implemented
   - All phases complete: set `**Status**` to `✅ IMPLEMENTED`

3. For test scenarios:
   - Do NOT mark until test exists and passes

**Consistency rule**: Only mark `[x]` if corresponding code exists and is tagged

### Phase 5: Quality Check

- [ ] Self-review against `checklist.md`
- [ ] **If Traceability Mode ON**: Verify all `to_code="true"` IDs have markers
- [ ] **If Traceability Mode ON**: Ensure no orphaned markers
- [ ] Run tests to verify implementation
- [ ] Verify engineering best practices followed

### Phase 6: Tag Verification (Traceability Mode ON only)

**Before finishing implementation:**
- [ ] Search codebase for ALL IDs from DESIGN (flow/algo/state/req/test)
- [ ] Confirm tags exist in files that implement corresponding logic/tests
- [ ] If any DESIGN ID has no code tag → report as gap and/or add tag

### When Updating Existing Code

- [ ] Preserve existing FDD markers
- [ ] Add markers for new design elements
- [ ] Remove markers for deleted design elements
- [ ] Update marker IDs if design IDs changed (with migration)

---

## Validation

Validation workflow verifies requirements are met:

### Phase 1: Implementation Coverage

For each ID/scope marked as implemented:

**Verify code exists:**
- [ ] Code files exist and contain implementation
- [ ] Code is not placeholder/stub (no TODO/FIXME/unimplemented!)
- [ ] No unimplemented!() in business logic

### Phase 2: Traceability Validation (Mode ON only)

**Reference**: `{FDD}/requirements/traceability.md` for validation rules

**Deterministic checks** (per spec):
- [ ] Marker format valid
- [ ] All begin/end pairs matched
- [ ] No empty blocks
- [ ] Phase postfix present on all markers

**Coverage checks**:
- [ ] All `to_code="true"` IDs have markers
- [ ] No orphaned markers (marker ID not in design)
- [ ] No stale markers (design ID changed/deleted)
- [ ] Design checkboxes synced with code markers

### Phase 3: Test Scenarios Validation

For each test scenario from design:

- [ ] Test file exists (unit/integration/e2e per adapter)
- [ ] Test contains scenario ID in comment for traceability
- [ ] Test is NOT ignored without justification
- [ ] Test actually validates scenario behavior (not placeholder)
- [ ] Test follows adapter testing conventions

### Phase 4: Build and Lint Validation

**Build:**
- [ ] Build succeeds
- [ ] No compilation errors
- [ ] No compiler warnings (or acceptable per adapter)

**Lint:**
- [ ] Linter passes
- [ ] No linter errors
- [ ] No linter warnings (or acceptable per adapter)

### Phase 5: Test Execution

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All e2e tests pass (if applicable)
- [ ] No ignored tests without justification
- [ ] Coverage meets adapter requirements

### Phase 6: Code Quality Validation

**Check for incomplete work:**
- [ ] No TODO/FIXME/XXX/HACK in domain/service layers
- [ ] No unimplemented!/todo! in business logic
- [ ] No bare unwrap() or panic in production code
- [ ] No ignored tests without documented reason
- [ ] No placeholder tests (assert!(true))

**Engineering best practices:**
- [ ] TDD: New/changed behavior covered by tests
- [ ] SOLID: Responsibilities separated; dependencies injectable
- [ ] DRY: No copy-paste duplication without justification
- [ ] KISS: No unnecessary complexity
- [ ] YAGNI: No speculative abstractions beyond design scope

### Phase 7: Code Logic Consistency with Design

**For each requirement marked IMPLEMENTED:**
- [ ] Read requirement specification
- [ ] Locate implementing code via @fdd-req tags
- [ ] Verify code logic matches requirement (no contradictions)
- [ ] Verify no skipped mandatory steps
- [ ] Verify error handling matches design error specifications

**For each flow marked implemented:**
- [ ] All flow steps executed in correct order
- [ ] No steps bypassed that would change behavior
- [ ] Conditional logic matches design conditions
- [ ] Error paths match design error handling

**For each algorithm marked implemented:**
- [ ] Algorithm logic matches design specification
- [ ] Performance characteristics match design (O(n), O(1), etc.)
- [ ] Edge cases handled as designed
- [ ] No logic shortcuts that violate design constraints

### Traceability Report

**Format**: See `{FDD}/requirements/traceability.md` → Validation Report

### Quality Report

Output format:
```
Code Quality Report
═══════════════════

Build: PASS/FAIL
Lint: PASS/FAIL
Tests: X/Y passed
Coverage: N%

Checklist: PASS/FAIL (N issues)

Issues:
- [SEVERITY] CHECKLIST-ID: Description

Logic Consistency: PASS/FAIL
- CRITICAL divergences: [...]
- MINOR divergences: [...]
```

### PASS/FAIL Criteria

**PASS only if:**
- Build/lint/tests pass per adapter
- Coverage meets adapter requirements
- No CRITICAL divergences between code and design
- If Traceability Mode ON: required tags present and properly paired

### Phase 8: Semantic Expert Review (Always)

Run expert panel review after producing validation output.

**Experts**:
- Developer, QA Engineer, Security Expert, Performance Engineer
- DevOps Engineer, Architect, Monitoring Engineer
- Database Architect, Data Engineer

**For EACH expert:**
1. Adopt role (write: `Role assumed: {expert}`)
2. Review actual code and tests in validation scope
3. If design artifact available: evaluate design-to-code alignment
4. Identify issues:
   - Contradictions vs design intent
   - Missing behavior (requirements/tests)
   - Unclear intent (naming/structure)
   - Unnecessary complexity (YAGNI, premature abstraction)
   - Missing non-functional concerns (security/perf/observability)
5. Provide concrete proposals:
   - What to remove (dead code, unused abstractions)
   - What to add (tests, error handling, validation)
   - What to rewrite (simpler structure, clearer naming)
6. Propose corrective workflow:
   - If design must change: `feature` or `design` (UPDATE mode)
   - If only code must change: `code` (continue implementation)

**Output format:**
```
### Semantic Expert Review

**Review status**: COMPLETED
**Reviewed artifact**: Code ({scope})

#### Expert: {expert}
- **Role assumed**: {expert}
- **Checklist completed**: YES
- **Findings**:
  - Contradictions: ...
  - Missing behavior: ...
  - Unclear intent: ...
  - Unnecessary complexity: ...
- **Proposed edits**:
  - Remove: "..." → Reason: ...
  - Add: ...
  - Rewrite: "..." → "..."

**Recommended corrective workflow**: {feature | design | code}
```

---

## Next Steps

After code generation/validation, offer these options to user:

### After Successful Implementation

| Condition | Suggested Next Step |
|-----------|---------------------|
| Feature complete | Update feature status to IMPLEMENTED in FEATURES manifest |
| All features done | `/fdd-validate DESIGN` — validate overall design completion |
| New feature needed | `/fdd-generate FEATURE` — design next feature |

### After Validation Issues

| Issue Type | Suggested Next Step |
|------------|---------------------|
| Design mismatch | `/fdd-generate FEATURE` — update feature design |
| Missing tests | Continue `/fdd-generate CODE` — add tests |
| Code quality issues | Continue `/fdd-generate CODE` — refactor |

### If No Design Exists

| Scenario | Suggested Next Step |
|----------|---------------------|
| Implementing new feature | `/fdd-generate FEATURE` — create feature design first |
| Implementing from PRD | `/fdd-generate DESIGN` then `/fdd-generate FEATURES` — create design hierarchy |
| Quick prototype | Proceed without traceability, suggest `/fdd-generate FEATURE` later |
