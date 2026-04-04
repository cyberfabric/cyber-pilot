"""Shared core.toml config loading for delegate and doctor commands.

@cpt-algo:cpt-cypilot-algo-ralphex-delegation-discover:p1
"""

from __future__ import annotations

import logging
from pathlib import Path

from ..utils._tomllib_compat import tomllib

logger = logging.getLogger(__name__)

# @cpt-begin:cpt-cypilot-algo-ralphex-delegation-discover:p1:inst-read-config
_ADAPTER_DIRS = (".bootstrap", "cypilot", ".cypilot", ".cpt")


def load_core_config(project_root: Path) -> dict:
    """Load core.toml from the project's adapter config directory.

    Searches ``.bootstrap`` first, then ``cypilot``.
    Returns the parsed config dict, or empty dict if not found.
    """
    path = find_core_toml(project_root)
    if path is None:
        return {}
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except (OSError, ValueError) as exc:
        logger.warning("Failed to parse %s: %s", path, exc)
        return {}


def find_core_toml(project_root: Path) -> Path | None:
    """Find the core.toml path for config persistence.

    Returns the first matching path, or ``None``.
    """
    for adapter in _ADAPTER_DIRS:
        config_path = project_root / adapter / "config" / "core.toml"
        if config_path.is_file():
            return config_path
    return None
# @cpt-end:cpt-cypilot-algo-ralphex-delegation-discover:p1:inst-read-config
