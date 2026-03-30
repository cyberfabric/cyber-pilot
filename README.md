# <p align="center"><img src="images/cypilot-kit.png" alt="Cypilot Banner" width="100%" /></p>

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-3.5-green.svg)]()
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)]()
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=cyberfabric_cyber-pilot&metric=coverage)](https://sonarcloud.io/summary/new_code?id=cyberfabric_cyber-pilot)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=cyberfabric_cyber-pilot&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=cyberfabric_cyber-pilot)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=cyberfabric_cyber-pilot&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=cyberfabric_cyber-pilot)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=cyberfabric_cyber-pilot&metric=bugs)](https://sonarcloud.io/summary/new_code?id=cyberfabric_cyber-pilot)

**Version**: 3.5 | **Status**: Active | **Language**: English

**Audience**: Developers using AI coding assistants, technical leads, engineering teams, DevOps engineers

## Cyber Pilot — Deterministic Agent Tool for Structured Workflows

Cypilot is a **deterministic agent tool** that embeds into AI coding assistants and CI pipelines to provide structured workflows, artifact validation, and design-to-code traceability.

Everything that can be validated, checked, or enforced without an LLM is handled by **deterministic scripts**; the LLM is reserved only for tasks that require reasoning, creativity, or natural language understanding.

## Problem

- **AI Agent Non-Determinism** — AI agents produce inconsistent results without structured guardrails; deterministic validation catches structural and traceability issues that LLMs miss or hallucinate
- **Design-Code Disconnect** — code diverges from design when there is no single source of truth and no automated traceability enforcement
- **Fragmented Tool Setup** — each AI agent (Windsurf, Cursor, Claude, Copilot) requires different file formats for skills, workflows, and rules; maintaining these manually is error-prone
- **Inconsistent PR Reviews** — code reviews vary in depth and focus without structured checklists and prompts
- **Manual Configuration Overhead** — project-specific conventions, artifact locations, and validation rules require manual setup and synchronization

## What Cypilot Provides

Two layers of functionality:

- **Core** — deterministic skill engine, universal workflows (generate/analyze/plan), multi-agent integrations (Windsurf, Cursor, Claude, Copilot, OpenAI), global CLI (`cypilot`/`cpt`), config directory management, extensible kit system, ID/traceability infrastructure, execution plans for context-safe phased execution, [RalphEx](https://ralphex.com/) delegation for autonomous plan execution, environment diagnostics (`cpt doctor`), and Cypilot DSL (CDSL) for behavioral specifications
- **[SDLC Kit](https://github.com/cyberfabric/cyber-pilot-kit-sdlc)** — artifact-first development pipeline (PRD → DESIGN → ADR → DECOMPOSITION → FEATURE → CODE) with templates, checklists, examples, deterministic validation, cross-artifact consistency checks, and GitHub PR review/status workflows

Works with any language, stack, or repository.

---

## Table of Contents

- [](#)
  - [Cyber Pilot — Deterministic Agent Tool for Structured Workflows](#cyber-pilot--deterministic-agent-tool-for-structured-workflows)
  - [Problem](#problem)
  - [What Cypilot Provides](#what-cypilot-provides)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [Global CLI (recommended)](#global-cli-recommended)
  - [Project Setup](#project-setup)
    - [Update](#update)
  - [Configuration](#configuration)
  - [Using Cypilot](#using-cypilot)
    - [Example Prompts](#example-prompts)
    - [Agent Skill](#agent-skill)
    - [Subagents](#subagents)
    - [Workflow Commands](#workflow-commands)
    - [Checklists and Quality Gates](#checklists-and-quality-gates)
  - [Architecture](#architecture)
    - [Directory Structure](#directory-structure)
    - [Kit System](#kit-system)
  - [Multi-Repo Workspaces](#multi-repo-workspaces)
    - [Quick Setup](#quick-setup)
    - [How It Works](#how-it-works)
    - [Cross-Repo Commands](#cross-repo-commands)
  - [RalphEx Integration](#ralphex-integration)
  - [Extensibility](#extensibility)
    - [Kit: **Cypilot SDLC**](#kit-cypilot-sdlc)
  - [Contributing](#contributing)

---

## Prerequisites

- **Python 3.11+** — required for the CLI tool and skill engine (uses `tomllib` from stdlib)
- **Git** — for project detection and version control
- **AI Agent** — Windsurf, Cursor, Claude Code, GitHub Copilot, or OpenAI Codex
- **`gh` CLI** (optional) — required only for PR review/status workflows
- **`pipx`** (recommended) — for global CLI installation

---

## Installation

### Global CLI (recommended)

```bash
pipx install git+https://github.com/cyberfabric/cyber-pilot.git
```

To update to the latest version:

```bash
pipx upgrade cypilot
```

This installs `cypilot` and `cpt` commands globally. The CLI is a thin proxy shell — on first run it downloads the skill bundle into `~/.cypilot/cache/` and delegates all commands to the cached or project-local skill engine.

---

## Project Setup

```bash
# Initialize Cypilot in your project
cpt init

# Generate agent entry points for your IDE
cpt generate-agents --agent claude

# Generate all agents for your IDE
cpt generate-agents
```

`cpt init` creates the Cypilot directory (default: `cypilot/`) with three subdirectories:

| Directory | Purpose | Editable? |
|-----------|---------|-----------|
| `.core/` | Read-only core files (skills, workflows, schemas, architecture, requirements) copied from cache | No |
| `.gen/` | Auto-generated aggregate files (SKILL.md, AGENTS.md, README.md) | No |
| `config/` | User-editable config (`core.toml`, `artifacts.toml`, AGENTS.md) and kit outputs | Yes |

The command also:
- Defines a root system (name/slug derived from the project directory)
- Creates `config/core.toml` and `config/artifacts.toml`
- Installs all available kits (copies kit files to `config/kits/{slug}/`)
- Injects a managed `<!-- @cpt:root-agents -->` block into the root `AGENTS.md`

Supported agents: `windsurf`, `cursor`, `claude`, `copilot`, `openai`.

The `generate-agents` command generates:
- **Workflow commands** — slash commands that load structured prompts for each workflow
- **Skill outputs** — agent skill definitions following the [Agent Skills specification](https://agentskills.io/specification)
- **Subagents** — isolated agent definitions with scoped tools, model selection, and dedicated prompts (all tools except Windsurf)

Five subagents are generated for tools that support them:

| Subagent | Purpose | Write Access |
|----------|---------|-------------|
| `cypilot-codegen` | Code generation when requirements are fully specified — no back-and-forth, just implementation | Yes (worktree isolation on Claude Code) |
| `cypilot-pr-review` | Structured PR review in isolated context — keeps detailed analysis separate from main conversation | No (read-only) |
| `cypilot-ralphex` | Delegates Cypilot plans to [RalphEx](https://ralphex.com/) for autonomous execution | Yes |
| `cypilot-phase-compiler` | Compiles one plan phase from its brief in an isolated agent context | Yes (isolated) |
| `cypilot-phase-runner` | Executes the next phase from a generated plan inside a dedicated agent context | Yes (isolated) |

### Update

```bash
cpt update
```

Updates `.core/` from cache, regenerates `.gen/` aggregates, and updates kit files in `config/kits/` with interactive diff prompts for modified files.

---

## Configuration

All user-editable config lives in `config/` inside your Cypilot directory:

| File | What it controls |
|------|-----------------|
| `core.toml` | Project settings, installed kits, kit resource paths (single source of truth) |
| `artifacts.toml` | Registered systems, artifact types, codebase paths, traceability modes |
| `AGENTS.md` | Agent navigation WHEN-rules (which files the agent opens per task) |
| `SKILL.md` | Custom skill instructions loaded into agent context |
| `rules/*.md` | Project rules — conventions, architecture, testing, patterns, etc. |

Kit resources (templates, rules, checklists, constraints, workflows) are registered in `core.toml` under `[kits.<slug>.resources]`. To see all resolved paths:

```bash
cpt resolve-vars --flat
```

For the full configuration guide — including how to customize agent behavior, `@cpt-*` identifiers and traceability, artifact templates, checklists, constraints, code rules, workflows, and more — with copy-pastable prompts for every use case — see **[guides/CONFIGURATION.md](guides/CONFIGURATION.md)**.

---

## Using Cypilot

Start requests with `cypilot` in your AI agent chat. This switches the agent into Cypilot mode: it loads config and rules, routes the request to the right workflow (plan vs generate vs analyze), and gates file writes behind explicit confirmation.

```
cypilot on            — enable Cypilot mode
cypilot off           — disable Cypilot mode
cypilot auto-config   — scan project and generate convention rules
```

A full walkthrough is available in [`guides/STORY.md`](guides/STORY.md).

### Example Prompts

**Setup & Configuration**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot init` | Initializes Cypilot — creates config directory, generates rules, injects root AGENTS.md |
| `cypilot auto-config` | Scans project structure and generates per-system convention rules |
| `cypilot show config` | Displays config structure, registered artifacts, and codebase mappings |
| `cypilot generate-agents --agent claude` | Regenerates agent entry points for a specific agent |

**Artifact Generation**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot make PRD for user authentication system` | Generates PRD with actors, requirements, flows following the template |
| `cypilot make DESIGN from PRD.md` | Transforms PRD into architecture design with full traceability |
| `cypilot decompose auth feature into tasks` | Creates DECOMPOSITION with ordered, dependency-mapped implementation units |
| `cypilot make FEATURE for login flow` | Produces feature design with acceptance criteria, CDSL flows, edge cases |

**Execution Plans (phased execution)**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot plan generate PRD for task manager` | Decomposes PRD generation into self-contained phase files (≤500 lines each) |
| `cypilot plan analyze DESIGN` | Creates phased analysis plan with focused checklist groups per phase |
| `cypilot execute next phase` | Reads next phase file, follows compiled instructions, reports against acceptance criteria |
| `cypilot plan status` | Reports plan progress: completed/pending/failed phases, next actionable phase |

**Validation & Quality**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot validate PRD.md` | Runs deterministic template validation + semantic quality scoring |
| `cypilot validate all` | Validates entire artifact hierarchy, checks cross-references, reports issues |
| `cypilot validate code for auth module` | Scans code for `@cpt-*` markers, verifies coverage against feature docs |
| `cypilot review DESIGN.md with consistency-checklist` | Multi-phase consistency analysis detecting contradictions |

**Traceability & Search**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot find requirements related to authentication` | Searches artifacts for IDs matching pattern, returns definitions and references |
| `cypilot trace cpt-myapp-fr-auth` | Traces requirement through DESIGN → FEATURE → code |
| `cypilot list unimplemented features` | Cross-references feature docs with code markers |

**Code Review & Pull Requests**

| Prompt | What the agent does |
|--------|---------------------|
| `cypilot review PR #123` | Fetches PR diff, analyzes against checklists, produces structured review report |
| `cypilot PR status #123` | Assesses unreplied comments by severity, audits resolved comments, reports CI status |

### Agent Skill

Cypilot provides a unified **Agent Skill** (`cypilot`) defined in `skills/cypilot/SKILL.md`. The skill is loaded into the agent's context when Cypilot mode is enabled and provides:

- Deterministic validation and traceability commands
- Protocol Guard for consistent context loading
- Workflow routing (plan vs generate vs analyze)
- ID lookup and cross-reference resolution
- Auto-configuration for brownfield projects

### Subagents

Subagents are defined once in `agents.toml` using semantic properties (`mode`, `isolation`, `model`) and automatically adapted to each tool's native format. One definition produces correct output for all supported tools — Claude Code is the canonical format (full fidelity), and other tools receive the best adaptation their format supports.

Five subagents are included:

- **`cypilot-codegen`** — Takes fully-specified requirements and implements them without back-and-forth. Runs in an isolated worktree (on Claude Code) with full write access.
- **`cypilot-pr-review`** — Performs structured, checklist-based PR reviews in a read-only isolated context, keeping detailed analysis separate from the main conversation.
- **`cypilot-ralphex`** — Manages the full RalphEx delegation lifecycle: discovery → plan export → delegation → handoff reporting.
- **`cypilot-phase-compiler`** — Compiles exactly one plan phase from its brief in an isolated agent context, without delegating to RalphEx or executing the phase.
- **`cypilot-phase-runner`** — Executes the next phase from a generated plan inside a dedicated agent context, without RalphEx delegation.

Generated automatically by `cypilot generate-agents --agent <name>`. Windsurf does not support subagents and is gracefully skipped.

**Tool support:**

| Capability | Claude Code | Cursor | GitHub Copilot | OpenAI Codex |
|---|:---:|:---:|:---:|:---:|
| Subagent definitions | Yes | Yes | Yes | Yes |
| Read-only enforcement | `disallowedTools` | `readonly: true` | Tool filter | In prompt |
| Model selection | Yes | Yes | — | — |
| Worktree isolation | Yes | — | — | — |
| Subagent-scoped hooks | Yes | — | — | — |

See [ADR-0016](architecture/ADR/0016-cpt-cypilot-adr-ai-cli-extensibility-subagents-v1.md) for the full adaptation model and format details.

### Workflow Commands

Cypilot has **three** universal workflows plus delegation and diagnostics:

| Command | Workflow | Description |
|---------|----------|-------------|
| `/cypilot-plan` | `plan.md` | Plan: decompose large tasks into self-contained phase files for phased execution |
| `/cypilot-generate` | `generate.md` | Write: create, edit, fix, update, implement, refactor, configure |
| `/cypilot-analyze` | `analyze.md` | Read: validate, review, check, inspect, audit, compare |
| `cpt delegate` | — | Compile a Cypilot plan and delegate to [RalphEx](https://ralphex.com/) for autonomous execution |
| `cpt doctor` | — | Run environment health checks (ralphex availability, etc.) |

> **Routing priority**: delegate > plan > generate > analyze. Delegation intent routes to the `cypilot-ralphex` subagent. "Plan to generate PRD" routes to `plan.md`, not `generate.md`.

> **Plan Escalation**: `generate.md` and `analyze.md` include a mandatory escalation gate — if the estimated context exceeds the safe budget (>2500 lines for generate, >2000 for analyze), the agent MUST offer to switch to `/cypilot-plan` for phased execution.

Kit-specific workflows (e.g., PR review, PR status) are provided by kits and exposed as agent entry points automatically.

### Checklists and Quality Gates

**Artifact checklists** (from SDLC kit):
- **PRD** — 300+ criteria for requirements completeness
- **DESIGN** — 380+ criteria for architecture validation
- **DECOMPOSITION** — 130+ criteria for feature breakdown quality
- **FEATURE** — 380+ criteria for implementation readiness
- **ADR** — 270+ criteria for decision rationale

**Generic checklists** in `requirements/`:
- [**Code checklist**](requirements/code-checklist.md) — 200+ criteria for code quality
- [**Consistency checklist**](requirements/consistency-checklist.md) — 45+ criteria for cross-artifact consistency
- [**Reverse engineering**](requirements/reverse-engineering.md) — 270+ criteria for legacy code analysis
- [**Prompt engineering**](requirements/prompt-engineering.md) — 220+ criteria for AI prompt design

## Architecture

### Directory Structure

After `cpt init`, a project has:

```
project/
├── cypilot/                    # Cypilot install directory
│   ├── .core/                  # Read-only core (from cache)
│   │   ├── skills/             # Skill engine + scripts
│   │   ├── workflows/          # Core workflows (generate.md, analyze.md, plan.md)
│   │   ├── schemas/            # JSON schemas
│   │   ├── architecture/       # Core architecture docs (PRD, DESIGN, specs)
│   │   └── requirements/       # Core requirements + checklists
│   ├── .gen/                   # Auto-generated aggregates
│   │   ├── AGENTS.md           # Aggregated WHEN rules from kits
│   │   ├── SKILL.md            # Composed skill with kit extensions
│   │   └── README.md           # Aggregated kit documentation
│   └── config/                 # User-editable
│       ├── core.toml           # System definitions, kit registrations
│       ├── artifacts.toml      # Artifact registry, autodetect rules
│       ├── AGENTS.md           # User WHEN rules
│       ├── SKILL.md            # User skill extensions
│       └── kits/sdlc/          # Kit files (artifacts, workflows, constraints)
│           ├── artifacts/      # Templates, rules, checklists, examples
│           ├── workflows/      # Kit-specific workflows
│           ├── constraints.toml
│           ├── SKILL.md
│           └── AGENTS.md
├── AGENTS.md                   # Root entry (managed block → cypilot/.gen/)
├── .windsurf/                  # Agent entry points (generated)
├── .cursor/
├── .claude/
└── .github/prompts/
```

### Kit System

Each kit is a **direct file package** containing ready-to-use resources:

| Kit Content | Purpose |
|-------------|----------|
| `artifacts/{KIND}/template.md` | Writing instructions for artifact kind |
| `artifacts/{KIND}/rules.md` | Validation rules |
| `artifacts/{KIND}/checklist.md` | Quality criteria |
| `artifacts/{KIND}/examples/` | Example artifacts |
| `constraints.toml` | Heading/ID constraints for validation |
| `workflows/` | Kit-specific workflows (e.g., PR review) |
| `SKILL.md` | Kit skill extensions |
| `AGENTS.md` | Agent system prompt content |

Kits are installed to `config/kits/{slug}/`. Running `cpt update` updates kit files with interactive diff prompts for any user modifications.

---

## Multi-Repo Workspaces

Cypilot supports **multi-repo workspaces** — a federation layer that lets you work across multiple repositories while maintaining cross-repo traceability. Each repo keeps its own independent adapter; the workspace provides a map of named sources.

**Use cases:**
- PRDs in a docs repo, design in another repo, code in yet another
- Shared kit packages in a separate repo
- Working from one repo while referencing artifacts in others

### Quick Setup

```bash
# Option A: Auto-discover nested repos and generate workspace
cpt workspace-init

# Option B: Add sources individually
cpt workspace-add --name docs --path ../docs-repo --role artifacts
cpt workspace-add --name shared-kits --path ../shared-kits --role kits

# Option C: Define workspace inline in your repo's config
cpt workspace-add --inline --name docs --path ../docs-repo
```

### How It Works

The **current working directory** always determines the primary repo. Other repos contribute artifacts, code, and kits for cross-referencing. No adapter merging — each repo owns its configuration.

**Workspace config** is discovered in priority order (project root only — no parent directory traversal):
1. **`workspace` key in `config/core.toml`** — either an inline `[workspace]` table or a `workspace = "<path>"` string pointing to an external `.toml` file
2. **Standalone `.cypilot-workspace.toml`** at the project root — auto-discovered as fallback when no `workspace` key exists in `core.toml` (no explicit reference needed)

> **Note:** Discovery starts from the current project's `config/core.toml` and does not search parent directories. Each repo must configure its own workspace entry point.

### Cross-Repo Commands

```bash
# Validate with cross-repo ID resolution (default when workspace active)
cpt validate

# Validate local repo only (skip cross-repo)
cpt validate --local-only

# Search for ID definitions across all repos
cpt where-defined --id cpt-myapp-req-001

# List IDs from a specific source
cpt list-ids --source docs-repo

# Check workspace status
cpt workspace-info
```

Missing source repos are handled gracefully — a warning is emitted and operations continue with available sources. Artifacts pointing to unreachable sources are skipped rather than silently falling back to local paths.

Cross-repo ID resolution is controlled by two traceability settings in the workspace config: `cross_repo` (enables workspace-aware path resolution) and `resolve_remote_ids` (expands remote IDs into the union set). Both default to `true`. Use `validate --local-only` to skip cross-repo resolution entirely.

For the full specification, see [`requirements/workspace.md`](requirements/workspace.md).

---

## RalphEx Integration

Cypilot integrates with [RalphEx](https://ralphex.com/) — an autonomous code execution platform. When RalphEx is available, Cypilot can delegate entire execution plans for autonomous processing.

**How it works:**

1. Create a plan with `/cypilot-plan` — produces `plan.toml` manifest + phase files
2. Run `cpt delegate <plan_dir>` — compiles phases into RalphEx-compatible Markdown and invokes RalphEx

```bash
# Dry run — assemble the command without invoking
cpt delegate .bootstrap/.plans/my-task --dry-run

# Execute — delegate with dashboard
cpt delegate .bootstrap/.plans/my-task --mode execute

# Tasks only — export plan without running
cpt delegate .bootstrap/.plans/my-task --mode tasks-only

# Review mode — read-only analysis
cpt delegate .bootstrap/.plans/my-task --mode review
```

**Environment check:**

```bash
cpt doctor    # checks ralphex availability, reports PASS/WARN/FAIL
```

RalphEx is optional — all Cypilot workflows work without it. When RalphEx is not installed, `cpt doctor` reports a WARN with installation guidance, and `cpt delegate` exits with a clear error and setup instructions.

See [ADR-0018](architecture/ADR/0018-cpt-cypilot-adr-ralphx-delegation-skill-v1.md) for the architecture decision and design rationale.

---

## Extensibility

Cypilot is extensible through **Kits** — self-contained packages that bundle templates, rules, checklists, examples, and workflows for a specific domain. The kit plugin system supports extension at three levels:

1. **Kit-level** — new kits for entirely new domains (e.g., API design, infrastructure-as-code)
2. **Artifact-level** — new artifact kinds within an existing kit
3. **Resource-level** — override templates, extend checklists, modify rules within an artifact kind

### Kit: **Cypilot SDLC**

The built-in SDLC Kit provides an artifact-first development pipeline with end-to-end traceability:

**PRD → ADR + DESIGN → DECOMPOSITION → FEATURE → CODE**

Each artifact kind has templates, rules, checklists (300+ criteria), and examples. The kit also provides PR review and PR status workflows for GitHub.

See the [SDLC Kit repository](https://github.com/cyberfabric/cyber-pilot-kit-sdlc) for the full pipeline overview, artifact kinds, and guides.

---

## Contributing

We welcome contributions! See **[CONTRIBUTING.md](CONTRIBUTING.md)** for the full guide covering:

- **Development setup** and self-hosted bootstrap architecture
- **Versioning** — where versions live and how to bump them
- **DCO requirement** — all commits must be signed off (`git commit -s`)
- **CI pipeline** — Makefile targets and GitHub Actions checks
- **Pull request process** — what must pass before merge

Quick start:
```bash
git clone https://github.com/cyberfabric/cyber-pilot.git
cd cyber-pilot
make install-proxy   # install cpt CLI from local source
make update          # sync .bootstrap/ from source
make test            # run tests
make validate        # validate artifacts
```
