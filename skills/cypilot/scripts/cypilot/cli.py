"""
Cypilot Validator - CLI Entry Point

Command-line interface for the Cypilot validation tool.
"""

import sys
import os
import json
import re
import argparse
from pathlib import Path
from typing import Any, List, Optional, Dict, Set, Tuple

from .utils.files import (
    find_project_root,
    load_project_config,
    find_adapter_directory,
    load_adapter_config,
    load_artifacts_registry,
)
from .utils.artifacts_meta import (
    ArtifactsMeta,
    create_backup,
    generate_default_registry,
)
from .utils.template import (
    Template,
    Artifact as TemplateArtifact,
)
from .utils.codebase import (
    CodeFile,
    cross_validate_code,
)


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
                            "path": ".claude/skills/cypilot-adapter/SKILL.md",
                            "target": "workflows/adapter.md",
                            "template": [
                                "---",
                                "name: cypilot-adapter",
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
            inner = inner.replace("\\\"", '"')
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


def _cmd_self_check(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="self-check", description="Validate registered template examples against templates")
    p.add_argument("--root", default=".", help="Project root to search from (default: current directory)")
    p.add_argument("--kit", "--rule", dest="kit", help="Specific kit ID to check (e.g., cypilot-sdlc)")
    p.add_argument("--verbose", action="store_true", help="Include full per-template error/warning lists")
    args = p.parse_args(argv)

    start_path = Path(args.root).resolve()
    project_root = find_project_root(start_path)
    if project_root is None:
        print(json.dumps({"status": "ERROR", "message": "Project root not found"}, indent=2, ensure_ascii=False))
        return 1

    adapter_dir = find_adapter_directory(project_root)
    if adapter_dir is None:
        print(json.dumps({"status": "ERROR", "message": "Adapter directory not found"}, indent=2, ensure_ascii=False))
        return 1

    reg, reg_err = load_artifacts_registry(adapter_dir)
    if reg_err or reg is None:
        print(json.dumps({"status": "ERROR", "message": reg_err or "Missing artifacts registry"}, indent=2, ensure_ascii=False))
        return 1

    # Validate slugs in the registry
    artifacts_meta = ArtifactsMeta.from_dict(reg)
    slug_errors = artifacts_meta.validate_all_slugs()
    if slug_errors:
        print(json.dumps({
            "status": "ERROR",
            "message": "Invalid slugs in artifacts.json",
            "slug_errors": slug_errors,
        }, indent=2, ensure_ascii=False))
        return 1

    kits_cfg = reg.get("kits") if isinstance(reg, dict) else None
    if not isinstance(kits_cfg, dict) or not kits_cfg:
        print(json.dumps({"status": "ERROR", "message": "No kits defined in artifacts.json"}, indent=2, ensure_ascii=False))
        return 1

    try:
        from .utils.template import validate_artifact_file_against_template
    except Exception:
        validate_artifact_file_against_template = None  # type: ignore[assignment]

    if validate_artifact_file_against_template is None:
        print(json.dumps({"status": "ERROR", "message": "Template validation module not available"}, indent=2, ensure_ascii=False))
        return 1

    results: List[Dict[str, object]] = []
    overall_status = "PASS"
    kits_checked = 0

    for kit_id, kit_def in kits_cfg.items():
        if args.kit and kit_id != args.kit:
            continue
        if not isinstance(kit_def, dict):
            continue

        kit_path_str = kit_def.get("path")
        if not isinstance(kit_path_str, str):
            continue

        kit_base = (project_root / kit_path_str).resolve()
        artifacts_dir = kit_base / "artifacts"
        if not artifacts_dir.is_dir():
            continue

        kits_checked += 1

        for kind_dir in sorted(artifacts_dir.iterdir()):
            if not kind_dir.is_dir():
                continue

            kind = kind_dir.name
            template_path = kind_dir / "template.md"
            # Find any .md file in examples/ directory (not just example.md)
            examples_dir = kind_dir / "examples"
            example_path = None
            if examples_dir.exists():
                md_files = list(examples_dir.glob("*.md"))
                if md_files:
                    example_path = md_files[0]  # Use first .md file found

            if not template_path.exists():
                continue

            item: Dict[str, object] = {
                "kit": kit_id,
                "kind": kind,
                "template_path": template_path.as_posix(),
                "example_path": example_path.as_posix() if example_path else None,
                "status": "PASS",
            }

            errs: List[Dict[str, object]] = []
            warns: List[Dict[str, object]] = []

            if not example_path:
                warns.append({"type": "file", "message": "Example not found (skipped)", "path": (kind_dir / "examples").as_posix()})
            else:
                rep = validate_artifact_file_against_template(
                    artifact_path=example_path,
                    template_path=template_path,
                    expected_kind=kind,
                )
                errs.extend(list(rep.get("errors", []) or []))
                warns.extend(list(rep.get("warnings", []) or []))

            if errs:
                item["status"] = "FAIL"
                item["error_count"] = len(errs)
                item["errors"] = errs  # Always show errors on failure
                overall_status = "FAIL"
            if warns:
                item["warning_count"] = len(warns)
                if errs or bool(args.verbose):
                    item["warnings"] = warns  # Show warnings on failure or verbose

            results.append(item)

    out = {
        "status": overall_status,
        "project_root": project_root.as_posix(),
        "adapter_dir": adapter_dir.as_posix(),
        "kits_checked": kits_checked,
        "templates_checked": len(results),
        "results": results,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if overall_status == "PASS" else 2


def _cmd_agents(argv: List[str]) -> int:
    """Unified command to register both workflows and skills for an agent."""
    p = argparse.ArgumentParser(prog="agents", description="Generate/update agent-specific workflow proxies and skill outputs")
    agent_group = p.add_mutually_exclusive_group(required=True)
    agent_group.add_argument("--agent", help="Agent/IDE key (e.g., windsurf, cursor, claude, copilot, openai)")
    agent_group.add_argument("--openai", action="store_true", help="Shortcut for --agent openai (OpenAI Codex)")
    p.add_argument("--root", default=".", help="Project root directory (default: current directory)")
    p.add_argument("--cypilot-root", default=None, help="Explicit Cypilot core root (optional override)")
    p.add_argument("--config", default=None, help="Path to unified agents config JSON (default: cypilot-agents.json in project root)")
    p.add_argument("--dry-run", action="store_true", help="Compute changes without writing files")
    args = p.parse_args(argv)

    agent = "openai" if bool(getattr(args, "openai", False)) else str(args.agent).strip()
    if not agent:
        raise SystemExit("--agent must be non-empty")

    start_path = Path(args.root).resolve()
    project_root = find_project_root(start_path)
    if project_root is None:
        print(json.dumps({
            "status": "NOT_FOUND",
            "message": "No project root found (no .git or .cypilot-config.json)",
            "searched_from": start_path.as_posix(),
        }, indent=2, ensure_ascii=False))
        return 1

    cypilot_root = Path(args.cypilot_root).resolve() if args.cypilot_root else None
    if cypilot_root is None:
        cypilot_root = (Path(__file__).resolve().parents[4])
        if not ((cypilot_root / "AGENTS.md").exists() and (cypilot_root / "workflows").is_dir()):
            cypilot_root = Path(__file__).resolve().parents[6]

    cfg_path = Path(args.config).resolve() if args.config else (project_root / "cypilot-agents.json")
    cfg = _load_json_file(cfg_path)

    recognized = agent in {"windsurf", "cursor", "claude", "copilot", "openai"}
    if cfg is None:
        cfg = _default_agents_config() if recognized else {"version": 1, "agents": {agent: {"workflows": {}, "skills": {}}}}
        if not args.dry_run:
            _write_json_file(cfg_path, cfg)

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
        if not args.dry_run:
            _write_json_file(cfg_path, cfg)

    if not isinstance(agents_cfg, dict) or agent not in agents_cfg or not isinstance(agents_cfg.get(agent), dict):
        print(json.dumps({
            "status": "CONFIG_ERROR",
            "message": "Agent config missing or invalid",
            "config_path": cfg_path.as_posix(),
            "agent": agent,
        }, indent=2, ensure_ascii=False))
        return 1

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

    # --- WORKFLOWS SECTION ---
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
                target_workflow_path = (cypilot_root / "workflows" / f"{wf_name}.md").resolve()

                # If a skill output (e.g., /cypilot) already owns this path, do not generate a workflow proxy.
                if desired_path.as_posix() in skill_output_paths:
                    continue

                # Paths inside generated proxy files must be relative to the proxy file location.
                target_rel = _safe_relpath_from_dir(target_workflow_path, desired_path.parent)

                # Parse frontmatter from source workflow
                fm = _parse_frontmatter(target_workflow_path)
                source_name = fm.get("name", command)
                source_description = fm.get("description", f"Proxy to Cypilot workflow {wf_name}")

                # Get custom content from config (optional user-defined section)
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

            # Rename misnamed proxy files
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
                dst = desired_by_target.get(target_rel)
                if not dst or pth.as_posix() == dst:
                    continue
                if Path(dst).exists():
                    continue
                if not args.dry_run:
                    workflow_dir.mkdir(parents=True, exist_ok=True)
                    Path(dst).parent.mkdir(parents=True, exist_ok=True)
                    pth.replace(Path(dst))
                workflows_result["renamed"].append((pth.as_posix(), dst))

            existing_files = list(workflow_dir.glob("*.md")) if workflow_dir.is_dir() else []

            # Create/update desired files
            for p_str, meta in desired.items():
                pth = Path(p_str)
                if not pth.exists():
                    workflows_result["created"].append(p_str)
                    if not args.dry_run:
                        pth.parent.mkdir(parents=True, exist_ok=True)
                        pth.write_text(meta["content"], encoding="utf-8")
                    continue
                try:
                    old = pth.read_text(encoding="utf-8")
                except Exception:
                    old = ""
                if old != meta["content"]:
                    workflows_result["updated"].append(p_str)
                    if not args.dry_run:
                        pth.write_text(meta["content"], encoding="utf-8")

            # Delete stale proxies
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
                if not target_rel.startswith("/"):
                    expected = (pth.parent / target_rel).resolve()
                else:
                    expected = Path(target_rel)
                try:
                    expected.relative_to(cypilot_root / "workflows")
                except ValueError:
                    continue
                if expected.exists():
                    continue
                workflows_result["deleted"].append(p_str)
                if not args.dry_run:
                    try:
                        pth.unlink()
                    except (PermissionError, FileNotFoundError, OSError):
                        pass  # Expected: cleanup failure is non-fatal

    # --- SKILLS SECTION ---
    skills_result: Dict[str, Any] = {"created": [], "updated": [], "outputs": [], "errors": []}

    if isinstance(skills_cfg, dict) and skills_cfg:
        outputs = skills_cfg.get("outputs")
        skill_name = skills_cfg.get("skill_name", "cypilot")

        if outputs is not None:
            if not isinstance(outputs, list) or not all(isinstance(x, dict) for x in outputs):
                skills_result["errors"].append("outputs must be an array of objects")
            else:
                # Cypilot skill source is always located relative to this script.
                # `.../skills/cypilot/scripts/cypilot/cli.py` -> `.../skills/cypilot/SKILL.md`
                target_skill_abs = (Path(__file__).resolve().parents[2] / "SKILL.md").resolve()
                if not target_skill_abs.is_file():
                    skills_result["errors"].append(
                        "Cypilot skill source not found (expected: " + target_skill_abs.as_posix() + ")"
                    )

                # Parse frontmatter from source SKILL.md
                skill_fm = _parse_frontmatter(target_skill_abs)
                skill_source_name = skill_fm.get("name", skill_name)
                skill_source_description = skill_fm.get("description", "Proxy to Cypilot core skill instructions")

                # Get custom content from config (optional user-defined section)
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

                    # Support custom target path (e.g., for workflow outputs)
                    custom_target = out_cfg.get("target")
                    if custom_target:
                        target_abs = (cypilot_root / custom_target).resolve()
                        target_rel = _safe_relpath_from_dir(target_abs, out_dir)
                        # Parse frontmatter from custom target
                        target_fm = _parse_frontmatter(target_abs)
                        out_name = target_fm.get("name", skill_source_name)
                        out_description = target_fm.get("description", skill_source_description)
                    else:
                        target_rel = _safe_relpath_from_dir(target_skill_abs, out_dir)
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
                        if not args.dry_run:
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
                            if not args.dry_run:
                                out_path.write_text(content, encoding="utf-8")
                            skills_result["outputs"].append({"path": _safe_relpath(out_path, project_root), "action": "updated"})
                        else:
                            skills_result["outputs"].append({"path": _safe_relpath(out_path, project_root), "action": "unchanged"})

    # --- OUTPUT ---
    all_errors = workflows_result.get("errors", []) + skills_result.get("errors", [])
    status = "PASS" if not all_errors else "PARTIAL"

    print(json.dumps({
        "status": status,
        "agent": agent,
        "project_root": project_root.as_posix(),
        "cypilot_root": cypilot_root.as_posix(),
        "config_path": cfg_path.as_posix(),
        "dry_run": bool(args.dry_run),
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
    }, indent=2, ensure_ascii=False))
    return 0 if not all_errors else 1


def _default_project_config(cypilot_core_path: str, cypilot_adapter_path: str) -> dict:
    return {
        "cypilotCorePath": cypilot_core_path,
        "cypilotAdapterPath": cypilot_adapter_path,
        "codeScanning": {
            "fileExtensions": [
                ".py",
                ".md",
                ".js",
                ".ts",
                ".tsx",
                ".go",
                ".rs",
                ".java",
                ".cs",
                ".sql",
            ],
            "singleLineComments": ["#", "//", "--"],
            "multiLineComments": [
                {"start": "/*", "end": "*/"},
                {"start": "<!--", "end": "-->"},
            ],
            "blockCommentPrefixes": ["*"],
        },
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


def _list_workflow_files(cypilot_root: Path) -> List[str]:
    workflows_dir = (cypilot_root / "workflows").resolve()
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


def _cmd_init(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="init", description="Initialize Cypilot config and minimal adapter")
    p.add_argument("--project-root", default=None, help="Project root directory to create .cypilot-config.json in")
    p.add_argument("--cypilot-root", default=None, help="Explicit Cypilot core root (optional override)")
    p.add_argument("--adapter-path", default=None, help="Adapter directory path relative to project root (default: .cypilot-adapter)")
    p.add_argument("--project-name", default=None, help="Project name used in adapter AGENTS.md (default: project root folder name)")
    p.add_argument("--yes", action="store_true", help="Do not prompt; accept defaults")
    p.add_argument("--dry-run", action="store_true", help="Compute changes without writing files")
    p.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = p.parse_args(argv)

    cwd = Path.cwd().resolve()
    cypilot_root = Path(args.cypilot_root).resolve() if args.cypilot_root else None
    if cypilot_root is None:
        cypilot_root = (Path(__file__).resolve().parents[4])
        if not ((cypilot_root / "AGENTS.md").exists() and (cypilot_root / "workflows").is_dir()):
            cypilot_root = Path(__file__).resolve().parents[6]

    # Default to the directory where the command was invoked.
    default_project_root = cwd
    if args.project_root is None and not args.yes:
        raw_root = _prompt_path("Where should I create .cypilot-config.json?", default_project_root.as_posix())
        project_root = _resolve_user_path(raw_root, cwd)
    else:
        raw_root = args.project_root or default_project_root.as_posix()
        project_root = _resolve_user_path(raw_root, cwd)

    # If a config already exists, prefer its adapter path as the default.
    config_path = (project_root / ".cypilot-config.json").resolve()
    existing_cfg = _load_json_file(config_path) if config_path.is_file() else None

    default_adapter_path = ".cypilot-adapter"
    if args.adapter_path is None and isinstance(existing_cfg, dict):
        existing_adapter_path = existing_cfg.get("cypilotAdapterPath")
        if isinstance(existing_adapter_path, str) and existing_adapter_path.strip():
            default_adapter_path = existing_adapter_path.strip()
    if args.adapter_path is None and not args.yes:
        adapter_rel = _prompt_path("Where should I create the Cypilot adapter directory (relative to project root)?", default_adapter_path)
    else:
        adapter_rel = args.adapter_path or default_adapter_path
    adapter_rel = adapter_rel.strip() or default_adapter_path

    adapter_dir = (project_root / adapter_rel).resolve()
    core_rel = _safe_relpath_from_dir(cypilot_root, project_root)
    extends_target = (cypilot_root / "AGENTS.md").resolve()
    extends_rel = _safe_relpath_from_dir(extends_target, adapter_dir)

    project_name = str(args.project_name).strip() if args.project_name else project_root.name

    # Use kit-based WHEN clause format (not workflow-based)
    kit_id = "cypilot-sdlc"
    artifacts_when = f"ALWAYS open and follow `artifacts.json` WHEN Cypilot uses kit `{kit_id}` for artifact kinds: PRD, DESIGN, DECOMPOSITION, ADR, SPEC OR codebase"
    # Use {cypilot_path} variable instead of relative paths for Cypilot core references
    desired_agents = "\n".join([
        f"# Cypilot Adapter: {project_name}",
        "",
        f"**Extends**: `{extends_rel}`",
        "",
        "---",
        "",
        "## Variables",
        "",
        "**While Cypilot is enabled**, remember these variables:",
        "",
        "| Variable | Value | Description |",
        "|----------|-------|-------------|",
        "| `{cypilot_adapter_path}` | Directory containing this AGENTS.md | Root path for Cypilot Adapter navigation |",
        "",
        "Use `{cypilot_adapter_path}` as the base path for all relative Cypilot Adapter file references.",
        "",
        "---",
        "",
        "## Navigation Rules",
        "",
        "ALWAYS open and follow `{cypilot_path}/schemas/artifacts.schema.json` WHEN working with artifacts.json",
        "",
        "ALWAYS open and follow `{cypilot_path}/requirements/artifacts-registry.md` WHEN working with artifacts.json",
        "",
        artifacts_when,
        "",
    ])

    # Generate default artifacts.json using the new hierarchical format
    desired_registry = generate_default_registry(project_name, core_rel)

    desired_cfg = _default_project_config(core_rel, adapter_rel)

    actions: Dict[str, str] = {}
    errors: List[Dict[str, str]] = []
    backups: List[str] = []

    # Create backup of adapter directory before --force overwrites
    if args.force and adapter_dir.exists() and not args.dry_run:
        backup_path = create_backup(adapter_dir)
        if backup_path:
            backups.append(backup_path.as_posix())

    config_existed_before = config_path.exists()
    if config_existed_before and not config_path.is_file():
        errors.append({"path": config_path.as_posix(), "error": "CONFIG_PATH_NOT_A_FILE"})
    elif config_existed_before and not args.force:
        existing = _load_json_file(config_path)
        if not isinstance(existing, dict):
            errors.append({"path": config_path.as_posix(), "error": "CONFIG_INVALID_JSON"})
        else:
            merged = dict(existing)
            changed = False

            existing_core = merged.get("cypilotCorePath")
            if not (isinstance(existing_core, str) and existing_core.strip()):
                merged["cypilotCorePath"] = core_rel
                changed = True

            existing_adapter = merged.get("cypilotAdapterPath")
            if not (isinstance(existing_adapter, str) and existing_adapter.strip()):
                merged["cypilotAdapterPath"] = adapter_rel
                changed = True

            # If config is incomplete, fill in missing required keys instead of failing.
            if changed:
                desired_cfg = merged
                if not args.dry_run:
                    project_root.mkdir(parents=True, exist_ok=True)
                    _write_json_file(config_path, desired_cfg)
                actions["config"] = "updated"
            elif merged.get("cypilotCorePath") != core_rel or merged.get("cypilotAdapterPath") != adapter_rel:
                errors.append({"path": config_path.as_posix(), "error": "CONFIG_CONFLICT"})
            else:
                actions["config"] = "unchanged"
    else:
        if config_existed_before and args.force:
            existing = _load_json_file(config_path)
            if isinstance(existing, dict):
                merged = dict(existing)
                merged["cypilotCorePath"] = core_rel
                merged["cypilotAdapterPath"] = adapter_rel
                desired_cfg = merged
        if not args.dry_run:
            project_root.mkdir(parents=True, exist_ok=True)
            _write_json_file(config_path, desired_cfg)
        actions["config"] = "updated" if config_existed_before else "created"

    agents_path = (adapter_dir / "AGENTS.md").resolve()
    agents_existed_before = agents_path.exists()
    if agents_existed_before and not agents_path.is_file():
        errors.append({"path": agents_path.as_posix(), "error": "ADAPTER_AGENTS_NOT_A_FILE"})
    elif agents_existed_before and not args.force:
        try:
            old = agents_path.read_text(encoding="utf-8")
        except Exception:
            old = ""
        if old == desired_agents:
            actions["adapter_agents"] = "unchanged"
        else:
            # Non-destructive init: keep existing adapter AGENTS.md unless --force.
            actions["adapter_agents"] = "unchanged"
    else:
        if not args.dry_run:
            adapter_dir.mkdir(parents=True, exist_ok=True)
            agents_path.write_text(desired_agents, encoding="utf-8")
        actions["adapter_agents"] = "updated" if agents_existed_before else "created"

    registry_path = (adapter_dir / "artifacts.json").resolve()
    registry_existed_before = registry_path.exists()
    if registry_existed_before and not registry_path.is_file():
        errors.append({"path": registry_path.as_posix(), "error": "ARTIFACTS_REGISTRY_NOT_A_FILE"})
    elif registry_existed_before and not args.force:
        existing_reg = _load_json_file(registry_path)
        if existing_reg == desired_registry:
            actions["artifacts_registry"] = "unchanged"
        else:
            # Non-destructive init: keep existing artifacts.json unless --force.
            actions["artifacts_registry"] = "unchanged"
    else:
        if not args.dry_run:
            adapter_dir.mkdir(parents=True, exist_ok=True)
            _write_json_file(registry_path, desired_registry)
        actions["artifacts_registry"] = "updated" if registry_existed_before else "created"

    if errors:
        err_result: Dict[str, object] = {
            "status": "ERROR",
            "message": "Init failed",
            "project_root": project_root.as_posix(),
            "cypilot_root": cypilot_root.as_posix(),
            "config_path": config_path.as_posix(),
            "adapter_dir": adapter_dir.as_posix(),
            "dry_run": bool(args.dry_run),
            "errors": errors,
        }
        if backups:
            err_result["backups"] = backups
        print(json.dumps(err_result, indent=2, ensure_ascii=False))
        return 1

    result: Dict[str, object] = {
        "status": "PASS",
        "project_root": project_root.as_posix(),
        "cypilot_root": cypilot_root.as_posix(),
        "config_path": config_path.as_posix(),
        "adapter_dir": adapter_dir.as_posix(),
        "dry_run": bool(args.dry_run),
        "actions": actions,
    }
    if backups:
        result["backups"] = backups
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


# =============================================================================
def _cmd_validate(argv: List[str]) -> int:
    """Validate Cypilot artifacts and code traceability.

    Performs deterministic validation checks (structure, cross-references,
    task statuses, traceability markers) and produces a machine-readable report.
    """
    from .utils.template import cross_validate_artifacts
    from .utils.context import get_context
    p = argparse.ArgumentParser(
        prog="validate",
        description="Validate Cypilot artifacts and code traceability (structure + cross-refs + traceability)",
    )
    p.add_argument("--artifact", default=None, help="Path to specific Cypilot artifact (if omitted, validates all registered Cypilot artifacts)")
    p.add_argument("--skip-code", action="store_true", help="Skip code traceability validation")
    p.add_argument("--verbose", action="store_true", help="Print full validation report")
    p.add_argument("--output", default=None, help="Write report to file instead of stdout")
    args = p.parse_args(argv)

    # Use pre-loaded context (templates already loaded on startup)
    ctx = get_context()
    if not ctx:
        print(json.dumps({"status": "ERROR", "message": "No adapter found. Run 'init' first."}, indent=None, ensure_ascii=False))
        return 1

    meta = ctx.meta
    project_root = ctx.project_root
    registered_systems = ctx.registered_systems
    known_kinds = ctx.get_known_id_kinds()

    # Collect artifacts to validate: (artifact_path, template_path, artifact_type, traceability)
    artifacts_to_validate: List[Tuple[Path, Path, str, str]] = []

    if args.artifact:
        artifact_path = Path(args.artifact).resolve()
        if not artifact_path.exists():
            print(json.dumps({"status": "ERROR", "message": f"Artifact not found: {artifact_path}"}, indent=None, ensure_ascii=False))
            return 1
        try:
            rel_path = artifact_path.relative_to(project_root).as_posix()
        except ValueError:
            rel_path = None
        if rel_path:
            result = meta.get_artifact_by_path(rel_path)
            if result:
                artifact_meta, system_node = result
                pkg = meta.get_kit(system_node.kit)
                if pkg and pkg.is_cypilot_format():
                    template_path_str = pkg.get_template_path(artifact_meta.kind)
                    template_path = (project_root / template_path_str).resolve()
                    artifacts_to_validate.append((artifact_path, template_path, artifact_meta.kind, artifact_meta.traceability))
        if not artifacts_to_validate:
            print(json.dumps({"status": "ERROR", "message": f"Artifact not in Cypilot registry: {args.artifact}"}, indent=None, ensure_ascii=False))
            return 1
    else:
        # Validate all Cypilot artifacts
        for artifact_meta, system_node in meta.iter_all_artifacts():
            pkg = meta.get_kit(system_node.kit)
            if not pkg or not pkg.is_cypilot_format():
                continue
            template_path_str = pkg.get_template_path(artifact_meta.kind)
            artifact_path = (project_root / artifact_meta.path).resolve()
            template_path = (project_root / template_path_str).resolve()
            if artifact_path.exists():
                artifacts_to_validate.append((artifact_path, template_path, artifact_meta.kind, artifact_meta.traceability))

    if not artifacts_to_validate:
        print(json.dumps({"status": "ERROR", "message": "No Cypilot artifacts found in registry"}, indent=None, ensure_ascii=False))
        return 1

    # Validate each artifact
    all_errors: List[Dict[str, object]] = []
    all_warnings: List[Dict[str, object]] = []
    artifact_reports: List[Dict[str, object]] = []
    parsed_artifacts: List[TemplateArtifact] = []

    for artifact_path, template_path, artifact_type, traceability in artifacts_to_validate:
        # Use pre-loaded template from context if available
        used_synthetic_template = False
        tmpl = ctx.get_template_for_kind(artifact_type)
        if tmpl is None:
            if template_path.exists():
                # Fallback: load from disk
                tmpl, tmpl_errs = Template.from_path(template_path)
                if tmpl_errs or tmpl is None:
                    all_errors.append({
                        "type": "template",
                        "message": f"Failed to load template for {artifact_type}",
                        "artifact": str(artifact_path),
                        "template": str(template_path),
                        "errors": tmpl_errs,
                    })
                    continue
            else:
                tmpl = Template(
                    path=Path("<synthetic-template>"),
                    kind=str(artifact_type),
                    version=None,
                    policy=None,
                    blocks=[],
                    _loaded=True,
                )
                used_synthetic_template = True

        from .utils.document import file_has_cypilot_markers

        is_markerless = used_synthetic_template or (not file_has_cypilot_markers(artifact_path))
        artifact: TemplateArtifact = tmpl.parse(artifact_path)
        parsed_artifacts.append(artifact)

        # Structure validation
        # If artifact has no `<!-- cpt:... -->` markers, skip template-structure validation
        # and rely on markerless checks + cross-artifact consistency.
        if is_markerless:
            errors = []
            warnings = []
        else:
            result = artifact.validate()
            errors = result.get("errors", [])
            warnings = result.get("warnings", [])

        artifact_report: Dict[str, object] = {
            "artifact": str(artifact_path),
            "artifact_type": artifact_type,
            "traceability": traceability,
            "status": "PASS" if not errors else "FAIL",
            "error_count": len(errors),
            "warning_count": len(warnings),
        }

        if args.verbose:
            artifact_report["errors"] = errors
            artifact_report["warnings"] = warnings
            artifact_report["id_definitions"] = len(artifact.id_definitions)
            artifact_report["id_references"] = len(artifact.id_references)

        artifact_reports.append(artifact_report)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    # Cross-reference validation - load ALL Cypilot artifacts for context
    # When validating a single artifact, we still need all artifacts to check references
    all_artifacts_for_cross: List[TemplateArtifact] = list(parsed_artifacts)
    validated_paths = {str(p) for p, _, _, _ in artifacts_to_validate}

    # Load remaining artifacts that weren't validated (for cross-reference context)
    for artifact_meta, system_node in meta.iter_all_artifacts():
        pkg = meta.get_kit(system_node.kit)
        if not pkg or not pkg.is_cypilot_format():
            continue
        art_path = (project_root / artifact_meta.path).resolve()
        if str(art_path) in validated_paths:
            continue  # Already parsed
        if not art_path.exists():
            continue
        tmpl = ctx.get_template_for_kind(artifact_meta.kind)
        if tmpl is None:
            tmpl = Template(
                path=Path("<synthetic-template>"),
                kind=str(artifact_meta.kind),
                version=None,
                policy=None,
                blocks=[],
                _loaded=True,
            )
        try:
            art = tmpl.parse(art_path)
            all_artifacts_for_cross.append(art)
        except Exception:
            pass  # Silently skip unparseable artifacts for cross-ref

    if len(all_artifacts_for_cross) > 0:
        cross_result = cross_validate_artifacts(all_artifacts_for_cross, registered_systems=registered_systems, known_kinds=known_kinds)
        cross_errors = cross_result.get("errors", [])
        cross_warnings = cross_result.get("warnings", [])
        # Only include cross-ref errors for artifacts we're validating
        for err in cross_errors:
            err_path = err.get("path", "")
            if err_path in validated_paths:
                all_errors.append(err)
        for warn in cross_warnings:
            warn_path = warn.get("path", "")
            if warn_path in validated_paths:
                all_warnings.append(warn)

    # Code traceability validation (unless skipped)
    code_files_scanned: List[Dict[str, object]] = []
    parsed_code_files: List[CodeFile] = []
    code_ids_found: Set[str] = set()
    to_code_ids: Set[str] = set()
    artifact_ids: Set[str] = set()
    markerless_full_ids_to_check: Set[str] = set()

    # Build map of artifact path to traceability mode
    traceability_by_path: Dict[str, str] = {}
    for artifact_path, _template_path, _artifact_type, traceability in artifacts_to_validate:
        traceability_by_path[str(artifact_path)] = traceability

    from .utils.document import (
        file_has_cypilot_markers,
        scan_cdsl_instructions_without_markers,
        scan_cpt_ids_without_markers,
    )

    # Determine which markerless FULL-traceability IDs we might accept references from code for.
    for artifact_path, _template_path, artifact_kind, traceability in artifacts_to_validate:
        if traceability != "FULL":
            continue
        if file_has_cypilot_markers(artifact_path):
            continue
        for h in scan_cpt_ids_without_markers(artifact_path):
            if h.get("type") == "definition" and h.get("id"):
                markerless_full_ids_to_check.add(str(h["id"]))

    strict_code_validation = not args.artifact
    should_scan_code = (not args.skip_code) and (strict_code_validation or bool(markerless_full_ids_to_check))

    if strict_code_validation and len(all_artifacts_for_cross) > 0:
        # Build complete set of defined artifact IDs (including markerless) for orphan checks.
        for art in all_artifacts_for_cross:
            if file_has_cypilot_markers(art.path):
                art._extract_ids_and_refs()
                for d in art.id_definitions:
                    artifact_ids.add(d.id)
                    art_traceability = traceability_by_path.get(str(art.path), "FULL")
                    if d.to_code and art_traceability == "FULL":
                        to_code_ids.add(d.id)
            else:
                for h in scan_cpt_ids_without_markers(art.path):
                    if h.get("type") == "definition" and h.get("id"):
                        artifact_ids.add(str(h["id"]))

    if should_scan_code:
        # Scan code files from all systems
        def resolve_code_path(p: str) -> Path:
            return (project_root / p).resolve()

        def scan_codebase_entry(entry: dict, traceability: str) -> None:
            code_path = resolve_code_path(entry.get("path", ""))
            extensions = entry.get("extensions", [".py"])

            if not code_path.exists():
                return

            if code_path.is_file():
                files_to_scan = [code_path]
            else:
                files_to_scan = []
                for ext in extensions:
                    files_to_scan.extend(code_path.rglob(f"*{ext}"))

            for file_path in files_to_scan:
                cf, errs = CodeFile.from_path(file_path)
                if errs or cf is None:
                    if strict_code_validation and errs:
                        all_errors.extend(errs)
                    continue

                parsed_code_files.append(cf)

                if strict_code_validation:
                    # Validate structure
                    result = cf.validate()
                    all_errors.extend(result.get("errors", []))
                    all_warnings.extend(result.get("warnings", []))

                # Track IDs found
                file_ids = cf.list_ids()
                code_ids_found.update(file_ids)

                if file_ids or cf.scope_markers or cf.block_markers:
                    code_files_scanned.append({
                        "path": str(file_path),
                        "scope_markers": len(cf.scope_markers),
                        "block_markers": len(cf.block_markers),
                        "ids_referenced": len(file_ids),
                    })

                if strict_code_validation:
                    # Check for orphaned markers (IDs not in artifacts)
                    if traceability == "FULL":
                        for ref in cf.references:
                            if ref.id not in artifact_ids:
                                all_errors.append({
                                    "type": "traceability",
                                    "message": "Code marker references ID not defined in any artifact",
                                    "path": str(file_path),
                                    "line": ref.line,
                                    "id": ref.id,
                                })

        def scan_system_codebase(system_node: "SystemNode") -> None:
            for cb_entry in system_node.codebase:
                # Determine traceability from system artifacts
                traceability = "FULL"
                for art in system_node.artifacts:
                    if art.traceability == "DOCS-ONLY":
                        traceability = "DOCS-ONLY"
                        break
                scan_codebase_entry({
                    "path": cb_entry.path,
                    "extensions": cb_entry.extensions,
                }, traceability)
            for child in system_node.children:
                scan_system_codebase(child)

        for system_node in meta.systems:
            scan_system_codebase(system_node)

        if strict_code_validation:
            # Check for missing code markers (to_code IDs without markers)
            missing_ids = to_code_ids - code_ids_found
            for missing_id in sorted(missing_ids):
                all_errors.append({
                    "type": "coverage",
                    "message": "ID marked to_code=\"true\" has no code marker",
                    "id": missing_id,
                })

            # CDSL instruction-level coverage:
            # For each checked ([x]) CDSL instruction under a to_code="true" ID in FULL traceability,
            # require a code block marker pair: @cpt-begin:{id}:p{phase}:inst-{inst} ... @cpt-end...
            code_block_keys: Set[Tuple[str, int, str]] = set()
            for cf in parsed_code_files:
                for bm in cf.block_markers:
                    code_block_keys.add((bm.id, int(bm.phase), str(bm.inst)))

            def find_parent_id_def(
                defs: List[object],
                line_no: int,
            ) -> Optional[object]:
                candidates = []
                for d in defs:
                    blk = getattr(d, "block", None)
                    if not blk:
                        continue
                    if blk.start_line <= line_no <= blk.end_line:
                        candidates.append(d)
                if not candidates:
                    return None
                # Choose the tightest enclosing block.
                candidates.sort(key=lambda x: (x.block.end_line - x.block.start_line))
                return candidates[0]

            for art in all_artifacts_for_cross:
                art_path_str = str(art.path)
                art_traceability = traceability_by_path.get(art_path_str, "FULL")
                if art_traceability != "FULL":
                    continue
                if not file_has_cypilot_markers(art.path):
                    continue

                art._extract_ids_and_refs()
                for inst in getattr(art, "cdsl_instructions", []) or []:
                    if not getattr(inst, "checked", False):
                        continue
                    phase = getattr(inst, "phase", None)
                    if phase is None:
                        continue

                    parent = find_parent_id_def(art.id_definitions, int(getattr(inst, "line", 1) or 1))
                    if parent is None:
                        continue
                    if not getattr(parent, "to_code", False):
                        continue

                    key = (str(parent.id), int(phase), str(getattr(inst, "inst", "")))
                    if key in code_block_keys:
                        continue

                    all_errors.append({
                        "type": "coverage",
                        "message": "Implemented CDSL instruction has no code block marker",
                        "artifact": art_path_str,
                        "line": int(getattr(inst, "line", 1) or 1),
                        "id": str(parent.id),
                        "phase": int(phase),
                        "inst": f"inst-{getattr(inst, 'inst', '')}",
                    })

            # Markerless artifacts: best-effort scan for CDSL instructions by regex.
            # Parent binding rule: nearest ID definition above the instruction.
            for art in all_artifacts_for_cross:
                art_path_str = str(art.path)
                art_traceability = traceability_by_path.get(art_path_str, "FULL")
                if art_traceability != "FULL":
                    continue
                if file_has_cypilot_markers(art.path):
                    continue

                for h in scan_cdsl_instructions_without_markers(art.path):
                    if not bool(h.get("checked", False)):
                        continue
                    parent_id = str(h.get("parent_id") or "").strip()
                    if not parent_id:
                        continue
                    phase = h.get("phase")
                    inst = str(h.get("inst") or "").strip()
                    if phase is None or not inst:
                        continue

                    key = (parent_id, int(phase), inst)
                    if key in code_block_keys:
                        continue

                    all_errors.append({
                        "type": "coverage",
                        "message": "Implemented CDSL instruction has no code block marker",
                        "artifact": art_path_str,
                        "line": int(h.get("line", 1) or 1),
                        "id": parent_id,
                        "phase": int(phase),
                        "inst": f"inst-{inst}",
                    })

    # Markerless covered-by (simplified):
    # If an artifact has no markers, each `**ID**: ...` definition must be referenced
    # from at least one OTHER artifact kind. If no other kinds exist in scope → warn.
    #
    # If traceability is FULL for this artifact, a code reference also satisfies coverage.
    if len(all_artifacts_for_cross) > 0:
        present_kinds: Set[str] = set()
        refs_by_id: Dict[str, Set[str]] = {}

        # Build reference index across ALL artifacts (including markerless).
        for art in all_artifacts_for_cross:
            kind = art.template.kind
            present_kinds.add(kind)

            if not file_has_cypilot_markers(art.path):
                for h in scan_cpt_ids_without_markers(art.path):
                    if h.get("type") != "reference":
                        continue
                    rid = str(h.get("id", "")).strip()
                    if not rid:
                        continue
                    refs_by_id.setdefault(rid, set()).add(kind)
                continue

            art._extract_ids_and_refs()
            for r in art.id_references:
                refs_by_id.setdefault(r.id, set()).add(kind)

        # Enforce rule for validated markerless artifacts.
        for art in all_artifacts_for_cross:
            art_path_str = str(art.path)
            if art_path_str not in validated_paths:
                continue
            if file_has_cypilot_markers(art.path):
                continue

            kind = art.template.kind
            other_kinds = sorted(k for k in present_kinds if k != kind)
            art_traceability = traceability_by_path.get(art_path_str, "FULL")

            for h in scan_cpt_ids_without_markers(art.path):
                if h.get("type") != "definition":
                    continue
                did = str(h.get("id", "")).strip()
                if not did:
                    continue
                line = int(h.get("line", 1) or 1)

                if not other_kinds:
                    all_warnings.append(Template.error(
                        "structure",
                        "ID not referenced (no other artifact kinds in scope)",
                        path=art.path,
                        line=line,
                        id=did,
                    ))
                    continue

                referenced_kinds = sorted(k for k in refs_by_id.get(did, set()) if k != kind)
                if referenced_kinds:
                    continue

                # Allow code reference to satisfy coverage when FULL.
                if art_traceability == "FULL" and did in code_ids_found:
                    continue

                all_errors.append(Template.error(
                    "structure",
                    "ID not referenced from other artifact kinds",
                    path=art.path,
                    line=line,
                    id=did,
                    other_kinds=other_kinds,
                ))

    # Build final report
    overall_status = "PASS" if not all_errors else "FAIL"

    report: Dict[str, object] = {
        "status": overall_status,
        "artifacts_validated": len(artifact_reports),
        "error_count": len(all_errors),
        "warning_count": len(all_warnings),
    }

    # Add code validation stats if code was validated
    if not args.skip_code and not args.artifact:
        report["code_files_scanned"] = len(code_files_scanned)
        report["to_code_ids_total"] = len(to_code_ids)
        report["code_ids_found"] = len(code_ids_found)
        if to_code_ids:
            report["coverage"] = f"{len(code_ids_found & to_code_ids)}/{len(to_code_ids)}"

    # Add next step hint for agent
    if overall_status == "PASS":
        report["next_step"] = "Deterministic validation passed. Now perform semantic validation: review content quality against checklist.md criteria."

    if args.verbose:
        report["artifacts"] = artifact_reports
        report["errors"] = all_errors
        report["warnings"] = all_warnings
    else:
        # Compact summary
        if all_errors:
            report["errors"] = all_errors[:20]  # Limit for readability
            if len(all_errors) > 20:
                report["errors_truncated"] = len(all_errors) - 20

        failed_artifacts = [r for r in artifact_reports if r.get("status") == "FAIL"]
        if failed_artifacts:
            report["failed_artifacts"] = [
                {"artifact": r.get("artifact"), "error_count": r.get("error_count")}
                for r in failed_artifacts
            ]

    out = json.dumps(report, indent=2 if args.verbose else None, ensure_ascii=False)
    if args.verbose:
        out += "\n"

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)

    return 0 if overall_status == "PASS" else 2


# =============================================================================
# SEARCH COMMANDS
# =============================================================================

def _cmd_list_ids(argv: List[str]) -> int:
    """List Cypilot IDs from artifacts using template-based parsing.

    If no artifact is specified, scans all Cypilot-format artifacts from the adapter registry.
    """
    p = argparse.ArgumentParser(prog="list-ids")
    p.add_argument("--artifact", default=None, help="Path to Cypilot artifact file (if omitted, scans all registered Cypilot artifacts)")
    p.add_argument("--pattern", default=None, help="Filter IDs by substring or regex pattern")
    p.add_argument("--regex", action="store_true", help="Treat pattern as regular expression")
    p.add_argument("--kind", default=None, help="Filter by ID kind from template markers (e.g., 'requirement', 'spec')")
    p.add_argument("--all", action="store_true", help="Include duplicate IDs in results")
    p.add_argument("--include-code", action="store_true", help="Also scan code files for Cypilot marker references")
    args = p.parse_args(argv)

    # Collect artifacts to scan: (artifact_path, template, artifact_kind)
    artifacts_to_scan: List[Tuple[Path, Template, str]] = []
    ctx = None

    if args.artifact:
        # Single artifact specified - find context from artifact's location
        artifact_path = Path(args.artifact).resolve()
        if not artifact_path.exists():
            print(json.dumps({"status": "ERROR", "message": f"Artifact not found: {artifact_path}"}, indent=None, ensure_ascii=False))
            return 1

        from .utils.context import CypilotContext
        ctx = CypilotContext.load(artifact_path.parent)
        if not ctx:
            print(json.dumps({"status": "ERROR", "message": "No adapter found. Run 'init' first or specify --artifact."}, indent=None, ensure_ascii=False))
            return 1

        project_root = ctx.project_root
        meta = ctx.meta

        # Find artifact in registry
        try:
            rel_path = artifact_path.relative_to(project_root).as_posix()
        except ValueError:
            rel_path = None

        if rel_path:
            result = meta.get_artifact_by_path(rel_path)
            if result:
                artifact_meta, system_node = result
                tmpl = ctx.get_template(system_node.kit, artifact_meta.kind)
                if tmpl:
                    artifacts_to_scan.append((artifact_path, tmpl, artifact_meta.kind))

        if not artifacts_to_scan:
            print(json.dumps({"status": "ERROR", "message": "Could not find template for artifact. Ensure artifact is registered in adapter."}, indent=None, ensure_ascii=False))
            return 1
    else:
        # No artifact specified - use global context from cwd
        from .utils.context import get_context
        ctx = get_context()
        if not ctx:
            print(json.dumps({"status": "ERROR", "message": "No adapter found. Run 'init' first or specify --artifact."}, indent=None, ensure_ascii=False))
            return 1

        meta = ctx.meta
        project_root = ctx.project_root

        for artifact_meta, system_node in meta.iter_all_artifacts():
            tmpl = ctx.get_template(system_node.kit, artifact_meta.kind)
            if not tmpl:
                continue
            artifact_path = (project_root / artifact_meta.path).resolve()
            if artifact_path.exists():
                artifacts_to_scan.append((artifact_path, tmpl, artifact_meta.kind))

        if not artifacts_to_scan:
            print(json.dumps({"status": "ERROR", "message": "No Cypilot-format artifacts found in registry."}, indent=None, ensure_ascii=False))
            return 1

    # Parse artifacts and collect IDs
    hits: List[Dict[str, object]] = []

    for artifact_path, tmpl, artifact_type in artifacts_to_scan:
        from .utils.document import scan_cpt_ids_without_markers

        fallback_hits = scan_cpt_ids_without_markers(artifact_path)
        if fallback_hits:
            for fh in fallback_hits:
                h: Dict[str, object] = {
                    "id": fh.get("id"),
                    "kind": None,
                    "type": fh.get("type"),
                    "artifact_type": artifact_type,
                    "line": fh.get("line"),
                    "artifact": str(artifact_path),
                    "checked": bool(fh.get("checked", False)),
                }
                if fh.get("priority") is not None:
                    h["priority"] = fh.get("priority")
                hits.append(h)
            continue

        parsed: TemplateArtifact = tmpl.parse(artifact_path)
        parsed._extract_ids_and_refs()  # Populate id_definitions and id_references

        # Collect ID definitions
        for id_def in parsed.id_definitions:
            block_kind = id_def.block.template_block.name if id_def.block else None
            h = {
                "id": id_def.id,
                "kind": block_kind,
                "type": "definition",
                "artifact_type": artifact_type,
                "line": id_def.line,
                "artifact": str(artifact_path),
                "checked": id_def.checked,
            }
            if id_def.priority:
                h["priority"] = id_def.priority
            hits.append(h)

        # Collect ID references
        for id_ref in parsed.id_references:
            block_kind = id_ref.block.template_block.name if id_ref.block else None
            h = {
                "id": id_ref.id,
                "kind": block_kind,
                "type": "reference",
                "artifact_type": artifact_type,
                "line": id_ref.line,
                "artifact": str(artifact_path),
                "checked": id_ref.checked,
            }
            if id_ref.priority:
                h["priority"] = id_ref.priority
            hits.append(h)

    # Scan code files if requested
    code_files_scanned = 0
    if args.include_code and not args.artifact and ctx:
        # Scan codebase entries from context
        for cb_entry, system_node in ctx.meta.iter_all_codebase():
            code_path = (ctx.project_root / cb_entry.path).resolve()
            extensions = cb_entry.extensions or [".py"]

            if not code_path.exists():
                continue

            if code_path.is_file():
                files = [code_path]
            else:
                files = []
                for ext in extensions:
                    files.extend(code_path.rglob(f"*{ext}"))

            for file_path in files:
                cf, errs = CodeFile.from_path(file_path)
                if errs or cf is None:
                    continue

                code_files_scanned += 1

                # Add code references
                for ref in cf.references:
                    h: Dict[str, object] = {
                        "id": ref.id,
                        "kind": ref.kind or "code",
                        "type": "code_reference",
                        "artifact_type": "CODE",
                        "line": ref.line,
                        "artifact": str(file_path),
                        "marker_type": ref.marker_type,
                    }
                    if ref.phase is not None:
                        h["phase"] = ref.phase
                    if ref.inst:
                        h["inst"] = ref.inst
                    hits.append(h)

    # Apply filters
    if args.kind:
        kind_filter = str(args.kind)
        hits = [h for h in hits if str(h.get("kind", "")) == kind_filter]

    if args.pattern:
        pat = str(args.pattern)
        if args.regex:
            rx = re.compile(pat)
            hits = [h for h in hits if rx.search(str(h.get("id", ""))) is not None]
        else:
            hits = [h for h in hits if pat in str(h.get("id", ""))]

    if not args.all:
        seen: Set[str] = set()
        uniq: List[Dict[str, object]] = []
        for h in hits:
            id_val = str(h.get("id", ""))
            if id_val in seen:
                continue
            seen.add(id_val)
            uniq.append(h)
        hits = uniq

    hits = sorted(hits, key=lambda h: (str(h.get("id", "")), int(h.get("line", 0))))

    result: Dict[str, object] = {
        "count": len(hits),
        "artifacts_scanned": len(artifacts_to_scan),
        "ids": hits
    }
    if code_files_scanned > 0:
        result["code_files_scanned"] = code_files_scanned

    print(json.dumps(result, indent=None, ensure_ascii=False))
    return 0


def _cmd_list_id_kinds(argv: List[str]) -> int:
    """List ID kinds that actually exist in artifacts.

    Parses artifacts against their templates and returns only kinds
    that have at least one ID definition in the artifact(s).
    """
    p = argparse.ArgumentParser(prog="list-id-kinds", description="List ID kinds found in Cypilot artifacts")
    p.add_argument("--artifact", default=None, help="Scan specific artifact (if omitted, scans all registered Cypilot artifacts)")
    args = p.parse_args(argv)

    # Find adapter and load registry
    adapter_dir = find_adapter_directory(Path.cwd())
    if not adapter_dir:
        print(json.dumps({"status": "ERROR", "message": "No adapter found. Run 'init' first."}, indent=None, ensure_ascii=False))
        return 1

    registry, reg_err = load_artifacts_registry(adapter_dir)
    if not registry or reg_err:
        print(json.dumps({"status": "ERROR", "message": reg_err or "Could not load artifacts.json"}, indent=None, ensure_ascii=False))
        return 1

    from .utils.artifacts_meta import ArtifactsMeta
    meta = ArtifactsMeta.from_dict(registry)
    project_root = (adapter_dir / meta.project_root).resolve()

    # Collect artifacts to scan: (artifact_path, template_path, artifact_type)
    artifacts_to_scan: List[Tuple[Path, Path, str]] = []

    if args.artifact:
        artifact_path = Path(args.artifact).resolve()
        if not artifact_path.exists():
            print(json.dumps({"status": "ERROR", "message": f"Artifact not found: {artifact_path}"}, indent=None, ensure_ascii=False))
            return 1

        try:
            rel_path = artifact_path.relative_to(project_root).as_posix()
        except ValueError:
            rel_path = None

        if rel_path:
            result = meta.get_artifact_by_path(rel_path)
            if result:
                artifact_meta, system_node = result
                pkg = meta.get_kit(system_node.kit)
                if pkg and pkg.is_cypilot_format():
                    template_path_str = pkg.get_template_path(artifact_meta.kind)
                    template_path = (project_root / template_path_str).resolve()
                    if not template_path.exists():
                        if template_path_str.startswith("kits/"):
                            alt = "rules/" + template_path_str[len("kits/"):]
                            alt_path = (project_root / alt).resolve()
                            if alt_path.exists():
                                template_path = alt_path
                        elif template_path_str.startswith("kits/"):
                            alt = "rules/" + template_path_str[len("kits/"):]
                            alt_path = (project_root / alt).resolve()
                            if alt_path.exists():
                                template_path = alt_path
                    artifacts_to_scan.append((artifact_path, template_path, artifact_meta.kind))

        if not artifacts_to_scan:
            print(json.dumps({"status": "ERROR", "message": f"Artifact not found in registry: {args.artifact}"}, indent=None, ensure_ascii=False))
            return 1
    else:
        # Scan all Cypilot artifacts
        for artifact_meta, system_node in meta.iter_all_artifacts():
            pkg = meta.get_kit(system_node.kit)
            if not pkg or not pkg.is_cypilot_format():
                continue
            template_path_str = pkg.get_template_path(artifact_meta.kind)
            artifact_path = (project_root / artifact_meta.path).resolve()
            template_path = (project_root / template_path_str).resolve()
            if not template_path.exists():
                if template_path_str.startswith("kits/"):
                    alt = "rules/" + template_path_str[len("kits/"):]
                    alt_path = (project_root / alt).resolve()
                    if alt_path.exists():
                        template_path = alt_path
                elif template_path_str.startswith("kits/"):
                    alt = "rules/" + template_path_str[len("kits/"):]
                    alt_path = (project_root / alt).resolve()
                    if alt_path.exists():
                        template_path = alt_path
            if artifact_path.exists():
                artifacts_to_scan.append((artifact_path, template_path, artifact_meta.kind))

        if not artifacts_to_scan:
            print(json.dumps({"status": "ERROR", "message": "No Cypilot-format artifacts found in registry."}, indent=None, ensure_ascii=False))
            return 1

    # Parse artifacts and collect kinds that have actual IDs
    template_to_kinds: Dict[str, Set[str]] = {}
    kind_to_templates: Dict[str, Set[str]] = {}
    kind_counts: Dict[str, int] = {}

    for artifact_path, template_path, artifact_type in artifacts_to_scan:
        if template_path.exists():
            tmpl, errs = Template.from_path(template_path)
            if errs or tmpl is None:
                continue
        else:
            tmpl = Template(
                path=Path("<synthetic-template>"),
                kind=str(artifact_type),
                version=None,
                policy=None,
                blocks=[],
                _loaded=True,
            )

        parsed: TemplateArtifact = tmpl.parse(artifact_path)
        parsed._extract_ids_and_refs()  # Populate id_definitions

        # Collect kinds from actual ID definitions in artifact
        for id_def in parsed.id_definitions:
            if id_def.block:
                kind_name = id_def.block.template_block.name
                # Track kind -> templates
                if kind_name not in kind_to_templates:
                    kind_to_templates[kind_name] = set()
                kind_to_templates[kind_name].add(artifact_type)
                # Track template -> kinds
                if artifact_type not in template_to_kinds:
                    template_to_kinds[artifact_type] = set()
                template_to_kinds[artifact_type].add(kind_name)
                # Count
                kind_counts[kind_name] = kind_counts.get(kind_name, 0) + 1

    # Build output
    all_kinds = sorted(kind_to_templates.keys())

    if args.artifact and artifacts_to_scan:
        artifact_path, _, artifact_type = artifacts_to_scan[0]
        kinds_in_artifact = sorted(template_to_kinds.get(artifact_type, set()))
        print(json.dumps({
            "artifact": str(artifact_path),
            "artifact_type": artifact_type,
            "kinds": kinds_in_artifact,
            "kind_counts": {k: kind_counts.get(k, 0) for k in kinds_in_artifact},
        }, indent=None, ensure_ascii=False))
    else:
        print(json.dumps({
            "kinds": all_kinds,
            "kind_counts": {k: kind_counts.get(k, 0) for k in all_kinds},
            "kind_to_templates": {k: sorted(v) for k, v in sorted(kind_to_templates.items())},
            "template_to_kinds": {k: sorted(v) for k, v in sorted(template_to_kinds.items())},
            "artifacts_scanned": len(artifacts_to_scan),
        }, indent=None, ensure_ascii=False))
    return 0


def _cmd_get_content(argv: List[str]) -> int:
    """Get content block for a specific Cypilot ID using template-based parsing."""
    p = argparse.ArgumentParser(prog="get-content", description="Get content block for a specific Cypilot ID")
    p.add_argument("--artifact", default=None, help="Path to Cypilot artifact file")
    p.add_argument("--code", default=None, help="Path to code file (alternative to --artifact)")
    p.add_argument("--id", required=True, help="Cypilot ID to retrieve content for")
    p.add_argument("--inst", default=None, help="Instruction ID for code blocks (e.g., 'inst-validate-input')")
    args = p.parse_args(argv)

    # Handle code file path
    if args.code:
        code_path = Path(args.code).resolve()
        if not code_path.is_file():
            print(json.dumps({"status": "ERROR", "message": f"Code file not found: {code_path}"}, indent=None, ensure_ascii=False))
            return 1

        cf, errs = CodeFile.from_path(code_path)
        if errs or cf is None:
            print(json.dumps({"status": "ERROR", "message": f"Failed to parse code file: {errs}"}, indent=None, ensure_ascii=False))
            return 1

        # Try to get content by ID or inst
        content = None
        if args.inst:
            content = cf.get_by_inst(args.inst)
        if content is None:
            content = cf.get(args.id)

        if content is None:
            print(json.dumps({"status": "NOT_FOUND", "id": args.id, "inst": args.inst}, indent=None, ensure_ascii=False))
            return 2

        print(json.dumps({"status": "FOUND", "id": args.id, "inst": args.inst, "text": content}, indent=None, ensure_ascii=False))
        return 0

    # Handle artifact path
    if not args.artifact:
        print(json.dumps({"status": "ERROR", "message": "Either --artifact or --code must be specified"}, indent=None, ensure_ascii=False))
        return 1

    artifact_path = Path(args.artifact).resolve()
    if not artifact_path.is_file():
        print(json.dumps({"status": "ERROR", "message": f"Artifact not found: {artifact_path}"}, indent=None, ensure_ascii=False))
        return 1

    # Load CypilotContext from artifact's location
    from .utils.context import CypilotContext
    ctx = CypilotContext.load(artifact_path.parent)
    if not ctx:
        print(json.dumps({"status": "ERROR", "message": "No adapter found"}, indent=None, ensure_ascii=False))
        return 1

    meta = ctx.meta
    project_root = ctx.project_root

    # Find artifact in registry to get its template
    try:
        rel_path = artifact_path.relative_to(project_root).as_posix()
    except ValueError:
        print(json.dumps({"status": "ERROR", "message": f"Artifact not under project root: {artifact_path}"}, indent=None, ensure_ascii=False))
        return 1

    artifact_entry = meta.get_artifact_by_path(rel_path)
    if artifact_entry is None:
        print(json.dumps({"status": "ERROR", "message": f"Artifact not registered: {rel_path}"}, indent=None, ensure_ascii=False))
        return 1

    artifact_meta, system = artifact_entry
    tmpl = ctx.get_template(system.kit, artifact_meta.kind)
    if tmpl is None:
        tmpl = Template(
            path=Path("<synthetic-template>"),
            kind=str(artifact_meta.kind),
            version=None,
            policy=None,
            blocks=[],
            _loaded=True,
        )

    # Parse artifact using pre-loaded template
    artifact = tmpl.parse(artifact_path)
    result = artifact.get_with_location(args.id)

    if result is None:
        # Fallback: artifacts without `<!-- cpt:... -->` markers can still provide
        # content via scope markup (see utils.document.get_content_scoped_without_markers).
        from .utils.document import get_content_scoped_without_markers

        fallback = get_content_scoped_without_markers(artifact_path, id_value=args.id)
        if fallback is None:
            print(json.dumps({"status": "NOT_FOUND", "id": args.id}, indent=None, ensure_ascii=False))
            return 2
        result = fallback

    text, start_line, end_line = result
    print(json.dumps({
        "status": "FOUND",
        "id": args.id,
        "text": text,
        "artifact": str(artifact_path),
        "start_line": start_line,
        "end_line": end_line,
        "kind": artifact_meta.kind,
        "system": system.name,
        "traceability": artifact_meta.traceability,
    }, indent=None, ensure_ascii=False))
    return 0


def _cmd_where_defined(argv: List[str]) -> int:
    """Find where an Cypilot ID is defined using template-based parsing."""
    p = argparse.ArgumentParser(prog="where-defined", description="Find where an Cypilot ID is defined")
    p.add_argument("--id", required=True, help="Cypilot ID to find definition for")
    p.add_argument("--artifact", default=None, help="Limit search to specific artifact (optional)")
    args = p.parse_args(argv)

    target_id = str(args.id).strip()
    if not target_id:
        print(json.dumps({"status": "ERROR", "message": "ID cannot be empty"}, indent=None, ensure_ascii=False))
        return 1

    # Collect artifacts to scan: (artifact_path, template, artifact_kind)
    artifacts_to_scan: List[Tuple[Path, Template, str]] = []

    if args.artifact:
        # Load context from artifact's location
        artifact_path = Path(args.artifact).resolve()
        if not artifact_path.exists():
            print(json.dumps({"status": "ERROR", "message": f"Artifact not found: {artifact_path}"}, indent=None, ensure_ascii=False))
            return 1

        from .utils.context import CypilotContext
        ctx = CypilotContext.load(artifact_path.parent)
        if not ctx:
            print(json.dumps({"status": "ERROR", "message": "No adapter found. Run 'init' first."}, indent=None, ensure_ascii=False))
            return 1

        meta = ctx.meta
        project_root = ctx.project_root

        try:
            rel_path = artifact_path.relative_to(project_root).as_posix()
        except ValueError:
            rel_path = None
        if rel_path:
            result = meta.get_artifact_by_path(rel_path)
            if result:
                artifact_meta, system_node = result
                tmpl = ctx.get_template(system_node.kit, artifact_meta.kind)
                if tmpl is None:
                    tmpl = Template(
                        path=Path("<synthetic-template>"),
                        kind=str(artifact_meta.kind),
                        version=None,
                        policy=None,
                        blocks=[],
                        _loaded=True,
                    )
                artifacts_to_scan.append((artifact_path, tmpl, artifact_meta.kind))
        if not artifacts_to_scan:
            print(json.dumps({"status": "ERROR", "message": f"Artifact not in Cypilot registry: {args.artifact}"}, indent=None, ensure_ascii=False))
            return 1
    else:
        # Use global context
        from .utils.context import get_context
        ctx = get_context()
        if not ctx:
            print(json.dumps({"status": "ERROR", "message": "No adapter found. Run 'init' first."}, indent=None, ensure_ascii=False))
            return 1

        meta = ctx.meta
        project_root = ctx.project_root

        # Scan all Cypilot artifacts
        for artifact_meta, system_node in meta.iter_all_artifacts():
            tmpl = ctx.get_template(system_node.kit, artifact_meta.kind)
            if tmpl is None:
                tmpl = Template(
                    path=Path("<synthetic-template>"),
                    kind=str(artifact_meta.kind),
                    version=None,
                    policy=None,
                    blocks=[],
                    _loaded=True,
                )
            artifact_path = (project_root / artifact_meta.path).resolve()
            if artifact_path.exists():
                artifacts_to_scan.append((artifact_path, tmpl, artifact_meta.kind))

    if not artifacts_to_scan:
        print(json.dumps({"status": "ERROR", "message": "No Cypilot artifacts found in registry"}, indent=None, ensure_ascii=False))
        return 1

    # Search for definitions
    definitions: List[Dict[str, object]] = []

    for artifact_path, tmpl, artifact_type in artifacts_to_scan:
        parsed: TemplateArtifact = tmpl.parse(artifact_path)
        parsed._extract_ids_and_refs()  # Populate id_definitions

        for id_def in parsed.id_definitions:
            if id_def.id == target_id:
                block_kind = id_def.block.template_block.name if id_def.block else None
                definitions.append({
                    "artifact": str(artifact_path),
                    "artifact_type": artifact_type,
                    "line": id_def.line,
                    "kind": block_kind,
                    "checked": id_def.checked,
                })

    if not definitions:
        print(json.dumps({
            "status": "NOT_FOUND",
            "id": target_id,
            "artifacts_scanned": len(artifacts_to_scan),
            "count": 0,
            "definitions": [],
        }, indent=None, ensure_ascii=False))
        return 2

    status = "FOUND" if len(definitions) == 1 else "AMBIGUOUS"
    print(json.dumps({
        "status": status,
        "id": target_id,
        "artifacts_scanned": len(artifacts_to_scan),
        "count": len(definitions),
        "definitions": definitions,
    }, indent=None, ensure_ascii=False))
    return 0 if status == "FOUND" else 2


def _cmd_where_used(argv: List[str]) -> int:
    """Find all references to an Cypilot ID using template-based parsing."""
    p = argparse.ArgumentParser(prog="where-used", description="Find all references to an Cypilot ID")
    p.add_argument("--id", required=True, help="Cypilot ID to find references for")
    p.add_argument("--artifact", default=None, help="Limit search to specific artifact (optional)")
    p.add_argument("--include-definitions", action="store_true", help="Include definitions in results")
    args = p.parse_args(argv)

    target_id = str(args.id).strip()
    if not target_id:
        print(json.dumps({"status": "ERROR", "message": "ID cannot be empty"}, indent=None, ensure_ascii=False))
        return 1

    # Collect artifacts to scan: (artifact_path, template, artifact_kind)
    artifacts_to_scan: List[Tuple[Path, Template, str]] = []

    if args.artifact:
        # Load context from artifact's location
        artifact_path = Path(args.artifact).resolve()
        if not artifact_path.exists():
            print(json.dumps({"status": "ERROR", "message": f"Artifact not found: {artifact_path}"}, indent=None, ensure_ascii=False))
            return 1

        from .utils.context import CypilotContext
        ctx = CypilotContext.load(artifact_path.parent)
        if not ctx:
            print(json.dumps({"status": "ERROR", "message": "No adapter found. Run 'init' first."}, indent=None, ensure_ascii=False))
            return 1

        meta = ctx.meta
        project_root = ctx.project_root

        try:
            rel_path = artifact_path.relative_to(project_root).as_posix()
        except ValueError:
            rel_path = None
        if rel_path:
            result = meta.get_artifact_by_path(rel_path)
            if result:
                artifact_meta, system_node = result
                tmpl = ctx.get_template(system_node.kit, artifact_meta.kind)
                if tmpl is None:
                    tmpl = Template(
                        path=Path("<synthetic-template>"),
                        kind=str(artifact_meta.kind),
                        version=None,
                        policy=None,
                        blocks=[],
                        _loaded=True,
                    )
                artifacts_to_scan.append((artifact_path, tmpl, artifact_meta.kind))
        if not artifacts_to_scan:
            print(json.dumps({"status": "ERROR", "message": f"Artifact not in Cypilot registry: {args.artifact}"}, indent=None, ensure_ascii=False))
            return 1
    else:
        # Use global context
        from .utils.context import get_context
        ctx = get_context()
        if not ctx:
            print(json.dumps({"status": "ERROR", "message": "No adapter found. Run 'init' first."}, indent=None, ensure_ascii=False))
            return 1

        meta = ctx.meta
        project_root = ctx.project_root

        # Scan all Cypilot artifacts
        for artifact_meta, system_node in meta.iter_all_artifacts():
            tmpl = ctx.get_template(system_node.kit, artifact_meta.kind)
            if tmpl is None:
                tmpl = Template(
                    path=Path("<synthetic-template>"),
                    kind=str(artifact_meta.kind),
                    version=None,
                    policy=None,
                    blocks=[],
                    _loaded=True,
                )
            artifact_path = (project_root / artifact_meta.path).resolve()
            if artifact_path.exists():
                artifacts_to_scan.append((artifact_path, tmpl, artifact_meta.kind))

    if not artifacts_to_scan:
        print(json.dumps({"status": "ERROR", "message": "No Cypilot artifacts found in registry"}, indent=None, ensure_ascii=False))
        return 1

    # Search for references
    references: List[Dict[str, object]] = []

    for artifact_path, tmpl, artifact_type in artifacts_to_scan:
        parsed: TemplateArtifact = tmpl.parse(artifact_path)
        parsed._extract_ids_and_refs()  # Populate id_definitions and id_references

        # Collect references
        for id_ref in parsed.id_references:
            if id_ref.id == target_id:
                block_kind = id_ref.block.template_block.name if id_ref.block else None
                references.append({
                    "artifact": str(artifact_path),
                    "artifact_type": artifact_type,
                    "line": id_ref.line,
                    "kind": block_kind,
                    "type": "reference",
                    "checked": id_ref.checked,
                })

        # Optionally include definitions
        if args.include_definitions:
            for id_def in parsed.id_definitions:
                if id_def.id == target_id:
                    block_kind = id_def.block.template_block.name if id_def.block else None
                    references.append({
                        "artifact": str(artifact_path),
                        "artifact_type": artifact_type,
                        "line": id_def.line,
                        "kind": block_kind,
                        "type": "definition",
                        "checked": id_def.checked,
                    })

    # Sort by artifact and line
    references = sorted(references, key=lambda r: (str(r.get("artifact", "")), int(r.get("line", 0))))

    print(json.dumps({
        "id": target_id,
        "artifacts_scanned": len(artifacts_to_scan),
        "count": len(references),
        "references": references,
    }, indent=None, ensure_ascii=False))
    return 0


# =============================================================================
# TEMPLATE VALIDATION COMMAND
# =============================================================================

def _cmd_validate_kits(argv: List[str]) -> int:
    """Validate Cypilot kit packages and template files.

    Checks that:
    - Kits are properly configured in artifacts.json
    - Templates have valid cypilot-template frontmatter (kind, version)
    - All Cypilot markers are properly paired (open/close)
    - Marker types and attributes are valid
    """
    p = argparse.ArgumentParser(prog="validate-kits", description="Validate Cypilot kit packages and template files")
    p.add_argument("--kit", "--rule", dest="kit", default=None, help="Kit ID to validate (if omitted, validates all kits)")
    p.add_argument("--template", default=None, help="Path to specific template file to validate")
    p.add_argument("--verbose", action="store_true", help="Print full validation report")
    args = p.parse_args(argv)

    templates_to_validate: List[Path] = []

    if args.template:
        template_path = Path(args.template).resolve()
        if not template_path.exists():
            print(json.dumps({"status": "ERROR", "message": f"Template not found: {template_path}"}, indent=None, ensure_ascii=False))
            return 1
        templates_to_validate.append(template_path)
    else:
        # Find all templates from adapter registry
        adapter_dir = find_adapter_directory(Path.cwd())
        if not adapter_dir:
            print(json.dumps({"status": "ERROR", "message": "No adapter found. Run 'init' first or specify --template."}, indent=None, ensure_ascii=False))
            return 1

        registry, reg_err = load_artifacts_registry(adapter_dir)
        if not registry or reg_err:
            print(json.dumps({"status": "ERROR", "message": reg_err or "Could not load artifacts.json"}, indent=None, ensure_ascii=False))
            return 1

        from .utils.artifacts_meta import ArtifactsMeta
        meta = ArtifactsMeta.from_dict(registry)
        project_root = (adapter_dir / meta.project_root).resolve()

        # Collect all unique template paths from template packages
        # Collect unique template paths from all Cypilot artifacts
        seen_paths: Set[str] = set()
        for artifact_meta, system_node in meta.iter_all_artifacts():
            if args.kit and system_node.kit != args.kit:
                continue
            pkg = meta.get_kit(system_node.kit)
            if not pkg or not pkg.is_cypilot_format():
                continue
            template_path_str = pkg.get_template_path(artifact_meta.kind)
            tmpl_path = (project_root / template_path_str).resolve()
            if tmpl_path.as_posix() not in seen_paths and tmpl_path.exists():
                seen_paths.add(tmpl_path.as_posix())
                templates_to_validate.append(tmpl_path)

        if not templates_to_validate:
            result: Dict[str, object] = {
                "status": "PASS",
                "mode": "MARKERLESS",
                "message": "No Cypilot templates found in registry (template validation skipped)",
                "templates_validated": 0,
                "error_count": 0,
            }
            out = json.dumps(result, indent=2 if args.verbose else None, ensure_ascii=False)
            if args.verbose:
                out += "\n"
            print(out)
            return 0

    # Validate each template
    all_errors: List[Dict[str, object]] = []
    template_reports: List[Dict[str, object]] = []
    overall_status = "PASS"

    for template_path in templates_to_validate:
        tmpl, errs = Template.from_path(template_path)

        report: Dict[str, object] = {
            "template": str(template_path),
            "status": "PASS" if not errs else "FAIL",
            "error_count": len(errs),
        }

        if errs:
            overall_status = "FAIL"
            if args.verbose:
                report["errors"] = errs
            all_errors.extend(errs)
        else:
            # Template parsed successfully - add metadata
            if tmpl is not None:
                report["kind"] = tmpl.kind
                report["version"] = f"{tmpl.version.major}.{tmpl.version.minor}" if tmpl.version else None
                report["blocks"] = len(tmpl.blocks) if tmpl.blocks else 0
                if args.verbose and tmpl.blocks:
                    report["block_types"] = list(set(b.type for b in tmpl.blocks))

        template_reports.append(report)

    # Build final report
    result: Dict[str, object] = {
        "status": overall_status,
        "templates_validated": len(template_reports),
        "error_count": len(all_errors),
    }

    if args.verbose:
        result["templates"] = template_reports
        if all_errors:
            result["errors"] = all_errors
    else:
        # Compact output
        failed = [r for r in template_reports if r.get("status") == "FAIL"]
        if failed:
            result["failed_templates"] = [
                {"template": r.get("template"), "error_count": r.get("error_count")}
                for r in failed
            ]
        if all_errors:
            result["errors"] = all_errors[:10]
            if len(all_errors) > 10:
                result["errors_truncated"] = len(all_errors) - 10

    out = json.dumps(result, indent=2 if args.verbose else None, ensure_ascii=False)
    if args.verbose:
        out += "\n"
    print(out)

    return 0 if overall_status == "PASS" else 2


# =============================================================================
# ADAPTER COMMAND
# =============================================================================

def _cmd_adapter_info(argv: List[str]) -> int:
    """
    Discover and display Cypilot adapter information.
    Shows adapter location, project name, and available specs.
    """
    p = argparse.ArgumentParser(prog="adapter-info", description="Discover Cypilot adapter configuration")
    p.add_argument("--root", default=".", help="Project root to search from (default: current directory)")
    p.add_argument("--cypilot-root", default=None, help="Cypilot core location (if agent knows it)")
    args = p.parse_args(argv)
    
    start_path = Path(args.root).resolve()
    cypilot_root_path = Path(args.cypilot_root).resolve() if args.cypilot_root else None
    
    # Find project root
    project_root = find_project_root(start_path)
    if project_root is None:
        print(json.dumps(
            {
                "status": "NOT_FOUND",
                "message": "No project root found (no .git or .cypilot-config.json)",
                "searched_from": start_path.as_posix(),
                "hint": "Create .cypilot-config.json in project root to configure Cypilot",
            },
            indent=2,
            ensure_ascii=False,
        ))
        return 1
    
    # Find adapter
    adapter_dir = find_adapter_directory(start_path, cypilot_root=cypilot_root_path)
    if adapter_dir is None:
        # Check if config exists to provide better error message
        cfg = load_project_config(project_root)
        if cfg is not None:
            adapter_rel = cfg.get("cypilotAdapterPath")
            if adapter_rel is not None and isinstance(adapter_rel, str):
                # Config exists but path is invalid
                print(json.dumps(
                    {
                        "status": "CONFIG_ERROR",
                        "message": f"Config specifies adapter path but directory not found or invalid",
                        "project_root": project_root.as_posix(),
                        "config_path": adapter_rel,
                        "expected_location": (project_root / adapter_rel).as_posix(),
                        "hint": "Check .cypilot-config.json cypilotAdapterPath points to valid directory with AGENTS.md",
                    },
                    indent=2,
                    ensure_ascii=False,
                ))
                return 1
        
        # No config, no adapter found via recursive search
        print(json.dumps(
            {
                "status": "NOT_FOUND",
                "message": "No .cypilot-adapter found in project (searched recursively up to 5 levels deep)",
                "project_root": project_root.as_posix(),
                "hint": "Create .cypilot-config.json with cypilotAdapterPath or run adapter-bootstrap workflow",
            },
            indent=2,
            ensure_ascii=False,
        ))
        return 1
    
    # Load adapter config
    config = load_adapter_config(adapter_dir)
    config["status"] = "FOUND"
    config["project_root"] = project_root.as_posix()

    # Include artifacts registry content from adapter, if present.
    registry_path = (adapter_dir / "artifacts.json").resolve()
    config["artifacts_registry_path"] = registry_path.as_posix()
    registry = _load_json_file(registry_path)
    if registry is None:
        config["artifacts_registry"] = None
        config["artifacts_registry_error"] = "MISSING_OR_INVALID_JSON" if registry_path.exists() else "MISSING"
    else:
        config["artifacts_registry"] = registry
        config["artifacts_registry_error"] = None
    
    # Calculate relative path
    try:
        relative_path = adapter_dir.relative_to(project_root).as_posix()
    except ValueError:
        relative_path = adapter_dir.as_posix()
    config["relative_path"] = relative_path
    
    # Check if .cypilot-config.json exists
    config_file = project_root / ".cypilot-config.json"
    config["has_config"] = config_file.exists()
    if not config_file.exists():
        config["config_hint"] = f"Create .cypilot-config.json with: {{\"cypilotAdapterPath\": \"{relative_path}\"}}"
    
    print(json.dumps(config, indent=2, ensure_ascii=False))
    return 0


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main(argv: Optional[List[str]] = None) -> int:
    argv_list = list(argv) if argv is not None else sys.argv[1:]

    # Load global Cypilot context on startup (templates, systems, etc.)
    # Always reload context based on current working directory (no caching)
    from .utils.context import CypilotContext, set_context
    ctx = CypilotContext.load()
    set_context(ctx)
    # Context may be None if no adapter found - that's OK for some commands like init

    # Define all available commands
    analysis_commands = ["validate", "validate-kits"]
    legacy_aliases = ["validate-code", "validate-rules"]
    search_commands = [
        "init",
        "list-ids", "list-id-kinds",
        "get-content",
        "where-defined", "where-used",
        "adapter-info",
        "self-check",
        "agents",
    ]
    all_commands = analysis_commands + search_commands + legacy_aliases

    # Handle --help / -h at top level
    if argv_list and argv_list[0] in ("-h", "--help"):
        print("usage: cypilot <command> [options]")
        print()
        print("Cypilot CLI - artifact validation and traceability tool")
        print()
        print("Validation commands:")
        for c in analysis_commands:
            print(f"  {c}")
        print()
        print("Search and utility commands:")
        for c in search_commands:
            print(f"  {c}")
        print()
        print("Legacy aliases:")
        print("  validate-code → validate")
        print("  validate-rules → validate-kits")
        print()
        print("Run 'cypilot <command> --help' for command-specific options.")
        return 0

    if not argv_list:
        print(json.dumps({
            "status": "ERROR",
            "message": "Missing subcommand",
            "analysis_commands": analysis_commands,
            "search_commands": search_commands,
        }, indent=None, ensure_ascii=False))
        return 1

    # Backward compatibility: if first arg starts with --, assume validate command
    if argv_list[0].startswith("-"):
        cmd = "validate"
        rest = argv_list
    else:
        cmd = argv_list[0]
        rest = argv_list[1:]

    # Dispatch to appropriate command handler
    if cmd == "validate":
        return _cmd_validate(rest)
    elif cmd == "validate-code":
        # Legacy alias: keep for compatibility.
        return _cmd_validate(rest)
    elif cmd in ("validate-kits", "validate-rules"):
        return _cmd_validate_kits(rest)
    elif cmd == "init":
        return _cmd_init(rest)
    elif cmd == "list-ids":
        return _cmd_list_ids(rest)
    elif cmd == "list-id-kinds":
        return _cmd_list_id_kinds(rest)
    elif cmd == "get-content":
        return _cmd_get_content(rest)
    elif cmd == "where-defined":
        return _cmd_where_defined(rest)
    elif cmd == "where-used":
        return _cmd_where_used(rest)
    elif cmd == "adapter-info":
        return _cmd_adapter_info(rest)
    elif cmd == "self-check":
        return _cmd_self_check(rest)
    elif cmd == "agents":
        return _cmd_agents(rest)
    else:
        print(json.dumps({
            "status": "ERROR",
            "message": f"Unknown command: {cmd}",
            "available": all_commands,
        }, indent=None, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["main"]
