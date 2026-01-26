---
fdd: true
type: workflow
name: Adapter Agents
version: 1.0
purpose: Configure or update AI agent integration for FDD
---

# Configure or Update AI Agent Integration

**Type**: Operation  
**Role**: Project Manager  
**Artifact**: AI agent configuration files

---

## Prerequisite Checklist

- [ ] Agent has read execution-protocol.md
- [ ] Agent has read workflow-execution.md
- [ ] Agent understands this workflow's purpose

---

## Overview

This workflow generates agent-specific integration files that proxy back to the canonical FDD workflows and the `fdd` skill.

It is intentionally implemented as a thin wrapper around the deterministic `fdd` generators:
- `agent-workflows`
- `agent-skills`

---



ALWAYS open and follow `../requirements/workflow-execution.md` WHEN executing this workflow

## Requirements

**ALWAYS open and follow**: `../.adapter/specs/patterns.md` (if adapter exists)

Extract adapter conventions if available

---

## Prerequisites

**Can run standalone** without adapter.

If an adapter exists, agent integrations should point the agent to read `{adapter-directory}/AGENTS.md` via the canonical FDD navigation rules.

---

## Steps

### 1. Select Agent

Ask the user for the agent key.

**Supported agents**:
- `windsurf`
- `cursor`
- `claude`
- `copilot`

Store as: `AGENT`

### 2. Preview Changes (Dry Run)

Run both generators in dry-run mode:

```bash
python3 skills/fdd/scripts/fdd.py agent-workflows --agent {AGENT} --dry-run
python3 skills/fdd/scripts/fdd.py agent-skills --agent {AGENT} --dry-run
```

Interpret results:
- If both exit with code `0`, the config is present and the planned changes are shown.
- If either exits with code `2` (`CONFIG_INCOMPLETE`), follow Step 3.

### 3. Unknown Agent / Incomplete Config Handling

If the agent is unknown or the config is incomplete:

1. Run the command without `--dry-run` once to write a stub config:

```bash
python3 skills/fdd/scripts/fdd.py agent-workflows --agent {AGENT}
python3 skills/fdd/scripts/fdd.py agent-skills --agent {AGENT}
```

2. Open the generated config files:
- `fdd-agent-workflows.json`
- `fdd-agent-skills.json`

3. Fill in the required fields for `{AGENT}` and re-run Step 2.

### 4. Apply Changes

After the user confirms the dry-run output, run the generators (no dry-run):

```bash
python3 skills/fdd/scripts/fdd.py agent-workflows --agent {AGENT}
python3 skills/fdd/scripts/fdd.py agent-skills --agent {AGENT}
```

### 5. Validate Result

Verify the generated files exist and re-run dry-run to ensure everything is up-to-date:

```bash
python3 skills/fdd/scripts/fdd.py agent-workflows --agent {AGENT} --dry-run
python3 skills/fdd/scripts/fdd.py agent-skills --agent {AGENT} --dry-run
```

---

## Configuration Examples

This workflow intentionally does not hardcode agent file formats.

All agent-specific file paths and templates are defined in:
- `fdd-agent-workflows.json`
- `fdd-agent-skills.json`

---

## Validation

**Manual validation**:
1. Agent config file(s) created
2. Contains FDD references
3. Contains workflow navigation
4. Contains adapter references (if applicable)

**Functional validation**:
- Ask agent about workflows
- Agent should reference FDD system
- Agent should suggest appropriate workflow

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

**Configuration complete**:
- AI agent now FDD-aware
- Will suggest workflows automatically
- Will reference adapter conventions

**Start FDD work**:
- `prd` - Define product requirements
- `adapter` - Configure adapter (if not yet done)
