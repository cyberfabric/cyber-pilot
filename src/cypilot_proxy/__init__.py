"""
Cypilot Global CLI Proxy

Thin proxy package that resolves skill targets (project-installed or cached)
and forwards commands. Installable via pipx.

@cpt-dod:cpt-cypilot-dod-core-infra-global-package:p1
"""

# @cpt-begin:cpt-cypilot-flow-version-config-resolve-version:p2:inst-resolve-proxy-version
try:
    from importlib.metadata import version as _metadata_version
    __version__ = _metadata_version("cypilot")
except Exception:
    __version__ = "unknown"
# @cpt-end:cpt-cypilot-flow-version-config-resolve-version:p2:inst-resolve-proxy-version
