"""
Cypilot Validator - Markdown Parsing Utilities

Functions for parsing markdown structure, extracting sections, and analyzing content.

@cpt-algo:cpt-cypilot-algo-traceability-validation-scan-ids:p1
@cpt-algo:cpt-cypilot-algo-traceability-validation-validate-structure:p1
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..constants import (
    SECTION_RE,
    HEADING_ID_RE,
    FIELD_HEADER_RE,
)


# @cpt-begin:cpt-cypilot-algo-traceability-validation-parsing-utils:p1:inst-parse-required-sections
def parse_required_sections(requirements_path: Path) -> Dict[str, str]:
    """
    Parse required sections from requirements file.
    
    Returns dict mapping section ID to section title.
    """
    sections: Dict[str, str] = {}
    for line in requirements_path.read_text(encoding="utf-8").splitlines():
        m = SECTION_RE.match(line)
        if not m:
            continue
        section_id = m.group(1)
        section_title = m.group(2)
        sections[section_id] = section_title
    return sections
# @cpt-end:cpt-cypilot-algo-traceability-validation-parsing-utils:p1:inst-parse-required-sections


# @cpt-begin:cpt-cypilot-algo-traceability-validation-parsing-utils:p1:inst-parse-find-sections
def find_present_section_ids(artifact_text: str) -> List[str]:
    """
    Find section letter IDs present in artifact (e.g., A, B, C).
    
    Looks for headings like "# A. Introduction"
    """
    present = []
    for line in artifact_text.splitlines():
        m = HEADING_ID_RE.match(line)
        if m:
            present.append(m.group(1))
    return present
# @cpt-end:cpt-cypilot-algo-traceability-validation-parsing-utils:p1:inst-parse-find-sections


# @cpt-begin:cpt-cypilot-algo-traceability-validation-parsing-utils:p1:inst-parse-split-sections
def split_by_section_letter(text: str, section_re: re.Pattern) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Split text by lettered sections using provided regex pattern.
    
    Args:
        text: Text to split
        section_re: Compiled regex pattern to match section headers
    
    Returns:
        Tuple of (section_order, section_dict)
        - section_order: List of section letters in order found
        - section_dict: Dict mapping section letter to list of lines in that section
    """
    lines = text.splitlines()
    found_order: List[str] = []
    sections: Dict[str, List[str]] = {}
    current: Optional[str] = None
    for line in lines:
        m = section_re.match(line.strip())
        if m:
            current = m.group(1).upper()
            if current not in sections:
                found_order.append(current)
                sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return found_order, sections


def split_by_section_letter_with_offsets(
    text: str, section_re: re.Pattern
) -> Tuple[List[str], Dict[str, List[str]], Dict[str, int]]:
    lines = text.splitlines()
    found_order: List[str] = []
    sections: Dict[str, List[str]] = {}
    offsets: Dict[str, int] = {}

    current: Optional[str] = None
    for idx, line in enumerate(lines, start=1):
        m = section_re.match(line.strip())
        if m:
            current = m.group(1).upper()
            if current not in sections:
                found_order.append(current)
                sections[current] = []
                offsets[current] = idx + 1
            continue
        if current is not None:
            sections[current].append(line)

    return found_order, sections, offsets
# @cpt-end:cpt-cypilot-algo-traceability-validation-parsing-utils:p1:inst-parse-split-sections


def _is_field_header_terminator(line: str) -> bool:
    """Check if line should terminate a field block.
    
    Field headers come in two styles:
    1. Non-list: **Field Name**: value
    2. List-style: - **Field Name**: value (used in DECOMPOSITION.md)
    
    Content with bold is NOT a field header:
    - **Bold Title**: prose explanation (like in PRD problem lists)
    
    Heuristic: List-style is a field header if value is short/empty/None.
    Prose explanations after bold are content, not field headers.
    """
    m = FIELD_HEADER_RE.match(line)
    if not m:
        return False
    
    stripped = line.lstrip()
    value = m.group(2).strip()
    
    # Non-list style (e.g., "**Status**: value") - always a field header
    if not stripped.startswith(("- **", "* **")):
        return True
    
    # List-style: check if value looks like field content vs prose
    # Field headers have: empty, "None", or start with backtick/link
    if not value or value == "None" or value.startswith("`") or value.startswith("["):
        return True
    
    # If value is long prose (>40 chars), it's likely content not a field header
    if len(value) > 40:
        return False
    
    # Short values in list-style are treated as field headers
    return True


# @cpt-begin:cpt-cypilot-algo-traceability-validation-parsing-utils:p1:inst-parse-field-block
def field_block(lines: List[str], field_name: str) -> Optional[Dict[str, object]]:
    """
    Extract field block from list of lines.
    
    Looks for field header like "**Field Name**: value" and extracts
    value plus all following lines until next field header.
    
    Returns dict with {index, value, tail} or None if not found.
    """
    for idx, line in enumerate(lines):
        m = FIELD_HEADER_RE.match(line)
        if not m:
            continue
        if m.group(1).strip() != field_name:
            continue
        value = m.group(2)
        tail: List[str] = []
        for j in range(idx + 1, len(lines)):
            if _is_field_header_terminator(lines[j]):
                break
            tail.append(lines[j])
        return {"index": idx, "value": value, "tail": tail}
    return None
# @cpt-end:cpt-cypilot-algo-traceability-validation-parsing-utils:p1:inst-parse-field-block


def has_list_item(lines: List[str]) -> bool:
    """Check if any line in list is a markdown list item (starts with - or *)."""
    return any(re.match(r"^\s*[-*]\s+\S+", l) for l in lines)


# @cpt-begin:cpt-cypilot-algo-traceability-validation-parsing-utils:p1:inst-parse-extract-ids
def extract_backticked_ids(line: str, pattern: re.Pattern) -> List[str]:
    """
    Extract IDs from backticked tokens that match pattern.
    
    Example: "`cpt-system-feature-x-flow-y`" -> ["cpt-system-feature-x-flow-y"]
    """
    ids: List[str] = []
    for tok in re.findall(r"`([^`]+)`", line):
        if pattern.fullmatch(tok.strip()):
            ids.append(tok.strip())
    return ids
# @cpt-end:cpt-cypilot-algo-traceability-validation-parsing-utils:p1:inst-parse-extract-ids
