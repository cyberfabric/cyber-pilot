import argparse
import json
from pathlib import Path
from typing import Dict, List

from ..utils.constraints import error as constraints_error


def cmd_validate_kits(argv: List[str]) -> int:
    """Validate Cypilot kit packages.

    Checks that:
    - kits referenced in artifacts.toml are accessible
    - constraints.toml (if present) parses and matches the expected schema
    """
    p = argparse.ArgumentParser(prog="validate-kits", description="Validate Cypilot kit packages")
    p.add_argument("--kit", "--rule", dest="kit", default=None, help="Kit ID to validate (if omitted, validates all kits)")
    p.add_argument("--verbose", action="store_true", help="Print full validation report")
    args = p.parse_args(argv)

    from ..utils.context import get_context
    from ..utils.constraints import load_constraints_toml

    ctx = get_context()
    if not ctx:
        print(json.dumps({"status": "ERROR", "message": "Cypilot not initialized. Run 'cypilot init' first."}, indent=None, ensure_ascii=False))
        return 1

    project_root = ctx.project_root

    kit_reports: List[Dict[str, object]] = []
    all_errors: List[Dict[str, object]] = []

    for kit_id, kit in (ctx.meta.kits or {}).items():
        if args.kit and str(kit_id) != str(args.kit):
            continue
        if not kit.is_cypilot_format():
            continue

        kit_root = (project_root / str(kit.path or "").strip().strip("/")).resolve()
        _kc, kc_errs = load_constraints_toml(kit_root)

        rep: Dict[str, object] = {
            "kit": str(kit_id),
            "path": str(kit_root),
            "status": "PASS" if not kc_errs else "FAIL",
            "error_count": len(kc_errs),
        }
        if kc_errs:
            errs = [constraints_error("constraints", "Invalid constraints.toml", path=(kit_root / "constraints.toml"), line=1, errors=list(kc_errs), kit=str(kit_id))]
            if args.verbose:
                rep["errors"] = errs
            all_errors.extend(errs)
        else:
            if args.verbose and _kc is not None and getattr(_kc, "by_kind", None):
                rep["kinds"] = sorted(_kc.by_kind.keys())

        kit_reports.append(rep)

    overall_status = "PASS" if not all_errors else "FAIL"
    result: Dict[str, object] = {
        "status": overall_status,
        "kits_validated": len(kit_reports),
        "error_count": len(all_errors),
    }

    if args.verbose:
        result["kits"] = kit_reports
        if all_errors:
            result["errors"] = all_errors
    else:
        failed = [r for r in kit_reports if r.get("status") == "FAIL"]
        if failed:
            result["failed_kits"] = [{"kit": r.get("kit"), "error_count": r.get("error_count")} for r in failed]
        if all_errors:
            result["errors"] = all_errors[:10]
            if len(all_errors) > 10:
                result["errors_truncated"] = len(all_errors) - 10

    out = json.dumps(result, indent=2 if args.verbose else None, ensure_ascii=False)
    if args.verbose:
        out += "\n"
    print(out)
    return 0 if overall_status == "PASS" else 2
