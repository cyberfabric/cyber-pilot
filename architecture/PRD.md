# PRD — Cyber Pilot (Cypilot)


<!-- toc -->

- [1. Overview](#1-overview)
  - [1.1 Purpose](#11-purpose)
  - [1.2 Background / Problem Statement](#12-background-problem-statement)
  - [1.3 Goals (Business Outcomes)](#13-goals-business-outcomes)
  - [1.4 Glossary](#14-glossary)
- [2. Actors](#2-actors)
  - [2.1 Human Actors](#21-human-actors)
  - [2.2 System Actors](#22-system-actors)
- [3. Operational Concept & Environment](#3-operational-concept-environment)
  - [3.1 Module-Specific Environment Constraints](#31-module-specific-environment-constraints)
- [4. Scope](#4-scope)
  - [4.1 In Scope](#41-in-scope)
  - [4.2 Out of Scope](#42-out-of-scope)
- [5. Functional Requirements](#5-functional-requirements)
  - [5.1 Core](#51-core)
  - [5.2 SDLC Kit (EXTRACTED — External Package)](#52-sdlc-kit-extracted-external-package)
- [6. Non-Functional Requirements](#6-non-functional-requirements)
  - [6.1 Module-Specific NFRs](#61-module-specific-nfrs)
  - [6.2 NFR Exclusions](#62-nfr-exclusions)
- [7. Public Library Interfaces](#7-public-library-interfaces)
  - [7.1 Public API Surface](#71-public-api-surface)
  - [7.2 External Integration Contracts](#72-external-integration-contracts)
- [8. Use Cases](#8-use-cases)
  - [UC-001 Install Cypilot Globally](#uc-001-install-cypilot-globally)
  - [UC-002 Initialize Project](#uc-002-initialize-project)
  - [UC-003 Enable Cypilot in Agent Session](#uc-003-enable-cypilot-in-agent-session)
  - [UC-004 Create Artifact](#uc-004-create-artifact)
  - [UC-005 Validate Artifacts](#uc-005-validate-artifacts)
  - [UC-006 Implement Feature from Design](#uc-006-implement-feature-from-design)
  - [UC-007 Review PR](#uc-007-review-pr)
  - [UC-008 Check PR Status](#uc-008-check-pr-status)
  - [UC-009 Configure Project via CLI](#uc-009-configure-project-via-cli)
  - [UC-010 Register or Extend a Kit](#uc-010-register-or-extend-a-kit)
  - [UC-011 Update Cypilot Version](#uc-011-update-cypilot-version)
  - [UC-012 Migrate Existing Project](#uc-012-migrate-existing-project)
- [9. Acceptance Criteria](#9-acceptance-criteria)
- [10. Dependencies](#10-dependencies)
- [11. Assumptions](#11-assumptions)
  - [Open Questions](#open-questions)
- [12. Risks](#12-risks)

<!-- /toc -->

## 1. Overview

### 1.1 Purpose

Cypilot is a deterministic agent tool that embeds into AI coding assistants and CI pipelines to provide structured workflows, artifact validation, and design-to-code traceability. Cypilot maximizes determinism: everything that can be validated, checked, or enforced without an LLM is handled deterministically; the LLM is reserved only for tasks that require reasoning, creativity, or natural language understanding.

The system is a single-layer generic engine:

- **Core** — deterministic command engine, generic workflows (generate/analyze), multi-agent integrations, global CLI, project configuration management, extensible kit system with GitHub-based kit installation, ID/traceability infrastructure, and Cypilot DSL (CDSL) for behavioral specifications

Domain-specific value is delivered by independently installable kits. The recommended SDLC kit (`cyberfabric/cyber-pilot-kit-sdlc`) provides an artifact-first development pipeline (PRD → DESIGN → ADR → DECOMPOSITION → FEATURE → CODE) with templates, checklists, examples, deterministic validation, cross-artifact consistency checks, and GitHub PR review/status workflows. Kits are external packages — Cypilot core contains no domain-specific content.

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
- A new user can install Cypilot globally and initialize a project in ≤ 5 minutes. (Baseline: not measured; Target: v2.0)
- Deterministic validation of any single artifact completes in ≤ 3 seconds on a typical developer laptop. (Baseline: ~1s current; Target: v2.0)
- 100% of `cpt-*` IDs defined in artifacts are resolvable via deterministic search without ambiguity. (Baseline: 100% current; Target: v2.0)
- Agent integration files for all supported agents are generated in ≤ 10 seconds. (Baseline: ~5s current; Target: v2.0)
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
| Skill | The core package installed in a project's install directory, containing all commands, validation logic, and utilities |
| Kit | Independently installable package of templates, checklists, rules, examples, and constraints for a domain (e.g., SDLC); installed from GitHub repositories |
| Config | Tool-managed configuration directory inside the install directory, containing project settings and per-kit configs |
| CDSL | Cypilot DSL — plain English behavioral specification language for actor flows and algorithms |
| Traceability | Linking design elements to code via unique identifiers and code tags |
| System Prompt | Project-specific context file (tech-stack, conventions, domain model) loaded by workflows conditionally |
| Agent Entry Point | Agent-specific file (workflow proxy, skill shim, or rule file) generated in the agent's native format |

---

## 2. Actors

### 2.1 Human Actors

#### User

**ID**: `cpt-cypilot-actor-user`

**Role**: Primary user of Cypilot. Uses the tool through AI agent chats and CLI to: create and validate artifacts, implement features with traceability, configure the project, review PRs against configurable checklists, and manage project conventions.

### 2.2 System Actors

#### AI Agent

**ID**: `cpt-cypilot-actor-ai-agent`

**Role**: Executes Cypilot workflows (generate, analyze, PR review) by following SKILL.md instructions, loading rules and templates, and producing structured output. Supported agents: Windsurf, Cursor, Claude, Copilot, OpenAI.

#### CI/CD Pipeline

**ID**: `cpt-cypilot-actor-ci-pipeline`

**Role**: Runs deterministic validation and PR review automatically on commits and pull requests. Reports results as status checks and blocks merges on failure.

#### Cypilot CLI

**ID**: `cpt-cypilot-actor-cypilot-cli`

**Role**: Global command-line tool installable with a single command. Provides project initialization, version management, and access to all Cypilot commands. Detects version mismatches and proposes updates.

---

## 3. Operational Concept & Environment

### 3.1 Module-Specific Environment Constraints

- The tool MUST run cross-platform (Linux, macOS, Windows) with minimal runtime dependencies
- Git required for project detection and version control
- GitHub integration required for PR review/status workflows
- Global installation MUST be achievable with a single command

---

## 4. Scope

### 4.1 In Scope

- Global CLI tool with single-command installation and project-specific command delegation
- Interactive project initialization with directory, agent, kit selection
- Tool-managed configuration directory with core configs and per-kit outputs (user-editable)
- Kit files — all user-editable, preserved via interactive diff on update
- Deterministic skill engine with machine-readable output for all commands
- Structured workflows for write and read operations with execution protocol
- Multi-agent integration (Windsurf, Cursor, Claude, Copilot, OpenAI)
- Extensible kit system with GitHub-based installation, registration, extension, and custom kit creation
- ID and traceability system with code tags, search, and validation
- CDSL behavioral specification language
- Version detection, update proposals (tool-only), config directory migration, and kit config relocation
- Interactive diff for kit file updates with conflict resolution
- Kit prompt during project initialization (SDLC kit offered with accept/decline)
- Rich CLI for configuration management (autodetect, artifacts, ignore lists, kits, constraints)
- Environment diagnostics
- Pre-commit hook integration

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

- [x] `p1` - **ID**: `cpt-cypilot-fr-core-installer`

The system MUST provide a global CLI tool installable with a single command. The tool MUST be available as both `cypilot` and the short alias `cpt`. The tool MUST:

1. Work both inside and outside projects.
2. Work offline after initial setup.
3. Perform non-blocking version checks — never delay command execution. Propose updates when a newer version is available.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Project Initialization

- [x] `p1` - **ID**: `cpt-cypilot-fr-core-init`

The system MUST provide an interactive project initialization command that bootstraps Cypilot in a project. The command MUST:

1. Check for existing installation and refuse to overwrite — propose updating instead.
2. Ask for: installation directory, which agents to support (default: all), and per-kit config output directory.
3. Enable all available kits by default.
4. Set up the project directory structure.
5. Define a **root system** — deriving the project name and slug from the project directory name.
6. Create project configuration with default artifact discovery rules for all registered kit artifact kinds.
7. Install all available kits by copying kit files into their config directories.
8. Generate agent entry points for all selected agents.
9. Inject a managed navigation block into the project root `AGENTS.md` (creating the file if absent) so that AI agents are automatically routed to Cypilot. Every subsequent CLI invocation MUST verify this block exists and is correct.
10. Support non-interactive mode for CI/scripting. After completion, display a prompt suggestion.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Config Directory

- [x] `p1` - **ID**: `cpt-cypilot-fr-core-config`

The system MUST maintain a structured project configuration. The system MUST:

1. Store all configuration in human-readable format. Config files MUST be edited exclusively by the tool — never by humans directly. Config changes MUST produce clean version-control diffs.
2. Provide per-kit file directories (path configurable per kit) containing all kit files — all user-editable. On update, changed files MUST be presented via interactive diff (see `cpt-cypilot-fr-core-resource-diff`).
3. Support automatic config migration between versions when the tool is updated.
4. Support artifact discovery rules for hierarchical monorepos where systems can be nested.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Deterministic Skill Engine

- [x] `p1` - **ID**: `cpt-cypilot-fr-core-skill-engine`

The system MUST provide a deterministic command engine. All validation, scanning, and transformation logic MUST be deterministic (same input → same output). All commands MUST support both human-readable and machine-readable output for CI integration.

**Actors**:
`cpt-cypilot-actor-ai-agent`, `cpt-cypilot-actor-ci-pipeline`, `cpt-cypilot-actor-cypilot-cli`

#### Generic Workflows

- [x] `p1` - **ID**: `cpt-cypilot-fr-core-workflows`

The system MUST provide structured workflows for write operations (create, edit, fix, update, implement) and read operations (validate, review, check, inspect, audit). Workflows MUST be portable across projects without hardcoded paths. Workflows MUST support transparent execution logging so users can observe agent reasoning.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

#### Multi-Agent Integration

- [x] `p1` - **ID**: `cpt-cypilot-fr-core-agents`

The system MUST provide a command that generates integration files for all supported AI coding assistants so each agent can access Cypilot workflows. Supported agents MUST include Windsurf, Cursor, Claude, Copilot, and OpenAI. The command MUST support regenerating integration files for a specific agent or for all agents at once. The command always fully regenerates integration files on each invocation.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`, `cpt-cypilot-actor-cypilot-cli`

#### Extensible Kit System

- [x] `p1` - **ID**: `cpt-cypilot-fr-core-kits`

The system MUST support extensible kit packages installable from GitHub repositories. Each kit is a file package containing:

1. **Kit files** — per-artifact directories with rules, templates, checklists, and examples, plus kit-wide constraint definitions, version metadata, and optional directories for workflows, scripts, and codebase rules. All files are user-editable.
2. **Installation from GitHub** — the tool MUST support installing kits from GitHub repositories. The tool MUST ask the user for the kit config output directory. The tool MUST copy all kit files from the downloaded source and register the kit in project configuration with the GitHub source and version.
3. **GitHub-based versioning** — each kit MUST be versioned via GitHub tags/releases. The kit's source (`github:<owner>/<repo>`) and version (GitHub tag) MUST be stored in `core.toml` kit section.
4. **Update with file-level diff** — the tool MUST support two update modes: **force** (overwrites all kit files) and **interactive** (default, uses file-level diff with resolution modes — see `cpt-cypilot-fr-core-resource-diff`). Kit updates download the new version from GitHub.
5. **SKILL extensions** — a kit MAY extend the core agent entry point with kit-specific commands and workflows.
6. **System prompt extensions** — a kit MAY include agent configuration content that is automatically loaded when the kit's artifacts or workflows are used.
7. **Workflow registrations** — a kit MAY include workflow files that generate agent entry points.
8. **Kit config relocation** — the system MUST provide a command to move a kit's config directory to a new location, update project configuration, and preserve all user edits.
9. **Kit prompt during init** — during project initialization, the tool MUST offer to install the recommended SDLC kit with an accept/decline prompt. If accepted, the kit is downloaded and installed inline. If declined, the user can install it later. In non-interactive mode, the prompt is skipped.

**User extensibility**: users MUST be able to edit any kit file. User modifications MUST be preserved across interactive kit updates via file-level diff.

The system MUST provide CLI commands to: install kits from GitHub, update kits, move kit config, create new custom kits, and validate kit structure. The tool MUST NOT bundle any domain-specific kits.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Generated Resource Editing & Interactive Diff

- [x] `p1` - **ID**: `cpt-cypilot-fr-core-resource-diff`

All kit files in the kit's config directory MUST be user-editable. Users MAY freely modify any kit file at any time. On kit update, the system MUST compare the new version of each file against the user's installed copy. **IF** the content is identical → no action needed. **IF** the content differs → the system MUST present an interactive diff allowing the user to accept, reject, or manually merge each change. The system MUST support batch accept/reject for all remaining files. The system MUST NOT accept a file with unresolved conflicts.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Directory Layout Migration

- [ ] `p1` - **ID**: `cpt-cypilot-fr-core-layout-migration`

The system MUST automatically restructure the directory layout during updates when an old layout is detected. The migration MUST:

1. Move kit files from old locations to the current layout structure.
2. Remove obsolete directories.
3. Update project configuration with new paths.

The migration MUST NOT lose any user modifications to kit files. The migration MUST create a backup before proceeding. If migration fails, the backup MUST be restored and the user notified with actionable guidance.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### ID and Traceability System

- [x] `p1` - **ID**: `cpt-cypilot-fr-core-traceability`

The system MUST provide a unique identifier system for all design elements with search, validation, and cross-reference resolution. The system MUST:

1. Support code tags linking implementation to design for bidirectional traceability.
2. Provide configurable traceability validation levels per artifact.
3. Provide search and query commands: list IDs, list ID kinds, get content, find definitions, find usages.
4. Support ID versioning — when an ID is replaced, references MUST be updated across all artifacts and code.
5. Validate cross-artifact consistency: all cross-references resolve, and checked references imply checked definitions.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`, `cpt-cypilot-actor-ci-pipeline`

#### Cypilot DSL (CDSL)

- [x] `p1` - **ID**: `cpt-cypilot-fr-core-cdsl`

The system MUST define a plain English behavioral specification language (CDSL) for actor flows, algorithms, and state descriptions. CDSL MUST be readable by non-programmers for validation and review. CDSL MUST translate directly to code with traceability tags. CDSL MUST be actor-centric. CDSL MUST support implementation tracking so teams can monitor progress per specification.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

#### Version Detection and Updates

- [ ] `p2` - **ID**: `cpt-cypilot-fr-core-version`

The system MUST provide a project update command that updates the project tool (skill) to the latest available version. The update MUST:

1. Automatically migrate project configuration between versions, preserving all user settings.
2. Detect the directory layout version and trigger layout migration if needed (see `cpt-cypilot-fr-core-layout-migration`).
3. Regenerate agent integration files for compatibility.
4. Migrate bundled kit references to GitHub sources for projects upgrading from versions < 3.0.8.

The update command MUST NOT update kit files — kit updates are a separate operation. Version information MUST be accessible via a version query. The system MUST support checking for available updates without applying them.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### CLI Configuration Interface

- [ ] `p2` - **ID**: `cpt-cypilot-fr-core-cli-config`

The system MUST provide rich CLI commands for project configuration without manual file editing. Core CLI commands MUST support: managing system definitions (add/remove/rename systems, assign kits), managing the ignore list (add/remove patterns with reasons), and registering/installing kits. Kit-specific config changes MUST be delegated to the kit's plugin CLI commands. All config changes MUST go through the tool to maintain config integrity and versioning. The CLI MUST provide dry-run mode for config changes and support reading current config values.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Template Quality Assurance

- [ ] `p2` - **ID**: `cpt-cypilot-fr-core-template-qa`

The system MUST provide a template quality assurance capability that validates example artifacts against their templates. The validation MUST ensure that the example artifact passes all template validation rules. This ensures that templates and examples remain synchronized and that templates are valid.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Table of Contents Management

- [x] `p1` - **ID**: `cpt-cypilot-fr-core-toc`

The system MUST provide table of contents generation and validation for Markdown files. TOC generation MUST create or update table of contents blocks with configurable heading level ranges. TOC validation MUST verify that TOC exists, anchors point to real headings, all headings are covered, and the TOC is not stale. Both operations MUST support batch processing of multiple files.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Environment Diagnostics

- [ ] `p2` - **ID**: `cpt-cypilot-fr-core-doctor`

The system MUST provide an environment diagnostics command that checks environment health: runtime prerequisites, git availability, GitHub integration status, agent detection (which supported agents are present), config integrity validation, installed version status, and kit structural correctness. The command MUST output a clear pass/fail report with actionable remediation steps for each failed check.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Pre-Commit Hook Integration

- [ ] `p3` - **ID**: `cpt-cypilot-fr-core-hooks`

The system MUST provide a pre-commit hook that runs lightweight validation on changed artifacts before commit. The hook MUST be fast (≤ 5 seconds for typical changes). The system MUST support installing and uninstalling the hook.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### Shell Completions

- [ ] `p3` - **ID**: `cpt-cypilot-fr-core-completions`

The system MUST provide shell completion scripts for bash, zsh, and fish. Completions MUST cover all commands, subcommands, and common options. The system MUST support installing completions for the user's shell.

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

#### VS Code Plugin

- [ ] `p2` - **ID**: `cpt-cypilot-fr-core-vscode-plugin`

The system MUST provide a VS Code extension (compatible with VS Code, Cursor, Windsurf) for IDE-native Cypilot support. The plugin MUST provide:

1. **ID Syntax Highlighting** — `cpt-*` identifiers MUST be visually distinguished in Markdown files (definitions, references, and code tags `@cpt-*`) with configurable color scheme.
2. **Go to Definition / Find References** — clicking a `cpt-*` reference MUST navigate to its definition; clicking a definition MUST show all references across the workspace (equivalent to `where-defined` / `where-used`).
3. **Real-Time Validation** — artifact documents MUST be validated on save (or on keystroke with debounce) against their template structure; validation issues MUST appear inline in the editor with a summary in the problems panel.
4. **ID Autocompletion** — typing `cpt-` MUST trigger autocompletion with all known IDs from the project registry, grouped by kind (actor, fr, nfr, usecase, etc.).
5. **Hover Information** — hovering over a `cpt-*` ID MUST show a tooltip with: definition location, artifact kind, priority, checked/unchecked status, and first line of content.
6. **Cross-Artifact Link Lens** — annotations above ID definitions MUST show reference count and coverage status (e.g., "3 references · covered by DESIGN, DECOMPOSITION").
7. **Traceability Tree View** — a sidebar panel MUST display the traceability tree: PRD → DESIGN → DECOMPOSITION → FEATURE → CODE, with checked/unchecked status per ID and click-to-navigate.
8. **Validation Status Bar** — the status bar MUST show current artifact validation status (PASS/FAIL with error count) and click to run full validation.
9. **Quick Fix Actions** — common validation issues (missing priority marker, placeholder detected, duplicate ID) MUST offer quick fix suggestions inline.
10. **Config-Aware** — the plugin MUST read the Cypilot config from the project's install directory to resolve systems, kits, autodetect rules, and ignore lists. The plugin MUST NOT require separate configuration.

The plugin MUST delegate all validation logic to the installed Cypilot CLI to ensure consistency between CLI and IDE results. The plugin MUST support workspaces with multiple systems.

**Actors**:
`cpt-cypilot-actor-user`

### 5.2 SDLC Kit (EXTRACTED — External Package)

> **EXTRACTED**: The SDLC kit has been extracted to a separate GitHub repository (`cyberfabric/cyber-pilot-kit-sdlc`). See ADR-0013 for details. All SDLC-specific functional requirements are now owned by the kit's own repository. Cypilot core knows only that the SDLC kit exists and is offered for installation during project initialization.
>
> All `cpt-cypilot-fr-sdlc-*` requirement IDs (pipeline, plugin, validation, cross-artifact, code-gen, brownfield, lifecycle, guides, pr-review, pr-status, pr-config) have been moved to the kit repository.

---

## 6. Non-Functional Requirements

### 6.1 Module-Specific NFRs

#### DRY Configuration

- [x] `p1` - **ID**: `cpt-cypilot-nfr-dry`

- Every rule or pattern MUST be configured in exactly one place — never duplicated across files or sections.
- Similar rules MUST be merged into more generic ones when they share the same intent.
- Kit constraints, templates, and rules MUST NOT repeat information already captured in the config.

#### Simplicity (Occam's Razor)

- [x] `p1` - **ID**: `cpt-cypilot-nfr-simplicity`

- The system MUST NOT introduce new rules or abstractions if the problem can be solved by an existing one.
- Installation dependencies MUST be minimal.
- Configuration syntax MUST be intuitive and readable without documentation.

#### CI & Automation First

- [x] `p1` - **ID**: `cpt-cypilot-nfr-ci-automation-first`

- The system MUST be a CLI tool with a config file — usable in CI pipelines without human interaction.
- All typical operations (validation, scanning, reporting) MUST be deterministic and automatable.
- LLM-based reasoning MUST be the last resort — used only for tasks that require creativity or natural language understanding.

#### Zero Harm

- [x] `p1` - **ID**: `cpt-cypilot-nfr-zero-harm`

- The tool MUST support custom SDLC pipelines and artifacts — not impose a single process.
- The tool MUST allow people to continue maintaining their artifacts manually if they choose.
- Low cognitive load: a new user MUST be able to configure everything in ≤ 5 minutes.
- Self-troubleshooting: a user MUST be able to diagnose any problem in ≤ 5 minutes.
- The tool MUST follow the lint pattern: harmless, configurable, advisory.
- The tool MUST NOT break code, builds, or tests under any circumstances.
- The tool MUST NOT define a process — it helps automate the user's existing process.
- The tool MAY offer best practices for users who don't have an existing process.

#### No Manual Maintenance

- [x] `p1` - **ID**: `cpt-cypilot-nfr-upgradability`

- The tool MUST be upgradeable with a single command.
- Upgrades MUST be backward compatible — no user action required beyond running the update command.
- User customizations to kit files MUST be preserved across upgrades (see `cpt-cypilot-fr-core-resource-diff`).

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

- Project initialization MUST complete interactive setup with ≤ 5 user decisions.
- Workflow instructions MUST be executable by a new user without prior Cypilot context, with ≤ 3 clarifying questions per workflow on average.
- All CLI commands MUST provide built-in help with usage examples.

### 6.2 NFR Exclusions

- **Authentication/Authorization** (SEC-PRD-001/002): Not applicable — Cypilot is a local CLI tool, not a multi-user system requiring access control.
- **Availability/Recovery** (REL-PRD-001/002): Not applicable — Cypilot runs locally as a CLI, not as a service requiring uptime guarantees.
- **Scalability** (ARCH-PRD-003): Not applicable — Cypilot processes single repositories locally; traditional scaling does not apply.
- **Throughput/Capacity** (PERF-PRD-002/003): Not applicable — Cypilot is a local development tool, not a high-throughput system.
- **Accessibility/Internationalization** (UX-PRD-002/003): Not applicable — CLI tool for developers; English-only is acceptable.
- **Regulatory/Legal** (COMPL-PRD-001/002/003): Not applicable — Cypilot is a methodology tool with no user data or regulated industry context.
- **Data Ownership/Lifecycle** (DATA-PRD-001/003): Not applicable — Cypilot does not persist user data; artifacts are owned by the project.
- **Support Requirements** (MAINT-PRD-002): Not applicable — open-source tool; support is community-driven.
- **Deployment/Monitoring** (OPS-PRD-001/002): Not applicable — installed locally; no server deployment or monitoring required.
- **Safety** (SAFE-PRD-001/002): Not applicable — pure information/development tool with no physical interaction or harm potential.

---

## 7. Public Library Interfaces

### 7.1 Public API Surface

#### Cypilot CLI

- [ ] `p1` - **ID**: `cpt-cypilot-interface-cli`

**Type**: CLI (command-line interface)

**Stability**: stable

**Description**: Global `cypilot` command with subcommands for all Cypilot operations. All commands support both human-readable and machine-readable output. The CLI is the primary interface for both humans and CI pipelines.

**Breaking Change Policy**: Backward-incompatible changes require a major version bump with a migration period.

### 7.2 External Integration Contracts

#### GitHub API Integration

- [ ] `p2` - **ID**: `cpt-cypilot-contract-github`

**Direction**: required from client

**Protocol/Format**: GitHub API

**Compatibility**: Adapts to GitHub API changes through an abstraction layer.

---

## 8. Use Cases

### UC-001 Install Cypilot Globally

**ID**: `cpt-cypilot-usecase-install`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

**Preconditions**: Runtime prerequisites met

**Flow**:

1. User installs Cypilot globally with a single command
2. Cypilot CLI is available as `cypilot` and `cpt` commands
3. User verifies installation — tool sets up on first run, then displays version

**Alternative Flows**:
- **Download fails**: Tool displays error and retries. If all retries fail, displays actionable error message.
- **Runtime incompatible**: Tool displays requirements and exits.

**Postconditions**: `cypilot`/`cpt` commands are available globally; all Cypilot commands are functional

---

### UC-002 Initialize Project

**ID**: `cpt-cypilot-usecase-init`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

**Preconditions**: Git repository exists; `cypilot` is installed globally

**Flow**:

1. User runs project initialization in the project root
2. Tool checks whether Cypilot is already installed in the project
3. Tool asks for install directory and which agents to support
4. Tool sets up the project: creates configuration, generates agent integration files
5. Tool injects navigation block into project root `AGENTS.md` so AI agents discover Cypilot automatically
6. Tool prompts: `Install SDLC kit? [a]ccept [d]ecline` — if accepted, downloads and installs the kit inline
7. Tool displays prompt suggestion for next steps

**Alternative Flows**:
- **Existing installation detected**: Tool displays current installation info and proposes updating if a newer version is available. Does NOT overwrite or modify the existing installation.

**Postconditions**: Project is set up with configuration and agent integration; SDLC kit installed if user accepted the prompt

---

### UC-003 Enable Cypilot in Agent Session

**ID**: `cpt-cypilot-usecase-enable`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

**Preconditions**: Project has Cypilot initialized (`{cypilot_path}/` exists)

**Flow**:

1. User types `cypilot on` in agent chat
2. AI Agent activates Cypilot mode: loads project configuration and verifies installation health
3. AI Agent announces: "Cypilot Mode Enabled. Config: FOUND at {path}"

**Alternative Flows**:
- **Cypilot not initialized**: AI Agent announces that Cypilot is not initialized and exits Cypilot mode.
- **Installation incomplete or corrupt**: AI Agent announces that the installation is incomplete and suggests running diagnostics.

**Postconditions**: AI Agent follows Cypilot workflows for subsequent requests; execution logging is active

---

### UC-004 Create Artifact

**ID**: `cpt-cypilot-usecase-create-artifact`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

**Preconditions**: Cypilot mode enabled; kit with target artifact kind is registered

**Flow**:

1. User requests artifact creation (e.g., "create PRD", "generate DESIGN")
2. AI Agent loads the appropriate template, checklist, and examples for the requested artifact kind (uses capability `cpt-cypilot-fr-core-workflows`)
3. AI Agent collects information via batch questions with proposals
4. User approves or modifies proposals
5. AI Agent generates artifact content following template structure and checklist criteria
6. AI Agent presents summary and asks for confirmation
7. User confirms; AI Agent writes file and updates config (uses capability `cpt-cypilot-fr-core-config`)
8. AI Agent runs deterministic validation automatically (uses capability `cpt-cypilot-fr-core-traceability`)

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

1. User or CI runs validation (via agent chat or CLI)
2. System runs deterministic structural validation: template compliance, ID formats, placeholders (uses capability `cpt-cypilot-fr-core-traceability`)
3. System runs cross-artifact validation: cross-references, checked consistency (uses capability `cpt-cypilot-fr-core-traceability`)
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
3. AI Agent reads project config for language-specific patterns and conventions (SDLC kit capability)
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

**Preconditions**: GitHub integration authenticated; PR exists on GitHub

**Flow**:

1. User requests PR review (e.g., "review PR 123")
2. AI Agent fetches latest PR data: diff, metadata, comments (SDLC kit capability)
3. AI Agent selects review prompt and checklist based on PR content (SDLC kit capability)
4. AI Agent analyzes changes against checklist criteria
5. AI Agent analyzes existing reviewer comments for validity and resolution status
6. AI Agent writes structured review report
7. AI Agent presents summary with findings and verdict

**Alternative Flows**:
- **GitHub integration not authenticated**: AI Agent displays authentication guidance and stops.
- **PR not found**: AI Agent displays error with PR number and repository and stops.

**Postconditions**: Structured review report saved; user has actionable findings

---

### UC-008 Check PR Status

**ID**: `cpt-cypilot-usecase-pr-status`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

**Preconditions**: GitHub integration authenticated; PR exists on GitHub

**Flow**:

1. User requests PR status (e.g., "PR status 123")
2. AI Agent fetches latest PR data and generates status report (SDLC kit capability)
3. AI Agent assesses severity of unreplied comments (CRITICAL/HIGH/MEDIUM/LOW)
4. AI Agent audits resolved comments: checks code for actual fixes, detects suspicious resolutions
5. AI Agent reorders report by severity and presents summary

**Alternative Flows**:
- **GitHub integration not authenticated or PR not found**: Same as UC-007 alternative flows.

**Postconditions**: Status report with severity distribution, suspicious resolutions flagged, actionable next steps

---

### UC-009 Configure Project via CLI

**ID**: `cpt-cypilot-usecase-configure`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

**Preconditions**: Cypilot initialized in project

**Flow**:

1. User uses CLI to modify configuration. Core commands manage project settings (e.g., add/remove systems, assign kits). Kit-specific config commands (p2) will manage kit-specific settings (e.g., artifact discovery rules, traceability levels)
2. Tool validates the change against the config schema (uses capability `cpt-cypilot-fr-core-cli-config`)
3. Tool applies the change to the appropriate config file (uses capability `cpt-cypilot-fr-core-config`)
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

1. User installs a kit from GitHub (e.g., cyberfabric/cyber-pilot-kit-sdlc)
2. Tool downloads the kit from the GitHub repository at the specified or latest version
3. Tool asks for kit config output directory
4. Tool copies all kit files from the downloaded source into the kit's config directory
5. Tool registers the kit in project configuration with GitHub source and version (uses capability `cpt-cypilot-fr-core-kits`)
6. Tool validates kit structural correctness

**Alternative Flows**:
- **Kit invalid**: Tool displays structural validation errors (missing required files) and does NOT register the kit. Suggests running diagnostics.
- **Kit already installed**: Tool displays current version and offers to update or skip.
- **Kit config relocation**: User requests to move an installed kit's config output directory to a new location.

**Postconditions**: Kit registered and available for workflows; all kit files in config directory; source and version tracked in `core.toml`

---

### UC-011 Update Cypilot Version

**ID**: `cpt-cypilot-usecase-update`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-cypilot-cli`

**Preconditions**: Cypilot installed globally and in project

**Flow**:

1. Tool notifies user when a newer version is available (uses capability `cpt-cypilot-fr-core-installer`)
2. User runs the update command
3. Tool downloads and applies the latest tool version (uses capability `cpt-cypilot-fr-core-version`)
4. Tool migrates directory layout if needed (uses capability `cpt-cypilot-fr-core-layout-migration`)
5. Tool migrates project configuration preserving all user settings (uses capability `cpt-cypilot-fr-core-config`)
6. Tool migrates bundled kit references to GitHub sources for projects upgrading from versions < 3.0.8 (uses capability `cpt-cypilot-fr-core-kits`)
7. Tool regenerates agent integration files for compatibility (uses capability `cpt-cypilot-fr-core-agents`)
8. Tool recommends updating each installed kit if newer versions are available

**Alternative Flows**:
- **Download fails**: Tool displays network error and suggests retrying.
- **Config migration conflict**: Tool preserves a backup, applies migration, and reports any settings that could not be automatically migrated.
- **Layout restructuring fails**: Tool restores backup and notifies user with actionable guidance.
- **Bundled kit detected**: Tool automatically migrates kit reference to GitHub source (versions < 3.0.8).

**Postconditions**: Project tool updated to latest version; layout migrated if needed; bundled kit references migrated to GitHub sources; agent integration refreshed. Kit file updates are a separate operation

---

### UC-012 Migrate Existing Project

**ID**: `cpt-cypilot-usecase-migrate`

**Actors**:
`cpt-cypilot-actor-user`, `cpt-cypilot-actor-ai-agent`

**Preconditions**: Existing project with code but no Cypilot artifacts

**Flow**:

1. User runs project initialization in existing project (uses capability `cpt-cypilot-fr-core-init`)
2. Tool detects existing code (brownfield) and offers reverse-engineering scan (SDLC kit capability)
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

- [ ] Project initialization completes interactive setup and creates a working install directory in ≤ 5 minutes
- [ ] Deterministic validation output is actionable (clear file/line/pointer for every issue)
- [ ] All supported agents receive correct integration files after agent generation
- [ ] Environment diagnostics reports environment health with pass/fail per check
- [ ] Config is never manually edited — all changes go through the CLI tool
- [ ] PR review workflow produces a structured report matching the template format

## 10. Dependencies

| Dependency | Description | Criticality |
|------------|-------------|-------------|
| Runtime platform | Cross-platform runtime for CLI tool and command engine | p1 |
| Git | Project detection, version control | p1 |
| Global installer | Single-command global CLI installation | p2 |
| GitHub integration | API access for PR review/status workflows | p2 |

## 11. Assumptions

- AI coding assistants (Windsurf, Cursor, Claude, Copilot) can follow structured markdown workflows with embedded instructions.
- Developers have the required runtime platform available.
- Projects use Git for version control (project detection relies on `.git` directory).
- Teams are willing to maintain design artifacts as part of their development workflow.
- Global CLI installation prerequisites are available.
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
| Network dependency for updates | Network required for installation and updates | Tool is installed once and works offline; updates are optional and explicit |
