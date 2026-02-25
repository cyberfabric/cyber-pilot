# Feature: SDLC Kit & Artifact Pipeline

- [ ] `p1` - **ID**: `cpt-cypilot-featstatus-sdlc-kit`

## 1. Feature Context

- [ ] `p1` - `cpt-cypilot-feature-sdlc-kit`

### 1.1 Overview

The SDLC kit delivers the primary domain content for Cypilot — blueprint `.md` files defining PRD, DESIGN, ADR, DECOMPOSITION, and FEATURE artifact kinds, plus a codebase blueprint for code review. Each blueprint uses `@cpt:` markers that the Blueprint Processor transforms into templates, rules, checklists, examples, and kit-wide constraints. The kit also provides pipeline guides (greenfield, brownfield, monolith) and a self-check command for verifying kit integrity.

### 1.2 Purpose

Without SDLC-specific content, Cypilot is a generic ID system with no domain value. This kit provides the artifact-first development methodology — PRD → DESIGN → ADR → DECOMPOSITION → FEATURE → CODE — that is Cypilot's primary use case. Addresses PRD requirements for an artifact pipeline (`cpt-cypilot-fr-sdlc-pipeline`) and an SDLC blueprint package (`cpt-cypilot-fr-sdlc-plugin`).

### 1.3 Actors

| Actor | Role in Feature |
|-------|-----------------|
| `cpt-cypilot-actor-user` | Authors and customizes blueprints, runs self-check, follows pipeline guides |
| `cpt-cypilot-actor-ai-agent` | Generates artifacts using kit templates/rules/checklists, follows pipeline ordering |
| `cpt-cypilot-actor-cypilot-cli` | Executes self-check validation, resolves pipeline context |

### 1.4 References

- **PRD**: [PRD.md](../PRD.md) — `cpt-cypilot-fr-sdlc-pipeline`, `cpt-cypilot-fr-sdlc-plugin`
- **Design**: [DESIGN.md](../DESIGN.md) — `cpt-cypilot-component-sdlc-plugin`
- **Dependencies**: `cpt-cypilot-feature-blueprint-system`, `cpt-cypilot-feature-traceability-validation`

## 2. Actor Flows (CDSL)

### Artifact Pipeline Guidance

- [ ] `p1` - **ID**: `cpt-cypilot-flow-sdlc-kit-pipeline`

**Actor**: `cpt-cypilot-actor-ai-agent`

**Success Scenarios**:
- Agent determines which artifact to generate next based on existing artifacts → suggests correct `cypilot generate <KIND>` command
- Greenfield project: agent starts with PRD, then DESIGN, then ADR/DECOMPOSITION/FEATURE
- Brownfield project: agent starts with reverse-engineering, then generates DESIGN from existing code

**Error Scenarios**:
- No system registered in `artifacts.toml` → error with hint to run `cypilot init`
- Kit not installed → error with hint to install SDLC kit

**Steps**:
1. [ ] - `p1` - Agent invokes pipeline guidance (triggered by generate workflow or user request) - `inst-invoke-pipeline`
2. [ ] - `p1` - Load registered artifacts for the target system from `artifacts.toml` - `inst-load-artifacts`
3. [ ] - `p1` - Resolve pipeline position using `cpt-cypilot-algo-sdlc-kit-resolve-pipeline` - `inst-resolve-position`
4. [ ] - `p1` - **IF** no artifacts exist - `inst-if-no-artifacts`
   1. [ ] - `p1` - Detect project type: GREENFIELD (no source code) or BROWNFIELD (source code exists) - `inst-detect-project-type`
   2. [ ] - `p1` - **IF** GREENFIELD **RETURN** suggest starting with PRD - `inst-if-greenfield`
   3. [ ] - `p1` - **IF** BROWNFIELD **RETURN** suggest reverse-engineering then DESIGN - `inst-if-brownfield`
5. [ ] - `p1` - **RETURN** next artifact kind to generate with rationale - `inst-return-next`

### Self-Check

- [ ] `p1` - **ID**: `cpt-cypilot-flow-sdlc-kit-self-check`

**Actor**: `cpt-cypilot-actor-user`

**Success Scenarios**:
- User runs `cypilot self-check` → all blueprint outputs verified, PASS with coverage report

**Error Scenarios**:
- Generated outputs missing or stale → FAIL with list of missing/stale files
- Blueprint file has invalid markers → FAIL with marker errors and line numbers

**Steps**:
1. [ ] - `p1` - User invokes `cypilot self-check` - `inst-user-self-check`
2. [ ] - `p1` - Load installed kits from `config/core.toml` - `inst-load-kits`
3. [ ] - `p1` - **FOR EACH** installed kit - `inst-foreach-kit`
   1. [ ] - `p1` - Validate kit completeness using `cpt-cypilot-algo-sdlc-kit-validate-completeness` - `inst-validate-kit`
4. [ ] - `p1` - Aggregate results across all kits - `inst-aggregate-results`
5. [ ] - `p1` - **IF** any kit fails **RETURN** FAIL with per-kit details - `inst-if-fail`
6. [ ] - `p1` - **RETURN** PASS with coverage summary (kits checked, blueprints found, outputs verified) - `inst-return-pass`

## 3. Processes / Business Logic (CDSL)

### Resolve Pipeline Position

- [ ] `p1` - **ID**: `cpt-cypilot-algo-sdlc-kit-resolve-pipeline`

**Input**: List of registered artifacts for a system (paths, kinds, traceability settings)

**Output**: Pipeline status: present artifact kinds, missing artifact kinds, recommended next kind with rationale

**Steps**:
1. [ ] - `p1` - Define pipeline ordering: PRD → DESIGN → ADR → DECOMPOSITION → FEATURE - `inst-define-ordering`
2. [ ] - `p1` - Classify each registered artifact by kind - `inst-classify-artifacts`
3. [ ] - `p1` - Identify present kinds (have at least one registered artifact) and missing kinds - `inst-identify-present-missing`
4. [ ] - `p1` - **FOR EACH** missing kind in pipeline order - `inst-foreach-missing`
   1. [ ] - `p1` - Check if dependencies are satisfied (PRD before DESIGN, DESIGN before FEATURE, etc.) - `inst-check-dependencies`
   2. [ ] - `p1` - **IF** dependencies satisfied **RETURN** this kind as recommended next step - `inst-if-deps-satisfied`
5. [ ] - `p1` - **IF** all kinds present **RETURN** pipeline complete, suggest CODE implementation - `inst-if-all-present`
6. [ ] - `p1` - **RETURN** pipeline status with present, missing, and recommendation - `inst-return-status`

### Validate Kit Completeness

- [ ] `p1` - **ID**: `cpt-cypilot-algo-sdlc-kit-validate-completeness`

**Input**: Kit slug, path to kit's installed directory

**Output**: Validation result: PASS/FAIL with details per blueprint

**Steps**:
1. [ ] - `p1` - Define expected artifact kinds for SDLC kit: PRD, DESIGN, ADR, DECOMPOSITION, FEATURE - `inst-define-expected`
2. [ ] - `p1` - Define expected codebase outputs: `codebase/rules.md`, `codebase/checklist.md` - `inst-define-codebase`
3. [ ] - `p1` - **FOR EACH** expected artifact kind - `inst-foreach-kind`
   1. [ ] - `p1` - Check that output directory `config/kits/{slug}/artifacts/{KIND}/` exists - `inst-check-output-dir`
   2. [ ] - `p1` - Check required files present: `rules.md`, `checklist.md`, `template.md` - `inst-check-required-files`
   3. [ ] - `p1` - **IF** any required file missing, record as FAIL for this kind - `inst-if-missing-file`
4. [ ] - `p1` - Check kit-wide `constraints.json` exists at `config/kits/{slug}/constraints.json` - `inst-check-constraints`
5. [ ] - `p1` - Check codebase outputs exist - `inst-check-codebase`
6. [ ] - `p1` - **IF** any check failed **RETURN** FAIL with list of missing files - `inst-if-any-fail`
7. [ ] - `p1` - **RETURN** PASS with coverage (kinds verified, files checked) - `inst-return-valid`

## 4. States (CDSL)

### Pipeline Position

- [ ] `p1` - **ID**: `cpt-cypilot-state-sdlc-kit-pipeline-position`

**States**: EMPTY, REQUIREMENTS, DESIGNED, DECOMPOSED, SPECIFIED, COMPLETE

**Initial State**: EMPTY

**Transitions**:
1. [ ] - `p1` - **FROM** EMPTY **TO** REQUIREMENTS **WHEN** PRD artifact is registered for the system - `inst-prd-registered`
2. [ ] - `p1` - **FROM** REQUIREMENTS **TO** DESIGNED **WHEN** DESIGN artifact is registered - `inst-design-registered`
3. [ ] - `p1` - **FROM** DESIGNED **TO** DECOMPOSED **WHEN** DECOMPOSITION artifact is registered - `inst-decomposition-registered`
4. [ ] - `p1` - **FROM** DECOMPOSED **TO** SPECIFIED **WHEN** at least one FEATURE artifact is registered - `inst-feature-registered`
5. [ ] - `p1` - **FROM** SPECIFIED **TO** COMPLETE **WHEN** all features in DECOMPOSITION have FEATURE artifacts - `inst-all-features`

> Kit lifecycle state (UNINSTALLED → INSTALLED → OUTDATED) is owned by `cpt-cypilot-feature-blueprint-system` (`cpt-cypilot-state-blueprint-system-kit-install`).

## 5. Definitions of Done

### Blueprint Coverage

- [ ] `p1` - **ID**: `cpt-cypilot-dod-sdlc-kit-blueprint-coverage`

The SDLC kit **MUST** provide blueprint files for all five artifact kinds (PRD, DESIGN, ADR, DECOMPOSITION, FEATURE) and one codebase blueprint. Each blueprint **MUST** use SDLC-specific `@cpt:` markers: `@cpt:blueprint` (identity), `@cpt:heading` (template structure), `@cpt:id` (identifier kinds), `@cpt:check` (checklist items), `@cpt:rule` (rules), `@cpt:prompt` (writing instructions), `@cpt:example` (examples). Each blueprint **MUST** include `@cpt:skill` extensions for AI agent discoverability and `@cpt:workflow` definitions for generate/analyze operations.

**Implements**:
- `cpt-cypilot-flow-sdlc-kit-pipeline`

**Covers (PRD)**:
- `cpt-cypilot-fr-sdlc-plugin`

**Covers (DESIGN)**:
- `cpt-cypilot-component-sdlc-plugin`
- `cpt-cypilot-principle-kit-centric`

### Pipeline Completeness

- [ ] `p1` - **ID**: `cpt-cypilot-dod-sdlc-kit-pipeline`

The SDLC kit **MUST** support the artifact-first pipeline: PRD → DESIGN → ADR → DECOMPOSITION → FEATURE → CODE. Each artifact kind **MUST** be usable independently (no forced sequence). The kit **MUST** support both greenfield (design-first, starting from PRD) and brownfield (code-first, starting from reverse-engineering) projects. Pipeline guides **MUST** exist for greenfield, brownfield, and monolith scenarios.

**Implements**:
- `cpt-cypilot-algo-sdlc-kit-resolve-pipeline`

**Covers (PRD)**:
- `cpt-cypilot-fr-sdlc-pipeline`

**Covers (DESIGN)**:
- `cpt-cypilot-component-sdlc-plugin`
- `cpt-cypilot-principle-dry`

### Generated Output Integrity

- [ ] `p1` - **ID**: `cpt-cypilot-dod-sdlc-kit-output-integrity`

All generated outputs (templates, rules, checklists, examples, constraints) **MUST** correctly reflect the current blueprint content. The Blueprint Processor **MUST** produce: `rules.md` (from `@cpt:rules` + `@cpt:rule`), `checklist.md` (from `@cpt:checklist` + `@cpt:check`), `template.md` (from `@cpt:heading` + `@cpt:prompt`), `example.md` (from `@cpt:heading` examples + `@cpt:example`), and `constraints.json` (from `@cpt:heading` + `@cpt:id`). Codebase blueprint **MUST** produce `codebase/rules.md` and `codebase/checklist.md`.

**Implements**:
- `cpt-cypilot-algo-sdlc-kit-validate-completeness`

**Covers (PRD)**:
- `cpt-cypilot-fr-sdlc-plugin`

**Covers (DESIGN)**:
- `cpt-cypilot-component-sdlc-plugin`
- `cpt-cypilot-constraint-markdown-contract`

### Self-Check Command

- [ ] `p1` - **ID**: `cpt-cypilot-dod-sdlc-kit-self-check`

The system **MUST** provide `cypilot self-check` that validates all installed kits have complete generated outputs matching their blueprints. Output **MUST** be JSON with PASS/FAIL status, per-kit details, and coverage metrics (kinds verified, files checked). Missing or stale outputs **MUST** be reported with file paths and suggested fix commands.

**Implements**:
- `cpt-cypilot-flow-sdlc-kit-self-check`

**Covers (PRD)**:
- `cpt-cypilot-fr-sdlc-pipeline`

**Covers (DESIGN)**:
- `cpt-cypilot-component-sdlc-plugin`

## 6. Acceptance Criteria

- [ ] All 5 artifact blueprints (PRD, DESIGN, ADR, DECOMPOSITION, FEATURE) exist in `kits/sdlc/blueprints/` with correct `@cpt:` markers
- [ ] Codebase blueprint exists and generates `codebase/rules.md` and `codebase/checklist.md`
- [ ] Each blueprint includes `@cpt:skill` extensions and `@cpt:workflow` definitions
- [ ] `cypilot self-check` reports PASS for a correctly installed kit with complete outputs
- [ ] `cypilot self-check` reports FAIL with details when outputs are missing or stale
- [ ] Pipeline guidance correctly identifies greenfield vs brownfield starting points
- [ ] Each artifact kind is usable independently without requiring prior artifact kinds
- [ ] Guides exist for greenfield (`GREENFIELD.md`), brownfield (`BROWNFIELD.md`), and monolith (`MONOLITH.md`) scenarios
- [ ] Generated `constraints.json` aggregates all ID kinds from SDLC blueprints
- [ ] All commands output JSON to stdout and use exit codes 0 (PASS) / 2 (FAIL)
