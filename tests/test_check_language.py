"""Tests for the check-language CLI command.

Covers:
- cmd_check_language() — argument parsing, exit codes
- _human_result() — human formatter
- _count_md_files() — file counting helper
- _default_roots() — fallback root resolution
- _read_config_languages() — config-driven language loading
"""

import sys
import io
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.commands.check_language import (
    cmd_check_language,
    _count_md_files,
    _default_roots,
    _human_result,
    _read_config_languages,
    _read_config_ignore_patterns,
)


def _run(argv, capture=True):
    """Execute cmd_check_language, suppressing all output by default."""
    if capture:
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cmd_check_language(argv)
        return code, out.getvalue(), err.getvalue()
    return cmd_check_language(argv), "", ""


class TestCmdCheckLanguagePassCases(unittest.TestCase):
    """cmd_check_language() returns 0 for clean English files."""

    def setUp(self):
        self._tmpdir = TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _md(self, name: str, content: str):
        p = self.root / name
        p.write_text(content, encoding="utf-8")
        return p

    def test_english_file_passes(self):
        p = self._md("doc.md", "# Title\n\nHello world.\n")
        code, _, _ = _run(["--languages", "en", str(p)])
        self.assertEqual(code, 0)

    def test_empty_directory_passes(self):
        empty = self.root / "empty"
        empty.mkdir()
        code, _, _ = _run(["--languages", "en", str(empty)])
        self.assertEqual(code, 0)

    def test_bilingual_file_passes_with_both_langs(self):
        p = self._md("bi.md", "Hello\nПривет\n")
        code, _, _ = _run(["--languages", "en,ru", str(p)])
        self.assertEqual(code, 0)

    def test_quiet_flag_does_not_change_exit_code(self):
        p = self._md("clean.md", "Clean English.\n")
        code, _, _ = _run(["--languages", "en", "--quiet", str(p)])
        self.assertEqual(code, 0)


class TestCmdCheckLanguageViolations(unittest.TestCase):
    """cmd_check_language() returns 2 when violations are found."""

    def setUp(self):
        self._tmpdir = TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _md(self, name: str, content: str):
        p = self.root / name
        p.write_text(content, encoding="utf-8")
        return p

    def test_cyrillic_in_english_doc_returns_2(self):
        p = self._md("doc.md", "# Title\n\nПривет мир\n")
        code, _, _ = _run(["--languages", "en", str(p)])
        self.assertEqual(code, 2)

    def test_multiple_violations_still_return_2(self):
        p = self._md("doc.md", "Строка 1\nСтрока 2\n")
        code, _, _ = _run(["--languages", "en", str(p)])
        self.assertEqual(code, 2)

    def test_quiet_flag_with_violations_returns_2(self):
        p = self._md("doc.md", "Привет\n")
        code, _, _ = _run(["--languages", "en", "--quiet", str(p)])
        self.assertEqual(code, 2)


class TestCmdCheckLanguageErrors(unittest.TestCase):
    """cmd_check_language() returns 1 on configuration / path errors."""

    def setUp(self):
        self._tmpdir = TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_unknown_language_returns_1(self):
        code, _, _ = _run(["--languages", "xx_INVALID", str(self.root)])
        self.assertEqual(code, 1)

    def test_nonexistent_path_returns_1(self):
        missing = str(self.root / "no_such_path")
        code, _, _ = _run(["--languages", "en", missing])
        self.assertEqual(code, 1)

    def test_mixed_known_unknown_langs_returns_1(self):
        code, _, _ = _run(["--languages", "en,xx,yy", str(self.root)])
        self.assertEqual(code, 1)


class TestCountMdFiles(unittest.TestCase):
    """_count_md_files() correctly counts .md files."""

    def setUp(self):
        self._tmpdir = TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_count_single_md_file(self):
        p = self.root / "a.md"
        p.write_text("x")
        self.assertEqual(_count_md_files([p]), 1)

    def test_count_non_md_file_is_zero(self):
        p = self.root / "a.py"
        p.write_text("x")
        self.assertEqual(_count_md_files([p]), 0)

    def test_count_directory_recursive(self):
        sub = self.root / "sub"
        sub.mkdir()
        (sub / "a.md").write_text("x")
        (sub / "b.md").write_text("x")
        (sub / "c.py").write_text("x")
        self.assertEqual(_count_md_files([self.root]), 2)

    def test_empty_directory(self):
        self.assertEqual(_count_md_files([self.root]), 0)

    def test_multiple_roots(self):
        p1 = self.root / "a.md"
        p2 = self.root / "b.md"
        p1.write_text("x")
        p2.write_text("x")
        self.assertEqual(_count_md_files([p1, p2]), 2)


class TestDefaultRoots(unittest.TestCase):
    """_default_roots() returns fallback path when no context is set."""

    def test_no_context_falls_back_to_cwd(self):
        with patch("cypilot.utils.context.get_context", return_value=None):
            roots = _default_roots()
        self.assertIsInstance(roots, list)
        self.assertGreater(len(roots), 0)

    def test_with_context_returns_architecture_dir(self):
        mock_ctx = MagicMock()
        mock_ctx.project_root = Path("/fake/project")
        with patch("cypilot.utils.context.get_context", return_value=mock_ctx):
            roots = _default_roots()
        self.assertEqual(roots, [Path("/fake/project") / "architecture"])


class TestReadConfigLanguages(unittest.TestCase):
    """_read_config_languages() reads from workspace config or returns default."""

    def test_no_context_returns_default_english(self):
        with patch("cypilot.utils.context.get_context", return_value=None):
            langs = _read_config_languages()
        self.assertEqual(langs, ["en"])

    def test_workspace_config_error_raises_value_error(self):
        mock_ctx = MagicMock()
        mock_ctx.project_root = Path("/fake/project")
        with patch("cypilot.utils.context.get_context", return_value=mock_ctx):
            with patch("cypilot.utils.workspace.find_workspace_config", return_value=(None, "bad config")):
                with self.assertRaises(ValueError):
                    _read_config_languages()

    def test_no_workspace_config_returns_english(self):
        mock_ctx = MagicMock()
        mock_ctx.project_root = Path("/fake/project")
        with patch("cypilot.utils.context.get_context", return_value=mock_ctx):
            with patch("cypilot.utils.workspace.find_workspace_config", return_value=(None, None)):
                langs = _read_config_languages()
        self.assertEqual(langs, ["en"])

    def test_workspace_config_with_languages_returns_them(self):
        mock_ctx = MagicMock()
        mock_ctx.project_root = Path("/fake/project")
        mock_cfg = MagicMock()
        mock_cfg.validation = MagicMock()
        mock_cfg.validation.allowed_content_languages = ["en", "ru"]
        with patch("cypilot.utils.context.get_context", return_value=mock_ctx):
            with patch("cypilot.utils.workspace.find_workspace_config", return_value=(mock_cfg, None)):
                langs = _read_config_languages()
        self.assertEqual(langs, ["en", "ru"])

    def test_workspace_config_no_validation_returns_english(self):
        mock_ctx = MagicMock()
        mock_ctx.project_root = Path("/fake/project")
        mock_cfg = MagicMock()
        mock_cfg.validation = None
        with patch("cypilot.utils.context.get_context", return_value=mock_ctx):
            with patch("cypilot.utils.workspace.find_workspace_config", return_value=(mock_cfg, None)):
                langs = _read_config_languages()
        self.assertEqual(langs, ["en"])


class TestHumanResult(unittest.TestCase):
    """_human_result() renders output without raising exceptions."""

    def _capture(self, data, quiet=False):
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            _human_result(data, quiet=quiet)
        return out.getvalue() + err.getvalue()

    def test_pass_status_renders(self):
        data = {"status": "PASS", "allowed_languages": ["en"], "files_scanned": 3}
        output = self._capture(data)
        self.assertIsInstance(output, str)

    def test_fail_status_renders_violations(self):
        data = {
            "status": "FAIL",
            "allowed_languages": ["en"],
            "files_scanned": 1,
            "violation_count": 1,
            "file_count": 1,
            "violations": [
                {"path": "/tmp/doc.md", "line": 5, "chars": "Привет", "preview": "Привет мир"}
            ],
        }
        output = self._capture(data)
        self.assertIsInstance(output, str)

    def test_error_status_renders(self):
        data = {"status": "ERROR", "message": "Something went wrong"}
        output = self._capture(data)
        self.assertIsInstance(output, str)

    def test_quiet_mode_suppresses_header(self):
        data = {"status": "PASS", "allowed_languages": ["en"], "files_scanned": 0}
        output_normal = self._capture(data, quiet=False)
        output_quiet = self._capture(data, quiet=True)
        # Quiet mode should produce less or equal output
        self.assertLessEqual(len(output_quiet), len(output_normal))


class TestReadConfigIgnorePatterns(unittest.TestCase):
    """_read_config_ignore_patterns() reads ignore patterns from workspace config."""

    def test_no_context_returns_empty_list(self):
        with patch("cypilot.utils.context.get_context", return_value=None):
            patterns = _read_config_ignore_patterns()
        self.assertEqual(patterns, [])

    def test_workspace_config_error_raises_value_error(self):
        mock_ctx = MagicMock()
        mock_ctx.project_root = Path("/fake/project")
        with patch("cypilot.utils.context.get_context", return_value=mock_ctx):
            with patch(
                "cypilot.utils.workspace.find_workspace_config",
                return_value=(None, "bad config"),
            ):
                with self.assertRaises(ValueError):
                    _read_config_ignore_patterns()

    def test_workspace_config_with_ignore_paths_returns_them(self):
        mock_ctx = MagicMock()
        mock_ctx.project_root = Path("/fake/project")
        mock_cfg = MagicMock()
        mock_cfg.validation = MagicMock()
        mock_cfg.validation.ignore_paths = ["docs/translations/**", "*.i18n.md"]
        with patch("cypilot.utils.context.get_context", return_value=mock_ctx):
            with patch(
                "cypilot.utils.workspace.find_workspace_config",
                return_value=(mock_cfg, None),
            ):
                patterns = _read_config_ignore_patterns()
        self.assertEqual(patterns, ["docs/translations/**", "*.i18n.md"])

    def test_no_workspace_config_returns_empty_list(self):
        mock_ctx = MagicMock()
        mock_ctx.project_root = Path("/fake/project")
        with patch("cypilot.utils.context.get_context", return_value=mock_ctx):
            with patch(
                "cypilot.utils.workspace.find_workspace_config",
                return_value=(None, None),
            ):
                patterns = _read_config_ignore_patterns()
        self.assertEqual(patterns, [])


class TestDefaultRootsExceptionBranch(unittest.TestCase):
    """_default_roots() falls back to cwd when get_context raises."""

    def test_import_error_falls_back_to_cwd(self):
        with patch("cypilot.utils.context.get_context", side_effect=ImportError("no module")):
            roots = _default_roots()
        self.assertIsInstance(roots, list)
        self.assertGreater(len(roots), 0)

    def test_attribute_error_falls_back_to_cwd(self):
        with patch("cypilot.utils.context.get_context", side_effect=AttributeError("no attr")):
            roots = _default_roots()
        self.assertIsInstance(roots, list)
        self.assertGreater(len(roots), 0)


class TestCmdCheckLanguageConfigErrors(unittest.TestCase):
    """cmd_check_language() returns 1 when config loading fails."""

    def setUp(self):
        self._tmpdir = TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_config_language_error_returns_1(self):
        with patch(
            "cypilot.commands.check_language._read_config_languages",
            side_effect=ValueError("bad config"),
        ):
            code, _, _ = _run([str(self.root)])
        self.assertEqual(code, 1)

    def test_config_ignore_patterns_error_returns_1(self):
        with patch(
            "cypilot.commands.check_language._read_config_languages",
            return_value=["en"],
        ):
            with patch(
                "cypilot.commands.check_language._read_config_ignore_patterns",
                side_effect=ValueError("bad ignore config"),
            ):
                code, _, _ = _run([str(self.root)])
        self.assertEqual(code, 1)

    def test_lang_scan_error_returns_1(self):
        from cypilot.utils.content_language import LangScanError
        with patch(
            "cypilot.utils.content_language.scan_paths",
            side_effect=LangScanError(Path("/fake/file.md"), OSError("perm denied")),
        ):
            code, _, _ = _run(["--languages", "en", str(self.root)])
        self.assertEqual(code, 1)

    def test_no_paths_uses_default_roots(self):
        arch = self.root / "architecture"
        arch.mkdir()
        with patch(
            "cypilot.commands.check_language._default_roots",
            return_value=[arch],
        ):
            with patch(
                "cypilot.commands.check_language._read_config_languages",
                return_value=["en"],
            ):
                with patch(
                    "cypilot.commands.check_language._read_config_ignore_patterns",
                    return_value=[],
                ):
                    code, _, _ = _run([])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
