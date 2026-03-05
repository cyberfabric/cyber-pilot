# Feature: Version & Config Management


<!-- toc -->

- [1. Feature Context](#1-feature-context)
  - [1. Overview](#1-overview)
  - [2. Purpose](#2-purpose)
  - [3. Actors](#3-actors)
  - [4. References](#4-references)
- [2. Actor Flows (CDSL)](#2-actor-flows-cdsl)
  - [Update Project Installation](#update-project-installation)
  - [Manage Config via CLI](#manage-config-via-cli)
- [3. Processes / Business Logic (CDSL)](#3-processes-business-logic-cdsl)
  - [Update Pipeline](#update-pipeline)
  - [Layout Restructuring](#layout-restructuring)
  - [Compare Blueprint Versions](#compare-blueprint-versions)
  - [Migrate Config](#migrate-config)
- [4. States (CDSL)](#4-states-cdsl)
  - [Installation Version State](#installation-version-state)
- [5. Definitions of Done](#5-definitions-of-done)
  - [Update Command](#update-command)
  - [Config CLI Commands](#config-cli-commands)
  - [Config Migration](#config-migration)
- [6. Implementation Modules](#6-implementation-modules)
- [7. Acceptance Criteria](#7-acceptance-criteria)

<!-- /toc -->

- [ ] `p2` - **ID**: `cpt-cypilot-featstatus-version-config`

## 1. Feature Context

- [ ] `p2` - `cpt-cypilot-feature-version-config`

### 1. Overview

Enables project skill updates with config migration, and provides CLI commands for managing system definitions, ignore lists, and kit registrations. The update command refreshes `.core/` from cache, detects and auto-restructures old directory layouts, updates kits via hash-based customization detection with interactive diff, regenerates outputs into kit config directories, and ensures `config/` scaffold files exist without overwriting user content.

### 2. Purpose

Ensures teams can upgrade Cypilot without losing configuration or customizations. Config CLI commands eliminate manual TOML editing and enforce schema validation. Addresses PRD requirements for version management (`cpt-cypilot-fr-core-version`) and CLI configuration (`cpt-cypilot-fr-core-cli-config`).

### 3. Actors

| Actor | Role in Feature |
|-------|-----------------|
| `cpt-cypilot-actor-user` | Runs `cpt update`, `cpt config`, `cpt migrate-config` |
| `cpt-cypilot-actor-cypilot-cli` | Executes update pipeline, config mutations, migration |

### 4. References

- **PRD**: [PRD.md](../PRD.md) — `cpt-cypilot-fr-core-version`, `cpt-cypilot-fr-core-layout-migration`, `cpt-cypilot-fr-core-cli-config`
- **Design**: [DESIGN.md](../DESIGN.md) — `cpt-cypilot-component-config-manager`, `cpt-cypilot-seq-update`
- **Dependencies**: `cpt-cypilot-feature-core-infra`, `cpt-cypilot-feature-blueprint-system`

## 2. Actor Flows (CDSL)

### Update Project Installation

- [ ] `p1` - **ID**: `cpt-cypilot-flow-version-config-update`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User runs `cpt update` → `.core/` refreshed from cache, old layout auto-restructured if detected, kits updated via hash-based detection, outputs regenerated with interactive diff, config scaffold ensured
- Blueprint hash matches known default → blueprint auto-updated silently
- Blueprint customized by user → interactive diff presented

**Error Scenarios**:
- Cypilot not initialized → error with hint to run `cpt init`
- Cache not available → error with hint to check network

**Steps**:
1. [x] - `p1` - User invokes `cpt update [--project-root P] [--dry-run]` - `inst-user-update`
2. [x] - `p1` - Resolve project root and cypilot directory - `inst-resolve-project`
3. [x] - `p1` - Replace `.core/` from cache (always force-overwrite) - `inst-replace-core`
4. [ ] - `p1` - Detect directory layout; if old layout detected, trigger automatic restructuring using `cpt-cypilot-algo-version-config-layout-restructure` - `inst-detect-layout`
5. [ ] - `p1` - Migrate `{cypilot_path}/config/core.toml` preserving all user settings - `inst-migrate-config`
6. [ ] - `p1` - For each kit: update via hash-based customization detection (unmodified blueprints auto-update, customized trigger interactive diff), regenerate outputs with interactive diff for user-modified resources - `inst-update-kits`
7. [x] - `p1` - Ensure config scaffold files exist (create only if missing) - `inst-ensure-scaffold`
8. [x] - `p1` - Regenerate agent entry points - `inst-regenerate-agents`
9. [x] - `p1` - Run self-check to verify kit integrity (`run_self_check_from_meta`); include result in report, WARN if failed - `inst-self-check`
10. [x] - `p1` - **RETURN** update report with actions taken and self-check result - `inst-return-report`

### Manage Config via CLI

- [ ] `p2` - **ID**: `cpt-cypilot-flow-version-config-manage`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User runs `cpt config show` → displays current core.toml contents
- User runs `cpt config system add` → adds system definition with schema validation

**Steps**:
1. - `p2` - User invokes `cpt config <subcommand> [args]` - `inst-user-config`
2. - `p2` - Validate change against config schema - `inst-validate-schema`
3. - `p2` - Apply change to config file - `inst-apply-change`
4. - `p2` - **RETURN** summary of what was modified - `inst-return-config-summary`

## 3. Processes / Business Logic (CDSL)

### Update Pipeline

- [x] `p1` - **ID**: `cpt-cypilot-algo-version-config-update-pipeline`

1. - `p1` - Replace `.core/` from cache - `inst-replace-core-algo`
2. - `p1` - Detect and auto-restructure old directory layout - `inst-detect-layout-algo`
3. - `p1` - Migrate `{cypilot_path}/config/core.toml` - `inst-migrate-config-algo`
4. - `p1` - For each kit: hash-based customization detection, interactive diff for customized blueprints - `inst-update-kits-algo`
5. - `p1` - Regenerate outputs into kit config directories with interactive diff for user-modified resources - `inst-regen-algo`
6. - `p1` - Ensure config scaffold - `inst-scaffold-algo`

### Layout Restructuring

- [ ] `p1` - **ID**: `cpt-cypilot-algo-version-config-layout-restructure`

**Input**: Cypilot directory path

**Output**: Restructured directory layout or no-op if already new layout

**Detection**: Old layout is detected when `{cypilot_path}/config/kits/{slug}/blueprints/` exists AND `{cypilot_path}/.gen/kits/{slug}/` exists.

**Steps**:
1. - `p1` - Backup affected directories - `inst-layout-backup`
2. - `p1` - Move `config/kits/{slug}/blueprints/` → `kits/{slug}/blueprints/` - `inst-layout-move-blueprints`
3. - `p1` - Move `config/kits/{slug}/conf.toml` → `kits/{slug}/conf.toml` - `inst-layout-move-conf`
4. - `p1` - Move `.gen/kits/{slug}/` → `config/kits/{slug}/` (generated outputs) - `inst-layout-move-gen`
5. - `p1` - Remove old reference copies in `kits/{slug}/` if present - `inst-layout-remove-refs`
6. - `p1` - Remove `.gen/kits/` directory (preserve `.gen/AGENTS.md`, `.gen/SKILL.md`, `.gen/README.md`) - `inst-layout-clean-gen`
7. - `p1` - Compute SHA-256 hashes for all blueprint files and store in `kits/{slug}/conf.toml` - `inst-layout-compute-hashes`
8. - `p1` - Update `core.toml` kit registrations with new paths - `inst-layout-update-core`
9. - `p1` - **IF** any step fails, restore from backup and report error - `inst-layout-rollback`

### Compare Blueprint Versions

- [x] `p1` - **ID**: `cpt-cypilot-algo-version-config-compare-versions`

1. - `p1` - Read `@cpt:blueprint` TOML block from each blueprint to extract version - `inst-read-versions`
2. - `p1` - Compare cache version vs user version per blueprint - `inst-compare-per-bp`
3. - `p1` - **RETURN** `current` (same), `migration_needed` (higher), or `missing` - `inst-return-comparison`

### Migrate Config

- [ ] `p2` - **ID**: `cpt-cypilot-algo-version-config-migrate`

1. - `p2` - Create backup of current config - `inst-backup`
2. - `p2` - Apply migration rules preserving user settings - `inst-apply-migration`
3. - `p2` - Report any settings that could not be migrated - `inst-report-unmigrated`

## 4. States (CDSL)

### Installation Version State

- [ ] `p1` - **ID**: `cpt-cypilot-state-version-config-installation`

```
[CURRENT] --new-cache-available--> [OUTDATED] --update--> [CURRENT]
[OUTDATED] --update-with-migration--> [MIGRATION_NEEDED] --manual-resolve--> [CURRENT]
```

## 5. Definitions of Done

### Update Command

- [ ] `p1` - **ID**: `cpt-cypilot-dod-version-config-update`

- [x] - `p1` - `cpt update` replaces `.core/` from cache
- [ ] - `p1` - `cpt update` detects old directory layout and auto-restructures (move blueprints from `config/kits/` to `kits/`, move generated outputs from `.gen/kits/` to `config/kits/`, compute initial hashes)
- [ ] - `p1` - `cpt update` updates kits via hash-based customization detection with interactive diff
- [ ] - `p1` - `cpt update` regenerates outputs into kit config directories with interactive diff for user-modified resources
- [ ] - `p1` - User config files in `config/` are NEVER overwritten (except through interactive diff acceptance)
- [x] - `p1` - Blueprint version comparison detects same, migration needed, and missing states
- [x] - `p1` - `--dry-run` shows what would be done without writing
- [x] - `p1` - `cpt update` automatically runs self-check after completion and includes result in report

### Config CLI Commands

- [ ] `p2` - **ID**: `cpt-cypilot-dod-version-config-cli`

- [ ] - `p2` - `cpt config show` displays current configuration
- [ ] - `p2` - `cpt config system add/remove` manages system definitions
- [ ] - `p2` - Schema validation rejects invalid changes before writing

### Config Migration

- [ ] `p2` - **ID**: `cpt-cypilot-dod-version-config-migration`

- [ ] - `p2` - `cpt migrate-config` migrates legacy JSON configs to TOML
- [ ] - `p2` - Backup created before any migration
- [ ] - `p2` - User settings preserved across version upgrades

## 6. Implementation Modules

| Module | Path | Responsibility |
|--------|------|----------------|
| Update Command | `skills/.../commands/update.py` | Update pipeline, layout restructuring, hash-based detection, output regeneration |

## 7. Acceptance Criteria

- [ ] `cpt update` refreshes `.core/` and regenerates outputs without touching user config (unless interactive diff accepted)
- [ ] `cpt update` detects and auto-restructures old directory layout with backup and rollback
- [x] Blueprint version comparison correctly identifies same, migration needed, and missing states
- [ ] Hash-based customization detection: unmodified blueprints auto-update, customized trigger interactive diff
- [ ] All generated outputs (SKILL.md, constraints.toml, artifacts/, codebase/, workflows/, scripts/) use interactive diff when content differs
- [ ] `cpt config show` displays readable config summary
- [ ] Config migration preserves all user settings with backup
- [x] `cpt update` automatically runs self-check after update and reports WARN if integrity check fails
