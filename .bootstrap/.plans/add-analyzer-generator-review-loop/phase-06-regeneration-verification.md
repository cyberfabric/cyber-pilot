```toml
[phase]
plan = "add-analyzer-generator-review-loop"
number = 6
total = 7
type = "implement"
title = "Regenerate agent outputs and verify the repo"
depends_on = [5]
input_manifest = ""
input_signature = ""
input_files = [".bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml", "CONTRIBUTING.md", "Makefile", ".claude/agents", "skills/cypilot/agents.toml", "tests/test_subagent_registration.py"]
output_files = [".claude/agents/cypilot-generator.md", ".claude/agents/cypilot-analyzer.md", ".claude/agents/cypilot-codegen.md", ".claude/agents/cypilot-pr-review.md"]
outputs = ["out/phase-06-verification-report.md"]
inputs = ["out/phase-05-test-update-summary.md"]
```

## Preamble

This is a self-contained phase file. All rules, constraints, and kit content
are included below. Project files listed in the Task section must be read
at runtime. Follow the instructions exactly, run any EXECUTE commands as
written, and report results against the acceptance criteria at the end.

## What

Regenerate the tracked Claude agent outputs for the expanded subagent registry, then run the bounded verification commands that do not widen the delivery surface beyond the four tracked `.claude/agents/` files and the intermediate verification report at `out/phase-06-verification-report.md`. This phase is limited to those tracked outputs, targeted verification commands, and verification reporting. Do not broaden scope into repo-wide update flows, unrelated architecture, lifecycle, or test changes.

## Prior Context

Phase 6 depends on Phase 5 and consumes `out/phase-05-test-update-summary.md` as its precondition and verification checklist.
The plan tracks four Claude agent outputs for this phase: `cypilot-generator.md`, `cypilot-analyzer.md`, `cypilot-codegen.md`, and `cypilot-pr-review.md` under `.claude/agents/`.
The current `.claude/agents/` directory contains `cypilot-codegen.md`, `cypilot-phase-compiler.md`, `cypilot-phase-runner.md`, `cypilot-pr-review.md`, and `cypilot-ralphex.md`.
`skills/cypilot/agents.toml` currently registers `cypilot-codegen`, `cypilot-pr-review`, `cypilot-ralphex`, `cypilot-phase-runner`, and `cypilot-phase-compiler`.
`make update` triggers repo-wide bootstrap regeneration via `cpt update --source . --force` and is outside this bounded phase's blind-execution delivery surface unless the plan contract is explicitly widened first.

## Rules

### Bootstrap handling

- You MUST treat `.bootstrap/.core/` and `.bootstrap/.gen/` as read-only mirrors during delivery work.
- You MUST NOT run `make update` or `cpt update --source . --force` as part of this bounded phase, because those commands can widen the working tree beyond the tracked delivery surface.
- If broader bootstrap verification becomes necessary, you MUST stop and report that the phase contract needs explicit widening before running repo-wide mutation.
- You MUST ensure the final delivery status is justified only by the four tracked Claude agent outputs plus `out/phase-06-verification-report.md`.
- You MUST keep the phase focused on the tracked Claude agent outputs, verification commands, and the verification report.
- You MUST NOT edit unrelated project files or broaden scope beyond this phase contract.

### Agent regeneration

- You MUST regenerate the Claude agent outputs with the canonical `generate-agents` command shape from `cypilot.clispec`.
- You MUST run `cpt --json generate-agents --agent claude` from the repository root and capture the exact result.
- You MUST record the command outcome, including the reported JSON status and the created or updated outputs.
- You MUST verify the tracked Claude agent files after regeneration: `.claude/agents/cypilot-generator.md`, `.claude/agents/cypilot-analyzer.md`, `.claude/agents/cypilot-codegen.md`, and `.claude/agents/cypilot-pr-review.md`.
- You MUST NOT treat untracked agent files as completion for this phase.

### Verification commands

- You MUST read every runtime input listed in the frontmatter before using it.
- You MUST use the bounded verification flow for this phase: targeted `pytest`, `make validate`, and `make self-check`.
- You MUST run targeted pytest against `tests/test_subagent_registration.py` and capture the exact command result.
- You MUST capture exact results for every verification command that is actually run in this bounded phase, including the command line, exit status, and a concise summary of observed output.
- You MUST record explicitly that `make update` / `cpt update --source . --force` were treated as out-of-scope repo-wide mutation for this phase.
- You MUST save the verification summary to `out/phase-06-verification-report.md`.
- You MUST self-verify against the acceptance criteria before reporting completion.

### Authoritative CODEBASE rules and checklist

The following content is inlined verbatim from `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/config/kits/sdlc/codebase/rules.md` and `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/config/kits/sdlc/codebase/checklist.md`. It is authoritative for this phase and MUST be followed without summarization or substitution by path-only references.

#### `rules.md` (verbatim)

```markdown
# CODEBASE Rules

**Artifact**: CODEBASE
**Kit**: sdlc

**Dependencies** (lazy-loaded):
- `{codebase_checklist}` — semantic quality criteria (load WHEN checking code quality)

## Table of Contents

1. [Prerequisites](#prerequisites)
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
4. [Validation](#validation)
   - [Phase 1: Implementation Coverage](#phase-1-implementation-coverage)
   - [Phase 2: Traceability Validation (Mode ON only)](#phase-2-traceability-validation-mode-on-only)
   - [Phase 3: Test Scenarios Validation](#phase-3-test-scenarios-validation)
   - [Phase 4: Build and Lint Validation](#phase-4-build-and-lint-validation)
   - [Phase 5: Test Execution](#phase-5-test-execution)
   - [Phase 6: Code Quality Validation](#phase-6-code-quality-validation)
   - [Phase 7: Code Logic Consistency with Design](#phase-7-code-logic-consistency-with-design)
   - [Phase 8: Semantic Expert Review (Always)](#phase-8-semantic-expert-review-always)
5. [Next Steps](#next-steps)
   - [After Success](#after-success)
   - [After Issues](#after-issues)
   - [No Design](#no-design)

---

## Prerequisites

- Read project `AGENTS.md` for code conventions
- Load source artifact/description (FEATURE preferred)
- If FEATURE source: identify all IDs with `to_code="true"` attribute
- Determine Traceability Mode (FULL vs DOCS-ONLY)

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

**Load on demand**: `{cypilot_path}/.core/architecture/specs/traceability.md` — WHEN Traceability Mode FULL

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

**Load on demand**:
- `{codebase_checklist}` — WHEN checking code quality
- `{cypilot_path}/.core/requirements/code-checklist.md` — WHEN checking generic code quality

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
- [ ] Determine Traceability Mode
- [ ] Plan implementation order

### Phase 2: Implementation (Work Packages)

**For each work package:**
1. Identify exact design items to code (flows/algos/states/requirements/tests)
2. Implement according to project conventions
3. If Traceability Mode ON: add `@cpt-begin`/`@cpt-end` markers **per CDSL instruction** while implementing — wrap only the specific lines that implement each instruction, not entire functions
4. Run work package validation (tests, build, linters per project config)
5. If Traceability Mode ON: update FEATURE.md checkboxes
6. Proceed to next work package

### Phase 3: Cypilot Markers (Traceability Mode ON only)

**Traceability Mode ON only.**

Apply markers per feature:
- **Scope markers**: `@cpt-{kind}:{cpt-id}:p{N}` — single-line, at function/class entry point
- **Block markers**: `@cpt-begin:{cpt-id}:p{N}:inst-{local}` / `@cpt-end:...` — paired, wrapping **only the specific lines** that implement one CDSL instruction

**Granularity rules (MANDATORY)**:
1. Each `@cpt-begin`/`@cpt-end` pair wraps the **smallest code fragment** that implements its CDSL instruction
2. When a function implements multiple CDSL instructions, place **separate** begin/end pairs for each instruction inside the function body
3. Place markers as **close to the implementing code as possible** — directly above/below the relevant lines
4. Do NOT wrap an entire function body with a single begin/end pair when the function implements multiple instructions

**Correct** — each instruction wrapped individually:
```python
# @cpt-algo:cpt-system-algo-process:p1
def process_data(items):
    # @cpt-begin:cpt-system-algo-process:p1:inst-validate
    if not items:
        raise ValueError("Empty input")
    # @cpt-end:cpt-system-algo-process:p1:inst-validate

    # @cpt-begin:cpt-system-algo-process:p1:inst-transform
    result = [transform(item) for item in items]
    # @cpt-end:cpt-system-algo-process:p1:inst-transform

    # @cpt-begin:cpt-system-algo-process:p1:inst-return-result
    return result
    # @cpt-end:cpt-system-algo-process:p1:inst-return-result
```

**WRONG** — entire function wrapped with one pair (loses per-instruction traceability):
```python
# @cpt-begin:cpt-system-algo-process:p1:inst-validate
def process_data(items):
    if not items:
        raise ValueError("Empty input")
    result = [transform(item) for item in items]
    return result
# @cpt-end:cpt-system-algo-process:p1:inst-validate
```

### Phase 4: Sync FEATURE (Traceability Mode ON only)

**Traceability Mode ON only.**

After each work package, sync checkboxes:
1. Mark implemented CDSL steps `[x]` in FEATURE
2. When all steps done → mark flow/algo/state/dod `[x]` in FEATURE
3. When all IDs done → mark feature entry `[x]` in DECOMPOSITION
4. Update feature status: `⏳ PLANNED` → `🔄 IN_PROGRESS` → `✅ IMPLEMENTED`

### Phase 5: Quality Check

**Load on demand**: `{codebase_checklist}` — WHEN self-reviewing code quality

- [ ] Self-review against `{codebase_checklist}`
- [ ] If Traceability Mode ON: verify all `to_code="true"` IDs have markers
- [ ] If Traceability Mode ON: ensure no orphaned markers
- [ ] Run tests to verify implementation
- [ ] Verify engineering best practices followed

### Phase 6: Tag Verification (Traceability Mode ON only)

**Traceability Mode ON only.**

- [ ] Search codebase for ALL IDs from FEATURE (flow/algo/state/dod)
- [ ] Confirm tags exist in files that implement corresponding logic/tests
- [ ] If any FEATURE ID has no code tag → report as gap and/or add tag

---

## Validation

### Phase 1: Implementation Coverage

- [ ] Code files exist and contain implementation
- [ ] Code is not placeholder/stub (no TODO/FIXME/unimplemented!)

### Phase 2: Traceability Validation (Mode ON only)

**Load on demand**: `{cypilot_path}/.core/architecture/specs/traceability.md` — required for this phase (Mode ON only)

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
```

#### `checklist.md` (verbatim)

```markdown
# Cypilot SDLC Code Checklist (Kit-Specific)

ALWAYS open and follow `{cypilot_path}/.core/requirements/code-checklist.md` FIRST

**Artifact**: Code Implementation (Cypilot SDLC)
**Version**: 1.0
**Purpose**: Kit-specific checks that require Cypilot SDLC artifacts (PRD/DESIGN/DECOMPOSITION/FEATURE/ADR) and/or Cypilot traceability.

---

## Table of Contents

1. [Traceability Preconditions](#traceability-preconditions)
2. [Semantic Alignment (SEM)](#semantic-alignment-sem)

---

## Traceability Preconditions

Before running the SDLC-specific checks:

- [ ] Determine traceability mode from `artifacts.toml` for the relevant system/artifact: `FULL` vs `DOCS-ONLY`
- [ ] If `FULL`: identify the design source(s) to trace (Feature design is preferred)
- [ ] If `DOCS-ONLY`: skip traceability requirements and validate semantics against provided design sources

---

## Semantic Alignment (SEM)

These checks are **Cypilot SDLC-specific** because they require Cypilot artifacts (Feature design, Overall Design, ADRs, PRD/DESIGN coverage) and/or Cypilot markers.

### SEM-CODE-001: Resolve Design Sources
**Severity**: HIGH

- [ ] Resolve Feature design via `@cpt-*` markers using the `cypilot where-defined` or `cypilot where-used` skill
- [ ] If no `@cpt-*` markers exist, ask the user to provide the Feature design location before proceeding
- [ ] If the user is unsure, search the repository for candidate feature designs and present options for user selection
- [ ] Resolve Overall Design by following references from the Feature design (or ask the user for the design path)

### SEM-CODE-002: Spec Context Semantics
**Severity**: HIGH

- [ ] Confirm code behavior aligns with the Feature Overview, Purpose, and key assumptions
- [ ] Verify all referenced actors are represented by actual interfaces, entrypoints, or roles in code
- [ ] Ensure referenced ADRs and related specs do not conflict with current implementation choices

### SEM-CODE-003: Spec Flows Semantics
**Severity**: HIGH

- [ ] Verify each implemented flow follows the ordered steps, triggers, and outcomes in Actor Flows
- [ ] Confirm conditionals, branching, and return paths match the flow logic
- [ ] Validate all flow steps marked with IDs are implemented and traceable

### SEM-CODE-004: Algorithms Semantics
**Severity**: HIGH

- [ ] Validate algorithm steps match the Feature design algorithms (inputs, rules, outputs)
- [ ] Ensure data transformations and calculations match the described business rules
- [ ] Confirm loop/iteration behavior and validation rules align with algorithm steps

### SEM-CODE-005: State Semantics
**Severity**: HIGH

- [ ] Confirm state transitions match the Feature design state machine
- [ ] Verify triggers and guards for transitions match defined conditions
- [ ] Ensure invalid transitions are prevented or handled explicitly

### SEM-CODE-006: Definition of Done Semantics
**Severity**: HIGH

- [ ] Verify each requirement in Definition of Done is implemented and testable
- [ ] Confirm implementation details (API, DB, domain entities) match the requirement section
- [ ] Validate requirement mappings to flows and algorithms are satisfied
- [ ] Ensure PRD coverage (FR/NFR) is preserved in implementation outcomes
- [ ] Ensure Design coverage (principles, constraints, components, sequences, db tables) is satisfied

### SEM-CODE-007: Overall Design Consistency
**Severity**: HIGH

- [ ] Confirm architecture vision and system boundaries are respected
- [ ] Validate architecture drivers (FR/NFR) are still satisfied by implementation
- [ ] Verify ADR decisions are reflected in code choices or explicitly overridden
- [ ] Confirm principles and constraints are enforced in implementation
- [ ] Validate domain model entities and invariants are respected by code
- [ ] Confirm component responsibilities, boundaries, and dependencies match the component model
- [ ] Validate API contracts and integration boundaries are honored
- [ ] Verify interactions and sequences are implemented as described
- [ ] Ensure database schemas, constraints, and access patterns align with design
- [ ] Confirm topology and tech stack choices are not contradicted
- [ ] Document any deviation with a rationale and approval

---

Use `{cypilot_path}/.core/requirements/code-checklist.md` for all generic code quality checks.
```

## Input

### Plan contract
- Runtime manifest: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml`
- Confirm phase identity, allowed scope, declared outputs, and downstream dependencies before modifying files.


### Tracked deliverables

- Claude outputs to regenerate and verify:
  - `.claude/agents/cypilot-generator.md`
  - `.claude/agents/cypilot-analyzer.md`
  - `.claude/agents/cypilot-codegen.md`
  - `.claude/agents/cypilot-pr-review.md`
- Intermediate report to create:
  - `out/phase-06-verification-report.md`

### Deterministic generation contract

- Canonical synopsis from `cypilot.clispec`:
  - `cpt --json generate-agents --agent <name> [options]`
- Relevant options for this phase:
  - `--agent <string>`
  - `--root <path>`
  - `--cypilot-root <path>`
  - `--dry-run <boolean>`
- Expected command for this phase:
  - `cpt --json generate-agents --agent claude`
- Expected result shape:
  - JSON object with `status`, `agent`, `workflows`, `skills`, `subagents`, and `errors`

### Bounded verification commands

- `make validate` runs `cpt validate`
- `make self-check` runs `cpt self-check`
- Targeted pytest for this phase:
  - `pytest tests/test_subagent_registration.py -v --tb=short`

### Out-of-scope repo-wide mutation

- `make update` runs `cpt update --source . --force`
- Do not run `make update` in this bounded phase unless the plan contract is explicitly widened first

### Current Claude agent directory snapshot

- `.claude/agents/cypilot-codegen.md`
- `.claude/agents/cypilot-phase-compiler.md`
- `.claude/agents/cypilot-phase-runner.md`
- `.claude/agents/cypilot-pr-review.md`
- `.claude/agents/cypilot-ralphex.md`

### Required verification report contents

- Regeneration command used and its exact result
- File-level status for each tracked Claude agent output
- Exact results for targeted `pytest`, `make validate`, and `make self-check`, plus an explicit note that `make update` / `cpt update --source . --force` were out of scope for this bounded phase
- Working tree status after regeneration and bounded verification, including confirmation that no broader repo-wide or bootstrap-only delivery deltas were accepted
- Final PASS or FAIL conclusion tied to the acceptance criteria

## Task

1. Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml` and confirm Phase 6 identity, the four tracked Claude outputs, the required verification report output, and the Phase 7 dependency.
2. Read `out/phase-05-test-update-summary.md` and extract the exact generation and verification checklist that Phase 6 must satisfy.
3. Read `CONTRIBUTING.md` and `Makefile` to confirm the self-hosted bootstrap rule, the meaning of `make update`, and why repo-wide bootstrap regeneration remains out of scope for this bounded phase.
4. Read `skills/cypilot/agents.toml`, inspect the current `.claude/agents/` directory contents, and read `tests/test_subagent_registration.py` to confirm the expected Claude agent outputs and targeted test scope.
5. Execute `cpt --json generate-agents --agent claude` from the repository root and capture the exact command line, exit status, JSON result, and any files created or updated.
6. Verify that `.claude/agents/cypilot-generator.md`, `.claude/agents/cypilot-analyzer.md`, `.claude/agents/cypilot-codegen.md`, and `.claude/agents/cypilot-pr-review.md` exist after regeneration, then record the exact file-level results.
7. Execute `pytest tests/test_subagent_registration.py -v --tb=short`, `make validate`, and `make self-check`, capturing the exact command line, exit status, and concise result summary for each command.
8. Inspect the post-verification working tree and confirm the final delivery diff is limited to the four tracked Claude outputs plus `out/phase-06-verification-report.md`; if broader repo-wide or bootstrap-only deltas appear, stop and report `FAIL` rather than widening the delivery surface implicitly.
9. Write `out/phase-06-verification-report.md` with the checklist from Phase 5, regeneration results, bounded verification command results, tracked output status, final diff status, and an explicit note that `make update` / `cpt update --source . --force` were treated as out-of-scope repo-wide mutation for this phase.
10. Self-verify the completed work against every acceptance criterion below, then report completion using the required output format.

## Acceptance Criteria

- [ ] `out/phase-05-test-update-summary.md` was read before regeneration or verification work began.
- [ ] The Claude regeneration command used the canonical `generate-agents` shape and its exact result was recorded.
- [ ] All four tracked Claude agent files were verified and their file-level outcomes were recorded in `out/phase-06-verification-report.md`.
- [ ] Exact results were recorded for `pytest tests/test_subagent_registration.py -v --tb=short`, `make validate`, and `make self-check`.
- [ ] `out/phase-06-verification-report.md` explicitly records that `make update` / `cpt update --source . --force` were treated as out-of-scope repo-wide mutation for this bounded phase.
- [ ] The final delivery diff is limited to the four tracked Claude agent outputs plus `out/phase-06-verification-report.md`, and the final diff status was recorded.
- [ ] `out/phase-06-verification-report.md` exists and contains the required verification summary.
- [ ] No unresolved `{...}` variables appear outside code fences.
- [ ] This phase file remains at or below 950 lines.

## Output Format

When complete, report results in this exact format:
```text
PHASE 6/7 COMPLETE
Status: PASS | FAIL
Files created: out/phase-06-verification-report.md
Files modified: .claude/agents/cypilot-generator.md, .claude/agents/cypilot-analyzer.md, .claude/agents/cypilot-codegen.md, .claude/agents/cypilot-pr-review.md
Acceptance criteria:
  [x] Criterion 1 — PASS
  [ ] Criterion 2 — FAIL: {reason}
  ...
Line count: {actual}/950
Notes: {any issues or decisions made}
```

Then generate a copy-pasteable prompt for the next phase inside a single code fence:

```text
Next phase prompt (copy-paste into new chat if needed):
```

```text
I have a Cypilot execution plan at:
  /Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml

Phase 6 is complete (PASS or FAIL).
Please read the plan manifest, then execute Phase 7: "Archive completed plan".
The phase file is: /Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/phase-07-archive-plan.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.
```
