"""Pure notification decision logic.

This module does not perform OS notification delivery; it only decides when to notify
and updates in-memory scheduling state.
"""

from __future__ import annotations

import time
from dataclasses import replace

from .models import Config, TrackerState, TrackerStatus


# @cpt-algo:cpt-overwork-alert-algo-notifications-should-notify:p1
def should_notify(*, state: TrackerState, config: Config, idle_seconds: int | None, now: float) -> bool:
    """Return True if a notification should be delivered now."""
    # @cpt-begin:cpt-overwork-alert-algo-notifications-should-notify:p1:inst-not-running
    if state.status != TrackerStatus.RUNNING:
        return False
    # @cpt-end:cpt-overwork-alert-algo-notifications-should-notify:p1:inst-not-running

    # @cpt-begin:cpt-overwork-alert-algo-notifications-should-notify:p1:inst-currently-idle
    if idle_seconds is None:
        return False

    if idle_seconds >= config.idle_threshold_seconds:
        return False
    # @cpt-end:cpt-overwork-alert-algo-notifications-should-notify:p1:inst-currently-idle

    # @cpt-begin:cpt-overwork-alert-algo-notifications-should-notify:p1:inst-not-over-limit
    if state.active_time_seconds <= config.limit_seconds:
        return False
    # @cpt-end:cpt-overwork-alert-algo-notifications-should-notify:p1:inst-not-over-limit

    # @cpt-begin:cpt-overwork-alert-algo-notifications-should-notify:p1:inst-first-alert
    if state.over_limit_since is None:
        return True
    # @cpt-end:cpt-overwork-alert-algo-notifications-should-notify:p1:inst-first-alert

    if state.last_reminder_at is None:
        return True

    # @cpt-begin:cpt-overwork-alert-algo-notifications-should-notify:p1:inst-repeat-alert
    if (now - state.last_reminder_at) >= config.repeat_interval_seconds:
        return True
    # @cpt-end:cpt-overwork-alert-algo-notifications-should-notify:p1:inst-repeat-alert

    # @cpt-begin:cpt-overwork-alert-algo-notifications-should-notify:p1:inst-default-no
    return False
    # @cpt-end:cpt-overwork-alert-algo-notifications-should-notify:p1:inst-default-no


# @cpt-dod:cpt-overwork-alert-dod-notifications-alert-and-repeat:p1
def apply_notification_policy(
    *,
    state: TrackerState,
    config: Config,
    idle_seconds: int | None,
    now: float | None = None,
) -> TrackerState:
    """Update notification scheduling state after a notification is delivered."""
    # @cpt-state:cpt-overwork-alert-state-notifications-over-limit:p1
    n = time.time() if now is None else now

    if not should_notify(state=state, config=config, idle_seconds=idle_seconds, now=n):
        return state

    if state.over_limit_since is None:
        # @cpt-begin:cpt-overwork-alert-state-notifications-over-limit:p1:inst-transition-first
        return replace(state, over_limit_since=n, last_reminder_at=n)
        # @cpt-end:cpt-overwork-alert-state-notifications-over-limit:p1:inst-transition-first

    # @cpt-begin:cpt-overwork-alert-state-notifications-over-limit:p1:inst-transition-remind
    return replace(state, last_reminder_at=n)
    # @cpt-end:cpt-overwork-alert-state-notifications-over-limit:p1:inst-transition-remind
