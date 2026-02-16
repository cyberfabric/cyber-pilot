# Feature: Kit Packages

- [x] `p1` - **ID**: `cpt-cypilot-featstatus-rules-packages`

- [x] - `cpt-cypilot-feature-rules-packages`

## 1. Feature Context

### 1. Overview
This feature defines how kits provide templates, rules, checklists, and examples for each artifact kind.

### 2. Purpose
Standardize artifact authoring and validation through reusable kit packages.

### 3. Actors
- `cpt-cypilot-actor-architect`

### 4. References
- Overall Design: [DESIGN.md](../DESIGN.md)

## 2. Actor Flows

### Primary flow

Kit packages are consumed by workflows and validators to load templates, checklists, rules, and examples.

## 3. Processes / Business Logic

### Package resolution

Resolve a kit package path, then load the template + associated files.

## 4. States

### N/A

Kit packages are static documentation packages.

## 5. Definitions of Done

### Kits provide consistent artifacts

- [x] `p1` - **ID**: `cpt-cypilot-dod-rules-packages`

Templates, rules, and checklists exist for supported artifact kinds and are consistent with constraints.

## 6. Acceptance Criteria

- [ ] Templates, rules, checklists, and examples load deterministically
- [ ] `make validate` passes after adding a new kit package
