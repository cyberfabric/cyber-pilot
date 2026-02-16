# Feature: Agent Compliance

- [ ] `p1` - **ID**: `cpt-cypilot-featstatus-agent-compliance`

- [x] - `cpt-cypilot-feature-agent-compliance`

## 1. Feature Context

### 1. Overview
This feature defines quality and compliance rules for agents operating on Cypilot artifacts and workflows.

### 2. Purpose
Prevent common anti-patterns and enforce evidence/traceability requirements.

### 3. Actors
- `cpt-cypilot-actor-ai-assistant`

### 4. References
- Overall Design: [DESIGN.md](../DESIGN.md)

## 2. Actor Flows (CDSL)

### Enforce agent compliance during workflows

- [ ] `p2` - **ID**: `cpt-cypilot-flow-agent-compliance-enforce-during-workflows`

1. [ ] - `p1` - Agent starts a workflow that produces or modifies an artifact - `inst-start-workflow`
2. [ ] - `p1` - Agent loads applicable kit templates and constraints - `inst-load-constraints`
3. [ ] - `p1` - Agent produces changes and runs deterministic validation - `inst-run-validation`
4. [ ] - `p1` - **IF** validation fails: **RETURN** actionable error list - `inst-return-errors`
5. [ ] - `p1` - **RETURN** compliant output - `inst-return-ok`

## 3. Processes / Business Logic (CDSL)

### Compliance check for artifact change

- [ ] `p2` - **ID**: `cpt-cypilot-algo-agent-compliance-check-artifact-change`

1. [ ] - `p1` - Identify modified artifacts and affected sections - `inst-identify-scope`
2. [ ] - `p1` - Apply heading and identifier scoping rules - `inst-apply-heading-rules`
3. [ ] - `p1` - Apply cross-artifact reference coverage rules - `inst-apply-coverage-rules`
4. [ ] - `p1` - **RETURN** pass/fail with remediation guidance - `inst-return-result`

## 4. States (CDSL)

### Compliance status state machine

- [ ] `p2` - **ID**: `cpt-cypilot-state-agent-compliance-status`

1. [ ] - `p1` - **FROM** UNKNOWN **TO** COMPLIANT **WHEN** all validations pass - `inst-to-compliant`
2. [ ] - `p1` - **FROM** UNKNOWN **TO** NON_COMPLIANT **WHEN** any validation fails - `inst-to-non-compliant`
3. [ ] - `p1` - **FROM** NON_COMPLIANT **TO** COMPLIANT **WHEN** issues are fixed and validation passes - `inst-remediate`

## 5. Definitions of Done

### Compliance rules are defined and enforceable

- [x] `p1` - **ID**: `cpt-cypilot-dod-agent-compliance`

Compliance rules exist for common failure modes and are consistently applied during workflows.

## 6. Acceptance Criteria

- [ ] Agents run deterministic validation after modifying artifacts.
- [ ] Agents do not introduce IDs outside scoped heading sections.
