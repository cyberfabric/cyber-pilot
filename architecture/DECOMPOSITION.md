# Decomposition: Cypilot


## 1. Overview

Cypilot DESIGN is decomposed into 10 features organized around architectural layers and functional cohesion. The decomposition follows a dependency order where core infrastructure enables the blueprint system and validation, which in turn enable the SDLC kit, agent integration, and advanced workflows.

**Decomposition Strategy**:
- Features grouped by architectural layer and functional cohesion (related components together)
- Dependencies minimize coupling between features — each feature is independently implementable given its dependencies
- p1 features (F1–F6, F10) cover all p1 functional requirements; p2 features (F7–F9) cover p2/p3 FRs
- 100% coverage of all DESIGN elements verified: 9 components, 6 sequences, 27 FRs, 4 NFRs, 12 principles, 4 constraints


## 2. Entries

**Overall implementation status:**

- [ ] `p1` - **ID**: `cpt-cypilot-status-overall`

### 2.1 [Core Infrastructure](feature-core-infra/) ⏳ HIGH

- [ ] `p1` - **ID**: `cpt-cypilot-feature-core-infra`

- **Purpose**: Provide the foundation layer — global CLI proxy, skill engine command dispatch, config directory management, and project initialization — upon which all other features are built.

- **Depends On**: None

- **Scope**:
  - Global CLI proxy with local cache (`~/.cypilot/cache/`), automatic skill bundle download from GitHub on first run, command routing, background version checks
  - Skill engine: command dispatch, JSON output serialization, exit code conventions (0/1/2)
  - Config manager: `config/core.toml` CRUD, schema validation, deterministic TOML serialization
  - Project initialization: interactive bootstrapper, root system definition (name/slug from directory), `config/core.toml` creation, `config/artifacts.toml` with default autodetect rules, root `AGENTS.md` injection, `config/AGENTS.md` with default WHEN rules

- **Out of scope**:
  - Kit installation logic (Feature 2)
  - Validation logic (Feature 3)
  - Agent entry point generation (Feature 5)
  - CLI config subcommands beyond init (Feature 7)

- **Requirements Covered**:

  - [ ] `p1` - `cpt-cypilot-fr-core-installer`
  - [ ] `p1` - `cpt-cypilot-fr-core-init`
  - [ ] `p1` - `cpt-cypilot-fr-core-config`
  - [ ] `p1` - `cpt-cypilot-fr-core-skill-engine`
  - [x] `p1` - `cpt-cypilot-nfr-adoption-usability`
  - [x] `p1` - `cpt-cypilot-nfr-reliability-recoverability`

- **Design Principles Covered**:

  - [x] `p1` - `cpt-cypilot-principle-determinism-first`
  - [ ] `p1` - `cpt-cypilot-principle-occams-razor`
  - [ ] `p2` - `cpt-cypilot-principle-tool-managed-config`
  - [ ] `p1` - `cpt-cypilot-principle-zero-harm`

- **Design Constraints Covered**:

  - [ ] `p1` - `cpt-cypilot-constraint-python-stdlib`
  - [ ] `p1` - `cpt-cypilot-constraint-cross-platform`
  - [ ] `p2` - `cpt-cypilot-constraint-git-project-heuristics`

- **Domain Model Entities**:
  - System
  - Config
  - Kit (registration only)

- **Design Components**:

  - [ ] `p1` - `cpt-cypilot-component-cli-proxy`
  - [ ] `p1` - `cpt-cypilot-component-skill-engine`
  - [ ] `p1` - `cpt-cypilot-component-config-manager`

- **API**:
  - `cypilot init [--dir DIR] [--agents AGENTS]`
  - `cypilot config show`

- **Sequences**:
  - `cpt-cypilot-seq-init`

- **Data**:
  - `config/core.toml` — system definitions, kit registrations, ignore lists
  - `config/artifacts.toml` — artifact registry with autodetect rules


### 2.2 [Blueprint System](feature-blueprint-system/) ⏳ HIGH

- [ ] `p1` - **ID**: `cpt-cypilot-feature-blueprint-system`

- **Purpose**: Enable single-source-of-truth blueprint files that generate all kit resources, with a reference-based update model preserving user customizations.

- **Depends On**: `cpt-cypilot-feature-core-infra`

- **Scope**:
  - Blueprint Processor: parse `@cpt:` markers, extract TOML/Markdown content blocks
  - Resource generation: `rules.md`, `checklist.md`, `template.md`, `example.md`, `constraints.toml`, `workflows/*.md`, `codebase/rules.md`, `codebase/checklist.md`
  - Kit Manager: install kits (save to `{cypilot}/kits/{slug}/`, copy blueprints to `config/kits/{slug}/blueprints/`), register in `core.toml`
  - Update model: force mode (full overwrite) and additive mode (three-way diff using reference)
  - SKILL composition: collect `@cpt:skill` sections for Agent Generator
  - System prompt collection: collect `@cpt:system-prompt` sections
  - Workflow registration: generate workflow files from `@cpt:workflow` markers
  - Blueprint validation: verify structure, marker closure, unique IDs

- **Out of scope**:
  - Custom marker types and output generators (planned p2 plugin system)
  - Validation of generated outputs (Feature 3)

- **Requirements Covered**:

  - [ ] `p1` - `cpt-cypilot-fr-core-blueprint`
  - [ ] `p1` - `cpt-cypilot-fr-core-kits`

- **Design Principles Covered**:

  - [ ] `p1` - `cpt-cypilot-principle-kit-centric`
  - [ ] `p1` - `cpt-cypilot-principle-plugin-extensibility`
  - [ ] `p1` - `cpt-cypilot-principle-dry`
  - [ ] `p2` - `cpt-cypilot-principle-no-manual-maintenance`

- **Design Constraints Covered**:

  - [ ] `p1` - `cpt-cypilot-constraint-markdown-contract`

- **Domain Model Entities**:
  - Blueprint
  - Kit
  - Constraint
  - Workflow

- **Design Components**:

  - [ ] `p1` - `cpt-cypilot-component-blueprint-processor`
  - [ ] `p1` - `cpt-cypilot-component-kit-manager`

- **API**:
  - `cypilot kit install <path>`
  - `cypilot kit update [--force]`
  - `cypilot validate --blueprints`

- **Sequences**:

  None (blueprint processing is invoked internally by kit install/update)

- **Data**:
  - `{cypilot}/kits/{slug}/` — reference kit copies
  - `config/kits/{slug}/blueprints/` — user-editable blueprint copies
  - `config/kits/{slug}/constraints.toml` — kit-wide structural constraints
  - `config/kits/{slug}/artifacts/{KIND}/` — generated per-artifact outputs
  - `config/kits/{slug}/workflows/` — generated workflow files


### 2.3 [Traceability & Validation](feature-traceability-validation/) ⏳ HIGH

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

  - [x] `p1` - `cpt-cypilot-fr-core-traceability`
  - [x] `p1` - `cpt-cypilot-fr-core-cdsl`
  - [x] `p1` - `cpt-cypilot-fr-sdlc-validation`
  - [x] `p1` - `cpt-cypilot-fr-sdlc-cross-artifact`
  - [x] `p1` - `cpt-cypilot-nfr-validation-performance`
  - [x] `p1` - `cpt-cypilot-nfr-security-integrity`

- **Design Principles Covered**:

  - [x] `p1` - `cpt-cypilot-principle-determinism-first`
  - [x] `p1` - `cpt-cypilot-principle-traceability-by-design`
  - [x] `p1` - `cpt-cypilot-principle-ci-automation-first`
  - [x] `p2` - `cpt-cypilot-principle-machine-readable`

- **Design Constraints Covered**:

  - [x] `p1` - `cpt-cypilot-constraint-no-weakening`

- **Domain Model Entities**:
  - Identifier
  - Artifact
  - Constraint

- **Design Components**:

  - [x] `p1` - `cpt-cypilot-component-validator`
  - [x] `p1` - `cpt-cypilot-component-traceability-engine`

- **API**:
  - `cypilot validate --artifact <path>`
  - `cypilot validate`
  - `cypilot list-ids [--kind K] [--pattern P]`
  - `cypilot where-defined <id>`
  - `cypilot where-used <id>`
  - `cypilot get-content <id>`

- **Sequences**:
  - `cpt-cypilot-seq-validate`
  - `cpt-cypilot-seq-traceability-query`

- **Data**:
  - In-memory ID index (definitions + references, built from filesystem scan)


### 2.4 [SDLC Kit & Artifact Pipeline](feature-sdlc-kit/) ⏳ HIGH

- [ ] `p1` - **ID**: `cpt-cypilot-feature-sdlc-kit`

- **Purpose**: Provide the primary domain kit — SDLC blueprints for PRD, DESIGN, ADR, DECOMPOSITION, and FEATURE — enabling the artifact-first development pipeline.

- **Depends On**: `cpt-cypilot-feature-blueprint-system`, `cpt-cypilot-feature-traceability-validation`

- **Scope**:
  - Blueprint authoring: one `.md` per artifact kind with SDLC-specific markers
  - Codebase blueprint: generates `codebase/rules.md` and `codebase/checklist.md`
  - Artifact-first pipeline: PRD → DESIGN → ADR → DECOMPOSITION → FEATURE → CODE
  - Generated outputs via Blueprint Processor
  - Each artifact kind usable independently (no forced sequence)

- **Out of scope**:
  - Custom marker registration (planned p2)
  - Code generation from design (Feature 9)
  - PR review/status (Feature 6)

- **Requirements Covered**:

  - [ ] `p1` - `cpt-cypilot-fr-sdlc-pipeline`
  - [ ] `p2` - `cpt-cypilot-fr-sdlc-plugin`

- **Design Principles Covered**:

  - [ ] `p1` - `cpt-cypilot-principle-kit-centric`
  - [ ] `p1` - `cpt-cypilot-principle-dry`

- **Design Constraints Covered**:

  - [ ] `p1` - `cpt-cypilot-constraint-markdown-contract`

- **Domain Model Entities**:
  - Blueprint
  - Artifact
  - Kit

- **Design Components**:

  - [ ] `p1` - `cpt-cypilot-component-sdlc-plugin`

- **API**:
  - `cypilot self-check`

- **Sequences**:

  None (SDLC kit provides blueprints; processing handled by Feature 2)

- **Data**:
  - `kits/sdlc/blueprints/` — source blueprint files
  - `config/kits/sdlc/` — installed kit config and generated outputs


### 2.5 [Agent Integration & Workflows](feature-agent-integration/) ⏳ MEDIUM

- [ ] `p1` - **ID**: `cpt-cypilot-feature-agent-integration`

- **Purpose**: Bridge Cypilot's unified skill system to diverse AI coding assistants by generating agent-native entry points and providing generic generate/analyze workflows.

- **Depends On**: `cpt-cypilot-feature-blueprint-system`

- **Scope**:
  - Agent Generator: produce entry points in each agent's native format
  - Supported agents: Windsurf, Cursor, Claude, Copilot, OpenAI
  - SKILL.md composition: collect `@cpt:skill` sections and assemble into main SKILL.md
  - Full overwrite on each invocation; `--agent` flag for single-agent regeneration
  - Generic workflows: `generate.md` and `analyze.md` with common execution protocol

- **Out of scope**:
  - Agent-specific state persistence
  - Kit-specific workflow content (provided by Feature 4)

- **Requirements Covered**:

  - [ ] `p1` - `cpt-cypilot-fr-core-agents`
  - [ ] `p1` - `cpt-cypilot-fr-core-workflows`

- **Design Principles Covered**:

  - [ ] `p2` - `cpt-cypilot-principle-skill-documented`
  - [ ] `p2` - `cpt-cypilot-principle-no-manual-maintenance`

- **Design Constraints Covered**:

  None

- **Domain Model Entities**:
  - AgentEntryPoint
  - Workflow

- **Design Components**:

  - [ ] `p2` - `cpt-cypilot-component-agent-generator`

- **API**:
  - `cypilot agents [--agent A]`

- **Sequences**:
  - `cpt-cypilot-seq-generate-workflow`

- **Data**:
  - `.windsurf/workflows/`, `.cursor/rules/`, `.claude/commands/`, `.github/prompts/`


### 2.6 [PR Workflows](feature-pr-workflows/) ⏳ MEDIUM

- [ ] `p1` - **ID**: `cpt-cypilot-feature-pr-workflows`

- **Purpose**: Enable structured GitHub PR review and status assessment via gh CLI with configurable prompts and checklists.

- **Depends On**: `cpt-cypilot-feature-sdlc-kit`, `cpt-cypilot-feature-agent-integration`

- **Scope**:
  - PR review: fetch PR data (diffs, metadata, comments) via `gh` CLI, analyze against prompts and checklists, produce structured review report
  - PR status: fetch comments, CI status, merge conflict state, classify unreplied comments by severity, output JSON report
  - Read-only: no local working tree modifications, always re-fetches data
  - Graceful degradation: actionable error if `gh` not available or not authenticated

- **Out of scope**:
  - PR config management CLI (Feature 9)
  - Writing PR comments or approvals (read-only analysis)

- **Requirements Covered**:

  - [ ] `p1` - `cpt-cypilot-fr-sdlc-pr-review`
  - [ ] `p1` - `cpt-cypilot-fr-sdlc-pr-status`

- **Design Principles Covered**:

  - [x] `p1` - `cpt-cypilot-principle-determinism-first`
  - [x] `p1` - `cpt-cypilot-principle-ci-automation-first`

- **Design Constraints Covered**:

  None

- **Domain Model Entities**:
  - Artifact (PR as analysis target)

- **Design Components**:

  None (PR workflows are agent-driven, using `gh` CLI subprocess)

- **API**:
  - `cypilot sdlc pr-review <number>`
  - `cypilot sdlc pr-status <number>`

- **Sequences**:
  - `cpt-cypilot-seq-pr-review`

- **Data**:
  - `config/kits/sdlc/` — PR review prompts, checklists, exclude lists

- **External Dependencies**:

  - [ ] `p2` - `cpt-cypilot-interface-github-gh-cli`


### 2.7 [Version & Config Management](feature-version-config/) ⏳ MEDIUM

- [ ] `p2` - **ID**: `cpt-cypilot-feature-version-config`

- **Purpose**: Enable project skill updates with config migration, and provide CLI commands for managing system definitions, ignore lists, and kit registrations.

- **Depends On**: `cpt-cypilot-feature-core-infra`, `cpt-cypilot-feature-blueprint-system`

- **Scope**:
  - Update command: copy cached skill to project, migrate `config/core.toml`, invoke kit migration scripts, regenerate agent entry points
  - Config migration: backup before applying, preserve all user settings across versions
  - CLI config interface: `config system add/remove`, dry-run mode
  - Schema validation before all config writes
  - Version information: `--version` flag

- **Out of scope**:
  - Kit-specific CLI subcommands (planned p2 plugin)
  - Initial project setup (Feature 1)

- **Requirements Covered**:

  - [ ] `p2` - `cpt-cypilot-fr-core-version`
  - [ ] `p2` - `cpt-cypilot-fr-core-cli-config`
  - [x] `p1` - `cpt-cypilot-nfr-reliability-recoverability`

- **Design Principles Covered**:

  - [ ] `p2` - `cpt-cypilot-principle-tool-managed-config`
  - [ ] `p2` - `cpt-cypilot-principle-no-manual-maintenance`

- **Design Constraints Covered**:

  None

- **Domain Model Entities**:
  - Config

- **Design Components**:

  Components reused from Feature 1 (`config-manager`, `skill-engine`) and Feature 2 (`kit-manager`)

- **API**:
  - `cypilot update [--check]`
  - `cypilot migrate-config`
  - `cypilot config system add <name> [--kit K]`
  - `cypilot config system remove <name>`
  - `cypilot --version`

- **Sequences**:
  - `cpt-cypilot-seq-update`

- **Data**:
  - `config/core.toml` — migrated config with version field


### 2.8 [Developer Experience](feature-developer-experience/) ⏳ LOW

- [ ] `p2` - **ID**: `cpt-cypilot-feature-developer-experience`

- **Purpose**: Enhance developer productivity with IDE integration, environment health checks, and utility commands for daily use.

- **Depends On**: `cpt-cypilot-feature-traceability-validation`

- **Scope**:
  - VS Code extension: ID syntax highlighting, go-to-definition, real-time validation, autocompletion, hover info, CodeLens, traceability tree view, quick fixes — all delegated to `cypilot validate`
  - `cypilot doctor`: check Python version, git, gh CLI, agents, config integrity
  - `cypilot self-check`: validate examples against templates
  - `cypilot hook install/uninstall`: git pre-commit hooks for validation
  - `cypilot completions install`: shell completion scripts for bash/zsh/fish

- **Out of scope**:
  - VS Code extension publishing (separate repo/process)
  - IDE-specific validation logic (delegated to skill)

- **Requirements Covered**:

  - [ ] `p2` - `cpt-cypilot-fr-core-vscode-plugin`
  - [ ] `p2` - `cpt-cypilot-fr-core-template-qa`
  - [ ] `p2` - `cpt-cypilot-fr-core-doctor`
  - [ ] `p3` - `cpt-cypilot-fr-core-hooks`
  - [ ] `p3` - `cpt-cypilot-fr-core-completions`

- **Design Principles Covered**:

  - [x] `p2` - `cpt-cypilot-principle-machine-readable`
  - [ ] `p1` - `cpt-cypilot-principle-zero-harm`

- **Design Constraints Covered**:

  None

- **Domain Model Entities**:
  - Identifier (for IDE features)

- **Design Components**:

  Components reused from Feature 3 (`validator`, `traceability-engine`)

- **API**:
  - `cypilot doctor`
  - `cypilot self-check`
  - `cypilot hook install`
  - `cypilot hook uninstall`
  - `cypilot completions install`

- **Sequences**:

  None

- **Data**:

  None


### 2.9 [Advanced SDLC Workflows](feature-advanced-sdlc/) ⏳ LOW

- [ ] `p2` - **ID**: `cpt-cypilot-feature-advanced-sdlc`

- **Purpose**: Enable code generation from design artifacts, brownfield project support, feature lifecycle tracking, PR configuration management, and quickstart guides.

- **Depends On**: `cpt-cypilot-feature-sdlc-kit`, `cpt-cypilot-feature-pr-workflows`

- **Scope**:
  - Code generation: agent-driven workflow loading FEATURE artifacts + project system prompts, producing code with `@cpt-*` traceability tags validated by Traceability Engine
  - Brownfield support: detect existing code during `init`, reverse-engineering mode for agents, incremental adoption
  - Feature lifecycle: status tracking (NOT_STARTED → IN_DESIGN → DESIGNED → READY → IN_PROGRESS → DONE) via checkbox state, transition rules, dependency blocking
  - PR config management: prompt selection, checklist mapping, domain-specific review criteria, exclude lists
  - Quickstart guides: progressive disclosure — human-facing overview docs, AI-facing navigation rules

- **Out of scope**:
  - Core pipeline definition (Feature 4)
  - PR review execution (Feature 6)

- **Requirements Covered**:

  - [ ] `p2` - `cpt-cypilot-fr-sdlc-code-gen`
  - [ ] `p2` - `cpt-cypilot-fr-sdlc-brownfield`
  - [ ] `p2` - `cpt-cypilot-fr-sdlc-lifecycle`
  - [ ] `p2` - `cpt-cypilot-fr-sdlc-pr-config`
  - [ ] `p2` - `cpt-cypilot-fr-sdlc-guides`

- **Design Principles Covered**:

  - [x] `p1` - `cpt-cypilot-principle-traceability-by-design`
  - [ ] `p2` - `cpt-cypilot-principle-skill-documented`

- **Design Constraints Covered**:

  None

- **Domain Model Entities**:
  - Artifact
  - Identifier

- **Design Components**:

  Components reused from Feature 4 (`sdlc-plugin`) and Feature 3 (`traceability-engine`)

- **API**:
  - `cypilot sdlc autodetect show --system S`
  - `cypilot sdlc autodetect add-artifact`
  - `cypilot sdlc autodetect add-codebase`

- **Sequences**:

  None (workflows are agent-driven)

- **Data**:
  - `config/kits/sdlc/` — PR config, autodetect rules


### 2.10 [V2 → V3 Migration](feature-v2-v3-migration/) ⏳ HIGH

- [ ] `p1` - **ID**: `cpt-cypilot-feature-v2-v3-migration`

- **Purpose**: Migrate existing Cypilot v2 projects (adapter-based, `artifacts.json`, legacy kit structure) to v3 (blueprint-based, `artifacts.toml`, global CLI installer, `config/` directory) with zero data loss.

- **Depends On**: `cpt-cypilot-feature-core-infra`, `cpt-cypilot-feature-blueprint-system`, `cpt-cypilot-feature-traceability-validation`

- **Scope**:
  - Detect v2 installation: identify `.cypilot-adapter/` directory, `artifacts.json`, legacy kit paths
  - Convert `artifacts.json` → `config/artifacts.toml`: map systems, artifacts, codebase, autodetect, ignore rules to TOML format
  - Convert legacy adapter directory → `config/` structure: migrate adapter-level specs to `config/sysprompts/`
  - Generate `config/core.toml` from legacy config: extract system definitions, kit registrations
  - Create `config/AGENTS.md` from legacy adapter `AGENTS.md`: convert WHEN rules, update paths
  - Migrate kit resources: install SDLC kit from cache, regenerate blueprint outputs into `config/kits/sdlc/`
  - Inject root `AGENTS.md` managed block with new `config/AGENTS.md` path
  - Regenerate all agent entry points for v3 structure
  - Preserve all existing artifact files and ID definitions unchanged
  - Validate migration completeness: all artifacts still resolve, all IDs still discoverable
  - Rollback support: backup v2 state before migration

- **Out of scope**:
  - Ongoing v3 updates after migration (Feature 7)
  - Manual migration of custom scripts or extensions
  - Supporting v2 and v3 simultaneously in the same project

- **Requirements Covered**:

  - [ ] `p1` - `cpt-cypilot-fr-core-init`
  - [ ] `p1` - `cpt-cypilot-fr-core-config`

- **Design Principles Covered**:

  - [ ] `p1` - `cpt-cypilot-principle-zero-harm`
  - [ ] `p2` - `cpt-cypilot-principle-no-manual-maintenance`

- **Design Constraints Covered**:

  None

- **Domain Model Entities**:
  - Config
  - System
  - Artifact

- **Design Components**:

  - [ ] `p1` - `cpt-cypilot-component-config-manager`
  - [ ] `p1` - `cpt-cypilot-component-kit-manager`
  - [ ] `p1` - `cpt-cypilot-component-skill-engine`

- **API**:
  - `cypilot migrate` (or detected automatically during `cypilot init` in v2 project)
  - `cypilot migrate-config`

- **Sequences**:

  None (migration is a one-time init-like flow)

- **Data**:
  - `.cypilot-adapter/` → `config/` (converted)
  - `artifacts.json` → `config/artifacts.toml` (converted)
  - `.cypilot-adapter/AGENTS.md` → `config/AGENTS.md` (converted)
  - `.cypilot-adapter/specs/` → `config/sysprompts/` (converted)


---

## 3. Feature Dependencies

```text
cpt-cypilot-feature-core-infra
    ↓
    ├─→ cpt-cypilot-feature-blueprint-system
    │    ↓
    │    ├─→ cpt-cypilot-feature-sdlc-kit ←── cpt-cypilot-feature-traceability-validation
    │    │    ↓
    │    │    └─→ cpt-cypilot-feature-pr-workflows ←── cpt-cypilot-feature-agent-integration
    │    │         ↓
    │    │         └─→ cpt-cypilot-feature-advanced-sdlc
    │    │
    │    ├─→ cpt-cypilot-feature-agent-integration
    │    │
    │    └─→ cpt-cypilot-feature-version-config ←── cpt-cypilot-feature-core-infra
    │
    ├─→ cpt-cypilot-feature-traceability-validation
    │    ↓
    │    └─→ cpt-cypilot-feature-developer-experience
    │
    └─→ cpt-cypilot-feature-v2-v3-migration ←── cpt-cypilot-feature-blueprint-system, cpt-cypilot-feature-traceability-validation
```

**Dependency Rationale**:

- `cpt-cypilot-feature-blueprint-system` requires `cpt-cypilot-feature-core-infra`: blueprints need config manager for kit registration and skill engine for command routing
- `cpt-cypilot-feature-traceability-validation` requires `cpt-cypilot-feature-core-infra`: validator needs config manager for system/artifact resolution
- `cpt-cypilot-feature-sdlc-kit` requires `cpt-cypilot-feature-blueprint-system` and `cpt-cypilot-feature-traceability-validation`: SDLC blueprints need the processor to generate resources, and constraints need the validator for enforcement
- `cpt-cypilot-feature-agent-integration` requires `cpt-cypilot-feature-blueprint-system`: agent generator consumes `@cpt:skill` sections and `@cpt:workflow` outputs from Blueprint Processor
- `cpt-cypilot-feature-pr-workflows` requires `cpt-cypilot-feature-sdlc-kit` and `cpt-cypilot-feature-agent-integration`: PR workflows use SDLC kit's prompts/checklists and are exposed via agent entry points
- `cpt-cypilot-feature-version-config` requires `cpt-cypilot-feature-core-infra` and `cpt-cypilot-feature-blueprint-system`: update command needs config migration and kit re-generation
- `cpt-cypilot-feature-developer-experience` requires `cpt-cypilot-feature-traceability-validation`: VS Code plugin and doctor delegate to validator and traceability engine
- `cpt-cypilot-feature-advanced-sdlc` requires `cpt-cypilot-feature-sdlc-kit` and `cpt-cypilot-feature-pr-workflows`: code generation uses SDLC kit artifacts, PR config extends PR review
- `cpt-cypilot-feature-v2-v3-migration` requires `cpt-cypilot-feature-core-infra`, `cpt-cypilot-feature-blueprint-system`, and `cpt-cypilot-feature-traceability-validation`: migration needs v3 infrastructure, blueprint system to regenerate resources, and validation to verify completeness
- `cpt-cypilot-feature-blueprint-system` and `cpt-cypilot-feature-traceability-validation` are independent of each other and can be developed in parallel
- `cpt-cypilot-feature-agent-integration` and `cpt-cypilot-feature-sdlc-kit` are independent of each other and can be developed in parallel
