import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..utils.artifacts_meta import create_backup, generate_default_registry, generate_slug
from ..utils.files import find_project_root
from ..utils import toml_utils

# Directories to copy from cache into project .cypilot/ dir
COPY_DIRS = ["kits", "skills", "architecture", "requirements", "schemas", "workflows"]
CACHE_DIR = Path.home() / ".cypilot" / "cache"


def _copy_from_cache(cache_dir: Path, target_dir: Path, force: bool = False) -> Dict[str, str]:
    """Copy tool directories from cache into project .cypilot/ dir.

    Reference directories (kits, skills, architecture, etc.) are ALWAYS refreshed
    from cache since they are managed content. User-editable content lives in config/.

    Returns dict of {dir_name: action} where action is 'created', 'updated', or 'skipped'.
    """
    results: Dict[str, str] = {}
    for name in COPY_DIRS:
        src = cache_dir / name
        dst = target_dir / name
        if not src.is_dir():
            results[name] = "missing_in_cache"
            continue
        if dst.exists():
            if not force:
                results[name] = "skipped"
                continue
            shutil.rmtree(dst)
            results[name] = "updated"
        else:
            results[name] = "created"
        shutil.copytree(src, dst)
    return results


def _default_core_toml(system_name: str, system_slug: str) -> dict:
    """Build default core.toml data for a new project."""
    return {
        "system": {
            "name": system_name,
            "slug": system_slug,
            "kit": "cypilot-sdlc",
        },
        "kits": {
            "cypilot-sdlc": {
                "format": "Cypilot",
                "path": "kits/sdlc",
            },
        },
    }


def _prompt_path(question: str, default: Optional[str]) -> str:
    prompt = f"{question}"
    if default is not None and str(default).strip():
        prompt += f" [{default}]"
    prompt += ": "
    try:
        sys.stderr.write(prompt)
        sys.stderr.flush()
        ans = input().strip()
    except EOFError:
        ans = ""
    if ans:
        return ans
    return default or ""


def _resolve_user_path(raw: str, base: Path) -> Path:
    p = Path(raw)
    if not p.is_absolute():
        p = base / p
    return p.resolve()


def _slug_to_pascal_case(slug: str) -> str:
    """Convert a slug like 'my-app' to PascalCase like 'MyApp'."""
    return "".join(word.capitalize() for word in slug.split("-")) if slug else "Unnamed"


def _define_root_system(project_root: Path) -> Dict[str, str]:
    """
    Define root system from project directory.

    Returns dict with 'name' (PascalCase) and 'slug' (lowercase-hyphenated).
    """
    # @cpt-begin:cpt-cypilot-algo-core-infra-define-root-system:p1:inst-extract-basename
    basename = project_root.name
    # @cpt-end:cpt-cypilot-algo-core-infra-define-root-system:p1:inst-extract-basename

    # @cpt-begin:cpt-cypilot-algo-core-infra-define-root-system:p1:inst-derive-slug
    slug = generate_slug(basename)
    # @cpt-end:cpt-cypilot-algo-core-infra-define-root-system:p1:inst-derive-slug

    # @cpt-begin:cpt-cypilot-algo-core-infra-define-root-system:p1:inst-derive-name
    name = _slug_to_pascal_case(slug)
    # @cpt-end:cpt-cypilot-algo-core-infra-define-root-system:p1:inst-derive-name

    # @cpt-begin:cpt-cypilot-algo-core-infra-define-root-system:p1:inst-return-system-def
    return {"name": name, "slug": slug}
    # @cpt-end:cpt-cypilot-algo-core-infra-define-root-system:p1:inst-return-system-def


_TOML_FENCE_RE = re.compile(r"```toml\s*\n(.*?)```", re.DOTALL)
MARKER_START = "<!-- @cpt:root-agents -->"
MARKER_END = "<!-- /@cpt:root-agents -->"


def _read_existing_install(project_root: Path) -> Optional[str]:
    """
    Check if project already has Cypilot installed by reading AGENTS.md TOML block.

    Returns install dir relative path if found, None otherwise.
    """
    import tomllib
    agents_file = project_root / "AGENTS.md"
    if not agents_file.is_file():
        return None
    try:
        content = agents_file.read_text(encoding="utf-8")
    except OSError:
        return None
    if MARKER_START not in content:
        return None
    for m in _TOML_FENCE_RE.finditer(content):
        try:
            data = tomllib.loads(m.group(1))
            val = data.get("cypilot")
            if isinstance(val, str) and val.strip():
                adapter_dir = project_root / val.strip()
                if adapter_dir.is_dir():
                    return val.strip()
        except Exception:
            continue
    return None


def _compute_managed_block(install_dir: str) -> str:
    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-compute-block
    return (
        f"{MARKER_START}\n"
        f"# Cypilot AI Agent Navigation\n"
        f"\n"
        f"**Remember these variables while working in this project:**\n"
        f"\n"
        f"```toml\n"
        f'cypilot = "{install_dir}"\n'
        f"```\n"
        f"\n"
        f"## Navigation Rules\n"
        f"\n"
        f"ALWAYS open and follow `{{cypilot}}/AGENTS.md` FIRST\n"
        f"\n"
        f"{MARKER_END}"
    )
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-compute-block


def _inject_root_agents(project_root: Path, install_dir: str, dry_run: bool = False) -> str:
    """Inject or update root AGENTS.md managed block. Returns action taken."""
    agents_file = project_root / "AGENTS.md"
    expected_block = _compute_managed_block(install_dir)

    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-if-no-agents
    if not agents_file.is_file():
        # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-create-agents-file
        if not dry_run:
            agents_file.write_text(expected_block + "\n", encoding="utf-8")
        return "created"
        # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-create-agents-file
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-if-no-agents

    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-read-existing
    content = agents_file.read_text(encoding="utf-8")
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-read-existing

    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-if-markers-exist
    if MARKER_START in content and MARKER_END in content:
        start_idx = content.index(MARKER_START)
        end_idx = content.index(MARKER_END) + len(MARKER_END)
        current_block = content[start_idx:end_idx]
        if current_block == expected_block.strip():
            return "unchanged"
        # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-replace-block
        new_content = content[:start_idx] + expected_block + content[end_idx:]
        # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-replace-block
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-if-markers-exist
    else:
        # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-insert-block
        new_content = expected_block + "\n\n" + content
        # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-insert-block

    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-write-agents
    if not dry_run:
        agents_file.write_text(new_content, encoding="utf-8")
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-write-agents

    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-return-agents-path
    return "updated"
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-return-agents-path


def cmd_init(argv: List[str]) -> int:
    # @cpt-dod:cpt-cypilot-dod-core-infra-init-config:p1
    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-user-init
    p = argparse.ArgumentParser(prog="init", description="Initialize Cypilot in a project")
    p.add_argument("--project-root", default=None, help="Project root directory")
    p.add_argument("--install-dir", default=None, help="Cypilot directory relative to project root (default: .cypilot)")
    p.add_argument("--project-name", default=None, help="Project name (default: project root folder name)")
    p.add_argument("--yes", action="store_true", help="Do not prompt; accept defaults")
    p.add_argument("--dry-run", action="store_true", help="Compute changes without writing files")
    p.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = p.parse_args(argv)
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-user-init

    cwd = Path.cwd().resolve()

    # Resolve project root
    default_project_root = cwd
    if args.project_root is None and not args.yes:
        raw_root = _prompt_path("Project root directory?", default_project_root.as_posix())
        project_root = _resolve_user_path(raw_root, cwd)
    else:
        raw_root = args.project_root or default_project_root.as_posix()
        project_root = _resolve_user_path(raw_root, cwd)

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-check-existing
    existing_install_rel = _read_existing_install(project_root)
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-check-existing

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-if-exists
    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-return-exists
    if existing_install_rel is not None and not args.force:
        print(json.dumps({
            "status": "FAIL",
            "message": "Cypilot already initialized. Use 'cypilot update' to upgrade or --force to reinitialize.",
            "project_root": project_root.as_posix(),
            "cypilot_dir": (project_root / existing_install_rel).as_posix(),
        }, indent=2, ensure_ascii=False))
        return 2
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-return-exists
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-if-exists

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-if-interactive
    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-prompt-dir
    default_install_dir = existing_install_rel or ".cypilot"
    if args.install_dir is None and not args.yes:
        install_rel = _prompt_path("Cypilot directory (relative to project root)?", default_install_dir)
    else:
        install_rel = args.install_dir or default_install_dir
    install_rel = install_rel.strip() or default_install_dir
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-prompt-dir
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-if-interactive

    cypilot_dir = (project_root / install_rel).resolve()

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-define-root
    root_system = _define_root_system(project_root)
    project_name = str(args.project_name).strip() if args.project_name else root_system["name"]
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-define-root

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-prompt-agents
    # Stub: agent selection not yet needed (single kit); will prompt when multi-kit support lands
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-prompt-agents

    # Verify cache exists
    if not CACHE_DIR.is_dir():
        print(json.dumps({
            "status": "ERROR",
            "message": f"Cypilot cache not found at {CACHE_DIR}. Run 'cypilot update' first.",
            "project_root": project_root.as_posix(),
        }, indent=2, ensure_ascii=False))
        return 1

    actions: Dict[str, str] = {}
    errors: List[Dict[str, str]] = []
    backups: List[str] = []

    # Create backup before --force overwrites
    if args.force and cypilot_dir.exists() and not args.dry_run:
        backup_path = create_backup(cypilot_dir)
        if backup_path:
            backups.append(backup_path.as_posix())

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-copy-skill
    if not args.dry_run:
        cypilot_dir.mkdir(parents=True, exist_ok=True)
        copy_results = _copy_from_cache(CACHE_DIR, cypilot_dir, force=args.force)
    else:
        copy_results = {d: "dry_run" for d in COPY_DIRS}
    actions["copy"] = json.dumps(copy_results)
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-copy-skill

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-create-config
    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config:p1:inst-mkdir-config
    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config-agents:p1:inst-gen-when-rules
    kit_id = "cypilot-sdlc"
    artifacts_when = f"ALWAYS open and follow `artifacts.toml` WHEN Cypilot uses kit `{kit_id}` for artifact kinds: PRD, DESIGN, DECOMPOSITION, ADR, FEATURE OR codebase"
    desired_agents = "\n".join([
        f"# Cypilot: {project_name}",
        "",
        "## Navigation Rules",
        "",
        "ALWAYS open and follow `schemas/artifacts.schema.toml` WHEN working with artifacts.toml",
        "",
        "ALWAYS open and follow `requirements/artifacts-registry.md` WHEN working with artifacts.toml",
        "",
        artifacts_when,
        "",
    ])
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config-agents:p1:inst-gen-when-rules

    desired_registry = generate_default_registry(project_name)

    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config:p1:inst-write-core-toml
    desired_core = _default_core_toml(project_name, root_system["slug"])
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config:p1:inst-write-core-toml
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config:p1:inst-mkdir-config
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-create-config

    # Write config files into config/ subdirectory
    config_dir = cypilot_dir / "config"
    if not args.dry_run:
        config_dir.mkdir(parents=True, exist_ok=True)

    core_toml_path = (config_dir / "core.toml").resolve()
    core_toml_existed = core_toml_path.is_file()
    if core_toml_existed and not args.force:
        actions["core_toml"] = "unchanged"
    else:
        if not args.dry_run:
            toml_utils.dump(desired_core, core_toml_path, header_comment="Cypilot project configuration")
        actions["core_toml"] = "updated" if core_toml_existed else "created"

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-create-config-agents
    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config-agents:p1:inst-write-config-agents
    agents_path = (config_dir / "AGENTS.md").resolve()
    agents_existed_before = agents_path.exists()
    if agents_existed_before and not agents_path.is_file():
        errors.append({"path": agents_path.as_posix(), "error": "CYPILOT_AGENTS_NOT_A_FILE"})
    elif agents_existed_before and not args.force:
        actions["cypilot_agents"] = "unchanged"
    else:
        if not args.dry_run:
            agents_path.write_text(desired_agents, encoding="utf-8")
        actions["cypilot_agents"] = "updated" if agents_existed_before else "created"
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config-agents:p1:inst-write-config-agents
    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config-agents:p1:inst-return-config-agents-path
    actions["cypilot_agents_path"] = agents_path.as_posix()
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config-agents:p1:inst-return-config-agents-path
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-create-config-agents

    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config:p1:inst-validate-schemas
    # Stub: schema validation deferred to p2
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config:p1:inst-validate-schemas

    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config:p1:inst-return-config-paths
    # (paths reported in final JSON output)
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config:p1:inst-return-config-paths

    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config:p1:inst-write-artifacts-toml
    registry_path = (config_dir / "artifacts.toml").resolve()
    registry_existed_before = registry_path.is_file()
    if registry_existed_before and not args.force:
        actions["artifacts_registry"] = "unchanged"
    else:
        if not args.dry_run:
            toml_utils.dump(desired_registry, registry_path, header_comment="Cypilot artifacts registry")
        actions["artifacts_registry"] = "updated" if registry_existed_before else "created"
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config:p1:inst-write-artifacts-toml

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-delegate-kits
    kit_results: Dict[str, Any] = {}
    kits_ref_dir = cypilot_dir / "kits"
    config_kits_dir = config_dir / "kits"
    if kits_ref_dir.is_dir() and not args.dry_run:
        from ..utils.blueprint import process_kit

        for kit_dir in sorted(kits_ref_dir.iterdir()):
            if not kit_dir.is_dir():
                continue
            bp_dir = kit_dir / "blueprints"
            if not bp_dir.is_dir():
                continue

            kit_slug = kit_dir.name
            user_bp_dir = config_kits_dir / kit_slug / "blueprints"

            # Copy blueprints to config/kits/{slug}/blueprints/ (user-editable)
            if user_bp_dir.exists():
                shutil.rmtree(user_bp_dir)
            user_bp_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(bp_dir, user_bp_dir)

            # Generate resources from blueprints
            summary, kit_errors = process_kit(
                kit_slug, user_bp_dir, config_kits_dir, dry_run=False,
            )
            kit_results[kit_slug] = {
                "files_written": summary.get("files_written", 0),
                "artifact_kinds": summary.get("artifact_kinds", []),
                "errors": kit_errors,
            }
            if kit_errors:
                errors.extend(
                    {"path": kit_slug, "error": e} for e in kit_errors
                )
    actions["kits"] = json.dumps(kit_results)
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-delegate-kits

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-delegate-agents
    # Stub: Agent Generator (Feature 5 boundary) — agent entry points generated separately
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-delegate-agents

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-inject-agents
    root_agents_action = _inject_root_agents(project_root, install_rel, dry_run=args.dry_run)
    actions["root_agents"] = root_agents_action
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-inject-agents

    if errors:
        err_result: Dict[str, object] = {
            "status": "ERROR",
            "message": "Init failed",
            "project_root": project_root.as_posix(),
            "cypilot_dir": cypilot_dir.as_posix(),
            "dry_run": bool(args.dry_run),
            "errors": errors,
        }
        if backups:
            err_result["backups"] = backups
        print(json.dumps(err_result, indent=2, ensure_ascii=False))
        return 1

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-return-init-ok
    # @cpt-begin:cpt-cypilot-state-core-infra-project-install:p1:inst-init-complete
    result: Dict[str, object] = {
        "status": "PASS",
        "project_root": project_root.as_posix(),
        "cypilot_dir": cypilot_dir.as_posix(),
        "core_toml": core_toml_path.as_posix(),
        "dry_run": bool(args.dry_run),
        "actions": actions,
        "root_system": root_system,
    }
    if backups:
        result["backups"] = backups
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0
    # @cpt-end:cpt-cypilot-state-core-infra-project-install:p1:inst-init-complete
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-return-init-ok
