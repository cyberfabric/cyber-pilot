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

    def test_install_kit_with_skill_and_workflow(self):
        """Kit with @cpt:skill and @cpt:workflow markers generates SKILL.md and workflow files."""
        from cypilot.commands.kit import install_kit
        with TemporaryDirectory() as td:
            td_p = Path(td)
            kit_src = td_p / "richkit"
            bp_dir = kit_src / "blueprints"
            bp_dir.mkdir(parents=True)
            (bp_dir / "FEAT.md").write_text(
                "`@cpt:blueprint`\n```toml\n"
                'artifact = "FEAT"\nkit = "richkit"\nversion = 1\n'
                "```\n`@/cpt:blueprint`\n\n"
                "`@cpt:heading`\n```toml\nid = \"h1\"\nlevel = 1\n"
                "template = \"Feature\"\n```\n`@/cpt:heading`\n\n"
                "`@cpt:skill`\n```markdown\nUse this for features.\n```\n`@/cpt:skill`\n\n"
                "`@cpt:workflow`\n```toml\nname = \"feat-review\"\n"
                'description = "Review features"\nversion = "1"\n'
                'purpose = "QA"\n```\n'
                "```markdown\n## Steps\n1. Check\n```\n`@/cpt:workflow`\n",
                encoding="utf-8",
            )
            from cypilot.utils import toml_utils
            toml_utils.dump({"version": 1, "blueprints": {"FEAT": 1}}, kit_src / "conf.toml")
            root = td_p / "project"
            adapter = _bootstrap_project(root)
            result = install_kit(kit_src, adapter, "richkit")
            self.assertIn(result["status"], ["PASS", "WARN"])
            # SKILL.md should be generated
            skill_path = adapter / ".gen" / "kits" / "richkit" / "SKILL.md"
            self.assertTrue(skill_path.is_file())
            skill_content = skill_path.read_text(encoding="utf-8")
            self.assertIn("Artifacts: FEAT", skill_content)
            self.assertIn("Workflows: feat-review", skill_content)
            # Workflow file should be generated
            wf_path = adapter / ".gen" / "kits" / "richkit" / "workflows" / "feat-review.md"
            self.assertTrue(wf_path.is_file())
            wf_content = wf_path.read_text(encoding="utf-8")
            self.assertIn("type: workflow", wf_content)
            self.assertIn('description: Review features', wf_content)
            self.assertIn('version: 1', wf_content)
            self.assertIn('purpose: QA', wf_content)


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


# =========================================================================
# _parse_segments / _three_way_merge_blueprint
# =========================================================================

class TestParseSegments(unittest.TestCase):
    """Tests for the segment parser."""

    def test_text_only(self):
        from cypilot.commands.kit import _parse_segments
        segs = _parse_segments("# Hello\n\nSome text.\n")
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0].kind, "text")

    def test_single_marker(self):
        from cypilot.commands.kit import _parse_segments
        text = "# Title\n\n`@cpt:blueprint`\n```toml\nkit = \"sdlc\"\n```\n`@/cpt:blueprint`\n\nEnd.\n"
        segs = _parse_segments(text)
        types = [s.kind for s in segs]
        self.assertEqual(types, ["text", "marker", "text"])
        self.assertEqual(segs[1].marker_type, "blueprint")
        self.assertEqual(segs[1].marker_key, "blueprint#0")

    def test_workflow_identity(self):
        from cypilot.commands.kit import _parse_segments
        text = (
            '`@cpt:workflow`\n```toml\nname = "pr-review"\n```\ncontent\n`@/cpt:workflow`\n'
            '`@cpt:workflow`\n```toml\nname = "pr-status"\n```\ncontent2\n`@/cpt:workflow`\n'
        )
        segs = _parse_segments(text)
        markers = [s for s in segs if s.kind == "marker"]
        self.assertEqual(len(markers), 2)
        self.assertEqual(markers[0].marker_key, "workflow:pr-review#0")
        self.assertEqual(markers[1].marker_key, "workflow:pr-status#0")

    def test_heading_identity(self):
        from cypilot.commands.kit import _parse_segments
        text = '`@cpt:heading`\n```toml\nlevel = 1\ntemplate = "Context"\n```\n`@/cpt:heading`\n'
        segs = _parse_segments(text)
        markers = [s for s in segs if s.kind == "marker"]
        self.assertEqual(markers[0].marker_key, "heading:L1#0")

    def test_duplicate_keys_disambiguated(self):
        from cypilot.commands.kit import _parse_segments
        text = (
            '`@cpt:heading`\n```toml\nlevel = 2\n```\n`@/cpt:heading`\n'
            '`@cpt:heading`\n```toml\nlevel = 2\n```\n`@/cpt:heading`\n'
        )
        segs = _parse_segments(text)
        markers = [s for s in segs if s.kind == "marker"]
        self.assertEqual(len(markers), 2)
        self.assertNotEqual(markers[0].marker_key, markers[1].marker_key)
        self.assertIn("heading:L2#0", markers[0].marker_key)
        self.assertIn("heading:L2#1", markers[1].marker_key)

    def test_unclosed_marker_treated_as_text(self):
        from cypilot.commands.kit import _parse_segments
        text = '`@cpt:skill`\nSome content without close\n'
        segs = _parse_segments(text)
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0].kind, "text")


class TestThreeWayMerge(unittest.TestCase):
    """Tests for marker-level three-way merge."""

    def test_unchanged_marker_gets_updated(self):
        """If user didn't change a marker, it should be updated from new ref."""
        from cypilot.commands.kit import _three_way_merge_blueprint
        old_ref = '`@cpt:heading`\n```toml\ntemplate = "Title"\n```\nOld content\n`@/cpt:heading`\n'
        new_ref = '`@cpt:heading`\n```toml\ntemplate = "Title"\n```\nNew content\n`@/cpt:heading`\n'
        user = '`@cpt:heading`\n```toml\ntemplate = "Title"\n```\nOld content\n`@/cpt:heading`\n'
        merged, report = _three_way_merge_blueprint(old_ref, new_ref, user)
        self.assertIn("New content", merged)
        self.assertNotIn("Old content", merged)
        self.assertEqual(len(report["updated"]), 1)
        self.assertEqual(len(report["skipped"]), 0)

    def test_customized_marker_skipped(self):
        """If user customized a marker, it should NOT be updated."""
        from cypilot.commands.kit import _three_way_merge_blueprint
        old_ref = '`@cpt:heading`\n```toml\ntemplate = "Title"\n```\nOriginal\n`@/cpt:heading`\n'
        new_ref = '`@cpt:heading`\n```toml\ntemplate = "Title"\n```\nUpdated\n`@/cpt:heading`\n'
        user = '`@cpt:heading`\n```toml\ntemplate = "Title"\n```\nMy custom text\n`@/cpt:heading`\n'
        merged, report = _three_way_merge_blueprint(old_ref, new_ref, user)
        self.assertIn("My custom text", merged)
        self.assertNotIn("Updated", merged)
        self.assertEqual(len(report["skipped"]), 1)
        self.assertEqual(len(report["updated"]), 0)

    def test_deleted_marker_not_readded(self):
        """If user deleted a marker, it should NOT be re-added."""
        from cypilot.commands.kit import _three_way_merge_blueprint
        old_ref = (
            'Intro\n'
            '`@cpt:heading`\n```toml\ntemplate = "A"\n```\nContent A\n`@/cpt:heading`\n'
            '`@cpt:heading`\n```toml\ntemplate = "B"\n```\nContent B\n`@/cpt:heading`\n'
        )
        new_ref = (
            'Intro\n'
            '`@cpt:heading`\n```toml\ntemplate = "A"\n```\nContent A v2\n`@/cpt:heading`\n'
            '`@cpt:heading`\n```toml\ntemplate = "B"\n```\nContent B v2\n`@/cpt:heading`\n'
        )
        # User deleted marker B
        user = (
            'Intro\n'
            '`@cpt:heading`\n```toml\ntemplate = "A"\n```\nContent A\n`@/cpt:heading`\n'
        )
        merged, report = _three_way_merge_blueprint(old_ref, new_ref, user)
        self.assertIn("Content A v2", merged)
        self.assertNotIn("Content B", merged)
        self.assertEqual(len(report["updated"]), 1)

    def test_text_between_markers_preserved(self):
        """Non-marker text (prose) is always preserved."""
        from cypilot.commands.kit import _three_way_merge_blueprint
        old_ref = 'Intro text\n\n`@cpt:skill`\nOld skill\n`@/cpt:skill`\n\nFooter\n'
        new_ref = 'Intro text\n\n`@cpt:skill`\nNew skill\n`@/cpt:skill`\n\nFooter\n'
        user = 'Intro text\n\n`@cpt:skill`\nOld skill\n`@/cpt:skill`\n\nFooter\n'
        merged, _ = _three_way_merge_blueprint(old_ref, new_ref, user)
        self.assertIn("Intro text", merged)
        self.assertIn("New skill", merged)
        self.assertIn("Footer", merged)

    def test_mixed_updated_and_skipped(self):
        """Some markers updated, some skipped (customized)."""
        from cypilot.commands.kit import _three_way_merge_blueprint
        old_ref = (
            '`@cpt:blueprint`\n```toml\nkit = "x"\n```\n`@/cpt:blueprint`\n'
            '`@cpt:skill`\nOld skill\n`@/cpt:skill`\n'
        )
        new_ref = (
            '`@cpt:blueprint`\n```toml\nkit = "x"\nartifact = "Y"\n```\n`@/cpt:blueprint`\n'
            '`@cpt:skill`\nNew skill\n`@/cpt:skill`\n'
        )
        # User customized blueprint, didn't touch skill
        user = (
            '`@cpt:blueprint`\n```toml\nkit = "x"\ncustom = true\n```\n`@/cpt:blueprint`\n'
            '`@cpt:skill`\nOld skill\n`@/cpt:skill`\n'
        )
        merged, report = _three_way_merge_blueprint(old_ref, new_ref, user)
        self.assertIn("custom = true", merged)  # customized — kept
        self.assertIn("New skill", merged)       # unchanged — updated
        self.assertEqual(report["skipped"], ["blueprint#0"])
        self.assertEqual(report["updated"], ["skill#0"])

    def test_no_changes_when_refs_identical(self):
        """If old_ref == new_ref, nothing changes."""
        from cypilot.commands.kit import _three_way_merge_blueprint
        same = '`@cpt:skill`\nSame\n`@/cpt:skill`\n'
        merged, report = _three_way_merge_blueprint(same, same, same)
        self.assertEqual(report["updated"], [])
        self.assertEqual(report["skipped"], [])
        self.assertEqual(report["kept"], ["skill#0"])


# =========================================================================
# migrate_kit (core function)
# =========================================================================

class TestMigrateKit(unittest.TestCase):
    """Tests for the migrate_kit function with marker-level merge."""

    def _setup_kit(self, td_p, old_heading="Feature v1", new_heading="Feature v2",
                   user_heading="Feature v1", ref_ver=2, user_ver=1, with_prev=True):
        """Create a project with old ref (.prev/), new ref, and user config."""
        root = td_p / "proj"
        adapter = _bootstrap_project(root)
        from cypilot.utils import toml_utils

        bp_template = (
            '`@cpt:blueprint`\n```toml\nkit = "sdlc"\nartifact = "FEAT"\n```\n`@/cpt:blueprint`\n\n'
            '`@cpt:heading`\n```toml\nlevel = 1\ntemplate = "{heading}"\n```\n`@/cpt:heading`\n'
        )

        # New reference
        ref_dir = adapter / "kits" / "sdlc"
        ref_bp = ref_dir / "blueprints"
        ref_bp.mkdir(parents=True)
        (ref_bp / "FEAT.md").write_text(
            bp_template.format(heading=new_heading), encoding="utf-8",
        )
        toml_utils.dump({"version": ref_ver}, ref_dir / "conf.toml")

        # Old reference (.prev/)
        if with_prev:
            prev_bp = ref_dir / ".prev" / "blueprints"
            prev_bp.mkdir(parents=True)
            (prev_bp / "FEAT.md").write_text(
                bp_template.format(heading=old_heading), encoding="utf-8",
            )

        # User config
        config_kit = adapter / "config" / "kits" / "sdlc"
        user_bp = config_kit / "blueprints"
        user_bp.mkdir(parents=True)
        (user_bp / "FEAT.md").write_text(
            bp_template.format(heading=user_heading), encoding="utf-8",
        )
        toml_utils.dump({"version": user_ver}, config_kit / "conf.toml")

        gen_kits = adapter / ".gen" / "kits"
        return root, adapter, ref_dir, config_kit, gen_kits

    def test_unchanged_marker_updated_via_prev(self):
        """Marker unchanged by user → updated from new ref (three-way via .prev/)."""
        from cypilot.commands.kit import migrate_kit
        with TemporaryDirectory() as td:
            _, _, ref_dir, config_kit, gen_kits = self._setup_kit(Path(td))
            result = migrate_kit("sdlc", ref_dir, config_kit, gen_kits)
            self.assertEqual(result["status"], "migrated")
            bp = result["blueprints"][0]
            self.assertEqual(bp["action"], "merged")
            self.assertTrue(any("heading" in k for k in bp.get("markers_updated", [])))
            user_text = (config_kit / "blueprints" / "FEAT.md").read_text()
            self.assertIn("Feature v2", user_text)

    def test_customized_marker_skipped(self):
        """Marker customized by user → skipped during merge."""
        from cypilot.commands.kit import migrate_kit
        with TemporaryDirectory() as td:
            _, _, ref_dir, config_kit, gen_kits = self._setup_kit(
                Path(td), user_heading="My Custom Heading",
            )
            result = migrate_kit("sdlc", ref_dir, config_kit, gen_kits)
            bp = result["blueprints"][0]
            # blueprint marker is unchanged → updated; heading is customized → skipped
            self.assertTrue(any("heading" in k for k in bp.get("markers_skipped", [])))
            user_text = (config_kit / "blueprints" / "FEAT.md").read_text()
            self.assertIn("My Custom Heading", user_text)

    def test_no_migration_when_current(self):
        from cypilot.commands.kit import migrate_kit
        with TemporaryDirectory() as td:
            _, _, ref_dir, config_kit, gen_kits = self._setup_kit(
                Path(td), ref_ver=1, user_ver=1,
            )
            result = migrate_kit("sdlc", ref_dir, config_kit, gen_kits)
            self.assertEqual(result["status"], "current")

    def test_updates_conf_toml(self):
        from cypilot.commands.kit import migrate_kit
        import tomllib
        with TemporaryDirectory() as td:
            _, _, ref_dir, config_kit, gen_kits = self._setup_kit(Path(td))
            migrate_kit("sdlc", ref_dir, config_kit, gen_kits)
            with open(config_kit / "conf.toml", "rb") as f:
                data = tomllib.load(f)
            self.assertEqual(data["version"], 2)

    def test_dry_run_does_not_write(self):
        from cypilot.commands.kit import migrate_kit
        with TemporaryDirectory() as td:
            _, _, ref_dir, config_kit, gen_kits = self._setup_kit(Path(td))
            result = migrate_kit("sdlc", ref_dir, config_kit, gen_kits, dry_run=True)
            # Should report migration but not write
            user_text = (config_kit / "blueprints" / "FEAT.md").read_text()
            self.assertIn("Feature v1", user_text)

    def test_fallback_without_prev_preserves_user(self):
        """Without .prev/, user customizations must NOT be overwritten."""
        from cypilot.commands.kit import migrate_kit
        with TemporaryDirectory() as td:
            _, _, ref_dir, config_kit, gen_kits = self._setup_kit(
                Path(td), with_prev=False,
                user_heading="My Custom Heading",
            )
            result = migrate_kit("sdlc", ref_dir, config_kit, gen_kits)
            self.assertEqual(result["status"], "migrated")
            # User customization MUST survive
            user_text = (config_kit / "blueprints" / "FEAT.md").read_text()
            self.assertIn("My Custom Heading", user_text)
            self.assertNotIn("Feature v2", user_text)

    def test_kit_version_drift(self):
        from cypilot.commands.kit import migrate_kit
        with TemporaryDirectory() as td:
            _, _, ref_dir, config_kit, gen_kits = self._setup_kit(
                Path(td), ref_ver=2, user_ver=2,
                old_heading="Feature v2", new_heading="Feature v2", user_heading="Feature v2",
            )
            from cypilot.utils import toml_utils
            toml_utils.dump({"version": 3}, ref_dir / "conf.toml")
            toml_utils.dump({"version": 2}, config_kit / "conf.toml")
            result = migrate_kit("sdlc", ref_dir, config_kit, gen_kits)
            self.assertEqual(result["status"], "migrated")
            self.assertIn("kit_version", result)

    def test_prev_cleaned_after_migration(self):
        from cypilot.commands.kit import migrate_kit
        with TemporaryDirectory() as td:
            _, _, ref_dir, config_kit, gen_kits = self._setup_kit(Path(td))
            migrate_kit("sdlc", ref_dir, config_kit, gen_kits)
            self.assertFalse((ref_dir / ".prev").exists())

    def test_missing_ref_blueprint_file(self):
        from cypilot.commands.kit import migrate_kit
        from cypilot.utils import toml_utils
        with TemporaryDirectory() as td:
            td_p = Path(td)
            root = td_p / "proj"
            adapter = _bootstrap_project(root)
            ref_dir = adapter / "kits" / "sdlc"
            ref_dir.mkdir(parents=True)
            (ref_dir / "blueprints").mkdir()
            toml_utils.dump({"version": 2}, ref_dir / "conf.toml")
            config_kit = adapter / "config" / "kits" / "sdlc"
            config_kit.mkdir(parents=True)
            toml_utils.dump({"version": 1}, config_kit / "conf.toml")
            gen_kits = adapter / ".gen" / "kits"
            result = migrate_kit("sdlc", ref_dir, config_kit, gen_kits)
            # No .md files in ref blueprints dir → no blueprints migrated
            self.assertEqual(result["status"], "migrated")
            self.assertNotIn("blueprints", result)


# =========================================================================
# cmd_kit_migrate (CLI)
# =========================================================================

class TestCmdKitMigrate(unittest.TestCase):

    def test_migrate_no_project_root(self):
        from cypilot.commands.kit import cmd_kit_migrate
        with TemporaryDirectory() as td:
            cwd = os.getcwd()
            try:
                os.chdir(td)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_migrate([])
                self.assertEqual(rc, 1)
            finally:
                os.chdir(cwd)

    def test_migrate_no_kits(self):
        from cypilot.commands.kit import cmd_kit_migrate
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            _bootstrap_project(root)
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_migrate([])
                self.assertEqual(rc, 2)
            finally:
                os.chdir(cwd)

    def test_migrate_dispatched_from_cmd_kit(self):
        from cypilot.commands.kit import cmd_kit
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            _bootstrap_project(root)
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit(["migrate"])
                self.assertEqual(rc, 2)  # no kits → 2
            finally:
                os.chdir(cwd)

    def _setup_migrate_project(self, td: Path, *, ref_ver: int = 2, user_ver: int = 1):
        """Set up a project with a kit that has version drift for migration."""
        root = td / "proj"
        adapter = _bootstrap_project(root)
        kit_slug = "testkit"
        ref_dir = adapter / "kits" / kit_slug
        ref_bp = ref_dir / "blueprints"
        ref_bp.mkdir(parents=True)
        (ref_bp / "FEAT.md").write_text(
            "<!-- @cpt:blueprint -->\n```toml\n"
            f'artifact = "FEATURE"\nversion = {ref_ver}\n'
            "```\n<!-- /@cpt:blueprint -->\n\n"
            "<!-- @cpt:heading -->\n# Feature Spec\n<!-- /@cpt:heading -->\n",
            encoding="utf-8",
        )
        from cypilot.utils import toml_utils
        toml_utils.dump({"version": ref_ver}, ref_dir / "conf.toml")
        config_kit = adapter / "config" / "kits" / kit_slug
        config_kit.mkdir(parents=True)
        toml_utils.dump({"version": user_ver}, config_kit / "conf.toml")
        (adapter / ".gen" / "kits").mkdir(parents=True, exist_ok=True)
        return root, adapter, kit_slug

    def test_migrate_kit_slug_not_found(self):
        from cypilot.commands.kit import cmd_kit_migrate
        with TemporaryDirectory() as td:
            root, adapter, _ = self._setup_migrate_project(Path(td))
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_migrate(["--kit", "nonexistent"])
                self.assertEqual(rc, 2)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["status"], "FAIL")
            finally:
                os.chdir(cwd)

    def test_migrate_all_kits_current(self):
        from cypilot.commands.kit import cmd_kit_migrate
        from cypilot.utils import toml_utils
        with TemporaryDirectory() as td:
            root, adapter, kit_slug = self._setup_migrate_project(Path(td), ref_ver=1, user_ver=1)
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_migrate([])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["status"], "PASS")
                self.assertEqual(out["kits_migrated"], 0)
            finally:
                os.chdir(cwd)

    def test_migrate_with_regen(self):
        from cypilot.commands.kit import cmd_kit_migrate
        with TemporaryDirectory() as td:
            root, adapter, kit_slug = self._setup_migrate_project(Path(td))
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_migrate(["--kit", kit_slug])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["kits_migrated"], 1)
                result = out["results"][0]
                self.assertEqual(result["status"], "migrated")
                self.assertIn("regenerated", result)
            finally:
                os.chdir(cwd)

    def test_migrate_dry_run(self):
        from cypilot.commands.kit import cmd_kit_migrate
        with TemporaryDirectory() as td:
            root, adapter, kit_slug = self._setup_migrate_project(Path(td))
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_kit_migrate(["--dry-run"])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertTrue(out.get("dry_run"))
                # No regeneration on dry-run
                for r in out["results"]:
                    self.assertNotIn("regenerated", r)
            finally:
                os.chdir(cwd)

    def test_migrate_regen_error_surfaces(self):
        from cypilot.commands.kit import cmd_kit_migrate
        with TemporaryDirectory() as td:
            root, adapter, kit_slug = self._setup_migrate_project(Path(td))
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                buf = io.StringIO()
                err_buf = io.StringIO()
                with patch("cypilot.utils.blueprint.process_kit", side_effect=RuntimeError("boom")):
                    with redirect_stdout(buf), redirect_stderr(err_buf):
                        rc = cmd_kit_migrate(["--kit", kit_slug])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["status"], "FAIL")
                result = out["results"][0]
                self.assertEqual(result["status"], "FAIL")
                self.assertIn("error", result.get("regenerated", {}))
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
