```toml
[phase]
plan = "implement-systematic-pylint-remediation"
number = 7
total = 8
type = "implement"
title = "Import and format normalization"
depends_on = [6]
input_files = ["pyproject.toml", "Makefile", ".github/workflows/ci.yml", "src/cypilot_proxy", "skills/cypilot/scripts/cypilot", "tests"]
output_files = ["pyproject.toml", "src/cypilot_proxy", "skills/cypilot/scripts/cypilot", "tests"]
outputs = ["out/phase-07-import-and-format-normalization.md"]
inputs = ["out/phase-01-message-priority.md", "out/phase-06-architecture-and-duplication-hygiene.md"]
```

## Preamble

This is a self-contained phase file. All rules, constraints, and kit content
are included below. Project files listed in the Task section must be read
at runtime. Follow the instructions exactly, run any EXECUTE commands as
written, and report results against the acceptance criteria at the end.

## What

Normalize the remaining import-placement and formatting-related convention backlog after the structural cleanup is complete. This phase is deliberately late in the rollout so that import and layout changes happen on top of already-simplified code. Keep the work mechanical and scoped to the convention IDs assigned here.

## Prior Context

The earlier phases already established the lint baseline and resolved runtime, warning, control-flow, and architecture hotspots.
This phase now handles the import-order and formatting conventions that are safer to fix after larger refactors settle.
The canonical local and CI entrypoint remains `make pylint`.
Later naming and docstring cleanup is still deferred to the final phase.

## User Decisions

### Already Decided (pre-resolved during planning)
- **Lifecycle**: `archive`
- **Execution mode**: autonomous phased cleanup
- **Priority family for this phase**: import placement and formatting conventions
- **Out-of-scope**: naming and docstring cleanup except for tiny incidental fallout

### Decisions Needed During This Phase
#### Review Gates
- [ ] **Review convention cleanup** — verify the completion report lists the exact convention IDs enabled and the principal files normalized

#### Confirmation Points
- [ ] **Confirm contract preservation** — import and layout changes must not alter runtime behavior or the `make pylint` / CI contract

#### User Input Required
- [ ] **None** — no additional user input is required during execution

## Rules

### Phase Scope Rules
- MUST read `out/phase-01-message-priority.md` and `out/phase-06-architecture-and-duplication-hygiene.md` before editing.
- MUST enable only the import-placement and formatting convention IDs assigned to this phase.
- MUST preserve the canonical `make pylint` and CI contract.
- MUST keep fixes mechanical and localized where possible.
- MUST NOT broaden into naming/docstring cleanup assigned to Phase 8 unless strictly incidental and unavoidable.
- MUST NOT reintroduce import cycles or duplicate-code hotspots already fixed earlier.

### Quality Rules
- Code follows project conventions from config.
- The simplest correct solution was chosen.
- Naming stays consistent when small import-related renames are necessary.
- Public APIs remain covered where behavior risk exists.
- Regression scenarios are covered when import movement risks runtime behavior.
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

### Enabled convention family for this phase
- `C0415`
- `C0413`
- `C0411`
- `C0414`
- `C0301`
- `C0302`
- `C0303`
- `C0305`
- `C0325`

### Runtime inputs to inspect
- `out/phase-01-message-priority.md`
- `out/phase-06-architecture-and-duplication-hygiene.md`
- `pyproject.toml`

## Task

1. Read `out/phase-01-message-priority.md`. Read `out/phase-06-architecture-and-duplication-hygiene.md`. Read `pyproject.toml`. Read `Makefile`. Read `.github/workflows/ci.yml`. Recover the assigned convention IDs and confirm the lint command contract.
2. Enable only this phase's convention IDs in `pyproject.toml`.
3. Read `src/cypilot_proxy`. Read `skills/cypilot/scripts/cypilot`. Inspect the failing files there, then apply the smallest mechanical fixes needed for import placement, import ordering, line/blank-line handling, and related formatting conventions.
4. Read `tests`. Add or update tests only if import movement or formatting cleanup changes runtime behavior or regression risk.
5. Run `EXECUTE: make pylint` and confirm the enabled convention IDs for this phase are clean; continue iterating until those enabled convention diagnostics pass.
6. Run targeted tests covering any changed behavior and confirm they pass.
7. Write `out/phase-07-import-and-format-normalization.md` summarizing the enabled IDs, principal files normalized, files changed, tests run, and any residual backlog intentionally deferred.
8. Self-verify that only this phase's convention IDs were enabled, that the `out/` report exists, and that no unresolved placeholder variables remain.

## Acceptance Criteria

- [ ] Only the import-placement and formatting convention IDs assigned to this phase were enabled.
- [ ] The enabled convention diagnostics are resolved in the current `make pylint` run.
- [ ] The `make pylint` and CI contract is preserved.
- [ ] `out/phase-07-import-and-format-normalization.md` exists and documents enabled IDs, files normalized, tests run, and residual backlog.
- [ ] No Phase 8 naming/docstring families were intentionally enabled in this phase.
- [ ] No unresolved placeholder variables outside code fences.
- [ ] Phase output stays within the stated scope boundary.

## Output Format

When complete, report results in this exact format:
```text
PHASE 7/8 COMPLETE
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

Phase 7 is complete ({status}).
Please read the plan manifest, then execute Phase 8: "Naming, docstrings, and steady-state".
The phase file is: .bootstrap/.plans/implement-systematic-pylint-remediation/phase-08-naming-docstrings-and-steady-state.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.
```

Then ask: `Continue in this chat? [y/n]`
