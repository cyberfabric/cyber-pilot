"""
Cypilot Validator - Python Package

Entry point for the Cypilot validation CLI tool.

@cpt-flow:cpt-cypilot-flow-core-infra-cli-invocation:p1
"""

import subprocess
from pathlib import Path
from typing import List, Optional

# Import from modular components
from .constants import *
from .utils import *

# Import CLI entry point
def main(argv: Optional[List[str]] = None) -> int:
    from .cli import main as _main
    return _main(argv)


# Last hardcoded version before migration to git-based versioning (ADR-0015).
# Used as legacy fallback when git tags and meta.toml are both unavailable.
# Remove after one release cycle.
_LEGACY_VERSION = "v3.0.12-beta"


# @cpt-begin:cpt-cypilot-algo-version-config-resolve-skill-version:p2:inst-git-describe
def _resolve_skill_version() -> str:
    """Resolve skill engine version using the ADR-0015 fallback chain.

    1. git describe --tags --match "skill-v*" (strip skill- prefix)
    2. ~/.cypilot/cache/meta.toml version field
    3. _LEGACY_VERSION (pre-migration cached copies)
    4. "unknown"
    """
    # Step 1: git describe (dev checkout with tags)
    skill_root = Path(__file__).resolve().parent
    git_dir = skill_root
    # Walk up to find .git (skill is nested under project root)
    for _ in range(10):
        if (git_dir / ".git").exists():
            break
        parent = git_dir.parent
        if parent == git_dir:
            break
        git_dir = parent
    else:
        git_dir = None

    if git_dir and (git_dir / ".git").exists():
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--match", "skill-v*"],
                cwd=str(git_dir),
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                tag = result.stdout.strip()
                # Strip "skill-" prefix
                if tag.startswith("skill-"):
                    return tag[len("skill-"):]
                return tag
        except (subprocess.SubprocessError, OSError):
            pass
# @cpt-end:cpt-cypilot-algo-version-config-resolve-skill-version:p2:inst-git-describe

    # @cpt-begin:cpt-cypilot-algo-version-config-resolve-skill-version:p2:inst-read-meta
    # Step 2: meta.toml fallback (cached copies)
    meta_path = Path.home() / ".cypilot" / "cache" / "meta.toml"
    if meta_path.is_file():
        try:
            import tomllib
            with open(meta_path, "rb") as f:
                meta = tomllib.load(f)
            version = meta.get("version")
            if isinstance(version, str) and version.strip():
                return version.strip()
        except Exception:
            pass
    # @cpt-end:cpt-cypilot-algo-version-config-resolve-skill-version:p2:inst-read-meta

    # @cpt-begin:cpt-cypilot-algo-version-config-resolve-skill-version:p2:inst-read-legacy-version
    # Step 3: legacy fallback (pre-migration cached copies)
    if _LEGACY_VERSION:
        return _LEGACY_VERSION
    # @cpt-end:cpt-cypilot-algo-version-config-resolve-skill-version:p2:inst-read-legacy-version

    # @cpt-begin:cpt-cypilot-algo-version-config-resolve-skill-version:p2:inst-version-unknown
    return "unknown"
    # @cpt-end:cpt-cypilot-algo-version-config-resolve-skill-version:p2:inst-version-unknown


__version__ = _resolve_skill_version()

__all__ = [
    # Main entry point
    "main",
]
