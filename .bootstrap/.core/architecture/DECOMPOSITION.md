# Decomposition: Cypilot



<!-- toc -->

- [1. Overview](#1-overview)
- [2. Entries](#2-entries)
  - [2.1 Core Infrastructure ⏳ HIGH](#21-core-infrastructure-high)
  - [2.2 Kit Management ⏳ HIGH](#22-kit-management-high)
  - [2.3 Traceability & Validation ⏳ HIGH](#23-traceability-validation-high)
  - [2.4 SDLC Kit & Artifact Pipeline (EXTRACTED) ⏳ HIGH](#24-sdlc-kit-artifact-pipeline-extracted-high)
  - [2.5 Agent Integration & Workflows ✅ DONE](#25-agent-integration-workflows-done)
  - [2.6 PR Workflows (EXTRACTED) ⏳ MEDIUM](#26-pr-workflows-extracted-medium)
  - [2.7 Version & Config Management ⏳ MEDIUM](#27-version-config-management-medium)
  - [2.8 Developer Experience ⏳ LOW](#28-developer-experience-low)
  - [2.9 Advanced SDLC Workflows (EXTRACTED) ⏳ LOW](#29-advanced-sdlc-workflows-extracted-low)
  - [2.10 V2 → V3 Migration ⏳ HIGH](#210-v2-v3-migration-high)
  - [2.11 Spec Coverage ⏳ HIGH](#211-spec-coverage-high)
- [3. Feature Dependencies](#3-feature-dependencies)

<!-- /toc -->

## 1. Overview

Cypilot DESIGN is decomposed into features organized around architectural layers and functional cohesion. The decomposition follows a dependency order where core infrastructure enables the kit system and validation, which in turn enable agent integration and advanced workflows.

**Decomposition Strategy**:
- Features grouped by architectural layer and functional cohesion (related components together)
- Dependencies minimize coupling between features — each feature is independently implementable given its dependencies
- SDLC-specific features (F4, F6, F9) have been **extracted** to the SDLC kit repository (`cyberfabric/cyber-pilot-kit-sdlc`) per `cpt-cypilot-adr-extract-sdlc-kit`
- Core features (F1–F3, F5, F7–F8, F10–F11) cover all core functional requirements


## 2. Entries

**Overall implementation status:**

- [ ] `p1` - **ID**: `cpt-cypilot-status-overall`

### 2.1 [Core Infrastructure](features/core-infra.md) ⏳ HIGH

- [x] `p1` - **ID**: `cpt-cypilot-feature-core-infra`

- **Purpose**: Provide the foundation layer — global CLI proxy, skill engine command dispatch, config directory management, and project initialization — upon which all other features are built.

- **Depends On**: None

- **Scope**:
  - Global CLI proxy with local cache (`~/.cypilot/cache/`), automatic skill bundle download from GitHub on first run, command routing, background version checks
  - Skill engine: command dispatch, JSON output serialization, exit code conventions (0/1/2)
  - Config manager: `{cypilot_path}/config/core.toml` CRUD, schema validation, deterministic TOML serialization
  - Project initialization: interactive bootstrapper, root system definition (name/slug from directory), per-kit config output directory selection, `{cypilot_path}/config/core.toml` creation (with kit config paths), `{cypilot_path}/config/artifacts.toml` with default autodetect rules, `{cypilot_path}/kits/` directory creation, root `AGENTS.md` injection, `{cypilot_path}/config/AGENTS.md` with default WHEN rules

- **Out of scope**:
  - Kit installation logic (Feature 2)
  - Validation logic (Feature 3)
  - Agent entry point generation (Feature 5)
  - CLI config subcommands beyond init (Feature 7)

- **Requirements Covered**:

  - `p1` - `cpt-cypilot-fr-core-installer`
  - `p1` - `cpt-cypilot-fr-core-init`
  - `p1` - `cpt-cypilot-fr-core-config`
  - `p1` - `cpt-cypilot-fr-core-skill-engine`
  - `p1` - `cpt-cypilot-nfr-adoption-usability`
  - `p1` - `cpt-cypilot-nfr-reliability-recoverability`

- **Design Principles Covered**:

  - `p1` - `cpt-cypilot-principle-determinism-first`
  - `p1` - `cpt-cypilot-principle-occams-razor`
  - `p2` - `cpt-cypilot-principle-tool-managed-config`
  - `p1` - `cpt-cypilot-principle-zero-harm`

- **Design Constraints Covered**:

  - `p1` - `cpt-cypilot-constraint-python-stdlib`
  - `p1` - `cpt-cypilot-constraint-cross-platform`
  - `p2` - `cpt-cypilot-constraint-git-project-heuristics`

- **Domain Model Entities**:
  - System
  - Config
  - Kit (registration only)

- **Design Components**:

  - `p1` - `cpt-cypilot-component-cli-proxy`
  - `p1` - `cpt-cypilot-component-skill-engine`
  - `p1` - `cpt-cypilot-component-config-manager`

- **API**:
  - `cpt init [--dir DIR] [--agents AGENTS]`
  - `cpt config show`

- **Sequences**:
  - `cpt-cypilot-seq-init`

- **Data**:
  - `{cypilot_path}/config/core.toml` — system definitions, kit registrations, ignore lists
  - `{cypilot_path}/config/artifacts.toml` — artifact registry with autodetect rules


### 2.2 [Kit Management](features/kit-management.md) ⏳ HIGH

- [x] `p1` - **ID**: `cpt-cypilot-feature-blueprint-system`

- **Purpose**: Manage kit lifecycle — installation, file-level diff updates, interactive conflict resolution, SKILL/AGENTS composition, and kit structural validation. Kits are direct file packages (per `cpt-cypilot-adr-remove-blueprint-system`).

- **Depends On**: `cpt-cypilot-feature-core-infra`

- **Scope**:
  - Kit Manager: install kits (copy files from source into `{cypilot_path}/config/kits/{slug}/`), register in `core.toml`
  - Update model: force mode (full overwrite) and interactive mode (file-level diff — compare each file in new version against user's installed copy, present unified diffs with accept/decline/accept-all/decline-all/modify prompts)
  - Resource Diff Engine: interactive conflict resolution for kit file updates (`accept-file`, `reject-file`, `accept-all`, `reject-all`, `modify` with git-style conflict markers)
  - Kit config relocation: `cpt kit move-config <slug>` moves kit config directory, updates `core.toml`
  - SKILL composition: collect kit `SKILL.md` files and write to `{cypilot_path}/config/SKILL.md`
  - System prompt composition: collect kit AGENTS.md content and append to `{cypilot_path}/config/AGENTS.md`
  - Kit structural validation: verify required files (`conf.toml`, `constraints.toml`, `artifacts/` directory)

- **Out of scope**:
  - Custom plugin hooks and CLI subcommands (planned p2 plugin system)
  - Validation of kit file content (Feature 3)

- **Requirements Covered**:

  - `p1` - `cpt-cypilot-fr-core-kits`
  - `p1` - `cpt-cypilot-fr-core-resource-diff`

- **Design Principles Covered**:

  - `p1` - `cpt-cypilot-principle-kit-centric`
  - `p1` - `cpt-cypilot-principle-plugin-extensibility`
  - `p1` - `cpt-cypilot-principle-dry`
  - `p2` - `cpt-cypilot-principle-no-manual-maintenance`

- **Design Constraints Covered**:

  - `p1` - `cpt-cypilot-constraint-markdown-contract`

- **Domain Model Entities**:
  - Kit
  - Constraint
  - Workflow

- **Design Components**:

  - `p1` - `cpt-cypilot-component-kit-manager`

- **API**:
  - `cypilot kit install <path>`
  - `cypilot kit update [--force]`
  - `cypilot kit move-config <slug>`

- **Sequences**:

  None (kit file operations are invoked internally by kit install/update)

- **Data**:
  - `{cypilot_path}/config/kits/{slug}/conf.toml` — kit version metadata
  - `{cypilot_path}/config/kits/{slug}/SKILL.md` — per-kit skill (user-editable)
  - `{cypilot_path}/config/kits/{slug}/constraints.toml` — kit-wide structural constraints (user-editable)
  - `{cypilot_path}/config/kits/{slug}/artifacts/{KIND}/` — per-artifact files (user-editable)
  - `{cypilot_path}/config/kits/{slug}/codebase/` — codebase rules and checklist (user-editable)
  - `{cypilot_path}/config/kits/{slug}/workflows/` — generated workflow files (user-editable)
  - `{cypilot_path}/config/kits/{slug}/scripts/` — kit scripts and prompts (user-editable)


### 2.3 [Traceability & Validation](features/traceability-validation.md) ⏳ HIGH

- [x] `p1` - **ID**: `cpt-cypilot-feature-traceability-validation`

- **Purpose**: Provide the deterministic quality gate — ID scanning, cross-reference resolution, structural validation, and constraint enforcement — that catches issues without relying on LLMs.

- **Depends On**: `cpt-cypilot-feature-core-infra`

- **Scope**:
  - Traceability Engine: scan artifacts for ID definitions and references, scan code for `@cpt-*` tags, resolve cross-references, query commands (list-ids, list-id-kinds, where-defined, where-used, get-content), ID versioning (`-vN`)
  - Validator: template structure compliance, ID format validation, priority markers, placeholder detection, cross-reference validation (covered_by, checked consistency), constraint enforcement from `constraints.toml`
  - Cross-artifact validation: load all registered artifacts, compare definitions vs references per constraints rules
  - CDSL: parse instruction markers for implementation tracking
  - Single-pass scanning for ≤3s performance

- **Out of scope**:
  - Semantic validation (checklist review done by AI agents)
  - Modifying artifacts (read-only analysis)
  - Kit-specific validation hooks (planned p2)

- **Requirements Covered**:

  - `p1` - `cpt-cypilot-fr-core-traceability`
  - `p1` - `cpt-cypilot-fr-core-cdsl`
  - `p1` - `cpt-cypilot-nfr-validation-performance`
  - `p1` - `cpt-cypilot-nfr-security-integrity`

- **Design Principles Covered**:

  - `p1` - `cpt-cypilot-principle-determinism-first`
  - `p1` - `cpt-cypilot-principle-traceability-by-design`
  - `p1` - `cpt-cypilot-principle-ci-automation-first`
  - `p2` - `cpt-cypilot-principle-machine-readable`

- **Design Constraints Covered**:

  - `p1` - `cpt-cypilot-constraint-no-weakening`

- **Domain Model Entities**:
  - Identifier
  - Artifact
  - Constraint

- **Design Components**:

  - `p1` - `cpt-cypilot-component-validator`
  - `p1` - `cpt-cypilot-component-traceability-engine`

- **API**:
  - `cpt validate --artifact <path>`
  - `cpt validate`
  - `cpt list-ids [--kind K] [--pattern P]`
  - `cpt where-defined --id <id>`
  - `cpt where-used --id <id>`
  - `cpt get-content --id <id>`

- **Sequences**:
  - `cpt-cypilot-seq-validate`
  - `cpt-cypilot-seq-traceability-query`

- **Data**:
  - In-memory ID index (definitions + references, built from filesystem scan)


### 2.4 SDLC Kit & Artifact Pipeline (EXTRACTED) ⏳ HIGH

> **EXTRACTED per `cpt-cypilot-adr-extract-sdlc-kit`**: This feature has been moved to the SDLC kit repository (`cyberfabric/cyber-pilot-kit-sdlc`). All SDLC-specific scope, requirements, components, and data are now owned by the kit's own repository.


### 2.5 [Agent Integration & Workflows](features/agent-integration.md) ✅ DONE

- [x] `p1` - **ID**: `cpt-cypilot-feature-agent-integration`

- **Purpose**: Bridge Cypilot's unified skill system to diverse AI coding assistants by generating agent-native entry points and providing generic generate/analyze workflows.

- **Depends On**: `cpt-cypilot-feature-core-infra`

- **Scope**:
  - Agent Generator: produce entry points in each agent's native format
  - Supported agents: Windsurf, Cursor, Claude, Copilot, OpenAI
  - SKILL.md composition: collect `@cpt:skill` sections and assemble into main SKILL.md
  - Full overwrite on each invocation; `--agent` flag for single-agent regeneration
  - Generic workflows: `{cypilot_path}/.core/workflows/generate.md` and `{cypilot_path}/.core/workflows/analyze.md` with common execution protocol

- **Out of scope**:
  - Agent-specific state persistence
  - Kit-specific workflow content (provided by Feature 4)

- **Requirements Covered**:

  - `p1` - `cpt-cypilot-fr-core-agents`
  - `p1` - `cpt-cypilot-fr-core-workflows`

- **Design Principles Covered**:

  - `p2` - `cpt-cypilot-principle-skill-documented`
  - `p2` - `cpt-cypilot-principle-no-manual-maintenance`

- **Design Constraints Covered**:

  None

- **Domain Model Entities**:
  - AgentEntryPoint
  - Workflow

- **Design Components**:

  - `p1` - `cpt-cypilot-component-agent-generator`

- **API**:
  - `cpt agents [--agent A]`

- **Sequences**:
  - `cpt-cypilot-seq-generate-workflow`

- **Data**:
  - `.windsurf/workflows/`, `.cursor/rules/`, `.claude/commands/`, `.github/prompts/`


### 2.6 PR Workflows (EXTRACTED) ⏳ MEDIUM

> **EXTRACTED per `cpt-cypilot-adr-extract-sdlc-kit`**: This feature has been moved to the SDLC kit repository (`cyberfabric/cyber-pilot-kit-sdlc`). PR review and status workflows are now provided by the SDLC kit as kit workflows.


### 2.7 [Version & Config Management](features/version-config.md) ⏳ MEDIUM

- [ ] `p2` - **ID**: `cpt-cypilot-feature-version-config`

- **Purpose**: Enable project skill updates with config migration, and provide CLI commands for managing system definitions, ignore lists, and kit registrations.

- **Depends On**: `cpt-cypilot-feature-core-infra`

- **Scope**:
  - Update command: copy cached skill to project, detect and auto-restructure old directory layout, migrate `{cypilot_path}/config/core.toml`, migrate bundled kit references to GitHub sources (versions < 3.0.8), regenerate agent entry points
  - Layout restructuring: automatically detect old directory layout during `cpt update` and restructure (move generated outputs from `.gen/kits/` to `config/kits/`, remove old reference copies)
  - Config migration: backup before applying, preserve all user settings across versions
  - CLI config interface: `config system add/remove`, dry-run mode
  - Schema validation before all config writes
  - Version information: `--version` flag

- **Out of scope**:
  - Kit-specific CLI subcommands (planned p2 plugin)
  - Initial project setup (Feature 1)

- **Requirements Covered**:

  - `p2` - `cpt-cypilot-fr-core-version`
  - `p1` - `cpt-cypilot-fr-core-layout-migration`
  - `p2` - `cpt-cypilot-fr-core-cli-config`
  - `p1` - `cpt-cypilot-nfr-reliability-recoverability`

- **Design Principles Covered**:

  - `p2` - `cpt-cypilot-principle-tool-managed-config`
  - `p2` - `cpt-cypilot-principle-no-manual-maintenance`

- **Design Constraints Covered**:

  None

- **Domain Model Entities**:
  - Config

- **Design Components**:

  Components reused from Feature 1 (`config-manager`, `skill-engine`) and Feature 2 (`kit-manager`)

- **API**:
  - `cpt update [--check]`
  - `cpt migrate-config`
  - `cpt config system add <name> [--kit K]`
  - `cpt config system remove <name>`
  - `cpt --version`

- **Sequences**:
  - `cpt-cypilot-seq-update`

- **Data**:
  - `{cypilot_path}/config/core.toml` — migrated config with version field


### 2.8 [Developer Experience](features/developer-experience.md) ⏳ LOW

- [ ] `p2` - **ID**: `cpt-cypilot-feature-developer-experience`

- **Purpose**: Enhance developer productivity with IDE integration, environment health checks, and utility commands for daily use.

- **Depends On**: `cpt-cypilot-feature-traceability-validation`

- **Scope**:
  - VS Code extension: ID syntax highlighting, go-to-definition, real-time validation, autocompletion, hover info, CodeLens, traceability tree view, quick fixes — all delegated to `cpt validate`
  - `cpt doctor`: check Python version, git, gh CLI, agents, config integrity
  - `cpt self-check`: validate examples against templates
  - `cpt hook install/uninstall`: git pre-commit hooks for validation
  - `cpt completions install`: shell completion scripts for bash/zsh/fish

- **Out of scope**:
  - VS Code extension publishing (separate repo/process)
  - IDE-specific validation logic (delegated to skill)

- **Requirements Covered**:

  - `p2` - `cpt-cypilot-fr-core-vscode-plugin`
  - `p2` - `cpt-cypilot-fr-core-template-qa`
  - `p2` - `cpt-cypilot-fr-core-doctor`
  - `p3` - `cpt-cypilot-fr-core-hooks`
  - `p3` - `cpt-cypilot-fr-core-completions`

- **Design Principles Covered**:

  - `p2` - `cpt-cypilot-principle-machine-readable`
  - `p1` - `cpt-cypilot-principle-zero-harm`

- **Design Constraints Covered**:

  None

- **Domain Model Entities**:
  - Identifier (for IDE features)

- **Design Components**:

  Components reused from Feature 3 (`validator`, `traceability-engine`)

- **API**:
  - `cpt doctor`
  - `cpt self-check`
  - `cpt hook install`
  - `cpt hook uninstall`
  - `cpt completions install`

- **Sequences**:

  None

- **Data**:

  None


### 2.9 Advanced SDLC Workflows (EXTRACTED) ⏳ LOW

> **EXTRACTED per `cpt-cypilot-adr-extract-sdlc-kit`**: This feature has been moved to the SDLC kit repository (`cyberfabric/cyber-pilot-kit-sdlc`). Code generation, brownfield support, feature lifecycle, PR config, and quickstart guides are now provided by the SDLC kit.


### 2.10 [V2 → V3 Migration](features/v2-v3-migration.md) ⏳ HIGH

- [x] `p1` - **ID**: `cpt-cypilot-feature-v2-v3-migration`

- **Purpose**: Migrate existing Cypilot v2 projects (adapter-based, `artifacts.toml`, legacy kit structure) to v3 (file-package kits, `artifacts.toml`, global CLI installer, `config/` directory) with zero data loss.

- **Depends On**: `cpt-cypilot-feature-core-infra`, `cpt-cypilot-feature-traceability-validation`

- **Scope**:
  - Detect v2 installation: identify `.cypilot-adapter/` directory, `artifacts.toml`, legacy kit paths
  - Convert `artifacts.toml` → `{cypilot_path}/config/artifacts.toml`: map systems, artifacts, codebase, autodetect, ignore rules to TOML format
  - Convert legacy adapter directory → `config/` structure: migrate adapter-level specs to `config/sysprompts/`
  - Generate `{cypilot_path}/config/core.toml` from legacy config: extract system definitions, kit registrations
  - Create `{cypilot_path}/config/AGENTS.md` from legacy adapter `AGENTS.md`: convert WHEN rules, update paths
  - Migrate kit resources: install SDLC kit from cache, copy kit files into `{cypilot_path}/config/kits/sdlc/`
  - Inject root `AGENTS.md` managed block with new `{cypilot_path}/config/AGENTS.md` path
  - Regenerate all agent entry points for v3 structure
  - Preserve all existing artifact files and ID definitions unchanged
  - Validate migration completeness: all artifacts still resolve, all IDs still discoverable
  - Rollback support: backup v2 state before migration

- **Out of scope**:
  - Ongoing v3 updates after migration (Feature 7)
  - Manual migration of custom scripts or extensions
  - Supporting v2 and v3 simultaneously in the same project

- **Requirements Covered**:

  - `p1` - `cpt-cypilot-fr-core-init`
  - `p1` - `cpt-cypilot-fr-core-config`

- **Design Principles Covered**:

  - `p1` - `cpt-cypilot-principle-zero-harm`
  - `p2` - `cpt-cypilot-principle-no-manual-maintenance`

- **Design Constraints Covered**:

  None

- **Domain Model Entities**:
  - Config
  - System
  - Artifact

- **Design Components**:

  - `p1` - `cpt-cypilot-component-config-manager`
  - `p1` - `cpt-cypilot-component-kit-manager`
  - `p1` - `cpt-cypilot-component-skill-engine`

- **API**:
  - `cpt migrate` (or detected automatically during `cpt init` in v2 project)
  - `cpt migrate-config`

- **Sequences**:

  None (migration is a one-time init-like flow)

- **Data**:
  - `.cypilot-adapter/` → `config/` (converted)
  - `artifacts.toml` → `{cypilot_path}/config/artifacts.toml` (converted)
  - `.cypilot-adapter/AGENTS.md` → `{cypilot_path}/config/AGENTS.md` (converted)
  - `.cypilot-adapter/specs/` → `config/sysprompts/` (converted)


### 2.11 [Spec Coverage](features/spec-coverage.md) ⏳ HIGH

- [x] `p1` - **ID**: `cpt-cypilot-feature-spec-coverage`

- **Purpose**: Measure how much of a project's codebase is covered by CDSL specification markers, report coverage percentage and instruction granularity quality, and support reverse-engineering of feature specs from existing code.

- **Depends On**: `cpt-cypilot-feature-traceability-validation`

- **Scope**:
  - Coverage percentage: ratio of spec-covered lines to total effective lines
  - Granularity score: instruction density (~1 instruction per 10 lines of code)
  - JSON report matching `coverage.py` structure (summary + per-file)
  - Threshold enforcement via `--min-coverage` and `--min-granularity` flags
  - Reverse-engineering workflow: identify uncovered code, place markers, generate specs (p2)

- **Out of scope**:
  - Modifying validation logic (Feature 3)
  - Generating PRD or DESIGN from code (manual process)

- **Requirements Covered**:

  - `p1` - `cpt-cypilot-fr-core-traceability`
  - `p1` - `cpt-cypilot-fr-core-cdsl`

- **Design Principles Covered**:

  - `p1` - `cpt-cypilot-principle-traceability-by-design`
  - `p1` - `cpt-cypilot-principle-determinism-first`

- **Design Constraints Covered**:

  - `p1` - `cpt-cypilot-constraint-no-weakening`

- **Domain Model Entities**:
  - CodeFile
  - CoverageRecord
  - CoverageReport

- **Design Components**:

  - `p1` - `cpt-cypilot-component-traceability-engine`
  - `p1` - `cpt-cypilot-component-validator`

- **API**:
  - `cpt spec-coverage [--min-coverage N] [--min-granularity N] [--verbose]`

- **Sequences**:

  None (single-command flow)

- **Data**:
  - Registered codebase entries from `{cypilot_path}/config/artifacts.toml`


---

## 3. Feature Dependencies

```text
cpt-cypilot-feature-core-infra
    ↓
    ├─→ cpt-cypilot-feature-blueprint-system (Kit Management)
    │
    ├─→ cpt-cypilot-feature-agent-integration
    │
    ├─→ cpt-cypilot-feature-version-config
    │
    ├─→ cpt-cypilot-feature-traceability-validation
    │    ↓
    │    ├─→ cpt-cypilot-feature-developer-experience
    │    │
    │    └─→ cpt-cypilot-feature-spec-coverage
    │
    └─→ cpt-cypilot-feature-v2-v3-migration ←── cpt-cypilot-feature-traceability-validation

    (EXTRACTED to cyberfabric/cyber-pilot-kit-sdlc:)
    cpt-cypilot-feature-sdlc-kit
    cpt-cypilot-feature-pr-workflows
    cpt-cypilot-feature-advanced-sdlc
```

**Dependency Rationale**:

- `cpt-cypilot-feature-traceability-validation` requires `cpt-cypilot-feature-core-infra`: validator needs config manager for system/artifact resolution
- `cpt-cypilot-feature-agent-integration` requires `cpt-cypilot-feature-core-infra`: agent generator consumes kit SKILL.md and workflow files
- `cpt-cypilot-feature-version-config` requires `cpt-cypilot-feature-core-infra`: update command needs config migration
- `cpt-cypilot-feature-developer-experience` requires `cpt-cypilot-feature-traceability-validation`: VS Code plugin and doctor delegate to validator and traceability engine
- `cpt-cypilot-feature-v2-v3-migration` requires `cpt-cypilot-feature-core-infra` and `cpt-cypilot-feature-traceability-validation`: migration needs v3 infrastructure and validation to verify completeness
- SDLC-specific features (F4, F6, F9) have been extracted to `cyberfabric/cyber-pilot-kit-sdlc` per `cpt-cypilot-adr-extract-sdlc-kit`
