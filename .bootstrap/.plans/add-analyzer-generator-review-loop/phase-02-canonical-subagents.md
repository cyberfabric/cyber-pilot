```toml
[phase]
plan = "add-analyzer-generator-review-loop"
number = 2
total = 7
type = "implement"
title = "Register canonical analyzer and generator subagents"
depends_on = [1]
input_manifest = ""
input_signature = ""
input_files = [
  ".bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml",
"skills/cypilot/agents.toml",
  "skills/cypilot/agents/cypilot-codegen.md",
  "skills/cypilot/agents/cypilot-pr-review.md",
  "architecture/features/subagent-registration.md"
]
output_files = [
  "skills/cypilot/agents.toml",
  "skills/cypilot/agents/cypilot-generator.md",
  "skills/cypilot/agents/cypilot-analyzer.md",
  "skills/cypilot/agents/cypilot-codegen.md",
  "skills/cypilot/agents/cypilot-pr-review.md"
]
outputs = ["out/phase-02-subagent-registry-contract.md"]
inputs = ["out/phase-01-subagent-spec-contract.md"]
```

## Preamble

This is a self-contained phase file. All rules, constraints, and kit content
are included below. Project files listed in the Task section must be read
at runtime. Follow the instructions exactly, run any EXECUTE commands as
written, and report results against the acceptance criteria at the end.

## What

Register the canonical generalized subagent layer by adding `cypilot-generator` and `cypilot-analyzer` to the Cypilot agent registry, creating their prompt files, and preserving the existing specialized legacy-compatible `cypilot-codegen` and `cypilot-pr-review` profiles. Scope is limited to the registry source files under `skills/cypilot/agents/` plus one intermediate contract summary in `out/`; do not expand into workflow routing, generated host-tool outputs, or test changes.

## Prior Context

- The active plan is `add-analyzer-generator-review-loop` and this phase is 2 of 7.
- Phase 2 depends on Phase 1 and declares `out/phase-01-subagent-spec-contract.md` as its required upstream input.
- The plan declares five source-file outputs for this phase plus `out/phase-02-subagent-registry-contract.md`.
- The brief states that the Phase 1 contract is the source of truth for names, responsibilities, and backward-compatibility constraints.
- The current registry already contains `cypilot-codegen`, `cypilot-pr-review`, `cypilot-ralphex`, `cypilot-phase-runner`, and `cypilot-phase-compiler`.
- The current specialized prompt files both bootstrap through `config/AGENTS.md`, `.gen/AGENTS.md`, and `.core/skills/cypilot/SKILL.md` before routing into their narrow workflows.
- The current feature spec defines subagents as host-tool-native agent contexts.
- The current feature spec explicitly excludes ralphex delegation from the subagent registration surface.
- The current feature spec excludes Windsurf from subagent support.

## User Decisions
### Already Decided (pre-resolved during planning)
- **Canonical additions**: Add `cypilot-generator` and `cypilot-analyzer` to `skills/cypilot/agents.toml`.
- **Legacy compatibility**: Preserve `cypilot-codegen` and `cypilot-pr-review` as specialized legacy-compatible profiles.
- **Prompt scope**: Create the new canonical prompt files under `skills/cypilot/agents/`.
- **Intermediate handoff**: Save a registry and prompt contract summary to `out/phase-02-subagent-registry-contract.md`.
### Decisions Needed During This Phase
#### Review Gates
- None.
#### Confirmation Points
- None.
#### User Input Required
- None.

## Rules

### Scope and compatibility
- MUST add `cypilot-generator` and `cypilot-analyzer` entries to `skills/cypilot/agents.toml`.
- MUST create `skills/cypilot/agents/cypilot-generator.md` and `skills/cypilot/agents/cypilot-analyzer.md`.
- MUST preserve `cypilot-codegen` and `cypilot-pr-review` as specialized legacy-compatible profiles.
- MUST preserve existing non-target registry entries such as `cypilot-ralphex`, `cypilot-phase-runner`, and `cypilot-phase-compiler`.
- MUST align any edits to `cypilot-codegen.md` and `cypilot-pr-review.md` only where the generalized model requires it.
- MUST save `out/phase-02-subagent-registry-contract.md` as the downstream handoff for Phase 3.
- MUST keep the phase limited to the files listed in `output_files` and `outputs`.

### Authority and architectural constraints
- MUST treat `out/phase-01-subagent-spec-contract.md` as the authoritative source for canonical names, responsibilities, and backward-compatibility constraints.
- MUST keep subagents host-tool-native rather than modeling external delegation as a subagent.
- MUST keep ralphex delegation outside the subagent registration surface.
- MUST keep Windsurf outside subagent support.
- MUST preserve existing workflow, command, and generated-output behavior outside this registry and prompt source update.

### Runtime-read discipline
- MUST read every runtime input listed in `input_files` and `inputs` before editing outputs.
- MUST use explicit `Read <file>` task steps for every runtime-read item.
- MUST NOT load workflow markdown, `commands/agents.py`, generated `.claude/agents/*` outputs, or unrelated tests.
- MUST NOT substitute unlisted files for the declared Phase 1 contract.

### Deliverable quality
- MUST keep the canonical prompts consistent with the bootstrap path pattern already used by the specialized prompts.
- MUST make the canonical prompts generalized and reusable while keeping the legacy prompts narrow and purpose-built.
- MUST record the final registry shape, prompt responsibilities, preserved compatibility rules, and Phase 3 assumptions in the `out/` handoff.
- MUST self-verify against the acceptance criteria before completing the phase.

## Input

### Plan contract
- Runtime manifest: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml`
- Confirm phase identity, allowed scope, declared outputs, and downstream dependencies before modifying files.

### Phase contract
- Phase file: `phase-02-canonical-subagents.md`
- Phase title: `Register canonical analyzer and generator subagents`
- Phase type: `implement`
- Depends on: Phase 1
- Downstream dependency: Phase 3 consumes `out/phase-02-subagent-registry-contract.md`

### Compilation constraints
- Required section order: TOML frontmatter, Preamble, What, Prior Context, User Decisions, Rules, Input, Task, Acceptance Criteria, Output Format.
- The preamble must match the template verbatim.
- The output format must use the required completion report and next-phase prompt template.
- No unresolved placeholder variables may appear outside code fences.

### Budget
- Phase file target: `<= 550` lines.
- Inlined content estimate: `~150` lines.
- Total execution context target: `<= 1400` lines.

### Phase-specific focus
- Add canonical `cypilot-generator` and `cypilot-analyzer` registry entries.
- Create the new canonical prompt files under `skills/cypilot/agents/`.
- Preserve `cypilot-codegen` and `cypilot-pr-review` as specialized legacy-compatible profiles.
- Save a registry and prompt contract summary to `out/phase-02-subagent-registry-contract.md`.

## Task

1. Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml` and confirm Phase 2 identity, allowed edit scope, required contract output, and the Phase 3 dependency.
2. Read `out/phase-01-subagent-spec-contract.md` and treat it as the source of truth for canonical names, responsibilities, and backward-compatibility constraints.
3. Read `architecture/features/subagent-registration.md` to confirm host-tool-native subagent scope, ralphex separation, and Windsurf exclusion.
4. Read `skills/cypilot/agents.toml` to capture the current registry shape and the non-target entries that must remain intact.
5. Read `skills/cypilot/agents/cypilot-codegen.md` and `skills/cypilot/agents/cypilot-pr-review.md` to capture the current bootstrap path pattern and narrow legacy prompt responsibilities.
6. Update `skills/cypilot/agents.toml` by adding canonical `cypilot-generator` and `cypilot-analyzer` entries without deleting or repurposing the existing specialized entries.
7. Create `skills/cypilot/agents/cypilot-generator.md` and `skills/cypilot/agents/cypilot-analyzer.md` so they reflect the canonical generalized responsibilities from the upstream contract and the current feature spec.
8. Update `skills/cypilot/agents/cypilot-codegen.md` and `skills/cypilot/agents/cypilot-pr-review.md` only where needed to align them with the canonical generalized model while preserving their narrow legacy-compatible purpose.
9. Write `out/phase-02-subagent-registry-contract.md` summarizing the final registry shape, canonical responsibilities, preserved backward-compatibility behavior, and the assumptions Phase 3 must preserve.
10. Self-verify that only the five listed source outputs and the single listed `out/` file were changed, and that all acceptance criteria pass.

## Acceptance Criteria

- [ ] `skills/cypilot/agents.toml` contains `cypilot-generator` and `cypilot-analyzer` entries and still contains `cypilot-codegen` and `cypilot-pr-review`.
- [ ] `skills/cypilot/agents/cypilot-generator.md` exists and defines the canonical generalized generation subagent.
- [ ] `skills/cypilot/agents/cypilot-analyzer.md` exists and defines the canonical generalized analysis subagent.
- [ ] `skills/cypilot/agents/cypilot-codegen.md` and `skills/cypilot/agents/cypilot-pr-review.md` remain specialized legacy-compatible prompts rather than being replaced by the canonical prompts.
- [ ] `out/phase-02-subagent-registry-contract.md` exists and records names, responsibilities, backward-compatibility constraints, and Phase 3 assumptions.
- [ ] No files outside `skills/cypilot/agents.toml`, `skills/cypilot/agents/cypilot-generator.md`, `skills/cypilot/agents/cypilot-analyzer.md`, `skills/cypilot/agents/cypilot-codegen.md`, `skills/cypilot/agents/cypilot-pr-review.md`, and `out/phase-02-subagent-registry-contract.md` are modified.
- [ ] No unresolved placeholder variables appear outside code fences in this phase file.
- [ ] This phase file is at or below 550 lines.

## Output Format

When complete, report results in this exact format:
```text
PHASE 2/7 COMPLETE
Status: PASS | FAIL
Files created: skills/cypilot/agents/cypilot-generator.md, skills/cypilot/agents/cypilot-analyzer.md, out/phase-02-subagent-registry-contract.md
Files modified: skills/cypilot/agents.toml, skills/cypilot/agents/cypilot-codegen.md, skills/cypilot/agents/cypilot-pr-review.md
Acceptance criteria:
  [x] Criterion 1 — PASS
  [ ] Criterion 2 — FAIL: reason
  ...
Line count: actual/550
Notes: any issues or decisions made
```

Then generate a copy-pasteable prompt for the next phase inside a single code fence:

```text
Next phase prompt (copy-paste into new chat if needed):
```

```text
I have a Cypilot execution plan at:
  /Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml

Phase 2 is complete (PASS or FAIL).
Please read the plan manifest, then execute Phase 3: "Wire subagent-aware generate/analyze review loop".
The phase file is: /Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/phase-03-review-loop-routing.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.
```

