---
fdd: true
type: requirement
name: Agent Compliance Protocol
version: 1.0
purpose: Enforcement protocol for AI agents executing FDD workflows (STRICT mode only)
---

# Agent Compliance Protocol

**Type**: Requirement
**Applies**: Only when Rules Mode = STRICT (see `execution-protocol.md`)

---

## Overview

This protocol defines mandatory behaviors for AI agents executing FDD workflows when FDD rules are enabled. It prevents common agent failure modes through structural enforcement.

**Key principle**: Trust but verify. Agents must prove they did the work, not just claim it.

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
| AP-008 | CONTEXT_ASSUMPTION | Assume file contents from previous context | File "too large to include" + no fresh Read |

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
✓ Read rules/sdlc/artifacts/DESIGN/checklist.md: 839 lines
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

1. ⚠️ Did I read the ENTIRE artifact via Read tool?
   → YES: Read architecture/DESIGN.md: 742 lines

2. ⚠️ Did I check EVERY checklist category?
   → YES: 12 categories processed (see breakdown above)

3. ⚠️ Did I provide evidence for each PASS/FAIL/N/A?
   → YES: Evidence table included

4. ⚠️ Did I verify N/A claims have explicit document statements?
   → YES: Found explicit N/A for PERF, SEC, OPS (lines 698, 712, 725)

5. ⚠️ Am I reporting based on actual file content, not memory?
   → YES: All quotes verified against fresh Read output
```

**If ANY answer is NO or unverifiable → validation is INVALID, must restart**

---

## Validation Output Schema (STRICT mode)

Agent MUST structure validation output as follows:

```markdown
## Validation Report

### 1. Protocol Compliance
- Rules Mode: STRICT (fdd-sdlc)
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
{answers to all 5 questions with evidence}

### 5. Final Status
- Deterministic: PASS | FAIL
- Semantic: PASS | FAIL ({N} issues)
- Overall: PASS | FAIL

### 6. Issues (if any)
{detailed issue descriptions}
```

**Free-form "PASS" or "looks good" without this structure → INVALID in STRICT mode**

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

When Rules Mode = RELAXED (no FDD rules):

- This compliance protocol does NOT apply
- Agent uses best judgment
- Output includes disclaimer: `⚠️ Validated without FDD rules (reduced rigor)`
- User accepts reduced confidence in results

---

## Validation Criteria (for this document)

- [ ] Agent understands anti-patterns and can self-detect
- [ ] Agent knows mandatory behaviors for STRICT mode
- [ ] Agent knows evidence standards for PASS/FAIL/N/A
- [ ] Agent knows self-test must be AFTER work, not before
- [ ] Agent knows output schema for STRICT mode
- [ ] Agent knows recovery procedure for violations
- [ ] Agent knows RELAXED mode has no enforcement
