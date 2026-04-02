"""Structural traceability graph for Cypilot codebase indexing.

Phase 1: Structural anchoring + content hashing
Phase 2: Incremental diff-aware index
Phase 3: Traceability graph
Phase 4: Real-time session sync

@cpt-algo:cpt-cypilot-algo-smart-indexing-compute-anchor:p1
@cpt-algo:cpt-cypilot-algo-smart-indexing-compute-hash:p1
@cpt-algo:cpt-cypilot-algo-smart-indexing-manage-cache:p2
@cpt-algo:cpt-cypilot-algo-smart-indexing-build-graph:p3
@cpt-algo:cpt-cypilot-algo-smart-indexing-detect-affected:p3
@cpt-algo:cpt-cypilot-algo-smart-indexing-file-watcher:p4
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple


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
            "type": self.type,
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
    Maintains a stack of (indent, name) to handle nested scopes:
    ``class Foo`` → ``def bar`` produces ``Foo.bar``, and returning
    to the class body restores ``Foo``.
    """
    result: Dict[int, str] = {}
    stack: List[Tuple[int, str]] = []  # (indent_level, name)

    for idx, line in enumerate(lines):
        line_no = idx + 1
        if not line.strip():
            # Blank line: keep current scope
            result[line_no] = ".".join(n for _, n in stack) if stack else ""
            continue

        line_indent = len(line) - len(line.lstrip())

        # Pop scopes that this line has exited
        while stack and line_indent <= stack[-1][0]:
            stack.pop()

        m = _FUNC_RE.match(line)
        if m:
            name = m.group(1) or m.group(2) or ""
            stack.append((line_indent, name))

        result[line_no] = ".".join(n for _, n in stack) if stack else ""

    return result
# @cpt-end:cpt-cypilot-algo-smart-indexing-compute-anchor:p1:inst-regex-fallback


# ---------------------------------------------------------------------------
# P1: Anchored Scan (combines scan_cpt_ids + heading anchors + content hash)
# ---------------------------------------------------------------------------

# @cpt-begin:cpt-cypilot-algo-smart-indexing-compute-anchor:p1:inst-return-anchors
def build_doc_anchored_hits(
    path: Path,
    hits: Sequence[Dict[str, object]],
    _headings_at: Sequence[Sequence[str]],
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
    """Extract text of the section containing target_line.

    Fence-aware: headings inside fenced code blocks (```) are ignored
    so that code samples containing ``# ...`` do not split the section.
    """
    if not lines:
        return ""

    # Find the heading at or above target_line (fence-aware scan backwards)
    section_start = 0
    section_level = 0
    # Build a quick fence-state map for the file
    in_fence = [False] * (len(lines) + 1)
    fence = False
    for i, raw in enumerate(lines):
        if _CODE_FENCE_RE.match(raw):
            fence = not fence
        in_fence[i] = fence

    for i in range(target_line - 1, -1, -1):
        if in_fence[i]:
            continue
        hm = _HEADING_RE.match(lines[i])
        if hm:
            section_start = i
            section_level = len(hm.group(1))
            break

    # Find end of section (next heading at same or higher level, outside fence)
    section_end = len(lines)
    for i in range(section_start + 1, len(lines)):
        if in_fence[i]:
            continue
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


# ===========================================================================
# P2: Incremental Diff-Aware Index
# ===========================================================================

_CACHE_VERSION = 1


@dataclass
class FileIndexEntry:
    """Cached parse results for a single file.

    Stores plain dict rows (same format as ``scan_cpt_ids()`` output)
    because ``cross_validate_artifacts()`` consumes those dicts directly.
    ``AnchoredHit`` enrichment (heading_path, container, content_hash)
    is computed on-the-fly from these rows and the file content when
    needed. This is by-design: the cache avoids coupling to the P1
    enrichment layer so it stays backward-compatible.
    """
    path: str
    mtime: float
    content_hash: str
    hits: List[Dict[str, object]] = field(default_factory=list)


# @cpt-begin:cpt-cypilot-algo-smart-indexing-manage-cache:p2:inst-init-cache
@dataclass
class IndexCache:
    """Persistent index cache with mtime + hash based staleness detection.

    Stores parsed scan results per file. Staleness is checked by mtime
    first (fast), then verified by content hash if mtime changed.
    """
    version: int = _CACHE_VERSION
    entries: Dict[str, FileIndexEntry] = field(default_factory=dict)

    def is_stale(self, path: Path) -> bool:
        """Check whether *path* needs re-parsing.

        Checks mtime first (fast). If mtime changed, falls back to
        content hash comparison so that a plain ``touch`` does not
        force a reparse when the content is unchanged.
        """
        key = str(path)
        entry = self.entries.get(key)
        if entry is None:
            return True
        try:
            current_mtime = path.stat().st_mtime
        except OSError:
            return True
        if current_mtime == entry.mtime:
            return False
        # mtime changed — verify by content hash
        try:
            current_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            return True
        if current_hash == entry.content_hash:
            # Content unchanged despite mtime change; update cached mtime
            entry.mtime = current_mtime
            return False
        return True

    def update_entry(self, path: Path, hits: List[Dict[str, object]]) -> None:
        """Store (or replace) the parse results for *path*."""
        key = str(path)
        try:
            raw = path.read_bytes()
            mtime = path.stat().st_mtime
        except OSError:
            return
        c_hash = hashlib.sha256(raw).hexdigest()
        self.entries[key] = FileIndexEntry(
            path=key, mtime=mtime, content_hash=c_hash, hits=hits,
        )

    def remove_entry(self, path: Path) -> None:
        """Remove a file that no longer exists."""
        self.entries.pop(str(path), None)

    def changed_files(self, paths: Sequence[Path]) -> List[Path]:
        """Return only the files that need re-parsing."""
        return [p for p in paths if self.is_stale(p)]
# @cpt-end:cpt-cypilot-algo-smart-indexing-manage-cache:p2:inst-init-cache

    # ---- serialisation ----------------------------------------------------

    # @cpt-begin:cpt-cypilot-algo-smart-indexing-manage-cache:p2:inst-serialize
    def save(self, cache_path: Path) -> None:
        """Persist the cache to JSON."""
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": self.version,
            "entries": {
                k: {
                    "path": e.path,
                    "mtime": e.mtime,
                    "content_hash": e.content_hash,
                    "hits": e.hits,
                }
                for k, e in self.entries.items()
            },
        }
        cache_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, cache_path: Path) -> "IndexCache":
        """Load from JSON. Returns empty cache on any error."""
        try:
            raw = json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            return cls()
        if not isinstance(raw, dict) or raw.get("version") != _CACHE_VERSION:
            return cls()
        cache = cls(version=raw.get("version", _CACHE_VERSION))
        for k, v in raw.get("entries", {}).items():
            if not isinstance(v, dict):
                continue
            cache.entries[k] = FileIndexEntry(
                path=v.get("path", k),
                mtime=float(v.get("mtime", 0)),
                content_hash=str(v.get("content_hash", "")),
                hits=list(v.get("hits", [])),
            )
        return cache
    # @cpt-end:cpt-cypilot-algo-smart-indexing-manage-cache:p2:inst-serialize


def git_changed_files(project_root: Path) -> Optional[Set[str]]:
    """Return set of file paths changed according to git, or None on error.

    Includes modified tracked files (staged + unstaged) *and* untracked
    files so that newly created artifacts are picked up for indexing.
    """
    try:
        # Modified tracked files (unstaged)
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=str(project_root),
            capture_output=True, text=True, timeout=10, check=False,
        )
        if result.returncode != 0:
            return None
        files = set(result.stdout.strip().splitlines())
        # Staged changes
        staged = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            cwd=str(project_root),
            capture_output=True, text=True, timeout=10, check=False,
        )
        if staged.returncode == 0:
            files.update(staged.stdout.strip().splitlines())
        # Untracked files (new files not yet added)
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=str(project_root),
            capture_output=True, text=True, timeout=10, check=False,
        )
        if untracked.returncode == 0:
            files.update(untracked.stdout.strip().splitlines())
        return files
    except (OSError, subprocess.TimeoutExpired):
        return None


# ===========================================================================
# P3: Traceability Graph
# ===========================================================================

class NodeType(Enum):
    ARTIFACT = "artifact"
    SECTION = "section"
    DEFINITION = "definition"
    REFERENCE = "reference"
    CODE_FILE = "code_file"
    CODE_BLOCK = "code_block"


class EdgeType(Enum):
    CONTAINS = "contains"
    DEFINES = "defines"
    REFERENCES = "references"
    IMPLEMENTS = "implements"


@dataclass
class TraceNode:
    """A node in the traceability graph."""
    id: str
    node_type: NodeType
    data: Dict[str, object] = field(default_factory=dict)


# @cpt-begin:cpt-cypilot-algo-smart-indexing-build-graph:p3:inst-build-adjacency
@dataclass
class TraceGraph:
    """Dual adjacency-list graph for traceability queries.

    Supports forward and reverse traversal with optional edge-type
    filtering. Purpose-built for the 5 node types and 4 edge types
    needed by Cypilot traceability.
    """
    nodes: Dict[str, TraceNode] = field(default_factory=dict)
    _forward: Dict[str, List[Tuple[str, EdgeType]]] = field(default_factory=dict)
    _reverse: Dict[str, List[Tuple[str, EdgeType]]] = field(default_factory=dict)

    def add_node(self, node: TraceNode) -> None:
        self.nodes[node.id] = node

    def add_edge(self, source: str, target: str, edge_type: EdgeType) -> None:
        self._forward.setdefault(source, []).append((target, edge_type))
        self._reverse.setdefault(target, []).append((source, edge_type))

    def neighbors(
        self, node_id: str, edge_type: Optional[EdgeType] = None,
    ) -> List[TraceNode]:
        """Forward neighbors, optionally filtered by edge type."""
        edges = self._forward.get(node_id, [])
        if edge_type is not None:
            edges = [(t, e) for t, e in edges if e == edge_type]
        return [self.nodes[t] for t, _ in edges if t in self.nodes]

    def reverse_neighbors(
        self, node_id: str, edge_type: Optional[EdgeType] = None,
    ) -> List[TraceNode]:
        """Reverse neighbors, optionally filtered by edge type."""
        edges = self._reverse.get(node_id, [])
        if edge_type is not None:
            edges = [(s, e) for s, e in edges if e == edge_type]
        return [self.nodes[s] for s, _ in edges if s in self.nodes]
# @cpt-end:cpt-cypilot-algo-smart-indexing-build-graph:p3:inst-build-adjacency

    # @cpt-begin:cpt-cypilot-algo-smart-indexing-detect-affected:p3:inst-find-file-nodes
    def nodes_for_file(self, file_path: Path) -> List[TraceNode]:
        """All nodes belonging to a specific file."""
        fp = str(file_path)
        return [
            n for n in self.nodes.values()
            if n.data.get("file") == fp or n.data.get("artifact_path") == fp
        ]

    def affected_by_change(self, file_path: Path) -> List[TraceNode]:
        """Key query: which nodes are affected when *file_path* changes?

        For each node in the changed file:
        1. Follow *forward* IMPLEMENTS edges (CODE_BLOCK -> DEFINITION)
           to find the definitions that the code implements.
        2. Follow *reverse* REFERENCES edges from those definitions
           to find all docs that reference them.
        3. Follow *reverse* IMPLEMENTS edges to find other code that
           implements the same definitions.

        This ensures a code change surfaces the specs it implements
        and all artifacts that reference those specs.
        """
        file_nodes = self.nodes_for_file(file_path)
        affected: Dict[str, TraceNode] = {}
        frontier = list(file_nodes)
        visited: Set[str] = set()
        while frontier:
            node = frontier.pop()
            if node.id in visited:
                continue
            visited.add(node.id)
            affected[node.id] = node
            # Forward: CODE_BLOCK -> DEFINITION (implementations)
            for fwd in self.neighbors(node.id, EdgeType.IMPLEMENTS):
                if fwd.id not in visited:
                    frontier.append(fwd)
            # Forward: REFERENCE -> DEFINITION
            for fwd in self.neighbors(node.id, EdgeType.REFERENCES):
                if fwd.id not in visited:
                    frontier.append(fwd)
            # Reverse: find nodes that reference or implement this one
            for rev in self.reverse_neighbors(node.id, EdgeType.REFERENCES):
                if rev.id not in visited:
                    frontier.append(rev)
            for rev in self.reverse_neighbors(node.id, EdgeType.IMPLEMENTS):
                if rev.id not in visited:
                    frontier.append(rev)
        return list(affected.values())
    # @cpt-end:cpt-cypilot-algo-smart-indexing-detect-affected:p3:inst-find-file-nodes

    def definitions_for_id(self, cpt_id: str) -> List[TraceNode]:
        """All DEFINITION nodes with a matching cpt ID."""
        return [
            n for n in self.nodes.values()
            if n.node_type == NodeType.DEFINITION and n.data.get("id") == cpt_id
        ]

    def references_for_id(self, cpt_id: str) -> List[TraceNode]:
        """All REFERENCE nodes pointing to a cpt ID."""
        return [
            n for n in self.nodes.values()
            if n.node_type == NodeType.REFERENCE and n.data.get("id") == cpt_id
        ]

    def implementations_for_id(self, cpt_id: str) -> List[TraceNode]:
        """All CODE_BLOCK nodes implementing a cpt ID."""
        return [
            n for n in self.nodes.values()
            if n.node_type == NodeType.CODE_BLOCK and n.data.get("id") == cpt_id
        ]


# @cpt-begin:cpt-cypilot-algo-smart-indexing-build-graph:p3:inst-create-artifact-nodes
def build_trace_graph(
    defs_by_id: Dict[str, List[Dict[str, object]]],
    refs_by_id: Dict[str, List[Dict[str, object]]],
    code_refs: Optional[List[Dict[str, object]]] = None,
) -> TraceGraph:
    """Build a TraceGraph from the flat index dicts.

    This is the bridge between the existing validation pipeline
    (which produces defs_by_id/refs_by_id) and the new graph.
    """
    graph = TraceGraph()
    artifact_nodes: Dict[str, str] = {}  # file path -> node id

    # Create artifact and definition nodes from defs_by_id
    for cpt_id, rows in defs_by_id.items():
        for row in rows:
            fp = str(row.get("artifact_path", ""))
            # Ensure artifact node exists
            if fp and fp not in artifact_nodes:
                art_nid = f"artifact:{fp}"
                graph.add_node(TraceNode(
                    id=art_nid, node_type=NodeType.ARTIFACT,
                    data={"file": fp, "artifact_path": fp,
                           "artifact_kind": row.get("artifact_kind", "")},
                ))
                artifact_nodes[fp] = art_nid

            # Definition node
            def_nid = f"def:{cpt_id}:{fp}:{row.get('line', 0)}"
            graph.add_node(TraceNode(
                id=def_nid, node_type=NodeType.DEFINITION,
                data={"id": cpt_id, "file": fp, "artifact_path": fp,
                       "line": row.get("line", 0), **{
                           k: row[k] for k in ("checked", "system", "id_kind",
                                                "artifact_kind") if k in row}},
            ))
            if fp in artifact_nodes:
                graph.add_edge(artifact_nodes[fp], def_nid, EdgeType.DEFINES)

    # Create reference nodes from refs_by_id
    for cpt_id, rows in refs_by_id.items():
        for row in rows:
            fp = str(row.get("artifact_path", ""))
            ref_nid = f"ref:{cpt_id}:{fp}:{row.get('line', 0)}"
            graph.add_node(TraceNode(
                id=ref_nid, node_type=NodeType.REFERENCE,
                data={"id": cpt_id, "file": fp, "artifact_path": fp,
                       "line": row.get("line", 0)},
            ))
            # Link reference to its definition(s)
            for def_node in graph.definitions_for_id(cpt_id):
                graph.add_edge(ref_nid, def_node.id, EdgeType.REFERENCES)

    # Create code block nodes
    if code_refs:
        for cref in code_refs:
            cpt_id = str(cref.get("id", ""))
            fp = str(cref.get("file", ""))
            line = cref.get("line", 0)
            cb_nid = f"code:{cpt_id}:{fp}:{line}"
            graph.add_node(TraceNode(
                id=cb_nid, node_type=NodeType.CODE_BLOCK,
                data={"id": cpt_id, "file": fp, "line": line,
                       "kind": cref.get("kind"), "inst": cref.get("inst")},
            ))
            for def_node in graph.definitions_for_id(cpt_id):
                graph.add_edge(cb_nid, def_node.id, EdgeType.IMPLEMENTS)

    return graph
# @cpt-end:cpt-cypilot-algo-smart-indexing-build-graph:p3:inst-create-artifact-nodes


# ===========================================================================
# P4: Real-Time Session Sync
# ===========================================================================

@dataclass(frozen=True)
class StaleNotification:
    """Notification that a tracked file has changed."""
    file_path: Path
    affected_ids: Tuple[str, ...] = ()
    message: str = ""


# @cpt-begin:cpt-cypilot-algo-smart-indexing-file-watcher:p4:inst-initial-snapshot
@dataclass
class SessionIndex:
    """Wraps graph + cache for live session sync.

    Polls watched files by mtime (fast gate) then verifies by content
    hash so that ``touch`` or save-without-change does not emit false
    stale notifications.
    """
    graph: TraceGraph = field(default_factory=TraceGraph)
    cache: IndexCache = field(default_factory=IndexCache)
    _mtime_snapshot: Dict[str, float] = field(default_factory=dict)
    _hash_snapshot: Dict[str, str] = field(default_factory=dict)

    def register_files(self, paths: Sequence[Path]) -> None:
        """Record initial mtime and content hash snapshot for all watched files."""
        for p in paths:
            try:
                self._mtime_snapshot[str(p)] = p.stat().st_mtime
                self._hash_snapshot[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
            except OSError:
                pass
    # @cpt-end:cpt-cypilot-algo-smart-indexing-file-watcher:p4:inst-initial-snapshot

    # @cpt-begin:cpt-cypilot-algo-smart-indexing-file-watcher:p4:inst-compare-mtime
    def check_for_changes(self) -> List[StaleNotification]:
        """Poll watched files, return stale notifications for changed ones.

        Uses mtime as a fast gate, then verifies by content hash so
        that ``touch`` or save-without-change is not reported as stale.
        """
        notifications: List[StaleNotification] = []
        for path_str, old_mtime in list(self._mtime_snapshot.items()):
            p = Path(path_str)
            try:
                current_mtime = p.stat().st_mtime
            except OSError:
                # Remove from snapshots so we don't spam on every poll
                self._mtime_snapshot.pop(path_str, None)
                self._hash_snapshot.pop(path_str, None)
                self.cache.remove_entry(p)
                notifications.append(StaleNotification(
                    file_path=p, message=f"File deleted or inaccessible: {p}",
                ))
                continue
            if current_mtime != old_mtime:
                # Verify by content hash
                try:
                    current_hash = hashlib.sha256(p.read_bytes()).hexdigest()
                except OSError:
                    current_hash = ""
                old_hash = self._hash_snapshot.get(path_str, "")
                self._mtime_snapshot[path_str] = current_mtime
                if current_hash == old_hash:
                    continue  # mtime changed but content didn't — skip
                self._hash_snapshot[path_str] = current_hash
                affected = self.graph.affected_by_change(p)
                affected_ids = tuple(
                    str(n.data.get("id", "")) for n in affected
                    if n.data.get("id")
                )
                notifications.append(StaleNotification(
                    file_path=p, affected_ids=affected_ids,
                    message=f"Changed: {p} (affects {len(affected_ids)} IDs)",
                ))
        return notifications
    # @cpt-end:cpt-cypilot-algo-smart-indexing-file-watcher:p4:inst-compare-mtime

    # @cpt-begin:cpt-cypilot-algo-smart-indexing-file-watcher:p4:inst-create-notification
    def refresh_file(self, path: Path, hits: List[Dict[str, object]]) -> None:
        """Incrementally update the cache for a single changed file."""
        self.cache.update_entry(path, hits)
        try:
            self._mtime_snapshot[str(path)] = path.stat().st_mtime
            self._hash_snapshot[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            pass
    # @cpt-end:cpt-cypilot-algo-smart-indexing-file-watcher:p4:inst-create-notification
