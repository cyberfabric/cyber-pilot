"""
Spider Validator - Document Utilities

Functions for working with documents and file paths.
"""

from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple


_SPD_ID_RE = re.compile(r"(spd-[a-z0-9][a-z0-9-]+)")
_HEADING_RE = re.compile(r"^\s*(#{1,6})\s+(.+?)\s*$")
_CODE_FENCE_RE = re.compile(r"^\s*```")

_ID_DEF_RE = re.compile(
    r"^(?:"
    r"\*\*ID\*\*:\s*`(?P<id>spd-[a-z0-9][a-z0-9-]+)`"
    r"|"
    r"`(?P<priority_only>p\d+)`\s*-\s*\*\*ID\*\*:\s*`(?P<id2>spd-[a-z0-9][a-z0-9-]+)`"
    r"|"
    r"[-*]\s+(?P<task>\[\s*[xX]?\s*\])\s*(?:`(?P<priority>p\d+)`\s*-\s*)?\*\*ID\*\*:\s*`(?P<id3>spd-[a-z0-9][a-z0-9-]+)`"
    r")\s*$"
)
_ID_REF_RE = re.compile(
    r"^(?:(?P<task>\[\s*[xX]?\s*\])\s*(?:`(?P<priority>p\d+)`\s*-\s*|\-\s*)|`(?P<priority_only>p\d+)`\s*-\s*)?"
    r"`(?P<id>spd-[a-z0-9][a-z0-9-]+)`\s*$"
)
_BACKTICK_ID_RE = re.compile(r"`(spd-[a-z0-9][a-z0-9-]+)`")


def _normalize_spd_id_from_line(line: str) -> Optional[str]:
    stripped = line.strip()
    if not stripped:
        return None

    # Common decorations: backticks or "**ID**: `...`"
    if stripped.startswith("**ID**:"):
        matches = _SPD_ID_RE.findall(stripped)
        return matches[0] if matches else None

    if stripped.startswith("`") and stripped.endswith("`") and len(stripped) > 2:
        stripped = stripped.strip("`").strip()

    if stripped.startswith("spd-"):
        m = _SPD_ID_RE.fullmatch(stripped)
        return m.group(1) if m else None

    matches = _SPD_ID_RE.findall(stripped)
    return matches[0] if matches else None


def file_has_spider_markers(path: Path) -> bool:
    lines = read_text_safe(path)
    if lines is None:
        return False
    return any("<!--" in ln and "spd:" in ln for ln in lines)


def scan_spd_ids_without_markers(path: Path) -> List[Dict[str, object]]:
    """Scan a file for Spider IDs without relying on `<!-- spd:... -->` markers.

    Heuristics:
    - Only scans outside fenced code blocks (```...```).
    - Treats `**ID**: `...`` and task list `**ID**:` lines as *definitions*.
    - Treats lines like `` `spd-...` `` / checkbox variants as *references*.
    - Treats any `` `spd-...` `` occurrence as a *reference* (unless it was a definition line).
    """
    lines = read_text_safe(path)
    if lines is None:
        return []
    if any("<!--" in ln and "spd:" in ln for ln in lines):
        return []

    hits: List[Dict[str, object]] = []
    in_fence = False

    for idx0, raw in enumerate(lines):
        if _CODE_FENCE_RE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        stripped = raw.strip()
        if not stripped:
            continue

        m = _ID_DEF_RE.match(stripped)
        if m:
            checked = (m.group("task") or "").lower().find("x") != -1
            priority = m.group("priority") or m.group("priority_only")
            id_value = m.group("id") or m.group("id2") or m.group("id3")
            h: Dict[str, object] = {"id": id_value, "line": idx0 + 1, "type": "definition", "checked": checked}
            if priority:
                h["priority"] = priority
            hits.append(h)
            continue

        # Reference line format (optionally checkbox / priority).
        stripped_ref = stripped
        if stripped_ref.startswith("- "):
            stripped_ref = stripped_ref[2:].strip()
        elif stripped_ref.startswith("* "):
            stripped_ref = stripped_ref[2:].strip()
        mref = _ID_REF_RE.match(stripped_ref)
        if mref:
            checked = (mref.group("task") or "").lower().find("x") != -1
            priority = mref.group("priority") or mref.group("priority_only")
            h = {"id": mref.group("id"), "line": idx0 + 1, "type": "reference", "checked": checked}
            if priority:
                h["priority"] = priority
            hits.append(h)
            continue

        # Generic inline backticked references.
        for mm in _BACKTICK_ID_RE.finditer(raw):
            hits.append({"id": mm.group(1), "line": idx0 + 1, "type": "reference", "checked": False})

    return hits


def get_content_scoped_without_markers(path: Path, *, id_value: str) -> Optional[Tuple[str, int, int]]:
    """Best-effort get-content fallback for artifacts with no `<!-- spd:... -->` markers.

    Supported formats:
      1) Hash-fence scope blocks:
         ##
         spd-...
         content...
         ##

         Variant where IDs act as delimiters inside the same fence:
         ##
         spd-a
         content A
         spd-b
         content B
         ##

      2) Markdown heading scopes:
         ### spd-...
         content...

    Returns:
        (text, start_line, end_line) with 1-based inclusive line numbers, or None.
    """
    lines = read_text_safe(path)
    if lines is None:
        return None

    # Only apply fallback when the file truly has no Spider markers.
    if any("<!--" in ln and "spd:" in ln for ln in lines):
        return None

    wanted = id_value.strip()

    def emit(text_lines: List[str], start_idx: int, end_idx: int) -> Optional[Tuple[str, int, int]]:
        # Trim surrounding empties for a stable output payload.
        while text_lines and not text_lines[0].strip():
            text_lines = text_lines[1:]
            start_idx += 1
        while text_lines and not text_lines[-1].strip():
            text_lines = text_lines[:-1]
            end_idx -= 1
        text = "\n".join(text_lines).strip()
        if text == "":
            return None
        return (text, start_idx + 1, end_idx + 1)

    # (1) Hash-fence blocks first: "##" or "###" line alone.
    fence_idxs = [i for i, ln in enumerate(lines) if ln.strip() in {"##", "###"}]
    for start_i, end_i in zip(fence_idxs[0::2], fence_idxs[1::2]):
        if end_i <= start_i + 1:
            continue
        inner = lines[start_i + 1 : end_i]
        # Split inner into segments by Spider ID lines.
        boundaries: List[Tuple[int, str]] = []
        for rel_idx, ln in enumerate(inner):
            sid = _normalize_spd_id_from_line(ln)
            if sid:
                boundaries.append((rel_idx, sid))
        if not boundaries:
            continue

        for bi, (b_rel, sid) in enumerate(boundaries):
            if sid != wanted:
                continue
            seg_start = start_i + 1 + b_rel + 1
            seg_end = end_i - 1
            if bi + 1 < len(boundaries):
                next_rel, _ = boundaries[bi + 1]
                seg_end = start_i + 1 + next_rel - 1
            if seg_start > seg_end:
                return None
            return emit(lines[seg_start : seg_end + 1], seg_start, seg_end)

    # (2) Heading scopes: return content until next heading of <= level.
    for idx, ln in enumerate(lines):
        m = _HEADING_RE.match(ln)
        if not m:
            continue
        level = len(m.group(1))
        title = m.group(2)
        matches = _SPD_ID_RE.findall(title)
        if wanted not in matches and wanted != title.strip() and wanted != title.strip("`").strip():
            continue

        start = idx + 1
        end = len(lines) - 1
        for j in range(idx + 1, len(lines)):
            m2 = _HEADING_RE.match(lines[j])
            if not m2:
                continue
            if len(m2.group(1)) <= level:
                end = j - 1
                break
        if start > end:
            return None
        return emit(lines[start : end + 1], start, end)

    # (3) ID-definition scoped by nearest heading: support common pattern
    #     #### Human Title
    #     **ID**: `spd-...`
    #     content...
    #     #### Next Title
    #
    # Extract from the line after the matching ID definition until the next heading
    # at the same-or-higher level as the nearest preceding heading (or any heading if none).
    in_fence = False
    last_heading_level: Optional[int] = None

    for idx, ln in enumerate(lines):
        if _CODE_FENCE_RE.match(ln):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        mh = _HEADING_RE.match(ln)
        if mh:
            last_heading_level = len(mh.group(1))
            continue

        mdef = _ID_DEF_RE.match(ln.strip())
        if not mdef:
            continue
        id_found = mdef.group("id") or mdef.group("id2") or mdef.group("id3")
        if id_found != wanted:
            continue

        start = idx + 1
        end = len(lines) - 1

        # If we have a preceding heading, stop at the next heading with level <= that.
        # Otherwise, stop at the next heading (any level).
        cutoff_level = last_heading_level if last_heading_level is not None else 6
        in_fence2 = False
        for j in range(idx + 1, len(lines)):
            if _CODE_FENCE_RE.match(lines[j]):
                in_fence2 = not in_fence2
                continue
            if in_fence2:
                continue
            # Stop at the next ID definition (acts as a delimiter within the same section).
            mnext = _ID_DEF_RE.match(lines[j].strip())
            if mnext:
                end = j - 1
                break
            m2 = _HEADING_RE.match(lines[j])
            if not m2:
                continue
            if len(m2.group(1)) <= cutoff_level:
                end = j - 1
                break

        if start > end:
            return None
        return emit(lines[start : end + 1], start, end)

    return None


def iter_text_files(
    root: Path,
    *,
    includes: Optional[List[str]] = None,
    excludes: Optional[List[str]] = None,
    max_bytes: int = 1_000_000,
) -> List[Path]:
    """
    Iterate over text files in directory.
    
    Args:
        root: Root directory to search
        includes: Glob patterns to include
        excludes: Glob patterns to exclude
        max_bytes: Maximum file size in bytes
    
    Returns:
        List of file paths
    """
    import os
    import fnmatch
    
    if excludes is None:
        excludes = []
    
    skip_dirs = {
        ".git", ".hg", ".svn", ".idea", ".vscode", "__pycache__",
        ".pytest_cache", ".mypy_cache", ".ruff_cache",
        "node_modules", "target", "dist", "build", ".venv", "venv",
    }
    
    out: List[Path] = []
    root = root.resolve()
    
    for dirpath, dirnames, filenames in os.walk(root):
        # Filter out skip directories
        dirnames[:] = sorted([d for d in dirnames if d not in skip_dirs and not d.startswith(".")])
        
        for fn in sorted(filenames):
            fp = Path(dirpath) / fn
            
            # Get relative path for pattern matching
            try:
                rel = fp.relative_to(root).as_posix()
            except ValueError:
                continue
            
            # Check excludes
            if excludes and any(fnmatch.fnmatch(rel, ex) for ex in excludes):
                continue
            
            # Check includes (when provided)
            if includes is not None and not any(fnmatch.fnmatch(rel, inc) for inc in includes):
                continue
            
            # Check file size
            try:
                st = fp.stat()
                if st.st_size > max_bytes:
                    continue
            except OSError:
                continue
            
            out.append(fp)
    
    return out


def read_text_safe(path: Path) -> Optional[List[str]]:
    """
    Safely read text file to lines.
    
    Args:
        path: File path to read
    
    Returns:
        List of lines or None if error
    """
    import os

    try:
        raw = path.read_bytes()
    except OSError:
        return None

    if b"\x00" in raw:
        return None

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("utf-8", errors="ignore")

    if os.linesep != "\n":
        text = text.replace("\r\n", "\n")

    return text.splitlines()


def to_relative_posix(path: Path, root: Path) -> str:
    """
    Convert path to relative POSIX string from root.
    
    Args:
        path: Path to convert
        root: Root path
    
    Returns:
        Relative POSIX path string
    """
    try:
        rel = path.resolve().relative_to(root.resolve())
    except Exception:
        return path.as_posix()
    return rel.as_posix()


__all__ = [
    "iter_text_files",
    "read_text_safe",
    "to_relative_posix",
    "get_content_scoped_without_markers",
    "scan_spd_ids_without_markers",
    "file_has_spider_markers",
]
