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

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from .artifacts_meta import Artifact, ArtifactsMeta, CodebaseEntry, Kit, load_artifacts_meta
from .constraints import KitConstraints, error, load_constraints_toml


@dataclass
class LoadedKit:
    """A kit with all its templates loaded."""
    kit: Kit
    templates: Dict[str, object]  # kind -> template-like (unused)
    constraints: Optional[KitConstraints] = None


@dataclass
class CypilotContext:
    """Global Cypilot context with loaded metadata and templates."""

    adapter_dir: Path
    project_root: Path
    meta: ArtifactsMeta
    kits: Dict[str, LoadedKit]  # kit_id -> LoadedKit
    registered_systems: Set[str]
    _errors: List[Dict[str, object]] = field(default_factory=list)

    @classmethod
    def load(cls, start_path: Optional[Path] = None) -> Optional["CypilotContext"]:
        """Load Cypilot context from cypilot directory.

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

        meta, err = load_artifacts_meta(adapter_dir)
        if err or meta is None:
            return None

        project_root = (adapter_dir / meta.project_root).resolve()
        # @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-find-and-load

        # Load all templates for each Cypilot kit
        kits: Dict[str, LoadedKit] = {}
        errors: List[Dict[str, object]] = []

        # @cpt-begin:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-load-kits
        for kit_id, kit in meta.kits.items():
            if not kit.is_cypilot_format():
                continue

            templates: Dict[str, object] = {}

            kit_path_str = str(kit.path or "").strip().strip("/")
            kit_root = (adapter_dir / kit_path_str).resolve()
            if not kit_root.is_dir():
                kit_root = (project_root / kit_path_str).resolve()
            kit_constraints: Optional[KitConstraints] = None
            constraints_errs: List[str] = []
            if kit_root.is_dir():
                kit_constraints, constraints_errs = load_constraints_toml(kit_root)
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

            kits[kit_id] = LoadedKit(kit=kit, templates=templates, constraints=kit_constraints)
        # @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-load-kits

        # @cpt-begin:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-expand-autodetect
        # Expand autodetect (v1.1+): turns pattern rules into concrete artifacts/codebase.
        # This must happen after kits are loaded so we can validate kinds against templates/constraints.
        def _is_kind_registered(kit_id: str, kind: str) -> bool:
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

        def _get_id_kind_tokens(kit_id: str) -> Set[str]:
            lk = (kits or {}).get(str(kit_id))
            if not lk:
                return set()
            kc = getattr(lk, "constraints", None)
            if not kc or not getattr(kc, "by_kind", None):
                return set()
            tokens: Set[str] = set()
            for _kind, akc in kc.by_kind.items():
                for ic in (akc.defined_id or []):
                    k = str(getattr(ic, "kind", "") or "").strip()
                    if k:
                        tokens.add(k)
            return tokens

        try:
            autodetect_errs = meta.expand_autodetect(
                adapter_dir=adapter_dir,
                project_root=project_root,
                is_kind_registered=_is_kind_registered,
                get_id_kind_tokens=_get_id_kind_tokens,
            )
            if autodetect_errs:
                cfg_dir = adapter_dir / "config"
                registry_path = (cfg_dir / "artifacts.toml").resolve() if (cfg_dir / "artifacts.toml").is_file() else (adapter_dir / "artifacts.toml").resolve()
                for msg in autodetect_errs:
                    errors.append(error(
                        "registry",
                        "Autodetect validation error",
                        path=registry_path,
                        line=1,
                        details=str(msg),
                    ))
        except Exception as e:
            cfg_dir = adapter_dir / "config"
            registry_path = (cfg_dir / "artifacts.toml").resolve() if (cfg_dir / "artifacts.toml").is_file() else (adapter_dir / "artifacts.toml").resolve()
            errors.append(error(
                "registry",
                "Autodetect expansion failed",
                path=registry_path,
                line=1,
                error=str(e),
            ))

        # @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-expand-autodetect

        # @cpt-begin:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-collect-systems
        # Get all system prefixes (slug hierarchy prefixes used in cpt-<system>-... IDs)
        registered_systems = meta.get_all_system_prefixes()
        # @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-collect-systems

        # @cpt-begin:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-return

        ctx = cls(
            adapter_dir=adapter_dir,
            project_root=project_root,
            meta=meta,
            kits=kits,
            registered_systems=registered_systems,
            _errors=errors,
        )
        # @cpt-end:cpt-cypilot-algo-core-infra-context-loading:p1:inst-ctx-return
        return ctx

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


@dataclass
class SourceContext:
    """Context for a single source in a workspace."""

    name: str
    path: Path  # Absolute path to source root
    role: str  # "artifacts" | "codebase" | "kits" | "full"
    adapter_dir: Optional[Path] = None
    meta: Optional[ArtifactsMeta] = None
    kits: Dict[str, LoadedKit] = field(default_factory=dict)
    registered_systems: Set[str] = field(default_factory=set)
    reachable: bool = True
    error: Optional[str] = None


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
        return self.primary.get_known_id_kinds()

    def get_all_registered_systems(self) -> Set[str]:
        """Get registered systems from primary and all reachable sources."""
        systems = set(self.primary.registered_systems)
        for sc in self.sources.values():
            if sc.reachable and sc.registered_systems:
                systems.update(sc.registered_systems)
        return systems

    def resolve_artifact_path(self, artifact: Union[Artifact, CodebaseEntry, Kit], fallback_root: Path) -> Path:
        """Resolve an artifact's filesystem path, routing through workspace source if set.

        When ``artifact.source`` names a reachable workspace source, the path is
        resolved relative to that source's root directory.  Otherwise falls back
        to *fallback_root* (typically the primary project root).
        """
        src_name = getattr(artifact, "source", None)
        if src_name and src_name in self.sources:
            sc = self.sources[src_name]
            if sc.reachable:
                return (sc.path / artifact.path).resolve()
        return (fallback_root / artifact.path).resolve()

    def get_all_artifact_ids(self) -> Set[str]:
        """Collect artifact IDs from all workspace sources (for cross-repo resolution)."""
        ids: Set[str] = set()
        # Primary source
        for art, _sys in self.primary.meta.iter_all_artifacts():
            art_path = self.resolve_artifact_path(art, self.primary.project_root)
            if art_path.exists():
                _scan_definition_ids(art_path, ids)
        # Remote sources (only when cross-repo traceability is enabled)
        if self.cross_repo:
            for sc in self.sources.values():
                _collect_source_definition_ids(sc, ids)
        return ids

    @classmethod
    def load(cls, primary_ctx: CypilotContext) -> Optional["WorkspaceContext"]:
        """Try to load workspace context from workspace config.

        Returns WorkspaceContext if workspace found, None otherwise.
        """
        from .workspace import find_workspace_config

        ws_cfg, ws_err = find_workspace_config(primary_ctx.project_root)
        if ws_cfg is None:
            if ws_err:
                import sys
                print(f"Warning: workspace config error: {ws_err}", file=sys.stderr)
            return None

        sources = {name: _load_source(name, src_entry, ws_cfg)
                   for name, src_entry in ws_cfg.sources.items()}

        return cls(
            primary=primary_ctx,
            sources=sources,
            workspace_file=ws_cfg.workspace_file,
            cross_repo=ws_cfg.traceability.cross_repo,
            resolve_remote_ids=ws_cfg.traceability.resolve_remote_ids,
        )


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
    except Exception:
        pass


def _collect_source_definition_ids(sc: "SourceContext", ids: Set[str]) -> None:
    """Collect definition IDs from a single reachable source's artifacts."""
    if not sc.reachable or sc.meta is None:
        return
    for art, _sys in sc.meta.iter_all_artifacts():
        art_path = (sc.path / art.path).resolve()
        if art_path.exists():
            _scan_definition_ids(art_path, ids)


def _load_source(name: str, src_entry: object, ws_cfg: object) -> "SourceContext":
    """Load a single workspace source, returning an unreachable stub or full context."""
    resolved_path = ws_cfg.resolve_source_path(name)
    if resolved_path is None or not resolved_path.is_dir():
        return SourceContext(
            name=name,
            path=resolved_path or Path(src_entry.path),
            role=src_entry.role,
            reachable=False,
            error=f"Source directory not found: {src_entry.path}",
        )
    return _load_reachable_source(name, src_entry, resolved_path)


def _load_reachable_source(name: str, src_entry: object, resolved_path: Path) -> "SourceContext":
    """Load adapter and metadata for a reachable workspace source."""
    from .files import find_cypilot_directory

    adapter_dir = find_cypilot_directory(resolved_path)

    # Fallback: try explicit adapter path from workspace config
    if adapter_dir is None and src_entry.adapter is not None:
        adapter_path = (resolved_path / src_entry.adapter).resolve()
        if adapter_path.is_dir() and (adapter_path / "AGENTS.md").exists():
            adapter_dir = adapter_path

    meta = None
    reg_systems: Set[str] = set()
    src_error = None

    if adapter_dir is not None:
        m, err = load_artifacts_meta(adapter_dir)
        if m and not err:
            meta = m
            reg_systems = m.get_all_system_prefixes()
    elif src_entry.adapter is not None:
        src_error = f"Adapter not found for source '{name}' at {resolved_path}"

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
    """Append artifacts from reachable remote workspace sources."""
    for sc in ctx.sources.values():
        if not sc.reachable or sc.meta is None:
            continue
        for art, _sys in sc.meta.iter_all_artifacts():
            art_path = (sc.path / art.path).resolve()
            if art_path.exists():
                artifacts.append((art_path, str(art.kind)))
            path_to_source[str(art_path)] = sc.name


# Global context instance (set by CLI on startup)
_global_context: Optional[Union[CypilotContext, WorkspaceContext]] = None


def get_context() -> Optional[Union[CypilotContext, WorkspaceContext]]:
    """Get the global Cypilot context (may be CypilotContext or WorkspaceContext)."""
    return _global_context


def set_context(ctx: Optional[Union[CypilotContext, WorkspaceContext]]) -> None:
    """Set the global Cypilot context."""
    global _global_context
    _global_context = ctx


def ensure_context(start_path: Optional[Path] = None) -> Optional[Union[CypilotContext, WorkspaceContext]]:
    """Ensure context is loaded, loading if necessary."""
    global _global_context
    if _global_context is None:
        base_ctx = CypilotContext.load(start_path)
        if base_ctx is not None:
            ws_ctx = WorkspaceContext.load(base_ctx)
            _global_context = ws_ctx if ws_ctx is not None else base_ctx
        else:
            _global_context = None
    return _global_context


def is_workspace() -> bool:
    """Check if the global context is a WorkspaceContext."""
    return isinstance(_global_context, WorkspaceContext)


def get_primary_context() -> Optional[CypilotContext]:
    """Get the primary CypilotContext regardless of workspace mode."""
    if isinstance(_global_context, WorkspaceContext):
        return _global_context.primary
    return _global_context


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
        if artifact_path.exists():
            artifacts.append((artifact_path, str(artifact_meta.kind)))

    # Remote source artifacts (workspace mode with cross-repo enabled)
    if is_ws and ctx.cross_repo:
        _collect_remote_artifacts(ctx, artifacts, path_to_source)

    return artifacts, path_to_source


__all__ = [
    "CypilotContext",
    "LoadedKit",
    "SourceContext",
    "WorkspaceContext",
    "collect_artifacts_to_scan",
    "get_context",
    "get_primary_context",
    "set_context",
    "ensure_context",
    "is_workspace",
]
