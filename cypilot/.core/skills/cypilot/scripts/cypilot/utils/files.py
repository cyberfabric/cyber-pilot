"""
Cypilot Validator - File System Operations

File I/O, project root discovery, cypilot detection, path resolution.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..constants import ARTIFACTS_REGISTRY_FILENAME
from . import toml_utils

_MARKER_START = "<!-- @cpt:root-agents -->"
_CORE_SUBDIR = ".core"
_GEN_SUBDIR = ".gen"


def core_subpath(cypilot_root: Path, *parts: str) -> Path:
    """Resolve a subpath within a cypilot root, checking .core/ first.

    New layout:  cypilot/.core/workflows/
    Old layout:  cypilot/workflows/  (source repo or legacy install)

    Returns the .core/ path if .core/ exists, otherwise the flat path.
    """
    core = cypilot_root / _CORE_SUBDIR
    if core.is_dir():
        return core.joinpath(*parts)
    return cypilot_root.joinpath(*parts)


def gen_subpath(cypilot_root: Path, *parts: str) -> Path:
    """Resolve a subpath within the .gen/ directory.

    Layout: cypilot/.gen/kits/sdlc/SKILL.md

    Returns the .gen/ path unconditionally (generated dir always uses .gen/).
    """
    return (cypilot_root / _GEN_SUBDIR).joinpath(*parts)


def cfg_get_str(cfg: object, *keys: str) -> Optional[str]:
    """Extract first non-empty string value from config dict for given keys."""
    if not isinstance(cfg, dict):
        return None
    for k in keys:
        v = cfg.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def find_project_root(start: Path) -> Optional[Path]:
    """
    Find project root by looking for AGENTS.md with @cpt:root-agents marker or .git directory.
    Searches up to 25 levels in directory hierarchy.
    """
    current = start.resolve()
    for _ in range(25):
        agents = current / "AGENTS.md"
        if agents.is_file():
            try:
                head = agents.read_text(encoding="utf-8")[:512]
            except OSError:
                head = ""
            if _MARKER_START in head:
                return current

        git_marker = current / ".git"
        if git_marker.exists():
            return current

        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _read_cypilot_var(project_root: Path) -> Optional[str]:
    """Read ``cypilot_path`` (or legacy ``cypilot``) variable from root AGENTS.md TOML block."""
    agents_file = project_root / "AGENTS.md"
    if not agents_file.is_file():
        return None
    try:
        content = agents_file.read_text(encoding="utf-8")
    except OSError:
        return None
    if _MARKER_START not in content:
        return None
    data = toml_utils.parse_toml_from_markdown(content)
    val = data.get("cypilot_path") or data.get("cypilot")
    return val.strip() if isinstance(val, str) and val.strip() else None


def load_project_config(project_root: Path) -> Optional[dict]:
    """Load project config from config/core.toml in cypilot dir (discovered via AGENTS.md)."""
    cypilot_rel = _read_cypilot_var(project_root)
    if cypilot_rel is None:
        return None
    core_toml = (project_root / cypilot_rel / "config" / "core.toml").resolve()
    # Fallback: legacy layout without config/ subdir
    if not core_toml.is_file():
        core_toml = (project_root / cypilot_rel / "core.toml").resolve()
    if not core_toml.is_file():
        return None
    try:
        return toml_utils.load(core_toml)
    except Exception:
        return None


def cypilot_root_from_project_config() -> Optional[Path]:
    """Get Cypilot core path from config core.toml [paths] section."""
    project_root = find_project_root(Path.cwd())
    if project_root is None:
        return None

    cfg = load_project_config(project_root)
    if cfg is None:
        return None

    paths = cfg.get("paths")
    core_rel = cfg_get_str(paths, "core") if isinstance(paths, dict) else None
    if core_rel is None:
        return None

    adapter_rel = _read_cypilot_var(project_root) or ""
    core = (project_root / adapter_rel / core_rel).resolve()
    if _is_cypilot_root(core):
        return core
    return None


def find_cypilot_directory(start: Path, cypilot_root: Optional[Path] = None) -> Optional[Path]:
    """
    Find cypilot directory starting from project root.

    Resolution order:
    1. Read ``cypilot`` variable from root AGENTS.md TOML block
    2. Recursively search for directories with AGENTS.md + rules/ (or legacy specs/)

    Args:
        start: Starting path for search
        cypilot_root: Known Cypilot core location (from agent context)
    """
    project_root = find_project_root(start)
    if project_root is None:
        return None

    # PRIORITY 1: Read cypilot variable from AGENTS.md TOML block
    adapter_rel = _read_cypilot_var(project_root)
    if adapter_rel is not None:
        adapter_dir = (project_root / adapter_rel).resolve()
        if adapter_dir.is_dir() and (adapter_dir / "config").is_dir():
            return adapter_dir
        return None

    # PRIORITY 2: Recursive search (only if no TOML variable found)
    skip_dirs = {
        ".git", "node_modules", "venv", "__pycache__", ".pytest_cache",
        "target", "build", "dist", ".idea", ".vscode", "vendor",
        "coverage", ".tox", ".mypy_cache", ".eggs"
    }
    
    def is_adapter_directory(path: Path) -> bool:
        """Check if directory looks like a cypilot config directory."""
        agents_file = path / "AGENTS.md"
        if not agents_file.exists():
            return False
        
        # Check AGENTS.md content
        try:
            content = agents_file.read_text(encoding="utf-8")
            
            # STRONGEST indicator: Extends Cypilot AGENTS.md
            # Example: **Extends**: `../.cypilot/AGENTS.md`
            if "**Extends**:" in content and "AGENTS.md" in content:
                # If agent provided cypilot_root, validate the Extends path
                if cypilot_root is not None:
                    # Extract Extends path from content
                    extends_match = re.search(r'\*\*Extends\*\*:\s*`([^`]+)`', content)
                    if extends_match:
                        extends_path = extends_match.group(1)
                        # Resolve relative to cypilot directory
                        resolved = (path / extends_path).resolve()
                        # Check if it points to cypilot_root
                        if resolved.parent == cypilot_root or (cypilot_root / "AGENTS.md") == resolved:
                            return True
                # Even without cypilot_root validation, Extends is strong signal
                return True
            
            # Look for cypilot-specific markers in content
            adapter_markers = [
                "# Cypilot Adapter:",
                ".cypilot-adapter",
                "cypilot-adapter",
                "## Cypilot Adapter",
                "This is an Cypilot adapter",
                "adapter for",
            ]
            content_lower = content.lower()
            for marker in adapter_markers:
                if marker.lower() in content_lower:
                    # Double-check with rules/ or specs/ directory if possible
                    if (path / "config" / "rules").is_dir() or (path / "rules").is_dir() or (path / "specs").is_dir():
                        return True
                    # Or check for rule/spec references in content
                    if "rule" in content_lower or "spec" in content_lower:
                        return True
        except Exception:
            pass  # Expected: search continues if file read fails

        # Fallback: verify it has rules/ or specs/ directory (strong structural indicator)
        if (path / "config" / "rules").is_dir() or (path / "rules").is_dir() or (path / "specs").is_dir():
            return True
        
        return False
    
    def search_recursive(root: Path, max_depth: int = 5, current_depth: int = 0) -> Optional[Path]:
        """Recursively search for cypilot directory."""
        if current_depth > max_depth:
            return None
        
        try:
            entries = list(root.iterdir())
        except (PermissionError, OSError):
            return None
        
        # First pass: check current level directories
        for entry in entries:
            if not entry.is_dir() or entry.name in skip_dirs:
                continue
            if is_adapter_directory(entry):
                return entry
        
        # Second pass: recurse into subdirectories (breadth-first preference)
        for entry in entries:
            if not entry.is_dir() or entry.name in skip_dirs:
                continue
            result = search_recursive(entry, max_depth, current_depth + 1)
            if result is not None:
                return result
        
        return None
    
    return search_recursive(project_root)


def load_cypilot_config(adapter_dir: Path) -> Dict[str, object]:
    """
    Load Cypilot configuration from AGENTS.md and rules/
    Returns dict with Cypilot metadata and available rules
    """
    config: Dict[str, object] = {
        "cypilot_dir": adapter_dir.as_posix(),
        "rules": [],
    }
    
    agents_file = adapter_dir / "AGENTS.md"
    if agents_file.exists():
        try:
            content = agents_file.read_text(encoding="utf-8")
            # Extract project name from heading
            for line in content.splitlines():
                if line.startswith("# Cypilot Adapter:"):
                    config["project_name"] = line.replace("# Cypilot Adapter:", "").strip()
                    break
        except Exception:
            pass  # Expected: project_name is optional metadata

    # List available rules (config/ layout, fallback to flat)
    rules_dir = adapter_dir / "config" / "rules"
    if not rules_dir.is_dir():
        rules_dir = adapter_dir / "rules"
    if rules_dir.is_dir():
        rule_files = []
        for rule_file in rules_dir.glob("*.md"):
            rule_files.append(rule_file.stem)
        config["rules"] = sorted(rule_files)
    
    return config


def load_artifacts_registry(adapter_dir: Path) -> Tuple[Optional[dict], Optional[str]]:
    path = adapter_dir / ARTIFACTS_REGISTRY_FILENAME
    # Fallback: try legacy artifacts.json if artifacts.toml not found
    if not path.is_file():
        legacy = adapter_dir / "artifacts.json"
        if legacy.is_file():
            path = legacy
        else:
            return None, f"Missing artifacts registry: {path}"
    try:
        if path.suffix == ".toml":
            cfg = toml_utils.load(path)
        else:
            raw = path.read_text(encoding="utf-8")
            cfg = json.loads(raw)
    except Exception as e:
        return None, f"Failed to read artifacts registry {path}: {e}"
    if not isinstance(cfg, dict):
        return None, f"Invalid artifacts registry (expected dict): {path}"
    if not isinstance(cfg.get("systems"), list) and not isinstance(cfg.get("artifacts"), list):
        return None, f"Invalid artifacts registry (missing 'systems' or 'artifacts' list): {path}"
    return cfg, None


def iter_registry_entries(registry: dict) -> List[dict]:
    items = registry.get("artifacts")
    if not isinstance(items, list):
        return []
    out: List[dict] = []
    for it in items:
        if isinstance(it, dict):
            out.append(it)
    return out


def _is_cypilot_root(path: Path) -> bool:
    """Check if *path* looks like a cypilot root (flat or .core/ layout)."""
    # New layout: .core/ subdir with requirements + workflows
    core = path / _CORE_SUBDIR
    if core.is_dir() and (core / "requirements").is_dir() and (core / "workflows").is_dir():
        return True
    # Old / source-repo layout: flat requirements + workflows + AGENTS.md
    if (
        (path / "AGENTS.md").exists()
        and (path / "requirements").is_dir()
        and (path / "workflows").is_dir()
    ):
        return True
    return False


def cypilot_root_from_this_file() -> Path:
    """
    Find Cypilot root by walking up directory tree looking for Cypilot markers.
    Cypilot can be located anywhere (as submodule, copied, etc.)
    """
    configured = cypilot_root_from_project_config()
    if configured is not None:
        return configured

    current = Path(__file__).resolve().parent.parent.parent.parent
    
    # Walk up directory tree looking for Cypilot root markers
    for _ in range(10):  # Limit search depth to avoid infinite loop
        if _is_cypilot_root(current):
            return current
        
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent
    
    # Fallback to old behavior if markers not found
    return Path(__file__).resolve().parents[6]


def load_text(path: Path) -> Tuple[str, Optional[str]]:
    """
    Load text from file, returning (content, error_message).
    Returns ("", error_message) on failure.
    """
    if not path.exists():
        return "", f"File not found: {path}"
    if not path.is_file():
        return "", f"Not a file: {path}"
    try:
        return path.read_text(encoding="utf-8"), None
    except Exception as e:
        return "", f"Failed to read {path}: {e}"
