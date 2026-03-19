---
cypilot: true
type: requirement
name: Execution Protocol
version: 2.0
purpose: Common protocol executed by generate.md and analyze.md workflows
---

# Execution Protocol

<!-- toc -->

- [Overview](#overview)
- [Violations & Recovery](#violations--recovery)
- [Compaction Recovery](#compaction-recovery)
- [Deterministic Operations](#deterministic-operations)
- [Mode Detection](#mode-detection)
  - [Cypilot Mode](#cypilot-mode)
  - [Rules Mode](#rules-mode)
  - [BOOTSTRAP Requirements](#bootstrap-requirements)
- [Discovery & Loading](#discovery--loading)
  - [Discover Cypilot](#discover-cypilot)
  - [Registry, Intent, and Kit Loading](#registry-intent-and-kit-loading)
- [Cross-Reference & Context Rules](#cross-reference--context-rules)
- [Error Handling](#error-handling)
- [Consolidated Validation Checklist](#consolidated-validation-checklist)

<!-- /toc -->

**Type**: Protocol (embedded in other workflows)

---

## Overview

Common steps shared by `{cypilot_path}/.core/workflows/generate.md` and `{cypilot_path}/.core/workflows/analyze.md`. Both workflows MUST execute this protocol before their specific logic.

## Violations & Recovery

If agent skips `execution-protocol.md`, workflow execution is **INVALID** and output must be **DISCARDED**.

| Violation | Recovery |
|---|---|
| ❌ Not reading this protocol first | Acknowledge violation + what was skipped |
| ❌ Not running `cpt info` | Discard invalid output |
| ❌ Not following invoked workflow rules (`{cypilot_path}/.core/workflows/generate.md` / `{cypilot_path}/.core/workflows/analyze.md`) | Restart: re-run protocol + show compliance report |

## Compaction Recovery

After context compaction, agent may lose active-workflow state, loaded specs, or current phase.

| Detection signals | Recovery protocol |
|---|---|
| Conversation starts with "This session is being continued from a previous conversation" | 1. Detect compaction from summary signals |
| Summary mentions `/cypilot-generate`, `/cypilot-analyze`, or other Cypilot commands | 2. Re-run: `cpt info` + load required specs from `{cypilot_path}/.gen/AGENTS.md` |
| Todo list contains Cypilot-related tasks in progress | 3. Re-extract `variables` dict from `info` output for template variable resolution in kit files |
|  | 4. Announce restored context (workflow, target, loaded specs), then continue |

**Agent MUST NOT**:
- Continue Cypilot work without re-loading specs after compaction
- Assume specs are "still loaded" from before compaction
- Skip protocol because "it was already done"

## Deterministic Operations

**ALWAYS** run `cypilot toc <file>` for ANY Table of Contents generation or update in Markdown files. **NEVER** write TOC manually — agent-generated anchors are unreliable. Manually written TOC = **INVALID output**.

## Mode Detection

### Cypilot Mode

| Topic | Required behavior |
|---|---|
| Default | Treat request as workflow execution ONLY when Cypilot is enabled |
| Enable | User invoking Cypilot workflow (`/cypilot`, `/prd`, `/design`, etc.) = Cypilot enabled |
| Disable | User requesting `/cypilot off` = Cypilot disabled for conversation |
| Disabled behavior | When disabled, behave as normal coding assistant |

Announce Cypilot mode (non-blocking):

```text
Cypilot mode: ENABLED. To disable: /cypilot off
```

### Rules Mode

After Cypilot discovery, determine **Rules Mode**:

| Mode | Detect when | Required behavior | Next step / message |
|---|---|---|---|
| **STRICT** | `artifacts.toml` found AND contains `rules` section AND target artifact/code matches registered system | Full protocol enforcement; mandatory semantic validation; evidence requirements enforced; anti-pattern detection active; Agent compliance protocol applies (see `{cypilot_path}/.core/requirements/agent-compliance.md`) | Announce `Rules Mode: STRICT (cypilot-sdlc rules loaded)` and `→ Full validation protocol enforced` |
| **BOOTSTRAP** | Cypilot found AND `artifacts.toml` has empty `systems[].artifacts` array | See BOOTSTRAP requirements below | Welcome + propose first artifact |
| **RELAXED** | No Cypilot found OR no `kits` in `artifacts.toml` | ALWAYS propose initialization; ALWAYS proceed as normal coding assistant WHEN user declines initialization | `Cypilot not configured` then `→ cpt init to initialize for this project` |

### BOOTSTRAP Requirements

- ALWAYS detect BOOTSTRAP mode WHEN cypilot found AND `artifacts.toml` has empty `systems[].artifacts` array
- ALWAYS read `kits` section from `artifacts.toml` WHEN BOOTSTRAP mode detected
- ALWAYS scan `{kit.path}/artifacts/` directories WHEN listing available artifact kinds
- ALWAYS determine project type WHEN BOOTSTRAP mode:
  - **GREENFIELD**: No existing source code — starting fresh, design-first approach
  - **BROWNFIELD**: Existing source code — needs reverse-engineering to extract design from code
- ALWAYS detect GREENFIELD WHEN codebase directories in `artifacts.toml` are empty OR contain only config files (no `.py`, `.ts`, `.js`, `.go`, `.rs`, `.java` etc.)
- ALWAYS detect BROWNFIELD WHEN codebase directories contain source code files
- ALWAYS show welcome message with project type WHEN BOOTSTRAP mode:

```text
🚀 New Project Detected ({GREENFIELD|BROWNFIELD})

Available kits:
• {kit_name} ({kit.path})
  Artifacts: {kinds from kit.path/artifacts/}

→ `cypilot generate <KIND>` to create your first artifact
```

- ALWAYS proceed with generate workflow without blocking WHEN user requests artifact generation in BOOTSTRAP mode
- NEVER trigger reverse-engineering WHEN GREENFIELD — there is no code to analyze
- ALWAYS offer reverse-engineering WHEN BROWNFIELD AND config has no specs — existing code should inform design artifacts
- NEVER offer reverse-engineering WHEN config already has specs — project analysis already done
- NEVER show warnings or "reduced rigor" messages WHEN in BOOTSTRAP mode

| Project type | Condition | Reverse-engineering |
|---|---|---|
| **GREENFIELD** | No source code in codebase dirs | ✗ Skip — nothing to analyze |
| **BROWNFIELD** | Source code exists | ✓ Offer — code informs design |

## Discovery & Loading

### Discover Cypilot

```bash
cpt info --json --root {PROJECT_ROOT} --cypilot-root {cypilot_path}
```

Parse JSON output: `status`, `cypilot_dir`, `project_root`, `specs`, `rules`, `variables`.

- Store `variables` — it maps every template variable (`{adr_template}`, `{scripts}`, etc.) to its absolute path; use it to resolve `{variable}` references in kit markdown files (AGENTS.md, SKILL.md, rules.md, workflows)
- If FOUND: load `{cypilot_path}/.gen/AGENTS.md` for navigation rules
- If NOT_FOUND: suggest running `cpt init` to bootstrap

### Registry, Intent, and Kit Loading

| Phase | Required Steps | Stored Context |
| --- | --- | --- |
| **Understand Registry** | MUST read `{cypilot_path}/config/artifacts.toml`; identify rules, systems, artifacts, and codebase; MUST inspect the registered kit package path(s) from `artifacts.toml.kits[*].path`, including `artifacts/` and `codebase/` | rules+paths, systems, artifact kinds, traceability settings |
| **Clarify Intent** | If unclear, ask for: 1. kit context, 2. target type (**Artifact** or **Code** and which kind/path), 3. specific system (if using kit). If context is clear, proceed silently | clarified target and system context |
| **Resolve Kit Package** | Find system containing target artifact; get `system.kit`; look up `artifacts.toml.kits[kit_name].path`; set `KIT_BASE` | `KIT_BASE` |
| **Determine Artifact Type** | Resolve from explicit parameter or registry lookup: `cypilot generate PRD` → PRD; `cypilot analyze {path}` → `artifacts.toml.systems[].artifacts[path].kind`; path in `codebase[]` → CODE | `ARTIFACT_TYPE` |
| **Load Rules.md** | Set `KITS_PATH = {KIT_BASE}/artifacts/{ARTIFACT_TYPE}/rules.md`; for CODE use `KITS_PATH = {KIT_BASE}/codebase/rules.md`; MUST read rules.md and parse Dependencies, Requirements, Tasks (for generate), Validation (for validate) | `KITS_PATH`, parsed rules sections |
| **Load Dependencies** | For each dependency from rules.md, resolve path relative to rules.md location, load file content, store for workflow use | `TEMPLATE`, `CHECKLIST`, `EXAMPLE` |
| **Confirm Requirements** | Agent confirms Structural, Semantic, Versioning, and Traceability requirements from rules | `REQUIREMENTS` |
| **Load Config Specs** | After rules loaded and target type determined, read `{cypilot_path}/.gen/AGENTS.md`; use the matching rules below to open applicable specs; if config uses legacy `WHEN executing workflows: ...`, map workflow names to artifact kinds internally | `CONFIG_SPECS` |

Match config specs in this order:
1. Match `{rule}` to the loaded rules ID (for example `cypilot-sdlc`)
2. Match target to the current artifact kind or `codebase` when working on code
3. Open every matching spec and store the resulting paths in `CONFIG_SPECS`

## Cross-Reference & Context Rules

Before proceeding, understand parent artifacts, child artifacts, related code implementing the target, and related artifacts implemented by code.

**MUST**:
- Use current project context for proposals
- Reference existing artifacts when relevant
- Show reasoning for proposals

**MUST NOT**:
- Make up information
- Assume without context
- Proceed without user confirmation (operations)

## Error Handling

| Error | User-facing response | Action |
|---|---|---|
| Cypilot Not Found | `⚠️ Cypilot not configured` → `Run cpt init to initialize` | STOP |
| `artifacts.toml` Parse Error | `⚠️ Cannot parse artifacts.toml: {parse error}` → `Fix TOML syntax errors in {cypilot_path}/config/artifacts.toml` → `Validate with: python3 -c 'import tomllib; tomllib.load(open("artifacts.toml", "rb"))'` | STOP |
| `rules.md` Not Found | `⚠️ Rules file not found: {KITS_PATH}` → verify kit exists at `{KIT_BASE}` → check `artifacts.toml` kits path → run `cpt init --force` to regenerate | STOP |
| Template/Checklist Not Found | `⚠️ Dependency not found: {dependency_path}` → referenced in `{KITS_PATH}` → expected at `{resolved_path}` → verify kit package is complete | STOP |
| System Not Registered | `⚠️ System not found: {system_name}` → show registered systems → options: `1. Register system via cpt init  2. Use existing system  3. Continue in RELAXED mode` | Prompt user to choose |
| Artifact Kind Not Supported | `⚠️ Unsupported artifact kind: {KIND}` → show available kinds in `{KIT_BASE}` → options: `1. Use supported kind  2. Create custom templates for {KIND}  3. Continue in RELAXED mode` | Prompt user to choose |

## Consolidated Validation Checklist

Use this single checklist for all execution-protocol validation.

| Group | Required checks |
|---|---|
| **Detection (D)** | D.1 Cypilot mode detected (agent states Cypilot enabled); D.2 Rules mode determined (STRICT/RELAXED + reason) |
| **Discovery (DI)** | DI.1 Cypilot discovery executed (`cpt info`); DI.2 `artifacts.toml` read/understood (agent lists systems/rules); DI.3 Rules directories explored (agent lists artifact kinds) |
| **Clarification (CL)** | CL.1 Target type clarified (artifact or code); CL.2 Artifact type determined (PRD, DESIGN, etc.); CL.3 System context clarified when using rules; CL.4 Rules context clarified when multiple rules |
| **Loading (L)** | L.1 `KITS_PATH` resolved (correct `rules.md`); L.2 Dependencies loaded (template/checklist/example); L.3 Requirements confirmed (agent enumerates requirements); L.4 Config specs loaded when WHEN clauses match |
| **Context (C)** | C.1 Cross-references understood (parent/child/related artifacts); C.2 Project context available (can reference project specifics) |
| **Final (F)** | F.1 D.1-D.2 pass; F.2 DI.1-DI.3 pass; F.3 CL.1-CL.4 pass (apply conditionals); F.4 L.1-L.4 pass (apply conditionals); F.5 C.1-C.2 pass; F.6 Ready for workflow-specific logic |
