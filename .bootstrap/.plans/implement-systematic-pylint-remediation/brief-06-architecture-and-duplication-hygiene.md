# Compilation Brief: Phase 6/8 — Architecture and duplication hygiene

--- CONTEXT BOUNDARY ---
Disregard all previous context. This brief is self-contained.
Read ONLY the files listed below. Follow the instructions exactly.
---

## Phase Metadata
```toml
[phase]
number = 6
total = 8
type = "implement"
title = "Architecture and duplication hygiene"
depends_on = [5]
input_files = ["pyproject.toml", "src/cypilot_proxy", "skills/cypilot/scripts/cypilot", "tests"]
output_files = ["pyproject.toml", "src/cypilot_proxy", "skills/cypilot/scripts/cypilot", "tests"]
outputs = ["out/phase-06-architecture-and-duplication-hygiene.md"]
inputs = ["out/phase-01-message-priority.md", "out/phase-05-control-flow-hotspots-ii.md"]
```

## Load Instructions
1. **Phase template**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.core/requirements/plan-template.md` (lines 58-79 and 152-199, ~70 lines)
   - Action: inline
   - Scope: use the exact preamble and output format contract
2. **Codebase rules**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/config/kits/sdlc/codebase/rules.md` (lines 131-158 and 286-324, ~67 lines)
   - Action: inline
   - Scope: keep engineering, quality, tests, and build/lint obligations for structural refactors
3. **Generic code checklist**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.core/requirements/code-checklist.md` (lines 42-45, 55-106, 114-132, 171-183, and 267-290, ~128 lines)
   - Action: inline
   - Scope: keep SRP, OCP, DIP, DRY, maintainability, complexity, scalability, and reporting obligations
4. **Prior outputs**: Read `out/phase-01-message-priority.md` and `out/phase-05-control-flow-hotspots-ii.md`
   - Action: runtime read
   - Scope: preserve ordering and avoid reopening previous categories
5. **Runtime project inputs**: Read `pyproject.toml`, then inspect the currently failing files under `src/cypilot_proxy`, `skills/cypilot/scripts/cypilot`, and touched `tests`
   - Action: runtime read
   - Scope: fix cyclic imports and duplicate-code without weakening coverage or contracts

**Do NOT load**: line-length/docstring cleanup except where strictly incidental to duplication fixes.

## Compile Phase File
Write to: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/implement-systematic-pylint-remediation/phase-06-architecture-and-duplication-hygiene.md`

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
Report: "Phase 6 compiled → phase-06-architecture-and-duplication-hygiene.md (N lines)"
Then apply context boundary and proceed to the next brief.
