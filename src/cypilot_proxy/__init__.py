"""
Cypilot Global CLI Proxy

Thin proxy package that resolves skill targets (project-installed or cached)
and forwards commands. Installable via pipx.

@cpt-dod:cpt-cypilot-dod-core-infra-global-package:p1
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("cypilot")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"
