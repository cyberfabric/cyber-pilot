---
fdd: true
type: workflow
name: Rules
version: 1.0
purpose: Create or edit FDD rules (templates, checklists, workflows, examples)
---

# Rules

**Type**: Navigation
**Role**: Architect

---

## Prerequisite Checklist

- [ ] Agent has read execution-protocol.md
- [ ] Agent understands this workflow's purpose

---

## Overview

This workflow creates or validates FDD rule packages. It collects context and delegates to specialized workflows in `rules/core/`.

---

ALWAYS open and follow `../requirements/execution-protocol.md` WHEN executing this workflow

---

## Prerequisites

**MUST validate**:
- [ ] Adapter exists - validate: Run `fdd adapter-info`
- [ ] `rules/core/` directory exists - validate: Check path

**If missing**: Run `adapter` workflow first.

---

## What Are FDD Rules?

FDD Rules define how artifacts are structured and validated. A rule package contains:

| Artifact | Purpose | Location |
|----------|---------|----------|
| **Template** | Structure definition with FDD markers | `{rule.path}/{KIND}.template.md` |
| **Checklist** | Validation criteria | `{rule.path}/checklists/{KIND}.md` |
| **Generate Workflow** | How to create/update artifacts | `{rule.path}/workflows/{kind}.md` |
| **Validate Workflow** | How to validate artifacts | `{rule.path}/workflows/{kind}-validate.md` |
| **Example** | Reference implementation | `{rule.path}/examples/{kind}/example.md` |

Rules are registered in `{adapter-dir}/artifacts.json` under the `rules` section.

---

## Steps

### 1. Determine Operation

Ask: **What do you want to do?**

- **Generate** → Go to Step 2
- **Validate** → Go to Step 4

---

### 2. Select Rule Package (Generate)

**Create new**:
- Ask: Rule ID (e.g., `my-rules`)
- Ask: Path (e.g., `rules/my-rules`)
- Register in `artifacts.json` → `rules` section
- Go to Step 3

**Edit existing**:
- Read `{adapter-dir}/artifacts.json` → `rules`
- Ask: Which rule package?
- Go to Step 3

---

### 3. Select Artifact Type (Generate)

Ask: **What artifact type to generate?**

- **Template** → Delegate to `rules/core/template/workflows/generate.md`
- **Checklist** → Delegate to `rules/core/checklist/workflows/generate.md`
- **Generate Workflow** → Delegate to `rules/core/generate/workflows/generate.md`
- **Validate Workflow** → Delegate to `rules/core/validate/workflows/generate.md`
- **Example** → Delegate to `rules/core/examples/workflows/generate.md`

---

### 4. Select Target (Validate)

- Read `{adapter-dir}/artifacts.json` → `rules`
- Ask: Which rule package?
- Ask: Which artifact type?
- Delegate to `rules/core/{type}/workflows/validate.md`

---

## Delegation

All generation and validation logic lives in `rules/core/`. This workflow only navigates.

```
rules/core/
├── template/workflows/{generate,validate}.md
├── checklist/workflows/{generate,validate}.md
├── generate/workflows/{generate,validate}.md
├── validate/workflows/{generate,validate}.md
└── examples/workflows/{generate,validate}.md
```

After collecting answers, open and follow the appropriate workflow file.

---

## Quick Reference

| User Intent | Workflow to Delegate |
|-------------|---------------------|
| Create template | `rules/core/template/workflows/generate.md` |
| Validate template | `rules/core/template/workflows/validate.md` |
| Create checklist | `rules/core/checklist/workflows/generate.md` |
| Validate checklist | `rules/core/checklist/workflows/validate.md` |
| Create generation workflow | `rules/core/generate/workflows/generate.md` |
| Validate generation workflow | `rules/core/generate/workflows/validate.md` |
| Create validation workflow | `rules/core/validate/workflows/generate.md` |
| Validate validation workflow | `rules/core/validate/workflows/validate.md` |
| Create example | `rules/core/examples/workflows/generate.md` |
| Validate example | `rules/core/examples/workflows/validate.md` |

---

## Validation Criteria

- Correct workflow was selected based on user intent
- All required context was collected before delegation
- Delegated workflow completed successfully
- If new rule package: registered in `artifacts.json`

---

## Validation Checklist

- [ ] Adapter check passed
- [ ] User intent determined (generate/validate)
- [ ] Target rule package identified
- [ ] Artifact type selected
- [ ] Delegated to correct workflow in `rules/core/`
- [ ] Delegated workflow reported success
