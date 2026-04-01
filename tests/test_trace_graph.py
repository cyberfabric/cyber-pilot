"""Tests for trace_graph.py — P1: Structural Anchoring + Content Hashing."""
import textwrap
from pathlib import Path

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "cypilot", "scripts"))

from cypilot.utils.trace_graph import (
    AnchoredHit,
    StructuralAnchor,
    build_doc_anchored_hits,
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
