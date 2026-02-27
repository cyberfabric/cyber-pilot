import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ..utils import error_codes as EC
from ..utils.codebase import CodeFile, cross_validate_code
from ..utils.constraints import ArtifactRecord, cross_validate_artifacts, error as constraints_error, validate_artifact_file
from ..utils.document import scan_cdsl_instructions, scan_cpt_ids
from ..utils.fixing import enrich_issues


def cmd_validate(argv: List[str]) -> int:
    """Validate Cypilot artifacts and code traceability.

    Performs deterministic validation checks (structure, cross-references,
    task statuses, traceability markers) and produces a machine-readable report.
    """
    from ..utils.context import get_context

    p = argparse.ArgumentParser(
        prog="validate",
        description="Validate Cypilot artifacts and code traceability (structure + cross-refs + traceability)",
    )
    p.add_argument("--artifact", default=None, help="Path to specific Cypilot artifact (if omitted, validates all registered Cypilot artifacts)")
    p.add_argument("--skip-code", action="store_true", help="Skip code traceability validation")
    p.add_argument("--verbose", action="store_true", help="Print full validation report")
    p.add_argument("--output", default=None, help="Write report to file instead of stdout")
    p.add_argument("--local-only", action="store_true", help="Skip cross-repo workspace validation (validate local repo only)")
    args = p.parse_args(argv)

    # Use pre-loaded context (templates already loaded on startup)
    ctx = get_context()
    if not ctx:
        print(json.dumps({"status": "ERROR", "message": "No adapter found. Run 'init' first."}, indent=None, ensure_ascii=False))
        return 1

    # Surface context-level load errors (e.g., invalid constraints.json) as validation errors.
    ctx_errors = list(getattr(ctx, "_errors", []) or [])

    meta = ctx.meta
    project_root = ctx.project_root
    registered_systems = ctx.registered_systems
    known_kinds = ctx.get_known_id_kinds()

    if getattr(meta, "kits", None):
        try:
            from .self_check import run_self_check_from_meta

            rc, report = run_self_check_from_meta(
                project_root=project_root,
                adapter_dir=ctx.adapter_dir,
                artifacts_meta=meta,
                kit_filter=None,
                verbose=bool(args.verbose),
            )
            if rc != 0 or str(report.get("status")) != "PASS":
                out = {
                    "status": "FAIL" if rc == 2 else "ERROR",
                    "message": "self-check failed (templates/examples are inconsistent)",
                    "self_check": report,
                }
                print(json.dumps(out, indent=2, ensure_ascii=False))
                return 2 if rc == 2 else 1
        except Exception as e:
            out = {
                "status": "ERROR",
                "message": "self-check failed to run",
                "error": str(e),
            }
            print(json.dumps(out, indent=2, ensure_ascii=False))
            return 1
    
    for loaded_kit in (ctx.kits or {}).values():
        kit_constraints = getattr(loaded_kit, "constraints", None)
        if not kit_constraints:
            continue
        for kind_constraints in kit_constraints.by_kind.values():
            for c in (kind_constraints.defined_id or []):
                if c and getattr(c, "kind", None):
                    known_kinds.add(str(c.kind).strip().lower())

    # Collect artifacts to validate: (artifact_path, template_path, artifact_type, traceability, kit_id)
    artifacts_to_validate: List[Tuple[Path, Path, str, str, str]] = []

    if args.artifact:
        artifact_path = Path(args.artifact).resolve()
        if not artifact_path.exists():
            print(json.dumps({"status": "ERROR", "message": f"Artifact not found: {artifact_path}"}, indent=None, ensure_ascii=False))
            return 1

        # Load context from artifact's location
        from ..utils.context import CypilotContext

        ctx = CypilotContext.load(artifact_path.parent)
        if not ctx:
            print(json.dumps({"status": "ERROR", "message": "No adapter found"}, indent=None, ensure_ascii=False))
            return 1

        # Refresh context-level errors for this context.
        ctx_errors = list(getattr(ctx, "_errors", []) or [])

        meta = ctx.meta
        project_root = ctx.project_root
        registered_systems = ctx.registered_systems
        known_kinds = ctx.get_known_id_kinds()
        for loaded_kit in (ctx.kits or {}).values():
            kit_constraints = getattr(loaded_kit, "constraints", None)
            if not kit_constraints:
                continue
            for kind_constraints in kit_constraints.by_kind.values():
                for c in (kind_constraints.defined_id or []):
                    if c and getattr(c, "kind", None):
                        known_kinds.add(str(c.kind).strip().lower())
        try:
            rel_path = artifact_path.relative_to(project_root).as_posix()
        except ValueError:
            rel_path = None
        if rel_path:
            result = meta.get_artifact_by_path(rel_path)
            if result:
                artifact_meta, system_node = result
                pkg = meta.get_kit(system_node.kit)
                if pkg and pkg.is_cypilot_format():
                    template_path_str = pkg.get_template_path(artifact_meta.kind)
                    template_path = (project_root / template_path_str).resolve()
                    artifacts_to_validate.append((artifact_path, template_path, artifact_meta.kind, artifact_meta.traceability, system_node.kit))
        if not artifacts_to_validate:
            print(json.dumps({"status": "ERROR", "message": f"Artifact not in Cypilot registry: {args.artifact}"}, indent=None, ensure_ascii=False))
            return 1
    else:
        # Validate all Cypilot artifacts
        for artifact_meta, system_node in meta.iter_all_artifacts():
            pkg = meta.get_kit(system_node.kit)
            if not pkg or not pkg.is_cypilot_format():
                continue
            template_path_str = pkg.get_template_path(artifact_meta.kind)
            artifact_path = (project_root / artifact_meta.path).resolve()
            template_path = (project_root / template_path_str).resolve()
            if artifact_path.exists():
                artifacts_to_validate.append((artifact_path, template_path, artifact_meta.kind, artifact_meta.traceability, system_node.kit))

    if not artifacts_to_validate:
        print(json.dumps({"status": "ERROR", "message": "No Cypilot artifacts found in registry"}, indent=None, ensure_ascii=False))
        return 1

    # Validate each artifact
    all_errors: List[Dict[str, object]] = []
    all_warnings: List[Dict[str, object]] = []
    artifact_reports: List[Dict[str, object]] = []
    artifact_report_by_path: Dict[str, Dict[str, object]] = {}
    artifact_records: List[ArtifactRecord] = []

    if ctx_errors:
        all_errors.extend(ctx_errors)

    # Registry-level errors make further checks unreliable — stop early.
    has_registry_errors = any(str(e.get("type", "")) == "registry" for e in all_errors)
    if has_registry_errors:
        enrich_issues(all_errors, project_root=project_root)
        out = {
            "status": "FAIL",
            "project_root": project_root.as_posix(),
            "artifact_count": len(artifacts_to_validate),
            "error_count": len(all_errors),
            "warning_count": 0,
            "errors": all_errors,
        }
        if args.output:
            Path(args.output).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            print(json.dumps(out, indent=2, ensure_ascii=False))
        return 2

    for artifact_path, _template_path, artifact_type, traceability, kit_id in artifacts_to_validate:
        constraints_for_kind = None
        loaded_kit = (ctx.kits or {}).get(str(kit_id))
        if loaded_kit and loaded_kit.constraints and str(artifact_type) in loaded_kit.constraints.by_kind:
            constraints_for_kind = loaded_kit.constraints.by_kind[str(artifact_type)]

        constraints_path = None
        if loaded_kit:
            try:
                constraints_path = (project_root / str(loaded_kit.kit.path or "").strip().strip("/") / "constraints.json").resolve()
            except Exception:
                constraints_path = None

        artifact_records.append(ArtifactRecord(path=artifact_path, artifact_kind=str(artifact_type), constraints=constraints_for_kind))

        result = validate_artifact_file(
            artifact_path=artifact_path,
            artifact_kind=str(artifact_type),
            constraints=constraints_for_kind,
            registered_systems=registered_systems,
            constraints_path=constraints_path,
            kit_id=str(kit_id),
        )
        errors = result.get("errors", [])
        warnings = result.get("warnings", [])

        artifact_report: Dict[str, object] = {
            "artifact": str(artifact_path),
            "artifact_type": artifact_type,
            "traceability": traceability,
            "status": "PASS" if not errors else "FAIL",
            "error_count": len(errors),
            "warning_count": len(warnings),
        }

        # On FAIL, include detailed error/warning lists by default so `validate` output is actionable
        # without requiring `--verbose`.
        if args.verbose or errors:
            artifact_report["errors"] = errors
        if args.verbose or warnings:
            artifact_report["warnings"] = warnings
            try:
                _hits = scan_cpt_ids(artifact_path)
                artifact_report["id_definitions"] = len([h for h in _hits if h.get("type") == "definition"])
                artifact_report["id_references"] = len([h for h in _hits if h.get("type") == "reference"])
            except Exception:
                artifact_report["id_definitions"] = 0
                artifact_report["id_references"] = 0

        artifact_reports.append(artifact_report)
        artifact_report_by_path[str(artifact_path)] = artifact_report
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    def _attach_issue_to_artifact_report(issue: Dict[str, object], *, is_error: bool) -> None:
        ipath = str(issue.get("path", "") or "")
        rep = artifact_report_by_path.get(ipath)
        if rep is None:
            return

        if is_error:
            rep["status"] = "FAIL"
            rep["error_count"] = int(rep.get("error_count", 0) or 0) + 1
            if args.verbose and isinstance(rep.get("errors"), list):
                rep["errors"].append(issue)
        else:
            rep["warning_count"] = int(rep.get("warning_count", 0) or 0) + 1
            if args.verbose and isinstance(rep.get("warnings"), list):
                rep["warnings"].append(issue)

    # Stop early: cross-artifact reference checks and code traceability checks are run only
    # after per-artifact structure/content checks pass.
    if all_errors:
        enrich_issues(all_errors, project_root=project_root)
        enrich_issues(all_warnings, project_root=project_root)
        out = {
            "status": "FAIL",
            "project_root": project_root.as_posix(),
            "artifact_count": len(artifacts_to_validate),
            "error_count": len(all_errors),
            "warning_count": len(all_warnings),
        }
        out["errors"] = all_errors
        if all_warnings:
            out["warnings"] = all_warnings
        if args.output:
            Path(args.output).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            print(json.dumps(out, indent=2, ensure_ascii=False))
        return 2

    # Cross-reference validation - load ALL Cypilot artifacts for context
    # When validating a single artifact, we still need all artifacts to check references
    all_artifacts_for_cross: List[ArtifactRecord] = list(artifact_records)
    validated_paths = {str(p) for p, _, _, _, _ in artifacts_to_validate}

    # Load remaining artifacts that weren't validated (for cross-reference context)
    for artifact_meta, system_node in meta.iter_all_artifacts():
        pkg = meta.get_kit(system_node.kit)
        if not pkg or not pkg.is_cypilot_format():
            continue
        art_path = (project_root / artifact_meta.path).resolve()
        if str(art_path) in validated_paths:
            continue  # Already parsed
        if not art_path.exists():
            continue
        constraints_for_kind = None
        loaded_kit = (ctx.kits or {}).get(str(system_node.kit))
        if loaded_kit and loaded_kit.constraints and str(artifact_meta.kind) in loaded_kit.constraints.by_kind:
            constraints_for_kind = loaded_kit.constraints.by_kind[str(artifact_meta.kind)]
        all_artifacts_for_cross.append(ArtifactRecord(path=art_path, artifact_kind=str(artifact_meta.kind), constraints=constraints_for_kind))

    if len(all_artifacts_for_cross) > 0:
        cross_result = cross_validate_artifacts(all_artifacts_for_cross, registered_systems=registered_systems, known_kinds=known_kinds)
        cross_errors = cross_result.get("errors", [])
        cross_warnings = cross_result.get("warnings", [])
        # Only include cross-ref errors for artifacts we're validating
        for err in cross_errors:
            err_path = err.get("path", "")
            if err_path in validated_paths:
                all_errors.append(err)
                _attach_issue_to_artifact_report(err, is_error=True)
        for warn in cross_warnings:
            warn_path = warn.get("path", "")
            if warn_path in validated_paths:
                all_warnings.append(warn)
                _attach_issue_to_artifact_report(warn, is_error=False)

    # Code traceability validation (unless skipped)
    code_files_scanned: List[Dict[str, object]] = []
    parsed_code_files_full: List[CodeFile] = []
    code_ids_found: Set[str] = set()
    to_code_ids: Set[str] = set()
    to_code_ids_task_unchecked: Set[str] = set()
    artifact_ids: Set[str] = set()
    full_ids_to_check: Set[str] = set()

    # Build map of artifact path to traceability mode
    traceability_by_path: Dict[str, str] = {}
    for artifact_path, _template_path, _artifact_type, traceability, _kit_id in artifacts_to_validate:
        traceability_by_path[str(artifact_path)] = traceability

    # Determine which FULL-traceability IDs we might accept references from code for.
    for artifact_path, _template_path, _artifact_kind, traceability, _kit_id in artifacts_to_validate:
        if traceability != "FULL":
            continue
        try:
            for h in scan_cpt_ids(artifact_path):
                if h.get("type") != "definition" or not h.get("id"):
                    continue
                full_ids_to_check.add(str(h["id"]))
        except Exception:
            continue

    strict_code_validation = not args.artifact
    should_scan_code = (not args.skip_code) and (strict_code_validation or bool(full_ids_to_check))

    if strict_code_validation and len(all_artifacts_for_cross) > 0:
        # Build complete set of defined artifact IDs for orphan checks.
        for art in all_artifacts_for_cross:
            art_traceability = traceability_by_path.get(str(art.path), "FULL")
            for h in scan_cpt_ids(art.path):
                if h.get("type") != "definition" or not h.get("id"):
                    continue
                did = str(h["id"])
                artifact_ids.add(did)
                if art_traceability == "FULL":
                    # Best-effort: assume to_code when any constraint says so for inferred kind.
                    constraints_for_kind = getattr(art, "constraints", None)
                    if constraints_for_kind is not None:
                        # infer kind token for to_code lookup: use first constrained kind found in id.
                        for ic in getattr(constraints_for_kind, "defined_id", []) or []:
                            k = str(getattr(ic, "kind", "") or "").strip().lower()
                            if not k:
                                continue
                            if f"-{k}-" in did.lower() and bool(getattr(ic, "to_code", False)):
                                has_task = bool(h.get("has_task", False))
                                checked = bool(h.get("checked", False))
                                if has_task:
                                    if checked:
                                        to_code_ids_task_unchecked.discard(did)
                                        to_code_ids.add(did)
                                    else:
                                        to_code_ids_task_unchecked.add(did)
                                else:
                                    to_code_ids.add(did)
                                break

    # Workspace: expand artifact_ids with IDs from remote sources for cross-repo resolution
    if not args.local_only:
        from ..utils.context import WorkspaceContext
        if isinstance(ctx, WorkspaceContext) and ctx.sources:
            for sc in ctx.sources.values():
                if not sc.reachable or sc.meta is None:
                    continue
                for art, _sys in sc.meta.iter_all_artifacts():
                    art_path = (sc.path / art.path).resolve()
                    if not art_path.exists():
                        continue
                    try:
                        for h in scan_cpt_ids(art_path):
                            if h.get("type") == "definition" and h.get("id"):
                                artifact_ids.add(str(h["id"]))
                    except Exception:
                        continue

    if should_scan_code:
        # Scan code files from all systems
        def resolve_code_path(pth: str) -> Path:
            return (project_root / pth).resolve()

        def scan_codebase_entry(entry: dict, traceability: str) -> None:
            code_path = resolve_code_path(entry.get("path", ""))
            extensions = entry.get("extensions", [".py"])

            if not code_path.exists():
                return

            if code_path.is_file():
                files_to_scan = [code_path]
            else:
                files_to_scan = []
                for ext in extensions:
                    files_to_scan.extend(code_path.rglob(f"*{ext}"))

            for file_path in files_to_scan:
                # Apply registry root ignore rules as a hard visibility filter.
                try:
                    rel = file_path.resolve().relative_to(project_root).as_posix()
                except Exception:
                    rel = None
                if rel and meta.is_ignored(rel):
                    continue

                cf, errs = CodeFile.from_path(file_path)
                if errs or cf is None:
                    if strict_code_validation and errs:
                        all_errors.extend(errs)
                    continue

                if traceability == "FULL":
                    parsed_code_files_full.append(cf)

                if strict_code_validation:
                    # Validate structure
                    result = cf.validate()
                    all_errors.extend(result.get("errors", []))
                    all_warnings.extend(result.get("warnings", []))

                # Track IDs found
                file_ids = cf.list_ids()
                code_ids_found.update(file_ids)

                if file_ids or cf.scope_markers or cf.block_markers:
                    code_files_scanned.append({
                        "path": str(file_path),
                        "scope_markers": len(cf.scope_markers),
                        "block_markers": len(cf.block_markers),
                        "ids_referenced": len(file_ids),
                    })

        def scan_system_codebase(system_node: "SystemNode") -> None:
            for cb_entry in system_node.codebase:
                # Determine traceability from system artifacts
                traceability = "FULL"
                for art in system_node.artifacts:
                    if art.traceability == "DOCS-ONLY":
                        traceability = "DOCS-ONLY"
                        break
                scan_codebase_entry({
                    "path": cb_entry.path,
                    "extensions": cb_entry.extensions,
                }, traceability)
            for child in system_node.children:
                scan_system_codebase(child)

        for system_node in meta.systems:
            scan_system_codebase(system_node)

        if strict_code_validation and parsed_code_files_full:
            # Collect CDSL instructions per ID from FULL-traceability artifacts
            artifact_instances: Dict[str, Set[str]] = {}
            for art in all_artifacts_for_cross:
                art_traceability = traceability_by_path.get(str(art.path), "FULL")
                if art_traceability != "FULL":
                    continue
                try:
                    for step in scan_cdsl_instructions(art.path):
                        pid = str(step.get("parent_id") or "")
                        inst = str(step.get("inst") or "")
                        checked = bool(step.get("checked", False))
                        if pid and inst and checked:
                            artifact_instances.setdefault(pid, set()).add(inst)
                except Exception:
                    continue

            cv = cross_validate_code(
                parsed_code_files_full,
                artifact_ids,
                to_code_ids,
                forbidden_code_ids=to_code_ids_task_unchecked,
                traceability="FULL",
                artifact_instances=artifact_instances,
            )
            all_errors.extend(cv.get("errors", []))
            all_warnings.extend(cv.get("warnings", []))

    # Reference coverage (simplified): if an artifact kind has no constraints, each ID
    # definition must be referenced from at least one other artifact kind.
    # If traceability is FULL, a code reference also satisfies coverage.
    if len(all_artifacts_for_cross) > 0:
        present_kinds: Set[str] = set()
        refs_by_id: Dict[str, Set[str]] = {}

        # Build reference index across ALL artifacts.
        for art in all_artifacts_for_cross:
            kind = str(getattr(art, "artifact_kind", "") or "")
            present_kinds.add(kind)

            try:
                for h in scan_cpt_ids(art.path):
                    if h.get("type") != "reference":
                        continue
                    rid = str(h.get("id") or "").strip()
                    if not rid:
                        continue
                    refs_by_id.setdefault(rid, set()).add(kind)
            except Exception:
                continue

        # Enforce rule for validated artifacts with no constraints.
        for art in all_artifacts_for_cross:
            art_path_str = str(art.path)
            if art_path_str not in validated_paths:
                continue
            if getattr(art, "constraints", None) is not None:
                continue

            kind = str(getattr(art, "artifact_kind", "") or "")
            other_kinds = sorted(k for k in present_kinds if k != kind)
            art_traceability = traceability_by_path.get(art_path_str, "FULL")

            try:
                defs = [h for h in scan_cpt_ids(art.path) if h.get("type") == "definition" and h.get("id")]
            except Exception:
                defs = []

            for d in defs:
                did = str(d.get("id") or "").strip()
                if not did:
                    continue
                line = int(d.get("line", 1) or 1)

                if not other_kinds:
                    warn = constraints_error(
                        "structure",
                        f"`{did}` is not referenced — no other artifact kinds exist in scope for cross-referencing",
                        code=EC.ID_NOT_REFERENCED_NO_SCOPE,
                        path=art.path,
                        line=line,
                        id=did,
                    )
                    all_warnings.append(warn)
                    _attach_issue_to_artifact_report(warn, is_error=False)
                    continue

                referenced_kinds = sorted(k for k in refs_by_id.get(did, set()) if k != kind)
                if referenced_kinds:
                    continue

                # Allow code reference to satisfy coverage when FULL.
                if art_traceability == "FULL" and did in code_ids_found:
                    continue

                err = constraints_error(
                    "structure",
                    f"`{did}` (defined in {kind}) is not referenced from any of {other_kinds}",
                    code=EC.ID_NOT_REFERENCED,
                    path=art.path,
                    line=line,
                    id=did,
                    other_kinds=other_kinds,
                )
                all_errors.append(err)
                _attach_issue_to_artifact_report(err, is_error=True)

    # Resolve target artifact paths for cross-ref errors (before enrich_issues strips 'path')
    _enrich_target_artifact_paths(all_errors, meta=meta, project_root=project_root)

    # Enrich errors/warnings with fixing prompts for LLM agents
    enrich_issues(all_errors, project_root=project_root)
    enrich_issues(all_warnings, project_root=project_root)

    # Build final report
    overall_status = "PASS" if not all_errors else "FAIL"

    report: Dict[str, object] = {
        "status": overall_status,
        "artifacts_validated": len(artifact_reports),
        "error_count": len(all_errors),
        "warning_count": len(all_warnings),
    }

    # Add code validation stats if code was validated
    if not args.skip_code and not args.artifact:
        report["code_files_scanned"] = len(code_files_scanned)
        report["to_code_ids_total"] = len(to_code_ids)
        report["code_ids_found"] = len(code_ids_found)
        if to_code_ids:
            report["coverage"] = f"{len(code_ids_found & to_code_ids)}/{len(to_code_ids)}"

    # Add next step hint for agent
    if overall_status == "PASS":
        report["next_step"] = "Deterministic validation passed. Now perform semantic validation: review content quality against checklist.md criteria."

    if args.verbose:
        report["errors"] = all_errors
        report["warnings"] = all_warnings
    elif overall_status != "PASS":
        # On failure, always print a detailed, pretty report.
        report["errors"] = all_errors
        if all_warnings:
            report["warnings"] = all_warnings
    else:
        # Compact summary on PASS
        failed_artifacts = [r for r in artifact_reports if r.get("status") == "FAIL"]
        if failed_artifacts:
            report["failed_artifacts"] = [
                {"artifact": r.get("artifact"), "error_count": r.get("error_count")}
                for r in failed_artifacts
            ]

    pretty = bool(args.verbose) or (overall_status != "PASS")
    out = json.dumps(report, indent=2 if pretty else None, ensure_ascii=False)
    if pretty:
        out += "\n"

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)

    return 0 if overall_status == "PASS" else 2


def _enrich_target_artifact_paths(
    issues: List[Dict[str, object]],
    *,
    meta: object,
    project_root: Path,
) -> None:
    """Add ``target_artifact_path`` to 'ID not referenced from required artifact kind' errors.

    Three outcomes per error:
    - ``target_artifact_path`` set  → artifact exists, prompt says "in `path`"
    - ``target_artifact_suggested_path`` set → artifact missing, autodetect knows where → "create `path`"
    - neither set → no autodetect rule → prompt asks LLM to request path from user
    """
    from ..utils.artifacts_meta import ArtifactsMeta, SystemNode, AutodetectRule

    if not isinstance(meta, ArtifactsMeta):
        return

    for issue in issues:
        if str(issue.get("code") or "") != EC.REF_MISSING_FROM_KIND:
            continue

        target_kind = str(issue.get("target_kind") or "").upper()
        if not target_kind:
            continue

        # Find the system node that owns the source artifact
        src_path = str(issue.get("path") or "")
        try:
            rel_src = Path(src_path).relative_to(project_root).as_posix()
        except (ValueError, TypeError):
            continue

        result = meta.get_artifact_by_path(rel_src)
        if not result:
            continue
        _, system_node = result

        # Search system's artifacts for an existing artifact of target_kind
        target_path = _find_artifact_in_system(system_node, target_kind, project_root)
        if target_path:
            issue["target_artifact_path"] = target_path
            continue

        # No existing artifact — check autodetect rules for suggested path
        suggested = _suggest_path_from_autodetect(system_node, target_kind)
        if suggested:
            issue["target_artifact_suggested_path"] = suggested
        # else: neither set → fixing.py will ask user


def _find_artifact_in_system(node: object, target_kind: str, project_root: Path) -> Optional[str]:
    """Search system node and its children for an existing artifact of target_kind.

    Returns relative path string if found, else None.
    """
    from ..utils.artifacts_meta import SystemNode

    if not isinstance(node, SystemNode):
        return None
    for art in (node.artifacts or []):
        if str(art.kind).upper() == target_kind:
            full = (project_root / art.path).resolve()
            if full.exists():
                return str(full)
    for child in (node.children or []):
        found = _find_artifact_in_system(child, target_kind, project_root)
        if found:
            return found
    return None


def _suggest_path_from_autodetect(node: object, target_kind: str) -> Optional[str]:
    """Derive a suggested file path from autodetect rules for a missing artifact.

    Returns a project-root-relative path like ``architecture/DESIGN.md``, or None.
    """
    from ..utils.artifacts_meta import SystemNode

    if not isinstance(node, SystemNode):
        return None

    for rule in (node.autodetect or []):
        arts = rule.artifacts or {}
        kind_upper = {str(k).upper(): k for k in arts}
        orig_key = kind_upper.get(target_kind)
        if not orig_key:
            continue
        ap = arts[orig_key]
        pattern = str(ap.pattern or "")
        if not pattern:
            continue

        # Compute artifacts_root with simple substitution
        system_root = str(rule.system_root or "{project_root}")
        system_root = system_root.replace("{project_root}", ".")
        system_root = system_root.replace("{system}", node.slug or "")

        arts_root = str(rule.artifacts_root or "{system_root}")
        arts_root = arts_root.replace("{system_root}", system_root)
        arts_root = arts_root.replace("{project_root}", ".")
        arts_root = arts_root.replace("{system}", node.slug or "")

        # If pattern is a simple filename (no glob chars), use it directly
        if "*" not in pattern and "?" not in pattern:
            suggested = f"{arts_root}/{pattern}"
        else:
            # Glob pattern — suggest conventional {KIND}.md
            suggested = f"{arts_root}/{target_kind}.md"

        # Normalize: strip leading "./"
        suggested = suggested.lstrip("./")
        if suggested.startswith("/"):
            suggested = suggested.lstrip("/")
        return suggested

    return None
