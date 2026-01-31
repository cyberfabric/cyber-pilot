"""
FDD Validator - CLI Entry Point

Command-line interface for the FDD validation tool.
"""

import sys
import os
import json
import re
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Set, Tuple

from .utils.files import (
    find_project_root,
    load_project_config,
    find_adapter_directory,
    load_adapter_config,
    load_artifacts_registry,
)
from .utils.artifacts_meta import (
    create_backup,
    generate_default_registry,
)
from .utils.template import (
    Template,
    Artifact as TemplateArtifact,
)
from .utils.codebase import (
    CodeFile,
    scan_directory as scan_code_directory,
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


def _windsurf_default_agent_workflows_config() -> dict:
    return {
        "version": 1,
        "agents": {
            "windsurf": {
                "workflow_dir": ".windsurf/workflows",
                "workflow_command_prefix": "fdd-",
                "workflow_filename_format": "{command}.md",
                "template": [
                    "# /{command}",
                    "",
                    "ALWAYS open and follow `{target_workflow_path}`",
                ],
            }
            ,
            "cursor": {
                "workflow_dir": ".cursor/commands",
                "workflow_command_prefix": "fdd-",
                "workflow_filename_format": "{command}.md",
                "template": [
                    "# /{command}",
                    "",
                    "ALWAYS open and follow `{target_workflow_path}`",
                ],
            },
            "claude": {
                "workflow_dir": ".claude/commands",
                "workflow_command_prefix": "fdd-",
                "workflow_filename_format": "{command}.md",
                "template": [
                    "---",
                    "description: Proxy to FDD workflow {workflow_name}",
                    "---",
                    "",
                    "ALWAYS open and follow `{target_workflow_path}`",
                ],
            },
            "copilot": {
                "workflow_dir": ".github/prompts",
                "workflow_command_prefix": "fdd-",
                "workflow_filename_format": "{command}.prompt.md",
                "template": [
                    "---",
                    "name: {command}",
                    "description: Proxy to FDD workflow {workflow_name}",
                    "---",
                    "",
                    "ALWAYS open and follow `{target_workflow_path}`",
                ],
            },
        },
    }


def _windsurf_default_agent_skills_config() -> dict:
    return {
        "version": 1,
        "agents": {
            "windsurf": {
                "skill_name": "fdd",
                "outputs": [
                    {
                        "path": ".windsurf/skills/fdd/SKILL.md",
                        "template": [
                            "---",
                            "name: {skill_name}",
                            "description: Proxy to FDD core skill instructions",
                            "---",
                            "",
                            "ALWAYS open and follow `{target_skill_path}`",
                        ],
                    }
                ],
            }
            ,
            "cursor": {
                "outputs": [
                    {
                        "path": ".cursor/rules/fdd.mdc",
                        "template": [
                            "---",
                            "description: Proxy to FDD core skill instructions",
                            "alwaysApply: true",
                            "---",
                            "",
                            "ALWAYS open and follow `{target_skill_path}`",
                        ],
                    },
                    {
                        "path": ".cursor/commands/fdd.md",
                        "template": [
                            "# /fdd",
                            "",
                            "ALWAYS open and follow `{target_skill_path}`",
                        ],
                    },
                ],
            },
            "claude": {
                "outputs": [
                    {
                        "path": ".claude/commands/fdd.md",
                        "template": [
                            "---",
                            "description: Proxy to FDD core skill instructions",
                            "---",
                            "",
                            "ALWAYS open and follow `{target_skill_path}`",
                        ],
                    }
                ],
            },
            "copilot": {
                "outputs": [
                    {
                        "path": ".github/copilot-instructions.md",
                        "template": [
                            "# FDD",
                            "",
                            "ALWAYS open and follow `{target_skill_path}`",
                        ],
                    },
                    {
                        "path": ".github/prompts/fdd-skill.prompt.md",
                        "template": [
                            "---",
                            "name: fdd-skill",
                            "description: Proxy to FDD core skill instructions",
                            "---",
                            "",
                            "ALWAYS open and follow `{target_skill_path}`",
                        ],
                    },
                ],
            },
        },
    }


def _render_template(lines: List[str], variables: Dict[str, str]) -> str:
    out: List[str] = []
    for line in lines:
        try:
            out.append(line.format(**variables))
        except KeyError as e:
            raise SystemExit(f"Missing template variable: {e}")
    return "\n".join(out).rstrip() + "\n"


def _cmd_agent_workflows(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="agent-workflows", description="Generate/update agent-specific workflow proxy files")
    p.add_argument("--agent", required=True, help="Agent/IDE key (e.g., windsurf)")
    p.add_argument("--root", default=".", help="Project root directory (default: current directory)")
    p.add_argument("--fdd-root", default=None, help="Explicit FDD core root (optional override)")
    p.add_argument("--config", default=None, help="Path to agent workflows config JSON (default: project root)")
    p.add_argument("--dry-run", action="store_true", help="Compute changes without writing files")
    args = p.parse_args(argv)

    agent = str(args.agent).strip()
    if not agent:
        raise SystemExit("--agent must be non-empty")

    start_path = Path(args.root).resolve()
    project_root = find_project_root(start_path)
    if project_root is None:
        print(json.dumps({
            "status": "NOT_FOUND",
            "message": "No project root found (no .git or .fdd-config.json)",
            "searched_from": start_path.as_posix(),
        }, indent=2, ensure_ascii=False))
        return 1

    fdd_root = Path(args.fdd_root).resolve() if args.fdd_root else None
    if fdd_root is None:
        fdd_root = (Path(__file__).resolve().parents[4])
        if not ((fdd_root / "AGENTS.md").exists() and (fdd_root / "workflows").is_dir()):
            fdd_root = Path(__file__).resolve().parents[6]

    cfg_path = Path(args.config).resolve() if args.config else (project_root / "fdd-agent-workflows.json")
    cfg = _load_json_file(cfg_path)

    recognized = agent in {"windsurf", "cursor", "claude", "copilot"}
    if cfg is None:
        cfg = _windsurf_default_agent_workflows_config() if recognized else {"version": 1, "agents": {agent: {}}}
        if not args.dry_run:
            _write_json_file(cfg_path, cfg)

    agents_cfg = cfg.get("agents") if isinstance(cfg, dict) else None
    if isinstance(cfg, dict) and isinstance(agents_cfg, dict) and agent not in agents_cfg:
        if recognized:
            defaults = _windsurf_default_agent_workflows_config()
            default_agents = defaults.get("agents") if isinstance(defaults, dict) else None
            if isinstance(default_agents, dict) and isinstance(default_agents.get(agent), dict):
                agents_cfg[agent] = default_agents[agent]
        else:
            agents_cfg[agent] = {}
        cfg["agents"] = agents_cfg
        if not args.dry_run:
            _write_json_file(cfg_path, cfg)

    if isinstance(cfg, dict) and isinstance(agents_cfg, dict) and agent in agents_cfg and not recognized:
        agent_cfg_candidate = agents_cfg.get(agent)
        if not isinstance(agent_cfg_candidate, dict) or not agent_cfg_candidate:
            print(json.dumps({
                "status": "CONFIG_INCOMPLETE",
                "message": "Unknown agent config must be filled in",
                "config_path": cfg_path.as_posix(),
                "agent": agent,
            }, indent=2, ensure_ascii=False))
            return 2

    if not isinstance(agents_cfg, dict) or agent not in agents_cfg or not isinstance(agents_cfg.get(agent), dict):
        print(json.dumps({
            "status": "CONFIG_ERROR",
            "message": "Agent config missing or invalid",
            "config_path": cfg_path.as_posix(),
            "agent": agent,
        }, indent=2, ensure_ascii=False))
        return 1

    agent_cfg: dict = agents_cfg[agent]
    workflow_dir_rel = agent_cfg.get("workflow_dir")
    filename_fmt = agent_cfg.get("workflow_filename_format", "{command}.md")
    prefix = agent_cfg.get("workflow_command_prefix", "fdd-")
    template = agent_cfg.get("template")

    if not isinstance(workflow_dir_rel, str) or not workflow_dir_rel.strip():
        print(json.dumps({
            "status": "CONFIG_INCOMPLETE",
            "message": "Agent config missing workflow_dir",
            "config_path": cfg_path.as_posix(),
            "agent": agent,
        }, indent=2, ensure_ascii=False))
        return 2
    if not isinstance(filename_fmt, str) or not filename_fmt.strip():
        print(json.dumps({
            "status": "CONFIG_INCOMPLETE",
            "message": "Agent config missing workflow_filename_format",
            "config_path": cfg_path.as_posix(),
            "agent": agent,
        }, indent=2, ensure_ascii=False))
        return 2
    if not isinstance(prefix, str):
        prefix = "fdd-"
    if not isinstance(template, list) or not all(isinstance(x, str) for x in template):
        print(json.dumps({
            "status": "CONFIG_INCOMPLETE",
            "message": "Agent config missing template (must be array of strings)",
            "config_path": cfg_path.as_posix(),
            "agent": agent,
        }, indent=2, ensure_ascii=False))
        return 2

    workflow_dir = (project_root / workflow_dir_rel).resolve()
    fdd_workflow_files = _list_workflow_files(fdd_root)
    fdd_workflow_names = [Path(p).stem for p in fdd_workflow_files]

    desired: Dict[str, Dict[str, str]] = {}
    for wf_name in fdd_workflow_names:
        command = "fdd" if wf_name == "fdd" else f"{prefix}{wf_name}"
        filename = filename_fmt.format(command=command, workflow_name=wf_name)
        desired_path = (workflow_dir / filename).resolve()
        target_workflow_path = (fdd_root / "workflows" / f"{wf_name}.md").resolve()
        target_rel = _safe_relpath(target_workflow_path, project_root)
        content = _render_template(
            template,
            {
                "command": command,
                "workflow_name": wf_name,
                "target_workflow_path": target_rel,
            },
        )
        desired[desired_path.as_posix()] = {
            "command": command,
            "workflow_name": wf_name,
            "target_workflow_path": target_rel,
            "content": content,
        }

    created: List[str] = []
    updated: List[str] = []
    renamed: List[Tuple[str, str]] = []
    rename_conflicts: List[Tuple[str, str]] = []
    deleted: List[str] = []

    existing_files: List[Path] = []
    if workflow_dir.is_dir():
        existing_files = list(workflow_dir.glob("*.md"))

    # Rename misnamed proxy files that target an existing workflow.
    desired_by_target: Dict[str, str] = {meta["target_workflow_path"]: p for p, meta in desired.items()}
    for pth in existing_files:
        if pth.as_posix() in desired:
            continue
        # Only consider renaming files that look like agent-workflow proxies.
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
        if not dst:
            continue
        if pth.as_posix() == dst:
            continue
        if Path(dst).exists():
            rename_conflicts.append((pth.as_posix(), dst))
            continue
        if not args.dry_run:
            workflow_dir.mkdir(parents=True, exist_ok=True)
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
            pth.replace(Path(dst))
        renamed.append((pth.as_posix(), dst))

    # Refresh listing after potential renames.
    existing_files = list(workflow_dir.glob("*.md")) if workflow_dir.is_dir() else []

    # Create/update desired files.
    for p_str, meta in desired.items():
        pth = Path(p_str)
        if not pth.exists():
            created.append(p_str)
            if not args.dry_run:
                pth.parent.mkdir(parents=True, exist_ok=True)
                pth.write_text(meta["content"], encoding="utf-8")
            continue
        try:
            old = pth.read_text(encoding="utf-8")
        except Exception:
            old = ""
        if old != meta["content"]:
            updated.append(p_str)
            if not args.dry_run:
                pth.write_text(meta["content"], encoding="utf-8")

    # Delete stale generated proxies (prefix-based + heuristic match), if they are not desired.
    desired_paths = set(desired.keys())
    for pth in existing_files:
        p_str = pth.as_posix()
        if p_str in desired_paths:
            continue
        if not pth.name.startswith(prefix) and not pth.name.startswith("fdd-"):
            continue
        try:
            txt = pth.read_text(encoding="utf-8")
        except Exception:
            continue
        m = re.search(r"ALWAYS open and follow `([^`]+)`", txt)
        if not m:
            continue
        target_rel = m.group(1)
        # Only delete if it points to a workflow under fdd_root/workflows/ that no longer exists.
        # If it's pointing elsewhere, leave it alone.
        if "workflows/" not in target_rel and "/workflows/" not in target_rel:
            continue
        expected = (project_root / target_rel).resolve() if not target_rel.startswith("/") else Path(target_rel)
        # If expected is inside fdd_root/workflows, treat as managed candidate.
        try:
            expected.relative_to(fdd_root / "workflows")
        except ValueError:
            continue
        if expected.exists():
            continue
        deleted.append(p_str)
        if not args.dry_run:
            try:
                pth.unlink()
            except (PermissionError, FileNotFoundError, OSError):
                pass

    print(json.dumps({
        "status": "PASS",
        "agent": agent,
        "project_root": project_root.as_posix(),
        "fdd_root": fdd_root.as_posix(),
        "config_path": cfg_path.as_posix(),
        "workflow_dir": _safe_relpath(workflow_dir, project_root),
        "dry_run": bool(args.dry_run),
        "counts": {
            "workflows": len(fdd_workflow_names),
            "created": len(created),
            "updated": len(updated),
            "renamed": len(renamed),
            "rename_conflicts": len(rename_conflicts),
            "deleted": len(deleted),
        },
        "created": created,
        "updated": updated,
        "renamed": renamed,
        "rename_conflicts": rename_conflicts,
        "deleted": deleted,
    }, indent=2, ensure_ascii=False))
    return 0


def _cmd_self_check(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="self-check", description="Validate registered template examples against templates")
    p.add_argument("--root", default=".", help="Project root to search from (default: current directory)")
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

    templates = reg.get("templates") if isinstance(reg, dict) else None
    if not isinstance(templates, dict):
        print(json.dumps({"status": "ERROR", "message": "Registry templates catalog missing or invalid"}, indent=2, ensure_ascii=False))
        return 1

    def _resolve_registry_path(p_raw: object) -> Optional[Path]:
        if not isinstance(p_raw, str) or not p_raw.strip():
            return None
        s = p_raw.strip()
        if s.startswith("./"):
            s = s[2:]
        if s.startswith("/"):
            return Path(s).resolve()
        return (project_root / s).resolve()

    try:
        from .utils.template import validate_artifact_file_against_template
    except Exception:
        validate_artifact_file_against_template = None  # type: ignore[assignment]

    if validate_artifact_file_against_template is None:
        print(json.dumps({"status": "ERROR", "message": "Template validation module not available"}, indent=2, ensure_ascii=False))
        return 1

    results: List[Dict[str, object]] = []
    overall_status = "PASS"

    for kind, tmpl_list in templates.items():
        if not isinstance(tmpl_list, list):
            continue
        for t in tmpl_list:
            if not isinstance(t, dict):
                continue
            level = str(t.get("validation_level") or "STRICT").strip().upper()
            if level != "STRICT":
                continue

            template_path = _resolve_registry_path(t.get("template_path"))
            example_path = _resolve_registry_path(t.get("example_path"))

            item: Dict[str, object] = {
                "kind": str(kind),
                "id": t.get("id"),
                "validation_level": level,
                "template_path": str(template_path) if template_path is not None else None,
                "example_path": str(example_path) if example_path is not None else None,
                "status": "PASS",
            }

            errs: List[Dict[str, object]] = []
            warns: List[Dict[str, object]] = []

            if template_path is None or not template_path.exists():
                errs.append({"type": "file", "message": "Template path not found", "path": str(template_path) if template_path is not None else ""})
            if example_path is None or not example_path.exists():
                errs.append({"type": "file", "message": "Example path not found", "path": str(example_path) if example_path is not None else ""})

            if not errs and template_path is not None and example_path is not None:
                rep = validate_artifact_file_against_template(
                    artifact_path=example_path,
                    template_path=template_path,
                    expected_kind=str(kind),
                )
                errs.extend(list(rep.get("errors", []) or []))
                warns.extend(list(rep.get("warnings", []) or []))

            if errs:
                item["status"] = "FAIL"
                item["error_count"] = len(errs)
                overall_status = "FAIL"
            if warns:
                item["warning_count"] = len(warns)
            if bool(args.verbose):
                item["errors"] = errs
                item["warnings"] = warns

            results.append(item)

    out = {
        "status": overall_status,
        "project_root": project_root.as_posix(),
        "adapter_dir": adapter_dir.as_posix(),
        "count": len(results),
        "results": results,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if overall_status == "PASS" else 2


def _cmd_agent_skills(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="agent-skills", description="Generate/update agent-specific skill outputs")
    p.add_argument("--agent", required=True, help="Agent/IDE key (e.g., windsurf)")
    p.add_argument("--root", default=".", help="Project root directory (default: current directory)")
    p.add_argument("--config", default=None, help="Path to agent skills config JSON (default: project root)")
    p.add_argument("--dry-run", action="store_true", help="Compute changes without writing files")
    args = p.parse_args(argv)

    agent = str(args.agent).strip()
    if not agent:
        raise SystemExit("--agent must be non-empty")

    start_path = Path(args.root).resolve()
    project_root = find_project_root(start_path)
    if project_root is None:
        print(json.dumps({
            "status": "NOT_FOUND",
            "message": "No project root found (no .git or .fdd-config.json)",
            "searched_from": start_path.as_posix(),
        }, indent=2, ensure_ascii=False))
        return 1

    cfg_path = Path(args.config).resolve() if args.config else (project_root / "fdd-agent-skills.json")
    cfg = _load_json_file(cfg_path)

    recognized = agent in {"windsurf", "cursor", "claude", "copilot"}
    if cfg is None:
        cfg = _windsurf_default_agent_skills_config() if recognized else {"version": 1, "agents": {agent: {}}}
        if not args.dry_run:
            _write_json_file(cfg_path, cfg)

    agents_cfg = cfg.get("agents") if isinstance(cfg, dict) else None
    if isinstance(cfg, dict) and isinstance(agents_cfg, dict) and agent not in agents_cfg:
        if recognized:
            defaults = _windsurf_default_agent_skills_config()
            default_agents = defaults.get("agents") if isinstance(defaults, dict) else None
            if isinstance(default_agents, dict) and isinstance(default_agents.get(agent), dict):
                agents_cfg[agent] = default_agents[agent]
        else:
            agents_cfg[agent] = {}
        cfg["agents"] = agents_cfg
        if not args.dry_run:
            _write_json_file(cfg_path, cfg)

    if isinstance(cfg, dict) and isinstance(agents_cfg, dict) and agent in agents_cfg and not recognized:
        agent_cfg_candidate = agents_cfg.get(agent)
        if not isinstance(agent_cfg_candidate, dict) or not agent_cfg_candidate:
            print(json.dumps({
                "status": "CONFIG_INCOMPLETE",
                "message": "Unknown agent config must be filled in",
                "config_path": cfg_path.as_posix(),
                "agent": agent,
            }, indent=2, ensure_ascii=False))
            return 2

    if not isinstance(agents_cfg, dict) or agent not in agents_cfg or not isinstance(agents_cfg.get(agent), dict):
        print(json.dumps({
            "status": "CONFIG_ERROR",
            "message": "Agent config missing or invalid",
            "config_path": cfg_path.as_posix(),
            "agent": agent,
        }, indent=2, ensure_ascii=False))
        return 1

    agent_cfg: dict = agents_cfg[agent]
    outputs = agent_cfg.get("outputs")
    if outputs is not None:
        if not isinstance(outputs, list) or not all(isinstance(x, dict) for x in outputs):
            print(json.dumps({
                "status": "CONFIG_INCOMPLETE",
                "message": "Agent config outputs must be an array of objects",
                "config_path": cfg_path.as_posix(),
                "agent": agent,
            }, indent=2, ensure_ascii=False))
            return 2

        created: List[str] = []
        updated: List[str] = []
        out_items: List[Dict[str, str]] = []

        target_skill_abs = (project_root / "skills" / "fdd" / "SKILL.md").resolve()
        skill_name = agent_cfg.get("skill_name")
        if not isinstance(skill_name, str) or not skill_name.strip():
            skill_name = "fdd"

        for idx, out_cfg in enumerate(outputs):
            rel_path = out_cfg.get("path")
            template = out_cfg.get("template")
            if not isinstance(rel_path, str) or not rel_path.strip():
                print(json.dumps({
                    "status": "CONFIG_INCOMPLETE",
                    "message": f"outputs[{idx}] missing path",
                    "config_path": cfg_path.as_posix(),
                    "agent": agent,
                }, indent=2, ensure_ascii=False))
                return 2
            if not isinstance(template, list) or not all(isinstance(x, str) for x in template):
                print(json.dumps({
                    "status": "CONFIG_INCOMPLETE",
                    "message": f"outputs[{idx}] missing template (must be array of strings)",
                    "config_path": cfg_path.as_posix(),
                    "agent": agent,
                }, indent=2, ensure_ascii=False))
                return 2

            out_path = (project_root / rel_path).resolve()
            out_dir = out_path.parent
            target_skill_rel = _safe_relpath_from_dir(target_skill_abs, out_dir)
            content = _render_template(
                template,
                {
                    "agent": agent,
                    "skill_name": str(skill_name),
                    "target_skill_path": target_skill_rel,
                },
            )

            if not out_path.exists():
                created.append(out_path.as_posix())
                if not args.dry_run:
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    out_path.write_text(content, encoding="utf-8")
                out_items.append({"path": _safe_relpath(out_path, project_root), "action": "created"})
            else:
                try:
                    old = out_path.read_text(encoding="utf-8")
                except Exception:
                    old = ""
                if old != content:
                    updated.append(out_path.as_posix())
                    if not args.dry_run:
                        out_path.write_text(content, encoding="utf-8")
                    out_items.append({"path": _safe_relpath(out_path, project_root), "action": "updated"})
                else:
                    out_items.append({"path": _safe_relpath(out_path, project_root), "action": "unchanged"})

        print(json.dumps({
            "status": "PASS",
            "agent": agent,
            "project_root": project_root.as_posix(),
            "config_path": cfg_path.as_posix(),
            "dry_run": bool(args.dry_run),
            "counts": {
                "outputs": len(outputs),
                "created": len(created),
                "updated": len(updated),
            },
            "outputs": out_items,
            "created": created,
            "updated": updated,
        }, indent=2, ensure_ascii=False))
        return 0

    # Legacy (windsurf) schema: a single skill folder with an entry file.
    skills_dir_rel = agent_cfg.get("skills_dir")
    skill_name = agent_cfg.get("skill_name")
    entry_filename = agent_cfg.get("entry_filename", "SKILL.md")
    template = agent_cfg.get("template")

    if not isinstance(skills_dir_rel, str) or not skills_dir_rel.strip():
        print(json.dumps({
            "status": "CONFIG_INCOMPLETE",
            "message": "Agent config missing skills_dir",
            "config_path": cfg_path.as_posix(),
            "agent": agent,
        }, indent=2, ensure_ascii=False))
        return 2
    if not isinstance(skill_name, str) or not skill_name.strip():
        print(json.dumps({
            "status": "CONFIG_INCOMPLETE",
            "message": "Agent config missing skill_name",
            "config_path": cfg_path.as_posix(),
            "agent": agent,
        }, indent=2, ensure_ascii=False))
        return 2
    if not isinstance(entry_filename, str) or not entry_filename.strip():
        entry_filename = "SKILL.md"
    if not isinstance(template, list) or not all(isinstance(x, str) for x in template):
        print(json.dumps({
            "status": "CONFIG_INCOMPLETE",
            "message": "Agent config missing template (must be array of strings)",
            "config_path": cfg_path.as_posix(),
            "agent": agent,
        }, indent=2, ensure_ascii=False))
        return 2

    skills_dir = (project_root / skills_dir_rel).resolve()
    skill_dir = (skills_dir / skill_name).resolve()
    entry_path = (skill_dir / entry_filename).resolve()

    target_skill_abs = (project_root / "skills" / "fdd" / "SKILL.md").resolve()
    target_skill_rel = _safe_relpath_from_dir(target_skill_abs, skill_dir)

    content = _render_template(
        template,
        {
            "skill_name": skill_name,
            "target_skill_path": target_skill_rel,
        },
    )

    created: List[str] = []
    updated: List[str] = []

    if not entry_path.exists():
        created.append(entry_path.as_posix())
        if not args.dry_run:
            entry_path.parent.mkdir(parents=True, exist_ok=True)
            entry_path.write_text(content, encoding="utf-8")
    else:
        try:
            old = entry_path.read_text(encoding="utf-8")
        except Exception:
            old = ""
        if old != content:
            updated.append(entry_path.as_posix())
            if not args.dry_run:
                entry_path.write_text(content, encoding="utf-8")

    print(json.dumps({
        "status": "PASS",
        "agent": agent,
        "project_root": project_root.as_posix(),
        "config_path": cfg_path.as_posix(),
        "dry_run": bool(args.dry_run),
        "skill": {
            "name": skill_name,
            "dir": _safe_relpath(skill_dir, project_root),
            "entry": _safe_relpath(entry_path, project_root),
        },
        "counts": {
            "created": len(created),
            "updated": len(updated),
        },
        "created": created,
        "updated": updated,
    }, indent=2, ensure_ascii=False))
    return 0


def _default_project_config(fdd_core_path: str, fdd_adapter_path: str) -> dict:
    return {
        "fddCorePath": fdd_core_path,
        "fddAdapterPath": fdd_adapter_path,
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


def _list_workflow_files(fdd_root: Path) -> List[str]:
    workflows_dir = (fdd_root / "workflows").resolve()
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
    p = argparse.ArgumentParser(prog="init", description="Initialize FDD config and minimal adapter")
    p.add_argument("--project-root", default=None, help="Project root directory to create .fdd-config.json in")
    p.add_argument("--fdd-root", default=None, help="Explicit FDD core root (optional override)")
    p.add_argument("--adapter-path", default=None, help="Adapter directory path relative to project root (default: FDD-Adapter)")
    p.add_argument("--project-name", default=None, help="Project name used in adapter AGENTS.md (default: project root folder name)")
    p.add_argument("--yes", action="store_true", help="Do not prompt; accept defaults")
    p.add_argument("--dry-run", action="store_true", help="Compute changes without writing files")
    p.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = p.parse_args(argv)

    cwd = Path.cwd().resolve()
    fdd_root = Path(args.fdd_root).resolve() if args.fdd_root else None
    if fdd_root is None:
        fdd_root = (Path(__file__).resolve().parents[4])
        if not ((fdd_root / "AGENTS.md").exists() and (fdd_root / "workflows").is_dir()):
            fdd_root = Path(__file__).resolve().parents[6]

    default_project_root = fdd_root.parent.resolve()
    if args.project_root is None and not args.yes:
        raw_root = _prompt_path("Where should I create .fdd-config.json?", default_project_root.as_posix())
        project_root = _resolve_user_path(raw_root, cwd)
    else:
        raw_root = args.project_root or default_project_root.as_posix()
        project_root = _resolve_user_path(raw_root, cwd)

    default_adapter_path = "FDD-Adapter"
    if args.adapter_path is None and not args.yes:
        adapter_rel = _prompt_path("Where should I create the FDD adapter directory (relative to project root)?", default_adapter_path)
    else:
        adapter_rel = args.adapter_path or default_adapter_path
    adapter_rel = adapter_rel.strip() or default_adapter_path

    adapter_dir = (project_root / adapter_rel).resolve()
    config_path = (project_root / ".fdd-config.json").resolve()
    core_rel = _safe_relpath_from_dir(fdd_root, project_root)
    extends_target = (fdd_root / "AGENTS.md").resolve()
    extends_rel = _safe_relpath_from_dir(extends_target, adapter_dir)

    project_name = str(args.project_name).strip() if args.project_name else project_root.name

    workflow_files = _list_workflow_files(fdd_root)
    workflow_list = ", ".join(workflow_files)
    artifacts_when = f"ALWAYS open and follow `artifacts.json` WHEN executing workflows: {workflow_list}" if workflow_list else "ALWAYS open and follow `artifacts.json` WHEN executing workflows"
    schema_rel = _safe_relpath_from_dir(fdd_root / "schemas" / "artifacts.schema.json", adapter_dir)
    registry_spec_rel = _safe_relpath_from_dir(fdd_root / "requirements" / "artifacts-registry.md", adapter_dir)
    desired_agents = "\n".join([
        f"# FDD Adapter: {project_name}",
        "",
        f"**Extends**: `{extends_rel}`",
        "",
        f"ALWAYS open and follow `{schema_rel}` WHEN working with artifacts.json",
        "",
        f"ALWAYS open and follow `{registry_spec_rel}` WHEN working with artifacts.json",
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
            existing_core = existing.get("fddCorePath")
            existing_adapter = existing.get("fddAdapterPath")
            if existing_core is None or existing_adapter is None:
                errors.append({"path": config_path.as_posix(), "error": "CONFIG_INCOMPLETE"})
            elif existing_core != core_rel or existing_adapter != adapter_rel:
                errors.append({"path": config_path.as_posix(), "error": "CONFIG_CONFLICT"})
            else:
                actions["config"] = "unchanged"
    else:
        if config_existed_before and args.force:
            existing = _load_json_file(config_path)
            if isinstance(existing, dict):
                merged = dict(existing)
                merged["fddCorePath"] = core_rel
                merged["fddAdapterPath"] = adapter_rel
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
            errors.append({"path": agents_path.as_posix(), "error": "ADAPTER_AGENTS_CONFLICT"})
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
            errors.append({"path": registry_path.as_posix(), "error": "ARTIFACTS_REGISTRY_CONFLICT"})
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
            "fdd_root": fdd_root.as_posix(),
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
        "fdd_root": fdd_root.as_posix(),
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
    """Validate FDD artifacts using template-based parsing.

    Validates structure against template, cross-references between artifacts,
    and task statuses.
    """
    from .utils.template import cross_validate_artifacts

    p = argparse.ArgumentParser(prog="validate", description="Validate FDD artifacts using template-based parsing")
    p.add_argument("--artifact", default=None, help="Path to specific FDD artifact (if omitted, validates all registered FDD artifacts)")
    p.add_argument("--verbose", action="store_true", help="Print full validation report")
    p.add_argument("--output", default=None, help="Write report to file instead of stdout")
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
                pkg = meta.get_rule(system_node.rules)
                if pkg and pkg.is_fdd_format():
                    template_path_str = pkg.get_template_path(artifact_meta.kind)
                    template_path = (project_root / template_path_str).resolve()
                    artifacts_to_validate.append((artifact_path, template_path, artifact_meta.kind, artifact_meta.traceability))
        if not artifacts_to_validate:
            print(json.dumps({"status": "ERROR", "message": f"Artifact not in FDD registry: {args.artifact}"}, indent=None, ensure_ascii=False))
            return 1
    else:
        # Validate all FDD artifacts
        for artifact_meta, system_node in meta.iter_all_artifacts():
            pkg = meta.get_rule(system_node.rules)
            if not pkg or not pkg.is_fdd_format():
                continue
            template_path_str = pkg.get_template_path(artifact_meta.kind)
            artifact_path = (project_root / artifact_meta.path).resolve()
            template_path = (project_root / template_path_str).resolve()
            if artifact_path.exists() and template_path.exists():
                artifacts_to_validate.append((artifact_path, template_path, artifact_meta.kind, artifact_meta.traceability))

    if not artifacts_to_validate:
        print(json.dumps({"status": "ERROR", "message": "No FDD artifacts found in registry"}, indent=None, ensure_ascii=False))
        return 1

    # Validate each artifact
    all_errors: List[Dict[str, object]] = []
    all_warnings: List[Dict[str, object]] = []
    artifact_reports: List[Dict[str, object]] = []
    parsed_artifacts: List[TemplateArtifact] = []

    for artifact_path, template_path, artifact_type, traceability in artifacts_to_validate:
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

        artifact: TemplateArtifact = tmpl.parse(artifact_path)
        parsed_artifacts.append(artifact)

        # Structure validation
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

    # Cross-reference validation across all artifacts
    if len(parsed_artifacts) > 1:
        cross_result = cross_validate_artifacts(parsed_artifacts)
        cross_errors = cross_result.get("errors", [])
        cross_warnings = cross_result.get("warnings", [])
        all_errors.extend(cross_errors)
        all_warnings.extend(cross_warnings)

    # Build final report
    overall_status = "PASS" if not all_errors else "FAIL"

    report: Dict[str, object] = {
        "status": overall_status,
        "artifacts_validated": len(artifact_reports),
        "error_count": len(all_errors),
        "warning_count": len(all_warnings),
    }

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
    """List FDD IDs from artifacts using template-based parsing.

    If no artifact is specified, scans all FDD-format artifacts from the adapter registry.
    """
    p = argparse.ArgumentParser(prog="list-ids")
    p.add_argument("--artifact", default=None, help="Path to FDD artifact file (if omitted, scans all registered FDD artifacts)")
    p.add_argument("--pattern", default=None, help="Filter IDs by substring or regex pattern")
    p.add_argument("--regex", action="store_true", help="Treat pattern as regular expression")
    p.add_argument("--kind", default=None, help="Filter by ID kind from template markers (e.g., 'requirement', 'feature')")
    p.add_argument("--all", action="store_true", help="Include duplicate IDs in results")
    p.add_argument("--include-code", action="store_true", help="Also scan code files for FDD marker references")
    args = p.parse_args(argv)

    # Collect artifacts to scan: (artifact_path, template_path, artifact_type)
    artifacts_to_scan: List[Tuple[Path, Path, str]] = []

    if args.artifact:
        # Single artifact specified
        artifact_path = Path(args.artifact).resolve()
        if not artifact_path.exists():
            print(json.dumps({"status": "ERROR", "message": f"Artifact not found: {artifact_path}"}, indent=None, ensure_ascii=False))
            return 1

        # Try to find template from adapter registry
        adapter_dir = find_adapter_directory(artifact_path.parent)
        if adapter_dir:
            registry, reg_err = load_artifacts_registry(adapter_dir)
            if registry and not reg_err:
                from .utils.artifacts_meta import ArtifactsMeta
                meta = ArtifactsMeta.from_dict(registry)
                project_root = (adapter_dir / meta.project_root).resolve()

                # Find artifact in registry
                try:
                    rel_path = artifact_path.relative_to(project_root).as_posix()
                except ValueError:
                    rel_path = None

                if rel_path:
                    result = meta.get_artifact_by_path(rel_path)
                    if result:
                        artifact_meta, system_node = result
                        pkg = meta.get_rule(system_node.rules)
                        if pkg and pkg.is_fdd_format():
                            template_path_str = pkg.get_template_path(artifact_meta.kind)
                            template_path = (project_root / template_path_str).resolve()
                            artifacts_to_scan.append((artifact_path, template_path, artifact_meta.kind))

        if not artifacts_to_scan:
            print(json.dumps({"status": "ERROR", "message": "Could not find template for artifact. Ensure artifact is registered in adapter."}, indent=None, ensure_ascii=False))
            return 1
    else:
        # No artifact specified - scan all FDD-format artifacts from registry
        adapter_dir = find_adapter_directory(Path.cwd())
        if not adapter_dir:
            print(json.dumps({"status": "ERROR", "message": "No adapter found. Run 'init' first or specify --artifact."}, indent=None, ensure_ascii=False))
            return 1

        registry, reg_err = load_artifacts_registry(adapter_dir)
        if not registry or reg_err:
            print(json.dumps({"status": "ERROR", "message": reg_err or "Could not load artifacts.json from adapter."}, indent=None, ensure_ascii=False))
            return 1

        from .utils.artifacts_meta import ArtifactsMeta
        meta = ArtifactsMeta.from_dict(registry)
        project_root = (adapter_dir / meta.project_root).resolve()

        for artifact_meta, system_node in meta.iter_all_artifacts():
            pkg = meta.get_rule(system_node.rules)
            if not pkg or not pkg.is_fdd_format():
                continue
            template_path_str = pkg.get_template_path(artifact_meta.kind)
            artifact_path = (project_root / artifact_meta.path).resolve()
            template_path = (project_root / template_path_str).resolve()
            if artifact_path.exists() and template_path.exists():
                artifacts_to_scan.append((artifact_path, template_path, artifact_meta.kind))

        if not artifacts_to_scan:
            print(json.dumps({"status": "ERROR", "message": "No FDD-format artifacts found in registry."}, indent=None, ensure_ascii=False))
            return 1

    # Parse artifacts and collect IDs
    hits: List[Dict[str, object]] = []

    for artifact_path, template_path, artifact_type in artifacts_to_scan:
        tmpl, errs = Template.from_path(template_path)
        if errs or tmpl is None:
            continue

        parsed: TemplateArtifact = tmpl.parse(artifact_path)
        parsed._extract_ids_and_refs()  # Populate id_definitions and id_references

        # Collect ID definitions
        for id_def in parsed.id_definitions:
            block_kind = id_def.block.template_block.name if id_def.block else None
            h: Dict[str, object] = {
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
    if args.include_code and not args.artifact:
        # Find adapter and scan codebase entries
        adapter_dir = find_adapter_directory(Path.cwd())
        if adapter_dir:
            registry, _ = load_artifacts_registry(adapter_dir)
            if registry:
                from .utils.artifacts_meta import ArtifactsMeta
                meta = ArtifactsMeta.from_dict(registry)
                project_root = (adapter_dir / meta.project_root).resolve()

                for cb_entry, system_node in meta.iter_all_codebase():
                    code_path = (project_root / cb_entry.path).resolve()
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
    p = argparse.ArgumentParser(prog="list-id-kinds", description="List ID kinds found in FDD artifacts")
    p.add_argument("--artifact", default=None, help="Scan specific artifact (if omitted, scans all registered FDD artifacts)")
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
                pkg = meta.get_rule(system_node.rules)
                if pkg and pkg.is_fdd_format():
                    template_path_str = pkg.get_template_path(artifact_meta.kind)
                    template_path = (project_root / template_path_str).resolve()
                    artifacts_to_scan.append((artifact_path, template_path, artifact_meta.kind))

        if not artifacts_to_scan:
            print(json.dumps({"status": "ERROR", "message": f"Artifact not found in registry: {args.artifact}"}, indent=None, ensure_ascii=False))
            return 1
    else:
        # Scan all FDD artifacts
        for artifact_meta, system_node in meta.iter_all_artifacts():
            pkg = meta.get_rule(system_node.rules)
            if not pkg or not pkg.is_fdd_format():
                continue
            template_path_str = pkg.get_template_path(artifact_meta.kind)
            artifact_path = (project_root / artifact_meta.path).resolve()
            template_path = (project_root / template_path_str).resolve()
            if artifact_path.exists() and template_path.exists():
                artifacts_to_scan.append((artifact_path, template_path, artifact_meta.kind))

        if not artifacts_to_scan:
            print(json.dumps({"status": "ERROR", "message": "No FDD-format artifacts found in registry."}, indent=None, ensure_ascii=False))
            return 1

    # Parse artifacts and collect kinds that have actual IDs
    template_to_kinds: Dict[str, Set[str]] = {}
    kind_to_templates: Dict[str, Set[str]] = {}
    kind_counts: Dict[str, int] = {}

    for artifact_path, template_path, artifact_type in artifacts_to_scan:
        tmpl, errs = Template.from_path(template_path)
        if errs or tmpl is None:
            continue

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
    """Get content block for a specific FDD ID using template-based parsing."""
    p = argparse.ArgumentParser(prog="get-content", description="Get content block for a specific FDD ID")
    p.add_argument("--artifact", default=None, help="Path to FDD artifact file")
    p.add_argument("--code", default=None, help="Path to code file (alternative to --artifact)")
    p.add_argument("--id", required=True, help="FDD ID to retrieve content for")
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

    from .utils.artifacts_meta import load_artifacts_meta

    # Find adapter and load artifacts meta
    adapter_dir = find_adapter_directory(artifact_path.parent)
    if adapter_dir is None:
        print(json.dumps({"status": "ERROR", "message": "No adapter found"}, indent=None, ensure_ascii=False))
        return 1

    meta, err = load_artifacts_meta(adapter_dir)
    if err or meta is None:
        print(json.dumps({"status": "ERROR", "message": err or "Failed to load artifacts meta"}, indent=None, ensure_ascii=False))
        return 1

    # Get project root from meta
    project_root = (adapter_dir / meta.project_root).resolve()

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
    template_path_str = meta.get_template_for_artifact(artifact_meta, system)
    if template_path_str is None:
        print(json.dumps({"status": "ERROR", "message": f"No template found for artifact type: {artifact_meta.type}"}, indent=None, ensure_ascii=False))
        return 1

    # Load template and parse artifact
    template_path = meta.resolve_template_path(template_path_str, adapter_dir)
    tmpl, errs = Template.from_path(template_path)
    if errs or tmpl is None:
        print(json.dumps({"status": "ERROR", "message": f"Failed to load template: {errs}"}, indent=None, ensure_ascii=False))
        return 1

    artifact = tmpl.parse(artifact_path)
    content = artifact.get(args.id)

    if content is None:
        print(json.dumps({"status": "NOT_FOUND", "id": args.id}, indent=None, ensure_ascii=False))
        return 2

    print(json.dumps({"status": "FOUND", "id": args.id, "text": content}, indent=None, ensure_ascii=False))
    return 0


def _cmd_where_defined(argv: List[str]) -> int:
    """Find where an FDD ID is defined using template-based parsing."""
    p = argparse.ArgumentParser(prog="where-defined", description="Find where an FDD ID is defined")
    p.add_argument("--id", required=True, help="FDD ID to find definition for")
    p.add_argument("--artifact", default=None, help="Limit search to specific artifact (optional)")
    args = p.parse_args(argv)

    target_id = str(args.id).strip()
    if not target_id:
        print(json.dumps({"status": "ERROR", "message": "ID cannot be empty"}, indent=None, ensure_ascii=False))
        return 1

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

    # Collect artifacts to scan
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
                pkg = meta.get_rule(system_node.rules)
                if pkg and pkg.is_fdd_format():
                    template_path_str = pkg.get_template_path(artifact_meta.kind)
                    template_path = (project_root / template_path_str).resolve()
                    artifacts_to_scan.append((artifact_path, template_path, artifact_meta.kind))
        if not artifacts_to_scan:
            print(json.dumps({"status": "ERROR", "message": f"Artifact not in FDD registry: {args.artifact}"}, indent=None, ensure_ascii=False))
            return 1
    else:
        # Scan all FDD artifacts
        for artifact_meta, system_node in meta.iter_all_artifacts():
            pkg = meta.get_rule(system_node.rules)
            if not pkg or not pkg.is_fdd_format():
                continue
            template_path_str = pkg.get_template_path(artifact_meta.kind)
            artifact_path = (project_root / artifact_meta.path).resolve()
            template_path = (project_root / template_path_str).resolve()
            if artifact_path.exists() and template_path.exists():
                artifacts_to_scan.append((artifact_path, template_path, artifact_meta.kind))

    if not artifacts_to_scan:
        print(json.dumps({"status": "ERROR", "message": "No FDD artifacts found in registry"}, indent=None, ensure_ascii=False))
        return 1

    # Search for definitions
    definitions: List[Dict[str, object]] = []

    for artifact_path, template_path, artifact_type in artifacts_to_scan:
        tmpl, errs = Template.from_path(template_path)
        if errs or tmpl is None:
            continue

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
    """Find all references to an FDD ID using template-based parsing."""
    p = argparse.ArgumentParser(prog="where-used", description="Find all references to an FDD ID")
    p.add_argument("--id", required=True, help="FDD ID to find references for")
    p.add_argument("--artifact", default=None, help="Limit search to specific artifact (optional)")
    p.add_argument("--include-definitions", action="store_true", help="Include definitions in results")
    args = p.parse_args(argv)

    target_id = str(args.id).strip()
    if not target_id:
        print(json.dumps({"status": "ERROR", "message": "ID cannot be empty"}, indent=None, ensure_ascii=False))
        return 1

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

    # Collect artifacts to scan
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
                pkg = meta.get_rule(system_node.rules)
                if pkg and pkg.is_fdd_format():
                    template_path_str = pkg.get_template_path(artifact_meta.kind)
                    template_path = (project_root / template_path_str).resolve()
                    artifacts_to_scan.append((artifact_path, template_path, artifact_meta.kind))
        if not artifacts_to_scan:
            print(json.dumps({"status": "ERROR", "message": f"Artifact not in FDD registry: {args.artifact}"}, indent=None, ensure_ascii=False))
            return 1
    else:
        # Scan all FDD artifacts
        for artifact_meta, system_node in meta.iter_all_artifacts():
            pkg = meta.get_rule(system_node.rules)
            if not pkg or not pkg.is_fdd_format():
                continue
            template_path_str = pkg.get_template_path(artifact_meta.kind)
            artifact_path = (project_root / artifact_meta.path).resolve()
            template_path = (project_root / template_path_str).resolve()
            if artifact_path.exists() and template_path.exists():
                artifacts_to_scan.append((artifact_path, template_path, artifact_meta.kind))

    if not artifacts_to_scan:
        print(json.dumps({"status": "ERROR", "message": "No FDD artifacts found in registry"}, indent=None, ensure_ascii=False))
        return 1

    # Search for references
    references: List[Dict[str, object]] = []

    for artifact_path, template_path, artifact_type in artifacts_to_scan:
        tmpl, errs = Template.from_path(template_path)
        if errs or tmpl is None:
            continue

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
# CODE VALIDATION COMMAND
# =============================================================================

def _cmd_validate_code(argv: List[str]) -> int:
    """Validate FDD traceability markers in code files.

    Checks that:
    - All @fdd-begin markers have matching @fdd-end
    - Block markers are not empty
    - Code markers reference IDs that exist in artifacts
    - All to_code="true" IDs have code markers (coverage)
    - Respects traceability mode (FULL vs DOCS-ONLY)
    """
    p = argparse.ArgumentParser(prog="validate-code", description="Validate FDD code traceability markers")
    p.add_argument("path", nargs="?", default=None, help="Path to code file or directory (defaults to codebase from artifacts.json)")
    p.add_argument("--system", default=None, help="System name to validate (if omitted, validates all systems)")
    p.add_argument("--verbose", action="store_true", help="Print full validation report")
    p.add_argument("--output", default=None, help="Output file for JSON report")
    args = p.parse_args(argv)

    # Find project root and adapter
    project_root = find_project_root(Path.cwd())
    if not project_root:
        print(json.dumps({"status": "ERROR", "message": "Not in FDD project"}, indent=None, ensure_ascii=False))
        return 1

    adapter_dir = find_adapter_directory(project_root)
    if not adapter_dir:
        print(json.dumps({"status": "ERROR", "message": "Adapter directory not found"}, indent=None, ensure_ascii=False))
        return 1

    reg, reg_err = load_artifacts_registry(adapter_dir)
    if reg_err or not isinstance(reg, dict):
        print(json.dumps({"status": "ERROR", "message": reg_err or "Invalid artifacts registry"}, indent=None, ensure_ascii=False))
        return 1

    # Collect artifact IDs and to_code IDs from all artifacts
    from .utils.template import Template, cross_validate_artifacts

    artifact_ids: Set[str] = set()
    to_code_ids: Set[str] = set()
    parsed_artifacts: List[TemplateArtifact] = []

    rules = reg.get("rules", {})
    systems = reg.get("systems", [])
    project_root_from_reg = reg.get("project_root", "..")

    def resolve_path(p: str) -> Path:
        rel = Path(project_root_from_reg) / p
        return (adapter_dir / rel).resolve()

    def process_system(system: dict, filter_system: Optional[str]) -> None:
        system_name = system.get("name", "")
        if filter_system and system_name != filter_system:
            for child in system.get("children", []):
                process_system(child, filter_system)
            return

        rules_name = system.get("rules", "")
        rule_cfg = rules.get(rules_name, {})
        rules_base = rule_cfg.get("path", "")

        # Process artifacts to collect IDs
        for art_cfg in system.get("artifacts", []):
            art_path = resolve_path(art_cfg.get("path", ""))
            art_kind = art_cfg.get("kind", "")
            if not art_path.is_file():
                continue

            # Find template
            template_path = resolve_path(f"{rules_base}/artifacts/{art_kind}/template.md")
            if not template_path.is_file():
                continue

            tmpl, errs = Template.from_path(template_path)
            if errs or tmpl is None:
                continue

            artifact = tmpl.parse(art_path)
            artifact._extract_ids_and_refs()
            parsed_artifacts.append(artifact)

            for d in artifact.id_definitions:
                artifact_ids.add(d.id)
                if d.to_code:
                    to_code_ids.add(d.id)

        # Recurse into children
        for child in system.get("children", []):
            process_system(child, filter_system)

    for system in systems:
        process_system(system, args.system)

    # Now scan code files
    all_errors: List[Dict[str, object]] = []
    all_warnings: List[Dict[str, object]] = []
    code_files_scanned: List[Dict[str, object]] = []
    code_ids_found: Set[str] = set()

    def scan_codebase_entry(entry: dict, traceability: str) -> None:
        code_path = resolve_path(entry.get("path", ""))
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
            if errs:
                all_errors.extend(errs)
                continue

            if cf is None:
                continue

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
            elif traceability == "DOCS-ONLY":
                # In DOCS-ONLY mode, markers are prohibited
                if cf.scope_markers or cf.block_markers:
                    all_errors.append({
                        "type": "traceability",
                        "message": "FDD markers found but traceability is DOCS-ONLY",
                        "path": str(file_path),
                        "line": 1,
                    })

    # If path specified, validate just that
    if args.path:
        target_path = Path(args.path).resolve()
        scan_codebase_entry({"path": str(target_path), "extensions": [target_path.suffix or ".py"]}, "FULL")
    else:
        # Scan all codebase entries from systems
        def scan_system_codebase(system: dict, filter_system: Optional[str]) -> None:
            system_name = system.get("name", "")
            if filter_system and system_name != filter_system:
                for child in system.get("children", []):
                    scan_system_codebase(child, filter_system)
                return

            for cb_entry in system.get("codebase", []):
                # Determine traceability from system artifacts
                traceability = "FULL"  # default
                for art in system.get("artifacts", []):
                    if art.get("traceability") == "DOCS-ONLY":
                        traceability = "DOCS-ONLY"
                        break
                scan_codebase_entry(cb_entry, traceability)

            for child in system.get("children", []):
                scan_system_codebase(child, filter_system)

        for system in systems:
            scan_system_codebase(system, args.system)

    # Check for missing code markers (to_code IDs without markers)
    missing_ids = to_code_ids - code_ids_found
    for missing_id in sorted(missing_ids):
        all_errors.append({
            "type": "coverage",
            "message": "ID marked to_code=\"true\" has no code marker",
            "id": missing_id,
        })

    # Build report
    overall_status = "PASS" if not all_errors else "FAIL"

    report: Dict[str, object] = {
        "status": overall_status,
        "code_files_scanned": len(code_files_scanned),
        "artifact_ids_total": len(artifact_ids),
        "to_code_ids_total": len(to_code_ids),
        "code_ids_found": len(code_ids_found),
        "coverage": f"{len(code_ids_found & to_code_ids)}/{len(to_code_ids)}" if to_code_ids else "N/A",
        "error_count": len(all_errors),
        "warning_count": len(all_warnings),
    }

    # Add next step hint
    if overall_status == "PASS":
        report["next_step"] = "Code traceability validation passed. Review implementation against design requirements."

    if args.verbose:
        report["code_files"] = code_files_scanned
        report["errors"] = all_errors
        report["warnings"] = all_warnings
        report["artifact_ids"] = sorted(artifact_ids)
        report["to_code_ids"] = sorted(to_code_ids)
        report["code_ids_found"] = sorted(code_ids_found)
        if missing_ids:
            report["missing_coverage"] = sorted(missing_ids)
    else:
        if all_errors:
            report["errors"] = all_errors[:20]
            if len(all_errors) > 20:
                report["errors_truncated"] = len(all_errors) - 20

    out = json.dumps(report, indent=2 if args.verbose else None, ensure_ascii=False)
    if args.verbose:
        out += "\n"

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)

    return 0 if overall_status == "PASS" else 2


# =============================================================================
# TEMPLATE VALIDATION COMMAND
# =============================================================================

def _cmd_validate_rules(argv: List[str]) -> int:
    """Validate FDD rules configuration and template files.

    Checks that:
    - Rules are properly configured in artifacts.json
    - Templates have valid fdd-template frontmatter (kind, version)
    - All FDD markers are properly paired (open/close)
    - Marker types and attributes are valid
    """
    p = argparse.ArgumentParser(prog="validate-rules", description="Validate FDD rules and template files")
    p.add_argument("--rule", default=None, help="Rule ID to validate (if omitted, validates all rules)")
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
        # Collect unique template paths from all FDD artifacts
        seen_paths: Set[str] = set()
        for artifact_meta, system_node in meta.iter_all_artifacts():
            pkg = meta.get_rule(system_node.rules)
            if not pkg or not pkg.is_fdd_format():
                continue
            template_path_str = pkg.get_template_path(artifact_meta.kind)
            tmpl_path = (project_root / template_path_str).resolve()
            if tmpl_path.as_posix() not in seen_paths and tmpl_path.exists():
                seen_paths.add(tmpl_path.as_posix())
                templates_to_validate.append(tmpl_path)

        if not templates_to_validate:
            print(json.dumps({"status": "ERROR", "message": "No FDD templates found in registry"}, indent=None, ensure_ascii=False))
            return 1

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
    Discover and display FDD adapter information.
    Shows adapter location, project name, and available specs.
    """
    p = argparse.ArgumentParser(prog="adapter-info", description="Discover FDD adapter configuration")
    p.add_argument("--root", default=".", help="Project root to search from (default: current directory)")
    p.add_argument("--fdd-root", default=None, help="FDD core location (if agent knows it)")
    args = p.parse_args(argv)
    
    start_path = Path(args.root).resolve()
    fdd_root_path = Path(args.fdd_root).resolve() if args.fdd_root else None
    
    # Find project root
    project_root = find_project_root(start_path)
    if project_root is None:
        print(json.dumps(
            {
                "status": "NOT_FOUND",
                "message": "No project root found (no .git or .fdd-config.json)",
                "searched_from": start_path.as_posix(),
                "hint": "Create .fdd-config.json in project root to configure FDD",
            },
            indent=2,
            ensure_ascii=False,
        ))
        return 1
    
    # Find adapter
    adapter_dir = find_adapter_directory(start_path, fdd_root=fdd_root_path)
    if adapter_dir is None:
        # Check if config exists to provide better error message
        cfg = load_project_config(project_root)
        if cfg is not None:
            adapter_rel = cfg.get("fddAdapterPath")
            if adapter_rel is not None and isinstance(adapter_rel, str):
                # Config exists but path is invalid
                print(json.dumps(
                    {
                        "status": "CONFIG_ERROR",
                        "message": f"Config specifies adapter path but directory not found or invalid",
                        "project_root": project_root.as_posix(),
                        "config_path": adapter_rel,
                        "expected_location": (project_root / adapter_rel).as_posix(),
                        "hint": "Check .fdd-config.json fddAdapterPath points to valid directory with AGENTS.md",
                    },
                    indent=2,
                    ensure_ascii=False,
                ))
                return 1
        
        # No config, no adapter found via recursive search
        print(json.dumps(
            {
                "status": "NOT_FOUND",
                "message": "No FDD-Adapter found in project (searched recursively up to 5 levels deep)",
                "project_root": project_root.as_posix(),
                "hint": "Create .fdd-config.json with fddAdapterPath or run adapter-bootstrap workflow",
            },
            indent=2,
            ensure_ascii=False,
        ))
        return 1
    
    # Load adapter config
    config = load_adapter_config(adapter_dir)
    config["status"] = "FOUND"
    config["project_root"] = project_root.as_posix()
    
    # Calculate relative path
    try:
        relative_path = adapter_dir.relative_to(project_root).as_posix()
    except ValueError:
        relative_path = adapter_dir.as_posix()
    config["relative_path"] = relative_path
    
    # Check if .fdd-config.json exists
    config_file = project_root / ".fdd-config.json"
    config["has_config"] = config_file.exists()
    if not config_file.exists():
        config["config_hint"] = f"Create .fdd-config.json with: {{\"fddAdapterPath\": \"{relative_path}\"}}"
    
    print(json.dumps(config, indent=2, ensure_ascii=False))
    return 0


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main(argv: Optional[List[str]] = None) -> int:
    argv_list = list(argv) if argv is not None else sys.argv[1:]
    
    # Define all available commands
    validation_commands = ["validate", "validate-code", "validate-rules"]
    search_commands = [
        "init",
        "list-ids", "list-id-kinds",
        "get-content",
        "where-defined", "where-used",
        "adapter-info",
        "self-check",
        "agent-workflows",
        "agent-skills",
    ]
    all_commands = validation_commands + search_commands

    if not argv_list:
        print(json.dumps({
            "status": "ERROR",
            "message": "Missing subcommand",
            "validation_commands": validation_commands,
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
        return _cmd_validate_code(rest)
    elif cmd == "validate-rules":
        return _cmd_validate_rules(rest)
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
    elif cmd == "agent-workflows":
        return _cmd_agent_workflows(rest)
    elif cmd == "agent-skills":
        return _cmd_agent_skills(rest)
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
