# Compilation Brief: Phase 1/8 — Baseline and rollout mechanism

--- CONTEXT BOUNDARY ---
Disregard all previous context. This brief is self-contained.
Read ONLY the files listed below. Follow the instructions exactly.
---

## Phase Metadata
```toml
[phase]
number = 1
total = 8
type = "implement"
title = "Baseline and rollout mechanism"
depends_on = []
input_files = ["pyproject.toml", "Makefile", ".github/workflows/ci.yml"]
output_files = ["pyproject.toml", "Makefile"]
outputs = ["out/phase-01-rollout-baseline.md", "out/phase-01-message-priority.md"]
inputs = []
```

## Load Instructions
1. **Phase template**: Read `.bootstrap/.core/requirements/plan-template.md` (lines 58-79 and 152-199, ~70 lines)
   - Action: inline
   - Scope: use the exact preamble and output format contract; do not invent extra sections
2. **Codebase rules**: Read `.bootstrap/config/kits/sdlc/codebase/rules.md` (lines 61-158 and 286-305, ~118 lines)
   - Action: inline
   - Scope: keep implementation-quality and build-lint obligations; skip prerequisites, tasks, next steps
3. **Pylint config**: Read `pyproject.toml` (lines 22-62, ~41 lines)
   - Action: runtime read
   - Scope: current pylint config and the commented `disable` block
4. **Lint entrypoint**: Read `Makefile` (lines 98-151, ~54 lines)
   - Action: runtime read
   - Scope: `check-pylint` and `pylint` targets; preserve the repository contract
5. **CI contract**: Read `.github/workflows/ci.yml` (lines 65-77, ~13 lines)
   - Action: runtime read
   - Scope: confirm CI still expects `make pylint`

**Do NOT load**: the entire source tree, the generic code checklist, or later phase `out/` reports.

## Compile Phase File
Write to: `.bootstrap/.plans/implement-systematic-pylint-remediation/phase-01-baseline-and-rollout.md`

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
Report: "Phase 1 compiled → phase-01-baseline-and-rollout.md (N lines)"
Then apply context boundary and proceed to the next brief.
