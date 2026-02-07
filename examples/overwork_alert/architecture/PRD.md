<!-- cpt:#:prd -->
# PRD

<!-- cpt:##:overview -->
## 1. Overview

<!-- cpt:paragraph:purpose -->
**Purpose**: Overwork Alert is a small macOS background tool that tracks your active work time and notifies you when you exceed a configurable limit. It exists to help you notice overwork early and take breaks before fatigue builds up.
<!-- cpt:paragraph:purpose -->

<!-- cpt:paragraph:context -->
Overwork Alert is a local-first, single-user productivity helper intended for developers and knowledge workers who regularly lose track of time during deep work.

It measures “work time” as **active time**: when you are idle longer than a configurable threshold, the timer pauses automatically and resumes when activity returns.
<!-- cpt:paragraph:context -->

**Target Users**:
<!-- cpt:list:target-users required="true" -->
- Developers who often work long focused sessions and want a clear “stop” reminder.
- Knowledge workers who want a simple session cap without a full time-tracking product.
- People practicing break routines (e.g., Pomodoro) who still need a long-session safety net.
<!-- cpt:list:target-users -->

**Key Problems Solved**:
<!-- cpt:list:key-problems required="true" -->
- Losing track of time during deep work, leading to skipped breaks and fatigue.
- Inconsistent break discipline because there is no reliable, automated reminder.
- Miscounting “work time” when stepping away, because idle time is not excluded.
<!-- cpt:list:key-problems -->

**Success Criteria**:
<!-- cpt:list:success-criteria required="true" -->
- Install and first-run setup completed in 10 minutes or less on macOS (baseline: N/A, target: v1.0).
- After exceeding the configured limit while active, the first alert appears within 5 seconds (baseline: N/A, target: v1.0).
- When idle exceeds the configured threshold, active-time accumulation pauses within 10 seconds (baseline: N/A, target: v1.0).
- Users can verify current status (active time, limit, paused state) via CLI in under 5 seconds (baseline: N/A, target: v1.0).
<!-- cpt:list:success-criteria -->

**Capabilities**:
<!-- cpt:list:capabilities required="true" -->
- Track active work time with idle-aware pausing.
- Configure work limit, idle threshold, and reminder repetition.
- Deliver macOS notifications when the limit is exceeded.
- Provide simple CLI controls to view status and control tracking.
- Optionally start automatically on user login.
<!-- cpt:list:capabilities -->
<!-- cpt:##:overview -->

<!-- cpt:##:actors -->
## 2. Actors

<!-- cpt:###:actor-title repeat="many" -->
### User

<!-- cpt:id:actor has="task" -->
- [x] **ID**: `cpt-overwork-alert-actor-user`

<!-- cpt:paragraph:actor-role -->
**Role**: Wants to be notified when they have worked too long, adjust configuration, and control the tracker (status/pause/resume/reset).
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### macOS System

<!-- cpt:id:actor has="task" -->
- [x] **ID**: `cpt-overwork-alert-actor-macos`

<!-- cpt:paragraph:actor-role -->
**Role**: Provides the runtime environment, surfaces user notifications, and exposes signals needed to estimate user idleness.
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:###:actor-title repeat="many" -->
### Login Background Runner

<!-- cpt:id:actor has="task" -->
- [x] **ID**: `cpt-overwork-alert-actor-login-runner`

<!-- cpt:paragraph:actor-role -->
**Role**: Starts the tool automatically on login and keeps it running in the background for continuous tracking.
<!-- cpt:paragraph:actor-role -->
<!-- cpt:id:actor -->
<!-- cpt:###:actor-title repeat="many" -->

<!-- cpt:##:actors -->

<!-- cpt:##:frs -->
## 3. Functional Requirements

<!-- cpt:###:fr-title repeat="many" -->
### FR-001 Track active work time (idle-aware)

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p1` - **ID**: `cpt-overwork-alert-fr-track-active-time`

<!-- cpt:free:fr-summary -->
The system MUST track “active work time” for the user.

Active work time MUST pause when the user has been idle longer than the configured idle threshold, and MUST resume when activity returns.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-overwork-alert-actor-user`
`cpt-overwork-alert-actor-macos`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-002 Configure limit and idle threshold

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p1` - **ID**: `cpt-overwork-alert-fr-configurable-limit`

<!-- cpt:free:fr-summary -->
The system MUST allow the user to configure:

- A daily/session work-time limit (default: 3 hours).
- An idle threshold used to pause active time (default: 5 minutes).
- A repeat reminder interval after the first over-limit alert (default: 30 minutes).

Configuration MUST have safe defaults if no configuration is present.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-overwork-alert-actor-user`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-003 Notify when limit is exceeded and repeat reminders

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p1` - **ID**: `cpt-overwork-alert-fr-notify-on-limit`

<!-- cpt:free:fr-summary -->
When the tracked active work time exceeds the configured limit, the system MUST notify the user.

If the user continues working while over the limit, the system MUST repeat notifications at the configured repeat interval until the user stops working (becomes idle) or manually pauses/resets tracking.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-overwork-alert-actor-user`
`cpt-overwork-alert-actor-macos`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-004 Manual reset (no automatic reset)

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p2` - **ID**: `cpt-overwork-alert-fr-manual-reset`

<!-- cpt:free:fr-summary -->
The system MUST provide a manual reset capability so the user can restart tracking on demand.

The system MUST NOT automatically reset accumulated work time based on time-of-day in v1.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-overwork-alert-actor-user`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-005 Run continuously in background and support autostart

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p2` - **ID**: `cpt-overwork-alert-fr-autostart`

<!-- cpt:free:fr-summary -->
The system MUST be able to run continuously in the background.

The system SHOULD support starting automatically at user login.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-overwork-alert-actor-user`
`cpt-overwork-alert-actor-login-runner`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:###:fr-title repeat="many" -->
### FR-006 Provide CLI controls (status/pause/resume/reset)

<!-- cpt:id:fr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p2` - **ID**: `cpt-overwork-alert-fr-cli-controls`

<!-- cpt:free:fr-summary -->
The system MUST provide a CLI interface that allows the user to:

- Start the tracker.
- View current status (active time, limit, paused/active state).
- Pause and resume tracking.
- Reset the current day/session accumulation.
<!-- cpt:free:fr-summary -->

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-overwork-alert-actor-user`
<!-- cpt:id-ref:actor -->
<!-- cpt:id:fr -->
<!-- cpt:###:fr-title repeat="many" -->

<!-- cpt:##:frs -->

<!-- cpt:##:usecases -->
## 4. Use Cases

<!-- cpt:###:uc-title repeat="many" -->
### UC-001 Run tracker and receive an overwork alert

<!-- cpt:id:usecase -->
**ID**: `cpt-overwork-alert-usecase-run-and-alert`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-overwork-alert-actor-user`
`cpt-overwork-alert-actor-macos`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: The user has a running tracker session (started manually or via autostart).
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**: Over-limit notification
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. The user works normally while the system accumulates active work time.
2. The user becomes idle longer than the idle threshold; the system pauses active-time accumulation.
3. The user returns to activity; the system resumes active-time accumulation.
4. The accumulated active work time exceeds the configured limit; the system sends an overwork notification.
5. If the user continues working while still over the limit, the system repeats notifications at the configured interval.
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: The user has been notified that the work-time limit was exceeded.
<!-- cpt:paragraph:postconditions -->

**Alternative Flows**:
<!-- cpt:list:alternative-flows -->
- **Configuration missing/invalid**: The system continues with safe defaults and the user can still receive alerts.
- **Notifications suppressed by system settings**: The system continues tracking and status remains available via CLI.
<!-- cpt:list:alternative-flows -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

<!-- cpt:###:uc-title repeat="many" -->
### UC-002 Configure the limit

<!-- cpt:id:usecase -->
**ID**: `cpt-overwork-alert-usecase-configure-limit`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-overwork-alert-actor-user`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: The user has access to the tool’s configuration mechanism.
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**: Adjust configuration
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. The user updates the configured limit and/or idle threshold.
2. The user restarts the tracker or triggers a configuration reload (as supported by the CLI).
3. The system uses the new configuration for subsequent tracking and alerts.
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: The updated configuration is in effect for tracking and notifications.
<!-- cpt:paragraph:postconditions -->

**Alternative Flows**:
<!-- cpt:list:alternative-flows -->
- **Invalid values**: The system rejects invalid configuration and continues using the last known good configuration.
<!-- cpt:list:alternative-flows -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

<!-- cpt:###:uc-title repeat="many" -->
### UC-003 Pause, resume, and reset a session

<!-- cpt:id:usecase -->
**ID**: `cpt-overwork-alert-usecase-control-session`

**Actors**:
<!-- cpt:id-ref:actor -->
`cpt-overwork-alert-actor-user`
<!-- cpt:id-ref:actor -->

<!-- cpt:paragraph:preconditions -->
**Preconditions**: The tracker is running.
<!-- cpt:paragraph:preconditions -->

<!-- cpt:paragraph:flow -->
**Flow**: Control the tracker
<!-- cpt:paragraph:flow -->

<!-- cpt:numbered-list:flow-steps -->
1. The user checks current status via CLI.
2. The user pauses tracking (e.g., during meetings or non-work time).
3. The user resumes tracking when ready.
4. The user resets tracking to restart accumulation for the day/session.
<!-- cpt:numbered-list:flow-steps -->

<!-- cpt:paragraph:postconditions -->
**Postconditions**: The tracker state reflects the user’s control actions (paused/resumed/reset).
<!-- cpt:paragraph:postconditions -->

**Alternative Flows**:
<!-- cpt:list:alternative-flows -->
- **Tracker not running**: The CLI reports the tracker is not active and provides guidance to start it.
<!-- cpt:list:alternative-flows -->
<!-- cpt:id:usecase -->
<!-- cpt:###:uc-title repeat="many" -->

<!-- cpt:##:usecases -->

<!-- cpt:##:nfrs -->
## 5. Non-functional requirements

<!-- cpt:###:nfr-title repeat="many" -->
### Privacy & Data Handling

<!-- cpt:id:nfr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p1` - **ID**: `cpt-overwork-alert-nfr-privacy-local-only`

<!-- cpt:list:nfr-statements -->
- The system MUST be local-first and MUST NOT send tracking data over the network by default.
- The system MUST store only minimal local state required to implement tracking and alerting.
<!-- cpt:list:nfr-statements -->
<!-- cpt:id:nfr -->
<!-- cpt:###:nfr-title repeat="many" -->

<!-- cpt:###:nfr-title repeat="many" -->
### Reliability

<!-- cpt:id:nfr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p2` - **ID**: `cpt-overwork-alert-nfr-reliability`

<!-- cpt:list:nfr-statements -->
- The system SHOULD degrade gracefully if notifications cannot be delivered (tracking continues, CLI status remains available).
<!-- cpt:list:nfr-statements -->
<!-- cpt:id:nfr -->
<!-- cpt:###:nfr-title repeat="many" -->

<!-- cpt:###:nfr-title repeat="many" -->
### Performance & Resource Usage

<!-- cpt:id:nfr has="priority,task" covered_by="DESIGN,DECOMPOSITION,SPEC" -->
- [x] `p2` - **ID**: `cpt-overwork-alert-nfr-low-overhead`

<!-- cpt:list:nfr-statements -->
- The system SHOULD be low-overhead and suitable for always-on background usage.
- The system SHOULD avoid high-frequency polling that would noticeably impact CPU or battery.
<!-- cpt:list:nfr-statements -->
<!-- cpt:id:nfr -->
<!-- cpt:###:nfr-title repeat="many" -->

<!-- cpt:###:intentional-exclusions -->
### Intentional Exclusions

<!-- cpt:list:exclusions -->
- **Accessibility** (UX-PRD-002): Not applicable — there is no custom UI surface in v1 beyond CLI and system notifications.
- **Internationalization** (UX-PRD-003): Not applicable — this is an example tool with English-only messages in v1.
- **Regulatory compliance** (COMPL-PRD-001): Not applicable — the tool does not process user-provided PII beyond local timestamps for tracking.
<!-- cpt:list:exclusions -->
<!-- cpt:###:intentional-exclusions -->
<!-- cpt:##:nfrs -->

<!-- cpt:##:nongoals -->
## 6. Non-Goals & Risks

<!-- cpt:###:nongoals-title -->
### Non-Goals

<!-- cpt:list:nongoals -->
- Not a full-featured time tracking or billing product.
- Not a cross-platform tool in v1.
- Not a menubar UI application in v1.
<!-- cpt:list:nongoals -->
<!-- cpt:###:nongoals-title -->

<!-- cpt:###:risks-title -->
### Risks

<!-- cpt:list:risks -->
- **Notification suppression**: macOS Focus modes or notification permissions may suppress alerts; mitigation is to provide clear setup guidance and always keep CLI status available.
- **Idle signal variability**: Idle measurement behavior may vary across macOS versions; mitigation is to test and document supported versions and known limitations.
<!-- cpt:list:risks -->
<!-- cpt:###:risks-title -->
<!-- cpt:##:nongoals -->

<!-- cpt:##:assumptions -->
## 7. Assumptions & Open Questions

<!-- cpt:###:assumptions-title -->
### Assumptions

<!-- cpt:list:assumptions -->
- The user is running macOS and permits notifications for this tool; if not, the tool still provides status via CLI.
- The user accepts a background process that runs continuously when enabled.
<!-- cpt:list:assumptions -->
<!-- cpt:###:assumptions-title -->

<!-- cpt:###:open-questions-title -->
### Open Questions

<!-- cpt:list:open-questions -->
- Should screen lock be treated as immediate idle regardless of the idle threshold? — Owner: User, Target: next iteration
- Should notifications include sound by default, or be notification-only? — Owner: User, Target: next iteration
<!-- cpt:list:open-questions -->
<!-- cpt:###:open-questions-title -->
<!-- cpt:##:assumptions -->

<!-- cpt:##:context -->
## 8. Additional context

<!-- cpt:###:context-title repeat="many" -->
### Example Scope Notes

<!-- cpt:free:prd-context-notes -->
This PRD is intentionally scoped as a minimal “end-to-end Cypilot SDLC” example within the Cypilot repository.
<!-- cpt:free:prd-context-notes -->
<!-- cpt:###:context-title repeat="many" -->

<!-- cpt:##:context -->
<!-- cpt:#:prd -->
