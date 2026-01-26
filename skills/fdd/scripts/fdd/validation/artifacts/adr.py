"""
FDD Validator - ADR Validation

Validates architectural decision records.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ...constants import (
    ADR_DATE_RE,
    ADR_HEADING_RE,
    ADR_ID_LINE_RE,
    ADR_ID_RE,
    ADR_NUM_RE,
    ADR_STATUS_RE,
    ACTOR_ID_RE,
    CAPABILITY_ID_RE,
    PRD_FR_ID_RE,
    PRINCIPLE_ID_RE,
    REQ_ID_RE,
)

from ...utils import (
    find_placeholders,
    load_adr_entries,
    load_text,
)


__all__ = ["validate_adr"]
def validate_adr(
    artifact_text: str,
    *,
    artifact_path: Optional[Path] = None,
    prd_path: Optional[Path] = None,
    design_path: Optional[Path] = None,
    skip_fs_checks: bool = False,
) -> Dict[str, object]:
    errors: List[Dict[str, object]] = []

    # Directory-mode validation: architecture/ADR/ contains many per-record ADR files.
    if artifact_path is not None and artifact_path.exists() and artifact_path.is_dir():
        adr_entries, issues = load_adr_entries(artifact_path)
        errors.extend(issues)

        placeholders: List[Dict[str, object]] = []
        prd_actors: set = set()
        prd_caps: set = set()
        design_req: set = set()
        design_principle: set = set()

        if not skip_fs_checks:
            bp = prd_path or (artifact_path.parent / "PRD.md")
            dp = design_path or (artifact_path.parent / "DESIGN.md")

            bt, berr = load_text(bp)
            if berr:
                errors.append({"type": "cross", "message": berr})
            else:
                prd_actors = set(ACTOR_ID_RE.findall(bt or ""))
                prd_caps = set(CAPABILITY_ID_RE.findall(bt or "")) | set(PRD_FR_ID_RE.findall(bt or ""))

            dt, derr = load_text(dp)
            if derr:
                errors.append({"type": "cross", "message": derr})
            else:
                design_req = set(REQ_ID_RE.findall(dt or ""))
                design_principle = set(PRINCIPLE_ID_RE.findall(dt or ""))

        per_file_issues: List[Dict[str, object]] = []
        for e in adr_entries:
            p = e.get("path")
            if not p:
                continue
            try:
                t = Path(str(p)).read_text(encoding="utf-8")
            except Exception as ex:
                per_file_issues.append({"adr": e.get("ref"), "message": f"Failed to read ADR file: {ex}", "path": str(p)})
                continue

            placeholders.extend(find_placeholders(t))
            per_file_issues.extend(
                _validate_single_adr_text(
                    t,
                    adr_ref=str(e.get("ref")),
                    require_h1=True,
                    prd_actors=prd_actors,
                    prd_caps=prd_caps,
                    design_req=design_req,
                    design_principle=design_principle,
                )
            )

        passed = (len(errors) == 0) and (len(per_file_issues) == 0) and (len(placeholders) == 0)
        return {
            "required_section_count": 4,
            "missing_sections": [],
            "placeholder_hits": placeholders,
            "status": "PASS" if passed else "FAIL",
            "errors": errors,
            "adr_issues": per_file_issues,
            "adr_count": len(adr_entries),
        }

    placeholders = find_placeholders(artifact_text)

    prd_actors: set = set()
    prd_caps: set = set()
    design_req: set = set()
    design_principle: set = set()

    if not skip_fs_checks and artifact_path is not None:
        bp = prd_path or (artifact_path.parent / "PRD.md")
        dp = design_path or (artifact_path.parent / "DESIGN.md")

        bt, berr = load_text(bp)
        if berr:
            errors.append({"type": "cross", "message": berr})
        else:
            prd_actors = set(ACTOR_ID_RE.findall(bt or ""))
            prd_caps = set(CAPABILITY_ID_RE.findall(bt or "")) | set(PRD_FR_ID_RE.findall(bt or ""))

        dt, derr = load_text(dp)
        if derr:
            errors.append({"type": "cross", "message": derr})
        else:
            design_req = set(REQ_ID_RE.findall(dt or ""))
            design_principle = set(PRINCIPLE_ID_RE.findall(dt or ""))

    per_adr_issues = _validate_single_adr_text(
        artifact_text,
        adr_ref=None,
        require_h1=True,
        prd_actors=prd_actors,
        prd_caps=prd_caps,
        design_req=design_req,
        design_principle=design_principle,
    )

    passed = (len(errors) == 0) and (len(per_adr_issues) == 0) and (len(placeholders) == 0)
    return {
        "required_section_count": 4,
        "missing_sections": [],
        "placeholder_hits": placeholders,
        "status": "PASS" if passed else "FAIL",
        "errors": errors,
        "adr_issues": per_adr_issues,
        "adr_count": 1,
    }


MADR_H1_RE = re.compile(r"^#\s+(ADR-(\d{4})):\s+(.+?)\s*$", re.MULTILINE)
ADR_ENTRY_RE = ADR_HEADING_RE


def _validate_single_adr_text(
    text: str,
    *,
    adr_ref: Optional[str],
    require_h1: bool,
    prd_actors: Optional[set] = None,
    prd_caps: Optional[set] = None,
    design_req: Optional[set] = None,
    design_principle: Optional[set] = None,
) -> List[Dict[str, object]]:
    issues: List[Dict[str, object]] = []

    def _has_heading(block: str, title: str) -> bool:
        t = re.escape(title)
        return (
            re.search(rf"^##\s+{t}\s*$", block, flags=re.MULTILINE) is not None
            or re.search(rf"^###\s+{t}\s*$", block, flags=re.MULTILINE) is not None
        )

    def _related_block(block: str) -> Optional[str]:
        if re.search(r"^##\s+Related Design Elements\s*$", block, flags=re.MULTILINE) is not None:
            return block.split("## Related Design Elements", 1)[1]
        if re.search(r"^###\s+Related Design Elements\s*$", block, flags=re.MULTILINE) is not None:
            return block.split("### Related Design Elements", 1)[1]
        return None

    h1 = [m for m in MADR_H1_RE.finditer(text)]
    is_single_record = len(h1) == 1
    if require_h1 and not is_single_record:
        issues.append({"adr": adr_ref or "(file)", "message": "ADR must have exactly one H1 heading: '# ADR-NNNN: Title'"})
        return issues

    if is_single_record:
        if ADR_DATE_RE.search(text) is None:
            issues.append({"adr": adr_ref or "(file)", "message": "Missing **Date**: YYYY-MM-DD"})
        if ADR_STATUS_RE.search(text) is None:
            issues.append({"adr": adr_ref or "(file)", "message": "Missing or invalid **Status**"})
        if ADR_ID_LINE_RE.search(text) is None:
            issues.append({"adr": adr_ref or "(file)", "message": "Missing or invalid **ADR ID** line"})

        if "Chosen option:" not in text:
            issues.append({"adr": adr_ref or "(file)", "message": "Decision Outcome must include 'Chosen option:'"})

        required_sections = [
            "Context and Problem Statement",
            "Considered Options",
            "Decision Outcome",
            "Related Design Elements",
        ]
        for sec in required_sections:
            if not _has_heading(text, sec):
                issues.append({"adr": adr_ref or "(file)", "message": f"Missing required section: {sec}"})

        rel = _related_block(text)
        if rel is not None:
            referenced = (
                set(ACTOR_ID_RE.findall(rel))
                | set(CAPABILITY_ID_RE.findall(rel))
                | set(PRD_FR_ID_RE.findall(rel))
                | set(REQ_ID_RE.findall(rel))
                | set(PRINCIPLE_ID_RE.findall(rel))
            )
            if not referenced:
                issues.append({"adr": adr_ref or "(file)", "message": "Related Design Elements must contain at least one ID"})

            if prd_actors:
                bad = sorted([x for x in ACTOR_ID_RE.findall(rel) if x not in prd_actors])
                if bad:
                    issues.append({"adr": adr_ref or "(file)", "message": "Unknown actor IDs in Related Design Elements", "ids": bad})
            if prd_caps:
                rel_caps = set(CAPABILITY_ID_RE.findall(rel)) | set(PRD_FR_ID_RE.findall(rel))
                bad = sorted([x for x in rel_caps if x not in prd_caps])
                if bad:
                    issues.append({"adr": adr_ref or "(file)", "message": "Unknown PRD IDs in Related Design Elements", "ids": bad})
            if design_req:
                bad = sorted([x for x in REQ_ID_RE.findall(rel) if x not in design_req])
                if bad:
                    issues.append({"adr": adr_ref or "(file)", "message": "Unknown requirement IDs in Related Design Elements", "ids": bad})
            if design_principle:
                bad = sorted([x for x in PRINCIPLE_ID_RE.findall(rel) if x not in design_principle])
                if bad:
                    issues.append({"adr": adr_ref or "(file)", "message": "Unknown principle IDs in Related Design Elements", "ids": bad})

        return issues

    return issues


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
