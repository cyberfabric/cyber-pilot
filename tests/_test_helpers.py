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
