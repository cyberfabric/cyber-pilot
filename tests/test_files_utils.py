"""
Test files utility functions.

Tests load_text, find_adapter_directory and related file operations.
"""

import unittest
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.utils.files import load_text, find_adapter_directory
from cypilot.utils.files import (
    cfg_get_str,
    cypilot_root_from_project_config,
    iter_registry_entries,
    load_adapter_config,
    load_artifacts_registry,
    load_project_config,
)


class TestLoadText(unittest.TestCase):
    """Test load_text function."""

    def test_load_text_existing_file(self):
        """Test loading text from existing file."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text("Test content\nLine 2")
            
            content, error = load_text(test_file)
            
            self.assertIsNone(error)
            self.assertEqual(content, "Test content\nLine 2")

    def test_load_text_nonexistent_file(self):
        """Test loading text from nonexistent file returns error."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "nonexistent.md"
            
            content, error = load_text(test_file)
            
            # Function returns empty string on error, not None
            self.assertEqual(content, "")
            self.assertIsNotNone(error)
            self.assertIn("not found", error.lower())

    def test_load_text_empty_file(self):
        """Test loading text from empty file."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "empty.md"
            test_file.write_text("")
            
            content, error = load_text(test_file)
            
            self.assertIsNone(error)
            self.assertEqual(content, "")

    def test_load_text_not_a_file(self):
        """Cover Not a file branch."""
        with TemporaryDirectory() as tmpdir:
            d = Path(tmpdir) / "dir"
            d.mkdir()
            content, error = load_text(d)
            self.assertEqual(content, "")
            self.assertIsNotNone(error)
            self.assertIn("Not a file", str(error))

    def test_load_text_read_exception(self):
        """Cover generic exception while reading file."""
        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "x.md"
            p.write_text("x", encoding="utf-8")

            orig = Path.read_text

            def boom(self, *args, **kwargs):
                raise RuntimeError("boom")

            try:
                Path.read_text = boom  # type: ignore
                content, error = load_text(p)
                self.assertEqual(content, "")
                self.assertIsNotNone(error)
                self.assertIn("Failed to read", str(error))
            finally:
                Path.read_text = orig  # type: ignore


class TestFindAdapterDirectory(unittest.TestCase):
    """Test find_adapter_directory function."""

    def test_find_adapter_with_agents_md(self):
        """Test finding adapter directory with AGENTS.md."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            
            # Create .git to mark as project root
            (root / ".git").mkdir()
            
            adapter_dir = root / ".cypilot-adapter"
            adapter_dir.mkdir()
            
            # Create AGENTS.md with adapter markers
            (adapter_dir / "AGENTS.md").write_text("# Cypilot Adapter: Test\n\nThis is an Cypilot adapter for testing.")
            
            # Create specs directory (required for validation)
            specs_dir = adapter_dir / "specs"
            specs_dir.mkdir()
            (specs_dir / "test.md").write_text("# Spec")
            
            result = find_adapter_directory(root)
            
            self.assertIsNotNone(result)
            self.assertEqual(result.resolve(), adapter_dir.resolve())

    def test_find_adapter_config_path_valid_wins(self):
        """When config specifies valid adapter path, it should be returned."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".cypilot-config.json").write_text('{"cypilotAdapterPath": "cfg-adapter"}', encoding="utf-8")
            adapter_dir = root / "cfg-adapter"
            adapter_dir.mkdir()
            (adapter_dir / "AGENTS.md").write_text("# Cypilot Adapter: X\n", encoding="utf-8")

            result = find_adapter_directory(root)
            self.assertIsNotNone(result)
            self.assertEqual(result.resolve(), adapter_dir.resolve())

    def test_find_adapter_config_path_invalid_no_fallback(self):
        """When config exists but path invalid, find_adapter_directory must return None (no recursive fallback)."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".cypilot-config.json").write_text('{"cypilotAdapterPath": "missing"}', encoding="utf-8")

            # A valid adapter exists elsewhere, but must NOT be used.
            adapter_dir = root / ".cypilot-adapter"
            adapter_dir.mkdir()
            (adapter_dir / "AGENTS.md").write_text("# Cypilot Adapter: X\n", encoding="utf-8")
            (adapter_dir / "specs").mkdir()

            result = find_adapter_directory(root)
            self.assertIsNone(result)

    def test_find_adapter_recursive_permission_error_returns_none(self):
        """Cover recursive search PermissionError path."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            # Monkeypatch Path.iterdir to raise PermissionError.
            orig_iterdir = Path.iterdir

            def boom(self):
                raise PermissionError("no")

            try:
                Path.iterdir = boom  # type: ignore
                result = find_adapter_directory(root)
                self.assertIsNone(result)
            finally:
                Path.iterdir = orig_iterdir  # type: ignore

    def test_find_adapter_extends_matches_cypilot_root(self):
        """Cover is_adapter_directory Extends path validation with provided cypilot_root."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            cypilot_root = root / "Cypilot"
            cypilot_root.mkdir()
            (cypilot_root / "AGENTS.md").write_text("# Core\n", encoding="utf-8")
            (cypilot_root / "requirements").mkdir()
            (cypilot_root / "workflows").mkdir()

            adapter_dir = root / ".cypilot-adapter"
            adapter_dir.mkdir()
            (adapter_dir / "AGENTS.md").write_text("# Cypilot Adapter: P\n\n**Extends**: `../Cypilot/AGENTS.md`\n", encoding="utf-8")

            found = find_adapter_directory(root, cypilot_root=cypilot_root)
            self.assertIsNotNone(found)
            self.assertEqual(found.resolve(), adapter_dir.resolve())


class TestConfigHelpers(unittest.TestCase):
    def test_cfg_get_str_variants(self):
        cfg = {"a": " x ", "b": ""}
        self.assertEqual(cfg_get_str(cfg, "b", "a"), "x")
        self.assertIsNone(cfg_get_str(cfg, "missing"))
        self.assertIsNone(cfg_get_str("not-dict", "a"))

    def test_load_project_config_invalid_json_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".cypilot-config.json").write_text("{not json", encoding="utf-8")
            self.assertIsNone(load_project_config(root))

    def test_load_project_config_non_dict_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".cypilot-config.json").write_text("[]", encoding="utf-8")
            self.assertIsNone(load_project_config(root))

    def test_cypilot_root_from_project_config_success(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            cypilot_core = root / "Cypilot"
            cypilot_core.mkdir()
            (cypilot_core / "AGENTS.md").write_text("# Core\n", encoding="utf-8")
            (cypilot_core / "requirements").mkdir()
            (cypilot_core / "workflows").mkdir()

            (root / ".cypilot-config.json").write_text('{"cypilotCorePath": "Cypilot"}', encoding="utf-8")

            # Run from a subdir to exercise find_project_root via cwd.
            sub = root / "src"
            sub.mkdir()
            cwd = Path.cwd()
            try:
                import os
                os.chdir(str(sub))
                found = cypilot_root_from_project_config()
                self.assertIsNotNone(found)
                self.assertEqual(found.resolve(), cypilot_core.resolve())
            finally:
                import os
                os.chdir(str(cwd))

    def test_cypilot_root_from_project_config_missing_key_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".cypilot-config.json").write_text("{}", encoding="utf-8")
            sub = root / "src"
            sub.mkdir()
            cwd = Path.cwd()
            try:
                import os
                os.chdir(str(sub))
                self.assertIsNone(cypilot_root_from_project_config())
            finally:
                import os
                os.chdir(str(cwd))

    def test_cypilot_root_from_project_config_invalid_core_dir_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".cypilot-config.json").write_text('{"cypilotCorePath": "MissingCypilot"}', encoding="utf-8")
            cwd = Path.cwd()
            try:
                import os
                os.chdir(str(root))
                self.assertIsNone(cypilot_root_from_project_config())
            finally:
                import os
                os.chdir(str(cwd))


class TestLoadAdapterConfig(unittest.TestCase):
    def test_load_adapter_config_reads_project_and_specs(self):
        with TemporaryDirectory() as tmpdir:
            ad = Path(tmpdir) / "adapter"
            ad.mkdir()
            (ad / "AGENTS.md").write_text("# Cypilot Adapter: MyProj\n", encoding="utf-8")
            (ad / "specs").mkdir()
            (ad / "specs" / "a.md").write_text("# A\n", encoding="utf-8")
            (ad / "specs" / "b.md").write_text("# B\n", encoding="utf-8")

            cfg = load_adapter_config(ad)
            self.assertEqual(cfg.get("project_name"), "MyProj")
            self.assertEqual(cfg.get("specs"), ["a", "b"])

    def test_load_adapter_config_without_specs_dir(self):
        with TemporaryDirectory() as tmpdir:
            ad = Path(tmpdir) / "adapter"
            ad.mkdir()
            (ad / "AGENTS.md").write_text("# Cypilot Adapter: MyProj\n", encoding="utf-8")
            cfg = load_adapter_config(ad)
            self.assertEqual(cfg.get("project_name"), "MyProj")
            self.assertEqual(cfg.get("specs"), [])

    def test_find_adapter_no_adapter(self):
        """Test when no adapter directory exists."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            
            # Create .git to mark as project root
            (root / ".git").mkdir()
            
            result = find_adapter_directory(root)
            
            self.assertIsNone(result)

    def test_find_adapter_with_specs_only(self):
        """Test finding adapter with specs/ directory only."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            
            # Create .git to mark as project root
            (root / ".git").mkdir()
            
            adapter_dir = root / ".cypilot-adapter"
            adapter_dir.mkdir()
            
            # Create AGENTS.md (required)
            (adapter_dir / "AGENTS.md").write_text("# Navigation\n\nAdapter navigation.")
            
            # Create specs directory (validates as adapter)
            specs_dir = adapter_dir / "specs"
            specs_dir.mkdir()
            (specs_dir / "api.md").write_text("# API")
            
            result = find_adapter_directory(root)
            
            self.assertIsNotNone(result)
            self.assertEqual(result.resolve(), adapter_dir.resolve())


class TestIterRegistryEntries(unittest.TestCase):
    def test_iter_registry_entries_with_artifacts_list(self):
        registry = {"artifacts": [{"path": "a.md"}, {"path": "b.md"}]}
        result = iter_registry_entries(registry)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["path"], "a.md")

    def test_iter_registry_entries_missing_artifacts_returns_empty(self):
        registry = {"systems": []}
        result = iter_registry_entries(registry)
        self.assertEqual(result, [])

    def test_iter_registry_entries_artifacts_not_list_returns_empty(self):
        registry = {"artifacts": "not-a-list"}
        result = iter_registry_entries(registry)
        self.assertEqual(result, [])

    def test_iter_registry_entries_skips_non_dict_items(self):
        registry = {"artifacts": [{"path": "a.md"}, "invalid", 123, {"path": "b.md"}]}
        result = iter_registry_entries(registry)
        self.assertEqual(len(result), 2)


class TestLoadArtifactsRegistryEdgeCases(unittest.TestCase):
    def test_load_artifacts_registry_missing_systems_and_artifacts(self):
        with TemporaryDirectory() as tmpdir:
            ad = Path(tmpdir)
            (ad / "artifacts.json").write_text('{"version": "1.0"}', encoding="utf-8")
            reg, err = load_artifacts_registry(ad)
            self.assertIsNone(reg)
            self.assertIn("missing 'systems' or 'artifacts'", err)


class TestLoadAdapterConfigExceptionHandling(unittest.TestCase):
    def test_load_adapter_config_agents_md_read_error(self):
        """Cover exception handling when reading AGENTS.md fails."""
        with TemporaryDirectory() as tmpdir:
            ad = Path(tmpdir) / "adapter"
            ad.mkdir()
            agents = ad / "AGENTS.md"
            agents.write_text("# Cypilot Adapter: Test\n", encoding="utf-8")

            orig = Path.read_text

            def boom(self, *args, **kwargs):
                if "AGENTS" in str(self):
                    raise RuntimeError("boom")
                return orig(self, *args, **kwargs)

            try:
                Path.read_text = boom  # type: ignore
                cfg = load_adapter_config(ad)
                # Should still return config without project_name
                self.assertIsInstance(cfg, dict)
                self.assertNotIn("project_name", cfg)
            finally:
                Path.read_text = orig  # type: ignore


class TestIsAdapterDirectoryContentBased(unittest.TestCase):
    def test_adapter_with_spec_in_agents_content(self):
        """Cover content-based detection (spec keyword in AGENTS.md)."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            adapter_dir = root / "my-adapter"
            adapter_dir.mkdir()
            # AGENTS.md mentions "spec" but no specs/ directory
            (adapter_dir / "AGENTS.md").write_text(
                "# Cypilot Adapter: Test\n\nSee our spec documents.\n",
                encoding="utf-8",
            )

            result = find_adapter_directory(root)
            self.assertIsNotNone(result)
            self.assertEqual(result.resolve(), adapter_dir.resolve())

    def test_adapter_max_depth_exceeded_returns_none(self):
        """Cover max_depth limit in recursive search."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            # Create deeply nested adapter (beyond default max_depth of 5)
            deep = root / "a" / "b" / "c" / "d" / "e" / "f" / "g" / "adapter"
            deep.mkdir(parents=True)
            (deep / "AGENTS.md").write_text("# Cypilot Adapter: Deep\n", encoding="utf-8")
            (deep / "specs").mkdir()

            result = find_adapter_directory(root)
            self.assertIsNone(result)


class TestCypilotRootFromProjectConfigEdgeCases(unittest.TestCase):
    def test_cypilot_root_no_project_root_returns_none(self):
        """Cover cypilot_root_from_project_config returning None when no project root."""
        with TemporaryDirectory() as tmpdir:
            # No .git or .cypilot-config.json - no project root
            cwd = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)
                result = cypilot_root_from_project_config()
                self.assertIsNone(result)
            finally:
                os.chdir(str(cwd))

    def test_cypilot_root_no_config_returns_none(self):
        """Cover cypilot_root_from_project_config returning None when config missing."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()  # Project root exists but no config
            cwd = Path.cwd()
            try:
                import os
                os.chdir(str(root))
                result = cypilot_root_from_project_config()
                self.assertIsNone(result)
            finally:
                os.chdir(str(cwd))


if __name__ == "__main__":
    unittest.main()
