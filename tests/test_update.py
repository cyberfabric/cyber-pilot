"""
Tests for commands/update.py — full update pipeline, dry-run, version drift, error paths.
"""

import io
import json
import os
import shutil
import sys
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))


def _write_toml(path: Path, data: dict) -> None:
    from cypilot.utils import toml_utils
    path.parent.mkdir(parents=True, exist_ok=True)
    toml_utils.dump(data, path)


def _make_cache(cache_dir: Path, kit_version: int = 1) -> None:
    """Create a realistic ~/.cypilot/cache for update tests."""
    for d in ("architecture", "requirements", "schemas", "workflows", "skills"):
        (cache_dir / d).mkdir(parents=True, exist_ok=True)
        (cache_dir / d / "README.md").write_text(f"# {d}\n", encoding="utf-8")
    # Kit as direct file package (no blueprints)
    kit_dir = cache_dir / "kits" / "sdlc"
    kit_dir.mkdir(parents=True, exist_ok=True)
    (kit_dir / "artifacts" / "PRD").mkdir(parents=True)
    (kit_dir / "artifacts" / "PRD" / "template.md").write_text(
        "# Product Requirements\n", encoding="utf-8",
    )
    (kit_dir / "workflows").mkdir(exist_ok=True)
    scripts_dir = kit_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    (scripts_dir / "helper.py").write_text("# helper\n", encoding="utf-8")
    (kit_dir / "SKILL.md").write_text(
        "# Kit sdlc\nKit skill instructions.\n", encoding="utf-8",
    )
    (kit_dir / "constraints.toml").write_text(
        "[naming]\npattern = 'sdlc-*'\n", encoding="utf-8",
    )
    _write_toml(kit_dir / "conf.toml", {
        "version": kit_version,
    })


def _init_project(root: Path, cache_dir: Path) -> Path:
    """Run init to create a fully initialized project."""
    from cypilot.cli import main
    (root / ".git").mkdir(exist_ok=True)
    cwd = os.getcwd()
    try:
        os.chdir(str(root))
        with patch("cypilot.commands.init.CACHE_DIR", cache_dir):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["init", "--yes"])
            assert rc == 0, f"init failed: {buf.getvalue()}"
    finally:
        os.chdir(cwd)
    return root / "cypilot"


# =========================================================================
# Helpers
# =========================================================================

class TestUpdateHelpers(unittest.TestCase):
    """Unit tests for update.py helper functions."""

    def test_ensure_file_creates_when_missing(self):
        from cypilot.commands.update import _ensure_file
        with TemporaryDirectory() as td:
            p = Path(td) / "new.md"
            actions = {}
            _ensure_file(p, "content", actions, "test_key")
            self.assertEqual(actions["test_key"], "created")
            self.assertEqual(p.read_text(encoding="utf-8"), "content")

    def test_ensure_file_preserves_existing(self):
        from cypilot.commands.update import _ensure_file
        with TemporaryDirectory() as td:
            p = Path(td) / "existing.md"
            p.write_text("old", encoding="utf-8")
            actions = {}
            _ensure_file(p, "new content", actions, "test_key")
            self.assertEqual(actions["test_key"], "preserved")
            self.assertEqual(p.read_text(encoding="utf-8"), "old")

    def test_config_readme_content(self):
        from cypilot.commands.update import _config_readme_content
        content = _config_readme_content()
        self.assertIn("config", content.lower())
        self.assertIn("core.toml", content)

    def test_read_conf_version(self):
        from cypilot.commands.update import _read_conf_version
        with TemporaryDirectory() as td:
            p = Path(td) / "conf.toml"
            _write_toml(p, {"version": 3})
            self.assertEqual(_read_conf_version(p), 3)

    def test_read_conf_version_missing(self):
        from cypilot.commands.update import _read_conf_version
        self.assertEqual(_read_conf_version(Path("/nonexistent")), 0)

    def test_read_conf_version_no_key(self):
        from cypilot.commands.update import _read_conf_version
        with TemporaryDirectory() as td:
            p = Path(td) / "conf.toml"
            _write_toml(p, {"other": "data"})
            self.assertEqual(_read_conf_version(p), 0)


# =========================================================================
# cmd_update error paths
# =========================================================================

class TestCmdUpdateErrors(unittest.TestCase):
    """Error handling in cmd_update."""

    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)

    def tearDown(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

    def test_no_project_root(self):
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            cwd = os.getcwd()
            try:
                os.chdir(td)
                buf = io.StringIO()
                err = io.StringIO()
                with redirect_stdout(buf), redirect_stderr(err):
                    rc = cmd_update([])
                self.assertEqual(rc, 1)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["status"], "ERROR")
            finally:
                os.chdir(cwd)

    def test_no_cypilot_var(self):
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            (root / "AGENTS.md").write_text("# no toml\n", encoding="utf-8")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                err = io.StringIO()
                with redirect_stdout(buf), redirect_stderr(err):
                    rc = cmd_update([])
                self.assertEqual(rc, 1)
            finally:
                os.chdir(cwd)

    def test_cypilot_dir_missing(self):
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            (root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "cpt"\n```\n<!-- /@cpt:root-agents -->\n',
                encoding="utf-8",
            )
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                err = io.StringIO()
                with redirect_stdout(buf), redirect_stderr(err):
                    rc = cmd_update([])
                self.assertEqual(rc, 1)
            finally:
                os.chdir(cwd)

    def test_no_cache(self):
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            cpt = root / "cpt"
            cpt.mkdir()
            (root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "cpt"\n```\n<!-- /@cpt:root-agents -->\n',
                encoding="utf-8",
            )
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                fake_cache = Path(td) / "nonexistent"
                with patch("cypilot.commands.update.CACHE_DIR", fake_cache):
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update([])
                self.assertEqual(rc, 1)
            finally:
                os.chdir(cwd)


# =========================================================================
# cmd_update full pipeline
# =========================================================================

class TestCmdUpdatePipeline(unittest.TestCase):
    """Full update pipeline: init then update."""

    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)

    def tearDown(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

    def test_update_after_init(self):
        """Update on a freshly initialized project succeeds."""
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            cache = Path(td) / "cache"
            _make_cache(cache)
            _init_project(root, cache)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with patch("cypilot.commands.update.CACHE_DIR", cache):
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update([])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertIn(out["status"], ["PASS", "WARN"])
                self.assertIn("actions", out)
                self.assertIn("core_update", out["actions"])
                self.assertIn("kits", out["actions"])
            finally:
                os.chdir(cwd)

    def test_update_dry_run(self):
        """--dry-run reports what would change without writing."""
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            cache = Path(td) / "cache"
            _make_cache(cache)
            _init_project(root, cache)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with patch("cypilot.commands.update.CACHE_DIR", cache):
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update(["--dry-run"])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertTrue(out["dry_run"])
            finally:
                os.chdir(cwd)

    def test_update_with_explicit_project_root(self):
        """--project-root flag works correctly."""
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            cache = Path(td) / "cache"
            _make_cache(cache)
            _init_project(root, cache)

            with patch("cypilot.commands.update.CACHE_DIR", cache):
                buf = io.StringIO()
                err = io.StringIO()
                with redirect_stdout(buf), redirect_stderr(err):
                    rc = cmd_update(["--project-root", str(root)])
            self.assertEqual(rc, 0)

    def test_update_version_drift(self):
        """When cache has newer kit version, update applies file-level diff."""
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            cache_v1 = Path(td) / "cache_v1"
            _make_cache(cache_v1, kit_version=1)
            _init_project(root, cache_v1)

            # Now update cache to v2
            cache_v2 = Path(td) / "cache_v2"
            _make_cache(cache_v2, kit_version=2)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with patch("cypilot.commands.update.CACHE_DIR", cache_v2):
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update([])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                kits = out["actions"].get("kits", {})
                sdlc_r = kits.get("sdlc", {})
                ver = sdlc_r.get("version", {})
                # Version drift runs the diff; if file content is identical, status is "current"
                self.assertIn(ver.get("status"), ["created", "updated", "current"])
            finally:
                os.chdir(cwd)

    def test_update_creates_missing_config_scaffold(self):
        """Update creates config/ scaffold files if missing."""
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            cache = Path(td) / "cache"
            _make_cache(cache)
            adapter = _init_project(root, cache)

            # Remove config scaffold files to test recreation
            for f in ["AGENTS.md", "SKILL.md", "README.md"]:
                p = adapter / "config" / f
                if p.exists():
                    p.unlink()

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with patch("cypilot.commands.update.CACHE_DIR", cache):
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update([])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                # Scaffold files should be recreated
                self.assertTrue((adapter / "config" / "AGENTS.md").is_file())
                self.assertTrue((adapter / "config" / "SKILL.md").is_file())
                self.assertTrue((adapter / "config" / "README.md").is_file())
            finally:
                os.chdir(cwd)

    def test_update_first_install_kit_content(self):
        """Update copies kit content on first install (no user kit yet)."""
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            cache = Path(td) / "cache"
            _make_cache(cache)
            adapter = _init_project(root, cache)

            # Remove kit content to simulate first install scenario
            config_kit = adapter / "config" / "kits" / "sdlc"
            if config_kit.exists():
                shutil.rmtree(config_kit)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with patch("cypilot.commands.update.CACHE_DIR", cache):
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update([])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                kits = out["actions"].get("kits", {})
                sdlc_r = kits.get("sdlc", {})
                self.assertEqual(sdlc_r.get("version", {}).get("status"), "created")
                # Kit content should now exist in config/kits/sdlc/
                self.assertTrue(config_kit.is_dir())
            finally:
                os.chdir(cwd)




class TestUpdateHelperExceptions(unittest.TestCase):
    """Cover exception paths in _read_conf_version."""

    def test_read_conf_version_corrupt_toml(self):
        from cypilot.commands.update import _read_conf_version
        with TemporaryDirectory() as td:
            p = Path(td) / "conf.toml"
            p.write_text("{{corrupt", encoding="utf-8")
            self.assertEqual(_read_conf_version(p), 0)


    def test_update_non_dir_in_kits_cache_skipped(self):
        """Files (non-dirs) in kits cache dir are skipped."""
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            cache = Path(td) / "cache"
            _make_cache(cache)
            # Add a stray file in kits/ dir
            (cache / "kits" / "README.md").write_text("stray\n", encoding="utf-8")
            _init_project(root, cache)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with patch("cypilot.commands.update.CACHE_DIR", cache):
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update([])
                self.assertEqual(rc, 0)
            finally:
                os.chdir(cwd)


# =========================================================================
# _read_core_whatsnew / _show_core_whatsnew
# =========================================================================

class TestReadCoreWhatsnew(unittest.TestCase):
    """Tests for reading standalone whatsnew.toml."""

    def test_read_valid(self):
        from cypilot.commands.update import _read_core_whatsnew
        with TemporaryDirectory() as td:
            p = Path(td) / "whatsnew.toml"
            p.write_text(
                '["v3.0.4-beta"]\nsummary = "A"\ndetails = "D1"\n\n'
                '["v3.0.5-beta"]\nsummary = "B"\ndetails = "D2"\n',
                encoding="utf-8",
            )
            result = _read_core_whatsnew(p)
            self.assertEqual(len(result), 2)
            self.assertIn("v3.0.4-beta", result)
            self.assertEqual(result["v3.0.4-beta"]["summary"], "A")
            self.assertEqual(result["v3.0.5-beta"]["details"], "D2")

    def test_read_missing_file(self):
        from cypilot.commands.update import _read_core_whatsnew
        self.assertEqual(_read_core_whatsnew(Path("/nonexistent/whatsnew.toml")), {})

    def test_read_corrupt_file(self):
        from cypilot.commands.update import _read_core_whatsnew
        with TemporaryDirectory() as td:
            p = Path(td) / "whatsnew.toml"
            p.write_text("{{invalid", encoding="utf-8")
            self.assertEqual(_read_core_whatsnew(p), {})

    def test_read_skips_non_dict_entries(self):
        from cypilot.commands.update import _read_core_whatsnew
        with TemporaryDirectory() as td:
            p = Path(td) / "whatsnew.toml"
            p.write_text(
                'scalar_key = "not a dict"\n\n'
                '["v1.0"]\nsummary = "OK"\ndetails = ""\n',
                encoding="utf-8",
            )
            result = _read_core_whatsnew(p)
            self.assertEqual(len(result), 1)
            self.assertIn("v1.0", result)


class TestShowCoreWhatsnew(unittest.TestCase):
    """Tests for core whatsnew display and prompting."""

    def test_non_interactive_shows_missing(self):
        from cypilot.commands.update import _show_core_whatsnew
        ref = {
            "v3.0.4": {"summary": "A", "details": "- d1"},
            "v3.0.5": {"summary": "B", "details": "- d2"},
        }
        err = io.StringIO()
        with redirect_stderr(err):
            result = _show_core_whatsnew(ref, {}, interactive=False)
        self.assertTrue(result)
        output = err.getvalue()
        self.assertIn("What's new", output)
        self.assertIn("A", output)
        self.assertIn("B", output)

    def test_filters_by_core_keys(self):
        """Only entries missing from .core/ whatsnew are shown."""
        from cypilot.commands.update import _show_core_whatsnew
        ref = {
            "v3.0.4": {"summary": "Old", "details": ""},
            "v3.0.5": {"summary": "New", "details": ""},
        }
        core = {"v3.0.4": {"summary": "Old", "details": ""}}
        err = io.StringIO()
        with redirect_stderr(err):
            _show_core_whatsnew(ref, core, interactive=False)
        output = err.getvalue()
        self.assertNotIn("Old", output)
        self.assertIn("New", output)

    def test_all_seen_returns_true(self):
        from cypilot.commands.update import _show_core_whatsnew
        same = {"v1": {"summary": "X", "details": ""}}
        self.assertTrue(_show_core_whatsnew(same, same, interactive=True))

    def test_empty_ref_returns_true(self):
        from cypilot.commands.update import _show_core_whatsnew
        self.assertTrue(_show_core_whatsnew({}, {}, interactive=True))

    def test_enter_continues(self):
        from cypilot.commands.update import _show_core_whatsnew
        ref = {"v1": {"summary": "X", "details": ""}}
        err = io.StringIO()
        with patch("builtins.input", return_value=""), redirect_stderr(err):
            self.assertTrue(_show_core_whatsnew(ref, {}, interactive=True))

    def test_q_aborts(self):
        from cypilot.commands.update import _show_core_whatsnew
        ref = {"v1": {"summary": "X", "details": ""}}
        err = io.StringIO()
        with patch("builtins.input", return_value="q"), redirect_stderr(err):
            self.assertFalse(_show_core_whatsnew(ref, {}, interactive=True))

    def test_eof_aborts(self):
        from cypilot.commands.update import _show_core_whatsnew
        ref = {"v1": {"summary": "X", "details": ""}}
        err = io.StringIO()
        with patch("builtins.input", side_effect=EOFError), redirect_stderr(err):
            self.assertFalse(_show_core_whatsnew(ref, {}, interactive=True))

    def test_non_interactive_auto_continues(self):
        """Non-interactive mode (CI/non-TTY) must auto-continue without blocking."""
        from cypilot.commands.update import _show_core_whatsnew
        ref = {"v1": {"summary": "X", "details": ""}}
        err = io.StringIO()
        with redirect_stderr(err):
            self.assertTrue(_show_core_whatsnew(ref, {}, interactive=False))


class TestCmdUpdateWhatsnew(unittest.TestCase):

    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)

    def tearDown(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)
    """Integration tests for core whatsnew in cmd_update pipeline."""

    def test_update_shows_whatsnew_and_copies_to_core(self):
        """Update with new whatsnew entries shows them and copies to .core/."""
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            cache = Path(td) / "cache"
            _make_cache(cache)
            # Add whatsnew.toml to cache
            (cache / "whatsnew.toml").write_text(
                '["v3.0.4"]\nsummary = "Test change"\ndetails = "- detail"\n',
                encoding="utf-8",
            )
            _init_project(root, cache)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with patch("cypilot.commands.update.CACHE_DIR", cache):
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update(["-y"])
                self.assertEqual(rc, 0)
                stderr_text = err.getvalue()
                self.assertIn("Test change", stderr_text)
                # whatsnew.toml should be copied to .core/
                core_wn = root / "cypilot" / ".core" / "whatsnew.toml"
                self.assertTrue(core_wn.is_file())
            finally:
                os.chdir(cwd)

    def test_update_second_run_no_whatsnew(self):
        """Second update with same cache → no whatsnew shown (already in .core/)."""
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            cache = Path(td) / "cache"
            _make_cache(cache)
            (cache / "whatsnew.toml").write_text(
                '["v3.0.4"]\nsummary = "Test"\ndetails = ""\n',
                encoding="utf-8",
            )
            _init_project(root, cache)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                # First update — shows whatsnew (non-interactive to avoid input())
                with patch("cypilot.commands.update.CACHE_DIR", cache):
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        cmd_update(["-y"])
                self.assertIn("Test", err.getvalue())

                # Second update — whatsnew already in .core/, nothing to show
                with patch("cypilot.commands.update.CACHE_DIR", cache):
                    buf2 = io.StringIO()
                    err2 = io.StringIO()
                    with redirect_stdout(buf2), redirect_stderr(err2):
                        rc = cmd_update([])
                self.assertEqual(rc, 0)
                self.assertNotIn("What's new", err2.getvalue())
            finally:
                os.chdir(cwd)

    def test_update_whatsnew_abort(self):
        """User types 'q' at whatsnew prompt → update aborted."""
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            cache = Path(td) / "cache"
            _make_cache(cache)
            (cache / "whatsnew.toml").write_text(
                '["v3.0.4"]\nsummary = "X"\ndetails = ""\n',
                encoding="utf-8",
            )
            _init_project(root, cache)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with patch("cypilot.commands.update.CACHE_DIR", cache), \
                     patch("builtins.input", return_value="q"), \
                     patch("sys.stdin") as mock_stdin:
                    mock_stdin.isatty.return_value = True
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update([])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["status"], "ABORTED")
                # .core/ should NOT have been updated
                core_wn = root / "cypilot" / ".core" / "whatsnew.toml"
                self.assertFalse(core_wn.is_file())
            finally:
                os.chdir(cwd)

    def test_update_dry_run_skips_whatsnew(self):
        """--dry-run skips whatsnew display entirely."""
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            cache = Path(td) / "cache"
            _make_cache(cache)
            (cache / "whatsnew.toml").write_text(
                '["v3.0.4"]\nsummary = "X"\ndetails = ""\n',
                encoding="utf-8",
            )
            _init_project(root, cache)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with patch("cypilot.commands.update.CACHE_DIR", cache):
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update(["--dry-run"])
                self.assertEqual(rc, 0)
                self.assertNotIn("What's new", err.getvalue())
            finally:
                os.chdir(cwd)


# =========================================================================
# _maybe_regenerate_agents
# =========================================================================

class TestMaybeRegenerateAgents(unittest.TestCase):
    """Tests for auto-regeneration of agent files during update."""

    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)

    def tearDown(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

    def _make_project_with_agents(self, root: Path, cache: Path) -> Path:
        """Create a project with init + generate-agents for one agent."""
        _make_cache(cache)
        cypilot_dir = _init_project(root, cache)

        # Create a fake .core/skills/cypilot/SKILL.md (needed by agents)
        skill_src = cypilot_dir / ".core" / "skills" / "cypilot" / "SKILL.md"
        skill_src.parent.mkdir(parents=True, exist_ok=True)
        skill_src.write_text(
            "---\nname: cypilot\ndescription: Test skill\n---\nContent\n",
            encoding="utf-8",
        )
        return cypilot_dir

    def test_no_changes_returns_empty(self):
        """When copy_results are all 'skipped', no agents are regenerated."""
        from cypilot.commands.update import _maybe_regenerate_agents
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            result = _maybe_regenerate_agents(
                {"architecture": "skipped", "skills": "skipped"},
                {"sdlc": {"version": {"status": "current"}}},
                root, root / "cypilot",
            )
            self.assertEqual(result, [])

    def test_core_updated_regenerates_existing_agents(self):
        """When core is updated, agents with existing files are regenerated."""
        from cypilot.commands.update import _maybe_regenerate_agents
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            (root / ".git").mkdir()
            cache = Path(td) / "cache"
            cypilot_dir = self._make_project_with_agents(root, cache)

            # Create a windsurf skill file (simulates already-installed agent)
            ws_skill = root / ".windsurf" / "skills" / "cypilot" / "SKILL.md"
            ws_skill.parent.mkdir(parents=True, exist_ok=True)
            ws_skill.write_text("old content", encoding="utf-8")

            result = _maybe_regenerate_agents(
                {"skills": "updated", "architecture": "updated"},
                {"sdlc": {"version": {"status": "current"}}},
                root, cypilot_dir,
            )
            self.assertIn("windsurf", result)
            # File should have been updated
            new_content = ws_skill.read_text(encoding="utf-8")
            self.assertNotEqual(new_content, "old content")

    def test_kit_migrated_triggers_regen(self):
        """When a kit is migrated, agents are regenerated."""
        from cypilot.commands.update import _maybe_regenerate_agents
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            (root / ".git").mkdir()
            cache = Path(td) / "cache"
            cypilot_dir = self._make_project_with_agents(root, cache)

            ws_skill = root / ".windsurf" / "skills" / "cypilot" / "SKILL.md"
            ws_skill.parent.mkdir(parents=True, exist_ok=True)
            ws_skill.write_text("old content", encoding="utf-8")

            result = _maybe_regenerate_agents(
                {"skills": "skipped"},
                {"sdlc": {"version": {"status": "migrated"}}},
                root, cypilot_dir,
            )
            self.assertIn("windsurf", result)

    def test_no_existing_agent_files_skips(self):
        """When no agent output files exist on disk, none are regenerated."""
        from cypilot.commands.update import _maybe_regenerate_agents
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            (root / ".git").mkdir()
            cache = Path(td) / "cache"
            cypilot_dir = self._make_project_with_agents(root, cache)

            # Don't create any agent files — all should be skipped
            result = _maybe_regenerate_agents(
                {"skills": "updated"},
                {},
                root, cypilot_dir,
            )
            self.assertEqual(result, [])

    def test_cmd_update_pipeline_regenerates_agents(self):
        """Full cmd_update pipeline: agents are regenerated when core updates."""
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            (root / ".git").mkdir()
            cache = Path(td) / "cache"
            cypilot_dir = self._make_project_with_agents(root, cache)

            # Create windsurf skill file (simulates already-installed agent)
            ws_skill = root / ".windsurf" / "skills" / "cypilot" / "SKILL.md"
            ws_skill.parent.mkdir(parents=True, exist_ok=True)
            ws_skill.write_text("old content", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with patch("cypilot.commands.update.CACHE_DIR", cache):
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update([])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertIn("agents_regenerated", out["actions"])
                self.assertIn("windsurf", out["actions"]["agents_regenerated"])
                # Verify file was actually updated
                new_content = ws_skill.read_text(encoding="utf-8")
                self.assertNotEqual(new_content, "old content")
            finally:
                os.chdir(cwd)

    def test_only_installed_agents_regenerated(self):
        """Only agents with existing files are regenerated, others skipped."""
        from cypilot.commands.update import _maybe_regenerate_agents
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            (root / ".git").mkdir()
            cache = Path(td) / "cache"
            cypilot_dir = self._make_project_with_agents(root, cache)

            # Only create cursor agent file
            cursor_skill = root / ".cursor" / "rules" / "cypilot.mdc"
            cursor_skill.parent.mkdir(parents=True, exist_ok=True)
            cursor_skill.write_text("old", encoding="utf-8")

            result = _maybe_regenerate_agents(
                {"skills": "updated"},
                {},
                root, cypilot_dir,
            )
            # cursor has existing file → regenerated
            self.assertIn("cursor", result)
            # windsurf has no files → not regenerated
            self.assertNotIn("windsurf", result)


class TestHumanUpdateOk(unittest.TestCase):
    """Cover _human_update_ok display branches."""

    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

    def test_basic_pass(self):
        from cypilot.commands.update import _human_update_ok
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_update_ok({
                "status": "PASS",
                "project_root": "/tmp/proj",
                "cypilot_dir": "/tmp/proj/cypilot",
                "dry_run": False,
                "actions": {},
            })
        out = buf.getvalue()
        self.assertIn("Update complete", out)

    def test_dry_run(self):
        from cypilot.commands.update import _human_update_ok
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_update_ok({
                "status": "PASS",
                "project_root": "/tmp/proj",
                "cypilot_dir": "/tmp/proj/cypilot",
                "dry_run": True,
                "actions": {},
            })
        out = buf.getvalue()
        self.assertIn("dry-run", out.lower())

    def test_with_errors_and_warnings(self):
        from cypilot.commands.update import _human_update_ok
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_update_ok({
                "status": "WARN",
                "project_root": "/tmp/proj",
                "cypilot_dir": "/tmp/proj/cypilot",
                "dry_run": False,
                "actions": {},
                "errors": [{"path": "kit.py", "error": "bad"}, "plain error"],
                "warnings": ["warn1"],
            })
        out = buf.getvalue()
        self.assertIn("bad", out)
        self.assertIn("warn1", out)
        self.assertIn("warnings", out.lower())

    def test_with_kits_data(self):
        from cypilot.commands.update import _human_update_ok
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_update_ok({
                "status": "PASS",
                "project_root": "/tmp/proj",
                "cypilot_dir": "/tmp/proj/cypilot",
                "dry_run": False,
                "actions": {
                    "kits": {
                        "sdlc": {
                            "version": {"status": "created"},
                            "gen": {"files_written": 10, "artifact_kinds": ["DESIGN"]},
                            "reference": "installed",
                        },
                        "bad": "string_value",
                    },
                },
            })
        out = buf.getvalue()
        self.assertIn("sdlc", out)
        self.assertIn("Kits", out)

    def test_with_core_update(self):
        from cypilot.commands.update import _human_update_ok
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_update_ok({
                "status": "PASS",
                "project_root": "/tmp/proj",
                "cypilot_dir": "/tmp/proj/cypilot",
                "dry_run": False,
                "actions": {
                    "core_update": {"architecture/": "updated", "skills/": "created"},
                    "file.md": "created",
                    "other.md": "updated",
                    "keep.md": "unchanged",
                },
            })
        out = buf.getvalue()
        self.assertIn("Core", out)
        self.assertIn("Created", out)
        self.assertIn("Updated", out)

    def test_with_agents_regenerated(self):
        from cypilot.commands.update import _human_update_ok
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_update_ok({
                "status": "PASS",
                "project_root": "/tmp/proj",
                "cypilot_dir": "/tmp/proj/cypilot",
                "dry_run": False,
                "actions": {
                    "agents_regenerated": ["cursor", "windsurf"],
                },
            })
        out = buf.getvalue()
        self.assertIn("cursor", out)

    def test_with_dict_and_list_actions(self):
        from cypilot.commands.update import _human_update_ok
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_update_ok({
                "status": "PASS",
                "project_root": "/tmp/proj",
                "cypilot_dir": "/tmp/proj/cypilot",
                "dry_run": False,
                "actions": {
                    "layout_migration": {"sdlc": "migrated"},
                    "extra_list": ["item1", "item2"],
                },
            })
        out = buf.getvalue()
        self.assertIn("layout_migration", out)
        self.assertIn("sdlc", out)
        self.assertIn("extra_list", out)
        self.assertIn("item1", out)


if __name__ == "__main__":
    unittest.main()
