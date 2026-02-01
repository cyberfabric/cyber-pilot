"""
FDD Context - Global context for FDD tooling.

Loads and caches:
- Adapter directory and project root
- ArtifactsMeta from artifacts.json
- All templates for each rule
- Registered system names

Use FddContext.load() to initialize on CLI startup.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from .artifacts_meta import ArtifactsMeta, Rule, load_artifacts_meta
from .template import Template


@dataclass
class LoadedRule:
    """A rule with all its templates loaded."""
    rule: Rule
    templates: Dict[str, Template]  # kind -> Template


@dataclass
class FddContext:
    """Global FDD context with loaded metadata and templates."""

    adapter_dir: Path
    project_root: Path
    meta: ArtifactsMeta
    rules: Dict[str, LoadedRule]  # rule_id -> LoadedRule
    registered_systems: Set[str]
    _errors: List[str] = field(default_factory=list)

    @classmethod
    def load(cls, start_path: Optional[Path] = None) -> Optional["FddContext"]:
        """Load FDD context from adapter directory.

        Args:
            start_path: Starting path to search for adapter (default: cwd)

        Returns:
            FddContext or None if adapter not found or load failed
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

        # Load all templates for each FDD rule
        rules: Dict[str, LoadedRule] = {}
        errors: List[str] = []

        for rule_id, rule in meta.rules.items():
            if not rule.is_fdd_format():
                continue

            templates: Dict[str, Template] = {}
            rule_path = project_root / rule.path / "artifacts"

            if rule_path.is_dir():
                # Scan for template directories (each dir is a KIND)
                for kind_dir in rule_path.iterdir():
                    if not kind_dir.is_dir():
                        continue
                    template_file = kind_dir / "template.md"
                    if template_file.is_file():
                        tmpl, tmpl_errs = Template.from_path(template_file)
                        if tmpl:
                            templates[tmpl.kind] = tmpl
                        else:
                            errors.extend([str(e) for e in tmpl_errs])

            rules[rule_id] = LoadedRule(rule=rule, templates=templates)

        # Get all system names
        registered_systems = meta.get_all_system_names()

        ctx = cls(
            adapter_dir=adapter_dir,
            project_root=project_root,
            meta=meta,
            rules=rules,
            registered_systems=registered_systems,
            _errors=errors,
        )
        return ctx

    def get_template(self, rule_id: str, kind: str) -> Optional[Template]:
        """Get a loaded template by rule and kind."""
        loaded_rule = self.rules.get(rule_id)
        if not loaded_rule:
            return None
        return loaded_rule.templates.get(kind)

    def get_all_templates(self) -> Dict[str, Template]:
        """Get all loaded templates as kind -> Template mapping."""
        result: Dict[str, Template] = {}
        for loaded_rule in self.rules.values():
            result.update(loaded_rule.templates)
        return result

    def get_template_for_kind(self, kind: str) -> Optional[Template]:
        """Get template for a kind from any rule."""
        for loaded_rule in self.rules.values():
            if kind in loaded_rule.templates:
                return loaded_rule.templates[kind]
        return None

    def get_all_kinds(self) -> Set[str]:
        """Get all known artifact kinds from loaded templates.

        Returns lowercase set of kind names (e.g., {"prd", "design", "feature", "adr"}).
        """
        kinds: Set[str] = set()
        for loaded_rule in self.rules.values():
            for kind in loaded_rule.templates.keys():
                kinds.add(kind.lower())
        return kinds

    def get_known_id_kinds(self) -> Set[str]:
        """Get all known ID kinds from template markers.

        Scans all templates for fdd:id:<kind> markers and returns the set of kinds.
        This is useful for parsing composite FDD IDs.
        """
        kinds: Set[str] = set()
        for loaded_rule in self.rules.values():
            for tmpl in loaded_rule.templates.values():
                for block in tmpl.blocks or []:
                    if block.type == "id":
                        # block.name is the kind (e.g., "fr", "actor", "flow", "algo")
                        kinds.add(block.name.lower())
        return kinds

    @property
    def load_errors(self) -> List[str]:
        """Return any errors that occurred during loading."""
        return self._errors


# Global context instance (set by CLI on startup)
_global_context: Optional[FddContext] = None


def get_context() -> Optional[FddContext]:
    """Get the global FDD context."""
    return _global_context


def set_context(ctx: Optional[FddContext]) -> None:
    """Set the global FDD context."""
    global _global_context
    _global_context = ctx


def ensure_context(start_path: Optional[Path] = None) -> Optional[FddContext]:
    """Ensure context is loaded, loading if necessary."""
    global _global_context
    if _global_context is None:
        _global_context = FddContext.load(start_path)
    return _global_context


__all__ = [
    "FddContext",
    "LoadedRule",
    "get_context",
    "set_context",
    "ensure_context",
]
