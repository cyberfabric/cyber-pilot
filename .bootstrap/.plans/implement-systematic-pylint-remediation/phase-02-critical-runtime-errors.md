```toml
[phase]
plan = "implement-systematic-pylint-remediation"
number = 2
total = 8
type = "implement"
title = "Critical runtime errors"
depends_on = [1]
input_files = ["pyproject.toml", "src/cypilot_proxy", "skills/cypilot/scripts/cypilot", "tests"]
output_files = ["pyproject.toml", "src/cypilot_proxy", "skills/cypilot/scripts/cypilot", "tests"]
outputs = ["out/phase-02-critical-errors.md"]
inputs = ["out/phase-01-rollout-baseline.md", "out/phase-01-message-priority.md"]
```

## Preamble

This is a self-contained phase file. All rules, constraints, and kit content
are included below. Project files listed in the Task section must be read
at runtime. Follow the instructions exactly, run any EXECUTE commands as
written, and report results against the acceptance criteria at the end.

## What

Resolve the highest-priority runtime and correctness pylint failures first. This phase is restricted to the enabled `E*` diagnostics and tightly related unblockers that are necessary to make those diagnostics pass cleanly. Do not enable warning, refactor, or convention families assigned to later phases.

## Prior Context

Phase 1 established a disable-all baseline and recorded the diagnostic rollout order.
Phase 1 also preserved `make pylint` as the canonical lint entrypoint.
The authoritative ordering for later phases lives in `out/phase-01-message-priority.md`.
This phase must begin from the baseline contract, not from ad hoc local changes.

## User Decisions

### Already Decided (pre-resolved during planning)
- **Lifecycle**: `archive`
- **Execution mode**: autonomous phased cleanup
- **Priority family for this phase**: critical runtime/correctness diagnostics only
- **Out-of-scope**: style, docstrings, naming, and duplication-focused cleanup

### Decisions Needed During This Phase
#### Review Gates
- [ ] **Review critical error closure** — verify the completion report lists the exact enabled messages and zero remaining failures for those messages

#### Confirmation Points
- [ ] **Confirm no category drift** — do not enable later-phase message IDs in this phase

#### User Input Required
- [ ] **None** — no additional user input is required during execution

## Rules

### Phase Scope Rules
- MUST read `out/phase-01-rollout-baseline.md` and `out/phase-01-message-priority.md` before editing.
- MUST enable only the critical runtime/correctness pylint messages assigned to this phase.
- MUST fix only diagnostics in the enabled set, except for minimal unblocker edits that are directly required to make those diagnostics pass.
- MUST preserve the staged-rollout baseline in `pyproject.toml` while enabling this phase's messages.
- MUST NOT enable later-phase warning, refactor, duplicate-code, import-format, naming, or docstring families.
- MUST NOT treat broad cleanup as acceptable if it obscures whether this phase actually resolved the enabled diagnostics.

### Error Handling and Testing Rules
- Errors fail explicitly.
- Error conditions are handled.
- Exceptions are not swallowed.
- Error messages are actionable.
- All external inputs are validated at system boundaries.
- New behavior has corresponding tests.
- Public APIs are covered.
- Happy paths are covered.
- Error paths are covered.
- Edge cases are covered.
- No silent failures are introduced.
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

### Enabled message family for this phase
- `E0602`
- `E1135`
- `E0102`
- Minimal unblockers required only to let `E0602`, `E1135`, and `E0102` be evaluated correctly:
  - add the smallest missing import or stub needed for module parsing/binding
  - apply the narrowest parser or syntax fix needed to restore valid parsing
  - make a tiny import guard or import-placement fix only when it directly unblocks those diagnostics
- Any unblocker MUST be the smallest change that enables evaluation, MUST NOT suppress or mask other messages, MUST include a one-line justification in the PR/report, and any unblocker outside the examples above requires reviewer sign-off

### Runtime inputs to inspect
- `out/phase-01-rollout-baseline.md`

## Task

1. Read `out/phase-01-rollout-baseline.md`. Read `out/phase-01-message-priority.md`. Read `pyproject.toml`. Recover the authoritative baseline and the exact message IDs assigned to this phase.
2. Enable only this phase's critical runtime/correctness message IDs in `pyproject.toml`.
3. Read `src/cypilot_proxy`. Read `skills/cypilot/scripts/cypilot`. Inspect the failing files there, then implement the smallest correct fixes needed to eliminate the enabled diagnostics without broad refactors.
4. Read `tests`. Add or update tests wherever behavior changes or regression protection is required to justify the fix.
5. Run `EXECUTE: make pylint` and confirm the enabled diagnostics for this phase are clean; if the output still includes failures from the same enabled set, continue fixing and re-running until those enabled diagnostics pass.
6. Run targeted tests covering the changed behavior and confirm they pass.
7. Write `out/phase-02-critical-errors.md` summarizing the enabled IDs, files changed, tests run, and any residual backlog intentionally deferred to later phases.
8. Self-verify that only this phase's messages were enabled, that the `out/` report exists, and that no unresolved placeholder variables remain.

## Acceptance Criteria

- [ ] Only the critical runtime/correctness message IDs assigned to this phase were enabled.
- [ ] The enabled critical diagnostics are resolved in the current `make pylint` run.
- [ ] Any changed behavior is covered by appropriate tests.
- [ ] `out/phase-02-critical-errors.md` exists and documents enabled IDs, files changed, tests run, and residual backlog.
- [ ] No later-phase message families were intentionally enabled in this phase.
- [ ] No unresolved placeholder variables outside code fences.
- [ ] Phase output stays within the stated scope boundary.

## Output Format

When complete, report results in this exact format:
```text
PHASE 2/8 COMPLETE
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

Phase 2 is complete ({status}).
Please read the plan manifest, then execute Phase 3: "High-risk warnings".
The phase file is: .bootstrap/.plans/implement-systematic-pylint-remediation/phase-03-high-risk-warnings.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.
```

Then ask: `Continue in this chat? [y/n]`
