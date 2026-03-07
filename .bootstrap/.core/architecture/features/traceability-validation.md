# Feature: Traceability & Validation

<!-- toc -->

- [1. Feature Context](#1-feature-context)
  - [1. Overview](#1-overview)
  - [2. Purpose](#2-purpose)
  - [3. Actors](#3-actors)
  - [4. References](#4-references)
- [2. Actor Flows (CDSL)](#2-actor-flows-cdsl)
  - [Validate Artifacts](#validate-artifacts)
  - [Query Traceability](#query-traceability)
- [3. Processes / Business Logic (CDSL)](#3-processes-business-logic-cdsl)
  - [Scan Artifact IDs](#scan-artifact-ids)
  - [Scan CDSL Instructions](#scan-cdsl-instructions)
  - [Validate Artifact Structure](#validate-artifact-structure)
  - [Cross-Validate Artifacts](#cross-validate-artifacts)
  - [Scan Code Markers](#scan-code-markers)
  - [Cross-Validate Code](#cross-validate-code)
  - [List ID Kinds](#list-id-kinds)
  - [Validate TOC](#validate-toc)
  - [TOC Utilities](#toc-utilities)
  - [Markdown Parsing Utilities](#markdown-parsing-utilities)
  - [Fixing Prompt Enrichment](#fixing-prompt-enrichment)
  - [Headings Contract Validation](#headings-contract-validation)
  - [Load Constraints](#load-constraints)
  - [Language Configuration](#language-configuration)
- [4. States (CDSL)](#4-states-cdsl)
  - [Validation Report Lifecycle](#validation-report-lifecycle)
- [5. Definitions of Done](#5-definitions-of-done)
  - [Artifact Structural Validation](#artifact-structural-validation)
  - [Cross-Artifact Reference Validation](#cross-artifact-reference-validation)
  - [Code Traceability Validation](#code-traceability-validation)
  - [Traceability Query Commands](#traceability-query-commands)
  - [CDSL Instruction Tracking](#cdsl-instruction-tracking)
- [6. Implementation Modules](#6-implementation-modules)
- [7. Acceptance Criteria](#7-acceptance-criteria)

<!-- /toc -->

- [x] `p1` - **ID**: `cpt-cypilot-featstatus-traceability-validation`

## 1. Feature Context

- [x] `p1` - `cpt-cypilot-feature-traceability-validation`

### 1. Overview

Deterministic quality gate that scans artifacts for ID definitions and references, scans code for `@cpt-*` traceability markers, validates structural contracts and cross-references, and provides query commands for navigating the ID graph. All checks are single-pass, stdlib-only, and produce machine-readable JSON reports with file paths, line numbers, and actionable fixing prompts.

### 2. Purpose

Catches structural and traceability issues that AI agents miss or hallucinate — without relying on an LLM. Ensures that every design element has a unique ID, every reference resolves to a definition, every checked reference implies a checked definition, and every `to_code` ID has a matching code marker. Addresses PRD requirements for ID and traceability (`cpt-cypilot-fr-core-traceability`) and CDSL instruction tracking (`cpt-cypilot-fr-core-cdsl`). Artifact validation and cross-artifact consistency capabilities are provided generically by the core Validator for any installed kit.

### 3. Actors

| Actor | Role in Feature |
|-------|-----------------|
| `cpt-cypilot-actor-user` | Invokes validation and traceability query commands from CLI |
| `cpt-cypilot-actor-ai-agent` | Invokes validation after artifact/code generation; uses query commands for navigation |
| `cpt-cypilot-actor-ci-pipeline` | Runs validation as a CI gate to enforce quality floor |

### 4. References

- **PRD**: [PRD.md](../PRD.md) — `cpt-cypilot-fr-core-traceability`, `cpt-cypilot-fr-core-cdsl`
- **Design**: [DESIGN.md](../DESIGN.md) — `cpt-cypilot-component-validator`, `cpt-cypilot-component-traceability-engine`
- **Specs**: [traceability.md](../specs/traceability.md), [CDSL.md](../specs/CDSL.md), [constraints.md](../specs/kit/constraints.md)
- **Dependencies**: `cpt-cypilot-feature-core-infra`

## 2. Actor Flows (CDSL)

### Validate Artifacts

- [x] `p1` - **ID**: `cpt-cypilot-flow-traceability-validation-validate`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User runs `cpt validate` → all registered artifacts validated, cross-references checked, code traceability verified, PASS with coverage report
- User runs `cpt validate --artifact <path>` → single artifact validated against its constraints, cross-references checked against all artifacts

**Error Scenarios**:
- Artifact not found in registry → ERROR with message
- Template structure mismatch → FAIL with heading contract details
- Cross-reference to undefined ID → FAIL with definition hint
- Code marker references non-existent artifact ID → FAIL with orphan details

**Steps**:
1. [x] - `p1` - User invokes `cpt validate [--artifact <path>] [--skip-code] [--verbose]` - `inst-user-validate`
2. [x] - `p1` - Load project context: cypilot config, registry, systems, kits, constraints - `inst-load-context`
3. [x] - `p1` - Resolve artifacts to validate: if `--artifact` specified resolve single artifact from registry, otherwise collect all registered Cypilot-format artifacts - `inst-resolve-artifacts`
4. [x] - `p1` - **IF** registry-level errors detected **RETURN** FAIL report immediately - `inst-if-registry-fail`
5. [x] - `p1` - Run self-check: validate kit examples against templates to ensure kit integrity - `inst-self-check`
6. [x] - `p1` - **FOR EACH** artifact to validate - `inst-foreach-artifact`
   1. [x] - `p1` - Load kind-specific constraints from kit - `inst-load-constraints`
   2. [x] - `p1` - Validate artifact structure using `cpt-cypilot-algo-traceability-validation-validate-structure` - `inst-validate-structure`
7. [x] - `p1` - **IF** per-artifact errors exist **RETURN** FAIL report (stop before cross-validation) - `inst-if-structure-fail`
8. [x] - `p1` - Cross-validate references across all artifacts using `cpt-cypilot-algo-traceability-validation-cross-validate` - `inst-cross-validate`
9. [x] - `p1` - **IF** `--skip-code` is not set, validate code traceability using `cpt-cypilot-algo-traceability-validation-cross-validate-code` - `inst-if-code`
10. [x] - `p1` - Enrich errors with fixing prompts for LLM agents - `inst-enrich-errors`
11. [x] - `p1` - **RETURN** JSON report (status, artifact count, error/warning counts, coverage stats, next step hint) - `inst-return-report`

**Supporting**:
- [x] - `p1` - Imports and module setup for validate command - `inst-validate-imports`
- [x] - `p1` - Internal helpers: attach issue to artifact report, enrich target artifact paths, find artifact in system, suggest path from autodetect - `inst-validate-helpers`
- [x] - `p1` - Human-friendly formatter: issue location, issue formatting, validate report display - `inst-validate-format`

### Query Traceability

- [x] `p1` - **ID**: `cpt-cypilot-flow-traceability-validation-query`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User runs `cpt list-ids` → all ID definitions listed with kind, file, line, checked status
- User runs `cpt where-defined --id <id>` → definition location returned with file path and line
- User runs `cpt where-used --id <id>` → all reference locations returned across artifacts and code
- User runs `cpt get-content --id <id>` → content block under the ID heading returned

**Error Scenarios**:
- ID not found in any artifact → empty result with exit code 2

**Steps**:
1. [x] - `p1` - User invokes one of: `list-ids [--kind K] [--pattern P]`, `where-defined --id <id>`, `where-used --id <id>`, `get-content --id <id>` - `inst-user-query`
2. [x] - `p1` - Load project context and resolve all registered artifacts - `inst-query-load-context`
3. [x] - `p1` - Scan all artifacts using `cpt-cypilot-algo-traceability-validation-scan-ids` to build ID index - `inst-scan-all`
4. [x] - `p1` - **IF** `list-ids --include-code`: scan codebase files for marker references - `inst-if-list-code`
5. [x] - `p1` - **IF** `list-ids`: filter index by `--kind` and `--pattern`, return definitions - `inst-if-list`
6. [x] - `p1` - **IF** `where-defined`: find definition entries for the given ID - `inst-if-where-def`
7. [x] - `p1` - **IF** `where-used`: find reference entries for the given ID across artifacts and code - `inst-if-where-used`
8. [x] - `p1` - **IF** `get-content`: locate ID definition, extract content block from heading scope - `inst-if-get-content`
9. [x] - `p1` - **RETURN** JSON result - `inst-return-query`

**Supporting**:
- [x] - `p1` - Imports and module setup for query commands (list-ids, where-defined, where-used) - `inst-query-imports`
- [x] - `p1` - Argument parsing, context resolution, and artifact collection for query commands - `inst-query-resolve`
- [x] - `p1` - Human-friendly formatters for list-ids, where-defined, and where-used output - `inst-query-format`

## 3. Processes / Business Logic (CDSL)

### Scan Artifact IDs

- [x] `p1` - **ID**: `cpt-cypilot-algo-traceability-validation-scan-ids`

**Input**: Path to a Markdown artifact file

**Output**: List of ID hits: `{id, line, type (definition|reference), checked, has_task, has_priority, priority}`

**Steps**:
1. [x] - `p1` - Read file as UTF-8 lines - `inst-read-file`
2. [x] - `p1` - **FOR EACH** line (skipping fenced code blocks) - `inst-foreach-line`
   1. [x] - `p1` - Match ID definition pattern: `**ID**: \`cpt-...\`` with optional checkbox and priority - `inst-match-def`
   2. [x] - `p1` - **IF** definition matched, extract id, checked, has_task, priority and append as definition hit - `inst-if-def`
   3. [x] - `p1` - **ELSE** match standalone reference pattern: `\`cpt-...\`` with optional checkbox - `inst-match-ref`
   4. [x] - `p1` - **ELSE** scan for inline backticked `cpt-*` references - `inst-match-inline`
3. [x] - `p1` - **RETURN** ordered list of hits - `inst-return-hits`
4. [x] - `p1` - Parse a `cpt-{system}-{kind}-{slug}` identifier: extract system, kind, slug with composite ID support - `inst-parse-cpt`

**Supporting**:
- [x] - `p1` - Imports, regex constants (ID definition, reference, backtick, heading, fence patterns), and ID normalization helper - `inst-scan-ids-datamodel`
- [x] - `p1` - Heading-by-line index builder for document scope resolution - `inst-scan-ids-headings`
- [x] - `p1` - Content scoped extraction: hash-fence blocks, heading scopes, ID-definition scopes - `inst-scan-ids-get-content`
- [x] - `p1` - File I/O utilities: safe text reader, text file iterator, relative path converter - `inst-scan-ids-file-utils`

### Scan CDSL Instructions

- [x] `p1` - **ID**: `cpt-cypilot-algo-traceability-validation-scan-cdsl`

**Input**: Path to a Markdown artifact file

**Output**: List of CDSL instruction records: `{parent_id, inst, checked, line, priority}`

**Steps**:
1. [x] - `p1` - Read file as UTF-8 lines - `inst-read-file`
2. [x] - `p1` - Track current parent ID by scanning ID definitions at heading level - `inst-track-parent`
3. [x] - `p1` - **FOR EACH** line matching CDSL instruction pattern (numbered list item with `inst-{slug}` suffix) - `inst-foreach-cdsl`
   1. [x] - `p1` - Extract checked status, priority, instruction slug - `inst-extract-inst`
   2. [x] - `p1` - Associate with current parent ID - `inst-associate-parent`
4. [x] - `p1` - **RETURN** list of instruction records - `inst-return-cdsl`

**Supporting**:
- [x] - `p1` - CDSL line regex and phase number parsing constants - `inst-scan-cdsl-datamodel`

### Validate Artifact Structure

- [x] `p1` - **ID**: `cpt-cypilot-algo-traceability-validation-validate-structure`

**Input**: Artifact path, artifact kind, kind-specific constraints, registered systems

**Output**: `{errors, warnings}` lists

**Steps**:
1. [x] - `p1` - **IF** constraints have headings contract, validate heading patterns (required sections, levels, ordering) - `inst-check-headings`
2. [x] - `p1` - **IF** headings errors exist **RETURN** early (IDs depend on correct structure) - `inst-if-headings-fail`
3. [x] - `p1` - Scan IDs using `cpt-cypilot-algo-traceability-validation-scan-ids` - `inst-scan-ids`
4. [x] - `p1` - Scan CDSL instructions using `cpt-cypilot-algo-traceability-validation-scan-cdsl` - `inst-scan-cdsl`
5. [x] - `p1` - **FOR EACH** CDSL step where parent ID is checked but step is unchecked - `inst-foreach-cdsl-mismatch`
   1. [x] - `p1` - Emit error: CDSL step unchecked but parent already checked - `inst-emit-cdsl-error`
6. [x] - `p1` - **FOR EACH** parent-child ID pair (heading scope) - `inst-foreach-parent-child`
   1. [x] - `p1` - **IF** all children checked AND parent unchecked, emit error - `inst-if-all-done-parent-not`
   2. [x] - `p1` - **IF** parent checked AND any child unchecked, emit error - `inst-if-parent-done-child-not`
7. [x] - `p1` - Validate ID format and heading scoping per constraints - `inst-validate-id-format`
8. [x] - `p1` - **RETURN** accumulated errors and warnings - `inst-return-structure`

**Supporting**:
- [x] - `p1` - Imports, dataclasses (ReferenceRule, HeadingConstraint, IdConstraint, ArtifactKindConstraints, KitConstraints, ArtifactRecord, ParsedCypilotId), error factory, and optional-bool parser - `inst-structure-datamodel`

### Cross-Validate Artifacts

- [x] `p1` - **ID**: `cpt-cypilot-algo-traceability-validation-cross-validate`

**Input**: List of all artifact records (path, kind, constraints)

**Output**: `{errors, warnings}` lists

**Steps**:
1. [x] - `p1` - Scan all artifacts to build definition index (`defs_by_id`) and reference index (`refs_by_id`) - `inst-build-index`
2. [x] - `p1` - **FOR EACH** reference to an internal-system ID - `inst-foreach-ref`
   1. [x] - `p1` - **IF** no matching definition exists, emit error: reference to undefined ID - `inst-if-no-def`
3. [x] - `p1` - **FOR EACH** reference with checked task marker - `inst-foreach-checked-ref`
   1. [x] - `p1` - **IF** corresponding definition has task marker AND is unchecked, emit error: ref done but def not done - `inst-if-ref-done-def-not`
4. [x] - `p1` - **FOR EACH** definition with checked task marker - `inst-foreach-checked-def`
   1. [x] - `p1` - **IF** any task-tracked reference is unchecked, emit error: def done but ref not done - `inst-if-def-done-ref-not`
5. [x] - `p1` - Enforce coverage rules from constraints (required cross-references between artifact kinds) - `inst-enforce-coverage`
6. [x] - `p1` - **RETURN** accumulated errors and warnings - `inst-return-cross`

**Supporting**:
- [x] - `p1` - Setup helpers: system matcher, kind extractor, external-system detector, heading-info builder, constraint indexing - `inst-cross-datamodel`

### Scan Code Markers

- [x] `p1` - **ID**: `cpt-cypilot-algo-traceability-validation-scan-code`

**Input**: Path to a code file

**Output**: Parsed code file: scope markers, block markers, references, structural errors

**Steps**:
1. [x] - `p1` - Read file lines - `inst-read-code`
2. [x] - `p1` - **FOR EACH** line matching `@cpt-{kind}:{id}:p{N}` - `inst-match-scope`
   1. [x] - `p1` - Extract kind, id, phase; add to scope markers list - `inst-extract-scope`
3. [x] - `p1` - **FOR EACH** line matching `@cpt-begin:{id}:p{N}:inst-{local}` - `inst-match-begin`
   1. [x] - `p1` - Push onto open block stack - `inst-push-block`
4. [x] - `p1` - **FOR EACH** line matching `@cpt-end:{id}:p{N}:inst-{local}` - `inst-match-end`
   1. [x] - `p1` - Pop from stack, validate matching begin marker - `inst-pop-block`
   2. [x] - `p1` - **IF** no matching begin or id/inst mismatch, emit structural error - `inst-if-mismatch`
5. [x] - `p1` - **IF** unclosed blocks remain on stack, emit errors - `inst-if-unclosed`
6. [x] - `p1` - **RETURN** parsed code file with markers and structural errors - `inst-return-code`
7. [x] - `p1` - Define code data model: regex patterns, ScopeMarker, BlockMarker, CodeReference, CodeFile dataclasses, error factory - `inst-code-datamodel`
8. [x] - `p1` - Query and validation methods: list_ids, get by ID/inst, validate duplicate scopes - `inst-code-query-validate`
9. [x] - `p1` - Convenience wrappers: load_code_file, validate_code_file entry points - `inst-code-wrappers`

### Cross-Validate Code

- [x] `p1` - **ID**: `cpt-cypilot-algo-traceability-validation-cross-validate-code`

**Input**: Parsed code files, artifact ID set, `to_code` ID set, forbidden IDs (unchecked task), CDSL instruction map

**Output**: `{errors, warnings}` lists

**Steps**:
1. [x] - `p1` - **IF** traceability mode is DOCS-ONLY and markers found, emit error: markers prohibited - `inst-if-docs-only`
2. [x] - `p1` - Collect all IDs referenced in code markers - `inst-collect-code-ids`
3. [x] - `p1` - **FOR EACH** code marker referencing an ID not in artifact definitions - `inst-foreach-orphan`
   1. [x] - `p1` - Emit error: orphaned code marker (ID not defined in any artifact) - `inst-emit-orphan`
4. [x] - `p1` - **FOR EACH** code marker referencing a `to_code` ID whose task checkbox is unchecked - `inst-foreach-forbidden`
   1. [x] - `p1` - Emit error: code marker exists but artifact task not checked - `inst-emit-forbidden`
5. [x] - `p1` - **FOR EACH** `to_code` ID without any code marker - `inst-foreach-missing`
   1. [x] - `p1` - Emit error: missing code marker for `to_code` ID - `inst-emit-missing`
6. [x] - `p1` - **FOR EACH** CDSL instruction in artifacts with code block markers - `inst-foreach-inst`
   1. [x] - `p1` - **IF** artifact instruction has no matching `@cpt-begin/@cpt-end` block, emit error - `inst-if-inst-missing`
   2. [x] - `p1` - **IF** code block has no matching CDSL step in artifact, emit error - `inst-if-inst-orphan`
7. [x] - `p1` - **RETURN** accumulated errors and warnings - `inst-return-code-cross`

### List ID Kinds

- [x] `p1` - **ID**: `cpt-cypilot-algo-traceability-validation-list-id-kinds`

**Input**: Optional artifact path, project context

**Output**: JSON with kind list, counts, kind↔template mappings

**Steps**:
1. [x] - `p1` - Parse arguments: `--artifact` - `inst-kinds-parse-args`
2. [x] - `p1` - Resolve artifacts to scan (single or all registered) - `inst-kinds-resolve-artifacts`
3. [x] - `p1` - **IF** no artifacts found **RETURN** empty result or error - `inst-kinds-if-no-artifacts`
4. [x] - `p1` - Build known kinds set from kit constraints - `inst-kinds-build-known`
5. [x] - `p1` - **FOR EACH** artifact, scan ID definitions and infer kind tokens from ID slugs - `inst-kinds-scan-ids`
6. [x] - `p1` - Aggregate kind counts and kind↔template mappings - `inst-kinds-aggregate`
7. [x] - `p1` - **RETURN** JSON: `{kinds, kind_counts, kind_to_templates, template_to_kinds}` - `inst-kinds-return`

**Supporting**:
- [x] - `p1` - Imports and module setup for list-id-kinds command - `inst-kinds-imports`
- [x] - `p1` - Human-friendly formatter for list-id-kinds output - `inst-kinds-format`

### Validate TOC

- [x] `p1` - **ID**: `cpt-cypilot-algo-traceability-validation-validate-toc`

**Input**: List of file paths (or all registered artifacts)

**Output**: JSON with per-file TOC validation results

**Steps**:
1. [x] - `p1` - Parse arguments: positional files or `--all` - `inst-toc-parse-args`
2. [x] - `p1` - Resolve file list (explicit paths or all registered artifacts) - `inst-toc-resolve-files`
3. [x] - `p1` - **FOR EACH** file - `inst-toc-foreach-file`
   1. [x] - `p1` - Parse existing TOC block between `<!-- toc -->` markers - `inst-toc-parse-existing`
   2. [x] - `p1` - Generate expected TOC from headings - `inst-toc-generate-expected`
   3. [x] - `p1` - Compare existing vs expected: check anchor validity, heading coverage, staleness - `inst-toc-compare`
   4. [x] - `p1` - **IF** mismatch, record error with diff details - `inst-toc-if-mismatch`
4. [x] - `p1` - **RETURN** JSON: `{status, files_checked, errors}` - `inst-toc-return`

**Supporting**:
- [x] - `p1` - Imports and module setup for validate-toc command - `inst-toc-imports`
- [x] - `p1` - Human-friendly formatter for validate-toc output - `inst-toc-format`

### TOC Utilities

- [x] `p1` - **ID**: `cpt-cypilot-algo-traceability-validation-toc-utils`

**Input**: Markdown content string, optional file path

1. [x] - `p1` - Parse headings from markdown lines (respecting fenced code blocks, min/max level, skip options) - `inst-toc-util-parse-headings`
2. [x] - `p1` - Build TOC string from heading tuples (numbered or bulleted, GitHub-compatible anchors) - `inst-toc-util-build-toc`
3. [x] - `p1` - Insert/update TOC using HTML markers (`<!-- toc -->`) for CLI command - `inst-toc-util-insert-markers`
4. [x] - `p1` - Insert/update TOC using heading-based insertion (`## Table of Contents`) for kit file generator - `inst-toc-util-insert-heading`
5. [x] - `p1` - Process file: strip manual TOC, insert marker-based TOC, write if changed - `inst-toc-util-process-file`
6. [x] - `p1` - Validate TOC: check existence, anchor validity, completeness, staleness - `inst-toc-util-validate`

**Supporting**:
- [x] - `p1` - Imports, constants, fence tracking, GitHub anchor slug generation - `inst-toc-util-datamodel`
- [x] - `p1` - Internal helpers: unique slug, next heading finder, manual TOC stripping, TOC section finder, entry extraction, anchor building, heading line finder - `inst-toc-util-helpers`

### Markdown Parsing Utilities

- [x] `p1` - **ID**: `cpt-cypilot-algo-traceability-validation-parsing-utils`

**Input**: Markdown text, section regex patterns

1. [x] - `p1` - Parse required sections from requirements file (section ID → title mapping) - `inst-parse-required-sections`
2. [x] - `p1` - Find present section IDs in artifact text (e.g., A, B, C letter headings) - `inst-parse-find-sections`
3. [x] - `p1` - Split text by lettered sections with optional line offsets - `inst-parse-split-sections`
4. [x] - `p1` - Extract field blocks from markdown (`**Field Name**: value` patterns) - `inst-parse-field-block`
5. [x] - `p1` - Extract backticked IDs matching a pattern from text - `inst-parse-extract-ids`

**Supporting**:
- [x] - `p1` - Imports, constants, field header termination heuristic, and list item detection helper - `inst-parse-datamodel`

### Fixing Prompt Enrichment

- [x] `p1` - **ID**: `cpt-cypilot-algo-traceability-validation-fixing-prompts`

**Input**: List of validation issues (errors/warnings), optional project root

1. [x] - `p1` - Define probable reasons registry mapping error codes to human-readable templates - `inst-fix-define-reasons`
2. [x] - `p1` - Build actionable fixing prompt per error code with location, ID, and constraint context - `inst-fix-build-prompt`
3. [x] - `p1` - Enrich each issue in-place: resolve reasons, attach fixing prompt, normalize location - `inst-fix-enrich`

**Supporting**:
- [x] - `p1` - Imports, SafeDict formatter, reason resolver, and prompt helper functions (location, kind context, headings hint, relative path) - `inst-fix-datamodel`

### Headings Contract Validation

- [x] `p1` - **ID**: `cpt-cypilot-algo-traceability-validation-headings-contract`

**Input**: Artifact path, artifact kind constraints (headings list), registered systems

**Output**: `{errors, warnings}` lists

**Steps**:
1. [x] - `p1` - Resolve heading constraint IDs by line: match each document heading to a constraint pattern, build per-line active scope stack - `inst-resolve-scope`
2. [x] - `p1` - Scan headings from markdown lines: parse level, title, numbering prefix (respecting fenced code blocks) - `inst-scan-headings`
3. [x] - `p1` - Initialize validation context: load heading constraints, build helper lookups, scan document headings - `inst-validate-init`
4. [x] - `p1` - Check numbering sequence: enforce that sibling sections under the same numeric parent progress consecutively - `inst-check-numbering`
5. [x] - `p1` - Match headings against constraints: hierarchical scope matching, required/multiple/numbered enforcement, emit errors for missing/duplicate/misnumbered headings - `inst-match-headings`

**Supporting**:
- [x] - `p1` - Heading line regex, number prefix regex, and module exports - `inst-headings-datamodel`

### Load Constraints

- [x] `p1` - **ID**: `cpt-cypilot-algo-traceability-validation-load-constraints`

**Input**: Kit root path or raw TOML data

**Output**: `KitConstraints` object or list of parse errors

**Steps**:
1. [x] - `p1` - Load `constraints.toml` from kit root, parse TOML, delegate to `parse_kit_constraints` - `inst-load-toml`
2. [x] - `p1` - Parse kit constraints: iterate artifact kinds, parse headings, identifiers, TOC flag, normalize heading IDs and prev/next references - `inst-parse-kit`
3. [x] - `p1` - Parse individual ID constraint: validate kind, required, name, template, examples, task, priority, to_code, headings, references - `inst-parse-id-constraint`
4. [x] - `p1` - Parse heading constraint: validate level, pattern, description, required, multiple, numbered, id, prev/next, pointer - `inst-parse-heading`
5. [x] - `p1` - Parse reference rule: validate coverage, task, priority, headings fields - `inst-parse-ref-rule`

**Supporting**:
- [x] - `p1` - Examples parser, heading-constraint ID slugifier, and references map parser - `inst-constraints-helpers`

### Language Configuration

- [x] `p1` - **ID**: `cpt-cypilot-algo-traceability-validation-language-config`

**Input**: Optional start path for project config lookup

1. [x] - `p1` - Define extension-based comment format defaults for all supported languages - `inst-lang-define-defaults`
2. [x] - `p1` - Load language config from project core.toml `codeScanning` section (with fallback to defaults) - `inst-lang-load-config`
3. [x] - `p1` - Build regex patterns for `@cpt-begin`/`@cpt-end` markers using language-specific comment syntax - `inst-lang-build-regex`

**Supporting**:
- [x] - `p1` - Imports, default constants, LanguageConfig class, default config factory, and extension-based comment merging helper - `inst-lang-datamodel`

## 4. States (CDSL)

### Validation Report Lifecycle

- [x] `p1` - **ID**: `cpt-cypilot-state-traceability-validation-report`

**States**: NOT_RUN, PASS, FAIL, ERROR

**Initial State**: NOT_RUN

**Transitions**:
1. [x] - `p1` - **FROM** NOT_RUN **TO** PASS **WHEN** validation completes with zero errors (exit code 0) - `inst-pass`
2. [x] - `p1` - **FROM** NOT_RUN **TO** FAIL **WHEN** validation completes with structural or traceability errors (exit code 2) - `inst-fail`
3. [x] - `p1` - **FROM** NOT_RUN **TO** ERROR **WHEN** validation cannot run (no cypilot, missing config, exit code 1) - `inst-error`

## 5. Definitions of Done

### Artifact Structural Validation

- [x] `p1` - **ID**: `cpt-cypilot-dod-traceability-validation-structure`

The system **MUST** validate each artifact against its kit-defined constraints: heading contract (required sections, levels, patterns), ID format (`cpt-{system}-{kind}-{slug}`), priority marker presence, CDSL step consistency (checked parent implies checked steps), and parent-child checkbox consistency. Validation **MUST** produce errors with file path, line number, and actionable fixing prompts. Self-check **MUST** verify kit examples pass template validation before proceeding.

**Implements**:
- `cpt-cypilot-flow-traceability-validation-validate`
- `cpt-cypilot-algo-traceability-validation-validate-structure`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-traceability`

**Covers (DESIGN)**:
- `cpt-cypilot-component-validator`
- `cpt-cypilot-principle-determinism-first`

### Cross-Artifact Reference Validation

- [x] `p1` - **ID**: `cpt-cypilot-dod-traceability-validation-cross-refs`

The system **MUST** validate cross-artifact relationships: every ID reference resolves to a definition, checked references imply checked definitions, checked definitions imply checked references, and coverage rules from `constraints.toml` are enforced (required cross-references between artifact kinds). All consistency violations **MUST** include line numbers and artifact paths.

**Implements**:
- `cpt-cypilot-algo-traceability-validation-cross-validate`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-traceability`

**Covers (DESIGN)**:
- `cpt-cypilot-component-validator`
- `cpt-cypilot-component-traceability-engine`
- `cpt-cypilot-principle-traceability-by-design`

### Code Traceability Validation

- [x] `p1` - **ID**: `cpt-cypilot-dod-traceability-validation-code`

The system **MUST** scan code files for `@cpt-*` markers (scope markers and block markers), validate marker structure (pairing, no empty blocks, proper nesting), and cross-validate against artifact IDs: orphaned markers (code references non-existent ID), missing markers (`to_code` IDs without code markers), forbidden markers (`to_code` ID with unchecked task checkbox), and CDSL instruction-level cross-validation. DOCS-ONLY traceability mode **MUST** prohibit all code markers. Single-pass scanning **MUST** complete in ≤ 3 seconds per artifact.

**Implements**:
- `cpt-cypilot-algo-traceability-validation-scan-code`
- `cpt-cypilot-algo-traceability-validation-cross-validate-code`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-traceability`
- `cpt-cypilot-fr-core-cdsl`

**Covers (DESIGN)**:
- `cpt-cypilot-component-traceability-engine`
- `cpt-cypilot-component-validator`
- `cpt-cypilot-principle-ci-automation-first`
- `cpt-cypilot-constraint-no-weakening`

### Traceability Query Commands

- [x] `p1` - **ID**: `cpt-cypilot-dod-traceability-validation-queries`

The system **MUST** provide CLI commands for navigating the ID graph: `list-ids [--kind K] [--pattern P]` (list definitions matching criteria), `where-defined --id <id>` (find definition location), `where-used --id <id>` (find all references), `get-content --id <id>` (extract content block). All commands **MUST** output JSON, scan all registered artifacts, and use exit codes 0 (found) / 2 (not found).

**Implements**:
- `cpt-cypilot-flow-traceability-validation-query`
- `cpt-cypilot-algo-traceability-validation-scan-ids`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-traceability`

**Covers (DESIGN)**:
- `cpt-cypilot-component-traceability-engine`
- `cpt-cypilot-seq-traceability-query`

### CDSL Instruction Tracking

- [x] `p1` - **ID**: `cpt-cypilot-dod-traceability-validation-cdsl`

The system **MUST** scan CDSL instruction markers (`inst-{slug}` suffixes in numbered list items) from FEATURE artifacts, associate each instruction with its parent ID, track checked/unchecked status, and cross-validate against `@cpt-begin/@cpt-end` block markers in code. Missing implementations and orphaned code blocks **MUST** both produce errors.

**Implements**:
- `cpt-cypilot-algo-traceability-validation-scan-cdsl`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-cdsl`

**Covers (DESIGN)**:
- `cpt-cypilot-component-validator`
- `cpt-cypilot-component-traceability-engine`

## 6. Implementation Modules

| Module | Path | Responsibility |
|--------|------|----------------|
| Validate Command | `skills/.../commands/validate.py` | Main validation orchestration, context loading, report generation |
| Validate TOC | `skills/.../commands/validate_toc.py` | TOC consistency validation |
| List IDs | `skills/.../commands/list_ids.py` | List ID definitions matching criteria |
| List ID Kinds | `skills/.../commands/list_id_kinds.py` | List all ID kind tokens found in artifacts |
| Get Content | `skills/.../commands/get_content.py` | Extract content block for a specific ID |
| Where Defined | `skills/.../commands/where_defined.py` | Find where an ID is defined |
| Where Used | `skills/.../commands/where_used.py` | Find all references to an ID |
| Document Utils | `skills/.../utils/document.py` | ID scanning, CDSL instruction scanning |
| Constraints Utils | `skills/.../utils/constraints.py` | Constraint loading, heading validation, cross-validation |
| Codebase Utils | `skills/.../utils/codebase.py` | Code file scanning, `@cpt-*` marker validation |
| Error Codes | `skills/.../utils/error_codes.py` | Stable error codes for validation issues |
| Fixing Utils | `skills/.../utils/fixing.py` | Fixing prompt generation for LLM agents |
| Language Config | `skills/.../utils/language_config.py` | Language-specific file extensions and comment patterns |
| Parsing Utils | `skills/.../utils/parsing.py` | Markdown structure parsing, section extraction |

## 7. Acceptance Criteria

- [x] `cpt validate` validates all registered artifacts and produces JSON report with PASS/FAIL status
- [x] `cpt validate --artifact <path>` validates a single artifact against its constraints
- [x] Heading contract validation catches missing required sections and wrong heading levels
- [x] ID format validation catches malformed `cpt-*` identifiers with line numbers
- [x] Cross-artifact validation catches undefined references, checked/unchecked mismatches, and coverage gaps
- [x] Code traceability validation catches orphaned markers, missing `to_code` markers, and unchecked-task markers
- [x] CDSL instruction tracking catches missing `@cpt-begin/@cpt-end` blocks and orphaned code blocks
- [x] DOCS-ONLY mode prohibits all `@cpt-*` code markers
- [x] `cpt list-ids`, `where-defined`, `where-used`, `get-content` return correct JSON results
- [x] Validation of a single artifact completes in ≤ 3 seconds
- [x] Full project validation (all artifacts + code) completes in ≤ 10 seconds for typical repositories
- [x] All validation errors include file path, line number, and actionable fixing prompt
- [x] All commands output JSON to stdout and use exit codes 0/1/2
