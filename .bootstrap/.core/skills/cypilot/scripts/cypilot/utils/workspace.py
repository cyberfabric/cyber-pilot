"""
Cypilot Workspace - Multi-repo federation support.

Loads and validates .cypilot-workspace.toml (standalone or inline in core.toml).
Each source maps a named repo to a local path, optional adapter location, and a role.
"""
# @cpt-algo:cpt-cypilot-feature-workspace:p1
# @cpt-begin:cpt-cypilot-algo-workspace-resolve-source:p1:inst-resolve-datamodel
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import re

from ..constants import WORKSPACE_CONFIG_FILENAME
from . import toml_utils

# Valid source roles
VALID_ROLES = {"artifacts", "codebase", "kits", "full"}

# Source name validation: alphanumeric, hyphens, underscores, dots only
_SOURCE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def validate_source_name(name: str) -> Optional[str]:
    """Validate a workspace source name. Returns error message or None."""
    if not name:
        return "Source name cannot be empty"
    if not _SOURCE_NAME_RE.match(name):
        return (
            f"Invalid source name '{name}' — "
            "must start with alphanumeric and contain only [A-Za-z0-9._-]"
        )
    if ".." in name:
        return f"Invalid source name '{name}' — must not contain '..'"
    return None

_CONFIG_FILENAME = "core.toml"


def _resolve_config_path(project_root: Path, cypilot_rel: str) -> Path:
    """Resolve the config file path, preferring config/ subdirectory."""
    config_path = (project_root / cypilot_rel / "config" / _CONFIG_FILENAME).resolve()
    if not config_path.is_file():
        config_path = (project_root / cypilot_rel / _CONFIG_FILENAME).resolve()
    return config_path


@dataclass
class SourceEntry:
    """A named source repo in the workspace."""

    name: str
    path: Optional[str] = None  # Filesystem path (resolved relative to workspace file location)
    adapter: Optional[str] = None  # Path to adapter dir within the source, or None
    role: str = "full"  # "artifacts" | "codebase" | "kits" | "full"
    url: Optional[str] = None  # Git remote URL (HTTPS or SSH)
    branch: Optional[str] = None  # Git branch/ref to checkout

    def __post_init__(self) -> None:
        self.path = (self.path.strip() or None) if self.path else None
        self.url = (self.url.strip() or None) if self.url else None
        self.branch = (self.branch.strip() or None) if self.branch else None
        if self.role not in VALID_ROLES:
            raise ValueError(
                f"Source '{self.name}' has invalid role '{self.role}' "
                f"(valid: {', '.join(sorted(VALID_ROLES))})"
            )

    @classmethod
    def from_dict(cls, name: str, data: dict) -> "SourceEntry":
        raw_path = str((data or {}).get("path", "")).strip() or None
        raw_adapter = (data or {}).get("adapter", None)
        # Omitted key means no adapter (TOML has no null)
        adapter = str(raw_adapter).strip() if isinstance(raw_adapter, str) and str(raw_adapter).strip() else None
        raw_role = str((data or {}).get("role", "full")).strip().lower()
        raw_url = (data or {}).get("url", None)
        url = str(raw_url).strip() if isinstance(raw_url, str) and str(raw_url).strip() else None
        raw_branch = (data or {}).get("branch", None)
        branch = str(raw_branch).strip() if isinstance(raw_branch, str) and str(raw_branch).strip() else None
        return cls(name=name, path=raw_path, adapter=adapter, role=raw_role, url=url, branch=branch)

    def to_dict(self) -> dict:
        d: dict = {}
        if self.url is not None:
            d["url"] = self.url
        if self.branch is not None:
            d["branch"] = self.branch
        if self.path:
            d["path"] = self.path
        if self.adapter is not None:
            d["adapter"] = self.adapter
        if self.role != "full":
            d["role"] = self.role
        return d
# @cpt-end:cpt-cypilot-algo-workspace-resolve-source:p1:inst-resolve-datamodel


# @cpt-begin:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-datamodel
@dataclass
class TraceabilityConfig:
    """Workspace-level traceability settings."""

    cross_repo: bool = True
    resolve_remote_ids: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "TraceabilityConfig":
        return cls(
            cross_repo=bool((data or {}).get("cross_repo", True)),
            resolve_remote_ids=bool((data or {}).get("resolve_remote_ids", True)),
        )

    def to_dict(self) -> dict:
        return {
            "cross_repo": self.cross_repo,
            "resolve_remote_ids": self.resolve_remote_ids,
        }


@dataclass
class NamespaceRule:
    """Maps a Git host to a local directory template."""

    host: str  # e.g. "gitlab.com"
    template: str  # e.g. "{org}/{repo}"

    def to_dict(self) -> dict:
        return {"host": self.host, "template": self.template}


@dataclass
class ResolveConfig:
    """Workspace-level git URL resolution settings."""

    workdir: str = ".workspace-sources"
    namespace: List["NamespaceRule"] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "ResolveConfig":
        workdir = str((data or {}).get("workdir", ".workspace-sources")).strip()
        raw_ns = (data or {}).get("namespace", {})
        namespace: List[NamespaceRule] = []
        if isinstance(raw_ns, dict):
            for host, template in raw_ns.items():
                if isinstance(host, str) and isinstance(template, str):
                    namespace.append(NamespaceRule(host=host.strip(), template=template.strip()))
        return cls(workdir=workdir, namespace=namespace)

    def to_dict(self) -> dict:
        d: dict = {"workdir": self.workdir}
        if self.namespace:
            d["namespace"] = {r.host: r.template for r in self.namespace}
        return d
# @cpt-end:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-git-datamodel


# @cpt-begin:cpt-cypilot-algo-workspace-find-config:p1:inst-find-config-datamodel
@dataclass
class WorkspaceConfig:
    """Parsed workspace configuration."""

    version: str = "1.0"
    sources: Dict[str, SourceEntry] = field(default_factory=dict)
    traceability: TraceabilityConfig = field(default_factory=TraceabilityConfig)
    resolve: Optional[ResolveConfig] = None  # Git URL resolution config
    workspace_file: Optional[Path] = None  # Absolute path to the workspace file
    is_inline: bool = False  # True if loaded from core.toml inline workspace
    resolution_base: Optional[Path] = None  # Override for source path resolution base directory

    @classmethod
    def from_dict(
        cls,
        data: dict,
        *,
        workspace_file: Optional[Path] = None,
        is_inline: bool = False,
        resolution_base: Optional[Path] = None,
    ) -> "WorkspaceConfig":
        version = str((data or {}).get("version", "1.0")).strip()
        sources: Dict[str, SourceEntry] = {}
        raw_sources = (data or {}).get("sources", {})
        if not isinstance(raw_sources, dict):
            raise ValueError("'sources' must be a mapping")
        for name, src_data in raw_sources.items():
            if not isinstance(src_data, dict):
                raise ValueError(f"Source '{name}' must be a table, got {type(src_data).__name__}")
            if isinstance(name, str) and name.strip():
                sources[name.strip()] = SourceEntry.from_dict(name.strip(), src_data)

        traceability = TraceabilityConfig()
        raw_trace = (data or {}).get("traceability", None)
        if isinstance(raw_trace, dict):
            traceability = TraceabilityConfig.from_dict(raw_trace)

        resolve_cfg: Optional[ResolveConfig] = None
        raw_resolve = (data or {}).get("resolve", None)
        if isinstance(raw_resolve, dict):
            resolve_cfg = ResolveConfig.from_dict(raw_resolve)

        return cls(
            version=version,
            sources=sources,
            traceability=traceability,
            resolve=resolve_cfg,
            workspace_file=workspace_file,
            is_inline=is_inline,
            resolution_base=resolution_base,
        )

    def to_dict(self) -> dict:
        d: dict = {"version": self.version}
        d["sources"] = {name: src.to_dict() for name, src in self.sources.items()}
        trace = self.traceability.to_dict()
        if trace != TraceabilityConfig().to_dict():
            d["traceability"] = trace
        if self.resolve is not None:
            d["resolve"] = self.resolve.to_dict()
        return d

    @classmethod
    def load(cls, workspace_path: Path) -> Tuple[Optional["WorkspaceConfig"], Optional[str]]:
        """Load workspace config from a TOML file.

        Args:
            workspace_path: Absolute path to .cypilot-workspace.toml

        Returns:
            (WorkspaceConfig, None) on success or (None, error_message) on failure.
        """
        if not workspace_path.is_file():
            return None, f"Workspace file not found: {workspace_path}"
        try:
            data = toml_utils.load(workspace_path)
        except Exception as e:
            return None, f"Failed to read workspace file {workspace_path}: {e}"
        if not isinstance(data, dict):
            return None, f"Invalid workspace file (expected TOML table): {workspace_path}"
        if "version" not in data:
            return None, f"Missing required field 'version' in {workspace_path}"
        if "sources" not in data:
            return None, f"Missing required field 'sources' in {workspace_path}"
        try:
            cfg = cls.from_dict(data, workspace_file=workspace_path.resolve(), is_inline=False)
        except ValueError as e:
            return None, f"Invalid workspace config in {workspace_path}: {e}"
        errs = cfg.validate()
        if errs:
            return None, f"Invalid workspace config in {workspace_path}: {'; '.join(errs)}"
        return cfg, None
    # @cpt-end:cpt-cypilot-algo-workspace-find-config:p1:inst-find-config-datamodel

    # @cpt-algo:cpt-cypilot-algo-workspace-resolve-source:p1
    def resolve_source_path(self, source_name: str) -> Optional[Path]:
        """Resolve the absolute filesystem path for a named source.

        For standalone workspace files, paths resolve relative to the file's
        parent directory.  For inline workspaces (defined in core.toml),
        paths resolve relative to the project root (set via resolution_base).
        For git URL sources, delegates to git_utils.resolve_git_source().
        """
        # @cpt-begin:cpt-cypilot-algo-workspace-resolve-source:p1:inst-resolve-lookup
        src = self.sources.get(source_name)
        # @cpt-end:cpt-cypilot-algo-workspace-resolve-source:p1:inst-resolve-lookup
        # @cpt-begin:cpt-cypilot-algo-workspace-resolve-source:p1:inst-resolve-if-not-found
        if src is None:
            return None
        # @cpt-end:cpt-cypilot-algo-workspace-resolve-source:p1:inst-resolve-if-not-found
        # @cpt-begin:cpt-cypilot-algo-workspace-resolve-source:p1:inst-resolve-determine-base
        if self.resolution_base is not None:
            base = self.resolution_base
        elif self.workspace_file is not None:
            base = self.workspace_file.parent
        else:
            return None
        # @cpt-end:cpt-cypilot-algo-workspace-resolve-source:p1:inst-resolve-determine-base
        # @cpt-begin:cpt-cypilot-algo-workspace-resolve-source:p1:inst-resolve-return
        if src.path:
            return (base / src.path).resolve()
        # @cpt-end:cpt-cypilot-algo-workspace-resolve-source:p1:inst-resolve-return
        # @cpt-begin:cpt-cypilot-algo-workspace-resolve-source:p1:inst-resolve-git-url-delegate
        # @cpt-begin:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-resolve-git-url-delegate
        if src.url:
            from .git_utils import resolve_git_source
            return resolve_git_source(src, self.resolve or ResolveConfig(), base)
        # @cpt-end:cpt-cypilot-algo-workspace-resolve-git-url:p1:inst-resolve-git-url-delegate
        # @cpt-end:cpt-cypilot-algo-workspace-resolve-source:p1:inst-resolve-git-url-delegate
        # @cpt-begin:cpt-cypilot-algo-workspace-resolve-source:p1:inst-resolve-fallback
        return None
        # @cpt-end:cpt-cypilot-algo-workspace-resolve-source:p1:inst-resolve-fallback

    # @cpt-begin:cpt-cypilot-state-workspace-config-lifecycle:p1:inst-config-methods
    def resolve_source_adapter(self, source_name: str) -> Optional[Path]:
        """Resolve the absolute path to a source's adapter directory."""
        src = self.sources.get(source_name)
        if src is None or not src.adapter:
            return None
        source_root = self.resolve_source_path(source_name)
        if source_root is None:
            return None
        return (source_root / src.adapter).resolve()

    def validate(self) -> List[str]:
        """Validate workspace config and return list of error messages."""
        errors: List[str] = []
        for name, src in self.sources.items():
            if src.url and self.is_inline:
                errors.append(f"Source '{name}' has 'url' but inline workspaces only support local paths")
            if src.path and src.url:
                errors.append(f"Source '{name}' has both 'path' and 'url' — they are mutually exclusive")
            if src.path and src.branch:
                errors.append(f"Source '{name}' has both 'path' and 'branch' — branch is only valid with 'url'")
            if not src.path and not src.url:
                errors.append(f"Source '{name}' must have either 'path' or 'url'")
            if src.role not in VALID_ROLES:
                errors.append(f"Source '{name}' has invalid role '{src.role}' (valid: {', '.join(sorted(VALID_ROLES))})")
        return errors

    def add_source(
        self,
        name: str,
        path: Optional[str] = None,
        role: str = "full",
        adapter: Optional[str] = None,
        url: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> None:
        """Add or update a source entry."""
        self.sources[name] = SourceEntry(name=name, path=path, adapter=adapter, role=role, url=url, branch=branch)

    def save(self, target_path: Optional[Path] = None) -> Optional[str]:
        """Save workspace config to file.

        For standalone workspaces, writes the workspace dict directly.
        For inline workspaces, merges into the existing config file so that
        other sections (kits, project_root, ignore, etc.) are preserved.

        Args:
            target_path: Path to save to (defaults to self.workspace_file).

        Returns:
            None on success, error message on failure.
        """
        path = target_path or self.workspace_file
        if path is None:
            return "No target path specified for saving workspace config"
        try:
            if self.is_inline:
                # Merge into existing config to preserve other sections
                existing: dict = {}
                if path.is_file():
                    existing = toml_utils.load(path)
                    if not isinstance(existing, dict):
                        return f"Invalid config format in {path} (expected mapping)"
                existing["workspace"] = self.to_dict()
                toml_utils.dump(existing, path)
            else:
                toml_utils.dump(self.to_dict(), path)
            self.workspace_file = path.resolve()
            return None
        except (OSError, ValueError) as e:
            return f"Failed to save workspace config to {path}: {e}"
    # @cpt-end:cpt-cypilot-state-workspace-config-lifecycle:p1:inst-config-methods


# @cpt-begin:cpt-cypilot-algo-workspace-find-config:p1:inst-find-parse-inline-impl
def _parse_inline_workspace(
    ws_value: dict,
    project_root: Path,
) -> Tuple[Optional[WorkspaceConfig], Optional[str]]:
    """Parse an inline [workspace] dict from core.toml."""
    from .files import _read_cypilot_var

    cypilot_rel = _read_cypilot_var(project_root)
    if cypilot_rel:
        config_file = _resolve_config_path(project_root, cypilot_rel)
    else:
        config_file = project_root / _CONFIG_FILENAME
    if "version" not in ws_value:
        return None, f"Missing required field 'version' in [workspace] section of {config_file}"
    if "sources" not in ws_value:
        return None, f"Missing required field 'sources' in [workspace] section of {config_file}"
    try:
        ws = WorkspaceConfig.from_dict(
            ws_value,
            workspace_file=config_file,
            is_inline=True,
            resolution_base=project_root.resolve(),
        )
    except ValueError as e:
        return None, f"Invalid inline workspace in {config_file}: {e}"
    errs = ws.validate()
    if errs:
        return None, f"Invalid inline workspace in {config_file}: {'; '.join(errs)}"
    return ws, None
# @cpt-end:cpt-cypilot-algo-workspace-find-config:p1:inst-find-parse-inline-impl


# @cpt-algo:cpt-cypilot-algo-workspace-find-config:p1
# @cpt-dod:cpt-cypilot-dod-workspace-backward-compat:p1
def find_workspace_config(project_root: Path) -> Tuple[Optional[WorkspaceConfig], Optional[str]]:
    """Find and load workspace configuration.

    Discovery order:
    1. 'workspace' key in project config (core.toml via AGENTS.md):
       - If string: treat as path to external workspace file
       - If dict: treat as inline workspace definition
    2. Standalone .cypilot-workspace.toml at project_root

    Args:
        project_root: The project root directory.

    Returns:
        (WorkspaceConfig, None) if found, or (None, None) if no workspace,
        or (None, error_message) on parse failure.
    """
    from .files import load_project_config, _read_cypilot_var

    # @cpt-begin:cpt-cypilot-algo-workspace-find-config:p1:inst-find-load-project-config
    cfg = load_project_config(project_root)
    # @cpt-end:cpt-cypilot-algo-workspace-find-config:p1:inst-find-load-project-config
    # @cpt-begin:cpt-cypilot-algo-workspace-find-config:p1:inst-find-if-no-config
    if cfg is None:
        # Distinguish "no config file" from "parse error":
        # load_project_config returns None for both. Check if the file exists.
        cypilot_rel = _read_cypilot_var(project_root)
        if cypilot_rel:
            candidate = _resolve_config_path(project_root, cypilot_rel)
            if candidate.is_file():
                return None, f"Failed to parse config: {candidate}"
        return _find_standalone_workspace(project_root)
    # @cpt-end:cpt-cypilot-algo-workspace-find-config:p1:inst-find-if-no-config

    ws_value = cfg.get("workspace")
    # @cpt-begin:cpt-cypilot-algo-workspace-find-config:p1:inst-find-if-ws-string
    if isinstance(ws_value, str) and ws_value.strip():
        # @cpt-end:cpt-cypilot-algo-workspace-find-config:p1:inst-find-if-ws-string
        # @cpt-begin:cpt-cypilot-algo-workspace-find-config:p1:inst-find-load-standalone
        ws_path = (project_root / ws_value.strip()).resolve()
        # @cpt-end:cpt-cypilot-algo-workspace-find-config:p1:inst-find-load-standalone
        # @cpt-begin:cpt-cypilot-algo-workspace-find-config:p1:inst-find-return-standalone
        return WorkspaceConfig.load(ws_path)
        # @cpt-end:cpt-cypilot-algo-workspace-find-config:p1:inst-find-return-standalone
    # @cpt-begin:cpt-cypilot-algo-workspace-find-config:p1:inst-find-if-ws-dict
    if isinstance(ws_value, dict):
        # @cpt-end:cpt-cypilot-algo-workspace-find-config:p1:inst-find-if-ws-dict
        # @cpt-begin:cpt-cypilot-algo-workspace-find-config:p1:inst-find-parse-inline
        ws_cfg = _parse_inline_workspace(ws_value, project_root)
        # @cpt-end:cpt-cypilot-algo-workspace-find-config:p1:inst-find-parse-inline
        # @cpt-begin:cpt-cypilot-algo-workspace-find-config:p1:inst-find-return-inline
        return ws_cfg
        # @cpt-end:cpt-cypilot-algo-workspace-find-config:p1:inst-find-return-inline

    # @cpt-begin:cpt-cypilot-algo-workspace-find-config:p1:inst-find-return-none
    if ws_value is not None:
        return None, f"Malformed 'workspace' in core.toml: expected string path or table, got {type(ws_value).__name__}: {ws_value!r}"
    return _find_standalone_workspace(project_root)
    # @cpt-end:cpt-cypilot-algo-workspace-find-config:p1:inst-find-return-none


# @cpt-begin:cpt-cypilot-algo-workspace-find-config:p1:inst-find-standalone-impl
def _find_standalone_workspace(
    project_root: Path,
) -> Tuple[Optional[WorkspaceConfig], Optional[str]]:
    """Fallback: discover standalone .cypilot-workspace.toml at project root."""
    candidate = (project_root / WORKSPACE_CONFIG_FILENAME).resolve()
    if candidate.is_file():
        return WorkspaceConfig.load(candidate)
    return None, None
# @cpt-end:cpt-cypilot-algo-workspace-find-config:p1:inst-find-standalone-impl


# @cpt-begin:cpt-cypilot-state-workspace-config-lifecycle:p1:inst-config-load-inline-impl
def load_inline_config(project_root: Path) -> Tuple[Optional[Path], dict, Optional[str]]:
    """Resolve and load the inline config TOML for workspace operations.

    Returns:
        (config_path, existing_config, None) on success.
        (None, {}, error_message) on failure.
    """
    from .files import _read_cypilot_var

    cypilot_rel = _read_cypilot_var(project_root)
    if not cypilot_rel:
        return None, {}, "No cypilot_path found in AGENTS.md. Run 'cypilot init' first."

    config_path = _resolve_config_path(project_root, cypilot_rel)

    existing: dict = {}
    if config_path.is_file():
        try:
            existing = toml_utils.load(config_path)
            if not isinstance(existing, dict):
                return None, {}, f"Invalid config format in {config_path} (expected mapping)"
        except (ValueError, OSError) as e:
            return None, {}, f"Failed to parse {config_path}: {e}"

    return config_path, existing, None


def require_project_root() -> Optional[Path]:
    """Find project root from CWD or emit error. Returns Path or None."""
    from .files import find_project_root
    from .ui import ui
    project_root = find_project_root(Path.cwd())
    if project_root is None:
        ui.result({"status": "ERROR", "message": "No project root found"})
    return project_root


__all__ = [
    "VALID_ROLES",
    "validate_source_name",
    "SourceEntry",
    "TraceabilityConfig",
    "NamespaceRule",
    "ResolveConfig",
    "WorkspaceConfig",
    "find_workspace_config",
    "require_project_root",

    "load_inline_config",
]
# @cpt-end:cpt-cypilot-state-workspace-config-lifecycle:p1:inst-config-load-inline-impl
