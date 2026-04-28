---
cypilot: true
type: workflow
name: cypilot-plan
description: Decompose large tasks into self-contained phase files
version: 1.0
purpose: Universal workflow for generating execution plans with phased delivery
---

# Plan


<!-- toc -->

- [Overview](#overview)
- [Context Budget & Overflow Prevention (CRITICAL)](#context-budget--overflow-prevention-critical)
- [Phase 0: Resolve Variables & Discover Tools](#phase-0-resolve-variables--discover-tools)
- [Phase 1: Assess Scope](#phase-1-assess-scope)
- [Phase 2: Decompose](#phase-2-decompose)
- [Phase 3: Compile Phase Files](#phase-3-compile-phase-files)
- [Phase 4: Finalize Plan](#phase-4-finalize-plan)
- [Appendix A: Execute Phases (Reference Only)](#appendix-a-execute-phases-reference-only)
- [Appendix B: Check Status (Reference Only)](#appendix-b-check-status-reference-only)
- [Plan Storage Format](#plan-storage-format)
- [Execution Log](#execution-log)

<!-- /toc -->

> **⛔ CRITICAL CONSTRAINT**: This workflow ONLY generates execution plans and related handoff artifacts. It NEVER executes the underlying task (generate, analyze, implement) directly. Even if the task seems small, this workflow's job is to produce phase files — not to do the work itself. If the task is small enough for direct execution, tell the user to use `/cypilot-generate` or `/cypilot-analyze` instead. The reference appendices below define the runtime contract that generated plans MUST support; they are not steps performed by this workflow.
> **⛔ CRITICAL CONSTRAINT — COMPLETE COVERAGE, COMPACT LOADING**: Before generating ANY plan, you MUST discover and process ALL navigation rules (`ALWAYS open`, `OPEN and follow`, `ALWAYS open and follow`) from the **target workflow** (generate.md, analyze.md, or the relevant workflow). Every applicable file referenced by those directives MUST be opened at least once, but you MUST retain only the specific sections/ranges needed for decomposition, interaction extraction, and compilation. Completeness is proven by a loaded-file manifest with paths and sections/ranges, not by keeping every dependency fully resident in context. Skipping ANY navigation rule still produces incomplete context and broken plans. This is the #1 source of plan quality failures.
> **⛔ CRITICAL CONSTRAINT — KIT RULES ARE LAW** *(highest priority)*: Every rule in the kit's `rules.md` for the target artifact kind MUST be enforced in the generated plan — **completely, without omission or summarization**. Rules are inlined verbatim into phase files. If the full rules don't fit in a single phase, split the phase so each sub-phase gets ALL rules relevant to its scope — but NEVER trim, summarize, or selectively skip rules to fit a budget. The `checklist.md` items are equally mandatory for analyze tasks. A plan that drops kit rules produces artifacts that fail validation.
> **⛔ CRITICAL CONSTRAINT — DETERMINISTIC FIRST**: Every phase step that CAN be done by a deterministic tool (cpt command, script, shell command) MUST use that tool instead of LLM reasoning. Discover available tools dynamically in Phase 0 — do NOT assume a fixed set of commands. Tool capabilities change between versions. The CLISPEC file is the source of truth for what commands exist and what they can do.
> **⛔ CRITICAL CONSTRAINT — INTERACTIVE QUESTIONS COMPLETENESS** *(mandatory)*: You MUST find ALL interactive questions, user input requests, confirmation gates, review requests, and decision points from: (1) the target workflow, (2) `rules.md` for the target artifact kind, (3) `checklist.md`, (4) `template.md`, AND (5) **every file referenced by navigation rules** (`ALWAYS open`, `OPEN and follow`) in those files — recursively. Every interaction point found MUST appear in the compiled plan: pre-resolvable questions asked BEFORE plan generation, phase-bound questions embedded in phase files. Inspect every applicable dependency, record the source path plus section/range for each interaction point, and carry forward only the extracted interaction data needed by later phases. **Missing even ONE interaction point = plan is INVALID.** See `{cypilot_path}/.core/requirements/plan-checklist.md` Section 2 for the complete extraction procedure.
> **⛔ CRITICAL CONSTRAINT — BRIEF BEFORE COMPILE**: Phase files MUST NOT be written directly. Every phase file MUST be compiled from a corresponding compilation brief (`brief-{NN}-{slug}.md`) that was written to disk in Phase 3.2. The brief is the contract between decomposition (what to include) and compilation (how to assemble). Skipping briefs produces phase files that silently omit kit content, miss load instructions, or inline wrong sections. **If you find yourself writing a phase file without first reading its brief from disk — STOP, you are violating the workflow.** Write the brief first, write it to disk, THEN compile from it. A phase file without a corresponding brief file on disk = INVALID plan.

ALWAYS open and follow `{cypilot_path}/.core/skills/cypilot/SKILL.md` FIRST WHEN {cypilot_mode} is `off`

**Type**: Operation

ALWAYS open and follow `{cypilot_path}/.core/requirements/execution-protocol.md` FIRST

ALWAYS open and follow `{cypilot_path}/.core/requirements/plan-template.md` WHEN compiling phase files

ALWAYS open and follow `{cypilot_path}/.core/requirements/plan-decomposition.md` WHEN decomposing tasks into phases

OPEN and follow `{cypilot_path}/.core/requirements/prompt-engineering.md` WHEN compiling phase files (phase files ARE agent instructions)

OPEN and follow `{cypilot_path}/.core/requirements/plan-checklist.md` WHEN validating plans (Phase 4.1 self-validation or /cypilot-analyze on plan)

For context compaction recovery during multi-phase workflows, follow `{cypilot_path}/.core/requirements/execution-protocol.md` Section "Compaction Recovery".

## Overview

This workflow generates execution plans, not direct results. Use it when work exceeds a single-context window, requires a long checklist, or involves multi-block implementation. Do **not** use it for small edits, direct execution, or work that fits in ~500 compiled lines. Output: `plan.toml` + `N` phase files in `{cypilot_path}/.plans/{task-slug}/`.

## Context Budget & Overflow Prevention (CRITICAL)

- Open every applicable dependency file to inspect required sections, but do NOT retain full file bodies once the needed slices are extracted.
- Do NOT load all kit dependencies at once; load incrementally per phase.
- Do NOT hold all phase files in context simultaneously; compile and write one at a time.
- If a phase compilation would exceed current context budget, checkpoint and use Compaction Recovery.
- The plan manifest (`plan.toml`) is the recovery checkpoint and MUST be written before compilation.
- If the raw task input itself exceeds `500` lines, materialize it under `{cypilot_path}/.plans/{task-slug}/input/`, chunk it to `<= 300` lines per file, and treat the resulting chunk files as the authoritative raw-input package for the plan. When the source includes direct prompt text, preserve that raw prompt as `input/direct-prompt.md` before chunking. (See `{cypilot_path}/.core/requirements/raw-input-overflow.md` for the shared overflow rule.)

Budget targets: Phase 0-1 `~200` lines, Phase 2 `~300`, Phase 3 `~500` per phase file, Phase 4 `~50`. The reference appendices below are runtime guidance only and do not consume plan-generation budget unless the user explicitly asks about execution behavior.

## Phase 0: Resolve Variables & Discover Tools

Run `EXECUTE: {cpt_cmd} --json info`; store `{cypilot_path}`, `{project_root}`, and the returned `variables` dict for later path resolution.

Variable checkpoint: after resolving `{cpt_cmd}`, `{cypilot_path}`, and `{project_root}`, carry them forward to Phase 3.1, where they MUST be written into the `[meta]` TOML table at the top of `plan.toml` so they survive context compaction and the runtime can read them on resume. On context loss or new-chat resume, parse `plan.toml`'s `[meta]` table first, then re-run `cpt --json info` to verify (or refresh) the resolved values before any path-dependent step.

### 0.1 Discover Available Tools

Read `READ: {cypilot_path}/.core/skills/cypilot/cypilot.clispec` and build a dynamic tool map from each `COMMAND` block as `{command_name} — {DESCRIPTION line} [outputs: {OUTPUT format}]`. Also inspect the resolved `variables` dict for script directories (for example `{scripts}` when present), scan each such directory for `*.py`, `*.sh` files, and add kit scripts with inferred purpose.

## Phase 1: Assess Scope

### 1.1 Identify Task Type

| Signal | Task Type | Target Workflow |
|--------|-----------|----------------|
| `create` / `generate` / `write` / `update` / `draft` + artifact kind | `generate` | `generate.md` |
| `validate` / `review` / `check` / `audit` / `analyze` + artifact kind | `analyze` | `analyze.md` |
| `implement` / `code` / `build` / `develop` + feature name | `implement` | `generate.md` (code mode) |

### 1.1b Extract Target Workflow Navigation Rules (CRITICAL)

Open `{cypilot_path}/.core/workflows/{target_workflow}` and: scan all navigation directives, list referenced files + `WHEN` conditions, evaluate them, open every applicable file, extract only the sections/ranges needed for plan generation, and record a loaded-file manifest with `path`, `reason`, `sections/ranges`, and `line_count`.

Report:
```text
Context loaded for plan generation:
  Workflow: {target_workflow} ({N} navigation rules processed)
  Files inspected: {M} files
  Loaded manifest: {path — sections/ranges — reason}
  Total retained context: ~{L} lines
  All navigation rules processed? [YES/NO]
```
**Gate**: do NOT proceed until ALL applicable navigation rules are processed, every required file referenced by navigation rules has been opened, and every retained slice needed for planning is captured in the manifest.

### 1.2 Estimate Compiled Size
  
  Estimate `template_lines + rules_lines + checklist_lines + existing_content_lines`.
  
1. If oversized raw input already has an approved or reusable plan package, remain on the plan path even when the compiled estimate is `≤ 500`.
2. Otherwise, if the estimate is `≤ 500`, continue to Phase 1.4 so `{task-slug}` can be resolved before checking for any existing authoritative raw-input package.
3. If the estimate is `> 500`, continue planning.

### 1.3 Scan for User Interaction Points (CRITICAL)
  
  > **⛔ MANDATORY**: Missing interaction points is the #2 source of plan failures after missing rules.

Recursively scan the target workflow, `rules.md`, `checklist.md`, `template.md`, and every applicable navigation-linked file for:

- `question`: `ask the user`, `ask user`, `what is`, `which`, trailing `?`
- `input`: `user provides`, `user specifies`, `user enters`, `input from user`
- `confirm`: `wait for`, `confirm`, `approval`, `before proceeding`
- `review`: `review`, `present for`, `show to user`, `user inspects`
- `decision`: `choose`, `select`, `option A or B`, `decide`

Collect findings, classify each as **Pre-resolvable**, **Phase-bound**, or **Cross-phase**, ask all pre-resolvable and cross-phase questions now, record answers in a `decisions` block, then verify:
```text
Interaction points scan complete:
  Files scanned: {N}
  Interaction points found: {M}
    - Pre-resolvable: {count}
    - Phase-bound: {count}
    - Cross-phase: {count}
  All source files scanned? [YES/NO]
  All interaction points classified? [YES/NO]
```
**Gate**: do NOT proceed if any source file was not scanned or any interaction point remains unclassified. If zero are found, report `No interaction points detected — task is fully autonomous` and omit User Decisions from phase files.

### 1.4 Identify Target
Resolve generate/analyze → artifact kind, file path, and kit; implement → FEATURE spec path and CDSL blocks. Also compute `plan.target_key`, the canonical target identity used for deterministic plan-directory naming and reuse:
- generate artifact target: prefer the single resolved output artifact path as `artifact-path:{absolute path}`; otherwise use `artifact:{artifact kind}:{explicit artifact name}`
- analyze path target: use `path:{absolute path}` for the primary file/directory target; analyze artifact target follows the generate artifact-target rule
- implement target: prefer `feature-path:{absolute FEATURE path}`; otherwise `feature-id:{FEATURE ID}`; otherwise `feature-title:{normalized FEATURE title}`
Also compute `plan.input_signature`, the canonical raw-input identity derived from the current direct prompt text plus every provided file path/content pair. The signature is derived exclusively from each source's kind, path, and content hash — presentation-only metadata such as stdin display labels are excluded so that relabeling does not break reuse. To obtain the signature without writing any files, run:
  `{cpt_cmd} --json chunk-input ... --output-dir {cypilot_path}/.plans/{task-slug}/input --dry-run`
  (add `--include-stdin` when direct prompt text must be included).
This signature is authoritative for raw-input package reuse; `plan.target_key` is not sufficient when the raw task input changes.
Then report:
```text
Plan scope:
  Type: {generate|analyze|implement}
  Target: {artifact kind or feature name}
  Target key: {canonical target identity}
  Input signature: {sha256 of direct prompt + provided file contents}
  Estimated size: ~{N} lines
```
After target identification, compute `{task-slug}` immediately for deterministic plan-directory naming and reuse.

If `{cypilot_path}/.plans/{task-slug}/input/manifest.json` already exists, read its `input_signature` and compare it to the `input_signature` returned by the `--dry-run` invocation above. If they match exactly, remain on the plan path and reuse that authoritative raw-input package even when the compiled estimate is `≤ 500`.

Otherwise, if the compiled estimate is `≤ 500` and oversized raw input does not already have an approved or reusable plan package, STOP and direct the user to `/cypilot-generate` or `/cypilot-analyze`.

If the direct prompt text plus all provided files exceeds `500` total lines and no authoritative raw-input package with the same `plan.input_signature` exists yet, present:
```text
Oversized raw input detected (~{N} lines total).
Preparing the plan will write chunk files under {cypilot_path}/.plans/{task-slug}/input/ by running:
  {cpt_cmd} --json chunk-input ... --output-dir {cypilot_path}/.plans/{task-slug}/input --max-lines 300 --threshold-lines 500
  Add --include-stdin when direct prompt text must be packaged together with provided files.
  The command also writes {cypilot_path}/.plans/{task-slug}/input/manifest.json with `input_signature` and only replaces the existing package after the full replacement package is staged successfully.
Proceed with raw-input materialization? [y/n]
Reply with `y` or `n`.
`y` → Suggested when you want full plan guarantees; materialize the raw-input package and continue planning from chunk files.
`n` → Stop here without writing the raw-input package.
```
Wait for explicit user confirmation before creating `{cypilot_path}/.plans/{task-slug}/input/` or executing `chunk-input` (without `--dry-run`). If the user approves (`y`), materialize the raw input there, record the emitted chunk paths plus `manifest.json`, and stop carrying the full raw input in active chat context once the package exists. If the user rejects (`n`), do not create any files or directories, report `Raw-input materialization declined — continue with direct workflow if you prefer reduced guarantees`, and stop. This is a valid completion state for `/cypilot-plan`.

## Phase 2: Decompose

Open and follow `{cypilot_path}/.core/requirements/plan-decomposition.md`.

Compilation is split to minimize context: write the manifest, write briefs, then compile one phase at a time.

### 2.1 Select Plan Lifecycle (before finalizing phases)

Ask how completed plans should be handled:
```text
Plan files are stored in {cypilot_path}/.plans/{task-slug}/.
How should completed plans be handled?
  [1] .gitignore — keep plan files in place and ensure .plans/ is gitignored
  [2] Cleanup phase — add a final Cleanup phase that removes compiled plan artifacts after delivery phases pass
  [3] Archive — move the plan directory to {cypilot_path}/.plans/.archive/
  [4] Manual — stop after execution and ask me what to do with the plan files
Reply with `1`, `2`, `3`, or `4`.
[1] Suggested default for most projects — keep plan files available locally and ensure `.plans/` stays gitignored.
[2] Remove compiled plan artifacts automatically after successful delivery.
[3] Keep the plan, but move it into the archive location after completion.
[4] Ask again at the end instead of choosing a lifecycle strategy now.
```
Record `lifecycle = "gitignore" | "cleanup" | "archive" | "manual"`. Lifecycle handling is deterministic and single-path:
- `gitignore`: planning-time repository hygiene. Ensure `.plans/` is gitignored before or immediately after the first plan file write. Set `plan.lifecycle_status = "done"` as soon as the ignore rule exists. No post-completion plan-file prompt is allowed.
- `cleanup`: reserve a final Cleanup phase now so `total_phases`, dependencies, briefs, and budget estimates are structurally correct before `plan.toml` is written. After all non-lifecycle phases are `done`, set `plan.lifecycle_status = "ready"`, execute the Cleanup phase, then set `plan.lifecycle_status = "done"` only if cleanup succeeds. If cleanup fails (file removal error, permission error, or unexpected state), set `plan.lifecycle_status = "failed"`, report the specific error and affected paths, and offer manual intervention: list the files that could not be removed and ask the user to remove them manually or retry. The Cleanup phase removes `brief-*`, `phase-*`, and `out/`; `plan.toml` remains as the terminal receipt. Those removed plan artifacts are intentional terminal lifecycle cleanup, not delivery regressions: later recovery/audit MUST treat them as exempt when `lifecycle = "cleanup"` and `plan.lifecycle_status = "done"`, and MUST NOT reopen delivery phases or replay Cleanup solely because those files are absent. No post-completion plan-file prompt is allowed.
- `archive`: after all phases are `done`, set `plan.lifecycle_status = "ready"`, move the plan directory to `{cypilot_path}/.plans/.archive/{task-slug}/`, then update `plan.active_plan_dir` and set `plan.lifecycle_status = "done"` in the moved manifest. If the archive move fails (target exists, permission error, or disk error), set `plan.lifecycle_status = "failed"`, report the specific error and source path, and offer manual intervention: ask the user to move the directory manually or choose a different lifecycle strategy. No post-completion plan-file prompt is allowed.
- `manual`: do nothing automatically. After all phases are `done`, set `plan.lifecycle_status = "manual_action_required"` and present exactly one keep/archive/delete choice. This is the only strategy that allows a post-completion plan-file decision prompt.

Select a strategy based on task type:
- **generate**: load the target template, list H2 sections, group them into phases of `2-4` sections, and record phase boundaries.
- **analyze**: load the target checklist, list checklist categories, group them by validation pipeline order (structural → semantic → cross-ref → traceability → synthesis), and record phase boundaries.
- **implement**: load the FEATURE spec, list CDSL blocks, assign one block + tests per phase, add scaffolding and final integration phases, and record boundaries.

Output a phase list containing phase number and title, covered sections / categories / blocks, dependencies, `input_files`, `output_files`, assigned interaction points, and intermediate results needed by later phases. If `lifecycle = cleanup`, append the reserved final Cleanup phase after all delivery phases and make it depend on the last non-cleanup phase.

When an `input/manifest.json` package exists and its `input_signature` matches `plan.input_signature`, assign the relevant `input/*.md` chunk files into `input_files` for the phases that need them. If the full raw-input package would overflow one phase, add dedicated ingestion or consolidation phases instead of attaching every chunk everywhere.

### Intermediate Results Analysis

 Identify data flow between phases: incremental artifact output, extracted data, analysis notes, generated IDs, and decision logs.

 Rules: if any later phase needs a phase result, save it to `{cypilot_path}/.plans/{task-slug}/out/{filename}`; if only the final artifact depends on it, write directly to the project path; if the final phase assembles prior outputs, list ALL required `inputs`; use names like `out/phase-{NN}-{what}.md`.

### Review Phases

If the source workflow requires review before writing, add review gates inside the relevant phase: the Output Format must present content for inspection and the Acceptance Criteria must include user approval. If the source requires a major consolidated review, add a dedicated Review phase that loads prior outputs, asks the required review questions, and blocks further progress until approved.

### Execution Context Prediction

For each phase, estimate `phase_file_lines + sum(input_files lines) + sum(inputs lines) + estimated_output_lines`. Flags: `> 2000` = OVERFLOW → MUST split further; `1501-2000` = WARNING. Budget is `2000` lines max per phase. Re-split overflow phases until all are within budget, then report:
```text
Decomposition ({strategy} strategy):
  Phase 1: {title} — ~{N} lines (phase: {P}, runtime: {R}) 
  Phase 2: {title} — ~{N} lines (phase: {P}, runtime: {R}) 
  Phase 3: {title} — ~{N} lines (phase: {P}, runtime: {R}) 
  ...
  Phase N: {title} — ~{N} lines (phase: {P}, runtime: {R}) 
  
  Total phases: {N}
  Overflow phases: 0
  Budget: 2000 lines max per phase
  
  Proceed with manifest + brief generation after any required raw-input materialization? [y/n]
Reply with `y` or `n`.
`y` → Suggested when the decomposition looks correct; write `plan.toml` and the compilation briefs.
`n` → Stop before writing the manifest and briefs.
```
Wait for user confirmation before proceeding.

Include plan raw-input chunks from `input/` in `sum(input_files lines)` exactly as they will be read at runtime; do NOT hide them inside vague estimates.

## Phase 3: Compile Phase Files

Open and follow `{cypilot_path}/.core/requirements/plan-template.md`.

Phase 3 is split to minimize context: write the manifest, write briefs, then stop for an explicit user choice about how phase files should be produced.

The manifest and all `brief-*` files are mandatory outputs of `/cypilot-plan`. After they are on disk, the workflow MUST pause and ask whether to continue with inline phase generation, per-brief phase-generation prompts, or `cypilot-phase-compiler` subagents.

### 3.1 Write Plan Manifest

Write `plan.toml` after decomposition and lifecycle selection, but **before** phase compilation:
```toml
[meta]
# Variables resolved in Phase 0 from `{cpt_cmd} --json info`.
# Persisted here so the runtime can read them on resume after context compaction
# without re-deriving them; refresh by re-running `cpt --json info` if stale.
cpt_cmd = "{resolved cpt_cmd value}"           # e.g. "cpt" or "python3 /abs/path/.bootstrap/.core/skills/cypilot/scripts/cypilot.py"
cypilot_path = "{absolute cypilot_path}"        # e.g. "/abs/path/.bootstrap"
project_root = "{absolute project_root}"        # e.g. "/abs/path/repo"
# variables = "{path to JSON snapshot}"          # OPTIONAL: full `variables` dict from `info` output

[plan]
task = "{task description}"
type = "{generate|analyze|implement}"
target = "{artifact kind}"          # e.g. "PRD", "DESIGN", "FEATURE"
target_key = "{canonical target identity}" # deterministic naming/reuse key for this plan target
kit_path = "{absolute path to kit}" # e.g. "/abs/path/config/kits/sdlc"
created = "{ISO 8601 timestamp}"
lifecycle = "{gitignore|cleanup|archive|manual}"
execution_status = "not_started"     # not_started|briefs_only|in_progress|done|failed
lifecycle_status = "pending"         # pending|ready|in_progress|manual_action_required|done|failed; use "done" immediately for `gitignore` once `.plans/` is gitignored
plan_dir = "{cypilot_path}/.plans/{task-slug}"
active_plan_dir = "{cypilot_path}/.plans/{task-slug}" # update if archived
input_dir = "{cypilot_path}/.plans/{task-slug}/input" # omit or set "" when no raw-input package was created
input_manifest = "{cypilot_path}/.plans/{task-slug}/input/manifest.json" # omit or set "" when no raw-input package was created
input_signature = "{sha256 of direct prompt + provided file contents}" # omit or set "" when no raw-input package was created
input_chunks = []                      # ordered `input/*.md` files emitted by `chunk-input`
total_phases = {N}

[[phases]]
number = 1
title = "{phase title}"
slug = "{short-slug}"
file = "phase-01-{slug}.md"
brief_file = "brief-01-{slug}.md"  # compilation brief (MUST exist before phase file)
status = "pending"
kind = "delivery"                    # delivery|lifecycle
depends_on = []
input_files = []                    # project files to read at runtime
output_files = ["{target file}"]    # project files this phase creates/modifies
outputs = ["out/phase-01-{what}.md"] # intermediate results for later phases
inputs = []                         # intermediate results from prior phases
template_sections = [1, 2, 3]      # H2 numbers from template.md (generate tasks)
checklist_sections = []             # H2 numbers from checklist.md (analyze tasks)
```
`plan.execution_status` tracks aggregate phase execution independently from plan-file handling. `plan.lifecycle_status` tracks whether plan storage actions are still pending, in progress, complete, or awaiting manual resolution.

### 3.2 Generate Compilation Briefs (from Template)

For each phase, generate a compilation brief (`~50-80` lines). ALWAYS open and follow `{cypilot_path}/.core/requirements/brief-template.md`. Estimate kit file sizes with `wc -l`, list examples with `ls`, fill the brief from `plan.toml`, and write `{cypilot_path}/.plans/{task-slug}/brief-{NN}-{slug}.md`. A brief contains the context boundary, phase metadata, load instructions, phase file structure, and context budget — never copied kit content or the phase file itself.

When `plan.input_chunks` is non-empty, each brief MUST include the specific `input/*.md` chunk files assigned to that phase in both `input_files` metadata and Load Instructions, with runtime-read steps for every listed chunk.

### 3.2A Stop After Briefs & Ask For Next Step

Once `plan.toml` and every `brief-*` file exist on disk, stop immediately and report:
```text
Brief package prepared: {cypilot_path}/.plans/{task-slug}/
  Manifest: plan.toml
  Briefs: {N}
  Compiled phase files: 0/{N}

What would you like to do next?

  [1] Generate phase files here — compile phases in the current chat from the briefs
  [2] Generate phase-compilation prompts — emit one self-contained prompt per brief for downstream chats
  [3] Run phase-compiler subagents — invoke `cypilot-phase-compiler` for each brief
  [4] Stop here — keep the manifest and briefs without compiling phase files yet
Reply with `1`, `2`, `3`, or `4`.
[1] Suggested when you want to keep working in this chat and compile phase files now.
[2] Emit downstream prompts instead of compiling phase files here.
[3] Use dedicated phase-compiler subagents for compilation.
[4] Stop after the brief package and resume later.
```
Wait for user choice before entering Phase 3.3. Do not emit `Plan created` at this checkpoint.

If the user chooses option `[4]`, set `plan.execution_status = "briefs_only"` in `plan.toml` before stopping. A plan with `execution_status = "briefs_only"` and existing `brief-*` files on disk is valid and does NOT require re-planning. Recovery instruction: in a new chat, read `plan.toml`, confirm `execution_status = "briefs_only"`, and present the same `[1]–[4]` menu to continue from the saved brief package.

### 3.3 Produce Phase Files Or Phase-Generation Prompts

Phase 3.3 runs only after the user chooses one of the post-brief paths.

For each phase, apply:
```text
--- CONTEXT BOUNDARY ---
Disregard previous workflow context except plan.toml metadata and recorded user decisions. The brief below is self-contained.
Read ONLY the files listed in the brief. Follow its instructions exactly.
---
```
Then:
1. Read the brief **FROM DISK** at `{cypilot_path}/.plans/{task-slug}/{brief_file}`. If it is not on disk, go back to 3.2. Using a brief that was not read from disk is INVALID.
2. If the user chose option `[1]`, compile exactly one `phase-*` file in the current chat from that brief, validate it against the brief, report `Phase {N} compiled inline → {filename} ({lines} lines)`, and continue.
3. If the user chose option `[2]`, emit exactly one self-contained downstream prompt for that brief. The prompt MUST instruct the downstream worker to read the brief from disk, apply the context boundary, and compile exactly one phase file. Report `Phase {N} prompt prepared → {brief_file}` and continue. Do not write `phase-*` files in this mode.
4. If the user chose option `[3]`, route compilation to `{cypilot_path}/.core/skills/cypilot/agents/cypilot-phase-compiler.md`. Accept the result only if it reports a successful compile summary with phase identity, output file path, and compile-time validation outcome. Report `Phase {N} compiled via subagent → {filename} ({lines} lines)` and continue.

The planner remains responsible for decomposition, manifest creation, and brief generation. Phase-file production may happen inline, via downstream prompts, or through the dedicated phase compiler subagent depending on the user's post-brief choice.

### 3.4 Validate Phase Files

Run Phase 3.4 only if option `[1]` or `[3]` generated phase files in this run.

After all phases are compiled:
1. Every `brief_file` exists on disk.
2. Each phase file matches its brief's load instructions.
3. Unresolved `{...}` variables outside code fences = zero.
4. Phase file size `≤ 1000` lines; otherwise split.
5. Rules completeness: every applicable `MUST` / `MUST NOT` from `rules.md` is present; if adding missing rules breaks budget, re-split — NEVER drop rules.
6. Context budget `phase_file_lines + input_files + inputs + output_lines ≤ 2000`; otherwise split.
7. After the final phase, the union of all Rules sections must cover `100%` of applicable rules.

## Phase 4: Finalize Plan

> **Note**: `plan.toml` was already written in Phase 3.1 and briefs were written in Phase 3.2. Enter Phase 4 only if the user selected option `[1]` or `[3]` and all `phase-*` files were produced in Phase 3.3. If the user selected option `[2]` or `[4]`, stop after the brief checkpoint and do not emit `Plan created`.

Status model in `plan.toml`:
- `phases[].status`: `pending`, `in_progress`, `done`, `failed`
- `plan.execution_status`: aggregate phase execution state, independent of lifecycle handling
- `plan.lifecycle_status`: plan-file lifecycle state, independent of whether all phases are already complete

Update rules:
- all phases `pending` → `plan.execution_status = "not_started"`
- user chose option `[4]` at brief checkpoint → `plan.execution_status = "briefs_only"` (valid stop state; resume by presenting `[1]-[4]` menu)
- any phase `in_progress`, or any mix of `done` and `pending`, → `plan.execution_status = "in_progress"`
- any phase `failed` → `plan.execution_status = "failed"` until explicitly reopened or downgraded
- all phases `done` → `plan.execution_status = "done"`; `plan.lifecycle_status` may still be `ready`, `in_progress`, or `manual_action_required`

### 4.1 Validate Plan Before Handoff (MANDATORY)

> **⛔ CRITICAL**: Offer plan validation as the FIRST next step.

Before generating the startup prompt or offering execution handoff:
1. Self-validate against `{cypilot_path}/.core/requirements/plan-checklist.md`.
2. Report:
```text
═══════════════════════════════════════════════
Plan Self-Validation: {task-slug}
───────────────────────────────────────────────
| Category | Status |
|----------|--------|
| 1. Structural | PASS/FAIL |
| 2. Interactive Questions | PASS/FAIL |
| 3. Rules Coverage | PASS/FAIL |
| 4. Context Completeness | PASS/FAIL |
| 5. Phase Independence | PASS/FAIL |
| 6. Budget Compliance | PASS/FAIL |
| 7. Lifecycle & Handoff | PASS/FAIL |
Overall: PASS/FAIL
═══════════════════════════════════════════════
```
If any category FAILs: list issues and offer to fix them.

### 4.2 Report Plan & Offer Next Steps

If all categories PASS, report:
```text
Plan created: {cypilot_path}/.plans/{task-slug}/
  Phases: {N}
  Files: {file_count}
  Lifecycle: {lifecycle}
```

You may emit `Plan created` only after Phase 3.4 PASS confirms that `plan.toml`, every `brief-*`, and every compiled `phase-*` file already exist on disk. If the run stopped after brief generation or produced only downstream prompts, omit this section.

Then immediately report:
```text
Native execution options available:
  This plan can be delegated to ralphex using Cypilot's native delegation feature.
  Command: {cpt_cmd} delegate "{cypilot_path}/.plans/{task-slug}"

Delegation prompt:
  I have a Cypilot execution plan ready at:
    {cypilot_path}/.plans/{task-slug}

  Please delegate this plan to ralphex using Cypilot's native delegation flow.

Native phase execution prompt:
  I have a Cypilot execution plan ready at:
    {cypilot_path}/.plans/{task-slug}/plan.toml

  Please execute the next phase using Cypilot's native phase runner.
```

 Then present ALL of these next steps and wait for user choice before generating the startup prompt:
```text
What would you like to do next?

  [1] Validate plan thoroughly — run /cypilot-analyze on the plan
  [2] Execute Phase 1 natively — use Cypilot's dedicated phase-runner subagent
  [3] Prepare execution handoff — generate the Phase 1 startup prompt for a downstream execution chat
  [4] Review plan files — inspect phase files before execution
  [5] Modify plan — adjust phases, add/remove content
Reply with `1`, `2`, `3`, `4`, or `5`.
[1] Suggested default before execution — verify the plan thoroughly with `/cypilot-analyze`.
[2] Start executing the first phase now with the native phase runner.
[3] Generate a handoff prompt for a separate execution chat.
[4] Inspect the plan files manually before deciding what to do next.
[5] Rework the plan structure or contents before execution.
```

### New-Chat Startup Prompt

When the user chooses execution handoff, emit the entire startup prompt inside a **single fenced code block**:
```text
I have a Cypilot execution plan ready at:
  {cypilot_path}/.plans/{task-slug}/plan.toml

Please read the plan manifest, then execute Phase 1.
The phase file is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for Phase 2.
```
  No explanatory text may be mixed into that code fence.

 ## Appendix A: Execute Phases (Reference Only)

 This appendix is the downstream runtime contract for generated plans. It is not a plan-creation phase.

 When the user requests phase execution, route native execution to `{cypilot_path}/.core/skills/cypilot/agents/cypilot-phase-runner.md`.

### 5.1 Load Phase

1. Read `plan.toml` and use manifest state, not chat memory, as the source of truth.
2. If `plan.execution_status = "briefs_only"`, do not read a phase file yet; instead return to the Phase 3.2 post-brief choice set so the user can compile phases via inline generation, downstream prompts, or `cypilot-phase-compiler`.
3. Select the earliest executable phase whose dependencies are all `done`.
4. Audit upstream `output_files`, declared `outputs`, and downstream `inputs`; when `lifecycle = "cleanup"` and `plan.lifecycle_status = "done"`, the intentional cleanup removal of `brief-*`, `phase-*`, and `out/` is exempt.
5. If the audit reopens work, repair lifecycle state before proceeding.
6. Mark the chosen phase `in_progress`, then read only that phase file and follow it exactly.

### 5.2 Execute

Follow the phase Task section exactly.

### 5.3 Save Intermediate Results

Before reporting, verify every file in the phase `outputs` list was created or updated. `out/` remains the data contract between phases.

### 5.4 Report

Produce the completion report in the phase file's Output Format.

### 5.5 Update Status

Set the phase status to `done` only when all acceptance criteria pass; otherwise set it to `failed` with the reason recorded in the manifest.

### 5.6 Phase Handoff

If the phase file already includes a handoff prompt, do not duplicate it. Otherwise emit a single fenced next-phase prompt, then offer same-chat continuation versus new-chat execution. Same-chat continuation MUST re-enter from `plan.toml`, re-audit dependencies, and ignore prior chat memory.

If the last phase completes:
- report all phases complete and set `plan.execution_status = "done"`
- run the lifecycle action exactly once according to `gitignore`, `cleanup`, `archive`, or `manual`
- if lifecycle is `manual`, present exactly one keep/archive/delete prompt
- optionally offer deterministic validation or semantic review only when validator applicability is proven for the completed target

 ### 5.7 Abandoned Plan Recovery

 If a plan is abandoned or same-chat continuation loses state: `plan.toml` is the checkpoint, but recovery MUST audit completed work before resuming.

1. Read `plan.toml`.
2. Audit every phase marked `done` in dependency order against its declared `output_files`, its declared `outputs`, and any intermediate artifacts required by downstream `inputs`, except that when `lifecycle = "cleanup"` and `plan.lifecycle_status = "done"`, the intentional Cleanup removals of `brief-*`, `phase-*`, and `out/` are exempt and MUST NOT count as inconsistency.
3. If a completed phase is inconsistent, reopen it by downgrading `status` from `done` to `pending` or `failed` as appropriate, and also downgrade every downstream dependent phase to `pending`.
4. If any phase was reopened, repair lifecycle state before resuming: keep `plan.lifecycle_status = "done"` only for `gitignore`; otherwise set `plan.lifecycle_status = "pending"` and cancel any stale `manual_action_required`, `ready`, or `in_progress` lifecycle state from the prior completion attempt.
5. Recompute `plan.execution_status` from the downgraded manifest.
6. Resume from the earliest executable phase after the audit — not merely the first phase that was previously `pending`.

Recovery prompt:
```text
I have an incomplete Cypilot execution plan at:
  {cypilot_path}/.plans/{task-slug}/plan.toml
Please read the plan manifest, audit completed phases against their declared `output_files`, declared `outputs`, and downstream `inputs`, repair stale lifecycle state if work is reopened, and resume from the earliest executable phase.
```

## Appendix B: Check Status (Reference Only)

This appendix defines status reporting after plan creation.

When the user asks for plan status, read `plan.toml` and report the task, type, target, execution status, lifecycle status, active location, and per-phase progress from the manifest. If `lifecycle_status = manual_action_required`, direct the operator back to the execution flow that presents the single lifecycle choice instead of duplicating that menu in a status-only response. If lifecycle handling failed or any phase failed, suggest retry, reopen, or manual recovery.

## Plan Storage Format

All plan data lives in `{cypilot_path}/.plans/{task-slug}/`:
```text
.plans/
  generate-prd-myapp/
    plan.toml
    input/
      manifest.json
      direct-prompt.md
      001-01-request-part-01.md
    brief-01-overview.md
    brief-02-requirements.md
    phase-01-overview.md
    phase-02-requirements.md
    out/
      phase-01-actors.md
      phase-01-id-scheme.md
      phase-02-req-ids.md
```
Compute `plan.target_key` first for deterministic naming, but use it for plan-directory reuse only together with the current raw-input identity. Directory naming stays human-readable; equality/reuse checks compare `type + plan.target_key + plan.input_signature` whenever raw-input packaging is in scope.
Naming conventions:
- generate: `{type}-{artifact_kind}-{artifact_slug}`. Use the explicit artifact name when available; otherwise use the output path stem.
- analyze: `{type}-{artifact_kind}-{artifact_slug}` for artifact-oriented reviews, or `{type}-path-{target_path_slug}` when the primary target is a file or directory path. For path targets, if the absolute target path is under `{project_root}`, strip `{project_root}/` first and normalize that relative path (`{project_root}/src/api/users.py` → `analyze-path-src-api-users-py`); otherwise normalize the absolute-path segments.
- implement: `{type}-feature-{feature_slug}`. Derive `{feature_slug}` from the FEATURE ID first; if no ID exists, use the FEATURE title; if neither exists, use the FEATURE file stem.
- normalization: lowercase, replace path separators / spaces / punctuation with `-`, collapse repeated `-`, trim leading/trailing `-`.
- collision handling: if an existing non-archived plan has the same `type`, the same `plan.target_key`, and the same `plan.input_signature` (or both plans have no raw-input package), reuse its directory; otherwise append `-2`, `-3`, ... using the lowest available suffix.
- phase file: `phase-{NN}-{slug}.md`
- plan manifest: always `plan.toml`
Lifecycle behavior is controlled by the strategy selected in Phase 2.1 and recorded in `plan.toml`; if archived, `active_plan_dir` points to the archive path, and if cleaned up, `plan.toml` remains as the terminal receipt even after compiled plan artifacts are removed.

## Execution Log

Keep a brief **plan-generation-only** observable log in chat, not on disk. Runtime execution/status examples belong to Appendix A and Appendix B only.
```text
[plan] Assessing scope: generate PRD for myapp
[plan] Estimated size: ~1200 lines → plan needed
[plan] Strategy: generate (by template sections)
[plan] Decomposition: 4 phases
[plan] Compiling phase 1/4: Overview and Actors
[plan] Phase 1 compiled: 380 lines (within budget)
[plan] ...
[plan] Plan written: .plans/generate-prd-myapp/ (4 phases)
...
```
