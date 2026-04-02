"""
Usage Telemetry for Cypilot CLI Proxy

Non-blocking telemetry: collects invocation data, writes to local log,
optionally sends to remote endpoint in OTLP Logs format.

Uses only Python stdlib. Never blocks or slows down the main CLI.

@cpt-dod:cpt-cypilot-dod-core-infra-telemetry:p1
"""

import json
import os
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from urllib.request import Request, urlopen


LOG_DIR = Path.home() / ".cypilot" / "logs"
DEFAULT_RETENTION_DAYS = 5
HTTP_TIMEOUT = 5
_SKIP_COMMANDS = {"--version", "--help", "-h"}
_ALLOWED_SCHEMES = ("http://", "https://")  # NOSONAR(S5332) HTTP is acceptable for internal OTEL collectors


def track_invocation(args: List[str]) -> None:
    """
    Fire-and-forget telemetry for a CLI invocation.

    Spawns a daemon thread that:
    1. Collects git user info via a single subprocess call
    2. Appends a JSONL record to ~/.cypilot/logs/YYYY-MM-DD.log
    3. Rotates old log files if a new day's file was just created
    4. POSTs OTLP Logs JSON to CYPILOT_TELEMETRY_URL (if set)
    5. Logs HTTP errors to the same log file

    Disabled entirely when CYPILOT_TELEMETRY=0.
    Skipped for --version and --help (no useful data, fast exit risk).
    """
    if os.environ.get("CYPILOT_TELEMETRY") == "0":
        return

    command = args[0] if args else ""

    if command in _SKIP_COMMANDS:
        return

    thread = threading.Thread(
        target=_telemetry_worker,
        args=(command,),
        daemon=True,
    )
    thread.start()


def _telemetry_worker(command: str) -> None:
    """Background worker: collect data, write log, send HTTP."""
    try:
        git_info = _collect_git_info()
        now = datetime.now(timezone.utc)
        time_unix_nano = str(int(now.timestamp() * 1_000_000_000))

        from cypilot_proxy import __version__

        record = {
            "timestamp": now.isoformat(),
            "git_user_name": git_info.get("user.name", ""),
            "git_user_email": git_info.get("user.email", ""),
            "git_remote": git_info.get("remote.origin.url", ""),
            "command": command,
            "cypilot_version": __version__,
        }

        is_new_file = _append_log(record, now)

        if is_new_file:
            _rotate_logs()

        telemetry_url = os.environ.get("CYPILOT_TELEMETRY_URL")
        if telemetry_url and telemetry_url.startswith(_ALLOWED_SCHEMES):
            otlp_payload = _build_otlp_logs(
                record=record,
                time_unix_nano=time_unix_nano,
                version=__version__,
            )
            _send_http(telemetry_url, otlp_payload)
        elif telemetry_url:
            _log_error(f"Telemetry URL rejected: scheme must be http:// or https:// (got {telemetry_url})")
    except Exception as exc:  # pylint: disable=broad-exception-caught
        _log_error(f"Telemetry worker error: {exc}")


def _collect_git_info() -> Dict[str, str]:
    """
    Collect git user.name, user.email, and remote.origin.url
    via a single subprocess call.
    """
    try:
        result = subprocess.run(
            [
                "git", "config", "--get-regexp",
                r"^(user\.(name|email)|remote\.origin\.url)$",
            ],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        info: Dict[str, str] = {}
        for line in result.stdout.strip().splitlines():
            parts = line.split(" ", 1)
            if len(parts) == 2:
                info[parts[0]] = parts[1]
        return info
    except (OSError, subprocess.TimeoutExpired):
        return {}


def _append_log(record: dict, now: Optional[datetime] = None) -> bool:
    """
    Append a JSONL record to today's log file.

    Returns True if the file was just created (new day).
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    today = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"{today}.log"

    is_new = not log_file.exists()

    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return is_new


def _rotate_logs() -> None:
    """Delete log files older than retention period."""
    try:
        retention_days = int(
            os.environ.get("CYPILOT_TELEMETRY_RETENTION_DAYS", DEFAULT_RETENTION_DAYS)
        )
    except ValueError:
        retention_days = DEFAULT_RETENTION_DAYS

    retention_days = max(1, retention_days)
    cutoff = time.time() - (retention_days * 86400)

    try:
        for log_file in LOG_DIR.glob("*.log"):
            if log_file.stat().st_mtime < cutoff:
                log_file.unlink(missing_ok=True)
    except OSError:
        pass


def _build_otlp_logs(
    record: dict,
    time_unix_nano: str,
    version: str,
) -> dict:
    """Build an OTLP Logs JSON payload."""
    return {
        "resourceLogs": [{
            "resource": {
                "attributes": [
                    _str_attr("service.name", "cypilot"),
                    _str_attr("service.version", version),
                ],
            },
            "scopeLogs": [{
                "scope": {"name": "cypilot.telemetry"},
                "logRecords": [{
                    "timeUnixNano": time_unix_nano,
                    "severityNumber": 9,
                    "severityText": "INFO",
                    "body": {"stringValue": "cpt.invocation"},
                    "attributes": [
                        _str_attr("enduser.name", record.get("git_user_name", "")),
                        _str_attr("enduser.email", record.get("git_user_email", "")),
                        _str_attr("vcs.repository.url.full", record.get("git_remote", "")),
                        _str_attr("cypilot.command", record.get("command", "")),
                    ],
                }],
            }],
        }],
    }


def _str_attr(key: str, value: str) -> dict:
    """Build an OTLP string attribute."""
    return {"key": key, "value": {"stringValue": value}}


def _send_http(url: str, payload: dict) -> None:
    """POST JSON payload to the telemetry endpoint. Log errors to file."""
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            resp.read()
    except OSError as exc:
        _log_error(f"Telemetry HTTP error: {exc}")


def _log_error(message: str) -> None:
    """Append an error record to today's log file."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc)
        log_file = LOG_DIR / f"{now.strftime('%Y-%m-%d')}.log"

        error_record = {
            "timestamp": now.isoformat(),
            "level": "ERROR",
            "message": message,
        }
        with log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(error_record, ensure_ascii=False) + "\n")
    except OSError:
        pass
