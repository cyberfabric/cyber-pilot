"""
FDD Validator - Feature DESIGN.md Validation

Validates feature design documents: structure, FDL syntax, requirements, cross-references.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ...constants import (
    FDL_STEP_LINE_RE,
    FEATURE_FLOW_ID_RE,
    FEATURE_ALGO_ID_RE,
    FEATURE_STATE_ID_RE,
    FEATURE_REQ_ID_RE,
    FEATURE_CONTEXT_ID_RE,
    LINK_RE,
)

from ...utils import (
    find_placeholders,
    split_by_feature_section_letter,
    field_block,
    has_list_item,
    slugify_anchor,
    load_text,
)


__all__ = ["validate_feature_design"]
def validate_feature_design(
    artifact_text: str,
    *,
    artifact_path: Optional[Path] = None,
    skip_fs_checks: bool = False,
) -> Dict[str, object]:
    """
    Validate feature DESIGN.md structure and content.
    
    Checks:
    - Section structure (A-E required, F optional)
    - FDL syntax in flows, algorithms, state machines
    - ID formatting and feature slug consistency
    - Cross-references to PRD.md and FEATURES.md
    - Requirements fields (including Implementation details)
    - Optional Additional Context items
    """
    errors: List[Dict[str, object]] = []
    placeholders = find_placeholders(artifact_text)
    section_order, sections = split_by_feature_section_letter(artifact_text)
    
    expected = ["A", "B", "C", "D", "E"]
    if "F" in sections:
        expected.append("F")
    if section_order and section_order[: len(expected)] != expected:
        errors.append({"type": "structure", "message": "Section order invalid", "required_order": expected, "found_order": section_order})

    feature_slug: Optional[str] = None
    if artifact_path is not None:
        parent = artifact_path.parent.name
        if parent.startswith("feature-"):
            feature_slug = parent[len("feature-") :]

    def _extract_full_ids(line: str, kind: str) -> List[str]:
        ids: List[str] = []
        pat = {
            "flow": re.compile(r"\bfdd-[a-z0-9-]+-feature-[a-z0-9-]+-flow-[a-z0-9-]+\b"),
            "algo": re.compile(r"\bfdd-[a-z0-9-]+-feature-[a-z0-9-]+-algo-[a-z0-9-]+\b"),
            "state": re.compile(r"\bfdd-[a-z0-9-]+-feature-[a-z0-9-]+-state-[a-z0-9-]+\b"),
            "req": re.compile(r"\bfdd-[a-z0-9-]+-feature-[a-z0-9-]+-req-[a-z0-9-]+\b"),
            "context": re.compile(r"\bfdd-[a-z0-9-]+-feature-[a-z0-9-]+-context-[a-z0-9-]+\b"),
        }[kind]

        for tok in re.findall(r"`([^`]+)`", line):
            if pat.fullmatch(tok.strip()):
                ids.append(tok.strip())

        for m in pat.finditer(line):
            ids.append(m.group(0))

        dedup: List[str] = []
        for x in ids:
            if x not in dedup:
                dedup.append(x)
        return dedup

    def _check_section_fdl(section_letter: str, kind: str) -> Tuple[set, set]:
        lines = sections.get(section_letter, [])
        ids: set = set()
        phases: set = set()

        current_scope_id: Optional[str] = None
        scope_inst_seen: set = set()

        in_code = False
        for idx, line in enumerate(lines, start=1):
            if line.strip().startswith("```"):
                in_code = not in_code
                errors.append({"type": "fdl", "message": f"Code blocks are not allowed in Section {section_letter}", "line": idx, "text": line.strip()})
                continue
            if in_code:
                continue

            if "**WHEN**" in line and section_letter in ("B", "C"):
                errors.append({"type": "fdl", "message": "**WHEN** is only allowed in state machines (Section D)", "section": section_letter, "line": idx, "text": line.strip()})

            bad_bold = re.findall(r"\*\*([A-Z ]+)\*\*", line)
            prohibited = {"THEN", "SET", "VALIDATE", "CHECK", "LOAD", "READ", "WRITE", "CREATE", "ADD"}
            if section_letter in ("B", "C"):
                prohibited.add("WHEN")
                prohibited.add("AND")
            for tok in bad_bold:
                t = tok.strip()
                if t in prohibited:
                    errors.append({"type": "fdl", "message": "Prohibited bold keyword in FDL", "section": section_letter, "keyword": t, "line": idx, "text": line.strip()})

            if section_letter in ("C",) and re.search(r"\b(fn|function|def|class|interface)\b", line, re.IGNORECASE):
                errors.append({"type": "fdl", "message": "Programming syntax is not allowed in algorithms", "section": section_letter, "line": idx, "text": line.strip()})

            if "**ID**:" in line:
                if not re.match(r"^\s*[-*]\s+\[[ xX]\]\s+\*\*ID\*\*:\s+", line):
                    errors.append({"type": "id", "message": "ID line must be a checkbox list item", "section": section_letter, "line": idx, "text": line.strip()})

                for fid in _extract_full_ids(line, kind):
                    ids.add(fid)

                if kind == "algo":
                    scope_ids = _extract_full_ids(line, kind)
                    current_scope_id = scope_ids[0] if scope_ids else None
                    scope_inst_seen = set()

                if feature_slug is not None:
                    m_kind = {
                        "flow": FEATURE_FLOW_ID_RE,
                        "algo": FEATURE_ALGO_ID_RE,
                        "state": FEATURE_STATE_ID_RE,
                    }[kind]
                    for m in m_kind.finditer(line):
                        if m.group(1) != feature_slug:
                            errors.append({"type": "id", "message": "Feature slug in ID does not match directory slug", "section": section_letter, "expected": feature_slug, "found": m.group(1), "line": idx, "text": line.strip()})

            m_ph = re.findall(r"`ph-(\d+)`", line)
            for n in m_ph:
                phases.add(int(n))

            if re.match(r"^\s*\d+\.\s+", line):
                if not FDL_STEP_LINE_RE.match(line):
                    errors.append({"type": "fdl", "message": "Invalid FDL step line format", "section": section_letter, "line": idx, "text": line.strip()})
                elif kind == "algo" and current_scope_id is not None:
                    m_inst = re.search(r"`(inst-[a-z0-9-]+)`\s*$", line.strip())
                    if m_inst:
                        inst_id = m_inst.group(1)
                        if inst_id in scope_inst_seen:
                            errors.append(
                                {
                                    "type": "fdl",
                                    "message": "Duplicate FDL instruction IDs within algorithm",
                                    "section": section_letter,
                                    "line": idx,
                                    "algorithm_id": current_scope_id,
                                    "inst": inst_id,
                                }
                            )
                        scope_inst_seen.add(inst_id)
            if re.match(r"^\s*-\s+\[[ xX]\]\s+-\s+", line):
                if not FDL_STEP_LINE_RE.match(line):
                    errors.append({"type": "fdl", "message": "Invalid FDL step line format", "section": section_letter, "line": idx, "text": line.strip()})
                elif kind == "algo" and current_scope_id is not None:
                    m_inst = re.search(r"`(inst-[a-z0-9-]+)`\s*$", line.strip())
                    if m_inst:
                        inst_id = m_inst.group(1)
                        if inst_id in scope_inst_seen:
                            errors.append(
                                {
                                    "type": "fdl",
                                    "message": "Duplicate FDL instruction IDs within algorithm",
                                    "section": section_letter,
                                    "line": idx,
                                    "algorithm_id": current_scope_id,
                                    "inst": inst_id,
                                }
                            )
                        scope_inst_seen.add(inst_id)

        return ids, phases

    flow_ids: set = set()
    algo_ids: set = set()
    state_ids: set = set()
    phase_nums: set = set()

    if "B" in sections:
        flow_ids, ph = _check_section_fdl("B", "flow")
        phase_nums |= ph
    if "C" in sections:
        algo_ids, ph = _check_section_fdl("C", "algo")
        phase_nums |= ph
    if "D" in sections:
        state_ids, ph = _check_section_fdl("D", "state")
        phase_nums |= ph

    anchors: set = set()
    for line in artifact_text.splitlines():
        m = re.match(r"^###\s+(.+?)\s*$", line.strip())
        if not m:
            continue
        anchors.add(slugify_anchor(m.group(1)))

    if "A" in sections:
        a_text = "\n".join(sections["A"])
        for sub in ("### 1. Overview", "### 2. Purpose", "### 3. Actors", "### 4. References"):
            if sub not in a_text:
                errors.append({"type": "structure", "message": "Missing required subsection in Section A", "section": "A", "subsection": sub})

        # Validate Feature ID field is present and matches directory slug
        m_fid = re.search(r"\*\*Feature ID\*\*:\s*`([^`]+)`", a_text)
        if not m_fid:
            errors.append({"type": "content", "message": "Missing **Feature ID** field in Section A", "section": "A"})
        else:
            feature_id_value = m_fid.group(1).strip()
            # Check Feature ID matches directory slug pattern
            if feature_slug is not None:
                expected_suffix = f"-feature-{feature_slug}"
                if not feature_id_value.endswith(expected_suffix):
                    errors.append({"type": "id", "message": "Feature ID does not match directory slug", "section": "A", "expected_suffix": expected_suffix, "found": feature_id_value})

        # Validate feature-level Status field is present and has valid value
        m_status = re.search(r"\*\*Status\*\*:\s*(.+?)(?:\n|$)", a_text)
        if not m_status:
            errors.append({"type": "content", "message": "Missing **Status** field in Section A", "section": "A"})
        else:
            status_val = m_status.group(1).strip()
            valid_statuses = {"NOT_STARTED", "IN_DESIGN", "DESIGN_READY", "IN_DEVELOPMENT", "IMPLEMENTED"}

            normalized: Optional[str] = None
            if "IN_PROGRESS" in status_val:
                normalized = "IN_DEVELOPMENT"
            else:
                for vs in valid_statuses:
                    if vs in status_val:
                        normalized = vs
                        break

            if normalized is None:
                errors.append(
                    {
                        "type": "content",
                        "message": "Feature Status must be one of: NOT_STARTED, IN_DESIGN, DESIGN_READY, IN_DEVELOPMENT, IMPLEMENTED",
                        "section": "A",
                        "found": status_val,
                    }
                )

        actors_block = a_text.split("### 3. Actors", 1)[1] if "### 3. Actors" in a_text else ""
        if "### 4. References" in actors_block:
            actors_block = actors_block.split("### 4. References", 1)[0]
        actor_lines = [l.strip() for l in actors_block.splitlines() if re.match(r"^\s*[-*]\s+\S+", l)]
        actor_ids: List[str] = []
        for l in actor_lines:
            m = re.search(r"`(fdd-[a-z0-9-]+-actor-[a-z0-9-]+)`", l)
            if not m:
                errors.append({"type": "id", "message": "Section A Actors must be FDD actor IDs wrapped in backticks", "section": "A", "text": l.strip()})
                continue
            actor_ids.append(m.group(1))

        if not skip_fs_checks and artifact_path is not None:
            bp = artifact_path.parents[2] / "PRD.md"
            bt, berr = load_text(bp)
            if berr:
                errors.append({"type": "cross", "message": berr})
            else:
                if actor_ids:
                    prd_actor_ids = set(re.findall(r"`(fdd-[a-z0-9-]+-actor-[a-z0-9-]+)`", bt or ""))
                    unknown_ids = sorted([a for a in actor_ids if a not in prd_actor_ids])
                    if prd_actor_ids and unknown_ids:
                        errors.append({"type": "cross", "message": "Actor IDs must match PRD.md actor IDs", "section": "A", "actors": unknown_ids})

            fp = artifact_path.parents[1] / "FEATURES.md"
            ft, ferr = load_text(fp)
            if ferr:
                errors.append({"type": "cross", "message": ferr})
            else:
                feature_id = None
                m_fid = re.search(r"\*\*Feature ID\*\*:\s*`([^`]+)`", a_text)
                if m_fid:
                    feature_id = m_fid.group(1).strip()
                if feature_id and feature_id not in ft:
                    errors.append({"type": "cross", "message": "Feature ID not found in FEATURES.md", "feature_id": feature_id})

    if "E" in sections:
        e_lines = sections["E"]
        req_indices: List[int] = []
        for idx, line in enumerate(e_lines):
            if line.strip().startswith("### "):
                req_indices.append(idx)

        if not req_indices:
            errors.append({"type": "content", "message": "Section E must contain at least one requirement heading", "section": "E"})
        else:
            req_ids: set = set()

            for i, start in enumerate(req_indices):
                end = req_indices[i + 1] if i + 1 < len(req_indices) else len(e_lines)
                block = e_lines[start:end]

                id_line = next((l for l in block if "**ID**:" in l), None)
                if id_line is None:
                    errors.append({"type": "id", "message": "Requirement missing ID line", "section": "E", "line": start + 1})
                else:
                    if not re.match(r"^\s*[-*]\s+\[[ xX]\]\s+\*\*ID\*\*:\s+", id_line):
                        errors.append({"type": "id", "message": "Requirement ID line must be a checkbox list item", "section": "E", "line": start + 1, "text": id_line.strip()})

                    for m in FEATURE_REQ_ID_RE.finditer(id_line):
                        if feature_slug is not None and m.group(1) != feature_slug:
                            errors.append({"type": "id", "message": "Feature slug in requirement ID does not match directory slug", "section": "E", "expected": feature_slug, "found": m.group(1), "line": start + 1})
                    for rid in _extract_full_ids(id_line, "req"):
                        req_ids.add(rid)

                required_fields = ["Status", "Description", "Implementation details", "References", "Implements", "Phases"]
                for field in required_fields:
                    fb = field_block(block, field)
                    if fb is None:
                        errors.append({"type": "content", "message": "Missing required field", "section": "E", "field": field, "line": start + 1})
                        continue

                    if not str(fb["value"]).strip() and not has_list_item(list(fb["tail"])):
                        errors.append({"type": "content", "message": "Field must not be empty", "section": "E", "field": field, "line": start + 1})

                    if field == "Status":
                        status_val = str(fb["value"]).strip()
                        valid_statuses = {"NOT_STARTED", "IN_DESIGN", "DESIGN_READY", "IN_DEVELOPMENT", "IMPLEMENTED"}

                        normalized: Optional[str] = None
                        if "IN_PROGRESS" in status_val:
                            normalized = "IN_DEVELOPMENT"
                        else:
                            for vs in valid_statuses:
                                if vs in status_val:
                                    normalized = vs
                                    break
                        if normalized is None:
                            errors.append({
                                "type": "content",
                                "message": "Status must be one of: NOT_STARTED, IN_DESIGN, DESIGN_READY, IN_DEVELOPMENT, IMPLEMENTED",
                                "section": "E",
                                "field": "Status",
                                "line": start + 1,
                                "found": status_val,
                            })

                phases_field = field_block(block, "Phases")
                phase_list: List[int] = []
                if phases_field is not None:
                    for l in list(phases_field["tail"]):
                        for n in re.findall(r"`ph-(\d+)`", l):
                            phase_list.append(int(n))
                        if re.match(r"^\s*-\s+`ph-\d+`", l.strip()):
                            errors.append({"type": "content", "message": "Phase lines must include a checkbox", "section": "E", "line": start + 1, "text": l.strip()})
                    if 1 not in phase_list:
                        errors.append({"type": "content", "message": "Requirement phases must include ph-1", "section": "E", "line": start + 1})
                    if phase_nums and any(p not in phase_nums for p in phase_list):
                        bad = sorted([p for p in phase_list if p not in phase_nums])
                        errors.append({"type": "content", "message": "Requirement phases must be a subset of feature phases", "section": "E", "line": start + 1, "phases": bad})

                refs_field = field_block(block, "References")
                if refs_field is not None:
                    ref_text = "\n".join([str(refs_field["value"])] + list(refs_field["tail"]))
                    for _, target in LINK_RE.findall(ref_text):
                        t = target.strip()
                        if not t.startswith("#"):
                            continue
                        anchor = t[1:]
                        if anchor and anchor not in anchors:
                            errors.append({"type": "link_target", "message": "Reference anchor does not exist", "section": "E", "line": start + 1, "anchor": anchor})

                impl_field = field_block(block, "Implements")
                if impl_field is not None:
                    impl_text = "\n".join([str(impl_field["value"])] + list(impl_field["tail"]))
                    impl_ids = set(re.findall(r"`([^`]+)`", impl_text))
                    defined = flow_ids | algo_ids | state_ids
                    bad = sorted([x for x in impl_ids if x.startswith("fdd-") and defined and x not in defined])
                    if bad:
                        errors.append({"type": "cross", "message": "Implements references unknown flow/algo/state IDs", "section": "E", "line": start + 1, "ids": bad})

                # Content-quality heuristic: if the document mentions API/DB concepts, require explicit lines in Implementation details.
                impl_details = field_block(block, "Implementation details")
                impl_text = ""
                if impl_details is not None:
                    impl_text = "\n".join([str(impl_details["value"])] + list(impl_details["tail"]))

                doc_lower = ("\n".join(sections.get("B", []) + sections.get("C", []) + sections.get("D", []))).lower()
                if any(x in doc_lower for x in ("/api/", " endpoint", " api", "http")):
                    if "api" not in impl_text.lower():
                        errors.append({"type": "content", "message": "Implementation details must explicitly describe impacted API when API is referenced in flows/algorithms/states", "section": "E", "line": start + 1})
                if any(x in doc_lower for x in ("select ", "insert ", "update ", "delete ", " database", " db ", "postgres")):
                    if "db" not in impl_text.lower() and "database" not in impl_text.lower():
                        errors.append({"type": "content", "message": "Implementation details must explicitly describe impacted DB when DB is referenced in flows/algorithms/states", "section": "E", "line": start + 1})

    if "F" in sections:
        f_lines = sections["F"]
        ctx_ids: set = set()
        for idx, line in enumerate(f_lines, start=1):
            if "**ID**:" not in line:
                continue
            for m in FEATURE_CONTEXT_ID_RE.finditer(line):
                if feature_slug is not None and m.group(1) != feature_slug:
                    errors.append({"type": "id", "message": "Feature slug in context ID does not match directory slug", "section": "F", "expected": feature_slug, "found": m.group(1), "line": idx, "text": line.strip()})
            for cid in _extract_full_ids(line, "context"):
                if cid in ctx_ids:
                    errors.append({"type": "id", "message": "Duplicate context IDs", "section": "F", "line": idx, "id": cid})
                ctx_ids.add(cid)

    passed = (len(errors) == 0) and (len(placeholders) == 0)
    
    status_value = "PASS" if passed else "FAIL"
    
    if not passed:
        status_value = "FAIL"
    
    return {
        "required_section_count": len([s for s in ["A", "B", "C", "D", "E"] if s in sections]),
        "missing_sections": [s for s in ["A", "B", "C", "D", "E"] if s not in sections],
        "placeholder_hits": placeholders,
        "status": status_value,
        "errors": errors,
    }
