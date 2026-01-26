"""
FDD Validator - Search and Filter Utilities

Functions for searching, filtering, and extracting IDs from text and documents.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def extract_ids(lines: List[str], *, with_cols: bool = False) -> List[Dict[str, object]]:
    """
    Extract FDD and ADR IDs from lines.
    
    Args:
        lines: Text lines to search
        with_cols: If True, include column positions in results
    
    Returns:
        List of dicts with 'id', 'line', 'kind', and optionally 'col'
    """
    out: List[Dict[str, object]] = []
    fdd_re = re.compile(r"\b(fdd-[a-z0-9][a-z0-9-]+)\b")
    adr_re = re.compile(r"\b(ADR-\d{4})\b")

    for i, line in enumerate(lines, start=1):
        for m in fdd_re.finditer(line):
            hit = {"id": m.group(1), "line": i, "kind": "fdd"}
            if with_cols:
                hit["col"] = m.start(1) + 1
            out.append(hit)
        for m in adr_re.finditer(line):
            hit = {"id": m.group(1), "line": i, "kind": "adr"}
            if with_cols:
                hit["col"] = m.start(1) + 1
            out.append(hit)
    return out


def filter_hits(hits: List[Dict[str, object]], *, pattern: Optional[str], regex: bool) -> List[Dict[str, object]]:
    """
    Filter ID hits by pattern.
    
    Args:
        hits: List of ID hits to filter
        pattern: Pattern to match (substring or regex)
        regex: If True, treat pattern as regex
    
    Returns:
        Filtered list of hits
    """
    if not pattern:
        return hits
    if regex:
        r = re.compile(pattern)
        return [h for h in hits if r.search(str(h.get("id", "")))]
    return [h for h in hits if pattern in str(h.get("id", ""))]


def unique_hits(hits: List[Dict[str, object]]) -> List[Dict[str, object]]:
    """
    Remove duplicate IDs from hits, keeping first occurrence.
    
    Args:
        hits: List of ID hits
    
    Returns:
        List with unique IDs only
    """
    seen: set = set()
    out: List[Dict[str, object]] = []
    for h in hits:
        id_val = str(h.get("id", ""))
        if id_val not in seen:
            seen.add(id_val)
            out.append(h)
    return out


def find_all_positions(line: str, needle: str) -> List[int]:
    """
    Find all positions of substring in line.
    
    Args:
        line: Line to search
        needle: Substring to find
    
    Returns:
        List of character positions where needle occurs
    """
    out: List[int] = []
    start = 0
    while True:
        pos = line.find(needle, start)
        if pos == -1:
            break
        out.append(pos)
        start = pos + 1
    return out


def parse_trace_query(raw: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Parse FDD trace query into base, phase, and instruction.
    
    Args:
        raw: Query string like "@fdd-proj-flow-x:ph-1:inst-2"
    
    Returns:
        Tuple of (base, phase, instruction)
    """
    s = str(raw).strip()
    if s.startswith("@"):
        s = s[1:]

    if s.startswith("fdd-") and ":" in s:
        head, rest = s.split(":", 1)
        if not (rest.startswith("ph-") or rest.startswith("inst-")):
            _ = head
            s = rest

    base = s
    phase: Optional[str] = None
    inst: Optional[str] = None

    if ":" in s:
        segs = s.split(":")
        base = segs[0]
        for seg in segs[1:]:
            if seg.startswith("ph-") and phase is None:
                phase = seg
                continue
            if seg.startswith("inst-") and inst is None:
                inst = seg
                continue

    return base, phase, inst


def compile_trace_regex(base: str, phase: Optional[str], inst: Optional[str]) -> re.Pattern:
    """
    Compile regex pattern for trace matching.
    
    Args:
        base: Base FDD ID
        phase: Phase identifier
        inst: Instruction identifier
    
    Returns:
        Compiled regex pattern
    """
    pat = re.escape(base)
    if phase:
        ph_pat = rf"(?:\b{re.escape(phase)}\b|`{re.escape(phase)}`|:{re.escape(phase)}\b)"
        pat += r".*" + ph_pat
    if inst:
        inst_pat = rf"(?:\b{re.escape(inst)}\b|`{re.escape(inst)}`|:{re.escape(inst)}\b)"
        pat += r".*" + inst_pat
    return re.compile(pat)


def _token_index(line: str, token: str) -> int:
    candidates = [token, f"`{token}`", f":{token}"]
    best = -1
    for c in candidates:
        j = line.find(c)
        if j >= 0 and (best < 0 or j < best):
            best = j
    return best


def _match_phase_inst_in_line(line: str, *, phase: Optional[str], inst: Optional[str]) -> Optional[Tuple[str, int]]:
    if phase is None and inst is None:
        return None
    if phase is not None:
        ph_i = _token_index(line, phase)
        if ph_i < 0:
            return None
    else:
        ph_i = -1

    if inst is not None:
        inst_i = _token_index(line, inst)
        if inst_i < 0:
            return None
        if ph_i >= 0 and inst_i < ph_i:
            return None
        return "inst", inst_i

    return "phase", ph_i


def infer_fdd_type(id_value: str) -> str:
    """
    Infer FDD type from ID string.
    
    Args:
        id_value: FDD ID string
    
    Returns:
        Type string (actor, capability, usecase, etc.)
    """
    if "-actor-" in id_value:
        return "actor"
    if "-fr-" in id_value:
        return "functional-requirement"
    if "-capability-" in id_value:
        return "capability"
    if "-usecase-" in id_value:
        return "usecase"
    if "-principle-" in id_value:
        return "principle"
    if "-nfr-" in id_value:
        return "nfr"
    if "-prd-context-" in id_value:
        return "prd-context"
    if "-constraint-" in id_value:
        return "constraint"
    if "-feature-" in id_value and "-flow-" in id_value:
        return "flow"
    if "-feature-" in id_value and "-algo-" in id_value:
        return "algo"
    if "-feature-" in id_value and "-state-" in id_value:
        return "state"
    if "-feature-" in id_value and "-context-" in id_value:
        return "feature-context"
    if "-feature-" in id_value and "-test-" in id_value:
        return "test"
    if "-feature-" in id_value and "-req-" in id_value:
        return "feature-requirement"
    if "-req-" in id_value:
        return "requirement"
    if "-adr-" in id_value:
        return "adr"
    return "id"


def iter_candidate_definition_files(root, *, needle: str) -> List[Path]:
    root_path = Path(root) if not isinstance(root, Path) else root

    kind = infer_fdd_type(needle)
    want_suffixes: List[str] = []
    if needle.startswith("ADR-"):
        want_suffixes = ["architecture/ADR/*.md", "architecture/ADR/*/*.md"]
    elif "-adr-" in needle:
        want_suffixes = ["architecture/ADR/*.md", "architecture/ADR/*/*.md"]
    elif kind in {"actor", "capability", "functional-requirement", "usecase", "prd-context"}:
        want_suffixes = ["architecture/PRD.md"]
    elif kind in {"requirement", "principle", "constraint"}:
        want_suffixes = ["architecture/DESIGN.md"]
    elif kind in {"nfr"}:
        want_suffixes = ["architecture/PRD.md", "architecture/DESIGN.md"]
    elif kind == "feature":
        want_suffixes = ["architecture/features/FEATURES.md"]
    elif kind in {"flow", "algo", "state", "test", "feature-requirement", "feature-context"} or "-td-" in needle:
        want_suffixes = ["architecture/features/feature-*/DESIGN.md"]
    else:
        want_suffixes = ["architecture/DESIGN.md", "architecture/PRD.md", "architecture/ADR/*.md", "architecture/ADR/*/*.md"]

    expanded: List[str] = []
    seen: set = set()
    for suf in want_suffixes:
        for pat in [suf, f"**/{suf}"]:
            if pat in seen:
                continue
            seen.add(pat)
            expanded.append(pat)
    want_suffixes = expanded

    from .document import iter_text_files, to_relative_posix

    root_path = root_path.resolve()
    files: List[Path] = []
    candidates = iter_text_files(root_path, includes=want_suffixes)
    for p in candidates:
        rel = to_relative_posix(p, root_path)
        if rel.endswith(".md"):
            files.append(p)
    return sorted(set(files), key=lambda pp: to_relative_posix(pp, root_path))


def definition_hits_in_file(*, path: Path, root: Path, needle: str, include_tags: bool) -> List[Dict[str, object]]:
    from .document import read_text_safe, to_relative_posix
    from .markdown import get_section_indices, get_design_subsections, prd_block_bounds, design_item_block_bounds
    from .. import constants

    lines = read_text_safe(path)
    if lines is None:
        return []
    rel = to_relative_posix(path, root)
    hits: List[Dict[str, object]] = []
    is_markdown = path.suffix.lower() == ".md"

    if needle.startswith("ADR-"):
        adr_heading_re = re.compile(rf"^#{{1,2}}\s+{re.escape(needle)}\s*:")
        for i, line in enumerate(lines, start=1):
            if adr_heading_re.match(line.strip()):
                hits.append({"path": rel, "line": i, "col": 1, "text": line, "match": "adr_heading"})
        return hits

    section_idx: Optional[Dict[str, Tuple[int, int]]] = None
    if is_markdown and rel.endswith("architecture/PRD.md"):
        section_idx = get_section_indices(lines, constants.SECTION_PRD_RE)
    if is_markdown and rel.endswith("architecture/DESIGN.md"):
        section_idx = get_section_indices(lines, re.compile(r"^##\s+([A-D])\.\s+(.+?)\s*$"))

    expected_prd_section: Optional[str] = None
    itype = infer_fdd_type(needle)
    if rel.endswith("architecture/PRD.md"):
        if itype == "actor":
            expected_prd_section = "B"
        elif itype == "capability" or itype == "functional-requirement":
            expected_prd_section = "C"
        elif itype == "usecase":
            expected_prd_section = "D"
        elif itype == "nfr":
            expected_prd_section = "E"
        elif itype == "prd-context":
            expected_prd_section = "F"

    expected_design_subsection: Optional[int] = None
    if rel.endswith("architecture/DESIGN.md"):
        if itype == "requirement":
            expected_design_subsection = 1
        elif itype == "nfr":
            expected_design_subsection = 2
        elif itype == "principle":
            expected_design_subsection = 3
        elif itype == "constraint":
            expected_design_subsection = 4

    for i, line in enumerate(lines, start=1):
        if needle not in line:
            continue
        if is_markdown and ("**ID**:" in line or (itype == "adr" and "**ADR ID**:" in line)):
            idx0 = i - 1
            if expected_prd_section is not None and section_idx is not None:
                rng = section_idx.get(expected_prd_section)
                if rng is None:
                    continue
                sec_s, sec_e = rng
                if not (sec_s <= idx0 < sec_e):
                    continue
                bnd = prd_block_bounds(lines, section_start=sec_s, section_end=sec_e, id_idx=idx0)
                if bnd is None:
                    continue
                bs, be = bnd
                if not (bs <= idx0 < be):
                    continue

            if rel.endswith("architecture/DESIGN.md") and section_idx is not None:
                b_rng = section_idx.get("B")
                if b_rng is None:
                    continue
                b_s, b_e = b_rng
                if not (b_s <= idx0 < b_e):
                    continue
                subs = get_design_subsections(lines, start=b_s, end=b_e)
                if expected_design_subsection is not None and expected_design_subsection in subs:
                    ss, se = subs[expected_design_subsection]
                    if not (ss <= idx0 < se):
                        continue
                ib_s, ib_e = design_item_block_bounds(lines, start=b_s, end=b_e, id_idx=idx0)
                if not (ib_s <= idx0 < ib_e):
                    continue

            for col0 in find_all_positions(line, needle) or [line.find(needle)]:
                if col0 >= 0:
                    hits.append({"path": rel, "line": i, "col": col0 + 1, "text": line, "match": "id_line"})
            continue

        if include_tags and "@fdd-" in line:
            for col0 in find_all_positions(line, needle) or [line.find(needle)]:
                if col0 >= 0:
                    hits.append({"path": rel, "line": i, "col": col0 + 1, "text": line, "match": "tag"})

    return hits


def where_defined_internal(
    *,
    root: Path,
    raw_id: str,
    include_tags: bool,
    includes: Optional[List[str]],
    excludes: Optional[List[str]],
    max_bytes: int,
) -> Tuple[str, List[Dict[str, object]], List[Dict[str, object]]]:
    from .document import iter_text_files, to_relative_posix, read_text_safe
    from .markdown import find_anchor_idx_for_id, extract_id_block

    base, phase, inst = parse_trace_query(raw_id)

    base_files = iter_candidate_definition_files(root, needle=base)
    files = base_files
    if include_tags:
        extra = iter_text_files(root, includes=includes, excludes=excludes, max_bytes=max_bytes)
        files = sorted(set(files + extra), key=lambda pp: to_relative_posix(pp, root))

    base_defs: List[Dict[str, object]] = []
    for fp in files:
        base_defs.extend(definition_hits_in_file(path=fp, root=root, needle=base, include_tags=bool(include_tags)))
    base_defs = sorted(base_defs, key=lambda h: (str(h.get("path", "")), int(h.get("line", 0)), int(h.get("col", 0))))

    if phase is None and inst is None:
        return base, base_defs, []

    seg_defs: List[Dict[str, object]] = []
    for d in base_defs:
        sp = str(d.get("path", ""))
        if "architecture/features/" not in sp or not sp.endswith("/DESIGN.md"):
            continue
        p = root / sp
        lines = read_text_safe(p)
        if lines is None:
            continue
        anchor0 = find_anchor_idx_for_id(lines, base)
        if anchor0 is None:
            continue
        start, end = extract_id_block(lines, anchor_idx=anchor0, id_value=base, kind="feature-design")
        for i in range(start, end):
            line = lines[i]
            matched = _match_phase_inst_in_line(line, phase=phase, inst=inst)
            if matched is None:
                continue
            seg, col0 = matched
            seg_defs.append(
                {
                    "path": sp,
                    "line": i + 1,
                    "col": col0 + 1,
                    "text": line,
                    "match": f"fdl_{seg}",
                    "segment": seg,
                }
            )

    seg_defs = sorted(seg_defs, key=lambda h: (str(h.get("path", "")), int(h.get("line", 0)), int(h.get("col", 0))))
    return base, seg_defs, base_defs


def where_defined(root, id_value: str) -> List[Dict[str, object]]:
    base, defs, _ctx = where_defined_internal(
        root=Path(root),
        raw_id=id_value,
        include_tags=False,
        includes=None,
        excludes=None,
        max_bytes=1_000_000,
    )
    _ = base
    return defs


def scan_ids(
    *,
    root: Path,
    pattern: Optional[str],
    regex: bool,
    kind: str,
    include: Optional[List[str]],
    exclude: Optional[List[str]],
    max_bytes: int,
    all_ids: bool,
) -> List[Dict[str, object]]:
    from .document import iter_text_files, read_text_safe, to_relative_posix

    root = root.resolve()
    scan_root = root if root.is_dir() else root.parent
    files = [root] if root.is_file() else iter_text_files(root, includes=include, excludes=exclude, max_bytes=int(max_bytes))

    rx: Optional[re.Pattern] = None
    if pattern and regex:
        pat = str(pattern)
        if "\\\\" in pat:
            pat = pat.replace("\\\\", "\\")
        rx = re.compile(pat)

    hits: List[Dict[str, object]] = []
    for fp in files:
        lines = read_text_safe(fp)
        if lines is None:
            continue
        for h in extract_ids(lines, with_cols=True):
            if kind != "all" and str(h.get("kind")) != str(kind):
                continue
            sid = str(h.get("id", ""))
            if pattern:
                if rx is not None:
                    if rx.search(sid) is None:
                        continue
                else:
                    if str(pattern) not in sid:
                        continue
            hit = {
                "id": sid,
                "kind": str(h.get("kind")),
                "path": to_relative_posix(fp, scan_root),
                "line": int(h.get("line", 0)),
                "col": int(h.get("col", 0)),
            }
            hits.append(hit)

    hits = sorted(hits, key=lambda h: (str(h.get("id", "")), str(h.get("path", "")), int(h.get("line", 0)), int(h.get("col", 0))))
    if not all_ids:
        seen: set = set()
        uniq: List[Dict[str, object]] = []
        for h in hits:
            k = (str(h.get("id", "")), str(h.get("path", "")))
            if k in seen:
                continue
            seen.add(k)
            uniq.append(h)
        hits = uniq

    return hits


def where_used(
    *,
    root: Path,
    raw_id: str,
    include: Optional[List[str]],
    exclude: Optional[List[str]],
    max_bytes: int,
) -> Tuple[str, Optional[str], Optional[str], List[Dict[str, object]]]:
    from .document import iter_text_files, read_text_safe, to_relative_posix

    raw_id = str(raw_id).strip()
    base, phase, inst = parse_trace_query(raw_id)
    root = root.resolve()
    files = iter_text_files(root, includes=include, excludes=exclude, max_bytes=int(max_bytes))

    _, defs, _ctx = where_defined_internal(
        root=root,
        raw_id=raw_id,
        include_tags=False,
        includes=include,
        excludes=exclude,
        max_bytes=int(max_bytes),
    )
    def_keys = {(str(d.get("path", "")), int(d.get("line", 0)), int(d.get("col", 0))) for d in defs}
    trace_pat = compile_trace_regex(base, phase, inst)

    hits: List[Dict[str, object]] = []
    for fp in files:
        lines = read_text_safe(fp)
        if lines is None:
            continue
        for i, line in enumerate(lines, start=1):
            if trace_pat.search(line) is None:
                continue
            cols = find_all_positions(line, base)
            for col0 in cols:
                h = {
                    "path": to_relative_posix(fp, root),
                    "line": i,
                    "col": col0 + 1,
                    "text": line,
                }
                k = (str(h.get("path")), int(h.get("line")), int(h.get("col")))
                if k in def_keys:
                    continue
                hits.append(h)

    hits = sorted(hits, key=lambda h: (str(h.get("path", "")), int(h.get("line", 0)), int(h.get("col", 0))))
    return base, phase, inst, hits


def search_lines(*, lines: List[str], query: str, regex: bool) -> List[Dict[str, object]]:
    hits: List[Dict[str, object]] = []
    if regex:
        pat = re.compile(query)
        for i, line in enumerate(lines, start=1):
            if pat.search(line):
                hits.append({"line": i, "text": line})
    else:
        q = query
        for i, line in enumerate(lines, start=1):
            if q in line:
                hits.append({"line": i, "text": line})
    return hits


def list_ids(
    *,
    lines: List[str],
    base_offset: int,
    pattern: Optional[str],
    regex: bool,
    all_ids: bool,
) -> List[Dict[str, object]]:
    hits = extract_ids(lines)
    for h in hits:
        h["line"] = int(h.get("line", 0)) + int(base_offset)
    hits = filter_hits(hits, pattern=pattern, regex=bool(regex))
    if not all_ids:
        hits = unique_hits(hits)
    hits = sorted(hits, key=lambda h: (str(h.get("id", "")), int(h.get("line", 0))))
    return hits


__all__ = [
    "extract_ids",
    "filter_hits",
    "unique_hits",
    "find_all_positions",
    "parse_trace_query",
    "compile_trace_regex",
    "infer_fdd_type",
    "iter_candidate_definition_files",
    "definition_hits_in_file",
    "where_defined_internal",
    "where_defined",
    "scan_ids",
    "where_used",
    "search_lines",
    "list_ids",
]
