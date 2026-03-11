"""
Tests for utils/diff_engine.py — Resource Diff Engine.

Covers: DiffReport, show_file_diff.
"""

import io
import sys
import tempfile
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.utils.diff_engine import (
    DiffReport,
    show_file_diff,
)


# =========================================================================
# DiffReport
# =========================================================================

class TestDiffReport(unittest.TestCase):
    """DiffReport properties."""

    def test_has_changes_empty(self):
        r = DiffReport()
        self.assertFalse(r.has_changes)

    def test_has_changes_with_added(self):
        r = DiffReport(added=["a.md"])
        self.assertTrue(r.has_changes)


# =========================================================================
# show_file_diff
# =========================================================================

class TestShowFileDiff(unittest.TestCase):
    """show_file_diff prints unified diff to stderr."""

    def test_shows_diff(self):
        old = b"line1\nline2\n"
        new = b"line1\nmodified\n"
        buf = io.StringIO()
        with patch("sys.stderr", buf):
            show_file_diff("test.md", old, new)
        output = buf.getvalue()
        self.assertIn("line2", output)
        self.assertIn("modified", output)

    def test_binary_file(self):
        old = b"\x00\x01\x02"
        new = b"\x03\x04\x05"
        buf = io.StringIO()
        with patch("sys.stderr", buf):
            show_file_diff("binary.bin", old, new)
        output = buf.getvalue()
        self.assertIn("binary", output)

    def test_identical_files_silent(self):
        content = b"same\n"
        buf = io.StringIO()
        with patch("sys.stderr", buf):
            show_file_diff("same.md", content, content)
        self.assertEqual(buf.getvalue(), "")


# =========================================================================
# _open_editor_for_file
# =========================================================================

class TestOpenEditorForFile(unittest.TestCase):
    """Cover _open_editor_for_file helper."""

    def test_binary_content_returns_none(self):
        from cypilot.utils.diff_engine import _open_editor_for_file
        result = _open_editor_for_file("bin.dat", b"\x00\x01", b"\x02\x03")
        self.assertIsNone(result)

    def test_editor_not_found_returns_none(self):
        from cypilot.utils.diff_engine import _open_editor_for_file
        with patch.dict("os.environ", {"VISUAL": "nonexistent_editor_xyz", "EDITOR": "nonexistent_editor_xyz"}):
            result = _open_editor_for_file("test.md", b"old\n", b"new\n")
        self.assertIsNone(result)

    def test_successful_edit_resolved(self):
        """Editor resolves conflict markers → returns edited bytes."""
        from cypilot.utils.diff_engine import _open_editor_for_file

        def fake_editor(cmd):
            path = cmd[-1]
            # Resolve by writing content without conflict markers
            with open(path, "w") as f:
                f.write("manually edited\n")

        with patch("subprocess.check_call", side_effect=fake_editor):
            with patch.dict("os.environ", {"VISUAL": "cat"}):
                result = _open_editor_for_file("test.md", b"old\n", b"new\n")
        self.assertIsNotNone(result)
        self.assertEqual(result, b"manually edited\n")

    def test_empty_result_returns_none(self):
        """If user deletes all content → returns None (abort)."""
        from cypilot.utils.diff_engine import _open_editor_for_file

        def fake_editor(cmd):
            path = cmd[-1]
            with open(path, "w") as f:
                f.write("\n")

        with patch("subprocess.check_call", side_effect=fake_editor):
            with patch.dict("os.environ", {"VISUAL": "cat"}):
                result = _open_editor_for_file("test.md", b"old\n", b"new\n")
        self.assertIsNone(result)

    def test_unresolved_markers_accept(self):
        """Conflict markers remain after editing → prompt → accept upstream."""
        from cypilot.utils.diff_engine import _open_editor_for_file

        def fake_editor(cmd):
            # Leave conflict markers in place (don't resolve)
            pass

        with patch("subprocess.check_call", side_effect=fake_editor):
            with patch.dict("os.environ", {"VISUAL": "cat"}):
                with patch("cypilot.utils.diff_engine._prompt_unresolved", return_value="accept"):
                    result = _open_editor_for_file("test.md", b"old\n", b"new\n")
        self.assertEqual(result, b"new\n")

    def test_unresolved_markers_decline(self):
        """Conflict markers remain after editing → prompt → decline."""
        from cypilot.utils.diff_engine import _open_editor_for_file

        def fake_editor(cmd):
            pass  # Leave conflict markers

        with patch("subprocess.check_call", side_effect=fake_editor):
            with patch.dict("os.environ", {"VISUAL": "cat"}):
                with patch("cypilot.utils.diff_engine._prompt_unresolved", return_value="decline"):
                    result = _open_editor_for_file("test.md", b"old\n", b"new\n")
        self.assertIsNone(result)

    def test_editor_exception_returns_none(self):
        """Editor raises exception → returns None."""
        from cypilot.utils.diff_engine import _open_editor_for_file
        with patch("subprocess.check_call", side_effect=RuntimeError("editor crash")):
            with patch.dict("os.environ", {"VISUAL": "cat"}):
                result = _open_editor_for_file("test.md", b"old\n", b"new\n")
        self.assertIsNone(result)

    def test_identical_content_no_conflict_markers(self):
        """When old == new, no conflict markers are produced."""
        from cypilot.utils.diff_engine import _open_editor_for_file

        def fake_editor(cmd):
            path = cmd[-1]
            with open(path) as f:
                content = f.read()
            # No conflict markers when content is identical
            self.assertNotIn("<<<<<<<", content)
            self.assertNotIn(">>>>>>>", content)
            # Write resolved content
            with open(path, "w") as f:
                f.write("kept\n")

        with patch("subprocess.check_call", side_effect=fake_editor):
            with patch.dict("os.environ", {"VISUAL": "cat"}):
                result = _open_editor_for_file("test.md", b"same\n", b"same\n")
        self.assertEqual(result, b"kept\n")


# =========================================================================
# _get_editor
# =========================================================================

class TestGetEditor(unittest.TestCase):
    """Cover _get_editor helper."""

    def test_visual_preferred(self):
        from cypilot.utils.diff_engine import _get_editor
        with patch.dict("os.environ", {"VISUAL": "code", "EDITOR": "vim"}):
            self.assertEqual(_get_editor(), "code")

    def test_editor_fallback(self):
        from cypilot.utils.diff_engine import _get_editor
        with patch.dict("os.environ", {"EDITOR": "nano"}, clear=True):
            self.assertEqual(_get_editor(), "nano")

    def test_default_vi(self):
        from cypilot.utils.diff_engine import _get_editor
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(_get_editor(), "vi")


# =========================================================================
# _build_conflict_content
# =========================================================================

class TestBuildConflictContent(unittest.TestCase):
    """Cover _build_conflict_content — delete/insert/replace opcodes."""

    def test_replace_opcode(self):
        from cypilot.utils.diff_engine import _build_conflict_content
        result = _build_conflict_content("f.md", "old line\n", "new line\n")
        self.assertIn("<<<<<<<", result)
        self.assertIn("=======", result)
        self.assertIn(">>>>>>>", result)
        self.assertIn("old line", result)
        self.assertIn("new line", result)

    def test_delete_opcode(self):
        from cypilot.utils.diff_engine import _build_conflict_content
        result = _build_conflict_content("f.md", "line1\nline2\n", "line1\n")
        self.assertIn("<<<<<<<", result)
        self.assertIn("line2", result)

    def test_insert_opcode(self):
        from cypilot.utils.diff_engine import _build_conflict_content
        result = _build_conflict_content("f.md", "line1\n", "line1\ninserted\n")
        self.assertIn("<<<<<<<", result)
        self.assertIn("inserted", result)

    def test_identical_no_markers(self):
        from cypilot.utils.diff_engine import _build_conflict_content
        result = _build_conflict_content("f.md", "same\n", "same\n")
        self.assertNotIn("<<<<<<<", result)
        self.assertEqual(result, "same\n")


# =========================================================================
# _prompt_kit_file
# =========================================================================

class TestPromptKitFile(unittest.TestCase):
    """Cover _prompt_kit_file — all response paths."""

    def test_accept_all_flag(self):
        from cypilot.utils.diff_engine import _prompt_kit_file
        state = {"accept_all": True}
        self.assertEqual(_prompt_kit_file("f.md", state), "accept")

    def test_decline_all_flag(self):
        from cypilot.utils.diff_engine import _prompt_kit_file
        state = {"decline_all": True}
        self.assertEqual(_prompt_kit_file("f.md", state), "decline")

    def test_accept_single(self):
        from cypilot.utils.diff_engine import _prompt_kit_file
        with patch("builtins.input", return_value="a"):
            self.assertEqual(_prompt_kit_file("f.md", {}), "accept")

    def test_decline_single(self):
        from cypilot.utils.diff_engine import _prompt_kit_file
        with patch("builtins.input", return_value="d"):
            self.assertEqual(_prompt_kit_file("f.md", {}), "decline")

    def test_accept_all_sets_flag(self):
        from cypilot.utils.diff_engine import _prompt_kit_file
        state = {}
        with patch("builtins.input", return_value="A"):
            result = _prompt_kit_file("f.md", state)
        self.assertEqual(result, "accept")
        self.assertTrue(state["accept_all"])

    def test_decline_all_sets_flag(self):
        from cypilot.utils.diff_engine import _prompt_kit_file
        state = {}
        with patch("builtins.input", return_value="D"):
            result = _prompt_kit_file("f.md", state)
        self.assertEqual(result, "decline")
        self.assertTrue(state["decline_all"])

    def test_modify(self):
        from cypilot.utils.diff_engine import _prompt_kit_file
        with patch("builtins.input", return_value="m"):
            self.assertEqual(_prompt_kit_file("f.md", {}), "modify")

    def test_eof_declines(self):
        from cypilot.utils.diff_engine import _prompt_kit_file
        with patch("builtins.input", side_effect=EOFError):
            self.assertEqual(_prompt_kit_file("f.md", {}), "decline")

    def test_unknown_input_declines(self):
        from cypilot.utils.diff_engine import _prompt_kit_file
        with patch("builtins.input", return_value="x"):
            self.assertEqual(_prompt_kit_file("f.md", {}), "decline")


# =========================================================================
# _show_kit_update_summary
# =========================================================================

class TestShowKitUpdateSummary(unittest.TestCase):
    """Cover _show_kit_update_summary display."""

    def test_summary_with_all_change_types(self):
        from cypilot.utils.diff_engine import _show_kit_update_summary, DiffReport
        report = DiffReport(
            added=["new.md"],
            removed=["old.md"],
            modified=["changed.md"],
            unchanged=["same.md"],
        )
        err = io.StringIO()
        with patch("sys.stderr", err):
            _show_kit_update_summary(report)
        out = err.getvalue()
        self.assertIn("1 added", out)
        self.assertIn("1 removed", out)
        self.assertIn("1 modified", out)
        self.assertIn("1 unchanged", out)
        self.assertIn("new.md", out)
        self.assertIn("old.md", out)
        self.assertIn("changed.md", out)


# =========================================================================
# show_file_diff — binary content
# =========================================================================

class TestShowFileDiffBinary(unittest.TestCase):
    def test_binary_content(self):
        err = io.StringIO()
        # Invalid UTF-8 sequences trigger UnicodeDecodeError
        with patch("sys.stderr", err):
            show_file_diff("bin.dat", b"\x80\x81\xff", b"\xfe\xfd")
        self.assertIn("binary", err.getvalue())


# =========================================================================
# _enumerate_kit_files
# =========================================================================

class TestEnumerateKitFiles(unittest.TestCase):
    """Cover _enumerate_kit_files — include and exclude modes."""

    def test_include_mode(self):
        from cypilot.utils.diff_engine import _enumerate_kit_files
        with TemporaryDirectory() as td:
            kit = Path(td)
            (kit / "artifacts" / "DESIGN").mkdir(parents=True)
            (kit / "artifacts" / "DESIGN" / "t.md").write_text("x\n", encoding="utf-8")
            (kit / "SKILL.md").write_text("s\n", encoding="utf-8")
            (kit / "conf.toml").write_text("v=1\n", encoding="utf-8")
            files = _enumerate_kit_files(kit, content_dirs=("artifacts",), content_files=("SKILL.md",))
            self.assertIn("SKILL.md", files)
            self.assertTrue(any("DESIGN" in k for k in files))
            # conf.toml not in content_files, so excluded
            self.assertNotIn("conf.toml", files)

    def test_exclude_mode(self):
        from cypilot.utils.diff_engine import _enumerate_kit_files
        with TemporaryDirectory() as td:
            kit = Path(td)
            (kit / "SKILL.md").write_text("s\n", encoding="utf-8")
            (kit / "conf.toml").write_text("v=1\n", encoding="utf-8")
            (kit / "__pycache__").mkdir()
            (kit / "__pycache__" / "x.pyc").write_bytes(b"\x00")
            files = _enumerate_kit_files(kit)  # default exclude mode
            self.assertIn("SKILL.md", files)
            self.assertNotIn("conf.toml", files)
            self.assertFalse(any("__pycache__" in k for k in files))

    def test_nonexistent_dir(self):
        from cypilot.utils.diff_engine import _enumerate_kit_files
        files = _enumerate_kit_files(Path("/nonexistent"))
        self.assertEqual(files, {})


# =========================================================================
# file_level_kit_update
# =========================================================================

class TestFileLevelKitUpdate(unittest.TestCase):
    """Cover file_level_kit_update — auto_approve, non-interactive, force."""

    def test_no_changes(self):
        from cypilot.utils.diff_engine import file_level_kit_update
        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            for d in (src, usr):
                d.mkdir()
                (d / "SKILL.md").write_text("same\n", encoding="utf-8")
            result = file_level_kit_update(src, usr, content_files=("SKILL.md",))
            self.assertEqual(result["status"], "current")
            self.assertEqual(result["accepted"], [])

    def test_auto_approve(self):
        from cypilot.utils.diff_engine import file_level_kit_update
        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            src.mkdir(); usr.mkdir()
            (src / "SKILL.md").write_text("new\n", encoding="utf-8")
            (usr / "SKILL.md").write_text("old\n", encoding="utf-8")
            result = file_level_kit_update(src, usr, auto_approve=True, content_files=("SKILL.md",))
            self.assertEqual(result["status"], "updated")
            self.assertIn("SKILL.md", result["accepted"])
            # File should be updated on disk
            self.assertEqual((usr / "SKILL.md").read_text(), "new\n")

    def test_non_interactive_declines(self):
        from cypilot.utils.diff_engine import file_level_kit_update
        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            src.mkdir(); usr.mkdir()
            (src / "SKILL.md").write_text("new\n", encoding="utf-8")
            (usr / "SKILL.md").write_text("old\n", encoding="utf-8")
            result = file_level_kit_update(src, usr, interactive=False, content_files=("SKILL.md",))
            self.assertEqual(result["status"], "updated")
            self.assertIn("SKILL.md", result["declined"])
            # File should NOT be changed
            self.assertEqual((usr / "SKILL.md").read_text(), "old\n")

    def test_force_overwrites(self):
        from cypilot.utils.diff_engine import file_level_kit_update
        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            src.mkdir(); usr.mkdir()
            (src / "SKILL.md").write_text("forced\n", encoding="utf-8")
            (usr / "SKILL.md").write_text("old\n", encoding="utf-8")
            result = file_level_kit_update(src, usr, force=True, content_files=("SKILL.md",))
            self.assertEqual(result["status"], "updated")
            self.assertIn("SKILL.md", result["accepted"])

    def test_added_file_auto_approve(self):
        from cypilot.utils.diff_engine import file_level_kit_update
        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            src.mkdir(); usr.mkdir()
            (src / "NEW.md").write_text("brand new\n", encoding="utf-8")
            result = file_level_kit_update(src, usr, auto_approve=True, content_files=("NEW.md",))
            self.assertEqual(result["status"], "updated")
            self.assertTrue((usr / "NEW.md").is_file())

    def test_removed_file_auto_approve(self):
        from cypilot.utils.diff_engine import file_level_kit_update
        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            src.mkdir(); usr.mkdir()
            (usr / "OLD.md").write_text("gone upstream\n", encoding="utf-8")
            result = file_level_kit_update(src, usr, auto_approve=True, content_files=("OLD.md",))
            self.assertEqual(result["status"], "updated")
            self.assertFalse((usr / "OLD.md").is_file())

    def test_interactive_accept(self):
        from cypilot.utils.diff_engine import file_level_kit_update
        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            src.mkdir(); usr.mkdir()
            (src / "SKILL.md").write_text("new\n", encoding="utf-8")
            (usr / "SKILL.md").write_text("old\n", encoding="utf-8")
            with patch("cypilot.utils.diff_engine._prompt_kit_file", return_value="accept"):
                result = file_level_kit_update(src, usr, interactive=True, content_files=("SKILL.md",))
            self.assertIn("SKILL.md", result["accepted"])

    def test_interactive_modify(self):
        from cypilot.utils.diff_engine import file_level_kit_update
        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            src.mkdir(); usr.mkdir()
            (src / "SKILL.md").write_text("new\n", encoding="utf-8")
            (usr / "SKILL.md").write_text("old\n", encoding="utf-8")
            with patch("cypilot.utils.diff_engine._prompt_kit_file", return_value="modify"):
                with patch("cypilot.utils.diff_engine._open_editor_for_file", return_value=b"edited\n"):
                    result = file_level_kit_update(src, usr, interactive=True, content_files=("SKILL.md",))
            self.assertIn("SKILL.md", result["accepted"])
            self.assertEqual((usr / "SKILL.md").read_text(), "edited\n")

    def test_interactive_modify_abort(self):
        from cypilot.utils.diff_engine import file_level_kit_update
        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            src.mkdir(); usr.mkdir()
            (src / "SKILL.md").write_text("new\n", encoding="utf-8")
            (usr / "SKILL.md").write_text("old\n", encoding="utf-8")
            with patch("cypilot.utils.diff_engine._prompt_kit_file", return_value="modify"):
                with patch("cypilot.utils.diff_engine._open_editor_for_file", return_value=None):
                    result = file_level_kit_update(src, usr, interactive=True, content_files=("SKILL.md",))
            self.assertIn("SKILL.md", result["declined"])

    def test_interactive_added_file(self):
        """Interactive prompt for newly added files."""
        from cypilot.utils.diff_engine import file_level_kit_update
        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            src.mkdir(); usr.mkdir()
            (src / "NEW.md").write_text("new file\n", encoding="utf-8")
            with patch("cypilot.utils.diff_engine._prompt_kit_file", return_value="accept"):
                result = file_level_kit_update(src, usr, interactive=True, content_files=("NEW.md",))
            self.assertTrue((usr / "NEW.md").is_file())

    def test_interactive_removed_file(self):
        """Interactive prompt for removed files."""
        from cypilot.utils.diff_engine import file_level_kit_update
        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            src.mkdir(); usr.mkdir()
            (usr / "OLD.md").write_text("old\n", encoding="utf-8")
            with patch("cypilot.utils.diff_engine._prompt_kit_file", return_value="accept"):
                result = file_level_kit_update(src, usr, interactive=True, content_files=("OLD.md",))
            self.assertFalse((usr / "OLD.md").is_file())

    def test_dry_run_does_not_write(self):
        from cypilot.utils.diff_engine import file_level_kit_update
        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            src.mkdir(); usr.mkdir()
            (src / "SKILL.md").write_text("new\n", encoding="utf-8")
            (usr / "SKILL.md").write_text("old\n", encoding="utf-8")
            result = file_level_kit_update(src, usr, auto_approve=True, dry_run=True, content_files=("SKILL.md",))
            # File should NOT be updated
            self.assertEqual((usr / "SKILL.md").read_text(), "old\n")


# =========================================================================
# file_level_kit_update with resource bindings
# =========================================================================

class TestFileLevelKitUpdateResourceBindings(unittest.TestCase):
    """Test file_level_kit_update with resource bindings for manifest-driven kits."""

    def test_file_resource_binding_redirect(self):
        """File resource is written to bound path, not user_dir."""
        from cypilot.utils.diff_engine import file_level_kit_update
        from cypilot.utils.manifest import ResourceInfo

        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            redirect_dir = Path(td) / "redirect"
            src.mkdir()
            usr.mkdir()
            redirect_dir.mkdir()

            # Source has a file
            (src / "artifacts").mkdir()
            (src / "artifacts" / "template.md").write_text("new template\n", encoding="utf-8")

            # Resource bindings redirect to different location
            resource_bindings = {
                "adr_template": redirect_dir / "template.md",
            }
            source_to_resource_id = {
                "artifacts/template.md": "adr_template",
            }
            resource_info = {
                "adr_template": ResourceInfo(type="file", source_base="artifacts/template.md"),
            }

            result = file_level_kit_update(
                src, usr,
                auto_approve=True,
                content_dirs=("artifacts",),
                resource_bindings=resource_bindings,
                source_to_resource_id=source_to_resource_id,
                resource_info=resource_info,
            )

            self.assertEqual(result["status"], "updated")
            # File should be at redirected path
            self.assertTrue((redirect_dir / "template.md").is_file())
            self.assertEqual((redirect_dir / "template.md").read_text(), "new template\n")
            # File should NOT be at default path
            self.assertFalse((usr / "artifacts" / "template.md").exists())

    def test_directory_resource_binding_redirect(self):
        """Directory resource files are written to bound directory with relative paths."""
        from cypilot.utils.diff_engine import file_level_kit_update
        from cypilot.utils.manifest import ResourceInfo

        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            redirect_dir = Path(td) / "redirect"
            src.mkdir()
            usr.mkdir()
            redirect_dir.mkdir()

            # Source has a directory with files
            (src / "artifacts" / "ADR").mkdir(parents=True)
            (src / "artifacts" / "ADR" / "template.md").write_text("ADR template\n", encoding="utf-8")
            (src / "artifacts" / "ADR" / "checklist.md").write_text("ADR checklist\n", encoding="utf-8")

            # Resource bindings redirect entire directory
            resource_bindings = {
                "adr_artifacts": redirect_dir / "ADR",
            }
            source_to_resource_id = {
                "artifacts/ADR/template.md": "adr_artifacts",
                "artifacts/ADR/checklist.md": "adr_artifacts",
            }
            resource_info = {
                "adr_artifacts": ResourceInfo(type="directory", source_base="artifacts/ADR"),
            }

            result = file_level_kit_update(
                src, usr,
                auto_approve=True,
                content_dirs=("artifacts",),
                resource_bindings=resource_bindings,
                source_to_resource_id=source_to_resource_id,
                resource_info=resource_info,
            )

            self.assertEqual(result["status"], "updated")
            # Files should be at redirected paths
            self.assertTrue((redirect_dir / "ADR" / "template.md").is_file())
            self.assertTrue((redirect_dir / "ADR" / "checklist.md").is_file())
            self.assertEqual((redirect_dir / "ADR" / "template.md").read_text(), "ADR template\n")
            # Files should NOT be at default paths
            self.assertFalse((usr / "artifacts" / "ADR" / "template.md").exists())

    def test_mixed_bound_and_unbound_files(self):
        """Files without bindings go to user_dir, bound files go to binding path."""
        from cypilot.utils.diff_engine import file_level_kit_update
        from cypilot.utils.manifest import ResourceInfo

        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            redirect_dir = Path(td) / "redirect"
            src.mkdir()
            usr.mkdir()
            redirect_dir.mkdir()

            # Source has bound and unbound files
            (src / "artifacts").mkdir()
            (src / "artifacts" / "template.md").write_text("bound file\n", encoding="utf-8")
            (src / "SKILL.md").write_text("unbound file\n", encoding="utf-8")

            resource_bindings = {
                "adr_template": redirect_dir / "template.md",
            }
            source_to_resource_id = {
                "artifacts/template.md": "adr_template",
                # SKILL.md has no binding
            }
            resource_info = {
                "adr_template": ResourceInfo(type="file", source_base="artifacts/template.md"),
            }

            result = file_level_kit_update(
                src, usr,
                auto_approve=True,
                content_dirs=("artifacts",),
                content_files=("SKILL.md",),
                resource_bindings=resource_bindings,
                source_to_resource_id=source_to_resource_id,
                resource_info=resource_info,
            )

            self.assertEqual(result["status"], "updated")
            # Bound file at redirect path
            self.assertTrue((redirect_dir / "template.md").is_file())
            # Unbound file at default path
            self.assertTrue((usr / "SKILL.md").is_file())
            self.assertEqual((usr / "SKILL.md").read_text(), "unbound file\n")

    def test_update_existing_bound_file(self):
        """Existing file at bound path is correctly detected and updated."""
        from cypilot.utils.diff_engine import file_level_kit_update
        from cypilot.utils.manifest import ResourceInfo

        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            redirect_dir = Path(td) / "redirect"
            src.mkdir()
            usr.mkdir()
            redirect_dir.mkdir()

            # Source has updated content
            (src / "artifacts").mkdir()
            (src / "artifacts" / "template.md").write_text("updated content\n", encoding="utf-8")

            # Existing file at bound location
            (redirect_dir / "template.md").write_text("old content\n", encoding="utf-8")

            resource_bindings = {
                "adr_template": redirect_dir / "template.md",
            }
            source_to_resource_id = {
                "artifacts/template.md": "adr_template",
            }
            resource_info = {
                "adr_template": ResourceInfo(type="file", source_base="artifacts/template.md"),
            }

            result = file_level_kit_update(
                src, usr,
                auto_approve=True,
                content_dirs=("artifacts",),
                resource_bindings=resource_bindings,
                source_to_resource_id=source_to_resource_id,
                resource_info=resource_info,
            )

            self.assertEqual(result["status"], "updated")
            self.assertIn("artifacts/template.md", result["accepted"])
            # File should be updated at bound path
            self.assertEqual((redirect_dir / "template.md").read_text(), "updated content\n")

    def test_no_resource_bindings_uses_default_paths(self):
        """Without resource bindings, files go to user_dir (backward compatibility)."""
        from cypilot.utils.diff_engine import file_level_kit_update

        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            src.mkdir(); usr.mkdir()

            (src / "artifacts").mkdir()
            (src / "artifacts" / "template.md").write_text("content\n", encoding="utf-8")

            # No resource bindings passed
            result = file_level_kit_update(
                src, usr,
                auto_approve=True,
                content_dirs=("artifacts",),
            )

            self.assertEqual(result["status"], "updated")
            # File at default path
            self.assertTrue((usr / "artifacts" / "template.md").is_file())

    def test_file_resource_binding_to_directory(self):
        """File resource with binding pointing to a directory appends filename."""
        from cypilot.utils.diff_engine import file_level_kit_update
        from cypilot.utils.manifest import ResourceInfo

        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            redirect_dir = Path(td) / "redirect"
            src.mkdir()
            usr.mkdir()
            redirect_dir.mkdir()

            # Source has example.md inside examples/ subdirectory
            (src / "artifacts" / "ADR" / "examples").mkdir(parents=True)
            (src / "artifacts" / "ADR" / "examples" / "example.md").write_text("new example\n", encoding="utf-8")

            # Existing file at bound directory (binding points to directory, not file)
            (redirect_dir / "example.md").write_text("old example\n", encoding="utf-8")

            # Binding points to directory, but manifest resource is a file
            resource_bindings = {
                "adr_example": redirect_dir,  # Directory, not file!
            }
            source_to_resource_id = {
                "artifacts/ADR/examples/example.md": "adr_example",
            }
            resource_info = {
                "adr_example": ResourceInfo(type="file", source_base="artifacts/ADR/examples/example.md"),
            }

            result = file_level_kit_update(
                src, usr,
                auto_approve=True,
                content_dirs=("artifacts",),
                resource_bindings=resource_bindings,
                source_to_resource_id=source_to_resource_id,
                resource_info=resource_info,
            )

            self.assertEqual(result["status"], "updated")
            # File should be updated at redirect_dir/example.md (filename appended)
            self.assertEqual((redirect_dir / "example.md").read_text(), "new example\n")

    def test_file_resource_binding_to_directory_detects_existing(self):
        """File resource with directory binding detects existing file (not shown as 'new')."""
        from cypilot.utils.diff_engine import file_level_kit_update
        from cypilot.utils.manifest import ResourceInfo

        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            redirect_dir = Path(td) / "redirect"
            src.mkdir()
            usr.mkdir()
            redirect_dir.mkdir()

            # Source has example.md
            (src / "artifacts" / "ADR" / "examples").mkdir(parents=True)
            (src / "artifacts" / "ADR" / "examples" / "example.md").write_text("same content\n", encoding="utf-8")

            # Existing file at bound directory with SAME content
            (redirect_dir / "example.md").write_text("same content\n", encoding="utf-8")

            resource_bindings = {
                "adr_example": redirect_dir,
            }
            source_to_resource_id = {
                "artifacts/ADR/examples/example.md": "adr_example",
            }
            resource_info = {
                "adr_example": ResourceInfo(type="file", source_base="artifacts/ADR/examples/example.md"),
            }

            result = file_level_kit_update(
                src, usr,
                auto_approve=True,
                content_dirs=("artifacts",),
                resource_bindings=resource_bindings,
                source_to_resource_id=source_to_resource_id,
                resource_info=resource_info,
            )

            # Should be "current" since file exists with same content
            self.assertEqual(result["status"], "current")
            # File should NOT be in added list
            self.assertNotIn("artifacts/ADR/examples/example.md", result.get("accepted", []))

    def test_existing_file_in_bound_directory_not_in_source(self):
        """Files existing in bound directory but not in source are detected as 'removed'."""
        from cypilot.utils.diff_engine import file_level_kit_update
        from cypilot.utils.manifest import ResourceInfo

        with TemporaryDirectory() as td:
            src = Path(td) / "src"
            usr = Path(td) / "usr"
            redirect_dir = Path(td) / "redirect"
            src.mkdir()
            usr.mkdir()
            redirect_dir.mkdir()

            # Source has template.md but NOT example.md
            (src / "artifacts").mkdir()
            (src / "artifacts" / "template.md").write_text("template content\n", encoding="utf-8")

            # Bound directory has BOTH template.md and example.md (example.md is user-only)
            (redirect_dir / "template.md").write_text("template content\n", encoding="utf-8")
            (redirect_dir / "example.md").write_text("user example\n", encoding="utf-8")

            resource_bindings = {
                "adr_artifacts": redirect_dir,
            }
            source_to_resource_id = {
                "artifacts/template.md": "adr_artifacts",
            }
            resource_info = {
                "adr_artifacts": ResourceInfo(type="directory", source_base="artifacts"),
            }

            result = file_level_kit_update(
                src, usr,
                interactive=False,  # Non-interactive declines changes
                content_dirs=("artifacts",),
                resource_bindings=resource_bindings,
                source_to_resource_id=source_to_resource_id,
                resource_info=resource_info,
            )

            # example.md should be detected as existing in bound dir
            # Since it's not in source, it would be classified as "removed"
            # With interactive=False, it should be declined (not deleted)
            self.assertTrue((redirect_dir / "example.md").is_file())
            self.assertEqual((redirect_dir / "example.md").read_text(), "user example\n")
            # Verify example.md was detected and declined
            self.assertIn("artifacts/example.md", result["declined"])


# =========================================================================
# _has_conflict_markers
# =========================================================================

class TestHasConflictMarkers(unittest.TestCase):
    def test_has_markers(self):
        from cypilot.utils.diff_engine import _has_conflict_markers
        self.assertTrue(_has_conflict_markers("<<<<<<< installed (yours)\nfoo\n=======\nbar\n>>>>>>> upstream (source)\n"))

    def test_no_markers(self):
        from cypilot.utils.diff_engine import _has_conflict_markers
        self.assertFalse(_has_conflict_markers("just normal text\n"))


# ---------------------------------------------------------------------------
# TOC handling during kit update
# ---------------------------------------------------------------------------

class TestStripTocForDiff(unittest.TestCase):
    """Tests for _strip_toc_for_diff."""

    def test_no_toc(self):
        from cypilot.utils.diff_engine import _strip_toc_for_diff
        content = b"# Title\n\n## Section A\n\nSome text.\n"
        stripped, fmt = _strip_toc_for_diff(content)
        self.assertEqual(stripped, content)
        self.assertEqual(fmt, "")

    def test_marker_toc(self):
        from cypilot.utils.diff_engine import _strip_toc_for_diff
        content = (
            "# Title\n\n"
            "<!-- toc -->\n\n"
            "- [Section A](#section-a)\n"
            "- [Section B](#section-b)\n\n"
            "<!-- /toc -->\n\n"
            "## Section A\n\nText A.\n"
        ).encode("utf-8")
        stripped, fmt = _strip_toc_for_diff(content)
        self.assertEqual(fmt, "markers")
        text = stripped.decode("utf-8")
        self.assertNotIn("<!-- toc -->", text)
        self.assertNotIn("Section A](#section-a)", text)
        self.assertIn("## Section A", text)
        self.assertIn("Text A.", text)

    def test_heading_toc(self):
        from cypilot.utils.diff_engine import _strip_toc_for_diff
        content = (
            "# Title\n\n"
            "## Table of Contents\n\n"
            "1. [Section A](#section-a)\n"
            "2. [Section B](#section-b)\n\n"
            "## Section A\n\nText A.\n"
        ).encode("utf-8")
        stripped, fmt = _strip_toc_for_diff(content)
        self.assertEqual(fmt, "heading")
        text = stripped.decode("utf-8")
        self.assertNotIn("Table of Contents", text)
        self.assertNotIn("Section A](#section-a)", text)
        self.assertIn("## Section A", text)

    def test_binary_content(self):
        from cypilot.utils.diff_engine import _strip_toc_for_diff
        content = b"\x80\x81\x82\xff\xfe"
        stripped, fmt = _strip_toc_for_diff(content)
        self.assertEqual(stripped, content)
        self.assertEqual(fmt, "")

    def test_heading_toc_at_end_of_file(self):
        """Heading TOC with no following heading — strips to end."""
        from cypilot.utils.diff_engine import _strip_toc_for_diff
        content = (
            "# Title\n\n"
            "## Table of Contents\n\n"
            "1. [A](#a)\n"
        ).encode("utf-8")
        stripped, fmt = _strip_toc_for_diff(content)
        self.assertEqual(fmt, "heading")
        text = stripped.decode("utf-8")
        self.assertNotIn("Table of Contents", text)
        self.assertIn("# Title", text)


class TestPromptTocRegen(unittest.TestCase):
    """Tests for _prompt_toc_regen."""

    @patch("builtins.input", return_value="y")
    def test_yes(self, _mock):
        from cypilot.utils.diff_engine import _prompt_toc_regen
        self.assertEqual(_prompt_toc_regen("foo.md"), "yes")

    @patch("builtins.input", return_value="yes")
    def test_yes_full(self, _mock):
        from cypilot.utils.diff_engine import _prompt_toc_regen
        self.assertEqual(_prompt_toc_regen("foo.md"), "yes")

    @patch("builtins.input", return_value="n")
    def test_no(self, _mock):
        from cypilot.utils.diff_engine import _prompt_toc_regen
        self.assertEqual(_prompt_toc_regen("foo.md"), "no")

    @patch("builtins.input", return_value="")
    def test_empty(self, _mock):
        from cypilot.utils.diff_engine import _prompt_toc_regen
        self.assertEqual(_prompt_toc_regen("foo.md"), "no")

    @patch("builtins.input", side_effect=EOFError)
    def test_eof(self, _mock):
        from cypilot.utils.diff_engine import _prompt_toc_regen
        self.assertEqual(_prompt_toc_regen("foo.md"), "no")


class TestPromptTocErrorContinue(unittest.TestCase):
    """Tests for _prompt_toc_error_continue."""

    @patch("builtins.input", return_value="c")
    def test_continue(self, _mock):
        from cypilot.utils.diff_engine import _prompt_toc_error_continue
        self.assertTrue(_prompt_toc_error_continue("foo.md", RuntimeError("oops")))

    @patch("builtins.input", return_value="s")
    def test_stop(self, _mock):
        from cypilot.utils.diff_engine import _prompt_toc_error_continue
        self.assertFalse(_prompt_toc_error_continue("foo.md", RuntimeError("oops")))

    @patch("builtins.input", return_value="")
    def test_default_continue(self, _mock):
        from cypilot.utils.diff_engine import _prompt_toc_error_continue
        self.assertTrue(_prompt_toc_error_continue("foo.md", RuntimeError("oops")))

    @patch("builtins.input", side_effect=EOFError)
    def test_eof_stops(self, _mock):
        from cypilot.utils.diff_engine import _prompt_toc_error_continue
        self.assertFalse(_prompt_toc_error_continue("foo.md", RuntimeError("oops")))


class TestRegenerateToc(unittest.TestCase):
    """Tests for _regenerate_toc."""

    def test_heading_format(self):
        from cypilot.utils.diff_engine import _regenerate_toc
        content = b"# Title\n\n## Section A\n\nText.\n\n## Section B\n\nMore.\n"
        result = _regenerate_toc(content, "heading")
        text = result.decode("utf-8")
        self.assertIn("Table of Contents", text)
        self.assertIn("Section A", text)
        self.assertIn("Section B", text)

    def test_markers_format(self):
        from cypilot.utils.diff_engine import _regenerate_toc
        content = b"# Title\n\n## Section A\n\nText.\n\n## Section B\n\nMore.\n"
        result = _regenerate_toc(content, "markers")
        text = result.decode("utf-8")
        self.assertIn("<!-- toc -->", text)
        self.assertIn("<!-- /toc -->", text)


class TestFileLevelKitUpdateTocIntegration(unittest.TestCase):
    """Integration tests for TOC stripping and regen in file_level_kit_update."""

    def _make_md_with_toc(self, title, sections, toc_format="heading"):
        """Build markdown with a TOC section."""
        lines = [f"# {title}", ""]
        if toc_format == "heading":
            lines.append("## Table of Contents")
            lines.append("")
            for i, s in enumerate(sections, 1):
                slug = s.lower().replace(" ", "-")
                lines.append(f"{i}. [{s}](#{slug})")
            lines.append("")
        elif toc_format == "markers":
            lines.append("<!-- toc -->")
            lines.append("")
            for s in sections:
                slug = s.lower().replace(" ", "-")
                lines.append(f"- [{s}](#{slug})")
            lines.append("")
            lines.append("<!-- /toc -->")
            lines.append("")
        for s in sections:
            lines.extend([f"## {s}", "", f"Content of {s}.", ""])
        return "\n".join(lines)

    def _make_md_no_toc(self, title, sections):
        """Build markdown without TOC."""
        lines = [f"# {title}", ""]
        for s in sections:
            lines.extend([f"## {s}", "", f"Content of {s}.", ""])
        return "\n".join(lines)

    def test_toc_stripped_from_diff_only_content_changes_shown(self):
        """Files differing only in TOC should be classified as unchanged."""
        from cypilot.utils.diff_engine import file_level_kit_update

        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "source"
            usr = Path(tmpdir) / "user"
            src.mkdir()
            usr.mkdir()

            sections = ["Alpha", "Beta"]
            # Source has TOC with entries
            (src / "rules.md").write_text(
                self._make_md_with_toc("Rules", sections), encoding="utf-8"
            )
            # User has same content but slightly different TOC formatting
            # (same content, different TOC) — should be unchanged after stripping
            (usr / "rules.md").write_text(
                self._make_md_with_toc("Rules", sections), encoding="utf-8"
            )

            result = file_level_kit_update(
                src, usr, interactive=False, auto_approve=False
            )
            self.assertEqual(result["status"], "current")
            self.assertEqual(result["modified"], [])

    def test_content_change_detected_despite_toc(self):
        """Real content changes are still detected after TOC stripping."""
        from cypilot.utils.diff_engine import file_level_kit_update

        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "source"
            usr = Path(tmpdir) / "user"
            src.mkdir()
            usr.mkdir()

            (src / "rules.md").write_text(
                self._make_md_with_toc("Rules", ["Alpha", "Beta", "Gamma"]),
                encoding="utf-8",
            )
            (usr / "rules.md").write_text(
                self._make_md_with_toc("Rules", ["Alpha", "Beta"]),
                encoding="utf-8",
            )

            result = file_level_kit_update(
                src, usr, interactive=False, auto_approve=False
            )
            # Non-interactive without auto_approve → declined
            self.assertEqual(result["status"], "updated")
            self.assertEqual(len(result["modified"]), 1)
            self.assertEqual(result["modified"][0]["action"], "declined")

    def test_auto_approve_regenerates_toc(self):
        """auto_approve writes content and auto-regenerates TOC."""
        from cypilot.utils.diff_engine import file_level_kit_update

        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "source"
            usr = Path(tmpdir) / "user"
            src.mkdir()
            usr.mkdir()

            # Source: new section, with TOC
            (src / "rules.md").write_text(
                self._make_md_with_toc("Rules", ["Alpha", "Beta", "Gamma"]),
                encoding="utf-8",
            )
            # User: old sections, with TOC
            (usr / "rules.md").write_text(
                self._make_md_with_toc("Rules", ["Alpha", "Beta"]),
                encoding="utf-8",
            )

            result = file_level_kit_update(
                src, usr, interactive=False, auto_approve=True
            )
            self.assertEqual(result["modified"][0]["action"], "accepted")

            # File should have been written with regenerated TOC
            written = (usr / "rules.md").read_text(encoding="utf-8")
            # Gamma section should be present (content accepted)
            self.assertIn("## Gamma", written)
            # TOC should have been regenerated (contains Gamma link)
            self.assertIn("Gamma", written.split("## Alpha")[0])

    def test_interactive_toc_prompt_yes(self):
        """Interactive: user says 'y' to TOC regen after accept."""
        from cypilot.utils.diff_engine import file_level_kit_update

        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "source"
            usr = Path(tmpdir) / "user"
            src.mkdir()
            usr.mkdir()

            (src / "rules.md").write_text(
                self._make_md_with_toc("Rules", ["Alpha", "New"]),
                encoding="utf-8",
            )
            (usr / "rules.md").write_text(
                self._make_md_with_toc("Rules", ["Alpha"]),
                encoding="utf-8",
            )

            # Patch input: first call = accept file ('a'), second = regen TOC ('y')
            with patch("builtins.input", side_effect=["a", "y"]):
                result = file_level_kit_update(
                    src, usr, interactive=True, auto_approve=False
                )

            self.assertEqual(result["modified"][0]["action"], "accepted")
            written = (usr / "rules.md").read_text(encoding="utf-8")
            self.assertIn("## New", written)
            # TOC should include "New"
            toc_area = written.split("## Alpha")[0]
            self.assertIn("New", toc_area)

    def test_interactive_accepted_has_source_toc(self):
        """Interactive: accepted file writes raw source content (includes TOC)."""
        from cypilot.utils.diff_engine import file_level_kit_update

        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "source"
            usr = Path(tmpdir) / "user"
            src.mkdir()
            usr.mkdir()

            (src / "rules.md").write_text(
                self._make_md_with_toc("Rules", ["Alpha", "New"]),
                encoding="utf-8",
            )
            (usr / "rules.md").write_text(
                self._make_md_with_toc("Rules", ["Alpha"]),
                encoding="utf-8",
            )

            # Accept file — raw source (with TOC) is written, no TOC regen prompt
            with patch("builtins.input", side_effect=["a"]):
                result = file_level_kit_update(
                    src, usr, interactive=True, auto_approve=False
                )

            self.assertEqual(result["modified"][0]["action"], "accepted")
            written = (usr / "rules.md").read_text(encoding="utf-8")
            self.assertIn("## New", written)
            # Raw source written — TOC is already present from source
            self.assertIn("Table of Contents", written)

    def test_toc_regen_error_rollback_continue(self):
        """TOC regen failure restores previous content; user continues."""
        from cypilot.utils.diff_engine import file_level_kit_update

        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "source"
            usr = Path(tmpdir) / "user"
            src.mkdir()
            usr.mkdir()

            src_content = self._make_md_with_toc("Rules", ["Alpha", "New"])
            (src / "rules.md").write_text(src_content, encoding="utf-8")
            original_user = self._make_md_with_toc("Rules", ["Alpha"])
            (usr / "rules.md").write_text(original_user, encoding="utf-8")

            # Use "modify" path so wrote_raw=False, triggering TOC regen.
            # Input: "m" (modify) → "y" (regen TOC) → "c" (continue after error)
            edited = self._make_md_no_toc("Rules", ["Alpha", "New"]).encode("utf-8")
            with (
                patch("builtins.input", side_effect=["m", "y", "c"]),
                patch(
                    "cypilot.utils.diff_engine._open_editor_for_file",
                    return_value=edited,
                ),
                patch(
                    "cypilot.utils.diff_engine._regenerate_toc",
                    side_effect=RuntimeError("toc broken"),
                ),
            ):
                result = file_level_kit_update(
                    src, usr, interactive=True, auto_approve=False
                )

            # File should be rolled back to original user content
            restored = (usr / "rules.md").read_text(encoding="utf-8")
            self.assertEqual(restored, original_user)

    def test_toc_regen_error_rollback_stop(self):
        """TOC regen failure — user stops; remaining files not processed."""
        from cypilot.utils.diff_engine import file_level_kit_update

        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "source"
            usr = Path(tmpdir) / "user"
            (src / "sub").mkdir(parents=True)
            (usr / "sub").mkdir(parents=True)

            # Two files with TOC
            (src / "a.md").write_text(
                self._make_md_with_toc("A", ["X", "Y"]), encoding="utf-8"
            )
            (usr / "a.md").write_text(
                self._make_md_with_toc("A", ["X"]), encoding="utf-8"
            )
            (src / "sub" / "b.md").write_text(
                self._make_md_with_toc("B", ["P", "Q"]), encoding="utf-8"
            )
            (usr / "sub" / "b.md").write_text(
                self._make_md_with_toc("B", ["P"]), encoding="utf-8"
            )

            # Use "modify" so wrote_raw=False, triggering TOC regen.
            # First file: "m" (modify) → "y" (regen TOC) → "s" (stop on error)
            edited_a = self._make_md_no_toc("A", ["X", "Y"]).encode("utf-8")
            with (
                patch("builtins.input", side_effect=["m", "y", "s"]),
                patch(
                    "cypilot.utils.diff_engine._open_editor_for_file",
                    return_value=edited_a,
                ),
                patch(
                    "cypilot.utils.diff_engine._regenerate_toc",
                    side_effect=RuntimeError("toc broken"),
                ),
            ):
                result = file_level_kit_update(
                    src, usr, interactive=True, auto_approve=False
                )

            # Only first file should have been processed (stopped after error)
            all_paths = [e["path"] for e in result["modified"]]
            self.assertEqual(len(all_paths), 1)

    def test_no_toc_file_no_prompt(self):
        """Files without TOC should not trigger TOC regen prompt."""
        from cypilot.utils.diff_engine import file_level_kit_update

        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "source"
            usr = Path(tmpdir) / "user"
            src.mkdir()
            usr.mkdir()

            (src / "plain.md").write_text(
                "# Title\n\n## A\n\nNew content.\n", encoding="utf-8"
            )
            (usr / "plain.md").write_text(
                "# Title\n\n## A\n\nOld content.\n", encoding="utf-8"
            )

            # Only one input needed: accept file. No TOC prompt.
            with patch("builtins.input", side_effect=["a"]):
                result = file_level_kit_update(
                    src, usr, interactive=True, auto_approve=False
                )

            self.assertEqual(result["modified"][0]["action"], "accepted")


if __name__ == "__main__":
    unittest.main()
