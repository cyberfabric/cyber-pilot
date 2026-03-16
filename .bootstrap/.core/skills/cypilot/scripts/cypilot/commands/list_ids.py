# @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-imports
import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ..utils.codebase import CodeFile
from ..utils.document import scan_cpt_ids
from ..utils.ui import ui
# @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-imports

# @cpt-flow:cpt-cypilot-flow-traceability-validation-query:p1
def cmd_list_ids(argv: List[str]) -> int:
    """List Cypilot IDs from artifacts.

    If no artifact is specified, scans all Cypilot-format artifacts from the adapter registry.
    """
    # @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-user-query
    p = argparse.ArgumentParser(prog="list-ids")
    p.add_argument("--artifact", default=None, help="Path to Cypilot artifact file (if omitted, scans all registered Cypilot artifacts)")
    p.add_argument("--pattern", default=None, help="Filter IDs by substring or regex pattern")
    p.add_argument("--regex", action="store_true", help="Treat pattern as regular expression")
    p.add_argument("--kind", default=None, help="Filter by inferred ID kind")
    p.add_argument("--all", action="store_true", help="Include duplicate IDs in results")
    p.add_argument("--include-code", action="store_true", help="Also scan code files for Cypilot marker references")
    p.add_argument("--source", default=None, help="Filter by workspace source name (workspace mode only)")
    args = p.parse_args(argv)
    # @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-user-query

    # @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-load-context
    # Collect artifacts to scan: (artifact_path, artifact_kind)
    artifacts_to_scan: List[Tuple[Path, str]] = []
    ctx = None

    if args.artifact:
        # Single artifact specified - find context from artifact's location
        artifact_path = Path(args.artifact).resolve()
        if not artifact_path.exists():
            ui.result({"status": "ERROR", "message": f"Artifact not found: {artifact_path}"})
            return 1

        from ..utils.context import CypilotContext

        ctx = CypilotContext.load(artifact_path.parent)
        if not ctx:
            ui.result({"status": "ERROR", "message": "Cypilot not initialized. Run 'cypilot init' first or specify --artifact."})
            return 1

        project_root = ctx.project_root
        meta = ctx.meta

        # Find artifact in registry
        try:
            rel_path = artifact_path.relative_to(project_root).as_posix()
        except ValueError:
            rel_path = None

        if rel_path:
            result = meta.get_artifact_by_path(rel_path)
            if result:
                artifact_meta, _system_node = result
                artifacts_to_scan.append((artifact_path, str(artifact_meta.kind)))

        if not artifacts_to_scan:
            ui.result({"status": "ERROR", "message": "Artifact not registered in Cypilot registry."})
            return 1
    else:
        # No artifact specified - use global context from cwd
        from ..utils.context import get_context, collect_artifacts_to_scan, WorkspaceContext

        ctx = get_context()
        if not ctx:
            ui.result({"status": "ERROR", "message": "Cypilot not initialized. Run 'cypilot init' first or specify --artifact."})
            return 1

        meta = ctx.meta
        project_root = ctx.project_root
        is_workspace = isinstance(ctx, WorkspaceContext)

        if args.source and not is_workspace:
            ui.result({"status": "ERROR", "message": "--source requires a workspace context"})
            return 1

        if not args.source:
            # No source filter — use shared collection helper
            artifacts_to_scan, _ = collect_artifacts_to_scan(ctx)
        else:
            # --source filter: skip primary, scan only matching remote source
            if is_workspace:
                from ..utils.context import get_expanded_meta as _get_expanded_meta
                for sc in ctx.sources.values():
                    if not sc.reachable or sc.meta is None:
                        continue
                    if sc.name != args.source:
                        continue
                    _meta = _get_expanded_meta(sc)
                    if _meta is None:
                        continue
                    for art, _sys in _meta.iter_all_artifacts():
                        art_path = (sc.path / art.path).resolve()
                        if art_path.exists():
                            artifacts_to_scan.append((art_path, str(art.kind)))

        if not artifacts_to_scan:
            ui.result({"count": 0, "artifacts_scanned": 0, "ids": []})
            return 0
    # @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-load-context

    # @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-scan-all
    # Parse artifacts and collect IDs
    hits: List[Dict[str, object]] = []

    from ..utils.context import WorkspaceContext as _WsCtx
    if ctx and isinstance(ctx, _WsCtx):
        registered_systems = set(ctx.get_all_registered_systems())
    else:
        registered_systems = set((ctx.registered_systems or set()) if ctx else set())
    known_kinds = set((ctx.get_known_id_kinds() if ctx else set()) or set())

    def _match_system_prefix(cpt_id: str) -> Optional[str]:
        best: Optional[str] = None
        for sys_slug in registered_systems:
            prefix = f"cpt-{sys_slug}-"
            if cpt_id.lower().startswith(prefix.lower()):
                if best is None or len(sys_slug) > len(best):
                    best = sys_slug
        return best

    def _infer_kind(cpt_id: str) -> Optional[str]:
        sys_slug = _match_system_prefix(cpt_id)
        if not sys_slug:
            return None
        remainder = cpt_id[len(f"cpt-{sys_slug}-"):]
        if not remainder:
            return None
        parts = [p for p in remainder.split("-") if p]
        if not parts:
            return None
        # Prefer latest known kind token in composite IDs
        best = None
        for part in parts:
            k = part.lower()
            if known_kinds and k not in known_kinds:
                continue
            best = k
        return best

    for artifact_path, artifact_type in artifacts_to_scan:
        for fh in scan_cpt_ids(artifact_path):
            cid = str(fh.get("id") or "").strip()
            if not cid:
                continue
            h: Dict[str, object] = {
                "id": cid,
                "kind": _infer_kind(cid),
                "type": fh.get("type"),
                "artifact_type": artifact_type,
                "line": fh.get("line"),
                "artifact": str(artifact_path),
                "checked": bool(fh.get("checked", False)),
            }
            if fh.get("priority") is not None:
                h["priority"] = fh.get("priority")
            hits.append(h)
    # @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-scan-all

    # @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-if-list-code
    # Scan code files if requested
    code_files_scanned = 0
    if args.include_code and not args.artifact and ctx:
        # Scan codebase entries from context
        for cb_entry, _system_node in ctx.meta.iter_all_codebase():
            code_path = (ctx.project_root / cb_entry.path).resolve()
            extensions = cb_entry.extensions or [".py"]

            if not code_path.exists():
                continue

            if code_path.is_file():
                files = [code_path]
            else:
                files = []
                for ext in extensions:
                    files.extend(code_path.rglob(f"*{ext}"))

            for file_path in files:
                # Apply registry root ignore rules as a hard visibility filter.
                try:
                    rel = file_path.resolve().relative_to(ctx.project_root).as_posix()
                except Exception:
                    rel = None
                if rel and ctx.meta.is_ignored(rel):
                    continue

                cf, errs = CodeFile.from_path(file_path)
                if errs or cf is None:
                    continue

                code_files_scanned += 1

                # Add code references
                for ref in cf.references:
                    h: Dict[str, object] = {
                        "id": ref.id,
                        "kind": ref.kind or "code",
                        "type": "code_reference",
                        "artifact_type": "CODE",
                        "line": ref.line,
                        "artifact": str(file_path),
                        "marker_type": ref.marker_type,
                    }
                    if ref.phase is not None:
                        h["phase"] = ref.phase
                    if ref.inst:
                        h["inst"] = ref.inst
                    hits.append(h)
    # @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-if-list-code

    # @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-if-list
    # Apply filters
    if args.kind:
        kind_filter = str(args.kind)
        hits = [h for h in hits if str(h.get("kind", "")) == kind_filter]

    if args.pattern:
        pat = str(args.pattern)
        if args.regex:
            rx = re.compile(pat)
            hits = [h for h in hits if rx.search(str(h.get("id", ""))) is not None]
        else:
            hits = [h for h in hits if pat in str(h.get("id", ""))]

    if not args.all:
        seen: Set[str] = set()
        uniq: List[Dict[str, object]] = []
        for h in hits:
            id_val = str(h.get("id", ""))
            if id_val in seen:
                continue
            seen.add(id_val)
            uniq.append(h)
        hits = uniq

    hits = sorted(hits, key=lambda h: (str(h.get("id", "")), int(h.get("line", 0))))

    result: Dict[str, object] = {
        "count": len(hits),
        "artifacts_scanned": len(artifacts_to_scan),
        "ids": hits,
    }
    if code_files_scanned > 0:
        result["code_files_scanned"] = code_files_scanned

    # @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-if-list
    # @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-return-query
    ui.result(result, human_fn=lambda d: _human_list_ids(d))
    return 0
    # @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-return-query

# @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-format
def _human_list_ids(data: dict) -> None:
    count = data.get("count", 0)
    n_art = data.get("artifacts_scanned", 0)
    code_scanned = data.get("code_files_scanned")

    ui.header("List IDs")
    ui.detail("Artifacts scanned", str(n_art))
    if code_scanned is not None:
        ui.detail("Code files scanned", str(code_scanned))
    ui.detail("IDs found", str(count))

    ids = data.get("ids", [])
    if not ids:
        ui.blank()
        ui.info("No IDs found.")
        ui.blank()
        return

    # Group by kind for readability
    by_kind: Dict[str, List[Dict]] = {}
    for h in ids:
        k = str(h.get("kind") or "unknown")
        by_kind.setdefault(k, []).append(h)

    ui.blank()
    for kind_name in sorted(by_kind.keys()):
        items = by_kind[kind_name]
        ui.step(f"{kind_name} ({len(items)})")
        for h in items:
            cid = h.get("id", "?")
            htype = h.get("type", "")
            line = h.get("line", "")
            artifact = h.get("artifact", "")
            loc = f":{line}" if line else ""
            art_label = ui.relpath(artifact) if artifact else ""
            ui.substep(f"  {cid}  ({htype}, {art_label}{loc})")

    ui.blank()
# @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-format
