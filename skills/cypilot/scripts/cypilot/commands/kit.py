"""
Kit Management Commands

Provides CLI handlers for kit install, kit update, and generate-resources.

@cpt-flow:cpt-cypilot-flow-blueprint-system-kit-install:p1
@cpt-flow:cpt-cypilot-flow-blueprint-system-kit-update:p1
@cpt-flow:cpt-cypilot-flow-blueprint-system-generate-resources:p1
@cpt-flow:cpt-cypilot-flow-blueprint-system-validate-kits:p1
@cpt-dod:cpt-cypilot-dod-blueprint-system-kit-install:p1
@cpt-dod:cpt-cypilot-dod-blueprint-system-kit-update:p1
@cpt-dod:cpt-cypilot-dod-blueprint-system-validate-kits:p1
@cpt-state:cpt-cypilot-state-blueprint-system-kit-install:p1
"""

import argparse
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Kit Install
# ---------------------------------------------------------------------------

def cmd_kit_install(argv: List[str]) -> int:
    """Install a kit from a local path.

    Usage: cypilot kit install <path> [--force]
    """
    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-user-install
    p = argparse.ArgumentParser(prog="kit install", description="Install a kit package")
    p.add_argument("path", help="Path to kit source directory (must contain blueprints/)")
    p.add_argument("--force", action="store_true", help="Overwrite existing kit")
    p.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = p.parse_args(argv)
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-user-install

    from ..utils.blueprint import parse_blueprint
    from ..utils.files import find_project_root, _read_cypilot_var

    kit_source = Path(args.path).resolve()
    blueprints_dir = kit_source / "blueprints"

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-validate-source
    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-if-invalid-source
    if not blueprints_dir.is_dir():
        print(json.dumps({
            "status": "FAIL",
            "message": f"Kit source missing blueprints/ directory: {kit_source}",
            "hint": "Kit must contain a blueprints/ directory with at least one .md file",
        }, indent=2, ensure_ascii=False))
        return 2

    bp_files = list(blueprints_dir.glob("*.md"))
    if not bp_files:
        print(json.dumps({
            "status": "FAIL",
            "message": f"No .md files in {blueprints_dir}",
            "hint": "blueprints/ must contain at least one blueprint .md file",
        }, indent=2, ensure_ascii=False))
        return 2
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-if-invalid-source
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-validate-source

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-extract-metadata
    kit_slug = ""
    kit_version = ""
    for bp_file in bp_files:
        bp = parse_blueprint(bp_file)
        if bp.kit_slug:
            kit_slug = bp.kit_slug
            kit_version = bp.version
            break

    if not kit_slug:
        kit_slug = kit_source.name
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-extract-metadata

    project_root = find_project_root(Path.cwd())
    if project_root is None:
        print(json.dumps({
            "status": "ERROR",
            "message": "No project root found",
            "hint": "Run 'cypilot init' first",
        }, indent=2, ensure_ascii=False))
        return 1

    cypilot_rel = _read_cypilot_var(project_root)
    if not cypilot_rel:
        print(json.dumps({
            "status": "ERROR",
            "message": "No cypilot directory configured",
            "hint": "Run 'cypilot init' first",
        }, indent=2, ensure_ascii=False))
        return 1

    cypilot_dir = (project_root / cypilot_rel).resolve()
    config_dir = cypilot_dir / "config"
    ref_dir = cypilot_dir / "kits" / kit_slug
    user_bp_dir = config_dir / "kits" / kit_slug / "blueprints"

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-if-already-registered
    if ref_dir.exists() and not args.force:
        print(json.dumps({
            "status": "FAIL",
            "message": f"Kit '{kit_slug}' already installed",
            "hint": "Use --force to overwrite",
        }, indent=2, ensure_ascii=False))
        return 2
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-if-already-registered

    if args.dry_run:
        print(json.dumps({
            "status": "DRY_RUN",
            "kit": kit_slug,
            "version": kit_version,
            "source": kit_source.as_posix(),
            "reference": ref_dir.as_posix(),
            "blueprints": user_bp_dir.as_posix(),
        }, indent=2, ensure_ascii=False))
        return 0

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-save-reference
    if ref_dir.exists():
        shutil.rmtree(ref_dir)
    shutil.copytree(kit_source, ref_dir)
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-save-reference

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-copy-blueprints
    if user_bp_dir.exists():
        shutil.rmtree(user_bp_dir)
    user_bp_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(blueprints_dir, user_bp_dir)
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-copy-blueprints

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-process-blueprints
    from ..utils.blueprint import process_kit

    config_kits_dir = config_dir / "kits"
    summary, errors = process_kit(
        kit_slug, user_bp_dir, config_kits_dir, dry_run=False,
    )
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-process-blueprints

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-register-kit
    _register_kit_in_core_toml(config_dir, kit_slug, kit_version, cypilot_dir)
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-register-kit

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-return-install-ok
    # @cpt-begin:cpt-cypilot-state-blueprint-system-kit-install:p1:inst-install-complete
    result: Dict[str, Any] = {
        "status": "PASS" if not errors else "WARN",
        "action": "installed",
        "kit": kit_slug,
        "version": kit_version,
        "files_written": summary.get("files_written", 0),
        "artifact_kinds": summary.get("artifact_kinds", []),
    }
    if errors:
        result["errors"] = errors

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0
    # @cpt-end:cpt-cypilot-state-blueprint-system-kit-install:p1:inst-install-complete
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-return-install-ok


# ---------------------------------------------------------------------------
# Kit Update
# ---------------------------------------------------------------------------

def cmd_kit_update(argv: List[str]) -> int:
    """Update installed kits.

    Usage: cypilot kit update [--force] [--kit SLUG]
    """
    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-user-update
    p = argparse.ArgumentParser(prog="kit update", description="Update installed kits")
    p.add_argument("--kit", default=None, help="Kit slug to update (default: all)")
    p.add_argument("--force", action="store_true", help="Force overwrite user blueprints")
    p.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = p.parse_args(argv)
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-user-update

    from ..utils.files import find_project_root, _read_cypilot_var

    project_root = find_project_root(Path.cwd())
    if project_root is None:
        print(json.dumps({"status": "ERROR", "message": "No project root found"}, ensure_ascii=False))
        return 1

    cypilot_rel = _read_cypilot_var(project_root)
    if not cypilot_rel:
        print(json.dumps({"status": "ERROR", "message": "No cypilot directory"}, ensure_ascii=False))
        return 1

    cypilot_dir = (project_root / cypilot_rel).resolve()
    config_dir = cypilot_dir / "config"
    kits_ref_dir = cypilot_dir / "kits"

    if not kits_ref_dir.is_dir():
        print(json.dumps({
            "status": "FAIL",
            "message": "No kits installed",
            "hint": "Run 'cypilot kit install <path>' first",
        }, indent=2, ensure_ascii=False))
        return 2

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-resolve-kits
    if args.kit:
        kit_dirs = [kits_ref_dir / args.kit]
        if not kit_dirs[0].is_dir():
            print(json.dumps({
                "status": "FAIL",
                "message": f"Kit '{args.kit}' not found in {kits_ref_dir}",
            }, indent=2, ensure_ascii=False))
            return 2
    else:
        kit_dirs = [d for d in sorted(kits_ref_dir.iterdir()) if d.is_dir()]

    if not kit_dirs:
        print(json.dumps({"status": "FAIL", "message": "No kits found"}, ensure_ascii=False))
        return 2
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-resolve-kits

    from ..utils.blueprint import process_kit

    results: List[Dict[str, Any]] = []
    all_errors: List[str] = []

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-foreach-kit
    # @cpt-begin:cpt-cypilot-state-blueprint-system-kit-install:p1:inst-version-drift
    for kit_dir in kit_dirs:
        kit_slug = kit_dir.name

        # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-load-new-source
        ref_bp_dir = kit_dir / "blueprints"
        user_bp_dir = config_dir / "kits" / kit_slug / "blueprints"

        if not ref_bp_dir.is_dir():
            all_errors.append(f"Kit '{kit_slug}' has no blueprints/ in reference")
            continue
        # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-load-new-source

        # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-if-force
        # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-force-overwrite
        if args.force:
            if not args.dry_run:
                if user_bp_dir.exists():
                    shutil.rmtree(user_bp_dir)
                user_bp_dir.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(ref_bp_dir, user_bp_dir)
        # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-force-overwrite
        # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-if-force

        # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-regenerate
        source_bp_dir = user_bp_dir if user_bp_dir.is_dir() else ref_bp_dir
        config_kits_dir = config_dir / "kits"

        if args.dry_run:
            results.append({"kit": kit_slug, "action": "dry_run"})
        else:
            summary, errors = process_kit(
                kit_slug, source_bp_dir, config_kits_dir, dry_run=False,
            )
            results.append({
                "kit": kit_slug,
                "action": "force_updated" if args.force else "regenerated",
                "files_written": summary.get("files_written", 0),
                "artifact_kinds": summary.get("artifact_kinds", []),
            })
            all_errors.extend(errors)
        # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-regenerate
    # @cpt-end:cpt-cypilot-state-blueprint-system-kit-install:p1:inst-version-drift
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-foreach-kit

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-update-version
    # (version updated implicitly during process_kit regeneration)
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-update-version

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-return-update-ok
    # @cpt-begin:cpt-cypilot-state-blueprint-system-kit-install:p1:inst-update-complete
    overall = "PASS" if not all_errors else "WARN"
    output: Dict[str, Any] = {
        "status": overall,
        "kits_updated": len(results),
        "results": results,
    }
    if all_errors:
        output["errors"] = all_errors

    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0
    # @cpt-end:cpt-cypilot-state-blueprint-system-kit-install:p1:inst-update-complete
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-return-update-ok


# ---------------------------------------------------------------------------
# Generate Resources
# ---------------------------------------------------------------------------

def cmd_generate_resources(argv: List[str]) -> int:
    """Regenerate kit resources from blueprints.

    Usage: cypilot generate-resources [--kit SLUG]
    """
    # @cpt-begin:cpt-cypilot-flow-blueprint-system-generate-resources:p1:inst-user-generate
    p = argparse.ArgumentParser(prog="generate-resources", description="Regenerate kit resources from blueprints")
    p.add_argument("--kit", default=None, help="Kit slug (default: all)")
    p.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = p.parse_args(argv)
    # @cpt-end:cpt-cypilot-flow-blueprint-system-generate-resources:p1:inst-user-generate

    from ..utils.files import find_project_root, _read_cypilot_var

    project_root = find_project_root(Path.cwd())
    if project_root is None:
        print(json.dumps({"status": "ERROR", "message": "No project root found"}, ensure_ascii=False))
        return 1

    cypilot_rel = _read_cypilot_var(project_root)
    if not cypilot_rel:
        print(json.dumps({"status": "ERROR", "message": "No cypilot directory"}, ensure_ascii=False))
        return 1

    cypilot_dir = (project_root / cypilot_rel).resolve()
    config_dir = cypilot_dir / "config"
    config_kits_dir = config_dir / "kits"

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-generate-resources:p1:inst-resolve-gen-kits
    if args.kit:
        bp_dirs = [(args.kit, config_kits_dir / args.kit / "blueprints")]
    else:
        bp_dirs = []
        if config_kits_dir.is_dir():
            for kit_dir in sorted(config_kits_dir.iterdir()):
                bp_dir = kit_dir / "blueprints"
                if bp_dir.is_dir():
                    bp_dirs.append((kit_dir.name, bp_dir))

    if not bp_dirs:
        print(json.dumps({
            "status": "FAIL",
            "message": "No kits with blueprints found",
            "hint": "Run 'cypilot kit install <path>' first",
        }, indent=2, ensure_ascii=False))
        return 2
    # @cpt-end:cpt-cypilot-flow-blueprint-system-generate-resources:p1:inst-resolve-gen-kits

    from ..utils.blueprint import process_kit

    results: List[Dict[str, Any]] = []
    all_errors: List[str] = []

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-generate-resources:p1:inst-foreach-gen-kit
    for kit_slug, bp_dir in bp_dirs:
        if not bp_dir.is_dir():
            all_errors.append(f"Kit '{kit_slug}' blueprints directory not found: {bp_dir}")
            continue

        # @cpt-begin:cpt-cypilot-flow-blueprint-system-generate-resources:p1:inst-gen-process
        summary, errors = process_kit(
            kit_slug, bp_dir, config_kits_dir, dry_run=args.dry_run,
        )
        results.append({
            "kit": kit_slug,
            "files_written": summary.get("files_written", 0),
            "artifact_kinds": summary.get("artifact_kinds", []),
        })
        all_errors.extend(errors)
        # @cpt-end:cpt-cypilot-flow-blueprint-system-generate-resources:p1:inst-gen-process
    # @cpt-end:cpt-cypilot-flow-blueprint-system-generate-resources:p1:inst-foreach-gen-kit

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-generate-resources:p1:inst-return-gen-ok
    overall = "PASS" if not all_errors else "WARN"
    output: Dict[str, Any] = {
        "status": overall,
        "kits_processed": len(results),
        "results": results,
    }
    if all_errors:
        output["errors"] = all_errors

    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0
    # @cpt-end:cpt-cypilot-flow-blueprint-system-generate-resources:p1:inst-return-gen-ok


# ---------------------------------------------------------------------------
# Validate Kits (enhanced with blueprint validation)
# ---------------------------------------------------------------------------

def cmd_validate_kits_blueprints(argv: List[str]) -> int:
    """Validate kit blueprints (structural validation).

    Checks blueprints/ directory, marker syntax, @cpt:blueprint identity.
    This is called as a sub-check within the existing validate-kits flow.

    Usage: cypilot validate-kits --blueprints
    """
    # @cpt-begin:cpt-cypilot-flow-blueprint-system-validate-kits:p1:inst-user-validate-kits
    from ..utils.files import find_project_root, _read_cypilot_var
    from ..utils.blueprint import parse_blueprint

    project_root = find_project_root(Path.cwd())
    if project_root is None:
        print(json.dumps({"status": "ERROR", "message": "No project root found"}, ensure_ascii=False))
        return 1

    cypilot_rel = _read_cypilot_var(project_root)
    if not cypilot_rel:
        print(json.dumps({"status": "ERROR", "message": "No cypilot directory"}, ensure_ascii=False))
        return 1

    cypilot_dir = (project_root / cypilot_rel).resolve()
    config_dir = cypilot_dir / "config"
    config_kits_dir = config_dir / "kits"
    # @cpt-end:cpt-cypilot-flow-blueprint-system-validate-kits:p1:inst-user-validate-kits

    kit_reports: List[Dict[str, Any]] = []
    all_errors: List[str] = []

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-validate-kits:p1:inst-load-registered-kits
    if not config_kits_dir.is_dir():
        print(json.dumps({
            "status": "PASS",
            "kits_validated": 0,
            "message": "No kits directory found",
        }, indent=2, ensure_ascii=False))
        return 0
    # @cpt-end:cpt-cypilot-flow-blueprint-system-validate-kits:p1:inst-load-registered-kits

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-validate-kits:p1:inst-foreach-validate-kit
    for kit_dir in sorted(config_kits_dir.iterdir()):
        if not kit_dir.is_dir():
            continue
        kit_slug = kit_dir.name
        bp_dir = kit_dir / "blueprints"

        report: Dict[str, Any] = {"kit": kit_slug}
        kit_errors: List[str] = []

        # @cpt-begin:cpt-cypilot-flow-blueprint-system-validate-kits:p1:inst-verify-blueprints-dir
        if not bp_dir.is_dir():
            kit_errors.append(f"Kit '{kit_slug}' missing blueprints/ directory")
            report["status"] = "FAIL"
            report["errors"] = kit_errors
            all_errors.extend(kit_errors)
            kit_reports.append(report)
            continue

        bp_files = list(bp_dir.glob("*.md"))
        if not bp_files:
            kit_errors.append(f"Kit '{kit_slug}' blueprints/ directory is empty")
            report["status"] = "FAIL"
            report["errors"] = kit_errors
            all_errors.extend(kit_errors)
            kit_reports.append(report)
            continue
        # @cpt-end:cpt-cypilot-flow-blueprint-system-validate-kits:p1:inst-verify-blueprints-dir

        has_identity = False
        artifact_kinds: List[str] = []

        # @cpt-begin:cpt-cypilot-flow-blueprint-system-validate-kits:p1:inst-foreach-blueprint
        for bp_file in bp_files:
            # @cpt-begin:cpt-cypilot-flow-blueprint-system-validate-kits:p1:inst-validate-markers
            bp = parse_blueprint(bp_file)
            kit_errors.extend(bp.errors)
            # @cpt-end:cpt-cypilot-flow-blueprint-system-validate-kits:p1:inst-validate-markers

            # @cpt-begin:cpt-cypilot-flow-blueprint-system-validate-kits:p1:inst-verify-identity
            has_bp_marker = any(m.marker_type == "blueprint" for m in bp.markers)
            if has_bp_marker:
                has_identity = True
            # @cpt-end:cpt-cypilot-flow-blueprint-system-validate-kits:p1:inst-verify-identity

            # @cpt-begin:cpt-cypilot-flow-blueprint-system-validate-kits:p1:inst-verify-content
            has_content = any(
                m.marker_type in ("heading", "rule", "check", "rules", "checklist", "prompt", "example")
                for m in bp.markers
            )
            if not has_content and not bp.errors:
                kit_errors.append(
                    f"{bp_file.name}: no content markers found "
                    f"(expected @cpt:heading, @cpt:rule, @cpt:check, etc.)"
                )
            # @cpt-end:cpt-cypilot-flow-blueprint-system-validate-kits:p1:inst-verify-content

            if bp.artifact_kind:
                artifact_kinds.append(bp.artifact_kind)
        # @cpt-end:cpt-cypilot-flow-blueprint-system-validate-kits:p1:inst-foreach-blueprint

        if not has_identity:
            kit_errors.append(
                f"Kit '{kit_slug}': no blueprint has @cpt:blueprint identity marker"
            )

        report["artifact_kinds"] = artifact_kinds
        report["blueprints_count"] = len(bp_files)
        if kit_errors:
            report["status"] = "FAIL"
            report["errors"] = kit_errors
            all_errors.extend(kit_errors)
        else:
            report["status"] = "PASS"

        kit_reports.append(report)
    # @cpt-end:cpt-cypilot-flow-blueprint-system-validate-kits:p1:inst-foreach-validate-kit

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-validate-kits:p1:inst-return-validate-ok
    overall = "PASS" if not all_errors else "FAIL"
    output: Dict[str, Any] = {
        "status": overall,
        "kits_validated": len(kit_reports),
        "error_count": len(all_errors),
        "kits": kit_reports,
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0 if overall == "PASS" else 2
    # @cpt-end:cpt-cypilot-flow-blueprint-system-validate-kits:p1:inst-return-validate-ok


# ---------------------------------------------------------------------------
# Kit CLI dispatcher (handles `cypilot kit <subcommand>`)
# ---------------------------------------------------------------------------

def cmd_kit(argv: List[str]) -> int:
    """Kit management command dispatcher.

    Usage: cypilot kit <install|update> [options]
    """
    if not argv:
        print(json.dumps({
            "status": "ERROR",
            "message": "Missing kit subcommand",
            "subcommands": ["install", "update"],
        }, indent=None, ensure_ascii=False))
        return 1

    subcmd = argv[0]
    rest = argv[1:]

    if subcmd == "install":
        return cmd_kit_install(rest)
    elif subcmd == "update":
        return cmd_kit_update(rest)
    else:
        print(json.dumps({
            "status": "ERROR",
            "message": f"Unknown kit subcommand: {subcmd}",
            "subcommands": ["install", "update"],
        }, indent=None, ensure_ascii=False))
        return 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _register_kit_in_core_toml(
    config_dir: Path,
    kit_slug: str,
    kit_version: str,
    cypilot_dir: Path,
) -> None:
    """Register or update a kit entry in config/core.toml."""
    core_toml = config_dir / "core.toml"
    if not core_toml.is_file():
        return

    try:
        import tomllib
        with open(core_toml, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return

    kits = data.setdefault("kits", {})
    kits[kit_slug] = {
        "format": "Cypilot",
        "path": f"{cypilot_dir.name}/kits/{kit_slug}",
    }
    if kit_version:
        kits[kit_slug]["version"] = kit_version

    # Write back using our TOML serializer
    try:
        from ..utils import toml_utils
        toml_utils.dump(data, core_toml, header_comment="Cypilot project configuration")
    except Exception:
        pass
