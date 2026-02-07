"""Tests for artifacts_meta module."""

import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.utils.artifacts_meta import (
    Artifact,
    ArtifactsMeta,
    CodebaseEntry,
    Kit,
    SystemNode,
    create_backup,
    generate_default_registry,
    load_artifacts_meta,
)


class TestKit(unittest.TestCase):
    def test_kit_from_dict(self):
        data = {"format": "Cypilot", "path": "templates"}
        kit = Kit.from_dict("test-kit", data)
        self.assertEqual(kit.kit_id, "test-kit")
        self.assertEqual(kit.format, "Cypilot")
        self.assertEqual(kit.path, "templates")

    def test_kit_is_cypilot_format(self):
        kit = Kit("id", "Cypilot", "path")
        self.assertTrue(kit.is_cypilot_format())
        kit2 = Kit("id", "OTHER", "path")
        self.assertFalse(kit2.is_cypilot_format())

    def test_kit_get_template_path(self):
        kit = Kit("id", "Cypilot", "kits/sdlc")
        self.assertEqual(kit.get_template_path("PRD"), "kits/sdlc/artifacts/PRD/template.md")
        self.assertEqual(kit.get_template_path("UNKNOWN"), "kits/sdlc/artifacts/UNKNOWN/template.md")


class TestArtifact(unittest.TestCase):
    def test_artifact_from_dict(self):
        data = {"path": "docs/PRD.md", "kind": "PRD", "traceability": "FULL", "name": "Product Requirements"}
        artifact = Artifact.from_dict(data)
        self.assertEqual(artifact.path, "docs/PRD.md")
        self.assertEqual(artifact.kind, "PRD")
        self.assertEqual(artifact.traceability, "FULL")
        self.assertEqual(artifact.name, "Product Requirements")

    def test_artifact_type_backward_compat(self):
        """Cover line 64: backward compat property 'type'."""
        artifact = Artifact(path="a.md", kind="PRD", traceability="DOCS-ONLY")
        self.assertEqual(artifact.type, "PRD")

    def test_artifact_from_dict_legacy_type_key(self):
        """Cover backward compat for 'type' key instead of 'kind'."""
        data = {"path": "docs/PRD.md", "type": "PRD"}
        artifact = Artifact.from_dict(data)
        self.assertEqual(artifact.kind, "PRD")


class TestCodebaseEntry(unittest.TestCase):
    def test_codebase_entry_from_dict(self):
        data = {"path": "src/", "extensions": [".py", ".js"], "name": "Source"}
        entry = CodebaseEntry.from_dict(data)
        self.assertEqual(entry.path, "src/")
        self.assertEqual(entry.extensions, [".py", ".js"])
        self.assertEqual(entry.name, "Source")

    def test_codebase_entry_extensions_not_list(self):
        """Cover line 91: extensions not a list."""
        data = {"path": "src/", "extensions": "not-a-list"}
        entry = CodebaseEntry.from_dict(data)
        self.assertEqual(entry.extensions, [])


class TestSystemNode(unittest.TestCase):
    def test_system_node_from_dict_basic(self):
        data = {
            "name": "MySystem",
            "kit": "cypilot-sdlc",
            "artifacts": [{"path": "PRD.md", "kind": "PRD"}],
            "codebase": [{"path": "src/", "extensions": [".py"]}],
        }
        node = SystemNode.from_dict(data)
        self.assertEqual(node.name, "MySystem")
        self.assertEqual(node.kit, "cypilot-sdlc")
        self.assertEqual(len(node.artifacts), 1)
        self.assertEqual(len(node.codebase), 1)

    def test_system_node_with_children(self):
        """Cover lines 135-136: parsing children."""
        data = {
            "name": "Parent",
            "kit": "cypilot",
            "children": [
                {"name": "Child1", "kit": "cypilot"},
                {"name": "Child2", "kit": "cypilot"},
            ],
        }
        node = SystemNode.from_dict(data)
        self.assertEqual(len(node.children), 2)
        self.assertEqual(node.children[0].name, "Child1")
        self.assertEqual(node.children[0].parent, node)


class TestArtifactsMeta(unittest.TestCase):
    def test_from_dict_basic(self):
        data = {
            "version": "1.0",
            "project_root": "..",
            "kits": {"cypilot": {"format": "Cypilot", "path": "templates"}},
            "systems": [{"name": "Test", "kit": "cypilot", "artifacts": [{"path": "PRD.md", "kind": "PRD"}]}],
        }
        meta = ArtifactsMeta.from_dict(data)
        self.assertEqual(meta.version, "1.0")
        self.assertEqual(meta.project_root, "..")
        self.assertEqual(len(meta.kits), 1)
        self.assertEqual(len(meta.systems), 1)

    def test_from_json(self):
        """Cover lines 222-223: from_json method."""
        data = {
            "version": "1.0",
            "project_root": "..",
            "kits": {},
            "systems": [],
        }
        meta = ArtifactsMeta.from_json(json.dumps(data))
        self.assertEqual(meta.version, "1.0")

    def test_from_file(self):
        """Cover lines 228-229: from_file method."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "artifacts.json"
            data = {"version": "1.0", "project_root": "..", "kits": {}, "systems": []}
            path.write_text(json.dumps(data), encoding="utf-8")
            meta = ArtifactsMeta.from_file(path)
            self.assertEqual(meta.version, "1.0")

    def test_get_artifact_by_path(self):
        """Cover lines 241-242: get_artifact_by_path method."""
        data = {
            "version": "1.0",
            "project_root": "..",
            "kits": {"cypilot": {"format": "Cypilot", "path": "templates"}},
            "systems": [{"name": "Test", "kit": "cypilot", "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}]}],
        }
        meta = ArtifactsMeta.from_dict(data)
        result = meta.get_artifact_by_path("architecture/PRD.md")
        self.assertIsNotNone(result)
        artifact, system = result
        self.assertEqual(artifact.kind, "PRD")
        self.assertEqual(system.name, "Test")

    def test_get_artifact_by_path_not_found(self):
        data = {"version": "1.0", "project_root": "..", "kits": {}, "systems": []}
        meta = ArtifactsMeta.from_dict(data)
        result = meta.get_artifact_by_path("nonexistent.md")
        self.assertIsNone(result)

    def test_get_artifact_by_path_normalize_dot_slash(self):
        """Cover line 189: normalize paths starting with './'."""
        data = {
            "version": "1.0",
            "project_root": "..",
            "kits": {},
            "systems": [{"name": "Test", "kit": "", "artifacts": [{"path": "./PRD.md", "kind": "PRD"}]}],
        }
        meta = ArtifactsMeta.from_dict(data)
        result = meta.get_artifact_by_path("PRD.md")
        self.assertIsNotNone(result)

    def test_iter_all_artifacts(self):
        data = {
            "version": "1.0",
            "project_root": "..",
            "kits": {},
            "systems": [{"name": "Test", "kit": "", "artifacts": [{"path": "a.md", "kind": "A"}, {"path": "b.md", "kind": "B"}]}],
        }
        meta = ArtifactsMeta.from_dict(data)
        artifacts = list(meta.iter_all_artifacts())
        self.assertEqual(len(artifacts), 2)

    def test_index_system_with_nested_children(self):
        """Cover lines 182: recursing into children during indexing."""
        data = {
            "version": "1.0",
            "project_root": "..",
            "kits": {},
            "systems": [
                {
                    "name": "Parent",
                    "kit": "",
                    "artifacts": [{"path": "parent.md", "kind": "P"}],
                    "children": [
                        {
                            "name": "Child",
                            "kit": "",
                            "artifacts": [{"path": "child.md", "kind": "C"}],
                        }
                    ],
                }
            ],
        }
        meta = ArtifactsMeta.from_dict(data)
        # Both parent and child artifacts should be indexed
        parent_result = meta.get_artifact_by_path("parent.md")
        child_result = meta.get_artifact_by_path("child.md")
        self.assertIsNotNone(parent_result)
        self.assertIsNotNone(child_result)

    def test_iter_all_system_names(self):
        """Cover iter_all_system_names method with nested systems."""
        data = {
            "version": "1.0",
            "project_root": "..",
            "kits": {},
            "systems": [
                {
                    "name": "myapp",
                    "kit": "",
                    "children": [
                        {"name": "account-server", "kit": ""},
                        {"name": "billing", "kit": "", "children": [{"name": "invoicing", "kit": ""}]},
                    ],
                },
                {"name": "other-system", "kit": ""},
            ],
        }
        meta = ArtifactsMeta.from_dict(data)
        names = list(meta.iter_all_system_names())
        self.assertIn("myapp", names)
        self.assertIn("account-server", names)
        self.assertIn("billing", names)
        self.assertIn("invoicing", names)
        self.assertIn("other-system", names)
        self.assertEqual(len(names), 5)

    def test_get_all_system_names(self):
        """Cover get_all_system_names method returns lowercase set."""
        data = {
            "version": "1.0",
            "project_root": "..",
            "kits": {},
            "systems": [
                {"name": "MyApp", "kit": ""},
                {"name": "Account-Server", "kit": ""},
            ],
        }
        meta = ArtifactsMeta.from_dict(data)
        names = meta.get_all_system_names()
        self.assertIsInstance(names, set)
        self.assertIn("myapp", names)
        self.assertIn("account-server", names)
        # Original case should NOT be in the set
        self.assertNotIn("MyApp", names)
        self.assertNotIn("Account-Server", names)


class TestLoadArtifactsMeta(unittest.TestCase):
    def test_load_artifacts_meta_success(self):
        """Cover lines 275-284: load_artifacts_meta success path."""
        with TemporaryDirectory() as tmpdir:
            ad = Path(tmpdir)
            data = {"version": "1.0", "project_root": "..", "kits": {}, "systems": []}
            (ad / "artifacts.json").write_text(json.dumps(data), encoding="utf-8")
            meta, err = load_artifacts_meta(ad)
            self.assertIsNotNone(meta)
            self.assertIsNone(err)

    def test_load_artifacts_meta_missing_file(self):
        with TemporaryDirectory() as tmpdir:
            ad = Path(tmpdir)
            meta, err = load_artifacts_meta(ad)
            self.assertIsNone(meta)
            self.assertIn("Missing", err)

    def test_load_artifacts_meta_invalid_json(self):
        with TemporaryDirectory() as tmpdir:
            ad = Path(tmpdir)
            (ad / "artifacts.json").write_text("{invalid", encoding="utf-8")
            meta, err = load_artifacts_meta(ad)
            self.assertIsNone(meta)
            self.assertIn("Invalid JSON", err)

    def test_load_artifacts_meta_generic_exception(self):
        """Cover generic exception handling in load_artifacts_meta."""
        with TemporaryDirectory() as tmpdir:
            ad = Path(tmpdir)
            (ad / "artifacts.json").write_text('{"version": "1.0"}', encoding="utf-8")
            # This will fail because systems/artifacts are missing
            # Actually the from_dict handles missing gracefully, so let's force an error
            orig = ArtifactsMeta.from_dict

            def boom(data):
                raise RuntimeError("boom")

            try:
                ArtifactsMeta.from_dict = staticmethod(boom)
                meta, err = load_artifacts_meta(ad)
                self.assertIsNone(meta)
                self.assertIn("Failed to load", err)
            finally:
                ArtifactsMeta.from_dict = orig


class TestCreateBackup(unittest.TestCase):
    def test_create_backup_file(self):
        """Cover lines 296-313: create_backup for a file."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            path.write_text('{"key": "value"}', encoding="utf-8")
            backup = create_backup(path)
            self.assertIsNotNone(backup)
            self.assertTrue(backup.exists())
            self.assertIn(".backup", backup.name)
            self.assertEqual(backup.read_text(), '{"key": "value"}')

    def test_create_backup_directory(self):
        """Cover create_backup for a directory."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "mydir"
            path.mkdir()
            (path / "file.txt").write_text("content", encoding="utf-8")
            backup = create_backup(path)
            self.assertIsNotNone(backup)
            self.assertTrue(backup.is_dir())
            self.assertTrue((backup / "file.txt").exists())

    def test_create_backup_nonexistent_returns_none(self):
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nonexistent"
            backup = create_backup(path)
            self.assertIsNone(backup)

    def test_create_backup_exception_returns_none(self):
        """Cover exception handling in create_backup."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            path.write_text("x", encoding="utf-8")

            import shutil
            orig = shutil.copy2

            def boom(*args, **kwargs):
                raise RuntimeError("boom")

            try:
                shutil.copy2 = boom
                backup = create_backup(path)
                self.assertIsNone(backup)
            finally:
                shutil.copy2 = orig


class TestGenerateDefaultRegistry(unittest.TestCase):
    def test_generate_default_registry(self):
        result = generate_default_registry("MyProject", "../Cypilot")
        self.assertEqual(result["version"], "1.0")
        self.assertEqual(result["project_root"], "..")
        self.assertIn("cypilot-sdlc", result["kits"])
        self.assertEqual(len(result["systems"]), 1)
        self.assertEqual(result["systems"][0]["name"], "MyProject")

    def test_join_path_edge_cases(self):
        """Cover line 321: _join_path with empty base."""
        from cypilot.utils.artifacts_meta import _join_path

        self.assertEqual(_join_path("", "tail"), "tail")
        self.assertEqual(_join_path(".", "tail"), "tail")
        self.assertEqual(_join_path("base/", "/tail"), "base/tail")


class TestSystemNodeHierarchy(unittest.TestCase):
    """Test SystemNode hierarchy methods."""

    def test_get_hierarchy_prefix(self):
        """Cover get_hierarchy_prefix method."""
        data = {
            "version": "1.0",
            "project_root": "..",
            "kits": {},
            "systems": [
                {
                    "name": "Platform",
                    "slug": "platform",
                    "kit": "cypilot-sdlc",
                    "children": [
                        {
                            "name": "Core",
                            "slug": "core",
                            "kit": "cypilot-sdlc",
                            "children": [
                                {
                                    "name": "Auth",
                                    "slug": "auth",
                                    "kit": "cypilot-sdlc",
                                }
                            ],
                        }
                    ],
                }
            ],
        }
        meta = ArtifactsMeta.from_dict(data)
        # Find the auth node
        auth_node = None
        for node in meta.iter_all_systems():
            if node.slug == "auth":
                auth_node = node
                break
        self.assertIsNotNone(auth_node)
        self.assertEqual(auth_node.get_hierarchy_prefix(), "platform-core-auth")

    def test_validate_slug_valid(self):
        """Cover validate_slug method with valid slug."""
        node = SystemNode(name="Test", slug="valid-slug", kit="test")
        result = node.validate_slug()
        self.assertIsNone(result)

    def test_validate_slug_missing(self):
        """Cover validate_slug method with missing slug."""
        node = SystemNode(name="Test", slug="", kit="test")
        result = node.validate_slug()
        self.assertIsNotNone(result)
        self.assertIn("Missing slug", result)

    def test_validate_slug_invalid_format(self):
        """Cover validate_slug method with invalid slug format."""
        node = SystemNode(name="Test", slug="Invalid_Slug!", kit="test")
        result = node.validate_slug()
        self.assertIsNotNone(result)
        self.assertIn("Invalid slug", result)


class TestArtifactsMetaIterators(unittest.TestCase):
    """Test ArtifactsMeta iterator methods with nested children."""

    def test_iter_all_codebase_with_children(self):
        """Cover iter_all_codebase with nested system children."""
        data = {
            "version": "1.0",
            "project_root": "..",
            "kits": {},
            "systems": [
                {
                    "name": "Parent",
                    "slug": "parent",
                    "kit": "cypilot-sdlc",
                    "codebase": [{"name": "Parent Code", "path": "src/parent"}],
                    "children": [
                        {
                            "name": "Child",
                            "slug": "child",
                            "kit": "cypilot-sdlc",
                            "codebase": [{"name": "Child Code", "path": "src/child"}],
                        }
                    ],
                }
            ],
        }
        meta = ArtifactsMeta.from_dict(data)
        codebase_entries = list(meta.iter_all_codebase())
        self.assertEqual(len(codebase_entries), 2)
        paths = [cb.path for cb, _ in codebase_entries]
        self.assertIn("src/parent", paths)
        self.assertIn("src/child", paths)

    def test_iter_all_systems_with_children(self):
        """Cover iter_all_systems with nested children."""
        data = {
            "version": "1.0",
            "project_root": "..",
            "kits": {},
            "systems": [
                {
                    "name": "Root",
                    "slug": "root",
                    "kit": "cypilot-sdlc",
                    "children": [
                        {
                            "name": "Child1",
                            "slug": "child1",
                            "kit": "cypilot-sdlc",
                            "children": [
                                {"name": "Grandchild", "slug": "grandchild", "kit": "cypilot-sdlc"}
                            ],
                        }
                    ],
                }
            ],
        }
        meta = ArtifactsMeta.from_dict(data)
        systems = list(meta.iter_all_systems())
        self.assertEqual(len(systems), 3)
        slugs = [s.slug for s in systems]
        self.assertIn("root", slugs)
        self.assertIn("child1", slugs)
        self.assertIn("grandchild", slugs)

    def test_get_system_by_slug(self):
        """Cover get_system_by_slug method."""
        data = {
            "version": "1.0",
            "project_root": "..",
            "kits": {},
            "systems": [
                {
                    "name": "MyApp",
                    "slug": "myapp",
                    "kit": "cypilot-sdlc",
                    "children": [{"name": "Module", "slug": "module", "kit": "cypilot-sdlc"}],
                }
            ],
        }
        meta = ArtifactsMeta.from_dict(data)
        node = meta.get_system_by_slug("module")
        self.assertIsNotNone(node)
        self.assertEqual(node.name, "Module")
        # Test not found
        self.assertIsNone(meta.get_system_by_slug("nonexistent"))

    def test_validate_all_slugs(self):
        """Cover validate_all_slugs method."""
        data = {
            "version": "1.0",
            "project_root": "..",
            "kits": {},
            "systems": [
                {"name": "Valid", "slug": "valid", "kit": "cypilot-sdlc"},
                {"name": "Invalid", "slug": "Invalid_Slug!", "kit": "cypilot-sdlc"},
            ],
        }
        meta = ArtifactsMeta.from_dict(data)
        errors = meta.validate_all_slugs()
        self.assertEqual(len(errors), 1)
        self.assertIn("Invalid slug", errors[0])


if __name__ == "__main__":
    unittest.main()
