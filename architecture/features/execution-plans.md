# Feature: Execution Plans


<!-- toc -->

- [1. Feature Context](#1-feature-context)
  - [1.1 Overview](#11-overview)
  - [1.2 Purpose](#12-purpose)
  - [1.3 Actors](#13-actors)
  - [1.4 References](#14-references)
- [2. Actor Flows (CDSL)](#2-actor-flows-cdsl)
  - [Generate Execution Plan](#generate-execution-plan)
  - [Chunk Raw Input Package](#chunk-raw-input-package)
  - [Execute Phase](#execute-phase)
  - [Check Plan Status](#check-plan-status)
- [3. Processes / Business Logic (CDSL)](#3-processes--business-logic-cdsl)
  - [Decompose Task](#decompose-task)
  - [Compile Phase File](#compile-phase-file)
  - [Enforce Line Budget](#enforce-line-budget)
  - [Normalize Raw Input Sources](#normalize-raw-input-sources)
  - [Compute Raw Input Chunk Ranges](#compute-raw-input-chunk-ranges)
  - [Write Raw Input Package](#write-raw-input-package)
- [4. States (CDSL)](#4-states-cdsl)
  - [Raw Input Package Lifecycle](#raw-input-package-lifecycle)
  - [Plan Lifecycle](#plan-lifecycle)
  - [Phase Lifecycle](#phase-lifecycle)
- [5. Definitions of Done](#5-definitions-of-done)
  - [Raw Input Package](#raw-input-package)
  - [Plan Workflow](#plan-workflow)
  - [Phase File Template](#phase-file-template)
  - [Decomposition Strategies](#decomposition-strategies)
  - [Plan Storage](#plan-storage)
  - [Plan Export Contract](#plan-export-contract)
- [6. Acceptance Criteria](#6-acceptance-criteria)

<!-- /toc -->

- [ ] `p1` - **ID**: `cpt-cypilot-featstatus-execution-plans`
## 1. Feature Context

- [ ] `p1` - `cpt-cypilot-feature-execution-plans`

### 1.1 Overview

Execution Plans decompose large agent tasks (artifact generation, validation, code implementation) into self-contained phase files that fit within a single LLM context window. Each phase file is a compiled prompt — all rules, constraints, conventions, and context are pre-resolved and inlined so that any AI agent can execute it without Cypilot knowledge. Accepted delegated execution extends this model by allowing plan outputs to be exported into executor-specific grammars — beginning with ralphex Markdown plans under `docs/plans/` — while Cypilot remains authoritative for decomposition, phase compilation, and deterministic validation commands (see `cpt-cypilot-adr-ralphex-delegation-skill`).

### 1.2 Purpose

Context window overflow is the primary source of non-deterministic results in Cypilot workflows. A single generate or analyze invocation can load 3000+ lines of instructions (SKILL.md + execution-protocol.md + workflow + rules + template + checklist + example + constraints + project context) before the agent writes any output. This causes:

- **Attention drift**: different parts of instructions "win" attention on each run, producing inconsistent results
- **Partial completion**: agent runs out of context mid-task, requiring manual re-scoping
- **Manual decomposition**: users must figure out how to break tasks into manageable pieces

Execution Plans solve this by moving decomposition from the user to the tool. The plan workflow reads all relevant sources once, decomposes the task into phases, and "compiles" each phase into a focused instruction file (≤500 lines target, ≤1000 max) containing only what's needed for that specific sub-task.

**Requirements**: `cpt-cypilot-fr-core-workflows`, `cpt-cypilot-fr-core-execution-plans`

**Principles**: `cpt-cypilot-principle-determinism-first`, `cpt-cypilot-principle-occams-razor`

### 1.3 Actors

| Actor | Role in Feature |
|-------|-----------------|
| `cpt-cypilot-actor-user` | Invokes plan workflow, reviews generated phases, triggers phase execution, checks plan progress |
| `cpt-cypilot-actor-ai-agent` | Generates execution plans, compiles phase files, executes individual phases |

### 1.4 References

- **PRD**: [PRD.md](../PRD.md) — `cpt-cypilot-fr-core-workflows`, `cpt-cypilot-fr-core-execution-plans`
- **Design**: [DESIGN.md](../DESIGN.md) — `cpt-cypilot-component-agent-generator`
- **ADRs**: [ADR-0018](../ADR/0018-cpt-cypilot-adr-ralphex-delegation-skill-v1.md) — `cpt-cypilot-adr-ralphex-delegation-skill` (plan export contract)
- **Dependencies**: `cpt-cypilot-feature-agent-integration` (builds on generate/analyze workflows)

## 2. Actor Flows (CDSL)

### Generate Execution Plan

- [x] `p1` - **ID**: `cpt-cypilot-flow-execution-plans-generate-plan`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User requests a large task → agent produces a plan manifest + phase files in `.plans/` directory
- User requests plan for specific artifact → agent decomposes by template sections

**Error Scenarios**:
- Task is small enough for single context → agent skips plan, executes directly via generate/analyze
- Kit dependencies missing → agent reports missing deps and stops
- `.plans/` directory cannot be created → agent reports filesystem error

**Steps**:
1. [x] - `p1` - User requests task via plan workflow (e.g., "plan generate PRD", "plan analyze DESIGN") - `inst-user-request`
2. [x] - `p1` - Agent loads task context: identify task type (generate/analyze/implement), target artifact kind, and kit - `inst-load-context`
3. [x] - `p1` - Agent loads all kit dependencies for target kind: template, rules, checklist, example, constraints - `inst-load-deps`
4. [x] - `p1` - Agent runs decomposition algorithm `cpt-cypilot-algo-execution-plans-decompose` to split task into phases - `inst-decompose`
5. [x] - `p1` - Agent creates `.plans/` directory in `{cypilot_path}` if not exists - `inst-create-dir`
6. [ ] - `p1` - **IF** `.plans/` not in `.gitignore` → agent adds it - `inst-gitignore`  *(not implemented — only `.archive/` is gitignored)*
7. [x] - `p1` - Agent creates plan directory: `{cypilot_path}/.plans/{task-slug}/` - `inst-create-plan-dir`
8. [x] - `p1` - **FOR EACH** phase in decomposition result - `inst-loop-phases`
   1. [x] - `p1` - Agent runs compile algorithm `cpt-cypilot-algo-execution-plans-compile-phase` to produce phase file content - `inst-compile`
   2. [x] - `p1` - Agent runs budget enforcement `cpt-cypilot-algo-execution-plans-enforce-budget` on compiled content - `inst-budget`
   3. [x] - `p1` - Agent writes phase file: `phase-{NN}-{slug}.md` - `inst-write-phase`
9. [x] - `p1` - Agent writes plan manifest: `plan.toml` with all phase metadata - `inst-write-manifest`
10. [x] - `p1` - Agent reports plan summary: total phases, estimated lines per phase, execution order - `inst-report`

### Chunk Raw Input Package

- [x] `p1` - **ID**: `cpt-cypilot-flow-execution-plans-chunk-raw-input`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User or planner invokes `cpt chunk-input ... --output-dir ...` → command emits deterministic `input/*.md` chunk files and JSON metadata
- User combines file inputs with direct prompt text via `--include-stdin` → raw prompt is preserved as `direct-prompt.md` and included in chunk metadata
- Planner encounters an existing `input/manifest.json` whose `input_signature` matches the current raw input → package is safely reused without re-chunking

**Error Scenarios**:
- Input file is missing or unreadable → command returns JSON `ERROR`
- `stdin` is required but empty → command returns JSON `ERROR`
- Output directory cannot be written → command returns JSON `ERROR`

**Steps**:
1. [x] - `p1` - User or planner invokes `cpt chunk-input [<path> ...] --output-dir <path> [--include-stdin]` - `inst-user-chunk-input`
2. [x] - `p1` - Command parses arguments and validates required numeric thresholds - `inst-parse-args`
3. [x] - `p1` - Command reads file sources and optional `stdin` according to invocation mode - `inst-read-sources`
4. [x] - `p1` - Command computes total line count, canonical `input_signature`, and whether planning is required - `inst-evaluate-threshold`
5. [x] - `p1` - **IF** `--dry-run` is set → command skips staging, writing, and atomic swap; instead returns the deterministic `input_signature` and a planned manifest (including chunk metadata, source records, and whether `direct-prompt.md` would be preserved) without persisting any files; callers use this for signature-based reuse checks - `inst-dry-run`
6. [x] - `p1` - Command stages a complete replacement package in a temporary sibling directory instead of deleting the active package first - `inst-prepare-output`
7. [x] - `p1` - **IF** `stdin` participated → command preserves raw direct prompt as `direct-prompt.md` inside the staged package - `inst-store-direct-prompt`
8. [x] - `p1` - Command writes deterministic numbered chunk files bounded by `max_lines` and `manifest.json` carrying `input_signature` and chunk metadata - `inst-write-chunks`
9. [x] - `p1` - Command atomically swaps the staged package into place; on write failure, the previously active package remains intact - `inst-return-result`

### Execute Phase

- [x] `p1` - **ID**: `cpt-cypilot-flow-execution-plans-execute-phase`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User asks to execute next phase → agent reads phase file, follows instructions, produces output
- All acceptance criteria pass → phase marked done in manifest

**Error Scenarios**:
- Phase depends on incomplete phase → agent reports dependency and stops
- Acceptance criteria fail → phase marked failed, agent reports specifics
- Phase file missing or corrupted → agent reports error

**Steps**:
1. [x] - `p1` - User requests phase execution (next phase or specific phase number) - `inst-user-exec`
2. [x] - `p1` - Agent reads `plan.toml` manifest to determine target phase - `inst-read-manifest`
3. [x] - `p1` - **IF** target phase has unmet dependencies → **RETURN** error with dependency list - `inst-check-deps`
4. [x] - `p1` - Agent updates phase status to `in_progress` in manifest - `inst-update-status-start`
5. [x] - `p1` - Agent reads phase file content (self-contained instructions) - `inst-read-phase`
6. [x] - `p1` - Agent follows phase instructions exactly (the phase file contains ALL needed context) - `inst-execute`
7. [x] - `p1` - Agent self-checks against acceptance criteria in phase file - `inst-self-check`
8. [x] - `p1` - **IF** all acceptance criteria pass - `inst-check-pass`
   1. [x] - `p1` - Agent updates phase status to `done` in manifest - `inst-mark-done`
   2. [x] - `p1` - Agent reports phase completion and next phase - `inst-report-done`
9. [x] - `p1` - **ELSE** - `inst-check-fail`
   1. [x] - `p1` - Agent updates phase status to `failed` in manifest with details - `inst-mark-failed`
   2. [x] - `p1` - Agent reports failed criteria - `inst-report-failed`

### Check Plan Status

- [x] `p2` - **ID**: `cpt-cypilot-flow-execution-plans-check-status`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User asks for plan status → agent reads manifest and reports phase progress

**Error Scenarios**:
- No active plan found → agent reports no plan

**Steps**:
1. [x] - `p2` - User requests plan status - `inst-user-status`
2. [x] - `p2` - Agent reads `plan.toml` manifest - `inst-read-manifest-status`
3. [x] - `p2` - Agent reports: plan name, total phases, completed/pending/failed counts, next actionable phase - `inst-report-status`

## 3. Processes / Business Logic (CDSL)

### Decompose Task

- [x] `p1` - **ID**: `cpt-cypilot-algo-execution-plans-decompose`

**Input**: Task type (generate/analyze/implement), target artifact kind, kit dependencies (template, checklist, rules)

**Output**: Ordered list of phases, each with: title, scope description, relevant template sections, relevant checklist items, relevant rules subset, dependency list

**Steps**:
1. [x] - `p1` - Determine decomposition strategy based on task type - `inst-determine-strategy`
2. [x] - `p1` - **IF** task type is `generate` (artifact creation) - `inst-strategy-generate`
   1. [x] - `p1` - Parse template into logical section groups (2-4 sections per phase) - `inst-parse-template`
   2. [x] - `p1` - Assign each section group to a phase in template order - `inst-assign-sections`
   3. [x] - `p1` - For each phase, extract only the rules applicable to its sections - `inst-extract-rules`
   4. [x] - `p1` - For each phase, extract only the checklist items applicable to its sections - `inst-extract-checklist`
3. [x] - `p1` - **IF** task type is `analyze` (validation/review) - `inst-strategy-analyze`
   1. [x] - `p1` - Parse checklist into category groups (structural, semantic, cross-reference, traceability) - `inst-parse-checklist`
   2. [x] - `p1` - Assign each category group to a phase - `inst-assign-categories`
   3. [x] - `p1` - Add synthesis phase at end (aggregate results, final verdict) - `inst-add-synthesis`
4. [x] - `p1` - **IF** task type is `implement` (code from FEATURE) - `inst-strategy-implement`
   1. [x] - `p1` - Parse FEATURE CDSL blocks (flows, algorithms, states) - `inst-parse-cdsl`
   2. [x] - `p1` - Assign each CDSL block + its tests to a phase - `inst-assign-cdsl`
   3. [x] - `p1` - Order phases by CDSL dependency graph - `inst-order-by-deps`
5. [x] - `p1` - Set phase dependencies: each phase depends on all prior phases that produce content it references - `inst-set-deps`
6. [x] - `p1` - **RETURN** ordered phase list with metadata - `inst-return-phases`

### Compile Phase File

- [x] `p1` - **ID**: `cpt-cypilot-algo-execution-plans-compile-phase`

**Input**: Phase metadata (from decompose), full kit dependencies, project context

**Output**: Self-contained phase file content (markdown) following `plan-template.md` structure

**Steps**:
1. [x] - `p1` - Generate TOML frontmatter: plan ID, phase number, total, type, status, dependencies, input/output paths - `inst-gen-frontmatter`
2. [x] - `p1` - Write "What" section: 2-3 sentences describing this phase's scope and its place in the plan - `inst-write-what`
3. [x] - `p1` - Write "Prior Context" section: summary of what previous phases produced (or "First phase" if phase 1) - `inst-write-prior`
4. [x] - `p1` - Write "Rules" section: inline ONLY rules applicable to THIS phase's scope - `inst-write-rules`
   1. [x] - `p1` - Extract structural rules relevant to phase's template sections - `inst-extract-structural`
   2. [x] - `p1` - Extract content rules relevant to phase's scope - `inst-extract-content`
   3. [x] - `p1` - Extract quality rules (always included, condensed) - `inst-extract-quality`
5. [x] - `p1` - Write "Input" section: pre-resolve all file paths, inline project context needed for this phase - `inst-write-input`
6. [x] - `p1` - Write "Task" section: numbered step-by-step instructions specific to this phase - `inst-write-task`
7. [x] - `p1` - Write "Acceptance Criteria" section: binary pass/fail checklist for this phase - `inst-write-criteria`
8. [x] - `p1` - Write "Output Format" section: exact expected output format and completion report template - `inst-write-output`
9. [x] - `p1` - Resolve ALL template variables (`{variable}` → absolute paths) in the compiled content - `inst-resolve-vars`
10. [x] - `p1` - **RETURN** compiled phase file content - `inst-return-compiled`

### Enforce Line Budget

- [x] `p1` - **ID**: `cpt-cypilot-algo-execution-plans-enforce-budget`

**Input**: Compiled phase file content, target budget (500 lines), maximum budget (1000 lines)

**Output**: Budget-compliant phase file content, or split recommendation

**Steps**:
1. [x] - `p1` - Count lines in compiled content - `inst-count-lines`
2. [x] - `p1` - **IF** lines ≤ target budget (500) → **RETURN** content as-is - `inst-under-target`
3. [x] - `p1` - **IF** lines > target but ≤ maximum (1000) - `inst-over-target`
   1. [x] - `p1` - ~~Trim rules section: remove rules not directly applicable to phase scope~~ — **SUPERSEDED** by "Kit Rules Are Law" constraint: rules are NEVER trimmed, phases are split instead - `inst-trim-rules`
   2. [x] - `p1` - ~~Condense quality rules to bullet points~~ — **SUPERSEDED** by "Kit Rules Are Law" constraint - `inst-condense-quality`
   3. [x] - `p1` - **IF** still > target → accept (within maximum budget) - `inst-accept-over`
4. [x] - `p1` - **IF** lines > maximum (1000) - `inst-over-max`
   1. [x] - `p1` - **RETURN** split recommendation: suggest splitting this phase into N sub-phases with proposed scope boundaries - `inst-recommend-split`

### Normalize Raw Input Sources

- [x] `p1` - **ID**: `cpt-cypilot-algo-execution-plans-chunk-normalize-input`

**Input**: CLI paths, `stdin`, `stdin_label`

**Output**: Ordered normalized raw-input sources with labels, display names, paths, text, and line counts

**Steps**:
1. [x] - `p1` - Normalize newline style for every input source before counting or chunking - `inst-normalize-newlines`
2. [x] - `p1` - Derive stable source labels from file stems or the supplied `stdin` label - `inst-slugify-source`
3. [x] - `p1` - Resolve file paths, read file contents as UTF-8, and reject missing inputs - `inst-read-file-source`
4. [x] - `p1` - Read `stdin` only when no file paths were provided or when `--include-stdin` explicitly requests mixed input - `inst-read-stdin-source`
5. [x] - `p1` - **RETURN** normalized sources in deterministic order with `kind`, `display_name`, `path`, `text`, and `line_count` - `inst-return-sources`

### Compute Raw Input Chunk Ranges

- [x] `p1` - **ID**: `cpt-cypilot-algo-execution-plans-chunk-ranges`

**Input**: `total_lines`, `max_lines`

**Output**: Ordered inclusive `(start_line, end_line)` ranges for one source

**Steps**:
1. [x] - `p1` - **IF** the source has zero effective lines → return a single empty range `(1, 0)` - `inst-empty-range`
2. [x] - `p1` - Iterate from line 1 in windows of size `max_lines` - `inst-range-loop`
3. [x] - `p1` - Cap each chunk end line at `total_lines` - `inst-range-cap`
4. [x] - `p1` - **RETURN** ordered inclusive chunk ranges - `inst-return-ranges`

### Write Raw Input Package

- [x] `p1` - **ID**: `cpt-cypilot-algo-execution-plans-chunk-write`

**Input**: Normalized sources, output directory, `max_lines`

**Output**: Written raw-input package files plus ordered chunk metadata

**Steps**:
1. [x] - `p1` - Create the parent directory if it does not already exist and allocate a temporary staging directory beside the target package - `inst-create-output-dir`
2. [x] - `p1` - **IF** a `stdin` source exists → write `direct-prompt.md` into the staged package and record its stored file - `inst-write-direct-prompt`
3. [x] - `p1` - Compute chunk ranges per source and render chunk text with normalized trailing newline handling - `inst-build-chunk-text`
4. [x] - `p1` - Write deterministic filenames `NNN-SS-label-part-PP.md` and collect per-chunk metadata - `inst-write-chunk-file`
5. [x] - `p1` - Write `manifest.json` with `input_signature`, source metadata, and chunk metadata for authoritative package reuse checks - `inst-write-package-manifest`
6. [x] - `p1` - Replace the live package only after the staged package is fully written; restore the previous package on `OSError` - `inst-return-chunks`

## 4. States (CDSL)

### Raw Input Package Lifecycle

- [x] `p1` - **ID**: `cpt-cypilot-state-execution-plans-raw-input-package`

**States**: absent, materialized, reused, failed

**Initial State**: absent

**Transitions**:
1. [x] - `p1` - **FROM** absent **TO** materialized **WHEN** `chunk-input` writes a new raw-input package successfully - `inst-package-materialized`
2. [x] - `p1` - **FROM** materialized **TO** materialized **WHEN** `chunk-input` re-runs in place after cleaning stale generated outputs - `inst-package-rewritten`
3. [x] - `p1` - **FROM** materialized **TO** reused **WHEN** the planner detects and reuses an existing authoritative raw-input package - `inst-package-reused`
4. [x] - `p1` - **FROM** absent **TO** failed **WHEN** source loading or package writing fails - `inst-package-failed`

### Plan Lifecycle

- [x] `p1` - **ID**: `cpt-cypilot-state-execution-plans-plan-lifecycle`

**States**: pending, in_progress, done, failed

**Initial State**: pending

**Transitions**:
1. [x] - `p1` - **FROM** pending **TO** in_progress **WHEN** first phase execution starts - `inst-plan-start`
2. [x] - `p1` - **FROM** in_progress **TO** done **WHEN** all phases are done - `inst-plan-done`
3. [x] - `p1` - **FROM** in_progress **TO** failed **WHEN** any phase fails and user does not retry - `inst-plan-failed`

### Phase Lifecycle

- [x] `p1` - **ID**: `cpt-cypilot-state-execution-plans-phase-lifecycle`

**States**: pending, in_progress, done, failed

**Initial State**: pending

**Transitions**:
1. [x] - `p1` - **FROM** pending **TO** in_progress **WHEN** agent begins executing phase - `inst-phase-start`
2. [x] - `p1` - **FROM** in_progress **TO** done **WHEN** all acceptance criteria pass - `inst-phase-done`
3. [x] - `p1` - **FROM** in_progress **TO** failed **WHEN** acceptance criteria fail - `inst-phase-failed`
4. [x] - `p1` - **FROM** failed **TO** in_progress **WHEN** user retries phase - `inst-phase-retry`

## 5. Definitions of Done

### Raw Input Package

- [x] `p1` - **ID**: `cpt-cypilot-dod-execution-plans-raw-input`

The system MUST provide a `chunk-input` command that takes file paths and/or `stdin` input and emits a deterministic raw-input package in the output directory. The package MUST contain:
- `manifest.json` with `input_signature`, source metadata, and ordered chunk metadata
- `direct-prompt.md` (if `stdin` was used)
- `NNN-SS-label-part-PP.md` chunk files (where `NNN` is the chunk number, `SS` is the source sequence number (zero-padded index), `label` is the slugified source label (lowercase, ASCII-safe, spaces and special characters replaced with hyphens or underscores to ensure deterministic, filesystem-safe filenames), and `PP` is the part number)

Package reuse MUST depend on an exact `input_signature` match, not only on plan target identity or directory existence. Re-running the command with changed raw input MUST preserve the previous live package unless the replacement package is fully written and successfully swapped into place.

**Implements**:
- `cpt-cypilot-flow-execution-plans-chunk-raw-input`
- `cpt-cypilot-algo-execution-plans-chunk-normalize-input`
- `cpt-cypilot-algo-execution-plans-chunk-ranges`
- `cpt-cypilot-algo-execution-plans-chunk-write`

**Constraints**: `cpt-cypilot-constraint-markdown-contract`

**Touches**:
- Directory: `{cypilot_path}/.plans/{task-slug}/input/` (new, contains raw-input package)

### Plan Workflow

- [x] `p1` - **ID**: `cpt-cypilot-dod-execution-plans-workflow`

The system MUST provide a `plan.md` workflow file that instructs AI agents how to decompose tasks into phases and generate self-contained phase files. The workflow MUST follow the same structure as existing `generate.md` and `analyze.md` workflows.

**Implements**:
- `cpt-cypilot-flow-execution-plans-generate-plan`
- `cpt-cypilot-flow-execution-plans-execute-phase`
- `cpt-cypilot-flow-execution-plans-check-status`

**Constraints**: `cpt-cypilot-constraint-markdown-contract`

**Touches**:
- File: `workflows/plan.md` (new)
- File: `{cypilot_path}/.core/workflows/plan.md` (synced copy)

### Phase File Template

- [x] `p1` - **ID**: `cpt-cypilot-dod-execution-plans-template`

The system MUST provide a `plan-template.md` requirement file that defines the strict structure for generated phase files. The template MUST enforce:
- TOML frontmatter with plan/phase metadata
- Self-contained preamble ("Any AI agent can execute this file")
- Sections: What, Prior Context, Rules (inlined), Input (pre-resolved), Task (step-by-step), Acceptance Criteria (binary), Output Format
- No unresolved template variables
- No external file references that require Cypilot knowledge

**Implements**:
- `cpt-cypilot-algo-execution-plans-compile-phase`

**Constraints**: `cpt-cypilot-constraint-markdown-contract`

**Touches**:
- File: `requirements/plan-template.md` (new)
- File: `{cypilot_path}/.core/requirements/plan-template.md` (synced copy)

### Decomposition Strategies

- [x] `p1` - **ID**: `cpt-cypilot-dod-execution-plans-decomposition`

The system MUST provide a `plan-decomposition.md` requirement file that defines decomposition strategies for each task type:
- **Generate**: split by template section groups (2-4 sections per phase)
- **Analyze**: split by checklist category groups (structural → semantic → cross-ref → traceability → synthesis)
- **Implement**: split by CDSL blocks (each flow/algorithm/state + its tests = 1 phase)

The file MUST include budget enforcement rules (500-line target, 1000-line max) and phase dependency resolution.

**Implements**:
- `cpt-cypilot-algo-execution-plans-decompose`
- `cpt-cypilot-algo-execution-plans-enforce-budget`

**Constraints**: `cpt-cypilot-constraint-markdown-contract`

**Touches**:
- File: `requirements/plan-decomposition.md` (new)
- File: `{cypilot_path}/.core/requirements/plan-decomposition.md` (synced copy)

### Plan Storage

- [x] `p1` - **ID**: `cpt-cypilot-dod-execution-plans-storage`

The system MUST store execution plans in `{cypilot_path}/.plans/{task-slug}/` directory. The directory MUST be added to `.gitignore` automatically on first use. Each plan directory contains:
- `plan.toml` — manifest with phase metadata and status tracking
- `input/` — authoritative raw-input package when oversized workflow input was materialized (`manifest.json`, optional `direct-prompt.md`, plus numbered chunk files)
- `phase-{NN}-{slug}.md` — self-contained phase files

**Implements**:
- `cpt-cypilot-flow-execution-plans-chunk-raw-input`
- `cpt-cypilot-flow-execution-plans-generate-plan`
- `cpt-cypilot-state-execution-plans-raw-input-package`
- `cpt-cypilot-state-execution-plans-plan-lifecycle`
- `cpt-cypilot-state-execution-plans-phase-lifecycle`

**Touches**:
- Directory: `{cypilot_path}/.plans/` (new, git-ignored)

### Plan Export Contract

- [ ] `p1` - **ID**: `cpt-cypilot-dod-execution-plans-export`

The system MUST support exporting Cypilot plan outputs into executor-specific grammars for delegated execution. The initial target grammar is ralphex Markdown plans.

**Export rules**:
- One Cypilot execution plan exports to one ralphex plan file under the ralphex-resolved `plans_dir` (default `docs/plans/`; resolved from ralphex config precedence, not Cypilot-owned)
- One Cypilot phase maps to one `### Task N:` block or a small contiguous task group inside the exported plan
- Cypilot phase instructions, task steps, and acceptance criteria are flattened into ralphex-compatible checkboxes and validation commands
- Exported plans MUST contain a `## Validation Commands` section derived from Cypilot's deterministic validation contract
- `{cypilot_path}/.plans/{task}/out/` remains the stable interchange point for intermediate outputs consumed by later export passes
- Exported plans are derived artifacts compiled from canonical Cypilot sources — they are not a second SDLC source of truth
- Export MUST NOT copy the entire SDLC kit into the executor plan; only the bounded slices needed for the delegated task are included

This feature owns the canonical plan structure and export contract definition. Concrete delegated export (compilation into ralphex grammar, `.ralphex/` overrides, CLI invocation) is implemented by `cpt-cypilot-feature-ralphex-delegation` — specifically `cpt-cypilot-algo-ralphex-delegation-compile-plan` and `cpt-cypilot-algo-ralphex-delegation-map-phase`.

**Constraints**: `cpt-cypilot-constraint-markdown-contract`

**Touches**:
- Directory: `{plans_dir}/` (exported ralphex-compatible plans, written by ralphex-delegation feature; path resolved from ralphex config, default `docs/plans/`)
- Directory: `{cypilot_path}/.plans/{task}/out/` (intermediate interchange outputs)

## 6. Acceptance Criteria

- [x] Plan workflow file (`workflows/plan.md`) exists and follows workflow structure conventions
- [x] Phase template file (`requirements/plan-template.md`) exists with all required sections
- [x] Decomposition strategies file (`requirements/plan-decomposition.md`) exists with strategies for generate/analyze/implement
- [x] Generated phase files are self-contained: zero unresolved `{variable}` references, zero "open file X" instructions
- [x] Generated phase files respect line budget: ≤500 lines target, ≤1000 lines maximum
- [x] Phase files can be executed by any AI agent without Cypilot context or tools
- [x] Plan manifest (`plan.toml`) correctly tracks phase status across executions
- [x] Oversized workflow input can be materialized into deterministic `input/*.md` chunk files with `direct-prompt.md` preservation and stale-output cleanup
- [ ] `.plans/` directory is automatically git-ignored *(only `.archive/` is currently gitignored)*
- [ ] Cypilot plan outputs can be exported into ralphex-compatible Markdown plan files under the ralphex-resolved `plans_dir`
- [ ] Exported plans contain `## Validation Commands` and `### Task N:` sections matching ralphex grammar
- [ ] Phase-to-task mapping flattens Cypilot acceptance criteria into ralphex checkboxes
