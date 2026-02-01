---
fdd: true
type: workflow
name: fdd-generate
description: Create/update FDD artifacts (PRD, DESIGN, FEATURES, ADR, Feature) or implement code from design with traceability markers
version: 1.0
purpose: Universal workflow for creating or updating any FDD artifact or code
---

# Generate

**Type**: Operation

ALWAYS open and follow `../requirements/execution-protocol.md` FIRST

ALWAYS open and follow `../requirements/reverse-engineering.md` WHEN user requests to analyze codebase, search in code, search in project documentation, or generate artifacts or code based on existing project structure

For context compaction recovery during multi-phase workflows, follow `../requirements/execution-protocol.md` Section "Compaction Recovery".

---

## Table of Contents

- [Reverse Engineering Prerequisite](#reverse-engineering-prerequisite)
- [Overview](#overview)
- [Agent Anti-Patterns](#-agent-anti-patterns-strict-mode)
- [Rules Mode Behavior](#rules-mode-behavior)
- [Phase 0: Ensure Dependencies](#phase-0-ensure-dependencies)
- [Phase 0.5: Clarify Output & Context](#phase-05-clarify-output--context)
- [Phase 1: Collect Information](#phase-1-collect-information)
- [Phase 2: Generate](#phase-2-generate)
- [Phase 2.5: Checkpoint](#phase-25-checkpoint-for-long-artifacts)
- [Phase 3: Summary](#phase-3-summary)
- [Phase 4: Write](#phase-4-write)
- [Phase 5: Validate](#phase-5-validate)
- [Phase 6: Offer Next Steps](#phase-6-offer-next-steps)
- [Error Handling](#error-handling)
- [State Summary](#state-summary)
- [Validation Criteria](#validation-criteria)

---

## Reverse Engineering Prerequisite

**When trigger conditions above are met**, before proceeding with generation:

1. **Check if adapter has project analysis**:
   - Does `{adapter-dir}/specs/` contain populated spec files?
   - Is there a recent project scan summary?

2. **If no project analysis exists**:
   ```
   To generate quality artifacts/code based on the existing project,
   I recommend running adapter in reverse engineering mode first:

   /fdd-adapter --rescan

   This will:
   - Analyze codebase structure (Layers 1-3)
   - Detect tech stack and patterns
   - Populate adapter specs

   After scan completes, we can continue with your request.

   Proceed with adapter scan? [yes/skip]
   ```

3. **If user confirms**: Run adapter workflow Phase 1, then return to original task
4. **If user skips**: Proceed with best-effort generation using `reverse-engineering.md` inline

---

## Overview

Universal generation workflow. Handles two modes:
- **Artifact mode**: Uses template + checklist + example
- **Code mode**: Uses checklist only

After executing `execution-protocol.md`, you have: TARGET_TYPE, RULES, KIND, PATH, MODE, and resolved dependencies.

**Examples**: Each artifact type has examples in `{rules-path}/artifacts/{KIND}/examples/`. Reference these during Phase 1 (input collection) and Phase 2 (content generation) for style and quality guidance.

---

## ⛔ Agent Anti-Patterns (STRICT mode)

**Reference**: `../requirements/agent-compliance.md` for full list.

**Critical anti-patterns for generation**:

| Anti-Pattern | What it looks like | Why it's wrong |
|--------------|-------------------|----------------|
| SKIP_TEMPLATE | Generate without loading template.md | Output structure will be incorrect |
| SKIP_EXAMPLE | Generate without referencing example.md | Output style/quality will be inconsistent |
| SKIP_CHECKLIST | Generate without self-review against checklist | Quality issues will pass to validation |
| PLACEHOLDER_SHIP | Write file with TODO/TBD markers | Incomplete artifact breaks downstream |
| NO_CONFIRMATION | Write files without user "yes" | User loses control over changes |

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

| Aspect | STRICT (FDD rules) | RELAXED (no rules) |
|--------|-------------------|-------------------|
| Template | Required | User-provided or best effort |
| Checklist | Required for self-review | Optional |
| Example | Required for reference | Optional |
| Validation | Mandatory after write | Optional |
| Quality guarantee | High | No guarantee |

**RELAXED mode disclaimer**:
```
⚠️ Generated without FDD rules (reduced quality assurance)
```

---

## Phase 0: Ensure Dependencies

**After execution-protocol.md, you have**:
- `RULES_PATH` — path to loaded rules.md
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
| **Design artifact** | Requirements to implement | Ask user to specify source |

**MUST NOT proceed** to Phase 1 until all dependencies are available.

---

## Phase 0.5: Clarify Output & Context

### System Context (if using rules)

**If unclear from context, ask**:
```
Which system does this artifact/code belong to?
- {list systems from artifacts.json}
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
- Plan registry entry for `artifacts.json`
- Check for existing file (UPDATE vs CREATE mode)

### Parent Artifact References

**If generating artifact**:
- Identify parent artifacts to reference
- Verify parent IDs exist
- Plan cross-references in new artifact

**If generating code**:
- Identify design artifact(s) being implemented
- Extract requirement IDs to trace
- Plan FDD markers for traceability (if FULL traceability)

### ID Naming

**For new artifacts with IDs**:
- Use project prefix from adapter
- Follow pattern: `fdd-{project}-{kind}-{slug}`
- Verify uniqueness with `fdd list-ids`

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

1. Parse related artifact (FEATURE design, etc.)
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
- **Phase 1: Setup** — load feature design, checklist
- **Phase 2: Implementation** — implement with FDD markers
- **Phase 3: Marker Format** — use correct marker syntax
- **Phase 4: Quality Check** — verify traceability

Standard checks (subset of [Validation Criteria](#validation-criteria)):
- [ ] Follows conventions
- [ ] Implements all requirements
- [ ] Has tests (if required)
- [ ] FDD markers present (if to_code="true")

### Content Rules

**MUST**:
- Follow content requirements exactly
- Use imperative language
- Wrap IDs in backticks
- Reference types from domain model (no redefinition)
- Use FDL for behavioral sections (if applicable)

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

**After Phase 2 completion, save checkpoint**:
```markdown
### Generation Checkpoint

**Workflow**: /fdd-generate {KIND}
**Phase**: 2 complete, ready for Phase 3
**Inputs collected**:
- {section}: {value summary}
- ...

**Content generated**: {line count} lines
**Pending**: Summary → Confirmation → Write → Validate

Resume: Re-read this checkpoint, verify no file changes, continue to Phase 3.
```

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
- `{adapter-dir}/artifacts.json`: {entry additions/updates, if any}

**Proceed?** [yes/no/modify]
```

**User responses**:
- **yes**: Create files and proceed to validation
- **no**: Cancel operation
- **modify**: Ask which question to revisit, iterate (max 3 iterations; after 3, require explicit "continue iterating" or restart workflow)

---

## Phase 4: Write

**Only after confirmation**:

1. Update `{adapter-dir}/artifacts.json` if new artifact path introduced
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

## Phase 5: Validate

**Automatic**: Run validation after generation (do not list in Next Steps):
```
/fdd-validate {TARGET_TYPE} {KIND}
```

**If PASS**:
```
✓ Validation: PASS
```
→ Read `Next Steps` section from loaded rules.md
→ Offer options to user based on current state

**If FAIL**:
```
✗ Validation: FAIL
{issues}
→ Fix issues and re-run validation
```

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

**If `fdd.py` script fails**:
```
⚠️ Tool error: {error message}
→ Check Python environment and dependencies
→ Verify adapter is correctly configured
→ Run /fdd-adapter --rescan to refresh
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

- [ ] ../requirements/execution-protocol.md executed
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
