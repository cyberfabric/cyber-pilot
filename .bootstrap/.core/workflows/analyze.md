---
cypilot: true
type: workflow
name: cypilot-analyze
description: Analyze Cypilot artifacts against templates or code against design requirements with traceability verification (tool invocation is validate-only)
version: 1.0
purpose: Universal workflow for analysing any Cypilot artifact or code
---

# Analyze


<!-- toc -->

- [Rules](#rules)
- [Overview](#overview)
- [Context Budget & Overflow Prevention (CRITICAL)](#context-budget--overflow-prevention-critical)
- [Mode Detection](#mode-detection)
- [Phase 0: Ensure Dependencies](#phase-0-ensure-dependencies)
- [Phase 0.1: Plan Escalation Gate](#phase-01-plan-escalation-gate)
- [Phase 0.5: Clarify Analysis Scope](#phase-05-clarify-analysis-scope)
- [Phase 1: File Existence Check](#phase-1-file-existence-check)
- [Phase 2: Deterministic Gate](#phase-2-deterministic-gate)
- [Phase 3: Semantic Review (Conditional)](#phase-3-semantic-review-conditional)
- [Phase 4: Output](#phase-4-output)
- [Phase 5: Offer Next Steps](#phase-5-offer-next-steps)
- [State Summary](#state-summary)
- [Key Principles](#key-principles)
- [Agent Self-Test (STRICT mode — AFTER completing work)](#agent-self-test-strict-mode--after-completing-work)
- [Validation Criteria](#validation-criteria)

<!-- /toc -->

ALWAYS open and follow `{cypilot_path}/.core/skills/cypilot/SKILL.md` FIRST WHEN {cypilot_mode} is `off`

**Type**: Analysis

ALWAYS open and follow `{cypilot_path}/.core/requirements/execution-protocol.md` FIRST

ALWAYS open and follow `{cypilot_path}/.core/requirements/code-checklist.md` WHEN user requests analysis of code, codebase changes, or implementation behavior (Code mode)

ALWAYS open and follow `{cypilot_path}/.core/requirements/consistency-checklist.md` WHEN user requests analysis of documentation/artifact consistency, contradiction detection, or cross-document alignment (Consistency mode)

ALWAYS open and follow `{cypilot_path}/.core/requirements/prompt-engineering.md` WHEN user requests analysis of:
- System prompts, agent prompts, or LLM prompts
- Agent instructions or agent guidelines
- Skills, workflows, or methodologies
- AGENTS.md or navigation rules
- Any document containing instructions for AI agents
- User explicitly mentions `prompt engineering review` or `instruction quality`

When `prompt-engineering.md` is loaded for instruction analysis, treat compact-prompts optimization as a **HIGH-priority requirement**: explicitly look for safe ways to reduce loaded context while preserving clarity, determinism, constraints, and recovery behavior.

## Rules

**MUST** check **EVERY SINGLE** applicable criterion; verify **EACH ITEM** individually; read the **COMPLETE** artifact; validate **EVERY** ID, reference, and section; check for **ALL** placeholders, empty sections, and missing content; cross-reference **EVERY** actor/capability/requirement ID; report **EVERY** issue found.

**MUST NOT** skip checks, assume sections are correct without verifying, or give benefit of doubt.

**One missed issue = INVALID analysis**

**Reference**: `{cypilot_path}/.core/requirements/agent-compliance.md` for the full anti-pattern list.
- `AP-001 SKIP_SEMANTIC`: reporting overall PASS from deterministic checks alone.
- `AP-002 MEMORY_VALIDATION`: claiming review without a fresh Read tool call.
- `AP-003 ASSUMED_NA`: marking a category N/A without document evidence.
- `AP-004 BULK_PASS`: claiming "all pass" without per-category evidence.
- `AP-005 SIMULATED_VALIDATION`: producing a validation summary without running `cpt validate`.
Before output, self-check: PASS without semantic review? fresh Read this turn? N/A claims quoted? per-category evidence present? actual `cpt validate` output shown? If any answer is no → STOP and restart with compliance.

## Overview
Modes: Full (default) = deterministic gate → semantic review; Semantic-only = skip deterministic gate; Artifact = template + checklist; Code = checklist + design requirements; Prompt review = prompt-engineering workflow.
Commands: `/cypilot-analyze`, `/cypilot-analyze semantic`, `/cypilot-analyze --artifact <path>`, `/cypilot-analyze semantic --artifact <path>`, `/cypilot-analyze prompt <path>`.
Prompt review triggers include "analyze this system prompt", "review agent instructions", "check this workflow/skill", and "prompt engineering review". After `execution-protocol.md`, you have `TARGET_TYPE`, `RULES`, `KIND`, `PATH`, and resolved dependencies.

## Context Budget & Overflow Prevention (CRITICAL)
- Budget first: estimate size before loading large docs (for example with `wc -l`) and state the budget for this turn.
- Load only what you use: prefer rules.md Validation and only needed checklist categories; avoid large registries/specs unless required.
- Chunk reads and summarize-and-drop: use `read_file` ranges, summarize each chunk, and keep only extracted criteria.
- Fail-safe: if checks cannot be completed within context, output `PARTIAL` with checkpoint status and resume guidance; do not claim overall PASS.
- Plan escalation: [Phase 0.1](#phase-01-plan-escalation-gate) is mandatory after dependencies load; if budget is exceeded, the agent MUST offer plan escalation before proceeding.

## Mode Detection
- `/cypilot-analyze semantic` or `cypilot analyze semantic` → `SEMANTIC_ONLY=true`; skip Phase 2 and go to Phase 3; semantic review remains mandatory.
- `/cypilot-analyze prompt` or prompt/instruction review context → `PROMPT_REVIEW=true`; open prompt-engineering.md, run 9-layer review, explicitly search for safe context-reduction opportunities per compact-prompts methodology, skip standard Cypilot analysis, use prompt-engineering output, and treat traceability / registry checks as N/A.
- Otherwise → `SEMANTIC_ONLY=false`, `PROMPT_REVIEW=false`; run full analysis.

## Phase 0: Ensure Dependencies
After `execution-protocol.md`, you have `KITS_PATH`, `TEMPLATE`, `CHECKLIST`, `EXAMPLE`, `REQUIREMENTS`, and `VALIDATION_CHECKS`.

- If `rules.md` loaded: dependencies and validation checks were already resolved; proceed silently.
- If `rules.md` not loaded: ask the user to provide/specify missing `checklist`, `template`, or `example`.
- Code mode additional: load `{cypilot_path}/.core/requirements/code-checklist.md` and ask the user to specify the design artifact if missing.

**MUST NOT proceed** to Phase 1 until all dependencies are available.

## Phase 0.1: Plan Escalation Gate
**MUST** estimate total context: target `rules.md` Validation, target `checklist.md`, artifact content, related cross-reference artifacts, expected analysis output, and ~30% reasoning overhead.

| Estimated total | Action |
|----------------|--------|
| `≤ 1200` lines | Proceed normally — optimal zone, >95% checklist coverage. |
| `1201-2000` lines | Proceed with warning + aggressive summarize-and-drop: _"This is a medium-sized analysis. Activating chunked loading — will output PARTIAL if context runs low."_ |
| `> 2000` lines | **MUST** offer plan escalation before proceeding. |

Offer when `> 2000` lines:
```
⚠️ This analysis is large — estimated ~{N} lines of context needed:
  - checklist.md:  ~{n} lines
  - rules.md:      ~{n} lines
  - artifact:      ~{n} lines
  - cross-refs:    ~{n} lines
  - output:        ~{n} lines (estimated)

This exceeds the safe single-context budget (~2000 lines).
The plan workflow can decompose this into focused analysis phases (≤500 lines each)
that ensure every checklist item is checked and nothing is skipped.

Options:
1. Switch to /cypilot-plan (recommended for thorough analysis)
2. Continue here (risk: context overflow, checks may be partially applied)
```
If user chooses plan: stop and tell them to run `/cypilot-plan analyze {KIND}` with the same parameters. If user chooses continue: proceed with aggressive chunking and log _"Proceeding in single-context mode — some checks may be missed for large artifacts."_

## Phase 0.5: Clarify Analysis Scope

If scope is unclear, ask:
```
What is the analysis scope?
- Full analysis (entire artifact/codebase)
- Partial analysis (specific sections/IDs)
- Quick check (structure only, skip semantic)
```
- Traceability mode: read artifacts.toml — `FULL` means check code markers and codebase cross-refs; `DOCS-ONLY` means skip codebase traceability checks.
- If `FULL`: identify code directories, plan `@cpt-*` marker checks, and verify all IDs have code implementations.
- Registry consistency: verify target path exists in artifacts.toml, kind matches, and system assignment is correct.
- If not registered: warn the user, suggest registering in `{cypilot_path}/config/artifacts.toml`, and if they continue require `/cypilot-analyze semantic` with output clearly labeled semantic-only.
- Cross-reference scope: identify parent artifacts, child artifacts, and code directories (if FULL); plan checks for outgoing refs, incoming refs, and orphaned IDs.

## Phase 1: File Existence Check

Check that `{PATH}` exists, is readable, and is not empty.

If any check fails:
```
✗ Target not found: {PATH}
→ Run /cypilot-generate {TARGET_TYPE} {KIND} to create
```
STOP analysis.

## Phase 2: Deterministic Gate

If `SEMANTIC_ONLY=true`, skip this phase and go to Phase 3.

> **⛔ CRITICAL**: The agent's own checklist walkthrough is **NOT** a substitute for `cpt validate`. A manual "✅ PASS" table in chat is semantic review, not deterministic validation — these are **separate steps**. See anti-pattern `SIMULATED_VALIDATION`.

Deterministic gate is available only when the target is registered in `{cypilot_path}/config/artifacts.toml` under a system with a configured `kit`, the kit `format` supports Cypilot CLI checks (typically `format: "Cypilot"`), and the artifact or code path is supported by the CLI.

If deterministic gate is not available, do **not** force `cypilot.py validate --artifact {PATH}`; require semantic-only analysis or ask the user to register/provide rules first.

Artifacts:
```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py validate --artifact {PATH}
```
Code:
```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py validate
```
- MUST execute `cpt validate` as an actual terminal command BEFORE any semantic review.
- MUST include exit code and JSON `status` / `error_count` / `warning_count` in the response as invocation evidence.
- MUST NOT proceed to Phase 3 until `cpt validate` returns `"status": "PASS"`; if FAIL, report issues and STOP.
- MUST NOT produce a validation summary without first showing actual `cpt validate` output; doing so is `SIMULATED_VALIDATION`.

If FAIL:
```
═══════════════════════════════════════════════
Analysis: {TARGET_TYPE}
───────────────────────────────────────────────
Status: FAIL
Exit code: 2
Errors: {N}, Warnings: {N}
───────────────────────────────────────────────
Blocking issues:
{list from validator}
═══════════════════════════════════════════════

→ Fix issues and re-run analysis
```
STOP — do not proceed to semantic review.

If PASS:
```
Deterministic gate: PASS (exit code: 0, errors: 0, warnings: {N})
```
Continue to Phase 3.

## Phase 3: Semantic Review (Conditional)

Run if deterministic gate PASS, or if `SEMANTIC_ONLY=true`.

| Invocation | Rules mode | Semantic review | Evidence required |
|------------|------------|-----------------|-------------------|
| `/cypilot-analyze semantic` | Any | MANDATORY | Yes — per `agent-compliance.md` |
| `/cypilot-analyze` | STRICT | MANDATORY | Yes — per `agent-compliance.md` |
| `/cypilot-analyze` | RELAXED | Optional | No — best effort |

STRICT mode: semantic review is MANDATORY; the agent MUST follow `{cypilot_path}/.core/requirements/agent-compliance.md`; the agent MUST provide evidence for each checklist category; the agent MUST NOT skip categories or report bulk PASS; failure to complete semantic review makes the analysis INVALID.

If semantic review cannot be completed: document checked categories with evidence, mark incomplete categories with reason, output `PARTIAL`, and include `Resume with /cypilot-analyze semantic after addressing blockers`. RELAXED mode: if semantic review is skipped, include `⚠️ Semantic review skipped (RELAXED mode)`.

### Semantic Review Content (STRICT mode)

Follow the loaded `rules.md` Validation section.

- [ ] Artifacts: execute rules.md semantic validation using the loaded checklist; load `{cypilot_path}/.gen/AGENTS.md`; check content quality, parent cross-references, naming conventions, placeholder-like content, adapter spec compliance, versioning requirements, and traceability requirements.
- [ ] Code: execute codebase/rules.md traceability + quality validation; load related design artifact(s); check requirement implementation, conventions, tests, required markers, and `[x]` completion in SPEC design.
- [ ] Completeness: no placeholder markers (`TODO`, `TBD`, `[Description]`), no empty sections, all IDs follow required format, all IDs are unique, all required fields are present.
- [ ] Coverage: all parent requirements addressed, all referenced IDs exist, all parent actors/capabilities covered, no orphaned references.
- [ ] Traceability (`FULL`): all requirement / flow / algorithm IDs have code markers, all test IDs have test implementations, markers follow `requirements/traceability.md`, and no stale markers remain.
- [ ] ID uniqueness & format: no duplicate IDs within artifact, no duplicate IDs across system (`cypilot list-ids`), all IDs follow naming convention, all IDs use the correct project prefix.
- [ ] Registry consistency: artifact is registered in artifacts.toml, kind matches, system assignment is correct, and path is correct.

Checkpoint rule for artifacts `>500` lines or multi-turn analysis: after each checklist group, note progress; if context runs low, save completed categories, remaining categories, and current artifact position; on resume, re-read the artifact, verify unchanged, and continue from the checkpoint. Categorize recommendations as **High**, **Medium**, or **Low**.

## Phase 4: Output

Print to chat only; create no files.

### Full Analysis Output (default)
```markdown
## Analysis
**Target**: {TARGET_TYPE}
**Kind**: {KIND}
**Name**: {name}
**Path**: {PATH}
**Status**: PASS/FAIL/PARTIAL

### Deterministic Gate
- Exit code: {0|2}
- Status: {PASS|FAIL|SKIPPED}
- Errors: {N}, Warnings: {N}

### Category Review
| Category | Status | Evidence |
|----------|--------|----------|
| {category} | PASS/FAIL/N/A/PARTIAL | {line refs, quotes} |

### Recommendations
- **High**: {issue with location}
- **Medium**: {issue with location}
- **Low**: {issue with location}

### Coverage
- Requirements: {X}/{Y} implemented
- Tests: {X}/{Y} covered

### Agent Self-Test Results
| Question | Answer | Evidence |
|----------|--------|----------|
| {question} | YES/NO | {evidence} |
```
### Semantic-Only Output (`/cypilot-analyze semantic`)
```
Semantic Analysis: {TARGET_TYPE}
kind: {KIND}
name: {name}
path: {PATH}
Mode: SEMANTIC ONLY (deterministic gate skipped)
Status: PASS/FAIL
| Category | Status | Evidence |
|----------|--------|----------|
| {category} | PASS/FAIL/N/A | {line refs, quotes} |
High: {issue with location}
Medium: {issue with location}
Checklist items: {X}/{Y} passed
N/A categories: {list with reasoning}
```
## Phase 5: Offer Next Steps

Read `## Next Steps` from `rules.md` and present applicable options.

PASS:
```
What would you like to do next?
1. {option from rules Next Steps for success}
2. {option from rules Next Steps}
3. Other
```
FAIL:
```
Fix the issues above, then:
1. Re-run analysis
2. {option from rules Next Steps for issues}
3. Other
```
## State Summary

| State | TARGET_TYPE | Uses Template | Uses Checklist | Uses Design |
|-------|-------------|---------------|----------------|-------------|
| Analysing artifact | artifact | ✓ | ✓ | parent only |
| Analysing code | code | ✗ | ✓ | ✓ |

## Key Principles

- Deterministic gate PASS/FAIL is authoritative when it runs.
- Semantic review adds recommendations and, in STRICT mode, evidence-backed verification.
- If the deterministic gate cannot run, do not label overall PASS; use semantic-only output and disclaim reduced rigor.
- Output is chat-only; never create `ANALYSIS_REPORT.md`; keep analysis stateless.
- If deterministic gate fails, STOP and report issues immediately.

## Agent Self-Test (STRICT mode — AFTER completing work)

Answer these AFTER doing the work and include evidence in the output.

| Question | Evidence required |
|----------|-------------------|
| Did I read execution-protocol.md before starting? | Show loaded rules and dependencies. |
| Did I use Read tool to read the ENTIRE artifact THIS turn? | `Read {path}: {N} lines` |
| Did I check EVERY checklist category individually? | Category breakdown table with per-category status. |
| Did I provide evidence (quotes, line numbers) for each PASS/FAIL/N/A? | Evidence column in category table. |
| For N/A claims, did I quote explicit "Not applicable" statements from the document? | Quote lines showing the author marked N/A. |
| Am I reporting from actual file content, not memory/summary? | Fresh Read tool call visible this turn. |

Sample:
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

RELAXED mode disclaimer:
```text
⚠️ Self-test skipped (RELAXED mode — no Cypilot rules)
```
## Validation Criteria

- [ ] `{cypilot_path}/.core/requirements/execution-protocol.md` executed
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
