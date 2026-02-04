---
spider: true
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
- [Spider Mode Detection](#spider-mode-detection)
- [Rules Mode Detection](#rules-mode-detection)
- [Discover Adapter](#discover-adapter)
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
2. ❌ Not running `spider adapter-info`
3. ❌ Not following invoked workflow rules (`generate.md` / `analyze.md`)

**Recovery**:
1. Acknowledge violation + what was skipped
2. Discard invalid output
3. Restart: re-run protocol + show compliance report

---

## 🔄 Compaction Recovery

**Problem**: After context compaction (conversation summarization), agent may lose:
- Knowledge that Spider workflow was active
- List of loaded specs
- Current workflow phase

**Detection signals** (agent should suspect compaction occurred):
- Conversation starts with "This session is being continued from a previous conversation"
- Summary mentions `/spider-generate`, `/spider-analyze`, or other Spider commands
- Todo list contains Spider-related tasks in progress

**Recovery protocol**:

1. Detect compaction from conversation summary signals
2. Re-run: `spider adapter-info` + load required specs from `{spider_adapter_path}/AGENTS.md`
3. Announce restored context (workflow, target, loaded specs), then continue

**Agent MUST NOT**:
- Continue Spider work without re-loading specs after compaction
- Assume specs are "still loaded" from before compaction
- Skip protocol because "it was already done"

---

## Spider Mode Detection

**Default behavior**:
- Treat request as workflow execution ONLY when Spider is enabled
- User invoking Spider workflow (`/spider`, `/prd`, `/design`, etc.) = Spider enabled
- User requesting `/spider off` = Spider disabled for conversation
- When disabled, behave as normal coding assistant

**Announce Spider mode** (non-blocking):
```
Spider mode: ENABLED. To disable: /spider off
```

---

## Rules Mode Detection

After adapter discovery, determine **Rules Mode**:

### Rules Mode: STRICT (Spider rules enabled)

**Condition**: `artifacts.json` found AND contains `rules` section AND target artifact/code matches registered system.

**Behavior**:
- Full protocol enforcement
- Mandatory semantic validation
- Evidence requirements enforced
- Anti-pattern detection active
- Agent compliance protocol applies (see `agent-compliance.md`)

**Announce**:
```
Rules Mode: STRICT (spider-sdlc rules loaded)
→ Full validation protocol enforced
```

### Rules Mode: BOOTSTRAP (new project)

ALWAYS detect BOOTSTRAP mode WHEN adapter found AND `artifacts.json` has empty `systems[].artifacts` array

ALWAYS read `weavers` section from `artifacts.json` WHEN BOOTSTRAP mode detected

ALWAYS scan `{weaver.path}/artifacts/` directories WHEN listing available artifact kinds

ALWAYS determine project type WHEN BOOTSTRAP mode:
- **GREENFIELD**: No existing source code — starting fresh, design-first approach
- **BROWNFIELD**: Existing source code — needs reverse-engineering to extract design from code

ALWAYS detect GREENFIELD WHEN codebase directories in `artifacts.json` are empty OR contain only config files (no `.py`, `.ts`, `.js`, `.go`, `.rs`, `.java` etc.)

ALWAYS detect BROWNFIELD WHEN codebase directories contain source code files

ALWAYS show welcome message with project type WHEN BOOTSTRAP mode:
```
🚀 New Project Detected ({GREENFIELD|BROWNFIELD})

Available weavers:
• {weaver_name} ({weaver.path})
  Artifacts: {kinds from weaver.path/artifacts/}

→ `spider generate <KIND>` to create your first artifact
```

ALWAYS proceed with generate workflow without blocking WHEN user requests artifact generation in BOOTSTRAP mode

NEVER trigger reverse-engineering WHEN GREENFIELD — there is no code to analyze

ALWAYS offer reverse-engineering WHEN BROWNFIELD AND adapter has no specs — existing code should inform design artifacts

NEVER offer reverse-engineering WHEN adapter already has specs — project analysis already done

NEVER show warnings or "reduced rigor" messages WHEN in BOOTSTRAP mode

---

### Rules Mode: RELAXED (no adapter)

ALWAYS detect RELAXED mode WHEN no adapter found OR no `weavers` in artifacts.json

ALWAYS propose initialization WHEN RELAXED mode:
```
Spider adapter not configured

→ `spider init` to initialize for this project
```

ALWAYS proceed as normal coding assistant WHEN user declines initialization

### Rules Mode Summary

| Aspect | STRICT | BOOTSTRAP | RELAXED |
|--------|--------|-----------|---------|
| Condition | Artifacts registered | Adapter found, no artifacts | No adapter |
| Behavior | Full enforcement | Welcome + propose SDLC | Suggest init |
| Template enforcement | ✓ Required | ✓ Required | ✗ None |
| Checklist validation | ✓ Mandatory | ✓ Mandatory | ✗ Skipped |
| Reverse-engineering | When needed | BROWNFIELD only | N/A |
| Blocking | No | No | No |
| Next step | Continue workflow | `spider generate <KIND>` | `spider init` |

### Project Type (BOOTSTRAP mode)

| Type | Condition | Reverse-engineering |
|------|-----------|---------------------|
| **GREENFIELD** | No source code in codebase dirs | ✗ Skip — nothing to analyze |
| **BROWNFIELD** | Source code exists | ✓ Offer — code informs design |

---

## Discover Adapter

```bash
python3 {spider_path}/skills/spider/scripts/spider.py adapter-info --root {PROJECT_ROOT} --spider-root {spider_path}
```

**Parse output**: `status`, `adapter_dir`, `project_root`, `specs`, `rules`

**If FOUND**: Load `{spider_adapter_path}/AGENTS.md` for navigation rules

**If NOT_FOUND**: Suggest running `/spider-adapter` to bootstrap

---

## Understand Registry

**MUST read** `{spider_adapter_path}/artifacts.json`:

1. **Rules**: What rule packages exist (`spider-sdlc`, `spd-core`, etc.)
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

### 1. Weaver Context
Ask which weaver to use (or manual dependencies) if unclear.

### 2. Target Type
Ask whether target is **Artifact** or **Code** (and which kind/path).

### 3. Specific System (if using weaver)
Ask which system (from `artifacts.json`) if using a weaver and system is unclear.

**If context is clear**: proceed silently, don't ask unnecessary questions.

---

## Load Weavers

**After determining target type**:

### 1. Resolve Weaver Package

From `artifacts.json`:

```
1. Find system containing target artifact
2. Get weaver name: system.weaver (e.g., "spider-sdlc")
3. Look up path: artifacts.json.weavers[weaver_name].path
4. WEAVER_BASE = resolved path (could be anything: "weavers/sdlc", "my-weaver", etc.)
```

**Example**:
```json
{
  "weavers": {
    "spider-sdlc": { "path": "weavers/sdlc" }
  },
  "systems": [{
    "name": "MySystem",
    "weaver": "spider-sdlc"
  }]
}
```
→ `WEAVER_BASE = "weavers/sdlc"`

### 2. Determine Artifact Type

From explicit parameter or artifacts.json lookup:

| Source | Resolution |
|--------|------------|
| `spider generate PRD` | Explicit: PRD |
| `spider analyze {path}` | Lookup: `artifacts.json.systems[].artifacts[path].kind` |
| Path in `codebase[]` | CODE |

### 3. Load Rules.md

```
WEAVERS_PATH = {WEAVER_BASE}/artifacts/{ARTIFACT_TYPE}/rules.md
```

For CODE:
```
WEAVERS_PATH = {WEAVER_BASE}/codebase/rules.md
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
- `WEAVER_BASE` — base path from artifacts.json
- `WEAVERS_PATH` — full path to rules.md
- `TEMPLATE` — loaded template content
- `CHECKLIST` — loaded checklist content
- `EXAMPLE` — loaded example content
- `REQUIREMENTS` — parsed requirements from rules

### 6. Load Adapter Specs

**After rules loaded and target type determined**, load applicable adapter specs:

**Read adapter AGENTS.md** at `{spider_adapter_path}/AGENTS.md`

**Parse WHEN clauses** matching current context:

```
For each line matching: ALWAYS open and follow `{spec}` WHEN Spider follows rules `{rule}` for {target}
  IF {rule} == loaded rules ID (e.g., "spider-sdlc"):
    IF target includes current artifact kind:
      → Open and follow {spec}
    IF target includes "codebase" AND working on code:
      → Open and follow {spec}
```

**Example resolution**:

- Loaded rules: `spider-sdlc`
- Target: `DESIGN`
- Match WHEN clauses for that ruleset/target
- Open matched specs (e.g. `specs/tech-stack.md`, `specs/domain-model.md`)

**Store loaded adapter specs**:
- `ADAPTER_DECOMPOSITION` — list of loaded spec paths
- Specs content available for workflow guidance

**Backward compatibility**: If adapter uses legacy format (`WHEN executing workflows: ...`), map workflow names to artifact kinds internally.

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

### Adapter Not Found

**If adapter not found**:
```
⚠️ Adapter not found
→ Run /spider-adapter to bootstrap
```
**Action**: STOP.

### artifacts.json Parse Error

**If artifacts.json is malformed**:
```
⚠️ Cannot parse artifacts.json: {parse error}
→ Fix JSON syntax errors in {spider_adapter_path}/artifacts.json
→ Validate with: python3 -m json.tool artifacts.json
```
**Action**: STOP.

### Rules.md Not Found

**If rules.md cannot be loaded**:
```
⚠️ Rules file not found: {WEAVERS_PATH}
→ Verify weaver package exists at {WEAVER_BASE}
→ Check artifacts.json weavers section has correct path
→ Run /spider-adapter --rescan to regenerate
```
**Action**: STOP.

### Template/Checklist Not Found

**If dependency from rules.md not found**:
```
⚠️ Dependency not found: {dependency_path}
→ Referenced in: {WEAVERS_PATH}
→ Expected at: {resolved_path}
→ Verify weaver package is complete
```
**Action**: STOP.

### System Not Registered

**If target artifact's system not in artifacts.json**:
```
⚠️ System not found: {system_name}
→ Registered systems: {list from artifacts.json}
→ Options:
  1. Register system via /spider-adapter
  2. Use existing system
  3. Continue in RELAXED mode (no rules enforcement)
```
**Action**: Prompt user to choose.

### Artifact Kind Not Supported

**If artifact kind not in weaver package**:
```
⚠️ Unsupported artifact kind: {KIND}
→ Available kinds in {WEAVER_BASE}: {list}
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

- D.1 (YES): Spider mode detected (agent states Spider enabled)
- D.2 (YES): Rules mode determined (STRICT/RELAXED + reason)

### Discovery (DI)

- DI.1 (YES): Adapter discovery executed (`spider adapter-info`)
- DI.2 (YES): `artifacts.json` read/understood (agent lists systems/rules)
- DI.3 (YES): Rules directories explored (agent lists artifact kinds)

### Clarification (CL)

- CL.1 (YES): Target type clarified (artifact or code)
- CL.2 (YES): Artifact type determined (PRD, DESIGN, etc.)
- CL.3 (CONDITIONAL): System context clarified (when using rules)
- CL.4 (CONDITIONAL): Rules context clarified (when multiple rules)

### Loading (L)

- L.1 (YES): `WEAVERS_PATH` resolved (correct `RULES.md`)
- L.2 (YES): Dependencies loaded (template/checklist/example)
- L.3 (YES): Requirements confirmed (agent enumerates requirements)
- L.4 (CONDITIONAL): Adapter specs loaded (matched WHEN clauses)

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
