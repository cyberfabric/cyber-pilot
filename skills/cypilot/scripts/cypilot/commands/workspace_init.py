"""
workspace-init: Initialize a new workspace by scanning sibling directories for repos with adapters.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List


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
    from ..utils.files import find_project_root, find_cypilot_directory, _read_cypilot_var, load_project_config

    project_root = find_project_root(Path.cwd())
    if project_root is None:
        print(json.dumps({
            "status": "ERROR",
            "message": "No project root found. Run from inside a project with .git or AGENTS.md.",
        }, indent=2, ensure_ascii=False))
        return 1

    scan_root = Path(args.root).resolve() if args.root else project_root.parent
    if not scan_root.is_dir():
        print(json.dumps({
            "status": "ERROR",
            "message": f"Scan root directory not found: {scan_root}",
        }, indent=2, ensure_ascii=False))
        return 1

    # Scan for repos with adapters
    discovered: Dict[str, dict] = {}
    try:
        entries = sorted(scan_root.iterdir(), key=lambda p: p.name)
    except (PermissionError, OSError):
        entries = []

    for entry in entries:
        if not entry.is_dir() or entry.name.startswith("."):
            continue

        # Check if this looks like a project (v3: AGENTS.md with marker, or .git)
        has_git = (entry / ".git").exists()
        has_agents_marker = False
        agents_file = entry / "AGENTS.md"
        if agents_file.is_file():
            try:
                head = agents_file.read_text(encoding="utf-8")[:512]
                has_agents_marker = "<!-- @cpt:root-agents -->" in head
            except OSError:
                pass
        if not has_git and not has_agents_marker:
            continue

        # Look for cypilot directory (v3: read cypilot_path from AGENTS.md TOML block)
        adapter_path = None

        # v3 discovery: read cypilot_path variable from AGENTS.md
        cypilot_rel = _read_cypilot_var(entry)
        if cypilot_rel:
            candidate = (entry / cypilot_rel).resolve()
            if candidate.is_dir() and (candidate / "config").is_dir():
                adapter_path = cypilot_rel

        # Fallback: try find_cypilot_directory for recursive search
        if adapter_path is None:
            found_dir = find_cypilot_directory(entry)
            if found_dir is not None:
                try:
                    adapter_path = str(found_dir.relative_to(entry))
                except ValueError:
                    adapter_path = str(found_dir)

        # Skip the current project (it will be the primary)
        if entry.resolve() == project_root.resolve():
            continue

        try:
            rel = entry.relative_to(scan_root).as_posix()
        except ValueError:
            rel = entry.as_posix()

        # Determine path relative to output location
        output_dir = Path(args.output).resolve().parent if args.output else scan_root
        if args.inline:
            output_dir = project_root
        try:
            source_path = str(entry.relative_to(output_dir).as_posix())
        except ValueError:
            source_path = str(entry.as_posix())

        info: dict = {"path": source_path}
        if adapter_path:
            info["adapter"] = adapter_path
        # Infer role from directory structure
        info["role"] = _infer_role(entry)

        discovered[entry.name] = info

    if not discovered:
        print(json.dumps({
            "status": "NO_SOURCES",
            "message": "No sibling repos with adapters found",
            "scan_root": str(scan_root),
            "hint": "Ensure sibling directories have .git or AGENTS.md with @cpt:root-agents marker",
        }, indent=2, ensure_ascii=False))
        return 0

    workspace_data: dict = {
        "version": "1.0",
        "sources": discovered,
    }

    if args.dry_run:
        print(json.dumps({
            "status": "DRY_RUN",
            "message": "Would generate workspace config",
            "workspace": workspace_data,
            "sources_found": len(discovered),
        }, indent=2, ensure_ascii=False))
        return 0

    if args.inline:
        # Write inline into core.toml [workspace] section
        cypilot_rel = _read_cypilot_var(project_root)
        if not cypilot_rel:
            print(json.dumps({
                "status": "ERROR",
                "message": "Cannot write inline workspace: no cypilot_path found in AGENTS.md. Run 'cypilot init' first.",
            }, indent=2, ensure_ascii=False))
            return 1

        config_path = (project_root / cypilot_rel / "config" / "core.toml").resolve()
        if not config_path.is_file():
            config_path = (project_root / cypilot_rel / "core.toml").resolve()

        from ..utils import toml_utils
        existing: dict = {}
        if config_path.is_file():
            try:
                existing = toml_utils.load(config_path)
                if not isinstance(existing, dict):
                    print(json.dumps({
                        "status": "ERROR",
                        "message": f"Invalid config format in {config_path} (expected mapping)",
                    }, indent=2, ensure_ascii=False))
                    return 1
            except (ValueError, OSError) as e:
                print(json.dumps({
                    "status": "ERROR",
                    "message": f"Failed to parse {config_path}: {e}",
                }, indent=2, ensure_ascii=False))
                return 1

        existing["workspace"] = {"sources": discovered}
        try:
            toml_utils.dump(existing, config_path)
        except Exception as e:
            print(json.dumps({
                "status": "ERROR",
                "message": f"Failed to write workspace to {config_path}: {e}",
            }, indent=2, ensure_ascii=False))
            return 1

        print(json.dumps({
            "status": "CREATED",
            "message": "Workspace added inline to core.toml",
            "config_path": str(config_path),
            "sources_count": len(discovered),
            "sources": list(discovered.keys()),
        }, indent=2, ensure_ascii=False))
    else:
        # Write standalone .cypilot-workspace.toml
        from ..utils import toml_utils as _toml_utils
        output_path = Path(args.output).resolve() if args.output else (scan_root / WORKSPACE_CONFIG_FILENAME)
        if output_path.is_dir():
            output_path = output_path / WORKSPACE_CONFIG_FILENAME
        try:
            _toml_utils.dump(workspace_data, output_path)
        except OSError as e:
            print(json.dumps({
                "status": "ERROR",
                "message": f"Failed to write workspace config to {output_path}: {e}",
            }, indent=2, ensure_ascii=False))
            return 1
        print(json.dumps({
            "status": "CREATED",
            "message": f"Workspace config created at {output_path}",
            "workspace_path": str(output_path),
            "sources_count": len(discovered),
            "sources": list(discovered.keys()),
        }, indent=2, ensure_ascii=False))

    return 0


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
