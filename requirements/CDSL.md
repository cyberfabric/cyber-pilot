---
cypilot: true
type: requirement
name: Cypilot DSL (CDSL) Language
version: 1.1
purpose: Define syntax and grammar for behavior description language
---

# Cypilot DSL (CDSL)

---

## Table of Contents

- [Agent Instructions](#agent-instructions)
- [Overview](#overview)
- [Core Rules](#core-rules)
- [Phase + Implementation Status](#phase--implementation-status-mandatory)
- [Basic Format](#basic-format)
- [Control Flow Keywords](#control-flow-keywords)
- [Example: Algorithm](#example-algorithm)
- [Example: Actor Flow](#example-actor-flow)
- [Validation Rules](#validation-rules)
- [State Machines](#state-machines-section-d)
- [Excluding Examples from Validation](#excluding-examples-from-validation)
- [Error Handling](#error-handling)
- [Consolidated Validation Checklist](#consolidated-validation-checklist)
- [References](#references)

---

## Agent Instructions

**ALWAYS open and follow**: This file WHEN writing behavioral sections (algorithms, flows, state machines) in DESIGN artifacts

**ALWAYS open and follow**: `overall-design-content.md` WHEN specifying behavioral sections in root DESIGN.md

**ALWAYS open and follow**: `spec-design-content.md` WHEN specifying behavioral sections in spec DESIGN.md

**Prerequisite**: Agent confirms understanding before proceeding:
- [ ] Agent has read and understood this requirement
- [ ] Agent will follow the rules defined here
- [ ] Agent understands Cypilot DSL (CDSL) is language-agnostic (no code syntax)

---

## Overview

**Cypilot DSL (CDSL)** - Plain English behavior description using markdown lists and bold keywords

**Format**: Numbered markdown lists (1, 2, 3...) + Bold keywords + Plain English

**No code syntax**: Cypilot DSL (CDSL) is language-agnostic, implementation-independent

---

## Core Rules

1. ✅ Use markdown numbered lists only
2. ✅ Bold keywords for control flow
3. ✅ Plain English descriptions
4. ✅ Indent nested steps
5. ❌ No code syntax ever

---

## Phase + Implementation Status (Mandatory)

**Every CDSL step line MUST include**:

- Implementation checkbox: `[ ]` (not implemented) or `[x]` (implemented)
- Phase token: `pN` (N is an integer, e.g., `p1`, `p2`)
- Instruction ID token: `inst-{short-id}` (kebab-case, stable across renumbering)

**Required format**:

- Numbered step: 1. [ ] - `p1` - {instruction} - `inst-some-job`
- Nested numbered step:    1. [ ] - `p1` - {instruction} - `inst-some-job`
- Bullet step (e.g. under PARALLEL): - [ ] - `p1` - {instruction} - `inst-some-job`

**Rules**:

- `pN` MUST be present on every step line (default is `p1`)
- `inst-{short-id}` MUST be present on every step line
- `inst-{short-id}` MUST be unique within its scope (a single flow, algorithm, state machine, or testing scenario)
- Authors MAY change phase numbers only on existing phase tokens (do not invent new syntax)

---

## Basic Format

**Algorithm: [Name]**

Input: [parameters]  
Output: [result]

1. [ ] - `p1` - [Step description] - `inst-step-one`
2. [ ] - `p1` - [Step description] - `inst-step-two`
3. [ ] - `p1` - **RETURN** [result] - `inst-return-result`

**That's it!** No complex syntax needed.

---

## Control Flow Keywords

### IF/ELSE IF/ELSE

1. [ ] - `p1` - [Step] - `inst-step`
2. [ ] - `p1` - **IF** [condition]: - `inst-if`
   1. [ ] - `p1` - [Nested step] - `inst-if-nested`
3. [ ] - `p1` - **ELSE IF** [condition]: - `inst-else-if`
   1. [ ] - `p1` - [Nested step] - `inst-else-if-nested`
4. [ ] - `p1` - **ELSE**: - `inst-else`
   1. [ ] - `p1` - [Nested step] - `inst-else-nested`

### FOR EACH

1. [ ] - `p1` - [Step] - `inst-step`
2. [ ] - `p1` - **FOR EACH** item in collection: - `inst-for-each`
   1. [ ] - `p1` - [Process item] - `inst-process-item`
3. [ ] - `p1` - [Next step] - `inst-next-step`

### WHILE

1. [ ] - `p1` - [Step] - `inst-step`
2. [ ] - `p1` - **WHILE** [condition]: - `inst-while`
   1. [ ] - `p1` - [Process] - `inst-while-body`
3. [ ] - `p1` - [Next step] - `inst-next-step`

### TRY/CATCH

1. [ ] - `p1` - **TRY**: - `inst-try`
   1. [ ] - `p1` - [Operation that may fail] - `inst-try-op`
2. [ ] - `p1` - **CATCH** [ErrorType]: - `inst-catch`
   1. [ ] - `p1` - [Handle error] - `inst-handle-error`
3. [ ] - `p1` - [Continue] - `inst-continue`

### PARALLEL

1. [ ] - `p1` - [Prepare] - `inst-prepare`
2. [ ] - `p1` - **PARALLEL**: - `inst-parallel`
   - [ ] - `p1` - [Task 1] - `inst-parallel-task-1`
   - [ ] - `p1` - [Task 2] - `inst-parallel-task-2`
   - [ ] - `p1` - [Task 3] - `inst-parallel-task-3`
3. [ ] - `p1` - Wait for completion - `inst-wait`
4. [ ] - `p1` - [Combine results] - `inst-combine-results`

### MATCH (Pattern Matching)

1. [ ] - `p1` - [Get value] - `inst-get-value`
2. [ ] - `p1` - **MATCH** [value]: - `inst-match`
   - [ ] - `p1` - **CASE** [pattern]: [Action] - `inst-case-1`
   - [ ] - `p1` - **CASE** [pattern]: [Action] - `inst-case-2`
   - [ ] - `p1` - **DEFAULT**: [Action] - `inst-default`
3. [ ] - `p1` - [Continue] - `inst-continue`

### GO TO / SKIP TO

1. [ ] - `p1` - [Step] - `inst-step`
2. [ ] - `p1` - **IF** [condition]: - `inst-if`
   1. [ ] - `p1` - **GO TO** step N - `inst-go-to`
3. [ ] - `p1` - [Step] - `inst-next-step`
4. [ ] - `p1` - **SKIP TO** step N - `inst-skip-to`

### RETURN (Early Exit)

1. [ ] - `p1` - [Step] - `inst-step`
2. [ ] - `p1` - **IF** [condition]: - `inst-if`
   1. [ ] - `p1` - **RETURN** [value] (exit early) - `inst-return`
3. [ ] - `p1` - [Continue only if not returned] - `inst-continue`

---

## Example: Algorithm

**Algorithm: Enable Entity with Dependencies**

Input: entity_id, tenants, security_context  
Output: List of enabled entity IDs

1. [x] - `p1` - Initialize empty list: enabled_entities - `inst-init-enabled-entities`
2. [x] - `p1` - Load entity from registry - `inst-load-entity`
3. [x] - `p1` - **IF** entity not found: - `inst-if-not-found`
   1. [x] - `p1` - **RETURN** 404 error - `inst-return-404`
4. [ ] - `p2` - Update entity.enabled_for = tenants - `inst-update-enabled-for`
5. [ ] - `p1` - Add entity_id to enabled_entities - `inst-add-enabled-id`
6. [x] - `p1` - **FOR EACH** ref_id in references: - `inst-for-each-ref`
   1. [x] - `p1` - Load ref_entity - `inst-load-ref-entity`
   2. [ ] - `p2` - **IF** ref_entity not enabled: - `inst-if-ref-not-enabled`
      1. [ ] - `p2` - Enable ref_entity (recursive) - `inst-enable-ref-entity`
      2. [ ] - `p2` - Add to enabled_entities - `inst-add-ref-to-enabled`
7. [x] - `p1` - **TRY**: - `inst-try`
   1. [x] - `p1` - Commit transaction - `inst-commit`
   2. [x] - `p1` - Log audit trail - `inst-log-audit`
8. [ ] - `p1` - **CATCH** any errors: - `inst-catch`
   1. [ ] - `p1` - Rollback transaction - `inst-rollback`
   2. [ ] - `p1` - **RETURN** 500 error - `inst-return-500`
9. [ ] - `p1` - **RETURN** enabled_entities - `inst-return-enabled-entities`

---

## Example: Actor Flow

**Flow: Admin Creates Dashboard**

Actor: Admin  
Goal: Create new dashboard

1. [ ] - `p1` - User opens Dashboard page - `inst-open-dashboard-page`
2. [ ] - `p1` - User clicks "Create New" - `inst-click-create-new`
3. [ ] - `p1` - UI shows dashboard editor - `inst-show-editor`
4. [ ] - `p1` - User enters name and description - `inst-enter-name-and-description`
5. [ ] - `p1` - User clicks "Save" - `inst-click-save`
6. [ ] - `p1` - **API**: `POST /api/analytics/v1/gts` - `inst-api-post-gts`
   - [ ] - `p1` - Body: `{type: "layout.dashboard", name: "..."}` - `inst-body-layout-dashboard`
7. [ ] - `p1` - UI redirects to dashboard editor - `inst-redirect-to-editor`
8. [ ] - `p1` - User adds widgets - `inst-add-widgets`

---

## Validation Rules

### ✅ Required

- Markdown numbered lists (1, 2, 3...)
- Bold keywords: **IF**, **FOR EACH**, **WHILE**, **TRY/CATCH**, **RETURN**, **MATCH**
- Plain English descriptions
- Indentation for nested steps
- Each step line includes `[ ]` or `[x]`, `pN`, and an instruction ID token `inst-{short-id}`
- For codebase traceability, every implemented instruction marker maps to code via paired Cypilot block markers wrapping non-empty code.
   - Format: `@cpt-begin:{cpt-id}:p{N}:inst-{id}` ... code ... `@cpt-end:{cpt-id}:p{N}:inst-{id}`
   - Example: `# @cpt-begin:cpt-system-spec-x-algo-validate:p1:inst-check-input`

### ❌ Prohibited

- Code examples (any language)
- Function syntax (`fn`, `function`, `async`)
- Type annotations (`: string`, `<T>`)
- Language operators (`&&`, `||`, `=>`)
- Pseudo-code syntax

### ✅ Allowed

- Variable names (no types): `entity`, `items`, `result`
- Simple notation: `entity.field`, `array[0]`
- API endpoints: `POST /api/v1/resource`
- Inline clarifications: `(condition explanation)`

---

## State Machines (Section D)

### Basic Format

**State Machine: [Entity Name]**

**States**: [ALL_STATES, COMMA_SEPARATED]

**Transitions**:
1. [ ] - `p1` - **FROM** [state] **TO** [state] **WHEN** [trigger] - `inst-transition-1`
2. [ ] - `p1` - **FROM** [state] **TO** [state] **WHEN** [trigger] - `inst-transition-2`

### With Actions

**Transition: [STATE_A] → [STATE_B]**
**When**: [trigger]
**Actions**:
1. [ ] - `p1` - [Action step] - `inst-action-1`
2. [ ] - `p1` - [Action step] - `inst-action-2`
3. [ ] - `p1` - **IF** [condition]: - `inst-action-if`
   1. [ ] - `p1` - [Conditional action] - `inst-action-if-body`

### Example

**State Machine: Order**

**States**: DRAFT, PENDING_PAYMENT, PAID, SHIPPED, DELIVERED, CANCELLED

**Transitions**:
1. [ ] - `p1` - **FROM** DRAFT **TO** PENDING_PAYMENT **WHEN** user submits order - `inst-submit`
2. [ ] - `p1` - **FROM** PENDING_PAYMENT **TO** PAID **WHEN** payment confirmed - `inst-pay`
3. [ ] - `p1` - **FROM** PAID **TO** SHIPPED **WHEN** order dispatched - `inst-ship`
4. [ ] - `p1` - **FROM** SHIPPED **TO** DELIVERED **WHEN** delivery confirmed - `inst-deliver`
5. [ ] - `p1` - **FROM** DRAFT **TO** CANCELLED **WHEN** user cancels - `inst-cancel`

---

## Excluding Examples from Validation

**Purpose**: Documentation and workflow files often contain **example** Cypilot tags that should not be validated as real implementation.

**Solution**: Use `!no-cpt-begin` / `!no-cpt-end` block markers to exclude content from Cypilot scanning.

**Syntax**:

- Markdown/HTML comments: `<!-- !no-cpt-begin -->` ... `<!-- !no-cpt-end -->`
- Code comments (Python): `# !no-cpt-begin` ... `# !no-cpt-end`
- Code comments (Rust/C++): `// !no-cpt-begin` ... `// !no-cpt-end`

**Behavior**:

- Everything between markers is **completely ignored** by the validator
- Unmatched `!no-cpt-begin` (without closing `!no-cpt-end`) excludes everything to end of file
- Nested exclusion blocks are supported
- This is different from single-line `!no-cpt` which only excludes one line

**Use Cases**:

1. **Documentation examples**: Wrap example Cypilot tags in docs with exclusion blocks
2. **Deprecated code**: Mark old code that still has Cypilot tags but shouldn't be validated
3. **Template/boilerplate code**: Exclude scaffolding/template code from validation

**Example**:

```markdown
Real implementation:
<!-- cpt-begin cpt-myproject-spec-x-flow-y:p1:inst-real -->
Actual workflow step
<!-- cpt-end   cpt-myproject-spec-x-flow-y:p1:inst-real -->

Documentation example (excluded from validation):
<!-- !no-cpt-begin -->
```rust
// cpt-begin cpt-example-spec-z-algo-w:p1:inst-example
example_code();
// cpt-end   cpt-example-spec-z-algo-w:p1:inst-example
```
<!-- !no-cpt-end -->
```

**Important**: Use this sparingly. Most Cypilot tags should be real and validated. Only exclude genuine examples/documentation.

---

## Error Handling

### Invalid CDSL Syntax

**If CDSL content contains prohibited syntax**:
```
⚠️ Invalid CDSL syntax detected: {description}
→ Location: {file}:{line}
→ Found: {prohibited element}
→ Fix: Replace with plain English description
```
**Action**: FAIL validation — Cypilot DSL (CDSL) must be language-agnostic.

### Missing Required Tokens

**If step line missing checkbox, phase token, or instruction ID**:
```
⚠️ Incomplete CDSL step line: {line content}
→ Location: {file}:{line}
→ Missing: {checkbox | pN | inst-{id}}
→ Fix: Add missing token(s) in format: N. [ ] - `p1` - description - `inst-id`
```
**Action**: FAIL validation — all tokens are mandatory.

### Duplicate Instruction IDs

**If same `inst-{id}` appears multiple times in scope**:
```
⚠️ Duplicate instruction ID: inst-{id}
→ First occurrence: {file}:{line1}
→ Duplicate: {file}:{line2}
→ Fix: Rename one ID to be unique within scope
```
**Action**: FAIL validation — IDs must be unique within scope.

### Unbalanced Cypilot Markers in Code

**If code has `cpt-begin` without matching `cpt-end`**:
```
⚠️ Unbalanced Cypilot marker: {marker}
→ Location: {file}:{line}
→ Found: cpt-begin without cpt-end (or vice versa)
→ Fix: Add matching marker or remove orphan
```
**Action**: FAIL validation — markers must be paired.

### Empty Cypilot Block in Code

**If `cpt-begin`/`cpt-end` wraps no code**:
```
⚠️ Empty Cypilot block: {marker}
→ Location: {file}:{line}
→ Block contains no implementation code
→ Fix: Add implementation OR remove markers if not implemented
```
**Action**: FAIL validation — markers must wrap non-empty code.

---

## Consolidated Validation Checklist

**Use this single checklist for all CDSL validation.**

### Structure (S)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| S.1 | Uses numbered markdown lists (1, 2, 3...) | YES | Regex: `^\d+\.` for step lines |
| S.2 | Proper nesting with indentation | YES | Nested steps have consistent indent |
| S.3 | Each step line includes `[ ]` or `[x]` | YES | Checkbox present after step number |
| S.4 | Each step line includes phase token `pN` | YES | Regex: `p\d+` in backticks |
| S.5 | Each step line includes instruction ID `inst-{id}` | YES | Regex: `inst-[a-z0-9-]+` in backticks |
| S.6 | No code blocks or function syntax | YES | No `fn`, `function`, `async`, `def` |
| S.7 | No type annotations | YES | No `: string`, `<T>`, `-> Type` |

### Keyword Usage (K)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| K.1 | Keywords are bold | YES | `**IF**`, `**FOR EACH**`, etc. |
| K.2 | IF used for conditions | YES | `**IF** [condition]:` format |
| K.3 | FOR EACH used for iterations | YES | `**FOR EACH** item in collection:` format |
| K.4 | FROM/TO/WHEN used for state transitions | YES | State machine format |
| K.5 | TRY/CATCH used for error handling | YES | Proper pairing |
| K.6 | RETURN used for algorithm outputs | YES | `**RETURN** [value]` format |

### Clarity (CL)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| CL.1 | Plain English descriptions | YES | No code-like syntax |
| CL.2 | No programming operators | YES | No `=>`, `&&`, `\|\|`, `==` |
| CL.3 | No function definitions | YES | No `fn`, `function`, `async`, `def` |
| CL.4 | Language-agnostic | YES | No language-specific constructs |
| CL.5 | Clear and unambiguous steps | YES | Each step has single clear action |

### Completeness (CO)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| CO.1 | All flows have numbered steps | YES | Step numbers present |
| CO.2 | All algorithms have Input/Output | YES | `Input:` and `Output:` lines present |
| CO.3 | All state machines have States and Transitions | YES | `**States**:` and `**Transitions**:` present |
| CO.4 | No missing tokens on step lines | YES | All 3 tokens present: checkbox, phase, inst-id |
| CO.5 | Instruction IDs unique within scope | YES | No duplicates per flow/algorithm |
| CO.6 | No placeholders or TODOs | YES | Search returns 0 matches |
| CO.7 | All conditions and actions specified | YES | No empty IF/ELSE/FOR EACH bodies |

### Code Traceability (CT)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| CT.1 | Implemented instructions have code markers | CONDITIONAL | If `[x]`, marker exists in code |
| CT.2 | Code markers use `cpt-begin`/`cpt-end` format | YES | Paired block markers |
| CT.3 | Cypilot blocks wrap non-empty code | YES | Code exists between markers |
| CT.4 | No orphan markers in code | YES | All begin/end balanced |

### Final (F)

| # | Check | Required | How to Verify |
|---|-------|----------|---------------|
| F.1 | All Structure checks pass | YES | S.1-S.7 verified |
| F.2 | All Keyword Usage checks pass | YES | K.1-K.6 verified |
| F.3 | All Clarity checks pass | YES | CL.1-CL.5 verified |
| F.4 | All Completeness checks pass | YES | CO.1-CO.7 verified |
| F.5 | All Code Traceability checks pass | CONDITIONAL | CT.1-CT.4 verified if code exists |

---

## References

**This file is referenced by**:
- DESIGN artifacts (behavioral sections)
- SPEC artifacts (algorithms, flows)
- Code files (via Cypilot markers)

**References**:
- `overall-design-content.md` — Root DESIGN behavioral sections
- `spec-design-content.md` — Spec DESIGN behavioral sections
- `{adapter-directory}/AGENTS.md` — Project-specific CDSL overrides (if any)
