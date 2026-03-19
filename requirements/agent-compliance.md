---
cypilot: true
type: requirement
name: Agent Compliance Protocol
version: 1.0
purpose: Enforcement protocol for AI agents executing Cypilot workflows (STRICT mode only)
---

# Agent Compliance Protocol

<!-- toc -->

- [Overview](#overview)
- [Agent Anti-Patterns](#agent-anti-patterns)
- [Mandatory Behaviors (STRICT mode)](#mandatory-behaviors-strict-mode)
- [Validation Output Schema (STRICT mode)](#validation-output-schema-strict-mode)
- [Error Handling](#error-handling)
- [Checkpoint Guidance](#checkpoint-guidance)
- [Recovery from Anti-Pattern Detection](#recovery-from-anti-pattern-detection)
- [Relaxed Mode Behavior](#relaxed-mode-behavior)
- [Consolidated Validation Checklist](#consolidated-validation-checklist)

<!-- /toc -->

**Type**: Requirement
**Applies**: Only when Rules Mode = STRICT (see `{cypilot_path}/.core/requirements/execution-protocol.md`)

## Overview
This protocol defines mandatory behaviors for AI agents executing Cypilot workflows when Cypilot rules are enabled. It prevents common agent failure modes through structural enforcement.

**Key principle**: Trust but verify — agents must provide observable evidence (quotes, line numbers, tool call confirmations) for every claim. "I checked it" without evidence = violation.

## Agent Anti-Patterns
Known failure modes to actively avoid:

| ID | Anti-pattern | Description | Detection signal |
|---|---|---|---|
| AP-001 | SKIP_SEMANTIC | Pass deterministic gate → skip semantic validation | No checklist items in output |
| AP-002 | MEMORY_VALIDATION | Validate from context/summary, not fresh file read | No Read tool call for target artifact |
| AP-003 | ASSUMED_NA | Mark checklist categories `N/A` without checking document | No quotes proving explicit N/A statements exist |
| AP-004 | BULK_PASS | Claim "all checks pass" without per-item verification | No individual evidence per checklist item |
| AP-005 | SELF_TEST_LIE | Answer self-test YES without actually completing work | Self-test output before actual validation work |
| AP-006 | SHORTCUT_OUTPUT | Report PASS immediately after deterministic gate | No semantic review section in output |
| AP-007 | TEDIUM_AVOIDANCE | Skip thorough checklist review because it's "tedious" | Missing categories in validation output |
| AP-008 | CONTEXT_ASSUMPTION | Assume file contents from previous context | System message says "file truncated" or "content summarized" + no fresh Read tool call in current turn |

If agent exhibits any anti-pattern, workflow output is **INVALID**.

## Mandatory Behaviors (STRICT mode)

| Area | MUST | MUST NOT |
|---|---|---|
| **Reading Artifacts** | Use `Read` tool for every artifact being validated or referenced; output `Read {path}: {line_count} lines`; re-read files if context was compacted (check for "too large to include" warnings) | Rely on context summaries for validation decisions; assume file contents from previous turns; skip reading because "I already read it earlier" |
| **Checklist Execution** | Use a todo tracking tool to track checklist progress category by category; process each checklist category individually; output PASS/FAIL/N/A for each category; provide evidence for each status claim | Batch all categories into single "PASS"; skip categories without explicit N/A justification; report completion without per-category breakdown |
| **Evidence Standards** | For PASS: quote specific text (2-5 sentences) and include line numbers or section headers; for N/A: quote explicit "Not applicable because..." statement; for FAIL: state what is missing/incorrect and where it should be | For N/A, agent CANNOT decide N/A on behalf of document author; if no explicit N/A statement exists, report VIOLATION, not N/A |
| **Self-Test Enforcement** | Self-test questions MUST be answered AFTER validation work, not before | If ANY self-test answer is NO or unverifiable, validation is INVALID and must restart |

Evidence examples:

```text
Read architecture/DESIGN.md: 742 lines
Read kits/sdlc/artifacts/DESIGN/checklist.md: 839 lines
```

Checklist progress evidence format:

| Category | Status | Evidence |
|---|---|---|
| ARCH-DESIGN-001 | PASS | Lines 45-67: "System purpose is to provide..." |
| ARCH-DESIGN-002 | PASS | Lines 102-145: Principles section with 9 principles |
| PERF-DESIGN-001 | N/A | Line 698: "Performance architecture not applicable — local CLI tool" |
| SEC-DESIGN-001 | N/A | No explicit N/A statement found → VIOLATION |

Agent self-test questions:

1. Did I load and follow `agent-compliance.md` (this protocol)?
2. Did I read the ENTIRE artifact via Read tool THIS turn?
3. Did I check EVERY checklist category?
4. Did I provide evidence for each PASS/FAIL/N/A?
5. Did I verify N/A claims have explicit document statements?
6. Am I reporting based on actual file content, not memory/summary?

## Validation Output Schema (STRICT mode)

Agent MUST structure validation output with these six sections:

| Section | Required content |
|---|---|
| **1. Protocol Compliance** | Rules Mode: STRICT (`cypilot-sdlc`); Artifact Read: `{path}` (`{N}` lines); Checklist Loaded: `{path}` (`{N}` lines) |
| **2. Deterministic Gate** | Status: PASS/FAIL; Errors: `{list if any}` |
| **3. Semantic Review (MANDATORY)** | `Checklist Progress` table with `{ID} \| PASS/FAIL/N/A \| {quote or violation description}` for each category; `Categories Summary` with Total, PASS, FAIL, N/A (explicit), N/A (missing statement) → VIOLATIONS |
| **4. Agent Self-Test** | Answers to all 6 self-test questions with evidence |
| **5. Final Status** | Deterministic: PASS/FAIL; Semantic: PASS/FAIL (`{N}` issues); Overall: PASS/FAIL |
| **6. Issues (if any)** | Detailed issue descriptions |

Minimal STRICT-mode example:

```markdown
## Validation Report

### 1. Protocol Compliance
- Rules Mode: STRICT (`cypilot-sdlc`)
- Artifact Read: architecture/DESIGN.md (742 lines)

### 2. Deterministic Gate
- Status: PASS

### 3. Semantic Review (MANDATORY)
- Checklist Progress: evidence table included

### 4. Agent Self-Test
- All 6 questions answered with evidence

### 5. Final Status
- Overall: PASS

### 6. Issues (if any)
- None
```

Free-form `PASS` or `looks good` without this structure is **INVALID** in STRICT mode.

## Error Handling

| Error | Required response | Action |
|---|---|---|
| Read tool fails | `⚠️ Cannot read artifact: {error}` → validation cannot proceed without artifact access → fix path/file/retry | STOP — validation requires artifact content |
| Context compaction during validation | `⚠️ Context compacted during validation` → previous Read outputs may be summarized/truncated → MUST re-read all artifacts before continuing | Re-execute Read tool for all artifacts, then continue from current checkpoint |
| Checklist file not found | `⚠️ Checklist not found: {path}` → cannot perform semantic validation without criteria → fix rules path / `artifacts.toml` configuration | STOP — semantic validation requires checklist |

## Checkpoint Guidance

When validating artifacts `>500` lines OR checklist has `>15` categories:

| Situation | Required behavior |
|---|---|
| After each category group (3-5 categories) | Output progress checkpoint listing completed category IDs/statuses, then continue |
| Context runs low | Save checkpoint with completed categories, remaining categories, and resume instructions |
| Resume after compaction | Re-read artifact via Read tool; verify artifact unchanged (check line count); continue from saved checkpoint |

## Recovery from Anti-Pattern Detection

If agent or user detects anti-pattern violation:

1. **Acknowledge** — `I exhibited anti-pattern {ID}: {description}`
2. **Explain** — `This happened because {honest reason}`
3. **Discard** — `Previous validation output is INVALID`
4. **Restart** — Execute full protocol from beginning
5. **Prove** — Include compliance evidence in new output

## Relaxed Mode Behavior

When Rules Mode = RELAXED (no Cypilot rules):

- This compliance protocol does NOT apply
- Agent uses best judgment
- Output includes disclaimer: `⚠️ Validated without Cypilot rules (reduced rigor)`
- User accepts reduced confidence in results

## Consolidated Validation Checklist

Use this checklist to validate agent compliance protocol understanding.

| Group | Check | Required | How to verify |
|---|---|---|---|
| **Understanding (U)** | U.1 Agent understands all 8 anti-patterns | YES | Can identify AP-001 through AP-008 by name |
| **Understanding (U)** | U.2 Agent knows mandatory behaviors for STRICT mode | YES | Can list Read, Checklist, Evidence, Self-Test requirements |
| **Understanding (U)** | U.3 Agent knows evidence standards for PASS/FAIL/N/A | YES | Can describe what each status requires |
| **Understanding (U)** | U.4 Agent knows self-test must be AFTER work | YES | Self-test appears at end of validation output |
| **Understanding (U)** | U.5 Agent knows output schema for STRICT mode | YES | Validation output follows 6-section schema |
| **Understanding (U)** | U.6 Agent knows recovery procedure for violations | YES | Can list 5 recovery steps |
| **Understanding (U)** | U.7 Agent knows RELAXED mode has no enforcement | YES | Includes disclaimer when RELAXED |
| **Execution (E)** | E.1 Read tool used for every artifact | YES | `Read {path}:` confirmation in output |
| **Execution (E)** | E.2 Checklist progress tracked with TodoWrite | YES | Todo list shows category progress |
| **Execution (E)** | E.3 Evidence provided for every status claim | YES | Evidence table has no empty cells |
| **Execution (E)** | E.4 Self-test answered with evidence | YES | All 6 questions answered with proof |
| **Execution (E)** | E.5 Output follows STRICT mode schema | YES | All 6 sections present |
| **Execution (E)** | E.6 No anti-patterns exhibited | YES | No detection signals present |
| **Final (F)** | F.1 All Understanding checks pass | YES | U.1-U.7 verified |
| **Final (F)** | F.2 All Execution checks pass | YES | E.1-E.6 verified |
| **Final (F)** | F.3 Validation output is complete | YES | No `continuing later` or partial reports |
