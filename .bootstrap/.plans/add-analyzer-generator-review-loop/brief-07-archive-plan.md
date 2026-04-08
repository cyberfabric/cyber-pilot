# Compilation Brief: Phase 7/7 — Archive completed plan

--- CONTEXT BOUNDARY ---
Disregard all previous context. This brief is self-contained.
Read ONLY the files listed below. Follow the instructions exactly.
---

## Phase Metadata
```toml
[phase]
number = 7
total = 7
type = "implement"
title = "Archive completed plan"
depends_on = [6]
input_files = [".bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml"]
output_files = []
outputs = []
inputs = ["out/phase-06-verification-report.md"]
```

## Load Instructions
1. **Plan contract**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml`
   - Action: runtime read
   - Scope: confirm lifecycle strategy is `archive` and check current delivery status before acting
2. **Final delivery output**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/out/phase-06-verification-report.md`
   - Action: runtime read
   - Scope: confirm the verification summary exists before lifecycle handling
3. **Phase template**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.core/requirements/plan-template.md` (~260 lines)
   - Action: inline structure contract
   - Scope: keep only section-order, preamble, and output-format requirements

**Do NOT load**: broad repo context, source files, or earlier raw implementation inputs.

## Compile Phase File
Write to: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/phase-07-archive-plan.md`

Required sections:
1. TOML frontmatter
2. Preamble — use the verbatim preamble from `plan-template.md`
3. What
4. Prior Context
5. User Decisions
6. Rules
7. Input
8. Task — add runtime reads for manifest and verification summary
9. Acceptance Criteria
10. Output Format — use the required completion report from `plan-template.md`, adapted for final lifecycle completion

Phase-specific focus:
- Verify all delivery phases are complete before lifecycle action
- Archive the plan directory into `.bootstrap/.plans/.archive/`
- Update `active_plan_dir` and lifecycle status in the moved manifest (`done`)
- Treat archive as one-time lifecycle handling, not as delivery work

## Context Budget
- Phase file target: ≤ 400 lines
- Inlined content estimate: ~120 lines
- Total execution context: ≤ 1200 lines
- If Rules exceeds 300 lines, narrow scope — NEVER drop rules

## After Compilation
Report: "Phase 7 compiled → phase-07-archive-plan.md (N lines)"
Then stop; this is the lifecycle phase.
