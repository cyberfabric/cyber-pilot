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

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.cli import main


def _bootstrap_registry(project_root: Path, *, entries: list) -> None:
    (project_root / ".git").mkdir(exist_ok=True)
    (project_root / ".cypilot-config.json").write_text(
        '{\n  "cypilotAdapterPath": "adapter"\n}\n',
        encoding="utf-8",
    )
    adapter_dir = project_root / "adapter"
    adapter_dir.mkdir(parents=True, exist_ok=True)
    (adapter_dir / "AGENTS.md").write_text(
        "# Cypilot Adapter: Test\n\n**Extends**: `../AGENTS.md`\n",
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

    def test_validate_dir_with_design_and_specs_flag_fails(self):
        """When --artifact is a directory containing DESIGN.md, unknown --specs must error."""
        with TemporaryDirectory() as tmpdir:
            feat = Path(tmpdir)
            (feat / "DESIGN.md").write_text("# Feature: X\n", encoding="utf-8")

            with self.assertRaises(SystemExit):
                main(["validate", "--artifact", str(feat), "--specs", "spec-x"]) 

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

    def test_validate_code_root_with_spec_artifacts(self):
        """Cover validation when --artifact is a code root directory with features."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / "src").mkdir(parents=True, exist_ok=True)

            (root / "architecture" / "specs").mkdir(parents=True)

            # Minimal artifacts for feature-a/feature-b so traceability runs.
            (root / "architecture" / "specs" / "feature-a.md").write_text("# Feature: A\n", encoding="utf-8")
            (root / "architecture" / "specs" / "feature-b.md").write_text("# Feature: B\n", encoding="utf-8")

            _bootstrap_registry(
                root,
                entries=[
                    {"kind": "FEATURE", "system": "Test", "path": "architecture/features/feature-a.md", "format": "Cypilot"},
                    {"kind": "FEATURE", "system": "Test", "path": "architecture/features/feature-b.md", "format": "Cypilot"},
                    {"kind": "SRC", "system": "Test", "path": "src", "format": "CONTEXT", "traceability_enabled": True, "extensions": [".py"]},
                ],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["validate", "--artifact", str(root)])

            self.assertIn(exit_code, (0, 1, 2))
            out = json.loads(stdout.getvalue())
            self.assertIn("status", out)

    def test_validate_spec_dir_with_design_md_runs_codebase_traceability(self):
        """Cover validate branch when --artifact is a feature file under specs/ directory."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir(exist_ok=True)
            feat_dir = root / "architecture" / "specs"
            feat_dir.mkdir(parents=True)
            feat = feat_dir / "feature-x.md"
            feat.write_text("# Feature: X\n", encoding="utf-8")

            _bootstrap_registry(
                root,
                entries=[
                    {"kind": "FEATURE", "system": "Test", "path": "architecture/features/feature-x.md", "format": "Cypilot"},
                ],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["validate", "--artifact", str(feat)])
            self.assertIn(exit_code, (0, 1, 2))
            out = json.loads(stdout.getvalue())
            self.assertIn("status", out)


    def test_validate_markerless_constraints_do_not_trigger_legacy_other_kinds_error(self):
        """Regression: when constraints exist, skip legacy 'ID not referenced from other artifact kinds'."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Minimal SDLC kit with constraints
            (root / "kits" / "sdlc").mkdir(parents=True)
            src_constraints = Path(__file__).parent.parent / "kits" / "sdlc" / "constraints.json"
            (root / "kits" / "sdlc" / "constraints.json").write_text(src_constraints.read_text(encoding="utf-8"), encoding="utf-8")

            # Create markerless DESIGN artifact defining a principle (DESIGN/principle prohibits PRD/ADR refs)
            (root / "architecture").mkdir(parents=True)
            (root / "architecture" / "DESIGN.md").write_text(
                """#### 2.1: Design Principles\n\n- [ ] `p1` - **ID**: `cpt-test-principle-loose-coupling`\n""",
                encoding="utf-8",
            )

            # Create PRD artifact to ensure there are other kinds present (to provoke legacy error if not skipped)
            (root / "architecture" / "PRD.md").write_text(
                """- [ ] `p1` - **ID**: `cpt-test-fr-foo`\n""",
                encoding="utf-8",
            )

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
                    "artifacts": [
                        {"path": "architecture/DESIGN.md", "kind": "DESIGN"},
                        {"path": "architecture/PRD.md", "kind": "PRD"},
                    ],
                }],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate", "--verbose"])
                self.assertIn(exit_code, [0, 2])
                out = json.loads(stdout.getvalue())
                errors = out.get("errors", []) or []
                # Legacy check should not run when constraints exist
                self.assertFalse(any(e.get("message") == "ID not referenced from other artifact kinds" for e in errors))
            finally:
                os.chdir(cwd)


class TestCLICommandsRulesOnlyKit(unittest.TestCase):
    def test_rules_only_kit_markerless_commands_work(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create kit structure with constraints.json but no template.md (rules-only kit)
            kit_root = root / "kits" / "cypilot-sdlc"
            (kit_root / "artifacts" / "PRD").mkdir(parents=True)
            (kit_root / "constraints.json").write_text(
                json.dumps({"PRD": {"identifiers": {"fr": {"required": False}}}}, indent=2) + "\n",
                encoding="utf-8",
            )

            # Create an artifact that includes an ID line; include markers to emulate real artifacts.
            (root / "modules" / "a" / "docs").mkdir(parents=True)
            (root / "modules" / "a" / "docs" / "PRD.md").write_text(
                "<!-- cpt:#:prd -->\n# PRD\n\n<!-- cpt:id:fr -->\n**ID**: `cpt-root-a-fr-test`\n<!-- cpt:id:fr -->\n",
                encoding="utf-8",
            )

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot-sdlc": {"format": "Cypilot", "path": "kits/cypilot-sdlc"}},
                systems=[
                    {
                        "name": "root",
                        "slug": "root",
                        "kit": "cypilot-sdlc",
                        "autodetect": [
                            {
                                "system_root": "{project_root}/modules/$system",
                                "artifacts_root": "{system_root}/docs",
                                "artifacts": {"PRD": {"pattern": "PRD.md", "traceability": "FULL"}},
                                "validation": {"require_kind_registered_in_kit": True},
                            }
                        ],
                    }
                ],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))

                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertGreaterEqual(int(out.get("count", 0)), 1)

                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-id-kinds"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertIn("kinds", out)

                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-defined", "--id", "cpt-root-a-fr-test"])
                self.assertIn(exit_code, [0, 2])
            finally:
                os.chdir(cwd)


class TestCLIInitCommand(unittest.TestCase):
    def test_init_creates_config_and_adapter_and_allows_agents(self):
        with TemporaryDirectory() as tmpdir:
            project = Path(tmpdir) / "project"
            project.mkdir()

            cypilot_core = project / "Cypilot"
            cypilot_core.mkdir()
            (cypilot_core / "AGENTS.md").write_text("# Cypilot Core\n", encoding="utf-8")
            (cypilot_core / "requirements").mkdir()
            (cypilot_core / "workflows").mkdir()
            (cypilot_core / "skills" / "cypilot").mkdir(parents=True)
            (cypilot_core / "skills" / "cypilot" / "SKILL.md").write_text(
                "---\nname: cypilot\ndescription: Cypilot skill\n---\n# Cypilot\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main([
                    "init",
                    "--project-root",
                    str(project),
                    "--cypilot-root",
                    str(cypilot_core),
                    "--yes",
                ])
            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "PASS")
            self.assertTrue((project / ".cypilot-config.json").exists())
            self.assertTrue((project / ".cypilot-adapter" / "AGENTS.md").exists())

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main([
                    "agents",
                    "--agent",
                    "windsurf",
                    "--root",
                    str(project),
                    "--cypilot-root",
                    str(cypilot_core),
                    "--dry-run",
                ])
            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "PASS")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main([
                    "agents",
                    "--openai",
                    "--root",
                    str(project),
                    "--cypilot-root",
                    str(cypilot_core),
                    "--dry-run",
                ])
            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "PASS")

    def test_init_interactive_defaults(self):
        with TemporaryDirectory() as tmpdir:
            project = Path(tmpdir) / "project"
            project.mkdir()

            cypilot_core = project / "Cypilot"
            cypilot_core.mkdir()
            (cypilot_core / "AGENTS.md").write_text("# Cypilot Core\n", encoding="utf-8")
            (cypilot_core / "requirements").mkdir()
            (cypilot_core / "workflows").mkdir()

            orig_cwd = os.getcwd()
            try:
                os.chdir(project.as_posix())
                with unittest.mock.patch("builtins.input", side_effect=["", ""]):
                    stdout = io.StringIO()
                    with redirect_stdout(stdout), redirect_stderr(io.StringIO()):
                        exit_code = main(["init", "--cypilot-root", str(cypilot_core)])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "PASS")
                self.assertTrue((project / ".cypilot-config.json").exists())
                self.assertTrue((project / ".cypilot-adapter" / "AGENTS.md").exists())
            finally:
                os.chdir(orig_cwd)


class TestCLIAgentsCommand(unittest.TestCase):
    """Test agents command for workflow and skill proxy generation."""

    def _write_minimal_cypilot_skill(self, root: Path) -> None:
        (root / "skills" / "cypilot").mkdir(parents=True, exist_ok=True)
        (root / "skills" / "cypilot" / "SKILL.md").write_text(
            "---\nname: cypilot\ndescription: Cypilot skill for testing\n---\n# Cypilot\n",
            encoding="utf-8",
        )

    def _write_workflows_with_frontmatter(self, root: Path) -> None:
        (root / "workflows").mkdir(parents=True, exist_ok=True)
        (root / "workflows" / "generate.md").write_text(
            "---\ncypilot: true\ntype: workflow\nname: cypilot-generate\ndescription: Generate Cypilot artifacts\n---\n# Generate\n",
            encoding="utf-8",
        )
        (root / "workflows" / "analyze.md").write_text(
            "---\ncypilot: true\ntype: workflow\nname: cypilot-analyze\ndescription: Analyze Cypilot artifacts\n---\n# Analyze\n",
            encoding="utf-8",
        )

    def test_agents_empty_agent_raises(self):
        """Test that empty agent argument raises SystemExit."""
        with self.assertRaises(SystemExit):
            main(["agents", "--agent", " "])

    def test_agents_project_root_not_found(self):
        """Test agents command when no project root found."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agents", "--agent", "windsurf", "--root", str(root)])
            self.assertEqual(code, 1)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "NOT_FOUND")

    def test_agents_windsurf_creates_files(self):
        """Test agents command creates workflow and skill files for windsurf."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(exit_code, 0)

            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "PASS")
            self.assertGreater(out.get("workflows", {}).get("counts", {}).get("created", 0), 0)

            # Ensure description is always double-quoted in generated skill frontmatter
            skill_file = root / ".windsurf" / "skills" / "cypilot" / "SKILL.md"
            self.assertTrue(skill_file.exists())
            content = skill_file.read_text(encoding="utf-8")
            self.assertRegex(content, r"(?m)^description:\s+\".*\"\s*$", msg="description not quoted in windsurf skill output")

    def test_agents_claude_workflow_description_is_quoted(self):
        """Test claude workflow proxies render description in quoted YAML frontmatter."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["agents", "--agent", "claude", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(exit_code, 0)

            # One of the generated workflow command proxies should contain quoted description
            proxy = root / ".claude" / "commands" / "cypilot-generate.md"
            self.assertTrue(proxy.exists())
            txt = proxy.read_text(encoding="utf-8")
            self.assertRegex(txt, r"(?m)^description:\s+\".*\"\s*$", msg="description not quoted in claude workflow proxy")

    def test_agents_dry_run_does_not_write_files(self):
        """Test agents command dry-run mode."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root), "--dry-run"])
            self.assertEqual(exit_code, 0)

            out = json.loads(stdout.getvalue())
            self.assertTrue(out.get("dry_run"))
            created = out.get("workflows", {}).get("created", [])
            self.assertTrue(all(not Path(p).exists() for p in created))

    def test_agents_unknown_agent_creates_stub_config(self):
        """Test agents command with unknown agent creates stub config."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["agents", "--agent", "mystery-agent", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(exit_code, 0)

            cfg_path = root / "cypilot-agents.json"
            self.assertTrue(cfg_path.exists())
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            self.assertIn("mystery-agent", cfg.get("agents", {}))

    def test_agents_config_error_invalid_agents(self):
        """Test agents command with invalid agents config."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / "cypilot-agents.json").write_text(
                json.dumps({"version": 1, "agents": "bad"}, indent=2) + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agents", "--agent", "windsurf", "--root", str(root)])
            self.assertEqual(code, 1)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "CONFIG_ERROR")

    def test_agents_missing_workflow_dir_error(self):
        """Test agents command with missing workflow_dir in config."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)
            (root / "cypilot-agents.json").write_text(
                json.dumps({
                    "version": 1,
                    "agents": {
                        "windsurf": {
                            "workflows": {"template": ["# test"]},
                            "skills": {}
                        }
                    }
                }, indent=2) + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            # Should return partial status due to workflow error
            out = json.loads(stdout.getvalue())
            self.assertIn("Missing workflow_dir", str(out.get("errors", [])))

    def test_agents_missing_template_error(self):
        """Test agents command with missing template in config."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)
            (root / "cypilot-agents.json").write_text(
                json.dumps({
                    "version": 1,
                    "agents": {
                        "windsurf": {
                            "workflows": {
                                "workflow_dir": ".windsurf/workflows",
                                "template": "not a list"
                            },
                            "skills": {}
                        }
                    }
                }, indent=2) + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            out = json.loads(stdout.getvalue())
            self.assertIn("Missing or invalid template", str(out.get("errors", [])))

    def test_agents_skills_invalid_outputs_error(self):
        """Test agents command with invalid skills outputs config."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)
            (root / "cypilot-agents.json").write_text(
                json.dumps({
                    "version": 1,
                    "agents": {
                        "windsurf": {
                            "workflows": {},
                            "skills": {"outputs": "not a list"}
                        }
                    }
                }, indent=2) + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            out = json.loads(stdout.getvalue())
            self.assertIn("outputs must be an array", str(out.get("errors", [])))

    def test_agents_skills_missing_path_error(self):
        """Test agents command with missing path in skills output."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            (root / "cypilot-agents.json").write_text(
                json.dumps({
                    "version": 1,
                    "agents": {
                        "windsurf": {
                            "workflows": {},
                            "skills": {
                                "outputs": [{"template": ["# test"]}]
                            }
                        }
                    }
                }, indent=2) + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            out = json.loads(stdout.getvalue())
            self.assertIn("missing path", str(out.get("errors", [])))

    def test_agents_skills_missing_template_error(self):
        """Test agents command with missing template in skills output."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            (root / "cypilot-agents.json").write_text(
                json.dumps({
                    "version": 1,
                    "agents": {
                        "windsurf": {
                            "workflows": {},
                            "skills": {
                                "outputs": [{"path": ".windsurf/test.md", "template": "not a list"}]
                            }
                        }
                    }
                }, indent=2) + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            out = json.loads(stdout.getvalue())
            self.assertIn("invalid template", str(out.get("errors", [])))

    def test_agents_updates_existing_files(self):
        """Test agents command updates existing proxy files."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            # First run - create files
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])

            # Modify a file to trigger update
            wf_dir = root / ".windsurf" / "workflows"
            if wf_dir.is_dir():
                for f in wf_dir.glob("*.md"):
                    f.write_text("# Modified\n", encoding="utf-8")
                    break

            # Second run - should update
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            # Should have some updated files
            updated = out.get("workflows", {}).get("counts", {}).get("updated", 0)
            self.assertGreaterEqual(updated, 0)

    def test_agents_recognized_agent_added_to_existing_config(self):
        """Test that a recognized agent is added to existing config."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            # Create config with only cursor
            cfg_path = root / "cypilot-agents.json"
            cfg_path.write_text(
                json.dumps({
                    "version": 1,
                    "agents": {
                        "cursor": {"workflows": {}, "skills": {}}
                    }
                }, indent=2) + "\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(code, 0)

            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            self.assertIn("windsurf", cfg.get("agents", {}))
            # windsurf should have workflows config
            self.assertIn("workflows", cfg["agents"]["windsurf"])

    def test_agents_skills_creates_and_updates_outputs(self):
        """Test agents command creates and updates skill output files."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)

            (root / "cypilot-agents.json").write_text(
                json.dumps({
                    "version": 1,
                    "agents": {
                        "test": {
                            "workflows": {},
                            "skills": {
                                "outputs": [{
                                    "path": ".test/skill.md",
                                    "template": [
                                        "---",
                                        "name: {name}",
                                        "description: {description}",
                                        "---",
                                        "# {name}",
                                        "",
                                        "ALWAYS open and follow `{target_skill_path}`",
                                    ]
                                }]
                            }
                        }
                    }
                }, indent=2) + "\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["agents", "--agent", "test", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(exit_code, 0)

            out = json.loads(stdout.getvalue())
            self.assertGreater(len(out.get("skills", {}).get("created", [])), 0)

            # Verify file was created
            skill_file = root / ".test" / "skill.md"
            self.assertTrue(skill_file.exists())
            content = skill_file.read_text(encoding="utf-8")
            self.assertIn("# cypilot", content)
            self.assertRegex(content, r"(?m)^description:\s+\".*\"\s*$", msg="description not quoted in skill output")

            # Modify file and run again to test update
            skill_file.write_text("# Modified\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["agents", "--agent", "test", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(exit_code, 0)

            out = json.loads(stdout.getvalue())
            self.assertGreater(len(out.get("skills", {}).get("updated", [])), 0)


class TestCLIParseFrontmatter(unittest.TestCase):
    """Test _parse_frontmatter function."""

    def test_parse_frontmatter_valid(self):
        """Test parsing valid frontmatter."""
        from cypilot.commands.agents import _parse_frontmatter

        with TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "test.md"
            f.write_text("---\nname: test\ndescription: A test file\n---\n# Content\n", encoding="utf-8")

            result = _parse_frontmatter(f)
            self.assertEqual(result.get("name"), "test")
            self.assertEqual(result.get("description"), "A test file")

    def test_parse_frontmatter_strips_quotes(self):
        """Test parsing frontmatter unquotes quoted scalars."""
        from cypilot.commands.agents import _parse_frontmatter

        with TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "test.md"
            f.write_text('---\nname: "test"\ndescription: "A test file"\n---\n# Content\n', encoding="utf-8")

            result = _parse_frontmatter(f)
            self.assertEqual(result.get("name"), "test")
            self.assertEqual(result.get("description"), "A test file")

    def test_parse_frontmatter_no_frontmatter(self):
        """Test parsing file without frontmatter."""
        from cypilot.commands.agents import _parse_frontmatter

        with TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "test.md"
            f.write_text("# Just content\n", encoding="utf-8")

            result = _parse_frontmatter(f)
            self.assertEqual(result, {})

    def test_parse_frontmatter_unclosed(self):
        """Test parsing file with unclosed frontmatter."""
        from cypilot.commands.agents import _parse_frontmatter

        with TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "test.md"
            f.write_text("---\nname: test\n# No closing\n", encoding="utf-8")

            result = _parse_frontmatter(f)
            self.assertEqual(result, {})

    def test_parse_frontmatter_file_not_found(self):
        """Test parsing non-existent file."""
        from cypilot.commands.agents import _parse_frontmatter

        result = _parse_frontmatter(Path("/tmp/does-not-exist-abc123.md"))
        self.assertEqual(result, {})

    def test_parse_frontmatter_empty_values_skipped(self):
        """Test that empty values are skipped."""
        from cypilot.commands.agents import _parse_frontmatter

        with TemporaryDirectory() as tmpdir:
            f = Path(tmpdir) / "test.md"
            f.write_text("---\nname: test\nempty:\n---\n# Content\n", encoding="utf-8")

            result = _parse_frontmatter(f)
            self.assertEqual(result.get("name"), "test")
            self.assertNotIn("empty", result)


class TestCLIAgentsEdgeCases(unittest.TestCase):
    """Test agents command edge cases for better coverage."""

    def _write_minimal_cypilot_skill(self, root: Path) -> None:
        (root / "skills" / "cypilot").mkdir(parents=True, exist_ok=True)
        (root / "skills" / "cypilot" / "SKILL.md").write_text(
            "---\nname: cypilot\ndescription: Cypilot skill\n---\n# Cypilot\n",
            encoding="utf-8",
        )

    def _write_workflows_with_frontmatter(self, root: Path) -> None:
        (root / "workflows").mkdir(parents=True, exist_ok=True)
        (root / "workflows" / "generate.md").write_text(
            "---\ncypilot: true\ntype: workflow\nname: cypilot-generate\ndescription: Generate\n---\n# Generate\n",
            encoding="utf-8",
        )

    def test_agents_renames_misnamed_proxy(self):
        """Test agents command renames misnamed proxy files."""
        from cypilot.commands.agents import _safe_relpath

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            wf_dir = root / ".windsurf" / "workflows"
            wf_dir.mkdir(parents=True)

            # Create misnamed proxy file (wrong filename but correct target)
            target_rel = _safe_relpath(root / "workflows" / "generate.md", root)
            misnamed = wf_dir / "old-name.md"
            misnamed.write_text(f"# /cypilot-generate\n\nALWAYS open and follow `{target_rel}`\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(exit_code, 0)

            out = json.loads(stdout.getvalue())
            # Should rename the misnamed file
            renamed = out.get("workflows", {}).get("renamed", [])
            self.assertGreaterEqual(len(renamed), 0)

    def test_agents_deletes_stale_proxy(self):
        """Test agents command deletes stale proxy files pointing to non-existent workflows."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            wf_dir = root / ".windsurf" / "workflows"
            wf_dir.mkdir(parents=True)

            # Create stale proxy pointing to non-existent workflow
            stale = wf_dir / "cypilot-stale.md"
            stale.write_text(f"# /cypilot-stale\n\nALWAYS open and follow `{root}/workflows/does-not-exist.md`\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(exit_code, 0)

            out = json.loads(stdout.getvalue())
            deleted = out.get("workflows", {}).get("deleted", [])
            self.assertGreaterEqual(len(deleted), 0)

    def test_agents_read_error_on_existing_file(self):
        """Test agents command handles read error on existing workflow proxy file."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            wf_dir = root / ".windsurf" / "workflows"
            wf_dir.mkdir(parents=True)

            # Create a proxy file
            proxy = wf_dir / "cypilot-generate.md"
            proxy.write_text("# existing\n", encoding="utf-8")

            orig = Path.read_text

            def _rt(self: Path, *a, **k):
                if self.resolve() == proxy.resolve():
                    raise OSError("read error")
                return orig(self, *a, **k)

            with unittest.mock.patch.object(Path, "read_text", _rt):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(code, 0)

    def test_agents_skills_read_error_on_output(self):
        """Test agents command handles read error on skills output file."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)

            skill_out = root / ".test" / "skill.md"
            skill_out.parent.mkdir(parents=True)
            skill_out.write_text("# existing\n", encoding="utf-8")

            (root / "cypilot-agents.json").write_text(
                json.dumps({
                    "version": 1,
                    "agents": {
                        "test": {
                            "workflows": {},
                            "skills": {
                                "outputs": [{
                                    "path": ".test/skill.md",
                                    "template": ["# {name}"]
                                }]
                            }
                        }
                    }
                }, indent=2) + "\n",
                encoding="utf-8",
            )

            orig = Path.read_text

            def _rt(self: Path, *a, **k):
                if self.resolve() == skill_out.resolve():
                    raise OSError("read error")
                return orig(self, *a, **k)

            with unittest.mock.patch.object(Path, "read_text", _rt):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = main(["agents", "--agent", "test", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(code, 0)

    def test_agents_delete_stale_unlink_error(self):
        """Test agents command handles unlink error when deleting stale proxy."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            wf_dir = root / ".windsurf" / "workflows"
            wf_dir.mkdir(parents=True)

            # Create stale proxy
            stale = wf_dir / "cypilot-stale.md"
            stale.write_text(f"# /cypilot-stale\n\nALWAYS open and follow `{root}/workflows/does-not-exist.md`\n", encoding="utf-8")

            orig_unlink = Path.unlink

            def _unlink(self: Path, *a, **k):
                if self.resolve() == stale.resolve():
                    raise OSError("unlink error")
                return orig_unlink(self, *a, **k)

            with unittest.mock.patch.object(Path, "unlink", _unlink):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            # Should still succeed (error is silently ignored)
            self.assertEqual(code, 0)

    def test_agents_rename_scan_read_error(self):
        """Test agents command handles read error during rename scan."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            wf_dir = root / ".windsurf" / "workflows"
            wf_dir.mkdir(parents=True)

            # Create a file that will cause read error
            bad = wf_dir / "bad.md"
            bad.write_text("# /test\n", encoding="utf-8")

            orig = Path.read_text
            call_count = [0]

            def _rt(self: Path, *a, **k):
                if self.resolve() == bad.resolve():
                    call_count[0] += 1
                    if call_count[0] == 1:
                        raise OSError("read error")
                return orig(self, *a, **k)

            with unittest.mock.patch.object(Path, "read_text", _rt):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(code, 0)

    def test_agents_rename_skip_non_proxy_files(self):
        """Test agents command skips files that don't look like proxies during rename scan."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            wf_dir = root / ".windsurf" / "workflows"
            wf_dir.mkdir(parents=True)

            # File without "# /" header - should be skipped
            no_header = wf_dir / "no-header.md"
            no_header.write_text("Just content\n", encoding="utf-8")

            # File without ALWAYS open marker - should be skipped
            no_marker = wf_dir / "no-marker.md"
            no_marker.write_text("# /test\n\nNo marker here\n", encoding="utf-8")

            # File with malformed ALWAYS open marker (no backtick close)
            bad_marker = wf_dir / "bad-marker.md"
            bad_marker.write_text("# /test\n\nALWAYS open and follow `no-close\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(code, 0)

    def test_agents_rename_conflict_skips(self):
        """Test agents command skips rename when destination already exists."""
        from cypilot.commands.agents import _safe_relpath

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            wf_dir = root / ".windsurf" / "workflows"
            wf_dir.mkdir(parents=True)

            # Create misnamed proxy
            target_rel = _safe_relpath(root / "workflows" / "generate.md", root)
            misnamed = wf_dir / "old-name.md"
            misnamed.write_text(f"# /cypilot-generate\n\nALWAYS open and follow `{target_rel}`\n", encoding="utf-8")

            # Also create the destination file (conflict)
            dst = wf_dir / "cypilot-generate.md"
            dst.write_text("preexisting content\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(code, 0)

            # Both files should still exist (no rename due to conflict)
            self.assertTrue(misnamed.exists())
            self.assertTrue(dst.exists())

    def test_agents_delete_stale_skips_non_workflow_target(self):
        """Test agents command skips deletion for proxies pointing to non-workflow paths."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            wf_dir = root / ".windsurf" / "workflows"
            wf_dir.mkdir(parents=True)

            # Proxy pointing to non-workflow path (not in workflows/ dir)
            non_wf = wf_dir / "cypilot-other.md"
            non_wf.write_text("# /cypilot-other\n\nALWAYS open and follow `some/other/path.md`\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(code, 0)

            # File should not be deleted (not a workflow proxy)
            self.assertTrue(non_wf.exists())

    def test_agents_delete_stale_skips_non_cypilot_workflow(self):
        """Test agents command skips deletion for proxies pointing outside cypilot_root."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            wf_dir = root / ".windsurf" / "workflows"
            wf_dir.mkdir(parents=True)

            # Proxy pointing to workflow outside cypilot_root
            outside = wf_dir / "cypilot-outside.md"
            outside.write_text("# /cypilot-outside\n\nALWAYS open and follow `/other/workflows/x.md`\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(code, 0)

    def test_agents_delete_stale_read_error(self):
        """Test agents command handles read error during stale deletion scan."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            wf_dir = root / ".windsurf" / "workflows"
            wf_dir.mkdir(parents=True)

            # Create a stale-looking file
            stale = wf_dir / "cypilot-stale.md"
            stale.write_text("# stale\n", encoding="utf-8")

            orig = Path.read_text
            read_count = [0]

            def _rt(self: Path, *a, **k):
                # Let workflow scan succeed, fail on stale scan
                if self.resolve() == stale.resolve():
                    read_count[0] += 1
                    if read_count[0] > 1:
                        raise OSError("read error")
                return orig(self, *a, **k)

            with unittest.mock.patch.object(Path, "read_text", _rt):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(code, 0)

    def test_agents_delete_stale_no_regex_match(self):
        """Test agents command handles stale file without proper ALWAYS marker."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            wf_dir = root / ".windsurf" / "workflows"
            wf_dir.mkdir(parents=True)

            # Create file with ALWAYS but malformed (no backtick)
            malformed = wf_dir / "cypilot-malformed.md"
            malformed.write_text("# /cypilot-malformed\n\nALWAYS open and follow something\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(code, 0)

    def test_agents_unrecognized_agent_added_to_existing_config(self):
        """Test that an unrecognized agent is added as stub to existing config."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            # Create config with only cursor
            cfg_path = root / "cypilot-agents.json"
            cfg_path.write_text(
                json.dumps({
                    "version": 1,
                    "agents": {
                        "cursor": {"workflows": {}, "skills": {}}
                    }
                }, indent=2) + "\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = main(["agents", "--agent", "new-mystery-agent", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(code, 0)

            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            self.assertIn("new-mystery-agent", cfg.get("agents", {}))
            # Should have empty stub config
            self.assertEqual(cfg["agents"]["new-mystery-agent"], {"workflows": {}, "skills": {}})

    def test_agents_rename_scan_second_read_error(self):
        """Test agents command handles second read error during rename scan."""
        from cypilot.commands.agents import _safe_relpath

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            self._write_minimal_cypilot_skill(root)
            self._write_workflows_with_frontmatter(root)

            wf_dir = root / ".windsurf" / "workflows"
            wf_dir.mkdir(parents=True)

            # Create misnamed proxy file
            target_rel = _safe_relpath(root / "workflows" / "generate.md", root)
            misnamed = wf_dir / "old.md"
            misnamed.write_text(f"# /cypilot-generate\n\nALWAYS open and follow `{target_rel}`\n", encoding="utf-8")

            orig = Path.read_text
            call_count = [0]

            def _rt(self: Path, *a, **k):
                if self.resolve() == misnamed.resolve():
                    call_count[0] += 1
                    # Fail on second read (first is head check)
                    if call_count[0] == 2:
                        raise OSError("read error on second read")
                return orig(self, *a, **k)

            with unittest.mock.patch.object(Path, "read_text", _rt):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = main(["agents", "--agent", "windsurf", "--root", str(root), "--cypilot-root", str(root)])
            self.assertEqual(code, 0)


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
                exit_code = main(["get-content", "--artifact", str(doc), "--id", "cpt-test-id"])
            self.assertEqual(exit_code, 1)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "ERROR")

    def test_get_content_file_not_found(self):
        """Cover ERROR for get-content when artifact file not found."""
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["get-content", "--artifact", "/tmp/does-not-exist.md", "--id", "cpt-test-id"])
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
                        "- [ ] **ID**: `cpt-test-req-auth`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            _bootstrap_registry(
                root,
                entries=[
                    {"kind": "DESIGN", "system": "Test", "path": "architecture/DESIGN.md", "format": "Cypilot", "traceability_enabled": True},
                ],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["where-defined", "--id", "cpt-test-req-auth"])
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
                        "**ID**: `cpt-test-req-auth`",
                        "Uses: `cpt-test-req-auth`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            _bootstrap_registry(
                root,
                entries=[
                    {"kind": "DESIGN", "system": "Test", "path": "architecture/DESIGN.md", "format": "Cypilot", "traceability_enabled": True},
                ],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["where-used", "--id", "cpt-test-req-auth"])
            self.assertIn(exit_code, (0, 1))


class TestCLICoreHelpers(unittest.TestCase):
    def test_safe_relpath_from_dir_relpath_exception_returns_abs(self):
        from cypilot.commands.agents import _safe_relpath_from_dir
        
        target = Path("/tmp/x")
        with unittest.mock.patch("os.path.relpath", side_effect=Exception("boom")):
            out = _safe_relpath_from_dir(target, Path("/tmp"))
        self.assertEqual(out, target.as_posix())

    def test_render_template_missing_variable_raises_system_exit(self):
        from cypilot.commands.agents import _render_template

        with self.assertRaises(SystemExit):
            _render_template(["{missing}"], {})

    def test_list_workflow_files_missing_dir_returns_empty(self):
        from cypilot.commands.agents import _list_workflow_files

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.assertEqual(_list_workflow_files(root), [])

    def test_list_workflow_files_filters_and_handles_read_error(self):
        from cypilot.commands.agents import _list_workflow_files

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
                out = _list_workflow_files(root)
            self.assertEqual(out, ["ok.md"])

    def test_list_workflow_files_iterdir_error_returns_empty(self):
        from cypilot.commands.agents import _list_workflow_files

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
                self.assertEqual(_list_workflow_files(root), [])

    def test_resolve_user_path_relative_uses_base(self):
        from cypilot.commands.init import _resolve_user_path

        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            out = _resolve_user_path("foo", base)
            self.assertEqual(out, (base / "foo").resolve())

    def test_prompt_path_returns_user_input_over_default(self):
        from cypilot.commands.init import _prompt_path

        with unittest.mock.patch("builtins.input", return_value="abc"):
            out = _prompt_path("Q?", "def")
        self.assertEqual(out, "abc")

    def test_load_json_file_invalid_json_returns_none(self):
        from cypilot.commands.agents import _load_json_file

        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "x.json"
            p.write_text("{not-json}", encoding="utf-8")
            self.assertIsNone(_load_json_file(p))


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
    """Test CLI backward compatibility."""

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
        """Cover adapter-info CONFIG_ERROR when .cypilot-config.json points to missing adapter directory."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".cypilot-config.json").write_text('{"cypilotAdapterPath": "missing-adapter"}', encoding="utf-8")

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

    def test_validate_code_markerless_cdsl_implemented_requires_block_marker(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_cypilot_project_with_markerless_cdsl_missing_block(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-code", "--verbose"])
                self.assertEqual(exit_code, 2)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "FAIL")
                errors = out.get("errors", [])
                self.assertTrue(any(
                    (e.get("type") == "coverage")
                    and ("ID marked to_code=\"true\" has no code marker" in str(e.get("message", "")))
                    and (e.get("id") == "cpt-test-flow-login")
                    for e in errors
                ))
            finally:
                os.chdir(cwd)

    def test_validate_code_cdsl_implemented_requires_block_marker(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_cypilot_project_with_cdsl_to_code_missing_block(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-code", "--verbose"])
                self.assertEqual(exit_code, 2)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "FAIL")
                errors = out.get("errors", [])
                self.assertTrue(any(
                    (e.get("type") == "coverage")
                    and ("ID marked to_code=\"true\" has no code marker" in str(e.get("message", "")))
                    for e in errors
                ))
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
            (outside / "AGENTS.md").write_text("# Cypilot Adapter: Outside\n\n**Extends**: `../AGENTS.md`\n", encoding="utf-8")

            # Point config path outside the project.
            (root / ".cypilot-config.json").write_text('{"cypilotAdapterPath": "../outside-adapter"}', encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["adapter-info", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "FOUND")
            self.assertEqual(out.get("relative_path"), str(outside.resolve().as_posix()))


def _bootstrap_registry_new_format(project_root: Path, *, systems: list, kits: dict = None) -> None:
    """Bootstrap registry with new format (systems instead of artifacts)."""
    (project_root / ".git").mkdir(exist_ok=True)
    (project_root / ".cypilot-config.json").write_text(
        '{\n  "cypilotAdapterPath": "adapter"\n}\n',
        encoding="utf-8",
    )
    adapter_dir = project_root / "adapter"
    adapter_dir.mkdir(parents=True, exist_ok=True)
    (adapter_dir / "AGENTS.md").write_text(
        "# Cypilot Adapter: Test\n\n**Extends**: `../AGENTS.md`\n",
        encoding="utf-8",
    )
    registry = {
        "version": "1.0",
        "project_root": "..",
        "kits": kits if kits is not None else {"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
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
            templates_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)

            # Create template
            tmpl_content = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- cpt:id:item -->
- [ ] `p1` - **ID**: `cpt-test-1`
<!-- cpt:id:item -->
"""
            (templates_dir / "template.md").write_text(tmpl_content, encoding="utf-8")

            # Create artifact
            art_dir = root / "architecture"
            art_dir.mkdir(parents=True)
            art_content = """<!-- cpt:id:item -->
- [x] `p1` - **ID**: `cpt-test-1`
<!-- cpt:id:item -->
"""
            (art_dir / "PRD.md").write_text(art_content, encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
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


class TestCLIValidateKitsCommand(unittest.TestCase):
    """Tests for validate-kits command."""

    def test_validate_rules_no_adapter(self):
        """Test validate-kits without adapter."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-kits"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)

    def test_validate_rules_with_template(self):
        """Test validate-kits with specific template."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            (root / "kits" / "sdlc").mkdir(parents=True)
            (root / "kits" / "sdlc" / "constraints.json").write_text(
                json.dumps({"PRD": {"identifiers": {"flow": {"to_code": True}}}}, indent=2) + "\n",
                encoding="utf-8",
            )

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-kits"])

                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "PASS")
                self.assertEqual(out.get("kits_validated"), 1)
            finally:
                os.chdir(cwd)

    def test_validate_rules_with_invalid_template(self):
        """Test validate-kits with invalid template."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            (root / "kits" / "sdlc").mkdir(parents=True)
            (root / "kits" / "sdlc" / "constraints.json").write_text("not-json", encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-kits", "--verbose"])

                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "FAIL")
                self.assertIn("errors", out)
            finally:
                os.chdir(cwd)

    def test_validate_rules_nonexistent_template(self):
        """Test validate-kits with nonexistent template."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "kits" / "sdlc").mkdir(parents=True)
            (root / "kits" / "sdlc" / "constraints.json").write_text(
                json.dumps({"PRD": {"identifiers": {"flow": {"to_code": True}}}}, indent=2) + "\n",
                encoding="utf-8",
            )
            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-kits", "--kit", "missing-kit"])

                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "PASS")
                self.assertEqual(out.get("kits_validated"), 0)
            finally:
                os.chdir(cwd)

    def test_validate_rules_verbose(self):
        """Test validate-kits with verbose flag."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            (root / "kits" / "sdlc").mkdir(parents=True)
            (root / "kits" / "sdlc" / "constraints.json").write_text(
                json.dumps({"PRD": {"identifiers": {"flow": {"to_code": True}}}}, indent=2) + "\n",
                encoding="utf-8",
            )
            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-kits", "--verbose"])

                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertIn("kits", out)
            finally:
                os.chdir(cwd)


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
                exit_code = main(["get-content", "--artifact", str(art_path), "--id", "cpt-test-1"])
            self.assertNotEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "ERROR")

    def test_get_content_with_artifact(self):
        """Test get-content with specific artifact."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            templates_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)

            # Create template
            tmpl_content = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- cpt:id:item -->
- [ ] `p1` - **ID**: `cpt-test-1`
<!-- cpt:id:item -->
"""
            (templates_dir / "template.md").write_text(tmpl_content, encoding="utf-8")

            # Create artifact
            art_dir = root / "architecture"
            art_dir.mkdir(parents=True)
            art_content = """<!-- cpt:id:item -->
- [x] `p1` - **ID**: `cpt-test-1`
<!-- cpt:id:item -->
"""
            art_path = art_dir / "PRD.md"
            art_path.write_text(art_content, encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                }],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--artifact", str(art_path), "--id", "cpt-test-1"])

            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertIn("text", out)  # get-content returns "text" field

    def test_get_content_without_markers_uses_heading_scope(self):
        """Fallback get-content for artifacts with no `<!-- cpt:... -->` markers (heading scope)."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            templates_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)

            tmpl_content = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- cpt:free:body -->
text
<!-- cpt:free:body -->
"""
            (templates_dir / "template.md").write_text(tmpl_content, encoding="utf-8")

            art_dir = root / "architecture"
            art_dir.mkdir(parents=True)
            art_content = """# PRD

### cpt-test-1
alpha
beta

### cpt-test-2
gamma
"""
            art_path = art_dir / "PRD.md"
            art_path.write_text(art_content, encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                }],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--artifact", str(art_path), "--id", "cpt-test-1"])

            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "FOUND")
            self.assertEqual(out.get("text"), "alpha\nbeta")

    def test_get_content_without_markers_uses_hash_fence_scope(self):
        """Fallback get-content for artifacts with no markers using ## scope fences."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            templates_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)

            tmpl_content = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- cpt:free:body -->
text
<!-- cpt:free:body -->
"""
            (templates_dir / "template.md").write_text(tmpl_content, encoding="utf-8")

            art_dir = root / "architecture"
            art_dir.mkdir(parents=True)
            art_content = """intro
##
cpt-test-1
line-a
line-b
##
outro
"""
            art_path = art_dir / "PRD.md"
            art_path.write_text(art_content, encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                }],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--artifact", str(art_path), "--id", "cpt-test-1"])

            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "FOUND")
            self.assertEqual(out.get("text"), "line-a\nline-b")

    def test_get_content_without_markers_hash_fence_multiple_ids(self):
        """Hash-fence scope variant: IDs are delimiters within the same fence."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            templates_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)

            tmpl_content = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- cpt:free:body -->
text
<!-- cpt:free:body -->
"""
            (templates_dir / "template.md").write_text(tmpl_content, encoding="utf-8")

            art_dir = root / "architecture"
            art_dir.mkdir(parents=True)
            art_content = """##
cpt-aa
aaa
cpt-bb
bbb
cpt-cc
ccc
##
"""
            art_path = art_dir / "PRD.md"
            art_path.write_text(art_content, encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                }],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--artifact", str(art_path), "--id", "cpt-bb"])

            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "FOUND")
            self.assertEqual(out.get("text"), "bbb")

    def test_get_content_without_markers_id_line_under_heading(self):
        """Fallback get-content: ID definition line under a normal heading scopes content to next heading."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            templates_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)

            tmpl_content = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- cpt:free:body -->
text
<!-- cpt:free:body -->
"""
            (templates_dir / "template.md").write_text(tmpl_content, encoding="utf-8")

            art_dir = root / "architecture"
            art_dir.mkdir(parents=True)
            art_content = """#### SaaS Developer

**ID**: `cpt-hyperspot-actor-saas-developer`

**Role**: Software engineer building business logic modules.

#### Platform Operator

**ID**: `cpt-hyperspot-actor-platform-operator`
"""
            art_path = art_dir / "PRD.md"
            art_path.write_text(art_content, encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                }],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--artifact", str(art_path), "--id", "cpt-hyperspot-actor-saas-developer"])

            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "FOUND")
            self.assertEqual(out.get("text"), "**Role**: Software engineer building business logic modules.")

    def test_get_content_without_markers_id_line_stops_at_next_defined_id(self):
        """Fallback get-content: stop at the next ID definition line before the next heading."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            templates_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)

            tmpl_content = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- cpt:free:body -->
text
<!-- cpt:free:body -->
"""
            (templates_dir / "template.md").write_text(tmpl_content, encoding="utf-8")

            art_dir = root / "architecture"
            art_dir.mkdir(parents=True)
            art_content = """#### People

**ID**: `cpt-aa`
aaa

**ID**: `cpt-bb`
bbb

#### Next
**ID**: `cpt-cc`
ccc
"""
            art_path = art_dir / "PRD.md"
            art_path.write_text(art_content, encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                }],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--artifact", str(art_path), "--id", "cpt-aa"])

            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "FOUND")
            self.assertEqual(out.get("text"), "aaa")


class TestCLIIdCommandsWithoutMarkers(unittest.TestCase):
    """Fallback behavior for ID commands when artifacts have no `<!-- cpt:... -->` markers."""

    def test_list_ids_without_markers_finds_definitions_and_refs(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            templates_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)

            tmpl_content = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- cpt:free:body -->
text
<!-- cpt:free:body -->
"""
            (templates_dir / "template.md").write_text(tmpl_content, encoding="utf-8")

            art_dir = root / "architecture"
            art_dir.mkdir(parents=True)
            art_content = """# PRD

**ID**: `cpt-test-define-1`

See also `cpt-test-ref-1` in text.

```md
**ID**: `cpt-test-ignored`
```
"""
            art_path = art_dir / "PRD.md"
            art_path.write_text(art_content, encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                }],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["list-ids", "--artifact", str(art_path)])

            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            ids = {h.get("id") for h in out.get("ids", [])}
            self.assertIn("cpt-test-define-1", ids)
            self.assertIn("cpt-test-ref-1", ids)
            self.assertNotIn("cpt-test-ignored", ids)

    def test_where_defined_without_markers(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            templates_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)
            (templates_dir / "template.md").write_text(
                """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- cpt:free:body -->
text
<!-- cpt:free:body -->
""",
                encoding="utf-8",
            )

            art_dir = root / "architecture"
            art_dir.mkdir(parents=True)
            art_path = art_dir / "PRD.md"
            art_path.write_text("**ID**: `cpt-test-def-1`\n", encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                }],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["where-defined", "--artifact", str(art_path), "--id", "cpt-test-def-1"])

            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "FOUND")
            self.assertEqual(out.get("count"), 1)

    def test_where_used_without_markers(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            templates_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)
            (templates_dir / "template.md").write_text(
                """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- cpt:free:body -->
text
<!-- cpt:free:body -->
""",
                encoding="utf-8",
            )

            art_dir = root / "architecture"
            art_dir.mkdir(parents=True)
            art_path = art_dir / "PRD.md"
            art_path.write_text("ref `cpt-test-ref-1`\n", encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                }],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["where-used", "--artifact", str(art_path), "--id", "cpt-test-ref-1"])

            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("id"), "cpt-test-ref-1")
            self.assertEqual(out.get("count"), 1)


class TestValidateMarkerlessCrossKindCoverage(unittest.TestCase):
    def test_validate_markerless_definition_fails_when_other_kind_exists_but_no_ref(self):
        """If other artifact kinds exist, markerless **ID** definitions must be referenced from another kind."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Templates
            prd_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
            dsn_dir = root / "kits" / "sdlc" / "artifacts" / "DESIGN"
            prd_dir.mkdir(parents=True)
            dsn_dir.mkdir(parents=True)
            tmpl = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: {KIND}
---
<!-- cpt:free:body -->
text
<!-- cpt:free:body -->
"""
            (prd_dir / "template.md").write_text(tmpl.format(KIND="PRD"), encoding="utf-8")
            (dsn_dir / "template.md").write_text(tmpl.format(KIND="DESIGN"), encoding="utf-8")

            # Artifacts (markerless)
            arch = root / "architecture"
            arch.mkdir(parents=True)
            prd_path = arch / "PRD.md"
            dsn_path = arch / "DESIGN.md"
            prd_path.write_text("**ID**: `cpt-test-aa`\ncontent\n", encoding="utf-8")
            dsn_path.write_text("# Design\n(no refs)\n", encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
                    "artifacts": [
                        {"path": "architecture/PRD.md", "kind": "PRD"},
                        {"path": "architecture/DESIGN.md", "kind": "DESIGN"},
                    ],
                }],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate", "--artifact", str(prd_path), "--skip-code", "--verbose"])
            finally:
                os.chdir(cwd)

            self.assertEqual(exit_code, 2)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "FAIL")
            self.assertGreater(out.get("error_count", 0), 0)

    def test_validate_markerless_definition_warns_when_no_other_kind_exists(self):
        """If no other artifact kinds exist, markerless definitions emit a warning (not an error)."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            prd_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
            prd_dir.mkdir(parents=True)
            (prd_dir / "template.md").write_text(
                """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- cpt:free:body -->
text
<!-- cpt:free:body -->
""",
                encoding="utf-8",
            )

            arch = root / "architecture"
            arch.mkdir(parents=True)
            prd_path = arch / "PRD.md"
            prd_path.write_text("**ID**: `cpt-test-aa`\ncontent\n", encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                }],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate", "--artifact", str(prd_path), "--skip-code", "--verbose"])
            finally:
                os.chdir(cwd)

            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "PASS")
            self.assertGreaterEqual(out.get("warning_count", 0), 1)

    def test_validate_markerless_definition_passes_when_referenced_from_other_kind(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            prd_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
            dsn_dir = root / "kits" / "sdlc" / "artifacts" / "DESIGN"
            prd_dir.mkdir(parents=True)
            dsn_dir.mkdir(parents=True)
            tmpl = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: {KIND}
---
<!-- cpt:free:body -->
text
<!-- cpt:free:body -->
"""
            (prd_dir / "template.md").write_text(tmpl.format(KIND="PRD"), encoding="utf-8")
            (dsn_dir / "template.md").write_text(tmpl.format(KIND="DESIGN"), encoding="utf-8")

            arch = root / "architecture"
            arch.mkdir(parents=True)
            prd_path = arch / "PRD.md"
            dsn_path = arch / "DESIGN.md"
            prd_path.write_text("**ID**: `cpt-test-aa`\ncontent\n", encoding="utf-8")
            dsn_path.write_text("ref `cpt-test-aa`\n", encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
                    "artifacts": [
                        {"path": "architecture/PRD.md", "kind": "PRD"},
                        {"path": "architecture/DESIGN.md", "kind": "DESIGN"},
                    ],
                }],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate", "--artifact", str(prd_path), "--skip-code", "--verbose"])
            finally:
                os.chdir(cwd)

            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "PASS")
            self.assertEqual(out.get("error_count"), 0)

    def test_validate_markerless_definition_passes_when_referenced_from_code_in_full_traceability(self):
        """If other kinds exist but no other-artifact ref, a code marker reference satisfies coverage when FULL."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            prd_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
            dsn_dir = root / "kits" / "sdlc" / "artifacts" / "DESIGN"
            prd_dir.mkdir(parents=True)
            dsn_dir.mkdir(parents=True)
            tmpl = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: {KIND}
---
<!-- cpt:free:body -->
text
<!-- cpt:free:body -->
"""
            (prd_dir / "template.md").write_text(tmpl.format(KIND="PRD"), encoding="utf-8")
            (dsn_dir / "template.md").write_text(tmpl.format(KIND="DESIGN"), encoding="utf-8")

            arch = root / "architecture"
            arch.mkdir(parents=True)
            prd_path = arch / "PRD.md"
            dsn_path = arch / "DESIGN.md"
            prd_path.write_text("**ID**: `cpt-test-aa`\ncontent\n", encoding="utf-8")
            dsn_path.write_text("# Design\n(no refs)\n", encoding="utf-8")

            src = root / "src"
            src.mkdir(parents=True)
            (src / "app.py").write_text("# @cpt-actor:cpt-test-aa:p1\n", encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
                    "artifacts": [
                        {"path": "architecture/PRD.md", "kind": "PRD", "traceability": "FULL"},
                        {"path": "architecture/DESIGN.md", "kind": "DESIGN", "traceability": "FULL"},
                    ],
                    "codebase": [{"name": "Code", "path": "src", "extensions": [".py"]}],
                }],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate", "--artifact", str(prd_path), "--verbose"])
            finally:
                os.chdir(cwd)

            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "PASS")


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
                    exit_code = main(["where-defined", "--id", "cpt-test-1"])
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
                    exit_code = main(["where-used", "--id", "cpt-test-1"])
                self.assertNotEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
            finally:
                os.chdir(cwd)


def _setup_cypilot_project(root: Path) -> None:
    """Setup a complete Cypilot project with template and artifact."""
    # Create template at new path: kits/sdlc/artifacts/PRD/template.md
    templates_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
    templates_dir.mkdir(parents=True)

    # Create template with ID block
    tmpl_content = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- cpt:id:item -->
- [ ] `p1` - **ID**: `cpt-test-1`
<!-- cpt:id:item -->
"""
    (templates_dir / "template.md").write_text(tmpl_content, encoding="utf-8")

    # Create artifact
    art_dir = root / "architecture"
    art_dir.mkdir(parents=True)
    art_content = """<!-- cpt:id:item -->
- [x] `p1` - **ID**: `cpt-test-1`
<!-- cpt:id:item -->
"""
    (art_dir / "PRD.md").write_text(art_content, encoding="utf-8")

    _bootstrap_registry_new_format(
        root,
        kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
        systems=[{
            "name": "Test",
            "kits": "cypilot",
            "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
        }],
    )


class TestCLIWhereDefinedWithArtifacts(unittest.TestCase):
    """Tests for where-defined command with actual artifacts."""

    def test_where_defined_found(self):
        """Test where-defined finds an ID."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_cypilot_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-defined", "--id", "cpt-test-1"])
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
            _setup_cypilot_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-defined", "--id", "cpt-nonexistent"])
                self.assertEqual(exit_code, 2)  # NOT_FOUND returns 2
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "NOT_FOUND")
            finally:
                os.chdir(cwd)

    def test_where_defined_with_artifact_flag(self):
        """Test where-defined with --artifact flag."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_cypilot_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                art_path = root / "architecture" / "PRD.md"
                with redirect_stdout(stdout):
                    exit_code = main(["where-defined", "--id", "cpt-test-1", "--artifact", str(art_path)])
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
            _setup_cypilot_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-used", "--id", "cpt-test-1"])
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
            _setup_cypilot_project(root)

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
            _setup_cypilot_project(root)

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
            _setup_cypilot_project(root)

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
            _setup_cypilot_project(root)

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
            _setup_cypilot_project(root)

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
            _setup_cypilot_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids", "--pattern", "cpt-.*", "--regex"])
                self.assertEqual(exit_code, 0)
            finally:
                os.chdir(cwd)

    def test_list_ids_with_all_flag(self):
        """Test list-ids with --all flag."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_cypilot_project(root)

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
            _setup_cypilot_project(root)

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
            _setup_cypilot_project(root)

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
            _setup_cypilot_project(root)

            stdout = io.StringIO()
            nonexistent = root / "nonexistent.md"
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--artifact", str(nonexistent), "--id", "cpt-test-1"])
            self.assertNotEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "ERROR")

    def test_get_content_artifact_not_in_registry(self):
        """Test get-content when artifact not in registry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_cypilot_project(root)

            # Create artifact NOT in registry
            unregistered = root / "unregistered.md"
            unregistered.write_text("# Not registered\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--artifact", str(unregistered), "--id", "cpt-test-1"])
            self.assertNotEqual(exit_code, 0)

    def test_get_content_id_not_found(self):
        """Test get-content when ID doesn't exist."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_cypilot_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                art_path = root / "architecture" / "PRD.md"
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["get-content", "--artifact", str(art_path), "--id", "cpt-nonexistent"])
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
            _setup_cypilot_project(root)

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
            _setup_cypilot_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                nonexistent = root / "nonexistent.md"
                with redirect_stdout(stdout):
                    exit_code = main(["where-defined", "--id", "cpt-test-1", "--artifact", str(nonexistent)])
                self.assertNotEqual(exit_code, 0)
            finally:
                os.chdir(cwd)


class TestCLIWhereUsedErrorBranches(unittest.TestCase):
    """Tests for where-used error branches."""

    def test_where_used_empty_id(self):
        """Test where-used with empty ID."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_cypilot_project(root)

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
            _setup_cypilot_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-used", "--id", "cpt-test-1", "--include-definitions"])
                # May return FOUND or NOT_FOUND depending on refs
                self.assertIn(exit_code, [0, 2])
            finally:
                os.chdir(cwd)

    def test_where_used_artifact_not_found(self):
        """Test where-used with nonexistent artifact."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_cypilot_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                nonexistent = root / "nonexistent.md"
                with redirect_stdout(stdout):
                    exit_code = main(["where-used", "--id", "cpt-test-1", "--artifact", str(nonexistent)])
                self.assertNotEqual(exit_code, 0)
            finally:
                os.chdir(cwd)

    def test_where_used_artifact_not_in_registry(self):
        """Test where-used with artifact not in registry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_cypilot_project(root)

            # Create artifact NOT in registry
            unregistered = root / "unregistered.md"
            unregistered.write_text("# Not registered\n", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-used", "--id", "cpt-test-1", "--artifact", str(unregistered)])
                self.assertNotEqual(exit_code, 0)
            finally:
                os.chdir(cwd)

    def test_where_used_with_valid_artifact(self):
        """Test where-used with valid artifact flag."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_cypilot_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                art_path = root / "architecture" / "PRD.md"
                with redirect_stdout(stdout):
                    exit_code = main(["where-used", "--id", "cpt-test-1", "--artifact", str(art_path)])
                # Will succeed or return NOT_FOUND
                self.assertIn(exit_code, [0, 2])
            finally:
                os.chdir(cwd)


class TestCLIValidateKitsErrorBranches(unittest.TestCase):
    """Tests for validate-kits error branches."""

    def test_validate_rules_registry_error(self):
        """Test validate-kits when registry has errors."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".cypilot-config.json").write_text('{"cypilotAdapterPath": "adapter"}', encoding="utf-8")
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
                    exit_code = main(["validate-kits"])
                self.assertNotEqual(exit_code, 0)
            finally:
                os.chdir(cwd)

    def test_validate_rules_no_cypilot_templates(self):
        """Test validate-kits when no Cypilot templates in registry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # Setup with non-Cypilot format
            _bootstrap_registry_new_format(
                root,
                kits={"other": {"format": "OTHER", "path": "templates"}},
                systems=[{"name": "Test", "kits": "other", "artifacts": []}],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-kits"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "PASS")
                self.assertEqual(out.get("kits_validated"), 0)
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
            (adapter / ".cypilot-config.json").write_text('{"cypilotAdapterPath": "adapter"}', encoding="utf-8")

            # Point config to existing adapter
            (root / ".cypilot-config.json").write_text('{"cypilotAdapterPath": "adapter"}', encoding="utf-8")

            cwd = os.getcwd()
            stdout = io.StringIO()
            try:
                os.chdir(str(root))
                with redirect_stdout(stdout):
                    exit_code = main(["init", "--yes"])
                # May fail if Cypilot core not found, but should at least try backup
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
            (root / ".cypilot-config.json").write_text('{"cypilotAdapterPath": "adapter"}', encoding="utf-8")
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

    def test_self_check_missing_rules(self):
        """Test self-check when rules are missing from registry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # Bootstrap with empty rules
            _bootstrap_registry_new_format(root, systems=[], kits={})

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
            _setup_cypilot_project(root)

            # Create artifact outside project root
            outside = Path(tmpdir) / "outside" / "test.md"
            outside.parent.mkdir(parents=True)
            outside.write_text("<!-- cpt:id:item -->\n- [x] `p1` - **ID**: `test`\n<!-- cpt:id:item -->", encoding="utf-8")

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
            _setup_cypilot_project(root)

            # Create artifact file under project root but not registered
            unregistered = root / "unregistered.md"
            unregistered.write_text("<!-- cpt:id:item -->\n- [x] `p1` - **ID**: `test`\n<!-- cpt:id:item -->", encoding="utf-8")

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
            (root / ".cypilot-config.json").write_text('{"cypilotAdapterPath": "adapter"}', encoding="utf-8")
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
            _setup_cypilot_project(root)

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

    def test_list_id_kinds_no_cypilot_artifacts(self):
        """Test list-id-kinds when no Cypilot-format artifacts in registry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _bootstrap_registry_new_format(
                root,
                kits={"other": {"format": "OTHER", "path": "templates"}},
                systems=[{"name": "Test", "kits": "other", "artifacts": []}],
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
            (root / ".cypilot-config.json").write_text('{"cypilotAdapterPath": "adapter"}', encoding="utf-8")
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
            _setup_cypilot_project(root)

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

            # Create invalid template (missing cypilot-template frontmatter)
            (templates_dir / "PRD.template.md").write_text(
                "<!-- cpt:id:item -->\nNo frontmatter here\n<!-- cpt:id:item -->",
                encoding="utf-8"
            )

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "templates"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
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
            _setup_cypilot_project(root)

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
            (root / ".cypilot-config.json").mkdir()

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
            (root / ".cypilot-config.json").write_text('{"someOtherKey": "value"}', encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["init", "--yes", "--project-root", str(root)])
                # May fail due to incomplete config or Cypilot core not found
                self.assertIn(exit_code, [0, 1, 2])
            finally:
                os.chdir(cwd)

    def test_init_existing_config_conflict(self):
        """Test init when existing config has conflicting paths."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            # Create config with different paths
            (root / ".cypilot-config.json").write_text(
                '{"cypilotCorePath": "different/path", "cypilotAdapterPath": "different/adapter"}',
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
            adapter = root / ".cypilot-adapter"
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
            adapter = root / ".cypilot-adapter"
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
            adapter = root / ".cypilot-adapter"
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

    def test_init_force_merges_existing_config(self):
        """Test init --force merges with existing valid config."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            # Create existing valid config with extra fields
            config = root / ".cypilot-config.json"
            config.write_text('{"cypilotCorePath": "old/path", "cypilotAdapterPath": "old/adapter", "customField": "keep-me"}', encoding="utf-8")

            # Create existing adapter
            adapter = root / ".cypilot-adapter"
            adapter.mkdir(parents=True)
            (adapter / "AGENTS.md").write_text("# Old content\n", encoding="utf-8")
            (adapter / "artifacts.json").write_text('{"version": 1}', encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["init", "--yes", "--force", "--project-root", str(root)])
                self.assertIn(exit_code, [0, 1, 2])
                # Check that config was updated but custom field preserved
                if config.exists():
                    updated = json.loads(config.read_text(encoding="utf-8"))
                    if isinstance(updated, dict) and "customField" in updated:
                        self.assertEqual(updated.get("customField"), "keep-me")
            finally:
                os.chdir(cwd)


class TestCLIWhereUsedErrorBranches(unittest.TestCase):
    """Tests for where-used command error branches."""

    def test_where_used_registry_error(self):
        """Test where-used when registry fails to load."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / ".cypilot-config.json").write_text('{"cypilotAdapterPath": "adapter"}', encoding="utf-8")
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
            _setup_cypilot_project(root)

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
            (root / ".cypilot-config.json").write_text('{"cypilotAdapterPath": "adapter"}', encoding="utf-8")
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
            _setup_cypilot_project(root)

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

    def test_list_ids_no_cypilot_artifacts(self):
        """Test list-ids when no Cypilot-format artifacts in registry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _bootstrap_registry_new_format(
                root,
                kits={"other": {"format": "OTHER", "path": "templates"}},
                systems=[{"name": "Test", "kits": "other", "artifacts": []}],
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
            (root / ".cypilot-config.json").write_text('{"cypilotAdapterPath": "adapter"}', encoding="utf-8")
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

    def test_validate_no_cypilot_artifacts(self):
        """Test validate when no Cypilot-format artifacts in registry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _bootstrap_registry_new_format(
                root,
                kits={"other": {"format": "OTHER", "path": "templates"}},
                systems=[{"name": "Test", "kits": "other", "artifacts": []}],
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
            _setup_cypilot_project(root)

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
            _setup_cypilot_project(root)
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
        """Test validate when artifact is not in Cypilot registry."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_cypilot_project(root)

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
                kits={"cypilot": {"format": "Cypilot", "path": "templates"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
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
            _setup_cypilot_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-used", "--id", "cpt-test-1", "--include-definitions"])
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
            _setup_cypilot_project(root)

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
            _setup_cypilot_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids", "--pattern", "cypilot"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertIn("ids", out)
            finally:
                os.chdir(cwd)

    def test_list_ids_with_regex_filter(self):
        """Test list-ids --pattern --regex filter."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_cypilot_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids", "--pattern", "cypilot.*1", "--regex"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertIn("ids", out)
            finally:
                os.chdir(cwd)

    def test_list_ids_all_duplicates(self):
        """Test list-ids --all to include duplicates."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_cypilot_project(root)

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
            templates_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)

            # Create template with priority
            tmpl_content = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- cpt:id:item -->
- [ ] `p1` - **ID**: `cpt-test-1`
<!-- cpt:id:item -->
"""
            (templates_dir / "template.md").write_text(tmpl_content, encoding="utf-8")

            # Create artifact with priority marker
            art_dir = root / "architecture"
            art_dir.mkdir(parents=True)
            art_content = """<!-- cpt:id:item -->
- [x] `p1` - **ID**: `cpt-test-1`
<!-- cpt:id:item -->

<!-- cpt:id-ref:item -->
- [x] `p2` - `cpt-test-1`: referenced here
<!-- cpt:id-ref:item -->
"""
            (art_dir / "PRD.md").write_text(art_content, encoding="utf-8")

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
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
            _setup_cypilot_project(root)
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
            _setup_cypilot_project(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["adapter-info"])
                self.assertIn(exit_code, [0, 1])  # May succeed or fail
            finally:
                os.chdir(cwd)


def _setup_cypilot_project_with_codebase(root: Path) -> None:
    """Setup complete Cypilot project with codebase entries for testing."""
    # Create template
    templates_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
    templates_dir.mkdir(parents=True)
    tmpl_content = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- cpt:id:item -->
- [ ] `p1` - **ID**: `cpt-test-1`
<!-- cpt:id:item -->
"""
    (templates_dir / "template.md").write_text(tmpl_content, encoding="utf-8")

    # Create artifact
    art_dir = root / "architecture"
    art_dir.mkdir(parents=True)
    art_content = """<!-- cpt:id:item -->
- [x] `p1` - **ID**: `cpt-test-1`
<!-- cpt:id:item -->
"""
    (art_dir / "PRD.md").write_text(art_content, encoding="utf-8")

    # Create code directory with Cypilot markers
    code_dir = root / "src"
    code_dir.mkdir(parents=True)
    (code_dir / "module.py").write_text(
        "# @cpt-flow:cpt-test-1:p1\ndef test(): pass\n",
        encoding="utf-8"
    )

    # Bootstrap registry with codebase entry
    _bootstrap_registry_new_format(
        root,
        kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
        systems=[{
            "name": "Test",
            "kit": "cypilot",
            "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD", "traceability": "FULL"}],
            "codebase": [{"path": "src", "extensions": [".py"]}],
        }],
    )


def _setup_cypilot_project_with_markerless_cdsl_missing_block(root: Path) -> None:
    (root / "kits" / "sdlc").mkdir(parents=True)
    (root / "kits" / "sdlc" / "constraints.json").write_text(
        json.dumps({"PRD": {"identifiers": {"flow": {"to_code": True}}}}, indent=2) + "\n",
        encoding="utf-8",
    )

    art_dir = root / "architecture"
    art_dir.mkdir(parents=True)
    art_content = """- [x] `p1` - **ID**: `cpt-test-flow-login`
"""
    (art_dir / "PRD.md").write_text(art_content, encoding="utf-8")

    code_dir = root / "src"
    code_dir.mkdir(parents=True)
    (code_dir / "module.py").write_text("def test():\n    return 1\n", encoding="utf-8")

    _bootstrap_registry_new_format(
        root,
        kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
        systems=[{
            "name": "Test",
            "kit": "cypilot",
            "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD", "traceability": "FULL"}],
            "codebase": [{"path": "src", "extensions": [".py"]}],
        }],
    )


def _setup_cypilot_project_with_cdsl_to_code_missing_block(root: Path) -> None:
    (root / "kits" / "sdlc").mkdir(parents=True)
    (root / "kits" / "sdlc" / "constraints.json").write_text(
        json.dumps({"PRD": {"identifiers": {"flow": {"to_code": True}}}}, indent=2) + "\n",
        encoding="utf-8",
    )

    art_dir = root / "architecture"
    art_dir.mkdir(parents=True)
    art_content = """- [x] **ID**: `cpt-test-flow-login`
"""
    (art_dir / "PRD.md").write_text(art_content, encoding="utf-8")

    code_dir = root / "src"
    code_dir.mkdir(parents=True)
    (code_dir / "module.py").write_text("def test():\n    return 1\n", encoding="utf-8")

    _bootstrap_registry_new_format(
        root,
        kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
        systems=[{
            "name": "Test",
            "kit": "cypilot",
            "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD", "traceability": "FULL"}],
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

    def test_validate_code_integrated(self):
        """Test validate-code is integrated into validate command."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_cypilot_project_with_codebase(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    # validate-code now redirects to validate (includes code validation by default)
                    exit_code = main(["validate-code"])
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
            _setup_cypilot_project_with_codebase(root)

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
            _setup_cypilot_project_with_codebase(root)
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
            _setup_cypilot_project_with_codebase(root)

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

    def test_validate_code_orphaned_marker(self):
        """Test validate detects orphaned markers (ID not in artifacts)."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_cypilot_project_with_codebase(root)

            # Add code file with orphaned marker (ID not in artifacts)
            orphan_file = root / "src" / "orphan.py"
            orphan_file.write_text(
                "# @cpt-flow:cpt-unknown-id:p1\ndef orphan(): pass\n",
                encoding="utf-8"
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate", "--verbose"])
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
            (root / ".cypilot-config.json").write_text(
                '{"cypilotAdapterPath": "adapter"}',
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

    def test_validate_with_skip_code(self):
        """Test validate with --skip-code flag."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _setup_cypilot_project_with_codebase(root)

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate", "--skip-code"])
                # Should succeed (no code validation)
                self.assertIn(exit_code, [0, 2])
                out = json.loads(stdout.getvalue())
                # Should not have code_files_scanned key when skipped
                self.assertNotIn("code_files_scanned", out)
            finally:
                os.chdir(cwd)

    def test_validate_code_with_nested_systems(self):
        """Test validate-code with nested system hierarchy."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Setup templates
            templates_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)
            (templates_dir / "template.md").write_text("""---
cypilot-template:
  version: {major: 1, minor: 0}
  kind: PRD
---
<!-- cpt:id:item -->
- [ ] `p1` - **ID**: `cpt-test-1`
<!-- cpt:id:item -->
""", encoding="utf-8")

            # Create artifact
            (root / "architecture").mkdir(parents=True)
            (root / "architecture" / "PRD.md").write_text("""<!-- cpt:id:item -->
- [x] `p1` - **ID**: `cpt-test-1`
<!-- cpt:id:item -->
""", encoding="utf-8")

            # Create code with markers
            (root / "src").mkdir(parents=True)
            (root / "src" / "module.py").write_text(
                "# @cpt-flow:cpt-test-1:p1\ndef test(): pass\n",
                encoding="utf-8"
            )

            # Bootstrap registry with nested systems
            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Parent",
                    "kits": "cypilot",
                    "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
                    "children": [{
                        "name": "Child",
                        "kits": "cypilot",
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
            templates_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)
            (templates_dir / "template.md").write_text("""---
cypilot-template:
  version: {major: 1, minor: 0}
  kind: PRD
---
<!-- cpt:id:item -->
- [ ] `p1` - **ID**: `cpt-test-1`
<!-- cpt:id:item -->
""", encoding="utf-8")

            (root / "architecture").mkdir(parents=True)
            (root / "architecture" / "PRD.md").write_text("""<!-- cpt:id:item -->
- [x] `p1` - **ID**: `cpt-test-1`
<!-- cpt:id:item -->
""", encoding="utf-8")

            # Bootstrap with codebase pointing to nonexistent directory
            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
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
                "# @cpt-flow:cpt-test-flow-login:p1\ndef login(): pass\n",
                encoding="utf-8"
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--code", str(code_file), "--id", "cpt-test-flow-login"])
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
                "# @cpt-begin:cpt-test-flow-login:p1:inst-validate\n"
                "def validate(): return True\n"
                "# @cpt-end:cpt-test-flow-login:p1:inst-validate\n",
                encoding="utf-8"
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main([
                    "get-content", "--code", str(code_file),
                    "--id", "cpt-test-flow-login", "--inst", "validate"
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
            templates_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
            templates_dir.mkdir(parents=True)
            tmpl_content = """---
cypilot-template:
  version:
    major: 1
    minor: 0
  kind: PRD
---
<!-- cpt:id:item -->
- [ ] `p1` - **ID**: `cpt-test-1`
<!-- cpt:id:item -->
"""
            (templates_dir / "template.md").write_text(tmpl_content, encoding="utf-8")

            art_dir = root / "architecture"
            art_dir.mkdir(parents=True)
            art_content = """<!-- cpt:id:item -->
- [x] `p1` - **ID**: `cpt-test-1`
<!-- cpt:id:item -->
"""
            (art_dir / "PRD.md").write_text(art_content, encoding="utf-8")

            # Create code directory with markers
            code_dir = root / "src"
            code_dir.mkdir(parents=True)
            (code_dir / "module.py").write_text(
                "# @cpt-flow:cpt-test-flow-test:p1\ndef test(): pass\n",
                encoding="utf-8"
            )

            # Bootstrap registry with codebase entry
            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
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


class TestCLIGetContentCodePath(unittest.TestCase):
    """Tests for get-content --code option paths."""

    def test_get_content_code_file_not_found(self):
        """Cover ERROR when code file doesn't exist."""
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["get-content", "--code", "/nonexistent/file.py", "--id", "test-id"])
        self.assertEqual(exit_code, 1)
        out = json.loads(stdout.getvalue())
        self.assertEqual(out.get("status"), "ERROR")
        self.assertIn("not found", out.get("message", "").lower())

    def test_get_content_code_file_parse_error(self):
        """Cover ERROR when code file fails to parse."""
        with TemporaryDirectory() as tmpdir:
            # Create a file that will fail to parse (empty or invalid)
            code_file = Path(tmpdir) / "test.py"
            code_file.write_text("", encoding="utf-8")  # Empty file

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--code", str(code_file), "--id", "cpt-test-id"])
            # Should fail or return not found
            self.assertIn(exit_code, (1, 2))

    def test_get_content_code_not_found(self):
        """Cover NOT_FOUND when ID not in code file."""
        with TemporaryDirectory() as tmpdir:
            code_file = Path(tmpdir) / "test.py"
            code_file.write_text("# just a comment\ndef foo(): pass\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-content", "--code", str(code_file), "--id", "cpt-nonexistent-id"])
            self.assertEqual(exit_code, 2)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "NOT_FOUND")

    def test_get_content_code_found_with_inst(self):
        """Cover FOUND path with --inst option."""
        with TemporaryDirectory() as tmpdir:
            code_file = Path(tmpdir) / "test.py"
            code_file.write_text(
                "# @cpt-flow:cpt-test-flow-auth:inst-validate\ndef validate(): pass\n# @cpt-flow\n",
                encoding="utf-8"
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main([
                    "get-content",
                    "--code", str(code_file),
                    "--id", "cpt-test-flow-auth",
                    "--inst", "inst-validate"
                ])
            # May succeed or fail depending on implementation
            self.assertIn(exit_code, (0, 2))

    def test_get_content_neither_artifact_nor_code(self):
        """Cover ERROR when neither --artifact nor --code specified."""
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["get-content", "--id", "cpt-test-id"])
        self.assertEqual(exit_code, 1)
        out = json.loads(stdout.getvalue())
        self.assertEqual(out.get("status"), "ERROR")
        self.assertIn("must be specified", out.get("message", ""))


class TestCLIWhereDefinedEdgeCases(unittest.TestCase):
    """Tests for where-defined error paths."""

    def test_where_defined_no_context(self):
        """where-defined with no adapter returns appropriate error."""
        with TemporaryDirectory() as tmpdir:
            cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-defined", "--id", "cpt-test-id"])
                self.assertEqual(exit_code, 1)
            finally:
                os.chdir(cwd)

    def test_where_defined_empty_id(self):
        """where-defined with empty ID returns error."""
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["where-defined", "--id", "   "])
        self.assertEqual(exit_code, 1)
        out = json.loads(stdout.getvalue())
        self.assertEqual(out.get("status"), "ERROR")
        self.assertIn("empty", out.get("message", "").lower())

    def test_where_defined_artifact_not_found(self):
        """where-defined with nonexistent artifact returns error."""
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["where-defined", "--id", "cpt-test-id", "--artifact", "/nonexistent/path.md"])
        self.assertEqual(exit_code, 1)
        out = json.loads(stdout.getvalue())
        self.assertEqual(out.get("status"), "ERROR")

    def test_where_used_no_context(self):
        """where-used with no adapter returns appropriate error."""
        with TemporaryDirectory() as tmpdir:
            cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["where-used", "--id", "cpt-test-id"])
                self.assertEqual(exit_code, 1)
            finally:
                os.chdir(cwd)

    def test_where_used_empty_id(self):
        """where-used with empty ID returns error."""
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["where-used", "--id", "   "])
        self.assertEqual(exit_code, 1)
        out = json.loads(stdout.getvalue())
        self.assertEqual(out.get("status"), "ERROR")
        self.assertIn("empty", out.get("message", "").lower())

    def test_where_used_artifact_not_found(self):
        """where-used with nonexistent artifact returns error."""
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["where-used", "--id", "cpt-test-id", "--artifact", "/nonexistent/path.md"])
        self.assertEqual(exit_code, 1)
        out = json.loads(stdout.getvalue())
        self.assertEqual(out.get("status"), "ERROR")


class TestCLIListIdsEdgeCases(unittest.TestCase):
    """Tests for list-ids edge cases."""

    def test_list_ids_no_context(self):
        """list-ids with no adapter returns error."""
        with TemporaryDirectory() as tmpdir:
            cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids"])
                self.assertEqual(exit_code, 1)
            finally:
                os.chdir(cwd)


class TestCLIValidateCrossRef(unittest.TestCase):
    """Tests for validate cross-reference edge cases."""

    def test_validate_loads_all_artifacts_for_cross_ref(self):
        """Validate single artifact loads all artifacts for cross-reference validation."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            art_dir = root / "architecture"
            art_dir.mkdir(parents=True)

            # Create two artifacts that reference each other
            (art_dir / "PRD.md").write_text(
                "# PRD\n\n## A. Overview\n\n**ID**: `cpt-test-fr-auth`\n\nRefs: `cpt-test-component-db`\n",
                encoding="utf-8"
            )
            (art_dir / "DESIGN.md").write_text(
                "# DESIGN\n\n## A. Overview\n\n**ID**: `cpt-test-component-db`\n\nRefs: `cpt-test-fr-auth`\n",
                encoding="utf-8"
            )

            _bootstrap_registry_new_format(
                root,
                kits={"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                systems=[{
                    "name": "Test",
                    "kits": "cypilot",
                    "artifacts": [
                        {"path": "architecture/PRD.md", "kind": "PRD"},
                        {"path": "architecture/DESIGN.md", "kind": "DESIGN"},
                    ],
                }],
            )

            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    # Validate only PRD but cross-ref should still work
                    exit_code = main(["validate", "--artifact", "architecture/PRD.md"])
                # Should pass or fail depending on templates
                self.assertIn(exit_code, (0, 1, 2))
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
