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


if __name__ == "__main__":
    unittest.main()
