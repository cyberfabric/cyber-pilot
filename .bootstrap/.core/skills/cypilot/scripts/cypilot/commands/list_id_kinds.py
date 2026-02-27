"""
List ID Kinds Command — list all ID kind tokens found in artifacts.

@cpt-flow:cpt-cypilot-flow-traceability-validation-query:p1
@cpt-dod:cpt-cypilot-dod-traceability-validation-queries:p1
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ..utils.document import scan_cpt_ids


def cmd_list_id_kinds(argv: List[str]) -> int:
    """List ID kinds that actually exist in artifacts.

    Parses artifacts against their templates and returns only kinds
    that have at least one ID definition in the artifact(s).
    """
    # @cpt-begin:cpt-cypilot-algo-traceability-validation-list-id-kinds:p1:inst-kinds-parse-args
    p = argparse.ArgumentParser(prog="list-id-kinds", description="List ID kinds found in Cypilot artifacts")
    p.add_argument("--artifact", default=None, help="Scan specific artifact (if omitted, scans all registered Cypilot artifacts)")
    args = p.parse_args(argv)
    # @cpt-end:cpt-cypilot-algo-traceability-validation-list-id-kinds:p1:inst-kinds-parse-args

    # @cpt-begin:cpt-cypilot-algo-traceability-validation-list-id-kinds:p1:inst-kinds-resolve-artifacts
    # Collect artifacts to scan: (artifact_path, artifact_kind)
    artifacts_to_scan: List[Tuple[Path, str]] = []
    ctx = None

    if args.artifact:
        artifact_path = Path(args.artifact).resolve()
        if not artifact_path.exists():
            print(json.dumps({"status": "ERROR", "message": f"Artifact not found: {artifact_path}"}, indent=None, ensure_ascii=False))
            return 1

        from ..utils.context import CypilotContext

        ctx = CypilotContext.load(artifact_path.parent)
        if not ctx:
            print(json.dumps({"status": "ERROR", "message": "Cypilot not initialized"}, indent=None, ensure_ascii=False))
            return 1

        project_root = ctx.project_root
        meta = ctx.meta

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
            print(json.dumps({"status": "ERROR", "message": f"Artifact not found in registry: {args.artifact}"}, indent=None, ensure_ascii=False))
            return 1
    else:
        # Scan all Cypilot artifacts from global context (autodetect-expanded)
        from ..utils.context import get_context

        ctx = get_context()
        if not ctx:
            print(json.dumps({"status": "ERROR", "message": "Cypilot not initialized. Run 'cypilot init' first."}, indent=None, ensure_ascii=False))
            return 1

        meta = ctx.meta
        project_root = ctx.project_root

        for artifact_meta, _system_node in meta.iter_all_artifacts():
            artifact_path = (project_root / artifact_meta.path).resolve()
            if artifact_path.exists():
                artifacts_to_scan.append((artifact_path, str(artifact_meta.kind)))

        # @cpt-begin:cpt-cypilot-algo-traceability-validation-list-id-kinds:p1:inst-kinds-if-no-artifacts
        if not artifacts_to_scan:
            print(json.dumps({"kinds": [], "kind_counts": {}, "kind_to_templates": {}, "template_to_kinds": {}, "artifacts_scanned": 0}, indent=None, ensure_ascii=False))
            return 0
        # @cpt-end:cpt-cypilot-algo-traceability-validation-list-id-kinds:p1:inst-kinds-if-no-artifacts
    # @cpt-end:cpt-cypilot-algo-traceability-validation-list-id-kinds:p1:inst-kinds-resolve-artifacts

    # @cpt-begin:cpt-cypilot-algo-traceability-validation-list-id-kinds:p1:inst-kinds-build-known
    # Parse artifacts and collect kinds that have actual IDs
    template_to_kinds: Dict[str, Set[str]] = {}
    kind_to_templates: Dict[str, Set[str]] = {}
    kind_counts: Dict[str, int] = {}

    registered_systems = set((ctx.registered_systems or set()) if ctx else set())
    known_kinds = set((ctx.get_known_id_kinds() if ctx else set()) or set())
    if ctx:
        for loaded_kit in (ctx.kits or {}).values():
            kit_constraints = getattr(loaded_kit, "constraints", None)
            if not kit_constraints:
                continue
            for kind_constraints in kit_constraints.by_kind.values():
                for c in (kind_constraints.defined_id or []):
                    if c and getattr(c, "kind", None):
                        known_kinds.add(str(c.kind).strip().lower())
    # @cpt-end:cpt-cypilot-algo-traceability-validation-list-id-kinds:p1:inst-kinds-build-known

    # @cpt-begin:cpt-cypilot-algo-traceability-validation-list-id-kinds:p1:inst-kinds-scan-ids
    def _match_system_prefix(cpt_id: str) -> Optional[str]:
        best: Optional[str] = None
        for sys_slug in registered_systems:
            prefix = f"cpt-{sys_slug}-"
            if cpt_id.lower().startswith(prefix.lower()):
                if best is None or len(sys_slug) > len(best):
                    best = sys_slug
        return best

    def _infer_kinds(cpt_id: str) -> List[str]:
        sys_slug = _match_system_prefix(cpt_id)
        if not sys_slug:
            return []
        remainder = cpt_id[len(f"cpt-{sys_slug}-"):]
        if not remainder:
            return []
        parts = [p for p in remainder.split("-") if p]
        out: List[str] = []
        for i in range(0, len(parts), 2):
            k = parts[i].lower()
            if known_kinds and k not in known_kinds:
                continue
            out.append(k)
        return out

    for artifact_path, artifact_type in artifacts_to_scan:
        for h in scan_cpt_ids(artifact_path):
            if h.get("type") != "definition":
                continue
            cid = str(h.get("id") or "").strip()
            if not cid:
                continue
            for kind_name in _infer_kinds(cid) or [None]:
                if not kind_name:
                    continue
                kind_to_templates.setdefault(kind_name, set()).add(artifact_type)
                template_to_kinds.setdefault(artifact_type, set()).add(kind_name)
                kind_counts[kind_name] = kind_counts.get(kind_name, 0) + 1
    # @cpt-end:cpt-cypilot-algo-traceability-validation-list-id-kinds:p1:inst-kinds-scan-ids

    # @cpt-begin:cpt-cypilot-algo-traceability-validation-list-id-kinds:p1:inst-kinds-return
    # Build output
    all_kinds = sorted(kind_to_templates.keys())

    if args.artifact and artifacts_to_scan:
        artifact_path, artifact_type = artifacts_to_scan[0]
        kinds_in_artifact = sorted(template_to_kinds.get(artifact_type, set()))
        print(json.dumps({
            "artifact": str(artifact_path),
            "artifact_type": artifact_type,
            "kinds": kinds_in_artifact,
            "kind_counts": {k: kind_counts.get(k, 0) for k in kinds_in_artifact},
        }, indent=None, ensure_ascii=False))
    else:
        print(json.dumps({
            "kinds": all_kinds,
            "kind_counts": {k: kind_counts.get(k, 0) for k in all_kinds},
            "kind_to_templates": {k: sorted(v) for k, v in sorted(kind_to_templates.items())},
            "template_to_kinds": {k: sorted(v) for k, v in sorted(template_to_kinds.items())},
            "artifacts_scanned": len(artifacts_to_scan),
        }, indent=None, ensure_ascii=False))
    # @cpt-end:cpt-cypilot-algo-traceability-validation-list-id-kinds:p1:inst-kinds-return
    return 0
