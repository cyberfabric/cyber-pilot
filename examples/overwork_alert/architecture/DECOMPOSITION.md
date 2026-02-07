<!-- cpt:#:decomposition -->
# Decomposition: Overwork Alert

<!-- cpt:##:overview -->
## 1. Overview

Overwork Alert is decomposed into a small set of specs aligned to the system’s major responsibilities: tracking core (idle-aware accumulation and configuration), notification policy and delivery, CLI control + local IPC, and launchd autostart.

**Decomposition Strategy**:
- Group by functional cohesion (each spec implements a coherent responsibility)
- Keep dependencies minimal and explicit (tracker core is the foundation)
- Ensure 100% coverage of DESIGN elements (components, sequences, and data model items assigned)
- Maintain mutual exclusivity (each component/sequence/data element is owned by a single spec)

<!-- cpt:##:overview -->

<!-- cpt:##:entries -->
## 2. Entries

**Overall implementation status:**
<!-- cpt:id:status has="priority,task" -->
- [x] `p1` - **ID**: `cpt-overwork-alert-status-overall`

<!-- cpt:###:spec-title repeat="many" -->
### 1. [Tracking Core](specs/tracker-core.md) - HIGH

<!-- cpt:id:spec has="priority,task" -->
- [x] `p1` - **ID**: `cpt-overwork-alert-spec-tracker-core`

<!-- cpt:paragraph:spec-purpose required="true" -->
- **Purpose**: Implement the daemon tracking loop and the idle-aware active-time accumulation model with safe configuration defaults.
<!-- cpt:paragraph:spec-purpose -->

<!-- cpt:paragraph:spec-depends -->
- **Depends On**: None
<!-- cpt:paragraph:spec-depends -->

<!-- cpt:list:spec-scope -->
- **Scope**:
  - Load configuration with safe defaults and validation
  - Sample macOS idle time and determine active vs idle
  - Maintain session-scoped in-memory tracker state (no persistence)
  - Accumulate active time only when running and not idle
<!-- cpt:list:spec-scope -->

<!-- cpt:list:spec-out-scope -->
- **Out of scope**:
  - Persisting accumulated time across restarts
  - Automatic time-of-day resets
<!-- cpt:list:spec-out-scope -->

- **Requirements Covered**:
<!-- cpt:id-ref:fr has="priority,task" -->
  - [x] `p1` - `cpt-overwork-alert-fr-track-active-time`
  - [x] `p1` - `cpt-overwork-alert-fr-configurable-limit`
  - [x] `p1` - `cpt-overwork-alert-nfr-privacy-local-only`
  - [x] `p2` - `cpt-overwork-alert-nfr-low-overhead`
<!-- cpt:id-ref:fr -->

- **Design Principles Covered**:
<!-- cpt:id-ref:principle has="priority,task" -->
  - [x] `p1` - `cpt-overwork-alert-principle-local-only-minimal-state`
  - [x] `p2` - `cpt-overwork-alert-principle-low-overhead`
<!-- cpt:id-ref:principle -->

- **Design Constraints Covered**:
<!-- cpt:id-ref:constraint has="priority,task" -->
  - [x] `p1` - `cpt-overwork-alert-constraint-no-auto-reset-no-persist`
  - [x] `p1` - `cpt-overwork-alert-constraint-macos-cli-only`
<!-- cpt:id-ref:constraint -->

<!-- cpt:list:spec-domain-entities -->
- **Domain Model Entities**:
  - Config
  - TrackerState
  - IdleSample
<!-- cpt:list:spec-domain-entities -->

- **Design Components**:
<!-- cpt:id-ref:component has="priority,task" -->
  - [x] `p1` - `cpt-overwork-alert-component-daemon`
  - [x] `p2` - `cpt-overwork-alert-component-idle-detector`
  - [x] `p2` - `cpt-overwork-alert-component-config-loader`
<!-- cpt:id-ref:component -->

<!-- cpt:list:spec-api -->
- **API**:
  - `overwork-alert start`
<!-- cpt:list:spec-api -->

- **Sequences**:
<!-- cpt:id-ref:seq has="priority,task" -->
  - [x] `p1` - `cpt-overwork-alert-seq-run-and-alert`
<!-- cpt:id-ref:seq -->

- **Data**:
<!-- cpt:id-ref:dbtable has="priority,task" -->
  - [x] `p2` - `cpt-overwork-alert-dbtable-tracker-state`
  - [x] `p2` - `cpt-overwork-alert-dbtable-config`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:spec -->
<!-- cpt:###:spec-title repeat="many" -->

<!-- cpt:###:spec-title repeat="many" -->
### 2. [Notifications](specs/notifications.md) - HIGH

<!-- cpt:id:spec has="priority,task" -->
- [x] `p1` - **ID**: `cpt-overwork-alert-spec-notifications`

<!-- cpt:paragraph:spec-purpose required="true" -->
- **Purpose**: Send macOS notifications when the limit is exceeded and repeat reminders at the configured interval while over limit.
<!-- cpt:paragraph:spec-purpose -->

<!-- cpt:paragraph:spec-depends -->
- **Depends On**: `cpt-overwork-alert-spec-tracker-core`
<!-- cpt:paragraph:spec-depends -->

<!-- cpt:list:spec-scope -->
- **Scope**:
  - Determine over-limit condition from tracker state
  - Deliver macOS notification for first over-limit event
  - Repeat reminders while still over limit and user is active
  - Degrade gracefully if notifications fail
<!-- cpt:list:spec-scope -->

<!-- cpt:list:spec-out-scope -->
- **Out of scope**:
  - Custom UI beyond system notifications
  - Persisting reminder history across restarts
<!-- cpt:list:spec-out-scope -->

- **Requirements Covered**:
<!-- cpt:id-ref:fr has="priority,task" -->
  - [x] `p1` - `cpt-overwork-alert-fr-notify-on-limit`
  - [x] `p2` - `cpt-overwork-alert-nfr-reliability`
<!-- cpt:id-ref:fr -->

- **Design Principles Covered**:
<!-- cpt:id-ref:principle has="priority,task" -->
  - [x] `p1` - `cpt-overwork-alert-principle-explicit-control`
<!-- cpt:id-ref:principle -->

- **Design Constraints Covered**:
<!-- cpt:id-ref:constraint has="priority,task" -->
  - [x] `p1` - `cpt-overwork-alert-constraint-no-auto-reset-no-persist`
<!-- cpt:id-ref:constraint -->

<!-- cpt:list:spec-domain-entities -->
- **Domain Model Entities**:
  - TrackerState
<!-- cpt:list:spec-domain-entities -->

- **Design Components**:
<!-- cpt:id-ref:component has="priority,task" -->
  - [x] `p2` - `cpt-overwork-alert-component-notifier`
<!-- cpt:id-ref:component -->

<!-- cpt:list:spec-api -->
- **API**:
  - (none)
<!-- cpt:list:spec-api -->

- **Sequences**:
<!-- cpt:id-ref:seq has="priority,task" -->
  - [x] `p1` - `cpt-overwork-alert-seq-run-and-alert`
<!-- cpt:id-ref:seq -->

- **Data**:
<!-- cpt:id-ref:dbtable has="priority,task" -->
  - [x] `p2` - `cpt-overwork-alert-dbtable-tracker-state`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:spec -->
<!-- cpt:###:spec-title repeat="many" -->

<!-- cpt:###:spec-title repeat="many" -->
### 3. [CLI Control + Local IPC](specs/cli-control.md) - MEDIUM

<!-- cpt:id:spec has="priority,task" -->
- [x] `p2` - **ID**: `cpt-overwork-alert-spec-cli-control`

<!-- cpt:paragraph:spec-purpose required="true" -->
- **Purpose**: Provide CLI commands for status/pause/resume/reset/stop and implement the local-only control channel between CLI and daemon.
<!-- cpt:paragraph:spec-purpose -->

<!-- cpt:paragraph:spec-depends -->
- **Depends On**: `cpt-overwork-alert-spec-tracker-core`
<!-- cpt:paragraph:spec-depends -->

<!-- cpt:list:spec-scope -->
- **Scope**:
  - CLI command parsing and output formatting
  - Local IPC request/response protocol for control commands
  - Pause/resume/reset/stop control semantics
<!-- cpt:list:spec-scope -->

<!-- cpt:list:spec-out-scope -->
- **Out of scope**:
  - Network-accessible API
  - Multi-user support
<!-- cpt:list:spec-out-scope -->

- **Requirements Covered**:
<!-- cpt:id-ref:fr has="priority,task" -->
  - [x] `p2` - `cpt-overwork-alert-fr-cli-controls`
  - [x] `p2` - `cpt-overwork-alert-fr-manual-reset`
<!-- cpt:id-ref:fr -->

- **Design Principles Covered**:
<!-- cpt:id-ref:principle has="priority,task" -->
  - [x] `p1` - `cpt-overwork-alert-principle-explicit-control`
<!-- cpt:id-ref:principle -->

- **Design Constraints Covered**:
<!-- cpt:id-ref:constraint has="priority,task" -->
  - [x] `p1` - `cpt-overwork-alert-constraint-macos-cli-only`
<!-- cpt:id-ref:constraint -->

<!-- cpt:list:spec-domain-entities -->
- **Domain Model Entities**:
  - TrackerState
  - ControlCommand
<!-- cpt:list:spec-domain-entities -->

- **Design Components**:
<!-- cpt:id-ref:component has="priority,task" -->
  - [x] `p1` - `cpt-overwork-alert-component-cli`
  - [x] `p2` - `cpt-overwork-alert-component-control-channel`
<!-- cpt:id-ref:component -->

<!-- cpt:list:spec-api -->
- **API**:
  - `overwork-alert status`
  - `overwork-alert pause`
  - `overwork-alert resume`
  - `overwork-alert reset`
  - `overwork-alert stop`
<!-- cpt:list:spec-api -->

- **Sequences**:
<!-- cpt:id-ref:seq has="priority,task" -->
  - [x] `p2` - `cpt-overwork-alert-seq-cli-reset`
<!-- cpt:id-ref:seq -->

- **Data**:
<!-- cpt:id-ref:dbtable has="priority,task" -->
  - [x] `p2` - `cpt-overwork-alert-dbtable-tracker-state`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:spec -->
<!-- cpt:###:spec-title repeat="many" -->

<!-- cpt:###:spec-title repeat="many" -->
### 4. [Autostart (LaunchAgent)](specs/launchagent-autostart.md) - MEDIUM

<!-- cpt:id:spec has="priority,task" -->
- [x] `p2` - **ID**: `cpt-overwork-alert-spec-launchagent-autostart`

<!-- cpt:paragraph:spec-purpose required="true" -->
- **Purpose**: Allow the tool to start automatically at login via a user LaunchAgent and provide CLI commands to install/uninstall autostart.
<!-- cpt:paragraph:spec-purpose -->

<!-- cpt:paragraph:spec-depends -->
- **Depends On**: `cpt-overwork-alert-spec-cli-control`
<!-- cpt:paragraph:spec-depends -->

<!-- cpt:list:spec-scope -->
- **Scope**:
  - Generate LaunchAgent plist content for the daemon
  - Install/uninstall/start/stop the LaunchAgent using launchctl
  - Ensure user-level (not system-level) installation
<!-- cpt:list:spec-scope -->

<!-- cpt:list:spec-out-scope -->
- **Out of scope**:
  - System-wide daemon installation
  - Menubar UI integration
<!-- cpt:list:spec-out-scope -->

- **Requirements Covered**:
<!-- cpt:id-ref:fr has="priority,task" -->
  - [x] `p2` - `cpt-overwork-alert-fr-autostart`
<!-- cpt:id-ref:fr -->

- **Design Principles Covered**:
<!-- cpt:id-ref:principle has="priority,task" -->
  - [x] `p1` - `cpt-overwork-alert-principle-local-only-minimal-state`
<!-- cpt:id-ref:principle -->

- **Design Constraints Covered**:
<!-- cpt:id-ref:constraint has="priority,task" -->
  - [x] `p1` - `cpt-overwork-alert-constraint-macos-cli-only`
<!-- cpt:id-ref:constraint -->

<!-- cpt:list:spec-domain-entities -->
- **Domain Model Entities**:
  - Config
<!-- cpt:list:spec-domain-entities -->

- **Design Components**:
<!-- cpt:id-ref:component has="priority,task" -->
  - [x] `p2` - `cpt-overwork-alert-component-launchagent-manager`
<!-- cpt:id-ref:component -->

<!-- cpt:list:spec-api -->
- **API**:
  - `overwork-alert install-autostart`
  - `overwork-alert uninstall-autostart`
<!-- cpt:list:spec-api -->

- **Sequences**:
<!-- cpt:id-ref:seq has="priority,task" -->
  - [x] `p2` - `cpt-overwork-alert-seq-run-and-alert`
<!-- cpt:id-ref:seq -->

- **Data**:
<!-- cpt:id-ref:dbtable has="priority,task" -->
  - [x] `p2` - `cpt-overwork-alert-dbtable-config`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:spec -->
<!-- cpt:###:spec-title repeat="many" -->

<!-- cpt:id:status -->
<!-- cpt:##:entries -->
<!-- cpt:#:decomposition -->
