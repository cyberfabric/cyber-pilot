# Compilation Brief: Phase 3/8 — High-risk warnings

--- CONTEXT BOUNDARY ---
Disregard all previous context. This brief is self-contained.
Read ONLY the files listed below. Follow the instructions exactly.
---

## Phase Metadata
```toml
[phase]
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

## Load Instructions
1. **Phase template**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.core/requirements/plan-template.md` (lines 58-79 and 152-199, ~70 lines)
   - Action: inline
   - Scope: use the exact preamble and output format contract
2. **Codebase rules**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/config/kits/sdlc/codebase/rules.md` (lines 131-158 and 286-305, ~49 lines)
   - Action: inline
   - Scope: keep engineering, quality, and build/lint obligations for warning cleanup
3. **Generic code checklist**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.core/requirements/code-checklist.md` (lines 37-45, 133-170, 198-216, and 232-245, ~131 lines)
   - Action: inline
   - Scope: keep severity ordering, explicit error handling, security-sensitive warning checks, and test obligations
4. **Prior outputs**: Read `out/phase-01-message-priority.md` and `out/phase-02-critical-errors.md`
   - Action: runtime read
   - Scope: preserve the agreed message order and avoid reopening resolved critical errors
5. **Runtime project inputs**: Read `pyproject.toml`, then inspect the currently failing files under `src/cypilot_proxy`, `skills/cypilot/scripts/cypilot`, and touched `tests`
   - Action: runtime read
   - Scope: fix only the warning IDs assigned to this phase

**Do NOT load**: docstring/naming cleanup, broad duplication refactors, or low-priority convention families.

## Compile Phase File
Write to: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/implement-systematic-pylint-remediation/phase-03-high-risk-warnings.md`

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
- Inlined content estimate: ~220 lines
- Total execution context: ≤ 2000 lines
- If Rules exceeds 300 lines, narrow scope — NEVER drop rules

## After Compilation
Report: "Phase 3 compiled → phase-03-high-risk-warnings.md (N lines)"
Then apply context boundary and proceed to the next brief.
