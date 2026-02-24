"""
Cypilot Validator - CLI Entry Point

Command-line interface for the Cypilot validation tool.

IMPORTANT: This module MUST NOT contain business logic.

- The CLI is responsible only for argv parsing and command dispatch.
- All validation, scanning, and transformation logic MUST live in dedicated modules under cypilot.utils or command modules.
"""

import sys
import json
from pathlib import Path
from typing import List, Optional


def _cmd_self_check(argv: List[str]) -> int:
    from .commands.self_check import cmd_self_check
    return cmd_self_check(argv)


def _cmd_agents(argv: List[str]) -> int:
    from .commands.agents import cmd_agents
    return cmd_agents(argv)


def _cmd_init(argv: List[str]) -> int:
    from .commands.init import cmd_init
    return cmd_init(argv)


# =============================================================================
def _cmd_validate(argv: List[str]) -> int:
    from .commands.validate import cmd_validate
    return cmd_validate(argv)


# =============================================================================
# SEARCH COMMANDS
# =============================================================================

def _cmd_list_ids(argv: List[str]) -> int:
    from .commands.list_ids import cmd_list_ids
    return cmd_list_ids(argv)


def _cmd_list_id_kinds(argv: List[str]) -> int:
    from .commands.list_id_kinds import cmd_list_id_kinds
    return cmd_list_id_kinds(argv)


def _cmd_get_content(argv: List[str]) -> int:
    from .commands.get_content import cmd_get_content
    return cmd_get_content(argv)


def _cmd_where_defined(argv: List[str]) -> int:
    from .commands.where_defined import cmd_where_defined
    return cmd_where_defined(argv)


def _cmd_where_used(argv: List[str]) -> int:
    from .commands.where_used import cmd_where_used
    return cmd_where_used(argv)


# =============================================================================
# KIT VALIDATION COMMAND
# =============================================================================

def _cmd_validate_kits(argv: List[str]) -> int:
    from .commands.validate_kits import cmd_validate_kits
    return cmd_validate_kits(argv)


# =============================================================================
# KIT MANAGEMENT COMMANDS
# =============================================================================

def _cmd_kit(argv: List[str]) -> int:
    from .commands.kit import cmd_kit
    return cmd_kit(argv)


def _cmd_generate_resources(argv: List[str]) -> int:
    from .commands.kit import cmd_generate_resources
    return cmd_generate_resources(argv)


# =============================================================================
# ADAPTER COMMAND
# =============================================================================

def _cmd_cypilot_info(argv: List[str]) -> int:
    from .commands.adapter_info import cmd_adapter_info
    return cmd_adapter_info(argv)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main(argv: Optional[List[str]] = None) -> int:
    argv_list = list(argv) if argv is not None else sys.argv[1:]

    # Load global Cypilot context on startup (templates, systems, etc.)
    # Always reload context based on current working directory (no caching)
    from .utils.context import CypilotContext, set_context
    ctx = CypilotContext.load()
    set_context(ctx)
    # Context may be None if no adapter found - that's OK for some commands like init

    # Define all available commands
    analysis_commands = ["validate", "validate-kits"]
    legacy_aliases = ["validate-code", "validate-rules"]
    kit_commands = ["kit", "generate-resources"]
    search_commands = [
        "init",
        "list-ids", "list-id-kinds",
        "get-content",
        "where-defined", "where-used",
        "info", "adapter-info",
        "self-check",
        "agents",
    ]
    all_commands = analysis_commands + kit_commands + search_commands + legacy_aliases

    # Handle --help / -h at top level
    if argv_list and argv_list[0] in ("-h", "--help"):
        print("usage: cypilot <command> [options]")
        print()
        print("Cypilot CLI - artifact validation and traceability tool")
        print()
        print("Validation commands:")
        for c in analysis_commands:
            print(f"  {c}")
        print()
        print("Kit management commands:")
        for c in kit_commands:
            print(f"  {c}")
        print()
        print("Search and utility commands:")
        for c in search_commands:
            print(f"  {c}")
        print()
        print("Legacy aliases:")
        print("  validate-code → validate")
        print("  validate-rules → validate-kits")
        print()
        print("Run 'cypilot <command> --help' for command-specific options.")
        return 0

    if not argv_list:
        print(json.dumps({
            "status": "ERROR",
            "message": "Missing subcommand",
            "analysis_commands": analysis_commands,
            "search_commands": search_commands,
        }, indent=None, ensure_ascii=False))
        return 1

    # @cpt-begin:cpt-cypilot-algo-core-infra-route-command:p1:inst-parse-command
    # Backward compatibility: if first arg starts with --, assume validate command
    if argv_list[0].startswith("-"):
        cmd = "validate"
        rest = argv_list
    else:
        cmd = argv_list[0]
        rest = argv_list[1:]
    # @cpt-end:cpt-cypilot-algo-core-infra-route-command:p1:inst-parse-command

    # @cpt-dod:cpt-cypilot-dod-core-infra-agents-integrity:p1
    # @cpt-begin:cpt-cypilot-algo-core-infra-route-command:p1:inst-verify-agents
    # Verify root AGENTS.md integrity on every invocation (silent re-inject if stale)
    if ctx is not None and cmd != "init":
        try:
            from .commands.init import _inject_root_agents
            from .utils.files import find_project_root, _read_cypilot_var
            project_root = find_project_root(Path.cwd())
            if project_root is not None:
                install_rel = _read_cypilot_var(project_root)
                if install_rel:
                    _inject_root_agents(project_root, install_rel)
        except Exception:
            pass  # Non-fatal: don't block command execution
    # @cpt-end:cpt-cypilot-algo-core-infra-route-command:p1:inst-verify-agents

    # @cpt-begin:cpt-cypilot-algo-core-infra-route-command:p1:inst-lookup-handler
    # @cpt-begin:cpt-cypilot-algo-core-infra-route-command:p1:inst-parse-args
    # @cpt-begin:cpt-cypilot-algo-core-infra-route-command:p1:inst-execute-handler
    # @cpt-begin:cpt-cypilot-algo-core-infra-route-command:p1:inst-serialize-json
    # @cpt-begin:cpt-cypilot-algo-core-infra-route-command:p1:inst-return-code
    # Dispatch to appropriate command handler
    if cmd == "validate":
        return _cmd_validate(rest)
    elif cmd == "validate-code":
        # Legacy alias: keep for compatibility.
        return _cmd_validate(rest)
    elif cmd in ("validate-kits", "validate-rules"):
        return _cmd_validate_kits(rest)
    elif cmd == "init":
        return _cmd_init(rest)
    elif cmd == "list-ids":
        return _cmd_list_ids(rest)
    elif cmd == "list-id-kinds":
        return _cmd_list_id_kinds(rest)
    elif cmd == "get-content":
        return _cmd_get_content(rest)
    elif cmd == "where-defined":
        return _cmd_where_defined(rest)
    elif cmd == "where-used":
        return _cmd_where_used(rest)
    elif cmd in ("info", "adapter-info"):
        return _cmd_cypilot_info(rest)
    elif cmd == "self-check":
        return _cmd_self_check(rest)
    elif cmd == "agents":
        return _cmd_agents(rest)
    elif cmd == "kit":
        return _cmd_kit(rest)
    elif cmd == "generate-resources":
        return _cmd_generate_resources(rest)
    else:
        # @cpt-begin:cpt-cypilot-algo-core-infra-route-command:p1:inst-if-no-handler
        # @cpt-begin:cpt-cypilot-algo-core-infra-route-command:p1:inst-return-unknown
        print(json.dumps({
            "status": "ERROR",
            "message": f"Unknown command: {cmd}",
            "available": all_commands,
        }, indent=None, ensure_ascii=False))
        return 1
        # @cpt-end:cpt-cypilot-algo-core-infra-route-command:p1:inst-return-unknown
        # @cpt-end:cpt-cypilot-algo-core-infra-route-command:p1:inst-if-no-handler
    # @cpt-end:cpt-cypilot-algo-core-infra-route-command:p1:inst-return-code
    # @cpt-end:cpt-cypilot-algo-core-infra-route-command:p1:inst-serialize-json
    # @cpt-end:cpt-cypilot-algo-core-infra-route-command:p1:inst-execute-handler
    # @cpt-end:cpt-cypilot-algo-core-infra-route-command:p1:inst-parse-args
    # @cpt-end:cpt-cypilot-algo-core-infra-route-command:p1:inst-lookup-handler


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["main"]
