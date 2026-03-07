# @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-imports
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

from ..utils.codebase import CodeFile
from ..utils.document import get_content_scoped
from ..utils.ui import ui
# @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-imports

# @cpt-flow:cpt-cypilot-flow-traceability-validation-query:p1
def cmd_get_content(argv: List[str]) -> int:
    """Get best-effort content block for a specific Cypilot ID."""
    p = argparse.ArgumentParser(prog="get-content", description="Get content block for a specific Cypilot ID")
    p.add_argument("--artifact", default=None, help="Path to Cypilot artifact file")
    p.add_argument("--code", default=None, help="Path to code file (alternative to --artifact)")
    p.add_argument("--id", required=True, help="Cypilot ID to retrieve content for")
    p.add_argument("--inst", default=None, help="Instruction ID for code blocks (e.g., 'inst-validate-input')")
    args = p.parse_args(argv)

    # @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-if-get-content
    # Handle code file path
    if args.code:
        code_path = Path(args.code).resolve()
        if not code_path.is_file():
            ui.result({"status": "ERROR", "message": f"Code file not found: {code_path}"})
            return 1

        cf, errs = CodeFile.from_path(code_path)
        if errs or cf is None:
            ui.result({"status": "ERROR", "message": f"Failed to parse code file: {errs}"})
            return 1

        # Try to get content by ID or inst
        content = None
        if args.inst:
            content = cf.get_by_inst(args.inst)
        if content is None:
            content = cf.get(args.id)

        if content is None:
            ui.result({"status": "NOT_FOUND", "id": args.id, "inst": args.inst})
            return 2

        ui.result({"status": "FOUND", "id": args.id, "inst": args.inst, "text": content}, human_fn=lambda d: _human_get_content(d))
        return 0

    # Handle artifact path
    if not args.artifact:
        ui.result({"status": "ERROR", "message": "Either --artifact or --code must be specified"})
        return 1

    artifact_path = Path(args.artifact).resolve()
    if not artifact_path.is_file():
        ui.result({"status": "ERROR", "message": f"Artifact not found: {artifact_path}"})
        return 1

    # Load CypilotContext from artifact's location
    from ..utils.context import CypilotContext

    ctx = CypilotContext.load(artifact_path.parent)
    if not ctx:
        ui.result({"status": "ERROR", "message": "Cypilot not initialized"})
        return 1

    meta = ctx.meta
    project_root = ctx.project_root

    # Find artifact in registry to get its template
    try:
        rel_path = artifact_path.relative_to(project_root).as_posix()
    except ValueError:
        ui.result({"status": "ERROR", "message": f"Artifact not under project root: {artifact_path}"})
        return 1

    artifact_entry = meta.get_artifact_by_path(rel_path)
    if artifact_entry is None:
        ui.result({"status": "ERROR", "message": f"Artifact not registered: {rel_path}"})
        return 1

    artifact_meta, system = artifact_entry
    result = get_content_scoped(artifact_path, id_value=args.id)
    if result is None:
        ui.result({"status": "NOT_FOUND", "id": args.id})
        return 2

    text, start_line, end_line = result
    ui.result({
        "status": "FOUND",
        "id": args.id,
        "text": text,
        "artifact": str(artifact_path),
        "start_line": start_line,
        "end_line": end_line,
        "kind": artifact_meta.kind,
        "system": system.name,
        "traceability": artifact_meta.traceability,
    }, human_fn=lambda d: _human_get_content(d))
    # @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-if-get-content
    return 0

# @cpt-begin:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-format
def _human_get_content(data: dict) -> None:
    status = data.get("status", "")
    cid = data.get("id", "?")

    ui.header("Get Content")
    ui.detail("ID", cid)

    if status in ("NOT_FOUND",):
        inst = data.get("inst")
        if inst:
            ui.detail("Inst", inst)
        ui.blank()
        ui.warn("Content not found.")
        ui.blank()
        return

    if status in ("ERROR",):
        ui.error(data.get("message", "Unknown error"))
        ui.blank()
        return

    artifact = data.get("artifact")
    if artifact:
        artifact = ui.relpath(str(artifact))
        ui.detail("Artifact", str(artifact))
    kind = data.get("kind")
    if kind:
        ui.detail("Kind", str(kind))
    system = data.get("system")
    if system:
        ui.detail("System", str(system))
    start = data.get("start_line")
    end = data.get("end_line")
    if start is not None and end is not None:
        ui.detail("Lines", f"{start}-{end}")
    traceability = data.get("traceability")
    if traceability:
        ui.detail("Traceability", str(traceability))
    inst = data.get("inst")
    if inst:
        ui.detail("Inst", inst)

    text = data.get("text", "")
    if text:
        ui.blank()
        ui.divider()
        for line in text.splitlines():
            ui.info(line)
        ui.divider()

    ui.blank()
# @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-query-format
