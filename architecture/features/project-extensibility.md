# Feature: Project-Level Extensibility


<!-- toc -->

- [1. Feature Context](#1-feature-context)
  - [1.1 Overview](#11-overview)
  - [1.2 Purpose](#12-purpose)
  - [1.3 MVP Scope and Follow-ups](#13-mvp-scope-and-follow-ups)
  - [1.4 Actors](#14-actors)
  - [1.5 References](#15-references)
- [2. Actor Flows (CDSL)](#2-actor-flows-cdsl)
  - [Generate with Multi-Layer Discovery](#generate-with-multi-layer-discovery)
  - [Discover and Register Components](#discover-and-register-components)
  - [Inspect Layer Provenance](#inspect-layer-provenance)
- [3. Processes / Business Logic (CDSL)](#3-processes--business-logic-cdsl)
  - [Walk-Up Layer Discovery](#walk-up-layer-discovery)
  - [Resolve Manifest Includes](#resolve-manifest-includes)
  - [Merge Components](#merge-components)
  - [Section Appending](#section-appending)
  - [Generate Skills](#generate-skills)
  - [Generate Agents](#generate-agents)
  - [Translate Extended Agent Schema](#translate-extended-agent-schema)
  - [Resolve Layer Variables](#resolve-layer-variables)
  - [Build Provenance Report](#build-provenance-report)
  - [Deterministic Component Assembly](#deterministic-component-assembly)
- [4. States (CDSL)](#4-states-cdsl)
  - [Manifest Layer State Machine](#manifest-layer-state-machine)
- [5. Definitions of Done](#5-definitions-of-done)
  - [Manifest V2 Schema Parsing](#manifest-v2-schema-parsing)
  - [Manifest Includes](#manifest-includes)
  - [Walk-Up Layer Discovery](#walk-up-layer-discovery-1)
  - [Inner-Scope-Wins Merging](#inner-scope-wins-merging)
  - [Section Appending](#section-appending-1)
  - [Skills Generation](#skills-generation)
  - [Agents Generation](#agents-generation)
  - [Extended Agent Schema](#extended-agent-schema)
  - [Layer Variable Resolution](#layer-variable-resolution)
  - [Provenance Traceability](#provenance-traceability)
  - [Deterministic Pipeline](#deterministic-pipeline)
  - [Component Auto-Discovery](#component-auto-discovery)
  - [Backward Compatibility](#backward-compatibility)
- [6. Acceptance Criteria](#6-acceptance-criteria)

<!-- /toc -->

- [ ] `p1` - **ID**: `cpt-cypilot-featstatus-project-extensibility`

## 1. Feature Context

- [ ] `p1` - `cpt-cypilot-feature-project-extensibility`

### 1.1 Overview

Extends `cpt generate-agents` with a four-layer manifest hierarchy (Core, Kit, Master Repo, Repo), enabling projects and orchestrator repos to declare skills, agents, workflows, and rules via `manifest.toml`. Adds an `includes` directive for subdirectory manifests (enabling component packages within a repo), `[[skills]]` generation, and an extended agent schema with fields for tool allowlists, model passthrough, color, and memory. Extends the existing `manifest.toml` schema to v2.0 with component sections (`[[agents]]`, `[[skills]]`, `[[workflows]]`, `[[rules]]`). Hook support (`[[hooks]]`) and permissions (`[[permissions]]`) are reserved in the schema but deferred to follow-up features.

The template composition model for MVP is section appending — inner layers can append content to generated templates. Full block-based template composition (replace, prepend, delete, insert operations) is deferred to a follow-up feature.

The entire pipeline is deterministic — same filesystem inputs always produce byte-identical outputs. No LLM invocation at any stage.

### 1.2 Purpose

Enable project-level and multi-repo extensibility for `cpt generate-agents` without breaking existing behavior. Currently only Core and Kit layers contribute components; this adds Master Repo and Repo layers. Projects under an orchestrator repo (the "master repo" pattern) gain monorepo-like discoverability of shared skills, agents, and rules while retaining multi-repo isolation.

The first concrete consumer is the standctl integration into cyber-repo, which distributes 3 agents, 1 skill, and 17 MCP tool permissions through an orchestrator repo pattern. This integration exposed five gaps in the original design (see improvement proposal), of which G1 (includes), G2 (skills generation), and G3 (extended agent schema) are addressed in this feature.

- **Requirements**: `cpt-cypilot-fr-core-agents`, `cpt-cypilot-fr-core-kits`, `cpt-cypilot-fr-core-kit-manifest`
- **Principles**: `cpt-cypilot-principle-plugin-extensibility`, `cpt-cypilot-principle-kit-centric`, `cpt-cypilot-principle-dry`, `cpt-cypilot-principle-determinism-first`
- **Constraints**: `cpt-cypilot-constraint-python-stdlib`, `cpt-cypilot-constraint-cross-platform`
- **Depends on**: `cpt-cypilot-feature-agent-integration`, `cpt-cypilot-feature-blueprint-system`, `cpt-cypilot-feature-subagent-registration`

### 1.3 MVP Scope and Follow-ups

**MVP (this feature)**:
- Four-layer hierarchy: Core → Kit → Master Repo → Repo
- `includes` directive for subdirectory manifests within a layer
- `[[skills]]` generation code path
- Extended agent schema: `tools`, `disallowed_tools`, `color`, `memory_dir`, model passthrough
- Section appending for template composition
- Provenance traceability (`--show-layers`)
- Component auto-discovery (`--discover`)
- Cross-agent translation including OpenAI Codex

**Follow-up: Organization and Project Layers**:
- Add Organization layer (git host root) and Project layer (parent of repo dir)
- Expands from 4 to 6 layers: Core → Kit → Master Repo → Org → Project → Repo
- Requires heuristic-based boundary detection for org/project levels

**Follow-up: Full Template Composition**:
- Block-based template composition with `<!-- @block:NAME -->` markers
- Operations: replace, prepend, append, delete, insert_after, insert_before
- MVP provides section appending only

**Follow-up: Permissions**:
- `[[permissions]]` section for MCP tool allowlisting
- Generation merges `allow` entries into `.claude/settings.local.json` (additive, idempotent)
- Important for reducing manual setup burden — currently a significant time sink for projects using MCP tools

**Follow-up: Hooks**:
- `[[hooks]]` generation (e.g., `SessionEnd` hooks into `.claude/settings.json`)
- Reserved in schema, parser accepts and ignores

### 1.4 Actors

| Actor | Role in Feature |
|-------|-----------------|
| Developer | Runs `cpt generate-agents` to generate agent-native entry points from multi-layer manifest hierarchy |
| AI Assistant | Consumes generated entry points (skills, agents, workflows, rules) |

### 1.5 References

- **PRD**: [PRD.md](../PRD.md) — `cpt-cypilot-fr-core-agents`, `cpt-cypilot-fr-core-kits`, `cpt-cypilot-fr-core-kit-manifest`
- **Design**: [DESIGN.md](../DESIGN.md) — `cpt-cypilot-component-agent-generator`
- **ADR**: `cpt-cypilot-adr-unified-manifest-hierarchy`
- **Dependencies**: `cpt-cypilot-feature-agent-integration`, `cpt-cypilot-feature-blueprint-system`, `cpt-cypilot-feature-subagent-registration` (predecessors for kit-level agent declarations)
- **Improvement Proposal**: `PR-108-IMPROVEMENT-PROPOSAL.md` — standctl integration case study

## 2. Actor Flows (CDSL)

### Generate with Multi-Layer Discovery

- [ ] `p1` - **ID**: `cpt-cypilot-flow-project-extensibility-generate-with-multi-layer`

**Actor**: Developer

**Success Scenarios**:
- Developer runs `cpt generate-agents --agent claude` inside a repo under a master repo hierarchy and all layers are discovered, included manifests resolved, merged, and translated into agent-native entry points
- Developer runs `cpt generate-agents --agent claude` in a standalone repo (no master repo) and only Core, Kit, and Repo layers apply — identical to current behavior

**Error Scenarios**:
- Manifest parse error at any layer — error reported with path and parse details, generation aborted
- Circular include detected — error reported with include chain, generation aborted
- Missing source file referenced by a component — warning emitted, component skipped, generation continues
- `tools` and `disallowed_tools` both specified on same agent — error reported, agent skipped

**Steps**:
1. [ ] - `p1` - Developer invokes `cpt generate-agents --agent <agent>` inside a repo - `inst-invoke-generate`
2. [ ] - `p1` - Determine current repo root via existing `find_project_root()` - `inst-find-repo-root`
3. [ ] - `p1` - Walk up filesystem to discover `manifest.toml` at each layer boundary (repo, master repo) - `inst-walk-up`
4. [ ] - `p1` - Load kit `manifest.toml` files from `core.toml` kit registrations - `inst-load-kit-manifests`
5. [ ] - `p1` - **FOR EACH** discovered manifest: resolve `includes` array, loading subdirectory manifests at the same layer (Process: Resolve Manifest Includes) - `inst-resolve-includes`
6. [ ] - `p1` - Build base config from `_default_agents_config()` (core layer) - `inst-build-base-config`
7. [ ] - `p1` - **FOR EACH** layer in resolution order (Core, Kit, Master Repo, Repo): collect components, inner layer wins on ID collision - `inst-merge-layers`
8. [ ] - `p1` - **FOR EACH** merged agent: generate agent files in agent-native format (Process: Generate Agents) - `inst-generate-agents`
9. [ ] - `p1` - **FOR EACH** merged skill: generate skill files in agent-native format (Process: Generate Skills) - `inst-generate-skills`
10. [ ] - `p1` - **FOR EACH** component with `append` content: apply section appending to generated templates (Process: Section Appending) - `inst-apply-appends`
11. [ ] - `p3` - *(Follow-up)* Generate hooks config (e.g., `.claude/settings.json`) — deferred - `inst-generate-hooks`
12. [ ] - `p3` - *(Follow-up)* Generate permissions config (e.g., `.claude/settings.local.json`) — deferred - `inst-generate-permissions`
13. [ ] - `p1` - Build provenance report — per-component record of winning layer and overridden layers - `inst-build-provenance`
14. [ ] - `p1` - **RETURN** generation report with per-layer provenance - `inst-return-report`

### Discover and Register Components

- [ ] `p2` - **ID**: `cpt-cypilot-flow-project-extensibility-discover-register`

**Actor**: Developer

**Success Scenarios**:
- Developer runs `cpt generate-agents --agent claude --discover` and conventional directories are scanned, manifest populated, then generation proceeds

**Error Scenarios**:
- No components found in conventional directories — user informed, discovery skipped, generation proceeds without discovered components

**Steps**:
1. [ ] - `p2` - Developer invokes `cpt generate-agents --agent <agent> --discover` - `inst-invoke-discover`
2. [ ] - `p2` - Scan conventional directories for components (`.claude/agents/*.md` for agents, `.claude/skills/*/SKILL.md` for skills, `.claude/commands/*.md` for workflows) — hook discovery deferred - `inst-scan-directories`
3. [ ] - `p2` - **FOR EACH** discovered component: generate manifest entry - `inst-generate-entries`
4. [ ] - `p2` - Write component sections into the appropriate `manifest.toml` for the current layer - `inst-write-manifest`
5. [ ] - `p2` - Proceed with Generate with Multi-Layer Discovery flow - `inst-proceed-generate`

### Inspect Layer Provenance

- [ ] `p2` - **ID**: `cpt-cypilot-flow-project-extensibility-inspect-provenance`

**Actor**: Developer

**Success Scenarios**:
- Developer runs `cpt generate-agents --show-layers` and sees a provenance table showing all components and their layer origins
- Developer runs `cpt generate-agents --show-layers --json` and receives machine-readable provenance

**Error Scenarios**:
- No manifests found beyond core — report shows only Core and Kit layers

**Steps**:
1. [ ] - `p2` - Developer invokes `cpt generate-agents --show-layers [--json]` - `inst-invoke-show-layers`
2. [ ] - `p2` - Execute walk-up discovery (same as Generate flow steps 2-7) - `inst-execute-discovery`
3. [ ] - `p2` - Build provenance table: component ID, winning layer (scope + path), overridden layers (scope + path each) - `inst-build-table`
4. [ ] - `p2` - **RETURN** provenance report as JSON (`--json`) or human-readable table - `inst-return-provenance`

## 3. Processes / Business Logic (CDSL)

### Walk-Up Layer Discovery

- [ ] `p1` - **ID**: `cpt-cypilot-algo-project-extensibility-walk-up-discovery`

**Input**: `repo_root` (Path), `cypilot_root` (Path)

**Output**: `List[ManifestLayer]` in resolution order

**Steps**:
1. [ ] - `p1` - Load kit manifests from `core.toml` kit registrations (kit layer) - `inst-load-kit-layer`
2. [ ] - `p1` - Load repo manifest from `{cypilot_root}/config/manifest.toml` (repo layer) - `inst-load-repo-layer`
3. [ ] - `p1` - Walk up from `repo_root` parent directory - `inst-walk-up-start`
4. [ ] - `p1` - At each directory, check for `manifest.toml` - `inst-check-manifest`
5. [ ] - `p1` - Detect master repo boundary: presence of `CLAUDE.md` + `skills/` at same level, or presence of `git/` subdirectory - `inst-detect-master`
6. [ ] - `p1` - **IF** master repo detected, load its `manifest.toml` and stop walk-up - `inst-stop-at-master`
7. [ ] - `p1` - **IF** no master repo found, **RETURN** only kit + repo layers (backward compatible) - `inst-fallback-layers`
8. [ ] - `p1` - **RETURN** layers in resolution order: [kit, master, repo] (missing layers omitted) - `inst-return-layers`

### Resolve Manifest Includes

- [ ] `p1` - **ID**: `cpt-cypilot-algo-project-extensibility-resolve-includes`

**Input**: `manifest` (parsed TOML dict), `manifest_dir` (Path), `include_chain` (set of absolute paths for circular detection)

**Output**: augmented manifest with included components merged in

**Steps**:
1. [ ] - `p1` - Read `includes` array from manifest (default empty) - `inst-read-includes`
2. [ ] - `p1` - **FOR EACH** include path in `includes` - `inst-iterate-includes`
   1. [ ] - `p1` - Resolve path relative to `manifest_dir` - `inst-resolve-include-path`
   2. [ ] - `p1` - **IF** resolved path is in `include_chain`, **RAISE** circular include error with chain - `inst-check-circular`
   3. [ ] - `p1` - **IF** include chain depth > 3, **RAISE** max depth exceeded error - `inst-check-depth`
   4. [ ] - `p1` - Parse included `manifest.toml` - `inst-parse-included`
   5. [ ] - `p1` - Recursively resolve includes in the included manifest (add current path to chain) - `inst-recurse-includes`
   6. [ ] - `p1` - Rewrite `prompt_file` and `source` paths in included components to be relative to the *included* manifest's directory (not the includer's) - `inst-rewrite-paths`
   7. [ ] - `p1` - **FOR EACH** component in included manifest: **IF** component ID already exists in includer, **RAISE** collision error - `inst-check-collision`
   8. [ ] - `p1` - Merge included components into the includer's component lists - `inst-merge-included`
3. [ ] - `p1` - **RETURN** augmented manifest - `inst-return-augmented`

### Merge Components

- [ ] `p1` - **ID**: `cpt-cypilot-algo-project-extensibility-merge-components`

**Input**: `List[ManifestLayer]`

**Output**: `MergedComponents` (dict of component_type to dict of id to component)

**Steps**:
1. [ ] - `p1` - Initialize empty merged dict for each component type (agents, skills, workflows, rules) — hooks and permissions deferred - `inst-init-merged`
2. [ ] - `p1` - **FOR EACH** layer in resolution order (Core, Kit, Master Repo, Repo) - `inst-iterate-layers`
   1. [ ] - `p1` - **FOR EACH** component in layer's manifest (after includes resolved) - `inst-iterate-components`
      1. [ ] - `p1` - Overwrite `merged[type][id]` with this component (last-writer-wins) - `inst-overwrite`
      2. [ ] - `p1` - Record provenance: layer scope, manifest path, whether it overwrote a previous definition - `inst-record-provenance`
3. [ ] - `p1` - **RETURN** merged components with provenance metadata - `inst-return-merged`

### Section Appending

- [ ] `p1` - **ID**: `cpt-cypilot-algo-project-extensibility-section-appending`

**Input**: `base_content` (str), `append_sections` from layers (list of content strings)

**Output**: `composed_content` (str)

**Steps**:
1. [ ] - `p1` - Start with base content from the winning component definition - `inst-start-base`
2. [ ] - `p1` - **FOR EACH** layer in resolution order that declares `append` content for this component ID - `inst-iterate-appends`
   1. [ ] - `p1` - Append the layer's content after the base content, separated by a newline - `inst-append-content`
3. [ ] - `p1` - **RETURN** composed content - `inst-return-composed`

> **Note**: Full block-based template composition (replace, prepend, delete, insert_after, insert_before operations with `<!-- @block:NAME -->` markers) is deferred to a follow-up feature. MVP supports section appending only.

### Generate Skills

- [ ] `p1` - **ID**: `cpt-cypilot-algo-project-extensibility-generate-skills`

**Input**: merged `[[skills]]` components, target agent, project root

**Output**: list of generated skill files

**Steps**:
1. [ ] - `p1` - **FOR EACH** skill in merged components where target agent is in `agents` list - `inst-iterate-skills`
   1. [ ] - `p1` - Read `prompt_file` (or `source`) content from the skill's resolved path - `inst-read-skill-source`
   2. [ ] - `p1` - Apply agent-specific frontmatter wrapper (Process: Translate Extended Agent Schema) - `inst-apply-skill-frontmatter`
   3. [ ] - `p1` - Determine output path using agent-native conventions (see Cross-Agent Translation) - `inst-determine-skill-path`
   4. [ ] - `p1` - Write skill file to output path - `inst-write-skill`
2. [ ] - `p1` - Track created/updated/unchanged in result dict - `inst-track-skill-results`
3. [ ] - `p1` - **RETURN** list of generated skill files with status - `inst-return-skills`

> **Note**: Manifest `[[skills]]` coexist with kit-composed skills (the existing `@cpt:skill` section mechanism). They use different code paths and different output directories. Manifest skills don't replace kit-composed skills.

### Generate Agents

- [x] `p1` - **ID**: `cpt-cypilot-algo-project-extensibility-generate-agents`

**Input**: merged `[[agents]]` components, target agent tool, project root

**Output**: list of generated agent files

**Steps**:
0. [x] - `p1` - Entry point: set up result dict and path template for target agent tool - `inst-generate-manifest-agents`
1. [x] - `p1` - **FOR EACH** agent in merged components where target agent is in `agents` list - `inst-iterate-agents`
   1. [x] - `p1` - Call Translate Extended Agent Schema to get translated frontmatter dict and body prefix (Process: Translate Extended Agent Schema) - `inst-translate-schema`
   2. [x] - `p1` - **IF** translation result has `skip = True`, skip this agent and log skip reason — continue to next - `inst-check-skip`
   3. [x] - `p1` - Read `prompt_file` (or `source`) content from the agent's resolved path - `inst-read-agent-source`
   4. [x] - `p1` - Assemble full file: YAML frontmatter block (`name:`, `description:`, translated frontmatter lines), then body (body_prefix from translation + prompt content) - `inst-assemble-agent-file`
   5. [x] - `p1` - Determine output path using agent-native conventions - `inst-determine-agent-path`
   6. [x] - `p1` - Write agent file to output path - `inst-write-agent`
2. [x] - `p1` - Track created/updated/unchanged in result dict - `inst-track-agent-results`
3. [x] - `p1` - **RETURN** list of generated agent files with status - `inst-return-agents`

### Translate Extended Agent Schema

- [ ] `p1` - **ID**: `cpt-cypilot-algo-project-extensibility-translate-agent-schema`

**Input**: semantic agent definition (from merged manifest), target agent tool

**Output**: agent-native frontmatter/config dict

The extended agent schema uses semantic fields that translate differently per tool:

**Semantic Schema Fields**:

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `id` | string | `^[a-z][a-z0-9_-]*$` | Unique agent identifier |
| `description` | string | | Human-readable description |
| `prompt_file` | string | | Path to prompt file (relative to manifest dir) |
| `source` | string | | Alternative: path to existing agent file |
| `mode` | string | `readwrite`, `readonly` | Tool access level |
| `isolation` | bool | | Isolated context (tool-dependent) |
| `model` | string | any | Model selection — passthrough string (e.g., `inherit`, `fast`, `sonnet`, `haiku`, `opus`, or tool-specific names) |
| `tools` | string[] | | Explicit tool allowlist (mutually exclusive with `disallowed_tools`) |
| `disallowed_tools` | string[] | | Explicit tool denylist (mutually exclusive with `tools`) |
| `color` | string | | Agent color (Claude Code only) |
| `memory_dir` | string | | Persistent memory directory path relative to project root |
| `agents` | string[] | | Which tools to generate for |

**Per-Tool Translation**:

| Semantic Field | Claude Code | Cursor | GitHub Copilot | OpenAI Codex |
|----------------|-------------|--------|----------------|--------------|
| `mode: readonly` | `disallowedTools: Write, Edit` | `readonly: true` | `tools: ["read","search"]` | `sandbox_mode = "read-only"` |
| `mode: readwrite` | `tools: Bash,Read,Write,Edit,Glob,Grep` | `tools: grep,view,edit,bash` | `tools: ["*"]` | `sandbox_mode = "workspace-write"` |
| `model` | direct passthrough to `model:` | `model:` field | n/a | `model` field (developer maps to tool-specific names) |
| `isolation: true` | `isolation: worktree` | n/a | n/a | n/a (always sandboxed) |
| `tools` | `tools:` list in frontmatter | limited tool strings | `tools` JSON array | n/a (MCP server level — noted in developer_instructions) |
| `disallowed_tools` | `disallowedTools:` list | n/a (ignored) | n/a (ignored) | n/a (ignored) |
| `color` | `color:` in frontmatter | n/a (ignored) | n/a (ignored) | n/a (ignored) |
| `memory_dir` | injected in prompt body | n/a (ignored) | n/a (ignored) | n/a (ignored) |

**Steps**:
1. [ ] - `p1` - Validate mutual exclusivity of `tools` and `disallowed_tools` — error if both present - `inst-validate-tools`
2. [ ] - `p1` - **IF** target is `claude`: build YAML frontmatter with all supported fields (tools, disallowedTools, model, isolation, color); inject memory_dir reference in prompt body if present - `inst-translate-claude`
3. [ ] - `p1` - **IF** target is `cursor`: build YAML frontmatter with mode/model; tools field has limited mapping (grep, view, edit, bash) — custom MCP tools not supported - `inst-translate-cursor`
4. [ ] - `p1` - **IF** target is `copilot`: build YAML frontmatter with tools array; no model/isolation/color support - `inst-translate-copilot`
5. [ ] - `p1` - **IF** target is `openai` (Codex): build TOML config with `sandbox_mode` (from mode), `model`, `developer_instructions`; per-agent tool restrictions are not supported (managed at MCP server level) - `inst-translate-codex`
6. [ ] - `p1` - **IF** target is `windsurf`: skip agent generation (no subagent support) with skip reason - `inst-translate-windsurf`
7. [ ] - `p1` - **RETURN** translated config dict - `inst-return-translated`

### Resolve Layer Variables

- [ ] `p1` - **ID**: `cpt-cypilot-algo-project-extensibility-resolve-layer-variables`

**Input**: `layers` (List[ManifestLayer]), existing variables from resolve-vars

**Output**: flat dict of variable to absolute path

**Steps**:
1. [ ] - `p1` - Start with existing variables from `_collect_all_variables()` (`cypilot_path`, `project_root`, kit resource bindings) - `inst-start-existing-vars`
2. [ ] - `p1` - Add layer path variables from discovered layers: `{base_dir}`, `{master_repo}`, `{repo}` - `inst-add-layer-vars`
3. [ ] - `p1` - **FOR EACH** layer, resolve source paths relative to that layer's manifest directory - `inst-resolve-source-paths`
4. [ ] - `p1` - **RETURN** merged variable dict - `inst-return-vars`

### Build Provenance Report

- [ ] `p2` - **ID**: `cpt-cypilot-algo-project-extensibility-build-provenance`

**Input**: `MergedComponents` with provenance metadata

**Output**: `ProvenanceReport` (per-component: winning layer, overridden layers, resolved paths)

**Steps**:
1. [ ] - `p2` - **FOR EACH** component type - `inst-iterate-types`
   1. [ ] - `p2` - **FOR EACH** component ID in merged results - `inst-iterate-ids`
      1. [ ] - `p2` - Record: component ID, component type, winning layer (scope + manifest path), list of overridden layers (scope + manifest path each), final resolved source path, include origin if from an included manifest - `inst-record-entry`
2. [ ] - `p2` - Sort by component type, then by component ID - `inst-sort-report`
3. [ ] - `p2` - **RETURN** structured report (JSON-serializable) - `inst-return-report`

### Deterministic Component Assembly

- [ ] `p1` - **ID**: `cpt-cypilot-algo-project-extensibility-deterministic-assembly`

**Input**: merged components, resolved variables, append sections

**Output**: agent-native files (deterministic)

**Steps**:
1. [ ] - `p1` - **FOR EACH** component in merged results where target agent matches - `inst-iterate-matched`
   1. [ ] - `p1` - Load source content for this component - `inst-load-source`
   2. [ ] - `p1` - Apply section appends from all layers in order (Process: Section Appending) - `inst-apply-appends`
   3. [ ] - `p1` - Translate agent schema fields to agent-native format (Process: Translate Extended Agent Schema) - `inst-translate-schema`
   4. [ ] - `p1` - Substitute all `{variable}` references using resolved variable dict (Process: Resolve Layer Variables) - `inst-substitute-vars`
   5. [ ] - `p1` - Determine output path using agent-native path conventions - `inst-determine-output-path`
   6. [ ] - `p1` - Write file content (sorted, deterministic — no timestamps, no randomness) - `inst-write-file`
2. [ ] - `p1` - **RETURN** list of written files with provenance - `inst-return-written`

## 4. States (CDSL)

### Manifest Layer State Machine

- [ ] `p1` - **ID**: `cpt-cypilot-state-project-extensibility-manifest-layer`

**States**: UNDISCOVERED, LOADED, PARSE_ERROR, INCLUDE_ERROR

**Initial State**: UNDISCOVERED

**Transitions**:
1. [ ] - `p1` - **FROM** UNDISCOVERED **TO** LOADED **WHEN** `manifest.toml` found at layer boundary and parsed successfully (including all includes resolved) - `inst-transition-loaded`
2. [ ] - `p1` - **FROM** UNDISCOVERED **TO** UNDISCOVERED **WHEN** no `manifest.toml` at this layer boundary (layer silently omitted) - `inst-transition-skipped`
3. [ ] - `p1` - **FROM** UNDISCOVERED **TO** PARSE_ERROR **WHEN** `manifest.toml` found but fails to parse - `inst-transition-error`
4. [ ] - `p1` - **FROM** UNDISCOVERED **TO** INCLUDE_ERROR **WHEN** `manifest.toml` parsed but an `includes` entry fails (circular, missing, depth exceeded, ID collision) - `inst-transition-include-error`

## 5. Definitions of Done

### Manifest V2 Schema Parsing

- [x] `p1` - **ID**: `cpt-cypilot-dod-project-extensibility-manifest-v2-schema`

The system **MUST** parse `manifest.toml` files with `version = "2.0"` containing `[[agents]]`, `[[skills]]`, `[[workflows]]`, and `[[rules]]` component sections, plus an optional `includes` array. The `[[agents]]` schema **MUST** support extended fields: `tools`, `disallowed_tools`, `color`, `memory_dir`, and passthrough `model` values beyond `inherit`/`fast`. The schema reserves `[[hooks]]` and `[[permissions]]` for follow-up features; the parser **SHOULD** accept but ignore them. Version `"1.0"` manifests (resources-only) **MUST** continue to work unchanged.

**Implements**:
- `cpt-cypilot-flow-project-extensibility-generate-with-multi-layer`
- `cpt-cypilot-algo-project-extensibility-merge-components`

**Touches**: `manifest.py`

### Manifest Includes

- [x] `p1` - **ID**: `cpt-cypilot-dod-project-extensibility-includes`

The system **MUST** support an `includes` array in `manifest.toml` v2.0 that loads subdirectory manifests at the same layer as the includer. Include paths are relative to the including manifest's directory. `prompt_file` and `source` paths in included manifests resolve relative to the *included* manifest's directory. The system **MUST** detect and reject circular includes, enforce a max depth of 3, and error on component ID collisions between includer and includee (not silent overrides). Included manifests' own `includes` arrays are processed recursively within the depth limit.

**Implements**:
- `cpt-cypilot-algo-project-extensibility-resolve-includes`

**Touches**: `manifest.py`, `agents.py`

### Walk-Up Layer Discovery

- [x] `p1` - **ID**: `cpt-cypilot-dod-project-extensibility-walk-up-discovery`

The system **MUST** walk up the filesystem from repo root, detecting the master repo boundary and loading `manifest.toml` at each discovered layer. Master repo detection uses: `CLAUDE.md` + `skills/` at same level, or presence of `git/` subdirectory. Walk-up stops at master repo root. Missing layers are silently omitted. For MVP, only Core, Kit, Master Repo, and Repo layers are supported. Organization and Project layer detection are deferred to a follow-up.

**Implements**:
- `cpt-cypilot-flow-project-extensibility-generate-with-multi-layer`
- `cpt-cypilot-algo-project-extensibility-walk-up-discovery`

**Touches**: `layer_discovery.py` (new), `agents.py`

### Inner-Scope-Wins Merging

- [ ] `p1` - **ID**: `cpt-cypilot-dod-project-extensibility-inner-scope-wins`

The system **MUST** merge components from all layers using last-writer-wins semantics where innermost scope (Repo) wins over outermost (Core). Components with the same ID at different layers result in the innermost definition winning. Components from `includes` at the same layer **MUST** error on ID collision (not silently override).

**Implements**:
- `cpt-cypilot-algo-project-extensibility-merge-components`

**Touches**: `agents.py`

### Section Appending

- [ ] `p1` - **ID**: `cpt-cypilot-dod-project-extensibility-section-appending`

The system **MUST** support an `append` field on component definitions that appends content to the generated output for that component. Appends from multiple layers stack in resolution order (outermost first). This is the MVP template composition mechanism. Full block-based composition (replace, prepend, delete, insert_after, insert_before with `<!-- @block:NAME -->` markers) is deferred to a follow-up.

**Implements**:
- `cpt-cypilot-algo-project-extensibility-section-appending`

**Touches**: `agents.py`

### Skills Generation

- [ ] `p1` - **ID**: `cpt-cypilot-dod-project-extensibility-skills-generation`

The system **MUST** generate skill files from `[[skills]]` manifest entries into agent-native output paths. Skills are generated for each target agent specified in the skill's `agents` list. Manifest skills coexist with kit-composed skills — they use different code paths and output directories. Generated skill files receive agent-specific frontmatter (e.g., YAML frontmatter with `description:` for Claude Code, `.mdc` format for Cursor).

**Implements**:
- `cpt-cypilot-algo-project-extensibility-generate-skills`

**Touches**: `agents.py`

### Agents Generation

- [x] `p1` - **ID**: `cpt-cypilot-dod-project-extensibility-agents-generation`

The system **MUST** generate agent files from `[[agents]]` manifest entries into agent-native output paths. For each agent entry, `translate_agent_schema()` is called to produce tool-native frontmatter; if the result has `skip = True` (e.g., Windsurf has no subagent support), the agent is silently skipped with reason logged. The assembled file contains a YAML frontmatter block (`name:`, `description:`, plus all translated fields) followed by the body prefix and prompt content. Manifest agents use separate output paths from kit-composed agents.

**Agent Output Paths**:

| Target | Output Path |
|--------|-------------|
| `claude` | `.claude/agents/{id}.md` |
| `cursor` | `.cursor/agents/{id}.mdc` |
| `copilot` | `.github/agents/{id}.md` |
| `openai` | `.agents/{id}/agent.md` |
| `windsurf` | skipped (no subagent support) |

**Implements**:
- `cpt-cypilot-algo-project-extensibility-generate-agents`
- `cpt-cypilot-flow-project-extensibility-generate-with-multi-layer`

**Touches**: `agents.py`

### Extended Agent Schema

- [ ] `p1` - **ID**: `cpt-cypilot-dod-project-extensibility-extended-agent-schema`

The system **MUST** translate extended agent schema fields to agent-native frontmatter for all five supported tools (Claude Code, Cursor, GitHub Copilot, OpenAI Codex, Windsurf). The extended fields are:

- `tools` (string[], optional) — explicit tool allowlist; Claude → `tools:`, Copilot → `tools`, Cursor/Codex → limited or n/a
- `disallowed_tools` (string[], optional) — explicit tool denylist; Claude → `disallowedTools:`, others → n/a
- `color` (string, optional) — Claude → `color:` frontmatter, others → ignored
- `memory_dir` (string, optional) — Claude → injected in prompt body as persistent memory path, others → ignored
- `model` (string, passthrough) — any string value; Claude → direct `model:`, Cursor → `model:`, Codex → `model` field, Copilot → n/a

The system **MUST** validate that `tools` and `disallowed_tools` are mutually exclusive and error if both are specified.

For Codex specifically: `mode: readonly` → `sandbox_mode = "read-only"`, `mode: readwrite` → `sandbox_mode = "workspace-write"`. Per-agent tool restrictions are not supported in Codex (managed at MCP server level); this limitation should be noted in the generation report.

**Implements**:
- `cpt-cypilot-algo-project-extensibility-translate-agent-schema`

**Touches**: `agents.py` (template functions)

### Layer Variable Resolution

- [ ] `p1` - **ID**: `cpt-cypilot-dod-project-extensibility-layer-variables`

The system **MUST** extend resolve-vars with layer path variables (`{base_dir}`, `{master_repo}`, `{repo}`) derived from walk-up discovery. Templates at any layer can reference these variables.

**Implements**:
- `cpt-cypilot-algo-project-extensibility-resolve-layer-variables`

**Touches**: `resolve_vars.py`

### Provenance Traceability

- [ ] `p2` - **ID**: `cpt-cypilot-dod-project-extensibility-provenance`

The system **MUST** produce a provenance report showing, for each generated component: the winning layer (scope + manifest path), any overridden layers, the final resolved source path, and include origin if the component came from an included manifest. Available via `--show-layers` flag (human-readable table or JSON with `--json`).

**Implements**:
- `cpt-cypilot-flow-project-extensibility-inspect-provenance`
- `cpt-cypilot-algo-project-extensibility-build-provenance`

**Touches**: `agents.py`

### Deterministic Pipeline

- [ ] `p1` - **ID**: `cpt-cypilot-dod-project-extensibility-deterministic`

The generation pipeline **MUST** be a pure function of filesystem inputs. Zero LLM calls. No network calls, no randomness, no timestamps in output. Running `cpt generate-agents` twice with identical inputs **MUST** produce byte-identical outputs.

**Implements**:
- `cpt-cypilot-algo-project-extensibility-deterministic-assembly`

**Touches**: `agents.py`
**Constraints**: `cpt-cypilot-principle-determinism-first`, `cpt-cypilot-constraint-python-stdlib`

### Component Auto-Discovery

- [ ] `p2` - **ID**: `cpt-cypilot-dod-project-extensibility-auto-discovery`

The system **MUST** support a `--discover` flag that scans conventional directories (`.claude/agents/*.md`, `.claude/skills/*/SKILL.md`, `.claude/commands/*.md`) and populates the current layer's `manifest.toml` with discovered component entries. Hook and permission discovery are deferred.

**Implements**:
- `cpt-cypilot-flow-project-extensibility-discover-register`

**Touches**: `agents.py`

### Backward Compatibility

- [x] `p1` - **ID**: `cpt-cypilot-dod-project-extensibility-backward-compat`

The system **MUST** produce identical output for standalone repos (no master repo) with no `manifest.toml`. Existing `agents.toml` for kit agents **MUST** be read as fallback when `[[agents]]` is not present in `manifest.toml`. The `_VALID_MODELS` set **MUST** be expanded to accept passthrough model strings while maintaining backward compatibility with `inherit` and `fast`.

**Implements**:
- `cpt-cypilot-flow-project-extensibility-generate-with-multi-layer`

**Touches**: `agents.py`

## 6. Acceptance Criteria

- [ ] `cpt generate-agents --agent claude` in a standalone repo (no `manifest.toml`, no master repo) produces identical output to current behavior
- [ ] `cpt generate-agents --agent claude` in a repo under a master repo hierarchy discovers and merges manifests from Core, Kit, Master Repo, and Repo layers
- [ ] A repo manifest with `includes = ["standctl/manifest.toml"]` correctly loads and merges the included manifest's components at the repo layer
- [ ] Circular includes are detected and produce a clear error with the include chain
- [ ] Component ID collision between includer and includee produces an error (not silent override)
- [ ] `[[skills]]` entries in a manifest produce agent-native skill files (e.g., `.claude/skills/{id}/SKILL.md`)
- [ ] `[[agents]]` entries in a manifest produce agent-native agent files (e.g., `.claude/agents/{id}.md` for Claude Code)
- [ ] An agent definition with `tools = ["mcp__standctl__*", "Bash"]` produces correct `tools:` frontmatter for Claude Code
- [ ] An agent definition with `tools` and `disallowed_tools` both set produces a validation error
- [ ] An agent with `color = "pink"` and `memory_dir = ".claude/agent-memory/x"` produces correct Claude frontmatter and prompt body
- [ ] An agent with `model = "sonnet"` translates to `model: sonnet` for Claude and `sandbox_mode = "workspace-write"` + `model = "..."` for Codex
- [ ] A skill ID defined at both master and repo layers results in the repo-layer definition winning
- [ ] Section appends from master and repo layers both appear in the generated output, stacked in order
- [ ] `cpt generate-agents --show-layers` displays a table showing each component's winning layer, including components from included manifests
- [ ] Running `cpt generate-agents` twice with same inputs produces identical output (diff is empty)
- [ ] `--discover` flag populates `manifest.toml` with discovered components
- [ ] Kit manifest v1.0 (resources-only) continues to parse without error
- [ ] Kit manifest v2.0 with `[[agents]]` section is preferred over separate `agents.toml`

**Non-applicable checklist domains**:
- **PERF**: Not applicable — generation runs once on developer command, not in hot path. Walk-up discovery touches fewer than 10 directories.
- **SEC**: Not applicable — local filesystem tool, no network, no auth, no user data. Manifest content is developer-authored.
- **REL**: Not applicable — CLI tool with no uptime requirements. Errors reported via exit codes.
- **DATA**: Not applicable — no persistent data store. Manifests are user-authored files.
- **INT**: Not applicable — no external API calls. All filesystem-based.
- **OPS**: Not applicable — local CLI tool, no deployment, no monitoring.
- **COMPL**: Not applicable — internal development tooling, no regulatory requirements.
- **UX**: Not applicable — CLI tool, no UI. User experience is via terminal output and generated files.
