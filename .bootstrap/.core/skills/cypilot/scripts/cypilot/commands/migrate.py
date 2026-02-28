"""
V2 → V3 Migration Command

Migrates existing Cypilot v2 projects (adapter-based, artifacts.json, legacy kit structure)
to v3 (blueprint-based, artifacts.toml, three-directory layout).

@cpt-flow:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1
@cpt-flow:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1
@cpt-algo:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1
@cpt-algo:cpt-cypilot-algo-v2-v3-migration-detect-core-install-type:p1
@cpt-algo:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1
@cpt-algo:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1
@cpt-algo:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1
@cpt-algo:cpt-cypilot-algo-v2-v3-migration-migrate-kits:p1
@cpt-algo:cpt-cypilot-algo-v2-v3-migration-convert-agents-md:p1
@cpt-algo:cpt-cypilot-algo-v2-v3-migration-generate-core-toml:p1
@cpt-algo:cpt-cypilot-algo-v2-v3-migration-inject-root-agents:p1
@cpt-algo:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1
@cpt-state:cpt-cypilot-state-v2-v3-migration-status:p1
@cpt-dod:cpt-cypilot-dod-v2-v3-migration-v2-detection:p1
@cpt-dod:cpt-cypilot-dod-v2-v3-migration-core-cleanup:p1
@cpt-dod:cpt-cypilot-dod-v2-v3-migration-artifacts-conversion:p1
@cpt-dod:cpt-cypilot-dod-v2-v3-migration-agents-conversion:p1
@cpt-dod:cpt-cypilot-dod-v2-v3-migration-core-config:p1
@cpt-dod:cpt-cypilot-dod-v2-v3-migration-root-agents-injection:p1
@cpt-dod:cpt-cypilot-dod-v2-v3-migration-kit-install:p1
@cpt-dod:cpt-cypilot-dod-v2-v3-migration-agent-entries:p1
@cpt-dod:cpt-cypilot-dod-v2-v3-migration-backup-rollback:p1
@cpt-dod:cpt-cypilot-dod-v2-v3-migration-validation:p1
@cpt-dod:cpt-cypilot-dod-v2-v3-migration-json-to-toml:p1
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..utils import toml_utils
from ..utils.files import find_project_root

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CACHE_DIR = Path.home() / ".cypilot" / "cache"
DEFAULT_V2_CORE = ".cypilot"
DEFAULT_V2_ADAPTER = ".cypilot-adapter"
DEFAULT_V3_INSTALL_DIR = "cypilot"
CORE_SUBDIR = ".core"
GEN_SUBDIR = ".gen"

# Migration state machine values
STATE_NOT_STARTED = "NOT_STARTED"
STATE_DETECTED = "DETECTED"
STATE_BACKED_UP = "BACKED_UP"
STATE_CONVERTING = "CONVERTING"
STATE_CONVERTED = "CONVERTED"
STATE_VALIDATING = "VALIDATING"
STATE_COMPLETED = "COMPLETED"
STATE_ROLLED_BACK = "ROLLED_BACK"
STATE_FAILED = "FAILED"

# Core install type enum values
INSTALL_TYPE_SUBMODULE = "SUBMODULE"
INSTALL_TYPE_GIT_CLONE = "GIT_CLONE"
INSTALL_TYPE_PLAIN_DIR = "PLAIN_DIR"
INSTALL_TYPE_ABSENT = "ABSENT"


def _strip_none(obj: Any) -> Any:
    """Recursively strip None values from dicts/lists (TOML has no null)."""
    if isinstance(obj, dict):
        return {k: _strip_none(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_strip_none(v) for v in obj if v is not None]
    return obj


# String enum → bool mapping used by v2 constraints.json
_ENUM_TO_BOOL: Dict[str, Optional[bool]] = {
    "required": True,
    "prohibited": False,
    "allow": None,      # allowed but not required → omit key
    "allowed": None,    # allowed but not required → omit key
    "optional": None,
}


def _coerce_enum_bools(obj: Any) -> Any:
    """Recursively convert v2 string enums to booleans in constraint data.

    Fields like 'multiple', 'numbered', 'task', 'priority' use string enums
    in v2 JSON ('prohibited'/'allow'/'required'/'optional') but v3 TOML
    expects booleans (true/false) or absent (= allowed/optional).
    """
    _ENUM_FIELDS = {"multiple", "numbered", "task", "priority", "coverage"}
    if isinstance(obj, dict):
        out: Dict[str, Any] = {}
        for k, v in obj.items():
            if k in _ENUM_FIELDS and isinstance(v, str):
                converted = _ENUM_TO_BOOL.get(v.lower())
                if converted is not None:
                    out[k] = converted
                # None means "optional/allowed" → omit the key entirely
            else:
                out[k] = _coerce_enum_bools(v)
        return out
    if isinstance(obj, list):
        return [_coerce_enum_bools(v) for v in obj]
    return obj


def _convert_constraints_v2_to_v3(v2_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert v2 constraints.json format to v3 constraints.toml format.

    Changes:
    - Wraps artifact kinds under 'artifacts' key
    - Converts string enums (prohibited/allow/required/optional) to booleans
    - Strips None values (TOML has no null)
    """
    # v2: {"PRD": {...}, "DESIGN": {...}}
    # v3: {"artifacts": {"PRD": {...}, "DESIGN": {...}}}
    coerced = _coerce_enum_bools(v2_data)
    # v2 had no TOC concept — disable by default for migrated custom kits
    if isinstance(coerced, dict):
        for kind_data in coerced.values():
            if isinstance(kind_data, dict) and "toc" not in kind_data:
                kind_data["toc"] = False
    return _strip_none({"artifacts": coerced})


# ===========================================================================
# WP1: V2 Detection
# ===========================================================================

def detect_core_install_type(project_root: Path, core_path: str) -> str:
    """Detect how the v2 core directory was installed.

    Returns one of: SUBMODULE, GIT_CLONE, PLAIN_DIR, ABSENT.
    """
    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-core-install-type:p1:inst-core-absent
    core_dir = project_root / core_path
    if not core_dir.exists():
        return INSTALL_TYPE_ABSENT
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-core-install-type:p1:inst-core-absent

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-core-install-type:p1:inst-check-gitmodules
    gitmodules = project_root / ".gitmodules"
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-core-install-type:p1:inst-check-gitmodules
    if gitmodules.is_file():
        try:
            content = gitmodules.read_text(encoding="utf-8")
            # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-core-install-type:p1:inst-check-submodule-entry
            pattern = re.compile(
                r'^\s*path\s*=\s*' + re.escape(core_path) + r'\s*$',
                re.MULTILINE,
            )
            # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-core-install-type:p1:inst-check-submodule-entry
            # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-core-install-type:p1:inst-return-submodule
            if pattern.search(content):
                return INSTALL_TYPE_SUBMODULE
            # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-core-install-type:p1:inst-return-submodule
        except OSError:
            pass

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-core-install-type:p1:inst-check-core-git
    git_inside = core_dir / ".git"
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-core-install-type:p1:inst-check-core-git
    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-core-install-type:p1:inst-check-core-git-exists
    if git_inside.exists():
        # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-core-install-type:p1:inst-return-git-clone
        return INSTALL_TYPE_GIT_CLONE
        # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-core-install-type:p1:inst-return-git-clone
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-core-install-type:p1:inst-check-core-git-exists

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-core-install-type:p1:inst-return-plain-dir
    return INSTALL_TYPE_PLAIN_DIR
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-core-install-type:p1:inst-return-plain-dir


def detect_v2(project_root: Path) -> Dict[str, Any]:
    """Detect a v2 Cypilot installation in the project.

    Returns a dict with keys:
        detected (bool), adapter_path, core_path, core_install_type,
        config_path, systems, kits, has_agents_md, has_config_json,
        artifacts_json (parsed content or None).
    """
    result: Dict[str, Any] = {"detected": False}

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-use-defaults
    adapter_path = DEFAULT_V2_ADAPTER
    core_path = DEFAULT_V2_CORE
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-use-defaults

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-check-config-json
    config_json_path = project_root / ".cypilot-config.json"
    has_config_json = config_json_path.is_file()
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-check-config-json

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-parse-config-json
    if has_config_json:
        try:
            cfg = json.loads(config_json_path.read_text(encoding="utf-8"))
            if isinstance(cfg, dict):
                if "cypilotAdapterPath" in cfg:
                    adapter_path = cfg["cypilotAdapterPath"]
                if "cypilotCorePath" in cfg:
                    core_path = cfg["cypilotCorePath"]
        except (json.JSONDecodeError, OSError):
            pass
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-parse-config-json

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-check-adapter-dir
    adapter_dir = project_root / adapter_path
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-check-adapter-dir
    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-adapter-not-found
    if not adapter_dir.is_dir():
        # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-return-not-detected
        if not has_config_json:
            return result
        if not adapter_dir.is_dir():
            result["detected"] = False
            result["error"] = f"Config found but adapter directory '{adapter_path}' missing"
            return result
        # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-return-not-detected
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-adapter-not-found

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-check-artifacts-json
    artifacts_json_file = adapter_dir / "artifacts.json"
    artifacts_data = None
    systems: List[Dict[str, Any]] = []
    kits: Dict[str, Any] = {}
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-check-artifacts-json

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-parse-artifacts-json
    if artifacts_json_file.is_file():
        try:
            artifacts_data = json.loads(
                artifacts_json_file.read_text(encoding="utf-8")
            )
            if isinstance(artifacts_data, dict):
                systems = artifacts_data.get("systems", [])
                kits = artifacts_data.get("kits", {})
        except (json.JSONDecodeError, OSError):
            artifacts_data = None
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-parse-artifacts-json

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-check-adapter-agents
    has_agents_md = (adapter_dir / "AGENTS.md").is_file()
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-check-adapter-agents

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-check-adapter-kits
    adapter_kits_dir = adapter_dir / "kits"
    kit_dirs: List[str] = []
    if adapter_kits_dir.is_dir():
        kit_dirs = [
            d.name for d in sorted(adapter_kits_dir.iterdir()) if d.is_dir()
        ]
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-check-adapter-kits

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-detect-core-type
    core_install_type = detect_core_install_type(project_root, core_path)
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-detect-core-type

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-return-detected
    result.update({
        "detected": True,
        "adapter_path": adapter_path,
        "core_path": core_path,
        "core_install_type": core_install_type,
        "config_path": ".cypilot-config.json" if has_config_json else None,
        "has_config_json": has_config_json,
        "has_agents_md": has_agents_md,
        "systems": systems,
        "kits": kits,
        "kit_dirs": kit_dirs,
        "artifacts_json": artifacts_data,
    })
    return result
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-detect-v2:p1:inst-return-detected


# ===========================================================================
# WP2: Backup & Cleanup
# ===========================================================================

def backup_v2_state(
    project_root: Path,
    adapter_path: str,
    core_path: str,
    core_install_type: str,
) -> Path:
    """Create a complete backup of the v2 project state.

    Returns the backup directory path.
    """
    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1:inst-gen-backup-name
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = project_root / f".cypilot-v2-backup-{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backed_up: List[str] = []
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1:inst-gen-backup-name

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1:inst-backup-adapter
    adapter_dir = project_root / adapter_path
    if adapter_dir.is_dir():
        shutil.copytree(adapter_dir, backup_dir / adapter_path)
        backed_up.append(adapter_path)
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1:inst-backup-adapter

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1:inst-backup-config-json
    for v2_root_file in (".cypilot-config.json", "cypilot-agents.json"):
        v2_path = project_root / v2_root_file
        if v2_path.is_file():
            shutil.copy2(v2_path, backup_dir / v2_root_file)
            backed_up.append(v2_root_file)
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1:inst-backup-config-json

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1:inst-backup-core
    core_dir = project_root / core_path
    if core_dir.is_dir():
        shutil.copytree(core_dir, backup_dir / core_path, symlinks=True)
        backed_up.append(core_path)
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1:inst-backup-core

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1:inst-backup-gitmodules
    if core_install_type == INSTALL_TYPE_SUBMODULE:
        gitmodules = project_root / ".gitmodules"
        if gitmodules.is_file():
            shutil.copy2(gitmodules, backup_dir / ".gitmodules")
            backed_up.append(".gitmodules")
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1:inst-backup-gitmodules

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1:inst-backup-root-agents
    root_agents = project_root / "AGENTS.md"
    if root_agents.is_file():
        shutil.copy2(root_agents, backup_dir / "AGENTS.md")
        backed_up.append("AGENTS.md")
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1:inst-backup-root-agents

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1:inst-backup-agent-dirs
    agent_dirs = [".windsurf", ".cursor", ".claude", ".github"]
    for agent_dir_name in agent_dirs:
        agent_dir = project_root / agent_dir_name
        if agent_dir.is_dir():
            shutil.copytree(agent_dir, backup_dir / agent_dir_name)
            backed_up.append(agent_dir_name)
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1:inst-backup-agent-dirs

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1:inst-write-manifest
    manifest = {
        "timestamp": timestamp,
        "core_install_type": core_install_type,
        "adapter_path": adapter_path,
        "core_path": core_path,
        "backed_up": backed_up,
    }
    (backup_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1:inst-write-manifest

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1:inst-return-backup-path
    return backup_dir
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-backup-v2-state:p1:inst-return-backup-path


def _rollback(project_root: Path, backup_dir: Path) -> Dict[str, Any]:
    """Restore v2 state from backup. Returns rollback result."""
    manifest_file = backup_dir / "manifest.json"
    if not manifest_file.is_file():
        return {"success": False, "error": "Backup manifest not found"}

    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return {"success": False, "error": f"Failed to read manifest: {e}"}

    restored: List[str] = []
    errors: List[str] = []

    for item in manifest.get("backed_up", []):
        src = backup_dir / item
        dst = project_root / item
        try:
            if dst.exists():
                if dst.is_dir():
                    shutil.rmtree(dst)
                else:
                    dst.unlink()
            if src.is_dir():
                shutil.copytree(src, dst, symlinks=True)
            elif src.is_file():
                shutil.copy2(src, dst)
            restored.append(item)
        except OSError as e:
            errors.append(f"Failed to restore {item}: {e}")

    return {
        "success": len(errors) == 0,
        "restored": restored,
        "errors": errors,
    }


def cleanup_core_path(
    project_root: Path,
    core_path: str,
    core_install_type: str,
) -> Dict[str, Any]:
    """Clean up the v2 core directory based on install type.

    Returns dict with success, cleaned_type, warnings.
    """
    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-cleanup-absent
    if core_install_type == INSTALL_TYPE_ABSENT:
        # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-return-absent-ok
        return {"success": True, "cleaned_type": INSTALL_TYPE_ABSENT, "warnings": []}
        # @cpt-end:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-return-absent-ok
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-cleanup-absent

    core_dir = project_root / core_path
    warnings: List[str] = []

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-cleanup-submodule
    if core_install_type == INSTALL_TYPE_SUBMODULE:
        try:
            # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-submodule-deinit
            subprocess.run(
                ["git", "submodule", "deinit", "-f", core_path],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                check=True,
            )
            # @cpt-end:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-submodule-deinit

            # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-git-rm-submodule
            subprocess.run(
                ["git", "rm", "-f", core_path],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                check=False,  # May fail if already removed by deinit
            )
            # @cpt-end:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-git-rm-submodule

            # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-remove-git-modules-dir
            git_modules_dir = project_root / ".git" / "modules" / core_path
            if git_modules_dir.is_dir():
                shutil.rmtree(git_modules_dir)
            # @cpt-end:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-remove-git-modules-dir

            # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-remove-gitmodules-entry
            # git rm updates .gitmodules but may leave the entry in older git;
            # ensure the entry is removed and handle empty .gitmodules
            gitmodules = project_root / ".gitmodules"
            if gitmodules.is_file():
                content = gitmodules.read_text(encoding="utf-8")
                cleaned = _remove_gitmodule_entry(content, core_path)
                # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-delete-empty-gitmodules
                if cleaned.strip():
                    gitmodules.write_text(cleaned, encoding="utf-8")
                    subprocess.run(
                        ["git", "add", ".gitmodules"],
                        cwd=str(project_root),
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                else:
                    gitmodules.unlink()
                    subprocess.run(
                        ["git", "rm", "--cached", ".gitmodules"],
                        cwd=str(project_root),
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                # @cpt-end:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-delete-empty-gitmodules
            # @cpt-end:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-remove-gitmodules-entry

            # Remove leftover empty directory if deinit/git-rm left it
            if core_dir.is_dir():
                shutil.rmtree(core_dir, ignore_errors=True)

            # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-return-submodule-ok
            warnings.append(
                "Submodule removed. Commit the changes to finalize."
            )
            return {
                "success": True,
                "cleaned_type": INSTALL_TYPE_SUBMODULE,
                "warnings": warnings,
            }
            # @cpt-end:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-return-submodule-ok
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "cleaned_type": INSTALL_TYPE_SUBMODULE,
                "warnings": [],
                "error": f"Submodule cleanup failed: {e.stderr or e.stdout or str(e)}",
            }
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-cleanup-submodule

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-cleanup-git-clone
    if core_install_type == INSTALL_TYPE_GIT_CLONE:
        try:
            # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-remove-clone-dir
            shutil.rmtree(core_dir)
            # @cpt-end:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-remove-clone-dir
            # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-return-clone-ok
            warnings.append(
                "Git clone removed. Local git history inside core path is lost."
            )
            return {
                "success": True,
                "cleaned_type": INSTALL_TYPE_GIT_CLONE,
                "warnings": warnings,
            }
            # @cpt-end:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-return-clone-ok
        except OSError as e:
            return {
                "success": False,
                "cleaned_type": INSTALL_TYPE_GIT_CLONE,
                "warnings": [],
                "error": f"Git clone removal failed: {e}",
            }
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-cleanup-git-clone

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-cleanup-plain-dir
    try:
        # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-remove-plain-dir
        shutil.rmtree(core_dir)
        # @cpt-end:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-remove-plain-dir
        # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-return-plain-ok
        return {
            "success": True,
            "cleaned_type": INSTALL_TYPE_PLAIN_DIR,
            "warnings": [],
        }
        # @cpt-end:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-return-plain-ok
    except OSError as e:
        return {
            "success": False,
            "cleaned_type": INSTALL_TYPE_PLAIN_DIR,
            "warnings": [],
            "error": f"Directory removal failed: {e}",
        }
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-cleanup-core-path:p1:inst-cleanup-plain-dir


def _remove_gitmodule_entry(content: str, path: str) -> str:
    """Remove a [submodule "..."] block from .gitmodules content by path."""
    lines = content.splitlines(True)
    result: List[str] = []
    skip = False
    for line in lines:
        if re.match(r'^\[submodule\s+"[^"]*"\]\s*$', line):
            skip = False  # Reset for each new section
        if skip:
            continue
        # Check if this is a section whose path matches
        if re.match(r'^\[submodule\s+"[^"]*"\]\s*$', line):
            # Look ahead for path = <core_path>
            idx = lines.index(line)
            block_lines = [line]
            j = idx + 1
            while j < len(lines) and not lines[j].startswith("["):
                block_lines.append(lines[j])
                j += 1
            block_text = "".join(block_lines)
            pattern = re.compile(
                r'^\s*path\s*=\s*' + re.escape(path) + r'\s*$',
                re.MULTILINE,
            )
            if pattern.search(block_text):
                skip = True
                continue
        result.append(line)
    return "".join(result)


# ===========================================================================
# WP3: Config Conversion
# ===========================================================================

def convert_artifacts_registry(
    artifacts_json: Dict[str, Any],
    target_dir: Path,
) -> Dict[str, Any]:
    """Convert v2 artifacts.json to v3 artifacts.toml.

    Args:
        artifacts_json: Parsed v2 artifacts.json content.
        target_dir: Directory to write artifacts.toml into (config/).

    Returns:
        Dict with systems_count, kits_count, kit_slug_map, warnings.
    """
    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1:inst-parse-v2-registry
    warnings: List[str] = []
    v2_kits = artifacts_json.get("kits", {})
    v2_systems = artifacts_json.get("systems", [])
    v2_ignore = artifacts_json.get("ignore", [])
    kit_slug_map: Dict[str, str] = {}
    v3_kits: Dict[str, Any] = {}
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1:inst-parse-v2-registry

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1:inst-iterate-kits
    for v2_slug, v2_kit_data in v2_kits.items():
        # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1:inst-preserve-kit-slug
        kit_slug_map[v2_slug] = v2_slug
        # @cpt-end:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1:inst-preserve-kit-slug
        # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1:inst-map-kit-path
        v3_kits[v2_slug] = {
            "format": v2_kit_data.get("format", "Cypilot"),
            "path": f"config/kits/{v2_slug}",
        }
        # @cpt-end:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1:inst-map-kit-path
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1:inst-iterate-kits

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1:inst-iterate-systems
    v3_systems: List[Dict[str, Any]] = []
    for system in v2_systems:
        v3_system = _convert_system(system, kit_slug_map)
        v3_systems.append(v3_system)
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1:inst-iterate-systems

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1:inst-convert-ignore-rules
    v3_ignore: List[Dict[str, Any]] = []
    for rule in v2_ignore:
        v3_ignore.append({
            "reason": rule.get("reason", ""),
            "patterns": rule.get("patterns", []),
        })
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1:inst-convert-ignore-rules

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1:inst-serialize-artifacts-toml
    # NOTE: kits are NOT written to artifacts.toml — they belong only in core.toml
    registry: Dict[str, Any] = {}
    if v3_ignore:
        registry["ignore"] = v3_ignore
    if v3_systems:
        registry["systems"] = v3_systems
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1:inst-serialize-artifacts-toml

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1:inst-write-artifacts-toml
    target_dir.mkdir(parents=True, exist_ok=True)
    toml_utils.dump(
        _strip_none(registry),
        target_dir / "artifacts.toml",
        header_comment="Cypilot artifacts registry (migrated from v2)",
    )
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1:inst-write-artifacts-toml

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1:inst-return-artifacts-result
    return {
        "systems_count": len(v3_systems),
        "kits_count": len(v3_kits),
        "kit_slug_map": kit_slug_map,
        "warnings": warnings,
    }
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-convert-artifacts-registry:p1:inst-return-artifacts-result


def _convert_system(
    system: Dict[str, Any],
    kit_slug_map: Dict[str, str],
) -> Dict[str, Any]:
    """Convert a single v2 system entry to v3 format."""
    v3: Dict[str, Any] = {
        "name": system.get("name", ""),
        "slug": system.get("slug", ""),
    }

    # Remap kit reference
    v2_kit = system.get("kit", "")
    v3["kit"] = kit_slug_map.get(v2_kit, v2_kit)

    # Convert autodetect rules
    autodetect = system.get("autodetect", [])
    if autodetect:
        v3["autodetect"] = []
        for rule in autodetect:
            v3_rule: Dict[str, Any] = {}
            # Remap kit in autodetect rule too
            rule_kit = rule.get("kit", v2_kit)
            v3_rule["kit"] = kit_slug_map.get(rule_kit, rule_kit)

            for key in ("system_root", "artifacts_root"):
                if key in rule:
                    v3_rule[key] = rule[key]

            if "artifacts" in rule:
                v3_rule["artifacts"] = rule["artifacts"]

            if "codebase" in rule:
                v3_rule["codebase"] = rule["codebase"]

            if "validation" in rule:
                v3_rule["validation"] = rule["validation"]

            v3["autodetect"].append(v3_rule)

    # Convert children recursively
    children = system.get("children", [])
    if children:
        v3["children"] = [_convert_system(c, kit_slug_map) for c in children]

    return v3


def convert_agents_md(
    project_root: Path,
    adapter_path: str,
    target_dir: Path,
) -> Dict[str, Any]:
    """Convert v2 adapter AGENTS.md to v3 config/AGENTS.md.

    Returns dict with skipped, rules_migrated, paths_updated.
    """
    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-convert-agents-md:p1:inst-read-adapter-agents
    adapter_agents = project_root / adapter_path / "AGENTS.md"
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-convert-agents-md:p1:inst-read-adapter-agents
    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-convert-agents-md:p1:inst-check-adapter-agents-exists
    if not adapter_agents.is_file():
        return {"skipped": True, "reason": "No adapter AGENTS.md"}
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-convert-agents-md:p1:inst-check-adapter-agents-exists

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-convert-agents-md:p1:inst-parse-agents-content
    try:
        content = adapter_agents.read_text(encoding="utf-8")
    except OSError as e:
        return {"skipped": True, "reason": f"Failed to read: {e}"}
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-convert-agents-md:p1:inst-parse-agents-content

    paths_updated = 0

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-convert-agents-md:p1:inst-convert-adapter-paths
    replacements = [
        ("{cypilot_adapter_path}", "{cypilot_path}/config"),
        (f"`{adapter_path}/", "`{cypilot_path}/config/"),
        (f"`{adapter_path}`", "`{cypilot_path}/config`"),
    ]
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            paths_updated += 1
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-convert-agents-md:p1:inst-convert-adapter-paths

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-convert-agents-md:p1:inst-remove-extends-ref
    extends_pattern = re.compile(
        r'\n\*\*Extends\*\*:\s*`[^`]*\.cypilot/AGENTS\.md`\s*\n',
        re.IGNORECASE,
    )
    content = extends_pattern.sub('\n', content)
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-convert-agents-md:p1:inst-remove-extends-ref

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-convert-agents-md:p1:inst-update-registry-refs
    content = content.replace("artifacts.json", "artifacts.toml")
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-convert-agents-md:p1:inst-update-registry-refs

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-convert-agents-md:p1:inst-write-config-agents
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "AGENTS.md").write_text(content, encoding="utf-8")
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-convert-agents-md:p1:inst-write-config-agents

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-convert-agents-md:p1:inst-return-agents-result
    return {
        "skipped": False,
        "paths_updated": paths_updated,
    }
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-convert-agents-md:p1:inst-return-agents-result


def generate_core_toml(
    project_root: Path,
    v2_systems: List[Dict[str, Any]],
    kit_slug_map: Dict[str, str],
    target_dir: Path,
) -> Dict[str, Any]:
    """Generate v3 core.toml from v2 project state.

    Args:
        project_root: Project root path.
        v2_systems: List of v2 system definitions.
        kit_slug_map: v2_slug → v3_slug mapping (identity).
        target_dir: Directory to write core.toml into (config/).

    Returns:
        Dict with status.
    """
    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-generate-core-toml:p1:inst-derive-project-info
    project_name = project_root.name
    slug_parts = re.split(r'[-_\s]+', project_name.lower())
    pascal_name = "".join(w.capitalize() for w in slug_parts) if slug_parts else "Unnamed"
    project_slug = "-".join(slug_parts) if slug_parts else "unnamed"
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-generate-core-toml:p1:inst-derive-project-info

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-generate-core-toml:p1:inst-set-schema-version
    core_data: Dict[str, Any] = {
        "version": "1.0",
        # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-generate-core-toml:p1:inst-set-project-root
        "project_root": "..",
        # @cpt-end:cpt-cypilot-algo-v2-v3-migration-generate-core-toml:p1:inst-set-project-root
    }
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-generate-core-toml:p1:inst-set-schema-version

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-generate-core-toml:p1:inst-iterate-v2-systems
    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-generate-core-toml:p1:inst-create-system-entry
    if v2_systems:
        primary = v2_systems[0]
        v2_kit = primary.get("kit", "")
        core_data["system"] = {
            "name": primary.get("name", pascal_name),
            "slug": primary.get("slug", project_slug),
            "kit": kit_slug_map.get(v2_kit, v2_kit),
        }
    else:
        core_data["system"] = {
            "name": pascal_name,
            "slug": project_slug,
            "kit": "cypilot-sdlc",
        }
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-generate-core-toml:p1:inst-create-system-entry
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-generate-core-toml:p1:inst-iterate-v2-systems

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-generate-core-toml:p1:inst-register-kits
    kits_registry: Dict[str, Any] = {}
    for v2_slug, v3_slug in kit_slug_map.items():
        kits_registry[v3_slug] = {
            "format": "Cypilot",
            "path": f"config/kits/{v2_slug}",
        }
    if kits_registry:
        core_data["kits"] = kits_registry
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-generate-core-toml:p1:inst-register-kits

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-generate-core-toml:p1:inst-write-core-toml
    target_dir.mkdir(parents=True, exist_ok=True)
    toml_utils.dump(
        _strip_none(core_data),
        target_dir / "core.toml",
        header_comment="Cypilot project configuration (migrated from v2)",
    )
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-generate-core-toml:p1:inst-write-core-toml

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-generate-core-toml:p1:inst-return-core-result
    return {"status": "created"}
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-generate-core-toml:p1:inst-return-core-result


# ===========================================================================
# WP4: Kit Migration
# ===========================================================================

def migrate_kits(
    v2_kits: Dict[str, Any],
    adapter_path: str,
    project_root: Path,
    cypilot_dir: Path,
) -> Dict[str, Any]:
    """Migrate kits from v2 to v3.

    Every kit is copied from adapter as-is with constraints.json → constraints.toml
    conversion. Slugs are preserved. Run `cpt update` after migration to regenerate.

    Returns dict with migrated_kits, warnings, errors.
    """
    migrated_kits: List[str] = []
    warnings: List[str] = []
    errors: List[str] = []

    config_dir = cypilot_dir / "config"
    gen_dir = cypilot_dir / GEN_SUBDIR
    adapter_dir = project_root / adapter_path

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-migrate-kits:p1:inst-iterate-kits-migrate
    for v2_slug in v2_kits:
        # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-migrate-kits:p1:inst-locate-kit-dir
        v2_kit_dir = adapter_dir / "kits" / v2_slug
        config_kit_dir = config_dir / "kits" / v2_slug
        # @cpt-end:cpt-cypilot-algo-v2-v3-migration-migrate-kits:p1:inst-locate-kit-dir

        if not v2_kit_dir.is_dir():
            # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-migrate-kits:p1:inst-kit-dir-missing
            warnings.append(
                f"Kit '{v2_slug}' directory not found at {v2_kit_dir}"
            )
            # @cpt-end:cpt-cypilot-algo-v2-v3-migration-migrate-kits:p1:inst-kit-dir-missing
            continue

        # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-migrate-kits:p1:inst-copy-kit-config
        config_kit_dir.mkdir(parents=True, exist_ok=True)
        _copy_tree_contents(v2_kit_dir, config_kit_dir)
        # @cpt-end:cpt-cypilot-algo-v2-v3-migration-migrate-kits:p1:inst-copy-kit-config

        # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-migrate-kits:p1:inst-convert-constraints
        # Convert constraints.json → constraints.toml in config/kits/
        # (.gen/ is ephemeral — regenerated by cpt update)
        constraints_json = config_kit_dir / "constraints.json"
        if constraints_json.is_file():
            try:
                raw_data = json.loads(
                    constraints_json.read_text(encoding="utf-8")
                )
                v3_data = _convert_constraints_v2_to_v3(raw_data)
                toml_utils.dump(
                    v3_data,
                    config_kit_dir / "constraints.toml",
                    header_comment=f"Constraints for kit '{v2_slug}' (migrated from constraints.json)",
                )
                constraints_json.unlink()
                # Validate the converted constraints
                from ..utils.constraints import load_constraints_toml
                _, parse_errors = load_constraints_toml(config_kit_dir)
                if parse_errors:
                    for pe in parse_errors:
                        errors.append(
                            f"Kit '{v2_slug}' constraints.toml validation: {pe}"
                        )
            except (json.JSONDecodeError, OSError, TypeError) as e:
                errors.append(
                    f"Failed to convert constraints.json for kit '{v2_slug}': {e}"
                )
        # @cpt-end:cpt-cypilot-algo-v2-v3-migration-migrate-kits:p1:inst-convert-constraints

        # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-migrate-kits:p1:inst-add-migrated-kit
        migrated_kits.append(v2_slug)
        # @cpt-end:cpt-cypilot-algo-v2-v3-migration-migrate-kits:p1:inst-add-migrated-kit
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-migrate-kits:p1:inst-iterate-kits-migrate

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-migrate-kits:p1:inst-return-kits-result
    return {
        "migrated_kits": migrated_kits,
        "warnings": warnings,
        "errors": errors,
    }
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-migrate-kits:p1:inst-return-kits-result


def _copy_tree_contents(src: Path, dst: Path) -> None:
    """Copy contents of src directory into dst (merging, not replacing)."""
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


# ===========================================================================
# WP5: Integration — Validation + Main Flow
# ===========================================================================

def validate_migration(
    project_root: Path,
    cypilot_dir: Path,
    v2_detection: Dict[str, Any],
) -> Dict[str, Any]:
    """Validate migration completeness.

    Returns dict with passed (bool) and issues list.
    """
    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-collect-issues
    issues: List[Dict[str, str]] = []
    config_dir = cypilot_dir / "config"
    gen_dir = cypilot_dir / GEN_SUBDIR
    core_dir = cypilot_dir / CORE_SUBDIR
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-collect-issues

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-verify-core-toml
    core_toml = config_dir / "core.toml"
    if not core_toml.is_file():
        # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-record-issue
        issues.append({
            "severity": "CRITICAL",
            "file": str(core_toml),
            "message": "core.toml not found",
        })
        # @cpt-end:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-record-issue
    else:
        try:
            toml_utils.load(core_toml)
        except Exception as e:
            issues.append({
                "severity": "CRITICAL",
                "file": str(core_toml),
                "message": f"core.toml parse error: {e}",
            })
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-verify-core-toml

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-verify-artifacts-toml
    artifacts_toml = config_dir / "artifacts.toml"
    if not artifacts_toml.is_file():
        issues.append({
            "severity": "CRITICAL",
            "file": str(artifacts_toml),
            "message": "artifacts.toml not found",
        })
    else:
        try:
            registry = toml_utils.load(artifacts_toml)
            # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-verify-systems-migrated
            v2_system_count = len(v2_detection.get("systems", []))
            v3_systems = registry.get("systems", [])
            if len(v3_systems) != v2_system_count:
                issues.append({
                    "severity": "HIGH",
                    "file": str(artifacts_toml),
                    "message": (
                        f"System count mismatch: v2 had {v2_system_count}, "
                        f"v3 has {len(v3_systems)}"
                    ),
                })
            # @cpt-end:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-verify-systems-migrated
        except Exception as e:
            issues.append({
                "severity": "CRITICAL",
                "file": str(artifacts_toml),
                "message": f"artifacts.toml parse error: {e}",
            })
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-verify-artifacts-toml

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-verify-root-agents-block
    root_agents = project_root / "AGENTS.md"
    if root_agents.is_file():
        try:
            content = root_agents.read_text(encoding="utf-8")
            if "<!-- @cpt:root-agents -->" not in content:
                issues.append({
                    "severity": "HIGH",
                    "file": str(root_agents),
                    "message": "Root AGENTS.md missing managed block",
                })
        except OSError:
            issues.append({
                "severity": "HIGH",
                "file": str(root_agents),
                "message": "Failed to read root AGENTS.md",
            })
    else:
        issues.append({
            "severity": "HIGH",
            "file": str(root_agents),
            "message": "Root AGENTS.md not found",
        })
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-verify-root-agents-block

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-verify-config-agents
    if v2_detection.get("has_agents_md"):
        config_agents = config_dir / "AGENTS.md"
        if not config_agents.is_file():
            issues.append({
                "severity": "MEDIUM",
                "file": str(config_agents),
                "message": "config/AGENTS.md not found (v2 had adapter AGENTS.md)",
            })
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-verify-config-agents

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-verify-core-dir
    if not core_dir.is_dir():
        issues.append({
            "severity": "CRITICAL",
            "file": str(core_dir),
            "message": ".core/ directory not found",
        })
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-verify-core-dir

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-verify-gen-dir
    if not gen_dir.is_dir():
        issues.append({
            "severity": "CRITICAL",
            "file": str(gen_dir),
            "message": ".gen/ directory not found",
        })
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-verify-gen-dir

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-verify-agent-entries
    for agent_dir_name in (".windsurf", ".cursor", ".claude"):
        agent_dir = project_root / agent_dir_name
        if not agent_dir.is_dir():
            issues.append({
                "severity": "LOW",
                "file": str(agent_dir),
                "message": f"Agent entry point directory {agent_dir_name}/ not found",
            })
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-verify-agent-entries

    # @cpt-begin:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-return-validation-result
    return {
        "passed": len(issues) == 0,
        "issues": issues,
    }
    # @cpt-end:cpt-cypilot-algo-v2-v3-migration-validate-migration:p1:inst-return-validation-result


# ===========================================================================
# Main migration flow
# ===========================================================================

def run_migrate(
    project_root: Path,
    install_dir: Optional[str] = None,
    yes: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Execute the full v2 → v3 migration.

    Returns a result dict with status, actions, and any errors.
    """
    # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-detect-v2
    # @cpt-begin:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-detected
    state = STATE_NOT_STARTED

    v2 = detect_v2(project_root)
    # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-check-v2-found
    if not v2["detected"]:
        # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-return-no-v2
        return {
            "status": "ERROR",
            "state": state,
            "message": "No v2 installation found. Use `cypilot init` for new projects.",
        }
        # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-return-no-v2
    state = STATE_DETECTED
    # @cpt-end:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-detected
    # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-check-v2-found
    # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-detect-v2

    adapter_path = v2["adapter_path"]
    core_path = v2["core_path"]
    core_install_type = v2["core_install_type"]

    # Derive install dir from v2 core path if not explicitly set
    if install_dir is None:
        install_dir = core_path if core_path else DEFAULT_V3_INSTALL_DIR

    # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-show-plan
    plan = {
        "adapter_path": adapter_path,
        "core_path": core_path,
        "core_install_type": core_install_type,
        "target_dir": install_dir,
        "systems_count": len(v2.get("systems", [])),
        "kits": list(v2.get("kits", {}).keys()),
        "has_agents_md": v2.get("has_agents_md", False),
        "has_config_json": v2.get("has_config_json", False),
    }

    if dry_run:
        return {
            "status": "DRY_RUN",
            "state": state,
            "plan": plan,
            "v2_detection": v2,
        }
    # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-show-plan

    # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-check-user-confirm
    if not yes:
        sys.stderr.write("\n=== V2 → V3 Migration Plan ===\n")
        sys.stderr.write(f"  Adapter path: {adapter_path}\n")
        sys.stderr.write(f"  Core path:    {core_path} ({core_install_type})\n")
        sys.stderr.write(f"  Target dir:   {install_dir}/\n")
        sys.stderr.write(f"  Systems:      {plan['systems_count']}\n")
        sys.stderr.write(f"  Kits:         {', '.join(plan['kits']) or 'none'}\n")
        sys.stderr.write(f"  AGENTS.md:    {'yes' if plan['has_agents_md'] else 'no'}\n")
        sys.stderr.write("\nProceed with migration? [y/N]: ")
        sys.stderr.flush()
        try:
            answer = input().strip().lower()
        except EOFError:
            answer = ""
        if answer not in ("y", "yes"):
            # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-return-cancelled
            return {
                "status": "CANCELLED",
                "state": state,
                "message": "Migration cancelled by user.",
            }
            # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-return-cancelled
    # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-check-user-confirm

    # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-create-backup
    # @cpt-begin:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-backed-up
    try:
        backup_dir = backup_v2_state(
            project_root, adapter_path, core_path, core_install_type,
        )
        state = STATE_BACKED_UP
    except OSError as e:
        return {
            "status": "ERROR",
            "state": state,
            "message": f"Backup failed: {e}",
        }
    # @cpt-end:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-backed-up
    # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-create-backup

    # @cpt-begin:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-converting
    state = STATE_CONVERTING
    all_warnings: List[str] = []
    cypilot_dir = project_root / install_dir
    config_dir = cypilot_dir / "config"
    # @cpt-end:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-converting

    try:
        # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-cleanup-core
        cleanup_result = cleanup_core_path(project_root, core_path, core_install_type)
        if not cleanup_result.get("success"):
            raise RuntimeError(
                f"Core cleanup failed: {cleanup_result.get('error', 'unknown')}"
            )
        all_warnings.extend(cleanup_result.get("warnings", []))
        # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-cleanup-core

        # Step 4: Initialize v3 directory structure using init's _copy_from_cache
        from .init import _copy_from_cache, _core_readme, _gen_readme, _config_readme

        cypilot_dir.mkdir(parents=True, exist_ok=True)
        config_dir.mkdir(parents=True, exist_ok=True)
        gen_dir = cypilot_dir / GEN_SUBDIR
        gen_dir.mkdir(parents=True, exist_ok=True)
        core_dir = cypilot_dir / CORE_SUBDIR
        core_dir.mkdir(parents=True, exist_ok=True)

        # Copy core files from cache
        if CACHE_DIR.is_dir():
            _copy_from_cache(CACHE_DIR, cypilot_dir, force=True)

        # Write READMEs
        (core_dir / "README.md").write_text(_core_readme(), encoding="utf-8")
        (gen_dir / "README.md").write_text(_gen_readme(), encoding="utf-8")
        (config_dir / "README.md").write_text(_config_readme(), encoding="utf-8")

        # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-convert-artifacts
        artifacts_json = v2.get("artifacts_json")
        kit_slug_map: Dict[str, str] = {}
        if artifacts_json:
            reg_result = convert_artifacts_registry(
                artifacts_json, config_dir,
            )
            all_warnings.extend(reg_result.get("warnings", []))
            kit_slug_map = reg_result.get("kit_slug_map", {})
        # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-convert-artifacts

        # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-register-kit-dirs
        # Register kit_dirs not already in kit_slug_map (kits on disk
        # but missing from artifacts.json)
        v2_kits = dict(v2.get("kits", {}))
        for kit_dir_name in v2.get("kit_dirs", []):
            if kit_dir_name not in kit_slug_map:
                kit_slug_map[kit_dir_name] = kit_dir_name
            if kit_dir_name not in v2_kits:
                v2_kits[kit_dir_name] = {"format": "Cypilot"}
        # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-register-kit-dirs

        # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-convert-agents
        agents_result = convert_agents_md(project_root, adapter_path, config_dir)
        if agents_result.get("skipped"):
            # Write empty config/AGENTS.md
            if not (config_dir / "AGENTS.md").is_file():
                (config_dir / "AGENTS.md").write_text(
                    "# Custom Agent Navigation Rules\n\n"
                    "Add your project-specific WHEN rules here.\n",
                    encoding="utf-8",
                )
        # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-convert-agents

        # Write config/SKILL.md if not exists
        config_skill = config_dir / "SKILL.md"
        if not config_skill.is_file():
            config_skill.write_text(
                "# Custom Skill Extensions\n\n"
                "Add your project-specific skill instructions here.\n",
                encoding="utf-8",
            )

        # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-generate-core-toml
        generate_core_toml(
            project_root,
            v2.get("systems", []),
            kit_slug_map,
            config_dir,
        )
        # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-generate-core-toml

        # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-migrate-kits
        kit_result = migrate_kits(
            v2_kits,
            adapter_path,
            project_root,
            cypilot_dir,
        )
        all_warnings.extend(kit_result.get("warnings", []))
        if kit_result.get("errors"):
            all_warnings.extend(
                f"Kit error: {e}" for e in kit_result["errors"]
            )
        # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-migrate-kits

        # Step 8b: Clean up adapter directory (already backed up)
        # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-cleanup-adapter
        adapter_dir_path = project_root / adapter_path
        if adapter_dir_path.is_dir():
            shutil.rmtree(adapter_dir_path)
        # Also remove v2 root config files
        for v2_root_file in (".cypilot-config.json", "cypilot-agents.json"):
            v2_path = project_root / v2_root_file
            if v2_path.is_file():
                v2_path.unlink()
        # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-cleanup-adapter

        # Step 8c: Write .gen/AGENTS.md (generated navigation rules)
        # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-write-gen-agents
        _write_gen_agents(gen_dir, project_root.name)
        # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-write-gen-agents

        # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-inject-root-agents
        from .init import _inject_root_agents
        _inject_root_agents(project_root, install_dir)
        # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-inject-root-agents

        # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-regen-agent-entries
        try:
            from .agents import cmd_agents as _cmd_agents_fn
            _cmd_agents_fn([
                "--root", str(project_root),
                "--cypilot-root", str(cypilot_dir),
            ])
        except SystemExit:
            pass  # cmd_agents may raise SystemExit on success
        except Exception as e:
            all_warnings.append(f"Agent entry point regeneration failed: {e}")
        # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-regen-agent-entries

    except Exception as e:
        # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-rollback-on-fail
        # Rollback on any failure during conversion
        # @cpt-begin:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-convert-rollback
        rollback_result = _rollback(project_root, backup_dir)
        if rollback_result.get("success"):
            state = STATE_ROLLED_BACK
            return {
                "status": "ERROR",
                "state": state,
                "message": f"Migration failed: {e}. Rolled back successfully.",
                "backup_dir": str(backup_dir),
                "rollback": rollback_result,
            }
        else:
            # @cpt-begin:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-failed
            state = STATE_FAILED
            return {
                "status": "CRITICAL_ERROR",
                "state": state,
                "message": (
                    f"Migration failed: {e}. "
                    f"Rollback also failed: {rollback_result.get('errors')}. "
                    f"Manual recovery from backup: {backup_dir}"
                ),
                "backup_dir": str(backup_dir),
                "rollback": rollback_result,
            }
            # @cpt-end:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-failed
        # @cpt-end:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-convert-rollback
        # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-rollback-on-fail

    # @cpt-begin:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-converted
    state = STATE_CONVERTED
    # @cpt-end:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-converted

    # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-validate-migration
    # @cpt-begin:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-validating
    state = STATE_VALIDATING
    validation = validate_migration(project_root, cypilot_dir, v2)
    # @cpt-end:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-validating
    # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-validate-migration

    # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-check-validation
    if not validation["passed"]:
        # Rollback on validation failure
        # @cpt-begin:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-rolled-back
        rollback_result = _rollback(project_root, backup_dir)
        if rollback_result.get("success"):
            state = STATE_ROLLED_BACK
            return {
                "status": "VALIDATION_FAILED",
                "state": state,
                "message": "Post-migration validation failed. Rolled back.",
                "validation": validation,
                "backup_dir": str(backup_dir),
                "rollback": rollback_result,
            }
        else:
            # @cpt-begin:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-validate-failed
            state = STATE_FAILED
            return {
                "status": "CRITICAL_ERROR",
                "state": state,
                "message": (
                    "Post-migration validation failed and rollback also failed. "
                    f"Manual recovery from backup: {backup_dir}"
                ),
                "validation": validation,
                "backup_dir": str(backup_dir),
                "rollback": rollback_result,
            }
            # @cpt-end:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-validate-failed
        # @cpt-end:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-rolled-back
    # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-check-validation

    # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-return-success
    # @cpt-begin:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-completed
    state = STATE_COMPLETED
    return {
        "status": "PASS",
        "state": state,
        "message": "Migration completed successfully.",
        "project_root": str(project_root),
        "cypilot_dir": str(cypilot_dir),
        "backup_dir": str(backup_dir),
        "plan": plan,
        "kit_result": kit_result,
        "warnings": all_warnings,
        "validation": validation,
    }
    # @cpt-end:cpt-cypilot-state-v2-v3-migration-status:p1:inst-transition-completed
    # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-project:p1:inst-return-success


def _write_gen_agents(gen_dir: Path, project_name: str) -> None:
    """Write .gen/AGENTS.md with generated navigation rules."""
    kit_id = "cypilot-sdlc"
    artifacts_when = (
        f"ALWAYS open and follow `{{cypilot_path}}/config/artifacts.toml` "
        f"WHEN Cypilot uses kit `{kit_id}` for artifact kinds: "
        f"PRD, DESIGN, DECOMPOSITION, ADR, FEATURE OR codebase"
    )
    content = "\n".join([
        f"# Cypilot: {project_name}",
        "",
        "## Navigation Rules",
        "",
        "ALWAYS open and follow `{cypilot_path}/.core/schemas/artifacts.schema.json` WHEN working with artifacts.toml",
        "",
        "ALWAYS open and follow `{cypilot_path}/.core/architecture/specs/artifacts-registry.md` WHEN working with artifacts.toml",
        "",
        artifacts_when,
        "",
    ])
    gen_dir.mkdir(parents=True, exist_ok=True)
    (gen_dir / "AGENTS.md").write_text(content, encoding="utf-8")


# ===========================================================================
# Migrate Config Flow (JSON → TOML)
# ===========================================================================

def run_migrate_config(project_root: Path) -> Dict[str, Any]:
    """Convert remaining JSON config files to TOML.

    Scans config/ and adapter directories for .json files.
    Converts each independently — failure in one doesn't block others.
    """
    converted: List[str] = []
    skipped: List[Dict[str, str]] = []

    # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1:inst-scan-json-files
    scan_dirs = []
    for candidate in ("config", ".cypilot-adapter", DEFAULT_V2_ADAPTER):
        d = project_root / candidate
        if d.is_dir():
            scan_dirs.append(d)

    json_files: List[Path] = []
    for d in scan_dirs:
        json_files.extend(d.glob("*.json"))
    # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1:inst-scan-json-files

    # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1:inst-iterate-json-files
    for json_file in json_files:
        toml_file = json_file.with_suffix(".toml")
        if toml_file.is_file():
            skipped.append({
                "file": str(json_file),
                "reason": "TOML version already exists",
            })
            continue

        # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1:inst-try-convert
        try:
            # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1:inst-parse-json
            data = json.loads(json_file.read_text(encoding="utf-8"))
            # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1:inst-parse-json
            # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1:inst-write-toml
            toml_utils.dump(_strip_none(data), toml_file)
            # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1:inst-write-toml
            # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1:inst-remove-json
            json_file.unlink()
            converted.append(str(json_file))
            # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1:inst-remove-json
        except (json.JSONDecodeError, OSError, TypeError) as e:
            # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1:inst-catch-convert-error
            # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1:inst-log-convert-error
            skipped.append({
                "file": str(json_file),
                "reason": str(e),
            })
            # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1:inst-log-convert-error
            # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1:inst-catch-convert-error
        # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1:inst-try-convert
    # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1:inst-iterate-json-files

    # @cpt-begin:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1:inst-return-config-summary
    return {
        "converted_count": len(converted),
        "skipped_count": len(skipped),
        "converted": converted,
        "skipped": skipped,
    }
    # @cpt-end:cpt-cypilot-flow-v2-v3-migration-migrate-config:p1:inst-return-config-summary


# ===========================================================================
# WP6: CLI Entry Points
# ===========================================================================

def cmd_migrate(argv: List[str]) -> int:
    """CLI handler for `cypilot migrate`."""
    p = argparse.ArgumentParser(
        prog="migrate",
        description="Migrate a v2 Cypilot project to v3",
    )
    p.add_argument(
        "--project-root", default=None,
        help="Project root directory (default: current directory)",
    )
    p.add_argument(
        "--install-dir", default=None,
        help=f"Cypilot directory relative to project root (default: derived from v2 core path, fallback: {DEFAULT_V3_INSTALL_DIR})",
    )
    p.add_argument("--yes", action="store_true", help="Skip confirmation prompt")
    p.add_argument("--dry-run", action="store_true", help="Detect and show plan only")
    args = p.parse_args(argv)

    project_root = Path(args.project_root).resolve() if args.project_root else Path.cwd().resolve()

    result = run_migrate(
        project_root,
        install_dir=args.install_dir,
        yes=args.yes,
        dry_run=args.dry_run,
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result.get("status") == "PASS":
        return 0
    elif result.get("status") == "DRY_RUN":
        return 0
    elif result.get("status") == "CANCELLED":
        return 0
    else:
        return 1


def cmd_migrate_config(argv: List[str]) -> int:
    """CLI handler for `cypilot migrate-config`."""
    p = argparse.ArgumentParser(
        prog="migrate-config",
        description="Convert remaining JSON config files to TOML",
    )
    p.add_argument(
        "--project-root", default=None,
        help="Project root directory (default: current directory)",
    )
    args = p.parse_args(argv)

    project_root = Path(args.project_root).resolve() if args.project_root else Path.cwd().resolve()

    result = run_migrate_config(project_root)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return 0
