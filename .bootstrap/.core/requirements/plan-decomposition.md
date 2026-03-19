---
cypilot: true
type: requirement
name: Plan Decomposition Strategies
version: 1.0
purpose: Define how to split tasks into phases by type — generate, analyze, implement
---

# Plan Decomposition Strategies


<!-- toc -->

- [Overview](#overview)
- [Strategy Selection](#strategy-selection)
- [Strategy 1: Generate (by Template Sections)](#strategy-1-generate-by-template-sections)
- [Strategy 2: Analyze Artifacts (by Checklist Categories)](#strategy-2-analyze-artifacts-by-checklist-categories)
- [Strategy 2b: Analyze Codebase (by Scope + Runtime Reading)](#strategy-2b-analyze-codebase-by-scope--runtime-reading)
- [Strategy 3: Implement (by CDSL Blocks)](#strategy-3-implement-by-cdsl-blocks)
- [Budget Enforcement](#budget-enforcement)
- [Execution Context Prediction](#execution-context-prediction)
- [Phase Dependencies](#phase-dependencies)
- [Single-Context Bypass](#single-context-bypass)

<!-- /toc -->

## Overview

The plan workflow MUST choose a decomposition strategy by task type. Every phase MUST be independently executable, self-contained except for declared runtime reads, and small enough to fit the context budget.

## Strategy Selection

| Task type | Detect when | Strategy |
|-----------|-------------|----------|
| `generate` | create, generate, write, update, draft | split by template sections |
| `analyze` | validate, review, check, audit, analyze | split by checklist categories |
| `implement` | implement, code, build, develop | split by CDSL blocks |

If intent is ambiguous, ask the user to clarify.

## Strategy 1: Generate (by Template Sections)

| Step | Rule |
|------|------|
| 1 | Load the target template |
| 2 | Identify all H2 sections |
| 3 | Group adjacent sections into phases of 2-4 sections each |
| 4 | Each phase creates or updates one section group |

Grouping rules:
 
- Group sections with dependencies.
- Keep the first and final synthesis groups small.
- Give any section that would exceed 300 compiled lines its own phase.

## Strategy 2: Analyze Artifacts (by Checklist Categories)

> For codebase analysis, use Strategy 2b.

| Step | Rule |
|------|------|
| 1 | Load the target checklist |
| 2 | Identify checklist categories by heading group |
| 3 | Group categories into phases following the validation pipeline |
| 4 | Each phase produces a partial report |

Validation pipeline order MUST be: Structural → Semantic → Cross-reference → Traceability → Synthesis.

Grouping rules:
 
- Structural + semantic MAY combine if checklist size is `< 20`.
- Cross-reference + traceability MAY combine if external references are few.
- Synthesis is always final.
- If the checklist has `< 15` items, use 2 phases: checks + synthesis.

## Strategy 2b: Analyze Codebase (by Scope + Runtime Reading)

> **⚠️ EXCEPTION TO SELF-CONTAINMENT**: code analysis is the one case where runtime file reading is permitted because code is too large to inline.

| Phase | Scope | Inline | Runtime read |
|------|-------|--------|--------------|
| 1 | Setup | Checklist, file patterns | Design artifact, directory listing |
| 2 | File-level | Naming/style checks | Source files |
| 3 | Module-level | Boundary/interface checks | Design artifact, module entry points |
| 4 | Cross-module | Contract/interface checks | Import graphs, related modules |
| 5 | Traceability | `@cpt-*` rules, ID rules | Design IDs, marked files |
| 6 | Synthesis | Acceptance criteria | Partial reports |

MUST inline checklist criteria, codebase rules, `@cpt-*` format, file-pattern metadata, and acceptance criteria.

MUST runtime-read DESIGN / FEATURE artifacts, source files, directory listings, import graphs, and prior `out/` results.

Grouping rules:
 
- If codebase has `< 10` files, combine file-level and module-level.
- If `> 50`, split file-level by top-level directory.
- Traceability is ALWAYS separate.
- Synthesis is always final.

## Strategy 3: Implement (by CDSL Blocks)

| Step | Rule |
|------|------|
| 1 | Load the FEATURE spec |
| 2 | Identify CDSL blocks: flows, algorithms, state machines |
| 3 | Each CDSL block + its tests becomes one phase |
| 4 | Add a final integration phase |

Grouping rules:
 
- Each flow/algo/state machine is its own phase.
- Blocks with `< 3` steps MAY combine with related blocks.
- Blocks that would exceed `> 500` lines MUST split by step groups.
- Tests stay with implementation.
- Scaffolding MUST NOT implement business logic.
- Integration MUST NOT introduce new business logic.

## Budget Enforcement

| Metric | Target | Maximum | Action |
|--------|--------|---------|--------|
| Compiled phase file | ≤ 500 | ≤ 1000 | Split into sub-phases |
| Rules section | ≤ 200 | ≤ 300 | Narrow phase scope |
| Input section | ≤ 300 | ≤ 500 | Split input |
| Task steps | 3-7 | 10 | Split task |

Enforcement algorithm: compile, count lines, accept if `≤ 500`, warn if `501-1000`, MUST split if `> 1000`.

Splitting rules:
 
- If Rules is largest, **NEVER trim or summarize rules** — narrow phase scope instead.
- If Input is largest, split input across more phases.
- If Task is largest, split task into sequential phases with explicit handoff.

> **Invariant**: the union of all phase Rules sections MUST cover 100% of the target `rules.md`.

## Execution Context Prediction

Phase files inline stable kit content while reading dynamic project content at runtime.

```text
execution_context = phase_file_lines
                   + sum(runtime_artifact_lines)
                   + sum(runtime_code_lines)
                   + sum(intermediate_input_lines)
                   + estimated_output_lines
```

Heuristics: `phase_file_lines` = compiled phase size; `runtime_artifact_lines` = artifacts in `input_files`; `runtime_code_lines` = file count × average size; `intermediate_input_lines` = prior `out/` files; `estimated_output_lines` = expected generated/report output.

| Level | Threshold | Action |
|-------|-----------|--------|
| Safe | `≤ 1500` | Accept |
| Warning | `1501-2000` | Accept with warning |
| Overflow | `> 2000` | **MUST split** |

| Largest contributor | Split strategy |
|--------------------|----------------|
| Runtime artifacts | split checks by artifact |
| Runtime code | split by directory or module |
| Intermediate inputs | add a consolidation phase |
| Phase file itself | narrow scope per phase |

Re-estimate after each split and repeat until every phase is within budget.

Example:

```text
Analyze PRD + DESIGN consistency
phase_file_lines: 600
runtime_artifacts: 1200
intermediate_inputs: 50
estimated_output_lines: 200
total: 2050 → OVERFLOW
action: split into one PRD-focused phase and one DESIGN-focused phase
```

During decomposition: estimate every phase, flag warning/overflow phases, auto-split overflow phases before compilation, then report estimates in the decomposition summary.

## Phase Dependencies

Phases MUST declare dependencies in TOML frontmatter.

- Phase 1 has no dependencies: `depends_on = []`.
- Later phases depend on the phase that creates required inputs.
- Independent phases MAY run in parallel.
- The final synthesis/integration phase depends on all required prior phases.
- The plan workflow MUST present phases sequentially by default even when parallel execution is possible.

## Single-Context Bypass

If total compiled content would fit within `500` lines, the plan workflow MUST stop and redirect to the direct workflow instead of generating a plan.

1. Estimate total compiled size.
2. If estimate `≤ 500`, redirect to `/cypilot-generate` or `/cypilot-analyze`.
3. If estimate `> 500`, continue plan generation.
