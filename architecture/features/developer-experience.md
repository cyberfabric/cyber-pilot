# Feature: Developer Experience


<!-- toc -->

- [1. Feature Context](#1-feature-context)
  - [1. Overview](#1-overview)
  - [2. Purpose](#2-purpose)
  - [3. Actors](#3-actors)
  - [4. References](#4-references)
- [2. Actor Flows (CDSL)](#2-actor-flows-cdsl)
  - [Environment Health Check](#environment-health-check)
  - [Self-Check](#self-check)
  - [Pre-Commit Hooks](#pre-commit-hooks)
  - [TOC Generation](#toc-generation)
  - [Shell Completions](#shell-completions)
- [3. Processes / Business Logic (CDSL)](#3-processes-business-logic-cdsl)
  - [Run Doctor Checks](#run-doctor-checks)
  - [Run Self-Check](#run-self-check)
- [4. States (CDSL)](#4-states-cdsl)
  - [Developer Experience State](#developer-experience-state)
- [5. Definitions of Done](#5-definitions-of-done)
  - [Doctor Command](#doctor-command)
  - [Self-Check Command](#self-check-command)
  - [Pre-Commit Hooks](#pre-commit-hooks-1)
  - [Shell Completions](#shell-completions-1)
- [6. Implementation Modules](#6-implementation-modules)
- [7. Acceptance Criteria](#7-acceptance-criteria)

<!-- /toc -->

- [ ] `p2` - **ID**: `cpt-cypilot-featstatus-developer-experience`

## 1. Feature Context

- [ ] `p2` - `cpt-cypilot-feature-developer-experience`

### 1. Overview

Enhances developer productivity with environment health checks, template QA, git pre-commit hooks, and shell completions. The `self-check` command validates that kit examples pass their own template constraints — ensuring kit integrity. The `doctor` command checks the development environment for required dependencies and configuration issues.

### 2. Purpose

Reduces friction in daily Cypilot usage. `doctor` catches environment issues before they cause cryptic errors. `self-check` catches kit regressions (template/example drift). Hooks enforce validation in CI. Completions improve CLI discoverability. Addresses PRD requirements for template QA (`cpt-cypilot-fr-core-template-qa`), environment diagnostics (`cpt-cypilot-fr-core-doctor`), pre-commit hooks (`cpt-cypilot-fr-core-hooks`), and shell completions (`cpt-cypilot-fr-core-completions`).

### 3. Actors

| Actor | Role in Feature |
|-------|-----------------|
| `cpt-cypilot-actor-user` | Runs `cypilot doctor`, `cypilot self-check`, installs hooks/completions |
| `cpt-cypilot-actor-ci-pipeline` | Runs validation via pre-commit hooks |

### 4. References

- **PRD**: [PRD.md](../PRD.md) — `cpt-cypilot-fr-core-template-qa`, `cpt-cypilot-fr-core-doctor`, `cpt-cypilot-fr-core-hooks`, `cpt-cypilot-fr-core-completions`
- **Design**: [DESIGN.md](../DESIGN.md) — `cpt-cypilot-component-validator`
- **Dependencies**: `cpt-cypilot-feature-traceability-validation`

## 2. Actor Flows (CDSL)

### Environment Health Check

- [ ] `p2` - **ID**: `cpt-cypilot-flow-developer-experience-doctor`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User runs `cypilot doctor` → all checks pass, environment is healthy

**Error Scenarios**:
- Python version too old → FAIL with version requirement
- `gh` CLI not installed → WARN (optional dependency)
- Config corrupted → FAIL with remediation hint

**Steps**:
1. - `p2` - User invokes `cypilot doctor` - `inst-user-doctor`
2. - `p2` - Check Python version (≥ 3.11) - `inst-check-python`
3. - `p2` - Check git availability - `inst-check-git`
4. - `p2` - Check `gh` CLI availability and authentication - `inst-check-gh`
5. - `p2` - Check agent installations - `inst-check-agents`
6. - `p2` - Check config integrity (core.toml, artifacts.toml parseable) - `inst-check-config`
7. - `p2` - **RETURN** health report with pass/fail per check - `inst-return-health`

### Self-Check

- [x] `p1` - **ID**: `cpt-cypilot-flow-developer-experience-self-check`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User runs `cypilot self-check` → all kit examples validate against their templates/constraints
- User runs `cypilot self-check --kit sdlc` → only SDLC kit checked

**Error Scenarios**:
- Example fails template validation → FAIL with specific heading/constraint mismatch details
- constraints.toml missing → ERROR with hint to regenerate

**Steps**:
1. [x] - `p1` - User invokes `cypilot self-check [--kit K] [--verbose]` - `inst-user-self-check`
2. [x] - `p1` - Load artifacts registry and kit metadata - `inst-load-registry`
3. - `p1` - **FOR EACH** kit (or filtered by `--kit`) - `inst-for-each-kit`
   1. - `p1` - Load constraints.toml for the kit - `inst-load-constraints`
   2. - `p1` - **FOR EACH** artifact kind in kit - `inst-for-each-kind`
      1. - `p1` - Validate template against heading constraints - `inst-validate-template`
      2. - `p1` - Validate example against heading constraints - `inst-validate-example`
      3. - `p1` - Check template/example consistency - `inst-check-consistency`
4. [x] - `p1` - **RETURN** self-check report with per-kind results - `inst-return-self-check`

### Pre-Commit Hooks

- [ ] `p3` - **ID**: `cpt-cypilot-flow-developer-experience-hooks`

**Steps**:
1. - `p3` - User invokes `cypilot hook install` - `inst-install-hook`
2. - `p3` - Write pre-commit hook script to `.git/hooks/pre-commit` - `inst-write-hook`
3. - `p3` - Hook runs `cypilot validate` on staged artifact files - `inst-hook-validate`

### TOC Generation

- [x] `p1` - **ID**: `cpt-cypilot-flow-developer-experience-toc`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User runs `cypilot toc <files>` → TOC generated/updated in each file
- User runs `cypilot toc --dry-run <files>` → changes shown without writing

**Error Scenarios**:
- File not found → ERROR per file
- Post-generation validation fails → VALIDATION_FAIL with details

**Steps**:
1. [x] - `p1` - User invokes `cypilot toc <files> [--max-level N] [--indent N] [--dry-run] [--skip-validate]` - `inst-toc-gen-parse-args`
2. [x] - `p1` - **FOR EACH** file - `inst-toc-gen-foreach-file`
   1. [x] - `p1` - Process file: extract headings, generate TOC, insert/update between `<!-- toc -->` markers - `inst-toc-gen-process`
   2. [x] - `p1` - **IF** not dry-run and not skip-validate, validate generated TOC - `inst-toc-gen-validate`
3. [x] - `p1` - **RETURN** JSON: `{status, files_processed, results}` - `inst-toc-gen-return`

### Shell Completions

- [ ] `p3` - **ID**: `cpt-cypilot-flow-developer-experience-completions`

**Steps**:
1. - `p3` - User invokes `cypilot completions install` - `inst-install-completions`
2. - `p3` - Detect shell (bash/zsh/fish) and write completion script - `inst-write-completions`

## 3. Processes / Business Logic (CDSL)

### Run Doctor Checks

- [ ] `p2` - **ID**: `cpt-cypilot-algo-developer-experience-doctor`

1. - `p2` - Check `python3 --version` ≥ 3.11 - `inst-check-python-version`
2. - `p2` - Check `git --version` available - `inst-check-git-version`
3. - `p2` - Check `gh --version` and `gh auth status` - `inst-check-gh-status`
4. - `p2` - Check Cypilot installation: `.core/`, `.gen/`, `config/` exist - `inst-check-installation`
5. - `p2` - Attempt to parse `core.toml` and `artifacts.toml` - `inst-check-parseable`

### Run Self-Check

- [x] `p1` - **ID**: `cpt-cypilot-algo-developer-experience-self-check`

1. - `p1` - Load constraints.toml for each kit - `inst-load-kit-constraints`
2. [x] - `p1` - For each artifact kind, locate template and example paths - `inst-locate-files`
3. [x] - `p1` - Validate template headings match constraints heading contract - `inst-validate-headings`
4. - `p1` - Validate example headings match constraints heading contract - `inst-validate-example-headings`
5. - `p1` - Check that template defines all required ID kinds from constraints - `inst-check-id-kinds`

## 4. States (CDSL)

### Developer Experience State

No feature-specific state machines. Self-check is stateless (run → report).

## 5. Definitions of Done

### Doctor Command

- [ ] `p2` - **ID**: `cpt-cypilot-dod-developer-experience-doctor`

- [ ] - `p2` - `cypilot doctor` checks Python, git, gh CLI, config integrity
- [ ] - `p2` - Each check reports pass/fail with actionable remediation
- [ ] - `p2` - Exit code 0 if all checks pass, 2 if any fail

### Self-Check Command

- [x] `p1` - **ID**: `cpt-cypilot-dod-developer-experience-self-check`

- [x] - `p1` - `cypilot self-check` validates all kit examples against their templates/constraints
- [x] - `p1` - `--kit` flag filters to a single kit
- [x] - `p1` - Reports per-kind pass/fail with specific issues
- [x] - `p1` - Integrated into `cypilot validate` as a fail-fast pre-check

### Pre-Commit Hooks

- [ ] `p3` - **ID**: `cpt-cypilot-dod-developer-experience-hooks`

- [ ] - `p3` - `cypilot hook install` writes pre-commit hook
- [ ] - `p3` - `cypilot hook uninstall` removes pre-commit hook
- [ ] - `p3` - Hook only validates staged artifact files

### Shell Completions

- [ ] `p3` - **ID**: `cpt-cypilot-dod-developer-experience-completions`

- [ ] - `p3` - `cypilot completions install` writes shell-appropriate completion script
- [ ] - `p3` - Supports bash, zsh, and fish

## 6. Implementation Modules

| Module | Path | Responsibility |
|--------|------|----------------|
| Self-Check Command | `skills/.../commands/self_check.py` | Kit example validation against templates/constraints |
| TOC Command | `skills/.../commands/toc.py` | CLI wrapper for TOC generation |
| TOC Utils | `skills/.../utils/toc.py` | Unified TOC generation, anchor slugs, code block awareness |

## 7. Acceptance Criteria

- [x] `cypilot self-check` validates kit integrity and reports per-kind results
- [ ] `cypilot doctor` reports environment health with pass/fail per check
- [ ] Pre-commit hooks enforce validation on staged artifacts
- [ ] Shell completions work for all documented commands
