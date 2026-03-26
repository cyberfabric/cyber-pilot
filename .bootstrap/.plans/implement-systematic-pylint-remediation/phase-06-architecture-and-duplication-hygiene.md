```toml
[phase]
plan = "implement-systematic-pylint-remediation"
number = 6
total = 8
type = "implement"
title = "Architecture and duplication hygiene"
depends_on = [5]
input_files = ["pyproject.toml", "src/cypilot_proxy", "skills/cypilot/scripts/cypilot", "tests"]
output_files = ["pyproject.toml", "src/cypilot_proxy", "skills/cypilot/scripts/cypilot", "tests"]
outputs = ["out/phase-06-architecture-and-duplication-hygiene.md"]
inputs = ["out/phase-01-message-priority.md", "out/phase-05-control-flow-hotspots-ii.md"]
```

## Preamble

This is a self-contained phase file. All rules, constraints, and kit content
are included below. Project files listed in the Task section must be read
at runtime. Follow the instructions exactly, run any EXECUTE commands as
written, and report results against the acceptance criteria at the end.

## What

Address the architectural hygiene backlog that remains after the control-flow cleanup: cyclic imports and duplicate code. This phase is allowed to perform broader structural extraction than previous phases, but it must still preserve behavior, maintain testability, and keep changes traceable. Do not mix in final import-format or docstring cleanup unless strictly incidental.

## Prior Context

Phase 1 established the staged rollout baseline.
Phases 2-5 closed the prioritized runtime, warning, and control-flow families.
This phase is the first one explicitly allowed to remove duplicate logic and untangle import cycles.
Later style and docstring work must remain deferred.

## User Decisions

### Already Decided (pre-resolved during planning)
- **Lifecycle**: `archive`
- **Execution mode**: autonomous phased cleanup
- **Priority family for this phase**: cyclic imports and duplicate code
- **Out-of-scope**: final import-format normalization, naming/docstrings cleanup

### Decisions Needed During This Phase
#### Review Gates
- [ ] **Review architecture cleanup** — verify the completion report names the resolved import cycles and duplication hotspots

#### Confirmation Points
- [ ] **Confirm behavior preservation** — structural extraction must not change semantics without tests

#### User Input Required
- [ ] **None** — no additional user input is required during execution

## Rules

### Phase Scope Rules
- MUST read `out/phase-01-message-priority.md` and `out/phase-05-control-flow-hotspots-ii.md` before editing.
- MUST enable only `R0401` and `R0801` in this phase.
- MUST prefer clear module boundaries, shared helpers with explicit ownership, and dependency inversion where helpful.
- MUST preserve behavior while removing cycles or duplication.
- MUST keep core logic testable without heavy integration setup.
- MUST NOT broaden into style-only cleanup assigned to later phases.
- MUST NOT suppress duplicate-code findings without a concrete architectural reason captured in the report.

### Engineering and Quality Rules
- Each module, class, or function has one reason to change.
- Behavior is extended through composition or configuration when appropriate.
- High-level modules do not depend directly on low-level details when avoidable.
- Copy-paste duplication is removed with clear ownership.
- Changes stay localized where possible.
- Public APIs are covered.
- Regression scenarios are covered.
- Build succeeds, no compilation errors.
- Linter passes for the enabled diagnostics in this phase.

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

### Enabled architecture family for this phase
- `R0401`
- `R0801`

### Runtime inputs to inspect
- `out/phase-01-message-priority.md`

## Task

1. Read `out/phase-01-message-priority.md`. Read `out/phase-05-control-flow-hotspots-ii.md`. Read `pyproject.toml`. Recover the assigned architecture IDs and current baseline.
2. Enable only `R0401` and `R0801` in `pyproject.toml`.
3. Read `src/cypilot_proxy`. Read `skills/cypilot/scripts/cypilot`. Inspect the failing files there, then remove cyclic imports and duplicate-code hotspots using behavior-preserving extractions, shared helpers, or dependency-boundary cleanup.
4. Read `tests`. Add or update tests anywhere structural extraction or dependency movement risks regression.
5. Run `EXECUTE: make pylint` and confirm `R0401` and `R0801` are clean; continue iterating until those enabled diagnostics pass.
6. Run targeted tests covering the changed behavior and confirm they pass.
7. Write `out/phase-06-architecture-and-duplication-hygiene.md` summarizing the enabled IDs, cycles removed, duplication hotspots resolved, files changed, tests run, and any residual backlog.
8. Self-verify that only this phase's architecture IDs were enabled, that the `out/` report exists, and that no unresolved placeholder variables remain.

## Acceptance Criteria

- [ ] Only `R0401` and `R0801` were enabled for this phase.
- [ ] The enabled architecture diagnostics are resolved in the current `make pylint` run.
- [ ] Structural changes preserve behavior and are protected by appropriate tests.
- [ ] `out/phase-06-architecture-and-duplication-hygiene.md` exists and documents enabled IDs, hotspots resolved, files changed, tests run, and residual backlog.
- [ ] No later style or docstring families were intentionally enabled in this phase.
- [ ] No unresolved placeholder variables outside code fences.
- [ ] Phase output stays within the stated scope boundary.

## Output Format

When complete, report results in this exact format:
```text
PHASE 6/8 COMPLETE
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

Phase 6 is complete ({status}).
Please read the plan manifest, then execute Phase 7: "Import and format normalization".
The phase file is: .bootstrap/.plans/implement-systematic-pylint-remediation/phase-07-import-and-format-normalization.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.
```

Then ask: `Continue in this chat? [y/n]`
