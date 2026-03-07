"""
Update command — refresh an existing Cypilot installation in-place.

Safety rules for config/:
- .core/  → full replace from cache (read-only reference)
- .gen/   → aggregate files only (AGENTS.md, SKILL.md, README.md)
- config/ → generated kit outputs + user config (NEVER overwrite user files):
  - core.toml, artifacts.toml   → only via migration when version is higher
  - AGENTS.md, SKILL.md, README.md → only create if missing
  - kits/{slug}/                → generated outputs (artifacts/, workflows/, SKILL.md, scripts/)
Pipeline:
1. Replace .core/ from cache
2. Update kits: file-level diff (cache vs user) with interactive prompts
3. Write aggregate .gen/ files
5. Ensure config/ scaffold files exist (create only if missing)
6. Run self-check to verify kit integrity

@cpt-flow:cpt-cypilot-flow-version-config-update:p1
@cpt-algo:cpt-cypilot-algo-version-config-update-pipeline:p1
@cpt-algo:cpt-cypilot-algo-version-config-compare-versions:p1
@cpt-algo:cpt-cypilot-algo-version-config-layout-restructure:p1
@cpt-state:cpt-cypilot-state-version-config-installation:p1
@cpt-dod:cpt-cypilot-dod-version-config-update:p1
"""

# @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-update-imports
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
from ..utils.ui import ui
# @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-update-imports

def cmd_update(argv: List[str]) -> int:
    """Update an existing Cypilot installation.

    Refreshes .core/ from cache, updates kit files, regenerates .gen/ aggregates.
    Never overwrites user config files.
    """
    # @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-user-update
    p = argparse.ArgumentParser(
        prog="update",
        description="Update Cypilot installation (refresh .core, regenerate .gen)",
    )
    p.add_argument("--project-root", default=None, help="Project root directory")
    p.add_argument("--dry-run", action="store_true", help="Show what would be done")
    p.add_argument("--no-interactive", action="store_true",
                   help="Disable interactive prompts (auto-skip customized markers)")
    p.add_argument("-y", "--yes", action="store_true",
                   help="Auto-approve all prompts (no interaction)")
    args = p.parse_args(argv)
    # @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-user-update

    # @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-resolve-project
    from ..utils.files import find_project_root, _read_cypilot_var

    cwd = Path.cwd().resolve()
    project_root = Path(args.project_root).resolve() if args.project_root else find_project_root(cwd)

    if project_root is None:
        ui.result(
            {"status": "ERROR", "message": "No project root found. Run 'cpt init' first."},
            human_fn=lambda d: (
                ui.error("No project root found."),
                ui.hint("Initialize Cypilot first:  cpt init"),
                ui.blank(),
            ),
        )
        return 1

    install_rel = _read_cypilot_var(project_root)
    if not install_rel:
        ui.result(
            {"status": "ERROR", "message": "Cypilot not initialized in this project. Run 'cpt init' first.", "project_root": project_root.as_posix()},
            human_fn=lambda d: (
                ui.error("Cypilot is not initialized in this project."),
                ui.detail("Project root", project_root.as_posix()),
                ui.hint("Initialize first:  cpt init"),
                ui.blank(),
            ),
        )
        return 1

    cypilot_dir = (project_root / install_rel).resolve()
    if not cypilot_dir.is_dir():
        ui.result(
            {"status": "ERROR", "message": f"Cypilot directory not found: {cypilot_dir}", "project_root": project_root.as_posix()},
            human_fn=lambda d: (
                ui.error(f"Cypilot directory not found: {cypilot_dir}"),
                ui.hint("Reinitialize:  cpt init --force"),
                ui.blank(),
            ),
        )
        return 1

    if not CACHE_DIR.is_dir():
        ui.result(
            {"status": "ERROR", "message": f"Cache not found at {CACHE_DIR}. Run 'cpt update' (proxy downloads first)."},
            human_fn=lambda d: (
                ui.error("Cypilot cache not found."),
                ui.detail("Expected at", str(CACHE_DIR)),
                ui.hint("The proxy layer downloads the cache before forwarding to this command."),
                ui.hint("If running directly, ensure cache exists at the path above."),
                ui.blank(),
            ),
        )
        return 1
    # @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-resolve-project

    # @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-whatsnew
    actions: Dict[str, Any] = {}
    errors: List[Dict[str, str]] = []
    warnings: List[str] = []

    core_dir = cypilot_dir / CORE_SUBDIR
    gen_dir = cypilot_dir / GEN_SUBDIR
    config_dir = cypilot_dir / "config"

    # ── Show core whatsnew (before .core/ is replaced) ────────────────────
    if not args.dry_run:
        cache_whatsnew = _read_core_whatsnew(CACHE_DIR / "whatsnew.toml")
        core_whatsnew = _read_core_whatsnew(core_dir / "whatsnew.toml")
        if cache_whatsnew:
            ack = _show_core_whatsnew(
                cache_whatsnew, core_whatsnew,
                interactive=not args.no_interactive and not args.yes and sys.stdin.isatty(),
            )
            if not ack:
                ui.result({"status": "ABORTED", "message": "Update aborted by user."})
                return 0
    # @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-whatsnew

    # @cpt-begin:cpt-cypilot-algo-version-config-update-pipeline:p1:inst-replace-core-algo
    # @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-replace-core
    # ── Step 1: Replace .core/ from cache (always force) ─────────────────
    ui.step("Updating core files from cache...")
    if not args.dry_run:
        cypilot_dir.mkdir(parents=True, exist_ok=True)
        copy_results = _copy_from_cache(CACHE_DIR, cypilot_dir, force=True)
        core_dir.mkdir(parents=True, exist_ok=True)
        (core_dir / "README.md").write_text(_core_readme(), encoding="utf-8")
        # Copy whatsnew.toml into .core/ so next update knows what was seen
        _cache_whatsnew = CACHE_DIR / "whatsnew.toml"
        if _cache_whatsnew.is_file():
            shutil.copy2(_cache_whatsnew, core_dir / "whatsnew.toml")
    else:
        copy_results = {d: "dry_run" for d in COPY_DIRS}
    actions["core_update"] = copy_results
    for name, action in copy_results.items():
        ui.file_action(f".core/{name}/", action)
    # @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-replace-core
    # @cpt-end:cpt-cypilot-algo-version-config-update-pipeline:p1:inst-replace-core-algo

    # @cpt-begin:cpt-cypilot-algo-version-config-update-pipeline:p1:inst-detect-layout-algo
    # @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-detect-layout
    # ── Step 1b: Detect and migrate old layout ───────────────────────────
    if not args.dry_run:
        from .kit import _detect_and_migrate_layout
        layout_migrated = _detect_and_migrate_layout(cypilot_dir, dry_run=False)
        if layout_migrated:
            ui.step("Migrating directory layout...")
            for slug, status in layout_migrated.items():
                ui.substep(f"{slug}: {status}")
            actions["layout_migration"] = layout_migrated
    # @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-detect-layout
    # @cpt-end:cpt-cypilot-algo-version-config-update-pipeline:p1:inst-detect-layout-algo

    # @cpt-begin:cpt-cypilot-algo-version-config-update-pipeline:p1:inst-migrate-kit-sources-algo
    # @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-migrate-kit-sources
    # ── Step 1c: Deduplicate legacy kit slugs + migrate sources ──────────
    if not args.dry_run:
        deduped = _deduplicate_legacy_kits(config_dir)
        if deduped:
            ui.step("Deduplicating legacy kit slugs...")
            for legacy, canonical in deduped.items():
                ui.substep(f"{legacy} → {canonical}")
            actions["kit_dedup"] = deduped

        migrated_kits = _migrate_kit_sources(config_dir)
        if migrated_kits:
            ui.step("Migrating kit sources to GitHub...")
            for slug, src in migrated_kits.items():
                ui.substep(f"{slug}: source → {src}")
            actions["kit_source_migration"] = migrated_kits
    # @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-migrate-kit-sources
    # @cpt-end:cpt-cypilot-algo-version-config-update-pipeline:p1:inst-migrate-kit-sources-algo

    # ── Step 2: Update kits from registered sources ─────────────────────────────
    ui.step("Updating kits...")
    from .kit import (
        update_kit, regenerate_gen_aggregates,
        _read_kits_from_core_toml, _parse_github_source, _download_kit_from_github,
    )

    kit_results: Dict[str, Any] = {}
    interactive = not args.no_interactive and sys.stdin.isatty()

    installed_kits = _read_kits_from_core_toml(config_dir)
    for kit_slug, kit_data in installed_kits.items():
        source_str = kit_data.get("source", "")
        kit_src: Optional[Path] = None
        tmp_to_clean: Optional[Path] = None

        if source_str.startswith("github:"):
            owner_repo = source_str.removeprefix("github:")
            try:
                owner, repo, version = _parse_github_source(owner_repo)
                kit_src, _ = _download_kit_from_github(owner, repo, version)
                tmp_to_clean = kit_src.parent
            except Exception as exc:
                errors.append({"path": kit_slug, "error": f"Download failed: {exc}"})
                ui.warn(f"{kit_slug}: download failed: {exc}")
                continue
        elif not source_str:
            # No source — check cache fallback
            cache_kit = CACHE_DIR / "kits" / kit_slug
            if cache_kit.is_dir():
                kit_src = cache_kit
            else:
                continue  # No source, no cache — skip

        if kit_src is None:
            continue

        try:
            kit_r = update_kit(
                kit_slug, kit_src, cypilot_dir,
                dry_run=args.dry_run,
                interactive=interactive,
                auto_approve=args.yes,
                source=source_str,
            )
        except Exception as exc:
            kit_r = {
                "kit": kit_slug,
                "status": "ERROR",
                "error": str(exc),
            }
            errors.append({"path": kit_slug, "error": str(exc)})
        finally:
            if tmp_to_clean:
                shutil.rmtree(tmp_to_clean, ignore_errors=True)

        kit_results[kit_slug] = kit_r

        if args.dry_run:
            continue

        # Collect gen errors
        if kit_r.get("gen_errors"):
            errors.extend(
                {"path": kit_slug, "error": e} for e in kit_r["gen_errors"]
            )

        # Report progress
        ver = kit_r.get("version", {})
        ver_status = ver.get("status", "") if isinstance(ver, dict) else ver
        gen = kit_r.get("gen", {})
        files_written = gen.get("files_written", 0) if isinstance(gen, dict) else 0

        if ver_status == "created":
            ui.substep(f"{kit_slug}: first install, {files_written} files written")
        elif ver_status == "updated":
            ui.substep(f"{kit_slug}: updated, {files_written} file(s) accepted")
            for fp in gen.get("accepted_files", []):
                ui.substep(f"      ~ {fp}")
            for fp in kit_r.get("gen_rejected", []):
                ui.substep(f"      ✗ {fp} (declined)")
        elif ver_status == "partial":
            rejected = kit_r.get("gen_rejected", [])
            ui.substep(f"{kit_slug}: partial, {files_written} accepted, {len(rejected)} declined")
            for fp in gen.get("accepted_files", []):
                ui.substep(f"      ~ {fp}")
            for fp in rejected:
                ui.substep(f"      ✗ {fp} (declined)")
        elif ver_status == "current":
            ui.substep(f"{kit_slug}: up to date")

    actions["kits"] = kit_results

    # ── Step 3: Regenerate .gen/ aggregates ────────────────────────────
    if not args.dry_run:
        gen_result = regenerate_gen_aggregates(cypilot_dir)
        actions.update(gen_result)
    # (end kit updates)

    # @cpt-begin:cpt-cypilot-algo-version-config-update-pipeline:p1:inst-scaffold-algo
    # @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-ensure-scaffold
    # ── Step 5: Ensure config/ scaffold (create only if missing) ─────────
    ui.step("Ensuring config/ scaffold...")
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
    # @cpt-end:cpt-cypilot-algo-version-config-update-pipeline:p1:inst-scaffold-algo

    # @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-regenerate-agents
    # ── Auto-regenerate agent integrations if real changes happened ────
    if not args.dry_run:
        agents_regen = _maybe_regenerate_agents(
            copy_results, kit_results, project_root, cypilot_dir,
        )
        if agents_regen:
            actions["agents_regenerated"] = agents_regen
    # @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-regenerate-agents

    # @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-self-check
    # ── Run validate-kits to verify kit integrity after update ───────────
    validate_kits_result: Optional[Dict[str, Any]] = None
    if not args.dry_run:
        try:
            from .validate_kits import run_validate_kits

            vk_rc, vk_report = run_validate_kits(
                project_root=project_root,
                adapter_dir=cypilot_dir,
            )
            validate_kits_result = vk_report
            vk_status = str(vk_report.get("status", ""))
            if vk_rc != 0 or vk_status != "PASS":
                warnings.append(f"validate-kits: {vk_status}")
                ui.warn(f"Validate kits: {vk_status}")
                # Show top errors inline so the user doesn't have to re-run
                for e in (vk_report.get("errors") or [])[:5]:
                    if isinstance(e, dict):
                        msg = e.get("message", "")
                        path = e.get("path", "")
                        if path:
                            msg = f"{path}: {msg}"
                        ui.substep(f"  ✗ {msg}")
                        for detail in (e.get("errors") or []):
                            ui.substep(f"      {detail}")
                    else:
                        ui.substep(f"  ✗ {e}")
                n_err = int(vk_report.get("error_count", 0))
                if n_err > 5:
                    ui.substep(f"  ... and {n_err - 5} more error(s)")
                ui.hint("Run 'cpt validate-kits --verbose' for full details.")
            else:
                ui.step("Validate kits: PASS")
        except Exception as exc:
            warnings.append(f"validate-kits failed to run: {exc}")
    # @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-self-check

    # @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-return-report
    # ── Report ───────────────────────────────────────────────────────────
    status = "PASS" if not errors and not warnings else "WARN"
    update_result: Dict[str, Any] = {
        "status": status,
        "project_root": project_root.as_posix(),
        "cypilot_dir": cypilot_dir.as_posix(),
        "dry_run": bool(args.dry_run),
        "actions": actions,
    }
    if errors:
        update_result["errors"] = errors
    if warnings:
        update_result["warnings"] = warnings
    if validate_kits_result is not None:
        update_result["validate_kits"] = validate_kits_result

    ui.result(update_result, human_fn=_human_update_ok)
    # @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-return-report
    return 0

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
# @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-update-helpers
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


def _maybe_regenerate_agents(
    copy_results: Dict[str, str],
    kit_results: Dict[str, Any],
    project_root: Path,
    cypilot_dir: Path,
) -> List[str]:
    """Auto-regenerate agent integration files when a real update happened.

    Triggers when core dirs were updated/created or any kit was created/migrated.
    Only regenerates agents whose skill output files already exist on disk.
    Returns list of agent names that were regenerated.
    """
    core_changed = any(v in ("updated", "created") for v in copy_results.values())
    kits_changed = any(
        isinstance(kr, dict)
        and isinstance(kr.get("version"), dict)
        and kr["version"].get("status") in ("created", "migrated")
        for kr in kit_results.values()
    )
    if not core_changed and not kits_changed:
        return []

    from .agents import (
        _ALL_RECOGNIZED_AGENTS,
        _default_agents_config,
        _process_single_agent,
    )

    cfg = _default_agents_config()
    agents_cfg = cfg.get("agents", {})
    regenerated: List[str] = []

    for agent in _ALL_RECOGNIZED_AGENTS:
        agent_cfg = agents_cfg.get(agent, {})
        skills_cfg = agent_cfg.get("skills", {})
        outputs = skills_cfg.get("outputs", [])
        # Only regenerate if at least one skill output file already exists
        has_existing = any(
            isinstance(out, dict)
            and isinstance(out.get("path"), str)
            and (project_root / out["path"]).is_file()
            for out in outputs
        )
        if not has_existing:
            continue
        result = _process_single_agent(
            agent, project_root, cypilot_dir, cfg, None, dry_run=False,
        )
        wf = result.get("workflows", {})
        sk = result.get("skills", {})
        n_changed = (
            len(wf.get("updated", []))
            + len(wf.get("created", []))
            + len(sk.get("updated", []))
            + len(sk.get("created", []))
        )
        if n_changed:
            regenerated.append(agent)

    if regenerated:
        ui.step("Regenerating agent integrations...")
        for agent in regenerated:
            ui.substep(f"{agent}: updated")

    return regenerated

# ---------------------------------------------------------------------------
# Bundled kit source migration (ADR-0013)
# ---------------------------------------------------------------------------

# Legacy slug → canonical slug mapping
_LEGACY_SLUG_RENAMES: Dict[str, str] = {
    "cypilot-sdlc": "sdlc",
}


def _deduplicate_legacy_kits(config_dir: Path) -> Dict[str, str]:
    """Deduplicate legacy kit slugs in core.toml and artifacts.toml.

    If both legacy and canonical slugs exist with the same path,
    merge into canonical and remove legacy. Updates:
    - core.toml [kits] section
    - core.toml [system].kit reference
    - artifacts.toml [[systems]].kit references

    Returns dict of {legacy_slug: canonical_slug} for deduplicated kits.
    """
    core_toml = config_dir / "core.toml"
    if not core_toml.is_file():
        return {}

    try:
        import tomllib
        with open(core_toml, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return {}

    kits = data.get("kits", {})
    if not isinstance(kits, dict):
        return {}

    renamed: Dict[str, str] = {}

    for legacy, canonical in _LEGACY_SLUG_RENAMES.items():
        if legacy not in kits or canonical not in kits:
            continue
        legacy_data = kits.get(legacy, {})
        canonical_data = kits.get(canonical, {})
        if not isinstance(legacy_data, dict) or not isinstance(canonical_data, dict):
            continue
        if legacy_data.get("path") != canonical_data.get("path"):
            continue  # Different paths — leave both

        # Same path — merge legacy into canonical, delete legacy
        for k, v in legacy_data.items():
            if k not in canonical_data or not canonical_data[k]:
                canonical_data[k] = v
        del kits[legacy]

        # Update system.kit in core.toml
        system = data.get("system", {})
        if isinstance(system, dict) and system.get("kit") == legacy:
            system["kit"] = canonical

        renamed[legacy] = canonical

    if not renamed:
        return {}

    # Write core.toml
    try:
        from ..utils import toml_utils
        toml_utils.dump(data, core_toml, header_comment="Cypilot project configuration")
    except Exception:
        pass

    # Update artifacts.toml — fix system.kit references
    artifacts_toml = config_dir / "artifacts.toml"
    if artifacts_toml.is_file():
        try:
            import tomllib as _tomllib
            with open(artifacts_toml, "rb") as f:
                reg = _tomllib.load(f)

            changed = False
            for sys_entry in reg.get("systems", []):
                if isinstance(sys_entry, dict) and sys_entry.get("kit") in renamed:
                    sys_entry["kit"] = renamed[sys_entry["kit"]]
                    changed = True

            if changed:
                from ..utils import toml_utils
                toml_utils.dump(reg, artifacts_toml, header_comment="Cypilot artifacts registry")
        except Exception:
            pass

    return renamed


# Known bundled kits and their GitHub sources
_KNOWN_KIT_SOURCES: Dict[str, str] = {
    "sdlc": "github:cyberfabric/cyber-pilot-kit-sdlc",
    "cypilot-sdlc": "github:cyberfabric/cyber-pilot-kit-sdlc",
}

def _migrate_kit_sources(config_dir: Path) -> Dict[str, str]:
    """Add 'source' field to installed kits that lack one (metadata-only).

    For projects upgrading from versions where kits were bundled in cache,
    this adds the GitHub source reference so that Step 2 can download and
    update the kit with interactive diff.

    Returns dict of {slug: source} for migrated kits. Empty if nothing changed.
    """
    core_toml = config_dir / "core.toml"
    if not core_toml.is_file():
        return {}

    try:
        import tomllib
        with open(core_toml, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return {}

    kits = data.get("kits", {})
    if not isinstance(kits, dict):
        return {}

    migrated: Dict[str, str] = {}
    for slug, kit_data in kits.items():
        if not isinstance(kit_data, dict):
            continue
        if kit_data.get("source"):
            continue  # Already has a source — skip
        known_source = _KNOWN_KIT_SOURCES.get(slug, "")
        if known_source:
            kit_data["source"] = known_source
            migrated[slug] = known_source

    if not migrated:
        return {}

    try:
        from ..utils import toml_utils
        toml_utils.dump(data, core_toml, header_comment="Cypilot project configuration")
    except Exception:
        pass

    return migrated


# Re-exported from kit.py — tests import it from here
from .kit import _read_conf_version as _read_conf_version  # noqa: F401

def _read_core_whatsnew(path: Path) -> Dict[str, Dict[str, str]]:
    """Read a standalone whatsnew.toml file.

    Returns dict mapping version string to {summary, details}.
    """
    if not path.is_file():
        return {}
    try:
        import tomllib
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return {}
    result: Dict[str, Dict[str, str]] = {}
    for key, entry in data.items():
        if isinstance(entry, dict):
            result[key] = {
                "summary": str(entry.get("summary", "")),
                "details": str(entry.get("details", "")),
            }
    return result

def _show_core_whatsnew(
    ref_whatsnew: Dict[str, Dict[str, str]],
    core_whatsnew: Dict[str, Dict[str, str]],
    *,
    interactive: bool = True,
) -> bool:
    """Display core whatsnew entries present in cache but missing from .core/.

    Returns True if user acknowledged (or non-interactive), False if declined.
    """
    missing = sorted(
        (v, ref_whatsnew[v]) for v in ref_whatsnew
        if v not in core_whatsnew
    )
    if not missing:
        return True

    sys.stderr.write(f"\n{'=' * 60}\n")
    sys.stderr.write(f"  What's new in Cypilot\n")
    sys.stderr.write(f"{'=' * 60}\n")

    for ver, entry in missing:
        sys.stderr.write(f"\n  \033[1m{ver}: {entry['summary']}\033[0m\n")
        if entry["details"]:
            for line in entry["details"].splitlines():
                sys.stderr.write(f"    {line}\n")

    sys.stderr.write(f"\n{'=' * 60}\n")

    if not interactive:
        return True

    sys.stderr.write("  Press Enter to continue with update (or 'q' to abort): ")
    sys.stderr.flush()
    try:
        response = input().strip().lower()
    except EOFError:
        return False
    return response != "q"
# @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-update-helpers

# ---------------------------------------------------------------------------
# Human-friendly formatter
# ---------------------------------------------------------------------------
# @cpt-begin:cpt-cypilot-flow-version-config-update:p1:inst-update-format-output
def _human_update_ok(data: Dict[str, Any]) -> None:
    dry = data.get("dry_run", False)
    status = data.get("status", "")
    errors = data.get("errors", [])
    warnings = data.get("warnings", [])
    prefix = "[dry-run] " if dry else ""

    ui.header(f"{prefix}Cypilot Update")
    ui.detail("Project root", str(data.get("project_root", "?")))
    ui.detail("Cypilot dir", str(data.get("cypilot_dir", "?")))

    actions = data.get("actions", {})
    if actions:
        # Summarize file actions
        created = [k for k, v in actions.items() if v == "created"]
        updated = [k for k, v in actions.items() if v == "updated"]
        unchanged = [k for k, v in actions.items() if v in ("unchanged", "preserved")]

        if created:
            ui.blank()
            ui.step(f"Created ({len(created)})")
            for k in created:
                ui.file_action(k, "created")
        if updated:
            ui.blank()
            ui.step(f"Updated ({len(updated)})")
            for k in updated:
                ui.file_action(k, "updated")
        if unchanged:
            ui.blank()
            ui.step(f"Unchanged ({len(unchanged)})")

        # Core update details
        core_update = actions.get("core_update")
        if isinstance(core_update, dict):
            ui.blank()
            ui.step("Core:")
            for sub_k, sub_v in core_update.items():
                ui.file_action(sub_k, str(sub_v))

        # Kit results
        kits_data = actions.get("kits")
        if isinstance(kits_data, dict):
            ui.blank()
            ui.step(f"Kits ({len(kits_data)})")
            for slug, kr in kits_data.items():
                if not isinstance(kr, dict):
                    ui.substep(f"  {slug}: {kr}")
                    continue
                ver = kr.get("version", {})
                ver_status = ver.get("status", "") if isinstance(ver, dict) else str(ver)
                gen = kr.get("gen", {})
                fw = gen.get("files_written", 0) if isinstance(gen, dict) else 0
                accepted_files = gen.get("accepted_files", []) if isinstance(gen, dict) else []
                rejected = kr.get("gen_rejected", [])

                if ver_status == "current":
                    ui.substep(f"  {slug}: up to date")
                else:
                    parts = [f"{slug}: {ver_status}"]
                    if fw:
                        parts.append(f"{fw} file(s) accepted")
                    if rejected:
                        parts.append(f"{len(rejected)} declined")
                    ui.substep(f"  {'  '.join(parts)}")
                    for fp in accepted_files:
                        ui.substep(f"    ~ {fp}")
                    for fp in rejected:
                        ui.substep(f"    ✗ {fp} (declined)")

        # Remaining dict/list actions (not already handled)
        skip = {"core_update", "kits", "agents_regenerated"}
        for k, v in actions.items():
            if k in skip or isinstance(v, str):
                continue
            if isinstance(v, dict):
                ui.blank()
                ui.step(f"{k}:")
                for sub_k, sub_v in v.items():
                    if isinstance(sub_v, (dict, list)):
                        ui.substep(f"  {sub_k}: ...")
                    else:
                        ui.substep(f"  {sub_k}: {sub_v}")
            elif isinstance(v, list):
                ui.blank()
                ui.step(f"{k}:")
                for item in v:
                    ui.substep(f"  {item}")

        agents_regen = actions.get("agents_regenerated")
        if isinstance(agents_regen, list) and agents_regen:
            ui.blank()
            ui.step(f"Agent integrations regenerated: {', '.join(agents_regen)}")

    if errors:
        ui.blank()
        ui.warn(f"Errors ({len(errors)}):")
        for err in errors:
            if isinstance(err, dict):
                ui.substep(f"• {err.get('path', '?')}: {err.get('error', '?')}")
            else:
                ui.substep(f"• {err}")
    if warnings:
        ui.blank()
        for w in warnings:
            ui.warn(w)

    if dry:
        ui.success("Dry run complete — no files were written.")
    elif status == "PASS":
        ui.success("Update complete!")
    else:
        ui.warn("Update finished with warnings (see above).")
    ui.blank()
# @cpt-end:cpt-cypilot-flow-version-config-update:p1:inst-update-format-output
