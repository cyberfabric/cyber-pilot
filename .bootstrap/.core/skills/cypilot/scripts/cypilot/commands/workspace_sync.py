"""
workspace-sync: Fetch and update worktrees for Git URL workspace sources.
"""
# @cpt-algo:cpt-cypilot-feature-workspace:p1
# @cpt-flow:cpt-cypilot-flow-workspace-sync:p1
# @cpt-dod:cpt-cypilot-dod-workspace-sync:p1
import argparse
from pathlib import Path
from typing import List

from ..utils.git_utils import _redact_url
from ..utils.ui import ui


def _resolve_sync_base(ws_cfg, project_root: Path) -> Path:
    """Determine the resolution base directory for workspace sync."""
    if ws_cfg.resolution_base is not None:
        return ws_cfg.resolution_base
    if ws_cfg.workspace_file is not None:
        return ws_cfg.workspace_file.parent
    return project_root


def _collect_git_sources(ws_cfg, source_name):
    """Filter workspace sources to only Git URL sources. Returns (git_sources, error_data) or (git_sources, None)."""
    # @cpt-begin:cpt-cypilot-flow-workspace-sync:p1:inst-sync-if-source-not-found
    if source_name is not None:
        src_entry = ws_cfg.sources.get(source_name)
        if src_entry is None:
            return None, {
                "status": "ERROR",
                "message": f"Source '{source_name}' not found",
                "available": list(ws_cfg.sources.keys()),
            }
        # @cpt-end:cpt-cypilot-flow-workspace-sync:p1:inst-sync-if-source-not-found
        # @cpt-begin:cpt-cypilot-flow-workspace-sync:p1:inst-sync-if-no-url
        if not src_entry.url:
            return None, {
                "status": "ERROR",
                "message": f"Source '{source_name}' has no Git URL — only Git URL sources can be synced",
            }
        # @cpt-end:cpt-cypilot-flow-workspace-sync:p1:inst-sync-if-no-url
        return {source_name: src_entry}, None
    return {name: src for name, src in ws_cfg.sources.items() if src.url}, None


def _sync_sources(git_sources, resolve_cfg, base, *, force=False):
    """Run sync for each git source. Returns (results, synced, failed)."""
    from ..utils.git_utils import sync_git_source

    results = []
    synced = 0
    failed = 0
    for name, src in git_sources.items():
        result = sync_git_source(src, resolve_cfg, base, force=force)
        result["name"] = name
        results.append(result)
        if result["status"] == "synced":
            synced += 1
        else:
            failed += 1
    return results, synced, failed


def cmd_workspace_sync(argv: List[str]) -> int:
    """Sync Git URL workspace sources: fetch + update worktrees."""
    # @cpt-begin:cpt-cypilot-flow-workspace-sync:p1:inst-user-workspace-sync
    p = argparse.ArgumentParser(
        prog="workspace-sync",
        description="Fetch and update worktrees for Git URL workspace sources",
    )
    p.add_argument(
        "--source", default=None,
        help="Sync only the named source (default: all Git URL sources)",
    )
    p.add_argument("--dry-run", action="store_true", help="Show which sources would be synced without network operations")
    p.add_argument("--force", action="store_true", help="Skip dirty worktree check — WARNING: uncommitted changes will be discarded via git reset --hard")
    args = p.parse_args(argv)
    # @cpt-end:cpt-cypilot-flow-workspace-sync:p1:inst-user-workspace-sync

    from ..utils.workspace import find_workspace_config, ResolveConfig, require_project_root

    # @cpt-begin:cpt-cypilot-flow-workspace-sync:p1:inst-sync-find-root
    project_root = require_project_root()
    # @cpt-end:cpt-cypilot-flow-workspace-sync:p1:inst-sync-find-root
    # @cpt-begin:cpt-cypilot-flow-workspace-sync:p1:inst-sync-if-no-root
    if project_root is None:
        return 1
    # @cpt-end:cpt-cypilot-flow-workspace-sync:p1:inst-sync-if-no-root

    # @cpt-begin:cpt-cypilot-flow-workspace-sync:p1:inst-sync-find-ws
    ws_cfg, ws_err = find_workspace_config(project_root)
    # @cpt-end:cpt-cypilot-flow-workspace-sync:p1:inst-sync-find-ws
    # @cpt-begin:cpt-cypilot-flow-workspace-sync:p1:inst-sync-if-no-ws
    if ws_cfg is None:
        msg = ws_err or "No workspace configuration found. Run 'workspace-init' first."
        ui.result({"status": "ERROR", "message": msg})
        return 1
    # @cpt-end:cpt-cypilot-flow-workspace-sync:p1:inst-sync-if-no-ws

    # @cpt-begin:cpt-cypilot-flow-workspace-sync:p1:inst-sync-collect-sources
    git_sources, src_err = _collect_git_sources(ws_cfg, args.source)
    if src_err is not None:
        ui.result(src_err)
        return 1
    # @cpt-end:cpt-cypilot-flow-workspace-sync:p1:inst-sync-collect-sources

    # @cpt-begin:cpt-cypilot-flow-workspace-sync:p1:inst-sync-if-no-git-sources
    if not git_sources:
        ui.result({
            "status": "OK",
            "message": "No Git URL sources to sync",
            "synced": 0,
            "failed": 0,
            "results": [],
        }, human_fn=_human_workspace_sync)
        return 0
    # @cpt-end:cpt-cypilot-flow-workspace-sync:p1:inst-sync-if-no-git-sources

    # @cpt-begin:cpt-cypilot-flow-workspace-sync:p1:inst-sync-if-dry-run
    if args.dry_run:
        ui.result({
            "status": "DRY_RUN",
            "message": "Would sync the following Git URL sources",
            "sources": [{"name": n, "url": _redact_url(s.url), "branch": s.branch} for n, s in git_sources.items()],
        }, human_fn=_human_workspace_sync)
        return 0
    # @cpt-end:cpt-cypilot-flow-workspace-sync:p1:inst-sync-if-dry-run

    # @cpt-begin:cpt-cypilot-flow-workspace-sync:p1:inst-sync-foreach-source
    resolve_cfg = ws_cfg.resolve or ResolveConfig()
    base = _resolve_sync_base(ws_cfg, project_root)
    results, synced, failed = _sync_sources(git_sources, resolve_cfg, base, force=args.force)
    # @cpt-end:cpt-cypilot-flow-workspace-sync:p1:inst-sync-foreach-source

    # @cpt-begin:cpt-cypilot-flow-workspace-sync:p1:inst-sync-return-ok
    status = "OK" if synced > 0 else "FAIL"
    ui.result({
        "status": status,
        "synced": synced,
        "failed": failed,
        "results": results,
    }, human_fn=_human_workspace_sync)
    return 0 if synced > 0 or failed == 0 else 2
    # @cpt-end:cpt-cypilot-flow-workspace-sync:p1:inst-sync-return-ok


# ---------------------------------------------------------------------------
# Human-friendly formatter
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-flow-workspace-sync:p1:inst-sync-human-fmt
def _human_workspace_sync(data: dict) -> None:
    status = data.get("status", "")
    message = data.get("message", "")

    ui.header("Workspace Sync")

    if status == "DRY_RUN":
        ui.detail("Mode", "dry-run (no network operations)")
        sources = data.get("sources", [])
        ui.detail("Sources to sync", str(len(sources)))
        ui.blank()
        for src in sources:
            branch = src.get("branch") or "HEAD"
            ui.substep(f"  {src['name']}  ({src.get('url', '?')})  [{branch}]")
        ui.blank()
        ui.success(message)
        ui.blank()
        return

    results = data.get("results", [])
    synced = data.get("synced", 0)
    failed = data.get("failed", 0)

    if not results and message:
        ui.info(message)
        ui.blank()
        return

    ui.detail("Synced", str(synced))
    ui.detail("Failed", str(failed))
    ui.blank()

    for r in results:
        name = r.get("name", "?")
        s = r.get("status", "?")
        if s == "synced":
            ui.substep(f"  {name}  [SYNCED]")
        else:
            err = r.get("error", "unknown error")
            ui.substep(f"  {name}  [FAILED] {err}")

    ui.blank()
    if status == "OK":
        ui.success("Sync complete")
    elif status == "FAIL":
        ui.error("All sources failed to sync")
    ui.blank()
# @cpt-end:cpt-cypilot-flow-workspace-sync:p1:inst-sync-human-fmt
