```toml
[phase]
plan = "implement-systematic-pylint-remediation"
number = 8
total = 8
type = "implement"
title = "Naming, docstrings, and steady-state"
depends_on = [7]
input_files = ["pyproject.toml", "src/cypilot_proxy", "skills/cypilot/scripts/cypilot", "tests"]
output_files = ["pyproject.toml", "src/cypilot_proxy", "skills/cypilot/scripts/cypilot", "tests"]
outputs = ["out/phase-08-steady-state.md"]
inputs = ["out/phase-01-message-priority.md", "out/phase-07-import-and-format-normalization.md"]
```

## Preamble

This is a self-contained phase file. All rules, constraints, and kit content
are included below. Project files listed in the Task section must be read
at runtime. Follow the instructions exactly, run any EXECUTE commands as
written, and report results against the acceptance criteria at the end.

## What

Finish the pylint rollout by enabling the last low-priority readability conventions and leaving the repository in a stable steady-state configuration. This phase handles naming and docstring families last on purpose, so earlier correctness and structural work stays prioritized. The final deliverable is both clean diagnostics for the remaining enabled set and a steady-state lint configuration that reflects the achieved rollout state.

## Prior Context

Phases 1-7 established the baseline and resolved all higher-priority runtime, warning, refactor, architecture, and formatting families.
This final phase closes the remaining naming/docstring readability backlog.
The plan lifecycle selected during planning is `archive`.
After this phase, the plan should report full completion rather than another phase handoff.

## User Decisions

### Already Decided (pre-resolved during planning)
- **Lifecycle**: `archive`
- **Execution mode**: autonomous phased cleanup
- **Priority family for this phase**: naming and docstring conventions
- **Final deliverable**: stable post-rollout pylint configuration plus final summary report

### Decisions Needed During This Phase
#### Review Gates
- [ ] **Review steady-state** — verify the completion report lists the exact final convention IDs enabled and the resulting steady-state config posture

#### Confirmation Points
- [ ] **Confirm final scope** — no new lower-value cleanup should be invented beyond the remaining enabled convention family

#### User Input Required
- [ ] **None** — no additional user input is required during execution

## Rules

### Phase Scope Rules
- MUST read `out/phase-01-message-priority.md` and `out/phase-07-import-and-format-normalization.md` before editing.
- MUST enable only the final naming/docstring convention IDs assigned to this phase.
- MUST leave `pyproject.toml` in a clear steady-state reflecting the completed rollout rather than an ambiguous intermediate state.
- MUST preserve the canonical `make pylint` and CI contract.
- MUST keep any final cleanup localized and readable.
- MUST NOT reopen already-resolved higher-priority categories except for direct regressions caused by this phase.

### Quality Rules
- Naming is clear and descriptive.
- Naming conventions stay consistent.
- Code is easy to modify.
- Public APIs remain covered where edits risk regression.
- Regression scenarios are covered when naming/docstring cleanup touches behavior-adjacent code.
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

### Enabled final convention family for this phase
- `C0103`
- `C0114`
- `C0115`
- `C0116`

### Runtime inputs to inspect
- `out/phase-01-message-priority.md`

## Task

1. Read `out/phase-01-message-priority.md`. Read `out/phase-07-import-and-format-normalization.md`. Read `pyproject.toml`. Recover the final assigned convention IDs and the current rollout baseline.
2. Enable only `C0103`, `C0114`, `C0115`, and `C0116` in `pyproject.toml`, then finish any final steady-state config normalization needed after the rollout.
3. Read `src/cypilot_proxy`. Read `skills/cypilot/scripts/cypilot`. Inspect the failing files there, then apply the smallest readable fixes needed for naming and docstring conventions.
4. Read `tests`. Add or update tests only if these edits affect behavior or regression risk.
5. Run `EXECUTE: make pylint` and confirm the enabled final convention IDs for this phase are clean; continue iterating until those enabled diagnostics pass.
6. Run targeted tests covering any changed behavior and confirm they pass.
7. Write `out/phase-08-steady-state.md` summarizing the enabled IDs, the final steady-state lint posture, files changed, tests run, and any residual backlog that remains intentionally out of scope.
8. Self-verify that only this phase's final convention IDs were enabled, that the `out/` report exists, and that no unresolved placeholder variables remain.

## Acceptance Criteria

- [ ] Only `C0103`, `C0114`, `C0115`, and `C0116` were enabled for this phase.
- [ ] The enabled final convention diagnostics are resolved in the current `make pylint` run.
- [ ] `pyproject.toml` is left in a clear steady-state pylint configuration.
- [ ] `out/phase-08-steady-state.md` exists and documents enabled IDs, steady-state posture, files changed, tests run, and any residual backlog.
- [ ] The `make pylint` and CI contract is preserved.
- [ ] No unresolved placeholder variables outside code fences.
- [ ] Phase output stays within the stated scope boundary.

## Output Format

When complete, report results in this exact format:
```text
PHASE 8/8 COMPLETE
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

If this is the **last phase**, instead of a next-phase prompt output:

```text
ALL PHASES COMPLETE (8/8)
Plan: .bootstrap/.plans/implement-systematic-pylint-remediation/plan.toml
Lifecycle: archive
```

Then ask: `Continue in this chat? [y/n]`
