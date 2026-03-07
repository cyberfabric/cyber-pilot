---
cypilot: true
type: spec
name: Kit Specification
version: 1.0
purpose: Define kit structure, installation, update model, directory layout, generated output overview, taxonomy, and extension protocol
drivers:
  - cpt-cypilot-fr-core-kits
  - cpt-cypilot-fr-sdlc-plugin
---

# Kit Specification


<!-- toc -->

- [Kit Specification](#kit-specification)
  - [Kit Overview](#kit-overview)
  - [Kit Directory Structure](#kit-directory-structure)
  - [Kit File Reference](#kit-file-reference)
  - [Project-Level Outputs](#project-level-outputs)
    - [taxonomy.md](#taxonomymd)
  - [Kit Extension Protocol (p2)](#kit-extension-protocol-p2)
  - [Related Specifications](#related-specifications)

<!-- /toc -->

---
---

## Kit Overview

A **Kit** is a file package that provides domain-specific artifact and codebase definitions for Cypilot. Each kit contains ready-to-use files — rules, templates, checklists, examples, constraints, workflows, and skill extensions — maintained directly by kit authors.

**What a kit provides** (installed into `{cypilot_path}/config/kits/<slug>/`):
- Per-artifact files: `artifacts/<KIND>/` containing `template.md`, `rules.md`, `checklist.md`, `examples/example.md`
- Codebase files: `codebase/` containing `rules.md`, `checklist.md`
- Kit-wide: `constraints.toml` (structural validation rules), `conf.toml` (version metadata)
- Workflow files: `workflows/{name}.md`
- SKILL.md — kit skill extensions for AI agent discoverability
- Scripts: `scripts/` — kit-specific scripts and prompts

**Key properties**:
- Kit registration (slug, version, config path) is stored in `{cypilot_path}/config/core.toml`
- All kit files are user-editable after installation
- User modifications are preserved across kit updates via file-level diff with interactive prompts
- Kit version is stored in `{cypilot_path}/config/kits/<slug>/conf.toml`

> **Plugin system** (CLI subcommands, validation hooks, generation hooks) is planned for p2 and not covered in this specification.
>
> **Legacy**: The previous blueprint-based kit model (where kit files were generated from `@cpt:` marker files) has been removed per `cpt-cypilot-adr-remove-blueprint-system`. See [blueprint.md](blueprint.md) for legacy reference only.

---

## Kit Directory Structure

When a kit is installed, all files are copied to `{cypilot_path}/config/kits/{slug}/` where users can edit them:

```
{cypilot_path}/config/kits/<slug>/
├── conf.toml                      # Kit version metadata (slug, version, name)
├── SKILL.md                       # Per-kit skill instructions (user-editable)
├── constraints.toml               # Kit-wide structural constraints (user-editable)
├── artifacts/                     # Per-artifact files
│   ├── PRD/
│   │   ├── template.md            # Heading structure for artifact creation
│   │   ├── rules.md               # Agent rules for generate/analyze workflows
│   │   ├── checklist.md           # Quality checklist
│   │   └── examples/example.md    # Concrete example artifact
│   ├── DESIGN/
│   │   └── ...
│   └── .../
├── codebase/                      # Codebase review files
│   ├── rules.md                   # Codebase agent rules
│   └── checklist.md               # Codebase quality checklist
├── scripts/                       # Kit-specific scripts and prompts
│   └── ...
└── workflows/                     # Workflow definitions
    ├── pr-review.md
    ├── pr-status.md
    └── ...
```

Top-level `.gen/` retains only aggregate files: `AGENTS.md`, `SKILL.md`, `README.md`.

**Flow**:
1. `cpt init` / `cypilot kit install` copies all kit files from source to `{cypilot_path}/config/kits/{slug}/` and registers kit in `core.toml`
2. Regenerate `.gen/AGENTS.md` and `.gen/SKILL.md` to include the new kit's navigation and skill routing
3. Users may freely edit any kit file at any time
4. On kit update, the system compares new files against user's installed copies via file-level diff, then regenerates `.gen/` aggregate files

**Update modes**:

| Mode | Command | Behavior |
|------|---------|----------|
| **Force** | `cypilot kit update --force` | Overwrites all kit files in `{cypilot_path}/config/kits/{slug}/`. User edits are discarded. |
| **Interactive** (default) | `cypilot kit update` | File-level diff: for each file, compare new version against user's installed copy. **IF** identical → no action. **IF** different → present unified diff with `[a]ccept / [d]ecline / [A]ccept all / [D]ecline all / [m]odify` prompts. |

---

## Kit File Reference

Each kit file is authored directly by kit authors and user-editable after installation.

| File | Location | Purpose | Spec |
|------|----------|---------|------|
| `rules.md` | `artifacts/<KIND>/` | Agent rules for generate/analyze workflows | [rules.md](rules.md) |
| `checklist.md` | `artifacts/<KIND>/` | Quality checklist for validation | [checklist.md](checklist.md) |
| `template.md` | `artifacts/<KIND>/` | Heading structure for artifact creation | [template.md](template.md) |
| `example.md` | `artifacts/<KIND>/examples/` | Concrete example artifact | [example.md](example.md) |
| `constraints.toml` | kit root | Kit-wide structural validation rules | [constraints.md](constraints.md) |
| codebase `rules.md` | `codebase/` | Codebase agent rules | [rules.md](rules.md) |
| codebase `checklist.md` | `codebase/` | Codebase quality checklist | [checklist.md](checklist.md) |
| `workflows/{name}.md` | `workflows/` | Workflow definitions | — |
| `SKILL.md` | kit root | Kit skill extensions | — |
| `conf.toml` | kit root | Kit version metadata | — |

---

## Project-Level Outputs

### taxonomy.md

`taxonomy.md` is an optional kit-level document that aggregates information about the kit's artifact kinds into a single human-readable reference.

**Location**: `{cypilot_path}/config/kits/{slug}/taxonomy.md`

This file is authored directly by kit authors as part of the kit file package.

---

## Kit Extension Protocol (p2)

> **p2**: The plugin system (CLI subcommands, validation hooks) is planned for a future phase. The following documents the target design for reference.

Kit authors extend Cypilot by adding files to the standard kit directories:
- New artifact kinds: add a new `artifacts/<KIND>/` directory with `rules.md`, `template.md`, `checklist.md`, `examples/example.md`
- New workflows: add `.md` files to `workflows/`
- New scripts: add files to `scripts/`
- SKILL extensions: edit `SKILL.md` to add kit-specific commands and workflows
- Constraint rules: edit `constraints.toml` to define structural validation rules

---

## Related Specifications

| Spec | Description |
|------|-------------|
| [blueprint.md](blueprint.md) | **DEPRECATED** — Legacy blueprint format reference |
| [rules.md](rules.md) | `rules.md` format, structure, loading, and usage |
| [checklist.md](checklist.md) | `checklist.md` format, domain organization, check items |
| [template.md](template.md) | `template.md` format, heading structure, placeholders |
| [constraints.md](constraints.md) | `constraints.toml` format, validation semantics, cross-artifact rules |
| [example.md](example.md) | `example.md` format, derivation from examples |
