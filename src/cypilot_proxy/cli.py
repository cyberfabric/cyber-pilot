"""
Cypilot Global CLI Proxy — Main Entry Point

Thin proxy that resolves skill target (project or cache) and forwards commands.
All actual logic lives in the skill engine — this proxy only routes.

@cpt-flow:cpt-cypilot-flow-core-infra-cli-invocation:p1
@cpt-algo:cpt-cypilot-algo-core-infra-route-command:p1
@cpt-dod:cpt-cypilot-dod-core-infra-cli-routes:p1
@cpt-dod:cpt-cypilot-dod-core-infra-global-package:p1
@cpt-state:cpt-cypilot-state-core-infra-project-install:p1
"""

# @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-cli-proxy-helpers
import json
import subprocess
import sys
from pathlib import Path
from typing import List, NoReturn, Optional

from cypilot_proxy.resolve import (
    find_cached_skill,
    find_project_skill,
    get_cached_version,
    get_project_version,
    resolve_skill,
)

def _extract_version_param(args: List[str]) -> Optional[str]:
    """
    Extract and remove --version VERSION from args list.

    Supports: --version VALUE, --version=VALUE
    Mutates args in place, returns the version string or None.
    """
    return _extract_named_param(args, "--version")

def _extract_named_param(args: List[str], name: str) -> Optional[str]:
    """
    Extract and remove a named parameter from args list.

    Supports: NAME VALUE, NAME=VALUE
    Mutates args in place, returns the value string or None.
    """
    i = 0
    while i < len(args):
        if args[i] == name and i + 1 < len(args):
            value = args[i + 1]
            del args[i:i + 2]
            return value
        if args[i].startswith(f"{name}="):
            value = args[i].split("=", 1)[1]
            del args[i]
            return value
        i += 1
    return None
# @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-cli-proxy-helpers

def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for the cpt command.
    """
    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-user-invokes
    args = argv if argv is not None else sys.argv[1:]
    # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-user-invokes

    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-cli-proxy-helpers
    # Handle --version with no value: show version info
    if args and args[0] == "--version" and len(args) == 1:
        from cypilot_proxy import __version__
        print(f"cypilot-proxy {__version__}")
        cached = get_cached_version()
        if cached:
            print(f"skill (cached): {cached}")
        project_skill = find_project_skill()
        if project_skill:
            pv = get_project_version(project_skill)
            if pv:
                print(f"skill (project): {pv}")
        return 0

    # Extract --version VERSION, --force, --source, --url, --no-cache only for init and update commands
    target_version = None
    force_update = False
    skip_cache = False
    source_dir = None
    custom_url = None
    if args and args[0] in ("init", "update"):
        target_version = _extract_version_param(args)
        source_dir = _extract_named_param(args, "--source")
        custom_url = _extract_named_param(args, "--url")
        if "--force" in args:
            force_update = True
            args.remove("--force")
        if "--no-cache" in args:
            skip_cache = True
            args.remove("--no-cache")
    # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-cli-proxy-helpers

    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-if-update-cache
    if args and args[0] == "update":
        if not skip_cache and "--help" not in args and "-h" not in args:
            # Step 1: Update cache
            if source_dir is not None:
                from cypilot_proxy.cache import copy_from_local

                success, message = copy_from_local(source_dir=source_dir, force=force_update)
            else:
                from cypilot_proxy.cache import download_and_cache

                # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-explicit-cache-update
                explicit = target_version or (args[1] if len(args) > 1 else None)
                success, message = download_and_cache(version=explicit, force=force_update, url=custom_url)
                # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-explicit-cache-update

            sys.stderr.write(f"{message}\n")
            if not success:
                return 1

        # Step 2: Forward to skill engine for .core/ + kits + .gen/ update
        skill_path = find_cached_skill()
        if skill_path is None:
            sys.stderr.write("Cache not found. Run 'cpt update' without --no-cache first.\n")
            # @cpt-begin:cpt-cypilot-state-core-infra-project-install:p1:inst-update-complete
            return 1
            # @cpt-end:cpt-cypilot-state-core-infra-project-install:p1:inst-update-complete

        sys.stderr.write("Updating project...\n")
        # Forward only 'update' + any remaining flags (strip version positional arg)
        update_args = ["update"]
        for flag in ("--dry-run", "--help", "-h", "--no-interactive", "-y", "--yes"):
            if flag in args:
                update_args.append(flag)
        # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-return-cache-update
        return _forward_to_skill(skill_path, update_args)
        # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-return-cache-update
    # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-if-update-cache

    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-cli-proxy-helpers
    # Re-add --force to args for init (skill needs it for config overwrite)
    if force_update and args and args[0] == "init":
        args.append("--force")

    # For init: always update cache first, then forward to cached skill
    if args and args[0] == "init" and not skip_cache and "--help" not in args and "-h" not in args:
        if source_dir is not None:
            from cypilot_proxy.cache import copy_from_local

            sys.stderr.write("Updating cache from local source...\n")
            success, message = copy_from_local(source_dir=source_dir, force=force_update)
        else:
            from cypilot_proxy.cache import download_and_cache

            if target_version:
                sys.stderr.write(f"Updating cache to version {target_version}...\n")
            else:
                sys.stderr.write("Updating cache to latest version...\n")
            success, message = download_and_cache(version=target_version, force=force_update, url=custom_url)
        sys.stderr.write(f"{message}\n")
        if not success:
            return 1
    # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-cli-proxy-helpers

    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-check-project-skill
    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-if-project-skill
    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-else-no-project
    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-check-cache
    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-if-cache
    # For init: always use cached skill (we just updated cache above)
    use_cache_for_init = (
        args and args[0] == "init"
        and not skip_cache
        and "--help" not in args and "-h" not in args
    )
    if use_cache_for_init:
        skill_path = find_cached_skill()
        source = "cache" if skill_path else "none"
    else:
        skill_path, source = resolve_skill()
    # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-if-cache
    # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-check-cache
    # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-else-no-project
    # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-if-project-skill
    # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-check-project-skill

    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-else-no-cache
    if skill_path is None:
        # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-auto-download
        from cypilot_proxy.cache import download_and_cache

        sys.stderr.write("\n")
        sys.stderr.write("  Cypilot skill engine not found.\n")
        sys.stderr.write("\n")
        sys.stderr.write("  Cypilot is a two-part tool:\n")
        sys.stderr.write("    • This CLI proxy (already installed)\n")
        sys.stderr.write("    • The skill engine (templates, validators, generators)\n")
        sys.stderr.write("\n")
        sys.stderr.write("  The skill engine needs to be downloaded once from GitHub\n")
        sys.stderr.write("  and cached at ~/.cypilot/cache/.\n")
        sys.stderr.write("\n")

        if sys.stdin.isatty():
            try:
                answer = input("  Download now? [Y/n] ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                answer = "n"
            if answer and answer not in ("y", "yes"):
                sys.stderr.write("\n  To download later, run: cpt update\n\n")
                return 1
        else:
            sys.stderr.write("  Downloading automatically (non-interactive mode)...\n")

        sys.stderr.write("\n")
        success, message = download_and_cache()
        # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-auto-download
        # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-if-download-failed
        if not success:
            # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-return-download-error
            sys.stderr.write(f"  Error: {message}\n")
            sys.stderr.write("  Retry: cpt update\n\n")
            return 1
            # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-return-download-error
        # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-if-download-failed

        sys.stderr.write(f"  {message}\n\n")
        # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-forward-fresh-cache
        skill_path = find_cached_skill()
        if skill_path is None:
            sys.stderr.write("  Error: Cache populated but skill entry point not found.\n")
            return 1
        source = "cache"
        # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-forward-fresh-cache
    # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-else-no-cache

    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-engine-execute
    result = _forward_to_skill(skill_path, args)
    # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-engine-execute

    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-bg-version-check
    if source == "project":
        _background_version_check(skill_path)
    # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-bg-version-check

    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-return-exit
    return result
    # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-return-exit

# @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-cli-proxy-helpers
def _forward_to_skill(skill_path: Path, args: List[str]) -> int:
    """
    Forward command to the resolved skill engine via subprocess.

    Uses the same Python interpreter that's running this proxy.
    """
    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-forward-project
    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-forward-cache
    cmd = [sys.executable, str(skill_path)] + args

    try:
        proc = subprocess.run(
            cmd,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        return proc.returncode
    except FileNotFoundError:
        sys.stderr.write(f"Error: Skill entry point not found: {skill_path}\n")
        return 1
    except OSError as e:
        sys.stderr.write(f"Error: Failed to execute skill: {e}\n")
        return 1
    # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-forward-cache
    # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-forward-project

def _background_version_check(project_skill_path: Path) -> None:
    """
    Non-blocking background version check.

    Compares cached version with project version and prints
    update notice to stderr if cached is newer.

    """
    try:
        cached_version = get_cached_version()
        if cached_version is None:
            return

        project_version = get_project_version(project_skill_path)
        if project_version is None:
            return

        # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-if-version-mismatch
        # @cpt-begin:cpt-cypilot-state-core-infra-project-install:p1:inst-version-mismatch
        if cached_version != project_version:
            # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-show-update-notice
            sys.stderr.write(
                f"cypilot: update available ({project_version} → {cached_version}). "
                f"Run: cypilot update\n"
            )
            # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-show-update-notice
        # @cpt-end:cpt-cypilot-state-core-infra-project-install:p1:inst-version-mismatch
        # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-if-version-mismatch
    except Exception:
        pass  # Never fail the actual command for a version check
# @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-cli-proxy-helpers
