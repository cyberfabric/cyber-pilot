---
name: spider
description: Spider provides two workflows: analyze and generate. Analyze for all read operations, generate for all write operations.
---

# Spider Unified Tool

## Goal

Spider provides: template-based validation, cross-reference validation, code traceability, ID search, and design-to-code implementation with `@spider-*` markers.

## Preconditions

- `python3` available
- Target paths exist and readable

---

## Protocol Guard

ALWAYS FIRST run `python3 {spider_path}/skills/spider/scripts/spider.py adapter-info` BEFORE any Spider workflow action

ALWAYS FIRST read `{spider_adapter_path}/AGENTS.md` WHEN adapter status is FOUND

ALWAYS FIRST parse and load ALL matched WHEN clause specs BEFORE proceeding with workflow

ALWAYS include Spider Context block WHEN editing code:
```
Spider Context:
- Adapter: {path}
- Target: {artifact|codebase}
- Specs loaded: {list paths or "none required"}
```

ALWAYS STOP and re-run Protocol Guard WHEN specs should be loaded but weren't listed

---

## Agent-Safe Invocation

ALWAYS use script entrypoint:
```bash
python3 {spider_path}/skills/spider/scripts/spider.py <subcommand> [options]
```

ALWAYS use `=` form for pattern args starting with `-`: `--pattern=-req-`

---

## Quick Commands (No Protocol)

ALWAYS SKIP Protocol Guard and workflow loading WHEN user invokes quick commands

ALWAYS run `python3 {spider_path}/skills/spider/scripts/spider.py init --yes` directly WHEN user invokes `spider init`

ALWAYS run `python3 {spider_path}/skills/spider/scripts/spider.py agents --agent <name>` directly WHEN user invokes `spider agents <name>`

---

## Workflow Routing

Spider has exactly **TWO** workflows. No exceptions.

ALWAYS open and follow `{spider_path}/workflows/generate.md` WHEN user intent is WRITE: create, edit, fix, update, implement, refactor, delete, add, setup, configure, build, code

ALWAYS open and follow `{spider_path}/workflows/analyze.md` WHEN user intent is READ: analyze, validate, review, analyze, check, inspect, audit, compare, list, show, find

ALWAYS ask user "analyze (read-only) or generate (modify)?" WHEN intent is UNCLEAR: help, look at, work with, handle and STOP WHEN user user cancel or exit 
---

## Spider Mode

ALWAYS set `{spider_mode}` = `on` FIRST WHEN user invokes `spider {prompt}`

ALWAYS run `adapter-info` WHEN enabling Spider mode

ALWAYS show status after enabling:
```
Spider Mode Enabled
Adapter: {FOUND at path | NOT_FOUND}
```

---

## Command Reference

### validate
```bash
python3 {spider_path}/skills/spider/scripts/spider.py validate [--artifact <path>] [--skip-code] [--verbose]
```
Validates artifacts/code with deterministic validation checks (structure, cross-refs, task statuses, traceability).

Legacy aliases: `validate-code` (same behavior), `validate-rules` (alias for `validate-weavers`).

### list-ids
```bash
python3 {spider_path}/skills/spider/scripts/spider.py list-ids [--artifact <path>] [--pattern <string>] [--kind <string>]
```

### get-content
```bash
python3 {spider_path}/skills/spider/scripts/spider.py get-content (--artifact <path> | --code <path>) --id <string>
```

### where-defined / where-used
```bash
python3 {spider_path}/skills/spider/scripts/spider.py where-defined --id <id>
python3 {spider_path}/skills/spider/scripts/spider.py where-used --id <id>
```

### adapter-info
```bash
python3 {spider_path}/skills/spider/scripts/spider.py adapter-info
```
Output: status, adapter_dir, project_name, specs, weavers

### init
```bash
python3 {spider_path}/skills/spider/scripts/spider.py init [--yes] [--dry-run]
```

### agents
```bash
python3 {spider_path}/skills/spider/scripts/spider.py agents --agent <name>
```
Supported: windsurf, cursor, claude, copilot, openai

Shortcut:
```bash
python3 {spider_path}/skills/spider/scripts/spider.py agents --openai
```

---

## Project Configuration

Optional `{project-root}/.spider-config.json`:
```json
{"spiderCorePath": ".spider", "spiderAdapterPath": ".spider-adapter"}
```

All commands output JSON. Exit codes: 0=PASS, 1=filesystem error, 2=FAIL.
