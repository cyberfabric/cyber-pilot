---
cypilot: true
type: requirement
name: Plan Checklist
version: 1.0
purpose: Checklist for validating execution plans — used by analyze workflow and plan self-validation
---

# Plan Checklist


<!-- toc -->

- [Procedure](#procedure)
- [1. Structural Validation](#1-structural-validation)
- [1b. Brief-Phase Integrity](#1b-brief-phase-integrity)
- [2. Interactive Questions Completeness](#2-interactive-questions-completeness)
- [3. Rules Coverage](#3-rules-coverage)
- [4. Context Completeness](#4-context-completeness)
- [5. Phase Independence](#5-phase-independence)
- [6. Budget Compliance](#6-budget-compliance)
- [7. Lifecycle & Handoff](#7-lifecycle--handoff)
- [Validation Procedure](#validation-procedure)
- [Output Format](#output-format)

<!-- /toc -->

## Procedure
- [ ] Use this checklist after plan generation, during `/cypilot-analyze` on a plan, or when debugging failing phases.
- [ ] Verify interactive questions, rules coverage, lifecycle handoff, and validation next-step behavior explicitly.

## 1. Structural Validation
- [ ] `plan.toml` exists at `.plans/{task-slug}/`.
- [ ] `[plan]` contains `task`, `type`, `target`, `created`, `total_phases`, and `lifecycle`.
- [ ] `[[phases]]` blocks match actual phase files.
- [ ] Phase numbers are sequential.
- [ ] `depends_on` forms a valid DAG.
- [ ] `outputs` and `inputs` are consistent across dependent phases.
- [ ] Every `[[phases]]` entry has `brief_file`.
- [ ] Every `brief-{NN}-{slug}.md` exists.
- [ ] Each phase has exactly one corresponding brief.
- [ ] Every `phase-{NN}-{slug}.md` exists.
- [ ] Every phase has valid TOML frontmatter.
- [ ] `number` matches filename.
- [ ] `total` matches `total_phases`.
- [ ] The 9 required sections appear in order: `Preamble`, `What`, `Prior Context`, `User Decisions`, `Rules`, `Input`, `Task`, `Acceptance Criteria`, `Output Format`.

## 1b. Brief-Phase Integrity
- [ ] Every brief file is written before phase compilation starts.
- [ ] Each brief Load Instructions block references specific kit file line ranges.
- [ ] Each phase Rules section covers the ranges referenced by its brief.
- [ ] No phase contains extra inlined kit content outside its brief references.

## 2. Interactive Questions Completeness
- [ ] Source scanning includes the target workflow plus target `rules.md`, `checklist.md`, and `template.md`.
- [ ] Source scanning includes every file referenced by `ALWAYS open` and `OPEN and follow` directives.
- [ ] Question and input-request patterns are detected (`ask the user`, `ask user`, `what is`, `which`, trailing `?`, `user provides`, `user specifies`, `user enters`, `input from user`).
- [ ] Confirmation, review, and decision patterns are detected (`wait for`, `confirm`, `approval`, `before proceeding`, `review`, `present for`, `show to user`, `user inspects`, `choose`, `select`, `option A or B`, `decide`).
- [ ] All detected interaction points are listed in plan-generation output.
- [ ] Each interaction point is classified as `pre-resolvable`, `phase-bound`, or `cross-phase`.
- [ ] Pre-resolvable questions are asked before plan generation.
- [ ] Cross-phase questions are asked before plan generation.
- [ ] Phase-bound questions are embedded in the correct phase files.
- [ ] Each phase with interactions has `## User Decisions`.
- [ ] `## User Decisions` includes `### Already Decided` and `### Decisions Needed During This Phase` when applicable.
- [ ] Review gates appear as explicit Task steps.
- [ ] No source interaction point is omitted.
- [ ] `interaction_points_in_plan >= interaction_points_in_sources`.
- [ ] Rules do not reference `rules.md` by path instead of inlining.
- [ ] Rules do not contain `Prerequisites`, `Load Dependencies`, or `Tasks`, and they contain all required MUST and MUST NOT statements.
- [ ] Input does not reference `checklist.md` or `template.md` by path instead of inlining.
- [ ] Input does not inline full project artifacts or source code except small examples.
- [ ] Every `input_files` and `inputs` entry has a matching `Read {file}` task step.
- [ ] Per-phase context estimate uses `phase_file_lines + sum(input_files) + sum(inputs) + output_lines`.
- [ ] Estimated context does not exceed `2000` lines; `1501-2000` is warned.

## 3. Rules Coverage
- [ ] Target `rules.md` is read and filtered.
- [ ] Every MUST rule appears verbatim in at least one phase Rules section.
- [ ] Every MUST NOT rule appears verbatim in at least one phase Rules section.
- [ ] Rules are not summarized or paraphrased.
- [ ] `Prerequisites`, `Load Dependencies`, `Tasks`, `Next Steps`, and TOC are stripped from Rules.
- [ ] Phase Rules sections cover 100% of applicable MUST and MUST NOT rules in union.
- [ ] For analyze plans, target `checklist.md` is fully loaded.
- [ ] Every checklist item appears in at least one phase.
- [ ] Checklist items are inlined verbatim.
- [ ] Coverage reporting marks each rule `COVERED` or `MISSING`, then reports coverage percentage and missing rules.

## 4. Context Completeness
- [ ] The target workflow is opened and scanned for navigation directives.
- [ ] All `ALWAYS open`, `OPEN and follow`, and `ALWAYS open and follow` directives are processed.
- [ ] The loaded-file manifest is recorded and reported.
- [ ] `cpt info` or `cpt resolve-vars` is executed.
- [ ] All `{variable}` references resolve to absolute paths.
- [ ] No unresolved `{...}` patterns remain outside code fences.
- [ ] Rules inline MUST and MUST NOT content from `rules.md`.
- [ ] `Prerequisites`, `Tasks`, and `Next Steps` are stripped from Rules.
- [ ] Assigned `checklist.md` criteria and `template.md` sections are inlined in Input.
- [ ] Examples are excerpted where helpful.
- [ ] No "see rules.md" or "load checklist" path references remain.
- [ ] Project artifacts and source files stay in `input_files`, and intermediate results stay in `inputs`, not inline.
- [ ] Task includes explicit read instructions for every `input_files` and `inputs` entry.

## 5. Phase Independence
- [ ] Each phase is executable without prior Cypilot knowledge.
- [ ] Each phase is executable without reading other phase files.
- [ ] Prior Context summarizes earlier outputs instead of referencing them.
- [ ] Tool commands include full arguments.
- [ ] Producer phases declare `outputs`.
- [ ] Consumer phases declare `inputs`.
- [ ] `outputs` use `out/`.
- [ ] The final phase lists every required prior output.

## 6. Budget Compliance
- [ ] Each phase file is `<=1000` lines.
- [ ] Each phase file targets `<=500` lines.
- [ ] Each Rules section is `<=300` lines.
- [ ] Each Input section is `<=500` lines.
- [ ] Each Task section has `3-10` steps.
- [ ] Execution context is estimated per phase.
- [ ] No phase exceeds `5000` predicted lines.
- [ ] Warning phases (`3001-5000`) are noted.
- [ ] Overflow phases are auto-split before compilation.

## 7. Lifecycle & Handoff
- [ ] User is asked about lifecycle strategy after plan generation.
- [ ] `plan.toml` sets `lifecycle` to `gitignore`, `cleanup`, `archive`, or `manual`.
- [ ] The lifecycle action is implemented.
- [ ] The last phase Output Format includes `ALL PHASES COMPLETE`, the lifecycle strategy reference, and `Continue in this chat? [y/n]`.
- [ ] Every non-final phase includes a single fenced, copy-pasteable next-phase prompt with both the `plan.toml` path and the next phase file path.
- [ ] The user is told to validate before execution, given `/cypilot-analyze` on the plan directory, and offered validation as an explicit next step.

## Validation Procedure
- [ ] Self-validation runs all categories, reports every FAIL with issue and location, computes `passed_items / total_items`, and requires correction before execution if pass rate is below 100%.
- [ ] Plan analysis loads `plan.toml`, all phase files, and source rules/checklist/template for the target kind.
- [ ] Automated checks cover structure, variable resolution, and budget compliance; manual checks cover interaction completeness, verbatim rules coverage, and navigation/context completeness.

## Output Format
```text
Plan Validation: {task-slug}
Plan: {cypilot_path}/.plans/{task-slug}/plan.toml
Phases: {N}
Target: {artifact kind}
Status: PASS | FAIL
### Category Results
| Category | Status | Issues |
|----------|--------|--------|
| 1. Structural | PASS/FAIL | {count} |
| 2. Interactive Questions | PASS/FAIL | {count} |
| 3. Rules Coverage | PASS/FAIL | {count} |
| 4. Context Completeness | PASS/FAIL | {count} |
| 5. Phase Independence | PASS/FAIL | {count} |
| 6. Budget Compliance | PASS/FAIL | {count} |
| 7. Lifecycle & Handoff | PASS/FAIL | {count} |
### Issues Found
**Category {number}: {name}**
- MISSING: {missing item} ({source path}:{line})
### Recommendations
1. {fix missing interaction points}
2. {fix missing rules coverage}
3. {re-compile affected phases}
Pass rate: {passed}/{total} ({percentage}%)
```
