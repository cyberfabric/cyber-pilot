"""
Kit Manifest Parser and Validator

Parses and validates ``manifest.toml`` — the declarative kit installation
manifest.  When present in a kit package root, the manifest governs
installation and update: only declared resources are installed.

@cpt-algo:cpt-cypilot-algo-kit-manifest-install:p1
"""

# @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-datamodel
from __future__ import annotations

import string
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ManifestResource:
    """A single resource declared in ``manifest.toml``."""

    id: str
    source: str
    default_path: str
    type: str  # "file" or "directory"
    description: str = ""
    user_modifiable: bool = True


@dataclass(frozen=True)
class Manifest:
    """Parsed representation of a kit ``manifest.toml``."""

    version: str
    root: str
    user_modifiable: bool
    resources: List[ManifestResource] = field(default_factory=list)
# @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-datamodel


# ---------------------------------------------------------------------------
# Schema validation helper
# ---------------------------------------------------------------------------

def _validate_against_schema(data: Dict[str, Any]) -> List[str]:
    """Validate *data* against ``kit-manifest.schema.json`` (best-effort).

    Uses a lightweight structural check — no third-party jsonschema library.
    Returns a list of error messages (empty if valid).
    """
    errors: List[str] = []

    # --- [manifest] section ---
    manifest = data.get("manifest")
    if not isinstance(manifest, dict):
        errors.append("Missing or invalid [manifest] section")
        return errors

    version = manifest.get("version")
    if not isinstance(version, str) or not version.strip():
        errors.append("[manifest].version is required and must be a non-empty string")

    root = manifest.get("root")
    if root is not None and (not isinstance(root, str) or not root.strip()):
        errors.append("[manifest].root must be a non-empty string when present")

    um = manifest.get("user_modifiable")
    if um is not None and not isinstance(um, bool):
        errors.append("[manifest].user_modifiable must be a boolean when present")

    # --- [[resources]] ---
    resources = data.get("resources")
    if not isinstance(resources, list) or len(resources) == 0:
        errors.append("[[resources]] must be a non-empty array")
        return errors

    _VALID_TYPES = {"file", "directory"}
    _ID_CHARS = set(string.ascii_lowercase + string.digits + "_")

    for idx, res in enumerate(resources):
        prefix = f"[[resources]][{idx}]"
        if not isinstance(res, dict):
            errors.append(f"{prefix}: must be a table")
            continue

        # id
        rid = res.get("id")
        if not isinstance(rid, str) or not rid.strip():
            errors.append(f"{prefix}.id is required and must be a non-empty string")
        elif not rid[0].islower() or not all(c in _ID_CHARS for c in rid):
            errors.append(
                f"{prefix}.id '{rid}' must match ^[a-z][a-z0-9_]*$ "
                "(lowercase letter start, then lowercase alphanumeric or underscore)"
            )

        # source
        source = res.get("source")
        if not isinstance(source, str) or not source.strip():
            errors.append(f"{prefix}.source is required and must be a non-empty string")

        # default_path
        dp = res.get("default_path")
        if not isinstance(dp, str) or not dp.strip():
            errors.append(f"{prefix}.default_path is required and must be a non-empty string")

        # type
        rtype = res.get("type")
        if not isinstance(rtype, str) or rtype not in _VALID_TYPES:
            errors.append(f"{prefix}.type must be one of {sorted(_VALID_TYPES)}, got {rtype!r}")

        # description (optional)
        desc = res.get("description")
        if desc is not None and not isinstance(desc, str):
            errors.append(f"{prefix}.description must be a string when present")

        # user_modifiable (optional)
        rum = res.get("user_modifiable")
        if rum is not None and not isinstance(rum, bool):
            errors.append(f"{prefix}.user_modifiable must be a boolean when present")

    return errors


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-read
def load_manifest(kit_source: Path) -> Optional[Manifest]:
    """Read and parse ``manifest.toml`` from *kit_source*.

    Returns ``None`` if the file does not exist.
    Raises ``ValueError`` if the file exists but is invalid.
    """
    manifest_path = kit_source / "manifest.toml"
    if not manifest_path.is_file():
        return None

    try:
        with open(manifest_path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"Invalid manifest.toml: {exc}") from exc

    # Schema-level structural validation
    schema_errors = _validate_against_schema(data)
    if schema_errors:
        raise ValueError(
            f"Invalid manifest.toml: {'; '.join(schema_errors)}"
        )

    meta = data["manifest"]
    raw_resources = data.get("resources", [])

    resources: List[ManifestResource] = []
    for r in raw_resources:
        resources.append(ManifestResource(
            id=str(r["id"]).strip(),
            source=str(r["source"]).strip(),
            default_path=str(r["default_path"]).strip(),
            type=str(r["type"]).strip(),
            description=str(r.get("description", "")).strip(),
            user_modifiable=bool(r.get("user_modifiable", True)),
        ))

    return Manifest(
        version=str(meta["version"]).strip(),
        root=str(meta.get("root", "{cypilot_path}/config/kits/{slug}")).strip(),
        user_modifiable=bool(meta.get("user_modifiable", True)),
        resources=resources,
    )
# @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-read


# @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-validate
def validate_manifest(manifest: Manifest, kit_source: Path) -> List[str]:
    """Validate a parsed *manifest* against the actual *kit_source* directory.

    Checks:
    - All resource ``id`` values are unique.
    - All ``source`` paths exist in the kit package.
    - ``default_path`` values are valid relative paths (no ``..`` escapes).
    - ``type`` matches the actual source (file vs directory).

    Returns a list of error messages (empty if valid).
    """
    errors: List[str] = []

    # 1. Unique ids
    seen_ids: Dict[str, int] = {}
    for idx, res in enumerate(manifest.resources):
        if res.id in seen_ids:
            errors.append(
                f"Duplicate resource id '{res.id}' "
                f"(first at index {seen_ids[res.id]}, again at {idx})"
            )
        else:
            seen_ids[res.id] = idx

    for res in manifest.resources:
        source_path = kit_source / res.source

        # 2. Source path exists
        if not source_path.exists():
            errors.append(
                f"Resource '{res.id}': source path '{res.source}' "
                f"does not exist in kit package"
            )
            continue

        # 3. Type matches actual source
        if res.type == "file" and not source_path.is_file():
            errors.append(
                f"Resource '{res.id}': type is 'file' but "
                f"source '{res.source}' is a directory"
            )
        elif res.type == "directory" and not source_path.is_dir():
            errors.append(
                f"Resource '{res.id}': type is 'directory' but "
                f"source '{res.source}' is a file"
            )

    # 4. default_path — valid relative paths
    for res in manifest.resources:
        dp = res.default_path
        if dp.startswith("/") or dp.startswith("\\"):
            errors.append(
                f"Resource '{res.id}': default_path '{dp}' must be a relative path"
            )
        # Check for path traversal
        try:
            resolved = Path(dp).as_posix()
            if ".." in resolved.split("/"):
                errors.append(
                    f"Resource '{res.id}': default_path '{dp}' "
                    f"must not contain '..' path components"
                )
        except (ValueError, OSError):
            errors.append(
                f"Resource '{res.id}': default_path '{dp}' is not a valid path"
            )

    return errors
# @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-validate


# ---------------------------------------------------------------------------
# Resource Resolution API
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-kit-manifest-resolve:p1:inst-resolve-read-bindings
def resolve_resource_bindings(
    config_dir: Path, slug: str, cypilot_dir: Path,
) -> Dict[str, Path]:
    """Resolve resource bindings for kit *slug* to absolute paths.

    Reads ``[kits.{slug}.resources]`` from ``core.toml`` in *config_dir*,
    then resolves each relative path against *cypilot_dir* (the adapter
    directory).  Paths may contain ``..`` components for resources placed
    outside the adapter tree.

    Returns a dict mapping resource identifiers to absolute ``Path`` objects.
    Returns an empty dict if no resources section exists.

    @cpt-algo:cpt-cypilot-algo-kit-manifest-resolve:p1
    """
    core_toml = config_dir / "core.toml"
    if not core_toml.is_file():
        return {}

    try:
        with open(core_toml, "rb") as f:
            data = tomllib.load(f)
    except Exception as exc:
        import sys
        sys.stderr.write(f"resolve_resource_bindings: failed to parse {core_toml}: {exc}\n")
        return {}

    kits = data.get("kits")
    if not isinstance(kits, dict):
        return {}
    kit_entry = kits.get(slug)
    if not isinstance(kit_entry, dict):
        return {}
    resources = kit_entry.get("resources")
    if not isinstance(resources, dict):
        return {}
    # @cpt-end:cpt-cypilot-algo-kit-manifest-resolve:p1:inst-resolve-read-bindings

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-resolve:p1:inst-resolve-to-absolute
    result: Dict[str, Path] = {}
    for identifier, binding in resources.items():
        if isinstance(binding, dict):
            rel_path = str(binding.get("path", "")).strip()
        elif isinstance(binding, str):
            rel_path = binding.strip()
        else:
            continue
        if not rel_path:
            continue
        result[identifier] = (cypilot_dir / rel_path).resolve()
    # @cpt-end:cpt-cypilot-algo-kit-manifest-resolve:p1:inst-resolve-to-absolute

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-resolve:p1:inst-resolve-return
    return result
    # @cpt-end:cpt-cypilot-algo-kit-manifest-resolve:p1:inst-resolve-return


# ---------------------------------------------------------------------------
# Source Path Mapping API
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ResourceInfo:
    """Metadata about a manifest resource for target path resolution."""

    type: str  # "file" or "directory"
    source_base: str  # source path in manifest (e.g., "artifacts/ADR")


# @cpt-algo:cpt-cypilot-algo-kit-manifest-source-mapping:p1
def build_source_to_resource_mapping(
    kit_source: Path,
) -> tuple[Dict[str, str], Dict[str, ResourceInfo]]:
    """Build mapping from source file paths to resource identifiers.

    For manifest-driven kit updates, this mapping allows determining which
    resource binding applies to each source file.

    Args:
        kit_source: Kit source directory (containing manifest.toml).

    Returns:
        Tuple of:
        - source_to_resource_id: Dict mapping each source file's relative path
          to its resource identifier. For directory resources, all files within
          the directory are mapped to the same resource id.
        - resource_info: Dict mapping resource id to ResourceInfo (type and
          source_base path for computing relative paths within directories).

    Returns (empty_dict, empty_dict) if no manifest.toml exists.

    @cpt-begin:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-load-manifest
    """
    manifest = load_manifest(kit_source)
    if manifest is None:
        return {}, {}
    # @cpt-end:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-load-manifest

    source_to_resource_id: Dict[str, str] = {}
    resource_info: Dict[str, ResourceInfo] = {}

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-record-resource-info
    # @cpt-begin:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-map-file-resources
    # @cpt-begin:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-expand-directories
    for res in manifest.resources:
        resource_info[res.id] = ResourceInfo(
            type=res.type,
            source_base=res.source,
        )
        if res.type == "file":
            source_to_resource_id[res.source] = res.id
        elif res.type == "directory":
            source_dir = kit_source / res.source
            if source_dir.is_dir():
                for fpath in source_dir.rglob("*"):
                    if fpath.is_file():
                        rel_path = fpath.relative_to(kit_source).as_posix()
                        source_to_resource_id[rel_path] = res.id
    # @cpt-end:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-expand-directories
    # @cpt-end:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-map-file-resources
    # @cpt-end:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-record-resource-info

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-return-mapping
    return source_to_resource_id, resource_info
    # @cpt-end:cpt-cypilot-algo-kit-manifest-source-mapping:p1:inst-return-mapping
