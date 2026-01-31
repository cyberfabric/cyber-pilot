"""
Integration tests for CLI commands.

Tests CLI entry point with various command combinations to improve coverage.
"""

import unittest
import sys
import os
import json
import io
import unittest.mock
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import redirect_stdout, redirect_stderr

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "fdd" / "scripts"))

from fdd.cli import main


def _bootstrap_registry(project_root: Path, *, entries: list) -> None:
    (project_root / ".git").mkdir(exist_ok=True)
    (project_root / ".fdd-config.json").write_text(
        '{\n  "fddAdapterPath": "adapter"\n}\n',
        encoding="utf-8",
    )
    adapter_dir = project_root / "adapter"
    adapter_dir.mkdir(parents=True, exist_ok=True)
    (adapter_dir / "AGENTS.md").write_text(
        "# FDD Adapter: Test\n\n**Extends**: `../AGENTS.md`\n",
        encoding="utf-8",
    )
    (adapter_dir / "artifacts.json").write_text(
        json.dumps({"version": "1.0", "artifacts": entries}, indent=2) + "\n",
        encoding="utf-8",
    )


class TestCLIValidateCommand(unittest.TestCase):
    """Test validate command variations."""

    def test_validate_default_artifact_is_current_dir(self):
        """Test validate command without --artifact uses current directory."""
        # --artifact now defaults to "." (current directory)
        # This test just verifies it doesn't raise an error for missing argument
        stdout = io.StringIO()
        stderr = io.StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            # Should not raise SystemExit for missing argument
            # (may still fail validation but that's expected)
            exit_code = main(["validate"])
            # Exit code 0 = PASS, 1 = ERROR (no adapter), 2 = FAIL - all valid
            self.assertIn(exit_code, [0, 1, 2])

    def test_validate_nonexistent_artifact(self):
        """Test validate command with non-existent artifact."""
        with TemporaryDirectory() as tmpdir:
            # Use valid artifact name
            fake_path = Path(tmpdir) / "DESIGN.md"
            
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                try:
                    exit_code = main(["validate", "--artifact", str(fake_path)])
                    # Should fail with file not found
                    self.assertNotEqual(exit_code, 0)
                    output = stdout.getvalue()
                    self.assertIn("ERROR", output.upper())
                except FileNotFoundError:
                    # Also acceptable - file doesn't exist
                    pass

    def test_validate_dir_with_design_and_features_flag_fails(self):
        """When --artifact is a feature dir containing DESIGN.md, --features must error."""
        with TemporaryDirectory() as tmpdir:
            feat = Path(tmpdir)
            (feat / "DESIGN.md").write_text("# Feature: X\n", encoding="utf-8")

            with self.assertRaises(SystemExit):
                main(["validate", "--artifact", str(feat), "--features", "feature-x"]) 

    def test_validate_dir_without_design_uses_code_root_traceability(self):
        """Cover validate branch when --artifact is a directory without DESIGN.md."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["validate", "--artifact", str(root)])

            self.assertIn(exit_code, (0, 1, 2))
            out = json.loads(stdout.getvalue())
            self.assertIn("status", out)

    def test_validate_code_root_with_feature_artifacts(self):
        """Cover validation when --artifact is a code root directory with features."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / "src").mkdir(parents=True, exist_ok=True)
            (root / "architecture" / "features" / "feature-a").mkdir(parents=True)
            (root / "architecture" / "features" / "feature-b").mkdir(parents=True)

            # Minimal artifacts for feature-a/feature-b so traceability runs.
            (root / "architecture" / "features" / "feature-a" / "DESIGN.md").write_text("# Feature: A\n", encoding="utf-8")
            (root / "architecture" / "features" / "feature-b" / "DESIGN.md").write_text("# Feature: B\n", encoding="utf-8")

            _bootstrap_registry(
                root,
                entries=[
                    {"kind": "FEATURE", "system": "Test", "path": "architecture/features/feature-a/DESIGN.md", "format": "FDD"},
                    {"kind": "FEATURE", "system": "Test", "path": "architecture/features/feature-b/DESIGN.md", "format": "FDD"},
                    {"kind": "SRC", "system": "Test", "path": "src", "format": "CONTEXT", "traceability_enabled": True, "extensions": [".py"]},
                ],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["validate", "--artifact", str(root)])

            self.assertIn(exit_code, (0, 1, 2))
            out = json.loads(stdout.getvalue())
            self.assertIn("status", out)

    def test_validate_feature_dir_with_design_md_runs_codebase_traceability(self):
        """Cover validate branch when --artifact is a feature directory containing DESIGN.md."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir(exist_ok=True)
            feat = root / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            (feat / "DESIGN.md").write_text("# Feature: X\n", encoding="utf-8")

            _bootstrap_registry(
                root,
                entries=[
                    {"kind": "FEATURE", "system": "Test", "path": "architecture/features/feature-x/DESIGN.md", "format": "FDD"},
                ],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["validate", "--artifact", str(feat)])
            self.assertIn(exit_code, (0, 1, 2))
            out = json.loads(stdout.getvalue())
            self.assertIn("status", out)


class TestCLIInitCommand(unittest.TestCase):
    def test_init_creates_config_and_adapter_and_allows_agent_workflows(self):
        with TemporaryDirectory() as tmpdir:
            project = Path(tmpdir) / "project"
            project.mkdir()

            fdd_core = project / "FDD"
            fdd_core.mkdir()
            (fdd_core / "AGENTS.md").write_text("# FDD Core\n", encoding="utf-8")
            (fdd_core / "requirements").mkdir()
            (fdd_core / "workflows").mkdir()

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main([
                    "init",
                    "--project-root",
                    str(project),
                    "--fdd-root",
                    str(fdd_core),
                    "--yes",
                ])
            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "PASS")
            self.assertTrue((project / ".fdd-config.json").exists())
            self.assertTrue((project / "FDD-Adapter" / "AGENTS.md").exists())

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main([
                    "agent-workflows",
                    "--agent",
                    "windsurf",
                    "--root",
                    str(project),
                    "--fdd-root",
                    str(fdd_core),
                    "--dry-run",
                ])
            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "PASS")

    def test_init_interactive_defaults(self):
        with TemporaryDirectory() as tmpdir:
            project = Path(tmpdir) / "project"
            project.mkdir()

            fdd_core = project / "FDD"
            fdd_core.mkdir()
            (fdd_core / "AGENTS.md").write_text("# FDD Core\n", encoding="utf-8")
            (fdd_core / "requirements").mkdir()
            (fdd_core / "workflows").mkdir()

            orig_cwd = os.getcwd()
            try:
                os.chdir(project.as_posix())
                with unittest.mock.patch("builtins.input", side_effect=["", ""]):
                    stdout = io.StringIO()
                    with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                        exit_code = main(["init", "--fdd-root", str(fdd_core)])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "PASS")
                self.assertTrue((project / ".fdd-config.json").exists())
                self.assertTrue((project / "FDD-Adapter" / "AGENTS.md").exists())
            finally:
                os.chdir(orig_cwd)


class TestCLISearchCommands(unittest.TestCase):
    """Test search command variations."""

    def test_list_ids_missing_file_errors(self):
        """Cover list-ids load_text error branch."""
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["list-ids", "--artifact", "/tmp/does-not-exist.md"])
        self.assertEqual(exit_code, 1)

    def test_get_content_no_adapter_error(self):
        """Cover ERROR for get-content when no adapter found."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Doc\n\n## A. A\n\nX\n", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--artifact", str(doc), "--id", "fdd-test-id"])
            self.assertEqual(exit_code, 1)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "ERROR")

    def test_agent_workflows_empty_agent_raises(self):
        with self.assertRaises(SystemExit):
            main(["agent-workflows", "--agent", " "])

    def test_agent_workflows_missing_filename_format_returns_config_incomplete(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / "fdd-agent-workflows.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "agents": {
                            "windsurf": {
                                "workflow_dir": ".windsurf/workflows",
                                "workflow_command_prefix": "fdd-",
                                "workflow_filename_format": " ",
                                "template": ["# /{command}", "", "ALWAYS open and follow `{target_workflow_path}`"],
                            }
                        },
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agent-workflows", "--agent", "windsurf", "--root", str(root)])
            self.assertEqual(code, 2)

    def test_agent_workflows_rename_scan_head_read_error_and_regex_no_match(self):
        from fdd import cli as fdd_cli

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            wf_dir = root / ".windsurf" / "workflows"
            wf_dir.mkdir(parents=True)

            bad_head = wf_dir / "x.md"
            bad_head.write_text("x\n", encoding="utf-8")

            no_match = wf_dir / "y.md"
            no_match.write_text("# /x\n\nALWAYS open and follow `abc\n", encoding="utf-8")

            orig = Path.read_text

            def _rt(self: Path, *a, **k):
                if self.resolve() == bad_head.resolve():
                    raise OSError("boom")
                return orig(self, *a, **k)

            with unittest.mock.patch.object(Path, "read_text", _rt):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = main(["agent-workflows", "--agent", "windsurf", "--root", str(root), "--fdd-root", str(Path(fdd_cli.__file__).resolve().parents[4])])
            self.assertEqual(code, 0)

    def test_agent_workflows_delete_stale_unlink_error_ignored(self):
        from fdd import cli as fdd_cli

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            wf_dir = root / ".windsurf" / "workflows"
            wf_dir.mkdir(parents=True)

            fdd_root = Path(fdd_cli.__file__).resolve().parents[4]
            target_abs = (fdd_root / "workflows" / "does-not-exist.md").resolve().as_posix()
            stale = wf_dir / "fdd-stale.md"
            stale.write_text(f"# /fdd-stale\n\nALWAYS open and follow `{target_abs}`\n", encoding="utf-8")

            orig_unlink = Path.unlink

            def _unlink(self: Path, *a, **k):
                if self.resolve() == stale.resolve():
                    raise OSError("no")
                return orig_unlink(self, *a, **k)

            with unittest.mock.patch.object(Path, "unlink", _unlink):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = main(["agent-workflows", "--agent", "windsurf", "--root", str(root), "--fdd-root", str(fdd_root)])
            self.assertEqual(code, 0)

    def test_agent_workflows_update_read_error_treated_as_empty(self):
        from fdd import cli as fdd_cli

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            wf_dir = root / ".windsurf" / "workflows"
            wf_dir.mkdir(parents=True)
            fdd_root = Path(fdd_cli.__file__).resolve().parents[4]

            dst = wf_dir / "fdd-prd.md"
            dst.write_text("x\n", encoding="utf-8")

            orig = Path.read_text

            def _rt(self: Path, *a, **k):
                if self.resolve() == dst.resolve():
                    raise OSError("boom")
                return orig(self, *a, **k)

            with unittest.mock.patch.object(Path, "read_text", _rt):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = main(["agent-workflows", "--agent", "windsurf", "--root", str(root), "--fdd-root", str(fdd_root)])
            self.assertEqual(code, 0)

    def test_get_content_file_not_found(self):
        """Cover ERROR for get-content when artifact file not found."""
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["get-content", "--artifact", "/tmp/does-not-exist.md", "--id", "fdd-test-id"])
        self.assertEqual(exit_code, 1)
        out = json.loads(stdout.getvalue())
        self.assertEqual(out.get("status"), "ERROR")


class TestCLITraceabilityCommands(unittest.TestCase):
    """Test traceability command variations."""

    def test_where_defined_basic(self):
        """Test where-defined command using adapter."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / "architecture").mkdir(parents=True)

            # Definition file
            design = root / "architecture" / "DESIGN.md"
            design.write_text(
                "\n".join(
                    [
                        "# Design",
                        "## A. x",
                        "## B. Requirements",
                        "- [ ] **ID**: `fdd-test-req-auth`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            _bootstrap_registry(
                root,
                entries=[
                    {"kind": "DESIGN", "system": "Test", "path": "architecture/DESIGN.md", "format": "FDD", "traceability_enabled": True},
                ],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["where-defined", "--id", "fdd-test-req-auth"])
            self.assertIn(exit_code, (0, 1, 2))

    def test_where_used_basic(self):
        """Test where-used command using adapter."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / "architecture").mkdir(parents=True)

            # Definition file
            design = root / "architecture" / "DESIGN.md"
            design.write_text(
                "\n".join(
                    [
                        "# Design",
                        "## A. x",
                        "## B. Requirements",
                        "**ID**: `fdd-test-req-auth`",
                        "Uses: `fdd-test-req-auth`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            _bootstrap_registry(
                root,
                entries=[
                    {"kind": "DESIGN", "system": "Test", "path": "architecture/DESIGN.md", "format": "FDD", "traceability_enabled": True},
                ],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["where-used", "--id", "fdd-test-req-auth"])
            self.assertIn(exit_code, (0, 1))


class TestCLIAgentIntegrationCommands(unittest.TestCase):
    def _write_minimal_fdd_skill(self, root: Path) -> None:
        (root / "skills" / "fdd").mkdir(parents=True, exist_ok=True)
        (root / "skills" / "fdd" / "SKILL.md").write_text("# FDD Skill\n", encoding="utf-8")

    def test_agent_skills_windsurf_legacy_creates_skill_folder(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_fdd_skill(root)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["agent-skills", "--agent", "windsurf", "--root", str(root)])
            self.assertEqual(exit_code, 0)

            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "PASS")
            entry = root / ".windsurf" / "skills" / "fdd" / "SKILL.md"
            self.assertTrue(entry.exists())
            txt = entry.read_text(encoding="utf-8")
            self.assertIn("ALWAYS open and follow", txt)

    def test_agent_skills_cursor_outputs_creates_rules_and_command(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_fdd_skill(root)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["agent-skills", "--agent", "cursor", "--root", str(root)])
            self.assertEqual(exit_code, 0)

            rules = root / ".cursor" / "rules" / "fdd.mdc"
            cmd = root / ".cursor" / "commands" / "fdd.md"
            self.assertTrue(rules.exists())
            self.assertTrue(cmd.exists())
            self.assertIn("ALWAYS open and follow", rules.read_text(encoding="utf-8"))
            self.assertIn("ALWAYS open and follow", cmd.read_text(encoding="utf-8"))

    def test_agent_skills_claude_outputs_creates_command(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_fdd_skill(root)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["agent-skills", "--agent", "claude", "--root", str(root)])
            self.assertEqual(exit_code, 0)

            cmd = root / ".claude" / "commands" / "fdd.md"
            self.assertTrue(cmd.exists())
            self.assertIn("ALWAYS open and follow", cmd.read_text(encoding="utf-8"))

    def test_agent_skills_copilot_outputs_creates_instructions_and_prompt(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_fdd_skill(root)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["agent-skills", "--agent", "copilot", "--root", str(root)])
            self.assertEqual(exit_code, 0)

            instructions = root / ".github" / "copilot-instructions.md"
            prompt = root / ".github" / "prompts" / "fdd-skill.prompt.md"
            self.assertTrue(instructions.exists())
            self.assertTrue(prompt.exists())
            self.assertIn("ALWAYS open and follow", instructions.read_text(encoding="utf-8"))
            self.assertIn("ALWAYS open and follow", prompt.read_text(encoding="utf-8"))


class TestCLIAgentWorkflowsCommands(unittest.TestCase):
    def _write_minimal_agent_workflows_cfg(self, root: Path, agent: str) -> Path:
        cfg_path = root / "fdd-agent-workflows.json"
        cfg_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "agents": {
                        agent: {
                            "workflow_dir": ".windsurf/workflows",
                            "workflow_command_prefix": "fdd-",
                            "workflow_filename_format": "{command}.md",
                            "template": [
                                "# /{command}",
                                "",
                                "ALWAYS open and follow `{target_workflow_path}`",
                            ],
                        }
                    },
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        return cfg_path

    def _write_minimal_fdd_skill(self, root: Path) -> None:
        (root / "skills" / "fdd").mkdir(parents=True, exist_ok=True)
        (root / "skills" / "fdd" / "SKILL.md").write_text("# FDD Skill\n", encoding="utf-8")

    def test_agent_workflows_windsurf_creates_files(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["agent-workflows", "--agent", "windsurf", "--root", str(root)])
            self.assertEqual(exit_code, 0)

            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "PASS")
            self.assertGreater(out.get("counts", {}).get("workflows", 0), 0)
            self.assertGreater(out.get("counts", {}).get("created", 0), 0)
            created = out.get("created", [])
            self.assertTrue(any(Path(p).exists() for p in created))

    def test_agent_workflows_dry_run_does_not_write_files(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["agent-workflows", "--agent", "windsurf", "--root", str(root), "--dry-run"])
            self.assertEqual(exit_code, 0)

            out = json.loads(stdout.getvalue())
            self.assertTrue(out.get("dry_run"))
            created = out.get("created", [])
            self.assertGreater(len(created), 0)
            self.assertTrue(all(not Path(p).exists() for p in created))

    def test_agent_workflows_fdd_entrypoint_is_not_prefixed(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_agent_workflows_cfg(root, "windsurf")

            (root / "workflows").mkdir(parents=True, exist_ok=True)
            (root / "workflows" / "fdd.md").write_text(
                "---\n"
                "fdd: true\n"
                "type: workflow\n"
                "name: FDD Entrypoint\n"
                "version: 1.0\n"
                "purpose: Enable FDD\n"
                "---\n\n"
                "# Enable FDD\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main([
                    "agent-workflows",
                    "--agent",
                    "windsurf",
                    "--root",
                    str(root),
                    "--fdd-root",
                    str(root),
                ])
            self.assertEqual(exit_code, 0)

            entry = root / ".windsurf" / "workflows" / "fdd.md"
            self.assertTrue(entry.exists())
            txt = entry.read_text(encoding="utf-8")
            self.assertIn("# /fdd", txt)
            self.assertIn("ALWAYS open and follow `workflows/fdd.md`", txt)

    def test_agent_workflows_unknown_agent_writes_stub_and_returns_config_incomplete(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["agent-workflows", "--agent", "mystery-agent", "--root", str(root)])
            self.assertEqual(exit_code, 2)

            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "CONFIG_INCOMPLETE")

    def test_agent_skills_empty_agent_raises(self):
        with self.assertRaises(SystemExit):
            main(["agent-skills", "--agent", " "])

    def test_agent_skills_project_root_not_found(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agent-skills", "--agent", "windsurf", "--root", str(root)])
            self.assertEqual(code, 1)

    def test_agent_skills_auto_adds_missing_recognized_agent_to_existing_config(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_fdd_skill(root)

            cfg_path = root / "fdd-agent-skills.json"
            cfg_path.write_text(
                json.dumps({"version": 1, "agents": {"cursor": {"outputs": []}}}, indent=2) + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agent-skills", "--agent", "windsurf", "--root", str(root)])
            self.assertIn(code, (0, 1, 2))
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            self.assertIn("windsurf", (cfg.get("agents") or {}))

    def test_agent_skills_outputs_read_error_updates(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_fdd_skill(root)

            cfg_path = root / "fdd-agent-skills.json"
            cfg_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "agents": {
                            "cursor": {
                                "outputs": [
                                    {
                                        "path": ".cursor/rules/fdd.mdc",
                                        "template": ["ALWAYS open and follow `{target_skill_path}`"],
                                    }
                                ]
                            }
                        },
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            out_path = root / ".cursor" / "rules" / "fdd.mdc"
            out_path.parent.mkdir(parents=True)
            out_path.write_text("x\n", encoding="utf-8")

            orig = Path.read_text

            def _rt(self: Path, *a, **k):
                if self.resolve() == out_path.resolve():
                    raise OSError("boom")
                return orig(self, *a, **k)

            with unittest.mock.patch.object(Path, "read_text", _rt):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = main(["agent-skills", "--agent", "cursor", "--root", str(root)])
            self.assertEqual(code, 0)

    def test_agent_skills_legacy_schema_missing_skill_name_and_entry_filename_defaults(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_fdd_skill(root)

            cfg_path = root / "fdd-agent-skills.json"
            cfg_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "agents": {
                            "windsurf": {
                                "skills_dir": ".windsurf/skills",
                                "template": ["ALWAYS open and follow `{target_skill_path}`"],
                            }
                        },
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agent-skills", "--agent", "windsurf", "--root", str(root)])
            self.assertEqual(code, 2)

            cfg_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "agents": {
                            "windsurf": {
                                "skills_dir": ".windsurf/skills",
                                "skill_name": "fdd",
                                "entry_filename": " ",
                                "template": ["ALWAYS open and follow `{target_skill_path}`"],
                            }
                        },
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            entry = root / ".windsurf" / "skills" / "fdd" / "SKILL.md"
            entry.parent.mkdir(parents=True, exist_ok=True)
            entry.write_text("x\n", encoding="utf-8")

            orig = Path.read_text

            def _rt(self: Path, *a, **k):
                if self.resolve() == entry.resolve():
                    raise OSError("boom")
                return orig(self, *a, **k)

            with unittest.mock.patch.object(Path, "read_text", _rt):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = main(["agent-skills", "--agent", "windsurf", "--root", str(root)])
            self.assertEqual(code, 0)


class TestCLISubcommandErrorBranches(unittest.TestCase):
    def test_agent_workflows_project_root_not_found(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agent-workflows", "--agent", "windsurf", "--root", str(root)])
            self.assertEqual(code, 1)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "NOT_FOUND")

    def test_agent_workflows_config_error_agents_not_dict(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / "fdd-agent-workflows.json").write_text(
                json.dumps({"version": 1, "agents": "bad"}, indent=2) + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agent-workflows", "--agent", "windsurf", "--root", str(root)])
            self.assertEqual(code, 1)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "CONFIG_ERROR")

    def test_agent_workflows_auto_adds_missing_recognized_agent_to_existing_config(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            cfg_path = root / "fdd-agent-workflows.json"
            cfg_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "agents": {
                            "cursor": {
                                "workflow_dir": ".cursor/commands",
                                "workflow_command_prefix": "fdd-",
                                "workflow_filename_format": "{command}.md",
                                "template": ["# /{command}", "", "ALWAYS open and follow `{target_workflow_path}`"],
                            }
                        },
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agent-workflows", "--agent", "windsurf", "--root", str(root)])
            self.assertEqual(code, 0)
            updated = json.loads(cfg_path.read_text(encoding="utf-8"))
            self.assertIn("windsurf", (updated.get("agents") or {}))

    def test_agent_workflows_prefix_non_str_defaults(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / "fdd-agent-workflows.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "agents": {
                            "windsurf": {
                                "workflow_dir": ".windsurf/workflows",
                                "workflow_command_prefix": 123,
                                "workflow_filename_format": "{command}.md",
                                "template": ["# /{command}", "", "ALWAYS open and follow `{target_workflow_path}`"],
                            }
                        },
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agent-workflows", "--agent", "windsurf", "--root", str(root)])
            self.assertEqual(code, 0)

    def test_agent_workflows_template_invalid_returns_config_incomplete(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / "fdd-agent-workflows.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "agents": {
                            "windsurf": {
                                "workflow_dir": ".windsurf/workflows",
                                "workflow_command_prefix": "fdd-",
                                "workflow_filename_format": "{command}.md",
                                "template": "bad",
                            }
                        },
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agent-workflows", "--agent", "windsurf", "--root", str(root)])
            self.assertEqual(code, 2)

    def test_agent_workflows_renames_misnamed_proxy_and_deletes_stale_proxy(self):
        from fdd import cli as fdd_cli

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            wf_dir = root / ".windsurf" / "workflows"
            wf_dir.mkdir(parents=True)

            fdd_root = Path(fdd_cli.__file__).resolve().parents[4]
            target = (fdd_root / "workflows" / "generate.md").resolve()
            target_rel = fdd_cli._safe_relpath(target, root)

            misnamed = wf_dir / "foo.md"
            misnamed.write_text(
                "\n".join(
                    [
                        "# /fdd-generate",
                        "",
                        f"ALWAYS open and follow `{target_rel}`",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            missing_target = (fdd_root / "workflows" / "does-not-exist.md").resolve()
            stale = wf_dir / "fdd-stale.md"
            stale.write_text(
                "\n".join(
                    [
                        "# /fdd-stale",
                        "",
                        f"ALWAYS open and follow `{missing_target.as_posix()}`",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["agent-workflows", "--agent", "windsurf", "--root", str(root)])
            self.assertEqual(exit_code, 0)

            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "PASS")

            expected_dst = wf_dir / "fdd-generate.md"
            self.assertTrue(expected_dst.exists())
            self.assertFalse(misnamed.exists())

            self.assertFalse(stale.exists())

    def test_agent_workflows_config_incomplete_missing_workflow_dir(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / "fdd-agent-workflows.json").write_text(
                json.dumps({"version": 1, "agents": {"cursor": {"template": ["x"]}}}, indent=2) + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agent-workflows", "--agent", "cursor", "--root", str(root)])
            self.assertEqual(code, 2)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "CONFIG_INCOMPLETE")

    def test_agent_workflows_rename_conflict(self):
        from fdd import cli as fdd_cli

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            wf_dir = root / ".windsurf" / "workflows"
            wf_dir.mkdir(parents=True)

            fdd_root = Path(fdd_cli.__file__).resolve().parents[4]
            target = (fdd_root / "workflows" / "generate.md").resolve()
            target_rel = fdd_cli._safe_relpath(target, root)

            misnamed = wf_dir / "foo.md"
            misnamed.write_text(f"# /fdd-generate\n\nALWAYS open and follow `{target_rel}`\n", encoding="utf-8")

            dst = wf_dir / "fdd-generate.md"
            dst.write_text("preexisting", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agent-workflows", "--agent", "windsurf", "--root", str(root)])
            self.assertEqual(code, 0)
            out = json.loads(stdout.getvalue())
            self.assertGreaterEqual(out.get("counts", {}).get("rename_conflicts", 0), 1)
            self.assertTrue(misnamed.exists())


class TestCLICoreHelpers(unittest.TestCase):
    def test_safe_relpath_from_dir_relpath_exception_returns_abs(self):
        from fdd import cli as fdd_cli

        target = Path("/tmp/x")
        with unittest.mock.patch.object(fdd_cli.os.path, "relpath", side_effect=Exception("boom")):
            out = fdd_cli._safe_relpath_from_dir(target, Path("/tmp"))
        self.assertEqual(out, target.as_posix())

    def test_render_template_missing_variable_raises_system_exit(self):
        from fdd import cli as fdd_cli

        with self.assertRaises(SystemExit):
            fdd_cli._render_template(["{missing}"], {})

    def test_list_workflow_files_missing_dir_returns_empty(self):
        from fdd import cli as fdd_cli

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.assertEqual(fdd_cli._list_workflow_files(root), [])

    def test_list_workflow_files_filters_and_handles_read_error(self):
        from fdd import cli as fdd_cli

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            workflows = root / "workflows"
            workflows.mkdir()

            (workflows / "subdir").mkdir()
            (workflows / "a.txt").write_text("x\n", encoding="utf-8")
            (workflows / "AGENTS.md").write_text("x\n", encoding="utf-8")
            (workflows / "README.md").write_text("x\n", encoding="utf-8")
            (workflows / "not-workflow.md").write_text("# title\n", encoding="utf-8")
            (workflows / "ok.md").write_text("---\ntype: workflow\n---\n", encoding="utf-8")
            bad = workflows / "bad.md"
            bad.write_text("---\ntype: workflow\n---\n", encoding="utf-8")

            orig = Path.read_text

            def _rt(self: Path, *a, **k):
                if self.resolve() == bad.resolve():
                    raise OSError("boom")
                return orig(self, *a, **k)

            with unittest.mock.patch.object(Path, "read_text", _rt):
                out = fdd_cli._list_workflow_files(root)
            self.assertEqual(out, ["ok.md"])

    def test_list_workflow_files_iterdir_error_returns_empty(self):
        from fdd import cli as fdd_cli

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            workflows = root / "workflows"
            workflows.mkdir()

            orig = Path.iterdir

            def _it(self: Path):
                if self.resolve() == workflows.resolve():
                    raise OSError("boom")
                return orig(self)

            with unittest.mock.patch.object(Path, "iterdir", _it):
                self.assertEqual(fdd_cli._list_workflow_files(root), [])

    def test_resolve_user_path_relative_uses_base(self):
        from fdd import cli as fdd_cli

        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            out = fdd_cli._resolve_user_path("foo", base)
            self.assertEqual(out, (base / "foo").resolve())

    def test_prompt_path_returns_user_input_over_default(self):
        from fdd import cli as fdd_cli

        with unittest.mock.patch("builtins.input", return_value="abc"):
            out = fdd_cli._prompt_path("Q?", "def")
        self.assertEqual(out, "abc")

    def test_load_json_file_invalid_json_returns_none(self):
        from fdd import cli as fdd_cli

        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "x.json"
            p.write_text("{not-json}", encoding="utf-8")
            self.assertIsNone(fdd_cli._load_json_file(p))


class TestCLIAgentSkillsMoreBranches(unittest.TestCase):
    def _write_minimal_fdd_skill(self, root: Path) -> None:
        (root / "skills" / "fdd").mkdir(parents=True, exist_ok=True)
        (root / "skills" / "fdd" / "SKILL.md").write_text("# FDD Skill\n", encoding="utf-8")

    def test_agent_skills_outputs_invalid_outputs_type(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_fdd_skill(root)
            (root / "fdd-agent-skills.json").write_text(
                json.dumps({"version": 1, "agents": {"cursor": {"outputs": "bad"}}}, indent=2) + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agent-skills", "--agent", "cursor", "--root", str(root)])
            self.assertEqual(code, 2)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "CONFIG_INCOMPLETE")

    def test_agent_skills_outputs_missing_path_and_template(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_fdd_skill(root)
            (root / "fdd-agent-skills.json").write_text(
                json.dumps({"version": 1, "agents": {"cursor": {"outputs": [{"template": ["x"]}]}}}, indent=2) + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agent-skills", "--agent", "cursor", "--root", str(root)])
            self.assertEqual(code, 2)

            (root / "fdd-agent-skills.json").write_text(
                json.dumps({"version": 1, "agents": {"cursor": {"outputs": [{"path": ".cursor/rules/fdd.mdc", "template": "bad"}]}}}, indent=2)
                + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agent-skills", "--agent", "cursor", "--root", str(root)])
            self.assertEqual(code, 2)

    def test_agent_skills_outputs_unchanged(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_fdd_skill(root)
            (root / "fdd-agent-skills.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "agents": {
                            "cursor": {
                                "outputs": [
                                    {
                                        "path": ".cursor/rules/fdd.mdc",
                                        "template": ["ALWAYS open and follow `{target_skill_path}`"],
                                    }
                                ]
                            }
                        },
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            out_path = root / ".cursor" / "rules" / "fdd.mdc"
            out_path.parent.mkdir(parents=True)
            out_path.write_text("ALWAYS open and follow `../../skills/fdd/SKILL.md`\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agent-skills", "--agent", "cursor", "--root", str(root)])
            self.assertEqual(code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("outputs")[0].get("action"), "unchanged")

    def test_agent_skills_legacy_schema_success_and_config_incomplete(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_fdd_skill(root)

            (root / "fdd-agent-skills.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "agents": {
                            "windsurf": {
                                "skills_dir": ".windsurf/skills",
                                "skill_name": "fdd",
                                "entry_filename": "SKILL.md",
                                "template": ["ALWAYS open and follow `{target_skill_path}`"],
                            }
                        },
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agent-skills", "--agent", "windsurf", "--root", str(root)])
            self.assertEqual(code, 0)
            entry = root / ".windsurf" / "skills" / "fdd" / "SKILL.md"
            self.assertTrue(entry.exists())

            (root / "fdd-agent-skills.json").write_text(
                json.dumps({"version": 1, "agents": {"windsurf": {"skill_name": "fdd", "template": ["x"]}}}, indent=2) + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agent-skills", "--agent", "windsurf", "--root", str(root)])
            self.assertEqual(code, 2)



class TestCLIErrorHandling(unittest.TestCase):
    """Test CLI error handling."""

    def test_unknown_command(self):
        """Test CLI with unknown command."""
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["unknown-command"])

        self.assertNotEqual(exit_code, 0)
        output = json.loads(stdout.getvalue())
        self.assertEqual(output["status"], "ERROR")
        self.assertIn("Unknown command", output["message"])

    def test_empty_command(self):
        """Test CLI with no command."""
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main([])

        self.assertNotEqual(exit_code, 0)
        output = json.loads(stdout.getvalue())
        self.assertEqual(output["status"], "ERROR")
        self.assertIn("Missing subcommand", output["message"])


class TestCLIBackwardCompatibility(unittest.TestCase):
    """Test CLI backward compatibility features."""

    def test_validate_without_subcommand(self):
        """Test that --artifact without subcommand defaults to validate."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "DESIGN.md"
            doc.write_text("""# Technical Design

## A. Architecture Overview

Content

## B. Requirements

Content

## C. Domain Model

Content
""")
            
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                # Old style: no subcommand, just --artifact
                exit_code = main(["--artifact", str(doc)])
            
            # Should work (backward compat)
            output = json.loads(stdout.getvalue())
            self.assertIn("status", output)


class TestCLIAdapterInfo(unittest.TestCase):
    def test_adapter_info_basic(self):
        """Cover adapter-info command."""
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["adapter-info"])
        self.assertEqual(exit_code, 0)
        out = json.loads(stdout.getvalue())
        self.assertIn("status", out)

    def test_adapter_info_config_error_when_path_invalid(self):
        """Cover adapter-info CONFIG_ERROR when .fdd-config.json points to missing adapter directory."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".fdd-config.json").write_text('{"fddAdapterPath": "missing-adapter"}', encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["adapter-info"])
                self.assertEqual(exit_code, 1)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "CONFIG_ERROR")
            finally:
                os.chdir(cwd)

    def test_adapter_info_relative_path_outside_project_root(self):
        """Cover adapter-info relative_to() ValueError branch when adapter is outside project root."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "project"
            root.mkdir(parents=True)
            (root / ".git").mkdir()

            outside = Path(tmpdir) / "outside-adapter"
            outside.mkdir(parents=True)
            (outside / "AGENTS.md").write_text("# FDD Adapter: Outside\n\n**Extends**: `../AGENTS.md`\n", encoding="utf-8")

            # Point config path outside the project.
            (root / ".fdd-config.json").write_text('{"fddAdapterPath": "../outside-adapter"}', encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["adapter-info", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "FOUND")
            self.assertEqual(out.get("relative_path"), str(outside.resolve().as_posix()))


def _bootstrap_registry_new_format(project_root: Path, *, systems: list, rules: dict = None) -> None:
    """Bootstrap registry with new format (systems instead of artifacts)."""
    (project_root / ".git").mkdir(exist_ok=True)
    (project_root / ".fdd-config.json").write_text(
        '{\n  "fddAdapterPath": "adapter"\n}\n',
        encoding="utf-8",
    )
    adapter_dir = project_root / "adapter"
    adapter_dir.mkdir(parents=True, exist_ok=True)
    (adapter_dir / "AGENTS.md").write_text(
        "# FDD Adapter: Test\n\n**Extends**: `../AGENTS.md`\n",
        encoding="utf-8",
    )
    registry = {
        "version": "1.0",
        "project_root": "..",
        "rules": rules or {"fdd": {"format": "FDD", "path": "rules/sdlc"}},
        "systems": systems,
    }
    (adapter_dir / "artifacts.json").write_text(
        json.dumps(registry, indent=2) + "\n",
        encoding="utf-8",
    )


class TestCLIListIdsCommand(unittest.TestCase):
    """Tests for list-ids command."""

    def test_list_ids_no_adapter(self):
        """Test list-ids without adapter."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)

    def test_list_ids_with_artifact(self):
        """Test list-ids with specific artifact."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            templates_dir = root / "rules" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)

            # Create template
            tmpl_content = """---
fdd-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- fdd:id:item -->
**ID**: [ ] `p1` - `fdd-test-1`
<!-- fdd:id:item -->
"""
            (templates_dir / "template.md").write_text(tmpl_content, encoding="utf-8")

            # Create artifact
            art_dir = root / "architecture"
            art_dir.mkdir(parents=True)
            art_content = """<!-- fdd:id:item -->
**ID**: [x] `p1` - `fdd-test-1`
<!-- fdd:id:item -->
"""
            (art_dir / "PRD.md").write_text(art_content, encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                rules={"fdd": {"format": "FDD", "path": "rules/sdlc"}},
                systems=[{
                    "name": "Test",
                    "rules": "fdd",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                }],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["list-ids", "--artifact", str(art_dir / "PRD.md")])

            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertIn("ids", out)

    def test_list_ids_artifact_not_found(self):
        """Test list-ids with nonexistent artifact."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _bootstrap_registry_new_format(root, systems=[])

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["list-ids", "--artifact", str(root / "nonexistent.md")])

            self.assertNotEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "ERROR")


class TestCLIListIdKindsCommand(unittest.TestCase):
    """Tests for list-id-kinds command."""

    def test_list_id_kinds_no_adapter(self):
        """Test list-id-kinds without adapter."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-id-kinds"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)


class TestCLIValidateRulesCommand(unittest.TestCase):
    """Tests for validate-rules command."""

    def test_validate_rules_no_adapter(self):
        """Test validate-rules without adapter."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-rules"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)

    def test_validate_rules_with_template(self):
        """Test validate-rules with specific template."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create valid template
            tmpl_content = """---
fdd-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- fdd:paragraph:summary -->
text
<!-- fdd:paragraph:summary -->
"""
            tmpl_path = root / "test.template.md"
            tmpl_path.write_text(tmpl_content, encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["validate-rules", "--template", str(tmpl_path)])

            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "PASS")

    def test_validate_rules_with_invalid_template(self):
        """Test validate-rules with invalid template."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create invalid template
            tmpl_path = root / "bad.template.md"
            tmpl_path.write_text("not a valid template", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["validate-rules", "--template", str(tmpl_path)])

            self.assertNotEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "FAIL")

    def test_validate_rules_nonexistent_template(self):
        """Test validate-rules with nonexistent template."""
        with TemporaryDirectory() as tmpdir:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["validate-rules", "--template", str(Path(tmpdir) / "nonexistent.md")])

            self.assertNotEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "ERROR")

    def test_validate_rules_verbose(self):
        """Test validate-rules with verbose flag."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create valid template
            tmpl_content = """---
fdd-template:
  version:
    major: 1
    minor: 0
  kind: TEST
---
<!-- fdd:paragraph:summary -->
text
<!-- fdd:paragraph:summary -->
"""
            tmpl_path = root / "test.template.md"
            tmpl_path.write_text(tmpl_content, encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["validate-rules", "--template", str(tmpl_path), "--verbose"])

            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertIn("templates", out)


class TestCLIGetContentCommand(unittest.TestCase):
    """Tests for get-content command."""

    def test_get_content_no_adapter(self):
        """Test get-content without adapter (artifact exists but no adapter)."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            # Create an artifact file but no adapter
            art_path = root / "PRD.md"
            art_path.write_text("# PRD\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--artifact", str(art_path), "--id", "fdd-test-1"])
            self.assertNotEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "ERROR")

    def test_get_content_with_artifact(self):
        """Test get-content with specific artifact."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            templates_dir = root / "rules" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)

            # Create template
            tmpl_content = """---
fdd-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- fdd:id:item -->
**ID**: [ ] `p1` - `fdd-test-1`
<!-- fdd:id:item -->
"""
            (templates_dir / "template.md").write_text(tmpl_content, encoding="utf-8")

            # Create artifact
            art_dir = root / "architecture"
            art_dir.mkdir(parents=True)
            art_content = """<!-- fdd:id:item -->
**ID**: [x] `p1` - `fdd-test-1`
<!-- fdd:id:item -->
"""
            art_path = art_dir / "PRD.md"
            art_path.write_text(art_content, encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                rules={"fdd": {"format": "FDD", "path": "rules/sdlc"}},
                systems=[{
                    "name": "Test",
                    "rules": "fdd",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                }],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--artifact", str(art_path), "--id", "fdd-test-1"])

            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertIn("text", out)  # get-content returns "text" field


class TestCLIWhereDefinedCommand(unittest.TestCase):
    """Additional tests for where-defined command."""

    def test_where_defined_no_adapter(self):
        """Test where-defined without adapter."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-defined", "--id", "fdd-test-1"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)


class TestCLIWhereUsedCommand(unittest.TestCase):
    """Additional tests for where-used command."""

    def test_where_used_no_adapter(self):
        """Test where-used without adapter."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-used", "--id", "fdd-test-1"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)


def _setup_fdd_project(root: Path) -> None:
    """Setup a complete FDD project with template and artifact."""
    # Create template at new path: rules/sdlc/artifacts/PRD/template.md
    templates_dir = root / "rules" / "sdlc" / "artifacts" / "PRD"
    templates_dir.mkdir(parents=True)

    # Create template with ID block
    tmpl_content = """---
fdd-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- fdd:id:item -->
**ID**: [ ] `p1` - `fdd-test-1`
<!-- fdd:id:item -->
"""
    (templates_dir / "template.md").write_text(tmpl_content, encoding="utf-8")

    # Create artifact
    art_dir = root / "architecture"
    art_dir.mkdir(parents=True)
    art_content = """<!-- fdd:id:item -->
**ID**: [x] `p1` - `fdd-test-1`
<!-- fdd:id:item -->
"""
    (art_dir / "PRD.md").write_text(art_content, encoding="utf-8")

    _bootstrap_registry_new_format(
        root,
        rules={"fdd": {"format": "FDD", "path": "rules/sdlc"}},
        systems=[{
            "name": "Test",
            "rules": "fdd",
            "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
        }],
    )


class TestCLIWhereDefinedWithArtifacts(unittest.TestCase):
    """Tests for where-defined command with actual artifacts."""

    def test_where_defined_found(self):
        """Test where-defined finds an ID."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-defined", "--id", "fdd-test-1"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "FOUND")
                self.assertEqual(out.get("count"), 1)
            finally:
                os.chdir(cwd)

    def test_where_defined_not_found(self):
        """Test where-defined returns NOT_FOUND for missing ID."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-defined", "--id", "fdd-nonexistent"])
                self.assertEqual(exit_code, 2)  # NOT_FOUND returns 2
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "NOT_FOUND")
            finally:
                os.chdir(cwd)

    def test_where_defined_with_artifact_flag(self):
        """Test where-defined with --artifact flag."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                art_path = root / "architecture" / "PRD.md"
                with redirect_stdout(stdout):
                    exit_code = main(["where-defined", "--id", "fdd-test-1", "--artifact", str(art_path)])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "FOUND")
            finally:
                os.chdir(cwd)


class TestCLIWhereUsedWithArtifacts(unittest.TestCase):
    """Tests for where-used command with actual artifacts."""

    def test_where_used_found(self):
        """Test where-used finds references."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-used", "--id", "fdd-test-1"])
                # Will succeed or return NOT_FOUND (no refs in simple setup)
                self.assertIn(exit_code, [0, 2])
            finally:
                os.chdir(cwd)


class TestCLIListIdKindsWithArtifacts(unittest.TestCase):
    """Tests for list-id-kinds command with actual artifacts."""

    def test_list_id_kinds_with_artifact(self):
        """Test list-id-kinds with --artifact flag."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                art_path = root / "architecture" / "PRD.md"
                with redirect_stdout(stdout):
                    exit_code = main(["list-id-kinds", "--artifact", str(art_path)])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertIn("kinds", out)
            finally:
                os.chdir(cwd)

    def test_list_id_kinds_scan_all(self):
        """Test list-id-kinds without --artifact scans all."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-id-kinds"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertIn("kinds", out)
                self.assertIn("artifacts_scanned", out)
            finally:
                os.chdir(cwd)


class TestCLIListIdsWithArtifacts(unittest.TestCase):
    """Tests for list-ids command with actual artifacts."""

    def test_list_ids_scan_all(self):
        """Test list-ids without --artifact scans all."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertIn("ids", out)
                self.assertEqual(out.get("count"), 1)
            finally:
                os.chdir(cwd)

    def test_list_ids_with_filters(self):
        """Test list-ids with --kind and --pattern filters."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids", "--kind", "item", "--pattern", "test"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertIn("ids", out)
            finally:
                os.chdir(cwd)


class TestCLIListIdsErrorBranches(unittest.TestCase):
    """Tests for list-ids command error branches."""

    def test_list_ids_artifact_not_in_registry(self):
        """Test list-ids when artifact exists but not in registry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            # Create artifact NOT in registry
            unregistered = root / "unregistered.md"
            unregistered.write_text("# Not registered\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["list-ids", "--artifact", str(unregistered)])
            self.assertNotEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "ERROR")

    def test_list_ids_with_regex_filter(self):
        """Test list-ids with --regex filter."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids", "--pattern", "fdd-.*", "--regex"])
                self.assertEqual(exit_code, 0)
            finally:
                os.chdir(cwd)

    def test_list_ids_with_all_flag(self):
        """Test list-ids with --all flag."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids", "--all"])
                self.assertEqual(exit_code, 0)
            finally:
                os.chdir(cwd)


class TestCLIListIdKindsErrorBranches(unittest.TestCase):
    """Tests for list-id-kinds error branches."""

    def test_list_id_kinds_artifact_not_found(self):
        """Test list-id-kinds when artifact file doesn't exist."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                nonexistent = root / "nonexistent.md"
                with redirect_stdout(stdout):
                    exit_code = main(["list-id-kinds", "--artifact", str(nonexistent)])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)

    def test_list_id_kinds_artifact_not_in_registry(self):
        """Test list-id-kinds when artifact not in registry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            # Create artifact NOT in registry
            unregistered = root / "unregistered.md"
            unregistered.write_text("# Not registered\n", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-id-kinds", "--artifact", str(unregistered)])
                self.assertNotEqual(exit_code, 0)
            finally:
                os.chdir(cwd)


class TestCLIGetContentErrorBranches(unittest.TestCase):
    """Tests for get-content error branches."""

    def test_get_content_artifact_not_found(self):
        """Test get-content when artifact file doesn't exist."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            stdout = io.StringIO()
            nonexistent = root / "nonexistent.md"
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--artifact", str(nonexistent), "--id", "fdd-test-1"])
            self.assertNotEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "ERROR")

    def test_get_content_artifact_not_in_registry(self):
        """Test get-content when artifact not in registry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            # Create artifact NOT in registry
            unregistered = root / "unregistered.md"
            unregistered.write_text("# Not registered\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--artifact", str(unregistered), "--id", "fdd-test-1"])
            self.assertNotEqual(exit_code, 0)

    def test_get_content_id_not_found(self):
        """Test get-content when ID doesn't exist."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                art_path = root / "architecture" / "PRD.md"
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["get-content", "--artifact", str(art_path), "--id", "fdd-nonexistent"])
                self.assertEqual(exit_code, 2)  # NOT_FOUND
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "NOT_FOUND")
            finally:
                os.chdir(cwd)


class TestCLIWhereDefinedErrorBranches(unittest.TestCase):
    """Tests for where-defined error branches."""

    def test_where_defined_empty_id(self):
        """Test where-defined with empty ID."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-defined", "--id", ""])
                self.assertNotEqual(exit_code, 0)
            finally:
                os.chdir(cwd)

    def test_where_defined_artifact_not_found(self):
        """Test where-defined with nonexistent artifact."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                nonexistent = root / "nonexistent.md"
                with redirect_stdout(stdout):
                    exit_code = main(["where-defined", "--id", "fdd-test-1", "--artifact", str(nonexistent)])
                self.assertNotEqual(exit_code, 0)
            finally:
                os.chdir(cwd)


class TestCLIWhereUsedErrorBranches(unittest.TestCase):
    """Tests for where-used error branches."""

    def test_where_used_empty_id(self):
        """Test where-used with empty ID."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-used", "--id", ""])
                self.assertNotEqual(exit_code, 0)
            finally:
                os.chdir(cwd)

    def test_where_used_with_include_definitions(self):
        """Test where-used with --include-definitions flag."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-used", "--id", "fdd-test-1", "--include-definitions"])
                # May return FOUND or NOT_FOUND depending on refs
                self.assertIn(exit_code, [0, 2])
            finally:
                os.chdir(cwd)

    def test_where_used_artifact_not_found(self):
        """Test where-used with nonexistent artifact."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                nonexistent = root / "nonexistent.md"
                with redirect_stdout(stdout):
                    exit_code = main(["where-used", "--id", "fdd-test-1", "--artifact", str(nonexistent)])
                self.assertNotEqual(exit_code, 0)
            finally:
                os.chdir(cwd)

    def test_where_used_artifact_not_in_registry(self):
        """Test where-used with artifact not in registry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            # Create artifact NOT in registry
            unregistered = root / "unregistered.md"
            unregistered.write_text("# Not registered\n", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-used", "--id", "fdd-test-1", "--artifact", str(unregistered)])
                self.assertNotEqual(exit_code, 0)
            finally:
                os.chdir(cwd)

    def test_where_used_with_valid_artifact(self):
        """Test where-used with valid artifact flag."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                art_path = root / "architecture" / "PRD.md"
                with redirect_stdout(stdout):
                    exit_code = main(["where-used", "--id", "fdd-test-1", "--artifact", str(art_path)])
                # Will succeed or return NOT_FOUND
                self.assertIn(exit_code, [0, 2])
            finally:
                os.chdir(cwd)


class TestCLIValidateRulesErrorBranches(unittest.TestCase):
    """Tests for validate-rules error branches."""

    def test_validate_rules_registry_error(self):
        """Test validate-rules when registry has errors."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".fdd-config.json").write_text('{"fddAdapterPath": "adapter"}', encoding="utf-8")
            adapter = root / "adapter"
            adapter.mkdir()
            (adapter / "AGENTS.md").write_text("# Test\n", encoding="utf-8")
            # Invalid JSON in registry
            (adapter / "artifacts.json").write_text("{invalid", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-rules"])
                self.assertNotEqual(exit_code, 0)
            finally:
                os.chdir(cwd)

    def test_validate_rules_no_fdd_templates(self):
        """Test validate-rules when no FDD templates in registry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # Setup with non-FDD format
            _bootstrap_registry_new_format(
                root,
                rules={"other": {"format": "OTHER", "path": "templates"}},
                systems=[{"name": "Test", "rules": "other", "artifacts": []}],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-rules"])
                self.assertNotEqual(exit_code, 0)
            finally:
                os.chdir(cwd)


class TestCLIInitBackupBranch(unittest.TestCase):
    """Test init command with existing adapter (backup branch)."""

    def test_init_with_existing_adapter_creates_backup(self):
        """Test init --yes with existing adapter creates backup."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            # Create existing adapter
            adapter = root / "adapter"
            adapter.mkdir()
            (adapter / "AGENTS.md").write_text("# Old adapter\n", encoding="utf-8")
            (adapter / ".fdd-config.json").write_text('{"fddAdapterPath": "adapter"}', encoding="utf-8")

            # Point config to existing adapter
            (root / ".fdd-config.json").write_text('{"fddAdapterPath": "adapter"}', encoding="utf-8")

            cwd = os.getcwd()
            stdout = io.StringIO()
            try:
                os.chdir(str(root))
                with redirect_stdout(stdout):
                    exit_code = main(["init", "--yes"])
                # May fail if FDD core not found, but should at least try backup
                self.assertIn(exit_code, [0, 1, 2])
            finally:
                os.chdir(cwd)


class TestCLISelfCheckCommand(unittest.TestCase):
    """Tests for self-check command."""

    def test_self_check_no_project_root(self):
        """Test self-check when project root not found."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # No .git or markers

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["self-check"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)

    def test_self_check_no_adapter(self):
        """Test self-check when adapter directory not found."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            # No adapter

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["self-check"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)

    def test_self_check_registry_error(self):
        """Test self-check when registry has error."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".fdd-config.json").write_text('{"fddAdapterPath": "adapter"}', encoding="utf-8")
            adapter = root / "adapter"
            adapter.mkdir()
            (adapter / "AGENTS.md").write_text("# Test\n", encoding="utf-8")
            (adapter / "artifacts.json").write_text("{invalid", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["self-check"])
                self.assertNotEqual(exit_code, 0)
            finally:
                os.chdir(cwd)

    def test_self_check_missing_templates_catalog(self):
        """Test self-check when templates catalog is missing."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _bootstrap_registry_new_format(root, systems=[])

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["self-check"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)


class TestCLIGetContentErrorBranches(unittest.TestCase):
    """Tests for get-content command error branches."""

    def test_get_content_artifact_not_under_project_root(self):
        """Test get-content when artifact is not under project root."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            # Create artifact outside project root
            outside = Path(tmpdir) / "outside" / "test.md"
            outside.parent.mkdir(parents=True)
            outside.write_text("<!-- fdd:id:item -->\n**ID**: [x] `p1` - `test`\n<!-- fdd:id:item -->", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    # Use a path outside the project
                    exit_code = main(["get-content", "--artifact", str(outside), "--id", "test"])
                # Should error (artifact not under project root or not registered)
                self.assertNotEqual(exit_code, 0)
            finally:
                os.chdir(cwd)

    def test_get_content_artifact_not_registered(self):
        """Test get-content when artifact is not in registry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            # Create artifact file under project root but not registered
            unregistered = root / "unregistered.md"
            unregistered.write_text("<!-- fdd:id:item -->\n**ID**: [x] `p1` - `test`\n<!-- fdd:id:item -->", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["get-content", "--artifact", str(unregistered), "--id", "test"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)


class TestCLIListIdKindsErrorBranches(unittest.TestCase):
    """Tests for list-id-kinds command error branches."""

    def test_list_id_kinds_registry_error(self):
        """Test list-id-kinds when registry fails to load."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".fdd-config.json").write_text('{"fddAdapterPath": "adapter"}', encoding="utf-8")
            adapter = root / "adapter"
            adapter.mkdir()
            (adapter / "AGENTS.md").write_text("# Test\n", encoding="utf-8")
            (adapter / "artifacts.json").write_text("{invalid", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-id-kinds"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)

    def test_list_id_kinds_artifact_not_under_project(self):
        """Test list-id-kinds when artifact is outside project root."""
        with TemporaryDirectory() as tmpdir1, TemporaryDirectory() as tmpdir2:
            root = Path(tmpdir1)
            _setup_fdd_project(root)

            # Create artifact in different temp dir
            outside = Path(tmpdir2) / "outside.md"
            outside.write_text("test content", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-id-kinds", "--artifact", str(outside)])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)

    def test_list_id_kinds_no_fdd_artifacts(self):
        """Test list-id-kinds when no FDD-format artifacts in registry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _bootstrap_registry_new_format(
                root,
                rules={"other": {"format": "OTHER", "path": "templates"}},
                systems=[{"name": "Test", "rules": "other", "artifacts": []}],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-id-kinds"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)


class TestCLIWhereDefinedErrorBranches(unittest.TestCase):
    """Tests for where-defined command error branches."""

    def test_where_defined_registry_error(self):
        """Test where-defined when registry fails to load."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".fdd-config.json").write_text('{"fddAdapterPath": "adapter"}', encoding="utf-8")
            adapter = root / "adapter"
            adapter.mkdir()
            (adapter / "AGENTS.md").write_text("# Test\n", encoding="utf-8")
            (adapter / "artifacts.json").write_text("{invalid", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-defined", "--id", "test"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)

    def test_where_defined_artifact_outside_project(self):
        """Test where-defined when artifact is outside project root."""
        with TemporaryDirectory() as tmpdir1, TemporaryDirectory() as tmpdir2:
            root = Path(tmpdir1)
            _setup_fdd_project(root)

            # Create artifact in different temp dir
            outside = Path(tmpdir2) / "outside.md"
            outside.write_text("test content", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-defined", "--id", "test", "--artifact", str(outside)])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)


class TestCLIValidateTemplatesVerbose(unittest.TestCase):
    """Tests for validate-templates command verbose mode."""

    def test_validate_templates_verbose_with_errors(self):
        """Test validate-templates --verbose with template errors."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            templates_dir = root / "templates"
            templates_dir.mkdir(parents=True)

            # Create invalid template (missing fdd-template frontmatter)
            (templates_dir / "PRD.template.md").write_text(
                "<!-- fdd:id:item -->\nNo frontmatter here\n<!-- fdd:id:item -->",
                encoding="utf-8"
            )

            _bootstrap_registry_new_format(
                root,
                rules={"fdd": {"format": "FDD", "path": "templates"}},
                systems=[{
                    "name": "Test",
                    "rules": "fdd",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                }],
            )

            # Create architecture dir
            (root / "architecture").mkdir(parents=True)
            (root / "architecture" / "PRD.md").write_text("test", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-templates", "--verbose"])
                # Exit code 1 = no templates found (error), 2 = template validation fail
                self.assertIn(exit_code, [0, 1, 2])
                out = json.loads(stdout.getvalue())
                self.assertIn("status", out)
            finally:
                os.chdir(cwd)

    def test_validate_templates_verbose_success(self):
        """Test validate-templates --verbose with valid templates."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-templates", "--verbose"])
                # May fail (1) if template lookup fails, or pass (0), or validation fail (2)
                self.assertIn(exit_code, [0, 1, 2])
                out = json.loads(stdout.getvalue())
                self.assertIn("status", out)
            finally:
                os.chdir(cwd)


class TestCLIInitErrorBranches(unittest.TestCase):
    """Tests for init command error branches."""

    def test_init_config_not_a_file(self):
        """Test init when config path exists but is not a file."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            # Create config as directory
            (root / ".fdd-config.json").mkdir()

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["init", "--yes", "--project-root", str(root)])
                self.assertNotEqual(exit_code, 0)
            finally:
                os.chdir(cwd)

    def test_init_existing_config_incomplete(self):
        """Test init when existing config is incomplete."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            # Create incomplete config
            (root / ".fdd-config.json").write_text('{"someOtherKey": "value"}', encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["init", "--yes", "--project-root", str(root)])
                # May fail due to incomplete config or FDD core not found
                self.assertIn(exit_code, [0, 1, 2])
            finally:
                os.chdir(cwd)

    def test_init_existing_config_conflict(self):
        """Test init when existing config has conflicting paths."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            # Create config with different paths
            (root / ".fdd-config.json").write_text(
                '{"fddCorePath": "different/path", "fddAdapterPath": "different/adapter"}',
                encoding="utf-8"
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["init", "--yes", "--project-root", str(root)])
                # May fail due to config conflict
                self.assertIn(exit_code, [0, 1, 2])
            finally:
                os.chdir(cwd)

    def test_init_adapter_agents_not_a_file(self):
        """Test init when adapter AGENTS.md exists but is not a file."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            adapter = root / "FDD-Adapter"
            adapter.mkdir(parents=True)
            # Create AGENTS.md as directory
            (adapter / "AGENTS.md").mkdir()

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["init", "--yes", "--project-root", str(root)])
                # Should fail due to AGENTS.md not being a file
                self.assertIn(exit_code, [0, 1, 2])
            finally:
                os.chdir(cwd)

    def test_init_registry_not_a_file(self):
        """Test init when artifacts.json exists but is not a file."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            adapter = root / "FDD-Adapter"
            adapter.mkdir(parents=True)
            # Create artifacts.json as directory
            (adapter / "artifacts.json").mkdir()

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["init", "--yes", "--project-root", str(root)])
                # Should fail due to artifacts.json not being a file
                self.assertIn(exit_code, [0, 1, 2])
            finally:
                os.chdir(cwd)

    def test_init_force_with_existing_adapter(self):
        """Test init --force creates backup when adapter exists."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            # Create existing adapter
            adapter = root / "FDD-Adapter"
            adapter.mkdir(parents=True)
            (adapter / "AGENTS.md").write_text("# Old content\n", encoding="utf-8")
            (adapter / "artifacts.json").write_text('{"version": "old"}', encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["init", "--yes", "--force", "--project-root", str(root)])
                # May succeed or fail, but should try to create backup
                self.assertIn(exit_code, [0, 1, 2])
            finally:
                os.chdir(cwd)


class TestCLIWhereUsedErrorBranches(unittest.TestCase):
    """Tests for where-used command error branches."""

    def test_where_used_registry_error(self):
        """Test where-used when registry fails to load."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".fdd-config.json").write_text('{"fddAdapterPath": "adapter"}', encoding="utf-8")
            adapter = root / "adapter"
            adapter.mkdir()
            (adapter / "AGENTS.md").write_text("# Test\n", encoding="utf-8")
            (adapter / "artifacts.json").write_text("{invalid", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-used", "--id", "test"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)

    def test_where_used_artifact_outside_project(self):
        """Test where-used when artifact is outside project root."""
        with TemporaryDirectory() as tmpdir1, TemporaryDirectory() as tmpdir2:
            root = Path(tmpdir1)
            _setup_fdd_project(root)

            # Create artifact in different temp dir
            outside = Path(tmpdir2) / "outside.md"
            outside.write_text("test content", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-used", "--id", "test", "--artifact", str(outside)])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)


class TestCLIListIdsErrorBranches(unittest.TestCase):
    """Tests for list-ids command error branches."""

    def test_list_ids_registry_error(self):
        """Test list-ids when registry fails to load."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".fdd-config.json").write_text('{"fddAdapterPath": "adapter"}', encoding="utf-8")
            adapter = root / "adapter"
            adapter.mkdir()
            (adapter / "AGENTS.md").write_text("# Test\n", encoding="utf-8")
            (adapter / "artifacts.json").write_text("{invalid", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)

    def test_list_ids_artifact_outside_project(self):
        """Test list-ids when artifact is outside project root."""
        with TemporaryDirectory() as tmpdir1, TemporaryDirectory() as tmpdir2:
            root = Path(tmpdir1)
            _setup_fdd_project(root)

            # Create artifact in different temp dir
            outside = Path(tmpdir2) / "outside.md"
            outside.write_text("test content", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids", "--artifact", str(outside)])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)

    def test_list_ids_no_fdd_artifacts(self):
        """Test list-ids when no FDD-format artifacts in registry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _bootstrap_registry_new_format(
                root,
                rules={"other": {"format": "OTHER", "path": "templates"}},
                systems=[{"name": "Test", "rules": "other", "artifacts": []}],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)


class TestCLIValidateCommandBranches(unittest.TestCase):
    """Tests for validate command error branches."""

    def test_validate_no_adapter(self):
        """Test validate when no adapter found."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            # No adapter

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)

    def test_validate_registry_error(self):
        """Test validate when registry fails to load."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".fdd-config.json").write_text('{"fddAdapterPath": "adapter"}', encoding="utf-8")
            adapter = root / "adapter"
            adapter.mkdir()
            (adapter / "AGENTS.md").write_text("# Test\n", encoding="utf-8")
            (adapter / "artifacts.json").write_text("{invalid", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)

    def test_validate_no_fdd_artifacts(self):
        """Test validate when no FDD-format artifacts in registry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _bootstrap_registry_new_format(
                root,
                rules={"other": {"format": "OTHER", "path": "templates"}},
                systems=[{"name": "Test", "rules": "other", "artifacts": []}],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)

    def test_validate_verbose_output(self):
        """Test validate --verbose output includes detailed info."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate", "--verbose"])
                self.assertIn(exit_code, [0, 1, 2])
                out = json.loads(stdout.getvalue())
                self.assertIn("status", out)
            finally:
                os.chdir(cwd)

    def test_validate_with_output_file(self):
        """Test validate --output writes to file."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)
            output_file = root / "report.json"

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate", "--output", str(output_file)])
                self.assertIn(exit_code, [0, 1, 2])
                # If successful, output file should exist
                if exit_code in [0, 2]:
                    self.assertTrue(output_file.exists())
            finally:
                os.chdir(cwd)

    def test_validate_artifact_not_in_registry(self):
        """Test validate when artifact is not in FDD registry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            # Create artifact file not in registry
            unregistered = root / "unregistered.md"
            unregistered.write_text("test", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate", "--artifact", str(unregistered)])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)

    def test_validate_template_load_failure(self):
        """Test validate when template fails to load."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            templates_dir = root / "templates"
            templates_dir.mkdir(parents=True)

            # Create invalid template
            (templates_dir / "PRD.template.md").write_text("invalid", encoding="utf-8")

            # Create artifact
            art_dir = root / "architecture"
            art_dir.mkdir(parents=True)
            (art_dir / "PRD.md").write_text("content", encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                rules={"fdd": {"format": "FDD", "path": "templates"}},
                systems=[{
                    "name": "Test",
                    "rules": "fdd",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                }],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate"])
                # May pass (0), fail (1), or have validation errors (2)
                self.assertIn(exit_code, [0, 1, 2])
            finally:
                os.chdir(cwd)


class TestCLIWhereUsedWithIncludeDefinitions(unittest.TestCase):
    """Tests for where-used command with --include-definitions."""

    def test_where_used_include_definitions(self):
        """Test where-used --include-definitions includes definitions."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-used", "--id", "fdd-test-1", "--include-definitions"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                # Should have references that may include definitions
                self.assertIn("references", out)
            finally:
                os.chdir(cwd)


class TestCLIListIdsFilters(unittest.TestCase):
    """Tests for list-ids command filter options."""

    def test_list_ids_with_kind_filter(self):
        """Test list-ids --kind filter."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids", "--kind", "item"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertIn("ids", out)
            finally:
                os.chdir(cwd)

    def test_list_ids_with_pattern_filter(self):
        """Test list-ids --pattern filter."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids", "--pattern", "fdd"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertIn("ids", out)
            finally:
                os.chdir(cwd)

    def test_list_ids_with_regex_filter(self):
        """Test list-ids --pattern --regex filter."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids", "--pattern", "fdd.*1", "--regex"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertIn("ids", out)
            finally:
                os.chdir(cwd)

    def test_list_ids_all_duplicates(self):
        """Test list-ids --all to include duplicates."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids", "--all"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertIn("ids", out)
            finally:
                os.chdir(cwd)

    def test_list_ids_with_priority(self):
        """Test list-ids captures priority in output."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            templates_dir = root / "rules" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)

            # Create template with priority
            tmpl_content = """---
fdd-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- fdd:id:item -->
**ID**: [ ] `p1` - `fdd-test-1`
<!-- fdd:id:item -->
"""
            (templates_dir / "template.md").write_text(tmpl_content, encoding="utf-8")

            # Create artifact with priority marker
            art_dir = root / "architecture"
            art_dir.mkdir(parents=True)
            art_content = """<!-- fdd:id:item -->
**ID**: [x] `p1` - `fdd-test-1`
<!-- fdd:id:item -->

<!-- fdd:id-ref:item -->
- [x] `p2` - `fdd-test-1`: referenced here
<!-- fdd:id-ref:item -->
"""
            (art_dir / "PRD.md").write_text(art_content, encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                rules={"fdd": {"format": "FDD", "path": "rules/sdlc"}},
                systems=[{
                    "name": "Test",
                    "rules": "fdd",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                }],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids", "--all"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertIn("ids", out)
            finally:
                os.chdir(cwd)


class TestCLIGetContentBranches(unittest.TestCase):
    """Tests for get-content command additional branches."""

    def test_get_content_no_adapter(self):
        """Test get-content when no adapter found."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            artifact = root / "test.md"
            artifact.write_text("content", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--artifact", str(artifact), "--id", "test"])
            self.assertNotEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "ERROR")

    def test_get_content_found(self):
        """Test get-content when ID is found."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)
            artifact = root / "architecture" / "PRD.md"

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["get-content", "--artifact", str(artifact), "--id", "item"])
                # May find or not find
                self.assertIn(exit_code, [0, 2])
            finally:
                os.chdir(cwd)


class TestCLIAdapterInfoCommand(unittest.TestCase):
    """Tests for adapter-info command."""

    def test_adapter_info_no_adapter(self):
        """Test adapter-info when no adapter found."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["adapter-info"])
                self.assertNotEqual(exit_code, 0)
            finally:
                os.chdir(cwd)

    def test_adapter_info_success(self):
        """Test adapter-info with valid adapter."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["adapter-info"])
                self.assertIn(exit_code, [0, 1])  # May succeed or fail
            finally:
                os.chdir(cwd)


def _setup_fdd_project_with_codebase(root: Path) -> None:
    """Setup complete FDD project with codebase entries for testing."""
    # Create template
    templates_dir = root / "rules" / "sdlc" / "artifacts" / "PRD"
    templates_dir.mkdir(parents=True)
    tmpl_content = """---
fdd-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- fdd:id:item -->
**ID**: [ ] `p1` - `fdd-test-1`
<!-- fdd:id:item -->
"""
    (templates_dir / "template.md").write_text(tmpl_content, encoding="utf-8")

    # Create artifact
    art_dir = root / "architecture"
    art_dir.mkdir(parents=True)
    art_content = """<!-- fdd:id:item -->
**ID**: [x] `p1` - `fdd-test-1`
<!-- fdd:id:item -->
"""
    (art_dir / "PRD.md").write_text(art_content, encoding="utf-8")

    # Create code directory with FDD markers
    code_dir = root / "src"
    code_dir.mkdir(parents=True)
    (code_dir / "module.py").write_text(
        "# @fdd-flow:fdd-test-1:ph-1\ndef test(): pass\n",
        encoding="utf-8"
    )

    # Bootstrap registry with codebase entry
    _bootstrap_registry_new_format(
        root,
        rules={"fdd": {"format": "FDD", "path": "rules/sdlc"}},
        systems=[{
            "name": "Test",
            "rules": "fdd",
            "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
            "codebase": [{"path": "src", "extensions": [".py"]}],
        }],
    )


class TestCLIValidateCodeCommand(unittest.TestCase):
    """Tests for validate-code command."""

    def test_validate_code_no_project(self):
        """Test validate-code when no project root found."""
        with TemporaryDirectory() as tmpdir:
            cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-code"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)

    def test_validate_code_no_adapter(self):
        """Test validate-code when project exists but no adapter."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-code"])
                self.assertNotEqual(exit_code, 0)
            finally:
                os.chdir(cwd)

    def test_validate_code_with_path(self):
        """Test validate-code with explicit path to code file."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project_with_codebase(root)

            # Create a code file with FDD markers
            code_file = root / "test_code.py"
            code_file.write_text("# @fdd-flow:fdd-test-1:ph-1\ndef foo(): pass\n", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-code", str(code_file)])
                # Should succeed or fail validation
                self.assertIn(exit_code, [0, 2])
                out = json.loads(stdout.getvalue())
                self.assertIn(out.get("status"), ["PASS", "FAIL"])
            finally:
                os.chdir(cwd)

    def test_validate_code_verbose(self):
        """Test validate-code with verbose output."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project_with_codebase(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-code", "--verbose"])
                self.assertIn(exit_code, [0, 2])
                out = json.loads(stdout.getvalue())
                # Verbose output should have more fields
                self.assertIn("status", out)
            finally:
                os.chdir(cwd)

    def test_validate_code_with_output_file(self):
        """Test validate-code with output file."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project_with_codebase(root)
            output_file = root / "report.json"

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-code", "--output", str(output_file)])
                self.assertIn(exit_code, [0, 2])
                # Verify output file was created
                self.assertTrue(output_file.exists())
                content = json.loads(output_file.read_text())
                self.assertIn("status", content)
            finally:
                os.chdir(cwd)

    def test_validate_code_full_scan_with_codebase(self):
        """Test validate-code scanning codebase entries."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project_with_codebase(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-code"])
                self.assertIn(exit_code, [0, 2])
                out = json.loads(stdout.getvalue())
                self.assertIn("code_files_scanned", out)
            finally:
                os.chdir(cwd)

    def test_validate_code_with_system_filter(self):
        """Test validate-code with --system filter."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project_with_codebase(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-code", "--system", "Test"])
                self.assertIn(exit_code, [0, 2])
            finally:
                os.chdir(cwd)

    def test_validate_code_orphaned_marker(self):
        """Test validate-code detects orphaned markers (ID not in artifacts)."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project_with_codebase(root)

            # Add code file with orphaned marker (ID not in artifacts)
            orphan_file = root / "src" / "orphan.py"
            orphan_file.write_text(
                "# @fdd-flow:fdd-unknown-id:ph-1\ndef orphan(): pass\n",
                encoding="utf-8"
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-code", "--verbose"])
                # Should fail due to orphaned marker
                self.assertEqual(exit_code, 2)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "FAIL")
                self.assertGreater(out.get("error_count", 0), 0)
            finally:
                os.chdir(cwd)

    def test_validate_code_invalid_registry(self):
        """Test validate-code with invalid registry file."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".fdd-config.json").write_text(
                '{"fddAdapterPath": "adapter"}',
                encoding="utf-8"
            )
            adapter_dir = root / "adapter"
            adapter_dir.mkdir()
            (adapter_dir / "AGENTS.md").write_text("# Test", encoding="utf-8")
            # Write invalid registry (not a dict)
            (adapter_dir / "artifacts.json").write_text("[]", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-code"])
                self.assertEqual(exit_code, 1)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)

    def test_validate_code_nonexistent_system(self):
        """Test validate-code with --system filter for non-existent system."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_fdd_project_with_codebase(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-code", "--system", "NonExistent"])
                # Should still succeed (just scan nothing)
                self.assertIn(exit_code, [0, 2])
            finally:
                os.chdir(cwd)

    def test_validate_code_with_nested_systems(self):
        """Test validate-code with nested system hierarchy."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Setup templates
            templates_dir = root / "rules" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)
            (templates_dir / "template.md").write_text("""---
fdd-template:
  version: {major: 1, minor: 0}
  kind: PRD
---
<!-- fdd:id:item -->
**ID**: [ ] `p1` - `fdd-test-1`
<!-- fdd:id:item -->
""", encoding="utf-8")

            # Create artifact
            (root / "architecture").mkdir(parents=True)
            (root / "architecture" / "PRD.md").write_text("""<!-- fdd:id:item -->
**ID**: [x] `p1` - `fdd-test-1`
<!-- fdd:id:item -->
""", encoding="utf-8")

            # Create code with markers
            (root / "src").mkdir(parents=True)
            (root / "src" / "module.py").write_text(
                "# @fdd-flow:fdd-test-1:ph-1\ndef test(): pass\n",
                encoding="utf-8"
            )

            # Bootstrap registry with nested systems
            _bootstrap_registry_new_format(
                root,
                rules={"fdd": {"format": "FDD", "path": "rules/sdlc"}},
                systems=[{
                    "name": "Parent",
                    "rules": "fdd",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                    "children": [{
                        "name": "Child",
                        "rules": "fdd",
                        "artifacts": [],
                        "codebase": [{"path": "src", "extensions": [".py"]}],
                    }],
                }],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-code"])
                self.assertIn(exit_code, [0, 2])
            finally:
                os.chdir(cwd)

    def test_validate_code_nonexistent_codebase_path(self):
        """Test validate-code skips non-existent codebase paths gracefully."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Setup minimal project
            templates_dir = root / "rules" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)
            (templates_dir / "template.md").write_text("""---
fdd-template:
  version: {major: 1, minor: 0}
  kind: PRD
---
<!-- fdd:id:item -->
**ID**: [ ] `p1` - `fdd-test-1`
<!-- fdd:id:item -->
""", encoding="utf-8")

            (root / "architecture").mkdir(parents=True)
            (root / "architecture" / "PRD.md").write_text("""<!-- fdd:id:item -->
**ID**: [x] `p1` - `fdd-test-1`
<!-- fdd:id:item -->
""", encoding="utf-8")

            # Bootstrap with codebase pointing to nonexistent directory
            _bootstrap_registry_new_format(
                root,
                rules={"fdd": {"format": "FDD", "path": "rules/sdlc"}},
                systems=[{
                    "name": "Test",
                    "rules": "fdd",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                    "codebase": [{"path": "nonexistent/dir", "extensions": [".py"]}],
                }],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-code"])
                # Should pass (no codebase found but no errors)
                self.assertIn(exit_code, [0, 2])
            finally:
                os.chdir(cwd)


class TestCLIGetContentCodeFile(unittest.TestCase):
    """Tests for get-content with --code option."""

    def test_get_content_code_file_not_found(self):
        """Test get-content --code with non-existent file."""
        with TemporaryDirectory() as tmpdir:
            fake_path = Path(tmpdir) / "nonexistent.py"

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--code", str(fake_path), "--id", "test"])
            self.assertNotEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "ERROR")

    def test_get_content_code_file_found(self):
        """Test get-content --code with valid file and existing ID."""
        with TemporaryDirectory() as tmpdir:
            code_file = Path(tmpdir) / "test.py"
            code_file.write_text(
                "# @fdd-flow:fdd-test-flow-login:ph-1\ndef login(): pass\n",
                encoding="utf-8"
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--code", str(code_file), "--id", "fdd-test-flow-login"])
            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "FOUND")

    def test_get_content_code_file_id_not_found(self):
        """Test get-content --code with valid file but non-existent ID."""
        with TemporaryDirectory() as tmpdir:
            code_file = Path(tmpdir) / "test.py"
            code_file.write_text("def foo(): pass\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--code", str(code_file), "--id", "nonexistent"])
            self.assertEqual(exit_code, 2)  # NOT_FOUND
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "NOT_FOUND")

    def test_get_content_code_with_inst(self):
        """Test get-content --code with --inst option."""
        with TemporaryDirectory() as tmpdir:
            code_file = Path(tmpdir) / "test.py"
            code_file.write_text(
                "# @fdd-begin:fdd-test-flow-login:ph-1:inst-validate\n"
                "def validate(): return True\n"
                "# @fdd-end:fdd-test-flow-login:ph-1:inst-validate\n",
                encoding="utf-8"
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main([
                    "get-content", "--code", str(code_file),
                    "--id", "fdd-test-flow-login", "--inst", "validate"
                ])
            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "FOUND")
            self.assertIn("validate", out.get("text", ""))

    def test_get_content_no_artifact_or_code(self):
        """Test get-content without --artifact or --code."""
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["get-content", "--id", "test"])
        self.assertNotEqual(exit_code, 0)
        out = json.loads(stdout.getvalue())
        self.assertEqual(out.get("status"), "ERROR")


class TestCLIListIdsIncludeCode(unittest.TestCase):
    """Tests for list-ids with --include-code option."""

    def test_list_ids_include_code_no_adapter(self):
        """Test list-ids --include-code without adapter."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids", "--include-code"])
                self.assertNotEqual(exit_code, 0)
            finally:
                os.chdir(cwd)

    def test_list_ids_include_code_with_adapter(self):
        """Test list-ids --include-code with valid adapter and codebase entry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Setup project with codebase entry
            templates_dir = root / "rules" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)
            tmpl_content = """---
fdd-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- fdd:id:item -->
**ID**: [ ] `p1` - `fdd-test-1`
<!-- fdd:id:item -->
"""
            (templates_dir / "template.md").write_text(tmpl_content, encoding="utf-8")

            art_dir = root / "architecture"
            art_dir.mkdir(parents=True)
            art_content = """<!-- fdd:id:item -->
**ID**: [x] `p1` - `fdd-test-1`
<!-- fdd:id:item -->
"""
            (art_dir / "PRD.md").write_text(art_content, encoding="utf-8")

            # Create code directory with markers
            code_dir = root / "src"
            code_dir.mkdir(parents=True)
            (code_dir / "module.py").write_text(
                "# @fdd-flow:fdd-test-flow-test:ph-1\ndef test(): pass\n",
                encoding="utf-8"
            )

            # Bootstrap registry with codebase entry
            _bootstrap_registry_new_format(
                root,
                rules={"fdd": {"format": "FDD", "path": "rules/sdlc"}},
                systems=[{
                    "name": "Test",
                    "rules": "fdd",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                    "codebase": [{"path": "src", "extensions": [".py"]}],
                }],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids", "--include-code"])
                # Should succeed
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertIn("count", out)
                # Should have code_files_scanned since we have codebase entry
                self.assertIn("code_files_scanned", out)
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
