"""
Skill Target Resolution

Walks directory tree to find project-installed skill, falls back to cache.

@cpt-algo:cpt-cypilot-algo-core-infra-resolve-skill:p1
"""

import re
import sys
import tomllib
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

MARKER_START = "<!-- @cpt:root-agents -->"

_TOML_FENCE_RE = re.compile(r"```toml\s*\n(.*?)```", re.DOTALL)

# Legacy: extract {cypilot_path} or {cypilot} from markdown table (pre-TOML format)
_CYPILOT_VAR_RE = re.compile(
    r"\|\s*`\{cypilot(?:_path)?\}`\s*\|\s*`([^`]+)`\s*\|"
)

# Legacy: extract install dir from old-format navigation rule
_OLD_NAV_RE = re.compile(
    r"ALWAYS open and follow `@/([^`/]+)/config/AGENTS\.md`"
)


def find_project_root(start_dir: Optional[Path] = None) -> Optional[Path]:
    """Find the project root by walking up looking for AGENTS.md with @cpt:root-agents marker."""
    current = (start_dir or Path.cwd()).resolve()
    for parent in [current, *current.parents]:
        agents_file = parent / "AGENTS.md"
        if agents_file.is_file():
            try:
                head = agents_file.read_text(encoding="utf-8")[:512]
            except OSError:
                continue
            if MARKER_START in head:
                return parent
    return None


def _parse_toml_from_markdown(text: str) -> Dict[str, Any]:
    """Extract and merge all ``toml`` fenced code blocks from markdown."""
    merged: Dict[str, Any] = {}
    for m in _TOML_FENCE_RE.finditer(text):
        try:
            data = tomllib.loads(m.group(1))
            merged.update(data)
        except Exception:
            continue
    return merged


def read_cypilot_path(project_root: Path) -> Optional[str]:
    """
    Read the ``cypilot_path`` (or legacy ``cypilot``) variable from root AGENTS.md.

    Tries TOML fenced block first (new format), then falls back to legacy
    markdown table extraction.

    Returns the install directory path (relative to project root) or None.
    """
    agents_file = project_root / "AGENTS.md"
    if not agents_file.is_file():
        return None
    try:
        content = agents_file.read_text(encoding="utf-8")
    except OSError:
        return None
    if MARKER_START not in content:
        return None

    # New format: ```toml block with cypilot_path = "..." (or legacy cypilot = "...")
    toml_data = _parse_toml_from_markdown(content)
    value = toml_data.get("cypilot_path") or toml_data.get("cypilot")
    if isinstance(value, str) and value.strip():
        return value.strip()

    # Legacy: markdown table | `{cypilot_path}` or `{cypilot}` | `@/...` |
    m = _CYPILOT_VAR_RE.search(content)
    if m is not None:
        legacy_value = m.group(1).strip()
        if legacy_value.startswith("@/"):
            legacy_value = legacy_value[2:]
        return legacy_value

    return None


def find_install_dir(project_root: Path) -> Optional[str]:
    """
    Determine the Cypilot install directory relative to project root.

    Resolution order:
    1. Read {cypilot_path} variable from AGENTS.md managed block (new format)
    2. Parse old-format navigation rule from AGENTS.md
    3. Scan for common install directory names
    """
    from_var = read_cypilot_path(project_root)
    if from_var is not None:
        return from_var

    agents_file = project_root / "AGENTS.md"
    if agents_file.is_file():
        try:
            content = agents_file.read_text(encoding="utf-8")
        except OSError:
            content = ""
        m = _OLD_NAV_RE.search(content)
        if m is not None:
            return m.group(1)

    for candidate in (".cypilot", "cypilot", ".cpt"):
        if (project_root / candidate / "skills").is_dir():
            return candidate

    return None


def get_cache_dir() -> Path:
    """Return the global Cypilot cache directory: ~/.cypilot/cache/"""
    return Path.home() / ".cypilot" / "cache"


def get_version_file() -> Path:
    """Return the version marker file path."""
    return get_cache_dir() / ".version"


def find_project_skill(start_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Find project-installed skill by reading {cypilot_path} variable from root AGENTS.md.

    Walks up from start_dir to find AGENTS.md with @cpt:root-agents marker,
    reads the {cypilot_path} variable to get the install directory, then looks
    for the skill entry point there.

    Returns path to the skill entry point (cypilot.py) or None.
    """
    # @cpt-begin:cpt-cypilot-algo-core-infra-resolve-skill:p1:inst-walk-parents
    project_root = find_project_root(start_dir)
    if project_root is None:
        return None

    install_dir = read_cypilot_path(project_root)
    if install_dir is None:
        return None
    # @cpt-end:cpt-cypilot-algo-core-infra-resolve-skill:p1:inst-walk-parents

    # @cpt-begin:cpt-cypilot-algo-core-infra-resolve-skill:p1:inst-if-marker
    # Check .core/ layout first, then flat layout
    core_skill_dir = project_root / install_dir / ".core" / "skills" / "cypilot" / "scripts"
    skill_dir = core_skill_dir if core_skill_dir.is_dir() else project_root / install_dir / "skills" / "cypilot" / "scripts"
    entry_point = skill_dir / "cypilot.py"
    if entry_point.is_file():
        # @cpt-begin:cpt-cypilot-algo-core-infra-resolve-skill:p1:inst-return-project-path
        return entry_point
        # @cpt-end:cpt-cypilot-algo-core-infra-resolve-skill:p1:inst-return-project-path

    # Also check for the package directly
    package_dir = skill_dir / "cypilot"
    if package_dir.is_dir() and (package_dir / "__init__.py").is_file():
        return skill_dir / "cypilot.py"
    # @cpt-end:cpt-cypilot-algo-core-infra-resolve-skill:p1:inst-if-marker

    return None


def find_cached_skill() -> Optional[Path]:
    """
    Check for cached skill at ~/.cypilot/cache/.

    Returns path to the skill entry point or None.
    """
    # @cpt-begin:cpt-cypilot-algo-core-infra-resolve-skill:p1:inst-check-global-cache
    cache_dir = get_cache_dir()
    entry_point = cache_dir / "skills" / "cypilot" / "scripts" / "cypilot.py"
    if entry_point.is_file():
        # @cpt-begin:cpt-cypilot-algo-core-infra-resolve-skill:p1:inst-return-cache-path
        return entry_point
        # @cpt-end:cpt-cypilot-algo-core-infra-resolve-skill:p1:inst-return-cache-path
    # @cpt-end:cpt-cypilot-algo-core-infra-resolve-skill:p1:inst-check-global-cache
    return None


def resolve_skill(start_dir: Optional[Path] = None) -> Tuple[Optional[Path], str]:
    """
    Resolve skill target: project-installed first, then cache.

    Returns (path_to_skill_entry, source) where source is "project" or "cache".
    Returns (None, "none") if no skill found.
    """
    # @cpt-begin:cpt-cypilot-algo-core-infra-resolve-skill:p1:inst-if-marker
    project_skill = find_project_skill(start_dir)
    if project_skill is not None:
        return project_skill, "project"
    # @cpt-end:cpt-cypilot-algo-core-infra-resolve-skill:p1:inst-if-marker

    # @cpt-begin:cpt-cypilot-algo-core-infra-resolve-skill:p1:inst-if-cache-exists
    cached_skill = find_cached_skill()
    if cached_skill is not None:
        return cached_skill, "cache"
    # @cpt-end:cpt-cypilot-algo-core-infra-resolve-skill:p1:inst-if-cache-exists

    # @cpt-begin:cpt-cypilot-algo-core-infra-resolve-skill:p1:inst-return-not-found
    return None, "none"
    # @cpt-end:cpt-cypilot-algo-core-infra-resolve-skill:p1:inst-return-not-found


def get_cached_version() -> Optional[str]:
    """Read the cached skill version from .version marker file."""
    version_file = get_version_file()
    if version_file.is_file():
        return version_file.read_text(encoding="utf-8").strip()
    return None


def get_project_version(skill_path: Path) -> Optional[str]:
    """Read version from project-installed skill's __init__.py."""
    init_file = skill_path.parent / "cypilot" / "__init__.py"
    if not init_file.is_file():
        return None
    try:
        content = init_file.read_text(encoding="utf-8")
        for line in content.splitlines():
            if line.startswith("__version__"):
                # Extract version string
                return line.split("=", 1)[1].strip().strip("\"'")
    except (OSError, ValueError):
        pass
    return None
