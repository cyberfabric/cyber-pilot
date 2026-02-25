---
name: cypilot
description: Artifacts (PRD/DESIGN/ADR/DECOMPOSITION/FEATURE) + checklists; deterministic validation & consistency analysis (structure, cross-refs, cross-artifact consistency, tasks, covered-by, ID/CDSL extraction from artifact text); code↔artifact traceability with `@cpt-*`; ID search/navigation (list-ids, where-defined/used, get-content); coding support via generate workflow; reverse-engineering guidance for brownfield codebases; prompt-engineering methodology for improving agent instructions; adapter + registry discovery (adapter-info, artifacts.toml, kits/rules); init/bootstrap; workflow router (analyze/generate); agent integrations (agents: workflow proxies + SKILL outputs for windsurf/cursor/claude/copilot/openai).
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

ALWAYS set **CONTEXT** to the file or section being executed WHEN emitting execution logs (e.g., `workflows/generate.md`, `DESIGN rules`, `execution-protocol`).

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

ALWAYS FIRST update `{cypilot_path}` WHEN the adapter is connected as a git submodule:

Determine submodule mode (works in any shell):
```bash
git -C {cypilot_path} rev-parse --abbrev-ref HEAD
```

If the command prints `HEAD`, the submodule is in **detached HEAD** (normal “pinned commit” submodule mode). Update it from the superproject:
```bash
git submodule update --init --recursive -- {cypilot_path}
```

If the command prints a branch name (e.g. `main`), the submodule is on a **branch** (you intentionally work on it like a normal repo). Update it by pulling inside the submodule:
```bash
git -C {cypilot_path} pull --ff-only
git -C {cypilot_path} submodule update --init --recursive
```

ALWAYS FIRST open and remember `{cypilot_path}/config/AGENTS.md`

ALWAYS open and follow `{cypilot_path}/config/SKILL.md` WHEN it exists

ALWAYS FIRST run `python3 {cypilot_path}/skills/cypilot/scripts/cypilot.py adapter-info` BEFORE any Cypilot workflow action

ALWAYS FIRST read `{cypilot_path}/config/AGENTS.md` WHEN adapter status is FOUND

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

## Cypilot Mode

ALWAYS set `{cypilot_mode}` = `on` FIRST WHEN user invokes `cypilot {prompt}`

ALWAYS run `adapter-info` WHEN enabling Cypilot mode

ALWAYS show status after enabling:
```
Cypilot Mode Enabled
Adapter: {FOUND at path | NOT_FOUND}
```
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

ALWAYS run `python3 {cypilot_path}/skills/scripts/pr.py list` directly WHEN user invokes `cypilot list PRs` or any PR listing intent — NEVER use `gh pr list`

---

## Workflow Routing

Cypilot has exactly **TWO** workflows. No exceptions.

ALWAYS open and follow `{cypilot_path}/.core/workflows/generate.md` WHEN user intent is WRITE: create, edit, fix, update, implement, refactor, delete, add, setup, configure, build, code

ALWAYS open and follow `{cypilot_path}/.core/workflows/analyze.md` WHEN user intent is READ: analyze, validate, review, analyze, check, inspect, audit, compare, list, show, find

ALWAYS ask user "analyze (read-only) or generate (modify)?" WHEN intent is UNCLEAR: help, look at, work with, handle and STOP WHEN user user cancel or exit

## PR Review & Status (Shortcut Routing)

ALWAYS re-fetch and re-analyze from scratch WHEN a PR review or status request is detected — even if the same PR was reviewed earlier in this conversation. Previous results are stale the moment a new request arrives. NEVER skip fetch or reuse earlier analysis.

ALWAYS run `python3 {cypilot_path}/skills/scripts/pr.py list` WHEN user intent matches PR list patterns:
- `list PRs`, `list open PRs`, `cypilot list PRs`
- `show PRs`, `show open PRs`, `what PRs are open`
- Any request to enumerate or browse open pull requests

AVOID use `gh pr list` directly — ALWAYS use `pr.py list` for listing PRs.

ALWAYS route to the `/cypilot-pr-review` workflow WHEN user intent matches PR review patterns:
- `review PR {number}`, `review PR #{number}`, `review PR https://...`
- `cypilot review PR {number}`, `PR review {number}`
- `code review PR {number}`, `check PR {number}`

ALWAYS route to the `/cypilot-pr-status` workflow WHEN user intent matches PR status patterns:
- `PR status {number}`, `cypilot PR status {number}`
- `status of PR {number}`, `check PR status {number}`

### PR List (Quick Command)

When routed to list PRs:
1. Run `python3 {cypilot_path}/skills/scripts/pr.py list`
2. Present the output to the user (respects `.prs/config.yaml` exclude list)
3. No Protocol Guard or workflow loading required — this is a quick command

### PR Review Workflow

When routed to PR review:
1. **ALWAYS fetch fresh data first** — run `pr.py fetch` even if data exists from a prior run
2. Read `{cypilot_path}/.core/workflows/pr-review.md` and follow its steps
3. Use `python3 {cypilot_path}/skills/scripts/pr.py` as the script
4. When target is `ALL` or no PR number given, run `pr.py list` first to show available PRs
5. Select prompt and checklist from `{cypilot_path}/config/pr-review.json` → `prompts`
6. Load prompt from `promptFile` and checklist from `checklist` in matched entry
7. Use templates from `.cypilot/templates/pr/`

### PR Status Workflow

When routed to PR status:
1. **ALWAYS fetch fresh data first** — `pr.py status` auto-fetches, but never assume prior data is current
2. Read `{cypilot_path}/.core/workflows/pr-status.md` and follow its steps
3. Use `python3 {cypilot_path}/skills/scripts/pr.py` as the script
4. When target is `ALL` or no PR number given, run `pr.py list` first to show available PRs

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
