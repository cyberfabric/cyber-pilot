import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ..utils.files import core_subpath, gen_subpath, find_project_root, _is_cypilot_root


def _safe_relpath(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def _safe_relpath_from_dir(target: Path, from_dir: Path) -> str:
    try:
        rel = os.path.relpath(target.as_posix(), from_dir.as_posix())
    except Exception:
        return target.as_posix()
    return rel.replace(os.sep, "/")


def _target_path_from_root(target: Path, project_root: Path) -> str:
    """Return agent-instruction path as @/<project-root-relative> when possible.

    Using a project-root-relative alias avoids long ``../../..`` traversals that
    escape the repository when the cypilot submodule lives at a path that is
    outside or at a different depth than the project root.

    After ``_ensure_cypilot_local`` runs, every referenced path should be inside
    ``project_root``, so the ``except`` branch is a defensive safety-net only.
    """
    try:
        rel = target.relative_to(project_root).as_posix()
        return f"@/{rel}"
    except ValueError:
        print(
            f"WARNING: path {target} is outside project root {project_root}, "
            "agent proxy will contain an absolute path",
            file=sys.stderr,
        )
        return target.as_posix()


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

    local_dot = project_root / "cypilot"

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


def _load_json_file(path: Path) -> Optional[dict]:
    if not path.is_file():
        return None
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, OSError, IOError):
        return None


def _write_json_file(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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
                "workflows": {
                    "workflow_dir": ".claude/commands",
                    "workflow_command_prefix": "cypilot-",
                    "workflow_filename_format": "{command}.md",
                    "custom_content": "",
                    "template": [
                        "---",
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
                            "path": ".claude/commands/cypilot.md",
                            "template": [
                                "---",
                                "description: {description}",
                                "---",
                                "",
                                "{custom_content}",
                                "ALWAYS open and follow `{target_skill_path}`",
                            ],
                        },
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


def _list_workflow_files(cypilot_root: Path) -> List[str]:
    workflows_dir = core_subpath(cypilot_root, "workflows").resolve()
    if not workflows_dir.is_dir():
        return []
    out: List[str] = []
    try:
        for p in workflows_dir.iterdir():
            if not p.is_file():
                continue
            if p.suffix.lower() != ".md":
                continue
            if p.name in {"AGENTS.md", "README.md"}:
                continue
            try:
                head = "\n".join(p.read_text(encoding="utf-8").splitlines()[:30])
            except Exception:
                continue
            if "type: workflow" not in head:
                continue
            out.append(p.name)
    except Exception:
        return []
    return sorted(set(out))


_ALL_RECOGNIZED_AGENTS = ["windsurf", "cursor", "claude", "copilot", "openai"]


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

    workflows_result: Dict[str, Any] = {"created": [], "updated": [], "renamed": [], "deleted": [], "errors": []}

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
            cypilot_workflow_files = _list_workflow_files(cypilot_root)
            cypilot_workflow_names = [Path(p).stem for p in cypilot_workflow_files]

            desired: Dict[str, Dict[str, str]] = {}
            for wf_name in cypilot_workflow_names:
                command = "cypilot" if wf_name == "cypilot" else f"{prefix}{wf_name}"
                filename = filename_fmt.format(command=command, workflow_name=wf_name)
                desired_path = (workflow_dir / filename).resolve()
                target_workflow_path = core_subpath(cypilot_root, "workflows", f"{wf_name}.md").resolve()

                if desired_path.as_posix() in skill_output_paths:
                    continue

                target_rel = _target_path_from_root(target_workflow_path, project_root)

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
                # Normalize legacy relative/absolute paths to @/... canonical form
                if not target_rel.startswith("@/"):
                    if target_rel.startswith("/"):
                        resolved = Path(target_rel)
                    else:
                        resolved = (pth.parent / target_rel).resolve()
                    target_rel = _target_path_from_root(resolved, project_root)
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
                if target_rel.startswith("@/"):
                    expected = (project_root / target_rel[2:]).resolve()
                elif not target_rel.startswith("/"):
                    expected = (pth.parent / target_rel).resolve()
                else:
                    expected = Path(target_rel)
                try:
                    expected.relative_to(core_subpath(cypilot_root, "workflows"))
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

    skills_result: Dict[str, Any] = {"created": [], "updated": [], "outputs": [], "errors": []}

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
                    out_dir = out_path.parent

                    custom_target = out_cfg.get("target")
                    if custom_target:
                        target_abs = core_subpath(cypilot_root, *Path(custom_target).parts).resolve()
                        target_rel = _target_path_from_root(target_abs, project_root)
                        target_fm = _parse_frontmatter(target_abs)
                        out_name = target_fm.get("name", skill_source_name)
                        out_description = target_fm.get("description", skill_source_description)
                    else:
                        target_rel = _target_path_from_root(target_skill_abs, project_root)
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

                    if not out_path.exists():
                        skills_result["created"].append(out_path.as_posix())
                        if not dry_run:
                            out_path.parent.mkdir(parents=True, exist_ok=True)
                            out_path.write_text(content, encoding="utf-8")
                        skills_result["outputs"].append({"path": _safe_relpath(out_path, project_root), "action": "created"})
                    else:
                        try:
                            old = out_path.read_text(encoding="utf-8")
                        except Exception:
                            old = ""
                        if old != content:
                            skills_result["updated"].append(out_path.as_posix())
                            if not dry_run:
                                out_path.write_text(content, encoding="utf-8")
                            skills_result["outputs"].append({"path": _safe_relpath(out_path, project_root), "action": "updated"})
                        else:
                            skills_result["outputs"].append({"path": _safe_relpath(out_path, project_root), "action": "unchanged"})

    all_errors = workflows_result.get("errors", []) + skills_result.get("errors", [])
    agent_status = "PASS" if not all_errors else "PARTIAL"

    return {
        "status": agent_status,
        "agent": agent,
        "workflows": {
            "created": workflows_result["created"],
            "updated": workflows_result["updated"],
            "renamed": workflows_result["renamed"],
            "deleted": workflows_result["deleted"],
            "counts": {
                "created": len(workflows_result["created"]),
                "updated": len(workflows_result["updated"]),
                "renamed": len(workflows_result["renamed"]),
                "deleted": len(workflows_result["deleted"]),
            },
        },
        "skills": {
            "created": skills_result["created"],
            "updated": skills_result["updated"],
            "outputs": skills_result["outputs"],
            "counts": {
                "created": len(skills_result["created"]),
                "updated": len(skills_result["updated"]),
            },
        },
        "errors": all_errors if all_errors else None,
    }


def cmd_agents(argv: List[str]) -> int:
    """Unified command to register both workflows and skills for an agent."""
    p = argparse.ArgumentParser(prog="agents", description="Generate/update agent-specific workflow proxies and skill outputs")
    agent_group = p.add_mutually_exclusive_group(required=False)
    agent_group.add_argument("--agent", default=None, help="Agent/IDE key (e.g., windsurf, cursor, claude, copilot, openai). Omit to init all supported agents.")
    agent_group.add_argument("--openai", action="store_true", help="Shortcut for --agent openai (OpenAI Codex)")
    p.add_argument("--root", default=".", help="Project root directory (default: current directory)")
    p.add_argument("--cypilot-root", default=None, help="Explicit Cypilot core root (optional override)")
    p.add_argument("--config", default=None, help="Path to agents config JSON (optional; defaults are built-in)")
    p.add_argument("--dry-run", action="store_true", help="Compute changes without writing files")
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
        print(json.dumps({
            "status": "NOT_FOUND",
            "message": "No project root found (no AGENTS.md with @cpt:root-agents or .git)",
            "searched_from": start_path.as_posix(),
        }, indent=2, ensure_ascii=False))
        return 1

    cypilot_root = Path(args.cypilot_root).resolve() if args.cypilot_root else None
    if cypilot_root is None:
        cypilot_root = (Path(__file__).resolve().parents[5])
        if not _is_cypilot_root(cypilot_root):
            cypilot_root = Path(__file__).resolve().parents[7]

    cypilot_root, copy_report = _ensure_cypilot_local(cypilot_root, project_root, args.dry_run)
    if copy_report.get("action") == "error":
        print(json.dumps({
            "status": "COPY_ERROR",
            "message": f"Failed to copy cypilot into project: {copy_report.get('message', 'unknown')}",
            "cypilot_root": cypilot_root.as_posix(),
            "project_root": project_root.as_posix(),
        }, indent=2, ensure_ascii=False))
        return 1

    cfg_path: Optional[Path] = Path(args.config).resolve() if args.config else None
    cfg: Optional[dict] = _load_json_file(cfg_path) if cfg_path else None

    any_recognized = any(a in set(_ALL_RECOGNIZED_AGENTS) for a in agents_to_process)
    if cfg is None:
        if any_recognized:
            cfg = _default_agents_config()
        else:
            cfg = {"version": 1, "agents": {a: {"workflows": {}, "skills": {}} for a in agents_to_process}}

    has_errors = False
    results: Dict[str, Any] = {}
    for agent in agents_to_process:
        result = _process_single_agent(agent, project_root, cypilot_root, cfg, cfg_path, args.dry_run)
        results[agent] = result
        if result.get("status") != "PASS":
            has_errors = True

    overall_status = "PASS" if not has_errors else "PARTIAL"

    print(json.dumps({
        "status": overall_status,
        "agents": list(agents_to_process),
        "project_root": project_root.as_posix(),
        "cypilot_root": cypilot_root.as_posix(),
        "config_path": cfg_path.as_posix() if cfg_path else None,
        "dry_run": bool(args.dry_run),
        "cypilot_copy": copy_report,
        "results": results,
    }, indent=2, ensure_ascii=False))

    return 0 if not has_errors else 1
