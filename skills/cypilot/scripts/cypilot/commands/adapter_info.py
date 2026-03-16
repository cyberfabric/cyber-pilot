"""
Adapter Info Command — discover and display Cypilot project configuration.

Shows project root, cypilot directory, rules, systems, and registry status.

@cpt-flow:cpt-cypilot-flow-core-infra-cli-invocation:p1
@cpt-dod:cpt-cypilot-dod-core-infra-init-config:p1
"""

import argparse
import json
import os
from pathlib import Path
from typing import Optional

from ..utils.files import (
    find_cypilot_directory,
    find_project_root,
    load_cypilot_config,
)
from ..utils.git_utils import _redact_url
from ..utils.ui import ui

def _load_json_file(path: Path) -> Optional[dict]:
    if not path.is_file():
        return None
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, OSError, IOError):
        return None

def _read_kit_conf(conf_path: Path) -> dict:
    """Read kit conf.toml and return key fields."""
    try:
        import tomllib
        with open(conf_path, "rb") as f:
            data = tomllib.load(f)
        out: dict = {}
        for k in ("version", "slug", "name"):
            if k in data:
                out[k] = data[k]
        return out
    except Exception:
        return {}

def cmd_adapter_info(argv: list[str]) -> int:
    """Discover and display Cypilot project configuration."""
    # @cpt-begin:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-parse-args
    p = argparse.ArgumentParser(prog="info", description="Discover Cypilot project configuration")
    p.add_argument("--root", default=".", help="Project root to search from (default: current directory)")
    p.add_argument("--cypilot-root", default=None, help="Cypilot core location (if agent knows it)")
    args = p.parse_args(argv)

    start_path = Path(args.root).resolve()
    cypilot_root_path = Path(args.cypilot_root).resolve() if args.cypilot_root else None
    # @cpt-end:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-parse-args

    # @cpt-begin:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-find-root
    project_root = find_project_root(start_path)
    # @cpt-end:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-find-root
    # @cpt-begin:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-if-no-root
    if project_root is None:
        # @cpt-begin:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-return-no-root
        ui.result({
            "status": "NOT_FOUND",
            "message": "No project root found (no AGENTS.md with @cpt:root-agents or .git)",
            "searched_from": start_path.as_posix(),
            "hint": "Run 'cypilot init' in your project root",
        })
        return 1
        # @cpt-end:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-return-no-root
    # @cpt-end:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-if-no-root

    # @cpt-begin:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-find-cypilot
    adapter_dir = find_cypilot_directory(start_path, cypilot_root=cypilot_root_path)
    # @cpt-end:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-find-cypilot
    # @cpt-begin:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-if-no-cypilot
    if adapter_dir is None:
        # @cpt-begin:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-return-no-cypilot
        ui.result({
            "status": "NOT_FOUND",
            "message": "Cypilot not initialized in project",
            "project_root": project_root.as_posix(),
            "hint": "Run 'cypilot init' to initialize Cypilot for this project",
        })
        return 1
        # @cpt-end:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-return-no-cypilot
    # @cpt-end:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-if-no-cypilot

    # @cpt-begin:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-load-config
    config = load_cypilot_config(adapter_dir)
    # @cpt-end:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-load-config
    config["status"] = "FOUND"
    config["project_root"] = project_root.as_posix()

    # @cpt-begin:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-locate-registry
    registry_path = (adapter_dir / "config" / "artifacts.toml").resolve()
    # Fallback: legacy flat layout
    if not registry_path.is_file():
        registry_path = (adapter_dir / "artifacts.toml").resolve()
    if not registry_path.is_file():
        legacy = adapter_dir / "artifacts.json"
        if legacy.is_file():
            registry_path = legacy.resolve()
    config["artifacts_registry_path"] = registry_path.as_posix()
    registry = _load_json_file(registry_path) if registry_path.suffix == ".json" else None
    if registry is None and registry_path.suffix == ".toml" and registry_path.is_file():
        try:
            import tomllib
            with open(registry_path, "rb") as f:
                registry = tomllib.load(f)
        except Exception:
            registry = None
    # Load core.toml for version/project_root/kits (authoritative source)
    core_data: Optional[dict] = None
    core_load_error: Optional[str] = None
    for cp in [(adapter_dir / "config" / "core.toml"), (adapter_dir / "core.toml")]:
        if cp.is_file():
            try:
                import tomllib as _tl
                with open(cp, "rb") as f:
                    core_data = _tl.load(f)
            except (_tl.TOMLDecodeError, OSError) as exc:
                core_load_error = f"{type(exc).__name__}: {exc}"
            break

    # @cpt-end:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-locate-registry
    # @cpt-begin:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-registry-missing
    if registry is None:
        config["artifacts_registry"] = None
        config["artifacts_registry_error"] = "MISSING_OR_INVALID_JSON" if registry_path.exists() else "MISSING"
        config["autodetect_registry"] = None
    # @cpt-end:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-registry-missing
    # @cpt-begin:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-expand-registry
    else:
        def _extract_autodetect_registry(raw: object, core: Optional[dict]) -> Optional[dict]:
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

            # version/project_root/kits: prefer core.toml, fallback to registry
            version = raw.get("version")
            p_root = raw.get("project_root")
            kits = raw.get("kits")
            if isinstance(core, dict):
                if version is None and isinstance(core.get("version"), str):
                    version = core["version"]
                if p_root is None and isinstance(core.get("project_root"), str):
                    p_root = core["project_root"]
                if (not kits) and isinstance(core.get("kits"), dict):
                    kits = core["kits"]

            return {
                "version": version,
                "project_root": p_root,
                "kits": kits,
                "ignore": raw.get("ignore"),
                "systems": [_extract_system(s) for s in (raw.get("systems") or [])],
            }

        config["autodetect_registry"] = _extract_autodetect_registry(registry, core_data)

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
                        slc = getattr(c, "single_line_comments", None)
                        if isinstance(slc, list) and slc:
                            d["singleLineComments"] = slc
                        mlc = getattr(c, "multi_line_comments", None)
                        if isinstance(mlc, list) and mlc:
                            d["multiLineComments"] = mlc
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
    # @cpt-end:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-expand-registry

    # @cpt-begin:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-compute-metadata
    try:
        relative_path = adapter_dir.relative_to(project_root).as_posix()
    except ValueError:
        relative_path = adapter_dir.as_posix()
    config["relative_path"] = relative_path

    core_toml = adapter_dir / "config" / "core.toml"
    if not core_toml.is_file():
        core_toml = adapter_dir / "core.toml"
    config["has_config"] = core_toml.exists()

    # Core config version
    if core_data and isinstance(core_data.get("version"), str):
        config["config_version"] = core_data["version"]

    # Kit details: versions, content, drift
    kit_details = {}
    config_kits_dir = adapter_dir / "config" / "kits"
    if config_kits_dir.is_dir():
        for kit_dir in sorted(config_kits_dir.iterdir()):
            if not kit_dir.is_dir():
                continue
            slug = kit_dir.name
            kd: dict = {"slug": slug}
            # Resolve core.toml entry for this kit once
            core_kit: dict = {}
            if core_data and isinstance(core_data.get("kits"), dict):
                _ck = core_data["kits"].get(slug, {})
                if isinstance(_ck, dict):
                    core_kit = _ck
            # Version from core.toml (single source of truth)
            if "version" in core_kit:
                kd["version"] = core_kit["version"]
            # Name/slug from kit's conf.toml in source (fallback)
            kit_conf = kit_dir / "conf.toml"
            if kit_conf.is_file():
                conf_info = _read_kit_conf(kit_conf)
                if "name" in conf_info:
                    kd["name"] = conf_info["name"]
                if "slug" in conf_info and "slug" not in kd:
                    kd["slug"] = conf_info["slug"]
            # Content directories present
            content_dirs = sorted(
                d.name for d in kit_dir.iterdir()
                if d.is_dir() and d.name in ("artifacts", "codebase", "scripts", "workflows")
            )
            if content_dirs:
                kd["content_dirs"] = content_dirs
            # Artifact kinds (from config/kits/{slug}/artifacts/)
            art_dir = kit_dir / "artifacts"
            if art_dir.is_dir():
                kd["artifact_kinds"] = sorted(d.name for d in art_dir.iterdir() if d.is_dir())
            # Workflows (from config/kits/{slug}/workflows/)
            wf_dir = kit_dir / "workflows"
            if wf_dir.is_dir():
                kd["workflows"] = sorted(f.stem for f in wf_dir.glob("*.md"))
            # Resources (from core.toml [kits.{slug}.resources])
            if isinstance(core_kit.get("resources"), dict):
                kd["resources"] = core_kit["resources"]
            kit_details[slug] = kd
    config["kit_details"] = kit_details

    # Agent integrations
    agents_found = []
    agent_dirs = {
        "windsurf": project_root / ".windsurf",
        "cursor": project_root / ".cursor",
        "claude": project_root / ".claude",
        "copilot": project_root / ".github" / "copilot-instructions.md",
        "openai": project_root / ".agents",
    }
    for agent_name, agent_path in agent_dirs.items():
        if agent_path.exists():
            agents_found.append(agent_name)
    config["agent_integrations"] = agents_found

    # Directory structure health
    dirs_status = {}
    for subdir in [".core", ".gen", "config"]:
        d = adapter_dir / subdir
        dirs_status[subdir] = d.is_dir()
    config["directories"] = dirs_status

    # Resolved template variables (flat dict for format_map substitution)
    if core_load_error is not None:
        config["variables"] = None
        config["variables_error"] = f"core.toml load failed: {core_load_error}"
        config["variables_degraded"] = True
    else:
        try:
            from .resolve_vars import _collect_all_variables
            vars_result = _collect_all_variables(project_root, adapter_dir, core_data)
            config["variables"] = vars_result["variables"]
            config["variables_by_kit"] = vars_result.get("kits", {})
            if vars_result.get("collisions"):
                config["variables_collisions"] = vars_result["collisions"]
        except (ImportError, OSError, ValueError) as exc:
            config["variables"] = None
            config["variables_error"] = str(exc)
            config["variables_degraded"] = True
    # @cpt-end:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-compute-metadata

    # @cpt-begin:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-workspace-section
    # Add workspace section when workspace detected
    try:
        from ..utils.workspace import find_workspace_config

        ws_cfg, ws_err = find_workspace_config(project_root)
        if ws_cfg is not None:
            ws_info: dict = {
                "active": True,
                "version": ws_cfg.version,
                "is_inline": ws_cfg.is_inline,
                "location": "inline (core.toml)" if ws_cfg.is_inline else str(ws_cfg.workspace_file),
                "sources_count": len(ws_cfg.sources),
                "sources": {},
            }
            for name, src in ws_cfg.sources.items():
                if src.url:
                    # For URL sources, peek at expected cache path without cloning
                    from ..utils.git_utils import peek_git_source_path
                    from ..utils.workspace import ResolveConfig
                    base = ws_cfg.resolution_base or (ws_cfg.workspace_file.parent if ws_cfg.workspace_file else None)
                    resolved = peek_git_source_path(src, ws_cfg.resolve or ResolveConfig(), base) if base else None
                    reachable = resolved is not None and resolved.is_dir()
                else:
                    resolved = ws_cfg.resolve_source_path(name)
                    reachable = resolved is not None and resolved.is_dir()
                ws_info["sources"][name] = {
                    "path": src.path or (_redact_url(src.url) if src.url else None),
                    "role": src.role,
                    "reachable": reachable,
                }
            config["workspace"] = ws_info
        else:
            ws_data: dict = {"active": False}
            if ws_err:
                ws_data["error"] = ws_err
            config["workspace"] = ws_data
    except Exception as exc:
        config["workspace"] = {"active": False, "error": str(exc)}
    # @cpt-end:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-workspace-section

    # @cpt-begin:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-return-ok
    ui.result(config, human_fn=_human_info)
    return 0
    # @cpt-end:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-return-ok

# @cpt-begin:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-human-fmt
def _human_info(data: dict) -> None:
    """Human-friendly formatter for the info command."""
    ui.header("Cypilot Project Info")

    # Basic info
    if data.get("project_name"):
        ui.detail("Project", str(data["project_name"]))
    ui.detail("Project root", str(data.get("project_root", "?")))
    ui.detail("Cypilot dir", str(data.get("relative_path", data.get("cypilot_dir", "?"))))
    if data.get("config_version"):
        ui.detail("Config version", str(data["config_version"]))

    # Directory structure health
    dirs = data.get("directories", {})
    if dirs:
        missing = [d for d, ok in dirs.items() if not ok]
        if missing:
            ui.warn(f"Missing directories: {', '.join(missing)}")

    # Kit details
    kit_details = data.get("kit_details", {})
    if kit_details:
        ui.blank()
        ui.step(f"Kits ({len(kit_details)})")
        for slug, kd in kit_details.items():
            name = kd.get("name", slug)
            ver = kd.get("version", "?")
            ui.substep(f"  {name}  v{ver}")

            cdirs = kd.get("content_dirs", [])
            if cdirs:
                ui.substep(f"    Content: {', '.join(cdirs)}")

            kinds = kd.get("artifact_kinds", [])
            if kinds:
                ui.substep(f"    Artifact kinds ({len(kinds)}): {', '.join(kinds)}")

            wfs = kd.get("workflows", [])
            if wfs:
                ui.substep(f"    Workflows: {', '.join(wfs)}")

            res = kd.get("resources", {})
            if res:
                ui.substep(f"    Resources ({len(res)}):")
                for rid, rbind in res.items():
                    rpath = rbind.get("path", "?") if isinstance(rbind, dict) else str(rbind)
                    ui.substep(f"      {rid}: {rpath}")

    # Systems with artifacts
    auto_reg = data.get("autodetect_registry") or {}
    systems = auto_reg.get("systems") or []
    reg = data.get("artifacts_registry")
    reg_systems = (reg.get("systems") or []) if isinstance(reg, dict) else []

    if systems or reg_systems:
        ui.blank()
        display_systems = reg_systems if reg_systems else systems
        ui.step(f"Systems ({len(display_systems)})")
        for sys_info in display_systems:
            if not isinstance(sys_info, dict):
                continue
            name = sys_info.get("name", "?")
            slug = sys_info.get("slug", "")
            kit = sys_info.get("kit", "")
            label = f"{name} ({slug})" if slug else name
            if kit:
                label += f"  kit={kit}"
            ui.substep(f"  {label}")

            # Artifacts
            arts = sys_info.get("artifacts") or []
            if arts:
                for a in arts:
                    if isinstance(a, dict):
                        path = a.get("path", "?")
                        kind = a.get("kind", "")
                        trace = a.get("traceability", "")
                        parts = [path]
                        if kind:
                            parts.append(kind)
                        if trace and trace != "DOCS-ONLY":
                            parts.append(trace)
                        ui.substep(f"      {parts[0]}  ({', '.join(parts[1:])})" if len(parts) > 1 else f"      {parts[0]}")

            # Codebase
            codes = sys_info.get("codebase") or []
            if codes:
                for c in codes:
                    if isinstance(c, dict):
                        cpath = c.get("path", "?")
                        exts = c.get("extensions") or []
                        ext_str = f"  [{', '.join(exts)}]" if exts else ""
                        ui.substep(f"      {cpath}{ext_str}")

            # Children
            for ch in (sys_info.get("children") or []):
                if isinstance(ch, dict):
                    ch_name = ch.get("name", "?")
                    ch_slug = ch.get("slug", "")
                    ui.substep(f"    └ {ch_name} ({ch_slug})")
                    for a in (ch.get("artifacts") or []):
                        if isinstance(a, dict):
                            ui.substep(f"        {a.get('path', '?')}  ({a.get('kind', '')})")
                    for c in (ch.get("codebase") or []):
                        if isinstance(c, dict):
                            cpath = c.get("path", "?")
                            exts = c.get("extensions") or []
                            ext_str = f"  [{', '.join(exts)}]" if exts else ""
                            ui.substep(f"        {cpath}{ext_str}")

    # Rules
    rules = data.get("rules", [])
    if rules:
        ui.blank()
        ui.step(f"Rules ({len(rules)})")
        for r in rules:
            ui.substep(f"  {r}")

    # Agent integrations
    agents = data.get("agent_integrations", [])
    if agents:
        ui.blank()
        ui.step(f"Agent integrations ({len(agents)})")
        ui.substep(f"  {', '.join(agents)}")

    # @cpt-begin:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-info-render-variables
    # Resolved variables
    variables = data.get("variables") or {}
    if variables:
        ui.blank()
        ui.step(f"Variables ({len(variables)})")
        for name, path in sorted(variables.items()):
            ui.substep(f"  {{{name}}}: {ui.relpath(path)}")
    if data.get("variables_degraded"):
        ui.blank()
        ui.warn(f"Variables: {data.get('variables_error', 'unknown error')}")
    # @cpt-end:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-info-render-variables

    # Workspace
    ws = data.get("workspace", {})
    if ws.get("active"):
        ui.blank()
        ui.step("Workspace")
        ui.substep(f"  Location: {ws.get('location', '?')}")
        ui.substep(f"  Sources: {ws.get('sources_count', 0)}")
    elif ws.get("error"):
        ui.blank()
        ui.warn(f"Workspace: {ws['error']}")

    # Registry errors
    reg_err = data.get("artifacts_registry_error")
    if reg_err:
        ui.blank()
        ui.warn(f"Registry: {reg_err}")

    ui.blank()
# @cpt-end:cpt-cypilot-algo-core-infra-display-info:p1:inst-info-human-fmt
