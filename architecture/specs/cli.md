---
cypilot: true
type: spec
name: Cypilot CLI Specification
version: 1.0
purpose: Complete CLI interface specification for the cypilot tool
drivers:
  - cpt-cypilot-fr-core-installer
  - cpt-cypilot-fr-core-init
  - cpt-cypilot-fr-core-skill-engine
  - cpt-cypilot-fr-core-cli-config
  - cpt-cypilot-fr-core-version
  - cpt-cypilot-fr-core-template-qa
  - cpt-cypilot-fr-core-doctor
  - cpt-cypilot-fr-core-hooks
  - cpt-cypilot-fr-core-completions
  - cpt-cypilot-fr-core-traceability
  - cpt-cypilot-fr-core-blueprint
  - cpt-cypilot-interface-cli-json
---

# Cypilot CLI Specification

---

## Table of Contents

- [Cypilot CLI Specification](#cypilot-cli-specification)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Installation](#installation)
  - [Invocation Model](#invocation-model)
  - [Global Conventions](#global-conventions)
    - [Output](#output)
    - [Exit Codes](#exit-codes)
    - [Common Options](#common-options)
  - [Core Commands](#core-commands)
    - [init](#init)
    - [update](#update)
    - [validate](#validate)
    - [list-ids](#list-ids)
    - [where-defined](#where-defined)
    - [where-used](#where-used)
    - [get-content](#get-content)
    - [list-id-kinds](#list-id-kinds)
    - [adapter-info](#adapter-info)
    - [agents](#agents)
    - [generate-resources](#generate-resources)
    - [doctor](#doctor)
    - [self-check](#self-check)
    - [config](#config)
      - [config show](#config-show)
      - [config system add](#config-system-add)
      - [config system remove](#config-system-remove)
      - [config system rename](#config-system-rename)
      - [config ignore add](#config-ignore-add)
      - [config ignore remove](#config-ignore-remove)
      - [config kit install](#config-kit-install)
    - [hook](#hook)
    - [completions](#completions)
  - [Kit Commands](#kit-commands)
    - [SDLC Kit Commands](#sdlc-kit-commands)
      - [sdlc autodetect show](#sdlc-autodetect-show)
      - [sdlc autodetect add-artifact](#sdlc-autodetect-add-artifact)
      - [sdlc autodetect add-codebase](#sdlc-autodetect-add-codebase)
      - [sdlc pr-review](#sdlc-pr-review)
      - [sdlc pr-status](#sdlc-pr-status)
  - [Output Format](#output-format)
  - [Exit Codes](#exit-codes-1)
  - [Environment Variables](#environment-variables)
  - [File System Layout](#file-system-layout)
    - [Global (per user)](#global-per-user)
    - [Project (per repository)](#project-per-repository)
    - [Agent Entry Points (generated)](#agent-entry-points-generated)
  - [Error Handling](#error-handling)
    - [Common Errors](#common-errors)
    - [Error Output](#error-output)
  - [Version Negotiation](#version-negotiation)

---

## Overview

Cypilot provides a CLI tool available as `cypilot` (full name) and `cpt` (short alias). The tool follows a two-layer architecture:

1. **Global CLI Proxy** — a thin shell installed globally via `pipx`, containing zero business logic. It resolves the correct skill bundle and proxies all commands to it.
2. **Skill Engine** — the actual command executor, installed either in the project (`.cypilot/`) or in the global cache (`~/.cypilot/cache/`).

All CLI output is JSON to stdout. Human-readable messages go to stderr. This enables piping and programmatic consumption.

---

## Installation

```bash
pipx install git+https://github.com/cyberfabric/cyber-pilot.git
```

After installation, both `cypilot` and `cpt` are available globally.

**Requirements**:
- Python 3.10+
- `pipx` (recommended) or `pip`

**Optional**:
- `git` — enhanced project detection via `.git` directory; not required
- `gh` CLI v2.0+ — required only for PR review/status commands

---

## Invocation Model

On every invocation, the CLI Proxy executes the following sequence:

1. **Cache check** — if `~/.cypilot/cache/` does not exist or is empty, download the latest skill bundle from GitHub before proceeding.
2. **Target resolution** — if the current directory is inside a project with `.cypilot/` directory, proxy to the project-installed skill. Otherwise, proxy to the cached skill.
3. **Background version check** — start a non-blocking check for newer versions. The check MUST NOT delay the main command. Concurrent checks are prevented via a lock file. A newly available version becomes visible on the next invocation.
4. **Version notice** — if the cached version is newer than the project-installed version, display a notice to stderr: `Cypilot {cached_version} available (project has {project_version}). Run 'cypilot update' to upgrade.`
5. **Command execution** — forward all arguments to the resolved skill engine.

```
cypilot <command> [subcommand] [options] [arguments]
cpt <command> [subcommand] [options] [arguments]
```

---

## Global Conventions

### Output

- **stdout** — JSON only. Every command outputs a JSON object or array.
- **stderr** — human-readable messages (progress, warnings, notices).
- **`--quiet`** — suppress stderr output.
- **`--verbose`** — increase stderr detail level.

### Exit Codes

| Code | Meaning | When |
|------|---------|------|
| 0 | PASS / Success | Command completed successfully |
| 1 | Error | Filesystem error, invalid arguments, runtime error |
| 2 | FAIL | Validation failed, check failed, item not found |

### Common Options

| Option | Description |
|--------|-------------|
| `--version` | Show cache and project skill versions |
| `--help` | Show help for command |
| `--json` | Force JSON output (default, explicit for clarity) |
| `--quiet` | Suppress stderr |
| `--verbose` | Increase stderr detail |

---

## Core Commands

### init

Initialize Cypilot in a project.

```
cypilot init [--dir DIR] [--agents AGENTS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--dir` | `.cypilot` | Installation directory |
| `--agents` | all | Comma-separated agent list: `windsurf,cursor,claude,copilot,openai` |

**Behavior**:
1. Check if Cypilot is already installed. If yes → abort with message, suggest `cypilot update`.
2. If interactive terminal → prompt for installation directory and agent selection.
3. Copy skill bundle from cache into the install directory.
4. Define the **root system** — derive name and slug from the project directory name (e.g., directory `my-app/` → `name = "MyApp"`, `slug = "my-app"`).
5. Create `config/core.toml` with project root, root system definition, and kit registrations.
6. Create `config/artifacts.toml` with a fully populated root system entry including default SDLC autodetect rules:
   - `artifacts_dir = "architecture"` (default artifact directory)
   - Autodetect rules for standard artifact kinds: `PRD.md`, `DESIGN.md`, `ADR/*.md`, `DECOMPOSITION.md`, `features/*.md` — all with default traceability levels and glob patterns
   - Default codebase entry: `path = "src"`, common extensions
   - Default ignore patterns: `vendor/*`, `node_modules/*`, `.git/*`
7. Install all available kits. Each kit generates its config in `config/kits/<slug>/` — blueprints, constraints, artifacts, workflows.
8. Generate agent entry points for selected agents.
9. Inject root `AGENTS.md` entry: insert managed `<!-- @cpt:root-agents -->` block at the beginning of `{project_root}/AGENTS.md` (create file if absent).
10. Create `config/AGENTS.md` with default WHEN rules for standard system prompts.
11. Output prompt suggestion: `cypilot on` or `cypilot help`.

**Root AGENTS.md integrity**: every CLI invocation (not just `init`) verifies the `<!-- @cpt:root-agents -->` block in root `AGENTS.md` exists and contains the correct path. If missing or stale, the block is silently re-injected. See [sysprompts.md](./sysprompts.md) for full format.

**Output** (JSON):
```json
{
  "status": "ok",
  "install_dir": ".cypilot",
  "kits_installed": ["sdlc"],
  "agents_configured": ["windsurf", "cursor", "claude", "copilot", "openai"],
  "systems": [{"name": "my-project", "slug": "my-project", "kit": "sdlc"}]
}
```

**Exit**: 0 on success, 1 on error, 2 if already initialized.

---

### update

Update project skill to the cached version.

```
cypilot update [--check] [--force]
```

| Option | Description |
|--------|-------------|
| `--check` | Show available updates without applying |
| `--force` | Force update even if versions match |

**Behavior**:
1. If `--check` → compare versions, output diff, exit.
2. If cache is outdated → download latest release from GitHub first.
3. Copy cached skill into project install directory.
4. Migrate `config/core.toml` to new schema version (preserve all user settings).
5. Invoke each kit's migration script for kit config files.
6. Update blueprints via reference-based three-way diff.
7. Regenerate all resources from updated blueprints.
8. Regenerate agent entry points.

**Output** (JSON):
```json
{
  "status": "ok",
  "previous_version": "0.5.0",
  "new_version": "0.6.0",
  "kits_migrated": ["sdlc"],
  "blueprints_updated": 5,
  "blueprints_conflicts": 0,
  "agent_entry_points_regenerated": true
}
```

**Exit**: 0 on success, 1 on error.

---

### validate

Validate artifacts.

```
cypilot validate [--artifact PATH] [--system SYSTEM] [--kind KIND] [--strict] [--blueprints]
```

| Option | Description |
|--------|-------------|
| `--artifact PATH` | Validate a single artifact file |
| `--system SYSTEM` | Validate all artifacts for a system |
| `--kind KIND` | Filter by artifact kind (PRD, DESIGN, etc.) |
| `--strict` | Enable strict validation (all checklist items) |
| `--blueprints` | Validate all blueprint files instead of artifacts |

**Without arguments**: validate all registered artifacts across all systems.

**Behavior (artifact validation)**:
1. Load config and resolve target artifacts via autodetect rules.
2. For each artifact:
   a. **Structural validation** — template heading compliance, required sections.
   b. **ID validation** — format, uniqueness, priority markers.
   c. **Placeholder detection** — TODO, TBD, FIXME.
   d. **Constraint enforcement** — allowed ID kinds per artifact kind from constraints.toml.
3. If multiple artifacts → **cross-artifact validation**:
   a. `covered_by` reference completeness.
   b. Checked-ref-implies-checked-def consistency.
   c. All ID references resolve to definitions.
4. Output score breakdown with actionable issues (file path, line number, severity).

**Behavior (blueprint validation, `--blueprints`)**:
1. Discover all blueprint files in `config/kits/<slug>/blueprints/*.md` across installed kits.
2. For each blueprint:
   a. **Header check** — `cpt:blueprint` marker present and is the first marker.
   b. **Block closure** — all block markers (`cpt:skill`, `cpt:check`, `cpt:prompt`, `cpt:rule`, etc.) have matching `@/cpt:...` close tags.
   c. **No nesting** — no block markers inside other block markers.
   d. **Known markers** — all marker types are registered by core or a loaded kit.
   e. **Attribute validity** — required attributes present, values in expected ranges.
   f. **Unique IDs** — heading IDs and check IDs unique within the blueprint.
   g. **Heading order** — `cpt:heading` markers appear in a valid document order (by level hierarchy).
   h. **Version compatibility** — blueprint version supported by current processor.
3. Output issues per blueprint with file path, line number, and error code.

**Output** (JSON):
```json
{
  "status": "PASS",
  "artifacts_validated": 3,
  "error_count": 0,
  "warning_count": 2,
  "issues": [
    {
      "file": "architecture/PRD.md",
      "line": 42,
      "severity": "warning",
      "rule": "PLACEHOLDER",
      "message": "TODO marker detected"
    }
  ],
  "next_step": "Deterministic validation passed. Now perform semantic validation."
}
```

**Exit**: 0=PASS, 2=FAIL.

---

### list-ids

List IDs matching criteria.

```
cypilot list-ids [--kind KIND] [--pattern PATTERN] [--system SYSTEM] [--format FORMAT]
```

| Option | Description |
|--------|-------------|
| `--kind KIND` | Filter by ID kind (fr, nfr, actor, component, etc.) |
| `--pattern PATTERN` | Glob or regex filter on ID slug |
| `--system SYSTEM` | Limit to a specific system |
| `--format FORMAT` | Output format: `json` (default), `table`, `ids-only` |

**Output** (JSON):
```json
{
  "ids": [
    {
      "id": "cpt-cypilot-fr-core-init",
      "kind": "fr",
      "file": "architecture/PRD.md",
      "line": 154,
      "checked": false,
      "priority": "p1"
    }
  ],
  "total": 42
}
```

**Exit**: 0.

---

### where-defined

Find where an ID is defined.

```
cypilot where-defined <id>
```

**Output** (JSON):
```json
{
  "id": "cpt-cypilot-fr-core-init",
  "defined_in": {
    "file": "architecture/PRD.md",
    "line": 154,
    "kind": "fr",
    "checked": false,
    "content_preview": "The system MUST provide an interactive `cypilot init` command..."
  }
}
```

**Exit**: 0=found, 2=not found.

---

### where-used

Find where an ID is referenced.

```
cypilot where-used <id>
```

**Output** (JSON):
```json
{
  "id": "cpt-cypilot-fr-core-init",
  "references": [
    {
      "file": "architecture/DESIGN.md",
      "line": 62,
      "context": "inline_reference"
    }
  ],
  "total": 3
}
```

**Exit**: 0.

---

### get-content

Get content block for an ID definition.

```
cypilot get-content <id>
```

**Output** (JSON):
```json
{
  "id": "cpt-cypilot-fr-core-init",
  "file": "architecture/PRD.md",
  "line_start": 154,
  "line_end": 159,
  "content": "The system MUST provide an interactive `cypilot init` command..."
}
```

**Exit**: 0=found, 2=not found.

---

### list-id-kinds

List all ID kinds known to the system.

```
cypilot list-id-kinds [--system SYSTEM]
```

**Output** (JSON):
```json
{
  "kinds": [
    {"kind": "fr", "artifact": "PRD", "kit": "sdlc", "count": 18},
    {"kind": "nfr", "artifact": "PRD", "kit": "sdlc", "count": 6},
    {"kind": "component", "artifact": "DESIGN", "kit": "sdlc", "count": 8}
  ]
}
```

**Exit**: 0.

---

### adapter-info

Show adapter status and registry information.

```
cypilot adapter-info
```

**Output** (JSON):
```json
{
  "adapter_path": ".cypilot-adapter",
  "artifacts_json": ".cypilot-adapter/artifacts.toml",
  "systems": [
    {
      "name": "Cypilot",
      "slug": "cypilot",
      "kit": "sdlc",
      "artifacts_root": "architecture",
      "artifacts_found": 3,
      "codebase_paths": ["skills/cypilot/scripts/"]
    }
  ],
  "kits": [
    {"slug": "sdlc", "version": "1.0", "path": "kits/sdlc"}
  ]
}
```

**Exit**: 0.

---

### agents

Generate agent entry points.

```
cypilot agents [--agent AGENT]
```

| Option | Description |
|--------|-------------|
| `--agent AGENT` | Generate for a specific agent only: `windsurf`, `cursor`, `claude`, `copilot`, `openai` |

**Without `--agent`**: regenerate for all agents.

**Behavior**:
1. Collect `cpt:skill` extension sections from all loaded blueprints.
2. Compose the main SKILL.md from core commands + collected extensions.
3. Generate workflow entry points in each agent's native format.
4. Generate skill shims referencing the composed SKILL.md.
5. Full overwrite on each invocation (no merge with existing files).

**Output targets**:
| Agent | Entry Points Directory |
|-------|----------------------|
| Windsurf | `.windsurf/workflows/` |
| Cursor | `.cursor/rules/` |
| Claude | `.claude/commands/` |
| Copilot | `.github/prompts/` |
| OpenAI | `.openai/` |

**Exit**: 0.

---

### generate-resources

Generate all kit resources from blueprints.

```
cypilot generate-resources [--kit KIT] [--artifact-kind KIND] [--dry-run]
```

| Option | Description |
|--------|-------------|
| `--kit KIT` | Generate for a specific kit only |
| `--artifact-kind KIND` | Generate for a specific artifact kind only |
| `--dry-run` | Show what would be generated without writing |

**Behavior**:
1. Load all blueprints for target kits/artifact kinds.
2. Parse `@cpt:` markers.
3. Invoke core output generators per marker type.
4. Write output files (template.md, rules.md, checklist.md, example.md per artifact; constraints.toml kit-wide; codebase/ for non-artifact blueprints).
5. Generation is deterministic: same blueprint → same output.

**Output** (JSON):
```json
{
  "status": "ok",
  "generated": [
    {"blueprint": "config/kits/sdlc/blueprints/PRD.md", "outputs": ["template.md", "rules.md", "checklist.md"]},
    {"blueprint": "config/kits/sdlc/blueprints/DESIGN.md", "outputs": ["template.md", "rules.md", "checklist.md"]}
  ],
  "constraints_toml_updated": true
}
```

**Exit**: 0 on success, 1 on error.

---

### doctor

Environment health check.

```
cypilot doctor
```

**Checks performed**:
| Check | Pass Condition |
|-------|---------------|
| Python version | ≥ 3.10 |
| git available | `git --version` succeeds (optional, not required) |
| gh CLI | `gh auth status` succeeds (required only for PR commands) |
| Agent detection | at least one supported agent directory found |
| Config integrity | `config/core.toml` exists and parses, schema valid |
| Skill version | project skill matches or is newer than cache |
| Kit structure | all registered kits have valid entry points |
| Blueprint integrity | all blueprints in `config/kits/<slug>/blueprints/` parse successfully, reference kits in `{cypilot_path}/.core/kits/` present |

**Output** (JSON):
```json
{
  "status": "healthy",
  "checks": [
    {"name": "python_version", "status": "pass", "detail": "3.12.1"},
    {"name": "git", "status": "pass", "detail": "2.43.0"},
    {"name": "gh_cli", "status": "warn", "detail": "not authenticated", "remediation": "Run 'gh auth login'"}
  ]
}
```

**Exit**: 0=healthy, 2=issues found.

---

### self-check

Validate example artifacts against their templates.

```
cypilot self-check [--strict] [--kit KIT]
```

**Behavior**:
1. For each artifact kind in each kit, locate example artifacts.
2. Validate each example against its template structure.
3. If `--strict`, apply full checklist validation.

**Exit**: 0=PASS, 2=FAIL.

---

### config

Manage project configuration.

```
cypilot config <subcommand> [options]
```

#### config show

```
cypilot config show [--section SECTION]
```

Display current core configuration. Optional `--section` to show only a part (systems, kits, ignore).

#### config system add

```
cypilot config system add --name NAME --slug SLUG --kit KIT
```

Add a system definition to `config/core.toml`.

#### config system remove

```
cypilot config system remove --slug SLUG
```

Remove a system definition.

#### config system rename

```
cypilot config system rename --slug SLUG --new-name NAME [--new-slug SLUG]
```

#### config ignore add

```
cypilot config ignore add --pattern PATTERN [--reason REASON]
```

Add a path pattern to the ignore list.

#### config ignore remove

```
cypilot config ignore remove --pattern PATTERN
```

#### config kit install

```
cypilot config kit install --slug SLUG --path PATH
```

Register and install a kit.

All config subcommands support `--dry-run` to preview changes without writing.

**Exit**: 0 on success, 1 on error.

---

### hook

Manage git pre-commit hooks.

```
cypilot hook install
cypilot hook uninstall
```

**`install`**: creates a git pre-commit hook that runs `cypilot lint` on changed artifact files. The hook MUST complete in ≤ 5 seconds for typical changes.

**`uninstall`**: removes the Cypilot pre-commit hook.

**Exit**: 0 on success, 1 on error.

---

### completions

Manage shell completions.

```
cypilot completions install [--shell SHELL]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--shell` | auto-detect | `bash`, `zsh`, or `fish` |

**Exit**: 0 on success, 1 on error.

---

## Kit Commands

Kit plugins register their own CLI subcommands under the kit's slug namespace.

### SDLC Kit Commands

#### sdlc autodetect show

```
cypilot sdlc autodetect show --system SYSTEM
```

Show autodetect rules (artifact patterns, traceability levels, codebase paths) for a system.

#### sdlc autodetect add-artifact

```
cypilot sdlc autodetect add-artifact --system SYSTEM --kind KIND --pattern PATTERN [--traceability FULL|DOCS-ONLY] [--required]
```

#### sdlc autodetect add-codebase

```
cypilot sdlc autodetect add-codebase --system SYSTEM --name NAME --path PATH --extensions EXTS
```

#### sdlc pr-review

```
cypilot sdlc pr-review <number> [--checklist CHECKLIST] [--prompt PROMPT]
```

Review a GitHub PR. Fetches diffs and metadata via `gh` CLI, analyzes against configured prompts and checklists. Read-only (no local modifications). Always re-fetches on each invocation.

#### sdlc pr-status

```
cypilot sdlc pr-status <number>
```

Check PR status: comment severity classification, CI status, merge conflict state, unreplied comment audit.

**All SDLC commands**: exit 0 on success, 1 on error.

---

## Output Format

All commands produce JSON output to stdout. The structure varies per command but follows common patterns:

**Success with status**:
```json
{"status": "ok", ...}
```

**Validation result**:
```json
{"status": "PASS|FAIL", "error_count": N, "warning_count": N, "issues": [...]}
```

**Item not found**:
```json
{"status": "not_found", "id": "cpt-..."}
```

**Error**:
```json
{"error": "description", "code": "ERROR_CODE"}
```

Error codes are uppercase snake_case identifiers (e.g., `CONFIG_NOT_FOUND`, `INVALID_ARTIFACT_PATH`, `KIT_NOT_REGISTERED`).

---

## Exit Codes

| Code | Name | Description |
|------|------|-------------|
| 0 | SUCCESS | Command completed, validation passed, item found |
| 1 | ERROR | Runtime error, filesystem error, invalid arguments |
| 2 | FAIL | Validation failed, check failed, item not found |

CI pipelines should check for exit code 2 to detect validation failures.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CYPILOT_CACHE_DIR` | Override cache directory location | `~/.cypilot/cache/` |
| `CYPILOT_NO_VERSION_CHECK` | Disable background version check | unset |
| `CYPILOT_NO_COLOR` | Disable colored stderr output | unset |
| `NO_COLOR` | Standard no-color convention (respected) | unset |

---

## File System Layout

### Global (per user)

```
~/.cypilot/
  cache/                    # Cached skill bundle (latest downloaded)
    skills/
    kits/
    ...
  version-check.lock        # Prevents concurrent version checks
```

### Project (per repository)

```
.cypilot/                   # Install directory (configurable)
  skills/                   # Skill bundle (copied from cache)
  kits/                     # Reference kit copies (installed on kit install)
    sdlc/
      blueprints/           # Reference blueprints (one .md per artifact kind)
        PRD.md
        DESIGN.md
        ...
      scripts/              # Kit scripts (not copied to config/)
  workflows/                # Core workflows (generate.md, analyze.md)
  requirements/             # Core requirement specs
  schemas/                  # JSON schemas
config/
  AGENTS.md                 # Project-level navigation (WHEN → sysprompt)
  core.toml                 # Core config (systems, kits, ignore)
  sysprompts/               # Project-specific system prompts
  kits/
    sdlc/                   # Installed kit
      blueprints/           # User-editable blueprint copies
        PRD.md
        DESIGN.md
        ...
      constraints.toml     # Generated: kit-wide structural constraints
      artifacts/            # Generated outputs per artifact kind
        PRD/
          template.md
          rules.md
          checklist.md
          example.md
        DESIGN/
          ...
      codebase/             # Generated from blueprints without artifact key
        rules.md
        checklist.md
      workflows/            # Generated from @cpt:workflow markers
```

### Agent Entry Points (generated)

```
.windsurf/workflows/        # Windsurf workflow proxies
.cursor/rules/              # Cursor rule files
.claude/commands/           # Claude command files
.github/prompts/            # Copilot prompt files
```

---

## Error Handling

### Common Errors

| Error Code | Cause | Resolution |
|------------|-------|------------|
| `NOT_INITIALIZED` | Command run outside a Cypilot project | Run `cypilot init` |
| `CONFIG_NOT_FOUND` | `config/core.toml` missing or corrupt | Run `cypilot init` or `cypilot doctor` |
| `KIT_NOT_REGISTERED` | Referenced kit not in config | Run `cypilot config kit install` |
| `ARTIFACT_NOT_FOUND` | Specified artifact path does not exist | Check path |
| `SCHEMA_VALIDATION` | Config file does not match schema | Run `cypilot doctor` for details |
| `GH_CLI_NOT_FOUND` | `gh` CLI not installed (PR commands only) | Install `gh` CLI |
| `GH_NOT_AUTHENTICATED` | `gh` CLI not authenticated | Run `gh auth login` |
| `BLUEPRINT_UPDATE_CONFLICT` | User and kit both modified the same section during additive update | Resolve conflicts in `<KIND>.md.conflicts`, then run `cypilot generate-resources` |
| `CACHE_EMPTY` | No cached skill and download failed | Check network, retry |

### Error Output

All errors produce JSON to stdout:
```json
{
  "error": "Human-readable description",
  "code": "ERROR_CODE",
  "details": {}
}
```

Plus a human-readable message to stderr.

---

## Version Negotiation

```
cypilot --version
```

**Output** (JSON):
```json
{
  "proxy_version": "0.6.0",
  "cache_version": "0.6.0",
  "project_version": "0.5.0",
  "update_available": true
}
```

The proxy version is the version of the globally installed CLI proxy (`pipx` package). The cache version is the version of the skill bundle in `~/.cypilot/cache/`. The project version is the version of the skill installed in the project's `.cypilot/` directory (null if not in a project).
