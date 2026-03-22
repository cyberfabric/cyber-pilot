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
    """Run init to create a fully initialized project.

    Mocks GitHub download to use cache kit source (via a temp copy so init's
    cleanup of the download dir doesn't destroy the cache).
    Strips GitHub source from core.toml so cmd_update uses cache fallback.
    """
    from cypilot.cli import main
    import tempfile
    (root / ".git").mkdir(exist_ok=True)
    # Copy kit source to a temp dir — init will delete kit_src.parent after install
    tmp_dl = Path(tempfile.mkdtemp())
    kit_copy = tmp_dl / "sdlc"
    shutil.copytree(cache_dir / "kits" / "sdlc", kit_copy)
    cwd = os.getcwd()
    try:
        os.chdir(str(root))
        with (
            patch("cypilot.commands.init.CACHE_DIR", cache_dir),
            patch(
                "cypilot.commands.kit._download_kit_from_github",
                return_value=(kit_copy, "1.0.0"),
            ),
        ):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["init", "--yes"])
            assert rc == 0, f"init failed: {buf.getvalue()}"
    finally:
        os.chdir(cwd)
    # Remove GitHub source from core.toml so cmd_update uses cache fallback
    adapter = root / "cypilot"
    core_toml = adapter / "config" / "core.toml"
    if core_toml.is_file():
        import tomllib
        from cypilot.utils import toml_utils
        with open(core_toml, "rb") as f:
            data = tomllib.load(f)
        for kit_data in data.get("kits", {}).values():
            kit_data.pop("source", None)
        toml_utils.dump(data, core_toml)
    return adapter


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
            kit_src_v2 = cache_v2 / "kits" / "sdlc"

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with (
                    patch("cypilot.commands.update.CACHE_DIR", cache_v2),
                    patch(
                        "cypilot.commands.kit._download_kit_from_github",
                        return_value=(kit_src_v2, "2"),
                    ),
                ):
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

            kit_src = cache / "kits" / "sdlc"
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with (
                    patch("cypilot.commands.update.CACHE_DIR", cache),
                    patch(
                        "cypilot.commands.kit._download_kit_from_github",
                        return_value=(kit_src, "1"),
                    ),
                ):
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
# read_whatsnew / show_core_whatsnew (moved to cypilot.utils.whatsnew)
# =========================================================================

class TestReadCoreWhatsnew(unittest.TestCase):
    """Tests for reading standalone whatsnew.toml."""

    def test_read_valid(self):
        from cypilot.utils.whatsnew import read_whatsnew as _read_core_whatsnew
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
        from cypilot.utils.whatsnew import read_whatsnew as _read_core_whatsnew
        self.assertEqual(_read_core_whatsnew(Path("/nonexistent/whatsnew.toml")), {})

    def test_read_corrupt_file(self):
        from cypilot.utils.whatsnew import read_whatsnew as _read_core_whatsnew
        with TemporaryDirectory() as td:
            p = Path(td) / "whatsnew.toml"
            p.write_text("{{invalid", encoding="utf-8")
            self.assertEqual(_read_core_whatsnew(p), {})

    def test_read_skips_non_dict_entries(self):
        from cypilot.utils.whatsnew import read_whatsnew as _read_core_whatsnew
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

    def test_read_whatsnew_section_format(self):
        """Test reading whatsnew.toml with [whatsnew."X.Y.Z"] format."""
        from cypilot.utils.whatsnew import read_whatsnew
        with TemporaryDirectory() as td:
            p = Path(td) / "whatsnew.toml"
            p.write_text(
                '[whatsnew."1.2.0"]\nsummary = "New feature"\ndetails = "- Added X"\n\n'
                '[whatsnew."1.3.0"]\nsummary = "Bug fix"\ndetails = "- Fixed Y"\n',
                encoding="utf-8",
            )
            result = read_whatsnew(p)
            self.assertEqual(len(result), 2)
            self.assertIn("1.2.0", result)
            self.assertIn("1.3.0", result)
            self.assertEqual(result["1.2.0"]["summary"], "New feature")
            self.assertEqual(result["1.3.0"]["details"], "- Fixed Y")


class TestWhatsnewVersionParsing(unittest.TestCase):
    """Tests for semver parsing and comparison in whatsnew module."""

    def test_parse_semver_basic(self):
        from cypilot.utils.whatsnew import parse_semver
        self.assertEqual(parse_semver("1.2.3"), (1, 2, 3, 1))
        self.assertEqual(parse_semver("0.0.1"), (0, 0, 1, 1))
        self.assertEqual(parse_semver("10.20.30"), (10, 20, 30, 1))

    def test_parse_semver_with_v_prefix(self):
        from cypilot.utils.whatsnew import parse_semver
        self.assertEqual(parse_semver("v1.2.3"), (1, 2, 3, 1))
        self.assertEqual(parse_semver("v0.1.0"), (0, 1, 0, 1))

    def test_parse_semver_with_whatsnew_prefix(self):
        from cypilot.utils.whatsnew import parse_semver
        self.assertEqual(parse_semver("whatsnew.1.2.3"), (1, 2, 3, 1))

    def test_parse_semver_partial(self):
        from cypilot.utils.whatsnew import parse_semver
        self.assertEqual(parse_semver("1.2"), (1, 2, 0, 1))
        self.assertEqual(parse_semver("1"), (1, 0, 0, 1))

    def test_parse_semver_prerelease_does_not_collapse_to_zero(self):
        from cypilot.utils.whatsnew import parse_semver
        self.assertNotEqual(parse_semver("v3.0.4-beta"), (0, 0, 0))

    def test_parse_semver_invalid(self):
        from cypilot.utils.whatsnew import parse_semver
        self.assertEqual(parse_semver("invalid"), (0, 0, 0))
        self.assertEqual(parse_semver("a.b.c"), (0, 0, 0))
        self.assertEqual(parse_semver(""), (0, 0, 0))

    def test_compare_versions_less_than(self):
        from cypilot.utils.whatsnew import compare_versions
        self.assertEqual(compare_versions("1.0.0", "2.0.0"), -1)
        self.assertEqual(compare_versions("1.0.0", "1.1.0"), -1)
        self.assertEqual(compare_versions("1.0.0", "1.0.1"), -1)

    def test_compare_versions_greater_than(self):
        from cypilot.utils.whatsnew import compare_versions
        self.assertEqual(compare_versions("2.0.0", "1.0.0"), 1)
        self.assertEqual(compare_versions("1.1.0", "1.0.0"), 1)
        self.assertEqual(compare_versions("1.0.1", "1.0.0"), 1)

    def test_compare_versions_equal(self):
        from cypilot.utils.whatsnew import compare_versions
        self.assertEqual(compare_versions("1.0.0", "1.0.0"), 0)
        self.assertEqual(compare_versions("v1.0.0", "1.0.0"), 0)

    def test_compare_versions_prerelease_sorts_before_release(self):
        from cypilot.utils.whatsnew import compare_versions
        self.assertEqual(compare_versions("v3.0.4-beta", "v3.0.4"), -1)


class TestShowKitWhatsnew(unittest.TestCase):
    """Tests for kit-specific whatsnew display."""

    def test_no_whatsnew_file_returns_true(self):
        from cypilot.utils.whatsnew import show_kit_whatsnew
        with TemporaryDirectory() as td:
            kit_dir = Path(td)
            result = show_kit_whatsnew(kit_dir, "1.0.0", "test-kit", interactive=False)
            self.assertTrue(result)

    def test_no_new_entries_returns_true(self):
        from cypilot.utils.whatsnew import show_kit_whatsnew
        with TemporaryDirectory() as td:
            kit_dir = Path(td)
            (kit_dir / "whatsnew.toml").write_text(
                '[whatsnew."1.0.0"]\nsummary = "Old"\ndetails = ""\n',
                encoding="utf-8",
            )
            # installed version is same or newer
            result = show_kit_whatsnew(kit_dir, "1.0.0", "test-kit", interactive=False)
            self.assertTrue(result)

    def test_shows_new_entries(self):
        from cypilot.utils.whatsnew import show_kit_whatsnew
        with TemporaryDirectory() as td:
            kit_dir = Path(td)
            (kit_dir / "whatsnew.toml").write_text(
                '[whatsnew."1.1.0"]\nsummary = "New feature"\ndetails = "- Added X"\n'
                '[whatsnew."1.2.0"]\nsummary = "Bug fix"\ndetails = ""\n',
                encoding="utf-8",
            )
            err = io.StringIO()
            with redirect_stderr(err):
                result = show_kit_whatsnew(kit_dir, "1.0.0", "test-kit", interactive=False)
            self.assertTrue(result)
            output = err.getvalue()
            self.assertIn("What's new in test-kit kit", output)
            self.assertIn("New feature", output)
            self.assertIn("Bug fix", output)

    def test_tty_ansi_formatting_plain_summary(self):
        """Test ANSI formatting when summary has no markdown."""
        from cypilot.utils.whatsnew import show_kit_whatsnew
        with TemporaryDirectory() as td:
            kit_dir = Path(td)
            (kit_dir / "whatsnew.toml").write_text(
                '[whatsnew."1.1.0"]\nsummary = "Plain summary"\ndetails = ""\n',
                encoding="utf-8",
            )
            err = io.StringIO()
            with patch("cypilot.utils.whatsnew.stderr_supports_ansi", return_value=True):
                with redirect_stderr(err):
                    show_kit_whatsnew(kit_dir, "1.0.0", "test-kit", interactive=False)
            output = err.getvalue()
            # Should have ANSI bold around version and summary
            self.assertIn("\033[1m1.1.0: Plain summary\033[0m", output)

    def test_filters_old_versions(self):
        from cypilot.utils.whatsnew import show_kit_whatsnew
        with TemporaryDirectory() as td:
            kit_dir = Path(td)
            (kit_dir / "whatsnew.toml").write_text(
                '[whatsnew."1.0.0"]\nsummary = "Old"\ndetails = ""\n'
                '[whatsnew."1.2.0"]\nsummary = "New"\ndetails = ""\n',
                encoding="utf-8",
            )
            err = io.StringIO()
            with redirect_stderr(err):
                show_kit_whatsnew(kit_dir, "1.1.0", "test-kit", interactive=False)
            output = err.getvalue()
            self.assertNotIn("Old", output)
            self.assertIn("New", output)

    def test_missing_version_treated_as_zero(self):
        from cypilot.utils.whatsnew import show_kit_whatsnew
        with TemporaryDirectory() as td:
            kit_dir = Path(td)
            (kit_dir / "whatsnew.toml").write_text(
                '[whatsnew."0.0.1"]\nsummary = "Initial"\ndetails = ""\n',
                encoding="utf-8",
            )
            err = io.StringIO()
            with redirect_stderr(err):
                result = show_kit_whatsnew(kit_dir, "", "test-kit", interactive=False)
            self.assertTrue(result)
            output = err.getvalue()
            self.assertIn("Initial", output)

    def test_interactive_q_aborts(self):
        from cypilot.utils.whatsnew import show_kit_whatsnew
        with TemporaryDirectory() as td:
            kit_dir = Path(td)
            (kit_dir / "whatsnew.toml").write_text(
                '[whatsnew."1.1.0"]\nsummary = "New"\ndetails = ""\n',
                encoding="utf-8",
            )
            err = io.StringIO()
            with patch("builtins.input", return_value="q"), redirect_stderr(err):
                result = show_kit_whatsnew(kit_dir, "1.0.0", "test-kit", interactive=True)
            self.assertFalse(result)

    def test_interactive_enter_continues(self):
        from cypilot.utils.whatsnew import show_kit_whatsnew
        with TemporaryDirectory() as td:
            kit_dir = Path(td)
            (kit_dir / "whatsnew.toml").write_text(
                '[whatsnew."1.1.0"]\nsummary = "New"\ndetails = ""\n',
                encoding="utf-8",
            )
            err = io.StringIO()
            with patch("builtins.input", return_value=""), redirect_stderr(err):
                result = show_kit_whatsnew(kit_dir, "1.0.0", "test-kit", interactive=True)
            self.assertTrue(result)


class TestShowCoreWhatsnew(unittest.TestCase):
    """Tests for core whatsnew display and prompting."""

    def test_non_interactive_shows_missing(self):
        from cypilot.utils.whatsnew import show_core_whatsnew as _show_core_whatsnew
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

    def test_non_interactive_renders_bold_markdown_in_summary(self):
        from cypilot.utils.whatsnew import show_core_whatsnew as _show_core_whatsnew
        ref = {
            "v3.2.0-beta": {
                "summary": "Prompt **compactification** release",
                "details": "",
            },
        }
        err = io.StringIO()
        with redirect_stderr(err):
            result = _show_core_whatsnew(ref, {}, interactive=False)
        self.assertTrue(result)
        output = err.getvalue()
        self.assertIn("Prompt compactification release", output)
        self.assertNotIn("**compactification**", output)
        self.assertNotIn("\033[1mcompactification\033[0m", output)

    def test_non_interactive_renders_bold_markdown_in_details(self):
        from cypilot.utils.whatsnew import show_core_whatsnew as _show_core_whatsnew
        ref = {
            "v3.2.0-beta": {
                "summary": "Prompt compactification",
                "details": "- **Aggressive** prompt compactification release",
            },
        }
        err = io.StringIO()
        with redirect_stderr(err):
            result = _show_core_whatsnew(ref, {}, interactive=False)
        self.assertTrue(result)
        output = err.getvalue()
        self.assertIn("- Aggressive prompt compactification release", output)
        self.assertNotIn("**Aggressive**", output)
        self.assertNotIn("\033[1mAggressive\033[0m", output)

    def test_non_interactive_renders_inline_code_in_summary(self):
        from cypilot.utils.whatsnew import show_core_whatsnew as _show_core_whatsnew
        ref = {
            "v3.2.0-beta": {
                "summary": "Use `workflows/analyze.md` for compact analysis",
                "details": "",
            },
        }
        err = io.StringIO()
        with redirect_stderr(err):
            result = _show_core_whatsnew(ref, {}, interactive=False)
        self.assertTrue(result)
        output = err.getvalue()
        self.assertIn("Use workflows/analyze.md for compact analysis", output)
        self.assertNotIn("`workflows/analyze.md`", output)
        self.assertNotIn("\033[36mworkflows/analyze.md\033[0m", output)

    def test_non_interactive_renders_inline_code_in_details(self):
        from cypilot.utils.whatsnew import show_core_whatsnew as _show_core_whatsnew
        ref = {
            "v3.2.0-beta": {
                "summary": "Prompt compactification",
                "details": "- Updated `skills/cypilot/SKILL.md` and `requirements/workspace.md`",
            },
        }
        err = io.StringIO()
        with redirect_stderr(err):
            result = _show_core_whatsnew(ref, {}, interactive=False)
        self.assertTrue(result)
        output = err.getvalue()
        self.assertIn("- Updated skills/cypilot/SKILL.md and requirements/workspace.md", output)
        self.assertNotIn("`skills/cypilot/SKILL.md`", output)
        self.assertNotIn("\033[36mskills/cypilot/SKILL.md\033[0m", output)

    def test_non_interactive_tty_renders_ansi_markup(self):
        from cypilot.utils.whatsnew import show_core_whatsnew as _show_core_whatsnew
        ref = {
            "v3.2.0-beta": {
                "summary": "Prompt **compactification** release in `workflows/analyze.md`",
                "details": "",
            },
        }
        err = io.StringIO()
        with patch("cypilot.utils.whatsnew.stderr_supports_ansi", return_value=True):
            with redirect_stderr(err):
                result = _show_core_whatsnew(ref, {}, interactive=False)
        self.assertTrue(result)
        output = err.getvalue()
        self.assertIn("\033[1mcompactification\033[0m", output)
        self.assertIn("\033[36mworkflows/analyze.md\033[0m", output)

    def test_non_interactive_strips_control_chars_from_summary_and_details(self):
        from cypilot.utils.whatsnew import show_core_whatsnew as _show_core_whatsnew
        ref = {
            "v3.2.0\x1b[2J": {
                "summary": "Safe\x1b[31m summary",
                "details": "- detail\x1b[2K\n- second\x07 line",
            },
        }
        err = io.StringIO()
        with redirect_stderr(err):
            result = _show_core_whatsnew(ref, {}, interactive=False)
        self.assertTrue(result)
        output = err.getvalue()
        self.assertIn("v3.2.0: Safe summary", output)
        self.assertIn("- detail", output)
        self.assertIn("- second line", output)
        self.assertNotIn("\x1b", output)
        self.assertNotIn("\x07", output)

    def test_filters_by_core_keys(self):
        """Only entries missing from .core/ whatsnew are shown."""
        from cypilot.utils.whatsnew import show_core_whatsnew as _show_core_whatsnew
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

    def test_missing_entries_are_sorted_semantically(self):
        from cypilot.utils.whatsnew import show_core_whatsnew as _show_core_whatsnew

        ref = {
            "1.10.0": {"summary": "Tenth minor", "details": ""},
            "1.9.0": {"summary": "Ninth minor", "details": ""},
        }
        err = io.StringIO()
        with redirect_stderr(err):
            _show_core_whatsnew(ref, {}, interactive=False)
        output = err.getvalue()
        self.assertLess(output.index("1.9.0"), output.index("1.10.0"))

    def test_all_seen_returns_true(self):
        from cypilot.utils.whatsnew import show_core_whatsnew as _show_core_whatsnew
        same = {"v1": {"summary": "X", "details": ""}}
        self.assertTrue(_show_core_whatsnew(same, same, interactive=True))

    def test_empty_ref_returns_true(self):
        from cypilot.utils.whatsnew import show_core_whatsnew as _show_core_whatsnew
        self.assertTrue(_show_core_whatsnew({}, {}, interactive=True))

    def test_enter_continues(self):
        from cypilot.utils.whatsnew import show_core_whatsnew as _show_core_whatsnew
        ref = {"v1": {"summary": "X", "details": ""}}
        err = io.StringIO()
        with patch("builtins.input", return_value=""), redirect_stderr(err):
            self.assertTrue(_show_core_whatsnew(ref, {}, interactive=True))

    def test_q_aborts(self):
        from cypilot.utils.whatsnew import show_core_whatsnew as _show_core_whatsnew
        ref = {"v1": {"summary": "X", "details": ""}}
        err = io.StringIO()
        with patch("builtins.input", return_value="q"), redirect_stderr(err):
            self.assertFalse(_show_core_whatsnew(ref, {}, interactive=True))

    def test_eof_aborts(self):
        from cypilot.utils.whatsnew import show_core_whatsnew as _show_core_whatsnew
        ref = {"v1": {"summary": "X", "details": ""}}
        err = io.StringIO()
        with patch("builtins.input", side_effect=EOFError), redirect_stderr(err):
            self.assertFalse(_show_core_whatsnew(ref, {}, interactive=True))

    def test_non_interactive_auto_continues(self):
        """Non-interactive mode (CI/non-TTY) must auto-continue without blocking."""
        from cypilot.utils.whatsnew import show_core_whatsnew as _show_core_whatsnew
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

    def test_update_shows_kit_whatsnew(self):
        """Main cmd_update flow shows kit whatsnew before updating the kit."""
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            cache_v1 = Path(td) / "cache_v1"
            _make_cache(cache_v1, kit_version=1)
            _init_project(root, cache_v1)

            cache_v2 = Path(td) / "cache_v2"
            _make_cache(cache_v2, kit_version=2)
            (cache_v2 / "kits" / "sdlc" / "whatsnew.toml").write_text(
                '[whatsnew."2.0.0"]\nsummary = "Kit update"\ndetails = "- Added feature"\n',
                encoding="utf-8",
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with patch("cypilot.commands.update.CACHE_DIR", cache_v2), \
                     patch(
                         "cypilot.commands.kit._read_kits_from_core_toml",
                         return_value={"sdlc": {"path": "config/kits/sdlc"}},
                     ), \
                     patch("cypilot.commands.kit._read_kit_version_from_core", return_value="1"), \
                     patch(
                         "cypilot.commands.kit.update_kit",
                         return_value={"version": {"status": "current"}, "gen": {"files_written": 0}},
                     ) as mock_update, \
                     patch("cypilot.commands.update.show_kit_whatsnew", return_value=True) as mock_show:
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update(["-y"])
                self.assertEqual(rc, 0)
                mock_show.assert_called()
                mock_update.assert_called()
            finally:
                os.chdir(cwd)

    def test_update_kit_whatsnew_abort_skips_kit_update(self):
        """Aborting kit whatsnew in cmd_update skips that kit update."""
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            cache_v1 = Path(td) / "cache_v1"
            _make_cache(cache_v1, kit_version=1)
            adapter = _init_project(root, cache_v1)
            original_skill = (adapter / "config" / "kits" / "sdlc" / "SKILL.md").read_text(encoding="utf-8")

            cache_v2 = Path(td) / "cache_v2"
            _make_cache(cache_v2, kit_version=2)
            (cache_v2 / "kits" / "sdlc" / "SKILL.md").write_text(
                "# Kit sdlc\nUpdated skill instructions.\n",
                encoding="utf-8",
            )
            (cache_v2 / "kits" / "sdlc" / "whatsnew.toml").write_text(
                '[whatsnew."2.0.0"]\nsummary = "Kit update"\ndetails = ""\n',
                encoding="utf-8",
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with patch("cypilot.commands.update.CACHE_DIR", cache_v2), \
                     patch(
                         "cypilot.commands.kit._read_kits_from_core_toml",
                         return_value={"sdlc": {"path": "config/kits/sdlc"}},
                     ), \
                     patch("cypilot.commands.kit._read_kit_version_from_core", return_value="1"), \
                     patch("cypilot.commands.kit.update_kit") as mock_update, \
                     patch("cypilot.commands.update.show_kit_whatsnew", return_value=False), \
                     patch("sys.stdin") as mock_stdin:
                    mock_stdin.isatty.return_value = True
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update([])
                self.assertEqual(rc, 0)
                mock_update.assert_not_called()
                updated_skill = (adapter / "config" / "kits" / "sdlc" / "SKILL.md").read_text(encoding="utf-8")
                self.assertEqual(updated_skill, original_skill)
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


# ---------------------------------------------------------------------------
# _deduplicate_legacy_kits
# ---------------------------------------------------------------------------

class TestDeduplicateLegacyKits(unittest.TestCase):
    def test_no_core_toml(self):
        from cypilot.commands.update import _deduplicate_legacy_kits
        self.assertEqual(_deduplicate_legacy_kits(Path("/nonexistent")), {})

    def test_no_legacy_slugs(self):
        from cypilot.commands.update import _deduplicate_legacy_kits
        from cypilot.utils import toml_utils
        with TemporaryDirectory() as td:
            config = Path(td)
            toml_utils.dump({"kits": {"sdlc": {"path": "config/kits/sdlc"}}}, config / "core.toml")
            self.assertEqual(_deduplicate_legacy_kits(config), {})

    def test_dedup_same_path(self):
        """When cypilot-sdlc and sdlc both exist with same path, legacy is removed."""
        from cypilot.commands.update import _deduplicate_legacy_kits
        from cypilot.utils import toml_utils
        import tomllib
        with TemporaryDirectory() as td:
            config = Path(td)
            toml_utils.dump({
                "kits": {
                    "cypilot-sdlc": {"path": "config/kits/sdlc", "format": "Cypilot"},
                    "sdlc": {"path": "config/kits/sdlc", "format": "Cypilot"},
                },
            }, config / "core.toml")
            result = _deduplicate_legacy_kits(config)
            self.assertEqual(result, {"cypilot-sdlc": "sdlc"})
            with open(config / "core.toml", "rb") as f:
                data = tomllib.load(f)
            self.assertNotIn("cypilot-sdlc", data["kits"])
            self.assertIn("sdlc", data["kits"])

    def test_dedup_different_paths_skipped(self):
        from cypilot.commands.update import _deduplicate_legacy_kits
        from cypilot.utils import toml_utils
        with TemporaryDirectory() as td:
            config = Path(td)
            toml_utils.dump({
                "kits": {
                    "cypilot-sdlc": {"path": "kits/cypilot-sdlc"},
                    "sdlc": {"path": "config/kits/sdlc"},
                },
            }, config / "core.toml")
            result = _deduplicate_legacy_kits(config)
            self.assertEqual(result, {})

    def test_dedup_updates_artifacts_toml(self):
        from cypilot.commands.update import _deduplicate_legacy_kits
        from cypilot.utils import toml_utils
        import tomllib
        with TemporaryDirectory() as td:
            config = Path(td)
            toml_utils.dump({
                "kits": {
                    "cypilot-sdlc": {"path": "config/kits/sdlc"},
                    "sdlc": {"path": "config/kits/sdlc"},
                },
            }, config / "core.toml")
            toml_utils.dump({
                "systems": [{"name": "default", "kit": "cypilot-sdlc"}],
            }, config / "artifacts.toml")
            _deduplicate_legacy_kits(config)
            with open(config / "artifacts.toml", "rb") as f:
                art = tomllib.load(f)
            self.assertEqual(art["systems"][0]["kit"], "sdlc")

    def test_artifacts_toml_fixed_even_without_core_dedup(self):
        """artifacts.toml legacy slug is fixed even when core.toml has only canonical slug."""
        from cypilot.commands.update import _deduplicate_legacy_kits
        from cypilot.utils import toml_utils
        import tomllib
        with TemporaryDirectory() as td:
            config = Path(td)
            # core.toml only has canonical slug — no dedup needed
            toml_utils.dump({
                "kits": {
                    "sdlc": {"path": "config/kits/sdlc"},
                },
            }, config / "core.toml")
            # artifacts.toml still references the legacy slug
            toml_utils.dump({
                "systems": [{"name": "Myapp", "slug": "myapp", "kit": "cypilot-sdlc"}],
            }, config / "artifacts.toml")
            result = _deduplicate_legacy_kits(config)
            self.assertEqual(result, {"cypilot-sdlc": "sdlc"})
            with open(config / "artifacts.toml", "rb") as f:
                art = tomllib.load(f)
            self.assertEqual(art["systems"][0]["kit"], "sdlc")


# ---------------------------------------------------------------------------
# _migrate_kit_sources
# ---------------------------------------------------------------------------

class TestMigrateKitSources(unittest.TestCase):
    def test_no_core_toml(self):
        from cypilot.commands.update import _migrate_kit_sources
        self.assertEqual(_migrate_kit_sources(Path("/nonexistent")), {})

    def test_already_has_source(self):
        from cypilot.commands.update import _migrate_kit_sources
        from cypilot.utils import toml_utils
        with TemporaryDirectory() as td:
            config = Path(td)
            toml_utils.dump({
                "kits": {"sdlc": {"source": "github:cyberfabric/cyber-pilot-kit-sdlc"}},
            }, config / "core.toml")
            self.assertEqual(_migrate_kit_sources(config), {})

    def test_adds_known_source(self):
        from cypilot.commands.update import _migrate_kit_sources
        from cypilot.utils import toml_utils
        import tomllib
        with TemporaryDirectory() as td:
            config = Path(td)
            toml_utils.dump({
                "kits": {"sdlc": {"path": "config/kits/sdlc"}},
            }, config / "core.toml")
            result = _migrate_kit_sources(config)
            self.assertEqual(result, {"sdlc": "github:cyberfabric/cyber-pilot-kit-sdlc"})
            with open(config / "core.toml", "rb") as f:
                data = tomllib.load(f)
            self.assertEqual(data["kits"]["sdlc"]["source"], "github:cyberfabric/cyber-pilot-kit-sdlc")

    def test_unknown_kit_skipped(self):
        from cypilot.commands.update import _migrate_kit_sources
        from cypilot.utils import toml_utils
        with TemporaryDirectory() as td:
            config = Path(td)
            toml_utils.dump({
                "kits": {"custom": {"path": "config/kits/custom"}},
            }, config / "core.toml")
            self.assertEqual(_migrate_kit_sources(config), {})

    def test_corrupt_core_toml(self):
        from cypilot.commands.update import _migrate_kit_sources
        with TemporaryDirectory() as td:
            (Path(td) / "core.toml").write_text("{{bad", encoding="utf-8")
            self.assertEqual(_migrate_kit_sources(Path(td)), {})


# ---------------------------------------------------------------------------
# Human formatter edge cases
# ---------------------------------------------------------------------------

class TestHumanUpdateOkEdgeCases(unittest.TestCase):
    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

    def test_kit_updated_status(self):
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
                            "version": {"status": "updated"},
                            "gen": {"files_written": 2, "accepted_files": ["a.md", "b.md"]},
                            "gen_rejected": ["c.md"],
                        },
                    },
                },
            })
        out = buf.getvalue()
        self.assertIn("updated", out)
        self.assertIn("a.md", out)
        self.assertIn("c.md", out)

    def test_kit_partial_status(self):
        from cypilot.commands.update import _human_update_ok
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_update_ok({
                "status": "WARN",
                "project_root": "/tmp/proj",
                "cypilot_dir": "/tmp/proj/cypilot",
                "dry_run": False,
                "actions": {
                    "kits": {
                        "sdlc": {
                            "version": {"status": "partial"},
                            "gen": {"files_written": 1, "accepted_files": ["a.md"]},
                            "gen_rejected": ["b.md", "c.md"],
                        },
                    },
                },
                "warnings": ["some warning"],
            })
        out = buf.getvalue()
        self.assertIn("partial", out)
        self.assertIn("declined", out)

    def test_dry_run_output(self):
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
        self.assertIn("Dry run", out)

    def test_nested_dict_action(self):
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
                    "some_list": ["item1"],
                    "nested_complex": {"sub": {"deep": True}},
                },
            })
        out = buf.getvalue()
        self.assertIn("layout_migration", out)
        self.assertIn("some_list", out)

    def test_errors_in_output(self):
        from cypilot.commands.update import _human_update_ok
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_update_ok({
                "status": "WARN",
                "project_root": "/tmp/proj",
                "cypilot_dir": "/tmp/proj/cypilot",
                "dry_run": False,
                "actions": {},
                "errors": [
                    {"path": "sdlc", "error": "download failed"},
                    "plain error string",
                ],
                "warnings": ["w1"],
            })
        out = buf.getvalue()
        self.assertIn("download failed", out)
        self.assertIn("plain error string", out)


# ---------------------------------------------------------------------------
# cmd_update with layout migration + kit source migration paths
# ---------------------------------------------------------------------------

class TestCmdUpdateLayoutMigration(unittest.TestCase):
    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)

    def tearDown(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

    def test_update_triggers_layout_migration(self):
        """cmd_update migrates old kits/ layout to config/kits/."""
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            cache = Path(td) / "cache"
            _make_cache(cache)
            adapter = _init_project(root, cache)

            # Create old layout: cypilot/kits/sdlc/ directory
            old_kits = adapter / "kits" / "sdlc"
            old_kits.mkdir(parents=True)
            (old_kits / "conf.toml").write_text("version = 1\n", encoding="utf-8")
            (old_kits / "artifacts").mkdir()
            (old_kits / "artifacts" / "old.md").write_text("# old\n", encoding="utf-8")

            kit_src = cache / "kits" / "sdlc"
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with (
                    patch("cypilot.commands.update.CACHE_DIR", cache),
                    patch(
                        "cypilot.commands.kit._download_kit_from_github",
                        return_value=(kit_src, "1"),
                    ),
                ):
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update([])
                self.assertEqual(rc, 0)
                # Old kits/ dir should be removed
                self.assertFalse(old_kits.exists())
            finally:
                os.chdir(cwd)

    def test_update_download_failure(self):
        """When GitHub download fails, update continues with errors."""
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            cache = Path(td) / "cache"
            _make_cache(cache)
            adapter = _init_project(root, cache)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with (
                    patch("cypilot.commands.update.CACHE_DIR", cache),
                    patch(
                        "cypilot.commands.kit._download_kit_from_github",
                        side_effect=RuntimeError("rate limit"),
                    ),
                ):
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update([])
                # May warn but shouldn't crash
                self.assertIn(rc, [0, 1])
            finally:
                os.chdir(cwd)


# ---------------------------------------------------------------------------
# _cleanup_legacy_blueprint_dirs (ADR-0001)
# ---------------------------------------------------------------------------

class TestCleanupLegacyBlueprintDirs(unittest.TestCase):
    """Tests for removing leftover blueprints/ from config/kits/*/."""

    def test_removes_blueprints_dir(self):
        from cypilot.commands.update import _cleanup_legacy_blueprint_dirs
        with TemporaryDirectory() as td:
            config = Path(td)
            bp = config / "kits" / "sdlc" / "blueprints"
            bp.mkdir(parents=True)
            (bp / "PRD.md").write_text("# old blueprint\n", encoding="utf-8")
            _cleanup_legacy_blueprint_dirs(config)
            self.assertFalse(bp.exists())
            # Kit dir itself should remain
            self.assertTrue((config / "kits" / "sdlc").is_dir())

    def test_noop_when_no_blueprints(self):
        from cypilot.commands.update import _cleanup_legacy_blueprint_dirs
        with TemporaryDirectory() as td:
            config = Path(td)
            kit = config / "kits" / "sdlc"
            kit.mkdir(parents=True)
            (kit / "SKILL.md").write_text("# skill\n", encoding="utf-8")
            _cleanup_legacy_blueprint_dirs(config)
            self.assertTrue((kit / "SKILL.md").is_file())

    def test_noop_when_no_kits_dir(self):
        from cypilot.commands.update import _cleanup_legacy_blueprint_dirs
        with TemporaryDirectory() as td:
            config = Path(td)
            _cleanup_legacy_blueprint_dirs(config)  # should not raise


# ---------------------------------------------------------------------------
# _remove_system_from_core_toml (ADR-0014)
# ---------------------------------------------------------------------------

class TestRemoveSystemFromCoreToml(unittest.TestCase):
    """Tests for the [system] removal migration step."""

    def test_removes_system_section(self):
        from cypilot.commands.update import _remove_system_from_core_toml
        with TemporaryDirectory() as td:
            config_dir = Path(td)
            _write_toml(config_dir / "core.toml", {
                "version": "1.0",
                "project_root": "..",
                "system": {"name": "Test", "slug": "test", "kit": "sdlc"},
                "kits": {"sdlc": {"format": "Cypilot", "path": "config/kits/sdlc"}},
            })
            result = _remove_system_from_core_toml(config_dir)
            self.assertTrue(result)

            from cypilot.utils import toml_utils
            core = toml_utils.load(config_dir / "core.toml")
            self.assertNotIn("system", core)
            self.assertEqual(core["version"], "1.0")
            self.assertIn("sdlc", core["kits"])

    def test_no_system_section_is_noop(self):
        from cypilot.commands.update import _remove_system_from_core_toml
        with TemporaryDirectory() as td:
            config_dir = Path(td)
            _write_toml(config_dir / "core.toml", {
                "version": "1.0",
                "project_root": "..",
                "kits": {},
            })
            result = _remove_system_from_core_toml(config_dir)
            self.assertFalse(result)

    def test_missing_core_toml(self):
        from cypilot.commands.update import _remove_system_from_core_toml
        result = _remove_system_from_core_toml(Path("/nonexistent"))
        self.assertFalse(result)

    def test_corrupt_core_toml(self):
        from cypilot.commands.update import _remove_system_from_core_toml
        with TemporaryDirectory() as td:
            config_dir = Path(td)
            (config_dir / "core.toml").write_text("{{invalid", encoding="utf-8")
            result = _remove_system_from_core_toml(config_dir)
            self.assertFalse(result)


# ---------------------------------------------------------------------------
# _default_core_toml (ADR-0014)
# ---------------------------------------------------------------------------

class TestDefaultCoreToml(unittest.TestCase):
    """Verify _default_core_toml no longer includes [system]."""

    def test_no_system_section(self):
        from cypilot.commands.init import _default_core_toml
        core = _default_core_toml()
        self.assertNotIn("system", core)
        self.assertEqual(core["version"], "1.0")
        self.assertEqual(core["project_root"], "..")
        # Kits are empty by default — registered dynamically via install_kit()
        self.assertEqual(core["kits"], {})


# ---------------------------------------------------------------------------
# WP7: _maybe_migrate_legacy_to_manifest (update pipeline integration)
# ---------------------------------------------------------------------------

def _make_kit_source_with_manifest(td: Path, slug: str = "testkit") -> Path:
    """Create a kit source with manifest.toml and source files for WP7 tests."""
    kit = td / slug
    kit.mkdir(parents=True, exist_ok=True)

    (kit / "artifacts" / "ADR").mkdir(parents=True)
    (kit / "artifacts" / "ADR" / "template.md").write_text("# ADR\n", encoding="utf-8")
    (kit / "artifacts" / "ADR" / "rules.md").write_text("# Rules\n", encoding="utf-8")
    (kit / "constraints.toml").write_text('[artifacts]\n', encoding="utf-8")
    (kit / "SKILL.md").write_text(f"# Kit {slug}\n", encoding="utf-8")

    _write_toml(kit / "conf.toml", {"version": "2.0", "slug": slug})

    import textwrap
    (kit / "manifest.toml").write_text(textwrap.dedent("""\
        [manifest]
        version = "1.0"
        root = "{cypilot_path}/config/kits/{slug}"
        user_modifiable = false

        [[resources]]
        id = "adr_artifacts"
        description = "ADR artifact definitions"
        source = "artifacts/ADR"
        default_path = "artifacts/ADR"
        type = "directory"
        user_modifiable = false

        [[resources]]
        id = "constraints"
        description = "Kit structural constraints"
        source = "constraints.toml"
        default_path = "constraints.toml"
        type = "file"
        user_modifiable = false

        [[resources]]
        id = "skill"
        description = "Kit skill instructions"
        source = "SKILL.md"
        default_path = "SKILL.md"
        type = "file"
        user_modifiable = false
    """), encoding="utf-8")
    return kit


def _setup_legacy_adapter(td: Path, slug: str = "testkit") -> Path:
    """Set up an adapter with a legacy kit install (no resources in core.toml)."""
    adapter = td / "adapter"
    config = adapter / "config"
    config_kit = config / "kits" / slug
    config_kit.mkdir(parents=True)

    (config_kit / "artifacts" / "ADR").mkdir(parents=True)
    (config_kit / "artifacts" / "ADR" / "template.md").write_text("# ADR\n", encoding="utf-8")
    (config_kit / "artifacts" / "ADR" / "rules.md").write_text("# Rules\n", encoding="utf-8")
    (config_kit / "constraints.toml").write_text('[artifacts]\n', encoding="utf-8")
    (config_kit / "SKILL.md").write_text(f"# Kit {slug}\n", encoding="utf-8")

    _write_toml(config / "core.toml", {
        "version": "1.0",
        "project_root": "..",
        "kits": {
            slug: {
                "format": "Cypilot",
                "path": f"config/kits/{slug}",
                "version": "2.0",
            }
        },
    })
    return adapter


class TestMaybeMigrateLegacyToManifest(unittest.TestCase):
    """Unit tests for _maybe_migrate_legacy_to_manifest() helper (WP7)."""

    def test_no_manifest_returns_none(self):
        """Kit source without manifest.toml → returns None (no migration)."""
        from cypilot.commands.update import _maybe_migrate_legacy_to_manifest
        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = td_path / "nokit"
            kit_src.mkdir()
            adapter = _setup_legacy_adapter(td_path, "nokit")
            config_dir = adapter / "config"

            result = _maybe_migrate_legacy_to_manifest(
                "nokit", kit_src, adapter, config_dir, interactive=False,
            )
            self.assertIsNone(result)

    def test_already_has_resources_returns_none(self):
        """Kit with existing resources in core.toml → returns None (skip)."""
        from cypilot.commands.update import _maybe_migrate_legacy_to_manifest
        import tomllib
        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = _make_kit_source_with_manifest(td_path, "mykit")
            adapter = _setup_legacy_adapter(td_path, "mykit")
            config_dir = adapter / "config"

            # Pre-populate resources in core.toml
            with open(config_dir / "core.toml", "rb") as f:
                data = tomllib.load(f)
            data["kits"]["mykit"]["resources"] = {
                "adr_artifacts": {"path": "config/kits/mykit/artifacts/ADR"},
            }
            _write_toml(config_dir / "core.toml", data)

            result = _maybe_migrate_legacy_to_manifest(
                "mykit", kit_src, adapter, config_dir, interactive=False,
            )
            self.assertIsNone(result)

    def test_triggers_migration_when_needed(self):
        """Source has manifest + no resources → triggers migration, returns result."""
        from cypilot.commands.update import _maybe_migrate_legacy_to_manifest
        import tomllib
        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = _make_kit_source_with_manifest(td_path, "mykit")
            adapter = _setup_legacy_adapter(td_path, "mykit")
            config_dir = adapter / "config"

            result = _maybe_migrate_legacy_to_manifest(
                "mykit", kit_src, adapter, config_dir, interactive=False,
            )

            self.assertIsNotNone(result)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["migrated_count"], 3)
            self.assertEqual(result["new_count"], 0)

            # Verify resources written to core.toml
            with open(config_dir / "core.toml", "rb") as f:
                data = tomllib.load(f)
            self.assertIn("resources", data["kits"]["mykit"])

    def test_invalid_manifest_returns_none(self):
        """Invalid manifest.toml in kit source → returns None (error handled)."""
        from cypilot.commands.update import _maybe_migrate_legacy_to_manifest
        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = td_path / "badkit"
            kit_src.mkdir()
            # Write an invalid manifest (missing required fields)
            (kit_src / "manifest.toml").write_text("[manifest]\n", encoding="utf-8")
            adapter = _setup_legacy_adapter(td_path, "badkit")
            config_dir = adapter / "config"

            result = _maybe_migrate_legacy_to_manifest(
                "badkit", kit_src, adapter, config_dir, interactive=False,
            )
            # ValueError from load_manifest is caught → returns None
            self.assertIsNone(result)

    def test_corrupt_manifest_returns_none(self):
        """Corrupt manifest.toml → returns None (exception caught)."""
        from cypilot.commands.update import _maybe_migrate_legacy_to_manifest
        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = td_path / "corrupt"
            kit_src.mkdir()
            (kit_src / "manifest.toml").write_text("{{invalid", encoding="utf-8")
            adapter = _setup_legacy_adapter(td_path, "corrupt")
            config_dir = adapter / "config"

            result = _maybe_migrate_legacy_to_manifest(
                "corrupt", kit_src, adapter, config_dir, interactive=False,
            )
            self.assertIsNone(result)


class TestCmdUpdateManifestMigration(unittest.TestCase):
    """Pipeline integration tests for WP7 manifest migration in cmd_update."""

    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)

    def tearDown(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

    def test_update_triggers_manifest_migration_version_match(self):
        """When kit versions match but no resources, migration still triggers.

        Manually sets up a project where:
        - Cache kit has manifest.toml + matching version
        - Installed kit has same version in core.toml but NO resources
        - update_kit returns early ("current") but WP7 catch-all triggers migration
        """
        from cypilot.commands.update import cmd_update
        import tomllib, textwrap

        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            (root / ".git").mkdir()

            # Set up adapter directory manually
            adapter = root / "cypilot"
            config = adapter / "config"
            config_kit = config / "kits" / "sdlc"
            config_kit.mkdir(parents=True)
            (adapter / ".core").mkdir(parents=True)
            (adapter / ".gen").mkdir(parents=True)

            # Create installed kit files
            (config_kit / "constraints.toml").write_text('[artifacts]\n', encoding="utf-8")
            (config_kit / "SKILL.md").write_text("# Kit sdlc\n", encoding="utf-8")
            _write_toml(config_kit / "conf.toml", {"version": "2.0"})

            # core.toml: version matches cache, NO resources
            _write_toml(config / "core.toml", {
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {
                        "format": "Cypilot",
                        "path": "config/kits/sdlc",
                        "version": "2.0",
                    },
                },
            })

            # AGENTS.md with cypilot_path
            (root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "cypilot"\n```\n<!-- /@cpt:root-agents -->\n',
                encoding="utf-8",
            )

            # Create cache with matching version + manifest.toml
            cache = Path(td) / "cache"
            _make_cache(cache, kit_version="2.0")
            kit_src = cache / "kits" / "sdlc"
            (kit_src / "constraints.toml").write_text('[artifacts]\n', encoding="utf-8")
            (kit_src / "SKILL.md").write_text("# Kit sdlc\n", encoding="utf-8")
            (kit_src / "manifest.toml").write_text(textwrap.dedent("""\
                [manifest]
                version = "1.0"
                root = "{cypilot_path}/config/kits/{slug}"
                user_modifiable = false

                [[resources]]
                id = "constraints"
                description = "Kit constraints"
                source = "constraints.toml"
                default_path = "constraints.toml"
                type = "file"
                user_modifiable = false

                [[resources]]
                id = "skill"
                description = "Kit skill"
                source = "SKILL.md"
                default_path = "SKILL.md"
                type = "file"
                user_modifiable = false
            """), encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with (
                    patch("cypilot.commands.update.CACHE_DIR", cache),
                    patch(
                        "cypilot.commands.kit._download_kit_from_github",
                        return_value=(kit_src, "2.0"),
                    ),
                ):
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update([])
                self.assertEqual(rc, 0)

                # Verify resources were populated in core.toml
                core_toml = config / "core.toml"
                with open(core_toml, "rb") as f:
                    data = tomllib.load(f)
                sdlc_entry = data["kits"]["sdlc"]
                self.assertIn("resources", sdlc_entry)
                self.assertIn("constraints", sdlc_entry["resources"])
                self.assertIn("skill", sdlc_entry["resources"])

                # Check manifest_migration in output
                out = json.loads(buf.getvalue())
                kits = out.get("actions", {}).get("kits", {})
                sdlc_r = kits.get("sdlc", {})
                mig = sdlc_r.get("manifest_migration")
                self.assertIsNotNone(mig)
                self.assertEqual(mig["status"], "PASS")
            finally:
                os.chdir(cwd)

    def test_update_skips_migration_when_resources_exist(self):
        """When kit already has resources in core.toml, migration is skipped."""
        from cypilot.commands.update import cmd_update
        import tomllib, textwrap

        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            (root / ".git").mkdir()

            adapter = root / "cypilot"
            config = adapter / "config"
            config_kit = config / "kits" / "sdlc"
            config_kit.mkdir(parents=True)
            (adapter / ".core").mkdir(parents=True)
            (adapter / ".gen").mkdir(parents=True)

            (config_kit / "constraints.toml").write_text('[artifacts]\n', encoding="utf-8")
            (config_kit / "SKILL.md").write_text("# Kit sdlc\n", encoding="utf-8")
            _write_toml(config_kit / "conf.toml", {"version": "2.0"})

            # core.toml WITH resources already populated
            _write_toml(config / "core.toml", {
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {
                        "format": "Cypilot",
                        "path": "config/kits/sdlc",
                        "version": "2.0",
                        "resources": {
                            "constraints": {"path": "config/kits/sdlc/constraints.toml"},
                        },
                    },
                },
            })

            (root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "cypilot"\n```\n<!-- /@cpt:root-agents -->\n',
                encoding="utf-8",
            )

            cache = Path(td) / "cache"
            _make_cache(cache, kit_version="2.0")
            kit_src = cache / "kits" / "sdlc"
            (kit_src / "manifest.toml").write_text(textwrap.dedent("""\
                [manifest]
                version = "1.0"
                root = "{cypilot_path}/config/kits/{slug}"
                user_modifiable = false

                [[resources]]
                id = "constraints"
                source = "constraints.toml"
                default_path = "constraints.toml"
                type = "file"
                user_modifiable = false
            """), encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with (
                    patch("cypilot.commands.update.CACHE_DIR", cache),
                    patch(
                        "cypilot.commands.kit._download_kit_from_github",
                        return_value=(kit_src, "2.0"),
                    ),
                ):
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update([])
                self.assertEqual(rc, 0)

                out = json.loads(buf.getvalue())
                kits = out.get("actions", {}).get("kits", {})
                sdlc_r = kits.get("sdlc", {})
                # No manifest_migration key — migration was skipped
                self.assertNotIn("manifest_migration", sdlc_r)
            finally:
                os.chdir(cwd)

    def test_dry_run_skips_migration(self):
        """--dry-run does not trigger manifest migration."""
        from cypilot.commands.update import cmd_update
        import tomllib, textwrap

        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            (root / ".git").mkdir()

            adapter = root / "cypilot"
            config = adapter / "config"
            config_kit = config / "kits" / "sdlc"
            config_kit.mkdir(parents=True)
            (adapter / ".core").mkdir(parents=True)
            (adapter / ".gen").mkdir(parents=True)

            (config_kit / "constraints.toml").write_text('[artifacts]\n', encoding="utf-8")
            (config_kit / "SKILL.md").write_text("# Kit sdlc\n", encoding="utf-8")
            _write_toml(config_kit / "conf.toml", {"version": "2.0"})

            # core.toml: NO resources
            _write_toml(config / "core.toml", {
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {
                        "format": "Cypilot",
                        "path": "config/kits/sdlc",
                        "version": "2.0",
                    },
                },
            })

            (root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "cypilot"\n```\n<!-- /@cpt:root-agents -->\n',
                encoding="utf-8",
            )

            cache = Path(td) / "cache"
            _make_cache(cache, kit_version="2.0")
            kit_src = cache / "kits" / "sdlc"
            (kit_src / "manifest.toml").write_text(textwrap.dedent("""\
                [manifest]
                version = "1.0"
                root = "{cypilot_path}/config/kits/{slug}"
                user_modifiable = false

                [[resources]]
                id = "constraints"
                source = "constraints.toml"
                default_path = "constraints.toml"
                type = "file"
                user_modifiable = false
            """), encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with (
                    patch("cypilot.commands.update.CACHE_DIR", cache),
                    patch(
                        "cypilot.commands.kit._download_kit_from_github",
                        return_value=(kit_src, "2.0"),
                    ),
                ):
                    buf = io.StringIO()
                    err = io.StringIO()
                    with redirect_stdout(buf), redirect_stderr(err):
                        rc = cmd_update(["--dry-run"])
                self.assertEqual(rc, 0)

                # No resources should be populated (dry-run)
                core_toml = config / "core.toml"
                with open(core_toml, "rb") as f:
                    data = tomllib.load(f)
                sdlc_entry = data["kits"]["sdlc"]
                self.assertNotIn("resources", sdlc_entry)
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
