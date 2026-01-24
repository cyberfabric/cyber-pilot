"""
FDD Validator - CLI Entry Point

Command-line interface for the FDD validation tool.
"""

import sys
import os
import json
import re
import fnmatch
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Set, Tuple

from .validation.artifacts import validate
from .validation.traceability import (
    validate_codebase_traceability,
    validate_code_root_traceability,
)
from .validation.fdl import validate_fdl_completion
from .utils import (
    detect_requirements,
    load_text,
    parse_required_sections,
    split_by_section_letter,
)
from .utils.files import (
    find_project_root,
    load_project_config,
    find_adapter_directory,
    load_adapter_config,
)
from .utils.document import detect_artifact_kind
from .utils.markdown import (
    extract_block,
    extract_id_block,
    extract_id_payload_block,
    find_anchor_idx_for_id,
    find_id_line,
    list_items,
    list_section_entries,
    read_change_block,
    read_feature_entry,
    read_heading_block_by_title,
    read_letter_section,
    resolve_under_heading,
)
from .utils.search import (
    list_ids,
    parse_trace_query,
    scan_ids,
    search_lines,
    where_defined_internal,
    where_used,
)
from . import constants


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
    except Exception:
        return None


def _write_json_file(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _truncate_list(xs: object, limit: int) -> list:
    if not isinstance(xs, list):
        return []
    return xs[: max(0, int(limit))]


def _summarize_validate_report(report: Dict[str, object]) -> Dict[str, object]:
    status = report.get("status")
    out: Dict[str, object] = {
        "status": status,
    }
    if "artifact_kind" in report:
        out["artifact_kind"] = report.get("artifact_kind")
    if "code_traceability_skipped" in report:
        out["code_traceability_skipped"] = report.get("code_traceability_skipped")
    if "path" in report:
        out["path"] = report.get("path")
    if "code_root" in report:
        out["code_root"] = report.get("code_root")
    if "feature_dir" in report:
        out["feature_dir"] = report.get("feature_dir")

    errs = list(report.get("errors", []) or [])
    if status != "PASS" and errs:
        out["error_count"] = len(errs)
        out["errors"] = _truncate_list(errs, 50)

    av = report.get("artifact_validation")
    if isinstance(av, dict):
        failures: Dict[str, object] = {}
        pass_count = 0
        fail_count = 0
        for k, v in av.items():
            if not isinstance(v, dict):
                continue
            st = v.get("status")
            if st == "PASS":
                pass_count += 1
                continue
            fail_count += 1
            v_errs = list(v.get("errors", []) or [])
            v_ph = list(v.get("placeholder_hits", []) or [])
            item: Dict[str, object] = {
                "status": st,
                "error_count": len(v_errs),
                "placeholder_count": len(v_ph),
            }
            if "path" in v:
                item["path"] = v.get("path")
            if v_errs:
                item["errors"] = _truncate_list(v_errs, 50)
            if v_ph:
                item["placeholder_hits"] = _truncate_list(v_ph, 50)
            failures[str(k)] = item
        out["artifact_validation"] = {
            "pass_count": pass_count,
            "fail_count": fail_count,
        }
        if failures:
            out["artifact_failures"] = failures

    t = report.get("traceability")
    if isinstance(t, dict):
        t_out: Dict[str, object] = {
            "feature_dir": t.get("feature_dir"),
            "scan_root": t.get("scan_root"),
            "feature_design": t.get("feature_design"),
            "feature_changes": t.get("feature_changes"),
            "scanned_file_count": t.get("scanned_file_count"),
        }
        missing = t.get("missing")
        if status != "PASS" and isinstance(missing, dict):
            scopes = missing.get("scopes")
            inst = missing.get("instruction_tags")
            if isinstance(scopes, dict):
                t_out["missing_scopes"] = {
                    str(k): _truncate_list(v, 20) for k, v in scopes.items() if isinstance(v, list) and v
                }
                t_out["missing_scope_count"] = sum(len(v) for v in scopes.values() if isinstance(v, list))
            if isinstance(inst, list):
                t_out["missing_instruction_tag_count"] = len(inst)
                if inst:
                    t_out["missing_instruction_tags"] = _truncate_list(inst, 20)
        out["traceability"] = t_out

    fr = report.get("feature_reports")
    if isinstance(fr, list):
        passed = 0
        failed = 0
        failing: List[Dict[str, object]] = []
        for item in fr:
            if not isinstance(item, dict):
                continue
            st = item.get("status")
            if st == "PASS":
                passed += 1
                continue
            failed += 1
            item_errs = list(item.get("errors", []) or [])
            item_trace = item.get("traceability")
            trace_out: Optional[Dict[str, object]] = None
            if isinstance(item_trace, dict):
                t_out: Dict[str, object] = {
                    "feature_dir": item_trace.get("feature_dir") or item.get("feature_dir"),
                    "scan_root": item_trace.get("scan_root"),
                    "feature_design": item_trace.get("feature_design"),
                    "feature_changes": item_trace.get("feature_changes"),
                    "scanned_file_count": item_trace.get("scanned_file_count"),
                }
                missing = item_trace.get("missing")
                if st != "PASS" and isinstance(missing, dict):
                    scopes = missing.get("scopes")
                    inst = missing.get("instruction_tags")
                    if isinstance(scopes, dict):
                        t_out["missing_scopes"] = {
                            str(k): _truncate_list(v, 20)
                            for k, v in scopes.items()
                            if isinstance(v, list) and v
                        }
                        t_out["missing_scope_count"] = sum(
                            len(v) for v in scopes.values() if isinstance(v, list)
                        )
                    if isinstance(inst, list):
                        t_out["missing_instruction_tag_count"] = len(inst)
                        if inst:
                            t_out["missing_instruction_tags"] = _truncate_list(inst, 20)
                trace_out = t_out
            failing.append(
                {
                    "feature_dir": item.get("feature_dir"),
                    "status": st,
                    "error_count": len(item_errs),
                    "errors": _truncate_list(item_errs, 50) if item_errs else [],
                    "traceability": trace_out,
                }
            )
        out["feature_reports"] = {
            "feature_count": report.get("feature_count"),
            "pass_count": passed,
            "fail_count": failed,
            "failures": failing,
        }

    return out


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


def _looks_like_generated_proxy(text: str, target_workflow_rel: str) -> bool:
    # Heuristic: file contains ALWAYS open and follow with the expected target path.
    # This avoids hardcoding tool-specific markers in generated files.
    needle = f"ALWAYS open and follow `{target_workflow_rel}`"
    return needle in text


def _list_fdd_workflows(fdd_root: Path) -> List[str]:
    workflows_dir = fdd_root / "workflows"
    if not workflows_dir.is_dir():
        raise SystemExit(f"FDD workflows dir not found: {workflows_dir}")

    names: List[str] = []
    for pth in sorted(workflows_dir.glob("*.md")):
        if pth.name in ("AGENTS.md", "README.md"):
            continue
        try:
            head = "\n".join(pth.read_text(encoding="utf-8").splitlines()[:30])
        except Exception:
            continue
        if "type: workflow" not in head:
            continue
        names.append(pth.stem)
    return names


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
    fdd_workflow_names = _list_fdd_workflows(fdd_root)

    desired: Dict[str, Dict[str, str]] = {}
    for wf_name in fdd_workflow_names:
        command = f"{prefix}{wf_name}"
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
        if "/workflows/" not in target_rel:
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
            except Exception:
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
    desired_agents = "\n".join([
        f"# FDD Adapter: {project_name}",
        "",
        f"**Extends**: `{extends_rel}`",
        "",
    ])

    desired_cfg = _default_project_config(core_rel, adapter_rel)

    actions: Dict[str, str] = {}
    errors: List[Dict[str, str]] = []

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

    if errors:
        print(json.dumps({
            "status": "ERROR",
            "message": "Init failed",
            "project_root": project_root.as_posix(),
            "fdd_root": fdd_root.as_posix(),
            "config_path": config_path.as_posix(),
            "adapter_dir": adapter_dir.as_posix(),
            "dry_run": bool(args.dry_run),
            "errors": errors,
        }, indent=2, ensure_ascii=False))
        return 1

    print(json.dumps({
        "status": "PASS",
        "project_root": project_root.as_posix(),
        "fdd_root": fdd_root.as_posix(),
        "config_path": config_path.as_posix(),
        "adapter_dir": adapter_dir.as_posix(),
        "dry_run": bool(args.dry_run),
        "actions": actions,
    }, indent=2, ensure_ascii=False))
    return 0


# =============================================================================
def _cmd_validate(argv: List[str]) -> int:
    """
    Validation command handler - wraps validate() function.
    """
    p = argparse.ArgumentParser(prog="validate")
    p.add_argument("--artifact", default=".", help="Path to artifact to validate (default: current directory = validate all)")
    p.add_argument("--requirements", default=None, help="Path to requirements file (optional, auto-detected)")
    p.add_argument("--design", default=None, help="Path to DESIGN.md for cross-references")
    p.add_argument("--business", default=None, help="Path to BUSINESS.md for cross-references")
    p.add_argument("--adr", default=None, help="Path to architecture/ADR/ for cross-references")
    p.add_argument("--skip-fs-checks", action="store_true", help="Skip filesystem checks")
    p.add_argument("--skip-code-traceability", action="store_true", help="Skip code traceability validation (only validate artifacts)")
    p.add_argument("--verbose", action="store_true", help="Print full report (default: summary with errors only)")
    p.add_argument("--output", default=None, help="Write report to file instead of stdout")
    p.add_argument("--features", default=None, help="Comma-separated feature slugs for code-root traceability")
    args = p.parse_args(argv)

    artifact_path = Path(args.artifact).resolve()
    
    # Check .fdd-config.json for skip-code-traceability setting
    skip_code_traceability = args.skip_code_traceability
    config_path = artifact_path / ".fdd-config.json" if artifact_path.is_dir() else artifact_path.parent / ".fdd-config.json"
    if not skip_code_traceability and config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            skip_code_traceability = config.get("skipCodeTraceability", False)
        except (json.JSONDecodeError, OSError):
            pass

    if artifact_path.is_dir():
        from .validation.cascade import validate_all_artifacts
        
        # ADR directory mode (artifact is architecture/ADR/ or named ADR)
        if artifact_path.name == "ADR" or (artifact_path / "general").exists():
            from .validation.cascade import validate_with_dependencies
            report = validate_with_dependencies(
                artifact_path,
                skip_fs_checks=bool(args.skip_fs_checks),
            )
            out_report = report if args.verbose else _summarize_validate_report(report)
            out = json.dumps(out_report, indent=2, ensure_ascii=False) + "\n"
            if args.output:
                Path(args.output).write_text(out, encoding="utf-8")
            else:
                print(out, end="")
            return 0 if report["status"] == "PASS" else 2
        
        # Backwards-compatible: feature directory mode (artifact contains DESIGN.md).
        if (artifact_path / "DESIGN.md").exists():
            if args.features:
                raise SystemExit("--features is only supported when --artifact is a code root directory")
            if skip_code_traceability:
                # Only validate the artifact, skip code traceability
                from .validation.cascade import validate_with_dependencies
                report = validate_with_dependencies(
                    artifact_path / "DESIGN.md",
                    skip_fs_checks=bool(args.skip_fs_checks),
                )
            else:
                report = validate_codebase_traceability(
                    artifact_path,
                    feature_design_path=Path(args.design).resolve() if args.design else None,
                    feature_changes_path=None,
                    skip_fs_checks=bool(args.skip_fs_checks),
                )
            report["artifact_kind"] = "codebase-trace"
        else:
            # First validate all FDD artifacts
            artifacts_report = validate_all_artifacts(
                artifact_path,
                skip_fs_checks=bool(args.skip_fs_checks),
            )
            
            if skip_code_traceability:
                # Only artifact validation, no code traceability
                report = {
                    "status": artifacts_report.get("status", "PASS"),
                    "artifact_kind": "codebase-trace",
                    "artifact_validation": artifacts_report.get("artifact_validation", {}),
                    "code_traceability_skipped": True,
                }
            else:
                # Then validate codebase traceability
                slugs: Optional[List[str]] = None
                if args.features:
                    slugs = [x.strip() for x in str(args.features).split(",") if x.strip()]
                trace_report = validate_code_root_traceability(
                    artifact_path,
                    feature_slugs=slugs,
                    skip_fs_checks=bool(args.skip_fs_checks),
                )
                
                # Combine reports
                report = trace_report
                report["artifact_kind"] = "codebase-trace"
                report["artifact_validation"] = artifacts_report.get("artifact_validation", {})
                
                # Overall status fails if either fails
                if artifacts_report.get("status") != "PASS":
                    report["status"] = "FAIL"

        out_report = report if args.verbose else _summarize_validate_report(report)
        out = json.dumps(out_report, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            Path(args.output).write_text(out, encoding="utf-8")
        else:
            print(out, end="")

        return 0 if report["status"] == "PASS" else 2

    # If custom requirements provided, use direct validation (no cascading)
    if args.requirements:
        requirements_path = Path(args.requirements).resolve()
        if not requirements_path.exists() or not requirements_path.is_file():
            raise SystemExit(f"Requirements file not found: {requirements_path}")
        
        artifact_kind, _ = detect_requirements(artifact_path) if artifact_path.name in (
            "BUSINESS.md", "ADR", "FEATURES.md", "CHANGES.md", "DESIGN.md"
        ) else ("custom", None)
        
        report = validate(
            artifact_path,
            requirements_path,
            artifact_kind,
            skip_fs_checks=bool(args.skip_fs_checks),
        )
        report["artifact_kind"] = artifact_kind
    else:
        # Use core cascading validation - automatically discovers and validates all dependencies
        from .validation.cascade import validate_with_dependencies
        
        report = validate_with_dependencies(
            artifact_path,
            skip_fs_checks=bool(args.skip_fs_checks),
        )

    out_report = report if args.verbose else _summarize_validate_report(report)
    out = json.dumps(out_report, indent=2, ensure_ascii=False) + "\n"

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out, end="")

    return 0 if report["status"] == "PASS" else 2


# =============================================================================
# SEARCH COMMANDS
# =============================================================================

def _cmd_list_sections(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="list-sections")
    p.add_argument("--artifact", required=True)
    p.add_argument("--under-heading", default=None)
    args = p.parse_args(argv)

    artifact_path = Path(args.artifact).resolve()
    text, err = load_text(artifact_path)
    if err:
        print(json.dumps({"status": "ERROR", "message": err}, indent=None, ensure_ascii=False))
        return 1
    lines = text.splitlines()
    kind = detect_artifact_kind(artifact_path)
    entries = list_section_entries(lines, kind=kind)
    print(json.dumps({"kind": kind, "count": len(entries), "entries": entries}, indent=None, ensure_ascii=False))
    return 0


def _cmd_list_ids(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="list-ids")
    p.add_argument("--artifact", required=True)
    p.add_argument("--under-heading", default=None)
    p.add_argument("--pattern", default=None)
    p.add_argument("--regex", action="store_true")
    p.add_argument("--all", action="store_true")
    args = p.parse_args(argv)

    artifact_path = Path(args.artifact).resolve()
    text, err = load_text(artifact_path)
    if err:
        print(json.dumps({"status": "ERROR", "message": err}, indent=None, ensure_ascii=False))
        return 1
    lines = text.splitlines()

    base_offset = 0
    if args.under_heading:
        resolved = resolve_under_heading(lines, args.under_heading)
        if resolved is None:
            print(json.dumps({"status": "NOT_FOUND", "heading": args.under_heading}, indent=None, ensure_ascii=False))
            return 1
        start, end, _ = resolved
        base_offset = start
        lines = lines[start:end]

    hits = list_ids(lines=lines, base_offset=base_offset, pattern=args.pattern, regex=bool(args.regex), all_ids=bool(args.all))
    print(json.dumps({"kind": detect_artifact_kind(artifact_path), "count": len(hits), "ids": hits}, indent=None, ensure_ascii=False))
    return 0


def _cmd_list_items(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="list-items", description="List structured items in an artifact")
    p.add_argument("--artifact", required=True)
    p.add_argument("--type", default=None, help="Filter by item type (e.g., actor, capability, requirement, flow)")
    p.add_argument("--lod", default="summary", choices=["id", "summary"], help="Level of detail")
    p.add_argument("--under-heading", default=None, help="Only search/list items inside the specified heading block")
    p.add_argument("--pattern", default=None, help="Substring filter (applied to id)")
    p.add_argument("--regex", action="store_true", help="Treat --pattern as regex")
    args = p.parse_args(argv)

    artifact_path = Path(args.artifact).resolve()
    kind = detect_artifact_kind(artifact_path)

    if kind == "adr" and artifact_path.exists() and artifact_path.is_dir():
        from .utils.helpers import scan_adr_directory

        adrs, issues = scan_adr_directory(artifact_path)
        items: List[Dict[str, object]] = []
        for a in adrs:
            it: Dict[str, object] = {"type": "adr", "id": str(a.get("ref")), "line": 0}
            if args.lod == "summary":
                it.update(
                    {
                        "title": a.get("title"),
                        "date": a.get("date"),
                        "status": a.get("status"),
                        "adr_id": a.get("id"),
                        "path": a.get("path"),
                    }
                )
            items.append(it)

        if args.pattern:
            if args.regex:
                rx = re.compile(str(args.pattern))
                items = [it for it in items if rx.search(str(it.get("id", ""))) is not None]
            else:
                items = [it for it in items if str(args.pattern) in str(it.get("id", ""))]
        if args.type:
            items = [it for it in items if str(it.get("type")) == str(args.type)]

        items = sorted(items, key=lambda it: str(it.get("id", "")))
        print(json.dumps({"kind": kind, "count": len(items), "items": items, "issues": issues}, indent=None, ensure_ascii=False))
        return 0

    text, err = load_text(artifact_path)
    if err:
        print(json.dumps({"status": "ERROR", "message": err}, indent=None, ensure_ascii=False))
        return 1
    lines = text.splitlines()

    active_lines = lines
    base_offset = 0
    if args.under_heading:
        resolved = resolve_under_heading(lines, args.under_heading)
        if resolved is None:
            print(json.dumps({"status": "NOT_FOUND", "kind": kind, "heading": args.under_heading}, indent=None, ensure_ascii=False))
            return 1
        start, end, _ = resolved
        base_offset = start
        active_lines = lines[start:end]

    items = list_items(
        kind=kind,
        artifact_name=artifact_path.name,
        lines=lines,
        active_lines=active_lines,
        base_offset=base_offset,
        lod=str(args.lod),
        pattern=args.pattern,
        regex=bool(args.regex),
        type_filter=args.type,
    )
    print(json.dumps({"kind": kind, "count": len(items), "items": items}, indent=None, ensure_ascii=False))
    return 0


def _cmd_read_section(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="read-section", description="Read a section of an artifact")
    p.add_argument("--artifact", required=True)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--section", help="Top-level letter section (e.g. A, B, C)")
    g.add_argument("--heading", help="Exact heading title to match")
    g.add_argument("--feature-id", help="Feature ID for FEATURES.md entry")
    g.add_argument("--change", type=int, help="Change number for CHANGES.md")
    g.add_argument("--id", help="Any ID to locate, then return its block")
    args = p.parse_args(argv)

    artifact_path = Path(args.artifact).resolve()
    text, err = load_text(artifact_path)
    if err:
        print(json.dumps({"status": "ERROR", "message": err}, indent=None, ensure_ascii=False))
        return 1
    lines = text.splitlines()
    kind = detect_artifact_kind(artifact_path)

    if args.id is not None:
        return _cmd_find_id(["--artifact", str(artifact_path), "--id", args.id])

    if args.feature_id is not None:
        if kind != "features-manifest":
            print(json.dumps({"status": "ERROR", "message": "--feature-id is only supported for FEATURES.md"}, indent=None, ensure_ascii=False))
            return 1
        rng = read_feature_entry(lines, args.feature_id)
        if rng is None:
            print(json.dumps({"status": "NOT_FOUND", "feature_id": args.feature_id}, indent=None, ensure_ascii=False))
            return 1
        start, end = rng
        print(json.dumps({"status": "FOUND", "feature_id": args.feature_id, "text": "\n".join(lines[start:end])}, indent=None, ensure_ascii=False))
        return 0

    if args.change is not None:
        if kind != "feature-changes":
            print(json.dumps({"status": "ERROR", "message": "--change is only supported for CHANGES.md"}, indent=None, ensure_ascii=False))
            return 1
        rng = read_change_block(lines, int(args.change))
        if rng is None:
            print(json.dumps({"status": "NOT_FOUND", "change": args.change}, indent=None, ensure_ascii=False))
            return 1
        start_idx, end = rng
        print(json.dumps({"status": "FOUND", "change": args.change, "text": "\n".join(lines[start_idx:end])}, indent=None, ensure_ascii=False))
        return 0

    if args.section is not None:
        letter = args.section.strip().upper()
        rng = read_letter_section(lines, letter)
        if rng is None:
            print(json.dumps({"status": "NOT_FOUND", "section": letter}, indent=None, ensure_ascii=False))
            return 1
        start_idx, end = rng
        print(json.dumps({"status": "FOUND", "section": letter, "text": "\n".join(lines[start_idx:end])}, indent=None, ensure_ascii=False))
        return 0

    if args.heading is not None:
        title = args.heading.strip()
        rng = read_heading_block_by_title(lines, title)
        if rng is None:
            print(json.dumps({"status": "NOT_FOUND", "heading": title}, indent=None, ensure_ascii=False))
            return 1
        start, end = rng
        print(json.dumps({"status": "FOUND", "heading": title, "text": "\n".join(lines[start:end])}, indent=None, ensure_ascii=False))
        return 0

    print(json.dumps({"status": "ERROR", "message": "No selector provided"}, indent=None, ensure_ascii=False))
    return 1


def _cmd_get_item(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="get-item", description="Get a structured block by id/heading/section/feature/change")
    p.add_argument("--artifact", required=True)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--section")
    g.add_argument("--heading")
    g.add_argument("--feature-id")
    g.add_argument("--change", type=int)
    g.add_argument("--id")
    args = p.parse_args(argv)

    if args.id is not None:
        return _cmd_find_id(["--artifact", args.artifact, "--id", args.id])

    sub: List[str] = ["--artifact", args.artifact]
    if args.section is not None:
        sub.extend(["--section", args.section])
    elif args.heading is not None:
        sub.extend(["--heading", args.heading])
    elif args.feature_id is not None:
        sub.extend(["--feature-id", args.feature_id])
    elif args.change is not None:
        sub.extend(["--change", str(args.change)])

    return _cmd_read_section(sub)


def _cmd_find_id(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="find-id")
    p.add_argument("--artifact", required=True)
    p.add_argument("--id", required=True)
    args = p.parse_args(argv)

    artifact_path = Path(args.artifact).resolve()
    text, err = load_text(artifact_path)
    if err:
        print(json.dumps({"status": "ERROR", "message": err}, indent=None, ensure_ascii=False))
        return 1
    lines = text.splitlines()

    kind = detect_artifact_kind(artifact_path)

    idx = find_id_line(lines, args.id)
    if idx is None:
        print(json.dumps({"status": "NOT_FOUND", "id": args.id}, indent=None, ensure_ascii=False))
        return 1

    anchor = find_anchor_idx_for_id(lines, args.id) or idx
    start, end = extract_id_block(lines, anchor_idx=anchor, id_value=args.id, kind=kind)
    payload = extract_id_payload_block(lines, id_idx=idx)
    payload_out: Optional[Dict[str, object]] = None
    if payload is not None:
        payload_out = {
            "open_line": int(payload["open_idx"]) + 1,
            "close_line": int(payload["close_idx"]) + 1,
            "text": str(payload["text"]),
        }
    print(json.dumps({
        "status": "FOUND",
        "id": args.id,
        "line": idx + 1,
        "payload": payload_out,
        "block_start_line": start + 1,
        "block_end_line": end,
        "text": "\n".join(lines[start:end]),
    }, indent=None, ensure_ascii=False))
    return 0


def _cmd_search(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="search")
    p.add_argument("--artifact", required=True)
    p.add_argument("--query", required=True)
    p.add_argument("--regex", action="store_true")
    args = p.parse_args(argv)

    artifact_path = Path(args.artifact).resolve()
    text, err = load_text(artifact_path)
    if err:
        print(json.dumps({"status": "ERROR", "message": err}, indent=None, ensure_ascii=False))
        return 1
    lines = text.splitlines()

    hits = search_lines(lines=lines, query=str(args.query), regex=bool(args.regex))
    print(json.dumps({"count": len(hits), "hits": hits}, indent=None, ensure_ascii=False))
    return 0


def _cmd_scan_ids(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="scan-ids")
    p.add_argument("--root", required=True)
    p.add_argument("--pattern", default=None)
    p.add_argument("--regex", action="store_true")
    p.add_argument("--kind", default="all", choices=["all", "fdd", "adr"])
    p.add_argument("--all", action="store_true")
    p.add_argument("--include", action="append", default=None)
    p.add_argument("--exclude", action="append", default=None)
    p.add_argument("--max-bytes", type=int, default=1_000_000)
    args = p.parse_args(argv)

    root = Path(args.root).resolve()
    hits = scan_ids(
        root=root,
        pattern=args.pattern,
        regex=bool(args.regex),
        kind=str(args.kind),
        include=args.include,
        exclude=args.exclude,
        max_bytes=int(args.max_bytes),
        all_ids=bool(args.all),
    )
    print(json.dumps({"root": root.as_posix(), "count": len(hits), "ids": hits}, indent=None, ensure_ascii=False))
    return 0


def _cmd_where_defined(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="where-defined", description="Find where an ID is defined")
    p.add_argument("--id", required=True)
    p.add_argument("--root", default=".", help="Root directory to search (default: current working directory)")
    p.add_argument("--include-tags", action="store_true", help="Also treat @fdd-* code tags as definitions")
    p.add_argument("--include", action="append", default=None, help="Glob include filter over relative paths (repeatable)")
    p.add_argument("--exclude", action="append", default=None, help="Glob exclude filter over relative paths (repeatable)")
    p.add_argument("--max-bytes", type=int, default=1_000_000, help="Skip files larger than this size")
    args = p.parse_args(argv)

    raw_id = str(args.id).strip()
    base, phase, inst = parse_trace_query(raw_id)
    root = Path(args.root).resolve()

    _base2, defs, ctx_defs = where_defined_internal(
        root=root,
        raw_id=raw_id,
        include_tags=bool(args.include_tags),
        includes=args.include,
        excludes=args.exclude,
        max_bytes=int(args.max_bytes),
    )

    _ = _base2

    if not defs:
        print(json.dumps(
            {
                "status": "NOT_FOUND",
                "id": raw_id,
                "base_id": base,
                "phase": phase,
                "inst": inst,
                "root": root.as_posix(),
                "count": 0,
                "definitions": [],
                "context_definitions": ctx_defs,
            },
            indent=None,
            ensure_ascii=False,
        ))
        return 1
    status = "FOUND" if len(defs) == 1 else "AMBIGUOUS"
    print(json.dumps(
        {
            "status": status,
            "id": raw_id,
            "base_id": base,
            "phase": phase,
            "inst": inst,
            "root": root.as_posix(),
            "count": len(defs),
            "definitions": defs,
            "context_definitions": ctx_defs,
        },
        indent=None,
        ensure_ascii=False,
    ))
    return 0 if status == "FOUND" else 2


def _cmd_where_used(argv: List[str]) -> int:
    p = argparse.ArgumentParser(prog="where-used", description="Find where an ID is referenced across a repository")
    p.add_argument("--id", required=True)
    p.add_argument("--root", default=".", help="Root directory to search (default: current working directory)")
    p.add_argument("--include", action="append", default=None, help="Glob include filter over relative paths (repeatable)")
    p.add_argument("--exclude", action="append", default=None, help="Glob exclude filter over relative paths (repeatable)")
    p.add_argument("--max-bytes", type=int, default=1_000_000, help="Skip files larger than this size")
    args = p.parse_args(argv)

    raw_id = str(args.id).strip()
    root = Path(args.root).resolve()

    base, phase, inst, hits = where_used(
        root=root,
        raw_id=raw_id,
        include=args.include,
        exclude=args.exclude,
        max_bytes=int(args.max_bytes),
    )
    print(json.dumps({"id": raw_id, "base_id": base, "phase": phase, "inst": inst, "root": root.as_posix(), "count": len(hits), "hits": hits}, indent=None, ensure_ascii=False))
    return 0


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
    validation_commands = ["validate"]
    search_commands = [
        "init",
        "list-sections", "list-ids", "list-items",
        "read-section", "get-item", "find-id",
        "search", "scan-ids",
        "where-defined", "where-used",
        "adapter-info",
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
    elif cmd == "init":
        return _cmd_init(rest)
    elif cmd == "list-sections":
        return _cmd_list_sections(rest)
    elif cmd == "list-ids":
        return _cmd_list_ids(rest)
    elif cmd == "list-items":
        return _cmd_list_items(rest)
    elif cmd == "read-section":
        return _cmd_read_section(rest)
    elif cmd == "get-item":
        return _cmd_get_item(rest)
    elif cmd == "find-id":
        return _cmd_find_id(rest)
    elif cmd == "search":
        return _cmd_search(rest)
    elif cmd == "scan-ids":
        return _cmd_scan_ids(rest)
    elif cmd == "where-defined":
        return _cmd_where_defined(rest)
    elif cmd == "where-used":
        return _cmd_where_used(rest)
    elif cmd == "adapter-info":
        return _cmd_adapter_info(rest)
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
