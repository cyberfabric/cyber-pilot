---
name: cypilot
description: "Invoke when user asks to do something with Cypilot, or wants to analyze/validate artifacts, or create/generate/implement anything using Cypilot workflows, or plan phased execution. Core capabilities: workflow routing (plan/analyze/generate/auto-config); deterministic validation (structure, cross-refs, traceability, TOC); code↔artifact traceability with @cpt-* markers; spec coverage measurement; ID search/navigation; init/bootstrap; adapter + registry discovery; auto-configuration of brownfield projects (scan conventions, generate rules); kit management (install/update with file-level diff); TOC generation; agent integrations (Windsurf, Cursor, Claude, Copilot, OpenAI)."
---

# Cypilot Unified Tool


<!-- toc -->

- [Cypilot Unified Tool](#cypilot-unified-tool)
  - [Goal](#goal)
  - [Preconditions](#preconditions)
  - [⚠️ MUST Instruction Semantics ⚠️](#️-must-instruction-semantics-️)
  - [Agent Acknowledgment](#agent-acknowledgment)
  - [Execution Logging](#execution-logging)
  - [Variables](#variables)
    - [Template Variable Resolution](#template-variable-resolution)
  - [CLI Resolution](#cli-resolution)
  - [Protocol Guard](#protocol-guard)
  - [Cypilot Mode](#cypilot-mode)
  - [Agent-Safe Invocation](#agent-safe-invocation)
  - [Quick Commands (No Protocol)](#quick-commands-no-protocol)
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
- [ ] I will not create files without user confirmation in operation workflows.
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

- ALWAYS FIRST open and remember `{cypilot_path}/.gen/AGENTS.md`
- ALWAYS open and follow `{cypilot_path}/config/AGENTS.md` when it exists
- ALWAYS open and follow `{cypilot_path}/.gen/SKILL.md` when it exists
- ALWAYS open and follow `{cypilot_path}/config/SKILL.md` when it exists
- ALWAYS FIRST run `{cpt_cmd} --json info` before any Cypilot workflow action
- ALWAYS store the `variables` dict from `info` output and use it to resolve `{variable}` references in AGENTS/SKILL/rules/workflows
- ALWAYS FIRST parse and load all matched WHEN-clause specs before proceeding
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
- ALWAYS pass `--json` as the first argument for agent-driven CLI calls
- ALWAYS use `=` form for pattern args starting with `-` (example: `--pattern=-req-`)

## Quick Commands (No Protocol)

| User invocation | Direct action |
|---|---|
| `cypilot init` | Run `{cpt_cmd} --json init --yes` |
| `cypilot agents <name>` | Run `{cpt_cmd} --json agents --agent <name>` |
| `cypilot generate-agents <name>` | Run `{cpt_cmd} --json generate-agents --agent <name>` |
| `cypilot auto-config` / `cypilot configure` | Open and follow `{cypilot_path}/.core/workflows/generate.md` |
| `cypilot workspace init` | Run `{cpt_cmd} --json workspace-init [--root <dir>] [--output <path>] [--inline] [--force] [--max-depth <N>] [--dry-run]` |
| `cypilot workspace add` | Run `{cpt_cmd} --json workspace-add --name <name> (--path <path> \| --url <url>) [--branch <branch>] [--role <role>] [--adapter <path>] [--inline] [--force]` |
| `cypilot workspace info` | Run `{cpt_cmd} --json workspace-info` |
| `cypilot workspace sync` | Run `{cpt_cmd} --json workspace-sync [--source <name>] [--dry-run] [--force]`; `--force` is destructive |

## Workflow Routing

Cypilot has exactly three core workflows plus specialized sub-workflows. Routing priority is `plan` > `generate`/`analyze`.

| Intent | Match | Action |
|---|---|---|
| Plan | `plan`, `create a plan`, `execution plan`, `break down`, `decompose`, or `plan to ...` | Open and follow `{cypilot_path}/.core/workflows/plan.md` first |
| Generate | `create`, `edit`, `fix`, `update`, `implement`, `refactor`, `delete`, `add`, `setup`, `configure`, `build`, `code` and user did not say `plan` | Open and follow `{cypilot_path}/.core/workflows/generate.md` |
| Analyze | `analyze`, `validate`, `review`, `check`, `inspect`, `audit`, `compare`, `list`, `show`, `find` and user did not say `plan` | Open and follow `{cypilot_path}/.core/workflows/analyze.md` |
| Workspace | `workspace`, `multi-repo`, `add source`, `add repo`, `cross-reference`, `cross-repo` | Open and follow `{cypilot_path}/.core/workflows/workspace.md` |
| Unclear | `help`, `look at`, `work with`, `handle` | Ask `plan (phased execution) / generate (modify) / analyze (read-only)?` and stop if the user cancels |

`configure` routes through `generate.md`; that workflow may auto-trigger `requirements/auto-config.md` for brownfield projects with no project-specific rules.

## Command Reference

Entrypoint: `{cpt_cmd} <command> [options]`
Machine output: add `--json` as the first argument. Exit codes: `0 = PASS`, `1 = filesystem/config error`, `2 = FAIL`.
Legacy aliases: `validate-code` = `validate`; `validate-rules` = `validate-kits`.

| Category | Commands |
|---|---|
| Validation | `validate` (artifacts + code), `validate-kits` (kit config), `validate-toc` (TOC integrity), `self-check` (template/example sync), `spec-coverage` (marker coverage) |
| Search | `list-ids` (enumerate IDs), `list-id-kinds` (kind counts), `get-content` (fetch by ID), `where-defined` (definition), `where-used` (references) |
| Kit management | `kit install` (install kit), `kit update` (file-level kit update) |
| Utilities | `toc` (generate TOC), `info` (discover config), `resolve-vars` (expand template vars), `init` (bootstrap project), `update` (refresh adapter), `agents` (show generated integrations), `generate-agents` (generate/update integrations) |
| Migration | `migrate` (v2→v3 project), `migrate-config` (JSON→TOML config) |
| Workspace | `workspace-init` (create workspace), `workspace-add` (add source), `workspace-info` (status), `workspace-sync` (update Git sources) |

### Validation Commands

#### validate
```bash
validate [--artifact <path>] [--skip-code] [--verbose] [--output <path>] [--local-only] [--source <name>]
```
Validates artifacts and code with deterministic checks (structure, cross-refs, task statuses, traceability markers — pairing, coverage, orphans). Use `--local-only` to skip cross-repo workspace validation. Use `--source <name>` to validate a specific workspace source. Note: `--local-only` and `--source` are independent and can be combined — `--source` narrows which artifacts are validated, `--local-only` controls whether cross-repo IDs are included as reference context.

Legacy aliases: `validate-code` (same behavior), `validate-rules` (alias for `validate-kits`).

#### validate-kits
```bash
validate-kits [--kit <id>] [--template <path>] [--verbose]
```
Validates kit configuration — template frontmatter, constraints, resource paths.

#### validate-toc
```bash
validate-toc <files...> [--max-level <N>] [--verbose]
```
Validates Table of Contents in Markdown files — TOC exists, anchors point to real headings, all headings covered, not stale.

#### self-check
```bash
self-check [--kit <id>] [--verbose]
```
Validates example artifacts against their templates (template QA). Ensures templates and examples remain synchronized.

#### spec-coverage
```bash
spec-coverage [--system <slug>] [--min-coverage <N>] [--min-file-coverage <N>] [--min-granularity <N>] [--verbose] [--output <path>]
```
Measures CDSL marker coverage in codebase files. Reports coverage percentage, granularity score, per-file details, and uncovered line ranges. Use `--system` to limit to specific system slug(s). Use `--min-file-coverage` to enforce per-file minimum.

### Search Commands

#### list-ids
```bash
list-ids [--artifact <path>] [--pattern <string>] [--regex] [--kind <string>] [--all] [--include-code] [--source <name>]
```
Lists all Cypilot IDs from registered artifacts. Supports filtering by pattern, kind, and optional code scanning. Use `--source <name>` to list IDs from a specific workspace source.

#### list-id-kinds
```bash
list-id-kinds [--artifact <path>]
```
Lists ID kinds that exist in artifacts with counts and template mappings.

#### get-content
```bash
get-content (--artifact <path> | --code <path>) --id <string> [--inst <string>]
```
Retrieves content block for a specific Cypilot ID from artifacts or code files.

#### where-defined
```bash
where-defined --id <id> [--artifact <path>]
```
Finds where a Cypilot ID is defined.

#### where-used
```bash
where-used --id <id> [--artifact <path>] [--include-definitions]
```
Finds all references to a Cypilot ID.

### Kit Management Commands

#### kit install
```bash
kit install <source-path> [--dry-run] [--yes]
```
Installs a kit from a source directory. Copies kit files to `config/kits/{slug}/`.

#### kit update
```bash
kit update [--kit <slug>] [--dry-run] [--yes] [--auto-approve]
```
Updates kit files in `config/kits/{slug}/` with file-level diff. Interactive prompts for modified files: accept/decline/accept-all/decline-all.

### Utility Commands

#### toc
```bash
toc <files...> [--max-level <N>] [--indent <N>] [--dry-run] [--skip-validate]
```
Generates or updates Table of Contents in Markdown files between `<!-- toc -->` markers.

#### info
```bash
info [--root <path>] [--cypilot-root <path>]
```
Discovers Cypilot configuration and shows project status (cypilot_dir, project_name, specs, kits). Includes a `variables` dict mapping all template variables to absolute paths.

#### resolve-vars
```bash
resolve-vars [--root <path>] [--kit <slug>] [--flat]
```
Resolves all template variables (`{adr_template}`, `{scripts}`, etc.) to absolute file paths. Sources: system variables (`cypilot_path`, `project_root`) + kit resource bindings from `core.toml`. Use `--kit` to filter to a single kit. Use `--flat` for a plain variable→path dict.

#### init
```bash
init [--project-root <path>] [--cypilot-root <path>] [--project-name <string>] [--yes] [--dry-run] [--force]
```
Initializes Cypilot config directory (`.core/`, `.gen/`, `config/`) and root `AGENTS.md`.

#### update
```bash
update [--source <path>] [--force] [--dry-run]
```
Updates `.core/` from cache, updates kit files in `config/kits/` with file-level diff, regenerates `.gen/` aggregates, ensures `config/` scaffold.

#### agents
```bash
agents [--agent <name>] [--root <path>] [--cypilot-root <path>]
```
Shows generated agent integration status. Read-only dry-run — reports which integration files currently exist or would be created/updated for each supported agent without writing anything.
Supported: windsurf, cursor, claude, copilot, openai.

#### generate-agents
```bash
generate-agents [--agent <name>] [--root <path>] [--cypilot-root <path>] [--dry-run] [--yes] [--show-layers] [--discover]
```
Generates agent-specific workflow proxies and skill entry points.
Supported: windsurf, cursor, claude, copilot, openai.

Generates workflow commands, skill outputs, and **subagents** (isolated agent definitions with scoped tools and dedicated prompts). Two subagents are created for tools that support them: `cypilot-codegen` (full write access, worktree isolation) and `cypilot-pr-review` (read-only). Windsurf does not support subagents and is gracefully skipped.

Use `--show-layers` to display layer provenance report instead of generating. Use `--discover` to scan conventional dirs and populate `manifest.toml` before generating.

Shortcut: `generate-agents --openai`

### Migration Commands

#### migrate
```bash
migrate [--project-root <path>] [--cypilot-root <path>] [--dry-run] [--yes]
```
Migrates Cypilot v2 projects to v3 (adapter-based → blueprint-based, artifacts.json → artifacts.toml, three-directory layout).

#### migrate-config
```bash
migrate-config [--project-root <path>] [--dry-run]
```
Converts legacy JSON config files to TOML format.

### Workspace Commands

Workspaces are either **standalone** (`.cypilot-workspace.toml` at project root) or **inline** (`[workspace]` section in `config/core.toml`). The two types cannot be mixed.

#### workspace-init
```bash
workspace-init [--root <dir>] [--output <path>] [--inline] [--force] [--max-depth <N>] [--dry-run]
```
Initialize a multi-repo workspace by scanning nested sub-directories for repos with cypilot directories. Rejects cross-type conflicts (inline vs standalone) and requires `--force` to reinitialize an existing workspace. Scanning depth is limited by `--max-depth` (default 3) to prevent unbounded traversal; symlinks are skipped.

#### workspace-add
```bash
workspace-add --name <name> (--path <path> | --url <url>) [--branch <branch>] [--role <role>] [--adapter <path>] [--inline] [--force]
```
Add a source to a workspace config. Auto-detects standalone vs inline workspace. Use `--inline` to force adding to `config/core.toml`. Git URL sources are not supported in inline mode. `--path` is validated at add-time; returns error if directory not found. Returns error if source name already exists unless `--force` is specified.

#### workspace-info
```bash
workspace-info
```
Display workspace config, list sources, show per-source status (cypilot dir found, artifact count, reachability).

#### workspace-sync
```bash
workspace-sync [--source <name>] [--dry-run] [--force]
```
Fetch and update worktrees for Git URL sources. Use `--source` to sync a single source. Use `--dry-run` to preview without network operations. Use `--force` to skip dirty worktree check (**WARNING: DESTRUCTIVE** — uncommitted changes will be discarded via `git reset --hard` and local commits may be lost via `git checkout -B`). Local path sources are skipped. Source resolution does not perform network operations for existing repos — use `workspace-sync` to explicitly update.

---

## Auto-Configuration

Use auto-config after `cypilot init` on a brownfield project, when project conventions are unknown, or after major structural changes. It scans structure/conventions, generates `{cypilot_path}/config/rules/{slug}.md`, adds WHEN rules to `{cypilot_path}/config/AGENTS.md`, and registers systems in `{cypilot_path}/config/artifacts.toml`. Invoke via `cypilot auto-config`, `cypilot configure`, or the automatic offer inside `generate.md`.

## Project Configuration

Project configuration lives in `{cypilot_path}/config/core.toml` (systems, kits, ignore lists). Artifact registry lives in `{cypilot_path}/config/artifacts.toml` (artifact paths, kinds, system mappings, codebase paths, autodetect rules). All commands output JSON when invoked with `--json`. Exit codes: 0=PASS, 1=filesystem error, 2=FAIL.
