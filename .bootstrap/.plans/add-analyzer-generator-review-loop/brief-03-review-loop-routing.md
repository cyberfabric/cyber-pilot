# Compilation Brief: Phase 3/7 — Wire subagent-aware generate/analyze review loop

--- CONTEXT BOUNDARY ---
Disregard all previous context. This brief is self-contained.
Read ONLY the files listed below. Follow the instructions exactly.
---

## Phase Metadata
```toml
[phase]
number = 3
total = 7
type = "implement"
title = "Wire subagent-aware generate/analyze review loop"
depends_on = [1, 2]
input_files = [".bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml", "workflows/generate.md", "workflows/analyze.md", "skills/cypilot/SKILL.md", "skills/cypilot/agents.toml", "skills/cypilot/agents/cypilot-generator.md", "skills/cypilot/agents/cypilot-analyzer.md"]
output_files = ["workflows/generate.md", "workflows/analyze.md", "skills/cypilot/SKILL.md"]
outputs = ["out/phase-03-review-loop-routing.md"]
inputs = ["out/phase-01-subagent-spec-contract.md", "out/phase-02-subagent-registry-contract.md"]
```

## Load Instructions
1. **Plan contract**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml`
   - Action: runtime read
   - Scope: confirm phase identity, outputs, and downstream dependencies
2. **Phase template**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.core/requirements/plan-template.md` (~260 lines)
   - Action: inline structure contract
   - Scope: keep only section order, preamble, and output-format requirements
3. **Prior decision outputs**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/out/phase-01-subagent-spec-contract.md` and `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/out/phase-02-subagent-registry-contract.md`
   - Action: runtime read
   - Scope: treat them as authoritative for which agent names to route and what compatibility guarantees must hold
4. **Generate workflow contract**: Read `workflows/generate.md` (lines 252-458, ~207 lines)
   - Action: runtime read
   - Scope: update validation/review-prompt behavior so review entry is subagent-aware while preserving the existing `Plan Review Prompt` / `Direct Review Prompt` pair
5. **Analyze workflow contract**: Read `workflows/analyze.md` (lines 245-469, ~225 lines)
   - Action: runtime read
   - Scope: update remediation prompting so bounded fixes prefer `cypilot-generator` and review loops prefer `cypilot-analyzer`
6. **Top-level routing invariants**: Read `skills/cypilot/SKILL.md` (lines 173-180, ~8 lines) plus `skills/cypilot/agents.toml` and the new generalized prompt files
   - Action: runtime read
   - Scope: keep completion invariants and routing priority coherent with the new loop wording

**Do NOT load**: `commands/agents.py`, tests, or bootstrap mirrors except the current plan artifacts.

## Compile Phase File
Write to: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/phase-03-review-loop-routing.md`

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
- Prefer `cypilot-generator` for isolated generate/fix tasks within `generate.md`
- Prefer `cypilot-analyzer` for isolated review/analyze tasks within `analyze.md`
- Keep inline/manual fallback paths intact for hosts without subagent orchestration
- Reuse existing prompt pairs instead of inventing a new review-loop prompt family
- Save a concise routing/invariant summary to `out/phase-03-review-loop-routing.md`

## Context Budget
- Phase file target: ≤ 600 lines
- Inlined content estimate: ~190 lines
- Total execution context: ≤ 1700 lines
- If Rules exceeds 300 lines, narrow scope — NEVER drop rules

## After Compilation
Report: "Phase 3 compiled → phase-03-review-loop-routing.md (N lines)"
Then apply context boundary and proceed to the next brief.
