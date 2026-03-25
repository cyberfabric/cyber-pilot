"""Tests for legacy install migration to manifest-driven resource bindings (WP4).

Covers migrate_legacy_kit_to_manifest() and the update_kit() integration
that auto-triggers migration when source has manifest.toml but core.toml
has no [kits.{slug}.resources].
"""
from __future__ import annotations

import os
import sys
import textwrap
import tomllib
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_manifest(kit_dir: Path, content: str) -> Path:
    """Write manifest.toml into *kit_dir* and return the path."""
    manifest_path = kit_dir / "manifest.toml"
    manifest_path.write_text(textwrap.dedent(content), encoding="utf-8")
    return manifest_path


def _make_kit_source_with_manifest(td: Path, slug: str = "testkit") -> Path:
    """Create a kit source with manifest.toml and source files."""
    kit = td / slug
    kit.mkdir(parents=True, exist_ok=True)

    (kit / "artifacts" / "ADR").mkdir(parents=True)
    (kit / "artifacts" / "ADR" / "template.md").write_text("# ADR\n", encoding="utf-8")
    (kit / "artifacts" / "ADR" / "rules.md").write_text("# Rules\n", encoding="utf-8")
    (kit / "constraints.toml").write_text('[artifacts]\n', encoding="utf-8")
    (kit / "SKILL.md").write_text(f"# Kit {slug}\n", encoding="utf-8")
    (kit / "new_resource.md").write_text("# New\n", encoding="utf-8")

    from cypilot.utils import toml_utils
    toml_utils.dump({"version": "2.0", "slug": slug}, kit / "conf.toml")

    _write_manifest(kit, """\
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
    """)
    return kit


def _setup_legacy_project(td: Path, slug: str = "testkit") -> Path:
    """Set up a project with a legacy kit install (no resources in core.toml).

    Returns the cypilot_dir (adapter).
    """
    adapter = td / "adapter"
    config = adapter / "config"
    config_kit = config / "kits" / slug
    config_kit.mkdir(parents=True)

    # Simulate legacy-installed kit files on disk
    (config_kit / "artifacts" / "ADR").mkdir(parents=True)
    (config_kit / "artifacts" / "ADR" / "template.md").write_text("# ADR\n", encoding="utf-8")
    (config_kit / "artifacts" / "ADR" / "rules.md").write_text("# Rules\n", encoding="utf-8")
    (config_kit / "constraints.toml").write_text('[artifacts]\n', encoding="utf-8")
    (config_kit / "SKILL.md").write_text(f"# Kit {slug}\n", encoding="utf-8")

    # core.toml WITHOUT resources section (legacy)
    from cypilot.utils import toml_utils
    toml_utils.dump({
        "version": "1.0",
        "project_root": "..",
        "kits": {
            slug: {
                "format": "Cypilot",
                "path": f"config/kits/{slug}",
                "version": "1.0",
            }
        },
    }, config / "core.toml")

    return adapter


# ---------------------------------------------------------------------------
# migrate_legacy_kit_to_manifest (unit tests)
# ---------------------------------------------------------------------------

class TestMigrateLegacyKitToManifest(unittest.TestCase):
    """Unit tests for migrate_legacy_kit_to_manifest()."""

    def test_existing_files_registered_silently(self):
        """Files at expected paths are registered without prompt or copy."""
        from cypilot.commands.kit import migrate_legacy_kit_to_manifest

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = _make_kit_source_with_manifest(td_path, "mykit")
            adapter = _setup_legacy_project(td_path, "mykit")

            result = migrate_legacy_kit_to_manifest(
                kit_src, adapter, "mykit", interactive=False,
            )

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["kit"], "mykit")
            # All 3 resources exist on disk → migrated silently
            self.assertEqual(result["migrated_count"], 3)
            self.assertEqual(result["new_count"], 0)
            self.assertIn("adr_artifacts", result["resource_bindings"])
            self.assertIn("constraints", result["resource_bindings"])
            self.assertIn("skill", result["resource_bindings"])

    def test_bindings_written_to_core_toml(self):
        """Resource bindings are persisted in core.toml [kits.mykit.resources]."""
        from cypilot.commands.kit import migrate_legacy_kit_to_manifest

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = _make_kit_source_with_manifest(td_path, "mykit")
            adapter = _setup_legacy_project(td_path, "mykit")

            migrate_legacy_kit_to_manifest(
                kit_src, adapter, "mykit", interactive=False,
            )

            with open(adapter / "config" / "core.toml", "rb") as f:
                data = tomllib.load(f)

            kit_entry = data["kits"]["mykit"]
            self.assertIn("resources", kit_entry)
            resources = kit_entry["resources"]
            self.assertIn("adr_artifacts", resources)
            self.assertIn("constraints", resources)
            self.assertIn("skill", resources)
            # Each binding has a "path" key
            self.assertIn("path", resources["adr_artifacts"])
            self.assertIn("path", resources["constraints"])

    def test_new_resource_copied_from_source(self):
        """A resource not on disk is copied from source and registered."""
        from cypilot.commands.kit import migrate_legacy_kit_to_manifest

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = _make_kit_source_with_manifest(td_path, "mykit")

            # Add a 4th resource to the manifest that doesn't exist in the project
            _write_manifest(kit_src, """\
                [manifest]
                version = "1.0"
                root = "{cypilot_path}/config/kits/{slug}"
                user_modifiable = false

                [[resources]]
                id = "adr_artifacts"
                source = "artifacts/ADR"
                default_path = "artifacts/ADR"
                type = "directory"
                user_modifiable = false

                [[resources]]
                id = "constraints"
                source = "constraints.toml"
                default_path = "constraints.toml"
                type = "file"
                user_modifiable = false

                [[resources]]
                id = "skill"
                source = "SKILL.md"
                default_path = "SKILL.md"
                type = "file"
                user_modifiable = false

                [[resources]]
                id = "new_resource"
                source = "new_resource.md"
                default_path = "new_resource.md"
                type = "file"
                user_modifiable = false
            """)

            adapter = _setup_legacy_project(td_path, "mykit")

            result = migrate_legacy_kit_to_manifest(
                kit_src, adapter, "mykit", interactive=False,
            )

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["migrated_count"], 3)  # existing files
            self.assertEqual(result["new_count"], 1)       # new_resource.md
            self.assertIn("new_resource", result["resource_bindings"])

            # Verify the new file was actually copied
            kit_root = adapter / "config" / "kits" / "mykit"
            self.assertTrue((kit_root / "new_resource.md").is_file())
            self.assertEqual(
                (kit_root / "new_resource.md").read_text(encoding="utf-8"),
                "# New\n",
            )

    def test_no_manifest_returns_skip(self):
        """If kit source has no manifest.toml, return SKIP."""
        from cypilot.commands.kit import migrate_legacy_kit_to_manifest

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = td_path / "nokit"
            kit_src.mkdir()

            adapter = _setup_legacy_project(td_path, "nokit")

            result = migrate_legacy_kit_to_manifest(
                kit_src, adapter, "nokit", interactive=False,
            )

            self.assertEqual(result["status"], "SKIP")

    def test_invalid_manifest_returns_fail(self):
        """If manifest validation fails, return FAIL."""
        from cypilot.commands.kit import migrate_legacy_kit_to_manifest

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = td_path / "badkit"
            kit_src.mkdir()
            # Manifest references non-existent source
            _write_manifest(kit_src, """\
                [manifest]
                version = "1.0"

                [[resources]]
                id = "missing"
                source = "does_not_exist.md"
                default_path = "out.md"
                type = "file"
            """)

            adapter = _setup_legacy_project(td_path, "badkit")

            result = migrate_legacy_kit_to_manifest(
                kit_src, adapter, "badkit", interactive=False,
            )

            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(len(result["errors"]) > 0)

    def test_reads_kit_root_from_core_toml(self):
        """Kit root is read from core.toml kits.{slug}.path."""
        from cypilot.commands.kit import migrate_legacy_kit_to_manifest

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = _make_kit_source_with_manifest(td_path, "mykit")

            adapter = td_path / "adapter"
            config = adapter / "config"
            custom_kit_dir = config / "custom_path" / "mykit"
            custom_kit_dir.mkdir(parents=True)

            # Simulate files at custom path
            (custom_kit_dir / "artifacts" / "ADR").mkdir(parents=True)
            (custom_kit_dir / "artifacts" / "ADR" / "template.md").write_text("# ADR\n", encoding="utf-8")
            (custom_kit_dir / "artifacts" / "ADR" / "rules.md").write_text("# Rules\n", encoding="utf-8")
            (custom_kit_dir / "constraints.toml").write_text('[artifacts]\n', encoding="utf-8")
            (custom_kit_dir / "SKILL.md").write_text("# Kit\n", encoding="utf-8")

            from cypilot.utils import toml_utils
            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "mykit": {
                        "format": "Cypilot",
                        "path": "config/custom_path/mykit",
                        "version": "1.0",
                    }
                },
            }, config / "core.toml")

            result = migrate_legacy_kit_to_manifest(
                kit_src, adapter, "mykit", interactive=False,
            )

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["migrated_count"], 3)
            # Paths should reference the custom location
            for binding_path in result["resource_bindings"].values():
                self.assertIn("custom_path", binding_path)

    def test_windows_absolute_registered_root_fails_on_non_windows(self):
        if os.name == "nt":
            self.skipTest("non-Windows-only absolute path regression")
        from cypilot.commands.kit import migrate_legacy_kit_to_manifest
        from cypilot.utils import toml_utils

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = _make_kit_source_with_manifest(td_path, "mykit")
            adapter = td_path / "adapter"
            config = adapter / "config"
            config.mkdir(parents=True)

            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "mykit": {
                        "format": "Cypilot",
                        "path": "C:/external-kits/mykit",
                        "version": "1.0",
                    }
                },
            }, config / "core.toml")

            result = migrate_legacy_kit_to_manifest(
                kit_src, adapter, "mykit", interactive=False,
            )

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("not accessible on this OS", result["errors"][0])

    def test_posix_absolute_registered_root_fails_on_windows(self):
        import cypilot.commands.kit as kit_module
        from cypilot.commands.kit import migrate_legacy_kit_to_manifest
        from cypilot.utils import toml_utils

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = _make_kit_source_with_manifest(td_path, "mykit")
            adapter = td_path / "adapter"
            config = adapter / "config"
            config.mkdir(parents=True)

            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "mykit": {
                        "format": "Cypilot",
                        "path": "/external-kits/mykit",
                        "version": "1.0",
                    }
                },
            }, config / "core.toml")

            with patch.object(kit_module.os, "name", "nt"):
                result = migrate_legacy_kit_to_manifest(
                    kit_src, adapter, "mykit", interactive=False,
                )

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("not accessible on this OS", result["errors"][0])

    def test_interactive_prompt_custom_relative_path(self):
        """Interactive prompt allows user to override new resource with relative path."""
        from cypilot.commands.kit import migrate_legacy_kit_to_manifest

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = _make_kit_source_with_manifest(td_path, "mykit")

            # Add a user_modifiable new resource to the manifest
            _write_manifest(kit_src, """\
                [manifest]
                version = "1.0"
                root = "{cypilot_path}/config/kits/{slug}"
                user_modifiable = false

                [[resources]]
                id = "adr_artifacts"
                source = "artifacts/ADR"
                default_path = "artifacts/ADR"
                type = "directory"
                user_modifiable = false

                [[resources]]
                id = "constraints"
                source = "constraints.toml"
                default_path = "constraints.toml"
                type = "file"
                user_modifiable = false

                [[resources]]
                id = "skill"
                source = "SKILL.md"
                default_path = "SKILL.md"
                type = "file"
                user_modifiable = false

                [[resources]]
                id = "new_resource"
                source = "new_resource.md"
                default_path = "new_resource.md"
                type = "file"
                user_modifiable = true
            """)

            adapter = _setup_legacy_project(td_path, "mykit")

            mock_stdin = MagicMock()
            mock_stdin.isatty.return_value = True
            with patch("sys.stdin", mock_stdin), \
                 patch("builtins.input", return_value="custom/placed.md"):
                result = migrate_legacy_kit_to_manifest(
                    kit_src, adapter, "mykit", interactive=True,
                )

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["new_count"], 1)
            # The user-provided relative path resolves under kit_root
            binding = result["resource_bindings"]["new_resource"]
            self.assertIn("custom/placed.md", binding)

            # Verify the file was actually copied to the custom path
            kit_root = adapter / "config" / "kits" / "mykit"
            self.assertTrue((kit_root / "custom" / "placed.md").is_file())

    def test_interactive_prompt_eof_uses_default(self):
        """EOFError during interactive prompt falls back to default path."""
        from cypilot.commands.kit import migrate_legacy_kit_to_manifest

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = _make_kit_source_with_manifest(td_path, "mykit")

            # Add a user_modifiable new resource
            _write_manifest(kit_src, """\
                [manifest]
                version = "1.0"
                root = "{cypilot_path}/config/kits/{slug}"
                user_modifiable = false

                [[resources]]
                id = "adr_artifacts"
                source = "artifacts/ADR"
                default_path = "artifacts/ADR"
                type = "directory"
                user_modifiable = false

                [[resources]]
                id = "constraints"
                source = "constraints.toml"
                default_path = "constraints.toml"
                type = "file"
                user_modifiable = false

                [[resources]]
                id = "skill"
                source = "SKILL.md"
                default_path = "SKILL.md"
                type = "file"
                user_modifiable = false

                [[resources]]
                id = "new_resource"
                source = "new_resource.md"
                default_path = "new_resource.md"
                type = "file"
                user_modifiable = true
            """)

            adapter = _setup_legacy_project(td_path, "mykit")

            mock_stdin = MagicMock()
            mock_stdin.isatty.return_value = True
            with patch("sys.stdin", mock_stdin), \
                 patch("builtins.input", side_effect=EOFError):
                result = migrate_legacy_kit_to_manifest(
                    kit_src, adapter, "mykit", interactive=True,
                )

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["new_count"], 1)
            # Falls back to default path
            kit_root = adapter / "config" / "kits" / "mykit"
            self.assertTrue((kit_root / "new_resource.md").is_file())

    def test_preserves_existing_core_toml_fields(self):
        """Migration preserves existing fields in core.toml (version, source)."""
        from cypilot.commands.kit import migrate_legacy_kit_to_manifest

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = _make_kit_source_with_manifest(td_path, "mykit")
            adapter = _setup_legacy_project(td_path, "mykit")

            # Add source field to core.toml
            from cypilot.utils import toml_utils
            config = adapter / "config"
            with open(config / "core.toml", "rb") as f:
                data = tomllib.load(f)
            data["kits"]["mykit"]["source"] = "github:org/repo"
            toml_utils.dump(data, config / "core.toml")

            migrate_legacy_kit_to_manifest(
                kit_src, adapter, "mykit", interactive=False,
            )

            with open(config / "core.toml", "rb") as f:
                data = tomllib.load(f)

            kit_entry = data["kits"]["mykit"]
            self.assertEqual(kit_entry["source"], "github:org/repo")
            self.assertEqual(kit_entry["version"], "1.0")
            self.assertIn("resources", kit_entry)


# ---------------------------------------------------------------------------
# update_kit() integration — legacy manifest migration trigger
# ---------------------------------------------------------------------------

class TestUpdateKitLegacyMigration(unittest.TestCase):
    """Tests that update_kit() auto-triggers migration when needed."""

    def test_update_triggers_migration_for_legacy_kit(self):
        """update_kit with manifest source + no resources → auto-populate bindings."""
        from cypilot.commands.kit import update_kit

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = _make_kit_source_with_manifest(td_path, "mykit")
            adapter = _setup_legacy_project(td_path, "mykit")

            update_kit(
                "mykit", kit_src, adapter,
                interactive=False, auto_approve=True, force=True,
            )

            # Check that resources were populated in core.toml
            with open(adapter / "config" / "core.toml", "rb") as f:
                data = tomllib.load(f)

            kit_entry = data["kits"]["mykit"]
            self.assertIn("resources", kit_entry)
            self.assertIn("adr_artifacts", kit_entry["resources"])
            self.assertIn("constraints", kit_entry["resources"])
            self.assertIn("skill", kit_entry["resources"])

    def test_update_skips_migration_when_resources_exist(self):
        """update_kit with existing resources → no migration triggered."""
        from cypilot.commands.kit import update_kit

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = _make_kit_source_with_manifest(td_path, "mykit")
            adapter = _setup_legacy_project(td_path, "mykit")

            # Pre-populate resources in core.toml
            from cypilot.utils import toml_utils
            config = adapter / "config"
            with open(config / "core.toml", "rb") as f:
                data = tomllib.load(f)
            data["kits"]["mykit"]["resources"] = {
                "adr_artifacts": {"path": "config/kits/mykit/artifacts/ADR"},
            }
            toml_utils.dump(data, config / "core.toml")

            update_kit(
                "mykit", kit_src, adapter,
                interactive=False, auto_approve=True, force=True,
            )

            # Resources should still only contain the original entry
            # (no overwrite by migration)
            with open(config / "core.toml", "rb") as f:
                data = tomllib.load(f)

            kit_entry = data["kits"]["mykit"]
            self.assertIn("resources", kit_entry)
            # Original binding preserved
            self.assertIn("adr_artifacts", kit_entry["resources"])

    def test_update_no_manifest_no_migration(self):
        """update_kit without manifest in source → no migration attempt."""
        from cypilot.commands.kit import update_kit

        with TemporaryDirectory() as td:
            td_path = Path(td)
            # Legacy kit source (no manifest.toml)
            kit_src = td_path / "legkit"
            kit_src.mkdir()
            (kit_src / "artifacts" / "ADR").mkdir(parents=True)
            (kit_src / "artifacts" / "ADR" / "template.md").write_text("# ADR\n", encoding="utf-8")
            (kit_src / "SKILL.md").write_text("# Kit\n", encoding="utf-8")
            (kit_src / "constraints.toml").write_text('[artifacts]\n', encoding="utf-8")
            from cypilot.utils import toml_utils
            toml_utils.dump({"version": "2.0", "slug": "legkit"}, kit_src / "conf.toml")

            adapter = _setup_legacy_project(td_path, "legkit")

            update_kit(
                "legkit", kit_src, adapter,
                interactive=False, auto_approve=True, force=True,
            )

            # No resources section should be added
            with open(adapter / "config" / "core.toml", "rb") as f:
                data = tomllib.load(f)

            kit_entry = data["kits"]["legkit"]
            self.assertNotIn("resources", kit_entry)

    def test_update_adds_new_manifest_resource_to_core_toml(self):
        """update_kit with new resource in manifest → binding added to core.toml."""
        from cypilot.commands.kit import update_kit

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = _make_kit_source_with_manifest(td_path, "mykit")
            adapter = _setup_legacy_project(td_path, "mykit")

            # Pre-populate resources in core.toml (simulating existing install)
            from cypilot.utils import toml_utils
            config = adapter / "config"
            with open(config / "core.toml", "rb") as f:
                data = tomllib.load(f)
            data["kits"]["mykit"]["resources"] = {
                "adr_artifacts": {"path": "config/kits/mykit/artifacts/ADR"},
                "constraints": {"path": "config/kits/mykit/constraints.toml"},
                "skill": {"path": "config/kits/mykit/SKILL.md"},
            }
            toml_utils.dump(data, config / "core.toml")

            # Add a NEW resource to the manifest (simulating kit version upgrade)
            _write_manifest(kit_src, """\
                [manifest]
                version = "1.0"
                root = "{cypilot_path}/config/kits/{slug}"
                user_modifiable = false

                [[resources]]
                id = "adr_artifacts"
                source = "artifacts/ADR"
                default_path = "artifacts/ADR"
                type = "directory"
                user_modifiable = false

                [[resources]]
                id = "constraints"
                source = "constraints.toml"
                default_path = "constraints.toml"
                type = "file"
                user_modifiable = false

                [[resources]]
                id = "skill"
                source = "SKILL.md"
                default_path = "SKILL.md"
                type = "file"
                user_modifiable = false

                [[resources]]
                id = "new_workflow"
                source = "new_resource.md"
                default_path = "workflows/new_workflow.md"
                type = "file"
                user_modifiable = false
            """)

            # Bump version to trigger update
            toml_utils.dump({"version": "2.1", "slug": "mykit"}, kit_src / "conf.toml")

            update_kit(
                "mykit", kit_src, adapter,
                interactive=False, auto_approve=True,
            )

            # Check that NEW resource was added to core.toml
            with open(config / "core.toml", "rb") as f:
                data = tomllib.load(f)

            kit_entry = data["kits"]["mykit"]
            self.assertIn("resources", kit_entry)
            # Existing bindings preserved
            self.assertIn("adr_artifacts", kit_entry["resources"])
            self.assertIn("constraints", kit_entry["resources"])
            self.assertIn("skill", kit_entry["resources"])
            # NEW binding added
            self.assertIn("new_workflow", kit_entry["resources"])
            self.assertIn("workflows/new_workflow.md", kit_entry["resources"]["new_workflow"]["path"])

    def test_update_manifest_migration_preserves_absolute_bindings_when_relpath_raises(self):
        import cypilot.commands.kit as kit_module
        from cypilot.commands.kit import update_kit
        from cypilot.utils import toml_utils

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = _make_kit_source_with_manifest(td_path, "mykit")
            _write_manifest(kit_src, """\
                [manifest]
                version = "1.0"
                root = "{cypilot_path}/config/kits/{slug}"
                user_modifiable = false

                [[resources]]
                id = "adr_artifacts"
                source = "artifacts/ADR"
                default_path = "artifacts/ADR"
                type = "directory"
                user_modifiable = false

                [[resources]]
                id = "constraints"
                source = "constraints.toml"
                default_path = "constraints.toml"
                type = "file"
                user_modifiable = false

                [[resources]]
                id = "skill"
                source = "SKILL.md"
                default_path = "SKILL.md"
                type = "file"
                user_modifiable = false

                [[resources]]
                id = "notes"
                source = "notes.txt"
                default_path = "notes.txt"
                type = "file"
                user_modifiable = false
            """)
            (kit_src / "notes.txt").write_text("notes\n", encoding="utf-8")

            adapter = td_path / "adapter"
            config = adapter / "config"
            external_kit_dir = (td_path / "external-kits" / "mykit").resolve()
            (external_kit_dir / "artifacts" / "ADR").mkdir(parents=True)
            (external_kit_dir / "artifacts" / "ADR" / "template.md").write_text("# ADR\n", encoding="utf-8")
            (external_kit_dir / "artifacts" / "ADR" / "rules.md").write_text("# Rules\n", encoding="utf-8")
            (external_kit_dir / "constraints.toml").write_text('[artifacts]\n', encoding="utf-8")
            (external_kit_dir / "SKILL.md").write_text("# Kit mykit\n", encoding="utf-8")
            config.mkdir(parents=True)

            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "mykit": {
                        "format": "Cypilot",
                        "path": external_kit_dir.as_posix(),
                        "version": "1.0",
                    }
                },
            }, config / "core.toml")

            original_relpath = kit_module.os.path.relpath

            def _patched_relpath(path, start):
                if os.fspath(path).startswith(external_kit_dir.as_posix()):
                    raise ValueError("path is on mount 'D:', start on mount 'C:'")
                return original_relpath(path, start)

            with patch.object(kit_module.os.path, "relpath", side_effect=_patched_relpath):
                result = update_kit(
                    "mykit", kit_src, adapter,
                    interactive=False, auto_approve=True,
                )

            self.assertNotEqual(result["version"]["status"], "failed")
            with open(config / "core.toml", "rb") as f:
                data = tomllib.load(f)
            resources = data["kits"]["mykit"]["resources"]
            self.assertEqual(data["kits"]["mykit"]["path"], external_kit_dir.as_posix())
            self.assertEqual(resources["skill"]["path"], f"{external_kit_dir.as_posix()}/SKILL.md")
            self.assertEqual(resources["constraints"]["path"], f"{external_kit_dir.as_posix()}/constraints.toml")
            self.assertEqual(resources["notes"]["path"], f"{external_kit_dir.as_posix()}/notes.txt")

    def test_manifest_update_preserves_registered_custom_kit_path(self):
        """Manifest-backed update keeps an existing custom kits.{slug}.path."""
        from cypilot.commands.kit import update_kit
        from cypilot.utils import toml_utils

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_src = _make_kit_source_with_manifest(td_path, "mykit")
            adapter = td_path / "adapter"
            config = adapter / "config"
            custom_kit_dir = adapter / "custom-kits" / "mykit"
            custom_kit_dir.mkdir(parents=True)
            (custom_kit_dir / "artifacts" / "ADR").mkdir(parents=True)
            (custom_kit_dir / "artifacts" / "ADR" / "template.md").write_text("# ADR\n", encoding="utf-8")
            (custom_kit_dir / "artifacts" / "ADR" / "rules.md").write_text("# Rules\n", encoding="utf-8")
            (custom_kit_dir / "constraints.toml").write_text('[artifacts]\n', encoding="utf-8")
            (custom_kit_dir / "SKILL.md").write_text("# Old Skill\n", encoding="utf-8")
            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "mykit": {
                        "format": "Cypilot",
                        "path": "custom-kits/mykit",
                        "version": "1.0",
                        "resources": {
                            "adr_artifacts": {"path": "custom-kits/mykit/artifacts/ADR"},
                            "constraints": {"path": "custom-kits/mykit/constraints.toml"},
                            "skill": {"path": "custom-kits/mykit/SKILL.md"},
                        },
                    }
                },
            }, config / "core.toml")

            (kit_src / "SKILL.md").write_text("# New Skill\n", encoding="utf-8")
            toml_utils.dump({"version": "2.1", "slug": "mykit"}, kit_src / "conf.toml")

            update_kit(
                "mykit", kit_src, adapter,
                interactive=False, auto_approve=True,
            )

            with open(config / "core.toml", "rb") as f:
                data = tomllib.load(f)

            kit_entry = data["kits"]["mykit"]
            self.assertEqual(kit_entry["path"], "custom-kits/mykit")
            self.assertEqual(kit_entry["version"], "2.1")
            self.assertEqual((custom_kit_dir / "SKILL.md").read_text(encoding="utf-8"), "# New Skill\n")
            self.assertFalse((adapter / "config" / "kits" / "mykit").exists())


if __name__ == "__main__":
    unittest.main()
