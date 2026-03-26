# @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-init-helpers
import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.artifacts_meta import create_backup, generate_default_registry, generate_slug
from ..utils import toml_utils
from ..utils.ui import ui

# Directories to copy from cache into project cypilot/.core/ dir
# Full directories (copied entirely)
COPY_DIRS = ["requirements", "schemas", "workflows", "skills"]
# Selective items from architecture/ (only specs needed by agents)
COPY_ARCHITECTURE_ITEMS = [
    "specs/traceability.md",   # ID formats, code traceability — used by kit rules
    "specs/CDSL.md",           # Behavioral spec language — referenced by traceability.md
    "specs/cli.md",            # CLI commands — referenced by traceability.md, kit/rules.md
    "specs/CLISPEC.md",        # CLI spec (detailed command definitions)
    "specs/artifacts-registry.md",  # Artifacts config — used by .gen/AGENTS.md
    "specs/kit/constraints.md",     # Constraints spec — used by ADR, PRD, DESIGN rules
    "specs/kit/kit.md",             # Kit structure — referenced by kit/rules.md
]
COPY_ROOT_DIRS: list[str] = []
CACHE_DIR = Path.home() / ".cypilot" / "cache"
CORE_SUBDIR = ".core"
GEN_SUBDIR = ".gen"
DEFAULT_INSTALL_DIR = "cypilot"

def _copy_from_cache(cache_dir: Path, target_dir: Path, force: bool = False) -> Dict[str, str]:
    """Copy tool directories from cache into project cypilot/.core/ dir.

    Core directories go into .core/ (read-only reference content).
    User-editable content lives in config/.

    When force=True, .core/ is fully cleared before copying to ensure no stale
    files remain from previous versions. This is the mode used by `cpt update`.

    Returns dict of {dir_name: action} where action is 'created', 'updated', or 'skipped'.
    """
    core_dir = target_dir / CORE_SUBDIR
    results: Dict[str, str] = {}

    # Snapshot which directories existed before rmtree so force re-copies
    # are reported as "updated" rather than "created".
    pre_force_existed: set = set()
    if force:
        for name in COPY_DIRS:
            if (core_dir / name).exists():
                pre_force_existed.add(name)
        for name in COPY_ROOT_DIRS:
            if (target_dir / name).exists():
                pre_force_existed.add(name)

    # Full cleanup of .core/ when force=True (ensures no stale files)
    # This is the mode used by `cpt update` which always passes force=True
    if force and core_dir.exists():
        shutil.rmtree(core_dir)

    core_dir.mkdir(parents=True, exist_ok=True)

    def _copy_dir(src: Path, dst: Path, name: str) -> None:
        """Copy a directory."""
        if not src.is_dir():
            results[name] = "missing_in_cache"
            return
        if dst.exists():
            if not force:
                results[name] = "skipped"
                return
            shutil.rmtree(dst)
            results[name] = "updated"
        else:
            results[name] = "updated" if force and name in pre_force_existed else "created"
        shutil.copytree(src, dst)

    def _copy_file(src: Path, dst: Path, name: str) -> None:
        """Copy a single file."""
        if not src.is_file():
            results[name] = "missing_in_cache"
            return
        if dst.exists():
            if not force:
                results[name] = "skipped"
                return
            results[name] = "updated"
        else:
            results[name] = "updated" if force and name in pre_force_existed else "created"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    # Copy full directories
    for name in COPY_DIRS:
        _copy_dir(cache_dir / name, core_dir / name, name)

    # Copy selective items from architecture/
    arch_src = cache_dir / "architecture"
    arch_dst = core_dir / "architecture"
    for item in COPY_ARCHITECTURE_ITEMS:
        src = arch_src / item
        dst = arch_dst / item
        if src.is_dir():
            _copy_dir(src, dst, f"architecture/{item}")
        elif src.is_file():
            _copy_file(src, dst, f"architecture/{item}")
        else:
            results[f"architecture/{item}"] = "missing_in_cache"

    for name in COPY_ROOT_DIRS:
        _copy_dir(cache_dir / name, target_dir / name, name)

    return results

def _core_readme() -> str:
    """README.md content for .core/ directory."""
    return (
        "# .core — Cypilot Core Files\n"
        "\n"
        "**Do NOT edit files in this directory.**\n"
        "\n"
        "These files are copied from the Cypilot cache (`~/.cypilot/cache/`) during\n"
        "`cpt init` or `cpt kit install`. They are the read-only reference copies of:\n"
        "\n"
        "- `skills/` — Cypilot skill scripts and CLI entry points\n"
        "- `workflows/` — workflow definitions\n"
        "- `requirements/` — validation requirements\n"
        "- `schemas/` — JSON schemas for configuration files\n"
        "- `architecture/specs/` — traceability, CDSL, CLI, and kit specifications\n"
        "\n"
        "To update these files, run `cpt init --force` or `cpt kit update`.\n"
        "Any manual changes **will be overwritten** on the next update.\n"
    )

def _gen_readme() -> str:
    """README.md content for .gen/ directory."""
    return (
        "# .gen — Generated Files\n"
        "\n"
        "**Do NOT edit files in this directory.**\n"
        "\n"
        "These files are auto-generated by Cypilot during\n"
        "`cpt init`, `cpt kit install`, or `cpt update`.\n"
        "\n"
        "Contents:\n"
        "\n"
        "- `SKILL.md` — aggregated skill navigation (routes to per-kit skills)\n"
        "- `AGENTS.md` — generated agent navigation rules\n"
        "- `README.md` — this file\n"
        "\n"
        "Per-kit files are in `config/kits/{slug}/`.\n"
        "To update: `cpt update` or `cpt kit update`.\n"
        "Any manual changes to generated files **will be overwritten** on the next update.\n"
    )

def _config_readme() -> str:
    """README.md content for config/ directory."""
    return (
        "# config — User Configuration\n"
        "\n"
        "This directory contains **user-editable** configuration files.\n"
        "\n"
        "## Files\n"
        "\n"
        "- `core.toml` — project settings (system name, slug, kit references)\n"
        "- `artifacts.toml` — artifacts registry (systems, ignore patterns)\n"
        "- `AGENTS.md` — custom agent navigation rules (add your own WHEN rules here)\n"
        "- `SKILL.md` — custom skill extensions (add your own skill instructions here)\n"
        "\n"
        "## Directories\n"
        "\n"
        "- `kits/{slug}/` — kit files (SKILL.md, AGENTS.md, artifacts/, codebase/, workflows/, scripts/).\n"
        "  These are updated via `cpt update` or `cpt kit update`.\n"
        "\n"
        "## Tips\n"
        "\n"
        "- `AGENTS.md` and `SKILL.md` start empty. Add any project-specific rules or\n"
        "  skill instructions here — they will be picked up alongside the kit ones.\n"
        "- Kit files can be edited directly; `cpt kit update` shows a diff for changes.\n"
    )

def _default_core_toml() -> dict:
    """Build default core.toml data for a new project.

    System identity (name, slug, kit) is defined in artifacts.toml only
    (see ADR-0014: cpt-cypilot-adr-remove-system-from-core-toml).

    Kits are registered dynamically via install_kit() when user accepts
    installation — not hardcoded here.
    """
    return {
        "version": "1.0",
        "project_root": "..",
        "kits": {},
    }

def _prompt_path(question: str, default: Optional[str]) -> str:
    prompt = f"{question}"
    if default is not None and str(default).strip():
        prompt += f" [{default}]"
    prompt += ": "
    try:
        sys.stderr.write(prompt)
        sys.stderr.flush()
        ans = input().strip()
    except EOFError:
        ans = ""
    if ans:
        return ans
    return default or ""

def _resolve_user_path(raw: str, base: Path) -> Path:
    p = Path(raw)
    if not p.is_absolute():
        p = base / p
    return p.resolve()

def _slug_to_pascal_case(slug: str) -> str:
    """Convert a slug like 'my-app' to PascalCase like 'MyApp'."""
    return "".join(word.capitalize() for word in slug.split("-")) if slug else "Unnamed"
# @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-init-helpers

def _define_root_system(project_root: Path) -> Dict[str, str]:
    """
    Define root system from project directory.

    Returns dict with 'name' (PascalCase) and 'slug' (lowercase-hyphenated).
    """
    # @cpt-begin:cpt-cypilot-algo-core-infra-define-root-system:p1:inst-extract-basename
    basename = project_root.name
    # @cpt-end:cpt-cypilot-algo-core-infra-define-root-system:p1:inst-extract-basename

    # @cpt-begin:cpt-cypilot-algo-core-infra-define-root-system:p1:inst-derive-slug
    slug = generate_slug(basename)
    # @cpt-end:cpt-cypilot-algo-core-infra-define-root-system:p1:inst-derive-slug

    # @cpt-begin:cpt-cypilot-algo-core-infra-define-root-system:p1:inst-derive-name
    name = _slug_to_pascal_case(slug)
    # @cpt-end:cpt-cypilot-algo-core-infra-define-root-system:p1:inst-derive-name

    # @cpt-begin:cpt-cypilot-algo-core-infra-define-root-system:p1:inst-return-system-def
    return {"name": name, "slug": slug}
    # @cpt-end:cpt-cypilot-algo-core-infra-define-root-system:p1:inst-return-system-def

_TOML_FENCE_RE = re.compile(r"```toml\s*\n(.*?)```", re.DOTALL)
MARKER_START = "<!-- @cpt:root-agents -->"
MARKER_END = "<!-- /@cpt:root-agents -->"
_AGENTS_FILENAME = "AGENTS.md"
_README_FILENAME = "README.md"

# @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-init-detect-existing
def _read_existing_install(project_root: Path) -> Optional[str]:
    """
    Check if project already has Cypilot installed by reading AGENTS.md TOML block.

    Returns install dir relative path if found, None otherwise.
    """
    import tomllib
    agents_file = project_root / _AGENTS_FILENAME
    if not agents_file.is_file():
        return None
    try:
        content = agents_file.read_text(encoding="utf-8")
    except OSError:
        return None
    if MARKER_START not in content:
        return None
    for m in _TOML_FENCE_RE.finditer(content):
        try:
            data = tomllib.loads(m.group(1))
            val = data.get("cypilot_path") or data.get("cypilot")
            if isinstance(val, str) and val.strip():
                adapter_dir = project_root / val.strip()
                if adapter_dir.is_dir():
                    return val.strip()
        except (OSError, ValueError, KeyError):
            continue
    return None
# @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-init-detect-existing

def _compute_managed_block(install_dir: str) -> str:
    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-compute-block
    return (
        f"{MARKER_START}\n"
        f"```toml\n"
        f'cypilot_path = "{install_dir}"\n'
        f"```\n"
        f"{MARKER_END}"
    )
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-compute-block

def _inject_managed_block(target_file: Path, install_dir: str, dry_run: bool = False, *, project_root: Optional[Path] = None) -> str:
    """Inject or update a managed block into *target_file*. Returns action taken."""
    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-validate-path
    resolved_target = target_file.resolve()
    if project_root is not None:
        resolved_root = project_root.resolve()
        if resolved_root not in resolved_target.parents and resolved_target != resolved_root:
            raise ValueError(f"Refusing to write outside project root: {resolved_target}")
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-validate-path
    expected_block = _compute_managed_block(install_dir)

    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-if-no-agents
    if not target_file.is_file():
        # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-create-agents-file
        if not dry_run:
            target_file.write_text(expected_block + "\n", encoding="utf-8")
        return "created"
        # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-create-agents-file
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-if-no-agents

    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-read-existing
    content = target_file.read_text(encoding="utf-8")
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-read-existing

    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-if-markers-exist
    if MARKER_START in content and MARKER_END in content:
        start_idx = content.index(MARKER_START)
        end_idx = content.index(MARKER_END) + len(MARKER_END)
        current_block = content[start_idx:end_idx]
        if current_block == expected_block.strip():
            return "unchanged"
        # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-replace-block
        new_content = content[:start_idx] + expected_block + content[end_idx:]
        # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-replace-block
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-if-markers-exist
    else:
        # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-insert-block
        new_content = expected_block + "\n\n" + content
        # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-insert-block

    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-write-agents
    if not dry_run:
        target_file.write_text(new_content, encoding="utf-8")
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-write-agents

    # @cpt-begin:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-return-agents-path
    return "updated"
    # @cpt-end:cpt-cypilot-algo-core-infra-inject-root-agents:p1:inst-return-agents-path

_DEFAULT_KIT_SOURCE = "cyberfabric/cyber-pilot-kit-sdlc"


def _prompt_kit_install_flag(interactive: bool) -> bool:
    """Return True if the user accepted kit installation (or --yes mode)."""
    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-prompt-kit
    if interactive and sys.stdin.isatty():
        sys.stderr.write(f"\n  Install SDLC kit ({_DEFAULT_KIT_SOURCE})?\n")
        sys.stderr.write("  [a]ccept / [d]ecline: ")
        sys.stderr.flush()
        try:
            answer = input().strip().lower()
        except EOFError:
            answer = "d"
        return answer in ("a", "accept")
    return not interactive
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-prompt-kit


def _install_default_kit(
    cypilot_dir: Path,
    interactive: bool,
    actions: Dict[str, str],
    errors: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Download and install the default SDLC kit. Returns kit_results dict."""
    from .kit import (
        install_kit, _parse_github_source, _download_kit_from_github,
    )
    kit_results: Dict[str, Any] = {}
    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-install-kit-accepted
    tmp_to_clean: Optional[Path] = None
    try:
        owner, repo, version = _parse_github_source(_DEFAULT_KIT_SOURCE)
        ui.step(f"Downloading {_DEFAULT_KIT_SOURCE}...")
        kit_source_dir, resolved_version = _download_kit_from_github(owner, repo, version)
        tmp_to_clean = kit_source_dir.parent

        kit_slug = "sdlc"
        github_source = f"github:{owner}/{repo}"
        kit_result = install_kit(
            kit_source_dir, cypilot_dir, kit_slug,
            kit_version=resolved_version, source=github_source,
            interactive=interactive,
        )

        art_dir = cypilot_dir / "config" / "kits" / kit_slug / "artifacts"
        artifact_kinds = (
            sorted(d.name for d in art_dir.iterdir() if d.is_dir())
            if art_dir.is_dir() else []
        )
        kit_results[kit_slug] = {
            "files_written": kit_result.get("files_copied", 0),
            "errors": kit_result.get("errors", []),
            "artifact_kinds": artifact_kinds,
        }
        kit_status = kit_result.get("status", "")
        if kit_result.get("errors") and kit_status not in ("PASS", "WARN"):
            errors.extend(
                {"path": kit_slug, "error": e} for e in kit_result["errors"]
            )
        for key, val in kit_result.get("actions", {}).items():
            actions[f"kit_{kit_slug}_{key}"] = val

        if kit_status == "WARN":
            ui.warn(f"Kit '{kit_slug}' installed with warnings")
        elif kit_status and kit_status != "PASS":
            ui.warn(f"Kit '{kit_slug}' installed with status: {kit_status}")
        else:
            ui.substep(f"Kit '{kit_slug}' installed (v{resolved_version or 'dev'})")
    except (OSError, ValueError, RuntimeError) as exc:
        ui.warn(f"Kit installation failed: {exc}")
        errors.append({"path": "kit", "error": str(exc)})
    finally:
        if tmp_to_clean is not None:
            shutil.rmtree(tmp_to_clean, ignore_errors=True)
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-install-kit-accepted
    return kit_results


def _inject_root_agents(project_root: Path, install_dir: str, dry_run: bool = False) -> str:
    """Inject or update root AGENTS.md managed block. Returns action taken."""
    return _inject_managed_block(project_root / _AGENTS_FILENAME, install_dir, dry_run, project_root=project_root)

# @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-init-inject-claude
def _inject_root_claude(project_root: Path, install_dir: str, dry_run: bool = False) -> str:
    """Inject or update root CLAUDE.md managed block. Returns action taken."""
    return _inject_managed_block(project_root / "CLAUDE.md", install_dir, dry_run, project_root=project_root)
# @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-init-inject-claude

def cmd_init(argv: List[str]) -> int:
    # @cpt-dod:cpt-cypilot-dod-core-infra-init-config:p1
    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-user-init
    p = argparse.ArgumentParser(prog="init", description="Initialize Cypilot in a project")
    p.add_argument("--project-root", default=None, help="Project root directory")
    p.add_argument("--install-dir", default=None, help="Cypilot directory relative to project root (default: cypilot)")
    p.add_argument("--project-name", default=None, help="Project name (default: project root folder name)")
    p.add_argument("--yes", action="store_true", help="Do not prompt; accept defaults")
    p.add_argument("--dry-run", action="store_true", help="Compute changes without writing files")
    p.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = p.parse_args(argv)
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-user-init

    cwd = Path.cwd().resolve()
    interactive = not args.yes

    if interactive:
        sys.stderr.write("\n")
        sys.stderr.write("  \033[1mWelcome to Cypilot\033[0m\n")
        sys.stderr.write("  Set up AI-powered architecture traceability for your project.\n")
        sys.stderr.write("  Cypilot will create a configuration directory with design artifacts,\n")
        sys.stderr.write("  validation rules, and agent integration files.\n")
        sys.stderr.write("\n")

    # Resolve project root
    default_project_root = cwd
    if args.project_root is None and interactive:
        sys.stderr.write("  \033[2mThe project root is the top-level directory of your repository.\033[0m\n")
        sys.stderr.write("  \033[2mPress Enter to use the current directory.\033[0m\n")
        raw_root = _prompt_path("Project root directory?", default_project_root.as_posix())
        project_root = _resolve_user_path(raw_root, cwd)
    else:
        raw_root = args.project_root or default_project_root.as_posix()
        project_root = _resolve_user_path(raw_root, cwd)

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-check-existing
    existing_install_rel = _read_existing_install(project_root)
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-check-existing

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-if-exists
    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-return-exists
    if existing_install_rel is not None and not args.force:
        ui.result(
            {
                "status": "FAIL",
                "message": "Cypilot already initialized. Use 'cypilot update' to upgrade or --force to reinitialize.",
                "project_root": project_root.as_posix(),
                "cypilot_dir": (project_root / existing_install_rel).as_posix(),
            },
            human_fn=lambda d: (
                ui.error("Cypilot is already initialized in this project."),
                ui.detail("Directory", (project_root / existing_install_rel).as_posix()),
                ui.blank(),
                ui.hint("To refresh to the latest version:  cpt update"),
                ui.hint("To reinitialize from scratch:      cpt init --force"),
                ui.blank(),
            ),
        )
        return 2
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-return-exists
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-if-exists

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-if-interactive
    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-prompt-dir
    default_install_dir = existing_install_rel or DEFAULT_INSTALL_DIR
    if args.install_dir is None and interactive:
        sys.stderr.write("\n")
        sys.stderr.write("  \033[2mCypilot stores its files in a subdirectory of your project.\033[0m\n")
        sys.stderr.write("  \033[2mThis directory will contain .core/, .gen/, and config/ folders.\033[0m\n")
        install_rel = _prompt_path("Cypilot directory (relative to project root)?", default_install_dir)
    else:
        install_rel = args.install_dir or default_install_dir
    install_rel = install_rel.strip() or default_install_dir
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-prompt-dir
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-if-interactive

    cypilot_dir = (project_root / install_rel).resolve()

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-define-root
    root_system = _define_root_system(project_root)
    project_name = str(args.project_name).strip() if args.project_name else root_system["name"]
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-define-root

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-prompt-agents
    # Stub: agent selection not yet needed (single kit); will prompt when multi-kit support lands
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-prompt-agents

    # Verify cache exists
    if not CACHE_DIR.is_dir():
        ui.result(
            {
                "status": "ERROR",
                "message": f"Cypilot cache not found at {CACHE_DIR}. Run 'cypilot update' first.",
                "project_root": project_root.as_posix(),
            },
            human_fn=lambda d: (
                ui.error("Cypilot cache not found."),
                ui.detail("Expected at", str(CACHE_DIR)),
                ui.blank(),
                ui.hint("Install Cypilot first:  pip install cypilot && cpt update"),
                ui.blank(),
            ),
        )
        return 1

    actions: Dict[str, str] = {}
    errors: List[Dict[str, str]] = []
    backups: List[str] = []

    # Create backup before --force overwrites
    if args.force and cypilot_dir.exists() and not args.dry_run:
        backup_path = create_backup(cypilot_dir)
        if backup_path:
            backups.append(backup_path.as_posix())

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-copy-skill
    if not args.dry_run:
        cypilot_dir.mkdir(parents=True, exist_ok=True)
        copy_results = _copy_from_cache(CACHE_DIR, cypilot_dir, force=args.force)
    else:
        copy_results = {d: "dry_run" for d in COPY_DIRS}
        for item in COPY_ARCHITECTURE_ITEMS:
            copy_results[f"architecture/{item}"] = "dry_run"
    actions["copy"] = json.dumps(copy_results)
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-copy-skill

    # Create the three subdirectories: .core/ (already created by _copy_from_cache), .gen/, config/
    config_dir = cypilot_dir / "config"
    gen_dir = cypilot_dir / GEN_SUBDIR
    core_dir = cypilot_dir / CORE_SUBDIR
    if not args.dry_run:
        config_dir.mkdir(parents=True, exist_ok=True)
        gen_dir.mkdir(parents=True, exist_ok=True)

    # Write README.md into each directory (always overwrite)
    if not args.dry_run:
        (core_dir / _README_FILENAME).write_text(_core_readme(), encoding="utf-8")
        (gen_dir / _README_FILENAME).write_text(_gen_readme(), encoding="utf-8")
        (config_dir / _README_FILENAME).write_text(_config_readme(), encoding="utf-8")
    actions["readmes"] = "created"

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-create-config
    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config:p1:inst-mkdir-config
    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config:p1:inst-write-core-toml
    desired_core = _default_core_toml()
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config:p1:inst-write-core-toml
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config:p1:inst-mkdir-config
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-create-config

    # Write config files into config/ subdirectory
    core_toml_path = (config_dir / "core.toml").resolve()
    core_toml_existed = core_toml_path.is_file()
    if core_toml_existed and not args.force:
        actions["core_toml"] = "unchanged"
    else:
        if not args.dry_run:
            toml_utils.dump(desired_core, core_toml_path, header_comment="Cypilot project configuration")
        actions["core_toml"] = "updated" if core_toml_existed else "created"

    # Write user-editable AGENTS.md to config/ (preserve existing)
    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-create-config-agents
    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config-agents:p1:inst-gen-when-rules
    config_agents_path = (config_dir / _AGENTS_FILENAME).resolve()
    config_agents_existed = config_agents_path.is_file()
    if config_agents_existed and not args.force:
        actions["config_agents"] = "unchanged"
    else:
        if not config_agents_existed and not args.dry_run:
            config_agents_path.write_text(
                "# Custom Agent Navigation Rules\n"
                "\n"
                "Add your project-specific WHEN rules here.\n"
                "These rules are loaded alongside the generated rules in `{cypilot_path}/.gen/" + _AGENTS_FILENAME + "`.\n",
                encoding="utf-8",
            )
            # If force + existed: leave user content untouched
        # @cpt-end:cpt-cypilot-algo-core-infra-create-config-agents:p1:inst-gen-when-rules
        # @cpt-begin:cpt-cypilot-algo-core-infra-create-config-agents:p1:inst-write-config-agents
        actions["config_agents"] = "unchanged" if config_agents_existed else "created"
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config-agents:p1:inst-write-config-agents
    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config-agents:p1:inst-return-config-agents-path
    actions["config_agents_path"] = config_agents_path.as_posix()
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config-agents:p1:inst-return-config-agents-path
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-create-config-agents

    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config:p1:inst-validate-schemas
    # Stub: schema validation deferred to p2
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config:p1:inst-validate-schemas

    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config:p1:inst-return-config-paths
    # (paths reported in final JSON output)
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config:p1:inst-return-config-paths

    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config:p1:inst-mkdir-kits
    # Kit installation via GitHub prompt (ADR-0013)
    from .kit import regenerate_gen_aggregates

    kit_results: Dict[str, Any] = {}

    if not args.dry_run:
        # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-prompt-kit
        install_kit_flag = _prompt_kit_install_flag(interactive)
        # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-prompt-kit

        # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-install-kit-accepted
        if install_kit_flag:
            kit_results = _install_default_kit(cypilot_dir, interactive, actions, errors)
            if errors:
                err_result: Dict[str, object] = {
                    "status": "ERROR",
                    "message": "Init failed",
                    "project_root": project_root.as_posix(),
                    "cypilot_dir": cypilot_dir.as_posix(),
                    "dry_run": bool(args.dry_run),
                    "errors": errors,
                }
                if backups:
                    err_result["backups"] = backups
                ui.result(err_result, human_fn=lambda d: _human_init_error(d))
                return 1
        # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-install-kit-accepted
        # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-skip-kit-declined
        else:
            ui.info(f"Skipped kit installation. Install later: cpt kit install {_DEFAULT_KIT_SOURCE}")
        # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-skip-kit-declined

    # @cpt-begin:cpt-cypilot-algo-core-infra-create-config:p1:inst-write-artifacts-toml
    # Write artifacts.toml after kit install decision so kit slug is known
    installed_kit_slug = next(iter(kit_results), "") if kit_results else ""
    desired_registry = generate_default_registry(project_name, kit_slug=installed_kit_slug)
    registry_path = (config_dir / "artifacts.toml").resolve()
    registry_existed_before = registry_path.is_file()
    if registry_existed_before and not args.force:
        actions["artifacts_registry"] = "unchanged"
    else:
        if not args.dry_run:
            toml_utils.dump(desired_registry, registry_path, header_comment="Cypilot artifacts registry")
        actions["artifacts_registry"] = "updated" if registry_existed_before else "created"
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config:p1:inst-write-artifacts-toml

    # Regenerate .gen/ aggregates (AGENTS.md, SKILL.md, README.md)
    if not args.dry_run:
        gen_result = regenerate_gen_aggregates(cypilot_dir)
        actions.update(gen_result)

    # Write config/SKILL.md — empty, for user extensions (preserve existing)
    if not args.dry_run:
        config_skill_path = config_dir / "SKILL.md"
        if not config_skill_path.is_file():
            config_skill_path.write_text(
                "# Custom Skill Extensions\n"
                "\n"
                "Add your project-specific skill instructions here.\n"
                "These are loaded alongside the generated skills in `{cypilot_path}/.gen/SKILL.md`.\n",
                encoding="utf-8",
            )
            actions["config_skill"] = "created"
        else:
            actions["config_skill"] = "unchanged"

    actions["kits"] = json.dumps(kit_results)
    # @cpt-end:cpt-cypilot-algo-core-infra-create-config:p1:inst-mkdir-kits

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-delegate-agents
    # Stub: Agent Generator (Feature 5 boundary) — agent entry points generated separately
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-delegate-agents

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-inject-agents
    root_agents_action = _inject_root_agents(project_root, install_rel, dry_run=args.dry_run)
    actions["root_agents"] = root_agents_action
    root_claude_action = _inject_root_claude(project_root, install_rel, dry_run=args.dry_run)
    actions["root_claude"] = root_claude_action
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-inject-agents

    if errors:
        err_result: Dict[str, object] = {
            "status": "ERROR",
            "message": "Init failed",
            "project_root": project_root.as_posix(),
            "cypilot_dir": cypilot_dir.as_posix(),
            "dry_run": bool(args.dry_run),
            "errors": errors,
        }
        if backups:
            err_result["backups"] = backups
        ui.result(err_result, human_fn=lambda d: _human_init_error(d))
        return 1

    # @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-return-init-ok
    # @cpt-begin:cpt-cypilot-state-core-infra-project-install:p1:inst-init-complete
    init_result: Dict[str, object] = {
        "status": "PASS",
        "project_root": project_root.as_posix(),
        "cypilot_dir": cypilot_dir.as_posix(),
        "core_toml": core_toml_path.as_posix(),
        "dry_run": bool(args.dry_run),
        "actions": actions,
        "root_system": root_system,
    }
    if backups:
        init_result["backups"] = backups
    ui.result(init_result, human_fn=lambda d: _human_init_ok(d, project_root, cypilot_dir, install_rel, project_name, kit_results))
    return 0
    # @cpt-end:cpt-cypilot-state-core-infra-project-install:p1:inst-init-complete
    # @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-return-init-ok

# ---------------------------------------------------------------------------
# Human-friendly formatters
# ---------------------------------------------------------------------------
# @cpt-begin:cpt-cypilot-flow-core-infra-project-init:p1:inst-init-format-output
def _human_init_ok(
    data: Dict[str, object],
    project_root: Path,
    _cypilot_dir: Path,
    install_rel: str,
    project_name: str,
    kit_results: Dict[str, Any],
) -> None:
    dry = data.get("dry_run", False)
    prefix = "[dry-run] " if dry else ""

    ui.header(f"{prefix}Cypilot Init")
    ui.detail("Project", project_name)
    ui.detail("Root", project_root.as_posix())
    ui.detail("Cypilot dir", f"{install_rel}/")
    ui.blank()

    ui.step("Core files copied to .core/")
    ui.step("Config created in config/")
    ui.substep("core.toml      — project settings")
    ui.substep("artifacts.toml — artifact registry")
    ui.substep("AGENTS.md      — custom agent rules (edit freely)")
    ui.substep("SKILL.md       — custom skill extensions (edit freely)")

    if kit_results:
        ui.step("Kits installed:")
        for slug, kr in kit_results.items():
            n = kr.get("files_written", 0)
            kinds = kr.get("artifact_kinds", [])
            ui.substep(f"{slug}: {n} files generated ({', '.join(kinds)})")

    ui.step("AGENTS.md navigation block injected into project root")

    if dry:
        ui.success("Dry run complete — no files were written.")
    else:
        ui.success("Cypilot initialized!")
        ui.blank()
        ui.info("Next steps:")
        ui.hint("1. Set up your IDE:  cpt generate-agents")
        ui.hint("2. Review config:    open " + install_rel + "/config/core.toml")
        ui.hint("3. Start using:      type '/cypilot' in your IDE chat")
    ui.blank()

def _human_init_error(data: Dict[str, object]) -> None:
    ui.error("Initialization failed")
    errors = data.get("errors", [])
    for err in errors:
        if isinstance(err, dict):
            ui.substep(f"• {err.get('path', '?')}: {err.get('error', '?')}")
        else:
            ui.substep(f"• {err}")
    ui.blank()
# @cpt-end:cpt-cypilot-flow-core-infra-project-init:p1:inst-init-format-output
