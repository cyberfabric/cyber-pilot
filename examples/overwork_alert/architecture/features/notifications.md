# Feature: Notifications

- [x] `p1` - **ID**: `cpt-ex-ovwa-featstatus-notifications`

- [x] - `cpt-ex-ovwa-feature-notifications`

## 1. Feature Context

### 1. Overview
This feature defines when and how the daemon notifies the user after exceeding the configured active-time limit. It covers the first alert and repeat reminders while the user remains active and tracking is running.

Key assumptions:
- Notification delivery is best-effort and may be suppressed by system settings.
- Notification scheduling state is held in memory and resets on daemon restart.

Configuration parameters (effective defaults in v1):
- limit_seconds: 10800 (3 hours)
- idle_threshold_seconds: 300 (5 minutes)
- repeat_interval_seconds: 1800 (30 minutes)

Acceptance criteria (timing):
- After the tracker first becomes over limit while RUNNING and user is active, the first notification MUST be delivered within 5 seconds.
- Repeat reminders MUST NOT occur more frequently than repeat_interval_seconds.

### 2. Purpose
Ensure the user receives timely, repeatable overwork alerts once the active-time limit is exceeded.

### 3. Actors
- `cpt-ex-ovwa-actor-user`
- `cpt-ex-ovwa-actor-macos`

### 4. References
- Overall Design: [DESIGN.md](../DESIGN.md)
- Related feature: tracker-core.md

## 2. Actor Flows

### Send first over-limit alert

- [x] **ID**: `cpt-ex-ovwa-flow-notifications-first-alert`

**Actors**:
- `cpt-ex-ovwa-actor-user`

1. [x] - `p1` - Daemon observes active_time_seconds > limit_seconds - `inst-detect-over-limit`
2. [x] - `p1` - **IF** tracker status is not RUNNING **RETURN** do_not_notify - `inst-skip-on-not-running`
3. [x] - `p1` - **IF** current idle_seconds >= idle_threshold_seconds **RETURN** do_not_notify - `inst-skip-on-idle`
4. [x] - `p1` - **IF** over-limit has not been notified yet: - `inst-check-first-alert`
5. [x] - `p1` - Notification Sender delivers macOS notification (title + message) - `inst-send-notification`
6. [x] - `p1` - Daemon records over_limit_since and last_reminder_at - `inst-record-notify-state`

### Send repeat reminder while still over limit

- [x] **ID**: `cpt-ex-ovwa-flow-notifications-repeat-reminder`

**Actors**:
- `cpt-ex-ovwa-actor-user`

1. [x] - `p1` - Daemon is over limit and user remains active - `inst-still-over-limit`
2. [x] - `p1` - **IF** tracker status is not RUNNING **RETURN** do_not_notify - `inst-skip-repeat-on-not-running`
3. [x] - `p1` - **IF** current idle_seconds >= idle_threshold_seconds **RETURN** do_not_notify - `inst-skip-repeat-on-idle`
4. [x] - `p1` - **IF** now - last_reminder_at >= repeat_interval_seconds: - `inst-check-interval`
5. [x] - `p1` - Notification Sender delivers macOS reminder notification - `inst-send-reminder`
6. [x] - `p1` - Daemon updates last_reminder_at - `inst-update-last-reminder`


## 3. Processes / Business Logic (CDSL)

### Determine whether to send a notification

- [x] **ID**: `cpt-ex-ovwa-algo-notifications-should-notify`

1. [x] - `p1` - **IF** tracker status is not RUNNING **RETURN** do_not_notify - `inst-not-running`
2. [x] - `p1` - **IF** current idle_seconds >= idle_threshold_seconds **RETURN** do_not_notify - `inst-currently-idle`
3. [x] - `p1` - **IF** active_time_seconds <= limit_seconds **RETURN** do_not_notify - `inst-not-over-limit`
4. [x] - `p1` - **IF** first alert not sent yet **RETURN** notify_now - `inst-first-alert`
5. [x] - `p1` - **IF** now - last_reminder_at >= repeat_interval_seconds **RETURN** notify_now - `inst-repeat-alert`
6. [x] - `p1` - **RETURN** do_not_notify - `inst-default-no`


## 4. States

### Over-limit notification state

- [x] **ID**: `cpt-ex-ovwa-state-notifications-over-limit`

1. [x] - `p1` - **FROM** UNDER_LIMIT **TO** OVER_LIMIT_FIRST_SENT **WHEN** first alert is delivered - `inst-transition-first`
2. [x] - `p1` - **FROM** OVER_LIMIT_FIRST_SENT **TO** OVER_LIMIT_REMINDING **WHEN** reminder is delivered - `inst-transition-remind`
3. [x] - `p1` - **FROM** OVER_LIMIT_REMINDING **TO** UNDER_LIMIT **WHEN** session is reset - `inst-transition-reset`


## 5. Definitions of Done

### Over-limit notifications and repeat reminders

- [x] `p1` - **ID**: `cpt-ex-ovwa-dod-notifications-alert-and-repeat`

When active time exceeds the configured limit while tracking is RUNNING and the user is active (idle below threshold), the system sends a macOS notification within 5 seconds. While the user remains active and over limit, the system repeats notifications at the configured repeat interval.

**Implementation details**:
- Component: `cpt-ex-ovwa-component-notifier`
- Data: `cpt-ex-ovwa-dbtable-tracker-state`

**Implements**:
- `p1` - `cpt-ex-ovwa-flow-notifications-first-alert`
- `p1` - `cpt-ex-ovwa-flow-notifications-repeat-reminder`

- `p1` - `cpt-ex-ovwa-algo-notifications-should-notify`

**Covers (PRD)**:
- `cpt-ex-ovwa-fr-notify-on-limit`

- `cpt-ex-ovwa-nfr-reliability`

**Covers (DESIGN)**:
- `cpt-ex-ovwa-principle-explicit-control`

- `cpt-ex-ovwa-constraint-no-auto-reset-no-persist`

- `cpt-ex-ovwa-component-notifier`
- `cpt-ex-ovwa-component-daemon`

- `cpt-ex-ovwa-seq-run-and-alert`

- `cpt-ex-ovwa-dbtable-tracker-state`



## 6. Acceptance Criteria

- [ ] Notifications are delivered for first over-limit event within 5 seconds when tracker is RUNNING and user is active.
- [ ] Repeat reminders are not delivered more frequently than repeat_interval_seconds.

## 7. Additional Context (optional)

If notifications cannot be delivered (suppressed by system settings or subprocess failures), tracking continues and the user can still query status via the CLI.

Out of scope / not applicable (v1):
- No persistence of notification scheduling state across daemon restarts.
- No escalation policy beyond repeat reminders (no sounds, no focus-mode overrides).
- No network calls; no remote push notifications.

