# Decomposition: Overwork Alert

## 1. Overview

Overwork Alert is decomposed into a small set of features aligned to the system’s major responsibilities: tracking core (idle-aware accumulation and configuration), notification policy and delivery, CLI control + local IPC, and launchd autostart.

**Decomposition Strategy**:
- Group by functional cohesion (each feature implements a coherent responsibility)
- Keep dependencies minimal and explicit (tracker core is the foundation)
- Ensure 100% coverage of DESIGN elements (components, sequences, and data model items assigned)
- Maintain mutual exclusivity (each component/sequence/data element is owned by a single feature)


## 2. Entries

**Overall implementation status:**
- [x] `p1` - **ID**: `cpt-ex-ovwa-status-overall`

### 1. [Tracking Core](features/tracker-core.md) - HIGH

- [x] `p1` - **ID**: `cpt-ex-ovwa-feature-tracker-core`

- **Purpose**: Implement the daemon tracking loop and the idle-aware active-time accumulation model with safe configuration defaults.

- **Depends On**: None

- **Scope**:
  - Load configuration with safe defaults and validation
  - Sample macOS idle time and determine active vs idle
  - Maintain session-scoped in-memory tracker state (no persistence)
  - Accumulate active time only when running and not idle

- **Out of scope**:
  - Persisting accumulated time across restarts
  - Automatic time-of-day resets

- **Requirements Covered**:
  - [x] `p1` - `cpt-ex-ovwa-fr-track-active-time`
  - [x] `p1` - `cpt-ex-ovwa-fr-configurable-limit`
  - [x] `p1` - `cpt-ex-ovwa-nfr-privacy-local-only`
  - [x] `p2` - `cpt-ex-ovwa-nfr-low-overhead`

- **Design Principles Covered**:
  - [x] `p1` - `cpt-ex-ovwa-principle-local-only-minimal-state`
  - [x] `p2` - `cpt-ex-ovwa-principle-low-overhead`

- **Design Constraints Covered**:
  - [x] `p1` - `cpt-ex-ovwa-constraint-no-auto-reset-no-persist`
  - [x] `p1` - `cpt-ex-ovwa-constraint-macos-cli-only`

- **Domain Model Entities**:
  - Config
  - TrackerState
  - IdleSample

- **Design Components**:
  - [x] `p1` - `cpt-ex-ovwa-component-daemon`
  - [x] `p2` - `cpt-ex-ovwa-component-idle-detector`
  - [x] `p2` - `cpt-ex-ovwa-component-config-loader`

- **API**:
  - `overwork-alert start`

- **Sequences**:
  - [x] `p1` - `cpt-ex-ovwa-seq-run-and-alert`

- **Data**:
  - [x] `p2` - `cpt-ex-ovwa-dbtable-tracker-state`
  - [x] `p2` - `cpt-ex-ovwa-dbtable-config`


### 2. [Notifications](features/notifications.md) - HIGH

- [x] `p1` - **ID**: `cpt-ex-ovwa-feature-notifications`

- **Purpose**: Send macOS notifications when the limit is exceeded and repeat reminders at the configured interval while over limit.

- **Depends On**: `cpt-ex-ovwa-feature-tracker-core`

- **Scope**:
  - Determine over-limit condition from tracker state
  - Deliver macOS notification for first over-limit event
  - Repeat reminders while still over limit and user is active
  - Degrade gracefully if notifications fail

- **Out of scope**:
  - Custom UI beyond system notifications
  - Persisting reminder history across restarts

- **Requirements Covered**:
  - [x] `p1` - `cpt-ex-ovwa-fr-notify-on-limit`
  - [x] `p2` - `cpt-ex-ovwa-nfr-reliability`

- **Design Principles Covered**:
  - [x] `p1` - `cpt-ex-ovwa-principle-explicit-control`

- **Design Constraints Covered**:
  - [x] `p1` - `cpt-ex-ovwa-constraint-no-auto-reset-no-persist`

- **Domain Model Entities**:
  - TrackerState

- **Design Components**:
  - [x] `p2` - `cpt-ex-ovwa-component-notifier`

- **API**:
  - (none)

- **Sequences**:
  - [x] `p1` - `cpt-ex-ovwa-seq-run-and-alert`

- **Data**:
  - [x] `p2` - `cpt-ex-ovwa-dbtable-tracker-state`


### 3. [CLI Control + Local IPC](features/cli-control.md) - MEDIUM

- [x] `p2` - **ID**: `cpt-ex-ovwa-feature-cli-control`

- **Purpose**: Provide CLI commands for status/pause/resume/reset/stop and implement the local-only control channel between CLI and daemon.

- **Depends On**: `cpt-ex-ovwa-feature-tracker-core`

- **Scope**:
  - CLI command parsing and output formatting
  - Local IPC request/response protocol for control commands
  - Pause/resume/reset/stop control semantics

- **Out of scope**:
  - Network-accessible API
  - Multi-user support

- **Requirements Covered**:
  - [x] `p2` - `cpt-ex-ovwa-fr-cli-controls`
  - [x] `p2` - `cpt-ex-ovwa-fr-manual-reset`

- **Design Principles Covered**:
  - [x] `p1` - `cpt-ex-ovwa-principle-explicit-control`

- **Design Constraints Covered**:
  - [x] `p1` - `cpt-ex-ovwa-constraint-macos-cli-only`

- **Domain Model Entities**:
  - TrackerState
  - ControlCommand

- **Design Components**:
  - [x] `p1` - `cpt-ex-ovwa-component-cli`
  - [x] `p2` - `cpt-ex-ovwa-component-control-channel`

- **API**:
  - `overwork-alert status`
  - `overwork-alert pause`
  - `overwork-alert resume`
  - `overwork-alert reset`
  - `overwork-alert stop`

- **Sequences**:
  - [x] `p2` - `cpt-ex-ovwa-seq-cli-reset`

- **Data**:
  - [x] `p2` - `cpt-ex-ovwa-dbtable-tracker-state`


### 4. [Autostart (LaunchAgent)](features/launchagent-autostart.md) - MEDIUM

- [x] `p2` - **ID**: `cpt-ex-ovwa-feature-launchagent-autostart`

- **Purpose**: Allow the tool to start automatically at login via a user LaunchAgent and provide CLI commands to install/uninstall autostart.

- **Depends On**: `cpt-ex-ovwa-feature-cli-control`

- **Scope**:
  - Generate LaunchAgent plist content for the daemon
  - Install/uninstall/start/stop the LaunchAgent using launchctl
  - Ensure user-level (not system-level) installation

- **Out of scope**:
  - System-wide daemon installation
  - Menubar UI integration

- **Requirements Covered**:
  - [x] `p2` - `cpt-ex-ovwa-fr-autostart`

- **Design Principles Covered**:
  - [x] `p1` - `cpt-ex-ovwa-principle-local-only-minimal-state`

- **Design Constraints Covered**:
  - [x] `p1` - `cpt-ex-ovwa-constraint-macos-cli-only`

- **Domain Model Entities**:
  - Config

- **Design Components**:
  - [x] `p2` - `cpt-ex-ovwa-component-launchagent-manager`

- **API**:
  - `overwork-alert install-autostart`
  - `overwork-alert uninstall-autostart`

- **Sequences**:
  - [x] `p2` - `cpt-ex-ovwa-seq-run-and-alert`

- **Data**:
  - [x] `p2` - `cpt-ex-ovwa-dbtable-config`



---

## 3. Feature Dependencies

```text
cpt-ex-ovwa-feature-tracker-core
    ↓
    ├─→ cpt-ex-ovwa-feature-notifications
    ├─→ cpt-ex-ovwa-feature-cli-control
    └─→ cpt-ex-ovwa-feature-launchagent-autostart
```

**Dependency Rationale**:

- `cpt-ex-ovwa-feature-notifications` requires `cpt-ex-ovwa-feature-tracker-core`: notifications depend on tracker state and active-time accumulation.
- `cpt-ex-ovwa-feature-cli-control` requires `cpt-ex-ovwa-feature-tracker-core`: control commands operate on tracker state and daemon lifecycle.
- `cpt-ex-ovwa-feature-launchagent-autostart` requires `cpt-ex-ovwa-feature-cli-control`: autostart is installed/uninstalled via CLI commands.
