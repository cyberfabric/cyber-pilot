```toml
[phase]
plan = "implement-systematic-pylint-remediation"
number = 5
total = 8
type = "implement"
title = "Control-flow hotspots II"
depends_on = [4]
input_files = ["pyproject.toml", "src/cypilot_proxy", "skills/cypilot/scripts/cypilot", "tests"]
output_files = ["pyproject.toml", "src/cypilot_proxy", "skills/cypilot/scripts/cypilot", "tests"]
outputs = ["out/phase-05-control-flow-hotspots-ii.md"]
inputs = ["out/phase-01-message-priority.md", "out/phase-04-control-flow-hotspots-i.md"]
```

## Preamble

This is a self-contained phase file. All rules, constraints, and kit content
are included below. Project files listed in the Task section must be read
at runtime. Follow the instructions exactly, run any EXECUTE commands as
written, and report results against the acceptance criteria at the end.

## What

Finish the second structural cleanup wave for the remaining high-priority control-flow metrics. This phase continues behavior-preserving refactoring, but it is narrower than a general rewrite: only the refactor IDs assigned here may be enabled and resolved. Preserve previous gains and avoid mixing this work with duplication or style cleanup.

## Prior Context

Phase 1 created the staged pylint rollout baseline.
Phases 2 and 3 closed critical runtime errors and high-risk warnings.
Phase 4 handled the first group of control-flow hotspots.
This phase finishes the remaining prioritized hotspot family before architectural and style cleanup begins.

## User Decisions

### Already Decided (pre-resolved during planning)
- **Lifecycle**: `archive`
- **Execution mode**: autonomous phased cleanup
- **Priority family for this phase**: second control-flow hotspot group
- **Out-of-scope**: duplicate-code cleanup, import-format cleanup, naming/docstrings

### Decisions Needed During This Phase
#### Review Gates
- [ ] **Review hotspot reduction** — verify the completion report identifies the exact refactor IDs enabled and the primary functions/modules simplified

#### Confirmation Points
- [ ] **Confirm behavior preservation** — refactors must not change user-visible behavior without corresponding tests

#### User Input Required
- [ ] **None** — no additional user input is required during execution

## Rules

### Phase Scope Rules
- MUST read `out/phase-01-message-priority.md` and `out/phase-04-control-flow-hotspots-i.md` before editing.
- MUST enable only the second hotspot metrics assigned to this phase.
- MUST preserve behavior while reducing control-flow complexity.
- MUST prefer extraction, helper normalization, and simplified branching over suppression.
- MUST keep core logic testable without heavy integration setup.
- MUST NOT use this phase for duplicate-code cleanup or broad architecture rewrites assigned to Phase 6.
- MUST NOT enable later-phase import-format, naming, or docstring families.

### Engineering and Testing Rules
- Each module, class, or function has one reason to change.
- Shared logic is extracted with clear ownership.
- The simplest correct solution was chosen.
- No speculative abstractions are introduced.
- Refactoring happens only after tests pass or with immediate regression protection added.
- Behavior stays unchanged during refactoring.
- Public APIs are covered.
- Error paths are covered.
- Regression scenarios are covered.
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

### Enabled hotspot family for this phase
- `R0911`
- `R1702`
- `R1705`
- `R0913`
- `R0917`
- `R0902`

### Runtime inputs to inspect
- `out/phase-01-message-priority.md`

## Task

1. Read `out/phase-01-message-priority.md`. Read `out/phase-04-control-flow-hotspots-i.md`. Read `pyproject.toml`. Recover the assigned hotspot IDs and current baseline.
2. Enable only `R0911`, `R1702`, `R1705`, `R0913`, `R0917`, and `R0902` in `pyproject.toml`.
3. Read `src/cypilot_proxy`. Read `skills/cypilot/scripts/cypilot`. Inspect the failing files there, then refactor only the hotspots reported for this phase using behavior-preserving decompositions and clearer control flow.
4. Read `tests`. Add or update tests anywhere refactoring changes control flow or risks regression.
5. Run `EXECUTE: make pylint` and confirm the enabled hotspot IDs for this phase are clean; continue iterating until those enabled refactor diagnostics pass.
6. Run targeted tests covering the changed behavior and confirm they pass.
7. Write `out/phase-05-control-flow-hotspots-ii.md` summarizing the enabled IDs, principal hotspots reduced, files changed, tests run, and residual backlog intentionally deferred.
8. Self-verify that only this phase's hotspot IDs were enabled, that the `out/` report exists, and that no unresolved placeholder variables remain.

## Acceptance Criteria

- [ ] Only `R0911`, `R1702`, `R1705`, `R0913`, `R0917`, and `R0902` were enabled for this phase.
- [ ] The enabled hotspot diagnostics are resolved in the current `make pylint` run.
- [ ] Refactors preserve behavior and are protected by appropriate tests.
- [ ] `out/phase-05-control-flow-hotspots-ii.md` exists and documents enabled IDs, hotspots reduced, files changed, tests run, and residual backlog.
- [ ] No duplicate-code or convention families were intentionally enabled in this phase.
- [ ] No unresolved placeholder variables outside code fences.
- [ ] Phase output stays within the stated scope boundary.

## Output Format

When complete, report results in this exact format:
```text
PHASE 5/8 COMPLETE
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

Phase 5 is complete ({status}).
Please read the plan manifest, then execute Phase 6: "Architecture and duplication hygiene".
The phase file is: .bootstrap/.plans/implement-systematic-pylint-remediation/phase-06-architecture-and-duplication-hygiene.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.
```

Then ask: `Continue in this chat? [y/n]`
