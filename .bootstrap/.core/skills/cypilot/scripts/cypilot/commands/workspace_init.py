"""
workspace-init: Initialize a new workspace by scanning nested sub-directories for repos with adapters.
"""
# @cpt-algo:cpt-cypilot-feature-workspace:p1
# @cpt-begin:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-helpers
import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..utils.ui import ui


def _is_project_dir(entry: Path) -> bool:
    """Check if a directory looks like a project (has .git or AGENTS.md with marker)."""
    if (entry / ".git").exists():
        return True
    agents_file = entry / "AGENTS.md"
    if not agents_file.is_file():
        return False
    try:
        head = agents_file.read_text(encoding="utf-8")[:512]
        return "<!-- @cpt:root-agents -->" in head
    except OSError:
        return False


def _find_adapter_path(entry: Path) -> Optional[str]:
    """Find the adapter path for a project directory."""
    from ..utils.files import find_cypilot_directory, _read_cypilot_var

    # v3 discovery: read cypilot_path variable from AGENTS.md
    cypilot_rel = _read_cypilot_var(entry)
    if cypilot_rel:
        candidate = (entry / cypilot_rel).resolve()
        if candidate.is_dir() and (candidate / "config").is_dir():
            return cypilot_rel

    # Fallback: try find_cypilot_directory for recursive search
    found_dir = find_cypilot_directory(entry)
    if found_dir is not None:
        try:
            return str(found_dir.relative_to(entry))
        except ValueError:
            return str(found_dir)
    return None


def _compute_source_path(entry: Path, output_dir: Path) -> str:
    """Compute relative source path from the output location."""
    try:
        return Path(os.path.relpath(entry, output_dir)).as_posix()
    except ValueError:
        # Windows: entry and output_dir are on different drives
        return entry.resolve().as_posix()
# @cpt-end:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-helpers


# @cpt-algo:cpt-cypilot-algo-workspace-infer-role:p1
def _infer_role(repo_path: Path) -> str:
    """Best-effort role inference from directory contents."""
    # @cpt-begin:cpt-cypilot-algo-workspace-infer-role:p1:inst-role-check-src
    has_src = any((repo_path / d).is_dir() for d in ["src", "lib", "app", "pkg"])
    # @cpt-end:cpt-cypilot-algo-workspace-infer-role:p1:inst-role-check-src
    # @cpt-begin:cpt-cypilot-algo-workspace-infer-role:p1:inst-role-check-docs
    has_docs = any((repo_path / d).is_dir() for d in ["docs", "architecture", "requirements"])
    # @cpt-end:cpt-cypilot-algo-workspace-infer-role:p1:inst-role-check-docs
    # @cpt-begin:cpt-cypilot-algo-workspace-infer-role:p1:inst-role-check-kits
    has_kits = (repo_path / "kits").is_dir()
    # @cpt-end:cpt-cypilot-algo-workspace-infer-role:p1:inst-role-check-kits

    # @cpt-begin:cpt-cypilot-algo-workspace-infer-role:p1:inst-role-if-multi
    capabilities = sum((has_src, has_docs, has_kits))
    if capabilities > 1:
        return "full"
    # @cpt-end:cpt-cypilot-algo-workspace-infer-role:p1:inst-role-if-multi
    # @cpt-begin:cpt-cypilot-algo-workspace-infer-role:p1:inst-role-if-kits
    if has_kits:
        return "kits"
    # @cpt-end:cpt-cypilot-algo-workspace-infer-role:p1:inst-role-if-kits
    # @cpt-begin:cpt-cypilot-algo-workspace-infer-role:p1:inst-role-if-artifacts
    if has_docs:
        return "artifacts"
    # @cpt-end:cpt-cypilot-algo-workspace-infer-role:p1:inst-role-if-artifacts
    # @cpt-begin:cpt-cypilot-algo-workspace-infer-role:p1:inst-role-if-codebase
    if has_src:
        return "codebase"
    # @cpt-end:cpt-cypilot-algo-workspace-infer-role:p1:inst-role-if-codebase
    # @cpt-begin:cpt-cypilot-algo-workspace-infer-role:p1:inst-role-return-full
    return "full"
    # @cpt-end:cpt-cypilot-algo-workspace-infer-role:p1:inst-role-return-full


def _sanitize_source_name(name: str) -> str:
    """Sanitize an auto-discovered source name to safe characters."""
    import re
    # Replace unsafe characters with hyphens
    sanitized = re.sub(r"[^A-Za-z0-9._-]", "-", name)
    # Strip leading non-alphanumeric characters
    sanitized = re.sub(r"^[^A-Za-z0-9]+", "", sanitized)
    # Collapse consecutive hyphens
    sanitized = re.sub(r"-{2,}", "-", sanitized)
    return sanitized or "source"


def _dedup_source_key(key: str, existing: Dict[str, dict], new_path: str) -> str:
    """Return a unique source key, warning on collision."""
    key = _sanitize_source_name(key)
    if key not in existing:
        return key
    n = 2
    while f"{key}-{n}" in existing:
        n += 1
    new_key = f"{key}-{n}"
    print(
        f"Warning: source name '{key}' collision — "
        f"'{new_path}' conflicts with '{existing[key].get('path', '?')}'; "
        f"renaming to '{new_key}'",
        file=sys.stderr,
    )
    return new_key


# @cpt-algo:cpt-cypilot-algo-workspace-discover-nested:p1
def _scan_nested_repos(
    scan_root: Path,
    output_dir: Path,
    max_depth: int = 3,
    _current_depth: int = 1,
) -> Dict[str, dict]:
    """Scan nested sub-directories for repos with adapters."""
    discovered: Dict[str, dict] = {}
    # @cpt-begin:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-check-depth
    if _current_depth > max_depth:
        return discovered
    # @cpt-end:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-check-depth
    # @cpt-begin:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-list-entries
    try:
        entries = sorted(scan_root.iterdir(), key=lambda p: p.name)
    except OSError as exc:
        print(f"Warning: cannot scan {scan_root}: {exc}", file=sys.stderr)
        entries = []
    # @cpt-end:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-list-entries

    # @cpt-begin:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-foreach-entry
    for entry in entries:
        if not entry.is_dir() or entry.name.startswith(".") or entry.is_symlink():
            continue
        # @cpt-end:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-foreach-entry
        # @cpt-begin:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-check-project
        if not _is_project_dir(entry):
            # @cpt-end:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-check-project
            # @cpt-begin:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-if-not-project
            # Not a project — recurse into subdirectory
            nested = _scan_nested_repos(entry, output_dir, max_depth, _current_depth + 1)
            for nkey, ninfo in nested.items():
                nkey = _dedup_source_key(nkey, discovered, ninfo.get("path", "?"))
                discovered[nkey] = ninfo
            continue
            # @cpt-end:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-if-not-project

        # @cpt-begin:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-find-adapter
        adapter_path = _find_adapter_path(entry)
        # @cpt-end:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-find-adapter
        # @cpt-begin:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-if-no-adapter
        if not adapter_path:
            continue
        # @cpt-end:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-if-no-adapter
        # @cpt-begin:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-compute-path
        info: dict = {"path": _compute_source_path(entry, output_dir), "adapter": adapter_path}
        # @cpt-end:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-compute-path
        # @cpt-begin:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-infer-role
        info["role"] = _infer_role(entry)
        # @cpt-end:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-infer-role
        # @cpt-begin:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-add-source
        key = _dedup_source_key(entry.name, discovered, info.get("path", "?"))
        discovered[key] = info
        # @cpt-end:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-add-source

    # @cpt-begin:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-return
    return discovered
    # @cpt-end:cpt-cypilot-algo-workspace-discover-nested:p1:inst-disc-return


# @cpt-begin:cpt-cypilot-state-workspace-config-lifecycle:p1:inst-config-create-inline
def _write_inline(
    project_root: Path,
    workspace_data: dict,
) -> Tuple[int, dict]:
    """Write workspace config inline into core.toml. Returns (exit_code, result_dict)."""
    # @cpt-end:cpt-cypilot-state-workspace-config-lifecycle:p1:inst-config-create-inline
    # @cpt-begin:cpt-cypilot-flow-workspace-init:p1:inst-write-inline-impl
    from ..utils.workspace import load_inline_config
    from ..utils import toml_utils

    config_path, existing, err = load_inline_config(project_root)
    if err:
        return 1, {"status": "ERROR", "message": err}

    existing["workspace"] = workspace_data
    try:
        toml_utils.dump(existing, config_path)
    except OSError as e:
        return 1, {"status": "ERROR", "message": f"Failed to write workspace to {config_path}: {e}"}

    return 0, {
        "status": "CREATED",
        "message": "Workspace added inline to core.toml",
        "config_path": str(config_path),
        "sources_count": len(workspace_data.get("sources", {})),
        "sources": list(workspace_data.get("sources", {}).keys()),
        "workspace": workspace_data,
    }
    # @cpt-end:cpt-cypilot-flow-workspace-init:p1:inst-write-inline-impl


# @cpt-begin:cpt-cypilot-state-workspace-config-lifecycle:p1:inst-config-create-standalone
def _write_standalone(
    output_path: Path,
    workspace_data: dict,
) -> Tuple[int, dict]:
    """Write standalone .cypilot-workspace.toml. Returns (exit_code, result_dict)."""
    # @cpt-end:cpt-cypilot-state-workspace-config-lifecycle:p1:inst-config-create-standalone
    # @cpt-begin:cpt-cypilot-flow-workspace-init:p1:inst-write-standalone-impl
    from ..constants import WORKSPACE_CONFIG_FILENAME
    from ..utils import toml_utils

    if output_path.is_dir():
        output_path = output_path / WORKSPACE_CONFIG_FILENAME

    try:
        toml_utils.dump(workspace_data, output_path)
    except OSError as e:
        return 1, {"status": "ERROR", "message": f"Failed to write workspace config to {output_path}: {e}"}

    return 0, {
        "status": "CREATED",
        "message": f"Workspace config created at {output_path}",
        "config_path": str(output_path),
        "sources_count": len(workspace_data.get("sources", {})),
        "sources": list(workspace_data.get("sources", {}).keys()),
        "workspace": workspace_data,
    }
    # @cpt-end:cpt-cypilot-flow-workspace-init:p1:inst-write-standalone-impl


# @cpt-begin:cpt-cypilot-flow-workspace-init:p1:inst-init-helpers
def _resolve_output_dir(args: argparse.Namespace, scan_root: Path, project_root: Path) -> Path:
    """Compute the output directory used for relative path computation."""
    if args.inline:
        return project_root
    if args.output:
        _out_resolved = Path(args.output).resolve()
        return _out_resolved if _out_resolved.is_dir() else _out_resolved.parent
    return scan_root


def _check_existing_workspace(project_root: Path, *, inline: bool, force: bool) -> Optional[str]:
    """Check for existing workspace config conflicts. Returns error message or None."""
    from ..utils.workspace import find_workspace_config as _find_ws

    existing_ws, ws_err = _find_ws(project_root)
    if existing_ws is None:
        if ws_err:
            return f"Existing workspace config is broken: {ws_err}. Fix or remove it before reinitializing."
        return None

    if inline and not existing_ws.is_inline:
        return (
            f"Standalone workspace already exists at {existing_ws.workspace_file}. "
            "Cannot create inline workspace — this would create parallel configs. "
            "Delete the standalone file first, then retry with --inline."
        )
    if not inline and existing_ws.is_inline:
        return (
            "Inline workspace already exists in core.toml. "
            "Cannot create standalone workspace — this would create parallel configs. "
            "Remove the [workspace] section from core.toml first, then retry."
        )
    if not force:
        config_loc = "core.toml" if existing_ws.is_inline else str(existing_ws.workspace_file)
        return (
            f"Workspace already exists ({config_loc}). "
            "Use --force to reinitialize (this will overwrite existing workspace config)."
        )
    return None
# @cpt-end:cpt-cypilot-flow-workspace-init:p1:inst-init-helpers


def _write_workspace_config(
    inline: bool,
    output_arg: Optional[str],
    project_root: Path,
    scan_root: Path,
    workspace_data: dict,
) -> tuple:
    """Execute workspace write (inline or standalone). Returns (exit_code, data)."""
    from ..constants import WORKSPACE_CONFIG_FILENAME

    # @cpt-begin:cpt-cypilot-flow-workspace-init:p1:inst-if-inline
    # @cpt-state:cpt-cypilot-state-workspace-config-lifecycle:p1
    # @cpt-begin:cpt-cypilot-state-workspace-config-lifecycle:p1:inst-config-reinit-inline
    if inline:
        return _write_inline(project_root, workspace_data)
    # @cpt-end:cpt-cypilot-state-workspace-config-lifecycle:p1:inst-config-reinit-inline
    # @cpt-end:cpt-cypilot-flow-workspace-init:p1:inst-if-inline
    # @cpt-begin:cpt-cypilot-flow-workspace-init:p1:inst-else-standalone
    # @cpt-begin:cpt-cypilot-state-workspace-config-lifecycle:p1:inst-config-reinit-standalone
    output_path = Path(output_arg).resolve() if output_arg else (scan_root / WORKSPACE_CONFIG_FILENAME)
    exit_code, data = _write_standalone(output_path, workspace_data)
    if output_arg and exit_code == 0:
        rel = output_path.relative_to(project_root) if output_path.is_relative_to(project_root) else output_path
        data["hint"] = (
            f"Custom output path used. Other commands will not discover this file automatically. "
            f'Add \'workspace = "{rel}"\' to config/core.toml to enable discovery.'
        )
    # @cpt-end:cpt-cypilot-state-workspace-config-lifecycle:p1:inst-config-reinit-standalone
    # @cpt-end:cpt-cypilot-flow-workspace-init:p1:inst-else-standalone
    return exit_code, data


# @cpt-flow:cpt-cypilot-flow-workspace-init:p1
# @cpt-dod:cpt-cypilot-dod-workspace-init:p1
def cmd_workspace_init(argv: List[str]) -> int:
    """Initialize a multi-repo workspace."""
    # @cpt-begin:cpt-cypilot-flow-workspace-init:p1:inst-user-workspace-init
    p = argparse.ArgumentParser(
        prog="workspace-init",
        description="Initialize a new workspace: scan nested sub-dirs for repos with adapters, generate .cypilot-workspace.toml",
    )
    p.add_argument(
        "--root", default=None,
        help="Directory to scan for nested repo sub-dirs (default: current project root)",
    )
    p.add_argument(
        "--output", default=None,
        help="Where to write .cypilot-workspace.toml (default: scan root)",
    )
    p.add_argument(
        "--inline", action="store_true",
        help="Write workspace config inline into current repo's config/core.toml instead of standalone file",
    )
    p.add_argument("--force", action="store_true", help="Force reinitialization when a workspace config already exists")
    def _positive_int(value: str) -> int:
        try:
            n = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"invalid integer value: {value!r}")
        if n < 1:
            raise argparse.ArgumentTypeError(f"must be >= 1, got {n}")
        return n
    p.add_argument("--max-depth", type=_positive_int, default=3, help="Maximum directory depth for nested repo scanning (default: 3, min: 1)")
    p.add_argument("--dry-run", action="store_true", help="Print what would be generated without writing files")
    args = p.parse_args(argv)

    if args.inline and args.output:
        ui.result({"status": "ERROR", "message": "--inline and --output are mutually exclusive. --inline always writes to config/core.toml."})
        return 1
    # @cpt-end:cpt-cypilot-flow-workspace-init:p1:inst-user-workspace-init

    from ..utils.workspace import require_project_root

    # @cpt-begin:cpt-cypilot-flow-workspace-init:p1:inst-find-project-root
    project_root = require_project_root()
    # @cpt-end:cpt-cypilot-flow-workspace-init:p1:inst-find-project-root
    # @cpt-begin:cpt-cypilot-flow-workspace-init:p1:inst-if-no-root
    if project_root is None:
        return 1
    # @cpt-end:cpt-cypilot-flow-workspace-init:p1:inst-if-no-root

    # @cpt-begin:cpt-cypilot-flow-workspace-init:p1:inst-determine-scan-root
    scan_root = Path(args.root).resolve() if args.root else project_root
    # @cpt-end:cpt-cypilot-flow-workspace-init:p1:inst-determine-scan-root
    # @cpt-begin:cpt-cypilot-flow-workspace-init:p1:inst-if-no-scan-root
    if not scan_root.is_dir():
        ui.result({"status": "ERROR", "message": f"Scan root directory not found: {scan_root}"})
        return 1
    # @cpt-end:cpt-cypilot-flow-workspace-init:p1:inst-if-no-scan-root

    # Determine output dir for relative path computation
    output_dir = _resolve_output_dir(args, scan_root, project_root)

    # @cpt-begin:cpt-cypilot-flow-workspace-init:p1:inst-discover-nested
    discovered = _scan_nested_repos(scan_root, output_dir, max_depth=args.max_depth)
    # @cpt-end:cpt-cypilot-flow-workspace-init:p1:inst-discover-nested

    # @cpt-begin:cpt-cypilot-flow-workspace-init:p1:inst-build-workspace-data
    workspace_data: dict = {"version": "1.0", "sources": discovered}
    # @cpt-end:cpt-cypilot-flow-workspace-init:p1:inst-build-workspace-data

    # @cpt-begin:cpt-cypilot-flow-workspace-init:p1:inst-if-dry-run
    if args.dry_run:
        ui.result({
            "status": "DRY_RUN",
            "message": "Would generate workspace config",
            "workspace": workspace_data,
            "sources_count": len(discovered),
            "sources": list(discovered.keys()),
        }, human_fn=_human_workspace_init)
        return 0
    # @cpt-end:cpt-cypilot-flow-workspace-init:p1:inst-if-dry-run

    # @cpt-begin:cpt-cypilot-flow-workspace-init:p1:inst-if-existing-ws
    # Check for existing workspace — prevent parallel configs and accidental overwrites
    conflict_err = _check_existing_workspace(project_root, inline=args.inline, force=args.force)
    if conflict_err:
        ui.result({"status": "ERROR", "message": conflict_err})
        return 1
    # @cpt-end:cpt-cypilot-flow-workspace-init:p1:inst-if-existing-ws

    exit_code, data = _write_workspace_config(
        args.inline, args.output, project_root, scan_root, workspace_data,
    )

    # @cpt-begin:cpt-cypilot-flow-workspace-init:p1:inst-return-init-ok
    ui.result(data, human_fn=_human_workspace_init)
    return exit_code
    # @cpt-end:cpt-cypilot-flow-workspace-init:p1:inst-return-init-ok


# ---------------------------------------------------------------------------
# Human-friendly formatter
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-flow-workspace-init:p1:inst-init-human-fmt
def _human_workspace_init(data: dict) -> None:
    status = data.get("status", "")
    message = data.get("message", "")
    sources = data.get("sources", [])
    n_sources = data.get("sources_count", len(sources))
    config_path = data.get("config_path", "")

    ui.header("Workspace Init")

    if status == "DRY_RUN":
        ui.detail("Mode", "dry-run (no files written)")
    if config_path:
        ui.detail("Config", ui.relpath(config_path))
    ui.detail("Sources", str(n_sources))

    if sources:
        ui.blank()
        ws_data = data.get("workspace", {})
        ws_sources = ws_data.get("sources", {}) if ws_data else {}
        for name in sources:
            src_info = ws_sources.get(name, {})
            role = src_info.get("role", "full")
            path = src_info.get("path", "")
            ui.substep(f"  {name}  ({role})  {path}")

    hint = data.get("hint")
    if hint:
        ui.blank()
        ui.info(hint)

    ui.blank()
    if status in ("CREATED", "DRY_RUN"):
        ui.success(message)
    elif status == "ERROR":
        ui.error(message)
    else:
        ui.info(f"Status: {status}" + (f" — {message}" if message else ""))
    ui.blank()
# @cpt-end:cpt-cypilot-flow-workspace-init:p1:inst-init-human-fmt
