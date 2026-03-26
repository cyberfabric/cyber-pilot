# Compilation Brief: Phase 8/8 — Naming, docstrings, and steady-state

--- CONTEXT BOUNDARY ---
Disregard all previous context. This brief is self-contained.
Read ONLY the files listed below. Follow the instructions exactly.
---

## Phase Metadata
```toml
[phase]
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

## Load Instructions
1. **Phase template**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.core/requirements/plan-template.md` (lines 58-79 and 152-199, ~70 lines)
   - Action: inline
   - Scope: use the exact preamble and final-phase output contract
2. **Codebase rules**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/config/kits/sdlc/codebase/rules.md` (lines 131-158 and 286-305, ~49 lines)
   - Action: inline
   - Scope: keep engineering, quality, and build/lint obligations for the final cleanup pass
3. **Generic code checklist**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.core/requirements/code-checklist.md` (lines 107-132, 198-216, and 267-290, ~65 lines)
   - Action: inline
   - Scope: maintainability, readability, testing, and reporting obligations
4. **Prior outputs**: Read `out/phase-01-message-priority.md` and `out/phase-07-import-and-format-normalization.md`
   - Action: runtime read
   - Scope: preserve ordering and ensure only the final naming/docstring/style backlog remains
5. **Runtime project inputs**: Read `pyproject.toml`, then inspect the currently failing files under `src/cypilot_proxy`, `skills/cypilot/scripts/cypilot`, and touched `tests`
   - Action: runtime read
   - Scope: finish the last enabled convention families and leave a stable steady-state config

**Do NOT load**: earlier category backlog unless the final run shows regression introduced by this phase.

## Compile Phase File
Write to: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/implement-systematic-pylint-remediation/phase-08-naming-docstrings-and-steady-state.md`

Required sections:
1. TOML frontmatter
2. Preamble — use the verbatim preamble from `plan-template.md`
3. What
4. Prior Context
5. User Decisions
6. Rules
7. Input
8. Task — add `Read <file>` steps for runtime-read items
9. Acceptance Criteria
10. Output Format — use the required completion report and final completion block from `plan-template.md`

## Context Budget
- Phase file target: ≤ 600 lines
- Inlined content estimate: ~150 lines
- Total execution context: ≤ 2000 lines
- If Rules exceeds 300 lines, narrow scope — NEVER drop rules

## After Compilation
Report: "Phase 8 compiled → phase-08-naming-docstrings-and-steady-state.md (N lines)"
Then apply context boundary and finish the plan.
