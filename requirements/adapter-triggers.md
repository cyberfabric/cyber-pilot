---
fdd: true
type: requirement
name: Adapter Triggers
version: 1.0
purpose: Define when AI agent proposes running adapter workflow
---

# Adapter Evolution Triggers

---

## Table of Contents

- [Overview](#overview)
- [Mandatory Adapter Initialization](#mandatory-adapter-initialization)
- [Trigger Rules](#trigger-rules)
  - [1. Design Decisions Made](#1-design-decisions-made)
  - [2. Feature Patterns Detected](#2-feature-patterns-detected)
  - [3. Implementation Code](#3-implementation-code)
  - [4. User Decisions](#4-user-decisions)
  - [5. Existing Project Discovery](#5-existing-project-discovery)
- [Detection Algorithm](#detection-algorithm)
- [User Response Handling](#user-response-handling)
- [Error Handling](#error-handling)
- [Agent Responsibilities](#agent-responsibilities)
- [Examples](#examples)
- [Integration with Workflows](#integration-with-workflows)
- [Consolidated Validation Checklist](#consolidated-validation-checklist)
- [References](#references)

---

## Prerequisite Checklist

- [ ] Agent has read and understood this requirement
- [ ] Agent will follow the rules defined here

---

## Overview

This document defines when AI agents should propose running the adapter workflow.

---

## Mandatory Adapter Initialization

**BEFORE any FDD workflow execution**:

Agent MUST check that adapter exists:
- Search for `{adapter-directory}/AGENTS.md` in common locations:
  - `/FDD-Adapter/AGENTS.md`
  - `spec/FDD-Adapter/AGENTS.md`
  - `docs/FDD-Adapter/AGENTS.md`

IF adapter NOT found:
- STOP workflow execution
- Propose: "Adapter not initialized. Run bootstrap?" [Yes]
- Run: `adapter` workflow Mode 1 (Bootstrap)
- After bootstrap: Resume original workflow

IF adapter exists (minimal or evolved):
- Continue with workflow execution

---

## Trigger Rules

Agent ALWAYS proposes running `adapter` workflow (Mode 2 Discovery or Mode 3 Evolution) WHEN:

### 1. Design Decisions Made

**Trigger**: DESIGN.md created, updated, or validated

**Check**:
- DESIGN.md Section C.2 (Domain Model) completed
- DESIGN.md Section C.3 (API Contracts) completed
- New ADRs created with technical decisions
- ADRs reference: tech stack, patterns, formats

**Scan for**:
- Tech stack changes (languages, frameworks, databases)
- Domain model format specification
- API contract format specification
- Architecture patterns

**Propose IF**:
- New ADR not reflected in adapter specs
- DESIGN.md Section C has content not in adapter
- Tech stack mentioned but not in specs/tech-stack.md

**Action**: 
```
Design completed. Technical decisions detected:
  - ADR-0001: Python/Django (not in adapter)
  - DESIGN.md C.2: JSON Schema format (not in adapter)
  
Run adapter workflow to capture these? [Yes] [No] [Review]
```

---

### 2. Feature Patterns Detected

**Trigger**: Feature DESIGN.md created or validated

**Check**:
- Feature DESIGN.md Section B (Actor Flows) completed
- Feature DESIGN.md Section C (Algorithms) completed
- Feature DESIGN.md Section E (Technical Details) completed

**Scan for**:
- Repeated patterns (same algorithm name/structure appears in ≥2 FEATURE artifacts within this project)
- Architecture patterns (Repository, Factory, Strategy, etc.)
- Code examples or pseudocode
- Technical implementation details

**Propose IF**:
- Pattern not in specs/patterns.md
- Code example worth capturing
- Technical detail is reusable

**Action**:
```
Feature pattern detected:
  - LRU caching strategy in fdd-context-provider
  
Add to adapter specs/patterns.md? [Yes] [No]
```

---

### 3. Implementation Code

**Trigger**: Code committed AND tests passed

**Check**:
- New files created in src/, app/, lib/
- Tests passed (test command exit code 0)
- Code review completed (if applicable)

**Scan for**:
- Utility functions called ≥3 times across the project codebase (count by grep/search)
- Repeated code patterns (similar structure in ≥2 files)
- Boilerplate code
- Integration code (external APIs, database)
- Deviation from conventions

**Propose IF**:
- Reusable utility detected
- Code pattern worth documenting
- Convention deviation detected

**Action**:
```
Reusable code detected:
  - retry_with_backoff() used 5 times
  
Add to adapter specs/snippets/error-handling.md? [Yes] [No]
```

---

### 4. User Decisions

**Trigger**: User explicitly states technical decision in conversation

**Detect keywords**:
- "we will use {technology}"
- "I decided to use {pattern}"
- "let's go with {framework}"
- "convention is {style}"
- User answers technical questions

**Propose IF**:
- Decision is technical (not prd)
- Decision affects implementation
- Decision not yet in adapter

**Action**:
```
Technical decision detected in conversation:
  "We will use PostgreSQL 15+ for database"
  
Capture in adapter specs/tech-stack.md? [Yes] [No]
```

---

### 5. Existing Project Discovery

**Trigger**: First FDD workflow run in existing codebase

**Check**:
- Source code exists (src/, app/, lib/)
- Package manager files exist
- Adapter is minimal (only Extends) OR doesn't exist

**Scan for**:
- Documentation, ADRs, configs, code structure, API definitions, domain models

**Propose**: 
```
Existing project detected with code/docs.
  - 11 ADRs found
  - Tech stack detected: Python 3.11+, Django 4.2+
  - Code patterns detected: Layered architecture
  
Run adapter discovery to capture existing decisions? [Yes] [No]
```

---

## Detection Algorithm

```yaml
At ANY workflow step:

1. Monitor for triggers:
   - Artifact created/updated (kinds: PRD, DESIGN, FEATURES, ADR, FEATURE)
   - Artifact validated (any kind)
   - Codebase changes (code committed, tests passed)
   - User stated technical decision

2. IF trigger detected:
   → Run trigger-specific scan
   → Check conditions
   → Build proposal

3. IF conditions met:
   → Show proposal to user
   → IF user accepts:
     → Run adapter workflow (appropriate mode)
     → Capture updates
     → Update adapter specs with rules-based WHEN clauses
   → IF user rejects:
     → Continue workflow
     → Log: "Adapter update skipped by user"

4. Continue original workflow
```

---

## User Response Handling

When proposal is shown to user, handle responses:

| Response | Action |
|----------|--------|
| **[Yes]** | Run adapter workflow (appropriate mode), then resume original workflow |
| **[No]** | Log "Adapter update skipped by user", continue original workflow |
| **[Review]** | Show detailed diff of what would be captured, then re-prompt with [Yes] / [No] |

### [Review] Response Flow

```
User selects: [Review]
Agent shows:
  Technical decisions to capture:

  1. specs/tech-stack.md (NEW):
     + Python 3.11+
     + Django 4.2+
     + PostgreSQL 15+

  2. specs/domain-model.md (NEW):
     + JSON Schema format
     + Entity: User, Project, Task

  3. AGENTS.md updates:
     + WHEN rule for tech-stack.md
     + WHEN rule for domain-model.md

  Proceed with capture? [Yes] [No]
```

---

## Error Handling

### Adapter Workflow Fails

**If adapter workflow fails during capture**:
```
⚠️ Adapter update failed: {error}
→ Original workflow state preserved
→ Technical decisions NOT captured
→ Fix: Run /fdd-adapter manually after resolving error
```
**Action**: Log error, continue original workflow without adapter updates.

### Trigger Detection Fails

**If trigger scan cannot complete** (file access, parsing error):
```
⚠️ Could not scan for adapter triggers: {reason}
→ Skipping adapter proposal for this step
→ Manual adapter update may be needed
```
**Action**: WARN and continue — do not block workflow.

### Conflicting Decisions

**If detected decision conflicts with existing adapter spec**:
```
⚠️ Conflict detected:
  - Adapter: Python 3.10+
  - DESIGN.md: Python 3.11+

Options:
  [Update] - Replace adapter spec with new decision
  [Keep] - Keep existing adapter spec
  [ADR] - Create ADR to document decision change
```

---

## Agent Responsibilities

**Agent MUST**:
1. ✅ Check adapter initialization before ANY workflow
2. ✅ Monitor for trigger events during workflow execution
3. ✅ Scan for candidates when trigger detected
4. ✅ Propose adapter update with clear context
5. ✅ Respect user decision (accept/reject/review)
6. ✅ Never silently skip adapter opportunities

**Agent MUST NOT**:
1. ❌ Run adapter workflow without user approval
2. ❌ Hardcode adapter calls in workflow steps
3. ❌ Skip adapter proposals to "save time"
4. ❌ Propose adapter for non-technical decisions

---

## Examples

### Example 1: Design Artifact Trigger

```
User: "Generate DESIGN artifact"
Agent: Checks adapter → Found minimal adapter
Agent: Executes generate workflow for artifact kind: DESIGN
Agent: DESIGN.md created with Section C completed
Agent: Trigger detected → Scans DESIGN.md + ADRs
Agent: Finds: 3 ADRs with tech stack, JSON Schema format, Markdown tables
Agent: Proposes: "Design completed. 3 technical decisions not in adapter. Capture?"
User: "Yes"
Agent: Runs adapter workflow Mode 3 (Evolution)
Agent: Creates specs/tech-stack.md, specs/domain-model.md, specs/api-contracts.md
Agent: Updates AGENTS.md with rules-based WHEN clauses:
       ALWAYS open and follow `specs/tech-stack.md` WHEN FDD follows rules `fdd-sdlc` for artifact kinds: DESIGN, ADR OR codebase
Agent: Returns to generate workflow completion
```

### Example 2: Implementation Trigger

```
Agent: Implementation completed, tests passed
Agent: Trigger detected → Scans committed code
Agent: Finds: retry_with_backoff() function used 5 times
Agent: Proposes: "Reusable retry utility detected. Add to adapter snippets?"
User: "Yes"
Agent: Runs adapter workflow Mode 3 (Evolution)
Agent: Creates specs/snippets/error-handling.md with function + usage
Agent: Updates AGENTS.md MUST rule for snippets
Agent: Returns to implementation workflow
```

### Example 3: User Decision Trigger

```
User: "Let's use FastAPI instead of Django"
Agent: Trigger detected → Tech stack decision
Agent: Proposes: "Tech stack change: FastAPI. Update adapter?"
User: "Yes"
Agent: Runs adapter workflow Mode 3 (Evolution)
Agent: Updates specs/tech-stack.md (Django → FastAPI)
Agent: Adds ADR: ADR-0012: FastAPI Migration
Agent: Returns to conversation
```

---

## Integration with Workflows

Instead of hardcoding adapter calls in each workflow, workflows reference this file:

```markdown
# Any Workflow

## Prerequisites

**ALWAYS open and follow**: `requirements/adapter-triggers.md`

Execute: Check adapter initialization
Execute: Monitor triggers during workflow

## Steps

[workflow steps here]

[At any step, if trigger detected, propose adapter update]
```

---

## Consolidated Validation Checklist

**Use this single checklist for all adapter-triggers validation.**

### Structure (S)

| # | Check | Required |
|---|-------|----------|
| S.1 | All 5 trigger types defined (Design, Feature Patterns, Implementation, User Decisions, Discovery) | YES |
| S.2 | Detection algorithm present | YES |
| S.3 | User response handling defined ([Yes], [No], [Review]) | YES |
| S.4 | Error handling section present | YES |
| S.5 | Agent responsibilities listed (MUST / MUST NOT) | YES |
| S.6 | Integration section complete | YES |
| S.7 | Proper markdown formatting | YES |

### Completeness (C)

| # | Check | Required |
|---|-------|----------|
| C.1 | Each trigger has: Trigger, Check, Scan, Propose IF, Action sections | YES |
| C.2 | Detection keywords specified (Trigger 4) | YES |
| C.3 | Proposal format examples provided for each trigger | YES |
| C.4 | Threshold scopes clarified (e.g., "≥3 times across project") | YES |
| C.5 | No placeholders or TODOs | YES |

### Clarity (CL)

| # | Check | Required |
|---|-------|----------|
| CL.1 | Trigger conditions unambiguous | YES |
| CL.2 | Agent actions clearly defined | YES |
| CL.3 | Examples concrete and realistic | YES |
| CL.4 | MUST/MUST NOT semantics correct (not "ALWAYS do NOT") | YES |
| CL.5 | Imperative language used | YES |

### Integration (I)

| # | Check | Required |
|---|-------|----------|
| I.1 | References execution-protocol.md correctly | YES |
| I.2 | References adapter-structure.md correctly | YES |
| I.3 | Consistent with FDD principles | YES |
| I.4 | Used by/References sections complete | YES |
| I.5 | Integration examples provided | YES |

### Final (F)

| # | Check | Required |
|---|-------|----------|
| F.1 | Document follows required structure | YES |
| F.2 | All validation criteria pass | YES |

---

## References

**Used by**:
- All FDD workflows (via execution-protocol.md)
- AI agent execution logic

**References**:
- `adapter-structure.md` - Adapter structure and WHEN rule format
- `../workflows/adapter.md` - Adapter workflow
- `execution-protocol.md` - Common execution protocol
