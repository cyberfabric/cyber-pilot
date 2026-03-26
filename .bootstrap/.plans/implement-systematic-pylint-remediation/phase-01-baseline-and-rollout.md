```toml
[phase]
plan = "implement-systematic-pylint-remediation"
number = 1
total = 8
type = "implement"
title = "Baseline and rollout mechanism"
depends_on = []
input_files = ["pyproject.toml", "Makefile", ".github/workflows/ci.yml"]
output_files = ["pyproject.toml", "Makefile"]
outputs = ["out/phase-01-rollout-baseline.md", "out/phase-01-message-priority.md"]
inputs = []
```

## Preamble

This is a self-contained phase file. All rules, constraints, and kit content
are included below. Project files listed in the Task section must be read
at runtime. Follow the instructions exactly, run any EXECUTE commands as
written, and report results against the acceptance criteria at the end.

## What

Establish the repository-wide pylint rollout mechanism before any real cleanup starts. This phase creates a safe baseline where all pylint checks are disabled by default, preserves the existing `make pylint` and CI contract, and records the authoritative priority order for re-enabling diagnostics. Do not attempt broad source cleanup here; the deliverable is the rollout framework plus the phase handoff artifacts.

## Prior Context

The repository currently runs `make pylint` against `src/cypilot_proxy` and `skills/cypilot/scripts/cypilot`.
Current top pylint families are dominated by conventions and refactors, but there are also runtime-relevant `E*` and `W*` diagnostics.
The user requested this exact strategy: disable everything first, then re-enable diagnostics one by one in priority order and fix each category before enabling the next.
CI currently invokes `make pylint` and that contract must remain stable.

## User Decisions

### Already Decided (pre-resolved during planning)
- **Lifecycle**: `archive`
- **Rollout strategy**: disable all pylint checks first, then re-enable one message or tightly-coupled family at a time
- **Priority direction**: highest-risk correctness/runtime issues first, style/docstrings last
- **Lint entrypoint to preserve**: `make pylint`

### Decisions Needed During This Phase
#### Review Gates
- [ ] **Review rollout baseline** — present the exact enabled/disabled strategy in the completion report before Phase 2 begins

#### Confirmation Points
- [ ] **Confirm no scope creep** — this phase must not broaden into fixing unrelated source issues

#### User Input Required
- [ ] **None** — no additional user input is required during execution

## Rules

### Rollout Rules
- MUST treat `pyproject.toml` as the authoritative pylint configuration file.
- MUST preserve `make pylint` as the canonical lint entrypoint used locally and in CI.
- MUST disable all pylint checks by default before beginning staged re-enable.
- MUST represent the rollout as explicit ordered message IDs or tightly-coupled families, not vague categories.
- MUST keep the rollout deterministic so each later phase enables only its assigned diagnostics.
- MUST record the exact priority order used for later phases.
- MUST NOT silently weaken lint scope by changing targets away from `src/cypilot_proxy` and `skills/cypilot/scripts/cypilot`.
- MUST NOT change CI to bypass pylint.
- MUST NOT fix unrelated source files in this phase unless required to keep the rollout mechanism valid.

### Engineering and Quality Rules
- Code follows project conventions from config.
- TDD applies to new behavior where practical; if no executable behavior changes exist in this phase, document why.
- DRY: remove duplication only when necessary for the rollout mechanism.
- KISS: prefer the simplest correct config shape for staged re-enable.
- YAGNI: add no speculative lint tooling beyond what this rollout needs.
- Code passes quality checklist.
- Functions and methods are appropriately sized.
- Error handling is consistent.
- Build succeeds, no compilation errors.
- Linter passes for the diagnostics enabled in this phase.

### Verbatim CODEBASE engineering obligations
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

### Verbatim CODEBASE validation obligations
- [ ] Code files exist and contain implementation
- [ ] Code is not placeholder/stub (no TODO/FIXME/unimplemented!)
- [ ] Build succeeds, no compilation errors
- [ ] Linter passes, no linter errors
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All e2e tests pass (if applicable)
- [ ] Coverage meets project requirements
- [ ] No TODO/FIXME/XXX/HACK in domain/service layers
- [ ] No unimplemented!/todo! in business logic
- [ ] TDD: New/changed behavior covered by tests
- [ ] SOLID: Responsibilities separated; dependencies injectable
- [ ] DRY: No copy-paste duplication
- [ ] KISS: No unnecessary complexity
- [ ] YAGNI: No speculative abstractions

## Input

### Current contracts and facts
- `pyproject.toml` already contains active `[tool.pylint.*]` sections and a commented example `disable` block.
- `Makefile` currently runs pylint through `make pylint` with `PYTHONPATH=src:skills/cypilot/scripts`.
- `.github/workflows/ci.yml` invokes `make pylint` in the `pylint` job.
- Current diagnostic triage from planning:
  - P0: `E0602`, `E1135`, `E0102`
  - P1: `W0718`, `W1510`, `W0707`, `W0404`, `W0212`, `W0603`, `W0612`, `W0613`, `W0611`
  - P2: `R0914`, `R0912`, `R0915`
  - P3: `R0911`, `R1702`, `R1705`, `R0913`, `R0917`, `R0902`
  - P4: `R0401`, `R0801`
  - P5: `C0415`, `C0413`, `C0411`, `C0414`, `C0301`, `C0302`, `C0303`, `C0305`
  - P6: `C0103`, `C0114`, `C0115`, `C0116`

## Task

1. Read `pyproject.toml` and confirm the current pylint configuration baseline.
2. Read `Makefile` and confirm the canonical local lint entrypoint remains `make pylint`.
3. Read `.github/workflows/ci.yml` and confirm CI still invokes `make pylint`.
4. Update `pyproject.toml` so pylint starts from a `disable=all` baseline in the canonical messages-control section, while preserving existing non-message settings such as paths, formatting, and design thresholds.
5. If needed, make the smallest related `Makefile` adjustment required to support staged message rollout while keeping `make pylint` as the canonical command and preserving the current lint targets.
6. Run `EXECUTE: make pylint` and verify the command still runs under the new baseline configuration; capture whether the baseline is clean and whether only intentionally enabled checks would fail.
7. Write `out/phase-01-rollout-baseline.md` documenting the exact config baseline, command contract, and any supporting `Makefile` behavior needed for later phases.
8. Write `out/phase-01-message-priority.md` documenting the authoritative diagnostic rollout order, the message IDs assigned to each later phase, and the rule that later phases must not enable out-of-order diagnostics.
9. Self-verify that no unrelated source cleanup was done, that CI/local lint entrypoints still point to `make pylint`, and that the two `out/` handoff files are complete.

## Acceptance Criteria

- [ ] `pyproject.toml` contains a valid pylint disable-all baseline for staged rollout.
- [ ] `make pylint` remains the canonical lint command used locally and by CI.
- [ ] Any `Makefile` changes are minimal and strictly in service of staged rollout.
- [ ] `out/phase-01-rollout-baseline.md` exists and explains the baseline contract.
- [ ] `out/phase-01-message-priority.md` exists and defines the ordered diagnostic families for Phases 2-8.
- [ ] No unrelated source cleanup was performed in this phase.
- [ ] No unresolved placeholder variables outside code fences.
- [ ] Phase output stays within the stated scope boundary.

## Output Format

When complete, report results in this exact format:
```text
PHASE 1/8 COMPLETE
Status: PASS | FAIL
Files created: {list}
Files modified: {list}
Acceptance criteria:
  [x] Criterion 1 — PASS
  [ ] Criterion 2 — FAIL: {reason}
  ...
Line count: {actual}/{budget}
Notes: {any issues or decisions made}
```

Then generate a **copy-pasteable prompt** for the next phase inside a single code fence:

```text
Next phase prompt (copy-paste into new chat if needed):
```

```text
I have a Cypilot execution plan at:
  .bootstrap/.plans/implement-systematic-pylint-remediation/plan.toml

Phase 1 is complete ({status}).
Please read the plan manifest, then execute Phase 2: "Critical runtime errors".
The phase file is: .bootstrap/.plans/implement-systematic-pylint-remediation/phase-02-critical-runtime-errors.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.
```

Then ask: `Continue in this chat? [y/n]`
