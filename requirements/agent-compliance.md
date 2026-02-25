---
cypilot: true
type: requirement
name: Agent Compliance Protocol
version: 1.0
purpose: Enforcement protocol for AI agents executing Cypilot workflows (STRICT mode only)
---

# Agent Compliance Protocol

**Type**: Requirement
**Applies**: Only when Rules Mode = STRICT (see `execution-protocol.md`)

---

## Table of Contents

- [Overview](#overview)
- [Agent Anti-Patterns](#-agent-anti-patterns)
- [Mandatory Behaviors](#mandatory-behaviors-strict-mode)
- [Validation Output Schema](#validation-output-schema-strict-mode)
- [Error Handling](#error-handling)
- [Checkpoint Guidance](#checkpoint-guidance-for-large-artifacts)
- [Recovery from Anti-Pattern Detection](#recovery-from-anti-pattern-detection)
- [Relaxed Mode Behavior](#relaxed-mode-behavior)
- [Consolidated Validation Checklist](#consolidated-validation-checklist)

---

## Overview

This protocol defines mandatory behaviors for AI agents executing Cypilot workflows when Cypilot rules are enabled. It prevents common agent failure modes through structural enforcement.

**Key principle**: Trust but verify — agents must provide observable evidence (quotes, line numbers, tool call confirmations) for every claim. "I checked it" without evidence = violation.

---

## ⛔ Agent Anti-Patterns

**Known failure modes to actively avoid**:

| ID | Anti-Pattern | Description | Detection Signal |
|----|--------------|-------------|------------------|
| AP-001 | SKIP_SEMANTIC | Pass deterministic gate → skip semantic validation | No checklist items in output |
| AP-002 | MEMORY_VALIDATION | Validate from context/summary, not fresh file read | No Read tool call for target artifact |
| AP-003 | ASSUMED_NA | Mark checklist categories "N/A" without checking document | No quotes proving explicit N/A statements exist |
| AP-004 | BULK_PASS | Claim "all checks pass" without per-item verification | No individual evidence per checklist item |
| AP-005 | SELF_TEST_LIE | Answer self-test YES without actually completing work | Self-test output before actual validation work |
| AP-006 | SHORTCUT_OUTPUT | Report PASS immediately after deterministic gate | No semantic review section in output |
| AP-007 | TEDIUM_AVOIDANCE | Skip thorough checklist review because it's "tedious" | Missing categories in validation output |
| AP-008 | CONTEXT_ASSUMPTION | Assume file contents from previous context | System message says "file truncated" or "content summarized" + no fresh Read tool call in current turn |

**If agent exhibits any anti-pattern → workflow output INVALID**

---

## Mandatory Behaviors (STRICT mode)

### 1. Reading Artifacts

**MUST**:
- Use `Read` tool for every artifact being validated or referenced
- Output confirmation: `Read {path}: {line_count} lines`
- Re-read files if context was compacted (check for "too large to include" warnings)

**MUST NOT**:
- Rely on context summaries for validation decisions
- Assume file contents from previous conversation turns
- Skip reading because "I already read it earlier"

**Evidence**:
```
✓ Read architecture/DESIGN.md: 742 lines
✓ Read kits/sdlc/artifacts/DESIGN/checklist.md: 839 lines
```

### 2. Checklist Execution

**MUST**:
- Use `TodoWrite` to track checklist progress category by category
- Process each checklist category individually (not all at once)
- Output status for each category: PASS | FAIL | N/A
- Provide evidence for each status claim

**MUST NOT**:
- Batch all categories into single "PASS"
- Skip categories without explicit N/A justification
- Report completion without per-category breakdown

**Evidence format**:
```
### Checklist Progress

| Category | Status | Evidence |
|----------|--------|----------|
| ARCH-DESIGN-001 | PASS | Lines 45-67: "System purpose is to provide..." |
| ARCH-DESIGN-002 | PASS | Lines 102-145: Principles section with 9 principles |
| PERF-DESIGN-001 | N/A | Line 698: "Performance architecture not applicable — local CLI tool" |
| SEC-DESIGN-001 | N/A | No explicit N/A statement found → VIOLATION |
```

### 3. Evidence Standards

**For PASS claims**:
- Quote specific text from document (2-5 sentences)
- Include line numbers or section headers
- Evidence must directly prove the requirement is met

**For N/A claims**:
- Quote the explicit "Not applicable because..." statement from document
- If no explicit statement exists → report as VIOLATION, not N/A
- Agent CANNOT decide N/A on behalf of document author

**For FAIL claims**:
- State what's missing or incorrect
- Provide location where it should be
- Quote surrounding context if helpful

### 4. Self-Test Enforcement

**Self-test questions MUST be answered AFTER validation work, not before**:

```markdown
### Agent Self-Test (completed AFTER validation)

1. ⚠️ Did I load and follow agent-compliance.md (this protocol)?
   → YES: Protocol loaded at start of STRICT mode validation

2. ⚠️ Did I read the ENTIRE artifact via Read tool THIS turn?
   → YES: Read architecture/DESIGN.md: 742 lines

3. ⚠️ Did I check EVERY checklist category?
   → YES: 12 categories processed (see breakdown above)

4. ⚠️ Did I provide evidence for each PASS/FAIL/N/A?
   → YES: Evidence table included

5. ⚠️ Did I verify N/A claims have explicit document statements?
   → YES: Found explicit N/A for PERF, SEC, OPS (lines 698, 712, 725)

6. ⚠️ Am I reporting based on actual file content, not memory/summary?
   → YES: All quotes verified against fresh Read output
```

**If ANY answer is NO or unverifiable → validation is INVALID, must restart**

---

## Validation Output Schema (STRICT mode)

Agent MUST structure validation output as follows:

```markdown
## Validation Report

### 1. Protocol Compliance
- Rules Mode: STRICT (cypilot-sdlc)
- Artifact Read: {path} ({N} lines)
- Checklist Loaded: {path} ({N} lines)

### 2. Deterministic Gate
- Status: PASS | FAIL
- Errors: {list if any}

### 3. Semantic Review (MANDATORY)

#### Checklist Progress
| Category | Status | Evidence |
|----------|--------|----------|
| {ID} | PASS/FAIL/N/A | {quote or violation description} |
| ... | ... | ... |

#### Categories Summary
- Total: {N}
- PASS: {N}
- FAIL: {N}
- N/A (explicit): {N}
- N/A (missing statement): {N} → VIOLATIONS

### 4. Agent Self-Test
{answers to all 6 questions with evidence}

### 5. Final Status
- Deterministic: PASS | FAIL
- Semantic: PASS | FAIL ({N} issues)
- Overall: PASS | FAIL

### 6. Issues (if any)
{detailed issue descriptions}
```

**Free-form "PASS" or "looks good" without this structure → INVALID in STRICT mode**

---

## Error Handling

### Read Tool Fails

**If Read tool returns error** (file not found, permission denied):
```
⚠️ Cannot read artifact: {error}
→ Validation cannot proceed without artifact access
→ Fix: Verify path, check file exists, retry
```
**Action**: STOP — validation requires artifact content.

### Context Compaction During Validation

**If context compaction occurs mid-validation** (conversation summary appears):
```
⚠️ Context compacted during validation
→ Previous Read outputs may be summarized/truncated
→ MUST re-read all artifacts before continuing
```
**Action**: Re-execute Read tool for all artifacts, then continue from current checkpoint.

### Checklist File Not Found

**If checklist cannot be loaded**:
```
⚠️ Checklist not found: {path}
→ Cannot perform semantic validation without criteria
→ Fix: Verify rules path, check artifacts.toml configuration
```
**Action**: STOP — semantic validation requires checklist.

---

## Checkpoint Guidance (for large artifacts)

**When validating artifacts >500 lines OR checklist has >15 categories**:

1. **After each category group** (3-5 categories), output progress:
   ```
   Checkpoint: Categories 1-5 of 15 complete
   - ARCH-DESIGN-001: PASS
   - ARCH-DESIGN-002: PASS
   - ARCH-DESIGN-003: PASS
   - PERF-DESIGN-001: N/A (explicit)
   - PERF-DESIGN-002: N/A (explicit)
   Continuing to categories 6-10...
   ```

2. **If context runs low** (approaching token limit), save state:
   ```
   ⚠️ Context limit approaching — saving checkpoint
   Completed: Categories 1-10 (all PASS/N/A)
   Remaining: Categories 11-15
   Resume: Re-read artifact, continue from category 11
   ```

3. **On resume after compaction**:
   - Re-read artifact via Read tool
   - Verify artifact unchanged (check line count)
   - Continue from saved checkpoint

---

## Recovery from Anti-Pattern Detection

If agent or user detects anti-pattern violation:

1. **Acknowledge** — "I exhibited anti-pattern {ID}: {description}"
2. **Explain** — "This happened because {honest reason}"
3. **Discard** — "Previous validation output is INVALID"
4. **Restart** — Execute full protocol from beginning
5. **Prove** — Include compliance evidence in new output

---

## Relaxed Mode Behavior

When Rules Mode = RELAXED (no Cypilot rules):

- This compliance protocol does NOT apply
- Agent uses best judgment
- Output includes disclaimer: `⚠️ Validated without Cypilot rules (reduced rigor)`
- User accepts reduced confidence in results

---

## Consolidated Validation Checklist

**Use this checklist to validate agent compliance protocol understanding.**

### Understanding (U)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| U.1 | Agent understands all 8 anti-patterns | YES | Can identify AP-001 through AP-008 by name |
| U.2 | Agent knows mandatory behaviors for STRICT mode | YES | Can list Read, Checklist, Evidence, Self-Test requirements |
| U.3 | Agent knows evidence standards for PASS/FAIL/N/A | YES | Can describe what each status requires |
| U.4 | Agent knows self-test must be AFTER work | YES | Self-test appears at end of validation output |
| U.5 | Agent knows output schema for STRICT mode | YES | Validation output follows 6-section schema |
| U.6 | Agent knows recovery procedure for violations | YES | Can list 5 recovery steps |
| U.7 | Agent knows RELAXED mode has no enforcement | YES | Includes disclaimer when RELAXED |

### Execution (E)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| E.1 | Read tool used for every artifact | YES | `Read {path}:` confirmation in output |
| E.2 | Checklist progress tracked with TodoWrite | YES | Todo list shows category progress |
| E.3 | Evidence provided for every status claim | YES | Evidence table has no empty cells |
| E.4 | Self-test answered with evidence | YES | All 6 questions answered with proof |
| E.5 | Output follows STRICT mode schema | YES | All 6 sections present |
| E.6 | No anti-patterns exhibited | YES | No detection signals present |

### Final (F)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| F.1 | All Understanding checks pass | YES | U.1-U.7 verified |
| F.2 | All Execution checks pass | YES | E.1-E.6 verified |
| F.3 | Validation output is complete | YES | No "continuing later" or partial reports |
