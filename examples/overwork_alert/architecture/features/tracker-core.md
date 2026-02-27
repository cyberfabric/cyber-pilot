# Feature: Tracker Core


<!-- toc -->

- [1. Feature Context](#1-feature-context)
  - [1. Overview](#1-overview)
  - [2. Purpose](#2-purpose)
  - [3. Actors](#3-actors)
  - [4. References](#4-references)
- [2. Actor Flows (CDSL)](#2-actor-flows-cdsl)
  - [Run tracking tick loop](#run-tracking-tick-loop)
- [3. Processes / Business Logic (CDSL)](#3-processes-business-logic-cdsl)
  - [Accumulate active time](#accumulate-active-time)
- [4. States (CDSL)](#4-states-cdsl)
  - [Tracker runtime status](#tracker-runtime-status)
- [5. Definitions of Done](#5-definitions-of-done)
  - [Idle-aware active-time accumulation](#idle-aware-active-time-accumulation)
  - [Configuration defaults and validation](#configuration-defaults-and-validation)
- [6. Acceptance Criteria](#6-acceptance-criteria)
- [Additional Context (optional)](#additional-context-optional)

<!-- /toc -->

- [x] `p1` - **ID**: `cpt-ex-ovwa-featstatus-tracker-core`

- [x] - `cpt-ex-ovwa-feature-tracker-core`

## 1. Feature Context

### 1. Overview
This feature defines the core background tracking loop: how the daemon measures “active work time” using macOS idle time, how it applies configuration defaults, and how it maintains session-scoped in-memory tracker state.

Key assumptions:
- Idle time is best-effort and may be unavailable on some ticks.
- Accumulated active time is not persisted across daemon restarts.
- Manual reset is implemented via a control command handled in a separate feature.

Configuration parameters (effective defaults in v1):
- limit_seconds: 10800 (3 hours)
- idle_threshold_seconds: 300 (5 minutes)
- repeat_interval_seconds: 1800 (30 minutes)
- tick_interval_seconds: 5
- max_tick_delta_seconds: tick_interval_seconds * 2

Acceptance criteria (timing/behavior):
- When idle exceeds idle_threshold_seconds, accumulation MUST stop within 10 seconds.
- When active work resumes (idle below threshold) and status is RUNNING, accumulation MUST resume on the next tick.

Validation behavior:
- If a configuration value is missing or invalid, the daemon MUST continue using the default.
- The daemon MUST treat time deltas < 0 as 0 seconds.
- The daemon MUST clamp large time deltas to max_tick_delta_seconds (e.g., after sleep/wake) to avoid overcounting.

### 2. Purpose
Provide deterministic, low-overhead, idle-aware active-time accumulation that downstream features (notifications and control) can rely on.

### 3. Actors
- `cpt-ex-ovwa-actor-user`
- `cpt-ex-ovwa-actor-macos`

### 4. References
- Overall Design: [DESIGN.md](../DESIGN.md)
- ADRs: `cpt-ex-ovwa-adr-cli-daemon-launchagent-no-menubar`
- Related feature: notifications.md

## 2. Actor Flows (CDSL)

### Run tracking tick loop

- [x] **ID**: `cpt-ex-ovwa-flow-tracker-core-tick-loop`

**Actors**:
- `cpt-ex-ovwa-actor-macos`

1. [x] - `p1` - Daemon loads effective configuration (defaults + validation) - `inst-load-config`
2. [x] - `p1` - **IF** last_tick_at is not set: set last_tick_at=now and **RETURN** (no accumulation) - `inst-init-first-tick`
3. [x] - `p1` - Daemon reads current idle time sample from macOS - `inst-read-idle`
4. [x] - `p1` - **IF** idle time is unavailable: set last_tick_at=now and **RETURN** (no accumulation) - `inst-handle-idle-unavailable`
5. [x] - `p1` - **IF** idle_seconds >= idle_threshold_seconds: set last_tick_at=now and **RETURN** (paused by idle) - `inst-skip-on-idle`
6. [x] - `p1` - **IF** tracker status is paused: set last_tick_at=now and **RETURN** (no accumulation) - `inst-skip-on-paused`
7. [x] - `p1` - Algorithm: update active_time_seconds using `cpt-ex-ovwa-algo-tracker-core-accumulate-active-time` - `inst-accumulate`
8. [x] - `p1` - **RETURN** updated TrackerState - `inst-return-state`


## 3. Processes / Business Logic (CDSL)

### Accumulate active time

- [x] **ID**: `cpt-ex-ovwa-algo-tracker-core-accumulate-active-time`

1. [x] - `p1` - Compute raw delta_seconds = now - last_tick_at - `inst-compute-delta`
2. [x] - `p1` - **IF** delta_seconds < 0 set delta_seconds = 0 - `inst-handle-negative-delta`
3. [x] - `p1` - Compute max_tick_delta_seconds = tick_interval_seconds * 2 - `inst-compute-max-delta`
4. [x] - `p1` - Clamp delta_seconds to max_tick_delta_seconds - `inst-clamp-delta`
5. [x] - `p1` - Add delta_seconds to active_time_seconds - `inst-add-delta`
6. [x] - `p1` - Update last_tick_at to now - `inst-update-last-tick`
7. [x] - `p1` - **RETURN** updated TrackerState - `inst-return-updated-state`


## 4. States (CDSL)

### Tracker runtime status

- [x] **ID**: `cpt-ex-ovwa-state-tracker-core-tracker-status`

1. [x] - `p1` - **FROM** RUNNING **TO** PAUSED **WHEN** user sends pause command - `inst-transition-pause`
2. [x] - `p1` - **FROM** PAUSED **TO** RUNNING **WHEN** user sends resume command - `inst-transition-resume`


## 5. Definitions of Done

### Idle-aware active-time accumulation

- [x] `p1` - **ID**: `cpt-ex-ovwa-dod-tracker-core-idle-aware-accumulation`

When the daemon is running, active time increases only while the user is not idle beyond the configured threshold. When the user is idle beyond the threshold, accumulation does not increase.

**Implementation details**:
- Component: `cpt-ex-ovwa-component-daemon`
- Component: `cpt-ex-ovwa-component-idle-detector`
- Data: `cpt-ex-ovwa-dbtable-tracker-state`

**Implements**:
- `p1` - `cpt-ex-ovwa-flow-tracker-core-tick-loop`

- `p1` - `cpt-ex-ovwa-algo-tracker-core-accumulate-active-time`

**Covers (PRD)**:
- `cpt-ex-ovwa-fr-track-active-time`
- `cpt-ex-ovwa-fr-configurable-limit`

- `cpt-ex-ovwa-nfr-low-overhead`
- `cpt-ex-ovwa-nfr-privacy-local-only`

**Covers (DESIGN)**:
- `cpt-ex-ovwa-principle-local-only-minimal-state`
- `cpt-ex-ovwa-principle-low-overhead`

- `cpt-ex-ovwa-constraint-no-auto-reset-no-persist`

- `cpt-ex-ovwa-component-daemon`
- `cpt-ex-ovwa-component-idle-detector`
- `cpt-ex-ovwa-component-config-loader`

- `cpt-ex-ovwa-seq-run-and-alert`

- `cpt-ex-ovwa-dbtable-tracker-state`
- `cpt-ex-ovwa-dbtable-config`


### Configuration defaults and validation

- [x] `p1` - **ID**: `cpt-ex-ovwa-dod-tracker-core-config-defaults`

If no configuration is present or some configuration values are invalid, the daemon continues operating using safe defaults.

**Implementation details**:
- Component: `cpt-ex-ovwa-component-config-loader`
- Data: `cpt-ex-ovwa-dbtable-config`

**Implements**:
- `p1` - `cpt-ex-ovwa-flow-tracker-core-tick-loop`

- `p1` - `cpt-ex-ovwa-algo-tracker-core-accumulate-active-time`

**Covers (PRD)**:
- `cpt-ex-ovwa-fr-configurable-limit`

- `cpt-ex-ovwa-nfr-privacy-local-only`

**Covers (DESIGN)**:
- `cpt-ex-ovwa-principle-local-only-minimal-state`

- `cpt-ex-ovwa-constraint-no-auto-reset-no-persist`

- `cpt-ex-ovwa-component-config-loader`

- `cpt-ex-ovwa-seq-run-and-alert`

- `cpt-ex-ovwa-dbtable-config`



## 6. Acceptance Criteria

- [ ] When idle exceeds idle_threshold_seconds, accumulation stops within 10 seconds.
- [ ] When active work resumes (idle below threshold) and status is RUNNING, accumulation resumes on the next tick.
- [ ] Invalid/missing config values fall back to safe defaults without crashing.

## Additional Context (optional)

This feature intentionally excludes manual reset, pause/resume, and CLI control details; those are defined in cli-control.md.

TrackerState field expectations (high-level):
- status: RUNNING or PAUSED
- active_time_seconds: monotonically non-decreasing within a session except when reset
- last_tick_at: time of most recent tick observation (updated even when skipping accumulation)

This feature does not define notification delivery. The daemon tick loop may pass the updated TrackerState (and the most recent idle sample) to the notification policy defined in notifications.md.

Out of scope / not applicable (v1):
- No persistence of accumulated time across daemon restarts.
- No network I/O and no telemetry.
- No UI beyond macOS notifications (notification policy defined in notifications.md).

