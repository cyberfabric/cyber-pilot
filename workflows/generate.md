---
fdd: true
type: workflow
name: Generate
version: 1.0
purpose: Universal workflow for creating or updating any FDD artifact or code
---

# Generate

**Type**: Operation

ALWAYS open and follow `../requirements/execution-protocol.md` FIRST

---

## Overview

Universal generation workflow. Handles two modes:
- **Artifact mode**: Uses template + checklist + example
- **Code mode**: Uses checklist only

After executing `execution-protocol.md`, you have: TARGET_TYPE, RULES, KIND, PATH, MODE, and resolved dependencies.

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

**Self-check before writing files**:
- Did I load and follow template.md? → Check output structure matches
- Did I reference example.md for style? → Check output tone/format
- Did I self-review against checklist? → Check quality before output
- Are there any placeholders? → Search for TODO, TBD, FIXME, [Description]
- Did user confirm with "yes"? → Check confirmation received

**If any self-check fails → STOP and fix before proceeding**

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

Standard checks:
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

Standard checks:
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
- **modify**: Ask which question to revisit, iterate

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
