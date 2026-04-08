```toml
[phase]
plan = "add-analyzer-generator-review-loop"
number = 3
total = 7
type = "implement"
title = "Wire subagent-aware generate/analyze review loop"
depends_on = [1, 2]
input_manifest = ""
input_signature = ""
input_files = [
  ".bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml",
"workflows/generate.md",
  "workflows/analyze.md",
  "skills/cypilot/SKILL.md",
  "skills/cypilot/agents.toml",
  "skills/cypilot/agents/cypilot-generator.md",
  "skills/cypilot/agents/cypilot-analyzer.md"
]
output_files = [
  "workflows/generate.md",
  "workflows/analyze.md",
  "skills/cypilot/SKILL.md"
]
outputs = ["out/phase-03-review-loop-routing.md"]
inputs = [
  "out/phase-01-subagent-spec-contract.md",
  "out/phase-02-subagent-registry-contract.md"
]
```

## Preamble

This is a self-contained phase file. All rules, constraints, and kit content
are included below. Project files listed in the Task section must be read
at runtime. Follow the instructions exactly, run any EXECUTE commands as
written, and report results against the acceptance criteria at the end.

## What

Update the canonical generate and analyze workflows so their review-loop handoffs become subagent-aware without changing the existing workflow families or completion guarantees. This phase is limited to `workflows/generate.md`, `workflows/analyze.md`, and `skills/cypilot/SKILL.md`. Preserve the current prompt-pair contracts, keep manual or inline fallback paths for hosts that do not orchestrate subagents, and emit a concise routing summary to `out/phase-03-review-loop-routing.md`.

## Prior Context

- Plan slug: `add-analyzer-generator-review-loop`.
- This is phase `3` of `7`.
- Phase type: `implement`.
- Phase 3 depends on phases `1` and `2`.
- Phase 1 output `out/phase-01-subagent-spec-contract.md` is the authoritative source for subagent naming and compatibility guarantees.
- Phase 2 output `out/phase-02-subagent-registry-contract.md` is the authoritative source for registry wiring and expected prompt files.
- `skills/cypilot/SKILL.md` already reserves routing priority `delegate > compile-phase > execute-phase > plan > generate/analyze`.
- `workflows/generate.md` already requires both `Plan Review Prompt` and `Direct Review Prompt` for file-writing generate flows.
- `workflows/analyze.md` already requires both `Fix Prompt` and `Plan Prompt` when actionable issues exist.
- `skills/cypilot/agents.toml` currently registers legacy codegen and PR review agents plus delegation and plan agents.
- Phase 2 is expected to provide `skills/cypilot/agents/cypilot-generator.md` and `skills/cypilot/agents/cypilot-analyzer.md` before this phase is executed.

## User Decisions
### Already Decided (pre-resolved during planning)
- **Preferred isolated generate or fix subagent**: `cypilot-generator`
- **Preferred isolated review or analyze subagent**: `cypilot-analyzer`
- **Fallback requirement**: keep inline or manual host paths intact when subagent orchestration is unavailable
- **Prompt-family requirement**: reuse the existing generate and analyze prompt pairs instead of inventing a new family
- **Phase handoff artifact**: write a concise routing and invariant summary to `out/phase-03-review-loop-routing.md`

### Decisions Needed During This Phase
#### Review Gates
- None.
#### Confirmation Points
- None.
#### User Input Required
- None.

## Rules

### Routing and Priority Invariants
- The top-level routing priority in `skills/cypilot/SKILL.md` MUST remain `delegate > compile-phase > execute-phase > plan > generate/analyze`.
- Generated-plan phase compilation intent MUST continue to route to `cypilot-phase-compiler`.
- Generated-plan phase execution intent MUST continue to route to `cypilot-phase-runner`.
- This phase MUST keep completion invariants coherent with the updated review-loop wording.
- This phase MUST prefer `cypilot-generator` only for isolated generate or fix work and `cypilot-analyzer` only for isolated review or analyze work.
- This phase MUST keep inline or manual fallback paths intact for hosts without subagent orchestration.
- This phase MUST NOT introduce a new review-loop prompt family.

### Generate Workflow Contract
- For any file-writing `/cypilot-generate` path, completion MUST still require both `Plan Review Prompt` and `Direct Review Prompt` in the same response.
- The generate workflow MUST still emit `Plan Review Prompt` before `Direct Review Prompt`.
- The generate workflow MUST still treat the next-step menu as informational only when files were written and MUST generate both review prompts automatically in the same response.
- Both generate review prompts MUST remain self-contained and usable in a fresh chat.
- Both generate review prompts MUST begin with the phrase `Invoke skill cypilot`.
- Both generate review prompts MUST embed changed file paths, a brief per-file change summary, and the completed `Validation Results` body.
- The generate workflow MUST NOT ask the next agent to regenerate or re-implement the changes.
- The generate workflow MUST keep deterministic-validation prerequisites and final-response gates coherent with any new subagent-aware wording.

### Analyze Workflow Contract
- For any `/cypilot-analyze` result with actionable issues, completion MUST still require both `Fix Prompt` and `Plan Prompt` in the same response.
- The analyze workflow MUST still emit `Fix Prompt` before `Plan Prompt`.
- Both analyze remediation prompts MUST remain self-contained and usable in a fresh chat.
- Both analyze remediation prompts MUST contain the sentence `Invoke skill cypilot`.
- Both analyze remediation prompts MUST embed the full issue list inline with severity, path, line numbers, evidence quotes, and root-cause expectation.
- Both analyze remediation prompts MUST include the target path and kind plus analysis status and deterministic-gate results.
- The analyze workflow MUST keep the next-step menu informational only when actionable issues exist and MUST NOT defer prompt generation to a later turn.
- The analyze workflow MUST keep chat-only output semantics.

### Phase Execution Rules
- Runtime project files listed in `input_files` and `inputs` MUST be read before edits are made.
- Edits MUST be limited to `workflows/generate.md`, `workflows/analyze.md`, and `skills/cypilot/SKILL.md`.
- The phase MUST write `out/phase-03-review-loop-routing.md` with a concise summary of the adopted routing and preserved invariants.
- The summary in `out/phase-03-review-loop-routing.md` MUST mention preferred subagents, preserved prompt-pair contracts, preserved fallback behavior, and any compatibility constraint inherited from phases 1 and 2.
- The phase MUST preserve bounded scope; do not edit registry-generation code, tests, or unrelated workflow sections.

## Input

### Plan contract
- Runtime manifest: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml`
- Confirm phase identity, allowed scope, declared outputs, and downstream dependencies before modifying files.

### Resolved Phase Contract
- Phase file path: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/phase-03-review-loop-routing.md`
- Next phase file path: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/phase-04-generation-pipeline.md`
- Output handoff file for this phase: `out/phase-03-review-loop-routing.md`
- Budget for this phase file: `600` lines maximum

### Structure Contract
- Section order is fixed: frontmatter, preamble, what, prior context, user decisions, rules, input, task, acceptance criteria, output format.
- The preamble text must remain verbatim.
- Runtime project files are read in the Task section; they are not inlined into this phase body.
- The final task step must self-verify against the acceptance criteria.

### Focus Contract
- Make `workflows/generate.md` subagent-aware for isolated generate or fix review-entry paths while keeping the existing `Plan Review Prompt` and `Direct Review Prompt` pair.
- Make `workflows/analyze.md` subagent-aware so bounded fixes prefer `cypilot-generator` and review loops prefer `cypilot-analyzer` while keeping the existing `Fix Prompt` and `Plan Prompt` pair.
- Keep `skills/cypilot/SKILL.md` routing and completion invariants aligned with the revised workflow wording.
- Preserve compatibility for hosts that cannot orchestrate subagents.

## Task

1. Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml` and confirm Phase 3 identity, allowed edit scope, required routing summary output, and the Phase 4 dependency.
2. Read `out/phase-01-subagent-spec-contract.md` and `out/phase-02-subagent-registry-contract.md`, then record the authoritative subagent names, compatibility guarantees, and any constraints this phase must preserve.
3. Read `workflows/generate.md`, `workflows/analyze.md`, `skills/cypilot/SKILL.md`, `skills/cypilot/agents.toml`, `skills/cypilot/agents/cypilot-generator.md`, and `skills/cypilot/agents/cypilot-analyzer.md`, then extract the exact completion-invariant, prompt-pair, fallback, and routing language that must remain valid after the edits.
4. Update `workflows/generate.md` so isolated generate or fix review-entry guidance prefers `cypilot-generator`, preserves automatic same-response review-prompt emission, preserves the existing `Plan Review Prompt` then `Direct Review Prompt` pair, and retains an inline or manual fallback path for hosts without subagent orchestration.
5. Update `workflows/analyze.md` so bounded remediation guidance prefers `cypilot-generator`, review-loop or review-analysis guidance prefers `cypilot-analyzer`, preserves automatic same-response remediation-prompt emission, preserves the existing `Fix Prompt` then `Plan Prompt` pair, and retains an inline or manual fallback path for hosts without subagent orchestration.
6. Update `skills/cypilot/SKILL.md` only as needed so top-level routing and workflow completion invariants stay coherent with the revised generate and analyze wording without changing routing priority order.
7. Write `out/phase-03-review-loop-routing.md` summarizing the preferred subagent routing, preserved prompt-pair contracts, preserved fallback behavior, and compatibility guarantees carried forward from phases 1 and 2.
8. Self-verify the edits against every acceptance criterion below, then report completion using the exact output format.

## Acceptance Criteria

- [ ] `workflows/generate.md` prefers `cypilot-generator` for isolated generate or fix review-entry tasks while preserving the existing same-response `Plan Review Prompt` and `Direct Review Prompt` pair.
- [ ] `workflows/analyze.md` prefers `cypilot-generator` for bounded fixes and `cypilot-analyzer` for review or analysis loops while preserving the existing same-response `Fix Prompt` and `Plan Prompt` pair.
- [ ] `skills/cypilot/SKILL.md` still states the same routing priority and its completion invariants remain coherent with the updated workflow wording.
- [ ] Inline or manual fallback behavior remains documented for hosts that do not support subagent orchestration.
- [ ] `out/phase-03-review-loop-routing.md` exists and concisely summarizes routing, invariants, fallback behavior, and carried-forward compatibility guarantees.
- [ ] This phase file is `600` lines or fewer.
- [ ] No unresolved template variables remain outside fenced code blocks.

## Output Format

When complete, report results in this exact format:
```text
PHASE 3/7 COMPLETE
Status: PASS | FAIL
Files created: {list}
Files modified: {list}
Acceptance criteria:
  [x] Criterion 1 — PASS
  [ ] Criterion 2 — FAIL: {reason}
  ...
Line count: {actual}/600
Notes: {any issues or decisions made}
```

Then generate a copy-pasteable prompt for the next phase inside a single code fence:

```text
Next phase prompt (copy-paste into new chat if needed):
```

```text
I have a Cypilot execution plan at:
  /Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml

Phase 3 is complete (PASS or FAIL).
Please read the plan manifest, then execute Phase 4: "Extend host agent generation pipeline".
The phase file is: /Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/phase-04-generation-pipeline.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.
```
