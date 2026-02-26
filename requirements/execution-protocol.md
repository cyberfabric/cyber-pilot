---
cypilot: true
type: requirement
name: Execution Protocol
version: 2.0
purpose: Common protocol executed by generate.md and analyze.md workflows
---

# Execution Protocol

**Type**: Protocol (embedded in other workflows)

---

## Table of Contents

- [Overview](#overview)
- [Execution Protocol Violations](#-execution-protocol-violations)
- [Compaction Recovery](#-compaction-recovery)
- [Cypilot Mode Detection](#cypilot-mode-detection)
- [Rules Mode Detection](#rules-mode-detection)
- [Discover Cypilot](#discover-cypilot)
- [Understand Registry](#understand-registry)
- [Clarify Intent](#clarify-intent)
- [Load Rules](#load-rules)
- [Cross-Reference Awareness](#cross-reference-awareness)
- [Context Usage](#context-usage)
- [Error Handling](#error-handling)
- [Consolidated Validation Checklist](#consolidated-validation-checklist)

---

## Overview

Common steps shared by `generate.md` and `analyze.md`. Both workflows MUST execute this protocol before their specific logic.

---
## ⚠️ Execution Protocol Violations

**If agent skips execution-protocol.md**: workflow execution is **INVALID** and output must be **DISCARDED**.

**Common violations**:
1. ❌ Not reading this protocol first
2. ❌ Not running `cypilot info`
3. ❌ Not following invoked workflow rules (`generate.md` / `analyze.md`)

**Recovery**:
1. Acknowledge violation + what was skipped
2. Discard invalid output
3. Restart: re-run protocol + show compliance report

---

## 🔄 Compaction Recovery

**Problem**: After context compaction (conversation summarization), agent may lose:
- Knowledge that Cypilot workflow was active
- List of loaded specs
- Current workflow phase

**Detection signals** (agent should suspect compaction occurred):
- Conversation starts with "This session is being continued from a previous conversation"
- Summary mentions `/cypilot-generate`, `/cypilot-analyze`, or other Cypilot commands
- Todo list contains Cypilot-related tasks in progress

**Recovery protocol**:

1. Detect compaction from conversation summary signals
2. Re-run: `cypilot info` + load required specs from `{cypilot_path}/.gen/AGENTS.md`
3. Announce restored context (workflow, target, loaded specs), then continue

**Agent MUST NOT**:
- Continue Cypilot work without re-loading specs after compaction
- Assume specs are "still loaded" from before compaction
- Skip protocol because "it was already done"

---

## Cypilot Mode Detection

**Default behavior**:
- Treat request as workflow execution ONLY when Cypilot is enabled
- User invoking Cypilot workflow (`/cypilot`, `/prd`, `/design`, etc.) = Cypilot enabled
- User requesting `/cypilot off` = Cypilot disabled for conversation
- When disabled, behave as normal coding assistant

**Announce Cypilot mode** (non-blocking):
```
Cypilot mode: ENABLED. To disable: /cypilot off
```

---

## Rules Mode Detection

After cypilot discovery, determine **Rules Mode**:

### Rules Mode: STRICT (Cypilot rules enabled)

**Condition**: `artifacts.toml` found AND contains `rules` section AND target artifact/code matches registered system.

**Behavior**:
- Full protocol enforcement
- Mandatory semantic validation
- Evidence requirements enforced
- Anti-pattern detection active
- Agent compliance protocol applies (see `agent-compliance.md`)

**Announce**:
```
Rules Mode: STRICT (cypilot-sdlc rules loaded)
→ Full validation protocol enforced
```

### Rules Mode: BOOTSTRAP (new project)

ALWAYS detect BOOTSTRAP mode WHEN cypilot found AND `artifacts.toml` has empty `systems[].artifacts` array

ALWAYS read `kits` section from `artifacts.toml` WHEN BOOTSTRAP mode detected

ALWAYS scan `{kit.path}/artifacts/` directories WHEN listing available artifact kinds

ALWAYS determine project type WHEN BOOTSTRAP mode:
- **GREENFIELD**: No existing source code — starting fresh, design-first approach
- **BROWNFIELD**: Existing source code — needs reverse-engineering to extract design from code

ALWAYS detect GREENFIELD WHEN codebase directories in `artifacts.toml` are empty OR contain only config files (no `.py`, `.ts`, `.js`, `.go`, `.rs`, `.java` etc.)

ALWAYS detect BROWNFIELD WHEN codebase directories contain source code files

ALWAYS show welcome message with project type WHEN BOOTSTRAP mode:
```
🚀 New Project Detected ({GREENFIELD|BROWNFIELD})

Available kits:
• {kit_name} ({kit.path})
  Artifacts: {kinds from kit.path/artifacts/}

→ `cypilot generate <KIND>` to create your first artifact
```

ALWAYS proceed with generate workflow without blocking WHEN user requests artifact generation in BOOTSTRAP mode

NEVER trigger reverse-engineering WHEN GREENFIELD — there is no code to analyze

ALWAYS offer reverse-engineering WHEN BROWNFIELD AND config has no specs — existing code should inform design artifacts

NEVER offer reverse-engineering WHEN config already has specs — project analysis already done

NEVER show warnings or "reduced rigor" messages WHEN in BOOTSTRAP mode

---

### Rules Mode: RELAXED (no cypilot)

ALWAYS detect RELAXED mode WHEN no cypilot found OR no `kits` in artifacts.toml

ALWAYS propose initialization WHEN RELAXED mode:
```
Cypilot not configured

→ `cypilot init` to initialize for this project
```

ALWAYS proceed as normal coding assistant WHEN user declines initialization

### Rules Mode Summary

| Aspect | STRICT | BOOTSTRAP | RELAXED |
|--------|--------|-----------|---------|
| Condition | Artifacts registered | Cypilot found, no artifacts | No cypilot |
| Behavior | Full enforcement | Welcome + propose SDLC | Suggest init |
| Template enforcement | ✓ Required | ✓ Required | ✗ None |
| Checklist validation | ✓ Mandatory | ✓ Mandatory | ✗ Skipped |
| Reverse-engineering | When needed | BROWNFIELD only | N/A |
| Blocking | No | No | No |
| Next step | Continue workflow | `cypilot generate <KIND>` | `cypilot init` |

### Project Type (BOOTSTRAP mode)

| Type | Condition | Reverse-engineering |
|------|-----------|---------------------|
| **GREENFIELD** | No source code in codebase dirs | ✗ Skip — nothing to analyze |
| **BROWNFIELD** | Source code exists | ✓ Offer — code informs design |

---

## Discover Cypilot

```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py info --root {PROJECT_ROOT} --cypilot-root {cypilot_path}
```

**Parse output**: `status`, `cypilot_dir`, `project_root`, `specs`, `rules`

**If FOUND**: Load `{cypilot_path}/.gen/AGENTS.md` for navigation rules

**If NOT_FOUND**: Suggest running `cypilot init` to bootstrap

---

## Understand Registry

**MUST read** `{cypilot_path}/config/artifacts.toml`:

1. **Rules**: What rule packages exist (`cypilot-sdlc`, `cpt-core`, etc.)
2. **Systems**: What systems are registered and their hierarchy
3. **Artifacts**: What artifacts exist, their kinds, and traceability settings
4. **Codebase**: What code directories are tracked

**MUST browse** rules directories:
- `{rules-path}/artifacts/` — available artifact kinds (PRD, DESIGN, ADR, etc.)
- `{rules-path}/codebase/` — available code checklists

**Store context**: rules+paths, systems, artifact kinds, traceability settings

---

## Clarify Intent

**If unclear from context, ask user**:

### 1. Kit Context
Ask which kit to use (or manual dependencies) if unclear.

### 2. Target Type
Ask whether target is **Artifact** or **Code** (and which kind/path).

### 3. Specific System (if using kit)
Ask which system (from `artifacts.toml`) if using a kit and system is unclear.

**If context is clear**: proceed silently, don't ask unnecessary questions.

---

## Load Kits

**After determining target type**:

### 1. Resolve Kit Package

From `artifacts.toml`:

```
1. Find system containing target artifact
2. Get kit name: system.kit (e.g., "cypilot-sdlc")
3. Look up path: artifacts.toml.kits[kit_name].path
4. KIT_BASE = resolved path (could be anything: "kits/sdlc", "my-kit", etc.)
```

**Example**:
```json
{
  "kits": {
    "cypilot-sdlc": { "path": "kits/sdlc" }
  },
  "systems": [{
    "name": "MySystem",
    "kit": "cypilot-sdlc"
  }]
}
```
→ `KIT_BASE = "kits/sdlc"`

### 2. Determine Artifact Type

From explicit parameter or artifacts.toml lookup:

| Source | Resolution |
|--------|------------|
| `cypilot generate PRD` | Explicit: PRD |
| `cypilot analyze {path}` | Lookup: `artifacts.toml.systems[].artifacts[path].kind` |
| Path in `codebase[]` | CODE |

### 3. Load Rules.md

```
KITS_PATH = {KIT_BASE}/artifacts/{ARTIFACT_TYPE}/rules.md
```

For CODE:
```
KITS_PATH = {KIT_BASE}/codebase/rules.md
```

**MUST read rules.md** and parse:
- **Dependencies** section → files to load
- **Requirements** section → confirm understanding
- **Tasks** section (for generate) → execution steps
- **Validation** section (for validate) → validation checks

### 4. Load Dependencies from Rules

Parse Dependencies section:
```markdown
**Dependencies**:
- `template.md` — required structure
- `checklist.md` — semantic quality criteria
- `examples/example.md` — reference implementation
```

For each dependency:
1. Resolve path relative to rules.md location
2. Load file content
3. Store for workflow use

### 5. Confirm Requirements

Agent reads Requirements section and confirms:
```
I understand the following requirements for {ARTIFACT_TYPE}:
- Structural: {list}
- Semantic: {list}
- Versioning: {list}
- Traceability: {list}
```

**Store loaded context**:
- `KIT_BASE` — base path from artifacts.toml
- `KITS_PATH` — full path to rules.md
- `TEMPLATE` — loaded template content
- `CHECKLIST` — loaded checklist content
- `EXAMPLE` — loaded example content
- `REQUIREMENTS` — parsed requirements from rules

### 6. Load Config Specs

**After rules loaded and target type determined**, load applicable config specs:

**Read AGENTS.md** at `{cypilot_path}/.gen/AGENTS.md`

**Parse WHEN clauses** matching current context:

```
For each line matching: ALWAYS open and follow `{spec}` WHEN Cypilot follows rules `{rule}` for {target}
  IF {rule} == loaded rules ID (e.g., "cypilot-sdlc"):
    IF target includes current artifact kind:
      → Open and follow {spec}
    IF target includes "codebase" AND working on code:
      → Open and follow {spec}
```

**Example resolution**:

- Loaded rules: `cypilot-sdlc`
- Target: `DESIGN`
- Match WHEN clauses for that ruleset/target
- Open matched specs (e.g. `specs/tech-stack.md`, `specs/domain-model.md`)

**Store loaded config specs**:
- `CONFIG_SPECS` — list of loaded spec paths
- Specs content available for workflow guidance

**Backward compatibility**: If config uses legacy format (`WHEN executing workflows: ...`), map workflow names to artifact kinds internally.

---

---

## Cross-Reference Awareness

**Before proceeding, understand**:
- Parent artifacts that might be referenced
- Child artifacts that depend on target
- Related code that implements target (if artifact)
- Related artifacts that code implements (if code)

---

## Context Usage

**MUST**:
- Use current project context for proposals
- Reference existing artifacts when relevant
- Show reasoning for proposals

**MUST NOT**:
- Make up information
- Assume without context
- Proceed without user confirmation (operations)

---

## Error Handling

### Cypilot Not Found

**If cypilot not found**:
```
⚠️ Cypilot not configured
→ Run `cypilot init` to initialize
```
**Action**: STOP.

### artifacts.toml Parse Error

**If artifacts.toml is malformed**:
```
⚠️ Cannot parse artifacts.toml: {parse error}
→ Fix JSON syntax errors in {cypilot_path}/config/artifacts.toml
→ Validate with: python3 -m json.tool artifacts.toml
```
**Action**: STOP.

### Rules.md Not Found

**If rules.md cannot be loaded**:
```
⚠️ Rules file not found: {KITS_PATH}
→ Verify kit package exists at {KIT_BASE}
→ Check artifacts.toml kits section has correct path
→ Run `cypilot init --force` to regenerate
```
**Action**: STOP.

### Template/Checklist Not Found

**If dependency from rules.md not found**:
```
⚠️ Dependency not found: {dependency_path}
→ Referenced in: {KITS_PATH}
→ Expected at: {resolved_path}
→ Verify kit package is complete
```
**Action**: STOP.

### System Not Registered

**If target artifact's system not in artifacts.toml**:
```
⚠️ System not found: {system_name}
→ Registered systems: {list from artifacts.toml}
→ Options:
  1. Register system via `cypilot init`
  2. Use existing system
  3. Continue in RELAXED mode (no rules enforcement)
```
**Action**: Prompt user to choose.

### Artifact Kind Not Supported

**If artifact kind not in kit package**:
```
⚠️ Unsupported artifact kind: {KIND}
→ Available kinds in {KIT_BASE}: {list}
→ Options:
  1. Use supported kind
  2. Create custom templates for {KIND}
  3. Continue in RELAXED mode
```
**Action**: Prompt user to choose.

---

## Consolidated Validation Checklist

**Use this single checklist for all execution-protocol validation.**

### Detection (D)

- D.1 (YES): Cypilot mode detected (agent states Cypilot enabled)
- D.2 (YES): Rules mode determined (STRICT/RELAXED + reason)

### Discovery (DI)

- DI.1 (YES): Cypilot discovery executed (`cypilot info`)
- DI.2 (YES): `artifacts.toml` read/understood (agent lists systems/rules)
- DI.3 (YES): Rules directories explored (agent lists artifact kinds)

### Clarification (CL)

- CL.1 (YES): Target type clarified (artifact or code)
- CL.2 (YES): Artifact type determined (PRD, DESIGN, etc.)
- CL.3 (CONDITIONAL): System context clarified (when using rules)
- CL.4 (CONDITIONAL): Rules context clarified (when multiple rules)

### Loading (L)

- L.1 (YES): `KITS_PATH` resolved (correct `RULES.md`)
- L.2 (YES): Dependencies loaded (template/checklist/example)
- L.3 (YES): Requirements confirmed (agent enumerates requirements)
- L.4 (CONDITIONAL): Config specs loaded (matched WHEN clauses)

### Context (C)

- C.1 (YES): Cross-references understood (parent/child/related artifacts)
- C.2 (YES): Project context available (can reference project specifics)

### Final (F)

- F.1 (YES): D.1–D.2 pass
- F.2 (YES): DI.1–DI.3 pass
- F.3 (YES): CL.1–CL.4 pass (apply conditionals)
- F.4 (YES): L.1–L.4 pass (apply conditionals)
- F.5 (YES): C.1–C.2 pass
- F.6 (YES): Ready for workflow-specific logic
