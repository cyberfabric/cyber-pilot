# CODEBASE Rules

**Artifact**: CODEBASE
**Kit**: sdlc

**Dependencies**:
- `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md` — semantic quality criteria

## Table of Contents

1. [Prerequisites](#prerequisites)
   - [Load Dependencies](#load-dependencies)
2. [Requirements](#requirements)
   - [Structural](#structural)
   - [Traceability](#traceability)
   - [Checkbox Cascade](#checkbox-cascade)
   - [Versioning](#versioning)
   - [Engineering](#engineering)
   - [Quality](#quality)
3. [Tasks](#tasks)
   - [Phase 1: Setup](#phase-1-setup)
   - [Phase 2: Implementation (Work Packages)](#phase-2-implementation-work-packages)
   - [Phase 3: Cypilot Markers (Traceability Mode ON only)](#phase-3-cypilot-markers-traceability-mode-on-only)
   - [Phase 4: Sync FEATURE (Traceability Mode ON only)](#phase-4-sync-feature-traceability-mode-on-only)
   - [Phase 5: Quality Check](#phase-5-quality-check)
   - [Phase 6: Tag Verification (Traceability Mode ON only)](#phase-6-tag-verification-traceability-mode-on-only)
   - [Phase 7: Table of Contents](#phase-7-table-of-contents)
4. [Validation](#validation)
   - [Phase 1: Implementation Coverage](#phase-1-implementation-coverage)
   - [Phase 2: Traceability Validation (Mode ON only)](#phase-2-traceability-validation-mode-on-only)
   - [Phase 3: Test Scenarios Validation](#phase-3-test-scenarios-validation)
   - [Phase 4: Build and Lint Validation](#phase-4-build-and-lint-validation)
   - [Phase 5: Test Execution](#phase-5-test-execution)
   - [Phase 6: Code Quality Validation](#phase-6-code-quality-validation)
   - [Phase 7: Code Logic Consistency with Design](#phase-7-code-logic-consistency-with-design)
   - [Phase 8: Semantic Expert Review (Always)](#phase-8-semantic-expert-review-always)
   - [Phase 9: Table of Contents Validation](#phase-9-table-of-contents-validation)
5. [Next Steps](#next-steps)
   - [After Success](#after-success)
   - [After Issues](#after-issues)
   - [No Design](#no-design)

---

## Prerequisites

### Load Dependencies

- [ ] Read project `AGENTS.md` for code conventions
- [ ] Load source artifact/description (FEATURE preferred)
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md` for quality guidance
- [ ] Load `{cypilot_path}/.core/requirements/code-checklist.md` for generic code quality checks
- [ ] If FEATURE source: identify all IDs with `to_code="true"` attribute
- [ ] Determine Traceability Mode (FULL vs DOCS-ONLY)
- [ ] If Traceability Mode FULL: load `{cypilot_path}/.core/architecture/specs/traceability.md`
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/constraints.toml` for kit-level constraints

**Source** (one of, in priority order):
1. FEATURE design — registered artifact with `to_code="true"` IDs
2. Other Cypilot artifact — PRD, DESIGN, ADR, DECOMPOSITION
3. Similar content — user-provided description, feature, or requirements
4. Prompt only — direct user instructions

**ALWAYS read** the FEATURE artifact being implemented (the source of `to_code="true"` IDs). The FEATURE contains flows, algorithms, states, and definition-of-done tasks that define what code must do.

**ALWAYS read** the system's DESIGN artifact (if registered in `artifacts.toml`) to understand overall architecture, components, principles, and constraints before implementing code.

---

## Requirements

### Structural

- [ ] Code implements FEATURE design requirements
- [ ] Code follows project conventions from config

### Traceability

**Reference**: `{cypilot_path}/.core/architecture/specs/traceability.md` for full specification

- [ ] Traceability Mode determined per feature (FULL vs DOCS-ONLY)
- [ ] If Mode ON: markers follow feature syntax (`@cpt-*`, `@cpt-begin`/`@cpt-end`)
- [ ] If Mode ON: all `to_code="true"` IDs have markers
- [ ] If Mode ON: every implemented CDSL instruction (`[x] ... \`inst-*\``) has a paired `@cpt-begin/.../@cpt-end` block marker in code
- [ ] If Mode ON: no orphaned/stale markers
- [ ] If Mode ON: design checkboxes synced with code
- [ ] If Mode OFF: no Cypilot markers in code

### Checkbox Cascade

CODE implementation triggers upstream checkbox updates through markers:

| Code Marker | FEATURE ID | Upstream Effect |
|-------------|-----------|-----------------|
| `@cpt-flow:{cpt-id}:p{N}` | kind: `flow` | When all pN markers exist → check `flow` ID in FEATURE |
| `@cpt-algo:{cpt-id}:p{N}` | kind: `algo` | When all pN markers exist → check `algo` ID in FEATURE |
| `@cpt-state:{cpt-id}:p{N}` | kind: `state` | When all pN markers exist → check `state` ID in FEATURE |
| `@cpt-dod:{cpt-id}:p{N}` | kind: `dod` | When all pN markers exist + evidence complete → check `dod` ID in FEATURE |

**Full Cascade Chain**:
```
CODE markers exist
    ↓
FEATURE: flow/algo/state/dod IDs → [x]
    ↓
DECOMPOSITION: feature entry [x]
    ↓
PRD/DESIGN: referenced IDs [x] when ALL downstream refs [x]
```

**When to Update Upstream Checkboxes**:
1. **After implementing CDSL instruction**: add block markers, mark step `[x]` in FEATURE
2. **After completing flow/algo/state/dod**: all steps `[x]` → mark ID `[x]` in FEATURE
3. **After completing FEATURE**: all IDs `[x]` → mark feature entry `[x]` in DECOMPOSITION
4. **After DECOMPOSITION updated**: check if all referenced IDs are `[x]` → mark in PRD/DESIGN

**Consistency rules (MANDATORY)**:
- [ ] Never mark CDSL instruction `[x]` unless corresponding code block markers exist and wrap non-empty implementation code
- [ ] Never add code block marker pair unless corresponding CDSL instruction exists in design (add it first if missing)
- [ ] Parent ID checkbox state MUST be consistent with all nested task-tracked items within its scope (as determined by heading boundaries)
- [ ] Task-tracked items include:
  - ID definitions with a task checkbox (e.g. `- [ ] p1 - **ID**: cpt-...`)
  - Task-checkbox references inside content (e.g. `- [ ] p1 - cpt-...`)
- [ ] If parent ID is `[x]` then ALL nested task-tracked items within its scope MUST be `[x]`
- [ ] If ALL nested task-tracked items within its scope are `[x]` then parent ID MUST be `[x]`
- [ ] Never mark a reference as `[x]` if its definition is still `[ ]` (cross-artifact consistency is validated)

**Validation Checks**:
- `cypilot validate` will warn if code marker exists but FEATURE checkbox is `[ ]`
- `cypilot validate` will warn if FEATURE checkbox is `[x]` but code marker is missing
- `cypilot validate` will report coverage: N% of FEATURE IDs have code markers

### Versioning

- [ ] When design ID versioned (`-v2`): update code markers to match
- [ ] Marker format with version: `@cpt-flow:{cpt-id}-v2:p{N}`
- [ ] Migration: update all markers when design version increments
- [ ] Keep old markers commented during transition (optional)

### Engineering

- [ ] **TDD**: Write failing test first, implement minimal code to pass, then refactor
- [ ] **SOLID**:
  - Single Responsibility: Each module/function focused on one reason to change
  - Open/Closed: Extend behavior via composition/configuration, not editing unrelated logic
  - Liskov Substitution: Implementations honor interface contract and invariants
  - Interface Segregation: Prefer small, purpose-driven interfaces over broad ones
  - Dependency Inversion: Depend on abstractions; inject dependencies for testability
- [ ] **DRY**: Remove duplication by extracting shared logic with clear ownership
- [ ] **KISS**: Prefer simplest correct solution matching design and project conventions
- [ ] **YAGNI**: No specs/abstractions not required by current design scope
- [ ] **Refactoring discipline**: Refactor only after tests pass; keep behavior unchanged
- [ ] **Testability**: Structure code so core logic is testable without heavy integration
- [ ] **Error handling**: Fail explicitly with clear errors; never silently ignore failures
- [ ] **Observability**: Log meaningful events at integration boundaries (no secrets)

### Quality

**Reference**: `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md` for detailed criteria

- [ ] Code passes quality checklist
- [ ] Functions/methods are appropriately sized
- [ ] Error handling is consistent
- [ ] Tests cover implemented requirements

---

## Tasks

### Phase 1: Setup

**Resolve Source** (priority order):
1. FEATURE design (registered) — Traceability FULL possible
2. Other Cypilot artifact (PRD/DESIGN/ADR) — DOCS-ONLY
3. User-provided description — DOCS-ONLY
4. Prompt only — DOCS-ONLY
5. None — suggest `/cypilot-generate FEATURE` first

**Load Context**:
- [ ] Read project `AGENTS.md` for code conventions
- [ ] Load source artifact/description
- [ ] Load `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md` for quality guidance
- [ ] Determine Traceability Mode
- [ ] Plan implementation order

### Phase 2: Implementation (Work Packages)

**For each work package:**
1. Identify exact design items to code (flows/algos/states/requirements/tests)
2. Implement according to project conventions
3. If Traceability Mode ON: add instruction-level tags while implementing
4. Run work package validation (tests, build, linters per project config)
5. If Traceability Mode ON: update FEATURE.md checkboxes
6. Proceed to next work package

### Phase 3: Cypilot Markers (Traceability Mode ON only)

**Traceability Mode ON only.**

Apply markers per feature:
- Scope markers: `@cpt-{kind}:{cpt-id}:p{N}` at function/class entry
- Block markers: `@cpt-begin:{cpt-id}:p{N}:inst-{local}` / `@cpt-end:...` wrapping CDSL steps

### Phase 4: Sync FEATURE (Traceability Mode ON only)

**Traceability Mode ON only.**

After each work package, sync checkboxes:
1. Mark implemented CDSL steps `[x]` in FEATURE
2. When all steps done → mark flow/algo/state/dod `[x]` in FEATURE
3. When all IDs done → mark feature entry `[x]` in DECOMPOSITION
4. Update feature status: `⏳ PLANNED` → `🔄 IN_PROGRESS` → `✅ IMPLEMENTED`

### Phase 5: Quality Check

- [ ] Self-review against `{cypilot_path}/.gen/kits/sdlc/codebase/checklist.md`
- [ ] If Traceability Mode ON: verify all `to_code="true"` IDs have markers
- [ ] If Traceability Mode ON: ensure no orphaned markers
- [ ] Run tests to verify implementation
- [ ] Verify engineering best practices followed

### Phase 6: Tag Verification (Traceability Mode ON only)

**Traceability Mode ON only.**

- [ ] Search codebase for ALL IDs from FEATURE (flow/algo/state/dod)
- [ ] Confirm tags exist in files that implement corresponding logic/tests
- [ ] If any FEATURE ID has no code tag → report as gap and/or add tag

### Phase 7: Table of Contents

- [ ] Run `cypilot toc <artifact-file>` to generate/update Table of Contents
- [ ] Verify TOC is present and complete with `cypilot validate-toc <artifact-file>`

---

## Validation

### Phase 1: Implementation Coverage

- [ ] Code files exist and contain implementation
- [ ] Code is not placeholder/stub (no TODO/FIXME/unimplemented!)

### Phase 2: Traceability Validation (Mode ON only)

**Mode ON only.** Reference: `{cypilot_path}/.core/architecture/specs/traceability.md`

- [ ] Marker format valid
- [ ] All begin/end pairs matched
- [ ] No empty blocks
- [ ] All `to_code="true"` IDs have markers
- [ ] No orphaned/stale markers
- [ ] Design checkboxes synced with code markers

### Phase 3: Test Scenarios Validation

- [ ] Test file exists for each test scenario from design
- [ ] Test contains scenario ID in comment for traceability
- [ ] Test is NOT ignored without justification
- [ ] Test actually validates scenario behavior

### Phase 4: Build and Lint Validation

- [ ] Build succeeds, no compilation errors
- [ ] Linter passes, no linter errors

**Report format**:
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

### Phase 5: Test Execution

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All e2e tests pass (if applicable)
- [ ] Coverage meets project requirements

### Phase 6: Code Quality Validation

- [ ] No TODO/FIXME/XXX/HACK in domain/service layers
- [ ] No unimplemented!/todo! in business logic
- [ ] No bare unwrap() or panic in production code
- [ ] TDD: New/changed behavior covered by tests
- [ ] SOLID: Responsibilities separated; dependencies injectable
- [ ] DRY: No copy-paste duplication
- [ ] KISS: No unnecessary complexity
- [ ] YAGNI: No speculative abstractions

### Phase 7: Code Logic Consistency with Design

**For each requirement marked IMPLEMENTED:**
- [ ] Read requirement specification
- [ ] Locate implementing code via @cpt-dod tags
- [ ] Verify code logic matches requirement (no contradictions)
- [ ] Verify no skipped mandatory steps
- [ ] Verify error handling matches design error specifications

**For each flow marked implemented:**
- [ ] All flow steps executed in correct order
- [ ] No steps bypassed that would change behavior
- [ ] Conditional logic matches design conditions
- [ ] Error paths match design error handling

**For each algorithm marked implemented:**
- [ ] Performance characteristics match design (O(n), O(1), etc.)
- [ ] Edge cases handled as designed
- [ ] No logic shortcuts that violate design constraints

### Phase 8: Semantic Expert Review (Always)

Run expert panel review after producing validation output.

**Review Scope Selection**:

| Change Size | Review Mode | Experts |
|-------------|-------------|--------|
| <50 LOC, single concern | Abbreviated | Developer + 1 relevant expert |
| 50-200 LOC, multiple concerns | Standard | Developer, QA, Security, Architect |
| >200 LOC or architectural | Full | All 8 experts |

**Abbreviated Review** (for small, focused changes):
1. Developer reviews code quality and design alignment
2. Select ONE additional expert based on change type
3. Skip remaining experts with note: `Abbreviated review: {N} LOC, single concern`

**Full Expert Panel**: Developer, QA Engineer, Security Expert, Performance Engineer, DevOps Engineer, Architect, Monitoring Engineer, Database Architect/Data Engineer

**For EACH expert:**
1. Adopt role (write: `Role assumed: {expert}`)
2. Review actual code and tests in validation scope
3. If design artifact available: evaluate design-to-code alignment
4. Identify issues (contradictions, missing behavior, unclear intent, unnecessary complexity, missing non-functional concerns)
5. Provide concrete proposals (what to remove, add, rewrite)
6. Propose corrective workflow: `feature`, `design`, or `code`

**Expert review output format:**
```
**Review status**: COMPLETED
**Reviewed artifact**: Code ({scope})
- **Role assumed**: {expert}
- **Checklist completed**: YES
- **Findings**:
- **Proposed edits**:
**Recommended corrective workflow**: {feature | design | code}
```

**PASS only if:**
- Build/lint/tests pass per project config
- Coverage meets project requirements
- No CRITICAL divergences between code and design
- If Traceability Mode ON: required tags present and properly paired

### Phase 9: Table of Contents Validation

- [ ] Table of Contents section exists (`## Table of Contents` or `<!-- toc -->` markers)
- [ ] All TOC anchors point to actual headings in the document
- [ ] All headings are represented in the TOC
- [ ] TOC order matches document heading order
- [ ] Run `cypilot validate-toc <artifact-file>` — must report PASS

---

## Next Steps

### After Success

- [ ] Feature complete → update feature status to IMPLEMENTED in DECOMPOSITION
- [ ] All features done → `/cypilot-analyze DESIGN` — validate overall design completion
- [ ] New feature needed → `/cypilot-generate FEATURE` — design next feature
- [ ] Want expert review only → `/cypilot-analyze semantic` — semantic validation

### After Issues

- [ ] Design mismatch → `/cypilot-generate FEATURE` — update feature design
- [ ] Missing tests → continue `/cypilot-generate CODE` — add tests
- [ ] Code quality issues → continue `/cypilot-generate CODE` — refactor

### No Design

- [ ] Implementing new feature → `/cypilot-generate FEATURE` first
- [ ] Implementing from PRD → `/cypilot-generate DESIGN` then DECOMPOSITION
- [ ] Quick prototype → proceed without traceability, suggest FEATURE later
