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

- [Analyze](#analyze)
  - [Rules](#rules)
  - [Overview](#overview)
  - [Context Budget \& Overflow Prevention (CRITICAL)](#context-budget--overflow-prevention-critical)
  - [Mode Detection](#mode-detection)
  - [Phase 0: Ensure Dependencies](#phase-0-ensure-dependencies)
  - [Phase 0.1: Plan Escalation Gate](#phase-01-plan-escalation-gate)
  - [Phase 0.5: Clarify Analysis Scope](#phase-05-clarify-analysis-scope)
  - [Phase 1: File Existence Check](#phase-1-file-existence-check)
  - [Phase 2: Deterministic Gate](#phase-2-deterministic-gate)
  - [Phase 3: Semantic Review (Conditional)](#phase-3-semantic-review-conditional)
    - [Semantic Review Content (STRICT mode)](#semantic-review-content-strict-mode)
  - [Phase 4: Output](#phase-4-output)
    - [Standard Analysis Output (non-prompt review)](#standard-analysis-output-non-prompt-review)
    - [Prompt Review Output (PROMPT\_REVIEW)](#prompt-review-output-prompt_review)
    - [Fix Prompt](#fix-prompt)
    - [Plan Prompt](#plan-prompt)
    - [Semantic-Only Output (`/cypilot-analyze semantic`)](#semantic-only-output-cypilot-analyze-semantic)
  - [Phase 5: Offer Next Steps](#phase-5-offer-next-steps)
  - [State Summary](#state-summary)
  - [Key Principles](#key-principles)
  - [Agent Self-Test (STRICT mode — AFTER completing work)](#agent-self-test-strict-mode--after-completing-work)
  - [Validation Criteria](#validation-criteria)

<!-- /toc -->

ALWAYS open and follow `{cypilot_path}/.core/skills/cypilot/SKILL.md` FIRST WHEN {cypilot_mode} is `off`

**Type**: Analysis

ALWAYS open and follow `{cypilot_path}/.core/requirements/execution-protocol.md` FIRST

ALWAYS open and follow `{cypilot_path}/.core/requirements/code-checklist.md` WHEN user requests analysis of code, codebase changes, or implementation behavior (Code mode); WHEN this rule triggers, ALWAYS also open and follow `{cypilot_path}/.core/requirements/bug-finding.md` as the companion defect-search methodology

ALWAYS open and follow `{cypilot_path}/.core/requirements/bug-finding.md` WHEN user requests bug hunting, logic bug review, edge-case search, regression risk analysis, root-cause search in code, or asks to find "all bugs/problems" in code; this direct trigger remains mandatory even when `code-checklist.md` was not the reason the review entered Code mode

ALWAYS open and follow `{cypilot_path}/.core/requirements/consistency-checklist.md` WHEN user requests analysis of documentation/artifact consistency, contradiction detection, or cross-document alignment (Consistency mode)

ALWAYS open and follow `{cypilot_path}/.core/requirements/prompt-engineering.md` WHEN user requests analysis of:
- System prompts, agent prompts, or LLM prompts
- Agent instructions or agent guidelines
- Skills, workflows, or methodologies
- AGENTS.md or navigation rules
- Any document containing instructions for AI agents
- User explicitly mentions `prompt engineering review`, `prompt bug review`, `prompt bugs`, or `instruction quality`

WHEN this rule triggers, ALWAYS also open and follow `{cypilot_path}/.core/requirements/prompt-bug-finding.md` as the companion behavioral defect-search methodology

ALWAYS open and follow `{cypilot_path}/.core/requirements/prompt-bug-finding.md` WHEN user requests bug hunting, hidden failure modes, unsafe behavior, regressions, instruction conflicts, routing defects, or root-cause search in prompts, agent instructions, workflows, skills, or other AI instruction documents; this direct trigger remains mandatory even when `prompt-engineering.md` was not the reason prompt review was selected

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
Modes: Full (default) = deterministic gate → semantic review; Semantic-only = skip deterministic gate; Artifact = template + checklist; Code = code-checklist + bug-finding + design requirements; Prompt review = prompt-engineering + prompt-bug-finding review for instruction documents.
Commands: `/cypilot-analyze`, `/cypilot-analyze semantic`, `/cypilot-analyze --artifact <path>`, `/cypilot-analyze semantic --artifact <path>`.
Prompt review trigger matching is intent-based, not exact-string based. Match intent (for example `prompt engineering review`, `review this prompt for bugs`, `check prompt quality`, or `analyze agent instructions`), and treat equivalent phrasing as triggering prompt review plus the companion `prompt-bug-finding.md` methodology when defect-oriented review is requested. Select prompt review from the request intent and target context; do **not** assume a dedicated prompt-specific public route unless the current host explicitly exposes one. After `execution-protocol.md`, you have `TARGET_TYPE`, `RULES`, `KIND`, `PATH`, and resolved dependencies.
If analysis finds actionable issues, the workflow MUST end by generating two chat-only remediation prompts: a bounded `Fix Prompt` that invokes skill `cypilot` and routes to `/cypilot-generate`, and a broader `Plan Prompt` that invokes skill `cypilot` and routes to `/cypilot-plan`. Both prompts MUST be self-contained final prompts usable in a fresh chat — all findings, paths, and context embedded inline.
For code-review-style requests such as `review my changes`, `review this diff`, `inspect this patch`, or similar review/audit requests, every reported defect, regression risk, or fix recommendation that requires artifact, code, or workflow/instruction changes counts as an actionable issue and therefore MUST trigger both remediation prompts in the same response.

## Context Budget & Overflow Prevention (CRITICAL)
- Budget first: estimate size before loading large docs (for example with `wc -l`) and state the budget for this turn.
- Load only what you use: prefer rules.md Validation and only needed checklist categories; avoid large registries/specs unless required.
- Chunk reads and summarize-and-drop: use `read_file` ranges, summarize each chunk, and keep only extracted criteria.
- Fail-safe: if checks cannot be completed within context, output `PARTIAL` with checkpoint status and resume guidance; do not claim overall PASS.
- Plan escalation: [Phase 0.1](#phase-01-plan-escalation-gate) is mandatory after dependencies load; if budget is exceeded, the agent MUST offer plan escalation before proceeding.

## Mode Detection
- `/cypilot-analyze semantic` or `cypilot analyze semantic` → `SEMANTIC_ONLY=true`; skip Phase 2 and go to Phase 3; semantic review remains mandatory.
- Prompt/instruction review context → `PROMPT_REVIEW=true`; open `prompt-engineering.md` and `prompt-bug-finding.md`; run the 9-layer prompt-engineering review, explicitly search for safe context-reduction opportunities per compact-prompts methodology, run prompt-bug-finding as the behavioral defect-search companion, skip standard Cypilot artifact/code checklist analysis, and use the prompt-review output contract from Phase 4. Do **not** pre-mark traceability, registry, or similar checks as `N/A`; mark `N/A` only when the reviewed document explicitly makes a check inapplicable, otherwise report `FAIL` or `PARTIAL` per the loaded prompt methodologies.
- Otherwise → `SEMANTIC_ONLY=false`, `PROMPT_REVIEW=false`; run full analysis.

## Phase 0: Ensure Dependencies
After `execution-protocol.md`, you have `KITS_PATH`, `TEMPLATE`, `CHECKLIST`, `EXAMPLE`, `REQUIREMENTS`, and `VALIDATION_CHECKS`.

- If `rules.md` loaded: dependencies and validation checks were already resolved; proceed silently.
- If `rules.md` not loaded: ask the user to provide/specify missing `checklist`, `template`, or `example`.
- Code mode additional: load `{cypilot_path}/.core/requirements/code-checklist.md` and `{cypilot_path}/.core/requirements/bug-finding.md`, then ask the user to specify the design artifact if missing.

**MUST NOT proceed** to Phase 1 until all dependencies are available.

Raw-input overflow rule: if the direct user prompt plus all provided files exceeds `500` total lines, the agent MUST NOT continue in direct analysis mode. It MUST route through `/cypilot-plan`, preserve the same request scope, and require the planner to materialize that raw input under `{cypilot_path}/.plans/{task-slug}/input/` before decomposition. The planner MUST obtain explicit user approval before creating that directory or executing the write-capable `{cpt_cmd} --json chunk-input ... --max-lines 300 --threshold-lines 500` command, and MUST pass `--include-stdin` when direct prompt text must be packaged together with provided files. This routing takes precedence over any later single-context bypass check inside planning.

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
- Partial analysis (specific sections/IDs; semantic review still required for the checked scope)
- Semantic-only review (skip deterministic gate, still perform semantic review)
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

Deterministic gate is available only when the current Cypilot configuration and target path support a canonical validator invocation for this target. Treat availability as proven by active config plus CLI support for `{cpt_cmd} --json validate ...`; do **not** infer availability from kit prose, examples, or `format` labels alone.

If deterministic gate is not available, do **not** force `{cpt_cmd} --json validate --artifact {PATH}`; do **not** complete `/cypilot-analyze` from Phase 2 alone; require semantic-only analysis or ask the user to register/provide rules first.

Artifacts:
```bash
{cpt_cmd} --json validate --artifact {PATH}
```
Code:
```bash
{cpt_cmd} --json validate
```
- MUST execute `{cpt_cmd} --json validate` as an actual terminal command BEFORE any semantic review.
- MUST include exit code and JSON `status` / `error_count` / `warning_count` in the response as invocation evidence.
- MUST NOT proceed to Phase 3 until `{cpt_cmd} --json validate` returns `"status": "PASS"`; if FAIL, report issues and STOP.
- MUST NOT produce a validation summary without first showing actual validator output; doing so is `SIMULATED_VALIDATION`.

Language content check (run when `[validation] allowed_content_languages` is configured in `.cypilot-workspace.toml`):
```bash
{cpt_cmd} --json check-language {PATH}
```
- Run AFTER `cpt validate` passes.
- If `check-language` returns violations (`LANG001`): report flagged lines as deterministic gate failures; do NOT proceed to Phase 3.
- Language violations are errors, not warnings; STRICT mode requires `PASS` before Phase 3.

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
STOP semantic review — do not proceed to Phase 3. Continue to Phase 4 and Phase 5 to report the blocking issues and generate the remediation prompts.

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
| `/cypilot-analyze` | RELAXED | MANDATORY | Yes — enough evidence for completed categories; otherwise `PARTIAL` |

STRICT mode: semantic review is MANDATORY; the agent MUST follow `{cypilot_path}/.core/requirements/agent-compliance.md`; the agent MUST provide evidence for each checklist category; the agent MUST NOT skip categories or report bulk PASS; failure to complete semantic review makes the analysis INVALID.

RELAXED mode does **not** permit skipping Phase 3, reporting deterministic-only completion, or treating a missing semantic review as a final completed analysis; it only relaxes how much methodology scaffolding is available when no Cypilot rules are loaded.

If semantic review cannot be completed: document checked categories with evidence, mark incomplete categories with reason, output `PARTIAL`, and include `Resume with /cypilot-analyze semantic after addressing blockers`.

### Semantic Review Content (STRICT mode)

Follow the loaded `rules.md` Validation section.

- [ ] Artifacts: execute rules.md semantic validation using the loaded checklist; load `{cypilot_path}/.gen/AGENTS.md`; check content quality, parent cross-references, naming conventions, placeholder-like content, adapter spec compliance, versioning requirements, and traceability requirements.
- [ ] Code: execute codebase/rules.md traceability + quality validation; load related design artifact(s); check requirement implementation, conventions, tests, required markers, and `[x]` completion in SPEC design.
- [ ] Bug finding (when `bug-finding.md` is loaded): use hotspot mapping, invariant extraction, failure-path exploration, universal bug-class sweep, counterexample construction, and dynamic-escalation guidance to maximize defect recall without claiming full coverage.
- [ ] Prompt bug finding (when `prompt-bug-finding.md` is loaded): use prompt hotspot mapping, invariant extraction, branch and handoff exploration, prompt bug-class sweep, counterexample dialogue construction, and dynamic-validation guidance to maximize defect recall without claiming full coverage.
- [ ] Completeness: no placeholder markers (`TODO`, `TBD`, `[Description]`), no empty sections, all IDs follow required format, all IDs are unique, all required fields are present.
- [ ] Coverage: all parent requirements addressed, all referenced IDs exist, all parent actors/capabilities covered, no orphaned references.
- [ ] Traceability (`FULL`): all requirement / flow / algorithm IDs have code markers, all test IDs have test implementations, markers follow `requirements/traceability.md`, and no stale markers remain.
- [ ] ID uniqueness & format: no duplicate IDs within artifact, no duplicate IDs across system (`cypilot list-ids`), all IDs follow naming convention, all IDs use the correct project prefix.
- [ ] Registry consistency: artifact is registered in artifacts.toml, kind matches, system assignment is correct, and path is correct.

Checkpoint rule for artifacts `>500` lines or multi-turn analysis: after each checklist group, note progress; if context runs low, save completed categories, remaining categories, and current artifact position; on resume, re-read the artifact, verify unchanged, and continue from the checkpoint. Categorize recommendations as **High**, **Medium**, or **Low**.

## Phase 4: Output

Print to chat only; create no files.

If the result contains any actionable issue (`FAIL`, `PARTIAL`, blocking validator errors, or any recommendation that requires artifact, code, or workflow/instruction changes), the agent MUST append both a final `Fix Prompt` section and a final `Plan Prompt` section after the analysis output. This requirement applies equally to artifact analysis, code analysis, PR-style review, and plain-language review requests such as `review my changes`.

Apply `enforceRemediationPrompts` at response finalization: detect actionable findings; require both `Fix Prompt` and `Plan Prompt`; require `Fix Prompt` to appear before `Plan Prompt`; and fail finalization with a clear validation error if either prompt is missing, out of order, or the response ends before both prompt blocks are emitted. An analysis summary alone is not completion. The validation report alone is not completion. The next-step menu alone is not completion.

Both remediation prompts MUST be **self-contained final prompts** usable in a fresh chat without any prior context:
- explicitly contain the sentence `Invoke skill cypilot`
- embed the full issue list inline (severity, file path, line numbers, evidence quotes, root-cause expectation) — do NOT reference "findings above" or any prior chat content
- include the target artifact/code path and kind
- include the analysis status and deterministic gate results (if run)
- state the workflow route (`/cypilot-generate` or `/cypilot-plan`)
- instruct the next agent to fix root causes, update tests/validation where needed, and report results
- the prompt alone must give the next agent everything needed to start work immediately

Prompt-specific routing:
- `Fix Prompt` = direct bounded remediation via `/cypilot-generate`
- `Plan Prompt` = phased or broad remediation via `/cypilot-plan`

### Standard Analysis Output (non-prompt review)
```markdown
## Validation Report

### 1. Protocol Compliance
- Rules Mode: {STRICT|RELAXED}
- Target: {TARGET_TYPE}
- Kind: {KIND}
- Name: {name}
- Path: {PATH}
- Artifact/Code Read: {PATH} ({N} lines)
- Checklist Loaded: {path or "none"} ({N} lines or "n/a")

### 2. Deterministic Gate
- Status: {PASS|FAIL|SKIPPED}
- Invocation: `{cpt_cmd} --json validate [--artifact {PATH}]`
- Exit code: {0|2|SKIPPED}
- Errors: {N}
- Warnings: {N}
- Language check: {PASS|FAIL|SKIPPED (not configured)}
- Notes: {why skipped or blocking validator summary}

### 3. Semantic Review
- This section is mandatory in completed analysis output even when category outcomes include `PASS`, `FAIL`, `PARTIAL`, or `N/A`.
- Checklist Progress:
| Category | Status | Evidence |
|----------|--------|----------|
| {category} | PASS/FAIL/PARTIAL/N/A | {line refs, quotes, or violation description} |

- Categories Summary: Total {N}; PASS {N}; FAIL {N}; PARTIAL {N}; N/A {N}; Unsupported-N/A violations {N}

### 4. Agent Self-Test
- See `## Agent Self-Test (STRICT mode — AFTER completing work)` below and copy its canonical questions into this table; if RELAXED mode uses a justified subset, state that explicitly.
| Question | Answer | Evidence |
|----------|--------|----------|
| {question} | YES/NO | {evidence} |

### 5. Final Status
- Deterministic: {PASS|FAIL|SKIPPED}
- Semantic: {PASS|FAIL|PARTIAL}
- Overall: {PASS|FAIL|PARTIAL}

### 6. Issues (if any)
- **High**: {issue with location}
- **Medium**: {issue with location}
- **Low**: {issue with location}
```

Use these same six section titles in both STRICT and RELAXED standard analysis output. In STRICT mode the titles must match exactly; in RELAXED mode content may be lighter, but do **not** substitute alternate headings such as `## Analysis` or `### Category Review`.

### Prompt Review Output (PROMPT_REVIEW)
`PROMPT_REVIEW=true` does **not** use the standard analysis template above. It MUST use the report format from `prompt-engineering.md` in this exact section order:

1. `Summary`
2. `Context Budget & Evidence`
3. `Compact-Prompts Findings`
4. `Layer Summaries`
5. `Issues Found`
6. `Recommended Fixes`
7. `Verification Checklist`

When `prompt-bug-finding.md` is also loaded, the `Summary` MUST begin with its required status block: `Review status`, `Deterministic gate`, `Scope reviewed`, `Review basis`, `Environment snapshot`, and `Coverage summary`. If the deterministic gate is `SKIPPED`, state why and explicitly state `no validator-backed evidence for this review path`.

Do **not** mark prompt-review checks `N/A` unless the reviewed document explicitly makes them inapplicable. If applicability or hotspot-relevant normative effect remains unresolved, report `FAIL` or `PARTIAL` as required by the loaded prompt methodologies.

### Fix Prompt
(copy-paste into new chat — self-contained, no prior context needed)
```text
Invoke skill `cypilot`.

I need a bounded fix via `/cypilot-generate` for `{PATH}` ({KIND}).

Analysis status: {PASS|FAIL|PARTIAL}
Deterministic gate: {exit code, errors, warnings — or "skipped"}

Issues to fix (source of truth — do not re-discover):
1. **[{severity}]** {file}:{line} — {description}. Evidence: "{quote}". Root cause: {expectation}.
2. **[{severity}]** {file}:{line} — {description}. Evidence: "{quote}". Root cause: {expectation}.
{... all issues}

Fix root causes, update tests/validation where needed, and report a final change summary.
Do not ask me to restate the task unless required inputs are missing.
```

### Plan Prompt
(copy-paste into new chat — self-contained, no prior context needed)
```text
Invoke skill `cypilot`.

I need a phased remediation plan via `/cypilot-plan` for `{PATH}` ({KIND}).

Analysis status: {PASS|FAIL|PARTIAL}
Deterministic gate: {exit code, errors, warnings — or "skipped"}

Issues to remediate (source of truth — do not re-discover):
1. **[{severity}]** {file}:{line} — {description}. Evidence: "{quote}". Root cause: {expectation}.
2. **[{severity}]** {file}:{line} — {description}. Evidence: "{quote}". Root cause: {expectation}.
{... all issues}

Create a phased plan to fix root causes, update tests/validation, and verify each phase.
Do not ask me to restate the task unless required inputs are missing.
```

### Semantic-Only Output (`/cypilot-analyze semantic`)
For non-prompt-review semantic-only analysis, reuse the `Standard Analysis Output (non-prompt review)` six-section schema.

Set `### 2. Deterministic Gate` to `Status: SKIPPED`, `Invocation: not run`, and `Notes: semantic-only invocation`.

Do **not** describe semantic-only findings as deterministic, validator-backed, or tool-validated.

If actionable issues exist in semantic-only mode, append the same final `Fix Prompt` and `Plan Prompt` sections after the semantic analysis output.

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
Issues require remediation. Use one of the generated prompts above as the default handoff.
1. Start a direct fix with skill `cypilot` via the generated `Fix Prompt`
2. Start phased remediation with skill `cypilot` via the generated `Plan Prompt`
3. Re-run analysis after fixes
```
If actionable issues exist, the next-step menu is informational only; `enforceRemediationPrompts` still applies, so the workflow MUST end in the same response with `Fix Prompt` followed by `Plan Prompt` as the final two sections. MUST NOT ask whether the prompts should be generated and MUST NOT defer them to a later user turn.

## State Summary

| State | TARGET_TYPE | Uses Template | Uses Checklist | Uses Design |
|-------|-------------|---------------|----------------|-------------|
| Analysing artifact | artifact | ✓ | ✓ | parent only |
| Analysing code | code | ✗ | ✓ | ✓ |

## Key Principles

- Deterministic gate PASS/FAIL is authoritative when it runs.
- Semantic review is mandatory for any completed analysis; in STRICT mode it also requires evidence-backed verification.
- If the deterministic gate cannot run, do not label overall PASS; use semantic-only output and disclaim reduced rigor.
- Output is chat-only; never create `ANALYSIS_REPORT.md`; keep analysis stateless.
- If deterministic gate fails, STOP and report issues immediately.
- Remediation prompts generated when issues require fixes

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
| If I reported actionable issues, did I include both `Fix Prompt` and `Plan Prompt`? | Final output contains both sections with issue-specific content. |

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
| Fix and Plan prompts included? | YES | Both sections present with issue-specific content |
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
- [ ] Traceability mode determined when applicable
- [ ] Registry consistency verified when applicable
- [ ] Cross-reference scope identified
- [ ] Target exists and readable
- [ ] Deterministic gate executed when available and required, otherwise explicitly marked `SKIPPED` with reason
- [ ] Language content check executed when `allowed_content_languages` is configured, otherwise explicitly marked `SKIPPED (not configured)`
- [ ] ID uniqueness verified (within artifact and across system)
- [ ] Cross-references verified (outgoing and incoming)
- [ ] Traceability markers verified (if `FULL` traceability)
- [ ] Result correctly reported (PASS/FAIL/PARTIAL)
- [ ] Prompt review output follows `prompt-engineering.md` section order and includes the `prompt-bug-finding.md` status block when that methodology is loaded
- [ ] Recommendations provided (if PASS)
- [ ] For outputs with actionable issues, the final-response gate self-check was completed before ending the response
- [ ] Both remediation prompts generated when issues require fixes
- [ ] `Fix Prompt` appears before `Plan Prompt` whenever actionable issues exist
- [ ] Workflow response did not end before the required remediation prompt pair was emitted
- [ ] For code review / `review my changes` requests, any reported fixable finding produced both remediation prompts in the same response
- [ ] Output to chat only
- [ ] Next steps suggested
- [ ] No completed `/cypilot-analyze` path bypassed Phase 3; incomplete semantic review is reported as `PARTIAL` with resume guidance
