# Compilation Brief: Phase 6/7 — Regenerate agent outputs and verify the repo

--- CONTEXT BOUNDARY ---
Disregard all previous context. This brief is self-contained.
Read ONLY the files listed below. Follow the instructions exactly.
---

## Phase Metadata
```toml
[phase]
number = 6
total = 7
type = "implement"
title = "Regenerate agent outputs and verify the repo"
depends_on = [5]
input_files = [".bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml", "CONTRIBUTING.md", "Makefile", ".claude/agents", "skills/cypilot/agents.toml", "tests/test_subagent_registration.py"]
output_files = [".claude/agents/cypilot-generator.md", ".claude/agents/cypilot-analyzer.md", ".claude/agents/cypilot-codegen.md", ".claude/agents/cypilot-pr-review.md"]
outputs = ["out/phase-06-verification-report.md"]
inputs = ["out/phase-05-test-update-summary.md"]
```

## Load Instructions
1. **Plan contract**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml`
   - Action: runtime read
   - Scope: confirm phase identity, outputs, and downstream dependencies
2. **Phase template**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.core/requirements/plan-template.md` (~260 lines)
   - Action: inline structure contract
   - Scope: keep only section order, preamble, and output-format requirements
3. **Verification preconditions**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/out/phase-05-test-update-summary.md`
   - Action: runtime read
   - Scope: use it as the checklist for what must be regenerated and verified
4. **Repo verification guidance**: Read `CONTRIBUTING.md` (lines 44-141 and 202-218, ~115 lines) and `Makefile` (~225 lines)
   - Action: runtime read
   - Scope: use targeted `pytest`, `make validate`, and `make self-check` as the bounded verification commands; treat `make update` / `cpt update --source . --force` as repo-wide mutation outside this phase's blind-execution surface unless the plan contract is explicitly widened
5. **Agent generation contract**: Read `skills/cypilot/agents.toml` (~72 lines), the current `.claude/agents/` directory listing, and `cypilot.clispec` `generate-agents` command block plus `skills/cypilot/SKILL.md` command reference (lines 335-369, ~35 lines)
   - Action: runtime read
   - Scope: regenerate tracked Claude agent outputs with the correct canonical agent-safe command shape and JSON output contract

6. **Authoritative CODEBASE rules**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/config/kits/sdlc/codebase/rules.md` (~260 lines)
   - Action: inline
   - Scope: keep the structural, engineering, quality, and validation requirements relevant to code, tests, generated agent outputs, and verification work; do not summarize them away
7. **Authoritative CODEBASE checklist**: Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/config/kits/sdlc/codebase/checklist.md` (~90 lines)
   - Action: inline
   - Scope: keep the traceability preconditions and semantic-alignment criteria relevant to the implementation and verification phases

**Do NOT load**: broad architecture docs or unrelated test modules.

## Compile Phase File
Write to: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/phase-06-regeneration-verification.md`

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
- Regenerate tracked Claude agent outputs for the expanded subagent registry
- Run the bounded verification commands and capture exact results
- Treat `make update` / `cpt update --source . --force` as out-of-scope repo-wide mutation unless the delivery surface is explicitly widened in a later step
- Save a verification summary to `out/phase-06-verification-report.md`

## Context Budget
- Phase file target: ≤ 950 lines
- Inlined content estimate: ~520 lines
- Total execution context: ≤ 2300 lines
- If Rules exceeds 300 lines, narrow scope — NEVER drop rules

## After Compilation
Report: "Phase 6 compiled → phase-06-regeneration-verification.md (N lines)"
Then apply context boundary and proceed to the next brief.
