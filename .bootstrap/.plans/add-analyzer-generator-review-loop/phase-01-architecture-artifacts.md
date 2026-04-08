```toml
[phase]
plan = "add-analyzer-generator-review-loop"
number = 1
total = 7
type = "implement"
title = "Update architecture artifacts"
depends_on = []
input_manifest = ""
input_signature = ""
input_files = [
  ".bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml",
"architecture/features/subagent-registration.md",
  "architecture/DECOMPOSITION.md",
  "architecture/DESIGN.md",
  "workflows/generate.md",
  "workflows/analyze.md"
]
output_files = [
  "architecture/features/subagent-registration.md",
  "architecture/DECOMPOSITION.md",
  "architecture/DESIGN.md"
]
outputs = ["out/phase-01-subagent-spec-contract.md"]
inputs = []
```

## Preamble

This is a self-contained phase file. All rules, constraints, and kit content
are included below. Project files listed in the Task section must be read
at runtime. Follow the instructions exactly, run any EXECUTE commands as
written, and report results against the acceptance criteria at the end.

## What

Update the architecture specification set for the generalized subagent model. Modify `architecture/features/subagent-registration.md`, `architecture/DECOMPOSITION.md`, and `architecture/DESIGN.md` so they describe canonical `cypilot-generator` and `cypilot-analyzer` subagents, preserve `cypilot-codegen` and `cypilot-pr-review` as backward-compatible specialized agents, and explain that the review loop reuses the existing generate/analyze prompt pairs. Do not edit code, tests, host-generated agent outputs, or unrelated architecture sections.

## Prior Context

- The plan `add-analyzer-generator-review-loop` has 7 phases; this is Phase 1.
- Phase 2 registers canonical analyzer/generator subagents from the architecture contract created here.
- Phase 3 wires generate/analyze review-loop routing from the architecture contract created here.
- The current feature spec centers on two specialized subagents: `cypilot-codegen` and `cypilot-pr-review`.
- `architecture/DECOMPOSITION.md` currently scopes subagent registration as specialized lightweight agent generation.
- `architecture/DESIGN.md` currently names isolated subagents as `codegen` and `PR review` examples and keeps ralphex outside the host-tool-native subagent surface.
- `workflows/generate.md` already defines a file-writing review loop that ends with `Plan Review Prompt` followed by `Direct Review Prompt`.
- `workflows/analyze.md` already defines actionable-analysis remediation prompts that end with `Fix Prompt` followed by `Plan Prompt`.

## User Decisions

### Already Decided (pre-resolved during planning)
- **Canonical general-purpose subagents**: add `cypilot-generator` and `cypilot-analyzer`.
- **Backward compatibility**: keep `cypilot-codegen` and `cypilot-pr-review` as specialized agents.
- **Review-loop contract**: reuse the existing generate/analyze prompt-pair contracts instead of creating a new prompt family.
- **Phase handoff artifact**: write `out/phase-01-subagent-spec-contract.md`.

### Decisions Needed During This Phase
No additional user decisions are required during this phase.

## Rules

### Scope and file boundary
- You MUST modify only `architecture/features/subagent-registration.md`, `architecture/DECOMPOSITION.md`, and `architecture/DESIGN.md`.
- You MUST create `out/phase-01-subagent-spec-contract.md`.
- You MUST NOT edit `workflows/generate.md`, `workflows/analyze.md`, any test file, `skills/cypilot/scripts/cypilot/commands/agents.py`, host-generated agent outputs, or unrelated architecture sections.
- You MUST keep this phase limited to architecture/specification alignment for later implementation phases.

### Subagent model contract
- The updated architecture artifacts MUST introduce `cypilot-generator` and `cypilot-analyzer` as the canonical general-purpose subagents for isolated generate and analyze work.
- The updated architecture artifacts MUST preserve `cypilot-codegen` and `cypilot-pr-review` as backward-compatible specialized subagents rather than removing or renaming them.
- The updated architecture artifacts MUST keep ralphex outside the host-tool-native subagent surface and MUST NOT describe ralphex as a subagent.
- The updated architecture artifacts MUST describe the generalized subagent model as expanding the current specialized surface rather than replacing it.

### Review-loop contract
- The architecture artifacts MUST describe the review loop as reusing existing workflow prompt pairs.
- The architecture artifacts MUST capture that file-writing generate flows already end with `Plan Review Prompt` followed by `Direct Review Prompt`.
- The architecture artifacts MUST capture that actionable analyze flows already end with `Fix Prompt` followed by `Plan Prompt`.
- The architecture artifacts MUST NOT invent a new review-prompt family, alternate prompt ordering, or a separate review workflow outside the existing generate/analyze contracts.

### Architecture alignment
- `architecture/features/subagent-registration.md` MUST align its feature context, actor flow, business logic, definitions of done, and acceptance criteria with the generalized subagent model.
- `architecture/DECOMPOSITION.md` MUST describe Subagent Registration as a generalized registration and generation surface for tool-scoped subagents, while preserving room for specialized agents.
- `architecture/DESIGN.md` MUST keep the AI Agent layer, Agent Entry Points layer, and `cpt-cypilot-component-agent-generator` description aligned with the generalized subagent model and the existing review-loop contracts.
- The resulting architecture wording MUST be specific enough that Phase 2 can register the new canonical subagents and Phase 3 can wire review-loop routing without reopening architecture scope.

### Runtime reads and execution discipline
- You MUST read the runtime source files listed in the Task section before editing.
- You MUST use the workflow excerpts only as architecture contract evidence for prompt-pair reuse and bounded remediation behavior.
- You MUST save a concise architecture delta summary to `out/phase-01-subagent-spec-contract.md` for downstream phases.

### Validation and quality
- You MUST keep the phase outputs free of unresolved brace-delimited template variables outside code fences.
- The architecture delta summary MUST be concise and no longer than 120 lines.
- You MUST self-verify every acceptance criterion before reporting completion.

## Input

### Plan contract
- Runtime manifest: `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml`
- Confirm phase identity, allowed scope, declared outputs, and downstream dependencies before modifying files.

```markdown
## Architecture delta to implement
- Canonical general-purpose subagents to add in architecture docs: `cypilot-generator`, `cypilot-analyzer`
- Specialized agents to preserve: `cypilot-codegen`, `cypilot-pr-review`
- Host-tool-native subagents remain distinct from external ralphex delegation

## Existing workflow prompt-pair contracts that architecture must reuse
- Generate workflow: file-writing outputs end with `Plan Review Prompt` then `Direct Review Prompt`
- Analyze workflow: actionable findings end with `Fix Prompt` then `Plan Prompt`
- Review-loop behavior should be documented as reuse of these existing prompt pairs, not as a new prompt family

## Files to update
- `architecture/features/subagent-registration.md`
- `architecture/DECOMPOSITION.md`
- `architecture/DESIGN.md`

## Downstream consumers
- Phase 2 uses the updated architecture contract to register canonical analyzer/generator subagents.
- Phase 3 uses the updated architecture contract to wire subagent-aware generate/analyze review-loop routing.
```

## Task

1. Read `/Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml` and confirm Phase 1 identity, allowed edit scope, required summary output, and downstream dependencies for Phases 2 and 3.
2. Read `architecture/features/subagent-registration.md` and extract the current feature context, actor flow, business-logic flow, definitions of done, and acceptance criteria that still describe only the specialized subagents.
3. Read `architecture/DECOMPOSITION.md` and `architecture/DESIGN.md` and extract the current decomposition scope, architecture-layer wording, and agent-generator wording that must be generalized while keeping ralphex outside the host-tool-native subagent surface.
4. Read `workflows/generate.md` and `workflows/analyze.md` and extract the existing prompt-pair and bounded-remediation contracts that the architecture docs must reference without rewriting those workflows.
5. Update `architecture/features/subagent-registration.md` so its overview, purpose, actor flow, business logic, definitions of done, acceptance criteria, and additional context describe the generalized subagent model, the preserved specialized agents, and the reused review-loop prompt pairs.
6. Update `architecture/DECOMPOSITION.md` and `architecture/DESIGN.md` so Subagent Registration, the AI Agent layer, the Agent Entry Points layer, and `cpt-cypilot-component-agent-generator` all align with the generalized subagent model and the preserved specialized agents.
7. Write `out/phase-01-subagent-spec-contract.md` summarizing the architecture delta, the preserved backward-compatible specialized agents, the reused workflow prompt pairs, and the downstream contract for Phases 2 and 3.
8. Self-verify the edited files and the summary against every acceptance criterion, including scope limits, prompt-pair reuse, backward compatibility, concise summary length, and absence of unresolved brace-delimited template variables outside code fences.

## Acceptance Criteria

- [ ] `architecture/features/subagent-registration.md` defines `cypilot-generator` and `cypilot-analyzer` as canonical general-purpose subagents for isolated generate/analyze work.
- [ ] `architecture/features/subagent-registration.md` preserves `cypilot-codegen` and `cypilot-pr-review` as backward-compatible specialized subagents.
- [ ] `architecture/features/subagent-registration.md`, `architecture/DECOMPOSITION.md`, and `architecture/DESIGN.md` all describe the review loop as reuse of the existing generate/analyze prompt pairs rather than a new prompt family.
- [ ] `architecture/DECOMPOSITION.md` and `architecture/DESIGN.md` align the subagent-registration architecture with a generalized subagent model while keeping ralphex outside the host-tool-native subagent surface.
- [ ] `out/phase-01-subagent-spec-contract.md` exists, summarizes the architecture delta and downstream contract for Phases 2 and 3, and is no longer than 120 lines.
- [ ] Only `architecture/features/subagent-registration.md`, `architecture/DECOMPOSITION.md`, `architecture/DESIGN.md`, and `out/phase-01-subagent-spec-contract.md` are modified or created by this phase.
- [ ] No unresolved brace-delimited template variables remain outside code fences in the edited outputs or the completion report.

## Output Format

When complete, report results in this exact format:
```text
PHASE 1/7 COMPLETE
Status: PASS | FAIL
Files created: {list}
Files modified: {list}
Acceptance criteria:
  [x] Criterion 1 — PASS
  [ ] Criterion 2 — FAIL: {reason}
  ...
Line count: {actual}/{budget}
Notes: {any issues or decisions made}
```

Then generate a **copy-pasteable prompt** for the next phase inside a single code fence:

```text
Next phase prompt (copy-paste into new chat if needed):
```

```text
I have a Cypilot execution plan at:
  /Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/plan.toml

Phase 1 is complete (PASS or FAIL).
Please read the plan manifest, then execute Phase 2: "Register canonical analyzer and generator subagents".
The phase file is: /Volumes/CaseSensitive/coding/cypilot/.bootstrap/.plans/add-analyzer-generator-review-loop/phase-02-canonical-subagents.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for the next phase.
```
