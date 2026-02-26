"""
Cypilot Workspace - Multi-repo federation support.

Loads and validates .cypilot-workspace.json (standalone or inline in .cypilot-config.json).
Each source maps a named repo to a local path, optional adapter location, and a role.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..constants import WORKSPACE_CONFIG_FILENAME

# Valid source roles
VALID_ROLES = {"artifacts", "codebase", "kits", "full"}


@dataclass
class SourceEntry:
    """A named source repo in the workspace."""

    name: str
    path: str  # Filesystem path (resolved relative to workspace file location)
    adapter: Optional[str] = None  # Path to adapter dir within the source, or None
    role: str = "full"  # "artifacts" | "codebase" | "kits" | "full"

    @classmethod
    def from_dict(cls, name: str, data: dict) -> "SourceEntry":
        raw_path = str((data or {}).get("path", "")).strip()
        raw_adapter = (data or {}).get("adapter", None)
        adapter = str(raw_adapter).strip() if isinstance(raw_adapter, str) else None
        # Explicit null in JSON means no adapter
        if raw_adapter is None and "adapter" in (data or {}):
            adapter = None
        raw_role = str((data or {}).get("role", "full")).strip().lower()
        role = raw_role if raw_role in VALID_ROLES else "full"
        return cls(name=name, path=raw_path, adapter=adapter, role=role)

    def to_dict(self) -> dict:
        d: dict = {"path": self.path}
        if self.adapter is not None:
            d["adapter"] = self.adapter
        if self.role != "full":
            d["role"] = self.role
        return d


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
class WorkspaceConfig:
    """Parsed workspace configuration."""

    version: str = "1.0"
    sources: Dict[str, SourceEntry] = field(default_factory=dict)
    traceability: TraceabilityConfig = field(default_factory=TraceabilityConfig)
    workspace_file: Optional[Path] = None  # Absolute path to the workspace file
    is_inline: bool = False  # True if loaded from .cypilot-config.json inline workspace

    @classmethod
    def from_dict(cls, data: dict, *, workspace_file: Optional[Path] = None, is_inline: bool = False) -> "WorkspaceConfig":
        version = str((data or {}).get("version", "1.0")).strip()
        sources: Dict[str, SourceEntry] = {}
        raw_sources = (data or {}).get("sources", {})
        if isinstance(raw_sources, dict):
            for name, src_data in raw_sources.items():
                if isinstance(name, str) and name.strip() and isinstance(src_data, dict):
                    sources[name.strip()] = SourceEntry.from_dict(name.strip(), src_data)

        traceability = TraceabilityConfig()
        raw_trace = (data or {}).get("traceability", None)
        if isinstance(raw_trace, dict):
            traceability = TraceabilityConfig.from_dict(raw_trace)

        return cls(
            version=version,
            sources=sources,
            traceability=traceability,
            workspace_file=workspace_file,
            is_inline=is_inline,
        )

    def to_dict(self) -> dict:
        d: dict = {"version": self.version}
        if self.sources:
            d["sources"] = {name: src.to_dict() for name, src in self.sources.items()}
        trace = self.traceability.to_dict()
        if trace != TraceabilityConfig().to_dict():
            d["traceability"] = trace
        return d

    @classmethod
    def load(cls, workspace_path: Path) -> Tuple[Optional["WorkspaceConfig"], Optional[str]]:
        """Load workspace config from a JSON file.

        Args:
            workspace_path: Absolute path to .cypilot-workspace.json

        Returns:
            (WorkspaceConfig, None) on success or (None, error_message) on failure.
        """
        if not workspace_path.is_file():
            return None, f"Workspace file not found: {workspace_path}"
        try:
            raw = workspace_path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except Exception as e:
            return None, f"Failed to read workspace file {workspace_path}: {e}"
        if not isinstance(data, dict):
            return None, f"Invalid workspace file (expected JSON object): {workspace_path}"
        cfg = cls.from_dict(data, workspace_file=workspace_path.resolve(), is_inline=False)
        return cfg, None

    def resolve_source_path(self, source_name: str) -> Optional[Path]:
        """Resolve the absolute filesystem path for a named source.

        Paths are resolved relative to the workspace file location.
        """
        src = self.sources.get(source_name)
        if src is None:
            return None
        base = self.workspace_file.parent if self.workspace_file else Path.cwd()
        return (base / src.path).resolve()

    def resolve_source_adapter(self, source_name: str) -> Optional[Path]:
        """Resolve the absolute path to a source's adapter directory."""
        src = self.sources.get(source_name)
        if src is None or src.adapter is None:
            return None
        source_root = self.resolve_source_path(source_name)
        if source_root is None:
            return None
        return (source_root / src.adapter).resolve()

    def get_reachable_sources(self) -> Dict[str, Path]:
        """Return dict of source_name -> resolved_path for sources whose path exists."""
        result: Dict[str, Path] = {}
        for name in self.sources:
            resolved = self.resolve_source_path(name)
            if resolved and resolved.is_dir():
                result[name] = resolved
        return result

    def validate(self) -> List[str]:
        """Validate workspace config and return list of error messages."""
        errors: List[str] = []
        if not self.sources:
            errors.append("Workspace has no sources defined")
        for name, src in self.sources.items():
            if not src.path:
                errors.append(f"Source '{name}' has empty path")
            if src.role not in VALID_ROLES:
                errors.append(f"Source '{name}' has invalid role '{src.role}' (valid: {', '.join(sorted(VALID_ROLES))})")
        return errors

    def add_source(self, name: str, path: str, role: str = "full", adapter: Optional[str] = None) -> None:
        """Add or update a source entry."""
        self.sources[name] = SourceEntry(name=name, path=path, adapter=adapter, role=role)

    def save(self, target_path: Optional[Path] = None) -> Optional[str]:
        """Save workspace config to file.

        Args:
            target_path: Path to save to (defaults to self.workspace_file).

        Returns:
            None on success, error message on failure.
        """
        path = target_path or self.workspace_file
        if path is None:
            return "No target path specified for saving workspace config"
        try:
            content = json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n"
            path.write_text(content, encoding="utf-8")
            self.workspace_file = path.resolve()
            return None
        except Exception as e:
            return f"Failed to save workspace config to {path}: {e}"


def find_workspace_config(project_root: Path) -> Tuple[Optional[WorkspaceConfig], Optional[str]]:
    """Find and load workspace configuration.

    Discovery order:
    1. Check 'workspace' key in .cypilot-config.json at project_root
       - If string: treat as path to external workspace file
       - If dict: treat as inline workspace definition
    2. Walk up from project_root looking for .cypilot-workspace.json
    3. Check parent directory of project_root for .cypilot-workspace.json

    Args:
        project_root: The project root directory.

    Returns:
        (WorkspaceConfig, None) if found, or (None, None) if no workspace,
        or (None, error_message) on parse failure.
    """
    from .files import load_project_config

    # Step 1: Check .cypilot-config.json for workspace key
    cfg = load_project_config(project_root)
    if cfg is not None:
        ws_value = cfg.get("workspace")
        if isinstance(ws_value, str) and ws_value.strip():
            # External workspace file reference
            ws_path = (project_root / ws_value.strip()).resolve()
            return WorkspaceConfig.load(ws_path)
        elif isinstance(ws_value, dict):
            # Inline workspace definition
            ws = WorkspaceConfig.from_dict(
                ws_value,
                workspace_file=(project_root / ".cypilot-config.json").resolve(),
                is_inline=True,
            )
            return ws, None

    # Step 2: Walk up looking for .cypilot-workspace.json
    current = project_root.resolve()
    for _ in range(10):
        ws_path = current / WORKSPACE_CONFIG_FILENAME
        if ws_path.is_file():
            return WorkspaceConfig.load(ws_path)
        parent = current.parent
        if parent == current:
            break
        current = parent

    # Step 3: Check parent directory of project_root
    parent_ws = project_root.resolve().parent / WORKSPACE_CONFIG_FILENAME
    if parent_ws.is_file():
        return WorkspaceConfig.load(parent_ws)

    # No workspace found — not an error, just means single-repo mode
    return None, None


__all__ = [
    "SourceEntry",
    "TraceabilityConfig",
    "WorkspaceConfig",
    "find_workspace_config",
    "VALID_ROLES",
]
