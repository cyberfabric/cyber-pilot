"""Tests for trace_graph.py — P1-P4."""
import json
import textwrap
import tempfile
from pathlib import Path

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "cypilot", "scripts"))

from cypilot.utils.trace_graph import (
    AnchoredHit,
    EdgeType,
    FileIndexEntry,
    IndexCache,
    NodeType,
    SessionIndex,
    StaleNotification,
    StructuralAnchor,
    TraceGraph,
    TraceNode,
    build_doc_anchored_hits,
    build_trace_graph,
    compute_code_containers_regex,
    compute_code_fingerprints,
    compute_doc_anchors,
    compute_py_containers,
    content_hash,
    hash_block_content,
)


# ---------------------------------------------------------------------------
# Content hashing
# ---------------------------------------------------------------------------

class TestContentHash:
    def test_basic_hash(self):
        h = content_hash("hello world")
        assert isinstance(h, str)
        assert len(h) == 64  # SHA-256 hex digest

    def test_stable_across_calls(self):
        assert content_hash("abc") == content_hash("abc")

    def test_trailing_whitespace_normalized(self):
        assert content_hash("line1  \nline2\t") == content_hash("line1\nline2")

    def test_different_content_different_hash(self):
        assert content_hash("a") != content_hash("b")

    def test_empty_string(self):
        h = content_hash("")
        assert isinstance(h, str) and len(h) == 64


class TestHashBlockContent:
    def test_block_hash(self):
        lines = ("    x = 1", "    y = 2")
        h = hash_block_content(lines)
        assert isinstance(h, str) and len(h) == 64

    def test_stable(self):
        lines = ("a", "b")
        assert hash_block_content(lines) == hash_block_content(lines)


# ---------------------------------------------------------------------------
# Document anchors
# ---------------------------------------------------------------------------

class TestComputeDocAnchors:
    def test_simple_headings(self):
        lines = ["# Top", "text", "## Sub", "more text"]
        anchors = compute_doc_anchors(lines)
        assert anchors[1] == ("Top",)
        assert anchors[2] == ("Top",)
        assert anchors[3] == ("Top", "Sub")
        assert anchors[4] == ("Top", "Sub")

    def test_heading_replacement(self):
        lines = ["# A", "## B", "## C", "text"]
        anchors = compute_doc_anchors(lines)
        assert anchors[3] == ("A", "C")
        assert anchors[4] == ("A", "C")

    def test_nested_headings(self):
        lines = ["# L1", "## L2", "### L3", "text", "## L2b"]
        anchors = compute_doc_anchors(lines)
        assert anchors[3] == ("L1", "L2", "L3")
        assert anchors[5] == ("L1", "L2b")

    def test_code_fence_skipped(self):
        lines = ["# Top", "```", "## Not a heading", "```", "text"]
        anchors = compute_doc_anchors(lines)
        assert anchors[3] == ("Top",)  # inside fence, inherits parent
        assert anchors[5] == ("Top",)

    def test_empty_file(self):
        assert compute_doc_anchors([]) == {}


# ---------------------------------------------------------------------------
# Python AST containers
# ---------------------------------------------------------------------------

class TestComputePyContainers:
    def test_simple_function(self):
        src = textwrap.dedent("""\
            x = 1

            def foo():
                return 42

            y = 2
        """)
        containers = compute_py_containers(src)
        assert containers[1] == ""         # x = 1 (module level)
        assert containers[3] == "foo"      # def foo():
        assert containers[4] == "foo"      # return 42
        assert containers[6] == ""         # y = 2

    def test_class_with_method(self):
        src = textwrap.dedent("""\
            class MyClass:
                def method(self):
                    pass
        """)
        containers = compute_py_containers(src)
        assert containers[1] == "MyClass"
        assert containers[2] == "MyClass.method"
        assert containers[3] == "MyClass.method"

    def test_nested_functions(self):
        src = textwrap.dedent("""\
            def outer():
                def inner():
                    pass
                return inner
        """)
        containers = compute_py_containers(src)
        assert containers[1] == "outer"
        assert containers[2] == "outer.inner"
        assert containers[4] == "outer"

    def test_syntax_error_returns_empty(self):
        assert compute_py_containers("def :(") == {}

    def test_async_function(self):
        src = textwrap.dedent("""\
            async def handler():
                await something()
        """)
        containers = compute_py_containers(src)
        assert containers[1] == "handler"
        assert containers[2] == "handler"


# ---------------------------------------------------------------------------
# Regex fallback containers
# ---------------------------------------------------------------------------

class TestComputeCodeContainersRegex:
    def test_python_def(self):
        lines = ["x = 1", "def foo():", "    pass", "def bar():", "    pass"]
        containers = compute_code_containers_regex(lines)
        assert containers[1] == ""
        assert containers[2] == "foo"
        assert containers[3] == "foo"
        assert containers[4] == "bar"

    def test_class_detection(self):
        lines = ["class Foo:", "    pass"]
        containers = compute_code_containers_regex(lines)
        assert containers[1] == "Foo"

    def test_rust_fn(self):
        lines = ["fn main() {", "    println!();", "}"]
        containers = compute_code_containers_regex(lines)
        assert containers[1] == "main"

    def test_empty(self):
        assert compute_code_containers_regex([]) == {}


# ---------------------------------------------------------------------------
# AnchoredHit
# ---------------------------------------------------------------------------

class TestAnchoredHit:
    def test_to_legacy_row(self):
        anchor = StructuralAnchor(heading_path=("Top", "Sub"), content_hash="abc123")
        hit = AnchoredHit(
            id="cpt-test-fr-foo",
            type="definition",
            anchor=anchor,
            line=42,
            checked=True,
            has_task=True,
            has_priority=True,
            priority="p1",
            artifact_kind="PRD",
            artifact_path=Path("/tmp/PRD.md"),
            system="test",
            id_kind="fr",
        )
        row = hit.to_legacy_row()
        assert row["id"] == "cpt-test-fr-foo"
        assert row["line"] == 42
        assert row["checked"] is True
        assert row["priority"] == "p1"
        assert row["has_task"] is True
        assert row["has_priority"] is True
        assert row["artifact_kind"] == "PRD"
        assert row["system"] == "test"
        assert row["id_kind"] == "fr"
        assert row["headings"] == ["Top", "Sub"]

    def test_to_legacy_row_defaults(self):
        anchor = StructuralAnchor()
        hit = AnchoredHit(id="cpt-x", type="reference", anchor=anchor, line=1)
        row = hit.to_legacy_row()
        assert row["checked"] is False
        assert row["priority"] is None
        assert row["headings"] == []


# ---------------------------------------------------------------------------
# Build doc anchored hits
# ---------------------------------------------------------------------------

class TestBuildDocAnchoredHits:
    def test_basic(self):
        lines = ["# Overview", "", "**ID**: `cpt-test-fr-foo`", "", "## Details", "text"]
        hits = [{"id": "cpt-test-fr-foo", "line": 3, "type": "definition", "checked": False}]
        headings_at = [[], ["Overview"], ["Overview"], ["Overview"], ["Overview"], ["Overview", "Details"], ["Overview", "Details"]]
        result = build_doc_anchored_hits(Path("/tmp/test.md"), hits, headings_at, lines=lines)
        assert len(result) == 1
        assert result[0].id == "cpt-test-fr-foo"
        assert result[0].anchor.heading_path == ("Overview",)
        assert result[0].anchor.content_hash != ""

    def test_empty_hits(self):
        result = build_doc_anchored_hits(Path("/tmp/test.md"), [], [[]], lines=[])
        assert result == []


# ---------------------------------------------------------------------------
# Code fingerprints
# ---------------------------------------------------------------------------

class TestComputeCodeFingerprints:
    def test_basic(self):
        class FakeBlock:
            def __init__(self, id, phase, inst, content):
                self.id = id
                self.phase = phase
                self.inst = inst
                self.content = content

        blocks = [
            FakeBlock("cpt-test-flow-a", 1, "step-1", ("x = 1", "y = 2")),
            FakeBlock("cpt-test-flow-a", 1, "step-2", ("z = 3",)),
        ]
        fps = compute_code_fingerprints(blocks)
        assert len(fps) == 2
        assert "cpt-test-flow-a:1:step-1" in fps
        assert "cpt-test-flow-a:1:step-2" in fps
        assert fps["cpt-test-flow-a:1:step-1"] != fps["cpt-test-flow-a:1:step-2"]

    def test_empty(self):
        assert compute_code_fingerprints([]) == {}


# ===========================================================================
# P2: IndexCache
# ===========================================================================

class TestIndexCache:
    def test_empty_cache_reports_stale(self, tmp_path):
        cache = IndexCache()
        f = tmp_path / "test.md"
        f.write_text("hello")
        assert cache.is_stale(f)

    def test_after_update_not_stale(self, tmp_path):
        cache = IndexCache()
        f = tmp_path / "test.md"
        f.write_text("hello")
        cache.update_entry(f, [{"id": "cpt-x", "line": 1}])
        assert not cache.is_stale(f)

    def test_mtime_change_is_stale(self, tmp_path):
        cache = IndexCache()
        f = tmp_path / "test.md"
        f.write_text("hello")
        cache.update_entry(f, [])
        # Modify file
        f.write_text("changed")
        assert cache.is_stale(f)

    def test_changed_files(self, tmp_path):
        cache = IndexCache()
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        f1.write_text("a")
        f2.write_text("b")
        cache.update_entry(f1, [])
        # f1 is cached, f2 is not
        changed = cache.changed_files([f1, f2])
        assert f2 in changed
        assert f1 not in changed

    def test_remove_entry(self, tmp_path):
        cache = IndexCache()
        f = tmp_path / "test.md"
        f.write_text("hello")
        cache.update_entry(f, [])
        assert not cache.is_stale(f)
        cache.remove_entry(f)
        assert cache.is_stale(f)

    def test_json_round_trip(self, tmp_path):
        cache = IndexCache()
        f = tmp_path / "test.md"
        f.write_text("hello")
        cache.update_entry(f, [{"id": "cpt-x", "line": 1, "type": "definition"}])

        cache_file = tmp_path / "cache.json"
        cache.save(cache_file)
        assert cache_file.exists()

        loaded = IndexCache.load(cache_file)
        assert str(f) in loaded.entries
        assert loaded.entries[str(f)].hits == [{"id": "cpt-x", "line": 1, "type": "definition"}]

    def test_load_corrupt_returns_empty(self, tmp_path):
        cache_file = tmp_path / "cache.json"
        cache_file.write_text("not json")
        loaded = IndexCache.load(cache_file)
        assert len(loaded.entries) == 0

    def test_load_wrong_version_returns_empty(self, tmp_path):
        cache_file = tmp_path / "cache.json"
        cache_file.write_text(json.dumps({"version": 999, "entries": {}}))
        loaded = IndexCache.load(cache_file)
        assert len(loaded.entries) == 0

    def test_load_missing_returns_empty(self, tmp_path):
        loaded = IndexCache.load(tmp_path / "nonexistent.json")
        assert len(loaded.entries) == 0


# ===========================================================================
# P3: TraceGraph
# ===========================================================================

class TestTraceGraph:
    def test_add_node_and_retrieve(self):
        g = TraceGraph()
        n = TraceNode(id="n1", node_type=NodeType.ARTIFACT, data={"file": "/a.md"})
        g.add_node(n)
        assert "n1" in g.nodes

    def test_add_edge_forward(self):
        g = TraceGraph()
        g.add_node(TraceNode(id="a", node_type=NodeType.ARTIFACT))
        g.add_node(TraceNode(id="d", node_type=NodeType.DEFINITION))
        g.add_edge("a", "d", EdgeType.DEFINES)
        neighbors = g.neighbors("a")
        assert len(neighbors) == 1
        assert neighbors[0].id == "d"

    def test_add_edge_reverse(self):
        g = TraceGraph()
        g.add_node(TraceNode(id="a", node_type=NodeType.ARTIFACT))
        g.add_node(TraceNode(id="d", node_type=NodeType.DEFINITION))
        g.add_edge("a", "d", EdgeType.DEFINES)
        rev = g.reverse_neighbors("d")
        assert len(rev) == 1
        assert rev[0].id == "a"

    def test_edge_type_filter(self):
        g = TraceGraph()
        g.add_node(TraceNode(id="a", node_type=NodeType.ARTIFACT))
        g.add_node(TraceNode(id="d1", node_type=NodeType.DEFINITION))
        g.add_node(TraceNode(id="r1", node_type=NodeType.REFERENCE))
        g.add_edge("a", "d1", EdgeType.DEFINES)
        g.add_edge("a", "r1", EdgeType.CONTAINS)
        assert len(g.neighbors("a", EdgeType.DEFINES)) == 1
        assert len(g.neighbors("a", EdgeType.CONTAINS)) == 1
        assert len(g.neighbors("a")) == 2

    def test_definitions_for_id(self):
        g = TraceGraph()
        g.add_node(TraceNode(id="def:cpt-x:f:1", node_type=NodeType.DEFINITION, data={"id": "cpt-x"}))
        g.add_node(TraceNode(id="def:cpt-y:f:2", node_type=NodeType.DEFINITION, data={"id": "cpt-y"}))
        assert len(g.definitions_for_id("cpt-x")) == 1
        assert len(g.definitions_for_id("cpt-z")) == 0

    def test_references_for_id(self):
        g = TraceGraph()
        g.add_node(TraceNode(id="ref:cpt-x:f:5", node_type=NodeType.REFERENCE, data={"id": "cpt-x"}))
        assert len(g.references_for_id("cpt-x")) == 1

    def test_implementations_for_id(self):
        g = TraceGraph()
        g.add_node(TraceNode(id="code:cpt-x:f:10", node_type=NodeType.CODE_BLOCK, data={"id": "cpt-x"}))
        assert len(g.implementations_for_id("cpt-x")) == 1

    def test_nodes_for_file(self):
        g = TraceGraph()
        g.add_node(TraceNode(id="n1", node_type=NodeType.DEFINITION, data={"file": "/a.md"}))
        g.add_node(TraceNode(id="n2", node_type=NodeType.DEFINITION, data={"file": "/b.md"}))
        assert len(g.nodes_for_file(Path("/a.md"))) == 1

    def test_affected_by_change(self):
        g = TraceGraph()
        # def in file A, ref in file B pointing to it
        g.add_node(TraceNode(id="def1", node_type=NodeType.DEFINITION, data={"id": "cpt-x", "file": "/a.md"}))
        g.add_node(TraceNode(id="ref1", node_type=NodeType.REFERENCE, data={"id": "cpt-x", "file": "/b.md"}))
        g.add_edge("ref1", "def1", EdgeType.REFERENCES)
        # Change file A -> should affect def1 (directly) and ref1 (via reverse REFERENCES)
        affected = g.affected_by_change(Path("/a.md"))
        affected_ids = {n.id for n in affected}
        assert "def1" in affected_ids

    def test_affected_by_change_code_implements(self):
        g = TraceGraph()
        g.add_node(TraceNode(id="def1", node_type=NodeType.DEFINITION, data={"id": "cpt-x", "file": "/spec.md"}))
        g.add_node(TraceNode(id="code1", node_type=NodeType.CODE_BLOCK, data={"id": "cpt-x", "file": "/impl.py"}))
        g.add_edge("code1", "def1", EdgeType.IMPLEMENTS)
        # Change impl.py -> should find code1
        affected = g.affected_by_change(Path("/impl.py"))
        assert any(n.id == "code1" for n in affected)


class TestBuildTraceGraph:
    def test_basic_graph(self):
        defs = {"cpt-x": [{"artifact_path": "/a.md", "line": 10, "artifact_kind": "PRD", "checked": False, "system": "test", "id_kind": "fr"}]}
        refs = {"cpt-x": [{"artifact_path": "/b.md", "line": 5}]}
        g = build_trace_graph(defs, refs)
        assert len(g.nodes) > 0
        assert len(g.definitions_for_id("cpt-x")) == 1
        assert len(g.references_for_id("cpt-x")) == 1

    def test_code_refs(self):
        defs = {"cpt-x": [{"artifact_path": "/a.md", "line": 1, "artifact_kind": "PRD"}]}
        refs = {}
        code = [{"id": "cpt-x", "file": "/impl.py", "line": 42, "kind": "flow", "inst": "step-1"}]
        g = build_trace_graph(defs, refs, code_refs=code)
        assert len(g.implementations_for_id("cpt-x")) == 1

    def test_empty(self):
        g = build_trace_graph({}, {})
        assert len(g.nodes) == 0


# ===========================================================================
# P4: SessionIndex
# ===========================================================================

class TestSessionIndex:
    def test_register_and_no_changes(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("hello")
        session = SessionIndex()
        session.register_files([f])
        notifications = session.check_for_changes()
        assert len(notifications) == 0

    def test_detect_change(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("hello")
        session = SessionIndex()
        session.register_files([f])
        # Modify file
        import time
        time.sleep(0.05)  # Ensure mtime changes
        f.write_text("changed")
        notifications = session.check_for_changes()
        assert len(notifications) == 1
        assert notifications[0].file_path == f

    def test_detect_deletion(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("hello")
        session = SessionIndex()
        session.register_files([f])
        f.unlink()
        notifications = session.check_for_changes()
        assert len(notifications) == 1
        assert "deleted" in notifications[0].message.lower() or "inaccessible" in notifications[0].message.lower()

    def test_refresh_file(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("hello")
        session = SessionIndex()
        session.register_files([f])
        session.refresh_file(f, [{"id": "cpt-x"}])
        assert str(f) in session.cache.entries

    def test_stale_notification_structure(self):
        n = StaleNotification(file_path=Path("/a.md"), affected_ids=("cpt-x",), message="Changed")
        assert n.file_path == Path("/a.md")
        assert n.affected_ids == ("cpt-x",)
        assert n.message == "Changed"
