"""Structural traceability graph for Cypilot codebase indexing.

Phase 1: Structural anchoring + content hashing
Phase 2: Incremental diff-aware index (future)
Phase 3: Traceability graph (future)
Phase 4: Real-time session sync (future)

@cpt-algo:cpt-cypilot-algo-smart-indexing-compute-anchor:p1
@cpt-algo:cpt-cypilot-algo-smart-indexing-compute-hash:p1
"""
from __future__ import annotations

import ast
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


_HEADING_RE = re.compile(r"^\s*(#{1,6})\s+(.+?)\s*$")
_CODE_FENCE_RE = re.compile(r"^\s*```")


# ---------------------------------------------------------------------------
# P1: Structural Anchoring
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StructuralAnchor:
    """Stable identity that survives line shifts.

    For docs: heading_path is a tuple of ancestor heading titles.
    For code: container is the enclosing class/function path.
    """
    heading_path: Tuple[str, ...] = ()
    container: Optional[str] = None
    content_hash: str = ""


@dataclass(frozen=True)
class AnchoredHit:
    """Enriched scan hit with structural anchor.

    Replaces the plain Dict[str, object] rows currently used in
    constraints.py cross_validate_artifacts() index building.
    """
    id: str
    type: str
    anchor: StructuralAnchor
    line: int
    checked: bool = False
    has_task: bool = False
    has_priority: bool = False
    priority: Optional[str] = None
    artifact_kind: str = ""
    artifact_path: Optional[Path] = None
    system: Optional[str] = None
    id_kind: Optional[str] = None

    def to_legacy_row(self) -> Dict[str, object]:
        """Bridge to existing flat-dict format for backward compatibility."""
        return {
            "id": self.id,
            "line": self.line,
            "checked": self.checked,
            "priority": self.priority,
            "has_task": self.has_task,
            "has_priority": self.has_priority,
            "artifact_kind": self.artifact_kind,
            "artifact_path": self.artifact_path,
            "system": self.system,
            "id_kind": self.id_kind,
            "headings": list(self.anchor.heading_path),
        }


# ---------------------------------------------------------------------------
# P1: Content Hashing
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-smart-indexing-compute-hash:p1:inst-compute-sha
def content_hash(text: str) -> str:
    """Compute SHA-256 hex digest of normalized text content."""
    normalized = "\n".join(line.rstrip() for line in text.splitlines())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
# @cpt-end:cpt-cypilot-algo-smart-indexing-compute-hash:p1:inst-compute-sha


# @cpt-begin:cpt-cypilot-algo-smart-indexing-compute-hash:p1:inst-extract-content
def hash_block_content(lines: Sequence[str]) -> str:
    """Hash the content of a @cpt-begin/@cpt-end block."""
    return content_hash("\n".join(lines))
# @cpt-end:cpt-cypilot-algo-smart-indexing-compute-hash:p1:inst-extract-content


# ---------------------------------------------------------------------------
# P1: Heading-Tree Anchor for Documents
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-smart-indexing-compute-anchor:p1:inst-build-heading-path
def compute_doc_anchors(lines: Sequence[str]) -> Dict[int, Tuple[str, ...]]:
    """Compute heading-tree path for each line in a markdown document.

    Returns a dict mapping 1-based line number to a tuple of ancestor
    heading titles.
    """
    result: Dict[int, Tuple[str, ...]] = {}
    stack: List[Tuple[int, str]] = []
    in_fence = False

    for idx, raw in enumerate(lines):
        line_no = idx + 1
        if _CODE_FENCE_RE.match(raw):
            in_fence = not in_fence
            result[line_no] = tuple(t for _, t in stack)
            continue
        if in_fence:
            result[line_no] = tuple(t for _, t in stack)
            continue

        hm = _HEADING_RE.match(raw)
        if hm:
            level = len(hm.group(1))
            title = hm.group(2).strip()
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))

        result[line_no] = tuple(t for _, t in stack)

    return result
# @cpt-end:cpt-cypilot-algo-smart-indexing-compute-anchor:p1:inst-build-heading-path


# ---------------------------------------------------------------------------
# P1: AST Container Anchor for Python Code
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-smart-indexing-compute-anchor:p1:inst-parse-ast
def compute_py_containers(source: str) -> Dict[int, str]:
    """Compute enclosing class/function path for each line in a Python file.

    Uses stdlib ast module. Returns a dict mapping 1-based line number
    to container path (e.g., "ClassName.method_name"). Lines at module
    level map to "".

    Falls back to empty dict on parse errors.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}

    containers: List[Tuple[int, int, str]] = []
    _collect_containers(tree, "", containers)
    containers.sort(key=lambda c: (-c[0], c[1]))

    total_lines = len(source.splitlines())
    result: Dict[int, str] = {}
    for line_no in range(1, total_lines + 1):
        for start, end, name in containers:
            if start <= line_no <= end:
                result[line_no] = name
                break
        else:
            result[line_no] = ""

    return result


def _collect_containers(
    node: ast.AST,
    prefix: str,
    out: List[Tuple[int, int, str]],
) -> None:
    """Recursively collect class/function containers from an AST."""
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = f"{prefix}.{child.name}" if prefix else child.name
            end_line = getattr(child, "end_lineno", child.lineno)
            out.append((child.lineno, end_line, name))
            _collect_containers(child, name, out)
        else:
            _collect_containers(child, prefix, out)
# @cpt-end:cpt-cypilot-algo-smart-indexing-compute-anchor:p1:inst-parse-ast


# @cpt-begin:cpt-cypilot-algo-smart-indexing-compute-anchor:p1:inst-regex-fallback
_FUNC_RE = re.compile(
    r"^\s*(?:(?:pub(?:\(crate\))?\s+)?(?:async\s+)?(?:fn|def|function|func)\s+(\w+)"
    r"|(?:class|struct|impl|interface|enum)\s+(\w+))",
)


def compute_code_containers_regex(lines: Sequence[str]) -> Dict[int, str]:
    """Fallback container detection for non-Python code files.

    Uses simple regex to detect def/function/class declarations.
    Less accurate than AST but language-agnostic.
    """
    result: Dict[int, str] = {}
    current_container = ""

    for idx, line in enumerate(lines):
        line_no = idx + 1
        m = _FUNC_RE.match(line)
        if m:
            current_container = m.group(1) or m.group(2) or ""
        result[line_no] = current_container

    return result
# @cpt-end:cpt-cypilot-algo-smart-indexing-compute-anchor:p1:inst-regex-fallback


# ---------------------------------------------------------------------------
# P1: Anchored Scan (combines scan_cpt_ids + heading anchors + content hash)
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-smart-indexing-compute-anchor:p1:inst-return-anchors
def build_doc_anchored_hits(
    path: Path,
    hits: Sequence[Dict[str, object]],
    headings_at: Sequence[Sequence[str]],
    *,
    lines: Optional[Sequence[str]] = None,
) -> List[AnchoredHit]:
    """Enrich scan_cpt_ids() output with structural anchors and content hashes.

    Args:
        path: Artifact file path.
        hits: Output from scan_cpt_ids(path).
        headings_at: Output from headings_by_line(path).
        lines: File lines (optional, read from path if not provided).
    """
    if lines is None:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            lines = []

    doc_anchors = compute_doc_anchors(lines)

    anchored: List[AnchoredHit] = []
    for h in hits:
        line = int(h.get("line", 1) or 1)
        heading_path = doc_anchors.get(line, ())
        section_text = _extract_section_text(lines, line)
        c_hash = content_hash(section_text) if section_text else ""

        anchor = StructuralAnchor(
            heading_path=heading_path,
            content_hash=c_hash,
        )
        anchored.append(AnchoredHit(
            id=str(h.get("id", "")),
            type=str(h.get("type", "reference")),
            anchor=anchor,
            line=line,
            checked=bool(h.get("checked", False)),
            has_task=bool(h.get("has_task", False)),
            has_priority=bool(h.get("has_priority", False)),
            priority=h.get("priority") if h.get("priority") else None,
        ))
    return anchored


def _extract_section_text(lines: Sequence[str], target_line: int) -> str:
    """Extract text of the section containing target_line."""
    if not lines:
        return ""

    section_start = 0
    section_level = 0
    for i in range(target_line - 1, -1, -1):
        hm = _HEADING_RE.match(lines[i])
        if hm:
            section_start = i
            section_level = len(hm.group(1))
            break

    section_end = len(lines)
    for i in range(section_start + 1, len(lines)):
        hm = _HEADING_RE.match(lines[i])
        if hm and len(hm.group(1)) <= section_level:
            section_end = i
            break

    return "\n".join(lines[section_start:section_end])
# @cpt-end:cpt-cypilot-algo-smart-indexing-compute-anchor:p1:inst-return-anchors


# ---------------------------------------------------------------------------
# P1: Code File Content Fingerprints
# ---------------------------------------------------------------------------

def compute_code_fingerprints(
    block_markers: Sequence,
) -> Dict[str, str]:
    """Compute content hash for each @cpt-begin/@cpt-end block.

    Returns dict mapping "{id}:{phase}:{inst}" to SHA-256 hex digest.
    """
    fingerprints: Dict[str, str] = {}
    for bm in block_markers:
        key = f"{bm.id}:{bm.phase}:{bm.inst}"
        fingerprints[key] = hash_block_content(bm.content)
    return fingerprints
