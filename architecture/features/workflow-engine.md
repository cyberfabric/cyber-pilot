# Feature: Workflow Engine

- [ ] `p1` - **ID**: `cpt-cypilot-featstatus-workflow-engine`

- [x] - `cpt-cypilot-feature-workflow-engine`

## 1. Feature Context

### 1. Overview
This feature defines the workflow protocol for generating and validating artifacts through guided steps.

### 2. Purpose
Enable repeatable, structured artifact creation and review.

### 3. Actors
- `cpt-cypilot-actor-ai-assistant`

### 4. References
- Overall Design: [DESIGN.md](../DESIGN.md)

## 2. Actor Flows (CDSL)

### Generate or validate artifact workflow

- [ ] `p2` - **ID**: `cpt-cypilot-flow-workflow-engine-generate-or-validate`

1. [ ] - `p1` - User or agent selects a workflow by intent - `inst-select-workflow`
2. [ ] - `p1` - Workflow validates prerequisites (required artifacts exist or can be bootstrapped) - `inst-validate-prereqs`
3. [ ] - `p1` - Workflow executes steps and produces deterministic outputs - `inst-execute-steps`
4. [ ] - `p1` - Workflow runs deterministic validation and **RETURN** report - `inst-run-validation`

## 3. Processes / Business Logic (CDSL)

### Resolve workflow from context

- [ ] `p2` - **ID**: `cpt-cypilot-algo-workflow-engine-resolve-workflow`

1. [ ] - `p1` - Inspect repository context to infer artifact kind and operation - `inst-inspect-context`
2. [ ] - `p1` - Choose the matching workflow entrypoint - `inst-choose-entrypoint`
3. [ ] - `p1` - **RETURN** workflow path and parameters - `inst-return-workflow`

## 4. States

### Workflow execution lifecycle

- [ ] `p2` - **ID**: `cpt-cypilot-state-workflow-engine-execution-lifecycle`

1. [ ] - `p1` - **FROM** CREATED **TO** VALIDATING **WHEN** prerequisites are checked - `inst-transition-validating`
2. [ ] - `p1` - **FROM** VALIDATING **TO** RUNNING **WHEN** steps begin - `inst-transition-running`
3. [ ] - `p1` - **FROM** RUNNING **TO** DONE **WHEN** outputs and validation report are produced - `inst-transition-done`

## 5. Definitions of Done

### Workflows guide consistent outputs

- [x] `p1` - **ID**: `cpt-cypilot-dod-workflow-engine`

Workflows exist for generating and analyzing artifacts and follow a deterministic execution protocol.

## 6. Acceptance Criteria

- [ ] Workflows exist for generating and validating core artifacts (PRD, DESIGN, ADR, DECOMPOSITION, FEATURE).
- [ ] Each workflow validates prerequisites before execution and produces deterministic validation output.
