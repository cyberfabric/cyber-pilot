```toml
[phase]
plan = "add-analyzer-generator-review-loop"
number = 5
total = 7
type = "implement"
title = "Update tests for the expanded subagent set"
depends_on = [4]
input_manifest = ""
input_signature = ""
input_files = [".bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml", "tests/test_subagent_registration.py", "skills/cypilot/scripts/cypilot/commands/agents.py", "skills/cypilot/agents.toml"]
output_files = ["tests/test_subagent_registration.py"]
outputs = ["out/phase-05-test-update-summary.md"]
inputs = ["out/phase-04-generation-pipeline.md"]
```

## Preamble

This is a self-contained phase file. All rules, constraints, and kit content
are included below. Project files listed in the Task section must be read
at runtime. Follow the instructions exactly, run any EXECUTE commands as
written, and report results against the acceptance criteria at the end.

## What

Update `tests/test_subagent_registration.py` so it validates the current expanded subagent registry and host-generation behavior instead of the old two-agent assumption. Keep the work tightly scoped to discovery and generation assertions, preserve legacy-agent coverage and Windsurf skip behavior, and produce a short handoff summary in `out/phase-05-test-update-summary.md`. Do not modify unrelated test modules or execute the phase beyond the requested file edits and self-verification.

## Prior Context

- Phase 5 of 7 depends on Phase 4.
- The only project file to modify in this phase is `tests/test_subagent_registration.py`.
- The required intermediate output for this phase is `out/phase-05-test-update-summary.md`.
- `_discover_kit_agents()` loads installed-kit `agents.toml` files before the core skill fallback.
- `_process_single_agent()` generates subagent files only for tools present in `_TOOL_AGENT_CONFIG` and skips subagent generation when the tool has no config or when no agents are discovered.
- After Phase 2, current canonical agent definitions are `cypilot-codegen`, `cypilot-pr-review`, `cypilot-ralphex`, `cypilot-phase-runner`, `cypilot-phase-compiler`, `cypilot-generator`, and `cypilot-analyzer`.
- `windsurf` is not present in `_TOOL_AGENT_CONFIG`, so Windsurf subagent generation remains a skip path.
- OpenAI emits one `.toml` file per discovered agent and removes stale `cypilot*.toml` files not in the desired set.

## User Decisions
### Already Decided (pre-resolved during planning)
- **Phase identity**: Phase 5 of 7, `implement`
- **Editable scope**: `tests/test_subagent_registration.py` only
- **Required handoff**: `out/phase-05-test-update-summary.md`
- **Compatibility floor**: keep legacy-agent assertions and Windsurf skip behavior covered

### Decisions Needed During This Phase
#### Review Gates
- None.

#### Confirmation Points
- None.

#### User Input Required
- None.

## Rules
### Scope and file boundaries
- MUST modify only `tests/test_subagent_registration.py` under project sources for this phase.
- MUST create or update `out/phase-05-test-update-summary.md` as the phase handoff.
- MUST keep the work tightly scoped to subagent discovery, registration, and host-generation behavior.
- MUST NOT edit unrelated test modules, workflow documents, architecture artifacts, or host output files in this phase.

### Behavioral coverage
- MUST expand expectations from the old two-agent model to the current generalized-plus-specialized registry.
- MUST preserve explicit assertions for the legacy agents `cypilot-codegen` and `cypilot-pr-review`.
- MUST preserve explicit assertions for Windsurf skip behavior.
- MUST keep host-specific expectations aligned with the actual implementation in `skills/cypilot/scripts/cypilot/commands/agents.py` and the canonical registry in `skills/cypilot/agents.toml`.
- MUST keep OpenAI expectations tied to one output `.toml` file per discovered agent and no combined `cypilot-agents.toml` file.

### Execution discipline
- MUST read every runtime input listed in the Task section before editing.
- MUST make expectations concrete as names, counts, output paths, or skip reasons; do not leave vague placeholders.
- MUST self-verify against every acceptance criterion before reporting completion.
- MUST NOT broaden the phase into regeneration, verification, or execution of later phases.

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


### Phase contract
- Deliverable: updated `tests/test_subagent_registration.py` plus `out/phase-05-test-update-summary.md`.
- Runtime dependencies: `out/phase-04-generation-pipeline.md`, `tests/test_subagent_registration.py`, `skills/cypilot/scripts/cypilot/commands/agents.py`, and `skills/cypilot/agents.toml`.
- Downstream dependency: Phase 6 consumes `out/phase-05-test-update-summary.md`.

### Stable implementation facts
- After Phase 2, the canonical registry defines seven agents: `cypilot-codegen`, `cypilot-pr-review`, `cypilot-ralphex`, `cypilot-phase-runner`, `cypilot-phase-compiler`, `cypilot-generator`, and `cypilot-analyzer`.
- Claude, Cursor, and Copilot generate one markdown-based proxy file per discovered agent.
- OpenAI generates one `.toml` proxy file per discovered agent.
- Windsurf remains a supported host for workflows and skills, but subagent proxy generation is skipped.
- Discovery order is installed kits first, then the core `skills/cypilot` fallback.

## Task
1. Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml` and confirm Phase 5 identity, allowed edit scope, required handoff file, and the Phase 6 dependency.
2. Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/out/phase-04-generation-pipeline.md`, `/Volumes/CaseSensitive/coding/cypilot/skills/cypilot/scripts/cypilot/commands/agents.py`, and `/Volumes/CaseSensitive/coding/cypilot/skills/cypilot/agents.toml`; extract the current discovered agent set, host-specific output behavior, OpenAI per-agent TOML behavior, and Windsurf skip condition that the tests must reflect.
3. Read `/Volumes/CaseSensitive/coding/cypilot/tests/test_subagent_registration.py` and identify fixtures, discovery assertions, host-output counts, and compatibility checks that still assume only two generated agents or two created files.
4. Update `tests/test_subagent_registration.py` so discovery expectations, fixture data, and per-host assertions match the current seven-agent registry while preserving explicit checks for `cypilot-codegen`, `cypilot-pr-review`, and Windsurf skip behavior.
5. Keep OpenAI assertions explicit about one `.toml` file per discovered agent, no combined `cypilot-agents.toml`, and content checks that continue to validate the generated proxy instructions.
6. Write `out/phase-05-test-update-summary.md` summarizing the changed expected agent names, created-file counts, dry-run or idempotency count changes, and any preserved compatibility assertions.
7. Self-verify the modified test file and summary against the acceptance criteria, then report completion using the required output format.

## Acceptance Criteria
- [ ] Only `tests/test_subagent_registration.py` is modified among project source files for this phase.
- [ ] `out/phase-05-test-update-summary.md` exists and summarizes changed names, counts, and preserved compatibility assertions.
- [ ] Discovery and generation expectations no longer hardcode a two-agent model or a stale five-agent model where the canonical registry now defines seven agents including `cypilot-generator` and `cypilot-analyzer`.
- [ ] Assertions for legacy agents `cypilot-codegen` and `cypilot-pr-review` remain present and valid.
- [ ] Windsurf skip behavior remains explicitly covered and still expects zero created or updated subagent outputs.
- [ ] Host-specific assertions remain aligned with implementation facts, including per-agent markdown outputs for Claude, Cursor, and Copilot plus per-agent `.toml` outputs for OpenAI with no combined `cypilot-agents.toml` file.
- [ ] No unresolved placeholder variables appear outside code fences.
- [ ] This phase file remains at or below 900 lines.

## Output Format

When complete, report results in this exact format:
```text
PHASE 5/7 COMPLETE
Status: PASS | FAIL
Files created: out/phase-05-test-update-summary.md
Files modified: tests/test_subagent_registration.py
Acceptance criteria:
  [x] Criterion 1 — PASS
  [ ] Criterion 2 — FAIL: reason
  ...
Line count: actual/900
Notes: any issues or decisions made
```

Then generate a copy-pasteable prompt for the next phase inside a single code fence:

```text
Next phase prompt (copy-paste into new chat if needed):
```

```text
I have a Cypilot execution plan at:
  /Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml

Phase 5 is complete (PASS or FAIL).
Please read the plan manifest, then execute Phase 6: "Regenerate agent outputs and verify the repo".
The phase file is: /Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/phase-06-regeneration-verification.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.
```
