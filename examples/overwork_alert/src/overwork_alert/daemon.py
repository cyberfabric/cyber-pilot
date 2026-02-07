"""Daemon loop for Overwork Alert.

Implements:
- tracker-core tick loop + accumulation
- notification policy + delivery
- local control channel command handling
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import replace
from pathlib import Path

from .config import load_config
from .idle import get_idle_seconds
from .ipc import ControlRequest, ControlServer
from .models import Config, TrackerState, TrackerStatus
from .notification_policy import apply_notification_policy, should_notify
from .notify import send_notification

logger = logging.getLogger(__name__)


def _clamp_delta_seconds(*, delta_seconds: float, max_tick_delta_seconds: int) -> float:
    # @cpt-begin:cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time:p1:inst-handle-negative-delta
    if delta_seconds < 0:
        return 0
    # @cpt-end:cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time:p1:inst-handle-negative-delta

    # @cpt-begin:cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time:p1:inst-clamp-delta
    if delta_seconds > max_tick_delta_seconds:
        return float(max_tick_delta_seconds)
    # @cpt-end:cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time:p1:inst-clamp-delta
    return delta_seconds


# @cpt-algo:cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time:p1
def _accumulate_active_time(*, state: TrackerState, config: Config, now: float) -> TrackerState:
    """Accumulate session active time for one tick."""
    if state.last_tick_at is None:
        return replace(state, last_tick_at=now)

    # @cpt-begin:cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time:p1:inst-compute-delta
    raw_delta_seconds = now - state.last_tick_at
    # @cpt-end:cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time:p1:inst-compute-delta

    # @cpt-begin:cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time:p1:inst-compute-max-delta
    max_tick_delta_seconds = config.max_tick_delta_seconds
    # @cpt-end:cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time:p1:inst-compute-max-delta

    delta_seconds = _clamp_delta_seconds(
        delta_seconds=raw_delta_seconds,
        max_tick_delta_seconds=max_tick_delta_seconds,
    )

    # @cpt-begin:cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time:p1:inst-add-delta
    new_active_time_seconds = state.active_time_seconds + int(delta_seconds)
    # @cpt-end:cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time:p1:inst-add-delta

    updated = replace(state, active_time_seconds=new_active_time_seconds)

    # @cpt-begin:cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time:p1:inst-update-last-tick
    updated = replace(updated, last_tick_at=now)
    # @cpt-end:cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time:p1:inst-update-last-tick

    # @cpt-begin:cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time:p1:inst-return-updated-state
    return updated
    # @cpt-end:cpt-overwork-alert-spec-tracker-core-algo-accumulate-active-time:p1:inst-return-updated-state


# @cpt-flow:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1
def tick_once(*, state: TrackerState, config: Config, idle_seconds: int | None, now: float) -> TrackerState:
    """Execute one tracking tick, applying idle/paused guards and delta clamping."""
    # @cpt-begin:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1:inst-init-first-tick
    if state.last_tick_at is None:
        return replace(state, last_tick_at=now)
    # @cpt-end:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1:inst-init-first-tick

    # @cpt-begin:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1:inst-handle-idle-unavailable
    if idle_seconds is None:
        return replace(state, last_tick_at=now)
    # @cpt-end:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1:inst-handle-idle-unavailable

    # @cpt-begin:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1:inst-skip-on-idle
    if idle_seconds >= config.idle_threshold_seconds:
        return replace(state, last_tick_at=now)
    # @cpt-end:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1:inst-skip-on-idle

    # @cpt-begin:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1:inst-skip-on-paused
    if state.status == TrackerStatus.PAUSED:
        return replace(state, last_tick_at=now)
    # @cpt-end:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1:inst-skip-on-paused

    # @cpt-begin:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1:inst-accumulate
    updated = _accumulate_active_time(state=state, config=config, now=now)
    # @cpt-end:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1:inst-accumulate

    # @cpt-begin:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1:inst-return-state
    return updated
    # @cpt-end:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1:inst-return-state


def _notification_message(*, config: Config) -> tuple[str, str]:
    title = "Overwork Alert"
    msg = "You have exceeded your configured work limit. Consider taking a break."
    return title, msg


def _maybe_send_overwork_notification(
    *,
    state: TrackerState,
    config: Config,
    idle_seconds: int | None,
    now: float,
) -> TrackerState:
    """Evaluate notification policy and send notifications if needed."""

    # @cpt-begin:cpt-overwork-alert-spec-notifications-flow-first-alert:p1:inst-detect-over-limit
    # @cpt-begin:cpt-overwork-alert-spec-notifications-flow-repeat-reminder:p1:inst-still-over-limit
    is_over_limit = state.active_time_seconds > config.limit_seconds
    # @cpt-end:cpt-overwork-alert-spec-notifications-flow-repeat-reminder:p1:inst-still-over-limit
    # @cpt-end:cpt-overwork-alert-spec-notifications-flow-first-alert:p1:inst-detect-over-limit
    if not is_over_limit:
        return state

    # @cpt-begin:cpt-overwork-alert-spec-notifications-flow-first-alert:p1:inst-skip-on-not-running
    # @cpt-begin:cpt-overwork-alert-spec-notifications-flow-repeat-reminder:p1:inst-skip-repeat-on-not-running
    if state.status != TrackerStatus.RUNNING:
        return state
    # @cpt-end:cpt-overwork-alert-spec-notifications-flow-repeat-reminder:p1:inst-skip-repeat-on-not-running
    # @cpt-end:cpt-overwork-alert-spec-notifications-flow-first-alert:p1:inst-skip-on-not-running

    # @cpt-begin:cpt-overwork-alert-spec-notifications-flow-first-alert:p1:inst-skip-on-idle
    # @cpt-begin:cpt-overwork-alert-spec-notifications-flow-repeat-reminder:p1:inst-skip-repeat-on-idle
    if idle_seconds is None or idle_seconds >= config.idle_threshold_seconds:
        return state
    # @cpt-end:cpt-overwork-alert-spec-notifications-flow-repeat-reminder:p1:inst-skip-repeat-on-idle
    # @cpt-end:cpt-overwork-alert-spec-notifications-flow-first-alert:p1:inst-skip-on-idle

    is_first_alert = state.over_limit_since is None

    if is_first_alert:
        # @cpt-flow:cpt-overwork-alert-spec-notifications-flow-first-alert:p1
        # @cpt-begin:cpt-overwork-alert-spec-notifications-flow-first-alert:p1:inst-check-first-alert
        already_notified = state.over_limit_since is not None
        # @cpt-end:cpt-overwork-alert-spec-notifications-flow-first-alert:p1:inst-check-first-alert
        if already_notified:
            return state
    else:
        # @cpt-flow:cpt-overwork-alert-spec-notifications-flow-repeat-reminder:p1
        # @cpt-begin:cpt-overwork-alert-spec-notifications-flow-repeat-reminder:p1:inst-check-interval
        interval_ok = should_notify(state=state, config=config, idle_seconds=idle_seconds, now=now)
        # @cpt-end:cpt-overwork-alert-spec-notifications-flow-repeat-reminder:p1:inst-check-interval
        if not interval_ok:
            return state

    if not should_notify(state=state, config=config, idle_seconds=idle_seconds, now=now):
        return state

    title, msg = _notification_message(config=config)

    if is_first_alert:
        # @cpt-begin:cpt-overwork-alert-spec-notifications-flow-first-alert:p1:inst-send-notification
        ok = send_notification(title=title, message=msg)
        # @cpt-end:cpt-overwork-alert-spec-notifications-flow-first-alert:p1:inst-send-notification
    else:
        # @cpt-begin:cpt-overwork-alert-spec-notifications-flow-repeat-reminder:p1:inst-send-reminder
        ok = send_notification(title=title, message=msg)
        # @cpt-end:cpt-overwork-alert-spec-notifications-flow-repeat-reminder:p1:inst-send-reminder

    if not ok:
        logger.warning("Notification delivery failed")

    if is_first_alert:
        # @cpt-begin:cpt-overwork-alert-spec-notifications-flow-first-alert:p1:inst-record-notify-state
        updated = apply_notification_policy(state=state, config=config, idle_seconds=idle_seconds, now=now)
        # @cpt-end:cpt-overwork-alert-spec-notifications-flow-first-alert:p1:inst-record-notify-state
        return updated

    # @cpt-begin:cpt-overwork-alert-spec-notifications-flow-repeat-reminder:p1:inst-update-last-reminder
    updated = apply_notification_policy(state=state, config=config, idle_seconds=idle_seconds, now=now)
    # @cpt-end:cpt-overwork-alert-spec-notifications-flow-repeat-reminder:p1:inst-update-last-reminder
    return updated


class Daemon:
    """Long-running daemon process (single user session)."""

    def __init__(self, *, config_path: Path | None = None) -> None:
        self._config_path = config_path
        self._state = TrackerState()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._ipc: ControlServer | None = None

    def run_forever(self) -> None:
        """Run the daemon until a stop command is received."""
        config = load_config(self._config_path)
        self._ipc = ControlServer(socket_path=config.control_socket_path, request_handler=self._handle_request)
        self._ipc.start()

        try:
            while not self._stop_event.is_set():
                # @cpt-begin:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1:inst-load-config
                config = load_config(self._config_path)
                # @cpt-end:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1:inst-load-config
                now = time.time()

                # Align with tracker-core flow: if last_tick_at is not set, set it and return
                # without idle sampling (no accumulation).
                first_tick = False
                with self._lock:
                    if self._state.last_tick_at is None:
                        # @cpt-begin:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1:inst-init-first-tick
                        self._state = replace(self._state, last_tick_at=now)
                        # @cpt-end:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1:inst-init-first-tick
                        first_tick = True

                if first_tick:
                    time.sleep(config.tick_interval_seconds)
                    continue

                # @cpt-begin:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1:inst-read-idle
                idle_seconds = get_idle_seconds()
                # @cpt-end:cpt-overwork-alert-spec-tracker-core-flow-tick-loop:p1:inst-read-idle

                with self._lock:
                    # @cpt-req:cpt-overwork-alert-spec-tracker-core-req-idle-aware-accumulation:p1
                    self._state = tick_once(state=self._state, config=config, idle_seconds=idle_seconds, now=now)

                    # @cpt-req:cpt-overwork-alert-spec-notifications-req-alert-and-repeat:p1
                    self._state = _maybe_send_overwork_notification(
                        state=self._state,
                        config=config,
                        idle_seconds=idle_seconds,
                        now=now,
                    )

                time.sleep(config.tick_interval_seconds)
        finally:
            try:
                if self._ipc:
                    self._ipc.stop()
            except OSError:
                pass

    # @cpt-algo:cpt-overwork-alert-spec-cli-control-algo-handle-command:p1
    def _handle_request(self, req: ControlRequest) -> dict:
        """Handle a validated control request from the local Unix socket."""
        # @cpt-state:cpt-overwork-alert-spec-tracker-core-state-tracker-status:p1
        # @cpt-begin:cpt-overwork-alert-spec-cli-control-algo-handle-command:p1:inst-parse-cmd
        cmd = req.cmd
        # @cpt-end:cpt-overwork-alert-spec-cli-control-algo-handle-command:p1:inst-parse-cmd
        with self._lock:
            if cmd == "status":
                # @cpt-flow:cpt-overwork-alert-spec-cli-control-flow-status:p1
                config = load_config(self._config_path)
                # @cpt-begin:cpt-overwork-alert-spec-cli-control-algo-handle-command:p1:inst-handle-status
                # @cpt-begin:cpt-overwork-alert-spec-cli-control-flow-status:p1:inst-return-status
                return {"ok": True, "state": self._state.to_dict(config=config)}
                # @cpt-end:cpt-overwork-alert-spec-cli-control-flow-status:p1:inst-return-status
                # @cpt-end:cpt-overwork-alert-spec-cli-control-algo-handle-command:p1:inst-handle-status

            if cmd == "pause":
                # @cpt-flow:cpt-overwork-alert-spec-cli-control-flow-pause:p1
                # @cpt-begin:cpt-overwork-alert-spec-cli-control-flow-pause:p1:inst-daemon-pause
                # @cpt-begin:cpt-overwork-alert-spec-cli-control-algo-handle-command:p1:inst-handle-pause
                # @cpt-begin:cpt-overwork-alert-spec-tracker-core-state-tracker-status:p1:inst-transition-pause
                self._state.status = TrackerStatus.PAUSED
                # @cpt-end:cpt-overwork-alert-spec-tracker-core-state-tracker-status:p1:inst-transition-pause
                # @cpt-end:cpt-overwork-alert-spec-cli-control-algo-handle-command:p1:inst-handle-pause
                return {"ok": True}
                # @cpt-end:cpt-overwork-alert-spec-cli-control-flow-pause:p1:inst-daemon-pause

            if cmd == "resume":
                # @cpt-flow:cpt-overwork-alert-spec-cli-control-flow-resume:p1
                # @cpt-begin:cpt-overwork-alert-spec-cli-control-flow-resume:p1:inst-daemon-resume
                # @cpt-begin:cpt-overwork-alert-spec-cli-control-algo-handle-command:p1:inst-handle-resume
                # @cpt-begin:cpt-overwork-alert-spec-tracker-core-state-tracker-status:p1:inst-transition-resume
                self._state.status = TrackerStatus.RUNNING
                # @cpt-end:cpt-overwork-alert-spec-tracker-core-state-tracker-status:p1:inst-transition-resume
                # @cpt-end:cpt-overwork-alert-spec-cli-control-algo-handle-command:p1:inst-handle-resume
                return {"ok": True}
                # @cpt-end:cpt-overwork-alert-spec-cli-control-flow-resume:p1:inst-daemon-resume

            if cmd == "reset":
                # @cpt-flow:cpt-overwork-alert-spec-cli-control-flow-reset:p1
                # @cpt-begin:cpt-overwork-alert-spec-cli-control-algo-handle-command:p1:inst-handle-reset
                # @cpt-begin:cpt-overwork-alert-spec-cli-control-flow-reset:p1:inst-clear-state
                self._state.active_time_seconds = 0
                # @cpt-begin:cpt-overwork-alert-spec-notifications-state-over-limit:p1:inst-transition-reset
                self._state.over_limit_since = None
                self._state.last_reminder_at = None
                # @cpt-end:cpt-overwork-alert-spec-notifications-state-over-limit:p1:inst-transition-reset

                # @cpt-end:cpt-overwork-alert-spec-cli-control-flow-reset:p1:inst-clear-state

                # @cpt-end:cpt-overwork-alert-spec-cli-control-algo-handle-command:p1:inst-handle-reset
                return {"ok": True}

            if cmd == "stop":
                # @cpt-flow:cpt-overwork-alert-spec-cli-control-flow-stop:p1
                # @cpt-begin:cpt-overwork-alert-spec-cli-control-flow-stop:p1:inst-daemon-stop
                # @cpt-begin:cpt-overwork-alert-spec-cli-control-algo-handle-command:p1:inst-handle-stop
                self._stop_event.set()
                # @cpt-end:cpt-overwork-alert-spec-cli-control-algo-handle-command:p1:inst-handle-stop
                return {"ok": True}
                # @cpt-end:cpt-overwork-alert-spec-cli-control-flow-stop:p1:inst-daemon-stop

        # @cpt-begin:cpt-overwork-alert-spec-cli-control-algo-handle-command:p1:inst-handle-invalid-cmd
        return {"ok": False, "error": "invalid_command"}
        # @cpt-end:cpt-overwork-alert-spec-cli-control-algo-handle-command:p1:inst-handle-invalid-cmd


def run_daemon(*, config_path: Path | None = None) -> None:
    """Convenience wrapper to run the daemon."""
    Daemon(config_path=config_path).run_forever()
