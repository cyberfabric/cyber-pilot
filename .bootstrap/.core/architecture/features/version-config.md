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
  - [Compare Blueprint Versions (LEGACY)](#compare-blueprint-versions-legacy)
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

Enables project skill updates with config migration, and provides CLI commands for managing system definitions, ignore lists, and kit registrations. The update command refreshes `.core/` from cache, detects and auto-restructures old directory layouts, migrates bundled kit references to GitHub sources (versions < 3.0.8), and ensures `config/` scaffold files exist without overwriting user content. Kit file updates are a separate operation via `cpt kit update`.

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

- [x] `p1` - **ID**: `cpt-cypilot-flow-version-config-update`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User runs `cpt update` → `.core/` refreshed from cache, old layout auto-restructured if detected, bundled kit refs migrated to GitHub sources, config scaffold ensured
- Bundled kit (no `source` field) → auto-migrated to GitHub source

**Error Scenarios**:
- Cypilot not initialized → error with hint to run `cpt init`
- Cache not available → error with hint to check network

**Steps**:
1. [x] - `p1` - User invokes `cpt update [--project-root P] [--dry-run]` - `inst-user-update`
2. [x] - `p1` - Resolve project root and cypilot directory - `inst-resolve-project`
3. [x] - `p1` - Replace `.core/` from cache (always force-overwrite) - `inst-replace-core`
4. [x] - `p1` - Detect directory layout; if old layout detected, trigger automatic restructuring using `cpt-cypilot-algo-version-config-layout-restructure` - `inst-detect-layout`
5. [x] - `p1` - Migrate `{cypilot_path}/config/core.toml` preserving all user settings - `inst-migrate-config`
6. [x] - `p1` - Migrate bundled kit references to GitHub sources (add `source` field for kits without one) - `inst-migrate-kit-sources`
7. [x] - `p1` - Ensure config scaffold files exist (create only if missing) - `inst-ensure-scaffold`
8. [x] - `p1` - Regenerate agent entry points - `inst-regenerate-agents`
9. [x] - `p1` - Run self-check to verify kit integrity (`run_self_check_from_meta`); include result in report, WARN if failed - `inst-self-check`
10. [x] - `p1` - **RETURN** update report with actions taken and self-check result - `inst-return-report`
11. [x] - `p1` - Imports, constants, and module setup for update command - `inst-update-imports`
12. [x] - `p1` - Display core whatsnew entries (cache vs installed) before applying update - `inst-whatsnew`
13. [x] - `p1` - Helper functions: ensure file creation, config README, auto-regenerate agents, read/show whatsnew - `inst-update-helpers`
14. [x] - `p1` - Human-friendly formatter for update report output - `inst-update-format-output`

### Manage Config via CLI

- [ ] `p2` - **ID**: `cpt-cypilot-flow-version-config-manage`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User runs `cpt config show` → displays current core.toml contents
- User runs `cpt config system add` → adds system definition with schema validation

**Steps**:
1. [ ] - `p2` - User invokes `cpt config <subcommand> [args]` - `inst-user-config`
2. [ ] - `p2` - Validate change against config schema - `inst-validate-schema`
3. [ ] - `p2` - Apply change to config file - `inst-apply-change`
4. [ ] - `p2` - **RETURN** summary of what was modified - `inst-return-config-summary`

## 3. Processes / Business Logic (CDSL)

### Update Pipeline

- [x] `p1` - **ID**: `cpt-cypilot-algo-version-config-update-pipeline`

1. [x] - `p1` - Replace `.core/` from cache - `inst-replace-core-algo`
2. [x] - `p1` - Detect and auto-restructure old directory layout - `inst-detect-layout-algo`
3. [x] - `p1` - Migrate `{cypilot_path}/config/core.toml` - `inst-migrate-config-algo`
4. [x] - `p1` - Migrate bundled kit references to GitHub sources (add `source` field) - `inst-migrate-kit-sources-algo`
5. [x] - `p1` - (Removed — no separate regen step; kit files are updated directly) - `inst-regen-algo`
6. [x] - `p1` - Ensure config scaffold - `inst-scaffold-algo`

### Layout Restructuring

- [x] `p1` - **ID**: `cpt-cypilot-algo-version-config-layout-restructure`

**Input**: Cypilot directory path

**Output**: Restructured directory layout or no-op if already new layout

**Detection**: Old layout is detected when `{cypilot_path}/.gen/kits/{slug}/` exists.

**Steps**:
1. [x] - `p1` - Backup affected directories - `inst-layout-backup`
2. [x] - `p1` - Move generated outputs: `.gen/kits/{slug}/` → `config/kits/{slug}/` - `inst-layout-move-gen`
3. [x] - `p1` - Remove old `kits/{slug}/` reference copies if present - `inst-layout-remove-refs`
4. [x] - `p1` - Remove `.gen/kits/` directory (preserve `.gen/AGENTS.md`, `.gen/SKILL.md`, `.gen/README.md`) - `inst-layout-clean-gen`
5. [x] - `p1` - Update `core.toml` kit registrations with new paths (`config/kits/{slug}`) - `inst-layout-update-core`
6. [x] - `p1` - **IF** any step fails, restore from backup and report error - `inst-layout-rollback`

### Compare Blueprint Versions (LEGACY)

- [x] `p1` - **ID**: `cpt-cypilot-algo-version-config-compare-versions`

> **LEGACY**: Blueprint version comparison is preserved for backward compatibility with v2/early-v3 installations. New kit updates use file-level diff.

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

- [x] `p1` - **ID**: `cpt-cypilot-state-version-config-installation`

```
[CURRENT] --new-cache-available--> [OUTDATED] --update--> [CURRENT]
[OUTDATED] --update-with-migration--> [MIGRATION_NEEDED] --manual-resolve--> [CURRENT]
```

## 5. Definitions of Done

### Update Command

- [x] `p1` - **ID**: `cpt-cypilot-dod-version-config-update`

- [x] - `p1` - `cpt update` replaces `.core/` from cache
- [x] - `p1` - `cpt update` detects old directory layout and auto-restructures (move generated outputs from `.gen/kits/` to `config/kits/`, remove old reference copies)
- [x] - `p1` - `cpt update` migrates bundled kit references to GitHub sources (versions < 3.0.8)
- [x] - `p1` - User config files in `config/` are NEVER overwritten
- [x] - `p1` - [LEGACY] Blueprint version comparison detects same, migration needed, and missing states
- [x] - `p1` - `--dry-run` shows what would be done without writing
- [x] - `p1` - `cpt update` regenerates `.gen/AGENTS.md` and `.gen/SKILL.md` after update
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
| Update Command | `skills/.../commands/update.py` | Update pipeline, layout restructuring, file-level kit diff |

## 7. Acceptance Criteria

- [x] `cpt update` refreshes `.core/` without touching user config
- [x] `cpt update` detects and auto-restructures old directory layout with backup and rollback
- [x] `cpt update` migrates bundled kit references to GitHub sources (versions < 3.0.8)
- [x] [LEGACY] Blueprint version comparison correctly identifies same, migration needed, and missing states
- [ ] `cpt config show` displays readable config summary
- [ ] Config migration preserves all user settings with backup
- [x] `cpt update` automatically runs self-check after update and reports WARN if integrity check fails
