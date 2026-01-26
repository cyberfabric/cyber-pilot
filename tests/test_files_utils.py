"""
Test files utility functions.

Tests load_text, find_adapter_directory and related file operations.
"""

import unittest
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "fdd" / "scripts"))

from fdd.utils.files import load_text, find_adapter_directory
from fdd.utils.files import (
    cfg_get_str,
    detect_requirements,
    fdd_root_from_project_config,
    load_adapter_config,
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
            
            adapter_dir = root / ".adapter"
            adapter_dir.mkdir()
            
            # Create AGENTS.md with adapter markers
            (adapter_dir / "AGENTS.md").write_text("# FDD Adapter: Test\n\nThis is an FDD adapter for testing.")
            
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
            (root / ".fdd-config.json").write_text('{"fddAdapterPath": "cfg-adapter"}', encoding="utf-8")
            adapter_dir = root / "cfg-adapter"
            adapter_dir.mkdir()
            (adapter_dir / "AGENTS.md").write_text("# FDD Adapter: X\n", encoding="utf-8")

            result = find_adapter_directory(root)
            self.assertIsNotNone(result)
            self.assertEqual(result.resolve(), adapter_dir.resolve())

    def test_find_adapter_config_path_invalid_no_fallback(self):
        """When config exists but path invalid, find_adapter_directory must return None (no recursive fallback)."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".fdd-config.json").write_text('{"fddAdapterPath": "missing"}', encoding="utf-8")

            # A valid adapter exists elsewhere, but must NOT be used.
            adapter_dir = root / ".adapter"
            adapter_dir.mkdir()
            (adapter_dir / "AGENTS.md").write_text("# FDD Adapter: X\n", encoding="utf-8")
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

    def test_find_adapter_extends_matches_fdd_root(self):
        """Cover is_adapter_directory Extends path validation with provided fdd_root."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            fdd_root = root / "FDD"
            fdd_root.mkdir()
            (fdd_root / "AGENTS.md").write_text("# Core\n", encoding="utf-8")
            (fdd_root / "requirements").mkdir()
            (fdd_root / "workflows").mkdir()

            adapter_dir = root / "FDD-Adapter"
            adapter_dir.mkdir()
            (adapter_dir / "AGENTS.md").write_text("# FDD Adapter: P\n\n**Extends**: `../FDD/AGENTS.md`\n", encoding="utf-8")

            found = find_adapter_directory(root, fdd_root=fdd_root)
            self.assertIsNotNone(found)
            self.assertEqual(found.resolve(), adapter_dir.resolve())


class TestDetectRequirements(unittest.TestCase):
    def test_detect_requirements_known_artifacts(self):
        kind, rp = detect_requirements(Path("/tmp/architecture/PRD.md"))
        self.assertEqual(kind, "prd")
        self.assertTrue(str(rp).endswith("requirements/prd-structure.md"))

        kind, rp = detect_requirements(Path("/tmp/architecture/ADR"))
        self.assertEqual(kind, "adr")

        kind, rp = detect_requirements(Path("/tmp/architecture/FEATURES.md"))
        self.assertEqual(kind, "features-manifest")

        kind, rp = detect_requirements(Path("/tmp/architecture/DESIGN.md"))
        self.assertEqual(kind, "overall-design")

        kind, rp = detect_requirements(Path("/tmp/architecture/features/feature-x/DESIGN.md"))
        self.assertEqual(kind, "feature-design")

    def test_detect_requirements_unsupported_raises(self):
        with self.assertRaises(ValueError):
            detect_requirements(Path("/tmp/README.txt"))


class TestConfigHelpers(unittest.TestCase):
    def test_cfg_get_str_variants(self):
        cfg = {"a": " x ", "b": ""}
        self.assertEqual(cfg_get_str(cfg, "b", "a"), "x")
        self.assertIsNone(cfg_get_str(cfg, "missing"))
        self.assertIsNone(cfg_get_str("not-dict", "a"))

    def test_load_project_config_invalid_json_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".fdd-config.json").write_text("{not json", encoding="utf-8")
            self.assertIsNone(load_project_config(root))

    def test_load_project_config_non_dict_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".fdd-config.json").write_text("[]", encoding="utf-8")
            self.assertIsNone(load_project_config(root))

    def test_fdd_root_from_project_config_success(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            fdd_core = root / "FDD"
            fdd_core.mkdir()
            (fdd_core / "AGENTS.md").write_text("# Core\n", encoding="utf-8")
            (fdd_core / "requirements").mkdir()
            (fdd_core / "workflows").mkdir()

            (root / ".fdd-config.json").write_text('{"fddCorePath": "FDD"}', encoding="utf-8")

            # Run from a subdir to exercise find_project_root via cwd.
            sub = root / "src"
            sub.mkdir()
            cwd = Path.cwd()
            try:
                import os
                os.chdir(str(sub))
                found = fdd_root_from_project_config()
                self.assertIsNotNone(found)
                self.assertEqual(found.resolve(), fdd_core.resolve())
            finally:
                import os
                os.chdir(str(cwd))

    def test_fdd_root_from_project_config_missing_key_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".fdd-config.json").write_text("{}", encoding="utf-8")
            sub = root / "src"
            sub.mkdir()
            cwd = Path.cwd()
            try:
                import os
                os.chdir(str(sub))
                self.assertIsNone(fdd_root_from_project_config())
            finally:
                import os
                os.chdir(str(cwd))

    def test_fdd_root_from_project_config_invalid_core_dir_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".fdd-config.json").write_text('{"fddCorePath": "MissingFDD"}', encoding="utf-8")
            cwd = Path.cwd()
            try:
                import os
                os.chdir(str(root))
                self.assertIsNone(fdd_root_from_project_config())
            finally:
                import os
                os.chdir(str(cwd))


class TestLoadAdapterConfig(unittest.TestCase):
    def test_load_adapter_config_reads_project_and_specs(self):
        with TemporaryDirectory() as tmpdir:
            ad = Path(tmpdir) / "adapter"
            ad.mkdir()
            (ad / "AGENTS.md").write_text("# FDD Adapter: MyProj\n", encoding="utf-8")
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
            (ad / "AGENTS.md").write_text("# FDD Adapter: MyProj\n", encoding="utf-8")
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
            
            adapter_dir = root / ".fdd-adapter"
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


if __name__ == "__main__":
    unittest.main()
