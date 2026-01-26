---
fdd: true
type: workflow
name: ADR Validate
version: 1.0
purpose: Validate Architecture Decision Records document
---

# Validate Architecture Decision Records

**Type**: Validation  
**Role**: Architect  
**Artifact**: Validation report (output to chat)

---

## Prerequisite Checklist

- [ ] Agent has read execution-protocol.md
- [ ] Agent has read workflow-execution.md
- [ ] Agent understands this workflow's purpose

---

## Overview

This workflow guides the execution of the specified task.

---

ALWAYS open and follow `../requirements/workflow-execution.md` WHEN executing this workflow

## ⚠️ PRE-FLIGHT CHECKLIST (ALWAYS Complete Before Proceeding)

**Agent ALWAYS verifies before starting this workflow**:

**Navigation Rules Compliance**:
- [ ] ✅ Open and follow `../requirements/execution-protocol.md` (MANDATORY BASE)
- [ ] ✅ Open and follow `../requirements/workflow-execution.md` (General execution)
- [ ] ✅ Open and follow `../requirements/workflow-execution-validations.md` (Validation specifics)

**Workflow-Specific Requirements**:
- [ ] ✅ Open and follow `../requirements/adr-structure.md` (This workflow's requirements)
- [ ] ✅ Check adapter initialization (FDD-Adapter/AGENTS.md exists)
- [ ] ✅ Validate all prerequisites from Prerequisites section below

**Self-Check**:
- [ ] ✅ I have read ALL files listed above
- [ ] ✅ I understand "Maximum Attention to Detail" requirement
- [ ] ✅ I am ready to check EVERY validation criterion individually
- [ ] ✅ I will verify `**ADR ID**:` field in EACH ADR header
- [ ] ✅ I will run grep searches for systematic verification
- [ ] ✅ I will complete self-test before reporting results

**⚠️ If ANY checkbox is unchecked → STOP and read missing files first**

---

## Requirements

**ALWAYS open and follow**: `../requirements/adr-structure.md`

Extract:
- MADR format requirements
- FDD extensions (Related Design Elements)
- ADR numbering rules
- Validation criteria (100 points breakdown)
- Pass threshold (≥90/100)

---

## Prerequisites

**MUST validate**:
- [ ] ADR directory exists - validate: Check directory at `architecture/ADR/`
- [ ] DESIGN.md exists - validate: Check file at `architecture/DESIGN.md`
- [ ] PRD.md exists - validate: Check file at `architecture/PRD.md`

**If missing**: Run prerequisite workflows first

---

## Steps

### 1. Read Dependencies

Open `architecture/PRD.md` and `architecture/DESIGN.md`

Extract:
- All actor IDs (from PRD.md Section B)
- All capability IDs (from PRD.md Section C)
- All requirement IDs (from DESIGN.md Section B)
- All principle IDs (from DESIGN.md Section B)

### 2. Execute Validation

Follow validation criteria from `adr-structure.md`:
- File Structure (15 pts): ADR directory exists, ADR-0001 exists
- ADR Numbering (15 pts): Sequential, no gaps, proper format (ADR-NNNN)
- Required Sections (30 pts): Context, Drivers, Options, Outcome, Related Elements
- Content Quality (25 pts): Clear context, ≥2 options, rationale, consequences
- FDD Integration (15 pts): Related Design Elements with valid IDs

Calculate total score

### 3. Output Results to Chat

**Format**:
```markdown
## Validation: ADR/

**Score**: {X}/100  
**Status**: PASS | FAIL  
**Threshold**: ≥90/100

---

### Findings

**File Structure** ({X}/15):
✅ | ❌ {item}

**ADR Numbering** ({X}/15):
✅ | ❌ {item}

**Required Sections** ({X}/30):
✅ | ❌ {item}

**Content Quality** ({X}/25):
✅ | ❌ {item}

**FDD Integration** ({X}/15):
✅ | ❌ {item}

---

### Recommendations

**High Priority**:
1. {Fix}

---

### Next Steps

{If PASS}: ✅ ADRs validated, proceed with feature development

{If FAIL}: ❌ Fix issues, re-run validation
```

---

## Validation

Self-validating workflow

---

## Validation Criteria

- [ ] All workflow steps completed
- [ ] Output artifacts are valid

---

## Validation Checklist

- [ ] All prerequisites were met
- [ ] All steps were executed in order

---

## Next Steps

**If PASS**: ADRs validated, architecture documentation complete

**If FAIL**: Fix ADR files under ADR/, re-validate
