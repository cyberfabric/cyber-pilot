---
cypilot: true
type: workflow
name: cypilot-analyze
description: Analyze Cypilot artifacts against templates or code against design requirements with traceability verification (tool invocation is validate-only)
version: 1.0
purpose: Universal workflow for analysing any Cypilot artifact or code
---

# Analyze

ALWAYS open and follow `{cypilot_path}/skills/cypilot/SKILL.md` FIRST WHEN {cypilot_mode} is `off`

**Type**: Analysis

ALWAYS open and follow `{cypilot_path}/requirements/execution-protocol.md` FIRST

ALWAYS open and follow `{cypilot_path}/requirements/code-checklist.md` WHEN user requests analysis of code, codebase changes, or implementation behavior (Code mode)

ALWAYS open and follow `{cypilot_path}/requirements/consistency-checklist.md` WHEN user requests analysis of documentation/artifact consistency, contradiction detection, or cross-document alignment (Consistency mode)

OPEN and follow `{cypilot_path}/requirements/prompt-engineering.md` WHEN user requests analysis of:
- System prompts, agent prompts, or LLM prompts
- Agent instructions or agent guidelines
- Skills, workflows, or methodologies
- AGENTS.md or navigation rules
- Any document containing instructions for AI agents
- User explicitly mentions "prompt engineering review" or "instruction quality"

---

## ⚠️ Maximum Attention to Detail

**MUST** perform analysis checking **ALL** applicable criteria from the loaded checklist:

- ✅ Check **EVERY SINGLE** applicable criterion
- ✅ Verify **EACH ITEM** individually, not in groups
- ✅ Read **COMPLETE** artifact from start to end
- ✅ Validate **EVERY** ID format, reference, section
- ✅ Check for **ALL** placeholders, empty sections, missing content
- ✅ Cross-reference **EVERY** actor/capability/requirement ID
- ✅ Report **EVERY** issue found

**MUST NOT**:
- ❌ Skip any checks
- ❌ Assume sections are correct without verifying
- ❌ Give benefit of doubt - verify everything

**One missed issue = INVALID analysis**

---

## ⛔ Agent Anti-Patterns (STRICT mode)

**Reference**: `{cypilot_path}/requirements/agent-compliance.md` for full list.

**Critical anti-patterns for analysis**:

| Anti-Pattern | What it looks like | Why it's wrong |
|--------------|-------------------|----------------|
| SKIP_SEMANTIC | Deterministic PASS → report overall PASS | Deterministic checks structure only, not content quality |
| MEMORY_VALIDATION | "I already read it" without Read tool | Context may be stale, compacted, or incomplete |
| ASSUMED_NA | "Security not applicable for this project" | Document must have explicit N/A statement, agent can't decide |
| BULK_PASS | "All checklist items pass" | No evidence = no proof of actual verification |

**Self-check before outputting analysis**:
- Am I reporting PASS without semantic review? → AP-001 SKIP_SEMANTIC
- Did I use Read tool for the target artifact THIS turn? → AP-002 MEMORY_VALIDATION
- Am I marking categories N/A without document quotes? → AP-003 ASSUMED_NA
- Am I claiming "all pass" without per-category evidence? → AP-004 BULK_PASS

**If any self-check fails → STOP and restart with compliance**

---

## Overview

Universal analysis workflow. Handles multiple modes:
- **Full mode** (default): Deterministic gate → Semantic review
- **Semantic mode**: Semantic-only analysis (skip deterministic gate)
- **Artifact mode**: Analyzes against template + checklist
- **Code mode**: Analyzes against checklist + design requirements

### Command Variants

| Command | Mode | Description |
|---------|------|-------------|
| `/cypilot-analyze` | Full | Deterministic gate → Semantic review |
| `/cypilot-analyze semantic` | Semantic only | Skip deterministic, checklist-based semantic analysis only |
| `/cypilot-analyze --artifact <path>` | Full | Analyze specific artifact |
| `/cypilot-analyze semantic --artifact <path>` | Semantic only | Semantic analysis for specific artifact |
| `/cypilot-analyze prompt <path>` | Prompt review | Prompt engineering methodology (9-layer analysis) |

**Prompt review triggers** (auto-detected from context):
- "analyze this system prompt"
- "review agent instructions"
- "check this workflow/skill"
- "prompt engineering review"

After executing `execution-protocol.md`, you have: TARGET_TYPE, RULES, KIND, PATH, and resolved dependencies.

---

## Context Budget & Overflow Prevention (CRITICAL)

This workflow can require loading multiple long checklists/specs. To prevent context overflow and "missed checks" failures:

- **Budget first**: Before loading large docs, estimate size (e.g., `wc -l`) and state a rough budget for what you will load this turn.
- **Load only what you will use**: Prefer rules.md "Validation" (analysis checks) and the specific checklist categories needed; avoid loading entire registries/specs unless required.
- **Chunk reads**: Use `read_file` in ranges and summarize each chunk; do not keep raw full-text of multiple 500+ line documents in context at once.
- **Summarize-and-drop**: After extracting the needed criteria, keep a short checklist summary and drop the raw text from working memory.
- **Fail-safe**: If you cannot complete the required checks within context, output `PARTIAL` with a checkpoint (what was checked, what remains, where to resume). Do not claim overall PASS.

---

## Mode Detection

**Check invocation**:

- If user invoked `/cypilot-analyze semantic` or `cypilot analyze semantic` → Set `SEMANTIC_ONLY=true`
- If user invoked `/cypilot-analyze prompt` or context indicates prompt/instruction review → Set `PROMPT_REVIEW=true`
- Otherwise → Set `SEMANTIC_ONLY=false`, `PROMPT_REVIEW=false` (full analysis)

**When `SEMANTIC_ONLY=true`**:
- Skip Phase 2 (Deterministic Gate)
- Go directly to Phase 3 (Semantic Review)
- Semantic review is MANDATORY regardless of STRICT/RELAXED mode

**When `PROMPT_REVIEW=true`**:
- Open and follow `{cypilot_path}/requirements/prompt-engineering.md`
- Execute 9-layer prompt engineering analysis
- Skip standard Cypilot analysis (not applicable to prompts)
- Output using prompt-engineering.md format
- Traceability checks: N/A (prompts don't have code markers)
- Registry checks: N/A (prompts may not be in artifacts.json)

---

## Phase 0: Ensure Dependencies

**After execution-protocol.md, you have**:
- `KITS_PATH` — path to loaded rules.md
- `TEMPLATE` — template content (from rules Dependencies)
- `CHECKLIST` — checklist content (from rules Dependencies)
- `EXAMPLE` — example content (from rules Dependencies)
- `REQUIREMENTS` — parsed requirements from rules
- `VALIDATION_CHECKS` — checks from rules.md Validation section

### Verify Rules Loaded

**If rules.md was loaded** (execution-protocol found artifact type):
- Dependencies already resolved from rules.md Dependencies section
- Checks defined in rules.md Validation section
- Proceed silently

**If rules.md NOT loaded** (manual mode):

| Dependency | Purpose | If missing |
|------------|---------|------------|
| **Checklist** | Criteria to check | Ask user to provide or specify path |
| **Template** | Expected structure and sections | Ask user to provide or specify path |
| **Example** | Reference for expected content quality | Ask user to provide or specify path |

### For Code (additional)

| Dependency | Purpose | If missing |
|------------|---------|------------|
| **Code checklist** | Baseline criteria for all code work | Load `{cypilot_path}/requirements/code-checklist.md` |
| **Design artifact** | Requirements that should be implemented | Ask user to specify source |

**MUST NOT proceed** to Phase 1 until all dependencies are available.

---

## Phase 0.5: Clarify Analysis Scope

### Scope Determination

**Ask user if unclear**:
```
What is the analysis scope?
- Full analysis (entire artifact/codebase)
- Partial analysis (specific sections/IDs)
- Quick check (structure only, skip semantic)
```

### Traceability Mode

**Check artifact's traceability setting in artifacts.json**:
- `FULL` → Check code markers, cross-reference IDs in codebase
- `DOCS-ONLY` → Skip codebase traceability checks

**If FULL traceability**:
- Identify codebase directories from artifacts.json
- Plan to check for `@cpt-*` markers
- Plan to verify all IDs have code implementations

### Registry Consistency

**Verify artifact is registered**:
- Check if target path exists in artifacts.json
- Verify kind matches registered kind
- Verify system assignment is correct

**If not registered**:
- Warn user and suggest registering it in `{cypilot_adapter_path}/artifacts.json` (preferred for STRICT analysis)
- If user wants to proceed anyway, require `/cypilot-analyze semantic` and clearly label output as semantic-only (no deterministic gate)

### Cross-Reference Scope

**Identify related artifacts**:
- Parent artifacts (what this references)
- Child artifacts (what references this)
- Code directories (if FULL traceability)

**Plan checking of**:
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
→ Run /cypilot-generate {TARGET_TYPE} {KIND} to create
```
STOP analysis.

---

## Phase 2: Deterministic Gate

**If `SEMANTIC_ONLY=true`**: Skip this phase, go to Phase 3.

**MUST run first when available** (when not semantic-only).

Deterministic gate is considered **available** when:
- Target is registered in `{cypilot_adapter_path}/artifacts.json` under a system with a `kit` configured (registry schema uses `kits`/`kit`), AND
- The kit `format` supports Cypilot CLI checks (typically `format: "Cypilot"`), AND
- You are analysing an artifact or code path supported by the CLI.

If deterministic gate is **not available** (e.g., unregistered path, RELAXED mode without configured kit/rules, or non-Cypilot kit format):
- Do **not** attempt to force `cypilot.py validate --artifact {PATH}`
- Require semantic-only analysis (`/cypilot-analyze semantic`) or ask the user to register/provide rules first

### For Artifacts

```bash
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py validate --artifact {PATH}
```

### For Code

```bash
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py validate --code {PATH} --design {design-path}
```

### Evaluate

**If FAIL**:
```
═══════════════════════════════════════════════
Analysis: {TARGET_TYPE}
───────────────────────────────────────────────
Status: FAIL
───────────────────────────────────────────────
Blocking issues:
{list from validator}
═══════════════════════════════════════════════

→ Fix issues and re-run analysis
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
| `/cypilot-analyze semantic` | Any | MANDATORY | Yes — per `agent-compliance.md` |
| `/cypilot-analyze` | **STRICT** | MANDATORY | Yes — per `agent-compliance.md` |
| `/cypilot-analyze` | **RELAXED** | Optional | No — best effort |

**If STRICT mode**:
- Semantic review is MANDATORY, not optional
- Agent MUST follow `{cypilot_path}/requirements/agent-compliance.md`
- Agent MUST provide evidence for each checklist category
- Agent MUST NOT skip categories or report bulk "PASS"
- Failure to complete semantic review → analysis INVALID

**If semantic review cannot be completed** (context limits, missing info, interruption):
1. Document which categories were checked with evidence
2. Mark incomplete categories with reason (e.g., "INCOMPLETE: context limit reached")
3. Output as `PARTIAL` — do NOT report overall PASS/FAIL
4. Include checkpoint guidance: "Resume with `/cypilot-analyze semantic` after addressing blockers"

**If RELAXED mode**:
- Semantic review is optional
- Agent proceeds with best effort
- Output includes disclaimer: `⚠️ Semantic review skipped (RELAXED mode)`

### Semantic Review Content (STRICT mode)

**Follow Validation section from loaded rules.md**:

### For Artifacts (rules.md Validation)

Execute phases from rules.md:
- **Phase 1: Structural Validation** — already done by deterministic gate
- **Phase 2: Semantic Validation** — checklist-based, from rules.md

Use checklist from Phase 0 dependencies.
Load adapter specs: `{cypilot_adapter_path}/AGENTS.md` → follow MANDATORY specs

Check (from rules.md + standard):
- [ ] Content quality per checklist
- [ ] Cross-references to parent artifacts valid
- [ ] Naming conventions followed
- [ ] No placeholder-like content
- [ ] Adapter specs compliance (paths, patterns, conventions)
- [ ] Versioning requirements met (from rules)
- [ ] Traceability requirements met (from rules)

### For Code (rules.md Validation)

Execute phases from codebase/rules.md:
- **Phase 1: Traceability Validation** — check code markers
- **Phase 2: Quality Validation** — checklist-based

Use checklist from Phase 0 dependencies.
Load design: related artifact(s)

Check (from rules.md + standard):
- [ ] All design requirements implemented
- [ ] Code follows conventions
- [ ] Tests cover requirements
- [ ] Cypilot markers present where required (to_code="true" IDs)
- [ ] Implemented items marked `[x]` in SPEC design

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
- [ ] Code markers use the canonical format from `requirements/traceability.md` (`@cpt-*` scope markers and `@cpt-begin`/`@cpt-end` blocks)
- [ ] No stale markers (ID no longer in design)

### ID Uniqueness & Format

- [ ] No duplicate IDs within artifact
- [ ] No duplicate IDs across system (use `cypilot list-ids`)
- [ ] All IDs follow naming convention
- [ ] All IDs have correct prefix for project

### Registry Consistency

- [ ] Artifact is registered in artifacts.json
- [ ] Kind matches registered kind
- [ ] System assignment is correct
- [ ] Path is correct

### Checkpoint for Large Artifacts

**For artifacts >500 lines or analysis taking multiple turns**:
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

### Full Analysis Output (default)

```
═══════════════════════════════════════════════
Analysis: {TARGET_TYPE}
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

### Semantic-Only Output (`/cypilot-analyze semantic`)

```
═══════════════════════════════════════════════
Semantic Analysis: {TARGET_TYPE}
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

Present applicable options to user based on result:

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
1. Re-run analysis
2. {option from rules Next Steps for issues}
3. Other
```

---

## State Summary

| State | TARGET_TYPE | Uses Template | Uses Checklist | Uses Design |
|-------|-------------|---------------|----------------|-------------|
| Analysing artifact | artifact | ✓ | ✓ | parent only |
| Analysing code | code | ✗ | ✓ | ✓ |

---

## Key Principles

### Deterministic Gate Is Authoritative

- If deterministic gate ran: its PASS/FAIL is the official result
- Semantic review adds recommendations (and, in STRICT mode, evidence-backed verification)
- If deterministic gate cannot run (unregistered/RELAXED/custom rules): do not label overall PASS; use semantic-only output and disclaim reduced rigor

### No Files Created

- All output to chat
- Never create ANALYSIS_REPORT.md
- Keep analysis stateless

### Fail Fast

- If deterministic gate fails → STOP
- Don't waste time on semantic review
- Report issues immediately

---

## Agent Self-Test (STRICT mode — AFTER completing work)

**CRITICAL**: Answer these questions AFTER doing the work, not before.
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

### Self-Test Output Format (include in analysis report)

```markdown
### Agent Self-Test Results

| Question | Answer | Evidence |
|----------|--------|----------|
| Read execution-protocol? | YES | Loaded cypilot-sdlc rules, checklist.md |
| Read artifact via Read tool? | YES | Read DESIGN.md: 742 lines |
| Checked every category? | YES | 12 categories in table above |
| Evidence for each status? | YES | Quotes included per category |
| N/A has document quotes? | YES | Lines 698, 712, 725 |
| Based on fresh read? | YES | Read tool called this turn |
```

**If ANY answer is NO or lacks evidence → Analysis is INVALID, must restart**

### RELAXED Mode

In RELAXED mode, self-test is advisory only. Include disclaimer:
```
⚠️ Self-test skipped (RELAXED mode — no Cypilot rules)
```

---

## Validation Criteria

- [ ] {cypilot_path}/requirements/execution-protocol.md executed
- [ ] Dependencies loaded (checklist, template, example)
- [ ] Analysis scope clarified
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
