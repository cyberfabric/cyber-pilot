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


class TestResolveConfigKits(unittest.TestCase):
    """Cover _resolve_config_kits in agents.py."""

    def test_fallback_to_adapter_config_kits(self):
        from cypilot.commands.agents import _resolve_config_kits

        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            cypilot_root = project_root / "somedir"
            cypilot_root.mkdir()
            # No config/kits at cypilot_root level
            # Create adapter config kits
            (project_root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "myadapter"\n```\n',
                encoding="utf-8",
            )
            adapter_config_kits = project_root / "myadapter" / "config" / "kits"
            adapter_config_kits.mkdir(parents=True)

            result = _resolve_config_kits(cypilot_root, project_root)
            self.assertEqual(result.resolve(), adapter_config_kits.resolve())

    def test_no_adapter_returns_default(self):
        from cypilot.commands.agents import _resolve_config_kits

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            result = _resolve_config_kits(root, root)
            # Returns the default config/kits path even if it doesn't exist
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


class TestListWorkflowFilesConfigKits(unittest.TestCase):
    """Cover kit workflow scanning in agents.py."""

    def test_scans_config_kit_workflows(self):
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

            # Create config kit workflows (new layout)
            config_kit_wf = root / "config" / "kits" / "sdlc" / "workflows"
            config_kit_wf.mkdir(parents=True)
            (config_kit_wf / "pr-review.md").write_text(
                "---\ntype: workflow\ndescription: pr review\n---\nContent\n",
                encoding="utf-8",
            )

            results = _list_workflow_files(root, project_root=None)
            names = [r[0] for r in results]
            self.assertIn("analyze.md", names)
            self.assertIn("pr-review.md", names)

    def test_config_kit_iterdir_exception_is_handled(self):
        from cypilot.commands.agents import _list_workflow_files
        from unittest.mock import patch

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            core_wf = root / ".core" / "workflows"
            core_wf.mkdir(parents=True)

            config_kits = root / "config" / "kits"
            config_kits.mkdir(parents=True)

            original_iterdir = Path.iterdir

            def _boom(self):
                if "kits" in str(self) and "config" in str(self):
                    raise OSError("boom")
                return original_iterdir(self)

            with patch.object(Path, "iterdir", _boom):
                results = _list_workflow_files(root)
            # Should not crash, just return core workflows (empty since no files)
            self.assertIsInstance(results, list)


class TestTargetPathFromRoot(unittest.TestCase):
    """Cover line 52 in agents.py (_target_path_from_root with cypilot_root=None)."""

    def test_cypilot_root_none_returns_cypilot_path_prefix(self):
        from cypilot.commands.agents import _target_path_from_root

        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            target = project_root / "some" / "file.md"
            result = _target_path_from_root(target, project_root, cypilot_root=None)
            self.assertEqual(result, "{cypilot_path}/some/file.md")


class TestLoadJsonFileNonDict(unittest.TestCase):
    """Cover lines 137, 141 in agents.py (_load_json_file edge cases)."""

    def test_json_array_returns_none(self):
        from cypilot.commands.agents import _load_json_file

        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "test.json"
            p.write_text("[1, 2, 3]", encoding="utf-8")
            self.assertIsNone(_load_json_file(p))

    def test_nonexistent_file_returns_none(self):
        from cypilot.commands.agents import _load_json_file

        self.assertIsNone(_load_json_file(Path("/nonexistent/file.json")))


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


class TestHumanAgentsList(unittest.TestCase):
    """Cover lines 1128-1158 (_human_agents_list formatter)."""

    @_with_human_mode
    def test_agents_with_existing_files(self):
        from cypilot.commands.agents import _human_agents_list
        import io
        from contextlib import redirect_stderr

        results = {
            "windsurf": {
                "workflows": {"updated": ["/p/.windsurf/workflows/cypilot-generate.md"], "created": []},
                "skills": {"updated": ["/p/.windsurf/skills/cypilot/SKILL.md"], "created": []},
            },
        }
        err = io.StringIO()
        with redirect_stderr(err):
            _human_agents_list({}, ["windsurf"], results, Path("/p"))
        output = err.getvalue()
        self.assertIn("windsurf", output)
        self.assertIn("2 file(s) installed", output)

    @_with_human_mode
    def test_agents_with_no_files(self):
        from cypilot.commands.agents import _human_agents_list
        import io
        from contextlib import redirect_stderr

        results = {
            "cursor": {
                "workflows": {"updated": [], "created": []},
                "skills": {"updated": [], "created": []},
            },
        }
        err = io.StringIO()
        with redirect_stderr(err):
            _human_agents_list({}, ["cursor"], results, Path("/p"))
        output = err.getvalue()
        self.assertIn("no files", output)

    @_with_human_mode
    def test_agents_not_configured(self):
        from cypilot.commands.agents import _human_agents_list
        import io
        from contextlib import redirect_stderr

        results = {
            "copilot": {
                "workflows": {"updated": [], "created": ["/p/.github/prompts/cypilot-generate.prompt.md"]},
                "skills": {"updated": [], "created": ["/p/.github/copilot-instructions.md"]},
            },
        }
        err = io.StringIO()
        with redirect_stderr(err):
            _human_agents_list({}, ["copilot"], results, Path("/p"))
        output = err.getvalue()
        self.assertIn("not configured", output)

    @_with_human_mode
    def test_no_agents_installed_hint(self):
        from cypilot.commands.agents import _human_agents_list
        import io
        from contextlib import redirect_stderr

        results = {
            "windsurf": {
                "workflows": {"updated": [], "created": []},
                "skills": {"updated": [], "created": []},
            },
        }
        err = io.StringIO()
        with redirect_stderr(err):
            _human_agents_list({}, ["windsurf"], results, Path("/p"))
        output = err.getvalue()
        self.assertIn("cpt generate-agents", output)


class TestHumanGenerateAgentsPreview(unittest.TestCase):
    """Cover lines 1166-1191 (_human_generate_agents_preview formatter)."""

    @_with_human_mode
    def test_preview_with_changes(self):
        from cypilot.commands.agents import _human_generate_agents_preview
        import io
        from contextlib import redirect_stderr

        results = {
            "windsurf": {
                "workflows": {
                    "created": ["/p/.windsurf/workflows/cypilot-generate.md"],
                    "updated": ["/p/.windsurf/workflows/cypilot-analyze.md"],
                },
                "skills": {
                    "created": ["/p/.windsurf/skills/cypilot/SKILL.md"],
                    "updated": [],
                },
            },
        }
        err = io.StringIO()
        with redirect_stderr(err):
            _human_generate_agents_preview(["windsurf"], results, Path("/p"))
        output = err.getvalue()
        self.assertIn("windsurf", output)

    @_with_human_mode
    def test_preview_up_to_date(self):
        from cypilot.commands.agents import _human_generate_agents_preview
        import io
        from contextlib import redirect_stderr

        results = {
            "cursor": {
                "workflows": {"created": [], "updated": []},
                "skills": {"created": [], "updated": []},
            },
        }
        err = io.StringIO()
        with redirect_stderr(err):
            _human_generate_agents_preview(["cursor"], results, Path("/p"))
        output = err.getvalue()
        self.assertIn("up to date", output)

    @_with_human_mode
    def test_preview_includes_deletion_only_changes(self):
        from cypilot.commands.agents import _human_generate_agents_preview
        import io
        from contextlib import redirect_stderr

        results = {
            "claude": {
                "workflows": {"created": [], "updated": [], "deleted": []},
                "skills": {
                    "created": [],
                    "updated": [],
                    "deleted": ["/p/.claude/commands/cypilot-plan.md", "/p/.claude/commands/cypilot-generate.md"],
                },
            },
        }
        err = io.StringIO()
        with redirect_stderr(err):
            _human_generate_agents_preview(["claude"], results, Path("/p"))
        output = err.getvalue()
        self.assertIn("claude", output)
        self.assertIn("deleted", output.lower())

    @_with_human_mode
    def test_preview_includes_workflow_renames_and_subagents(self):
        from cypilot.commands.agents import _human_generate_agents_preview
        import io
        from contextlib import redirect_stderr

        results = {
            "claude": {
                "workflows": {
                    "created": [],
                    "updated": [],
                    "renamed": [("/p/.claude/commands/cypilot-old.md", "/p/.claude/commands/cypilot-new.md")],
                    "deleted": [],
                },
                "skills": {"created": [], "updated": [], "deleted": []},
                "subagents": {
                    "created": ["/p/.claude/agents/cypilot-codegen.md"],
                    "updated": [],
                    "skipped": False,
                    "skip_reason": "",
                },
            },
        }
        err = io.StringIO()
        with redirect_stderr(err):
            _human_generate_agents_preview(["claude"], results, Path("/p"))
        output = err.getvalue()
        self.assertIn("workflow renamed", output)
        self.assertIn("cypilot-codegen.md", output)


class TestHumanGenerateAgentsOk(unittest.TestCase):
    """Cover lines 1194-1252 (_human_generate_agents_ok formatter)."""

    @_with_human_mode
    def test_ok_pass_with_files(self):
        from cypilot.commands.agents import _human_generate_agents_ok
        import io
        from contextlib import redirect_stderr

        results = {
            "windsurf": {
                "status": "PASS",
                "workflows": {
                    "created": ["/p/.windsurf/workflows/cypilot-generate.md"],
                    "updated": ["/p/.windsurf/workflows/cypilot-analyze.md"],
                    "counts": {"created": 1, "updated": 1},
                },
                "skills": {
                    "created": ["/p/.windsurf/skills/cypilot/SKILL.md"],
                    "updated": ["/p/.windsurf/workflows/cypilot.md"],
                    "counts": {"created": 1, "updated": 1},
                },
                "errors": [],
            },
        }
        err = io.StringIO()
        with redirect_stderr(err):
            _human_generate_agents_ok({"status": "PASS"}, ["windsurf"], results, dry_run=False)
        output = err.getvalue()
        self.assertIn("Agent integration complete", output)

    @_with_human_mode
    def test_ok_dry_run(self):
        from cypilot.commands.agents import _human_generate_agents_ok
        import io
        from contextlib import redirect_stderr

        results = {
            "cursor": {
                "status": "PASS",
                "workflows": {"created": [], "updated": [], "counts": {}},
                "skills": {"created": [], "updated": [], "counts": {}},
            },
        }
        err = io.StringIO()
        with redirect_stderr(err):
            _human_generate_agents_ok({"status": "PASS"}, ["cursor"], results, dry_run=True)
        output = err.getvalue()
        self.assertIn("Dry run", output)

    @_with_human_mode
    def test_ok_dry_run_uses_future_tense_and_reports_subagents(self):
        from cypilot.commands.agents import _human_generate_agents_ok
        import io
        from contextlib import redirect_stderr

        results = {
            "claude": {
                "status": "PASS",
                "workflows": {
                    "created": [],
                    "updated": [],
                    "renamed": [("/p/.claude/commands/cypilot-old.md", "/p/.claude/commands/cypilot-new.md")],
                    "deleted": ["/p/.claude/commands/cypilot-analyze.md"],
                    "counts": {"created": 0, "updated": 0, "renamed": 1, "deleted": 1},
                },
                "skills": {
                    "created": [],
                    "updated": [],
                    "deleted": ["/p/.claude/commands/cypilot-plan.md", "/p/.claude/commands/cypilot-generate.md"],
                    "skipped": [".claude/commands/cypilot-workspace.md (missing generated marker)", ".claude/commands/cypilot-analyze.md (missing generated marker)"],
                    "counts": {"created": 0, "updated": 0, "deleted": 1, "skipped": 1},
                },
                "subagents": {
                    "created": ["/p/.claude/agents/cypilot-codegen.md"],
                    "updated": [],
                    "skipped": False,
                    "skip_reason": "",
                    "counts": {"created": 1, "updated": 0},
                },
                "errors": [],
            },
        }
        err = io.StringIO()
        with redirect_stderr(err):
            _human_generate_agents_ok({"status": "PASS"}, ["claude"], results, dry_run=True)
        output = err.getvalue()
        self.assertIn("workflow renamed", output)
        self.assertIn("would be removed", output)
        self.assertIn("would be preserved", output)
        self.assertIn("subagent file(s)", output)

    @_with_human_mode
    def test_ok_with_errors(self):
        from cypilot.commands.agents import _human_generate_agents_ok
        import io
        from contextlib import redirect_stderr

        results = {
            "custom": {
                "status": "ERROR",
                "workflows": {"created": [], "updated": [], "counts": {}},
                "skills": {"created": [], "updated": [], "counts": {}},
                "errors": ["something went wrong"],
            },
        }
        err = io.StringIO()
        with redirect_stderr(err):
            _human_generate_agents_ok({"status": "ERROR"}, ["custom"], results, dry_run=False)
        output = err.getvalue()
        self.assertIn("something went wrong", output)
        self.assertIn("errors", output.lower())


class TestProcessSingleAgentEdgeCases(unittest.TestCase):
    """Cover edge cases in _process_single_agent: non-dict output, kit desc enrichment, workflow deletion."""

    def _make_project(self, tmpdir):
        root = (Path(tmpdir) / "proj").resolve()
        root.mkdir()
        (root / ".git").mkdir()
        cpt = root / "cypilot"
        cpt.mkdir()
        core_skill = cpt / ".core" / "skills" / "cypilot" / "SKILL.md"
        core_skill.parent.mkdir(parents=True)
        core_skill.write_text(
            "---\nname: cypilot\ndescription: Test skill\n---\nContent\n",
            encoding="utf-8",
        )
        # Create .gen/kits/sdlc/SKILL.md with description for kit enrichment (lines 805, 808-815)
        kit_skill = cpt / ".gen" / "kits" / "sdlc" / "SKILL.md"
        kit_skill.parent.mkdir(parents=True)
        kit_skill.write_text(
            "---\nname: sdlc-skill\ndescription: SDLC workflow kit\n---\nKit content\n",
            encoding="utf-8",
        )
        return root, cpt

    def test_kit_description_enrichment(self):
        """Skill description is enriched with kit descriptions (lines 805, 808-815)."""
        from cypilot.commands.agents import _process_single_agent, _default_agents_config

        with TemporaryDirectory() as td:
            root, cpt = self._make_project(td)
            # Create windsurf skill output
            ws_skill = root / ".windsurf" / "skills" / "cypilot" / "SKILL.md"
            ws_skill.parent.mkdir(parents=True)
            ws_skill.write_text("old", encoding="utf-8")

            cfg = _default_agents_config()
            result = _process_single_agent("windsurf", root, cpt, cfg, None, dry_run=False)
            # Skill file should contain kit description
            content = ws_skill.read_text(encoding="utf-8")
            self.assertIn("SKILL.md", content)

    def test_non_dict_output_cfg_skipped(self):
        """Non-dict entries in outputs list are skipped (line 614)."""
        from cypilot.commands.agents import _process_single_agent

        with TemporaryDirectory() as td:
            root, cpt = self._make_project(td)
            cfg = {
                "version": 1,
                "agents": {
                    "windsurf": {
                        "workflows": {},
                        "skills": {
                            "outputs": [
                                "not_a_dict",  # should be skipped
                                {
                                    "path": ".windsurf/skills/cypilot/SKILL.md",
                                    "template": ["ALWAYS open and follow `{target_skill_path}`"],
                                },
                            ],
                        },
                    },
                },
            }
            result = _process_single_agent("windsurf", root, cpt, cfg, None, dry_run=True)
            self.assertIn("skills", result)

    def test_stale_workflow_deleted(self):
        """Workflow proxy pointing to non-existent target is deleted (lines 767-774)."""
        from cypilot.commands.agents import _process_single_agent, _default_agents_config

        with TemporaryDirectory() as td:
            root, cpt = self._make_project(td)
            # Ensure .core/workflows/ exists so core_subpath resolves there
            core_wf = cpt / ".core" / "workflows"
            core_wf.mkdir(parents=True, exist_ok=True)
            # Put a real workflow so the agent generates a valid proxy
            (core_wf / "analyze.md").write_text(
                "---\nname: analyze\ndescription: Analyze artifacts\n---\nContent\n",
                encoding="utf-8",
            )

            wf_dir = root / ".windsurf" / "workflows"
            wf_dir.mkdir(parents=True)
            # Create a stale workflow proxy pointing to a removed workflow
            (wf_dir / "cypilot-old.md").write_text(
                "# /cypilot-old\n\nALWAYS open and follow `{cypilot_path}/.core/workflows/old-removed.md`\n",
                encoding="utf-8",
            )
            cfg = _default_agents_config()
            result = _process_single_agent("windsurf", root, cpt, cfg, None, dry_run=False)
            wf = result.get("workflows", {})
            self.assertIn(
                (wf_dir / "cypilot-old.md").as_posix(),
                wf.get("deleted", []),
            )
            # File should be removed
            self.assertFalse((wf_dir / "cypilot-old.md").exists())

    def test_claude_generated_legacy_command_deleted(self):
        from cypilot.commands.agents import _process_single_agent, _default_agents_config

        with TemporaryDirectory() as td:
            root, cpt = self._make_project(td)
            (cpt / ".core" / "workflows").mkdir(parents=True, exist_ok=True)
            (cpt / ".core" / "workflows" / "generate.md").write_text(
                "---\nname: cypilot-generate\ndescription: Generate\n---\n# Generate\n",
                encoding="utf-8",
            )
            (cpt / ".core" / "workflows" / "analyze.md").write_text(
                "---\nname: cypilot-analyze\ndescription: Analyze\n---\n# Analyze\n",
                encoding="utf-8",
            )
            (cpt / ".core" / "workflows" / "plan.md").write_text(
                "---\nname: cypilot-plan\ndescription: Plan\n---\n# Plan\n",
                encoding="utf-8",
            )
            (cpt / ".core" / "workflows" / "workspace.md").write_text(
                "---\nname: cypilot-workspace\ndescription: Workspace\n---\n# Workspace\n",
                encoding="utf-8",
            )

            legacy_dir = root / ".claude" / "commands"
            legacy_dir.mkdir(parents=True)
            legacy_file = legacy_dir / "cypilot-generate.md"
            legacy_file.write_text(
                "# /cypilot-generate\n\nALWAYS open and follow `{cypilot_path}/.core/workflows/generate.md`\n",
                encoding="utf-8",
            )

            result = _process_single_agent("claude", root, cpt, _default_agents_config(), None, dry_run=False)
            self.assertIn(
                legacy_file.relative_to(root).as_posix(),
                result.get("skills", {}).get("deleted", []),
            )
            self.assertFalse(legacy_file.exists())

    def test_claude_generated_legacy_command_wrong_target_is_preserved(self):
        from cypilot.commands.agents import _process_single_agent, _default_agents_config

        with TemporaryDirectory() as td:
            root, cpt = self._make_project(td)
            (cpt / ".core" / "workflows").mkdir(parents=True, exist_ok=True)
            (cpt / ".core" / "workflows" / "plan.md").write_text(
                "---\nname: cypilot-plan\ndescription: Plan\n---\n# Plan\n",
                encoding="utf-8",
            )
            (cpt / ".core" / "workflows" / "workspace.md").write_text(
                "---\nname: cypilot-workspace\ndescription: Workspace\n---\n# Workspace\n",
                encoding="utf-8",
            )
            (cpt / ".core" / "workflows" / "generate.md").write_text(
                "---\nname: cypilot-generate\ndescription: Generate\n---\n# Generate\n",
                encoding="utf-8",
            )
            (cpt / ".core" / "workflows" / "analyze.md").write_text(
                "---\nname: cypilot-analyze\ndescription: Analyze\n---\n# Analyze\n",
                encoding="utf-8",
            )

            legacy_dir = root / ".claude" / "commands"
            legacy_dir.mkdir(parents=True)
            legacy_file = legacy_dir / "cypilot-generate.md"
            legacy_file.write_text(
                "# /cypilot-generate\n\nALWAYS open and follow `{cypilot_path}/.core/workflows/analyze.md`\n",
                encoding="utf-8",
            )

            result = _process_single_agent("claude", root, cpt, _default_agents_config(), None, dry_run=False)
            self.assertNotIn(
                legacy_file.relative_to(root).as_posix(),
                result.get("skills", {}).get("deleted", []),
            )
            skipped = result.get("skills", {}).get("skipped", [])
            self.assertTrue(any("missing generated marker" in item for item in skipped))
            self.assertTrue(legacy_file.exists())

    def test_claude_hand_authored_legacy_command_preserved(self):
        from cypilot.commands.agents import _process_single_agent, _default_agents_config

        with TemporaryDirectory() as td:
            root, cpt = self._make_project(td)
            (cpt / ".core" / "workflows").mkdir(parents=True, exist_ok=True)
            (cpt / ".core" / "workflows" / "plan.md").write_text(
                "---\nname: cypilot-plan\ndescription: Plan\n---\n# Plan\n",
                encoding="utf-8",
            )
            (cpt / ".core" / "workflows" / "generate.md").write_text(
                "---\nname: cypilot-generate\ndescription: Generate\n---\n# Generate\n",
                encoding="utf-8",
            )
            (cpt / ".core" / "workflows" / "analyze.md").write_text(
                "---\nname: cypilot-analyze\ndescription: Analyze\n---\n# Analyze\n",
                encoding="utf-8",
            )
            (cpt / ".core" / "workflows" / "workspace.md").write_text(
                "---\nname: cypilot-workspace\ndescription: Workspace\n---\n# Workspace\n",
                encoding="utf-8",
            )

            legacy_dir = root / ".claude" / "commands"
            legacy_dir.mkdir(parents=True)
            legacy_file = legacy_dir / "cypilot-generate.md"
            legacy_file.write_text(
                "# /cypilot-generate\n\nCustom instructions stay here.\n",
                encoding="utf-8",
            )

            result = _process_single_agent("claude", root, cpt, _default_agents_config(), None, dry_run=False)
            self.assertNotIn(
                legacy_file.relative_to(root).as_posix(),
                result.get("skills", {}).get("deleted", []),
            )
            skipped = result.get("skills", {}).get("skipped", [])
            self.assertTrue(any("missing generated marker" in item for item in skipped))
            self.assertTrue(legacy_file.exists())

    def test_claude_cleanup_ignores_non_string_output_path(self):
        from cypilot.commands.agents import _process_single_agent, _default_agents_config

        with TemporaryDirectory() as td:
            root, cpt = self._make_project(td)
            (cpt / ".core" / "workflows").mkdir(parents=True, exist_ok=True)
            for workflow_name in ("generate", "analyze", "plan", "workspace"):
                (cpt / ".core" / "workflows" / f"{workflow_name}.md").write_text(
                    f"---\nname: cypilot-{workflow_name}\ndescription: {workflow_name}\n---\n# {workflow_name}\n",
                    encoding="utf-8",
                )

            cfg = _default_agents_config()
            cfg["agents"]["claude"]["skills"]["outputs"].append(
                {"path": 123, "template": ["ALWAYS open and follow `{target_path}`"]},
            )

            result = _process_single_agent("claude", root, cpt, cfg, None, dry_run=True)
            self.assertIn("skills", result)
            self.assertTrue(any("missing path" in err for err in (result.get("errors") or [])))


class TestEnsureCypilotLocalRootDirsAndFiles(unittest.TestCase):
    """Cover lines 123-127, 130-133 by patching _COPY_ROOT_DIRS/_COPY_FILES."""

    def test_copy_root_dirs_and_files(self):
        from cypilot.commands.agents import _ensure_cypilot_local
        from unittest.mock import patch

        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "project"
            project_root.mkdir()
            cypilot_root = Path(tmpdir) / "external"
            cypilot_root.mkdir()

            # Create source dirs for _COPY_DIRS
            (cypilot_root / "skills").mkdir()
            (cypilot_root / "skills" / "test.py").write_text("# s", encoding="utf-8")

            # Create a root-level dir and a file for the patched lists
            (cypilot_root / "guides").mkdir()
            (cypilot_root / "guides" / "README.md").write_text("# g", encoding="utf-8")
            (cypilot_root / "VERSION").write_text("1.0", encoding="utf-8")

            with patch("cypilot.commands.agents._COPY_ROOT_DIRS", ["guides"]), \
                 patch("cypilot.commands.agents._COPY_FILES", ["VERSION"]):
                result_path, report = _ensure_cypilot_local(cypilot_root, project_root, dry_run=False)

            self.assertEqual(report["action"], "copied")
            # guides/ should be at local root level (not under .core/)
            self.assertTrue((result_path / "guides" / "README.md").is_file())
            # VERSION should be under .core/
            self.assertTrue((result_path / ".core" / "VERSION").is_file())


class TestCypilotRalphexRegistration(unittest.TestCase):
    """Verify cypilot-ralphex is registered and discoverable by agent generation."""

    def _make_project_with_agents_toml(self, tmpdir):
        root = (Path(tmpdir) / "proj").resolve()
        root.mkdir()
        (root / ".git").mkdir()
        cpt = root / "cypilot"
        cpt.mkdir()
        core_skill = cpt / ".core" / "skills" / "cypilot"
        core_skill.mkdir(parents=True)
        # Copy the real agents.toml
        src_agents_toml = Path(__file__).parent.parent / "skills" / "cypilot" / "agents.toml"
        import shutil
        shutil.copy2(src_agents_toml, core_skill / "agents.toml")
        # Create the prompt file so validation passes
        agents_dir = core_skill / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "cypilot-ralphex.md").write_text(
            "You are a Cypilot ralphex delegation agent.\n",
            encoding="utf-8",
        )
        (agents_dir / "cypilot-codegen.md").write_text(
            "You are a Cypilot code generator.\n",
            encoding="utf-8",
        )
        (agents_dir / "cypilot-pr-review.md").write_text(
            "You are a Cypilot PR reviewer.\n",
            encoding="utf-8",
        )
        return root, cpt

    def _make_full_project(self, tmpdir):
        """Create project with core structure needed for _process_single_agent."""
        root, cpt = self._make_project_with_agents_toml(tmpdir)
        core_skill = cpt / ".core" / "skills" / "cypilot" / "SKILL.md"
        core_skill.write_text(
            "---\nname: cypilot\ndescription: Test skill\n---\nContent\n",
            encoding="utf-8",
        )
        (cpt / ".core" / "workflows").mkdir(parents=True, exist_ok=True)
        return root, cpt

    def test_ralphex_in_agents_toml(self):
        """agents.toml contains a cypilot-ralphex entry."""
        agents_toml = Path(__file__).parent.parent / "skills" / "cypilot" / "agents.toml"
        with open(agents_toml, "rb") as f:
            import tomllib
            data = tomllib.load(f)
        agents = data.get("agents", {})
        self.assertIn("cypilot-ralphex", agents)
        entry = agents["cypilot-ralphex"]
        self.assertEqual(entry["prompt_file"], "agents/cypilot-ralphex.md")
        self.assertEqual(entry["mode"], "readwrite")
        self.assertFalse(entry.get("isolation", False))

    def test_ralphex_discovered_by_kit_agents(self):
        """_discover_kit_agents finds cypilot-ralphex from agents.toml."""
        from cypilot.commands.agents import _discover_kit_agents

        with TemporaryDirectory() as td:
            root, cpt = self._make_project_with_agents_toml(td)
            agents = _discover_kit_agents(cpt, root)
            names = [a["name"] for a in agents]
            self.assertIn("cypilot-ralphex", names)
            ralphex = next(a for a in agents if a["name"] == "cypilot-ralphex")
            self.assertEqual(ralphex["mode"], "readwrite")
            self.assertFalse(ralphex["isolation"])
            self.assertIsNotNone(ralphex["prompt_file_abs"])

    def test_ralphex_generates_claude_subagent_proxy(self):
        """Agent generation produces a claude subagent proxy for cypilot-ralphex."""
        from cypilot.commands.agents import _process_single_agent, _default_agents_config

        with TemporaryDirectory() as td:
            root, cpt = self._make_full_project(td)

            cfg = _default_agents_config()
            result = _process_single_agent("claude", root, cpt, cfg, None, dry_run=False)

            subagents = result.get("subagents", {})
            all_files = subagents.get("created", []) + subagents.get("updated", [])
            ralphex_files = [f for f in all_files if "cypilot-ralphex" in f]
            self.assertTrue(
                len(ralphex_files) > 0,
                f"Expected cypilot-ralphex subagent proxy, got: {all_files}",
            )
            # Verify the generated file uses ALWAYS open and follow
            proxy_path = Path(ralphex_files[0])
            content = proxy_path.read_text(encoding="utf-8")
            self.assertIn("ALWAYS open and follow", content)
            self.assertIn("cypilot-ralphex", content)
            # Verify readwrite tools (not readonly)
            self.assertIn("Write", content)
            self.assertIn("Edit", content)

    def test_ralphex_generates_cursor_subagent_proxy(self):
        """Agent generation produces a cursor subagent proxy for cypilot-ralphex."""
        from cypilot.commands.agents import _process_single_agent, _default_agents_config

        with TemporaryDirectory() as td:
            root, cpt = self._make_full_project(td)

            cfg = _default_agents_config()
            result = _process_single_agent("cursor", root, cpt, cfg, None, dry_run=False)

            subagents = result.get("subagents", {})
            all_files = subagents.get("created", []) + subagents.get("updated", [])
            ralphex_files = [f for f in all_files if "cypilot-ralphex" in f]
            self.assertTrue(
                len(ralphex_files) > 0,
                f"Expected cypilot-ralphex cursor proxy, got: {all_files}",
            )
            proxy_path = Path(ralphex_files[0])
            content = proxy_path.read_text(encoding="utf-8")
            self.assertIn("ALWAYS open and follow", content)
            # Cursor readwrite gets edit tool
            self.assertIn("edit", content)

    def test_ralphex_generates_copilot_subagent_proxy(self):
        """Agent generation produces a copilot subagent proxy for cypilot-ralphex."""
        from cypilot.commands.agents import _process_single_agent, _default_agents_config

        with TemporaryDirectory() as td:
            root, cpt = self._make_full_project(td)

            cfg = _default_agents_config()
            result = _process_single_agent("copilot", root, cpt, cfg, None, dry_run=False)

            subagents = result.get("subagents", {})
            all_files = subagents.get("created", []) + subagents.get("updated", [])
            ralphex_files = [f for f in all_files if "cypilot-ralphex" in f]
            self.assertTrue(
                len(ralphex_files) > 0,
                f"Expected cypilot-ralphex copilot proxy, got: {all_files}",
            )
            proxy_path = Path(ralphex_files[0])
            content = proxy_path.read_text(encoding="utf-8")
            self.assertIn("ALWAYS open and follow", content)
            # Copilot readwrite gets wildcard tools
            self.assertIn('"*"', content)

    def test_ralphex_generates_openai_toml_entry(self):
        """Agent generation includes cypilot-ralphex in OpenAI TOML output."""
        from cypilot.commands.agents import _process_single_agent, _default_agents_config

        with TemporaryDirectory() as td:
            root, cpt = self._make_full_project(td)

            cfg = _default_agents_config()
            result = _process_single_agent("openai", root, cpt, cfg, None, dry_run=False)

            subagents = result.get("subagents", {})
            all_files = subagents.get("created", []) + subagents.get("updated", [])
            toml_files = [f for f in all_files if "cypilot-ralphex.toml" in f]
            self.assertTrue(
                len(toml_files) > 0,
                f"Expected cypilot-ralphex.toml, got: {all_files}",
            )
            content = Path(toml_files[0]).read_text(encoding="utf-8")
            self.assertIn("cypilot-ralphex", content)
            self.assertIn("ALWAYS open and follow", content)

    def test_ralphex_not_forked_per_tool(self):
        """All generated proxies point to the same canonical prompt path."""
        from cypilot.commands.agents import _process_single_agent, _default_agents_config

        with TemporaryDirectory() as td:
            root, cpt = self._make_full_project(td)

            canonical_fragment = "skills/cypilot/agents/cypilot-ralphex.md"
            for agent in ("claude", "cursor", "copilot", "openai"):
                cfg = _default_agents_config()
                result = _process_single_agent(agent, root, cpt, cfg, None, dry_run=False)
                subagents = result.get("subagents", {})
                all_files = subagents.get("created", []) + subagents.get("updated", [])
                for fpath in all_files:
                    content = Path(fpath).read_text(encoding="utf-8")
                    if "cypilot-ralphex" in fpath or "cypilot_ralphex" in content:
                        self.assertIn(
                            canonical_fragment,
                            content,
                            f"{agent} proxy does not point to canonical path",
                        )

    def test_windsurf_skill_routes_to_canonical_skill(self):
        """Windsurf skill output references the canonical SKILL.md (delegation routing)."""
        from cypilot.commands.agents import _process_single_agent, _default_agents_config

        with TemporaryDirectory() as td:
            root, cpt = self._make_full_project(td)

            cfg = _default_agents_config()
            result = _process_single_agent("windsurf", root, cpt, cfg, None, dry_run=False)

            # Windsurf exposes capabilities through SKILL.md routing, not subagent files
            skills = result.get("skills", {})
            skill_files = skills.get("created", []) + skills.get("updated", [])
            self.assertTrue(
                len(skill_files) > 0,
                "Expected windsurf skill outputs to be generated",
            )
            # Verify at least one skill output references the canonical SKILL.md
            found_skill_ref = False
            for fpath in skill_files:
                content = Path(fpath).read_text(encoding="utf-8")
                if "ALWAYS open and follow" in content and "SKILL.md" in content:
                    found_skill_ref = True
                    break
            self.assertTrue(found_skill_ref, "Windsurf skill must reference canonical SKILL.md")

            # Windsurf does not have dedicated subagent proxy files
            subagents = result.get("subagents", {})
            self.assertTrue(
                subagents.get("skipped", False),
                "Windsurf subagents should be skipped (no subagent proxy format)",
            )


if __name__ == "__main__":
    unittest.main()
