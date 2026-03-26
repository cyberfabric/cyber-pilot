"""
Resolve Variables Command — resolve template variables to absolute paths.

Reads kit resource bindings from ``core.toml`` and resolves all template
variables (``{adr_template}``, ``{scripts}``, ``{cypilot_path}``, etc.)
to absolute file paths.  Output is a flat dict suitable for
``str.format_map()`` substitution in Markdown files.

@cpt-flow:cpt-cypilot-flow-developer-experience-resolve-vars:p1
@cpt-dod:cpt-cypilot-dod-developer-experience-resolve-vars:p1
@cpt-algo:cpt-cypilot-algo-project-extensibility-resolve-layer-variables:p1
@cpt-algo:cpt-cypilot-algo-project-extensibility-deterministic-assembly:p1
"""

import argparse
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..utils.files import (
    find_cypilot_directory,
    find_project_root,
)
from ..utils.manifest import ComponentEntry, ManifestLayer, ManifestLayerState, apply_section_appends
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


# ---------------------------------------------------------------------------
# Layer Variables Assembly
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-layer-variables:p1:inst-step1-start
def add_layer_variables(
    variables: Dict[str, str],
    layers: List[ManifestLayer],
    repo_root: Path,
) -> Dict[str, str]:
    """Extend *variables* with layer path variables derived from walk-up discovery.

    Layer variables:
    - ``base_dir``: outermost discovered layer root (master repo if found, else repo root)
    - ``master_repo``: master repo root path (empty string if no master repo)
    - ``repo``: current repo root path

    Layer variables do NOT override existing system/kit variables.

    Args:
        variables:  Existing flat variable dict from ``_collect_all_variables()``.
        layers:     Discovered ``ManifestLayer`` list (resolution order).
        repo_root:  Absolute path to the current repo root.

    Returns:
        New dict with layer path variables merged in (first-writer-wins).
    """
    # @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-layer-variables:p1:inst-step2-extract-paths
    # Derive master_repo and base_dir from the layer list.
    # A "master" scope layer carries the master repo root (its path is the
    # manifest file, so its parent is the master repo root directory).
    master_repo_path: str = ""
    for layer in layers:
        if layer.scope == "master" and layer.state == ManifestLayerState.LOADED:
            # layer.path is the manifest file; parent is the master repo root
            master_repo_path = layer.path.parent.as_posix()
            break
    # @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-layer-variables:p1:inst-step2-extract-paths

    # @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-layer-variables:p1:inst-step3-resolve-paths
    repo_path = repo_root.resolve().as_posix()
    # base_dir is the outermost layer: master repo if present, else repo root
    base_dir_path = master_repo_path if master_repo_path else repo_path
    # @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-layer-variables:p1:inst-step3-resolve-paths

    # @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-layer-variables:p1:inst-step4-merge
    # Build layer vars — use first-writer-wins: do NOT override existing vars
    layer_vars: Dict[str, str] = {
        "base_dir": base_dir_path,
        "master_repo": master_repo_path,
        "repo": repo_path,
    }
    result: Dict[str, str] = dict(variables)
    for key, val in layer_vars.items():
        if key not in result:
            result[key] = val
    # @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-layer-variables:p1:inst-step4-merge

    # @cpt-begin:cpt-cypilot-algo-project-extensibility-resolve-layer-variables:p1:inst-step5-return
    return result
    # @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-layer-variables:p1:inst-step5-return
# @cpt-end:cpt-cypilot-algo-project-extensibility-resolve-layer-variables:p1:inst-step1-start


def _apply_safe_vars(text: str, variables: dict) -> str:
    """Replace {key} placeholders without consuming literal {{ or }}.

    Unlike ``str.format_map()``, this only replaces known variable keys and
    leaves double-braces (used in JSON / template content) untouched.
    """
    if not variables:
        return text

    keys = [k for k in variables if k]
    if not keys:
        return text

    def _repl(m: re.Match) -> str:
        key = m.group(1)
        return variables.get(key, m.group(0))

    pattern = r"\{(" + "|".join(re.escape(k) for k in keys) + r")\}"
    return re.sub(pattern, _repl, text)


# @cpt-begin:cpt-cypilot-algo-project-extensibility-deterministic-assembly:p1:inst-step1-foreach
def assemble_component(
    component_id: str,
    source_content: str,
    layers: List[ComponentEntry],
    variables: Dict[str, str],
    _target: str,
    component_type: Optional[str] = None,
) -> str:
    """Deterministically assemble a component from merged data.

    Steps:
    1. Apply section appends from the pre-merged components list.
    2. Substitute ``{variable}`` references using ``str.format_map()``.

    The result is a pure function of inputs — no I/O, no timestamps,
    no randomness.

    Args:
        component_id:   ID of the component to assemble.
        source_content: Base source content (e.g. prompt file body).
        layers:         Already-merged ``ComponentEntry`` instances (from
                        ``MergedComponents``).  Each entry's ``.append`` field
                        contains accumulated layer appends.
        variables:      Flat variable dict for ``{var}`` substitution.
        target:         Target agent identifier (reserved for future filtering).
        component_type: Optional type hint (e.g. ``"agents"``, ``"skills"``) passed
                        to ``apply_section_appends()`` to avoid cross-type ID collisions.

    Returns:
        Assembled content string with appends applied and variables substituted.
    """
    # @cpt-begin:cpt-cypilot-algo-project-extensibility-deterministic-assembly:p1:inst-step1.1-load-source
    # Step 1.1: Start with source content
    composed = source_content
    # @cpt-end:cpt-cypilot-algo-project-extensibility-deterministic-assembly:p1:inst-step1.1-load-source

    # @cpt-begin:cpt-cypilot-algo-project-extensibility-deterministic-assembly:p1:inst-step1.2-apply-appends
    # Step 1.2: Apply section appends from pre-merged components
    composed = apply_section_appends(composed, layers, component_id, component_type=component_type)
    # @cpt-end:cpt-cypilot-algo-project-extensibility-deterministic-assembly:p1:inst-step1.2-apply-appends

    # @cpt-begin:cpt-cypilot-algo-project-extensibility-deterministic-assembly:p1:inst-step1.4-substitute
    # Step 1.4: Substitute {variable} references — use a regex-based replacer
    # that only touches known keys, leaving unknown keys and literal {{ / }}
    # (e.g. JSON or template content) intact.
    composed = _apply_safe_vars(composed, variables)
    # @cpt-end:cpt-cypilot-algo-project-extensibility-deterministic-assembly:p1:inst-step1.4-substitute

    # @cpt-begin:cpt-cypilot-algo-project-extensibility-deterministic-assembly:p1:inst-step1.6-return
    # Step 1.6: Return assembled content — caller handles I/O
    return composed
    # @cpt-end:cpt-cypilot-algo-project-extensibility-deterministic-assembly:p1:inst-step1.6-return
# @cpt-end:cpt-cypilot-algo-project-extensibility-deterministic-assembly:p1:inst-step1-foreach


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

    # -- Enrich with layer variables (base_dir, master_repo, repo) --
    try:
        from ..utils.layer_discovery import discover_layers
        layers = discover_layers(project_root, adapter_dir)
        result["variables"] = add_layer_variables(
            result["variables"], layers, project_root,
        )
    except (ValueError, OSError) as exc:
        import sys
        sys.stderr.write(f"WARNING: layer discovery failed: {exc}\n")
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
        # Rebuild flat with only system + this kit + layer vars (system wins on collision)
        filtered_flat = dict(result["system"])
        for k, v in kit_section.items():
            if k not in filtered_flat:
                filtered_flat[k] = v
        # Preserve layer variables (base_dir, master_repo, repo) from enriched set —
        # these are in result["variables"] but not in system or any kit's resources.
        all_kit_var_names = {k for kvars in result["kits"].values() for k in kvars}
        for k, v in result["variables"].items():
            if k not in filtered_flat and k not in all_kit_var_names:
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
