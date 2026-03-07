# @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-imports
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from ..utils.document import scan_cpt_ids
from ..utils.ui import ui
# @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-imports

# @cpt-flow:cpt-cypilot-flow-traceability-validation-query:p1
# @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-resolve
def cmd_where_defined(argv: List[str]) -> int:
    """Find where a Cypilot ID is defined."""
    p = argparse.ArgumentParser(prog="where-defined", description="Find where an Cypilot ID is defined")
    p.add_argument("id_positional", nargs="?", default=None, help="Cypilot ID to find definition for")
    p.add_argument("--id", default=None, help="Cypilot ID to find definition for")
    p.add_argument("--artifact", default=None, help="Limit search to specific artifact (optional)")
    args = p.parse_args(argv)

    if args.id_positional and args.id:
        sys.stderr.write("WARNING: both positional ID and --id given; using positional\n")
    target_id = (args.id_positional or args.id or "").strip()
    if not target_id:
        ui.result({"status": "ERROR", "message": "ID cannot be empty"})
        return 1

    # Collect artifacts to scan: (artifact_path, artifact_kind)
    artifacts_to_scan: List[Tuple[Path, str]] = []

    if args.artifact:
        # Load context from artifact's location
        artifact_path = Path(args.artifact).resolve()
        if not artifact_path.exists():
            ui.result({"status": "ERROR", "message": f"Artifact not found: {artifact_path}"})
            return 1

        from ..utils.context import CypilotContext

        ctx = CypilotContext.load(artifact_path.parent)
        if not ctx:
            ui.result({"status": "ERROR", "message": "Cypilot not initialized. Run 'cypilot init' first."})
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
            ui.result({"status": "ERROR", "message": f"Artifact not in Cypilot registry: {args.artifact}"})
            return 1
    else:
        # Use global context
        from ..utils.context import get_context

        ctx = get_context()
        if not ctx:
            ui.result({"status": "ERROR", "message": "Cypilot not initialized. Run 'cypilot init' first."})
            return 1

        meta = ctx.meta
        project_root = ctx.project_root

        # Scan all Cypilot artifacts
        for artifact_meta, _system_node in meta.iter_all_artifacts():
            artifact_path = (project_root / artifact_meta.path).resolve()
            if artifact_path.exists():
                artifacts_to_scan.append((artifact_path, str(artifact_meta.kind)))

    if not artifacts_to_scan:
        ui.result({"status": "NOT_FOUND", "id": target_id, "artifacts_scanned": 0, "count": 0, "definitions": []}, human_fn=lambda d: _human_where_defined(d))
        return 0
    # @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-resolve

    # @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-if-where-def
    # Search for definitions
    definitions: List[Dict[str, object]] = []

    for artifact_path, artifact_type in artifacts_to_scan:
        for h in scan_cpt_ids(artifact_path):
            if h.get("type") != "definition":
                continue
            if str(h.get("id") or "") != target_id:
                continue
            definitions.append({
                "artifact": str(artifact_path),
                "artifact_type": artifact_type,
                "line": int(h.get("line", 1) or 1),
                "kind": None,
                "checked": bool(h.get("checked", False)),
            })

    if not definitions:
        ui.result({"status": "NOT_FOUND", "id": target_id, "artifacts_scanned": len(artifacts_to_scan), "count": 0, "definitions": []}, human_fn=lambda d: _human_where_defined(d))
        return 2

    status = "FOUND" if len(definitions) == 1 else "AMBIGUOUS"
    ui.result({"status": status, "id": target_id, "artifacts_scanned": len(artifacts_to_scan), "count": len(definitions), "definitions": definitions}, human_fn=lambda d: _human_where_defined(d))
    # @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-if-where-def
    return 0 if status == "FOUND" else 2

# @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-format
def _human_where_defined(data: dict) -> None:
    target = data.get("id", "?")
    status = data.get("status", "")
    defs = data.get("definitions", [])
    n_art = data.get("artifacts_scanned", 0)

    ui.header("Where Defined")
    ui.detail("ID", target)
    ui.detail("Artifacts scanned", str(n_art))

    if not defs:
        ui.blank()
        ui.warn(f"ID not found in any artifact.")
        ui.blank()
        return

    if status == "AMBIGUOUS":
        ui.warn(f"Ambiguous — {len(defs)} definitions found")

    ui.blank()
    for d in defs:
        art = ui.relpath(d.get("artifact", "?"))
        line = d.get("line", "")
        art_type = d.get("artifact_type", "")
        checked = d.get("checked", False)
        loc = f":{line}" if line else ""
        suffix = "  ✓" if checked else ""
        ui.step(f"{art}{loc}  ({art_type}){suffix}")

    ui.blank()
# @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-format
