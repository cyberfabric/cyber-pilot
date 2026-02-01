---
fdd: true
type: workflow
name: fdd-validate
description: Validate FDD artifacts against templates or code against design requirements with traceability verification
version: 1.0
purpose: Universal workflow for validating any FDD artifact or code
---

# Validate

**Type**: Validation

ALWAYS open and follow `../requirements/execution-protocol.md` FIRST

OPEN and follow `../requirements/prompt-engineering.md` WHEN user requests validation of:
- System prompts, agent prompts, or LLM prompts
- Agent instructions or agent guidelines
- Skills, workflows, or methodologies
- AGENTS.md or navigation rules
- Any document containing instructions for AI agents
- User explicitly mentions "prompt engineering review" or "instruction quality"

---

## ⚠️ Maximum Attention to Detail

**MUST** perform validation checking **ALL** applicable criteria from the loaded checklist:

- ✅ Check **EVERY SINGLE** validation criterion
- ✅ Verify **EACH ITEM** individually, not in groups
- ✅ Read **COMPLETE** artifact from start to end
- ✅ Validate **EVERY** ID format, reference, section
- ✅ Check for **ALL** placeholders, empty sections, missing content
- ✅ Cross-reference **EVERY** actor/capability/requirement ID
- ✅ Report **EVERY** issue found

**MUST NOT**:
- ❌ Skip any validation checks
- ❌ Assume sections are correct without verifying
- ❌ Give benefit of doubt - verify everything

**One missed issue = INVALID validation**

---

## ⛔ Agent Anti-Patterns (STRICT mode)

**Reference**: `../requirements/agent-compliance.md` for full list.

**Critical anti-patterns for validation**:

| Anti-Pattern | What it looks like | Why it's wrong |
|--------------|-------------------|----------------|
| SKIP_SEMANTIC | Deterministic PASS → report overall PASS | Deterministic checks structure only, not content quality |
| MEMORY_VALIDATION | "I already read it" without Read tool | Context may be stale, compacted, or incomplete |
| ASSUMED_NA | "Security not applicable for this project" | Document must have explicit N/A statement, agent can't decide |
| BULK_PASS | "All checklist items pass" | No evidence = no proof of actual verification |

**Self-check before outputting validation**:
- Am I reporting PASS without semantic review? → AP-001 SKIP_SEMANTIC
- Did I use Read tool for the target artifact THIS turn? → AP-002 MEMORY_VALIDATION
- Am I marking categories N/A without document quotes? → AP-003 ASSUMED_NA
- Am I claiming "all pass" without per-category evidence? → AP-004 BULK_PASS

**If any self-check fails → STOP and restart with compliance**

---

## Overview

Universal validation workflow. Handles multiple modes:
- **Full mode** (default): Deterministic gate → Semantic review
- **Semantic mode**: Semantic-only validation (skip deterministic gate)
- **Artifact mode**: Validates against template + checklist
- **Code mode**: Validates against checklist + design requirements

### Command Variants

| Command | Mode | Description |
|---------|------|-------------|
| `/fdd-validate` | Full | Deterministic gate → Semantic review |
| `/fdd-validate semantic` | Semantic only | Skip deterministic, checklist-based validation only |
| `/fdd-validate --artifact <path>` | Full | Validate specific artifact |
| `/fdd-validate semantic --artifact <path>` | Semantic only | Semantic validation for specific artifact |
| `/fdd-validate prompt <path>` | Prompt review | Prompt engineering methodology (9-layer analysis) |

**Prompt review triggers** (auto-detected from context):
- "validate this system prompt"
- "review agent instructions"
- "check this workflow/skill"
- "prompt engineering review"

After executing `execution-protocol.md`, you have: TARGET_TYPE, RULES, KIND, PATH, and resolved dependencies.

---

## Mode Detection

**Check invocation**:

- If user invoked `/fdd-validate semantic` or `/fdd validate semantic` → Set `SEMANTIC_ONLY=true`
- If user invoked `/fdd-validate prompt` or context indicates prompt/instruction review → Set `PROMPT_REVIEW=true`
- Otherwise → Set `SEMANTIC_ONLY=false`, `PROMPT_REVIEW=false` (full validation)

**When `SEMANTIC_ONLY=true`**:
- Skip Phase 2 (Deterministic Gate)
- Go directly to Phase 3 (Semantic Review)
- Semantic review is MANDATORY regardless of STRICT/RELAXED mode

**When `PROMPT_REVIEW=true`**:
- Open and follow `../requirements/prompt-engineering.md`
- Execute 9-layer prompt engineering analysis
- Skip standard FDD validation (not applicable to prompts)
- Output using prompt-engineering.md format
- Traceability checks: N/A (prompts don't have code markers)
- Registry checks: N/A (prompts may not be in artifacts.json)

---

## Phase 0: Ensure Dependencies

**After execution-protocol.md, you have**:
- `RULES_PATH` — path to loaded rules.md
- `TEMPLATE` — template content (from rules Dependencies)
- `CHECKLIST` — checklist content (from rules Dependencies)
- `EXAMPLE` — example content (from rules Dependencies)
- `REQUIREMENTS` — parsed requirements from rules
- `VALIDATION_CHECKS` — validation checks from rules.md Validation section

### Verify Rules Loaded

**If rules.md was loaded** (execution-protocol found artifact type):
- Dependencies already resolved from rules.md Dependencies section
- Validation checks defined in rules.md Validation section
- Proceed silently

**If rules.md NOT loaded** (manual mode):

| Dependency | Purpose | If missing |
|------------|---------|------------|
| **Checklist** | Validation criteria to check | Ask user to provide or specify path |
| **Template** | Expected structure and sections | Ask user to provide or specify path |
| **Example** | Reference for expected content quality | Ask user to provide or specify path |

### For Code (additional)

| Dependency | Purpose | If missing |
|------------|---------|------------|
| **Design artifact** | Requirements that should be implemented | Ask user to specify source |

**MUST NOT proceed** to Phase 1 until all dependencies are available.

---

## Phase 0.5: Clarify Validation Scope

### Scope Determination

**Ask user if unclear**:
```
What is the validation scope?
- Full validation (entire artifact/codebase)
- Partial validation (specific sections/IDs)
- Quick check (structure only, skip semantic)
```

### Traceability Mode

**Check artifact's traceability setting in artifacts.json**:
- `FULL` → Validate code markers, cross-reference IDs in codebase
- `DOCS-ONLY` → Skip codebase traceability checks

**If FULL traceability**:
- Identify codebase directories from artifacts.json
- Plan to check for `@fdd-*` markers
- Plan to verify all IDs have code implementations

### Registry Consistency

**Verify artifact is registered**:
- Check if target path exists in artifacts.json
- Verify kind matches registered kind
- Verify system assignment is correct

**If not registered**: Warn user, suggest registration.

### Cross-Reference Scope

**Identify related artifacts**:
- Parent artifacts (what this references)
- Child artifacts (what references this)
- Code directories (if FULL traceability)

**Plan validation of**:
- All outgoing references exist
- All incoming references are valid
- No orphaned IDs

---

## Phase 1: File Existence Check

**Check**:
1. Target exists at `{PATH}`
2. Target is not empty
3. Target is readable

**If fails**:
```
✗ Target not found: {PATH}
→ Run /fdd-generate {TARGET_TYPE} {KIND} to create
```
STOP validation.

---

## Phase 2: Deterministic Gate

**If `SEMANTIC_ONLY=true`**: Skip this phase, go to Phase 3.

**MUST run first** (when not semantic-only) - this is the authoritative PASS/FAIL.

### For Artifacts

```bash
python3 {FDD}/skills/fdd/scripts/fdd.py validate --artifact {PATH}
```

### For Code

```bash
python3 {FDD}/skills/fdd/scripts/fdd.py validate --code {PATH} --design {design-path}
```

### Evaluate

**If FAIL**:
```
═══════════════════════════════════════════════
Validation: {TARGET_TYPE}
───────────────────────────────────────────────
Status: FAIL
───────────────────────────────────────────────
Blocking issues:
{list from validator}
═══════════════════════════════════════════════

→ Fix issues and re-run validation
```
**STOP** - do not proceed to semantic review.

**If PASS**: Continue to conditional semantic review.

---

## Phase 3: Semantic Review (Conditional)

**Run if**:
- Deterministic gate PASS, OR
- `SEMANTIC_ONLY=true` (skip deterministic gate)

### Mode-Dependent Behavior

| Invocation | Rules Mode | Semantic Review | Evidence Required |
|------------|------------|-----------------|-------------------|
| `/fdd-validate semantic` | Any | MANDATORY | Yes — per `agent-compliance.md` |
| `/fdd-validate` | **STRICT** | MANDATORY | Yes — per `agent-compliance.md` |
| `/fdd-validate` | **RELAXED** | Optional | No — best effort |

**If STRICT mode**:
- Semantic review is MANDATORY, not optional
- Agent MUST follow `../requirements/agent-compliance.md`
- Agent MUST provide evidence for each checklist category
- Agent MUST NOT skip categories or report bulk "PASS"
- Failure to complete semantic review → validation INVALID

**If semantic review cannot be completed** (context limits, missing info, interruption):
1. Document which categories were checked with evidence
2. Mark incomplete categories with reason (e.g., "INCOMPLETE: context limit reached")
3. Output as `PARTIAL` — do NOT report overall PASS/FAIL
4. Include checkpoint guidance: "Resume with `/fdd-validate semantic` after addressing blockers"

**If RELAXED mode**:
- Semantic review is optional
- Agent proceeds with best effort
- Output includes disclaimer: `⚠️ Semantic review skipped (RELAXED mode)`

### Semantic Review Content (STRICT mode)

**Follow Validation section from loaded rules.md**:

### For Artifacts (rules.md Validation)

Execute validation phases from rules.md:
- **Phase 1: Structural Validation** — already done by deterministic gate
- **Phase 2: Semantic Validation** — checklist-based, from rules.md

Use checklist from Phase 0 dependencies.
Load adapter specs: `{adapter-dir}/AGENTS.md` → follow MANDATORY specs

Check (from rules.md + standard):
- [ ] Content quality per checklist
- [ ] Cross-references to parent artifacts valid
- [ ] Naming conventions followed
- [ ] No placeholder-like content
- [ ] Adapter specs compliance (paths, patterns, conventions)
- [ ] Versioning requirements met (from rules)
- [ ] Traceability requirements met (from rules)

### For Code (rules.md Validation)

Execute validation phases from codebase/rules.md:
- **Phase 1: Traceability Validation** — check code markers
- **Phase 2: Quality Validation** — checklist-based

Use checklist from Phase 0 dependencies.
Load design: related artifact(s)

Check (from rules.md + standard):
- [ ] All design requirements implemented
- [ ] Code follows conventions
- [ ] Tests cover requirements
- [ ] FDD markers present where required (to_code="true" IDs)
- [ ] Implemented items marked `[x]` in FEATURE design

### Completeness Checks

- [ ] No placeholder markers (TODO, TBD, [Description])
- [ ] No empty sections
- [ ] All IDs follow format from requirements
- [ ] All IDs unique
- [ ] All required fields present

### Coverage Checks

- [ ] All parent requirements addressed
- [ ] All referenced IDs exist in parent artifacts
- [ ] All actors/capabilities from parent covered
- [ ] No orphaned references

### Traceability Checks (if FULL traceability)

- [ ] All requirement IDs have code markers
- [ ] All flow IDs have code markers
- [ ] All algorithm IDs have code markers
- [ ] All test IDs have test implementations
- [ ] Code markers use correct format (`@fdd-{kind}:{id}:ph-{N}`)
- [ ] No stale markers (ID no longer in design)

### ID Uniqueness & Format

- [ ] No duplicate IDs within artifact
- [ ] No duplicate IDs across system (use `fdd list-ids`)
- [ ] All IDs follow naming convention
- [ ] All IDs have correct prefix for project

### Registry Consistency

- [ ] Artifact is registered in artifacts.json
- [ ] Kind matches registered kind
- [ ] System assignment is correct
- [ ] Path is correct

### Checkpoint for Large Artifacts

**For artifacts >500 lines or validation taking multiple turns**:
- After completing each checklist category group, note progress in output
- If context runs low, save checkpoint before continuing:
  - List completed categories with status
  - List remaining categories
  - Note current position in artifact
- On resume: re-read artifact, verify unchanged, continue from checkpoint

### Collect Recommendations

Categorize by priority:
- **High**: Should fix before proceeding
- **Medium**: Should fix eventually
- **Low**: Nice to have

---

## Phase 4: Output

Print to chat (NO files created):

### Full Validation Output (default)

```
═══════════════════════════════════════════════
Validation: {TARGET_TYPE}
───────────────────────────────────────────────
kind:   {KIND}
name:   {name}
path:   {PATH}
───────────────────────────────────────────────
Status: PASS
═══════════════════════════════════════════════

### Deterministic Gate
✓ PASS

### Recommendations

**High priority**:
- {issue with location}

**Medium priority**:
- {issue with location}

**Low priority**:
- {issue with location}

### Coverage (if applicable)
- Requirements: {X}/{Y} implemented
- Tests: {X}/{Y} covered

───────────────────────────────────────────────
═══════════════════════════════════════════════
```

### Semantic-Only Validation Output (`/fdd-validate semantic`)

```
═══════════════════════════════════════════════
Semantic Validation: {TARGET_TYPE}
───────────────────────────────────────────────
kind:   {KIND}
name:   {name}
path:   {PATH}
───────────────────────────────────────────────
Mode: SEMANTIC ONLY (deterministic gate skipped)
Status: PASS/FAIL
═══════════════════════════════════════════════

### Checklist Review

| Category | Status | Evidence |
|----------|--------|----------|
| {category} | PASS/FAIL/N/A | {line refs, quotes} |

### Issues Found

**High priority**:
- {issue with location}

**Medium priority**:
- {issue with location}

### Coverage
- Checklist items: {X}/{Y} passed
- N/A categories: {list with reasoning}

───────────────────────────────────────────────
═══════════════════════════════════════════════
```

---

## Phase 5: Offer Next Steps

**Read from rules.md** → `## Next Steps` section

Present applicable options to user based on validation result:

**If PASS**:
```
What would you like to do next?
1. {option from rules Next Steps for success}
2. {option from rules Next Steps}
3. Other
```

**If FAIL**:
```
Fix the issues above, then:
1. Re-run validation
2. {option from rules Next Steps for issues}
3. Other
```

---

## State Summary

| State | TARGET_TYPE | Uses Template | Uses Checklist | Uses Design |
|-------|-------------|---------------|----------------|-------------|
| Validating artifact | artifact | ✓ | ✓ | parent only |
| Validating code | code | ✗ | ✓ | ✓ |

---

## Key Principles

### Deterministic Gate Is Authoritative

- `fdd validate` PASS/FAIL is the official result
- Semantic review only adds recommendations
- Never override deterministic result

### No Files Created

- All output to chat
- Never create VALIDATION_REPORT.md
- Keep validation stateless

### Fail Fast

- If deterministic gate fails → STOP
- Don't waste time on semantic review
- Report issues immediately

---

## Agent Self-Test (STRICT mode — AFTER completing work)

**CRITICAL**: Answer these questions AFTER doing the validation work, not before.
**CRITICAL**: Include answers with evidence in your output.

### Self-Test Questions

1. ⚠️ Did I read execution-protocol.md before starting?
   → Evidence: Show that you loaded rules and dependencies

2. ⚠️ Did I use Read tool to read the ENTIRE artifact THIS turn?
   → Evidence: `Read {path}: {N} lines`

3. ⚠️ Did I check EVERY checklist category individually?
   → Evidence: Category breakdown table with per-category status

4. ⚠️ Did I provide evidence (quotes, line numbers) for each PASS/FAIL/N/A?
   → Evidence: Evidence column in category table

5. ⚠️ For N/A claims, did I quote explicit "Not applicable" statements from document?
   → Evidence: Quotes showing document author marked it N/A

6. ⚠️ Am I reporting based on actual file content, not memory/summary?
   → Evidence: Fresh Read tool call visible in this conversation turn

### Self-Test Output Format (include in validation report)

```markdown
### Agent Self-Test Results

| Question | Answer | Evidence |
|----------|--------|----------|
| Read execution-protocol? | YES | Loaded fdd-sdlc rules, checklist.md |
| Read artifact via Read tool? | YES | Read DESIGN.md: 742 lines |
| Checked every category? | YES | 12 categories in table above |
| Evidence for each status? | YES | Quotes included per category |
| N/A has document quotes? | YES | Lines 698, 712, 725 |
| Based on fresh read? | YES | Read tool called this turn |
```

**If ANY answer is NO or lacks evidence → Validation is INVALID, must restart**

### RELAXED Mode

In RELAXED mode, self-test is advisory only. Include disclaimer:
```
⚠️ Self-test skipped (RELAXED mode — no FDD rules)
```

---

## Validation Criteria

- [ ] ../requirements/execution-protocol.md executed
- [ ] Dependencies loaded (checklist, template, example)
- [ ] Validation scope clarified
- [ ] Traceability mode determined
- [ ] Registry consistency verified
- [ ] Cross-reference scope identified
- [ ] Target exists and readable
- [ ] Deterministic gate executed
- [ ] ID uniqueness verified (within artifact and across system)
- [ ] Cross-references verified (outgoing and incoming)
- [ ] Traceability markers verified (if FULL traceability)
- [ ] Result correctly reported (PASS/FAIL)
- [ ] Recommendations provided (if PASS)
- [ ] Output to chat only
- [ ] Next steps suggested
