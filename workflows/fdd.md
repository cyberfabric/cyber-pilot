---
fdd: true
type: workflow
name: FDD Entrypoint
version: 1.0
purpose: Explicitly enable FDD mode (opt-in)
---

# Enable FDD Mode

**Type**: Operation  
**Role**: Any  
**Artifact**: None (conversation context)

---

## Prerequisites

---

## Prerequisite Checklist

- [ ] User explicitly requested enabling FDD (e.g., `/fdd`)
- [ ] Agent has read execution-protocol.md

---

## Overview

Enable FDD in the current conversation explicitly (opt-in), so subsequent requests may be treated as FDD workflow execution and may use FDD adapter discovery.

---

## Steps

### 1. Confirm Enablement

Treat the user invoking this workflow as explicit confirmation that FDD mode should be enabled for this conversation.

Do not ask for additional confirmation.

### 2. Discover Adapter (Read-Only)

Discover the project adapter using the fdd tool adapter discovery.

If adapter is FOUND:
- Open and follow `{adapter_dir}/AGENTS.md`

If adapter is NOT_FOUND:
- Continue with FDD core defaults only

### 3. Establish Strict Opt-In for Artifacts

If the user opens/edits files that look like FDD artifacts (based on `{adapter-dir}/artifacts.json` in the target project):
- Propose enabling FDD if it is not enabled
- MUST NOT enable FDD automatically

### 4. Route Next Request

Display adapter status and available workflows:

```
FDD Mode Enabled

Adapter: {FOUND at path | NOT_FOUND}

Available workflows:
| Command    | Description |
|------------|-------------|
| generate   | Create/update artifacts or implement code |
| validate   | Validate artifacts or code |
| adapter    | Create/update project adapter |
| rules      | Generate rules packages |

What would you like to do?
```

---

## Validation Criteria

- Workflow structure contains required sections

---

## Validation

---

## Validation Checklist

- [ ] Workflow structure is valid

---

## Next Steps

| Command | Description |
|---------|-------------|
| `generate` | Create or update artifacts (PRD, DESIGN, FEATURES, ADR, Feature) or implement code from design |
| `validate` | Validate artifacts against templates or code against design requirements |
| `adapter` | Create or update project adapter (artifacts.json, specs, AGENTS.md) |
| `rules` | Generate rules packages for custom artifact types |
