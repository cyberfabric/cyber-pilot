# Feature: Adapter System

- [x] `p1` - **ID**: `cpt-cypilot-featstatus-adapter-system`

- [x] - `cpt-cypilot-feature-adapter-system`

## 1. Feature Context

### 1. Overview
This feature defines how a project configures Cypilot via an adapter directory and an artifacts registry.

### 2. Purpose
Enable project-specific configuration without modifying core methodology.

### 3. Actors
- `cpt-cypilot-actor-developer`

### 4. References
- Overall Design: [DESIGN.md](../DESIGN.md)

## 2. Actor Flows

### Primary flow

A technical lead initializes an adapter and the system discovers `artifacts.json` and navigation rules.

## 3. Processes / Business Logic

### Adapter discovery

Locate adapter root, read `AGENTS.md`, parse `artifacts.json`, and expose resolved artifact paths.

## 4. States

### N/A

Adapter configuration is file-based.

## 5. Definitions of Done

### Adapter can be discovered and loaded

- [x] `p1` - **ID**: `cpt-cypilot-dod-adapter-system`

Adapter discovery and artifacts registry loading work deterministically for a project.

## 6. Acceptance Criteria

- [ ] `cypilot adapter-info` returns deterministic results for the same repository state
- [ ] Missing/invalid adapter files are reported with actionable diagnostics
