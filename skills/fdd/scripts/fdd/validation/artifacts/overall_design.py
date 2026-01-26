"""
FDD Validator - Overall DESIGN.md Validation

Validates architecture/DESIGN.md: system design, requirements, NFRs, principles, constraints.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ...constants import (
    ADR_ID_RE,
    ADR_NUM_RE,
    ACTOR_ID_RE,
    USECASE_ID_RE,
)

from ...utils import (
    find_placeholders,
    load_text,
    find_present_section_ids,
    parse_prd_model,
    load_adr_entries,
)


__all__ = ["validate_overall_design"]
def validate_overall_design(
    artifact_text: str,
    *,
    artifact_path: Optional[Path] = None,
    prd_path: Optional[Path] = None,
    adr_path: Optional[Path] = None,
    skip_fs_checks: bool = False,
) -> Dict[str, object]:
    errors: List[Dict[str, object]] = []
    placeholders = find_placeholders(artifact_text)

    present = find_present_section_ids(artifact_text)
    needed = ["A", "B", "C"]
    missing = [s for s in needed if s not in set(present)]
    if missing:
        errors.append({"type": "structure", "message": "Missing required top-level sections", "missing": missing})

    b_subs = [m.group(1) for m in re.finditer(r"^###\s+B\.(\d+)\s*[:.]", artifact_text, re.MULTILINE)]
    expected_b = ["1", "2"]
    if not b_subs:
        errors.append({"type": "structure", "message": "Section B must include subsections B.1..B.2", "expected": expected_b})
    elif b_subs != expected_b:
        errors.append({"type": "structure", "message": "Section B must have exactly B.1..B.2 in order", "found": b_subs, "expected": expected_b})

    c_subs = [m.group(1) for m in re.finditer(r"^###\s+C\.(\d+)\s*[:.]", artifact_text, re.MULTILINE)]
    required_c = ["1", "2", "3", "4"]
    optional_c = {"5", "6", "7"}
    if not c_subs:
        errors.append({"type": "structure", "message": "Section C must include subsections C.1..C.4", "expected": required_c})
    else:
        if len(c_subs) < len(required_c) or c_subs[:4] != required_c:
            errors.append({"type": "structure", "message": "Section C must include C.1..C.4 in order", "found": c_subs, "expected": required_c})
        else:
            tail = c_subs[4:]
            bad_tail = [x for x in tail if x not in optional_c]
            if bad_tail:
                errors.append({"type": "structure", "message": "Section C optional subsections may only include C.5..C.7", "found": tail, "bad": bad_tail})
            else:
                ordered_tail = sorted(tail, key=lambda s: int(s))
                if tail != ordered_tail:
                    errors.append({"type": "structure", "message": "Section C optional subsections must be in ascending order", "found": tail})

    has_arch_drivers = re.search(r"^###\s+Architecture drivers\s*$", artifact_text, re.MULTILINE) is not None
    if not has_arch_drivers:
        errors.append({"type": "structure", "message": "Section A must include '### Architecture drivers'"})
    else:
        if re.search(r"^####\s+Product requirements\s*$", artifact_text, re.MULTILINE) is None:
            errors.append({"type": "structure", "message": "Architecture drivers must include '#### Product requirements'"})
        header_re = re.compile(r"^\|\s*FDD ID\s*\|\s*Solution short description\s*\|\s*$", re.MULTILINE)
        if header_re.search(artifact_text) is None:
            errors.append({"type": "structure", "message": "Product requirements must include a table with columns: FDD ID | Solution short description"})

    prd_actors: set = set()
    prd_usecases: set = set()
    adr_ids: set = set()
    adr_num_to_id: Dict[int, str] = {}

    if not skip_fs_checks and artifact_path is not None:
        bp = prd_path or (artifact_path.parent / "PRD.md")
        ap = adr_path or (artifact_path.parent / "ADR")

        bt, berr = load_text(bp)
        if berr:
            errors.append({"type": "cross", "message": berr})
        else:
            prd_actors, _prd_caps_to_actors, prd_usecases = parse_prd_model(bt or "")

        if ap.exists() and ap.is_dir():
            adr_entries, adr_issues = load_adr_entries(ap)
            errors.extend(adr_issues)
            for e in adr_entries:
                if "id" in e and e["id"]:
                    adr_ids.add(str(e["id"]))
                if "num" in e and "id" in e and e.get("id"):
                    adr_num_to_id[int(e["num"])] = str(e["id"])  # type: ignore[arg-type]

    reference_issues: List[Dict[str, object]] = []

    if prd_actors:
        referenced_actors = sorted(set(ACTOR_ID_RE.findall(artifact_text)))
        bad = [a for a in referenced_actors if a not in prd_actors]
        if bad:
            reference_issues.append({"message": "Unknown actor IDs", "ids": bad})

    if prd_usecases:
        referenced_usecases = sorted(set(USECASE_ID_RE.findall(artifact_text)))
        bad = [u for u in referenced_usecases if u not in prd_usecases]
        if bad:
            reference_issues.append({"message": "Unknown use case IDs", "ids": bad})

    if adr_ids:
        referenced_adrs: Set[str] = set(ADR_ID_RE.findall(artifact_text))
        for n in ADR_NUM_RE.findall(artifact_text):
            mapped = adr_num_to_id.get(int(n))
            if mapped:
                referenced_adrs.add(mapped)
        bad = sorted([a for a in referenced_adrs if a not in adr_ids])
        if bad:
            reference_issues.append({"message": "Unknown ADR references", "ids": bad})

    passed = (len(errors) == 0) and (len(reference_issues) == 0) and (len(placeholders) == 0)
    return {
        "required_section_count": 3,
        "missing_sections": [{"id": s, "title": ""} for s in missing],
        "placeholder_hits": placeholders,
        "status": "PASS" if passed else "FAIL",
        "errors": errors,
        "requirement_issues": reference_issues,
        "requirement_count": 0,
    }


FIELD_HEADER_RE = re.compile(r"^\s*[-*]?\s*\*\*([^*]+)\*\*:\s*(.*)$")

KNOWN_FIELD_NAMES = {
    "Purpose",
    "Target Users",
    "Key Problems Solved",
    "Success Criteria",
    "Actor",
    "Actors",
    "Role",
    "Preconditions",
    "Flow",
    "Postconditions",
    "Status",
    "Depends On",
    "Blocks",
    "Scope",
    "Requirements Covered",
    "Principles Covered",
    "Constraints Affected",
    "Phases",
    "References",
    "Implements",
    "ADRs",
    "Capabilities",
    "Technology",
    "Location",
    "Input",
    "Output",
    "Testing Scenarios",
    "Testing Scenarios (FDL)",
    "Acceptance Criteria",
}
