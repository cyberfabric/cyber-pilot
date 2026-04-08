# Compilation Brief: Phase 2/7 — Register canonical analyzer and generator subagents

--- CONTEXT BOUNDARY ---
Disregard all previous context. This brief is self-contained.
Read ONLY the files listed below. Follow the instructions exactly.
---

## Phase Metadata
```toml
[phase]
number = 2
total = 7
type = "implement"
title = "Register canonical analyzer and generator subagents"
depends_on = [1]
input_files = [".bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml", "skills/cypilot/agents.toml", "skills/cypilot/agents/cypilot-codegen.md", "skills/cypilot/agents/cypilot-pr-review.md", "architecture/features/subagent-registration.md"]
output_files = ["skills/cypilot/agents.toml", "skills/cypilot/agents/cypilot-generator.md", "skills/cypilot/agents/cypilot-analyzer.md", "skills/cypilot/agents/cypilot-codegen.md", "skills/cypilot/agents/cypilot-pr-review.md"]
outputs = ["out/phase-02-subagent-registry-contract.md"]
inputs = ["out/phase-01-subagent-spec-contract.md"]
```

## Load Instructions
1. **Plan contract**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml`
   - Action: runtime read
   - Scope: confirm phase identity, outputs, and downstream dependencies
2. **Phase template**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.core/requirements/plan-template.md` (~260 lines)
   - Action: inline structure contract
   - Scope: keep only section order, preamble, and output-format requirements
3. **Prior architecture decision**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/out/phase-01-subagent-spec-contract.md`
   - Action: runtime read
   - Scope: treat it as the source of truth for names, responsibilities, and backward-compatibility constraints
4. **Current registry**: Read `skills/cypilot/agents.toml` (~72 lines)
   - Action: runtime read
   - Scope: add canonical generalized agents without deleting specialized existing entries
5. **Existing specialized prompts**: Read `skills/cypilot/agents/cypilot-codegen.md` (~14 lines) and `skills/cypilot/agents/cypilot-pr-review.md` (~14 lines)
   - Action: runtime read
   - Scope: keep their narrow purpose intact and align wording only where the generalized model requires it
6. **Updated feature spec**: Read `architecture/features/subagent-registration.md` (~302 lines after Phase 1)
   - Action: runtime read
   - Scope: ensure the new registry and prompt files match the updated feature contract

**Do NOT load**: workflow markdown, `commands/agents.py`, generated `.claude/agents/*` outputs, or unrelated tests.

## Compile Phase File
Write to: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/phase-02-canonical-subagents.md`

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
- Add `cypilot-generator` and `cypilot-analyzer` entries to `skills/cypilot/agents.toml`
- Create the new prompt files under `skills/cypilot/agents/`
- Preserve `cypilot-codegen` and `cypilot-pr-review` as specialized legacy-compatible profiles
- Save a registry/prompt contract summary to `out/phase-02-subagent-registry-contract.md`

## Context Budget
- Phase file target: ≤ 550 lines
- Inlined content estimate: ~150 lines
- Total execution context: ≤ 1400 lines
- If Rules exceeds 300 lines, narrow scope — NEVER drop rules

## After Compilation
Report: "Phase 2 compiled → phase-02-canonical-subagents.md (N lines)"
Then apply context boundary and proceed to the next brief.
