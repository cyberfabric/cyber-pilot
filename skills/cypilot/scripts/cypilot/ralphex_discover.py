"""
ralphex Discovery Module - Locate and validate the ralphex executable.

Handles PATH lookup, persisted config reuse, and availability validation
for the ralphex external executor integration.

@cpt-algo:cpt-cypilot-algo-ralphex-delegation-discover:p1
@cpt-algo:cpt-cypilot-algo-ralphex-delegation-validate:p1
"""

import logging
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional

from .utils import toml_utils

logger = logging.getLogger(__name__)

_VERSION_RES = (
    re.compile(r"^v?\d+\.\d+$"),
    re.compile(r"^v?\d+\.\d+\.\d+$"),
    re.compile(r"^v?\d+\.\d+\.\d+[-+].+$"),
)

# @cpt-begin:cpt-cypilot-algo-ralphex-delegation-validate:p1:inst-if-none
INSTALL_GUIDANCE = (
    "ralphex is not installed. Install via one of:\n"
    "  - Homebrew (macOS): brew install cyberfabric/tap/ralphex\n"
    "  - Go: go install github.com/cyberfabric/ralphex@latest\n"
    "  - Binary releases: https://github.com/cyberfabric/ralphex/releases"
)
# @cpt-end:cpt-cypilot-algo-ralphex-delegation-validate:p1:inst-if-none


def _extract_version(output: str) -> Optional[str]:
    for raw_token in output.split():
        token = raw_token.strip(" \t\r\n,;:()[]{}<>'\"")
        for pattern in _VERSION_RES:
            if pattern.fullmatch(token):
                return token[1:] if token.startswith("v") else token
    return None


def discover(config: dict) -> Optional[str]:
    """Discover the ralphex executable.

    Search order:
    1. PATH lookup via ``shutil.which``
    2. Persisted path from ``core.toml`` ``[integrations.ralphex].executable_path``
    3. Verify persisted binary still exists on disk

    Args:
        config: Parsed core.toml data dict.

    Returns:
        Absolute path to the ralphex binary, or ``None`` if not found.
    """
    # @cpt-begin:cpt-cypilot-algo-ralphex-delegation-discover:p1:inst-search-path
    path = shutil.which("ralphex")
    if path is not None:
        logger.info("ralphex found on PATH: %s", path)
        return path
    # @cpt-end:cpt-cypilot-algo-ralphex-delegation-discover:p1:inst-search-path

    # @cpt-begin:cpt-cypilot-algo-ralphex-delegation-discover:p1:inst-read-config
    persisted = (
        config
        .get("integrations", {})
        .get("ralphex", {})
        .get("executable_path", "")
    )
    # @cpt-end:cpt-cypilot-algo-ralphex-delegation-discover:p1:inst-read-config

    # @cpt-begin:cpt-cypilot-algo-ralphex-delegation-discover:p1:inst-verify-persisted
    if persisted and os.path.isfile(persisted):
        logger.info("ralphex found via persisted config: %s", persisted)
        # @cpt-begin:cpt-cypilot-algo-ralphex-delegation-discover:p1:inst-return-path
        return persisted
        # @cpt-end:cpt-cypilot-algo-ralphex-delegation-discover:p1:inst-return-path
    # @cpt-end:cpt-cypilot-algo-ralphex-delegation-discover:p1:inst-verify-persisted

    # @cpt-begin:cpt-cypilot-algo-ralphex-delegation-discover:p1:inst-return-none
    logger.info("ralphex not found on PATH or in persisted config")
    return None
    # @cpt-end:cpt-cypilot-algo-ralphex-delegation-discover:p1:inst-return-none


def validate(ralphex_path: Optional[str]) -> Dict[str, object]:
    """Validate ralphex availability at the given path.

    Runs ``ralphex --version`` and parses the output to determine
    compatibility.

    Args:
        ralphex_path: Absolute path to the ralphex executable, or None.

    Returns:
        Dict with keys:
        - ``status``: one of ``"available"``, ``"unavailable"``, ``"incompatible"``
        - ``version``: parsed version string (if available)
        - ``message``: human-readable diagnostic message
    """
    # @cpt-begin:cpt-cypilot-algo-ralphex-delegation-validate:p1:inst-if-none
    if ralphex_path is None:
        return {
            "status": "unavailable",
            "version": None,
            "message": INSTALL_GUIDANCE,
        }
    # @cpt-end:cpt-cypilot-algo-ralphex-delegation-validate:p1:inst-if-none

    # @cpt-begin:cpt-cypilot-algo-ralphex-delegation-validate:p1:inst-run-version
    try:
        proc = subprocess.run(
            [ralphex_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        logger.warning("ralphex --version failed: %s", exc)
        return {
            "status": "incompatible",
            "version": None,
            "message": (
                f"Failed to run ralphex at {ralphex_path}: {exc}\n"
                "Please update or reinstall ralphex."
            ),
        }
    # @cpt-end:cpt-cypilot-algo-ralphex-delegation-validate:p1:inst-run-version

    # @cpt-begin:cpt-cypilot-algo-ralphex-delegation-validate:p1:inst-parse-version
    output = proc.stdout.strip() or proc.stderr.strip()
    version = _extract_version(output)
    # @cpt-end:cpt-cypilot-algo-ralphex-delegation-validate:p1:inst-parse-version

    # @cpt-begin:cpt-cypilot-algo-ralphex-delegation-validate:p1:inst-return-available
    if proc.returncode == 0 and version:
        logger.info("ralphex %s validated at %s", version, ralphex_path)
        return {
            "status": "available",
            "version": version,
            "message": f"ralphex {version} available at {ralphex_path}",
        }
    # @cpt-end:cpt-cypilot-algo-ralphex-delegation-validate:p1:inst-return-available

    # @cpt-begin:cpt-cypilot-algo-ralphex-delegation-validate:p1:inst-return-incompatible
    logger.warning("ralphex at %s returned incompatible output: %s", ralphex_path, output)
    return {
        "status": "incompatible",
        "version": version,
        "message": (
            f"ralphex at {ralphex_path} returned unexpected output.\n"
            "Please update to a compatible version:\n"
            "  - Homebrew: brew upgrade cyberfabric/tap/ralphex\n"
            "  - Go: go install github.com/cyberfabric/ralphex@latest\n"
            "  - Binary releases: https://github.com/cyberfabric/ralphex/releases"
        ),
    }
    # @cpt-end:cpt-cypilot-algo-ralphex-delegation-validate:p1:inst-return-incompatible


# @cpt-begin:cpt-cypilot-flow-ralphex-delegation-discover:p1:inst-persist-path
def persist_path(config_path: Path, ralphex_path: str) -> None:
    """Persist discovered ralphex path to core.toml.

    Loads the existing config, updates ``[integrations.ralphex].executable_path``,
    and writes it back.

    Args:
        config_path: Path to core.toml.
        ralphex_path: Absolute path to persist.
    """
    data = toml_utils.load(config_path)
    integrations = data.setdefault("integrations", {})
    ralphex_section = integrations.setdefault("ralphex", {})
    if ralphex_section.get("executable_path") == ralphex_path:
        return
    ralphex_section["executable_path"] = ralphex_path
    toml_utils.dump(data, config_path, header_comment="Cypilot project configuration")
    logger.info("Persisted ralphex path to %s", config_path)
# @cpt-end:cpt-cypilot-flow-ralphex-delegation-discover:p1:inst-persist-path
