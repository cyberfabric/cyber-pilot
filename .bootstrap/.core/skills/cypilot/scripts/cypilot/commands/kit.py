"""
Kit Management Commands

Provides CLI handlers for kit install and kit update.
Kits are direct file packages — no blueprint processing or generation.
"""

import argparse
import json
import os
import shutil
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..utils.ui import ui


# ---------------------------------------------------------------------------
# GitHub source helpers
# ---------------------------------------------------------------------------

def _github_headers() -> Dict[str, str]:
    """Build common headers for GitHub API requests.

    Includes Authorization if GITHUB_TOKEN is set in the environment.
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "cypilot-kit-installer",
    }
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _parse_github_source(source: str) -> Tuple[str, str, str]:
    """Parse 'owner/repo[@version]' into (owner, repo, version).

    Returns (owner, repo, version) where version may be empty.
    Raises ValueError if format is invalid.
    """
    version = ""
    if "@" in source:
        source, version = source.rsplit("@", 1)

    parts = source.strip("/").split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(
            f"Invalid GitHub source: '{source}'. Expected format: owner/repo"
        )
    return parts[0], parts[1], version


def _download_kit_from_github(
    owner: str,
    repo: str,
    version: str = "",
) -> Tuple[Path, str]:
    """Download a kit from GitHub and extract to a temp directory.

    Uses GitHub API tarball endpoint (stdlib only, no dependencies).

    Args:
        owner: GitHub repository owner.
        repo: GitHub repository name.
        version: Git ref (tag/branch/SHA). If empty, resolves latest release.

    Returns:
        (extracted_dir, resolved_version) — caller must clean up parent temp dir.

    Raises:
        RuntimeError: on network or extraction errors.
    """
    # Resolve version: if empty, query latest release
    if not version:
        version = _resolve_latest_github_release(owner, repo)

    # Download tarball
    url = f"https://api.github.com/repos/{owner}/{repo}/tarball/{version}"
    req = urllib.request.Request(url, headers=_github_headers())

    tmp_dir = Path(tempfile.mkdtemp(prefix="cypilot-kit-"))
    tar_path = tmp_dir / "kit.tar.gz"

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(tar_path, "wb") as f:
                shutil.copyfileobj(resp, f)
    except Exception as exc:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise RuntimeError(
            f"Failed to download kit from GitHub ({owner}/{repo}@{version}): {exc}"
        ) from exc

    # Extract
    try:
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=tmp_dir, filter="data")
    except Exception as exc:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise RuntimeError(
            f"Failed to extract kit archive: {exc}"
        ) from exc

    tar_path.unlink(missing_ok=True)

    # Find the extracted directory (GitHub tarballs contain one top-level dir)
    subdirs = [d for d in tmp_dir.iterdir() if d.is_dir()]
    if len(subdirs) != 1:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise RuntimeError(
            f"Unexpected archive structure: expected 1 directory, found {len(subdirs)}"
        )

    return subdirs[0], version


def _resolve_latest_github_release(owner: str, repo: str) -> str:
    """Query GitHub API for the latest release tag.

    Falls back to default branch if no releases exist.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    req = urllib.request.Request(url, headers=_github_headers())

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            tag = data.get("tag_name", "")
            if tag:
                return tag
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            pass  # No releases — fall through to default branch
        else:
            raise RuntimeError(
                f"GitHub API error ({exc.code}): {exc.reason}"
            ) from exc
    except Exception as exc:
        raise RuntimeError(
            f"Failed to query GitHub releases for {owner}/{repo}: {exc}"
        ) from exc

    # No releases found — use default branch (empty ref = default branch tarball)
    return ""

# ---------------------------------------------------------------------------
# Config seeding — copy default .toml configs from kit scripts to config/
# ---------------------------------------------------------------------------

# Directories and files that constitute kit content (copied to config/kits/{slug}/)
_KIT_CONTENT_DIRS = ("artifacts", "codebase", "scripts", "workflows")
_KIT_CONTENT_FILES = ("constraints.toml", "SKILL.md", "AGENTS.md")
# Infrastructure file — copied but not subject to interactive diff
_KIT_CONF_FILE = "conf.toml"

_CONFIG_EXTENSIONS = {".toml"}

def _seed_kit_config_files(
    gen_scripts_dir: Path,
    config_dir: Path,
    actions: Dict[str, str],
) -> None:
    """Copy top-level .toml files from generated scripts into config/ if missing.

    Only seeds files that don't already exist in config/ — never overwrites
    user-editable config.
    """
    # @cpt-begin:cpt-cypilot-algo-kit-content-mgmt:p1:inst-seed-configs
    config_dir.mkdir(parents=True, exist_ok=True)
    for src in gen_scripts_dir.iterdir():
        if src.is_file() and src.suffix in _CONFIG_EXTENSIONS:
            dst = config_dir / src.name
            if not dst.exists():
                shutil.copy2(src, dst)
                actions[f"config_{src.stem}"] = "seeded"
    # @cpt-end:cpt-cypilot-algo-kit-content-mgmt:p1:inst-seed-configs

# ---------------------------------------------------------------------------
# Shared CLI helper — resolve project root + cypilot directory
# ---------------------------------------------------------------------------

def _resolve_cypilot_dir() -> Optional[tuple]:
    """Resolve project root and cypilot directory from CWD.

    Returns (project_root, cypilot_dir) or None (after printing JSON error).
    """
    from ..utils.files import find_project_root, _read_cypilot_var

    project_root = find_project_root(Path.cwd())
    if project_root is None:
        ui.result({"status": "ERROR", "message": "No project root found"})
        return None

    cypilot_rel = _read_cypilot_var(project_root)
    if not cypilot_rel:
        ui.result({"status": "ERROR", "message": "No cypilot directory"})
        return None

    cypilot_dir = (project_root / cypilot_rel).resolve()
    return project_root, cypilot_dir

# ---------------------------------------------------------------------------
# Kit content helpers — copy specific dirs/files, collect metadata for .gen/
# ---------------------------------------------------------------------------

# @cpt-algo:cpt-cypilot-algo-kit-content-mgmt:p1
def _copy_kit_content(
    kit_source: Path,
    config_kit_dir: Path,
) -> Dict[str, str]:
    """Copy kit content items from *kit_source* → *config_kit_dir*.

    Copies only the directories listed in ``_KIT_CONTENT_DIRS``, the files
    listed in ``_KIT_CONTENT_FILES``, and the infra ``_KIT_CONF_FILE``.
    Returns a dict of ``{item: action}`` entries.
    """
    # @cpt-begin:cpt-cypilot-algo-kit-content-mgmt:p1:inst-copy-content
    actions: Dict[str, str] = {}
    config_kit_dir.mkdir(parents=True, exist_ok=True)

    for d in _KIT_CONTENT_DIRS:
        src = kit_source / d
        dst = config_kit_dir / d
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            actions[d] = "copied"

    for f in _KIT_CONTENT_FILES:
        src = kit_source / f
        dst = config_kit_dir / f
        if src.is_file():
            shutil.copy2(src, dst)
            actions[f] = "copied"

    return actions
    # @cpt-end:cpt-cypilot-algo-kit-content-mgmt:p1:inst-copy-content


def _collect_kit_metadata(
    config_kit_dir: Path,
    kit_slug: str,
) -> Dict[str, str]:
    """Read installed kit files and return metadata for .gen/ aggregation.

    Returns dict with:
        skill_nav      — navigation line for ``.gen/SKILL.md``
        agents_content — raw content of kit's AGENTS.md for ``.gen/AGENTS.md``
    """
    # @cpt-begin:cpt-cypilot-algo-kit-content-mgmt:p1:inst-collect-metadata
    result: Dict[str, str] = {"skill_nav": "", "agents_content": ""}

    skill_path = config_kit_dir / "SKILL.md"
    if skill_path.is_file():
        result["skill_nav"] = (
            f"ALWAYS invoke `{{cypilot_path}}/config/kits/{kit_slug}/SKILL.md` FIRST"
        )

    agents_path = config_kit_dir / "AGENTS.md"
    if agents_path.is_file():
        try:
            result["agents_content"] = agents_path.read_text(encoding="utf-8")
        except OSError:
            pass

    return result
    # @cpt-end:cpt-cypilot-algo-kit-content-mgmt:p1:inst-collect-metadata


# ---------------------------------------------------------------------------
# .gen/ aggregation — single source of truth for all callers
# ---------------------------------------------------------------------------

# @cpt-algo:cpt-cypilot-algo-kit-regen-gen:p1
def regenerate_gen_aggregates(cypilot_dir: Path) -> Dict[str, Any]:
    """Regenerate .gen/AGENTS.md, .gen/SKILL.md, .gen/README.md from all installed kits.

    Scans config/kits/*/ for installed kits, collects metadata (skill_nav,
    agents_content) from each, and writes the aggregate files into .gen/.

    This is the canonical function — called by cmd_kit_install, cmd_kit_update,
    cmd_init, and cmd_update.

    Returns dict with keys: gen_agents, gen_skill, gen_readme (action strings).
    """
    config_dir = cypilot_dir / "config"
    gen_dir = cypilot_dir / ".gen"
    gen_dir.mkdir(parents=True, exist_ok=True)

    result: Dict[str, Any] = {}

    # @cpt-begin:cpt-cypilot-algo-kit-regen-gen:p1:inst-scan-kits
    # Collect metadata from all installed kits
    gen_skill_nav_parts: List[str] = []
    gen_agents_parts: List[str] = []
    config_kits_dir = config_dir / "kits"
    if config_kits_dir.is_dir():
        for kit_dir in sorted(config_kits_dir.iterdir()):
            if not kit_dir.is_dir():
                continue
            # @cpt-begin:cpt-cypilot-algo-kit-regen-gen:p1:inst-collect-all-metadata
            meta = _collect_kit_metadata(kit_dir, kit_dir.name)
            if meta["skill_nav"]:
                gen_skill_nav_parts.append(meta["skill_nav"])
            if meta["agents_content"]:
                gen_agents_parts.append(meta["agents_content"])
            # @cpt-end:cpt-cypilot-algo-kit-regen-gen:p1:inst-collect-all-metadata
    # @cpt-end:cpt-cypilot-algo-kit-regen-gen:p1:inst-scan-kits

    # @cpt-begin:cpt-cypilot-algo-kit-regen-gen:p1:inst-read-project-name
    # Read project name from artifacts.toml (ADR-0014)
    project_name = _read_project_name_from_registry(config_dir) or "Cypilot"
    # @cpt-end:cpt-cypilot-algo-kit-regen-gen:p1:inst-read-project-name

    # @cpt-begin:cpt-cypilot-algo-kit-regen-gen:p1:inst-write-gen-agents
    # Write .gen/AGENTS.md
    gen_agents_content = "\n".join([
        f"# Cypilot: {project_name}",
        "",
        "## Navigation Rules",
        "",
        "ALWAYS open and follow `{cypilot_path}/config/artifacts.toml` WHEN working with artifacts or codebase",
        "",
        "ALWAYS open and follow `{cypilot_path}/.core/schemas/artifacts.schema.json` WHEN working with artifacts.toml",
        "",
        "ALWAYS open and follow `{cypilot_path}/.core/architecture/specs/artifacts-registry.md` WHEN working with artifacts.toml",
        "",
    ])
    if gen_agents_parts:
        gen_agents_content = gen_agents_content.rstrip() + "\n\n" + "\n\n".join(gen_agents_parts) + "\n"
    (gen_dir / "AGENTS.md").write_text(gen_agents_content, encoding="utf-8")
    result["gen_agents"] = "updated"
    # @cpt-end:cpt-cypilot-algo-kit-regen-gen:p1:inst-write-gen-agents

    # @cpt-begin:cpt-cypilot-algo-kit-regen-gen:p1:inst-write-gen-skill
    # Write .gen/SKILL.md
    nav_rules = "\n\n".join(gen_skill_nav_parts) if gen_skill_nav_parts else ""
    (gen_dir / "SKILL.md").write_text(
        "# Cypilot Generated Skills\n\n"
        "This file routes to per-kit skill instructions.\n\n"
        + (nav_rules + "\n" if nav_rules else ""),
        encoding="utf-8",
    )
    result["gen_skill"] = "updated"
    # @cpt-end:cpt-cypilot-algo-kit-regen-gen:p1:inst-write-gen-skill

    # @cpt-begin:cpt-cypilot-algo-kit-regen-gen:p1:inst-write-gen-readme
    # Write .gen/README.md
    from .init import _gen_readme
    (gen_dir / "README.md").write_text(_gen_readme(), encoding="utf-8")
    result["gen_readme"] = "updated"
    # @cpt-end:cpt-cypilot-algo-kit-regen-gen:p1:inst-write-gen-readme

    return result


def _read_project_name_from_registry(config_dir: Path) -> Optional[str]:
    """Read project name from config/artifacts.toml [[systems]][0].name.

    Per ADR-0014 (cpt-cypilot-adr-remove-system-from-core-toml),
    artifacts.toml is the single source of truth for system identity.
    """
    artifacts_toml = config_dir / "artifacts.toml"
    if not artifacts_toml.is_file():
        return None
    try:
        import tomllib
        with open(artifacts_toml, "rb") as f:
            data = tomllib.load(f)
        systems = data.get("systems", [])
        if isinstance(systems, list) and systems:
            first = systems[0]
            if isinstance(first, dict):
                name = first.get("name")
                if isinstance(name, str) and name.strip():
                    return name.strip()
    except Exception as exc:
        sys.stderr.write(f"kit: warning: cannot read project name from {artifacts_toml}: {exc}\n")
    return None


# ---------------------------------------------------------------------------
# Core kit installation logic (used by both cmd_kit_install and init)
# ---------------------------------------------------------------------------

# @cpt-dod:cpt-cypilot-dod-kit-install:p1
# @cpt-state:cpt-cypilot-state-kit-installation:p1
# @cpt-algo:cpt-cypilot-algo-kit-install:p1
def install_kit(
    kit_source: Path,
    cypilot_dir: Path,
    kit_slug: str,
    kit_version: str = "",
    source: str = "",
    *,
    interactive: bool = False,
) -> Dict[str, Any]:
    """Install a kit: copy ready files from source into config/kits/{slug}/.

    Kits are direct file packages — no blueprint processing.
    Caller is responsible for validation and dry-run checks.

    Args:
        kit_source: Kit source directory.
        cypilot_dir: Resolved project cypilot directory.
        kit_slug: Kit identifier.
        kit_version: Kit version string.
        source: Source identifier for registration (e.g. "github:owner/repo").
        interactive: If True and stdin is a tty, prompt for user_modifiable paths.

    Returns:
        Dict with: status, kit, version, files_copied,
        errors, actions, skill_nav, agents_content.
    """
    config_dir = cypilot_dir / "config"
    config_kits_dir = config_dir / "kits"
    config_kit_dir = config_kits_dir / kit_slug

    actions: Dict[str, str] = {}
    errors: List[str] = []

    # @cpt-begin:cpt-cypilot-algo-kit-install:p1:inst-validate-source
    if not kit_source.is_dir():
        return {
            "status": "FAIL",
            "kit": kit_slug,
            "errors": [f"Kit source not found: {kit_source}"],
        }
    # @cpt-end:cpt-cypilot-algo-kit-install:p1:inst-validate-source

    # @cpt-begin:cpt-cypilot-algo-kit-install:p1:inst-manifest-install
    # Check for manifest-driven installation
    from ..utils.manifest import load_manifest
    manifest = load_manifest(kit_source)
    if manifest is not None:
        return install_kit_with_manifest(
            kit_source, cypilot_dir, kit_slug, kit_version,
            manifest, interactive=interactive, source=source,
        )
    # @cpt-end:cpt-cypilot-algo-kit-install:p1:inst-manifest-install

    # @cpt-begin:cpt-cypilot-algo-kit-install:p1:inst-copy-content
    # Copy kit content → config/kits/{slug}/ (legacy path)
    copy_actions = _copy_kit_content(kit_source, config_kit_dir)
    actions.update(copy_actions)
    # @cpt-end:cpt-cypilot-algo-kit-install:p1:inst-copy-content

    # @cpt-begin:cpt-cypilot-algo-kit-install:p1:inst-read-version
    # Read version from source conf.toml (conf.toml is NOT copied into installed kit)
    if not kit_version:
        src_conf = kit_source / _KIT_CONF_FILE
        if src_conf.is_file():
            kit_version = _read_kit_version(src_conf)
    # @cpt-end:cpt-cypilot-algo-kit-install:p1:inst-read-version

    # @cpt-begin:cpt-cypilot-algo-kit-install:p1:inst-seed-configs
    # Seed kit config files into config/ (only if missing)
    scripts_dir = config_kit_dir / "scripts"
    if scripts_dir.is_dir():
        _seed_kit_config_files(scripts_dir, config_dir, actions)
    # @cpt-end:cpt-cypilot-algo-kit-install:p1:inst-seed-configs

    # @cpt-begin:cpt-cypilot-algo-kit-install:p1:inst-register-core
    # Register in core.toml
    _register_kit_in_core_toml(config_dir, kit_slug, kit_version, cypilot_dir, source=source)
    # @cpt-end:cpt-cypilot-algo-kit-install:p1:inst-register-core

    # @cpt-begin:cpt-cypilot-algo-kit-install:p1:inst-collect-meta
    # Collect metadata for .gen/ aggregation
    meta = _collect_kit_metadata(config_kit_dir, kit_slug)
    # @cpt-end:cpt-cypilot-algo-kit-install:p1:inst-collect-meta

    # @cpt-begin:cpt-cypilot-algo-kit-install:p1:inst-return-result
    files_copied = sum(1 for v in copy_actions.values() if v == "copied")

    return {
        "status": "PASS" if not errors else "WARN",
        "action": "installed",
        "kit": kit_slug,
        "version": kit_version,
        "files_copied": files_copied,
        "errors": errors,
        "skill_nav": meta["skill_nav"],
        "agents_content": meta["agents_content"],
        "actions": actions,
    }
    # @cpt-end:cpt-cypilot-algo-kit-install:p1:inst-return-result


# ---------------------------------------------------------------------------
# Manifest-driven kit installation
# ---------------------------------------------------------------------------

# @cpt-algo:cpt-cypilot-algo-kit-manifest-install:p1
def install_kit_with_manifest(
    kit_source: Path,
    cypilot_dir: Path,
    kit_slug: str,
    kit_version: str,
    manifest: "Manifest",
    *,
    interactive: bool = True,
    source: str = "",
) -> Dict[str, Any]:
    """Install a kit using its manifest.toml — manifest-driven installation.

    Each declared resource is copied from kit source to a resolved target path.
    Resource bindings are registered in core.toml under ``[kits.{slug}.resources]``.

    Args:
        kit_source: Kit source directory (containing manifest.toml).
        cypilot_dir: Resolved project cypilot directory.
        kit_slug: Kit identifier.
        kit_version: Kit version string.
        manifest: Parsed Manifest object.
        interactive: If True and stdin is a tty, prompt for user_modifiable paths.
        source: Source identifier for registration (e.g. "github:owner/repo").

    Returns:
        Dict with: status, kit, version, files_copied, resource_bindings,
        errors, skill_nav, agents_content.
    """
    from ..utils.manifest import validate_manifest

    config_dir = cypilot_dir / "config"
    errors: List[str] = []  # collects non-fatal warnings (copy/template failures)
    files_copied = 0

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-read
    # Validate manifest against kit source
    validation_errors = validate_manifest(manifest, kit_source)
    if validation_errors:
        return {
            "status": "FAIL",
            "kit": kit_slug,
            "errors": validation_errors,
        }
    # @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-read

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-root-prompt
    # Resolve kit root directory from manifest template
    kit_root_template = manifest.root
    kit_root_rel = kit_root_template.replace(
        "{cypilot_path}", "."
    ).replace(
        "{slug}", kit_slug
    )
    kit_root = (cypilot_dir / kit_root_rel).resolve()

    if interactive and manifest.user_modifiable and sys.stdin.isatty():
        try:
            user_input = input(
                f"Kit root directory [{kit_root}]: "
            ).strip()
            if user_input:
                kit_root = Path(user_input).resolve()
        except (EOFError, KeyboardInterrupt):
            pass
    # @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-root-prompt

    kit_root.mkdir(parents=True, exist_ok=True)
    resource_bindings: Dict[str, Dict[str, str]] = {}

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-foreach-resource
    for res in manifest.resources:
        # @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-prompt-path
        target_rel = res.default_path
        if interactive and res.user_modifiable and sys.stdin.isatty():
            try:
                prompt_default = str(kit_root / res.default_path)
                user_input = input(
                    f"  Resource '{res.id}' path [{prompt_default}]: "
                ).strip()
                if user_input:
                    # User provided absolute or relative path
                    user_path = Path(user_input)
                    if user_path.is_absolute():
                        target_abs = user_path
                    else:
                        target_abs = (kit_root / user_path).resolve()
                    # Compute relative path from cypilot_dir for binding
                    target_rel = os.path.relpath(target_abs, cypilot_dir)
                    resource_bindings[res.id] = {"path": target_rel}
                    # @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-copy-resource
                    _copy_manifest_resource(kit_source, res, target_abs)
                    # @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-copy-resource
                    files_copied += 1
                    continue
            except (EOFError, KeyboardInterrupt):
                pass
        # @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-prompt-path

        # @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-default-path
        target_abs = (kit_root / res.default_path).resolve()
        # Store binding relative to cypilot_dir (supports .. for paths outside)
        binding_path = os.path.relpath(target_abs, cypilot_dir)
        resource_bindings[res.id] = {"path": binding_path}
        # @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-default-path

        # @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-copy-resource
        _copy_manifest_resource(kit_source, res, target_abs)
        # @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-copy-resource
        files_copied += 1
    # @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-foreach-resource

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-resolve-vars
    # Resolve {identifier} template variables in all copied kit files
    _resolve_template_variables(kit_root, resource_bindings)
    # @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-resolve-vars

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-register-bindings
    # Read version from source conf.toml if not provided
    if not kit_version:
        src_conf = kit_source / _KIT_CONF_FILE
        if src_conf.is_file():
            kit_version = _read_kit_version(src_conf)

    # Seed kit config files into config/ (only if missing)
    scripts_dir = kit_root / "scripts"
    if scripts_dir.is_dir():
        _seed_kit_config_files(scripts_dir, config_dir, {})

    # Register in core.toml with resource bindings
    _register_kit_in_core_toml(
        config_dir, kit_slug, kit_version, cypilot_dir,
        source=source, resources=resource_bindings,
    )
    # @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-register-bindings

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-collect-meta
    # Collect metadata for .gen/ aggregation
    meta = _collect_kit_metadata(kit_root, kit_slug)
    # @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-collect-meta

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-return
    return {
        "status": "PASS" if not errors else "WARN",
        "action": "installed",
        "kit": kit_slug,
        "version": kit_version,
        "files_copied": files_copied,
        "resource_bindings": {k: v["path"] for k, v in resource_bindings.items()},
        "errors": errors,
        "skill_nav": meta["skill_nav"],
        "agents_content": meta["agents_content"],
    }
    # @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-return


def _copy_manifest_resource(
    kit_source: Path,
    res: "ManifestResource",
    target_abs: Path,
) -> None:
    """Copy a single manifest resource from kit source to target path.

    Note: For directory resources, the existing target is removed before copying.
    Callers are responsible for ensuring *target_abs* is within the expected
    kit root directory (validated by ``validate_manifest`` for default paths;
    user-provided interactive paths are trusted as local CLI input).
    """
    src = kit_source / res.source
    if res.type == "directory":
        if target_abs.exists():
            shutil.rmtree(target_abs)
        shutil.copytree(src, target_abs)
    else:
        target_abs.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target_abs)


_TEMPLATE_EXTENSIONS = {".md", ".toml", ".txt", ".yaml", ".yml"}


def _resolve_template_variables(
    kit_root: Path,
    resource_bindings: Dict[str, Dict[str, str]],
) -> None:
    """Resolve ``{identifier}`` template variables in copied kit text files.

    Walks *kit_root* recursively and replaces ``{resource_id}`` placeholders
    with the resolved path from *resource_bindings* in all text files with
    supported extensions.
    """
    if not resource_bindings:
        return

    replacements = {f"{{{rid}}}": info["path"] for rid, info in resource_bindings.items()}

    for fpath in kit_root.rglob("*"):
        if not fpath.is_file() or fpath.suffix not in _TEMPLATE_EXTENSIONS:
            continue
        try:
            text = fpath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        new_text = text
        for pattern, value in replacements.items():
            new_text = new_text.replace(pattern, value)
        if new_text != text:
            fpath.write_text(new_text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Legacy Install Migration — auto-populate resource bindings from disk
# ---------------------------------------------------------------------------

# @cpt-algo:cpt-cypilot-algo-kit-manifest-legacy-migration:p1
def migrate_legacy_kit_to_manifest(
    kit_source: Path,
    cypilot_dir: Path,
    kit_slug: str,
    *,
    interactive: bool = True,
) -> Dict[str, Any]:
    """Migrate a legacy kit install to manifest-driven resource bindings.

    When ``cpt update`` runs and the kit source now contains ``manifest.toml``
    but ``core.toml`` has no ``[kits.{slug}.resources]``, this function
    auto-populates resource bindings from existing files on disk.

    For each manifest resource:
    - If the file/directory already exists at the expected path → register silently.
    - If it does not exist (truly new resource) → copy from source and register.

    Args:
        kit_source: Kit source directory (containing ``manifest.toml``).
        cypilot_dir: Resolved project cypilot directory.
        kit_slug: Kit identifier.
        interactive: If True and stdin is a tty, prompt for new resource paths.

    Returns:
        Dict with: status, kit, migrated_count, new_count, resource_bindings.
    """
    from ..utils.manifest import load_manifest, validate_manifest

    config_dir = cypilot_dir / "config"
    resource_bindings: Dict[str, Dict[str, str]] = {}
    migrated_count = 0  # existing files registered silently
    new_count = 0       # new files copied from source

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-read-manifest
    manifest = load_manifest(kit_source)
    if manifest is None:
        return {
            "status": "SKIP",
            "kit": kit_slug,
            "message": "No manifest.toml in kit source",
        }

    validation_errors = validate_manifest(manifest, kit_source)
    if validation_errors:
        return {
            "status": "FAIL",
            "kit": kit_slug,
            "errors": validation_errors,
        }
    # @cpt-end:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-read-manifest

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-read-root
    kit_data = _read_kits_from_core_toml(config_dir).get(kit_slug, {})
    kit_root_rel = kit_data.get("path", f"config/kits/{kit_slug}")
    kit_root = (cypilot_dir / kit_root_rel).resolve()
    # @cpt-end:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-read-root

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-foreach-resource
    for res in manifest.resources:
        # @cpt-begin:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-compute-path
        expected_path = kit_root / res.default_path
        # @cpt-end:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-compute-path

        # @cpt-begin:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-register-existing
        if expected_path.exists():
            # File/directory already on disk — register silently
            binding_path = os.path.relpath(expected_path, cypilot_dir)
            resource_bindings[res.id] = {"path": binding_path}
            migrated_count += 1
            continue
        # @cpt-end:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-register-existing

        # @cpt-begin:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-prompt-new
        # Truly new resource — copy from source and register
        target_abs = expected_path
        if interactive and res.user_modifiable and sys.stdin.isatty():
            try:
                user_input = input(
                    f"  New resource '{res.id}' path [{expected_path}]: "
                ).strip()
                if user_input:
                    user_path = Path(user_input)
                    if user_path.is_absolute():
                        target_abs = user_path
                    else:
                        target_abs = (kit_root / user_path).resolve()
            except (EOFError, KeyboardInterrupt):
                pass

        _copy_manifest_resource(kit_source, res, target_abs)
        binding_path = os.path.relpath(target_abs, cypilot_dir)
        resource_bindings[res.id] = {"path": binding_path}
        new_count += 1
        # @cpt-end:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-prompt-new
    # @cpt-end:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-foreach-resource

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-write-bindings
    # Write all resource bindings to core.toml [kits.{slug}.resources]
    _register_kit_in_core_toml(
        config_dir, kit_slug, "", cypilot_dir,
        resources=resource_bindings,
    )
    # Resolve template variables in kit files with new resource bindings
    _resolve_template_variables(kit_root, resource_bindings)
    # @cpt-end:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-write-bindings

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-return
    return {
        "status": "PASS",
        "kit": kit_slug,
        "migrated_count": migrated_count,
        "new_count": new_count,
        "resource_bindings": {k: v["path"] for k, v in resource_bindings.items()},
    }
    # @cpt-end:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-return


# ---------------------------------------------------------------------------
# Kit Install CLI
# ---------------------------------------------------------------------------

# @cpt-flow:cpt-cypilot-flow-kit-install-cli:p1
def cmd_kit_install(argv: List[str]) -> int:
    """Install a kit from GitHub or a local path.

    Delegates to install_kit() for the actual work, then regenerates
    .gen/ aggregates.

    Usage:
        cypilot kit install owner/repo[@version]   (GitHub, default)
        cypilot kit install --path /local/dir       (local directory)
    """
    # @cpt-begin:cpt-cypilot-flow-kit-install-cli:p1:inst-parse-args
    p = argparse.ArgumentParser(
        prog="kit install",
        description="Install a kit package from GitHub or a local directory",
    )
    p.add_argument(
        "source", nargs="?", default=None,
        help="GitHub source: owner/repo[@version] (e.g. cyberfabric/cyber-pilot-kit-sdlc@v1.0.0)",
    )
    p.add_argument(
        "--path", dest="local_path", default=None,
        help="Install from a local directory instead of GitHub",
    )
    p.add_argument("--force", action="store_true", help="Overwrite existing kit")
    p.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = p.parse_args(argv)

    if not args.source and not args.local_path:
        p.error("Provide a GitHub source (owner/repo) or --path for a local directory")
    if args.source and args.local_path:
        p.error("Cannot use both positional source and --path")
    # @cpt-end:cpt-cypilot-flow-kit-install-cli:p1:inst-parse-args

    # @cpt-begin:cpt-cypilot-flow-kit-install-cli:p1:inst-validate-source
    github_source = ""  # "github:owner/repo" for registration
    tmp_dir_to_clean: Optional[Path] = None

    if args.local_path:
        # Local directory source
        kit_source = Path(args.local_path).resolve()
        if not kit_source.is_dir():
            ui.result({
                "status": "FAIL",
                "message": f"Kit source directory not found: {kit_source}",
                "hint": "Provide a path to a valid kit directory",
            })
            return 2
    else:
        # GitHub source (default)
        try:
            owner, repo, version = _parse_github_source(args.source)
        except ValueError as exc:
            ui.result({
                "status": "FAIL",
                "message": str(exc),
                "hint": "Expected format: owner/repo or owner/repo@version",
            })
            return 2

        ui.step(f"Downloading {owner}/{repo}" + (f"@{version}" if version else " (latest)") + "...")
        try:
            kit_source, resolved_version = _download_kit_from_github(owner, repo, version)
            tmp_dir_to_clean = kit_source.parent
        except RuntimeError as exc:
            ui.result({
                "status": "FAIL",
                "message": str(exc),
            })
            return 1
    # @cpt-end:cpt-cypilot-flow-kit-install-cli:p1:inst-validate-source

    # @cpt-begin:cpt-cypilot-flow-kit-install-cli:p1:inst-read-slug-version
    if args.local_path:
        kit_slug = _read_kit_slug(kit_source) or kit_source.name
        kit_version = _read_kit_version(kit_source / _KIT_CONF_FILE) if (kit_source / _KIT_CONF_FILE).is_file() else ""
    else:
        kit_slug = _read_kit_slug(kit_source) or repo.removeprefix("cyber-pilot-kit-")
        kit_version = resolved_version or _read_kit_version(kit_source / _KIT_CONF_FILE) if (kit_source / _KIT_CONF_FILE).is_file() else resolved_version
        github_source = f"github:{owner}/{repo}"
        ui.substep(f"Resolved: {kit_slug}@{kit_version or '(dev)'}")
    # @cpt-end:cpt-cypilot-flow-kit-install-cli:p1:inst-read-slug-version

    try:
        # @cpt-begin:cpt-cypilot-flow-kit-install-cli:p1:inst-resolve-project
        resolved = _resolve_cypilot_dir()
        if resolved is None:
            return 1
        _, cypilot_dir = resolved
        config_kit_dir = cypilot_dir / "config" / "kits" / kit_slug
        # @cpt-end:cpt-cypilot-flow-kit-install-cli:p1:inst-resolve-project

        # @cpt-begin:cpt-cypilot-flow-kit-install-cli:p1:inst-check-existing
        if config_kit_dir.exists() and not args.force:
            ui.result(
                {
                    "status": "FAIL",
                    "kit": kit_slug,
                    "message": f"Kit '{kit_slug}' is already installed at {config_kit_dir}",
                    "hint": f"Use 'cpt kit update' to update, or 'cpt kit install {args.source or args.local_path} --force' to reinstall",
                },
                human_fn=lambda d: _human_kit_install(d),
            )
            return 2
        # @cpt-end:cpt-cypilot-flow-kit-install-cli:p1:inst-check-existing

        # @cpt-begin:cpt-cypilot-flow-kit-install-cli:p1:inst-dry-run
        if args.dry_run:
            ui.result({
                "status": "DRY_RUN",
                "kit": kit_slug,
                "version": kit_version,
                "source": github_source or kit_source.as_posix(),
                "target": config_kit_dir.as_posix(),
            })
            return 0
        # @cpt-end:cpt-cypilot-flow-kit-install-cli:p1:inst-dry-run

        # @cpt-begin:cpt-cypilot-flow-kit-install-cli:p1:inst-delegate-install
        result = install_kit(kit_source, cypilot_dir, kit_slug, kit_version, source=github_source, interactive=True)
        # @cpt-end:cpt-cypilot-flow-kit-install-cli:p1:inst-delegate-install

        # @cpt-begin:cpt-cypilot-flow-kit-install-cli:p1:inst-regen-gen
        regenerate_gen_aggregates(cypilot_dir)
        # @cpt-end:cpt-cypilot-flow-kit-install-cli:p1:inst-regen-gen

        # @cpt-begin:cpt-cypilot-flow-kit-install-cli:p1:inst-output-result
        output: Dict[str, Any] = {
            "status": result["status"],
            "action": result.get("action", "installed"),
            "kit": kit_slug,
            "version": kit_version,
            "files_written": result.get("files_copied", 0),
        }
        if github_source:
            output["source"] = github_source
        if result.get("errors"):
            output["errors"] = result["errors"]

        ui.result(output, human_fn=lambda d: _human_kit_install(d))
        return 0
        # @cpt-end:cpt-cypilot-flow-kit-install-cli:p1:inst-output-result

    finally:
        if tmp_dir_to_clean:
            shutil.rmtree(tmp_dir_to_clean, ignore_errors=True)

def _human_kit_install(data: dict) -> None:
    status = data.get("status", "")
    kit_slug = data.get("kit", "?")
    version = data.get("version", "?")
    action = data.get("action", "installed")

    ui.header("Kit Install")
    ui.detail("Kit", kit_slug)
    ui.detail("Version", str(version))
    ui.detail("Action", action)

    if status == "DRY_RUN":
        ui.detail("Source", data.get("source", "?"))
        ui.detail("Target", data.get("target", "?"))
        ui.success("Dry run — no files written.")
        ui.blank()
        return

    fw = data.get("files_written", 0)
    kinds = data.get("artifact_kinds", [])
    ui.detail("Files written", str(fw))
    if kinds:
        ui.detail("Artifact kinds", ", ".join(kinds))

    errs = data.get("errors", [])
    if errs:
        ui.blank()
        for e in errs:
            ui.warn(str(e))

    if status == "PASS":
        ui.success(f"Kit '{kit_slug}' installed.")
    elif status == "FAIL":
        msg = data.get("message", "")
        hint = data.get("hint", "")
        ui.error(msg or "Install failed.")
        if hint:
            ui.hint(hint)
    else:
        ui.info(f"Status: {status}")
    ui.blank()

# ---------------------------------------------------------------------------
# Kit Update
# ---------------------------------------------------------------------------

# @cpt-flow:cpt-cypilot-flow-kit-update-cli:p1
def cmd_kit_update(argv: List[str]) -> int:
    """Update installed kits from their registered sources or a local path.

    Without arguments, updates all installed kits that have a registered
    source in core.toml.  With a slug, updates only that kit.
    With --path, updates from a local directory.

    Usage:
        cypilot kit update                          (all kits from sources)
        cypilot kit update sdlc                     (specific kit from source)
        cypilot kit update --path /local/dir        (from local directory)
    """
    # @cpt-begin:cpt-cypilot-flow-kit-update-cli:p1:inst-parse-args
    p = argparse.ArgumentParser(
        prog="kit update",
        description="Update installed kits from GitHub sources or a local directory",
    )
    p.add_argument(
        "slug", nargs="?", default=None,
        help="Kit slug to update (default: all installed kits)",
    )
    p.add_argument(
        "--path", dest="local_path", default=None,
        help="Update from a local directory instead of registered source",
    )
    p.add_argument("--force", action="store_true",
                   help="Skip version check and force update")
    p.add_argument("--dry-run", action="store_true", help="Show what would be done")
    p.add_argument("--no-interactive", action="store_true",
                   help="Disable interactive prompts (auto-decline changes)")
    p.add_argument("-y", "--yes", action="store_true",
                   help="Auto-approve all prompts (no interaction)")
    args = p.parse_args(argv)
    # @cpt-end:cpt-cypilot-flow-kit-update-cli:p1:inst-parse-args

    # @cpt-begin:cpt-cypilot-flow-kit-update-cli:p1:inst-resolve-project
    resolved = _resolve_cypilot_dir()
    if resolved is None:
        return 1
    _, cypilot_dir = resolved
    config_dir = cypilot_dir / "config"
    # @cpt-end:cpt-cypilot-flow-kit-update-cli:p1:inst-resolve-project

    interactive = not args.no_interactive and sys.stdin.isatty()

    # @cpt-begin:cpt-cypilot-flow-kit-update-cli:p1:inst-validate-source
    # Build list of (slug, source_dir, github_source, tmp_dir) to update
    update_targets: List[Tuple[str, Path, str, Optional[Path]]] = []

    if args.local_path:
        # Local directory source
        kit_source = Path(args.local_path).resolve()
        if not kit_source.is_dir():
            ui.result({
                "status": "FAIL",
                "message": f"Kit source directory not found: {kit_source}",
                "hint": "Provide a path to a valid kit directory",
            })
            return 2
    else:
        # Read kits from core.toml
        kits_map = _read_kits_from_core_toml(config_dir)
        if not kits_map:
            ui.result({
                "status": "FAIL",
                "message": "No kits registered in core.toml",
                "hint": "Install a kit first: cpt kit install owner/repo",
            })
            return 2

        # Filter to specific slug if provided
        if args.slug:
            if args.slug not in kits_map:
                ui.result({
                    "status": "FAIL",
                    "message": f"Kit '{args.slug}' not found in core.toml",
                    "hint": f"Registered kits: {', '.join(kits_map.keys())}",
                })
                return 2
            kits_map = {args.slug: kits_map[args.slug]}
    # @cpt-end:cpt-cypilot-flow-kit-update-cli:p1:inst-validate-source

    # @cpt-begin:cpt-cypilot-flow-kit-update-cli:p1:inst-read-slug
    if args.local_path:
        kit_slug = args.slug or _read_kit_slug(kit_source) or kit_source.name
        update_targets.append((kit_slug, kit_source, "", None))
    else:
        # Resolve GitHub sources
        for slug, kit_data in kits_map.items():
            source_str = kit_data.get("source", "")
            if not source_str:
                ui.warn(f"Kit '{slug}' has no registered source — skipping")
                continue

            if source_str.startswith("github:"):
                owner_repo = source_str.removeprefix("github:")
                try:
                    owner, repo, version = _parse_github_source(owner_repo)
                except ValueError as exc:
                    ui.warn(f"Kit '{slug}': invalid source '{source_str}': {exc}")
                    continue

                ui.step(f"Downloading {owner}/{repo}...")
                try:
                    kit_source_dir, resolved_version = _download_kit_from_github(owner, repo, version)
                    update_targets.append((slug, kit_source_dir, source_str, kit_source_dir.parent))
                except RuntimeError as exc:
                    ui.warn(f"Kit '{slug}': download failed: {exc}")
                    continue
            else:
                ui.warn(f"Kit '{slug}': unsupported source type '{source_str}' — skipping")

        if not update_targets:
            ui.result({
                "status": "FAIL",
                "message": "No kits to update (no valid sources found)",
            })
            return 2
    # @cpt-end:cpt-cypilot-flow-kit-update-cli:p1:inst-read-slug

    # @cpt-begin:cpt-cypilot-flow-kit-update-cli:p1:inst-delegate-update
    all_results: List[Dict[str, Any]] = []
    errors: List[str] = []

    for kit_slug, kit_source, github_source, tmp_dir in update_targets:
        try:
            # @cpt-begin:cpt-cypilot-flow-kit-update-cli:p1:inst-legacy-migration
            # Legacy manifest migration is handled inside update_kit() when
            # source has manifest.toml and kit lacks resource bindings.
            kit_r = update_kit(
                kit_slug, kit_source, cypilot_dir,
                dry_run=args.dry_run,
                interactive=interactive,
                auto_approve=args.yes,
                force=args.force,
                source=github_source,
            )
            # @cpt-end:cpt-cypilot-flow-kit-update-cli:p1:inst-legacy-migration
        except Exception as exc:
            kit_r = {"kit": kit_slug, "version": {"status": "ERROR"}, "gen": {}}
            errors.append(f"{kit_slug}: {exc}")
        finally:
            if tmp_dir:
                shutil.rmtree(tmp_dir, ignore_errors=True)

        ver = kit_r.get("version", {})
        ver_status = ver.get("status", "") if isinstance(ver, dict) else str(ver)
        gen = kit_r.get("gen", {})
        accepted = gen.get("accepted_files", []) if isinstance(gen, dict) else []
        declined = kit_r.get("gen_rejected", [])
        files_written = gen.get("files_written", 0) if isinstance(gen, dict) else 0

        all_results.append({
            "kit": kit_slug,
            "action": ver_status,
            "accepted": accepted,
            "declined": declined,
            "files_written": files_written,
        })
    # @cpt-end:cpt-cypilot-flow-kit-update-cli:p1:inst-delegate-update

    # @cpt-begin:cpt-cypilot-flow-kit-update-cli:p1:inst-regen-gen
    if not args.dry_run:
        regenerate_gen_aggregates(cypilot_dir)
    # @cpt-end:cpt-cypilot-flow-kit-update-cli:p1:inst-regen-gen

    # @cpt-begin:cpt-cypilot-flow-kit-update-cli:p1:inst-format-output
    n_updated = sum(1 for r in all_results if r["action"] not in ("current", "dry_run", "ERROR"))
    output: Dict[str, Any] = {
        "status": "PASS" if not errors else "WARN",
        "kits_updated": n_updated,
        "results": all_results,
    }
    if errors:
        output["errors"] = errors
    if n_updated == 0 and not errors:
        output["message"] = "All kits are up to date"

    ui.result(output, human_fn=lambda d: _human_kit_update(d))
    return 0
    # @cpt-end:cpt-cypilot-flow-kit-update-cli:p1:inst-format-output

def _human_kit_update(data: dict) -> None:
    status = data.get("status", "")
    n = data.get("kits_updated", 0)

    ui.header("Kit Update")
    ui.detail("Kits updated", str(n))

    for r in data.get("results", []):
        kit_slug = r.get("kit", "?")
        action = r.get("action", "?")
        accepted = r.get("accepted", [])
        declined = r.get("declined", [])
        unchanged = r.get("unchanged", 0)
        parts = [f"{kit_slug}: {action}"]
        if accepted:
            parts.append(f"{len(accepted)} accepted")
        if declined:
            parts.append(f"{len(declined)} declined")
        if unchanged:
            parts.append(f"{unchanged} unchanged")
        ui.step("  ".join(parts))
        for fp in accepted:
            ui.substep(f"  ~ {fp}")
        for fp in declined:
            ui.substep(f"  ✗ {fp} (declined)")

    errs = data.get("errors", [])
    if errs:
        ui.blank()
        for e in errs:
            ui.warn(str(e))

    if status == "PASS":
        ui.success("Kit update complete.")
    elif status == "WARN":
        ui.warn("Kit update finished with warnings.")
    else:
        ui.info(f"Status: {status}")
    ui.blank()

# ---------------------------------------------------------------------------
# Kit Migrate — conf.toml helpers
# ---------------------------------------------------------------------------

def _read_conf_version(conf_path: Path) -> int:
    """Read top-level 'version' from conf.toml. Returns 0 if missing."""
    # @cpt-begin:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-conf-version
    if not conf_path.is_file():
        return 0
    try:
        import tomllib
        with open(conf_path, "rb") as f:
            data = tomllib.load(f)
        ver = data.get("version")
        return int(ver) if ver is not None else 0
    except Exception:
        return 0
    # @cpt-end:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-conf-version

# ---------------------------------------------------------------------------
# Layout migration — old (kits/ + .gen/kits/) → new (config/kits/ only, no kits/)
# @cpt-algo:cpt-cypilot-algo-version-config-layout-restructure:p1
# ---------------------------------------------------------------------------

def _detect_and_migrate_layout(
    cypilot_dir: Path,
    *,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Detect old directory layout and migrate to the new flat model.

    Handles two legacy layouts:

    Layout A (oldest):
        config/kits/{slug}/blueprints/  — user blueprints
        .gen/kits/{slug}/               — generated outputs
        kits/{slug}/                    — reference copies

    Layout B (intermediate):
        kits/{slug}/blueprints/         — user blueprints
        kits/{slug}/conf.toml           — kit config
        config/kits/{slug}/             — generated outputs

    New layout (direct file packages):
        config/kits/{slug}/             — all kit content (no blueprints)
        (no kits/ directory)

    Migration merges non-blueprint content into config/kits/{slug}/,
    updates core.toml paths, then removes kits/ and .gen/kits/.

    Returns dict with migrated kit slugs or empty if no migration needed.
    """
    config_kits = cypilot_dir / "config" / "kits"
    gen_kits = cypilot_dir / ".gen" / "kits"
    kits_dir = cypilot_dir / "kits"

    # Detect: old layout exists when kits/ directory is present
    has_kits_dir = kits_dir.is_dir() and any(kits_dir.iterdir())
    has_gen_kits = gen_kits.is_dir() and any(gen_kits.iterdir())
    if not has_kits_dir and not has_gen_kits:
        return {}

    migrated: Dict[str, Any] = {}
    backup_dir = cypilot_dir / ".layout_backup"

    # ── Migrate kits/{slug}/ content into config/kits/{slug}/ ──────────
    if has_kits_dir:
        for kit_dir in sorted(kits_dir.iterdir()):
            if not kit_dir.is_dir():
                continue
            slug = kit_dir.name
            config_kit = config_kits / slug

            if dry_run:
                migrated[slug] = "would_migrate"
                continue

            try:
                # @cpt-begin:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-backup
                # Backup
                kit_backup = backup_dir / slug
                if kit_backup.exists():
                    shutil.rmtree(kit_backup)
                kit_backup.mkdir(parents=True, exist_ok=True)
                shutil.copytree(kit_dir, kit_backup / "user_kit")
                # @cpt-end:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-backup

                # Copy non-blueprint content from kits/{slug}/ → config/kits/{slug}/
                config_kit.mkdir(parents=True, exist_ok=True)
                for item in kit_dir.iterdir():
                    if item.name in ("blueprints", "blueprint_hashes.toml", "__pycache__", ".prev"):
                        continue  # skip legacy artifacts
                    dst = config_kit / item.name
                    if item.is_dir():
                        if dst.exists():
                            shutil.rmtree(dst)
                        shutil.copytree(item, dst)
                    elif not dst.exists():
                        # Don't overwrite existing config/kits/ files
                        shutil.copy2(item, dst)

                migrated[slug] = "migrated"
            except Exception as exc:
                # @cpt-begin:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-rollback
                # Rollback
                kit_backup = backup_dir / slug
                if kit_backup.is_dir() and (kit_backup / "user_kit").is_dir():
                    target = kits_dir / slug
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.copytree(kit_backup / "user_kit", target)
                migrated[slug] = f"FAILED: {exc}"
                # @cpt-end:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-rollback

    # @cpt-begin:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-move-gen
    # ── Migrate .gen/kits/{slug}/ into config/kits/{slug}/ ─────────────
    if has_gen_kits:
        for gen_kit in sorted(gen_kits.iterdir()):
            if not gen_kit.is_dir():
                continue
            slug = gen_kit.name
            config_kit = config_kits / slug

            if dry_run:
                migrated.setdefault(slug, "would_migrate")
                continue

            try:
                config_kit.mkdir(parents=True, exist_ok=True)
                for item in gen_kit.iterdir():
                    dst = config_kit / item.name
                    if item.is_dir():
                        if not dst.exists():
                            shutil.copytree(item, dst)
                    elif not dst.exists():
                        shutil.copy2(item, dst)
                migrated.setdefault(slug, "migrated")
            except Exception as exc:
                migrated[slug] = f"FAILED: {exc}"
    # @cpt-end:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-move-gen

    if dry_run:
        return migrated

    # @cpt-begin:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-update-core
    # ── Update core.toml kit paths ─────────────────────────────────────
    config_dir = cypilot_dir / "config"
    core_toml = config_dir / "core.toml"
    if core_toml.is_file():
        import tomllib
        with open(core_toml, "rb") as f:
            data = tomllib.load(f)
        kits_conf = data.get("kits", {})
        updated = False
        for kit_id, kit_entry in kits_conf.items():
            if isinstance(kit_entry, dict):
                old_path = kit_entry.get("path", "")
                if old_path.startswith(".gen/kits/") or old_path.startswith("kits/"):
                    slug = old_path.rsplit("/", 1)[-1]
                    kit_entry["path"] = f"config/kits/{slug}"
                    updated = True
        if updated:
            from ..utils import toml_utils
            toml_utils.dump(data, core_toml, header_comment="Cypilot project configuration")
    # @cpt-end:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-update-core

    # @cpt-begin:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-remove-refs
    # ── Remove legacy directories ──────────────────────────────────────
    has_failures = any(isinstance(s, str) and s.startswith("FAILED") for s in migrated.values())

    if not has_failures and kits_dir.is_dir():
        shutil.rmtree(kits_dir)

    # @cpt-end:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-remove-refs

    # @cpt-begin:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-clean-gen
    if gen_kits.is_dir():
        shutil.rmtree(gen_kits, ignore_errors=True)
    # @cpt-end:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-clean-gen

    # Clean up backups for successful migrations; preserve failed ones
    if backup_dir.is_dir():
        for slug, status in migrated.items():
            kit_backup = backup_dir / slug
            if status == "migrated" and kit_backup.is_dir():
                shutil.rmtree(kit_backup, ignore_errors=True)
        try:
            backup_dir.rmdir()
        except OSError:
            pass

    return migrated


# @cpt-dod:cpt-cypilot-dod-kit-update:p1
# @cpt-algo:cpt-cypilot-algo-kit-update:p1
def update_kit(
    kit_slug: str,
    source_dir: Path,
    cypilot_dir: Path,
    *,
    dry_run: bool = False,
    interactive: bool = True,
    auto_approve: bool = False,
    force: bool = False,
    source: str = "",
) -> Dict[str, Any]:
    """Full update cycle for a single kit.

    Kits are direct file packages.  On first install the kit content is
    copied wholesale.  On subsequent runs a file-level diff is shown and
    the user decides per-file.

    Args:
        kit_slug: Kit identifier (e.g. "sdlc").
        source_dir: New kit data (e.g. cache/kits/{slug}/ or local dir).
        cypilot_dir: Project adapter directory.
        dry_run: If True, don't write files.
        interactive: If True, prompt user for confirmation before writing.
        auto_approve: If True, skip all prompts (accept all).
        force: If True, skip version check and force-overwrite all files.
        source: Source identifier for registration (e.g. "github:owner/repo").

    Layout:
        config/kits/{slug}/     — installed kit files (user-editable)

    Returns dict consumed by update.py / cmd_kit_update:
        kit, version, gen, skill_nav?, agents_content?, gen_errors?
    """
    # @cpt-begin:cpt-cypilot-algo-kit-update:p1:inst-resolve-config
    config_dir = cypilot_dir / "config"
    config_kits_dir = config_dir / "kits"
    config_kit_dir = config_kits_dir / kit_slug

    result: Dict[str, Any] = {"kit": kit_slug}
    # @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-resolve-config

    # @cpt-begin:cpt-cypilot-algo-kit-update:p1:inst-dry-run-check
    if dry_run:
        result["version"] = {"status": "dry_run"}
        result["gen"] = "dry_run"
        return result
    # @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-dry-run-check

    # @cpt-begin:cpt-cypilot-algo-kit-update:p1:inst-read-source-version
    # Read source version
    src_conf = source_dir / _KIT_CONF_FILE
    source_version = _read_kit_version(src_conf) if src_conf.is_file() else ""
    # @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-read-source-version

    # @cpt-begin:cpt-cypilot-algo-kit-update:p1:inst-version-check
    # ── Version check (skip update if same version, unless force) ────────
    if not force and source_version and config_kit_dir.is_dir():
        installed_version = _read_kit_version_from_core(config_dir, kit_slug)
        if installed_version and installed_version == source_version:
            result["version"] = {"status": "current"}
            result["gen"] = {"files_written": 0}
            # Still collect metadata for .gen/ aggregation
            meta = _collect_kit_metadata(config_kit_dir, kit_slug)
            if meta["skill_nav"]:
                result["skill_nav"] = meta["skill_nav"]
            if meta["agents_content"]:
                result["agents_content"] = meta["agents_content"]
            return result
    # @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-version-check

    # @cpt-begin:cpt-cypilot-algo-kit-update:p1:inst-legacy-manifest-migration
    # Before file-level diff, check for legacy → manifest migration
    from ..utils.manifest import load_manifest as _load_manifest
    _manifest = _load_manifest(source_dir)
    if _manifest is not None and config_kit_dir.is_dir():
        _kit_data = _read_kits_from_core_toml(config_dir).get(kit_slug, {})
        if not _kit_data.get("resources"):
            _mig_result = migrate_legacy_kit_to_manifest(
                source_dir, cypilot_dir, kit_slug, interactive=interactive,
            )
            if _mig_result.get("status") == "FAIL":
                sys.stderr.write(
                    f"kit: warning: manifest migration for '{kit_slug}' failed: "
                    f"{_mig_result.get('errors', [])}\n"
                )
    # @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-legacy-manifest-migration

    # @cpt-begin:cpt-cypilot-algo-kit-update:p1:inst-resolve-resource-bindings
    # Build source-to-resource-id mapping and resolve resource bindings
    _resource_bindings = None
    _source_to_resource_id = None
    _resource_info = None
    if _manifest is not None:
        from ..utils.manifest import (
            build_source_to_resource_mapping,
            resolve_resource_bindings,
        )
        _source_to_resource_id, _resource_info = build_source_to_resource_mapping(source_dir)
        _resource_bindings = resolve_resource_bindings(config_dir, kit_slug, cypilot_dir)
    # @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-resolve-resource-bindings

    # @cpt-begin:cpt-cypilot-algo-kit-update:p1:inst-first-install
    # ── 1. First-install or file-level update ────────────────────────
    if not config_kit_dir.is_dir():
        # First install — copy all kit content
        copy_actions = _copy_kit_content(source_dir, config_kit_dir)
        result["version"] = {"status": "created"}
        result["gen"] = {
            "files_written": sum(1 for v in copy_actions.values() if v == "copied"),
        }

        # Seed kit config files into config/ (only if missing)
        scripts_dir = config_kit_dir / "scripts"
        if scripts_dir.is_dir():
            _seed_kit_config_files(scripts_dir, config_dir, {})

        # Register in core.toml (single source of truth for installed version)
        _register_kit_in_core_toml(config_dir, kit_slug, source_version, cypilot_dir)
    # @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-first-install
    else:
        # @cpt-begin:cpt-cypilot-algo-kit-update:p1:inst-file-level-diff
        # Existing kit — file-level diff update
        from ..utils.diff_engine import file_level_kit_update

        report = file_level_kit_update(
            source_dir, config_kit_dir,
            interactive=interactive,
            auto_approve=auto_approve,
            content_dirs=_KIT_CONTENT_DIRS,
            content_files=_KIT_CONTENT_FILES,
            resource_bindings=_resource_bindings,
            source_to_resource_id=_source_to_resource_id,
            resource_info=_resource_info,
        )
        accepted = report.get("accepted", [])
        declined = report.get("declined", [])

        # Determine version status
        if accepted:
            ver_status = "updated"
        elif declined:
            ver_status = "partial"
        else:
            ver_status = "current"

        result["version"] = {"status": ver_status}
        result["gen"] = {
            "files_written": len(accepted),
            "accepted_files": accepted,
        }
        if declined:
            result["gen_rejected"] = declined
        # @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-file-level-diff

        # @cpt-begin:cpt-cypilot-algo-kit-update:p1:inst-update-core-toml
        # Update version in core.toml from source (always, even if some files declined)
        if source_version:
            _register_kit_in_core_toml(config_dir, kit_slug, source_version, cypilot_dir, source=source)
        # @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-update-core-toml

    # @cpt-begin:cpt-cypilot-algo-kit-update:p1:inst-collect-metadata
    # ── 2. Collect metadata for .gen/ aggregation ────────────────────
    meta = _collect_kit_metadata(config_kit_dir, kit_slug)
    if meta["skill_nav"]:
        result["skill_nav"] = meta["skill_nav"]
    if meta["agents_content"]:
        result["agents_content"] = meta["agents_content"]
    # @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-collect-metadata

    # @cpt-begin:cpt-cypilot-algo-kit-update:p1:inst-return-result
    return result
    # @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-return-result

def cmd_kit_migrate(argv: List[str]) -> int:
    """Deprecated — use 'cypilot kit update <path>' instead.

    The migrate command was part of the blueprint-based three-way merge system
    which has been removed.  File-level updates are now handled by 'kit update'.
    """
    sys.stderr.write(
        "WARNING: 'cypilot kit migrate' is deprecated.\n"
        "         Use 'cypilot kit update <path>' instead.\n"
    )
    return 1

# ---------------------------------------------------------------------------
# Kit CLI dispatcher (handles `cypilot kit <subcommand>`)
# ---------------------------------------------------------------------------

# @cpt-flow:cpt-cypilot-flow-kit-dispatch:p1
def cmd_kit(argv: List[str]) -> int:
    """Kit management command dispatcher.

    Usage: cypilot kit <install|update|validate|migrate> [options]
    """
    # @cpt-begin:cpt-cypilot-flow-kit-dispatch:p1:inst-parse-subcmd
    if not argv:
        ui.result({"status": "ERROR", "message": "Missing kit subcommand", "subcommands": ["install", "update", "validate", "migrate"]})
        return 1

    subcmd = argv[0]
    rest = argv[1:]
    # @cpt-end:cpt-cypilot-flow-kit-dispatch:p1:inst-parse-subcmd

    # @cpt-begin:cpt-cypilot-flow-kit-dispatch:p1:inst-route
    if subcmd == "install":
        return cmd_kit_install(rest)
    elif subcmd == "update":
        return cmd_kit_update(rest)
    elif subcmd == "validate":
        from .validate_kits import cmd_validate_kits
        return cmd_validate_kits(rest)
    elif subcmd == "migrate":
        return cmd_kit_migrate(rest)
    else:
        ui.result({"status": "ERROR", "message": f"Unknown kit subcommand: {subcmd}", "subcommands": ["install", "update", "validate", "migrate"]})
        return 1
    # @cpt-end:cpt-cypilot-flow-kit-dispatch:p1:inst-route

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_kits_from_core_toml(config_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Read all kit entries from config/core.toml [kits] section.

    Returns dict of {slug: {format, path, source?, version?}}.
    """
    core_toml = config_dir / "core.toml"
    if not core_toml.is_file():
        return {}
    try:
        import tomllib
        with open(core_toml, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return {}
    kits = data.get("kits", {})
    if not isinstance(kits, dict):
        return {}
    return {k: v for k, v in kits.items() if isinstance(v, dict)}


# @cpt-algo:cpt-cypilot-algo-kit-config-helpers:p1
def _read_kit_slug(kit_source: Path) -> str:
    """Read kit slug from source conf.toml. Returns '' if not found."""
    # @cpt-begin:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-slug
    conf_toml = kit_source / "conf.toml"
    if not conf_toml.is_file():
        return ""
    try:
        import tomllib
        with open(conf_toml, "rb") as f:
            data = tomllib.load(f)
        slug = data.get("slug")
        if isinstance(slug, str) and slug.strip():
            return slug.strip()
    except Exception as exc:
        sys.stderr.write(f"kit: warning: cannot read {conf_toml}: {exc}\n")
    return ""
    # @cpt-end:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-slug

def _read_kit_version_from_core(config_dir: Path, kit_slug: str) -> str:
    """Read installed kit version from config/core.toml [kits.{slug}].version."""
    # @cpt-begin:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-version-from-core
    core_toml = config_dir / "core.toml"
    if not core_toml.is_file():
        return ""
    try:
        import tomllib
        with open(core_toml, "rb") as f:
            data = tomllib.load(f)
        kit_entry = data.get("kits", {}).get(kit_slug, {})
        ver = kit_entry.get("version")
        if ver is not None:
            return str(ver)
    except Exception as exc:
        sys.stderr.write(f"kit: warning: cannot read version for '{kit_slug}' from {core_toml}: {exc}\n")
    return ""
    # @cpt-end:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-version-from-core

def _read_kit_version(conf_path: Path) -> str:
    """Read kit version from conf.toml."""
    # @cpt-begin:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-kit-version
    try:
        import tomllib
        with open(conf_path, "rb") as f:
            data = tomllib.load(f)
        ver = data.get("version")
        if ver is not None:
            return str(ver)
    except Exception as exc:
        sys.stderr.write(f"kit: warning: cannot read version from {conf_path}: {exc}\n")
    return ""
    # @cpt-end:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-kit-version

def _register_kit_in_core_toml(
    config_dir: Path,
    kit_slug: str,
    kit_version: str,
    cypilot_dir: Path,
    source: str = "",
    resources: Optional[Dict[str, Dict[str, str]]] = None,
) -> None:
    """Register or update a kit entry in config/core.toml."""
    # @cpt-begin:cpt-cypilot-algo-kit-config-helpers:p1:inst-register-core
    core_toml = config_dir / "core.toml"
    if not core_toml.is_file():
        return

    try:
        import tomllib
        with open(core_toml, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return

    kits = data.setdefault("kits", {})
    # Merge into existing entry to preserve fields like 'source'
    existing = kits.get(kit_slug, {})
    if not isinstance(existing, dict):
        existing = {}
    existing["format"] = "Cypilot"
    if not existing.get("path"):
        existing["path"] = f"config/kits/{kit_slug}"
    if source:
        existing["source"] = source
    if kit_version:
        existing["version"] = kit_version
    if resources is not None:
        existing["resources"] = resources
    kits[kit_slug] = existing

    # Write back using our TOML serializer
    try:
        from ..utils import toml_utils
        toml_utils.dump(data, core_toml, header_comment="Cypilot project configuration")
    except Exception as exc:
        sys.stderr.write(f"kit: warning: failed to register {kit_slug} in {core_toml}: {exc}\n")
    # @cpt-end:cpt-cypilot-algo-kit-config-helpers:p1:inst-register-core
