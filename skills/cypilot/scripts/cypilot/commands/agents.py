"""
Agent Entry Point Generator

Generates agent-native entry points (Windsurf, Cursor, Claude, Copilot, OpenAI),
composes SKILL.md from kit @cpt:skill sections, and creates workflow proxies.

@cpt-flow:cpt-cypilot-flow-agent-integration-generate:p1
@cpt-flow:cpt-cypilot-flow-agent-integration-workflow:p1
@cpt-flow:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1
@cpt-algo:cpt-cypilot-algo-agent-integration-discover-agents:p1
@cpt-algo:cpt-cypilot-algo-agent-integration-generate-shims:p1
@cpt-algo:cpt-cypilot-algo-agent-integration-compose-skill:p1
@cpt-algo:cpt-cypilot-algo-agent-integration-list-workflows:p1
@cpt-state:cpt-cypilot-state-agent-integration-entry-points:p1
@cpt-dod:cpt-cypilot-dod-agent-integration-entry-points:p1
@cpt-dod:cpt-cypilot-dod-agent-integration-skill-composition:p1
@cpt-dod:cpt-cypilot-dod-agent-integration-workflow-discovery:p1
@cpt-dod:cpt-cypilot-dod-project-extensibility-backward-compat:p1
"""

import argparse
import json
import os
import re
import shutil
import sys
import tomllib
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ..utils.files import core_subpath, config_subpath, find_project_root, _is_cypilot_root, _read_cypilot_var, load_project_config
from ..utils.ui import ui

# Phase 8: Multi-layer pipeline imports
from ..utils.manifest import ManifestLayerState as _ManifestLayerState
from ..utils.layer_discovery import discover_layers as _discover_layers
from ..utils.manifest import resolve_includes as _resolve_includes, merge_components as _merge_components
from ..commands.resolve_vars import add_layer_variables as _add_layer_variables

# @cpt-begin:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-v2-detect
def _layers_have_v2_manifests(layers: list) -> bool:
    """Return True if any loaded layer has a v2.0 manifest with components."""
    for layer in layers:
        if layer.state == _ManifestLayerState.LOADED and layer.manifest is not None:
            m = layer.manifest
            if m.version == "2.0" and (m.agents or m.skills or m.workflows or m.rules or m.includes):
                return True
    return False
# @cpt-end:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-v2-detect


# @cpt-begin:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-path-helpers
def _safe_relpath(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()

def _target_path_from_root(target: Path, project_root: Path, cypilot_root: Optional[Path] = None) -> str:
    """Return agent-instruction path using ``{cypilot_path}/`` variable prefix.

    If *target* is inside *cypilot_root*, returns ``{cypilot_path}/<relative>``
    which is portable — the variable is defined in root AGENTS.md.

    Falls back to ``@/<project-root-relative>`` for paths outside cypilot_root.
    """
    if cypilot_root is not None:
        try:
            rel = target.relative_to(cypilot_root).as_posix()
            return "{cypilot_path}/" + rel
        except ValueError:
            pass
    try:
        rel = target.relative_to(project_root).as_posix()
        return "{cypilot_path}/" + rel if cypilot_root is None else f"@/{rel}"
    except ValueError:
        sys.stderr.write(
            f"WARNING: path {target} is outside project root {project_root}, "
            "agent proxy will contain an absolute path\n"
        )
        return target.as_posix()
# @cpt-end:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-path-helpers

# @cpt-begin:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-ensure-local-copy
# Directories and files to copy when cypilot is external to the project.
_COPY_DIRS = ["workflows", "requirements", "schemas", "templates", "prompts", "kits", "architecture", "skills"]
_COPY_ROOT_DIRS: list[str] = []
_COPY_FILES: list = []
_CORE_SUBDIR = ".core"
_COPY_IGNORE = shutil.ignore_patterns(
    "__pycache__", "*.pyc", ".git", ".venv", "tests", ".pytest_cache", ".coverage", "coverage.json",
)

def _ensure_cypilot_local(
    cypilot_root: Path, project_root: Path, dry_run: bool,
) -> Tuple[Path, dict]:
    """Ensure cypilot files are available inside *project_root*.

    If *cypilot_root* is already inside *project_root*, nothing happens.
    Otherwise the relevant subset is copied into ``project_root/cypilot/``.

    Returns ``(effective_cypilot_root, copy_report)``.
    """
    # 1. Already inside project
    try:
        cypilot_root.resolve().relative_to(project_root.resolve())
        return cypilot_root, {"action": "none"}
    except ValueError:
        pass

    # Read actual cypilot directory name from AGENTS.md (e.g. .cypilot, cpt, cypilot)
    configured_name = _read_cypilot_var(project_root)
    local_dot = project_root / (configured_name if configured_name else "cypilot")

    # 2. Existing submodule
    if (local_dot / ".git").exists():
        return local_dot, {"action": "none", "reason": "existing_submodule"}

    # 3. Existing installation (.core/ layout or legacy flat layout)
    if _is_cypilot_root(local_dot):
        return local_dot, {"action": "none", "reason": "existing_installation"}

    # 4. Copy (dry-run keeps original root so template rendering still works)
    if dry_run:
        return cypilot_root, {"action": "would_copy"}

    try:
        file_count = 0
        local_dot.mkdir(parents=True, exist_ok=True)

        core_dst = local_dot / _CORE_SUBDIR
        core_dst.mkdir(parents=True, exist_ok=True)
        gen_dst = local_dot / ".gen"
        gen_dst.mkdir(parents=True, exist_ok=True)

        for dirname in _COPY_DIRS:
            src = cypilot_root / dirname
            if src.is_dir():
                dst = core_dst / dirname
                shutil.copytree(src, dst, ignore=_COPY_IGNORE, dirs_exist_ok=True)
                file_count += sum(1 for _ in dst.rglob("*") if _.is_file())

        for dirname in _COPY_ROOT_DIRS:
            src = cypilot_root / dirname
            if src.is_dir():
                dst = local_dot / dirname
                shutil.copytree(src, dst, ignore=_COPY_IGNORE, dirs_exist_ok=True)
                file_count += sum(1 for _ in dst.rglob("*") if _.is_file())

        for fname in _COPY_FILES:
            src = cypilot_root / fname
            if src.is_file():
                shutil.copy2(src, core_dst / fname)
                file_count += 1

        return local_dot, {"action": "copied", "file_count": file_count}
    except Exception as exc:
        return cypilot_root, {"action": "error", "message": str(exc)}
# @cpt-end:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-ensure-local-copy

def _load_json_file(path: Path) -> Optional[dict]:
    if not path.is_file():
        return None
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, OSError, IOError):
        return None

def _write_or_skip(
    out_path: Path,
    content: str,
    result: Dict[str, Any],
    project_root: Path,
    dry_run: bool,
) -> None:
    """Write *content* to *out_path*, tracking create/update/unchanged in *result*.

    *result* must have ``created``, ``updated``, and ``outputs`` lists.
    """
    # Path traversal prevention (S2083): canonicalize via resolve(), verify the
    # canonical path is inside project_root, then use ONLY the canonical path
    # for all filesystem operations — the tainted input is never written directly.
    root_resolved = project_root.resolve()
    canonical = out_path.resolve()
    try:
        canonical.relative_to(root_resolved)
    except ValueError:
        raise ValueError(
            f"Output path '{out_path}' escapes project root '{project_root}' — "
            "path traversal is not allowed"
        )
    rel = _safe_relpath(canonical, project_root)
    if not canonical.exists():
        result["created"].append(canonical.as_posix())
        if not dry_run:
            canonical.parent.mkdir(parents=True, exist_ok=True)
            canonical.write_text(content, encoding="utf-8")  # NOSONAR
        result["outputs"].append({"path": rel, "action": "created"})
    else:
        try:
            old = canonical.read_text(encoding="utf-8")
        except Exception:
            old = ""
        if old != content:
            result["updated"].append(canonical.as_posix())
            if not dry_run:
                canonical.write_text(content, encoding="utf-8")  # NOSONAR
            result["outputs"].append({"path": rel, "action": "updated"})
        else:
            result["outputs"].append({"path": rel, "action": "unchanged"})

def _discover_kit_agents(
    cypilot_root: Path,
    project_root: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Discover agent definitions from core skill area and installed kits.

    Scans kits first (higher precedence), then core skill area (fallback).
    First definition seen for each name wins.

    Each ``[agents.<name>]`` section declares semantic capabilities (mode,
    isolation, model) that the per-tool template mapper translates to
    tool-specific frontmatter.

    Returns a list of dicts, each with keys:
    ``name``, ``description``, ``prompt_file_abs``, ``mode``, ``isolation``,
    ``model``, ``source_dir``.
    """
    _VALID_MODES = {"readwrite", "readonly"}
    # _VALID_MODELS: "inherit" and "fast" are documented values; any other
    # string is accepted as a passthrough model name (warning, not error).
    _KNOWN_MODELS = {"inherit", "fast"}

    seen_names: Set[str] = set()
    out: List[Dict[str, Any]] = []

    def _load_agents_toml(toml_path: Path, source_dir: Path) -> None:
        if not toml_path.is_file():
            return
        try:
            with open(toml_path, "rb") as f:
                data = tomllib.load(f)
        except Exception as exc:
            sys.stderr.write(f"WARNING: failed to parse {toml_path}: {exc}\n")
            return
        agents_section = data.get("agents")
        if not isinstance(agents_section, dict):
            return
        for name, info in agents_section.items():
            if not isinstance(info, dict):
                continue
            if name in seen_names:
                continue
            # Reject names containing path separators to prevent path traversal
            if "/" in name or "\\" in name or ".." in name:
                sys.stderr.write(f"WARNING: skipping agent with unsafe name: {name!r}\n")
                continue
            prompt_rel = info.get("prompt_file", "")
            if not isinstance(prompt_rel, str):
                sys.stderr.write(
                    f"WARNING: agent {name!r} has non-string prompt_file, skipping\n"
                )
                continue
            if not prompt_rel:
                sys.stderr.write(
                    f"WARNING: agent {name!r} missing prompt_file, skipping\n"
                )
                continue
            prompt_abs = None
            candidate = (source_dir / prompt_rel).resolve()
            # Ensure resolved path stays within source_dir (prevent path traversal)
            try:
                candidate.relative_to(source_dir.resolve())
            except ValueError:
                sys.stderr.write(
                    f"WARNING: agent {name!r} prompt_file escapes source dir, skipping\n"
                )
                continue
            if not candidate.is_file():
                sys.stderr.write(
                    f"WARNING: agent {name!r} prompt_file not found: {prompt_rel}, skipping\n"
                )
                continue
            prompt_abs = candidate
            mode = info.get("mode", "readwrite")
            model = info.get("model", "inherit")
            if mode not in _VALID_MODES:
                sys.stderr.write(
                    f"WARNING: agent {name!r} has invalid mode {mode!r}, skipping\n"
                )
                continue
            if model not in _KNOWN_MODELS:
                sys.stderr.write(
                    f"WARNING: agent {name!r} has unknown model {model!r}, using as passthrough\n"
                )
            seen_names.add(name)
            out.append({
                "name": name,
                "description": info.get("description", f"Cypilot {name} subagent"),
                "prompt_file_abs": prompt_abs,
                "mode": mode,
                "isolation": bool(info.get("isolation", False)),
                "model": model,
                "source_dir": source_dir,
            })

    # 1. Installed kits — agents defined by kit packages
    config_kits = _resolve_config_kits(cypilot_root, project_root)
    if config_kits.is_dir():
        registered = _registered_kit_dirs(project_root)
        try:
            kit_dirs = sorted(config_kits.iterdir())
        except Exception:
            kit_dirs = []
        for kit_dir in kit_dirs:
            if not kit_dir.is_dir():
                continue
            if registered is not None and kit_dir.name not in registered:
                continue
            _load_agents_toml(kit_dir / "agents.toml", kit_dir)

    # 2. Core skill area — fallback for agents not already defined by kits
    core_skill = core_subpath(cypilot_root, "skills", "cypilot")
    _load_agents_toml(core_skill / "agents.toml", core_skill)

    return out


# ── Per-tool subagent template mapping ──────────────────────────────
#
# These functions map semantic agent capabilities (mode, isolation, model)
# to tool-specific YAML frontmatter lines.  Tool knowledge stays here;
# kit knowledge stays in agents.toml.

def _agent_template_claude(agent: Dict[str, Any]) -> List[str]:
    """Build Claude Code agent proxy template lines."""
    lines = [
        "---",
        "name: {name}",
        "description: {description}",
    ]
    if agent["mode"] == "readonly":
        lines.append("tools: Bash, Read, Glob, Grep")
        lines.append("disallowedTools: Write, Edit")
    else:
        lines.append("tools: Bash, Read, Write, Edit, Glob, Grep")
    model = agent["model"]
    lines.append(f"model: {'sonnet' if model == 'fast' else model}")
    if agent["isolation"]:
        lines.append("isolation: worktree")
    lines += ["---", "", "ALWAYS open and follow `{target_agent_path}`"]
    return lines


def _agent_template_cursor(agent: Dict[str, Any]) -> List[str]:
    """Build Cursor agent proxy template lines."""
    lines = [
        "---",
        "name: {name}",
        "description: {description}",
    ]
    if agent["mode"] == "readonly":
        lines.append("tools: grep, view, bash")
        lines.append("readonly: true")
    else:
        lines.append("tools: grep, view, edit, bash")
    model = agent["model"]
    lines.append(f"model: {model}")
    lines += ["---", "", "ALWAYS open and follow `{target_agent_path}`"]
    return lines


def _agent_template_copilot(agent: Dict[str, Any]) -> List[str]:
    """Build GitHub Copilot agent proxy template lines."""
    lines = [
        "---",
        "name: {name}",
        "description: {description}",
    ]
    if agent["mode"] == "readonly":
        lines.append('tools: ["read", "search"]')
    else:
        lines.append('tools: ["*"]')
    lines += ["---", "", "ALWAYS open and follow `{target_agent_path}`"]
    return lines


_TOOL_AGENT_CONFIG: Dict[str, Dict[str, Any]] = {
    "claude": {
        "output_dir": ".claude/agents",
        "filename_format": "{name}.md",
        "template_fn": _agent_template_claude,
    },
    "cursor": {
        "output_dir": ".cursor/agents",
        "filename_format": "{name}.md",
        "template_fn": _agent_template_cursor,
    },
    "copilot": {
        "output_dir": ".github/agents",
        "filename_format": "{name}.agent.md",
        "template_fn": _agent_template_copilot,
    },
    "openai": {
        "output_dir": ".codex/agents",
        "format": "toml",
    },
}


def _render_toml_agents(agents: List[Dict[str, Any]], target_agent_paths: Dict[str, str]) -> str:
    """Render OpenAI Codex TOML agent configuration.

    Generated TOML uses ``ALWAYS open and follow`` pointers to shared agent
    definition files, consistent with the proxy pattern used for markdown tools.

    *agents* is a list of semantic agent dicts from ``_discover_kit_agents()``.
    """
    lines: List[str] = ["# Cypilot subagent definitions for OpenAI Codex", ""]
    for agent in agents:
        name = agent["name"]
        desc = " ".join(agent.get("description", "").split())
        agent_path = target_agent_paths.get(name, "")
        prompt = f"ALWAYS open and follow `{agent_path}`"
        desc_escaped = desc.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'[agents.{name.replace("-", "_")}]')
        lines.append(f'description = "{desc_escaped}"')
        lines.append('developer_instructions = """')
        lines.append(prompt)
        lines.append('"""')
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# @cpt-begin:cpt-cypilot-algo-agent-integration-discover-agents:p1:inst-define-registry
def _default_agents_config() -> dict:
    """Unified config for both workflows and skills registration per agent."""
    return {
        "version": 1,
        "agents": {
            "windsurf": {
                "workflows": {
                    "workflow_dir": ".windsurf/workflows",
                    "workflow_command_prefix": "cypilot-",
                    "workflow_filename_format": "{command}.md",
                    "custom_content": "",
                    "template": [
                        "# /{command}",
                        "",
                        "{custom_content}",
                        "ALWAYS open and follow `{target_workflow_path}`",
                    ],
                },
                "skills": {
                    "skill_name": "cypilot",
                    "custom_content": "",
                    "outputs": [
                        {
                            "path": ".windsurf/skills/cypilot/SKILL.md",
                            "template": [
                                "---",
                                "name: {name}",
                                "description: {description}",
                                "---",
                                "",
                                "{custom_content}",
                                "ALWAYS open and follow `{target_skill_path}`",
                            ],
                        },
                        {
                            "path": ".windsurf/workflows/cypilot.md",
                            "template": [
                                "# /cypilot",
                                "",
                                "{custom_content}",
                                "ALWAYS open and follow `{target_skill_path}`",
                            ],
                        },
                    ],
                },
            },
            "cursor": {
                "workflows": {
                    "workflow_dir": ".cursor/commands",
                    "workflow_command_prefix": "cypilot-",
                    "workflow_filename_format": "{command}.md",
                    "custom_content": "",
                    "template": [
                        "# /{command}",
                        "",
                        "{custom_content}",
                        "ALWAYS open and follow `{target_workflow_path}`",
                    ],
                },
                "skills": {
                    "custom_content": "",
                    "outputs": [
                        {
                            "path": ".cursor/rules/cypilot.mdc",
                            "template": [
                                "---",
                                "description: {description}",
                                "alwaysApply: true",
                                "---",
                                "",
                                "{custom_content}",
                                "ALWAYS open and follow `{target_skill_path}`",
                            ],
                        },
                        {
                            "path": ".cursor/commands/cypilot.md",
                            "template": [
                                "# /cypilot",
                                "",
                                "{custom_content}",
                                "ALWAYS open and follow `{target_skill_path}`",
                            ],
                        },
                    ],
                },
            },
            "claude": {
                "skills": {
                    "custom_content": "",
                    "outputs": [
                        {
                            "path": ".claude/skills/cypilot/SKILL.md",
                            "template": [
                                "---",
                                "name: cypilot",
                                "description: {description}",
                                "disable-model-invocation: false",
                                "user-invocable: true",
                                "allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task, WebFetch",
                                "---",
                                "",
                                "{custom_content}",
                                "ALWAYS open and follow `{target_skill_path}`",
                            ],
                        },
                        {
                            "path": ".claude/skills/cypilot-generate/SKILL.md",
                            "target": "workflows/generate.md",
                            "template": [
                                "---",
                                "name: cypilot-generate",
                                "description: {description}",
                                "disable-model-invocation: false",
                                "user-invocable: true",
                                "allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task",
                                "---",
                                "",
                                "ALWAYS open and follow `{target_path}`",
                            ],
                        },
                        {
                            "path": ".claude/skills/cypilot-analyze/SKILL.md",
                            "target": "workflows/analyze.md",
                            "template": [
                                "---",
                                "name: cypilot-analyze",
                                "description: {description}",
                                "disable-model-invocation: false",
                                "user-invocable: true",
                                "allowed-tools: Bash, Read, Glob, Grep",
                                "---",
                                "",
                                "ALWAYS open and follow `{target_path}`",
                            ],
                        },
                        {
                            "path": ".claude/skills/cypilot-plan/SKILL.md",
                            "target": "workflows/plan.md",
                            "template": [
                                "---",
                                "name: cypilot-plan",
                                "description: {description}",
                                "disable-model-invocation: false",
                                "user-invocable: true",
                                "allowed-tools: Bash, Read, Write, Edit, Glob, Grep",
                                "---",
                                "",
                                "ALWAYS open and follow `{target_path}`",
                            ],
                        },
                        {
                            "path": ".claude/skills/cypilot-workspace/SKILL.md",
                            "target": "workflows/workspace.md",
                            "template": [
                                "---",
                                "name: cypilot-workspace",
                                "description: {description}",
                                "disable-model-invocation: false",
                                "user-invocable: true",
                                "allowed-tools: Bash, Read, Write, Edit, Glob, Grep",
                                "---",
                                "",
                                "ALWAYS open and follow `{target_path}`",
                            ],
                        },
                    ],
                },
            },
            "copilot": {
                "workflows": {
                    "workflow_dir": ".github/prompts",
                    "workflow_command_prefix": "cypilot-",
                    "workflow_filename_format": "{command}.prompt.md",
                    "custom_content": "",
                    "template": [
                        "---",
                        "name: {name}",
                        "description: {description}",
                        "---",
                        "",
                        "{custom_content}",
                        "ALWAYS open and follow `{target_workflow_path}`",
                    ],
                },
                "skills": {
                    "custom_content": "",
                    "outputs": [
                        {
                            "path": ".github/copilot-instructions.md",
                            "template": [
                                "# Cypilot",
                                "",
                                "{custom_content}",
                                "ALWAYS open and follow `{target_skill_path}`",
                            ],
                        },
                        {
                            "path": ".github/prompts/cypilot.prompt.md",
                            "template": [
                                "---",
                                "name: {name}",
                                "description: {description}",
                                "---",
                                "",
                                "{custom_content}",
                                "ALWAYS open and follow `{target_skill_path}`",
                            ],
                        },
                    ],
                },
            },
            "openai": {
                "skills": {
                    "custom_content": "",
                    "outputs": [
                        {
                            "path": ".agents/skills/cypilot/SKILL.md",
                            "template": [
                                "---",
                                "name: {name}",
                                "description: {description}",
                                "---",
                                "",
                                "{custom_content}",
                                "ALWAYS open and follow `{target_skill_path}`",
                            ],
                        }
                    ],
                },
            },
        },
    }
# @cpt-end:cpt-cypilot-algo-agent-integration-discover-agents:p1:inst-define-registry

# @cpt-begin:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-parse-frontmatter
def _parse_frontmatter(file_path: Path) -> Dict[str, str]:
    """Parse YAML frontmatter from markdown file. Returns dict with name, description, etc."""
    result: Dict[str, str] = {}
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return result

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return result

    end_idx = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx < 0:
        return result

    for line in lines[1:end_idx]:
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if key and value:
                result[key] = _strip_wrapping_yaml_quotes(value)

    return result

def _strip_wrapping_yaml_quotes(value: str) -> str:
    v = str(value).strip()
    if len(v) >= 2 and ((v[0] == v[-1] == '"') or (v[0] == v[-1] == "'")):
        inner = v[1:-1]
        if v[0] == '"':
            inner = inner.replace('\\"', '"')
            inner = inner.replace("\\\\", "\\")
            inner = inner.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")
        return inner
    return v

def _yaml_double_quote(value: str) -> str:
    v = str(value)
    v = v.replace("\\", "\\\\")
    v = v.replace('"', "\\\"")
    v = v.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")
    return f'"{v}"'

def _ensure_frontmatter_description_quoted(content: str) -> str:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return content

    end_idx = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx < 0:
        return content

    for i in range(1, end_idx):
        raw = lines[i]
        if not raw.lstrip().startswith("description:"):
            continue

        indent_len = len(raw) - len(raw.lstrip())
        indent = raw[:indent_len]

        _, _, rest = raw.lstrip().partition(":")
        rest = rest.strip()

        comment = ""
        if " #" in rest:
            val_part, _, comment_part = rest.partition(" #")
            rest = val_part.strip()
            comment = " #" + comment_part

        rest = _strip_wrapping_yaml_quotes(rest)
        lines[i] = f"{indent}description: {_yaml_double_quote(rest)}{comment}".rstrip()

    return "\n".join(lines).rstrip() + "\n"

def _render_template(lines: List[str], variables: Dict[str, str]) -> str:
    out: List[str] = []
    for line in lines:
        try:
            out.append(line.format(**variables))
        except KeyError as e:
            raise SystemExit(f"Missing template variable: {e}")
    rendered = "\n".join(out).rstrip() + "\n"
    return _ensure_frontmatter_description_quoted(rendered)


def _expected_claude_legacy_targets(
    skill_name: str,
    project_root: Path,
    cypilot_root: Path,
) -> Set[str]:
    if not isinstance(skill_name, str) or not skill_name.startswith("cypilot-"):
        return set()
    workflow_name = skill_name[len("cypilot-"):]
    workflow_path = core_subpath(cypilot_root, "workflows", f"{workflow_name}.md").resolve()
    return {
        f"{{cypilot_path}}/.core/workflows/{workflow_name}.md",
        _target_path_from_root(workflow_path, project_root, cypilot_root),
        workflow_path.as_posix(),
    }


def _normalize_agent_target_path(
    target_path: str,
    current_file: Path,
    project_root: Path,
    cypilot_root: Path,
) -> str:
    if target_path.startswith("{cypilot_path}/") or target_path.startswith("@/"):
        return target_path
    if target_path.startswith("/"):
        return Path(target_path).as_posix()
    return _target_path_from_root((current_file.parent / target_path).resolve(), project_root, cypilot_root)


def _looks_like_generated_claude_legacy_command(
    content: str,
    *,
    expected_targets: Set[str],
    current_file: Path,
    project_root: Path,
    cypilot_root: Path,
) -> bool:
    stripped = content.strip()
    if not stripped:
        return False
    if not re.fullmatch(
        r"# /[^\n]+(?:\n[ \t]*){1,3}ALWAYS open and follow `[^`]+`",
        stripped,
    ):
        return False
    match = re.search(r"ALWAYS open and follow `([^`]+)`", stripped)
    if not match:
        return False
    target_path = match.group(1)
    normalized_target = _normalize_agent_target_path(
        target_path, current_file, project_root, cypilot_root,
    )
    return normalized_target in expected_targets
# @cpt-end:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-parse-frontmatter

# @cpt-begin:cpt-cypilot-algo-agent-integration-discover-agents:p1:inst-resolve-kits
def _resolve_config_kits(cypilot_root: Path, project_root: Optional[Path] = None) -> Path:
    """Resolve config/kits/ directory, with fallback to adapter dir for source repos.

    In self-hosted / source-repo mode, cypilot_root == project_root and
    config/ lives inside the adapter directory (e.g. .bootstrap/config/).
    """
    config_kits = config_subpath(cypilot_root, "kits")
    if config_kits.is_dir():
        return config_kits
    if project_root is not None:
        adapter_name = _read_cypilot_var(project_root)
        if adapter_name:
            adapter_config_kits = project_root / adapter_name / "config" / "kits"
            if adapter_config_kits.is_dir():
                return adapter_config_kits
    return config_kits

def _registered_kit_dirs(project_root: Optional[Path]) -> Optional[Set[str]]:
    """Return set of kit directory names registered in core.toml, or None if config unavailable."""
    if project_root is None:
        return None
    cfg = load_project_config(project_root)
    if cfg is None:
        return None
    kits = cfg.get("kits")
    if not isinstance(kits, dict):
        return None
    dirs: Set[str] = set()
    for kit_cfg in kits.values():
        if isinstance(kit_cfg, dict):
            path = kit_cfg.get("path", "")
            if path:
                dirs.add(Path(path).name)
    return dirs if dirs else None
# @cpt-end:cpt-cypilot-algo-agent-integration-discover-agents:p1:inst-resolve-kits

# @cpt-begin:cpt-cypilot-algo-agent-integration-list-workflows:p1:inst-scan-core-workflows
def _list_workflow_files(cypilot_root: Path, project_root: Optional[Path] = None) -> List[Tuple[str, Path]]:
    """List workflow files from .core/workflows/ and config/kits/*/workflows/.

    Returns list of (filename, full_path) tuples.  Kit workflows
    are discovered alongside core workflows so the agent proxy
    generator can route to them.
    """
    seen_names: set = set()
    out: List[Tuple[str, Path]] = []

    def _scan_dir(d: Path) -> None:
        if not d.is_dir():
            return
        try:
            for p in d.iterdir():
                if not p.is_file() or p.suffix.lower() != ".md":
                    continue
                if p.name in {"AGENTS.md", "README.md"}:
                    continue
                try:
                    head = "\n".join(p.read_text(encoding="utf-8").splitlines()[:30])
                except Exception:
                    continue
                if "type: workflow" not in head:
                    continue
                if p.name not in seen_names:
                    seen_names.add(p.name)
                    out.append((p.name, p.resolve()))
        except Exception:
            pass

    # 1. Core workflows
    _scan_dir(core_subpath(cypilot_root, "workflows"))

    # 2. Kit workflows (config/kits/*/workflows/)
    registered = _registered_kit_dirs(project_root)
    config_kits = _resolve_config_kits(cypilot_root, project_root)
    if config_kits.is_dir():
        try:
            for kit_dir in sorted(config_kits.iterdir()):
                if registered is not None and kit_dir.name not in registered:
                    continue
                _scan_dir(kit_dir / "workflows")
        except Exception:
            pass

    out.sort(key=lambda t: t[0])
    return out
# @cpt-end:cpt-cypilot-algo-agent-integration-list-workflows:p1:inst-scan-core-workflows

_ALL_RECOGNIZED_AGENTS = ["windsurf", "cursor", "claude", "copilot", "openai"]

# @cpt-begin:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-create-proxy
def _process_single_agent(
    agent: str,
    project_root: Path,
    cypilot_root: Path,
    cfg: dict,
    cfg_path: Optional[Path],
    dry_run: bool,
) -> Dict[str, Any]:
    """Process a single agent and return its result dict."""
    recognized = agent in set(_ALL_RECOGNIZED_AGENTS)

    agents_cfg = cfg.get("agents") if isinstance(cfg, dict) else None
    if isinstance(cfg, dict) and isinstance(agents_cfg, dict) and agent not in agents_cfg:
        if recognized:
            defaults = _default_agents_config()
            default_agents = defaults.get("agents") if isinstance(defaults, dict) else None
            if isinstance(default_agents, dict) and isinstance(default_agents.get(agent), dict):
                agents_cfg[agent] = default_agents[agent]
        else:
            agents_cfg[agent] = {"workflows": {}, "skills": {}}
        cfg["agents"] = agents_cfg

    if not isinstance(agents_cfg, dict) or agent not in agents_cfg or not isinstance(agents_cfg.get(agent), dict):
        return {
            "status": "CONFIG_ERROR",
            "message": "Agent config missing or invalid",
            "config_path": cfg_path.as_posix() if cfg_path else None,
            "agent": agent,
        }

    agent_cfg: dict = agents_cfg[agent]
    workflows_cfg = agent_cfg.get("workflows", {})
    skills_cfg = agent_cfg.get("skills", {})

    skill_output_paths: Set[str] = set()
    if isinstance(skills_cfg, dict):
        outputs = skills_cfg.get("outputs")
        if isinstance(outputs, list):
            for out_cfg in outputs:
                if not isinstance(out_cfg, dict):
                    continue
                rel_path = out_cfg.get("path")
                if isinstance(rel_path, str) and rel_path.strip():
                    skill_output_paths.add((project_root / rel_path).resolve().as_posix())

    workflows_result: Dict[str, Any] = {"created": [], "updated": [], "unchanged": [], "renamed": [], "deleted": [], "errors": []}

    if isinstance(workflows_cfg, dict) and workflows_cfg:
        workflow_dir_rel = workflows_cfg.get("workflow_dir")
        filename_fmt = workflows_cfg.get("workflow_filename_format", "{command}.md")
        prefix = workflows_cfg.get("workflow_command_prefix", "cypilot-")
        template = workflows_cfg.get("template")

        if not isinstance(workflow_dir_rel, str) or not workflow_dir_rel.strip():
            workflows_result["errors"].append("Missing workflow_dir in workflows config")
        elif not isinstance(template, list) or not all(isinstance(x, str) for x in template):
            workflows_result["errors"].append("Missing or invalid template in workflows config")
        else:
            workflow_dir = (project_root / workflow_dir_rel).resolve()
            cypilot_workflow_entries = _list_workflow_files(cypilot_root, project_root)

            desired: Dict[str, Dict[str, str]] = {}
            for wf_filename, wf_full_path in cypilot_workflow_entries:
                wf_name = Path(wf_filename).stem
                command = "cypilot" if wf_name == "cypilot" else f"{prefix}{wf_name}"
                filename = filename_fmt.format(command=command, workflow_name=wf_name)
                desired_path = (workflow_dir / filename).resolve()
                target_workflow_path = wf_full_path

                if desired_path.as_posix() in skill_output_paths:
                    continue

                target_rel = _target_path_from_root(target_workflow_path, project_root, cypilot_root)

                fm = _parse_frontmatter(target_workflow_path)
                source_name = fm.get("name", command)
                source_description = fm.get("description", f"Proxy to Cypilot workflow {wf_name}")

                custom_content = workflows_cfg.get("custom_content", "")

                content = _render_template(
                    template,
                    {
                        "command": command,
                        "workflow_name": wf_name,
                        "target_workflow_path": target_rel,
                        "name": source_name,
                        "description": source_description,
                        "custom_content": custom_content,
                    },
                )
                desired[desired_path.as_posix()] = {
                    "command": command,
                    "workflow_name": wf_name,
                    "target_workflow_path": target_rel,
                    "content": content,
                }

            existing_files: List[Path] = []
            if workflow_dir.is_dir():
                existing_files = list(workflow_dir.glob("*.md"))

            desired_by_target: Dict[str, str] = {meta["target_workflow_path"]: p for p, meta in desired.items()}
            for pth in existing_files:
                if pth.as_posix() in desired:
                    continue
                if not pth.name.startswith(prefix):
                    try:
                        head = "\n".join(pth.read_text(encoding="utf-8").splitlines()[:5])
                    except Exception:
                        continue
                    if not head.lstrip().startswith("# /"):
                        continue
                try:
                    txt = pth.read_text(encoding="utf-8")
                except Exception:
                    continue
                if "ALWAYS open and follow `" not in txt:
                    continue
                m = re.search(r"ALWAYS open and follow `([^`]+)`", txt)
                if not m:
                    continue
                target_rel = m.group(1)
                # Normalize legacy relative/absolute paths to {cypilot_path}/... canonical form
                if not target_rel.startswith("@/") and not target_rel.startswith("{cypilot_path}/"):
                    if target_rel.startswith("/"):
                        resolved = Path(target_rel)
                    else:
                        resolved = (pth.parent / target_rel).resolve()
                    target_rel = _target_path_from_root(resolved, project_root, cypilot_root)
                dst = desired_by_target.get(target_rel)
                if not dst or pth.as_posix() == dst:
                    continue
                if Path(dst).exists():
                    continue
                if not dry_run:
                    workflow_dir.mkdir(parents=True, exist_ok=True)
                    Path(dst).parent.mkdir(parents=True, exist_ok=True)
                    pth.replace(Path(dst))
                workflows_result["renamed"].append((pth.as_posix(), dst))

            existing_files = list(workflow_dir.glob("*.md")) if workflow_dir.is_dir() else []

            for p_str, meta in desired.items():
                pth = Path(p_str)
                if not pth.exists():
                    workflows_result["created"].append(p_str)
                    if not dry_run:
                        pth.parent.mkdir(parents=True, exist_ok=True)
                        pth.write_text(meta["content"], encoding="utf-8")
                    continue
                try:
                    old = pth.read_text(encoding="utf-8")
                except Exception:
                    old = ""
                if old != meta["content"]:
                    workflows_result["updated"].append(p_str)
                    if not dry_run:
                        pth.write_text(meta["content"], encoding="utf-8")
                else:
                    workflows_result["unchanged"].append(p_str)

            desired_paths = set(desired.keys())
            for pth in existing_files:
                p_str = pth.as_posix()
                if p_str in desired_paths:
                    continue
                if not pth.name.startswith(prefix) and not pth.name.startswith("cypilot-"):
                    continue
                try:
                    txt = pth.read_text(encoding="utf-8")
                except Exception:
                    continue
                m = re.search(r"ALWAYS open and follow `([^`]+)`", txt)
                if not m:
                    continue
                target_rel = m.group(1)
                if "workflows/" not in target_rel and "/workflows/" not in target_rel:
                    continue
                if target_rel.startswith("{cypilot_path}/"):
                    expected = (cypilot_root / target_rel[len("{cypilot_path}/"):]).resolve()
                elif target_rel.startswith("@/"):
                    expected = (project_root / target_rel[2:]).resolve()
                elif not target_rel.startswith("/"):
                    expected = (pth.parent / target_rel).resolve()
                else:
                    expected = Path(target_rel)
                # Accept targets in .core/workflows/ or config/kits/*/workflows/
                try:
                    expected.relative_to(core_subpath(cypilot_root, "workflows"))
                except ValueError:
                    try:
                        expected.relative_to(_resolve_config_kits(cypilot_root, project_root))
                    except ValueError:
                        continue
                if expected.exists():
                    continue
                workflows_result["deleted"].append(p_str)
                if not dry_run:
                    try:
                        pth.unlink()
                    except (PermissionError, FileNotFoundError, OSError):
                        pass

    skills_result: Dict[str, Any] = {"created": [], "updated": [], "deleted": [], "skipped": [], "outputs": [], "errors": []}

    if isinstance(skills_cfg, dict) and skills_cfg:
        outputs = skills_cfg.get("outputs")
        skill_name = skills_cfg.get("skill_name", "cypilot")

        if outputs is not None:
            if not isinstance(outputs, list) or not all(isinstance(x, dict) for x in outputs):
                skills_result["errors"].append("outputs must be an array of objects")
            else:
                target_skill_abs = core_subpath(cypilot_root, "skills", "cypilot", "SKILL.md").resolve()
                if not target_skill_abs.is_file():
                    skills_result["errors"].append(
                        "Cypilot skill source not found (expected: " + target_skill_abs.as_posix() + "). "
                        "Run /cypilot to reinitialize."
                    )

                skill_fm = _parse_frontmatter(target_skill_abs)
                skill_source_name = skill_fm.get("name", skill_name)
                skill_source_description = skill_fm.get("description", "Proxy to Cypilot core skill instructions")

                # Enrich description with per-kit skill descriptions from config/kits/*/SKILL.md
                registered = _registered_kit_dirs(project_root)
                config_kits = _resolve_config_kits(cypilot_root, project_root)
                if config_kits.is_dir():
                    kit_descs: List[str] = []
                    try:
                        for kit_dir in sorted(config_kits.iterdir()):
                            if registered is not None and kit_dir.name not in registered:
                                continue
                            kit_skill = kit_dir / "SKILL.md"
                            if kit_skill.is_file():
                                kit_fm = _parse_frontmatter(kit_skill)
                                kit_desc = kit_fm.get("description", "")
                                if kit_desc:
                                    kit_descs.append(f"Kit {kit_dir.name}: {kit_desc}")
                    except Exception:
                        pass
                    if kit_descs:
                        skill_source_description = skill_source_description.rstrip(".") + ". " + ". ".join(kit_descs) + "."

                custom_content = skills_cfg.get("custom_content", "")

                for idx, out_cfg in enumerate(outputs):
                    rel_path = out_cfg.get("path")
                    template = out_cfg.get("template")
                    if not isinstance(rel_path, str) or not rel_path.strip():
                        skills_result["errors"].append(f"outputs[{idx}] missing path")
                        continue
                    if not isinstance(template, list) or not all(isinstance(x, str) for x in template):
                        skills_result["errors"].append(f"outputs[{idx}] missing or invalid template")
                        continue

                    out_path = (project_root / rel_path).resolve()

                    custom_target = out_cfg.get("target")
                    if custom_target:
                        target_abs = core_subpath(cypilot_root, *Path(custom_target).parts).resolve()
                        target_rel = _target_path_from_root(target_abs, project_root, cypilot_root)
                        target_fm = _parse_frontmatter(target_abs)
                        out_name = target_fm.get("name", skill_source_name)
                        out_description = target_fm.get("description", skill_source_description)
                    else:
                        target_rel = _target_path_from_root(target_skill_abs, project_root, cypilot_root)
                        out_name = skill_source_name
                        out_description = skill_source_description

                    content = _render_template(
                        template,
                        {
                            "agent": agent,
                            "skill_name": str(skill_name),
                            "target_skill_path": target_rel,
                            "target_path": target_rel,
                            "name": out_name,
                            "description": out_description,
                            "custom_content": custom_content,
                        },
                    )

                    _write_or_skip(out_path, content, skills_result, project_root, dry_run)

    # ── Clean up legacy .claude/commands/ files that are now replaced by skills ──
    if agent == "claude" and isinstance(skills_cfg, dict):
        outputs = skills_cfg.get("outputs")
        if isinstance(outputs, list):
            skill_names: Set[str] = set()
            for out_cfg in outputs:
                if not isinstance(out_cfg, dict):
                    continue
                rel_path = out_cfg.get("path", "")
                if not isinstance(rel_path, str):
                    continue
                parts = Path(rel_path).parts
                if len(parts) >= 3 and parts[0] == ".claude" and parts[1] == "skills":
                    skill_names.add(parts[2])

            legacy_commands_dir = project_root / ".claude" / "commands"
            if legacy_commands_dir.is_dir() and skill_names:
                for legacy_skill in skill_names:
                    legacy_file = legacy_commands_dir / f"{legacy_skill}.md"
                    if not legacy_file.is_file():
                        continue
                    rel_path = legacy_file.relative_to(project_root).as_posix()
                    try:
                        legacy_content = legacy_file.read_text(encoding="utf-8")
                    except OSError:
                        skills_result["errors"].append(f"failed to inspect {rel_path}")
                        continue
                    expected_targets = _expected_claude_legacy_targets(
                        legacy_skill, project_root, cypilot_root,
                    )
                    if not expected_targets:
                        skills_result["skipped"].append(f"{rel_path} (missing generated marker)")
                        continue
                    if not _looks_like_generated_claude_legacy_command(
                        legacy_content,
                        expected_targets=expected_targets,
                        current_file=legacy_file,
                        project_root=project_root,
                        cypilot_root=cypilot_root,
                    ):
                        skills_result["skipped"].append(f"{rel_path} (missing generated marker)")
                        continue
                    if not dry_run:
                        try:
                            legacy_file.unlink()
                            skills_result["deleted"].append(rel_path)
                        except OSError:
                            skills_result["errors"].append(f"failed to delete {rel_path}")
                    else:
                        skills_result["deleted"].append(rel_path)

    # ── Subagent generation ────────────────────────────────────────────
    subagents_result: Dict[str, Any] = {"created": [], "updated": [], "skipped": False, "outputs": [], "errors": []}

    tool_cfg = _TOOL_AGENT_CONFIG.get(agent)
    kit_agents = _discover_kit_agents(cypilot_root, project_root)

    if tool_cfg is None or not kit_agents:
        subagents_result["skipped"] = True
        if tool_cfg is None:
            subagents_result["skip_reason"] = f"{agent} does not support subagents"
        else:
            subagents_result["skip_reason"] = "no agents discovered"
    else:
        output_dir_rel = tool_cfg["output_dir"]
        output_format = tool_cfg.get("format", "markdown")
        filename_fmt = tool_cfg.get("filename_format", "{name}.md")
        output_dir = (project_root / output_dir_rel).resolve()

        # Build target_agent_paths from discovered kit agents
        target_agent_paths: Dict[str, str] = {}
        for ka in kit_agents:
            if ka.get("prompt_file_abs"):
                target_agent_paths[ka["name"]] = _target_path_from_root(
                    ka["prompt_file_abs"], project_root, cypilot_root,
                )

        if output_format == "toml":
            # Render all agents into a single TOML file
            toml_path = (output_dir / "cypilot-agents.toml").resolve()
            content = _render_toml_agents(kit_agents, target_agent_paths)
            _write_or_skip(toml_path, content, subagents_result, project_root, dry_run)
        else:
            # Markdown + YAML frontmatter (claude, cursor, copilot)
            template_fn = tool_cfg.get("template_fn")
            if template_fn is None:
                subagents_result["errors"].append(f"No template function for {agent}")
            else:
                for ka in kit_agents:
                    name = ka["name"]
                    template = template_fn(ka)
                    target_agent_rel = target_agent_paths.get(name, "")
                    if not target_agent_rel:
                        subagents_result["errors"].append(
                            f"agent {name!r} has no resolved prompt target, skipped"
                        )
                        continue

                    content = _render_template(
                        template,
                        {
                            "name": name,
                            "description": ka["description"],
                            "target_agent_path": target_agent_rel,
                        },
                    )

                    filename = filename_fmt.format(name=name)
                    out_path = (output_dir / filename).resolve()

                    # Ensure output stays within output_dir (prevent path traversal)
                    try:
                        out_path.relative_to(output_dir)
                    except ValueError:
                        subagents_result["errors"].append(
                            f"agent {name!r} would write outside {output_dir_rel}, skipped"
                        )
                        continue

                    _write_or_skip(out_path, content, subagents_result, project_root, dry_run)

    all_errors = workflows_result.get("errors", []) + skills_result.get("errors", []) + subagents_result.get("errors", [])
    agent_status = "PASS" if not all_errors else "PARTIAL"

    return {
        "status": agent_status,
        "agent": agent,
        "workflows": {
            "created": workflows_result["created"],
            "updated": workflows_result["updated"],
            "unchanged": workflows_result["unchanged"],
            "renamed": workflows_result["renamed"],
            "deleted": workflows_result["deleted"],
            "counts": {
                "created": len(workflows_result["created"]),
                "updated": len(workflows_result["updated"]),
                "unchanged": len(workflows_result["unchanged"]),
                "renamed": len(workflows_result["renamed"]),
                "deleted": len(workflows_result["deleted"]),
            },
        },
        "skills": {
            "created": skills_result["created"],
            "updated": skills_result["updated"],
            "deleted": skills_result["deleted"],
            "skipped": skills_result["skipped"],
            "outputs": skills_result["outputs"],
            "counts": {
                "created": len(skills_result["created"]),
                "updated": len(skills_result["updated"]),
                "deleted": len(skills_result["deleted"]),
                "skipped": len(skills_result["skipped"]),
            },
        },
        "subagents": {
            "created": subagents_result["created"],
            "updated": subagents_result["updated"],
            "skipped": subagents_result["skipped"],
            "skip_reason": subagents_result.get("skip_reason", ""),
            "outputs": subagents_result["outputs"],
            "counts": {
                "created": len(subagents_result["created"]),
                "updated": len(subagents_result["updated"]),
            },
        },
        "errors": all_errors if all_errors else None,
    }
# @cpt-end:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-create-proxy

# @cpt-begin:cpt-cypilot-algo-agent-integration-discover-agents:p1:inst-resolve-context
def _resolve_agents_context(argv: List[str], prog: str, description: str, *, allow_yes: bool = False) -> Optional[tuple]:
    """Shared argument parsing and project resolution for agents commands.

    Returns (args, agents_to_process, project_root, cypilot_root, copy_report, cfg_path, cfg)
    or None if it handled the response itself (error / early exit).
    """
    p = argparse.ArgumentParser(prog=prog, description=description)
    agent_group = p.add_mutually_exclusive_group(required=False)
    agent_group.add_argument("--agent", default=None, help="Agent/IDE key (e.g., windsurf, cursor, claude, copilot, openai). Omit to target all supported agents.")
    agent_group.add_argument("--openai", action="store_true", help="Shortcut for --agent openai (OpenAI Codex)")
    p.add_argument("--root", default=".", help="Project root directory (default: current directory)")
    p.add_argument("--cypilot-root", default=None, help="Explicit Cypilot core root (optional override)")
    p.add_argument("--config", default=None, help="Path to agents config JSON (optional; defaults are built-in)")
    p.add_argument("--dry-run", action="store_true", help="Compute changes without writing files")
    p.add_argument("--show-layers", action="store_true", help="Display layer provenance report instead of generating")
    p.add_argument("--discover", action="store_true", help="Scan conventional dirs and populate manifest.toml before generating")
    if allow_yes:
        p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
    args = p.parse_args(argv)

    # Determine agent list
    if bool(getattr(args, "openai", False)):
        agents_to_process = ["openai"]
    elif args.agent is not None:
        agent = str(args.agent).strip()
        if not agent:
            raise SystemExit("--agent must be non-empty")
        agents_to_process = [agent]
    else:
        agents_to_process = list(_ALL_RECOGNIZED_AGENTS)

    start_path = Path(args.root).resolve()
    project_root = find_project_root(start_path)
    if project_root is None:
        ui.result(
            {"status": "NOT_FOUND", "message": "No project root found (no AGENTS.md with @cpt:root-agents or .git)", "searched_from": start_path.as_posix()},
            human_fn=lambda d: (
                ui.error("No project root found."),
                ui.detail("Searched from", start_path.as_posix()),
                ui.hint("Initialize Cypilot first:  cpt init"),
                ui.blank(),
            ),
        )
        return None

    cypilot_root = Path(args.cypilot_root).resolve() if args.cypilot_root else None
    if cypilot_root is None:
        cypilot_rel = _read_cypilot_var(project_root)
        if cypilot_rel:
            candidate = (project_root / cypilot_rel).resolve()
            if _is_cypilot_root(candidate):
                cypilot_root = candidate
        if cypilot_root is None:
            resolved_file = Path(__file__).resolve()
            for _level in (5, 6, 7):
                _candidate = resolved_file.parents[_level]
                if _is_cypilot_root(_candidate):
                    cypilot_root = _candidate
                    break
            else:
                cypilot_root = resolved_file.parents[5]

    cypilot_root, copy_report = _ensure_cypilot_local(cypilot_root, project_root, args.dry_run)
    if copy_report.get("action") == "error":
        _err_msg = f"Failed to copy cypilot into project: {copy_report.get('message', 'unknown')}"
        ui.result(
            {"status": "COPY_ERROR", "message": _err_msg, "cypilot_root": cypilot_root.as_posix(), "project_root": project_root.as_posix()},
            human_fn=lambda d: (
                ui.error(_err_msg),
                ui.hint("Check permissions and disk space."),
                ui.blank(),
            ),
        )
        return None

    cfg_path: Optional[Path] = Path(args.config).resolve() if args.config else None
    cfg: Optional[dict] = _load_json_file(cfg_path) if cfg_path else None

    any_recognized = any(a in set(_ALL_RECOGNIZED_AGENTS) for a in agents_to_process)
    if cfg is None:
        if any_recognized:
            cfg = _default_agents_config()
        else:
            cfg = {"version": 1, "agents": {a: {"workflows": {}, "skills": {}} for a in agents_to_process}}

    return args, agents_to_process, project_root, cypilot_root, copy_report, cfg_path, cfg
# @cpt-end:cpt-cypilot-algo-agent-integration-discover-agents:p1:inst-resolve-context

# @cpt-begin:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-cmd-agents-list
def cmd_agents(argv: List[str]) -> int:
    """Read-only command: list generated agent integration files."""
    ctx = _resolve_agents_context(argv, prog="agents", description="Show generated agent integration files")
    if ctx is None:
        return 1
    args, agents_to_process, project_root, cypilot_root, copy_report, cfg_path, cfg = ctx

    # Scan for existing agent files (dry-run to see what exists)
    results: Dict[str, Any] = {}
    for agent in agents_to_process:
        result = _process_single_agent(agent, project_root, cypilot_root, cfg, cfg_path, dry_run=True)
        results[agent] = result

    ui.result(
        {
            "status": "OK",
            "agents": list(agents_to_process),
            "project_root": project_root.as_posix(),
            "cypilot_root": cypilot_root.as_posix(),
            "results": results,
        },
        human_fn=lambda d: _human_agents_list(d, agents_to_process, results, project_root),
    )
    return 0
# @cpt-end:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-cmd-agents-list

def cmd_generate_agents(argv: List[str]) -> int:
    """Generate/update agent-specific workflow proxies and skill outputs."""
    # @cpt-begin:cpt-cypilot-flow-agent-integration-generate:p1:inst-user-agents
    ctx = _resolve_agents_context(
        argv, prog="generate-agents",
        description="Generate/update agent-specific workflow proxies and skill outputs",
        allow_yes=True,
    )
    if ctx is None:
        return 1
    args, agents_to_process, project_root, cypilot_root, copy_report, cfg_path, cfg = ctx
    # @cpt-end:cpt-cypilot-flow-agent-integration-generate:p1:inst-user-agents

    # @cpt-begin:cpt-cypilot-flow-agent-integration-generate:p1:inst-resolve-project
    # Resolved in _resolve_agents_context: project_root via find_project_root,
    # cypilot_root via AGENTS.md cypilot_path variable or __file__ ancestry.
    # @cpt-end:cpt-cypilot-flow-agent-integration-generate:p1:inst-resolve-project
    # @cpt-begin:cpt-cypilot-flow-agent-integration-generate:p1:inst-ensure-local
    # Handled in _resolve_agents_context via _ensure_cypilot_local:
    # copies cypilot files into project when cypilot_root is external.
    # @cpt-end:cpt-cypilot-flow-agent-integration-generate:p1:inst-ensure-local

    # ── NEW: Multi-layer discovery path ────────────────────────────────────
    # @cpt-begin:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-step2-discover-layers
    layers = _discover_layers(project_root, cypilot_root)
    # @cpt-end:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-step2-discover-layers

    if _layers_have_v2_manifests(layers):
        # ── NEW PATH: Multi-layer v2.0 manifest pipeline ─────────────────
        # @cpt-begin:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-step3-5-resolve-includes

        # Step 3: Resolve includes for each layer
        # Use project_root.parent as trusted root to allow cross-repo includes
        # (e.g. ../sibling-repo/...) within the same workspace.
        workspace_root = project_root.parent.resolve()
        has_v2_errors = False
        resolved_layers = []
        for layer in layers:
            if (
                layer.state == _ManifestLayerState.LOADED
                and layer.manifest is not None
                and layer.manifest.includes
            ):
                try:
                    resolved_manifest = _resolve_includes(
                        layer.manifest, layer.path.parent, trusted_root=workspace_root
                    )
                    import dataclasses
                    resolved_layer = dataclasses.replace(layer, manifest=resolved_manifest)
                    resolved_layers.append(resolved_layer)
                except ValueError as exc:
                    sys.stderr.write(f"ERROR: failed to resolve includes for {layer.path}: {exc}\n")
                    has_v2_errors = True
                    resolved_layers.append(layer)
            else:
                resolved_layers.append(layer)
        if has_v2_errors:
            return 1
        # @cpt-end:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-step3-5-resolve-includes

        # Step 4: Handle --discover flag: scan dirs and populate manifest.toml
        # @cpt-begin:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-discover-flag
        if getattr(args, "discover", False):
            discovered = discover_components(project_root)
            manifest_out = cypilot_root / "config" / "manifest.toml"
            if not args.dry_run:
                write_discovered_manifest(discovered, manifest_out)
                sys.stderr.write(f"INFO: wrote discovered manifest to {manifest_out}\n")
            # Re-run discovery after writing
            layers = _discover_layers(project_root, cypilot_root)
            resolved_layers = []
            has_v2_errors = False
            for layer in layers:
                if (
                    layer.state == _ManifestLayerState.LOADED
                    and layer.manifest is not None
                    and layer.manifest.includes
                ):
                    try:
                        resolved_manifest = _resolve_includes(
                            layer.manifest, layer.path.parent, trusted_root=workspace_root
                        )
                        import dataclasses as _dc
                        resolved_layer = _dc.replace(layer, manifest=resolved_manifest)
                        resolved_layers.append(resolved_layer)
                    except ValueError as exc:
                        sys.stderr.write(f"ERROR: failed to resolve includes for {layer.path}: {exc}\n")
                        has_v2_errors = True
                        resolved_layers.append(layer)
                else:
                    resolved_layers.append(layer)
            if has_v2_errors:
                return 1
        # @cpt-end:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-discover-flag

        # Step 5: Merge components from all layers
        # @cpt-begin:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-step6-merge
        merged = _merge_components(resolved_layers)
        # @cpt-end:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-step6-merge

        # Step 6: Handle --show-layers flag
        # @cpt-begin:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-show-layers-flag
        if getattr(args, "show_layers", False):
            report = build_provenance_report(merged, project_root)
            from ..utils.ui import is_json_mode
            if is_json_mode():
                ui.result({"status": "OK", "provenance": report})
            else:
                human_text = format_provenance_human(report)
                sys.stdout.write(human_text + "\n")
            return 0
        # @cpt-end:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-show-layers-flag

        # Step 7: Extend variables with layer path variables
        # @cpt-begin:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-step9-layer-vars
        base_variables: Dict[str, str] = {
            "cypilot_path": cypilot_root.as_posix(),
            "project_root": project_root.as_posix(),
        }
        variables = _add_layer_variables(base_variables, resolved_layers, project_root)
        # @cpt-end:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-step9-layer-vars

        # Step 8: Generate for each target agent using manifest v2 pipeline
        # @cpt-begin:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-step7-translate

        # Preview pass — compute what would change
        preview_v2_create = 0
        preview_v2_update = 0
        for target in agents_to_process:
            pr_a = generate_manifest_agents(merged.agents, target, project_root, dry_run=True)
            pr_s = generate_manifest_skills(merged.skills, target, project_root, dry_run=True)
            preview_v2_create += len(pr_a.get("created", [])) + len(pr_s.get("created", []))
            preview_v2_update += len(pr_a.get("updated", [])) + len(pr_s.get("updated", []))

        if args.dry_run:
            # Build and show dry-run result then return
            dry_results: Dict[str, Any] = {}
            for target in agents_to_process:
                a = generate_manifest_agents(merged.agents, target, project_root, dry_run=True, variables=variables)
                s = generate_manifest_skills(merged.skills, target, project_root, dry_run=True, variables=variables)
                dry_results[target] = {"status": "PASS", "agent": target, "manifest_v2": True, "translated_agents": len(merged.agents), "skills": s, "v2_agents": a, "workflows": {"created": [], "updated": [], "unchanged": [], "renamed": [], "deleted": [], "counts": {}}}
            dr = _build_result(dry_results, agents_to_process, project_root, cypilot_root, cfg_path, copy_report, dry_run=True)
            dr["manifest_v2"] = True
            ui.result(dr, human_fn=lambda d: _human_generate_agents_ok(d, agents_to_process, dry_results, dry_run=True))
            return 0

        if preview_v2_create == 0 and preview_v2_update == 0:
            ui.info("No changes needed — agent files are up to date.")
        else:
            from ..utils.ui import is_json_mode
            if not is_json_mode():
                auto_approve = getattr(args, "yes", False)
                if not auto_approve:
                    # show count and ask
                    sys.stdout.write(f"Will create {preview_v2_create} file(s), update {preview_v2_update} file(s). Continue? [y/N] ")
                    sys.stdout.flush()
                    answer = sys.stdin.readline().strip().lower()
                    if answer not in ("y", "yes"):
                        ui.info("Aborted.")
                        return 0

        has_errors = False
        results: Dict[str, Any] = {}

        for target in agents_to_process:
            # Generate agent files from merged agents (manifest v2 pipeline)
            agents_result = generate_manifest_agents(
                merged.agents,
                target,
                project_root,
                args.dry_run,
                variables=variables,
            )

            # Generate skill files from merged skills
            skills_result = generate_manifest_skills(
                merged.skills,
                target,
                project_root,
                args.dry_run,
                variables=variables,
            )

            results[target] = {
                "status": "PASS",
                "agent": target,
                "manifest_v2": True,
                "translated_agents": len(merged.agents),
                "skills": skills_result,
                "v2_agents": agents_result,
                "workflows": {"created": [], "updated": [], "unchanged": [], "renamed": [], "deleted": [], "counts": {}},
            }
        # @cpt-end:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-step7-translate

        # Also run the legacy pipeline for workflows and skill proxies
        # (v2 manifest handles agents/skills, legacy handles workflows/skill proxies)
        for agent in agents_to_process:
            legacy_result = _process_single_agent(agent, project_root, cypilot_root, cfg, cfg_path, dry_run=args.dry_run)
            if agent in results:
                # Merge legacy workflow results into v2 result
                results[agent]["workflows"] = legacy_result.get("workflows", {})
                legacy_skills = legacy_result.get("skills", {})
                # Only use legacy skills if no v2 skills were generated for this agent
                v2_skill_ids = {e.get("path", "") for e in results[agent].get("skills", {}).get("outputs", [])}
                if not any(agent in str(sk_path) for sk_path in v2_skill_ids):
                    results[agent]["legacy_skills"] = legacy_skills
                if legacy_result.get("status") != "PASS":
                    has_errors = True
            else:
                results[agent] = legacy_result
                if legacy_result.get("status") != "PASS":
                    has_errors = True

        agents_result = _build_result(results, agents_to_process, project_root, cypilot_root, cfg_path, copy_report, dry_run=args.dry_run)
        agents_result["manifest_v2"] = True
        agents_result["layers"] = len(resolved_layers)
        ui.result(agents_result, human_fn=lambda d: _human_generate_agents_ok(d, agents_to_process, results, dry_run=args.dry_run))
        return 0 if not has_errors else 1

    # ── EXISTING PATH: Legacy agents.toml flow (unchanged) ────────────────
    # @cpt-begin:cpt-cypilot-dod-project-extensibility-backward-compat:p1:inst-legacy-path
    # Backward compatibility: no v2.0 manifest → use existing _discover_kit_agents() flow.
    # Existing repos with no manifest.toml MUST produce identical output.

    # Handle --show-layers flag in legacy mode (no layers to show)
    if getattr(args, "show_layers", False):
        report = {"components": []}
        from ..utils.ui import is_json_mode
        if is_json_mode():
            ui.result({"status": "OK", "provenance": report})
        else:
            sys.stdout.write("Layer Provenance Report\n=======================\n(no v2.0 manifest layers found)\n")
        return 0

    # Handle --discover flag in legacy mode
    if getattr(args, "discover", False):
        discovered = discover_components(project_root)
        manifest_out = cypilot_root / "config" / "manifest.toml"
        if not args.dry_run:
            write_discovered_manifest(discovered, manifest_out)
            sys.stderr.write(f"INFO: wrote discovered manifest to {manifest_out}\n")

    # Step 1: Dry run to preview changes
    # @cpt-begin:cpt-cypilot-flow-agent-integration-generate:p1:inst-for-each-agent
    preview_results: Dict[str, Any] = {}
    for agent in agents_to_process:
        preview_results[agent] = _process_single_agent(agent, project_root, cypilot_root, cfg, cfg_path, dry_run=True)

    # Compute total changes
    total_create = 0
    total_update = 0
    total_delete = 0
    for r in preview_results.values():
        wf = r.get("workflows", {})
        sk = r.get("skills", {})
        sub = r.get("subagents", {})
        total_create += (
            len(wf.get("created", []))
            + len(sk.get("created", []))
            + len(sub.get("created", []))
        )
        total_update += (
            len(wf.get("updated", []))
            + len(wf.get("renamed", []))
            + len(sk.get("updated", []))
            + len(sub.get("updated", []))
        )
        total_delete += (
            len(wf.get("deleted", []))
            + len(sk.get("deleted", []))
            + len(sub.get("deleted", []))
        )

    if args.dry_run:
        # Just show the preview and exit
        agents_result = _build_result(preview_results, agents_to_process, project_root, cypilot_root, cfg_path, copy_report, dry_run=True)
        ui.result(agents_result, human_fn=lambda d: _human_generate_agents_ok(d, agents_to_process, preview_results, dry_run=True))
        return 0

    # Step 2: Show preview and ask for confirmation (interactive)
    if total_create == 0 and total_update == 0 and total_delete == 0:
        ui.info("No changes needed — agent files are up to date.")
    else:
        from ..utils.ui import is_json_mode
        if not is_json_mode():
            auto_approve = getattr(args, "yes", False)
            if not auto_approve:
                _human_generate_agents_preview(agents_to_process, preview_results, project_root)
            if not auto_approve and sys.stdin.isatty():
                try:
                    answer = input("  Proceed? [Y/n] ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    answer = "n"
                if answer and answer not in ("y", "yes"):
                    ui.result(
                        {"status": "ABORTED", "message": "Cancelled by user"},
                        human_fn=lambda d: (ui.warn("Aborted."), ui.blank()),
                    )
                    return 1

    # Step 3: Execute the actual write
    has_errors = False
    results: Dict[str, Any] = {}
    for agent in agents_to_process:
        result = _process_single_agent(agent, project_root, cypilot_root, cfg, cfg_path, dry_run=False)
        results[agent] = result
        if result.get("status") != "PASS":
            has_errors = True
    # @cpt-end:cpt-cypilot-flow-agent-integration-generate:p1:inst-for-each-agent

    # @cpt-begin:cpt-cypilot-flow-agent-integration-generate:p1:inst-return-report
    agents_result = _build_result(results, agents_to_process, project_root, cypilot_root, cfg_path, copy_report, dry_run=False)
    ui.result(agents_result, human_fn=lambda d: _human_generate_agents_ok(d, agents_to_process, results, dry_run=False))

    # @cpt-end:cpt-cypilot-flow-agent-integration-generate:p1:inst-return-report
    # @cpt-end:cpt-cypilot-dod-project-extensibility-backward-compat:p1:inst-legacy-path
    return 0 if not has_errors else 1

# @cpt-begin:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-format-output
def _build_result(
    results: Dict[str, Any],
    agents_to_process: List[str],
    project_root: Path,
    cypilot_root: Path,
    cfg_path: Optional[Path],
    copy_report: dict,
    dry_run: bool,
) -> Dict[str, Any]:
    has_errors = any(r.get("status") != "PASS" for r in results.values())
    return {
        "status": "PASS" if not has_errors else "PARTIAL",
        "agents": list(agents_to_process),
        "project_root": project_root.as_posix(),
        "cypilot_root": cypilot_root.as_posix(),
        "config_path": cfg_path.as_posix() if cfg_path else None,
        "dry_run": dry_run,
        "cypilot_copy": copy_report,
        "results": results,
    }

# ---------------------------------------------------------------------------
# Human-friendly formatters
# ---------------------------------------------------------------------------

def _human_agents_list(
    data: Dict[str, Any],
    agents_to_process: List[str],
    results: Dict[str, Any],
    project_root: Path,
) -> None:
    ui.header("Cypilot Agent Integrations")

    any_files = False
    for agent_name, r in results.items():
        wf = r.get("workflows", {})
        sk = r.get("skills", {})
        existing_wf = wf.get("updated", []) + wf.get("unchanged", [])
        existing_sk = list(sk.get("updated", []))
        for o in sk.get("outputs", []):
            if o.get("action") == "unchanged":
                existing_sk.append(o.get("path", ""))
        created_wf = wf.get("created", [])
        created_sk = sk.get("created", [])

        total_existing = len(existing_wf) + len(existing_sk)
        total_missing = len(created_wf) + len(created_sk)

        if total_existing > 0:
            any_files = True
            ui.step(f"{agent_name}: {total_existing} file(s) installed")
            for path in existing_wf + existing_sk:
                ui.substep(f"  {_safe_relpath(Path(path), project_root)}")
        elif total_missing > 0:
            ui.step(f"{agent_name}: not configured ({total_missing} file(s) available)")
        else:
            ui.step(f"{agent_name}: no files")

    ui.blank()
    if not any_files:
        ui.hint("No agent integrations found. Generate them with:")
        ui.hint("  cpt generate-agents")
    else:
        ui.hint("To regenerate agent files:  cpt generate-agents")
    ui.blank()

def _human_generate_agents_preview(
    agents_to_process: List[str],
    results: Dict[str, Any],
    project_root: Path,
) -> None:
    agent_label = ", ".join(agents_to_process)
    ui.header(f"Generate Agent Integration — {agent_label}")
    ui.blank()

    for agent_name, r in results.items():
        wf = r.get("workflows", {})
        sk = r.get("skills", {})
        sub = r.get("subagents", {})
        created_wf = wf.get("created", [])
        updated_wf = wf.get("updated", [])
        renamed_wf = wf.get("renamed", [])
        deleted_wf = wf.get("deleted", [])
        created_sk = sk.get("created", [])
        updated_sk = sk.get("updated", [])
        deleted_sk = sk.get("deleted", [])
        created_sub = sub.get("created", [])
        updated_sub = sub.get("updated", [])
        skipped_sub = sub.get("skipped", False)
        skipped_sub_reason = sub.get("skip_reason", "")

        if not (
            created_wf or updated_wf or renamed_wf or deleted_wf
            or created_sk or updated_sk or deleted_sk
            or created_sub or updated_sub
        ):
            ui.step(f"{agent_name}: up to date")
            if skipped_sub and skipped_sub_reason:
                ui.substep(f"subagents skipped: {skipped_sub_reason}")
            continue

        ui.step(f"{agent_name}:")
        for path in created_wf:
            ui.file_action(path, "created")
        for path in updated_wf:
            ui.file_action(path, "updated")
        for old_path, new_path in renamed_wf:
            ui.substep(f"workflow renamed: {old_path} -> {new_path}")
        for path in deleted_wf:
            ui.file_action(path, "deleted")
        for path in created_sk:
            ui.file_action(path, "created")
        for path in updated_sk:
            ui.file_action(path, "updated")
        for path in deleted_sk:
            ui.file_action(path, "deleted")
        for path in created_sub:
            ui.file_action(path, "created")
        for path in updated_sub:
            ui.file_action(path, "updated")
        if skipped_sub and skipped_sub_reason:
            ui.substep(f"subagents skipped: {skipped_sub_reason}")
    ui.blank()

def _human_generate_agents_ok(
    data: Dict[str, Any],
    agents_to_process: List[str],
    results: Dict[str, Any],
    dry_run: bool,
) -> None:
    agent_label = ", ".join(agents_to_process)
    ui.header(f"Cypilot Agent Setup — {agent_label}")

    for agent_name, r in results.items():
        agent_status = r.get("status", "?")
        wf = r.get("workflows", {})
        sk = r.get("skills", {})
        sub = r.get("subagents", {})
        wf_counts = wf.get("counts", {})
        sk_counts = sk.get("counts", {})
        sub_counts = sub.get("counts", {})

        if agent_status == "PASS":
            ui.step(f"{agent_name}")
        else:
            ui.warn(f"{agent_name} ({agent_status})")

        # Workflows
        created_wf = wf.get("created", [])
        updated_wf = wf.get("updated", [])
        renamed_wf = wf.get("renamed", [])
        deleted_wf = wf.get("deleted", [])
        for path in created_wf:
            ui.file_action(path, "created")
        for path in updated_wf:
            ui.file_action(path, "updated")
        for old_path, new_path in renamed_wf:
            ui.substep(f"workflow renamed: {old_path} -> {new_path}")
        for path in deleted_wf:
            ui.file_action(path, "deleted")

        # Skills
        created_sk = sk.get("created", [])
        updated_sk = sk.get("updated", [])
        deleted_sk = sk.get("deleted", [])
        skipped_sk = sk.get("skipped", [])
        for path in created_sk:
            ui.file_action(path, "created")
        for path in updated_sk:
            ui.file_action(path, "updated")
        for path in deleted_sk:
            ui.file_action(path, "deleted")
        for item in skipped_sk:
            ui.warn(f"  skipped: {item}")

        # Subagents
        created_sub = sub.get("created", [])
        updated_sub = sub.get("updated", [])
        for path in created_sub:
            ui.file_action(path, "created")
        for path in updated_sub:
            ui.file_action(path, "updated")
        if sub.get("skipped") and sub.get("skip_reason"):
            ui.substep(f"subagents skipped: {sub.get('skip_reason')}")

        # V2 manifest agents
        v2_ag = r.get("v2_agents", {})
        created_v2_ag = v2_ag.get("created", [])
        updated_v2_ag = v2_ag.get("updated", [])
        for path in created_v2_ag:
            ui.file_action(path, "created")
        for path in updated_v2_ag:
            ui.file_action(path, "updated")

        total_wf = (
            wf_counts.get("created", 0)
            + wf_counts.get("updated", 0)
            + wf_counts.get("renamed", 0)
        )
        total_wf_deleted = wf_counts.get("deleted", 0)
        total_sk = sk_counts.get("created", 0) + sk_counts.get("updated", 0)
        total_sub = sub_counts.get("created", 0) + sub_counts.get("updated", 0)
        total_v2_ag = len(created_v2_ag) + len(updated_v2_ag)
        total_deleted = sk_counts.get("deleted", 0)
        total_skipped = sk_counts.get("skipped", 0)
        if total_wf or total_wf_deleted or total_sk or total_sub or total_v2_ag or total_deleted or total_skipped:
            parts = []
            if total_wf:
                parts.append(f"{total_wf} workflow(s)")
            if total_wf_deleted:
                parts.append(
                    f"{total_wf_deleted} workflow proxy/proxies {'would be removed' if dry_run else 'removed'}"
                )
            if total_sk:
                parts.append(f"{total_sk} skill file(s)")
            if total_sub:
                parts.append(f"{total_sub} subagent file(s)")
            if total_v2_ag:
                parts.append(f"{total_v2_ag} agent file(s)")
            if total_deleted:
                parts.append(
                    f"{total_deleted} legacy command(s) {'would be removed' if dry_run else 'removed'}"
                )
            if total_skipped:
                parts.append(
                    f"{total_skipped} legacy command(s) {'would be preserved' if dry_run else 'preserved'}"
                )
            ui.substep(", ".join(parts))

        # Errors
        errs = r.get("errors") or []
        for e in errs:
            ui.warn(f"  {e}")

    if dry_run:
        ui.success("Dry run complete — no files were written.")
    elif data.get("status") == "PASS":
        ui.success("Agent integration complete!")
        ui.blank()
        ui.info("Your IDE will now:")
        ui.hint("• Route /cypilot-generate, /cypilot-analyze, /cypilot-plan, and /cypilot-workspace to Cypilot workflows")
        ui.hint("• Recognize the Cypilot skill in chat")
    else:
        ui.warn("Agent setup finished with some errors (see above).")
    ui.blank()
# @cpt-end:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-format-output


# ---------------------------------------------------------------------------
# Extended Agent Schema Translation (Phase 5)
# @cpt-algo:cpt-cypilot-algo-project-extensibility-translate-agent-schema:p1
# @cpt-algo:cpt-cypilot-algo-project-extensibility-generate-skills:p1
# ---------------------------------------------------------------------------

# AgentEntry and SkillEntry come from manifest.py (Phases 1-4).
from ..utils.manifest import AgentEntry as _AgentEntry, SkillEntry as _SkillEntry  # type: ignore


# @cpt-begin:cpt-cypilot-algo-project-extensibility-translate-agent-schema:p1:inst-per-tool-translators

def _translate_claude_schema(agent: "_AgentEntry") -> Dict[str, Any]:
    """Translate AgentEntry to Claude Code native frontmatter.

    Supports all extended fields: tools, disallowed_tools, model, isolation,
    color, memory_dir.
    """
    # @cpt-begin:cpt-cypilot-algo-project-extensibility-translate-agent-schema:p1:inst-step-claude
    frontmatter: List[str] = []

    # MCP tools (mcp__* prefix) are deferred pending an ADR — strip before writing frontmatter.
    filtered_tools = [t for t in (agent.tools or []) if not t.startswith("mcp__")]
    filtered_disallowed = [t for t in (agent.disallowed_tools or []) if not t.startswith("mcp__")]

    # tools or disallowed_tools (mutual exclusivity already validated)
    if filtered_tools:
        frontmatter.append("tools: " + ", ".join(filtered_tools))
    elif filtered_disallowed:
        frontmatter.append("disallowedTools: " + ", ".join(filtered_disallowed))
    elif agent.mode == "readonly":
        frontmatter.append("tools: Bash, Read, Glob, Grep")
        frontmatter.append("disallowedTools: Write, Edit")
    else:
        frontmatter.append("tools: Bash, Read, Write, Edit, Glob, Grep")

    if agent.model:
        frontmatter.append(f"model: {agent.model}")

    if agent.isolation:
        frontmatter.append("isolation: worktree")

    if agent.skills:
        frontmatter.append(f"skills: {', '.join(agent.skills)}")

    if agent.color:
        frontmatter.append(f"color: {agent.color}")

    # memory_dir is NOT a frontmatter field — appended as a note after prompt body
    body_suffix = ""
    if agent.memory_dir:
        body_suffix = f"\n\n---\n*Agent memory directory: `{agent.memory_dir}`*"

    # @cpt-end:cpt-cypilot-algo-project-extensibility-translate-agent-schema:p1:inst-step-claude
    return {
        "frontmatter": frontmatter,
        "body_prefix": "",
        "body_suffix": body_suffix,
        "skip": False,
        "skip_reason": "",
    }


def _translate_cursor_schema(agent: "_AgentEntry") -> Dict[str, Any]:
    """Translate AgentEntry to Cursor native frontmatter.

    Maps mode to limited tool strings. Ignores color, memory_dir, isolation.
    """
    # @cpt-begin:cpt-cypilot-algo-project-extensibility-translate-agent-schema:p1:inst-step-cursor
    frontmatter: List[str] = []

    if agent.mode == "readonly":
        frontmatter.append("tools: grep, view, bash")
        frontmatter.append("readonly: true")
    else:
        frontmatter.append("tools: grep, view, edit, bash")

    if agent.model:
        frontmatter.append(f"model: {agent.model}")

    # @cpt-end:cpt-cypilot-algo-project-extensibility-translate-agent-schema:p1:inst-step-cursor
    return {
        "frontmatter": frontmatter,
        "body_prefix": "",
        "skip": False,
        "skip_reason": "",
    }


def _translate_copilot_schema(agent: "_AgentEntry") -> Dict[str, Any]:
    """Translate AgentEntry to GitHub Copilot native frontmatter.

    Produces tools JSON array. No model/isolation/color support.
    """
    # @cpt-begin:cpt-cypilot-algo-project-extensibility-translate-agent-schema:p1:inst-step-copilot
    frontmatter: List[str] = []

    if agent.tools:
        tools_json = json.dumps(agent.tools)
        frontmatter.append(f"tools: {tools_json}")
    elif agent.mode == "readonly":
        frontmatter.append('tools: ["read", "search"]')
    else:
        frontmatter.append('tools: ["*"]')

    # @cpt-end:cpt-cypilot-algo-project-extensibility-translate-agent-schema:p1:inst-step-copilot
    return {
        "frontmatter": frontmatter,
        "body_prefix": "",
        "skip": False,
        "skip_reason": "",
    }


def _translate_codex_schema(agent: "_AgentEntry") -> Dict[str, Any]:
    """Translate AgentEntry to OpenAI Codex TOML config dict.

    Maps mode to sandbox_mode. Per-agent tool restrictions not supported.
    """
    # @cpt-begin:cpt-cypilot-algo-project-extensibility-translate-agent-schema:p1:inst-step-codex
    sandbox_mode = "read-only" if agent.mode == "readonly" else "workspace-write"

    result: Dict[str, Any] = {
        "sandbox_mode": sandbox_mode,
        "developer_instructions": agent.description or "",
        "skip": False,
        "skip_reason": "",
        "frontmatter": [],
        "body_prefix": "",
    }

    if agent.model:
        result["model"] = agent.model

    # @cpt-end:cpt-cypilot-algo-project-extensibility-translate-agent-schema:p1:inst-step-codex
    return result


def _translate_windsurf_schema(agent: "_AgentEntry") -> Dict[str, Any]:
    """Windsurf does not support subagent generation — returns skip result."""
    # @cpt-begin:cpt-cypilot-algo-project-extensibility-translate-agent-schema:p1:inst-step-windsurf
    return {
        "frontmatter": [],
        "body_prefix": "",
        "skip": True,
        "skip_reason": "Windsurf does not support subagent generation",
    }
    # @cpt-end:cpt-cypilot-algo-project-extensibility-translate-agent-schema:p1:inst-step-windsurf

# @cpt-end:cpt-cypilot-algo-project-extensibility-translate-agent-schema:p1:inst-per-tool-translators


# Dispatch table: maps target tool name to per-tool translator function.
_SCHEMA_TRANSLATOR_MAP: Dict[str, Any] = {
    "claude": _translate_claude_schema,
    "cursor": _translate_cursor_schema,
    "copilot": _translate_copilot_schema,
    "openai": _translate_codex_schema,
    "windsurf": _translate_windsurf_schema,
}


# @cpt-begin:cpt-cypilot-algo-project-extensibility-translate-agent-schema:p1:inst-translate-agent-schema
def translate_agent_schema(agent: "_AgentEntry", target: str) -> Dict[str, Any]:
    """Translate a manifest AgentEntry to agent-native frontmatter/config.

    Validates mutual exclusivity of tools and disallowed_tools, then dispatches
    to the appropriate per-tool translator.

    Args:
        agent: AgentEntry from merged manifest (Phase 4).
        target: Target tool name ('claude', 'cursor', 'copilot', 'openai', 'windsurf').

    Returns:
        Dict with keys: frontmatter (List[str]), body_prefix (str),
        skip (bool), skip_reason (str), plus tool-specific extras.

    Raises:
        ValueError: if both tools and disallowed_tools are set, or target unknown.
    """
    # Step 1: Validate mutual exclusivity of tools and disallowed_tools
    if agent.tools and agent.disallowed_tools:
        raise ValueError(
            f"Agent '{agent.id}': 'tools' and 'disallowed_tools' are mutually exclusive — "
            "set one or neither, not both."
        )

    # Step 2: Dispatch to per-tool translator
    translator_fn = _SCHEMA_TRANSLATOR_MAP.get(target)
    if translator_fn is None:
        raise ValueError(
            f"Unknown target tool '{target}'. "
            f"Supported targets: {sorted(_SCHEMA_TRANSLATOR_MAP.keys())}"
        )

    return translator_fn(agent)
# @cpt-end:cpt-cypilot-algo-project-extensibility-translate-agent-schema:p1:inst-translate-agent-schema


# Skill output paths per agent tool
_SKILL_OUTPUT_PATHS: Dict[str, str] = {
    "claude":   ".claude/skills/{id}/SKILL.md",
    "cursor":   ".cursor/rules/{id}.mdc",
    "copilot":  ".github/skills/{id}.md",
    "openai":   ".agents/skills/{id}/SKILL.md",
    "windsurf": ".windsurf/skills/{id}/SKILL.md",
}


# @cpt-begin:cpt-cypilot-algo-project-extensibility-generate-skills:p1:inst-generate-manifest-skills
def generate_manifest_skills(
    skills: Dict[str, "_SkillEntry"],
    target: str,
    project_root: Path,
    dry_run: bool,
    variables: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Generate skill files from merged [[skills]] manifest entries.

    Iterates skills where the target agent is in the skill's agents list,
    reads source content, applies agent-specific frontmatter wrapper,
    determines the output path, and writes the skill file.

    Args:
        skills: Dict of skill_id -> SkillEntry from merged manifest.
        target: Target tool name ('claude', 'cursor', 'copilot', 'openai', 'windsurf').
        project_root: Absolute path to project root directory.
        dry_run: If True, compute actions but do not write files.

    Returns:
        Dict with keys: created (List[str]), updated (List[str]),
        unchanged (List[str]), outputs (List[dict]).
    """
    result: Dict[str, Any] = {
        "created": [],
        "updated": [],
        "unchanged": [],
        "outputs": [],
    }

    path_template = _SKILL_OUTPUT_PATHS.get(target, f".{target}/skills/{{id}}/SKILL.md")

    # Step 1: FOR EACH skill where target is in agents list (empty list = all targets)
    for skill_id, skill in skills.items():
        # Empty agents list means "generate for all targets" (consistent with agents behavior)
        if skill.agents and target not in skill.agents:
            continue

        # Step 1.1: Determine source path (prefer source over prompt_file)
        src_path_str = skill.source or skill.prompt_file
        if not src_path_str:
            sys.stderr.write(
                f"WARNING: skill '{skill_id}' has no source or prompt_file, skipping\n"
            )
            continue

        src_path = Path(src_path_str)
        if not src_path.is_absolute():
            src_path = project_root / src_path_str

        # Step 1.1 continued: Read source content
        if not src_path.is_file():
            sys.stderr.write(
                f"WARNING: skill '{skill_id}' source not found: {src_path}, skipping\n"
            )
            continue

        try:
            source_content = src_path.read_text(encoding="utf-8")
        except Exception as exc:
            sys.stderr.write(
                f"WARNING: skill '{skill_id}' failed to read source: {exc}, skipping\n"
            )
            continue

        # Step 1.2: Apply agent-specific frontmatter wrapper
        # For Claude: wrap with YAML frontmatter (name + description)
        # For other targets: use source content as-is
        if target == "claude":
            escaped_desc = skill.description.replace("\\", "\\\\").replace('"', '\\"')
            fm_lines = [
                "---",
                f"name: {skill_id}",
                f'description: "{escaped_desc}"',
                "---",
                "",
            ]
            content = "\n".join(fm_lines) + source_content
        else:
            content = source_content

        # Apply accumulated section appends (from merge_component_entry)
        if skill.append:
            content = content.rstrip("\n") + "\n" + skill.append

        # Apply layer variable substitution
        if variables:
            for k, v in variables.items():
                content = content.replace(f"{{{k}}}", v)

        # Step 1.3: Determine output path using agent-native conventions
        rel_out = path_template.replace("{id}", skill_id)
        out_path = project_root / rel_out

        # Step 1.4: Write skill file to output path using _write_or_skip
        _write_or_skip(out_path, content, result, project_root, dry_run)

    # Step 3: Return result dict
    result["unchanged"] = [
        o["path"] for o in result["outputs"] if o.get("action") == "unchanged"
    ]
    return result


# Agent output paths per agent tool
# @cpt-algo:cpt-cypilot-algo-project-extensibility-generate-agents:p1
# @cpt-dod:cpt-cypilot-dod-project-extensibility-agents-generation:p1
_AGENT_OUTPUT_PATHS: Dict[str, str] = {
    "claude":   ".claude/agents/{id}.md",
    "cursor":   ".cursor/agents/{id}.mdc",
    "copilot":  ".github/agents/{id}.md",
    "openai":   ".agents/{id}/agent.md",
    # windsurf: no subagent support — handled via translate_agent_schema skip
}


# @cpt-begin:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-generate-manifest-agents
def generate_manifest_agents(
    agents: Dict[str, "_AgentEntry"],
    target: str,
    project_root: Path,
    dry_run: bool,
    variables: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Generate agent files from merged [[agents]] manifest entries.

    Iterates agents where the target tool is in the agent's agents list,
    calls translate_agent_schema to obtain frontmatter and body_prefix,
    assembles the full file (YAML frontmatter + body), determines the output
    path using agent-native conventions, and writes the agent file.

    Args:
        agents: Dict of agent_id -> AgentEntry from merged manifest.
        target: Target tool name ('claude', 'cursor', 'copilot', 'openai', 'windsurf').
        project_root: Absolute path to project root directory.
        dry_run: If True, compute actions but do not write files.

    Returns:
        Dict with keys: created (List[str]), updated (List[str]),
        unchanged (List[str]), outputs (List[dict]).
    """
    result: Dict[str, Any] = {
        "created": [],
        "updated": [],
        "unchanged": [],
        "outputs": [],
    }

    path_template = _AGENT_OUTPUT_PATHS.get(target, f".{target}/agents/{{id}}.md")

    # Step 1: FOR EACH agent where target is in agents list
    # @cpt-begin:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-iterate-agents
    for agent_id, agent in agents.items():
        # Empty agents list means "generate for all targets"
        if agent.agents and target not in agent.agents:
            continue

        # Step 1.1: Call translate_agent_schema to get frontmatter dict + body_prefix
        # @cpt-begin:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-translate-schema
        try:
            translated = translate_agent_schema(agent, target)
        except ValueError as exc:
            sys.stderr.write(
                f"WARNING: agent '{agent_id}' schema translation failed for target '{target}': {exc}, skipping\n"
            )
            result.setdefault("errors", []).append({"agent": agent_id, "error": str(exc)})
            continue
        # @cpt-end:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-translate-schema

        # Step 1.2: IF skip=True → skip agent, log skip reason, continue
        # @cpt-begin:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-check-skip
        if translated.get("skip"):
            skip_reason = translated.get("skip_reason", "")
            sys.stderr.write(
                f"INFO: agent '{agent_id}' skipped for target '{target}': {skip_reason}\n"
            )
            continue
        # @cpt-end:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-check-skip

        # Step 1.3: Read prompt_file (or source) content from agent's resolved path
        # @cpt-begin:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-read-agent-source
        src_path_str = agent.source or agent.prompt_file
        if not src_path_str:
            sys.stderr.write(
                f"WARNING: agent '{agent_id}' has no source or prompt_file, skipping\n"
            )
            continue

        src_path = Path(src_path_str)
        if not src_path.is_absolute():
            src_path = project_root / src_path_str

        if not src_path.is_file():
            sys.stderr.write(
                f"WARNING: agent '{agent_id}' source not found: {src_path}, skipping\n"
            )
            continue

        try:
            source_content = src_path.read_text(encoding="utf-8")
        except Exception as exc:
            sys.stderr.write(
                f"WARNING: agent '{agent_id}' failed to read source: {exc}, skipping\n"
            )
            continue

        # Strip existing frontmatter from source so manifest-generated frontmatter
        # is the only frontmatter in the output.
        if source_content.startswith("---"):
            end_idx = source_content.find("\n---\n", 4)
            if end_idx != -1:
                source_content = source_content[end_idx + 5:]
        # @cpt-end:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-read-agent-source

        # Step 1.4: Assemble full file: YAML frontmatter block (name:, description:,
        # translated fields), then body (body_prefix + prompt content)
        # @cpt-begin:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-assemble-agent-file
        if not agent.description:
            sys.stderr.write(
                f"WARNING: agent '{agent_id}' has no description — agent will not register with Claude CLI\n"
            )
            continue

        # Special path for OpenAI/Codex: emit TOML format
        if target == "openai":
            sandbox_mode = translated.get("sandbox_mode", "workspace-write")
            dev_instructions = translated.get("developer_instructions", agent.description or "")
            model_str = translated.get("model", "")
            toml_lines = [f"[agents.{agent_id.replace('-', '_')}]"]
            escaped_desc = (agent.description or "").replace("\\", "\\\\").replace('"', '\\"')
            toml_lines.append(f'description = "{escaped_desc}"')
            toml_lines.append(f'sandbox_mode = "{sandbox_mode}"')
            if model_str and model_str != "inherit":
                toml_lines.append(f'model = "{model_str}"')
            toml_lines.append('developer_instructions = """')
            toml_lines.append(dev_instructions)
            toml_lines.append('"""')
            if agent.append:
                toml_lines.append(agent.append)
            content = "\n".join(toml_lines) + "\n"
            if variables:
                for k, v in variables.items():
                    content = content.replace(f"{{{k}}}", v)
            # Use .toml extension for codex output
            rel_out = path_template.replace("{id}", agent_id).replace(".md", ".toml")
            out_path = project_root / rel_out
            _write_or_skip(out_path, content, result, project_root, dry_run)
            continue

        frontmatter_lines: List[str] = ["---"]
        frontmatter_lines.append(f"name: {agent.id}")
        escaped = agent.description.replace("\\", "\\\\").replace('"', '\\"')
        frontmatter_lines.append(f'description: "{escaped}"')
        frontmatter_lines.extend(translated.get("frontmatter", []))
        frontmatter_lines.append("---")

        body_prefix = translated.get("body_prefix", "")
        body_suffix = translated.get("body_suffix", "")
        content = "\n".join(frontmatter_lines) + "\n" + body_prefix + source_content + body_suffix

        # Apply accumulated section appends (from merge_component_entry)
        if agent.append:
            content = content.rstrip("\n") + "\n" + agent.append

        # Apply layer variable substitution
        if variables:
            for k, v in variables.items():
                content = content.replace(f"{{{k}}}", v)
        # @cpt-end:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-assemble-agent-file

        # Step 1.5: Determine output path using agent-native conventions
        # @cpt-begin:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-determine-agent-path
        rel_out = path_template.replace("{id}", agent_id)
        out_path = project_root / rel_out
        # @cpt-end:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-determine-agent-path

        # Step 1.6: Write agent file to output path
        # @cpt-begin:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-write-agent
        _write_or_skip(out_path, content, result, project_root, dry_run)
        # @cpt-end:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-write-agent

    # @cpt-end:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-iterate-agents

    # Step 2/3: Track created/updated/unchanged and return
    # @cpt-begin:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-track-agent-results
    result["unchanged"] = [
        o["path"] for o in result["outputs"] if o.get("action") == "unchanged"
    ]
    # @cpt-end:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-track-agent-results

    # @cpt-begin:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-return-agents
    return result
    # @cpt-end:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-return-agents

# @cpt-end:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-generate-manifest-agents


# ---------------------------------------------------------------------------
# Provenance Report + Auto-Discovery (Phase 7)
# @cpt-algo:cpt-cypilot-algo-project-extensibility-build-provenance:p2
# @cpt-flow:cpt-cypilot-flow-project-extensibility-discover-register:p2
# ---------------------------------------------------------------------------

from ..utils.manifest import MergedComponents as _MergedComponents, ProvenanceRecord as _ProvenanceRecord  # type: ignore  # noqa: E402


# @cpt-begin:cpt-cypilot-algo-project-extensibility-build-provenance:p2:inst-step1-build-report
def build_provenance_report(
    merged: "_MergedComponents",
    project_root: Path,
) -> Dict[str, Any]:
    """Build a JSON-serializable provenance report from MergedComponents.

    Iterates all component types in merged result, records winning layer,
    overridden layers, and source paths for each component.  Output is
    sorted by component type then component ID for deterministic results.

    Args:
        merged:       MergedComponents result from merge_components().
        project_root: Absolute path to project root (used to make paths relative).

    Returns:
        JSON-serializable dict with key ``"components"``: list of records,
        each containing id, type, winning_scope, winning_path, overridden.
    """
    # @cpt-begin:cpt-cypilot-algo-project-extensibility-build-provenance:p2:inst-step1-inner
    component_sections: List[Tuple[str, Dict]] = [
        ("agents", merged.agents),
        ("skills", merged.skills),
        ("workflows", merged.workflows),
        ("rules", merged.rules),
    ]

    records: List[Dict[str, Any]] = []

    for component_type, component_dict in component_sections:
        # @cpt-begin:cpt-cypilot-algo-project-extensibility-build-provenance:p2:inst-step1-foreach-id
        for cid in sorted(component_dict.keys()):
            prov: "_ProvenanceRecord" = merged.provenance[cid]

            # Winning layer info
            winning_path_str = _safe_relpath(prov.winning_path, project_root)

            # Overridden layers info
            overridden_list: List[Dict[str, str]] = []
            for scope, path in prov.overridden:
                overridden_list.append({
                    "scope": scope,
                    "path": _safe_relpath(path, project_root),
                })

            # Source path from the component entry
            entry = component_dict[cid]
            source_path = getattr(entry, "source", "") or getattr(entry, "prompt_file", "") or ""
            if source_path:
                source_path_obj = Path(source_path)
                if source_path_obj.is_absolute():
                    try:
                        source_path = source_path_obj.relative_to(project_root).as_posix()
                    except ValueError:
                        source_path = source_path_obj.as_posix()

            record: Dict[str, Any] = {
                "id": cid,
                "type": component_type,
                "winning_scope": prov.winning_scope,
                "winning_path": winning_path_str,
                "overridden": overridden_list,
            }
            if source_path:
                record["source_path"] = source_path

            records.append(record)
        # @cpt-end:cpt-cypilot-algo-project-extensibility-build-provenance:p2:inst-step1-foreach-id
    # @cpt-end:cpt-cypilot-algo-project-extensibility-build-provenance:p2:inst-step1-inner

    # Step 2: Sort by type then ID (type order is deterministic via section order above,
    # IDs within each type are already sorted).
    return {"components": records}
# @cpt-end:cpt-cypilot-algo-project-extensibility-build-provenance:p2:inst-step1-build-report


def format_provenance_human(report: Dict[str, Any]) -> str:
    """Format a provenance report as a human-readable table.

    Produces output matching the --show-layers format described in the phase spec.

    Args:
        report: Dict returned by build_provenance_report().

    Returns:
        Multi-line string with Layer Provenance Report table.
    """
    components: List[Dict[str, Any]] = report.get("components", [])

    # Group by type
    by_type: Dict[str, List[Dict[str, Any]]] = {}
    for rec in components:
        t = rec["type"]
        by_type.setdefault(t, []).append(rec)

    lines: List[str] = ["Layer Provenance Report", "======================="]

    # Emit in canonical section order
    section_order = ["agents", "skills", "workflows", "rules"]
    for section in section_order:
        recs = by_type.get(section, [])
        if not recs:
            continue
        lines.append(f"\n{section.capitalize()}:")
        for rec in recs:
            cid = rec["id"]
            scope = rec["winning_scope"].capitalize()
            path = rec["winning_path"]
            overridden = rec.get("overridden", [])
            override_str = ""
            if overridden:
                override_scopes = ", ".join(o["scope"].capitalize() for o in overridden)
                override_str = f"    overrides: {override_scopes}"
            # Align: component ID padded to 16 chars, then scope/path
            lines.append(f"  {cid:<16} {scope} ({path}){override_str}")

    return "\n".join(lines)


# @cpt-begin:cpt-cypilot-flow-project-extensibility-discover-register:p2:inst-step2-scan-dirs
def discover_components(project_root: Path) -> Dict[str, List[Dict[str, str]]]:
    """Scan conventional directories for components.

    Searches the following conventional paths relative to *project_root*:
    - .claude/agents/*.md  → agents (ID = filename stem)
    - .claude/skills/*/SKILL.md → skills (ID = parent directory name)
    - .claude/commands/*.md → workflows (ID = filename stem)

    For each discovered file, attempts to extract a description from YAML
    frontmatter (``description:`` line) if present.

    Args:
        project_root: Absolute path to project root directory.

    Returns:
        Dict mapping component type (``"agents"``, ``"skills"``, ``"workflows"``)
        to a list of dicts, each with ``"id"``, ``"source"``, ``"description"``.
    """
    discovered: Dict[str, List[Dict[str, str]]] = {
        "agents": [],
        "skills": [],
        "workflows": [],
    }

    # @cpt-begin:cpt-cypilot-flow-project-extensibility-discover-register:p2:inst-step2.1-agents
    _claude = project_root / ".claude"
    agents_dir = _claude / "agents"
    if agents_dir.is_dir():
        for md_file in sorted(agents_dir.glob("*.md")):
            if md_file.is_file():
                component_id = md_file.stem
                description = _extract_frontmatter_description(md_file)
                discovered["agents"].append({
                    "id": component_id,
                    "source": md_file.as_posix(),
                    "description": description,
                })
    # @cpt-end:cpt-cypilot-flow-project-extensibility-discover-register:p2:inst-step2.1-agents

    # @cpt-begin:cpt-cypilot-flow-project-extensibility-discover-register:p2:inst-step2.2-skills
    skills_dir = _claude / "skills"
    if skills_dir.is_dir():
        for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
            if skill_md.is_file():
                component_id = skill_md.parent.name
                description = _extract_frontmatter_description(skill_md)
                discovered["skills"].append({
                    "id": component_id,
                    "source": skill_md.as_posix(),
                    "description": description,
                })
    # @cpt-end:cpt-cypilot-flow-project-extensibility-discover-register:p2:inst-step2.2-skills

    # @cpt-begin:cpt-cypilot-flow-project-extensibility-discover-register:p2:inst-step2.3-workflows
    commands_dir = _claude / "commands"
    if commands_dir.is_dir():
        for md_file in sorted(commands_dir.glob("*.md")):
            if md_file.is_file():
                component_id = md_file.stem
                description = _extract_frontmatter_description(md_file)
                discovered["workflows"].append({
                    "id": component_id,
                    "source": md_file.as_posix(),
                    "description": description,
                })
    # @cpt-end:cpt-cypilot-flow-project-extensibility-discover-register:p2:inst-step2.3-workflows

    return discovered
# @cpt-end:cpt-cypilot-flow-project-extensibility-discover-register:p2:inst-step2-scan-dirs


def _extract_frontmatter_description(path: Path) -> str:
    """Extract description from YAML frontmatter in a markdown file.

    Looks for a ``description:`` key in the YAML front matter block delimited
    by ``---`` markers.  Returns empty string if not found or on any error.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return ""

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""

    _desc_key = "description:"
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith(_desc_key):
            return line[len(_desc_key):].strip().strip('"').strip("'")

    return ""


# @cpt-begin:cpt-cypilot-flow-project-extensibility-discover-register:p2:inst-step4-write-manifest
def write_discovered_manifest(
    discovered: Dict[str, List[Dict[str, str]]],
    manifest_path: Path,
) -> None:
    """Write or update a manifest.toml with discovered component sections.

    Generates a v2.0 manifest.toml at *manifest_path* from the *discovered*
    components dict (as returned by ``discover_components()``).  If the file
    already exists, reads existing ``id`` values and only appends entries
    whose IDs are not already present.  If all discovered entries are already
    present, the file is not modified.

    The ``manifest_path``'s parent directory is created if it does not exist.

    Args:
        discovered:    Dict mapping component type to list of component dicts
                       (each with ``id``, ``source``, ``description``).
        manifest_path: Absolute path to the manifest.toml to write.
    """
    manifest_path.parent.mkdir(parents=True, exist_ok=True)  # NOSONAR

    # If the file already exists, collect existing IDs via simple string scan
    # and only write entries whose IDs are not already present.
    existing_ids: Set[str] = set()
    existing_content: Optional[str] = None
    if manifest_path.is_file():
        try:
            existing_content = manifest_path.read_text(encoding="utf-8")
        except Exception:
            existing_content = None
        if existing_content is not None:
            import re as _re
            for m in _re.finditer(r'^id\s*=\s*"([^"]+)"', existing_content, _re.MULTILINE):
                existing_ids.add(m.group(1))

    section_order = ["agents", "skills", "workflows"]

    if existing_content is not None:
        # Append-only mode: only write new entries
        new_lines: List[str] = []
        for section in section_order:
            entries = discovered.get(section, [])
            for entry in entries:
                if entry["id"] in existing_ids:
                    continue
                new_lines.append(f'[[{section}]]')
                new_lines.append(f'id = "{entry["id"]}"')
                if entry.get("description"):
                    desc = entry["description"].replace('"', '\\"')
                    new_lines.append(f'description = "{desc}"')
                if entry.get("source"):
                    src = entry["source"].replace('"', '\\"')
                    new_lines.append(f'source = "{src}"')
                new_lines.append('')

        if not new_lines:
            # All discovered entries already present — skip write
            return

        appended = existing_content.rstrip("\n") + "\n\n# New entries appended by --discover\n" + "\n".join(new_lines)
        manifest_path.write_text(appended, encoding="utf-8")  # NOSONAR
        return

    # Fresh write
    lines: List[str] = [
        '[manifest]',
        'version = "2.0"',
        '',
    ]

    for section in section_order:
        entries = discovered.get(section, [])
        for entry in entries:
            lines.append(f'[[{section}]]')
            lines.append(f'id = "{entry["id"]}"')
            if entry.get("description"):
                desc = entry["description"].replace('"', '\\"')
                lines.append(f'description = "{desc}"')
            if entry.get("source"):
                src = entry["source"].replace('"', '\\"')
                lines.append(f'source = "{src}"')
            lines.append('')

    manifest_path.write_text("\n".join(lines), encoding="utf-8")  # NOSONAR
# @cpt-end:cpt-cypilot-flow-project-extensibility-discover-register:p2:inst-step4-write-manifest
# @cpt-end:cpt-cypilot-algo-project-extensibility-generate-skills:p1:inst-generate-manifest-skills
