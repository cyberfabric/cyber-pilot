# Feature: Blueprint System


<!-- toc -->

- [1. Feature Context](#1-feature-context)
  - [1. Overview](#1-overview)
  - [2. Purpose](#2-purpose)
  - [3. Actors](#3-actors)
  - [4. References](#4-references)
- [2. Actor Flows (CDSL)](#2-actor-flows-cdsl)
  - [Kit Installation](#kit-installation)
  - [Kit Update](#kit-update)
  - [Resource Generation](#resource-generation)
  - [Kit Structural Validation](#kit-structural-validation)
- [3. Processes / Business Logic (CDSL)](#3-processes-business-logic-cdsl)
  - [Parse Blueprint](#parse-blueprint)
  - [Process Kit](#process-kit)
  - [Generate Per-Artifact Outputs](#generate-per-artifact-outputs)
  - [Generate Kit-Wide Constraints](#generate-kit-wide-constraints)
  - [Three-Way Merge](#three-way-merge)
  - [Collect SKILL Extensions](#collect-skill-extensions)
  - [Generate Workflows](#generate-workflows)
- [4. States (CDSL)](#4-states-cdsl)
  - [Kit Installation State](#kit-installation-state)
- [5. Definitions of Done](#5-definitions-of-done)
  - [Blueprint Parsing](#blueprint-parsing)
  - [Per-Artifact Resource Generation](#per-artifact-resource-generation)
  - [Kit-Wide Constraints Generation](#kit-wide-constraints-generation)
  - [Kit Installation and Registration](#kit-installation-and-registration)
  - [Kit Update](#kit-update-1)
  - [Kit Structural Validation](#kit-structural-validation-1)
  - [Resource Regeneration](#resource-regeneration)
- [6. Implementation Modules](#6-implementation-modules)
- [7. Acceptance Criteria](#7-acceptance-criteria)

<!-- /toc -->

- [ ] `p1` - **ID**: `cpt-cypilot-featstatus-blueprint-system`

## 1. Feature Context

- [ ] `p1` - `cpt-cypilot-feature-blueprint-system`

### 1. Overview

Single-source-of-truth blueprint files that define artifact kinds and generate all kit resources. Each blueprint is a Markdown file enriched with `@cpt:` markers from which the Blueprint Processor deterministically produces templates, rules, checklists, examples, constraints, and workflows. The Kit Manager handles kit lifecycle — installation, registration, update, and structural validation.

### 2. Purpose

Eliminates resource duplication across kit artifacts. Without blueprints, every artifact kind requires separate manually-maintained files (template, rules, checklist, constraints) that duplicate structural knowledge and drift apart over time. Addresses PRD requirements for an extensible kit system (`cpt-cypilot-fr-core-kits`) and a core blueprint contract (`cpt-cypilot-fr-core-blueprint`).

### 3. Actors

| Actor | Role in Feature |
|-------|-----------------|
| `cpt-cypilot-actor-user` | Installs kits, customizes blueprints, triggers resource generation and kit updates |
| `cpt-cypilot-actor-cypilot-cli` | Executes blueprint processing, kit management commands, and structural validation |

### 4. References

- **PRD**: [PRD.md](../PRD.md) — `cpt-cypilot-fr-core-blueprint`, `cpt-cypilot-fr-core-kits`
- **Design**: [DESIGN.md](../DESIGN.md) — `cpt-cypilot-component-blueprint-processor`, `cpt-cypilot-component-kit-manager`
- **Dependencies**: `cpt-cypilot-feature-core-infra`

## 2. Actor Flows (CDSL)

### Kit Installation

- [x] `p1` - **ID**: `cpt-cypilot-flow-blueprint-system-kit-install`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User installs a kit from a local path → kit source saved to reference directory, blueprints copied to user-editable location, all resources generated, kit registered in `{cypilot_path}/config/core.toml`
- User installs a kit during `cypilot init` → same as above, triggered automatically for bundled kits

**Error Scenarios**:
- Kit path does not contain a `blueprints/` directory → error with structural requirements
- Blueprint file has invalid marker syntax → error listing malformed markers with line numbers
- Kit slug already registered and `--force` not provided → error with hint to use `--force`

**Steps**:
1. [x] - `p1` - User invokes `cypilot kit install <path> [--force]` - `inst-user-install`
2. [x] - `p1` - Validate kit source: verify `blueprints/` directory exists with at least one `.md` file - `inst-validate-source`
3. [x] - `p1` - **IF** validation fails **RETURN** error with structural requirements - `inst-if-invalid-source`
4. [x] - `p1` - Extract kit metadata: read `@cpt:blueprint` marker from first blueprint to get kit slug and version - `inst-extract-metadata`
5. [x] - `p1` - **IF** kit slug already registered AND `--force` not set **RETURN** error with hint - `inst-if-already-registered`
6. [x] - `p1` - Save kit source to `{cypilot_path}/.core/kits/{slug}/` (reference copy) - `inst-save-reference`
7. [x] - `p1` - Copy blueprints to `{cypilot_path}/config/kits/{slug}/blueprints/` (user-editable) - `inst-copy-blueprints`
8. [x] - `p1` - Process all blueprints using `cpt-cypilot-algo-blueprint-system-process-kit` - `inst-process-blueprints`
9. [x] - `p1` - Register kit in `{cypilot_path}/config/core.toml` with slug, format, path, and artifact templates - `inst-register-kit`
10. [x] - `p1` - **RETURN** installation summary (kit slug, generated files count, registered artifact kinds) - `inst-return-install-ok`

### Kit Update

- [x] `p1` - **ID**: `cpt-cypilot-flow-blueprint-system-kit-update`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User runs `cypilot kit update --force` → reference replaced, all user blueprints overwritten, outputs regenerated
- User runs `cypilot kit update` (additive) → three-way diff preserves user modifications, inserts new markers, regenerates outputs

**Error Scenarios**:
- No kits installed → error with hint to install first
- Three-way diff finds conflicts (both user and kit modified same section) → error listing conflicts for manual resolution

**Steps**:
1. [x] - `p1` - User invokes `cypilot kit update [--force] [--kit SLUG]` - `inst-user-update`
2. [x] - `p1` - Resolve target kits: if `--kit` specified use that, otherwise update all installed kits - `inst-resolve-kits`
3. [x] - `p1` - **FOR EACH** kit in target kits - `inst-foreach-kit`
   1. [x] - `p1` - Load new kit source from cache at `{cypilot_path}/.core/kits/{slug}/` - `inst-load-new-source`
   2. [x] - `p1` - **IF** `--force` - `inst-if-force`
      1. [x] - `p1` - Overwrite user blueprints in `{cypilot_path}/config/kits/{slug}/blueprints/` with new source - `inst-force-overwrite`
   3. [x] - `p1` - Regenerate all outputs using `cpt-cypilot-algo-blueprint-system-process-kit` - `inst-regenerate`

> **p2**: ELSE apply three-way merge using `cpt-cypilot-algo-blueprint-system-three-way-merge` (additive mode with conflict detection)
   5. [x] - `p1` - Update kit version in `{cypilot_path}/config/core.toml` - `inst-update-version`
4. [x] - `p1` - **RETURN** update summary (kits updated, files regenerated, conflicts if any) - `inst-return-update-ok`

### Resource Generation

- [x] `p1` - **ID**: `cpt-cypilot-flow-blueprint-system-generate-resources`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User runs `cypilot generate-resources` → all kit blueprints re-processed, outputs regenerated

**Error Scenarios**:
- Blueprint has syntax errors → error with marker, line number, and fix suggestion

**Steps**:
1. [x] - `p1` - User invokes `cypilot generate-resources [--kit SLUG]` - `inst-user-generate`
2. [x] - `p1` - Resolve target kits from `{cypilot_path}/config/core.toml` - `inst-resolve-gen-kits`
3. [x] - `p1` - **FOR EACH** kit in target kits - `inst-foreach-gen-kit`
   1. [x] - `p1` - Process all blueprints using `cpt-cypilot-algo-blueprint-system-process-kit` - `inst-gen-process`
4. [x] - `p1` - **RETURN** generation summary (files written, artifact kinds processed) - `inst-return-gen-ok`

### Kit Structural Validation

- [x] `p1` - **ID**: `cpt-cypilot-flow-blueprint-system-validate-kits`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User runs `cypilot validate-kits` → all installed kits validated, PASS with coverage report

**Error Scenarios**:
- Kit missing `blueprints/` directory → FAIL with details
- Blueprint missing mandatory `@cpt:blueprint` marker → FAIL with details

**Steps**:
1. [x] - `p1` - User invokes `cypilot validate-kits` - `inst-user-validate-kits`
2. [x] - `p1` - Load all registered kits from `{cypilot_path}/config/core.toml` - `inst-load-registered-kits`
3. [x] - `p1` - **FOR EACH** kit - `inst-foreach-validate-kit`
   1. - `p1` - Verify `blueprints/` directory exists in user-editable path - `inst-verify-blueprints-dir`
   2. - `p1` - **FOR EACH** blueprint file in `blueprints/` - `inst-foreach-blueprint`
      1. - `p1` - Parse blueprint and validate marker syntax - `inst-validate-markers`
      2. - `p1` - Verify `@cpt:blueprint` identity marker present - `inst-verify-identity`
      3. - `p1` - Verify at least one `@cpt:heading` or output marker present - `inst-verify-content`
4. [x] - `p1` - **RETURN** validation result (PASS/FAIL, per-kit details) - `inst-return-validate-ok`

## 3. Processes / Business Logic (CDSL)

### Parse Blueprint

- [x] `p1` - **ID**: `cpt-cypilot-algo-blueprint-system-parse-blueprint`

**Input**: Path to a single blueprint `.md` file

**Output**: Parsed blueprint structure: list of markers with type, content, line range, and metadata

**Steps**:
1. [x] - `p1` - Read file content as UTF-8 text - `inst-read-file`
2. [x] - `p1` - Scan for opening markers: lines matching `` `@cpt:TYPE` `` pattern - `inst-scan-open`
3. [x] - `p1` - **FOR EACH** opening marker - `inst-foreach-marker`
   1. [x] - `p1` - Find matching closing marker `` `@/cpt:TYPE` `` - `inst-find-close`
   2. [x] - `p1` - **IF** no closing marker found **RETURN** error with line number - `inst-if-unclosed`
   3. [x] - `p1` - Extract content between markers (fenced code blocks: ` ```toml `, ` ```markdown `) - `inst-extract-content`
   4. [x] - `p1` - Parse marker metadata based on type (TOML config for blueprint/heading/id, Markdown for rule/check/skill/workflow) - `inst-parse-metadata`
4. [x] - `p1` - Validate no nested markers (flat structure required) - `inst-validate-flat`
5. [x] - `p1` - **RETURN** parsed blueprint with ordered marker list - `inst-return-parsed`

### Process Kit

- [x] `p1` - **ID**: `cpt-cypilot-algo-blueprint-system-process-kit`

**Input**: Kit slug, path to kit's `blueprints/` directory

**Output**: Generated output files in `{cypilot_path}/config/kits/{slug}/`

**Steps**:
1. [x] - `p1` - List all `.md` files in `blueprints/` directory - `inst-list-blueprints`
2. [x] - `p1` - **FOR EACH** blueprint file - `inst-foreach-bp`
   1. [x] - `p1` - Parse blueprint using `cpt-cypilot-algo-blueprint-system-parse-blueprint` - `inst-parse-bp`
   2. [x] - `p1` - Extract artifact kind from `@cpt:blueprint` marker (`artifact` key, or filename without `.md`) - `inst-extract-kind`
   3. [x] - `p1` - Generate per-artifact outputs using `cpt-cypilot-algo-blueprint-system-generate-artifact-outputs` - `inst-gen-artifact`
3. [x] - `p1` - Aggregate constraints from all blueprints using `cpt-cypilot-algo-blueprint-system-generate-constraints` - `inst-gen-constraints`
4. [x] - `p1` - **RETURN** list of generated file paths - `inst-return-generated`

> **p2**: Collect SKILL extensions (`cpt-cypilot-algo-blueprint-system-collect-skill`) and generate workflow files (`cpt-cypilot-algo-blueprint-system-generate-workflows`)

### Generate Per-Artifact Outputs

- [x] `p1` - **ID**: `cpt-cypilot-algo-blueprint-system-generate-artifact-outputs`

**Input**: Parsed blueprint, artifact kind, output directory (`{cypilot_path}/config/kits/{slug}/artifacts/{KIND}/`)

**Output**: Generated files: `rules.md`, `checklist.md`, `template.md`, `example.md`

**Steps**:
1. [x] - `p1` - Create output directory if absent - `inst-mkdir-output`
2. [x] - `p1` - Generate `rules.md`: collect `@cpt:rules` block (if present) and all `@cpt:rule` blocks, concatenate with section headers - `inst-gen-rules`
3. [x] - `p1` - Generate `checklist.md`: collect `@cpt:checklist` block (if present) and all `@cpt:check` blocks, concatenate with section headers - `inst-gen-checklist`
4. [x] - `p1` - Generate `template.md`: extract headings from `@cpt:heading` markers (use `template` key with placeholder syntax), strip all metadata markers, preserve `@cpt:prompt` content as writing instructions - `inst-gen-template`
5. [x] - `p1` - Generate `example.md`: extract `examples` array from `@cpt:heading` markers (first value per heading), collect `@cpt:example` blocks for body-level examples - `inst-gen-example`
6. [x] - `p1` - **IF** blueprint has no `artifact` key (codebase blueprint) - `inst-if-codebase`
   1. [x] - `p1` - Generate `codebase/rules.md` and `codebase/checklist.md` instead of per-artifact outputs - `inst-gen-codebase`
7. [x] - `p1` - Write all generated files to output directory - `inst-write-outputs`
8. [x] - `p1` - **RETURN** list of written file paths - `inst-return-outputs`

### Generate Kit-Wide Constraints

- [x] `p1` - **ID**: `cpt-cypilot-algo-blueprint-system-generate-constraints`

**Input**: List of parsed blueprints for a kit

**Output**: `{cypilot_path}/config/kits/{slug}/constraints.toml`

**Steps**:
1. [x] - `p1` - Initialize empty constraints structure with `version` and `id_kinds` sections - `inst-init-constraints`
2. [x] - `p1` - **FOR EACH** parsed blueprint - `inst-foreach-bp-constraints`
   1. [x] - `p1` - Extract artifact kind from `@cpt:blueprint` marker - `inst-extract-kind-constraint`
   2. [x] - `p1` - **FOR EACH** `@cpt:heading` marker - `inst-foreach-heading`
      1. [x] - `p1` - **IF** heading has `pattern` key, add to constraints under artifact kind - `inst-add-heading-pattern`
   3. [x] - `p1` - **FOR EACH** `@cpt:id` marker - `inst-foreach-id`
      1. [x] - `p1` - Extract ID kind definition (name, `to_code`, `defined_in`, `referenced_in`) - `inst-extract-id-kind`
      2. [x] - `p1` - Add to `id_kinds` section - `inst-add-id-kind`
3. [x] - `p1` - Write constraints to `{cypilot_path}/config/kits/{slug}/constraints.toml` using deterministic TOML serialization - `inst-write-constraints`
4. [x] - `p1` - **RETURN** path to written constraints file - `inst-return-constraints`

### Three-Way Merge

- [ ] `p2` - **ID**: `cpt-cypilot-algo-blueprint-system-three-way-merge`

**Input**: Reference blueprint (old version in `{cypilot_path}/.core/kits/{slug}/`), user blueprint (`{cypilot_path}/config/kits/{slug}/blueprints/`), new blueprint (from updated kit source)

**Output**: Merged blueprint content, or list of conflicts

**Steps**:
1. - `p2` - Parse all three versions into marker lists - `inst-parse-three`
2. - `p2` - Identify marker-level changes: added markers (in new, not in reference), removed markers (in reference, not in new), modified markers (in both, content differs) - `inst-identify-changes`
3. - `p2` - Identify user modifications: markers where user blueprint differs from reference - `inst-identify-user-mods`
4. - `p2` - Apply merge rules - `inst-apply-merge`
   1. - `p2` - Insert new markers (added by kit, not present in user) at appropriate positions - `inst-insert-new`
   2. - `p2` - Preserve user-modified markers unchanged - `inst-preserve-user`
   3. - `p2` - Update unmodified markers to new version - `inst-update-unmodified`
   4. - `p2` - Respect user deletions: markers removed by user stay removed - `inst-respect-deletions`
5. - `p2` - **IF** both user and kit modified the same marker - `inst-if-conflict`
   1. - `p2` - Flag as conflict, include both versions - `inst-flag-conflict`
6. - `p2` - **RETURN** merged content or conflict list - `inst-return-merge`

### Collect SKILL Extensions

- [ ] `p2` - **ID**: `cpt-cypilot-algo-blueprint-system-collect-skill`

**Input**: List of parsed blueprints

**Output**: Aggregated SKILL extension content for SKILL.md composition

**Steps**:
1. - `p2` - **FOR EACH** parsed blueprint - `inst-foreach-skill-bp`
   1. - `p2` - Extract all `@cpt:skill` marker content - `inst-extract-skill`
2. - `p2` - Concatenate sections in blueprint order - `inst-concat-skill`
3. - `p2` - **RETURN** aggregated SKILL content - `inst-return-skill`

### Generate Workflows

- [ ] `p2` - **ID**: `cpt-cypilot-algo-blueprint-system-generate-workflows`

**Input**: List of parsed blueprints, output directory (`{cypilot_path}/config/kits/{slug}/workflows/`)

**Output**: Generated workflow `.md` files

**Steps**:
1. - `p2` - **FOR EACH** parsed blueprint - `inst-foreach-wf-bp`
   1. - `p2` - Extract all `@cpt:workflow` markers - `inst-extract-workflow`
   2. - `p2` - **FOR EACH** workflow marker - `inst-foreach-workflow`
      1. - `p2` - Parse TOML header (name, description) and Markdown body (steps) - `inst-parse-workflow`
      2. - `p2` - Write to `{cypilot_path}/config/kits/{slug}/workflows/{name}.md` - `inst-write-workflow`
2. - `p2` - **RETURN** list of generated workflow paths - `inst-return-workflows`

## 4. States (CDSL)

### Kit Installation State

- [x] `p1` - **ID**: `cpt-cypilot-state-blueprint-system-kit-install`

**States**: UNINSTALLED, INSTALLED, OUTDATED

**Initial State**: UNINSTALLED

**Transitions**:
1. [x] - `p1` - **FROM** UNINSTALLED **TO** INSTALLED **WHEN** `cypilot kit install` completes successfully - `inst-install-complete`
2. [x] - `p1` - **FROM** INSTALLED **TO** OUTDATED **WHEN** cached kit version differs from installed version - `inst-version-drift`
3. [x] - `p1` - **FROM** OUTDATED **TO** INSTALLED **WHEN** `cypilot kit update` completes successfully - `inst-update-complete`

## 5. Definitions of Done

### Blueprint Parsing

- [x] `p1` - **ID**: `cpt-cypilot-dod-blueprint-system-parsing`

The system **MUST** parse blueprint `.md` files, extracting all `@cpt:` marker types (`blueprint`, `heading`, `id`, `rule`, `check`, `prompt`, `example`, `rules`, `checklist`, `skill`, `system-prompt`, `workflow`) with their content, metadata, and line ranges. Malformed markers **MUST** produce actionable error messages with file path and line number.

**Implements**:
- `cpt-cypilot-algo-blueprint-system-parse-blueprint`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-blueprint`

**Covers (DESIGN)**:
- `cpt-cypilot-component-blueprint-processor`

### Per-Artifact Resource Generation

- [x] `p1` - **ID**: `cpt-cypilot-dod-blueprint-system-artifact-gen`

The system **MUST** generate four output files per artifact blueprint: `rules.md` (from `@cpt:rules` + `@cpt:rule`), `checklist.md` (from `@cpt:checklist` + `@cpt:check`), `template.md` (from `@cpt:heading` + `@cpt:prompt`, with placeholder syntax preserved), and `example.md` (from `@cpt:heading` examples + `@cpt:example`). Codebase blueprints (without `artifact` key) **MUST** generate `codebase/rules.md` and `codebase/checklist.md` instead.

**Implements**:
- `cpt-cypilot-algo-blueprint-system-generate-artifact-outputs`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-blueprint`

**Covers (DESIGN)**:
- `cpt-cypilot-component-blueprint-processor`
- `cpt-cypilot-principle-dry`

### Kit-Wide Constraints Generation

- [x] `p1` - **ID**: `cpt-cypilot-dod-blueprint-system-constraints-gen`

The system **MUST** aggregate `@cpt:heading` and `@cpt:id` markers from all blueprints in a kit into a single `constraints.toml` at `{cypilot_path}/config/kits/{slug}/constraints.toml`. The constraints file **MUST** define ID kinds with their `to_code`, `defined_in`, and `referenced_in` attributes, using deterministic TOML serialization.

**Implements**:
- `cpt-cypilot-algo-blueprint-system-generate-constraints`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-blueprint`

**Covers (DESIGN)**:
- `cpt-cypilot-component-blueprint-processor`
- `cpt-cypilot-constraint-markdown-contract`

### Kit Installation and Registration

- [x] `p1` - **ID**: `cpt-cypilot-dod-blueprint-system-kit-install`

The system **MUST** provide `cypilot kit install <path>` that saves kit source to `{cypilot_path}/.core/kits/{slug}/` (reference), copies blueprints to `{cypilot_path}/config/kits/{slug}/blueprints/` (user-editable), processes all blueprints to generate outputs, and registers the kit in `{cypilot_path}/config/core.toml`. Installation of an already-registered kit without `--force` **MUST** produce exit code 2 with a helpful message.

**Implements**:
- `cpt-cypilot-flow-blueprint-system-kit-install`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-kits`

**Covers (DESIGN)**:
- `cpt-cypilot-component-kit-manager`
- `cpt-cypilot-principle-kit-centric`

### Kit Update

- [x] `p1` - **ID**: `cpt-cypilot-dod-blueprint-system-kit-update`

The system **MUST** provide `cypilot kit update [--force] [--kit SLUG]`. Force mode **MUST** overwrite all user blueprints and regenerate outputs. Additive mode (p2) **MUST** use three-way diff with the reference in `{cypilot_path}/.core/kits/{slug}/` to preserve user modifications while incorporating new markers.

**Implements**:
- `cpt-cypilot-flow-blueprint-system-kit-update`
- `cpt-cypilot-algo-blueprint-system-three-way-merge`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-kits`

**Covers (DESIGN)**:
- `cpt-cypilot-component-kit-manager`
- `cpt-cypilot-principle-no-manual-maintenance`

### Kit Structural Validation

- [x] `p1` - **ID**: `cpt-cypilot-dod-blueprint-system-validate-kits`

The system **MUST** provide `cypilot validate-kits` that validates all installed kits have a `blueprints/` directory, each blueprint has a valid `@cpt:blueprint` identity marker, and marker syntax is correct. Output **MUST** be JSON with PASS/FAIL status and per-kit details.

**Implements**:
- `cpt-cypilot-flow-blueprint-system-validate-kits`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-kits`

**Covers (DESIGN)**:
- `cpt-cypilot-component-kit-manager`

### Resource Regeneration

- [x] `p1` - **ID**: `cpt-cypilot-dod-blueprint-system-regenerate`

The system **MUST** provide `cypilot generate-resources [--kit SLUG]` that re-processes all blueprints for the specified kit (or all kits) and regenerates all output files. This enables users to customize blueprints and see the results without a full kit update cycle.

**Implements**:
- `cpt-cypilot-flow-blueprint-system-generate-resources`
- `cpt-cypilot-algo-blueprint-system-process-kit`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-blueprint`

**Covers (DESIGN)**:
- `cpt-cypilot-component-blueprint-processor`
- `cpt-cypilot-principle-plugin-extensibility`

## 6. Implementation Modules

| Module | Path | Responsibility |
|--------|------|----------------|
| Kit Command | `skills/.../commands/kit.py` | Kit install, update, generate-resources CLI handlers |
| Validate Kits | `skills/.../commands/validate_kits.py` | Kit structural validation command |
| Blueprint Utils | `skills/.../utils/blueprint.py` | Blueprint parsing, `@cpt:` marker extraction, resource generation |
| Constraints Utils | `skills/.../utils/constraints.py` | Constraint loading and validation (shared with F-03) |

## 7. Acceptance Criteria

- [ ] `cypilot kit install <path>` installs a kit, generates all outputs, and registers in `{cypilot_path}/config/core.toml`
- [ ] `cypilot kit update --force` overwrites user blueprints and regenerates all outputs
- [ ] `cypilot generate-resources` re-processes all blueprints and regenerates outputs from user-edited blueprints
- [ ] `cypilot validate-kits` reports PASS for structurally valid kits and FAIL with details for invalid ones
- [ ] Blueprint parsing handles all marker types: `@cpt:blueprint`, `@cpt:heading`, `@cpt:id`, `@cpt:rule`, `@cpt:check`, `@cpt:prompt`, `@cpt:example`, `@cpt:rules`, `@cpt:checklist`, `@cpt:skill`, `@cpt:system-prompt`, `@cpt:workflow`
- [ ] Generated `template.md` preserves placeholder syntax `{descriptive text}` from `@cpt:heading` markers
- [ ] Generated `constraints.toml` aggregates ID kinds with `to_code`, `defined_in`, `referenced_in` from all blueprints
- [ ] Malformed blueprint markers produce actionable error messages with file path and line number
- [ ] All commands output JSON to stdout and use exit codes 0/1/2
- [ ] Kit installation during `cypilot init` works identically to explicit `cypilot kit install`
