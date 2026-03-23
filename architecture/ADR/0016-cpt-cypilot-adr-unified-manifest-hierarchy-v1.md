---
status: proposed
date: 2026-03-13
decision-makers: project maintainer
---

# ADR-0016: Unified Manifest Hierarchy for Multi-Layer Component Registration

**ID**: `cpt-cypilot-adr-unified-manifest-hierarchy`

<!-- toc -->

- [Context and Problem Statement](#context-and-problem-statement)
- [Decision Drivers](#decision-drivers)
- [Considered Options](#considered-options)
- [Decision Outcome](#decision-outcome)
  - [Consequences](#consequences)
  - [Confirmation](#confirmation)
- [Pros and Cons of the Options](#pros-and-cons-of-the-options)
  - [Option 1: Extend manifest.toml with Component Sections + Walk-Up Discovery](#option-1-extend-manifesttoml-with-component-sections--walk-up-discovery)
  - [Option 2: Separate Config Files per Component Type](#option-2-separate-config-files-per-component-type)
  - [Option 3: Central Registry Approach](#option-3-central-registry-approach)
- [More Information](#more-information)
- [Traceability](#traceability)

<!-- /toc -->

## Context and Problem Statement

Cypilot generates agent entry points (skills, workflows, rules) for 5 AI coding tools from a hardcoded registry in `_default_agents_config()`. The subagent registration feature (commit `ffb5446`) added kit-level agent declarations via a separate `agents.toml` file. However, there is no mechanism for individual projects to:

1. Register their own skills, agents, workflows, or rules through `cpt generate-agents` (hook support is deferred to a follow-up feature)
2. Extend base templates with project-specific content
3. Compose components across a multi-repo hierarchy (orchestrator repo pattern)
4. Achieve provenance traceability — understanding which layer contributed each component

The orchestrator repo pattern (exemplified by "cyber-repo") provides monorepo-like discoverability with multi-repo isolation. Projects inside the orchestrator inherit shared tooling from parent layers. Without Cypilot support, project-level components work as standalone features but are not portable across agent tools and are not managed by `cpt generate-agents`.

## Decision Drivers

* **Single format** — avoid config file proliferation; reuse the existing manifest.toml schema
* **Deterministic assembly** — the generation pipeline must be a pure function of filesystem inputs, consistent with `cpt-cypilot-principle-determinism-first`; LLMs are reserved for authoring, the pipeline never invokes an LLM
* **Composability** — each layer extends (not replaces) parent layers; block-based template composition
* **Provenance traceability** — developers must be able to inspect which layer contributed each component and what was overridden, to debug unexpected behavior in multi-layer setups
* **Backward compatibility** — existing v1 manifests and standalone repos must work unchanged
* **Python stdlib only** — per `cpt-cypilot-constraint-python-stdlib`
* **Inner scope wins** — consistent with manifest merge semantics where the most specific layer takes precedence

## Considered Options

1. **Extend manifest.toml with component sections + walk-up discovery** — extend the existing manifest.toml format to v2.0 with `[[agents]]`, `[[skills]]`, `[[workflows]]`, `[[rules]]` sections (the schema also reserves `[[hooks]]` and `[[permissions]]` for follow-up features); use walk-up filesystem discovery to find manifests at each layer; add `includes` directive for subdirectory manifests within a layer; MVP supports four layers (Core, Kit, Master Repo, Repo) with Organization and Project layers deferred; same file format at every layer
2. **Separate config files per component type** — keep manifest.toml for kit resources; add separate files (`agents.toml`, `skills.toml`, `rules.toml`) at each layer; walk-up discovery looks for each file type independently
3. **Central registry approach** — a single `components.toml` at the repo level that explicitly lists all components from all layers with their source paths; no walk-up discovery; the developer manually declares the full component tree

## Decision Outcome

Chosen option: **Option 1 — Extend manifest.toml with component sections + walk-up discovery**, because it reuses the existing manifest format that kits already ship (no new formats to learn), naturally maps to the filesystem hierarchy for implicit layer discovery, and provides composable template extension without config file proliferation. The `agents.toml` that already exists for subagent registration is subsumed into the manifest, reducing the number of config files. The addition of an `includes` directive enables component packages (like standctl) within a repo to participate in generation without flattening all definitions into a root manifest.

### Consequences

* Good, because one manifest format serves all layers — kits, repos, and orchestrator layers use identical schema
* Good, because walk-up discovery requires zero explicit configuration for multi-repo setups — filesystem structure IS the configuration
* Good, because `includes` directive enables component packages within a repo without flattening
* Good, because section appending enables additive extension without full template overrides
* Good, because extended agent schema (tools, color, memory_dir, model passthrough) covers real-world agents like standctl
* Good, because provenance report makes multi-layer debugging transparent
* Good, because deterministic pipeline ensures reproducible builds with no LLM dependency
* Neutral, because manifest.toml v2.0 is a schema bump — kits must opt-in to use component sections, but v1 manifests remain valid
* Neutral, because MVP supports four layers (Core, Kit, Master Repo, Repo); Organization and Project layers deferred to follow-up
* Bad, because walk-up discovery relies on heuristics for master repo boundary detection (marker files)
* Neutral, because `[[hooks]]` and `[[permissions]]` support are deferred to follow-up features — initial implementation covers `[[agents]]`, `[[skills]]`, `[[workflows]]`, and `[[rules]]` only; `[[permissions]]` is an important follow-up as manual MCP tool permission setup is a significant time sink
* Neutral, because full block-based template composition is deferred — MVP uses section appending only

### Confirmation

Confirmed when:

- `cpt generate-agents --agent claude` in a multi-layer repo produces correct merged output from all discovered layers (Core, Kit, Master Repo, Repo)
- `cpt generate-agents --show-layers` shows accurate provenance for all components, including which layer contributed each entry
- Standalone repos (no master repo) produce identical output to current behavior — zero regression
- Two runs with identical filesystem inputs produce byte-identical output (deterministic)
- Kit manifest v1.0 continues to parse without error alongside v2.0 manifests
- Existing `agents.toml` declarations are correctly read when present, and migrate cleanly into manifest.toml `[[agents]]`
- Manifests with `includes` correctly load subdirectory manifests at the same layer, with circular detection and ID collision errors
- Extended agent schema fields (tools, color, memory_dir, model passthrough) translate correctly to each target tool's native format

## Pros and Cons of the Options

### Option 1: Extend manifest.toml with Component Sections + Walk-Up Discovery

Single format with component sections added to manifest.toml v2.0; walk-up filesystem discovery locates manifests at each layer in the hierarchy.

* Good, because reuses existing manifest.toml — no new config format to learn
* Good, because walk-up discovery is implicit — filesystem hierarchy IS the config
* Good, because kits and projects use identical schema — one format to document and validate
* Good, because `agents.toml` is subsumed — fewer files to maintain
* Good, because `includes` directive enables modular component packages within a repo
* Good, because provenance traceability is built into the merge process
* Neutral, because requires manifest version bump to 2.0 (but v1 still supported)
* Bad, because walk-up heuristics may misdetect layer boundaries in unusual directory structures

### Option 2: Separate Config Files per Component Type

Keep manifest.toml for kit resources. Add separate files (`skills.toml`, `rules.toml`) at each layer, discovered independently.

* Good, because each file is focused on one concern
* Good, because simpler per-file schema
* Bad, because N component types multiplied by M layers creates many files to discover and merge
* Bad, because `agents.toml` already exists as a precedent — adding more .toml files per type leads to proliferation
* Bad, because harder to see all components a layer provides at a glance
* Bad, because provenance tracking must span multiple files per layer

### Option 3: Central Registry Approach

A single `components.toml` at the repo level that explicitly lists all components from all layers with their source paths. No walk-up discovery.

* Good, because explicit — no discovery heuristics needed
* Good, because single file to inspect for the full component tree
* Bad, because defeats the purpose of multi-layer composition — developer manually maintains the registry
* Bad, because changes at any layer require updating the central registry
* Bad, because no natural inheritance — every repo must redeclare everything
* Bad, because not composable — cannot "just add a manifest.toml" at a new layer

## More Information

- Related: `cpt-cypilot-adr-extract-sdlc-kit` — kits are external GitHub packages with manifest-driven resource binding; this ADR extends that manifest format with component sections
- Related: `cpt-cypilot-adr-remove-system-from-core-toml` — system identity lives in `artifacts.toml`, not `core.toml`; manifests do not duplicate system identity
- Related: Subagent registration (commit `ffb5446`) — current `agents.toml` declarations migrate into manifest.toml `[[agents]]`
- Feature: `cpt-cypilot-feature-project-extensibility` — the feature spec implementing this decision
- Reference implementation: "cyber-repo" orchestrator pattern with standctl integration as first consumer
- Improvement proposal: `PR-108-IMPROVEMENT-PROPOSAL.md` — standctl integration case study that identified gaps G1 (includes), G2 (skills), G3 (extended schema)

## Traceability

- **PRD**: [PRD.md](../PRD.md)
- **DESIGN**: [DESIGN.md](../DESIGN.md)

This decision directly addresses the following requirements and design elements:

* `cpt-cypilot-fr-core-agents` — extends agent generation with multi-layer inputs
* `cpt-cypilot-fr-core-kits` — extends kit system with component declarations in manifest
* `cpt-cypilot-fr-core-kit-manifest` — extends manifest.toml schema to v2.0 with component sections
* `cpt-cypilot-principle-plugin-extensibility` — enables project-level extension of the generation pipeline
* `cpt-cypilot-principle-determinism-first` — pipeline is deterministic, no LLM calls
* `cpt-cypilot-constraint-python-stdlib` — implementation uses only Python stdlib
