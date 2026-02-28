# Feature: V2 → V3 Migration


<!-- toc -->

- [1. Feature Context](#1-feature-context)
  - [1.1 Overview](#11-overview)
  - [1.2 Purpose](#12-purpose)
  - [1.3 Actors](#13-actors)
  - [1.4 References](#14-references)
- [2. Actor Flows (CDSL)](#2-actor-flows-cdsl)
  - [Migrate V2 Project](#migrate-v2-project)
  - [Migrate Config Format (JSON → TOML)](#migrate-config-format-json-toml)
- [3. Processes / Business Logic (CDSL)](#3-processes-business-logic-cdsl)
  - [Detect V2 Installation](#detect-v2-installation)
  - [Backup V2 State](#backup-v2-state)
  - [Detect Core Install Type](#detect-core-install-type)
  - [Clean Up V2 Core Path](#clean-up-v2-core-path)
  - [Convert Artifacts Registry](#convert-artifacts-registry)
  - [Migrate Kits](#migrate-kits)
  - [Convert Adapter AGENTS.md](#convert-adapter-agentsmd)
  - [Generate core.toml](#generate-coretoml)
  - [Inject Root AGENTS.md Managed Block](#inject-root-agentsmd-managed-block)
  - [Validate Migration Completeness](#validate-migration-completeness)
- [4. States (CDSL)](#4-states-cdsl)
  - [Migration State Machine](#migration-state-machine)
- [5. Definitions of Done](#5-definitions-of-done)
  - [V2 Detection](#v2-detection)
  - [V2 Core Path Cleanup](#v2-core-path-cleanup)
  - [Artifacts Registry Conversion](#artifacts-registry-conversion)
  - [Adapter AGENTS.md Conversion](#adapter-agentsmd-conversion)
  - [Core Config Generation](#core-config-generation)
  - [Root AGENTS.md Injection](#root-agentsmd-injection)
  - [Kit Installation and Regeneration](#kit-installation-and-regeneration)
  - [Agent Entry Points Regeneration](#agent-entry-points-regeneration)
  - [Backup and Rollback](#backup-and-rollback)
  - [Migration Validation](#migration-validation)
  - [JSON → TOML Config Migration](#json-toml-config-migration)
- [6. Acceptance Criteria](#6-acceptance-criteria)
- [7. Additional Context](#7-additional-context)
  - [Non-Applicable Domains](#non-applicable-domains)
  - [Maintainability Notes](#maintainability-notes)
  - [Testing Approach](#testing-approach)

<!-- /toc -->

- [ ] `p1` - **ID**: `cpt-cypilot-featstatus-v2-v3-migration`
## 1. Feature Context

- [ ] `p2` - `cpt-cypilot-feature-v2-v3-migration`

### 1.1 Overview

Migrate existing Cypilot v2 projects (adapter-based, `artifacts.json`, legacy kit structure) to v3 (blueprint-based, `artifacts.toml`, global CLI installer, `config/` directory) with zero data loss. The migration handles complex real-world projects with multiple systems, nested autodetect rules, custom WHEN rules, and legacy JSON config files.

Problem: V2 projects use `.cypilot-adapter/` with JSON configs and a flat kit structure that is incompatible with the v3 three-directory layout (`.core/`, `.gen/`, `config/`). Additionally, the v2 core directory (`.cypilot/`) may be installed in three different ways — as a git submodule, a git clone, or a plain directory — each requiring different cleanup strategies.
Primary value: Enables existing v2 users to adopt v3 without manual restructuring or data loss.
Key assumptions: V2 project has a valid `.cypilot-adapter/` directory with `artifacts.json` and optionally `AGENTS.md`. The core path may be any of the three install types.

### 1.2 Purpose

This feature addresses the need for a seamless upgrade path from Cypilot v2 to v3. It implements the migration strategy defined in the Overall Design (Section 4, "Migration Strategy") and satisfies the project initialization and config directory requirements for existing v2 installations.

- `cpt-cypilot-fr-core-init` — `cypilot init` must detect existing v2 installations and offer migration
- `cpt-cypilot-fr-core-config` — config directory must be created with proper TOML format and schema versioning
- `cpt-cypilot-principle-zero-harm` — migration must not impose costs; rollback must restore original state
- `cpt-cypilot-principle-no-manual-maintenance` — migration runs automatically; no manual file editing required

### 1.3 Actors

| Actor | Role in Feature |
|-------|-----------------|
| `cpt-cypilot-actor-user` | Initiates migration via `cypilot migrate` or `cypilot init` in a v2 project |
| `cpt-cypilot-actor-cypilot-cli` | Executes migration commands, validates results, reports status |

### 1.4 References

- **PRD**: [PRD.md](../PRD.md)
- **Design**: [DESIGN.md](../DESIGN.md)
- **Dependencies**: `cpt-cypilot-feature-core-infra`, `cpt-cypilot-feature-blueprint-system`, `cpt-cypilot-feature-traceability-validation`
- **Use Case**: `cpt-cypilot-usecase-migrate` (UC-012)

## 2. Actor Flows (CDSL)

### Migrate V2 Project

- [ ] `p1` - **ID**: `cpt-cypilot-flow-v2-v3-migration-migrate-project`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- V2 project fully migrated to v3 structure with all artifacts, IDs, and config preserved
- Agent entry points regenerated for v3
- Root `AGENTS.md` updated with managed block

**Error Scenarios**:
- V2 detection fails (no `.cypilot-adapter/` found) — abort with guidance
- `artifacts.json` parse failure — abort, suggest manual inspection
- Config validation fails after conversion — rollback to backup, report errors
- Partial migration failure — rollback to backup, report which step failed
- Submodule deinit fails (dirty worktree, missing git) — abort with guidance, backup preserved
- Git clone removal fails (permissions) — abort, suggest manual cleanup

**Steps**:
1. [ ] - `p1` - User runs `cypilot migrate` or `cypilot init` in a project containing `.cypilot-adapter/` — `inst-user-trigger`
2. [ ] - `p1` - Detect v2 installation using `cpt-cypilot-algo-v2-v3-migration-detect-v2` — `inst-detect-v2`
3. [ ] - `p1` - **IF** v2 not detected — `inst-check-v2-found`
   1. [ ] - `p1` - **RETURN** error "No v2 installation found. Use `cypilot init` for new projects." — `inst-return-no-v2`
4. [ ] - `p1` - Display migration plan summary to user (source paths, target paths, systems found, kits found, core install type: submodule/clone/plain) — `inst-show-plan`
5. [ ] - `p1` - **IF** user declines migration — `inst-check-user-confirm`
   1. [ ] - `p1` - **RETURN** "Migration cancelled by user." — `inst-return-cancelled`
6. [ ] - `p1` - Create backup using `cpt-cypilot-algo-v2-v3-migration-backup-v2-state` — `inst-create-backup`
7. [ ] - `p1` - Clean up v2 core path using `cpt-cypilot-algo-v2-v3-migration-cleanup-core-path` (handles submodule/clone/plain) — `inst-cleanup-core`
8. [ ] - `p1` - Convert artifacts registry using `cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry` — `inst-convert-artifacts`
9. [ ] - `p1` - Convert adapter AGENTS.md using `cpt-cypilot-algo-v2-v3-migration-convert-agents-md` — `inst-convert-agents`
10. [ ] - `p1` - Generate core.toml using `cpt-cypilot-algo-v2-v3-migration-generate-core-toml` — `inst-generate-core-toml`
11. [ ] - `p1` - Migrate kits using `cpt-cypilot-algo-v2-v3-migration-migrate-kits` (vanilla SDLC from cache, custom kits copied as-is) — `inst-migrate-kits`
12. [ ] - `p1` - Inject root AGENTS.md managed block using `cpt-cypilot-algo-v2-v3-migration-inject-root-agents` — `inst-inject-root-agents`
13. [ ] - `p1` - Regenerate agent entry points for all supported agents — `inst-regen-agent-entries`
14. [ ] - `p1` - Validate migration using `cpt-cypilot-algo-v2-v3-migration-validate-migration` — `inst-validate-migration`
15. [ ] - `p1` - **IF** validation fails — `inst-check-validation`
    1. [ ] - `p1` - Rollback using backup — `inst-rollback-on-fail`
    2. [ ] - `p1` - **RETURN** error with validation details and rollback confirmation — `inst-return-validation-fail`
16. [ ] - `p1` - **RETURN** migration success summary (systems migrated, artifacts preserved, config files created, core_install_type cleaned) — `inst-return-success`

### Migrate Config Format (JSON → TOML)

- [ ] `p1` - **ID**: `cpt-cypilot-flow-v2-v3-migration-migrate-config`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- All JSON config files converted to TOML with schema validation
- Original JSON files removed after successful conversion

**Error Scenarios**:
- JSON parse failure — skip file, report error, continue with remaining files
- TOML schema validation failure — keep JSON, report error, skip that file

**Steps**:
1. [ ] - `p1` - User runs `cypilot migrate-config` — `inst-user-trigger-config`
2. [ ] - `p1` - Scan for existing `.json` config files in `config/` and `.cypilot-adapter/` — `inst-scan-json-files`
3. [ ] - `p1` - **FOR EACH** JSON config file found — `inst-iterate-json-files`
   1. [ ] - `p1` - Parse JSON content — `inst-parse-json`
   2. [ ] - `p1` - **TRY** — `inst-try-convert`
      1. [ ] - `p1` - Serialize as TOML — `inst-serialize-toml`
      2. [ ] - `p1` - Validate TOML against schema — `inst-validate-toml-schema`
      3. [ ] - `p1` - Write `.toml` file — `inst-write-toml`
      4. [ ] - `p1` - Remove original `.json` file — `inst-remove-json`
   3. [ ] - `p1` - **CATCH** parse or validation error — `inst-catch-convert-error`
      1. [ ] - `p1` - Keep `.json` file, log error with file path and reason — `inst-log-convert-error`
4. [ ] - `p1` - **RETURN** conversion summary (converted count, skipped count, error details) — `inst-return-config-summary`

## 3. Processes / Business Logic (CDSL)

### Detect V2 Installation

- [ ] `p1` - **ID**: `cpt-cypilot-algo-v2-v3-migration-detect-v2`

**Input**: Project root path

**Output**: V2 detection result (detected: bool, adapter_path, config_path, core_path, core_install_type: SUBMODULE | GIT_CLONE | PLAIN_DIR | ABSENT, systems, kits)

**Steps**:
1. [ ] - `p1` - Check for `.cypilot-adapter/` directory at project root — `inst-check-adapter-dir`
2. [ ] - `p1` - **IF** `.cypilot-adapter/` not found — `inst-adapter-not-found`
   1. [ ] - `p1` - Check for `.cypilot-config.json` as fallback indicator — `inst-check-config-json`
   2. [ ] - `p1` - **IF** neither found **RETURN** {detected: false} — `inst-return-not-detected`
3. [ ] - `p1` - Parse `.cypilot-config.json` if present — extract `cypilotCorePath`, `cypilotAdapterPath` — `inst-parse-config-json`
4. [ ] - `p1` - **IF** `.cypilot-config.json` not present, use defaults: core=`.cypilot`, adapter=`.cypilot-adapter` — `inst-use-defaults`
5. [ ] - `p1` - Check for `artifacts.json` inside adapter path — `inst-check-artifacts-json`
6. [ ] - `p1` - **IF** `artifacts.json` found, parse and extract: version, systems[], kits{}, ignore[] — `inst-parse-artifacts-json`
7. [ ] - `p1` - Check for `AGENTS.md` inside adapter path — `inst-check-adapter-agents`
8. [ ] - `p1` - Check for kit directories inside adapter `kits/` — `inst-check-adapter-kits`
9. [ ] - `p1` - Determine core path install type using `cpt-cypilot-algo-v2-v3-migration-detect-core-install-type` — `inst-detect-core-type`
10. [ ] - `p1` - **RETURN** {detected: true, adapter_path, config_path, core_path, core_install_type, systems, kits, has_agents_md, has_config_json} — `inst-return-detected`

### Backup V2 State

- [ ] `p1` - **ID**: `cpt-cypilot-algo-v2-v3-migration-backup-v2-state`

**Input**: Project root path, adapter_path, core_path

**Output**: Backup path (string)

**Steps**:
1. [ ] - `p1` - Generate timestamped backup directory name: `.cypilot-v2-backup-{YYYYMMDD-HHMMSS}` — `inst-gen-backup-name`
2. [ ] - `p1` - Copy `.cypilot-adapter/` to backup directory — `inst-backup-adapter`
3. [ ] - `p1` - **IF** `.cypilot-config.json` exists, copy to backup — `inst-backup-config-json`
4. [ ] - `p1` - **IF** core path (`.cypilot/`) exists, copy to backup — `inst-backup-core`
5. [ ] - `p1` - **IF** core_install_type == SUBMODULE, copy `.gitmodules` to backup — `inst-backup-gitmodules`
6. [ ] - `p1` - **IF** root `AGENTS.md` exists, copy to backup — `inst-backup-root-agents`
7. [ ] - `p1` - **IF** agent entry point directories (`.windsurf/`, `.cursor/`, `.claude/`, `.github/`) exist, copy to backup — `inst-backup-agent-dirs`
8. [ ] - `p1` - Write backup manifest (list of backed-up paths, timestamps, v2 version info, core_install_type) — `inst-write-manifest`
9. [ ] - `p1` - **RETURN** backup_path — `inst-return-backup-path`

### Detect Core Install Type

- [ ] `p1` - **ID**: `cpt-cypilot-algo-v2-v3-migration-detect-core-install-type`

**Input**: core_path (e.g., `.cypilot/`)

**Output**: core_install_type: SUBMODULE | GIT_CLONE | PLAIN_DIR | ABSENT

**Steps**:
1. [ ] - `p1` - **IF** core_path does not exist **RETURN** ABSENT — `inst-core-absent`
2. [ ] - `p1` - Check for `.gitmodules` in project root — `inst-check-gitmodules`
3. [ ] - `p1` - **IF** `.gitmodules` exists and contains an entry with `path = {core_path}` — `inst-check-submodule-entry`
   1. [ ] - `p1` - **RETURN** SUBMODULE — `inst-return-submodule`
4. [ ] - `p1` - Check for `.git` inside core_path — `inst-check-core-git`
5. [ ] - `p1` - **IF** `{core_path}/.git` exists (file or directory) — `inst-check-core-git-exists`
   1. [ ] - `p1` - **RETURN** GIT_CLONE — `inst-return-git-clone`
6. [ ] - `p1` - **RETURN** PLAIN_DIR — `inst-return-plain-dir`

### Clean Up V2 Core Path

- [ ] `p1` - **ID**: `cpt-cypilot-algo-v2-v3-migration-cleanup-core-path`

**Input**: Project root path, core_path, core_install_type

**Output**: Cleanup result (success: bool, cleaned_type, warnings[])

**Steps**:
1. [ ] - `p1` - **IF** core_install_type == ABSENT — `inst-cleanup-absent`
   1. [ ] - `p1` - **RETURN** {success: true, cleaned_type: ABSENT, warnings: []} — `inst-return-absent-ok`
2. [ ] - `p1` - **IF** core_install_type == SUBMODULE — `inst-cleanup-submodule`
   1. [ ] - `p1` - Run `git submodule deinit -f {core_path}` to unregister the submodule — `inst-submodule-deinit`
   2. [ ] - `p1` - Remove the submodule entry from `.gitmodules` — `inst-remove-gitmodules-entry`
   3. [ ] - `p1` - **IF** `.gitmodules` is now empty, delete the file — `inst-delete-empty-gitmodules`
   4. [ ] - `p1` - Remove the submodule directory from `.git/modules/{core_path}` — `inst-remove-git-modules-dir`
   5. [ ] - `p1` - Run `git rm -f {core_path}` to remove the submodule from the index — `inst-git-rm-submodule`
   6. [ ] - `p1` - Stage `.gitmodules` changes — `inst-stage-gitmodules`
   7. [ ] - `p1` - **RETURN** {success: true, cleaned_type: SUBMODULE, warnings: ["Submodule removed. Commit the changes to finalize."]} — `inst-return-submodule-ok`
3. [ ] - `p1` - **IF** core_install_type == GIT_CLONE — `inst-cleanup-git-clone`
   1. [ ] - `p1` - Remove the entire core_path directory (including `.git/` inside it) — `inst-remove-clone-dir`
   2. [ ] - `p1` - **RETURN** {success: true, cleaned_type: GIT_CLONE, warnings: ["Git clone removed. Local git history inside core path is lost."]} — `inst-return-clone-ok`
4. [ ] - `p1` - **IF** core_install_type == PLAIN_DIR — `inst-cleanup-plain-dir`
   1. [ ] - `p1` - Remove the entire core_path directory — `inst-remove-plain-dir`
   2. [ ] - `p1` - **RETURN** {success: true, cleaned_type: PLAIN_DIR, warnings: []} — `inst-return-plain-ok`

### Convert Artifacts Registry

- [ ] `p1` - **ID**: `cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry`

**Input**: V2 `artifacts.json` content (parsed), target `{cypilot_path}/config/`

**Output**: `artifacts.toml` written to `{cypilot_path}/config/artifacts.toml`

**Steps**:
1. [ ] - `p1` - Parse v2 `artifacts.json` — extract `systems[]`, `kits{}`, `ignore[]` — `inst-parse-v2-registry`
2. [ ] - `p1` - **FOR EACH** system in `systems[]` — `inst-iterate-systems`
   1. [ ] - `p1` - Map system fields: `name` → `name`, `slug` → `slug`, `kit` → `kit` — `inst-map-system-fields`
   2. [ ] - `p1` - Map `artifacts_dir` to v3 format — `inst-map-artifacts-dir`
   3. [ ] - `p1` - **FOR EACH** autodetect rule in system — `inst-iterate-autodetect`
      1. [ ] - `p1` - Convert `system_root`, `artifacts_root` path templates — `inst-convert-path-templates`
      2. [ ] - `p1` - Convert `artifacts{}` map (pattern, traceability, required per kind) — `inst-convert-artifact-rules`
      3. [ ] - `p1` - Convert `codebase[]` entries (name, path, extensions) — `inst-convert-codebase-entries`
      4. [ ] - `p1` - Convert `validation{}` settings — `inst-convert-validation-settings`
   4. [ ] - `p1` - Map `children[]` if present — `inst-map-children`
3. [ ] - `p1` - **FOR EACH** kit in `kits{}` — `inst-iterate-kits`
   1. [ ] - `p1` - Classify kit: check if kit slug matches known vanilla SDLC kit (exact `sdlc` or legacy aliases like `cf-sdlc`) — `inst-classify-kit`
   2. [ ] - `p1` - **IF** kit is vanilla SDLC — `inst-kit-is-vanilla`
      1. [ ] - `p1` - Remap legacy slug to `sdlc` — `inst-remap-kit-slug`
      2. [ ] - `p1` - Map kit `path` to v3 location: `{cypilot_path}/.gen/kits/sdlc` — `inst-map-kit-path`
      3. [ ] - `p1` - Drop kit-level `artifacts{}` template/examples references (v3 regenerates from blueprints) — `inst-drop-kit-artifact-refs`
   3. [ ] - `p1` - **ELSE** (custom/unknown kit) — `inst-kit-is-custom`
      1. [ ] - `p1` - Preserve original kit slug verbatim — `inst-preserve-custom-slug`
      2. [ ] - `p1` - Map kit `path` to v3 location: `{cypilot_path}/config/kits/{slug}` — `inst-map-custom-kit-path`
      3. [ ] - `p1` - Mark kit as `custom: true` in registry (migration cannot regenerate) — `inst-mark-custom-kit`
4. [ ] - `p1` - Convert `ignore[]` rules — preserve `reason` and `patterns` — `inst-convert-ignore-rules`
5. [ ] - `p1` - Serialize to TOML with deterministic formatting (sorted keys) — `inst-serialize-artifacts-toml`
6. [ ] - `p1` - Validate against artifacts registry schema — `inst-validate-artifacts-schema`
7. [ ] - `p1` - Write `{cypilot_path}/config/artifacts.toml` — `inst-write-artifacts-toml`
8. [ ] - `p1` - **RETURN** conversion result (systems count, kits count, warnings) — `inst-return-artifacts-result`

### Migrate Kits

- [ ] `p1` - **ID**: `cpt-cypilot-algo-v2-v3-migration-migrate-kits`

**Input**: V2 detection result (kits{}, adapter_path), `{cypilot_path}`

**Output**: Kit migration result (vanilla_kits[], custom_kits[], warnings[])

**Steps**:
1. [ ] - `p1` - **FOR EACH** kit in v2 kits{} — `inst-iterate-kits-migrate`
   1. [ ] - `p1` - **IF** kit is vanilla SDLC (slug `sdlc` or legacy alias) — `inst-kit-vanilla-check`
      1. [ ] - `p1` - Install SDLC kit from cache into `{cypilot_path}/config/kits/sdlc/blueprints/` — `inst-install-sdlc-blueprints`
      2. [ ] - `p1` - Regenerate blueprint outputs into `{cypilot_path}/.gen/kits/sdlc/` (templates, rules, checklists, examples, constraints.toml) — `inst-regen-sdlc-outputs`
      3. [ ] - `p1` - Add to vanilla_kits[] — `inst-add-vanilla-kit`
   2. [ ] - `p1` - **ELSE** (custom/unknown kit) — `inst-kit-custom-migrate`
      1. [ ] - `p1` - Copy v2 kit directory from `{adapter_path}/kits/{v2_slug}/` to `{cypilot_path}/config/kits/{slug}/` — `inst-copy-custom-kit-config`
      2. [ ] - `p1` - Copy v2 kit outputs (artifacts/, codebase/, rules) to `{cypilot_path}/.gen/kits/{slug}/` as-is — `inst-copy-custom-kit-gen`
      3. [ ] - `p1` - **IF** `constraints.json` exists in v2 kit directory — `inst-check-custom-constraints-json`
         1. [ ] - `p1` - Convert `constraints.json` → `constraints.toml` (JSON parse → TOML serialize) — `inst-convert-custom-constraints`
         2. [ ] - `p1` - Write `constraints.toml` to `{cypilot_path}/.gen/kits/{slug}/constraints.toml` — `inst-write-custom-constraints-toml`
         3. [ ] - `p1` - Do NOT copy original `constraints.json` — `inst-skip-custom-constraints-json`
      4. [ ] - `p1` - **ELSE** — `inst-no-custom-constraints`
         1. [ ] - `p1` - Copy any existing constraints file as-is — `inst-copy-constraints-fallback`
      5. [ ] - `p1` - Emit warning: "Kit '{slug}' is not a known kit. Copied as-is — templates, rules, and constraints were NOT regenerated. Manual review recommended." — `inst-warn-custom-kit`
      6. [ ] - `p1` - Add to custom_kits[] — `inst-add-custom-kit`
2. [ ] - `p1` - **RETURN** {vanilla_kits, custom_kits, warnings} — `inst-return-kits-result`

### Convert Adapter AGENTS.md

- [ ] `p1` - **ID**: `cpt-cypilot-algo-v2-v3-migration-convert-agents-md`

**Input**: V2 `.cypilot-adapter/AGENTS.md` content, target `{cypilot_path}/config/`

**Output**: `{cypilot_path}/config/AGENTS.md` written

**Steps**:
1. [ ] - `p1` - Read `.cypilot-adapter/AGENTS.md` — `inst-read-adapter-agents`
2. [ ] - `p1` - **IF** file not found **RETURN** {skipped: true, reason: "No adapter AGENTS.md"} — `inst-check-adapter-agents-exists`
3. [ ] - `p1` - Parse content — extract WHEN rules, variables, project overview, module rules — `inst-parse-agents-content`
4. [ ] - `p1` - Convert path references: replace `{cypilot_adapter_path}` with `{cypilot_path}/config` — `inst-convert-adapter-paths`
5. [ ] - `p1` - Convert `Extends` reference: remove legacy `../.cypilot/AGENTS.md` reference — `inst-remove-extends-ref`
6. [ ] - `p1` - Update `artifacts.json` references to `artifacts.toml` in WHEN rules — `inst-update-registry-refs`
7. [ ] - `p1` - Preserve all custom WHEN rules, module rules, and project-specific content verbatim — `inst-preserve-custom-rules`
8. [ ] - `p1` - Write `{cypilot_path}/config/AGENTS.md` — `inst-write-config-agents`
9. [ ] - `p1` - **RETURN** conversion result (rules migrated count, paths updated count) — `inst-return-agents-result`

### Generate core.toml

- [ ] `p1` - **ID**: `cpt-cypilot-algo-v2-v3-migration-generate-core-toml`

**Input**: V2 detection result, converted artifacts data

**Output**: `{cypilot_path}/config/core.toml` written

**Steps**:
1. [ ] - `p1` - Derive project name and slug from project directory name — `inst-derive-project-info`
2. [ ] - `p1` - Set schema version to current v3 version — `inst-set-schema-version`
3. [ ] - `p1` - Set `project_root` to relative path `..` — `inst-set-project-root`
4. [ ] - `p1` - **FOR EACH** system from v2 artifacts — `inst-iterate-v2-systems`
   1. [ ] - `p1` - Create system entry with name, slug, kit assignment — `inst-create-system-entry`
5. [ ] - `p1` - Register kits — map v2 kit registrations to v3 format (slug → path) — `inst-register-kits`
6. [ ] - `p1` - Validate against `core-config.schema.json` — `inst-validate-core-schema`
7. [ ] - `p1` - Write `{cypilot_path}/config/core.toml` with deterministic serialization — `inst-write-core-toml`
8. [ ] - `p1` - **RETURN** core.toml creation result — `inst-return-core-result`

### Inject Root AGENTS.md Managed Block

- [ ] `p1` - **ID**: `cpt-cypilot-algo-v2-v3-migration-inject-root-agents`

**Input**: Project root path, `{cypilot_path}`

**Output**: Root `AGENTS.md` updated with managed block

**Steps**:
1. [ ] - `p1` - Read existing root `AGENTS.md` — `inst-read-root-agents`
2. [ ] - `p1` - **IF** file not found, create with managed block only — `inst-create-root-agents`
3. [ ] - `p1` - Check for existing `<!-- @cpt:root-agents -->` block — `inst-check-existing-block`
4. [ ] - `p1` - **IF** block exists, replace with updated content — `inst-replace-block`
5. [ ] - `p1` - **ELSE** prepend managed block before existing content — `inst-prepend-block`
6. [ ] - `p1` - Managed block content: `cypilot_path` variable, navigation rules pointing to `{cypilot_path}/.gen/AGENTS.md` and `{cypilot_path}/config/AGENTS.md` — `inst-compose-block`
7. [ ] - `p1` - Preserve all existing non-managed content verbatim — `inst-preserve-existing-content`
8. [ ] - `p1` - Write updated `AGENTS.md` — `inst-write-root-agents`
9. [ ] - `p1` - **RETURN** injection result (created or updated, preserved content size) — `inst-return-inject-result`

### Validate Migration Completeness

- [ ] `p1` - **ID**: `cpt-cypilot-algo-v2-v3-migration-validate-migration`

**Input**: Project root path, `{cypilot_path}`, v2 detection result

**Output**: Validation result (passed: bool, issues[])

**Steps**:
1. [ ] - `p1` - Verify `{cypilot_path}/config/core.toml` exists and is valid — `inst-verify-core-toml`
2. [ ] - `p1` - Verify `{cypilot_path}/config/artifacts.toml` exists and is valid — `inst-verify-artifacts-toml`
3. [ ] - `p1` - Verify all v2 systems are present in v3 artifacts.toml — `inst-verify-systems-migrated`
4. [ ] - `p1` - Verify all existing artifact files still resolve via v3 autodetect — `inst-verify-artifacts-resolve`
5. [ ] - `p1` - Verify all `cpt-*` IDs from v2 artifacts are still discoverable — `inst-verify-ids-discoverable`
6. [ ] - `p1` - Verify root `AGENTS.md` contains `<!-- @cpt:root-agents -->` managed block — `inst-verify-root-agents-block`
7. [ ] - `p1` - Verify `{cypilot_path}/config/AGENTS.md` exists (if v2 had adapter AGENTS.md) — `inst-verify-config-agents`
8. [ ] - `p1` - Verify agent entry points exist for all supported agents — `inst-verify-agent-entries`
9. [ ] - `p1` - Verify `{cypilot_path}/.core/` exists with core skill files — `inst-verify-core-dir`
10. [ ] - `p1` - Verify `{cypilot_path}/.gen/` exists with generated kit outputs — `inst-verify-gen-dir`
11. [ ] - `p1` - **FOR EACH** issue found — `inst-collect-issues`
    1. [ ] - `p1` - Record issue with severity, file path, and remediation — `inst-record-issue`
12. [ ] - `p1` - **RETURN** {passed: issues.length == 0, issues} — `inst-return-validation-result`

## 4. States (CDSL)

### Migration State Machine

- [ ] `p2` - **ID**: `cpt-cypilot-state-v2-v3-migration-status`

**States**: NOT_STARTED, DETECTED, BACKED_UP, CONVERTING, CONVERTED, VALIDATING, COMPLETED, ROLLED_BACK, FAILED

**Initial State**: NOT_STARTED

**Transitions**:
1. [ ] - `p1` - **FROM** NOT_STARTED **TO** DETECTED **WHEN** v2 installation detected and user confirms — `inst-transition-detected`
2. [ ] - `p1` - **FROM** DETECTED **TO** BACKED_UP **WHEN** backup created successfully — `inst-transition-backed-up`
3. [ ] - `p1` - **FROM** BACKED_UP **TO** CONVERTING **WHEN** conversion starts (artifacts, agents, config) — `inst-transition-converting`
4. [ ] - `p1` - **FROM** CONVERTING **TO** CONVERTED **WHEN** all conversions complete successfully — `inst-transition-converted`
5. [ ] - `p1` - **FROM** CONVERTED **TO** VALIDATING **WHEN** post-migration validation starts — `inst-transition-validating`
6. [ ] - `p1` - **FROM** VALIDATING **TO** COMPLETED **WHEN** validation passes — `inst-transition-completed`
7. [ ] - `p1` - **FROM** VALIDATING **TO** ROLLED_BACK **WHEN** validation fails and rollback succeeds — `inst-transition-rolled-back`
8. [ ] - `p1` - **FROM** CONVERTING **TO** ROLLED_BACK **WHEN** conversion fails and rollback succeeds — `inst-transition-convert-rollback`
9. [ ] - `p1` - **FROM** CONVERTING **TO** FAILED **WHEN** conversion fails and rollback also fails — `inst-transition-failed`
10. [ ] - `p1` - **FROM** VALIDATING **TO** FAILED **WHEN** validation fails and rollback also fails — `inst-transition-validate-failed`

## 5. Definitions of Done

### V2 Detection

- [ ] `p1` - **ID**: `cpt-cypilot-dod-v2-v3-migration-v2-detection`

The system **MUST** detect v2 installations by identifying `.cypilot-adapter/` directory, `artifacts.json`, and legacy kit paths. The system **MUST** parse `.cypilot-config.json` when present to determine adapter and core paths, falling back to defaults (`.cypilot`, `.cypilot-adapter`) when absent. The system **MUST** detect the core path install type (SUBMODULE, GIT_CLONE, PLAIN_DIR, ABSENT) by checking `.gitmodules` and `.git` presence inside the core path.

**Implements**:
- `cpt-cypilot-flow-v2-v3-migration-migrate-project`
- `cpt-cypilot-algo-v2-v3-migration-detect-v2`
- `cpt-cypilot-algo-v2-v3-migration-detect-core-install-type`

**Touches**:
- Entities: `Config`, `System`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-init`

**Covers (DESIGN)**:
- `cpt-cypilot-principle-zero-harm`
- `cpt-cypilot-component-config-manager`
- `cpt-cypilot-component-skill-engine`

### V2 Core Path Cleanup

- [ ] `p1` - **ID**: `cpt-cypilot-dod-v2-v3-migration-core-cleanup`

The system **MUST** handle three distinct v2 core installation types during migration:

1. **SUBMODULE**: The system **MUST** fully remove the git submodule — `git submodule deinit`, remove `.gitmodules` entry, remove `.git/modules/{path}`, and `git rm` the path. The system **MUST** warn the user to commit the resulting changes.
2. **GIT_CLONE**: The system **MUST** remove the entire core directory including its embedded `.git/`. Local git history inside the core path is intentionally discarded.
3. **PLAIN_DIR**: The system **MUST** remove the entire core directory. No special handling required.

In all cases, the backup **MUST** be created before cleanup. If cleanup fails, the system **MUST** abort migration with the backup intact.

**Implements**:
- `cpt-cypilot-flow-v2-v3-migration-migrate-project`
- `cpt-cypilot-algo-v2-v3-migration-cleanup-core-path`
- `cpt-cypilot-algo-v2-v3-migration-detect-core-install-type`

**Touches**:
- Entities: `Config`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-init`

**Covers (DESIGN)**:
- `cpt-cypilot-principle-zero-harm`
- `cpt-cypilot-component-config-manager`
- `cpt-cypilot-component-skill-engine`

### Artifacts Registry Conversion

- [ ] `p1` - **ID**: `cpt-cypilot-dod-v2-v3-migration-artifacts-conversion`

The system **MUST** convert `.cypilot-adapter/artifacts.json` to `{cypilot_path}/config/artifacts.toml`. The conversion **MUST** preserve all systems, autodetect rules, codebase entries, ignore rules, and validation settings. Legacy kit slugs (e.g., `cf-sdlc`) **MUST** be remapped to standard slugs (`sdlc`) when the kit is the standard SDLC kit. The resulting TOML **MUST** validate against the artifacts registry schema.

**Implements**:
- `cpt-cypilot-flow-v2-v3-migration-migrate-project`
- `cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry`

**Touches**:
- Entities: `Config`, `System`, `Artifact`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-config`

**Covers (DESIGN)**:
- `cpt-cypilot-principle-zero-harm`
- `cpt-cypilot-principle-no-manual-maintenance`
- `cpt-cypilot-component-config-manager`

### Adapter AGENTS.md Conversion

- [ ] `p1` - **ID**: `cpt-cypilot-dod-v2-v3-migration-agents-conversion`

The system **MUST** convert `.cypilot-adapter/AGENTS.md` to `{cypilot_path}/config/AGENTS.md`. The conversion **MUST** update path references from `{cypilot_adapter_path}` to `{cypilot_path}/config`, remove legacy `Extends` references, update `artifacts.json` references to `artifacts.toml`, and preserve all custom WHEN rules and project-specific content verbatim.

**Implements**:
- `cpt-cypilot-flow-v2-v3-migration-migrate-project`
- `cpt-cypilot-algo-v2-v3-migration-convert-agents-md`

**Touches**:
- Entities: `Config`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-config`

**Covers (DESIGN)**:
- `cpt-cypilot-principle-zero-harm`
- `cpt-cypilot-component-config-manager`

### Core Config Generation

- [ ] `p1` - **ID**: `cpt-cypilot-dod-v2-v3-migration-core-config`

The system **MUST** generate `{cypilot_path}/config/core.toml` from the v2 project state. The generated config **MUST** include schema version, project root, all system definitions (name, slug, kit assignment), and kit registrations. The config **MUST** validate against `core-config.schema.json`.

**Implements**:
- `cpt-cypilot-flow-v2-v3-migration-migrate-project`
- `cpt-cypilot-algo-v2-v3-migration-generate-core-toml`

**Touches**:
- Entities: `Config`, `System`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-config`

**Covers (DESIGN)**:
- `cpt-cypilot-component-config-manager`

### Root AGENTS.md Injection

- [ ] `p1` - **ID**: `cpt-cypilot-dod-v2-v3-migration-root-agents-injection`

The system **MUST** inject or update the `<!-- @cpt:root-agents -->` managed block in the project root `AGENTS.md`. Existing non-managed content **MUST** be preserved verbatim. If the file does not exist, it **MUST** be created with the managed block. The managed block **MUST** contain navigation rules pointing to `{cypilot_path}/.gen/AGENTS.md` and `{cypilot_path}/config/AGENTS.md`.

**Implements**:
- `cpt-cypilot-flow-v2-v3-migration-migrate-project`
- `cpt-cypilot-algo-v2-v3-migration-inject-root-agents`

**Touches**:
- Entities: `Config`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-init`

**Covers (DESIGN)**:
- `cpt-cypilot-principle-zero-harm`
- `cpt-cypilot-component-skill-engine`

### Kit Installation and Regeneration

- [ ] `p1` - **ID**: `cpt-cypilot-dod-v2-v3-migration-kit-install`

The system **MUST** distinguish between vanilla SDLC kits and custom/unknown kits during migration:

1. **Vanilla SDLC kit** (slug `sdlc` or legacy aliases like `cf-sdlc`): The system **MUST** install from cache into `{cypilot_path}/config/kits/sdlc/blueprints/` and regenerate all blueprint outputs (templates, rules, checklists, examples, constraints.toml) into `{cypilot_path}/.gen/kits/sdlc/`. Legacy `constraints.json` files **MUST NOT** be migrated — they are regenerated from blueprints.
2. **Custom/unknown kits**: The system **MUST** copy the v2 kit directory as-is into `{cypilot_path}/config/kits/{slug}/` and copy existing outputs (artifacts/, codebase/, rules) into `{cypilot_path}/.gen/kits/{slug}/` without regeneration. If the custom kit contains `constraints.json`, the system **MUST** convert it to `constraints.toml` (JSON parse → TOML serialize) — this is a pure format conversion with no semantic interpretation. The system **MUST** emit a warning that the custom kit was not regenerated and requires manual review.

The system **MUST NOT** attempt to regenerate or interpret custom kit content — it has no knowledge of custom kit blueprints or semantics. The `constraints.json` → `constraints.toml` conversion is the only transformation applied to custom kits.

**Implements**:
- `cpt-cypilot-flow-v2-v3-migration-migrate-project`
- `cpt-cypilot-algo-v2-v3-migration-migrate-kits`

**Touches**:
- Entities: `Config`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-config`

**Covers (DESIGN)**:
- `cpt-cypilot-principle-no-manual-maintenance`
- `cpt-cypilot-principle-zero-harm`
- `cpt-cypilot-component-kit-manager`

### Agent Entry Points Regeneration

- [ ] `p1` - **ID**: `cpt-cypilot-dod-v2-v3-migration-agent-entries`

The system **MUST** regenerate all agent entry points for v3 structure (`.windsurf/`, `.cursor/`, `.claude/`, `.github/`). Existing empty agent directories from v2 **MUST** be replaced with properly populated v3 entry points containing workflow proxies and skill shims.

**Implements**:
- `cpt-cypilot-flow-v2-v3-migration-migrate-project`

**Touches**:
- Entities: `AgentEntryPoint`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-init`

**Covers (DESIGN)**:
- `cpt-cypilot-principle-no-manual-maintenance`
- `cpt-cypilot-component-skill-engine`

### Backup and Rollback

- [ ] `p1` - **ID**: `cpt-cypilot-dod-v2-v3-migration-backup-rollback`

The system **MUST** create a complete backup of the v2 state before migration. The backup **MUST** include `.cypilot-adapter/`, `.cypilot-config.json`, core path, root `AGENTS.md`, and agent entry point directories. If migration or validation fails, the system **MUST** restore the backup and report the failure. The backup **MUST** include a manifest documenting all backed-up paths.

**Implements**:
- `cpt-cypilot-flow-v2-v3-migration-migrate-project`
- `cpt-cypilot-algo-v2-v3-migration-backup-v2-state`

**Touches**:
- Entities: `Config`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-init`

**Covers (DESIGN)**:
- `cpt-cypilot-principle-zero-harm`
- `cpt-cypilot-component-config-manager`

### Migration Validation

- [ ] `p1` - **ID**: `cpt-cypilot-dod-v2-v3-migration-validation`

The system **MUST** validate migration completeness by verifying: config files exist and are valid, all v2 systems are present in v3, all artifact files still resolve via autodetect, all `cpt-*` IDs are still discoverable, root `AGENTS.md` has the managed block, agent entry points exist, and the v3 directory structure (`.core/`, `.gen/`, `config/`) is complete.

**Implements**:
- `cpt-cypilot-flow-v2-v3-migration-migrate-project`
- `cpt-cypilot-algo-v2-v3-migration-validate-migration`

**Touches**:
- Entities: `Config`, `System`, `Artifact`, `Identifier`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-init`
- `cpt-cypilot-fr-core-config`

**Covers (DESIGN)**:
- `cpt-cypilot-principle-zero-harm`
- `cpt-cypilot-component-config-manager`
- `cpt-cypilot-component-skill-engine`

### JSON → TOML Config Migration

- [ ] `p1` - **ID**: `cpt-cypilot-dod-v2-v3-migration-json-to-toml`

The system **MUST** provide `cypilot migrate-config` to convert remaining JSON config files to TOML. The migrator **MUST** process files individually — a failure in one file does not block others. Each converted TOML file **MUST** validate against its schema before the original JSON is removed. The migrator **MUST** run automatically during `cypilot update` when upgrading from a JSON-based version.

**Implements**:
- `cpt-cypilot-flow-v2-v3-migration-migrate-config`

**Touches**:
- Entities: `Config`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-config`

**Covers (DESIGN)**:
- `cpt-cypilot-principle-no-manual-maintenance`
- `cpt-cypilot-component-config-manager`

## 6. Acceptance Criteria

- [ ] `cypilot migrate` converts a v2 project with `.cypilot-adapter/artifacts.json` to v3 `{cypilot_path}/config/artifacts.toml` with all systems and autodetect rules preserved
- [ ] `cypilot migrate` preserves all custom WHEN rules from `.cypilot-adapter/AGENTS.md` in `{cypilot_path}/config/AGENTS.md`
- [ ] `cypilot migrate` creates valid `{cypilot_path}/config/core.toml` that passes schema validation
- [ ] `cypilot migrate` injects `<!-- @cpt:root-agents -->` managed block into root `AGENTS.md` without destroying existing content
- [ ] `cypilot migrate` creates backup that can be manually restored to fully recover v2 state
- [ ] `cypilot migrate` rollback restores v2 state when post-migration validation fails
- [ ] All `cpt-*` IDs from v2 artifact files remain discoverable after migration (verified by `cypilot validate`)
- [ ] All v2 artifact files still resolve via v3 autodetect rules (no missing file errors)
- [ ] `cypilot migrate-config` converts all JSON config files to TOML individually, skipping failed files
- [ ] Complex case: hyperspot project (2 systems, 2 autodetect patterns, 17 ignore rules, custom kit slug `cf-sdlc`) migrates successfully with zero data loss
- [ ] Agent entry points (`.windsurf/`, `.cursor/`, `.claude/`, `.github/`) are regenerated for v3 structure
- [ ] Vanilla SDLC kit (including legacy slug `cf-sdlc`) is fully regenerated from blueprints in v3 structure
- [ ] Custom/unknown kits are copied as-is to `config/kits/{slug}/` and `.gen/kits/{slug}/` with a warning emitted; `constraints.json` is converted to `constraints.toml`
- [ ] Submodule case: `.cypilot` as git submodule is fully deinitialized — `.gitmodules` entry removed, `.git/modules/` cleaned, submodule path removed from index
- [ ] Git clone case: `.cypilot` containing `.git/` directory is removed entirely, v3 structure created in its place
- [ ] Plain directory case: `.cypilot` as a plain directory is removed and replaced with v3 structure

## 7. Additional Context

### Non-Applicable Domains

- **Security (SEC)**: Not applicable because this feature is a local CLI migration tool with no authentication, authorization, network operations, or sensitive data handling. All file operations are local filesystem reads/writes.
- **Performance (PERF)**: Not applicable because migration is a one-time operation. There are no latency targets, caching strategies, or scalability concerns. The operation processes a small number of config files sequentially.
- **Usability (UX)**: Not applicable because this is a CLI command with no frontend. User interaction is limited to confirmation prompts and reading JSON output.
- **Operations (OPS)**: Not applicable because this is a local CLI tool with no deployment, monitoring, or observability infrastructure.
- **Compliance (COMPL)**: Not applicable because this feature handles no regulated data, PII, or compliance-sensitive information.

### Maintainability Notes

- The migration is forward-only — v3 projects cannot be downgraded to v2
- The `cypilot migrate` command reuses existing components: Config Manager for TOML serialization, Kit Manager for kit installation, Skill Engine for agent entry point generation
- Legacy kit slug remapping (e.g., `cf-sdlc` → `sdlc`) uses a configurable alias table, not hard-coded conditions
- Custom kits are opaque to the migrator — copied verbatim, never regenerated or interpreted; users must manually update custom kits for v3 compatibility if needed
- The `.cypilot-config.json` file is a v2-only artifact — v3 uses `core.toml` exclusively
- The backup directory (`.cypilot-v2-backup-*`) can be safely deleted after confirming migration success

### Testing Approach

- **Unit tests**: Test each conversion algorithm independently with fixture v2 configs (simple case, complex case matching hyperspot structure)
- **Integration tests**: Run full `cypilot migrate` on fixture v2 projects, verify all validation checks pass
- **Core install type tests**: Three fixture variants — submodule (mock `.gitmodules` + `.git/modules/`), git clone (`.cypilot/.git/` directory), plain directory (no `.git` artifacts)
- **Submodule cleanup tests**: Verify `git submodule deinit`, `.gitmodules` entry removal, `.git/modules/` cleanup, index removal; verify rollback restores `.gitmodules` and submodule state
- **Custom kit tests**: Fixture with custom kit slug (not `sdlc`), verify copied as-is to `config/kits/` and `.gen/kits/`, verify warning emitted, verify no regeneration attempted
- **Mixed kit tests**: Fixture with both vanilla SDLC (`cf-sdlc`) and a custom kit, verify SDLC regenerated while custom copied as-is
- **Edge case tests**: Empty `artifacts.json`, missing `AGENTS.md`, custom `cypilotCorePath`, conflicting existing v3 files, core path ABSENT (no `.cypilot/` at all)
- **Rollback tests**: Inject failures at each conversion step (including core cleanup), verify backup restoration including `.gitmodules` for submodule case
- **Complex case test**: Fixture matching hyperspot structure (2 systems, nested autodetect, 17 ignore rules, custom kit slug, `.cypilot-config.json` with custom paths)
