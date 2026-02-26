import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

from ..utils.document import scan_cpt_ids


def cmd_where_defined(argv: List[str]) -> int:
    """Find where a Cypilot ID is defined."""
    p = argparse.ArgumentParser(prog="where-defined", description="Find where an Cypilot ID is defined")
    p.add_argument("--id", required=True, help="Cypilot ID to find definition for")
    p.add_argument("--artifact", default=None, help="Limit search to specific artifact (optional)")
    args = p.parse_args(argv)

    target_id = str(args.id).strip()
    if not target_id:
        print(json.dumps({"status": "ERROR", "message": "ID cannot be empty"}, indent=None, ensure_ascii=False))
        return 1

    # Collect artifacts to scan: (artifact_path, artifact_kind)
    artifacts_to_scan: List[Tuple[Path, str]] = []

    if args.artifact:
        # Load context from artifact's location
        artifact_path = Path(args.artifact).resolve()
        if not artifact_path.exists():
            print(json.dumps({"status": "ERROR", "message": f"Artifact not found: {artifact_path}"}, indent=None, ensure_ascii=False))
            return 1

        from ..utils.context import CypilotContext

        ctx = CypilotContext.load(artifact_path.parent)
        if not ctx:
            print(json.dumps({"status": "ERROR", "message": "No adapter found. Run 'init' first."}, indent=None, ensure_ascii=False))
            return 1

        meta = ctx.meta
        project_root = ctx.project_root

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
            print(json.dumps({"status": "ERROR", "message": f"Artifact not in Cypilot registry: {args.artifact}"}, indent=None, ensure_ascii=False))
            return 1
    else:
        # Use global context
        from ..utils.context import get_context

        ctx = get_context()
        if not ctx:
            print(json.dumps({"status": "ERROR", "message": "No adapter found. Run 'init' first."}, indent=None, ensure_ascii=False))
            return 1

        meta = ctx.meta
        project_root = ctx.project_root

        # Scan all Cypilot artifacts
        for artifact_meta, _system_node in meta.iter_all_artifacts():
            artifact_path = (project_root / artifact_meta.path).resolve()
            if artifact_path.exists():
                artifacts_to_scan.append((artifact_path, str(artifact_meta.kind)))

        # Workspace: also scan artifacts from remote sources
        from ..utils.context import WorkspaceContext
        if isinstance(ctx, WorkspaceContext):
            for sc in ctx.sources.values():
                if not sc.reachable or sc.meta is None:
                    continue
                for art, _sys in sc.meta.iter_all_artifacts():
                    art_path = (sc.path / art.path).resolve()
                    if art_path.exists():
                        artifacts_to_scan.append((art_path, str(art.kind)))

    if not artifacts_to_scan:
        print(json.dumps({"status": "ERROR", "message": "No Cypilot artifacts found in registry"}, indent=None, ensure_ascii=False))
        return 1

    # Build path-to-source mapping for workspace results
    path_to_source: Dict[str, str] = {}
    from ..utils.context import WorkspaceContext
    if isinstance(ctx, WorkspaceContext):
        for sc in ctx.sources.values():
            if not sc.reachable or sc.meta is None:
                continue
            for art, _sys in sc.meta.iter_all_artifacts():
                art_path = (sc.path / art.path).resolve()
                path_to_source[str(art_path)] = sc.name

    # Search for definitions
    definitions: List[Dict[str, object]] = []

    for artifact_path, artifact_type in artifacts_to_scan:
        for h in scan_cpt_ids(artifact_path):
            if h.get("type") != "definition":
                continue
            if str(h.get("id") or "") != target_id:
                continue
            d: Dict[str, object] = {
                "artifact": str(artifact_path),
                "artifact_type": artifact_type,
                "line": int(h.get("line", 1) or 1),
                "kind": None,
                "checked": bool(h.get("checked", False)),
            }
            src = path_to_source.get(str(artifact_path))
            if src:
                d["source"] = src
            definitions.append(d)

    if not definitions:
        print(json.dumps({
            "status": "NOT_FOUND",
            "id": target_id,
            "artifacts_scanned": len(artifacts_to_scan),
            "count": 0,
            "definitions": [],
        }, indent=None, ensure_ascii=False))
        return 2

    status = "FOUND" if len(definitions) == 1 else "AMBIGUOUS"
    print(json.dumps({
        "status": status,
        "id": target_id,
        "artifacts_scanned": len(artifacts_to_scan),
        "count": len(definitions),
        "definitions": definitions,
    }, indent=None, ensure_ascii=False))
    return 0 if status == "FOUND" else 2
