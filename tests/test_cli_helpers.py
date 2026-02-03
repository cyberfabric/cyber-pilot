"""
Unit tests for CLI helper functions.

Tests utility functions from spider.utils.document that perform parsing, filtering, and formatting.
"""

import unittest
import sys
import json
import io
import contextlib
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "spider" / "scripts"))

from spider.utils.document import detect_artifact_kind, iter_text_files, read_text_safe, to_relative_posix

from spider import cli as spider_cli


class TestDetectKind(unittest.TestCase):
    """Test detect_artifact_kind function."""

    def test_detect_features_manifest(self):
        """Test detecting DECOMPOSITION.md."""
        path = Path("/test/DECOMPOSITION.md")
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


class TestCliInternalHelpers(unittest.TestCase):
    def test_load_json_file_invalid_json_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "bad.json"
            p.write_text("{bad}", encoding="utf-8")
            self.assertIsNone(spider_cli._load_json_file(p))

    def test_load_json_file_non_dict_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "list.json"
            p.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
            self.assertIsNone(spider_cli._load_json_file(p))

    def test_safe_relpath_from_dir_fallbacks_to_absolute_on_error(self):
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            target = base / "x" / "y"
            with patch("os.path.relpath", side_effect=Exception("boom")):
                rel = spider_cli._safe_relpath_from_dir(target, base)
            self.assertEqual(rel, target.as_posix())

    def test_prompt_path_eof_returns_default(self):
        with patch("builtins.input", side_effect=EOFError()):
            out = spider_cli._prompt_path("Q?", "default")
        self.assertEqual(out, "default")

    def test_safe_relpath_outside_base_returns_absolute(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "root"
            other = Path(tmpdir) / "other" / "x.txt"
            out = spider_cli._safe_relpath(other, root)
            self.assertEqual(out, other.as_posix())

    def test_write_json_file_writes_trailing_newline(self):
        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "out.json"
            spider_cli._write_json_file(p, {"a": 1})
            raw = p.read_text(encoding="utf-8")
            self.assertTrue(raw.endswith("\n"))
            self.assertEqual(json.loads(raw), {"a": 1})


class TestCliCommandCoverage(unittest.TestCase):
    def test_self_check_project_root_not_found(self):
        with TemporaryDirectory() as td:
            with patch.object(spider_cli, "find_project_root", return_value=None):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    code = spider_cli._cmd_self_check(["--root", td])
        self.assertEqual(code, 1)

    def test_self_check_adapter_dir_not_found(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            with patch.object(spider_cli, "find_project_root", return_value=root):
                with patch.object(spider_cli, "find_adapter_directory", return_value=None):
                    buf = io.StringIO()
                    with contextlib.redirect_stdout(buf):
                        code = spider_cli._cmd_self_check(["--root", td])
        self.assertEqual(code, 1)

    def test_self_check_registry_no_rules(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            adapter = root / ".spider-adapter"
            adapter.mkdir()
            with patch.object(spider_cli, "find_project_root", return_value=root):
                with patch.object(spider_cli, "find_adapter_directory", return_value=adapter):
                    with patch.object(spider_cli, "load_artifacts_registry", return_value=({"version": "1.0"}, None)):
                        buf = io.StringIO()
                        with contextlib.redirect_stdout(buf):
                            code = spider_cli._cmd_self_check(["--root", td])
        self.assertEqual(code, 1)

    def test_self_check_with_rules_structure(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            adapter = root / ".spider-adapter"
            adapter.mkdir()
            # Create rules structure
            weavers_dir = root / "weavers" / "test" / "artifacts" / "PRD"
            weavers_dir.mkdir(parents=True)
            (weavers_dir / "template.md").write_text(
                "---\n"
                "spider-template:\n  version:\n    major: 1\n    minor: 0\n  kind: PRD\n"
                "---\n\n# PRD\n",
                encoding="utf-8",
            )
            # No example - should warn but pass (no examples = no failures)
            registry = {
                "version": "1.0",
                "weavers": {
                    "test-rules": {"format": "Spider", "path": "weavers/test"}
                },
            }
            with patch.object(spider_cli, "find_project_root", return_value=root):
                with patch.object(spider_cli, "find_adapter_directory", return_value=adapter):
                    with patch.object(spider_cli, "load_artifacts_registry", return_value=(registry, None)):
                        buf = io.StringIO()
                        with contextlib.redirect_stdout(buf):
                            code = spider_cli._cmd_self_check(["--root", td])
        # PASS when no examples exist (warnings only)
        self.assertEqual(code, 0)

    def test_init_yes_dry_run(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = spider_cli.main(["init", "--project-root", str(root), "--yes", "--dry-run"])
        self.assertEqual(rc, 0)

    def test_main_missing_subcommand_returns_error(self):
        rc = spider_cli.main([])
        self.assertEqual(rc, 1)

    def test_main_unknown_command_returns_error(self):
        rc = spider_cli.main(["does-not-exist"])
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()