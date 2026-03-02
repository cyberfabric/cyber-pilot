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
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


# Subdirectories to copy from kit source (reference + install)
KIT_COPY_SUBDIRS = ["blueprints", "scripts"]


# ---------------------------------------------------------------------------
# Config seeding — copy default .toml configs from kit scripts to config/
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
    for src in gen_scripts_dir.iterdir():
        if src.is_file() and src.suffix in _CONFIG_EXTENSIONS:
            dst = config_dir / src.name
            if not dst.exists():
                shutil.copy2(src, dst)
                actions[f"config_{src.stem}"] = "seeded"


# ---------------------------------------------------------------------------
# Shared CLI helper — resolve project root + cypilot directory
# ---------------------------------------------------------------------------


def _resolve_cypilot_dir() -> Optional[tuple]:
    """Resolve project root and cypilot directory from CWD.

    Returns (project_root, cypilot_dir) or None (after printing JSON error).
    """
    from ..utils.files import find_project_root, _read_cypilot_var

    project_root = find_project_root(Path.cwd())
    if project_root is None:
        print(json.dumps({"status": "ERROR", "message": "No project root found"}, ensure_ascii=False))
        return None

    cypilot_rel = _read_cypilot_var(project_root)
    if not cypilot_rel:
        print(json.dumps({"status": "ERROR", "message": "No cypilot directory"}, ensure_ascii=False))
        return None

    cypilot_dir = (project_root / cypilot_rel).resolve()
    return project_root, cypilot_dir


# ---------------------------------------------------------------------------
# Shared helper — write per-kit SKILL.md + workflow files into .gen/
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

    return result


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
            print(f"kit-install: failed to read {conf_toml}: {exc}",
                  file=sys.stderr)

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

    resolved = _resolve_cypilot_dir()
    if resolved is None:
        return 1
    _, cypilot_dir = resolved
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
# Kit Migrate — marker-level three-way merge
# ---------------------------------------------------------------------------

# Regex mirrors blueprint.py parser
_MIG_OPEN_RE = re.compile(r"^`@cpt:(\w[\w-]*)` *$")
_MIG_CLOSE_RE = re.compile(r"^`@/cpt:(\w[\w-]*)` *$")


@dataclass
class _Segment:
    """A contiguous block inside a blueprint: either plain text or a @cpt: marker."""
    kind: str           # "text" or "marker"
    raw: str            # full raw text (including open/close tags for markers)
    marker_type: str = ""   # e.g. "heading", "workflow", "skill" (empty for text)
    marker_key: str = ""    # stable identity key


def _marker_identity_key(marker_type: str, raw_content: str) -> str:
    """Derive a stable identity key for a marker from its type and TOML data.

    Keys:
      blueprint        → "blueprint"
      skill            → "skill"
      workflow:{name}   → workflow identified by name
      heading:{template} → heading identified by template text
      id:{kind}        → id marker by kind
      example:{index}  → fallback positional (handled by caller)
      {type}:{index}   → fallback positional (handled by caller)
    """
    # Quick TOML key extraction without full parser
    def _toml_val(key: str) -> str:
        for line in raw_content.splitlines():
            stripped = line.strip()
            if (stripped.startswith(f"{key} ") or stripped.startswith(f"{key}=")) and "=" in stripped:
                _, _, val = stripped.partition("=")
                return val.strip().strip('"').strip("'")
        return ""

    if marker_type in ("blueprint", "skill"):
        return marker_type
    if marker_type == "workflow":
        name = _toml_val("name")
        return f"workflow:{name}" if name else "workflow"
    if marker_type == "heading":
        # Use the stable `id` field as primary key; fall back to level.
        # Duplicate same-level headings are disambiguated by positional index.
        hid = _toml_val("id")
        if hid:
            return f"heading:{hid}"
        level = _toml_val("level")
        return f"heading:L{level}" if level else "heading"
    if marker_type == "id":
        kind = _toml_val("kind")
        return f"id:{kind}" if kind else "id"
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
        marker_lines: List[str] = [lines[i]]
        j = i + 1
        found_close = False
        while j < len(lines):
            marker_lines.append(lines[j])
            close_stripped = lines[j].rstrip("\n\r")
            m_close = _MIG_CLOSE_RE.match(close_stripped.strip())
            if m_close and m_close.group(1) == marker_type:
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
        key = _marker_identity_key(marker_type, raw_content)

        segments.append(_Segment(
            kind="marker",
            raw=raw,
            marker_type=marker_type,
            marker_key=key,
        ))
        i = j

    if text_buf:
        segments.append(_Segment(kind="text", raw="".join(text_buf)))

    # Always add positional index per base key for consistent matching
    # across files that may have different numbers of markers.
    key_seen: Dict[str, int] = {}
    for seg in segments:
        if seg.kind != "marker":
            continue
        base = seg.marker_key
        idx = key_seen.get(base, 0)
        key_seen[base] = idx + 1
        seg.marker_key = f"{base}#{idx}"

    return segments


def _three_way_merge_blueprint(
    old_ref_text: str,
    new_ref_text: str,
    user_text: str,
) -> tuple:
    """Three-way merge of a blueprint at the @cpt: marker level.

    Args:
        old_ref_text: Previous reference version (before update).
        new_ref_text: New reference version (after update).
        user_text: User's current config copy.

    Returns:
        (merged_text, report) where report is a dict with:
        - updated: list of marker keys that were updated
        - skipped: list of marker keys skipped (user customized)
        - kept: list of marker keys kept as-is (no change in reference)
    """
    old_segments = _parse_segments(old_ref_text)
    new_segments = _parse_segments(new_ref_text)
    user_segments = _parse_segments(user_text)

    # Build lookup maps: key → raw text
    old_map: Dict[str, str] = {}
    for seg in old_segments:
        if seg.kind == "marker":
            old_map[seg.marker_key] = seg.raw

    new_map: Dict[str, str] = {}
    for seg in new_segments:
        if seg.kind == "marker":
            new_map[seg.marker_key] = seg.raw

    updated: List[str] = []
    skipped: List[str] = []
    kept: List[str] = []
    # Each element: (raw_text, marker_key or None)
    merged_parts: List[tuple] = []

    for seg in user_segments:
        if seg.kind == "text":
            merged_parts.append((seg.raw, None))
            continue

        key = seg.marker_key
        old_raw = old_map.get(key)
        new_raw = new_map.get(key)

        if old_raw is None:
            # Marker not in old reference — user-added or unknown, keep as-is
            merged_parts.append((seg.raw, key))
            kept.append(key)
        elif new_raw is None:
            # Marker removed in new reference — keep user's version
            merged_parts.append((seg.raw, key))
            kept.append(key)
        elif seg.raw == old_raw:
            # User hasn't changed it — safe to update
            if new_raw != old_raw:
                merged_parts.append((new_raw, key))
                updated.append(key)
            else:
                merged_parts.append((seg.raw, key))
                kept.append(key)
        else:
            # User customized this marker — skip update
            merged_parts.append((seg.raw, key))
            skipped.append(key)

    # Insert markers that are truly new (in new_ref but NOT in old_ref)
    # at their correct position based on new_segments ordering.
    # Markers that existed in old_ref but were removed by the user stay deleted.
    inserted: List[str] = []
    seen_keys = set(updated) | set(skipped) | set(kept)
    for ni, seg in enumerate(new_segments):
        if seg.kind != "marker":
            continue
        if seg.marker_key in seen_keys or seg.marker_key in old_map:
            continue

        # Find nearest preceding known marker in new_segments as anchor
        anchor_key = None
        for pi in range(ni - 1, -1, -1):
            prev = new_segments[pi]
            if prev.kind == "marker" and prev.marker_key in seen_keys:
                anchor_key = prev.marker_key
                break

        # Find anchor position in merged_parts and insert after it
        insert_idx = 0
        if anchor_key is not None:
            for mi in range(len(merged_parts) - 1, -1, -1):
                if merged_parts[mi][1] == anchor_key:
                    insert_idx = mi + 1
                    break

        merged_parts.insert(insert_idx, (seg.raw, seg.marker_key))
        inserted.append(seg.marker_key)
        seen_keys.add(seg.marker_key)

    merged_text = "".join(part[0] for part in merged_parts)
    report = {
        "updated": updated, "skipped": skipped,
        "kept": kept, "inserted": inserted,
    }
    return merged_text, report


# ---------------------------------------------------------------------------
# Kit Migrate — conf.toml helpers
# ---------------------------------------------------------------------------


def _read_conf_toml(conf_path: Path) -> Dict[str, Any]:
    """Read and parse a conf.toml file. Returns empty dict on failure."""
    if not conf_path.is_file():
        return {}
    try:
        import tomllib
        with open(conf_path, "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


def _read_conf_version(conf_path: Path) -> int:
    """Read top-level 'version' from conf.toml. Returns 0 if missing."""
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


def update_kit(
    kit_slug: str,
    source_dir: Path,
    cypilot_dir: Path,
    *,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Full update cycle for a single kit.

    Args:
        kit_slug: Kit identifier (e.g. "sdlc").
        source_dir: New kit data (e.g. cache/kits/{slug}/ or local dir).
        cypilot_dir: Project adapter directory.
        dry_run: If True, don't write files.

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
    else:
        # Check version drift and auto-migrate
        mig_result = migrate_kit(
            kit_slug, ref_dir, config_kit_dir,
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


def migrate_kit(
    kit_slug: str,
    ref_dir: Path,
    config_kit_dir: Path,
    *,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Migrate a single kit's config blueprints using marker-level three-way merge.

    Triggered by kit-level version drift (ref version > user version).
    When triggered, merges ALL blueprint .md files from reference into user config:
    - Unchanged markers → updated from new reference
    - Customized markers → skipped (preserved)
    - Deleted markers → NOT re-added

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

    if ref_kit_ver <= user_kit_ver:
        return {"kit": kit_slug, "status": "current"}

    # Directories
    ref_bp_dir = ref_dir / "blueprints"
    prev_bp_dir = ref_dir / ".prev" / "blueprints"  # old reference (saved by cpt update)
    user_bp_dir = config_kit_dir / "blueprints"

    # Merge ALL blueprint .md files from reference
    bp_results: List[Dict[str, Any]] = []

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
                merged_text, report = _three_way_merge_blueprint(
                    old_ref_text, new_ref_text, user_text,
                )
            else:
                # No .prev/ — conservative: treat new_ref as old_ref so all
                # user diffs are seen as "customized" and preserved.
                merged_text, report = _three_way_merge_blueprint(
                    new_ref_text, new_ref_text, user_text,
                )

            bp_report: Dict[str, Any] = {"blueprint": bp_name}
            if report["updated"]:
                bp_report["markers_updated"] = report["updated"]
            if report["skipped"]:
                bp_report["markers_skipped"] = report["skipped"]
            if report.get("inserted"):
                bp_report["markers_inserted"] = report["inserted"]

            if report["updated"] or report.get("inserted"):
                bp_report["action"] = "merged"
                if not dry_run:
                    user_bp_dir.mkdir(parents=True, exist_ok=True)
                    user_file.write_text(merged_text, encoding="utf-8")
            elif report["skipped"]:
                bp_report["action"] = "skipped_all_customized"
            else:
                bp_report["action"] = "no_marker_changes"

            bp_results.append(bp_report)

    kit_ver_label = f"v{user_kit_ver} → v{ref_kit_ver}"

    # Update config conf.toml to match reference
    if not dry_run:
        ref_conf_file = ref_dir / "conf.toml"
        user_conf_file = config_kit_dir / "conf.toml"
        if ref_conf_file.is_file():
            config_kit_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ref_conf_file, user_conf_file)

    # Clean up .prev/ after successful migration
    if not dry_run:
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
    p = argparse.ArgumentParser(
        prog="kit migrate",
        description="Migrate kit blueprints to latest versions",
    )
    p.add_argument("--kit", default=None, help="Kit slug to migrate (default: all)")
    p.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = p.parse_args(argv)

    resolved = _resolve_cypilot_dir()
    if resolved is None:
        return 1
    _, cypilot_dir = resolved
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

    # Resolve kit dirs
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

    gen_kits_dir = gen_dir / "kits"
    results: List[Dict[str, Any]] = []

    for kit_dir in kit_dirs:
        kit_slug = kit_dir.name
        config_kit_dir = config_dir / "kits" / kit_slug
        result = migrate_kit(
            kit_slug, kit_dir, config_kit_dir,
            dry_run=args.dry_run,
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
                    print(f"kit-migrate: regen failed for {kit_slug}: {err}",
                          file=sys.stderr)
        results.append(result)

    migrated_count = sum(1 for r in results if r["status"] == "migrated")
    has_failures = any(r["status"] == "FAIL" for r in results)
    output: Dict[str, Any] = {
        "status": "FAIL" if has_failures else "PASS",
        "kits_migrated": migrated_count,
        "kits_current": len(results) - migrated_count,
        "results": results,
    }
    if args.dry_run:
        output["dry_run"] = True

    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------------------
# Kit CLI dispatcher (handles `cypilot kit <subcommand>`)
# ---------------------------------------------------------------------------

def cmd_kit(argv: List[str]) -> int:
    """Kit management command dispatcher.

    Usage: cypilot kit <install|update|migrate> [options]
    """
    if not argv:
        print(json.dumps({
            "status": "ERROR",
            "message": "Missing kit subcommand",
            "subcommands": ["install", "update", "migrate"],
        }, indent=None, ensure_ascii=False))
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
        print(json.dumps({
            "status": "ERROR",
            "message": f"Unknown kit subcommand: {subcmd}",
            "subcommands": ["install", "update", "migrate"],
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
