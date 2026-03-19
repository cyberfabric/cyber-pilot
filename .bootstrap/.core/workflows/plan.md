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
- [Phase 3: Compile Phase Files](#phase-3-compile-phase-files)
- [Phase 4: Finalize Plan](#phase-4-finalize-plan)
- [Phase 5: Execute Phases](#phase-5-execute-phases)
- [Phase 6: Check Status](#phase-6-check-status)
- [Plan Storage Format](#plan-storage-format)
- [Execution Log](#execution-log)

<!-- /toc -->

> **⛔ CRITICAL CONSTRAINT**: This workflow ONLY generates execution plans. It NEVER executes the underlying task (generate, analyze, implement) directly. Even if the task seems small, this workflow's job is to produce phase files — not to do the work itself. If the task is small enough for direct execution, tell the user to use `/cypilot-generate` or `/cypilot-analyze` instead.

> **⛔ CRITICAL CONSTRAINT — FULL CONTEXT LOADING**: Before generating ANY plan, you MUST load and process ALL navigation rules (`ALWAYS open`, `OPEN and follow`, `ALWAYS open and follow`) from the **target workflow** (generate.md, analyze.md, or the relevant workflow). Every file referenced by those directives MUST be opened and its content used during decomposition and compilation. Skipping ANY navigation rule means phase files will be compiled with incomplete context, producing broken or shallow results. This is the #1 source of plan quality failures.

> **⛔ CRITICAL CONSTRAINT — KIT RULES ARE LAW** *(highest priority)*: Every rule in the kit's `rules.md` for the target artifact kind MUST be enforced in the generated plan — **completely, without omission or summarization**. Rules are inlined verbatim into phase files. If the full rules don't fit in a single phase, split the phase so each sub-phase gets ALL rules relevant to its scope — but NEVER trim, summarize, or selectively skip rules to fit a budget. The `checklist.md` items are equally mandatory for analyze tasks. A plan that drops kit rules produces artifacts that fail validation.

> **⛔ CRITICAL CONSTRAINT — DETERMINISTIC FIRST**: Every phase step that CAN be done by a deterministic tool (cpt command, script, shell command) MUST use that tool instead of LLM reasoning. Discover available tools dynamically in Phase 0 — do NOT assume a fixed set of commands. Tool capabilities change between versions. The CLISPEC file is the source of truth for what commands exist and what they can do.

> **⛔ CRITICAL CONSTRAINT — INTERACTIVE QUESTIONS COMPLETENESS** *(mandatory)*: You MUST find ALL interactive questions, user input requests, confirmation gates, review requests, and decision points from: (1) the target workflow, (2) `rules.md` for the target artifact kind, (3) `checklist.md`, (4) `template.md`, AND (5) **every file referenced by navigation rules** (`ALWAYS open`, `OPEN and follow`) in those files — recursively. Every interaction point found MUST appear in the compiled plan: pre-resolvable questions asked BEFORE plan generation, phase-bound questions embedded in phase files. **Missing even ONE interaction point = plan is INVALID.** See `{cypilot_path}/.core/requirements/plan-checklist.md` Section 2 for the complete extraction procedure.

> **⛔ CRITICAL CONSTRAINT — BRIEF BEFORE COMPILE**: Phase files MUST NOT be written directly. Every phase file MUST be compiled from a corresponding compilation brief (`brief-{NN}-{slug}.md`) that was written to disk in Phase 3.2. The brief is the contract between decomposition (what to include) and compilation (how to assemble). Skipping briefs produces phase files that silently omit kit content, miss load instructions, or inline wrong sections. **If you find yourself writing a phase file without first reading its brief from disk — STOP, you are violating the workflow.** Write the brief first, write it to disk, THEN compile from it. A phase file without a corresponding brief file on disk = INVALID plan.

ALWAYS open and follow `{cypilot_path}/.core/skills/cypilot/SKILL.md` FIRST WHEN {cypilot_mode} is `off`

**Type**: Operation

ALWAYS open and follow `{cypilot_path}/.core/requirements/execution-protocol.md` FIRST

ALWAYS open and follow `{cypilot_path}/.core/requirements/plan-template.md` WHEN compiling phase files

ALWAYS open and follow `{cypilot_path}/.core/requirements/plan-decomposition.md` WHEN decomposing tasks into phases

OPEN and follow `{cypilot_path}/.core/requirements/prompt-engineering.md` WHEN compiling phase files (phase files ARE agent instructions)

OPEN and follow `{cypilot_path}/.core/requirements/plan-checklist.md` WHEN validating plans (Phase 4.1 self-validation or /cypilot-analyze on plan)

For context compaction recovery during multi-phase workflows, follow `{cypilot_path}/.core/requirements/execution-protocol.md` Section "Compaction Recovery".

---

## Overview

This workflow generates execution plans, not direct results. Use it when work exceeds a single-context window, requires a long checklist, or involves multi-block implementation. Do **not** use it for small edits, direct execution, or work that fits in ~500 compiled lines. Output: `plan.toml` + `N` phase files in `{cypilot_path}/.plans/{task-slug}/`.

## Context Budget & Overflow Prevention (CRITICAL)

- Do NOT load all kit dependencies at once; load incrementally per phase.
- Do NOT hold all phase files in context simultaneously; compile and write one at a time.
- If a phase compilation would exceed current context budget, checkpoint and use Compaction Recovery.
- The plan manifest (`plan.toml`) is the recovery checkpoint and MUST be written before compilation.

Budget targets: Phase 0-1 `~200` lines, Phase 2 `~300`, Phase 3 `~500` per phase file, Phase 4 `~50`, Phase 5-6 `~500` one phase at a time.

## Phase 0: Resolve Variables & Discover Tools

Run `EXECUTE: {cypilot_command} info`; store `{cypilot_path}`, `{project_root}`, and kit paths.

### 0.1 Discover Available Tools

Read `READ: {cypilot_path}/.core/skills/cypilot/cypilot.clispec` and build a dynamic tool map from each `COMMAND` block as `{command_name} — {DESCRIPTION line} [outputs: {OUTPUT format}]`. Also scan `SCAN: {kit_scripts_path}/ for *.py, *.sh files` and add kit scripts with inferred purpose.

## Phase 1: Assess Scope

### 1.1 Identify Task Type

| Signal | Task Type | Target Workflow |
|--------|-----------|----------------|
| `create` / `generate` / `write` / `update` / `draft` + artifact kind | `generate` | `generate.md` |
| `validate` / `review` / `check` / `audit` / `analyze` + artifact kind | `analyze` | `analyze.md` |
| `implement` / `code` / `build` / `develop` + feature name | `implement` | `generate.md` (code mode) |

### 1.1b Extract Target Workflow Navigation Rules (CRITICAL)

Open `{cypilot_path}/.core/workflows/{target_workflow}` and: scan all navigation directives, list referenced files + `WHEN` conditions, evaluate them, open every applicable file, and record a loaded-file manifest.

Report:
```text
Context loaded for plan generation:
  Workflow: {target_workflow} ({N} navigation rules processed)
  Kit files: {M} files loaded ({rules}, {checklist}, {template}, ...)
  Total context: ~{L} lines
  All navigation rules processed? [YES/NO]
```
**Gate**: do NOT proceed until ALL applicable navigation rules are processed and all required referenced files are loaded.

### 1.2 Estimate Compiled Size

Estimate `template_lines + rules_lines + checklist_lines + existing_content_lines`. If `≤ 500`, STOP and direct the user to `/cypilot-generate` or `/cypilot-analyze`; only continue if `> 500`.

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
 
 Resolve generate/analyze → artifact kind, file path, and kit; implement → FEATURE spec path and CDSL blocks. Then report:
 ```text
 Plan scope:
   Type: {generate|analyze|implement}
   Target: {artifact kind or feature name}
   Estimated size: ~{N} lines
 ```
 
 ## Phase 2: Decompose
 
 Open and follow `{cypilot_path}/.core/requirements/plan-decomposition.md`.
 
 Compilation is split to minimize context: write the manifest, write briefs, then compile one phase at a time.
 
 Select a strategy based on task type:
 - **generate**: load the target template, list H2 sections, group them into phases of `2-4` sections, and record phase boundaries.
 - **analyze**: load the target checklist, list checklist categories, group them by validation pipeline order (structural → semantic → cross-ref → traceability → synthesis), and record phase boundaries.
 - **implement**: load the FEATURE spec, list CDSL blocks, assign one block + tests per phase, add scaffolding and final integration phases, and record boundaries.

Output a phase list containing phase number and title, covered sections / categories / blocks, dependencies, `input_files`, `output_files`, assigned interaction points, and intermediate results needed by later phases.

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

  Proceed with compilation? [y/n]
```
Wait for user confirmation before proceeding.

---

## Phase 3: Compile Phase Files

Open and follow `{cypilot_path}/.core/requirements/plan-template.md`.

Compilation is split to minimize context: write the manifest, write briefs, then compile one phase at a time.

### 3.1 Write Plan Manifest

Write `plan.toml` **before** compilation:
```toml
[plan]
task = "{task description}"
type = "{generate|analyze|implement}"
target = "{artifact kind}"          # e.g. "PRD", "DESIGN", "FEATURE"
kit_path = "{absolute path to kit}" # e.g. "/abs/path/config/kits/sdlc"
created = "{ISO 8601 timestamp}"
total_phases = {N}

[[phases]]
number = 1
title = "{phase title}"
slug = "{short-slug}"
file = "phase-01-{slug}.md"
brief_file = "brief-01-{slug}.md"  # compilation brief (MUST exist before phase file)
status = "pending"
depends_on = []
input_files = []                    # project files to read at runtime
output_files = ["{target file}"]    # project files this phase creates/modifies
outputs = ["out/phase-01-{what}.md"] # intermediate results for later phases
inputs = []                         # intermediate results from prior phases
template_sections = [1, 2, 3]      # H2 numbers from template.md (generate tasks)
checklist_sections = []             # H2 numbers from checklist.md (analyze tasks)

# ... one [[phases]] block per phase
```

### 3.2 Generate Compilation Briefs (from Template)

For each phase, generate a compilation brief (`~50-80` lines). ALWAYS open and follow `{cypilot_path}/.core/requirements/brief-template.md`. Estimate kit file sizes with `wc -l`, list examples with `ls`, fill the brief from `plan.toml`, and write `{cypilot_path}/.plans/{task-slug}/brief-{NN}-{slug}.md`. A brief contains the context boundary, phase metadata, load instructions, phase file structure, and context budget — never copied kit content or the phase file itself.

### 3.3 Compile Phase Files (Agent + Context Boundary)

For each phase, apply:
```text
--- CONTEXT BOUNDARY ---
Disregard all previous context. The brief below is self-contained.
Read ONLY the files listed in the brief. Follow its instructions exactly.
---
```
Then:
1. Read the brief **FROM DISK** at `{cypilot_path}/.plans/{task-slug}/{brief_file}`. If it is not on disk, go back to 3.2. Compiling without reading the brief from disk is INVALID.
2. Read kit files per the brief: rules (`MUST` / `MUST NOT` only; skip Prerequisites / Tasks / Next Steps), template sections, and example.
3. Write the phase file with TOML frontmatter, Preamble, What, Prior Context, User Decisions, Rules, Input, Task, Acceptance Criteria, Output Format.
4. Apply deterministic-first task design: `EXECUTE:` for deterministic work, LLM reasoning only for creative/synthesis, `Read <file>` for inputs, and review gates as `Present output to user for review. Wait for approval.`
5. Report `Phase {N} compiled → {filename} ({lines} lines)` and re-apply the context boundary before the next phase.

Continue mode = same chat with context boundary. New chat mode = recommended for `4+` phases.

### 3.4 Validate Phase Files

After all phases are compiled:
1. Every `brief_file` exists on disk.
2. Each phase file matches its brief's load instructions.
3. Unresolved `{...}` variables outside code fences = zero.
4. Phase file size `≤ 1000` lines; otherwise split.
5. Rules completeness: every applicable `MUST` / `MUST NOT` from `rules.md` is present; if adding missing rules breaks budget, re-split — NEVER drop rules.
6. Context budget `phase_file_lines + input_files + inputs + output_lines ≤ 2000`; otherwise split.
7. After the final phase, the union of all Rules sections must cover `100%` of applicable rules.

---

## Phase 4: Finalize Plan

> **Note**: `plan.toml` was already written in Phase 3.1 and phase files compiled in Phase 3.2-3.3.

Status values in `plan.toml`: `pending`, `in_progress`, `done`, `failed`.

### Plan Lifecycle Strategy

Ask how completed plans should be handled:
```text
Plan files are stored in {cypilot_path}/.plans/{task-slug}/.
How should completed plans be handled?
  [1] .gitignore — add .plans/ to .gitignore
  [2] Cleanup phase — add a final phase that deletes plan files after all phases pass
  [3] Archive — move to {cypilot_path}/.plans/.archive/
  [4] Keep as-is — leave plan files in place, user manages manually
```
Record `lifecycle = "gitignore" | "cleanup" | "archive" | "manual"`. Rules: `gitignore` appends `.plans/`; `cleanup` adds a final Cleanup phase; `archive` moves to `.plans/.archive/{task-slug}/` and gitignores only `.plans/.archive/`; `manual` does nothing. Report `Plan created: {cypilot_path}/.plans/{task-slug}/` with phase count, file count, and lifecycle.

### Phase 4.1: Validate Plan Before Execution (MANDATORY)

> **⛔ CRITICAL**: Offer plan validation as the FIRST next step.

Before generating the startup prompt:
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
If any category FAILs: list issues and offer to fix them. If all PASS: present ALL of these next steps and wait for user choice before generating the startup prompt:
```text
What would you like to do next?

  [1] Validate plan thoroughly — run /cypilot-analyze on the plan
  [2] Start execution — begin with Phase 1
  [3] Review plan files — inspect phase files before execution
  [4] Modify plan — adjust phases, add/remove content
```

### New-Chat Startup Prompt

When requested, emit the entire startup prompt inside a **single fenced code block**:
```text
I have a Cypilot execution plan ready at:
  {cypilot_path}/.plans/{task-slug}/plan.toml

Please read the plan manifest, then execute Phase 1.
The phase file is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for Phase 2.
```
No explanatory text may be mixed into that code fence.

---

## Phase 5: Execute Phases

When the user requests phase execution:

### 5.1 Load Phase

1. Read `plan.toml` to find the next pending phase respecting dependencies.
2. Update that phase status to `in_progress`.
3. Read the phase file.
4. Follow the phase file exactly — it is self-contained.

### 5.2 Execute

Follow the phase Task section exactly.

### 5.3 Save Intermediate Results

Before reporting, verify every file in the phase `outputs` list was created/updated. If any is missing, report failure. `out/` files are the data contract between phases.

### 5.4 Report

Produce the completion report in the phase file's Output Format.

### 5.5 Update Status

If all acceptance criteria pass: set status to `done`; otherwise set it to `failed` and record the reason.

```toml
[[phases]]
number = 1
title = "PRD Overview and Actors"
file = "phase-01-overview.md"
status = "done"
depends_on = []
completed = "2026-03-12T14:30:00Z"
```

### 5.6 Phase Handoff

If the phase file already includes a handoff prompt, do NOT generate a duplicate. Otherwise output:
```text
Phase {N}/{M}: {status}

Next phase prompt (copy-paste into new chat if needed):
```
Then emit the next-phase prompt inside a **single fenced code block**:
```text
I have a Cypilot execution plan at:
  {cypilot_path}/.plans/{task-slug}/plan.toml

Phase {N} is complete ({status}).
Please read the plan manifest, then execute Phase {N+1}: "{title}".
The phase file is: {cypilot_path}/.plans/{task-slug}/phase-{NN}-{slug}.md
It is self-contained — follow its instructions exactly.
After completion, report results and generate the prompt for Phase {N+2}.
```
Then ask:
```text
Continue in this chat? [y] execute next phase here | [n] copy prompt above to new chat
(Recommended: new chat for guaranteed clean context)
```
If user chooses continue, apply:
```text
--- CONTEXT BOUNDARY ---
Previous phase execution is complete. Disregard all prior context.
Read ONLY the next phase file — it is self-contained.
Do not reference any information from before this boundary.
---
```
The phase file on disk is the sole source of truth.

**If last phase** instead of a next-phase prompt, MUST:
1. Report completion:
   ```text
   ═══════════════════════════════════════════════
   ALL PHASES COMPLETE ({M}/{M})
   ───────────────────────────────────────────────
   Plan: {cypilot_path}/.plans/{task-slug}/plan.toml
   Target: {artifact kind or feature}
   Phases completed: {M}
   Lifecycle strategy: {lifecycle}
   ═══════════════════════════════════════════════
   ```
2. Execute the lifecycle strategy from `plan.toml`.
3. Ask:
   ```text
   Plan execution complete. What would you like to do with the plan files?

     [1] Keep — leave plan files for reference
     [2] Archive — move to .plans/.archive/ (gitignored)
     [3] Delete — remove plan directory entirely
     [4] Already handled — lifecycle strategy was {lifecycle}
   ```
4. Offer validation:
   ```text
   Would you like to validate the generated {artifact/code}?

     [1] Yes — run /cypilot-analyze on the output
     [2] No — done for now
   ```

### 5.7 Abandoned Plan Recovery

If a plan is abandoned: `plan.toml` is the checkpoint; read it, find the first `pending` or `in_progress` phase, verify any partial outputs, and resume from there.

Recovery prompt:
```text
I have an incomplete Cypilot execution plan at:
  {cypilot_path}/.plans/{task-slug}/plan.toml
Please read the plan manifest, check which phases are done/pending, and resume execution from the first incomplete phase.
```

---

## Phase 6: Check Status

When the user asks for plan status, read `plan.toml` and report:
```text
Plan: {task description}
  Type: {type}
  Target: {target}
  Progress: {done}/{total} phases

  Phase 1: {title} — {status}
  Phase 2: {title} — {status}
  ...
  Phase N: {title} — {status}
```
If any phase failed, suggest retry / skip / abort.

---

## Plan Storage Format

All plan data lives in `{cypilot_path}/.plans/{task-slug}/`:
```text
.plans/
  generate-prd-myapp/
    plan.toml
    brief-01-overview.md
    brief-02-requirements.md
    phase-01-overview.md
    phase-02-requirements.md
    out/
      phase-01-actors.md
      phase-01-id-scheme.md
      phase-02-req-ids.md
```
Naming conventions:
- task slug: `{type}-{artifact_kind}-{project_slug}`
- phase file: `phase-{NN}-{slug}.md`
- plan manifest: always `plan.toml`

Cleanup is controlled by the lifecycle strategy from Phase 4.

---

## Execution Log

Keep a brief observable log in chat, not on disk:
```text
[plan] Assessing scope: generate PRD for myapp
[plan] Estimated size: ~1200 lines → plan needed
[plan] Strategy: generate (by template sections)
[plan] Decomposition: 4 phases
[plan] Compiling phase 1/4: Overview and Actors
[plan] Phase 1 compiled: 380 lines (within budget)
[plan] ...
[plan] Plan written: .plans/generate-prd-myapp/ (4 phases)
[exec] Phase 1/4: in_progress
[exec] Phase 1/4: done (all criteria passed)
...
```
