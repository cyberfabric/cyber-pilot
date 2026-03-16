# @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-imports
import argparse
from typing import Dict, List

from ..utils.context import resolve_target_and_artifacts
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

    target_id, _, artifacts_to_scan, path_to_source, err = resolve_target_and_artifacts(args)
    if err:
        ui.result({"status": "ERROR", "message": err}, human_fn=lambda d: _human_where_defined(d))
        return 1

    if not artifacts_to_scan:
        ui.result({"status": "NO_ARTIFACTS", "id": target_id, "artifacts_scanned": 0, "count": 0, "definitions": []}, human_fn=lambda d: _human_where_defined(d))
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
        ui.result({"status": "NOT_FOUND", "id": target_id, "artifacts_scanned": len(artifacts_to_scan), "count": 0, "definitions": []}, human_fn=lambda d: _human_where_defined(d))
        return 2

    status = "FOUND" if len(definitions) == 1 else "AMBIGUOUS"
    ui.result({"status": status, "id": target_id, "artifacts_scanned": len(artifacts_to_scan), "count": len(definitions), "definitions": definitions}, human_fn=lambda d: _human_where_defined(d))
    # @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-if-where-def
    return 0 if status == "FOUND" else 2

# @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-format
def _human_where_defined(data: dict) -> None:
    status = data.get("status", "")

    if status == "ERROR":
        ui.header("Where Defined")
        ui.blank()
        ui.error(data.get("message", "unknown error"))
        ui.blank()
        return

    target = data.get("id", "?")
    defs = data.get("definitions", [])
    n_art = data.get("artifacts_scanned", 0)

    ui.header("Where Defined")
    ui.detail("ID", target)
    ui.detail("Artifacts scanned", str(n_art))

    if not defs:
        ui.blank()
        if status == "NO_ARTIFACTS":
            ui.warn("No artifacts available to scan.")
        else:
            ui.warn("ID not found in any artifact.")
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
        source = d.get("source")
        loc = f":{line}" if line else ""
        suffix = "  ✓" if checked else ""
        src_tag = f" [{source}]" if source else ""
        ui.step(f"{art}{loc}  ({art_type}){src_tag}{suffix}")

    ui.blank()
# @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-format
