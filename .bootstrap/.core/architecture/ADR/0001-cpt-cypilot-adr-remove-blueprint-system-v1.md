---
status: accepted
date: 2026-03-06
decision-makers: project maintainer
---

# ADR-0001: Replace Blueprint System with Direct File Package Model


<!-- toc -->

- [Context and Problem Statement](#context-and-problem-statement)
- [Decision Drivers](#decision-drivers)
- [Considered Options](#considered-options)
- [Decision Outcome](#decision-outcome)
  - [Consequences](#consequences)
  - [Confirmation](#confirmation)
- [Pros and Cons of the Options](#pros-and-cons-of-the-options)
  - [Option 1: Keep Blueprint System As-Is](#option-1-keep-blueprint-system-as-is)
  - [Option 2: Move Blueprint Processor to Dev-Only Script](#option-2-move-blueprint-processor-to-dev-only-script)
  - [Option 3: Remove Blueprints Entirely, Kit = Ready Files](#option-3-remove-blueprints-entirely-kit-ready-files)
- [More Information](#more-information)
- [Traceability](#traceability)

<!-- /toc -->

**ID**: `cpt-cypilot-adr-remove-blueprint-system`
## Context and Problem Statement

Cypilot's kit system currently uses a Blueprint Processor that parses Markdown files containing `@cpt:` markers and generates all kit resources (rules, templates, checklists, constraints, examples, workflows) from them. Kit updates rely on SHA-256 hash-based customization detection and marker-level three-way merge to preserve user edits. This architecture introduces significant complexity:

- The Blueprint Processor (`blueprint.py`, ~1500 lines) parses markers, generates multiple output types, and manages dual-ownership of files
- Kit updates require hash computation, version comparison, and three-way merge at the marker level — a fragile process that produces conservative merges defeating its own purpose
- Users receive both blueprints (`kits/{slug}/blueprints/`) and generated outputs (`config/kits/{slug}/`) — two representations of the same content
- The `generate-resources` command, `process_kit` function, and `migrate_kit` function add complexity to the install/update pipeline
- The generated kit files (`config/kits/sdlc/`) already exist as ready-to-use artifacts and are directly editable by users

The fundamental question is: if we already have the generated kit files and users edit them directly, why maintain the generation machinery at all?

## Decision Drivers

* **Complexity reduction** — the blueprint system accounts for ~30% of kit.py code and introduces the most fragile logic (three-way merge, hash detection)
* **Update reliability** — hash-based detection and marker-level merge produce surprising results (conservative merge that rejects valid changes)
* **Conceptual simplicity** — users should work with one set of files, not understand blueprints vs generated outputs
* **Maintenance burden** — blueprint format changes require updating parser, generators, hash logic, merge logic, and tests (~40 tests across 7 files)
* **No external consumers** — there are no third-party kit authors using the Blueprint Processor; only the SDLC kit exists

## Considered Options

1. **Keep Blueprint System As-Is** — retain Blueprint Processor, hash-based detection, three-way merge
2. **Move Blueprint Processor to Dev-Only Script** — remove from runtime, keep as build tool for kit development
3. **Remove Blueprints Entirely, Kit = Ready Files** — delete blueprints and processor, edit kit files directly

## Decision Outcome

Chosen option: **Option 3 — Remove Blueprints Entirely**, because the generated kit files already exist, are human-readable and directly editable, and maintaining a generation pipeline for a single kit adds complexity without proportional value. The blueprint system was designed for a future where multiple kits would be authored by third parties, but that future has not materialized and the simpler model serves current needs better.

### Consequences

* Good, because the kit model becomes trivially simple: kit = directory of files, update = file-level diff
* Good, because ~1500 lines of blueprint parsing/generation code can be deleted
* Good, because ~40 tests related to blueprint processing can be removed, reducing test maintenance
* Good, because the update pipeline simplifies to: compare files → show diff → prompt user
* Good, because users no longer need to understand the blueprint/generated-output duality
* Bad, because if a structural change affects many kit files (e.g., renaming a heading pattern across all artifact rules), each file must be edited manually instead of regenerating from a single blueprint
* Bad, because the `@cpt:` marker format and Blueprint Processor represent significant prior investment that is being discarded
* Neutral, because the existing `config/kits/sdlc/` files are already the canonical source of truth in practice — this decision formalizes that reality

### Confirmation

Confirmed when:

- All blueprint-related code is removed (`blueprint.py`, `codebase.py` blueprint parts, `process_kit`, `generate-resources`, `migrate_kit` three-way merge)
- `kits/sdlc/blueprints/` directory is deleted
- `cpt init` and `cpt update` work without blueprint processing
- `validate-kits` validates kit file structure without requiring `blueprints/` directory
- Kit update uses file-level diff with interactive accept/decline/modify prompts
- All specification documents (DESIGN.md, PRD.md, DECOMPOSITION.md, feature specs) are updated to reflect the new model
- Existing tests are updated or removed as appropriate

## Pros and Cons of the Options

### Option 1: Keep Blueprint System As-Is

Retain the full Blueprint Processor with hash-based customization detection and three-way marker merge.

* Good, because single-source-of-truth: one blueprint generates all resources for an artifact kind
* Good, because structural changes to kit outputs can be made by editing one blueprint
* Bad, because three-way merge at marker level is fragile and produces conservative results
* Bad, because hash-based detection requires maintaining hash registries across versions
* Bad, because users must understand dual file sets (blueprints vs generated outputs)
* Bad, because the update pipeline is complex: hash → compare → merge → regenerate

### Option 2: Move Blueprint Processor to Dev-Only Script

Remove Blueprint Processor from the runtime package, keep it as a development build tool (`scripts/build_kit.py` or `make generate-kit`).

* Good, because runtime is simplified — no generation at install/update time
* Good, because kit development still benefits from single-source generation
* Bad, because the build tool still needs maintenance
* Bad, because two divergent codepaths exist: dev-time generation and runtime file copy
* Bad, because blueprint format changes still require parser updates

### Option 3: Remove Blueprints Entirely, Kit = Ready Files

Delete all blueprint files, the Blueprint Processor, and related code. Edit `config/kits/sdlc/` files directly.

* Good, because maximum simplicity — one set of files, one model, one update mechanism
* Good, because largest code deletion (~1500 lines parser + ~40 tests)
* Good, because kit files are already human-readable Markdown and TOML
* Bad, because bulk structural changes across kit files require manual editing
* Bad, because prior investment in blueprint system is fully written off

## More Information

Components to be removed:

| Component | File | Lines (approx) |
|-----------|------|-----------------|
| Blueprint Processor | `utils/blueprint.py` | ~1500 |
| Codebase blueprint parts | `utils/codebase.py` | ~200 |
| `process_kit` | `commands/kit.py` | ~300 |
| `generate-resources` CLI | `commands/kit.py` + `cli.py` | ~100 |
| `migrate_kit` (three-way merge) | `commands/kit.py` | ~400 |
| Hash read/write | `commands/kit.py` | ~100 |
| Blueprint validation | `commands/validate_kits.py` | partial rewrite |
| Tests | 7 files | ~40 tests |
| Blueprints directory | `kits/sdlc/blueprints/` | 9 files |

New kit update model:

| Step | Description |
|------|-------------|
| 1 | Enumerate all files in source kit (from cache) |
| 2 | Classify each file: added / removed / modified / unchanged |
| 3 | Display summary (N added, N removed, N modified, N unchanged) |
| 4 | For each changed file: show unified diff, prompt `[a]ccept [d]ecline [A]ccept-all [D]ecline-all [m]odify` |
| 5 | Apply accepted changes, skip declined, open editor for modify |

## Traceability

- **PRD**: [PRD.md](../PRD.md)
- **DESIGN**: [DESIGN.md](../DESIGN.md)

This decision directly addresses the following requirements and design elements:

* `cpt-cypilot-fr-core-kits` — Simplifies the Extensible Kit System from blueprint-based generation to direct file management
* `cpt-cypilot-fr-core-resource-diff` — Redefines the Resource Diff Engine as the primary kit update mechanism (file-level diff with interactive prompts)
* cpt-cypilot-fr-core-blueprint (see DESIGN — DEPRECATED) — Deprecates and removes the Artifact Blueprint requirement entirely
* cpt-cypilot-component-blueprint-processor — Removes this component from the architecture
* `cpt-cypilot-component-kit-manager` — Simplifies Kit Manager to file copy + file-level diff (no generation, no hash detection)
* `cpt-cypilot-principle-plugin-extensibility` — Redefines kit extensibility as file packages rather than blueprint packages
