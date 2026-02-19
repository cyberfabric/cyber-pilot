import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

from ..utils.document import scan_cpt_ids


def cmd_where_used(argv: List[str]) -> int:
    """Find all references to a Cypilot ID."""
    p = argparse.ArgumentParser(prog="where-used", description="Find all references to an Cypilot ID")
    p.add_argument("--id", required=True, help="Cypilot ID to find references for")
    p.add_argument("--artifact", default=None, help="Limit search to specific artifact (optional)")
    p.add_argument("--include-definitions", action="store_true", help="Include definitions in results")
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

    if not artifacts_to_scan:
        print(json.dumps({"status": "ERROR", "message": "No Cypilot artifacts found in registry"}, indent=None, ensure_ascii=False))
        return 1

    # Search for references
    references: List[Dict[str, object]] = []

    for artifact_path, artifact_type in artifacts_to_scan:
        for h in scan_cpt_ids(artifact_path):
            if str(h.get("id") or "") != target_id:
                continue
            if h.get("type") == "definition" and not bool(args.include_definitions):
                continue
            references.append({
                "artifact": str(artifact_path),
                "artifact_type": artifact_type,
                "line": int(h.get("line", 1) or 1),
                "kind": None,
                "type": str(h.get("type")),
                "checked": bool(h.get("checked", False)),
            })

    # Sort by artifact and line
    references = sorted(references, key=lambda r: (str(r.get("artifact", "")), int(r.get("line", 0))))

    print(json.dumps({
        "id": target_id,
        "artifacts_scanned": len(artifacts_to_scan),
        "count": len(references),
        "references": references,
    }, indent=None, ensure_ascii=False))
    return 0
