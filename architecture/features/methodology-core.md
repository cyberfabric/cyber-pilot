# Feature: Methodology Core

- [ ] `p1` - **ID**: `cpt-cypilot-featstatus-methodology-core`

- [x] - `cpt-cypilot-feature-methodology-core`

## 1. Feature Context

### 1. Overview
This feature defines the core Cypilot methodology primitives that all other features depend on: identifiers, CDSL, and execution protocol.

### 2. Purpose
Provide a stable, reusable foundation for artifact authoring and validation.

### 3. Actors
- `cpt-cypilot-actor-ai-assistant`

### 4. References
- Overall Design: [DESIGN.md](../DESIGN.md)

## 2. Actor Flows (CDSL)

### Author a new artifact with required structure

- [ ] `p2` - **ID**: `cpt-cypilot-flow-methodology-core-author-artifact`

1. [ ] - `p1` - Author creates a new artifact from a kit template - `inst-create-from-template`
2. [ ] - `p1` - Author fills required headings and defines IDs in scoped sections - `inst-fill-headings-ids`
3. [ ] - `p1` - Author runs validation and iterates until no errors - `inst-validate-iterate`
4. [ ] - `p1` - **RETURN** compliant artifact - `inst-return-artifact`

## 3. Processes / Business Logic (CDSL)

### Apply constraints to an artifact document

- [ ] `p2` - **ID**: `cpt-cypilot-algo-methodology-core-apply-constraints`

1. [ ] - `p1` - Load kit constraints for the artifact kind - `inst-load-kit-constraints`
2. [ ] - `p1` - Validate required headings and ordering - `inst-validate-headings`
3. [ ] - `p1` - Validate ID definitions and reference coverage - `inst-validate-ids-refs`
4. [ ] - `p1` - **RETURN** errors/warnings list - `inst-return-findings`

## 4. States (CDSL)

### Validation outcome state machine

- [ ] `p2` - **ID**: `cpt-cypilot-state-methodology-core-validation-outcome`

1. [ ] - `p1` - **FROM** UNKNOWN **TO** VALID **WHEN** validations pass - `inst-to-valid`
2. [ ] - `p1` - **FROM** UNKNOWN **TO** INVALID **WHEN** any validation fails - `inst-to-invalid`
3. [ ] - `p1` - **FROM** INVALID **TO** VALID **WHEN** issues are fixed and validation passes - `inst-remediate`

## 5. Definitions of Done

### Methodology Core is stable and documented

- [x] `p1` - **ID**: `cpt-cypilot-dod-methodology-core`

The methodology primitives are documented and consistent, including identifier formats and the CDSL instruction format.

## 6. Acceptance Criteria

- [ ] FEATURE artifacts include the required sections and validate against heading constraints.
- [ ] ID definitions appear only under the correct scoped headings (e.g., flows under Actor Flows).
