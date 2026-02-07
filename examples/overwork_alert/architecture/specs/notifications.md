<!-- cpt:#:spec -->
# Spec: Notifications

<!-- cpt:id-ref:spec has="task" -->
- [x] - `cpt-overwork-alert-spec-notifications`
<!-- cpt:id-ref:spec -->

<!-- cpt:##:context -->
## 1. Spec Context

<!-- cpt:overview -->
### 1. Overview
This spec defines when and how the daemon notifies the user after exceeding the configured active-time limit. It covers the first alert and repeat reminders while the user remains active and tracking is running.

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
<!-- cpt:overview -->

<!-- cpt:paragraph:purpose -->
### 2. Purpose
Ensure the user receives timely, repeatable overwork alerts once the active-time limit is exceeded.
<!-- cpt:paragraph:purpose -->

### 3. Actors
<!-- cpt:id-ref:actor -->
- `cpt-overwork-alert-actor-user`
- `cpt-overwork-alert-actor-macos`
<!-- cpt:id-ref:actor -->

### 4. References
<!-- cpt:list:references -->
- Overall Design: [DESIGN.md](../DESIGN.md)
- Related spec: tracker-core.md
<!-- cpt:list:references -->
<!-- cpt:##:context -->

<!-- cpt:##:flows -->
## 2. Actor Flows

<!-- cpt:###:flow-title repeat="many" -->
### Send first over-limit alert

<!-- cpt:id:flow has="task" to_code="true" -->
- [x] **ID**: `cpt-overwork-alert-spec-notifications-flow-first-alert`

**Actors**:
<!-- cpt:id-ref:actor -->
- `cpt-overwork-alert-actor-user`
<!-- cpt:id-ref:actor -->

<!-- cpt:cdsl:flow-steps -->
1. [x] - `p1` - Daemon observes active_time_seconds > limit_seconds - `inst-detect-over-limit`
2. [x] - `p1` - **IF** tracker status is not RUNNING **RETURN** do_not_notify - `inst-skip-on-not-running`
3. [x] - `p1` - **IF** current idle_seconds >= idle_threshold_seconds **RETURN** do_not_notify - `inst-skip-on-idle`
4. [x] - `p1` - **IF** over-limit has not been notified yet: - `inst-check-first-alert`
5. [x] - `p1` - Notification Sender delivers macOS notification (title + message) - `inst-send-notification`
6. [x] - `p1` - Daemon records over_limit_since and last_reminder_at - `inst-record-notify-state`
<!-- cpt:cdsl:flow-steps -->
<!-- cpt:id:flow -->
<!-- cpt:###:flow-title repeat="many" -->

<!-- cpt:###:flow-title repeat="many" -->
### Send repeat reminder while still over limit

<!-- cpt:id:flow has="task" to_code="true" -->
- [x] **ID**: `cpt-overwork-alert-spec-notifications-flow-repeat-reminder`

**Actors**:
<!-- cpt:id-ref:actor -->
- `cpt-overwork-alert-actor-user`
<!-- cpt:id-ref:actor -->

<!-- cpt:cdsl:flow-steps -->
1. [x] - `p1` - Daemon is over limit and user remains active - `inst-still-over-limit`
2. [x] - `p1` - **IF** tracker status is not RUNNING **RETURN** do_not_notify - `inst-skip-repeat-on-not-running`
3. [x] - `p1` - **IF** current idle_seconds >= idle_threshold_seconds **RETURN** do_not_notify - `inst-skip-repeat-on-idle`
4. [x] - `p1` - **IF** now - last_reminder_at >= repeat_interval_seconds: - `inst-check-interval`
5. [x] - `p1` - Notification Sender delivers macOS reminder notification - `inst-send-reminder`
6. [x] - `p1` - Daemon updates last_reminder_at - `inst-update-last-reminder`
<!-- cpt:cdsl:flow-steps -->
<!-- cpt:id:flow -->
<!-- cpt:###:flow-title repeat="many" -->

<!-- cpt:##:flows -->

<!-- cpt:##:algorithms -->
## 3. Algorithms

<!-- cpt:###:algo-title repeat="many" -->
### Determine whether to send a notification

<!-- cpt:id:algo has="task" to_code="true" -->
- [x] **ID**: `cpt-overwork-alert-spec-notifications-algo-should-notify`

<!-- cpt:cdsl:algo-steps -->
1. [x] - `p1` - **IF** tracker status is not RUNNING **RETURN** do_not_notify - `inst-not-running`
2. [x] - `p1` - **IF** current idle_seconds >= idle_threshold_seconds **RETURN** do_not_notify - `inst-currently-idle`
3. [x] - `p1` - **IF** active_time_seconds <= limit_seconds **RETURN** do_not_notify - `inst-not-over-limit`
4. [x] - `p1` - **IF** first alert not sent yet **RETURN** notify_now - `inst-first-alert`
5. [x] - `p1` - **IF** now - last_reminder_at >= repeat_interval_seconds **RETURN** notify_now - `inst-repeat-alert`
6. [x] - `p1` - **RETURN** do_not_notify - `inst-default-no`
<!-- cpt:cdsl:algo-steps -->
<!-- cpt:id:algo -->
<!-- cpt:###:algo-title repeat="many" -->

<!-- cpt:##:algorithms -->

<!-- cpt:##:states -->
## 4. States

<!-- cpt:###:state-title repeat="many" -->
### Over-limit notification state

<!-- cpt:id:state has="task" to_code="true" -->
- [x] **ID**: `cpt-overwork-alert-spec-notifications-state-over-limit`

<!-- cpt:cdsl:state-transitions -->
1. [x] - `p1` - **FROM** UNDER_LIMIT **TO** OVER_LIMIT_FIRST_SENT **WHEN** first alert is delivered - `inst-transition-first`
2. [x] - `p1` - **FROM** OVER_LIMIT_FIRST_SENT **TO** OVER_LIMIT_REMINDING **WHEN** reminder is delivered - `inst-transition-remind`
3. [x] - `p1` - **FROM** OVER_LIMIT_REMINDING **TO** UNDER_LIMIT **WHEN** session is reset - `inst-transition-reset`
<!-- cpt:cdsl:state-transitions -->
<!-- cpt:id:state -->
<!-- cpt:###:state-title repeat="many" -->

<!-- cpt:##:states -->

<!-- cpt:##:requirements -->
## 5. Definition of Done

<!-- cpt:###:req-title repeat="many" -->
### Over-limit notifications and repeat reminders

<!-- cpt:id:req has="priority,task" to_code="true" -->
- [x] `p1` - **ID**: `cpt-overwork-alert-spec-notifications-req-alert-and-repeat`

<!-- cpt:paragraph:req-body -->
When active time exceeds the configured limit while tracking is RUNNING and the user is active (idle below threshold), the system sends a macOS notification within 5 seconds. While the user remains active and over limit, the system repeats notifications at the configured repeat interval.
<!-- cpt:paragraph:req-body -->

**Implementation details**:
<!-- cpt:list:req-impl -->
- Component: `cpt-overwork-alert-component-notifier`
- Data: `cpt-overwork-alert-dbtable-tracker-state`
<!-- cpt:list:req-impl -->

**Implements**:
<!-- cpt:id-ref:flow has="priority" -->
- `p1` - `cpt-overwork-alert-spec-notifications-flow-first-alert`
- `p1` - `cpt-overwork-alert-spec-notifications-flow-repeat-reminder`
<!-- cpt:id-ref:flow -->

<!-- cpt:id-ref:algo has="priority" -->
- `p1` - `cpt-overwork-alert-spec-notifications-algo-should-notify`
<!-- cpt:id-ref:algo -->

**Covers (PRD)**:
<!-- cpt:id-ref:fr -->
- `cpt-overwork-alert-fr-notify-on-limit`
<!-- cpt:id-ref:fr -->

<!-- cpt:id-ref:nfr -->
- `cpt-overwork-alert-nfr-reliability`
<!-- cpt:id-ref:nfr -->

**Covers (DESIGN)**:
<!-- cpt:id-ref:principle -->
- `cpt-overwork-alert-principle-explicit-control`
<!-- cpt:id-ref:principle -->

<!-- cpt:id-ref:constraint -->
- `cpt-overwork-alert-constraint-no-auto-reset-no-persist`
<!-- cpt:id-ref:constraint -->

<!-- cpt:id-ref:component -->
- `cpt-overwork-alert-component-notifier`
- `cpt-overwork-alert-component-daemon`
<!-- cpt:id-ref:component -->

<!-- cpt:id-ref:seq -->
- `cpt-overwork-alert-seq-run-and-alert`
<!-- cpt:id-ref:seq -->

<!-- cpt:id-ref:dbtable -->
- `cpt-overwork-alert-dbtable-tracker-state`
<!-- cpt:id-ref:dbtable -->

<!-- cpt:id:req -->
<!-- cpt:###:req-title repeat="many" -->

<!-- cpt:##:requirements -->

<!-- cpt:##:additional-context -->
## 6. Additional Context (optional)

<!-- cpt:free:context-notes -->
If notifications cannot be delivered (suppressed by system settings or subprocess failures), tracking continues and the user can still query status via the CLI.

Out of scope / not applicable (v1):
- No persistence of notification scheduling state across daemon restarts.
- No escalation policy beyond repeat reminders (no sounds, no focus-mode overrides).
- No network calls; no remote push notifications.
<!-- cpt:free:context-notes -->
<!-- cpt:##:additional-context -->

<!-- cpt:#:spec -->
