# Compilation Brief: Phase 4/8 — Control-flow hotspots I

--- CONTEXT BOUNDARY ---
Disregard all previous context. This brief is self-contained.
Read ONLY the files listed below. Follow the instructions exactly.
---

## Phase Metadata
```toml
[phase]
number = 4
total = 8
type = "implement"
title = "Control-flow hotspots I"
depends_on = [3]
input_files = ["pyproject.toml", "src/cypilot_proxy", "skills/cypilot/scripts/cypilot", "tests"]
output_files = ["pyproject.toml", "src/cypilot_proxy", "skills/cypilot/scripts/cypilot", "tests"]
outputs = ["out/phase-04-control-flow-hotspots-i.md"]
inputs = ["out/phase-01-message-priority.md", "out/phase-03-high-risk-warnings.md"]
```

## Load Instructions
1. **Phase template**: Read `.bootstrap/.core/requirements/plan-template.md` (lines 58-79 and 152-199, ~70 lines)
   - Action: inline
   - Scope: use the exact preamble and output format contract
2. **Codebase rules**: Read `.bootstrap/config/kits/sdlc/codebase/rules.md` (lines 131-158 and 286-324, ~67 lines)
   - Action: inline
   - Scope: keep engineering, quality, tests, and build/lint obligations for structural refactors
3. **Generic code checklist**: Read `.bootstrap/.core/requirements/code-checklist.md` (lines 46-132, 198-216, and 267-290, ~130 lines)
   - Action: inline
   - Scope: keep TDD, SRP, DRY, KISS, YAGNI, complexity control, and reporting obligations
4. **Prior outputs**: Read `out/phase-01-message-priority.md` and `out/phase-03-high-risk-warnings.md`
   - Action: runtime read
   - Scope: preserve ordering and avoid reopening completed warning work
5. **Runtime project inputs**: Read `pyproject.toml`, then inspect the currently failing files under `src/cypilot_proxy`, `skills/cypilot/scripts/cypilot`, and touched `tests`
   - Action: runtime read
   - Scope: fix only the control-flow metrics assigned to this phase

**Do NOT load**: duplication-specific backlog, import formatting backlog, or docstring/naming cleanup.

## Compile Phase File
Write to: `.bootstrap/.plans/implement-systematic-pylint-remediation/phase-04-control-flow-hotspots-i.md`

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
- Inlined content estimate: ~210 lines
- Total execution context: ≤ 2000 lines
- If Rules exceeds 300 lines, narrow scope — NEVER drop rules

## After Compilation
Report: "Phase 4 compiled → phase-04-control-flow-hotspots-i.md (N lines)"
Then apply context boundary and proceed to the next brief.
