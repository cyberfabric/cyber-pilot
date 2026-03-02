"""
workspace-init: Initialize a new workspace by scanning sibling directories for repos with adapters.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _is_project_dir(entry: Path) -> bool:
    """Check if a directory looks like a project (has .git or AGENTS.md with marker)."""
    if (entry / ".git").exists():
        return True
    agents_file = entry / "AGENTS.md"
    if not agents_file.is_file():
        return False
    try:
        head = agents_file.read_text(encoding="utf-8")[:512]
        return "<!-- @cpt:root-agents -->" in head
    except OSError:
        return False


def _find_adapter_path(entry: Path) -> Optional[str]:
    """Find the adapter path for a project directory."""
    from ..utils.files import find_cypilot_directory, _read_cypilot_var

    # v3 discovery: read cypilot_path variable from AGENTS.md
    cypilot_rel = _read_cypilot_var(entry)
    if cypilot_rel:
        candidate = (entry / cypilot_rel).resolve()
        if candidate.is_dir() and (candidate / "config").is_dir():
            return cypilot_rel

    # Fallback: try find_cypilot_directory for recursive search
    found_dir = find_cypilot_directory(entry)
    if found_dir is not None:
        try:
            return str(found_dir.relative_to(entry))
        except ValueError:
            return str(found_dir)
    return None


def _compute_source_path(entry: Path, output_dir: Path) -> str:
    """Compute relative source path from the output location."""
    try:
        return str(entry.relative_to(output_dir).as_posix())
    except ValueError:
        return str(entry.as_posix())


def _infer_role(repo_path: Path) -> str:
    """Best-effort role inference from directory contents."""
    has_src = any((repo_path / d).is_dir() for d in ["src", "lib", "app", "pkg"])
    has_docs = any((repo_path / d).is_dir() for d in ["docs", "architecture", "requirements"])
    has_kits = (repo_path / "kits").is_dir()

    if has_kits and not has_src:
        return "kits"
    if has_docs and not has_src:
        return "artifacts"
    if has_src and not has_docs:
        return "codebase"
    return "full"


def _scan_sibling_repos(
    scan_root: Path,
    project_root: Path,
    output_dir: Path,
) -> Dict[str, dict]:
    """Scan sibling directories for repos with adapters."""
    discovered: Dict[str, dict] = {}
    try:
        entries = sorted(scan_root.iterdir(), key=lambda p: p.name)
    except (PermissionError, OSError):
        entries = []

    for entry in entries:
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        if not _is_project_dir(entry):
            continue
        if entry.resolve() == project_root.resolve():
            continue

        info: dict = {"path": _compute_source_path(entry, output_dir)}
        adapter_path = _find_adapter_path(entry)
        if adapter_path:
            info["adapter"] = adapter_path
        info["role"] = _infer_role(entry)
        discovered[entry.name] = info

    return discovered


def _json_error(message: str) -> str:
    """Format a JSON error response."""
    return json.dumps({"status": "ERROR", "message": message}, indent=2, ensure_ascii=False)


def _write_inline(
    project_root: Path,
    workspace_data: dict,
) -> Tuple[int, str]:
    """Write workspace config inline into core.toml. Returns (exit_code, json_output)."""
    from ..utils.files import _read_cypilot_var
    from ..utils import toml_utils

    cypilot_rel = _read_cypilot_var(project_root)
    if not cypilot_rel:
        return 1, _json_error("Cannot write inline workspace: no cypilot_path found in AGENTS.md. Run 'cypilot init' first.")

    config_path = (project_root / cypilot_rel / "config" / "core.toml").resolve()
    if not config_path.is_file():
        config_path = (project_root / cypilot_rel / "core.toml").resolve()

    existing: dict = {}
    if config_path.is_file():
        try:
            existing = toml_utils.load(config_path)
            if not isinstance(existing, dict):
                return 1, _json_error(f"Invalid config format in {config_path} (expected mapping)")
        except (ValueError, OSError) as e:
            return 1, _json_error(f"Failed to parse {config_path}: {e}")

    existing["workspace"] = workspace_data
    try:
        toml_utils.dump(existing, config_path)
    except Exception as e:
        return 1, _json_error(f"Failed to write workspace to {config_path}: {e}")

    return 0, json.dumps({
        "status": "CREATED",
        "message": "Workspace added inline to core.toml",
        "config_path": str(config_path),
        "sources_count": len(workspace_data.get("sources", {})),
        "sources": list(workspace_data.get("sources", {}).keys()),
    }, indent=2, ensure_ascii=False)


def _write_standalone(
    output_path: Path,
    workspace_data: dict,
) -> Tuple[int, str]:
    """Write standalone .cypilot-workspace.toml. Returns (exit_code, json_output)."""
    from ..constants import WORKSPACE_CONFIG_FILENAME
    from ..utils import toml_utils

    if output_path.is_dir():
        output_path = output_path / WORKSPACE_CONFIG_FILENAME

    try:
        toml_utils.dump(workspace_data, output_path)
    except OSError as e:
        return 1, _json_error(f"Failed to write workspace config to {output_path}: {e}")

    return 0, json.dumps({
        "status": "CREATED",
        "message": f"Workspace config created at {output_path}",
        "workspace_path": str(output_path),
        "sources_count": len(workspace_data.get("sources", {})),
        "sources": list(workspace_data.get("sources", {}).keys()),
    }, indent=2, ensure_ascii=False)


def cmd_workspace_init(argv: List[str]) -> int:
    """Initialize a multi-repo workspace."""
    p = argparse.ArgumentParser(
        prog="workspace-init",
        description="Initialize a new workspace: scan sibling dirs for repos with adapters, generate .cypilot-workspace.toml",
    )
    p.add_argument(
        "--root", default=None,
        help="Directory to scan for sibling repos (default: parent of current project root)",
    )
    p.add_argument(
        "--output", default=None,
        help="Where to write .cypilot-workspace.toml (default: scan root)",
    )
    p.add_argument(
        "--inline", action="store_true",
        help="Write workspace config inline into current repo's config/core.toml instead of standalone file",
    )
    p.add_argument("--dry-run", action="store_true", help="Print what would be generated without writing files")
    args = p.parse_args(argv)

    from ..constants import WORKSPACE_CONFIG_FILENAME
    from ..utils.files import find_project_root

    project_root = find_project_root(Path.cwd())
    if project_root is None:
        print(_json_error("No project root found. Run from inside a project with .git or AGENTS.md."))
        return 1

    scan_root = Path(args.root).resolve() if args.root else project_root.parent
    if not scan_root.is_dir():
        print(_json_error(f"Scan root directory not found: {scan_root}"))
        return 1

    # Determine output dir for relative path computation
    output_dir = Path(args.output).resolve().parent if args.output else scan_root
    if args.inline:
        output_dir = project_root

    discovered = _scan_sibling_repos(scan_root, project_root, output_dir)

    if not discovered:
        print(json.dumps({
            "status": "NO_SOURCES",
            "message": "No sibling repos with adapters found",
            "scan_root": str(scan_root),
            "hint": "Ensure sibling directories have .git or AGENTS.md with @cpt:root-agents marker",
        }, indent=2, ensure_ascii=False))
        return 0

    workspace_data: dict = {"version": "1.0", "sources": discovered}

    if args.dry_run:
        print(json.dumps({
            "status": "DRY_RUN",
            "message": "Would generate workspace config",
            "workspace": workspace_data,
            "sources_found": len(discovered),
        }, indent=2, ensure_ascii=False))
        return 0

    if args.inline:
        exit_code, output = _write_inline(project_root, workspace_data)
    else:
        output_path = Path(args.output).resolve() if args.output else (scan_root / WORKSPACE_CONFIG_FILENAME)
        exit_code, output = _write_standalone(output_path, workspace_data)

    print(output)
    return exit_code
