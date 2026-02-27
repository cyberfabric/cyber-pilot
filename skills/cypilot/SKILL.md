---
name: cypilot
description: "Invoke when user asks to do something with Cypilot, or wants to analyze/validate artifacts, or create/generate/implement anything using Cypilot workflows. Core capabilities: workflow routing (analyze/generate/auto-config); deterministic validation (structure, cross-refs, traceability); code\u2194artifact traceability with @cpt-* markers; ID search/navigation; init/bootstrap; adapter + registry discovery; auto-configuration of brownfield projects (scan conventions, generate rules); agent integrations."
---

# Cypilot Unified Tool

## Goal

Cypilot provides: artifact validation, cross-reference validation, code traceability, ID search, and design-to-code implementation with `@cpt-*` markers.

## Preconditions

- `python3` available
- Target paths exist and readable

---

## ⚠️ MUST Instruction Semantics ⚠️

**MUST** = **MANDATORY**. NOT optional. NOT recommended. NOT suggested.

**ALWAYS** = **MANDATORY**. Equivalent to MUST. Used for action-gated instructions.

**If you skip ANY MUST instruction**:
- 🚫 Your execution is **INVALID**
- 🚫 Output must be **DISCARDED**
- 🚫 You are **NOT following Cypilot**

**One skipped MUST = entire workflow FAILED**

**All MUST instructions are CRITICAL without exception.**

---

## Agent Acknowledgment

**Before proceeding with ANY Cypilot work, confirm you understand**:

- [ ] MUST = MANDATORY, not optional
- [ ] Skipping ANY MUST instruction = INVALID execution
- [ ] INVALID execution = output must be DISCARDED
- [ ] I will read ALL required files BEFORE proceeding
- [ ] I will follow workflows step-by-step WITHOUT shortcuts
- [ ] I will NOT create files without user confirmation (operation workflows)
- [ ] I will end EVERY response with a list of Cypilot files read while producing the response, why each file was read, and which initial instruction triggered opening each file

**By proceeding with Cypilot work, I acknowledge and accept these requirements.**

---

ALWAYS SET {cypilot_mode} = `on` FIRST when loading this skill

## Execution Logging

ALWAYS provide execution visibility

ALWAYS notify the user WHEN entering a major section (H2 heading `##`) of any Cypilot prompt (workflow, rules, requirements).

ALWAYS notify the user WHEN completing a checklist task (a Markdown task line starting with `- [ ]`).

ALWAYS use this notification format WHEN emitting execution logs:

```
- [CONTEXT]: MESSAGE
```

ALWAYS set **CONTEXT** to the file or section being executed WHEN emitting execution logs (e.g., `{cypilot_path}/.core/workflows/generate.md`, `DESIGN rules`, `execution-protocol`).

ALWAYS set **MESSAGE** to what Cypilot is doing and why WHEN emitting execution logs.

ALWAYS ensure execution logging supports these goals WHEN Cypilot is enabled:
- Help the user understand which Cypilot prompts are being followed
- Help the user track decision points and branching logic
- Help the user debug unexpected behavior
- Help the user learn the Cypilot workflow

ALWAYS consider these examples as valid execution logs WHEN Cypilot is enabled:

```
- [execution-protocol]: Entering "Load Rules" — target is CODE, loading codebase/rules.md
- [DESIGN rules]: Completing "Validate structure" — all required sections present
- [workflows/generate.md]: Entering "Determine Target" — user requested code implementation
```

---

## Variables

**While Cypilot is enabled**, remember these variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `{cypilot_path}` | Directory containing this `../../SKILL.md`| Project root for Cypilot navigation |
| `{cypilot_mode}` | `on` or `off` | Current Cypilot mode state |

**Setting `{cypilot_mode}`**:
- Explicit command: `cypilot on` / `cypilot off`
- Cypilot prompts that activate/deactivate Cypilot workflows

Use `{cypilot_path}` as the base path for all relative Cypilot file references.

## Protocol Guard

ALWAYS FIRST open and remember `{cypilot_path}/.gen/AGENTS.md`

ALWAYS open and follow `{cypilot_path}/config/AGENTS.md` WHEN it exists

ALWAYS open and follow `{cypilot_path}/.gen/SKILL.md` WHEN it exists

ALWAYS open and follow `{cypilot_path}/config/SKILL.md` WHEN it exists

ALWAYS FIRST run `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py info` BEFORE any Cypilot workflow action

ALWAYS FIRST read `{cypilot_path}/.gen/AGENTS.md` WHEN cypilot status is FOUND

ALWAYS FIRST parse and load ALL matched WHEN clause specs BEFORE proceeding with workflow

ALWAYS include Cypilot Context block WHEN editing code:
```
Cypilot Context:
- Cypilot: {path}
- Target: {artifact|codebase}
- Specs loaded: {list paths or "none required"}
```

ALWAYS STOP and re-run Protocol Guard WHEN specs should be loaded but weren't listed

---

## Cypilot Mode

ALWAYS set `{cypilot_mode}` = `on` FIRST WHEN user invokes `cypilot {prompt}`

ALWAYS run `info` WHEN enabling Cypilot mode

ALWAYS show status after enabling:
```
Cypilot Mode Enabled
Cypilot: {FOUND at path | NOT_FOUND}
```
---

## Agent-Safe Invocation

ALWAYS use script entrypoint:
```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py <subcommand> [options]
```

ALWAYS use `=` form for pattern args starting with `-`: `--pattern=-req-`

---

## Quick Commands (No Protocol)

ALWAYS SKIP Protocol Guard and workflow loading WHEN user invokes quick commands

ALWAYS run `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py init --yes` directly WHEN user invokes `cypilot init`

ALWAYS run `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py agents --agent <name>` directly WHEN user invokes `cypilot agents <name>`

ALWAYS open and follow `{cypilot_path}/.core/workflows/generate.md` directly WHEN user invokes `cypilot auto-config` or `cypilot configure` — generate.md will trigger the auto-config methodology

---

## Workflow Routing

Cypilot has exactly **TWO** workflows. No exceptions.

ALWAYS open and follow `{cypilot_path}/.core/workflows/generate.md` WHEN user intent is WRITE: create, edit, fix, update, implement, refactor, delete, add, setup, configure, build, code

ALWAYS open and follow `{cypilot_path}/.core/workflows/analyze.md` WHEN user intent is READ: analyze, validate, review, analyze, check, inspect, audit, compare, list, show, find

ALWAYS ask user "analyze (read-only) or generate (modify)?" WHEN intent is UNCLEAR: help, look at, work with, handle and STOP WHEN user cancel or exit

> **Note**: `generate.md` auto-triggers the auto-config methodology (`requirements/auto-config.md`) when it detects a brownfield project with no project-specific rules. "configure" intent routes through generate.md.

## Command Reference

### validate
```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py validate [--artifact <path>] [--skip-code] [--verbose]
```
Validates artifacts/code with deterministic validation checks (structure, cross-refs, task statuses, traceability).

Legacy aliases: `validate-code` (same behavior), `validate-rules` (alias for `validate-kits`).

### list-ids
```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py list-ids [--artifact <path>] [--pattern <string>] [--kind <string>]
```

### get-content
```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py get-content (--artifact <path> | --code <path>) --id <string>
```

### where-defined / where-used
```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py where-defined --id <id>
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py where-used --id <id>
```

### info
```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py info
```
Output: status, cypilot_dir, project_name, specs, kits

### init
```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py init [--yes] [--dry-run]
```

### agents
```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py agents --agent <name>
```
Supported: windsurf, cursor, claude, copilot, openai

Shortcut:
```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py agents --openai
```

---

## Auto-Configuration

Cypilot can scan a brownfield project and generate project-specific rules automatically.

**What it does**:
- Scans project structure, entry points, conventions, patterns
- Generates per-system rule files → `{cypilot_path}/config/rules/{slug}.md`
- Adds WHEN rules to `{cypilot_path}/config/AGENTS.md`
- Registers detected systems in `{cypilot_path}/config/artifacts.toml`

**When to use**:
- After `cypilot init` on an existing (brownfield) project
- When Cypilot doesn't know your project conventions yet
- When you want to reconfigure after major project changes

**How to invoke**:
- `cypilot auto-config` — run auto-config workflow
- `cypilot configure` — alias
- Automatic — `generate.md` offers auto-config when brownfield + no rules detected

---

## Project Configuration

Optional `{project-root}/.cypilot-config.json`:
```json
{"cypilotPath": "cypilot"}
```

All commands output JSON. Exit codes: 0=PASS, 1=filesystem error, 2=FAIL.
