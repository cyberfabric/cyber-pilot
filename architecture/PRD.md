# PRD — Cyber Pilot (Cypilot)

## 1. Overview

### 1.1 Purpose

Cypilot is a deterministic agent tool that embeds into AI coding assistants and CI pipelines to provide structured workflows, artifact validation, and design-to-code traceability. Cypilot maximizes determinism: everything that can be validated, checked, or enforced without an LLM is handled by deterministic scripts; the LLM is reserved only for tasks that require reasoning, creativity, or natural language understanding.

The system consists of two layers:

- **Core** — deterministic skill engine, generic workflows (generate/analyze), multi-agent integrations, global CLI, config directory management, extensible kit system, ID/traceability infrastructure, and Cypilot DSL (CDSL) for behavioral specifications
- **SDLC Kit** — artifact-first development pipeline (PRD → DESIGN → ADR → DECOMPOSITION → FEATURE → CODE) with templates, checklists, examples, deterministic validation, cross-artifact consistency checks, and GitHub PR review/status workflows with configurable prompts, severity assessment, and resolved-comment audit

### 1.2 Background / Problem Statement

**Target Users**:
- Developers using AI coding assistants (Windsurf, Cursor, Claude, Copilot) for daily work
- Technical Leads setting up development methodology and project conventions
- Teams adopting structured design-to-code workflows with AI assistance
- DevOps engineers integrating Cypilot validation into CI/CD pipelines for artifact and code quality gates

**Key Problems Solved**:
- **AI Agent Non-Determinism**: AI agents produce inconsistent results without structured guardrails; deterministic validation catches structural and traceability issues that LLMs miss or hallucinate
- **Design-Code Disconnect**: Code diverges from design when there is no single source of truth and no automated traceability enforcement
- **Fragmented Tool Setup**: Each AI agent (Windsurf, Cursor, Claude, Copilot) requires different file formats for skills, workflows, and rules; maintaining these manually is error-prone
- **Inconsistent PR Reviews**: Code reviews vary in depth and focus without structured checklists and prompts; reviewers miss patterns that deterministic analysis catches
- **Manual Configuration Overhead**: Project-specific conventions, artifact locations, and validation rules require manual setup and synchronization across tools

### 1.3 Goals (Business Outcomes)

**Success Criteria**:
- A new user can install Cypilot globally and initialize a project (`pipx install cypilot && cypilot init`) in ≤ 5 minutes. (Baseline: not measured; Target: v2.0)
- Deterministic validation of any single artifact completes in ≤ 3 seconds on a typical developer laptop. (Baseline: ~1s current; Target: v2.0)
- 100% of `cpt-*` IDs defined in artifacts are resolvable via deterministic search (`cypilot where-defined`) without ambiguity. (Baseline: 100% current; Target: v2.0)
- Agent workflow entry points for all supported agents are generated in ≤ 10 seconds via `cypilot agents`. (Baseline: ~5s current; Target: v2.0)
- PR review workflow produces a structured review report within 2 minutes of invocation. (Baseline: not measured; Target: v2.0)

**Capabilities**:
- Install once globally, initialize per project with interactive setup
- Execute deterministic validation and traceability scanning without LLM
- Provide structured workflows for artifact creation, analysis, and code generation
- Generate and maintain agent-specific entry points for all supported AI assistants
- Review and assess GitHub PRs with configurable prompts and checklists
- Manage project configuration through a structured config directory edited only by the tool

### 1.4 Glossary

| Term | Definition |
|------|------------|
| Cypilot | Deterministic agent tool: global CLI + project-installed skill + kits + workflows |
| Skill | The core Python package installed in a project's `.cypilot/` directory, containing all commands, validation logic, and utilities |
| Kit | Extensible package of templates, checklists, rules, examples, and constraints for a domain (e.g., SDLC) |
| Config | `config/` directory inside the install directory containing `core.toml` and per-kit configs in `kits/<slug>/`, managed exclusively by the tool |
| CDSL | Cypilot DSL — plain English behavioral specification language for actor flows and algorithms |
| Traceability | Linking design elements to code via `cpt-*` IDs and `@cpt-*` code tags |
| System Prompt | Project-specific context file in `.cypilot/config/sysprompts/` (tech-stack, conventions, domain model) loaded by workflows via config/AGENTS.md WHEN rules |
| Agent Entry Point | Agent-specific file (workflow proxy, skill shim, or rule file) generated in the agent's native format |

---

## 2. Actors

### 2.1 Human Actors

#### User

**ID**: `cpt-cypilot-actor-user`

**Role**: Primary user of Cypilot. Uses the tool through AI agent chats and CLI to: create and validate artifacts, implement features with traceability, configure the project (`cypilot init`, kits, autodetect rules), review PRs against configurable checklists, and manage project conventions.

### 2.2 System Actors

#### AI Agent

**ID**: `cpt-cypilot-actor-ai-agent`

**Role**: Executes Cypilot workflows (generate, analyze, PR review) by following SKILL.md instructions, loading rules and templates, and producing structured output. Supported agents: Windsurf, Cursor, Claude, Copilot, OpenAI.

#### CI/CD Pipeline

**ID**: `cpt-cypilot-actor-ci-pipeline`

**Role**: Runs deterministic validation and PR review automatically on commits and pull requests. Reports results as status checks and blocks merges on failure.

#### Cypilot CLI

**ID**: `cpt-cypilot-actor-cypilot-cli`

**Role**: Global command-line tool installed via `pipx`. Provides `init` for bootstrapping and delegates all other commands to the project-installed skill. Detects version mismatches and proposes updates.

---

## 3. Operational Concept & Environment

### 3.1 Module-Specific Environment Constraints

- Python 3.10+ required for the CLI tool and skill engine
- Git required for project detection, version control, and skill installation
- `gh` CLI required for PR review/status workflows (GitHub integration)
- `pipx` recommended for global CLI installation (isolation from project dependencies)

---

## 4. Scope

### 4.1 In Scope

- Global CLI tool with `pipx` installation and project-specific command delegation
- Interactive project initialization with directory, agent, and kit selection
- Config directory (`config/`) with core and per-kit configs, managed exclusively by the tool
- Deterministic skill engine with JSON output for all commands
- Generic workflows (generate/analyze) with execution protocol
- Multi-agent integration (Windsurf, Cursor, Claude, Copilot, OpenAI)
- Extensible kit system with registration, extension, and custom kit creation
- ID and traceability system with code tags, search, and validation
- CDSL behavioral specification language
- SDLC artifact pipeline with templates, checklists, cross-artifact validation, and PR review/status workflows
- Version detection, update proposals, and config directory migration
- Rich CLI for configuration management (autodetect, artifacts, ignore lists, kits, constraints)
- Environment diagnostics (`cypilot doctor`)
- Pre-commit hook integration (`cypilot hook install`)

### 4.2 Out of Scope

- Replacing project management tools (Jira, Linear, etc.)
- Automatically generating production-quality code without human review
- GUI or web interface for Cypilot management
- Non-GitHub VCS platform support for PR review (GitLab, Bitbucket) in initial release
- Real-time collaboration or multi-user synchronization

---

## 5. Functional Requirements

### 5.1 Core

#### Global CLI Installer

- [ ] `p1` - **ID**: `cpt-cypilot-fr-core-installer`

The system MUST provide a global CLI tool installable via `pipx install git+https://github.com/cyberfabric/cyber-pilot.git`. The tool MUST be available as both `cypilot` and the short alias `cpt`. The global tool MUST have zero built-in commands — it is a pure proxy shell. On every invocation the tool MUST:

1. **Ensure cache** — maintain a local skill bundle cache (`~/.cypilot/cache/`). If no cache exists, download the latest skill bundle from the GitHub repository before proceeding. The tool MUST NOT require git as a runtime dependency.
2. **Resolve command target** — if the current directory is inside a project with an installed skill (`.cypilot/` directory), proxy the command to the project-installed skill. Otherwise, proxy the command to the cached skill.
3. **Version check (non-blocking)** — on every invocation, check for newer versions in the background. The check MUST NOT block or delay the main command execution. Concurrent checks MUST be prevented. A newly available version becomes visible on the next invocation.
4. **Version highlight** — if the cached version is newer than the project-installed version, display a notice: "Cypilot {cached_version} available (project has {project_version}). Run `cypilot update` to upgrade."

The tool MUST NOT contain any skill logic, workflow logic, or command implementations. All functionality comes from the cached or project-installed skill bundle.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Project Initialization

- [ ] `p1` - **ID**: `cpt-cypilot-fr-core-init`

The system MUST provide an interactive `cypilot init` command that bootstraps Cypilot in a project. Before proceeding, the command MUST check whether Cypilot is already installed in the project. If an existing installation is detected, the command MUST NOT overwrite it — instead it MUST inform the user and propose `cypilot update` if a newer version is available. The dialog MUST ask: (1) installation directory (default: `.cypilot`), (2) which agents to support (default: all available — windsurf, cursor, claude, copilot, openai). All available kits MUST be enabled by default. The command MUST create the full directory structure including skills (copied from the cache), kits, workflows, prompts, schemas, and agent-specific entry points. The command MUST define a **root system** — deriving the project name and slug from the project directory name. The command MUST create `config/core.toml` (containing project root, root system definition, kit registrations) and `config/artifacts.toml` with a fully populated root system entry including default SDLC autodetect rules for standard artifact kinds (`PRD.md`, `DESIGN.md`, `ADR/*.md`, `DECOMPOSITION.md`, `features/*.md`), default codebase entries, and ignore patterns. Installed kits MUST generate their full config in `config/kits/<slug>/` — blueprints, constraints, per-artifact outputs, and workflows. The command MUST inject a managed `<!-- @cpt:root-agents -->` block at the beginning of the project root `AGENTS.md` (creating the file if absent) containing `ALWAYS open @/{install_dir}/config/AGENTS.md FIRST`. The command MUST create `config/AGENTS.md` with default WHEN rules for standard system prompts. Every subsequent CLI invocation MUST verify the root AGENTS.md block exists and is correct, silently re-injecting it if missing or stale. After completion, the command MUST display a prompt suggestion: `cypilot on` or `cypilot help`.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Config Directory

- [ ] `p1` - **ID**: `cpt-cypilot-fr-core-config`

The system MUST maintain a `config/` directory inside the Cypilot install directory. All config files MUST be edited exclusively by the tool — never by humans directly. All config files MUST be TOML format with deterministic serialization (sorted keys, consistent formatting). The directory structure MUST be:

- **`config/core.toml`** — core Cypilot config containing: project root, kit registrations (slug → path mapping), system definitions (name, slug, kit assignment), ignore lists. The core config MUST be versioned with a schema version field. The system MUST support migration of `core.toml` between versions automatically when the skill is updated.
- **`config/kits/<slug>/`** — per-kit directory containing: `blueprints/` (user-editable copies of source blueprints), `constraints.toml` (kit-wide structural constraints aggregated from all artifact blueprints), `artifacts/<KIND>/` (generated per-artifact outputs: template.md, rules.md, checklist.md, example.md), `codebase/` (generated from blueprints without `artifact` key: rules.md, checklist.md), and `workflows/` (generated from `@cpt:workflow` markers). Cypilot core MUST NOT interpret kit-specific semantics — it only knows that a kit is registered and where its blueprints and generated outputs live. Autodetect rules MUST support complex nested structures: per-system root paths, per-system artifact roots with glob patterns and traceability levels, per-system codebase definitions with paths and file extensions. Autodetect MUST support hierarchical monorepos where systems can be nested (e.g., `{project_root}/examples/$system`).

Cypilot core's domain is: artifact awareness (knows artifacts exist, how to locate them via kit-provided autodetect rules), ID and traceability (format, scanning, cross-references), and kit routing (which kit owns which artifact kind).

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Deterministic Skill Engine

- [ ] `p1` - **ID**: `cpt-cypilot-fr-core-skill-engine`

The system MUST provide a Python-based deterministic skill engine as the core command executor. All commands MUST output JSON. All validation, scanning, and transformation logic MUST be deterministic (same input → same output). Exit codes MUST follow the convention: 0=PASS, 1=filesystem error, 2=FAIL. The skill MUST be self-contained and importable from the project's install directory. The skill MUST provide SKILL.md as the agent entry point with execution protocol, workflow routing, and command reference.

**Actors**:
`cpt-cypilot-actor-ai-agent`, `cpt-cypilot-actor-ci-pipeline`, `cpt-cypilot-actor-cypilot-cli`

#### Generic Workflows

- [ ] `p1` - **ID**: `cpt-cypilot-fr-core-workflows`

The system MUST provide exactly two universal workflows: generate (write: create, edit, fix, update, implement) and analyze (read: validate, review, check, inspect, audit). Both workflows MUST execute a common execution protocol before their specific logic. Workflows MUST be Markdown files with frontmatter metadata, structured phases, and validation criteria. Workflows MUST support execution logging with context and message format for agent transparency. Workflows MUST NOT hardcode repository paths — all paths MUST be resolved from the config and adapter.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

#### Multi-Agent Integration

- [ ] `p1` - **ID**: `cpt-cypilot-fr-core-agents`

The system MUST provide a unified `agents` command that generates agent-specific entry points for all supported AI coding assistants. Supported agents MUST include Windsurf, Cursor, Claude, Copilot, and OpenAI. The command MUST generate workflow entry points in each agent's native format (`.windsurf/workflows/`, `.cursor/rules/`, `.claude/commands/`, `.github/prompts/`) and skill entry points that reference the core SKILL.md. Agent selection MUST NOT be persisted in the config. The command MUST accept an optional `--agent` argument to regenerate entry points for a specific agent; without `--agent`, the command MUST regenerate entry points for all supported agents. The command always fully overwrites agent entry points on each invocation.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`, `cpt-cypilot-actor-cypilot-cli`

#### Extensible Kit System

- [ ] `p1` - **ID**: `cpt-cypilot-fr-core-kits`

The system MUST support extensible kit packages. Each kit is a blueprint package with the following minimum required structure:

1. **Blueprints directory** — each kit MUST provide a `blueprints/` directory containing one `.md` file per artifact kind. The filename (without `.md`) becomes the artifact kind slug (e.g., `PRD.md` → artifact kind `PRD`). This is the single source of truth for all kit resources.
2. **Installation** — during installation, the tool MUST save the kit source to `{cypilot_path}/.core/kits/{slug}/` (reference copy) and copy blueprints to `config/kits/{slug}/blueprints/` (user-editable). The Blueprint Processor MUST then generate all outputs into `config/kits/{slug}/artifacts/<KIND>/` and `config/kits/{slug}/workflows/`.
3. **Versioning** — each kit MUST have its own version (independent of the core Cypilot version). The version MUST be stored in the kit's `@cpt:blueprint` marker metadata.
4. **Migration** — the tool MUST support two update modes: **force** (`cypilot kit update --force`) updates the reference in `{cypilot_path}/.core/kits/{slug}/`, overwrites all user blueprints, and regenerates outputs; **additive** (`cypilot kit update`, default) uses the reference (`{cypilot_path}/.core/kits/{slug}/`) for a three-way diff, preserving user modifications. New markers are inserted; deleted markers stay deleted; user-modified sections are preserved. After merge, the reference is updated.
5. **SKILL extensions** — a kit MAY include `@cpt:skill` markers in blueprints that extend the core SKILL.md with kit-specific commands and workflows.
6. **System prompt extensions** — a kit MAY include `@cpt:system-prompt` markers in blueprints that are automatically loaded when the kit's artifacts or workflows are used.
7. **Workflow registrations** — a kit MAY include `@cpt:workflow` markers in blueprints that generate workflow files and agent entry points.

**User extensibility**: users MUST be able to edit blueprints in `config/kits/{slug}/blueprints/` and regenerate outputs with `cypilot generate-resources`. User modifications MUST be preserved across additive kit updates using the reference in `{cypilot_path}/.core/kits/{slug}/` for three-way diff.

Kit installation MUST register the kit in `config/core.toml`, create the kit's directory structure in `config/kits/<slug>/`, and generate all resources. The system MUST provide CLI commands to: install kits, update kits, and create new custom kits. The `validate-kits` command MUST validate that kit packages are structurally correct (have a `blueprints/` directory with valid blueprint files).

> **Plugin system** (Python entry points, custom CLI subcommands, validation hooks, generation hooks) is planned for p2.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Artifact Blueprint

- [ ] `p1` - **ID**: `cpt-cypilot-fr-core-blueprint`

The system MUST provide an **Artifact Blueprint** — a core contract defining a single-source-of-truth file per artifact kind from which all kit resources are generated. The blueprint MUST serve as both the artifact template and the specification for that artifact kind. The core MUST define the blueprint format, provide a blueprint processor, and enforce the contract across all kits.

The core blueprint contract MUST require only one mandatory output: `rules.md` (agent instructions for generate and analyze workflows). All other outputs are kit-defined — each kit registers its own generation targets (e.g., the SDLC kit registers template, checklist, constraints; another kit may register different file types). The core MUST provide an extension point for kits to register custom blueprint marker types and their corresponding output generators.

The tool MUST generate the initial blueprint and MUST be able to update it on kit upgrades. The tool MUST detect which parts of the blueprint the user has modified and MUST NOT overwrite those modifications. New markers added by the tool MUST be inserted without affecting user content. Markers deleted by the user MUST NOT be re-added. Users MUST be able to customize any part of the blueprint and all customizations MUST be preserved across updates. New artifact kinds MUST be creatable by adding a new blueprint.

The blueprint MUST support optional **SKILL extensions** — sections that extend the main SKILL.md with kit-specific commands, workflows, and capabilities. When a kit's blueprint defines a SKILL extension, it MUST be automatically integrated into the agent-facing SKILL.md so that AI agents discover kit capabilities without additional configuration.

The blueprint MUST support optional **system prompt extensions** — sections that provide additional context or instructions to AI agents when working with that artifact kind. These extensions MUST be automatically loaded by the generate and analyze workflows when processing the corresponding artifact.

The blueprint MUST support optional **workflow registrations** — structured definitions of workflows that agents can execute. Each workflow declared in a blueprint MUST be generated as a workflow `.md` file in the kit's `workflows/` directory. During agent entry point generation (`cypilot agents`), each workflow MUST get an entry point in every supported agent's native format (e.g., `.windsurf/workflows/cypilot-{name}.md`) that references the kit workflow file. Workflow names MUST be unique across all blueprints.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### ID and Traceability System

- [x] `p1` - **ID**: `cpt-cypilot-fr-core-traceability`

The system MUST provide a unique ID system for all design elements using structured format `cpt-{system-slug}-{kind}-{slug}`. This is the core domain of Cypilot: the core knows that artifacts exist, knows how to locate them (via autodetect rules provided by kits), knows which kit owns which artifact kind, and owns the ID format, scanning, and cross-reference resolution. The system MUST support code tags (`@cpt-*`) linking implementation to design. Traceability validation MUST be configurable per artifact (FULL or DOCS-ONLY). The system MUST provide commands: `list-ids`, `list-id-kinds`, `get-content`, `where-defined`, `where-used`. IDs MAY be versioned by appending `-vN` suffix. When an ID is replaced, references MUST be updated across all artifacts and code. Cross-artifact validation MUST check: covered_by references resolve, checked references imply checked definitions, and all ID references resolve to definitions. Artifact-specific validation logic (template compliance, structural rules) is delegated to the owning kit's plugin.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`, `cpt-cypilot-actor-ci-pipeline`

#### Cypilot DSL (CDSL)

- [x] `p1` - **ID**: `cpt-cypilot-fr-core-cdsl`

The system MUST define a plain English behavioral specification language (CDSL) for actor flows, algorithms, and state descriptions. CDSL MUST use structured numbered lists with bold keywords (**IF**, **ELSE**, **WHILE**, **FOR EACH**, **AND**, **OR**, **NOT**, **MUST**, **REQUIRED**, **OPTIONAL**). CDSL MUST support instruction markers with checkboxes (`- [ ] Inst-label: description`) and phase-based organization (`p1`, `p2`, etc.) for implementation tracking. CDSL MUST be readable by non-programmers for validation and review. CDSL MUST translate directly to code with traceability tags. CDSL MUST be actor-centric (steps start with **Actor** or **System**).

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

#### Version Detection and Updates

- [ ] `p2` - **ID**: `cpt-cypilot-fr-core-version`

The `cypilot update` command MUST update the project-installed skill to the version currently in the cache (`~/.cypilot/cache/`). The update MUST automatically migrate `config/core.toml` between versions, preserving all user settings. Each kit's migration script MUST be invoked to migrate its own config files. The update MUST regenerate agent entry points for compatibility. If the cache is outdated, the update MUST first download the latest release archive from GitHub before applying. Version information MUST be accessible via `cypilot --version` (shows both cache and project versions). The system MUST support `cypilot update --check` to show available updates without applying them.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### CLI Configuration Interface

- [ ] `p2` - **ID**: `cpt-cypilot-fr-core-cli-config`

The system MUST provide rich CLI commands for project configuration without manual file editing. Core CLI commands MUST support: managing system definitions in `config/core.toml` (add/remove/rename systems, assign kits), managing the ignore list (add/remove patterns with reasons), and registering/installing kits. Kit-specific config changes MUST be delegated to the kit's plugin CLI commands. For example, the SDLC kit plugin provides commands for managing autodetect rules per system (artifact patterns, traceability levels, codebase paths, file extensions) — the core CLI does not interpret these structures. All config changes MUST go through the tool to maintain config integrity and versioning. The CLI MUST provide dry-run mode for config changes. The CLI MUST support reading current config values (e.g., `cypilot config show`, `cypilot sdlc autodetect show --system cypilot`).

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Template Quality Assurance

- [ ] `p2` - **ID**: `cpt-cypilot-fr-core-template-qa`

The system MUST provide a `self-check` command that validates example artifacts against their templates. When validation level is STRICT, the self-check command MUST validate that the example artifact passes all template validation rules. This ensures that templates and examples remain synchronized and that templates are valid.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Environment Diagnostics

- [ ] `p2` - **ID**: `cpt-cypilot-fr-core-doctor`

The system MUST provide a `cypilot doctor` command that checks environment health: Python version compatibility, git availability, `gh` CLI authentication status, agent detection (which supported agents are present), config directory integrity validation, skill version status, and kit structural correctness. The command MUST output a clear pass/fail report with actionable remediation steps for each failed check.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Pre-Commit Hook Integration

- [ ] `p3` - **ID**: `cpt-cypilot-fr-core-hooks`

The system MUST provide a `cypilot hook install` command that installs a git pre-commit hook running lightweight validation (`cypilot lint`) on changed artifacts before commit. The hook MUST be fast (≤ 5 seconds for typical changes). The hook MUST be removable via `cypilot hook uninstall`.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Shell Completions

- [ ] `p3` - **ID**: `cpt-cypilot-fr-core-completions`

The system MUST provide shell completion scripts for bash, zsh, and fish. Completions MUST cover all commands, subcommands, and common options. Completions MUST be installable via `cypilot completions install`.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### VS Code Plugin

- [ ] `p2` - **ID**: `cpt-cypilot-fr-core-vscode-plugin`

The system MUST provide a VS Code extension (compatible with VS Code, Cursor, Windsurf) for IDE-native Cypilot support. The plugin MUST provide:

1. **ID Syntax Highlighting** — `cpt-*` identifiers MUST be visually distinguished in Markdown files (definitions, references, and code tags `@cpt-*`) with configurable color scheme.
2. **Go to Definition / Find References** — clicking a `cpt-*` reference MUST navigate to its definition; clicking a definition MUST show all references across the workspace (equivalent to `where-defined` / `where-used`).
3. **Real-Time Validation** — artifact documents MUST be validated on save (or on keystroke with debounce) against their template structure; validation issues MUST appear as VS Code diagnostics (errors, warnings) with inline squiggles and Problems panel entries.
4. **ID Autocompletion** — typing `cpt-` MUST trigger autocompletion with all known IDs from the project registry, grouped by kind (actor, fr, nfr, usecase, etc.).
5. **Hover Information** — hovering over a `cpt-*` ID MUST show a tooltip with: definition location, artifact kind, priority, checked/unchecked status, and first line of content.
6. **Cross-Artifact Link Lens** — CodeLens annotations above ID definitions MUST show reference count and covered_by status (e.g., "3 references · covered by DESIGN, DECOMPOSITION").
7. **Traceability Tree View** — a sidebar panel MUST display the traceability tree: PRD → DESIGN → DECOMPOSITION → FEATURE → CODE, with checked/unchecked status per ID and click-to-navigate.
8. **Validation Status Bar** — the status bar MUST show current artifact validation status (PASS/FAIL with error count) and click to run full validation.
9. **Quick Fix Actions** — common validation issues (missing priority marker, placeholder detected, duplicate ID) MUST offer quick fix suggestions via VS Code Quick Fix API.
10. **Config-Aware** — the plugin MUST read the Cypilot config from the project's install directory to resolve systems, kits, autodetect rules, and ignore lists. The plugin MUST NOT require separate configuration.

The plugin MUST delegate all validation logic to the installed Cypilot skill (`cypilot validate`) to ensure consistency between CLI and IDE results. The plugin MUST support workspace with multiple systems.

**Actors**:
`cpt-cypilot-actor-user`

### 5.2 SDLC Kit

#### Artifact Pipeline

- [ ] `p1` - **ID**: `cpt-cypilot-fr-sdlc-pipeline`

The SDLC kit MUST provide an artifact-first development pipeline: PRD → DESIGN → ADR → DECOMPOSITION → FEATURE → CODE. Each artifact kind MUST have a template, checklist, rules, and at least one example. Each artifact kind MUST be usable independently (no forced sequence). The kit MUST support both greenfield (design-first) and brownfield (code-first) projects.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

#### SDLC Kit

- [ ] `p2` - **ID**: `cpt-cypilot-fr-sdlc-plugin`

The SDLC kit MUST provide a blueprint package with artifact definitions for PRD, DESIGN, ADR, DECOMPOSITION, and FEATURE in `kits/sdlc/blueprints/`. The Blueprint Processor generates all outputs from these blueprints using the core Artifact Blueprint contract (`cpt-cypilot-fr-core-blueprint`). The SDLC kit MUST:

1. **Blueprint definitions** — provide blueprints using SDLC-specific marker types: `@cpt:heading` and `@cpt:id` (→ kit-wide `constraints.toml`), `@cpt:check` (→ `checklist.md`), `@cpt:prompt` (→ `template.md` writing instructions), `@cpt:rule` (→ `rules.md`), `@cpt:example` (→ `example.md`). The `@cpt:heading` + `@cpt:prompt` markers generate `template.md`. Codebase blueprints (without `artifact` key) generate `codebase/rules.md` and `codebase/checklist.md`.
2. **Artifact type control** — the kit owns and controls all its artifact types via blueprints. New artifact types MAY be added by creating a new blueprint `.md` file in the kit's `blueprints/` directory.
3. **SKILL extensions** — blueprints MUST include `@cpt:skill` sections so that SDLC-specific commands and workflows are discoverable by AI agents via the main SKILL.md.
4. **Workflow registrations** — blueprints MUST include `@cpt:workflow` sections that generate workflow files and agent entry points for generate, analyze, and review operations.
5. **Update compatibility** — user customizations in blueprints (in `config/kits/sdlc/blueprints/`) MUST be preserved across kit version updates via the reference-based three-way diff. Conflicts between user changes and kit updates MUST be flagged for manual resolution.

> Kit-specific CLI subcommands, validation hooks, and config extensibility are planned for p2.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Artifact Validation

- [x] `p1` - **ID**: `cpt-cypilot-fr-sdlc-validation`

The SDLC kit MUST provide deterministic structural and semantic validation for all artifact kinds. Validation MUST include: template structure compliance, ID format validation, priority marker presence, placeholder detection (TODO, TBD, FIXME), and cross-reference validation. Validation MUST produce a score breakdown with actionable issues including file paths and line numbers. Pass/fail thresholds MUST be configurable per artifact kind.

**Actors**:
`cpt-cypilot-actor-ai-agent`, `cpt-cypilot-actor-ci-pipeline`

#### Cross-Artifact Validation

- [x] `p1` - **ID**: `cpt-cypilot-fr-sdlc-cross-artifact`

The SDLC kit MUST validate cross-artifact relationships when multiple artifacts are validated together. ID blocks with `covered_by` attributes MUST have at least one reference in artifacts whose kind matches the covered_by list. All ID references MUST resolve to a definition in some artifact. When a reference is marked as checked (`[x]`), the corresponding definition MUST also be marked as checked. Cross-artifact validation MUST be deterministic and report all consistency violations with line numbers and artifact paths.

**Actors**:
`cpt-cypilot-actor-ai-agent`, `cpt-cypilot-actor-ci-pipeline`

#### Code Generation from Design

- [ ] `p2` - **ID**: `cpt-cypilot-fr-sdlc-code-gen`

The SDLC kit MUST provide an implementation workflow that is system-prompt-aware and works with any programming language. The workflow MUST use project system prompts (domain model, API contracts) when present. The workflow MUST add traceability tags when traceability is enabled for the relevant artifacts. The workflow MUST prefer TDD where feasible and follow SOLID principles.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

#### Brownfield Support

- [ ] `p2` - **ID**: `cpt-cypilot-fr-sdlc-brownfield`

The SDLC kit MUST support adding Cypilot to existing projects without disruption. The system MUST auto-detect existing architecture from code and configs. The system MUST support reverse-engineering artifacts from existing documentation and code. The system MUST support incremental adoption (start with config, add artifacts gradually).

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

#### Feature Lifecycle Management

- [ ] `p2` - **ID**: `cpt-cypilot-fr-sdlc-lifecycle`

The SDLC kit MUST track feature status from NOT_STARTED through IN_DESIGN, DESIGNED, READY, IN_PROGRESS to DONE. Feature dependency management MUST detect blocking relationships. Status transition validation MUST prevent skipping states.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

#### Quickstart Guides

- [ ] `p2` - **ID**: `cpt-cypilot-fr-sdlc-guides`

The SDLC kit MUST provide quickstart guides with copy-paste prompts for common workflows. Documentation MUST use progressive disclosure: human-facing overview docs and AI navigation rules for agents.

**Actors**:
`cpt-cypilot-actor-user`

#### PR Review Workflow

- [ ] `p1` - **ID**: `cpt-cypilot-fr-sdlc-pr-review`

The SDLC kit MUST provide a PR review workflow that fetches PR diffs and metadata from GitHub, analyzes changes against configurable prompts and checklists, and produces structured review reports. The workflow MUST always re-fetch data from scratch on each invocation (no caching). Reviews MUST be read-only (no local working tree modifications). The workflow MUST support reviewing a single PR or all open PRs. Reviews MUST include a reviewer comment analysis section assessing existing feedback.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

#### PR Status Workflow

- [ ] `p1` - **ID**: `cpt-cypilot-fr-sdlc-pr-status`

The SDLC kit MUST provide a PR status workflow that generates reports with: severity assessment of unreplied comments (CRITICAL/HIGH/MEDIUM/LOW), resolved-comment audit with suspicious resolution detection, CI and merge conflict status. The workflow MUST auto-fetch latest data before generating each report. The workflow MUST support single PR and ALL modes. Unreplied comments MUST be reordered by severity.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

#### PR Review Configuration

- [ ] `p2` - **ID**: `cpt-cypilot-fr-sdlc-pr-config`

The SDLC kit MUST support per-project PR review configuration with: prompt selection (code review, design review, ADR review, etc.), checklist mapping per review type, domain-specific review criteria, and template variables for project-specific paths. The kit MUST support an exclude list for PRs that should be skipped. Configuration MUST be stored in the kit's config directory (`config/kits/sdlc/`).

**Actors**:
`cpt-cypilot-actor-user`

---

## 6. Non-Functional Requirements

### 6.1 Module-Specific NFRs

#### Validation Performance

- [x] `p2` - **ID**: `cpt-cypilot-nfr-validation-performance`

- Deterministic validation of a single artifact MUST complete in ≤ 3 seconds.
- Full project validation (all artifacts + codebase) SHOULD complete in ≤ 10 seconds for typical repositories (≤ 50k LOC).
- Validation output MUST be clear and actionable with file paths and line numbers.

#### Security and Integrity

- [x] `p1` - **ID**: `cpt-cypilot-nfr-security-integrity`

- Validation MUST NOT execute untrusted code from artifacts.
- Validation MUST produce deterministic results given the same repository state.
- The config directory MUST NOT contain secrets or credentials.

#### Reliability and Recoverability

- [x] `p2` - **ID**: `cpt-cypilot-nfr-reliability-recoverability`

- Validation failures MUST include enough context to remediate without reverse-engineering the validator.
- The system MUST provide actionable guidance for common failure modes.
- Config migration MUST NOT lose user settings.

#### Adoption and Usability

- [x] `p2` - **ID**: `cpt-cypilot-nfr-adoption-usability`

- `cypilot init` MUST complete interactive setup with ≤ 5 user decisions.
- Workflow instructions MUST be executable by a new user without prior Cypilot context, with ≤ 3 clarifying questions per workflow on average.
- All CLI commands MUST provide `--help` with usage examples.

### 6.2 NFR Exclusions

- **Authentication/Authorization** (SEC-PRD-001/002): Not applicable — Cypilot is a local CLI tool, not a multi-user system requiring access control.
- **Availability/Recovery** (REL-PRD-001/002): Not applicable — Cypilot runs locally as a CLI, not as a service requiring uptime guarantees.
- **Scalability** (ARCH-PRD-003): Not applicable — Cypilot processes single repositories locally; traditional scaling does not apply.
- **Throughput/Capacity** (PERF-PRD-002/003): Not applicable — Cypilot is a local development tool, not a high-throughput system.
- **Accessibility/Internationalization** (UX-PRD-002/003): Not applicable — CLI tool for developers; English-only is acceptable.
- **Regulatory/Legal** (COMPL-PRD-001/002/003): Not applicable — Cypilot is a methodology tool with no user data or regulated industry context.
- **Data Ownership/Lifecycle** (DATA-PRD-001/003): Not applicable — Cypilot does not persist user data; artifacts are owned by the project.
- **Support Requirements** (MAINT-PRD-002): Not applicable — open-source tool; support is community-driven.
- **Deployment/Monitoring** (OPS-PRD-001/002): Not applicable — installed locally via pipx; no server deployment or monitoring required.
- **Safety** (SAFE-PRD-001/002): Not applicable — pure information/development tool with no physical interaction or harm potential.

---

## 7. Public Library Interfaces

### 7.1 Public API Surface

#### Cypilot CLI

- [ ] `p1` - **ID**: `cpt-cypilot-interface-cli`

**Type**: CLI (command-line interface)

**Stability**: stable

**Description**: Global `cypilot` command with subcommands delegated to the project-installed skill. All commands output JSON. The CLI is the primary interface for both humans and CI pipelines.

**Breaking Change Policy**: Major version bump required for CLI argument changes; JSON output schema changes require migration period.

### 7.2 External Integration Contracts

#### GitHub API (via `gh` CLI)

- [ ] `p2` - **ID**: `cpt-cypilot-contract-github`

**Direction**: required from client

**Protocol/Format**: GitHub REST/GraphQL API accessed through `gh` CLI

**Compatibility**: Requires `gh` CLI v2.0+; adapts to GitHub API changes through `gh` abstraction layer.

---

## 8. Use Cases

### UC-001 Install Cypilot Globally

**ID**: `cpt-cypilot-usecase-install`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

**Preconditions**: Python 3.10+ and pipx installed

**Flow**:

1. User runs `pipx install git+https://github.com/cyberfabric/cyber-pilot.git`
2. Cypilot CLI proxy is installed globally and available as `cypilot` and `cpt` commands
3. User runs `cypilot --version` — tool downloads the latest release archive from GitHub into `~/.cypilot/cache/` on first run, then displays version

**Alternative Flows**:
- **Download fails**: Tool displays error with HTTP status and retries up to 3 times. If all retries fail, displays: "Failed to download skill bundle. Check network connection and try again."
- **Python version incompatible**: Tool displays: "Python 3.10+ required (found {version})." and exits.

**Postconditions**: `cypilot`/`cpt` commands are available globally; skill bundle cached; all commands are proxied to the cached or project-installed skill

---

### UC-002 Initialize Project

**ID**: `cpt-cypilot-usecase-init`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

**Preconditions**: Git repository exists; `cypilot` is installed globally

**Flow**:

1. User runs `cypilot init` in the project root
2. Tool checks whether Cypilot is already installed in the project
3. Tool asks: "Install directory?" (default: `.cypilot`) — User confirms or changes
4. Tool asks: "Which agents to support?" (default: all) — User selects from windsurf, cursor, claude, copilot, openai
5. Tool copies the skill from the cache (`~/.cypilot/cache/`) into the install directory, installs all available kits (uses capability `cpt-cypilot-fr-core-init`)
6. Tool creates directory structure: skills/, kits/, workflows/, prompts/, schemas/, config/
7. Tool defines root system — derives name and slug from project directory name (uses capability `cpt-cypilot-fr-core-init`)
8. Tool creates `config/core.toml` with project root, root system definition, and kit registrations (uses capability `cpt-cypilot-fr-core-config`)
9. Tool creates `config/artifacts.toml` with fully populated root system entry: default SDLC autodetect rules for standard artifact kinds, codebase entries, and ignore patterns (uses capability `cpt-cypilot-fr-core-config`, `cpt-cypilot-fr-core-kits`)
10. Tool installs all available kits — each kit generates full config in `config/kits/<slug>/` (uses capability `cpt-cypilot-fr-core-kits`)
11. Tool generates agent entry points for selected agents (uses capability `cpt-cypilot-fr-core-agents`)
12. Tool injects `<!-- @cpt:root-agents -->` managed block into project root `AGENTS.md` (creates file if absent) (uses capability `cpt-cypilot-fr-core-init`)
13. Tool creates `config/AGENTS.md` with default WHEN rules for standard system prompts
14. Tool displays: "Cypilot initialized. Start with: `cypilot on` or `cypilot help`"

**Alternative Flows**:
- **Existing installation detected**: Tool displays "Cypilot is already installed at {path} (version {version})." and proposes `cypilot update` if a newer version is available. Does NOT overwrite or modify the existing installation.

**Postconditions**: Project has `.cypilot/` with full structure, config, agent entry points, and root `AGENTS.md` entry; ready for artifact workflows

---

### UC-003 Enable Cypilot in Agent Session

**ID**: `cpt-cypilot-usecase-enable`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

**Preconditions**: Project has Cypilot initialized (`.cypilot/` exists)

**Flow**:

1. User types `cypilot on` in agent chat
2. AI Agent loads SKILL.md, sets `{cypilot_mode}` = `on` (uses capability `cpt-cypilot-fr-core-skill-engine`)
3. AI Agent runs Protocol Guard: checks submodule status, runs `info`
4. AI Agent loads config/AGENTS.md and applicable project config
5. AI Agent announces: "Cypilot Mode Enabled. Config: FOUND at {path}"

**Alternative Flows**:
- **`.cypilot/` not found**: AI Agent announces: "Cypilot not initialized. Run `cypilot init` first." and exits Cypilot mode.
- **SKILL.md or config missing/corrupt**: AI Agent announces: "Cypilot installation incomplete. Run `cypilot doctor` for diagnostics."

**Postconditions**: AI Agent follows Cypilot workflows for subsequent requests; execution logging is active

---

### UC-004 Create Artifact

**ID**: `cpt-cypilot-usecase-create-artifact`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

**Preconditions**: Cypilot mode enabled; kit with target artifact kind is registered

**Flow**:

1. User requests artifact creation (e.g., "create PRD", "generate DESIGN")
2. AI Agent executes generate workflow: loads execution protocol, resolves kit, loads rules/template/checklist/example (uses capability `cpt-cypilot-fr-core-workflows`)
3. AI Agent collects information via batch questions with proposals
4. User approves or modifies proposals
5. AI Agent generates artifact content following template structure and checklist criteria
6. AI Agent presents summary and asks for confirmation
7. User confirms; AI Agent writes file and updates config (uses capability `cpt-cypilot-fr-core-config`)
8. AI Agent runs deterministic validation automatically (uses capability `cpt-cypilot-fr-sdlc-validation`)

**Alternative Flows**:
- **Kit not registered for requested kind**: AI Agent displays available artifact kinds from registered kits and asks user to choose.
- **Validation fails after generation**: AI Agent presents issues and offers to fix them automatically.

**Postconditions**: Artifact file created, registered in config, and validated

---

### UC-005 Validate Artifacts

**ID**: `cpt-cypilot-usecase-validate`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`, `cpt-cypilot-actor-ci-pipeline`

**Preconditions**: Artifacts exist in the project

**Flow**:

1. User or CI runs validation (via agent chat or `cypilot validate`)
2. System runs deterministic structural validation: template compliance, ID formats, placeholders (uses capability `cpt-cypilot-fr-sdlc-validation`)
3. System runs cross-artifact validation: covered_by references, checked consistency (uses capability `cpt-cypilot-fr-sdlc-cross-artifact`)
4. System reports PASS/FAIL with score breakdown and actionable issues

**Postconditions**: Validation report with file paths, line numbers, and remediation guidance

**Alternative Flows**:
- **Validation fails**: User reviews issues, edits artifacts, re-runs validation

---

### UC-006 Implement Feature from Design

**ID**: `cpt-cypilot-usecase-implement`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

**Preconditions**: FEATURE artifact exists with CDSL behavioral specification

**Flow**:

1. User requests implementation of a feature
2. AI Agent loads FEATURE artifact and extracts implementation scope (uses capability `cpt-cypilot-fr-core-cdsl`)
3. AI Agent reads project config for language-specific patterns and conventions (uses capability `cpt-cypilot-fr-sdlc-code-gen`)
4. AI Agent generates code with traceability tags where enabled (uses capability `cpt-cypilot-fr-core-traceability`)
5. User reviews and iterates on generated code
6. AI Agent validates traceability coverage

**Alternative Flows**:
- **FEATURE artifact has invalid or missing CDSL**: AI Agent reports structural issues and suggests running validation or editing the FEATURE artifact first.
- **Traceability validation fails**: AI Agent lists untraced IDs and offers to add missing `@cpt-*` tags.

**Postconditions**: Feature implemented with traceability tags; validation confirms coverage

---

### UC-007 Review PR

**ID**: `cpt-cypilot-usecase-pr-review`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

**Preconditions**: `gh` CLI authenticated; PR exists on GitHub

**Flow**:

1. User requests PR review (e.g., "review PR 123")
2. AI Agent fetches latest PR data: diff, metadata, comments (uses capability `cpt-cypilot-fr-sdlc-pr-review`)
3. AI Agent selects review prompt and checklist based on PR content (uses capability `cpt-cypilot-fr-sdlc-pr-config`)
4. AI Agent analyzes changes against checklist criteria
5. AI Agent analyzes existing reviewer comments for validity and resolution status
6. AI Agent writes structured review report to `.prs/{ID}/review.md`
7. AI Agent presents summary with findings and verdict

**Alternative Flows**:
- **`gh` CLI not authenticated**: AI Agent displays: "GitHub CLI not authenticated. Run `gh auth login` first." and stops.
- **PR not found**: AI Agent displays: "PR #{number} not found in {owner}/{repo}." and stops.

**Postconditions**: Structured review report saved; user has actionable findings

---

### UC-008 Check PR Status

**ID**: `cpt-cypilot-usecase-pr-status`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

**Preconditions**: `gh` CLI authenticated; PR exists on GitHub

**Flow**:

1. User requests PR status (e.g., "PR status 123")
2. AI Agent fetches latest PR data and generates status report (uses capability `cpt-cypilot-fr-sdlc-pr-status`)
3. AI Agent assesses severity of unreplied comments (CRITICAL/HIGH/MEDIUM/LOW)
4. AI Agent audits resolved comments: checks code for actual fixes, detects suspicious resolutions
5. AI Agent reorders report by severity and presents summary

**Alternative Flows**:
- **`gh` CLI not authenticated or PR not found**: Same as UC-007 alternative flows.

**Postconditions**: Status report with severity distribution, suspicious resolutions flagged, actionable next steps

---

### UC-009 Configure Project via CLI

**ID**: `cpt-cypilot-usecase-configure`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

**Preconditions**: Cypilot initialized in project

**Flow**:

1. User uses CLI to modify configuration. Core commands manage `core.toml` (e.g., `cypilot config system add --name "Backend" --slug backend --kit sdlc`). Kit-specific config commands (p2) will manage kit config (e.g., `cypilot sdlc autodetect add-artifact --system backend --kind API --pattern "api/**/*.yaml" --traceability DOCS-ONLY`)
2. Tool validates the change against the config schema (uses capability `cpt-cypilot-fr-core-cli-config`)
3. Tool applies the change to the appropriate config file in `config/` (uses capability `cpt-cypilot-fr-core-config`)
4. Tool confirms the change with a summary of what was modified

**Alternative Flows**:
- **Schema validation fails**: Tool displays the specific validation error, shows the attempted change, and does NOT apply it. Suggests corrected syntax.
- **Dry-run mode**: User adds `--dry-run` flag; tool displays what would change without applying.

**Postconditions**: Config updated; change is reflected in subsequent validations and workflows

---

### UC-010 Register or Extend a Kit

**ID**: `cpt-cypilot-usecase-kit-manage`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

**Preconditions**: Cypilot initialized in project

**Flow**:

1. User installs a new kit or extends an existing one (e.g., `cypilot kit install sdlc`)
2. Tool saves kit source to `{cypilot_path}/.core/kits/{slug}/` (reference copy)
3. Tool copies blueprints from `{cypilot_path}/.core/kits/{slug}/blueprints/` to `config/kits/{slug}/blueprints/` (user-editable)
4. Blueprint Processor generates all outputs into `config/kits/{slug}/artifacts/` and `config/kits/{slug}/workflows/`
5. Tool registers the kit in `config/core.toml`
6. Tool validates kit structural correctness

**Alternative Flows**:
- **Kit invalid**: Tool displays structural validation errors (missing `blueprints/` directory, invalid blueprint files) and does NOT register the kit. Suggests `cypilot doctor` for diagnostics.
- **Kit already installed**: Tool displays current version and offers to update or skip.

**Postconditions**: Kit registered/extended and available for workflows

---

### UC-011 Update Cypilot Version

**ID**: `cpt-cypilot-usecase-update`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

**Preconditions**: Cypilot installed globally and in project

**Flow**:

1. On any command invocation, the proxy displays: "Cypilot {cached_version} available (project has {project_version}). Run `cypilot update` to upgrade." (uses capability `cpt-cypilot-fr-core-installer`)
2. User runs `cypilot update`
3. Tool refreshes cache from the latest GitHub release if needed, then copies the cached skill into the project (uses capability `cpt-cypilot-fr-core-version`)
4. Tool migrates `config/core.toml` preserving all user settings; invokes each kit's migration script for `config/kits/<slug>/` (uses capability `cpt-cypilot-fr-core-config`, `cpt-cypilot-fr-core-kits`)
5. Tool regenerates agent entry points for compatibility (uses capability `cpt-cypilot-fr-core-agents`)

**Alternative Flows**:
- **Cache download fails**: Tool displays network error and suggests retrying or using `cypilot update --check` to verify availability.
- **Config migration conflict**: Tool preserves a backup of the previous config, applies migration, and reports any settings that could not be automatically migrated.

**Postconditions**: Project skill updated to cached version; config migrated; agent entry points refreshed

---

### UC-012 Migrate Existing Project

**ID**: `cpt-cypilot-usecase-migrate`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

**Preconditions**: Existing project with code but no Cypilot artifacts

**Flow**:

1. User runs `cypilot init` in existing project (uses capability `cpt-cypilot-fr-core-init`)
2. Tool detects existing code (brownfield) and offers reverse-engineering scan (uses capability `cpt-cypilot-fr-sdlc-brownfield`)
3. AI Agent analyzes code structure, configs, and documentation
4. AI Agent proposes project config (tech stack, conventions, domain model)
5. User reviews and approves proposed specs
6. AI Agent creates initial artifacts from discovered patterns
7. User adds traceability tags incrementally (uses capability `cpt-cypilot-fr-core-traceability`)

**Alternative Flows**:
- **No code detected (greenfield)**: Tool skips reverse-engineering scan and proceeds with standard init flow (UC-002).
- **User rejects proposed specs**: AI Agent saves partial specs as drafts and allows the user to edit manually before committing.

**Postconditions**: Existing project has Cypilot config and initial artifacts; team can use workflows for new development

---

## 9. Acceptance Criteria

- [ ] `cypilot init` completes interactive setup and creates a working `.cypilot/` directory in ≤ 5 minutes
- [ ] Deterministic validation output is actionable (clear file/line/pointer for every issue)
- [ ] All supported agents receive correct entry points after `cypilot agents`
- [ ] `cypilot doctor` reports environment health with pass/fail per check
- [ ] Config is never manually edited — all changes go through the CLI tool
- [ ] PR review workflow produces a structured report matching the template format

## 10. Dependencies

| Dependency | Description | Criticality |
|------------|-------------|-------------|
| Python 3.10+ | Runtime for CLI tool and skill engine | p1 |
| Git | Project detection, skill installation, version control | p1 |
| pipx | Global CLI installation (recommended) | p2 |
| gh CLI | GitHub API access for PR review/status workflows | p2 |

## 11. Assumptions

- AI coding assistants (Windsurf, Cursor, Claude, Copilot) can follow structured markdown workflows with embedded instructions.
- Developers have access to Python 3.10+ for running the Cypilot CLI tool.
- Projects use Git for version control (project detection relies on `.git` directory).
- Teams are willing to maintain design artifacts as part of their development workflow.
- The `pipx` package manager is available or installable for global CLI installation.
- GitHub is the primary VCS platform for PR review workflows (other platforms may be supported later).

### Open Questions

No open questions remain at this time — all architectural questions (config directory structure, kit structure, PR review placement in SDLC kit) were resolved during PRD development.

## 12. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| AI agent variability | Inconsistent artifact quality across different agents | Deterministic validation catches structural issues; checklists enforce quality baseline |
| Adoption resistance | Teams bypass the workflow or skip validation | Incremental adoption via brownfield support; immediate value from validation and PR review |
| Kit rigidity | Templates don't fit all project types | Kit extension system allows custom overrides; custom kits can be created from scratch |
| Version fragmentation | Different team members have different skill versions | Version detection on every invocation; config migration ensures backward compatibility |
| Git dependency for skill updates | Network required for skill installation and updates | Skill is installed once and works offline; updates are optional and explicit |
