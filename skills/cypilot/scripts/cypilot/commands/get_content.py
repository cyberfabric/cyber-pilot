import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

from ..utils.codebase import CodeFile
from ..utils.document import get_content_scoped


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
            print(json.dumps({"status": "ERROR", "message": f"Code file not found: {code_path}"}, indent=None, ensure_ascii=False))
            return 1

        cf, errs = CodeFile.from_path(code_path)
        if errs or cf is None:
            print(json.dumps({"status": "ERROR", "message": f"Failed to parse code file: {errs}"}, indent=None, ensure_ascii=False))
            return 1

        # Try to get content by ID or inst
        content = None
        if args.inst:
            content = cf.get_by_inst(args.inst)
        if content is None:
            content = cf.get(args.id)

        if content is None:
            print(json.dumps({"status": "NOT_FOUND", "id": args.id, "inst": args.inst}, indent=None, ensure_ascii=False))
            return 2

        print(json.dumps({"status": "FOUND", "id": args.id, "inst": args.inst, "text": content}, indent=None, ensure_ascii=False))
        return 0

    # Handle artifact path
    if not args.artifact:
        print(json.dumps({"status": "ERROR", "message": "Either --artifact or --code must be specified"}, indent=None, ensure_ascii=False))
        return 1

    artifact_path = Path(args.artifact).resolve()
    if not artifact_path.is_file():
        print(json.dumps({"status": "ERROR", "message": f"Artifact not found: {artifact_path}"}, indent=None, ensure_ascii=False))
        return 1

    # Load CypilotContext from artifact's location
    from ..utils.context import CypilotContext

    ctx = CypilotContext.load(artifact_path.parent)
    if not ctx:
        print(json.dumps({"status": "ERROR", "message": "Cypilot not initialized"}, indent=None, ensure_ascii=False))
        return 1

    meta = ctx.meta
    project_root = ctx.project_root

    # Find artifact in registry to get its template
    try:
        rel_path = artifact_path.relative_to(project_root).as_posix()
    except ValueError:
        print(json.dumps({"status": "ERROR", "message": f"Artifact not under project root: {artifact_path}"}, indent=None, ensure_ascii=False))
        return 1

    artifact_entry = meta.get_artifact_by_path(rel_path)
    if artifact_entry is None:
        print(json.dumps({"status": "ERROR", "message": f"Artifact not registered: {rel_path}"}, indent=None, ensure_ascii=False))
        return 1

    artifact_meta, system = artifact_entry
    result = get_content_scoped(artifact_path, id_value=args.id)
    if result is None:
        print(json.dumps({"status": "NOT_FOUND", "id": args.id}, indent=None, ensure_ascii=False))
        return 2

    text, start_line, end_line = result
    print(json.dumps({
        "status": "FOUND",
        "id": args.id,
        "text": text,
        "artifact": str(artifact_path),
        "start_line": start_line,
        "end_line": end_line,
        "kind": artifact_meta.kind,
        "system": system.name,
        "traceability": artifact_meta.traceability,
    }, indent=None, ensure_ascii=False))
    # @cpt-end:cpt-cypilot-flow-traceability-validation-query:p1:inst-if-get-content
    return 0
