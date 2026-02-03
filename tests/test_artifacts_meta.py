"""Tests for artifacts_meta module."""

import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "spider" / "scripts"))

from spider.utils.artifacts_meta import (
    Artifact,
    ArtifactsMeta,
    CodebaseEntry,
    Weaver,
    SystemNode,
    create_backup,
    generate_default_registry,
    load_artifacts_meta,
)


class TestWeaver(unittest.TestCase):
    def test_weaver_from_dict(self):
        data = {"format": "Spider", "path": "templates"}
        weaver = Weaver.from_dict("test-weaver", data)
        self.assertEqual(weaver.weaver_id, "test-weaver")
        self.assertEqual(weaver.format, "Spider")
        self.assertEqual(weaver.path, "templates")

    def test_weaver_is_spider_format(self):
        weaver = Weaver("id", "Spider", "path")
        self.assertTrue(weaver.is_spider_format())
        weaver2 = Weaver("id", "OTHER", "path")
        self.assertFalse(weaver2.is_spider_format())

    def test_weaver_get_template_path(self):
        weaver = Weaver("id", "Spider", "weavers/sdlc")
        self.assertEqual(weaver.get_template_path("PRD"), "weavers/sdlc/artifacts/PRD/template.md")
        self.assertEqual(weaver.get_template_path("UNKNOWN"), "weavers/sdlc/artifacts/UNKNOWN/template.md")


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
            "weaver": "spider-sdlc",
            "artifacts": [{"path": "PRD.md", "kind": "PRD"}],
            "codebase": [{"path": "src/", "extensions": [".py"]}],
        }
        node = SystemNode.from_dict(data)
        self.assertEqual(node.name, "MySystem")
        self.assertEqual(node.weaver, "spider-sdlc")
        self.assertEqual(len(node.artifacts), 1)
        self.assertEqual(len(node.codebase), 1)

    def test_system_node_with_children(self):
        """Cover lines 135-136: parsing children."""
        data = {
            "name": "Parent",
            "weaver": "spider",
            "children": [
                {"name": "Child1", "weaver": "spider"},
                {"name": "Child2", "weaver": "spider"},
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
            "weavers": {"spider": {"format": "Spider", "path": "templates"}},
            "systems": [{"name": "Test", "weaver": "spider", "artifacts": [{"path": "PRD.md", "kind": "PRD"}]}],
        }
        meta = ArtifactsMeta.from_dict(data)
        self.assertEqual(meta.version, "1.0")
        self.assertEqual(meta.project_root, "..")
        self.assertEqual(len(meta.weavers), 1)
        self.assertEqual(len(meta.systems), 1)

    def test_from_json(self):
        """Cover lines 222-223: from_json method."""
        data = {
            "version": "1.0",
            "project_root": "..",
            "weavers": {},
            "systems": [],
        }
        meta = ArtifactsMeta.from_json(json.dumps(data))
        self.assertEqual(meta.version, "1.0")

    def test_from_file(self):
        """Cover lines 228-229: from_file method."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "artifacts.json"
            data = {"version": "1.0", "project_root": "..", "weavers": {}, "systems": []}
            path.write_text(json.dumps(data), encoding="utf-8")
            meta = ArtifactsMeta.from_file(path)
            self.assertEqual(meta.version, "1.0")

    def test_get_artifact_by_path(self):
        """Cover lines 241-242: get_artifact_by_path method."""
        data = {
            "version": "1.0",
            "project_root": "..",
            "weavers": {"spider": {"format": "Spider", "path": "templates"}},
            "systems": [{"name": "Test", "weaver": "spider", "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}]}],
        }
        meta = ArtifactsMeta.from_dict(data)
        result = meta.get_artifact_by_path("architecture/PRD.md")
        self.assertIsNotNone(result)
        artifact, system = result
        self.assertEqual(artifact.kind, "PRD")
        self.assertEqual(system.name, "Test")

    def test_get_artifact_by_path_not_found(self):
        data = {"version": "1.0", "project_root": "..", "weavers": {}, "systems": []}
        meta = ArtifactsMeta.from_dict(data)
        result = meta.get_artifact_by_path("nonexistent.md")
        self.assertIsNone(result)

    def test_get_artifact_by_path_normalize_dot_slash(self):
        """Cover line 189: normalize paths starting with './'."""
        data = {
            "version": "1.0",
            "project_root": "..",
            "weavers": {},
            "systems": [{"name": "Test", "weaver": "", "artifacts": [{"path": "./PRD.md", "kind": "PRD"}]}],
        }
        meta = ArtifactsMeta.from_dict(data)
        result = meta.get_artifact_by_path("PRD.md")
        self.assertIsNotNone(result)

    def test_iter_all_artifacts(self):
        data = {
            "version": "1.0",
            "project_root": "..",
            "weavers": {},
            "systems": [{"name": "Test", "weaver": "", "artifacts": [{"path": "a.md", "kind": "A"}, {"path": "b.md", "kind": "B"}]}],
        }
        meta = ArtifactsMeta.from_dict(data)
        artifacts = list(meta.iter_all_artifacts())
        self.assertEqual(len(artifacts), 2)

    def test_index_system_with_nested_children(self):
        """Cover lines 182: recursing into children during indexing."""
        data = {
            "version": "1.0",
            "project_root": "..",
            "weavers": {},
            "systems": [
                {
                    "name": "Parent",
                    "weaver": "",
                    "artifacts": [{"path": "parent.md", "kind": "P"}],
                    "children": [
                        {
                            "name": "Child",
                            "weaver": "",
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
            "weavers": {},
            "systems": [
                {
                    "name": "myapp",
                    "weaver": "",
                    "children": [
                        {"name": "account-server", "weaver": ""},
                        {"name": "billing", "weaver": "", "children": [{"name": "invoicing", "weaver": ""}]},
                    ],
                },
                {"name": "other-system", "weaver": ""},
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
            "weavers": {},
            "systems": [
                {"name": "MyApp", "weaver": ""},
                {"name": "Account-Server", "weaver": ""},
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
            data = {"version": "1.0", "project_root": "..", "weavers": {}, "systems": []}
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
        result = generate_default_registry("MyProject", "../Spider")
        self.assertEqual(result["version"], "1.0")
        self.assertEqual(result["project_root"], "..")
        self.assertIn("spider-sdlc", result["weavers"])
        self.assertEqual(len(result["systems"]), 1)
        self.assertEqual(result["systems"][0]["name"], "MyProject")

    def test_join_path_edge_cases(self):
        """Cover line 321: _join_path with empty base."""
        from spider.utils.artifacts_meta import _join_path

        self.assertEqual(_join_path("", "tail"), "tail")
        self.assertEqual(_join_path(".", "tail"), "tail")
        self.assertEqual(_join_path("base/", "/tail"), "base/tail")


if __name__ == "__main__":
    unittest.main()
