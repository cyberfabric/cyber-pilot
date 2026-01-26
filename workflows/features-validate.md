---
fdd: true
type: workflow
name: Features Validate
version: 1.0
purpose: Validate features manifest
---

# Validate Features Manifest

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
- [ ] ✅ Open and follow `../requirements/features-manifest-structure.md` (This workflow's requirements)
- [ ] ✅ Check adapter initialization (`.fdd-config.json` exists and adapter directory exists per `fdd adapter-info`)
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

**ALWAYS open and follow**: `../requirements/features-manifest-structure.md`

Extract:
- Required structure
- Validation criteria (100 points breakdown)
- Pass threshold (≥95/100)

---

## Prerequisites

**MUST validate**:
- [ ] FEATURES.md exists - validate: Check file at `architecture/features/FEATURES.md`
- [ ] DESIGN.md exists - validate: Check file at `architecture/DESIGN.md`
- [ ] DESIGN.md validated - validate: Deterministic validator PASS (`fdd validate`, including traceability with PRD.md and `architecture/ADR/`) and score threshold met (≥90/100 if scoring is reported)

**If missing**: Run prerequisite workflows

---

## Steps

### 1. Read Dependencies

Open `architecture/DESIGN.md`

Extract:
- All requirement IDs (Section B)

### 2. Run Deterministic Gate

Run the deterministic validator for prerequisites and the target artifact.

**Commands** (run from repo root):
```bash
python3 skills/fdd/scripts/fdd.py validate --artifact architecture/DESIGN.md --prdarchitecture/PRD.md --adr ADR
python3 skills/fdd/scripts/fdd.py validate --artifact architecture/features/FEATURES.md --design architecture/DESIGN.md
```

**MUST** include the raw JSON output of these commands in the chat under a "Deterministic Gate Output" subsection.

**If FAIL**: Stop and report workflow FAIL.

**If PASS**: Continue. Deterministic PASS is NOT workflow completion.

### 3. Execute Validation

Follow validation criteria from `features-manifest-structure.md`:
- Structure (20 pts): Required sections present
- Feature Definitions (30 pts): All features have ID, name, purpose, scope
- Coverage (30 pts): All DESIGN.md requirements covered by features
- Dependencies (20 pts): Valid, no circular dependencies

Calculate total score

### 4. Output Results to Chat

**Format**:
```markdown
## Validation: FEATURES.md

**Score**: {X}/100  
**Status**: PASS | FAIL  
**Threshold**: ≥95/100

---

### Findings

**Structure** ({X}/20):
✅ | ❌ {item}

**Feature Definitions** ({X}/30):
✅ | ❌ {item}

**Coverage** ({X}/30):
✅ | ❌ {item}

**Dependencies** ({X}/20):
✅ | ❌ {item}

---

### Coverage Analysis

**Requirements covered**: {X}/{total} ({percentage}%)
**Orphaned requirements**: {list if any}

---

### Recommendations

**High Priority**:
1. {Fix}

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

**If PASS**: `feature` workflow (design first feature from FEATURES.md)

**If FAIL**: Fix FEATURES.md issues, re-run `features-validate`
