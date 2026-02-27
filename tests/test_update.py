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
    bp_dir = cache_dir / "kits" / "sdlc" / "blueprints"
    bp_dir.mkdir(parents=True, exist_ok=True)
    (bp_dir / "prd.md").write_text(
        "<!-- @cpt:blueprint -->\n```toml\n"
        f'artifact = "PRD"\nkit = "sdlc"\nversion = {kit_version}\n'
        "```\n<!-- /@cpt:blueprint -->\n\n"
        "<!-- @cpt:heading -->\n# Product Requirements\n<!-- /@cpt:heading -->\n",
        encoding="utf-8",
    )
    scripts_dir = cache_dir / "kits" / "sdlc" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    (scripts_dir / "helper.py").write_text("# helper\n", encoding="utf-8")
    _write_toml(cache_dir / "kits" / "sdlc" / "conf.toml", {
        "version": kit_version,
        "blueprints": {"prd": kit_version},
        "scripts": {"helper": kit_version},
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

    def test_read_project_name_from_core_toml(self):
        from cypilot.commands.update import _read_project_name
        with TemporaryDirectory() as td:
            config_dir = Path(td)
            _write_toml(config_dir / "core.toml", {
                "system": {"name": "MyProject", "slug": "myproject"},
            })
            self.assertEqual(_read_project_name(config_dir), "MyProject")

    def test_read_project_name_missing(self):
        from cypilot.commands.update import _read_project_name
        with TemporaryDirectory() as td:
            self.assertIsNone(_read_project_name(Path(td)))

    def test_read_project_name_corrupt(self):
        from cypilot.commands.update import _read_project_name
        with TemporaryDirectory() as td:
            (Path(td) / "core.toml").write_text("{{invalid", encoding="utf-8")
            self.assertIsNone(_read_project_name(Path(td)))

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

    def test_read_conf_section(self):
        from cypilot.commands.update import _read_conf_section
        with TemporaryDirectory() as td:
            p = Path(td) / "conf.toml"
            _write_toml(p, {"blueprints": {"prd": 2, "design": 1}})
            result = _read_conf_section(p, "blueprints")
            self.assertEqual(result, {"prd": 2, "design": 1})

    def test_read_conf_section_missing_file(self):
        from cypilot.commands.update import _read_conf_section
        self.assertEqual(_read_conf_section(Path("/none"), "x"), {})

    def test_read_conf_section_non_dict(self):
        from cypilot.commands.update import _read_conf_section
        with TemporaryDirectory() as td:
            p = Path(td) / "conf.toml"
            _write_toml(p, {"blueprints": "not a dict"})
            self.assertEqual(_read_conf_section(p, "blueprints"), {})


class TestCompareConfVersions(unittest.TestCase):
    """Tests for _compare_conf_versions drift detection."""

    def test_current_when_equal(self):
        from cypilot.commands.update import _compare_conf_versions
        result = _compare_conf_versions(1, 1, {"prd": 1}, {"prd": 1}, {}, {})
        self.assertEqual(result["status"], "current")

    def test_migration_needed_kit_version(self):
        from cypilot.commands.update import _compare_conf_versions
        result = _compare_conf_versions(2, 1, {}, {}, {}, {})
        self.assertEqual(result["status"], "migration_needed")
        self.assertIn("kit_version_drift", result)

    def test_migration_needed_blueprint_drift(self):
        from cypilot.commands.update import _compare_conf_versions
        result = _compare_conf_versions(1, 1, {"prd": 2}, {"prd": 1}, {}, {})
        self.assertEqual(result["status"], "migration_needed")
        self.assertIn("blueprint_drift", result)
        self.assertEqual(result["blueprint_drift"]["prd"]["cache"], 2)

    def test_migration_needed_script_drift(self):
        from cypilot.commands.update import _compare_conf_versions
        result = _compare_conf_versions(1, 1, {}, {}, {"helper": 2}, {"helper": 1})
        self.assertEqual(result["status"], "migration_needed")
        self.assertIn("script_drift", result)

    def test_new_blueprint_triggers_migration(self):
        from cypilot.commands.update import _compare_conf_versions
        result = _compare_conf_versions(1, 1, {"new": 1}, {}, {}, {})
        self.assertEqual(result["status"], "migration_needed")
        self.assertEqual(result["blueprint_drift"]["new"]["user"], 0)


# =========================================================================
# cmd_update error paths
# =========================================================================

class TestCmdUpdateErrors(unittest.TestCase):
    """Error handling in cmd_update."""

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
                self.assertIn("gen_kits", out["actions"])
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

    def test_update_version_drift_warns(self):
        """When cache has newer kit version, update warns about migration."""
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
                # Should have warnings about migration needed
                stderr_text = err.getvalue()
                self.assertIn("MIGRATION", stderr_text)
                kit_versions = out["actions"].get("kit_versions", {})
                sdlc_drift = kit_versions.get("sdlc", {})
                self.assertEqual(sdlc_drift.get("status"), "migration_needed")
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

    def test_update_first_install_blueprints(self):
        """Update copies blueprints on first install (no user blueprints yet)."""
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            cache = Path(td) / "cache"
            _make_cache(cache)
            adapter = _init_project(root, cache)

            # Remove user blueprints to simulate first install scenario
            user_bp = adapter / "config" / "kits" / "sdlc" / "blueprints"
            if user_bp.exists():
                shutil.rmtree(user_bp)
            # Also remove conf.toml
            user_conf = adapter / "config" / "kits" / "sdlc" / "conf.toml"
            if user_conf.exists():
                user_conf.unlink()

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
                kit_versions = out["actions"].get("kit_versions", {})
                self.assertEqual(kit_versions.get("sdlc", {}).get("status"), "created")
                # Blueprints should now exist
                self.assertTrue(user_bp.is_dir())
            finally:
                os.chdir(cwd)


def _make_rich_cache(cache_dir: Path) -> None:
    """Cache with blueprints that have @cpt:skill, @cpt:sysprompt, @cpt:workflow markers."""
    for d in ("architecture", "requirements", "schemas", "workflows", "skills"):
        (cache_dir / d).mkdir(parents=True, exist_ok=True)
        (cache_dir / d / "README.md").write_text(f"# {d}\n", encoding="utf-8")
    bp_dir = cache_dir / "kits" / "rich" / "blueprints"
    bp_dir.mkdir(parents=True, exist_ok=True)
    (bp_dir / "feature.md").write_text(
        "<!-- @cpt:blueprint -->\n```toml\n"
        'artifact = "FEATURE"\nkit = "rich"\nversion = 1\n'
        "```\n<!-- /@cpt:blueprint -->\n\n"
        "<!-- @cpt:heading -->\n# Feature Spec\n<!-- /@cpt:heading -->\n\n"
        "<!-- @cpt:skill -->\nUse this kit for feature specs.\n<!-- /@cpt:skill -->\n\n"
        "<!-- @cpt:sysprompt -->\nYou are a feature assistant.\n<!-- /@cpt:sysprompt -->\n\n"
        "<!-- @cpt:workflow -->\n```toml\n"
        'name = "feature-review"\ndescription = "Review features"\n'
        'version = "1.0"\npurpose = "QA"\n'
        "```\n\nReview the feature.\n<!-- /@cpt:workflow -->\n",
        encoding="utf-8",
    )
    _write_toml(cache_dir / "kits" / "rich" / "conf.toml", {
        "version": 1, "blueprints": {"feature": 1},
    })


class TestUpdateWithRichBlueprints(unittest.TestCase):
    """Update with skill/sysprompt/workflow content to cover gen lines 242-283."""

    def test_update_generates_skill_sysprompt_workflow(self):
        """Mock process_kit to return rich content → covers gen lines 242-283."""
        from cypilot.commands.update import cmd_update
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            cache = Path(td) / "cache"
            _make_cache(cache)
            _init_project(root, cache)

            fake_summary = {
                "files_written": 1,
                "artifact_kinds": ["PRD"],
                "files": ["prd.md"],
                "skill_content": "## PRD\n\nUse this kit for PRDs.",
                "sysprompt_content": "You are a requirements assistant.",
                "workflows": [
                    {"name": "review", "description": "Review docs",
                     "version": "1.0", "purpose": "QA", "content": "Review the doc."},
                ],
            }

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with patch("cypilot.commands.update.CACHE_DIR", cache):
                    with patch("cypilot.utils.blueprint.process_kit",
                               return_value=(fake_summary, [])):
                        buf = io.StringIO()
                        err = io.StringIO()
                        with redirect_stdout(buf), redirect_stderr(err):
                            rc = cmd_update([])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertIn(out["status"], ["PASS", "WARN"])

                adapter = root / "cypilot"
                gen_dir = adapter / ".gen"
                # SKILL.md should reference the kit
                skill_md = gen_dir / "SKILL.md"
                self.assertTrue(skill_md.is_file())
                skill_text = skill_md.read_text(encoding="utf-8")
                self.assertIn("sdlc", skill_text)

                # AGENTS.md should have sysprompt content
                agents_md = gen_dir / "AGENTS.md"
                self.assertTrue(agents_md.is_file())
                agents_text = agents_md.read_text(encoding="utf-8")
                self.assertIn("requirements assistant", agents_text)

                # Workflow file should exist
                wf_dir = gen_dir / "kits" / "sdlc" / "workflows"
                self.assertTrue(wf_dir.is_dir())
                wf_files = list(wf_dir.glob("*.md"))
                self.assertGreater(len(wf_files), 0)
                wf_text = wf_files[0].read_text(encoding="utf-8")
                self.assertIn("cypilot: true", wf_text)
                self.assertIn("type: workflow", wf_text)
                self.assertIn("description: Review docs", wf_text)
                self.assertIn("version: 1.0", wf_text)
                self.assertIn("purpose: QA", wf_text)
            finally:
                os.chdir(cwd)


class TestUpdateHelperExceptions(unittest.TestCase):
    """Cover exception paths in _read_conf_version/_read_conf_section."""

    def test_read_conf_version_corrupt_toml(self):
        from cypilot.commands.update import _read_conf_version
        with TemporaryDirectory() as td:
            p = Path(td) / "conf.toml"
            p.write_text("{{corrupt", encoding="utf-8")
            self.assertEqual(_read_conf_version(p), 0)

    def test_read_conf_section_corrupt_toml(self):
        from cypilot.commands.update import _read_conf_section
        with TemporaryDirectory() as td:
            p = Path(td) / "conf.toml"
            p.write_text("{{corrupt", encoding="utf-8")
            self.assertEqual(_read_conf_section(p, "blueprints"), {})

    def test_update_with_process_kit_errors(self):
        """When process_kit returns errors, update records them."""
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
                fake_summary = {"files_written": 0, "artifact_kinds": []}
                fake_errors = ["blueprint parse error"]
                with patch("cypilot.commands.update.CACHE_DIR", cache):
                    with patch("cypilot.utils.blueprint.process_kit",
                               return_value=(fake_summary, fake_errors)):
                        buf = io.StringIO()
                        err = io.StringIO()
                        with redirect_stdout(buf), redirect_stderr(err):
                            rc = cmd_update([])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["status"], "WARN")
                self.assertTrue(out.get("errors"))
            finally:
                os.chdir(cwd)

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


if __name__ == "__main__":
    unittest.main()
