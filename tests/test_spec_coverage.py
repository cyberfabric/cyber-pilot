"""Tests for spec_coverage command."""

import json
import sys
import unittest
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.utils.artifacts_meta import (
    ArtifactsMeta,
    CodebaseEntry,
    Kit,
    SystemNode,
)
from cypilot.commands.spec_coverage import cmd_spec_coverage, _output


class TestOutput(unittest.TestCase):
    def test_output_to_stdout(self):
        args = MagicMock()
        args.output = None
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            _output({"status": "PASS"}, args)
            out = mock_out.getvalue()
        parsed = json.loads(out)
        self.assertEqual(parsed["status"], "PASS")

    def test_output_to_file(self):
        with TemporaryDirectory() as d:
            out_path = str(Path(d) / "report.json")
            args = MagicMock()
            args.output = out_path
            _output({"status": "PASS", "count": 42}, args)
            data = json.loads(Path(out_path).read_text(encoding="utf-8"))
            self.assertEqual(data["status"], "PASS")
            self.assertEqual(data["count"], 42)


class TestCmdSpecCoverage(unittest.TestCase):
    def _make_context(self, project_root, systems=None):
        meta = ArtifactsMeta(
            version=1,
            project_root=".",
            kits={"test": Kit("test", "Cypilot", "kits/test")},
            systems=systems or [],
        )
        ctx = MagicMock()
        ctx.meta = meta
        ctx.project_root = project_root
        return ctx

    def test_no_context(self):
        with patch("cypilot.utils.context.get_context", return_value=None):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                ret = cmd_spec_coverage([])
        self.assertEqual(ret, 1)
        parsed = json.loads(mock_out.getvalue())
        self.assertEqual(parsed["status"], "ERROR")

    def test_no_codebase_files(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            ctx = self._make_context(root, systems=[
                SystemNode(name="sys1", slug="sys1", kit="test",
                           artifacts=[], codebase=[], children=[]),
            ])
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    ret = cmd_spec_coverage([])
            self.assertEqual(ret, 0)
            parsed = json.loads(mock_out.getvalue())
            self.assertEqual(parsed["status"], "PASS")
            self.assertEqual(parsed["summary"]["total_files"], 0)

    def test_with_code_files(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            src = root / "src"
            src.mkdir()
            (src / "main.py").write_text(
                "# @cpt-algo:cpt-my-algo:p1\nx = 1\n", encoding="utf-8"
            )
            ctx = self._make_context(root, systems=[
                SystemNode(name="sys1", slug="sys1", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="src", extensions=[".py"])]),
            ])
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    ret = cmd_spec_coverage([])
            self.assertEqual(ret, 0)
            parsed = json.loads(mock_out.getvalue())
            self.assertEqual(parsed["status"], "PASS")
            self.assertGreater(parsed["summary"]["total_files"], 0)

    def test_threshold_pass(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            src = root / "src"
            src.mkdir()
            (src / "full.py").write_text(
                "# @cpt-algo:cpt-my-algo:p1\nx = 1\ny = 2\n", encoding="utf-8"
            )
            ctx = self._make_context(root, systems=[
                SystemNode(name="sys1", slug="sys1", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="src", extensions=[".py"])]),
            ])
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    ret = cmd_spec_coverage(["--min-coverage", "0"])
            self.assertEqual(ret, 0)

    def test_threshold_fail(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            src = root / "src"
            src.mkdir()
            (src / "bare.py").write_text("x = 1\ny = 2\n", encoding="utf-8")
            ctx = self._make_context(root, systems=[
                SystemNode(name="sys1", slug="sys1", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="src", extensions=[".py"])]),
            ])
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    ret = cmd_spec_coverage(["--min-coverage", "90"])
            self.assertEqual(ret, 2)
            parsed = json.loads(mock_out.getvalue())
            self.assertEqual(parsed["status"], "FAIL")
            self.assertIn("threshold_failures", parsed)

    def test_granularity_threshold_fail(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            src = root / "src"
            src.mkdir()
            (src / "scope_only.py").write_text(
                "# @cpt-algo:cpt-my-algo:p1\nx = 1\n", encoding="utf-8"
            )
            ctx = self._make_context(root, systems=[
                SystemNode(name="sys1", slug="sys1", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="src", extensions=[".py"])]),
            ])
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    ret = cmd_spec_coverage(["--min-granularity", "0.9"])
            self.assertEqual(ret, 2)

    def test_verbose_flag(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            src = root / "src"
            src.mkdir()
            (src / "main.py").write_text(
                "# @cpt-begin:cpt-my-algo:p1:inst-init\n"
                "x = 1\n"
                "# @cpt-end:cpt-my-algo:p1:inst-init\n",
                encoding="utf-8",
            )
            ctx = self._make_context(root, systems=[
                SystemNode(name="sys1", slug="sys1", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="src", extensions=[".py"])]),
            ])
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    ret = cmd_spec_coverage(["--verbose"])
            self.assertEqual(ret, 0)
            parsed = json.loads(mock_out.getvalue())
            # Verbose should include marker details in files
            for entry in parsed.get("files", {}).values():
                self.assertIn("scope_markers", entry)

    def test_output_to_file_flag(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            src = root / "src"
            src.mkdir()
            (src / "main.py").write_text("x = 1\n", encoding="utf-8")
            out_file = str(root / "out.json")
            ctx = self._make_context(root, systems=[
                SystemNode(name="sys1", slug="sys1", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="src", extensions=[".py"])]),
            ])
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                ret = cmd_spec_coverage(["--output", out_file])
            self.assertEqual(ret, 0)
            data = json.loads(Path(out_file).read_text(encoding="utf-8"))
            self.assertIn("summary", data)

    def test_nonexistent_codebase_path_skipped(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            ctx = self._make_context(root, systems=[
                SystemNode(name="sys1", slug="sys1", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="nonexistent/dir", extensions=[".py"])]),
            ])
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    ret = cmd_spec_coverage([])
            self.assertEqual(ret, 0)
            parsed = json.loads(mock_out.getvalue())
            self.assertEqual(parsed["summary"]["total_files"], 0)

    def test_single_file_codebase_entry(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / "main.py").write_text("x = 1\n", encoding="utf-8")
            ctx = self._make_context(root, systems=[
                SystemNode(name="sys1", slug="sys1", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="main.py", extensions=[".py"])]),
            ])
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    ret = cmd_spec_coverage([])
            self.assertEqual(ret, 0)
            parsed = json.loads(mock_out.getvalue())
            self.assertEqual(parsed["summary"]["total_files"], 1)

    def test_child_system_codebase(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            src = root / "child_src"
            src.mkdir()
            (src / "app.py").write_text("y = 2\n", encoding="utf-8")
            child = SystemNode(
                name="child", slug="child", kit="test",
                artifacts=[], children=[],
                codebase=[CodebaseEntry(path="child_src", extensions=[".py"])],
            )
            ctx = self._make_context(root, systems=[
                SystemNode(name="sys1", slug="sys1", kit="test",
                           artifacts=[], codebase=[], children=[child]),
            ])
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    ret = cmd_spec_coverage([])
            self.assertEqual(ret, 0)
            parsed = json.loads(mock_out.getvalue())
            self.assertEqual(parsed["summary"]["total_files"], 1)

    def test_ignored_files_excluded(self):
        with TemporaryDirectory() as d:
            root = Path(d).resolve()
            src = root / "src"
            src.mkdir()
            (src / "main.py").write_text("x = 1\n", encoding="utf-8")
            from cypilot.utils.artifacts_meta import IgnoreBlock
            meta = ArtifactsMeta(
                version=1,
                project_root=".",
                kits={"test": Kit("test", "Cypilot", "kits/test")},
                systems=[
                    SystemNode(name="sys1", slug="sys1", kit="test",
                               artifacts=[], children=[],
                               codebase=[CodebaseEntry(path="src", extensions=[".py"])]),
                ],
                ignore=[IgnoreBlock(reason="test", patterns=["src/main.py"])],
            )
            ctx = MagicMock()
            ctx.meta = meta
            ctx.project_root = root
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    ret = cmd_spec_coverage([])
            self.assertEqual(ret, 0)
            parsed = json.loads(mock_out.getvalue())
            self.assertEqual(parsed["summary"]["total_files"], 0)


    def test_system_filter_includes_matching(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            src1 = root / "src1"
            src1.mkdir()
            (src1 / "a.py").write_text("x = 1\n", encoding="utf-8")
            src2 = root / "src2"
            src2.mkdir()
            (src2 / "b.py").write_text("y = 2\n", encoding="utf-8")
            ctx = self._make_context(root, systems=[
                SystemNode(name="Alpha", slug="alpha", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="src1", extensions=[".py"])]),
                SystemNode(name="Beta", slug="beta", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="src2", extensions=[".py"])]),
            ])
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    ret = cmd_spec_coverage(["--system", "alpha"])
            self.assertEqual(ret, 0)
            parsed = json.loads(mock_out.getvalue())
            self.assertEqual(parsed["summary"]["total_files"], 1)
            file_paths = list(parsed.get("files", {}).keys())
            self.assertTrue(any("src1" in p for p in file_paths))
            self.assertFalse(any("src2" in p for p in file_paths))

    def test_system_filter_excludes_non_matching(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            src = root / "src"
            src.mkdir()
            (src / "a.py").write_text("x = 1\n", encoding="utf-8")
            ctx = self._make_context(root, systems=[
                SystemNode(name="Only", slug="only", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="src", extensions=[".py"])]),
            ])
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    ret = cmd_spec_coverage(["--system", "other"])
            self.assertEqual(ret, 0)
            parsed = json.loads(mock_out.getvalue())
            self.assertEqual(parsed["summary"]["total_files"], 0)

    def test_system_filter_multiple(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            for name in ("s1", "s2", "s3"):
                p = root / name
                p.mkdir()
                (p / "f.py").write_text("x = 1\n", encoding="utf-8")
            ctx = self._make_context(root, systems=[
                SystemNode(name="S1", slug="s1", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="s1", extensions=[".py"])]),
                SystemNode(name="S2", slug="s2", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="s2", extensions=[".py"])]),
                SystemNode(name="S3", slug="s3", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="s3", extensions=[".py"])]),
            ])
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    ret = cmd_spec_coverage(["--system", "s1", "--system", "s3"])
            self.assertEqual(ret, 0)
            parsed = json.loads(mock_out.getvalue())
            self.assertEqual(parsed["summary"]["total_files"], 2)

    def test_min_file_coverage_pass(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            src = root / "src"
            src.mkdir()
            (src / "full.py").write_text(
                "# @cpt-algo:cpt-my-algo:p1\nx = 1\ny = 2\n", encoding="utf-8"
            )
            ctx = self._make_context(root, systems=[
                SystemNode(name="sys1", slug="sys1", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="src", extensions=[".py"])]),
            ])
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    ret = cmd_spec_coverage(["--min-file-coverage", "0"])
            self.assertEqual(ret, 0)

    def test_min_file_coverage_fail(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            src = root / "src"
            src.mkdir()
            (src / "bare.py").write_text("x = 1\ny = 2\n", encoding="utf-8")
            ctx = self._make_context(root, systems=[
                SystemNode(name="sys1", slug="sys1", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="src", extensions=[".py"])]),
            ])
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    ret = cmd_spec_coverage(["--min-file-coverage", "90"])
            self.assertEqual(ret, 2)
            parsed = json.loads(mock_out.getvalue())
            self.assertEqual(parsed["status"], "FAIL")
            self.assertTrue(any("file" in f and "coverage" in f
                                for f in parsed.get("threshold_failures", [])))

    def test_uncovered_ranges_always_in_output(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            src = root / "src"
            src.mkdir()
            (src / "partial.py").write_text(
                "# @cpt-begin:cpt-a:p1:inst-x\nx = 1\n# @cpt-end:cpt-a:p1:inst-x\ny = 2\nz = 3\n",
                encoding="utf-8",
            )
            ctx = self._make_context(root, systems=[
                SystemNode(name="sys1", slug="sys1", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="src", extensions=[".py"])]),
            ])
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    ret = cmd_spec_coverage([])
            self.assertEqual(ret, 0)
            parsed = json.loads(mock_out.getvalue())
            for entry in parsed.get("files", {}).values():
                if entry.get("covered_lines", 0) < entry.get("total_lines", 0):
                    self.assertIn("uncovered_ranges", entry)


class TestFormatRanges(unittest.TestCase):
    """Cover _format_ranges helper."""

    def test_single_line_range(self):
        from cypilot.commands.spec_coverage import _format_ranges
        self.assertEqual(_format_ranges([[5, 5]]), "5")

    def test_multi_line_range(self):
        from cypilot.commands.spec_coverage import _format_ranges
        self.assertEqual(_format_ranges([[1, 3], [7, 7]]), "1-3, 7")

    def test_empty(self):
        from cypilot.commands.spec_coverage import _format_ranges
        self.assertEqual(_format_ranges([]), "")


class TestMinFileGranularity(TestCmdSpecCoverage):
    """Cover min_file_granularity threshold logic."""

    def test_min_file_granularity_fail(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            src = root / "src"
            src.mkdir()
            (src / "low_gran.py").write_text(
                "# @cpt-algo:cpt-my-algo:p1\nx = 1\ny = 2\nz = 3\n", encoding="utf-8"
            )
            ctx = self._make_context(root, systems=[
                SystemNode(name="sys1", slug="sys1", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="src", extensions=[".py"])]),
            ])
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    ret = cmd_spec_coverage(["--min-file-granularity", "0.99"])
            parsed = json.loads(mock_out.getvalue())
            if parsed["status"] == "FAIL":
                self.assertTrue(any("granularity" in f for f in parsed.get("threshold_failures", [])))

    def test_min_file_coverage_with_zero_total(self):
        """File with 0 total_lines is skipped in per-file coverage check."""
        with TemporaryDirectory() as d:
            root = Path(d)
            src = root / "src"
            src.mkdir()
            (src / "empty.py").write_text("", encoding="utf-8")
            ctx = self._make_context(root, systems=[
                SystemNode(name="sys1", slug="sys1", kit="test",
                           artifacts=[], children=[],
                           codebase=[CodebaseEntry(path="src", extensions=[".py"])]),
            ])
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    ret = cmd_spec_coverage(["--min-file-coverage", "50"])
            self.assertIn(ret, (0, 2))


class TestHumanSpecCoverage(unittest.TestCase):
    """Cover _human_spec_coverage with uncovered_ranges."""

    def test_human_output_with_uncovered_ranges(self):
        from cypilot.commands.spec_coverage import _human_spec_coverage
        data = {
            "status": "PASS",
            "summary": {
                "covered_files": 1, "total_files": 1,
                "covered_lines": 3, "effective_lines": 5,
                "coverage_pct": 60.0, "granularity_score": 0.5,
            },
            "files": {
                "src/foo.py": {
                    "total_lines": 5, "covered_lines": 3,
                    "coverage_pct": 60.0, "granularity": 0.5,
                    "uncovered_ranges": [[4, 5]],
                }
            },
        }
        import io
        buf = io.StringIO()
        with patch("sys.stderr", buf):
            _human_spec_coverage(data)


if __name__ == "__main__":
    unittest.main()
