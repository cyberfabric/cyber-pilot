"""
Walk-Up Layer Discovery

Discovers ``manifest.toml`` files at each layer boundary (kit, master repo, repo)
by walking up the filesystem from the repo root.

@cpt-algo:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1
@cpt-dod:cpt-cypilot-dod-project-extensibility-walk-up-discovery:p1
"""

# @cpt-begin:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:inst-imports
from __future__ import annotations

import logging
import tomllib
from pathlib import Path
from typing import List, Optional

from .manifest import ManifestLayer, ManifestLayerState, parse_manifest_v2, _rewrite_component_paths
# @cpt-end:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:inst-imports

logger = logging.getLogger(__name__)

_MANIFEST_TOML = "manifest.toml"

# ---------------------------------------------------------------------------
# Boundary Detection
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:inst-is-boundary
def _is_master_repo_boundary(dir_path: Path) -> bool:
    """Return True if *dir_path* is a master repo boundary.

    Detection criteria (either):
    - ``CLAUDE.md`` file AND ``skills/`` subdirectory present at the same level.
    - ``.git/`` subdirectory present.
    """
    git_marker = dir_path / ".git"
    if git_marker.is_dir() or git_marker.is_file():
        return True
    if (dir_path / "CLAUDE.md").is_file() and (dir_path / "skills").is_dir():
        return True
    return False
# @cpt-end:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:inst-is-boundary


# ---------------------------------------------------------------------------
# Walk-Up Detection
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:inst-detect-master
def _detect_master_repo(start_dir: Path) -> Optional[Path]:
    """Walk up from *start_dir* parent, returning the first master repo root found.

    Walk starts from ``start_dir.parent`` (not *start_dir* itself) and stops
    as soon as a boundary marker is detected.

    Returns the boundary directory ``Path`` if found, else ``None``.
    """
    current = start_dir.parent
    # Walk up until we hit the filesystem root
    while True:
        if _is_master_repo_boundary(current):
            return current
        parent = current.parent
        if parent == current:
            # Reached filesystem root without finding a boundary
            return None
        current = parent
# @cpt-end:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:inst-detect-master


# ---------------------------------------------------------------------------
# Layer Loaders
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:inst-load-repo-layer
def _load_repo_layer(cypilot_root: Path) -> Optional[ManifestLayer]:
    """Load the repo manifest from ``{cypilot_root}/config/manifest.toml``.

    Returns ``None`` if the file does not exist (silently omitted).
    Returns a ``ManifestLayer`` with ``PARSE_ERROR`` state if parsing fails.
    """
    manifest_path = cypilot_root / "config" / _MANIFEST_TOML
    if not manifest_path.is_file():
        return None

    try:
        manifest = parse_manifest_v2(manifest_path)
        return ManifestLayer(
            scope="repo",
            path=manifest_path,
            manifest=manifest,
            state=ManifestLayerState.LOADED,
        )
    except (ValueError, OSError):
        return ManifestLayer(
            scope="repo",
            path=manifest_path,
            manifest=None,
            state=ManifestLayerState.PARSE_ERROR,
        )
# @cpt-end:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:inst-load-repo-layer


# @cpt-begin:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:inst-load-kit-layers
def _load_kit_layers(cypilot_root: Path) -> List[ManifestLayer]:
    """Load kit manifest layers from kit registrations in ``core.toml``.

    Reads ``{cypilot_root}/config/core.toml``, iterates over ``[kits]``
    entries, and loads ``manifest.toml`` from each kit path.

    Kits without a ``manifest.toml`` are silently omitted.
    Kits with a parse error return a ``PARSE_ERROR`` state layer.
    """
    core_toml = cypilot_root / "config" / "core.toml"
    if not core_toml.is_file():
        return []

    try:
        with open(core_toml, "rb") as f:
            data = tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError):
        return []

    kits_section = data.get("kits")
    if not isinstance(kits_section, dict):
        return []

    layers: List[ManifestLayer] = []
    for _slug, kit_entry in kits_section.items():
        if not isinstance(kit_entry, dict):
            continue
        kit_path_raw = kit_entry.get("path", "")
        if not kit_path_raw:
            continue

        kit_path = Path(str(kit_path_raw))
        # Resolve relative paths against cypilot_root
        if not kit_path.is_absolute():
            kit_path = (cypilot_root / kit_path).resolve()
        else:
            kit_path = kit_path.resolve()

        # Post-resolve containment check (only for relative paths that could
        # escape via '..' or symlinks; absolute paths are explicitly authored)
        if not Path(str(kit_path_raw)).is_absolute() and not kit_path.is_relative_to(cypilot_root.resolve()):
            logger.warning(
                "Kit path '%s' resolves outside cypilot root, skipping",
                kit_path_raw,
            )
            continue

        manifest_path = kit_path / _MANIFEST_TOML
        if not manifest_path.is_file():
            # Silently omit kits without a manifest
            continue

        try:
            manifest = parse_manifest_v2(manifest_path)
            layers.append(ManifestLayer(
                scope="kit",
                path=manifest_path,
                manifest=manifest,
                state=ManifestLayerState.LOADED,
            ))
        except (ValueError, OSError):
            layers.append(ManifestLayer(
                scope="kit",
                path=manifest_path,
                manifest=None,
                state=ManifestLayerState.PARSE_ERROR,
            ))

    return layers
# @cpt-end:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:inst-load-kit-layers


# ---------------------------------------------------------------------------
# Master Repo Layer Loader
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:inst-load-master-layer
def _load_master_layer(master_root: Path) -> Optional[ManifestLayer]:
    """Load the master repo manifest from ``{master_root}/manifest.toml``.

    Returns ``None`` if the file does not exist (silently omitted).
    Returns a ``ManifestLayer`` with ``PARSE_ERROR`` state if parsing fails.
    """
    manifest_path = master_root / _MANIFEST_TOML
    if not manifest_path.is_file():
        return None

    try:
        from dataclasses import replace as dc_replace
        manifest = parse_manifest_v2(manifest_path)
        manifest_dir = manifest_path.parent
        trusted_root = manifest_dir.resolve()
        rewritten_agents = [_rewrite_component_paths(c, manifest_dir, trusted_root) for c in manifest.agents]
        rewritten_skills = [_rewrite_component_paths(c, manifest_dir, trusted_root) for c in manifest.skills]
        manifest = dc_replace(manifest, agents=rewritten_agents, skills=rewritten_skills)
        return ManifestLayer(
            scope="master",
            path=manifest_path,
            manifest=manifest,
            state=ManifestLayerState.LOADED,
        )
    except (ValueError, OSError):
        return ManifestLayer(
            scope="master",
            path=manifest_path,
            manifest=None,
            state=ManifestLayerState.PARSE_ERROR,
        )
# @cpt-end:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:inst-load-master-layer


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:inst-discover-layers
def discover_layers(repo_root: Path, cypilot_root: Path) -> List[ManifestLayer]:
    """Discover manifest layers in resolution order.

    Resolution order (outermost to innermost):
    1. Kit layers — from ``core.toml`` kit registrations
    2. Master Repo layer — discovered via walk-up (if found)
    3. Repo layer — from ``{cypilot_root}/config/manifest.toml``

    Missing layers (no ``manifest.toml``) are silently omitted.
    Parse errors result in ``ManifestLayerState.PARSE_ERROR`` layers.

    Args:
        repo_root: Root of the current repo.
        cypilot_root: Cypilot adapter directory (e.g. ``{repo}/.bootstrap``).

    Returns:
        List of ``ManifestLayer`` in resolution order.
    """
    # Step 1: Load kit layers from core.toml
    # @cpt-begin:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:step-1-kit-layers
    layers: List[ManifestLayer] = []
    kit_layers = _load_kit_layers(cypilot_root)
    layers.extend(kit_layers)
    # @cpt-end:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:step-1-kit-layers

    # Step 3-6: Load master manifest — check project root first, then walk up
    # @cpt-begin:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:step-3-6-walkup
    # A project may be its own master repo (manifest.toml at project root with
    # scope = "master").  Check repo_root itself before walking up to a parent.
    root_manifest = repo_root / _MANIFEST_TOML
    if root_manifest.is_file():
        master_layer = _load_master_layer(repo_root)
        if master_layer is not None:
            layers.append(master_layer)
    else:
        master_root = _detect_master_repo(repo_root)
        if master_root is not None:
            master_layer = _load_master_layer(master_root)
            if master_layer is not None:
                layers.append(master_layer)
    # @cpt-end:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:step-3-6-walkup

    # Step 2: Load repo layer from {cypilot_root}/config/manifest.toml
    # @cpt-begin:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:step-2-repo-layer
    repo_layer = _load_repo_layer(cypilot_root)
    if repo_layer is not None:
        layers.append(repo_layer)
    # @cpt-end:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:step-2-repo-layer

    return layers
# @cpt-end:cpt-cypilot-algo-project-extensibility-walk-up-discovery:p1:inst-discover-layers
