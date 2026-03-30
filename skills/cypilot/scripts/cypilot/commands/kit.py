"""
Kit Management Commands

Provides CLI handlers for kit install and kit update.
Kits are direct file packages — no blueprint processing or generation.
"""

# @cpt-algo:cpt-cypilot-algo-kit-github-helpers:p1
# @cpt-begin:cpt-cypilot-algo-kit-github-helpers:p1:inst-kit-imports
import argparse
import json
import os
import shutil
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Dict, List, Optional, Tuple

from ..utils.ui import ui
from ..utils.whatsnew import show_kit_whatsnew
# @cpt-end:cpt-cypilot-algo-kit-github-helpers:p1:inst-kit-imports


# ---------------------------------------------------------------------------
# GitHub source helpers
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-kit-github-helpers:p1:inst-github-headers
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
# @cpt-end:cpt-cypilot-algo-kit-github-helpers:p1:inst-github-headers


# @cpt-begin:cpt-cypilot-algo-kit-github-helpers:p1:inst-parse-source
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
# @cpt-end:cpt-cypilot-algo-kit-github-helpers:p1:inst-parse-source


_GITHUB_TARBALL_MAX_MEMBERS = 4096
_GITHUB_TARBALL_MAX_TOTAL_SIZE = 512 * 1024 * 1024
_GITHUB_TARBALL_MAX_EXPANSION_RATIO = 200


def _validate_tar_archive_before_extract(
    tar: tarfile.TarFile,
    tar_path: Path,
    tmp_dir: Path,
) -> None:
    tmp_dir_resolved = tmp_dir.resolve()
    total_size = 0
    member_count = 0

    while True:
        member = tar.next()
        if member is None:
            break
        member_count += 1
        if member_count > _GITHUB_TARBALL_MAX_MEMBERS:
            raise RuntimeError(
                "Archive extraction blocked: too many archive entries "
                f"(>{_GITHUB_TARBALL_MAX_MEMBERS})"
            )
        member_path = (tmp_dir / member.name).resolve()
        if not member_path.is_relative_to(tmp_dir_resolved):
            raise RuntimeError(
                f"Unsafe path in archive: {member.name!r}"
            )
        if member.isfile():
            total_size += member.size
            if total_size > _GITHUB_TARBALL_MAX_TOTAL_SIZE:
                raise RuntimeError(
                    "Archive extraction blocked: total extracted size exceeds "
                    f"limit ({total_size} > {_GITHUB_TARBALL_MAX_TOTAL_SIZE} bytes)"
                )

    archive_size = tar_path.stat().st_size
    if total_size > 0 and archive_size <= 0:
        raise RuntimeError(
            "Archive extraction blocked: invalid compressed archive size "
            f"({archive_size} bytes)"
        )
    if archive_size > 0 and total_size > archive_size * _GITHUB_TARBALL_MAX_EXPANSION_RATIO:
        raise RuntimeError(
            "Archive extraction blocked: suspicious compression expansion ratio "
            f"({total_size}/{archive_size} > {_GITHUB_TARBALL_MAX_EXPANSION_RATIO}x)"
        )


# @cpt-begin:cpt-cypilot-algo-kit-github-helpers:p1:inst-download
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

    # Extract — validate member paths to prevent zip-slip (S5042), then use
    # the built-in ``filter="data"`` safeguard for defence-in-depth.
    try:
        with tarfile.open(tar_path, "r:gz") as tar:
            _validate_tar_archive_before_extract(tar, tar_path, tmp_dir)
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=tmp_dir, filter="data")  # noqa: S202
    except RuntimeError:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise
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
# @cpt-end:cpt-cypilot-algo-kit-github-helpers:p1:inst-download


# @cpt-begin:cpt-cypilot-algo-kit-github-helpers:p1:inst-resolve-release
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
# @cpt-end:cpt-cypilot-algo-kit-github-helpers:p1:inst-resolve-release

# ---------------------------------------------------------------------------
# Config seeding — copy default .toml configs from kit scripts to config/
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-kit-content-mgmt:p1:inst-content-constants
# Directories and files that constitute kit content (copied to config/kits/{slug}/)
_KIT_CONTENT_DIRS = ("artifacts", "codebase", "scripts", "workflows")
_KIT_SKILL_FILE = "SKILL.md"
_KIT_AGENTS_FILE = "AGENTS.md"
_KIT_CONTENT_FILES = ("constraints.toml", _KIT_SKILL_FILE, _KIT_AGENTS_FILE)
# Infrastructure file — copied but not subject to interactive diff
_KIT_CONF_FILE = "conf.toml"
_KIT_CORE_TOML = "core.toml"

_CONFIG_EXTENSIONS = {".toml"}
# @cpt-end:cpt-cypilot-algo-kit-content-mgmt:p1:inst-content-constants

# @cpt-begin:cpt-cypilot-algo-kit-content-mgmt:p1:inst-seed-configs
def _seed_kit_config_files(
    gen_scripts_dir: Path,
    config_dir: Path,
    actions: Dict[str, str],
) -> None:
    """Copy top-level .toml files from generated scripts into config/ if missing.

    Only seeds files that don't already exist in config/ — never overwrites
    user-editable config.
    """
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

# @cpt-begin:cpt-cypilot-algo-kit-config-helpers:p1:inst-resolve-cypilot-dir
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
# @cpt-end:cpt-cypilot-algo-kit-config-helpers:p1:inst-resolve-cypilot-dir

# ---------------------------------------------------------------------------
# Kit content helpers — copy specific dirs/files, collect metadata for .gen/
# ---------------------------------------------------------------------------

# @cpt-algo:cpt-cypilot-algo-kit-content-mgmt:p1
# @cpt-begin:cpt-cypilot-algo-kit-content-mgmt:p1:inst-copy-content
def _copy_kit_content(
    kit_source: Path,
    config_kit_dir: Path,
) -> Dict[str, str]:
    """Copy kit content items from *kit_source* → *config_kit_dir*.

    Copies only the directories listed in ``_KIT_CONTENT_DIRS``, the files
    listed in ``_KIT_CONTENT_FILES``, and the infra ``_KIT_CONF_FILE``.
    Returns a dict of ``{item: action}`` entries.
    """
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


# @cpt-begin:cpt-cypilot-algo-kit-content-mgmt:p1:inst-collect-metadata-fn
def _normalize_path_string(path_value: str) -> str:
    normalized = PurePosixPath(path_value.strip().replace("\\", "/")).as_posix()
    return "" if normalized == "." else normalized


def _is_windows_absolute_path(registered_kit_path: str) -> bool:
    if not registered_kit_path:
        return False
    normalized = _normalize_path_string(registered_kit_path)
    return PureWindowsPath(normalized).is_absolute()


def _is_posix_absolute_path(registered_kit_path: str) -> bool:
    if not registered_kit_path:
        return False
    normalized = _normalize_path_string(registered_kit_path)
    return PurePosixPath(normalized).is_absolute()


def _is_registered_kit_path_absolute(registered_kit_path: str) -> bool:
    if not registered_kit_path:
        return False
    return (
        _is_posix_absolute_path(registered_kit_path)
        or _is_windows_absolute_path(registered_kit_path)
    )


def _resolve_registered_kit_dir(
    cypilot_dir: Path,
    registered_kit_path: str,
) -> Optional[Path]:
    normalized = _normalize_path_string(registered_kit_path)
    if not normalized:
        return cypilot_dir.resolve()
    is_windows_absolute = _is_windows_absolute_path(registered_kit_path)
    is_posix_absolute = _is_posix_absolute_path(registered_kit_path)
    if os.name == "nt":
        if is_windows_absolute:
            return Path(normalized).resolve()
        if is_posix_absolute:
            return None
    else:
        if is_posix_absolute:
            return Path(normalized).resolve()
        if is_windows_absolute:
            return None
    return (cypilot_dir / Path(normalized)).resolve()


def _normalize_registered_kit_path(
    registered_kit_path: Any,
    kit_slug: str,
) -> str:
    if isinstance(registered_kit_path, str) and registered_kit_path.strip():
        return _normalize_path_string(registered_kit_path)
    return f"config/kits/{kit_slug}"


def _serialize_manifest_binding_path(target_path: Any, cypilot_dir: Path) -> str:
    target_str = os.fspath(target_path)
    try:
        return _normalize_path_string(
            os.path.relpath(target_str, os.fspath(cypilot_dir))
        )
    except ValueError:
        return _normalize_path_string(target_str)


def _extract_registered_binding_path(binding: Any) -> Optional[str]:
    binding_path = binding.get("path") if isinstance(binding, dict) else binding
    if not isinstance(binding_path, str) or not binding_path.strip():
        return None
    return _normalize_path_string(binding_path)


def _resolve_registered_metadata_target_for_name(
    cypilot_dir: Path,
    binding_paths: List[str],
    target_name: str,
) -> Optional[Tuple[Path, str]]:
    for binding_rel in binding_paths:
        if PurePosixPath(binding_rel).name != target_name:
            continue
        binding_abs = _resolve_registered_kit_dir(cypilot_dir, binding_rel)
        if binding_abs is None or not binding_abs.is_file():
            continue
        binding_root = PurePosixPath(binding_rel).parent.as_posix()
        return binding_abs.parent, "" if binding_root == "." else binding_root
    return None


def _resolve_registered_metadata_target_from_resources(
    cypilot_dir: Path,
    resources: Any,
) -> Optional[Tuple[Path, str]]:
    if not isinstance(resources, dict):
        return None
    binding_paths = [
        binding_path
        for binding_path in (
            _extract_registered_binding_path(binding)
            for binding in resources.values()
        )
        if binding_path is not None
    ]
    for target_name in (_KIT_SKILL_FILE, _KIT_AGENTS_FILE):
        metadata_target = _resolve_registered_metadata_target_for_name(
            cypilot_dir,
            binding_paths,
            target_name,
        )
        if metadata_target is not None:
            return metadata_target
    return None


def _resolve_registered_kit_metadata_target(
    cypilot_dir: Path,
    kit_slug: str,
    kit_entry: Any,
) -> Tuple[Optional[Path], str]:
    kit_data = kit_entry if isinstance(kit_entry, dict) else {}
    registered_path = kit_data.get("path") if isinstance(kit_data.get("path"), str) else None
    kit_rel_path = _normalize_registered_kit_path(registered_path, kit_slug)
    kit_dir = _resolve_registered_kit_dir(
        cypilot_dir,
        registered_path if isinstance(registered_path, str) and registered_path.strip() else kit_rel_path,
    )
    if kit_dir is not None and (
        (kit_dir / _KIT_SKILL_FILE).is_file() or (kit_dir / _KIT_AGENTS_FILE).is_file()
    ):
        return kit_dir, kit_rel_path

    metadata_target = _resolve_registered_metadata_target_from_resources(
        cypilot_dir,
        kit_data.get("resources", {}),
    )
    if metadata_target is not None:
        return metadata_target

    return kit_dir, kit_rel_path


def _resolve_installed_kit_root(
    cypilot_dir: Path,
    config_dir: Path,
    kit_slug: str,
) -> Tuple[Optional[Path], str, Dict[str, Any], bool]:
    kit_entry = _read_kits_from_core_toml(config_dir).get(kit_slug, {})
    registered_path = kit_entry.get("path") if isinstance(kit_entry, dict) else None
    kit_rel_path = _normalize_registered_kit_path(registered_path, kit_slug)
    kit_dir = _resolve_registered_kit_dir(
        cypilot_dir,
        registered_path if isinstance(registered_path, str) and registered_path.strip() else kit_rel_path,
    )
    return kit_dir, kit_rel_path, kit_entry, isinstance(registered_path, str) and bool(registered_path.strip())


def _collect_kit_metadata(
    config_kit_dir: Optional[Path],
    kit_slug: str,
    registered_kit_path: Optional[str] = None,
) -> Dict[str, str]:
    """Read installed kit files and return metadata for .gen/ aggregation.

    Returns dict with:
        skill_nav      — navigation line for ``.gen/SKILL.md``
        agents_content — raw content of kit's AGENTS.md for ``.gen/AGENTS.md``
    """
    # @cpt-begin:cpt-cypilot-algo-kit-content-mgmt:p1:inst-collect-metadata
    result: Dict[str, str] = {"skill_nav": "", "agents_content": ""}
    kit_rel_path = _normalize_registered_kit_path(registered_kit_path, kit_slug)

    skill_path = config_kit_dir / _KIT_SKILL_FILE if config_kit_dir is not None else None
    if (
        (skill_path is not None and skill_path.is_file())
        or (config_kit_dir is None and _is_registered_kit_path_absolute(kit_rel_path))
    ):
        if not kit_rel_path:
            skill_target = f"{{cypilot_path}}/{_KIT_SKILL_FILE}"
        elif _is_registered_kit_path_absolute(kit_rel_path):
            skill_target = f"{kit_rel_path}/{_KIT_SKILL_FILE}"
        else:
            skill_target = f"{{cypilot_path}}/{kit_rel_path}/{_KIT_SKILL_FILE}"
        result["skill_nav"] = f"ALWAYS invoke `{skill_target}` FIRST"

    agents_path = config_kit_dir / _KIT_AGENTS_FILE if config_kit_dir is not None else None
    if agents_path is not None and agents_path.is_file():
        try:
            result["agents_content"] = agents_path.read_text(encoding="utf-8")
        except OSError:
            pass

    return result
    # @cpt-end:cpt-cypilot-algo-kit-content-mgmt:p1:inst-collect-metadata
# @cpt-end:cpt-cypilot-algo-kit-content-mgmt:p1:inst-collect-metadata-fn


# ---------------------------------------------------------------------------
# .gen/ aggregation — single source of truth for all callers
# ---------------------------------------------------------------------------

# @cpt-algo:cpt-cypilot-algo-kit-regen-gen:p1
# @cpt-begin:cpt-cypilot-algo-kit-regen-gen:p1:inst-regen-fn
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
    kits_map = _read_kits_from_core_toml(config_dir)
    if kits_map:
        for kit_slug in sorted(kits_map):
            kit_dir, kit_rel_path = _resolve_registered_kit_metadata_target(
                cypilot_dir, kit_slug, kits_map.get(kit_slug, {}),
            )
            meta = _collect_kit_metadata(kit_dir, kit_slug, kit_rel_path)
            if meta["skill_nav"]:
                gen_skill_nav_parts.append(meta["skill_nav"])
            if meta["agents_content"]:
                gen_agents_parts.append(meta["agents_content"])
    else:
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

    # @cpt-algo:cpt-cypilot-algo-v2-v3-migration-write-gen-agents:p1
    # @cpt-begin:cpt-cypilot-algo-kit-regen-gen:p1:inst-write-gen-agents
    # Write .gen/AGENTS.md
    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-write-gen-agents:p1:inst-compose-agents
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
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-write-gen-agents:p1:inst-compose-agents
    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-write-gen-agents:p1:inst-write-agents
    gen_dir.mkdir(parents=True, exist_ok=True)
    (gen_dir / _KIT_AGENTS_FILE).write_text(gen_agents_content, encoding="utf-8")
    result["gen_agents"] = "updated"
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-write-gen-agents:p1:inst-write-agents
    # @cpt-end:cpt-cypilot-algo-kit-regen-gen:p1:inst-write-gen-agents

    # @cpt-begin:cpt-cypilot-algo-kit-regen-gen:p1:inst-write-gen-skill
    # Write .gen/SKILL.md
    nav_rules = "\n\n".join(gen_skill_nav_parts) if gen_skill_nav_parts else ""
    (gen_dir / _KIT_SKILL_FILE).write_text(
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
# @cpt-end:cpt-cypilot-algo-kit-regen-gen:p1:inst-regen-fn


# @cpt-begin:cpt-cypilot-algo-kit-regen-gen:p1:inst-read-project-name-fn
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
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"kit: warning: cannot read project name from {artifacts_toml}: {exc}\n")
    return None
# @cpt-end:cpt-cypilot-algo-kit-regen-gen:p1:inst-read-project-name-fn


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
    config_kit_dir, config_kit_rel, kit_entry, has_registered_kit_path = _resolve_installed_kit_root(
        cypilot_dir, config_dir, kit_slug,
    )

    actions: Dict[str, str] = {}
    errors: List[str] = []

    if config_kit_dir is None:
        return {
            "status": "FAIL",
            "kit": kit_slug,
            "errors": [
                f"Kit '{kit_slug}' is registered at absolute path '{config_kit_rel}' which is not accessible on this OS",
            ],
        }

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
            kit_path=(
                kit_entry.get("path", "")
                if has_registered_kit_path and isinstance(kit_entry, dict)
                else ""
            ),
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
    meta = _collect_kit_metadata(config_kit_dir, kit_slug, config_kit_rel)
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
    kit_path: str = "",
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
    if kit_path:
        kit_root_rel = _normalize_registered_kit_path(kit_path, kit_slug)
        kit_root = _resolve_registered_kit_dir(cypilot_dir, kit_path)
        if kit_root is None:
            return {
                "status": "FAIL",
                "kit": kit_slug,
                "errors": [
                    f"Kit '{kit_slug}' is registered at absolute path '{kit_root_rel}' which is not accessible on this OS",
                ],
            }
    else:
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

        kit_root_rel = _serialize_manifest_binding_path(kit_root, cypilot_dir)
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
                    user_path = Path(user_input)
                    if user_path.is_absolute():
                        target_abs = user_path
                    else:
                        target_abs = (kit_root / user_path).resolve()
                    target_rel = _serialize_manifest_binding_path(target_abs, cypilot_dir)
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
        binding_path = _serialize_manifest_binding_path(target_abs, cypilot_dir)
        resource_bindings[res.id] = {"path": binding_path}
        # @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-default-path

        # @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-copy-resource
        _copy_manifest_resource(kit_source, res, target_abs)
        # @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-copy-resource
        files_copied += 1
    # @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-foreach-resource

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-resolve-vars
    # Resolve {identifier} template variables in copied kit files
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
        source=source, resources=resource_bindings, kit_path=kit_root_rel,
    )
    # @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-register-bindings

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-manifest-collect-meta
    # Collect metadata for .gen/ aggregation
    meta = _collect_kit_metadata(kit_root, kit_slug, kit_root_rel)
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


# @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-copy-manifest-resource
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
# @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-copy-manifest-resource


# @cpt-begin:cpt-cypilot-algo-kit-manifest-install:p1:inst-resolve-template-vars
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
# @cpt-end:cpt-cypilot-algo-kit-manifest-install:p1:inst-resolve-template-vars


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
    kit_root, kit_root_rel, _kit_entry, _has_registered_path = _resolve_installed_kit_root(
        cypilot_dir,
        config_dir,
        kit_slug,
    )
    if kit_root is None:
        return {
            "status": "FAIL",
            "kit": kit_slug,
            "errors": [
                f"Kit '{kit_slug}' is registered at absolute path '{kit_root_rel}' which is not accessible on this OS",
            ],
        }
    # @cpt-end:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-read-root

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-foreach-resource
    for res in manifest.resources:
        # @cpt-begin:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-compute-path
        expected_path = kit_root / res.default_path
        # @cpt-end:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-compute-path

        # @cpt-begin:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-register-existing
        if expected_path.exists():
            # File/directory already on disk — register silently
            binding_path = _serialize_manifest_binding_path(expected_path, cypilot_dir)
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
        binding_path = _serialize_manifest_binding_path(target_abs, cypilot_dir)
        resource_bindings[res.id] = {"path": binding_path}
        new_count += 1
    # @cpt-end:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-prompt-new
    # @cpt-end:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-foreach-resource

    # @cpt-begin:cpt-cypilot-algo-kit-manifest-legacy-migration:p1:inst-legacy-write-bindings
    # Write all resource bindings to core.toml [kits.{slug}.resources]
    _register_kit_in_core_toml(
        config_dir, kit_slug, "", cypilot_dir,
        resources=resource_bindings,
        kit_path=_resolve_manifest_kit_root_rel(manifest, resource_bindings, kit_slug),
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

# @cpt-begin:cpt-cypilot-flow-kit-install-cli:p1:inst-resolve-github-source
def _resolve_install_source_github(
    source_arg: str,
) -> Optional[Tuple[Path, str, str, str, Optional[Path], Optional[int]]]:
    """Parse and download a GitHub kit source for ``cmd_kit_install``.

    Returns ``(kit_source, kit_slug, kit_version, github_source, tmp_dir, None)``
    on success, or a tuple whose last element is a non-zero exit code on failure.
    Returns ``None`` if source parsing fails (caller should return 2).
    """
    try:
        owner, repo, version = _parse_github_source(source_arg)
    except ValueError as exc:
        ui.result({
            "status": "FAIL",
            "message": str(exc),
            "hint": "Expected format: owner/repo or owner/repo@version",
        })
        return None

    ui.step(f"Downloading {owner}/{repo}" + (f"@{version}" if version else " (latest)") + "...")
    try:
        kit_source, resolved_version = _download_kit_from_github(owner, repo, version)
    except RuntimeError as exc:
        ui.result({"status": "FAIL", "message": str(exc)})
        return (Path("."), "", "", "", None, 1)

    conf_file = kit_source / _KIT_CONF_FILE
    kit_slug = _read_kit_slug(kit_source) or repo.removeprefix("cyber-pilot-kit-")
    kit_version = (
        resolved_version or _read_kit_version(conf_file)
        if conf_file.is_file() else resolved_version
    )
    github_source = f"github:{owner}/{repo}"
    ui.substep(f"Resolved: {kit_slug}@{kit_version or '(dev)'}")
    return (kit_source, kit_slug, kit_version, github_source, kit_source.parent, None)
# @cpt-end:cpt-cypilot-flow-kit-install-cli:p1:inst-resolve-github-source


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
        kit_source = Path(args.local_path).resolve()
        if not kit_source.is_dir():
            ui.result({
                "status": "FAIL",
                "message": f"Kit source directory not found: {kit_source}",
                "hint": "Provide a path to a valid kit directory",
            })
            return 2
        # @cpt-begin:cpt-cypilot-flow-kit-install-cli:p1:inst-read-slug-version
        kit_slug = _read_kit_slug(kit_source) or kit_source.name
        kit_version = (
            _read_kit_version(kit_source / _KIT_CONF_FILE)
            if (kit_source / _KIT_CONF_FILE).is_file() else ""
        )
        # @cpt-end:cpt-cypilot-flow-kit-install-cli:p1:inst-read-slug-version
    else:
        gh = _resolve_install_source_github(args.source)
        if gh is None:
            return 2
        # @cpt-begin:cpt-cypilot-flow-kit-install-cli:p1:inst-read-slug-version
        kit_source, kit_slug, kit_version, github_source, tmp_dir_to_clean, exit_code = gh
        # @cpt-end:cpt-cypilot-flow-kit-install-cli:p1:inst-read-slug-version
        if exit_code is not None:
            return exit_code
    # @cpt-end:cpt-cypilot-flow-kit-install-cli:p1:inst-validate-source

    try:
        # @cpt-begin:cpt-cypilot-flow-kit-install-cli:p1:inst-resolve-project
        resolved = _resolve_cypilot_dir()
        if resolved is None:
            return 1
        _, cypilot_dir = resolved
        config_dir = cypilot_dir / "config"
        config_kit_dir, _, _, _ = _resolve_installed_kit_root(
            cypilot_dir, config_dir, kit_slug,
        )
        if config_kit_dir is None:
            ui.result(
                {
                    "status": "FAIL",
                    "kit": kit_slug,
                    "message": f"Kit '{kit_slug}' is registered at an absolute path that is not accessible on this OS",
                },
                human_fn=lambda d: _human_kit_install(d),
            )
            return 2
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
        # @cpt-begin:cpt-cypilot-flow-kit-install-cli:p1:inst-cleanup-tmp
        if tmp_dir_to_clean:
            shutil.rmtree(tmp_dir_to_clean, ignore_errors=True)
        # @cpt-end:cpt-cypilot-flow-kit-install-cli:p1:inst-cleanup-tmp

# @cpt-begin:cpt-cypilot-flow-kit-install-cli:p1:inst-human-output
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
# @cpt-end:cpt-cypilot-flow-kit-install-cli:p1:inst-human-output

# ---------------------------------------------------------------------------
# Kit Update
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-flow-kit-update-cli:p1:inst-resolve-github-targets
def _resolve_github_update_targets(
    kits_map: Dict[str, Dict[str, Any]],
) -> Tuple[List[Tuple[str, Path, str, Optional[Path]]], List[Dict[str, Any]]]:
    """Download GitHub kit sources and return update targets list.

    For each kit with a ``github:`` source, downloads the tarball and appends
    ``(slug, source_dir, source_str, tmp_dir)`` to the result list.
    Kits with missing or unsupported sources emit warnings and are recorded
    as structured failures.

    Returns:
        Tuple of (targets, failures) where failures are dicts with
        kit, action="ERROR", message, and optionally source.
    """
    targets: List[Tuple[str, Path, str, Optional[Path]]] = []
    failures: List[Dict[str, Any]] = []
    for slug, kit_data in kits_map.items():
        source_str = kit_data.get("source", "")
        if not source_str:
            msg = f"Kit '{slug}' has no registered source — skipping"
            ui.warn(msg)
            failures.append({"kit": slug, "action": "ERROR", "message": msg})
            continue
        if not source_str.startswith("github:"):
            msg = f"Kit '{slug}': unsupported source type '{source_str}' — skipping"
            ui.warn(msg)
            failures.append({"kit": slug, "action": "ERROR", "message": msg, "source": source_str})
            continue

        owner_repo = source_str.removeprefix("github:")
        try:
            owner, repo, version = _parse_github_source(owner_repo)
        except ValueError as exc:
            msg = f"Kit '{slug}': invalid source '{source_str}': {exc}"
            ui.warn(msg)
            failures.append({"kit": slug, "action": "ERROR", "message": msg, "source": source_str})
            continue

        ui.step(f"Downloading {owner}/{repo}...")
        try:
            kit_source_dir, _resolved = _download_kit_from_github(owner, repo, version)
            targets.append((slug, kit_source_dir, source_str, kit_source_dir.parent))
        except RuntimeError as exc:
            msg = f"Kit '{slug}': download failed: {exc}"
            ui.warn(msg)
            failures.append({"kit": slug, "action": "failed", "message": msg, "source": source_str})
    return targets, failures
# @cpt-end:cpt-cypilot-flow-kit-update-cli:p1:inst-resolve-github-targets


# @cpt-begin:cpt-cypilot-flow-kit-update-cli:p1:inst-build-update-result
def _normalize_kit_update_action(action: Any) -> str:
    normalized = str(action or "").strip().lower()
    if normalized in {"error", "fail", "failed"}:
        return "failed"
    return normalized


def _build_kit_update_result(kit_slug: str, kit_r: Dict[str, Any]) -> Dict[str, Any]:
    """Extract a normalised result entry from update_kit() output."""
    ver = kit_r.get("version", {})
    ver_status = _normalize_kit_update_action(
        ver.get("status", "") if isinstance(ver, dict) else str(ver),
    )
    gen = kit_r.get("gen", {})
    accepted = gen.get("accepted_files", []) if isinstance(gen, dict) else []
    declined = kit_r.get("gen_rejected", [])
    files_written = gen.get("files_written", 0) if isinstance(gen, dict) else 0
    unchanged = gen.get("unchanged", 0) if isinstance(gen, dict) else 0
    result = {
        "kit": kit_slug,
        "action": ver_status,
        "accepted": accepted,
        "declined": declined,
        "files_written": files_written,
        "unchanged": unchanged,
    }
    if kit_r.get("errors"):
        result["errors"] = list(kit_r.get("errors", []))
    return result
# @cpt-end:cpt-cypilot-flow-kit-update-cli:p1:inst-build-update-result


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
    source_failures: List[Dict[str, Any]] = []

    if args.local_path:
        kit_source = Path(args.local_path).resolve()
        if not kit_source.is_dir():
            ui.result({
                "status": "FAIL",
                "message": f"Kit source directory not found: {kit_source}",
                "hint": "Provide a path to a valid kit directory",
            })
            return 2
        # @cpt-begin:cpt-cypilot-flow-kit-update-cli:p1:inst-read-slug
        kit_slug = args.slug or _read_kit_slug(kit_source) or kit_source.name
        # @cpt-end:cpt-cypilot-flow-kit-update-cli:p1:inst-read-slug
        update_targets.append((kit_slug, kit_source, "", None))
    else:
        kits_map = _read_kits_from_core_toml(config_dir)
        if not kits_map:
            ui.result({
                "status": "FAIL",
                "message": "No kits registered in core.toml",
                "hint": "Install a kit first: cpt kit install owner/repo",
            })
            return 2

        if args.slug:
            if args.slug not in kits_map:
                ui.result({
                    "status": "FAIL",
                    "message": f"Kit '{args.slug}' not found in core.toml",
                    "hint": f"Registered kits: {', '.join(kits_map.keys())}",
                })
                return 2
            kits_map = {args.slug: kits_map[args.slug]}

        update_targets, source_failures = _resolve_github_update_targets(kits_map)
        if not update_targets:
            if source_failures:
                ui.result({
                    "status": "FAIL",
                    "message": "All kits failed source resolution",
                    "results": source_failures,
                    "errors": [f"{sf['kit']}: {sf['message']}" for sf in source_failures],
                })
            else:
                ui.result({
                    "status": "FAIL",
                    "message": "No kits to update (no valid sources found)",
                })
            return 2
    # @cpt-end:cpt-cypilot-flow-kit-update-cli:p1:inst-validate-source

    # @cpt-begin:cpt-cypilot-flow-kit-update-cli:p1:inst-delegate-update
    all_results: List[Dict[str, Any]] = []
    errors: List[str] = []

    for sf in source_failures:
        normalized_source_failure = dict(sf)
        normalized_source_failure["action"] = _normalize_kit_update_action(
            normalized_source_failure.get("action"),
        )
        all_results.append(normalized_source_failure)
        errors.append(f"{sf['kit']}: {sf['message']}")

    for kit_slug, kit_source, github_source, tmp_dir in update_targets:
        # @cpt-begin:cpt-cypilot-flow-kit-update-cli:p1:inst-show-whatsnew
        if not args.dry_run:
            installed_version = _read_kit_version_from_core(config_dir, kit_slug)
            ack = show_kit_whatsnew(
                kit_source,
                installed_version,
                kit_slug,
                interactive=interactive and not args.yes,
            )
            if not ack:
                all_results.append({
                    "kit": kit_slug,
                    "action": "aborted",
                    "accepted": [],
                    "declined": [],
                    "files_written": 0,
                })
                if tmp_dir:
                    shutil.rmtree(tmp_dir, ignore_errors=True)
                continue
        # @cpt-end:cpt-cypilot-flow-kit-update-cli:p1:inst-show-whatsnew

        try:
            # @cpt-begin:cpt-cypilot-flow-kit-update-cli:p1:inst-legacy-migration
            kit_r = update_kit(
                kit_slug, kit_source, cypilot_dir,
                dry_run=args.dry_run,
                interactive=interactive,
                auto_approve=args.yes,
                force=args.force,
                source=github_source,
            )
            # @cpt-end:cpt-cypilot-flow-kit-update-cli:p1:inst-legacy-migration
        except Exception as exc:  # pylint: disable=broad-exception-caught  # per-kit safety net — must not crash the update loop
            kit_r = {"kit": kit_slug, "version": {"status": "failed"}, "gen": {}}
            errors.append(f"{kit_slug}: {exc}")
        finally:
            if tmp_dir:
                shutil.rmtree(tmp_dir, ignore_errors=True)

        if kit_r.get("errors"):
            errors.extend(f"{kit_slug}: {err}" for err in kit_r.get("errors", []))
        all_results.append(_build_kit_update_result(kit_slug, kit_r))
    # @cpt-end:cpt-cypilot-flow-kit-update-cli:p1:inst-delegate-update

    # @cpt-begin:cpt-cypilot-flow-kit-update-cli:p1:inst-regen-gen
    has_failed_updates = any(
        _normalize_kit_update_action(r.get("action")) == "failed"
        for r in all_results
    )
    if not args.dry_run and not has_failed_updates:
        regenerate_gen_aggregates(cypilot_dir)
    # @cpt-end:cpt-cypilot-flow-kit-update-cli:p1:inst-regen-gen

    # @cpt-begin:cpt-cypilot-flow-kit-update-cli:p1:inst-format-output
    n_updated = sum(
        1
        for r in all_results
        if _normalize_kit_update_action(r.get("action"))
        not in ("current", "dry_run", "aborted", "failed")
    )
    command_failed = has_failed_updates
    if command_failed:
        status = "FAIL"
    elif not errors:
        status = "PASS"
    else:
        status = "WARN"
    output: Dict[str, Any] = {
        "status": status,
        "kits_updated": n_updated,
        "results": all_results,
    }
    if errors:
        output["errors"] = errors
    if n_updated == 0 and not errors:
        output["message"] = "All kits are up to date"

    ui.result(output, human_fn=lambda d: _human_kit_update(d))
    return 2 if command_failed else 0
    # @cpt-end:cpt-cypilot-flow-kit-update-cli:p1:inst-format-output

# @cpt-begin:cpt-cypilot-flow-kit-update-cli:p1:inst-human-output
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
# @cpt-end:cpt-cypilot-flow-kit-update-cli:p1:inst-human-output

# ---------------------------------------------------------------------------
# Kit Migrate — conf.toml helpers
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-conf-version
def _read_conf_version(conf_path: Path) -> int:
    """Read top-level 'version' from conf.toml. Returns 0 if missing."""
    if not conf_path.is_file():
        return 0
    try:
        import tomllib
        with open(conf_path, "rb") as f:
            data = tomllib.load(f)
        ver = data.get("version")
        return int(ver) if ver is not None else 0
    except (OSError, ValueError):
        return 0
    # @cpt-end:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-conf-version

# ---------------------------------------------------------------------------
# Layout migration — old (kits/ + .gen/kits/) → new (config/kits/ only, no kits/)
# @cpt-algo:cpt-cypilot-algo-version-config-layout-restructure:p1
# ---------------------------------------------------------------------------

_LEGACY_SKIP_NAMES = frozenset(("blueprints", "blueprint_hashes.toml", "__pycache__", ".prev"))


def _copy_legacy_kit_item(item: Path, dst: Path) -> None:
    if item.is_dir():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(item, dst)
        return
    if not dst.exists():
        shutil.copy2(item, dst)


def _backup_existing_config_kit(config_kit: Path, kit_backup: Path) -> Path:
    config_backup = kit_backup / "config_kit"
    if config_backup.exists():
        shutil.rmtree(config_backup)
    if config_kit.is_dir():
        config_backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(config_kit, config_backup)
    return config_backup


def _restore_existing_config_kit(config_backup: Path, config_kit: Path) -> None:
    if config_kit.exists():
        shutil.rmtree(config_kit)
    if not config_backup.is_dir():
        return
    config_kit.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(config_backup), str(config_kit))


# @cpt-begin:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-migrate-kits-entry
def _migrate_single_kits_dir_entry(
    kit_dir: Path,
    config_kits: Path,
    backup_dir: Path,
) -> str:
    """Copy one kits/{slug}/ entry into config/kits/{slug}/, with backup/rollback.

    Returns ``"migrated"`` on success or ``"FAILED: <msg>"`` on error.
    """
    slug = kit_dir.name
    config_kit = config_kits / slug
    kit_backup = backup_dir / slug / "kits_entry"
    config_backup = kit_backup / "config_kit"
    config_kit_tmp = config_kits / f".{slug}.tmp"

    try:
        _backup_existing_config_kit(config_kit, kit_backup)

        if config_kit_tmp.exists():
            shutil.rmtree(config_kit_tmp)
        config_kit_tmp.mkdir(parents=True, exist_ok=True)
        for item in kit_dir.iterdir():
            if item.name in _LEGACY_SKIP_NAMES:
                continue
            dst = config_kit_tmp / item.name
            _copy_legacy_kit_item(item, dst)
        if config_kit.exists():
            shutil.rmtree(config_kit)
        os.replace(config_kit_tmp, config_kit)
        return "migrated"
    except OSError as exc:
        if config_kit_tmp.exists():
            shutil.rmtree(config_kit_tmp, ignore_errors=True)
        _restore_existing_config_kit(config_backup, config_kit)
        return f"FAILED: {exc}"
# @cpt-end:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-migrate-kits-entry


# @cpt-begin:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-migrate-gen-entry
def _migrate_single_gen_kit_entry(gen_kit: Path, config_kits: Path, backup_dir: Path) -> str:
    """Copy one .gen/kits/{slug}/ entry into config/kits/{slug}/ (no-overwrite).

    Returns ``"migrated"`` on success or ``"FAILED: <msg>"`` on error.
    """
    slug = gen_kit.name
    config_kit = config_kits / slug
    kit_backup = backup_dir / slug / "gen_entry"
    config_backup = kit_backup / "config_kit"
    config_kit_tmp = config_kits / f".{slug}.gen.tmp"

    try:
        _backup_existing_config_kit(config_kit, kit_backup)

        if config_kit_tmp.exists():
            shutil.rmtree(config_kit_tmp)
        if config_kit.is_dir():
            shutil.copytree(config_kit, config_kit_tmp)
        else:
            config_kit_tmp.mkdir(parents=True, exist_ok=True)
        for item in gen_kit.iterdir():
            dst = config_kit_tmp / item.name
            if item.is_dir():
                if not dst.exists():
                    shutil.copytree(item, dst)
            elif not dst.exists():
                shutil.copy2(item, dst)
        if config_kit.exists():
            shutil.rmtree(config_kit)
        os.replace(config_kit_tmp, config_kit)
        return "migrated"
    except OSError as exc:
        if config_kit_tmp.exists():
            shutil.rmtree(config_kit_tmp, ignore_errors=True)
        _restore_existing_config_kit(config_backup, config_kit)
        return f"FAILED: {exc}"
# @cpt-end:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-migrate-gen-entry


# @cpt-begin:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-update-core-paths
def _update_core_toml_kit_paths(config_dir: Path) -> None:
    """Rewrite legacy .gen/kits/ and kits/ paths in core.toml to config/kits/."""
    core_toml = config_dir / _KIT_CORE_TOML
    if not core_toml.is_file():
        return
    import tomllib
    with open(core_toml, "rb") as f:
        data = tomllib.load(f)
    kits_conf = data.get("kits", {})
    updated = False
    for kit_entry in kits_conf.values():
        if not isinstance(kit_entry, dict):
            continue
        old_path = kit_entry.get("path", "")
        if old_path.startswith(".gen/kits/") or old_path.startswith("kits/"):
            slug = old_path.rsplit("/", 1)[-1]
            kit_entry["path"] = f"config/kits/{slug}"
            updated = True
    if updated:
        from ..utils import toml_utils
        toml_utils.dump(data, core_toml, header_comment="Cypilot project configuration")
# @cpt-end:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-update-core-paths


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
    # @cpt-begin:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-backup
    if has_kits_dir:
        for kit_dir in sorted(kits_dir.iterdir()):
            if not kit_dir.is_dir():
                continue
            slug = kit_dir.name
            if dry_run:
                migrated[slug] = "would_migrate"
                continue
            migrated[slug] = _migrate_single_kits_dir_entry(kit_dir, config_kits, backup_dir)
    # @cpt-end:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-backup

    # @cpt-begin:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-move-gen
    # ── Migrate .gen/kits/{slug}/ into config/kits/{slug}/ ─────────────
    if has_gen_kits:
        for gen_kit in sorted(gen_kits.iterdir()):
            if not gen_kit.is_dir():
                continue
            slug = gen_kit.name
            if dry_run:
                migrated.setdefault(slug, "would_migrate")
                continue
            result = _migrate_single_gen_kit_entry(gen_kit, config_kits, backup_dir)
            # Failure must override any earlier success for the same slug
            if isinstance(result, str) and result.startswith("FAILED"):
                migrated[slug] = result
            else:
                migrated.setdefault(slug, result)
    # @cpt-end:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-move-gen

    if dry_run:
        return migrated

    _finalize_layout_migration(migrated, cypilot_dir, kits_dir, gen_kits, backup_dir)
    return migrated


def _finalize_layout_migration(
    migrated: Dict[str, Any],
    cypilot_dir: Path,
    kits_dir: Path,
    gen_kits: Path,
    backup_dir: Path,
) -> None:
    """Post-migration cleanup: update core.toml, remove legacy dirs, clean backups."""
    # @cpt-begin:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-rollback
    has_failures = any(isinstance(s, str) and s.startswith("FAILED") for s in migrated.values())

    # @cpt-begin:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-update-core
    # ── Update core.toml kit paths (only when all migrations succeeded) ──
    if not has_failures:
        _update_core_toml_kit_paths(cypilot_dir / "config")
    # @cpt-end:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-update-core

    # @cpt-begin:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-remove-refs
    # ── Remove legacy directories (only when all migrations succeeded) ───
    if not has_failures and kits_dir.is_dir():
        shutil.rmtree(kits_dir)
    # @cpt-end:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-remove-refs

    # @cpt-begin:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-clean-gen
    if not has_failures and gen_kits.is_dir():
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
    # @cpt-end:cpt-cypilot-algo-version-config-layout-restructure:p1:inst-layout-rollback


# @cpt-begin:cpt-cypilot-algo-kit-update:p1:inst-perform-first-install
def _perform_first_install_kit(
    source_dir: Path,
    config_kit_dir: Path,
    config_dir: Path,
    kit_slug: str,
    source_version: str,
    cypilot_dir: Path,
    source: str = "",
) -> Dict[str, Any]:
    """Copy kit content, seed configs, and register in core.toml for a first install.

    Returns a result dict matching the install_kit status shape.
    """
    copy_actions = _copy_kit_content(source_dir, config_kit_dir)
    scripts_dir = config_kit_dir / "scripts"
    if scripts_dir.is_dir():
        _seed_kit_config_files(scripts_dir, config_dir, {})
    _register_kit_in_core_toml(config_dir, kit_slug, source_version, cypilot_dir, source=source)
    return {
        "status": "PASS",
        "action": "installed",
        "kit": kit_slug,
        "version": source_version,
        "files_copied": sum(1 for v in copy_actions.values() if v == "copied"),
        "errors": [],
        "actions": copy_actions,
    }
# @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-perform-first-install


def _resolve_manifest_root_from_binding(
    binding_path: Optional[str],
    default_path: str,
) -> Optional[str]:
    if not isinstance(binding_path, str) or not binding_path.strip():
        return None
    binding_parts = PurePosixPath(binding_path).parts
    default_parts = PurePosixPath(default_path).parts
    if len(binding_parts) < len(default_parts):
        return None
    if tuple(binding_parts[-len(default_parts):]) != tuple(default_parts):
        return None
    prefix_parts = binding_parts[:-len(default_parts)]
    if prefix_parts:
        return PurePosixPath(*prefix_parts).as_posix()
    return ""


def _resolve_declared_manifest_root(manifest: Any, kit_slug: str) -> str:
    manifest_root = getattr(manifest, "root", "")
    if isinstance(manifest_root, str) and manifest_root.strip():
        resolved_root = manifest_root.replace("{cypilot_path}", ".").replace("{slug}", kit_slug).strip()
        if resolved_root and resolved_root != ".":
            return PurePosixPath(resolved_root).as_posix()
    return f"config/kits/{kit_slug}"


def _resolve_manifest_kit_root_rel(
    manifest: Any,
    merged: Dict[str, Dict[str, str]],
    kit_slug: str,
) -> str:
    for res in getattr(manifest, "resources", []):
        binding = merged.get(res.id, {})
        binding_path = binding.get("path") if isinstance(binding, dict) else None
        binding_root = _resolve_manifest_root_from_binding(binding_path, res.default_path)
        if binding_root is not None:
            return binding_root

    return _resolve_declared_manifest_root(manifest, kit_slug)


# @cpt-begin:cpt-cypilot-algo-kit-update:p1:inst-sync-manifest-bindings
def _sync_manifest_resource_bindings(
    manifest: Any,
    config_dir: Path,
    kit_slug: str,
) -> Optional[Dict[str, Dict[str, str]]]:
    """Merge existing resource bindings with any new manifest resources.

    Returns merged bindings dict, or None if there is no manifest.
    """
    if manifest is None:
        return None
    existing_raw = _read_kits_from_core_toml(config_dir).get(kit_slug, {}).get("resources", {})
    merged: Dict[str, Dict[str, str]] = {}
    for res_id, binding in existing_raw.items():
        if isinstance(binding, dict):
            merged[res_id] = binding
        elif isinstance(binding, str):
            merged[res_id] = {"path": binding}
    kit_root_rel = _resolve_manifest_kit_root_rel(manifest, merged, kit_slug)
    for res in manifest.resources:
        if res.id not in merged:
            if kit_root_rel:
                resource_path = (PurePosixPath(kit_root_rel) / res.default_path).as_posix()
            else:
                resource_path = PurePosixPath(res.default_path).as_posix()
            merged[res.id] = {"path": resource_path}
    return merged
# @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-sync-manifest-bindings


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

    result: Dict[str, Any] = {"kit": kit_slug}
    # @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-resolve-config

    installed_kit_dir, installed_kit_rel, installed_kit_entry, has_registered_kit_path = _resolve_installed_kit_root(
        cypilot_dir, config_dir, kit_slug,
    )
    registered_kit_path = (
        installed_kit_entry.get("path", "")
        if isinstance(installed_kit_entry, dict)
        else ""
    )

    if installed_kit_dir is None:
        result["version"] = {"status": "failed"}
        result["gen"] = {"files_written": 0}
        result["errors"] = [
            f"Kit '{kit_slug}' is registered at absolute path '{installed_kit_rel}' which is not accessible on this OS",
        ]
        return result

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
    if not force and source_version and installed_kit_dir.is_dir():
        installed_version = _read_kit_version_from_core(config_dir, kit_slug)
        if installed_version and installed_version == source_version:
            result["version"] = {"status": "current"}
            result["gen"] = {"files_written": 0}
            # Still collect metadata for .gen/ aggregation
            _current_dir, _current_rel = _resolve_registered_kit_metadata_target(
                cypilot_dir, kit_slug, installed_kit_entry,
            )
            meta = _collect_kit_metadata(_current_dir, kit_slug, _current_rel)
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
    if _manifest is not None and installed_kit_dir.is_dir():
        if not installed_kit_entry.get("resources"):
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
        try:
            _source_to_resource_id, _resource_info = build_source_to_resource_mapping(source_dir)
            _resource_bindings = resolve_resource_bindings(config_dir, kit_slug, cypilot_dir)
        except ValueError as exc:
            result["version"] = {"status": "failed"}
            result["gen"] = {"files_written": 0}
            result["errors"] = [str(exc)]
            return result
    # @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-resolve-resource-bindings

    # @cpt-begin:cpt-cypilot-algo-kit-update:p1:inst-first-install
    # ── 1. First-install or file-level update ────────────────────────
    if not installed_kit_dir.is_dir():
        if _manifest is not None:
            _install_result = install_kit_with_manifest(
                source_dir, cypilot_dir, kit_slug, source_version,
                _manifest,
                interactive=interactive and not auto_approve,
                source=source,
                kit_path=registered_kit_path if has_registered_kit_path else "",
            )
            files_written = _install_result.get("files_copied", 0)
        else:
            _install_result = _perform_first_install_kit(
                source_dir, installed_kit_dir, config_dir, kit_slug, source_version, cypilot_dir,
                source=source,
            )
            files_written = _install_result.get("files_copied", 0)
        install_status = str(_install_result.get("status", "PASS")).upper()
        if install_status == "FAIL":
            result["version"] = {"status": "failed", "source_status": install_status}
        else:
            result["version"] = {"status": "created", "source_status": install_status}
        result["gen"] = {"files_written": files_written}
        if _install_result.get("errors"):
            result["errors"] = list(_install_result.get("errors", []))
        if _install_result.get("actions"):
            result["actions"] = _install_result.get("actions")
        if _install_result.get("status") == "FAIL":
            return result
    # @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-first-install
    else:
        # @cpt-begin:cpt-cypilot-algo-kit-update:p1:inst-file-level-diff
        from ..utils.diff_engine import file_level_kit_update

        report = file_level_kit_update(
            source_dir, installed_kit_dir,
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
            "unchanged": report.get("unchanged", 0),
        }
        if declined:
            result["gen_rejected"] = declined
        # @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-file-level-diff

        # @cpt-begin:cpt-cypilot-algo-kit-update:p1:inst-update-core-toml
        _merged_resources = _sync_manifest_resource_bindings(
            _manifest, config_dir, kit_slug,
        )
        if source_version or _merged_resources:
            _kit_root_rel = registered_kit_path if _manifest is not None else ""
            _register_kit_in_core_toml(
                config_dir, kit_slug, source_version, cypilot_dir,
                source=source, resources=_merged_resources, kit_path=_kit_root_rel,
            )
        # @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-update-core-toml

    # @cpt-begin:cpt-cypilot-algo-kit-update:p1:inst-collect-metadata
    # ── 2. Collect metadata for .gen/ aggregation ────────────────────
    _meta_entry = _read_kits_from_core_toml(config_dir).get(kit_slug, {})
    _meta_dir, _meta_rel = _resolve_registered_kit_metadata_target(
        cypilot_dir, kit_slug, _meta_entry,
    )
    meta = _collect_kit_metadata(_meta_dir, kit_slug, _meta_rel)
    if meta["skill_nav"]:
        result["skill_nav"] = meta["skill_nav"]
    if meta["agents_content"]:
        result["agents_content"] = meta["agents_content"]
    # @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-collect-metadata

    # @cpt-begin:cpt-cypilot-algo-kit-update:p1:inst-return-result
    return result
    # @cpt-end:cpt-cypilot-algo-kit-update:p1:inst-return-result

# @cpt-begin:cpt-cypilot-flow-kit-dispatch:p1:inst-migrate-deprecated
def cmd_kit_migrate(_argv: List[str]) -> int:
    """Deprecated — use 'cypilot kit update <path>' instead.

    The migrate command was part of the blueprint-based three-way merge system
    which has been removed.  File-level updates are now handled by 'kit update'.
    """
    sys.stderr.write(
        "WARNING: 'cypilot kit migrate' is deprecated.\n"
        "         Use 'cypilot kit update <path>' instead.\n"
    )
    return 1
# @cpt-end:cpt-cypilot-flow-kit-dispatch:p1:inst-migrate-deprecated

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

# @cpt-begin:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-kits-core
def _read_kits_from_core_toml(config_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Read all kit entries from config/core.toml [kits] section.

    Returns dict of {slug: {format, path, source?, version?}}.
    """
    core_toml = config_dir / _KIT_CORE_TOML
    if not core_toml.is_file():
        return {}
    try:
        import tomllib
        with open(core_toml, "rb") as f:
            data = tomllib.load(f)
    except (OSError, ValueError):
        return {}
    kits = data.get("kits", {})
    if not isinstance(kits, dict):
        return {}
    return {k: v for k, v in kits.items() if isinstance(v, dict)}
# @cpt-end:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-kits-core


# @cpt-algo:cpt-cypilot-algo-kit-config-helpers:p1
# @cpt-begin:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-slug-fn
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
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"kit: warning: cannot read {conf_toml}: {exc}\n")
    return ""
    # @cpt-end:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-slug
# @cpt-end:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-slug-fn

# @cpt-begin:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-version-core-fn
def _read_kit_version_from_core(config_dir: Path, kit_slug: str) -> str:
    """Read installed kit version from config/core.toml [kits.{slug}].version."""
    # @cpt-begin:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-version-from-core
    core_toml = config_dir / _KIT_CORE_TOML
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
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"kit: warning: cannot read version for '{kit_slug}' from {core_toml}: {exc}\n")
    return ""
    # @cpt-end:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-version-from-core
# @cpt-end:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-version-core-fn

# @cpt-begin:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-kit-version-fn
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
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"kit: warning: cannot read version from {conf_path}: {exc}\n")
    return ""
    # @cpt-end:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-kit-version
# @cpt-end:cpt-cypilot-algo-kit-config-helpers:p1:inst-read-kit-version-fn

# @cpt-begin:cpt-cypilot-algo-kit-config-helpers:p1:inst-register-core-fn
def _register_kit_in_core_toml(
    config_dir: Path,
    kit_slug: str,
    kit_version: str,
    _cypilot_dir: Path,  # reserved for future cypilot-dir-relative path computation
    source: str = "",
    resources: Optional[Dict[str, Dict[str, str]]] = None,
    kit_path: str = "",
) -> None:
    """Register or update a kit entry in config/core.toml."""
    # @cpt-begin:cpt-cypilot-algo-kit-config-helpers:p1:inst-register-core
    core_toml = config_dir / _KIT_CORE_TOML
    if not core_toml.is_file():
        return

    try:
        import tomllib
        with open(core_toml, "rb") as f:
            data = tomllib.load(f)
    except (OSError, ValueError):
        return

    kits = data.setdefault("kits", {})
    # Merge into existing entry to preserve fields like 'source'
    existing = kits.get(kit_slug, {})
    if not isinstance(existing, dict):
        existing = {}
    existing["format"] = "Cypilot"
    if kit_path:
        normalized_kit_path = _normalize_registered_kit_path(kit_path, kit_slug)
        existing_path = existing.get("path")
        if (
            isinstance(existing_path, str)
            and _normalize_path_string(existing_path) == normalized_kit_path
        ):
            existing["path"] = existing_path
        else:
            existing["path"] = normalized_kit_path
    elif not existing.get("path"):
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
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"kit: warning: failed to register {kit_slug} in {core_toml}: {exc}\n")
    # @cpt-end:cpt-cypilot-algo-kit-config-helpers:p1:inst-register-core
# @cpt-end:cpt-cypilot-algo-kit-config-helpers:p1:inst-register-core-fn
