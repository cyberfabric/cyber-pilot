---
cypilot: true
type: workflow
name: cypilot-generate
description: Create/update artifacts or implement code
version: 1.0
purpose: Universal workflow for creating or updating any artifact or code
---

# Generate

<!-- toc -->

- [Reverse Engineering Prerequisite (BROWNFIELD only)](#reverse-engineering-prerequisite-brownfield-only)
- [Overview](#overview)
- [Context Budget & Overflow Prevention (CRITICAL)](#context-budget--overflow-prevention-critical)
- [Agent Anti-Patterns (STRICT mode)](#agent-anti-patterns-strict-mode)
- [Rules Mode Behavior](#rules-mode-behavior)
- [Phase 0: Ensure Dependencies](#phase-0-ensure-dependencies)
- [Phase 0.1: Plan Escalation Gate](#phase-01-plan-escalation-gate)
- [Phase 0.5: Clarify Output & Context](#phase-05-clarify-output--context)
- [Phase 1: Collect Information](#phase-1-collect-information)
- [Phase 2: Generate](#phase-2-generate)
- [Phase 2.5: Checkpoint (for long artifacts)](#phase-25-checkpoint-for-long-artifacts)
- [Phase 3: Summary](#phase-3-summary)
- [Phase 4: Write](#phase-4-write)
- [Phase 5: Analyze](#phase-5-analyze)
  - [Step 1: Deterministic Validation (tool-based)](#step-1-deterministic-validation-tool-based)
- [Phase 6: Offer Next Steps](#phase-6-offer-next-steps)
- [Error Handling](#error-handling)
- [State Summary](#state-summary)
- [Validation Criteria](#validation-criteria)

<!-- /toc -->

## Reverse Engineering Prerequisite (BROWNFIELD only)

`GREENFIELD`: skip this section and proceed to Phase 0. `BROWNFIELD`: reverse-engineering may inform generated artifacts, code implementation, and code edits. ALWAYS SKIP this section WHEN GREENFIELD — nothing to reverse-engineer.

For BROWNFIELD work:
- Use Protocol Guard's matched WHEN-clause spec resolution for the current request; treat only task-matched, applicable project specs/rules as satisfying the brownfield rules gate.
- If one or more project-specific specs/rules are matched for the current request, load and follow them before generating.
- If no project-specific specs/rules are matched for the current brownfield request, offer auto-config even when unrelated files exist under `{cypilot_path}/config/rules/` or unrelated specs are registered.
- MUST NOT treat mere on-disk rules-file presence or any unrelated registered spec as sufficient to skip auto-config.
- ALWAYS open and follow `{cypilot_path}/.core/requirements/auto-config.md` WHEN user accepts auto-config.

```text
Brownfield project detected — existing code found but no task-matched, applicable project-specific specs/rules were found for this request.
Auto-config can scan your project and generate rules that teach Cypilot your conventions.
This produces config/rules/, heading-level WHEN rules in config/AGENTS.md, navigation rules for existing project guides, and system entries in config/artifacts.toml.

→ Run auto-config now? [yes/no/skip]
Reply with `yes`, `no`, or `skip`.
"yes"  → Suggested for first-time setup; run auto-config now, then return to generation with task-matched project rules.
"no"   → Cancel generation now.
"skip" → Continue without task-matched project specs/rules (reduced quality for this run).
```

If user confirms `yes`: execute auto-config methodology (Phases 1→6), then return to generate. If user says `skip`: proceed without task-matched project-specific specs/rules. If user says `no`: cancel.

## Overview

Artifact generation mode = template + example by default; load checklist up front only when the current rules explicitly require it before writing. Code generation mode = design/spec context first; load checklist during validation/review unless the current rules explicitly require it during implementation. Config mode = create/update config files. After `execution-protocol.md`, you have `TARGET_TYPE`, `RULES`, `KIND`, `PATH`, `MODE`, and resolved phase-appropriate dependencies. Key variables: `{cypilot_path}/config/`, `{ARTIFACTS_REGISTRY}`, `{KITS_PATH}`, `{PATH}`. Use `{KITS_PATH}/artifacts/{KIND}/examples/` for style and quality guidance.

## Context Budget & Overflow Prevention (CRITICAL)

- Budget first: estimate size before loading large docs (for example with `wc -l`) and state the budget for this turn.
- Load only what you need: prefer only the generation-phase sections required for the current `KIND`; defer checklist loading to validation/review unless the current rules explicitly require it earlier.
- Chunk reads and summarize-and-drop: use `read_file` ranges, summarize each chunk, and keep only extracted criteria.
- Fail-safe: if required steps cannot fit in context, stop and output a checkpoint in chat only; do not proceed to writing files.
- Plan escalation: [Phase 0.1](#phase-01-plan-escalation-gate) is mandatory after dependencies load; if budget is exceeded, the agent MUST offer plan escalation before proceeding.

## Agent Anti-Patterns (STRICT mode)

**Reference**: `{cypilot_path}/.core/requirements/agent-compliance.md` for the full list.

Critical failures: `SKIP_TEMPLATE`, `SKIP_EXAMPLE`, `SKIP_CHECKLIST`, `PLACEHOLDER_SHIP`, `NO_CONFIRMATION`, `SIMULATED_VALIDATION`.

Self-check before writing files (MANDATORY in STRICT mode): template loaded, example referenced, no placeholders, and explicit `yes` received. Checklist self-review is required here only when the current rules explicitly require checklist use before writing; otherwise defer checklist review to Phase 5. If any required answer fails → STOP and fix before proceeding. STRICT mode MUST include self-check results in Phase 3 Summary output.

## Rules Mode Behavior

STRICT: generation must load the required generation-phase dependencies (typically template + example for artifacts, design/spec context for code), checklist-driven review must run in Phase 5, and Phase 6 requires validation `PASS`. RELAXED: use user-provided or best-effort phase-appropriate dependencies, still attempt post-write validation automatically when practical, and if validation cannot reach `PASS` after recovery, stop with an explicitly unvalidated result instead of treating it as success.

```text
⚠️ Generated without Cypilot rules (reduced quality assurance)
```

## Phase 0: Ensure Dependencies

After `execution-protocol.md`, you have `KITS_PATH`, the phase-appropriate dependency set, and `REQUIREMENTS`.

Variable checkpoint: `{cpt_cmd}`, `{cypilot_path}`, and `{project_root}` are resolved by `execution-protocol.md`. On context loss or new-chat resume, re-run `cpt --json info` to restore these values before any path-dependent step.

| Condition | Action |
|-----------|--------|
| `rules.md` loaded | Phase-appropriate dependencies were already resolved from rules Dependencies; proceed silently. |
| `rules.md` not loaded | Ask the user to provide/specify the generation-phase dependencies that are actually needed now; request `checklist` only when the current phase or rules explicitly require it. |
| Code mode additional | Ask the user to specify the design artifact if missing; load `{cypilot_path}/.core/requirements/code-checklist.md` up front only when the current rules explicitly require implementation-time checklist guidance, otherwise defer it to Phase 5 review. |

**MUST NOT proceed** to Phase 1 until all generation-phase dependencies required for the current target are available.

Raw-input overflow rule: see `{cypilot_path}/.core/requirements/raw-input-overflow.md`. If the direct user prompt plus all provided files exceeds `500` total lines, the agent MUST stop direct generation long enough to offer `/cypilot-plan` versus continuing here with reduced guarantees, exactly as specified in that file.

## Phase 0.1: Plan Escalation Gate

**MUST** estimate total context from `rules.md`, the generation-phase dependencies actually needed for this run (for example `template.md` and `example.md`, plus `checklist.md` only when explicitly required before writing), expected output size, project context, and ~30% reasoning overhead.

| Estimated total | Action |
|----------------|--------|
| `≤ 1500` lines | Proceed normally — optimal zone, >95% rule adherence. |
| `1501-2500` lines | Proceed with warning + aggressive summarize-and-drop: _"This is a medium-sized task. Activating chunked loading — will checkpoint if context runs low."_ |
| `> 2500` lines | **MUST** offer plan escalation before proceeding. |

> **Why these thresholds**: rule-following quality drops above ~2000 lines of active constraints; SDLC kit files plus output and reasoning can easily exceed 2500.

When `> 2500` lines, offer:

```text
⚠️ This task is large — estimated ~{N} lines of context needed (`rules.md`, active generation dependencies, output, project ctx).
This exceeds the safe single-context budget (~2500 lines). The plan workflow can decompose this into focused phases (≤500 lines each) that ensure every kit rule is followed and nothing is skipped.

Options:
1. Switch to /cypilot-plan (recommended for full quality)
2. Continue here (risk: context overflow, rules may be partially applied)
Reply with `1` or `2`.
1. Switch to /cypilot-plan — Suggested for full quality; this decomposes the task into focused phases and reduces context-overflow risk.
2. Continue here — Faster, but context overflow may reduce rule coverage.
```

If user chooses plan: stop and tell them to run `/cypilot-plan generate {KIND}` with the same parameters. If user chooses continue: proceed with aggressive chunking and log _"Proceeding in single-context mode — quality may be reduced for large artifacts."_

## Phase 0.5: Clarify Output & Context

If system context is unclear, ask:

```text
Which system does this artifact/code belong to?
- {list systems from artifacts.toml}
- Create new system
Reply with the system name or `Create new system`.
```

Store the selected system for registry placement.

If output destination is unclear, ask:

```text
Where should the result go?
- File (will be written to disk and registered)
- Chat only (preview, no file created)
- MCP tool / external system (specify)
Reply with `File`, `Chat only`, or `MCP tool / external system`.
```

Then: store the selected system; if file output + using rules, determine the path, plan the `artifacts.toml` entry, and check `UPDATE` vs `CREATE`; for artifacts identify parent references; for code identify design artifacts + requirement IDs + traceability markers; for new IDs use `cpt-{system}-{kind}-{slug}` and verify uniqueness with `{cpt_cmd} --json list-ids`.

## Phase 1: Collect Information

Artifacts: parse template H2 sections into questions, load the example, and present required questions in one batch with concrete proposals.

```markdown
## Inputs for {KIND}: {name}
Why this input is needed: complete the required sections with concrete, reviewable proposals before writing anything.
### {Section from template H2}
- Context: {from template}
- Proposal: {based on project context}
- Reference: {from example}
...
Reply: `approve all` or provide edits per item
```

Code: parse the related artifact, extract requirements to implement, and present:

```markdown
## Implementation Plan for {KIND}
Source: {related artifact path}
Requirements to implement:
1. {requirement}
2. {requirement}
...
Proposed approach: {implementation strategy}
Why this input is needed: confirm the implementation direction before code changes are written.
Reply: `approve` or describe the modifications you want
```

Input collection rules: MUST ask all required questions in a single batch by default, propose specific answers, use project context, show reasoning clearly, allow modifications, and require final confirmation. MUST NOT ask open-ended questions without proposals, skip questions, assume answers, or proceed without final confirmation.

After approval:

```text
Inputs confirmed. Proceeding to generation...
```

## Phase 2: Generate

Follow the loaded `rules.md` Tasks section.

Artifacts: load the generation-phase dependencies required now (typically template + example, plus checklist only when explicitly required before writing), create content per rules, and generate IDs/structure.

Code: load spec design and any implementation-time dependencies required by the current rules, implement with traceability markers, and use the correct marker format; defer checklist-driven review to Phase 5 unless the current rules explicitly require it earlier.

Standard checks:

- [ ] No placeholders (`TODO`, `TBD`, `[Description]`)
- [ ] All IDs valid and unique
- [ ] All sections filled
- [ ] Parent artifacts referenced correctly
- [ ] Follows conventions
- [ ] Implements all requirements
- [ ] Has tests (if required)
- [ ] Traceability markers present (if `to_code="true"`)

Content rules: MUST follow content requirements exactly, use imperative language, wrap IDs in backticks, reference types from the domain model, and use Cypilot DSL (CDSL) for behavioral sections when applicable. MUST NOT leave placeholders, skip required content, redefine parent types, or use code examples in `DESIGN.md`.

Markdown quality: MUST use empty lines between headings/paragraphs/lists, fenced code blocks with language tags, and proper line-break formatting.

## Phase 2.5: Checkpoint (for long artifacts)

Checkpoint when artifacts have `>10` sections or generation spans multiple turns.

```markdown
### Generation Checkpoint
**Workflow**: /cypilot-generate {KIND}
**Phase**: 2 complete, ready for Phase 3
**Inputs collected**: {section summaries}
**Content generated**: {line count} lines
**Pending**: Summary → Confirmation → Write → Analyze
Resume: Re-read this checkpoint, verify no file changes, continue to Phase 3.
```

Checkpoint policy: default is chat only; write a checkpoint file only if the user explicitly requests/approves it. On resume after compaction: re-read the target file if it exists, re-load rules dependencies, then continue from the saved phase.

## Phase 3: Summary

```markdown
## Summary
**Target**: {TARGET_TYPE}
**Kind**: {KIND}
**Name**: {name}
**Path**: {path}
**Mode**: {MODE}
**Content preview**: {brief overview of what will be created/changed}
**Files to write**: `{path}`: {description}; {additional files if any}
**Artifacts registry**: `{cypilot_path}/config/artifacts.toml`: {entry additions/updates, if any}
**STRICT self-check**: template loaded = {yes/no}; example referenced = {yes/no}; checklist status = {required-and-complete/deferred-to-phase-5}; placeholders absent = {yes/no}; explicit `yes` received = {yes/no}
**Proceed?** [yes/no/modify]
Reply with `yes`, `no`, or `modify`.
`yes` → Suggested when the summary is accurate; write files and continue to validation.
`no` → Cancel without writing files.
`modify` → Revisit the inputs or proposal before any files are written.
```

Responses: `yes` = create files and validate; `no` = cancel; `modify` = revisit a question and iterate (max 3 iterations, then require explicit `continue iterating` or restart workflow).

## Phase 4: Write

Only after confirmation: update `{cypilot_path}/config/artifacts.toml` if a new artifact path is introduced, create directories if needed, write file(s), and verify content.

```text
✓ Written: {path}
```

**MUST NOT** create files before confirmation, create incomplete files, or create placeholder files.

## Phase 5: Analyze

Attempt deterministic validation automatically after generation; do not list it in Next Steps. STRICT mode requires validation `PASS` before Phase 6. RELAXED mode may exit with an explicitly unvalidated result either because no target-applicable deterministic validator exists for the current written output (`Deterministic gate: SKIPPED`) or through the Error Handling recovery branch after repeated validation failure (`Deterministic gate: FAIL`).

> **⛔ CRITICAL**: The agent's own checklist walkthrough is **NOT** a substitute for the applicable deterministic validator command(s). A manual "✅ PASS" table in chat is semantic review, not deterministic validation — these are **separate steps**. See anti-pattern `SIMULATED_VALIDATION`.

### Phase 5a: Deterministic Validation (tool-based)

MUST run deterministic validation as an actual terminal command using the canonical agent-safe form.

Deterministic gate is available only when the current Cypilot configuration and current written output support a canonical validator invocation for this target. Treat availability as proven by active config plus CLI support for the concrete validator command(s) selected for the current output; do **not** infer availability or non-availability from kit prose, examples, `format` labels, or the absence of an exact example in this workflow. Before taking a RELAXED `Deterministic gate: SKIPPED` path, MUST record `Validator availability proof` showing which canonical validator route(s) were checked for the current target (for example project-wide `validate`, artifact-scoped `validate --artifact {PATH}`, `validate-toc {PATH}`, or another deterministic validator explicitly required by the current target) and why none is target-applicable for the current written output.

Artifacts:

```bash
{cpt_cmd} --json validate
```

Specific artifact:

```bash
{cpt_cmd} --json validate --artifact {PATH}
```

Workflow / instruction Markdown file with TOC requirements:

```bash
{cpt_cmd} --json validate-toc {PATH}
```

Language content check (run after writing any `.md` artifact when `[validation] allowed_content_languages` is configured in `.cypilot-workspace.toml`):

```bash
{cpt_cmd} --json check-language {PATH}
```

If `check-language` returns violations (`LANG001`): fix flagged lines — rewrite non-English content in the allowed language(s) — then re-run until `PASS`. Language violations are errors, not warnings; STRICT mode requires `PASS` before Phase 6.

Rules:
- execute the deterministic validator BEFORE any semantic review
- choose the target-applicable deterministic validator command(s) for the current output and rules (for example `{cpt_cmd} --json validate`, `{cpt_cmd} --json validate --artifact {PATH}`, `{cpt_cmd} --json validate-toc {PATH}`, or another deterministic validator explicitly required by the current target)
- use `{cpt_cmd} --json validate-toc {PATH}` as the canonical deterministic validator for workflow / instruction Markdown files when TOC validation applies, and MUST NOT classify that target as having no target-applicable deterministic validator while that route exists
- treat `{cpt_cmd} --json validate --artifact {PATH}` as artifact-scoped only when the current file is a registered artifact target
- record the exact deterministic validator command(s) executed, including subcommand and path flags, plus each command's actual validator exit code and JSON `status` / `error_count` / `warning_count`
- record the overall deterministic gate result across the full required validator set
- if no target-applicable deterministic validator exists for the current written output and RELAXED mode takes the explicitly unvalidated path, record `Deterministic gate: SKIPPED`, explicit `Validator availability proof`, explicit `Skip reason`, and an explicit `Validator-backed evidence note` that no deterministic validator command completed
- if RELAXED recovery stops after repeated validation failure, record the actual failing command results and `Deterministic gate: FAIL`
- in STRICT mode, MUST NOT proceed to Phase 5b until all applicable deterministic validator command(s) for the current target have been run and the overall deterministic gate is `PASS`
- MUST NOT summarize validation without the actual validator output, omit which validator command produced each result, collapse a mixed-result validator set into a single untraceable line, or claim that no validator was target-applicable without the required validator-availability proof
- if FAIL → fix errors → re-run until PASS
- repeated validation failure is a recovery branch, not a PASS substitute

Gate: MUST NOT proceed to Phase 5b until Phase 5a deterministic gate result is recorded (PASS, FAIL, or SKIPPED with proof).

### Phase 5b: Semantic Review + Results Assembly

Only enter Phase 5b after Phase 5a is complete (deterministic gate result recorded).

Only after deterministic PASS (or SKIPPED with recorded proof): load `checklist.md` if it was not already loaded, then self-review generated content against it, verify no placeholders (`TODO`, `TBD`, `FIXME`), verify cross-references are meaningful, and verify content quality/completeness.

Validation Results body below is the single authoritative sub-contract for deterministic validation metadata. Whenever this workflow requires validation results to be embedded elsewhere, paste the completed body verbatim with actual values instead of rewriting the fields; include the conditional `SKIPPED`-only lines only when the deterministic gate is `SKIPPED`.

```markdown
## Validation Results
Deterministic validator command(s): `{exact command(s) run}` | `none; skipped before execution`
Deterministic validator results:
- `{command 1}` → exit code {actual exit code}, status {actual JSON status}, errors {N}, warnings {N}
- `{command N}` → exit code {actual exit code}, status {actual JSON status}, errors {N}, warnings {N}
- `skipped before execution` → no deterministic validator command executed; include this line only when deterministic validation was skipped
Deterministic gate: {PASS|FAIL|SKIPPED}; overall result across all required validator command(s)
Validator availability proof (SKIPPED only): {canonical validator route(s) checked and why none is target-applicable for the current written output}
Skip reason (SKIPPED only): {why deterministic validation was skipped}
Validator-backed evidence note (SKIPPED only): {`none; deterministic validation was skipped, so there is no validator-backed evidence`}
Semantic review basis: {`static/manual only; no validator-backed semantic checker exists` | `validator-backed by {tool}` | `hybrid: validator-backed by {tool} + manual checklist review`}
Semantic Review: checklist coverage {summary}; content quality {summary}; issues found {list or "none"}
```

If deterministic validation passes and semantic review passes: proceed to Phase 6. If no target-applicable deterministic validator exists for the current written output, STRICT mode stops here; RELAXED mode may proceed only on an explicitly unvalidated `Deterministic gate: SKIPPED` path with explicit `Validator availability proof`, `Skip reason`, and `Validator-backed evidence note`. If semantic issues are found: fix them and re-validate from the validator step. If deterministic validation cannot reach PASS after recovery attempts, follow Error Handling: STRICT mode stops here; RELAXED mode may only exit with an explicitly unvalidated `Deterministic gate: FAIL` result and MUST NOT present it as PASS. If Phase 4 wrote or updated any files before either RELAXED explicitly unvalidated exit, Phase 6 still applies and the response remains incomplete until both `Plan Review Prompt` and `Direct Review Prompt` blocks are emitted.

## Phase 6: Offer Next Steps

Prerequisite guard: before constructing `Review Prompts`, verify that Phase 5 produced the complete `Validation Results` body from the canonical template with actual values filled in. If the body is missing, still contains placeholder/template content, or is otherwise incomplete, abort Phase 6 with a clear prerequisite error stating that Phase 5 validation output must be completed before review prompts can be generated.

Read `## Next Steps` from `rules.md` and present:

```text
What would you like to do next?
1. {option from rules Next Steps}
2. {option from rules Next Steps}
3. Other
Reply with the option number or a short custom instruction.
1. {option from rules Next Steps} — Mark as `Suggested` when it is the clearest continuation from the current result; state why and what happens next.
2. {option from rules Next Steps} — State what this does next.
3. Other — Say what you want to change or do next.
```

If Phase 4 wrote or updated any files, the next-step menu is informational only; whether the workflow is ending on the validated success path or any RELAXED explicitly unvalidated exit, it MUST generate the review prompts automatically in the same response after listing the options. MUST NOT ask whether review prompts should be generated and MUST NOT wait for a later user turn to generate them.

If Phase 4 wrote or updated any files, MUST append a final chat-only `Review Prompts` section immediately after the next-step options in the same response. If output was chat-only and no files changed, skip this section.

This applies to any file-writing generate flow, including validated outputs, RELAXED explicitly unvalidated outputs, artifacts, code, workflow/instruction updates, and multi-file edits.

If files were written and the response omits the `Review Prompts` section or either required review prompt, or ends before those blocks are emitted, the generate output is incomplete.

A summary alone is not completion. The `Validation Results` body alone is not completion. The next-step menu alone is not completion. For any file-writing generate flow, the response is invalid unless it ends with `Review Prompts`, then `Plan Review Prompt`, then `Direct Review Prompt`.

Before ending a file-writing response, perform this final self-check: were files written; if yes, was the `Review Prompts` section emitted; if yes, were both `Plan Review Prompt` and `Direct Review Prompt` emitted in that order; only then may the response end.

`Review Prompts` rules — both prompts MUST be **self-contained final prompts** usable in a fresh chat without any prior context:

- explicitly begin with the phrase `Invoke skill cypilot`
- state that `/cypilot-generate` is complete and the next chat is for reviewing the generated changes
- embed inline: changed file paths, what was changed per file (brief summary), kind/target, and the completed `Validation Results` body with actual values
- verify again before emitting the prompts that the `Validation Results` body is present and complete; if not, stop with the Phase 6 prerequisite error instead of generating partial prompts
- do NOT reference "previous chat", "findings above", or any content outside the prompt itself
- the prompt alone must give the next agent everything needed to start work immediately
- generate **two separate prompts**:
 1. `Plan Review Prompt` — route to `/cypilot-plan` when the review scope is broad, multi-file, or needs to be phased or strict coverage
 2. `Direct Review Prompt` — route to `/cypilot-analyze` when the review scope is bounded and can be performed immediately
- include both prompts in the same final response whenever files were written
- MUST NOT ask the next agent to regenerate or re-implement the changes

Template:

```text
Plan Review Prompt (copy-paste into new chat if needed):
```

```text
Invoke skill `cypilot`.

I just completed `/cypilot-generate` and want a phased review plan for the generated changes.

Target: {TARGET_TYPE} / {KIND}
Changed files:
- `{path}` — {brief description of what was created/changed}
- `{additional path}` — {brief description}

{paste the completed Validation Results body from the canonical template above verbatim, preserving field names, order, values, and any conditional `SKIPPED`-only lines exactly as emitted}

Use `/cypilot-plan` to create a phased review plan for these changes.
Focus on review coverage, risk hotspots, and the minimal set of review phases needed for high confidence.
After creating the plan, give me the next execution prompt for the first review phase.

Do not regenerate the implementation. Do not ask me to restate the task unless required inputs are missing.
```

```text
Direct Review Prompt (copy-paste into new chat if needed):
```

```text
Invoke skill `cypilot`.

I just completed `/cypilot-generate` and want an immediate review of the generated changes.

Target: {TARGET_TYPE} / {KIND}
Changed files:
- `{path}` — {brief description of what was created/changed}
- `{additional path}` — {brief description}

{paste the completed Validation Results body from the canonical template above verbatim, preserving field names, order, values, and any conditional `SKIPPED`-only lines exactly as emitted}

Use `/cypilot-analyze` to review these changes now.
Report findings with severity, evidence, risks, regressions, and recommended fixes.

Do not regenerate the implementation. Do not ask me to restate the task unless required inputs are missing.
```

## Error Handling

Tool failure:

```text
⚠️ Tool error: {error message}
→ Check Python environment and dependencies
→ Verify cypilot is correctly configured
→ Run `{cpt_cmd} --json update` to refresh the adapter if the local installation is stale
```

STOP — do not continue with incomplete state.

User abandonment: do not auto-proceed with assumptions; state is resumed by re-running the workflow command; no cleanup is required because no partial files are created before Phase 4.

Validation failure loop (3+ times):

```text
⚠️ Deterministic validation is still failing after repeated fixes. Options:
1. Review checklist requirements manually and fix the reported validator errors
2. Simplify artifact scope or revert the last change set, then re-run validation
3. RELAXED mode only: stop the validated success path and return the result as explicitly unvalidated with `Deterministic gate: FAIL`; do not present it as PASS, and if files were written still emit both review prompts before ending the response
Reply with `1`, `2`, or `3`.
1. Review checklist requirements manually and fix the reported validator errors — Suggested default path; continue trying to reach validator `PASS`.
2. Simplify artifact scope or revert the last change set, then re-run validation — Use this when the current scope is too broad or the last changes were incorrect.
3. RELAXED mode only: stop the validated success path and return the result as explicitly unvalidated with `Deterministic gate: FAIL`; do not present it as PASS, and if files were written still emit both review prompts before ending the response.
```

A legitimate RELAXED `Deterministic gate: SKIPPED` exit for file-writing output is separate from this failure loop: use it only when `Validator availability proof` shows that no canonical validator route is target-applicable for the current written output, and record the explicit `Validator availability proof`, `Skip reason`, `Validator-backed evidence note`, and mandatory review-prompt pair without inventing a validation-failure narrative.

## State Summary

| State | TARGET_TYPE | Has Template | Has Checklist | Has Example |
|-------|-------------|--------------|---------------|-------------|
| Generating artifact | artifact | ✓ | phase-dependent | ✓ |
| Generating code | code | ✗ | phase-dependent | ✗ |

## Validation Criteria

- [ ] `{cypilot_path}/.core/requirements/execution-protocol.md` executed
- [ ] Phase-appropriate dependencies loaded (generation: template/example unless checklist explicitly required; validation/review: checklist when applicable)
- [ ] System context clarified (if using rules)
- [ ] Output destination clarified
- [ ] Parent references identified
- [ ] ID naming verified unique
- [ ] Information collected and confirmed
- [ ] Content generated with no placeholders
- [ ] All IDs follow naming convention
- [ ] All cross-references valid
- [ ] File written after confirmation (if file output)
- [ ] Artifacts registry updated (if file output + rules)
- [ ] Validation executed
- [ ] Language content check executed (`cpt check-language`) when `allowed_content_languages` is configured
- [ ] Exact deterministic validator command(s), per-command validator results, and overall deterministic gate recorded
- [ ] `Validator availability proof` recorded when deterministic gate is `SKIPPED`
- [ ] `Semantic review basis` recorded
- [ ] `Skip reason` and `Validator-backed evidence note` recorded when deterministic gate is `SKIPPED`
- [ ] For file-writing output, the final-response gate self-check was completed before ending the response
- [ ] `Review Prompts` section generated when files were written
- [ ] `Plan Review Prompt` appears before `Direct Review Prompt` whenever files were written
- [ ] Both `Plan Review Prompt` and `Direct Review Prompt` generated in the same response whenever files were written, including RELAXED explicitly unvalidated exits
