---
cypilot: true
type: workflow
name: cypilot-generate
description: Create/update artifacts or implement code
version: 1.0
purpose: Universal workflow for creating or updating any artifact or code
---

# Generate

ALWAYS open and follow `{cypilot_path}/.core/skills/cypilot/SKILL.md` FIRST WHEN {cypilot_mode} is `off`

**Type**: Operation

ALWAYS open and follow `{cypilot_path}/.core/requirements/execution-protocol.md` FIRST

ALWAYS open and follow `{cypilot_path}/.core/requirements/reverse-engineering.md` WHEN BROWNFIELD project AND user requests to analyze codebase, search in code, or generate artifacts from existing code

NEVER open reverse-engineering.md WHEN GREENFIELD project — there is no code to reverse-engineer

ALWAYS open and follow `{cypilot_path}/.core/requirements/code-checklist.md` WHEN user requests implementing, generating, or editing code (Code mode)

OPEN and follow `{cypilot_path}/.core/requirements/prompt-engineering.md` WHEN user requests generation or updates of:
- System prompts, agent prompts, or LLM prompts
- Agent instructions or agent guidelines
- Skills, workflows, or methodologies
- AGENTS.md or navigation rules
- Any document containing instructions for AI agents

For context compaction recovery during multi-phase workflows, follow `{cypilot_path}/.core/requirements/execution-protocol.md` Section "Compaction Recovery".

---

## Table of Contents

- [Generate](#generate)
  - [Table of Contents](#table-of-contents)
  - [Reverse Engineering Prerequisite (BROWNFIELD only)](#reverse-engineering-prerequisite-brownfield-only)
  - [Overview](#overview)
    - [Resolved Variables (from `execution-protocol.md` + info)](#resolved-variables-from-execution-protocolmd--info)
  - [Context Budget \& Overflow Prevention (CRITICAL)](#context-budget--overflow-prevention-critical)
  - [⛔ Agent Anti-Patterns (STRICT mode)](#-agent-anti-patterns-strict-mode)
  - [Rules Mode Behavior](#rules-mode-behavior)
  - [Phase 0: Ensure Dependencies](#phase-0-ensure-dependencies)
    - [Verify Rules Loaded](#verify-rules-loaded)
    - [For Code (additional)](#for-code-additional)
  - [Phase 0.5: Clarify Output \& Context](#phase-05-clarify-output--context)
    - [System Context (if using rules)](#system-context-if-using-rules)
    - [Output Destination](#output-destination)
    - [Parent Artifact References](#parent-artifact-references)
    - [ID Naming](#id-naming)
  - [Phase 1: Collect Information](#phase-1-collect-information)
    - [For Artifacts (template-based)](#for-artifacts-template-based)
    - [For Code (checklist-based)](#for-code-checklist-based)
    - [Input Collection Rules](#input-collection-rules)
    - [Confirmation](#confirmation)
  - [Phase 2: Generate](#phase-2-generate)
    - [For Artifacts (rules.md Tasks)](#for-artifacts-rulesmd-tasks)
    - [For Code (rules.md Tasks)](#for-code-rulesmd-tasks)
    - [Content Rules](#content-rules)
    - [Markdown Quality](#markdown-quality)
  - [Phase 2.5: Checkpoint (for long artifacts)](#phase-25-checkpoint-for-long-artifacts)
  - [Phase 3: Summary](#phase-3-summary)
  - [Phase 4: Write](#phase-4-write)
  - [Phase 5: Analyze](#phase-5-analyze)
    - [Step 1: Deterministic Validation (tool-based)](#step-1-deterministic-validation-tool-based)
    - [Step 2: Semantic Review (LLM-based)](#step-2-semantic-review-llm-based)
    - [Step 3: Report Both Results](#step-3-report-both-results)
  - [Phase 6: Offer Next Steps](#phase-6-offer-next-steps)
  - [Error Handling](#error-handling)
    - [Tool Failures](#tool-failures)
    - [User Abandonment](#user-abandonment)
    - [Validation Failure Loop](#validation-failure-loop)
  - [State Summary](#state-summary)
  - [Validation Criteria](#validation-criteria)

---

## Reverse Engineering Prerequisite (BROWNFIELD only)

**GREENFIELD vs BROWNFIELD**:
- **GREENFIELD**: New project with no existing code — skip this section entirely, proceed to Phase 0
- **BROWNFIELD**: Existing project with source code — reverse-engineering helps extract design from code

ALWAYS SKIP this section WHEN GREENFIELD — nothing to reverse-engineer

**BROWNFIELD only** — when existing code needs to inform artifacts:

1. **Check if config has project rules or specs**:
   - Does `{cypilot_path}/config/rules/` contain any `.md` files?
   - Does `cypilot.py info` report any `specs`?
   - If rules or specs exist, load and follow them before generating.
   - If **neither** rules nor specs exist → offer auto-config (step 2).

2. **Offer auto-config** (no rules AND no specs):

   ALWAYS open and follow `{cypilot_path}/.core/requirements/auto-config.md` WHEN user accepts auto-config

   ```
   Brownfield project detected — existing code found but no project-specific rules configured.

   Auto-config can scan your project and generate rules that teach Cypilot your conventions.
   This produces:
   • Per-system rule files in config/rules/ (with TOC)
   • Heading-level WHEN rules in config/AGENTS.md
   • Doc navigation rules for existing project guides
   • System entries in config/artifacts.toml

   → Run auto-config now? [yes/no/skip]

   "yes"  → Run auto-config methodology (recommended for first-time setup)
   "no"   → Cancel generation
   "skip" → Continue without project rules (reduced quality)
   ```

3. **If user confirms "yes"**: Execute auto-config methodology (Phases 1→6), then return to generate
4. **If user says "skip"**: Proceed without project-specific rules
5. **If user says "no"**: Cancel

---

## Overview

Universal generation workflow. Handles three modes:
- **Artifact mode**: Uses template + checklist + example (PRD, DESIGN, DECOMPOSITION, ADR, SPEC)
- **Code mode**: Uses checklist only (implementation, fixes, refactoring)
- **Config mode**: Create/update config files (AGENTS.md, artifacts.toml, specs/)

After executing `execution-protocol.md`, you have: TARGET_TYPE, RULES, KIND, PATH, MODE, and resolved dependencies.

### Resolved Variables (from `execution-protocol.md` + info)

- `{cypilot_path}/config/` — config directory from `cypilot.py info` (contains `artifacts.toml`)
- `{ARTIFACTS_REGISTRY}` — `{cypilot_path}/config/artifacts.toml`
- `{KITS_PATH}` — kit package base directory resolved from registry (registry schema uses `kits`/`kit`)
- `{PATH}` — target artifact/code path for the current operation

**Examples**: Each artifact type has examples in `{KITS_PATH}/artifacts/{KIND}/examples/`. Reference these during Phase 1 (input collection) and Phase 2 (content generation) for style and quality guidance.

---

## Context Budget & Overflow Prevention (CRITICAL)

This workflow can require loading multiple long templates/checklists/examples and (optionally) reverse-engineering guidance. To prevent context overflow and accidental rule skipping:

- **Budget first**: Before loading large docs, estimate size (e.g., `wc -l`) and state a rough budget for what you will load this turn.
- **Load only what you will use**: Prefer the specific template sections and checklist categories needed for the current KIND; avoid loading entire registries/specs unless required.
- **Chunk reads**: Use `read_file` in ranges and summarize each chunk; do not keep raw full-text of multiple 500+ line documents in context at once.
- **Summarize-and-drop**: After extracting the needed criteria, keep a short checklist summary and drop the raw text from working memory.
- **Fail-safe**: If you cannot complete required steps within context, stop and output a checkpoint (chat-only) describing what is done and what remains. Do not proceed to writing files.

---

## ⛔ Agent Anti-Patterns (STRICT mode)

**Reference**: `{cypilot_path}/.core/requirements/agent-compliance.md` for full list.

**Critical anti-patterns for generation**:

| Anti-Pattern | What it looks like | Why it's wrong |
|--------------|-------------------|----------------|
| SKIP_TEMPLATE | Generate without loading template.md | Output structure will be incorrect |
| SKIP_EXAMPLE | Generate without referencing example.md | Output style/quality will be inconsistent |
| SKIP_CHECKLIST | Generate without self-review against checklist | Quality issues will pass to validation |
| PLACEHOLDER_SHIP | Write file with TODO/TBD markers | Incomplete artifact breaks downstream |
| NO_CONFIRMATION | Write files without user "yes" | User loses control over changes |
| SIMULATED_VALIDATION | Produce "✅ PASS" table without running `cpt validate` | Semantic review cannot catch structural errors (IDs, headings, cross-refs) that only the deterministic tool detects |

**Self-check before writing files** (MANDATORY in STRICT mode):

| Check | Verification | If FAIL |
|-------|--------------|---------|
| Loaded template.md? | Output structure matches template H2 sections | STOP — reload template |
| Referenced example.md? | Output tone/format consistent with example | STOP — review example |
| Self-reviewed against checklist? | All checklist items addressed | STOP — complete review |
| No placeholders? | Search for TODO, TBD, FIXME, [Description] returns 0 | STOP — fill all placeholders |
| User confirmed "yes"? | Explicit confirmation received | STOP — request confirmation |

**If any self-check fails → STOP and fix before proceeding**

**STRICT mode enforcement**: Agent MUST include self-check results in Phase 3 Summary output. Skipping self-check is anti-pattern `SKIP_CHECKLIST`.

---

## Rules Mode Behavior

| Aspect | STRICT (Cypilot rules) | RELAXED (no rules) |
|--------|-------------------|-------------------|
| Template | Required | User-provided or best effort |
| Checklist | Required for self-review | Optional |
| Example | Required for reference | Optional |
| Validation | Mandatory after write | Optional |
| Quality guarantee | High | No guarantee |

**RELAXED mode disclaimer**:
```
⚠️ Generated without Cypilot rules (reduced quality assurance)
```

---

## Phase 0: Ensure Dependencies

**After execution-protocol.md, you have**:
- `KITS_PATH` — path to loaded rules.md
- `TEMPLATE` — template content (from rules Dependencies)
- `CHECKLIST` — checklist content (from rules Dependencies)
- `EXAMPLE` — example content (from rules Dependencies)
- `REQUIREMENTS` — parsed requirements from rules

### Verify Rules Loaded

**If rules.md was loaded** (execution-protocol found artifact type):
- Dependencies already resolved from rules.md Dependencies section
- Proceed silently

**If rules.md NOT loaded** (manual mode):

| Dependency | Purpose | If missing |
|------------|---------|------------|
| **Checklist** | Validation criteria and quality expectations | Ask user to provide or specify path |
| **Template** | Required structure and sections | Ask user to provide or specify path |
| **Example** | Reference for content style and format | Ask user to provide or specify path |

### For Code (additional)

| Dependency | Purpose | If missing |
|------------|---------|------------|
| **Code checklist** | Baseline quality criteria for all code work | Load `{cypilot_path}/.core/requirements/code-checklist.md` |
| **Design artifact** | Requirements to implement | Ask user to specify source |

**MUST NOT proceed** to Phase 1 until all dependencies are available.

---

## Phase 0.5: Clarify Output & Context

### System Context (if using rules)

**If unclear from context, ask**:
```
Which system does this artifact/code belong to?
- {list systems from artifacts.toml}
- Create new system
```

**Store**: Selected system for registry placement.

### Output Destination

**Ask user** (if not specified):
```
Where should the result go?
- File (will be written to disk and registered)
- Chat only (preview, no file created)
- MCP tool / external system (specify)
```

**If file output + using rules**:
- Determine correct path based on system and kind
- Plan registry entry for `artifacts.toml`
- Check for existing file (UPDATE vs CREATE mode)

### Parent Artifact References

**If generating artifact**:
- Identify parent artifacts to reference
- Verify parent IDs exist
- Plan cross-references in new artifact

**If generating code**:
- Identify design artifact(s) being implemented
- Extract requirement IDs to trace
- Plan Cypilot markers for traceability (if FULL traceability)

### ID Naming

**For new artifacts with IDs**:
- Use project prefix from config
- Follow pattern: `cpt-{system}-{kind}-{slug}`
- Verify uniqueness with `cypilot list-ids`

---

## Phase 1: Collect Information

### For Artifacts (template-based)

1. Parse template H2 sections → questions
2. Load example for reference answers
3. Present batch questions with proposals

```markdown
## Inputs for {KIND}: {name}

### 1. {Section from template H2}

**Context**: {from template}
**Proposal**: {based on project context}
**Reference**: {from example}

### 2. {Next section}
...

**Reply**: "approve all" or edits per item
```

### For Code (checklist-based)

1. Parse related artifact (SPEC design, etc.)
2. Extract requirements to implement
3. Present implementation plan

```markdown
## Implementation Plan for {KIND}

**Source**: {related artifact path}

### Requirements to implement:
1. {requirement from design}
2. {requirement from design}
...

### Proposed approach:
{implementation strategy}

**Reply**: "approve" or modifications
```

### Input Collection Rules

**MUST**:
- Ask all required questions in a single batch by default
- Propose specific answers (not open-ended)
- Use project context for proposals
- Show reasoning clearly
- Allow modification of proposals
- Require final confirmation before proceeding

**MUST NOT**:
- Ask open-ended questions without proposals
- Skip questions
- Assume answers
- Proceed without final confirmation

### Confirmation

After approval:
```
Inputs confirmed. Proceeding to generation...
```

---

## Phase 2: Generate

**Follow Tasks section from loaded rules.md**:

### For Artifacts (rules.md Tasks)

Execute phases from rules.md:
- **Phase 1: Setup** — load template, checklist, example (already done)
- **Phase 2: Content Creation** — fill sections per rules guidance
- **Phase 3: IDs and Structure** — generate IDs per rules format
- **Phase 4: Quality Check** — self-review against checklist

Standard checks (subset of [Validation Criteria](#validation-criteria)):
- [ ] No placeholders (TODO, TBD, [Description])
- [ ] All IDs valid and unique
- [ ] All sections filled
- [ ] Parent artifacts referenced correctly

### For Code (rules.md Tasks)

Execute phases from codebase/rules.md:
- **Phase 1: Setup** — load spec design, checklist
- **Phase 2: Implementation** — implement with traceability markers
- **Phase 3: Traceability Format** — use correct traceability marker syntax
- **Phase 4: Quality Check** — verify traceability

Standard checks (subset of [Validation Criteria](#validation-criteria)):
- [ ] Follows conventions
- [ ] Implements all requirements
- [ ] Has tests (if required)
- [ ] Traceability markers present (if to_code="true")

### Content Rules

**MUST**:
- Follow content requirements exactly
- Use imperative language
- Wrap IDs in backticks
- Reference types from domain model (no redefinition)
- Use Cypilot DSL (CDSL) for behavioral sections (if applicable)

**MUST NOT**:
- Leave placeholders
- Skip required content
- Redefine parent types
- Use code examples in DESIGN.md

### Markdown Quality

**MUST**:
- Use empty lines between headings, paragraphs, lists
- Use fenced code blocks with language tags
- End metadata lines with two spaces for line breaks (or use lists)

---

## Phase 2.5: Checkpoint (for long artifacts)

**When to checkpoint**: Artifacts with >10 sections OR generation taking multiple conversation turns.

**After Phase 2 completion, save checkpoint (chat-only by default)**:
```markdown
### Generation Checkpoint

**Workflow**: /cypilot-generate {KIND}
**Phase**: 2 complete, ready for Phase 3
**Inputs collected**:
- {section}: {value summary}
- ...

**Content generated**: {line count} lines
**Pending**: Summary → Confirmation → Write → Analyze

Resume: Re-read this checkpoint, verify no file changes, continue to Phase 3.
```

**Checkpoint write policy**:
- Default: checkpoint is output to chat only (no files created)
- Only write a checkpoint file if the user explicitly requests/approves it

**On resume after compaction**:
1. Re-read target file (if exists) to verify no external changes
2. Re-load rules dependencies
3. Continue from saved phase

---

## Phase 3: Summary

```markdown
## Summary

**Target**: {TARGET_TYPE}
**Kind**: {KIND}
**Name**: {name}
**Path**: {path}
**Mode**: {MODE}

### Content preview:
{brief overview of what will be created/changed}

### Files to write:
- `{path}`: {description}
{additional files if any}

### Artifacts registry:
- `{cypilot_path}/config/artifacts.toml`: {entry additions/updates, if any}

**Proceed?** [yes/no/modify]
```

**User responses**:
- **yes**: Create files and proceed to validation
- **no**: Cancel operation
- **modify**: Ask which question to revisit, iterate (max 3 iterations; after 3, require explicit "continue iterating" or restart workflow)

---

## Phase 4: Write

**Only after confirmation**:

1. Update `{cypilot_path}/config/artifacts.toml` if new artifact path introduced
2. Create directories if needed
3. Write file(s)
4. Verify content

Output:
```
✓ Written: {path}
```

**MUST NOT**:
- Create files before confirmation
- Create incomplete files
- Create placeholder files

---

## Phase 5: Analyze

**Automatic**: Run validation after generation (do not list in Next Steps).

> **⛔ CRITICAL**: The agent's own checklist walkthrough is **NOT** a substitute for `cpt validate`. A manual "✅ PASS" table in chat is semantic review, not deterministic validation — these are **separate steps**. See anti-pattern `SIMULATED_VALIDATION`.

### Step 1: Deterministic Validation (tool-based)

**MUST** run `cpt validate` as an actual terminal command:

For artifacts:
```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py validate --root {PROJECT_ROOT} --cypilot-root {cypilot_path}
```

For code:
```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py validate --root {PROJECT_ROOT} --cypilot-root {cypilot_path}
```

**Rules**:

1. **Tool-first**: The agent MUST execute the validator command BEFORE any semantic review. No exceptions.
2. **Output evidence**: The agent MUST include the validator's exit code and `status`/`error_count`/`warning_count` from the JSON output in its response so the user can verify the tool was actually invoked.
3. **Gate**: The agent MUST NOT proceed to Step 2 or Phase 6 until `cpt validate` returns `"status": "PASS"`. If it returns FAIL, fix the errors and re-run until PASS.
4. **Anti-pattern**: The agent MUST NOT produce a validation summary without first showing the actual output of `cpt validate`. Doing so is `SIMULATED_VALIDATION`.

**If FAIL** → fix errors in the artifact → re-run `cpt validate` → repeat until PASS.

**If PASS** → proceed to Step 2.

### Step 2: Semantic Review (LLM-based)

**Only after `cpt validate` returns PASS**:

- Self-review generated content against checklist.md
- Verify no placeholders (TODO, TBD, FIXME)
- Verify cross-references are meaningful (not just structurally valid)
- Verify content quality and completeness

### Step 3: Report Both Results

```markdown
## Validation Results

### Deterministic (`cpt validate`)
- Exit code: {0|2}
- Status: {PASS|FAIL}
- Errors: {N}, Warnings: {N}

### Semantic Review
- Checklist coverage: {summary}
- Content quality: {summary}
- Issues found: {list or "none"}
```

→ If both pass: proceed to Phase 6
→ If semantic issues found: fix and re-validate (return to Step 1)

---

## Phase 6: Offer Next Steps

**Read from rules.md** → `## Next Steps` section

Present applicable options to user:
```
What would you like to do next?
1. {option from rules Next Steps}
2. {option from rules Next Steps}
3. Other
```

---

## Error Handling

### Tool Failures

**If `cypilot.py` script fails**:
```
⚠️ Tool error: {error message}
→ Check Python environment and dependencies
→ Verify cypilot is correctly configured
→ Run /cypilot-adapter to refresh
```
**STOP** — do not continue with incomplete state.

### User Abandonment

**If user does not respond or abandons mid-workflow**:
- Do not auto-proceed with assumptions
- State can be resumed by re-running the workflow command
- No cleanup required (no partial files created until Phase 4)

### Validation Failure Loop

**If validation fails repeatedly (3+ times)**:
```
⚠️ Validation failing repeatedly. Options:
1. Review checklist requirements manually
2. Simplify artifact scope
3. Skip validation (RELAXED mode only)
```

---

## State Summary

| State | TARGET_TYPE | Has Template | Has Checklist | Has Example |
|-------|-------------|--------------|---------------|-------------|
| Generating artifact | artifact | ✓ | ✓ | ✓ |
| Generating code | code | ✗ | ✓ | ✗ |

---

## Validation Criteria

- [ ] {cypilot_path}/.core/requirements/execution-protocol.md executed
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
