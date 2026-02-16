# Feature: Cypilot CLI Tool

- [x] `p1` - **ID**: `cpt-cypilot-featstatus-cypilot-cli`

- [x] - `cpt-cypilot-feature-cypilot-cli`

## 1. Feature Context

### 1. Overview
This feature defines the deterministic CLI surface for validating artifacts and traceability.

### 2. Purpose
Provide machine-readable validation reports and utility commands for artifact navigation.

### 3. Actors
- `cpt-cypilot-actor-developer`

### 4. References
- Overall Design: [DESIGN.md](../DESIGN.md)

## 2. Actor Flows

### Primary flow

The user (or CI) runs `cypilot validate` against a target artifact and receives a deterministic JSON report.

## 3. Processes / Business Logic

### Validation execution

Perform artifact discovery, parse constraints, scan IDs, and emit a structured ValidationResult.

## 4. States

### N/A

The CLI is stateless; it executes commands and returns results.

## 5. Definitions of Done

### CLI validates artifacts deterministically

- [x] `p1` - **ID**: `cpt-cypilot-dod-cypilot-cli`

CLI commands produce deterministic results for the same inputs and report failures in a structured format.

## 6. Acceptance Criteria

- [ ] `make validate` passes and produces stable JSON output
- [ ] Error messages include path + line for every violation
