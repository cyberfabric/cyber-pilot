"""LaunchAgent install/uninstall for Overwork Alert (user-level only)."""

from __future__ import annotations

import plistlib
import subprocess
import sys
from pathlib import Path

from .config import DEFAULT_CONFIG_PATH


# @cpt-begin:cpt-ex-ovwa-algo-launchagent-autostart-build-plist:p1:inst-choose-label
DEFAULT_LABEL = "com.cypilot.overwork-alert"
# @cpt-end:cpt-ex-ovwa-algo-launchagent-autostart-build-plist:p1:inst-choose-label


def get_launchagent_plist_path(label: str = DEFAULT_LABEL) -> Path:
    """Return the expected LaunchAgent plist path for the given label."""
    return Path.home() / "Library" / "LaunchAgents" / f"{label}.plist"


# @cpt-algo:cpt-ex-ovwa-algo-launchagent-autostart-build-plist:p1
def build_plist_bytes(*, label: str, src_dir: Path) -> bytes:
    """Build plist content for the user LaunchAgent."""
    env = {"PYTHONPATH": str(src_dir)}

    # @cpt-begin:cpt-ex-ovwa-algo-launchagent-autostart-build-plist:p1:inst-set-args
    program_args = [
        sys.executable,
        "-m",
        "overwork_alert",
        "start",
        "--config",
        str(DEFAULT_CONFIG_PATH),
    ]
    # @cpt-end:cpt-ex-ovwa-algo-launchagent-autostart-build-plist:p1:inst-set-args

    payload = {
        "Label": label,
        "ProgramArguments": program_args,
        # @cpt-begin:cpt-ex-ovwa-algo-launchagent-autostart-build-plist:p1:inst-set-options
        "RunAtLoad": True,
        "KeepAlive": True,
        # @cpt-end:cpt-ex-ovwa-algo-launchagent-autostart-build-plist:p1:inst-set-options
        # @cpt-begin:cpt-ex-ovwa-algo-launchagent-autostart-build-plist:p1:inst-set-throttle
        "ThrottleInterval": 10,
        # @cpt-end:cpt-ex-ovwa-algo-launchagent-autostart-build-plist:p1:inst-set-throttle
        "EnvironmentVariables": env,
        "StandardOutPath": str(Path.home() / "Library" / "Logs" / "overwork-alert.log"),
        "StandardErrorPath": str(Path.home() / "Library" / "Logs" / "overwork-alert.err.log"),
    }

    # @cpt-begin:cpt-ex-ovwa-algo-launchagent-autostart-build-plist:p1:inst-return-plist
    return plistlib.dumps(payload)
    # @cpt-end:cpt-ex-ovwa-algo-launchagent-autostart-build-plist:p1:inst-return-plist


def _launchctl(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["launchctl", *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


# @cpt-flow:cpt-ex-ovwa-flow-launchagent-autostart-install:p1
def install(*, src_dir: Path, label: str = DEFAULT_LABEL) -> None:
    """Install (or update) the LaunchAgent plist and load it via launchctl."""
    # @cpt-dod:cpt-ex-ovwa-dod-launchagent-autostart-install-and-run:p1
    # @cpt-state:cpt-ex-ovwa-state-launchagent-autostart-installation:p1
    plist_path = get_launchagent_plist_path(label)
    plist_path.parent.mkdir(parents=True, exist_ok=True)

    # @cpt-begin:cpt-ex-ovwa-flow-launchagent-autostart-install:p1:inst-build-plist
    desired = build_plist_bytes(label=label, src_dir=src_dir)
    # @cpt-end:cpt-ex-ovwa-flow-launchagent-autostart-install:p1:inst-build-plist

    # @cpt-begin:cpt-ex-ovwa-flow-launchagent-autostart-install:p1:inst-install-idempotent
    if plist_path.exists():
        try:
            existing = plist_path.read_bytes()
        except OSError:
            existing = b""
        should_write = existing != desired
    else:
        should_write = True
    # @cpt-end:cpt-ex-ovwa-flow-launchagent-autostart-install:p1:inst-install-idempotent

    if should_write:
        try:
            # @cpt-begin:cpt-ex-ovwa-flow-launchagent-autostart-install:p1:inst-write-plist
            plist_path.write_bytes(desired)
            # @cpt-end:cpt-ex-ovwa-flow-launchagent-autostart-install:p1:inst-write-plist
        except OSError as e:
            # @cpt-begin:cpt-ex-ovwa-flow-launchagent-autostart-install:p1:inst-write-plist-error
            raise RuntimeError("Failed to write plist") from e
            # @cpt-end:cpt-ex-ovwa-flow-launchagent-autostart-install:p1:inst-write-plist-error

    _launchctl("unload", str(plist_path))

    # @cpt-begin:cpt-ex-ovwa-flow-launchagent-autostart-install:p1:inst-launchctl-load
    proc = _launchctl("load", str(plist_path))
    # @cpt-end:cpt-ex-ovwa-flow-launchagent-autostart-install:p1:inst-launchctl-load
    if proc.returncode != 0:
        # @cpt-begin:cpt-ex-ovwa-flow-launchagent-autostart-install:p1:inst-launchctl-load-error
        raise RuntimeError(f"launchctl load failed: {proc.stderr.strip()}")
        # @cpt-end:cpt-ex-ovwa-flow-launchagent-autostart-install:p1:inst-launchctl-load-error

    # @cpt-begin:cpt-ex-ovwa-state-launchagent-autostart-installation:p1:inst-transition-installed
    return
    # @cpt-end:cpt-ex-ovwa-state-launchagent-autostart-installation:p1:inst-transition-installed


# @cpt-flow:cpt-ex-ovwa-flow-launchagent-autostart-uninstall:p1
def uninstall(*, label: str = DEFAULT_LABEL) -> None:
    """Unload and remove the user LaunchAgent plist (idempotent)."""
    plist_path = get_launchagent_plist_path(label)

    if not plist_path.exists():
        # @cpt-begin:cpt-ex-ovwa-flow-launchagent-autostart-uninstall:p1:inst-uninstall-idempotent
        return
        # @cpt-end:cpt-ex-ovwa-flow-launchagent-autostart-uninstall:p1:inst-uninstall-idempotent

    # @cpt-begin:cpt-ex-ovwa-flow-launchagent-autostart-uninstall:p1:inst-launchctl-unload
    proc = _launchctl("unload", str(plist_path))
    # @cpt-end:cpt-ex-ovwa-flow-launchagent-autostart-uninstall:p1:inst-launchctl-unload
    if proc.returncode != 0:
        # @cpt-begin:cpt-ex-ovwa-flow-launchagent-autostart-uninstall:p1:inst-launchctl-unload-warn
        pass
        # @cpt-end:cpt-ex-ovwa-flow-launchagent-autostart-uninstall:p1:inst-launchctl-unload-warn

    try:
        # @cpt-begin:cpt-ex-ovwa-flow-launchagent-autostart-uninstall:p1:inst-delete-plist
        plist_path.unlink()
        # @cpt-end:cpt-ex-ovwa-flow-launchagent-autostart-uninstall:p1:inst-delete-plist
    except OSError as e:
        # @cpt-begin:cpt-ex-ovwa-flow-launchagent-autostart-uninstall:p1:inst-delete-plist-error
        raise RuntimeError("Failed to delete plist") from e
        # @cpt-end:cpt-ex-ovwa-flow-launchagent-autostart-uninstall:p1:inst-delete-plist-error

    # @cpt-begin:cpt-ex-ovwa-state-launchagent-autostart-installation:p1:inst-transition-removed
    return
    # @cpt-end:cpt-ex-ovwa-state-launchagent-autostart-installation:p1:inst-transition-removed
