"""
workspace-add: Add a source to workspace config (standalone or inline).
"""
# @cpt-algo:cpt-cypilot-feature-workspace:p1

import argparse
import re
from pathlib import Path
from typing import List

from ..utils.ui import ui
from ..utils.git_utils import _redact_url
from ..utils.workspace import WorkspaceConfig

# SCP-style SSH: git@host:org/repo or user@host:path
_SCP_SSH_RE = re.compile(r"^[A-Za-z0-9._-]+@[A-Za-z0-9._-]+:.+")


def _is_scp_style_ssh(url: str) -> bool:
    """Return True if *url* looks like an SCP-style SSH remote (git@host:path)."""
    return _SCP_SSH_RE.match(url) is not None


def _validate_add_args(args: argparse.Namespace) -> str | None:
    """Validate parsed workspace-add args. Return error message or None."""
    if args.inline and args.url:
        return "Git URL sources are not supported in inline workspace config. Remove --inline to add to a standalone workspace file."
    if args.branch and args.path:
        return "--branch is only valid with --url sources. Path sources do not use branch."
    if args.url:
        url = args.url
        if not (url.startswith("https://") or url.startswith("ssh://") or _is_scp_style_ssh(url)):
            return "Unsupported URL scheme — only HTTPS and SSH are allowed."
    return None


def _resolve_inline_workspace(existing: dict) -> tuple[dict, str | None]:
    """Validate and return the inline workspace dict from a parsed core.toml.

    Returns (workspace_dict, None) on success or ({}, error_message) on failure.
    """
    ws = existing.get("workspace")
    if isinstance(ws, str):
        return {}, "Workspace is defined as external file reference. Run without --inline to add to standalone file."
    if ws is not None and not isinstance(ws, dict):
        return {}, f"Malformed 'workspace' in config: expected table, got {type(ws).__name__}"
    if ws is None:
        ws = {"version": "1.0", "sources": {}}
    sources = ws.get("sources")
    if sources is not None and not isinstance(sources, dict):
        return {}, f"Malformed 'workspace.sources' in config: expected table, got {type(sources).__name__}"
    if sources is None:
        ws["sources"] = {}
    return ws, None


def _emit_add_result(args: argparse.Namespace, replaced: bool, config_path: str, message: str) -> int:
    """Build and emit the workspace-add result dict."""
    source_info: dict = {"name": args.name, "role": args.role}
    if args.path:
        source_info["path"] = args.path
    if args.adapter:
        source_info["adapter"] = args.adapter
    url = getattr(args, "url", None)
    if url:
        source_info["url"] = _redact_url(url)
    branch = getattr(args, "branch", None)
    if branch:
        source_info["branch"] = branch
    result: dict = {"status": "ADDED", "message": message, "config_path": config_path, "source": source_info}
    if replaced:
        result["replaced"] = True
    ui.result(result, human_fn=_human_workspace_add)
    return 0


def _add_to_standalone(args: argparse.Namespace, ws_cfg: WorkspaceConfig) -> int:
    """Add source to an existing standalone .cypilot-workspace.toml."""
    # @cpt-begin:cpt-cypilot-flow-workspace-add:p1:inst-add-check-collision
    replaced = args.name in ws_cfg.sources
    if replaced and not args.force:
        ui.result({"status": "ERROR", "message": f"Source '{args.name}' already exists. Use --force to replace."})
        return 1
    # @cpt-end:cpt-cypilot-flow-workspace-add:p1:inst-add-check-collision
    # @cpt-begin:cpt-cypilot-flow-workspace-add:p1:inst-add-source
    ws_cfg.add_source(args.name, args.path, role=args.role, adapter=args.adapter, url=args.url, branch=args.branch)
    # @cpt-end:cpt-cypilot-flow-workspace-add:p1:inst-add-source
    # @cpt-begin:cpt-cypilot-flow-workspace-add:p1:inst-add-save
    # @cpt-begin:cpt-cypilot-state-workspace-config-lifecycle:p1:inst-config-update-standalone
    save_err = ws_cfg.save()
    if save_err:
        ui.result({"status": "ERROR", "message": save_err})
        return 1
    # @cpt-end:cpt-cypilot-state-workspace-config-lifecycle:p1:inst-config-update-standalone
    # @cpt-end:cpt-cypilot-flow-workspace-add:p1:inst-add-save

    # @cpt-begin:cpt-cypilot-flow-workspace-add:p1:inst-add-return-ok
    verb = "updated in" if replaced else "added to"
    return _emit_add_result(args, replaced, str(ws_cfg.workspace_file), f"Source '{args.name}' {verb} workspace")
    # @cpt-end:cpt-cypilot-flow-workspace-add:p1:inst-add-return-ok


# @cpt-begin:cpt-cypilot-state-workspace-config-lifecycle:p1:inst-config-update-inline
def _add_to_inline(args: argparse.Namespace, project_root: Path) -> int:
    """Add source inline to the current repo's config/core.toml."""
    # @cpt-end:cpt-cypilot-state-workspace-config-lifecycle:p1:inst-config-update-inline
    # @cpt-begin:cpt-cypilot-flow-workspace-add:p1:inst-add-inline-impl
    if getattr(args, "url", None):
        ui.result({"status": "ERROR", "message": "Git URL sources are not supported in inline workspace config."})
        return 1

    from ..utils.workspace import load_inline_config
    from ..utils import toml_utils

    config_path, existing, err = load_inline_config(project_root)
    if err:
        ui.result({"status": "ERROR", "message": err})
        return 1

    # Get or create inline workspace
    ws, ws_err = _resolve_inline_workspace(existing)
    if ws_err:
        ui.result({"status": "ERROR", "message": ws_err})
        return 1

    branch = getattr(args, "branch", None)
    # @cpt-begin:cpt-cypilot-flow-workspace-add:p1:inst-add-check-collision
    replaced = args.name in ws["sources"]
    if replaced and not args.force:
        ui.result({"status": "ERROR", "message": f"Source '{args.name}' already exists. Use --force to replace."})
        return 1
    # @cpt-end:cpt-cypilot-flow-workspace-add:p1:inst-add-check-collision
    source_entry: dict = {"path": args.path}
    if args.role != "full":
        source_entry["role"] = args.role
    if args.adapter:
        source_entry["adapter"] = args.adapter
    if branch:
        source_entry["branch"] = branch

    ws["sources"][args.name] = source_entry
    existing["workspace"] = ws

    try:
        toml_utils.dump(existing, config_path)
    except OSError as e:
        ui.result({"status": "ERROR", "message": f"Failed to write to {config_path}: {e}"})
        return 1

    verb = "updated in" if replaced else "added inline to"
    return _emit_add_result(args, replaced, str(config_path), f"Source '{args.name}' {verb} core.toml")
    # @cpt-end:cpt-cypilot-flow-workspace-add:p1:inst-add-inline-impl


# @cpt-flow:cpt-cypilot-flow-workspace-add:p1
# @cpt-dod:cpt-cypilot-dod-workspace-source-mgmt:p1
def cmd_workspace_add(argv: List[str]) -> int:
    """Add a source to a workspace config (standalone or inline with --inline)."""
    # @cpt-begin:cpt-cypilot-flow-workspace-add:p1:inst-user-workspace-add
    p = argparse.ArgumentParser(
        prog="workspace-add",
        description="Add a source to a workspace config",
    )
    p.add_argument("--name", required=True, help="Source name (human-readable key)")
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--path", default="", help="Path to the source repo (relative to workspace file or project root)")
    source.add_argument("--url", default=None, help="Git remote URL (HTTPS or SSH) for the source")
    p.add_argument("--role", default="full", choices=["artifacts", "codebase", "kits", "full"], help="Source role")
    p.add_argument("--adapter", default=None, help="Path to cypilot dir within the source (e.g., cypilot, .bootstrap)")
    p.add_argument("--branch", default=None, help="Git branch/ref to checkout")
    p.add_argument("--inline", action="store_true", help="Add source inline to config/core.toml instead of standalone workspace file")
    p.add_argument("--force", action="store_true", help="Replace existing source with the same name instead of returning an error")
    args = p.parse_args(argv)

    arg_err = _validate_add_args(args)
    if arg_err:
        ui.result({"status": "ERROR", "message": arg_err})
        return 1

    from ..utils.workspace import validate_source_name
    name_err = validate_source_name(args.name)
    if name_err:
        ui.result({"status": "ERROR", "message": name_err})
        return 1
    # @cpt-end:cpt-cypilot-flow-workspace-add:p1:inst-user-workspace-add

    from ..utils.workspace import find_workspace_config, require_project_root

    # @cpt-begin:cpt-cypilot-flow-workspace-add:p1:inst-add-find-root
    project_root = require_project_root()
    # @cpt-end:cpt-cypilot-flow-workspace-add:p1:inst-add-find-root
    # @cpt-begin:cpt-cypilot-flow-workspace-add:p1:inst-add-if-no-root
    if project_root is None:
        return 1
    # @cpt-end:cpt-cypilot-flow-workspace-add:p1:inst-add-if-no-root

    # @cpt-begin:cpt-cypilot-flow-workspace-add:p1:inst-add-if-inline-flag
    if args.inline:
        # Check for existing standalone workspace — reject to prevent parallel configs
        existing, ws_err = find_workspace_config(project_root)
        if ws_err:
            ui.result({"status": "ERROR", "message": ws_err})
            return 1
        if existing is not None and not existing.is_inline:
            ui.result({"status": "ERROR", "message": (
                f"Standalone workspace already exists at {existing.workspace_file}. "
                "Remove --inline to add to the standalone file, or delete the standalone file first."
            )})
            return 1
        return _add_to_inline(args, project_root)
    # @cpt-end:cpt-cypilot-flow-workspace-add:p1:inst-add-if-inline-flag

    # Auto-detect workspace type
    # @cpt-begin:cpt-cypilot-flow-workspace-add:p1:inst-add-find-ws
    ws_cfg, ws_err = find_workspace_config(project_root)
    # @cpt-end:cpt-cypilot-flow-workspace-add:p1:inst-add-find-ws
    # @cpt-begin:cpt-cypilot-flow-workspace-add:p1:inst-add-if-no-ws
    if ws_cfg is None:
        msg = ws_err or "No workspace config found. Run 'workspace-init' first."
        ui.result({"status": "ERROR", "message": msg})
        return 1
    # @cpt-end:cpt-cypilot-flow-workspace-add:p1:inst-add-if-no-ws

    # @cpt-begin:cpt-cypilot-flow-workspace-add:p1:inst-add-auto-detect-inline
    if ws_cfg.is_inline:
        # Inline workspace detected — auto-route to inline add
        if args.url:
            ui.result({"status": "ERROR", "message": "Git URL sources are not supported in inline workspace config. Use a standalone workspace file instead."})
            return 1
        return _add_to_inline(args, project_root)
    # @cpt-end:cpt-cypilot-flow-workspace-add:p1:inst-add-auto-detect-inline

    return _add_to_standalone(args, ws_cfg)


# ---------------------------------------------------------------------------
# Human-friendly formatter
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-flow-workspace-add:p1:inst-add-human-fmt
def _human_workspace_add(data: dict) -> None:
    status = data.get("status", "")
    message = data.get("message", "")
    config_path = data.get("config_path", "")
    source = data.get("source", {})

    ui.header("Workspace Add")

    if config_path:
        ui.detail("Config", ui.relpath(config_path))

    if source:
        ui.detail("Source", source.get("name", ""))
        ui.detail("Path", source.get("path", "") or source.get("url", ""))
        ui.detail("Role", source.get("role", "full"))
        if source.get("adapter"):
            ui.detail("Adapter", source["adapter"])
        if source.get("branch"):
            ui.detail("Branch", source["branch"])

    if data.get("replaced"):
        ui.detail("Action", "replaced existing source")

    ui.blank()
    if status == "ADDED":
        ui.success(message)
    elif status == "ERROR":
        ui.error(message)
    else:
        ui.info(f"Status: {status}" + (f" — {message}" if message else ""))
    ui.blank()
# @cpt-end:cpt-cypilot-flow-workspace-add:p1:inst-add-human-fmt
