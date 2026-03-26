```toml
[phase]
plan = "implement-systematic-pylint-remediation"
number = 4
total = 8
type = "implement"
title = "Control-flow hotspots I"
depends_on = [3]
input_files = ["pyproject.toml", "src/cypilot_proxy", "skills/cypilot/scripts/cypilot", "tests"]
output_files = ["pyproject.toml", "src/cypilot_proxy", "skills/cypilot/scripts/cypilot", "tests"]
outputs = ["out/phase-04-control-flow-hotspots-i.md"]
inputs = ["out/phase-01-message-priority.md", "out/phase-03-next-prompt.txt"]
```

## Preamble

This is a self-contained phase file. All rules, constraints, and kit content
are included below. Project files listed in the Task section must be read
at runtime. Follow the instructions exactly, run any EXECUTE commands as
written, and report results against the acceptance criteria at the end.

## What

Start the first structural cleanup wave for the most important control-flow hotspots. This phase focuses on reducing local complexity in the functions that trigger the first batch of refactor metrics, while preserving behavior and keeping changes bounded enough to validate clearly. Avoid tackling duplication or low-priority style cleanup here.

## Prior Context

Phase 1 created the staged pylint rollout baseline.
Phase 2 resolved critical runtime/correctness diagnostics.
Phase 3 resolved the high-risk warning family and recorded any deferred backlog.
This phase now opens the first limited refactor family under the same staged baseline.

## User Decisions

### Already Decided (pre-resolved during planning)
- **Lifecycle**: `archive`
- **Execution mode**: autonomous phased cleanup
- **Priority family for this phase**: first control-flow hotspot group
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
- MUST read `out/phase-01-message-priority.md` and `out/phase-03-next-prompt.txt` before editing.
- MUST enable only the first hotspot metrics assigned to this phase.
- MUST preserve behavior while reducing control-flow complexity.
- MUST prefer extraction, decomposition, and clearer intermediate helpers over suppression.
- MUST keep core logic testable without heavy integration setup.
- MUST NOT use the refactor as a pretext for broad architecture rewrites or duplicate-code cleanup assigned to later phases.
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
- `R0914`
- `R0912`
- `R0915`

### Runtime inputs to inspect
- `out/phase-01-message-priority.md`
- `out/phase-03-next-prompt.txt`

## Task

1. Read `out/phase-01-message-priority.md`. Read `out/phase-03-next-prompt.txt`. Read `pyproject.toml`. Recover the assigned hotspot IDs and current baseline.
2. Enable only `R0914`, `R0912`, and `R0915` in `pyproject.toml`.
3. Read `src/cypilot_proxy`. Read `skills/cypilot/scripts/cypilot`. Inspect the failing files there, then refactor only the hotspots reported for this phase using behavior-preserving extractions, helper functions, or localized decompositions.
4. Read `tests`. Add or update tests anywhere refactoring changes control flow or risks regression.
5. Run `EXECUTE: make pylint` and confirm the enabled hotspot IDs for this phase are clean; continue iterating until those enabled refactor diagnostics pass.
6. Run targeted tests covering the changed behavior and confirm they pass.
7. Write `out/phase-04-control-flow-hotspots-i.md` summarizing the enabled IDs, principal hotspots reduced, files changed, tests run, and residual backlog intentionally deferred.
8. Self-verify that only this phase's hotspot IDs were enabled, that the `out/` report exists, and that no unresolved placeholder variables remain.

## Acceptance Criteria

- [ ] Only `R0914`, `R0912`, and `R0915` were enabled for this phase.
- [ ] The enabled hotspot diagnostics are resolved in the current `make pylint` run.
- [ ] Refactors preserve behavior and are protected by appropriate tests.
- [ ] `out/phase-04-control-flow-hotspots-i.md` exists and documents enabled IDs, hotspots reduced, files changed, tests run, and residual backlog.
- [ ] No duplicate-code or convention families were intentionally enabled in this phase.
- [ ] No unresolved placeholder variables outside code fences.
- [ ] Phase output stays within the stated scope boundary.

## Output Format

When complete, report results in this exact format:
```text
PHASE 4/8 COMPLETE
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

Phase 4 is complete ({status}).
Please read the plan manifest, then execute Phase 5: "Control-flow hotspots II".
The phase file is: .bootstrap/.plans/implement-systematic-pylint-remediation/phase-05-control-flow-hotspots-ii.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.
```

Then ask: `Continue in this chat? [y/n]`
