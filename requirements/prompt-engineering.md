---
fdd: true
type: requirement
name: Prompt Engineering Review Methodology
version: 1.0
purpose: Systematic methodology for reviewing and improving agent instructions
---

# Prompt Engineering Review Methodology

**Scope**: Any file containing agent instructions — system prompts, skills, workflows, requirements, AGENTS.md, methodologies

---

## Overview

This methodology provides a systematic approach to reviewing and improving any agent instruction document. Each layer analyzes a specific aspect of prompt quality, building toward actionable improvements.

**Core Principle**: Agent instructions are code for human cognition. They require the same rigor as software engineering — clear specifications, explicit contracts, testable outcomes, and systematic debugging.

---

## Table of Contents

1. [Layer 1: Document Classification](#layer-1-document-classification)
2. [Layer 2: Clarity & Specificity](#layer-2-clarity--specificity-analysis)
3. [Layer 3: Structure & Organization](#layer-3-structure--organization)
4. [Layer 4: Completeness Analysis](#layer-4-completeness-analysis)
5. [Layer 5: Anti-Pattern Detection](#layer-5-anti-pattern-detection)
6. [Layer 6: Context Engineering](#layer-6-context-engineering)
7. [Layer 7: Testability Assessment](#layer-7-testability-assessment)
8. [Layer 8: Agent Ergonomics](#layer-8-agent-ergonomics)
9. [Layer 9: Improvement Synthesis](#layer-9-improvement-synthesis)
10. [Execution Protocol](#execution-protocol)
11. [Quick Reference: Anti-Pattern Codes](#quick-reference-anti-pattern-codes)
12. [Integration with FDD](#integration-with-fdd)
13. [References](#references)

---

## Analysis Layers

```
Layer 1: Document Classification     → What type of instruction is this?
Layer 2: Clarity & Specificity       → Is it unambiguous?
Layer 3: Structure & Organization    → Is it scannable and navigable?
Layer 4: Completeness Analysis       → What's missing?
Layer 5: Anti-Pattern Detection      → What common mistakes are present?
Layer 6: Context Engineering         → Is context managed efficiently?
Layer 7: Testability Assessment      → Can we verify compliance?
Layer 8: Agent Ergonomics            → Is it agent-friendly?
Layer 9: Improvement Synthesis       → What should change?
```

---

# Layer 1: Document Classification

**Goal**: Identify document type and applicable standards

## 1.1 Document Type Identification

### 1.1.1 Primary Type

- [ ] **System Prompt**: Core identity, capabilities, constraints
- [ ] **Skill/Tool**: Specific capability with invocation pattern
- [ ] **Workflow**: Multi-step process with phases
- [ ] **Requirement**: Specification that other documents must follow
- [ ] **AGENTS.md**: Navigation and context loading rules
- [ ] **Template**: Structure for generating artifacts
- [ ] **Checklist**: Validation criteria

### 1.1.2 Instruction Scope

- [ ] **Global**: Applies to all agent interactions
- [ ] **Conditional**: Applies when specific conditions met (WHEN clauses)
- [ ] **Task-Specific**: Applies only during specific task execution

### 1.1.3 Target Audience

- [ ] **Single Agent Type**: Designed for specific agent (Claude, GPT, etc.)
- [ ] **Agent-Agnostic**: Works across different LLM agents
- [ ] **Hybrid**: Core is agnostic, with agent-specific sections

## 1.2 Context Requirements

### 1.2.1 Dependencies

- [ ] List all referenced documents
- [ ] Identify circular dependencies
- [ ] Check if dependencies exist and are accessible
- [ ] Verify version compatibility

### 1.2.2 Preconditions

- [ ] What must be true before this document applies?
- [ ] What context must be loaded first?
- [ ] What tools/capabilities are assumed available?

---

# Layer 2: Clarity & Specificity Analysis

**Goal**: Evaluate how unambiguous the instructions are

## 2.1 Language Quality

### 2.1.1 Ambiguity Detection

Scan for ambiguous language patterns:

- [ ] **Vague qualifiers**: "appropriate", "relevant", "suitable", "proper", "good"
- [ ] **Subjective terms**: "better", "improved", "professional", "clean"
- [ ] **Undefined references**: "the above", "this", "that", "it" without clear antecedent
- [ ] **Implicit assumptions**: Instructions that assume context not explicitly stated
- [ ] **Weasel words**: "might", "could", "possibly", "generally", "usually"

### 2.1.2 Specificity Check

For each instruction, verify:

- [ ] **WHO** performs the action (agent, user, system)?
- [ ] **WHAT** exactly should be done?
- [ ] **WHEN** should it be done (trigger condition)?
- [ ] **HOW** should it be done (method/approach)?
- [ ] **WHY** is it necessary (helps agent prioritize)?

### 2.1.3 Quantification

- [ ] Are quantities specified where applicable? ("3 examples" vs "a few examples")
- [ ] Are limits defined? ("max 100 words" vs "brief")
- [ ] Are thresholds explicit? ("if more than 5 errors" vs "if many errors")

## 2.2 Instruction Clarity

### 2.2.1 Imperative Language

- [ ] Instructions use imperative mood ("Do X" not "You should do X")
- [ ] Active voice preferred over passive
- [ ] One action per sentence where possible

### 2.2.2 Positive vs Negative Framing

- [ ] Prefer "DO this" over "DON'T do that"
- [ ] If negative, include positive alternative
- [ ] MUST NOT / NEVER clearly distinguished from SHOULD NOT / AVOID

### 2.2.3 Priority Indicators

- [ ] Critical instructions marked (MUST, REQUIRED, CRITICAL)
- [ ] Optional instructions marked (MAY, OPTIONAL, CONSIDER)
- [ ] Hierarchy of importance clear

---

# Layer 3: Structure & Organization

**Goal**: Evaluate document navigability and cognitive load

## 3.1 Information Architecture

### 3.1.1 Hierarchy Quality

- [ ] Logical heading hierarchy (H1 → H2 → H3)
- [ ] Section titles are descriptive and scannable
- [ ] Related content grouped together
- [ ] Important content early, details later (inverted pyramid)

### 3.1.2 Chunking

- [ ] Long sections broken into digestible subsections
- [ ] Lists used for enumerations (not paragraphs)
- [ ] Tables used for structured comparisons
- [ ] Code blocks used for commands/examples

### 3.1.3 Navigation Aids

- [ ] Table of contents for long documents
- [ ] Internal links between related sections
- [ ] Clear section boundaries (horizontal rules)
- [ ] Summary/overview at start

## 3.2 Cognitive Load Management

### 3.2.1 Information Density

- [ ] One concept per paragraph
- [ ] Avoid nested conditionals beyond 2 levels
- [ ] Complex logic presented as decision trees/flowcharts
- [ ] Abbreviations defined on first use

### 3.2.2 Visual Hierarchy

- [ ] Important terms **bolded**
- [ ] Code/IDs in `backticks`
- [ ] Warnings/cautions visually distinct (⚠️, boxes)
- [ ] Examples clearly demarcated

### 3.2.3 Redundancy Check

- [ ] No contradictory instructions
- [ ] Intentional repetition marked as such
- [ ] Cross-references used instead of duplication

---

# Layer 4: Completeness Analysis

**Goal**: Identify missing information

## 4.1 Essential Elements

### 4.1.1 Identity & Purpose

- [ ] **Purpose statement**: Why does this document exist?
- [ ] **Scope definition**: What does it cover and NOT cover?
- [ ] **Success criteria**: How do we know instructions were followed correctly?

### 4.1.2 Operational Elements

- [ ] **Entry conditions**: When/how to activate these instructions
- [ ] **Exit conditions**: When/how to deactivate or complete
- [ ] **Error handling**: What to do when things go wrong
- [ ] **Edge cases**: Unusual situations addressed

### 4.1.3 Integration Elements

- [ ] **Dependencies listed**: Other docs/tools required
- [ ] **Outputs defined**: What should be produced
- [ ] **Handoffs specified**: How to pass control to other workflows

## 4.2 Missing Content Detection

### 4.2.1 Gap Analysis

For each instruction, ask:

- [ ] What if the agent doesn't understand?
- [ ] What if the preconditions aren't met?
- [ ] What if there are multiple valid interpretations?
- [ ] What if external resources are unavailable?

### 4.2.2 Scenario Coverage

- [ ] Happy path documented
- [ ] Error paths documented
- [ ] Recovery procedures documented
- [ ] Escalation procedures documented (when to ask user)

---

# Layer 5: Anti-Pattern Detection

**Goal**: Identify common prompt engineering mistakes

## 5.1 Specification Anti-Patterns

### 5.1.1 Underspecification

- [ ] **AP-VAGUE**: Instructions rely on "common sense" or implicit knowledge
- [ ] **AP-MISSING-FORMAT**: Output format not specified
- [ ] **AP-MISSING-ROLE**: No persona/expertise defined when needed
- [ ] **AP-MISSING-CONSTRAINTS**: No boundaries on length, scope, style

### 5.1.2 Overspecification

- [ ] **AP-OVERLOAD**: Too many tasks in single instruction
- [ ] **AP-MICROMANAGE**: Unnecessary low-level details
- [ ] **AP-CONFLICTING**: Contradictory requirements
- [ ] **AP-IMPOSSIBLE**: Requirements that can't all be satisfied

## 5.2 Context Anti-Patterns

### 5.2.1 Context Mismanagement

- [ ] **AP-CONTEXT-BLOAT**: Excessive context that dilutes important info
- [ ] **AP-CONTEXT-STARVATION**: Critical context missing
- [ ] **AP-CONTEXT-DRIFT**: Assumed context may not persist (compaction)
- [ ] **AP-VAGUE-REFERENCE**: "The above" / "this" without clear antecedent

### 5.2.2 Memory Anti-Patterns

- [ ] **AP-ASSUMES-MEMORY**: Relies on agent remembering earlier conversation
- [ ] **AP-NO-CHECKPOINT**: Long workflows without state checkpoints
- [ ] **AP-IMPLICIT-STATE**: State changes not explicitly tracked

## 5.3 Behavioral Anti-Patterns

### 5.3.1 Execution Anti-Patterns

- [ ] **AP-NO-VERIFICATION**: No self-check or validation step
- [ ] **AP-SKIP-ALLOWED**: Easy to skip critical steps
- [ ] **AP-SILENT-FAIL**: Failures not surfaced to user
- [ ] **AP-INFINITE-LOOP**: Possible to get stuck in retry loop

### 5.3.2 Output Anti-Patterns

- [ ] **AP-HALLUCINATION-PRONE**: Instructions encourage guessing
- [ ] **AP-NO-UNCERTAINTY**: No permission to say "I don't know"
- [ ] **AP-NO-SOURCES**: No requirement to cite/verify claims

## 5.4 Maintainability Anti-Patterns

### 5.4.1 Evolution Anti-Patterns

- [ ] **AP-HARDCODED**: Magic numbers/strings instead of parameters
- [ ] **AP-DRY-VIOLATION**: Same instruction repeated in multiple places
- [ ] **AP-NO-VERSION**: No versioning for breaking changes
- [ ] **AP-TANGLED**: Changes to one part break unrelated parts

---

# Layer 6: Context Engineering

**Goal**: Evaluate efficient use of limited context window

## 6.1 Token Efficiency

### 6.1.1 Content Audit

- [ ] Identify verbose sections that can be compressed
- [ ] Identify redundant content across sections
- [ ] Identify content that could be loaded conditionally
- [ ] Calculate approximate token count

### 6.1.2 Information Priority

- [ ] Most critical instructions in first 20% of document
- [ ] Examples/details can be truncated without losing core behavior
- [ ] Conditional content clearly marked for selective loading

## 6.2 Context Lifecycle

### 6.2.1 Loading Strategy

- [ ] What must be loaded at start? (Always-on context)
- [ ] What can be loaded on-demand? (WHEN clauses)
- [ ] What can be summarized if context runs low?
- [ ] What must never be dropped?

### 6.2.2 Persistence Strategy

- [ ] How to preserve critical state across compaction?
- [ ] What should be written to files vs kept in memory?
- [ ] How to detect and recover from context loss?

## 6.3 Attention Management

### 6.3.1 Attention Anchors

- [ ] Critical instructions repeated/reinforced
- [ ] Important sections visually emphasized
- [ ] Guardrails in dedicated section (models trained to attend to this)

### 6.3.2 Attention Dilution Prevention

- [ ] Not too many instructions competing for attention
- [ ] Related instructions grouped (not scattered)
- [ ] Low-priority content clearly marked or separated

---

# Layer 7: Testability Assessment

**Goal**: Evaluate whether compliance can be verified

## 7.1 Verifiable Instructions

### 7.1.1 Binary Verification

For each instruction, can we determine:

- [ ] Did the agent do it? (Yes/No, not subjective)
- [ ] Did the agent do it correctly? (Measurable criteria)
- [ ] Did the agent do it completely? (Checkable completeness)

### 7.1.2 Observable Outputs

- [ ] Instructions produce observable artifacts
- [ ] Intermediate steps visible (not just final output)
- [ ] Compliance evidence included in output

## 7.2 Self-Verification Mechanisms

### 7.2.1 Built-in Checks

- [ ] Document includes validation criteria
- [ ] Agent instructed to self-verify before completing
- [ ] Checklist format for critical steps
- [ ] "Proof of work" requirements (show reasoning)

### 7.2.2 External Verification

- [ ] Can be validated by automated tools
- [ ] Can be validated by another agent
- [ ] Can be validated by human reviewer

## 7.3 Test Case Specification

### 7.3.1 Happy Path Tests

- [ ] At least one example of correct behavior
- [ ] Example shows complete input → output
- [ ] Example demonstrates key edge cases

### 7.3.2 Negative Tests

- [ ] Examples of what NOT to do
- [ ] Examples of incorrect outputs
- [ ] Examples of how to recover from errors

---

# Layer 8: Agent Ergonomics

**Goal**: Evaluate how well instructions work with LLM capabilities

## 8.1 Model Alignment

### 8.1.1 Capability Match

- [ ] Instructions match model capabilities (don't ask impossible things)
- [ ] Complex reasoning broken into steps (chain-of-thought friendly)
- [ ] Format requests match model training (JSON, Markdown, etc.)

### 8.1.2 Training Alignment

- [ ] Uses patterns model likely saw in training
- [ ] Role/persona appropriate for task
- [ ] Style consistent with effective prompt patterns

## 8.2 Failure Mode Handling

### 8.2.1 Graceful Degradation

- [ ] What happens if agent partially fails?
- [ ] Can agent recover without human intervention?
- [ ] Are there explicit "ask for help" triggers?

### 8.2.2 Hallucination Prevention

- [ ] Instructions require verification/citation
- [ ] Agent permitted to express uncertainty
- [ ] Speculative content clearly marked
- [ ] External tool use for factual queries

## 8.3 Iterative Compatibility

### 8.3.1 Refinement Support

- [ ] Output can be iteratively improved
- [ ] Feedback incorporation path defined
- [ ] Partial success is actionable (not all-or-nothing)

### 8.3.2 Conversation Compatibility

- [ ] Works in multi-turn conversations
- [ ] Handles clarification requests
- [ ] Handles scope changes mid-task

---

# Layer 9: Improvement Synthesis

**Goal**: Consolidate findings into actionable improvements

## 9.1 Issue Prioritization

### 9.1.1 Severity Classification

| Severity | Criteria | Action |
|----------|----------|--------|
| **CRITICAL** | Blocks agent from completing task | Fix immediately |
| **HIGH** | Causes incorrect/inconsistent output | Fix before deployment |
| **MEDIUM** | Reduces quality or efficiency | Fix in next iteration |
| **LOW** | Minor improvement opportunity | Backlog |

### 9.1.2 Effort Classification

| Effort | Criteria |
|--------|----------|
| **TRIVIAL** | Single word/phrase change |
| **SMALL** | Single section rewrite |
| **MEDIUM** | Multiple section changes |
| **LARGE** | Document restructure |

## 9.2 Improvement Recommendations

### 9.2.1 Quick Wins

- [ ] List CRITICAL + TRIVIAL/SMALL fixes
- [ ] Prioritize by impact/effort ratio
- [ ] Identify dependencies between fixes

### 9.2.2 Strategic Improvements

- [ ] List structural/architectural changes needed
- [ ] Identify refactoring opportunities
- [ ] Suggest new sections or documents

## 9.3 Implementation Guidance

### 9.3.1 For Each Fix

Provide:

- [ ] **What**: Specific change to make
- [ ] **Where**: Exact location (section, line)
- [ ] **Why**: Issue being addressed
- [ ] **How**: Suggested replacement text
- [ ] **Verify**: How to confirm fix worked

### 9.3.2 Testing Plan

- [ ] Test cases for critical fixes
- [ ] Regression checks for existing behavior
- [ ] Validation that fixes don't conflict

---

# Execution Protocol

## Prerequisites

Before starting review:

- [ ] Full document text accessible
- [ ] Related documents available for cross-reference
- [ ] Understanding of document's purpose and context
- [ ] Access to example outputs (if available)

## Execution Order

Layers MUST be executed in order 1-9. Each layer builds on previous findings.

**Checkpointing**: After each layer, summarize findings before proceeding.

**Time Boxing**: Set time limits per layer based on document size:

| Document Size | Layer 1-3 | Layer 4-5 | Layer 6-8 | Layer 9 |
|---------------|-----------|-----------|-----------|---------|
| Small (<500 lines) | 10min | 15min | 15min | 10min |
| Medium (500-2000 lines) | 20min | 30min | 30min | 20min |
| Large (>2000 lines) | 30min | 45min | 45min | 30min |

**Rationale**: Time boxes prevent perfectionism paralysis and ensure progress. Layers 4-5 (completeness, anti-patterns) and 6-8 (context, testability, ergonomics) get more time as they require deeper analysis. Layer 9 synthesizes findings rather than discovering new ones, so needs less time. If a layer cannot be completed within its time box, note blocking issues and proceed — incomplete analysis is better than no analysis.

## Error Handling

### Partial Completion

If a layer cannot be fully completed:

1. **Document what was analyzed** — note which checklist items were completed
2. **Note blocking issues** — why couldn't the layer be completed (missing context, ambiguous scope, etc.)
3. **Mark as PARTIAL** — in output, indicate layer status as PARTIAL with reason
4. **Proceed to next layer** — don't block the entire review

### Missing Information

If required information is unavailable:

- **Dependencies not accessible**: Note as blocker, analyze what IS available
- **Examples not provided**: Flag in Layer 7 (Testability), suggest creating examples
- **Context unclear**: Ask user for clarification OR make assumptions explicit

### Recovery Protocol

If review must be interrupted (context compaction, session end):

1. Save current state to file: `review-checkpoint-{document}-{layer}.md`
2. Include: completed layers summary, current layer progress, issues found so far
3. On resume: read checkpoint, verify document unchanged, continue from saved layer

## Output Format

After completing all layers, produce:

```markdown
# Prompt Engineering Review: {Document Name}

## Summary
- **Document Type**: {type}
- **Overall Quality**: {GOOD|NEEDS_IMPROVEMENT|POOR}
- **Critical Issues**: {count}
- **Total Issues**: {count}

## Layer Summaries
{One paragraph per layer}

## Issues Found

### Critical
| ID | Layer | Description | Location | Fix |
|----|-------|-------------|----------|-----|
| C1 | L5 | AP-VAGUE: No output format | Section 3.2 | Add format spec |

### High
{table}

### Medium
{table}

### Low
{table}

## Recommended Fixes

### Immediate (Critical/High + Low Effort)
1. {Fix description with before/after}

### Next Iteration (Medium Priority)
1. {Fix description}

### Backlog (Low Priority / High Effort)
1. {Fix description}

## Verification Checklist
- [ ] All critical issues addressed
- [ ] No new issues introduced
- [ ] Examples/tests updated if needed
```

---

## Quick Reference: Anti-Pattern Codes

| Code | Category | Description |
|------|----------|-------------|
| AP-VAGUE | Specification | Ambiguous language |
| AP-MISSING-FORMAT | Specification | No output format |
| AP-MISSING-ROLE | Specification | No persona defined |
| AP-MISSING-CONSTRAINTS | Specification | No boundaries |
| AP-OVERLOAD | Specification | Too many tasks |
| AP-MICROMANAGE | Specification | Too much detail |
| AP-CONFLICTING | Specification | Contradictory rules |
| AP-IMPOSSIBLE | Specification | Unsatisfiable |
| AP-CONTEXT-BLOAT | Context | Too much context |
| AP-CONTEXT-STARVATION | Context | Missing context |
| AP-CONTEXT-DRIFT | Context | Context may be lost |
| AP-VAGUE-REFERENCE | Context | Unclear antecedent |
| AP-ASSUMES-MEMORY | Memory | Relies on memory |
| AP-NO-CHECKPOINT | Memory | No state saves |
| AP-IMPLICIT-STATE | Memory | Hidden state |
| AP-NO-VERIFICATION | Execution | No self-check |
| AP-SKIP-ALLOWED | Execution | Can skip steps |
| AP-SILENT-FAIL | Execution | Hidden failures |
| AP-INFINITE-LOOP | Execution | Can get stuck |
| AP-HALLUCINATION-PRONE | Output | Encourages guessing |
| AP-NO-UNCERTAINTY | Output | Can't say "don't know" |
| AP-NO-SOURCES | Output | No citation needed |
| AP-HARDCODED | Maintainability | Magic values |
| AP-DRY-VIOLATION | Maintainability | Repeated content |
| AP-NO-VERSION | Maintainability | No versioning |
| AP-TANGLED | Maintainability | Coupled changes |

---

## Integration with FDD

This methodology integrates with FDD workflows:

- **Validate workflow**: Use this methodology for semantic validation of instruction documents
- **Generate workflow**: Apply these principles when creating new instruction documents
- **Adapter workflow**: Ensure AGENTS.md follows these best practices

---

## References

### Methodology Sources

- [Anthropic Prompt Engineering Docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [Anthropic Context Engineering for Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [IBM 2026 Prompt Engineering Guide](https://www.ibm.com/think/prompt-engineering)
- [Microsoft AI Agents Design Patterns](https://microsoft.github.io/ai-agents-for-beginners/03-agentic-design-patterns/)
- [Taxonomy of Prompt Defects](https://arxiv.org/html/2509.14404v1)

### Anti-Pattern Sources

- [14 Prompt Engineering Mistakes](https://opendatascience.com/beyond-prompt-and-pray-14-prompt-engineering-mistakes-youre-probably-still-making/)
- [10 Common LLM Prompt Mistakes](https://www.goinsight.ai/blog/llm-prompt-mistake/)
- [Common Challenges and Solutions](https://latitude-blog.ghost.io/blog/common-llm-prompt-engineering-challenges-and-solutions/)

### Agent-Specific Resources

- [4 Tips for AI Agent System Prompts](https://theagentarchitect.substack.com/p/4-tips-writing-system-prompts-ai-agents-work)
- [11 Prompting Techniques for Better AI Agents](https://www.augmentcode.com/blog/how-to-build-your-agent-11-prompting-techniques-for-better-ai-agents)
- [System Prompts Design Patterns](https://tetrate.io/learn/ai/system-prompts-guide)

---

## Validation

Review is complete when:

- [ ] All 9 layers analyzed
- [ ] All checklist items attempted (marked done or N/A)
- [ ] Issues categorized by severity
- [ ] Fixes prioritized by impact/effort
- [ ] Implementation guidance provided
- [ ] Verification plan included
