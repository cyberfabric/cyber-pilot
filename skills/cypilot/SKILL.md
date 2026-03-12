---
name: cypilot
description: "Invoke when user asks to do something with Cypilot, or wants to analyze/validate artifacts, or create/generate/implement anything using Cypilot workflows. Core capabilities: workflow routing (analyze/generate/auto-config); deterministic validation (structure, cross-refs, traceability, TOC); code↔artifact traceability with @cpt-* markers; spec coverage measurement; ID search/navigation; init/bootstrap; adapter + registry discovery; auto-configuration of brownfield projects (scan conventions, generate rules); kit management (install/update with file-level diff); TOC generation; agent integrations (Windsurf, Cursor, Claude, Copilot, OpenAI)."
---

# Cypilot Unified Tool

## Goal

Cypilot provides: artifact validation, cross-reference validation, code traceability, spec coverage measurement, ID search/navigation, kit management (install/update with file-level diff), TOC generation/validation, multi-agent integration, and design-to-code implementation with `@cpt-*` markers.

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
- [ ] I will include a list of Cypilot files read while producing the response, why each file was read, and which initial instruction triggered opening each file — ALWAYS placed BEFORE any user action prompt (approve all, yes/no, proceed, modify, etc.) so the user sees context before deciding

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

### Template Variable Resolution

Kit markdown files (SKILL.md, AGENTS.md, rules.md, workflows) use template variables like `{adr_template}`, `{scripts}`, `{workflow_pr_review}`, etc. These are **resource identifiers** declared in the kit's `manifest.toml` and registered in `core.toml` after installation.

**How to resolve variables**:

1. **From `info` output** (automatic during Protocol Guard): The `info` command includes a `variables` dict that maps every template variable to its absolute path. Parse the `variables` field from the JSON output.

2. **Dedicated command** (when you need a fresh or filtered variable map):
```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json resolve-vars
```

**Variable sources** (merged in order):
- **System**: `cypilot_path`, `project_root`
- **Kit resources**: all resource IDs from installed kits (e.g., `adr_template`, `scripts`, `workflow_pr_review`)

ALWAYS use the resolved absolute path WHEN encountering a `{variable}` reference in any Cypilot markdown file.

ALWAYS resolve variables from the `info` output first — the `variables` dict is already available after Protocol Guard.

## Protocol Guard

ALWAYS FIRST open and remember `{cypilot_path}/.gen/AGENTS.md`

ALWAYS open and follow `{cypilot_path}/config/AGENTS.md` WHEN it exists

ALWAYS open and follow `{cypilot_path}/.gen/SKILL.md` WHEN it exists

ALWAYS open and follow `{cypilot_path}/config/SKILL.md` WHEN it exists

ALWAYS FIRST run `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json info` BEFORE any Cypilot workflow action

ALWAYS store the `variables` dict from `info` output — use it to resolve `{variable}` references in kit files (AGENTS.md, SKILL.md, rules.md, workflows)

ALWAYS FIRST read `{cypilot_path}/.gen/AGENTS.md` WHEN cypilot status is FOUND

ALWAYS resolve `{variable}` references in loaded kit files using the `variables` dict from `info` output

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
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json <subcommand> [options]
```

ALWAYS pass `--json` as the FIRST argument (before the subcommand) WHEN invoking any Cypilot CLI command from an AI agent. This ensures machine-readable JSON output on stdout. Without `--json`, the CLI produces human-friendly output intended for interactive terminal use.

ALWAYS use `=` form for pattern args starting with `-`: `--pattern=-req-`

---

## Quick Commands (No Protocol)

ALWAYS SKIP Protocol Guard and workflow loading WHEN user invokes quick commands

ALWAYS run `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json init --yes` directly WHEN user invokes `cypilot init`

ALWAYS run `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json generate-agents --agent <name>` directly WHEN user invokes `cypilot generate-agents <name>`

ALWAYS open and follow `{cypilot_path}/.core/workflows/generate.md` directly WHEN user invokes `cypilot auto-config` or `cypilot configure` — generate.md will trigger the auto-config methodology

---

## Workflow Routing

Cypilot has exactly **TWO** workflows. No exceptions.

ALWAYS open and follow `{cypilot_path}/.core/workflows/generate.md` WHEN user intent is WRITE: create, edit, fix, update, implement, refactor, delete, add, setup, configure, build, code

ALWAYS open and follow `{cypilot_path}/.core/workflows/analyze.md` WHEN user intent is READ: analyze, validate, review, analyze, check, inspect, audit, compare, list, show, find

ALWAYS ask user "analyze (read-only) or generate (modify)?" WHEN intent is UNCLEAR: help, look at, work with, handle and STOP WHEN user cancel or exit

> **Note**: `generate.md` auto-triggers the auto-config methodology (`requirements/auto-config.md`) when it detects a brownfield project with no project-specific rules. "configure" intent routes through generate.md.

## Command Reference

All commands use the entrypoint:
```bash
python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py <command> [options]
```

All commands output JSON to stdout when invoked with `--json`. Without `--json`, output is human-friendly. Exit codes: 0=PASS, 1=filesystem/config error, 2=FAIL.

### Validation Commands

#### validate
```bash
validate [--artifact <path>] [--skip-code] [--verbose] [--output <path>]
```
Validates artifacts and code with deterministic checks (structure, cross-refs, task statuses, traceability markers — pairing, coverage, orphans).

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
list-ids [--artifact <path>] [--pattern <string>] [--regex] [--kind <string>] [--all] [--include-code]
```
Lists all Cypilot IDs from registered artifacts. Supports filtering by pattern, kind, and optional code scanning.

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
agents --agent <name> [--root <path>] [--cypilot-root <path>] [--dry-run]
```
Generates agent-specific workflow proxies and skill entry points.
Supported: windsurf, cursor, claude, copilot, openai.

Shortcut: `agents --openai`

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

Project configuration is stored in `{cypilot_path}/config/core.toml`:
- System definitions (name, slug)
- Kit registrations and paths
- Ignore lists for validation

Artifact registry: `{cypilot_path}/config/artifacts.toml`
- Artifact paths, kinds, and system mappings
- Codebase paths for traceability scanning
- Autodetect rules for artifact discovery

All commands output JSON when invoked with `--json`. Exit codes: 0=PASS, 1=filesystem error, 2=FAIL.
