"""
Tests for the tomllib migration in this PR.

The PR removes the ``_tomllib_compat`` compatibility shim and replaces all
``from ..utils._tomllib_compat import tomllib`` imports with direct
``import tomllib`` (Python 3.11+ stdlib).

Key changes under test:
- ``_tomllib_compat`` module is deleted (no longer importable)
- ``whatsnew.read_whatsnew()`` now has a graceful ``ModuleNotFoundError``
  fallback that returns ``{}`` instead of crashing
- ``adapter_info._read_kit_conf()`` uses inline ``import tomllib``
- ``init._read_existing_install()`` uses inline ``import tomllib``
- ``toml_utils`` uses direct stdlib ``import tomllib`` (no regression)
- All other modules that previously used the compat shim still work correctly
"""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_toml_file(path: Path, content: str) -> None:
    """Write raw TOML text to *path* for use in tests."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# _tomllib_compat removal
# ---------------------------------------------------------------------------

class TestTomllibCompatModuleRemoved(unittest.TestCase):
    """Verify that ``_tomllib_compat`` is no longer present or importable."""

    def test_compat_module_file_does_not_exist(self):
        """The _tomllib_compat.py source file must not be present in the skills tree."""
        repo_root = Path(__file__).resolve().parents[1]
        compat_paths = list(repo_root.rglob("_tomllib_compat.py"))
        self.assertEqual(
            compat_paths,
            [],
            f"_tomllib_compat.py still exists at: {compat_paths}",
        )

    def test_import_tomllib_compat_raises_import_error(self):
        """Importing cypilot.utils._tomllib_compat must raise ImportError/ModuleNotFoundError."""
        with self.assertRaises((ImportError, ModuleNotFoundError)):
            import cypilot.utils._tomllib_compat  # noqa: F401

    def test_no_source_file_imports_tomllib_compat(self):
        """No Python source file under skills/ should import from _tomllib_compat."""
        repo_root = Path(__file__).resolve().parents[1]
        skills_root = repo_root / "skills" / "cypilot" / "scripts"
        offenders = []
        for py_file in skills_root.rglob("*.py"):
            text = py_file.read_text(encoding="utf-8", errors="replace")
            if "_tomllib_compat" in text:
                offenders.append(str(py_file))
        self.assertEqual(
            offenders,
            [],
            f"These files still reference _tomllib_compat: {offenders}",
        )


# ---------------------------------------------------------------------------
# whatsnew.read_whatsnew() – graceful ModuleNotFoundError
# ---------------------------------------------------------------------------

class TestReadWhatsnewTomllibUnavailable(unittest.TestCase):
    """Tests for the new ModuleNotFoundError guard in read_whatsnew()."""

    def test_returns_empty_when_tomllib_unavailable(self):
        """read_whatsnew() must return {} gracefully when tomllib is not available."""
        from cypilot.utils.whatsnew import read_whatsnew

        with TemporaryDirectory() as td:
            path = Path(td) / "whatsnew.toml"
            _write_toml_file(
                path,
                '[whatsnew."1.0.0"]\nsummary = "Initial"\ndetails = ""\n',
            )
            # Setting sys.modules['tomllib'] to None makes 'import tomllib'
            # raise ModuleNotFoundError (the sentinel value blocks the import).
            with patch.dict(sys.modules, {"tomllib": None}):
                result = read_whatsnew(path)

        self.assertEqual(result, {})

    def test_returns_empty_when_tomllib_unavailable_for_nonexistent_file(self):
        """read_whatsnew() with unavailable tomllib still returns {} for missing file."""
        from cypilot.utils.whatsnew import read_whatsnew

        missing = Path("/nonexistent_xyz/whatsnew.toml")
        with patch.dict(sys.modules, {"tomllib": None}):
            result = read_whatsnew(missing)

        self.assertEqual(result, {})

    def test_returns_data_when_tomllib_available(self):
        """read_whatsnew() works normally when tomllib is available (regression guard)."""
        from cypilot.utils.whatsnew import read_whatsnew

        with TemporaryDirectory() as td:
            path = Path(td) / "whatsnew.toml"
            _write_toml_file(
                path,
                '[whatsnew."2.0.0"]\nsummary = "Major"\ndetails = "Breaking change"\n',
            )
            result = read_whatsnew(path)

        self.assertIn("2.0.0", result)
        self.assertEqual(result["2.0.0"]["summary"], "Major")
        self.assertEqual(result["2.0.0"]["details"], "Breaking change")

    def test_missing_file_always_returns_empty(self):
        """read_whatsnew() returns {} for a missing file regardless of tomllib status."""
        from cypilot.utils.whatsnew import read_whatsnew

        result = read_whatsnew(Path("/absolutely/nonexistent/path/whatsnew.toml"))
        self.assertEqual(result, {})

    def test_corrupt_toml_returns_empty(self):
        """read_whatsnew() returns {} for a corrupt TOML file (regression guard)."""
        from cypilot.utils.whatsnew import read_whatsnew

        with TemporaryDirectory() as td:
            path = Path(td) / "whatsnew.toml"
            path.write_text("{{{{not valid toml", encoding="utf-8")
            result = read_whatsnew(path)

        self.assertEqual(result, {})


# ---------------------------------------------------------------------------
# adapter_info._read_kit_conf() – inline import tomllib
# ---------------------------------------------------------------------------

class TestReadKitConf(unittest.TestCase):
    """Tests for adapter_info._read_kit_conf() which uses an inline import tomllib."""

    def test_returns_key_fields_from_valid_toml(self):
        """_read_kit_conf() extracts version, slug, and name from valid conf.toml."""
        from cypilot.commands.adapter_info import _read_kit_conf

        with TemporaryDirectory() as td:
            conf = Path(td) / "conf.toml"
            _write_toml_file(
                conf,
                'version = "2.1.0"\nslug = "sdlc"\nname = "SDLC Kit"\n'
                'extra_field = "ignored"\n',
            )
            result = _read_kit_conf(conf)

        self.assertEqual(result["version"], "2.1.0")
        self.assertEqual(result["slug"], "sdlc")
        self.assertEqual(result["name"], "SDLC Kit")
        self.assertNotIn("extra_field", result)

    def test_returns_empty_dict_for_missing_file(self):
        """_read_kit_conf() returns {} when the file does not exist (OSError path)."""
        from cypilot.commands.adapter_info import _read_kit_conf

        result = _read_kit_conf(Path("/nonexistent/conf.toml"))
        self.assertEqual(result, {})

    def test_returns_empty_dict_for_corrupt_toml(self):
        """_read_kit_conf() returns {} for invalid TOML (ValueError / TOMLDecodeError)."""
        from cypilot.commands.adapter_info import _read_kit_conf

        with TemporaryDirectory() as td:
            conf = Path(td) / "conf.toml"
            conf.write_text("{{{invalid toml", encoding="utf-8")
            result = _read_kit_conf(conf)

        self.assertEqual(result, {})

    def test_returns_only_present_fields(self):
        """_read_kit_conf() only includes keys that are present in the file."""
        from cypilot.commands.adapter_info import _read_kit_conf

        with TemporaryDirectory() as td:
            conf = Path(td) / "conf.toml"
            _write_toml_file(conf, 'version = "1.0"\n')
            result = _read_kit_conf(conf)

        self.assertIn("version", result)
        self.assertNotIn("slug", result)
        self.assertNotIn("name", result)

    def test_returns_empty_dict_for_empty_file(self):
        """_read_kit_conf() returns {} for an empty TOML file (no relevant keys)."""
        from cypilot.commands.adapter_info import _read_kit_conf

        with TemporaryDirectory() as td:
            conf = Path(td) / "conf.toml"
            conf.write_text("", encoding="utf-8")
            result = _read_kit_conf(conf)

        self.assertEqual(result, {})

    def test_all_three_fields_present(self):
        """_read_kit_conf() returns a dict with all three fields when all are set."""
        from cypilot.commands.adapter_info import _read_kit_conf

        with TemporaryDirectory() as td:
            conf = Path(td) / "conf.toml"
            _write_toml_file(conf, 'version = "3.0"\nslug = "my-kit"\nname = "My Kit"\n')
            result = _read_kit_conf(conf)

        self.assertEqual(len(result), 3)
        self.assertEqual(result, {"version": "3.0", "slug": "my-kit", "name": "My Kit"})


# ---------------------------------------------------------------------------
# init._read_existing_install() – inline import tomllib
# ---------------------------------------------------------------------------

class TestReadExistingInstall(unittest.TestCase):
    """Tests for init._read_existing_install() which uses an inline import tomllib."""

    _MARKER_START = "<!-- @cpt:root-agents -->"
    _MARKER_END = "<!-- /@cpt:root-agents -->"

    def _write_agents_file(self, project_root: Path, toml_block: str) -> None:
        content = f"{self._MARKER_START}\n```toml\n{toml_block}\n```\n{self._MARKER_END}\n"
        (project_root / "AGENTS.md").write_text(content, encoding="utf-8")

    def test_returns_path_when_cypilot_path_present(self):
        """Returns the install dir when a valid cypilot_path TOML block exists."""
        from cypilot.commands.init import _read_existing_install

        with TemporaryDirectory() as td:
            root = Path(td)
            install_dir = root / "cypilot"
            install_dir.mkdir()
            self._write_agents_file(root, 'cypilot_path = "cypilot"')
            result = _read_existing_install(root)

        self.assertEqual(result, "cypilot")

    def test_returns_none_when_no_agents_file(self):
        """Returns None when AGENTS.md does not exist."""
        from cypilot.commands.init import _read_existing_install

        with TemporaryDirectory() as td:
            root = Path(td)
            result = _read_existing_install(root)

        self.assertIsNone(result)

    def test_returns_none_when_marker_absent(self):
        """Returns None when AGENTS.md exists but lacks the managed marker."""
        from cypilot.commands.init import _read_existing_install

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "AGENTS.md").write_text("# Some content\n", encoding="utf-8")
            result = _read_existing_install(root)

        self.assertIsNone(result)

    def test_returns_none_when_install_dir_does_not_exist(self):
        """Returns None when the TOML block references a non-existent directory."""
        from cypilot.commands.init import _read_existing_install

        with TemporaryDirectory() as td:
            root = Path(td)
            # Write the marker but do NOT create the directory it references
            self._write_agents_file(root, 'cypilot_path = "nonexistent-dir"')
            result = _read_existing_install(root)

        self.assertIsNone(result)

    def test_returns_none_for_corrupt_toml_block(self):
        """Returns None when the TOML block inside the marker is invalid."""
        from cypilot.commands.init import _read_existing_install

        with TemporaryDirectory() as td:
            root = Path(td)
            content = (
                f"{self._MARKER_START}\n"
                "```toml\n"
                "{{{{not valid toml\n"
                "```\n"
                f"{self._MARKER_END}\n"
            )
            (root / "AGENTS.md").write_text(content, encoding="utf-8")
            result = _read_existing_install(root)

        self.assertIsNone(result)

    def test_uses_cypilot_alias_key(self):
        """Returns path when the legacy 'cypilot' key (without _path suffix) is used."""
        from cypilot.commands.init import _read_existing_install

        with TemporaryDirectory() as td:
            root = Path(td)
            install_dir = root / ".cpt"
            install_dir.mkdir()
            self._write_agents_file(root, 'cypilot = ".cpt"')
            result = _read_existing_install(root)

        self.assertEqual(result, ".cpt")


# ---------------------------------------------------------------------------
# toml_utils – no regression from direct import
# ---------------------------------------------------------------------------

class TestTomlUtilsWithDirectImport(unittest.TestCase):
    """Regression tests for toml_utils after the switch to direct stdlib tomllib."""

    def test_loads_valid_toml_string(self):
        """toml_utils.loads() correctly parses a TOML string."""
        from cypilot.utils.toml_utils import loads

        data = loads('name = "test"\nversion = "1.0"\n')
        self.assertEqual(data["name"], "test")
        self.assertEqual(data["version"], "1.0")

    def test_load_valid_toml_file(self):
        """toml_utils.load() correctly parses a TOML file."""
        from cypilot.utils.toml_utils import load

        with TemporaryDirectory() as td:
            path = Path(td) / "test.toml"
            _write_toml_file(path, 'key = "value"\nnumber = 42\n')
            data = load(path)

        self.assertEqual(data["key"], "value")
        self.assertEqual(data["number"], 42)

    def test_parse_toml_from_markdown_single_block(self):
        """parse_toml_from_markdown() extracts a single TOML block."""
        from cypilot.utils.toml_utils import parse_toml_from_markdown

        md = "Some text\n```toml\ncypilot_path = \"adapter\"\n```\nMore text\n"
        result = parse_toml_from_markdown(md)
        self.assertEqual(result["cypilot_path"], "adapter")

    def test_parse_toml_from_markdown_multiple_blocks(self):
        """parse_toml_from_markdown() merges multiple TOML blocks."""
        from cypilot.utils.toml_utils import parse_toml_from_markdown

        md = (
            "```toml\na = 1\n```\n"
            "Some text\n"
            "```toml\nb = 2\n```\n"
        )
        result = parse_toml_from_markdown(md)
        self.assertEqual(result["a"], 1)
        self.assertEqual(result["b"], 2)

    def test_parse_toml_from_markdown_no_blocks(self):
        """parse_toml_from_markdown() returns {} when no TOML blocks exist."""
        from cypilot.utils.toml_utils import parse_toml_from_markdown

        result = parse_toml_from_markdown("No TOML here\n```python\nprint(1)\n```\n")
        self.assertEqual(result, {})

    def test_dumps_roundtrip(self):
        """dumps() produces TOML that tomllib can re-parse correctly."""
        import tomllib
        from cypilot.utils.toml_utils import dumps

        data = {"version": "1.0", "name": "my-project", "kits": {}}
        toml_str = dumps(data)
        restored = tomllib.loads(toml_str)
        self.assertEqual(restored["version"], "1.0")
        self.assertEqual(restored["name"], "my-project")


# ---------------------------------------------------------------------------
# agents.py, _core_config.py, layer_discovery.py – regression: direct import
# ---------------------------------------------------------------------------

class TestModuleLevelTomllibImports(unittest.TestCase):
    """Verify that modules which switched to module-level 'import tomllib' still load."""

    def test_agents_module_imports_without_error(self):
        """cypilot.commands.agents imports successfully (uses module-level tomllib)."""
        import importlib
        mod = importlib.import_module("cypilot.commands.agents")
        self.assertIsNotNone(mod)

    def test_layer_discovery_module_imports_without_error(self):
        """cypilot.utils.layer_discovery imports successfully (uses module-level tomllib)."""
        import importlib
        mod = importlib.import_module("cypilot.utils.layer_discovery")
        self.assertIsNotNone(mod)

    def test_manifest_module_imports_without_error(self):
        """cypilot.utils.manifest imports successfully (uses module-level tomllib)."""
        import importlib
        mod = importlib.import_module("cypilot.utils.manifest")
        self.assertIsNotNone(mod)

    def test_toml_utils_module_imports_without_error(self):
        """cypilot.utils.toml_utils imports successfully (uses module-level tomllib)."""
        import importlib
        mod = importlib.import_module("cypilot.utils.toml_utils")
        self.assertIsNotNone(mod)

    def test_ralphex_export_module_imports_without_error(self):
        """cypilot.ralphex_export imports successfully (uses module-level tomllib)."""
        import importlib
        mod = importlib.import_module("cypilot.ralphex_export")
        self.assertIsNotNone(mod)


# ---------------------------------------------------------------------------
# Regression: adapter_info core.toml loading with inline 'import tomllib as _tl'
# ---------------------------------------------------------------------------

class TestAdapterInfoCoreTomllib(unittest.TestCase):
    """Tests for the inline 'import tomllib as _tl' in cmd_adapter_info's core.toml loading."""

    def _make_minimal_project(self, root: Path) -> Path:
        """Create a minimal project structure; returns adapter_dir."""
        (root / ".git").mkdir()
        (root / "AGENTS.md").write_text(
            '<!-- @cpt:root-agents -->\n'
            '```toml\ncypilot_path = "adapter"\n```\n'
            '<!-- /@cpt:root-agents -->\n',
            encoding="utf-8",
        )
        adapter = root / "adapter"
        adapter.mkdir()
        (adapter / "config").mkdir()
        (adapter / "config" / "AGENTS.md").write_text("# Test\n", encoding="utf-8")
        return adapter

    def test_core_toml_loaded_correctly(self):
        """Config version from core.toml appears in info output."""
        import io
        import json
        from contextlib import redirect_stdout
        from cypilot.cli import main

        with TemporaryDirectory() as td:
            root = Path(td)
            adapter = self._make_minimal_project(root)
            (adapter / "config" / "core.toml").write_text(
                'version = "3.5.0"\nproject_root = ".."\n',
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["info", "--root", str(root)])
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())

        self.assertEqual(out.get("config_version"), "3.5.0")

    def test_corrupt_core_toml_sets_load_error(self):
        """When core.toml is corrupt, variables_degraded is set and no crash."""
        import io
        import json
        from contextlib import redirect_stdout
        from cypilot.cli import main

        with TemporaryDirectory() as td:
            root = Path(td)
            adapter = self._make_minimal_project(root)
            (adapter / "config" / "core.toml").write_text(
                "{{{{not valid toml!",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["info", "--root", str(root)])
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())

        # Should report degraded variables or None config_version — no crash
        self.assertTrue(
            out.get("variables_degraded") or out.get("config_version") is None
        )


# ---------------------------------------------------------------------------
# Regression: artifacts_meta inline 'import tomllib' paths
# ---------------------------------------------------------------------------

class TestArtifactsMetaTomllibInline(unittest.TestCase):
    """Tests for the inline tomllib imports in artifacts_meta.load_artifacts_meta()."""

    def test_toml_registry_loads_correctly(self):
        """load_artifacts_meta() reads a TOML registry using the inline import."""
        from cypilot.utils.artifacts_meta import load_artifacts_meta

        with TemporaryDirectory() as td:
            adapter_dir = Path(td)
            config_dir = adapter_dir / "config"
            config_dir.mkdir()
            _write_toml_file(
                config_dir / "artifacts.toml",
                'version = "1.0"\nproject_root = ".."\n\n'
                '[[systems]]\nname = "MyApp"\nslug = "myapp"\nkit = "sdlc"\n',
            )
            meta, err = load_artifacts_meta(adapter_dir)

        self.assertIsNone(err)
        self.assertIsNotNone(meta)
        self.assertEqual(meta.version, "1.0")

    def test_core_toml_merged_into_registry(self):
        """load_artifacts_meta() merges version/project_root from core.toml."""
        from cypilot.utils.artifacts_meta import load_artifacts_meta

        with TemporaryDirectory() as td:
            adapter_dir = Path(td)
            config_dir = adapter_dir / "config"
            config_dir.mkdir()
            # artifacts.toml without version — should be filled from core.toml
            _write_toml_file(
                config_dir / "artifacts.toml",
                '[[systems]]\nname = "App"\nslug = "app"\n',
            )
            _write_toml_file(
                config_dir / "core.toml",
                'version = "2.5.0"\nproject_root = "../.."\n',
            )
            meta, err = load_artifacts_meta(adapter_dir)

        self.assertIsNone(err)
        self.assertIsNotNone(meta)
        self.assertEqual(meta.version, "2.5.0")

    def test_missing_registry_returns_error(self):
        """load_artifacts_meta() returns (None, error_msg) when no registry exists."""
        from cypilot.utils.artifacts_meta import load_artifacts_meta

        with TemporaryDirectory() as td:
            adapter_dir = Path(td)
            meta, err = load_artifacts_meta(adapter_dir)

        self.assertIsNone(meta)
        self.assertIsNotNone(err)


if __name__ == "__main__":
    unittest.main()