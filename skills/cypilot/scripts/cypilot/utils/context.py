"""
Cypilot Context - Global context for Cypilot tooling.

Loads and caches:
- Adapter directory and project root
- ArtifactsMeta from artifacts.toml
- All templates for each kit
- Registered system names

Use CypilotContext.load() to initialize on CLI startup.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

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
        from .files import find_cypilot_directory

        start = start_path or Path.cwd()
        adapter_dir = find_cypilot_directory(start)
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


# Global context instance (set by CLI on startup)
_global_context: Optional[CypilotContext] = None


def get_context() -> Optional[CypilotContext]:
    """Get the global Cypilot context."""
    return _global_context


def set_context(ctx: Optional[CypilotContext]) -> None:
    """Set the global Cypilot context."""
    global _global_context
    _global_context = ctx


def ensure_context(start_path: Optional[Path] = None) -> Optional[CypilotContext]:
    """Ensure context is loaded, loading if necessary."""
    global _global_context
    if _global_context is None:
        _global_context = CypilotContext.load(start_path)
    return _global_context


__all__ = [
    "CypilotContext",
    "LoadedKit",
    "get_context",
    "set_context",
    "ensure_context",
]
