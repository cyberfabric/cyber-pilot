# Compilation Brief: Phase 2/8 — Critical runtime errors

--- CONTEXT BOUNDARY ---
Disregard all previous context. This brief is self-contained.
Read ONLY the files listed below. Follow the instructions exactly.
---

## Phase Metadata
```toml
[phase]
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

## Load Instructions
1. **Phase template**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.core/requirements/plan-template.md` (lines 58-79 and 152-199, ~70 lines)
   - Action: inline
   - Scope: use the exact preamble and output format contract
2. **Codebase rules**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/config/kits/sdlc/codebase/rules.md` (lines 61-158 and 261-305, ~143 lines)
   - Action: inline
   - Scope: keep engineering, error-handling, quality, and build/lint validation obligations relevant to critical error cleanup
3. **Generic code checklist**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.core/requirements/code-checklist.md` (lines 37-45, 133-151, 198-216, and 232-245, ~112 lines)
   - Action: inline
   - Scope: keep severity ordering, explicit error handling, input validation, testing, and no-silent-failure constraints
4. **Baseline outputs**: Read `out/phase-01-rollout-baseline.md` and `out/phase-01-message-priority.md`
   - Action: runtime read
   - Scope: use the authoritative rollout contract and message ordering
5. **Runtime project inputs**: Read `pyproject.toml`, then inspect the currently failing files under `src/cypilot_proxy`, `skills/cypilot/scripts/cypilot`, and touched `tests`
   - Action: runtime read
   - Scope: fix only diagnostics enabled for this phase

**Do NOT load**: style-only diagnostics, docstring-only cleanup, or duplication-focused backlog.

## Compile Phase File
Write to: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/implement-systematic-pylint-remediation/phase-02-critical-runtime-errors.md`

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
10. Output Format — use the required completion report + next-phase prompt from `plan-template.md`

## Context Budget
- Phase file target: ≤ 600 lines
- Inlined content estimate: ~260 lines
- Total execution context: ≤ 2000 lines
- If Rules exceeds 300 lines, narrow scope — NEVER drop rules

## After Compilation
Report: "Phase 2 compiled → phase-02-critical-runtime-errors.md (N lines)"
Then apply context boundary and proceed to the next brief.
