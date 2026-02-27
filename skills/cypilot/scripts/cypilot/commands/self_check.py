import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..utils.artifacts_meta import ArtifactsMeta
from ..utils.constraints import (
    error as constraints_error,
    heading_constraint_ids_by_line,
    validate_artifact_file,
    validate_headings_contract,
)
from ..utils import error_codes as EC
from ..utils.document import read_text_safe
from ..utils.files import find_cypilot_directory, find_project_root, load_artifacts_registry


def run_self_check_from_meta(
    *,
    project_root: Path,
    adapter_dir: Path,
    artifacts_meta: ArtifactsMeta,
    kit_filter: Optional[str] = None,
    verbose: bool = False,
) -> Tuple[int, Dict[str, object]]:
    """Run self-check using already-loaded registry metadata.

    This is used by both the CLI `self-check` command and by `validate` to fail-fast.
    It does NOT do cypilot/project discovery.
    """
    from ..utils.constraints import load_constraints_toml

    def _check_template_constraints_consistency(
        *,
        template_path: Path,
        kind: str,
        kit_id: str,
        kit_base: Path,
        kit_constraints,
        artifacts_meta: ArtifactsMeta,
    ) -> Dict[str, List[Dict[str, object]]]:
        errs: List[Dict[str, object]] = []
        warns: List[Dict[str, object]] = []

        if kit_constraints is None:
            errs.append({
                "type": "constraints",
                "message": "constraints.toml not found (template consistency checks skipped)",
                "path": str(kit_base / "constraints.toml"),
            })
            return {"errors": errs, "warnings": warns}

        kind_u = str(kind).strip().upper()
        constraints_for_kind = None
        if kit_constraints is not None and getattr(kit_constraints, "by_kind", None) and kind_u in kit_constraints.by_kind:
            constraints_for_kind = kit_constraints.by_kind[kind_u]

        if constraints_for_kind is None:
            errs.append(constraints_error(
                "template",
                "Template kind not found in constraints.toml",
                path=template_path,
                line=1,
                kit_id=str(kit_id),
                artifact_kind=kind_u,
            ))
            return {"errors": errs, "warnings": warns}

        constraints_path = None
        try:
            constraints_path = (kit_base / "constraints.toml").resolve()
        except Exception:
            constraints_path = None

        # 1) Heading contract must hold for templates too.
        rep = validate_headings_contract(
            path=template_path,
            constraints=constraints_for_kind,
            registered_systems=artifacts_meta.get_all_system_prefixes(),
            artifact_kind=kind_u,
            constraints_path=constraints_path,
            kit_id=str(kit_id),
        )
        errs.extend(list(rep.get("errors", []) or []))
        warns.extend(list(rep.get("warnings", []) or []))

        # Phase gating: if template outline is invalid, skip ID/reference checks.
        if errs:
            return {"errors": errs, "warnings": warns}

        lines = read_text_safe(template_path)
        if lines is None:
            errs.append(constraints_error(
                "template",
                "Template file could not be read",
                path=template_path,
                line=1,
                kit_id=str(kit_id),
                artifact_kind=kind_u,
            ))
            return {"errors": errs, "warnings": warns}

        # Use heading constraint ids so that we can validate placement against IdConstraint.headings.
        headings_at = None
        if getattr(constraints_for_kind, "headings", None):
            headings_at = heading_constraint_ids_by_line(template_path, constraints_for_kind.headings)

        def _occurrences(needle: str) -> List[int]:
            if not needle:
                return []
            out: List[int] = []
            for idx0, raw in enumerate(lines):
                if needle in raw:
                    out.append(idx0 + 1)
            return out

        def _definition_occurrences(tpl: str) -> List[int]:
            if not tpl:
                return []
            out: List[int] = []
            for idx0, raw in enumerate(lines):
                # Definition placeholders must be in an ID-definition line.
                if "**ID**" not in raw:
                    continue
                if f"`{tpl}`" in raw:
                    out.append(idx0 + 1)
            return out

        # 2) Defined ID kinds must appear in template and be placed under allowed headings.
        for ic in (getattr(constraints_for_kind, "defined_id", None) or []):
            id_kind = str(getattr(ic, "kind", "") or "").strip().lower()
            tpl = str(getattr(ic, "template", "") or "").strip()
            required = bool(getattr(ic, "required", False))
            if not id_kind:
                continue
            if not tpl:
                errs.append(constraints_error(
                    "template",
                    "ID kind has no template in constraints.toml",
                    path=template_path,
                    line=1,
                    kit_id=str(kit_id),
                    artifact_kind=kind_u,
                    id_kind=id_kind,
                ))
                continue

            # Distinguish definition placeholders from references.
            occ = _definition_occurrences(tpl)
            if required and not occ:
                errs.append(constraints_error(
                    "template",
                    "Template missing ID placeholder for defined kind",
                    path=template_path,
                    line=1,
                    kit_id=str(kit_id),
                    artifact_kind=kind_u,
                    id_kind=id_kind,
                    id_kind_template=tpl,
                ))
                continue
            if not required and not occ:
                warns.append(constraints_error(
                    "template",
                    "Template missing optional ID placeholder for defined kind",
                    path=template_path,
                    line=1,
                    kit_id=str(kit_id),
                    artifact_kind=kind_u,
                    id_kind=id_kind,
                    id_kind_template=tpl,
                ))
                continue

            allowed_headings = [str(h).strip() for h in (getattr(ic, "headings", None) or []) if str(h).strip()]
            allowed_norm = {h.lower() for h in allowed_headings}
            if allowed_norm and headings_at is not None:
                for ln in occ:
                    active = [str(h).strip() for h in (headings_at[ln] if ln < len(headings_at) else [])]
                    if not any(a.lower() in allowed_norm for a in active):
                        errs.append(constraints_error(
                            "template",
                            "ID placeholder not under required headings",
                            path=template_path,
                            line=ln,
                            kit_id=str(kit_id),
                            artifact_kind=kind_u,
                            id_kind=id_kind,
                            id_kind_template=tpl,
                            headings=sorted(allowed_norm),
                            found_headings=active,
                        ))

        # 2b) Reverse check: every definition/reference pattern in the template must
        #     have its kind registered in constraints.  We extract the kind token from
        #     the template pattern (the first non-placeholder segment after `cpt-{system}-`).
        _TPL_PAT = re.compile(r"`(cpt-[^`]*\{[^`]*)`")

        def _kind_from_pattern(pat: str) -> Optional[str]:
            """Extract ID kind from a template pattern like cpt-{system}-KIND-{slug}."""
            s = pat
            if not s.startswith("cpt-"):
                return None
            s = s[4:]
            # Skip leading placeholder segments like {system}
            while s.startswith("{"):
                end = s.find("}")
                if end < 0:
                    return None
                s = s[end + 1:]
                if s.startswith("-"):
                    s = s[1:]
            # First segment is the kind
            idx = s.find("-")
            token = (s[:idx] if idx >= 0 else s).strip().lower()
            return token if token else None

        known_def_kinds: set[str] = {
            str(getattr(ic, "kind", "") or "").strip().lower()
            for ic in (getattr(constraints_for_kind, "defined_id", None) or [])
            if str(getattr(ic, "kind", "") or "").strip()
        }
        # Collect ALL ID kinds across all artifact kinds (for reference check).
        known_all_kinds: set[str] = set()
        if kit_constraints is not None and getattr(kit_constraints, "by_kind", None):
            for _kk, _kc in kit_constraints.by_kind.items():
                for ic in (getattr(_kc, "defined_id", None) or []):
                    k = str(getattr(ic, "kind", "") or "").strip().lower()
                    if k:
                        known_all_kinds.add(k)

        for idx0, raw in enumerate(lines):
            for m in _TPL_PAT.finditer(raw):
                found = m.group(1)
                found_kind = _kind_from_pattern(found)
                if not found_kind:
                    continue
                is_def_line = "**ID**" in raw
                if is_def_line:
                    if found_kind not in known_def_kinds:
                        errs.append(constraints_error(
                            "template",
                            f"Template has definition `{found}` whose kind `{found_kind}` is not in constraints",
                            code=EC.TEMPLATE_DEF_KIND_NOT_IN_CONSTRAINTS,
                            path=template_path,
                            line=idx0 + 1,
                            kit_id=str(kit_id),
                            artifact_kind=kind_u,
                            id_kind_template=found,
                        ))
                else:
                    if found_kind not in known_all_kinds:
                        errs.append(constraints_error(
                            "template",
                            f"Template has reference `{found}` whose kind `{found_kind}` is not in constraints",
                            code=EC.TEMPLATE_REF_KIND_NOT_IN_CONSTRAINTS,
                            path=template_path,
                            line=idx0 + 1,
                            kit_id=str(kit_id),
                            artifact_kind=kind_u,
                            id_kind_template=found,
                        ))

        # 3) Cross-artifact reference placeholders required by constraints must exist in target templates.
        defined_kinds_here = {
            str(getattr(ic, "kind", "") or "").strip().lower()
            for ic in (getattr(constraints_for_kind, "defined_id", None) or [])
            if str(getattr(ic, "kind", "") or "").strip()
        }

        expectations: Dict[tuple[str, str], Dict[str, object]] = {}
        if kit_constraints is not None and getattr(kit_constraints, "by_kind", None):
            for _src_kind_u, src_c in kit_constraints.by_kind.items():
                for ic in (getattr(src_c, "defined_id", None) or []):
                    id_kind = str(getattr(ic, "kind", "") or "").strip().lower()
                    tpl = str(getattr(ic, "template", "") or "").strip()
                    if not id_kind or not tpl:
                        continue
                    if id_kind in defined_kinds_here:
                        # Avoid double-accounting when the same kind is also defined in this artifact.
                        continue

                    refs = getattr(ic, "references", None) or {}
                    rule = refs.get(kind_u)
                    if rule is None:
                        continue

                    cov = getattr(rule, "coverage", None)  # True=required, False=prohibited, None=optional
                    if cov is False:
                        continue

                    allowed = [str(h).strip() for h in (getattr(rule, "headings", None) or []) if str(h).strip()]
                    key = (id_kind, tpl)
                    if key not in expectations:
                        expectations[key] = {
                            "required": cov is True,
                            "allowed": set(h.lower() for h in allowed),
                        }
                    else:
                        expectations[key]["required"] = bool(expectations[key]["required"]) or (cov is True)
                        expectations[key]["allowed"].update(h.lower() for h in allowed)

        for (id_kind, tpl), ex in expectations.items():
            occ = _occurrences(tpl)
            if bool(ex.get("required")) and not occ:
                errs.append(constraints_error(
                    "template",
                    "Template missing required reference placeholder",
                    path=template_path,
                    line=1,
                    kit_id=str(kit_id),
                    artifact_kind=kind_u,
                    id_kind=id_kind,
                    id_kind_template=tpl,
                ))
                continue
            if not bool(ex.get("required")) and not occ:
                warns.append(constraints_error(
                    "template",
                    "Template missing optional reference placeholder",
                    path=template_path,
                    line=1,
                    kit_id=str(kit_id),
                    artifact_kind=kind_u,
                    id_kind=id_kind,
                    id_kind_template=tpl,
                ))
                continue

            allowed_norm = set(ex.get("allowed") or set())
            # Placement rules for references are enforced only as:
            # - required refs must appear at least once under allowed headings (if specified)
            # - optional refs are allowed anywhere (including outside the allowed headings)
            if bool(ex.get("required")) and occ and allowed_norm and headings_at is not None:
                occ_in_allowed: List[int] = []
                occ_outside_allowed: List[int] = []
                for ln in occ:
                    active = [str(h).strip() for h in (headings_at[ln] if ln < len(headings_at) else [])]
                    if any(a.lower() in allowed_norm for a in active):
                        occ_in_allowed.append(ln)
                    else:
                        occ_outside_allowed.append(ln)
                if not occ_in_allowed:
                    ln = occ_outside_allowed[0] if occ_outside_allowed else 1
                    active0 = [str(h).strip() for h in (headings_at[ln] if ln < len(headings_at) else [])]
                    errs.append(constraints_error(
                        "template",
                        "Required reference placeholder not under required headings",
                        path=template_path,
                        line=ln,
                        kit_id=str(kit_id),
                        artifact_kind=kind_u,
                        id_kind=id_kind,
                        id_kind_template=tpl,
                        headings=sorted(allowed_norm),
                        found_headings=active0,
                    ))

        return {"errors": errs, "warnings": warns}

    results: List[Dict[str, object]] = []
    overall_status = "PASS"
    kits_checked = 0

    kits = getattr(artifacts_meta, "kits", None) or {}
    if not isinstance(kits, dict) or not kits:
        out = {
            "status": "ERROR",
            "message": "No kits defined in artifacts.toml",
            "project_root": project_root.as_posix(),
            "cypilot_dir": adapter_dir.as_posix(),
        }
        return 1, out

    for kit_id, kit_obj in kits.items():
        if kit_filter and str(kit_id) != str(kit_filter):
            continue
        if kit_obj is None:
            continue

        kit_path_str = str(getattr(kit_obj, "path", "") or "").strip()
        if not kit_path_str:
            continue

        kit_base = (project_root / kit_path_str).resolve()
        artifacts_dir = kit_base / "artifacts"
        # NOTE: With explicit kit.artifacts mapping, artifacts_dir may be absent.

        kit_constraints, kit_constraint_errs = load_constraints_toml(kit_base)
        if kit_constraint_errs:
            results.append({
                "kit": kit_id,
                "kind": None,
                "status": "FAIL",
                "error_count": len(kit_constraint_errs),
                "errors": [constraints_error("constraints", "Invalid constraints.toml", path=(kit_base / "constraints.toml"), line=1, errors=list(kit_constraint_errs))],
            })
            overall_status = "FAIL"
            kits_checked += 1
            continue

        kits_checked += 1

        # Determine which kinds to check.
        kinds_to_check: List[str] = []
        explicit_kinds: List[str] = []
        raw_map = getattr(kit_obj, "artifacts", None) or {}
        if isinstance(raw_map, dict) and raw_map:
            explicit_kinds = sorted([str(k).strip() for k in raw_map.keys() if isinstance(k, str) and str(k).strip()])

        if explicit_kinds:
            kinds_to_check = explicit_kinds
        elif artifacts_dir.is_dir():
            kinds_to_check = sorted([p.name for p in artifacts_dir.iterdir() if p.is_dir()])
        else:
            # No explicit mapping and no artifacts/ directory.
            continue

        for kind in kinds_to_check:
            kind = str(kind).strip()
            if not kind:
                continue

            template_path = None
            examples_dir = None
            if kit_obj is not None:
                try:
                    template_path = (project_root / kit_obj.get_template_path(kind)).resolve()
                except Exception:
                    template_path = None
                try:
                    examples_dir = (project_root / kit_obj.get_examples_path(kind)).resolve()
                except Exception:
                    examples_dir = None

            # Fallback to legacy layout if explicit paths are unavailable.
            kind_dir = artifacts_dir / kind
            if template_path is None:
                template_path = (kind_dir / "template.md").resolve()
            if examples_dir is None:
                examples_dir = (kind_dir / "examples").resolve()

            # Pick any .md file in examples directory (not just example.md)
            example_path = None
            try:
                if examples_dir.exists():
                    md_files = list(Path(examples_dir).glob("*.md"))
                    if md_files:
                        example_path = md_files[0]
            except Exception:
                example_path = None

            item: Dict[str, object] = {
                "kit": str(kit_id),
                "kind": kind,
                "example_path": example_path.as_posix() if example_path else None,
                "status": "PASS",
            }

            errs: List[Dict[str, object]] = []
            warns: List[Dict[str, object]] = []

            if template_path is None or not Path(template_path).is_file():
                pth = str(template_path) if template_path is not None else str((kind_dir / "template.md"))
                errs.append({"type": "file", "message": "Template not found", "path": pth})
            else:
                trep = _check_template_constraints_consistency(
                    template_path=Path(template_path),
                    kind=str(kind),
                    kit_id=str(kit_id),
                    kit_base=kit_base,
                    kit_constraints=kit_constraints,
                    artifacts_meta=artifacts_meta,
                )
                errs.extend(list(trep.get("errors", []) or []))
                warns.extend(list(trep.get("warnings", []) or []))

            if not example_path:
                errs.append({"type": "file", "message": "Example not found", "path": str(examples_dir)})
            else:
                constraints_for_kind = None
                if kit_constraints is not None and getattr(kit_constraints, "by_kind", None) and str(kind).upper() in kit_constraints.by_kind:
                    constraints_for_kind = kit_constraints.by_kind[str(kind).upper()]
                constraints_path = None
                try:
                    constraints_path = (kit_base / "constraints.toml").resolve()
                except Exception:
                    constraints_path = None
                rep = validate_artifact_file(
                    artifact_path=example_path,
                    artifact_kind=str(kind),
                    constraints=constraints_for_kind,
                    registered_systems=None,
                    constraints_path=constraints_path,
                    kit_id=str(kit_id),
                )
                errs.extend(list(rep.get("errors", []) or []))
                warns.extend(list(rep.get("warnings", []) or []))

            if errs:
                item["status"] = "FAIL"
                item["error_count"] = len(errs)
                item["errors"] = errs  # Always show errors on failure
                overall_status = "FAIL"
            if warns:
                item["warning_count"] = len(warns)
                if errs or bool(verbose):
                    item["warnings"] = warns  # Show warnings on failure or verbose

            results.append(item)

    out = {
        "status": overall_status,
        "project_root": project_root.as_posix(),
        "cypilot_dir": adapter_dir.as_posix(),
        "kits_checked": kits_checked,
        "templates_checked": len(results),
        "results": results,
    }
    return (0 if overall_status == "PASS" else 2), out


def cmd_self_check(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="self-check", description="Validate kit example artifacts against constraints")
    p.add_argument("--root", default=".", help="Project root to search from (default: current directory)")
    p.add_argument("--kit", "--rule", dest="kit", help="Specific kit ID to check (e.g., cypilot-sdlc)")
    p.add_argument("--verbose", action="store_true", help="Include full per-template error/warning lists")
    args = p.parse_args(argv)

    start_path = Path(args.root).resolve()
    project_root = find_project_root(start_path)
    if project_root is None:
        print(json.dumps({"status": "ERROR", "message": "Project root not found"}, indent=2, ensure_ascii=False))
        return 1

    adapter_dir = find_cypilot_directory(project_root)
    if adapter_dir is None:
        print(json.dumps({"status": "ERROR", "message": "Cypilot not initialized. Run 'cypilot init' first."}, indent=2, ensure_ascii=False))
        return 1

    reg, reg_err = load_artifacts_registry(adapter_dir)
    if reg_err or reg is None:
        print(json.dumps({"status": "ERROR", "message": reg_err or "Missing artifacts registry"}, indent=2, ensure_ascii=False))
        return 1

    # Validate slugs in the registry
    artifacts_meta = ArtifactsMeta.from_dict(reg)
    slug_errors = artifacts_meta.validate_all_slugs()
    if slug_errors:
        print(json.dumps({
            "status": "ERROR",
            "message": "Invalid slugs in artifacts.toml",
            "slug_errors": slug_errors,
        }, indent=2, ensure_ascii=False))
        return 1

    rc, out = run_self_check_from_meta(
        project_root=project_root,
        adapter_dir=adapter_dir,
        artifacts_meta=artifacts_meta,
        kit_filter=str(args.kit) if args.kit else None,
        verbose=bool(args.verbose),
    )
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return rc
