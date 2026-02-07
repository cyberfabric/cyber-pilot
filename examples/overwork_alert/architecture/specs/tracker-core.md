<!-- cpt:#:spec -->
# Spec: Tracker Core

<!-- cpt:id-ref:spec has="task" -->
- [x] - `cpt-overwork-alert-spec-tracker-core`
<!-- cpt:id-ref:spec -->

<!-- cpt:##:context -->
## 1. Spec Context

<!-- cpt:overview -->
### 1. Overview
This spec defines the core background tracking loop: how the daemon measures “active work time” using macOS idle time, how it applies configuration defaults, and how it maintains session-scoped in-memory tracker state.

Key assumptions:
- Idle time is best-effort and may be unavailable on some ticks.
- Accumulated active time is not persisted across daemon restarts.
- Manual reset is implemented via a control command handled in a separate spec.

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
<!-- cpt:overview -->

<!-- cpt:paragraph:purpose -->
### 2. Purpose
Provide deterministic, low-overhead, idle-aware active-time accumulation that downstream specs (notifications and control) can rely on.
<!-- cpt:paragraph:purpose -->

### 3. Actors
<!-- cpt:id-ref:actor -->
- `cpt-overwork-alert-actor-user`
- `cpt-overwork-alert-actor-macos`
<!-- cpt:id-ref:actor -->

### 4. References
<!-- cpt:list:references -->
- Overall Design: [DESIGN.md](../DESIGN.md)
- ADRs: `cpt-overwork-alert-adr-cli-daemon-launchagent-no-menubar`
- Related spec: notifications.md
<!-- cpt:list:references -->
<!-- cpt:##:context -->

<!-- cpt:##:flows -->
## 2. Actor Flows

<!-- cpt:###:flow-title repeat="many" -->
### Run tracking tick loop

<!-- cpt:id:flow has="task" to_code="true" -->
- [x] **ID**: `cpt-overwork-alert-spec-tracker-core-flow-tick-loop`

**Actors**:
<!-- cpt:id-ref:actor -->
- `cpt-overwork-alert-actor-macos`
<!-- cpt:id-ref:actor -->

<!-- cpt:cdsl:flow-steps -->
1. [x] - `p1` - Daemon loads effective configuration (defaults + validation) - `inst-load-config`
2. [x] - `p1` - **IF** last_tick_at is not set: set last_tick_at=now and **RETURN** (no accumulation) - `inst-init-first-tick`
3. [x] - `p1` - Daemon reads current idle time sample from macOS - `inst-read-idle`
4. [x] - `p1` - **IF** idle time is unavailable: set last_tick_at=now and **RETURN** (no accumulation) - `inst-handle-idle-unavailable`
5. [x] - `p1` - **IF** idle_seconds >= idle_threshold_seconds: set last_tick_at=now and **RETURN** (paused by idle) - `inst-skip-on-idle`
6. [x] - `p1` - **IF** tracker status is paused: set last_tick_at=now and **RETURN** (no accumulation) - `inst-skip-on-paused`
7. [x] - `p1` - Algorithm: update active_time_seconds using `cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time` - `inst-accumulate`
8. [x] - `p1` - **RETURN** updated TrackerState - `inst-return-state`
<!-- cpt:cdsl:flow-steps -->
<!-- cpt:id:flow -->
<!-- cpt:###:flow-title repeat="many" -->

<!-- cpt:##:flows -->

<!-- cpt:##:algorithms -->
## 3. Algorithms

<!-- cpt:###:algo-title repeat="many" -->
### Accumulate active time

<!-- cpt:id:algo has="task" to_code="true" -->
- [x] **ID**: `cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time`

<!-- cpt:cdsl:algo-steps -->
1. [x] - `p1` - Compute raw delta_seconds = now - last_tick_at - `inst-compute-delta`
2. [x] - `p1` - **IF** delta_seconds < 0 set delta_seconds = 0 - `inst-handle-negative-delta`
3. [x] - `p1` - Compute max_tick_delta_seconds = tick_interval_seconds * 2 - `inst-compute-max-delta`
4. [x] - `p1` - Clamp delta_seconds to max_tick_delta_seconds - `inst-clamp-delta`
5. [x] - `p1` - Add delta_seconds to active_time_seconds - `inst-add-delta`
6. [x] - `p1` - Update last_tick_at to now - `inst-update-last-tick`
7. [x] - `p1` - **RETURN** updated TrackerState - `inst-return-updated-state`
<!-- cpt:cdsl:algo-steps -->
<!-- cpt:id:algo -->
<!-- cpt:###:algo-title repeat="many" -->

<!-- cpt:##:algorithms -->

<!-- cpt:##:states -->
## 4. States

<!-- cpt:###:state-title repeat="many" -->
### Tracker runtime status

<!-- cpt:id:state has="task" to_code="true" -->
- [x] **ID**: `cpt-overwork-alert-spec-tracker-core-state-tracker-status`

<!-- cpt:cdsl:state-transitions -->
1. [x] - `p1` - **FROM** RUNNING **TO** PAUSED **WHEN** user sends pause command - `inst-transition-pause`
2. [x] - `p1` - **FROM** PAUSED **TO** RUNNING **WHEN** user sends resume command - `inst-transition-resume`
<!-- cpt:cdsl:state-transitions -->
<!-- cpt:id:state -->
<!-- cpt:###:state-title repeat="many" -->

<!-- cpt:##:states -->

<!-- cpt:##:requirements -->
## 5. Definition of Done

<!-- cpt:###:req-title repeat="many" -->
### Idle-aware active-time accumulation

<!-- cpt:id:req has="priority,task" to_code="true" -->
- [x] `p1` - **ID**: `cpt-overwork-alert-spec-tracker-core-req-idle-aware-accumulation`

<!-- cpt:paragraph:req-body -->
When the daemon is running, active time increases only while the user is not idle beyond the configured threshold. When the user is idle beyond the threshold, accumulation does not increase.
<!-- cpt:paragraph:req-body -->

**Implementation details**:
<!-- cpt:list:req-impl -->
- Component: `cpt-overwork-alert-component-daemon`
- Component: `cpt-overwork-alert-component-idle-detector`
- Data: `cpt-overwork-alert-dbtable-tracker-state`
<!-- cpt:list:req-impl -->

**Implements**:
<!-- cpt:id-ref:flow has="priority" -->
- `p1` - `cpt-overwork-alert-spec-tracker-core-flow-tick-loop`
<!-- cpt:id-ref:flow -->

<!-- cpt:id-ref:algo has="priority" -->
- `p1` - `cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time`
<!-- cpt:id-ref:algo -->

**Covers (PRD)**:
<!-- cpt:id-ref:fr -->
- `cpt-overwork-alert-fr-track-active-time`
- `cpt-overwork-alert-fr-configurable-limit`
<!-- cpt:id-ref:fr -->

<!-- cpt:id-ref:nfr -->
- `cpt-overwork-alert-nfr-low-overhead`
- `cpt-overwork-alert-nfr-privacy-local-only`
<!-- cpt:id-ref:nfr -->

**Covers (DESIGN)**:
<!-- cpt:id-ref:principle -->
- `cpt-overwork-alert-principle-local-only-minimal-state`
- `cpt-overwork-alert-principle-low-overhead`
<!-- cpt:id-ref:principle -->

<!-- cpt:id-ref:constraint -->
- `cpt-overwork-alert-constraint-no-auto-reset-no-persist`
<!-- cpt:id-ref:constraint -->

<!-- cpt:id-ref:component -->
- `cpt-overwork-alert-component-daemon`
- `cpt-overwork-alert-component-idle-detector`
- `cpt-overwork-alert-component-config-loader`
<!-- cpt:id-ref:component -->

<!-- cpt:id-ref:seq -->
- `cpt-overwork-alert-seq-run-and-alert`
<!-- cpt:id-ref:seq -->

<!-- cpt:id-ref:dbtable -->
- `cpt-overwork-alert-dbtable-tracker-state`
- `cpt-overwork-alert-dbtable-config`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:req -->
<!-- cpt:###:req-title repeat="many" -->

<!-- cpt:###:req-title repeat="many" -->
### Configuration defaults and validation

<!-- cpt:id:req has="priority,task" to_code="true" -->
- [x] `p1` - **ID**: `cpt-overwork-alert-spec-tracker-core-req-config-defaults`

<!-- cpt:paragraph:req-body -->
If no configuration is present or some configuration values are invalid, the daemon continues operating using safe defaults.
<!-- cpt:paragraph:req-body -->

**Implementation details**:
<!-- cpt:list:req-impl -->
- Component: `cpt-overwork-alert-component-config-loader`
- Data: `cpt-overwork-alert-dbtable-config`
<!-- cpt:list:req-impl -->

**Implements**:
<!-- cpt:id-ref:flow has="priority" -->
- `p1` - `cpt-overwork-alert-spec-tracker-core-flow-tick-loop`
<!-- cpt:id-ref:flow -->

<!-- cpt:id-ref:algo has="priority" -->
- `p1` - `cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time`
<!-- cpt:id-ref:algo -->

**Covers (PRD)**:
<!-- cpt:id-ref:fr -->
- `cpt-overwork-alert-fr-configurable-limit`
<!-- cpt:id-ref:fr -->

<!-- cpt:id-ref:nfr -->
- `cpt-overwork-alert-nfr-privacy-local-only`
<!-- cpt:id-ref:nfr -->

**Covers (DESIGN)**:
<!-- cpt:id-ref:principle -->
- `cpt-overwork-alert-principle-local-only-minimal-state`
<!-- cpt:id-ref:principle -->

<!-- cpt:id-ref:constraint -->
- `cpt-overwork-alert-constraint-no-auto-reset-no-persist`
<!-- cpt:id-ref:constraint -->

<!-- cpt:id-ref:component -->
- `cpt-overwork-alert-component-config-loader`
<!-- cpt:id-ref:component -->

<!-- cpt:id-ref:seq -->
- `cpt-overwork-alert-seq-run-and-alert`
<!-- cpt:id-ref:seq -->

<!-- cpt:id-ref:dbtable -->
- `cpt-overwork-alert-dbtable-config`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:req -->
<!-- cpt:###:req-title repeat="many" -->

<!-- cpt:##:requirements -->

<!-- cpt:##:additional-context -->
## 6. Additional Context (optional)

<!-- cpt:free:context-notes -->
This spec intentionally excludes manual reset, pause/resume, and CLI control details; those are defined in cli-control.md.

TrackerState field expectations (high-level):
- status: RUNNING or PAUSED
- active_time_seconds: monotonically non-decreasing within a session except when reset
- last_tick_at: time of most recent tick observation (updated even when skipping accumulation)

This spec does not define notification delivery. The daemon tick loop may pass the updated TrackerState (and the most recent idle sample) to the notification policy defined in notifications.md.

Out of scope / not applicable (v1):
- No persistence of accumulated time across daemon restarts.
- No network I/O and no telemetry.
- No UI beyond macOS notifications (notification policy defined in notifications.md).
<!-- cpt:free:context-notes -->
<!-- cpt:##:additional-context -->

<!-- cpt:#:spec -->
