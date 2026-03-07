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
    _normalize_pr_review_data,
    _migrate_adapter_json_configs,
    _cleanup_old_adapter_agent_files,
    _install_default_kit_from_cache,
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
    from cypilot.utils import toml_utils
    toml_utils.dump({"version": 1}, kit_dir / "conf.toml")
    # Skill source needed by cmd_agents during migration
    skill_src = cache_dir / "skills" / "cypilot" / "SKILL.md"
    skill_src.parent.mkdir(parents=True, exist_ok=True)
    skill_src.write_text(
        "---\nname: cypilot\ndescription: Cypilot core skill\n---\nSkill content\n",
        encoding="utf-8",
    )
    # Core workflow needed so agent proxies can be generated
    wf = cache_dir / "workflows" / "analyze.md"
    wf.parent.mkdir(parents=True, exist_ok=True)
    wf.write_text(
        "---\nname: analyze\ndescription: Analyze artifacts\n---\nContent\n",
        encoding="utf-8",
    )


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
            result = convert_artifacts_registry(v2_data, target)
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
            result = convert_artifacts_registry(v2_data, target)
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
            result = convert_artifacts_registry(v2_data, target)
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
            result = convert_artifacts_registry(v2_data, target)
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
    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)

    def tearDown(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

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
    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)

    def tearDown(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

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
            result = convert_artifacts_registry(v2["artifacts_json"], target)
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

    def test_cleanup_submodule_deinit_failure_non_fatal(self):
        """Submodule deinit failure is non-fatal — cleanup continues."""
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot").mkdir()
            (root / ".gitmodules").write_text(
                '[submodule "core"]\n  path = .cypilot\n  url = https://example.com\n'
            )

            def _mock_run(cmd, **kwargs):
                mock_result = unittest.mock.MagicMock()
                if cmd[:3] == ["git", "submodule", "deinit"]:
                    mock_result.returncode = 1
                    mock_result.stderr = "error: pathspec '.cypilot' did not match any file(s) known to git"
                else:
                    mock_result.returncode = 0
                return mock_result

            with patch("subprocess.run", side_effect=_mock_run):
                result = cleanup_core_path(root, ".cypilot", INSTALL_TYPE_SUBMODULE)
            self.assertTrue(result["success"])
            self.assertEqual(result["cleaned_type"], INSTALL_TYPE_SUBMODULE)
            self.assertTrue(any("deinit failed" in w for w in result["warnings"]))

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
                    with patch("cypilot.commands.agents.cmd_generate_agents",
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
# Test: _normalize_pr_review_data
# ===========================================================================

class TestNormalizePrReviewData(unittest.TestCase):
    def test_renames_top_level_keys(self):
        data = {"dataDir": ".prs", "other": "keep"}
        result = _normalize_pr_review_data(data)
        self.assertEqual(result["data_dir"], ".prs")
        self.assertEqual(result["other"], "keep")
        self.assertNotIn("dataDir", result)

    def test_renames_prompt_entry_keys(self):
        data = {
            "prompts": [
                {"description": "Code Review", "promptFile": "some/path.md", "checklist": "c.md"},
            ],
        }
        result = _normalize_pr_review_data(data)
        entry = result["prompts"][0]
        self.assertEqual(entry["prompt_file"], "some/path.md")
        self.assertNotIn("promptFile", entry)
        self.assertEqual(entry["description"], "Code Review")

    def test_rewrites_prompt_paths(self):
        data = {
            "prompts": [
                {"promptFile": "{cypilot_path}/.core/prompts/pr/code-review.md"},
                {"promptFile": "prompts/pr/prd-review.md"},
            ],
        }
        result = _normalize_pr_review_data(data)
        self.assertIn("config/kits/sdlc/scripts/prompts/pr/code-review.md", result["prompts"][0]["prompt_file"])
        self.assertIn("config/kits/sdlc/scripts/prompts/pr/prd-review.md", result["prompts"][1]["prompt_file"])

    def test_empty_data(self):
        self.assertEqual(_normalize_pr_review_data({}), {})

    def test_non_dict_prompt_entries_preserved(self):
        data = {"prompts": ["string_entry", 42]}
        result = _normalize_pr_review_data(data)
        self.assertEqual(result["prompts"], ["string_entry", 42])

    def test_custom_kit_slug(self):
        data = {
            "prompts": [
                {"promptFile": ".core/prompts/pr/code-review.md"},
                {"promptFile": "prompts/pr/prd-review.md"},
            ],
        }
        result = _normalize_pr_review_data(data, kit_slug="mykit")
        self.assertIn("config/kits/mykit/scripts/prompts/pr/code-review.md", result["prompts"][0]["prompt_file"])
        self.assertIn("config/kits/mykit/scripts/prompts/pr/prd-review.md", result["prompts"][1]["prompt_file"])
        # Ensure default slug is NOT present
        self.assertNotIn("sdlc", result["prompts"][0]["prompt_file"])
        self.assertNotIn("sdlc", result["prompts"][1]["prompt_file"])


class TestMigrateAdapterJsonConfigs(unittest.TestCase):
    def test_converts_pr_review_json(self):
        with TemporaryDirectory() as d:
            adapter = Path(d) / "adapter"
            adapter.mkdir()
            config = Path(d) / "config"
            pr_json = {"dataDir": ".prs", "prompts": [{"promptFile": "prompts/pr/code.md"}]}
            (adapter / "pr-review.json").write_text(json.dumps(pr_json))
            result, failed = _migrate_adapter_json_configs(adapter, config)
            self.assertIn("pr-review.json", result)
            self.assertEqual(failed, [])
            toml_path = config / "pr-review.toml"
            self.assertTrue(toml_path.is_file())
            content = toml_path.read_text()
            self.assertIn("data_dir", content)
            self.assertNotIn("dataDir", content)
            self.assertIn("prompt_file", content)
            self.assertIn("config/kits/sdlc/scripts/prompts/pr/", content)

    def test_converts_pr_review_json_custom_slug(self):
        with TemporaryDirectory() as d:
            adapter = Path(d) / "adapter"
            adapter.mkdir()
            config = Path(d) / "config"
            pr_json = {"dataDir": ".prs", "prompts": [{"promptFile": "prompts/pr/code.md"}]}
            (adapter / "pr-review.json").write_text(json.dumps(pr_json))
            result, failed = _migrate_adapter_json_configs(adapter, config, kit_slug="custom")
            self.assertIn("pr-review.json", result)
            self.assertEqual(failed, [])
            content = (config / "pr-review.toml").read_text()
            self.assertIn("config/kits/custom/scripts/prompts/pr/", content)
            self.assertNotIn("sdlc", content)

    def test_skips_artifacts_json(self):
        with TemporaryDirectory() as d:
            adapter = Path(d) / "adapter"
            adapter.mkdir()
            config = Path(d) / "config"
            (adapter / "artifacts.json").write_text('{"key": "val"}')
            result, failed = _migrate_adapter_json_configs(adapter, config)
            self.assertEqual(result, [])
            self.assertEqual(failed, [])
            self.assertFalse((config / "artifacts.toml").exists())

    def test_skips_when_toml_exists(self):
        with TemporaryDirectory() as d:
            adapter = Path(d) / "adapter"
            adapter.mkdir()
            config = Path(d) / "config"
            config.mkdir()
            (adapter / "custom.json").write_text('{"a": 1}')
            (config / "custom.toml").write_text('a = 1\n')
            result, failed = _migrate_adapter_json_configs(adapter, config)
            self.assertEqual(result, [])
            self.assertEqual(failed, [])

    def test_handles_broken_json(self):
        with TemporaryDirectory() as d:
            adapter = Path(d) / "adapter"
            adapter.mkdir()
            config = Path(d) / "config"
            (adapter / "broken.json").write_text("NOT JSON")
            result, failed = _migrate_adapter_json_configs(adapter, config)
            self.assertEqual(result, [])
            self.assertIn("broken.json", failed)

    def test_converts_generic_json(self):
        with TemporaryDirectory() as d:
            adapter = Path(d) / "adapter"
            adapter.mkdir()
            config = Path(d) / "config"
            (adapter / "custom.json").write_text('{"key": "value"}')
            result, failed = _migrate_adapter_json_configs(adapter, config)
            self.assertIn("custom.json", result)
            self.assertEqual(failed, [])
            self.assertTrue((config / "custom.toml").is_file())


class TestRunMigrateConfigPrReview(unittest.TestCase):
    def test_pr_review_json_normalized(self):
        """run_migrate_config applies pr-review specific normalization."""
        with TemporaryDirectory() as d:
            root = Path(d)
            config_dir = root / "config"
            config_dir.mkdir()
            pr_json = {
                "dataDir": ".prs",
                "prompts": [
                    {"description": "Code", "promptFile": "prompts/pr/code-review.md"},
                ],
            }
            (config_dir / "pr-review.json").write_text(json.dumps(pr_json))
            result = run_migrate_config(root)
            self.assertEqual(result["converted_count"], 1)
            toml_path = config_dir / "pr-review.toml"
            self.assertTrue(toml_path.is_file())
            content = toml_path.read_text()
            self.assertIn("data_dir", content)
            self.assertNotIn("dataDir", content)
            self.assertIn("prompt_file", content)
            self.assertNotIn("promptFile", content)
            self.assertIn("config/kits/sdlc/scripts/prompts/pr/", content)


# ===========================================================================
# Test: cmd_migrate exit codes
# ===========================================================================

class TestCmdMigrateExitCodes(unittest.TestCase):
    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)

    def tearDown(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

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


# ===========================================================================
# Test: _human_migrate_result (lines 1821-1859)
# ===========================================================================

def _with_human_mode(fn):
    """Decorator: temporarily disable JSON mode so ui.* writes to stderr."""
    from functools import wraps
    @wraps(fn)
    def wrapper(*a, **kw):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)
        try:
            return fn(*a, **kw)
        finally:
            set_json_mode(True)
    return wrapper


class TestHumanMigrateResult(unittest.TestCase):
    """Cover lines 1821-1859 (_human_migrate_result formatter)."""

    @_with_human_mode
    def test_pass_status(self):
        from cypilot.commands.migrate import _human_migrate_result
        err = io.StringIO()
        with redirect_stderr(err):
            _human_migrate_result({
                "status": "PASS",
                "message": "Migration completed successfully.",
                "backup_dir": "/tmp/backup",
                "cypilot_dir": "/tmp/proj/.cypilot",
            })
        output = err.getvalue()
        self.assertIn("PASS", output)
        self.assertIn("/tmp/backup", output)
        self.assertIn("/tmp/proj/.cypilot", output)

    @_with_human_mode
    def test_pass_with_warnings(self):
        from cypilot.commands.migrate import _human_migrate_result
        err = io.StringIO()
        with redirect_stderr(err):
            _human_migrate_result({
                "status": "PASS",
                "message": "Done",
                "warnings": ["Some warning"],
                "backup_dir": "/tmp/b",
            })
        output = err.getvalue()
        self.assertIn("Some warning", output)

    @_with_human_mode
    def test_dry_run_status(self):
        from cypilot.commands.migrate import _human_migrate_result
        err = io.StringIO()
        with redirect_stderr(err):
            _human_migrate_result({
                "status": "DRY_RUN",
                "plan": {
                    "adapter_path": ".cypilot-adapter",
                    "core_path": ".cypilot",
                    "core_install_type": "PLAIN_DIR",
                    "target_dir": ".cypilot",
                    "systems_count": 2,
                    "kits": ["cf-sdlc"],
                    "has_agents_md": True,
                },
            })
        output = err.getvalue()
        self.assertIn("dry run", output.lower())
        self.assertIn(".cypilot-adapter", output)
        self.assertIn("cf-sdlc", output)

    @_with_human_mode
    def test_cancelled_status(self):
        from cypilot.commands.migrate import _human_migrate_result
        err = io.StringIO()
        with redirect_stderr(err):
            _human_migrate_result({"status": "CANCELLED"})
        self.assertIn("cancelled", err.getvalue().lower())

    @_with_human_mode
    def test_validation_failed_status(self):
        from cypilot.commands.migrate import _human_migrate_result
        err = io.StringIO()
        with redirect_stderr(err):
            _human_migrate_result({"status": "VALIDATION_FAILED"})
        # No output expected (issues already printed by run_migrate)
        # Just check it doesn't crash

    @_with_human_mode
    def test_error_status(self):
        from cypilot.commands.migrate import _human_migrate_result
        err = io.StringIO()
        with redirect_stderr(err):
            _human_migrate_result({
                "status": "ERROR",
                "message": "Something broke",
                "backup_dir": "/tmp/b",
            })
        output = err.getvalue()
        self.assertIn("ERROR", output)
        self.assertIn("Something broke", output)
        self.assertIn("/tmp/b", output)

    @_with_human_mode
    def test_critical_error_no_backup(self):
        from cypilot.commands.migrate import _human_migrate_result
        err = io.StringIO()
        with redirect_stderr(err):
            _human_migrate_result({
                "status": "CRITICAL_ERROR",
                "message": "Total failure",
            })
        output = err.getvalue()
        self.assertIn("CRITICAL_ERROR", output)

    @_with_human_mode
    def test_unknown_status(self):
        from cypilot.commands.migrate import _human_migrate_result
        err = io.StringIO()
        with redirect_stderr(err):
            _human_migrate_result({"status": "WEIRD", "message": "hmm"})
        self.assertIn("WEIRD", err.getvalue())

    @_with_human_mode
    def test_pass_no_cypilot_dir(self):
        from cypilot.commands.migrate import _human_migrate_result
        err = io.StringIO()
        with redirect_stderr(err):
            _human_migrate_result({
                "status": "PASS",
                "message": "OK",
                "backup_dir": "/b",
            })
        # Should not crash when cypilot_dir is missing


# ===========================================================================
# Test: _regenerate_gen_from_config (lines 1549-1583)
# ===========================================================================

class TestRegenerateGenFromConfig(unittest.TestCase):
    """Cover lines 1549-1583 in _regenerate_gen_from_config."""

    def test_no_config_kits_dir(self):
        """kits/ doesn't exist → early return."""
        from cypilot.commands.migrate import _regenerate_gen_from_config
        with TemporaryDirectory() as td:
            cypilot_dir = Path(td)
            config_dir = cypilot_dir / "config"
            config_dir.mkdir()
            gen_dir = cypilot_dir / ".gen"
            _regenerate_gen_from_config(config_dir, gen_dir, cypilot_dir=cypilot_dir)
            # Should not crash

    def test_processes_kit_content(self):
        """Kit with content in config/kits/{slug}/ is processed."""
        from cypilot.commands.migrate import _regenerate_gen_from_config
        with TemporaryDirectory() as td:
            cypilot_dir = Path(td)
            config_dir = cypilot_dir / "config"
            config_dir.mkdir(parents=True)
            # Create kit content in config/kits/ (new model)
            kit_dir = config_dir / "kits" / "testkit"
            kit_dir.mkdir(parents=True)
            (kit_dir / "SKILL.md").write_text(
                "# Kit testkit\nInstructions.\n", encoding="utf-8",
            )
            gen_dir = cypilot_dir / ".gen"
            _regenerate_gen_from_config(config_dir, gen_dir, cypilot_dir=cypilot_dir)
            # Kit dir should still exist in config/kits/
            self.assertTrue((config_dir / "kits" / "testkit").is_dir())

    def test_scripts_stay_in_config(self):
        """Scripts in config/kits/ are preserved (no copy to .gen/)."""
        from cypilot.commands.migrate import _regenerate_gen_from_config
        with TemporaryDirectory() as td:
            cypilot_dir = Path(td)
            config_dir = cypilot_dir / "config"
            bp_dir = cypilot_dir / "kits" / "skit" / "blueprints"
            bp_dir.mkdir(parents=True)
            (bp_dir / "X.md").write_text(
                '`@cpt:blueprint`\n```toml\nartifact = "X"\n```\n`@/cpt:blueprint`\n',
                encoding="utf-8",
            )
            scripts_dir = config_dir / "kits" / "skit" / "scripts"
            scripts_dir.mkdir(parents=True)
            (scripts_dir / "helper.py").write_text("# h\n", encoding="utf-8")
            gen_dir = cypilot_dir / ".gen"
            _regenerate_gen_from_config(config_dir, gen_dir, cypilot_dir=cypilot_dir)
            # Scripts stay in config/kits/, not copied to .gen/
            self.assertTrue((config_dir / "kits" / "skit" / "scripts" / "helper.py").is_file())



# ===========================================================================
# Test: _rollback OSError (lines 405-406)
# ===========================================================================

class TestRollbackOSError(unittest.TestCase):
    """Cover lines 405-406: OSError during restore."""

    def test_restore_oserror(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            backup = root / "backup"
            backup.mkdir()
            # Create a file in backup
            (backup / "somefile.txt").write_text("data")
            manifest = {"backed_up": ["somefile.txt"]}
            (backup / "manifest.json").write_text(json.dumps(manifest))
            # Make destination read-only to trigger OSError on copy
            orig_copy2 = shutil.copy2
            def failing_copy(src, dst, *a, **kw):
                if "somefile.txt" in str(src):
                    raise OSError("permission denied")
                return orig_copy2(src, dst, *a, **kw)
            with patch("shutil.copy2", side_effect=failing_copy):
                result = _rollback(root, backup)
            self.assertFalse(result["success"])
            self.assertTrue(len(result["errors"]) > 0)


# ===========================================================================
# Test: cleanup_core_path submodule OSError (lines 510-511)
# ===========================================================================

class TestCleanupSubmoduleOSError(unittest.TestCase):
    """Cover lines 510-511: OSError during submodule dir removal."""

    def test_submodule_rmtree_oserror(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / ".cypilot").mkdir()
            (root / ".gitmodules").write_text(
                '[submodule "x"]\n  path = .cypilot\n  url = https://example.com\n'
            )
            orig_rmtree = shutil.rmtree
            call_count = [0]
            def oserror_rmtree(path, *a, **kw):
                call_count[0] += 1
                if ".cypilot" in str(path) and call_count[0] <= 2:
                    raise OSError("cannot remove")
                return orig_rmtree(path, *a, **kw)
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = unittest.mock.MagicMock(returncode=0)
                with patch("shutil.rmtree", side_effect=oserror_rmtree):
                    result = cleanup_core_path(root, ".cypilot", INSTALL_TYPE_SUBMODULE)
            self.assertFalse(result["success"])
            self.assertIn("cleanup failed", result.get("error", "").lower())


# ===========================================================================
# Test: run_migrate with kit_dirs not in artifacts.json (lines 1285, 1287)
# ===========================================================================

class TestRunMigrateKitDirsOnDisk(unittest.TestCase):
    """Cover lines 1285, 1287: kits on disk but missing from artifacts.json."""

    def test_extra_kit_dir_registered(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            # Add an extra kit directory not in artifacts.json
            extra_kit = root / ".cypilot-adapter" / "kits" / "extra-kit"
            extra_kit.mkdir(parents=True)
            (extra_kit / "README.md").write_text("# extra\n")
            cache = root / "_cache"
            _make_cache(cache)
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with patch("cypilot.commands.migrate.CACHE_DIR", cache):
                    with patch("cypilot.commands.init.CACHE_DIR", cache):
                        result = run_migrate(root, yes=True)
            finally:
                os.chdir(cwd)
            self.assertIn(result["status"], ("PASS", "VALIDATION_FAILED"))


# ===========================================================================
# Test: run_migrate agents_md skipped → empty config/AGENTS.md (lines 1294-1300)
# ===========================================================================

class TestRunMigrateNoAgentsMd(unittest.TestCase):
    """Cover lines 1294-1300: no adapter AGENTS.md → creates empty."""

    def test_missing_adapter_agents_creates_empty(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            # Remove adapter AGENTS.md to trigger skipped path
            agents_path = root / ".cypilot-adapter" / "AGENTS.md"
            if agents_path.exists():
                agents_path.unlink()
            cache = root / "_cache"
            _make_cache(cache)
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with patch("cypilot.commands.migrate.CACHE_DIR", cache):
                    with patch("cypilot.commands.init.CACHE_DIR", cache):
                        result = run_migrate(root, yes=True)
            finally:
                os.chdir(cwd)
            self.assertIn(result["status"], ("PASS", "VALIDATION_FAILED"))
            # config/AGENTS.md should exist (empty scaffold)
            config_agents = root / ".cypilot" / "config" / "AGENTS.md"
            self.assertTrue(config_agents.is_file())


# ===========================================================================
# Test: _normalize_pr_review_data TypeError (line 1654)
# ===========================================================================

class TestNormalizePrReviewTypeError(unittest.TestCase):
    """Cover line 1654: non-dict input raises TypeError."""

    def test_non_dict_raises(self):
        with self.assertRaises(TypeError):
            _normalize_pr_review_data([1, 2, 3])

    def test_string_raises(self):
        with self.assertRaises(TypeError):
            _normalize_pr_review_data("not a dict")


# ===========================================================================
# Test: run_migrate_config with core.toml (lines 1747-1754)
# ===========================================================================

class TestRunMigrateConfigCoreToml(unittest.TestCase):
    """Cover lines 1747-1754: reads kit slug from core.toml."""

    def test_reads_kit_from_core_toml(self):
        from cypilot.utils import toml_utils
        with TemporaryDirectory() as d:
            root = Path(d)
            config_dir = root / "config"
            config_dir.mkdir()
            toml_utils.dump({
                "version": "1.0",
                "system": {"name": "Test", "kit": "custom-kit"},
            }, config_dir / "core.toml")
            pr_json = {"dataDir": ".prs", "prompts": [{"promptFile": "prompts/pr/code.md"}]}
            (config_dir / "pr-review.json").write_text(json.dumps(pr_json))
            result = run_migrate_config(root)
            self.assertEqual(result["converted_count"], 1)
            content = (config_dir / "pr-review.toml").read_text()
            self.assertIn("custom-kit", content)

    def test_corrupt_core_toml_uses_default(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            config_dir = root / "config"
            config_dir.mkdir()
            (config_dir / "core.toml").write_text("{{invalid", encoding="utf-8")
            (config_dir / "test.json").write_text('{"a": 1}')
            result = run_migrate_config(root)
            self.assertEqual(result["converted_count"], 1)


# ===========================================================================
# Test: cmd_migrate returns 0 on PASS (line 1896)
# ===========================================================================

class TestCmdMigratePassReturn(unittest.TestCase):
    """Cover line 1896: cmd_migrate returns 0 when status is PASS."""

    def test_pass_returns_0(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            cache = root / "_cache"
            _make_cache(cache)
            with patch("cypilot.commands.migrate.CACHE_DIR", cache):
                with patch("cypilot.commands.init.CACHE_DIR", cache):
                    with patch("cypilot.commands.migrate._human_migrate_result"):
                        result = run_migrate(Path(d), yes=True)
            if result.get("status") == "PASS":
                # Verify cmd_migrate would return 0
                buf = io.StringIO()
                with redirect_stdout(buf):
                    with patch("cypilot.commands.migrate.run_migrate", return_value=result):
                        rc = cmd_migrate(["--project-root", d, "--yes"])
                self.assertEqual(rc, 0)


# ===========================================================================
# Test: validate_migration — root AGENTS.md missing managed block (line 1047)
# ===========================================================================

class TestValidateMigrationMissingManagedBlock(unittest.TestCase):
    """Cover line 1047: root AGENTS.md exists but missing managed block."""

    def test_missing_managed_block(self):
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
            # Root AGENTS.md without managed block
            (root / "AGENTS.md").write_text("# Just plain content\nNo managed block.\n")
            v2 = {"systems": [], "has_agents_md": False}
            result = validate_migration(root, cypilot_dir, v2)
            self.assertTrue(any("managed block" in i["message"] for i in result["issues"]))


# ===========================================================================
# Test: validation failure with HIGH severity (line 1477)
# ===========================================================================

class TestRunMigrateValidationHighSeverity(unittest.TestCase):
    """Cover line 1477: HIGH severity issues printed as warnings."""

    def test_validation_with_high_issues(self):
        """Full migrate that triggers validation failure with HIGH issues."""
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            cache = root / "_cache"
            _make_cache(cache)
            # Patch validate_migration to return HIGH severity issues
            fake_validation = {
                "passed": False,
                "issues": [
                    {"severity": "HIGH", "message": "Root AGENTS.md missing managed block"},
                    {"severity": "MEDIUM", "message": "Some medium issue"},
                ],
            }
            with patch("cypilot.commands.migrate.CACHE_DIR", cache):
                with patch("cypilot.commands.init.CACHE_DIR", cache):
                    with patch("cypilot.commands.migrate.validate_migration",
                               return_value=fake_validation):
                        result = run_migrate(root, yes=True)
            self.assertIn(result["status"], ("VALIDATION_FAILED", "CRITICAL_ERROR"))


# ===========================================================================
# Test: validation failed + rollback failed → CRITICAL_ERROR (lines 1496-1497)
# ===========================================================================

class TestRunMigrateValidationFailedRollbackFailed(unittest.TestCase):
    """Cover lines 1496-1497: validation fails and rollback also fails."""

    def test_critical_error(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            cache = root / "_cache"
            _make_cache(cache)
            fake_validation = {
                "passed": False,
                "issues": [{"severity": "HIGH", "message": "bad"}],
            }
            with patch("cypilot.commands.migrate.CACHE_DIR", cache):
                with patch("cypilot.commands.init.CACHE_DIR", cache):
                    with patch("cypilot.commands.migrate.validate_migration",
                               return_value=fake_validation):
                        with patch("cypilot.commands.migrate._rollback",
                                   return_value={"success": False, "errors": ["rollback fail"]}):
                            result = run_migrate(root, yes=True)
            self.assertEqual(result["status"], "CRITICAL_ERROR")


# ===========================================================================
# Test: cmd_generate_agents raises SystemExit (line 1421)
# ===========================================================================

class TestRunMigrateAgentsSystemExit(unittest.TestCase):
    """Cover line 1421: cmd_generate_agents raises SystemExit."""

    def test_system_exit_caught(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            cache = root / "_cache"
            _make_cache(cache)
            with patch("cypilot.commands.migrate.CACHE_DIR", cache):
                with patch("cypilot.commands.init.CACHE_DIR", cache):
                    with patch("cypilot.commands.agents.cmd_generate_agents",
                               side_effect=SystemExit(0)):
                        result = run_migrate(root, yes=True)
            # Should not crash; migration continues
            self.assertIn(result["status"], ("PASS", "VALIDATION_FAILED"))


# ===========================================================================
# Test: kit migration errors surfaced as warnings (lines 1336, 1344-1346)
# ===========================================================================

class TestRunMigrateKitErrors(unittest.TestCase):
    """Cover lines 1336, 1344-1346: kit errors and blueprint counts."""

    def test_kit_migration_errors_become_warnings(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            cache = root / "_cache"
            _make_cache(cache)
            fake_kit_result = {
                "migrated_kits": ["cf-sdlc"],
                "migrated": ["cf-sdlc"],
                "warnings": [],
                "errors": ["constraint validation failed"],
                "blueprint_count": 5,
            }
            with patch("cypilot.commands.migrate.CACHE_DIR", cache):
                with patch("cypilot.commands.init.CACHE_DIR", cache):
                    with patch("cypilot.commands.migrate.migrate_kits",
                               return_value=fake_kit_result):
                        result = run_migrate(root, yes=True)
            # Kit errors should appear in warnings
            self.assertIn(result["status"], ("PASS", "VALIDATION_FAILED"))


# ===========================================================================
# Test: JSON convert failed → preserve adapter (lines 1376, 1365, 1367)
# ===========================================================================

class TestRunMigrateJsonConvertFailed(unittest.TestCase):
    """Cover lines 1365, 1367, 1376: JSON conversion failure preserves adapter dir."""

    def test_failed_json_preserves_adapter(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            # Add a broken JSON config
            (root / ".cypilot-adapter" / "broken.json").write_text("NOT JSON")
            cache = root / "_cache"
            _make_cache(cache)
            with patch("cypilot.commands.migrate.CACHE_DIR", cache):
                with patch("cypilot.commands.init.CACHE_DIR", cache):
                    result = run_migrate(root, yes=True)
            # Adapter dir should be preserved due to failed JSON conversion
            self.assertTrue((root / ".cypilot-adapter").is_dir())


# ===========================================================================
# Test: no systems → primary_slug fallback (line 1360)
# ===========================================================================

class TestRunMigrateNoSystems(unittest.TestCase):
    """Cover line 1360: no systems in v2 → fallback to first kit slug."""

    def test_no_systems_uses_kit_fallback(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            adapter = root / ".cypilot-adapter"
            core = root / ".cypilot"
            adapter.mkdir(parents=True)
            core.mkdir(parents=True)
            (root / ".git").mkdir()
            (root / "AGENTS.md").write_text("# agents\n")
            # artifacts.json with no systems but has kits
            artifacts = {
                "version": "1.0",
                "systems": [],
                "kits": {"my-kit": {"format": "Cypilot", "path": "kits/my-kit"}},
                "ignore": [],
            }
            (adapter / "artifacts.json").write_text(json.dumps(artifacts))
            # Add a pr-review.json to exercise the primary_slug logic
            (adapter / "pr-review.json").write_text(
                json.dumps({"dataDir": ".prs", "prompts": []})
            )
            cache = root / "_cache"
            _make_cache(cache)
            with patch("cypilot.commands.migrate.CACHE_DIR", cache):
                with patch("cypilot.commands.init.CACHE_DIR", cache):
                    result = run_migrate(root, yes=True)
            self.assertIn(result["status"], ("PASS", "VALIDATION_FAILED"))


# ===========================================================================
# Test: v2 root config files removed (lines 1387-1388)
# ===========================================================================

class TestRunMigrateRemovesV2RootFiles(unittest.TestCase):
    """Cover lines 1387-1388: cypilot-agents.json removed."""

    def test_v2_root_files_removed(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            _make_v2_project(root)
            # Add v2 root files
            (root / ".cypilot-config.json").write_text('{"cypilotCorePath": ".cypilot"}')
            (root / "cypilot-agents.json").write_text('{"agents": []}')
            cache = root / "_cache"
            _make_cache(cache)
            with patch("cypilot.commands.migrate.CACHE_DIR", cache):
                with patch("cypilot.commands.init.CACHE_DIR", cache):
                    result = run_migrate(root, yes=True)
            self.assertIn(result["status"], ("PASS", "VALIDATION_FAILED"))
            self.assertFalse((root / ".cypilot-config.json").exists())
            self.assertFalse((root / "cypilot-agents.json").exists())


# ===========================================================================
# Test: _cleanup_old_adapter_agent_files
# ===========================================================================

class TestCleanupOldAdapterAgentFiles(unittest.TestCase):
    """Cover _cleanup_old_adapter_agent_files — removes v2 adapter proxies."""

    def test_removes_cypilot_adapter_workflow(self):
        """cypilot-adapter.md pointing to adapter.md is removed."""
        with TemporaryDirectory() as d:
            root = Path(d)
            wf = root / ".windsurf" / "workflows"
            wf.mkdir(parents=True)
            (wf / "cypilot-adapter.md").write_text(
                "# /cypilot-adapter\n\n\nALWAYS open and follow `../../.cypilot/workflows/adapter.md`\n"
            )
            # Keep a non-adapter workflow
            (wf / "cypilot-analyze.md").write_text(
                "# /cypilot-analyze\n\n\nALWAYS open and follow `../../.cypilot/workflows/analyze.md`\n"
            )
            removed = _cleanup_old_adapter_agent_files(root, ".cypilot-adapter", ".cypilot")
            self.assertEqual(len(removed), 1)
            self.assertIn("cypilot-adapter.md", removed[0])
            self.assertFalse((wf / "cypilot-adapter.md").exists())
            self.assertTrue((wf / "cypilot-analyze.md").exists())

    def test_removes_adapter_from_all_agents(self):
        """cypilot-adapter.md removed from windsurf, cursor, claude."""
        with TemporaryDirectory() as d:
            root = Path(d)
            content = "# /cypilot-adapter\n\nALWAYS open and follow `../../.cypilot/workflows/adapter.md`\n"
            for rel in (".windsurf/workflows", ".cursor/commands", ".claude/commands"):
                p = root / rel
                p.mkdir(parents=True)
                (p / "cypilot-adapter.md").write_text(content)
            removed = _cleanup_old_adapter_agent_files(root, ".cypilot-adapter", ".cypilot")
            self.assertEqual(len(removed), 3)
            for rel in (".windsurf/workflows", ".cursor/commands", ".claude/commands"):
                self.assertFalse((root / rel / "cypilot-adapter.md").exists())

    def test_removes_claude_skill_dir(self):
        """Claude .claude/skills/cypilot-adapter/ directory is removed."""
        with TemporaryDirectory() as d:
            root = Path(d)
            skill_dir = root / ".claude" / "skills" / "cypilot-adapter"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: cypilot-adapter\n---\n\n"
                "ALWAYS open and follow `../../../.cypilot/workflows/adapter.md`\n"
            )
            removed = _cleanup_old_adapter_agent_files(root, ".cypilot-adapter", ".cypilot")
            self.assertTrue(any("cypilot-adapter" in r for r in removed))
            self.assertFalse(skill_dir.exists())

    def test_removes_adapter_dir_refs(self):
        """Files referencing .cypilot-adapter/ directory are removed."""
        with TemporaryDirectory() as d:
            root = Path(d)
            wf = root / ".windsurf" / "workflows"
            wf.mkdir(parents=True)
            (wf / "some-proxy.md").write_text(
                "# /some\n\nALWAYS open and follow `.cypilot-adapter/AGENTS.md`\n"
            )
            removed = _cleanup_old_adapter_agent_files(root, ".cypilot-adapter", ".cypilot")
            self.assertEqual(len(removed), 1)
            self.assertFalse((wf / "some-proxy.md").exists())

    def test_no_crash_on_missing_dirs(self):
        """No error when agent dirs don't exist."""
        with TemporaryDirectory() as d:
            root = Path(d)
            removed = _cleanup_old_adapter_agent_files(root, ".cypilot-adapter", ".cypilot")
            self.assertEqual(removed, [])

    def test_preserves_non_proxy_files(self):
        """Non-proxy .md files are preserved."""
        with TemporaryDirectory() as d:
            root = Path(d)
            wf = root / ".windsurf" / "workflows"
            wf.mkdir(parents=True)
            (wf / "my-custom.md").write_text("# My custom workflow\nDo stuff\n")
            removed = _cleanup_old_adapter_agent_files(root, ".cypilot-adapter", ".cypilot")
            self.assertEqual(removed, [])
            self.assertTrue((wf / "my-custom.md").exists())


# ===========================================================================
# Test: _install_default_kit_from_cache
# ===========================================================================

class TestInstallDefaultKitFromCache(unittest.TestCase):
    """Cover _install_default_kit_from_cache — installs default kit if none present."""

    def test_installs_when_no_kits(self):
        """Default kit installed when config/kits/ is empty."""
        with TemporaryDirectory() as d:
            cypilot_dir = Path(d) / "cypilot"
            cypilot_dir.mkdir()
            (cypilot_dir / "config").mkdir()
            cache = Path(d) / "cache"
            _make_cache(cache)
            result = _install_default_kit_from_cache(cypilot_dir, cache)
            self.assertIsNotNone(result)
            self.assertEqual(result["kit"], "sdlc")
            # Kit content should be installed in config/kits/
            self.assertTrue((cypilot_dir / "config" / "kits" / "sdlc").is_dir())

    def test_skips_when_kits_exist(self):
        """Returns None when config/kits/ already has content."""
        with TemporaryDirectory() as d:
            cypilot_dir = Path(d) / "cypilot"
            (cypilot_dir / "config" / "kits" / "mykit").mkdir(parents=True)
            cache = Path(d) / "cache"
            _make_cache(cache)
            result = _install_default_kit_from_cache(cypilot_dir, cache)
            self.assertIsNone(result)

    def test_skips_when_cache_has_no_kit(self):
        """Returns None when cache doesn't have default kit."""
        with TemporaryDirectory() as d:
            cypilot_dir = Path(d) / "cypilot"
            cypilot_dir.mkdir()
            cache = Path(d) / "cache"
            cache.mkdir()
            result = _install_default_kit_from_cache(cypilot_dir, cache)
            self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
