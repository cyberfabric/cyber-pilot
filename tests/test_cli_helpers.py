"""
Unit tests for CLI helper functions.

Tests utility functions from fdd.utils.search, fdd.utils.markdown, and fdd.utils.document that perform parsing, filtering, and formatting.
"""

import unittest
import sys
import re
import json
import io
import contextlib
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "fdd" / "scripts"))

from fdd.utils.document import detect_artifact_kind, iter_text_files, read_text_safe, to_relative_posix
from fdd.utils.markdown import find_nearest_heading, get_heading_level
from fdd.utils.search import (
    extract_ids,
    filter_hits,
    find_all_positions,
    infer_fdd_type,
    parse_trace_query,
    _match_phase_inst_in_line,
    unique_hits,
)

from fdd import cli as fdd_cli


class TestParseTraceQuery(unittest.TestCase):
    """Test parse_trace_query function."""

    def test_parse_simple_base(self):
        """Test parsing simple base ID."""
        base, phase, inst = parse_trace_query("@fdd-test-flow-login")
        
        # Function strips @fdd- prefix when present
        self.assertIsNotNone(base)
        self.assertIsNone(phase)
        self.assertIsNone(inst)

    def test_parse_with_phase(self):
        """Test parsing with phase."""
        base, phase, inst = parse_trace_query("fdd-test-flow-login:ph-1")
        
        # Extracts phase correctly
        self.assertEqual(base, "fdd-test-flow-login")
        self.assertEqual(phase, "ph-1")
        self.assertIsNone(inst)

    def test_parse_with_phase_and_instruction(self):
        """Test parsing with phase and instruction."""
        base, phase, inst = parse_trace_query("fdd-test-flow-login:ph-1:inst-step-1")
        
        # Extracts both phase and instruction
        self.assertEqual(base, "fdd-test-flow-login")
        self.assertEqual(phase, "ph-1")
        self.assertEqual(inst, "inst-step-1")

    def test_parse_without_at_symbol(self):
        """Test parsing without @ symbol."""
        base, phase, inst = parse_trace_query("fdd-test-flow-login:ph-1")
        
        # Without @ it treats whole thing as base
        self.assertIsNotNone(base)
        self.assertIsNone(inst)

    def test_parse_unqualified_rest_is_treated_as_base(self):
        base, phase, inst = parse_trace_query("fdd-test-flow-login:foo")
        self.assertEqual(base, "foo")
        self.assertIsNone(phase)
        self.assertIsNone(inst)


class TestMatchPhaseInstInLine(unittest.TestCase):
    def test_match_returns_none_when_inst_precedes_phase(self):
        line = "inst-return-ok ph-1"
        matched = _match_phase_inst_in_line(line, phase="ph-1", inst="inst-return-ok")
        self.assertIsNone(matched)

    def test_match_phase_only(self):
        line = "1. [ ] - `ph-1` - **RETURN** ok - `inst-return-ok`"
        matched = _match_phase_inst_in_line(line, phase="ph-1", inst=None)
        self.assertIsNotNone(matched)
        assert matched is not None
        seg, _col = matched
        self.assertEqual(seg, "phase")


class TestExtractIds(unittest.TestCase):
    """Test extract_ids function."""

    def test_extract_single_id(self):
        """Test extracting single ID."""
        lines = ["Some text with `fdd-test-actor-user` in it"]
        
        ids = extract_ids(lines)
        
        self.assertGreater(len(ids), 0)
        self.assertEqual(ids[0]["id"], "fdd-test-actor-user")

    def test_extract_multiple_ids(self):
        """Test extracting multiple IDs."""
        lines = [
            "Actor: `fdd-test-actor-user`",
            "Capability: `fdd-test-capability-login`",
        ]
        
        ids = extract_ids(lines)
        
        self.assertGreaterEqual(len(ids), 2)

    def test_extract_with_columns(self):
        """Test extracting IDs with column numbers."""
        lines = ["Text `fdd-test-actor-user` more text"]
        
        ids = extract_ids(lines, with_cols=True)
        
        self.assertGreater(len(ids), 0)
        self.assertIn("col", ids[0])


class TestFilterIdHits(unittest.TestCase):
    """Test filter_hits function."""

    def test_filter_with_substring(self):
        """Test filtering with substring pattern."""
        hits = [
            {"id": "fdd-test-actor-user"},
            {"id": "fdd-test-actor-admin"},
            {"id": "fdd-test-capability-login"},
        ]
        
        filtered = filter_hits(hits, pattern="actor", regex=False)
        
        self.assertEqual(len(filtered), 2)

    def test_filter_with_regex(self):
        """Test filtering with regex pattern."""
        hits = [
            {"id": "fdd-test-actor-user"},
            {"id": "fdd-test-actor-admin"},
            {"id": "fdd-test-capability-login"},
        ]
        
        filtered = filter_hits(hits, pattern="actor-.*", regex=True)
        
        self.assertEqual(len(filtered), 2)

    def test_filter_no_pattern(self):
        """Test filtering with no pattern returns all."""
        hits = [
            {"id": "fdd-test-actor-user"},
            {"id": "fdd-test-capability-login"},
        ]
        
        filtered = filter_hits(hits, pattern=None, regex=False)
        
        self.assertEqual(len(filtered), 2)


class TestUniqueIdHits(unittest.TestCase):
    """Test unique_hits function."""

    def test_remove_duplicates(self):
        """Test removing duplicate IDs."""
        hits = [
            {"id": "fdd-test-actor-user", "line": 10},
            {"id": "fdd-test-actor-user", "line": 20},
            {"id": "fdd-test-capability-login", "line": 30},
        ]
        
        unique = unique_hits(hits)
        
        self.assertEqual(len(unique), 2)

    def test_preserve_order(self):
        """Test preserving first occurrence order."""
        hits = [
            {"id": "fdd-test-actor-admin", "line": 10},
            {"id": "fdd-test-actor-user", "line": 20},
            {"id": "fdd-test-actor-admin", "line": 30},
        ]
        
        unique = unique_hits(hits)
        
        self.assertEqual(len(unique), 2)
        self.assertEqual(unique[0]["id"], "fdd-test-actor-admin")
        self.assertEqual(unique[1]["id"], "fdd-test-actor-user")


class TestNearestHeadingTitle(unittest.TestCase):
    """Test find_nearest_heading function."""

    def test_find_nearest_heading(self):
        """Test finding nearest heading."""
        lines = [
            "# Main Title",
            "",
            "## Section A",
            "",
            "Some content",
            "More content",
        ]
        
        title = find_nearest_heading(lines, from_idx=5)
        
        self.assertEqual(title, "Section A")

    def test_find_parent_heading(self):
        """Test finding parent heading."""
        lines = [
            "# Main Title",
            "",
            "## Section A",
            "",
            "### Subsection",
            "Content",
        ]
        
        title = find_nearest_heading(lines, from_idx=5)
        
        self.assertEqual(title, "Subsection")

    def test_no_heading_found(self):
        """Test when no heading is found."""
        lines = [
            "Just some text",
            "No headings here",
        ]
        
        title = find_nearest_heading(lines, from_idx=1)
        
        self.assertIsNone(title)


class TestInferFddTypeFromId(unittest.TestCase):
    """Test infer_fdd_type function."""

    def test_infer_actor(self):
        """Test inferring actor type."""
        fdd_type = infer_fdd_type("fdd-test-actor-user")
        self.assertEqual(fdd_type, "actor")

    def test_infer_capability(self):
        """Test inferring capability type."""
        fdd_type = infer_fdd_type("fdd-test-capability-login")
        self.assertEqual(fdd_type, "capability")

    def test_infer_requirement(self):
        """Test inferring requirement type."""
        fdd_type = infer_fdd_type("fdd-test-req-001")
        self.assertEqual(fdd_type, "requirement")

    def test_infer_functional_requirement(self):
        fdd_type = infer_fdd_type("fdd-test-fr-login")
        self.assertEqual(fdd_type, "functional-requirement")

    def test_infer_usecase(self):
        """Test inferring usecase type."""
        fdd_type = infer_fdd_type("fdd-test-usecase-login")
        self.assertEqual(fdd_type, "usecase")

    def test_infer_principle(self):
        fdd_type = infer_fdd_type("fdd-test-principle-keep-it-simple")
        self.assertEqual(fdd_type, "principle")

    def test_infer_nfr(self):
        fdd_type = infer_fdd_type("fdd-test-nfr-latency")
        self.assertEqual(fdd_type, "nfr")

    def test_infer_prd_context(self):
        fdd_type = infer_fdd_type("fdd-test-prd-context-scope")
        self.assertEqual(fdd_type, "prd-context")

    def test_infer_constraint(self):
        fdd_type = infer_fdd_type("fdd-test-constraint-no-external-deps")
        self.assertEqual(fdd_type, "constraint")

    def test_infer_feature_scoped_types(self):
        self.assertEqual(infer_fdd_type("fdd-demo-feature-x-flow-login"), "flow")
        self.assertEqual(infer_fdd_type("fdd-demo-feature-x-algo-a"), "algo")
        self.assertEqual(infer_fdd_type("fdd-demo-feature-x-state-logged-in"), "state")
        self.assertEqual(infer_fdd_type("fdd-demo-feature-x-context-session"), "feature-context")
        self.assertEqual(infer_fdd_type("fdd-demo-feature-x-test-login"), "test")
        self.assertEqual(infer_fdd_type("fdd-demo-feature-x-req-login"), "feature-requirement")

    def test_infer_adr(self):
        """Test inferring ADR type."""
        fdd_type = infer_fdd_type("fdd-test-adr-0001")
        self.assertEqual(fdd_type, "adr")

    def test_infer_generic(self):
        """Test inferring generic ID type."""
        fdd_type = infer_fdd_type("fdd-test-something-else")
        self.assertEqual(fdd_type, "id")


class TestDetectKind(unittest.TestCase):
    """Test detect_artifact_kind function."""

    def test_detect_features_manifest(self):
        """Test detecting FEATURES.md."""
        path = Path("/test/FEATURES.md")
        kind = detect_artifact_kind(path)
        self.assertEqual(kind, "features-manifest")

    def test_detect_design(self):
        """Test detecting DESIGN.md."""
        path = Path("/test/DESIGN.md")
        kind = detect_artifact_kind(path)
        self.assertEqual(kind, "overall-design")

    def test_detect_feature_design(self):
        """Test detecting feature DESIGN.md."""
        path = Path("/test/architecture/features/feature-x/DESIGN.md")
        kind = detect_artifact_kind(path)
        self.assertEqual(kind, "feature-design")

    def test_detect_generic(self):
        """Test detecting generic file."""
        path = Path("/test/README.md")
        kind = detect_artifact_kind(path)
        self.assertEqual(kind, "generic")


class TestFindAllInLine(unittest.TestCase):
    """Test find_all_positions function."""

    def test_find_single_occurrence(self):
        """Test finding single occurrence."""
        positions = find_all_positions("Hello world", "world")
        
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0], 6)

    def test_find_multiple_occurrences(self):
        """Test finding multiple occurrences."""
        positions = find_all_positions("test test test", "test")
        
        self.assertEqual(len(positions), 3)
        self.assertEqual(positions, [0, 5, 10])

    def test_find_no_occurrences(self):
        """Test finding no occurrences."""
        positions = find_all_positions("Hello world", "xyz")
        
        self.assertEqual(len(positions), 0)


class TestRelativePosix(unittest.TestCase):
    """Test to_relative_posix function."""

    def test_relative_path_within_root(self):
        """Test relative path within root."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            subpath = root / "subdir" / "file.txt"
            
            rel = to_relative_posix(subpath, root)
            
            self.assertEqual(rel, "subdir/file.txt")

    def test_absolute_path_outside_root(self):
        """Test absolute path when outside root."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "root"
            outside = Path(tmpdir) / "outside" / "file.txt"
            
            rel = to_relative_posix(outside, root)
            
            # Should return absolute path when outside root
            self.assertIn("outside", rel)


class TestIterTextFiles(unittest.TestCase):
    def test_iter_text_files_include_exclude_and_max_bytes(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "a").mkdir()
            (root / "a" / "small.md").write_text("x\n", encoding="utf-8")
            (root / "a" / "big.md").write_text("x" * 200, encoding="utf-8")
            (root / "a" / "skip.md").write_text("x\n", encoding="utf-8")

            hits = iter_text_files(
                root,
                includes=["**/*.md"],
                excludes=["**/skip.md"],
                max_bytes=100,
            )
            rels = sorted([p.resolve().relative_to(root.resolve()).as_posix() for p in hits])
            self.assertEqual(rels, ["a/small.md"])

    def test_iter_text_files_relative_to_value_error_is_ignored(self):
        import os
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            orig_walk = os.walk

            def fake_walk(_root):
                yield ("/", [], ["outside.md"])

            os.walk = fake_walk
            try:
                hits = iter_text_files(root)
                self.assertEqual(hits, [])
            finally:
                os.walk = orig_walk


class TestReadTextSafe(unittest.TestCase):
    def test_read_text_safe_nonexistent_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "missing.txt"
            self.assertIsNone(read_text_safe(p))

    def test_read_text_safe_null_bytes_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "bin.txt"
            p.write_bytes(b"a\x00b")
            self.assertIsNone(read_text_safe(p))

    def test_read_text_safe_invalid_utf8_ignores(self):
        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "bad.txt"
            p.write_bytes(b"hi\xff\xfe")
            lines = read_text_safe(p)
            self.assertIsNotNone(lines)
            self.assertTrue(any("hi" in x for x in lines or []))

    def test_read_text_safe_normalizes_crlf_when_linesep_differs(self):
        import os

        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "crlf.txt"
            p.write_bytes(b"a\r\nb\r\n")

            orig = os.linesep
            try:
                os.linesep = "\r\n"
                lines = read_text_safe(p)
                self.assertEqual(lines, ["a", "b"])
            finally:
                os.linesep = orig


class TestHeadingLevel(unittest.TestCase):
    """Test get_heading_level function."""

    def test_level_1(self):
        """Test detecting level 1 heading."""
        level = get_heading_level("# Title")
        self.assertEqual(level, 1)

    def test_level_2(self):
        """Test detecting level 2 heading."""
        level = get_heading_level("## Section")
        self.assertEqual(level, 2)

    def test_level_3(self):
        """Test detecting level 3 heading."""
        level = get_heading_level("### Subsection")
        self.assertEqual(level, 3)

    def test_not_heading(self):
        """Test detecting non-heading line."""
        level = get_heading_level("Regular text")
        self.assertIsNone(level)

    def test_heading_with_spaces(self):
        """Test heading with extra spaces."""
        level = get_heading_level("####    Title with spaces")
        self.assertEqual(level, 4)


class TestCliInternalHelpers(unittest.TestCase):
    def test_truncate_list_non_list_returns_empty(self):
        self.assertEqual(fdd_cli._truncate_list({"a": 1}, 5), [])

    def test_truncate_list_negative_limit_returns_empty(self):
        self.assertEqual(fdd_cli._truncate_list([1, 2, 3], -1), [])

    def test_load_json_file_invalid_json_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "bad.json"
            p.write_text("{bad}", encoding="utf-8")
            self.assertIsNone(fdd_cli._load_json_file(p))

    def test_load_json_file_non_dict_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "list.json"
            p.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
            self.assertIsNone(fdd_cli._load_json_file(p))

    def test_safe_relpath_from_dir_fallbacks_to_absolute_on_error(self):
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            target = base / "x" / "y"
            with patch("os.path.relpath", side_effect=Exception("boom")):
                rel = fdd_cli._safe_relpath_from_dir(target, base)
            self.assertEqual(rel, target.as_posix())

    def test_prompt_path_eof_returns_default(self):
        with patch("builtins.input", side_effect=EOFError()):
            out = fdd_cli._prompt_path("Q?", "default")
        self.assertEqual(out, "default")

    def test_safe_relpath_outside_base_returns_absolute(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "root"
            other = Path(tmpdir) / "other" / "x.txt"
            out = fdd_cli._safe_relpath(other, root)
            self.assertEqual(out, other.as_posix())

    def test_write_json_file_writes_trailing_newline(self):
        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "out.json"
            fdd_cli._write_json_file(p, {"a": 1})
            raw = p.read_text(encoding="utf-8")
            self.assertTrue(raw.endswith("\n"))
            self.assertEqual(json.loads(raw), {"a": 1})

    def test_summarize_validate_report_includes_failure_details(self):
        report = {
            "status": "FAIL",
            "path": "/tmp/x",
            "errors": [{"type": "x", "message": "m"}],
            "artifact_validation": {
                "a": {
                    "status": "FAIL",
                    "errors": [{"type": "e", "message": "e"}],
                    "missing_sections": ["A"],
                    "adr_issues": [{"type": "adr", "message": "m"}],
                    "placeholder_hits": ["TODO"],
                    "path": "p",
                },
                "b": {"status": "PASS"},
                "c": "not-a-dict",
            },
            "traceability": {
                "feature_dir": "f",
                "scan_root": "r",
                "feature_design": "d",
                "scanned_file_count": 1,
                "missing": {
                    "scopes": {"flows": ["x"], "algos": []},
                    "instruction_tags": ["@fdd-algo:x:ph-1"],
                },
            },
        }
        out = fdd_cli._summarize_validate_report(report)
        self.assertEqual(out.get("status"), "FAIL")
        self.assertIn("error_count", out)
        self.assertIn("artifact_validation", out)
        self.assertIn("artifact_failures", out)
        self.assertIn("traceability", out)

    def test_summarize_validate_report_summarizes_feature_reports(self):
        report = {
            "status": "FAIL",
            "feature_dir": "/tmp/feature-dir",
            "feature_count": 4,
            "feature_reports": [
                "not-a-dict",
                {
                    "status": "PASS",
                    "feature_dir": "feature-a",
                },
                {
                    "status": "FAIL",
                    "feature_dir": "feature-b",
                    "errors": [{"type": "e", "message": "m"}],
                    "traceability": {
                        "feature_dir": "feature-b",
                        "scan_root": ".",
                        "feature_design": "DESIGN.md",
                        "scanned_file_count": 2,
                        "missing": {
                            "scopes": {"flows": ["x", "y"], "algos": []},
                            "instruction_tags": ["@fdd-algo:x:ph-1"],
                        },
                    },
                },
                {
                    "status": "FAIL",
                    "feature_dir": "feature-c",
                    "errors": [],
                    "traceability": "not-a-dict",
                },
            ],
        }

        out = fdd_cli._summarize_validate_report(report)
        self.assertEqual(out.get("status"), "FAIL")
        self.assertEqual(out.get("feature_dir"), "/tmp/feature-dir")

        fr = out.get("feature_reports")
        self.assertIsInstance(fr, dict)
        self.assertEqual(fr.get("feature_count"), 4)
        self.assertEqual(fr.get("pass_count"), 1)
        self.assertEqual(fr.get("fail_count"), 2)
        self.assertIsInstance(fr.get("failures"), list)


class TestCliAgentWorkflowsCoverage(unittest.TestCase):
    def test_agent_workflows_unknown_agent_requires_config(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".fdd-config.json").write_text("{}\n", encoding="utf-8")

            rc = fdd_cli.main(["agent-workflows", "--agent", "myagent", "--root", str(root), "--dry-run"])
            self.assertEqual(rc, 2)


class TestSearchModuleExtraCoverage(unittest.TestCase):
    def test_list_ids_applies_base_offset(self):
        from fdd.utils.search import list_ids

        hits = list_ids(
            lines=["**ID**: `fdd-test-actor-user`"],
            base_offset=5,
            pattern=None,
            regex=False,
            all_ids=True,
        )
        self.assertEqual(hits[0]["line"], 6)

    def test_scan_ids_handles_regex_with_escaped_backslashes(self):
        from fdd.utils.search import scan_ids

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "a.md").write_text("`fdd-test-actor-123`\n", encoding="utf-8")
            hits = scan_ids(
                root=root,
                pattern="fdd-test-actor-\\\\d+",
                regex=True,
                kind="all",
                include=["*.md"],
                exclude=None,
                max_bytes=1_000_000,
                all_ids=False,
            )
            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0]["id"], "fdd-test-actor-123")

    def test_where_used_excludes_definition_line(self):
        from fdd.utils.search import where_used

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "architecture").mkdir()
            (root / "architecture" / "DESIGN.md").write_text(
                "## B. Requirements\n\n- **ID**: `fdd-test-req-login`\n",
                encoding="utf-8",
            )
            (root / "src").mkdir()
            (root / "src" / "x.py").write_text(
                "# @fdd-req:fdd-test-req-login:ph-1\n",
                encoding="utf-8",
            )

            base, phase, inst, hits = where_used(
                root=root,
                raw_id="fdd-test-req-login",
                include=["**/*.md", "**/*.py"],
                exclude=None,
                max_bytes=1_000_000,
            )
            self.assertEqual(base, "fdd-test-req-login")
            self.assertIsNone(phase)
            self.assertIsNone(inst)
            self.assertEqual(len(hits), 1)
            self.assertTrue(str(hits[0]["path"]).endswith("src/x.py"))

    def test_search_lines_regex_branch(self):
        from fdd.utils.search import search_lines

        hits = search_lines(lines=["foo1", "bar"], query=r"foo\d+", regex=True)
        self.assertEqual(len(hits), 1)


class TestCliCommandCoverage(unittest.TestCase):
    def test_main_missing_subcommand_returns_error(self):
        rc = fdd_cli.main([])
        self.assertEqual(rc, 1)

    def test_main_unknown_command_returns_error(self):
        rc = fdd_cli.main(["does-not-exist"]) 
        self.assertEqual(rc, 1)

    def test_list_ids_under_heading_not_found_returns_1(self):
        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "doc.md"
            p.write_text("# Title\n\nText `fdd-demo-actor-user`\n", encoding="utf-8")
            rc = fdd_cli.main(["list-ids", "--artifact", str(p), "--under-heading", "Missing"])
            self.assertEqual(rc, 1)

    def test_read_section_feature_id_wrong_kind_returns_1(self):
        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "DESIGN.md"
            p.write_text("# Design\n", encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = fdd_cli.main(["read-section", "--artifact", str(p), "--feature-id", "fdd-demo-feature-x"])
            self.assertEqual(rc, 1)
            self.assertIn("\"status\": \"ERROR\"", buf.getvalue())

    def test_read_section_section_not_found_returns_1(self):
        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "PRD.md"
            p.write_text("# PRD\n", encoding="utf-8")
            rc = fdd_cli.main(["read-section", "--artifact", str(p), "--section", "Z"])
            self.assertEqual(rc, 1)

    def test_where_defined_not_found_returns_1(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "README.md").write_text("hello\n", encoding="utf-8")
            rc = fdd_cli.main(["where-defined", "--id", "fdd-demo-req-missing", "--root", str(root)])
            self.assertEqual(rc, 1)

    def test_agent_workflows_deletes_stale_proxy_pointing_to_missing_workflow(self):
        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / ".fdd-config.json").write_text("{}\n", encoding="utf-8")
            wf_dir = project_root / "wf"
            wf_dir.mkdir(parents=True, exist_ok=True)

            repo_root = Path(__file__).parent.parent
            missing_target = (repo_root / "workflows" / "does-not-exist.md").resolve()
            stale = wf_dir / "fdd-stale.md"
            stale.write_text(
                "# /fdd-stale\n\nALWAYS open and follow `" + missing_target.as_posix() + "`\n",
                encoding="utf-8",
            )

            cfg = {
                "version": 1,
                "agents": {
                    "windsurf": {
                        "workflow_dir": "wf",
                        "workflow_command_prefix": "fdd-",
                        "workflow_filename_format": "{command}.md",
                        "template": [
                            "# /{command}\n",
                            "\n",
                            "ALWAYS open and follow `{target_workflow_path}`\n",
                        ],
                    }
                },
            }
            cfg_path = project_root / "fdd-agent-workflows.json"
            cfg_path.write_text(json.dumps(cfg), encoding="utf-8")

            rc = fdd_cli.main([
                "agent-workflows",
                "--agent",
                "windsurf",
                "--root",
                str(project_root),
                "--config",
                str(cfg_path),
                "--fdd-root",
                str(repo_root),
            ])
            self.assertEqual(rc, 0)
            self.assertFalse(stale.exists())

    def test_agent_skills_legacy_invalid_template_returns_2(self):
        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / ".fdd-config.json").write_text("{}\n", encoding="utf-8")
            cfg = {
                "version": 1,
                "agents": {
                    "windsurf": {
                        "skills_dir": ".windsurf/skills",
                        "skill_name": "fdd",
                        "template": "not-a-list",
                    }
                },
            }
            cfg_path = project_root / "fdd-agent-skills.json"
            cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
            rc = fdd_cli.main([
                "agent-skills",
                "--agent",
                "windsurf",
                "--root",
                str(project_root),
                "--config",
                str(cfg_path),
                "--dry-run",
            ])
            self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
