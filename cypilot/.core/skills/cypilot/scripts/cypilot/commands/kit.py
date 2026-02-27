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


# Subdirectories to copy from kit source (reference + install)
KIT_COPY_SUBDIRS = ["blueprints", "scripts"]


# ---------------------------------------------------------------------------
# Core kit installation logic (used by both cmd_kit_install and init)
# ---------------------------------------------------------------------------

def install_kit(
    kit_source: Path,
    cypilot_dir: Path,
    kit_slug: str,
    kit_version: str = "",
) -> Dict[str, Any]:
    """Install a kit: copy blueprints+scripts, process, generate outputs.

    Copies only blueprints/ and scripts/ from kit_source.
    Caller is responsible for validation and dry-run checks.

    Args:
        kit_source: Kit source directory (must contain blueprints/).
        cypilot_dir: Resolved project cypilot directory.
        kit_slug: Kit identifier.
        kit_version: Kit version string.

    Returns:
        Dict with: status, kit, version, files_written, artifact_kinds,
        errors, actions, skill_nav, sysprompt_content.
    """
    config_dir = cypilot_dir / "config"
    gen_dir = cypilot_dir / ".gen"
    ref_dir = cypilot_dir / "kits" / kit_slug
    user_bp_dir = config_dir / "kits" / kit_slug / "blueprints"
    gen_kits_dir = gen_dir / "kits"
    blueprints_dir = kit_source / "blueprints"
    scripts_dir = kit_source / "scripts"

    actions: Dict[str, str] = {}
    errors: List[str] = []

    if not blueprints_dir.is_dir():
        return {
            "status": "FAIL",
            "kit": kit_slug,
            "errors": [f"Kit source missing blueprints/: {kit_source}"],
        }

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-save-reference
    # Save reference (only blueprints + scripts)
    for subdir_name in KIT_COPY_SUBDIRS:
        src = kit_source / subdir_name
        dst = ref_dir / subdir_name
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dst)
            actions[f"ref_{subdir_name}"] = "copied"
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-save-reference

    # Copy conf.toml to reference and config/kits/{slug}/
    conf_src = kit_source / "conf.toml"
    if conf_src.is_file():
        ref_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(conf_src, ref_dir / "conf.toml")
        user_kit_dir = config_dir / "kits" / kit_slug
        user_kit_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(conf_src, user_kit_dir / "conf.toml")
        actions["conf_toml"] = "copied"
        # Read kit version from conf.toml if not provided
        if not kit_version:
            kit_version = _read_kit_version(conf_src)

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-copy-blueprints
    # Copy blueprints to config/kits/{slug}/blueprints/ (user-editable)
    if user_bp_dir.exists():
        shutil.rmtree(user_bp_dir)
    user_bp_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(blueprints_dir, user_bp_dir)
    actions["user_blueprints"] = "copied"
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-copy-blueprints

    # Copy scripts to .gen/kits/{slug}/scripts/
    if scripts_dir.is_dir():
        gen_kit_scripts = gen_kits_dir / kit_slug / "scripts"
        if gen_kit_scripts.exists():
            shutil.rmtree(gen_kit_scripts)
        gen_kit_scripts.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(scripts_dir, gen_kit_scripts)
        actions["gen_scripts"] = "copied"

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-process-blueprints
    # Process blueprints → generate resources into .gen/kits/{slug}/
    from ..utils.blueprint import process_kit

    summary, kit_errors = process_kit(
        kit_slug, user_bp_dir, gen_kits_dir, dry_run=False,
    )
    errors.extend(kit_errors)
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-process-blueprints

    # Write per-kit SKILL.md into .gen/kits/{slug}/SKILL.md
    skill_nav = ""
    skill_content = summary.get("skill_content", "")
    if skill_content:
        gen_kit_skill_path = gen_kits_dir / kit_slug / "SKILL.md"
        gen_kit_skill_path.parent.mkdir(parents=True, exist_ok=True)
        art_kinds = [k.upper() for k in summary.get("artifact_kinds", []) if k]
        wf_names = [w["name"] for w in summary.get("workflows", []) if w.get("name")]
        desc_parts: list[str] = []
        if art_kinds:
            desc_parts.append(f"Artifacts: {', '.join(art_kinds)}")
        if wf_names:
            desc_parts.append(f"Workflows: {', '.join(wf_names)}")
        kit_description = "; ".join(desc_parts) if desc_parts else f"Kit {kit_slug}"
        gen_kit_skill_path.write_text(
            f"---\nname: cypilot-{kit_slug}\n"
            f"description: \"{kit_description}\"\n---\n\n"
            f"# Cypilot Skill — Kit `{kit_slug}`\n\n"
            f"Generated from kit `{kit_slug}` blueprints.\n\n"
            + skill_content + "\n",
            encoding="utf-8",
        )
        skill_nav = f"ALWAYS invoke `{{cypilot_path}}/.gen/kits/{kit_slug}/SKILL.md` FIRST"
        actions["gen_kit_skill"] = "created"

    # Write generated workflows into .gen/kits/{slug}/workflows/{name}.md
    kit_workflows = summary.get("workflows", [])
    for wf in kit_workflows:
        wf_name = wf["name"]
        wf_path = gen_kits_dir / kit_slug / "workflows" / f"{wf_name}.md"
        wf_path.parent.mkdir(parents=True, exist_ok=True)
        fm_lines = [
            "---",
            "cypilot: true",
            "type: workflow",
            f"name: cypilot-{wf_name}",
        ]
        if wf.get("description"):
            fm_lines.append(f"description: {wf['description']}")
        if wf.get("version"):
            fm_lines.append(f"version: {wf['version']}")
        if wf.get("purpose"):
            fm_lines.append(f"purpose: {wf['purpose']}")
        fm_lines.append("---")
        frontmatter = "\n".join(fm_lines)
        wf_path.write_text(
            frontmatter + "\n\n" + wf["content"] + "\n",
            encoding="utf-8",
        )
        actions[f"gen_workflow_{wf_name}"] = "created"

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-register-kit
    # Register in core.toml
    _register_kit_in_core_toml(config_dir, kit_slug, kit_version, cypilot_dir)
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-register-kit

    return {
        "status": "PASS" if not errors else "WARN",
        "action": "installed",
        "kit": kit_slug,
        "version": kit_version,
        "files_written": summary.get("files_written", 0),
        "artifact_kinds": summary.get("artifact_kinds", []),
        "errors": errors,
        "skill_nav": skill_nav,
        "sysprompt_content": summary.get("sysprompt_content", ""),
        "actions": actions,
    }


# ---------------------------------------------------------------------------
# Kit Install CLI
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
    ref_dir = cypilot_dir / "kits" / kit_slug

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
        user_bp_dir = cypilot_dir / "config" / "kits" / kit_slug / "blueprints"
        print(json.dumps({
            "status": "DRY_RUN",
            "kit": kit_slug,
            "version": kit_version,
            "source": kit_source.as_posix(),
            "reference": ref_dir.as_posix(),
            "blueprints": user_bp_dir.as_posix(),
        }, indent=2, ensure_ascii=False))
        return 0

    result = install_kit(kit_source, cypilot_dir, kit_slug, kit_version)

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-return-install-ok
    # @cpt-begin:cpt-cypilot-state-blueprint-system-kit-install:p1:inst-install-complete
    output: Dict[str, Any] = {
        "status": result["status"],
        "action": result.get("action", "installed"),
        "kit": kit_slug,
        "version": kit_version,
        "files_written": result.get("files_written", 0),
        "artifact_kinds": result.get("artifact_kinds", []),
    }
    if result.get("errors"):
        output["errors"] = result["errors"]

    print(json.dumps(output, indent=2, ensure_ascii=False))
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
    gen_dir = cypilot_dir / ".gen"
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
        gen_kits_dir = gen_dir / "kits"

        if args.dry_run:
            results.append({"kit": kit_slug, "action": "dry_run"})
        else:
            summary, errors = process_kit(
                kit_slug, source_bp_dir, gen_kits_dir, dry_run=False,
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
    gen_dir = cypilot_dir / ".gen"
    config_kits_dir = config_dir / "kits"
    gen_kits_dir = gen_dir / "kits"

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
            kit_slug, bp_dir, gen_kits_dir, dry_run=args.dry_run,
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

def _read_kit_version(conf_path: Path) -> str:
    """Read kit version from conf.toml."""
    try:
        import tomllib
        with open(conf_path, "rb") as f:
            data = tomllib.load(f)
        ver = data.get("version")
        if ver is not None:
            return str(ver)
    except Exception:
        pass
    return ""


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
        "path": f".gen/kits/{kit_slug}",
    }
    if kit_version:
        kits[kit_slug]["version"] = kit_version

    # Write back using our TOML serializer
    try:
        from ..utils import toml_utils
        toml_utils.dump(data, core_toml, header_comment="Cypilot project configuration")
    except Exception:
        pass
