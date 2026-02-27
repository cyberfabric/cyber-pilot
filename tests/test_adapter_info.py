"""
Test info command.

Tests adapter discovery, config loading, and error handling.
"""
import unittest
import json
import tempfile
import shutil
import io
import sys
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr

# Add cypilot.py to path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.cli import main
from cypilot.utils.files import (
    find_project_root,
    load_project_config,
    find_cypilot_directory as find_adapter_directory,
    load_cypilot_config as load_adapter_config,
)


class TestAdapterInfoCommand(unittest.TestCase):
    """Test suite for info CLI command."""
    
    def test_adapter_info_found_with_config(self):
        """Test info when adapter exists and is configured."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Setup: Create project structure with config
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            
            # New layout: AGENTS.md TOML block
            (project_root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = ".cypilot-adapter"\n```\n',
                encoding="utf-8",
            )
            
            adapter_dir = project_root / ".cypilot-adapter"
            adapter_dir.mkdir()
            config_dir = adapter_dir / "config"
            config_dir.mkdir()
            rules_dir = config_dir / "rules"
            rules_dir.mkdir(parents=True)
            
            # Create config/AGENTS.md
            (config_dir / "AGENTS.md").write_text("""# Cypilot Adapter: TestProject

**Extends**: `../Cypilot/AGENTS.md`

**Version**: 1.0
""")
            # Create AGENTS.md at adapter root (for project_name extraction)
            (adapter_dir / "AGENTS.md").write_text("""# Cypilot Adapter: TestProject

**Extends**: `../Cypilot/AGENTS.md`
""")
            
            # Create config/core.toml so has_config is true
            (config_dir / "core.toml").write_text('version = "1.0"\n', encoding="utf-8")
            
            # Create some rule files
            (rules_dir / "tech-stack.md").write_text("# Tech Stack\n")
            (rules_dir / "domain-model.md").write_text("# Domain Model\n")

            # Create artifacts.toml in config/ (new format)
            (config_dir / "artifacts.toml").write_text(
                'version = "1.0"\nproject_root = ".."\n\n[[systems]]\nname = "Test"\nslug = "test"\nkit = "k"\n\n[[systems.artifacts]]\npath = "architecture/PRD.md"\nkind = "PRD"\ntraceability = "FULL"\n',
                encoding="utf-8",
            )
            
            # Run command
            stdout_capture = io.StringIO()
            with redirect_stdout(stdout_capture):
                exit_code = main(["info", "--root", str(project_root)])
            
            # Verify output
            output = json.loads(stdout_capture.getvalue())
            
            self.assertEqual(exit_code, 0)
            self.assertEqual(output["status"], "FOUND")
            self.assertEqual(output["project_name"], "TestProject")
            self.assertIn("domain-model", output["rules"])
            self.assertIn("tech-stack", output["rules"])
            self.assertTrue(output["has_config"])
            self.assertIn(".cypilot-adapter", output["cypilot_dir"])
            self.assertIn("artifacts_registry_path", output)
            self.assertIn("artifacts_registry", output)
            self.assertIsNone(output.get("artifacts_registry_error"))

    def test_adapter_info_expands_autodetect_systems(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            (project_root / ".git").mkdir()
            (project_root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = ".cypilot-adapter"\n```\n',
                encoding="utf-8",
            )

            adapter_dir = project_root / ".cypilot-adapter"
            adapter_dir.mkdir()
            (adapter_dir / "config").mkdir()
            (adapter_dir / "config" / "AGENTS.md").write_text("# Cypilot Adapter: TestProject\n", encoding="utf-8")
            (adapter_dir / "AGENTS.md").write_text("# Cypilot Adapter: TestProject\n\n**Extends**: `../AGENTS.md`\n", encoding="utf-8")

            # Minimal kit with constraints.toml (rules-only, no template.md)
            kit_root = adapter_dir / "kits" / "k"
            (kit_root / "artifacts" / "PRD").mkdir(parents=True)
            from _test_helpers import write_constraints_toml
            write_constraints_toml(kit_root, {"PRD": {"identifiers": {"fr": {"required": False}}}})

            # A module with autodetected PRD
            (project_root / "modules" / "m" / "docs").mkdir(parents=True)
            (project_root / "modules" / "m" / "docs" / "PRD.md").write_text("**ID**: `cpt-testproject-m-fr-x`\n", encoding="utf-8")

            (adapter_dir / "config" / "artifacts.toml").write_text(
                'version = "1.1"\n'
                'project_root = ".."\n\n'
                '[kits.k]\nformat = "Cypilot"\npath = ".cypilot-adapter/kits/k"\n\n'
                '[[systems]]\nname = "TestProject"\nslug = "testproject"\nkit = "k"\n\n'
                '[[systems.autodetect]]\nsystem_root = "{project_root}/modules/$system"\n'
                'artifacts_root = "{system_root}/docs"\n\n'
                '[systems.autodetect.artifacts.PRD]\npattern = "PRD.md"\ntraceability = "FULL"\n\n'
                '[systems.autodetect.validation]\nrequire_kind_registered_in_kit = true\n',
                encoding="utf-8",
            )

            stdout_capture = io.StringIO()
            with redirect_stdout(stdout_capture):
                exit_code = main(["info", "--root", str(project_root)])
            self.assertEqual(exit_code, 0)
            output = json.loads(stdout_capture.getvalue())
            reg = output.get("artifacts_registry")
            self.assertIsInstance(reg, dict)
            self.assertEqual(reg.get("version"), "1.1")
            self.assertIsInstance(reg.get("systems"), list)
            self.assertGreaterEqual(len(reg.get("systems", [])), 1)

            raw_rules = output.get("autodetect_registry")
            self.assertIsInstance(raw_rules, dict)
            self.assertEqual(raw_rules.get("version"), "1.1")
            self.assertIsInstance(raw_rules.get("systems"), list)
            self.assertGreaterEqual(len(raw_rules.get("systems", [])), 1)
            self.assertTrue(any((s.get("autodetect") or []) for s in (raw_rules.get("systems") or [])))

            def _iter_systems(systems):
                for s in systems or []:
                    yield s
                    yield from _iter_systems(s.get("children") or [])

            all_systems = list(_iter_systems(reg.get("systems") or []))
            self.assertTrue(all("autodetect" not in s for s in all_systems))

            all_artifacts = []
            for s in all_systems:
                all_artifacts.extend(s.get("artifacts") or [])

            self.assertTrue(any(a.get("path") == "modules/m/docs/PRD.md" for a in all_artifacts))
    
    def test_adapter_info_found_without_config(self):
        """Test info finds adapter via recursive search when no AGENTS.md TOML block."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Setup: Create project structure WITHOUT TOML block config
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            
            # Add .git to mark as project root
            (project_root / ".git").mkdir()
            
            adapter_dir = project_root / ".cypilot-adapter"
            adapter_dir.mkdir()
            (adapter_dir / "config").mkdir()
            (adapter_dir / "config" / "rules").mkdir()
            
            # Create AGENTS.md with Extends (for recursive search)
            agents_file = adapter_dir / "AGENTS.md"
            agents_file.write_text("""# Cypilot Adapter: MyProject

**Extends**: `../../Cypilot/AGENTS.md`
""")
            
            # Run command
            stdout_capture = io.StringIO()
            with redirect_stdout(stdout_capture):
                exit_code = main(["info", "--root", str(project_root)])
            
            # Verify output
            output = json.loads(stdout_capture.getvalue())
            
            self.assertEqual(exit_code, 0)
            self.assertEqual(output["status"], "FOUND")
            self.assertEqual(output["project_name"], "MyProject")
            self.assertFalse(output["has_config"])
            self.assertIn("artifacts_registry_path", output)
            self.assertIn("artifacts_registry", output)
    
    def test_adapter_info_not_found(self):
        """Test info when no adapter exists."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Setup: Create project without adapter
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            (project_root / ".git").mkdir()
            
            # Run command
            stdout_capture = io.StringIO()
            with redirect_stdout(stdout_capture):
                exit_code = main(["info", "--root", str(project_root)])
            
            # Verify output
            output = json.loads(stdout_capture.getvalue())
            
            self.assertEqual(exit_code, 1)
            self.assertEqual(output["status"], "NOT_FOUND")
            self.assertIn("hint", output)
    
    def test_adapter_info_config_error(self):
        """Test info when AGENTS.md points to non-existent adapter."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Setup: Create project with invalid adapter path
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            
            # AGENTS.md TOML block points to non-existent adapter dir
            (project_root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "invalid-path"\n```\n',
                encoding="utf-8",
            )
            
            # Run command
            stdout_capture = io.StringIO()
            with redirect_stdout(stdout_capture):
                exit_code = main(["info", "--root", str(project_root)])
            
            # Verify output
            output = json.loads(stdout_capture.getvalue())
            
            self.assertEqual(exit_code, 1)
            self.assertEqual(output["status"], "NOT_FOUND")
    
    def test_adapter_info_no_project_root(self):
        """Test info when not in a project (no .git or config)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Setup: Create empty directory (not a project)
            empty_dir = Path(tmp_dir) / "not-a-project"
            empty_dir.mkdir()
            
            # Run command
            stdout_capture = io.StringIO()
            with redirect_stdout(stdout_capture):
                exit_code = main(["info", "--root", str(empty_dir)])
            
            # Verify output
            output = json.loads(stdout_capture.getvalue())
            
            self.assertEqual(exit_code, 1)
            self.assertEqual(output["status"], "NOT_FOUND")
            self.assertIn("No project root found", output["message"])
    
    def test_adapter_info_with_cypilot_root_exclusion(self):
        """Test info excludes Cypilot core directory when cypilot-root provided."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Setup: Create nested structure with both Cypilot and adapter
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            (project_root / ".git").mkdir()
            
            # Create Cypilot core directory (should be excluded)
            cypilot_core = project_root / "Cypilot"
            cypilot_core.mkdir()
            (cypilot_core / "AGENTS.md").write_text("# Cypilot Core\n")
            (cypilot_core / "requirements").mkdir()
            (cypilot_core / "workflows").mkdir()
            
            # Create real adapter (discoverable via recursive search)
            adapter_dir = project_root / ".cypilot-adapter"
            adapter_dir.mkdir()
            (adapter_dir / "config").mkdir()
            (adapter_dir / "config" / "rules").mkdir()
            agents_file = adapter_dir / "AGENTS.md"
            agents_file.write_text("""# Cypilot Adapter: RealProject

**Extends**: `../Cypilot/AGENTS.md`
""")
            
            # Run command with cypilot-root
            stdout_capture = io.StringIO()
            with redirect_stdout(stdout_capture):
                exit_code = main([
                    "info",
                    "--root", str(project_root),
                    "--cypilot-root", str(cypilot_core)
                ])
            
            # Verify it found the adapter, not Cypilot core
            output = json.loads(stdout_capture.getvalue())
            
            self.assertEqual(exit_code, 0)
            self.assertEqual(output["status"], "FOUND")
            self.assertEqual(output["project_name"], "RealProject")
            self.assertIn(".cypilot-adapter", output["cypilot_dir"])
            self.assertNotIn("Cypilot", output["cypilot_dir"])


class TestAdapterHelperFunctions(unittest.TestCase):
    """Test suite for adapter discovery helper functions."""
    
    def test_find_project_root_with_agents_md(self):
        """Test find_project_root locates AGENTS.md with @cpt:root-agents marker."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            (project_root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "adapter"\n```\n',
                encoding="utf-8",
            )
            
            subdir = project_root / "src" / "lib"
            subdir.mkdir(parents=True)
            
            found = find_project_root(subdir)
            self.assertEqual(found.resolve() if found else None, project_root.resolve())
    
    def test_find_project_root_with_git(self):
        """Test find_project_root locates .git directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            (project_root / ".git").mkdir()
            
            subdir = project_root / "src"
            subdir.mkdir()
            
            found = find_project_root(subdir)
            self.assertEqual(found.resolve() if found else None, project_root.resolve())
    
    def test_find_project_root_not_found(self):
        """Test find_project_root returns None when no markers found."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            empty_dir = Path(tmp_dir) / "empty"
            empty_dir.mkdir()
            
            found = find_project_root(empty_dir)
            self.assertIsNone(found)
    
    def test_load_project_config_valid(self):
        """Test load_project_config with valid TOML."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            
            # New layout: AGENTS.md TOML block + config/core.toml
            (project_root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "adapter"\n```\n',
                encoding="utf-8",
            )
            adapter = project_root / "adapter" / "config"
            adapter.mkdir(parents=True)
            (adapter / "core.toml").write_text(
                'version = "1.0"\nother = "value"\n',
                encoding="utf-8",
            )
            
            config = load_project_config(project_root)
            self.assertIsNotNone(config)
            self.assertEqual(config["version"], "1.0")
            self.assertEqual(config["other"], "value")
    
    def test_load_project_config_missing(self):
        """Test load_project_config returns None when file missing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            
            config = load_project_config(project_root)
            self.assertIsNone(config)
    
    def test_load_project_config_invalid_json(self):
        """Test load_project_config handles invalid JSON."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            
            config_file = project_root / ".cypilot-config.json"
            config_file.write_text("{ invalid json }")
            
            config = load_project_config(project_root)
            self.assertIsNone(config)
    
    def test_find_adapter_directory_with_config(self):
        """Test find_adapter_directory uses AGENTS.md TOML block path first."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            
            # Create AGENTS.md TOML block
            (project_root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "custom-adapter"\n```\n',
                encoding="utf-8",
            )
            
            # Create adapter at configured path with config/ subdir
            adapter_dir = project_root / "custom-adapter"
            adapter_dir.mkdir()
            (adapter_dir / "config").mkdir()
            
            found = find_adapter_directory(project_root)
            self.assertEqual(found.resolve() if found else None, adapter_dir.resolve())
    
    def test_find_adapter_directory_recursive_search(self):
        """Test find_adapter_directory uses recursive search without config."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            (project_root / ".git").mkdir()
            
            # Create adapter in nested location
            adapter_dir = project_root / "docs" / ".cypilot-adapter"
            adapter_dir.mkdir(parents=True)
            (adapter_dir / "config" / "rules").mkdir(parents=True)
            agents_file = adapter_dir / "AGENTS.md"
            agents_file.write_text("""# Cypilot Adapter: Test

**Extends**: `../../Cypilot/AGENTS.md`
""")
            
            found = find_adapter_directory(project_root)
            self.assertEqual(found.resolve() if found else None, adapter_dir.resolve())
    
    def test_load_adapter_config_complete(self):
        """Test load_adapter_config extracts all metadata."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            adapter_dir = Path(tmp_dir) / "adapter"
            adapter_dir.mkdir()
            
            # Create AGENTS.md
            agents_file = adapter_dir / "AGENTS.md"
            agents_file.write_text("""# Cypilot Adapter: MyProject

**Extends**: `../Cypilot/AGENTS.md`
**Version**: 2.0
""")
            
            # Create rules
            rules_dir = adapter_dir / "config" / "rules"
            rules_dir.mkdir(parents=True)
            (rules_dir / "tech-stack.md").write_text("# Tech Stack")
            (rules_dir / "api-contracts.md").write_text("# API Contracts")
            
            config = load_adapter_config(adapter_dir)
            
            self.assertEqual(config["project_name"], "MyProject")
            self.assertIn("tech-stack", config["rules"])
            self.assertIn("api-contracts", config["rules"])
            self.assertEqual(len(config["rules"]), 2)


if __name__ == "__main__":
    unittest.main()
