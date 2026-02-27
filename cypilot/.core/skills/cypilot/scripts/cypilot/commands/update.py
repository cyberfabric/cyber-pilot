"""
Update command — refresh an existing Cypilot installation in-place.

Safety rules for config/:
- .core/  → full replace from cache (read-only reference)
- .gen/   → full regenerate from USER's blueprints in config/kits/
- config/ → NEVER overwrite user files:
  - core.toml, artifacts.toml   → only via migration when version is higher
  - AGENTS.md, SKILL.md, README.md → only create if missing
  - kits/{slug}/blueprints/     → skip if same version; warn if higher (migration needed)

Pipeline:
1. Replace .core/ from cache
2. Update kit reference copies (cypilot/kits/{slug}/) from cache
3. Compare blueprint versions: skip same, warn if migration needed
4. Regenerate .gen/ from user's blueprints
5. Ensure config/ scaffold files exist (create only if missing)
"""

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .init import (
    CACHE_DIR,
    COPY_DIRS,
    CORE_SUBDIR,
    GEN_SUBDIR,
    _copy_from_cache,
    _core_readme,
    _gen_readme,
    _inject_root_agents,
)


def cmd_update(argv: List[str]) -> int:
    """Update an existing Cypilot installation.

    Refreshes .core/ from cache, regenerates .gen/ from user blueprints.
    Never overwrites user config files.
    """
    p = argparse.ArgumentParser(
        prog="update",
        description="Update Cypilot installation (refresh .core, regenerate .gen)",
    )
    p.add_argument("--project-root", default=None, help="Project root directory")
    p.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = p.parse_args(argv)

    from ..utils.files import find_project_root, _read_cypilot_var

    cwd = Path.cwd().resolve()
    project_root = Path(args.project_root).resolve() if args.project_root else find_project_root(cwd)

    if project_root is None:
        print(json.dumps({
            "status": "ERROR",
            "message": "No project root found. Run 'cpt init' first.",
        }, indent=2, ensure_ascii=False))
        return 1

    install_rel = _read_cypilot_var(project_root)
    if not install_rel:
        print(json.dumps({
            "status": "ERROR",
            "message": "Cypilot not initialized in this project. Run 'cpt init' first.",
            "project_root": project_root.as_posix(),
        }, indent=2, ensure_ascii=False))
        return 1

    cypilot_dir = (project_root / install_rel).resolve()
    if not cypilot_dir.is_dir():
        print(json.dumps({
            "status": "ERROR",
            "message": f"Cypilot directory not found: {cypilot_dir}",
            "project_root": project_root.as_posix(),
        }, indent=2, ensure_ascii=False))
        return 1

    if not CACHE_DIR.is_dir():
        print(json.dumps({
            "status": "ERROR",
            "message": f"Cache not found at {CACHE_DIR}. Run 'cpt update' (proxy downloads first).",
        }, indent=2, ensure_ascii=False))
        return 1

    actions: Dict[str, Any] = {}
    errors: List[Dict[str, str]] = []
    warnings: List[str] = []

    core_dir = cypilot_dir / CORE_SUBDIR
    gen_dir = cypilot_dir / GEN_SUBDIR
    config_dir = cypilot_dir / "config"

    # ── Step 1: Replace .core/ from cache (always force) ─────────────────
    sys.stderr.write("Step 1: Updating .core/ from cache...\n")
    if not args.dry_run:
        cypilot_dir.mkdir(parents=True, exist_ok=True)
        copy_results = _copy_from_cache(CACHE_DIR, cypilot_dir, force=True)
        core_dir.mkdir(parents=True, exist_ok=True)
        (core_dir / "README.md").write_text(_core_readme(), encoding="utf-8")
    else:
        copy_results = {d: "dry_run" for d in COPY_DIRS}
    actions["core_update"] = copy_results
    sys.stderr.write(f"  {copy_results}\n")

    # ── Step 2: Update kit reference copies (cypilot/kits/) from cache ───
    sys.stderr.write("Step 2: Updating kit references...\n")
    kits_cache_dir = CACHE_DIR / "kits"
    kits_ref_dir = cypilot_dir / "kits"

    if not args.dry_run and kits_cache_dir.is_dir():
        for kit_src in sorted(kits_cache_dir.iterdir()):
            if not kit_src.is_dir():
                continue
            kit_slug = kit_src.name
            ref_dst = kits_ref_dir / kit_slug
            # Reference copies are always overwritten (like .core/)
            for subdir_name in ("blueprints", "scripts"):
                src = kit_src / subdir_name
                dst = ref_dst / subdir_name
                if src.is_dir():
                    if dst.exists():
                        shutil.rmtree(dst)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(src, dst)
            # Copy conf.toml to reference
            conf_src = kit_src / "conf.toml"
            if conf_src.is_file():
                ref_dst.mkdir(parents=True, exist_ok=True)
                shutil.copy2(conf_src, ref_dst / "conf.toml")
            sys.stderr.write(f"  kits/{kit_slug}: reference updated\n")
    actions["kit_references"] = "updated"

    # ── Step 3: Compare kit versions via conf.toml ───────────────────────
    sys.stderr.write("Step 3: Checking kit versions...\n")
    kit_version_report: Dict[str, Any] = {}

    if kits_cache_dir.is_dir():
        for kit_src in sorted(kits_cache_dir.iterdir()):
            if not kit_src.is_dir() or not (kit_src / "blueprints").is_dir():
                continue
            kit_slug = kit_src.name
            user_kit_dir = config_dir / "kits" / kit_slug
            user_bp_dir = user_kit_dir / "blueprints"
            user_conf = user_kit_dir / "conf.toml"
            cache_conf = kit_src / "conf.toml"

            if not user_bp_dir.is_dir():
                # User blueprints don't exist yet — copy from cache (first install)
                if not args.dry_run:
                    user_bp_dir.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(kit_src / "blueprints", user_bp_dir)
                    # Copy conf.toml on first install
                    if cache_conf.is_file():
                        shutil.copy2(cache_conf, user_kit_dir / "conf.toml")
                kit_version_report[kit_slug] = {"status": "created"}
                sys.stderr.write(f"  {kit_slug}: blueprints created (first install)\n")
            else:
                # Compare versions via conf.toml
                cache_ver = _read_conf_version(cache_conf)
                user_ver = _read_conf_version(user_conf)
                cache_bp_versions = _read_conf_section(cache_conf, "blueprints")
                user_bp_versions = _read_conf_section(user_conf, "blueprints")
                cache_script_versions = _read_conf_section(cache_conf, "scripts")
                user_script_versions = _read_conf_section(user_conf, "scripts")

                drift = _compare_conf_versions(
                    cache_ver, user_ver,
                    cache_bp_versions, user_bp_versions,
                    cache_script_versions, user_script_versions,
                )
                kit_version_report[kit_slug] = drift

                if drift["status"] == "current":
                    sys.stderr.write(f"  {kit_slug}: v{user_ver} — up to date\n")
                elif drift["status"] == "migration_needed":
                    details: List[str] = []
                    if drift.get("kit_version_drift"):
                        details.append(f"kit v{user_ver} → v{cache_ver}")
                    for bp, d in drift.get("blueprint_drift", {}).items():
                        details.append(f"{bp} v{d['user']} → v{d['cache']}")
                    for sc, d in drift.get("script_drift", {}).items():
                        details.append(f"script/{sc} v{d['user']} → v{d['cache']}")
                    sys.stderr.write(
                        f"  {kit_slug}: MIGRATION NEEDED — {', '.join(details)}\n"
                        f"    Reference updated in kits/{kit_slug}/.\n"
                        f"    User config in config/kits/{kit_slug}/ NOT touched.\n"
                        f"    Review kits/{kit_slug}/ vs config/kits/{kit_slug}/, "
                        f"then run 'cpt generate-resources'.\n"
                    )
                    warnings.append(f"Kit '{kit_slug}': migration needed — {', '.join(details)}")

            # Copy scripts to .gen/kits/{slug}/scripts/ (always ok, generated)
            scripts_src = kit_src / "scripts"
            if not args.dry_run and scripts_src.is_dir():
                gen_kit_scripts = gen_dir / "kits" / kit_slug / "scripts"
                if gen_kit_scripts.exists():
                    shutil.rmtree(gen_kit_scripts)
                gen_kit_scripts.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(scripts_src, gen_kit_scripts)

    actions["kit_versions"] = kit_version_report

    # ── Step 4: Regenerate .gen/ from USER's blueprints ──────────────────
    sys.stderr.write("Step 4: Regenerating .gen/ from user blueprints...\n")
    from ..utils.blueprint import process_kit

    gen_dir.mkdir(parents=True, exist_ok=True)
    gen_kits_dir = gen_dir / "kits"
    gen_skill_nav_parts: List[str] = []
    gen_agents_parts: List[str] = []
    kit_gen_results: Dict[str, Any] = {}

    config_kits_dir = config_dir / "kits"
    if config_kits_dir.is_dir():
        for kit_dir in sorted(config_kits_dir.iterdir()):
            bp_dir = kit_dir / "blueprints"
            if not bp_dir.is_dir():
                continue
            kit_slug = kit_dir.name

            if args.dry_run:
                kit_gen_results[kit_slug] = "dry_run"
                continue

            summary, kit_errors = process_kit(
                kit_slug, bp_dir, gen_kits_dir, dry_run=False,
            )
            kit_gen_results[kit_slug] = {
                "files_written": summary.get("files_written", 0),
                "artifact_kinds": summary.get("artifact_kinds", []),
            }
            if kit_errors:
                errors.extend({"path": kit_slug, "error": e} for e in kit_errors)

            # Collect skill nav and sysprompt
            skill_content = summary.get("skill_content", "")
            if skill_content:
                art_kinds = [k.upper() for k in summary.get("artifact_kinds", []) if k]
                wf_names = [w["name"] for w in summary.get("workflows", []) if w.get("name")]
                desc_parts: list[str] = []
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
                gen_skill_nav_parts.append(
                    f"ALWAYS invoke `{{cypilot_path}}/.gen/kits/{kit_slug}/SKILL.md` FIRST"
                )

            sysprompt_content = summary.get("sysprompt_content", "")
            if sysprompt_content:
                gen_agents_parts.append(sysprompt_content)

            # Write generated workflows
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
                wf_path.write_text("\n".join(fm_lines) + "\n\n" + wf["content"] + "\n", encoding="utf-8")

            sys.stderr.write(
                f"  {kit_slug}: {summary.get('files_written', 0)} files generated\n"
            )

    actions["gen_kits"] = kit_gen_results

    # Write .gen/AGENTS.md
    if not args.dry_run:
        project_name = _read_project_name(config_dir) or "Cypilot"
        kit_id = "cypilot-sdlc"
        artifacts_when = (
            f"ALWAYS open and follow `{{cypilot_path}}/config/artifacts.toml` "
            f"WHEN Cypilot uses kit `{kit_id}` for artifact kinds: "
            f"PRD, DESIGN, DECOMPOSITION, ADR, FEATURE OR codebase"
        )
        gen_agents_content = "\n".join([
            f"# Cypilot: {project_name}",
            "",
            "## Navigation Rules",
            "",
            "ALWAYS open and follow `{cypilot_path}/.core/schemas/artifacts.schema.json` WHEN working with artifacts.toml",
            "",
            "ALWAYS open and follow `{cypilot_path}/.core/architecture/specs/artifacts-registry.md` WHEN working with artifacts.toml",
            "",
            artifacts_when,
            "",
        ])
        if gen_agents_parts:
            gen_agents_content = gen_agents_content.rstrip() + "\n\n" + "\n\n".join(gen_agents_parts) + "\n"
        (gen_dir / "AGENTS.md").write_text(gen_agents_content, encoding="utf-8")
        actions["gen_agents"] = "updated"

        # Write .gen/SKILL.md
        nav_rules = "\n\n".join(gen_skill_nav_parts) if gen_skill_nav_parts else ""
        (gen_dir / "SKILL.md").write_text(
            "# Cypilot Generated Skills\n\n"
            "This file routes to per-kit skill instructions.\n\n"
            + (nav_rules + "\n" if nav_rules else ""),
            encoding="utf-8",
        )
        actions["gen_skill"] = "updated"

        (gen_dir / "README.md").write_text(_gen_readme(), encoding="utf-8")

    # ── Step 5: Ensure config/ scaffold (create only if missing) ─────────
    sys.stderr.write("Step 5: Ensuring config/ scaffold...\n")
    if not args.dry_run:
        config_dir.mkdir(parents=True, exist_ok=True)
        _ensure_file(config_dir / "README.md", _config_readme_content(), actions, "config_readme")
        _ensure_file(
            config_dir / "AGENTS.md",
            "# Custom Agent Navigation Rules\n\n"
            "Add your project-specific WHEN rules here.\n"
            "These rules are loaded alongside the generated rules in `{cypilot_path}/.gen/AGENTS.md`.\n",
            actions, "config_agents",
        )
        _ensure_file(
            config_dir / "SKILL.md",
            "# Custom Skill Extensions\n\n"
            "Add your project-specific skill instructions here.\n"
            "These are loaded alongside the generated skills in `{cypilot_path}/.gen/SKILL.md`.\n",
            actions, "config_skill",
        )

    # Re-inject root AGENTS.md
    if not args.dry_run:
        root_agents_action = _inject_root_agents(project_root, install_rel)
        actions["root_agents"] = root_agents_action

    # ── Report ───────────────────────────────────────────────────────────
    status = "PASS" if not errors and not warnings else "WARN"
    result: Dict[str, Any] = {
        "status": status,
        "project_root": project_root.as_posix(),
        "cypilot_dir": cypilot_dir.as_posix(),
        "dry_run": bool(args.dry_run),
        "actions": actions,
    }
    if errors:
        result["errors"] = errors
    if warnings:
        result["warnings"] = warnings

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_file(path: Path, content: str, actions: Dict, key: str) -> None:
    """Create file only if it doesn't exist."""
    if path.is_file():
        actions[key] = "preserved"
    else:
        path.write_text(content, encoding="utf-8")
        actions[key] = "created"


def _config_readme_content() -> str:
    """README.md content for config/ directory."""
    return (
        "# config — User Configuration\n"
        "\n"
        "This directory contains **user-editable** configuration files.\n"
        "\n"
        "## Files\n"
        "\n"
        "- `core.toml` — project settings (system name, slug, kit references)\n"
        "- `artifacts.toml` — artifacts registry (systems, ignore patterns)\n"
        "- `AGENTS.md` — custom agent navigation rules\n"
        "- `SKILL.md` — custom skill extensions\n"
        "\n"
        "## Directories\n"
        "\n"
        "- `kits/{slug}/blueprints/` — editable copies of kit blueprints\n"
        "- `rules/` — project rules (auto-configured or user-defined)\n"
        "\n"
        "**These files are never overwritten by `cpt update`.**\n"
    )


def _read_project_name(config_dir: Path) -> Optional[str]:
    """Read project name from core.toml."""
    core_toml = config_dir / "core.toml"
    if not core_toml.is_file():
        return None
    try:
        import tomllib
        with open(core_toml, "rb") as f:
            data = tomllib.load(f)
        system = data.get("system", {})
        if isinstance(system, dict):
            name = system.get("name")
            if isinstance(name, str) and name.strip():
                return name.strip()
    except Exception:
        pass
    return None


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


def _read_conf_section(conf_path: Path, section: str) -> Dict[str, int]:
    """Read a [section] from conf.toml as {name: version_int}."""
    if not conf_path.is_file():
        return {}
    try:
        import tomllib
        with open(conf_path, "rb") as f:
            data = tomllib.load(f)
        raw = data.get(section, {})
        if not isinstance(raw, dict):
            return {}
        return {str(k): int(v) for k, v in raw.items()}
    except Exception:
        return {}


def _compare_conf_versions(
    cache_ver: int,
    user_ver: int,
    cache_bp: Dict[str, int],
    user_bp: Dict[str, int],
    cache_scripts: Dict[str, int],
    user_scripts: Dict[str, int],
) -> Dict[str, Any]:
    """Compare kit versions from conf.toml (cache vs user).

    Returns dict with status 'current' or 'migration_needed' plus drift details.
    """
    result: Dict[str, Any] = {"status": "current"}

    # Kit-level version drift
    if cache_ver > user_ver:
        result["kit_version_drift"] = {"cache": cache_ver, "user": user_ver}

    # Per-blueprint drift
    bp_drift: Dict[str, Dict[str, int]] = {}
    for name, cver in cache_bp.items():
        uver = user_bp.get(name, 0)
        if cver > uver:
            bp_drift[name] = {"cache": cver, "user": uver}
    if bp_drift:
        result["blueprint_drift"] = bp_drift

    # Per-script drift
    sc_drift: Dict[str, Dict[str, int]] = {}
    for name, cver in cache_scripts.items():
        uver = user_scripts.get(name, 0)
        if cver > uver:
            sc_drift[name] = {"cache": cver, "user": uver}
    if sc_drift:
        result["script_drift"] = sc_drift

    if result.get("kit_version_drift") or bp_drift or sc_drift:
        result["status"] = "migration_needed"

    return result
