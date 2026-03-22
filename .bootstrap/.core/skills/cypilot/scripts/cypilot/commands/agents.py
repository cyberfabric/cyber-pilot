"""
Agent Entry Point Generator

Generates agent-native entry points (Windsurf, Cursor, Claude, Copilot, OpenAI),
composes SKILL.md from kit @cpt:skill sections, and creates workflow proxies.

@cpt-flow:cpt-cypilot-flow-agent-integration-generate:p1
@cpt-flow:cpt-cypilot-flow-agent-integration-workflow:p1
@cpt-algo:cpt-cypilot-algo-agent-integration-discover-agents:p1
@cpt-algo:cpt-cypilot-algo-agent-integration-generate-shims:p1
@cpt-algo:cpt-cypilot-algo-agent-integration-compose-skill:p1
@cpt-algo:cpt-cypilot-algo-agent-integration-list-workflows:p1
@cpt-state:cpt-cypilot-state-agent-integration-entry-points:p1
@cpt-dod:cpt-cypilot-dod-agent-integration-entry-points:p1
@cpt-dod:cpt-cypilot-dod-agent-integration-skill-composition:p1
@cpt-dod:cpt-cypilot-dod-agent-integration-workflow-discovery:p1
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
    rel = _safe_relpath(out_path, project_root)
    if not out_path.exists():
        result["created"].append(out_path.as_posix())
        if not dry_run:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(content, encoding="utf-8")
        result["outputs"].append({"path": rel, "action": "created"})
    else:
        try:
            old = out_path.read_text(encoding="utf-8")
        except Exception:
            old = ""
        if old != content:
            result["updated"].append(out_path.as_posix())
            if not dry_run:
                out_path.write_text(content, encoding="utf-8")
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
    _VALID_MODELS = {"inherit", "fast"}

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
            seen_names.add(name)
            prompt_rel = info.get("prompt_file", "")
            prompt_abs = None
            if prompt_rel:
                candidate = (source_dir / prompt_rel).resolve()
                # Ensure resolved path stays within source_dir (prevent path traversal)
                try:
                    candidate.relative_to(source_dir.resolve())
                    prompt_abs = candidate
                except ValueError:
                    sys.stderr.write(
                        f"WARNING: agent {name!r} prompt_file escapes source dir, skipping\n"
                    )
                    continue
            mode = info.get("mode", "readwrite")
            model = info.get("model", "inherit")
            if mode not in _VALID_MODES:
                sys.stderr.write(
                    f"WARNING: agent {name!r} has invalid mode {mode!r}, skipping\n"
                )
                continue
            if model not in _VALID_MODELS:
                sys.stderr.write(
                    f"WARNING: agent {name!r} has invalid model {model!r}, skipping\n"
                )
                continue
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
            _human_generate_agents_preview(agents_to_process, preview_results, project_root)
            auto_approve = getattr(args, "yes", False)
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

        total_wf = (
            wf_counts.get("created", 0)
            + wf_counts.get("updated", 0)
            + wf_counts.get("renamed", 0)
        )
        total_wf_deleted = wf_counts.get("deleted", 0)
        total_sk = sk_counts.get("created", 0) + sk_counts.get("updated", 0)
        total_sub = sub_counts.get("created", 0) + sub_counts.get("updated", 0)
        total_deleted = sk_counts.get("deleted", 0)
        total_skipped = sk_counts.get("skipped", 0)
        if total_wf or total_wf_deleted or total_sk or total_sub or total_deleted or total_skipped:
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
