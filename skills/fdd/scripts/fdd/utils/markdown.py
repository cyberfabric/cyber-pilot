"""
FDD Validator - Markdown Structure Utilities

Functions for extracting and navigating markdown document structures.
"""

import re
from typing import Dict, List, Optional, Tuple

from ..constants import SECTION_FEATURE_RE, FEATURE_HEADING_RE, SECTION_PRD_RE


def get_heading_level(line: str) -> Optional[int]:
    """
    Get markdown heading level from line.
    
    Args:
        line: Line to check
    
    Returns:
        Heading level (1-6) or None if not a heading
    """
    m = re.match(r"^(#{1,6})\s+", line)
    if not m:
        return None

    return len(m.group(1))


def list_section_entries(lines: List[str], *, kind: str) -> List[Dict[str, object]]:
    entries: List[Dict[str, object]] = []
    if kind == "features-manifest":
        for i, line in enumerate(lines, start=1):
            m = FEATURE_HEADING_RE.match(line.strip())
            if not m:
                continue
            entries.append(
                {
                    "line": i,
                    "feature_id": m.group(2),
                    "index": int(m.group(1)),
                    "dir": m.group(3),
                    "emoji": m.group(4),
                    "priority": m.group(5),
                }
            )
        return entries

    for i, line in enumerate(lines, start=1):
        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", line.strip())
        if not m:
            continue
        entries.append({"line": i, "level": len(m.group(1)), "title": m.group(2).strip()})
    return entries


def read_feature_entry(lines: List[str], feature_id: str) -> Optional[Tuple[int, int]]:
    fid = str(feature_id)
    for i, line in enumerate(lines):
        m = FEATURE_HEADING_RE.match(line)
        if m and m.group(2) == fid:
            start = i
            end = i + 1
            while end < len(lines) and not FEATURE_HEADING_RE.match(lines[end]):
                end += 1
            return start, end
    return None


def read_letter_section(lines: List[str], letter: str) -> Optional[Tuple[int, int]]:
    lt = str(letter).strip().upper()
    start_idx: Optional[int] = None
    for i, line in enumerate(lines):
        if re.match(rf"^##\s+{re.escape(lt)}\.\s+", line.strip()):
            start_idx = i
            break
    if start_idx is None:
        return None
    end = start_idx + 1
    while end < len(lines) and not re.match(r"^##\s+[A-Z]\.\s+", lines[end].strip()):
        end += 1
    return start_idx, end


def read_heading_block_by_title(lines: List[str], title: str) -> Optional[Tuple[int, int]]:
    needle = str(title).strip()
    start_idx: Optional[int] = None
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if m and m.group(2).strip() == needle:
            start_idx = i
            break
    if start_idx is None:
        return None
    start, end = extract_block(lines, start_idx)
    return start, end


def list_items(
    *,
    kind: str,
    artifact_name: str,
    lines: List[str],
    active_lines: List[str],
    base_offset: int,
    lod: str,
    pattern: Optional[str],
    regex: bool,
    type_filter: Optional[str],
) -> List[Dict[str, object]]:
    from .. import constants
    from .search import extract_ids, infer_fdd_type
    from .helpers import scan_adr_directory

    id_filter = pattern
    rx: Optional[re.Pattern] = None
    if id_filter and regex:
        rx = re.compile(str(id_filter))

    items: List[Dict[str, object]] = []

    if kind == "features-manifest":
        for i, line in enumerate(active_lines, start=base_offset + 1):
            m = FEATURE_HEADING_RE.match(line.strip())
            if not m:
                continue
            fid = m.group(2)
            it: Dict[str, object] = {"type": "feature", "id": fid, "line": i}
            if lod == "summary":
                it.update({"index": int(m.group(1)), "dir": m.group(3), "emoji": m.group(4), "priority": m.group(5)})
            items.append(it)

    elif kind == "generic" and artifact_name == "PRD.md":
        section: Optional[str] = None
        for idx, line in enumerate(active_lines):
            m = SECTION_PRD_RE.match(line.strip())
            if m:
                section = m.group(1)
            if not line.strip().startswith("#### "):
                continue

            title = line.strip().removeprefix("#### ").strip()
            j = idx + 1
            while j < len(active_lines) and not active_lines[j].strip():
                j += 1
            id_line = active_lines[j] if j < len(active_lines) else ""
            ids = [h["id"] for h in extract_ids([id_line]) if str(h.get("kind")) == "fdd"]
            if not ids:
                continue
            iid = str(ids[0])
            itype = "item"
            if section == "B":
                itype = "actor"
            elif section == "C":
                itype = "functional-requirement"
            elif section == "D":
                itype = "usecase"
            elif section == "E":
                itype = "nfr"
            elif section == "F":
                itype = "prd-context"
            abs_idx = base_offset + idx
            it = {"type": itype, "id": iid, "line": abs_idx + 1}
            if lod == "summary":
                it.update({"title": title, "section": section})
            items.append(it)

    elif kind == "overall-design":
        id_line_re = re.compile(r"^\s*(?:[-*]\s+\[[ xX]\]\s+)?\*\*ID\*\*:\s*(.+?)\s*$")
        for rel_idx, line in enumerate(active_lines):
            m = id_line_re.match(line.strip())
            if not m:
                continue
            ids = [h["id"] for h in extract_ids([m.group(1)]) if str(h.get("kind")) == "fdd"]
            if not ids:
                continue
            iid_s = str(ids[0])
            itype = infer_fdd_type(iid_s)
            checked = "[x]" in line or "[X]" in line
            abs_idx = base_offset + rel_idx
            it = {"type": itype, "id": iid_s, "line": abs_idx + 1}
            if lod == "summary":
                it.update({"title": find_nearest_heading(lines, from_idx=abs_idx), "checked": checked})
            items.append(it)

    elif kind == "adr":
        # Canonical ADR artifact is a directory (architecture/ADR/) with per-record ADR files.
        # For list-items, we summarize each ADR file by ADR-NNNN number and title.
        from pathlib import Path

        adr_dir = Path(constants.__file__).resolve()  # placeholder init
        # Caller provides no path here; we infer from artifact_name only in legacy callers.
        # In CLI, kind == 'adr' is only produced when the artifact_path is a directory, so
        # the CLI must bypass this helper when it doesn't have a directory.
        # For compatibility with direct callers (tests), allow passing artifact_name == 'ADR'.
        if artifact_name != "ADR":
            return items

        # In direct callers, active_lines are not meaningful for directories.
        # Return empty list here and rely on CLI path-based listing.
        return items

    elif kind == "feature-design":
        id_line_re = re.compile(r"^\s*(?:[-*]\s+\[[ xX]\]\s+)?\*\*ID\*\*:\s*(.+?)\s*$")
        for rel_idx, line in enumerate(active_lines):
            m = id_line_re.match(line.strip())
            if not m:
                continue
            ids = [h["id"] for h in extract_ids([m.group(1)]) if str(h.get("kind")) == "fdd"]
            if not ids:
                continue
            iid_s = str(ids[0])
            itype = infer_fdd_type(iid_s)
            checked = "[x]" in line or "[X]" in line
            abs_idx = base_offset + rel_idx
            it = {"type": itype, "id": iid_s, "line": abs_idx + 1}
            if lod == "summary":
                it.update({"title": find_nearest_heading(lines, from_idx=abs_idx), "checked": checked})
            items.append(it)

    if id_filter:
        if rx is not None:
            items = [it for it in items if rx.search(str(it.get("id", ""))) is not None]
        else:
            items = [it for it in items if str(id_filter) in str(it.get("id", ""))]

    if type_filter:
        items = [it for it in items if str(it.get("type")) == str(type_filter)]

    items = sorted(items, key=lambda it: (str(it.get("type", "")), str(it.get("id", "")), int(it.get("line", 0))))
    return items


def find_nearest_heading(lines: List[str], *, from_idx: int) -> Optional[str]:
    """
    Find nearest heading title before given index.
    
    Args:
        lines: Document lines
        from_idx: Index to search backwards from
    
    Returns:
        Heading title or None if not found
    """
    for i in range(from_idx, -1, -1):
        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", lines[i])
        if m:
            return m.group(2)
    return None


def extract_heading_block(lines: List[str], anchor_idx: int) -> Tuple[int, int]:
    """
    Extract block starting from heading at anchor_idx.
    
    Args:
        lines: Document lines
        anchor_idx: Index of heading line
    
    Returns:
        Tuple of (start_idx, end_idx)
    """
    start = anchor_idx
    while start > 0 and get_heading_level(lines[start]) is None:
        start -= 1
    level = get_heading_level(lines[start])
    if level is None:
        return anchor_idx, anchor_idx + 1

    end = start + 1
    while end < len(lines):
        lvl = get_heading_level(lines[end])
        if lvl is not None and lvl <= level:
            break
        end += 1
    return start, end


def resolve_under_heading(lines: List[str], heading: str) -> Optional[Tuple[int, int, int]]:
    needle = heading.strip()
    for idx, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not m:
            continue
        title = m.group(2).strip()
        if title != needle:
            continue
        start, end = extract_heading_block(lines, idx)
        level = len(m.group(1))
        return start, end, level
    return None


def extract_block(lines: List[str], start_idx: int) -> Tuple[int, int]:
    """
    Extract block from start_idx to next heading.
    
    Args:
        lines: Document lines
        start_idx: Starting index
    
    Returns:
        Tuple of (start_idx, end_idx)
    """
    start = start_idx
    while start > 0 and not re.match(r"^#{1,6}\s+", lines[start]):
        start -= 1
    
    end = start_idx + 1
    while end < len(lines) and not re.match(r"^#{1,6}\s+", lines[end]):
        end += 1
    return start, end


def get_section_indices(lines: List[str], section_re: re.Pattern) -> Dict[str, Tuple[int, int]]:
    """
    Get indices of lettered sections in document.
    
    Args:
        lines: Document lines
        section_re: Regex pattern for section headers
    
    Returns:
        Dict mapping section letter to (start, end) indices
    """
    starts: List[Tuple[str, int]] = []
    for i, line in enumerate(lines):
        m = section_re.match(line.strip())
        if m:
            starts.append((m.group(1).upper(), i))
    
    out: Dict[str, Tuple[int, int]] = {}
    for i, (letter, start) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else len(lines)
        out[letter] = (start, end)
    return out


def get_feature_sections(lines: List[str]) -> Dict[str, Tuple[int, int]]:
    """
    Get section indices for feature DESIGN.md (A-G sections).
    
    Args:
        lines: Document lines
    
    Returns:
        Dict mapping section letter to (start, end) indices
    """
    starts: List[Tuple[str, int]] = []
    for i, line in enumerate(lines):
        m = SECTION_FEATURE_RE.match(line.strip())
        if m:
            starts.append((m.group(1).upper(), i))
    
    out: Dict[str, Tuple[int, int]] = {}
    for i, (letter, start) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else len(lines)
        out[letter] = (start, end)
    return out


def get_design_subsections(lines: List[str], *, start: int, end: int) -> Dict[int, Tuple[int, int]]:
    """
    Get subsection indices within design section.
    
    Args:
        lines: Document lines
        start: Section start index
        end: Section end index
    
    Returns:
        Dict mapping subsection number to (start, end) indices
    """
    sub_re = re.compile(r"^###\s+(\d+)\.\s+(.+?)\s*$")
    starts: List[Tuple[int, int]] = []
    for i in range(start, end):
        m = sub_re.match(lines[i].strip())
        if m:
            starts.append((int(m.group(1)), i))
    
    out: Dict[int, Tuple[int, int]] = {}
    for i, (num, sub_start) in enumerate(starts):
        sub_end = starts[i + 1][1] if i + 1 < len(starts) else end
        out[num] = (sub_start, sub_end)
    return out


def find_nearest_prev_heading(lines: List[str], *, idx: int, start: int, prefix: str) -> Optional[int]:
    """
    Find nearest previous heading with given prefix.
    
    Args:
        lines: Document lines
        idx: Index to search backwards from
        start: Don't search before this index
        prefix: Heading prefix to match (e.g., "#### ")
    
    Returns:
        Index of heading or None
    """
    for i in range(idx, start - 1, -1):
        if lines[i].strip().startswith(prefix):
            return i
    return None


def resolve_heading(lines: List[str], heading: str) -> Optional[Tuple[int, int, int]]:
    """
    Resolve heading to its indices and level.
    
    Args:
        lines: Document lines
        heading: Heading text to find
    
    Returns:
        Tuple of (index, level, end) or None
    """
    needle = heading.strip()
    for idx, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not m:
            continue
        if m.group(2).strip() == needle:
            level = len(m.group(1))
            end = idx + 1
            while end < len(lines):
                m2 = re.match(r"^(#{1,6})\s+", lines[end])
                if m2 and len(m2.group(1)) <= level:
                    break
                end += 1
            return idx, level, end
    return None


def find_id_line(lines: List[str], needle: str) -> Optional[int]:
    """
    Find line containing needle.
    
    Args:
        lines: Lines to search
        needle: String to find
    
    Returns:
        Line index or None
    """
    for idx, line in enumerate(lines):
        if needle in line:
            return idx
    return None


def extract_payload_block(lines: List[str], *, start_idx: int) -> Optional[Tuple[int, int]]:
    """
    Extract a payload block delimited by either:
    - lines containing exactly "<!-- fdd-id-content -->" (preferred)
    - legacy lines containing exactly "---" (migration support)

    The opening delimiter is expected at start_idx. The closing delimiter is the next
    line that equals the same delimiter (after start_idx).

    Returns:
        (open_idx, close_idx) where close_idx is the index of the closing delimiter.
        Returns None if the opening delimiter is not present at start_idx or if there
        is no closing delimiter.
    """
    if start_idx < 0 or start_idx >= len(lines):
        return None
    open_marker = lines[start_idx].strip()
    if open_marker not in {"<!-- fdd-id-content -->", "---"}:
        return None
    end = start_idx + 1
    while end < len(lines) and lines[end].strip() != open_marker:
        end += 1
    if end >= len(lines):
        return None
    return start_idx, end


def extract_id_payload_block(lines: List[str], *, id_idx: int) -> Optional[Dict[str, object]]:
    """
    Extract an ID payload block that appears immediately after an **ID** line.

    The payload block may be preceded by optional blank lines.

    Returns:
        Dict with:
        - open_idx: opening delimiter line index
        - close_idx: closing delimiter line index
        - text: payload text (without delimiters)
        Returns None if no payload block is present.
    """
    j = id_idx + 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    rng = extract_payload_block(lines, start_idx=j)
    if rng is None:
        return None
    open_idx, close_idx = rng
    payload_lines = lines[open_idx + 1 : close_idx]
    return {
        "open_idx": open_idx,
        "close_idx": close_idx,
        "text": "\n".join(payload_lines).rstrip("\n"),
    }


def find_anchor_idx_for_id(lines: List[str], needle: str) -> Optional[int]:
    """
    Find anchor index for ID in lines.
    
    Args:
        lines: Document lines
        needle: ID to find
    
    Returns:
        Anchor line index or None
    """
    # First try ID lines
    for idx, line in enumerate(lines):
        s = line.strip()
        if needle not in s:
            continue
        if "**ID**:" in s:
            return idx
    
    # Then try headings
    for idx, line in enumerate(lines):
        if needle in line and get_heading_level(line) is not None:
            return idx
    
    return find_id_line(lines, needle)


def extract_id_block(lines: List[str], *, anchor_idx: int, id_value: str, kind: str) -> Tuple[int, int]:
    """
    Extract block for ID.
    
    Args:
        lines: Document lines
        anchor_idx: Anchor line index
        id_value: ID value
        kind: Artifact kind
    
    Returns:
        Tuple of (start, end) indices
    """
    if kind == "feature-design":
        sections = get_feature_sections(lines)
        for letter, (sec_start, sec_end) in sections.items():
            if sec_start <= anchor_idx < sec_end:
                return extract_heading_block(lines, anchor_idx)
        return extract_heading_block(lines, anchor_idx)
    return extract_heading_block(lines, anchor_idx)


def prd_block_bounds(lines: List[str], *, section_start: int, section_end: int, id_idx: int) -> Optional[Tuple[int, int]]:
    """
    Get PRD block bounds.
    
    Args:
        lines: Document lines
        section_start: Section start index
        section_end: Section end index
        id_idx: ID line index
    
    Returns:
        Tuple of (start, end) or None
    """
    h = find_nearest_prev_heading(lines, idx=id_idx, start=section_start, prefix="#### ")
    if h is None:
        return None
    e = h + 1
    while e < section_end and not lines[e].strip().startswith("#### "):
        e += 1
    return h, e


def design_item_block_bounds(lines: List[str], *, start: int, end: int, id_idx: int) -> Tuple[int, int]:
    """
    Get design item block bounds.
    
    Args:
        lines: Document lines
        start: Start index
        end: End index
        id_idx: ID line index
    
    Returns:
        Tuple of (start, end) indices
    """
    def is_boundary(s: str) -> bool:
        stripped = s.strip()
        if stripped.startswith("#### "):
            return True
        if re.match(r"^\*\*[^*]+\*\*:\s*$", stripped):
            return True
        return False
    
    h = id_idx
    while h > start and not is_boundary(lines[h]):
        h -= 1
    e = id_idx + 1
    while e < end and not is_boundary(lines[e]):
        e += 1
    return h, e


__all__ = [
    "get_heading_level",
    "find_nearest_heading",
    "list_section_entries",
    "list_items",
    "read_feature_entry",
    "read_letter_section",
    "read_heading_block_by_title",
    "extract_heading_block",
    "extract_block",
    "get_section_indices",
    "get_feature_sections",
    "get_design_subsections",
    "find_nearest_prev_heading",
    "resolve_heading",
    "resolve_under_heading",
    "find_id_line",
    "find_anchor_idx_for_id",
    "extract_id_block",
    "extract_payload_block",
    "extract_id_payload_block",
    "prd_block_bounds",
    "design_item_block_bounds",
]
