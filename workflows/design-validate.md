---
fdd: true
type: workflow
name: Design Validate
version: 1.0
purpose: Validate overall design document
---

# Validate Overall Design

**Type**: Validation  
**Role**: Architect, Product Manager (for PRD alignment)  
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
- [ ] ✅ Open and follow `../requirements/overall-design-structure.md` (This workflow's requirements)
- [ ] ✅ Check adapter initialization (FDD-Adapter/AGENTS.md exists)
- [ ] ✅ Validate all prerequisites from Prerequisites section below

**Self-Check**:
- [ ] ✅ I have read ALL files listed above
- [ ] ✅ I understand "Maximum Attention to Detail" requirement
- [ ] ✅ I am ready to check EVERY validation criterion individually
- [ ] ✅ I will run grep searches for systematic verification
- [ ] ✅ I will complete self-test before reporting results

**⚠️ If ANY checkbox is unchecked → STOP and read missing files first**

---

## Requirements

**ALWAYS open and follow**: `../requirements/overall-design-structure.md`

Extract:
- Required sections structure
- Validation criteria (100 points breakdown)
- Pass threshold (≥90/100)

---

## Prerequisites

**MUST validate**:
- [ ] DESIGN.md exists - validate: Check file at `architecture/DESIGN.md`
- [ ] PRD.md exists - validate: Check file at `architecture/PRD.md`
- [ ] PRD.md validated - validate: Score ≥90/100

**If missing**: Run prerequisite workflows first

---

## Steps

### 1. Read Dependencies

Open `architecture/PRD.md`

Extract:
- All actor IDs
- All use case IDs
- Vision statement

### 2. Execute Validation

Follow validation criteria from `overall-design-structure.md`:
- Structure: Required sections/subsections present, correct order
- Completeness: No placeholders, required ID payload blocks present
- Cross-References: All referenced actor/use case/ADR IDs exist
- Domain Model & API Contracts: Links/locations present as required

Calculate total score

### 3. Output Results to Chat

**Format**:
```markdown
## Validation: DESIGN.md

**Score**: {X}/100  
**Status**: PASS | FAIL  
**Threshold**: ≥90/100

---

### Findings

**Structure** ({X}/20):
✅ | ❌ {item}

**Completeness** ({X}/25):
✅ | ❌ {item}

**Cross-References** ({X}/{points}):
✅ | ❌ {item}

**Domain Model & API Contracts** ({X}/{points}):
✅ | ❌ {item}

---

### Recommendations

**High Priority**:
1. {Fix}

---

### Next Steps

{If PASS}: ✅ Run `adr-validate` to validate ADRs, then proceed to `features` workflow

{If FAIL}: ❌ Fix issues, re-validate
```

### 4. Validate `architecture/ADR/` (If DESIGN.md passed)

**If DESIGN.md validation score ≥90**:
- Check if `architecture/ADR/` exists
- If exists: Run `adr-validate` workflow
- If missing: Suggest running `adr` workflow first

**Output**:
```markdown
---

## ADR Validation

{If architecture/ADR/ exists}: Running adr-validate...
{If architecture/ADR/ missing}: ⚠️ architecture/ADR/ not found. Run `adr` workflow to create Architecture Decision Records.
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

**If DESIGN.md PASS and ADR PASS**: `features` workflow

**If DESIGN.md PASS but `architecture/ADR/` missing**: `adr` workflow to create ADRs

**If DESIGN.md FAIL**: Fix DESIGN.md, re-validate
