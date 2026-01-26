"""
FDD Validator - PRD.md Validation

Validates PRD documents: actors, capabilities, use cases.
"""

import re
from typing import Dict, List, Set

from ...constants import (
    ACTOR_ID_RE,
    NFR_ID_RE,
    PRD_CONTEXT_ID_RE,
    PRD_FR_ID_RE,
    USECASE_ID_RE,
)

from ...utils import (
    find_placeholders,
    split_by_prd_section_letter,
    field_block,
    has_list_item,
    extract_backticked_ids,
)


__all__ = ["validate_prd"]


def _paragraph_count(lines: List[str]) -> int:
    """Count paragraphs in text lines."""
    paras = 0
    buf: List[str] = []
    for l in lines:
        s = l.strip()
        if not s:
            if any(x.strip() for x in buf):
                paras += 1
            buf = []
            continue
        if s.startswith("#"):
            continue
        buf.append(s)
    if any(x.strip() for x in buf):
        paras += 1
    return paras


def validate_prd(artifact_text: str) -> Dict[str, object]:
    errors: List[Dict[str, object]] = []
    section_order, sections = split_by_prd_section_letter(artifact_text)

    required = ["A", "B", "C", "D", "E"]
    missing_required = [s for s in required if s not in sections]
    if missing_required:
        errors.append({"type": "structure", "message": "Missing required top-level sections", "missing": missing_required})

    allowed = set(["A", "B", "C", "D", "E", "F"])
    unknown = [s for s in sections.keys() if s not in allowed]
    if unknown:
        errors.append({"type": "structure", "message": "Unknown top-level sections", "sections": sorted(unknown)})

    expected = ["A", "B", "C", "D", "E"]
    if "F" in sections:
        expected.append("F")
    if section_order and section_order[: len(expected)] != expected:
        errors.append({"type": "structure", "message": "Section order invalid", "required_order": expected, "found_order": section_order})

    placeholders = find_placeholders(artifact_text)

    actor_ids: List[str] = []
    fr_ids: List[str] = []
    usecase_ids: List[str] = []
    nfr_ids: List[str] = []
    ctx_ids: List[str] = []
    issues: List[Dict[str, object]] = []

    if "A" in sections:
        a_lines = sections["A"]
        purpose_block = field_block(a_lines, "Purpose")
        if purpose_block is None or not str(purpose_block["value"]).strip():
            issues.append({"section": "A", "missing_field": "Purpose"})

        for f in ("Target Users", "Key Problems Solved", "Success Criteria"):
            fb = field_block(a_lines, f)
            if fb is None:
                issues.append({"section": "A", "missing_field": f})
                continue
            if str(fb["value"]).strip():
                continue
            if not has_list_item(list(fb["tail"])):
                issues.append({"section": "A", "message": f"Field '{f}' must contain at least one list item"})

        cap_block = field_block(a_lines, "Capabilities")
        if cap_block is None:
            issues.append({"section": "A", "missing_field": "Capabilities"})
        else:
            if str(cap_block["value"]).strip():
                pass
            elif not has_list_item(list(cap_block["tail"])):
                issues.append({"section": "A", "message": "Field 'Capabilities' must contain at least one list item"})
        if _paragraph_count(a_lines) < 2:
            issues.append({"section": "A", "message": "Section A must contain at least 2 paragraphs"})

    if "B" in sections:
        b_lines = sections["B"]
        has_human = any("Human Actors" in l for l in b_lines)
        has_system = any("System Actors" in l for l in b_lines)
        if not has_human or not has_system:
            issues.append({"section": "B", "message": "Section B must be grouped by Human Actors and System Actors"})

        idxs = [i for i, l in enumerate(b_lines) if l.strip().startswith("#### ")]
        if not idxs:
            issues.append({"section": "B", "message": "No actors found (expected '#### Actor Name')"})
        for i, start in enumerate(idxs):
            end = idxs[i + 1] if i + 1 < len(idxs) else len(b_lines)
            block = b_lines[start:end]
            title_line = block[0].strip()
            meta = [l for l in block[1:] if l.strip()]
            if not meta:
                issues.append({"section": "B", "message": "Actor block missing metadata", "actor": title_line})
                continue
            id_line = meta[0]
            if "**ID**:" not in id_line:
                issues.append({"section": "B", "message": "Actor ID must be first non-empty line after heading", "actor": title_line})
            ids = extract_backticked_ids(id_line, ACTOR_ID_RE)
            if not ids:
                issues.append({"section": "B", "message": "Invalid actor ID format", "actor": title_line, "line": id_line})
            else:
                actor_ids.extend(ids)

            role_ok = any("**Role**:" in l for l in meta[1:6])
            if not role_ok:
                issues.append({"section": "B", "message": "Missing **Role** line", "actor": title_line})
            if any("**Capabilities**" in l for l in block):
                issues.append({"section": "B", "message": "Actor block must not list capabilities", "actor": title_line})

        dup = sorted({x for x in actor_ids if actor_ids.count(x) > 1})
        if dup:
            issues.append({"section": "B", "message": "Duplicate actor IDs", "ids": dup})

    if "C" in sections:
        c_lines = sections["C"]
        idxs = [i for i, l in enumerate(c_lines) if l.strip().startswith("#### ")]
        if not idxs:
            issues.append({"section": "C", "message": "No functional requirements found (expected '#### Requirement Name')"})
        for i, start in enumerate(idxs):
            end = idxs[i + 1] if i + 1 < len(idxs) else len(c_lines)
            block = c_lines[start:end]
            title_line = block[0].strip()
            meta = [l for l in block[1:] if l.strip()]
            if not meta:
                issues.append({"section": "C", "message": "Functional requirement block missing metadata", "requirement": title_line})
                continue
            id_line = meta[0]
            if "**ID**:" not in id_line:
                issues.append({"section": "C", "message": "Functional requirement ID must be first non-empty line after heading", "requirement": title_line})

            ids = extract_backticked_ids(id_line, PRD_FR_ID_RE)
            if not ids:
                issues.append({"section": "C", "message": "Invalid functional requirement ID format", "requirement": title_line, "line": id_line})
            else:
                fr_ids.extend(ids)

            actors_line = next((l for l in block if "**Actors**:" in l), None)
            if actors_line is None:
                issues.append({"section": "C", "message": "Functional requirement missing **Actors** line", "requirement": title_line})
            else:
                a_ids = extract_backticked_ids(actors_line, ACTOR_ID_RE)
                if not a_ids:
                    issues.append({"section": "C", "message": "Functional requirement **Actors** must list actor IDs", "requirement": title_line})
                else:
                    missing = [x for x in a_ids if x not in set(actor_ids)]
                    if missing:
                        issues.append({"section": "C", "message": "Functional requirement references unknown actor IDs", "requirement": title_line, "missing": missing})

            has_any_content = False
            for l in block:
                s = l.strip()
                if not s:
                    continue
                if s.startswith("#### "):
                    continue
                if "**ID**:" in s:
                    continue
                if "**Actors**:" in s:
                    continue
                if s.startswith("<!--"):
                    continue
                has_any_content = True
                break
            if not has_any_content:
                issues.append({"section": "C", "message": "Functional requirement must include a description", "requirement": title_line})

        dup_frs = sorted({x for x in fr_ids if fr_ids.count(x) > 1})
        if dup_frs:
            issues.append({"section": "C", "message": "Duplicate functional requirement IDs", "ids": dup_frs})

    if "D" in sections:
        d_lines = sections["D"]
        idxs = [i for i, l in enumerate(d_lines) if l.strip().startswith("#### ")]
        if not idxs:
            issues.append({"section": "D", "message": "No use cases found (expected '#### UC-XXX: Use Case Name')"})
        for i, start in enumerate(idxs):
            end = idxs[i + 1] if i + 1 < len(idxs) else len(d_lines)
            block = d_lines[start:end]
            title_line = block[0].strip()
            meta = [l for l in block[1:] if l.strip()]
            if not meta:
                issues.append({"section": "D", "message": "Use case block missing metadata", "usecase": title_line})
                continue
            id_line = next((l for l in meta[:6] if "**ID**:" in l), None)
            if id_line is None:
                issues.append({"section": "D", "message": "Missing **ID** line", "usecase": title_line})
                continue
            ids = extract_backticked_ids(id_line, USECASE_ID_RE)
            if not ids:
                issues.append({"section": "D", "message": "Invalid use case ID format", "usecase": title_line, "line": id_line})
            else:
                usecase_ids.extend(ids)

            actor_line = next((l for l in block if "**Actor**:" in l), None)
            if actor_line is None:
                issues.append({"section": "D", "message": "Missing **Actor** line", "usecase": title_line})
            else:
                a_ids = extract_backticked_ids(actor_line, ACTOR_ID_RE)
                if not a_ids:
                    issues.append({"section": "D", "message": "Use case **Actor** must list actor IDs", "usecase": title_line})
                else:
                    missing = [x for x in a_ids if x not in set(actor_ids)]
                    if missing:
                        issues.append({"section": "D", "message": "Use case references unknown actor IDs", "usecase": title_line, "missing": missing})

            if not any("**Preconditions**" in l for l in block):
                issues.append({"section": "D", "message": "Missing **Preconditions**", "usecase": title_line})
            if not any(l.strip().startswith("1.") for l in block):
                issues.append({"section": "D", "message": "Missing numbered flow steps", "usecase": title_line})
            if not any("**Postconditions**" in l for l in block):
                issues.append({"section": "D", "message": "Missing **Postconditions**", "usecase": title_line})

        dup = sorted({x for x in usecase_ids if usecase_ids.count(x) > 1})
        if dup:
            issues.append({"section": "D", "message": "Duplicate use case IDs", "ids": dup})

        fr_set = set(fr_ids)
        uc_set = set(usecase_ids)
        for l in d_lines:
            for fid in PRD_FR_ID_RE.findall(l):
                if fid not in fr_set:
                    issues.append({"section": "D", "message": "Use case references unknown functional requirement ID", "id": fid})
            for uid in USECASE_ID_RE.findall(l):
                if uid not in uc_set:
                    issues.append({"section": "D", "message": "Use case references unknown use case ID", "id": uid})

    if "E" in sections:
        e_lines = sections["E"]
        idxs = [i for i, l in enumerate(e_lines) if l.strip().startswith("#### ")]
        if not idxs:
            issues.append({"section": "E", "message": "No non-functional requirements found (expected '#### NFR Name')"})
        for i, start in enumerate(idxs):
            end = idxs[i + 1] if i + 1 < len(idxs) else len(e_lines)
            block = e_lines[start:end]
            title_line = block[0].strip()
            meta = [l for l in block[1:] if l.strip()]
            if not meta:
                issues.append({"section": "E", "message": "NFR block missing metadata", "nfr": title_line})
                continue
            id_line = meta[0]
            if "**ID**:" not in id_line:
                issues.append({"section": "E", "message": "NFR ID must be first non-empty line after heading", "nfr": title_line})
            ids = extract_backticked_ids(id_line, NFR_ID_RE)
            if not ids:
                issues.append({"section": "E", "message": "Invalid NFR ID format", "nfr": title_line, "line": id_line})
            else:
                nfr_ids.extend(ids)

            has_any_content = False
            for l in block:
                s = l.strip()
                if not s:
                    continue
                if s.startswith("#### "):
                    continue
                if "**ID**:" in s:
                    continue
                if s.startswith("<!--"):
                    continue
                has_any_content = True
                break
            if not has_any_content:
                issues.append({"section": "E", "message": "NFR must include a description", "nfr": title_line})

        dup = sorted({x for x in nfr_ids if nfr_ids.count(x) > 1})
        if dup:
            issues.append({"section": "E", "message": "Duplicate NFR IDs", "ids": dup})

    if "F" in sections:
        f_lines = sections["F"]
        # Optional section: if IDs are used, ensure they match PRD_CONTEXT_ID_RE.
        for l in f_lines:
            if "**ID**:" not in l:
                continue
            ids = extract_backticked_ids(l, PRD_CONTEXT_ID_RE)
            if ids:
                ctx_ids.extend(ids)
            elif "`fdd-" in l:
                issues.append({"section": "F", "message": "Invalid PRD context ID format", "line": l.strip()})

        dup = sorted({x for x in ctx_ids if ctx_ids.count(x) > 1})
        if dup:
            issues.append({"section": "F", "message": "Duplicate PRD context IDs", "ids": dup})

    passed = (len(errors) == 0) and (len(issues) == 0) and (len(placeholders) == 0)
    return {
        "required_section_count": len(required),
        "missing_sections": [{"id": s, "title": ""} for s in missing_required],
        "placeholder_hits": placeholders,
        "status": "PASS" if passed else "FAIL",
        "errors": errors,
        "issues": issues,
    }
FEATURE_HEADING_RE = re.compile(
    r"^###\s+(\d+)\.\s+\[(.+?)\]\((feature-[^)]+/)\)\s+([⏳🔄✅])\s+(CRITICAL|HIGH|MEDIUM|LOW)\s*$"
)
