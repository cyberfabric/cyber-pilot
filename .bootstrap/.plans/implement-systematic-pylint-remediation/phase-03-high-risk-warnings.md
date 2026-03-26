```toml
[phase]
plan = "implement-systematic-pylint-remediation"
number = 3
total = 8
type = "implement"
title = "High-risk warnings"
depends_on = [2]
input_files = ["pyproject.toml", "src/cypilot_proxy", "skills/cypilot/scripts/cypilot", "tests"]
output_files = ["pyproject.toml", "src/cypilot_proxy", "skills/cypilot/scripts/cypilot", "tests"]
outputs = ["out/phase-03-high-risk-warnings.md"]
inputs = ["out/phase-01-message-priority.md", "out/phase-02-critical-errors.md"]
```

## Preamble

This is a self-contained phase file. All rules, constraints, and kit content
are included below. Project files listed in the Task section must be read
at runtime. Follow the instructions exactly, run any EXECUTE commands as
written, and report results against the acceptance criteria at the end.

## What

Resolve the next safety-relevant warning family after critical runtime errors are closed. This phase focuses on warnings that can hide bugs, weaken error handling, or leave risky behavior in place, while still avoiding deeper structural refactors assigned to later phases. Keep the work bounded to the warning IDs explicitly assigned here.

## Prior Context

Phase 1 defined the rollout baseline and message ordering.
Phase 2 closed the critical runtime/correctness diagnostics and recorded its residual backlog.
This phase must preserve those earlier wins and build on the same staged baseline.
The authoritative ordering remains in `out/phase-01-message-priority.md`.

## User Decisions

### Already Decided (pre-resolved during planning)
- **Lifecycle**: `archive`
- **Execution mode**: autonomous phased cleanup
- **Priority family for this phase**: high-risk warnings only
- **Out-of-scope**: complexity refactors, duplicate-code cleanup, style/docstrings/naming

### Decisions Needed During This Phase
#### Review Gates
- [ ] **Review warning-family closure** — verify the completion report lists the exact enabled warning IDs and zero remaining failures for those IDs

#### Confirmation Points
- [ ] **Confirm no category drift** — do not enable refactor or convention families in this phase

#### User Input Required
- [ ] **None** — no additional user input is required during execution

## Rules

### Phase Scope Rules
- MUST read `out/phase-01-message-priority.md` and `out/phase-02-critical-errors.md` before editing.
- MUST enable only the warning IDs assigned to this phase.
- MUST fix only diagnostics in the enabled warning set, except for minimal unblockers required to make those warnings pass safely.
- MUST preserve the fixes from Phase 2 and avoid reopening already resolved critical diagnostics.
- MUST NOT enable the later refactor or convention families assigned to Phases 4-8.
- MUST NOT suppress warnings by weakening behavior or swallowing errors.

### Safety and Quality Rules
- Errors fail explicitly.
- Partial failures are handled.
- Recovery actions are defined where relevant.
- Proper error chaining is used when re-raising.
- Sensitive or unsafe patterns are not introduced.
- Public APIs are covered.
- Error paths are covered.
- Regression scenarios are covered.
- Tests are readable and independent.
- Linter passes for the enabled diagnostics in this phase.
- Build succeeds, no compilation errors.

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

### Enabled warning family for this phase
- `W0718`
- `W1510`
- `W0707`
- `W0404`
- `W0212`
- `W0603`
- `W0612`
- `W0613`
- `W0611`

### Runtime inputs to inspect
- `out/phase-01-message-priority.md`

## Task

1. Read `out/phase-01-message-priority.md`. Read `out/phase-02-critical-errors.md`. Read `pyproject.toml`. Recover the baseline, the assigned warning IDs, and any residual constraints from Phase 2.
2. Enable only this phase's warning IDs in `pyproject.toml`.
3. Read `src/cypilot_proxy`. Read `skills/cypilot/scripts/cypilot`. Inspect the failing files there, then implement the smallest safe fixes needed to eliminate the enabled warnings without broad structural refactors.
4. Read `tests`. Add or update tests when behavior or regression risk justifies them, especially for exception handling, subprocess invocation, or import behavior changes.
5. Run `EXECUTE: make pylint` and confirm the enabled warning IDs for this phase are clean; continue iterating until those enabled warnings pass.
6. Run targeted tests covering the changed behavior and confirm they pass.
7. Write `out/phase-03-high-risk-warnings.md` summarizing the enabled IDs, files changed, tests run, and residual backlog intentionally deferred to later phases.
8. Self-verify that only this phase's warning IDs were enabled, that the `out/` report exists, and that no unresolved placeholder variables remain.

## Acceptance Criteria

- [ ] Only the warning IDs assigned to this phase were enabled.
- [ ] The enabled warning diagnostics are resolved in the current `make pylint` run.
- [ ] Any changed behavior is covered by appropriate tests.
- [ ] `out/phase-03-high-risk-warnings.md` exists and documents enabled IDs, files changed, tests run, and residual backlog.
- [ ] No refactor or convention families were intentionally enabled in this phase.
- [ ] No unresolved placeholder variables outside code fences.
- [ ] Phase output stays within the stated scope boundary.

## Output Format

When complete, report results in this exact format:
```text
PHASE 3/8 COMPLETE
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

Phase 3 is complete ({status}).
Please read the plan manifest, then execute Phase 4: "Control-flow hotspots I".
The phase file is: .bootstrap/.plans/implement-systematic-pylint-remediation/phase-04-control-flow-hotspots-i.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.
```

Then ask: `Continue in this chat? [y/n]`
