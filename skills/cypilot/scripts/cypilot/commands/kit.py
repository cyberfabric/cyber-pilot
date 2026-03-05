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
@cpt-dod:cpt-cypilot-dod-blueprint-system-kit-migrate:p1
@cpt-state:cpt-cypilot-state-blueprint-system-kit-install:p1
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.ui import ui

# Subdirectories to copy from kit source (reference + install)
KIT_COPY_SUBDIRS = ["blueprints", "scripts"]

# ---------------------------------------------------------------------------
# Config seeding — copy default .toml configs from kit scripts to config/
# @cpt-algo:cpt-cypilot-algo-blueprint-system-seed-configs:p1
# ---------------------------------------------------------------------------

_CONFIG_EXTENSIONS = {".toml"}

def _seed_kit_config_files(
    gen_scripts_dir: Path,
    config_dir: Path,
    actions: Dict[str, str],
) -> None:
    """Copy top-level .toml files from generated scripts into config/ if missing.

    Only seeds files that don't already exist in config/ — never overwrites
    user-editable config.
    """
    config_dir.mkdir(parents=True, exist_ok=True)
    # @cpt-begin:cpt-cypilot-algo-blueprint-system-seed-configs:p1:inst-foreach-toml
    for src in gen_scripts_dir.iterdir():
        if src.is_file() and src.suffix in _CONFIG_EXTENSIONS:
            dst = config_dir / src.name
            # @cpt-begin:cpt-cypilot-algo-blueprint-system-seed-configs:p1:inst-seed-if-missing
            if not dst.exists():
                shutil.copy2(src, dst)
                actions[f"config_{src.stem}"] = "seeded"
            # @cpt-end:cpt-cypilot-algo-blueprint-system-seed-configs:p1:inst-seed-if-missing
    # @cpt-end:cpt-cypilot-algo-blueprint-system-seed-configs:p1:inst-foreach-toml

# ---------------------------------------------------------------------------
# Shared CLI helper — resolve project root + cypilot directory
# @cpt-algo:cpt-cypilot-algo-blueprint-system-resolve-dir:p1
# ---------------------------------------------------------------------------

def _resolve_cypilot_dir() -> Optional[tuple]:
    """Resolve project root and cypilot directory from CWD.

    Returns (project_root, cypilot_dir) or None (after printing JSON error).
    """
    from ..utils.files import find_project_root, _read_cypilot_var

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-resolve-dir:p1:inst-find-root
    project_root = find_project_root(Path.cwd())
    if project_root is None:
        ui.result({"status": "ERROR", "message": "No project root found"})
        return None
    # @cpt-end:cpt-cypilot-algo-blueprint-system-resolve-dir:p1:inst-find-root

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-resolve-dir:p1:inst-read-cypilot-var
    cypilot_rel = _read_cypilot_var(project_root)
    if not cypilot_rel:
        ui.result({"status": "ERROR", "message": "No cypilot directory"})
        return None
    # @cpt-end:cpt-cypilot-algo-blueprint-system-resolve-dir:p1:inst-read-cypilot-var

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-resolve-dir:p1:inst-resolve-abs
    cypilot_dir = (project_root / cypilot_rel).resolve()
    return project_root, cypilot_dir
    # @cpt-end:cpt-cypilot-algo-blueprint-system-resolve-dir:p1:inst-resolve-abs

# ---------------------------------------------------------------------------
# Shared helper — write per-kit SKILL.md + workflow files into .gen/
# @cpt-algo:cpt-cypilot-algo-blueprint-system-write-gen-outputs:p1
# ---------------------------------------------------------------------------

def _write_kit_gen_outputs(
    kit_slug: str,
    summary: Dict[str, Any],
    gen_kits_dir: Path,
) -> Dict[str, Any]:
    """Write per-kit SKILL.md and workflow .md files into .gen/kits/{slug}/.

    Returns dict with keys: skill_nav (str or ""), workflows_written (list).
    """
    result: Dict[str, Any] = {"skill_nav": "", "workflows_written": []}

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-write-gen-outputs:p1:inst-write-skill
    skill_content = summary.get("skill_content", "")
    if skill_content:
        art_kinds = [k.upper() for k in summary.get("artifact_kinds", []) if k]
        wf_names = [w["name"] for w in summary.get("workflows", []) if w.get("name")]
        desc_parts: List[str] = []
        if art_kinds:
            desc_parts.append(f"Artifacts: {', '.join(art_kinds)}")
        if wf_names:
            desc_parts.append(f"Workflows: {', '.join(wf_names)}")
        kit_description = "; ".join(desc_parts) if desc_parts else f"Kit {kit_slug}"

        gen_kit_skill_path = gen_kits_dir / kit_slug / "SKILL.md"
        gen_kit_skill_path.parent.mkdir(parents=True, exist_ok=True)
        gen_kit_skill_path.write_text(
            f"---\nname: cypilot-{kit_slug}\n"
            f"description: \"{kit_description}\"\n---\n\n"
            f"# Cypilot Skill — Kit `{kit_slug}`\n\n"
            f"Generated from kit `{kit_slug}` blueprints.\n\n"
            + skill_content + "\n",
            encoding="utf-8",
        )
        result["skill_nav"] = (
            f"ALWAYS invoke `{{cypilot_path}}/.gen/kits/{kit_slug}/SKILL.md` FIRST"
        )
    # @cpt-end:cpt-cypilot-algo-blueprint-system-write-gen-outputs:p1:inst-write-skill

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-write-gen-outputs:p1:inst-write-workflow
    # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-workflows:p2:inst-write-workflow
    for wf in summary.get("workflows", []):
        wf_name = wf["name"]
        wf_path = gen_kits_dir / kit_slug / "workflows" / f"{wf_name}.md"
        wf_path.parent.mkdir(parents=True, exist_ok=True)
        fm_lines = ["---", "cypilot: true", "type: workflow", f"name: cypilot-{wf_name}"]
        if wf.get("description"):
            fm_lines.append(f"description: {wf['description']}")
        if wf.get("version"):
            fm_lines.append(f"version: {wf['version']}")
        if wf.get("purpose"):
            fm_lines.append(f"purpose: {wf['purpose']}")
        fm_lines.append("---")
        wf_path.write_text(
            "\n".join(fm_lines) + "\n\n" + wf["content"] + "\n",
            encoding="utf-8",
        )
        result["workflows_written"].append(wf_name)
    # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-workflows:p2:inst-write-workflow
    # @cpt-end:cpt-cypilot-algo-blueprint-system-write-gen-outputs:p1:inst-write-workflow

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-write-gen-outputs:p1:inst-return-gen-outputs
    # @cpt-begin:cpt-cypilot-algo-blueprint-system-generate-workflows:p2:inst-return-workflows
    return result
    # @cpt-end:cpt-cypilot-algo-blueprint-system-generate-workflows:p2:inst-return-workflows
    # @cpt-end:cpt-cypilot-algo-blueprint-system-write-gen-outputs:p1:inst-return-gen-outputs

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

        # Seed kit config files into config/ (only if missing)
        _seed_kit_config_files(gen_kit_scripts, config_dir, actions)

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-process-blueprints
    # Process blueprints → generate resources into .gen/kits/{slug}/
    from ..utils.blueprint import process_kit

    summary, kit_errors = process_kit(
        kit_slug, user_bp_dir, gen_kits_dir, dry_run=False,
    )
    errors.extend(kit_errors)
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-process-blueprints

    # Write per-kit SKILL.md + workflow files into .gen/
    gen_out = _write_kit_gen_outputs(kit_slug, summary, gen_kits_dir)
    skill_nav = gen_out["skill_nav"]
    if skill_nav:
        actions["gen_kit_skill"] = "created"
    for wf_name in gen_out["workflows_written"]:
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
        ui.result({
            "status": "FAIL",
            "message": f"Kit source missing blueprints/ directory: {kit_source}",
            "hint": "Kit must contain a blueprints/ directory with at least one .md file",
        })
        return 2

    bp_files = list(blueprints_dir.glob("*.md"))
    if not bp_files:
        ui.result({
            "status": "FAIL",
            "message": f"No .md files in {blueprints_dir}",
            "hint": "blueprints/ must contain at least one blueprint .md file",
        })
        return 2
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-if-invalid-source
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-validate-source

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-extract-metadata
    # Kit slug and version from conf.toml (single source of truth)
    kit_slug = ""
    kit_version = ""
    conf_toml = kit_source / "conf.toml"
    if conf_toml.is_file():
        try:
            import tomllib
            with open(conf_toml, "rb") as f:
                conf_data = tomllib.load(f)
            slug = conf_data.get("slug")
            if isinstance(slug, str) and slug.strip():
                kit_slug = slug.strip()
            ver = conf_data.get("version")
            if ver is not None:
                kit_version = str(ver)
        except Exception as exc:
            sys.stderr.write(f"kit-install: failed to read {conf_toml}: {exc}\n")

    if not kit_slug:
        kit_slug = kit_source.name
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-extract-metadata

    project_root = find_project_root(Path.cwd())
    if project_root is None:
        ui.result({
            "status": "ERROR",
            "message": "No project root found",
            "hint": "Run 'cypilot init' first",
        })
        return 1

    cypilot_rel = _read_cypilot_var(project_root)
    if not cypilot_rel:
        ui.result({
            "status": "ERROR",
            "message": "No cypilot directory configured",
            "hint": "Run 'cypilot init' first",
        })
        return 1

    cypilot_dir = (project_root / cypilot_rel).resolve()
    ref_dir = cypilot_dir / "kits" / kit_slug

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-if-already-registered
    if ref_dir.exists() and not args.force:
        ui.result({
            "status": "FAIL",
            "message": f"Kit '{kit_slug}' already installed",
            "hint": "Use --force to overwrite",
        })
        return 2
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-if-already-registered

    if args.dry_run:
        user_bp_dir = cypilot_dir / "config" / "kits" / kit_slug / "blueprints"
        ui.result({
            "status": "DRY_RUN",
            "kit": kit_slug,
            "version": kit_version,
            "source": kit_source.as_posix(),
            "reference": ref_dir.as_posix(),
            "blueprints": user_bp_dir.as_posix(),
        })
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

    ui.result(output, human_fn=lambda d: _human_kit_install(d))
    return 0
    # @cpt-end:cpt-cypilot-state-blueprint-system-kit-install:p1:inst-install-complete
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-install:p1:inst-return-install-ok

def _human_kit_install(data: dict) -> None:
    status = data.get("status", "")
    kit_slug = data.get("kit", "?")
    version = data.get("version", "?")
    action = data.get("action", "installed")

    ui.header("Kit Install")
    ui.detail("Kit", kit_slug)
    ui.detail("Version", str(version))
    ui.detail("Action", action)

    if status == "DRY_RUN":
        ui.detail("Source", data.get("source", "?"))
        ui.detail("Reference", data.get("reference", "?"))
        ui.detail("Blueprints", data.get("blueprints", "?"))
        ui.success("Dry run — no files written.")
        ui.blank()
        return

    fw = data.get("files_written", 0)
    kinds = data.get("artifact_kinds", [])
    ui.detail("Files written", str(fw))
    if kinds:
        ui.detail("Artifact kinds", ", ".join(kinds))

    errs = data.get("errors", [])
    if errs:
        ui.blank()
        for e in errs:
            ui.warn(str(e))

    if status == "PASS":
        ui.success(f"Kit '{kit_slug}' installed.")
    elif status == "FAIL":
        msg = data.get("message", "")
        hint = data.get("hint", "")
        ui.error(msg or "Install failed.")
        if hint:
            ui.hint(hint)
    else:
        ui.info(f"Status: {status}")
    ui.blank()

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

    resolved = _resolve_cypilot_dir()
    if resolved is None:
        return 1
    _, cypilot_dir = resolved
    config_dir = cypilot_dir / "config"
    gen_dir = cypilot_dir / ".gen"
    kits_ref_dir = cypilot_dir / "kits"

    if not kits_ref_dir.is_dir():
        ui.result({"status": "FAIL", "message": "No kits installed", "hint": "Run 'cypilot kit install <path>' first"})
        return 2

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-resolve-kits
    if args.kit:
        kit_dirs = [kits_ref_dir / args.kit]
        if not kit_dirs[0].is_dir():
            ui.result({"status": "FAIL", "message": f"Kit '{args.kit}' not found in {kits_ref_dir}"})
            return 2
    else:
        kit_dirs = [d for d in sorted(kits_ref_dir.iterdir()) if d.is_dir()]

    if not kit_dirs:
        ui.result({"status": "FAIL", "message": "No kits found"})
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

    ui.result(output, human_fn=lambda d: _human_kit_update(d))
    return 0
    # @cpt-end:cpt-cypilot-state-blueprint-system-kit-install:p1:inst-update-complete
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-update:p1:inst-return-update-ok

def _human_kit_update(data: dict) -> None:
    status = data.get("status", "")
    n = data.get("kits_updated", 0)

    ui.header("Kit Update")
    ui.detail("Kits updated", str(n))

    for r in data.get("results", []):
        kit_slug = r.get("kit", "?")
        action = r.get("action", "?")
        fw = r.get("files_written")
        kinds = r.get("artifact_kinds", [])
        parts = [f"{kit_slug}: {action}"]
        if fw is not None:
            parts.append(f"{fw} files")
        if kinds:
            parts.append(", ".join(kinds))
        ui.step("  ".join(parts))

    errs = data.get("errors", [])
    if errs:
        ui.blank()
        for e in errs:
            ui.warn(str(e))

    if status == "PASS":
        ui.success("Kit update complete.")
    elif status == "WARN":
        ui.warn("Kit update finished with warnings.")
    else:
        ui.info(f"Status: {status}")
    ui.blank()

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

    resolved = _resolve_cypilot_dir()
    if resolved is None:
        return 1
    _, cypilot_dir = resolved
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
        ui.result({"status": "FAIL", "message": "No kits with blueprints found", "hint": "Run 'cypilot kit install <path>' first"})
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

    ui.result(output, human_fn=lambda d: _human_generate_resources(d))
    return 0
    # @cpt-end:cpt-cypilot-flow-blueprint-system-generate-resources:p1:inst-return-gen-ok

def _human_generate_resources(data: dict) -> None:
    status = data.get("status", "")
    n = data.get("kits_processed", 0)

    ui.header("Generate Resources")
    ui.detail("Kits processed", str(n))

    for r in data.get("results", []):
        kit_slug = r.get("kit", "?")
        fw = r.get("files_written", 0)
        kinds = r.get("artifact_kinds", [])
        kind_str = f"  ({', '.join(kinds)})" if kinds else ""
        ui.step(f"{kit_slug}: {fw} files generated{kind_str}")

    errs = data.get("errors", [])
    if errs:
        ui.blank()
        for e in errs:
            ui.warn(str(e))

    if status == "PASS":
        ui.success("Resources generated.")
    elif status == "WARN":
        ui.warn("Generation finished with warnings.")
    else:
        ui.info(f"Status: {status}")
    ui.blank()

# ---------------------------------------------------------------------------
# Kit Migrate — marker-level three-way merge
# @cpt-algo:cpt-cypilot-algo-blueprint-system-three-way-merge:p1
# ---------------------------------------------------------------------------

# Regex mirrors blueprint.py parser — supports both legacy and named syntax
# @cpt-begin:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-derive-identity-key
_MIG_OPEN_RE = re.compile(r"^`@cpt:(\w[\w-]*)(?::(\w[\w-]*))?` *$")
_MIG_CLOSE_RE = re.compile(r"^`@/cpt:(\w[\w-]*)(?::(\w[\w-]*))?` *$")

_SINGLETON_MARKERS = frozenset({"blueprint", "skill", "system-prompt", "rules", "checklist"})

@dataclass
class _Segment:
    """A contiguous block inside a blueprint: either plain text or a @cpt: marker."""
    kind: str           # "text" or "marker"
    raw: str            # full raw text (including open/close tags for markers)
    marker_type: str = ""   # e.g. "heading", "workflow", "skill" (empty for text)
    marker_key: str = ""    # stable identity key
    explicit_id: str = ""   # ID from named syntax @cpt:TYPE:ID (empty for legacy)

def _marker_identity_key(marker_type: str, raw_content: str, explicit_id: str = "") -> str:
    """Derive a stable identity key for a marker from its type and TOML data.

    Resolution chain (highest priority first):
      1. Explicit syntax ID: @cpt:TYPE:ID → "TYPE:ID"
      2. Singleton markers: blueprint, skill, system-prompt, rules, checklist → TYPE
      3. TOML-derived key: heading:{id}, workflow:{name}, id:{kind}
      4. Positional fallback: TYPE (caller appends #N index)
    """
    # 1. Singleton markers — type IS the key
    if marker_type in _SINGLETON_MARKERS:
        return marker_type

    # 2. Explicit syntax ID (highest priority for non-singletons)
    if explicit_id:
        return f"{marker_type}:{explicit_id}"

    # 3. TOML-derived key
    # Quick TOML key extraction without full parser
    def _toml_val(key: str) -> str:
        for line in raw_content.splitlines():
            stripped = line.strip()
            if (stripped.startswith(f"{key} ") or stripped.startswith(f"{key}=")) and "=" in stripped:
                _, _, val = stripped.partition("=")
                return val.strip().strip('"').strip("'")
        return ""

    if marker_type == "workflow":
        name = _toml_val("name")
        return f"workflow:{name}" if name else "workflow"
    if marker_type == "heading":
        hid = _toml_val("id")
        if hid:
            return f"heading:{hid}"
        level = _toml_val("level")
        return f"heading:L{level}" if level else "heading"
    if marker_type == "id":
        kind = _toml_val("kind")
        return f"id:{kind}" if kind else "id"

    # 4. Fallback to type (caller appends positional index)
    return marker_type

def _parse_segments(text: str) -> List[_Segment]:
    """Parse blueprint text into ordered segments (text and marker blocks).

    Each marker segment includes its opening tag, content, and closing tag.
    Text segments are everything between markers.
    """
    lines = text.splitlines(keepends=True)
    segments: List[_Segment] = []
    text_buf: List[str] = []
    i = 0

    while i < len(lines):
        stripped = lines[i].rstrip("\n\r")
        m_open = _MIG_OPEN_RE.match(stripped.strip())
        if not m_open:
            text_buf.append(lines[i])
            i += 1
            continue

        # Flush accumulated text
        if text_buf:
            segments.append(_Segment(kind="text", raw="".join(text_buf)))
            text_buf = []

        marker_type = m_open.group(1)
        explicit_id = m_open.group(2) or ""
        marker_lines: List[str] = [lines[i]]
        j = i + 1
        found_close = False
        while j < len(lines):
            marker_lines.append(lines[j])
            close_stripped = lines[j].rstrip("\n\r")
            m_close = _MIG_CLOSE_RE.match(close_stripped.strip())
            if m_close and m_close.group(1) == marker_type and (m_close.group(2) or "") == explicit_id:
                found_close = True
                j += 1
                break
            j += 1

        if not found_close:
            # Unclosed marker — treat as text
            text_buf.extend(marker_lines)
            i = j
            continue

        raw = "".join(marker_lines)
        # Content between open and close tags (for identity extraction)
        content_lines = marker_lines[1:-1]
        raw_content = "".join(content_lines)
        key = _marker_identity_key(marker_type, raw_content, explicit_id)

        segments.append(_Segment(
            kind="marker",
            raw=raw,
            marker_type=marker_type,
            marker_key=key,
            explicit_id=explicit_id,
        ))
        i = j

    if text_buf:
        segments.append(_Segment(kind="text", raw="".join(text_buf)))

    # Add positional index per base key for markers WITHOUT explicit syntax ID.
    # Named markers (@cpt:TYPE:ID) already have unique keys and skip indexing.
    key_seen: Dict[str, int] = {}
    for seg in segments:
        if seg.kind != "marker":
            continue
        if seg.explicit_id:
            continue
        base = seg.marker_key
        idx = key_seen.get(base, 0)
        key_seen[base] = idx + 1
        seg.marker_key = f"{base}#{idx}"

    return segments
# @cpt-end:cpt-cypilot-algo-blueprint-system-parse-blueprint:p1:inst-derive-identity-key

def _kebab_safe(value: str) -> str:
    """Normalize a string to a safe kebab-case token for marker IDs.

    Lowercase, replace non-alphanumeric sequences with hyphens, strip edges.
    """
    result = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return result.strip("-")

def _derive_marker_id(marker_type: str, raw_content: str, preceding_heading_id: str = "") -> str:
    """Derive a kebab-case ID for a legacy marker based on its type and TOML content.

    Used by the legacy marker upgrade step to convert @cpt:TYPE → @cpt:TYPE:ID.
    """
    # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p2:inst-upgrade-legacy
    def _toml_val(key: str) -> str:
        for line in raw_content.splitlines():
            stripped = line.strip()
            if (stripped.startswith(f"{key} ") or stripped.startswith(f"{key}=")) and "=" in stripped:
                _, _, val = stripped.partition("=")
                return val.strip().strip('"').strip("'")
        return ""

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p2:inst-upgrade-heading
    if marker_type == "heading":
        return _kebab_safe(_toml_val("id"))
    # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p2:inst-upgrade-heading
    # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p2:inst-upgrade-id
    if marker_type == "id":
        return _kebab_safe(_toml_val("kind"))
    # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p2:inst-upgrade-id
    # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p2:inst-upgrade-workflow
    if marker_type == "workflow":
        return _kebab_safe(_toml_val("name"))
    # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p2:inst-upgrade-workflow
    # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p2:inst-upgrade-check
    if marker_type == "check":
        return _kebab_safe(_toml_val("id"))
    # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p2:inst-upgrade-check
    # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p2:inst-upgrade-rule
    if marker_type == "rule":
        kind = _toml_val("kind")
        section = _toml_val("section")
        if kind and section:
            return _kebab_safe(f"{kind}-{section}")
        return _kebab_safe(kind or section)
    # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p2:inst-upgrade-rule
    # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p2:inst-upgrade-prompt-example
    if marker_type in ("prompt", "example"):
        return _kebab_safe(preceding_heading_id)
    # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p2:inst-upgrade-prompt-example
    return ""
    # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p2:inst-upgrade-legacy

def _upgrade_legacy_tags(merged_parts: List[tuple]) -> tuple:
    """Rewrite legacy @cpt:TYPE tags to @cpt:TYPE:ID in merged output.

    Skips singleton markers and markers that already have explicit IDs.
    Derives IDs from TOML content per marker type.

    Returns (updated_parts, upgraded_keys, upgraded_details).
    """
    upgraded: List[str] = []
    upgraded_details: Dict[str, tuple] = {}  # key → (old_tag, new_tag)
    last_heading_id = ""
    id_counts: Dict[str, int] = {}
    result: List[tuple] = []

    for raw, key in merged_parts:
        if key is None:
            result.append((raw, key))
            continue

        # Parse opening tag to check if already named
        lines_list = raw.splitlines(keepends=True)
        if not lines_list:
            result.append((raw, key))
            continue
        first_line = lines_list[0].rstrip("\n\r").strip()
        m = _MIG_OPEN_RE.match(first_line)
        if not m:
            result.append((raw, key))
            continue

        # Track heading IDs from already-named markers
        if m.group(2):
            if m.group(1) == "heading":
                last_heading_id = m.group(2)
            result.append((raw, key))
            continue

        marker_type = m.group(1)
        if marker_type in _SINGLETON_MARKERS:
            result.append((raw, key))
            continue

        # Extract content between tags for ID derivation
        content = "".join(lines_list[1:-1]) if len(lines_list) > 2 else ""
        derived_id = _derive_marker_id(marker_type, content, last_heading_id)

        if not derived_id:
            result.append((raw, key))
            continue

        # Disambiguate duplicate IDs: append -1, -2, etc.
        count_key = f"{marker_type}:{derived_id}"
        count = id_counts.get(count_key, 0)
        id_counts[count_key] = count + 1
        final_id = derived_id if count == 0 else f"{derived_id}-{count}"

        if marker_type == "heading":
            last_heading_id = final_id

        # Rewrite opening and closing tags
        new_raw = re.sub(
            r"^`@cpt:" + re.escape(marker_type) + r"`( *)$",
            "`@cpt:" + marker_type + ":" + final_id + "`\\1",
            raw, count=1, flags=re.MULTILINE,
        )
        new_raw = re.sub(
            r"^`@/cpt:" + re.escape(marker_type) + r"`( *)$",
            "`@/cpt:" + marker_type + ":" + final_id + "`\\1",
            new_raw, count=1, flags=re.MULTILINE,
        )

        if new_raw != raw:
            upgraded.append(key)
            upgraded_details[key] = (
                f"@cpt:{marker_type}",
                f"@cpt:{marker_type}:{final_id}",
            )
        result.append((new_raw, key))

    return result, upgraded, upgraded_details

def _normalize_legacy_to_named(text: str, reference_text: str = "") -> tuple:
    """Upgrade legacy @cpt:TYPE tags to @cpt:TYPE:ID in text for merge normalization.

    When reference_text is provided, uses positional matching within each marker
    type to map legacy markers to their named equivalents in the reference.
    This handles all marker types, including those without derivable TOML IDs.

    Falls back to TOML-based derivation when reference is not available.

    Returns (normalized_text, upgraded_details) where upgraded_details maps
    marker_key -> (old_tag, new_tag).
    """
    if not reference_text:
        segments = _parse_segments(text)
        parts = [(seg.raw, seg.marker_key if seg.kind == "marker" else None)
                 for seg in segments]
        normalized, _, upg_details = _upgrade_legacy_tags(parts)
        return "".join(p[0] for p in normalized), upg_details

    text_segments = _parse_segments(text)
    ref_segments = _parse_segments(reference_text)

    # Group markers by type for positional matching
    ref_by_type: Dict[str, List[_Segment]] = {}
    for seg in ref_segments:
        if seg.kind == "marker":
            ref_by_type.setdefault(seg.marker_type, []).append(seg)

    text_by_type: Dict[str, List[_Segment]] = {}
    for seg in text_segments:
        if seg.kind == "marker":
            text_by_type.setdefault(seg.marker_type, []).append(seg)

    # Build upgrade map: text segment id → (marker_type, explicit_id from reference)
    upgrade_map: Dict[int, tuple] = {}
    for mtype, t_segs in text_by_type.items():
        r_segs = ref_by_type.get(mtype, [])
        if len(t_segs) != len(r_segs):
            continue  # counts differ — can't safely map positionally
        for t_seg, r_seg in zip(t_segs, r_segs):
            if not t_seg.explicit_id and r_seg.explicit_id:
                upgrade_map[id(t_seg)] = (mtype, r_seg.explicit_id)

    # Rewrite tags in text segments
    result_parts: List[str] = []
    norm_details: Dict[str, tuple] = {}  # key → (old_tag, new_tag)
    for seg in text_segments:
        if seg.kind != "marker" or id(seg) not in upgrade_map:
            result_parts.append(seg.raw)
            continue

        mtype, new_id = upgrade_map[id(seg)]
        raw = seg.raw
        raw = re.sub(
            r"^`@cpt:" + re.escape(mtype) + r"`( *)$",
            "`@cpt:" + mtype + ":" + new_id + "`\\1",
            raw, count=1, flags=re.MULTILINE,
        )
        raw = re.sub(
            r"^`@/cpt:" + re.escape(mtype) + r"`( *)$",
            "`@/cpt:" + mtype + ":" + new_id + "`\\1",
            raw, count=1, flags=re.MULTILINE,
        )
        result_parts.append(raw)
        norm_details[seg.marker_key] = (
            f"@cpt:{mtype}",
            f"@cpt:{mtype}:{new_id}",
        )

    return "".join(result_parts), norm_details

def _prompt_confirm(message: str, state: Dict[str, bool], *, allow_modify: bool = False) -> str:
    """Interactive prompt returning 'y', 'n', or 'm' (when allow_modify=True).

    state['all'] tracks whether user already chose 'all' (auto-approve).
    Prompts go to stderr, input from stdin.
    """
    if state.get("all"):
        return "y"
    if allow_modify:
        sys.stderr.write(f"{message} [y/N/m(odify)/all] ")
    else:
        sys.stderr.write(f"{message} [y/N/all (approve remaining files)] ")
    sys.stderr.flush()
    try:
        response = input().strip().lower()
    except EOFError:
        return "n"
    if response == "all":
        state["all"] = True
        return "y"
    if allow_modify and response in ("m", "modify"):
        return "m"
    return "y" if response == "y" else "n"

def _show_marker_content(raw: str, color: str = "red") -> None:
    """Show marker content lines in a single color (red=removed, green=added)."""
    code = "\033[31m" if color == "red" else "\033[32m"
    for line in raw.splitlines():
        sys.stderr.write(f"        {code}{line}\033[0m\n")

def _show_marker_diff(key: str, user_raw: str, new_raw: str) -> None:
    """Show compact unified diff between user and reference marker content."""
    import difflib
    user_lines = user_raw.splitlines(keepends=True)
    new_lines = new_raw.splitlines(keepends=True)
    diff = list(difflib.unified_diff(
        user_lines, new_lines,
        fromfile=f"yours ({key})",
        tofile=f"reference ({key})",
        lineterm="",
    ))
    if not diff:
        return
    for line in diff:
        line_s = line.rstrip("\n")
        if line_s.startswith("+++") or line_s.startswith("---"):
            sys.stderr.write(f"        {line_s}\n")
        elif line_s.startswith("+"):
            sys.stderr.write(f"        \033[32m{line_s}\033[0m\n")
        elif line_s.startswith("-"):
            sys.stderr.write(f"        \033[31m{line_s}\033[0m\n")
        elif line_s.startswith("@@"):
            sys.stderr.write(f"        \033[36m{line_s}\033[0m\n")

_EDITOR_SEPARATOR = "# ── edit below this line ──────────────────────────────────────"

def _get_editor() -> str:
    """Return the user's preferred editor, git-style: $VISUAL → $EDITOR → vi."""
    return os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vi"

def _open_editor_for_marker(
    key: str,
    user_raw: str,
    new_raw: str,
) -> Optional[str]:
    """Open user's default editor for manual marker merge, git-style.

    Creates a temp file with the diff as comments and the user's current
    content as default. Returns edited content, or None if aborted
    (empty file saved or editor failed).
    """
    import difflib

    # Build diff for reference
    user_lines = user_raw.splitlines(keepends=True)
    new_lines = new_raw.splitlines(keepends=True)
    diff = list(difflib.unified_diff(
        user_lines, new_lines,
        fromfile=f"yours ({key})",
        tofile=f"reference ({key})",
        lineterm="",
    ))

    # Compose temp file content
    header_lines = [
        f"# cypilot migrate: edit marker [{key}]",
        "#",
        "# Diff between your version (−) and the new reference (+):",
    ]
    if diff:
        header_lines.append("#")
        for d in diff:
            header_lines.append(f"#   {d.rstrip()}")
    else:
        header_lines.append("#   (no diff — versions are identical)")
    header_lines.extend([
        "#",
        "# Edit the content below the separator line.",
        "# To abort, delete all content below the separator and save.",
        _EDITOR_SEPARATOR,
    ])

    content = "\n".join(header_lines) + "\n" + user_raw

    editor = _get_editor()
    tmp_path: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".md",
            prefix=f"cypilot-migrate-{key.replace(':', '-').replace('#', '-')}-",
            delete=False,
            encoding="utf-8",
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        import shlex
        cmd = shlex.split(editor)
        subprocess.check_call(cmd + [tmp_path])

        with open(tmp_path, encoding="utf-8") as f:
            edited = f.read()
    except FileNotFoundError:
        sys.stderr.write(f"        editor not found: {editor}\n")
        return None
    except Exception as exc:
        sys.stderr.write(f"        editor failed: {exc}\n")
        return None
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    # Extract content after separator
    sep_idx = edited.find(_EDITOR_SEPARATOR)
    if sep_idx != -1:
        after_sep = edited[sep_idx + len(_EDITOR_SEPARATOR):]
        # Strip exactly one leading newline after separator
        if after_sep.startswith("\n"):
            after_sep = after_sep[1:]
        result = after_sep
    else:
        # No separator found — use entire content, strip header comments
        lines = edited.splitlines(keepends=True)
        first_non_comment = 0
        for i, line in enumerate(lines):
            if not line.startswith("#"):
                first_non_comment = i
                break
        else:
            first_non_comment = len(lines)
        result = "".join(lines[first_non_comment:])

    # Empty result = abort
    if not result.strip():
        return None

    return result

def _three_way_merge_blueprint(
    old_ref_text: str,
    new_ref_text: str,
    user_text: str,
    *,
    force_keys: frozenset = frozenset(),
    restore_keys: frozenset = frozenset(),
    remove_keys: frozenset = frozenset(),
    skip_keys: frozenset = frozenset(),
    skip_insert_keys: frozenset = frozenset(),
    modify_overrides: Optional[Dict[str, str]] = None,
) -> tuple:
    """Three-way merge of a blueprint at the @cpt: marker level.

    Args:
        old_ref_text: Previous reference version (before update).
        new_ref_text: New reference version (after update).
        user_text: User's current config copy.
        force_keys: Set of marker keys to force-update even if user customized.
        restore_keys: Set of marker keys to restore (user deleted, re-insert from ref).
        remove_keys: Set of marker keys to remove (reference deleted, user still has).
        skip_keys: Set of marker keys to NOT update (keep user version even though ref changed).
        skip_insert_keys: Set of marker keys to NOT insert (even though new in ref).
        modify_overrides: Dict of marker key → custom content from manual editor merge.

    Returns:
        (merged_text, report) where report is a dict with:
        - updated: list of marker keys that were updated
        - skipped: list of marker keys skipped (user customized)
        - kept: list of marker keys kept as-is (no change in reference)
        - inserted: list of marker keys inserted (new in reference)
        - deleted: list of marker keys user removed (still in reference)
        - upgraded: list of marker keys upgraded from legacy to named syntax
        - modified: list of marker keys manually edited by user
    """
    if modify_overrides is None:
        modify_overrides = {}
    # Normalize legacy markers to named syntax before comparison.
    # Uses new_ref as positional guide so ALL marker types get correct IDs.
    old_ref_text, _ = _normalize_legacy_to_named(old_ref_text, new_ref_text)
    user_text, norm_upgraded_details = _normalize_legacy_to_named(user_text, new_ref_text)

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-parse-three
    old_segments = _parse_segments(old_ref_text)
    new_segments = _parse_segments(new_ref_text)
    user_segments = _parse_segments(user_text)
    # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-parse-three

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-identify-changes
    # Build lookup maps: key → raw text
    old_map: Dict[str, str] = {}
    for seg in old_segments:
        if seg.kind == "marker":
            old_map[seg.marker_key] = seg.raw

    new_map: Dict[str, str] = {}
    for seg in new_segments:
        if seg.kind == "marker":
            new_map[seg.marker_key] = seg.raw
    # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-identify-changes

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-apply-merge
    updated: List[str] = []
    updated_details: Dict[str, tuple] = {}  # key → (old_raw, new_raw)
    skipped: List[str] = []
    skipped_details: Dict[str, tuple] = {}  # key → (user_raw, new_raw)
    ref_removed: List[str] = []
    ref_removed_details: Dict[str, str] = {}  # key → user_raw
    kept: List[str] = []
    modified: List[str] = []  # keys manually edited via editor
    # Each element: (raw_text, marker_key or None)
    merged_parts: List[tuple] = []

    for seg in user_segments:
        if seg.kind == "text":
            merged_parts.append((seg.raw, None))
            continue

        key = seg.marker_key
        old_raw = old_map.get(key)
        new_raw = new_map.get(key)

        # Manual editor override takes precedence over all other logic
        if key in modify_overrides:
            merged_parts.append((modify_overrides[key], key))
            modified.append(key)
            continue

        # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-keep-user-added
        if old_raw is None:
            # Marker not in old reference — user-added or unknown, keep as-is
            merged_parts.append((seg.raw, key))
            kept.append(key)
        # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-keep-user-added
        # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-keep-ref-removed
        elif new_raw is None:
            # Marker removed in new reference
            if key in remove_keys:
                # User approved removal — drop it
                pass
            else:
                merged_parts.append((seg.raw, key))
            ref_removed.append(key)
            ref_removed_details[key] = seg.raw
        # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-keep-ref-removed
        # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-update-unmodified
        elif seg.raw == old_raw:
            # User hasn't changed it — safe to update
            if new_raw != old_raw and key not in skip_keys:
                merged_parts.append((new_raw, key))
                updated.append(key)
                updated_details[key] = (old_raw, new_raw)
            # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-keep-unchanged
            else:
                merged_parts.append((seg.raw, key))
                kept.append(key)
            # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-keep-unchanged
        # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-update-unmodified
        else:
            # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-preserve-user
            # User customized this marker
            if key in force_keys and new_raw is not None:
                merged_parts.append((new_raw, key))
                updated.append(key)
                updated_details[key] = (seg.raw, new_raw)
            else:
                merged_parts.append((seg.raw, key))
                skipped.append(key)
                skipped_details[key] = (seg.raw, new_raw)
            # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-preserve-user
    # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-apply-merge

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-respect-deletions
    # Detect markers that user deleted (present in old_ref AND new_ref but absent from user).
    user_keys = {seg.marker_key for seg in user_segments if seg.kind == "marker"}
    deleted: List[str] = []
    deleted_details: Dict[str, str] = {}  # key → new_raw
    for key in new_map:
        if key not in user_keys and key in old_map:
            deleted.append(key)
            deleted_details[key] = new_map[key]
    # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-respect-deletions

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-insert-new
    # Insert markers that are truly new (in new_ref but NOT in old_ref)
    # at their correct position based on new_segments ordering.
    # Markers that existed in old_ref but were removed by the user stay deleted
    # unless they are in restore_keys.
    inserted: List[str] = []
    restored: List[str] = []
    seen_keys = set(updated) | set(skipped) | set(kept)
    for ni, seg in enumerate(new_segments):
        if seg.kind != "marker":
            continue
        is_new = seg.marker_key not in old_map and seg.marker_key not in seen_keys
        is_restore = seg.marker_key in restore_keys and seg.marker_key in deleted_details
        if not is_new and not is_restore:
            continue
        if is_new and seg.marker_key in skip_insert_keys:
            continue
        if seg.marker_key in seen_keys:
            continue

        # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-find-anchor
        # Find nearest preceding known marker in new_segments as anchor
        anchor_key = None
        for pi in range(ni - 1, -1, -1):
            prev = new_segments[pi]
            if prev.kind == "marker" and prev.marker_key in seen_keys:
                anchor_key = prev.marker_key
                break
        # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-find-anchor

        insert_idx = len(merged_parts)  # default: append at end
        # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-insert-after-anchor
        if anchor_key is not None:
            for mi in range(len(merged_parts) - 1, -1, -1):
                if merged_parts[mi][1] == anchor_key:
                    insert_idx = mi + 1
                    break
        # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-insert-after-anchor
        # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-insert-fallback
        elif anchor_key is None:
            # No preceding anchor found — search forward for nearest following
            # known marker in new_segments and insert before it
            for fi in range(ni + 1, len(new_segments)):
                fwd = new_segments[fi]
                if fwd.kind == "marker" and fwd.marker_key in seen_keys:
                    fwd_key = fwd.marker_key
                    for mi in range(len(merged_parts)):
                        if merged_parts[mi][1] == fwd_key:
                            insert_idx = mi
                            break
                    break
            # If still no match, insert_idx stays at len(merged_parts) — append
        # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-insert-fallback

        if seg.marker_key in modify_overrides:
            merged_parts.insert(insert_idx, (modify_overrides[seg.marker_key], seg.marker_key))
            modified.append(seg.marker_key)
        else:
            merged_parts.insert(insert_idx, (seg.raw, seg.marker_key))
        if is_restore:
            restored.append(seg.marker_key)
        else:
            inserted.append(seg.marker_key)
        seen_keys.add(seg.marker_key)
    # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-insert-new

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p2:inst-upgrade-legacy
    # Upgrade legacy markers to named syntax in the merged output
    merged_parts, upgraded, upgraded_details = _upgrade_legacy_tags(merged_parts)
    # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p2:inst-upgrade-legacy

    # @cpt-begin:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-return-merge
    merged_text = "".join(part[0] for part in merged_parts)
    # Remove restored markers from deleted list
    deleted = [k for k in deleted if k not in restored]
    report = {
        "updated": updated, "updated_details": updated_details,
        "skipped": skipped, "skipped_details": skipped_details,
        "deleted": deleted, "deleted_details": deleted_details,
        "restored": restored,
        "ref_removed": [k for k in ref_removed if k not in remove_keys],
        "ref_removed_details": ref_removed_details,
        "removed": [k for k in ref_removed if k in remove_keys],
        "kept": kept, "inserted": inserted,
        "modified": modified,
        "upgraded": list(dict.fromkeys(list(norm_upgraded_details) + upgraded)),
        "upgraded_details": {**norm_upgraded_details, **upgraded_details},
    }
    return merged_text, report
    # @cpt-end:cpt-cypilot-algo-blueprint-system-three-way-merge:p1:inst-return-merge

# ---------------------------------------------------------------------------
# Kit Migrate — conf.toml helpers
# @cpt-algo:cpt-cypilot-algo-blueprint-system-conf-toml-helpers:p1
# ---------------------------------------------------------------------------

def _read_conf_toml(conf_path: Path) -> Dict[str, Any]:
    """Read and parse a conf.toml file. Returns empty dict on failure."""
    # @cpt-begin:cpt-cypilot-algo-blueprint-system-conf-toml-helpers:p1:inst-read-conf
    if not conf_path.is_file():
        return {}
    try:
        import tomllib
        with open(conf_path, "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}
    # @cpt-end:cpt-cypilot-algo-blueprint-system-conf-toml-helpers:p1:inst-read-conf

def _read_conf_version(conf_path: Path) -> int:
    """Read top-level 'version' from conf.toml. Returns 0 if missing."""
    # @cpt-begin:cpt-cypilot-algo-blueprint-system-conf-toml-helpers:p1:inst-read-version
    if not conf_path.is_file():
        return 0
    try:
        import tomllib
        with open(conf_path, "rb") as f:
            data = tomllib.load(f)
        ver = data.get("version")
        return int(ver) if ver is not None else 0
    except Exception:
        return 0
    # @cpt-end:cpt-cypilot-algo-blueprint-system-conf-toml-helpers:p1:inst-read-version

def _read_whatsnew(conf_path: Path) -> Dict[int, Dict[str, str]]:
    """Read [whatsnew] section from conf.toml.

    Returns dict mapping version (int) to {summary, details}.
    """
    data = _read_conf_toml(conf_path)
    raw = data.get("whatsnew", {})
    result: Dict[int, Dict[str, str]] = {}
    for key, entry in raw.items():
        try:
            ver = int(key)
        except (ValueError, TypeError):
            continue
        if isinstance(entry, dict):
            result[ver] = {
                "summary": str(entry.get("summary", "")),
                "details": str(entry.get("details", "")),
            }
    return result

def _show_whatsnew(
    kit_slug: str,
    ref_whatsnew: Dict[int, Dict[str, str]],
    user_whatsnew: Dict[int, Dict[str, str]],
    *,
    interactive: bool = True,
) -> bool:
    """Display whatsnew entries present in ref but missing from user config.

    Compares ref vs user whatsnew keys; shows only entries the user hasn't seen.
    Returns True if user acknowledged (or non-interactive), False if declined.
    """
    missing = sorted(
        (v, ref_whatsnew[v]) for v in ref_whatsnew
        if v not in user_whatsnew
    )
    if not missing:
        return True

    sys.stderr.write(f"\n{'=' * 60}\n")
    sys.stderr.write(f"  What's new in kit '{kit_slug}'\n")
    sys.stderr.write(f"{'=' * 60}\n")

    for ver, entry in missing:
        sys.stderr.write(f"\n  \033[1mv{ver}: {entry['summary']}\033[0m\n")
        if entry["details"]:
            for line in entry["details"].splitlines():
                sys.stderr.write(f"    {line}\n")

    sys.stderr.write(f"\n{'=' * 60}\n")

    if not interactive:
        return True

    sys.stderr.write("  Press Enter to continue with migration (or 'q' to abort): ")
    sys.stderr.flush()
    try:
        response = input().strip().lower()
    except EOFError:
        return False
    return response != "q"

def update_kit(
    kit_slug: str,
    source_dir: Path,
    cypilot_dir: Path,
    *,
    dry_run: bool = False,
    interactive: bool = True,
    auto_approve: bool = False,
) -> Dict[str, Any]:
    """Full update cycle for a single kit.

    Args:
        kit_slug: Kit identifier (e.g. "sdlc").
        source_dir: New kit data (e.g. cache/kits/{slug}/ or local dir).
        cypilot_dir: Project adapter directory.
        dry_run: If True, don't write files.
        interactive: If True, prompt user for confirmation before writing.
        auto_approve: If True, skip all prompts (equivalent to 'all').

    Steps:
        1. Save .prev/ snapshot of current reference
        2. Copy new reference from source → kits/{slug}/
        3. First-install or version-check + auto-migrate user blueprints
        4. Copy scripts → .gen/kits/{slug}/scripts/
        5. Regenerate .gen/ from user blueprints (process_kit)

    Returns dict with reference, version, and gen results.
    """
    ref_dir = cypilot_dir / "kits" / kit_slug
    config_kit_dir = cypilot_dir / "config" / "kits" / kit_slug
    gen_kits_dir = cypilot_dir / ".gen" / "kits"

    result: Dict[str, Any] = {"kit": kit_slug}

    if dry_run:
        result["reference"] = "dry_run"
        result["version"] = {"status": "dry_run"}
        result["gen"] = "dry_run"
        return result

    # ── 1. Save .prev/ snapshot ──────────────────────────────────────────
    prev_dir = ref_dir / ".prev"
    if ref_dir.is_dir() and (ref_dir / "blueprints").is_dir():
        if prev_dir.exists():
            shutil.rmtree(prev_dir)
        prev_dir.mkdir(parents=True, exist_ok=True)
        old_bp = ref_dir / "blueprints"
        if old_bp.is_dir():
            shutil.copytree(old_bp, prev_dir / "blueprints")
        old_conf = ref_dir / "conf.toml"
        if old_conf.is_file():
            shutil.copy2(old_conf, prev_dir / "conf.toml")

    # ── 2. Copy new reference from source ────────────────────────────────
    for subdir_name in ("blueprints", "scripts"):
        src = source_dir / subdir_name
        dst = ref_dir / subdir_name
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dst)
    conf_src = source_dir / "conf.toml"
    if conf_src.is_file():
        ref_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(conf_src, ref_dir / "conf.toml")
    result["reference"] = "updated"

    # ── 3. First-install or version-check + migrate ──────────────────────
    user_bp_dir = config_kit_dir / "blueprints"

    if not user_bp_dir.is_dir():
        # First install — copy blueprints + conf.toml to config/
        src_bp = source_dir / "blueprints"
        if src_bp.is_dir():
            user_bp_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src_bp, user_bp_dir)
        if conf_src.is_file():
            config_kit_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(conf_src, config_kit_dir / "conf.toml")
        result["version"] = {"status": "created"}
        # Clean up .prev/ — not needed after first install
        if prev_dir.is_dir():
            shutil.rmtree(prev_dir)
    else:
        # Check version drift and auto-migrate
        mig_result = migrate_kit(
            kit_slug, ref_dir, config_kit_dir,
            interactive=interactive, auto_approve=auto_approve,
        )
        result["version"] = mig_result

    # ── 4. Copy scripts → .gen/kits/{slug}/scripts/ ──────────────────────
    scripts_src = source_dir / "scripts"
    if scripts_src.is_dir():
        gen_kit_scripts = gen_kits_dir / kit_slug / "scripts"
        if gen_kit_scripts.exists():
            shutil.rmtree(gen_kit_scripts)
        gen_kit_scripts.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(scripts_src, gen_kit_scripts)

    # ── 5. Regenerate .gen/ from user blueprints ─────────────────────────
    from ..utils.blueprint import process_kit
    bp_dir = user_bp_dir if user_bp_dir.is_dir() else (ref_dir / "blueprints")
    if bp_dir.is_dir():
        summary, gen_errors = process_kit(
            kit_slug, bp_dir, gen_kits_dir, dry_run=False,
        )
        result["gen"] = {
            "files_written": summary.get("files_written", 0),
            "artifact_kinds": summary.get("artifact_kinds", []),
        }
        if gen_errors:
            result["gen_errors"] = gen_errors

        # Write per-kit SKILL.md + workflow files
        gen_out = _write_kit_gen_outputs(kit_slug, summary, gen_kits_dir)
        if gen_out["skill_nav"]:
            result["skill_nav"] = gen_out["skill_nav"]

        sysprompt_content = summary.get("sysprompt_content", "")
        if sysprompt_content:
            result["agents_content"] = sysprompt_content
    else:
        result["gen"] = {"files_written": 0, "artifact_kinds": []}

    return result

# @cpt-flow:cpt-cypilot-flow-blueprint-system-kit-migrate:p1
def migrate_kit(
    kit_slug: str,
    ref_dir: Path,
    config_kit_dir: Path,
    *,
    dry_run: bool = False,
    interactive: bool = True,
    auto_approve: bool = False,
) -> Dict[str, Any]:
    """Migrate a single kit's config blueprints using marker-level three-way merge.

    Triggered by kit-level version drift (ref version > user version).
    When triggered, merges ALL blueprint .md files from reference into user config:
    - Unchanged markers → updated from new reference
    - Customized markers → skipped (preserved) unless force-overwritten
    - Deleted markers → NOT re-added

    When interactive=True, prompts user for confirmation before writing each file.
    Customized markers get a separate warning prompt.
    auto_approve=True skips all prompts (equivalent to answering 'all').

    Also updates config conf.toml.

    Returns dict with migration details.
    """
    ref_conf = _read_conf_toml(ref_dir / "conf.toml")
    user_conf = _read_conf_toml(config_kit_dir / "conf.toml")

    try:
        ref_kit_ver = int(ref_conf.get("version", 0))
    except (ValueError, TypeError):
        ref_kit_ver = 0
    try:
        user_kit_ver = int(user_conf.get("version", 0))
    except (ValueError, TypeError):
        user_kit_ver = 0

    version_bump = ref_kit_ver > user_kit_ver

    # Show whatsnew before migration starts
    if version_bump and not dry_run:
        ref_whatsnew = _read_whatsnew(ref_dir / "conf.toml")
        user_whatsnew = _read_whatsnew(config_kit_dir / "conf.toml")
        if ref_whatsnew:
            ack = _show_whatsnew(
                kit_slug, ref_whatsnew, user_whatsnew,
                interactive=interactive and not auto_approve,
            )
            if not ack:
                return {"kit": kit_slug, "status": "aborted"}

    # Directories
    ref_bp_dir = ref_dir / "blueprints"
    prev_bp_dir = ref_dir / ".prev" / "blueprints"  # old reference (saved by cpt update)
    user_bp_dir = config_kit_dir / "blueprints"

    # Merge ALL blueprint .md files from reference
    bp_results: List[Dict[str, Any]] = []
    apply_state: Dict[str, bool] = {"all": auto_approve}

    if ref_bp_dir.is_dir():
        for ref_file in sorted(ref_bp_dir.glob("*.md")):
            bp_name = ref_file.stem
            user_file = user_bp_dir / ref_file.name
            old_ref_file = prev_bp_dir / ref_file.name

            new_ref_text = ref_file.read_text(encoding="utf-8")

            if not user_file.is_file():
                # New blueprint — copy it
                if not dry_run:
                    user_bp_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ref_file, user_file)
                bp_results.append({
                    "blueprint": bp_name,
                    "action": "created",
                })
                continue

            user_text = user_file.read_text(encoding="utf-8")

            if old_ref_file.is_file():
                old_ref_text = old_ref_file.read_text(encoding="utf-8")
            else:
                # No .prev/ — conservative: treat new_ref as old_ref so all
                # user diffs are seen as "customized" and preserved.
                old_ref_text = new_ref_text

            merged_text, report = _three_way_merge_blueprint(
                old_ref_text, new_ref_text, user_text,
            )

            bp_report: Dict[str, Any] = {"blueprint": bp_name}
            if report["updated"]:
                bp_report["markers_updated"] = report["updated"]
            if report["skipped"]:
                bp_report["markers_skipped"] = report["skipped"]
            if report.get("inserted"):
                bp_report["markers_inserted"] = report["inserted"]
            if report.get("deleted"):
                bp_report["markers_deleted"] = report["deleted"]
            if report.get("ref_removed"):
                bp_report["markers_ref_removed"] = report["ref_removed"]

            text_changed = merged_text != user_text
            has_changes = (
                report["updated"] or report.get("inserted")
                or report["skipped"] or report.get("deleted")
                or report.get("ref_removed")
                or text_changed
            )

            if not has_changes:
                bp_report["action"] = "no_marker_changes"
                bp_results.append(bp_report)
                continue

            # ── Interactive: show all diffs, prompt per file ─────────
            if interactive and not dry_run:
                upd_details = report.get("updated_details", {})
                skip_details = report.get("skipped_details", {})
                n_upd = len(report["updated"])
                n_ins = len(report.get("inserted", []))
                n_skip = len(report["skipped"])
                n_del = len(report.get("deleted", []))
                n_rem = len(report.get("ref_removed", []))
                syntax_only = (
                    text_changed
                    and not n_upd and not n_ins
                    and not n_skip and not n_del and not n_rem
                )

                # Syntax-only upgrade: auto-apply, just log
                if syntax_only:
                    sys.stderr.write(f"\n  [{kit_slug}] {bp_name}: syntax upgrade\n")
                    upg_details = report.get("upgraded_details", {})
                    for k in report.get("upgraded", []):
                        if k in upg_details:
                            old_tag, new_tag = upg_details[k]
                            sys.stderr.write(f"      {old_tag} → {new_tag}\n")
                    bp_report["action"] = "merged"
                    bp_report["markers_upgraded"] = True
                    user_bp_dir.mkdir(parents=True, exist_ok=True)
                    user_file.write_text(merged_text, encoding="utf-8")
                    bp_results.append(bp_report)
                    continue

                # Content changes: prompt per marker
                sys.stderr.write(f"\n  [{kit_slug}] {bp_name}:\n")

                upg_details = report.get("upgraded_details", {})
                if report.get("upgraded"):
                    sys.stderr.write("    syntax upgrade (legacy → named markers):\n")
                    for k in report["upgraded"]:
                        if k in upg_details:
                            old_tag, new_tag = upg_details[k]
                            sys.stderr.write(f"      {old_tag} → {new_tag}\n")

                # Build inserted content map
                ins_map: Dict[str, str] = {}
                for seg in _parse_segments(new_ref_text):
                    if seg.kind == "marker" and seg.marker_key in set(report.get("inserted", [])):
                        ins_map[seg.marker_key] = seg.raw

                # Per-marker prompts: collect decisions
                declined_update: List[str] = []
                declined_insert: List[str] = []
                accepted_force: List[str] = []
                accepted_restore: List[str] = []
                accepted_remove: List[str] = []
                modify_overrides: Dict[str, str] = {}

                for k in report["updated"]:
                    sys.stderr.write(f"    ✎ {k} — updated from reference\n")
                    if k in upd_details:
                        _show_marker_diff(k, *upd_details[k])
                    ans = _prompt_confirm("    apply?", apply_state, allow_modify=True)
                    if ans == "n":
                        declined_update.append(k)
                    elif ans == "m" and k in upd_details:
                        old_raw, new_raw = upd_details[k]
                        edited = _open_editor_for_marker(k, old_raw, new_raw)
                        if edited is not None:
                            modify_overrides[k] = edited
                            sys.stderr.write(f"        ✓ manually edited\n")
                        else:
                            sys.stderr.write(f"        ✗ aborted — keeping yours\n")
                            declined_update.append(k)

                for k in report.get("inserted", []):
                    sys.stderr.write(f"    + {k} — new marker\n")
                    if k in ins_map:
                        _show_marker_content(ins_map[k], color="green")
                    ans = _prompt_confirm("    insert?", apply_state, allow_modify=True)
                    if ans == "n":
                        declined_insert.append(k)
                    elif ans == "m" and k in ins_map:
                        edited = _open_editor_for_marker(k, ins_map[k], ins_map[k])
                        if edited is not None:
                            modify_overrides[k] = edited
                            sys.stderr.write(f"        ✓ manually edited\n")
                        else:
                            sys.stderr.write(f"        ✗ aborted — skipping insert\n")
                            declined_insert.append(k)

                for k in report["skipped"]:
                    sys.stderr.write(f"    ≡ {k} — customized by you\n")
                    if k in skip_details:
                        _show_marker_diff(k, *skip_details[k])
                    ans = _prompt_confirm("    overwrite?", apply_state, allow_modify=True)
                    if ans == "y":
                        accepted_force.append(k)
                    elif ans == "m" and k in skip_details:
                        user_raw, new_raw = skip_details[k]
                        edited = _open_editor_for_marker(k, user_raw, new_raw)
                        if edited is not None:
                            modify_overrides[k] = edited
                            sys.stderr.write(f"        ✓ manually edited\n")
                        else:
                            sys.stderr.write(f"        ✗ aborted — keeping yours\n")

                del_details = report.get("deleted_details", {})
                for k in report.get("deleted", []):
                    sys.stderr.write(f"    ✗ {k} — deleted by you (exists in reference)\n")
                    if k in del_details:
                        _show_marker_content(del_details[k], color="red")
                    if _prompt_confirm("    restore?", apply_state) == "y":
                        accepted_restore.append(k)

                ref_rem_details = report.get("ref_removed_details", {})
                for k in report.get("ref_removed", []):
                    sys.stderr.write(f"    − {k} — removed from reference (will be deleted from config)\n")
                    if k in ref_rem_details:
                        _show_marker_content(ref_rem_details[k], color="red")
                    if _prompt_confirm("    remove?", apply_state) == "y":
                        accepted_remove.append(k)

                # Re-merge with per-marker decisions
                merged_text, report = _three_way_merge_blueprint(
                    old_ref_text, new_ref_text, user_text,
                    force_keys=frozenset(accepted_force),
                    restore_keys=frozenset(accepted_restore),
                    remove_keys=frozenset(accepted_remove),
                    skip_keys=frozenset(declined_update),
                    skip_insert_keys=frozenset(declined_insert),
                    modify_overrides=modify_overrides,
                )

                if merged_text == user_text:
                    bp_report["action"] = "declined"
                    bp_results.append(bp_report)
                    continue

                # Rebuild bp_report from final merge
                bp_report = {"blueprint": bp_name}
                if report["updated"]:
                    bp_report["markers_updated"] = report["updated"]
                if report["skipped"]:
                    bp_report["markers_skipped"] = report["skipped"]
                if report.get("inserted"):
                    bp_report["markers_inserted"] = report["inserted"]
                if report.get("restored"):
                    bp_report["markers_restored"] = report["restored"]
                if report.get("modified"):
                    bp_report["markers_modified"] = report["modified"]
                if accepted_force:
                    bp_report["markers_forced"] = accepted_force
                if declined_update:
                    bp_report["markers_declined"] = declined_update
                if declined_insert:
                    bp_report["markers_insert_declined"] = declined_insert

                bp_report["action"] = "merged"
                if (not report["updated"] and not report.get("inserted")
                        and not report.get("modified")):
                    bp_report["markers_upgraded"] = True
                user_bp_dir.mkdir(parents=True, exist_ok=True)
                user_file.write_text(merged_text, encoding="utf-8")

            else:
                # Non-interactive / dry-run path
                bp_report["action"] = "merged"
                if text_changed and not report["updated"] and not report.get("inserted"):
                    bp_report["markers_upgraded"] = True
                if not dry_run:
                    user_bp_dir.mkdir(parents=True, exist_ok=True)
                    user_file.write_text(merged_text, encoding="utf-8")

            bp_results.append(bp_report)

    # Check if any changes were actually applied
    has_applied_changes = any(
        r.get("action") in ("merged", "created")
        for r in bp_results
    )
    all_declined = bp_results and not has_applied_changes and any(
        r.get("action") == "declined" for r in bp_results
    )

    if not has_applied_changes and not version_bump:
        # No applied changes and no version bump — clean up .prev/ and return current
        if not dry_run:
            prev_dir = ref_dir / ".prev"
            if prev_dir.is_dir():
                shutil.rmtree(prev_dir)
        return {"kit": kit_slug, "status": "current"}

    kit_ver_label = f"v{user_kit_ver} → v{ref_kit_ver}"

    # Update config conf.toml only on version bump with real applied changes;
    # don't bump version if user declined all changes (re-prompt on next update)
    if version_bump and not dry_run and not all_declined:
        ref_conf_file = ref_dir / "conf.toml"
        user_conf_file = config_kit_dir / "conf.toml"
        if ref_conf_file.is_file():
            config_kit_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ref_conf_file, user_conf_file)

    # Clean up .prev/ after successful migration (keep if all declined — needed for retry)
    if not dry_run and not all_declined:
        prev_dir = ref_dir / ".prev"
        if prev_dir.is_dir():
            shutil.rmtree(prev_dir)

    result: Dict[str, Any] = {
        "kit": kit_slug,
        "status": "migrated",
        "kit_version": kit_ver_label,
    }
    if bp_results:
        result["blueprints"] = bp_results
    return result

def cmd_kit_migrate(argv: List[str]) -> int:
    """Migrate kit blueprints to latest versions from reference.

    Usage: cypilot kit migrate [--kit SLUG] [--dry-run]

    For each kit where conf.toml versions differ between reference and config:
    - Copies updated blueprints from reference to config
    - Updates config conf.toml to match reference versions
    - Regenerates .gen/ from updated blueprints
    """
    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-migrate:p1:inst-user-migrate
    p = argparse.ArgumentParser(
        prog="kit migrate",
        description="Migrate kit blueprints to latest versions",
    )
    p.add_argument("--kit", default=None, help="Kit slug to migrate (default: all)")
    p.add_argument("--dry-run", action="store_true", help="Show what would be done")
    p.add_argument("--no-interactive", action="store_true",
                   help="Disable interactive prompts (auto-skip customized markers)")
    p.add_argument("-y", "--yes", action="store_true",
                   help="Auto-approve all prompts (no interaction)")
    args = p.parse_args(argv)
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-migrate:p1:inst-user-migrate

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-migrate:p1:inst-resolve-migrate-kits
    resolved = _resolve_cypilot_dir()
    if resolved is None:
        return 1
    _, cypilot_dir = resolved
    config_dir = cypilot_dir / "config"
    gen_dir = cypilot_dir / ".gen"
    kits_ref_dir = cypilot_dir / "kits"

    if not kits_ref_dir.is_dir():
        ui.result({"status": "FAIL", "message": "No kits installed", "hint": "Run 'cypilot kit install <path>' first"})
        return 2

    # Resolve kit dirs
    if args.kit:
        kit_dirs = [kits_ref_dir / args.kit]
        if not kit_dirs[0].is_dir():
            ui.result({"status": "FAIL", "message": f"Kit '{args.kit}' not found in {kits_ref_dir}"})
            return 2
    else:
        kit_dirs = [d for d in sorted(kits_ref_dir.iterdir()) if d.is_dir()]
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-migrate:p1:inst-resolve-migrate-kits

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-migrate:p1:inst-foreach-migrate-kit
    gen_kits_dir = gen_dir / "kits"
    results: List[Dict[str, Any]] = []

    for kit_dir in kit_dirs:
        kit_slug = kit_dir.name
        config_kit_dir = config_dir / "kits" / kit_slug
        interactive = not args.no_interactive and sys.stdin.isatty()
        result = migrate_kit(
            kit_slug, kit_dir, config_kit_dir,
            dry_run=args.dry_run,
            interactive=interactive,
            auto_approve=args.yes,
        )
        # Regenerate .gen/ after successful migration
        if result["status"] == "migrated" and not args.dry_run:
            user_bp_dir = config_kit_dir / "blueprints"
            bp_dir = user_bp_dir if user_bp_dir.is_dir() else (kit_dir / "blueprints")
            if bp_dir.is_dir():
                from ..utils.blueprint import process_kit
                try:
                    summary, _errors = process_kit(
                        kit_slug, bp_dir, gen_kits_dir, dry_run=False,
                    )
                    gen_out = _write_kit_gen_outputs(kit_slug, summary, gen_kits_dir)
                    result["regenerated"] = {
                        "files_written": summary.get("files_written", 0),
                        "artifact_kinds": summary.get("artifact_kinds", []),
                        "workflows_written": gen_out["workflows_written"],
                    }
                except Exception as err:
                    result["status"] = "FAIL"
                    result["regenerated"] = {"error": str(err)}
                    sys.stderr.write(f"kit-migrate: regen failed for {kit_slug}: {err}\n")
        results.append(result)
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-migrate:p1:inst-foreach-migrate-kit

    # @cpt-begin:cpt-cypilot-flow-blueprint-system-kit-migrate:p1:inst-return-migrate-ok
    migrated_count = sum(1 for r in results if r["status"] == "migrated")
    aborted_count = sum(1 for r in results if r["status"] == "aborted")
    has_failures = any(r["status"] == "FAIL" for r in results)
    output: Dict[str, Any] = {
        "status": "FAIL" if has_failures else ("ABORTED" if aborted_count and not migrated_count else "PASS"),
        "kits_migrated": migrated_count,
        "kits_current": len(results) - migrated_count - aborted_count,
        "results": results,
    }
    if aborted_count:
        output["kits_aborted"] = aborted_count
    if args.dry_run:
        output["dry_run"] = True

    ui.result(output, human_fn=lambda d: _human_kit_migrate(d))
    return 0
    # @cpt-end:cpt-cypilot-flow-blueprint-system-kit-migrate:p1:inst-return-migrate-ok

def _human_kit_migrate(data: dict) -> None:
    status = data.get("status", "")
    dry = data.get("dry_run", False)

    ui.header("Kit Migrate" + (" (dry run)" if dry else ""))
    ui.detail("Migrated", str(data.get("kits_migrated", 0)))
    ui.detail("Current", str(data.get("kits_current", 0)))
    if data.get("kits_aborted"):
        ui.detail("Aborted", str(data["kits_aborted"]))

    for r in data.get("results", []):
        kit_slug = r.get("kit", "?")
        rs = r.get("status", "?")
        from_v = r.get("from_version")
        to_v = r.get("to_version")
        ver_str = ""
        if from_v is not None and to_v is not None:
            ver_str = f" v{from_v} → v{to_v}"

        if rs == "migrated":
            ui.step(f"{kit_slug}: migrated{ver_str}")
            regen = r.get("regenerated", {})
            if regen:
                fw = regen.get("files_written", 0)
                ww = regen.get("workflows_written", 0)
                err = regen.get("error")
                if err:
                    ui.warn(f"  Regen failed: {err}")
                else:
                    ui.substep(f"  Regenerated: {fw} files, {ww} workflows")
            # Show merge details
            merged = r.get("merged_blueprints", [])
            for mb in merged:
                bp_name = mb.get("blueprint", "?")
                accepted = mb.get("accepted", 0)
                declined = mb.get("declined", 0)
                inserted = mb.get("inserted", 0)
                deleted = mb.get("deleted", 0)
                parts = []
                if accepted:
                    parts.append(f"{accepted} accepted")
                if declined:
                    parts.append(f"{declined} declined")
                if inserted:
                    parts.append(f"{inserted} inserted")
                if deleted:
                    parts.append(f"{deleted} deleted")
                if parts:
                    ui.substep(f"  {bp_name}: {', '.join(parts)}")
        elif rs == "current":
            ui.step(f"{kit_slug}: already current{ver_str}")
        elif rs == "aborted":
            ui.warn(f"{kit_slug}: aborted{ver_str}")
        elif rs == "FAIL":
            msg = r.get("message", "")
            ui.warn(f"{kit_slug}: FAILED — {msg}")
        else:
            ui.substep(f"{kit_slug}: {rs}")

    if status == "PASS":
        if dry:
            ui.success("Dry run complete — no files written.")
        else:
            ui.success("Kit migration complete.")
    elif status == "ABORTED":
        ui.warn("Migration aborted.")
    elif status == "FAIL":
        ui.error("Migration failed.")
    else:
        ui.info(f"Status: {status}")
    ui.blank()

# ---------------------------------------------------------------------------
# Kit CLI dispatcher (handles `cypilot kit <subcommand>`)
# ---------------------------------------------------------------------------

def cmd_kit(argv: List[str]) -> int:
    """Kit management command dispatcher.

    Usage: cypilot kit <install|update|migrate> [options]
    """
    if not argv:
        ui.result({"status": "ERROR", "message": "Missing kit subcommand", "subcommands": ["install", "update", "migrate"]})
        return 1

    subcmd = argv[0]
    rest = argv[1:]

    if subcmd == "install":
        return cmd_kit_install(rest)
    elif subcmd == "update":
        return cmd_kit_update(rest)
    elif subcmd == "migrate":
        return cmd_kit_migrate(rest)
    else:
        ui.result({"status": "ERROR", "message": f"Unknown kit subcommand: {subcmd}", "subcommands": ["install", "update", "migrate"]})
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
