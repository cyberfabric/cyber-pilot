---
name: cypilot
description: Cypilot provides two workflows: analyze and generate. Analyze for all read operations, generate for all write operations.
---

# Cypilot Unified Tool

## Goal

Cypilot provides: template-based validation, cross-reference validation, code traceability, ID search, and design-to-code implementation with `@cpt-*` markers.

## Preconditions

- `python3` available
- Target paths exist and readable

---

## Protocol Guard

ALWAYS FIRST run `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py adapter-info` BEFORE any Cypilot workflow action

ALWAYS FIRST read `{cypilot_adapter_path}/AGENTS.md` WHEN adapter status is FOUND

ALWAYS FIRST parse and load ALL matched WHEN clause specs BEFORE proceeding with workflow

ALWAYS include Cypilot Context block WHEN editing code:
```
Cypilot Context:
- Adapter: {path}
- Target: {artifact|codebase}
- Specs loaded: {list paths or "none required"}
```

ALWAYS STOP and re-run Protocol Guard WHEN specs should be loaded but weren't listed

---

## Agent-Safe Invocation

ALWAYS use script entrypoint:
```bash
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py <subcommand> [options]
```

ALWAYS use `=` form for pattern args starting with `-`: `--pattern=-req-`

---

## Quick Commands (No Protocol)

ALWAYS SKIP Protocol Guard and workflow loading WHEN user invokes quick commands

ALWAYS run `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py init --yes` directly WHEN user invokes `cypilot init`

ALWAYS run `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py agents --agent <name>` directly WHEN user invokes `cypilot agents <name>`

---

## Workflow Routing

Cypilot has exactly **TWO** workflows. No exceptions.

ALWAYS open and follow `{cypilot_path}/workflows/generate.md` WHEN user intent is WRITE: create, edit, fix, update, implement, refactor, delete, add, setup, configure, build, code

ALWAYS open and follow `{cypilot_path}/workflows/analyze.md` WHEN user intent is READ: analyze, validate, review, analyze, check, inspect, audit, compare, list, show, find

ALWAYS ask user "analyze (read-only) or generate (modify)?" WHEN intent is UNCLEAR: help, look at, work with, handle and STOP WHEN user user cancel or exit 
---

## Cypilot Mode

ALWAYS set `{cypilot_mode}` = `on` FIRST WHEN user invokes `cypilot {prompt}`

ALWAYS run `adapter-info` WHEN enabling Cypilot mode

ALWAYS show status after enabling:
```
Cypilot Mode Enabled
Adapter: {FOUND at path | NOT_FOUND}
```

---

## Command Reference

### validate
```bash
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py validate [--artifact <path>] [--skip-code] [--verbose]
```
Validates artifacts/code with deterministic validation checks (structure, cross-refs, task statuses, traceability).

Legacy aliases: `validate-code` (same behavior), `validate-rules` (alias for `validate-kits`).

### list-ids
```bash
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py list-ids [--artifact <path>] [--pattern <string>] [--kind <string>]
```

### get-content
```bash
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py get-content (--artifact <path> | --code <path>) --id <string>
```

### where-defined / where-used
```bash
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py where-defined --id <id>
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py where-used --id <id>
```

### adapter-info
```bash
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py adapter-info
```
Output: status, adapter_dir, project_name, specs, kits

### init
```bash
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py init [--yes] [--dry-run]
```

### agents
```bash
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py agents --agent <name>
```
Supported: windsurf, cursor, claude, copilot, openai

Shortcut:
```bash
python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py agents --openai
```

---

## Project Configuration

Optional `{project-root}/.cypilot-config.json`:
```json
{"cypilotCorePath": ".cypilot", "cypilotAdapterPath": ".cypilot-adapter"}
```

All commands output JSON. Exit codes: 0=PASS, 1=filesystem error, 2=FAIL.
