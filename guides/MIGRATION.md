# V2 → V3 Migration Guide

This guide covers migrating a Cypilot v2 project (adapter-based, `artifacts.json`, legacy kit structure) to v3 (blueprint-based, `artifacts.toml`, three-directory layout).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [What Changes](#what-changes)
- [CLI Reference](#cli-reference)
- [Step-by-Step Walkthrough](#step-by-step-walkthrough)
- [Edge Cases & Prompts](#edge-cases--prompts)
  - [Custom Kits](#custom-kits)
  - [Submodule Core](#submodule-core)
  - [Non-Standard Paths](#non-standard-paths)
  - [Monorepo / Multi-System](#monorepo--multi-system)
  - [Custom AGENTS.md Rules](#custom-agentsmd-rules)
  - [Post-Migration Validation Failures](#post-migration-validation-failures)
  - [Rollback](#rollback)

---

## Prerequisites

1. **Update Cypilot** to the latest version before migrating:
   ```bash
   cpt update
   ```
2. **Commit or stash** any uncommitted changes in your project.
3. **Verify v2 is detected** with a dry run:
   ```bash
   cpt migrate --dry-run
   ```

## Quick Start

```bash
# 1. Preview the migration plan
cpt migrate --dry-run

# 2. Run the migration (interactive confirmation)
cpt migrate

# 3. Or skip confirmation
cpt migrate --yes

# 4. Convert any remaining JSON configs to TOML
cpt migrate-config
```

## What Changes

### Directory Structure

| V2 | V3 | Notes |
|---|---|---|
| `.cypilot/` (core submodule/clone) | `{install_dir}/.core/` | Read-only, from cache |
| `.cypilot-adapter/` (user config) | `{install_dir}/config/` | User-editable |
| — | `{install_dir}/.gen/` | Auto-generated |
| `.cypilot-adapter/artifacts.json` | `{install_dir}/config/artifacts.toml` | Systems & ignore only |
| `.cypilot-adapter/AGENTS.md` | `{install_dir}/config/AGENTS.md` | Path refs updated |
| `.cypilot-config.json` | `{install_dir}/config/core.toml` | Kits registered here |
| `.cypilot-adapter/kits/{slug}/` | `{install_dir}/config/kits/{slug}/` | Custom kits copied |

> **Cleanup**: After migration, `.cypilot-adapter/` and `.cypilot-config.json` are **deleted** (already in the backup).

> **Kit registration**: In v3, kits are registered **only** in `core.toml`, not in `artifacts.toml`. The `artifacts.toml` file contains only systems and ignore rules.

> **Target directory**: The migration preserves the original core path by default.
> If your v2 core was at `.cypilot`, the v3 install dir will also be `.cypilot`.
> Override with `--install-dir <path>` if needed.

### Kit Slugs

Kit slugs are **preserved as-is** during migration. No remapping occurs — if your v2 kit was `cf-sdlc`, it stays `cf-sdlc` in v3.

### What the Tool Does

1. **Detects** v2 installation (adapter dir, core path, install type)
2. **Creates backup** at `.cypilot-v2-backup-{timestamp}/`
3. **Cleans up** v2 core path (removes submodule, git clone, or plain dir)
4. **Initializes** v3 directory structure (`.core/`, `.gen/`, `config/`)
5. **Converts** `artifacts.json` → `artifacts.toml` (systems & ignore only)
6. **Converts** adapter `AGENTS.md` → `config/AGENTS.md` (updates path refs)
7. **Generates** `core.toml` with kit registration and project metadata
8. **Migrates kits** — copies kit files from adapter, converts `constraints.json` → `constraints.toml`
9. **Deletes** `.cypilot-adapter/` and `.cypilot-config.json` (already backed up)
10. **Injects** root `AGENTS.md` managed block
11. **Regenerates** agent entry points (`.windsurf/`, `.cursor/`, `.claude/`)
12. **Validates** migration completeness
13. **Rolls back** automatically on failure

## CLI Reference

### `cpt migrate`

```
Usage: migrate [--project-root PATH] [--install-dir PATH] [--yes] [--dry-run]

Options:
  --project-root PATH   Project root directory (default: current directory)
  --install-dir PATH    Cypilot directory relative to project root
                        (default: derived from v2 core path, fallback: cypilot)
  --yes                 Skip confirmation prompt
  --dry-run             Detect and show plan only, no changes
```

### `cpt migrate-config`

```
Usage: migrate-config [--project-root PATH]

Converts remaining .json config files to .toml in config/ and adapter directories.
Each file is converted independently — failure in one doesn't block others.
```

## Step-by-Step Walkthrough

### 1. Dry Run

```bash
cpt migrate --dry-run
```

Review the output:
- **Adapter path**: where your v2 config lives
- **Core path**: where your v2 core was (submodule, clone, or plain dir)
- **Core install type**: `SUBMODULE`, `GIT_CLONE`, `PLAIN_DIR`, or `ABSENT`
- **Systems**: number of systems in your artifacts registry
- **Kits**: list of kit slugs to migrate

### 2. Run Migration

```bash
cpt migrate
```

Review the plan and type `y` to proceed. The tool will:
- Create a timestamped backup
- Perform all conversion steps
- Validate the result
- Roll back automatically if validation fails

### 3. Post-Migration Checks

```bash
# Verify the new structure
ls -la {install_dir}/
ls -la {install_dir}/.core/
ls -la {install_dir}/.gen/
ls -la {install_dir}/config/

# Check config files
cat {install_dir}/config/core.toml       # kits registered here
cat {install_dir}/config/artifacts.toml   # systems & ignore only

# Verify adapter was cleaned up
[ ! -d .cypilot-adapter ] && echo 'OK: adapter removed' || echo 'WARN: adapter still present'
[ ! -f .cypilot-config.json ] && echo 'OK: config.json removed' || echo 'WARN: config.json still present'

# Run validation
cpt validate
```

### 4. Clean Up Remaining JSON

```bash
cpt migrate-config
```

### 5. Commit

```bash
git add -A
git commit -m "chore: migrate Cypilot v2 → v3"
```

---

## Edge Cases & Prompts

Below are prompts you can give to Cypilot (or any AI agent) to handle specific migration scenarios that the automated tool may not fully cover.

### Custom Kits

The migration tool copies custom kit files to `config/kits/{slug}/` and `.gen/kits/{slug}/`, and converts `constraints.json` → `constraints.toml` automatically. Templates and rules are **not** regenerated. After migration:

> **Prompt:**
> ```
> @cypilot I just migrated from v2 to v3. I have a custom kit "{kit-slug}" that was
> copied to config/kits/{kit-slug}/. Please:
> 1. Review the kit structure and check if it needs blueprint conversion
> 2. Convert any constraints.json to constraints.toml if not done
> 3. Check if the kit has @cpt:blueprint markers — if not, help me add them
> 4. Regenerate the kit outputs by running: cpt update --force
> ```

For kits with complex custom logic:

> **Prompt:**
> ```
> @cypilot My custom kit "{kit-slug}" has custom validation rules and artifact
> templates that were hand-written in v2. Help me convert them to the v3 blueprint
> format so they can be auto-generated by `cpt update`. Show me the diff of what
> would change.
> ```

### Submodule Core

If your v2 core was a git submodule (`.cypilot` tracked in `.gitmodules`):

The migration tool automatically:
- Runs `git submodule deinit .cypilot`
- Removes the submodule entry from `.gitmodules`
- Cleans up `.git/modules/.cypilot`

If the automatic cleanup fails:

> **Prompt:**
> ```
> @cypilot The v2→v3 migration failed to remove the .cypilot git submodule.
> Help me manually clean it up:
> 1. Remove the submodule from .gitmodules
> 2. Remove the submodule from .git/config
> 3. Remove .git/modules/.cypilot
> 4. Remove the .cypilot directory
> Then I'll re-run: cpt migrate
> ```

### Non-Standard Paths

If your project uses non-default paths (set via `.cypilot-config.json`):

```bash
# The tool reads .cypilot-config.json automatically
# But you can also override the target:
cpt migrate --install-dir my-custom-path
```

> **Prompt:**
> ```
> @cypilot My project uses a non-standard Cypilot layout:
> - Core at: {core-path}
> - Adapter at: {adapter-path}
> - Config at: .cypilot-config.json
>
> After running `cpt migrate`, verify that:
> 1. All path references in AGENTS.md are updated
> 2. The root AGENTS.md managed block points to the correct directory
> 3. Agent entry points (.windsurf/, .cursor/, .claude/) use correct paths
> ```

### Monorepo / Multi-System

If your `artifacts.json` has multiple systems:

> **Prompt:**
> ```
> @cypilot I migrated a monorepo with multiple systems from v2 to v3.
> Please verify:
> 1. All systems are present in config/artifacts.toml
> 2. Each system's autodetect rules and artifact paths are correct
> 3. The children hierarchy is preserved
> 4. Kit references are preserved (slugs are not remapped)
> ```

### Custom AGENTS.md Rules

If you had custom navigation rules in your adapter AGENTS.md:

> **Prompt:**
> ```
> @cypilot After migration, I need to review config/AGENTS.md to ensure my custom
> WHEN rules are still correct. Please:
> 1. Check that path references use {cypilot_path}/config/ prefix
> 2. Verify no legacy references to .cypilot-adapter remain
> 3. Check that artifacts.json references are updated to artifacts.toml
> 4. Ensure the rules are compatible with the new 3-directory layout
> ```

### Post-Migration Validation Failures

If the migration reports validation issues:

> **Prompt:**
> ```
> @cypilot My v2→v3 migration completed but validation reported these issues:
> {paste validation output}
>
> Help me fix each issue. For CRITICAL issues, explain what went wrong.
> For HIGH/MEDIUM issues, suggest the minimal fix.
> ```

### Rollback

If you need to manually restore from backup:

```bash
# Find the backup
ls -d .cypilot-v2-backup-*

# Restore adapter (deleted during migration)
cp -r .cypilot-v2-backup-{timestamp}/.cypilot-adapter .

# Restore core (if it was backed up)
cp -r .cypilot-v2-backup-{timestamp}/.cypilot .

# Restore config json (if it existed)
cp .cypilot-v2-backup-{timestamp}/.cypilot-config.json . 2>/dev/null

# Remove the v3 directory
rm -rf cypilot/  # or .cypilot/ depending on your install dir

# Restore .gitmodules if it was modified
git checkout .gitmodules
```

> **Prompt:**
> ```
> @cypilot The v2→v3 migration failed and automatic rollback didn't work.
> My backup is at: {backup-path}
> Help me manually restore the v2 state and clean up any partial v3 files.
> ```
