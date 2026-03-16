"""
Cypilot Context - Global context for Cypilot tooling.

Loads and caches:
- Cypilot directory and project root
- ArtifactsMeta from artifacts.toml
- All templates for each kit
- Registered system names
- Workspace configuration (multi-repo federation)

Use CypilotContext.load() to initialize on CLI startup.

@cpt-algo:cpt-cypilot-algo-core-infra-config-management:p1
@cpt-flow:cpt-cypilot-flow-core-infra-cli-invocation:p1
"""

import sys
# @cpt-begin:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-datamodel
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple, Union

if TYPE_CHECKING:
    from .workspace import SourceEntry, WorkspaceConfig

from .artifacts_meta import Artifact, ArtifactsMeta, CodebaseEntry, Kit, load_artifacts_meta
from .constraints import KitConstraints, error, load_constraints_toml

@dataclass
class LoadedKit:
    """A kit with all its templates loaded."""
    kit: Kit
    templates: Dict[str, object]  # kind -> template-like (unused)
    constraints: Optional[KitConstraints] = None
    resource_bindings: Optional[Dict[str, str]] = None

@dataclass
class CypilotContext:
    """Global Cypilot context with loaded metadata and templates."""

    adapter_dir: Path
    project_root: Path
    meta: ArtifactsMeta
    kits: Dict[str, LoadedKit]  # kit_id -> LoadedKit
    registered_systems: Set[str]
    _errors: List[Dict[str, object]] = field(default_factory=list)
    # @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-datamodel

    @classmethod
    def load(cls, start_path: Optional[Path] = None) -> Optional["CypilotContext"]:
        """Load Cypilot context by discovering adapter directory.

        Args:
            start_path: Starting path to search for cypilot (default: cwd)

        Returns:
            CypilotContext or None if cypilot not found or load failed
        """
        from .files import find_cypilot_directory

        # @cpt-begin:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-find-and-load
        start = start_path or Path.cwd()
        adapter_dir = find_cypilot_directory(start)
        if not adapter_dir:
            return None
        # @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-find-and-load
        return cls.load_from_dir(adapter_dir)

    @classmethod
    def load_from_dir(cls, adapter_dir: Path) -> Optional["CypilotContext"]:
        """Load context from a known adapter directory (skip discovery)."""
        meta, err = load_artifacts_meta(adapter_dir)
        if err or meta is None:
            return None

        project_root = (adapter_dir / meta.project_root).resolve()

        # @cpt-begin:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-load-kits
        kits, errors = _load_all_kits(meta, adapter_dir, project_root)
        # @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-load-kits

        # @cpt-begin:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-expand-autodetect
        errors.extend(_expand_autodetect_errors(meta, adapter_dir, project_root, kits))
        # @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-expand-autodetect

        # @cpt-begin:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-collect-systems
        registered_systems = meta.get_all_system_prefixes()
        # @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-collect-systems

        # @cpt-begin:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-build-primary
        ctx = cls(
            adapter_dir=adapter_dir,
            project_root=project_root,
            meta=meta,
            kits=kits,
            registered_systems=registered_systems,
            _errors=errors,
        )
        # @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-build-primary
        return ctx

    # @cpt-begin:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-globals
    def get_known_id_kinds(self) -> Set[str]:
        kinds: Set[str] = set()
        for loaded_kit in self.kits.values():
            kc = getattr(loaded_kit, "constraints", None)
            if not kc or not getattr(kc, "by_kind", None):
                continue
            for kind_constraints in kc.by_kind.values():
                for c in (kind_constraints.defined_id or []):
                    if c and getattr(c, "kind", None):
                        kinds.add(str(c.kind).strip().lower())
        return kinds


# ---------------------------------------------------------------------------
# Helpers extracted from load_from_dir for cognitive-complexity budget
# ---------------------------------------------------------------------------


_ARTIFACTS_TOML = "artifacts.toml"


def _resolve_registry_path(adapter_dir: Path) -> Path:
    """Resolve the artifacts registry path for error reporting."""
    cfg_dir = adapter_dir / "config"
    if (cfg_dir / _ARTIFACTS_TOML).is_file():
        return (cfg_dir / _ARTIFACTS_TOML).resolve()
    return (adapter_dir / _ARTIFACTS_TOML).resolve()


def _load_single_kit(kit_id, kit, adapter_dir, project_root):
    """Load a single kit's templates, constraints, and resource bindings."""
    templates = {}

    kit_path_str = str(kit.path or "").strip().strip("/")
    kit_root = (adapter_dir / kit_path_str).resolve()
    if not kit_root.is_dir():
        kit_root = (project_root / kit_path_str).resolve()
    # @cpt-begin:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-load-resource-bindings
    rb = None
    _resolved_bindings = {}
    try:
        from .manifest import resolve_resource_bindings as _resolve_rb
        cfg_dir = adapter_dir / "config"
        if not cfg_dir.is_dir():
            cfg_dir = adapter_dir
        _resolved_bindings = _resolve_rb(cfg_dir, kit_id, adapter_dir)
        if _resolved_bindings:
            rb = {k: str(v) for k, v in _resolved_bindings.items()}
    except (OSError, ImportError, ValueError) as exc:
        sys.stderr.write(f"context: failed to load resource bindings for kit {kit_id}: {exc}\n")
    # @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-load-resource-bindings

    kit_constraints = None
    constraints_errs = []
    # @cpt-begin:cpt-cypilot-algo-core-infra-context-loading:p1:inst-constraints-from-binding
    _constraints_root = kit_root
    if _resolved_bindings and "constraints" in _resolved_bindings:
        _constraints_path = _resolved_bindings["constraints"]
        if _constraints_path.is_file():
            _constraints_root = _constraints_path.parent
    # @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-constraints-from-binding
    if _constraints_root.is_dir():
        kit_constraints, constraints_errs = load_constraints_toml(_constraints_root)
    elif kit_root.is_dir():
        kit_constraints, constraints_errs = load_constraints_toml(kit_root)

    errors = []
    if constraints_errs:
        constraints_path = (kit_root / "constraints.toml").resolve()
        errors.append(error(
            "constraints",
            "Invalid constraints.toml",
            path=constraints_path,
            line=1,
            errors=list(constraints_errs),
            kit=kit_id,
        ))

    loaded = LoadedKit(kit=kit, templates=templates, constraints=kit_constraints, resource_bindings=rb)
    return loaded, errors


# @cpt-begin:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-load-kits
def _load_all_kits(meta, adapter_dir, project_root):
    """Load all Cypilot-format kits from metadata."""
    kits = {}
    errors = []
    for kit_id, kit in meta.kits.items():
        if not kit.is_cypilot_format():
            continue
        loaded, kit_errors = _load_single_kit(kit_id, kit, adapter_dir, project_root)
        kits[kit_id] = loaded
        errors.extend(kit_errors)
    return kits, errors
# @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-load-kits


def _is_kind_registered_in_kits(kits, kit_id, kind):
    """Check if a kind is registered in a kit's templates or constraints."""
    lk = (kits or {}).get(str(kit_id))
    if not lk:
        return False
    k = str(kind)
    if k in (lk.templates or {}):
        return True
    kc = getattr(lk, "constraints", None)
    if kc and getattr(kc, "by_kind", None) and k in kc.by_kind:
        return True
    return False


def _get_id_kind_tokens_from_kits(kits, kit_id):
    """Get ID kind tokens from kit constraints."""
    lk = (kits or {}).get(str(kit_id))
    if not lk:
        return set()
    kc = getattr(lk, "constraints", None)
    if not kc or not getattr(kc, "by_kind", None):
        return set()
    tokens = set()
    for _kind, akc in kc.by_kind.items():
        for ic in (akc.defined_id or []):
            k = str(getattr(ic, "kind", "") or "").strip()
            if k:
                tokens.add(k)
    return tokens


# @cpt-begin:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-expand-autodetect
def _expand_autodetect_errors(meta, adapter_dir, project_root, kits):
    """Run autodetect expansion and return any errors."""
    errors = []
    try:
        autodetect_errs = meta.expand_autodetect(
            adapter_dir=adapter_dir,
            project_root=project_root,
            is_kind_registered=lambda kid, k: _is_kind_registered_in_kits(kits, kid, k),
            get_id_kind_tokens=lambda kid: _get_id_kind_tokens_from_kits(kits, kid),
        )
        if autodetect_errs:
            registry_path = _resolve_registry_path(adapter_dir)
            for msg in autodetect_errs:
                errors.append(error(
                    "registry",
                    "Autodetect validation error",
                    path=registry_path,
                    line=1,
                    details=str(msg),
                ))
    except (OSError, ValueError, KeyError) as e:
        registry_path = _resolve_registry_path(adapter_dir)
        errors.append(error(
            "registry",
            "Autodetect expansion failed",
            path=registry_path,
            line=1,
            error=str(e),
        ))
    return errors
# @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-expand-autodetect


# @cpt-algo:cpt-cypilot-feature-workspace:p1
@dataclass
class SourceContext:
    """Context for a single source in a workspace."""

    name: str
    path: Optional[Path] = None  # Absolute path to source root (None when unreachable)
    role: str = "full"  # "artifacts" | "codebase" | "kits" | "full"
    adapter_dir: Optional[Path] = None
    meta: Optional[ArtifactsMeta] = None
    kits: Dict[str, LoadedKit] = field(default_factory=dict)
    registered_systems: Set[str] = field(default_factory=set)
    reachable: bool = True
    error: Optional[str] = None
    # @cpt-algo:cpt-cypilot-algo-workspace-resolve-adapter-context:p1
    adapter_context: Optional["CypilotContext"] = None
    _adapter_resolved: bool = False  # Sentinel: True means we already attempted loading


@dataclass
class WorkspaceContext:
    """Multi-repo workspace context wrapping a primary CypilotContext and remote sources."""

    primary: CypilotContext
    sources: Dict[str, SourceContext] = field(default_factory=dict)
    workspace_file: Optional[Path] = None
    cross_repo: bool = True  # From traceability.cross_repo in workspace config
    resolve_remote_ids: bool = True  # From traceability.resolve_remote_ids

    @property
    def adapter_dir(self) -> Path:
        return self.primary.adapter_dir

    @property
    def project_root(self) -> Path:
        return self.primary.project_root

    @property
    def meta(self) -> ArtifactsMeta:
        return self.primary.meta

    @property
    def kits(self) -> Dict[str, LoadedKit]:
        return self.primary.kits

    @property
    def registered_systems(self) -> Set[str]:
        return self.primary.registered_systems

    def get_known_id_kinds(self) -> Set[str]:
        kinds = self.primary.get_known_id_kinds()
        for sc in self.sources.values():
            if not sc.reachable:
                continue
            if sc.adapter_context is not None:
                kinds.update(sc.adapter_context.get_known_id_kinds())
        return kinds

    def get_all_registered_systems(self) -> Set[str]:
        """Get registered systems from primary and all reachable sources.

        For remote sources, prefers the expanded meta (with autodetect
        resolved) when available so that child-system slugs are included.
        """
        systems = set(self.primary.registered_systems)
        for sc in self.sources.values():
            if not sc.reachable:
                continue
            if sc.adapter_context is not None:
                systems.update(sc.adapter_context.registered_systems)
            elif sc.registered_systems:
                systems.update(sc.registered_systems)
        return systems

    # @cpt-algo:cpt-cypilot-algo-workspace-resolve-artifact:p1
    def resolve_artifact_path(self, artifact: Union[Artifact, CodebaseEntry, Kit], fallback_root: Path) -> Optional[Path]:
        """Resolve an artifact's filesystem path, routing through workspace source if set.

        When ``artifact.source`` names a reachable workspace source, the path is
        resolved relative to that source's root directory.  When the source is
        explicitly set but missing or unreachable, returns ``None`` rather than
        silently falling back to a local path.  Falls back to *fallback_root*
        only when no source is specified.
        """
        # @cpt-begin:cpt-cypilot-algo-workspace-resolve-artifact:p1:inst-art-check-source
        src_name = getattr(artifact, "source", None)
        # @cpt-end:cpt-cypilot-algo-workspace-resolve-artifact:p1:inst-art-check-source
        # @cpt-begin:cpt-cypilot-algo-workspace-resolve-artifact:p1:inst-art-if-source
        if src_name:
            # @cpt-end:cpt-cypilot-algo-workspace-resolve-artifact:p1:inst-art-if-source
            # @cpt-begin:cpt-cypilot-algo-workspace-resolve-artifact:p1:inst-art-lookup-source
            sc = self.sources.get(src_name)
            # @cpt-end:cpt-cypilot-algo-workspace-resolve-artifact:p1:inst-art-lookup-source
            # @cpt-begin:cpt-cypilot-algo-workspace-resolve-artifact:p1:inst-art-if-reachable
            if sc is not None and sc.reachable and sc.path is not None:
                return (sc.path / artifact.path).resolve()
            # @cpt-end:cpt-cypilot-algo-workspace-resolve-artifact:p1:inst-art-if-reachable
            # @cpt-begin:cpt-cypilot-algo-workspace-resolve-artifact:p1:inst-art-return-none
            return None
            # @cpt-end:cpt-cypilot-algo-workspace-resolve-artifact:p1:inst-art-return-none
        # @cpt-begin:cpt-cypilot-algo-workspace-resolve-artifact:p1:inst-art-return-local
        return (fallback_root / artifact.path).resolve()
        # @cpt-end:cpt-cypilot-algo-workspace-resolve-artifact:p1:inst-art-return-local

    # @cpt-algo:cpt-cypilot-algo-workspace-collect-ids:p1
    def get_all_artifact_ids(self) -> Set[str]:
        """Collect artifact IDs from all workspace sources (for cross-repo resolution)."""
        ids: Set[str] = set()
        # @cpt-begin:cpt-cypilot-algo-workspace-collect-ids:p1:inst-ids-collect-primary
        for art, _sys in self.primary.meta.iter_all_artifacts():
            art_path = self.resolve_artifact_path(art, self.primary.project_root)
            if art_path is not None and art_path.exists():
                _scan_definition_ids(art_path, ids)
        # @cpt-end:cpt-cypilot-algo-workspace-collect-ids:p1:inst-ids-collect-primary
        # @cpt-begin:cpt-cypilot-algo-workspace-collect-ids:p1:inst-ids-if-cross-repo
        if self.cross_repo and self.resolve_remote_ids:
            # @cpt-end:cpt-cypilot-algo-workspace-collect-ids:p1:inst-ids-if-cross-repo
            # @cpt-begin:cpt-cypilot-algo-workspace-collect-ids:p1:inst-ids-foreach-source
            for sc in self.sources.values():
                # @cpt-end:cpt-cypilot-algo-workspace-collect-ids:p1:inst-ids-foreach-source
                # @cpt-begin:cpt-cypilot-algo-workspace-collect-ids:p1:inst-ids-scan-source-artifacts
                # @cpt-begin:cpt-cypilot-algo-workspace-collect-ids:p1:inst-ids-add-with-warning
                _collect_source_definition_ids(sc, ids)
                # @cpt-end:cpt-cypilot-algo-workspace-collect-ids:p1:inst-ids-add-with-warning
                # @cpt-end:cpt-cypilot-algo-workspace-collect-ids:p1:inst-ids-scan-source-artifacts
        # @cpt-begin:cpt-cypilot-algo-workspace-collect-ids:p1:inst-ids-return
        return ids
        # @cpt-end:cpt-cypilot-algo-workspace-collect-ids:p1:inst-ids-return

    # @cpt-algo:cpt-cypilot-algo-workspace-load-context:p1
    # @cpt-dod:cpt-cypilot-dod-workspace-cross-repo:p1
    # @cpt-dod:cpt-cypilot-dod-workspace-graceful-degradation:p1
    @classmethod
    def load(cls, primary_ctx: CypilotContext) -> Optional["WorkspaceContext"]:
        """Try to load workspace context from workspace config.

        Returns WorkspaceContext if workspace found, None otherwise.
        """
        from .workspace import find_workspace_config

        # @cpt-begin:cpt-cypilot-algo-workspace-load-context:p1:inst-ctx-find-config
        ws_cfg, ws_err = find_workspace_config(primary_ctx.project_root)
        # @cpt-end:cpt-cypilot-algo-workspace-load-context:p1:inst-ctx-find-config
        # @cpt-begin:cpt-cypilot-algo-workspace-load-context:p1:inst-ctx-if-error
        if ws_cfg is None:
            if ws_err:
                print(f"Warning: workspace config error: {ws_err}", file=sys.stderr)
            # @cpt-end:cpt-cypilot-algo-workspace-load-context:p1:inst-ctx-if-error
            # @cpt-begin:cpt-cypilot-algo-workspace-load-context:p1:inst-ctx-if-no-config
            return None
            # @cpt-end:cpt-cypilot-algo-workspace-load-context:p1:inst-ctx-if-no-config

        # @cpt-begin:cpt-cypilot-algo-workspace-load-context:p1:inst-ctx-foreach-source
        sources = {name: _load_source(name, src_entry, ws_cfg)
                   for name, src_entry in ws_cfg.sources.items()}
        # @cpt-end:cpt-cypilot-algo-workspace-load-context:p1:inst-ctx-foreach-source

        # @cpt-begin:cpt-cypilot-algo-workspace-load-context:p1:inst-ctx-build
        result = cls(
            primary=primary_ctx,
            sources=sources,
            workspace_file=ws_cfg.workspace_file,
            cross_repo=ws_cfg.traceability.cross_repo,
            resolve_remote_ids=ws_cfg.traceability.resolve_remote_ids,
        )
        # @cpt-end:cpt-cypilot-algo-workspace-load-context:p1:inst-ctx-build
        # @cpt-begin:cpt-cypilot-algo-workspace-load-context:p1:inst-ctx-return
        return result
        # @cpt-end:cpt-cypilot-algo-workspace-load-context:p1:inst-ctx-return


# @cpt-dod:cpt-cypilot-dod-workspace-cross-repo-editing:p1
def resolve_adapter_context(sc: "SourceContext") -> Optional["CypilotContext"]:
    """Load a source's own CypilotContext from its adapter directory.

    Returns cached result on repeat calls. Returns None for unreachable
    sources, sources without adapters, or when loading fails.
    """
    # @cpt-begin:cpt-cypilot-algo-workspace-resolve-adapter-context:p1:inst-adapter-if-unreachable
    if not sc.reachable:
        return None
    # @cpt-end:cpt-cypilot-algo-workspace-resolve-adapter-context:p1:inst-adapter-if-unreachable
    # @cpt-begin:cpt-cypilot-algo-workspace-resolve-adapter-context:p1:inst-adapter-cache
    if sc._adapter_resolved:
        return sc.adapter_context
    # @cpt-end:cpt-cypilot-algo-workspace-resolve-adapter-context:p1:inst-adapter-cache
    # @cpt-begin:cpt-cypilot-algo-workspace-resolve-adapter-context:p1:inst-adapter-if-no-dir
    if sc.adapter_dir is None:
        sc._adapter_resolved = True
        return None
    # @cpt-end:cpt-cypilot-algo-workspace-resolve-adapter-context:p1:inst-adapter-if-no-dir
    # @cpt-begin:cpt-cypilot-algo-workspace-resolve-adapter-context:p1:inst-adapter-compute-path
    # @cpt-begin:cpt-cypilot-algo-workspace-resolve-adapter-context:p1:inst-adapter-if-missing
    if not sc.adapter_dir.is_dir():
        print(f"Warning: adapter directory not found for source '{sc.name}': {sc.adapter_dir}", file=sys.stderr)
        sc._adapter_resolved = True
        return None
    # @cpt-end:cpt-cypilot-algo-workspace-resolve-adapter-context:p1:inst-adapter-if-missing
    # @cpt-end:cpt-cypilot-algo-workspace-resolve-adapter-context:p1:inst-adapter-compute-path
    # @cpt-begin:cpt-cypilot-algo-workspace-resolve-adapter-context:p1:inst-adapter-load-context
    # @cpt-begin:cpt-cypilot-algo-workspace-resolve-adapter-context:p1:inst-adapter-if-load-fail
    try:
        loaded = CypilotContext.load_from_dir(sc.adapter_dir)
    except (OSError, ValueError) as e:
        print(f"Warning: failed to load adapter context for source '{sc.name}': {e}", file=sys.stderr)
        sc._adapter_resolved = True
        return None
    if loaded is None:
        print(f"Warning: adapter context could not be loaded for source '{sc.name}'", file=sys.stderr)
        sc._adapter_resolved = True
        return None
    # @cpt-end:cpt-cypilot-algo-workspace-resolve-adapter-context:p1:inst-adapter-if-load-fail
    # @cpt-end:cpt-cypilot-algo-workspace-resolve-adapter-context:p1:inst-adapter-load-context
    # @cpt-begin:cpt-cypilot-algo-workspace-resolve-adapter-context:p1:inst-adapter-return
    sc.adapter_context = loaded
    sc._adapter_resolved = True
    return loaded
    # @cpt-end:cpt-cypilot-algo-workspace-resolve-adapter-context:p1:inst-adapter-return


# @cpt-begin:cpt-cypilot-algo-workspace-resolve-adapter-context:p1:inst-adapter-expand-meta
def get_expanded_meta(sc: "SourceContext") -> Optional[ArtifactsMeta]:
    """Return source meta with autodetect patterns expanded.

    During initial workspace loading, ``_load_reachable_source`` only calls
    ``load_artifacts_meta`` which parses the registry but skips kit loading
    and ``expand_autodetect()``.  This helper lazily triggers a full context
    load (via ``resolve_adapter_context``) on first access so that callers
    see the complete set of artifacts — including those discovered by
    autodetect glob rules.

    The result is cached on ``sc.adapter_context``, so repeated calls are free.
    """
    if sc.adapter_context is not None:
        return sc.adapter_context.meta
    if not sc._adapter_resolved and sc.adapter_dir is not None:
        ctx = resolve_adapter_context(sc)
        if ctx is not None:
            return ctx.meta
    return sc.meta
# @cpt-end:cpt-cypilot-algo-workspace-resolve-adapter-context:p1:inst-adapter-expand-meta


# @cpt-algo:cpt-cypilot-algo-workspace-determine-target:p1
def determine_target_source(
    target_path: Union[str, Path],
    ws_ctx: "WorkspaceContext",
) -> Tuple[Optional["SourceContext"], "CypilotContext"]:
    """Determine which workspace source owns a target file path.

    Uses longest-prefix matching against resolved source paths.
    Returns (source_context, adapter_or_primary_context).
    When no source matches, returns (None, primary_context).
    """
    # @cpt-begin:cpt-cypilot-algo-workspace-determine-target:p1:inst-target-resolve-abs
    abs_target = Path(target_path).resolve()
    # @cpt-end:cpt-cypilot-algo-workspace-determine-target:p1:inst-target-resolve-abs
    # @cpt-begin:cpt-cypilot-algo-workspace-determine-target:p1:inst-target-foreach-source
    # Sort by path length descending for longest-prefix match
    sorted_sources = sorted(
        ws_ctx.sources.values(),
        key=lambda sc: len(str(sc.path)) if sc.path is not None else 0,
        reverse=True,
    )
    for sc in sorted_sources:
        if not sc.reachable or sc.path is None:
            continue
        # @cpt-begin:cpt-cypilot-algo-workspace-determine-target:p1:inst-target-if-match
        try:
            abs_target.relative_to(sc.path.resolve())
        except ValueError:
            continue
        # @cpt-end:cpt-cypilot-algo-workspace-determine-target:p1:inst-target-if-match
        # @cpt-begin:cpt-cypilot-algo-workspace-determine-target:p1:inst-target-resolve-adapter
        adapter_ctx = resolve_adapter_context(sc)
        # @cpt-end:cpt-cypilot-algo-workspace-determine-target:p1:inst-target-resolve-adapter
        # @cpt-begin:cpt-cypilot-algo-workspace-determine-target:p1:inst-target-return-source
        if adapter_ctx is not None:
            return (sc, adapter_ctx)
        # @cpt-end:cpt-cypilot-algo-workspace-determine-target:p1:inst-target-return-source
        # @cpt-begin:cpt-cypilot-algo-workspace-determine-target:p1:inst-target-return-source-no-adapter
        return (sc, ws_ctx.primary)
        # @cpt-end:cpt-cypilot-algo-workspace-determine-target:p1:inst-target-return-source-no-adapter
    # @cpt-end:cpt-cypilot-algo-workspace-determine-target:p1:inst-target-foreach-source
    # @cpt-begin:cpt-cypilot-algo-workspace-determine-target:p1:inst-target-return-primary
    return (None, ws_ctx.primary)
    # @cpt-end:cpt-cypilot-algo-workspace-determine-target:p1:inst-target-return-primary


# ---------------------------------------------------------------------------
# Helpers extracted for cognitive-complexity budget
# ---------------------------------------------------------------------------


def _scan_definition_ids(artifact_path: Path, ids: Set[str]) -> None:
    """Scan an artifact file and add definition IDs to the set."""
    from .document import scan_cpt_ids

    try:
        for h in scan_cpt_ids(artifact_path):
            if h.get("type") == "definition" and h.get("id"):
                ids.add(str(h["id"]))
    except Exception as exc:
        print(f"Warning: failed to scan IDs from {artifact_path}: {exc}", file=sys.stderr)


def _collect_source_definition_ids(sc: "SourceContext", ids: Set[str]) -> None:
    """Collect definition IDs from a single reachable source's artifacts."""
    if not sc.reachable or sc.meta is None or sc.path is None:
        return
    if sc.role not in ("artifacts", "full"):
        return
    meta = get_expanded_meta(sc)
    if meta is None:
        return
    for art, _sys in meta.iter_all_artifacts():
        art_path = (sc.path / art.path).resolve()
        if art_path.exists():
            _scan_definition_ids(art_path, ids)


# @cpt-state:cpt-cypilot-state-workspace-source-reachability:p1
def _load_source(name: str, src_entry: "SourceEntry", ws_cfg: "WorkspaceConfig") -> "SourceContext":
    """Load a single workspace source, returning an unreachable stub or full context."""
    # @cpt-begin:cpt-cypilot-algo-workspace-load-context:p1:inst-ctx-resolve-path
    resolved_path = ws_cfg.resolve_source_path(name)
    # @cpt-end:cpt-cypilot-algo-workspace-load-context:p1:inst-ctx-resolve-path
    # @cpt-begin:cpt-cypilot-algo-workspace-load-context:p1:inst-ctx-if-unreachable
    # @cpt-begin:cpt-cypilot-state-workspace-source-reachability:p1:inst-source-becomes-unreachable
    if resolved_path is None or not resolved_path.is_dir():
        return SourceContext(
            name=name,
            path=resolved_path,
            role=src_entry.role,
            reachable=False,
            error=f"Source directory not found: {src_entry.path}",
        )
    # @cpt-end:cpt-cypilot-state-workspace-source-reachability:p1:inst-source-becomes-unreachable
    # @cpt-end:cpt-cypilot-algo-workspace-load-context:p1:inst-ctx-if-unreachable
    explicit_adapter = ws_cfg.resolve_source_adapter(name)
    return _load_reachable_source(name, src_entry, resolved_path, explicit_adapter)


# @cpt-begin:cpt-cypilot-algo-workspace-load-context:p1:inst-ctx-load-source-meta
# @cpt-begin:cpt-cypilot-state-workspace-source-reachability:p1:inst-source-becomes-reachable
def _load_reachable_source(
    name: str,
    src_entry: "SourceEntry",
    resolved_path: Path,
    explicit_adapter: Optional[Path] = None,
) -> "SourceContext":
    """Load adapter and metadata for a reachable workspace source."""
    # @cpt-end:cpt-cypilot-state-workspace-source-reachability:p1:inst-source-becomes-reachable
    # @cpt-end:cpt-cypilot-algo-workspace-load-context:p1:inst-ctx-load-source-meta
    from .files import find_cypilot_directory

    # Priority: use explicitly configured adapter path first;
    # when pinned adapter is invalid do NOT auto-discover a different one
    # (mirrors workspace_info._probe_source_adapter semantics).
    adapter_dir = None
    src_error = None
    if explicit_adapter is not None:
        if explicit_adapter.is_dir() and (explicit_adapter / "config").is_dir():
            adapter_dir = explicit_adapter
        else:
            # Pinned adapter invalid — report error, skip auto-discovery
            src_error = (
                f"Pinned adapter for source '{name}' is not a valid "
                f"cypilot directory: {explicit_adapter}"
            )
    else:
        # No explicit adapter — auto-discover from source root
        adapter_dir = find_cypilot_directory(resolved_path)

    meta = None
    reg_systems: Set[str] = set()

    if adapter_dir is not None:
        m, err = load_artifacts_meta(adapter_dir)
        if m and not err:
            meta = m
            reg_systems = m.get_all_system_prefixes()
        elif err:
            src_error = (
                f"Failed to load artifacts metadata for source '{name}'"
                f" (adapter: {adapter_dir}): {err}"
            )

    return SourceContext(
        name=name,
        path=resolved_path,
        role=src_entry.role,
        adapter_dir=adapter_dir,
        meta=meta,
        kits={},
        registered_systems=reg_systems,
        reachable=True,
        error=src_error,
    )


def _collect_remote_artifacts(
    ctx: "WorkspaceContext",
    artifacts: List[Tuple[Path, str]],
    path_to_source: Dict[str, str],
) -> None:
    """Append artifacts from reachable remote workspace sources.

    Skips paths already present in *artifacts* (e.g. primary artifacts that
    reference a remote source via the ``source`` field) to avoid duplicates.
    """
    seen = {str(p) for p, _ in artifacts}
    for sc in ctx.sources.values():
        if not sc.reachable or sc.meta is None or sc.path is None or sc.role not in ("artifacts", "full"):
            continue
        meta = get_expanded_meta(sc)
        if meta is None:
            continue
        for art, _sys in meta.iter_all_artifacts():
            art_path = (sc.path / art.path).resolve()
            path_key = str(art_path)
            if path_key not in seen and art_path.exists():
                artifacts.append((art_path, str(art.kind)))
                path_to_source[path_key] = sc.name
            seen.add(path_key)


# Global context instance (set by CLI on startup)
_global_context: Optional[Union[CypilotContext, WorkspaceContext]] = None
_workspace_upgrade_attempted: bool = False


def get_context() -> Optional[Union[CypilotContext, WorkspaceContext]]:
    """Get the global Cypilot context (may be CypilotContext or WorkspaceContext).

    On first call, lazily attempts to upgrade a CypilotContext to
    WorkspaceContext so that workspace loading (including potential network
    operations for git URL sources) is deferred until a command actually
    needs the context.
    """
    global _global_context, _workspace_upgrade_attempted
    if not _workspace_upgrade_attempted and isinstance(_global_context, CypilotContext):
        _workspace_upgrade_attempted = True
        ws_ctx = WorkspaceContext.load(_global_context)
        if ws_ctx is not None:
            _global_context = ws_ctx
    return _global_context


def set_context(ctx: Optional[Union[CypilotContext, WorkspaceContext]]) -> None:
    """Set the global Cypilot context."""
    global _global_context, _workspace_upgrade_attempted
    _global_context = ctx
    # If caller already provides a WorkspaceContext, skip lazy upgrade
    _workspace_upgrade_attempted = isinstance(ctx, WorkspaceContext) or ctx is None


def ensure_context(start_path: Optional[Path] = None) -> Optional[Union[CypilotContext, WorkspaceContext]]:
    """Ensure context is loaded, loading if necessary."""
    global _global_context, _workspace_upgrade_attempted
    if _global_context is None:
        base_ctx = CypilotContext.load(start_path)
        if base_ctx is not None:
            # @cpt-begin:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-workspace-upgrade
            ws_ctx = WorkspaceContext.load(base_ctx)
            _workspace_upgrade_attempted = True
            # @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-workspace-upgrade
            # @cpt-begin:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-return-workspace
            _global_context = ws_ctx if ws_ctx is not None else base_ctx
            # @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-return-workspace
        else:
            # @cpt-begin:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-return
            _global_context = None
            # @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-return
    return _global_context


def is_workspace() -> bool:
    """Check if the global context is a WorkspaceContext."""
    ctx = get_context()
    return isinstance(ctx, WorkspaceContext)


def get_primary_context() -> Optional[CypilotContext]:
    """Get the primary CypilotContext regardless of workspace mode."""
    ctx = get_context()
    if isinstance(ctx, WorkspaceContext):
        return ctx.primary
    return ctx


def collect_artifacts_to_scan(
    ctx: Union[CypilotContext, WorkspaceContext],
) -> Tuple[List[Tuple[Path, str]], Dict[str, str]]:
    """Collect all artifact paths for scanning, with workspace-aware resolution.

    Returns:
        (artifacts_to_scan, path_to_source) where artifacts_to_scan is a list of
        (artifact_path, artifact_kind) tuples and path_to_source maps absolute
        path strings to workspace source names.
    """
    artifacts: List[Tuple[Path, str]] = []
    path_to_source: Dict[str, str] = {}
    project_root = ctx.project_root

    # Primary artifacts
    is_ws = isinstance(ctx, WorkspaceContext)
    for artifact_meta, _system_node in ctx.meta.iter_all_artifacts():
        if is_ws:
            artifact_path = ctx.resolve_artifact_path(artifact_meta, project_root)
        else:
            artifact_path = (project_root / artifact_meta.path).resolve()
        if artifact_path is not None and artifact_path.exists():
            artifacts.append((artifact_path, str(artifact_meta.kind)))
            src_name = getattr(artifact_meta, "source", None)
            if is_ws and src_name:
                path_to_source[str(artifact_path)] = src_name

    # Remote source artifacts (workspace mode with cross-repo and remote ID resolution enabled)
    if is_ws and ctx.cross_repo and ctx.resolve_remote_ids:
        _collect_remote_artifacts(ctx, artifacts, path_to_source)

    return artifacts, path_to_source


def _resolve_single_artifact(
    artifact_arg: str,
) -> Tuple[
    Optional[CypilotContext],
    List[Tuple[Path, str]],
    Optional[str],
]:
    """Resolve a single artifact by path for where-* commands.

    Returns (ctx, artifacts_to_scan, error_message).
    """
    artifact_path = Path(artifact_arg).resolve()
    if not artifact_path.exists():
        return None, [], f"Artifact not found: {artifact_path}"

    ctx = CypilotContext.load(artifact_path.parent)
    if not ctx:
        return None, [], "Cypilot not initialized. Run 'cypilot init' first."

    try:
        rel_path = artifact_path.relative_to(ctx.project_root).as_posix()
    except ValueError:
        rel_path = None

    artifacts: List[Tuple[Path, str]] = []
    if rel_path:
        result = ctx.meta.get_artifact_by_path(rel_path)
        if result:
            artifact_meta, _system_node = result
            artifacts.append((artifact_path, str(artifact_meta.kind)))
    if not artifacts:
        return None, [], f"Artifact not in Cypilot registry: {artifact_arg}"
    return ctx, artifacts, None


def resolve_artifacts_for_command(
    artifact_arg: Optional[str],
) -> Tuple[
    Optional[Union[CypilotContext, WorkspaceContext]],
    List[Tuple[Path, str]],
    Dict[str, str],
    Optional[str],
]:
    """Resolve artifacts for where-defined / where-used commands.

    Returns:
        (ctx, artifacts_to_scan, path_to_source, error_message).
        If *error_message* is not None the caller should emit it and return 1.
    """
    if artifact_arg:
        ctx, artifacts_to_scan, err = _resolve_single_artifact(artifact_arg)
        if err:
            return None, [], {}, err
        return ctx, artifacts_to_scan, {}, None

    ctx = get_context()
    if not ctx:
        return None, [], {}, "Cypilot not initialized. Run 'cypilot init' first."

    artifacts_to_scan, path_to_source = collect_artifacts_to_scan(ctx)
    return ctx, artifacts_to_scan, path_to_source, None


def resolve_target_and_artifacts(
    args: object,
) -> Tuple[
    Optional[str],
    Optional[Union[CypilotContext, WorkspaceContext]],
    List[Tuple[Path, str]],
    Dict[str, str],
    Optional[str],
]:
    """Parse target ID and resolve artifacts for where-* commands.

    Expects *args* to have ``id_positional``, ``id``, and ``artifact``
    attributes (as produced by the shared argparse setup).

    Returns:
        (target_id, ctx, artifacts_to_scan, path_to_source, error_message).
        If *error_message* is not None the caller should emit it and return 1.
    """
    if args.id_positional and args.id:
        sys.stderr.write("WARNING: both positional ID and --id given; using positional\n")
    target_id = (args.id_positional or args.id or "").strip()
    if not target_id:
        return None, None, [], {}, "ID cannot be empty"

    ctx, artifacts_to_scan, path_to_source, err = resolve_artifacts_for_command(args.artifact)
    if err:
        return None, None, [], {}, err

    return target_id, ctx, artifacts_to_scan, path_to_source, None


__all__ = [
    "CypilotContext",
    "LoadedKit",
    "SourceContext",
    "WorkspaceContext",
    "collect_artifacts_to_scan",
    "determine_target_source",
    "get_context",
    "get_primary_context",
    "get_expanded_meta",
    "resolve_adapter_context",
    "resolve_artifacts_for_command",
    "resolve_target_and_artifacts",
    "set_context",
    "ensure_context",
    "is_workspace",
]
# @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-globals
