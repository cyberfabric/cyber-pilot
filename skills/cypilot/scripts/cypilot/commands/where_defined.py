import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

from ..utils.document import scan_cpt_ids


# @cpt-flow:cpt-cypilot-flow-traceability-validation-query:p1
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
    path_to_source: Dict[str, str] = {}

    if args.artifact:
        # Load context from artifact's location
        artifact_path = Path(args.artifact).resolve()
        if not artifact_path.exists():
            print(json.dumps({"status": "ERROR", "message": f"Artifact not found: {artifact_path}"}, indent=None, ensure_ascii=False))
            return 1

        from ..utils.context import CypilotContext

        ctx = CypilotContext.load(artifact_path.parent)
        if not ctx:
            print(json.dumps({"status": "ERROR", "message": "Cypilot not initialized. Run 'cypilot init' first."}, indent=None, ensure_ascii=False))
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
        from ..utils.context import get_context, collect_artifacts_to_scan

        ctx = get_context()
        if not ctx:
            print(json.dumps({"status": "ERROR", "message": "Cypilot not initialized. Run 'cypilot init' first."}, indent=None, ensure_ascii=False))
            return 1

        artifacts_to_scan, path_to_source = collect_artifacts_to_scan(ctx)

    if not artifacts_to_scan:
        print(json.dumps({
            "status": "NOT_FOUND",
            "id": target_id,
            "artifacts_scanned": 0,
            "count": 0,
            "definitions": [],
        }, indent=None, ensure_ascii=False))
        return 0

    # @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-if-where-def

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
    # @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-if-where-def
    return 0 if status == "FOUND" else 2
