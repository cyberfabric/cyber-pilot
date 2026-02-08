"""
Cypilot Context - Global context for Cypilot tooling.

Loads and caches:
- Adapter directory and project root
- ArtifactsMeta from artifacts.json
- All templates for each kit
- Registered system names

Use CypilotContext.load() to initialize on CLI startup.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from .artifacts_meta import ArtifactsMeta, Kit, load_artifacts_meta
from .constraints import KitConstraints, load_constraints_json
from .template import Template


@dataclass
class LoadedKit:
    """A kit with all its templates loaded."""
    kit: Kit
    templates: Dict[str, Template]  # kind -> Template
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

            templates: Dict[str, Template] = {}

            kit_root = (project_root / str(kit.path or "").strip().strip("/")).resolve()
            kit_constraints: Optional[KitConstraints] = None
            constraints_errs: List[str] = []
            if kit_root.is_dir():
                kit_constraints, constraints_errs = load_constraints_json(kit_root)
            if constraints_errs:
                constraints_path = (kit_root / "constraints.json").resolve()
                errors.append(Template.error(
                    "constraints",
                    "Invalid constraints.json",
                    path=constraints_path,
                    line=1,
                    errors=list(constraints_errs),
                    kit=kit_id,
                ))

            kit_path = str(kit.path or "").strip().strip("/")
            candidates: List[Path] = []
            if kit_path:
                # Primary: whatever is in artifacts.json
                candidates.append(project_root / kit_path / "artifacts")

            # De-dupe while preserving order
            seen: Set[str] = set()
            for artifacts_dir in candidates:
                key = artifacts_dir.resolve().as_posix() if artifacts_dir.exists() else artifacts_dir.as_posix()
                if key in seen:
                    continue
                seen.add(key)

                if not artifacts_dir.is_dir():
                    continue

                # Scan for template directories (each dir is a KIND)
                for kind_dir in artifacts_dir.iterdir():
                    if not kind_dir.is_dir():
                        continue
                    template_file = kind_dir / "template.md"
                    if not template_file.is_file():
                        continue
                    tmpl, tmpl_errs = Template.from_path(template_file)
                    if tmpl:
                        if kit_constraints and tmpl.kind in kit_constraints.by_kind:
                            from .template import apply_kind_constraints
                            ce = apply_kind_constraints(tmpl, kit_constraints.by_kind[tmpl.kind])
                            if ce:
                                errors.extend(ce)
                        templates[tmpl.kind] = tmpl
                    else:
                        errors.extend(tmpl_errs)

                # Stop at the first candidate that yields any templates.
                if templates:
                    break

            kits[kit_id] = LoadedKit(kit=kit, templates=templates, constraints=kit_constraints)

        # Get all system names
        registered_systems = meta.get_all_system_names()

        ctx = cls(
            adapter_dir=adapter_dir,
            project_root=project_root,
            meta=meta,
            kits=kits,
            registered_systems=registered_systems,
            _errors=errors,
        )
        return ctx

    def get_template(self, kit_id: str, kind: str) -> Optional[Template]:
        """Get a loaded template by kit and kind."""
        loaded_kit = self.kits.get(kit_id)
        if not loaded_kit:
            return None
        return loaded_kit.templates.get(kind)

    def get_template_for_kind(self, kind: str) -> Optional[Template]:
        """Get template for a kind from any kit."""
        for loaded_kit in self.kits.values():
            if kind in loaded_kit.templates:
                return loaded_kit.templates[kind]
        return None

    def get_known_id_kinds(self) -> Set[str]:
        """Get all known ID kinds from template markers.

        Scans all templates for cpt:id:<kind> markers and returns the set of kinds.
        This is useful for parsing composite Cypilot IDs.
        """
        kinds: Set[str] = set()
        for loaded_kit in self.kits.values():
            for tmpl in loaded_kit.templates.values():
                for block in tmpl.blocks or []:
                    if block.type == "id":
                        # block.name is the kind (e.g., "fr", "actor", "flow", "algo")
                        kinds.add(block.name.lower())
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
