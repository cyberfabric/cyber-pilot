"""
Spider Context - Global context for Spider tooling.

Loads and caches:
- Adapter directory and project root
- ArtifactsMeta from artifacts.json
- All templates for each weaver
- Registered system names

Use SpiderContext.load() to initialize on CLI startup.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from .artifacts_meta import ArtifactsMeta, Weaver, load_artifacts_meta
from .template import Template


@dataclass
class LoadedWeaver:
    """A weaver with all its templates loaded."""
    weaver: Weaver
    templates: Dict[str, Template]  # kind -> Template


@dataclass
class SpiderContext:
    """Global Spider context with loaded metadata and templates."""

    adapter_dir: Path
    project_root: Path
    meta: ArtifactsMeta
    weavers: Dict[str, LoadedWeaver]  # weaver_id -> LoadedWeaver
    registered_systems: Set[str]
    _errors: List[str] = field(default_factory=list)

    @classmethod
    def load(cls, start_path: Optional[Path] = None) -> Optional["SpiderContext"]:
        """Load Spider context from adapter directory.

        Args:
            start_path: Starting path to search for adapter (default: cwd)

        Returns:
            SpiderContext or None if adapter not found or load failed
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

        # Load all templates for each Spider weaver
        weavers: Dict[str, LoadedWeaver] = {}
        errors: List[str] = []

        for weaver_id, weaver in meta.weavers.items():
            if not weaver.is_spider_format():
                continue

            templates: Dict[str, Template] = {}

            weaver_path = str(weaver.path or "").strip().strip("/")
            candidates: List[Path] = []
            if weaver_path:
                # Primary: whatever is in artifacts.json
                candidates.append(project_root / weaver_path / "artifacts")

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
                        templates[tmpl.kind] = tmpl
                    else:
                        errors.extend([str(e) for e in tmpl_errs])

                # Stop at the first candidate that yields any templates.
                if templates:
                    break

            weavers[weaver_id] = LoadedWeaver(weaver=weaver, templates=templates)

        # Get all system names
        registered_systems = meta.get_all_system_names()

        ctx = cls(
            adapter_dir=adapter_dir,
            project_root=project_root,
            meta=meta,
            weavers=weavers,
            registered_systems=registered_systems,
            _errors=errors,
        )
        return ctx

    def get_template(self, weaver_id: str, kind: str) -> Optional[Template]:
        """Get a loaded template by weaver and kind."""
        loaded_weaver = self.weavers.get(weaver_id)
        if not loaded_weaver:
            return None
        return loaded_weaver.templates.get(kind)

    def get_template_for_kind(self, kind: str) -> Optional[Template]:
        """Get template for a kind from any weaver."""
        for loaded_weaver in self.weavers.values():
            if kind in loaded_weaver.templates:
                return loaded_weaver.templates[kind]
        return None

    def get_known_id_kinds(self) -> Set[str]:
        """Get all known ID kinds from template markers.

        Scans all templates for spd:id:<kind> markers and returns the set of kinds.
        This is useful for parsing composite Spider IDs.
        """
        kinds: Set[str] = set()
        for loaded_weaver in self.weavers.values():
            for tmpl in loaded_weaver.templates.values():
                for block in tmpl.blocks or []:
                    if block.type == "id":
                        # block.name is the kind (e.g., "fr", "actor", "flow", "algo")
                        kinds.add(block.name.lower())
        return kinds


# Global context instance (set by CLI on startup)
_global_context: Optional[SpiderContext] = None


def get_context() -> Optional[SpiderContext]:
    """Get the global Spider context."""
    return _global_context


def set_context(ctx: Optional[SpiderContext]) -> None:
    """Set the global Spider context."""
    global _global_context
    _global_context = ctx


def ensure_context(start_path: Optional[Path] = None) -> Optional[SpiderContext]:
    """Ensure context is loaded, loading if necessary."""
    global _global_context
    if _global_context is None:
        _global_context = SpiderContext.load(start_path)
    return _global_context


__all__ = [
    "SpiderContext",
    "LoadedWeaver",
    "get_context",
    "set_context",
    "ensure_context",
]
