"""
Targeted tests to increase coverage for agents.py to 90%+.

Covers:
- _ensure_frontmatter_description_quoted edge cases
- _resolve_gen_kits adapter fallback
- _registered_kit_dirs edge cases
- _ensure_cypilot_local copy path
- _list_workflow_files gen kit scanning
"""

import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))


class TestEnsureFrontmatterDescriptionQuoted(unittest.TestCase):
    """Cover lines 440, 455-457 in agents.py."""

    def test_no_closing_frontmatter_returns_unchanged(self):
        from cypilot.commands.agents import _ensure_frontmatter_description_quoted

        content = "---\ndescription: hello\nno closing fence\n"
        self.assertEqual(_ensure_frontmatter_description_quoted(content), content)

    def test_description_with_inline_comment(self):
        from cypilot.commands.agents import _ensure_frontmatter_description_quoted

        content = '---\ndescription: some value # a comment\n---\nbody\n'
        result = _ensure_frontmatter_description_quoted(content)
        self.assertIn('"some value"', result)
        self.assertIn("# a comment", result)


class TestResolveGenKits(unittest.TestCase):
    """Cover lines 484, 490 in agents.py."""

    def test_fallback_to_adapter_gen_kits(self):
        from cypilot.commands.agents import _resolve_gen_kits

        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            cypilot_root = project_root / "somedir"
            cypilot_root.mkdir()
            # No .gen/kits at cypilot_root level
            # Create adapter gen kits
            (project_root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "myadapter"\n```\n',
                encoding="utf-8",
            )
            adapter_gen_kits = project_root / "myadapter" / ".gen" / "kits"
            adapter_gen_kits.mkdir(parents=True)

            result = _resolve_gen_kits(cypilot_root, project_root)
            self.assertEqual(result.resolve(), adapter_gen_kits.resolve())

    def test_no_adapter_returns_default(self):
        from cypilot.commands.agents import _resolve_gen_kits

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            result = _resolve_gen_kits(root, root)
            # Returns the default .gen/kits path even if it doesn't exist
            self.assertTrue(str(result).endswith("kits"))


class TestRegisteredKitDirs(unittest.TestCase):
    """Cover line 503 in agents.py."""

    def test_kits_not_dict_returns_none(self):
        from cypilot.commands.agents import _registered_kit_dirs

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "cypilot"\n```\n',
                encoding="utf-8",
            )
            cfg_dir = root / "cypilot" / "config"
            cfg_dir.mkdir(parents=True)
            # core.toml with kits as a string instead of dict
            (cfg_dir / "core.toml").write_text(
                'schema_version = "1.0"\nproject_root = ".."\nkits = "not_a_dict"\n',
                encoding="utf-8",
            )
            result = _registered_kit_dirs(root)
            self.assertIsNone(result)


class TestEnsureCypilotLocal(unittest.TestCase):
    """Cover lines 117-132 in agents.py."""

    def test_copy_when_external(self):
        from cypilot.commands.agents import _ensure_cypilot_local

        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "project"
            project_root.mkdir()
            # No AGENTS.md → will use default "cypilot" name
            cypilot_root = Path(tmpdir) / "external_cypilot"
            cypilot_root.mkdir()

            # Create a minimal cypilot structure at external root
            (cypilot_root / "skills").mkdir()
            (cypilot_root / "skills" / "test.py").write_text("# test", encoding="utf-8")
            (cypilot_root / "workflows").mkdir()
            (cypilot_root / "workflows" / "wf.md").write_text("# wf", encoding="utf-8")

            result_path, report = _ensure_cypilot_local(cypilot_root, project_root, dry_run=False)
            self.assertEqual(report["action"], "copied")
            self.assertGreater(report["file_count"], 0)
            self.assertTrue((result_path / ".core").is_dir())

    def test_copy_error_returns_error_report(self):
        from cypilot.commands.agents import _ensure_cypilot_local
        from unittest.mock import patch

        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "project"
            project_root.mkdir()
            cypilot_root = Path(tmpdir) / "external"
            cypilot_root.mkdir()

            with patch("pathlib.Path.mkdir", side_effect=PermissionError("denied")):
                result_path, report = _ensure_cypilot_local(cypilot_root, project_root, dry_run=False)
            self.assertEqual(report["action"], "error")
            self.assertIn("denied", report["message"])


class TestListWorkflowFilesGenKits(unittest.TestCase):
    """Cover lines 552-558 in agents.py."""

    def test_scans_gen_kit_workflows(self):
        from cypilot.commands.agents import _list_workflow_files

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # Create core workflows dir (need .core/ so core_subpath routes there)
            core_wf = root / ".core" / "workflows"
            core_wf.mkdir(parents=True)
            (core_wf / "analyze.md").write_text(
                "---\ntype: workflow\ndescription: analyze\n---\nContent\n",
                encoding="utf-8",
            )

            # Create gen kit workflows
            gen_kit_wf = root / ".gen" / "kits" / "sdlc" / "workflows"
            gen_kit_wf.mkdir(parents=True)
            (gen_kit_wf / "pr-review.md").write_text(
                "---\ntype: workflow\ndescription: pr review\n---\nContent\n",
                encoding="utf-8",
            )

            results = _list_workflow_files(root, project_root=None)
            names = [r[0] for r in results]
            self.assertIn("analyze.md", names)
            self.assertIn("pr-review.md", names)

    def test_gen_kit_iterdir_exception_is_handled(self):
        from cypilot.commands.agents import _list_workflow_files
        from unittest.mock import patch

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            core_wf = root / ".core" / "workflows"
            core_wf.mkdir(parents=True)

            gen_kits = root / ".gen" / "kits"
            gen_kits.mkdir(parents=True)

            original_iterdir = Path.iterdir

            def _boom(self):
                if "kits" in str(self) and ".gen" in str(self):
                    raise OSError("boom")
                return original_iterdir(self)

            with patch.object(Path, "iterdir", _boom):
                results = _list_workflow_files(root)
            # Should not crash, just return core workflows (empty since no files)
            self.assertIsInstance(results, list)


class TestLoadJsonFileNonDict(unittest.TestCase):
    """Cover line 137 in agents.py (_load_json_file returns None for non-dict)."""

    def test_json_array_returns_none(self):
        from cypilot.commands.agents import _load_json_file

        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "test.json"
            p.write_text("[1, 2, 3]", encoding="utf-8")
            self.assertIsNone(_load_json_file(p))


if __name__ == "__main__":
    unittest.main()
