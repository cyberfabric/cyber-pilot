"""
FDD Validator - Common Validation Functions

Common validation logic shared across artifact types.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ...constants import LINK_RE

from ...utils import parse_required_sections, find_present_section_ids, find_placeholders


def validate_generic_sections(artifact_text: str, requirements_path: Path) -> Dict[str, object]:
    """Validate artifact against generic section requirements."""
    required_sections = parse_required_sections(requirements_path)
    if not required_sections:
        placeholders = find_placeholders(artifact_text)
        return {
            "required_section_count": 0,
            "missing_sections": [],
            "placeholder_hits": placeholders,
            "status": "FAIL",
            "errors": [
                {
                    "type": "requirements",
                    "message": "Could not parse required sections from requirements file (expected headings like '### Section X: ...')",
                    "requirements": str(requirements_path),
                }
            ],
        }

    present_ids_list = find_present_section_ids(artifact_text)
    present_ids = set(present_ids_list)
    
    # Format missing sections as list of dicts with id and title
    missing = [
        {
            "id": section_id,
            "title": required_sections[section_id],
        }
        for section_id in required_sections.keys()
        if section_id not in present_ids
    ]

    errors: List[Dict[str, object]] = []

    # Check for duplicate section IDs
    counts: Dict[str, int] = {}
    for sid in present_ids_list:
        counts[sid] = counts.get(sid, 0) + 1
    dup_sids = sorted([sid for sid, c in counts.items() if c > 1])
    if dup_sids:
        errors.append({"type": "structure", "message": "Duplicate section ids in artifact", "ids": dup_sids})

    # Check section order
    required_order = list(required_sections.keys())
    present_required_in_order = [sid for sid in present_ids_list if sid in required_sections]
    if present_required_in_order != required_order:
        errors.append(
            {
                "type": "structure",
                "message": "Sections are not in required order",
                "required_order": required_order,
                "found_order": present_required_in_order,
            }
        )
    
    placeholders = find_placeholders(artifact_text)
    passed = (len(missing) == 0) and (len(placeholders) == 0) and (len(errors) == 0)

    return {
        "required_section_count": len(required_sections),
        "missing_sections": missing,
        "placeholder_hits": placeholders,
        "status": "PASS" if passed else "FAIL",
        "errors": errors,
    }


def common_checks(
    *,
    artifact_text: str,
    artifact_path: Path,
    requirements_path: Path,
    artifact_kind: str,
    skip_fs_checks: bool = False,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    """
    Common validation checks applied to all artifacts.
    
    Returns:
        - List of error dicts
        - List of placeholder dicts
    """
    from ...constants import LINK_RE, HTML_COMMENT_RE, ID_LINE_RE, SIZE_HARD_LIMIT_RE, ADR_ID_LINE_RE
    
    errors: List[Dict[str, object]] = []
    placeholder_hits: List[Dict[str, object]] = []

    # Find HTML comment placeholders
    for match in HTML_COMMENT_RE.finditer(artifact_text):
        comment_text = match.group(0)
        for word in ["TODO", "TBD", "TBF", "TBC", "TBA", "FIXME", "XXX"]:
            if word in comment_text.upper():
                placeholder_hits.append({"type": "html_comment", "token": word, "text": comment_text[:50]})
                break

    # Check for disallowed link notation
    disallowed_pattern = re.compile(r"(@/|@DESIGN\.md|@PRD\.md|@ADR\.md)")
    for match in disallowed_pattern.finditer(artifact_text):
        errors.append({"type": "link_format", "message": "Disallowed IDE-specific link notation", "token": match.group(0)})

    # Check file links if not skipping
    if not skip_fs_checks:
        for idx, line in enumerate(artifact_text.splitlines(), start=1):
            for _, target in LINK_RE.findall(line):
                t = target.strip()
                if not t or t.startswith("#"):
                    continue
                if t.startswith("http://") or t.startswith("https://"):
                    continue
                if t.startswith("/"):
                    errors.append({"type": "link_format", "message": "Absolute link targets are not allowed", "line": idx, "text": line.strip()})
                    continue
                t = t.split("#", 1)[0]
                if not t:
                    continue
                resolved = (artifact_path.parent / t).resolve()
                if not resolved.exists():
                    errors.append({"type": "link_target", "message": "Broken file link target", "line": idx, "target": t, "text": line.strip()})

    # Check FDD ID formatting and duplicates
    ids_seen: List[str] = []
    lines = artifact_text.splitlines()

    in_fence_mask: List[bool] = [False] * len(lines)
    _fence: Optional[str] = None
    for _idx, _line in enumerate(lines):
        _s = _line.lstrip()
        _m = re.match(r"```+", _s)
        if _m:
            _ticks = _m.group(0)
            in_fence_mask[_idx] = True
            if _fence is None:
                _fence = _ticks
            else:
                if _s.startswith(_fence):
                    _fence = None
            continue
        if _fence is not None:
            in_fence_mask[_idx] = True

    for i, line in enumerate(lines):
        if "**ADR ID**:" in line:
            m_adr = ADR_ID_LINE_RE.search(line)
            if not m_adr:
                errors.append({"type": "id", "message": "ADR ID values must be wrapped in backticks", "line": i + 1, "text": line.strip()})
                continue
            val = f"`{m_adr.group(1)}`"
        elif "**ID**:" in line:
            m = ID_LINE_RE.search(line)
            if not m:
                continue
            val = m.group(1).strip()
        else:
            continue

        if "fdd-" in val and "`" not in val:
            errors.append({"type": "id", "message": "ID values must be wrapped in backticks", "line": i + 1, "text": line.strip()})

        for tok in re.findall(r"`([^`]+)`", val):
            if tok.startswith("fdd-"):
                ids_seen.append(tok)

    # Enforce that FDD IDs used as values in artifact docs are wrapped in backticks.
    # This is intentionally narrower than "any occurrence" to avoid breaking
    # canonical markdown link labels (e.g. FEATURES.md headings with [fdd-...](...)).
    if artifact_kind in {"prd", "overall-design", "adr", "features-manifest", "feature-design"}:
        fdd_id_re = re.compile(r"\bfdd-[a-z0-9-]+\b")
        md_link_re = re.compile(r"\[[^\]]+\]\([^)]+\)")
        inline_code_re = re.compile(r"`[^`]*`")

        in_code_fence = False
        for idx, line in enumerate(lines, start=1):
            s = line.strip()
            if s.startswith("```"):
                in_code_fence = not in_code_fence
                continue
            if in_code_fence:
                continue

            if s == "<!-- fdd-id-content -->":
                continue

            if "**ID**:" in line or "**ADR ID**:" in line:
                continue

            # Only validate value-like lines to avoid false positives in prose.
            if not re.match(r"^\s*[-*]\s+", line) and "**" not in line:
                continue

            cleaned = inline_code_re.sub("", line)
            cleaned = md_link_re.sub("", cleaned)

            for tok in fdd_id_re.findall(cleaned):
                errors.append(
                    {
                        "type": "id",
                        "message": "FDD IDs must be wrapped in backticks",
                        "line": idx,
                        "id": tok,
                        "text": line.strip(),
                    }
                )

    # Enforce strict ID payload blocks for FDD artifacts.
    # After any **ID**: `fdd-*` line, require a payload block delimited by
    # <!-- fdd-id-content --> ... <!-- fdd-id-content --> (payload may be empty)
    # and require that no non-empty lines exist outside the payload within the enclosing element.
    # Enclosing element is computed as the range between headings of the same level
    # (stop at next heading with level <= the element's heading level).
    if artifact_kind in {"prd", "overall-design", "features-manifest", "feature-design"}:
        id_line_start_re = re.compile(r"^\s*(?:[-*]\s*)?(?:\[[ xX]\]\s*)?\*\*ID\*\*:\s*(.+)$", re.IGNORECASE)
        heading_re = re.compile(r"^(#{1,6})\s+")

        def _heading_level_at(idx: int) -> Optional[int]:
            if 0 <= idx < len(lines) and in_fence_mask[idx]:
                return None
            mh = heading_re.match(lines[idx].strip())
            if not mh:
                return None
            return len(mh.group(1))

        def _enclosing_heading_bounds(id_idx: int) -> Tuple[int, int, Optional[int]]:
            start = id_idx
            while start >= 0 and _heading_level_at(start) is None:
                start -= 1
            if start < 0:
                return 0, len(lines), None
            lvl = _heading_level_at(start)
            if lvl is None:
                return 0, len(lines), None
            end = start + 1
            while end < len(lines):
                nlvl = _heading_level_at(end)
                if nlvl is not None and nlvl <= lvl:
                    break
                end += 1
            return start, end, lvl

        def _next_id_idx(id_idx: int, *, stop_at: int) -> int:
            j = id_idx + 1
            while j < stop_at:
                if not in_fence_mask[j] and id_line_start_re.match(lines[j]):
                    return j
                j += 1
            return stop_at

        for i, line in enumerate(lines):
            if in_fence_mask[i]:
                continue
            m = id_line_start_re.match(line)
            if not m:
                continue
            val = m.group(1)
            fdd_ids = [tok.strip() for tok in re.findall(r"`([^`]+)`", val) if tok.strip().startswith("fdd-")]
            for tok in re.findall(r"\bfdd-[a-z0-9-]+\b", val):
                if tok not in fdd_ids:
                    fdd_ids.append(tok)
            if not fdd_ids:
                continue

            _, heading_end, _heading_lvl = _enclosing_heading_bounds(i)
            next_id = _next_id_idx(i, stop_at=heading_end)
            elem_end = min(next_id, heading_end)

            # Find payload open delimiter after optional blank lines (must be inside the element).
            j = i + 1
            while j < elem_end and lines[j].strip() == "":
                j += 1
            open_marker = None
            if j < elem_end:
                s = lines[j].strip()
                if s == "<!-- fdd-id-content -->":
                    open_marker = s
                elif s == "---":
                    # Temporary migration support.
                    open_marker = s
                    errors.append(
                        {
                            "type": "id_payload_legacy",
                            "message": "Legacy payload delimiter '---' is deprecated; use '<!-- fdd-id-content -->'",
                            "line": j + 1,
                            "id": fdd_ids[0],
                        }
                    )

            if open_marker is None:
                errors.append(
                    {
                        "type": "id_payload",
                        "message": "Missing payload block after **ID** line (expected '<!-- fdd-id-content --> ... <!-- fdd-id-content -->')",
                        "line": i + 1,
                        "id": fdd_ids[0],
                    }
                )
                continue

            # Find payload close delimiter (must be inside the element).
            k = j + 1
            while k < elem_end:
                if in_fence_mask[k]:
                    k += 1
                    continue
                if lines[k].strip() == open_marker:
                    break
                k += 1
            if k >= elem_end:
                errors.append(
                    {
                        "type": "id_payload",
                        "message": "Payload block must close before element boundary",
                        "line": i + 1,
                        "id": fdd_ids[0],
                    }
                )
                continue

            # After payload close, only blank lines are allowed until the end of this element.
            t = k + 1
            while t < elem_end:
                if in_fence_mask[t]:
                    t += 1
                    continue
                s = lines[t].strip()
                if s == "":
                    t += 1
                    continue

                # Allow markdown horizontal rules as separators (outside payload).
                if s == "---":
                    break

                errors.append(
                    {
                        "type": "id_payload",
                        "message": "Content after payload block must be inside the payload block",
                        "line": t + 1,
                        "id": fdd_ids[0],
                    }
                )
                break

    dup_ids = sorted({x for x in ids_seen if ids_seen.count(x) > 1})
    if dup_ids:
        errors.append({"type": "id", "message": "Duplicate fdd- IDs in document", "ids": dup_ids})

    # Check ID line spacing
    id_line_start_re = re.compile(r"^\s*(?:[-*]\s*)?(?:\[[ xX]\]\s*)?\*\*ID\*\*:\s*", re.IGNORECASE)
    for i, line in enumerate(lines[:-1]):
        if not re.match(r"^#{2,6}\s+", line.strip()):
            continue

        j = i + 1
        while j < len(lines) and lines[j].strip() == "":
            j += 1

        if j < len(lines) and id_line_start_re.match(lines[j]):
            if j != i + 2:
                errors.append({
                    "type": "id",
                    "message": "Exactly one blank line is required between heading and **ID** line",
                    "line": i + 1,
                    "text": line.strip(),
                })

    # Check section heading format
    for idx, line in enumerate(lines, start=1):
        if re.match(r"^##\s+Section\s+[A-Z]:", line.strip()):
            errors.append({"type": "section_heading", "message": "Disallowed section heading format (use '## A. Title')", "line": idx, "text": line.strip()})

    return errors, placeholder_hits


def _normalize_feature_relpath(path: str) -> str:
    p = path.strip()
    if not p.endswith("/"):
        p = p + "/"
    return p


def _extract_feature_links(text: str) -> List[str]:
    links: List[str] = []
    for _, target in LINK_RE.findall(text):
        t = target.strip()
        if not t.startswith("feature-"):
            continue
        links.append(_normalize_feature_relpath(t))
    return links


def _extract_id_list(field_block: Dict[str, object]) -> List[str]:
    raw: List[str] = []
    inline = str(field_block["value"]).strip()
    if inline:
        raw.extend([p.strip() for p in inline.split(",") if p.strip()])
    for line in list(field_block["tail"]):
        m = re.match(r"^\s*[-*]\s+(.+?)\s*$", line)
        if not m:
            continue
        raw.append(m.group(1).strip())

    ids: List[str] = []
    for item in raw:
        cleaned = item.strip().strip("`")
        if cleaned:
            ids.append(cleaned)
    return ids


__all__ = ["validate_generic_sections", "common_checks"]
