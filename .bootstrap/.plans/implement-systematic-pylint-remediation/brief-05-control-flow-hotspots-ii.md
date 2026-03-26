# Compilation Brief: Phase 5/8 — Control-flow hotspots II

--- CONTEXT BOUNDARY ---
Disregard all previous context. This brief is self-contained.
Read ONLY the files listed below. Follow the instructions exactly.
---

## Phase Metadata
```toml
[phase]
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

## Load Instructions
1. **Phase template**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.core/requirements/plan-template.md` (lines 58-79 and 152-199, ~70 lines)
   - Action: inline
   - Scope: use the exact preamble and output format contract
2. **Codebase rules**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/config/kits/sdlc/codebase/rules.md` (lines 131-158 and 286-324, ~67 lines)
   - Action: inline
   - Scope: keep engineering, quality, tests, and build/lint obligations for structural refactors
3. **Generic code checklist**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.core/requirements/code-checklist.md` (lines 46-132, 198-216, and 267-290, ~130 lines)
   - Action: inline
   - Scope: keep TDD, SRP, DRY, KISS, YAGNI, complexity control, and reporting obligations
4. **Prior outputs**: Read `out/phase-01-message-priority.md` and `out/phase-04-control-flow-hotspots-i.md`
   - Action: runtime read
   - Scope: preserve ordering and avoid reopening completed control-flow work
5. **Runtime project inputs**: Read `pyproject.toml`, then inspect the currently failing files under `src/cypilot_proxy`, `skills/cypilot/scripts/cypilot`, and touched `tests`
   - Action: runtime read
   - Scope: fix only the metrics and refactor IDs assigned to this phase

**Do NOT load**: duplication-specific backlog, import formatting backlog, or docstring/naming cleanup.

## Compile Phase File
Write to: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/implement-systematic-pylint-remediation/phase-05-control-flow-hotspots-ii.md`

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
Report: "Phase 5 compiled → phase-05-control-flow-hotspots-ii.md (N lines)"
Then apply context boundary and proceed to the next brief.
