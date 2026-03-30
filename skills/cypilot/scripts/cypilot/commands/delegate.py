"""
Delegate Command — ralphex delegation from a Cypilot plan.

Compiles a Cypilot plan into ralphex-compatible format, resolves the
ralphex executable, and orchestrates the delegation flow. Respects
the bootstrap gate: missing ``.ralphex/config`` is a blocking error
(exit code 2) with opt-in guidance.

@cpt-flow:cpt-cypilot-flow-ralphex-delegation-execute:p1
@cpt-dod:cpt-cypilot-dod-ralphex-delegation-modes:p1
"""

import argparse
import logging
from pathlib import Path
from typing import List

from ..utils.ui import ui, is_json_mode, set_json_mode

logger = logging.getLogger(__name__)


# @cpt-begin:cpt-cypilot-flow-ralphex-delegation-execute:p1:inst-invoke-execute
def cmd_delegate(argv: List[str]) -> int:
    """Run ralphex delegation from a Cypilot plan."""
    json_was_enabled = is_json_mode()

    p = argparse.ArgumentParser(
        prog="delegate",
        description="Compile a Cypilot plan and delegate to ralphex",
    )
    p.add_argument(
        "plan_dir",
        help="Path to the Cypilot plan directory containing plan.toml",
    )
    p.add_argument(
        "--mode",
        choices=["execute", "tasks-only", "review"],
        default="execute",
        help="Delegation mode (default: execute)",
    )
    p.add_argument(
        "--worktree",
        action="store_true",
        help="Request worktree isolation (execute and tasks-only only)",
    )
    serve_group = p.add_mutually_exclusive_group()
    serve_group.add_argument(
        "--serve",
        dest="serve",
        action="store_true",
        help="Request dashboard serving (default)",
    )
    serve_group.add_argument(
        "--no-serve",
        dest="serve",
        action="store_false",
        help="Disable dashboard serving",
    )
    p.set_defaults(serve=True)
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Assemble the command without invoking ralphex",
    )
    p.add_argument(
        "--default-branch",
        default="main",
        help="Default branch for review precondition (default: main)",
    )
    p.add_argument(
        "--plans-dir",
        default=None,
        help="Override plans directory (highest precedence)",
    )
    p.add_argument(
        "--root",
        default=".",
        help="Project root (default: current directory)",
    )
    try:
        args = p.parse_args(argv)

        project_root = Path(args.root).resolve()

        if not project_root.is_dir():
            ui.result(
                {"status": "error", "error": f"Project root not found or not a directory: {project_root}"},
                human_fn=lambda d: ui.error(d["error"]),
            )
            return 1

        plan_path_arg = Path(args.plan_dir)
        if plan_path_arg.is_absolute():
            plan_dir = plan_path_arg.resolve()
        else:
            plan_dir = (project_root / plan_path_arg).resolve()

        if not plan_dir.is_dir():
            ui.result(
                {"status": "error", "error": f"Plan directory not found: {plan_dir}"},
                human_fn=lambda d: ui.error(d["error"]),
            )
            return 1

        plan_toml = plan_dir / "plan.toml"
        if not plan_toml.is_file():
            ui.result(
                {"status": "error", "error": f"plan.toml not found in {plan_dir}"},
                human_fn=lambda d: ui.error(d["error"]),
            )
            return 1

        from ._core_config import find_core_toml, load_core_config
        config = load_core_config(project_root)
        config_path = find_core_toml(project_root)

        from ..ralphex_export import run_delegation

        if json_was_enabled:
            set_json_mode(False)
        result = run_delegation(
            config=config,
            plan_dir=str(plan_dir),
            repo_root=str(project_root),
            mode=args.mode,
            worktree=args.worktree,
            serve=args.serve,
            default_branch=args.default_branch,
            config_path=config_path,
            dry_run=args.dry_run,
            plans_dir_override=args.plans_dir,
            stream_output=not json_was_enabled,
        )

        if json_was_enabled:
            set_json_mode(True)

        bootstrap = result.get("bootstrap")
        if bootstrap and bootstrap.get("needed"):
            ui.step("[WARN] " + bootstrap["message"])

        exit_code = _result_to_exit_code(result)

        ui.result(
            result,
            human_fn=_print_human,
        )

        return exit_code
    finally:
        if json_was_enabled:
            set_json_mode(True)
# @cpt-end:cpt-cypilot-flow-ralphex-delegation-execute:p1:inst-invoke-execute


# @cpt-begin:cpt-cypilot-dod-ralphex-delegation-modes:p1:inst-determine-mode
def _result_to_exit_code(result: dict) -> int:
    """Map delegation result status to CLI exit code."""
    status = result.get("status", "error")
    if status in ("ready", "delegated"):
        return 0
    # error status
    return 2


def _print_human(result: dict) -> None:
    """Print human-readable delegation result."""
    status = result.get("status", "error")
    dashboard_url = result.get("dashboard_url")

    if status == "error":
        ui.error(f"Delegation failed: {result.get('error', 'unknown error')}")
        return

    if status == "ready":
        ui.step("[DRY RUN] Command assembled (not invoked):")
        command = result.get("command", [])
        if command:
            ui.info(f"  {' '.join(command)}")
        plan_file = result.get("plan_file")
        if plan_file:
            ui.info(f"  Exported plan: {plan_file}")
        if dashboard_url:
            ui.info(f"  Dashboard: {dashboard_url}")
        ui.info(f"  Lifecycle: {result.get('lifecycle_state', 'unknown')}")
        return

    if status == "delegated":
        lifecycle = result.get("lifecycle_state", "unknown")
        header = "Delegation completed:" if lifecycle == "completed" else "Delegation started:"
        ui.step(header)
        command = result.get("command", [])
        if command:
            ui.info(f"  {' '.join(command)}")
        ui.info(f"  Mode: {result.get('mode', 'unknown')}")
        if dashboard_url:
            ui.info(f"  Dashboard: {dashboard_url}")
        ui.info(f"  Lifecycle: {result.get('lifecycle_state', 'unknown')}")
# @cpt-end:cpt-cypilot-dod-ralphex-delegation-modes:p1:inst-determine-mode
