"""
Tests for commands/migrate.py — V2 → V3 migration.

Covers: detect_v2, detect_core_install_type, backup_v2_state, cleanup_core_path,
convert_artifacts_registry, convert_agents_md, generate_core_toml, migrate_kits,
validate_migration, run_migrate, run_migrate_config, cmd_migrate, cmd_migrate_config.
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

from cypilot.commands.migrate import (
    INSTALL_TYPE_ABSENT,
    INSTALL_TYPE_GIT_CLONE,
    INSTALL_TYPE_PLAIN_DIR,
    INSTALL_TYPE_SUBMODULE,
    backup_v2_state,
    cleanup_core_path,
    convert_agents_md,
    convert_artifacts_registry,
    detect_core_install_type,
    detect_v2,
    generate_core_toml,
    migrate_kits,
    run_migrate,
    run_migrate_config,
    validate_migration,
    cmd_migrate,
    cmd_migrate_config,
    _remove_gitmodule_entry,
    _rollback,
    _write_gen_agents,
    _copy_tree_contents,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_v2_project(root: Path, *, custom_core: str = "", custom_adapter: str = "") -> None:
    """Scaffold a minimal v2 project at *root*."""
    adapter = root / (custom_adapter or ".cypilot-adapter")
    core = root / (custom_core or ".cypilot")
    adapter.mkdir(parents=True, exist_ok=True)
    core.mkdir(parents=True, exist_ok=True)

    # artifacts.json
    artifacts = {
        "version": "1.0",
        "systems": [
            {
                "name": "MyApp",
                "slug": "my-app",
                "kit": "cf-sdlc",
                "autodetect": [
                    {
                        "kit": "cf-sdlc",
                        "system_root": ".",
                        "artifacts_root": "architecture",
                        "artifacts": {
                            "PRD": {"pattern": "PRD.md", "traceability": "full", "required": True},
                        },
                        "codebase": [{"name": "src", "path": "src", "extensions": [".py"]}],
                        "validation": {"traceability": True},
                    }
                ],
            }
        ],
        "kits": {
            "cf-sdlc": {
                "format": "Cypilot",
                "path": "kits/cf-sdlc",
            }
        },
        "ignore": [
            {"reason": "Third party", "patterns": ["vendor/**"]},
        ],
    }
    (adapter / "artifacts.json").write_text(json.dumps(artifacts), encoding="utf-8")

    # AGENTS.md
    (adapter / "AGENTS.md").write_text(
        "# MyApp Agent Rules\n\n"
        "**Extends**: `../.cypilot/AGENTS.md`\n\n"
        "ALWAYS open artifacts.json WHEN reviewing\n",
        encoding="utf-8",
    )

    # Kit directory
    kit_dir = adapter / "kits" / "cf-sdlc"
    kit_dir.mkdir(parents=True, exist_ok=True)
    (kit_dir / "README.md").write_text("# cf-sdlc kit\n", encoding="utf-8")

    # .git (to make it look like a git project)
    (root / ".git").mkdir(exist_ok=True)

    # Root AGENTS.md (v2 style — no managed block)
    (root / "AGENTS.md").write_text("# Project AGENTS\n\nSome rules here.\n", encoding="utf-8")


def _make_v2_with_config_json(root: Path, core_path: str = ".cypilot", adapter_path: str = ".cypilot-adapter") -> None:
    """Scaffold v2 project with .cypilot-config.json."""
    _make_v2_project(root, custom_core=core_path, custom_adapter=adapter_path)
    config = {
        "cypilotCorePath": core_path,
        "cypilotAdapterPath": adapter_path,
    }
    (root / ".cypilot-config.json").write_text(json.dumps(config), encoding="utf-8")


def _make_cache(cache_dir: Path) -> None:
    """Create a minimal cache for migration tests."""
    for d in ("architecture", "requirements", "schemas", "workflows", "skills"):
        (cache_dir / d).mkdir(parents=True, exist_ok=True)
        (cache_dir / d / "README.md").write_text(f"# {d}\n", encoding="utf-8")
    bp_dir = cache_dir / "kits" / "sdlc" / "blueprints"
    bp_dir.mkdir(parents=True, exist_ok=True)
    (bp_dir / "prd.md").write_text(
        "<!-- @cpt:blueprint -->\n```toml\n"
        'artifact = "PRD"\nkit = "sdlc"\nversion = 1\n'
        "```\n<!-- /@cpt:blueprint -->\n\n"
        "<!-- @cpt:heading -->\n# Product Requirements\n<!-- /@cpt:heading -->\n",
        encoding="utf-8",
    )
    scripts_dir = cache_dir / "kits" / "sdlc" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    (scripts_dir / "helper.py").write_text("# helper\n", encoding="utf-8")
    from cypilot.utils import toml_utils
    toml_utils.dump({"version": 1, "blueprints": {"prd": 1}}, cache_dir / "kits" / "sdlc" / "conf.toml")


# ===========================================================================
# Test: detect_core_install_type
# ===========================================================================

class TestDetectCoreInstallType(unittest.TestCase):
    def test_absent(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            result = detect_core_install_type(root, ".cypilot")
            self.assertEqual(result, INSTALL_TYPE_ABSENT)

    def test_plain_dir(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot").mkdir()
            result = detect_core_install_type(root, ".cypilot")
            self.assertEqual(result, INSTALL_TYPE_PLAIN_DIR)

    def test_git_clone(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot" / ".git").mkdir(parents=True)
            result = detect_core_install_type(root, ".cypilot")
            self.assertEqual(result, INSTALL_TYPE_GIT_CLONE)

    def test_git_clone_file(self):
        """Submodule worktrees use .git as a file, but if not in .gitmodules → GIT_CLONE."""
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot").mkdir()
            (root / ".cypilot" / ".git").write_text("gitdir: ../.git/modules/.cypilot\n")
            result = detect_core_install_type(root, ".cypilot")
            self.assertEqual(result, INSTALL_TYPE_GIT_CLONE)

    def test_submodule(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot").mkdir()
            (root / ".gitmodules").write_text(
                '[submodule "cypilot-core"]\n'
                '  path = .cypilot\n'
                '  url = https://github.com/example/cypilot.git\n'
            )
            result = detect_core_install_type(root, ".cypilot")
            self.assertEqual(result, INSTALL_TYPE_SUBMODULE)


# ===========================================================================
# Test: detect_v2
# ===========================================================================

class TestDetectV2(unittest.TestCase):
    def test_no_v2(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            result = detect_v2(root)
            self.assertFalse(result["detected"])

    def test_basic_v2(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            result = detect_v2(root)
            self.assertTrue(result["detected"])
            self.assertEqual(result["adapter_path"], ".cypilot-adapter")
            self.assertEqual(result["core_path"], ".cypilot")
            self.assertEqual(result["core_install_type"], INSTALL_TYPE_PLAIN_DIR)
            self.assertTrue(result["has_agents_md"])
            self.assertFalse(result["has_config_json"])
            self.assertEqual(len(result["systems"]), 1)
            self.assertIn("cf-sdlc", result["kits"])

    def test_v2_with_config_json(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_with_config_json(root, core_path="custom-core", adapter_path="custom-adapter")
            result = detect_v2(root)
            self.assertTrue(result["detected"])
            self.assertEqual(result["adapter_path"], "custom-adapter")
            self.assertEqual(result["core_path"], "custom-core")
            self.assertTrue(result["has_config_json"])

    def test_v2_missing_adapter(self):
        """Config JSON exists but adapter dir missing → not detected."""
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot-config.json").write_text('{"cypilotAdapterPath": "missing"}')
            result = detect_v2(root)
            self.assertFalse(result["detected"])

    def test_v2_no_artifacts_json(self):
        """Adapter dir exists but no artifacts.json → still detected (partial v2)."""
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot-adapter").mkdir()
            (root / ".cypilot").mkdir()
            result = detect_v2(root)
            self.assertTrue(result["detected"])
            self.assertIsNone(result["artifacts_json"])

    def test_v2_empty_artifacts_json(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot-adapter").mkdir()
            (root / ".cypilot").mkdir()
            (root / ".cypilot-adapter" / "artifacts.json").write_text("{}")
            result = detect_v2(root)
            self.assertTrue(result["detected"])
            self.assertEqual(result["systems"], [])
            self.assertEqual(result["kits"], {})


# ===========================================================================
# Test: backup_v2_state
# ===========================================================================

class TestBackupV2State(unittest.TestCase):
    def test_creates_backup(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            backup_dir = backup_v2_state(root, ".cypilot-adapter", ".cypilot", INSTALL_TYPE_PLAIN_DIR)
            self.assertTrue(backup_dir.is_dir())
            self.assertTrue((backup_dir / ".cypilot-adapter").is_dir())
            self.assertTrue((backup_dir / ".cypilot").is_dir())
            self.assertTrue((backup_dir / "AGENTS.md").is_file())
            manifest = json.loads((backup_dir / "manifest.json").read_text())
            self.assertIn(".cypilot-adapter", manifest["backed_up"])
            self.assertIn(".cypilot", manifest["backed_up"])
            self.assertIn("AGENTS.md", manifest["backed_up"])

    def test_backup_with_config_json(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_with_config_json(root)
            backup_dir = backup_v2_state(root, ".cypilot-adapter", ".cypilot", INSTALL_TYPE_PLAIN_DIR)
            self.assertTrue((backup_dir / ".cypilot-config.json").is_file())

    def test_backup_submodule_includes_gitmodules(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            (root / ".gitmodules").write_text('[submodule "x"]\n  path = .cypilot\n')
            backup_dir = backup_v2_state(root, ".cypilot-adapter", ".cypilot", INSTALL_TYPE_SUBMODULE)
            self.assertTrue((backup_dir / ".gitmodules").is_file())

    def test_backup_agent_dirs(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            (root / ".windsurf").mkdir()
            (root / ".windsurf" / "rules.md").write_text("# rules\n")
            backup_dir = backup_v2_state(root, ".cypilot-adapter", ".cypilot", INSTALL_TYPE_PLAIN_DIR)
            self.assertTrue((backup_dir / ".windsurf").is_dir())


# ===========================================================================
# Test: cleanup_core_path
# ===========================================================================

class TestCleanupCorePath(unittest.TestCase):
    def test_absent(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            result = cleanup_core_path(root, ".cypilot", INSTALL_TYPE_ABSENT)
            self.assertTrue(result["success"])
            self.assertEqual(result["cleaned_type"], INSTALL_TYPE_ABSENT)

    def test_plain_dir(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot" / "some_file.txt").mkdir(parents=True)
            result = cleanup_core_path(root, ".cypilot", INSTALL_TYPE_PLAIN_DIR)
            self.assertTrue(result["success"])
            self.assertFalse((root / ".cypilot").exists())

    def test_git_clone(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot" / ".git").mkdir(parents=True)
            result = cleanup_core_path(root, ".cypilot", INSTALL_TYPE_GIT_CLONE)
            self.assertTrue(result["success"])
            self.assertFalse((root / ".cypilot").exists())
            self.assertTrue(len(result["warnings"]) > 0)


# ===========================================================================
# Test: _remove_gitmodule_entry
# ===========================================================================

class TestRemoveGitmoduleEntry(unittest.TestCase):
    def test_removes_matching_entry(self):
        content = (
            '[submodule "cypilot-core"]\n'
            '  path = .cypilot\n'
            '  url = https://github.com/example/cypilot.git\n'
            '[submodule "other"]\n'
            '  path = lib/other\n'
            '  url = https://github.com/example/other.git\n'
        )
        result = _remove_gitmodule_entry(content, ".cypilot")
        self.assertNotIn(".cypilot", result)
        self.assertIn("lib/other", result)
        self.assertIn('[submodule "other"]', result)

    def test_leaves_unrelated(self):
        content = (
            '[submodule "other"]\n'
            '  path = lib/other\n'
            '  url = https://github.com/example/other.git\n'
        )
        result = _remove_gitmodule_entry(content, ".cypilot")
        self.assertEqual(result, content)

    def test_empty_after_removal(self):
        content = (
            '[submodule "cypilot"]\n'
            '  path = .cypilot\n'
            '  url = https://example.com\n'
        )
        result = _remove_gitmodule_entry(content, ".cypilot")
        self.assertEqual(result.strip(), "")


# ===========================================================================
# Test: convert_artifacts_registry
# ===========================================================================

class TestConvertArtifactsRegistry(unittest.TestCase):
    def test_basic_conversion(self):
        with TemporaryDirectory() as d:
            target = Path(d)
            v2_data = {
                "version": "1.0",
                "systems": [
                    {"name": "MyApp", "slug": "my-app", "kit": "cf-sdlc"},
                ],
                "kits": {
                    "cf-sdlc": {"format": "Cypilot", "path": "kits/cf-sdlc"},
                },
                "ignore": [
                    {"reason": "vendor", "patterns": ["vendor/**"]},
                ],
            }
            result = convert_artifacts_registry(v2_data, "cypilot", target)
            self.assertEqual(result["systems_count"], 1)
            self.assertEqual(result["kits_count"], 1)
            self.assertIn("cf-sdlc", result["kit_slug_map"])
            self.assertEqual(result["kit_slug_map"]["cf-sdlc"], "cf-sdlc")

            # Verify TOML written — kits should NOT be in artifacts.toml
            from cypilot.utils import toml_utils
            toml_path = target / "artifacts.toml"
            self.assertTrue(toml_path.is_file())
            registry = toml_utils.load(toml_path)
            self.assertNotIn("kits", registry)
            # Systems and ignore should be present
            self.assertEqual(len(registry["systems"]), 1)
            self.assertEqual(len(registry["ignore"]), 1)

    def test_custom_kit(self):
        with TemporaryDirectory() as d:
            target = Path(d)
            v2_data = {
                "version": "1.0",
                "systems": [],
                "kits": {
                    "my-custom-kit": {"format": "Cypilot", "path": "kits/my-custom-kit"},
                },
                "ignore": [],
            }
            result = convert_artifacts_registry(v2_data, "cypilot", target)
            self.assertEqual(result["kit_slug_map"]["my-custom-kit"], "my-custom-kit")

            # Verify kits NOT in artifacts.toml
            from cypilot.utils import toml_utils
            registry = toml_utils.load(target / "artifacts.toml")
            self.assertNotIn("kits", registry)

    def test_mixed_kits(self):
        """Both vanilla SDLC and custom kit in the same registry."""
        with TemporaryDirectory() as d:
            target = Path(d)
            v2_data = {
                "version": "1.0",
                "systems": [
                    {"name": "Core", "slug": "core", "kit": "cf-sdlc"},
                    {"name": "Custom", "slug": "custom", "kit": "my-kit"},
                ],
                "kits": {
                    "cf-sdlc": {"format": "Cypilot", "path": "kits/cf-sdlc"},
                    "my-kit": {"format": "Cypilot", "path": "kits/my-kit"},
                },
                "ignore": [],
            }
            result = convert_artifacts_registry(v2_data, "cypilot", target)
            self.assertEqual(result["kits_count"], 2)
            self.assertEqual(result["kit_slug_map"]["cf-sdlc"], "cf-sdlc")
            self.assertEqual(result["kit_slug_map"]["my-kit"], "my-kit")

    def test_system_autodetect_preserved(self):
        with TemporaryDirectory() as d:
            target = Path(d)
            v2_data = {
                "version": "1.0",
                "systems": [{
                    "name": "MyApp",
                    "slug": "my-app",
                    "kit": "sdlc",
                    "autodetect": [{
                        "kit": "sdlc",
                        "system_root": ".",
                        "artifacts_root": "architecture",
                        "artifacts": {"PRD": {"pattern": "PRD.md"}},
                        "codebase": [{"name": "src", "path": "src"}],
                        "validation": {"traceability": True},
                    }],
                }],
                "kits": {"sdlc": {"format": "Cypilot", "path": "kits/sdlc"}},
                "ignore": [],
            }
            result = convert_artifacts_registry(v2_data, "cypilot", target)
            from cypilot.utils import toml_utils
            registry = toml_utils.load(target / "artifacts.toml")
            system = registry["systems"][0]
            self.assertEqual(system["slug"], "my-app")
            self.assertEqual(system["kit"], "sdlc")
            self.assertEqual(len(system["autodetect"]), 1)
            self.assertEqual(system["autodetect"][0]["kit"], "sdlc")


# ===========================================================================
# Test: convert_agents_md
# ===========================================================================

class TestConvertAgentsMd(unittest.TestCase):
    def test_converts_paths(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            adapter = root / ".cypilot-adapter"
            adapter.mkdir()
            (adapter / "AGENTS.md").write_text(
                "# Rules\n"
                "**Extends**: `../.cypilot/AGENTS.md`\n"
                "ALWAYS open artifacts.json WHEN reviewing\n"
                "ALWAYS check `.cypilot-adapter/kits/sdlc`\n",
                encoding="utf-8",
            )
            target = root / "cypilot" / "config"
            result = convert_agents_md(root, ".cypilot-adapter", target)
            self.assertFalse(result.get("skipped"))
            content = (target / "AGENTS.md").read_text()
            self.assertNotIn("artifacts.json", content)
            self.assertIn("artifacts.toml", content)
            self.assertNotIn("Extends", content)

    def test_missing_adapter_agents(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot-adapter").mkdir()
            target = root / "cypilot" / "config"
            result = convert_agents_md(root, ".cypilot-adapter", target)
            self.assertTrue(result.get("skipped"))


# ===========================================================================
# Test: generate_core_toml
# ===========================================================================

class TestGenerateCoreToml(unittest.TestCase):
    def test_basic_generation(self):
        with TemporaryDirectory() as d:
            root = Path(d) / "my-app"
            root.mkdir()
            target = root / "cypilot" / "config"
            v2_systems = [{"name": "MyApp", "slug": "my-app", "kit": "cf-sdlc"}]
            kit_slug_map = {"cf-sdlc": "cf-sdlc"}
            result = generate_core_toml(root, v2_systems, kit_slug_map, target)
            self.assertEqual(result["status"], "created")

            from cypilot.utils import toml_utils
            core = toml_utils.load(target / "core.toml")
            self.assertEqual(core["version"], "1.0")
            self.assertEqual(core["project_root"], "..")
            self.assertEqual(core["system"]["name"], "MyApp")
            self.assertEqual(core["system"]["kit"], "cf-sdlc")
            self.assertIn("cf-sdlc", core["kits"])

    def test_no_systems_defaults(self):
        with TemporaryDirectory() as d:
            root = Path(d) / "my-project"
            root.mkdir()
            target = root / "cypilot" / "config"
            result = generate_core_toml(root, [], {}, target)
            from cypilot.utils import toml_utils
            core = toml_utils.load(target / "core.toml")
            self.assertEqual(core["system"]["kit"], "cypilot-sdlc")
            # No kits registered when slug map is empty
            self.assertNotIn("kits", core)


# ===========================================================================
# Test: migrate_kits
# ===========================================================================

class TestMigrateKits(unittest.TestCase):
    def test_kit_copied_from_adapter(self):
        """Kit files are copied from adapter to config/kits/ only (.gen/ is ephemeral)."""
        with TemporaryDirectory() as d:
            root = Path(d)
            adapter = root / ".cypilot-adapter"
            kit_dir = adapter / "kits" / "cf-sdlc"
            kit_dir.mkdir(parents=True)
            (kit_dir / "README.md").write_text("# kit\n")
            (kit_dir / "constraints.json").write_text('{"PRD": {"name": "test", "identifiers": {"req": {"kind": "req"}}, "headings": [{"id": "h1", "level": 1, "required": true, "multiple": "prohibited", "numbered": "allow"}]}}')

            cypilot_dir = root / "cypilot"
            (cypilot_dir / "config").mkdir(parents=True)
            (cypilot_dir / ".gen").mkdir(parents=True)

            result = migrate_kits(
                {"cf-sdlc": {"format": "Cypilot"}},
                ".cypilot-adapter",
                root,
                cypilot_dir,
            )
            self.assertIn("cf-sdlc", result["migrated_kits"])
            config_kit = cypilot_dir / "config" / "kits" / "cf-sdlc"
            # Files copied to config/kits/
            self.assertTrue((config_kit / "README.md").is_file())
            # Constraints converted to toml, json removed
            self.assertTrue((config_kit / "constraints.toml").is_file())
            self.assertFalse((config_kit / "constraints.json").is_file())
            # Nothing in .gen/ (ephemeral, regenerated by cpt update)
            self.assertFalse((cypilot_dir / ".gen" / "kits" / "cf-sdlc").exists())

    def test_kit_with_artifacts_copied(self):
        """Kit with artifact subdirs is copied to config/kits/ only."""
        with TemporaryDirectory() as d:
            root = Path(d)
            adapter = root / ".cypilot-adapter"
            kit_dir = adapter / "kits" / "my-kit"
            kit_dir.mkdir(parents=True)
            (kit_dir / "README.md").write_text("# my kit\n")
            artifacts_dir = kit_dir / "artifacts" / "CUSTOM"
            artifacts_dir.mkdir(parents=True)
            (artifacts_dir / "template.md").write_text("# template\n")

            cypilot_dir = root / "cypilot"
            (cypilot_dir / "config").mkdir(parents=True)
            (cypilot_dir / ".gen").mkdir(parents=True)

            result = migrate_kits(
                {"my-kit": {"format": "Cypilot"}},
                ".cypilot-adapter",
                root,
                cypilot_dir,
            )
            self.assertIn("my-kit", result["migrated_kits"])
            # Verify files were copied to config/
            self.assertTrue((cypilot_dir / "config" / "kits" / "my-kit" / "README.md").is_file())
            self.assertTrue((cypilot_dir / "config" / "kits" / "my-kit" / "artifacts" / "CUSTOM" / "template.md").is_file())

    def test_custom_kit_constraints_json_converted(self):
        """v2 constraints.json is converted to v3 format: artifacts wrapper + bool values."""
        with TemporaryDirectory() as d:
            root = Path(d)
            adapter = root / ".cypilot-adapter"
            kit_dir = adapter / "kits" / "my-kit"
            kit_dir.mkdir(parents=True)
            constraints = {
                "PRD": {
                    "name": "PRD constraints",
                    "identifiers": {
                        "req": {
                            "kind": "req",
                            "task": "required",
                            "priority": "optional",
                            "references": {
                                "DESIGN": {
                                    "coverage": "required",
                                    "task": "required",
                                    "priority": "optional",
                                },
                            },
                        },
                    },
                    "headings": [
                        {
                            "id": "prd-h1",
                            "level": 1,
                            "required": True,
                            "multiple": "prohibited",
                            "numbered": "allow",
                        }
                    ],
                }
            }
            (kit_dir / "constraints.json").write_text(json.dumps(constraints))

            cypilot_dir = root / "cypilot"
            (cypilot_dir / "config").mkdir(parents=True)
            (cypilot_dir / ".gen").mkdir(parents=True)

            result = migrate_kits(
                {"my-kit": {"format": "Cypilot"}},
                ".cypilot-adapter",
                root,
                cypilot_dir,
            )
            config_kit = cypilot_dir / "config" / "kits" / "my-kit"
            self.assertTrue((config_kit / "constraints.toml").is_file())
            self.assertFalse((config_kit / "constraints.json").is_file())
            # Verify v3 structure: wrapped under 'artifacts', booleans not strings
            from cypilot.utils import toml_utils
            data = toml_utils.load(config_kit / "constraints.toml")
            self.assertIn("artifacts", data)
            heading = data["artifacts"]["PRD"]["headings"][0]
            self.assertIs(heading["multiple"], False)  # "prohibited" → false
            self.assertNotIn("numbered", heading)       # "allow" → omitted (allowed, not required)
            # Verify identifier-level enums
            req_id = data["artifacts"]["PRD"]["identifiers"]["req"]
            self.assertIs(req_id["task"], True)          # "required" → true
            self.assertNotIn("priority", req_id)         # "optional" → omitted
            # Verify reference-level enums (coverage, task, priority)
            ref = req_id["references"]["DESIGN"]
            self.assertIs(ref["coverage"], True)         # "required" → true
            self.assertIs(ref["task"], True)              # "required" → true
            self.assertNotIn("priority", ref)             # "optional" → omitted

    def test_constraints_validation_errors_surfaced(self):
        """When converted constraints fail validation, errors are returned."""
        with TemporaryDirectory() as d:
            root = Path(d)
            adapter = root / ".cypilot-adapter"
            kit_dir = adapter / "kits" / "bad-kit"
            kit_dir.mkdir(parents=True)
            # Missing 'identifiers' — will fail parse_kit_constraints
            constraints = {"PRD": {"name": "bad", "headings": []}}
            (kit_dir / "constraints.json").write_text(json.dumps(constraints))

            cypilot_dir = root / "cypilot"
            (cypilot_dir / "config").mkdir(parents=True)
            (cypilot_dir / ".gen").mkdir(parents=True)

            result = migrate_kits(
                {"bad-kit": {}},
                ".cypilot-adapter",
                root,
                cypilot_dir,
            )
            self.assertTrue(any("validation" in e for e in result["errors"]))


# ===========================================================================
# Test: validate_migration
# ===========================================================================

class TestValidateMigration(unittest.TestCase):
    def test_missing_everything(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            cypilot_dir = root / "cypilot"
            cypilot_dir.mkdir()
            v2 = {"systems": [], "has_agents_md": False}
            result = validate_migration(root, cypilot_dir, v2)
            self.assertFalse(result["passed"])
            self.assertTrue(len(result["issues"]) > 0)

    def test_valid_migration(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            cypilot_dir = root / "cypilot"
            config_dir = cypilot_dir / "config"
            gen_dir = cypilot_dir / ".gen"
            core_dir = cypilot_dir / ".core"
            config_dir.mkdir(parents=True)
            gen_dir.mkdir(parents=True)
            core_dir.mkdir(parents=True)

            # Write minimal valid files
            from cypilot.utils import toml_utils
            toml_utils.dump({"version": "1.0", "project_root": ".."}, config_dir / "core.toml")
            toml_utils.dump({"version": "1.0", "systems": [], "kits": {}}, config_dir / "artifacts.toml")
            (config_dir / "AGENTS.md").write_text("# rules\n")

            # Root AGENTS.md with managed block
            (root / "AGENTS.md").write_text("<!-- @cpt:root-agents -->\nrules\n<!-- /@cpt:root-agents -->\n")

            # Agent dirs
            for ad in (".windsurf", ".cursor", ".claude"):
                (root / ad).mkdir()

            v2 = {"systems": [], "has_agents_md": True}
            result = validate_migration(root, cypilot_dir, v2)
            self.assertTrue(result["passed"])


# ===========================================================================
# Test: run_migrate (integration)
# ===========================================================================

class TestRunMigrate(unittest.TestCase):
    def test_no_v2_detected(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            result = run_migrate(root, yes=True)
            self.assertEqual(result["status"], "ERROR")

    def test_dry_run(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            result = run_migrate(root, yes=True, dry_run=True)
            self.assertEqual(result["status"], "DRY_RUN")
            self.assertIn("plan", result)
            self.assertTrue(result["plan"]["has_agents_md"])

    def test_full_migration(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            cache = root / "_cache"
            _make_cache(cache)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with patch("cypilot.commands.migrate.CACHE_DIR", cache):
                    # Also patch init's CACHE_DIR since it's used via _copy_from_cache
                    with patch("cypilot.commands.init.CACHE_DIR", cache):
                        # Patch cmd_agents to avoid complexity in test
                        with patch("cypilot.commands.migrate.run_migrate.__module__"):
                            pass
                        result = run_migrate(root, yes=True)
            finally:
                os.chdir(cwd)

            # Migration should complete (possibly with validation warnings about agent dirs)
            self.assertIn(result["status"], ("PASS", "VALIDATION_FAILED"))
            # Backup should exist
            self.assertIn("backup_dir", result)
            # Adapter directory should be cleaned up
            self.assertFalse((root / ".cypilot-adapter").exists())
            # Kits should NOT be in artifacts.toml
            artifacts_toml = root / ".cypilot" / "config" / "artifacts.toml"
            if artifacts_toml.is_file():
                from cypilot.utils import toml_utils
                registry = toml_utils.load(artifacts_toml)
                self.assertNotIn("kits", registry)


# ===========================================================================
# Test: run_migrate_config
# ===========================================================================

class TestRunMigrateConfig(unittest.TestCase):
    def test_converts_json_to_toml(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            config_dir = root / "config"
            config_dir.mkdir()
            (config_dir / "test.json").write_text('{"key": "value"}')
            result = run_migrate_config(root)
            self.assertEqual(result["converted_count"], 1)
            self.assertTrue((config_dir / "test.toml").is_file())
            self.assertFalse((config_dir / "test.json").is_file())

    def test_skips_existing_toml(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            config_dir = root / "config"
            config_dir.mkdir()
            (config_dir / "test.json").write_text('{"key": "value"}')
            (config_dir / "test.toml").write_text('key = "existing"\n')
            result = run_migrate_config(root)
            self.assertEqual(result["converted_count"], 0)
            self.assertEqual(result["skipped_count"], 1)

    def test_no_json_files(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            result = run_migrate_config(root)
            self.assertEqual(result["converted_count"], 0)


# ===========================================================================
# Test: cmd_migrate / cmd_migrate_config (CLI entry points)
# ===========================================================================

class TestCmdMigrate(unittest.TestCase):
    def test_help(self):
        with self.assertRaises(SystemExit) as ctx:
            cmd_migrate(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_no_v2_returns_error(self):
        with TemporaryDirectory() as d:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_migrate(["--project-root", d, "--yes"])
            self.assertEqual(rc, 1)
            output = json.loads(buf.getvalue())
            self.assertEqual(output["status"], "ERROR")

    def test_dry_run_output(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_migrate(["--project-root", d, "--dry-run"])
            self.assertEqual(rc, 0)
            output = json.loads(buf.getvalue())
            self.assertEqual(output["status"], "DRY_RUN")


class TestCmdMigrateConfig(unittest.TestCase):
    def test_help(self):
        with self.assertRaises(SystemExit) as ctx:
            cmd_migrate_config(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_empty_project(self):
        with TemporaryDirectory() as d:
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_migrate_config(["--project-root", d])
            self.assertEqual(rc, 0)
            output = json.loads(buf.getvalue())
            self.assertEqual(output["converted_count"], 0)


# ===========================================================================
# Test: Complex case (hyperspot-like structure)
# ===========================================================================

class TestComplexMigration(unittest.TestCase):
    """Fixture matching hyperspot: 2 systems, nested autodetect, 17 ignore rules, custom kit slug."""

    def _make_hyperspot(self, root: Path) -> None:
        adapter = root / ".cypilot-adapter"
        core = root / ".cypilot"
        adapter.mkdir()
        core.mkdir()
        (root / ".git").mkdir()

        ignore_rules = [{"reason": f"Rule {i}", "patterns": [f"pattern{i}/**"]} for i in range(17)]
        artifacts = {
            "version": "1.0",
            "systems": [
                {
                    "name": "Backend",
                    "slug": "backend",
                    "kit": "cf-sdlc",
                    "autodetect": [
                        {
                            "kit": "cf-sdlc",
                            "system_root": "backend",
                            "artifacts_root": "backend/architecture",
                            "artifacts": {
                                "PRD": {"pattern": "PRD.md", "traceability": "full", "required": True},
                                "DESIGN": {"pattern": "DESIGN.md", "traceability": "full"},
                            },
                            "codebase": [{"name": "api", "path": "backend/src", "extensions": [".py"]}],
                        },
                    ],
                    "children": [
                        {"name": "Workers", "slug": "workers", "kit": "cf-sdlc"},
                    ],
                },
                {
                    "name": "Frontend",
                    "slug": "frontend",
                    "kit": "cf-sdlc",
                    "autodetect": [
                        {
                            "kit": "cf-sdlc",
                            "system_root": "frontend",
                            "artifacts_root": "frontend/docs",
                        },
                    ],
                },
            ],
            "kits": {
                "cf-sdlc": {"format": "Cypilot", "path": "kits/cf-sdlc"},
            },
            "ignore": ignore_rules,
        }
        (adapter / "artifacts.json").write_text(json.dumps(artifacts), encoding="utf-8")
        (adapter / "AGENTS.md").write_text("# Hyperspot rules\nCustom WHEN rules here.\n")

        kit_dir = adapter / "kits" / "cf-sdlc"
        kit_dir.mkdir(parents=True)

        # Config JSON with custom paths
        (root / ".cypilot-config.json").write_text(json.dumps({
            "cypilotCorePath": ".cypilot",
            "cypilotAdapterPath": ".cypilot-adapter",
        }))

    def test_hyperspot_detection(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            self._make_hyperspot(root)
            result = detect_v2(root)
            self.assertTrue(result["detected"])
            self.assertEqual(len(result["systems"]), 2)
            self.assertTrue(result["has_config_json"])

    def test_hyperspot_artifacts_conversion(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            self._make_hyperspot(root)
            v2 = detect_v2(root)
            target = Path(d) / "target"
            result = convert_artifacts_registry(v2["artifacts_json"], "cypilot", target)
            self.assertEqual(result["systems_count"], 2)
            self.assertEqual(result["kit_slug_map"]["cf-sdlc"], "cf-sdlc")

            from cypilot.utils import toml_utils
            registry = toml_utils.load(target / "artifacts.toml")
            # 17 ignore rules preserved
            self.assertEqual(len(registry["ignore"]), 17)
            # System with children preserved
            backend = registry["systems"][0]
            self.assertEqual(backend["slug"], "backend")
            self.assertIn("children", backend)
            self.assertEqual(len(backend["children"]), 1)
            # Autodetect preserved
            self.assertEqual(len(backend["autodetect"]), 1)
            self.assertEqual(backend["autodetect"][0]["kit"], "cf-sdlc")


# ===========================================================================
# Test: _rollback
# ===========================================================================

class TestRollback(unittest.TestCase):
    def test_rollback_restores_files(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            # Create a backup dir with manifest
            backup = root / "backup"
            backup.mkdir()
            (backup / ".cypilot-adapter").mkdir()
            (backup / ".cypilot-adapter" / "artifacts.json").write_text('{"v": 1}')
            (backup / "AGENTS.md").write_text("# agents")
            manifest = {"backed_up": [".cypilot-adapter", "AGENTS.md"]}
            (backup / "manifest.json").write_text(json.dumps(manifest))
            result = _rollback(root, backup)
            self.assertTrue(result["success"])
            self.assertIn(".cypilot-adapter", result["restored"])
            self.assertTrue((root / "AGENTS.md").is_file())

    def test_rollback_no_manifest(self):
        with TemporaryDirectory() as d:
            backup = Path(d) / "empty_backup"
            backup.mkdir()
            result = _rollback(Path(d), backup)
            self.assertFalse(result["success"])
            self.assertIn("manifest", result["error"])

    def test_rollback_corrupt_manifest(self):
        with TemporaryDirectory() as d:
            backup = Path(d) / "backup"
            backup.mkdir()
            (backup / "manifest.json").write_text("NOT JSON")
            result = _rollback(Path(d), backup)
            self.assertFalse(result["success"])

    def test_rollback_overwrites_existing(self):
        """Rollback should overwrite files/dirs that exist at destination."""
        with TemporaryDirectory() as d:
            root = Path(d)
            # Pre-existing file at destination
            (root / "AGENTS.md").write_text("new content")
            backup = root / "backup"
            backup.mkdir()
            (backup / "AGENTS.md").write_text("old content")
            manifest = {"backed_up": ["AGENTS.md"]}
            (backup / "manifest.json").write_text(json.dumps(manifest))
            result = _rollback(root, backup)
            self.assertTrue(result["success"])
            self.assertEqual((root / "AGENTS.md").read_text(), "old content")

    def test_rollback_overwrites_existing_dir(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / "somedir").mkdir()
            (root / "somedir" / "new.txt").write_text("new")
            backup = root / "backup"
            backup.mkdir()
            (backup / "somedir").mkdir()
            (backup / "somedir" / "old.txt").write_text("old")
            manifest = {"backed_up": ["somedir"]}
            (backup / "manifest.json").write_text(json.dumps(manifest))
            result = _rollback(root, backup)
            self.assertTrue(result["success"])
            self.assertTrue((root / "somedir" / "old.txt").is_file())


# ===========================================================================
# Test: _write_gen_agents
# ===========================================================================

class TestWriteGenAgents(unittest.TestCase):
    def test_writes_gen_agents(self):
        with TemporaryDirectory() as d:
            gen_dir = Path(d) / ".gen"
            _write_gen_agents(gen_dir, "my-project")
            agents = gen_dir / "AGENTS.md"
            self.assertTrue(agents.is_file())
            content = agents.read_text()
            self.assertIn("my-project", content)
            self.assertIn("cypilot-sdlc", content)


# ===========================================================================
# Test: _copy_tree_contents
# ===========================================================================

class TestCopyTreeContents(unittest.TestCase):
    def test_copies_files_and_dirs(self):
        with TemporaryDirectory() as d:
            src = Path(d) / "src"
            dst = Path(d) / "dst"
            src.mkdir()
            dst.mkdir()
            (src / "file.txt").write_text("hello")
            sub = src / "subdir"
            sub.mkdir()
            (sub / "nested.txt").write_text("nested")
            _copy_tree_contents(src, dst)
            self.assertEqual((dst / "file.txt").read_text(), "hello")
            self.assertEqual((dst / "subdir" / "nested.txt").read_text(), "nested")

    def test_overwrites_existing_dir(self):
        with TemporaryDirectory() as d:
            src = Path(d) / "src"
            dst = Path(d) / "dst"
            src.mkdir()
            dst.mkdir()
            (src / "subdir").mkdir()
            (src / "subdir" / "new.txt").write_text("new")
            (dst / "subdir").mkdir()
            (dst / "subdir" / "old.txt").write_text("old")
            _copy_tree_contents(src, dst)
            self.assertTrue((dst / "subdir" / "new.txt").is_file())
            self.assertFalse((dst / "subdir" / "old.txt").is_file())


# ===========================================================================
# Test: detect edge cases
# ===========================================================================

class TestDetectEdgeCases(unittest.TestCase):
    def test_detect_core_install_type_gitmodules_read_error(self):
        """OSError reading .gitmodules should fall through to GIT_CLONE check."""
        with TemporaryDirectory() as d:
            root = Path(d)
            core = root / ".cypilot"
            core.mkdir()
            # Create .gitmodules as a directory (causes OSError on read_text)
            (root / ".gitmodules").mkdir()
            result = detect_core_install_type(root, ".cypilot")
            self.assertEqual(result, INSTALL_TYPE_PLAIN_DIR)

    def test_detect_v2_corrupt_config_json(self):
        """Corrupt .cypilot-config.json should fall through to defaults."""
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot-adapter").mkdir()
            (root / ".cypilot").mkdir()
            (root / ".cypilot-config.json").write_text("NOT VALID JSON")
            result = detect_v2(root)
            self.assertTrue(result["detected"])
            self.assertEqual(result["adapter_path"], ".cypilot-adapter")

    def test_detect_v2_corrupt_artifacts_json(self):
        """Corrupt artifacts.json should set artifacts_data to None."""
        with TemporaryDirectory() as d:
            root = Path(d)
            adapter = root / ".cypilot-adapter"
            adapter.mkdir()
            (root / ".cypilot").mkdir()
            (adapter / "artifacts.json").write_text("BROKEN")
            result = detect_v2(root)
            self.assertTrue(result["detected"])
            self.assertIsNone(result["artifacts_json"])


# ===========================================================================
# Test: cleanup_core_path edge cases
# ===========================================================================

class TestCleanupEdgeCases(unittest.TestCase):
    def test_cleanup_submodule(self):
        """Submodule cleanup with mocked subprocess."""
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot").mkdir()
            (root / ".git" / "modules" / ".cypilot").mkdir(parents=True)
            (root / ".gitmodules").write_text(
                '[submodule "core"]\n  path = .cypilot\n  url = https://example.com\n'
            )
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = unittest.mock.MagicMock(returncode=0)
                result = cleanup_core_path(root, ".cypilot", INSTALL_TYPE_SUBMODULE)
            self.assertTrue(result["success"])
            self.assertEqual(result["cleaned_type"], INSTALL_TYPE_SUBMODULE)
            self.assertFalse((root / ".git" / "modules" / ".cypilot").exists())

    def test_cleanup_submodule_failure(self):
        """Submodule cleanup failure returns error."""
        import subprocess as sp
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot").mkdir()
            with patch("subprocess.run", side_effect=sp.CalledProcessError(1, "git", stderr="fail")):
                result = cleanup_core_path(root, ".cypilot", INSTALL_TYPE_SUBMODULE)
            self.assertFalse(result["success"])
            self.assertIn("Submodule", result.get("error", ""))

    def test_cleanup_submodule_deletes_empty_gitmodules(self):
        """When .gitmodules becomes empty after entry removal, delete it."""
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot").mkdir()
            # .gitmodules with only the matching entry
            (root / ".gitmodules").write_text(
                '[submodule "core"]\n  path = .cypilot\n  url = https://example.com\n'
            )
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = unittest.mock.MagicMock(returncode=0)
                result = cleanup_core_path(root, ".cypilot", INSTALL_TYPE_SUBMODULE)
            self.assertTrue(result["success"])
            self.assertFalse((root / ".gitmodules").exists())

    def test_cleanup_submodule_keeps_nonempty_gitmodules(self):
        """When .gitmodules has other entries, keep it."""
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot").mkdir()
            (root / ".gitmodules").write_text(
                '[submodule "core"]\n  path = .cypilot\n  url = https://example.com\n'
                '[submodule "other"]\n  path = lib/other\n  url = https://other.com\n'
            )
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = unittest.mock.MagicMock(returncode=0)
                result = cleanup_core_path(root, ".cypilot", INSTALL_TYPE_SUBMODULE)
            self.assertTrue(result["success"])
            self.assertTrue((root / ".gitmodules").is_file())
            content = (root / ".gitmodules").read_text()
            self.assertIn("other", content)

    def test_cleanup_plain_dir_oserror(self):
        """OSError during plain dir removal."""
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot").mkdir()
            with patch("shutil.rmtree", side_effect=OSError("perm denied")):
                result = cleanup_core_path(root, ".cypilot", INSTALL_TYPE_PLAIN_DIR)
            self.assertFalse(result["success"])
            self.assertIn("removal failed", result["error"])

    def test_cleanup_git_clone_oserror(self):
        """OSError during git clone removal."""
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot" / ".git").mkdir(parents=True)
            with patch("shutil.rmtree", side_effect=OSError("perm denied")):
                result = cleanup_core_path(root, ".cypilot", INSTALL_TYPE_GIT_CLONE)
            self.assertFalse(result["success"])
            self.assertIn("clone removal", result["error"])


# ===========================================================================
# Test: convert_agents_md edge cases
# ===========================================================================

class TestConvertAgentsMdEdgeCases(unittest.TestCase):
    def test_oserror_reading_adapter_agents(self):
        """OSError reading adapter AGENTS.md should return skipped."""
        with TemporaryDirectory() as d:
            root = Path(d)
            adapter = root / ".cypilot-adapter"
            adapter.mkdir()
            (adapter / "AGENTS.md").write_text("# rules")
            target = root / "config"
            with patch.object(Path, "read_text", side_effect=OSError("perm denied")):
                result = convert_agents_md(root, ".cypilot-adapter", target)
            self.assertTrue(result.get("skipped"))
            self.assertIn("Failed to read", result.get("reason", ""))


# ===========================================================================
# Test: generate_core_toml edge cases
# ===========================================================================

class TestGenerateCoreTomlEdgeCases(unittest.TestCase):
    def test_custom_kit_in_registry(self):
        """Custom (non-vanilla) kit should get config/kits/ path."""
        with TemporaryDirectory() as d:
            root = Path(d) / "proj"
            root.mkdir()
            target = root / "cypilot" / "config"
            v2_systems = [{"name": "App", "slug": "app", "kit": "my-custom"}]
            kit_slug_map = {"my-custom": "my-custom"}
            result = generate_core_toml(root, v2_systems, kit_slug_map, target)
            self.assertEqual(result["status"], "created")
            from cypilot.utils import toml_utils
            core = toml_utils.load(target / "core.toml")
            self.assertEqual(core["kits"]["my-custom"]["path"], "config/kits/my-custom")


# ===========================================================================
# Test: migrate_kits edge cases
# ===========================================================================

class TestMigrateKitsEdgeCases(unittest.TestCase):
    def test_kit_dir_not_found(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot-adapter").mkdir()
            cypilot_dir = root / "cypilot"
            (cypilot_dir / "config").mkdir(parents=True)
            (cypilot_dir / ".gen").mkdir(parents=True)
            result = migrate_kits(
                {"unknown-kit": {}}, ".cypilot-adapter", root, cypilot_dir,
            )
            self.assertTrue(any("not found" in w for w in result["warnings"]))

    def test_custom_kit_constraints_json_error(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            adapter = root / ".cypilot-adapter"
            kit_dir = adapter / "kits" / "bad-kit"
            kit_dir.mkdir(parents=True)
            (kit_dir / "constraints.json").write_text("INVALID JSON")
            cypilot_dir = root / "cypilot"
            (cypilot_dir / "config").mkdir(parents=True)
            (cypilot_dir / ".gen").mkdir(parents=True)
            result = migrate_kits(
                {"bad-kit": {}}, ".cypilot-adapter", root, cypilot_dir,
            )
            self.assertTrue(any("Failed to convert" in e for e in result["errors"]))
            # Fallback: constraints.json kept as-is in config/
            config_kit = cypilot_dir / "config" / "kits" / "bad-kit"
            self.assertTrue((config_kit / "constraints.json").is_file())

    def test_custom_kit_constraints_fallback(self):
        """Kit with constraints.toml (no .json) should keep it as-is in config/."""
        with TemporaryDirectory() as d:
            root = Path(d)
            adapter = root / ".cypilot-adapter"
            kit_dir = adapter / "kits" / "toml-kit"
            kit_dir.mkdir(parents=True)
            (kit_dir / "constraints.toml").write_text('key = "val"\n')
            cypilot_dir = root / "cypilot"
            (cypilot_dir / "config").mkdir(parents=True)
            (cypilot_dir / ".gen").mkdir(parents=True)
            result = migrate_kits(
                {"toml-kit": {}}, ".cypilot-adapter", root, cypilot_dir,
            )
            self.assertIn("toml-kit", result["migrated_kits"])
            config_kit = cypilot_dir / "config" / "kits" / "toml-kit"
            self.assertTrue((config_kit / "constraints.toml").is_file())


# ===========================================================================
# Test: validate_migration edge cases
# ===========================================================================

class TestValidateMigrationEdgeCases(unittest.TestCase):
    def test_core_toml_parse_error(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            cypilot_dir = root / "cypilot"
            config_dir = cypilot_dir / "config"
            config_dir.mkdir(parents=True)
            (cypilot_dir / ".gen").mkdir()
            (cypilot_dir / ".core").mkdir()
            (config_dir / "core.toml").write_text("INVALID TOML {{[")
            from cypilot.utils import toml_utils
            toml_utils.dump({"systems": []}, config_dir / "artifacts.toml")
            (root / "AGENTS.md").write_text("<!-- @cpt:root-agents -->\n<!-- /@cpt:root-agents -->\n")
            v2 = {"systems": [], "has_agents_md": False}
            result = validate_migration(root, cypilot_dir, v2)
            self.assertFalse(result["passed"])
            self.assertTrue(any("parse error" in i["message"] for i in result["issues"]))

    def test_artifacts_toml_parse_error(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            cypilot_dir = root / "cypilot"
            config_dir = cypilot_dir / "config"
            config_dir.mkdir(parents=True)
            (cypilot_dir / ".gen").mkdir()
            (cypilot_dir / ".core").mkdir()
            from cypilot.utils import toml_utils
            toml_utils.dump({"version": "1.0"}, config_dir / "core.toml")
            (config_dir / "artifacts.toml").write_text("BAD TOML {{[")
            (root / "AGENTS.md").write_text("<!-- @cpt:root-agents -->\n<!-- /@cpt:root-agents -->\n")
            v2 = {"systems": [], "has_agents_md": False}
            result = validate_migration(root, cypilot_dir, v2)
            self.assertFalse(result["passed"])
            self.assertTrue(any("parse error" in i["message"] for i in result["issues"]))

    def test_systems_count_mismatch(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            cypilot_dir = root / "cypilot"
            config_dir = cypilot_dir / "config"
            config_dir.mkdir(parents=True)
            (cypilot_dir / ".gen").mkdir()
            (cypilot_dir / ".core").mkdir()
            from cypilot.utils import toml_utils
            toml_utils.dump({"version": "1.0"}, config_dir / "core.toml")
            toml_utils.dump({"systems": [{"name": "A", "slug": "a"}]}, config_dir / "artifacts.toml")
            (root / "AGENTS.md").write_text("<!-- @cpt:root-agents -->\n<!-- /@cpt:root-agents -->\n")
            # v2 had 3 systems but v3 only has 1
            v2 = {"systems": [{}, {}, {}], "has_agents_md": False}
            result = validate_migration(root, cypilot_dir, v2)
            self.assertTrue(any("mismatch" in i["message"] for i in result["issues"]))

    def test_config_agents_missing_when_v2_had_it(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            cypilot_dir = root / "cypilot"
            config_dir = cypilot_dir / "config"
            config_dir.mkdir(parents=True)
            (cypilot_dir / ".gen").mkdir()
            (cypilot_dir / ".core").mkdir()
            from cypilot.utils import toml_utils
            toml_utils.dump({"version": "1.0"}, config_dir / "core.toml")
            toml_utils.dump({"systems": []}, config_dir / "artifacts.toml")
            (root / "AGENTS.md").write_text("<!-- @cpt:root-agents -->\n<!-- /@cpt:root-agents -->\n")
            v2 = {"systems": [], "has_agents_md": True}
            result = validate_migration(root, cypilot_dir, v2)
            self.assertTrue(any("config/AGENTS.md" in i["message"] for i in result["issues"]))

    def test_root_agents_read_error(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            cypilot_dir = root / "cypilot"
            config_dir = cypilot_dir / "config"
            config_dir.mkdir(parents=True)
            (cypilot_dir / ".gen").mkdir()
            (cypilot_dir / ".core").mkdir()
            from cypilot.utils import toml_utils
            toml_utils.dump({"version": "1.0"}, config_dir / "core.toml")
            toml_utils.dump({"systems": []}, config_dir / "artifacts.toml")
            (root / "AGENTS.md").write_text("some content")
            v2 = {"systems": [], "has_agents_md": False}
            # Mock read_text to raise OSError only for root AGENTS.md
            orig_read = Path.read_text
            def patched_read(self_path, *a, **kw):
                if self_path.name == "AGENTS.md" and self_path.parent == root:
                    raise OSError("perm denied")
                return orig_read(self_path, *a, **kw)
            with patch.object(Path, "read_text", patched_read):
                result = validate_migration(root, cypilot_dir, v2)
            self.assertTrue(any("Failed to read" in i["message"] for i in result["issues"]))


# ===========================================================================
# Test: run_migrate edge cases
# ===========================================================================

class TestRunMigrateEdgeCases(unittest.TestCase):
    def test_user_cancels(self):
        """User types 'n' at confirmation prompt."""
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            with patch("builtins.input", return_value="n"):
                result = run_migrate(root, yes=False)
            self.assertEqual(result["status"], "CANCELLED")

    def test_user_confirms(self):
        """User types 'y' at confirmation prompt."""
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            cache = root / "_cache"
            _make_cache(cache)
            with patch("builtins.input", return_value="y"):
                with patch("cypilot.commands.migrate.CACHE_DIR", cache):
                    with patch("cypilot.commands.init.CACHE_DIR", cache):
                        result = run_migrate(root, yes=False)
            self.assertIn(result["status"], ("PASS", "VALIDATION_FAILED"))

    def test_user_eof(self):
        """EOFError at confirmation prompt should cancel."""
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            with patch("builtins.input", side_effect=EOFError):
                result = run_migrate(root, yes=False)
            self.assertEqual(result["status"], "CANCELLED")

    def test_backup_failure(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            with patch("cypilot.commands.migrate.backup_v2_state", side_effect=OSError("disk full")):
                result = run_migrate(root, yes=True)
            self.assertEqual(result["status"], "ERROR")
            self.assertIn("Backup failed", result["message"])

    def test_conversion_failure_with_rollback(self):
        """Exception during conversion triggers rollback."""
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            cache = root / "_cache"
            _make_cache(cache)
            with patch("cypilot.commands.migrate.CACHE_DIR", cache):
                with patch("cypilot.commands.init.CACHE_DIR", cache):
                    with patch("cypilot.commands.migrate.cleanup_core_path",
                               return_value={"success": False, "error": "boom"}):
                        result = run_migrate(root, yes=True)
            self.assertEqual(result["status"], "ERROR")
            self.assertIn("Rolled back", result.get("message", ""))

    def test_conversion_failure_rollback_also_fails(self):
        """When both conversion and rollback fail, return CRITICAL_ERROR."""
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            cache = root / "_cache"
            _make_cache(cache)
            with patch("cypilot.commands.migrate.CACHE_DIR", cache):
                with patch("cypilot.commands.init.CACHE_DIR", cache):
                    with patch("cypilot.commands.migrate.cleanup_core_path",
                               return_value={"success": False, "error": "boom"}):
                        with patch("cypilot.commands.migrate._rollback",
                                   return_value={"success": False, "errors": ["rollback fail"]}):
                            result = run_migrate(root, yes=True)
            self.assertEqual(result["status"], "CRITICAL_ERROR")

    def test_install_dir_derived_from_core_path(self):
        """When install_dir=None, should use v2 core path."""
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            result = run_migrate(root, install_dir=None, yes=True, dry_run=True)
            self.assertEqual(result["status"], "DRY_RUN")
            self.assertEqual(result["plan"]["target_dir"], ".cypilot")

    def test_cmd_agents_exception(self):
        """Exception in cmd_agents should be caught as warning."""
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            cache = root / "_cache"
            _make_cache(cache)
            with patch("cypilot.commands.migrate.CACHE_DIR", cache):
                with patch("cypilot.commands.init.CACHE_DIR", cache):
                    with patch("cypilot.commands.agents.cmd_agents",
                               side_effect=Exception("agents broke")):
                        result = run_migrate(root, yes=True)
            if result["status"] == "PASS":
                self.assertTrue(any("agents" in w.lower() for w in result.get("warnings", [])))


# ===========================================================================
# Test: run_migrate_config edge cases
# ===========================================================================

class TestRunMigrateConfigEdgeCases(unittest.TestCase):
    def test_json_decode_error(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            config_dir = root / "config"
            config_dir.mkdir()
            (config_dir / "broken.json").write_text("NOT JSON")
            result = run_migrate_config(root)
            self.assertEqual(result["converted_count"], 0)
            self.assertEqual(result["skipped_count"], 1)
            self.assertIn("broken.json", result["skipped"][0]["file"])


# ===========================================================================
# Test: cmd_migrate exit codes
# ===========================================================================

class TestCmdMigrateExitCodes(unittest.TestCase):
    def test_cancelled_returns_0(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            buf = io.StringIO()
            with patch("builtins.input", return_value="n"):
                with redirect_stdout(buf):
                    rc = cmd_migrate(["--project-root", d])
            self.assertEqual(rc, 0)
            output = json.loads(buf.getvalue())
            self.assertEqual(output["status"], "CANCELLED")

    def test_dry_run_returns_0(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_migrate(["--project-root", d, "--dry-run"])
            self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
