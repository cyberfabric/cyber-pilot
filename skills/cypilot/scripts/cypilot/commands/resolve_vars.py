"""
Resolve Variables Command — resolve template variables to absolute paths.

Reads kit resource bindings from ``core.toml`` and resolves all template
variables (``{adr_template}``, ``{scripts}``, ``{cypilot_path}``, etc.)
to absolute file paths.  Output is a flat dict suitable for
``str.format_map()`` substitution in Markdown files.

@cpt-flow:cpt-cypilot-flow-developer-experience-resolve-vars:p1
@cpt-dod:cpt-cypilot-dod-developer-experience-resolve-vars:p1
"""

import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..utils.files import (
    find_cypilot_directory,
    find_project_root,
)
from ..utils.ui import ui


# @cpt-begin:cpt-cypilot-algo-developer-experience-resolve-vars:p1:inst-merge-flat-dict
def _merge_with_collision_tracking(
    system_vars: Dict[str, str],
    kit_vars: Dict[str, Dict[str, str]],
) -> Tuple[Dict[str, str], List[Dict[str, str]]]:
    """Merge system and kit variables with first-writer-wins collision tracking.

    Returns (flat_dict, collisions_list).
    """
    flat: Dict[str, str] = dict(system_vars)
    collisions: List[Dict[str, str]] = []
    owners: Dict[str, str] = {k: "system" for k in system_vars}
    for slug, kvars in kit_vars.items():
        for var_name, var_path in kvars.items():
            if var_name in flat and flat[var_name] != var_path:
                collisions.append({
                    "variable": var_name,
                    "kit": slug,
                    "path": var_path,
                    "previous_kit": owners[var_name],
                    "previous_path": flat[var_name],
                })
                continue  # first-writer-wins; skip collision
            flat[var_name] = var_path
            owners[var_name] = slug
    return flat, collisions
# @cpt-end:cpt-cypilot-algo-developer-experience-resolve-vars:p1:inst-merge-flat-dict


# @cpt-begin:cpt-cypilot-algo-developer-experience-resolve-vars:p1:inst-resolve-binding-path
def _resolve_kit_variables(
    adapter_dir: Path,
    core_kit: dict,
) -> Dict[str, str]:
    """Resolve resource bindings for a single kit to absolute paths."""
    resources = core_kit.get("resources")
    if not isinstance(resources, dict):
        return {}

    result: Dict[str, str] = {}
    for identifier, binding in resources.items():
        # @cpt-begin:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-resolve-binding
        if isinstance(binding, dict):
            raw_path = binding.get("path")
            if not isinstance(raw_path, str):
                continue
            rel_path = raw_path.strip()
        elif isinstance(binding, str):
            rel_path = binding.strip()
        else:
            continue
        if not rel_path:
            continue
        result[identifier] = (adapter_dir / rel_path).resolve().as_posix()
        # @cpt-end:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-resolve-binding

    return result
# @cpt-end:cpt-cypilot-algo-developer-experience-resolve-vars:p1:inst-resolve-binding-path


def _collect_all_variables(
    project_root: Path,
    adapter_dir: Path,
    core_data: Optional[dict],
) -> Dict[str, Any]:
    """Collect all template variables from system config and kit resources.

    Returns a dict with:
    - ``system``: system-level variables (cypilot_path, project_root, etc.)
    - ``kits``: per-kit resource variables {slug: {var: path}}
    - ``variables``: flat merged dict of all variables for format_map()
    """
    # @cpt-begin:cpt-cypilot-algo-developer-experience-resolve-vars:p1:inst-collect-system-vars
    # @cpt-begin:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-system
    # -- System variables --
    system_vars: Dict[str, str] = {
        "cypilot_path": adapter_dir.resolve().as_posix(),
        "project_root": project_root.resolve().as_posix(),
    }
    # @cpt-end:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-system
    # @cpt-end:cpt-cypilot-algo-developer-experience-resolve-vars:p1:inst-collect-system-vars

    # @cpt-begin:cpt-cypilot-algo-developer-experience-resolve-vars:p1:inst-extract-kit-resources
    # @cpt-begin:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-foreach-kit
    # -- Kit resource variables --
    kit_vars: Dict[str, Dict[str, str]] = {}
    if core_data and isinstance(core_data.get("kits"), dict):
        for slug, kit_entry in core_data["kits"].items():
            if not isinstance(kit_entry, dict):
                continue
            resolved = _resolve_kit_variables(
                adapter_dir, kit_entry,
            )
            if resolved:
                kit_vars[slug] = resolved
    # @cpt-end:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-foreach-kit
    # @cpt-end:cpt-cypilot-algo-developer-experience-resolve-vars:p1:inst-extract-kit-resources

    # -- Flat merged dict (system + all kits) --
    flat, collisions = _merge_with_collision_tracking(system_vars, kit_vars)

    # @cpt-begin:cpt-cypilot-algo-developer-experience-resolve-vars:p1:inst-return-structured
    result: Dict[str, Any] = {
        "system": system_vars,
        "kits": kit_vars,
        "variables": flat,
    }
    if collisions:
        result["collisions"] = collisions
    return result
    # @cpt-end:cpt-cypilot-algo-developer-experience-resolve-vars:p1:inst-return-structured


def cmd_resolve_vars(argv: list[str]) -> int:
    """Resolve template variables to absolute paths."""
    # @cpt-begin:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-parse-args
    p = argparse.ArgumentParser(
        prog="resolve-vars",
        description="Resolve template variables to absolute paths",
    )
    p.add_argument(
        "--root", default=".",
        help="Project root to search from (default: current directory)",
    )
    p.add_argument(
        "--kit", default=None,
        help="Filter to a specific kit slug",
    )
    p.add_argument(
        "--flat", action="store_true",
        help="Output only the flat variables dict (default: structured output)",
    )
    args = p.parse_args(argv)

    start_path = Path(args.root).resolve()
    # @cpt-end:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-parse-args

    # @cpt-begin:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-discover
    # -- Discover project --
    project_root = find_project_root(start_path)
    if project_root is None:
        ui.result({
            "status": "ERROR",
            "message": "No project root found",
            "searched_from": start_path.as_posix(),
        })
        return 1

    adapter_dir = find_cypilot_directory(start_path)
    if adapter_dir is None:
        ui.result({
            "status": "ERROR",
            "message": "Cypilot not initialized in project",
            "project_root": project_root.as_posix(),
        })
        return 1
    # @cpt-end:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-discover

    # @cpt-begin:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-load-core
    # -- Load core.toml --
    core_data: Optional[dict] = None
    for cp in [
        adapter_dir / "config" / "core.toml",
        adapter_dir / "core.toml",
    ]:
        if cp.is_file():
            try:
                import tomllib
                with open(cp, "rb") as f:
                    core_data = tomllib.load(f)
            except (tomllib.TOMLDecodeError, OSError) as exc:
                import sys
                sys.stderr.write(f"WARNING: Failed to parse {cp}: {exc}\n")
                core_data = {
                    "__load_error__": f"{type(exc).__name__}: {exc}",
                    "path": str(cp),
                }
            break
    # @cpt-end:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-load-core

    # @cpt-begin:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-merge
    # -- Resolve variables --
    result = _collect_all_variables(project_root, adapter_dir, core_data)
    if isinstance(core_data, dict) and "__load_error__" in core_data:
        result["core_load_error"] = core_data["__load_error__"]
    # @cpt-end:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-merge

    # @cpt-begin:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-filter-kit
    # -- Filter by kit if requested --
    if args.kit:
        slug = args.kit
        kit_section = result["kits"].get(slug)
        if kit_section is None:
            ui.result({
                "status": "ERROR",
                "message": f"Kit '{slug}' not found or has no resource bindings",
                "available_kits": list(result["kits"].keys()),
            })
            return 1
        # Rebuild flat with only system + this kit (system wins on collision)
        filtered_flat = dict(result["system"])
        for k, v in kit_section.items():
            if k not in filtered_flat:
                filtered_flat[k] = v
        result = {
            "system": result["system"],
            "kits": {slug: kit_section},
            "variables": filtered_flat,
        }
    # @cpt-end:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-filter-kit

    # @cpt-begin:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-return
    # -- Output --
    if args.flat:
        flat_output: Dict[str, Any] = {"variables": result["variables"]}
        if result.get("collisions"):
            flat_output["collisions"] = result["collisions"]
        if result.get("core_load_error"):
            flat_output["core_load_error"] = result["core_load_error"]
        ui.result(flat_output, human_fn=_human_flat)
    else:
        output = {
            "status": "OK",
            **result,
        }
        ui.result(output, human_fn=_human_structured)

    return 0
    # @cpt-end:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-return


# @cpt-begin:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-human-flat
def _human_flat(data: dict) -> None:
    """Human-friendly flat variable listing."""
    ui.header("Resolved Variables")
    variables = data.get("variables", data)
    for name, path in sorted(variables.items()):
        ui.detail(f"{{{name}}}", ui.relpath(path))
    ui.blank()
# @cpt-end:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-human-flat


# @cpt-begin:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-human-structured
def _human_structured(data: dict) -> None:
    """Human-friendly structured variable listing."""
    ui.header("Resolved Variables")

    # System variables
    system = data.get("system", {})
    if system:
        ui.step("System")
        for name, path in sorted(system.items()):
            ui.detail(f"  {{{name}}}", ui.relpath(path))

    # Per-kit variables
    kits = data.get("kits", {})
    if kits:
        ui.blank()
        for slug, kvars in sorted(kits.items()):
            ui.step(f"Kit: {slug} ({len(kvars)} variables)")
            for name, path in sorted(kvars.items()):
                ui.detail(f"  {{{name}}}", ui.relpath(path))

    # Summary
    flat = data.get("variables", {})
    ui.blank()
    ui.info(f"Total: {len(flat)} variables resolved")
    ui.blank()
# @cpt-end:cpt-cypilot-flow-developer-experience-resolve-vars:p1:inst-resolve-vars-human-structured
