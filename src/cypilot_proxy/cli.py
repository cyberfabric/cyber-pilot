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


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for the cypilot/cpt commands.
    """
    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-user-invokes
    args = argv if argv is not None else sys.argv[1:]
    # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-user-invokes

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

    # Extract --version VERSION, --force, --source, --url only for init and update commands
    target_version = None
    force_update = False
    source_dir = None
    custom_url = None
    if args and args[0] in ("init", "update"):
        target_version = _extract_version_param(args)
        source_dir = _extract_named_param(args, "--source")
        custom_url = _extract_named_param(args, "--url")
        if "--force" in args:
            force_update = True
            args.remove("--force")

    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-if-update-cache
    if args and args[0] == "update":
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
        # Use cached skill (freshly updated) to avoid stale code
        skill_path = find_cached_skill()
        if skill_path is None:
            sys.stderr.write("Cache updated but skill entry point not found.\n")
            # @cpt-begin:cpt-cypilot-state-core-infra-project-install:p1:inst-update-complete
            return 1
            # @cpt-end:cpt-cypilot-state-core-infra-project-install:p1:inst-update-complete

        sys.stderr.write("Updating project...\n")
        # Forward only 'update' + any remaining flags (strip version positional arg)
        update_args = ["update"]
        if "--dry-run" in args:
            update_args.append("--dry-run")
        # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-return-cache-update
        return _forward_to_skill(skill_path, update_args)
        # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-return-cache-update
    # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-if-update-cache

    # Re-add --force to args for init (skill needs it for config overwrite)
    if force_update and args and args[0] == "init":
        args.append("--force")

    # For init with --version: update cache first, then forward init to skill
    if target_version is not None:
        from cypilot_proxy.cache import download_and_cache

        sys.stderr.write(f"Updating cache to version {target_version}...\n")
        success, message = download_and_cache(version=target_version, force=force_update)
        sys.stderr.write(f"{message}\n")
        if not success:
            return 1

    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-check-project-skill
    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-if-project-skill
    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-else-no-project
    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-check-cache
    # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-if-cache
    # For init --force / --version: use cached skill to avoid chicken-and-egg
    # (old project skill would run init that copies new code, but old code is in memory)
    use_cache_for_init = (
        args and args[0] == "init"
        and (force_update or target_version is not None)
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

        sys.stderr.write("Cypilot: No skill found. Downloading from GitHub...\n")
        success, message = download_and_cache()
        # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-auto-download
        # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-if-download-failed
        if not success:
            # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-return-download-error
            sys.stderr.write(f"Error: {message}\n")
            sys.stderr.write("Retry: cypilot update\n")
            return 1
            # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-return-download-error
        # @cpt-end:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-if-download-failed

        sys.stderr.write(f"{message}\n")
        # @cpt-begin:cpt-cypilot-flow-core-infra-cli-invocation:p1:inst-forward-fresh-cache
        skill_path = find_cached_skill()
        if skill_path is None:
            sys.stderr.write("Error: Cache populated but skill entry point not found.\n")
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
