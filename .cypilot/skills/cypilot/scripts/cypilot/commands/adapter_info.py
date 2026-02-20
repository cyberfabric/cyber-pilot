import argparse
import json
import os
from pathlib import Path
from typing import Optional

from ..utils.files import (
    find_adapter_directory,
    find_project_root,
    load_adapter_config,
    load_project_config,
)


def _load_json_file(path: Path) -> Optional[dict]:
    if not path.is_file():
        return None
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, OSError, IOError):
        return None


def cmd_adapter_info(argv: list[str]) -> int:
    """Discover and display Cypilot adapter information."""
    p = argparse.ArgumentParser(prog="adapter-info", description="Discover Cypilot adapter configuration")
    p.add_argument("--root", default=".", help="Project root to search from (default: current directory)")
    p.add_argument("--cypilot-root", default=None, help="Cypilot core location (if agent knows it)")
    args = p.parse_args(argv)

    start_path = Path(args.root).resolve()
    cypilot_root_path = Path(args.cypilot_root).resolve() if args.cypilot_root else None

    project_root = find_project_root(start_path)
    if project_root is None:
        print(json.dumps(
            {
                "status": "NOT_FOUND",
                "message": "No project root found (no .git or .cypilot-config.json)",
                "searched_from": start_path.as_posix(),
                "hint": "Create .cypilot-config.json in project root to configure Cypilot",
            },
            indent=2,
            ensure_ascii=False,
        ))
        return 1

    adapter_dir = find_adapter_directory(start_path, cypilot_root=cypilot_root_path)
    if adapter_dir is None:
        cfg = load_project_config(project_root)
        if cfg is not None:
            adapter_rel = cfg.get("cypilotAdapterPath")
            if adapter_rel is not None and isinstance(adapter_rel, str):
                print(json.dumps(
                    {
                        "status": "CONFIG_ERROR",
                        "message": "Config specifies adapter path but directory not found or invalid",
                        "project_root": project_root.as_posix(),
                        "config_path": adapter_rel,
                        "expected_location": (project_root / adapter_rel).as_posix(),
                        "hint": "Check .cypilot-config.json cypilotAdapterPath points to valid directory with AGENTS.md",
                    },
                    indent=2,
                    ensure_ascii=False,
                ))
                return 1

        print(json.dumps(
            {
                "status": "NOT_FOUND",
                "message": "No .cypilot-adapter found in project (searched recursively up to 5 levels deep)",
                "project_root": project_root.as_posix(),
                "hint": "Create .cypilot-config.json with cypilotAdapterPath or run adapter-bootstrap workflow",
            },
            indent=2,
            ensure_ascii=False,
        ))
        return 1

    config = load_adapter_config(adapter_dir)
    config["status"] = "FOUND"
    config["project_root"] = project_root.as_posix()

    registry_path = (adapter_dir / "artifacts.json").resolve()
    config["artifacts_registry_path"] = registry_path.as_posix()
    registry = _load_json_file(registry_path)
    if registry is None:
        config["artifacts_registry"] = None
        config["artifacts_registry_error"] = "MISSING_OR_INVALID_JSON" if registry_path.exists() else "MISSING"
        config["autodetect_registry"] = None
    else:
        def _extract_autodetect_registry(raw: object) -> Optional[dict]:
            if not isinstance(raw, dict):
                return None
            if "systems" not in raw:
                return None

            def _extract_system(s: object) -> dict:
                if not isinstance(s, dict):
                    return {}
                out: dict = {}
                for k in ("name", "slug", "kit"):
                    v = s.get(k)
                    if isinstance(v, str):
                        out[k] = v
                if isinstance(s.get("autodetect"), list):
                    out["autodetect"] = s.get("autodetect")
                if isinstance(s.get("children"), list):
                    out["children"] = [_extract_system(ch) for ch in (s.get("children") or [])]
                else:
                    out["children"] = []
                return out

            return {
                "version": raw.get("version"),
                "project_root": raw.get("project_root"),
                "kits": raw.get("kits"),
                "ignore": raw.get("ignore"),
                "systems": [_extract_system(s) for s in (raw.get("systems") or [])],
            }

        config["autodetect_registry"] = _extract_autodetect_registry(registry)

        expanded: object = registry
        if isinstance(registry, dict) and "systems" in registry:
            try:
                from ..utils.context import CypilotContext

                ctx = CypilotContext.load(adapter_dir)
                if ctx is not None:
                    meta = ctx.meta

                    def _artifact_to_dict(a: object) -> dict:
                        return {
                            "path": str(getattr(a, "path", "")),
                            "kind": str(getattr(a, "kind", getattr(a, "type", ""))),
                            "traceability": str(getattr(a, "traceability", "DOCS-ONLY")),
                        }

                    def _codebase_to_dict(c: object) -> dict:
                        d = {
                            "path": str(getattr(c, "path", "")),
                        }
                        exts = getattr(c, "extensions", None)
                        if isinstance(exts, list) and exts:
                            d["extensions"] = [str(x) for x in exts if isinstance(x, str)]
                        nm = getattr(c, "name", None)
                        if isinstance(nm, str) and nm.strip():
                            d["name"] = nm
                        return d

                    def _system_to_dict(s: object) -> dict:
                        out = {
                            "name": str(getattr(s, "name", "")),
                            "slug": str(getattr(s, "slug", "")),
                            "kit": str(getattr(s, "kit", "")),
                            "artifacts": [_artifact_to_dict(a) for a in (getattr(s, "artifacts", []) or [])],
                            "codebase": [_codebase_to_dict(c) for c in (getattr(s, "codebase", []) or [])],
                            "children": [],
                        }
                        out["children"] = [_system_to_dict(ch) for ch in (getattr(s, "children", []) or [])]
                        return out

                    expanded = {
                        "version": str(getattr(meta, "version", "")),
                        "project_root": str(getattr(meta, "project_root", "..")),
                        "kits": {
                            str(kid): {
                                "format": str(getattr(k, "format", "")),
                                "path": str(getattr(k, "path", "")),
                            }
                            for kid, k in (getattr(meta, "kits", {}) or {}).items()
                        },
                        "ignore": [
                            {
                                "reason": str(getattr(blk, "reason", "")),
                                "patterns": list(getattr(blk, "patterns", []) or []),
                            }
                            for blk in (getattr(meta, "ignore", []) or [])
                        ],
                        "systems": [_system_to_dict(s) for s in (getattr(meta, "systems", []) or [])],
                    }
            except Exception:
                expanded = registry

        config["artifacts_registry"] = expanded
        config["artifacts_registry_error"] = None

    try:
        relative_path = adapter_dir.relative_to(project_root).as_posix()
    except ValueError:
        relative_path = adapter_dir.as_posix()
    config["relative_path"] = relative_path

    config_file = project_root / ".cypilot-config.json"
    config["has_config"] = config_file.exists()
    if not config_file.exists():
        config["config_hint"] = f"Create .cypilot-config.json with: {{\"cypilotAdapterPath\": \"{relative_path}\"}}"

    print(json.dumps(config, indent=2, ensure_ascii=False))
    return 0
