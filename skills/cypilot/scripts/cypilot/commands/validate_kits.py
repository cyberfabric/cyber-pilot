"""
Validate Kits Command — validate kit structure, templates, and examples.

Kits are direct file packages — validation checks kit directory presence,
conf.toml readability, constraints.toml schema, and template/example
consistency against constraints.
"""

# @cpt-begin:cpt-cypilot-flow-kit-validate-cli:p1:inst-validate-kits-imports
import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..utils.constraints import error as constraints_error
from ..utils.ui import ui
# @cpt-end:cpt-cypilot-flow-kit-validate-cli:p1:inst-validate-kits-imports


# @cpt-dod:cpt-cypilot-dod-kit-validate:p1
# @cpt-algo:cpt-cypilot-algo-kit-validate:p1
def run_validate_kits(
    *,
    project_root: Path,
    adapter_dir: Path,
    kit_filter: Optional[str] = None,
    verbose: bool = False,
) -> Tuple[int, Dict[str, Any]]:
    """Run full kit validation (structural + template/example checks).

    Returns (return_code, report_dict).  rc=0 means PASS, rc=2 means FAIL.
    This is the reusable engine called by both the CLI and ``cmd_update``.
    """
    # @cpt-begin:cpt-cypilot-algo-kit-validate:p1:inst-init-context
    from ..utils.context import get_context
    from ..utils.constraints import load_constraints_toml
    from ..utils.artifacts_meta import load_artifacts_meta

    ctx = get_context()
    if not ctx:
        return 1, {"status": "ERROR", "message": "Cypilot not initialized. Run 'cypilot init' first."}
    # @cpt-end:cpt-cypilot-algo-kit-validate:p1:inst-init-context

    # @cpt-begin:cpt-cypilot-algo-kit-validate:p1:inst-structural-check
    # ── Phase 1: Structural validation ────────────────────────────────
    kit_reports: List[Dict[str, object]] = []
    all_errors: List[Dict[str, object]] = []

    for kit_id, kit in (ctx.meta.kits or {}).items():
        if kit_filter and str(kit_id) != str(kit_filter):
            continue
        if not kit.is_cypilot_format():
            continue

        kit_root = (project_root / str(kit.path or "").strip().strip("/")).resolve()
        config_kit_dir = adapter_dir / "config" / "kits" / str(kit_id)
        _has_kit_dir = config_kit_dir.is_dir()

        _kc, kc_errs = load_constraints_toml(kit_root)

        rep: Dict[str, object] = {
            "kit": str(kit_id),
            "path": str(kit_root),
            "status": "PASS" if not kc_errs else "FAIL",
            "error_count": len(kc_errs),
        }
        if kc_errs:
            errs = [constraints_error("constraints", "Invalid constraints.toml", path=(kit_root / "constraints.toml"), line=1, errors=list(kc_errs), kit=str(kit_id))]
            if verbose:
                rep["errors"] = errs
            all_errors.extend(errs)
        else:
            if verbose and _kc is not None and getattr(_kc, "by_kind", None):
                rep["kinds"] = sorted(_kc.by_kind.keys())

        kit_reports.append(rep)
    # @cpt-end:cpt-cypilot-algo-kit-validate:p1:inst-structural-check

    # @cpt-begin:cpt-cypilot-algo-kit-validate:p1:inst-template-check
    # ── Phase 2: Template & example validation ────────────────────────
    # @cpt-begin:cpt-cypilot-flow-developer-experience-self-check:p1:inst-load-registry
    self_check_report: Dict[str, object] = {}
    artifacts_meta, meta_err = load_artifacts_meta(adapter_dir)
    # @cpt-end:cpt-cypilot-flow-developer-experience-self-check:p1:inst-load-registry
    if artifacts_meta is not None and not meta_err:
        from .self_check import run_self_check_from_meta
        _, sc_out = run_self_check_from_meta(
            project_root=project_root,
            adapter_dir=adapter_dir,
            artifacts_meta=artifacts_meta,
            kit_filter=kit_filter,
            verbose=verbose,
        )
        self_check_report = sc_out
        sc_results = sc_out.get("results", [])
        for r in sc_results:
            if r.get("status") == "FAIL":
                sc_errs = r.get("errors", [])
                all_errors.extend(sc_errs)
    # @cpt-end:cpt-cypilot-algo-kit-validate:p1:inst-template-check

    # @cpt-begin:cpt-cypilot-algo-kit-validate:p1:inst-build-result
    # ── Build result ──────────────────────────────────────────────────
    overall_status = "PASS" if not all_errors else "FAIL"
    result: Dict[str, Any] = {
        "status": overall_status,
        "kits_validated": len(kit_reports),
        "error_count": len(all_errors),
    }

    if self_check_report:
        result["templates_checked"] = self_check_report.get("templates_checked", 0)
        result["self_check_results"] = self_check_report.get("results", [])

    if verbose:
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

    return (0 if overall_status == "PASS" else 2), result
    # @cpt-end:cpt-cypilot-algo-kit-validate:p1:inst-build-result


# @cpt-flow:cpt-cypilot-flow-kit-validate-cli:p1
def cmd_validate_kits(argv: List[str]) -> int:
    """Validate Cypilot kit packages (CLI entry point)."""
    # @cpt-begin:cpt-cypilot-flow-kit-validate-cli:p1:inst-parse-args
    p = argparse.ArgumentParser(prog="validate-kits", description="Validate kit structure, templates, and examples")
    p.add_argument("path", nargs="?", default=None, help="Path to a kit directory to validate (e.g. kits/sdlc). If omitted, validates registered kits.")
    p.add_argument("--kit", "--rule", dest="kit", default=None, help="Kit ID to validate (if omitted, validates all kits)")
    p.add_argument("--verbose", action="store_true", help="Print full validation report")
    args = p.parse_args(argv)
    # @cpt-end:cpt-cypilot-flow-kit-validate-cli:p1:inst-parse-args

    # @cpt-begin:cpt-cypilot-flow-kit-validate-cli:p1:inst-path-mode
    if args.path:
        rc, result = _validate_kit_by_path(Path(args.path), verbose=bool(args.verbose))
        ui.result(result, human_fn=lambda d: _human_validate_kits(d))
        return rc
    # @cpt-end:cpt-cypilot-flow-kit-validate-cli:p1:inst-path-mode

    # @cpt-begin:cpt-cypilot-flow-kit-validate-cli:p1:inst-registered-mode
    from ..utils.context import get_context
    ctx = get_context()
    if not ctx:
        ui.result({"status": "ERROR", "message": "Cypilot not initialized. Run 'cypilot init' first."})
        return 1

    rc, result = run_validate_kits(
        project_root=ctx.project_root,
        adapter_dir=ctx.adapter_dir,
        kit_filter=str(args.kit) if args.kit else None,
        verbose=bool(args.verbose),
    )
    # @cpt-end:cpt-cypilot-flow-kit-validate-cli:p1:inst-registered-mode

    # @cpt-begin:cpt-cypilot-flow-kit-validate-cli:p1:inst-output-result
    ui.result(result, human_fn=lambda d: _human_validate_kits(d))
    return rc
    # @cpt-end:cpt-cypilot-flow-kit-validate-cli:p1:inst-output-result


# @cpt-algo:cpt-cypilot-algo-kit-validate-by-path:p1
def _validate_kit_by_path(kit_path: Path, *, verbose: bool = False) -> Tuple[int, Dict[str, Any]]:
    """Validate a standalone kit directory (not necessarily registered in config)."""
    # @cpt-begin:cpt-cypilot-algo-kit-validate-by-path:p1:inst-resolve-dir
    from ..utils.constraints import load_constraints_toml
    from ..utils.artifacts_meta import ArtifactsMeta

    kit_dir = Path(kit_path).resolve()
    if not kit_dir.is_dir():
        return 1, {"status": "ERROR", "message": f"Kit directory not found: {kit_dir}"}

    # Derive slug from directory name
    slug = kit_dir.name
    # @cpt-end:cpt-cypilot-algo-kit-validate-by-path:p1:inst-resolve-dir

    # @cpt-begin:cpt-cypilot-algo-kit-validate-by-path:p1:inst-structural-check
    # ── Phase 1: Structural — constraints.toml ────────────────────────
    all_errors: List[Dict[str, object]] = []
    _kc, kc_errs = load_constraints_toml(kit_dir)

    kit_report: Dict[str, object] = {
        "kit": slug,
        "path": str(kit_dir),
        "status": "PASS" if not kc_errs else "FAIL",
        "error_count": len(kc_errs),
    }
    if kc_errs:
        errs = [constraints_error("constraints", "Invalid constraints.toml", path=(kit_dir / "constraints.toml"), line=1, errors=list(kc_errs), kit=slug)]
        if verbose:
            kit_report["errors"] = errs
        all_errors.extend(errs)
    else:
        if verbose and _kc is not None and getattr(_kc, "by_kind", None):
            kit_report["kinds"] = sorted(_kc.by_kind.keys())
    # @cpt-end:cpt-cypilot-algo-kit-validate-by-path:p1:inst-structural-check

    # @cpt-begin:cpt-cypilot-algo-kit-validate-by-path:p1:inst-build-artifacts-meta
    # ── Phase 2: Template & example validation ────────────────────────
    # Build a synthetic ArtifactsMeta so run_self_check_from_meta can work
    artifacts_dict: Dict[str, Dict[str, str]] = {}
    artifacts_dir = kit_dir / "artifacts"
    if artifacts_dir.is_dir():
        for kind_dir in sorted(artifacts_dir.iterdir()):
            if not kind_dir.is_dir():
                continue
            kind = kind_dir.name
            tpl = kind_dir / "template.md"
            examples = kind_dir / "examples"
            if tpl.is_file():
                artifacts_dict[kind] = {
                    "template": str(tpl),
                    "examples": str(examples),  # path may not exist; self_check handles that
                }

    meta = ArtifactsMeta.from_dict({
        "version": "1.1",
        "project_root": str(kit_dir.parent),
        "kits": {slug: {"format": "Cypilot", "path": str(kit_dir), "artifacts": artifacts_dict}},
    })
    # @cpt-end:cpt-cypilot-algo-kit-validate-by-path:p1:inst-build-artifacts-meta

    # @cpt-begin:cpt-cypilot-algo-kit-validate-by-path:p1:inst-template-check
    self_check_report: Dict[str, object] = {}
    if not kc_errs:  # Only run template checks if constraints parsed OK
        from .self_check import run_self_check_from_meta
        _, sc_out = run_self_check_from_meta(
            project_root=kit_dir.parent,
            adapter_dir=kit_dir.parent,
            artifacts_meta=meta,
            kit_filter=slug,
            verbose=verbose,
        )
        self_check_report = sc_out
        for r in sc_out.get("results", []):
            if r.get("status") == "FAIL":
                all_errors.extend(r.get("errors", []))
    # @cpt-end:cpt-cypilot-algo-kit-validate-by-path:p1:inst-template-check

    # @cpt-begin:cpt-cypilot-algo-kit-validate-by-path:p1:inst-build-result
    # ── Build result ──────────────────────────────────────────────────
    overall_status = "PASS" if not all_errors else "FAIL"
    result: Dict[str, Any] = {
        "status": overall_status,
        "kits_validated": 1,
        "error_count": len(all_errors),
    }
    if self_check_report:
        result["templates_checked"] = self_check_report.get("templates_checked", 0)
        result["self_check_results"] = self_check_report.get("results", [])
    if verbose:
        result["kits"] = [kit_report]
        if all_errors:
            result["errors"] = all_errors
    else:
        if all_errors:
            result["errors"] = all_errors[:10]
            if len(all_errors) > 10:
                result["errors_truncated"] = len(all_errors) - 10

    return (0 if overall_status == "PASS" else 2), result
    # @cpt-end:cpt-cypilot-algo-kit-validate-by-path:p1:inst-build-result

# @cpt-begin:cpt-cypilot-flow-kit-validate-cli:p1:inst-validate-kits-format
def _show_error(e: object, *, prefix: str = "\u2717") -> None:
    """Display a single error/warning dict with nested details."""
    if not isinstance(e, dict):
        ui.substep(f"  {prefix} {e}")
        return
    msg = e.get("message", "")
    path = ui.relpath(str(e.get("path", ""))) if e.get("path") else ""
    line = e.get("line", "")
    loc = f"{path}:{line}" if path and line else (path or "")
    # Add context fields when available (id_kind, artifact_kind)
    ctx_parts: List[str] = []
    if e.get("artifact_kind"):
        ctx_parts.append(str(e["artifact_kind"]))
    if e.get("id_kind"):
        ctx_parts.append(f"id={e['id_kind']}")
    if e.get("id_kind_template"):
        ctx_parts.append(f"tpl={e['id_kind_template']}")
    ctx = f" [{', '.join(ctx_parts)}]" if ctx_parts else ""
    # Show the main message
    if loc:
        ui.substep(f"  {prefix} {loc}  {msg}{ctx}")
    else:
        ui.substep(f"  {prefix} {msg}{ctx}")
    # Show nested error details (e.g. from constraints parsing)
    for detail in (e.get("errors") or []):
        ui.substep(f"      {detail}")


def _human_validate_kits(data: dict) -> None:
    ui.header("Validate Kits")
    n = data.get("kits_validated", 0)
    n_err = data.get("error_count", 0)
    n_tpl = data.get("templates_checked", 0)
    ui.detail("Kits validated", str(n))
    if n_tpl:
        ui.detail("Templates checked", str(n_tpl))
    ui.detail("Errors", str(n_err))

    # Verbose mode: full kit reports (structural)
    for k in data.get("kits", []):
        kit_id = k.get("kit", "?")
        status = k.get("status", "?")
        kinds = k.get("kinds", [])
        if status == "PASS":
            kind_str = f"  ({', '.join(kinds)})" if kinds else ""
            ui.step(f"{kit_id}: PASS{kind_str}")
        else:
            ui.warn(f"{kit_id}: {status} ({k.get('error_count', 0)} errors)")
            for e in k.get("errors", [])[:10]:
                _show_error(e)

    # Template/example validation results (self-check)
    sc_results = data.get("self_check_results", [])
    if sc_results:
        ui.blank()
        ui.substep("Templates & examples:")
        for r in sc_results:
            kit_id = r.get("kit") or "?"
            kind = r.get("kind") or "?"
            rs = r.get("status", "?")
            n_r_err = r.get("error_count", 0)
            n_r_warn = r.get("warning_count", 0)
            if rs == "PASS":
                suffix = ""
                if n_r_warn:
                    suffix = f" ({n_r_warn} warning(s))"
                    if not data.get("kits"):  # non-verbose
                        suffix += " — use --verbose for details"
                ui.step(f"{kit_id}/{kind}: PASS{suffix}")
            else:
                ui.warn(f"{kit_id}/{kind}: {rs} — {n_r_err} error(s), {n_r_warn} warning(s)")
            for e in r.get("errors", [])[:10]:
                _show_error(e)
            for w in r.get("warnings", [])[:10]:
                _show_error(w, prefix="⚠")

    # Non-verbose mode: show top-level errors only if not already shown via sc_results
    if not data.get("kits") and not sc_results:
        failed = data.get("failed_kits", [])
        if failed:
            ui.blank()
            for fk in failed:
                ui.warn(f"{fk.get('kit', '?')}: {fk.get('error_count', 0)} error(s)")
        for e in (data.get("errors") or [])[:10]:
            _show_error(e)
        truncated = data.get("errors_truncated", 0)
        if truncated:
            ui.substep(f"  ... and {truncated} more error(s)")

    overall = data.get("status", "")
    ui.blank()
    if overall == "PASS":
        ui.success(f"{n} kit(s) validated, all passed.")
    else:
        ui.error(f"{n} kit(s) validated, {n_err} error(s).")
    ui.blank()
# @cpt-end:cpt-cypilot-flow-kit-validate-cli:p1:inst-validate-kits-format
