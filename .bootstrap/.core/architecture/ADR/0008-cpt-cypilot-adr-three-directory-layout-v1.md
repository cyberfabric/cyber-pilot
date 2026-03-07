---
status: accepted
date: 2026-03-07
decision-makers: project maintainer
---

# ADR-0008: Three-Directory Layout (.core / .gen / config)


<!-- toc -->

- [Context and Problem Statement](#context-and-problem-statement)
- [Decision Drivers](#decision-drivers)
- [Considered Options](#considered-options)
- [Decision Outcome](#decision-outcome)
  - [Consequences](#consequences)
  - [Confirmation](#confirmation)
- [Pros and Cons of the Options](#pros-and-cons-of-the-options)
  - [Three-directory layout](#three-directory-layout)
  - [Flat layout](#flat-layout)
  - [Two-directory layout](#two-directory-layout)
- [Traceability](#traceability)

<!-- /toc -->

**ID**: `cpt-cypilot-adr-three-directory-layout`

## Context and Problem Statement

Cypilot installs files into a project directory (`{cypilot_path}/`, default: `cypilot/`). These files have different ownership and mutability characteristics: some are read-only tool internals, some are auto-generated aggregations, and some are user-editable configuration. Mixing them in a flat structure creates confusion about what can be edited and what will be overwritten on update.

## Decision Drivers

* **Clear ownership** — users must know which files they can edit and which the tool manages
* **Safe updates** — `cpt update` must be able to overwrite tool files without touching user config
* **Separation of concerns** — generated aggregations (AGENTS.md, SKILL.md) are derived from user config; they must not be confused with source config
* **Discoverability** — convention-over-configuration for where to find things

## Considered Options

1. **Three-directory layout** (.core / .gen / config) — separate read-only, generated, and user-editable directories
2. **Flat layout** — all files in one directory with naming conventions
3. **Two-directory layout** (.core / config) — no separate generated directory

## Decision Outcome

Chosen: **Three-directory layout** inside `{cypilot_path}/`.

### Consequences

| Directory | Ownership | On Update | Contents |
|-----------|-----------|-----------|----------|
| `.core/` | Tool (read-only) | Fully replaced from cache | Skills, scripts, schemas, workflows, requirements |
| `.gen/` | Tool (auto-generated) | Fully regenerated from user config | `AGENTS.md`, `SKILL.md`, `README.md` — top-level aggregations only |
| `config/` | User (editable) | Preserved; kit files updated via interactive diff | `core.toml`, `artifacts.toml`, `kits/{slug}/`, `AGENTS.md`, `SKILL.md` |

* Good, because clear ownership boundary — users edit `config/`, never `.core/` or `.gen/`
* Good, because `cpt update` can safely replace `.core/` and regenerate `.gen/` without data loss
* Good, because kit files in `config/kits/` are user-editable with interactive diff protection
* Bad, because three directories add structural complexity vs a flat layout
* Neutral, because `.gen/` contains only top-level files (not kit outputs) — kit outputs live in `config/kits/`

### Confirmation

Confirmed by `cpt update` safely replacing `.core/` and regenerating `.gen/` without touching user-edited files in `config/`.

## Pros and Cons of the Options

### Three-directory layout

* Good, because clear ownership boundaries
* Good, because safe updates without data loss
* Bad, because structural complexity

### Flat layout

* Good, because simpler directory structure
* Bad, because no clear ownership — users may edit tool-managed files
* Bad, because update must carefully avoid overwriting user files

### Two-directory layout

* Good, because simpler than three directories
* Bad, because generated aggregations mixed with user config

## Traceability

- **PRD**: `cpt-cypilot-fr-core-config`
- **DESIGN**: `cpt-cypilot-component-config-manager`, `cpt-cypilot-component-kit-manager`
- **Supersedes**: Old layout where `.gen/kits/{slug}/` held generated kit outputs (now in `config/kits/{slug}/`)
