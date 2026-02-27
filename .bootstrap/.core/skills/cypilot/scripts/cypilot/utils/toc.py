"""
Unified TOC (Table of Contents) generation for Markdown files.

Used by:
- ``cypilot toc`` CLI command (file-level TOC with HTML markers)
- Blueprint artifact generator (content-level TOC with heading-based insertion)

Features:
- GitHub-compatible anchor slugs (handles links, backticks, bold/italic, duplicates)
- Fenced code block awareness (backtick and tilde fences, including 4+ char fences)
- Two insertion modes: HTML markers (``<!-- toc -->``) and heading-based (``## Table of Contents``)
- Two list styles: numbered top-level (for generated docs) and all-bullet (for user files)
- Configurable heading level range and indent size
- Auto-skip of document title (first H1) and existing TOC headings

@cpt-algo:cpt-cypilot-algo-traceability-validation-toc-utils:p1
@cpt-flow:cpt-cypilot-flow-developer-experience-self-check:p1
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_FENCE_RE = re.compile(r"^(`{3,}|~{3,})")

TOC_MARKER_START = "<!-- toc -->"
TOC_MARKER_END = "<!-- /toc -->"

_TOC_HEADING_NAMES = frozenset({"table of contents", "toc"})


# ---------------------------------------------------------------------------
# Anchor / slug
# ---------------------------------------------------------------------------

def github_anchor(text: str) -> str:
    """Convert heading text to a GitHub-compatible anchor slug.

    Matches GitHub's rendering rules:
    - Strip markdown links ``[text](url)`` → keep text
    - Remove inline formatting (bold, italic, code backticks, strikethrough)
    - Lowercase
    - Keep word chars (unicode), spaces, hyphens
    - Spaces → hyphens, collapse consecutive hyphens
    """
    text = text.strip().lower()
    # Remove markdown links but keep link text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Remove formatting markers: **, __, *, _, `, ~
    text = re.sub(r"\*\*|__|[*_`~]", "", text)
    # Keep only word chars, spaces, hyphens
    text = re.sub(r"[^\w\s\-]", "", text)
    # Spaces → hyphens
    text = re.sub(r"\s+", "-", text)
    # Collapse consecutive hyphens
    text = re.sub(r"-{2,}", "-", text)
    return text.strip("-")


# ---------------------------------------------------------------------------
# Heading parsing
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-traceability-validation-toc-utils:p1:inst-toc-util-parse-headings
def parse_headings(
    lines: List[str],
    *,
    min_level: int = 1,
    max_level: int = 6,
    skip_first: bool = False,
    skip_toc_heading: bool = False,
) -> List[Tuple[int, str]]:
    """Extract ``(level, text)`` pairs from markdown lines.

    Args:
        lines: Raw lines of the markdown file (no trailing newlines).
        min_level: Minimum heading level to include.
        max_level: Maximum heading level to include.
        skip_first: If True, skip the very first heading (document title).
        skip_toc_heading: If True, skip headings named "Table of Contents" or "TOC".
    """
    headings: List[Tuple[int, str]] = []
    in_fence = False
    first_skipped = False

    for line in lines:
        # Track fenced code blocks (``` or ~~~ with 3+ chars)
        if _FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        m = _HEADING_RE.match(line)
        if not m:
            continue

        level = len(m.group(1))
        text = m.group(2).strip()

        if skip_first and not first_skipped:
            first_skipped = True
            continue

        if level < min_level or level > max_level:
            continue

        if skip_toc_heading and text.lower() in _TOC_HEADING_NAMES:
            continue

        headings.append((level, text))

    return headings
# @cpt-end:cpt-cypilot-algo-traceability-validation-toc-utils:p1:inst-toc-util-parse-headings


# ---------------------------------------------------------------------------
# TOC building
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-traceability-validation-toc-utils:p1:inst-toc-util-build-toc
def build_toc(
    headings: List[Tuple[int, str]],
    *,
    indent_size: int = 2,
    numbered: bool = False,
) -> str:
    """Build a markdown TOC string from heading tuples.

    Args:
        headings: List of ``(level, text)`` tuples.
        indent_size: Spaces per nesting level.
        numbered: If True, top-level items are numbered (``1. 2. 3.``),
                  sub-items are bulleted. If False, all items are bulleted.

    Normalises indentation so the shallowest heading is at indent 0.
    Tracks duplicate slugs and appends ``-1``, ``-2``, etc. (GitHub style).
    """
    if not headings:
        return ""

    min_level = min(h[0] for h in headings)
    slug_counts: Dict[str, int] = {}
    toc_lines: List[str] = []

    def _display(raw: str) -> str:
        # Strip markdown links [text](url) → text so TOC entries
        # don't contain nested brackets that break anchor parsing.
        return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw)

    if numbered:
        # Parent-stack approach: numbered top-level, bulleted sub-items
        parent_stack: List[int] = []
        top_num = 0

        for level, text in headings:
            slug = _unique_slug(text, slug_counts)
            disp = _display(text)

            # Pop stack entries at same or higher level
            while parent_stack and parent_stack[-1] >= level:
                parent_stack.pop()

            depth = len(parent_stack)
            parent_stack.append(level)

            if depth == 0:
                top_num += 1
                toc_lines.append(f"{top_num}. [{disp}](#{slug})")
            else:
                indent = " " * indent_size * depth
                toc_lines.append(f"{indent}- [{disp}](#{slug})")
    else:
        # Flat bullet approach: all items bulleted
        for level, text in headings:
            slug = _unique_slug(text, slug_counts)
            disp = _display(text)
            indent = " " * indent_size * (level - min_level)
            toc_lines.append(f"{indent}- [{disp}](#{slug})")

    return "\n".join(toc_lines)
# @cpt-end:cpt-cypilot-algo-traceability-validation-toc-utils:p1:inst-toc-util-build-toc


def _unique_slug(text: str, slug_counts: Dict[str, int]) -> str:
    """Return a unique GitHub-compatible slug, tracking duplicates."""
    slug = github_anchor(text)
    if slug in slug_counts:
        slug_counts[slug] += 1
        return f"{slug}-{slug_counts[slug]}"
    else:
        slug_counts[slug] = 0
        return slug


# ---------------------------------------------------------------------------
# TOC insertion — marker-based (for CLI ``cypilot toc``)
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-traceability-validation-toc-utils:p1:inst-toc-util-insert-markers
def insert_toc_markers(
    content: str,
    *,
    max_level: int = 6,
    indent_size: int = 2,
) -> str:
    """Insert or update TOC between ``<!-- toc -->`` / ``<!-- /toc -->`` markers.

    If markers are absent, inserts them after the first H1 heading
    (or at position 0 if no H1 exists).

    Used by the ``cypilot toc`` CLI command for user-facing files.
    """
    lines = content.split("\n")
    headings = parse_headings(lines, min_level=2, max_level=max_level)

    if not headings:
        return content

    toc_text = build_toc(headings, indent_size=indent_size)

    # Find existing markers
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == TOC_MARKER_START and start_idx is None:
            start_idx = i
        elif stripped == TOC_MARKER_END and start_idx is not None:
            end_idx = i
            break

    if start_idx is not None and end_idx is not None:
        # Replace content between markers
        new_lines = lines[: start_idx + 1] + ["", toc_text, ""] + lines[end_idx:]
    else:
        # Insert after first H1, or at position 0
        insert_pos = 0
        in_fence = False
        for i, line in enumerate(lines):
            if _FENCE_RE.match(line.strip()):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = _HEADING_RE.match(line)
            if m and len(m.group(1)) == 1:
                insert_pos = i + 1
                # Skip blank lines immediately after H1
                while insert_pos < len(lines) and lines[insert_pos].strip() == "":
                    insert_pos += 1
                break

        toc_block = ["", TOC_MARKER_START, "", toc_text, "", TOC_MARKER_END, ""]
        new_lines = lines[:insert_pos] + toc_block + lines[insert_pos:]

    return "\n".join(new_lines)
# @cpt-end:cpt-cypilot-algo-traceability-validation-toc-utils:p1:inst-toc-util-insert-markers


# ---------------------------------------------------------------------------
# TOC insertion — heading-based (for blueprint-generated content)
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-traceability-validation-toc-utils:p1:inst-toc-util-insert-heading
def insert_toc_heading(
    content: str,
    *,
    max_heading_level: int = 2,
    indent_size: int = 3,
    numbered: bool = True,
) -> str:
    """Insert or replace a ``## Table of Contents`` section in markdown content.

    If an existing ``## Table of Contents`` heading is found, replaces the
    section up to the next heading or ``---`` separator.
    Otherwise inserts before the first ``---`` separator (after YAML
    frontmatter), or after the first heading + metadata block.

    Used by the blueprint artifact generator for generated docs
    (rules.md, checklist.md, example.md).
    """
    lines = content.split("\n")
    headings = parse_headings(
        lines,
        skip_first=True,
        skip_toc_heading=True,
        max_level=max_heading_level,
    )

    if not headings:
        return content

    toc_body = build_toc(headings, indent_size=indent_size, numbered=numbered)
    toc_section = f"## Table of Contents\n\n{toc_body}"

    # --- Try replacing an existing ToC section ---
    toc_start = toc_end = None
    for i, line in enumerate(lines):
        if re.match(r"^##\s+Table of Contents\s*$", line):
            toc_start = i
            # End = next heading or --- separator
            for j in range(i + 1, len(lines)):
                if re.match(r"^#{1,6}\s", lines[j]) or lines[j].strip() == "---":
                    toc_end = j
                    break
            else:
                toc_end = len(lines)
            break

    if toc_start is not None and toc_end is not None:
        # Strip blank lines around the replacement region
        while toc_start > 0 and lines[toc_start - 1].strip() == "":
            toc_start -= 1
        while toc_end < len(lines) and lines[toc_end].strip() == "":
            toc_end += 1
        before = "\n".join(lines[:toc_start])
        after = "\n".join(lines[toc_end:])
        return f"{before}\n\n{toc_section}\n\n{after}"

    # --- No existing ToC: insert before first non-frontmatter --- ---
    i = 0
    # Skip YAML frontmatter (starts and ends with ---)
    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        if i < len(lines):
            i += 1  # skip closing ---

    # Find the first --- separator (section break)
    for j in range(i, len(lines)):
        if lines[j].strip() == "---":
            before = "\n".join(lines[:j]).rstrip("\n")
            after = "\n".join(lines[j:])
            return f"{before}\n\n{toc_section}\n\n{after}"

    # No --- found: insert after first heading + metadata block
    for j in range(i, len(lines)):
        if re.match(r"^#{1,6}\s", lines[j]):
            k = j + 1
            while k < len(lines):
                s = lines[k].strip()
                if s.startswith("**") or s.startswith("- ") or s == "":
                    k += 1
                else:
                    break
            before = "\n".join(lines[:k]).rstrip("\n")
            after = "\n".join(lines[k:])
            return f"{before}\n\n{toc_section}\n\n{after}"

    # Fallback: prepend
    return f"{toc_section}\n\n{content}"
# @cpt-end:cpt-cypilot-algo-traceability-validation-toc-utils:p1:inst-toc-util-insert-heading


# ---------------------------------------------------------------------------
# File-level processing (for CLI command)
# ---------------------------------------------------------------------------

def _strip_manual_toc(content: str) -> Tuple[str, bool]:
    """Remove a standalone ``## Table of Contents`` section not inside markers.

    Returns ``(cleaned_content, was_removed)``.
    Detects manual TOC sections that duplicate the marker-based TOC.
    """
    lines = content.split("\n")

    # Check if markers already exist — only strip manual TOC if markers present
    # or will be inserted (i.e., always strip manual TOC for marker-based flow).
    toc_heading_start = None
    toc_heading_end = None
    in_fence = False

    for i, line in enumerate(lines):
        if _FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        # Skip lines inside <!-- toc --> markers — those are ours
        stripped = line.strip()
        if stripped == TOC_MARKER_START:
            # Fast-forward past marker block
            for j in range(i + 1, len(lines)):
                if lines[j].strip() == TOC_MARKER_END:
                    break
            continue

        if re.match(r"^##\s+Table of Contents\s*$", line):
            toc_heading_start = i
            # Find end: next heading or --- separator
            for j in range(i + 1, len(lines)):
                if re.match(r"^#{1,6}\s", lines[j]) or lines[j].strip() == "---":
                    toc_heading_end = j
                    break
            else:
                toc_heading_end = len(lines)
            break

    if toc_heading_start is None:
        return content, False

    # Strip blank lines around the section
    start = toc_heading_start
    end = toc_heading_end
    while start > 0 and lines[start - 1].strip() == "":
        start -= 1
    while end < len(lines) and lines[end].strip() == "":
        end += 1

    new_lines = lines[:start] + lines[end:]
    return "\n".join(new_lines), True


# @cpt-begin:cpt-cypilot-algo-traceability-validation-toc-utils:p1:inst-toc-util-process-file
def process_file(
    filepath: Path,
    *,
    max_level: int = 6,
    dry_run: bool = False,
    indent_size: int = 2,
) -> dict:
    """Generate/update TOC in a single markdown file using HTML markers.

    Detects and removes standalone ``## Table of Contents`` sections
    (manual TOCs) before inserting/updating the marker-based TOC.

    Returns a result dict with status info.
    """
    if not filepath.is_file():
        return {"file": str(filepath), "status": "ERROR", "message": "File not found"}

    content = filepath.read_text(encoding="utf-8")

    # Strip any manual ## Table of Contents section (duplicates marker-based TOC)
    content, manual_removed = _strip_manual_toc(content)

    new_content = insert_toc_markers(content, max_level=max_level, indent_size=indent_size)

    lines = content.split("\n")
    heading_count = len(parse_headings(lines, min_level=2, max_level=max_level))

    if heading_count == 0:
        return {"file": str(filepath), "status": "SKIP", "message": "No headings found"}

    # If only manual TOC was removed but markers unchanged, still write
    original = filepath.read_text(encoding="utf-8")
    if new_content == original:
        return {"file": str(filepath), "status": "UNCHANGED", "heading_count": heading_count}

    if not dry_run:
        filepath.write_text(new_content, encoding="utf-8")

    action = "WOULD_UPDATE" if dry_run else "UPDATED"
    result: dict = {"file": str(filepath), "status": action, "heading_count": heading_count}
    if manual_removed:
        result["manual_toc_removed"] = True
    return result
# @cpt-end:cpt-cypilot-algo-traceability-validation-toc-utils:p1:inst-toc-util-process-file


# ---------------------------------------------------------------------------
# TOC validation
# ---------------------------------------------------------------------------

# Regex to extract markdown links from TOC entries: ``[text](#anchor)``
_TOC_LINK_RE = re.compile(r"\[([^\]]+)\]\(#([^)]+)\)")


def _find_toc_section(
    lines: List[str],
) -> Optional[Tuple[int, int, str]]:
    """Locate the TOC section in a markdown file.

    Returns ``(start_line, end_line, mode)`` where mode is
    ``"heading"`` (``## Table of Contents``) or ``"markers"``
    (``<!-- toc -->`` / ``<!-- /toc -->``).  Returns ``None`` if no
    TOC section is found.

    Line indices are 0-based and inclusive/exclusive (``lines[start:end]``).
    """
    # Try heading-based first
    for i, line in enumerate(lines):
        if re.match(r"^##\s+Table of Contents\s*$", line):
            # Find end: next heading or --- separator
            for j in range(i + 1, len(lines)):
                if re.match(r"^#{1,6}\s", lines[j]) or lines[j].strip() == "---":
                    return (i, j, "heading")
            return (i, len(lines), "heading")

    # Try marker-based
    start_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == TOC_MARKER_START and start_idx is None:
            start_idx = i
        elif stripped == TOC_MARKER_END and start_idx is not None:
            return (start_idx, i + 1, "markers")

    return None


def _extract_toc_entries(
    lines: List[str],
    toc_start: int,
    toc_end: int,
) -> List[Tuple[str, str, int]]:
    """Extract ``(display_text, anchor, line_number)`` from TOC lines.

    ``line_number`` is 1-based for error reporting.
    """
    entries: List[Tuple[str, str, int]] = []
    for i in range(toc_start, toc_end):
        for display, anchor in _TOC_LINK_RE.findall(lines[i]):
            entries.append((display.strip(), anchor.strip(), i + 1))
    return entries


def _build_expected_anchors(
    headings: List[Tuple[int, str]],
) -> Dict[str, str]:
    """Build ``{anchor: heading_text}`` map with duplicate handling.

    Uses the same unique-slug logic as TOC generation so anchors match.
    """
    slug_counts: Dict[str, int] = {}
    result: Dict[str, str] = {}
    for _level, text in headings:
        slug = _unique_slug(text, slug_counts)
        result[slug] = text
    return result


# @cpt-begin:cpt-cypilot-algo-traceability-validation-toc-utils:p1:inst-toc-util-validate
def validate_toc(
    content: str,
    *,
    artifact_path: Optional[Path] = None,
    max_heading_level: int = 6,
) -> Dict[str, List[Dict[str, Any]]]:
    """Validate the Table of Contents in a markdown document.

    Checks performed:

    1. **TOC exists** — document has a ``## Table of Contents`` section or
       ``<!-- toc -->`` markers.
    2. **Anchors valid** — every ``[text](#anchor)`` in the TOC points to
       an actual heading in the document.
    3. **Completeness** — every heading (within level range, excluding title
       and TOC heading itself) is represented in the TOC.
    4. **Freshness** — if the TOC were regenerated, it would match the
       current content (catches reordering / renamed headings).

    Returns ``{"errors": [...], "warnings": [...]}`` in the same format
    as ``validate_artifact_file``.
    """
    from . import error_codes as EC
    from .constraints import error

    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    path = artifact_path or Path("<unknown>")
    lines = content.split("\n")

    # Headings relevant for TOC (skip title, skip TOC heading itself)
    headings = parse_headings(
        lines,
        skip_first=True,
        skip_toc_heading=True,
        max_level=max_heading_level,
    )

    if not headings:
        # No headings → nothing to validate
        return {"errors": errors, "warnings": warnings}

    # 1. TOC exists?
    toc_info = _find_toc_section(lines)
    if toc_info is None:
        errors.append(error(
            "toc",
            "Document has headings but no Table of Contents section",
            code=EC.TOC_MISSING,
            path=path,
            line=1,
            heading_count=len(headings),
        ))
        return {"errors": errors, "warnings": warnings}

    toc_start, toc_end, toc_mode = toc_info

    # 2. Extract TOC entries and expected anchors
    toc_entries = _extract_toc_entries(lines, toc_start, toc_end)
    expected_anchors = _build_expected_anchors(headings)

    # Set of anchors found in TOC
    toc_anchors: Dict[str, int] = {}  # anchor → line (1-based)
    for _display, anchor, line_num in toc_entries:
        toc_anchors[anchor] = line_num

    # 3. Every TOC anchor must point to a real heading
    for display, anchor, line_num in toc_entries:
        if anchor not in expected_anchors:
            errors.append(error(
                "toc",
                f"TOC entry `[{display}](#{anchor})` points to non-existent heading",
                code=EC.TOC_ANCHOR_BROKEN,
                path=path,
                line=line_num,
                toc_display=display,
                toc_anchor=anchor,
            ))

    # 4. Every heading must be in the TOC
    for anchor, heading_text in expected_anchors.items():
        if anchor not in toc_anchors:
            # Find the heading's line number
            heading_line = _find_heading_line(lines, heading_text)
            errors.append(error(
                "toc",
                f"Heading `{heading_text}` is not listed in the Table of Contents",
                code=EC.TOC_HEADING_NOT_IN_TOC,
                path=path,
                line=heading_line,
                heading_text=heading_text,
                expected_anchor=anchor,
            ))

    # 5. Staleness check — regenerate TOC and compare
    if not errors:
        if toc_mode == "heading":
            fresh = insert_toc_heading(content, max_heading_level=max_heading_level)
        else:
            fresh = insert_toc_markers(content, max_level=max_heading_level)

        if fresh != content:
            # Find the first differing line for a useful line number
            fresh_lines = fresh.split("\n")
            diff_line = 1
            for i in range(min(len(lines), len(fresh_lines))):
                if lines[i] != fresh_lines[i]:
                    diff_line = i + 1
                    break
            else:
                diff_line = min(len(lines), len(fresh_lines)) + 1

            warnings.append(error(
                "toc",
                "Table of Contents is outdated — regenerate with `cypilot toc`",
                code=EC.TOC_STALE,
                path=path,
                line=diff_line,
            ))

    return {"errors": errors, "warnings": warnings}
# @cpt-end:cpt-cypilot-algo-traceability-validation-toc-utils:p1:inst-toc-util-validate


def _find_heading_line(lines: List[str], heading_text: str) -> int:
    """Find the 1-based line number of a heading by its text."""
    for i, line in enumerate(lines):
        m = _HEADING_RE.match(line)
        if m and m.group(2).strip() == heading_text:
            return i + 1
    return 1
