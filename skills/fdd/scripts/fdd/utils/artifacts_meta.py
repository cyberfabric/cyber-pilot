"""
FDD Validator - Artifacts Metadata Registry

Parses and provides access to artifacts.json with the hierarchical system structure.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

from ..constants import ARTIFACTS_REGISTRY_FILENAME


@dataclass
class Rule:
    """A template rule defining format and rules package path."""

    rule_id: str
    format: str
    path: str  # Path to rules package (e.g., "rules/sdlc")

    @classmethod
    def from_dict(cls, rule_id: str, data: dict) -> "Rule":
        return cls(
            rule_id=rule_id,
            format=str(data.get("format", "")),
            path=str(data.get("path", "")),
        )

    def is_fdd_format(self) -> bool:
        """Check if this rule uses FDD format (full tooling support)."""
        return self.format == "FDD"

    def get_template_path(self, kind: str) -> str:
        """Get template file path for a given artifact kind."""
        # Path pattern: {path}/artifacts/{KIND}/template.md
        return f"{self.path.rstrip('/')}/artifacts/{kind}/template.md"

    def get_checklist_path(self, kind: str) -> str:
        """Get checklist file path for a given artifact kind."""
        # Path pattern: {path}/artifacts/{KIND}/checklist.md
        return f"{self.path.rstrip('/')}/artifacts/{kind}/checklist.md"

    def get_example_path(self, kind: str) -> str:
        """Get example file path for a given artifact kind."""
        # Path pattern: {path}/artifacts/{KIND}/examples/example.md
        return f"{self.path.rstrip('/')}/artifacts/{kind}/examples/example.md"


@dataclass
class Artifact:
    """A registered artifact (document)."""

    path: str
    kind: str  # Artifact kind (e.g., PRD, DESIGN, ADR)
    traceability: str  # "FULL" | "DOCS-ONLY"
    name: Optional[str] = None  # Human-readable name (optional)

    # Backward compatibility property
    @property
    def type(self) -> str:
        return self.kind

    @classmethod
    def from_dict(cls, data: dict) -> "Artifact":
        # Support both "kind" (new) and "type" (old) keys
        kind = str(data.get("kind", data.get("type", "")))
        name = data.get("name")
        return cls(
            path=str(data.get("path", "")),
            kind=kind,
            traceability=str(data.get("traceability", "DOCS-ONLY")),
            name=str(name) if name else None,
        )


@dataclass
class CodebaseEntry:
    """A registered source code directory."""

    path: str
    extensions: List[str] = field(default_factory=list)
    name: Optional[str] = None  # Human-readable name (optional)

    @classmethod
    def from_dict(cls, data: dict) -> "CodebaseEntry":
        exts = data.get("extensions", [])
        if not isinstance(exts, list):
            exts = []
        name = data.get("name")
        return cls(
            path=str(data.get("path", "")),
            extensions=[str(e) for e in exts if isinstance(e, str)],
            name=str(name) if name else None,
        )


@dataclass
class SystemNode:
    """A node in the system hierarchy (system, subsystem, component, module, etc.)."""

    name: str
    rules: str  # Reference to rule ID
    artifacts: List[Artifact] = field(default_factory=list)
    codebase: List[CodebaseEntry] = field(default_factory=list)
    children: List["SystemNode"] = field(default_factory=list)
    parent: Optional["SystemNode"] = field(default=None, repr=False)

    @classmethod
    def from_dict(cls, data: dict, parent: Optional["SystemNode"] = None) -> "SystemNode":
        rules = str(data.get("rules", ""))
        node = cls(
            name=str(data.get("name", "")),
            rules=rules,
            parent=parent,
        )

        raw_artifacts = data.get("artifacts", [])
        if isinstance(raw_artifacts, list):
            for a in raw_artifacts:
                if isinstance(a, dict):
                    node.artifacts.append(Artifact.from_dict(a))

        raw_codebase = data.get("codebase", [])
        if isinstance(raw_codebase, list):
            for c in raw_codebase:
                if isinstance(c, dict):
                    node.codebase.append(CodebaseEntry.from_dict(c))

        raw_children = data.get("children", [])
        if isinstance(raw_children, list):
            for child_data in raw_children:
                if isinstance(child_data, dict):
                    node.children.append(cls.from_dict(child_data, parent=node))

        return node


class ArtifactsMeta:
    """
    Parses and provides access to artifacts.json.

    Provides methods to find:
    - Artifacts by path or kind
    - Systems by name or level
    - Rules by ID
    - Codebase entries
    """

    def __init__(
        self,
        version: str,
        project_root: str,
        rules: Dict[str, Rule],
        systems: List[SystemNode],
    ):
        self.version = version
        self.project_root = project_root
        self.rules = rules
        self.systems = systems

        # Build indices for fast lookups
        self._artifacts_by_path: Dict[str, Tuple[Artifact, SystemNode]] = {}
        self._build_indices()

    def _build_indices(self) -> None:
        """Build lookup indices from the system tree."""
        for root_system in self.systems:
            self._index_system(root_system)

    def _index_system(self, node: SystemNode) -> None:
        """Index a system node and its descendants."""
        # Index artifacts
        for artifact in node.artifacts:
            normalized_path = self._normalize_path(artifact.path)
            self._artifacts_by_path[normalized_path] = (artifact, node)

        # Recurse into children
        for child in node.children:
            self._index_system(child)

    @staticmethod
    def _normalize_path(path: str) -> str:
        """Normalize path for consistent lookups."""
        p = path.strip()
        if p.startswith("./"):
            p = p[2:]
        return p

    @classmethod
    def from_dict(cls, data: dict) -> "ArtifactsMeta":
        """Create ArtifactsMeta from parsed JSON dict."""
        version = str(data.get("version", "1.0"))
        project_root = str(data.get("project_root", ".."))

        rules: Dict[str, Rule] = {}
        raw_rules = data.get("rules", {})
        if isinstance(raw_rules, dict):
            for rule_id, rule_data in raw_rules.items():
                if isinstance(rule_data, dict):
                    rules[rule_id] = Rule.from_dict(rule_id, rule_data)

        systems: List[SystemNode] = []
        raw_systems = data.get("systems", [])
        if isinstance(raw_systems, list):
            for sys_data in raw_systems:
                if isinstance(sys_data, dict):
                    systems.append(SystemNode.from_dict(sys_data))

        return cls(
            version=version,
            project_root=project_root,
            rules=rules,
            systems=systems,
        )

    @classmethod
    def from_json(cls, json_str: str) -> "ArtifactsMeta":
        """Create ArtifactsMeta from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_file(cls, path: Path) -> "ArtifactsMeta":
        """Create ArtifactsMeta from file path."""
        content = path.read_text(encoding="utf-8")
        return cls.from_json(content)

    # === Rule Methods ===

    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """Get a rule by ID."""
        return self.rules.get(rule_id)

    # === Artifact Methods ===

    def get_artifact_by_path(self, path: str) -> Optional[Tuple[Artifact, SystemNode]]:
        """Get artifact and its owning system by path."""
        normalized = self._normalize_path(path)
        return self._artifacts_by_path.get(normalized)

    def iter_all_artifacts(self) -> Iterator[Tuple[Artifact, SystemNode]]:
        """Iterate over all artifacts with their owning systems."""
        yield from self._artifacts_by_path.values()

    def iter_all_codebase(self) -> Iterator[Tuple["CodebaseEntry", SystemNode]]:
        """Iterate over all codebase entries with their owning systems."""
        def _iter_system(system: SystemNode) -> Iterator[Tuple["CodebaseEntry", SystemNode]]:
            for cb in system.codebase:
                yield cb, system
            for child in system.children:
                yield from _iter_system(child)

        for system in self.systems:
            yield from _iter_system(system)

    # === Resolution Methods ===

    def resolve_template_path(self, template_path: str, base_dir: Path) -> Path:
        """Resolve template path relative to project root."""
        project_root_path = (base_dir / self.project_root).resolve()
        return (project_root_path / template_path).resolve()

    # === Template Resolution for Artifacts ===

    def get_template_for_artifact(self, artifact: Artifact, system: SystemNode) -> Optional[str]:
        """Get the template path for an artifact based on its system's rule."""
        rule = self.rules.get(system.rules)
        if rule is None:
            return None
        return rule.get_template_path(artifact.kind)


def load_artifacts_meta(adapter_dir: Path) -> Tuple[Optional[ArtifactsMeta], Optional[str]]:
    """
    Load ArtifactsMeta from adapter directory.

    Args:
        adapter_dir: Path to adapter directory containing artifacts.json

    Returns:
        Tuple of (ArtifactsMeta or None, error message or None)
    """
    path = adapter_dir / ARTIFACTS_REGISTRY_FILENAME
    if not path.is_file():
        return None, f"Missing artifacts registry: {path}"
    try:
        meta = ArtifactsMeta.from_file(path)
        return meta, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON in artifacts registry {path}: {e}"
    except Exception as e:
        return None, f"Failed to load artifacts registry {path}: {e}"


def create_backup(path: Path) -> Optional[Path]:
    """Create a timestamped backup of a file or directory.

    Args:
        path: Path to file or directory to backup

    Returns:
        Path to backup if created, None otherwise
    """
    if not path.exists():
        return None

    from datetime import datetime
    import shutil

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_name = f"{path.name}.{timestamp}.backup"
    backup_path = path.parent / backup_name

    try:
        if path.is_dir():
            shutil.copytree(path, backup_path)
        else:
            shutil.copy2(path, backup_path)
        return backup_path
    except Exception:
        return None


def _join_path(base: str, tail: str) -> str:
    """Join base path with tail, handling edge cases."""
    b = str(base).strip()
    t = str(tail).strip()
    if b in {"", "."}:
        return t
    return f"{b.rstrip('/')}/{t.lstrip('/')}"


def generate_default_registry(
    project_name: str,
    fdd_core_rel_path: str,
) -> dict:
    """Generate default artifacts.json registry for a new project.

    Args:
        project_name: Name of the project (used as system name)
        fdd_core_rel_path: Relative path from adapter directory to FDD core rules

    Returns:
        Dictionary with the default registry structure (new format)
    """
    return {
        "version": "1.0",
        "project_root": "..",
        "rules": {
            "fdd-sdlc": {
                "format": "FDD",
                "path": _join_path(fdd_core_rel_path, "rules/sdlc"),
            },
        },
        "systems": [
            {
                "name": project_name,
                "rules": "fdd-sdlc",
                "artifacts": [],
                "codebase": [],
                "children": [],
            },
        ],
    }


__all__ = [
    "ArtifactsMeta",
    "SystemNode",
    "Artifact",
    "CodebaseEntry",
    "Rule",
    "load_artifacts_meta",
    "create_backup",
    "generate_default_registry",
]
