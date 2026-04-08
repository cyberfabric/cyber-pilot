```toml
[phase]
plan = "add-analyzer-generator-review-loop"
number = 7
total = 7
type = "implement"
title = "Archive completed plan"
depends_on = [6]
input_manifest = ""
input_signature = ""
input_files = [".bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml"]
output_files = []
outputs = []
inputs = ["out/phase-06-verification-report.md"]
```

## Preamble

This is a self-contained phase file. All rules, constraints, and kit content
are included below. Project files listed in the Task section must be read
at runtime. Follow the instructions exactly, run any EXECUTE commands as
written, and report results against the acceptance criteria at the end.

## What

Archive the completed execution plan after delivery work is finished and the
verification handoff exists. This phase only handles final lifecycle closure
for the plan directory under `.bootstrap/.plans/` and must not redo delivery,
decomposition, or lifecycle selection.

## Prior Context

- The plan slug is `add-analyzer-generator-review-loop`.
- This is phase 7 of 7 and its manifest dependency is phase 6.
- The manifest declares `lifecycle = "archive"`.
- The required prior handoff is `out/phase-06-verification-report.md`.
- This phase is lifecycle handling only; it is not delivery work.

## User Decisions

### Already Decided (pre-resolved during planning)

- **Lifecycle strategy**: `archive`
- **Archive target root**: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/.archive/`
- **Scope boundary**: archive the completed plan only; do not redo decomposition or lifecycle selection

### Decisions Needed During This Phase

No additional user decisions are required during this phase.

## Rules

### Execution Boundary

- MUST treat this phase file as self-contained and rely only on the runtime reads listed in the Task section.
- MUST read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml` before any lifecycle action.
- MUST read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/out/phase-06-verification-report.md` before any archive action.
- MUST NOT read broad repository context, source files, or earlier raw implementation inputs.
- MUST NOT redo decomposition, delivery implementation, or lifecycle selection.

### Lifecycle Preconditions

- MUST confirm the manifest still declares `lifecycle = "archive"` before moving the plan directory.
- MUST confirm phase 7 still depends on phase 6 before lifecycle handling.
- MUST treat the verification summary as the authoritative delivery-completion handoff for this lifecycle phase.
- MUST confirm the verification summary exists before archive handling.
- MUST confirm all delivery phases are complete before the archive move, using the verification summary and manifest consistency checks.
- MUST fail without moving the plan directory if any prerequisite check fails.

### Archive Operation

- MUST archive `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop` into `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/.archive/add-analyzer-generator-review-loop`.
- MUST preserve the full plan directory contents during the move.
- MUST update `active_plan_dir` in the moved manifest to `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/.archive/add-analyzer-generator-review-loop`.
- MUST update `lifecycle_status` in the moved manifest to `done`.
- MUST leave the lifecycle strategy as `archive`.
- MUST treat the archive move as one-time lifecycle handling, not as delivery work.

### Reporting

- MUST self-verify every acceptance criterion before reporting completion.
- MUST use the final-phase completion report format in this file.
- MUST include the phase line-count result in the final report.
- MUST NOT modify repository files outside the plan archive assets required by this phase.

## Input

- **Runtime manifest**: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml`
- **Runtime verification summary**: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/out/phase-06-verification-report.md`
- **Archive destination**: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/.archive/add-analyzer-generator-review-loop`
- **Required pre-archive state**:
  - Manifest lifecycle remains `archive`.
  - Phase 6 verification summary exists.
  - Delivery phases 1 through 6 are complete.
- **Required post-archive state**:
  - The archived directory contains the full moved plan.
  - The moved manifest points `active_plan_dir` at the archived directory.
  - The moved manifest records `lifecycle_status = "done"`.

## Task

1. Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml` and record the current `plan_dir`, `active_plan_dir`, `lifecycle`, `lifecycle_status`, and phase-7 dependency on phase 6.
2. Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/out/phase-06-verification-report.md` and confirm the verification summary exists before any lifecycle handling.
3. Confirm the manifest still uses the `archive` lifecycle and that the verification summary shows delivery phases 1 through 6 are complete before moving the plan directory. If any prerequisite fails, stop and report `FAIL` without archiving.
4. Move `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop` to `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/.archive/add-analyzer-generator-review-loop` as a single archive action, preserving all plan contents.
5. Edit the moved `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/.archive/add-analyzer-generator-review-loop/plan.toml` so `active_plan_dir` points to the archived directory and `lifecycle_status` is `done`.
6. Verify the source active plan directory is no longer active, the archived directory contains the complete moved plan, and no files outside the plan archive assets were modified.
7. Self-verify every acceptance criterion, then report results using the required final lifecycle completion format.

## Acceptance Criteria

- [ ] The manifest was read before any lifecycle action and still declares `lifecycle = "archive"`.
- [ ] The verification summary file exists and was read before any archive action.
- [ ] The verification summary confirms delivery phases 1 through 6 are complete before the move.
- [ ] The plan directory now exists at `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/.archive/add-analyzer-generator-review-loop`.
- [ ] The moved manifest sets `active_plan_dir` to `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/.archive/add-analyzer-generator-review-loop`.
- [ ] The moved manifest sets `lifecycle_status` to `done`.
- [ ] No repository files outside the plan archive assets were modified.
- [ ] No unresolved placeholder variables remain outside code fences in this phase file.
- [ ] This phase file is at or under 400 lines.

## Output Format

When complete, report results in this exact format:

```text
PHASE 7/7 COMPLETE
Status: PASS | FAIL
Files created: none | list
Files modified: list
Acceptance criteria:
  [x] Criterion 1 — PASS
  [ ] Criterion 2 — FAIL: reason
  ...
Line count: actual/400
Notes: any issues or lifecycle observations

ALL PHASES COMPLETE (7/7)
Plan: /Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/.archive/add-analyzer-generator-review-loop/plan.toml
Lifecycle: archive
```

Then ask: `Continue in this chat? [y/n]`
