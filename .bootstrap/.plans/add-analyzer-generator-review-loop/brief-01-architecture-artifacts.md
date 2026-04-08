# Compilation Brief: Phase 1/7 — Update architecture artifacts

--- CONTEXT BOUNDARY ---
Disregard all previous context. This brief is self-contained.
Read ONLY the files listed below. Follow the instructions exactly.
---

## Phase Metadata
```toml
[phase]
number = 1
total = 7
type = "implement"
title = "Update architecture artifacts"
depends_on = []
input_files = [".bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml", "architecture/features/subagent-registration.md", "architecture/DECOMPOSITION.md", "architecture/DESIGN.md", "workflows/generate.md", "workflows/analyze.md"]
output_files = ["architecture/features/subagent-registration.md", "architecture/DECOMPOSITION.md", "architecture/DESIGN.md"]
outputs = ["out/phase-01-subagent-spec-contract.md"]
inputs = []
```

## Load Instructions
1. **Plan contract**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml`
   - Action: runtime read
   - Scope: confirm phase identity, outputs, and downstream dependencies
2. **Phase template**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.core/requirements/plan-template.md` (~260 lines)
   - Action: inline structure contract
   - Scope: keep only the required section order, preamble, and output-format contract
3. **Primary feature spec**: Read `architecture/features/subagent-registration.md` (lines 35-302, ~268 lines)
   - Action: runtime read
   - Scope: update feature context, invoke flow, and definitions-of-done to include `cypilot-generator` / `cypilot-analyzer` while preserving legacy specialized agents
4. **Architecture references**: Read `architecture/DECOMPOSITION.md` (lines 688-731, ~44 lines) and `architecture/DESIGN.md` (lines 270-290 and 586-592, ~30 lines)
   - Action: runtime read
   - Scope: keep subagent-registration decomposition and agent-generator architecture aligned with the new generalized subagent model
5. **Workflow contracts driving the spec delta**: Read `workflows/generate.md` (lines 252-458, ~207 lines) and `workflows/analyze.md` (lines 245-395, ~151 lines)
   - Action: runtime read
   - Scope: capture current prompt-pair contracts, review-loop expectations, and bounded remediation behavior that specs must describe

**Do NOT load**: `skills/cypilot/scripts/cypilot/commands/agents.py`, test files, host-generated agent outputs, or unrelated architecture sections.

## Compile Phase File
Write to: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/phase-01-architecture-artifacts.md`

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
- Introduce `cypilot-generator` and `cypilot-analyzer` as general-purpose subagents for isolated generate/analyze work
- Preserve `cypilot-codegen` and `cypilot-pr-review` as backward-compatible specialized agents
- Describe the review loop as reusing the existing prompt pairs rather than inventing a new prompt family
- Save a concise architecture delta summary to `out/phase-01-subagent-spec-contract.md`

## Context Budget
- Phase file target: ≤ 600 lines
- Inlined content estimate: ~180 lines
- Total execution context: ≤ 1600 lines
- If Rules exceeds 300 lines, narrow scope — NEVER drop rules

## After Compilation
Report: "Phase 1 compiled → phase-01-architecture-artifacts.md (N lines)"
Then apply context boundary and proceed to the next brief.
