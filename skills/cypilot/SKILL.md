---
name: cypilot
description: "Invoke when user asks to do something with Cypilot, or wants to analyze/validate artifacts, or create/generate/implement anything using Cypilot workflows, or plan phased execution. Core capabilities: workflow routing (plan/analyze/generate/auto-config); deterministic validation (structure, cross-refs, traceability, TOC); code↔artifact traceability with @cpt-* markers; spec coverage measurement; ID search/navigation; init/bootstrap; adapter + registry discovery; auto-configuration of brownfield projects (scan conventions, generate rules); kit management (install/update with file-level diff); TOC generation; agent integrations (Windsurf, Cursor, Claude, Copilot, OpenAI)."
---

# Cypilot Unified Tool


<!-- toc -->

- [Goal](#goal)
- [Preconditions](#preconditions)
- [⚠️ MUST Instruction Semantics ⚠️](#must-instruction-semantics)
- [Agent Acknowledgment](#agent-acknowledgment)
- [Execution Logging](#execution-logging)
- [Variables](#variables)
  - [Template Variable Resolution](#template-variable-resolution)
- [CLI Resolution](#cli-resolution)
- [Protocol Guard](#protocol-guard)
- [Cypilot Mode](#cypilot-mode)
- [Agent-Safe Invocation](#agent-safe-invocation)
- [Quick Commands](#quick-commands)
  - [Direct CLI Commands (No Workflow Routing)](#direct-cli-commands-no-workflow-routing)
  - [Workflow Shortcuts](#workflow-shortcuts)
- [Workflow Routing](#workflow-routing)
- [Command Reference](#command-reference)
- [Auto-Configuration](#auto-configuration)
- [Project Configuration](#project-configuration)

<!-- /toc -->

## Goal

Cypilot provides artifact validation, cross-reference validation, code traceability, spec coverage measurement, ID search/navigation, kit management, TOC generation/validation, multi-agent integration, and design-to-code implementation with `@cpt-*` markers.

## Preconditions

- `cpt` available (preferred) or `python3` as fallback
- Target paths exist and are readable

---

## ⚠️ MUST Instruction Semantics ⚠️

**MUST** and **ALWAYS** are mandatory. Skipping any MUST instruction invalidates execution, the output must be discarded, and the workflow fails.

## Agent Acknowledgment

- [ ] MUST/ALWAYS are mandatory; skipping any MUST invalidates execution.
- [ ] I will read all required files before proceeding.
- [ ] I will follow workflows step-by-step without shortcuts.
- [ ] I will not create or modify files, or execute any other write-capable Cypilot command, without explicit user confirmation, and I will not add auto-approval flags unless the user explicitly asks for them.
- [ ] I will list Cypilot files read, why, and the triggering instruction before any approval prompt.

By proceeding with Cypilot work, I acknowledge and accept these requirements.

ALWAYS SET {cypilot_mode} = `on` FIRST when loading this skill

## Execution Logging

ALWAYS provide execution visibility:
- Notify the user when entering any H2 section of a Cypilot prompt.
- Notify the user when completing any `- [ ]` checklist task.
- Use `- [CONTEXT]: MESSAGE`; set context to the file/section and message to the action + why.
- Logging must help the user understand loaded prompts, routing decisions, debugging state, and workflow progress.

Example:
```text
- [execution-protocol]: Entering "Load Rules" — target is CODE, loading codebase/rules.md
- [DESIGN rules]: Completing "Validate structure" — all required sections present
- [workflows/generate.md]: Entering "Determine Target" — user requested code implementation
```

## Variables

| Variable | Value | Use |
|---|---|---|
| `{cypilot_path}` | Directory path resolved from root `AGENTS.md` | Base path for all Cypilot-relative references |
| `{cypilot_mode}` | `on` or `off` | Current Cypilot mode state |
| `{cpt_cmd}` | `cpt` or `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py` | Resolved CLI entrypoint |
| `{cpt_installed}` | `true` or `false` | Whether the `cpt` CLI is available |

Setting `{cypilot_mode}`: explicit `cypilot on/off` or a prompt that activates/deactivates Cypilot workflows.

### Template Variable Resolution

- Resolve variables from `{cpt_cmd} --json info` first; parse the returned `variables` dict.
- Use `{cpt_cmd} --json resolve-vars` only when a fresh or filtered map is needed.
- Variable sources: system (`cypilot_path`, `project_root`) + installed kit resources.
- ALWAYS resolve `{variable}` references to absolute paths before using kit markdown files.

## CLI Resolution

Run before Protocol Guard when `{cypilot_mode}` is `on`:
1. `command -v cpt` → `{cpt_cmd} = cpt`, `{cpt_installed} = true`
2. Otherwise `{cpt_cmd} = python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py`, `{cpt_installed} = false`
3. If `cpt` is missing and `~/.cypilot/cache/cpt-prompt-dismissed` does not exist, offer `pipx install git+https://github.com/cyberfabric/cyber-pilot.git`; on dismiss create the marker file
4. Re-offer installation if the user later asks about the long invocation path

ALWAYS use `{cpt_cmd}` for all later CLI invocations.

## Protocol Guard

- ALWAYS FIRST run `{cpt_cmd} --json info` before any Cypilot workflow action
- ALWAYS store the `variables` dict from `info` output and use it to resolve `{variable}` references in AGENTS/SKILL/rules/workflows
- ALWAYS follow this load order: `info` → registry/intent/target/rules resolution from `execution-protocol.md` → matched WHEN-clause specs
- ALWAYS open and remember `{cypilot_path}/.gen/AGENTS.md` after `info` succeeds; use it for navigation and WHEN-clause matching
- ALWAYS open and follow `{cypilot_path}/config/AGENTS.md` when it exists and the current route or matched WHEN clause requires it
- ALWAYS open and follow `{cypilot_path}/.gen/SKILL.md` when it exists and the current route or matched WHEN clause requires it
- ALWAYS open and follow `{cypilot_path}/config/SKILL.md` when it exists and the current route or matched WHEN clause requires it
- ALWAYS load matched WHEN-clause specs only after registry understanding, target determination, and `rules.md` resolution provide enough context to match safely
- MUST NOT preload every AGENTS/SKILL/spec file up front; load only the smallest set needed for the current request
- Before opening a large AGENTS/SKILL/spec file, estimate size and prefer chunked reads of matched sections over full-file reads
- If safe WHEN-clause matching is not yet possible, stop after registry/target/rules resolution and continue only when enough context exists to load specs boundedly
- If required Protocol Guard context would exceed the current turn budget, checkpoint or escalate instead of proceeding with partial or unbounded spec loading
- ALWAYS include this block when editing code:
```text
Cypilot Context:
- Cypilot: {path}
- Target: {artifact|codebase}
- Specs loaded: {list paths or "none required"}
```
- ALWAYS stop and re-run Protocol Guard when required specs should have been loaded but were not

## Cypilot Mode

- ALWAYS set `{cypilot_mode} = on` first when user invokes `cypilot {prompt}`
- ALWAYS run `info` when enabling Cypilot mode
- ALWAYS show:
```text
Cypilot Mode Enabled
Cypilot: {FOUND at path | NOT_FOUND}
```

## Agent-Safe Invocation

- ALWAYS use `{cpt_cmd} --json <subcommand> [options]`
- ALWAYS pass `--json` immediately after `{cpt_cmd}` and before the subcommand for agent-driven CLI calls
- ALWAYS use `=` form for pattern args starting with `-` (example: `--pattern=-req-`)
- MUST obtain explicit user confirmation before executing any write-capable command, including direct CLI commands that do not route through a workflow
- MUST NOT add auto-approval flags such as `--yes`, `-y`, or `--force` to write-capable commands unless the user explicitly requested that non-interactive behavior

## Quick Commands

### Direct CLI Commands (No Workflow Routing)

No workflow routing skips workflow selection only. It does not waive confirmation: obtain explicit user confirmation before executing any write-capable direct CLI command below.

| User invocation | Direct action |
|---|---|
| `cypilot init` | After explicit user confirmation, run `{cpt_cmd} --json init` |
| `cypilot agents <name>` | Run `{cpt_cmd} --json agents --agent <name>` |
| `cypilot generate-agents <name>` | After explicit user confirmation, run `{cpt_cmd} --json generate-agents --agent <name>` |
| `cypilot workspace init` | After explicit user confirmation, run `{cpt_cmd} --json workspace-init [--root <dir>] [--output <path>] [--inline] [--force] [--max-depth <N>] [--dry-run]` |
| `cypilot workspace add` | After explicit user confirmation, run `{cpt_cmd} --json workspace-add --name <name> (--path <path> \| --url <url>) [--branch <branch>] [--role <role>] [--adapter <path>] [--inline] [--force]` |
| `cypilot workspace info` | Run `{cpt_cmd} --json workspace-info` |
| `cypilot workspace sync` | After explicit user confirmation, run `{cpt_cmd} --json workspace-sync [--source <name>] [--dry-run] [--force]`; `--force` is destructive |

### Workflow Shortcuts

| User invocation | Action |
|---|---|
| `cypilot auto-config` / `cypilot configure` | Open and follow `{cypilot_path}/.core/workflows/generate.md` |

## Workflow Routing

Cypilot has exactly three core workflows plus specialized sub-workflows. Routing priority is `plan` > `generate`/`analyze`.

| Intent | Match | Action |
|---|---|---|
| Plan | `plan`, `create a plan`, `execution plan`, `break down`, `decompose`, or `plan to ...` | Open and follow `{cypilot_path}/.core/workflows/plan.md` first |
| Generate | `create`, `edit`, `fix`, `update`, `implement`, `refactor`, `delete`, `add`, `setup`, `configure`, `build`, `code` and user did not say `plan` | Open and follow `{cypilot_path}/.core/workflows/generate.md` |
| Analyze | `analyze`, `validate`, `review`, `check`, `inspect`, `audit`, `compare`, `list`, `show`, `find` and user did not say `plan` | Open and follow `{cypilot_path}/.core/workflows/analyze.md` |
| Workspace | `workspace`, `multi-repo`, `add source`, `add repo`, `cross-reference`, `cross-repo` | Open and follow `{cypilot_path}/.core/workflows/workspace.md` |
| Unclear | `help`, `look at`, `work with`, `handle` | Ask `plan (phased execution) / generate (modify) / analyze (read-only)?` and stop if the user cancels |

`configure` and `auto-config` are workflow shortcuts, not direct no-protocol commands; both route through `generate.md`, which may auto-trigger `requirements/auto-config.md` for brownfield projects with no project-specific rules.

## Command Reference

Entrypoint: `{cpt_cmd} <command> [options]`
Machine output: add `--json` immediately after `{cpt_cmd}` and before the subcommand. Exit codes: `0 = PASS`, `1 = filesystem/config error`, `2 = FAIL`.
Legacy aliases: `validate-code` = `validate`; `validate-rules` = `validate-kits`.

| Category | Commands |
|---|---|
| Validation | `{cpt_cmd} --json validate` (artifacts + code), `{cpt_cmd} --json validate-kits` (kit config), `{cpt_cmd} --json validate-toc` (TOC integrity), `{cpt_cmd} --json self-check` (template/example sync), `{cpt_cmd} --json spec-coverage` (marker coverage) |
| Search | `{cpt_cmd} --json list-ids` (enumerate IDs), `{cpt_cmd} --json list-id-kinds` (kind counts), `{cpt_cmd} --json get-content` (fetch by ID), `{cpt_cmd} --json where-defined` (definition), `{cpt_cmd} --json where-used` (references) |
| Kit management | `{cpt_cmd} --json kit install` (install kit), `{cpt_cmd} --json kit update` (file-level kit update) |
| Utilities | `{cpt_cmd} --json toc` (generate TOC), `{cpt_cmd} --json info` (discover config), `{cpt_cmd} --json resolve-vars` (expand template vars), `{cpt_cmd} --json init` (bootstrap project), `{cpt_cmd} --json update` (refresh adapter), `{cpt_cmd} --json agents` (show generated integrations), `{cpt_cmd} --json generate-agents` (generate/update integrations) |
| Migration | `{cpt_cmd} --json migrate` (v2→v3 project), `{cpt_cmd} --json migrate-config` (JSON→TOML config) |
| Workspace | `{cpt_cmd} --json workspace-init` (create workspace), `{cpt_cmd} --json workspace-add` (add source), `{cpt_cmd} --json workspace-info` (status), `{cpt_cmd} --json workspace-sync` (update Git sources) |

See `skills/cypilot/cypilot.clispec` for full syntax, arguments, options, exit semantics, and examples.

## Auto-Configuration

Use auto-config after `cypilot init` on a brownfield project, when project conventions are unknown, or after major structural changes. It scans structure/conventions, generates `{cypilot_path}/config/rules/{slug}.md`, adds WHEN rules to `{cypilot_path}/config/AGENTS.md`, and registers systems in `{cypilot_path}/config/artifacts.toml`. Invoke via `cypilot auto-config`, `cypilot configure`, or the automatic offer inside `generate.md`.

## Project Configuration

Project configuration lives in `{cypilot_path}/config/core.toml` (systems, kits, ignore lists). Artifact registry lives in `{cypilot_path}/config/artifacts.toml` (artifact paths, kinds, system mappings, codebase paths, autodetect rules). All commands output JSON when invoked with `--json`. Exit codes: 0=PASS, 1=filesystem error, 2=FAIL.
