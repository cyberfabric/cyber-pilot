# Feature: Core Infrastructure

- [ ] `p1` - **ID**: `cpt-cypilot-featstatus-core-infra`

## 1. Feature Context

- [ ] `p1` - `cpt-cypilot-feature-core-infra`

### 1.1 Overview

Foundation layer providing the global CLI proxy, skill engine command dispatch, config directory management, and project initialization. This feature is the base upon which all other Cypilot features are built — no other feature can function without it.

### 1.2 Purpose

Enables users to install Cypilot globally, initialize it in any project with sensible defaults, and execute deterministic commands with consistent JSON output. Addresses PRD requirements for a ≤5-minute install-to-init experience (`cpt-cypilot-fr-core-installer`, `cpt-cypilot-fr-core-init`) and a structured config directory (`cpt-cypilot-fr-core-config`).

### 1.3 Actors

| Actor | Role in Feature |
|-------|-----------------|
| `cpt-cypilot-actor-user` | Runs `cypilot init`, `cypilot config show`, `cypilot migrate-config` |
| `cpt-cypilot-actor-cypilot-cli` | Global proxy that resolves skill target and forwards commands |

### 1.4 References

- **PRD**: [PRD.md](../PRD.md)
- **Design**: [DESIGN.md](../DESIGN.md)
- **CLI Spec**: [cli.md](../specs/cli.md)
- **Dependencies**: None (foundation feature)

## 2. Actor Flows (CDSL)

### Global CLI Invocation

- [x] `p1` - **ID**: `cpt-cypilot-flow-core-infra-cli-invocation`

**Actors**:

- `cpt-cypilot-actor-user`
- `cpt-cypilot-actor-cypilot-cli`

**Success Scenarios**:
- User runs any `cypilot` command from inside a project → routed to project-installed skill
- User runs `cypilot` command outside a project → routed to cached skill
- First run after `pipx install` with empty cache → skill bundle downloaded from GitHub automatically

**Error Scenarios**:
- GitHub download fails (network, rate limit) → error with retry instructions
- Python version < 3.10 → error with version requirement

**Steps**:
1. [x] - `p1` - User invokes `cypilot <command> [args]` from terminal - `inst-user-invokes`
2. [x] - `p1` - CLI proxy checks for project-installed skill at `.cypilot/` in current or parent directories - `inst-check-project-skill`
3. [x] - `p1` - **IF** project skill found - `inst-if-project-skill`
   1. [x] - `p1` - Forward command and args to project skill engine - `inst-forward-project`
4. [x] - `p1` - **ELSE** - `inst-else-no-project`
   1. [x] - `p1` - Check cached skill at `~/.cypilot/cache/` - `inst-check-cache`
   2. [x] - `p1` - **IF** cached skill exists - `inst-if-cache`
      1. [x] - `p1` - Forward command and args to cached skill engine - `inst-forward-cache`
   3. [x] - `p1` - **ELSE** no cached skill — first run after install - `inst-else-no-cache`
      1. [x] - `p1` - Algorithm: download and cache skill using `cpt-cypilot-algo-core-infra-cache-skill` - `inst-auto-download`
      2. [x] - `p1` - **IF** download failed - `inst-if-download-failed`
         1. [x] - `p1` - **RETURN** error: "Failed to download Cypilot skill. Check network and retry." (exit 1) - `inst-return-download-error`
      3. [x] - `p1` - Forward command and args to freshly cached skill engine - `inst-forward-fresh-cache`
5. [x] - `p1` - Skill engine executes command, produces JSON to stdout - `inst-engine-execute`
6. [x] - `p1` - CLI proxy performs non-blocking background version check - `inst-bg-version-check`
7. [x] - `p1` - **IF** cached version newer than project version - `inst-if-version-mismatch`
   1. [x] - `p1` - Display update notice to stderr - `inst-show-update-notice`
8. [x] - `p1` - **IF** first arg is `--update-cache` - `inst-if-update-cache`
   1. [x] - `p1` - Algorithm: download and cache skill using `cpt-cypilot-algo-core-infra-cache-skill` with optional version/branch/SHA argument - `inst-explicit-cache-update`
   2. [x] - `p1` - **RETURN** JSON: `{status, message, version}` (exit 0 on success, 1 on failure) - `inst-return-cache-update`
9. [x] - `p1` - **RETURN** exit code from skill engine (0=PASS, 1=error, 2=FAIL) - `inst-return-exit`

### Project Initialization

- [ ] `p1` - **ID**: `cpt-cypilot-flow-core-infra-project-init`

**Actors**:

- `cpt-cypilot-actor-user`
- `cpt-cypilot-actor-cypilot-cli`

**Success Scenarios**:
- User initializes a fresh project → full config created, root system defined, AGENTS.md injected
- User initializes with custom directory and agent selection → respects choices

**Error Scenarios**:
- Cypilot already initialized → abort with suggestion to use `cypilot update`
- No cached skill bundle → error with install instructions

**Steps**:
1. [ ] - `p1` - User invokes `cypilot init [--dir DIR] [--agents AGENTS]` - `inst-user-init`
2. [ ] - `p1` - Check if `.cypilot/` (or specified dir) already exists - `inst-check-existing`
3. [ ] - `p1` - **IF** already initialized - `inst-if-exists`
   1. [ ] - `p1` - **RETURN** error: "Cypilot already initialized. Use 'cypilot update' to upgrade." (exit 2) - `inst-return-exists`
4. [ ] - `p1` - **IF** interactive terminal AND no --dir flag - `inst-if-interactive`
   1. [ ] - `p1` - Prompt user for installation directory (default: `.cypilot`) - `inst-prompt-dir`
   2. [ ] - `p1` - Prompt user for agent selection (default: all) - `inst-prompt-agents`
5. [ ] - `p1` - Copy skill bundle from `~/.cypilot/cache/` into install directory - `inst-copy-skill`
6. [ ] - `p1` - Algorithm: define root system using `cpt-cypilot-algo-core-infra-define-root-system` - `inst-define-root`
7. [ ] - `p1` - Algorithm: create config directory using `cpt-cypilot-algo-core-infra-create-config` - `inst-create-config`
8. [ ] - `p1` - Delegate kit installation to Kit Manager (Feature 2 boundary) - `inst-delegate-kits`
9. [ ] - `p1` - Delegate agent entry point generation to Agent Generator (Feature 5 boundary) - `inst-delegate-agents`
10. [ ] - `p1` - Algorithm: inject root AGENTS.md using `cpt-cypilot-algo-core-infra-inject-root-agents` - `inst-inject-agents`
11. [ ] - `p1` - Algorithm: create config/AGENTS.md using `cpt-cypilot-algo-core-infra-create-config-agents` - `inst-create-config-agents`
12. [ ] - `p1` - **RETURN** JSON: `{status, install_dir, kits_installed, agents_configured, systems}` (exit 0) - `inst-return-init-ok`


## 3. Processes / Business Logic (CDSL)

### Resolve Skill Target

- [x] `p1` - **ID**: `cpt-cypilot-algo-core-infra-resolve-skill`

**Input**: Current working directory, command arguments

**Output**: Path to skill engine entry point, or error

**Steps**:
1. [x] - `p1` - Walk from current directory upward looking for `AGENTS.md` with `<!-- @cpt:root-agents -->` marker, read `{cypilot}` variable to get install dir - `inst-walk-parents`
2. [x] - `p1` - **IF** install dir found and skill entry point exists at `{cypilot}/skills/cypilot/scripts/cypilot.py` - `inst-if-marker`
   1. [x] - `p1` - **RETURN** path to project skill engine - `inst-return-project-path`
3. [x] - `p1` - **ELSE** check `~/.cypilot/cache/` for cached skill bundle - `inst-check-global-cache`
4. [x] - `p1` - **IF** cache exists - `inst-if-cache-exists`
   1. [x] - `p1` - **RETURN** path to cached skill engine - `inst-return-cache-path`
5. [x] - `p1` - **ELSE** **RETURN** error: no skill found - `inst-return-not-found`

### Route Command

- [x] `p1` - **ID**: `cpt-cypilot-algo-core-infra-route-command`

**Input**: Command name, arguments, resolved skill path

**Output**: JSON to stdout, exit code

**Steps**:
1. [x] - `p1` - Parse command name from first positional argument - `inst-parse-command`
2. [x] - `p1` - Look up command handler in registry - `inst-lookup-handler`
3. [x] - `p1` - **IF** handler not found - `inst-if-no-handler`
   1. [x] - `p1` - **RETURN** error JSON: `{error: "Unknown command"}` (exit 1) - `inst-return-unknown`
4. [x] - `p1` - Parse remaining arguments per handler's argument spec - `inst-parse-args`
5. [x] - `p1` - Verify root AGENTS.md integrity (re-inject if missing/stale) - `inst-verify-agents`
6. [x] - `p1` - Execute handler with parsed arguments - `inst-execute-handler`
7. [x] - `p1` - Serialize handler result to JSON on stdout - `inst-serialize-json`
8. [x] - `p1` - **RETURN** exit code from handler (0=PASS, 1=error, 2=FAIL) - `inst-return-code`

### Define Root System

- [ ] `p1` - **ID**: `cpt-cypilot-algo-core-infra-define-root-system`

**Input**: Project directory path

**Output**: System definition `{name, slug}`

**Steps**:
1. [ ] - `p1` - Extract directory basename from project path (e.g., `/path/to/my-app` → `my-app`) - `inst-extract-basename`
2. [ ] - `p1` - Derive slug: lowercase, replace spaces/underscores with hyphens, strip non-alphanumeric - `inst-derive-slug`
3. [ ] - `p1` - Derive name: convert slug to PascalCase (e.g., `my-app` → `MyApp`) - `inst-derive-name`
4. [ ] - `p1` - **RETURN** `{name, slug}` - `inst-return-system-def`

### Create Config Directory

- [ ] `p1` - **ID**: `cpt-cypilot-algo-core-infra-create-config`

**Input**: Install directory path, root system definition

**Output**: Created `config/core.toml` and `config/artifacts.toml`

**Steps**:
1. [ ] - `p1` - Create `config/` directory inside install directory - `inst-mkdir-config`
2. [ ] - `p1` - Write `config/core.toml` with: project root path, root system definition (name, slug, kit="sdlc"), kit registrations - `inst-write-core-toml`
3. [ ] - `p1` - Write `config/artifacts.toml` with root system entry: - `inst-write-artifacts-toml`
   1. [ ] - `p1` - Set `artifacts_dir = "architecture"` (default) - `inst-set-artifacts-dir`
   2. [ ] - `p1` - Add autodetect rules for standard artifact kinds: PRD.md, DESIGN.md, ADR/*.md, DECOMPOSITION.md, features/*.md — all with default traceability levels - `inst-add-autodetect-rules`
   3. [ ] - `p1` - Add default codebase entry: `path = "src"`, extensions = [".py", ".ts", ".js", ".go", ".rs", ".java"] - `inst-add-codebase`
   4. [ ] - `p1` - Add default ignore patterns: `vendor/*`, `node_modules/*`, `.git/*` - `inst-add-ignore`
4. [ ] - `p1` - Validate both files against schemas before final write - `inst-validate-schemas`
5. [ ] - `p1` - **RETURN** paths to created files - `inst-return-config-paths`

### Inject Root AGENTS.md

- [x] `p1` - **ID**: `cpt-cypilot-algo-core-infra-inject-root-agents`

**Input**: Project root path, install directory path

**Output**: Updated or created `{project_root}/AGENTS.md`

**Steps**:
1. [x] - `p1` - Compute managed block content: Variables table with `{cypilot} = @/{install_dir}`, navigation rule `ALWAYS open and follow {cypilot}/config/AGENTS.md FIRST` - `inst-compute-block`
2. [x] - `p1` - **IF** `{project_root}/AGENTS.md` does not exist - `inst-if-no-agents`
   1. [x] - `p1` - Create file with managed block wrapped in `<!-- @cpt:root-agents -->` markers - `inst-create-agents-file`
3. [x] - `p1` - **ELSE** read existing file content - `inst-read-existing`
   1. [x] - `p1` - **IF** managed block markers found - `inst-if-markers-exist`
      1. [x] - `p1` - Replace content between markers with computed block - `inst-replace-block`
   2. [x] - `p1` - **ELSE** insert managed block at beginning of file - `inst-insert-block`
4. [x] - `p1` - Write file - `inst-write-agents`
5. [x] - `p1` - **RETURN** path to AGENTS.md - `inst-return-agents-path`

### Cache Skill from GitHub

- [x] `p1` - **ID**: `cpt-cypilot-algo-core-infra-cache-skill`

**Input**: Target ref (optional, defaults to "latest") — accepts version tag (v3.0.0), branch name (main), or commit SHA

**Output**: Path to cached skill bundle at `~/.cypilot/cache/`, or error

**Steps**:
1. [x] - `p1` - Create `~/.cypilot/cache/` directory if absent - `inst-mkdir-cache`
2. [x] - `p1` - Resolve target version: if "latest", query GitHub API for latest release tag - `inst-resolve-version`
3. [x] - `p1` - **IF** cached version matches target version - `inst-if-cache-fresh`
   1. [x] - `p1` - **RETURN** existing cache path (no download needed) - `inst-return-cache-hit`
4. [x] - `p1` - Download skill bundle archive from GitHub release asset - `inst-download-archive`
5. [x] - `p1` - **IF** download fails (network error, 404, rate limit) - `inst-if-download-error`
   1. [x] - `p1` - **RETURN** error with HTTP status and retry suggestion - `inst-return-download-fail`
6. [x] - `p1` - Extract archive into `~/.cypilot/cache/` (overwrite previous) - `inst-extract-archive`
7. [x] - `p1` - Write version marker file `~/.cypilot/cache/.version` with downloaded version - `inst-write-version`
8. [x] - `p1` - **RETURN** path to cached skill bundle - `inst-return-cache-path-new`

### Create Config AGENTS.md

- [ ] `p1` - **ID**: `cpt-cypilot-algo-core-infra-create-config-agents`

**Input**: Install directory path, installed kits list

**Output**: Created `config/AGENTS.md`

**Steps**:
1. [ ] - `p1` - Generate default WHEN rules for standard system prompts (tech-stack, conventions, domain-model, patterns, project-structure, testing, build-deploy) - `inst-gen-when-rules`
2. [ ] - `p1` - Write `config/AGENTS.md` with navigation header and WHEN rules - `inst-write-config-agents`
3. [ ] - `p1` - **RETURN** path to created file - `inst-return-config-agents-path`


## 4. States (CDSL)

### Project Installation State

- [ ] `p1` - **ID**: `cpt-cypilot-state-core-infra-project-install`

**States**: UNINITIALIZED, INITIALIZED, STALE

**Initial State**: UNINITIALIZED

**Transitions**:
1. [ ] - `p1` - **FROM** UNINITIALIZED **TO** INITIALIZED **WHEN** `cypilot init` completes successfully - `inst-init-complete`
2. [ ] - `p1` - **FROM** INITIALIZED **TO** STALE **WHEN** cached skill version is newer than project skill version - `inst-version-mismatch`
3. [ ] - `p1` - **FROM** STALE **TO** INITIALIZED **WHEN** `cypilot update` completes successfully - `inst-update-complete`

## 5. Definitions of Done

### CLI Proxy Routes Commands

- [x] `p1` - **ID**: `cpt-cypilot-dod-core-infra-cli-routes`

The system **MUST** provide a global `cypilot` (and `cpt` alias) CLI entry point that resolves the skill target (project-installed or cached) and forwards all commands with their arguments, returning JSON output and appropriate exit codes.

**Implements**:
- `cpt-cypilot-flow-core-infra-cli-invocation`
- `cpt-cypilot-algo-core-infra-resolve-skill`
- `cpt-cypilot-algo-core-infra-route-command`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-installer`
- `cpt-cypilot-fr-core-skill-engine`
- `cpt-cypilot-nfr-adoption-usability`

**Covers (DESIGN)**:
- `cpt-cypilot-principle-determinism-first`
- `cpt-cypilot-principle-zero-harm`
- `cpt-cypilot-constraint-python-stdlib`
- `cpt-cypilot-constraint-cross-platform`
- `cpt-cypilot-component-cli-proxy`
- `cpt-cypilot-component-skill-engine`

### Global CLI Package

- [x] `p1` - **ID**: `cpt-cypilot-dod-core-infra-global-package`

The project **MUST** provide a Python package `cypilot` that acts as the global CLI proxy. The package **MUST** be installable via `pipx install git+https://github.com/{org}/cypilot.git` (or from PyPI when published). The package **MUST** contain only the thin proxy logic — skill resolution, cache management, command forwarding — with zero third-party dependencies (Python stdlib only). The package **MUST** register `cypilot` and `cpt` as console entry points. The package **MUST** work natively on Linux, Windows, and macOS.

**Implements**:
- `cpt-cypilot-flow-core-infra-cli-invocation`
- `cpt-cypilot-algo-core-infra-resolve-skill`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-installer`
- `cpt-cypilot-nfr-adoption-usability`

**Covers (DESIGN)**:
- `cpt-cypilot-constraint-python-stdlib`
- `cpt-cypilot-constraint-cross-platform`
- `cpt-cypilot-component-cli-proxy`

### Skill Cache Downloads from GitHub

- [x] `p1` - **ID**: `cpt-cypilot-dod-core-infra-skill-cache`

The system **MUST** provide a cache mechanism in the CLI proxy that downloads the skill bundle from a GitHub release into `~/.cypilot/cache/` on first invocation (or when cache is empty/stale). The download **MUST** be automatic and transparent — no separate manual step beyond `pipx install cypilot`. The proxy **MUST** report actionable errors on download failure.

**Implements**:
- `cpt-cypilot-algo-core-infra-cache-skill`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-installer`
- `cpt-cypilot-nfr-adoption-usability`

**Covers (DESIGN)**:
- `cpt-cypilot-component-cli-proxy`

### Init Creates Full Config

- [ ] `p1` - **ID**: `cpt-cypilot-dod-core-infra-init-config`

The system **MUST** provide a `cypilot init` command that defines the root system from the project directory name, creates `config/core.toml` with system and kit registrations, creates `config/artifacts.toml` with default SDLC autodetect rules, injects the root `AGENTS.md` managed block, and creates `config/AGENTS.md` with default WHEN rules.

**Implements**:
- `cpt-cypilot-flow-core-infra-project-init`
- `cpt-cypilot-algo-core-infra-define-root-system`
- `cpt-cypilot-algo-core-infra-create-config`
- `cpt-cypilot-algo-core-infra-inject-root-agents`
- `cpt-cypilot-algo-core-infra-create-config-agents`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-init`
- `cpt-cypilot-fr-core-config`
- `cpt-cypilot-nfr-adoption-usability`

**Covers (DESIGN)**:
- `cpt-cypilot-principle-tool-managed-config`
- `cpt-cypilot-principle-occams-razor`
- `cpt-cypilot-constraint-git-project-heuristics`
- `cpt-cypilot-component-config-manager`
- `cpt-cypilot-seq-init`

### Root AGENTS.md Integrity

- [x] `p1` - **ID**: `cpt-cypilot-dod-core-infra-agents-integrity`

The system **MUST** verify the root `AGENTS.md` managed block on every CLI invocation (not just init). If the `<!-- @cpt:root-agents -->` block is missing, stale, or the file does not exist, the system silently re-injects it with the correct path to `config/AGENTS.md`.

**Implements**:
- `cpt-cypilot-algo-core-infra-inject-root-agents`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-init`

**Covers (DESIGN)**:
- `cpt-cypilot-principle-zero-harm`
- `cpt-cypilot-component-skill-engine`

## 6. Acceptance Criteria

- [ ] `cypilot init` creates `config/core.toml` and `config/artifacts.toml` with correct root system definition
- [ ] `cypilot init` in an already-initialized project returns exit code 2 with helpful message
- [x] `cypilot <command>` from inside a project routes to project skill; from outside routes to cache
- [x] First `cypilot` invocation after `pipx install` with empty cache automatically downloads skill from GitHub
- [x] `cypilot --update-cache [VERSION|BRANCH]` downloads specified version/branch/SHA into cache
- [x] Download failure produces actionable error message with HTTP status
- [ ] All commands output JSON to stdout and use exit codes 0/1/2
- [x] Root `AGENTS.md` managed block is verified and re-injected on every CLI invocation
- [x] Background version check does not block command execution
- [ ] `config/AGENTS.md` is created with default WHEN rules for standard system prompts
