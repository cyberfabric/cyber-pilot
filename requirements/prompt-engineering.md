---
cypilot: true
type: requirement
name: Prompt Engineering Review Methodology
version: 1.4
purpose: Systematic methodology for reviewing and improving agent instructions with compact-prompts optimization, interaction UX quality, and router-based decomposition
---

# Prompt Engineering Review Methodology


<!-- toc -->

- [Overview](#overview)
- [Layer Map](#layer-map)
- [L1: Document Classification](#l1-document-classification)
- [L2: Clarity & Specificity](#l2-clarity--specificity)
- [L3: Structure & Organization](#l3-structure--organization)
- [L4: Completeness Analysis](#l4-completeness-analysis)
- [L5: Anti-Pattern Detection](#l5-anti-pattern-detection)
  - [Specification](#specification)
  - [Context & Memory](#context--memory)
  - [Execution & Output](#execution--output)
  - [Interaction UX](#interaction-ux)
  - [Maintainability](#maintainability)
- [L6: Context Engineering](#l6-context-engineering)
- [L7: Testability Assessment](#l7-testability-assessment)
- [L8: User Interaction UX](#l8-user-interaction-ux)
- [L9: Agent Ergonomics](#l9-agent-ergonomics)
- [L10: Improvement Synthesis](#l10-improvement-synthesis)
- [Execution Protocol](#execution-protocol)
- [Integration with Cypilot](#integration-with-cypilot)
- [References](#references)
- [Validation](#validation)

<!-- /toc -->

**Scope**: Any file containing agent instructions — system prompts, skills, workflows, requirements, `AGENTS.md`, and methodologies.

**Out of scope**: This does not provide a “best prompt” template or generate production prompts; it defines a review method and report format.

**Companion methodology**: for bug hunting, hidden failure modes, unsafe behavior, regressions, instruction conflicts, or root-cause analysis in prompts and agent instructions, also use `prompt-bug-finding.md` as the behavioral defect search procedure.

## Overview

Agent instructions are executable policy for agent behavior and user interaction. Review them like software: classify the artifact, test for ambiguity, verify structure, identify missing contracts, detect anti-patterns, manage context budget, confirm testability, check interaction UX, check model ergonomics, then synthesize prioritized fixes.

**High-priority rule**: for analysis and generation work, aggressively reduce loaded context whenever behavior, determinism, constraints, safety, output contracts, and recovery rules remain intact.

**CRITICAL interaction UX rule**: whenever instructions ask the user for input, confirmation, or a choice, review whether the prompt explains why the input is needed, what the user is expected to provide, what each option leads to, which option is suggested in the current context, and exactly how the user should reply.

## Layer Map

| Layer | Question |
|---|---|
| L1 | What kind of instruction document is this? |
| L2 | Are the instructions explicit and unambiguous? |
| L3 | Is the document scannable and cognitively manageable? |
| L4 | What required information is missing? |
| L5 | Which prompt anti-patterns are present? |
| L6 | Is context loaded, compressed, and preserved correctly? |
| L7 | Can compliance be verified? |
| L8 | Are user-facing questions, options, and transitions easy to understand and act on? |
| L9 | Does the document align with LLM strengths and limits? |
| L10 | What should be fixed first? |

## L1: Document Classification

**Primary type**: identify whether the document is a `System Prompt`, `Skill/Tool`, `Workflow`, `Requirement`, `AGENTS.md`, `Template`, or `Checklist`.

**Instruction scope**: mark whether the rules are `Global`, `Conditional` (`WHEN`-gated), or `Task-Specific`.

**Audience**: determine whether it targets a `Single Agent Type`, is `Agent-Agnostic`, or is `Hybrid`.

**Dependencies**: list referenced docs, detect circular dependencies, confirm dependencies exist and are accessible, and verify version compatibility.

**Preconditions**: record what must already be true, what context must be loaded first, and what tools or capabilities are assumed.

## L2: Clarity & Specificity

**Ambiguity scan**: flag vague qualifiers (`appropriate`, `relevant`, `suitable`, `proper`, `good`), subjective terms (`better`, `improved`, `professional`, `clean`), undefined references (`the above`, `this`, `that`, `it`), implicit assumptions, and weasel words (`might`, `could`, `possibly`, `generally`, `usually`).

**Specificity**: every instruction should state **WHO** acts, **WHAT** happens, **WHEN** it triggers, **HOW** it is executed, and **WHY** it matters.

**Quantification**: prefer explicit counts, limits, and thresholds over words like `few`, `brief`, or `many`.

**Sentence quality**: use imperative mood, prefer active voice, and keep to one action per sentence when possible.

**Framing**: prefer positive requirements; if a negative is necessary, pair it with the required alternative; distinguish `MUST NOT` / `NEVER` from `SHOULD NOT` / `AVOID`.

**Priority**: critical rules are marked (`MUST`, `REQUIRED`, `CRITICAL`), optional rules are marked (`MAY`, `OPTIONAL`, `CONSIDER`), and importance hierarchy is obvious.

**Compact clarity rules**: use short imperative sentences; front-load trigger + action + object (`WHEN X, do Y to Z`); use explicit nouns and verbs; replace vague wording with measurable limits or decision rules; keep stable terminology; remove filler and repeated restatements; prefer bullets, tables, and checklists over narrative; keep only examples that change behavior or clarify edge cases.

## L3: Structure & Organization

**Hierarchy quality**: headings follow logical `H1 -> H2 -> H3` order, section titles are descriptive, related content is grouped together, and the document uses inverted-pyramid ordering where important content appears early.

**Chunking**: long sections are split into digestible units; lists replace enumeration paragraphs; tables handle structured comparison; code blocks are reserved for commands and examples.

**Navigation aids**: long docs include a TOC, related sections are cross-linked, boundaries are visually clear, and a summary or overview appears near the start.

**Cognitive load**: keep one concept per paragraph, avoid nested conditionals beyond two levels, express complex logic as decision trees or ordered steps, and define abbreviations on first use.

**Visual hierarchy**: emphasize important terms with bolding, keep code and IDs in backticks, make warnings visually distinct, and clearly demarcate examples.

**Redundancy check**: remove contradictions, mark intentional repetition as intentional, and replace duplication with cross-references.

## L4: Completeness Analysis

**Identity & purpose**: verify a purpose statement, scope boundary, and success criteria.

**Operational elements**: verify entry conditions, exit conditions, response-completion gates, required terminal sections or handoff blocks, error handling, clarification strategy, option semantics, and edge-case guidance.

**Integration elements**: dependencies are listed, outputs are defined, handoffs to other workflows are specified, and any required final prompt pair or terminal block ordering is explicit, and any required user decision point explains what happens after each option.

**Gap analysis**: ask what happens if the agent does not understand, preconditions are not met, multiple interpretations exist, external resources are unavailable, or the user does not understand what a requested choice means.

**Scenario coverage**: ensure the happy path, error paths, recovery procedures, escalation triggers, user-decision branches, and completion branches are documented; check whether the response can terminate after a summary, validation block, or next-step menu even though required final sections are still missing.

## L5: Anti-Pattern Detection

### Specification

| Code | Detect when |
|---|---|
| `AP-VAGUE` | Instructions rely on common sense, ambiguity, or implicit knowledge. |
| `AP-MISSING-FORMAT` | Output format is not specified. |
| `AP-MISSING-ROLE` | Needed persona or expertise is undefined. |
| `AP-MISSING-CONSTRAINTS` | Length, scope, style, or boundary constraints are missing. |
| `AP-OVERLOAD` | Too many tasks are packed into one instruction. |
| `AP-MICROMANAGE` | Low-level detail constrains execution without improving outcomes. |
| `AP-LONG-WINDED` | The same rule is padded with prose, repetition, or bloated examples. |
| `AP-CONFLICTING` | Requirements contradict one another. |
| `AP-IMPOSSIBLE` | Not all requirements can be satisfied simultaneously. |
| `AP-NO-ROUTER` | Multi-step or branching instructions lack a compact router/index that says what may load next and when. |
| `AP-OVERSIZED-RESOURCE` | A loadable instruction resource, module, or deliberate slice exceeds `50` lines. |
| `AP-MONOLITHIC-STEP` | Multiple steps, branches, or modes are bundled into one loadable unit instead of decomposed into routeable modules. |

### Context & Memory

| Code | Detect when |
|---|---|
| `AP-CONTEXT-BLOAT` | Excessive context dilutes priorities. |
| `AP-SYSTEM-PROMPT-BLOAT` | A system prompt violates `6.1.3`: always-on text is `> 200` lines or embeds conditional blocks that should be modular. |
| `AP-CONTEXT-STARVATION` | Critical context is missing. |
| `AP-CONTEXT-DRIFT` | Required context may be lost through compaction or long sessions. |
| `AP-BURIED-PRIORITY` | Critical rules are hidden instead of surfaced early and scannably. |
| `AP-VAGUE-REFERENCE` | References such as `the above` or `this` have no clear antecedent. |
| `AP-ASSUMES-MEMORY` | The document assumes the agent will remember earlier turns. |
| `AP-NO-CHECKPOINT` | Long workflows lack state checkpoints. |
| `AP-IMPLICIT-STATE` | State changes are not explicitly tracked. |

### Execution & Output

| Code | Detect when |
|---|---|
| `AP-NO-VERIFICATION` | No self-check or validation step exists. |
| `AP-FALSE-COMPLETION` | The prompt allows the response to end after a summary, validation result, next-step menu, or checkpoint-looking block even though required final sections or handoff prompts are still missing. |
| `AP-MISSING-TERMINAL-BLOCK` | Required final prompt blocks, handoff sections, or terminal block ordering are unspecified or only implied. |
| `AP-SKIP-ALLOWED` | Critical steps are easy to skip. |
| `AP-SILENT-FAIL` | Failures are not surfaced to the user. |
| `AP-INFINITE-LOOP` | Retry loops can stall indefinitely. |
| `AP-HALLUCINATION-PRONE` | The prompt encourages guessing. |
| `AP-NO-UNCERTAINTY` | The agent is not allowed to say `I don't know`. |
| `AP-NO-SOURCES` | Claims need not be cited or verified. |

### Interaction UX

| Code | Detect when |
|---|---|
| `AP-UNEXPLAINED-ASK` | The prompt asks the user for information or confirmation without stating why it is needed or what good input looks like. |
| `AP-AMBIGUOUS-OPTIONS` | Options or reply labels are hard to distinguish, use unclear wording, or hide important differences. |
| `AP-HIDDEN-CONSEQUENCE` | The user is asked to choose before the prompt explains what each option will do next. |
| `AP-NO-SUGGESTED-OPTION` | A decision point lacks a suggested or recommended path even though the current context clearly favors one option. |
| `AP-GENERIC-SUGGESTION` | Suggested follow-ups or recommended options are generic instead of being anchored to the current request, state, or prior result. |
| `AP-OPTION-OVERLOAD` | Too many choices, too much prose, or mixed decision scopes increase cognitive load unnecessarily. |

### Maintainability

| Code | Detect when |
|---|---|
| `AP-HARDCODED` | Magic strings or numbers appear instead of parameters. |
| `AP-DRY-VIOLATION` | The same rule appears in multiple places. |
| `AP-NO-VERSION` | Breaking changes are not versioned. |
| `AP-TANGLED` | Editing one area breaks unrelated behavior. |

## L6: Context Engineering

**Content audit**: identify compressible sections, redundant sections, content that should load conditionally, and approximate size. Optional sizing helpers: `wc -l path/to/document.md` for line count and a simple word-count proxy for rough token estimation.

**Information priority**: confirm the most critical instructions appear in the first `20%` of the document, examples and details can be truncated without losing core behavior, and conditional content is clearly marked for selective loading.

**CRIT — system prompt budget**: if the reviewed document is a `System Prompt`, its always-on portion MUST NOT exceed `200` lines. Count the fully assembled always-on text, including headings, blank lines, and lists. Content moved into on-demand modules does not count. PASS if `<= 200`; FAIL if `> 200`.

**If the system prompt exceeds budget**: keep only always-on invariants (identity, safety, tool rules, output contract); move task-specific or conditional material into modules; add explicit loading rules via `AGENTS.md`, workflow `WHEN` clauses, or ordered steps. Recommended organizations: module index + conditional loading, phase-based chain loading, or mode-based branching. Acceptance: prompt `<= 200`, optional detail externalized, triggers are explicit, and next modules are obvious.

**CRIT — workflow/skill/methodology overflow control**: any document that tells the agent to load more files MUST define budget, gating, chunking, summarization, and a fail-safe. Minimum controls: max files / max total lines or a mandatory summarize-and-drop policy; rules for when a dependency should load; partial loading by TOC/section/range instead of whole-file default; conversion of loaded text into an operational summary; and a stop / checkpoint / ask-user fallback when budget would be exceeded.

**CRIT — loadable resource budget**: every loadable instruction resource MUST be `<= 50` lines.

A **loadable instruction resource** is any file, module, or deliberate contiguous slice that the agent is expected to load as one active execution unit at runtime. Concrete test: a unit qualifies as a loadable instruction resource only when the agent must ingest it whole at runtime — invoked as a single programmatic load or import (for example a `Read` of the whole file, an `ALWAYS open and follow {path}` directive, a workflow `WHEN`-clause spec load, or a router pointing at the file as the next-load target). Examples that ARE loadable instruction resources: a workflow phase file, a skill `SKILL.md` actively loaded by the protocol guard, a router-referenced module, a checklist file ingested whole during a phase, an agent prompt opened in full.

**Exemptions**: methodology documents, reference guides, multi-chapter specifications, ADRs, design documents, and other non-runtime documentation are exempt from the `<= 50` line cap UNLESS they contain runtime execution sequences or agent-loadable instruction blocks (e.g., `WHEN`-clause specs, `ALWAYS open and follow` directives, or router targets). When such a document carries runtime instructions inline, the runtime block itself is the loadable resource and MUST be either (a) `<= 50` lines, or (b) extracted into its own routeable module so the runtime slice satisfies the cap.

**Measurement rule**: count headings, blank lines, lists, and examples within the runtime-loadable unit (do not count surrounding non-runtime prose in an exempted document). PASS only if every runtime-loadable unit is `<= 50`; FAIL if any runtime unit exceeds `50`.

**Migration rule**: during brownfield review or refactor, an oversized legacy prompt may be inspected only through bounded slices `<= 50` lines each to plan decomposition. That temporary inspection does not make the legacy prompt compliant; the legacy document remains non-compliant until decomposed, and the compliant target state is routeable resources `<= 50` lines each.

**CRIT — router / lazy-loading decomposition contract**: if behavior spans multiple steps, branches, modes, or recovery paths, the prompt MUST be decomposed into a compact router plus on-demand modules. The router decides what loads next; each module contains only one active branch, one active step, or one tightly related decision/recovery unit. The router MUST NOT inline full instructions for sibling branches or later steps that are not yet active.

| Module type | Purpose | MUST contain | MUST NOT contain |
|---|---|---|---|
| Router / index | Entry point and branch selection | purpose, branch names, explicit triggers, next-file mapping, stop/escalate rule | full downstream step-by-step content for multiple branches |
| Step module | One execution step | goal, prerequisites, actions, outputs, next route or stop condition | instructions for unrelated steps, future phases, or sibling branches |
| Decision module | One user/system choice point | options, consequences, suggested path, reply contract, next-file mapping | hidden consequences, mixed decision scopes, or unrelated execution detail |
| Shared invariant module | Reusable always-on constraints | invariants reused by multiple branches, stable definitions, non-branching guardrails | branch-local sequencing or large optional guidance |
| Recovery module | Error, retry, or resume path | failure trigger, recovery actions, return route | normal-path bulk instructions |

**Preferred representation**: use compact tables for router/index data and short ordered lists for execution steps. Use the smallest format that preserves deterministic routing, obvious next loads, and unambiguous branch boundaries.

**Mandatory loading protocol**:
1. Load the router or entry module first.
2. Resolve the active branch, mode, or step from explicit triggers before loading any downstream module.
3. Load exactly one downstream module at a time unless two modules are both mandatory for the same immediate action and still respect the `<= 50`-line rule.
4. After each module, retain only a short operational summary plus required state; drop unrelated raw text.
5. Load the next module only from an explicit `next`, `when`, `if`, or decision mapping.
6. Recovery, review, and completion modules load only when their trigger fires; they MUST NOT stay always-on by default.
7. Resumption MUST restart from the router or checkpoint plus the next required module, not from chat memory alone.

**Decomposition acceptance**: PASS only if a cold-start agent can begin from the router, determine the next module without guessing, load one `<= 50`-line unit at a time, and complete the active path without reading sibling branches first.

**Evidence requirement**: the review output lists loaded files with sizes and sections/ranges, plus the chosen budget and whether it was respected or which fail-safe path was taken.

**HIGH-priority compact-prompts review**: answer this question explicitly — *What can be removed, externalized, deduplicated, summarized, or conditionally loaded without changing required behavior?* Required optimization loop: classify content as always-on invariant / conditional guidance / example-reference / archival detail; keep only minimum viable always-on context; externalize conditional detail into triggered modules; compress prose into bullets, tables, and decision rules; deduplicate to one canonical statement per rule; keep the smallest example set that still prevents ambiguity; then verify every `MUST`, `MUST NOT`, trigger, threshold, format rule, and fail-safe still exists.

**Compaction checks**: split always-on vs on-demand content explicitly; replace repeated narrative with one rule plus reference; convert branching prose into decision tables or ordered steps; prefer `WHEN` / `IF` / `ONLY IF` triggers over buried clauses; surface critical priorities early; keep output formats and acceptance criteria close to dependent instructions; remove decorative wording; prefer short labels with one-sentence explanations over dense paragraphs.

**Lossless-first compression order**: remove noise in this order unless the document proves a different order is safer: filler/courtesy; repeated framing; hedging and weak qualifiers; decorative transitions; duplicated examples; archival detail; optional explanatory prose. `MUST NOT` remove constraints, thresholds, triggers, fail-safes, or required terminal blocks before higher-noise categories are exhausted.

**Controlled shorthand**: compressed phrasing such as `X -> Y`, `IF X: Y`, short labels, or omitted connectives is acceptable only when a fresh agent can still interpret the rule without guessing. Use one stable compressed label per concept and define any non-obvious shorthand once near first use.

**Dense packet formats**: for operational content, prefer compact units such as one line = one action, one decision rule, or one problem + fix. Favor field-like formats such as `Goal:`, `Risk:`, `Do:`, `Do not:`, and `Proof:` over narrative when they preserve full meaning.

**Decompression test**: after compaction, verify that a reviewer can restate each compressed rule in full plain language without inventing missing constraints. Mark `FAIL` if compression depends on hidden context, unstable shorthand, or memory of earlier turns.

**Noise-floor rule**: remove ritual acknowledgments, motivational padding, repeated reassurance, conversational filler, and meta-commentary unless they change behavior, reduce execution risk, or prevent ambiguity.

**Response-shape budgets**: define expected compactness by output type, not only by overall document size. Prefer explicit target shapes such as short operational answer, one-issue-per-line review comment, goal/state/blocker/next status update, or minimal self-contained handoff prompt instead of generic instructions like `be concise`.

**Prompt-writing recommendations**: state role, task, constraints, then output contract unless a different dependency order is necessary; use one stable name per artifact, mode, workflow, or variable; keep thresholds numeric (`<= 200 lines`, `max 3 iterations`, `read 1 file at a time`); pair forbidden behavior with the required alternative; make scope explicit (`In scope`, `Out of scope`, `Do not infer`); prefer concrete condition-action phrasing; avoid nested parentheticals and stacked caveats when a sub-list is clearer.

**Compactness examples**:

| Anti-pattern | Before | After |
|---|---|---|
| `AP-LONG-WINDED` | `When you are in a situation where context may be running low...` | `WHEN context runs low, summarize loaded instructions into a short operational checklist and drop the raw text.` |
| `AP-BURIED-PRIORITY` | `Use good judgment... before writing anything make sure they have approved it.` | `MUST NOT write files before explicit user confirmation.` |

**Severity guidance**: missed safe compaction opportunities are `HIGH` when they affect always-on prompts or frequently loaded instruction files; compaction that removes required behavior, constraints, or recovery steps is a `FAIL`.

**Lifecycle**: specify what loads at start, what loads on demand, what can be summarized when context is low, what must never be dropped, how critical state survives compaction, what belongs in files vs working memory, and how context loss is detected and recovered.

**Attention management**: repeat or reinforce critical instructions, visually emphasize important sections, keep guardrails in a dedicated section, avoid too many competing instructions, group related rules, and separate low-priority content.

## L7: Testability Assessment

**Binary verification**: for each instruction, determine whether the agent did it, did it correctly, and did it completely.

**Observable outputs**: require visible artifacts, visible intermediate steps, and explicit compliance evidence.

**Built-in checks**: include validation criteria, a pre-completion self-check, checklist formatting for critical steps, and proof-of-work requirements when appropriate.

**Interactive UX checks**: when the document asks the user to choose or confirm, verify that tests can confirm all of the following from the emitted prompt alone: why the input is needed, what reply format is accepted, what each option does, and whether any suggested option is anchored to the current context.

**When a workflow requires terminal prompts or final handoff blocks, the pre-completion self-check should verify that those exact blocks were emitted before the response may end.**

**External verification**: prefer rules that can be checked by automated tools, another agent, or a human reviewer.

**Happy-path tests**: provide at least one correct example, with full input-to-output trace and key edge cases.

**Negative tests**: show what not to do, what incorrect outputs look like, and how to recover.

## L8: User Interaction UX

**User-facing prompts**: verify that every user-facing prompt explains why the input is needed, what the user is expected to provide, what each option leads to, which option is suggested in the current context, and exactly how the user should reply.

**Goal-oriented questions**: verify that each question, confirmation gate, or next-step menu moves the user toward a concrete outcome and states why this question is being asked now.

**Capability and limit framing**: verify that when the user's choice depends on system capabilities, constraints, or uncertainty, the prompt explains what the system can do, what it cannot do, and why the recommendation is appropriate.

**Ask only for missing information**: verify that the prompt does not ask the user to restate context already available, and that complex requests are broken into manageable steps rather than requesting all possible details at once.

**Option clarity**: verify that options or reply labels are easy to distinguish, use clear wording, and do not hide important differences.

**Consequence explanation**: verify that the user is not asked to choose before the prompt explains what each option will do next.

**Suggested options**: verify that a decision point has a suggested or recommended path when the current context clearly favors one option.

**Generic suggestions**: verify that suggested follow-ups or recommended options are anchored to the current request, state, or prior result, not generic.

**Option overload**: verify that too many choices, too much prose, or mixed decision scopes do not increase cognitive load unnecessarily.

**Reply contract**: verify that the prompt tells the user exactly how to answer (`1`, `2`, `yes`, `no`, `approve all`, or specific edits) so the reply format never has to be guessed.

**Fallback quality**: verify that confusion or unsupported input leads to a targeted clarifying question, a small set of clear alternatives, or a nearest-supported path instead of a dead-end response.

**Transition clarity**: verify that shifts between stages (for example clarification -> action, or validation -> next steps) are explicitly communicated so the user understands what changed and why.

## L9: Agent Ergonomics

**Capability match**: ensure instructions do not ask impossible things, break complex reasoning into steps, and request output formats the model is good at (`JSON`, `Markdown`, etc.).

**Training alignment**: use familiar prompt patterns, an appropriate role/persona, and a style consistent with effective prompting.

**Graceful degradation**: define what happens on partial failure, whether the agent can recover without intervention, and when it must ask for help.

**Hallucination prevention**: require verification or citation, permit uncertainty, mark speculation, and use external tools for factual queries.

**Iterative compatibility**: support iterative improvement, define how feedback is incorporated, and keep partial success actionable.

**Conversation compatibility**: support multi-turn use, clarification requests, and mid-task scope changes.

## L10: Improvement Synthesis

**Severity**:

| Severity | Criteria | Action |
|---|---|---|
| `CRITICAL` | Blocks task completion | Fix immediately |
| `HIGH` | Causes incorrect or inconsistent output | Fix before deployment |
| `MEDIUM` | Reduces quality or efficiency | Fix next iteration |
| `LOW` | Minor improvement opportunity | Backlog |

**Effort**:

| Effort | Criteria |
|---|---|
| `TRIVIAL` | Single word or phrase change |
| `SMALL` | Single section rewrite |
| `MEDIUM` | Multiple section changes |
| `LARGE` | Document restructure |

**Quick wins**: list `CRITICAL` plus `TRIVIAL` / `SMALL` fixes, rank by impact-to-effort ratio, and note dependencies between fixes. For user-facing prompts, prioritize fixes that reduce user confusion at decision points before cosmetic wording changes.

**Strategic improvements**: list structural changes, refactoring opportunities, and missing sections or companion docs.

**Per-fix guidance**: provide `What`, `Where`, `Why`, `How`, and `Verify`. For interaction UX fixes, include the intended user mental model, the suggested default path, and the exact outcome text that should become clearer.

**Testing plan**: define tests for critical fixes, regression checks for preserved behavior, and validation that fixes do not conflict.

## Execution Protocol

**Prerequisites**: full document text is accessible; related documents are available for cross-reference; document purpose and context are understood; example outputs are available when applicable.

**Order**: execute layers `1 -> 10` in sequence. Review completion requires the required report format plus a fully evaluated verification checklist. After each layer, checkpoint findings before continuing.

**Work budgeting**: prefer bounded review passes over elapsed time. Size the review with `wc -l path/to/document.md` and use this pass budget:

| Document Size | L1-L3 | L4-L6 | L7-L9 | L10 |
|---|---|---|---|---|
| Small (`< 500`) | 1 pass | 1 pass | 1 pass | 1 synthesis pass |
| Medium (`500-2000`) | 1-2 passes | 1-2 passes | 1-2 passes | 1 synthesis pass |
| Large (`> 2000`) | 2 passes | 2 passes | 2 passes | 1-2 synthesis passes |

If a layer exceeds its pass budget, note blockers and continue; incomplete analysis is better than no analysis.

**Error handling**:

- `Partial layer`: document completed checks, blockers, mark the layer `PARTIAL`, then proceed.
- `Missing information`: if dependencies are inaccessible, analyze what is available; if examples are missing, flag Layer 7 and recommend examples; if context is unclear, ask the user or make assumptions explicit.
- `Recovery`: default to a chat-only checkpoint; save `review-checkpoint-{document}-{layer}.md` only with explicit user request or approval; on resume, read the available checkpoint source, verify the document is unchanged, and continue.

**Output format**: produce a report with these sections in order: `Summary`, `Context Budget & Evidence`, `Compact-Prompts Findings`, `Layer Summaries`, `Issues Found` (Critical / High / Medium / Low tables), `Recommended Fixes` (Immediate / Next Iteration / Backlog), and `Verification Checklist`.

**Required report fields**:

- `Summary`: document type, overall quality (`GOOD | NEEDS_IMPROVEMENT | POOR`), critical issue count, total issue count. When paired with `prompt-bug-finding.md`, start `Summary` with that methodology's required status block, including `Review status` and `Deterministic gate: PASS | FAIL | SKIPPED`; if the gate is `SKIPPED`, state why and explicitly state `no validator-backed evidence for this review path` before the quality counts.
- `Context Budget & Evidence`: budget, inputs loaded (`path — size — sections/ranges`), and overflow handling.
- `Compact-Prompts Findings`: safe reductions found, content kept intentionally, deferred or blocked opportunities, and a behavior-preservation check confirming `MUST`, `MUST NOT`, triggers, thresholds, output rules, and fail-safes remain intact.
- `Layer Summaries`: cover every layer explicitly; when the document contains user-facing questions, confirmations, or menus, include dedicated interaction-UX findings covering why the prompt asks, option clarity, option outcomes, suggested-path quality, reply format, and fallback behavior.
- `Verification Checklist`: all critical issues addressed; no new issues introduced; examples/tests updated when needed; context overflow prevention evidenced; compact-prompts findings reported explicitly; and, when the reviewed document requires terminal response blocks, the checklist explicitly states whether false completion paths were ruled out.

When the deterministic gate is `SKIPPED`, do not describe semantic review, checklist review, or manual inspection as deterministic, validator-backed, or tool-validated unless actual validator or tool output exists.

**N/A rule**: mark a check `N/A` only when the document explicitly makes it inapplicable; otherwise mark `FAIL` or `PARTIAL` and explain what is missing.

## Integration with Cypilot

- Use this methodology for semantic validation and generation of instruction documents.
- Keep `AGENTS.md` and related adapters aligned with these rules.
- Pair this methodology with `prompt-bug-finding.md` when the task is defect-oriented.

## References

This document is the authoritative working method. External sources informed its design, but the prompt surface here stays intentionally compact.

**Companion methodology**: `prompt-bug-finding.md` for bug hunting, hidden failure modes, unsafe behavior, regressions, instruction conflicts, or root-cause analysis in prompts and agent instructions.

## Validation

Review is complete when:

- [ ] All 10 layers analyzed
- [ ] All checklist items attempted (`PASS`, `FAIL`, `PARTIAL`, or explicit `N/A`)
- [ ] Issues categorized by severity and effort
- [ ] Fixes prioritized by impact/effort
- [ ] Implementation guidance provided
- [ ] Safe compact-prompts opportunities identified and prioritized for prompt/instruction documents
- [ ] Compact-prompts findings reported explicitly in the review output
- [ ] For every user-facing interaction point, question purpose, option clarity, option outcomes, suggested-path quality, reply format, and fallback clarity were checked explicitly
- [ ] Required completion gates, terminal blocks, and false-completion paths were checked explicitly when the document defines a final response contract
- [ ] Verification plan included
