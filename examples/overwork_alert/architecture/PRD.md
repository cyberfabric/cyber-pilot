# PRD

## 1. Overview

### 1.1 Purpose

**Purpose**: Overwork Alert is a small macOS background tool that tracks your active work time and notifies you when you exceed a configurable limit. It exists to help you notice overwork early and take breaks before fatigue builds up.

Overwork Alert is a local-first, single-user productivity helper intended for developers and knowledge workers who regularly lose track of time during deep work.

It measures “work time” as **active time**: when you are idle longer than a configurable threshold, the timer pauses automatically and resumes when activity returns.

### 1.2 Background / Problem Statement

**Target Users**:
- Developers who often work long focused sessions and want a clear “stop” reminder.
- Knowledge workers who want a simple session cap without a full time-tracking product.
- People practicing break routines (e.g., Pomodoro) who still need a long-session safety net.

**Key Problems Solved**:
- Losing track of time during deep work, leading to skipped breaks and fatigue.
- Inconsistent break discipline because there is no reliable, automated reminder.
- Miscounting “work time” when stepping away, because idle time is not excluded.

### 1.3 Goals (Business Outcomes)

**Success Criteria**:
- Install and first-run setup completed in 10 minutes or less on macOS (baseline: N/A, target: v1.0).
- After exceeding the configured limit while active, the first alert appears within 5 seconds (baseline: N/A, target: v1.0).
- When idle exceeds the configured threshold, active-time accumulation pauses within 10 seconds (baseline: N/A, target: v1.0).
- Users can verify current status (active time, limit, paused state) via CLI in under 5 seconds (baseline: N/A, target: v1.0).

**Capabilities**:
- Track active work time with idle-aware pausing.
- Configure work limit, idle threshold, and reminder repetition.
- Deliver macOS notifications when the limit is exceeded.
- Provide simple CLI controls to view status and control tracking.
- Optionally start automatically on user login.

### 1.4 Glossary

| Term | Definition |
|------|------------|
| active time | Time accumulated while user is not idle beyond idle_threshold_seconds |
| idle threshold | Duration of inactivity after which tracking pauses |
| limit | Configured maximum active time for a session/day |

## 2. Actors

### 2.1 Human Actors

### User

**ID**: `cpt-overwork-alert-actor-user`

**Role**: Wants to be notified when they have worked too long, adjust configuration, and control the tracker (status/pause/resume/reset).

### 2.2 System Actors

### macOS System

**ID**: `cpt-overwork-alert-actor-macos`

**Role**: Provides the runtime environment, surfaces user notifications, and exposes signals needed to estimate user idleness.

### Login Background Runner

**ID**: `cpt-overwork-alert-actor-login-runner`

**Role**: Starts the tool automatically on login and keeps it running in the background for continuous tracking.

## 3. Operational Concept & Environment

### 3.1 Module-Specific Environment Constraints

- macOS user session only
- Local-only operation (no network dependencies)

## 4. Scope

### 4.1 In Scope

- Idle-aware active-time tracking
- Over-limit notifications and repeat reminders
- Local CLI control and local-only IPC
- Optional LaunchAgent autostart

### 4.2 Out of Scope

- Menubar UI or custom GUI
- System-wide (root) installation
- Cloud sync or remote telemetry


## 5. Functional Requirements

### FR-001 Track active work time (idle-aware)

- [x] `p1` - **ID**: `cpt-overwork-alert-fr-track-active-time`

The system MUST track “active work time” for the user.

Active work time MUST pause when the user has been idle longer than the configured idle threshold, and MUST resume when activity returns.

**Actors**:
`cpt-overwork-alert-actor-user`
`cpt-overwork-alert-actor-macos`

### FR-002 Configure limit and idle threshold

- [x] `p1` - **ID**: `cpt-overwork-alert-fr-configurable-limit`

The system MUST allow the user to configure:

- A daily/session work-time limit (default: 3 hours).
- An idle threshold used to pause active time (default: 5 minutes).
- A repeat reminder interval after the first over-limit alert (default: 30 minutes).

Configuration MUST have safe defaults if no configuration is present.

**Actors**:
`cpt-overwork-alert-actor-user`

### FR-003 Notify when limit is exceeded and repeat reminders

- [x] `p1` - **ID**: `cpt-overwork-alert-fr-notify-on-limit`

When the tracked active work time exceeds the configured limit, the system MUST notify the user.

If the user continues working while over the limit, the system MUST repeat notifications at the configured repeat interval until the user stops working (becomes idle) or manually pauses/resets tracking.

**Actors**:
`cpt-overwork-alert-actor-user`
`cpt-overwork-alert-actor-macos`

### FR-004 Manual reset (no automatic reset)

- [x] `p2` - **ID**: `cpt-overwork-alert-fr-manual-reset`

The system MUST provide a manual reset capability so the user can restart tracking on demand.

The system MUST NOT automatically reset accumulated work time based on time-of-day in v1.

**Actors**:
`cpt-overwork-alert-actor-user`

### FR-005 Run continuously in background and support autostart

- [x] `p2` - **ID**: `cpt-overwork-alert-fr-autostart`

The system MUST be able to run continuously in the background.

The system SHOULD support starting automatically at user login.

**Actors**:
`cpt-overwork-alert-actor-user`
`cpt-overwork-alert-actor-login-runner`

### FR-006 Provide CLI controls (status/pause/resume/reset)

- [x] `p2` - **ID**: `cpt-overwork-alert-fr-cli-controls`

The system MUST provide a CLI interface that allows the user to:

- Start the tracker.
- View current status (active time, limit, paused/active state).
- Pause and resume tracking.
- Reset the current day/session accumulation.

**Actors**:
`cpt-overwork-alert-actor-user`


## 6. Non-Functional Requirements

### 6.1 Module-Specific NFRs

### Privacy & Data Handling

- [x] `p1` - **ID**: `cpt-overwork-alert-nfr-privacy-local-only`

- The system MUST be local-first and MUST NOT send tracking data over the network by default.
- The system MUST store only minimal local state required to implement tracking and alerting.

### Reliability

- [x] `p2` - **ID**: `cpt-overwork-alert-nfr-reliability`

- The system SHOULD degrade gracefully if notifications cannot be delivered (tracking continues, CLI status remains available).

### Performance & Resource Usage

- [x] `p2` - **ID**: `cpt-overwork-alert-nfr-low-overhead`

- The system SHOULD be low-overhead and suitable for always-on background usage.
- The system SHOULD avoid high-frequency polling that would noticeably impact CPU or battery.

### 6.2 NFR Exclusions

- (none)

## 7. Public Library Interfaces

### 7.1 Public API Surface

- (n/a)

### 7.2 External Integration Contracts

- (n/a)

## 8. Use Cases

### UC-001 Run tracker and receive an overwork alert

**ID**: `cpt-overwork-alert-usecase-run-and-alert`

**Actors**:
`cpt-overwork-alert-actor-user`
`cpt-overwork-alert-actor-macos`

**Preconditions**: The user has a running tracker session (started manually or via autostart).

**Flow**: Over-limit notification

1. The user works normally while the system accumulates active work time.
2. The user becomes idle longer than the idle threshold; the system pauses active-time accumulation.
3. The user returns to activity; the system resumes active-time accumulation.
4. The accumulated active work time exceeds the configured limit; the system sends an overwork notification.
5. If the user continues working while still over the limit, the system repeats notifications at the configured interval.

**Postconditions**: The user has been notified that the work-time limit was exceeded.

**Alternative Flows**:
- **Configuration missing/invalid**: The system continues with safe defaults and the user can still receive alerts.
- **Notifications suppressed by system settings**: The system continues tracking and status remains available via CLI.

### UC-002 Configure the limit

**ID**: `cpt-overwork-alert-usecase-configure-limit`

**Actors**:
`cpt-overwork-alert-actor-user`

**Preconditions**: The user has access to the tool’s configuration mechanism.

**Flow**: Adjust configuration

1. The user updates the configured limit and/or idle threshold.
2. The user restarts the tracker or triggers a configuration reload (as supported by the CLI).
3. The system uses the new configuration for subsequent tracking and alerts.

**Postconditions**: The updated configuration is in effect for tracking and notifications.

**Alternative Flows**:
- **Invalid values**: The system rejects invalid configuration and continues using the last known good configuration.

### UC-003 Pause, resume, and reset a session

**ID**: `cpt-overwork-alert-usecase-control-session`

**Actors**:
`cpt-overwork-alert-actor-user`

**Preconditions**: The tracker is running.

**Flow**: Control the tracker

1. The user checks current status via CLI.
2. The user pauses tracking (e.g., during meetings or non-work time).
3. The user resumes tracking when ready.
4. The user resets tracking to restart accumulation for the day/session.

**Postconditions**: The tracker state reflects the user’s control actions (paused/resumed/reset).

**Alternative Flows**:
- **Tracker not running**: The CLI reports the tracker is not active and provides guidance to start it.

## 9. Acceptance Criteria

- [ ] Install and first-run setup completed in 10 minutes or less on macOS.
- [ ] After exceeding the configured limit while active, the first alert appears within 5 seconds.
- [ ] When idle exceeds the configured threshold, active-time accumulation pauses within 10 seconds.
- [ ] Users can verify current status via CLI in under 5 seconds.

## 10. Dependencies

| Dependency | Description | Criticality |
|------------|-------------|-------------|
| macOS Notification Center | User notifications | p2 |
| launchd | LaunchAgent autostart | p2 |

## 11. Assumptions

- Users run macOS with access to local notifications.
- The tool runs in a single-user session context.

## 12. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Notifications suppressed by user/system | Alerts may not be delivered | CLI status remains available; treat notification failures as non-fatal |
| Idle detection unavailable intermittently | Tracking may skip ticks | Use best-effort idle signal; skip accumulation on unknown idle |

- The system SHOULD be low-overhead and suitable for always-on background usage.
- The system SHOULD avoid high-frequency polling that would noticeably impact CPU or battery.

### Intentional Exclusions

- **Accessibility** (UX-PRD-002): Not applicable — there is no custom UI surface in v1 beyond CLI and system notifications.
- **Internationalization** (UX-PRD-003): Not applicable — this is an example tool with English-only messages in v1.
- **Regulatory compliance** (COMPL-PRD-001): Not applicable — the tool does not process user-provided PII beyond local timestamps for tracking.

## 13. Non-Goals & Risks

### Non-Goals

- Not a full-featured time tracking or billing product.
- Not a cross-platform tool in v1.
- Not a menubar UI application in v1.

### Risks

- **Notification suppression**: macOS Focus modes or notification permissions may suppress alerts; mitigation is to provide clear setup guidance and always keep CLI status available.
- **Idle signal variability**: Idle measurement behavior may vary across macOS versions; mitigation is to test and document supported versions and known limitations.

## 14. Assumptions & Open Questions

### Assumptions

- The user is running macOS and permits notifications for this tool; if not, the tool still provides status via CLI.
- The user accepts a background process that runs continuously when enabled.

### Open Questions

- Should screen lock be treated as immediate idle regardless of the idle threshold? — Owner: User, Target: next iteration
- Should notifications include sound by default, or be notification-only? — Owner: User, Target: next iteration

## 15. Additional context

### Example Scope Notes

This PRD is intentionally scoped as a minimal “end-to-end Cypilot SDLC” example within the Cypilot repository.

