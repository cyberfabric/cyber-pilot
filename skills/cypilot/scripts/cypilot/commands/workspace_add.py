"""
workspace-add / workspace-add-inline: Add a source to workspace config.
"""

import argparse
import json
from pathlib import Path
from typing import List


def cmd_workspace_add(argv: List[str]) -> int:
    """Add a source to an existing .cypilot-workspace.json."""
    p = argparse.ArgumentParser(
        prog="workspace-add",
        description="Add a source to an existing workspace config",
    )
    p.add_argument("--name", required=True, help="Source name (human-readable key)")
    p.add_argument("--path", required=True, help="Path to the source repo (relative to workspace file)")
    p.add_argument("--role", default="full", choices=["artifacts", "codebase", "kits", "full"], help="Source role")
    p.add_argument("--adapter", default=None, help="Path to adapter dir within the source (e.g., .cypilot-adapter)")
    args = p.parse_args(argv)

    from ..utils.workspace import find_workspace_config
    from ..utils.files import find_project_root

    project_root = find_project_root(Path.cwd())
    if project_root is None:
        print(json.dumps({"status": "ERROR", "message": "No project root found"}, indent=2, ensure_ascii=False))
        return 1

    ws_cfg, ws_err = find_workspace_config(project_root)
    if ws_cfg is None:
        msg = ws_err or "No workspace config found. Run 'workspace-init' first."
        print(json.dumps({"status": "ERROR", "message": msg}, indent=2, ensure_ascii=False))
        return 1

    if ws_cfg.is_inline:
        print(json.dumps({
            "status": "ERROR",
            "message": "Workspace is defined inline in .cypilot-config.json. Use 'workspace-add-inline' instead.",
        }, indent=2, ensure_ascii=False))
        return 1

    ws_cfg.add_source(args.name, args.path, role=args.role, adapter=args.adapter)
    save_err = ws_cfg.save()
    if save_err:
        print(json.dumps({"status": "ERROR", "message": save_err}, indent=2, ensure_ascii=False))
        return 1

    print(json.dumps({
        "status": "ADDED",
        "message": f"Source '{args.name}' added to workspace",
        "workspace_path": str(ws_cfg.workspace_file),
        "source": {
            "name": args.name,
            "path": args.path,
            "role": args.role,
            "adapter": args.adapter,
        },
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_workspace_add_inline(argv: List[str]) -> int:
    """Add a source inline to the current repo's .cypilot-config.json."""
    p = argparse.ArgumentParser(
        prog="workspace-add-inline",
        description="Add a source inline to the current repo's .cypilot-config.json",
    )
    p.add_argument("--name", required=True, help="Source name (human-readable key)")
    p.add_argument("--path", required=True, help="Path to the source repo (relative to project root)")
    p.add_argument("--role", default="full", choices=["artifacts", "codebase", "kits", "full"], help="Source role")
    p.add_argument("--adapter", default=None, help="Path to adapter dir within the source")
    args = p.parse_args(argv)

    from ..constants import PROJECT_CONFIG_FILENAME
    from ..utils.files import find_project_root

    project_root = find_project_root(Path.cwd())
    if project_root is None:
        print(json.dumps({"status": "ERROR", "message": "No project root found"}, indent=2, ensure_ascii=False))
        return 1

    config_path = project_root / PROJECT_CONFIG_FILENAME
    try:
        existing = json.loads(config_path.read_text(encoding="utf-8")) if config_path.is_file() else {}
        if not isinstance(existing, dict):
            existing = {}
    except Exception:
        existing = {}

    # Get or create inline workspace
    ws = existing.get("workspace")
    if isinstance(ws, str):
        print(json.dumps({
            "status": "ERROR",
            "message": "Workspace is defined as external file reference. Use 'workspace-add' instead.",
            "workspace_ref": ws,
        }, indent=2, ensure_ascii=False))
        return 1

    if not isinstance(ws, dict):
        ws = {"sources": {}}
    if not isinstance(ws.get("sources"), dict):
        ws["sources"] = {}

    source_entry: dict = {"path": args.path}
    if args.role != "full":
        source_entry["role"] = args.role
    if args.adapter:
        source_entry["adapter"] = args.adapter

    ws["sources"][args.name] = source_entry
    existing["workspace"] = ws

    config_path.write_text(
        json.dumps(existing, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "status": "ADDED",
        "message": f"Source '{args.name}' added inline to .cypilot-config.json",
        "config_path": str(config_path),
        "source": {
            "name": args.name,
            "path": args.path,
            "role": args.role,
            "adapter": args.adapter,
        },
    }, indent=2, ensure_ascii=False))
    return 0
