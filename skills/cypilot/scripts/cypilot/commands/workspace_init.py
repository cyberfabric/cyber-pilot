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
        description="Initialize a new workspace: scan sibling dirs for repos with adapters, generate .cypilot-workspace.json",
    )
    p.add_argument(
        "--root", default=None,
        help="Directory to scan for sibling repos (default: parent of current project root)",
    )
    p.add_argument(
        "--output", default=None,
        help="Where to write .cypilot-workspace.json (default: scan root)",
    )
    p.add_argument(
        "--inline", action="store_true",
        help="Write workspace config inline into current repo's .cypilot-config.json instead of standalone file",
    )
    p.add_argument("--dry-run", action="store_true", help="Print what would be generated without writing files")
    args = p.parse_args(argv)

    from ..constants import PROJECT_CONFIG_FILENAME, WORKSPACE_CONFIG_FILENAME
    from ..utils.files import find_project_root

    project_root = find_project_root(Path.cwd())
    if project_root is None:
        print(json.dumps({
            "status": "ERROR",
            "message": "No project root found. Run from inside a project with .git or .cypilot-config.json.",
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

        # Check if this looks like a project
        has_git = (entry / ".git").exists()
        has_config = (entry / PROJECT_CONFIG_FILENAME).is_file()
        if not has_git and not has_config:
            continue

        # Look for adapter
        adapter_path = None
        if has_config:
            try:
                import json as _json
                cfg = _json.loads((entry / PROJECT_CONFIG_FILENAME).read_text(encoding="utf-8"))
                adapter_rel = cfg.get("cypilotAdapterPath") if isinstance(cfg, dict) else None
                if isinstance(adapter_rel, str) and adapter_rel.strip():
                    candidate = (entry / adapter_rel.strip()).resolve()
                    if candidate.is_dir() and (candidate / "AGENTS.md").exists():
                        adapter_path = adapter_rel.strip()
            except Exception:
                pass

        if adapter_path is None:
            # Check common adapter locations
            for candidate_name in [".cypilot-adapter", ".cypilot"]:
                candidate = entry / candidate_name
                if candidate.is_dir() and (candidate / "AGENTS.md").exists():
                    adapter_path = candidate_name
                    break

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
            "hint": "Ensure sibling directories have .git or .cypilot-config.json",
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
        # Write inline into .cypilot-config.json
        config_path = project_root / PROJECT_CONFIG_FILENAME
        try:
            existing = json.loads(config_path.read_text(encoding="utf-8")) if config_path.is_file() else {}
            if not isinstance(existing, dict):
                existing = {}
        except Exception:
            existing = {}

        existing["workspace"] = {"sources": discovered}
        config_path.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({
            "status": "CREATED",
            "message": "Workspace added inline to .cypilot-config.json",
            "config_path": str(config_path),
            "sources_count": len(discovered),
            "sources": list(discovered.keys()),
        }, indent=2, ensure_ascii=False))
    else:
        # Write standalone .cypilot-workspace.json
        output_path = Path(args.output).resolve() if args.output else (scan_root / WORKSPACE_CONFIG_FILENAME)
        output_path.write_text(
            json.dumps(workspace_data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
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
