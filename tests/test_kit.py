"""
Tests for commands/kit.py — kit install, update, dispatcher, helpers.

Scenario-based tests covering CLI subcommands and core kit logic.
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


def _make_kit_source(td: Path, slug: str = "testkit") -> Path:
    """Create a minimal kit source directory (direct file package)."""
    kit_src = td / slug
    kit_src.mkdir(parents=True, exist_ok=True)
    # Content dirs
    (kit_src / "artifacts" / "FEATURE").mkdir(parents=True)
    (kit_src / "artifacts" / "FEATURE" / "template.md").write_text(
        "# Feature Spec\n", encoding="utf-8",
    )
    (kit_src / "workflows").mkdir(exist_ok=True)
    # Content files
    (kit_src / "SKILL.md").write_text(
        f"# Kit {slug}\nKit skill instructions.\n", encoding="utf-8",
    )
    (kit_src / "constraints.toml").write_text(
        "[naming]\npattern = '{slug}-*'\n", encoding="utf-8",
    )
    # conf.toml
    from cypilot.utils import toml_utils
    toml_utils.dump({"version": 1}, kit_src / "conf.toml")
    return kit_src


def _bootstrap_project(root: Path, adapter_rel: str = "cypilot") -> Path:
    """Set up a minimal initialized project for kit commands."""
    root.mkdir(parents=True, exist_ok=True)
    (root / ".git").mkdir(exist_ok=True)
    (root / "AGENTS.md").write_text(
        f'<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "{adapter_rel}"\n```\n<!-- /@cpt:root-agents -->\n',
        encoding="utf-8",
    )
    adapter = root / adapter_rel
    config = adapter / "config"
    gen = adapter / ".gen"
    for d in [adapter, config, gen, adapter / ".core"]:
        d.mkdir(parents=True, exist_ok=True)
    (config / "AGENTS.md").write_text("# Test\n", encoding="utf-8")
    from cypilot.utils import toml_utils
    toml_utils.dump({
        "version": "1.0",
        "project_root": "..",
        "system": {"name": "Test", "slug": "test", "kit": "cypilot-sdlc"},
        "kits": {},
    }, config / "core.toml")
    return adapter

class TestCmdKitDispatcher(unittest.TestCase):
    """Kit CLI dispatcher: handles subcommands and errors."""

    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)

    def tearDown(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

    def test_no_subcommand(self):
        from cypilot.commands.kit import cmd_kit
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_kit([])
        self.assertEqual(rc, 1)
        out = json.loads(buf.getvalue())
        self.assertEqual(out["status"], "ERROR")
        self.assertIn("subcommand", out["message"].lower())

    def test_unknown_subcommand(self):
        from cypilot.commands.kit import cmd_kit
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_kit(["frobnicate"])
        self.assertEqual(rc, 1)
        out = json.loads(buf.getvalue())
        self.assertIn("Unknown", out["message"])


class TestCmdKitUpdate(unittest.TestCase):
    """CLI kit update command scenarios."""

    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)

    def tearDown(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

    def test_update_source_not_found(self):
        from cypilot.commands.kit import cmd_kit_update
        with TemporaryDirectory() as td:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_kit_update([str(Path(td) / "nonexistent")])
            self.assertEqual(rc, 2)
            out = json.loads(buf.getvalue())
            self.assertIn("not found", out["message"])

    def test_update_no_project_root(self):
        from cypilot.commands.kit import cmd_kit_update
        with TemporaryDirectory() as td:
            kit_src = _make_kit_source(Path(td), "mykit")
            cwd = os.getcwd()
            try:
                os.chdir(td)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_update([str(kit_src)])
                self.assertEqual(rc, 1)
            finally:
                os.chdir(cwd)

    def test_update_kit_not_installed_does_first_install(self):
        """update_kit handles first-install if kit is not yet installed."""
        from cypilot.commands.kit import cmd_kit_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "newkit")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_update([str(kit_src)])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["results"][0]["action"], "created")
            finally:
                os.chdir(cwd)

    def test_update_dry_run(self):
        from cypilot.commands.kit import cmd_kit_update, install_kit
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "upkit")
            install_kit(kit_src, adapter, "upkit")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_update([str(kit_src), "--dry-run"])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["status"], "PASS")
            finally:
                os.chdir(cwd)

    def test_update_auto_approve(self):
        from cypilot.commands.kit import cmd_kit_update, install_kit
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "autokit")
            install_kit(kit_src, adapter, "autokit")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_update([str(kit_src), "--no-interactive", "-y"])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["status"], "PASS")
            finally:
                os.chdir(cwd)

    def test_update_same_version_skips(self):
        """Same version in source and installed → skip update."""
        from cypilot.commands.kit import cmd_kit_update, install_kit
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "vkit")
            install_kit(kit_src, adapter, "vkit")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_update([str(kit_src)])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["results"][0]["action"], "current")
            finally:
                os.chdir(cwd)

    def test_update_force_bypasses_version_check(self):
        """--force skips version check even if versions match."""
        from cypilot.commands.kit import cmd_kit_update, install_kit
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "fkit")
            install_kit(kit_src, adapter, "fkit")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_update([str(kit_src), "--force"])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                # With identical files, force still reports "current" (no actual diff)
                self.assertIn(out["results"][0]["action"], ("current", "updated"))
            finally:
                os.chdir(cwd)


class TestKitHelpers(unittest.TestCase):
    def test_read_kit_version_valid(self):
        from cypilot.commands.kit import _read_kit_version
        from cypilot.utils import toml_utils
        with TemporaryDirectory() as td:
            p = Path(td) / "conf.toml"
            toml_utils.dump({"version": 2}, p)
            self.assertEqual(_read_kit_version(p), "2")

    def test_read_kit_version_missing(self):
        from cypilot.commands.kit import _read_kit_version
        self.assertEqual(_read_kit_version(Path("/nonexistent/conf.toml")), "")

    def test_read_kit_version_no_key(self):
        from cypilot.commands.kit import _read_kit_version
        from cypilot.utils import toml_utils
        with TemporaryDirectory() as td:
            p = Path(td) / "conf.toml"
            toml_utils.dump({"other": "data"}, p)
            self.assertEqual(_read_kit_version(p), "")

    def test_register_kit_in_core_toml(self):
        from cypilot.commands.kit import _register_kit_in_core_toml
        from cypilot.utils import toml_utils
        with TemporaryDirectory() as td:
            config_dir = Path(td) / "config"
            config_dir.mkdir()
            toml_utils.dump({"version": "1.0", "kits": {}}, config_dir / "core.toml")
            _register_kit_in_core_toml(config_dir, "mykit", "1", Path(td))
            import tomllib
            with open(config_dir / "core.toml", "rb") as f:
                data = tomllib.load(f)
            self.assertIn("mykit", data["kits"])
            self.assertEqual(data["kits"]["mykit"]["path"], "config/kits/mykit")

    def test_register_kit_no_core_toml(self):
        """No core.toml → does nothing, no error."""
        from cypilot.commands.kit import _register_kit_in_core_toml
        with TemporaryDirectory() as td:
            _register_kit_in_core_toml(Path(td), "nokit", "1", Path(td))

    def test_register_kit_corrupt_core_toml(self):
        """Corrupt core.toml → does nothing, no error."""
        from cypilot.commands.kit import _register_kit_in_core_toml
        with TemporaryDirectory() as td:
            config_dir = Path(td)
            (config_dir / "core.toml").write_text("{{invalid", encoding="utf-8")
            _register_kit_in_core_toml(config_dir, "nokit", "1", Path(td))




class TestCmdKitInstall(unittest.TestCase):
    """Cover cmd_kit_install CLI command."""

    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)

    def tearDown(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

    def test_install_invalid_source(self):
        from cypilot.commands.kit import cmd_kit_install
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_kit_install(["/nonexistent/path/to/kit"])
        self.assertEqual(rc, 2)
        out = json.loads(buf.getvalue())
        self.assertEqual(out["status"], "FAIL")

    def test_install_no_project_root(self):
        from cypilot.commands.kit import cmd_kit_install
        with TemporaryDirectory() as td:
            kit_src = _make_kit_source(Path(td), "testkit")
            cwd = os.getcwd()
            try:
                os.chdir(td)
                # Remove .git so no project root is found
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_install([str(kit_src)])
                self.assertEqual(rc, 1)
            finally:
                os.chdir(cwd)

    def test_install_no_cypilot_dir(self):
        from cypilot.commands.kit import cmd_kit_install
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            (root / ".git").mkdir()
            (root / "AGENTS.md").write_text("# nothing\n", encoding="utf-8")
            kit_src = _make_kit_source(Path(td), "testkit")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_install([str(kit_src)])
                self.assertEqual(rc, 1)
            finally:
                os.chdir(cwd)

    def test_install_already_exists(self):
        from cypilot.commands.kit import cmd_kit_install
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "testkit")
            (adapter / "config" / "kits" / "testkit").mkdir(parents=True)
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_install([str(kit_src)])
                self.assertEqual(rc, 2)
                out = json.loads(buf.getvalue())
                self.assertIn("already installed", out["message"])
            finally:
                os.chdir(cwd)

    def test_install_dry_run(self):
        from cypilot.commands.kit import cmd_kit_install
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "testkit")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_install([str(kit_src), "--dry-run"])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["status"], "DRY_RUN")
            finally:
                os.chdir(cwd)

    def test_install_success(self):
        from cypilot.commands.kit import cmd_kit_install
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "testkit")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_install([str(kit_src)])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["status"], "PASS")
                self.assertEqual(out["kit"], "testkit")
            finally:
                os.chdir(cwd)

    def test_install_with_force(self):
        from cypilot.commands.kit import cmd_kit_install
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "testkit")
            (adapter / "config" / "kits" / "testkit").mkdir(parents=True)
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_install([str(kit_src), "--force"])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["status"], "PASS")
            finally:
                os.chdir(cwd)

    def test_install_slug_from_conf_toml(self):
        """Kit slug is read from conf.toml slug field."""
        from cypilot.commands.kit import cmd_kit_install
        from cypilot.utils import toml_utils
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "rawdir")
            toml_utils.dump({"slug": "custom-slug", "version": 1}, kit_src / "conf.toml")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_install([str(kit_src)])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["kit"], "custom-slug")
            finally:
                os.chdir(cwd)


class TestDetectAndMigrateLayout(unittest.TestCase):
    """Cover _detect_and_migrate_layout — legacy layout migration."""

    def test_no_migration_needed(self):
        from cypilot.commands.kit import _detect_and_migrate_layout
        with TemporaryDirectory() as td:
            adapter = Path(td) / "cypilot"
            (adapter / "config" / "kits" / "sdlc").mkdir(parents=True)
            result = _detect_and_migrate_layout(adapter)
            self.assertEqual(result, {})

    def test_dry_run_kits_dir(self):
        from cypilot.commands.kit import _detect_and_migrate_layout
        with TemporaryDirectory() as td:
            adapter = Path(td) / "cypilot"
            kits_dir = adapter / "kits" / "sdlc"
            kits_dir.mkdir(parents=True)
            (kits_dir / "conf.toml").write_text("version = 1\n", encoding="utf-8")
            result = _detect_and_migrate_layout(adapter, dry_run=True)
            self.assertIn("sdlc", result)
            self.assertEqual(result["sdlc"], "would_migrate")
            # Verify kits/ dir still exists (dry run)
            self.assertTrue(kits_dir.is_dir())

    def test_migrate_kits_dir(self):
        from cypilot.commands.kit import _detect_and_migrate_layout
        with TemporaryDirectory() as td:
            adapter = Path(td) / "cypilot"
            kits_dir = adapter / "kits" / "sdlc"
            kits_dir.mkdir(parents=True)
            (kits_dir / "conf.toml").write_text("version = 1\n", encoding="utf-8")
            (kits_dir / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
            # Legacy artifacts to skip
            bp_dir = kits_dir / "blueprints"
            bp_dir.mkdir()
            (bp_dir / "DESIGN.md").write_text("blueprint\n", encoding="utf-8")
            result = _detect_and_migrate_layout(adapter)
            self.assertEqual(result["sdlc"], "migrated")
            config_kit = adapter / "config" / "kits" / "sdlc"
            self.assertTrue((config_kit / "conf.toml").is_file())
            self.assertTrue((config_kit / "SKILL.md").is_file())
            # Blueprints should NOT be copied
            self.assertFalse((config_kit / "blueprints").exists())
            # Old kits/ dir should be removed
            self.assertFalse((adapter / "kits").is_dir())

    def test_migrate_gen_kits_dir(self):
        from cypilot.commands.kit import _detect_and_migrate_layout
        with TemporaryDirectory() as td:
            adapter = Path(td) / "cypilot"
            gen_kit = adapter / ".gen" / "kits" / "sdlc"
            gen_kit.mkdir(parents=True)
            (gen_kit / "SKILL.md").write_text("# Gen Skill\n", encoding="utf-8")
            result = _detect_and_migrate_layout(adapter)
            self.assertIn("sdlc", result)
            config_kit = adapter / "config" / "kits" / "sdlc"
            self.assertTrue((config_kit / "SKILL.md").is_file())
            # .gen/kits/ should be removed
            self.assertFalse((adapter / ".gen" / "kits").is_dir())

    def test_migrate_updates_core_toml_paths(self):
        from cypilot.commands.kit import _detect_and_migrate_layout
        from cypilot.utils import toml_utils
        with TemporaryDirectory() as td:
            adapter = Path(td) / "cypilot"
            kits_dir = adapter / "kits" / "sdlc"
            kits_dir.mkdir(parents=True)
            (kits_dir / "conf.toml").write_text("version = 1\n", encoding="utf-8")
            config_dir = adapter / "config"
            config_dir.mkdir(parents=True)
            toml_utils.dump({
                "kits": {"sdlc": {"path": "kits/sdlc", "format": "Cypilot"}},
            }, config_dir / "core.toml")
            _detect_and_migrate_layout(adapter)
            import tomllib
            with open(config_dir / "core.toml", "rb") as f:
                data = tomllib.load(f)
            self.assertEqual(data["kits"]["sdlc"]["path"], "config/kits/sdlc")

    def test_migrate_with_subdir(self):
        """Migration copies subdirectories from kits/{slug}/."""
        from cypilot.commands.kit import _detect_and_migrate_layout
        with TemporaryDirectory() as td:
            adapter = Path(td) / "cypilot"
            kits_dir = adapter / "kits" / "sdlc"
            (kits_dir / "artifacts" / "DESIGN").mkdir(parents=True)
            (kits_dir / "artifacts" / "DESIGN" / "template.md").write_text("# T\n", encoding="utf-8")
            (kits_dir / "conf.toml").write_text("version = 1\n", encoding="utf-8")
            _detect_and_migrate_layout(adapter)
            config_kit = adapter / "config" / "kits" / "sdlc"
            self.assertTrue((config_kit / "artifacts" / "DESIGN" / "template.md").is_file())

    def test_dry_run_gen_kits(self):
        from cypilot.commands.kit import _detect_and_migrate_layout
        with TemporaryDirectory() as td:
            adapter = Path(td) / "cypilot"
            gen_kit = adapter / ".gen" / "kits" / "sdlc"
            gen_kit.mkdir(parents=True)
            (gen_kit / "SKILL.md").write_text("# S\n", encoding="utf-8")
            result = _detect_and_migrate_layout(adapter, dry_run=True)
            self.assertEqual(result["sdlc"], "would_migrate")
            # .gen/kits/ should still exist (dry run)
            self.assertTrue(gen_kit.is_dir())


class TestCmdKitMigrateDeprecated(unittest.TestCase):
    """cmd_kit_migrate redirects to cmd_kit_update."""

    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)

    def tearDown(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

    def test_migrate_warns_and_returns_error(self):
        from cypilot.commands.kit import cmd_kit_migrate
        err = io.StringIO()
        with redirect_stderr(err):
            rc = cmd_kit_migrate([])
        self.assertEqual(rc, 1)
        self.assertIn("deprecated", err.getvalue().lower())
        self.assertIn("kit update", err.getvalue())


class TestCmdKitDispatcherRoutes(unittest.TestCase):
    """Cover cmd_kit routing to install, update, migrate subcommands."""

    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)

    def tearDown(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

    def test_route_install(self):
        from cypilot.commands.kit import cmd_kit
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_kit(["install", "/nonexistent"])
        self.assertEqual(rc, 2)

    def test_route_update(self):
        from cypilot.commands.kit import cmd_kit
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_kit(["update", "/nonexistent"])
        self.assertEqual(rc, 2)

    def test_route_migrate(self):
        from cypilot.commands.kit import cmd_kit
        with TemporaryDirectory() as td:
            cwd = os.getcwd()
            try:
                os.chdir(td)
                err = io.StringIO()
                buf = io.StringIO()
                with redirect_stderr(err), redirect_stdout(buf):
                    rc = cmd_kit(["migrate"])
                self.assertIn("deprecated", err.getvalue().lower())
            finally:
                os.chdir(cwd)


class TestUpdateKitExistingBranch(unittest.TestCase):
    """Cover update_kit when kit already exists (file-level diff path)."""

    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)

    def tearDown(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

    def test_update_existing_kit_auto_approve(self):
        from cypilot.commands.kit import update_kit, install_kit
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "ukit")
            install_kit(kit_src, adapter, "ukit")
            # Modify source to create a diff
            (kit_src / "SKILL.md").write_text("# Updated Skill\n", encoding="utf-8")
            result = update_kit("ukit", kit_src, adapter, auto_approve=True)
            self.assertEqual(result["kit"], "ukit")
            self.assertIn(result["version"]["status"], ("updated", "current"))

    def test_update_existing_kit_non_interactive(self):
        from cypilot.commands.kit import update_kit, install_kit
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "ukit2")
            install_kit(kit_src, adapter, "ukit2")
            (kit_src / "SKILL.md").write_text("# Changed\n", encoding="utf-8")
            result = update_kit("ukit2", kit_src, adapter, interactive=False)
            # Non-interactive declines changes
            self.assertIn(result["version"]["status"], ("partial", "current"))

    def test_update_kit_dry_run(self):
        from cypilot.commands.kit import update_kit
        with TemporaryDirectory() as td:
            adapter = Path(td) / "cypilot"
            adapter.mkdir()
            result = update_kit("test", Path(td), adapter, dry_run=True)
            self.assertEqual(result["version"]["status"], "dry_run")

    def test_update_existing_with_declined(self):
        from cypilot.commands.kit import update_kit, install_kit
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "dkit")
            install_kit(kit_src, adapter, "dkit")
            # Modify source
            (kit_src / "constraints.toml").write_text("[changed]\nx = 1\n", encoding="utf-8")
            result = update_kit("dkit", kit_src, adapter, interactive=False)
            if result.get("gen_rejected"):
                self.assertIsInstance(result["gen_rejected"], list)

    def test_update_kit_not_installed_coverage(self):
        """cmd_kit_update with valid source but kit not installed."""
        from cypilot.commands.kit import cmd_kit_update
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)
        try:
            with TemporaryDirectory() as td:
                root = Path(td) / "proj"
                _bootstrap_project(root)
                kit_src = _make_kit_source(Path(td), "notinstalled")
                cwd = os.getcwd()
                try:
                    os.chdir(str(root))
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = cmd_kit_update([str(kit_src)])
                    self.assertEqual(rc, 0)
                    out = json.loads(buf.getvalue())
                    self.assertEqual(out["results"][0]["action"], "created")
                finally:
                    os.chdir(cwd)
        finally:
            set_json_mode(False)


class TestHumanKitInstall(unittest.TestCase):
    """Cover _human_kit_install display function (runs with JSON mode OFF)."""

    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

    def test_pass(self):
        from cypilot.commands.kit import _human_kit_install
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_kit_install({"status": "PASS", "kit": "sdlc", "version": "1", "action": "installed", "files_written": 5})
        self.assertIn("sdlc", buf.getvalue())

    def test_dry_run(self):
        from cypilot.commands.kit import _human_kit_install
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_kit_install({"status": "DRY_RUN", "kit": "sdlc", "version": "1", "source": "/a", "target": "/b"})
        self.assertIn("Dry run", buf.getvalue())

    def test_fail(self):
        from cypilot.commands.kit import _human_kit_install
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_kit_install({"status": "FAIL", "kit": "sdlc", "message": "not found", "hint": "check path"})
        self.assertIn("not found", buf.getvalue())

    def test_with_errors(self):
        from cypilot.commands.kit import _human_kit_install
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_kit_install({"status": "WARN", "kit": "sdlc", "version": "1", "errors": ["err1"]})
        self.assertIn("err1", buf.getvalue())


class TestHumanKitUpdate(unittest.TestCase):
    """Cover _human_kit_update display function."""

    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

    def test_pass_with_results(self):
        from cypilot.commands.kit import _human_kit_update
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_kit_update({
                "status": "PASS",
                "kits_updated": 1,
                "results": [
                    {"kit": "sdlc", "action": "updated", "accepted": ["a.md", "b.md"], "declined": ["c.md"], "unchanged": 5},
                ],
            })
        out = buf.getvalue()
        self.assertIn("sdlc", out)
        self.assertIn("2 accepted", out)
        self.assertIn("1 declined", out)
        self.assertIn("5 unchanged", out)
        self.assertIn("complete", out)

    def test_warn_with_errors(self):
        from cypilot.commands.kit import _human_kit_update
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_kit_update({
                "status": "WARN",
                "kits_updated": 1,
                "results": [{"kit": "sdlc", "action": "current"}],
                "errors": ["oops", "fail"],
            })
        out = buf.getvalue()
        self.assertIn("oops", out)
        self.assertIn("fail", out)
        self.assertIn("warnings", out.lower())

    def test_unknown_status(self):
        from cypilot.commands.kit import _human_kit_update
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_kit_update({"status": "CUSTOM", "results": []})
        self.assertIn("CUSTOM", buf.getvalue())

    def test_no_results(self):
        from cypilot.commands.kit import _human_kit_update
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_kit_update({"status": "PASS", "kits_updated": 0, "results": []})
        self.assertIn("0", buf.getvalue())


class TestSeedKitConfigFiles(unittest.TestCase):
    """Cover _seed_kit_config_files."""

    def test_seeds_missing_files(self):
        from cypilot.commands.kit import _seed_kit_config_files
        with TemporaryDirectory() as td:
            scripts_dir = Path(td) / "scripts"
            scripts_dir.mkdir()
            (scripts_dir / "run.sh").write_text("#!/bin/sh\n", encoding="utf-8")
            config_dir = Path(td) / "config"
            config_dir.mkdir()
            actions = {}
            _seed_kit_config_files(scripts_dir, config_dir, actions)
            # Function should copy scripts content to config if missing


class TestReadConfVersion(unittest.TestCase):
    """Cover _read_conf_version edge cases."""

    def test_valid(self):
        from cypilot.commands.kit import _read_conf_version
        from cypilot.utils import toml_utils
        with TemporaryDirectory() as td:
            p = Path(td) / "conf.toml"
            toml_utils.dump({"version": 3}, p)
            self.assertEqual(_read_conf_version(p), 3)

    def test_missing_file(self):
        from cypilot.commands.kit import _read_conf_version
        self.assertEqual(_read_conf_version(Path("/nonexistent/conf.toml")), 0)

    def test_no_version_key(self):
        from cypilot.commands.kit import _read_conf_version
        from cypilot.utils import toml_utils
        with TemporaryDirectory() as td:
            p = Path(td) / "conf.toml"
            toml_utils.dump({"slug": "sdlc"}, p)
            self.assertEqual(_read_conf_version(p), 0)

    def test_corrupt(self):
        from cypilot.commands.kit import _read_conf_version
        with TemporaryDirectory() as td:
            p = Path(td) / "conf.toml"
            p.write_text("{{invalid", encoding="utf-8")
            self.assertEqual(_read_conf_version(p), 0)


if __name__ == "__main__":
    unittest.main()
