import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..utils.artifacts_meta import create_backup, generate_default_registry, generate_slug
from ..utils.files import find_project_root


def _safe_relpath_from_dir(target: Path, from_dir: Path) -> str:
    try:
        rel = os.path.relpath(target.as_posix(), from_dir.as_posix())
    except Exception:
        return target.as_posix()
    return rel.replace(os.sep, "/")


def _load_json_file(path: Path) -> Optional[dict]:
    if not path.is_file():
        return None
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, OSError, IOError):
        return None


def _write_json_file(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _default_project_config(cypilot_core_path: str, cypilot_adapter_path: str) -> dict:
    return {
        "cypilotCorePath": cypilot_core_path,
        "cypilotAdapterPath": cypilot_adapter_path,
        "codeScanning": {
            "fileExtensions": [
                ".py",
                ".md",
                ".js",
                ".ts",
                ".tsx",
                ".go",
                ".rs",
                ".java",
                ".cs",
                ".sql",
            ],
            "singleLineComments": ["#", "//", "--"],
            "multiLineComments": [
                {"start": "/*", "end": "*/"},
                {"start": "<!--", "end": "-->"},
            ],
            "blockCommentPrefixes": ["*"],
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


MARKER_START = "<!-- @cpt:root-agents -->"
MARKER_END = "<!-- /@cpt:root-agents -->"


def _compute_managed_block(install_dir: str) -> str:
    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-compute-block
    return (
        f"{MARKER_START}\n"
        f"# Cypilot AI Agent Navigation\n"
        f"\n"
        f"**Version**: 1.2\n"
        f"\n"
        f"---\n"
        f"\n"
        f"## Variables\n"
        f"\n"
        f"| Variable | Value | Description |\n"
        f"|----------|-------|-------------|\n"
        f"| `{{cypilot}}` | `@/{install_dir}` | Cypilot install directory |\n"
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
    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-user-init
    p = argparse.ArgumentParser(prog="init", description="Initialize Cypilot config and minimal adapter")
    p.add_argument("--project-root", default=None, help="Project root directory to create .cypilot-config.json in")
    p.add_argument("--cypilot-root", default=None, help="Explicit Cypilot core root (optional override)")
    p.add_argument("--adapter-path", default=None, help="Adapter directory path relative to project root (default: .cypilot-adapter)")
    p.add_argument("--project-name", default=None, help="Project name used in adapter AGENTS.md (default: project root folder name)")
    p.add_argument("--yes", action="store_true", help="Do not prompt; accept defaults")
    p.add_argument("--dry-run", action="store_true", help="Compute changes without writing files")
    p.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = p.parse_args(argv)
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-user-init

    cwd = Path.cwd().resolve()
    cypilot_root = Path(args.cypilot_root).resolve() if args.cypilot_root else None
    if cypilot_root is None:
        cypilot_root = (Path(__file__).resolve().parents[5])
        if not ((cypilot_root / "AGENTS.md").exists() and (cypilot_root / "workflows").is_dir()):
            cypilot_root = Path(__file__).resolve().parents[7]

    # Default to the directory where the command was invoked.
    default_project_root = cwd
    if args.project_root is None and not args.yes:
        raw_root = _prompt_path("Where should I create .cypilot-config.json?", default_project_root.as_posix())
        project_root = _resolve_user_path(raw_root, cwd)
    else:
        raw_root = args.project_root or default_project_root.as_posix()
        project_root = _resolve_user_path(raw_root, cwd)

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-check-existing
    config_path = (project_root / ".cypilot-config.json").resolve()
    existing_cfg = _load_json_file(config_path) if config_path.is_file() else None
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-check-existing

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-if-exists
    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-return-exists
    if existing_cfg is not None and not args.force:
        adapter_check = existing_cfg.get("cypilotAdapterPath", "")
        if isinstance(adapter_check, str) and (project_root / adapter_check).is_dir():
            print(json.dumps({
                "status": "FAIL",
                "message": "Cypilot already initialized. Use 'cypilot update' to upgrade or --force to reinitialize.",
                "project_root": project_root.as_posix(),
                "config_path": config_path.as_posix(),
            }, indent=2, ensure_ascii=False))
            return 2
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-return-exists
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-if-exists

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-if-interactive
    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-prompt-dir
    default_adapter_path = ".cypilot-adapter"
    if args.adapter_path is None and isinstance(existing_cfg, dict):
        existing_adapter_path = existing_cfg.get("cypilotAdapterPath")
        if isinstance(existing_adapter_path, str) and existing_adapter_path.strip():
            default_adapter_path = existing_adapter_path.strip()
    if args.adapter_path is None and not args.yes:
        adapter_rel = _prompt_path("Where should I create the Cypilot adapter directory (relative to project root)?", default_adapter_path)
    else:
        adapter_rel = args.adapter_path or default_adapter_path
    adapter_rel = adapter_rel.strip() or default_adapter_path
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-prompt-dir
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-if-interactive

    adapter_dir = (project_root / adapter_rel).resolve()
    core_rel = _safe_relpath_from_dir(cypilot_root, project_root)
    extends_target = (cypilot_root / "AGENTS.md").resolve()
    extends_rel = _safe_relpath_from_dir(extends_target, adapter_dir)

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-define-root
    root_system = _define_root_system(project_root)
    project_name = str(args.project_name).strip() if args.project_name else root_system["name"]
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-define-root

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-prompt-agents
    # Stub: agent selection not yet needed (single kit); will prompt when multi-kit support lands
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-prompt-agents

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-copy-skill
    # Stub: cache-only model — proxy forwards to ~/.cypilot/cache/, no project-local copy needed yet
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-copy-skill

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-create-config
    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config-agents:p1:inst-gen-when-rules
    kit_id = "cypilot-sdlc"
    artifacts_when = f"ALWAYS open and follow `artifacts.json` WHEN Cypilot uses kit `{kit_id}` for artifact kinds: PRD, DESIGN, DECOMPOSITION, ADR, FEATURE OR codebase"
    desired_agents = "\n".join([
        f"# Cypilot Adapter: {project_name}",
        "",
        f"**Extends**: `{extends_rel}`",
        "",
        "---",
        "",
        "## Variables",
        "",
        "**While Cypilot is enabled**, remember these variables:",
        "",
        "| Variable | Value | Description |",
        "|----------|-------|-------------|",
        "| `{cypilot_adapter_path}` | Directory containing this AGENTS.md | Root path for Cypilot Adapter navigation |",
        "",
        "Use `{cypilot_adapter_path}` as the base path for all relative Cypilot Adapter file references.",
        "",
        "---",
        "",
        "## Navigation Rules",
        "",
        "ALWAYS open and follow `{cypilot_path}/schemas/artifacts.schema.json` WHEN working with artifacts.json",
        "",
        "ALWAYS open and follow `{cypilot_path}/requirements/artifacts-registry.md` WHEN working with artifacts.json",
        "",
        artifacts_when,
        "",
    ])
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config-agents:p1:inst-gen-when-rules

    desired_registry = generate_default_registry(project_name, core_rel)

    desired_cfg = _default_project_config(core_rel, adapter_rel)
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-create-config

    actions: Dict[str, str] = {}
    errors: List[Dict[str, str]] = []
    backups: List[str] = []

    # Create backup of adapter directory before --force overwrites
    if args.force and adapter_dir.exists() and not args.dry_run:
        backup_path = create_backup(adapter_dir)
        if backup_path:
            backups.append(backup_path.as_posix())

    config_existed_before = config_path.exists()
    if config_existed_before and not config_path.is_file():
        errors.append({"path": config_path.as_posix(), "error": "CONFIG_PATH_NOT_A_FILE"})
    elif config_existed_before and not args.force:
        existing = _load_json_file(config_path)
        if not isinstance(existing, dict):
            errors.append({"path": config_path.as_posix(), "error": "CONFIG_INVALID_JSON"})
        else:
            merged = dict(existing)
            changed = False

            existing_core = merged.get("cypilotCorePath")
            if not (isinstance(existing_core, str) and existing_core.strip()):
                merged["cypilotCorePath"] = core_rel
                changed = True

            existing_adapter = merged.get("cypilotAdapterPath")
            if not (isinstance(existing_adapter, str) and existing_adapter.strip()):
                merged["cypilotAdapterPath"] = adapter_rel
                changed = True

            if changed:
                desired_cfg = merged
                if not args.dry_run:
                    project_root.mkdir(parents=True, exist_ok=True)
                    _write_json_file(config_path, desired_cfg)
                actions["config"] = "updated"
            elif merged.get("cypilotCorePath") != core_rel or merged.get("cypilotAdapterPath") != adapter_rel:
                errors.append({"path": config_path.as_posix(), "error": "CONFIG_CONFLICT"})
            else:
                actions["config"] = "unchanged"
    else:
        if config_existed_before and args.force:
            existing = _load_json_file(config_path)
            if isinstance(existing, dict):
                merged = dict(existing)
                merged["cypilotCorePath"] = core_rel
                merged["cypilotAdapterPath"] = adapter_rel
                desired_cfg = merged
        if not args.dry_run:
            project_root.mkdir(parents=True, exist_ok=True)
            _write_json_file(config_path, desired_cfg)
        actions["config"] = "updated" if config_existed_before else "created"

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-create-config-agents
    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config-agents:p1:inst-write-config-agents
    agents_path = (adapter_dir / "AGENTS.md").resolve()
    agents_existed_before = agents_path.exists()
    if agents_existed_before and not agents_path.is_file():
        errors.append({"path": agents_path.as_posix(), "error": "ADAPTER_AGENTS_NOT_A_FILE"})
    elif agents_existed_before and not args.force:
        try:
            old = agents_path.read_text(encoding="utf-8")
        except Exception:
            old = ""
        if old == desired_agents:
            actions["adapter_agents"] = "unchanged"
        else:
            actions["adapter_agents"] = "unchanged"
    else:
        if not args.dry_run:
            adapter_dir.mkdir(parents=True, exist_ok=True)
            agents_path.write_text(desired_agents, encoding="utf-8")
        actions["adapter_agents"] = "updated" if agents_existed_before else "created"
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config-agents:p1:inst-write-config-agents
    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config-agents:p1:inst-return-config-agents-path
    actions["adapter_agents_path"] = agents_path.as_posix()
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config-agents:p1:inst-return-config-agents-path
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-create-config-agents

    registry_path = (adapter_dir / "artifacts.json").resolve()
    registry_existed_before = registry_path.exists()
    if registry_existed_before and not registry_path.is_file():
        errors.append({"path": registry_path.as_posix(), "error": "ARTIFACTS_REGISTRY_NOT_A_FILE"})
    elif registry_existed_before and not args.force:
        existing_reg = _load_json_file(registry_path)
        if existing_reg == desired_registry:
            actions["artifacts_registry"] = "unchanged"
        else:
            actions["artifacts_registry"] = "unchanged"
    else:
        if not args.dry_run:
            adapter_dir.mkdir(parents=True, exist_ok=True)
            _write_json_file(registry_path, desired_registry)
        actions["artifacts_registry"] = "updated" if registry_existed_before else "created"

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-delegate-kits
    # Stub: Kit Manager (Feature 2 boundary) — default kit registered in artifacts.json
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-delegate-kits

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-delegate-agents
    # Stub: Agent Generator (Feature 5 boundary) — agent entry points generated separately
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-delegate-agents

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-inject-agents
    root_agents_action = _inject_root_agents(project_root, adapter_rel, dry_run=args.dry_run)
    actions["root_agents"] = root_agents_action
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-inject-agents

    if errors:
        err_result: Dict[str, object] = {
            "status": "ERROR",
            "message": "Init failed",
            "project_root": project_root.as_posix(),
            "cypilot_root": cypilot_root.as_posix(),
            "config_path": config_path.as_posix(),
            "adapter_dir": adapter_dir.as_posix(),
            "dry_run": bool(args.dry_run),
            "errors": errors,
        }
        if backups:
            err_result["backups"] = backups
        print(json.dumps(err_result, indent=2, ensure_ascii=False))
        return 1

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-return-init-ok
    result: Dict[str, object] = {
        "status": "PASS",
        "project_root": project_root.as_posix(),
        "cypilot_root": cypilot_root.as_posix(),
        "config_path": config_path.as_posix(),
        "adapter_dir": adapter_dir.as_posix(),
        "dry_run": bool(args.dry_run),
        "actions": actions,
        "root_system": root_system,
    }
    if backups:
        result["backups"] = backups
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-return-init-ok
