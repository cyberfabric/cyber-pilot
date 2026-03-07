# Feature: Kit Management

<!-- toc -->

- [1. Feature Context](#1-feature-context)
  - [1. Overview](#1-overview)
  - [2. Purpose](#2-purpose)
  - [3. Actors](#3-actors)
  - [4. References](#4-references)
- [2. Actor Flows (CDSL)](#2-actor-flows-cdsl)
  - [Kit Install CLI](#kit-install-cli)
  - [Kit Update CLI](#kit-update-cli)
  - [Kit Validate CLI](#kit-validate-cli)
  - [Kit CLI Dispatcher](#kit-cli-dispatcher)
- [3. Processes / Business Logic (CDSL)](#3-processes-business-logic-cdsl)
  - [Kit Content Management](#kit-content-management)
  - [Gen Aggregation](#gen-aggregation)
  - [Kit Installation](#kit-installation)
  - [Kit Update](#kit-update)
  - [File-Level Kit Update](#file-level-kit-update)
  - [Kit File Enumeration](#kit-file-enumeration)
  - [Kit File Classification](#kit-file-classification)
  - [Kit Interactive Review](#kit-interactive-review)
  - [Kit Diff Display](#kit-diff-display)
  - [Kit Conflict Merge](#kit-conflict-merge)
  - [Kit TOC Handling](#kit-toc-handling)
  - [Kit Snapshot](#kit-snapshot)
  - [Kit Validation Engine](#kit-validation-engine)
  - [Kit Validate by Path](#kit-validate-by-path)
  - [Kit Config Helpers](#kit-config-helpers)
- [4. States (CDSL)](#4-states-cdsl)
  - [Kit Installation State](#kit-installation-state)
- [5. Definitions of Done](#5-definitions-of-done)
  - [Kit Install Copies Files](#kit-install-copies-files)
  - [Kit Update Shows Diffs](#kit-update-shows-diffs)
  - [Kit Validate Checks Integrity](#kit-validate-checks-integrity)
- [6. Implementation Modules](#6-implementation-modules)
- [7. Acceptance Criteria](#7-acceptance-criteria)

<!-- /toc -->

- [x] `p1` - **ID**: `cpt-cypilot-featstatus-kit-management`

## 1. Feature Context

- [x] `p1` - `cpt-cypilot-featstatus-kit-management`

### 1. Overview

Manage kit lifecycle — installation, file-level diff updates, interactive conflict resolution, SKILL/AGENTS composition, and kit structural validation. Kits are direct file packages (per `cpt-cypilot-adr-remove-blueprint-system`).

### 2. Purpose

Enables users to install, update, and validate kit packages with interactive file-level diffs, automatic `.gen/` aggregation, and structural validation. Kits are direct file packages stored in `config/kits/{slug}/` — no blueprint processing, no three-way merge, no hash detection.

### 3. Actors

| Actor | Role in Feature |
|-------|-----------------|
| `cpt-cypilot-actor-user` | Runs `cpt kit install`, `cpt kit update`, `cpt validate-kits` |
| `cpt-cypilot-actor-cypilot-cli` | Dispatches kit subcommands to skill engine |

### 4. References

- **PRD**: `cpt-cypilot-fr-core-kits`, `cpt-cypilot-fr-core-resource-diff`
- **Design**: `cpt-cypilot-component-kit-manager`, `cpt-cypilot-component-validator`
- **ADR**: `cpt-cypilot-adr-remove-blueprint-system`

---

## 2. Actor Flows (CDSL)

### Kit Install CLI

- [x] `p1` - **ID**: `cpt-cypilot-flow-kit-install-cli`

**Actor**: `cpt-cypilot-actor-user`

**Trigger**: User runs `cpt kit install <path> [--force] [--dry-run]`

**Steps**:
1. [x] - `p1` - Parse CLI arguments (path, --force, --dry-run) - `inst-parse-args`
2. [x] - `p1` - Validate kit source directory exists - `inst-validate-source`
3. [x] - `p1` - Read slug and version from source conf.toml - `inst-read-slug-version`
4. [x] - `p1` - Resolve project root and cypilot directory via `_resolve_cypilot_dir` - `inst-resolve-project`
5. [x] - `p1` - Check if kit already installed; fail if exists without --force - `inst-check-existing`
6. [x] - `p1` - **IF** --dry-run: return preview and STOP - `inst-dry-run`
7. [x] - `p1` - Delegate to `install_kit()` for actual installation - `inst-delegate-install`
8. [x] - `p1` - Regenerate `.gen/` aggregates via `regenerate_gen_aggregates` - `inst-regen-gen`
9. [x] - `p1` - Format and output result JSON - `inst-output-result`

### Kit Update CLI

- [x] `p1` - **ID**: `cpt-cypilot-flow-kit-update-cli`

**Actor**: `cpt-cypilot-actor-user`

**Trigger**: User runs `cpt kit update <path> [--force] [--dry-run] [--no-interactive] [-y]`

**Steps**:
1. [x] - `p1` - Parse CLI arguments (path, --force, --dry-run, --no-interactive, -y) - `inst-parse-args`
2. [x] - `p1` - Validate kit source directory exists - `inst-validate-source`
3. [x] - `p1` - Read slug from source conf.toml - `inst-read-slug`
4. [x] - `p1` - Resolve project root and cypilot directory - `inst-resolve-project`
5. [x] - `p1` - Delegate to `update_kit()` with interactive/auto_approve/force flags - `inst-delegate-update`
6. [x] - `p1` - Regenerate `.gen/` aggregates (unless dry-run) - `inst-regen-gen`
7. [x] - `p1` - Format version status, accepted/declined files, and output result - `inst-format-output`

### Kit Validate CLI

- [x] `p1` - **ID**: `cpt-cypilot-flow-kit-validate-cli`

**Actor**: `cpt-cypilot-actor-user`

**Trigger**: User runs `cpt validate-kits [path] [--kit ID] [--verbose]`

**Steps**:
1. [x] - `p1` - Parse CLI arguments (optional path, --kit, --verbose) - `inst-parse-args`
2. [x] - `p1` - **IF** path provided: validate standalone kit via `_validate_kit_by_path` - `inst-path-mode`
3. [x] - `p1` - **ELSE**: get context and run `run_validate_kits` for registered kits - `inst-registered-mode`
4. [x] - `p1` - Output result JSON with human formatter - `inst-output-result`

**Supporting**:
- [x] - `p1` - Imports and module setup for validate-kits command - `inst-validate-kits-imports`
- [x] - `p1` - Human-friendly formatter and error display helpers for validate-kits output - `inst-validate-kits-format`

### Kit CLI Dispatcher

- [x] `p1` - **ID**: `cpt-cypilot-flow-kit-dispatch`

**Actor**: `cpt-cypilot-actor-cypilot-cli`

**Trigger**: User runs `cpt kit <subcommand>`

**Steps**:
1. [x] - `p1` - Parse subcommand (install | update | migrate) - `inst-parse-subcmd`
2. [x] - `p1` - Route to appropriate handler; error on unknown subcommand - `inst-route`

---

## 3. Processes / Business Logic (CDSL)

### Kit Content Management

- [x] `p1` - **ID**: `cpt-cypilot-algo-kit-content-mgmt`

**Input**: Kit source directory, target config directory

**Output**: Copied kit files, seeded config files, collected metadata

**Steps**:
1. [x] - `p1` - Seed config files: copy `.toml` files from kit scripts/ to config/ (only if missing) - `inst-seed-configs`
2. [x] - `p1` - Copy kit content: iterate `_KIT_CONTENT_DIRS` and `_KIT_CONTENT_FILES`, copy from source to config/kits/{slug}/ - `inst-copy-content`
3. [x] - `p1` - Collect kit metadata: read SKILL.md for navigation line, AGENTS.md for content aggregation - `inst-collect-metadata`

### Gen Aggregation

- [x] `p1` - **ID**: `cpt-cypilot-algo-kit-regen-gen`

**Input**: Cypilot adapter directory

**Output**: Updated `.gen/AGENTS.md`, `.gen/SKILL.md`, `.gen/README.md`

**Steps**:
1. [x] - `p1` - Scan `config/kits/*/` for all installed kit directories - `inst-scan-kits`
2. [x] - `p1` - Collect metadata (skill_nav, agents_content) from each kit - `inst-collect-all-metadata`
3. [x] - `p1` - Read project name from `config/core.toml [system].name` - `inst-read-project-name`
4. [x] - `p1` - Compose and write `.gen/AGENTS.md` with navigation rules and kit agent content - `inst-write-gen-agents`
5. [x] - `p1` - Compose and write `.gen/SKILL.md` with per-kit skill navigation pointers - `inst-write-gen-skill`
6. [x] - `p1` - Write `.gen/README.md` using `_gen_readme()` - `inst-write-gen-readme`

### Kit Installation

- [x] `p1` - **ID**: `cpt-cypilot-algo-kit-install`

**Input**: Kit source path, cypilot dir, slug, version

**Output**: Result dict with status, files_copied, actions, metadata

**Steps**:
1. [x] - `p1` - Validate kit source directory exists - `inst-validate-source`
2. [x] - `p1` - Copy kit content to `config/kits/{slug}/` via `_copy_kit_content` - `inst-copy-content`
3. [x] - `p1` - Read version from source `conf.toml` if not provided - `inst-read-version`
4. [x] - `p1` - Seed config files from kit's scripts/ directory - `inst-seed-configs`
5. [x] - `p1` - Register kit in `core.toml` with path and version - `inst-register-core`
6. [x] - `p1` - Collect metadata for `.gen/` aggregation - `inst-collect-meta`
7. [x] - `p1` - **RETURN** result with status, files_copied, actions, skill_nav, agents_content - `inst-return-result`

### Kit Update

- [x] `p1` - **ID**: `cpt-cypilot-algo-kit-update`

**Input**: Kit slug, source dir, cypilot dir, flags (dry_run, interactive, auto_approve, force)

**Output**: Result dict with kit, version status, gen actions, accepted/declined files

**Steps**:
1. [x] - `p1` - Resolve config dir paths (config_dir, config_kits_dir, config_kit_dir) - `inst-resolve-config`
2. [x] - `p1` - **IF** dry_run: return early with dry_run status - `inst-dry-run-check`
3. [x] - `p1` - Read source version from `conf.toml` - `inst-read-source-version`
4. [x] - `p1` - **IF** not force and version matches installed: return "current" status with metadata - `inst-version-check`
5. [x] - `p1` - **IF** config/kits/{slug}/ does not exist: first-install via `_copy_kit_content`, seed configs, register in core.toml - `inst-first-install`
6. [x] - `p1` - **ELSE**: existing kit — delegate to `file_level_kit_update` for interactive diff - `inst-file-level-diff`
7. [x] - `p1` - Update version in `core.toml` from source version - `inst-update-core-toml`
8. [x] - `p1` - Collect metadata for `.gen/` aggregation - `inst-collect-metadata`
9. [x] - `p1` - **RETURN** result with kit, version, gen, accepted/declined files - `inst-return-result`

### File-Level Kit Update

- [x] `p1` - **ID**: `cpt-cypilot-algo-kit-file-update`

**Input**: Source dir, user dir, flags (interactive, auto_approve, force, dry_run, content_dirs, content_files)

**Output**: Dict with status, added/removed/modified/unchanged, accepted/declined paths

**Steps**:
1. [x] - `p1` - Enumerate source and user kit files via `_enumerate_kit_files` - `inst-enumerate-files`
2. [x] - `p1` - Strip TOC from both sides for cleaner diff comparison, record `toc_formats` per file - `inst-strip-toc`
3. [x] - `p1` - Classify changes between source and user via `_classify_kit_files` - `inst-classify-changes`
4. [x] - `p1` - **IF** no changes: return "current" status early - `inst-check-no-changes`
5. [x] - `p1` - Show update summary with colored counts (added/removed/modified/unchanged) - `inst-show-summary`
6. [x] - `p1` - **FOR EACH** changed file: display context (new file, deleted, or unified diff) - `inst-show-change-context`
7. [x] - `p1` - **FOR EACH** changed file: get user decision via `_prompt_kit_file` or auto-accept/decline per flags - `inst-prompt-decision`
8. [x] - `p1` - **IF** decision is "modify": open editor for manual merge via `_open_editor_for_file` - `inst-editor-merge`
9. [x] - `p1` - Apply accepted changes: write new/modified files, delete removed files - `inst-apply-changes`
10. [x] - `p1` - **IF** file had TOC and was written: prompt/auto-regenerate TOC, handle errors with rollback - `inst-toc-regen`
11. [x] - `p1` - **RETURN** result with all entries, accepted/declined paths - `inst-build-result`

**Supporting**:
- [x] - `p1` - Result list initialization and changed file aggregation helpers - `inst-update-datamodel`

### Kit File Enumeration

- [x] `p1` - **ID**: `cpt-cypilot-algo-kit-file-enumerate`

**Input**: Directory path, include/exclude filters

**Output**: Dict of `{relative_posix_path: content_bytes}`

**Steps**:
1. [x] - `p1` - Walk directory recursively, collecting files matching include filters or excluding by exclude filters - `inst-walk-dir`
2. [x] - `p1` - **IF** `content_dirs`/`content_files` provided: include-only mode (top-level dir in content_dirs or root file in content_files) - `inst-include-filter`
3. [x] - `p1` - **ELSE**: exclude mode (skip files in `_KIT_EXCLUDE_FILES`, dirs in `_KIT_EXCLUDE_DIRS`) - `inst-exclude-filter`
4. [x] - `p1` - Read file bytes and store in result dict - `inst-read-bytes`

**Supporting**:
- [x] - `p1` - Kit exclude/include constants and default content filters - `inst-enum-datamodel`

### Kit File Classification

- [x] `p1` - **ID**: `cpt-cypilot-algo-kit-file-classify`

**Input**: Source files dict, user files dict

**Output**: DiffReport with added/removed/modified/unchanged

**Steps**:
1. [x] - `p1` - Union all paths from source and user, classify each as added/removed/modified/unchanged by content comparison - `inst-classify`

### Kit Interactive Review

- [x] `p1` - **ID**: `cpt-cypilot-algo-kit-interactive-review`

**Input**: Relative path, review state dict

**Output**: User decision: accept/decline/modify

**Steps**:
1. [x] - `p1` - **IF** `accept_all` or `decline_all` set in state: return immediately - `inst-check-bulk`
2. [x] - `p1` - Prompt user with `[a]ccept [d]ecline [A]ccept-all [D]ecline-all [m]odify`, parse response, update state flags for bulk decisions, return choice - `inst-prompt`

### Kit Diff Display

- [x] `p1` - **ID**: `cpt-cypilot-algo-kit-diff-display`

**Input**: DiffReport or file content pair

**Output**: Colored text to stderr

**Steps**:
1. [x] - `p1` - Show summary: colored counts of added (green +), removed (red -), modified (yellow ~) files - `inst-show-summary`
2. [x] - `p1` - Show per-file unified diff: decode bytes, compute `difflib.unified_diff`, color-code output lines - `inst-show-file-diff`

**Supporting**:
- [x] - `p1` - Imports, DiffReport dataclass, and editor/conflict marker constants - `inst-diff-datamodel`

### Kit Conflict Merge

- [x] `p1` - **ID**: `cpt-cypilot-algo-kit-conflict-merge`

**Input**: Old content bytes, new content bytes, relative path

**Output**: Resolved content bytes or None (decline)

**Steps**:
1. [x] - `p1` - Detect conflict markers: scan lines for `<<<<<<<`, `=======`, `>>>>>>>` - `inst-detect-markers`
2. [x] - `p1` - Build conflict content: use `SequenceMatcher` to produce git-style `<<<<<<<`/`=======`/`>>>>>>>` regions for each differing hunk - `inst-build-conflicts`
3. [x] - `p1` - Open editor: write conflict content to temp file, invoke `$VISUAL`/`$EDITOR`/`vi`, read result; if empty return None - `inst-open-editor`
4. [x] - `p1` - **IF** conflict markers remain: prompt retry/accept-upstream/decline - `inst-prompt-unresolved`
5. [x] - `p1` - Loop: retry reopens editor, accept returns upstream, decline returns None - `inst-resolve-loop`

**Supporting**:
- [x] - `p1` - Editor detection helper function - `inst-merge-datamodel`

### Kit TOC Handling

- [x] `p1` - **ID**: `cpt-cypilot-algo-kit-toc-handling`

**Input**: File content bytes

**Output**: TOC-stripped content for diff, regenerated content post-write

**Steps**:
1. [x] - `p1` - Strip marker-based TOC (`<!-- toc -->` / `<!-- /toc -->`) or heading-based TOC (`## Table of Contents`) from content - `inst-strip-toc`
2. [x] - `p1` - Prompt user about TOC regeneration (or auto-regen if auto_approve) - `inst-prompt-regen`
3. [x] - `p1` - Regenerate TOC using `insert_toc_markers` or `insert_toc_heading` based on detected format - `inst-regenerate`
4. [x] - `p1` - **IF** regeneration fails: restore previous content, prompt continue/stop - `inst-handle-error`

**Supporting**:
- [x] - `p1` - TOC marker constants and heading regex patterns - `inst-toc-datamodel`

### Kit Snapshot

- [x] `p1` - **ID**: `cpt-cypilot-algo-kit-snapshot`

**Input**: Directory path, file extensions filter

**Output**: Snapshot dict `{rel_path: bytes}`, DiffReport

**Steps**:
1. [x] - `p1` - Recursively read all files matching extensions into `{relative_path: bytes}` dict - `inst-read-files`

### Kit Validation Engine

- [x] `p1` - **ID**: `cpt-cypilot-algo-kit-validate`

**Input**: Project root, adapter dir, optional kit filter, verbose flag

**Output**: (return_code, report_dict) — rc=0 PASS, rc=2 FAIL

**Steps**:
1. [x] - `p1` - Get context and initialize validation state - `inst-init-context`
2. [x] - `p1` - **Phase 1 — Structural**: for each registered Cypilot-format kit, load and validate `constraints.toml` - `inst-structural-check`
3. [x] - `p1` - **Phase 2 — Templates**: load `artifacts_meta`, run `self_check` for template/example consistency - `inst-template-check`
4. [x] - `p1` - Build result: aggregate errors, set overall PASS/FAIL status - `inst-build-result`

### Kit Validate by Path

- [x] `p1` - **ID**: `cpt-cypilot-algo-kit-validate-by-path`

**Input**: Kit directory path, verbose flag

**Output**: (return_code, report_dict)

**Steps**:
1. [x] - `p1` - Resolve kit directory, verify exists - `inst-resolve-dir`
2. [x] - `p1` - **Phase 1 — Structural**: load and validate `constraints.toml` - `inst-structural-check`
3. [x] - `p1` - Build synthetic `ArtifactsMeta` from kit's artifacts/ directory - `inst-build-artifacts-meta`
4. [x] - `p1` - **Phase 2 — Templates**: run `self_check` for template/example validation - `inst-template-check`
5. [x] - `p1` - Build result: aggregate errors, set PASS/FAIL - `inst-build-result`

### Kit Config Helpers

- [x] `p1` - **ID**: `cpt-cypilot-algo-kit-config-helpers`

**Input**: Various conf.toml / core.toml paths

**Output**: Parsed config values

**Steps**:
1. [x] - `p1` - Read top-level `version` from conf.toml as integer - `inst-read-conf-version`
2. [x] - `p1` - Read kit `slug` from source conf.toml - `inst-read-slug`
3. [x] - `p1` - Read installed kit version from `core.toml [kits.{slug}].version` - `inst-read-version-from-core`
4. [x] - `p1` - Read kit version string from conf.toml path - `inst-read-kit-version`
5. [x] - `p1` - Register or update kit entry in `core.toml` with format, path, and version - `inst-register-core`

---

## 4. States (CDSL)

### Kit Installation State

- [x] `p1` - **ID**: `cpt-cypilot-state-kit-installation`

| State | Condition | Transitions |
|-------|-----------|-------------|
| `not_installed` | `config/kits/{slug}/` does not exist | → `installed` via `install_kit` |
| `installed` | Kit files present in `config/kits/{slug}/` | → `updated` via `update_kit`, → `current` if version matches |
| `current` | Installed version matches source version | → `updated` via force update |
| `updated` | Files changed via file-level diff | → `current` on next check |

---

## 5. Definitions of Done

### Kit Install Copies Files

- [x] `p1` - **ID**: `cpt-cypilot-dod-kit-install`

1. [x] - `p1` - `install_kit` copies all `_KIT_CONTENT_DIRS` and `_KIT_CONTENT_FILES` from source to `config/kits/{slug}/`
2. [x] - `p1` - Kit is registered in `core.toml` with correct path and version
3. [x] - `p1` - `.gen/` aggregates are updated after install

### Kit Update Shows Diffs

- [x] `p1` - **ID**: `cpt-cypilot-dod-kit-update`

1. [x] - `p1` - `file_level_kit_update` enumerates and classifies files correctly
2. [x] - `p1` - Interactive mode shows colored unified diffs per changed file
3. [x] - `p1` - User can accept/decline/modify per file, or bulk accept/decline all
4. [x] - `p1` - TOC sections are stripped for diff comparison and regenerated post-write
5. [x] - `p1` - Editor merge uses git-style conflict markers

### Kit Validate Checks Integrity

- [x] `p1` - **ID**: `cpt-cypilot-dod-kit-validate`

1. [x] - `p1` - `constraints.toml` is parsed and validated per kit
2. [x] - `p1` - Templates and examples are checked against constraints via `self_check`
3. [x] - `p1` - Both registered and standalone (by-path) kits can be validated

---

## 6. Implementation Modules

| Module | Algorithms Implemented |
|--------|----------------------|
| `skills/cypilot/scripts/cypilot/commands/kit.py` | `cpt-cypilot-algo-kit-content-mgmt`, `cpt-cypilot-algo-kit-regen-gen`, `cpt-cypilot-algo-kit-install`, `cpt-cypilot-algo-kit-update`, `cpt-cypilot-algo-kit-config-helpers`, `cpt-cypilot-flow-kit-install-cli`, `cpt-cypilot-flow-kit-update-cli`, `cpt-cypilot-flow-kit-dispatch` |
| `skills/cypilot/scripts/cypilot/utils/diff_engine.py` | `cpt-cypilot-algo-kit-file-update`, `cpt-cypilot-algo-kit-file-enumerate`, `cpt-cypilot-algo-kit-file-classify`, `cpt-cypilot-algo-kit-interactive-review`, `cpt-cypilot-algo-kit-diff-display`, `cpt-cypilot-algo-kit-conflict-merge`, `cpt-cypilot-algo-kit-toc-handling`, `cpt-cypilot-algo-kit-snapshot` |
| `skills/cypilot/scripts/cypilot/commands/validate_kits.py` | `cpt-cypilot-algo-kit-validate`, `cpt-cypilot-algo-kit-validate-by-path`, `cpt-cypilot-flow-kit-validate-cli` |

---

## 7. Acceptance Criteria

- [ ] `p1` - `cpt kit install <path>` installs a kit and returns JSON with status, files_copied
- [ ] `p1` - `cpt kit update <path>` shows interactive diff and applies accepted changes
- [ ] `p1` - `cpt validate-kits` validates all registered kits (constraints + templates)
- [ ] `p1` - `.gen/AGENTS.md` and `.gen/SKILL.md` are regenerated after install/update
- [ ] `p1` - File-level diff correctly handles TOC stripping, conflict merging, and editor integration
- [ ] `p1` - All CDSL instructions have corresponding `@cpt-begin`/`@cpt-end` markers in code
