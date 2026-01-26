"""
FDD Validator - FEATURES.md Validation

Validates features manifest: feature list, status tracking, requirements coverage.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set

from ...constants import (
    FEATURE_HEADING_RE,
    STATUS_OVERVIEW_RE,
    REQ_ID_RE,
    NFR_ID_RE,
    PRINCIPLE_ID_RE,
    CONSTRAINT_ID_RE,
)

from ...utils import find_placeholders, load_text, field_block, has_list_item

from .common import _extract_feature_links, _extract_id_list


__all__ = ["validate_features_manifest"]


def _line_has_field(line: str, field_name: str, *, allow_empty_value: bool) -> bool:
    """Check if line contains a field with the given name."""
    if allow_empty_value:
        return re.match(rf"^\s*[-*]?\s*\*\*{re.escape(field_name)}\*\*:\s*(.*)$", line) is not None
    return re.match(rf"^\s*[-*]?\s*\*\*{re.escape(field_name)}\*\*:\s*.+$", line) is not None


def validate_features_manifest(
    artifact_text: str,
    *,
    artifact_path: Optional[Path] = None,
    design_path: Optional[Path] = None,
    skip_fs_checks: bool = False,
) -> Dict[str, object]:
    errors: List[Dict[str, object]] = []

    lines = artifact_text.splitlines()
    if not lines:
        errors.append({"type": "file", "message": "Empty file"})
        return {
            "required_section_count": 0,
            "missing_sections": [],
            "placeholder_hits": find_placeholders(artifact_text),
            "status": "FAIL",
            "errors": errors,
            "feature_issues": [],
            "feature_count": 0,
        }

    if not re.match(r"^#\s+Features:\s+.+$", lines[0].strip()):
        errors.append({"type": "header", "message": "Missing or invalid title '# Features: {PROJECT_NAME}'", "line": 1})

    overview_line = next((l for l in lines[:120] if "**Status Overview**:" in l), None)
    if overview_line is None:
        errors.append({"type": "header", "message": "Missing '**Status Overview**:'"})

    has_meaning = any(l.strip() == "**Meaning**:" for l in lines[:120])
    if not has_meaning:
        errors.append({"type": "header", "message": "Missing '**Meaning**:'"})

    # Minimal meaning lines check
    meaning_block = "\n".join(lines[:160])
    for emoji in ("⏳", "📝", "📘", "🔄", "✅"):
        if emoji not in meaning_block:
            errors.append({"type": "header", "message": f"Missing meaning entry for '{emoji}'"})

    feature_indices: List[int] = []
    feature_headers: List[Dict[str, object]] = []
    for idx, line in enumerate(lines):
        m = FEATURE_HEADING_RE.match(line.strip())
        if not m:
            continue
        feature_indices.append(idx)
        feature_headers.append(
            {
                "line": idx + 1,
                "number": int(m.group(1)),
                "id": m.group(2),
                "path": m.group(3),
                "emoji": m.group(4),
                "priority": m.group(5),
            }
        )

    if not feature_indices:
        errors.append({"type": "structure", "message": "No feature entries found (expected '### N. [id](feature-.../) EMOJI PRIORITY')"})
    else:
        nums = [h["number"] for h in feature_headers]
        expected = list(range(1, len(nums) + 1))
        if nums != expected:
            errors.append(
                {
                    "type": "structure",
                    "message": "Feature numbering must be sequential starting at 1 with no gaps",
                    "found": nums,
                }
            )

    seen_numbers: Dict[int, int] = {}
    seen_ids: Dict[str, int] = {}
    seen_paths: Dict[str, int] = {}
    for h in feature_headers:
        n = int(h["number"])
        seen_numbers[n] = seen_numbers.get(n, 0) + 1
        fid = str(h["id"]).strip()
        seen_ids[fid] = seen_ids.get(fid, 0) + 1
        p = str(h["path"]).strip()
        seen_paths[p] = seen_paths.get(p, 0) + 1

    dup_numbers = sorted([n for n, c in seen_numbers.items() if c > 1])
    dup_ids = sorted([k for k, c in seen_ids.items() if c > 1])
    dup_paths = sorted([k for k, c in seen_paths.items() if c > 1])
    if dup_numbers:
        errors.append({"type": "structure", "message": "Duplicate feature numbers", "numbers": dup_numbers})
    if dup_ids:
        errors.append({"type": "structure", "message": "Duplicate feature ids", "ids": dup_ids})
    if dup_paths:
        errors.append({"type": "structure", "message": "Duplicate feature paths", "paths": dup_paths})

    path_set = {str(h["path"]) for h in feature_headers}

    if overview_line is not None:
        m_overview = STATUS_OVERVIEW_RE.search(overview_line)
        if not m_overview:
            errors.append({"type": "header", "message": "Invalid Status Overview format"})
        else:
            total = int(m_overview.group(1))
            implemented = int(m_overview.group(2))
            in_development = int(m_overview.group(3))
            design_ready_raw = m_overview.group(4)
            in_design_raw = m_overview.group(5)
            not_started = int(m_overview.group(6))

            design_ready = int(design_ready_raw) if design_ready_raw is not None else 0
            in_design = int(in_design_raw) if in_design_raw is not None else 0

            actual_total = len(feature_headers)
            actual_implemented = sum(1 for h in feature_headers if h["emoji"] == "✅")
            actual_in_development = sum(1 for h in feature_headers if h["emoji"] == "🔄")
            actual_design_ready = sum(1 for h in feature_headers if h["emoji"] == "📘")
            actual_in_design = sum(1 for h in feature_headers if h["emoji"] == "📝")
            actual_not_started = sum(1 for h in feature_headers if h["emoji"] == "⏳")

            if design_ready_raw is None and in_design_raw is None:
                if actual_design_ready != 0 or actual_in_design != 0:
                    errors.append(
                        {
                            "type": "header",
                            "message": "Status Overview uses legacy 3-status format but feature list includes design statuses",
                            "actual": {
                                "design_ready": actual_design_ready,
                                "in_design": actual_in_design,
                            },
                        }
                    )

            declared = {
                "total": total,
                "implemented": implemented,
                "in_development": in_development,
                "design_ready": design_ready,
                "in_design": in_design,
                "not_started": not_started,
            }
            actual = {
                "total": actual_total,
                "implemented": actual_implemented,
                "in_development": actual_in_development,
                "design_ready": actual_design_ready,
                "in_design": actual_in_design,
                "not_started": actual_not_started,
            }

            if declared != actual:
                errors.append(
                    {
                        "type": "header",
                        "message": "Status Overview counts do not match feature entries",
                        "declared": declared,
                        "actual": actual,
                    }
                )

    design_ids: Dict[str, set] = {"req": set(), "principle": set(), "constraint": set()}
    covered_ids: Dict[str, set] = {"req": set(), "principle": set(), "constraint": set()}
    dep_graph: Dict[str, List[str]] = {}
    if not skip_fs_checks and artifact_path is not None:
        resolved_design = design_path
        if resolved_design is None:
            resolved_design = artifact_path.parent.parent / "DESIGN.md"
        if not resolved_design.exists() or not resolved_design.is_file():
            errors.append({"type": "cross", "message": "DESIGN.md not found for cross-check", "path": str(resolved_design)})
        else:
            dt = resolved_design.read_text(encoding="utf-8")
            design_ids["req"].update(REQ_ID_RE.findall(dt))
            design_ids["req"].update(NFR_ID_RE.findall(dt))
            design_ids["principle"].update(PRINCIPLE_ID_RE.findall(dt))
            design_ids["constraint"].update(CONSTRAINT_ID_RE.findall(dt))

    required_fields: List[Tuple[str, bool]] = [
        ("Purpose", False),
        ("Status", False),
        ("Depends On", True),
        ("Blocks", True),
        ("Scope", True),
        ("Requirements Covered", True),
        ("Phases", True),
    ]

    feature_issues: List[Dict[str, object]] = []
    for i, header in enumerate(feature_headers):
        start = feature_indices[i]
        end = feature_indices[i + 1] if i + 1 < len(feature_indices) else len(lines)
        block_lines = lines[start:end]

        missing_fields = [
            field
            for (field, allow_empty) in required_fields
            if not any(_line_has_field(l, field, allow_empty_value=allow_empty) for l in block_lines)
        ]

        phases_block_initial = field_block(block_lines, "Phases")
        phases_ok = phases_block_initial is not None and "`ph-1`" in "\n".join([block_lines[phases_block_initial["index"]]] + list(phases_block_initial["tail"]))

        empty_list_fields: List[str] = []
        for field_name in ("Depends On", "Blocks", "Scope", "Requirements Covered", "Phases"):
            fb = field_block(block_lines, field_name)
            if fb is None:
                continue
            inline_value = str(fb["value"]).strip()
            if inline_value:
                continue
            if field_name in ("Depends On", "Blocks"):
                if inline_value == "None":
                    continue
            if has_list_item(list(fb["tail"])):
                continue
            empty_list_fields.append(field_name)

        status_mismatch: Optional[str] = None
        invalid_status: Optional[str] = None
        status_value: Optional[str] = None
        status_field = field_block(block_lines, "Status")
        valid_statuses = {"NOT_STARTED", "IN_DESIGN", "DESIGN_READY", "IN_DEVELOPMENT", "IMPLEMENTED"}
        status_to_emoji = {
            "NOT_STARTED": "⏳",
            "IN_DESIGN": "📝",
            "DESIGN_READY": "📘",
            "IN_DEVELOPMENT": "🔄",
            "IMPLEMENTED": "✅",
        }
        if status_field is not None:
            status_value = str(status_field["value"]).strip()
            if status_value == "IN_PROGRESS":
                status_value = "IN_DEVELOPMENT"
            # Validate status value is one of the allowed values
            if status_value not in valid_statuses:
                invalid_status = (
                    "Status must be one of: NOT_STARTED, IN_DESIGN, DESIGN_READY, IN_DEVELOPMENT, IMPLEMENTED "
                    f"(found: '{status_value}')"
                )
            else:
                expected_emoji = status_to_emoji.get(status_value)
                if expected_emoji is not None and expected_emoji != header["emoji"]:
                    status_mismatch = f"Status '{status_value}' does not match header emoji '{header['emoji']}'"
        
        # Validate phase statuses
        phase_issues: List[str] = []
        phases_block = field_block(block_lines, "Phases")
        if phases_block is not None:
            phases_text = "\n".join([block_lines[phases_block["index"]]] + list(phases_block["tail"]))
            # Check each phase line has valid status emoji
            phase_lines = [l for l in phases_text.splitlines() if re.search(r"`ph-\d+`", l)]
            implemented_count = 0
            total_phases = len(phase_lines)
            for pl in phase_lines:
                has_status_emoji = any(emoji in pl for emoji in ("⏳", "🔄", "✅"))
                if not has_status_emoji:
                    phase_issues.append(f"Phase line missing status emoji (⏳/🔄/✅): {pl.strip()[:60]}")
                if "✅" in pl:
                    implemented_count += 1
            # If feature is IMPLEMENTED, all phases must be IMPLEMENTED
            if status_value == "IMPLEMENTED" and total_phases > 0 and implemented_count < total_phases:
                phase_issues.append(f"Feature status is IMPLEMENTED but only {implemented_count}/{total_phases} phases are ✅ IMPLEMENTED")

        slug_mismatch: Optional[str] = None
        m_id = re.search(r"-feature-(.+)$", str(header["id"]))
        if m_id:
            expected_path = f"feature-{m_id.group(1)}/"
            if str(header["path"]) != expected_path:
                slug_mismatch = f"Feature link path '{header['path']}' does not match id slug '{expected_path}'"

        dir_issue: Optional[str] = None
        design_file_issue: Optional[str] = None
        if not skip_fs_checks and artifact_path is not None:
            features_dir = artifact_path.parent
            feature_dir = (features_dir / str(header["path"]))
            if not feature_dir.exists() or not feature_dir.is_dir():
                dir_issue = f"Feature directory does not exist: {feature_dir}"
            else:
                dp = feature_dir / "DESIGN.md"
                if status_value in {"IN_DESIGN", "DESIGN_READY", "IN_DEVELOPMENT", "IMPLEMENTED"} and not dp.exists():
                    design_file_issue = "Feature status is IN_PROGRESS/IMPLEMENTED but feature DESIGN.md is missing"
                elif dp.exists() and dp.is_file():
                    try:
                        dt = dp.read_text(encoding="utf-8")
                    except Exception:
                        dt = ""

                    header_text = "\n".join(dt.splitlines()[:120])
                    m_feature_id = re.search(r"^\*\*Feature ID\*\*:\s*`([^`]+)`\s*$", header_text, re.MULTILINE)
                    m_status = re.search(r"^\*\*Status\*\*:\s*(.+?)\s*$", header_text, re.MULTILINE)

                    if not m_feature_id:
                        design_file_issue = "Feature DESIGN.md missing **Feature ID** field"
                    elif str(m_feature_id.group(1)).strip() != str(header["id"]).strip():
                        design_file_issue = "Feature DESIGN.md **Feature ID** does not match FEATURES.md"
                    elif status_value in valid_statuses:
                        if not m_status:
                            design_file_issue = "Feature DESIGN.md missing **Status** field"
                        else:
                            design_status = m_status.group(1).strip()
                            # Normalize: extract status keyword from value (may have emoji prefix)
                            design_status_normalized = None
                            for vs in valid_statuses:
                                if vs in design_status:
                                    design_status_normalized = vs
                                    break
                            if design_status_normalized is None and "IN_PROGRESS" in design_status:
                                design_status_normalized = "IN_DEVELOPMENT"
                            if design_status_normalized != status_value:
                                design_file_issue = f"Feature DESIGN.md **Status** '{design_status}' does not match FEATURES.md '{status_value}'"

        dep_issues: List[str] = []
        depends_on_links: List[str] = []
        for dep_field in ("Depends On", "Blocks"):
            fb = field_block(block_lines, dep_field)
            if fb is None:
                continue
            inline_value = str(fb["value"]).strip()
            if inline_value == "None":
                continue
            dep_text = "\n".join([inline_value] + list(fb["tail"]))
            for link in _extract_feature_links(dep_text):
                if link not in path_set:
                    dep_issues.append(f"{dep_field} references missing feature entry: {link}")
                if link == str(header["path"]):
                    dep_issues.append(f"{dep_field} self-reference is not allowed: {link}")
                if dep_field == "Depends On" and link in path_set:
                    depends_on_links.append(link)

        dep_graph[str(header["path"])] = depends_on_links

        cross_issues: List[str] = []
        if design_ids["req"]:
            req_field = field_block(block_lines, "Requirements Covered")
            if req_field is not None:
                for rid in _extract_id_list(req_field):
                    covered_ids["req"].add(rid)
                    if rid not in design_ids["req"]:
                        cross_issues.append(f"Requirements Covered references missing id in DESIGN.md: {rid}")
        if design_ids["principle"]:
            p_field = field_block(block_lines, "Principles Covered")
            if p_field is not None:
                for pid in _extract_id_list(p_field):
                    covered_ids["principle"].add(pid)
                    if pid not in design_ids["principle"]:
                        cross_issues.append(f"Principles Covered references missing id in DESIGN.md: {pid}")
        if design_ids["constraint"]:
            c_field = field_block(block_lines, "Constraints Affected")
            if c_field is not None:
                for cid in _extract_id_list(c_field):
                    covered_ids["constraint"].add(cid)
                    if cid not in design_ids["constraint"]:
                        cross_issues.append(f"Constraints Affected references missing id in DESIGN.md: {cid}")

        if missing_fields or (not phases_ok) or empty_list_fields or invalid_status or status_mismatch or phase_issues or slug_mismatch or dir_issue or design_file_issue or dep_issues or cross_issues:
            issue = {
                "feature": header,
                "missing_fields": missing_fields,
            }
            all_phase_issues: List[str] = []
            if not phases_ok:
                all_phase_issues.append("Missing `ph-1` in phases")
            if phase_issues:
                all_phase_issues.extend(phase_issues)
            if all_phase_issues:
                issue["phase_issues"] = all_phase_issues
            if empty_list_fields:
                issue["empty_list_fields"] = empty_list_fields
            status_issues_list: List[str] = []
            if invalid_status:
                status_issues_list.append(invalid_status)
            if status_mismatch:
                status_issues_list.append(status_mismatch)
            if status_issues_list:
                issue["status_issues"] = status_issues_list
            if slug_mismatch:
                issue["slug_issues"] = [slug_mismatch]
            if dir_issue:
                issue["dir_issues"] = [dir_issue]
            if design_file_issue:
                issue["design_file_issues"] = [design_file_issue]
            if dep_issues:
                issue["dependency_issues"] = dep_issues
            if cross_issues:
                issue["cross_issues"] = cross_issues
            feature_issues.append(issue)

    placeholders = find_placeholders(artifact_text)

    if design_ids["req"]:
        missing_req_coverage = sorted([rid for rid in design_ids["req"] if rid not in covered_ids["req"]])
        if missing_req_coverage:
            errors.append(
                {
                    "type": "cross",
                    "message": "Not all DESIGN.md requirement IDs are covered by FEATURES.md",
                    "missing": missing_req_coverage,
                    "design_count": len(design_ids["req"]),
                    "covered_count": len(covered_ids["req"]),
                }
            )

    def _has_cycle(graph: Dict[str, List[str]]) -> bool:
        visiting: Set[str] = set()
        visited: Set[str] = set()

        def dfs(v: str) -> bool:
            if v in visited:
                return False
            if v in visiting:
                return True
            visiting.add(v)
            for nxt in graph.get(v, []):
                if dfs(nxt):
                    return True
            visiting.remove(v)
            visited.add(v)
            return False

        for v in graph.keys():
            if dfs(v):
                return True
        return False

    if dep_graph and _has_cycle(dep_graph):
        errors.append({"type": "content", "message": "Dependency graph contains a cycle"})


    passed = (len(errors) == 0) and (len(feature_issues) == 0) and (len(placeholders) == 0)

    return {
        "required_section_count": len(required_fields) + 3,
        "missing_sections": [],
        "placeholder_hits": placeholders,
        "status": "PASS" if passed else "FAIL",
        "errors": errors,
        "feature_issues": feature_issues,
        "coverage": {
            "design_requirement_ids_count": len(design_ids["req"]),
            "covered_requirement_ids_count": len(covered_ids["req"]),
        },
    }
