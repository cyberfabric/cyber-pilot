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
- [Phase 6: Offer Next Steps](#phase-6-offer-next-steps)
- [Error Handling](#error-handling)
- [State Summary](#state-summary)
- [Validation Criteria](#validation-criteria)

<!-- /toc -->

ALWAYS open and follow `{cypilot_path}/.core/skills/cypilot/SKILL.md` FIRST WHEN {cypilot_mode} is `off`

**Type**: Operation

ALWAYS open and follow `{cypilot_path}/.core/requirements/execution-protocol.md` FIRST

ALWAYS open and follow `{cypilot_path}/.core/requirements/reverse-engineering.md` WHEN BROWNFIELD project AND user requests to analyze codebase, search in code, or generate artifacts from existing code

NEVER open reverse-engineering.md WHEN GREENFIELD project — there is no code to reverse-engineer

ALWAYS open and follow `{cypilot_path}/.core/requirements/code-checklist.md` WHEN user requests implementing, generating, or editing code (Code mode)

ALWAYS open and follow `{cypilot_path}/.core/requirements/prompt-engineering.md` WHEN user requests generation or updates of:
- System prompts, agent prompts, or LLM prompts
- Agent instructions or agent guidelines
- Skills, workflows, or methodologies
- AGENTS.md or navigation rules
- Any document containing instructions for AI agents

When `prompt-engineering.md` is loaded for generation/update of AI instruction documents, treat compact-prompts optimization as a **HIGH-priority requirement**: actively search for safe opportunities to reduce loaded context while keeping instructions explicit, strict, and operationally complete.

For context compaction recovery during multi-phase workflows, follow `{cypilot_path}/.core/requirements/execution-protocol.md` Section "Compaction Recovery".

## Reverse Engineering Prerequisite (BROWNFIELD only)

`GREENFIELD`: skip this section and proceed to Phase 0. `BROWNFIELD`: reverse-engineering may inform generated artifacts. ALWAYS SKIP this section WHEN GREENFIELD — nothing to reverse-engineer.

For BROWNFIELD work:
- Check whether `{cypilot_path}/config/rules/` has any `.md` files and whether `cypilot.py info` reports any `specs`.
- If rules or specs exist, load and follow them before generating.
- If neither exists, offer auto-config.
- ALWAYS open and follow `{cypilot_path}/.core/requirements/auto-config.md` WHEN user accepts auto-config.

```text
Brownfield project detected — existing code found but no project-specific rules configured.
Auto-config can scan your project and generate rules that teach Cypilot your conventions.
This produces config/rules/, heading-level WHEN rules in config/AGENTS.md, navigation rules for existing project guides, and system entries in config/artifacts.toml.

→ Run auto-config now? [yes/no/skip]
"yes"  → Run auto-config methodology (recommended for first-time setup)
"no"   → Cancel generation
"skip" → Continue without project rules (reduced quality)
```

If user confirms `yes`: execute auto-config methodology (Phases 1→6), then return to generate. If user says `skip`: proceed without project-specific rules. If user says `no`: cancel.

## Overview

Artifact mode = template + checklist + example. Code mode = checklist only. Config mode = create/update config files. After `execution-protocol.md`, you have `TARGET_TYPE`, `RULES`, `KIND`, `PATH`, `MODE`, and resolved dependencies. Key variables: `{cypilot_path}/config/`, `{ARTIFACTS_REGISTRY}`, `{KITS_PATH}`, `{PATH}`. Use `{KITS_PATH}/artifacts/{KIND}/examples/` for style and quality guidance.

## Context Budget & Overflow Prevention (CRITICAL)

- Budget first: estimate size before loading large docs (for example with `wc -l`) and state the budget for this turn.
- Load only what you need: prefer only the template, checklist, and example sections required for the current `KIND`.
- Chunk reads and summarize-and-drop: use `read_file` ranges, summarize each chunk, and keep only extracted criteria.
- Fail-safe: if required steps cannot fit in context, stop and output a checkpoint in chat only; do not proceed to writing files.
- Plan escalation: [Phase 0.1](#phase-01-plan-escalation-gate) is mandatory after dependencies load; if budget is exceeded, the agent MUST offer plan escalation before proceeding.

## Agent Anti-Patterns (STRICT mode)

**Reference**: `{cypilot_path}/.core/requirements/agent-compliance.md` for the full list.

Critical failures: `SKIP_TEMPLATE`, `SKIP_EXAMPLE`, `SKIP_CHECKLIST`, `PLACEHOLDER_SHIP`, `NO_CONFIRMATION`, `SIMULATED_VALIDATION`.

Self-check before writing files (MANDATORY in STRICT mode): template loaded, example referenced, checklist self-review complete, no placeholders, and explicit `yes` received. If any answer fails → STOP and fix before proceeding. STRICT mode MUST include self-check results in Phase 3 Summary output.

## Rules Mode Behavior

STRICT: template, checklist, example, and post-write validation are required for high quality. RELAXED: user-provided or best-effort template/example/checklist, optional validation, and no quality guarantee.

```text
⚠️ Generated without Cypilot rules (reduced quality assurance)
```

## Phase 0: Ensure Dependencies

After `execution-protocol.md`, you have `KITS_PATH`, `TEMPLATE`, `CHECKLIST`, `EXAMPLE`, and `REQUIREMENTS`.

| Condition | Action |
|-----------|--------|
| `rules.md` loaded | Dependencies were already resolved from rules Dependencies; proceed silently. |
| `rules.md` not loaded | Ask the user to provide/specify missing `checklist`, `template`, or `example`. |
| Code mode additional | Load `{cypilot_path}/.core/requirements/code-checklist.md` and ask the user to specify the design artifact if missing. |

**MUST NOT proceed** to Phase 1 until all dependencies are available.

## Phase 0.1: Plan Escalation Gate

**MUST** estimate total context from `rules.md`, `template.md`, `checklist.md`, `example.md`, expected output size, project context, and ~30% reasoning overhead.

| Estimated total | Action |
|----------------|--------|
| `≤ 1500` lines | Proceed normally — optimal zone, >95% rule adherence. |
| `1501-2500` lines | Proceed with warning + aggressive summarize-and-drop: _"This is a medium-sized task. Activating chunked loading — will checkpoint if context runs low."_ |
| `> 2500` lines | **MUST** offer plan escalation before proceeding. |

> **Why these thresholds**: rule-following quality drops above ~2000 lines of active constraints; SDLC kit files plus output and reasoning can easily exceed 2500.

When `> 2500` lines, offer:

```text
⚠️ This task is large — estimated ~{N} lines of context needed (`rules.md`, `template.md`, `checklist.md`, `example.md`, output, project ctx).
This exceeds the safe single-context budget (~2500 lines). The plan workflow can decompose this into focused phases (≤500 lines each) that ensure every kit rule is followed and nothing is skipped.

Options:
1. Switch to /cypilot-plan (recommended for full quality)
2. Continue here (risk: context overflow, rules may be partially applied)
```

If user chooses plan: stop and tell them to run `/cypilot-plan generate {KIND}` with the same parameters. If user chooses continue: proceed with aggressive chunking and log _"Proceeding in single-context mode — quality may be reduced for large artifacts."_

## Phase 0.5: Clarify Output & Context

If system context is unclear, ask:

```text
Which system does this artifact/code belong to?
- {list systems from artifacts.toml}
- Create new system
```

Store the selected system for registry placement.

If output destination is unclear, ask:

```text
Where should the result go?
- File (will be written to disk and registered)
- Chat only (preview, no file created)
- MCP tool / external system (specify)
```

Then: store the selected system; if file output + using rules, determine the path, plan the `artifacts.toml` entry, and check `UPDATE` vs `CREATE`; for artifacts identify parent references; for code identify design artifacts + requirement IDs + traceability markers; for new IDs use `cpt-{system}-{kind}-{slug}` and verify uniqueness with `cypilot list-ids`.

## Phase 1: Collect Information

Artifacts: parse template H2 sections into questions, load the example, and present required questions in one batch with concrete proposals.

```markdown
## Inputs for {KIND}: {name}
### {Section from template H2}
- Context: {from template}
- Proposal: {based on project context}
- Reference: {from example}
...
Reply: "approve all" or edits per item
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
Reply: "approve" or modifications
```

Input collection rules: MUST ask all required questions in a single batch by default, propose specific answers, use project context, show reasoning clearly, allow modifications, and require final confirmation. MUST NOT ask open-ended questions without proposals, skip questions, assume answers, or proceed without final confirmation.

After approval:

```text
Inputs confirmed. Proceeding to generation...
```

## Phase 2: Generate

Follow the loaded `rules.md` Tasks section.

Artifacts: load template/checklist/example, create content per rules, generate IDs/structure, then self-review against the checklist.

Code: load spec design + checklist, implement with traceability markers, use the correct marker format, then quality-check traceability.

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
**STRICT self-check**: template loaded = {yes/no}; example referenced = {yes/no}; checklist reviewed = {yes/no}; placeholders absent = {yes/no}; explicit `yes` received = {yes/no}
**Proceed?** [yes/no/modify]
```

Responses: `yes` = create files and validate; `no` = cancel; `modify` = revisit a question and iterate (max 3 iterations, then require explicit `continue iterating` or restart workflow).

## Phase 4: Write

Only after confirmation: update `{cypilot_path}/config/artifacts.toml` if a new artifact path is introduced, create directories if needed, write file(s), and verify content.

```text
✓ Written: {path}
```

**MUST NOT** create files before confirmation, create incomplete files, or create placeholder files.

## Phase 5: Analyze

Run validation automatically after generation; do not list it in Next Steps.

> **⛔ CRITICAL**: The agent's own checklist walkthrough is **NOT** a substitute for `cpt validate`. A manual "✅ PASS" table in chat is semantic review, not deterministic validation — these are **separate steps**. See anti-pattern `SIMULATED_VALIDATION`.

### Step 1: Deterministic Validation (tool-based)

MUST run `cpt validate` as an actual terminal command.

Artifacts:

```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py validate
```

Specific artifact:

```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py validate --artifact {PATH}
```

Rules: execute the validator BEFORE any semantic review; include exit code and JSON `status` / `error_count` / `warning_count`; MUST NOT proceed until `cpt validate` returns `"status": "PASS"`; MUST NOT summarize validation without the actual validator output. If FAIL → fix errors → re-run until PASS.

Only after PASS: self-review generated content against `checklist.md`, verify no placeholders (`TODO`, `TBD`, `FIXME`), verify cross-references are meaningful, and verify content quality/completeness.

```markdown
## Validation Results
Deterministic (`cpt validate`): exit code {0|2}, status {PASS|FAIL}, errors {N}, warnings {N}
Semantic Review: checklist coverage {summary}; content quality {summary}; issues found {list or "none"}
```

If both pass: proceed to Phase 6. If semantic issues are found: fix them and re-validate from the validator step.

## Phase 6: Offer Next Steps

Read `## Next Steps` from `rules.md` and present:

```text
What would you like to do next?
1. {option from rules Next Steps}
2. {option from rules Next Steps}
3. Other
```

## Error Handling

Tool failure:

```text
⚠️ Tool error: {error message}
→ Check Python environment and dependencies
→ Verify cypilot is correctly configured
→ Run /cypilot-adapter to refresh
```

STOP — do not continue with incomplete state.

User abandonment: do not auto-proceed with assumptions; state is resumed by re-running the workflow command; no cleanup is required because no partial files are created before Phase 4.

Validation failure loop (3+ times):

```text
⚠️ Validation failing repeatedly. Options:
1. Review checklist requirements manually
2. Simplify artifact scope
3. Skip validation (RELAXED mode only)
```

## State Summary

| State | TARGET_TYPE | Has Template | Has Checklist | Has Example |
|-------|-------------|--------------|---------------|-------------|
| Generating artifact | artifact | ✓ | ✓ | ✓ |
| Generating code | code | ✗ | ✓ | ✗ |

## Validation Criteria

- [ ] `{cypilot_path}/.core/requirements/execution-protocol.md` executed
- [ ] Dependencies loaded (checklist, template, example)
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
