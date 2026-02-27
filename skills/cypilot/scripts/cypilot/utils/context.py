"""
Cypilot Context - Global context for Cypilot tooling.

Loads and caches:
- Adapter directory and project root
- ArtifactsMeta from artifacts.json
- All templates for each kit
- Registered system names
- Workspace configuration (multi-repo federation)

Use CypilotContext.load() to initialize on CLI startup.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from .artifacts_meta import ArtifactsMeta, Kit, load_artifacts_meta
from .constraints import KitConstraints, error, load_constraints_json


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
        """Load Cypilot context from adapter directory.

        Args:
            start_path: Starting path to search for adapter (default: cwd)

        Returns:
            CypilotContext or None if adapter not found or load failed
        """
        from .files import find_adapter_directory

        start = start_path or Path.cwd()
        adapter_dir = find_adapter_directory(start)
        if not adapter_dir:
            return None

        meta, err = load_artifacts_meta(adapter_dir)
        if err or meta is None:
            return None

        project_root = (adapter_dir / meta.project_root).resolve()

        # Load all templates for each Cypilot kit
        kits: Dict[str, LoadedKit] = {}
        errors: List[Dict[str, object]] = []

        for kit_id, kit in meta.kits.items():
            if not kit.is_cypilot_format():
                continue

            templates: Dict[str, object] = {}

            kit_root = (project_root / str(kit.path or "").strip().strip("/")).resolve()
            kit_constraints: Optional[KitConstraints] = None
            constraints_errs: List[str] = []
            if kit_root.is_dir():
                kit_constraints, constraints_errs = load_constraints_json(kit_root)
            if constraints_errs:
                constraints_path = (kit_root / "constraints.json").resolve()
                errors.append(error(
                    "constraints",
                    "Invalid constraints.json",
                    path=constraints_path,
                    line=1,
                    errors=list(constraints_errs),
                    kit=kit_id,
                ))

            kits[kit_id] = LoadedKit(kit=kit, templates=templates, constraints=kit_constraints)

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
                registry_path = (adapter_dir / "artifacts.json").resolve()
                for msg in autodetect_errs:
                    errors.append(error(
                        "registry",
                        "Autodetect validation error",
                        path=registry_path,
                        line=1,
                        details=str(msg),
                    ))
        except Exception as e:
            registry_path = (adapter_dir / "artifacts.json").resolve()
            errors.append(error(
                "registry",
                "Autodetect expansion failed",
                path=registry_path,
                line=1,
                error=str(e),
            ))

        # Get all system prefixes (slug hierarchy prefixes used in cpt-<system>-... IDs)
        registered_systems = meta.get_all_system_prefixes()

        ctx = cls(
            adapter_dir=adapter_dir,
            project_root=project_root,
            meta=meta,
            kits=kits,
            registered_systems=registered_systems,
            _errors=errors,
        )
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

    def get_all_artifact_ids(self) -> Set[str]:
        """Collect artifact IDs from all workspace sources (for cross-repo resolution)."""
        from .document import scan_cpt_ids

        ids: Set[str] = set()
        # Primary source
        for art, _sys in self.primary.meta.iter_all_artifacts():
            art_path = (self.primary.project_root / art.path).resolve()
            if art_path.exists():
                try:
                    for h in scan_cpt_ids(art_path):
                        if h.get("type") == "definition" and h.get("id"):
                            ids.add(str(h["id"]))
                except Exception:
                    continue
        # Remote sources
        for sc in self.sources.values():
            if not sc.reachable or sc.meta is None:
                continue
            for art, _sys in sc.meta.iter_all_artifacts():
                art_path = (sc.path / art.path).resolve()
                if art_path.exists():
                    try:
                        for h in scan_cpt_ids(art_path):
                            if h.get("type") == "definition" and h.get("id"):
                                ids.add(str(h["id"]))
                    except Exception:
                        continue
        return ids

    @classmethod
    def load(cls, primary_ctx: CypilotContext) -> Optional["WorkspaceContext"]:
        """Try to load workspace context from workspace config.

        Returns WorkspaceContext if workspace found, None otherwise.
        """
        from .workspace import find_workspace_config

        ws_cfg, ws_err = find_workspace_config(primary_ctx.project_root)
        if ws_cfg is None:
            return None

        sources: Dict[str, SourceContext] = {}
        for name, src_entry in ws_cfg.sources.items():
            resolved_path = ws_cfg.resolve_source_path(name)
            if resolved_path is None or not resolved_path.is_dir():
                sources[name] = SourceContext(
                    name=name,
                    path=resolved_path or Path(src_entry.path),
                    role=src_entry.role,
                    reachable=False,
                    error=f"Source directory not found: {src_entry.path}",
                )
                continue

            # Try to load adapter and meta for this source
            adapter_dir = None
            meta = None
            source_kits: Dict[str, LoadedKit] = {}
            reg_systems: Set[str] = set()
            src_error = None

            if src_entry.adapter is not None:
                adapter_path = (resolved_path / src_entry.adapter).resolve()
                if adapter_path.is_dir() and (adapter_path / "AGENTS.md").exists():
                    adapter_dir = adapter_path
                    m, err = load_artifacts_meta(adapter_dir)
                    if m and not err:
                        meta = m
                        # Resolve project_root relative to adapter_dir for the source
                        source_project_root = (adapter_dir / m.project_root).resolve()
                        reg_systems = m.get_all_system_prefixes()
                else:
                    src_error = f"Adapter not found at {adapter_path}"

            sources[name] = SourceContext(
                name=name,
                path=resolved_path,
                role=src_entry.role,
                adapter_dir=adapter_dir,
                meta=meta,
                kits=source_kits,
                registered_systems=reg_systems,
                reachable=True,
                error=src_error,
            )

        return cls(
            primary=primary_ctx,
            sources=sources,
            workspace_file=ws_cfg.workspace_file,
        )


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


__all__ = [
    "CypilotContext",
    "LoadedKit",
    "SourceContext",
    "WorkspaceContext",
    "get_context",
    "get_primary_context",
    "set_context",
    "ensure_context",
    "is_workspace",
]
