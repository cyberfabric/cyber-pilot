"""
workspace-info: Display workspace configuration and per-source status.
"""
# @cpt-algo:cpt-cypilot-feature-workspace:p1
# @cpt-begin:cpt-cypilot-flow-workspace-info:p1:inst-info-helpers
import argparse
from pathlib import Path
from typing import List, Optional

from ..utils.git_utils import _redact_url
from ..utils.ui import ui
from ..utils.workspace import WorkspaceConfig


def _probe_source_adapter(resolved: Path, explicit_adapter: Optional[Path]) -> Optional[Path]:
    """Find the adapter directory for a reachable source.

    Prioritizes the explicit adapter path from workspace config over
    auto-discovery to avoid finding a wrong nested adapter.
    """
    if explicit_adapter is not None:
        if explicit_adapter.is_dir() and (explicit_adapter / "config").is_dir():
            return explicit_adapter
        return None  # explicit path declared but invalid

    from ..utils.files import find_cypilot_directory
    return find_cypilot_directory(resolved)


def _build_source_info(ws_cfg: WorkspaceConfig, name: str) -> dict:
    """Build status dict for a single workspace source."""
    src = ws_cfg.sources[name]
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
    if src.url is not None:
        info["url"] = _redact_url(src.url)
    if src.branch is not None:
        info["branch"] = src.branch

    if not reachable:
        if src.url:
            info["warning"] = (
                f"Source not cloned — run 'workspace-sync' to fetch: {_redact_url(src.url)}"
            )
        else:
            identifier = src.path or name
            info["warning"] = f"Source directory not reachable: {identifier}"
        return info

    explicit_adapter = (resolved / src.adapter).resolve() if src.adapter else None
    found_adapter = _probe_source_adapter(resolved, explicit_adapter)
    info["adapter_found"] = found_adapter is not None
    if found_adapter is not None:
        _enrich_with_artifact_counts(info, found_adapter)

    return info


def _enrich_with_artifact_counts(info: dict, adapter_dir: Path) -> None:
    """Add artifact/system counts to source info dict."""
    try:
        from ..utils.artifacts_meta import load_artifacts_meta

        meta, err = load_artifacts_meta(adapter_dir)
        if err:
            info["metadata_error"] = err
            return
        if meta:
            info["artifact_count"] = sum(1 for _ in meta.iter_all_artifacts())
            info["system_count"] = len(meta.systems)
    except (OSError, ValueError, RuntimeError) as exc:
        info["metadata_error"] = str(exc)
# @cpt-end:cpt-cypilot-flow-workspace-info:p1:inst-info-helpers


# @cpt-flow:cpt-cypilot-flow-workspace-info:p1
def cmd_workspace_info(argv: List[str]) -> int:
    """Display workspace config, list sources, show per-source status."""
    # @cpt-begin:cpt-cypilot-flow-workspace-info:p1:inst-user-workspace-info
    p = argparse.ArgumentParser(
        prog="workspace-info",
        description="Display workspace configuration and per-source status",
    )
    p.parse_args(argv)
    # @cpt-end:cpt-cypilot-flow-workspace-info:p1:inst-user-workspace-info

    from ..utils.context import get_context, WorkspaceContext
    from ..utils.workspace import find_workspace_config, require_project_root

    # @cpt-begin:cpt-cypilot-flow-workspace-info:p1:inst-info-find-root
    project_root = require_project_root()
    # @cpt-end:cpt-cypilot-flow-workspace-info:p1:inst-info-find-root
    # @cpt-begin:cpt-cypilot-flow-workspace-info:p1:inst-info-if-no-root
    if project_root is None:
        return 1
    # @cpt-end:cpt-cypilot-flow-workspace-info:p1:inst-info-if-no-root

    # @cpt-begin:cpt-cypilot-flow-workspace-info:p1:inst-info-find-ws
    ws_cfg, ws_err = find_workspace_config(project_root)
    # @cpt-end:cpt-cypilot-flow-workspace-info:p1:inst-info-find-ws
    if ws_cfg is None:
        # @cpt-begin:cpt-cypilot-flow-workspace-info:p1:inst-info-if-error
        if ws_err:
            ui.result({
                "status": "ERROR",
                "message": ws_err,
                "project_root": str(project_root),
            })
            return 1
        # @cpt-end:cpt-cypilot-flow-workspace-info:p1:inst-info-if-error
        # @cpt-begin:cpt-cypilot-flow-workspace-info:p1:inst-info-if-no-ws
        ui.result({
            "status": "ERROR",
            "message": "No workspace configuration found",
            "project_root": str(project_root),
            "hint": "Run 'workspace-init' to scan and create a workspace, add [workspace] to config/core.toml, set workspace = \"<path>\" in core.toml, or place .cypilot-workspace.toml at project root",
        })
        return 1
        # @cpt-end:cpt-cypilot-flow-workspace-info:p1:inst-info-if-no-ws

    # @cpt-begin:cpt-cypilot-flow-workspace-info:p1:inst-info-foreach-source
    sources_info = [_build_source_info(ws_cfg, name) for name in ws_cfg.sources]
    config_path = str(ws_cfg.workspace_file) if ws_cfg.workspace_file else None
    # @cpt-end:cpt-cypilot-flow-workspace-info:p1:inst-info-foreach-source

    # @cpt-begin:cpt-cypilot-flow-workspace-info:p1:inst-info-build-result
    result: dict = {
        "status": "OK",
        "version": ws_cfg.version,
        "config_path": config_path,
        "is_inline": ws_cfg.is_inline,
        "project_root": str(project_root),
        "sources_count": len(ws_cfg.sources),
        "sources": sources_info,
        "traceability": {
            "cross_repo": ws_cfg.traceability.cross_repo,
            "resolve_remote_ids": ws_cfg.traceability.resolve_remote_ids,
        },
    }

    config_errors = ws_cfg.validate()
    if config_errors:
        result["config_warnings"] = config_errors

    # @cpt-end:cpt-cypilot-flow-workspace-info:p1:inst-info-build-result

    # @cpt-begin:cpt-cypilot-flow-workspace-info:p1:inst-info-load-context
    ctx = get_context()
    if isinstance(ctx, WorkspaceContext):
        reachable_count = sum(1 for sc in ctx.sources.values() if sc.reachable)
        result["context_loaded"] = True
        result["reachable_sources"] = reachable_count
        result["total_registered_systems"] = len(ctx.get_all_registered_systems())
    else:
        result["context_loaded"] = False
    # @cpt-end:cpt-cypilot-flow-workspace-info:p1:inst-info-load-context

    # @cpt-begin:cpt-cypilot-flow-workspace-info:p1:inst-info-return-ok
    ui.result(result, human_fn=_human_workspace_info)
    return 0
    # @cpt-end:cpt-cypilot-flow-workspace-info:p1:inst-info-return-ok


# ---------------------------------------------------------------------------
# Human-friendly formatter
# ---------------------------------------------------------------------------
# @cpt-begin:cpt-cypilot-flow-workspace-info:p1:inst-info-human-fmt

def _fmt_source(src: dict) -> None:
    """Format a single source entry for human output."""
    name = src.get("name", "?")
    role = src.get("role", "full")
    reachable = src.get("reachable", False)
    marker = "OK" if reachable else "UNREACHABLE"
    ui.substep(f"  {name}  ({role})  [{marker}]")
    if src.get("url"):
        ui.substep(f"    url: {src['url']}")
    if src.get("path"):
        ui.substep(f"    path: {src['path']}")
    if src.get("adapter"):
        ui.substep(f"    adapter: {src['adapter']}")
    if src.get("artifact_count") is not None:
        ui.substep(f"    artifacts: {src['artifact_count']}  systems: {src.get('system_count', 0)}")
    if src.get("metadata_error"):
        ui.substep(f"    metadata_error: {src['metadata_error']}")
    if src.get("warning"):
        ui.substep(f"    warning: {src['warning']}")


def _fmt_traceability(traceability: dict) -> None:
    """Format the traceability section for human output."""
    cross = traceability.get("cross_repo", True)
    resolve = traceability.get("resolve_remote_ids", True)
    ui.detail("Cross-repo traceability", "on" if cross else "off")
    ui.detail("Resolve remote IDs", "on" if resolve else "off")


def _fmt_status(data: dict) -> None:
    """Format the final status/warnings block for human output."""
    warnings = data.get("config_warnings", [])
    if warnings:
        ui.blank()
        for w in warnings:
            ui.substep(f"  config warning: {w}")

    ui.blank()
    status = data.get("status", "")
    if status == "OK":
        ui.success("Workspace is configured")
    elif status == "ERROR":
        ui.error(data.get("message", ""))
    else:
        ui.info(f"Status: {status}")
    ui.blank()


def _human_workspace_info(data: dict) -> None:
    sources = data.get("sources", [])
    config_path = data.get("config_path", "")
    is_inline = data.get("is_inline", False)
    traceability = data.get("traceability", {})

    ui.header("Workspace Info")

    if config_path:
        ui.detail("Config", ui.relpath(config_path))
    ui.detail("Version", data.get("version", "?"))
    ui.detail("Type", "inline" if is_inline else "standalone")
    ui.detail("Sources", str(data.get("sources_count", len(sources))))

    if traceability:
        _fmt_traceability(traceability)

    if data.get("context_loaded"):
        ui.detail("Reachable sources", str(data.get("reachable_sources", 0)))
        ui.detail("Registered systems", str(data.get("total_registered_systems", 0)))

    if sources:
        ui.blank()
        for src in sources:
            _fmt_source(src)

    _fmt_status(data)
# @cpt-end:cpt-cypilot-flow-workspace-info:p1:inst-info-human-fmt
