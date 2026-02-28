# Feature: Spec Coverage


<!-- toc -->

- [1. Feature Context](#1-feature-context)
  - [1. Overview](#1-overview)
  - [2. Purpose](#2-purpose)
  - [3. Actors](#3-actors)
  - [4. References](#4-references)
- [2. Actor Flows (CDSL)](#2-actor-flows-cdsl)
  - [Run Spec Coverage Report](#run-spec-coverage-report)
  - [Reverse-Engineer Feature Specs](#reverse-engineer-feature-specs)
- [3. Processes / Business Logic (CDSL)](#3-processes-business-logic-cdsl)
  - [Scan Code Coverage](#scan-code-coverage)
  - [Calculate Coverage Metrics](#calculate-coverage-metrics)
  - [Calculate Granularity Score](#calculate-granularity-score)
  - [Generate Coverage Report](#generate-coverage-report)
  - [Place CDSL Markers](#place-cdsl-markers)
- [4. States (CDSL)](#4-states-cdsl)
  - [Coverage Report Lifecycle](#coverage-report-lifecycle)
- [5. Definitions of Done](#5-definitions-of-done)
  - [Coverage Percentage Metric](#coverage-percentage-metric)
  - [Granularity Quality Metric](#granularity-quality-metric)
  - [Coverage Report Output](#coverage-report-output)
- [6. Implementation Modules](#6-implementation-modules)
- [7. Acceptance Criteria](#7-acceptance-criteria)

<!-- /toc -->

- [ ] `p1` - **ID**: `cpt-cypilot-featstatus-spec-coverage`

## 1. Feature Context

- [x] `p1` - `cpt-cypilot-feature-spec-coverage`

### 1. Overview

Measures how much of a project's codebase is covered by CDSL specification markers (`@cpt-*`), analogous to test coverage reports. Produces two metrics: **coverage percentage** (ratio of spec-covered lines to total lines) and **granularity score** (instruction density — approximately 1 instruction per 10 lines of code). The command outputs a machine-readable JSON report similar to standard `coverage.py` reports, with per-file and summary statistics.

### 2. Purpose

Without spec coverage, teams have no visibility into which parts of the codebase are formally specified and traceable. A file with only a scope marker at the top and bottom appears "covered" but provides no meaningful traceability. The granularity metric catches this anti-pattern by measuring instruction density. Addresses the need for quantitative spec quality assessment beyond binary PASS/FAIL validation.

### 3. Actors

| Actor | Role in Feature |
|-------|-----------------|
| `cpt-cypilot-actor-user` | Invokes `cypilot spec-coverage` from CLI to generate coverage report |
| `cpt-cypilot-actor-ai-agent` | Uses coverage report to identify unspecified code during reverse-engineering |
| `cpt-cypilot-actor-ci-pipeline` | Runs spec-coverage as a CI gate to enforce minimum coverage thresholds |

### 4. References

- **PRD**: [PRD.md](../PRD.md) — `cpt-cypilot-fr-core-traceability`, `cpt-cypilot-fr-core-cdsl`
- **Design**: [DESIGN.md](../DESIGN.md) — `cpt-cypilot-component-traceability-engine`, `cpt-cypilot-component-validator`
- **Dependencies**: `cpt-cypilot-feature-traceability-validation`

## 2. Actor Flows (CDSL)

### Run Spec Coverage Report

- [x] `p1` - **ID**: `cpt-cypilot-flow-spec-coverage-report`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User runs `cypilot spec-coverage` → all registered codebase files scanned, coverage report generated with per-file and summary statistics
- User runs `cypilot spec-coverage --min-coverage 80` → same as above, exit code 2 if coverage below threshold
- User runs `cypilot spec-coverage --min-granularity 0.7` → same as above, exit code 2 if granularity below threshold

**Error Scenarios**:
- No codebase entries registered → ERROR with hint to configure artifacts.toml
- No code files found → report with 0% coverage

**Steps**:
1. [x] - `p1` - User invokes `cypilot spec-coverage [--min-coverage N] [--min-granularity N] [--verbose]` - `inst-user-spec-coverage`
2. [x] - `p1` - Load project context: cypilot config, registry, systems, codebase entries - `inst-load-context`
3. [x] - `p1` - Resolve all code files from registered codebase entries - `inst-resolve-code-files`
4. [x] - `p1` - **FOR EACH** code file, scan for `@cpt-*` markers using `cpt-cypilot-algo-spec-coverage-scan` - `inst-foreach-file`
5. [x] - `p1` - Calculate coverage metrics using `cpt-cypilot-algo-spec-coverage-metrics` - `inst-calc-metrics`
6. [x] - `p1` - Calculate granularity scores using `cpt-cypilot-algo-spec-coverage-granularity` - `inst-calc-granularity`
7. [x] - `p1` - Generate report using `cpt-cypilot-algo-spec-coverage-report` - `inst-gen-report`
8. [x] - `p1` - **IF** `--min-coverage` set AND coverage < threshold → exit code 2 - `inst-if-threshold`
9. [x] - `p1` - **RETURN** JSON report (summary, per-file stats, uncovered files) - `inst-return-report`

### Reverse-Engineer Feature Specs

- [ ] `p2` - **ID**: `cpt-cypilot-flow-spec-coverage-reverse-engineer`

**Actor**: `cpt-cypilot-actor-ai-agent`

**Success Scenarios**:
- Agent invokes reverse-engineering workflow → unspecified code identified, CDSL markers placed in code, feature specs generated from code structure

**Steps**:
1. [ ] - `p2` - Agent runs `cypilot spec-coverage` to identify uncovered code - `inst-re-identify-gaps`
2. [ ] - `p2` - Agent analyzes uncovered code to identify logical function groups - `inst-re-analyze-code`
3. [ ] - `p2` - Agent places `@cpt-begin`/`@cpt-end` markers in code with instruction slugs - `inst-re-place-markers`
4. [ ] - `p2` - Agent generates FEATURE spec from placed markers, mapping instructions to CDSL steps - `inst-re-generate-spec`
5. [ ] - `p2` - Agent runs `cypilot validate` to verify consistency between new spec and markers - `inst-re-validate`

## 3. Processes / Business Logic (CDSL)

### Scan Code Coverage

- [x] `p1` - **ID**: `cpt-cypilot-algo-spec-coverage-scan`

**Input**: Code file path, language configuration

**Output**: `{path, total_lines, covered_lines, covered_ranges, markers, block_markers}`

**Steps**:
1. [x] - `p1` - Read file and count total non-blank, non-comment lines (effective lines) - `inst-scan-count-lines`
2. [x] - `p1` - Scan for `@cpt-algo`, `@cpt-flow`, `@cpt-dod` scope markers (file-level coverage) - `inst-scan-scope-markers`
3. [x] - `p1` - Scan for `@cpt-begin`/`@cpt-end` block markers (range-level coverage) - `inst-scan-block-markers`
4. [x] - `p1` - Calculate covered line ranges: lines between block marker pairs are covered; file-level scope markers cover all lines - `inst-scan-calc-ranges`
5. [x] - `p1` - **RETURN** file coverage record with ranges and marker counts - `inst-scan-return`

### Calculate Coverage Metrics

- [x] `p1` - **ID**: `cpt-cypilot-algo-spec-coverage-metrics`

**Input**: List of per-file coverage records

**Output**: `{total_lines, covered_lines, coverage_pct, per_file_coverage}`

**Steps**:
1. [x] - `p1` - Sum total effective lines across all files - `inst-metrics-sum-total`
2. [x] - `p1` - Sum covered lines across all files - `inst-metrics-sum-covered`
3. [x] - `p1` - Calculate overall coverage percentage: `covered / total * 100` - `inst-metrics-calc-pct`
4. [x] - `p1` - **RETURN** metrics with per-file breakdown - `inst-metrics-return`

### Calculate Granularity Score

- [x] `p1` - **ID**: `cpt-cypilot-algo-spec-coverage-granularity`

**Input**: List of per-file coverage records

**Output**: `{granularity_score, per_file_granularity, flagged_files}`

A file with good granularity has approximately 1 CDSL instruction (`@cpt-begin`/`@cpt-end` block) per 10 lines of code. Files with only scope markers at file level (no block markers) get a granularity score of 0 even if nominally 100% covered. This prevents the anti-pattern of wrapping an entire file with a single begin/end pair.

**Steps**:
1. [x] - `p1` - **FOR EACH** covered file - `inst-gran-foreach`
2. [x] - `p1` - Count block marker pairs (instruction-level markers) in file - `inst-gran-count-blocks`
3. [x] - `p1` - Calculate ideal block count: `effective_lines / 10` - `inst-gran-ideal`
4. [x] - `p1` - Calculate file granularity: `min(1.0, actual_blocks / ideal_blocks)` — capped at 1.0 - `inst-gran-calc`
5. [x] - `p1` - Flag files where granularity < 0.5 (fewer than 1 instruction per 20 lines) - `inst-gran-flag`
6. [x] - `p1` - Calculate overall granularity: weighted average across covered files (weighted by line count) - `inst-gran-overall`
7. [x] - `p1` - **RETURN** granularity scores with flagged files - `inst-gran-return`

### Generate Coverage Report

- [x] `p1` - **ID**: `cpt-cypilot-algo-spec-coverage-report`

**Input**: Coverage metrics, granularity scores, verbosity flag

**Output**: JSON report matching `coverage.py` structure

**Steps**:
1. [x] - `p1` - Build summary section: total files, covered files, coverage %, granularity score - `inst-report-summary`
2. [x] - `p1` - Build per-file section: path, total lines, covered lines, coverage %, granularity, uncovered ranges - `inst-report-per-file`
3. [x] - `p1` - **IF** verbose, include marker details per file - `inst-report-verbose`
4. [x] - `p1` - **RETURN** formatted JSON report - `inst-report-return`

### Place CDSL Markers

- [ ] `p2` - **ID**: `cpt-cypilot-algo-spec-coverage-place-markers`

**Input**: Code file path, target algo/flow ID, function boundaries

**Output**: Modified code file with `@cpt-begin`/`@cpt-end` markers inserted

**Steps**:
1. [ ] - `p2` - Parse code file to identify function/method boundaries - `inst-place-parse`
2. [ ] - `p2` - Generate instruction slugs from function names (kebab-case) - `inst-place-slugs`
3. [ ] - `p2` - Insert `@cpt-begin` before function body and `@cpt-end` after function body - `inst-place-insert`
4. [ ] - `p2` - **RETURN** list of placed markers with file path and line numbers - `inst-place-return`

## 4. States (CDSL)

### Coverage Report Lifecycle

- [ ] `p1` - **ID**: `cpt-cypilot-state-spec-coverage-report`

**States**: NOT_RUN, COVERED, PARTIAL, UNCOVERED

**Transitions**:
1. [ ] - `p1` - **FROM** NOT_RUN **TO** COVERED **WHEN** coverage ≥ threshold AND granularity ≥ threshold - `inst-state-covered`
2. [ ] - `p1` - **FROM** NOT_RUN **TO** PARTIAL **WHEN** coverage > 0 but below threshold OR granularity below threshold - `inst-state-partial`
3. [ ] - `p1` - **FROM** NOT_RUN **TO** UNCOVERED **WHEN** no CDSL markers found in any code file - `inst-state-uncovered`

## 5. Definitions of Done

### Coverage Percentage Metric

- [x] `p1` - **ID**: `cpt-cypilot-dod-spec-coverage-percentage`

The system **MUST** calculate what percentage of effective code lines (non-blank, non-comment) are within the scope of at least one CDSL marker. Lines between `@cpt-begin`/`@cpt-end` pairs are covered. Lines in files with only scope markers (`@cpt-algo`, `@cpt-flow`) are covered at file level. The metric **MUST** be reported as a float 0.0–100.0.

**Implements**:
- `cpt-cypilot-algo-spec-coverage-scan`
- `cpt-cypilot-algo-spec-coverage-metrics`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-traceability`

**Covers (DESIGN)**:
- `cpt-cypilot-component-traceability-engine`

### Granularity Quality Metric

- [x] `p1` - **ID**: `cpt-cypilot-dod-spec-coverage-granularity`

The system **MUST** calculate instruction density per covered file: `min(1.0, block_marker_count / (effective_lines / 10))`. Files with only scope markers and no block markers **MUST** receive granularity 0.0. The overall granularity **MUST** be the line-weighted average across covered files. Files with granularity < 0.5 **MUST** be flagged in the report.

**Implements**:
- `cpt-cypilot-algo-spec-coverage-granularity`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-cdsl`

**Covers (DESIGN)**:
- `cpt-cypilot-component-traceability-engine`

### Coverage Report Output

- [x] `p1` - **ID**: `cpt-cypilot-dod-spec-coverage-report`

The system **MUST** output a JSON report with: summary (total files, covered files, coverage %, granularity score), per-file statistics (path, total lines, covered lines, coverage %, granularity, uncovered line ranges), and list of completely uncovered files. The report format **MUST** mirror `coverage.py` JSON output structure. Exit code 0 when above thresholds, 2 when below.

**Implements**:
- `cpt-cypilot-flow-spec-coverage-report`
- `cpt-cypilot-algo-spec-coverage-report`

**Covers (PRD)**:
- `cpt-cypilot-fr-core-traceability`

**Covers (DESIGN)**:
- `cpt-cypilot-component-validator`

## 6. Implementation Modules

| Module | Path | Responsibility |
|--------|------|----------------|
| Spec Coverage Command | `skills/.../commands/spec_coverage.py` | CLI entry point, argument parsing, threshold checks |
| Coverage Scanner | `skills/.../utils/coverage.py` | Code file scanning, line counting, marker detection |
| Coverage Metrics | `skills/.../utils/coverage.py` | Coverage % and granularity calculation |
| Report Generator | `skills/.../utils/coverage.py` | JSON report assembly |
| Codebase Utils | `skills/.../utils/codebase.py` | Existing code scanning infrastructure (reused) |
| Language Config | `skills/.../utils/language_config.py` | Language-specific comment patterns (reused) |

## 7. Acceptance Criteria

- [ ] `cypilot spec-coverage` scans all registered codebase files and produces JSON report
- [ ] Coverage percentage correctly identifies lines within `@cpt-begin`/`@cpt-end` blocks
- [ ] Scope-only files (no block markers) are reported with granularity 0.0
- [ ] Granularity metric correctly penalizes files with few instructions relative to their size
- [ ] `--min-coverage N` flag causes exit code 2 when coverage is below threshold
- [ ] `--min-granularity N` flag causes exit code 2 when granularity is below threshold
- [ ] `--verbose` flag includes per-file marker details in report
- [ ] Report format mirrors `coverage.py` JSON structure (summary + per-file)
- [ ] Scanning completes in ≤ 5 seconds for typical repositories
- [ ] All output is valid JSON to stdout with exit codes 0/1/2
