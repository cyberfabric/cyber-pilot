# Compilation Brief: Phase 5/7 — Update tests for the expanded subagent set

--- CONTEXT BOUNDARY ---
Disregard all previous context. This brief is self-contained.
Read ONLY the files listed below. Follow the instructions exactly.
---

## Phase Metadata
```toml
[phase]
number = 5
total = 7
type = "implement"
title = "Update tests for the expanded subagent set"
depends_on = [4]
input_files = [".bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml", "tests/test_subagent_registration.py", "skills/cypilot/scripts/cypilot/commands/agents.py", "skills/cypilot/agents.toml"]
output_files = ["tests/test_subagent_registration.py"]
outputs = ["out/phase-05-test-update-summary.md"]
inputs = ["out/phase-04-generation-pipeline.md"]
```

## Load Instructions
1. **Plan contract**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml`
   - Action: runtime read
   - Scope: confirm phase identity, outputs, and downstream dependencies
2. **Phase template**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.core/requirements/plan-template.md` (~260 lines)
   - Action: inline structure contract
   - Scope: keep only section order, preamble, and output-format requirements
3. **Pipeline change summary**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/out/phase-04-generation-pipeline.md`
   - Action: runtime read
   - Scope: convert code changes into concrete test expectations
4. **Test targets**: Read `tests/test_subagent_registration.py` (lines 33-170 and 421-588, ~306 lines)
   - Action: runtime read
   - Scope: update fixture registry, host-generation counts, and skip/compatibility assertions for the expanded agent set
5. **Implementation reference**: Read `skills/cypilot/scripts/cypilot/commands/agents.py` (same bounded ranges used in Phase 4) plus `skills/cypilot/agents.toml` (~72 lines)
   - Action: runtime read
   - Scope: keep test expectations tied to the actual generation logic and canonical registry

6. **Authoritative CODEBASE rules**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/config/kits/sdlc/codebase/rules.md` (~260 lines)
   - Action: inline
   - Scope: keep the structural, engineering, quality, and validation requirements relevant to code, tests, generated agent outputs, and verification work; do not summarize them away
7. **Authoritative CODEBASE checklist**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/config/kits/sdlc/codebase/checklist.md` (~90 lines)
   - Action: inline
   - Scope: keep the traceability preconditions and semantic-alignment criteria relevant to the implementation and verification phases

**Do NOT load**: workflow docs, architecture artifacts, or unrelated test modules.

## Compile Phase File
Write to: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/phase-05-test-updates.md`

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

Phase-specific focus:
- Expand expectations from the old two-agent model to the new generalized-plus-specialized set
- Preserve assertions for legacy agents and Windsurf skip behavior
- Keep test updates tightly scoped to subagent registration/generation behavior
- Save a summary of changed expectations to `out/phase-05-test-update-summary.md`

## Context Budget
- Phase file target: ≤ 900 lines
- Inlined content estimate: ~520 lines
- Total execution context: ≤ 2200 lines
- If Rules exceeds 300 lines, narrow scope — NEVER drop rules

## After Compilation
Report: "Phase 5 compiled → phase-05-test-updates.md (N lines)"
Then apply context boundary and proceed to the next brief.
