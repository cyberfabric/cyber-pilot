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

@cpt-flow:cpt-cypilot-flow-version-config-update:p1
@cpt-algo:cpt-cypilot-algo-version-config-update-pipeline:p1
@cpt-algo:cpt-cypilot-algo-version-config-compare-versions:p1
@cpt-dod:cpt-cypilot-dod-version-config-update:p1
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
    _inject_root_claude,
)


def cmd_update(argv: List[str]) -> int:
    """Update an existing Cypilot installation.

    Refreshes .core/ from cache, regenerates .gen/ from user blueprints.
    Never overwrites user config files.
    """
    # @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-user-update
    p = argparse.ArgumentParser(
        prog="update",
        description="Update Cypilot installation (refresh .core, regenerate .gen)",
    )
    p.add_argument("--project-root", default=None, help="Project root directory")
    p.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = p.parse_args(argv)
    # @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-user-update

    # @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-resolve-project
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
    # @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-resolve-project

    actions: Dict[str, Any] = {}
    errors: List[Dict[str, str]] = []
    warnings: List[str] = []

    core_dir = cypilot_dir / CORE_SUBDIR
    gen_dir = cypilot_dir / GEN_SUBDIR
    config_dir = cypilot_dir / "config"

    # @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-replace-core
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
    # @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-replace-core

    # @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-update-kits
    # ── Step 2: Update kits (ref copy, migrate, regen .gen/) ─────────────
    sys.stderr.write("Step 2: Updating kits...\n")
    from .kit import update_kit

    kits_cache_dir = CACHE_DIR / "kits"
    if not args.dry_run:
        gen_dir.mkdir(parents=True, exist_ok=True)
    gen_skill_nav_parts: List[str] = []
    gen_agents_parts: List[str] = []
    kit_results: Dict[str, Any] = {}

    if kits_cache_dir.is_dir():
        for kit_src in sorted(kits_cache_dir.iterdir()):
            if not kit_src.is_dir():
                continue
            kit_slug = kit_src.name

            try:
                kit_r = update_kit(
                    kit_slug, kit_src, cypilot_dir, dry_run=args.dry_run,
                )
            except Exception as exc:
                kit_r = {
                    "kit": kit_slug,
                    "status": "ERROR",
                    "error": str(exc),
                }
                errors.append({"path": kit_slug, "error": str(exc)})
            kit_results[kit_slug] = kit_r

            if args.dry_run:
                continue

            # Collect gen errors
            if kit_r.get("gen_errors"):
                errors.extend(
                    {"path": kit_slug, "error": e} for e in kit_r["gen_errors"]
                )

            # Collect cross-kit aggregation parts
            if kit_r.get("skill_nav"):
                gen_skill_nav_parts.append(kit_r["skill_nav"])
            if kit_r.get("agents_content"):
                gen_agents_parts.append(kit_r["agents_content"])

            # Report progress
            ver = kit_r.get("version", {})
            ver_status = ver.get("status", "") if isinstance(ver, dict) else ver
            gen = kit_r.get("gen", {})
            files_written = gen.get("files_written", 0) if isinstance(gen, dict) else 0

            if ver_status == "created":
                sys.stderr.write(f"  {kit_slug}: first install, {files_written} files generated\n")
            elif ver_status == "migrated":
                sys.stderr.write(f"  {kit_slug}: migrated {ver.get('kit_version', '')}\n")
                for bp_r in ver.get("blueprints", []):
                    action = bp_r.get("action", "")
                    bp_name = bp_r.get("blueprint", "")
                    if action == "merged":
                        updated = bp_r.get("markers_updated", [])
                        skipped = bp_r.get("markers_skipped", [])
                        sys.stderr.write(
                            f"    {bp_name}: {len(updated)} markers updated"
                        )
                        if skipped:
                            sys.stderr.write(
                                f", {len(skipped)} skipped (customized)"
                            )
                        sys.stderr.write("\n")
                    elif action == "created":
                        sys.stderr.write(f"    {bp_name}: created (new)\n")
                    elif action == "skipped_all_customized":
                        sys.stderr.write(
                            f"    {bp_name}: all markers customized, skipped\n"
                        )
                sys.stderr.write(f"    {files_written} files generated\n")
            elif ver_status == "current":
                sys.stderr.write(f"  {kit_slug}: up to date, {files_written} files generated\n")

    actions["kits"] = kit_results
    # @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-update-kits

    # @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-regenerate-agents
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
    # @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-regenerate-agents

    # @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-ensure-scaffold
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

    # Re-inject root AGENTS.md and CLAUDE.md
    if not args.dry_run:
        root_agents_action = _inject_root_agents(project_root, install_rel)
        actions["root_agents"] = root_agents_action
        root_claude_action = _inject_root_claude(project_root, install_rel)
        actions["root_claude"] = root_claude_action
    # @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-ensure-scaffold

    # @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-return-report
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
    # @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-return-report
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


# Re-exported from kit.py — tests import it from here
from .kit import _read_conf_version as _read_conf_version  # noqa: F401


