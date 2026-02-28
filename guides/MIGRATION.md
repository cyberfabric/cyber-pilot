# V2 → V3 Migration Guide

This guide covers migrating a Cypilot v2 project (adapter-based, `artifacts.json`, legacy kit structure) to v3 (blueprint-based, `artifacts.toml`, three-directory layout).

## Table of Contents

- [V2 → V3 Migration Guide](#v2--v3-migration-guide)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Quick Start](#quick-start)
  - [What Changes](#what-changes)
    - [Directory Structure](#directory-structure)
    - [Kit Slugs](#kit-slugs)
    - [What the Tool Does](#what-the-tool-does)
  - [CLI Reference](#cli-reference)
    - [`cpt migrate`](#cpt-migrate)
    - [`cpt migrate-config`](#cpt-migrate-config)
  - [Step-by-Step Walkthrough](#step-by-step-walkthrough)
    - [1. Dry Run](#1-dry-run)
    - [2. Run Migration](#2-run-migration)
    - [3. Post-Migration Checks](#3-post-migration-checks)
    - [4. Clean Up Remaining JSON](#4-clean-up-remaining-json)
  - [Post-Migration AI Validation](#post-migration-ai-validation)
    - [What the Deterministic Migration Does NOT Check](#what-the-deterministic-migration-does-not-check)
    - [Validation Prompt](#validation-prompt)
    - [Interpreting Results](#interpreting-results)
  - [Guided Fixes](#guided-fixes)
    - [Legacy Path Fixes](#legacy-path-fixes)
    - [Autodetect Fixes](#autodetect-fixes)
    - [Blueprint Conversion](#blueprint-conversion)
    - [Validation Fixes](#validation-fixes)
    - [Gitignore Fixes](#gitignore-fixes)
    - [5. Regenerate and Commit](#5-regenerate-and-commit)
  - [Edge Cases \& Prompts](#edge-cases--prompts)
    - [Custom Kits](#custom-kits)
    - [Submodule Core](#submodule-core)
    - [Non-Standard Paths](#non-standard-paths)
    - [Monorepo / Multi-System](#monorepo--multi-system)
    - [Custom AGENTS.md Rules](#custom-agentsmd-rules)
    - [Post-Migration Validation Failures](#post-migration-validation-failures)
    - [Rollback](#rollback)

---

## Prerequisites

1. **Update the CLI** to the latest version (`cpt migrate` uses the cached skill bundle, which the proxy updates automatically):
   ```bash
   pipx install --force git+https://github.com/cyberfabric/cyber-pilot.git
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

---

## Post-Migration AI Validation

The deterministic migration handles structure, file conversion, and path rewriting. However, it **cannot** verify semantic correctness — things like stale path references in project docs, broken WHEN rule logic, missing blueprint markers, or CI configs pointing to old directories.

Use the prompt below **immediately after** step 4 (migrate-config) to catch what the tool missed.

### What the Deterministic Migration Does NOT Check

| Category | What can slip through | Why it matters |
|---|---|---|
| **Legacy path references** | `.cypilot-adapter/`, `.cypilot/`, `{cypilot_adapter_path}` in docs, scripts, CI, hooks | Broken tooling, wrong file loading |
| **WHEN rule semantics** | Path substitution is syntactic — rule *logic* may be stale or context-wrong | Agent loads wrong files or skips rules |
| **autodetect paths** | `artifacts_root`, `system_root`, `codebase` paths in `artifacts.toml` | Validation and artifact discovery fail |
| **Blueprint markers** | Custom kits have no `@cpt:blueprint` markers → `.gen/` regeneration skips them | Kit outputs not regenerated |
| **Cross-references** | Artifact IDs, `@cpt-*` traceability markers referencing moved files | Broken traceability |
| **Kit outputs** | Templates, rules, checklists are copied as-is, not regenerated | Outdated kit output format |
| **External tooling** | CI/CD pipelines, git hooks, Makefiles referencing old paths | Build/deploy failures |
| **`.gitignore`** | Old patterns may not cover new dirs; new dirs may be ignored accidentally | Files tracked or untracked incorrectly |

### Validation Prompt

Give this prompt to Cypilot (or any AI agent) **after** running the deterministic migration:

> **Prompt:**
> ```
> @cypilot I just completed the deterministic v2 → v3 migration.
> My install directory is: {install_dir}
>
> Run a semantic validation of the migration. For EACH category below,
> report PASS or FAIL with evidence:
>
> 1. LEGACY PATH SCAN
>    Search the ENTIRE project for stale v2 references:
>    - Strings: `.cypilot-adapter`, `.cypilot-config.json`, `cypilot-agents.json`
>    - Variables: `{cypilot_adapter_path}`, `cypilotAdapterPath`, `cypilotCorePath`
>    - Old path patterns: references to the v2 core path outside {install_dir}/
>    Scan: *.md, *.toml, *.json, *.yaml, *.yml, *.sh, *.py, Makefile, Dockerfile,
>          .github/workflows/*, .gitignore, .git/hooks/*
>    Report: file, line number, matched string for each hit.
>
> 2. WHEN RULE AUDIT
>    Open {install_dir}/config/AGENTS.md and verify:
>    - Every path in WHEN/ALWAYS clauses resolves to an existing file
>    - No references to `artifacts.json` (should be `artifacts.toml`)
>    - No references to `{cypilot_adapter_path}` (should be `{cypilot_path}/config`)
>    - No references to directories outside {install_dir}/
>    Report: each rule line, PASS/FAIL, and the resolved target path.
>
> 3. AUTODETECT PATH CHECK
>    Open {install_dir}/config/artifacts.toml and for each system's autodetect rules:
>    - Verify `system_root` directory exists
>    - Verify `artifacts_root` directory exists
>    - Verify each artifact path pattern matches at least one file
>    - Verify each `codebase` path exists
>    Report: system slug, rule index, field, PASS/FAIL.
>
> 4. BLUEPRINT MARKER CHECK
>    For each kit in {install_dir}/config/kits/:
>    - Check if kit has a blueprints/ subdirectory with .md files
>    - Check if each blueprint has a `@cpt:blueprint` TOML block
>    - If no blueprints exist, flag as NEEDS_CONVERSION
>    Report: kit slug, blueprint count, marker status.
>
> 5. KIT OUTPUT FRESHNESS
>    Run: cpt validate
>    Report the full output. If validation passes, report PASS.
>    If it fails, list each issue.
>
> 6. EXTERNAL TOOLING SCAN
>    Search for references to old Cypilot paths in:
>    - CI configs: .github/workflows/*.yml, .gitlab-ci.yml, Jenkinsfile
>    - Build files: Makefile, package.json scripts, pyproject.toml scripts
>    - Git hooks: .git/hooks/*, .husky/*
>    - Docker: Dockerfile*, docker-compose*.yml
>    Report: file, line, matched reference.
>
> 7. GITIGNORE CHECK
>    Open .gitignore and verify:
>    - {install_dir}/.core/ is NOT ignored (must be tracked in git)
>    - {install_dir}/.gen/ is NOT ignored (must be tracked in git)
>    - {install_dir}/config/ is NOT ignored (must be tracked in git)
>    - Old v2 ignore patterns (`.cypilot`, `.cypilot-adapter`) are removed or updated
>    Report: each relevant line, PASS/FAIL.
>
> Format the output as a summary table:
> | # | Category | Status | Issues |
> Then list details for each FAIL.
> ```

### Interpreting Results

- **All PASS** → Migration is clean. Proceed to `cpt update --force` to regenerate `.gen/`.
- **FAIL in categories 1, 2, 6** → Path reference issues. Use the **Legacy Path Fixes** prompt below.
- **FAIL in category 3** → Autodetect configuration issue. Use the **Autodetect Fixes** prompt below.
- **FAIL in category 4** → Kit needs blueprint conversion. Use the **Blueprint Conversion** prompt below.
- **FAIL in category 5** → Validation errors. Use the **Validation Fixes** prompt below.
- **FAIL in category 7** → Gitignore issue. Use the **Gitignore Fixes** prompt below.

---

## Guided Fixes

Use these prompts to fix issues found by the validation above. Each prompt targets a specific category, uses imperative instructions, and includes verification criteria.

### Legacy Path Fixes

> **Prompt:**
> ```
> @cypilot The post-migration validation found stale v2 path references.
> Here are the hits:
> {paste the FAIL details from categories 1, 2, and 6}
>
> For EACH stale reference:
> 1. Determine the correct v3 replacement:
>    - `.cypilot-adapter/` → `{install_dir}/config/`
>    - `.cypilot/` (as core) → `{install_dir}/.core/`
>    - `{cypilot_adapter_path}` → `{cypilot_path}/config`
>    - `artifacts.json` → `artifacts.toml`
>    - `.cypilot-config.json` → `{install_dir}/config/core.toml`
> 2. Apply the replacement. Preserve surrounding context.
> 3. If the reference is in a WHEN rule, verify the target file exists after replacement.
> 4. If the reference is in CI/build config, verify the command still works.
>
> After all fixes, re-run the legacy path scan (categories 1, 2, 6) and confirm all PASS.
> Do NOT commit — show me the diff first.
> ```

### Autodetect Fixes

> **Prompt:**
> ```
> @cypilot The post-migration validation found broken autodetect paths in artifacts.toml.
> Here are the failing rules:
> {paste the FAIL details from category 3}
>
> For EACH failing autodetect rule:
> 1. Open {install_dir}/config/artifacts.toml
> 2. Locate the system and autodetect entry by slug and index
> 3. Check if the path simply needs a prefix update (v2 → v3 directory move)
> 4. If the target directory genuinely doesn't exist, flag it and ask me
> 5. Fix paths that are resolvable
>
> After fixes, re-run autodetect path validation and confirm all PASS.
> Show the before/after for each changed path.
> ```

### Blueprint Conversion

> **Prompt:**
> ```
> @cypilot The post-migration validation found kits without blueprint markers.
> Kits flagged as NEEDS_CONVERSION:
> {paste the FAIL details from category 4}
>
> For EACH kit that needs conversion:
> 1. List all .md files in {install_dir}/config/kits/{slug}/
> 2. Identify which files are artifact templates, rules, or checklists
> 3. For each file, determine the appropriate @cpt:blueprint marker:
>    - artifact = the artifact KIND this blueprint defines
>    - kit = the kit slug
>    - version = 1
> 4. Show me the proposed @cpt:blueprint TOML block for each file
> 5. Wait for my approval before inserting markers
>
> After I approve, insert the markers and run: cpt update --force
> Verify .gen/kits/{slug}/ is regenerated correctly.
> ```

### Validation Fixes

> **Prompt:**
> ```
> @cypilot The post-migration `cpt validate` reported these issues:
> {paste the full validation output from category 5}
>
> For EACH validation issue:
> 1. Classify the root cause:
>    - STRUCTURE: missing section, wrong heading level
>    - CROSS-REF: broken ID reference, missing artifact
>    - TRACEABILITY: @cpt-* marker pointing to moved/renamed file
>    - CONFIG: malformed TOML, missing required field
> 2. Determine if the fix is in an artifact file or a config file
> 3. Apply the minimal fix. Do NOT rewrite entire files.
> 4. For traceability issues: update the @cpt-* marker path, not the code
>
> After fixes, re-run: cpt validate
> Confirm exit code 0 (PASS). If issues remain, report them.
> ```

### Gitignore Fixes

> **Prompt:**
> ```
> @cypilot The post-migration .gitignore check found issues:
> {paste the FAIL details from category 7}
>
> Apply these rules to .gitignore:
> 1. VERIFY not ignored (all three directories MUST be tracked in git):
>    - `{install_dir}/.core/` — read-only but committed
>    - `{install_dir}/.gen/` — auto-generated but committed
>    - `{install_dir}/config/` — user-editable, committed
> 2. REMOVE any .gitignore entries that would ignore these directories
> 3. REMOVE or UPDATE stale v2 patterns:
>    - Old `.cypilot` ignore entries that no longer apply
>    - Old `.cypilot-adapter` ignore entries
> 4. KEEP any user-added patterns unrelated to Cypilot
>
> Show the diff before committing.
> ```

### 5. Regenerate and Commit

After all validation checks pass and fixes are applied, finalize the migration:

```bash
# Regenerate .gen/ from corrected blueprints and config
cpt update --force

# Re-validate everything
cpt validate

# Commit the complete migration (deterministic + AI-validated fixes)
git add -A
git commit -m "chore: migrate Cypilot v2 → v3"
```

> **Note**: This is the single commit point for the entire migration. Do not commit between the deterministic steps and the AI validation — keep everything in one atomic commit.

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
