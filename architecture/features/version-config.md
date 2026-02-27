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

Enables project skill updates with config migration, and provides CLI commands for managing system definitions, ignore lists, and kit registrations. The update command refreshes `.core/` from cache, compares blueprint versions, regenerates `.gen/`, and ensures `config/` scaffold files exist without overwriting user content.

### 2. Purpose

Ensures teams can upgrade Cypilot without losing configuration or customizations. Config CLI commands eliminate manual TOML editing and enforce schema validation. Addresses PRD requirements for version management (`cpt-cypilot-fr-core-version`) and CLI configuration (`cpt-cypilot-fr-core-cli-config`).

### 3. Actors

| Actor | Role in Feature |
|-------|-----------------|
| `cpt-cypilot-actor-user` | Runs `cypilot update`, `cypilot config`, `cypilot migrate-config` |
| `cpt-cypilot-actor-cypilot-cli` | Executes update pipeline, config mutations, migration |

### 4. References

- **PRD**: [PRD.md](../PRD.md) — `cpt-cypilot-fr-core-version`, `cpt-cypilot-fr-core-cli-config`
- **Design**: [DESIGN.md](../DESIGN.md) — `cpt-cypilot-component-config-manager`, `cpt-cypilot-seq-update`
- **Dependencies**: `cpt-cypilot-feature-core-infra`, `cpt-cypilot-feature-blueprint-system`

## 2. Actor Flows (CDSL)

### Update Project Installation

- [x] `p1` - **ID**: `cpt-cypilot-flow-version-config-update`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User runs `cypilot update` → `.core/` refreshed from cache, `.gen/` regenerated from user blueprints, config scaffold ensured
- Blueprint versions match → user blueprints untouched
- Blueprint version higher in cache → warning displayed, user blueprints untouched

**Error Scenarios**:
- Cypilot not initialized → error with hint to run `cypilot init`
- Cache not available → error with hint to check network

**Steps**:
1. [x] - `p1` - User invokes `cypilot update [--project-root P] [--dry-run]` - `inst-user-update`
2. [x] - `p1` - Resolve project root and cypilot directory - `inst-resolve-project`
3. [x] - `p1` - Replace `.core/` from cache (always force-overwrite) - `inst-replace-core`
4. [x] - `p1` - Update kit reference copies (`cypilot/kits/{slug}/`) from cache - `inst-update-kit-refs`
5. [x] - `p1` - Compare blueprint versions (cache vs user `config/kits/{slug}/blueprints/`) - `inst-compare-versions`
6. - `p1` - **IF** same version → skip user blueprints - `inst-if-same-version`
7. - `p1` - **IF** higher version → WARN "migration needed", don't touch user blueprints - `inst-if-migration-needed`
8. - `p1` - **IF** missing → copy from cache (first install) - `inst-if-missing`
9. [x] - `p1` - Regenerate `.gen/` from user's blueprints (NOT from cache) - `inst-regenerate-gen`
10. [x] - `p1` - Ensure config scaffold files exist (create only if missing) - `inst-ensure-scaffold`
11. [x] - `p1` - Regenerate agent entry points - `inst-regenerate-agents`
12. [x] - `p1` - **RETURN** update report with actions taken - `inst-return-report`

### Manage Config via CLI

- [ ] `p2` - **ID**: `cpt-cypilot-flow-version-config-manage`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User runs `cypilot config show` → displays current core.toml contents
- User runs `cypilot config system add` → adds system definition with schema validation

**Steps**:
1. - `p2` - User invokes `cypilot config <subcommand> [args]` - `inst-user-config`
2. - `p2` - Validate change against config schema - `inst-validate-schema`
3. - `p2` - Apply change to config file - `inst-apply-change`
4. - `p2` - **RETURN** summary of what was modified - `inst-return-config-summary`

## 3. Processes / Business Logic (CDSL)

### Update Pipeline

- [x] `p1` - **ID**: `cpt-cypilot-algo-version-config-update-pipeline`

1. - `p1` - Replace `.core/` from cache - `inst-replace-core-algo`
2. - `p1` - Update kit reference copies from cache - `inst-update-refs-algo`
3. - `p1` - Compare blueprint versions using `_read_blueprint_versions()` and `_compare_versions()` - `inst-compare-algo`
4. - `p1` - Regenerate `.gen/` from user blueprints - `inst-regen-algo`
5. - `p1` - Ensure config scaffold - `inst-scaffold-algo`

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

- [x] `p1` - **ID**: `cpt-cypilot-dod-version-config-update`

- [x] - `p1` - `cypilot update` replaces `.core/` from cache
- [x] - `p1` - `cypilot update` regenerates `.gen/` from user blueprints
- [x] - `p1` - User config files in `config/` are NEVER overwritten
- [x] - `p1` - Blueprint version comparison detects same, migration needed, and missing states
- [x] - `p1` - `--dry-run` shows what would be done without writing

### Config CLI Commands

- [ ] `p2` - **ID**: `cpt-cypilot-dod-version-config-cli`

- [ ] - `p2` - `cypilot config show` displays current configuration
- [ ] - `p2` - `cypilot config system add/remove` manages system definitions
- [ ] - `p2` - Schema validation rejects invalid changes before writing

### Config Migration

- [ ] `p2` - **ID**: `cpt-cypilot-dod-version-config-migration`

- [ ] - `p2` - `cypilot migrate-config` migrates legacy JSON configs to TOML
- [ ] - `p2` - Backup created before any migration
- [ ] - `p2` - User settings preserved across version upgrades

## 6. Implementation Modules

| Module | Path | Responsibility |
|--------|------|----------------|
| Update Command | `skills/.../commands/update.py` | Update pipeline, blueprint version comparison, `.gen/` regeneration |

## 7. Acceptance Criteria

- [x] `cypilot update` refreshes `.core/` and regenerates `.gen/` without touching user config
- [x] Blueprint version comparison correctly identifies same, migration needed, and missing states
- [ ] `cypilot config show` displays readable config summary
- [ ] Config migration preserves all user settings with backup
