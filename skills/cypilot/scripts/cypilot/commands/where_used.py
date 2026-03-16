# @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-imports
import argparse
from typing import Dict, List

from ..utils.context import resolve_target_and_artifacts
from ..utils.document import scan_cpt_ids
from ..utils.ui import ui
# @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-imports

# @cpt-flow:cpt-cypilot-flow-traceability-validation-query:p1
# @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-resolve
def cmd_where_used(argv: List[str]) -> int:
    """Find all references to a Cypilot ID."""
    p = argparse.ArgumentParser(prog="where-used", description="Find all references to an Cypilot ID")
    p.add_argument("id_positional", nargs="?", default=None, help="Cypilot ID to find references for")
    p.add_argument("--id", default=None, help="Cypilot ID to find references for")
    p.add_argument("--artifact", default=None, help="Limit search to specific artifact (optional)")
    p.add_argument("--include-definitions", action="store_true", help="Include definitions in results")
    args = p.parse_args(argv)

    target_id, _, artifacts_to_scan, path_to_source, err = resolve_target_and_artifacts(args)
    if err:
        ui.result({"status": "ERROR", "message": err})
        return 1

    if not artifacts_to_scan:
        ui.result({"id": target_id, "artifacts_scanned": 0, "count": 0, "references": []}, human_fn=lambda d: _human_where_used(d))
        return 0
    # @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-resolve

    # @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-if-where-used

    # Search for references
    references: List[Dict[str, object]] = []

    for artifact_path, artifact_type in artifacts_to_scan:
        for h in scan_cpt_ids(artifact_path):
            if str(h.get("id") or "") != target_id:
                continue
            if h.get("type") == "definition" and not bool(args.include_definitions):
                continue
            r: Dict[str, object] = {
                "artifact": str(artifact_path),
                "artifact_type": artifact_type,
                "line": int(h.get("line", 1) or 1),
                "kind": None,
                "type": str(h.get("type")),
                "checked": bool(h.get("checked", False)),
            }
            src = path_to_source.get(str(artifact_path))
            if src:
                r["source"] = src
            references.append(r)

    # Sort by artifact and line
    references = sorted(references, key=lambda r: (str(r.get("artifact", "")), int(r.get("line", 0))))

    # @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-if-where-used
    ui.result({"id": target_id, "artifacts_scanned": len(artifacts_to_scan), "count": len(references), "references": references}, human_fn=lambda d: _human_where_used(d))
    return 0

# @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-format
def _human_where_used(data: dict) -> None:
    target = data.get("id", "?")
    refs = data.get("references", [])
    n_art = data.get("artifacts_scanned", 0)

    ui.header("Where Used")
    ui.detail("ID", target)
    ui.detail("Artifacts scanned", str(n_art))
    ui.detail("References found", str(data.get("count", len(refs))))

    if not refs:
        ui.blank()
        ui.info("No references found.")
        ui.blank()
        return

    ui.blank()
    for r in refs:
        art = ui.relpath(r.get("artifact", "?"))
        line = r.get("line", "")
        art_type = r.get("artifact_type", "")
        ref_type = r.get("type", "")
        checked = r.get("checked", False)
        source = r.get("source")
        loc = f":{line}" if line else ""
        suffix = "  \u2713" if checked else ""
        src_tag = f" [{source}]" if source else ""
        ui.step(f"{art}{loc}  ({ref_type}, {art_type}){src_tag}{suffix}")

    ui.blank()
# @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-format
