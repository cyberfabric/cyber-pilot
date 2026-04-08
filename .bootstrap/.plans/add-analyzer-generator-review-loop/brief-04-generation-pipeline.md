# Compilation Brief: Phase 4/7 — Extend host agent generation pipeline

--- CONTEXT BOUNDARY ---
Disregard all previous context. This brief is self-contained.
Read ONLY the files listed below. Follow the instructions exactly.
---

## Phase Metadata
```toml
[phase]
number = 4
total = 7
type = "implement"
title = "Extend host agent generation pipeline"
depends_on = [2, 3]
input_files = [".bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml", "skills/cypilot/scripts/cypilot/commands/agents.py", "skills/cypilot/agents.toml", "skills/cypilot/agents/cypilot-generator.md", "skills/cypilot/agents/cypilot-analyzer.md", "tests/test_subagent_registration.py"]
output_files = ["skills/cypilot/scripts/cypilot/commands/agents.py"]
outputs = ["out/phase-04-generation-pipeline.md"]
inputs = ["out/phase-02-subagent-registry-contract.md", "out/phase-03-review-loop-routing.md"]
```

## Load Instructions
1. **Plan contract**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml`
   - Action: runtime read
   - Scope: confirm phase identity, outputs, and downstream dependencies
2. **Phase template**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.core/requirements/plan-template.md` (~260 lines)
   - Action: inline structure contract
   - Scope: keep only section order, preamble, and output-format requirements
3. **Prior contracts**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/out/phase-02-subagent-registry-contract.md` and `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/out/phase-03-review-loop-routing.md`
   - Action: runtime read
   - Scope: treat them as the source of truth for what the pipeline must emit and which names/routes are canonical
4. **Pipeline implementation**: Read `skills/cypilot/scripts/cypilot/commands/agents.py` (lines 372-520, 1248-1832, 2639-2798, and 3183-3294, ~1000 lines total)
   - Action: runtime read
   - Scope: update agent discovery, per-host translation, legacy generation flow, and manifest generation for the expanded agent set without widening scope to unrelated command code
5. **Canonical registry inputs**: Read `skills/cypilot/agents.toml` (~72 lines) plus `skills/cypilot/agents/cypilot-generator.md` and `skills/cypilot/agents/cypilot-analyzer.md`
   - Action: runtime read
   - Scope: ensure generated host outputs reflect the new registry entries and prompts exactly
6. **Current tests as behavioral guardrails**: Read `tests/test_subagent_registration.py` (lines 33-170 and 421-588, ~306 lines)
   - Action: runtime read
   - Scope: use existing discovery/generation assertions to avoid breaking old host-specific behavior while extending coverage

6. **Authoritative CODEBASE rules**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/config/kits/sdlc/codebase/rules.md` (~260 lines)
   - Action: inline
   - Scope: keep the structural, engineering, quality, and validation requirements relevant to code, tests, generated agent outputs, and verification work; do not summarize them away
7. **Authoritative CODEBASE checklist**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/config/kits/sdlc/codebase/checklist.md` (~90 lines)
   - Action: inline
   - Scope: keep the traceability preconditions and semantic-alignment criteria relevant to the implementation and verification phases

**Do NOT load**: workflow markdown bodies, unrelated tests, or the full repository tree.

## Compile Phase File
Write to: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/phase-04-generation-pipeline.md`

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
- Extend legacy `agents.toml` discovery and generation to include the two new generalized agents
- Preserve existing per-host schema mappings and Windsurf skip behavior
- Keep backward compatibility with `cypilot-codegen` and `cypilot-pr-review`
- Save a pipeline-impact summary to `out/phase-04-generation-pipeline.md`

## Context Budget
- Phase file target: ≤ 950 lines
- Inlined content estimate: ~520 lines
- Total execution context: ≤ 2300 lines
- If Rules exceeds 300 lines, narrow scope — NEVER drop rules

## After Compilation
Report: "Phase 4 compiled → phase-04-generation-pipeline.md (N lines)"
Then apply context boundary and proceed to the next brief.
