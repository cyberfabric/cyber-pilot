"""
Cypilot Validator - Artifacts Metadata Registry

Parses and provides access to artifacts.json with the hierarchical system structure.
"""

import fnmatch
import glob
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Optional, Set, Tuple

from ..constants import ARTIFACTS_REGISTRY_FILENAME

# Slug validation pattern: lowercase letters, numbers, hyphens (no leading/trailing hyphens)
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


@dataclass
class Kit:
    """A kit package defining format and path to templates/rules."""

    kit_id: str
    format: str
    path: str  # Path to kit package (e.g., "kits/sdlc")
    artifacts: Dict[str, Dict[str, str]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, kit_id: str, data: dict) -> "Kit":
        raw_format = (data or {}).get("format", "")
        fmt = str(raw_format).strip() if isinstance(raw_format, str) else ""

        raw_path = (data or {}).get("path", "")
        path = str(raw_path).strip() if isinstance(raw_path, str) else ""

        raw_artifacts = (data or {}).get("artifacts", {})
        artifacts: Dict[str, Dict[str, str]] = {}
        if isinstance(raw_artifacts, dict):
            for kind, spec in raw_artifacts.items():
                if not isinstance(kind, str) or not kind.strip():
                    continue
                if not isinstance(spec, dict):
                    continue
                tpl = spec.get("template")
                ex = spec.get("examples")
                if isinstance(tpl, str) and tpl.strip() and isinstance(ex, str) and ex.strip():
                    artifacts[kind.strip().upper()] = {"template": tpl.strip(), "examples": ex.strip()}
        return cls(
            kit_id=kit_id,
            format=fmt,
            path=path,
            artifacts=artifacts,
        )

    def is_cypilot_format(self) -> bool:
        """Check if this kit uses Cypilot format (full tooling support)."""
        return self.format == "Cypilot"

    @staticmethod
    def _substitute_registry_tokens(path_template: str) -> str:
        """Expand registry tokens in a path template.

        Currently supported:
        - {project_root}: expands to '.' (caller resolves relative to actual project root Path)
        """
        out = str(path_template or "")
        out = out.replace("{project_root}", ".")
        return out

    def get_template_path(self, kind: str) -> str:
        """Get template file path for a given artifact kind."""
        k = str(kind or "").strip().upper()
        if self.artifacts and k in self.artifacts:
            tpl = (self.artifacts.get(k) or {}).get("template")
            if isinstance(tpl, str) and tpl.strip():
                return self._substitute_registry_tokens(tpl.strip())
        # Backward compatible default: {path}/artifacts/{KIND}/template.md
        return f"{self.path.rstrip('/')}/artifacts/{kind}/template.md"

    def get_examples_path(self, kind: str) -> str:
        """Get examples directory path for a given artifact kind."""
        k = str(kind or "").strip().upper()
        if self.artifacts and k in self.artifacts:
            ex = (self.artifacts.get(k) or {}).get("examples")
            if isinstance(ex, str) and ex.strip():
                return self._substitute_registry_tokens(ex.strip())
        # Backward compatible default: {path}/artifacts/{KIND}/examples
        return f"{self.path.rstrip('/')}/artifacts/{kind}/examples"


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
class IgnoreBlock:
    """Global ignore rule block."""

    reason: str
    patterns: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "IgnoreBlock":
        reason = str((data or {}).get("reason", "") or "").strip()
        raw_patterns = (data or {}).get("patterns", [])
        patterns: List[str] = []
        if isinstance(raw_patterns, list):
            patterns = [str(p).strip() for p in raw_patterns if isinstance(p, str) and str(p).strip()]
        return cls(reason=reason, patterns=patterns)


@dataclass
class AutodetectArtifactPattern:
    pattern: str
    traceability: str
    required: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "AutodetectArtifactPattern":
        return cls(
            pattern=str((data or {}).get("pattern", "") or "").strip(),
            traceability=str((data or {}).get("traceability", "FULL") or "FULL").strip(),
            required=bool((data or {}).get("required", True)),
        )


@dataclass
class AutodetectRule:
    """Autodetect rule (v1.1+)."""

    kit: Optional[str] = None
    system_root: Optional[str] = None
    artifacts_root: Optional[str] = None
    aliases: Dict[str, dict] = field(default_factory=dict)
    artifacts: Dict[str, AutodetectArtifactPattern] = field(default_factory=dict)
    codebase: List[CodebaseEntry] = field(default_factory=list)
    validation: Dict[str, object] = field(default_factory=dict)
    children: List["AutodetectRule"] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "AutodetectRule":
        raw_artifacts = (data or {}).get("artifacts", {})
        artifacts: Dict[str, AutodetectArtifactPattern] = {}
        if isinstance(raw_artifacts, dict):
            for kind, v in raw_artifacts.items():
                if isinstance(kind, str) and isinstance(v, dict):
                    artifacts[kind] = AutodetectArtifactPattern.from_dict(v)

        raw_codebase = (data or {}).get("codebase", [])
        codebase: List[CodebaseEntry] = []
        if isinstance(raw_codebase, list):
            for c in raw_codebase:
                if isinstance(c, dict):
                    codebase.append(CodebaseEntry.from_dict(c))

        raw_children = (data or {}).get("children", [])
        children: List[AutodetectRule] = []
        if isinstance(raw_children, list):
            for r in raw_children:
                if isinstance(r, dict):
                    children.append(cls.from_dict(r))

        aliases = (data or {}).get("aliases", {})
        if not isinstance(aliases, dict):
            aliases = {}

        validation = (data or {}).get("validation", {})
        if not isinstance(validation, dict):
            validation = {}

        kit = (data or {}).get("kit", None)
        return cls(
            kit=str(kit).strip() if isinstance(kit, str) and str(kit).strip() else None,
            system_root=str((data or {}).get("system_root", "") or "").strip() or None,
            artifacts_root=str((data or {}).get("artifacts_root", "") or "").strip() or None,
            aliases={str(k): v for k, v in aliases.items() if isinstance(k, str) and isinstance(v, dict)},
            artifacts=artifacts,
            codebase=codebase,
            validation=validation,
            children=children,
        )


@dataclass
class SystemNode:
    """A node in the system hierarchy (system, subsystem, component, module, etc.)."""

    name: str
    slug: str  # Machine-readable identifier (lowercase, no spaces)
    kit: str  # Reference to kit ID
    artifacts: List[Artifact] = field(default_factory=list)
    codebase: List[CodebaseEntry] = field(default_factory=list)
    children: List["SystemNode"] = field(default_factory=list)
    autodetect: List[AutodetectRule] = field(default_factory=list)
    parent: Optional["SystemNode"] = field(default=None, repr=False)

    def get_hierarchy_prefix(self) -> str:
        """Get the hierarchical ID prefix by concatenating slugs from root to this node.

        Example: For a component 'auth' under subsystem 'core' under system 'saas-platform',
        returns 'saas-platform-core-auth'.
        """
        parts: List[str] = []
        node: Optional[SystemNode] = self
        while node is not None:
            if node.slug:
                parts.append(node.slug)
            node = node.parent
        return "-".join(reversed(parts))

    def validate_slug(self) -> Optional[str]:
        """Validate the slug format. Returns error message if invalid, None if valid."""
        if not self.slug:
            # Allow grouping nodes (no slug) only if they don't directly own artifacts/codebase.
            if (self.artifacts or []) or (self.codebase or []):
                return f"Missing slug for system '{self.name}'"
            return None
        if not SLUG_PATTERN.match(self.slug):
            return (
                f"Invalid slug '{self.slug}' for system '{self.name}'. "
                "Slug must be lowercase letters, numbers, and hyphens only "
                "(no leading/trailing hyphens, no spaces)."
            )
        return None

    @classmethod
    def from_dict(cls, data: dict, parent: Optional["SystemNode"] = None) -> "SystemNode":
        kit = str(data.get("kit", data.get("kits", "")))
        # For backward compatibility, generate slug from name if not provided
        name = str(data.get("name", ""))
        raw_slug = (data or {}).get("slug", None)
        slug = str(raw_slug) if isinstance(raw_slug, str) else ""
        if not slug and ("slug" not in (data or {})) and name:
            # Auto-generate slug from name: lowercase, replace spaces with hyphens
            slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        node = cls(
            name=name,
            slug=slug,
            kit=kit,
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

        raw_autodetect = data.get("autodetect", [])
        if isinstance(raw_autodetect, list):
            for r in raw_autodetect:
                if isinstance(r, dict):
                    node.autodetect.append(AutodetectRule.from_dict(r))

        return node


class ArtifactsMeta:
    """
    Parses and provides access to artifacts.json.

    Provides methods to find:
    - Artifacts by path or kind
    - Systems by name or level
    - Kits by ID
    - Codebase entries
    """

    def __init__(
        self,
        version: str,
        project_root: str,
        kits: Dict[str, Kit],
        systems: List[SystemNode],
        ignore: Optional[List[IgnoreBlock]] = None,
    ):
        self.version = version
        self.project_root = project_root
        self.kits = kits
        self.systems = systems

        self.ignore = ignore or []
        self._ignore_patterns: List[str] = []
        for blk in self.ignore:
            for p in (blk.patterns or []):
                sp = str(p).strip()
                if sp:
                    self._ignore_patterns.append(sp)

        # Build indices for fast lookups
        self._artifacts_by_path: Dict[str, Tuple[Artifact, SystemNode]] = {}
        self._build_indices()

    def is_ignored(self, rel_path: str) -> bool:
        """Return True if rel_path matches any registry root ignore pattern."""
        rp = self._normalize_path(rel_path)
        for pat in self._ignore_patterns:
            if fnmatch.fnmatch(rp, pat):
                return True
            # Treat "dir/*" as also ignoring "dir" itself (common expectation for directory ignores).
            if pat.endswith("/*"):
                base = pat[:-2]
                if rp == base:
                    return True
        return False

    def _build_indices(self) -> None:
        """Build lookup indices from the system tree."""
        for root_system in self.systems:
            self._index_system(root_system)

    def _index_system(self, node: SystemNode) -> None:
        """Index a system node and its descendants."""
        # Index artifacts
        for artifact in node.artifacts:
            if self.is_ignored(artifact.path):
                continue
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

        ignore: List[IgnoreBlock] = []
        raw_ignore = data.get("ignore", [])
        if isinstance(raw_ignore, list):
            for blk in raw_ignore:
                if isinstance(blk, dict):
                    ignore.append(IgnoreBlock.from_dict(blk))

        kits: Dict[str, Kit] = {}
        raw_kits = data.get("kits", {})
        if isinstance(raw_kits, dict):
            for kit_id, kit_data in raw_kits.items():
                if isinstance(kit_data, dict):
                    kits[kit_id] = Kit.from_dict(kit_id, kit_data)

        systems: List[SystemNode] = []
        raw_systems = data.get("systems", [])
        if isinstance(raw_systems, list):
            for sys_data in raw_systems:
                if isinstance(sys_data, dict):
                    systems.append(SystemNode.from_dict(sys_data))

        return cls(
            version=version,
            project_root=project_root,
            kits=kits,
            systems=systems,
            ignore=ignore,
        )

    def rebuild_indices(self) -> None:
        self._artifacts_by_path = {}
        self._build_indices()

    def get_kit(self, kit_id: str) -> Optional[Kit]:
        """Get a kit definition by ID."""
        return (self.kits or {}).get(str(kit_id))

    def expand_autodetect(
        self,
        *,
        adapter_dir: Path,
        project_root: Path,
        is_kind_registered: Optional[Callable[[str, str], bool]] = None,
    ) -> List[str]:
        """Expand autodetect rules into concrete artifact/codebase entries.

        Returns a list of validation error messages (best-effort).
        """

        errors: List[str] = []

        # Normalize roots to avoid path-prefix mismatches on macOS (e.g. /var vs /private/var)
        adapter_dir = adapter_dir.resolve()
        project_root = project_root.resolve()

        def _substitute(s: str, *, system: str, system_root: str, parent_root: str) -> str:
            out = str(s)
            out = out.replace("{system}", system)
            # {project_root} is the project root directory, not the registry's relative project_root string.
            # It intentionally expands to '.' so templates like '{project_root}/subsystems' resolve under
            # the provided `project_root` path.
            out = out.replace("{project_root}", ".")
            out = out.replace("{system_root}", system_root)
            out = out.replace("{parent_root}", parent_root)
            return out

        def _resolve_path(expanded: str) -> Path:
            e = str(expanded).strip()
            pr = str(self.project_root).strip()
            if pr and (e == pr or e.startswith(pr.rstrip("/") + "/")):
                return (adapter_dir / e).resolve()
            return (project_root / e).resolve()

        def _rel_to_project_root(p: Path) -> Optional[str]:
            try:
                return p.relative_to(project_root).as_posix()
            except Exception:
                return None

        def _glob_files(root_abs: Path, pat: str) -> List[Path]:
            if not pat:
                return []
            g = str((root_abs / pat).as_posix())
            hits = [Path(x) for x in glob.glob(g, recursive=True)]
            out: List[Path] = []
            for h in hits:
                if not h.is_file():
                    continue
                rel = _rel_to_project_root(h.resolve())
                if not rel:
                    continue
                if self.is_ignored(rel):
                    continue
                out.append(h.resolve())
            return out

        def _iter_markdown_files(root_abs: Path) -> List[Path]:
            if not root_abs.is_dir():
                return []
            g = str((root_abs / "**" / "*.md").as_posix())
            hits = [Path(x) for x in glob.glob(g, recursive=True)]
            out: List[Path] = []
            for h in hits:
                if not h.is_file():
                    continue
                rel = _rel_to_project_root(h.resolve())
                if not rel:
                    continue
                if self.is_ignored(rel):
                    continue
                out.append(h.resolve())
            return out

        def _get_or_create_child_system(parent: SystemNode, *, slug: str, name: str, kit: str) -> SystemNode:
            for ch in parent.children:
                if str(ch.slug) == str(slug):
                    return ch
            child = SystemNode(name=str(name), slug=str(slug), kit=str(kit), artifacts=[], codebase=[], children=[], autodetect=[], parent=parent)
            parent.children.append(child)
            return child

        def _discover_child_system_roots(
            parent: SystemNode,
            rule: AutodetectRule,
            *,
            parent_root_str: str,
        ) -> List[Tuple[SystemNode, str, Path]]:
            """Discover child systems for rules whose system_root contains $system.

            Returns list of (child_node, child_system_root_str, child_system_root_abs).
            """

            system_root_template = str(rule.system_root or "{project_root}")
            if "$system" not in system_root_template:
                return []

            # Expand other placeholders, keep $system for globbing.
            templ = _substitute(system_root_template, system=parent.slug, system_root="", parent_root=parent_root_str)
            # Build directory glob: replace $system with '*'
            g = templ.replace("$system", "*")

            # Resolve as project-root relative (preferred). If it looks adapter-root relative, _resolve_path handles it.
            root_glob = str((_resolve_path(g)).as_posix())
            hits = [Path(x) for x in glob.glob(root_glob, recursive=False)]
            out: List[Tuple[SystemNode, str, Path]] = []
            for h in hits:
                try:
                    h = h.resolve()
                except Exception:
                    continue
                if not h.exists() or not h.is_dir():
                    continue
                rel = _rel_to_project_root(h)
                if rel is None:
                    continue
                if self.is_ignored(rel):
                    continue
                raw_name = h.name
                slug = generate_slug(str(raw_name))
                if not slug:
                    continue
                kit_id = rule.kit or parent.kit
                child = _get_or_create_child_system(parent, slug=slug, name=str(raw_name), kit=str(kit_id))
                out.append((child, rel, h))

            return out

        def _apply_rule(
            node: SystemNode,
            rule: AutodetectRule,
            *,
            parent_root_str: str,
            system_root_override: Optional[Tuple[str, Path]] = None,
        ) -> Tuple[List[Artifact], List[CodebaseEntry], str, List[AutodetectRule]]:
            kit_id = rule.kit or node.kit

            # Resolve system_root
            if system_root_override is not None:
                system_root_str, system_root_abs = system_root_override
            else:
                system_root_template = rule.system_root or "{project_root}"
                system_root_str = _substitute(system_root_template, system=node.slug, system_root="", parent_root=parent_root_str)
                system_root_abs = _resolve_path(system_root_str)
                system_root_rel = _rel_to_project_root(system_root_abs)
                if system_root_rel is None:
                    # If outside project_root, treat as out-of-scope
                    system_root_rel = ""

            # Resolve artifacts_root
            artifacts_root_template = rule.artifacts_root or "{system_root}"
            artifacts_root_str = _substitute(artifacts_root_template, system=node.slug, system_root=system_root_str, parent_root=parent_root_str)
            artifacts_root_abs = _resolve_path(artifacts_root_str)

            discovered_artifacts: List[Artifact] = []
            used_patterns: List[str] = []
            for kind, ap in (rule.artifacts or {}).items():
                kind_s = str(kind).strip()
                if not kind_s:
                    continue
                if ap.pattern:
                    used_patterns.append(str(ap.pattern))
                if is_kind_registered is not None and bool(rule.validation.get("require_kind_registered_in_kit", False)):
                    if not is_kind_registered(str(kit_id), kind_s):
                        errors.append(f"Autodetect kind not registered in kit: kit={kit_id} kind={kind_s} system={node.slug}")
                        continue

                hits = _glob_files(artifacts_root_abs, ap.pattern)
                if ap.required and not hits:
                    errors.append(f"Required autodetect artifact missing: system={node.slug} kind={kind_s} pattern={ap.pattern}")
                for h in hits:
                    rel = _rel_to_project_root(h)
                    if not rel:
                        continue
                    if bool(rule.validation.get("require_md_extension", False)) and not rel.lower().endswith(".md"):
                        errors.append(f"Autodetect artifact must be .md: {rel}")
                        continue
                    discovered_artifacts.append(Artifact(path=rel, kind=kind_s, traceability=str(ap.traceability or "FULL")))

            if bool(rule.validation.get("fail_on_unmatched_markdown", False)):
                md_files = _iter_markdown_files(artifacts_root_abs)
                for mf in md_files:
                    try:
                        rel_to_root = mf.relative_to(artifacts_root_abs).as_posix()
                    except Exception:
                        continue
                    matched = False
                    for pat in used_patterns:
                        if pat and fnmatch.fnmatch(rel_to_root, pat):
                            matched = True
                            break
                    if not matched:
                        rel = _rel_to_project_root(mf)
                        if rel:
                            errors.append(f"Unmatched markdown under artifacts_root: system={node.slug} path={rel}")

            discovered_codebase: List[CodebaseEntry] = []
            for cb in (rule.codebase or []):
                cb_path_t = cb.path
                cb_path_expanded = _substitute(cb_path_t, system=node.slug, system_root=system_root_str, parent_root=parent_root_str)
                cb_abs = _resolve_path(cb_path_expanded)
                cb_rel = _rel_to_project_root(cb_abs)
                if not cb_rel:
                    continue
                if self.is_ignored(cb_rel):
                    continue
                discovered_codebase.append(CodebaseEntry(path=cb_rel, extensions=list(cb.extensions or []), name=cb.name))

            return discovered_artifacts, discovered_codebase, system_root_str, list(rule.children or [])

        def _expand_node(node: SystemNode, inherited_rules: List[Tuple[AutodetectRule, str]]) -> List[Tuple[AutodetectRule, str]]:
            effective: List[Tuple[AutodetectRule, str]] = list(inherited_rules)
            default_parent_root = inherited_rules[0][1] if inherited_rules else str(self.project_root)
            for r in (node.autodetect or []):
                # Node-level rules use the current node's parent_root (derived from inheritance if any).
                effective.append((r, default_parent_root))

            # Apply rules in order
            existing_artifacts_by_path: Dict[str, Artifact] = {self._normalize_path(a.path): a for a in node.artifacts}
            existing_codebase_by_path: Dict[str, CodebaseEntry] = {self._normalize_path(c.path): c for c in node.codebase}

            next_inherited: List[Tuple[AutodetectRule, str]] = []

            processed_children: Set[str] = set()

            for rule, parent_root_str in effective:
                # Special: system_root containing $system means "discover child systems".
                if rule.system_root and "$system" in str(rule.system_root):
                    discovered = _discover_child_system_roots(node, rule, parent_root_str=parent_root_str)
                    for child_node, child_root_str, child_root_abs in discovered:
                        disc_artifacts, disc_codebase, system_root_str, child_rules = _apply_rule(
                            child_node,
                            rule,
                            parent_root_str=parent_root_str,
                            system_root_override=(child_root_str, child_root_abs),
                        )

                        existing_child_artifacts_by_path: Dict[str, Artifact] = {self._normalize_path(a.path): a for a in child_node.artifacts}
                        existing_child_codebase_by_path: Dict[str, CodebaseEntry] = {self._normalize_path(c.path): c for c in child_node.codebase}

                        for da in disc_artifacts:
                            np = self._normalize_path(da.path)
                            if np in existing_child_artifacts_by_path:
                                if str(existing_child_artifacts_by_path[np].kind) != str(da.kind):
                                    errors.append(
                                        f"Autodetect conflict on path with different kind: path={da.path} explicit={existing_child_artifacts_by_path[np].kind} detected={da.kind}"
                                    )
                                continue
                            existing_child_artifacts_by_path[np] = da
                            child_node.artifacts.append(da)

                        for dc in disc_codebase:
                            np = self._normalize_path(dc.path)
                            if np in existing_child_codebase_by_path:
                                continue
                            existing_child_codebase_by_path[np] = dc
                            child_node.codebase.append(dc)

                        # Expand grandchildren immediately with correct parent_root.
                        inherited_for_grandchildren = [(cr, system_root_str) for cr in (child_rules or [])]
                        _expand_node(child_node, inherited_for_grandchildren)
                        processed_children.add(self._normalize_path(child_node.slug))

                    continue

                disc_artifacts, disc_codebase, system_root_str, child_rules = _apply_rule(node, rule, parent_root_str=parent_root_str)
                for da in disc_artifacts:
                    np = self._normalize_path(da.path)
                    if np in existing_artifacts_by_path:
                        # explicit wins; if kind differs, keep explicit and record error
                        if str(existing_artifacts_by_path[np].kind) != str(da.kind):
                            errors.append(f"Autodetect conflict on path with different kind: path={da.path} explicit={existing_artifacts_by_path[np].kind} detected={da.kind}")
                        continue
                    existing_artifacts_by_path[np] = da
                    node.artifacts.append(da)

                for dc in disc_codebase:
                    np = self._normalize_path(dc.path)
                    if np in existing_codebase_by_path:
                        continue
                    existing_codebase_by_path[np] = dc
                    node.codebase.append(dc)

                # Inherit child rules for next nesting level
                for cr in child_rules:
                    next_inherited.append((cr, system_root_str))

            for child in node.children:
                if self._normalize_path(child.slug) in processed_children:
                    continue
                child_inherited = _expand_node(child, next_inherited)
                # Child's own next_inherited is not propagated to siblings
                _ = child_inherited

            return next_inherited

        for sys_node in self.systems:
            _expand_node(sys_node, [])

        self.rebuild_indices()
        return errors

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

    # === Kit Methods ===

    def get_kit(self, kit_id: str) -> Optional[Kit]:
        """Get a kit by ID."""
        return self.kits.get(kit_id)

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
                if self.is_ignored(cb.path):
                    continue
                yield cb, system
            for child in system.children:
                yield from _iter_system(child)

        for system in self.systems:
            yield from _iter_system(system)

    def iter_all_system_prefixes(self) -> Iterator[str]:
        """Iterate over all system prefixes used in Cypilot IDs.

        Cypilot IDs are prefixed as: cpt-<system>-<kind>-<slug>

        Where <system> is the system node's slug hierarchy prefix (see
        SystemNode.get_hierarchy_prefix()). This differs from the human-facing
        system 'name'.
        """

        def _iter_system(node: SystemNode) -> Iterator[str]:
            try:
                prefix = node.get_hierarchy_prefix()
            except Exception:
                prefix = ""
            if prefix:
                yield prefix
            for child in node.children:
                yield from _iter_system(child)

        for system in self.systems:
            yield from _iter_system(system)

    def get_all_system_prefixes(self) -> set:
        """Get a set of all system prefixes (normalized to lowercase)."""
        return {p.lower() for p in self.iter_all_system_prefixes()}

    def iter_all_systems(self) -> Iterator[SystemNode]:
        """Iterate over all system nodes in the registry (including nested children)."""
        def _iter_system(node: SystemNode) -> Iterator[SystemNode]:
            yield node
            for child in node.children:
                yield from _iter_system(child)

        for system in self.systems:
            yield from _iter_system(system)

    def validate_all_slugs(self) -> List[str]:
        """Validate all slugs in the registry. Returns list of error messages."""
        errors = []
        for node in self.iter_all_systems():
            error = node.validate_slug()
            if error:
                errors.append(error)
        return errors


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


def generate_slug(name: str) -> str:
    """Generate a valid slug from a name.

    Converts to lowercase, replaces non-alphanumeric chars with hyphens,
    removes leading/trailing hyphens.

    Args:
        name: Human-readable name

    Returns:
        Valid slug string
    """
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    # Collapse multiple hyphens
    slug = re.sub(r"-+", "-", slug)
    return slug if slug else "unnamed"


def generate_default_registry(
    project_name: str,
    cypilot_core_rel_path: str,
) -> dict:
    """Generate default artifacts.json registry for a new project.

    Args:
        project_name: Name of the project (used as system name)
        cypilot_core_rel_path: Relative path from adapter directory to Cypilot kits

    Returns:
        Dictionary with the default registry structure (new format)
    """
    return {
        "version": "1.0",
        "project_root": "..",
        "kits": {
            "cypilot-sdlc": {
                "format": "Cypilot",
                "path": _join_path(cypilot_core_rel_path, "kits/sdlc"),
            },
        },
        "systems": [
            {
                "name": project_name,
                "slug": generate_slug(project_name),
                "kit": "cypilot-sdlc",
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
    "IgnoreBlock",
    "AutodetectRule",
    "AutodetectArtifactPattern",
    "CodebaseEntry",
    "Kit",
    "SLUG_PATTERN",
    "load_artifacts_meta",
    "create_backup",
    "generate_default_registry",
    "generate_slug",
]
