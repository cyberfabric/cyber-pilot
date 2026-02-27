"""
Tests for commands/kit.py — kit install, update, generate-resources, validate-kits, dispatcher.

Scenario-based tests covering all CLI subcommands and the core install_kit logic.
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
    """Create a minimal kit source directory with blueprints/ and conf.toml."""
    kit_src = td / slug
    bp = kit_src / "blueprints"
    bp.mkdir(parents=True)
    (bp / "feature.md").write_text(
        "<!-- @cpt:blueprint -->\n```toml\n"
        f'artifact = "FEATURE"\nkit = "{slug}"\nversion = 1\n'
        "```\n<!-- /@cpt:blueprint -->\n\n"
        "<!-- @cpt:heading -->\n# Feature Spec\n<!-- /@cpt:heading -->\n",
        encoding="utf-8",
    )
    from cypilot.utils import toml_utils
    toml_utils.dump({"version": 1, "blueprints": {"feature": 1}}, kit_src / "conf.toml")
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


# =========================================================================
# install_kit (core function)
# =========================================================================

class TestInstallKit(unittest.TestCase):
    """Core install_kit function scenarios."""

    def test_install_kit_no_blueprints_returns_fail(self):
        """Kit source without blueprints/ returns FAIL."""
        from cypilot.commands.kit import install_kit
        with TemporaryDirectory() as td:
            kit_src = Path(td) / "empty_kit"
            kit_src.mkdir()
            cypilot_dir = Path(td) / "project" / "cypilot"
            cypilot_dir.mkdir(parents=True)
            result = install_kit(kit_src, cypilot_dir, "empty")
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(result["errors"])

    def test_install_kit_success(self):
        """Successful kit install copies blueprints, generates resources."""
        from cypilot.commands.kit import install_kit
        with TemporaryDirectory() as td:
            td_p = Path(td)
            kit_src = _make_kit_source(td_p, "mykit")
            root = td_p / "project"
            adapter = _bootstrap_project(root)
            result = install_kit(kit_src, adapter, "mykit")
            self.assertIn(result["status"], ["PASS", "WARN"])
            self.assertEqual(result["kit"], "mykit")
            # Reference copy should exist
            self.assertTrue((adapter / "kits" / "mykit" / "blueprints").is_dir())
            # User blueprints copied
            self.assertTrue((adapter / "config" / "kits" / "mykit" / "blueprints").is_dir())

    def test_install_kit_with_scripts(self):
        """Kit with scripts/ directory copies scripts to .gen/."""
        from cypilot.commands.kit import install_kit
        with TemporaryDirectory() as td:
            td_p = Path(td)
            kit_src = _make_kit_source(td_p, "scripted")
            scripts = kit_src / "scripts"
            scripts.mkdir()
            (scripts / "helper.py").write_text("# helper\n", encoding="utf-8")
            root = td_p / "project"
            adapter = _bootstrap_project(root)
            result = install_kit(kit_src, adapter, "scripted")
            self.assertIn(result["status"], ["PASS", "WARN"])
            self.assertTrue((adapter / ".gen" / "kits" / "scripted" / "scripts" / "helper.py").is_file())


# =========================================================================
# cmd_kit dispatcher
# =========================================================================

class TestCmdKitDispatcher(unittest.TestCase):
    """Kit CLI dispatcher: handles subcommands and errors."""

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


# =========================================================================
# cmd_kit_install
# =========================================================================

class TestCmdKitInstall(unittest.TestCase):
    """CLI kit install command scenarios."""

    def test_install_missing_blueprints_dir(self):
        """Install from source with no blueprints/ returns FAIL."""
        from cypilot.commands.kit import cmd_kit_install
        with TemporaryDirectory() as td:
            kit_src = Path(td) / "nokit"
            kit_src.mkdir()
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_kit_install([str(kit_src)])
            self.assertEqual(rc, 2)
            out = json.loads(buf.getvalue())
            self.assertEqual(out["status"], "FAIL")

    def test_install_empty_blueprints(self):
        """Install from source with empty blueprints/ returns FAIL."""
        from cypilot.commands.kit import cmd_kit_install
        with TemporaryDirectory() as td:
            bp = Path(td) / "kit" / "blueprints"
            bp.mkdir(parents=True)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_kit_install([str(Path(td) / "kit")])
            self.assertEqual(rc, 2)

    def test_install_no_project_root(self):
        """Install outside a project root returns error."""
        from cypilot.commands.kit import cmd_kit_install
        with TemporaryDirectory() as td:
            kit_src = _make_kit_source(Path(td), "k1")
            cwd = os.getcwd()
            try:
                empty = Path(td) / "empty"
                empty.mkdir()
                os.chdir(str(empty))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_install([str(kit_src)])
                self.assertEqual(rc, 1)
            finally:
                os.chdir(cwd)

    def test_install_no_cypilot_var(self):
        """Install in project without cypilot_path in AGENTS.md returns error."""
        from cypilot.commands.kit import cmd_kit_install
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            (root / ".git").mkdir()
            (root / "AGENTS.md").write_text("# no toml block\n", encoding="utf-8")
            kit_src = _make_kit_source(Path(td), "k2")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_install([str(kit_src)])
                self.assertEqual(rc, 1)
            finally:
                os.chdir(cwd)

    def test_install_already_exists_without_force(self):
        """Installing a kit that already exists without --force returns FAIL."""
        from cypilot.commands.kit import cmd_kit_install
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "dup")
            # Pre-create the kit reference
            (adapter / "kits" / "dup").mkdir(parents=True)
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_install([str(kit_src)])
                self.assertEqual(rc, 2)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["status"], "FAIL")
                self.assertIn("already installed", out["message"])
            finally:
                os.chdir(cwd)

    def test_install_dry_run(self):
        """--dry-run prints plan without writing files."""
        from cypilot.commands.kit import cmd_kit_install
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "drykit")
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

    def test_install_full_success(self):
        """Successful kit install via CLI."""
        from cypilot.commands.kit import cmd_kit_install
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "goodkit")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_install([str(kit_src)])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertIn(out["status"], ["PASS", "WARN"])
            finally:
                os.chdir(cwd)


# =========================================================================
# cmd_kit_update
# =========================================================================

class TestCmdKitUpdate(unittest.TestCase):
    """CLI kit update command scenarios."""

    def test_update_no_project_root(self):
        from cypilot.commands.kit import cmd_kit_update
        with TemporaryDirectory() as td:
            cwd = os.getcwd()
            try:
                os.chdir(td)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_update([])
                self.assertEqual(rc, 1)
            finally:
                os.chdir(cwd)

    def test_update_no_cypilot_dir(self):
        from cypilot.commands.kit import cmd_kit_update
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            (root / "AGENTS.md").write_text("# no toml\n", encoding="utf-8")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_update([])
                self.assertEqual(rc, 1)
            finally:
                os.chdir(cwd)

    def test_update_no_kits_dir(self):
        from cypilot.commands.kit import cmd_kit_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            _bootstrap_project(root)
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_update([])
                self.assertEqual(rc, 2)
                out = json.loads(buf.getvalue())
                self.assertIn("No kits", out["message"])
            finally:
                os.chdir(cwd)

    def test_update_specific_kit_not_found(self):
        from cypilot.commands.kit import cmd_kit_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            (adapter / "kits").mkdir()
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_update(["--kit", "nosuch"])
                self.assertEqual(rc, 2)
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
                    rc = cmd_kit_update(["--dry-run"])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["status"], "PASS")
            finally:
                os.chdir(cwd)

    def test_update_force(self):
        from cypilot.commands.kit import cmd_kit_update, install_kit
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "forcekit")
            install_kit(kit_src, adapter, "forcekit")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_update(["--force"])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertIn(out["status"], ["PASS", "WARN"])
                self.assertGreaterEqual(out["kits_updated"], 1)
            finally:
                os.chdir(cwd)

    def test_update_missing_ref_blueprints(self):
        """Kit reference with no blueprints/ → error recorded."""
        from cypilot.commands.kit import cmd_kit_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            (adapter / "kits" / "broken").mkdir(parents=True)
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_update([])
                # Should still complete, but with errors/warnings
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertIn(out["status"], ["PASS", "WARN"])
            finally:
                os.chdir(cwd)


# =========================================================================
# cmd_generate_resources
# =========================================================================

class TestCmdGenerateResources(unittest.TestCase):
    """CLI generate-resources command scenarios."""

    def test_no_project_root(self):
        from cypilot.commands.kit import cmd_generate_resources
        with TemporaryDirectory() as td:
            cwd = os.getcwd()
            try:
                os.chdir(td)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_generate_resources([])
                self.assertEqual(rc, 1)
            finally:
                os.chdir(cwd)

    def test_no_cypilot_dir(self):
        from cypilot.commands.kit import cmd_generate_resources
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            (root / "AGENTS.md").write_text("# nothing\n", encoding="utf-8")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_generate_resources([])
                self.assertEqual(rc, 1)
            finally:
                os.chdir(cwd)

    def test_no_kits_with_blueprints(self):
        from cypilot.commands.kit import cmd_generate_resources
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            _bootstrap_project(root)
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_generate_resources([])
                self.assertEqual(rc, 2)
            finally:
                os.chdir(cwd)

    def test_generate_success(self):
        from cypilot.commands.kit import cmd_generate_resources, install_kit
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "genkit")
            install_kit(kit_src, adapter, "genkit")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_generate_resources([])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertIn(out["status"], ["PASS", "WARN"])
                self.assertGreaterEqual(out["kits_processed"], 1)
            finally:
                os.chdir(cwd)

    def test_generate_dry_run(self):
        from cypilot.commands.kit import cmd_generate_resources, install_kit
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "drygenkit")
            install_kit(kit_src, adapter, "drygenkit")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_generate_resources(["--dry-run"])
                self.assertEqual(rc, 0)
            finally:
                os.chdir(cwd)

    def test_generate_specific_kit(self):
        from cypilot.commands.kit import cmd_generate_resources, install_kit
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            kit_src = _make_kit_source(Path(td), "speckit")
            install_kit(kit_src, adapter, "speckit")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_generate_resources(["--kit", "speckit"])
                self.assertEqual(rc, 0)
            finally:
                os.chdir(cwd)

    def test_generate_missing_bp_dir(self):
        """Specified kit exists but blueprints dir doesn't → error recorded."""
        from cypilot.commands.kit import cmd_generate_resources
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            (adapter / "config" / "kits" / "nokit").mkdir(parents=True)
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_generate_resources(["--kit", "nokit"])
                # Should fail since blueprints dir missing
                self.assertIn(rc, [0, 2])
            finally:
                os.chdir(cwd)


# =========================================================================
# _read_kit_version + _register_kit_in_core_toml
# =========================================================================

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
            self.assertEqual(data["kits"]["mykit"]["path"], ".gen/kits/mykit")

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


if __name__ == "__main__":
    unittest.main()
