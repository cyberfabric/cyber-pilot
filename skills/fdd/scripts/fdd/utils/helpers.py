"""
FDD Validator - Helper Functions

Helper functions for parsing and analyzing artifacts.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ..constants import (
    HEADING_ID_RE,
    ACTOR_ID_RE,
    CAPABILITY_ID_RE,
    PRD_FR_ID_RE,
    USECASE_ID_RE,
    LINK_RE,
    REQ_ID_RE,
    NFR_ID_RE,
    ADR_HEADING_RE,
    ADR_DATE_RE,
    ADR_STATUS_RE,
    ADR_ID_RE,
    ADR_ID_LINE_RE,
    FDD_ADR_NUM_RE,
)

from .markdown import extract_id_payload_block


def find_present_section_ids(artifact_text: str) -> List[str]:
    """Extract all section letter IDs (A, B, C, etc.) present in the artifact."""
    present: List[str] = []
    for line in artifact_text.splitlines():
        m = HEADING_ID_RE.match(line.strip())
        if m:
            present.append(m.group(1))
    return present


def parse_prd_model(text: str) -> Tuple[Set[str], Dict[str, Set[str]], Set[str]]:
    """
    Parse PRD.md and extract actors, capabilities, and use cases.
    
    Returns:
        - Set of actor IDs
        - Dict mapping capability IDs to their actor IDs
        - Set of use case IDs
    """
    actor_ids: Set[str] = set(ACTOR_ID_RE.findall(text))
    capability_to_actors: Dict[str, Set[str]] = {}
    usecase_ids: Set[str] = set(USECASE_ID_RE.findall(text))

    lines = text.splitlines()

    # Parse "Capabilities" blocks (or legacy "Functional Requirements") and map ID -> referenced actors.
    in_c_section = False
    current_id: Optional[str] = None

    for line in lines:
        s = line.strip()

        if s.startswith("## "):
            # Enter Section C variants:
            # - lettered: "## C. ..." / "## Section C: ..."
            # - content named: "## Capabilities" / "## B. Capabilities"
            # - legacy: "## C. Functional Requirements"
            in_c_section = bool(
                re.search(r"^##\s+(?:Section\s+)?C\b", s, re.IGNORECASE)
                or re.search(r"^##\s+C\.\s+", s, re.IGNORECASE)
                or re.search(r"capabilities", s, re.IGNORECASE)
                or re.search(r"functional\s+requirements", s, re.IGNORECASE)
            )
            current_id = None
            continue

        if not in_c_section:
            continue

        # Detect new block ID (capability preferred, but allow legacy fr IDs)
        cap_matches = CAPABILITY_ID_RE.findall(s)
        fr_matches = PRD_FR_ID_RE.findall(s)

        if cap_matches:
            current_id = cap_matches[0]
            capability_to_actors.setdefault(current_id, set())
            continue
        if fr_matches:
            current_id = fr_matches[0]
            capability_to_actors.setdefault(current_id, set())
            continue

        # Collect actor references within the current block
        if current_id:
            for aid in ACTOR_ID_RE.findall(s):
                capability_to_actors[current_id].add(aid)

    return actor_ids, capability_to_actors, usecase_ids


ADR_FILENAME_RE = re.compile(r"^(\d{4})-(fdd-[a-z0-9-]+-adr-[a-z0-9-]+)\.md$")


def load_adr_entries(adr_path: Path) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    """Load ADR entries from either a legacy single file or the ADR/ directory model."""
    adr_path = Path(adr_path)
    if not adr_path.exists():
        return [], [{"type": "file", "message": f"ADR path not found: {adr_path}"}]

    if not adr_path.is_dir():
        return [], [{"type": "file", "message": f"ADR path must be a directory: {adr_path}"}]

    return scan_adr_directory(adr_path)


def scan_adr_directory(adr_dir: Path) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    """
    Scan ADR/ directory for per-record ADR files.

    Expected layout:
    - ADR/{category}/0001-fdd-...-adr-...md
    - ADR/0001-fdd-...-adr-...md (category optional)

    Returns:
        - ADR entries
        - Validation issues
    """
    issues: List[Dict[str, object]] = []
    adrs: List[Dict[str, object]] = []

    try:
        files = sorted([p for p in adr_dir.rglob("*.md") if p.is_file() and not p.name.startswith(".")])
    except Exception as e:
        return [], [{"type": "file", "message": f"Failed to scan ADR directory: {adr_dir}: {e}"}]

    if not files:
        return [], [{"type": "structure", "message": "No ADR files found"}]

    for pth in files:
        mfn = ADR_FILENAME_RE.match(pth.name)
        if not mfn:
            continue

        file_num = int(mfn.group(1))
        file_id = mfn.group(2)

        try:
            text = pth.read_text(encoding="utf-8")
        except Exception as e:
            issues.append({"type": "file", "message": f"Failed to read ADR file: {e}", "path": str(pth)})
            continue

        headings = [mm for mm in ADR_HEADING_RE.finditer(text)]
        if len(headings) != 1:
            issues.append({"type": "structure", "message": "ADR file must contain exactly one ADR heading", "path": str(pth), "count": len(headings)})
            continue

        h = headings[0]
        if not h.group(0).lstrip().startswith("# "):
            issues.append({"type": "structure", "message": "ADR heading must be an H1 heading (#)", "path": str(pth), "heading": h.group(0).strip()})
        adr_ref = h.group(1)
        adr_num = int(h.group(2))
        title = h.group(3)
        if adr_num != file_num:
            issues.append({"type": "structure", "message": "ADR number in filename must match ADR heading", "path": str(pth), "filename": file_num, "heading": adr_num})

        # Look ahead for metadata (up to 10 lines after heading)
        date_val: Optional[str] = None
        status_val: Optional[str] = None
        adr_id: Optional[str] = None

        lines = text.splitlines()
        heading_line_idx = 0
        for idx, line in enumerate(lines):
            if ADR_HEADING_RE.match(line.strip()):
                heading_line_idx = idx
                break

        for j in range(heading_line_idx + 1, min(heading_line_idx + 11, len(lines))):
            next_line = lines[j]

            date_m = ADR_DATE_RE.search(next_line)
            if date_m:
                date_val = date_m.group(1)

            status_m = ADR_STATUS_RE.search(next_line)
            if status_m:
                status_val = status_m.group(1)

            id_m = ADR_ID_LINE_RE.search(next_line)
            if id_m:
                adr_id = id_m.group(1)

            if next_line.strip().startswith("## "):
                break

        if adr_id is None:
            issues.append({"type": "structure", "message": "ADR missing or invalid **ADR ID** line", "path": str(pth), "adr": adr_ref})
        elif adr_id != file_id:
            issues.append({"type": "structure", "message": "ADR file ID must match filename ID", "path": str(pth), "filename_id": file_id, "id": adr_id})

        adrs.append({"ref": adr_ref, "num": adr_num, "title": title, "date": date_val, "status": status_val, "id": adr_id, "path": str(pth)})

    if not adrs:
        return [], (issues + [{"type": "structure", "message": "No ADR entries found"}])

    nums = sorted([int(a.get("num", 0)) for a in adrs])
    expected = list(range(1, len(nums) + 1))
    if nums != expected:
        issues.append({"type": "structure", "message": "ADR numbers must be sequential starting at ADR-0001 with no gaps", "found": nums})
    if 1 not in nums:
        issues.append({"type": "structure", "message": "ADR-0001 must exist"})

    dup_nums = sorted({n for n in nums if nums.count(n) > 1})
    if dup_nums:
        issues.append({"type": "structure", "message": "Duplicate ADR numbers", "nums": dup_nums})

    fdd_ids = [str(a.get("id")) for a in adrs if a.get("id")]
    dup_fdd = sorted({x for x in fdd_ids if fdd_ids.count(x) > 1})
    if dup_fdd:
        issues.append({"type": "structure", "message": "Duplicate ADR IDs", "ids": dup_fdd})

    # Stable ordering: by ADR number
    adrs = sorted(adrs, key=lambda a: int(a.get("num", 0)))
    return adrs, issues


def parse_prd_capability_statuses(text: str) -> Dict[str, Dict[str, object]]:
    lines = text.splitlines()

    start_idx: Optional[int] = None
    for i, line in enumerate(lines):
        if line.strip() == "## C. Functional Requirements":
            start_idx = i
            break
    if start_idx is None:
        return {}

    end_idx = len(lines)
    for j in range(start_idx + 1, len(lines)):
        if lines[j].strip().startswith("## "):
            end_idx = j
            break

    out: Dict[str, Dict[str, object]] = {}

    cap_id_line_re = re.compile(r"^\s*\*\*ID\*\*:\s*`([^`]+)`")
    status_re = re.compile(r"^\s*\*\*Status\*\*:\s*(.+?)\s*$", re.MULTILINE)

    current_heading: Optional[str] = None
    for idx in range(start_idx, end_idx):
        s = lines[idx].strip()
        if s.startswith("#### "):
            current_heading = s.removeprefix("#### ").strip()
            continue
        if "**ID**:" not in s:
            continue
        m = cap_id_line_re.match(s)
        if not m:
            continue
        cap_id = m.group(1).strip()
        if not PRD_FR_ID_RE.fullmatch(cap_id):
            continue

        payload = extract_id_payload_block(lines, id_idx=idx)
        payload_text = str(payload.get("text")) if isinstance(payload, dict) else ""
        status_val: Optional[str] = None
        m_status = status_re.search(payload_text)
        if m_status:
            raw = m_status.group(1).strip()
            if "IMPLEMENTED" in raw:
                status_val = "IMPLEMENTED"
            elif "DESIGNED" in raw:
                status_val = "DESIGNED"

        features: List[str] = []
        for _, target in LINK_RE.findall(payload_text):
            t = target.strip()
            if not t.startswith("feature-"):
                continue
            if not t.endswith("/"):
                t = t + "/"
            features.append(t)
        features = sorted(set(features))

        out[cap_id] = {
            "status": status_val,
            "features": features,
            "heading": current_heading,
            "line": idx + 1,
        }

    return out


def parse_design_requirement_statuses(text: str) -> Dict[str, str]:
    lines = text.splitlines()
    out: Dict[str, str] = {}

    id_line_re = re.compile(r"^\s*\*\*ID\*\*:\s*`([^`]+)`")
    status_re = re.compile(r"^\s*\*\*Status\*\*:\s*(.+?)\s*$", re.MULTILINE)

    for idx, line in enumerate(lines):
        if "**ID**:" not in line:
            continue
        m = id_line_re.match(line.strip())
        if not m:
            continue
        rid = m.group(1).strip()
        if not (REQ_ID_RE.fullmatch(rid) or NFR_ID_RE.fullmatch(rid)):
            continue

        payload = extract_id_payload_block(lines, id_idx=idx)
        payload_text = str(payload.get("text")) if isinstance(payload, dict) else ""
        m_status = status_re.search(payload_text)
        if not m_status:
            continue
        raw = m_status.group(1).strip()
        if "IMPLEMENTED" in raw:
            out[rid] = "IMPLEMENTED"
        elif "IN_FEATURE" in raw:
            out[rid] = "IN_FEATURE"

    return out


__all__ = [
    "find_present_section_ids",
    "parse_prd_model",
    "load_adr_entries",
    "scan_adr_directory",
    "parse_prd_capability_statuses",
    "parse_design_requirement_statuses",
]
