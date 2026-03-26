"""Shared test helpers for Cypilot tests."""
from __future__ import annotations

import io
import json
import os
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Dict, List, Tuple


def write_constraints_toml(path: Path, data: Dict[str, Any]) -> None:
    """Write a constraints dict (artifact-kind-keyed) as constraints.toml.

    *path* is the kit root directory (constraints.toml is created inside it).
    *data* maps artifact kinds to their constraint dicts, e.g.
    ``{"PRD": {"identifiers": {"fr": {"required": True}}}}``.
    """
    from cypilot.utils.toml_utils import dumps
    (path / "constraints.toml").write_text(
        dumps({"artifacts": data}), encoding="utf-8",
    )


def make_test_cache(cache_dir: Path) -> None:
    """Create a minimal cache scaffold for init tests."""
    for d in ("architecture", "requirements", "schemas", "workflows", "skills"):
        (cache_dir / d).mkdir(parents=True, exist_ok=True)
        (cache_dir / d / "README.md").write_text(f"# {d}\n", encoding="utf-8")
    bp_dir = cache_dir / "kits" / "sdlc" / "blueprints"
    bp_dir.mkdir(parents=True, exist_ok=True)
    (bp_dir / "prd.md").write_text(
        "<!-- @cpt:blueprint -->\n```toml\n"
        'artifact = "PRD"\nkit = "sdlc"\nversion = 1\n'
        "```\n<!-- /@cpt:blueprint -->\n\n"
        "<!-- @cpt:heading -->\n# Product Requirements\n<!-- /@cpt:heading -->\n",
        encoding="utf-8",
    )
    from cypilot.utils import toml_utils
    toml_utils.dump({"version": 1, "blueprints": {"prd": 1}}, cache_dir / "kits" / "sdlc" / "conf.toml")


def bootstrap_test_project(
    root: Path,
    adapter_rel: str = "cypilot",
    *,
    systems: List[Dict[str, str]] | None = None,
) -> Path:
    from cypilot.utils import toml_utils

    root.mkdir(parents=True, exist_ok=True)
    (root / ".git").mkdir(exist_ok=True)
    (root / "AGENTS.md").write_text(
        f'<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "{adapter_rel}"\n```\n<!-- /@cpt:root-agents -->\n',
        encoding="utf-8",
    )
    adapter = root / adapter_rel
    config = adapter / "config"
    gen = adapter / ".gen"
    for d in (adapter, config, gen, adapter / ".core"):
        d.mkdir(parents=True, exist_ok=True)
    (config / "AGENTS.md").write_text("# Test\n", encoding="utf-8")
    toml_utils.dump({
        "version": "1.0",
        "project_root": "..",
        "kits": {},
    }, config / "core.toml")
    if systems is not None:
        toml_utils.dump({"systems": systems}, config / "artifacts.toml")
    return adapter


def write_registered_sdlc_config(
    config_dir: Path,
    *,
    resources: Dict[str, Any] | None = None,
    core_kit_path: str = "config/kits/sdlc",
    artifacts_kit_path: str = "config/kits/sdlc",
    version: str = "2.0",
) -> None:
    from cypilot.utils import toml_utils

    config_dir.mkdir(parents=True, exist_ok=True)
    core_kit: Dict[str, Any] = {
        "format": "Cypilot",
        "path": core_kit_path,
        "version": version,
    }
    if resources is not None:
        core_kit["resources"] = resources
    toml_utils.dump({
        "version": "1.0",
        "project_root": "..",
        "kits": {"sdlc": core_kit},
    }, config_dir / "core.toml")
    toml_utils.dump({
        "version": "1.0",
        "project_root": "..",
        "kits": {
            "sdlc": {"format": "Cypilot", "path": artifacts_kit_path},
        },
        "systems": [{"name": "Test", "slug": "test", "kit": "sdlc"}],
    }, config_dir / "artifacts.toml")



def run_cli_in_project(root: Path, args: List[str]) -> Tuple[int, dict]:
    """Run CLI main() in *root*, return (exit_code, parsed_json_output)."""
    from cypilot.cli import main
    from cypilot.utils.ui import is_json_mode, set_json_mode

    cwd = os.getcwd()
    saved_json_mode = is_json_mode()
    try:
        os.chdir(str(root))
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(args)
        out = json.loads(stdout.getvalue())
        return exit_code, out
    finally:
        set_json_mode(saved_json_mode)
        os.chdir(cwd)
