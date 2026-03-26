# Compilation Brief: Phase 7/8 — Import and format normalization

--- CONTEXT BOUNDARY ---
Disregard all previous context. This brief is self-contained.
Read ONLY the files listed below. Follow the instructions exactly.
---

## Phase Metadata
```toml
[phase]
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

## Load Instructions
1. **Phase template**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.core/requirements/plan-template.md` (lines 58-79 and 152-199, ~70 lines)
   - Action: inline
   - Scope: use the exact preamble and output format contract
2. **Codebase rules**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/config/kits/sdlc/codebase/rules.md` (lines 131-158 and 286-305, ~49 lines)
   - Action: inline
   - Scope: keep engineering, quality, and build/lint obligations for import/format cleanup
3. **Current lint contract**: Read `pyproject.toml`, `Makefile` (lines 98-151), and `.github/workflows/ci.yml` (lines 65-77)
   - Action: runtime read
   - Scope: preserve the canonical `make pylint` contract while enabling import/format conventions
4. **Prior outputs**: Read `out/phase-01-message-priority.md` and `out/phase-06-architecture-and-duplication-hygiene.md`
   - Action: runtime read
   - Scope: preserve ordering and avoid reopening previous categories
5. **Runtime project inputs**: Inspect the currently failing files under `src/cypilot_proxy`, `skills/cypilot/scripts/cypilot`, and touched `tests`
   - Action: runtime read
   - Scope: fix import order/location and format conventions assigned to this phase

**Do NOT load**: docstring/naming backlog except when an incidental import move requires a tiny follow-up.

## Compile Phase File
Write to: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/implement-systematic-pylint-remediation/phase-07-import-and-format-normalization.md`

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
- Inlined content estimate: ~170 lines
- Total execution context: ≤ 2000 lines
- If Rules exceeds 300 lines, narrow scope — NEVER drop rules

## After Compilation
Report: "Phase 7 compiled → phase-07-import-and-format-normalization.md (N lines)"
Then apply context boundary and proceed to the next brief.
