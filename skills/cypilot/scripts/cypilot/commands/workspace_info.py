"""
workspace-info: Display workspace configuration and per-source status.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List


def cmd_workspace_info(argv: List[str]) -> int:
    """Display workspace config, list sources, show per-source status."""
    p = argparse.ArgumentParser(
        prog="workspace-info",
        description="Display workspace configuration and per-source status",
    )
    p.parse_args(argv)

    from ..utils.context import get_context, is_workspace, WorkspaceContext
    from ..utils.files import find_project_root
    from ..utils.workspace import find_workspace_config

    project_root = find_project_root(Path.cwd())
    if project_root is None:
        print(json.dumps({
            "status": "ERROR",
            "message": "No project root found",
        }, indent=2, ensure_ascii=False))
        return 1

    ws_cfg, ws_err = find_workspace_config(project_root)
    if ws_cfg is None:
        msg = ws_err or "No workspace configuration found"
        print(json.dumps({
            "status": "NO_WORKSPACE",
            "message": msg,
            "project_root": str(project_root),
            "hint": "Run 'workspace-init' to create a workspace, or add 'workspace' key to .cypilot-config.json",
        }, indent=2, ensure_ascii=False))
        return 0

    # Build source status list
    sources_info: List[dict] = []
    for name, src in ws_cfg.sources.items():
        resolved = ws_cfg.resolve_source_path(name)
        reachable = resolved is not None and resolved.is_dir()

        info: dict = {
            "name": name,
            "path": src.path,
            "resolved_path": str(resolved) if resolved else None,
            "role": src.role,
            "adapter": src.adapter,
            "reachable": reachable,
        }

        if reachable and resolved:
            # Check adapter
            if src.adapter:
                adapter_path = (resolved / src.adapter).resolve()
                info["adapter_found"] = adapter_path.is_dir() and (adapter_path / "AGENTS.md").exists()
                if info["adapter_found"]:
                    # Count artifacts
                    try:
                        from ..utils.artifacts_meta import load_artifacts_meta
                        meta, err = load_artifacts_meta(adapter_path)
                        if meta and not err:
                            art_count = sum(1 for _ in meta.iter_all_artifacts())
                            sys_count = len(meta.systems)
                            info["artifact_count"] = art_count
                            info["system_count"] = sys_count
                    except Exception:
                        pass
            else:
                info["adapter_found"] = None
        elif not reachable:
            info["warning"] = f"Source directory not reachable: {src.path}"

        sources_info.append(info)

    workspace_location = "inline (.cypilot-config.json)" if ws_cfg.is_inline else str(ws_cfg.workspace_file)

    result: dict = {
        "status": "WORKSPACE_FOUND",
        "version": ws_cfg.version,
        "workspace_location": workspace_location,
        "is_inline": ws_cfg.is_inline,
        "project_root": str(project_root),
        "sources_count": len(ws_cfg.sources),
        "sources": sources_info,
        "traceability": {
            "cross_repo": ws_cfg.traceability.cross_repo,
            "resolve_remote_ids": ws_cfg.traceability.resolve_remote_ids,
        },
    }

    # Check global context for workspace-level info
    ctx = get_context()
    if isinstance(ctx, WorkspaceContext):
        reachable_count = sum(1 for sc in ctx.sources.values() if sc.reachable)
        result["context_loaded"] = True
        result["reachable_sources"] = reachable_count
        result["total_registered_systems"] = len(ctx.get_all_registered_systems())
    else:
        result["context_loaded"] = False

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0
