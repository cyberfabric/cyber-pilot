"""
Agent Entry Point Generator

Generates agent-native entry points (Windsurf, Cursor, Claude, Copilot, OpenAI),
composes SKILL.md from kit @cpt:skill sections, and creates workflow proxies.

@cpt-flow:cpt-cypilot-flow-agent-integration-generate:p1
@cpt-flow:cpt-cypilot-flow-agent-integration-workflow:p1
@cpt-flow:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1
@cpt-flow:cpt-cypilot-flow-project-extensibility-discover-register:p2
@cpt-algo:cpt-cypilot-algo-agent-integration-discover-agents:p1
@cpt-algo:cpt-cypilot-algo-agent-integration-generate-shims:p1
@cpt-algo:cpt-cypilot-algo-agent-integration-compose-skill:p1
@cpt-algo:cpt-cypilot-algo-agent-integration-list-workflows:p1
@cpt-algo:cpt-cypilot-algo-project-extensibility-translate-agent-schema:p1
@cpt-algo:cpt-cypilot-algo-project-extensibility-generate-skills:p1
@cpt-algo:cpt-cypilot-algo-project-extensibility-generate-agents:p1
@cpt-algo:cpt-cypilot-algo-project-extensibility-build-provenance:p2
@cpt-state:cpt-cypilot-state-agent-integration-entry-points:p1
@cpt-dod:cpt-cypilot-dod-agent-integration-entry-points:p1
@cpt-dod:cpt-cypilot-dod-agent-integration-skill-composition:p1
@cpt-dod:cpt-cypilot-dod-agent-integration-workflow-discovery:p1
@cpt-dod:cpt-cypilot-dod-project-extensibility-agents-generation:p1
@cpt-dod:cpt-cypilot-dod-project-extensibility-backward-compat:p1
"""

# @cpt-begin:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-agents-datamodel
import argparse
import json
import re
import shutil
import sys
import tomllib
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Regex for valid TOML bare key / agent name: ASCII letters, digits, hyphen, underscore.
_VALID_AGENT_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")

from ..utils.files import core_subpath, config_subpath, find_project_root, _is_cypilot_root, _read_cypilot_var, load_project_config
from ..utils.ui import ui

_TMPL_NAME = "name: {name}"
_TMPL_DESCRIPTION = "description: {description}"
_AGENT_TEMPLATE_HEADER = ["---", _TMPL_NAME, _TMPL_DESCRIPTION]
_ALWAYS_FOLLOW_TARGET_PATH = "ALWAYS open and follow `{target_path}`"
_FOLLOW_LINK_RE = re.compile(r"ALWAYS open and follow `([^`]+)`")


def _extract_cypilot_follow_target(content: str) -> Optional[str]:
    """Return the follow-link target if *content* is a Cypilot-generated routing file.

    Returns the target path string when the content contains
    ``ALWAYS open and follow `<target>``` with a Cypilot-owned target
    (must start with ``{cypilot_path}/``).  Returns ``None`` otherwise.

    Note: ``@/`` (project-relative) paths are NOT accepted because any
    tool can use that prefix — it is not Cypilot-specific.
    """
    m = _FOLLOW_LINK_RE.search(content)
    if not m:
        return None
    target = m.group(1)
    if target.startswith("{cypilot_path}/"):
        return target
    return None


def _is_pure_cypilot_generated(
    content: str,
    *,
    expected_name: Optional[str] = None,
    expected_description: Optional[str] = None,
) -> bool:
    """Return True only if *content* is a pure Cypilot-generated stub with no user content.

    A pure generated file consists of optional YAML frontmatter, optional
    blank lines, and the ``ALWAYS open and follow`` directive — nothing else.
    Files that contain a Cypilot follow-link *plus* additional user-authored
    content are **not** considered pure generated and must be preserved.

    Frontmatter is compared against the canonical generated shape: Cypilot
    stubs only ever write ``name`` and ``description``.  Any extra key
    indicates user customisation, so the file is not treated as pure.
    When *expected_name* or *expected_description* are provided the corresponding
    frontmatter values must match exactly; a mismatch means the user edited them.
    """
    if not _extract_cypilot_follow_target(content):
        return False
    # Extract and validate YAML frontmatter when present
    stripped = content
    if stripped.startswith("---"):
        end = stripped.find("\n---", 3)
        if end != -1:
            fm_block = stripped[3:end]
            fm: Dict[str, str] = {}
            for line in fm_block.splitlines():
                if ":" in line:
                    key, _, val = line.partition(":")
                    key = key.strip()
                    if key:
                        fm[key] = _strip_wrapping_yaml_quotes(val.strip())
            # Canonical generated frontmatter only uses name and description.
            # Any extra key means the frontmatter was customised by the user.
            if not set(fm.keys()).issubset({"name", "description"}):
                return False
            # Check that the caller-supplied expected values match the file.
            if expected_name is not None and fm.get("name") != expected_name:
                return False
            if expected_description is not None and fm.get("description") != expected_description:
                return False
            stripped = stripped[end + 4:]  # skip past closing ---
    # Remove all follow-link lines
    lines = [
        line for line in stripped.splitlines()
        if not _FOLLOW_LINK_RE.search(line)
    ]
    # If only whitespace remains, the file is purely generated
    return not any(line.strip() for line in lines)


def _file_has_cypilot_follow_link(path: Path) -> bool:
    """Return True when *path* exists and contains a Cypilot follow-link."""
    try:
        return bool(_extract_cypilot_follow_target(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeDecodeError):
        return False


_VALID_AGENT_MODES = {"readwrite", "readonly"}
_KNOWN_AGENT_MODELS = {"inherit", "fast"}


def _validate_agent_entry(
    name: str,
    info: Dict[str, Any],
    source_dir: Path,
    seen_names: Set[str],
) -> Optional[Dict[str, Any]]:
    """Validate and build one agent entry dict; return None to skip."""
    if not isinstance(info, dict):
        return None
    if name in seen_names:
        return None
    if "/" in name or "\\" in name or ".." in name:
        sys.stderr.write(f"WARNING: skipping agent with unsafe name: {name!r}\n")
        return None
    prompt_rel = info.get("prompt_file", "")
    prompt_abs = None
    if prompt_rel:
        if not isinstance(prompt_rel, str):
            sys.stderr.write(
                f"WARNING: agent {name!r} prompt_file must be a string, got {type(prompt_rel).__name__!r}, skipping\n"
            )
            return None
        candidate = (source_dir / prompt_rel).resolve()
        try:
            candidate.relative_to(source_dir.resolve())
        except ValueError:
            sys.stderr.write(
                f"WARNING: agent {name!r} prompt_file escapes source dir, skipping\n"
            )
            return None
        if not candidate.is_file():
            sys.stderr.write(
                f"WARNING: agent {name!r} prompt_file not found: {candidate}, skipping\n"
            )
            return None
        prompt_abs = candidate
    mode = info.get("mode", "readwrite")
    model = info.get("model", "inherit")
    if mode not in _VALID_AGENT_MODES:
        sys.stderr.write(f"WARNING: agent {name!r} has invalid mode {mode!r}, skipping\n")
        return None
    if model not in _KNOWN_AGENT_MODELS:
        sys.stderr.write(f"WARNING: agent {name!r} has unknown model {model!r}, using as passthrough\n")
    return {
        "name": name,
        "description": info.get("description", f"Cypilot {name} subagent"),
        "prompt_file_abs": prompt_abs,
        "mode": mode,
        "isolation": bool(info.get("isolation", False)),
        "model": model,
        "source_dir": source_dir,
    }
# @cpt-end:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-agents-datamodel

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
    except OSError as exc:
        return cypilot_root, {"action": "error", "message": str(exc)}
# @cpt-end:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-ensure-local-copy

# @cpt-begin:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-write-helpers
def _load_json_file(path: Path) -> Optional[dict]:
    if not path.is_file():
        return None
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, OSError, IOError, UnicodeDecodeError):
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
    except ValueError as exc:
        raise ValueError(
            f"Output path '{out_path}' escapes project root '{project_root}' — "
            "path traversal is not allowed"
        ) from exc
    rel = _safe_relpath(canonical, project_root)
    if not canonical.exists():
        result["created"].append(canonical.as_posix())
        if not dry_run:
            canonical.parent.mkdir(parents=True, exist_ok=True)
            canonical.write_text(content, encoding="utf-8")  # NOSONAR
        result["outputs"].append({"path": rel, "action": "created"})
    else:
        try:
            old = out_path.read_text(encoding="utf-8")
        except OSError:
            old = ""
        if old != content:
            result["updated"].append(canonical.as_posix())
            if not dry_run:
                canonical.write_text(content, encoding="utf-8")  # NOSONAR
            result["outputs"].append({"path": rel, "action": "updated"})
        else:
            result["outputs"].append({"path": rel, "action": "unchanged"})
# @cpt-end:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-write-helpers

# @cpt-begin:cpt-cypilot-algo-agent-integration-discover-agents:p1:inst-resolve-kits
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
        except (OSError, tomllib.TOMLDecodeError) as exc:
            sys.stderr.write(f"WARNING: failed to parse {toml_path}: {exc}\n")
            return
        agents_section = data.get("agents")
        if not isinstance(agents_section, dict):
            return
        for name, info in agents_section.items():
            entry = _validate_agent_entry(name, info, source_dir, seen_names)
            if entry is None:
                continue
            seen_names.add(name)
            out.append(entry)

    # 1. Installed kits — agents defined by kit packages
    config_kits = _resolve_config_kits(cypilot_root, project_root)
    if config_kits.is_dir():
        registered = _registered_kit_dirs(project_root)
        registered_dirs: Set[str] = registered if isinstance(registered, set) else set()
        try:
            kit_dirs = sorted(config_kits.iterdir())
        except OSError:
            kit_dirs = []
        for kit_dir in kit_dirs:
            if not kit_dir.is_dir():
                continue
            if registered_dirs and kit_dir.name not in registered_dirs:
                continue
            _load_agents_toml(kit_dir / "agents.toml", kit_dir)

    # 2. Core skill area — fallback for agents not already defined by kits
    core_skill = core_subpath(cypilot_root, "skills", "cypilot")
    _load_agents_toml(core_skill / "agents.toml", core_skill)

    return out
# @cpt-end:cpt-cypilot-algo-agent-integration-discover-agents:p1:inst-resolve-kits


# @cpt-begin:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-create-proxy-templates
# ── Per-tool subagent template mapping ──────────────────────────────
#
# These functions map semantic agent capabilities (mode, isolation, model)
# to tool-specific YAML frontmatter lines.  Tool knowledge stays here;
# kit knowledge stays in agents.toml.

def _agent_template_claude(agent: Dict[str, Any]) -> List[str]:
    """Build Claude Code agent proxy template lines."""
    lines = list(_AGENT_TEMPLATE_HEADER)
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
    lines = list(_AGENT_TEMPLATE_HEADER)
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
    lines = list(_AGENT_TEMPLATE_HEADER)
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
        "filename_format": "{name}.toml",
    },
}


def _render_toml_agent(agent: Dict[str, Any], target_agent_path: str) -> str:
    """Render a single OpenAI Codex TOML agent role file.

    Each agent becomes its own ``.toml`` file with top-level ``name``,
    ``description``, and ``developer_instructions`` — the fields required
    by the Codex CLI agent-role schema.
    """
    name = agent["name"]
    raw_desc = agent.get("description", "")
    if not isinstance(raw_desc, str):
        raw_desc = str(raw_desc) if raw_desc is not None else ""
    desc = " ".join(raw_desc.split())
    desc_escaped = _escape_toml_basic_string(desc)
    safe_path = _escape_toml_multiline_string(target_agent_path)
    prompt = f"ALWAYS open and follow `{safe_path}`"
    lines: List[str] = [
        f'name = "{_escape_toml_basic_string(name)}"',
        f'description = "{desc_escaped}"',
        'developer_instructions = """',
        prompt,
        '"""',
    ]
    return "\n".join(lines) + "\n"
# @cpt-end:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-create-proxy-templates


# @cpt-begin:cpt-cypilot-algo-agent-integration-discover-agents:p1:inst-define-registry
def _agents_skill_outputs() -> list:
    """Shared .agents/skills/ outputs for all non-Claude tools.

    These templates are tool-agnostic — no ``{custom_content}`` because the
    same file is written identically regardless of which tool triggers it.
    """
    _AGENTS_SKILL_TEMPLATE = [
        "---",
        "name: {name}",
        _TMPL_DESCRIPTION,
        "---",
        "",
        "ALWAYS open and follow `{target_skill_path}`",
    ]
    _AGENTS_WORKFLOW_SKILL_TEMPLATE = [
        "---",
        "name: {name}",
        _TMPL_DESCRIPTION,
        "---",
        "",
        _ALWAYS_FOLLOW_TARGET_PATH,
    ]
    return [
        {
            "path": ".agents/skills/cypilot/SKILL.md",
            "template": list(_AGENTS_SKILL_TEMPLATE),
        },
        {
            "path": ".agents/skills/cypilot-generate/SKILL.md",
            "target": "workflows/generate.md",
            "template": list(_AGENTS_WORKFLOW_SKILL_TEMPLATE),
        },
        {
            "path": ".agents/skills/cypilot-analyze/SKILL.md",
            "target": "workflows/analyze.md",
            "template": list(_AGENTS_WORKFLOW_SKILL_TEMPLATE),
        },
        {
            "path": ".agents/skills/cypilot-plan/SKILL.md",
            "target": "workflows/plan.md",
            "template": list(_AGENTS_WORKFLOW_SKILL_TEMPLATE),
        },
        {
            "path": ".agents/skills/cypilot-workspace/SKILL.md",
            "target": "workflows/workspace.md",
            "template": list(_AGENTS_WORKFLOW_SKILL_TEMPLATE),
        },
    ]


def _default_agents_config() -> dict:
    """Unified config for both workflows and skills registration per agent.

    Skill outputs use two conventions:
    - Claude  → ``.claude/skills/`` (Claude-native with allowed-tools, user-invocable)
    - Others  → ``.agents/skills/`` (shared directory readable by all tools)

    Workflow outputs remain tool-specific (slash commands need per-tool dirs).
    """
    shared_skills = _agents_skill_outputs()
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
                    "outputs": shared_skills + [
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
                    "outputs": shared_skills + [
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
                                _TMPL_DESCRIPTION,
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
                                _TMPL_DESCRIPTION,
                                "disable-model-invocation: false",
                                "user-invocable: true",
                                "allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task",
                                "---",
                                "",
                                _ALWAYS_FOLLOW_TARGET_PATH,
                            ],
                        },
                        {
                            "path": ".claude/skills/cypilot-analyze/SKILL.md",
                            "target": "workflows/analyze.md",
                            "template": [
                                "---",
                                "name: cypilot-analyze",
                                _TMPL_DESCRIPTION,
                                "disable-model-invocation: false",
                                "user-invocable: true",
                                "allowed-tools: Bash, Read, Glob, Grep",
                                "---",
                                "",
                                _ALWAYS_FOLLOW_TARGET_PATH,
                            ],
                        },
                        {
                            "path": ".claude/skills/cypilot-plan/SKILL.md",
                            "target": "workflows/plan.md",
                            "template": [
                                "---",
                                "name: cypilot-plan",
                                _TMPL_DESCRIPTION,
                                "disable-model-invocation: false",
                                "user-invocable: true",
                                "allowed-tools: Bash, Read, Write, Edit, Glob, Grep",
                                "---",
                                "",
                                _ALWAYS_FOLLOW_TARGET_PATH,
                            ],
                        },
                        {
                            "path": ".claude/skills/cypilot-workspace/SKILL.md",
                            "target": "workflows/workspace.md",
                            "template": [
                                "---",
                                "name: cypilot-workspace",
                                _TMPL_DESCRIPTION,
                                "disable-model-invocation: false",
                                "user-invocable: true",
                                "allowed-tools: Bash, Read, Write, Edit, Glob, Grep",
                                "---",
                                "",
                                _ALWAYS_FOLLOW_TARGET_PATH,
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
                        _TMPL_NAME,
                        _TMPL_DESCRIPTION,
                        "---",
                        "",
                        "{custom_content}",
                        "ALWAYS open and follow `{target_workflow_path}`",
                    ],
                },
                "skills": {
                    "custom_content": "",
                    "outputs": shared_skills + [
                        {
                            "path": ".github/copilot-instructions.md",
                            "template": [
                                "# Cypilot",
                                "",
                                "{custom_content}",
                            ],
                        },
                        {
                            "path": ".github/prompts/cypilot.prompt.md",
                            "template": [
                                "---",
                                _TMPL_NAME,
                                _TMPL_DESCRIPTION,
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
                    "outputs": list(shared_skills),
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
    except OSError:
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
            inner = inner.replace("\\\\", "\\")
            inner = inner.replace('\\"', '"')
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
            raise SystemExit(f"Missing template variable: {e}") from e
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
    match = _FOLLOW_LINK_RE.search(stripped)
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
                except OSError:
                    continue
                if "type: workflow" not in head:
                    continue
                if p.name not in seen_names:
                    seen_names.add(p.name)
                    out.append((p.name, p.resolve()))
        except OSError:
            pass

    # 1. Core workflows
    _scan_dir(core_subpath(cypilot_root, "workflows"))

    # 2. Kit workflows (config/kits/*/workflows/)
    registered = _registered_kit_dirs(project_root)
    registered_dirs: Set[str] = registered if isinstance(registered, set) else set()
    config_kits = _resolve_config_kits(cypilot_root, project_root)
    if config_kits.is_dir():
        try:
            for kit_dir in sorted(config_kits.iterdir()):
                if registered_dirs and kit_dir.name not in registered_dirs:
                    continue
                _scan_dir(kit_dir / "workflows")
        except OSError:
            pass

    out.sort(key=lambda t: t[0])
    return out
# @cpt-end:cpt-cypilot-algo-agent-integration-list-workflows:p1:inst-scan-core-workflows

# ---------------------------------------------------------------------------
# Kit workflow → skill generation for skill-native tools
# ---------------------------------------------------------------------------
# Tools that fully support user-invocable skills do NOT need legacy slash-
# command/workflow files.  Instead, discovered kit workflows are emitted as
# proper skill entries so they appear in the tool's skill list (e.g.
# /cypilot-pr-review in Claude Code) without a separate .claude/commands/ file.

_KIT_WORKFLOW_SKILL_PATHS: Dict[str, str] = {
    "claude": ".claude/skills/{skill_id}/SKILL.md",
    # All non-Claude tools share .agents/skills/
    "openai": ".agents/skills/{skill_id}/SKILL.md",
    "windsurf": ".agents/skills/{skill_id}/SKILL.md",
    "cursor": ".agents/skills/{skill_id}/SKILL.md",
    "copilot": ".agents/skills/{skill_id}/SKILL.md",
}

_AGENTS_KIT_WORKFLOW_TEMPLATE: List[str] = [
    "---",
    "name: {name}",
    _TMPL_DESCRIPTION,
    "---",
    "",
    _ALWAYS_FOLLOW_TARGET_PATH,
]

_KIT_WORKFLOW_SKILL_TEMPLATES: Dict[str, List[str]] = {
    "claude": [
        "---",
        "name: {name}",
        _TMPL_DESCRIPTION,
        "disable-model-invocation: false",
        "user-invocable: true",
        "allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch",
        "---",
        "",
        _ALWAYS_FOLLOW_TARGET_PATH,
    ],
    "openai": _AGENTS_KIT_WORKFLOW_TEMPLATE,
    "windsurf": _AGENTS_KIT_WORKFLOW_TEMPLATE,
    "cursor": _AGENTS_KIT_WORKFLOW_TEMPLATE,
    "copilot": _AGENTS_KIT_WORKFLOW_TEMPLATE,
}


def _generate_kit_workflow_skills(
    agent: str,
    project_root: Path,
    cypilot_root: Path,
    skill_output_paths: Set[str],
    skills_result: Dict[str, Any],
    dry_run: bool,
    kit_workflows: Optional[List[Tuple[str, str]]] = None,
) -> None:
    """Emit skill entries for kit workflows on skill-native tools.

    For tools that have no ``workflows`` config (i.e. they fully support
    user-invocable skills), discovered kit workflows are generated as
    skill files instead of legacy slash-command proxies.
    """
    path_pattern = _KIT_WORKFLOW_SKILL_PATHS.get(agent)
    template = _KIT_WORKFLOW_SKILL_TEMPLATES.get(agent)
    if not path_pattern or not template:
        return

    if kit_workflows is None:
        kit_workflows = _list_workflow_files(cypilot_root, project_root)

    for wf_filename, wf_full_path in kit_workflows:
        wf_name = Path(wf_filename).stem
        skill_id = f"cypilot-{wf_name}" if wf_name != "cypilot" else "cypilot"

        out_rel = path_pattern.format(skill_id=skill_id)
        out_path = (project_root / out_rel).resolve()

        # Skip if already covered by a hardcoded skill output
        if out_path.as_posix() in skill_output_paths:
            continue

        fm = _parse_frontmatter(wf_full_path)
        target_rel = _target_path_from_root(wf_full_path, project_root, cypilot_root)
        name = fm.get("name", skill_id)
        description = fm.get("description", f"Cypilot {wf_name} workflow")

        content = _render_template(
            template,
            {"name": name, "description": description, "target_path": target_rel},
        )

        _write_or_skip(out_path, content, skills_result, project_root, dry_run)


# @cpt-begin:cpt-cypilot-algo-agent-integration-discover-agents:p1:inst-define-registry-const
_ALL_RECOGNIZED_AGENTS = ["windsurf", "cursor", "claude", "copilot", "openai"]
# @cpt-end:cpt-cypilot-algo-agent-integration-discover-agents:p1:inst-define-registry-const

# Per-tool Cypilot-specific generated files — used to detect which agents
# are actually installed.  We check for specific Cypilot-generated files
# rather than generic tool directories to avoid false positives when
# unrelated tool files exist (e.g. .cursor/commands/other.md).
_AGENT_MARKERS: Dict[str, List[str]] = {
    "claude":   [".claude/skills/cypilot/SKILL.md"],
    "windsurf": [".windsurf/workflows/cypilot.md"],
    "cursor":   [".cursor/commands/cypilot.md"],
    "copilot":  [".github/.cypilot-installed"],
    # Fresh OpenAI installs create .codex/.cypilot-installed.
    # Legacy fallback handled by _is_agent_installed().
    "openai":   [".codex/.cypilot-installed"],
}

# Non-OpenAI tool markers — used to disambiguate the shared
# .agents/skills/ directory for legacy OpenAI detection.
_NON_OPENAI_MARKERS = [
    m for agent, ms in _AGENT_MARKERS.items()
    if agent != "openai" for m in ms
]


def _has_non_openai_install_signal(project_root: Path) -> bool:
    """Return True when any non-OpenAI Cypilot install marker or legacy fallback exists."""
    if any((project_root / m).is_file() for m in _NON_OPENAI_MARKERS):
        return True

    if _file_has_cypilot_follow_link(project_root / ".windsurf" / "skills" / "cypilot" / "SKILL.md"):
        return True

    if _file_has_cypilot_follow_link(project_root / ".cursor" / "rules" / "cypilot.mdc"):
        return True

    legacy_ci = project_root / ".github" / "copilot-instructions.md"
    if legacy_ci.is_file():
        try:
            if legacy_ci.read_text(encoding="utf-8").startswith("# Cypilot"):
                return True
        except (OSError, UnicodeDecodeError):
            pass

    return (project_root / ".github" / "prompts" / "cypilot.prompt.md").is_file()


def _is_agent_installed(agent: str, project_root: Path) -> bool:
    """Return True when *agent* has a Cypilot install detected under *project_root*.

    Checks primary markers first, then legacy fallbacks per agent.
    """
    markers = _AGENT_MARKERS.get(agent, [])
    if any((project_root / m).is_file() for m in markers):
        return True

    # ── Legacy Windsurf fallback ──────────────────────────────────────────
    # Pre-shared-agents installs used .windsurf/skills/cypilot/SKILL.md.
    if agent == "windsurf":
        legacy = project_root / ".windsurf" / "skills" / "cypilot" / "SKILL.md"
        if _file_has_cypilot_follow_link(legacy):
            return True

    # ── Legacy Cursor fallback ────────────────────────────────────────────
    # Pre-shared-agents installs used .cursor/rules/cypilot.mdc.
    if agent == "cursor":
        legacy = project_root / ".cursor" / "rules" / "cypilot.mdc"
        if _file_has_cypilot_follow_link(legacy):
            return True

    # ── Legacy Copilot fallback ───────────────────────────────────────────
    # A Cypilot-managed copilot-instructions.md (starts with "# Cypilot")
    # is a valid signal from pre-marker installs.  Also detect via
    # .github/prompts/cypilot.prompt.md for installs where the instructions
    # file was user-authored but other Copilot outputs were generated.
    if agent == "copilot":
        legacy_ci = project_root / ".github" / "copilot-instructions.md"
        if legacy_ci.is_file():
            try:
                if legacy_ci.read_text(encoding="utf-8").startswith("# Cypilot"):
                    return True
            except (OSError, UnicodeDecodeError):
                pass
        prompt_file = project_root / ".github" / "prompts" / "cypilot.prompt.md"
        if prompt_file.is_file():
            return True

    # ── Legacy OpenAI fallback ────────────────────────────────────────────
    # Detect via Cypilot-specific artifacts inside .codex/ (agents/*.toml
    # with follow-link) or via shared .agents/skills/cypilot/SKILL.md when
    # no other tool's marker is present.
    if agent == "openai":
        codex_agents = project_root / ".codex" / "agents"
        if codex_agents.is_dir():
            for f in codex_agents.iterdir():
                if f.is_file():
                    try:
                        if _extract_cypilot_follow_target(f.read_text(encoding="utf-8")):
                            return True
                    except (OSError, UnicodeDecodeError):
                        pass
        shared_skill = project_root / ".agents" / "skills" / "cypilot" / "SKILL.md"
        if shared_skill.is_file():
            if not _has_non_openai_install_signal(project_root):
                return True

    return False


# Legacy tool-specific skill paths replaced by shared .agents/skills/
_LEGACY_TOOL_SKILL_PATHS: Dict[str, List[str]] = {
    "windsurf": [".windsurf/skills/cypilot/SKILL.md"],
    "cursor": [".cursor/rules/cypilot.mdc"],
}

# Cypilot installation markers for agents that share generic directories
_INSTALL_MARKERS: Dict[str, Tuple[str, str]] = {
    "openai":  (".codex/.cypilot-installed", "# Cypilot OpenAI/Codex integration marker\n"),
    "copilot": (".github/.cypilot-installed", "# Cypilot Copilot integration marker\n"),
}

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
                    except OSError:
                        continue
                    if not head.lstrip().startswith("# /"):
                        continue
                try:
                    txt = pth.read_text(encoding="utf-8")
                except OSError:
                    continue
                if "ALWAYS open and follow `" not in txt:
                    continue
                m = _FOLLOW_LINK_RE.search(txt)
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
                except OSError:
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
                except OSError:
                    continue
                m = _FOLLOW_LINK_RE.search(txt)
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
                registered_dirs: Set[str] = registered if isinstance(registered, set) else set()
                config_kits = _resolve_config_kits(cypilot_root, project_root)
                if config_kits.is_dir():
                    kit_descs: List[str] = []
                    try:
                        for kit_dir in sorted(config_kits.iterdir()):
                            if registered_dirs and kit_dir.name not in registered_dirs:
                                continue
                            kit_skill = kit_dir / "SKILL.md"
                            if kit_skill.is_file():
                                kit_fm = _parse_frontmatter(kit_skill)
                                kit_desc = kit_fm.get("description", "")
                                if kit_desc:
                                    kit_descs.append(f"Kit {kit_dir.name}: {kit_desc}")
                    except OSError:
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

                    # Guard: skip overwriting user-authored copilot-instructions.md.
                    # The file is only Cypilot-managed when it starts with "# Cypilot".
                    if rel_path == ".github/copilot-instructions.md" and out_path.is_file():
                        try:
                            existing = out_path.read_text(encoding="utf-8")
                        except OSError:
                            existing = ""
                        if not existing.startswith("# Cypilot"):
                            rel = _safe_relpath(out_path.resolve(), project_root)
                            skills_result["skipped"].append(
                                f"{rel} (user-authored, not overwriting)"
                            )
                            skills_result["_copilot_user_authored"] = True
                            continue

                    _write_or_skip(out_path, content, skills_result, project_root, dry_run)

    # ── Kit workflows → shared skills ──────────────────────────────────────
    # Always generate .agents/skills/ entries for kit workflows so that every
    # non-Claude agent has accessible shared skill files, regardless of whether
    # a separate workflows_cfg produces tool-native proxy files.
    _cached_kit_workflows = _list_workflow_files(cypilot_root, project_root)
    _generate_kit_workflow_skills(
        agent, project_root, cypilot_root, skill_output_paths,
        skills_result, dry_run,
        kit_workflows=_cached_kit_workflows,
    )

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

    # ── Clean up legacy commands for kit workflows now emitted as skills ──
    if agent == "claude" and _cached_kit_workflows is not None:
        legacy_commands_dir = project_root / ".claude" / "commands"
        if legacy_commands_dir.is_dir():
            for wf_filename, wf_full_path in _cached_kit_workflows:
                wf_name = Path(wf_filename).stem
                cmd_name = f"cypilot-{wf_name}" if wf_name != "cypilot" else "cypilot"
                legacy_file = legacy_commands_dir / f"{cmd_name}.md"
                if not legacy_file.is_file():
                    continue
                rel_path = legacy_file.relative_to(project_root).as_posix()
                try:
                    content = legacy_file.read_text(encoding="utf-8")
                except OSError:
                    continue
                # Only delete if provably Cypilot-generated (no user content) and targeting THIS workflow
                follow_target = _extract_cypilot_follow_target(content)
                if not follow_target or "workflows/" not in follow_target:
                    continue
                if Path(follow_target).name != wf_filename:
                    continue
                if not _is_pure_cypilot_generated(content, expected_name=cmd_name):
                    continue
                if not dry_run:
                    try:
                        legacy_file.unlink()
                        skills_result["deleted"].append(rel_path)
                    except OSError:
                        skills_result["errors"].append(f"failed to delete {rel_path}")
                else:
                    skills_result["deleted"].append(rel_path)

    # ── Clean up legacy tool-specific skill files now replaced by .agents/skills/ ──
    for legacy_rel in _LEGACY_TOOL_SKILL_PATHS.get(agent, []):
        legacy_file = project_root / legacy_rel
        if not legacy_file.is_file():
            continue
        try:
            content = legacy_file.read_text(encoding="utf-8")
        except OSError:
            continue
        # Only delete if provably Cypilot-generated (no user content beyond the stub).
        # Derive the canonical skill name: parent dir for SKILL.md, stem otherwise.
        _lp = Path(legacy_rel)
        _legacy_skill_name = _lp.parent.name if _lp.name == "SKILL.md" else _lp.stem
        if not _is_pure_cypilot_generated(content, expected_name=_legacy_skill_name):
            continue
        rel_path = legacy_rel
        if not dry_run:
            try:
                legacy_file.unlink()
                skills_result["deleted"].append(rel_path)
            except OSError:
                skills_result["errors"].append(f"failed to delete {rel_path}")
        else:
            skills_result["deleted"].append(rel_path)

    # ── Install markers ───────────────────────────────────────────────────
    # Tools that share generic directories need a unique Cypilot-specific
    # marker so detection/regeneration can distinguish Cypilot installs from
    # unrelated user files.  The marker is always created when the agent is
    # processed — even if copilot-instructions.md was preserved as user-
    # authored, the other generated outputs (prompts, shared skills, agents)
    # still need to be managed by future `cpt update` runs.
    marker_info = _INSTALL_MARKERS.get(agent)
    if marker_info and not dry_run:
        marker = project_root / marker_info[0]
        marker.parent.mkdir(parents=True, exist_ok=True)
        if not marker.exists():
            marker.write_text(marker_info[1], encoding="utf-8")

    # ── Subagent generation ────────────────────────────────────────────
    subagents_result: Dict[str, Any] = {"created": [], "updated": [], "deleted": [], "skipped": False, "outputs": [], "errors": []}

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
            # Render one TOML file per agent (Codex CLI expects top-level fields per file)
            for ka in kit_agents:
                name = ka["name"]
                agent_path = target_agent_paths.get(name, "")
                if not agent_path:
                    sys.stderr.write(
                        f"WARNING: agent {name!r} has no resolved prompt target, skipping subagent proxy\n"
                    )
                    subagents_result["skipped"] = True
                    subagents_result["skip_reason"] = subagents_result.get("skip_reason", "") or "one or more agents missing prompt target"
                    continue
                toml_path = (output_dir / f"{name}.toml").resolve()
                content = _render_toml_agent(ka, agent_path)
                _write_or_skip(toml_path, content, subagents_result, project_root, dry_run)
            # Clean up stale TOML files: legacy combined file and renamed/removed agents
            desired_toml_names = {f"{ka['name']}.toml" for ka in kit_agents if target_agent_paths.get(ka["name"])}
            if output_dir.is_dir():
                try:
                    for toml_file in output_dir.glob("cypilot*.toml"):
                        if toml_file.name in desired_toml_names:
                            continue
                        rel = _safe_relpath(toml_file, project_root)
                        subagents_result["outputs"].append({"path": rel, "action": "deleted"})
                        if not dry_run:
                            try:
                                toml_file.unlink()
                            except OSError:
                                pass
                except OSError:
                    pass
        else:
            # Markdown + YAML frontmatter (claude, cursor, copilot)
            template_fn = tool_cfg.get("template_fn")
            if template_fn is None:
                subagents_result["errors"].append(f"No template function for {agent}")
            else:
                for ka in kit_agents:
                    name = ka["name"]
                    target_agent_rel = target_agent_paths.get(name, "")
                    if not target_agent_rel:
                        sys.stderr.write(
                            f"WARNING: agent {name!r} has no resolved prompt target, skipping subagent proxy\n"
                        )
                        subagents_result["skipped"] = True
                        subagents_result["skip_reason"] = subagents_result.get("skip_reason", "") or "one or more agents missing prompt target"
                        continue
                    template = template_fn(ka)

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
            "deleted": subagents_result["deleted"],
            "skipped": subagents_result["skipped"],
            "skip_reason": subagents_result.get("skip_reason", ""),
            "outputs": subagents_result["outputs"],
            "counts": {
                "created": len(subagents_result["created"]),
                "updated": len(subagents_result["updated"]),
                "deleted": len(subagents_result["deleted"]),
            },
        },
        "errors": all_errors if all_errors else None,
    }
# @cpt-end:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-create-proxy

# @cpt-begin:cpt-cypilot-algo-agent-integration-discover-agents:p1:inst-resolve-context-helper
def _find_cypilot_root_from_file() -> Path:
    """Probe __file__ ancestry at levels 5/6/7 for a valid cypilot root; fall back to deepest available."""
    resolved_file = Path(__file__).resolve()
    max_index = len(resolved_file.parents) - 1
    for _level in (5, 6, 7):
        if _level > max_index:
            continue
        _candidate = resolved_file.parents[_level]
        if _is_cypilot_root(_candidate):
            return _candidate
    return resolved_file.parents[min(5, max_index)]
# @cpt-end:cpt-cypilot-algo-agent-integration-discover-agents:p1:inst-resolve-context-helper


# @cpt-begin:cpt-cypilot-algo-agent-integration-discover-agents:p1:inst-resolve-context
def _resolve_cypilot_root(args: argparse.Namespace, project_root: Path) -> Optional[Path]:
    """Discover the Cypilot root directory from CLI args or project convention."""
    cypilot_root = Path(args.cypilot_root).resolve() if args.cypilot_root else None
    if cypilot_root is None:
        cypilot_rel = _read_cypilot_var(project_root)
        if cypilot_rel:
            candidate = (project_root / cypilot_rel).resolve()
            if _is_cypilot_root(candidate):
                cypilot_root = candidate
        if cypilot_root is None:
            cypilot_root = _find_cypilot_root_from_file()
    return cypilot_root


def _load_agents_cfg(
    args: argparse.Namespace,
    agents_to_process: List[str],
) -> Optional[Tuple[Optional[Path], dict]]:
    """Load or build the agents config.  Returns ``(cfg_path, cfg)`` or *None* on error."""
    cfg_path: Optional[Path] = Path(args.config).resolve() if args.config else None
    if cfg_path is not None:
        cfg: Optional[dict] = _load_json_file(cfg_path)
        if cfg is None:
            _cfg_err = f"Cannot read or parse config file: {cfg_path}"
            ui.result(
                {"status": "CONFIG_ERROR", "message": _cfg_err, "config": cfg_path.as_posix()},
                human_fn=lambda d: (
                    ui.error(_cfg_err),
                    ui.hint("Ensure the file exists and contains a valid JSON object."),
                    ui.blank(),
                ),
            )
            return None
    else:
        cfg = None

    any_recognized = any(a in set(_ALL_RECOGNIZED_AGENTS) for a in agents_to_process)
    if cfg is None:
        if any_recognized:
            cfg = _default_agents_config()
        else:
            cfg = {"version": 1, "agents": {a: {"workflows": {}, "skills": {}} for a in agents_to_process}}

    return cfg_path, cfg


def _resolve_agents_context(argv: List[str], prog: str, description: str, *, allow_yes: bool = False, read_only: bool = False) -> Optional[tuple]:
    """Shared argument parsing and project resolution for agents commands.

    When ``read_only=True``, this helper skips ``_ensure_cypilot_local`` so no
    file copying or local-state mutation occurs. Use ``read_only`` for safe
    list/inspection commands that should not modify project-local Cypilot files.

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

    cypilot_root = _resolve_cypilot_root(args, project_root)

    if read_only:
        copy_report: dict = {"action": "none"}
    else:
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

    cfg_result = _load_agents_cfg(args, agents_to_process)
    if cfg_result is None:
        return None
    cfg_path, cfg = cfg_result

    return args, agents_to_process, project_root, cypilot_root, copy_report, cfg_path, cfg
# @cpt-end:cpt-cypilot-algo-agent-integration-discover-agents:p1:inst-resolve-context

# @cpt-begin:cpt-cypilot-algo-agent-integration-generate-shims:p1:inst-cmd-agents-list
def cmd_agents(argv: List[str]) -> int:
    """Read-only command: list generated agent integration files."""
    ctx = _resolve_agents_context(argv, prog="agents", description="Show generated agent integration files", read_only=True)
    if ctx is None:
        return 1
    _args, agents_to_process, project_root, cypilot_root, _copy_report, cfg_path, cfg = ctx

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

# @cpt-begin:cpt-cypilot-flow-agent-integration-generate:p1:inst-user-agents-entry

# @cpt-begin:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-step3-5-resolve-includes
def _resolve_includes_for_layers(layers: List, project_root: Path) -> Tuple[List, bool]:
    """Resolve ``includes`` for each layer manifest.

    Returns ``(resolved_layers, has_errors)``.  Errors are logged to stderr;
    no exceptions are raised.
    """
    import dataclasses as _dc
    has_v2_errors = False
    resolved_layers = []
    for layer in layers:
        if (
            layer.state == _ManifestLayerState.LOADED
            and layer.manifest is not None
            and layer.manifest.includes
        ):
            try:
                # Repo-scoped manifests live inside the adapter dir but may
                # legitimately include files from anywhere within the project
                # (e.g. ../../tools/standctl/manifest.toml).  Use project_root
                # as trusted root for repo layers; other scopes use the
                # manifest's own directory.
                if layer.scope == "repo":
                    trusted = project_root.resolve()
                else:
                    trusted = layer.path.parent.resolve()
                resolved_manifest = _resolve_includes(
                    layer.manifest, layer.path.parent, trusted_root=trusted
                )
                resolved_layer = _dc.replace(layer, manifest=resolved_manifest)
                resolved_layers.append(resolved_layer)
            except ValueError as exc:
                sys.stderr.write(f"ERROR: failed to resolve includes for {layer.path}: {exc}\n")
                has_v2_errors = True
                resolved_layers.append(layer)
        else:
            resolved_layers.append(layer)
    return resolved_layers, has_v2_errors
# @cpt-end:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-step3-5-resolve-includes


# @cpt-begin:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-discover-flag
def _run_discover_flag(args: Any, project_root: Path, cypilot_root: Path) -> None:
    """Run --discover: scan dirs and write new entries to manifest.toml."""
    discovered = discover_components(project_root)
    manifest_out = cypilot_root / "config" / "manifest.toml"
    if not args.dry_run:
        write_discovered_manifest(discovered, manifest_out)
        sys.stderr.write(f"INFO: wrote discovered manifest to {manifest_out}\n")
# @cpt-end:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-discover-flag


# @cpt-begin:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-show-layers-flag
def _handle_show_layers_v2(args: Any, merged: Any, project_root: Path) -> Optional[int]:
    """Handle --show-layers for the v2 manifest path.

    Returns ``0`` if --show-layers was handled, ``None`` otherwise.
    """
    if not getattr(args, "show_layers", False):
        return None
    report = build_provenance_report(merged, project_root)
    from ..utils.ui import is_json_mode
    if is_json_mode():
        ui.result({"status": "OK", "provenance": report})
    else:
        human_text = format_provenance_human(report)
        sys.stdout.write(human_text + "\n")
    return 0
# @cpt-end:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-show-layers-flag


# @cpt-begin:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-step7-translate
def _confirm_v2_generation(
    args: Any,
    preview_create: int,
    preview_update: int,
) -> bool:
    """Return True if generation should proceed, False if user aborted.

    Handles: dry_run short-circuit, no-changes case, JSON-mode bypass,
    --yes flag, and interactive prompt.
    """
    if args.dry_run:
        return False
    if preview_create == 0 and preview_update == 0:
        ui.info("No changes needed — agent files are up to date.")
        return False
    from ..utils.ui import is_json_mode
    if not is_json_mode():
        auto_approve = getattr(args, "yes", False)
        if not auto_approve:
            if not sys.stdin.isatty():
                return True  # non-interactive: proceed
            sys.stdout.write(
                f"Will create {preview_create} file(s), update {preview_update} file(s). Continue? [Y/n] "
            )
            sys.stdout.flush()
            answer = sys.stdin.readline().strip().lower()
            if answer and answer not in ("y", "yes"):
                ui.info("Aborted.")
                return False
    return True


def _run_v2_pipeline(
    args: Any,
    merged: Any,
    agents_to_process: List[str],
    project_root: Path,
    cypilot_root: Path,
    variables: Dict[str, str],
    cfg: Any,
    cfg_path: Optional[Path],
    _copy_report: dict,
    trusted_roots: Optional[List[Path]] = None,
) -> Tuple[Dict[str, Any], bool]:
    """Run generate_manifest_agents + generate_manifest_skills + legacy pipeline.

    Returns ``(results_dict, has_errors)``.
    """
    has_errors = False
    results: Dict[str, Any] = {}

    for target in agents_to_process:
        agents_r = generate_manifest_agents(
            merged.agents, target, project_root, args.dry_run, variables=variables, cypilot_root=cypilot_root, trusted_roots=trusted_roots,
        )
        skills_r = generate_manifest_skills(
            merged.skills, target, project_root, args.dry_run, variables=variables, cypilot_root=cypilot_root, trusted_roots=trusted_roots,
        )
        results[target] = {
            "status": "PASS",
            "agent": target,
            "manifest_v2": True,
            "translated_agents": len(merged.agents),
            "skills": skills_r,
            "v2_agents": agents_r,
            "workflows": {"created": [], "updated": [], "unchanged": [], "renamed": [], "deleted": [], "counts": {}},
        }

    for agent in agents_to_process:
        legacy_result = _process_single_agent(agent, project_root, cypilot_root, cfg, cfg_path, dry_run=args.dry_run)
        if agent in results:
            results[agent]["workflows"] = legacy_result.get("workflows", {})
            results[agent]["subagents"] = legacy_result.get("subagents", {})
            legacy_skills = legacy_result.get("skills", {})
            v2_skill_ids = {e.get("path", "") for e in results[agent].get("skills", {}).get("outputs", [])}
            if not any(agent in str(sk_path) for sk_path in v2_skill_ids):
                results[agent]["legacy_skills"] = legacy_skills
            if legacy_result.get("status") != "PASS":
                has_errors = True
        else:
            results[agent] = legacy_result
            if legacy_result.get("status") != "PASS":
                has_errors = True

    return results, has_errors
# @cpt-end:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-step7-translate


def cmd_generate_agents(argv: List[str]) -> int:
    """Generate/update agent-specific workflow proxies and skill outputs."""
    # @cpt-end:cpt-cypilot-flow-agent-integration-generate:p1:inst-user-agents-entry
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
        # Step 3: Resolve includes for each layer
        resolved_layers, has_v2_errors = _resolve_includes_for_layers(layers, project_root)
        if has_v2_errors:
            return 1

        # Step 4: Handle --discover flag
        if getattr(args, "discover", False):
            _run_discover_flag(args, project_root, cypilot_root)
            layers = _discover_layers(project_root, cypilot_root)
            resolved_layers, has_v2_errors = _resolve_includes_for_layers(layers, project_root)
            if has_v2_errors:
                return 1

        # Step 5: Merge components from all layers
        # @cpt-begin:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-step6-merge
        merged = _merge_components(resolved_layers)
        # @cpt-end:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-step6-merge

        # Collect trusted roots from discovered layer directories so that
        # master-layer source paths (rewritten to absolute) pass the
        # containment check in _read_source_content.
        _trusted_roots = [layer.path.parent for layer in resolved_layers if layer.state == _ManifestLayerState.LOADED]

        # Step 6: Handle --show-layers flag
        rc = _handle_show_layers_v2(args, merged, project_root)
        if rc is not None:
            return rc

        # Step 7: Extend variables with layer path variables
        # @cpt-begin:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-step9-layer-vars
        base_variables: Dict[str, str] = {
            "cypilot_path": cypilot_root.as_posix(),
            "project_root": project_root.as_posix(),
        }
        variables = _add_layer_variables(base_variables, resolved_layers, project_root)
        # @cpt-end:cpt-cypilot-flow-project-extensibility-generate-with-multi-layer:p1:inst-step9-layer-vars

        # Step 8: Preview pass — count ALL writes including legacy workflows
        preview_v2_create = 0
        preview_v2_update = 0
        preview_agents: Dict[str, Dict[str, Any]] = {}
        preview_skills: Dict[str, Dict[str, Any]] = {}
        legacy_preview: Dict[str, Any] = {}
        for target in agents_to_process:
            pr_a = generate_manifest_agents(merged.agents, target, project_root, dry_run=True, variables=variables, cypilot_root=cypilot_root, trusted_roots=_trusted_roots)
            pr_s = generate_manifest_skills(merged.skills, target, project_root, dry_run=True, variables=variables, cypilot_root=cypilot_root, trusted_roots=_trusted_roots)
            preview_agents[target] = pr_a
            preview_skills[target] = pr_s
            preview_v2_create += len(pr_a.get("created", [])) + len(pr_s.get("created", []))
            preview_v2_update += len(pr_a.get("updated", [])) + len(pr_s.get("updated", []))
            # Also preview legacy workflow outputs from _process_single_agent
            lp = _process_single_agent(target, project_root, cypilot_root, cfg, cfg_path, dry_run=True)
            legacy_preview[target] = lp
            for section in ("workflows", "skills", "subagents"):
                sec = lp.get(section, {})
                preview_v2_create += len(sec.get("created", []))
                preview_v2_update += len(sec.get("updated", [])) + len(sec.get("renamed", []))

        if args.dry_run:
            dry_results: Dict[str, Any] = {}
            for target in agents_to_process:
                lp = legacy_preview[target]
                dry_results[target] = {
                    "status": "PASS",
                    "agent": target,
                    "manifest_v2": True,
                    "translated_agents": len(merged.agents),
                    "skills": preview_skills[target],
                    "v2_agents": preview_agents[target],
                    "workflows": lp.get("workflows", {"created": [], "updated": [], "unchanged": [], "renamed": [], "deleted": [], "counts": {}}),
                    "subagents": lp.get("subagents", {}),
                    "legacy_skills": lp.get("skills", {}),
                }
            dr = _build_result(dry_results, agents_to_process, project_root, cypilot_root, cfg_path, copy_report, dry_run=True)
            dr["manifest_v2"] = True
            ui.result(dr, human_fn=lambda d: _human_generate_agents_ok(d, agents_to_process, dry_results, dry_run=True))
            return 0

        if not _confirm_v2_generation(args, preview_v2_create, preview_v2_update):
            return 0

        results, has_errors = _run_v2_pipeline(
            args, merged, agents_to_process, project_root, cypilot_root, variables, cfg, cfg_path, copy_report, trusted_roots=_trusted_roots,
        )
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
        _failing = {"PARTIAL", "CONFIG_ERROR"}
        if any(r.get("status") in _failing for r in preview_results.values()):
            return 1
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
    # @cpt-begin:cpt-cypilot-flow-agent-integration-generate:p1:inst-return-exit-code
    # @cpt-end:cpt-cypilot-dod-project-extensibility-backward-compat:p1:inst-legacy-path
    return 0 if not has_errors else 1
    # @cpt-end:cpt-cypilot-flow-agent-integration-generate:p1:inst-return-exit-code

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
    _data: Dict[str, Any],
    _agents_to_process: List[str],
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
    _project_root: Path,
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

def _render_agent_file_actions(
    wf: Dict[str, Any],
    sk: Dict[str, Any],
    sub: Dict[str, Any],
) -> None:
    """Emit ui.file_action calls for one agent's workflows, skills, and subagents."""
    for path in wf.get("created", []):
        ui.file_action(path, "created")
    for path in wf.get("updated", []):
        ui.file_action(path, "updated")
    for old_path, new_path in wf.get("renamed", []):
        ui.substep(f"workflow renamed: {old_path} -> {new_path}")
    for path in wf.get("deleted", []):
        ui.file_action(path, "deleted")
    for path in sk.get("created", []):
        ui.file_action(path, "created")
    for path in sk.get("updated", []):
        ui.file_action(path, "updated")
    for path in sk.get("deleted", []):
        ui.file_action(path, "deleted")
    for item in sk.get("skipped", []):
        ui.warn(f"  skipped: {item}")
    for path in sub.get("created", []):
        ui.file_action(path, "created")
    for path in sub.get("updated", []):
        ui.file_action(path, "updated")
    for path in sub.get("deleted", []):
        ui.file_action(path, "deleted")
    if sub.get("skipped") and sub.get("skip_reason"):
        ui.substep(f"subagents skipped: {sub.get('skip_reason')}")


def _build_agent_summary_parts(
    wf_counts: Dict[str, Any],
    sk_counts: Dict[str, Any],
    sub_counts: Dict[str, Any],
    dry_run: bool,
) -> List[str]:
    """Build summary parts list for one agent's result counts."""
    total_wf = wf_counts.get("created", 0) + wf_counts.get("updated", 0) + wf_counts.get("renamed", 0)
    total_wf_deleted = wf_counts.get("deleted", 0)
    total_sk = sk_counts.get("created", 0) + sk_counts.get("updated", 0)
    total_sub = sub_counts.get("created", 0) + sub_counts.get("updated", 0)
    total_deleted = sk_counts.get("deleted", 0) + sub_counts.get("deleted", 0)
    total_skipped = sk_counts.get("skipped", 0)
    parts: List[str] = []
    if total_wf:
        parts.append(f"{total_wf} workflow(s)")
    if total_wf_deleted:
        parts.append(f"{total_wf_deleted} workflow proxy/proxies {'would be removed' if dry_run else 'removed'}")
    if total_sk:
        parts.append(f"{total_sk} skill file(s)")
    if total_sub:
        parts.append(f"{total_sub} subagent file(s)")
    if total_deleted:
        parts.append(f"{total_deleted} legacy command(s) {'would be removed' if dry_run else 'removed'}")
    if total_skipped:
        parts.append(f"{total_skipped} legacy command(s) {'would be preserved' if dry_run else 'preserved'}")
    return parts


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

        _render_agent_file_actions(wf, sk, sub)

        # V2 manifest agents
        v2_ag = r.get("v2_agents", {})
        created_v2_ag = v2_ag.get("created", [])
        updated_v2_ag = v2_ag.get("updated", [])
        for path in created_v2_ag:
            ui.file_action(path, "created")
        for path in updated_v2_ag:
            ui.file_action(path, "updated")

        total_v2_ag = len(created_v2_ag) + len(updated_v2_ag)
        parts = _build_agent_summary_parts(
            wf_counts, sk_counts, sub_counts, dry_run,
        )
        if total_v2_ag:
            parts.append(f"{total_v2_ag} agent file(s)")
        if parts:
            ui.substep(", ".join(parts))


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


def _translate_windsurf_schema(_agent: "_AgentEntry") -> Dict[str, Any]:
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
# All skills go to shared .agents/skills/ directory (readable by all agents)
# Agent targeting is enforced via frontmatter metadata in the generated file
_SKILL_OUTPUT_PATHS: Dict[str, str] = {
    "claude":   ".claude/skills/{id}/SKILL.md",
    # All non-Claude tools share .agents/skills/
    "cursor":   ".agents/skills/{id}/SKILL.md",
    "copilot":  ".agents/skills/{id}/SKILL.md",
    "openai":   ".agents/skills/{id}/SKILL.md",
    "windsurf": ".agents/skills/{id}/SKILL.md",
}


def _read_source_content(
    entity_kind: str,
    entity_id: str,
    src_str: str,
    project_root: Path,
    cypilot_root: Optional[Path] = None,
    trusted_roots: Optional[List[Path]] = None,
) -> Optional[str]:
    """Resolve *src_str* to an absolute path, read text, strip leading frontmatter.

    *entity_kind* is used only in warning messages (e.g. ``"agent"`` or ``"skill"``).
    Returns ``None`` and writes to stderr on any error.
    """
    src_path = Path(src_str)
    if not src_path.is_absolute():
        src_path = project_root / src_str

    # Path traversal guard: ensure resolved path stays within project root,
    # cypilot_root (which may be external, e.g. a shared kit location), or
    # any trusted root (e.g. a discovered master repo root).
    resolved = src_path.resolve()
    try:
        resolved.relative_to(project_root.resolve())
    except ValueError:
        allowed = False
        if cypilot_root is not None:
            try:
                resolved.relative_to(cypilot_root.resolve())
                allowed = True
            except ValueError:
                pass
        if not allowed and trusted_roots:
            for root in trusted_roots:
                try:
                    resolved.relative_to(root.resolve())
                    allowed = True
                    break
                except ValueError:
                    pass
        if not allowed:
            sys.stderr.write(
                f"WARNING: {entity_kind} '{entity_id}' source escapes project root: {src_path}, skipping\n"
            )
            return None

    if not resolved.is_file():
        sys.stderr.write(
            f"WARNING: {entity_kind} '{entity_id}' source not found: {resolved}, skipping\n"
        )
        return None

    try:
        content = resolved.read_text(encoding="utf-8")
    except OSError as exc:
        sys.stderr.write(
            f"WARNING: {entity_kind} '{entity_id}' failed to read source: {exc}, skipping\n"
        )
        return None

    # Strip existing frontmatter block (---\n...\n---\n) from source
    if content.startswith("---"):
        end_idx = content.find("\n---\n", 4)
        if end_idx != -1:
            content = content[end_idx + 5:]

    return content


def _apply_variables(content: str, variables: Optional[Dict[str, str]]) -> str:
    """Replace ``{key}`` placeholders in *content* with values from *variables*."""
    if not variables:
        return content
    # Filter out empty-string keys which would produce bad regex
    keys = [k for k in variables if k]
    if not keys:
        return content
    # Single-pass replacement prevents transitive expansion of values
    # containing {other_var} patterns.
    pattern = re.compile(r"\{(" + "|".join(re.escape(k) for k in keys) + r")\}")
    return pattern.sub(lambda m: variables[m.group(1)], content)


def _build_skill_content(
    skill_id: str,
    skill: Any,
    source_content: str,
    variables: Optional[Dict[str, str]],
) -> str:
    """Assemble the final content for a skill file.

    Prepends name/description frontmatter (consistent with the shared
    .agents/skills/ convention), appends ``skill.append`` if set, then
    applies variable substitution.
    """
    fm_lines = [
        "---",
        f"name: {skill_id}",
        f"description: {_yaml_double_quote(skill.description)}",
        "---",
        "",
    ]
    content = "\n".join(fm_lines) + source_content

    if skill.append:
        content = content.rstrip("\n") + "\n" + skill.append

    # Sanitize variable values: strip newlines to prevent breaking YAML
    # frontmatter structure (consistent with TOML sanitization in OpenAI path).
    if variables:
        safe_vars = {k: v.replace("\n", " ") for k, v in variables.items()}
    else:
        safe_vars = variables
    return _apply_variables(content, safe_vars)


# @cpt-begin:cpt-cypilot-algo-project-extensibility-generate-skills:p1:inst-generate-manifest-skills
def generate_manifest_skills(
    skills: Dict[str, "_SkillEntry"],
    target: str,
    project_root: Path,
    dry_run: bool,
    variables: Optional[Dict[str, str]] = None,
    cypilot_root: Optional[Path] = None,
    trusted_roots: Optional[List[Path]] = None,
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
        "deleted": [],
        "outputs": [],
    }
    generated_skill_contents: Dict[str, str] = {}

    path_template = _SKILL_OUTPUT_PATHS.get(target, f".{target}/skills/{{id}}/SKILL.md")

    # Step 1: FOR EACH skill where target is in agents list (empty list = all targets)
    for skill_id, skill in skills.items():
        # Empty agents list means "generate for all targets" (consistent with agents behavior)
        if skill.agents and target not in skill.agents:
            continue

        # Step 1.1: Determine source path (prefer source over prompt_file)
        src_str = skill.source or skill.prompt_file
        if not src_str:
            sys.stderr.write(
                f"WARNING: skill '{skill_id}' has no source or prompt_file, skipping\n"
            )
            continue

        source_content = _read_source_content("skill", skill_id, src_str, project_root, cypilot_root=cypilot_root, trusted_roots=trusted_roots)
        if source_content is None:
            continue

        # Step 1.2: Apply agent-specific frontmatter, appends, and variables
        content = _build_skill_content(skill_id, skill, source_content, variables)
        generated_skill_contents[skill_id] = content

        # Step 1.3: Determine output path using agent-native conventions
        rel_out = path_template.replace("{id}", skill_id)
        out_path = project_root / rel_out

        # Step 1.4: Write skill file to output path using _write_or_skip
        _write_or_skip(out_path, content, result, project_root, dry_run)

    # Step 2: Clean up legacy manifest-skill files from old per-tool paths
    _LEGACY_SKILL_OUTPUT_PATHS: Dict[str, str] = {
        "cursor":   ".cursor/rules/{id}.mdc",
        "copilot":  ".github/skills/{id}.md",
        "windsurf": ".windsurf/skills/{id}/SKILL.md",
    }
    legacy_pattern = _LEGACY_SKILL_OUTPUT_PATHS.get(target)
    if legacy_pattern:
        for skill_id, skill in skills.items():
            # Same agent-targeting filter as generation (empty = all targets)
            if skill.agents and target not in skill.agents:
                continue
            legacy_rel = legacy_pattern.replace("{id}", skill_id)
            legacy_path = project_root / legacy_rel
            if not legacy_path.is_file():
                continue
            # Only delete if provably Cypilot-generated (no user content beyond the stub).
            try:
                content = legacy_path.read_text(encoding="utf-8")
            except OSError:
                continue
            expected_generated = generated_skill_contents.get(skill_id, "")
            matches_generated_body = (
                bool(expected_generated)
                and content.rstrip("\n") == expected_generated.rstrip("\n")
            )
            if not _is_pure_cypilot_generated(
                content,
                expected_name=skill_id,
                expected_description=skill.description or None,
            ) and not matches_generated_body:
                continue
            rel = legacy_rel
            if not dry_run:
                try:
                    legacy_path.unlink()
                except OSError:
                    continue
            result["deleted"].append(rel)
            deleted_record = {"path": rel, "action": "deleted"}
            result["outputs"].append(deleted_record)
            skill_obj = skills.get(skill_id)
            if skill_obj is not None:
                if isinstance(skill_obj, dict):
                    skill_deleted = skill_obj.get("deleted")
                    if not isinstance(skill_deleted, list):
                        skill_deleted = []
                        skill_obj["deleted"] = skill_deleted
                else:
                    skill_deleted = getattr(skill_obj, "deleted", None)
                    if not isinstance(skill_deleted, list):
                        skill_deleted = []
                        try:
                            object.__setattr__(skill_obj, "deleted", skill_deleted)
                        except (AttributeError, TypeError):
                            skill_deleted = None
                if isinstance(skill_deleted, list):
                    skill_deleted.append({"path": rel, "action": "deleted"})

    # Step 3: Return result dict
    result["unchanged"] = [
        o["path"] for o in result["outputs"] if o.get("action") == "unchanged"
    ]
    return result


# Agent output paths per agent tool
_AGENT_OUTPUT_PATHS: Dict[str, str] = {
    "claude":   ".claude/agents/{id}.md",
    "cursor":   ".cursor/agents/{id}.mdc",
    "copilot":  ".github/agents/{id}.md",
    "openai":   ".agents/{id}/agent.md",
    # windsurf: no subagent support — handled via translate_agent_schema skip
}


# @cpt-begin:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-assemble-agent-file
def _build_openai_agent_file(
    agent_id: str,
    agent: Any,
    translated: Dict[str, Any],
    source_content: str,
    path_template: str,
    variables: Optional[Dict[str, str]],
) -> Tuple[str, str]:
    """Assemble TOML content and output path for an OpenAI/Codex agent.

    Returns ``(content, rel_out)`` where *rel_out* has ``.md`` replaced by ``.toml``.
    """
    sandbox_mode = translated.get("sandbox_mode", "workspace-write")
    dev_instructions = source_content
    model_str = translated.get("model", "")
    # Validate agent_id before using in TOML section header
    safe_id = agent_id.replace("-", "_")
    if not _VALID_AGENT_NAME_RE.match(safe_id):
        sys.stderr.write(f"WARNING: agent id {agent_id!r} is not a valid TOML key, skipping\n")
        return "", ""
    toml_lines = [f"[agents.{safe_id}]"]
    toml_lines.append(f'description = "{_escape_toml_basic_string(agent.description or "")}"')
    toml_lines.append(f'sandbox_mode = "{sandbox_mode}"')
    if model_str and model_str != "inherit":
        toml_lines.append(f'model = "{_escape_toml_basic_string(model_str)}"')
    # Escape backslashes and triple-quotes in content to prevent TOML injection
    safe_instructions = _escape_toml_multiline_string(dev_instructions)
    toml_lines.append('developer_instructions = """')
    toml_lines.append(safe_instructions)
    # Append content inside the triple-quoted string to prevent TOML injection.
    if agent.append:
        safe_append = _escape_toml_multiline_string(agent.append)
        toml_lines.append(safe_append)
    toml_lines.append('"""')
    content = "\n".join(toml_lines) + "\n"
    # Sanitize variable values to prevent TOML injection: escape backslashes
    # and triple-quotes in replacement values so they cannot break TOML parsing.
    if variables:
        safe_vars = {k: _escape_toml_multiline_string(v) for k, v in variables.items()}
    else:
        safe_vars = variables
    content = _apply_variables(content, safe_vars)
    rel_out = path_template.replace("{id}", agent_id).replace(".md", ".toml")
    return content, rel_out


def _build_standard_agent_file(
    agent_id: str,
    agent: Any,
    translated: Dict[str, Any],
    source_content: str,
    path_template: str,
    variables: Optional[Dict[str, str]],
) -> Tuple[str, str]:
    """Assemble YAML frontmatter + body content and output path for a standard agent.

    Returns ``(content, rel_out)``.
    """
    frontmatter_lines: List[str] = ["---"]
    frontmatter_lines.append(f"name: {agent.id}")
    frontmatter_lines.append(f"description: {_yaml_double_quote(agent.description)}")
    frontmatter_lines.extend(translated.get("frontmatter", []))
    frontmatter_lines.append("---")

    body_prefix = translated.get("body_prefix", "")
    body_suffix = translated.get("body_suffix", "")
    content = "\n".join(frontmatter_lines) + "\n" + body_prefix + source_content + body_suffix

    if agent.append:
        content = content.rstrip("\n") + "\n" + agent.append

    # Sanitize variable values: strip newlines to prevent breaking YAML
    # frontmatter structure (consistent with TOML sanitization in OpenAI path).
    if variables:
        safe_vars = {k: v.replace("\n", " ") for k, v in variables.items()}
    else:
        safe_vars = variables
    content = _apply_variables(content, safe_vars)
    # @cpt-begin:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-determine-agent-path
    rel_out = path_template.replace("{id}", agent_id)
    # @cpt-end:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-determine-agent-path
    return content, rel_out
# @cpt-end:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-assemble-agent-file


# @cpt-begin:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-generate-manifest-agents
def generate_manifest_agents(
    agents: Dict[str, "_AgentEntry"],
    target: str,
    project_root: Path,
    dry_run: bool,
    variables: Optional[Dict[str, str]] = None,
    cypilot_root: Optional[Path] = None,
    trusted_roots: Optional[List[Path]] = None,
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
            sys.stderr.write(
                f"INFO: agent '{agent_id}' skipped for target '{target}': {translated.get('skip_reason', '')}\n"
            )
            continue
        # @cpt-end:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-check-skip
        if not agent.description and target == "claude":
            sys.stderr.write(
                f"WARNING: agent '{agent_id}' has no description — agent will not register with Claude CLI\n"
            )
            continue
        # Step 1.3: Read prompt_file (or source) content from agent's resolved path
        # @cpt-begin:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-read-agent-source
        src_str = agent.source or agent.prompt_file
        if not src_str:
            sys.stderr.write(
                f"WARNING: agent '{agent_id}' has no source or prompt_file, skipping\n"
            )
            continue
        source_content = _read_source_content("agent", agent_id, src_str, project_root, cypilot_root=cypilot_root, trusted_roots=trusted_roots)
        # @cpt-end:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-read-agent-source
        if source_content is None:
            continue
        # Step 1.4: Assemble full file and determine output path
        # @cpt-begin:cpt-cypilot-algo-project-extensibility-generate-agents:p1:inst-write-agent
        if target == "openai":
            content, rel_out = _build_openai_agent_file(agent_id, agent, translated, source_content, path_template, variables)
        else:
            content, rel_out = _build_standard_agent_file(agent_id, agent, translated, source_content, path_template, variables)
        if not content and not rel_out:
            continue
        out_path = project_root / rel_out
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
            prov_key = f"{component_type}:{cid}"
            prov: "_ProvenanceRecord" = merged.provenance[prov_key]

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


def _discover_md_files(base_dir: Path, glob_pattern: str, id_fn) -> List[Dict[str, str]]:
    """Scan *base_dir* for files matching *glob_pattern*, extract IDs via *id_fn*.

    Returns a list of ``{"id": ..., "source": ..., "description": ...}`` dicts.
    Silently returns [] if *base_dir* does not exist.
    """
    if not base_dir.is_dir():
        return []
    results = []
    for md_file in sorted(base_dir.glob(glob_pattern)):
        if md_file.is_file():
            results.append({
                "id": id_fn(md_file),
                "source": md_file.as_posix(),
                "description": _extract_frontmatter_description(md_file),
            })
    return results


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
    _claude = project_root / ".claude"
    return {
        "agents":    _discover_md_files(_claude / "agents",   "*.md",        lambda p: p.stem),
        "skills":    _discover_md_files(_claude / "skills",   "*/SKILL.md",  lambda p: p.parent.name),
        "workflows": _discover_md_files(_claude / "commands", "*.md",        lambda p: p.stem),
    }
# @cpt-end:cpt-cypilot-flow-project-extensibility-discover-register:p2:inst-step2-scan-dirs


def _extract_frontmatter_description(path: Path) -> str:
    """Extract description from YAML frontmatter in a markdown file.

    Looks for a ``description:`` key in the YAML front matter block delimited
    by ``---`` markers.  Returns empty string if not found or on any error.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""

    _desc_key = "description:"
    for line in lines[1:]:
        if line.strip() == "---":
            break
        stripped = line.lstrip()
        if stripped.startswith(_desc_key):
            return stripped[len(_desc_key):].strip().strip('"').strip("'")

    return ""


def _collect_existing_ids(content: str) -> Set[str]:
    """Return the set of ``id`` values already present in TOML *content*."""
    return {m.group(1) for m in re.finditer(r'^id\s*=\s*"([^"]+)"', content, re.MULTILINE)}


def _escape_toml_basic_string(value: str) -> str:
    """Escape *value* for use inside a TOML basic (double-quoted) string.

    Handles backslashes, double quotes, and control characters (newlines,
    tabs, carriage returns) that would otherwise break TOML parsing.
    """
    value = value.replace("\\", "\\\\")
    value = value.replace('"', '\\"')
    value = value.replace("\n", "\\n")
    value = value.replace("\r", "\\r")
    value = value.replace("\t", "\\t")
    return value


def _escape_toml_multiline_string(value: str) -> str:
    """Escape *value* for use inside a TOML multi-line basic string (triple-quoted).

    In multi-line basic strings (``\"\"\"...\"\"\"``), backslashes are still
    escape characters, so literal ``\\`` must be doubled.  Triple-quote
    sequences must also be escaped to prevent premature closure.
    """
    value = value.replace("\\", "\\\\")
    value = value.replace('"""', '""\\"')
    return value


def _format_toml_entry(section: str, entry: Dict[str, str]) -> List[str]:
    """Return lines for one ``[[section]]`` TOML block for *entry*."""
    lines: List[str] = [f'[[{section}]]', f'id = "{_escape_toml_basic_string(entry["id"])}"']
    if entry.get("description"):
        lines.append(f'description = "{_escape_toml_basic_string(entry["description"])}"')
    if entry.get("source"):
        lines.append(f'source = "{_escape_toml_basic_string(entry["source"])}"')
    lines.append('')
    return lines


def _build_manifest_section_lines(
    discovered: Dict,
    section_order: List[str],
    exclude_ids: Set[str],
) -> List[str]:
    """Return flat list of TOML lines for all sections, skipping *exclude_ids*."""
    lines: List[str] = []
    for section in section_order:
        for entry in discovered.get(section, []):
            if entry["id"] not in exclude_ids:
                lines.extend(_format_toml_entry(section, entry))
    return lines


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

    section_order = ["agents", "skills", "workflows"]
    existing_content: Optional[str] = None
    if manifest_path.is_file():
        try:
            existing_content = manifest_path.read_text(encoding="utf-8")
        except OSError:
            existing_content = None

    if existing_content is not None:
        existing_ids = _collect_existing_ids(existing_content)
        new_lines = _build_manifest_section_lines(discovered, section_order, existing_ids)
        if not new_lines:
            return
        appended = existing_content.rstrip("\n") + "\n\n# New entries appended by --discover\n" + "\n".join(new_lines)
        manifest_path.write_text(appended, encoding="utf-8")  # NOSONAR
        return

    header = ['[manifest]', 'version = "2.0"', '']
    body = _build_manifest_section_lines(discovered, section_order, set())
    manifest_path.write_text("\n".join(header + body), encoding="utf-8")  # NOSONAR
# @cpt-end:cpt-cypilot-flow-project-extensibility-discover-register:p2:inst-step4-write-manifest
# @cpt-end:cpt-cypilot-algo-project-extensibility-generate-skills:p1:inst-generate-manifest-skills
