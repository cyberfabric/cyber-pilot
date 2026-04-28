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

    def test_scope_exit(self):
        """Container should be cleared when indentation returns to declaration level."""
        lines = ["def foo():", "    body", "top_level_code", "more_top_level"]
        containers = compute_code_containers_regex(lines)
        assert containers[1] == "foo"
        assert containers[2] == "foo"
        assert containers[3] == ""   # scope exited
        assert containers[4] == ""   # still at top level

    def test_nested_class_method(self):
        """After inner method exits, outer class scope should be restored."""
        lines = [
            "class Foo:",          # indent 0, pushes Foo
            "    def bar(self):",  # indent 4, pushes bar -> Foo.bar
            "        body",        # indent 8, still in Foo.bar
            "    other_line",      # indent 4, pops bar -> Foo
            "top_level",           # indent 0, pops Foo -> ""
        ]
        containers = compute_code_containers_regex(lines)
        assert containers[1] == "Foo"
        assert containers[2] == "Foo.bar"
        assert containers[3] == "Foo.bar"
        assert containers[4] == "Foo"       # back to class scope
        assert containers[5] == ""          # top level

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
        assert row["type"] == "definition"
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

    def test_mtime_change_content_changed_is_stale(self, tmp_path):
        cache = IndexCache()
        f = tmp_path / "test.md"
        f.write_text("hello")
        cache.update_entry(f, [])
        # Modify file content
        f.write_text("changed")
        assert cache.is_stale(f)

    def test_touch_same_content_not_stale(self, tmp_path):
        """Touch (mtime change) with same content should NOT be stale."""
        cache = IndexCache()
        f = tmp_path / "test.md"
        f.write_text("hello")
        cache.update_entry(f, [])
        # Touch file (change mtime but not content)
        import os
        os.utime(f, (f.stat().st_atime + 10, f.stat().st_mtime + 10))
        assert not cache.is_stale(f)

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
        # Change impl.py -> should find code1 AND def1 (via forward IMPLEMENTS)
        affected = g.affected_by_change(Path("/impl.py"))
        affected_ids = {n.id for n in affected}
        assert "code1" in affected_ids
        assert "def1" in affected_ids  # traversed forward IMPLEMENTS edge

    def test_affected_by_change_code_reaches_referencing_docs(self):
        """Code change -> definition -> referencing docs."""
        g = TraceGraph()
        g.add_node(TraceNode(id="def1", node_type=NodeType.DEFINITION, data={"id": "cpt-x", "file": "/spec.md"}))
        g.add_node(TraceNode(id="code1", node_type=NodeType.CODE_BLOCK, data={"id": "cpt-x", "file": "/impl.py"}))
        g.add_node(TraceNode(id="ref1", node_type=NodeType.REFERENCE, data={"id": "cpt-x", "file": "/decomp.md"}))
        g.add_edge("code1", "def1", EdgeType.IMPLEMENTS)
        g.add_edge("ref1", "def1", EdgeType.REFERENCES)
        # Change impl.py -> should reach code1 -> def1 -> ref1
        affected = g.affected_by_change(Path("/impl.py"))
        affected_ids = {n.id for n in affected}
        assert "code1" in affected_ids
        assert "def1" in affected_ids
        assert "ref1" in affected_ids  # referencing doc discovered


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
        # Modify file content and force mtime change via os.utime
        f.write_text("changed")
        os.utime(f, (f.stat().st_atime + 10, f.stat().st_mtime + 10))
        notifications = session.check_for_changes()
        assert len(notifications) == 1
        assert notifications[0].file_path == f

    def test_touch_no_content_change_no_notification(self, tmp_path):
        """Touch (mtime change) without content change should NOT emit notification."""
        f = tmp_path / "test.md"
        f.write_text("hello")
        session = SessionIndex()
        session.register_files([f])
        # Touch file (change mtime but not content)
        os.utime(f, (f.stat().st_atime + 10, f.stat().st_mtime + 10))
        notifications = session.check_for_changes()
        assert len(notifications) == 0

    def test_detect_deletion(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("hello")
        session = SessionIndex()
        session.register_files([f])
        f.unlink()
        notifications = session.check_for_changes()
        assert len(notifications) == 1
        assert "deleted" in notifications[0].message.lower() or "inaccessible" in notifications[0].message.lower()

    def test_deleted_file_not_spammed_on_subsequent_polls(self, tmp_path):
        """After a file is deleted, subsequent polls should not re-report it."""
        f = tmp_path / "test.md"
        f.write_text("hello")
        session = SessionIndex()
        session.register_files([f])
        f.unlink()
        # First poll: should report deletion
        n1 = session.check_for_changes()
        assert len(n1) == 1
        # Second poll: should NOT report again (tombstoned)
        n2 = session.check_for_changes()
        assert len(n2) == 0

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


# ===========================================================================
# Additional coverage tests
# ===========================================================================

class TestComputeCodeContainersRegexBlankLine:
    """Cover line 219-220: blank line inside a scope keeps current container."""

    def test_blank_line_inside_function_scope(self):
        lines = [
            "def foo():",     # indent 0 -> foo
            "    x = 1",      # indent 4 -> foo
            "",               # blank line -> should keep "foo" (line 219-220)
            "    y = 2",      # indent 4 -> foo
        ]
        containers = compute_code_containers_regex(lines)
        assert containers[3] == "foo"  # blank line preserves scope


class TestBuildDocAnchoredHitsNoFile:
    """Cover lines 260-263: OSError fallback when lines=None and path missing."""

    def test_nonexistent_path_no_lines(self):
        hits = [{"id": "cpt-x", "line": 1, "type": "definition"}]
        headings_at = [[]]
        result = build_doc_anchored_hits(
            Path("/nonexistent/path/file.md"), hits, headings_at, lines=None,
        )
        assert len(result) == 1
        assert result[0].id == "cpt-x"
        # With empty lines from OSError fallback, content_hash should be ""
        assert result[0].anchor.content_hash == ""


class TestExtractSectionTextEdgeCases:
    """Cover lines 298, 308, 313, 324, 327-328 in _extract_section_text."""

    def test_empty_lines(self):
        """Line 298: empty lines list returns empty string."""
        from cypilot.utils.trace_graph import _extract_section_text
        assert _extract_section_text([], 1) == ""

    def test_fenced_heading_ignored(self):
        """Lines 308, 313: headings inside fenced code blocks are skipped."""
        from cypilot.utils.trace_graph import _extract_section_text
        lines = [
            "# Real heading",     # 0: section start
            "Some text",          # 1
            "```",                # 2: fence open
            "# Fake heading",     # 3: inside fence, should be ignored
            "```",                # 4: fence close
            "More text",          # 5
            "# Next heading",     # 6: real heading ends section
        ]
        # target_line=4 (1-based line 5) is inside the first section
        result = _extract_section_text(lines, 5)
        assert "Real heading" in result
        assert "More text" in result
        # The fake heading inside the fence should NOT split the section
        assert "Fake heading" in result

    def test_fenced_heading_does_not_end_section(self):
        """Lines 324, 327-328: heading inside fence after section_start is skipped."""
        from cypilot.utils.trace_graph import _extract_section_text
        lines = [
            "# Section A",       # 0
            "Content A",         # 1
            "```",               # 2: fence open
            "# Not a heading",   # 3: inside fence
            "```",               # 4: fence close
            "Still section A",   # 5
            "# Section B",       # 6: real next section
        ]
        result = _extract_section_text(lines, 2)
        # Section A should span from line 0 to line 5 (exclusive of line 6)
        assert "Content A" in result
        assert "Still section A" in result
        assert "Section B" not in result

    def test_section_search_skips_fenced_heading_backwards(self):
        """Line 313: backward scan skips headings inside fences."""
        from cypilot.utils.trace_graph import _extract_section_text
        lines = [
            "# Top",             # 0
            "```",               # 1: fence open
            "# Fenced",          # 2: inside fence
            "```",               # 3: fence close
            "text after fence",  # 4
        ]
        # target_line=5 (1-based) -> idx 4, scanning backwards should skip
        # the fenced heading at idx 2 and find "# Top" at idx 0
        result = _extract_section_text(lines, 5)
        assert "Top" in result
        assert "text after fence" in result


class TestIndexCacheIsStaleEdgeCases:
    """Cover lines 400-401, 407-408, 421-422 in IndexCache."""

    def test_is_stale_stat_oserror(self, tmp_path):
        """Lines 400-401: OSError from stat() returns True."""
        cache = IndexCache()
        f = tmp_path / "test.md"
        f.write_text("hello")
        cache.update_entry(f, [])
        # Delete the file so stat() raises OSError
        f.unlink()
        assert cache.is_stale(f) is True

    def test_is_stale_read_bytes_oserror(self, tmp_path):
        """Lines 407-408: OSError from read_bytes() after mtime changed."""
        import hashlib as _hl
        cache = IndexCache()
        f = tmp_path / "test.md"
        f.write_text("hello")
        cache.update_entry(f, [])
        # Change mtime so we enter the hash-verification branch
        os.utime(f, (f.stat().st_atime + 10, f.stat().st_mtime + 10))
        # Now make the file unreadable by deleting it -- but we need stat
        # to succeed. Instead, use a directory (stat works, read_bytes fails).
        saved_mtime = f.stat().st_mtime
        saved_hash = _hl.sha256(f.read_bytes()).hexdigest()
        # Overwrite entry with current mtime-1 so mtime differs
        entry = cache.entries[str(f)]
        entry.mtime = saved_mtime - 1
        entry.content_hash = saved_hash
        # Delete and replace with directory so read_bytes raises OSError
        f.unlink()
        f.mkdir()
        assert cache.is_stale(f) is True
        f.rmdir()

    def test_update_entry_oserror(self, tmp_path):
        """Lines 421-422: update_entry with non-existent path is a no-op."""
        cache = IndexCache()
        missing = tmp_path / "gone.md"
        cache.update_entry(missing, [{"id": "cpt-z"}])
        assert str(missing) not in cache.entries

    def test_is_stale_mtime_changed_hash_matches_updates_mtime(self, tmp_path):
        """Lines 400-401, 409-411: mtime changed but hash matches -> update cached mtime."""
        cache = IndexCache()
        f = tmp_path / "test.md"
        f.write_text("hello")
        cache.update_entry(f, [])
        old_cached_mtime = cache.entries[str(f)].mtime
        # Touch file to change mtime without changing content
        new_mtime = old_cached_mtime + 100
        os.utime(f, (new_mtime, new_mtime))
        assert not cache.is_stale(f)
        # Verify that cached mtime was updated to the new value
        assert cache.entries[str(f)].mtime == new_mtime


class TestIndexCacheLoadEdgeCases:
    """Cover line 469: non-dict entry in entries is skipped."""

    def test_load_with_non_dict_entry(self, tmp_path):
        cache_file = tmp_path / "cache.json"
        data = {
            "version": 1,
            "entries": {
                "/good.md": {
                    "path": "/good.md",
                    "mtime": 1.0,
                    "content_hash": "abc",
                    "hits": [],
                },
                "/bad.md": "not a dict",  # line 469: should be skipped
            },
        }
        cache_file.write_text(json.dumps(data))
        loaded = IndexCache.load(cache_file)
        assert "/good.md" in loaded.entries
        assert "/bad.md" not in loaded.entries


class TestTraceGraphQueryMethods:
    """Cover lines 614, 624, 631 via affected_by_change traversal paths."""

    def test_references_for_id_no_match(self):
        """Line 614: references_for_id with no matching nodes."""
        g = TraceGraph()
        g.add_node(TraceNode(id="def1", node_type=NodeType.DEFINITION, data={"id": "cpt-x"}))
        assert g.references_for_id("cpt-nonexistent") == []

    def test_implementations_for_id_no_match(self):
        """Line 631: implementations_for_id with no matching nodes."""
        g = TraceGraph()
        g.add_node(TraceNode(id="ref1", node_type=NodeType.REFERENCE, data={"id": "cpt-x"}))
        assert g.implementations_for_id("cpt-nonexistent") == []

    def test_affected_by_change_forward_references_edge(self):
        """Line 624: ensure forward REFERENCES edge is traversed."""
        g = TraceGraph()
        # A reference node in the changed file that points to a definition
        g.add_node(TraceNode(
            id="ref1", node_type=NodeType.REFERENCE,
            data={"id": "cpt-x", "file": "/changed.md"},
        ))
        g.add_node(TraceNode(
            id="def1", node_type=NodeType.DEFINITION,
            data={"id": "cpt-x", "file": "/spec.md"},
        ))
        g.add_edge("ref1", "def1", EdgeType.REFERENCES)
        affected = g.affected_by_change(Path("/changed.md"))
        affected_ids = {n.id for n in affected}
        assert "ref1" in affected_ids
        assert "def1" in affected_ids  # reached via forward REFERENCES

    def test_affected_by_change_reverse_implements(self):
        """Line 631: reverse IMPLEMENTS edge traversal.

        When a definition changes, other code blocks implementing it
        should be discovered via reverse IMPLEMENTS.
        """
        g = TraceGraph()
        g.add_node(TraceNode(
            id="def1", node_type=NodeType.DEFINITION,
            data={"id": "cpt-x", "file": "/spec.md"},
        ))
        g.add_node(TraceNode(
            id="code1", node_type=NodeType.CODE_BLOCK,
            data={"id": "cpt-x", "file": "/impl1.py"},
        ))
        g.add_node(TraceNode(
            id="code2", node_type=NodeType.CODE_BLOCK,
            data={"id": "cpt-x", "file": "/impl2.py"},
        ))
        g.add_edge("code1", "def1", EdgeType.IMPLEMENTS)
        g.add_edge("code2", "def1", EdgeType.IMPLEMENTS)
        # Change spec.md -> def1 is direct, code1 and code2 via reverse IMPLEMENTS
        affected = g.affected_by_change(Path("/spec.md"))
        affected_ids = {n.id for n in affected}
        assert "def1" in affected_ids
        assert "code1" in affected_ids
        assert "code2" in affected_ids


class TestSessionIndexRefreshAndHash:
    """Cover lines 762-763, 791-792, 815-818 in SessionIndex."""

    def test_refresh_file_updates_snapshots(self, tmp_path):
        """Lines 815-818: refresh_file updates both mtime and hash snapshots."""
        import hashlib as _hl
        f = tmp_path / "test.md"
        f.write_text("original")
        session = SessionIndex()
        session.register_files([f])
        old_hash = session._hash_snapshot[str(f)]
        old_mtime = session._mtime_snapshot[str(f)]
        # Modify file
        f.write_text("updated content")
        session.refresh_file(f, [{"id": "cpt-refreshed"}])
        # Snapshots should reflect the new content
        assert session._hash_snapshot[str(f)] != old_hash
        assert session._hash_snapshot[str(f)] == _hl.sha256(b"updated content").hexdigest()
        assert str(f) in session.cache.entries

    def test_refresh_file_oserror(self, tmp_path):
        """Lines 817-818: refresh_file with missing file is a no-op for snapshots."""
        session = SessionIndex()
        missing = tmp_path / "gone.md"
        session.refresh_file(missing, [{"id": "cpt-x"}])
        # Should not crash; cache update is also a no-op for missing files
        assert str(missing) not in session._mtime_snapshot

    def test_check_for_changes_read_bytes_oserror(self, tmp_path):
        """Lines 791-792: OSError on read_bytes sets current_hash to empty string."""
        f = tmp_path / "test.md"
        f.write_text("hello")
        session = SessionIndex()
        session.register_files([f])
        # Change mtime so we enter the hash branch, then make read fail
        old_mtime = f.stat().st_mtime
        # Replace file with a directory so stat works but read_bytes fails
        f.unlink()
        f.mkdir()
        # Manually set a different mtime to trigger the branch
        new_mtime = old_mtime + 10
        os.utime(f, (new_mtime, new_mtime))
        notifications = session.check_for_changes()
        # Should detect a change (empty hash != old hash)
        assert len(notifications) == 1
        f.rmdir()

    def test_register_files_oserror(self, tmp_path):
        """Lines 762-763: register_files with non-existent path is silently skipped."""
        session = SessionIndex()
        missing = tmp_path / "nonexistent.md"
        session.register_files([missing])
        assert str(missing) not in session._mtime_snapshot
        assert str(missing) not in session._hash_snapshot
