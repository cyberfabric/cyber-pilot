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

---

## Table of Contents

- [Kit Specification](#kit-specification)
  - [Kit Overview](#kit-overview)
  - [Kit Directory Structure](#kit-directory-structure)
    - [Reference Kit (in {cypilot_path}/.core/)](#reference-kit-in-cypilot_path-core)
    - [Installed Kit (in project)](#installed-kit-in-project)
  - [Generated Outputs](#generated-outputs)
  - [Project-Level Outputs](#project-level-outputs)
    - [taxonomy.md](#taxonomymd)
  - [Kit Extension Protocol (p2)](#kit-extension-protocol-p2)
    - [Registering Custom Markers](#registering-custom-markers)
    - [Output Generator Interface](#output-generator-interface)
  - [Related Specifications](#related-specifications)

---

## Kit Overview

A **Kit** is a blueprint package that provides domain-specific artifact and codebase definitions for Cypilot. Each kit contains one or more **Blueprints** — single-source-of-truth Markdown files from which all kit resources are deterministically generated.

Blueprints with an `artifact` key in `@cpt:blueprint` define artifact kinds (e.g., PRD, DESIGN). Blueprints without an `artifact` key define codebase-level resources (rules, checklists for code). See [Blueprint Specification](blueprint.md) for the full blueprint format, markers, parsing algorithm, and update model.

**What a kit provides**:
- Blueprint files (`blueprints/*.md`) — one per artifact kind or codebase concern (required)

**What is generated from blueprints** (placed in `config/kits/<slug>/`):
- Per-artifact outputs: `artifacts/<KIND>/` containing `template.md`, `rules.md`, `checklist.md`, `example.md`
- Codebase outputs: `codebase/` containing `rules.md`, `checklist.md`
- Kit-wide: `constraints.toml` (aggregated from all artifact blueprints)
- Workflow files from `@cpt:workflow` markers: `workflows/{name}.md`
- SKILL.md extensions from `@cpt:skill` markers

**Key properties**:
- Kit registration (slug, version) is stored in `config/core.toml`
- Blueprints are the single source — all other resources are generated
- Deterministic: same blueprint → identical output files (byte-for-byte)
- User-customizable: blueprints are copied into `config/kits/<slug>/blueprints/` where users can edit them and regenerate outputs
- Update model protects user modifications across kit updates (see [blueprint.md § Update Model](blueprint.md#update-model))

> **Plugin system** (CLI subcommands, validation hooks, generation hooks) is planned for p2 and not covered in this specification.

---

## Kit Directory Structure

### Reference Kit (in {cypilot_path}/.core/)

When a kit is installed, its source is saved to `{cypilot_path}/.core/kits/{slug}/` as the reference copy:

```
{cypilot_path}/.core/kits/<slug>/
├── blueprints/                    # One .md per artifact kind (required)
│   ├── PRD.md
│   ├── DESIGN.md
│   ├── ADR.md
│   ├── CODEBASE.md                # No artifact key → codebase outputs
│   └── ...
└── scripts/                       # Kit scripts (optional)
    └── ...
```

- `blueprints/` is the **minimum required structure**. For blueprints with `artifact` key, the filename (without `.md`) becomes the artifact kind slug (e.g., `PRD.md` → artifact kind `PRD`). Blueprints without `artifact` key generate into `codebase/`.
- `scripts/` contains kit-specific scripts. Scripts are **not copied** to `config/` — they are referenced directly from `{cypilot_path}/.core/kits/{slug}/scripts/`.

The reference copy is used for three-way diff during additive updates. Users MUST NOT edit files in `{cypilot_path}/.core/kits/`.

### Installed Kit (in project)

Blueprints are copied from the reference into the project's config directory where users can edit them. All outputs are generated from these user-editable copies:

```
config/kits/<slug>/
├── blueprints/                    # Copies of source blueprints (user-editable)
│   ├── PRD.md
│   ├── DESIGN.md
│   ├── CODEBASE.md
│   └── ...
├── constraints.toml               # Generated: kit-wide structural constraints (from all artifact blueprints)
├── taxonomy.md                    # Generated: kit taxonomy (artifact kinds, ID types, traceability)
├── artifacts/                     # Generated outputs per artifact kind
│   ├── PRD/
│   │   ├── template.md            # Generated: heading structure
│   │   ├── rules.md               # Generated: agent rules
│   │   ├── checklist.md           # Generated: quality checklist
│   │   └── example.md             # Generated: concrete example
│   ├── DESIGN/
│   │   └── ...
│   └── .../
├── codebase/                      # Generated from blueprints without artifact key
│   ├── rules.md               # Generated: codebase agent rules
│   └── checklist.md           # Generated: codebase quality checklist
└── workflows/                     # Generated from @cpt:workflow markers
    ├── generate-prd.md
    ├── analyze-prd.md
    └── ...
```

**Flow**:
1. `cypilot init` / `cypilot kit install` saves kit source to `{cypilot_path}/.core/kits/{slug}/` (reference copy)
2. Blueprints are copied from `{cypilot_path}/.core/kits/{slug}/blueprints/` to `config/kits/{slug}/blueprints/` (user-editable)
3. Blueprint Processor reads user blueprints and generates outputs into `artifacts/<KIND>/`, `codebase/`, `constraints.toml`, and `workflows/`
4. Users edit blueprints in `config/kits/{slug}/blueprints/` and run `cypilot generate-resources` to regenerate outputs

**Update modes** (see also [blueprint.md § Update Model](blueprint.md#update-model)):

| Mode | Command | Behavior |
|------|---------|----------|
| **Force** | `cypilot kit update --force` | Updates reference in `{cypilot_path}/.core/kits/{slug}/`, overwrites all user blueprints, regenerates all outputs. User edits are discarded. |
| **Additive** | `cypilot kit update` | Three-way diff: reference (`{cypilot_path}/.core/kits/{slug}/`) vs. user blueprints vs. new kit version. User-modified sections are preserved; new markers are merged in; deleted markers stay removed. Reference is updated after merge. |

---

## Generated Outputs

All outputs are generated by the core Blueprint Processor from `@cpt:` markers. Kits do not define custom output generators in p1 — all generation logic is in the core.

| Output | Location | Source Markers | Spec |
|--------|----------|---------------|------|
| `rules.md` | `artifacts/<KIND>/` | `@cpt:rules` + `@cpt:rule` | [rules.md](rules.md) |
| `checklist.md` | `artifacts/<KIND>/` | `@cpt:checklist` + `@cpt:check` | [checklist.md](checklist.md) |
| `template.md` | `artifacts/<KIND>/` | `@cpt:heading` + `@cpt:prompt` | [template.md](template.md) |
| `example.md` | `artifacts/<KIND>/` | `@cpt:heading` (examples) + `@cpt:example` | [example.md](example.md) |
| `constraints.toml` | kit root | `@cpt:heading` + `@cpt:id` (aggregated) | [constraints.md](constraints.md) |
| codebase `rules.md` | `codebase/` | `@cpt:rules` + `@cpt:rule` | [rules.md](rules.md) |
| codebase `checklist.md` | `codebase/` | `@cpt:checklist` + `@cpt:check` | [checklist.md](checklist.md) |
| `workflows/{name}.md` | `workflows/` | `@cpt:workflow` | [blueprint.md § cpt:workflow](blueprint.md#cptworkflow) |

**Determinism guarantee**: same blueprint content → identical output files (byte-for-byte). The processor sorts, formats, and serializes deterministically.

---

## Project-Level Outputs

### taxonomy.md

`taxonomy.md` is a **generated** kit-level document. It aggregates information from the kit's blueprints into a single human-readable reference.

**Location**: `config/kits/{slug}/taxonomy.md`

**Source data** (collected from the kit's blueprints):
- `@cpt:blueprint` — artifact kind name, description, kit identity
- `@cpt:id` — identifier kind names, descriptions, examples, `to_code` flags
- `@cpt:heading` — section descriptions (from `description` keys)
- `@cpt:example` — concrete example snippets per artifact kind
- `@cpt:blueprint` `intro` field — general taxonomy introduction text

**Structure of generated taxonomy.md**:

```markdown
# Project Taxonomy

## Introduction

{Aggregated intro text from @cpt:blueprint `intro` fields across all kits.
Provides project-level context: what artifacts exist, how they relate,
and how identifiers connect design to implementation.}

## Artifact Kinds

### PRD — Product Requirements Document

{Description from @cpt:blueprint of PRD}

**Identifier kinds**:
| Kind | Name | Description | To Code |
|------|------|-------------|---------|
| `fr` | Functional Requirement | ... | yes |
| `nfr` | Non-functional Requirement | ... | no |
| `actor` | Actor | ... | no |

**Example IDs**: `cpt-myapp-fr-login`, `cpt-myapp-nfr-latency`

### DESIGN — Technical Design

{Description from @cpt:blueprint of DESIGN}

...

## Cross-Artifact Traceability

{Summary of how IDs flow between artifact kinds,
derived from @cpt:id ref.* rules across all blueprints.}
```

**Blueprint `intro` field**: each blueprint's `@cpt:blueprint` TOML block MAY include an `intro` key with general taxonomy text for the introduction section:

```toml
# Inside @cpt:blueprint
intro = "PRD defines the product requirements and serves as the primary input for DESIGN."
```

**Generation command**: `cypilot generate-resources`

---

## Kit Extension Protocol (p2)

> **p2**: The plugin system (custom markers, output generators) is planned for a future phase. The following documents the target design for reference.

### Registering Custom Markers

Kits register markers during plugin initialization:

```python
def register_blueprint_markers(processor):
    processor.register_marker(
        name="heading",
        content_mode="template-visible",
        handler=HeadingMarkerHandler(),
        generators=[ConstraintsTomlGenerator()]
    )
    processor.register_marker(
        name="check",
        content_mode="metadata",
        handler=CheckMarkerHandler(),
        generators=[ChecklistMdGenerator()]
    )
```

Each registration provides:
- **name** — marker name (used as `cpt:{name}`)
- **content_mode** — `template-visible` (content kept in template.md) or `metadata` (content stripped)
- **handler** — parser that extracts structured data from the marker
- **generators** — list of output generators that consume this marker's data

### Output Generator Interface

Each generator implements:

```python
class OutputGenerator:
    def output_filename(self) -> str:
        """Return the output file name (e.g., 'checklist.md')"""

    def generate(self, markers: list[MarkerData], context: BlueprintContext) -> str:
        """Generate file content from collected markers"""
```

The Blueprint Processor:
1. Parses all markers, grouping by type.
2. For each registered generator, collects relevant markers.
3. Invokes `generate()` with the collected markers.
4. Writes the output to `output_filename()` in the artifact directory.

---

## Related Specifications

| Spec | Description |
|------|-------------|
| [blueprint.md](blueprint.md) | Blueprint format, marker syntax, marker reference, placeholder syntax, parsing algorithm, update model, validation rules |
| [rules.md](rules.md) | Generated `rules.md` format, structure, loading, and usage |
| [checklist.md](checklist.md) | Generated `checklist.md` format, domain organization, check items |
| [template.md](template.md) | Generated `template.md` format, heading structure, placeholders |
| [constraints.md](constraints.md) | Generated `constraints.toml` format, validation semantics, cross-artifact rules |
| [example.md](example.md) | Generated `example.md` format, derivation from blueprint examples |
